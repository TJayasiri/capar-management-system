"""
Company Management Routes
Create and manage factory/company records
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import Company, User
from ..auth import get_current_user

router = APIRouter(tags=["companies"])

# -------------------------
# Pydantic Schemas
# -------------------------
class CompanyCreate(BaseModel):
    name: str
    address: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# -------------------------
# Routes
# -------------------------
@router.get("/test")
async def test_companies():
    """Health-check for companies routes."""
    return {
        "message": "Companies routes working",
        "endpoints": {
            "create": "POST /api/companies/",
            "list": "GET /api/companies/?skip=0&limit=100",
            "get": "GET /api/companies/{company_id}",
            "update": "PUT /api/companies/{company_id}",
            "delete": "DELETE /api/companies/{company_id}"
        },
    }

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new company"""
    
    # Check if company name already exists
    existing = db.query(Company).filter(Company.name == company_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name already exists"
        )
    
    # Create company
    db_company = Company(
        name=company_data.name,
        address=company_data.address,
        contact_person=company_data.contact_person,
        email=company_data.email,
        phone=company_data.phone
    )
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all companies with optional search"""
    
    query = db.query(Company)
    
    # Add search functionality
    if search:
        query = query.filter(
            Company.name.contains(search) |
            Company.contact_person.contains(search) |
            Company.email.contains(search)
        )
    
    companies = query.offset(skip).limit(limit).all()
    return companies

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific company by ID"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Company not found"
        )
    
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a company"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update only provided fields
    update_data = company_data.dict(exclude_unset=True)
    
    # Check for duplicate name if name is being updated
    if "name" in update_data:
        existing = db.query(Company).filter(
            Company.name == update_data["name"],
            Company.id != company_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name already exists"
            )
    
    # Apply updates
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a company"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if company has associated CAPARs
    from ..models import CAPAR
    capar_count = db.query(CAPAR).filter(CAPAR.company_id == company_id).count()
    if capar_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete company with {capar_count} associated CAPARs"
        )
    
    db.delete(company)
    db.commit()
    
    return

@router.get("/{company_id}/capars")
async def get_company_capars(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all CAPARs for a specific company"""
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    from ..models import CAPAR
    capars = db.query(CAPAR).filter(
        CAPAR.company_id == company_id
    ).offset(skip).limit(limit).all()
    
    return {
        "company": {
            "id": company.id,
            "name": company.name
        },
        "capars": capars,
        "total_capars": len(capars)
    }