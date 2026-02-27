"""
Cart API routes.
Note: Cart is primarily managed client-side (localStorage).
These endpoints help validate cart contents and calculate totals.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Piece
from schemas import CartItem, Cart, PieceResponse


router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.post("/validate", response_model=Cart)
async def validate_cart(
    piece_ids: List[int],
    db: AsyncSession = Depends(get_db)
):
    """
    Validate cart items and return current prices.
    
    This is called before checkout to ensure:
    1. All pieces still exist
    2. None have been sold
    3. Prices are current
    """
    if not piece_ids:
        return Cart(items=[], subtotal=0)
    
    # Fetch all pieces
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(Piece.id.in_(piece_ids))
    )
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    # Build validated cart
    items = []
    errors = []
    
    for piece_id in piece_ids:
        piece = next((p for p in pieces if p.id == piece_id), None)
        
        if not piece:
            errors.append(f"Piece {piece_id} no longer exists")
            continue
        
        if piece.is_sold:
            errors.append(f"'{piece.title}' has already been sold")
            continue
        
        # Get primary image URL
        image_url = None
        for img in piece.images:
            if img.is_primary:
                image_url = img.image_url
                break
        if not image_url and piece.images:
            image_url = piece.images[0].image_url
        
        # Use sale price if available and valid
        final_price = piece.price
        if piece.sale_price is not None and piece.sale_price > 0 and not piece.is_sold:
            final_price = piece.sale_price
        items.append(CartItem(
            piece_id=piece.id,
            title=piece.title,
            price=final_price,
            image_url=image_url
        ))
    
    if errors:
        raise HTTPException(
            status_code=400,
            detail={"message": "Some items are no longer available", "errors": errors}
        )
    
    subtotal = sum(item.price for item in items)
    
    return Cart(items=items, subtotal=subtotal)


@router.get("/check/{piece_id}")
async def check_availability(
    piece_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Quick check if a piece is still available for purchase.
    """
    query = select(Piece).where(Piece.id == piece_id)
    result = await db.execute(query)
    piece = result.scalar_one_or_none()
    
    if not piece:
        return {"available": False, "reason": "not_found"}
    
    if piece.is_sold:
        return {"available": False, "reason": "sold"}
    
    return {"available": True, "price": piece.price}
