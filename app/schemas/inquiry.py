from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import InquiryStatus
from app.schemas.property import PropertyResponse


class InquiryCreate(BaseModel):
    property_id: int
    scheduled_viewing_date: datetime
    notes: Optional[str] = Field(default=None, max_length=1000)


class InquiryStatusUpdate(BaseModel):
    status: InquiryStatus
    landlord_notes: Optional[str] = Field(default=None, max_length=1000)


class InquiryResponse(BaseModel):
    id: int
    property_id: int
    applicant_id: int
    scheduled_viewing_date: datetime
    status: str
    notes: Optional[str] = None
    landlord_notes: Optional[str] = None
    created_at: datetime
    property: Optional[PropertyResponse] = None
    applicant: Optional[UserSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
