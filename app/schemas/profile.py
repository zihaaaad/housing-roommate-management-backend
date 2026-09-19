from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import (
    CleanlinessLevel,
    DietaryPreference,
    PartyHabit,
    PetHabit,
    SleepSchedule,
    SmokingHabit,
    WorkStatus,
)


class UserProfileCreate(BaseModel):
    bio: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=18, le=120)
    gender: Optional[str] = None
    budget_min: float = Field(default=0.0, ge=0)
    budget_max: float = Field(default=0.0, ge=0)
    preferred_city: Optional[str] = None
    preferred_neighborhood: Optional[str] = None
    cleanliness_level: CleanlinessLevel = CleanlinessLevel.MODERATE
    sleep_schedule: SleepSchedule = SleepSchedule.FLEXIBLE
    smoking_habit: SmokingHabit = SmokingHabit.NON_SMOKER
    pet_habit: PetHabit = PetHabit.PET_FRIENDLY
    party_habit: PartyHabit = PartyHabit.OCCASIONALLY
    dietary_preference: DietaryPreference = DietaryPreference.ANY
    work_status: WorkStatus = WorkStatus.HYBRID
    move_in_date: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    bio: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=18, le=120)
    gender: Optional[str] = None
    budget_min: Optional[float] = Field(default=None, ge=0)
    budget_max: Optional[float] = Field(default=None, ge=0)
    preferred_city: Optional[str] = None
    preferred_neighborhood: Optional[str] = None
    cleanliness_level: Optional[CleanlinessLevel] = None
    sleep_schedule: Optional[SleepSchedule] = None
    smoking_habit: Optional[SmokingHabit] = None
    pet_habit: Optional[PetHabit] = None
    party_habit: Optional[PartyHabit] = None
    dietary_preference: Optional[DietaryPreference] = None
    work_status: Optional[WorkStatus] = None
    move_in_date: Optional[datetime] = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    bio: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    budget_min: float
    budget_max: float
    preferred_city: Optional[str] = None
    preferred_neighborhood: Optional[str] = None
    cleanliness_level: str
    sleep_schedule: str
    smoking_habit: str
    pet_habit: str
    party_habit: str
    dietary_preference: str
    work_status: str
    move_in_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithProfileResponse(UserSummaryResponse):
    profile: Optional[UserProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)
