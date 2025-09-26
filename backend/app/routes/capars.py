"""
CAPAR Management Routes
"""
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import (
    CAPAR,
    CAPARItem,
    Company,
    CAPARStatus,
    ItemStatus,
    Priority,
    User,
)
from app.auth import get_current_user

#router = APIRouter(prefix="/capars", tags=["capars"])
router = APIRouter(tags=["capars"])


# -------- Pydantic Schemas --------
class CAPARItemCreate(BaseModel):
    finding: str
    corrective_action: str
    responsible_person: str
    due_date: date
    priority: Priority = Priority.MEDIUM
    category_id: Optional[int] = None

class CAPARItemResponse(BaseModel):
    id: int
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
    company_id: int
    audit_date: date
    audit_type: str
    reference_no: str
    items: List[CAPARItemCreate] = Field(default_factory=list)

class CAPARResponse(BaseModel):
    id: int
    company_id: int
    audit_date: date
    audit_type: str
    reference_no: str
    status: CAPARStatus
    created_at: datetime
    items: List[CAPARItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class CAPARUpdateStatus(BaseModel):
    status: CAPARStatus

class ItemUpdateStatus(BaseModel):
    status: ItemStatus
    completion_notes: Optional[str] = None

# -------- Routes --------
@router.get("/test")
async def test_capars():
    return {
        "message": "CAPAR routes working",
        "endpoints": {
            "create": "POST /api/capars/",
            "list": "GET /api/capars/",
            "get": "GET /api/capars/{capar_id}",
            "suggestions": "GET /api/capars/suggestions/actions",
        },
    }

@router.post("/", response_model=CAPARResponse, status_code=status.HTTP_201_CREATED)
async def create_capar(
    capar_data: CAPARCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.id == capar_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    existing = db.query(CAPAR).filter(CAPAR.reference_no == capar_data.reference_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reference number already exists")

    db_capar = CAPAR(
        company_id=capar_data.company_id,
        audit_date=capar_data.audit_date,
        audit_type=capar_data.audit_type,
        reference_no=capar_data.reference_no,
        created_by_id=current_user.id,
    )
    db.add(db_capar)
    db.commit()
    db.refresh(db_capar)

    # Bulk create items (simple loop; replace with bulk_save_objects if desired)
    for item in capar_data.items:
        db_item = CAPARItem(
            capar_id=db_capar.id,
            finding=item.finding,
            corrective_action=item.corrective_action,
            responsible_person=item.responsible_person,
            due_date=item.due_date,
            priority=item.priority,
            category_id=item.category_id,
        )
        db.add(db_item)

    db.commit()
    # Eager load items for response
    capar_with_items = (
        db.query(CAPAR)
        .options(selectinload(CAPAR.items))
        .filter(CAPAR.id == db_capar.id)
        .first()
    )
    return capar_with_items

@router.get("/", response_model=List[CAPARResponse])
async def list_capars(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_: Optional[CAPARStatus] = Query(None, alias="status"),
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(CAPAR).options(selectinload(CAPAR.items))
    if status_ is not None:
        q = q.filter(CAPAR.status == status_)
    if company_id is not None:
        q = q.filter(CAPAR.company_id == company_id)

    capars = q.order_by(CAPAR.created_at.desc()).offset(skip).limit(limit).all()
    return capars

@router.get("/{capar_id}", response_model=CAPARResponse)
async def get_capar(
    capar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    capar = (
        db.query(CAPAR)
        .options(selectinload(CAPAR.items))
        .filter(CAPAR.id == capar_id)
        .first()
    )
    if not capar:
        raise HTTPException(status_code=404, detail="CAPAR not found")
    return capar

@router.get("/suggestions/actions")
async def get_action_suggestions(
    finding_text: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suggestions_db = {
        "safety": {
            "keywords": ["safety", "hazard", "injury", "accident", "ppe"],
            "actions": [
                "Conduct immediate safety risk assessment",
                "Implement mandatory PPE policy and training",
                "Install safety signage and warning systems",
            ],
        },
        "quality": {
            "keywords": ["quality", "defect", "nonconforming", "specification"],
            "actions": [
                "Implement quality control checkpoints",
                "Review and update quality procedures",
                "Enhance inspection processes",
            ],
        },
    }

    text = finding_text.lower()
    matched = []
    for data in suggestions_db.values():
        if any(k in text for k in data["keywords"]):
            matched.extend(data["actions"])

    if not matched:
        matched = [
            "Conduct root cause analysis",
            "Review current procedures",
            "Provide staff training",
        ]

    return {"suggestions": matched[:5]}



# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from datetime import date, datetime
# from typing import List, Optional
# from pydantic import BaseModel

# from app.database import get_db  # Changed from ..database
# from app.models import CAPAR, CAPARItem, Company, CAPARStatus, ItemStatus, Priority, User  # Changed from ..models
# from app.auth import get_current_user  # Changed from ..auth

# router = APIRouter()

# # Pydantic schemas
# class CAPARItemCreate(BaseModel):
#     finding: str
#     corrective_action: str
#     responsible_person: str
#     due_date: date
#     priority: Priority = Priority.MEDIUM
#     category_id: Optional[int] = None

# class CAPARItemResponse(BaseModel):
#     id: int
#     finding: str
#     corrective_action: str
#     responsible_person: str
#     due_date: date
#     status: ItemStatus
#     priority: Priority
#     completion_date: Optional[date] = None
#     created_at: datetime
#     
#     class Config:
#         from_attributes = True

# class CAPARCreate(BaseModel):
#     company_id: int
#     audit_date: date
#     audit_type: str
#     reference_no: str
#     items: List[CAPARItemCreate] = []

# class CAPARResponse(BaseModel):
#     id: int
#     company_id: int
#     audit_date: date
#     audit_type: str
#     reference_no: str
#     status: CAPARStatus
#     created_at: datetime
#     items: List[CAPARItemResponse] = []
#     
#     class Config:
#         from_attributes = True

# class CAPARUpdateStatus(BaseModel):
#     status: CAPARStatus

# class ItemUpdateStatus(BaseModel):
#     status: ItemStatus
#     completion_notes: Optional[str] = None

# @router.get("/test")
# async def test_capars():
#     return {
#         "message": "CAPAR routes working",
#         "endpoints": {
#             "create": "POST /api/capars/",
#             "list": "GET /api/capars/",
#             "get": "GET /api/capars/{capar_id}",
#             "suggestions": "GET /api/capars/suggestions/actions"
#         }
#     }

# @router.post("/", response_model=CAPARResponse)
# async def create_capar(
#     capar_data: CAPARCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     company = db.query(Company).filter(Company.id == capar_data.company_id).first()
#     if not company:
#         raise HTTPException(status_code=404, detail="Company not found")
#     
#     existing = db.query(CAPAR).filter(CAPAR.reference_no == capar_data.reference_no).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Reference number already exists")
#     
#     db_capar = CAPAR(
#         company_id=capar_data.company_id,
#         audit_date=capar_data.audit_date,
#         audit_type=capar_data.audit_type,
#         reference_no=capar_data.reference_no,
#         created_by_id=current_user.id
#     )
#     
#     db.add(db_capar)
#     db.commit()
#     db.refresh(db_capar)
#     
#     for item_data in capar_data.items:
#         db_item = CAPARItem(
#             capar_id=db_capar.id,
#             finding=item_data.finding,
#             corrective_action=item_data.corrective_action,
#             responsible_person=item_data.responsible_person,
#             due_date=item_data.due_date,
#             priority=item_data.priority,
#             category_id=item_data.category_id
#         )
#         db.add(db_item)
#     
#     db.commit()
#     db.refresh(db_capar)
#     return db_capar

# @router.get("/", response_model=List[CAPARResponse])
# async def list_capars(
#     skip: int = 0,
#     limit: int = 100,
#     status: Optional[CAPARStatus] = None,
#     company_id: Optional[int] = None,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     query = db.query(CAPAR)
#     if status:
#         query = query.filter(CAPAR.status == status)
#     if company_id:
#         query = query.filter(CAPAR.company_id == company_id)
#     
#     capars = query.offset(skip).limit(limit).all()
#     return capars

# @router.get("/{capar_id}", response_model=CAPARResponse)
# async def get_capar(
#     capar_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     capar = db.query(CAPAR).filter(CAPAR.id == capar_id).first()
#     if not capar:
#         raise HTTPException(status_code=404, detail="CAPAR not found")
#     return capar

# @router.get("/suggestions/actions")
# async def get_action_suggestions(
#     finding_text: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     suggestions_db = {
#         "safety": {
#             "keywords": ["safety", "hazard", "injury", "accident", "ppe"],
#             "actions": [
#                 "Conduct immediate safety risk assessment",
#                 "Implement mandatory PPE policy and training",
#                 "Install safety signage and warning systems"
#             ]
#         },
#         "quality": {
#             "keywords": ["quality", "defect", "nonconforming", "specification"],
#             "actions": [
#                 "Implement quality control checkpoints",
#                 "Review and update quality procedures",
#                 "Enhance inspection processes"
#             ]
#         }
#     }
#     
#     finding_lower = finding_text.lower()
#     matched_suggestions = []
#     
#     for category, data in suggestions_db.items():
#         if any(keyword in finding_lower for keyword in data["keywords"]):
#             matched_suggestions.extend(data["actions"])
#     
#     if not matched_suggestions:
#         matched_suggestions = [
#             "Conduct root cause analysis",
#             "Review current procedures",
#             "Provide staff training"
#         ]
#     
#     return {"suggestions": matched_suggestions[:5]}