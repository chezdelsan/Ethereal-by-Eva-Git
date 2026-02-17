"""
Seed script to populate database with sample art pieces.
Run this to set up test data for development.

Usage:
    python seed.py
"""

import asyncio
from database import init_db, async_session
from models import Piece, PieceImage


# Sample art pieces for testing
SAMPLE_PIECES = [
    {
        "title": "Sunset Over Athens",
        "description": "A vibrant acrylic painting capturing the golden hour over the Ohio University campus. Rich oranges and purples blend seamlessly to create a warm, nostalgic atmosphere.",
        "price": 15000,  # $150.00
        "category": "painting",
        "dimensions": "18x24 inches",
        "weight_oz": 32,
        "is_featured": True,
        "images": [
            {"url": "https://picsum.photos/seed/sunset1/800/600", "is_primary": True, "alt": "Sunset painting front view"},
            {"url": "https://picsum.photos/seed/sunset2/800/600", "is_primary": False, "alt": "Sunset painting detail"},
            {"url": "https://picsum.photos/seed/sunset3/800/600", "is_primary": False, "alt": "Sunset painting framed"},
        ]
    },
    {
        "title": "Wildflower Dreams",
        "description": "Delicate pastel work featuring Ohio wildflowers in soft, dreamy hues. Each petal is carefully rendered to capture the essence of spring in Appalachia.",
        "price": 8500,  # $85.00
        "category": "pastel",
        "dimensions": "12x16 inches",
        "weight_oz": 16,
        "is_featured": True,
        "images": [
            {"url": "https://picsum.photos/seed/wildflower1/800/600", "is_primary": True, "alt": "Wildflower pastel artwork"},
            {"url": "https://picsum.photos/seed/wildflower2/800/600", "is_primary": False, "alt": "Detail of flower petals"},
        ]
    },
    {
        "title": "Childhood Memories",
        "description": "A whimsical crayon piece that evokes the innocence of youth. Bold colors and playful strokes create a joyful, energetic composition.",
        "price": 4500,  # $45.00
        "category": "crayon",
        "dimensions": "9x12 inches",
        "weight_oz": 8,
        "is_featured": False,
        "images": [
            {"url": "https://picsum.photos/seed/childhood1/800/600", "is_primary": True, "alt": "Crayon artwork"},
        ]
    },
    {
        "title": "Urban Rhythm",
        "description": "Dynamic marker illustration capturing the pulse of city life. Sharp lines and bold contrasts create a modern, graphic aesthetic.",
        "price": 6500,  # $65.00
        "category": "marker",
        "dimensions": "11x14 inches",
        "weight_oz": 12,
        "is_featured": True,
        "images": [
            {"url": "https://picsum.photos/seed/urban1/800/600", "is_primary": True, "alt": "Urban marker art"},
            {"url": "https://picsum.photos/seed/urban2/800/600", "is_primary": False, "alt": "Close-up of line work"},
        ]
    },
    {
        "title": "Forest Spirit",
        "description": "An enchanting paper maché sculpture of a woodland creature. Hand-painted with acrylics and sealed for lasting beauty.",
        "price": 12000,  # $120.00
        "category": "paper_mache",
        "dimensions": "8x6x10 inches",
        "weight_oz": 24,
        "is_featured": True,
        "images": [
            {"url": "https://picsum.photos/seed/forest1/800/600", "is_primary": True, "alt": "Paper maché sculpture front"},
            {"url": "https://picsum.photos/seed/forest2/800/600", "is_primary": False, "alt": "Sculpture side view"},
            {"url": "https://picsum.photos/seed/forest3/800/600", "is_primary": False, "alt": "Sculpture detail"},
        ]
    },
    {
        "title": "Morning Light",
        "description": "Soft pastels capture the gentle light of early morning through a window. A peaceful, contemplative piece perfect for any space.",
        "price": 7500,  # $75.00
        "category": "pastel",
        "dimensions": "14x18 inches",
        "weight_oz": 20,
        "is_featured": False,
        "images": [
            {"url": "https://picsum.photos/seed/morning1/800/600", "is_primary": True, "alt": "Morning light pastel"},
        ]
    },
    {
        "title": "Abstract Joy",
        "description": "A vibrant explosion of color in acrylic. This abstract piece brings energy and happiness to any room.",
        "price": 18000,  # $180.00
        "category": "painting",
        "dimensions": "24x30 inches",
        "weight_oz": 48,
        "is_featured": False,
        "images": [
            {"url": "https://picsum.photos/seed/abstract1/800/600", "is_primary": True, "alt": "Abstract painting"},
            {"url": "https://picsum.photos/seed/abstract2/800/600", "is_primary": False, "alt": "Texture detail"},
        ]
    },
    {
        "title": "Neon Dreams",
        "description": "Bold marker work featuring neon-inspired colors and geometric patterns. A statement piece for modern spaces.",
        "price": 5500,  # $55.00
        "category": "marker",
        "dimensions": "12x12 inches",
        "weight_oz": 10,
        "is_featured": False,
        "images": [
            {"url": "https://picsum.photos/seed/neon1/800/600", "is_primary": True, "alt": "Neon marker art"},
        ]
    },
    {
        "title": "Garden Party",
        "description": "Cheerful crayon illustration of a whimsical garden scene. Perfect for children's rooms or anyone young at heart.",
        "price": 3500,  # $35.00
        "category": "crayon",
        "dimensions": "8x10 inches",
        "weight_oz": 6,
        "is_featured": False,
        "images": [
            {"url": "https://picsum.photos/seed/garden1/800/600", "is_primary": True, "alt": "Garden crayon art"},
        ]
    },
    {
        "title": "Wise Owl",
        "description": "A charming paper maché owl with hand-painted details. Each feather carefully sculpted and colored.",
        "price": 9500,  # $95.00
        "category": "paper_mache",
        "dimensions": "6x5x8 inches",
        "weight_oz": 18,
        "is_featured": False,
        "images": [
            {"url": "https://picsum.photos/seed/owl1/800/600", "is_primary": True, "alt": "Owl sculpture"},
            {"url": "https://picsum.photos/seed/owl2/800/600", "is_primary": False, "alt": "Owl back view"},
        ]
    },
]


async def seed_database():
    """Populate database with sample data."""
    
    # Initialize database tables
    await init_db()
    
    async with async_session() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        count_result = await session.execute(select(func.count(Piece.id)))
        count = count_result.scalar()
        
        if count > 0:
            print(f"⚠️  Database already has {count} pieces. Skipping seed.")
            print("   To reseed, delete ethereal_by_eva.db and run again.")
            return
        
        print("🌱 Seeding database with sample art pieces...")
        
        for piece_data in SAMPLE_PIECES:
            # Create piece
            piece = Piece(
                title=piece_data["title"],
                description=piece_data["description"],
                price=piece_data["price"],
                category=piece_data["category"],
                dimensions=piece_data["dimensions"],
                weight_oz=piece_data["weight_oz"],
                is_featured=piece_data["is_featured"],
            )
            session.add(piece)
            await session.flush()  # Get the piece ID
            
            # Add images
            for i, img_data in enumerate(piece_data["images"]):
                image = PieceImage(
                    piece_id=piece.id,
                    image_url=img_data["url"],
                    is_primary=img_data["is_primary"],
                    display_order=i,
                    alt_text=img_data.get("alt")
                )
                session.add(image)
            
            print(f"   ✓ Added: {piece.title}")
        
        await session.commit()
        print(f"\n✅ Successfully seeded {len(SAMPLE_PIECES)} art pieces!")


if __name__ == "__main__":
    asyncio.run(seed_database())
