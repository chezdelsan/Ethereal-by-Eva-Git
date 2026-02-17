"""
Configuration management for Ethereal by Eva.
Loads environment variables and provides typed settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./ethereal_by_eva.db"
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    
    # Shippo
    shippo_api_key: str = ""
    
    # Admin
    admin_password: str = "admin"  # Change in production!
    
    # Email
    resend_api_key: str = ""
    from_email: str = "orders@example.com"
    admin_email: str = ""
    
    # Shipping origin (Athens, OH)
    ship_from_name: str = "Ethereal by Eva"
    ship_from_street: str = "1 Ohio University"
    ship_from_city: str = "Athens"
    ship_from_state: str = "OH"
    ship_from_zip: str = "45701"
    ship_from_country: str = "US"
    
    # CORS origins (for frontend)
    cors_origins: list[str] = [
        "http://localhost:5500",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
