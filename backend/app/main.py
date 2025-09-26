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

# Import routers with error handling
try:
    from .routes.auth import router as auth_router
    AUTH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Auth routes not available: {e}")
    AUTH_AVAILABLE = False

try:
    from .routes.capars import router as capars_router
    CAPARS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  CAPARS routes not available: {e}")
    CAPARS_AVAILABLE = False

try:
    from .routes.companies import router as companies_router
    COMPANIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Companies routes not available: {e}")
    COMPANIES_AVAILABLE = False

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
        
        # CREATE TABLES EXPLICITLY - Add this
        from .models.capar import Base
        from .database import engine
        Base.metadata.create_all(bind=engine)
        print("✅ User tables created from models")
        
        # Initialize database (any additional setup)
        init_db()
        
        print("✅ Application startup completed successfully")
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Shutting down CAPAR Management System")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application startup and shutdown events"""
#     # Startup
#     print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
#     
#     try:
#         # Validate settings
#         validate_settings()
#         
#         # Check database connection
#         check_db_connection()
#         
#         # Initialize database (create tables)
#         init_db()
#         
#         print("✅ Application startup completed successfully")
#         
#     except Exception as e:
#         print(f"❌ Application startup failed: {e}")
#         raise
#     
#     yield
#     
#     # Shutdown
#     print("👋 Shutting down CAPAR Management System")

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

# Include routers conditionally
if AUTH_AVAILABLE:
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    print("✅ Auth routes included")

if CAPARS_AVAILABLE:
    app.include_router(capars_router, prefix="/api/capars", tags=["CAPARs"])
    print("✅ CAPARS routes included")

if COMPANIES_AVAILABLE:
    app.include_router(companies_router, prefix="/api/companies", tags=["Companies"])
    print("✅ Companies routes included")

# Fallback CAPAR endpoints if routes fail to load
if not CAPARS_AVAILABLE:
    @app.get("/api/capars/test")
    async def fallback_capars_test():
        return {"message": "Fallback CAPAR endpoint - routes not loaded properly"}
    
    @app.get("/api/capars/")
    async def fallback_list_capars():
        return {"capars": [], "message": "Fallback endpoint - fix route imports"}

# Root endpoint
@app.get("/")
async def root():
    """Welcome message and API info"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running",
        "routes_loaded": {
            "auth": AUTH_AVAILABLE,
            "capars": CAPARS_AVAILABLE,
            "companies": COMPANIES_AVAILABLE
        },
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
            "database": db_health,
            "routes_status": {
                "auth": AUTH_AVAILABLE,
                "capars": CAPARS_AVAILABLE,
                "companies": COMPANIES_AVAILABLE
            }
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
    available_endpoints = {}
    
    if AUTH_AVAILABLE:
        available_endpoints["auth"] = "/api/auth/"
    if CAPARS_AVAILABLE:
        available_endpoints["capars"] = "/api/capars/"
    if COMPANIES_AVAILABLE:
        available_endpoints["companies"] = "/api/companies/"
    
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "endpoints": available_endpoints,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )