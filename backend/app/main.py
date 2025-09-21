from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .core.config import settings
from .core.database import get_db, create_tables
from .users.routers import router as users_router
from .jobs.routers import router as jobs_router
from .finance.routers import router as finance_router
from .energy.routers import router as energy_router
from .carbon.routers import router as carbon_router
from .ai.routers import router as ai_router
from .policy.routers import router as policy_router

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    openapi_url="/api/v1/openapi.json" if settings.debug else None,
    docs_url="/api/v1/docs" if settings.debug else None,
    redoc_url="/api/v1/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://wakanda-mandate.gov"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(finance_router, prefix="/api/v1")
app.include_router(energy_router, prefix="/api/v1")
app.include_router(carbon_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(policy_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    create_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Wakanda Digital Government Platform API",
        "version": settings.api_version,
        "environment": settings.environment,
        "status": "operational"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.api_version,
        "environment": settings.environment
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "title": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "modules": [
            {
                "name": "Users",
                "description": "User management and authentication",
                "endpoints": "/api/v1/users"
            },
            {
                "name": "Jobs",
                "description": "Government job postings and applications",
                "endpoints": "/api/v1/jobs"
            },
            {
                "name": "Finance",
                "description": "Budget management and financial analytics",
                "endpoints": "/api/v1/finance"
            },
            {
                "name": "Energy",
                "description": "Energy consumption and efficiency tracking",
                "endpoints": "/api/v1/energy"
            },
            {
                "name": "Carbon",
                "description": "Carbon emissions monitoring and offset tracking",
                "endpoints": "/api/v1/carbon"
            },
            {
                "name": "AI",
                "description": "AI-powered chat and analysis with OpenRouter",
                "endpoints": "/api/v1/ai"
            },
            {
                "name": "Policy",
                "description": "Policy document management and search",
                "endpoints": "/api/v1/policy"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )