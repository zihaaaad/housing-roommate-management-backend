from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.auth import UserSummaryResponse


class MessageCreate(BaseModel):
    receiver_id: int
    property_id: Optional[int] = None
    content: str = Field(min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    property_id: Optional[int] = None
    content: str
    is_read: bool
    created_at: datetime
    sender: Optional[UserSummaryResponse] = None
    receiver: Optional[UserSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
