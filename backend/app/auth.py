# backend/app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models.capar import User

security = HTTPBearer()

# Temporary simple auth - you can enhance this later
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # For testing - create a default user if none exists
    user = db.query(User).first()
    if not user:
        user = User(
            username="admin",
            email="admin@capar.com", 
            hashed_password="temp_hash",
            is_active=1
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

