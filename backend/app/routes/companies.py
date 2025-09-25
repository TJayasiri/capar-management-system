"""
Company Management Routes
Create and manage factory/company records
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from ..database import get_db
from ..models import Company, User
from .auth import get_current_user

router = APIRouter()

# Pydantic schemas
class CompanyCreate(BaseModel):
    name: str
    address: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry_type: Optional[str] = None
    company_size: Optional[str] = None

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry_type: Optional[str] = None
    company_size: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Routes
@router.get("/test")
async def test_companies():
    """Test companies routes"""
    return {
        "message": "Companies routes working",
        "endpoints": {
            "create": "POST /api/companies/",
            "list": "GET /api/companies/",
            "get": "GET /api/companies/{company_id}"
        }
    }

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        country=company_data.country,
        contact_email=company_data.contact_email,
        contact_phone=company_data.contact_phone,
        industry_type=company_data.industry_type,
        company_size=company_data.company_size
    )
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all companies"""
    
    companies = db.query(Company).filter(Company.is_active == True).offset(skip).limit(limit).all()
    return companies

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific company by ID"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company