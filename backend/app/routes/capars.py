# backend/app/routes/capars.py
"""
CAPAR Management Routes
Create, read, update, and track CAPARs and CAPAR items
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models import CAPAR, CAPARItem, Company, CAPARStatus, ItemStatus, Priority, User
from ..auth import get_current_user

router = APIRouter()

# Pydantic schemas
class CAPARItemCreate(BaseModel):
    finding: str
    corrective_action: str
    responsible_person: str
    due_date: date
    priority: Priority = Priority.MEDIUM
    category_id: Optional[str] = None

class CAPARItemResponse(BaseModel):
    id: int  # Changed from UUID to int
    finding: str
    corrective_action: str
    responsible_person: str
    due_date: date
    status: ItemStatus
    priority: Priority
    completion_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CAPARCreate(BaseModel):
    company_id: int  # Changed from UUID to int
    title: str
    description: str
    audit_date: date
    audit_type: str
    reference_no: str
    items: List[CAPARItemCreate] = []

class CAPARResponse(BaseModel):
    id: int  # Changed from UUID to int
    company_id: int
    capar_number: str
    title: str
    description: str
    audit_date: date
    audit_type: str
    reference_no: str
    status: CAPARStatus
    created_date: datetime
    items: List[CAPARItemResponse] = []
    
    class Config:
        from_attributes = True

class CAPARUpdateStatus(BaseModel):
    status: CAPARStatus

class ItemUpdateStatus(BaseModel):
    status: ItemStatus
    completion_notes: Optional[str] = None

# Routes
@router.get("/test")
async def test_capars():
    """Test CAPAR routes"""
    return {
        "message": "CAPAR routes working",
        "endpoints": {
            "create": "POST /api/capars/",
            "list": "GET /api/capars/",
            "get": "GET /api/capars/{capar_id}",
            "update_status": "PATCH /api/capars/{capar_id}/status"
        }
    }

@router.post("/", response_model=CAPARResponse)
async def create_capar(
    capar_data: CAPARCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new CAPAR with items"""
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == capar_data.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if reference number already exists
    existing = db.query(CAPAR).filter(CAPAR.reference_no == capar_data.reference_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reference number already exists"
        )
    
    # Generate CAPAR number
    capar_count = db.query(CAPAR).count() + 1
    capar_number = f"CAPAR-{datetime.now().year}-{capar_count:04d}"
    
    # Create CAPAR
    db_capar = CAPAR(
        capar_number=capar_number,
        title=capar_data.title,
        description=capar_data.description,
        company_id=capar_data.company_id,
        audit_date=capar_data.audit_date,
        audit_type=capar_data.audit_type,
        reference_no=capar_data.reference_no,
        created_by_id=current_user.id,
        capar_type="corrective"  # Default value
    )
    
    db.add(db_capar)
    db.commit()
    db.refresh(db_capar)
    
    # Create CAPAR items
    for item_data in capar_data.items:
        db_item = CAPARItem(
            capar_id=db_capar.id,
            finding=item_data.finding,
            corrective_action=item_data.corrective_action,
            responsible_person=item_data.responsible_person,
            due_date=item_data.due_date,
            priority=item_data.priority,
            category_id=item_data.category_id
        )
        db.add(db_item)
    
    db.commit()
    
    # Refresh to get items
    db.refresh(db_capar)
    
    return db_capar

@router.get("/", response_model=List[CAPARResponse])
async def list_capars(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CAPARStatus] = None,
    company_id: Optional[int] = None,  # Changed from UUID to int
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List CAPARs with filtering"""
    
    query = db.query(CAPAR)
    
    # Apply filters
    if status:
        query = query.filter(CAPAR.status == status)
    if company_id:
        query = query.filter(CAPAR.company_id == company_id)
    
    # Apply pagination
    capars = query.offset(skip).limit(limit).all()
    
    return capars

@router.get("/{capar_id}", response_model=CAPARResponse)
async def get_capar(
    capar_id: int,  # Changed from UUID to int
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific CAPAR by ID"""
    
    capar = db.query(CAPAR).filter(CAPAR.id == capar_id).first()
    if not capar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPAR not found"
        )
    
    return capar

