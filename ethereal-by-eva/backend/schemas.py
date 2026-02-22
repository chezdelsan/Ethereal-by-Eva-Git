"""
Pydantic schemas for API request/response validation.
These define the shape of data sent to and from the API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# =============================================================================
# PIECE SCHEMAS
# =============================================================================

class PieceImageSchema(BaseModel):
    """Schema for piece images."""
    id: int
    image_url: str
    is_primary: bool
    display_order: int
    alt_text: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PieceBase(BaseModel):
    """Base schema for piece data."""
    title: str
    description: str
    price: int  # In cents
    category: str
    dimensions: Optional[str] = None
    weight_oz: int = 16


class PieceCreate(PieceBase):
    """Schema for creating a new piece."""
    is_featured: bool = False
    gallery_only: bool = False


class PieceUpdate(BaseModel):
    """Schema for updating a piece (all fields optional)."""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    gallery_only: Optional[bool] = None
    category: Optional[str] = None
    dimensions: Optional[str] = None
    weight_oz: Optional[int] = None
    is_featured: Optional[bool] = None
    is_sold: Optional[bool] = None


class PieceResponse(PieceBase):
    """Schema for piece in API responses."""
    id: int
    is_sold: bool
    is_featured: bool
    gallery_only: bool = False
    created_at: datetime
    images: List[PieceImageSchema] = []
    
    # Computed field for primary image
    @property
    def primary_image_url(self) -> Optional[str]:
        for img in self.images:
            if img.is_primary:
                return img.image_url
        return self.images[0].image_url if self.images else None
    
    model_config = ConfigDict(from_attributes=True)


class PieceListResponse(BaseModel):
    """Schema for paginated piece list."""
    pieces: List[PieceResponse]
    total: int
    page: int
    per_page: int


# =============================================================================
# CART SCHEMAS (client-side cart, these are just for validation)
# =============================================================================

class CartItem(BaseModel):
    """A single item in the cart."""
    piece_id: int
    title: str
    price: int
    image_url: Optional[str] = None


class Cart(BaseModel):
    """Shopping cart."""
    items: List[CartItem]
    subtotal: int  # Sum of all item prices


# =============================================================================
# CHECKOUT SCHEMAS
# =============================================================================

class ShippingAddress(BaseModel):
    """Customer shipping address."""
    name: str
    street: str
    city: str
    state: str
    zip: str
    country: str = "US"


class ShippingRateRequest(BaseModel):
    """Request for shipping rate calculation."""
    address: ShippingAddress
    piece_ids: List[int]


class ShippingRate(BaseModel):
    """A shipping rate option."""
    carrier: str
    service: str
    price: int  # In cents
    estimated_days: int


class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    email: EmailStr
    name: str
    phone: Optional[str] = None
    address: ShippingAddress
    piece_ids: List[int]


class CheckoutResponse(BaseModel):
    """Response with Stripe checkout URL."""
    checkout_url: str
    session_id: str


# =============================================================================
# ORDER SCHEMAS
# =============================================================================

class OrderItemResponse(BaseModel):
    """Schema for order item in responses."""
    id: int
    piece_id: int
    price_at_purchase: int
    title_at_purchase: str
    
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Schema for order in API responses."""
    id: int
    customer_email: str
    customer_name: str
    shipping_address: dict
    subtotal: int
    shipping_cost: int
    total: int
    status: str
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class OrderUpdateAdmin(BaseModel):
    """Schema for admin updating an order."""
    status: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None


# =============================================================================
# CATEGORY SCHEMAS
# =============================================================================

# Valid categories
VALID_CATEGORIES = ["painting"]


class CategoryInfo(BaseModel):
    """Information about the only available category: painting."""
    slug: str
    name: str
    count: int
