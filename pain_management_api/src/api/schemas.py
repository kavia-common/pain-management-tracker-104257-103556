from datetime import datetime
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, EmailStr, Field

# Base User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Base Pain Event Schemas
class PainEventBase(BaseModel):
    severity: float = Field(..., ge=0, le=10)
    location: str
    symptoms: List[str] = []
    triggers: List[str] = []
    notes: Optional[str] = None

class PainEventCreate(PainEventBase):
    pass

class PainEventUpdate(PainEventBase):
    pass

class PainEventInDB(PainEventBase):
    id: int
    user_id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Base Provider Schemas
class ProviderBase(BaseModel):
    email: EmailStr
    full_name: str
    specialty: Optional[str] = None
    organization: Optional[str] = None

class ProviderCreate(ProviderBase):
    password: str = Field(..., min_length=8)

class ProviderUpdate(ProviderBase):
    password: Optional[str] = Field(None, min_length=8)

class ProviderInDB(ProviderBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Provider Access Schemas
class ProviderAccessBase(BaseModel):
    provider_id: int
    access_granted: bool = False

class ProviderAccessCreate(ProviderAccessBase):
    pass

class ProviderAccessUpdate(ProviderAccessBase):
    pass

class ProviderAccessInDB(ProviderAccessBase):
    id: int
    user_id: int
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# FHIR Export Schemas
class FHIRExportBase(BaseModel):
    pain_event_id: int
    fhir_resource_type: str
    fhir_data: Dict[str, Union[str, int, float, bool, Dict, List]]

class FHIRExportCreate(FHIRExportBase):
    pass

class FHIRExportInDB(FHIRExportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
