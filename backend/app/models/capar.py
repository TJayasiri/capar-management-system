# backend/app/models/capar.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
import uuid

Base = declarative_base()

class CAPARStatus(enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress" 
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    CLOSED = "closed"

class CAPARType(enum.Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"
    BOTH = "both"

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ItemStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    capars = relationship("CAPAR", foreign_keys="CAPAR.created_by_id", back_populates="created_by")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    capars = relationship("CAPAR", back_populates="company")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SuggestedAction(Base):
    __tablename__ = "suggested_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    action_text = Column(Text, nullable=False)
    keywords = Column(Text)  # JSON string of keywords
    created_at = Column(DateTime, default=datetime.utcnow)

class CAPAR(Base):
    __tablename__ = "capars"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    company_id = Column(Integer, ForeignKey("companies.id"))
    audit_date = Column(Date, nullable=False)
    audit_type = Column(String(100), nullable=False)
    reference_no = Column(String(100), unique=True, nullable=False)
    
    # Status and metadata
    status = Column(Enum(CAPARStatus), default=CAPARStatus.DRAFT)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="capars")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="capars")
    items = relationship("CAPARItem", back_populates="capar", cascade="all, delete-orphan")

class CAPARItem(Base):
    __tablename__ = "capar_items"
    
    id = Column(Integer, primary_key=True, index=True)
    capar_id = Column(Integer, ForeignKey("capars.id"))
    
    # Item details
    finding = Column(Text, nullable=False)
    corrective_action = Column(Text, nullable=False)
    responsible_person = Column(String(100), nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Status and priority
    status = Column(Enum(ItemStatus), default=ItemStatus.PENDING)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Optional fields
    category_id = Column(Integer, ForeignKey("categories.id"))
    completion_date = Column(Date)
    completion_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capar = relationship("CAPAR", back_populates="items")
    category = relationship("Category")