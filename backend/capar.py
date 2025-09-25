"""
CAPAR Models
Main CAPAR and CAPAR Items models
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, Enum, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from ..database import Base


class CAPARStatus(str, enum.Enum):
    """CAPAR status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ItemStatus(str, enum.Enum):
    """Individual CAPAR item status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class Priority(str, enum.Enum):
    """Priority levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CAPAR(Base):
    """Main CAPAR document"""
    
    __tablename__ = "capars"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Company relationship
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="capars")
    
    # CAPAR basic info
    audit_date = Column(Date, nullable=False)
    audit_type = Column(String(255), nullable=False)
    reference_no = Column(String(255), unique=True, index=True)
    
    # Status
    status = Column(Enum(CAPARStatus), default=CAPARStatus.DRAFT)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User who created this CAPAR
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by_user = relationship("User", back_populates="created_capars")
    
    # Relationships
    items = relationship("CAPARItem", back_populates="capar", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CAPAR(id={self.id}, ref='{self.reference_no}', status='{self.status}')>"
    
    @property
    def total_items_count(self):
        """Total number of CAPAR items"""
        return len(self.items)
    
    @property
    def completed_items_count(self):
        """Number of completed items"""
        return len([item for item in self.items if item.status == ItemStatus.COMPLETED])
    
    @property
    def completion_percentage(self):
        """Completion percentage"""
        if self.total_items_count == 0:
            return 0
        return int((self.completed_items_count / self.total_items_count) * 100)
    
    @property
    def overdue_items_count(self):
        """Number of overdue items"""
        today = date.today()
        return len([
            item for item in self.items 
            if item.due_date and item.due_date < today and item.status != ItemStatus.COMPLETED
        ])
    
    @property
    def high_priority_items_count(self):
        """Number of high priority items"""
        return len([item for item in self.items if item.priority == Priority.HIGH])


class CAPARItem(Base):
    """Individual finding and corrective action"""
    
    __tablename__ = "capar_items"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # CAPAR relationship
    capar_id = Column(UUID(as_uuid=True), ForeignKey("capars.id"), nullable=False)
    capar = relationship("CAPAR", back_populates="items")
    
    # Finding details
    finding = Column(Text, nullable=False)
    corrective_action = Column(Text, nullable=False)
    
    # Category relationship
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="capar_items")
    
    # Responsibility and timing
    responsible_person = Column(String(255), nullable=False)
    due_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    
    # Status and priority
    status = Column(Enum(ItemStatus), default=ItemStatus.NOT_STARTED)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Evidence and notes
    evidence_files = Column(JSON)  # Store file paths/URLs as JSON array
    completion_notes = Column(Text)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CAPARItem(id={self.id}, status='{self.status}', priority='{self.priority}')>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if item is overdue"""
        if not self.due_date or self.status == ItemStatus.COMPLETED:
            return False
        return self.due_date < date.today()
    
    @property
    def days_remaining(self) -> int:
        """Days remaining until due date (negative if overdue)"""
        if not self.due_date:
            return 0
        delta = self.due_date - date.today()
        return delta.days
    
    @property
    def days_to_complete(self) -> int:
        """Days taken to complete (if completed)"""
        if not self.completion_date or not self.capar.created_at:
            return 0
        delta = self.completion_date - self.capar.created_at.date()
        return delta.days
    
    def mark_completed(self, completion_notes: str = None):
        """Mark item as completed"""
        self.status = ItemStatus.COMPLETED
        self.completion_date = date.today()
        self.completion_notes = completion_notes
        self.updated_at = datetime.utcnow()