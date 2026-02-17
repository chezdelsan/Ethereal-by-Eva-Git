"""
Checkout and payment routes.
Handles Stripe checkout sessions, webhooks, and emails.
"""

import stripe
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Piece, Order, OrderItem
from schemas import ShippingRateRequest, ShippingRate, CheckoutRequest, CheckoutResponse
from config import settings
from email_service import send_customer_confirmation, send_admin_notification

stripe.api_key = settings.stripe_secret_key

router = APIRouter(prefix="/api", tags=["checkout"])


@router.post("/shipping/rates", response_model=List[ShippingRate])
async def get_shipping_rates(
    request: ShippingRateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate shipping rates (flat rate for now)."""
    query = select(Piece).where(Piece.id.in_(request.piece_ids))
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    if len(pieces) != len(request.piece_ids):
        raise HTTPException(status_code=400, detail="Some pieces not found")
    
    return [
        ShippingRate(carrier="USPS", service="Priority Mail", price=1295, estimated_days=3)
    ]


@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe checkout session."""
    query = select(Piece).where(Piece.id.in_(request.piece_ids))
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    if len(pieces) != len(request.piece_ids):
        raise HTTPException(status_code=400, detail="Some pieces not found")
    
    for piece in pieces:
        if piece.is_sold:
            raise HTTPException(status_code=400, detail=f"'{piece.title}' is no longer available")
    
    subtotal = sum(p.price for p in pieces)
    shipping_cost = 1295
    total = subtotal + shipping_cost
    
    line_items = [
        {
            "price_data": {
                "currency": "usd",
                "unit_amount": piece.price,
                "product_data": {
                    "name": piece.title,
                    "description": f"One-of-a-kind {piece.category} - {piece.dimensions or 'Original artwork'}",
                },
            },
            "quantity": 1,
        }
        for piece in pieces
    ]
    
    line_items.append({
        "price_data": {
            "currency": "usd",
            "unit_amount": shipping_cost,
            "product_data": {"name": "Shipping (USPS Priority Mail)", "description": "Estimated delivery: 2-3 business days"},
        },
        "quantity": 1,
    })
    
    order = Order(
        customer_email=request.email,
        customer_name=request.name,
        customer_phone=request.phone,
        shipping_address={
            "name": request.address.name,
            "street": request.address.street,
            "city": request.address.city,
            "state": request.address.state,
            "zip": request.address.zip,
            "country": request.address.country,
        },
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        status="pending",
    )
    db.add(order)
    await db.flush()
    
    for piece in pieces:
        db.add(OrderItem(
            order_id=order.id,
            piece_id=piece.id,
            price_at_purchase=piece.price,
            title_at_purchase=piece.title,
        ))
    
    await db.commit()
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{settings.frontend_url}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/cart.html",
            customer_email=request.email,
            metadata={"order_id": str(order.id), "piece_ids": ",".join(str(p.id) for p in pieces)},
        )
        
        order.stripe_session_id = checkout_session.id
        await db.commit()
        
        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}
        
    except stripe.error.StripeError as e:
        await db.delete(order)
        await db.commit()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events and send emails."""
    payload = await request.body()
    
    try:
        event = stripe.Event.construct_from(
            stripe.util.convert_to_stripe_object(stripe.util.json.loads(payload)),
            stripe.api_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        
        if order_id:
            query = select(Order).where(Order.id == int(order_id))
            result = await db.execute(query)
            order = result.scalar_one_or_none()
            
            if order:
                order.status = "paid"
                order.stripe_payment_intent = session.get("payment_intent")
                
                # Mark pieces as sold
                piece_ids = session.get("metadata", {}).get("piece_ids", "")
                items = []
                if piece_ids:
                    for piece_id in piece_ids.split(","):
                        piece_query = select(Piece).where(Piece.id == int(piece_id))
                        piece_result = await db.execute(piece_query)
                        piece = piece_result.scalar_one_or_none()
                        if piece:
                            piece.is_sold = True
                            items.append({"title": piece.title, "price": piece.price})
                
                await db.commit()
                
                # Send confirmation emails
                order_data = {
                    "id": order.id,
                    "customer_name": order.customer_name,
                    "customer_email": order.customer_email,
                    "shipping_address": order.shipping_address,
                    "subtotal": order.subtotal,
                    "shipping_cost": order.shipping_cost,
                    "total": order.total,
                }
                
                send_customer_confirmation(order_data, items)
                send_admin_notification(order_data, items)
    
    return {"received": True}


@router.get("/order/{session_id}")
async def get_order_by_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get order details by Stripe session ID."""
    query = select(Order).where(Order.stripe_session_id == session_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items_query = select(OrderItem).where(OrderItem.order_id == order.id)
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()
    
    return {
        "id": order.id,
        "status": order.status,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "shipping_address": order.shipping_address,
        "subtotal": order.subtotal,
        "shipping_cost": order.shipping_cost,
        "total": order.total,
        "items": [{"title": item.title_at_purchase, "price": item.price_at_purchase} for item in items],
        "created_at": order.created_at.isoformat(),
    }
