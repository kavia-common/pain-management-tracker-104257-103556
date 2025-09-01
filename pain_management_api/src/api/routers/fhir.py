from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.db import get_db
from src.api.models import User, PainEvent, FHIRExport
from src.api.deps import get_current_user
from src.api.fhir_mapper import create_fhir_bundle, map_pain_event_to_observation

router = APIRouter(prefix="/fhir", tags=["fhir"])

@router.get("/exports/bundle")
async def export_fhir_bundle(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Export all user data and pain events as a FHIR Bundle.
    
    Returns:
        A FHIR Bundle containing Patient and Observation resources
    """
    # Get all pain events for the user
    result = await db.execute(
        select(PainEvent)
        .where(PainEvent.user_id == current_user.id)
        .order_by(PainEvent.timestamp.desc())
    )
    pain_events = result.scalars().all()
    
    # Create FHIR Bundle
    bundle = create_fhir_bundle(current_user, pain_events)
    
    return bundle

@router.post("/exports/pain-event/{pain_event_id}", status_code=status.HTTP_201_CREATED)
async def export_pain_event(
    pain_event_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Export a specific pain event as a FHIR Observation resource.
    
    Parameters:
        pain_event_id: ID of the pain event to export
    Returns:
        FHIR Export record
    """
    # Get pain event
    result = await db.execute(
        select(PainEvent)
        .where(
            PainEvent.id == pain_event_id,
            PainEvent.user_id == current_user.id
        )
    )
    pain_event = result.scalar_one_or_none()
    
    if pain_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pain event not found"
        )
    
    # Create FHIR Observation
    fhir_data = map_pain_event_to_observation(pain_event)
    
    # Save FHIR export
    fhir_export = FHIRExport(
        pain_event_id=pain_event_id,
        fhir_resource_type="Observation",
        fhir_data=fhir_data
    )
    
    db.add(fhir_export)
    await db.commit()
    await db.refresh(fhir_export)
    
    return fhir_export
