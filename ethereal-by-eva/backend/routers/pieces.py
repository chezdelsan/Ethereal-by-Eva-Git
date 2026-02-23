"""
Public piece browsing routes.
No authentication required.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Piece, PieceImage
from schemas import PieceResponse, PieceListResponse, CategoryInfo

router = APIRouter(prefix="/api", tags=["pieces"])


@router.get("/pieces", response_model=PieceListResponse)
async def list_pieces(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    available: Optional[bool] = None,
    sort: Optional[str] = Query(None, regex="^(newest|price_asc|price_desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    List pieces with filtering and pagination.
    Excludes gallery_only pieces from public view.
    """
    query = select(Piece).options(selectinload(Piece.images))
    
    # Always exclude gallery_only pieces from public listing
    query = query.where(Piece.gallery_only == False)
    
    # Apply filters
    if category:
        query = query.where(Piece.category == category)
    
    if featured is not None:
        query = query.where(Piece.is_featured == featured)
    
    if available is not None:
        query = query.where(Piece.is_sold == (not available))
    
    # Apply sorting
    if sort == "newest":
        query = query.order_by(Piece.created_at.desc())
    elif sort == "price_asc":
        query = query.order_by(Piece.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Piece.price.desc())
    else:
        query = query.order_by(Piece.created_at.desc())
    
    # Get total count (excluding gallery_only)
    count_query = select(func.count(Piece.id)).where(Piece.gallery_only == False)
    if category:
        count_query = count_query.where(Piece.category == category)
    if featured is not None:
        count_query = count_query.where(Piece.is_featured == featured)
    if available is not None:
        count_query = count_query.where(Piece.is_sold == (not available))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    return PieceListResponse(
        pieces=[PieceResponse.model_validate(p) for p in pieces],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/pieces/featured", response_model=List[PieceResponse])
async def get_featured_pieces(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get featured pieces for homepage. Excludes gallery_only and sold pieces."""
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(Piece.is_featured == True)
        .where(Piece.is_sold == False)
        .where(Piece.gallery_only == False)
        .order_by(Piece.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    pieces = result.scalars().all()
    return [PieceResponse.model_validate(p) for p in pieces]


@router.get("/pieces/new", response_model=List[PieceResponse])
async def get_new_pieces(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get newest pieces. Excludes gallery_only and sold pieces."""
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(Piece.is_sold == False)
        .where(Piece.gallery_only == False)
        .order_by(Piece.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    pieces = result.scalars().all()
    return [PieceResponse.model_validate(p) for p in pieces]


@router.get("/pieces/categories", response_model=List[CategoryInfo])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all categories with piece counts. Excludes gallery_only pieces."""
    query = (
        select(Piece.category, func.count(Piece.id))
        .where(Piece.is_sold == False)
        .where(Piece.gallery_only == False)
        .group_by(Piece.category)
    )
    
    result = await db.execute(query)
    categories = result.all()
    
    # Format category names
    category_names = {
        "painting": "Paintings",
        "pastel": "Pastels",
        "crayon": "Crayon",
        "marker": "Marker",
        "paper_mache": "Paper Maché",
    }
    
    return [
        CategoryInfo(
            slug=cat,
            name=category_names.get(cat, cat.title()),
            count=count
        )
        for cat, count in categories
    ]


@router.get("/pieces/{piece_id}", response_model=PieceResponse)
async def get_piece(
    piece_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single piece by ID."""
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(Piece.id == piece_id)
    )
    
    result = await db.execute(query)
    piece = result.scalar_one_or_none()
    
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    return PieceResponse.model_validate(piece)


@router.get("/gallery/pieces", response_model=List[PieceResponse])
async def get_gallery_pieces(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get pieces for gallery page - sold OR gallery_only pieces that are set to show."""
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(or_(Piece.is_sold == True, Piece.gallery_only == True))
        .where(Piece.show_in_gallery == True)
        .order_by(Piece.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    pieces = result.scalars().all()
    return [PieceResponse.model_validate(p) for p in pieces]
