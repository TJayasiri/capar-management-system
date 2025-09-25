"""
Suggested Action Model
Template actions for common findings
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class SuggestedAction(Base):
    """Suggested corrective actions for categories"""
    
    __tablename__ = "suggested_actions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Category relationship
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="suggested_actions")
    
    # Keywords for matching findings
    finding_keywords = Column(Text)  # Comma-separated keywords like "eye wash,station,missing"
    
    # Suggested action details
    suggested_action = Column(Text, nullable=False)
    typical_days = Column(Integer, default=30)  # Typical completion time in days
    typical_priority = Column(String(20), default="MEDIUM")  # "HIGH", "MEDIUM", "LOW"
    
    # Additional context
    responsible_role = Column(String(100))  # Typical responsible role
    evidence_required = Column(Text)  # What evidence is typically needed
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer, default=0)  # Percentage of successful implementations
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))  # Greenleaf admin who created this
    
    def __repr__(self):
        return f"<SuggestedAction(id={self.id}, category='{self.category.name if self.category else 'None'}')>"
    
    @property
    def keywords_list(self):
        """Return keywords as a list"""
        if self.finding_keywords:
            return [kw.strip().lower() for kw in self.finding_keywords.split(",")]
        return []
    
    def matches_finding(self, finding_text: str) -> int:
        """
        Check how well this suggested action matches a finding
        Returns a score (0-100) based on keyword matches
        """
        if not finding_text or not self.finding_keywords:
            return 0
        
        finding_lower = finding_text.lower()
        keywords = self.keywords_list
        
        matches = 0
        for keyword in keywords:
            if keyword in finding_lower:
                matches += 1
        
        # Return percentage match
        if keywords:
            return int((matches / len(keywords)) * 100)
        return 0
    
    def increment_usage(self):
        """Increment usage count when suggestion is used"""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()