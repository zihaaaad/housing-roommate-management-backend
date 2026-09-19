from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.core.response import PaginatedApiResponse, PaginationMetadata, StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession, require_roles
from app.models.user import User
from app.schemas.auth import UserBasicUpdate, UserRoleUpdate, UserSummaryResponse
from app.schemas.common import MessageOnlyResponse, UserRole
from app.schemas.profile import UserProfileResponse, UserProfileUpdate, UserWithProfileResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User & Profiles"])


@router.get("/profile", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserProfileResponse])
def get_my_profile(current_user: CurrentUser, db: DatabaseSession):
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)
    return StandardApiResponse(
        message="Profile details retrieved.",
        data=UserProfileResponse.model_validate(profile)
    )


@router.put("/profile", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserProfileResponse])
def update_my_profile(payload: UserProfileUpdate, current_user: CurrentUser, db: DatabaseSession):
    user_service = UserService(db)
    updated_profile = user_service.update_user_profile(current_user.id, payload)
    return StandardApiResponse(
        message="Profile preferences updated successfully.",
        data=UserProfileResponse.model_validate(updated_profile)
    )


@router.get("/me/full", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserWithProfileResponse])
def get_my_complete_account(current_user: CurrentUser, db: DatabaseSession):
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)
    response_data = UserWithProfileResponse.model_validate(current_user)
    response_data.profile = UserProfileResponse.model_validate(profile)
    return StandardApiResponse(
        message="Full account information retrieved.",
        data=response_data
    )


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserWithProfileResponse])
def get_user_by_id(user_id: int, db: DatabaseSession):
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    profile = user_service.get_user_profile(user_id)
    response_data = UserWithProfileResponse.model_validate(user)
    response_data.profile = UserProfileResponse.model_validate(profile)
    return StandardApiResponse(
        message="User profile retrieved.",
        data=response_data
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedApiResponse[UserSummaryResponse])
def list_users(
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN.value)),
    search: Optional[str] = Query(default=None),
    role: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    user_service = UserService(db)
    users, total_items = user_service.list_users(search=search, role=role, page=page, limit=limit)
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    return PaginatedApiResponse(
        message="Users list retrieved successfully.",
        data=[UserSummaryResponse.model_validate(u) for u in users],
        pagination=PaginationMetadata(
            page=page,
            limit=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next_page=page < total_pages,
            has_prev_page=page > 1
        )
    )


@router.patch("/{user_id}/status", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserSummaryResponse])
def change_user_active_status(
    user_id: int,
    is_active: bool,
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN.value))
):
    user_service = UserService(db)
    user = user_service.toggle_user_active_status(user_id, is_active)
    return StandardApiResponse(
        message=f"User status updated to {'active' if is_active else 'inactive'}.",
        data=UserSummaryResponse.model_validate(user)
    )


@router.put("/me/basic", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserSummaryResponse])
def update_my_basic_details(payload: UserBasicUpdate, current_user: CurrentUser, db: DatabaseSession):
    user_service = UserService(db)
    updated_user = user_service.update_user_basic_details(
        user_id=current_user.id,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        avatar_url=payload.avatar_url
    )
    return StandardApiResponse(
        message="Account details updated successfully.",
        data=UserSummaryResponse.model_validate(updated_user)
    )


@router.patch("/{user_id}/role", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[UserSummaryResponse])
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN.value))
):
    user_service = UserService(db)
    user = user_service.update_user_role(user_id, payload.role.value)
    return StandardApiResponse(
        message=f"User role updated to {payload.role.value}.",
        data=UserSummaryResponse.model_validate(user)
    )


@router.delete("/me", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_own_account(current_user: CurrentUser, db: DatabaseSession):
    user_service = UserService(db)
    user_service.delete_user(current_user.id, current_user)
    return StandardApiResponse(
        message="Account deleted successfully.",
        data=MessageOnlyResponse(message="Your account has been deleted.")
    )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_user_by_admin(
    user_id: int,
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN.value))
):
    user_service = UserService(db)
    user_service.delete_user(user_id, current_user)
    return StandardApiResponse(
        message="User deleted successfully.",
        data=MessageOnlyResponse(message=f"User with ID {user_id} has been deleted.")
    )

