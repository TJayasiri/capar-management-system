"""
Company (Factory) Model
Represents manufacturing facilities/companies
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class Company(Base):
    """Company/Factory model for CAPAR system"""
    
    __tablename__ = "companies"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Company info
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text)
    country = Column(String(100))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Company type and industry
    industry_type = Column(String(100))  # "Manufacturing", "Food Processing", etc.
    company_size = Column(String(50))    # "Small", "Medium", "Large"
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Greenleaf admin responsible for this company
    greenleaf_admin_id = Column(UUID(as_uuid=True))  # Reference to Greenleaf admin user
    
    # Relationships
    users = relationship("User", back_populates="company")
    capars = relationship("CAPAR", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
    
    @property
    def active_capars_count(self):
        """Count of active CAPARs for this company"""
        return len([capar for capar in self.capars if capar.status == "active"])
    
    @property
    def total_users_count(self):
        """Count of users for this company"""
        return len([user for user in self.users if user.is_active])