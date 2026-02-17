"""
API routes for art pieces.
Public endpoints for browsing and viewing pieces.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Piece, PieceImage
from schemas import (
    PieceResponse, 
    PieceListResponse, 
    CategoryInfo, 
    VALID_CATEGORIES
)


router = APIRouter(prefix="/api/pieces", tags=["pieces"])


@router.get("", response_model=PieceListResponse)
async def list_pieces(
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(None, description="Filter featured only"),
    available: bool = Query(True, description="Only show unsold pieces"),
    sort: str = Query("newest", description="Sort: newest, oldest, price_low, price_high"),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    List art pieces with optional filtering and sorting.
    """
    # Build query
    query = select(Piece).options(selectinload(Piece.images))
    count_query = select(func.count(Piece.id))
    
    # Apply filters
    if category:
        if category not in VALID_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {VALID_CATEGORIES}")
        query = query.where(Piece.category == category)
        count_query = count_query.where(Piece.category == category)
    
    if featured is not None:
        query = query.where(Piece.is_featured == featured)
        count_query = count_query.where(Piece.is_featured == featured)
    
    if available:
        query = query.where(Piece.is_sold == False)
        count_query = count_query.where(Piece.is_sold == False)
    
    # Apply sorting
    if sort == "newest":
        query = query.order_by(Piece.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(Piece.created_at.asc())
    elif sort == "price_low":
        query = query.order_by(Piece.price.asc())
    elif sort == "price_high":
        query = query.order_by(Piece.price.desc())
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    # Execute query
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    return PieceListResponse(
        pieces=[PieceResponse.model_validate(p) for p in pieces],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/featured", response_model=List[PieceResponse])
async def get_featured_pieces(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get featured pieces for homepage display.
    """
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(Piece.is_featured == True)
        .where(Piece.is_sold == False)
        .order_by(Piece.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    return [PieceResponse.model_validate(p) for p in pieces]


@router.get("/new", response_model=List[PieceResponse])
async def get_new_pieces(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Get newest pieces (recent drops).
    """
    query = (
        select(Piece)
        .options(selectinload(Piece.images))
        .where(Piece.is_sold == False)
        .order_by(Piece.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    pieces = result.scalars().all()
    
    return [PieceResponse.model_validate(p) for p in pieces]


@router.get("/categories", response_model=List[CategoryInfo])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Get all categories with piece counts.
    """
    categories = []
    
    # Pretty names for categories
    category_names = {
        "painting": "Paintings",
        "pastel": "Pastels",
        "crayon": "Crayon Art",
        "marker": "Marker Art",
        "paper_mache": "Paper Maché"
    }
    
    for slug in VALID_CATEGORIES:
        # Count available pieces in this category
        count_query = select(func.count(Piece.id)).where(
            Piece.category == slug,
            Piece.is_sold == False
        )
        result = await db.execute(count_query)
        count = result.scalar()
        
        categories.append(CategoryInfo(
            slug=slug,
            name=category_names.get(slug, slug.title()),
            count=count
        ))
    
    return categories


@router.get("/{piece_id}", response_model=PieceResponse)
async def get_piece(piece_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single piece by ID with all its images.
    """
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