@router.patch("/{capar_id}/status", response_model=CAPARResponse)
async def update_capar_status(
    capar_id: int,  # Changed from UUID to int
    status_update: CAPARUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CAPAR status"""
    
    capar = db.query(CAPAR).filter(CAPAR.id == capar_id).first()
    if not capar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPAR not found"
        )
    
    capar.status = status_update.status
    capar.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(capar)
    
    return capar

@router.patch("/items/{item_id}/status", response_model=CAPARItemResponse)
async def update_item_status(
    item_id: int,  # Changed from UUID to int
    status_update: ItemUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CAPAR item status"""
    
    item = db.query(CAPARItem).filter(CAPARItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPAR item not found"
        )
    
    item.status = status_update.status
    item.updated_at = datetime.utcnow()
    
    # If marking as completed, set completion date
    if status_update.status == ItemStatus.COMPLETED:
        item.completion_date = date.today()
        if status_update.completion_notes:
            item.completion_notes = status_update.completion_notes
    
    db.commit()
    db.refresh(item)
    
    return item

@router.get("/{capar_id}/summary")
async def get_capar_summary(
    capar_id: int,  # Changed from UUID to int
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CAPAR summary with progress statistics"""
    
    capar = db.query(CAPAR).filter(CAPAR.id == capar_id).first()
    if not capar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CAPAR not found"
        )
    
    items = db.query(CAPARItem).filter(CAPARItem.capar_id == capar_id).all()
    
    total_items = len(items)
    completed_items = len([item for item in items if item.status == ItemStatus.COMPLETED])
    overdue_items = len([
        item for item in items 
        if item.due_date < date.today() and item.status != ItemStatus.COMPLETED
    ])
    high_priority_items = len([item for item in items if item.priority == Priority.HIGH])
    
    completion_percentage = int((completed_items / total_items) * 100) if total_items > 0 else 0
    
    return {
        "capar_id": capar_id,
        "capar_number": capar.capar_number,
        "reference_no": capar.reference_no,
        "audit_type": capar.audit_type,
        "status": capar.status,
        "total_items": total_items,
        "completed_items": completed_items,
        "overdue_items": overdue_items,
        "high_priority_items": high_priority_items,
        "completion_percentage": completion_percentage,
        "created_at": capar.created_date
    }

# Smart Suggestions Engine
@router.get("/suggestions/actions")
async def get_action_suggestions(
    finding_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI-powered action suggestions based on audit findings"""
    
    # Common finding patterns and suggested actions
    suggestions_db = {
        "safety": {
            "keywords": ["safety", "hazard", "injury", "accident", "ppe", "protective equipment", "unsafe"],
            "actions": [
                "Conduct immediate safety risk assessment",
                "Implement mandatory PPE policy and training",
                "Install safety signage and warning systems",
                "Review and update safety procedures",
                "Provide comprehensive safety training to all staff"
            ]
        },
        "documentation": {
            "keywords": ["document", "record", "procedure", "missing", "incomplete", "paperwork"],
            "actions": [
                "Create standardized documentation templates",
                "Implement document control system",
                "Train staff on proper record keeping procedures",
                "Schedule regular documentation audits",
                "Digitize paper-based processes"
            ]
        },
        "training": {
            "keywords": ["training", "competency", "skill", "knowledge", "awareness", "education"],
            "actions": [
                "Develop comprehensive training program",
                "Schedule regular competency assessments",
                "Create training materials and resources",
                "Implement mentorship program",
                "Track training completion and effectiveness"
            ]
        },
        "quality": {
            "keywords": ["quality", "defect", "nonconforming", "specification", "standard", "reject"],
            "actions": [
                "Implement quality control checkpoints",
                "Review and update quality procedures",
                "Enhance inspection processes",
                "Provide quality training to operators",
                "Install quality monitoring systems"
            ]
        }
    }
    
    finding_lower = finding_text.lower()
    matched_suggestions = []
    matched_categories = []
    
    # Find matching categories
    for category, data in suggestions_db.items():
        if any(keyword in finding_lower for keyword in data["keywords"]):
            matched_suggestions.extend(data["actions"])
            matched_categories.append(category)
    
    # Remove duplicates
    unique_suggestions = list(dict.fromkeys(matched_suggestions))
    
    # If no match, provide general suggestions
    if not unique_suggestions:
        unique_suggestions = [
            "Conduct thorough root cause analysis",
            "Review current procedures and policies",
            "Provide additional staff training",
            "Implement monitoring and verification system",
            "Schedule follow-up assessment and review"
        ]
        matched_categories = ["general"]
    
    return {
        "suggestions": unique_suggestions[:6],
        "categories": matched_categories,
        "finding_analyzed": finding_text
    }