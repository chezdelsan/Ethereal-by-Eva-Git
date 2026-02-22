"""
Seed script - Test data for all categories.
Run: python seed.py
"""

import asyncio
from database import init_db, async_session
from models import Piece, PieceImage

SAMPLE_PIECES = [
    # PAINTINGS (15, all categories converted)
    {
        "title": "Sea Stars",
        "description": "",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 32,
        "is_featured": True,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Ocean Dreams",
        "description": "Serene seascape with rolling waves. Calming blues and seafoam greens.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 48,
        "is_featured": True,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Abstract Energy",
        "description": "Vibrant abstract expressionism. Explosive colors and dynamic brushstrokes.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 28,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Lavender Fields",
        "description": "Soft pastel landscape of rolling lavender hills. Dreamy and peaceful.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 16,
        "is_featured": True,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Portrait Study",
        "description": "Delicate pastel portrait with soft skin tones and expressive eyes.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 18,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Morning Mist",
        "description": "Ethereal forest scene shrouded in gentle morning fog.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 14,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Childhood Garden",
        "description": "Whimsical garden scene with oversized flowers. Pure joy on paper.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 8,
        "is_featured": True,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Rainbow City",
        "description": "Colorful cityscape where every building is a different hue.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 6,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Happy Animals",
        "description": "Playful zoo scene with smiling animals. Perfect for a kid's room.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 6,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Neon Nights",
        "description": "Bold marker illustration of a city at night. Electric colors pop.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 12,
        "is_featured": True,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Geometric Dreams",
        "description": "Precise geometric patterns in vibrant marker. Hypnotic design.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 10,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Comic Hero",
        "description": "Original comic-style character illustration. Bold lines and colors.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 14,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Forest Fox",
        "description": "Hand-sculpted fox with painted details. Whimsical woodland friend.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 24,
        "is_featured": True,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Moon Bowl",
        "description": "Decorative bowl with crescent moon design. Functional art piece.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 18,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
    {
        "title": "Garden Gnome",
        "description": "Cheerful garden gnome sculpture. Hand-painted with love.",
        "price": 9999,  # $99.99
        "category": "painting",
        "dimensions": "12x12 inches",
        "weight_oz": 20,
        "is_featured": False,
        "images": [{"url": "/static/images/placeholder.jpg", "is_primary": True}]
    },
]


async def seed_database():
    await init_db()
    
    async with async_session() as session:
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(Piece.id)))
        count = result.scalar()
        
        if count > 0:
            print(f"⚠️  Database has {count} pieces. Delete ethereal_by_eva.db to reseed.")
            return
        
        print("🌱 Seeding test data...")
        
        for data in SAMPLE_PIECES:
            piece = Piece(
                title=data["title"],
                description=data["description"],
                price=data["price"],
                category=data["category"],
                dimensions=data["dimensions"],
                weight_oz=data["weight_oz"],
                is_featured=data["is_featured"],
            )
            session.add(piece)
            await session.flush()
            
            for i, img in enumerate(data["images"]):
                session.add(PieceImage(
                    piece_id=piece.id,
                    image_url=img["url"],
                    is_primary=img["is_primary"],
                    display_order=i,
                ))
            
            print(f"   ✓ {piece.category}: {piece.title} (${piece.price/100:.2f})")
        
        await session.commit()
        print(f"\n✅ Added {len(SAMPLE_PIECES)} test pieces!")
        print("\n📋 Summary by category:")
        print("   • Paintings: 15 (all categories, all $)")


if __name__ == "__main__":
    asyncio.run(seed_database())
