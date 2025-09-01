from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from src.api.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pain_events = relationship("PainEvent", back_populates="user")
    provider_access = relationship("ProviderAccess", back_populates="user")

class PainEvent(Base):
    __tablename__ = "pain_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    severity = Column(Float, nullable=False)  # Pain scale (0-10)
    location = Column(String, nullable=False)
    symptoms = Column(JSON)  # Store array of symptoms
    triggers = Column(JSON)  # Store array of triggers
    notes = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="pain_events")
    fhir_exports = relationship("FHIRExport", back_populates="pain_event")

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    specialty = Column(String)
    organization = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider_access = relationship("ProviderAccess", back_populates="provider")

class ProviderAccess(Base):
    __tablename__ = "provider_access"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    access_granted = Column(Boolean, default=False)
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="provider_access")
    provider = relationship("Provider", back_populates="provider_access")

class FHIRExport(Base):
    __tablename__ = "fhir_exports"

    id = Column(Integer, primary_key=True, index=True)
    pain_event_id = Column(Integer, ForeignKey("pain_events.id"), nullable=False)
    fhir_resource_type = Column(String, nullable=False)  # e.g., "Observation"
    fhir_data = Column(JSON, nullable=False)  # Store FHIR JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pain_event = relationship("PainEvent", back_populates="fhir_exports")
