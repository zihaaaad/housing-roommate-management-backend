from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"
    ROOMMATE_SEEKER = "ROOMMATE_SEEKER"


class PropertyType(str, Enum):
    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    STUDIO = "STUDIO"
    SHARED_FLAT = "SHARED_FLAT"
    SUBLET = "SUBLET"
    MESS = "MESS"


class FurnishedStatus(str, Enum):
    FURNISHED = "FURNISHED"
    SEMI_FURNISHED = "SEMI_FURNISHED"
    UNFURNISHED = "UNFURNISHED"


class PropertyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    LEASED = "LEASED"
    ARCHIVED = "ARCHIVED"


class RoomType(str, Enum):
    SINGLE = "SINGLE"
    MASTER_WITH_BATH = "MASTER_WITH_BATH"
    DOUBLE_SHARED = "DOUBLE_SHARED"
    SEAT_SHARED = "SEAT_SHARED"



class RoommateRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class InquiryStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class NotificationType(str, Enum):
    BOOKING_UPDATE = "BOOKING_UPDATE"
    APPLICATION_UPDATE = "APPLICATION_UPDATE"
    ROOMMATE_REQUEST = "ROOMMATE_REQUEST"
    SYSTEM_ALERT = "SYSTEM_ALERT"


class CleanlinessLevel(str, Enum):
    VERY_CLEAN = "VERY_CLEAN"
    MODERATE = "MODERATE"
    RELAXED = "RELAXED"


class SleepSchedule(str, Enum):
    EARLY_BIRD = "EARLY_BIRD"
    NIGHT_OWL = "NIGHT_OWL"
    FLEXIBLE = "FLEXIBLE"


class SmokingHabit(str, Enum):
    NON_SMOKER = "NON_SMOKER"
    OUTSIDE_ONLY = "OUTSIDE_ONLY"
    SMOKER = "SMOKER"


class PetHabit(str, Enum):
    NO_PETS = "NO_PETS"
    HAS_PETS = "HAS_PETS"
    PET_FRIENDLY = "PET_FRIENDLY"


class PartyHabit(str, Enum):
    RARELY = "RARELY"
    OCCASIONALLY = "OCCASIONALLY"
    FREQUENTLY = "FREQUENTLY"


class DietaryPreference(str, Enum):
    ANY = "ANY"
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    OMNIVORE = "OMNIVORE"


class WorkStatus(str, Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    IN_OFFICE = "IN_OFFICE"
    STUDENT = "STUDENT"


class PaginationQueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class MessageOnlyResponse(BaseModel):
    message: str
