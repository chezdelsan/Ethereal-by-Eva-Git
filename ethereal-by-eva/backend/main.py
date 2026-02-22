"""
Ethereal by Eva - Art E-Commerce API
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routers import pieces, cart, checkout, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """
    # Startup: Initialize database
    await init_db()
    print("✨ Ethereal by Eva API is starting up...")
    
    yield
    
    # Shutdown
    print("👋 Ethereal by Eva API is shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Ethereal by Eva",
    description="API for one-of-a-kind art e-commerce",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://localhost:3000",
        "https://etherealbyeva.com",
        "https://www.etherealbyeva.com",
        "https://ethereal-frontend-ibkk.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(pieces.router)
app.include_router(cart.router)
app.include_router(checkout.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Health check and API info."""
    return {
        "name": "Ethereal by Eva API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
