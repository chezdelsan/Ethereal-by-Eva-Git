"""
Configuration management for Ethereal by Eva.
Loads environment variables and provides typed settings.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - handles both SQLite (local) and PostgreSQL (production)
    database_url: str = "sqlite+aiosqlite:///./ethereal_by_eva.db"
    
    @property
    def async_database_url(self) -> str:
        """Convert DATABASE_URL to async version for SQLAlchemy."""
        url = self.database_url
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    
    # Shippo
    shippo_api_key: str = ""
    
    # Admin
    admin_password: str = "admin"
    
    # Email
    resend_api_key: str = ""
    from_email: str = "onboarding@resend.dev"
    admin_email: str = ""
    
    # Shipping origin (Athens, OH)
    ship_from_name: str = "Ethereal by Eva"
    ship_from_street: str = "1 Ohio University"
    ship_from_city: str = "Athens"
    ship_from_state: str = "OH"
    ship_from_zip: str = "45701"
    ship_from_country: str = "US"
    
    # Frontend URL (for Stripe redirects)
    frontend_url: str = "http://localhost:5500"
    
    # CORS origins
    cors_origins: list[str] = [
        "http://localhost:5500",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Add production frontend URL to CORS if set
if settings.frontend_url not in settings.cors_origins:
    settings.cors_origins.append(settings.frontend_url)
