from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import RoommateRequestStatus
from app.schemas.profile import UserProfileResponse


class RoommateCompatibilityScore(BaseModel):
    overall_score: float
    budget_score: float
    location_score: float
    cleanliness_score: float
    sleep_schedule_score: float
    habits_score: float
    party_score: float


class RoommateMatchResponse(BaseModel):
    user: UserSummaryResponse
    profile: UserProfileResponse
    compatibility: RoommateCompatibilityScore


class RoommateRequestCreate(BaseModel):
    recipient_id: int
    property_id: Optional[int] = None
    message: str = Field(min_length=5, max_length=1000)


class RoommateRequestStatusUpdate(BaseModel):
    status: RoommateRequestStatus
    response_message: Optional[str] = Field(default=None, max_length=1000)


class RoommateRequestResponse(BaseModel):
    id: int
    requester_id: int
    recipient_id: int
    property_id: Optional[int] = None
    status: str
    message: str
    response_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requester: Optional[UserSummaryResponse] = None
    recipient: Optional[UserSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
