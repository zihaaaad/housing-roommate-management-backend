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


class ConversationSummaryResponse(BaseModel):
    id: int
    full_name: str
    username: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    last_message: str
    last_message_at: datetime
    lastMessage: Optional[str] = None
    unread_count: int = 0
    partner: Optional[UserSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
