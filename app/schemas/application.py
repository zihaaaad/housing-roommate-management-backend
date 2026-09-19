from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import ApplicationStatus
from app.schemas.property import PropertyResponse
from app.schemas.room import RoomResponse


class ApplicationCreate(BaseModel):
    property_id: int
    room_id: Optional[int] = None
    proposed_move_in_date: datetime
    lease_duration_months: int = Field(default=12, ge=1)
    monthly_income: float = Field(gt=0)
    credit_score: Optional[int] = Field(default=None, ge=300, le=850)
    employment_status: str = Field(min_length=2, max_length=100)
    emergency_contact_name: str = Field(min_length=2, max_length=150)
    emergency_contact_phone: str = Field(min_length=5, max_length=50)


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    landlord_decision_notes: Optional[str] = Field(default=None, max_length=1000)


class ApplicationResponse(BaseModel):
    id: int
    property_id: int
    room_id: Optional[int] = None
    applicant_id: int
    proposed_move_in_date: datetime
    lease_duration_months: int
    monthly_income: float
    credit_score: Optional[int] = None
    employment_status: str
    emergency_contact_name: str
    emergency_contact_phone: str
    status: str
    landlord_decision_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    property: Optional[PropertyResponse] = None
    room: Optional[RoomResponse] = None
    applicant: Optional[UserSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
