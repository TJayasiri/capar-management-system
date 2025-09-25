"""
CAPAR Management System - Main FastAPI Application
Entry point for the backend API
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Import our modules
from .config import settings, validate_settings
from .database import init_db, check_db_connection, get_db_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    try:
        # Validate settings
        validate_settings()
        
        # Check database connection
        check_db_connection()
        
        # Initialize database (create tables)
        init_db()
        
        print("✅ Application startup completed successfully")
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Shutting down CAPAR Management System")


# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Corrective Action Preventive Action Request Management System",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Welcome message and API info"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled in production"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    try:
        db_health = await get_db_health()
        
        return {
            "status": "healthy",
            "app": {
                "name": settings.app_name,
                "version": settings.app_version,
                "debug": settings.debug
            },
            "database": db_health
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# API Info endpoint
@app.get("/api/info")
async def api_info():
    """API information and available endpoints"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "endpoints": {
            "auth": "/api/auth/",
            "companies": "/api/companies/",
            "capars": "/api/capars/",
            "categories": "/api/categories/",
            "users": "/api/users/"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "Something went wrong"
        }
    )


# Include routers (we'll add these later)
# from .routes import auth, companies, capars, categories, users
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
# app.include_router(capars.router, prefix="/api/capars", tags=["CAPARs"])
# app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
# app.include_router(users.router, prefix="/api/users", tags=["Users"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )