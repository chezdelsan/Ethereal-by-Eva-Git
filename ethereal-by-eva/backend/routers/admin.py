"""
Admin API routes for managing inventory and orders.
Protected by simple password authentication.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Piece, PieceImage, Order, OrderItem
from schemas import PieceCreate, PieceUpdate, PieceResponse, OrderResponse, OrderUpdateAdmin
from config import settings
from email_service import send_shipping_notification


router = APIRouter(prefix="/api/admin", tags=["admin"])


async def verify_admin(x_admin_password: str = Header(...)):
    """Simple password authentication for admin routes."""
    if x_admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return True


# =============================================================================
# PIECES
# =============================================================================

@router.get("/pieces", response_model=List[PieceResponse])
async def admin_list_pieces(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """List all pieces (including sold ones) for admin."""
    query = select(Piece).options(selectinload(Piece.images)).order_by(Piece.created_at.desc())
    result = await db.execute(query)
    pieces = result.scalars().all()
    return [PieceResponse.model_validate(p) for p in pieces]


@router.post("/pieces", response_model=PieceResponse)
async def create_piece(
    piece_data: PieceCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Create a new art piece."""
    piece = Piece(
        title=piece_data.title,
        description=piece_data.description,
        price=piece_data.price,
        category=piece_data.category,
        dimensions=piece_data.dimensions,
        weight_oz=piece_data.weight_oz,
        is_featured=piece_data.is_featured,
    )
    db.add(piece)
    await db.commit()
    await db.refresh(piece)
    
    query = select(Piece).options(selectinload(Piece.images)).where(Piece.id == piece.id)
    result = await db.execute(query)
    piece = result.scalar_one()
    return PieceResponse.model_validate(piece)


@router.put("/pieces/{piece_id}", response_model=PieceResponse)
async def update_piece(
    piece_id: int,
    piece_data: PieceUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Update an existing piece."""
    query = select(Piece).options(selectinload(Piece.images)).where(Piece.id == piece_id)
    result = await db.execute(query)
    piece = result.scalar_one_or_none()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    update_data = piece_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(piece, field, value)
    
    await db.commit()
    await db.refresh(piece)
    return PieceResponse.model_validate(piece)


@router.delete("/pieces/{piece_id}")
async def delete_piece(
    piece_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Delete a piece."""
    query = select(Piece).where(Piece.id == piece_id)
    result = await db.execute(query)
    piece = result.scalar_one_or_none()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    await db.delete(piece)
    await db.commit()
    return {"message": "Piece deleted successfully"}


@router.post("/pieces/{piece_id}/images")
async def add_piece_image(
    piece_id: int,
    image_url: str,
    is_primary: bool = False,
    alt_text: str = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Add an image to a piece."""
    query = select(Piece).where(Piece.id == piece_id)
    result = await db.execute(query)
    piece = result.scalar_one_or_none()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    img_query = select(PieceImage).where(PieceImage.piece_id == piece_id)
    img_result = await db.execute(img_query)
    existing_images = img_result.scalars().all()
    
    display_order = len(existing_images)
    
    if is_primary:
        for img in existing_images:
            img.is_primary = False
    
    if not existing_images:
        is_primary = True
    
    image = PieceImage(
        piece_id=piece_id,
        image_url=image_url,
        is_primary=is_primary,
        display_order=display_order,
        alt_text=alt_text
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return {"message": "Image added", "image_id": image.id}


@router.delete("/pieces/{piece_id}/images/{image_id}")
async def delete_piece_image(
    piece_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Remove an image from a piece."""
    query = select(PieceImage).where(PieceImage.id == image_id, PieceImage.piece_id == piece_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    await db.delete(image)
    await db.commit()
    return {"message": "Image deleted"}


# =============================================================================
# ORDERS
# =============================================================================

@router.get("/orders", response_model=List[OrderResponse])
async def admin_list_orders(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """List all orders for admin."""
    query = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    if status:
        query = query.where(Order.status == status)
    result = await db.execute(query)
    orders = result.scalars().all()
    return [OrderResponse.model_validate(o) for o in orders]


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def admin_update_order(
    order_id: int,
    update_data: OrderUpdateAdmin,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    """Update order status or tracking info. Sends shipping email automatically."""
    query = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if we're marking as shipped (status changing to 'shipped')
    is_shipping = (
        update_data.status == "shipped" and 
        order.status != "shipped" and
        update_data.tracking_number
    )
    
    # Update fields
    if update_data.status:
        order.status = update_data.status
    if update_data.tracking_number:
        order.tracking_number = update_data.tracking_number
    if update_data.shipping_carrier:
        order.shipping_carrier = update_data.shipping_carrier
    
    # Set shipped timestamp
    if update_data.status == "shipped" and not order.shipped_at:
        order.shipped_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(order)
    
    # Send shipping notification email
    if is_shipping:
        order_data = {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "shipping_address": order.shipping_address,
        }
        send_shipping_notification(
            order_data, 
            update_data.tracking_number,
            update_data.shipping_carrier or "USPS"
        )
    
    return OrderResponse.model_validate(order)
