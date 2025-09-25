# backend/app/models/capar.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

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
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    capars = relationship("CAPAR", back_populates="created_by")

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    contact_person = Column(String(100))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    capars = relationship("CAPAR", back_populates="company")

class CAPAR(Base):
    __tablename__ = "capars"
    
    id = Column(Integer, primary_key=True, index=True)
    capar_number = Column(String(50), unique=True, index=True)
    
    # Basic info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    reference_no = Column(String(100), unique=True)
    audit_date = Column(Date)
    audit_type = Column(String(100))
    
    # Status and priority
    capar_type = Column(Enum(CAPARType), nullable=False)
    status = Column(Enum(CAPARStatus), default=CAPARStatus.DRAFT)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Audit information
    audit_finding = Column(Text)
    root_cause = Column(Text)
    immediate_action = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    
    # Dates
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    target_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Assignments
    assigned_to = Column(String(100))
    department = Column(String(100))
    
    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="capars")
    created_by = relationship("User", back_populates="capars")
    items = relationship("CAPARItem", back_populates="capar", cascade="all, delete-orphan")
    attachments = relationship("CAPARAttachment", back_populates="capar")

class CAPARItem(Base):
    __tablename__ = "capar_items"
    
    id = Column(Integer, primary_key=True, index=True)
    capar_id = Column(Integer, ForeignKey("capars.id"))
    
    # Item details
    finding = Column(Text, nullable=False)
    corrective_action = Column(Text, nullable=False)
    responsible_person = Column(String(100), nullable=False)
    
    # Status and priority
    status = Column(Enum(ItemStatus), default=ItemStatus.PENDING)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Dates
    due_date = Column(Date, nullable=False)
    completion_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional info
    completion_notes = Column(Text)
    category_id = Column(String(100))  # For categorizing findings
    
    # Relationship
    capar = relationship("CAPAR", back_populates="items")

class CAPARAttachment(Base):
    __tablename__ = "capar_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    capar_id = Column(Integer, ForeignKey("capars.id"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    content_type = Column(String(100))
    
    capar = relationship("CAPAR", back_populates="attachments")