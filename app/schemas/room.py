from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import RoomType


class RoomCreate(BaseModel):
    room_name: str = Field(min_length=1, max_length=100)
    room_type: RoomType = RoomType.SINGLE
    monthly_rent: float = Field(gt=0)
    security_deposit: float = Field(default=0.0, ge=0)
    is_available: bool = True
    private_bathroom: bool = False
    square_feet: Optional[int] = Field(default=None, gt=0)
    available_date: Optional[datetime] = None


class RoomUpdate(BaseModel):
    room_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    room_type: Optional[RoomType] = None
    monthly_rent: Optional[float] = Field(default=None, gt=0)
    security_deposit: Optional[float] = Field(default=None, ge=0)
    is_available: Optional[bool] = None
    private_bathroom: Optional[bool] = None
    square_feet: Optional[int] = Field(default=None, gt=0)
    available_date: Optional[datetime] = None


class RoomResponse(BaseModel):
    id: int
    property_id: int
    room_name: str
    room_type: str
    monthly_rent: float
    security_deposit: float
    is_available: bool
    private_bathroom: bool
    square_feet: Optional[int] = None
    available_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
