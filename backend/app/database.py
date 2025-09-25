"""
Database connection and session management
SQLAlchemy setup for PostgreSQL
"""
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from .config import settings


# Database URL
DATABASE_URL = settings.database_url

# For development, you might want to use SQLite first
if not DATABASE_URL or "postgresql" not in DATABASE_URL:
    # Fallback to SQLite for development
    DATABASE_URL = "sqlite:///./capar_development.db"
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool
else:
    # PostgreSQL production settings
    connect_args = {}
    poolclass = None

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=poolclass,
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Use this in FastAPI route dependencies
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    try:
        # Import all models here to ensure they're registered with Base
        from .models import Company, User, Category, SuggestedAction, CAPAR, CAPARItem
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't raise error during development
        pass


def check_db_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Use text() wrapper for raw SQL
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# Health check function
async def get_db_health():
    """Async health check for database"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        return {"database": "healthy", "status": "connected"}
    except Exception as e:
        return {"database": "unhealthy", "error": str(e)}