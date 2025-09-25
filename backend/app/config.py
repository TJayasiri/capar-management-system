"""
CAPAR System Configuration Settings
Manages all environment variables and app settings
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Info
    app_name: str = "CAPAR Management System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./capar_development.db"
    
    # Security
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS - Handle as string and split manually
    #allowed_origins_str: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")
    # In your existing config.py, update the allowed_origins_str default
    allowed_origins_str: str = Field(default="http://localhost:3000,http://localhost:3001", alias="ALLOWED_ORIGINS")

    # File Upload
    max_file_size: int = 10485760  # 10MB
    upload_path: str = "./uploads"
    
    # Email (optional)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = ""
    mail_tls: bool = True
    mail_ssl: bool = False
    
    @property
    def allowed_origins(self) -> List[str]:
        """Convert comma-separated origins to list"""
        if self.allowed_origins_str:
            return [origin.strip() for origin in self.allowed_origins_str.split(",")]
        return ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

        


# Create global settings instance
settings = Settings()

# Helper function to get database URL for different environments
def get_database_url() -> str:
    """Get database URL with fallback for development"""
    if settings.database_url:
        return settings.database_url
    
    # Development fallback
    return "sqlite:///./capar_development.db"


# Validation function
def validate_settings():
    """Validate required settings are present"""
    required_fields = [
        "secret_key"
    ]
    
    missing_fields = []
    for field in required_fields:
        field_value = getattr(settings, field, None)
        if not field_value or field_value == "change-this-secret-key-in-production":
            missing_fields.append(field)
    
    if missing_fields:
        print(f"⚠️  Warning: Using default values for: {', '.join(missing_fields)}")
        print("   Please update your .env file for production")
    
    print(f"✅ Settings loaded successfully for {settings.app_name} v{settings.app_version}")
    return True