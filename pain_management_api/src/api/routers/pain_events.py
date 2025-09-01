from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.db import get_db
from src.api.models import User, PainEvent
from src.api.schemas import PainEventCreate, PainEventUpdate, PainEventInDB
from src.api.deps import get_current_user

router = APIRouter(prefix="/pain-events", tags=["pain-events"])

@router.post("/", response_model=PainEventInDB, status_code=status.HTTP_201_CREATED)
async def create_pain_event(
    pain_event: PainEventCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new pain event for the authenticated user.
    
    Parameters:
    - severity: Pain scale (0-10)
    - location: Body location of pain
    - symptoms: List of symptoms
    - triggers: List of triggers
    - notes: Optional additional notes
    """
    db_pain_event = PainEvent(
        **pain_event.model_dump(),
        user_id=current_user.id
    )
    
    db.add(db_pain_event)
    await db.commit()
    await db.refresh(db_pain_event)
    return db_pain_event

@router.get("/", response_model=List[PainEventInDB])
async def list_pain_events(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all pain events for the authenticated user.
    
    Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    """
    result = await db.execute(
        select(PainEvent)
        .where(PainEvent.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(PainEvent.timestamp.desc())
    )
    return result.scalars().all()

@router.get("/{pain_event_id}", response_model=PainEventInDB)
async def get_pain_event(
    pain_event_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific pain event by ID for the authenticated user.
    
    Parameters:
    - pain_event_id: ID of the pain event to retrieve
    """
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
    
    return pain_event

@router.patch("/{pain_event_id}", response_model=PainEventInDB)
async def update_pain_event(
    pain_event_id: int,
    pain_event_update: PainEventUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific pain event for the authenticated user.
    
    Parameters:
    - pain_event_id: ID of the pain event to update
    - severity: Updated pain scale (0-10)
    - location: Updated body location of pain
    - symptoms: Updated list of symptoms
    - triggers: Updated list of triggers
    - notes: Updated additional notes
    """
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
    
    # Update pain event fields
    update_data = pain_event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pain_event, field, value)
    
    await db.commit()
    await db.refresh(pain_event)
    return pain_event

@router.delete("/{pain_event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pain_event(
    pain_event_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific pain event for the authenticated user.
    
    Parameters:
    - pain_event_id: ID of the pain event to delete
    """
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
    
    await db.delete(pain_event)
    await db.commit()
