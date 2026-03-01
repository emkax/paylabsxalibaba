"""
PayLabs Merchant Health Intelligence Platform - Backend API

A FastAPI application that provides REST APIs for the merchant health dashboard,
integrating with PayLabs Payment Gateway and Alibaba Cloud AI services.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and models
from database import engine, Base
from models import Transaction, MerchantHealthSnapshot, AIRecommendation, SimulationResult

# Import routers
from api.routes import merchant_router, ai_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="PayLabs Merchant Health Intelligence API",
    description="REST API for merchant health dashboard with AI-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API health check"""
    return {
        "name": "PayLabs Merchant Health Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check database connection
        from database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# Include routers
app.include_router(merchant_router)
app.include_router(ai_router)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true"
    )
