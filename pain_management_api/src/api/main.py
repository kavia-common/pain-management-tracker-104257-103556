import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db import get_db, engine, Base
from src.api.routers import auth, pain_events, fhir

# API Tags metadata
tags_metadata = [
    {
        "name": "auth",
        "description": "Operations for user authentication and profile management"
    },
    {
        "name": "pain-events",
        "description": "Operations for managing pain diary entries including severity, location, symptoms, and triggers"
    },
    {
        "name": "fhir",
        "description": "FHIR-HL7 data export operations for healthcare interoperability"
    }
]

# Get CORS origins from environment
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(
    title="Pain Management API",
    description="""
    Backend API for a Pain Management Diary application that enables users to track and manage pain events.
    Features include:
    - User authentication and profile management
    - Pain event recording with severity, location, symptoms, and triggers
    - FHIR-HL7 data export for healthcare interoperability
    - Secure data sharing with healthcare providers
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Pain Management Support",
        "email": "support@painmanagement.example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(auth.router)
app.include_router(pain_events.router)
app.include_router(fhir.router)

@app.on_event("startup")
async def startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Test database connection
        await db.execute("SELECT 1")
        await db.commit()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
