from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.common import UserRole


class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    full_name: str = Field(min_length=2, max_length=150)
    phone_number: Optional[str] = Field(default=None, max_length=50)
    role: UserRole = UserRole.ROOMMATE_SEEKER


class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str


class UserSummaryResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    phone_number: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserSummaryResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=6, max_length=100)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=100)


class UserBasicUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    phone_number: Optional[str] = Field(default=None, min_length=5, max_length=50)
    avatar_url: Optional[str] = Field(default=None, max_length=500)


class UserRoleUpdate(BaseModel):
    role: UserRole

