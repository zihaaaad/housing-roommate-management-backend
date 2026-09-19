from fastapi import APIRouter, Depends, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.auth import (
    AuthTokenResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserSummaryResponse,
)
from app.schemas.common import MessageOnlyResponse
from app.services.auth_service import AuthenticationService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=StandardApiResponse[UserSummaryResponse])
def register(payload: UserRegisterRequest, db: DatabaseSession):
    auth_service = AuthenticationService(db)
    new_user = auth_service.register_user(payload)
    return StandardApiResponse(
        message="User account created successfully.",
        data=UserSummaryResponse.model_validate(new_user)
    )


@router.post("/login", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[AuthTokenResponse])
def login(payload: UserLoginRequest, db: DatabaseSession):
    auth_service = AuthenticationService(db)
    token_response = auth_service.authenticate_and_login(payload)
    return StandardApiResponse(
        message="Authentication successful.",
        data=token_response
    )


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[RefreshTokenResponse])
def refresh_token(payload: RefreshTokenRequest, db: DatabaseSession):
    auth_service = AuthenticationService(db)
    refreshed_token = auth_service.refresh_access_token(payload.refresh_token)
    return StandardApiResponse(
        message="Access token refreshed successfully.",
        data=refreshed_token
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[ForgotPasswordResponse])
def forgot_password(payload: ForgotPasswordRequest, db: DatabaseSession):
    auth_service = AuthenticationService(db)
    result = auth_service.initiate_password_reset(payload)
    return StandardApiResponse(
        message="Password reset request processed.",
        data=result
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def reset_password(payload: ResetPasswordRequest, db: DatabaseSession):
    auth_service = AuthenticationService(db)
    auth_service.complete_password_reset(payload)
    return StandardApiResponse(
        message="Password has been reset.",
        data=MessageOnlyResponse(message="Password reset complete. You can now log in.")
    )


@router.post("/change-password", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def change_password(payload: ChangePasswordRequest, current_user: CurrentUser, db: DatabaseSession):
    auth_service = AuthenticationService(db)
    auth_service.change_password(current_user.id, payload)
    return StandardApiResponse(
        message="Password changed successfully.",
        data=MessageOnlyResponse(message="Password updated successfully.")
    )


@router.get("/me", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserSummaryResponse])
def get_current_user_profile(current_user: CurrentUser):
    return StandardApiResponse(
        message="Current user profile retrieved.",
        data=UserSummaryResponse.model_validate(current_user)
    )
