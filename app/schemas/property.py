from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import FurnishedStatus, PropertyStatus, PropertyType
from app.schemas.room import RoomResponse


class PropertyCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    property_type: PropertyType = PropertyType.APARTMENT
    address: str = Field(min_length=3, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=30)
    country: str = Field(default="Bangladesh", max_length=100)
    total_bedrooms: int = Field(default=1, ge=0)
    total_bathrooms: int = Field(default=1, ge=0)
    square_feet: Optional[int] = Field(default=None, gt=0)
    furnished_status: FurnishedStatus = FurnishedStatus.UNFURNISHED
    is_pet_friendly: bool = False
    is_smoking_allowed: bool = False
    parking_available: bool = False
    amenities: str = Field(default="")
    base_monthly_rent: float = Field(gt=0)
    security_deposit: float = Field(default=0.0, ge=0)
    utilities_included: bool = False
    available_from: Optional[datetime] = None
    lease_duration_months: int = Field(default=12, ge=1)
    image_urls: str = Field(default="")


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10)
    property_type: Optional[PropertyType] = None
    address: Optional[str] = Field(default=None, min_length=3, max_length=255)
    city: Optional[str] = Field(default=None, min_length=2, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=30)
    country: Optional[str] = Field(default=None, max_length=100)
    total_bedrooms: Optional[int] = Field(default=None, ge=0)
    total_bathrooms: Optional[int] = Field(default=None, ge=0)
    square_feet: Optional[int] = Field(default=None, gt=0)
    furnished_status: Optional[FurnishedStatus] = None
    is_pet_friendly: Optional[bool] = None
    is_smoking_allowed: Optional[bool] = None
    parking_available: Optional[bool] = None
    amenities: Optional[str] = None
    base_monthly_rent: Optional[float] = Field(default=None, gt=0)
    security_deposit: Optional[float] = Field(default=None, ge=0)
    utilities_included: Optional[bool] = None
    available_from: Optional[datetime] = None
    lease_duration_months: Optional[int] = Field(default=None, ge=1)
    status: Optional[PropertyStatus] = None
    image_urls: Optional[str] = None


class PropertyFilterParams(BaseModel):
    search: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    city: Optional[str] = None
    min_rent: Optional[float] = Field(default=None, ge=0)
    max_rent: Optional[float] = Field(default=None, ge=0)
    min_bedrooms: Optional[int] = Field(default=None, ge=0)
    min_bathrooms: Optional[int] = Field(default=None, ge=0)
    is_pet_friendly: Optional[bool] = None
    furnished_status: Optional[FurnishedStatus] = None
    available_from_start: Optional[datetime] = None
    available_from_end: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class PropertyResponse(BaseModel):
    id: int
    landlord_id: int
    title: str
    description: str
    property_type: str
    address: str
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    total_bedrooms: int
    total_bathrooms: int
    square_feet: Optional[int] = None
    furnished_status: str
    is_pet_friendly: bool
    is_smoking_allowed: bool
    parking_available: bool
    amenities: str
    base_monthly_rent: float
    security_deposit: float
    utilities_included: bool
    available_from: datetime
    lease_duration_months: int
    status: str
    image_urls: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PropertyDetailResponse(PropertyResponse):
    landlord: Optional[UserSummaryResponse] = None
    rooms: List[RoomResponse] = []

    model_config = ConfigDict(from_attributes=True)
