"""
User Model
Handles authentication and user management
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User roles in the system"""
    GREENLEAF_SUPER_ADMIN = "greenleaf_super_admin"  # Can delete data, manage all
    GREENLEAF_ADMIN = "greenleaf_admin"              # Manage companies, view all
    FACTORY_ADMIN = "factory_admin"                  # Manage own company's CAPARs
    FACTORY_USER = "factory_user"                    # Create/edit own CAPARs


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User info
    full_name = Column(String(255), nullable=False)
    job_title = Column(String(100))
    phone = Column(String(50))
    
    # Role and permissions
    role = Column(Enum(UserRole), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Company relationship (nullable for Greenleaf users)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="users")
    
    # CAPARs created by this user
    created_capars = relationship("CAPAR", back_populates="created_by_user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_greenleaf_user(self) -> bool:
        """Check if user is from Greenleaf (not factory)"""
        return self.role in [UserRole.GREENLEAF_SUPER_ADMIN, UserRole.GREENLEAF_ADMIN]
    
    @property
    def is_factory_user(self) -> bool:
        """Check if user is from a factory"""
        return self.role in [UserRole.FACTORY_ADMIN, UserRole.FACTORY_USER]
    
    @property
    def can_delete_data(self) -> bool:
        """Check if user can delete data permanently"""
        return self.role == UserRole.GREENLEAF_SUPER_ADMIN
    
    @property
    def can_manage_companies(self) -> bool:
        """Check if user can manage companies"""
        return self.role in [UserRole.GREENLEAF_SUPER_ADMIN, UserRole.GREENLEAF_ADMIN]
    
    @property
    def can_manage_own_capars(self) -> bool:
        """Check if user can manage CAPARs for their company"""
        return self.role in [UserRole.FACTORY_ADMIN, UserRole.FACTORY_USER]