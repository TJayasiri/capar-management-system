"""
Category Model
Predefined categories for CAPAR findings
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class Category(Base):
    """Category model for classifying CAPAR findings"""
    
    __tablename__ = "categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Category info
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Category classification
    category_type = Column(String(100))  # "Safety", "Quality", "Security", "Environmental"
    priority_level = Column(String(20))  # "HIGH", "MEDIUM", "LOW"
    
    # Usage statistics
    usage_count = Column(Integer, default=0)  # How many times used
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))  # Greenleaf admin who created this
    
    # Relationships
    suggested_actions = relationship("SuggestedAction", back_populates="category")
    capar_items = relationship("CAPARItem", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.category_type}')>"
    
    @property
    def total_actions_count(self):
        """Count of suggested actions for this category"""
        return len(self.suggested_actions)
    
    def increment_usage(self):
        """Increment usage count when category is used"""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()