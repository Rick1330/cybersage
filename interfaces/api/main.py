"""
FastAPI Application Entry Point

This module initializes and configures the FastAPI application with middleware,
error handlers, and route registration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.logging_service import LoggingService
from .routes import router
import yaml

# Load configuration
with open("configs/settings.yaml") as f:
    config = yaml.safe_load(f)

# Initialize services
logging_service = LoggingService(
    config_path="configs/logging_config.yaml"
)
logger = logging_service.get_logger()

# Create FastAPI app
app = FastAPI(
    title="CyberSage API",
    description="AI-powered cybersecurity assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["api"]["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
