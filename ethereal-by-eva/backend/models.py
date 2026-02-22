"""
Database models for Ethereal by Eva.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Piece(Base):
    """An art piece for sale."""
    
    __tablename__ = "pieces"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)  # Price in cents (e.g., 15000 = $150.00)
    
    # Category: painting
    category: Mapped[str] = mapped_column(String(50))  # Only 'painting' allowed
    
    # Status
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    gallery_only: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Physical details (for shipping calculation)
    dimensions: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Always '12x12 inches'
    weight_oz: Mapped[int] = mapped_column(Integer, default=16)  # Weight in ounces
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images: Mapped[List["PieceImage"]] = relationship(back_populates="piece", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Piece {self.id}: {self.title}>"


class PieceImage(Base):
    """Images for an art piece (supports multiple images per piece)."""
    
    __tablename__ = "piece_images"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    piece_id: Mapped[int] = mapped_column(ForeignKey("pieces.id", ondelete="CASCADE"))
    
    image_url: Mapped[str] = mapped_column(String(500))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    alt_text: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Relationship
    piece: Mapped["Piece"] = relationship(back_populates="images")
    
    def __repr__(self):
        return f"<PieceImage {self.id} for Piece {self.piece_id}>"


class Order(Base):
    """A customer order."""
    
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Stripe reference
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    stripe_payment_intent: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Customer info (guest checkout, no user account)
    customer_email: Mapped[str] = mapped_column(String(200))
    customer_name: Mapped[str] = mapped_column(String(200))
    customer_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Shipping address (stored as JSON for flexibility)
    shipping_address: Mapped[dict] = mapped_column(JSON)
    # Expected format: {street, city, state, zip, country}
    
    # Order totals (all in cents)
    subtotal: Mapped[int] = mapped_column(Integer)  # Sum of item prices
    shipping_cost: Mapped[int] = mapped_column(Integer)  # Shipping fee
    total: Mapped[int] = mapped_column(Integer)  # subtotal + shipping
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # Possible values: pending, paid, shipped, delivered, cancelled
    
    # Shipping info (filled in after shipping)
    shipping_carrier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.id}: {self.status}>"


class OrderItem(Base):
    """Individual items within an order."""
    
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    piece_id: Mapped[int] = mapped_column(ForeignKey("pieces.id"))
    
    # Snapshot of price at time of purchase
    price_at_purchase: Mapped[int] = mapped_column(Integer)
    title_at_purchase: Mapped[str] = mapped_column(String(200))
    
    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    piece: Mapped["Piece"] = relationship()
    
    def __repr__(self):
        return f"<OrderItem {self.id}: {self.title_at_purchase}>"
