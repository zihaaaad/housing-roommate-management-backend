from typing import List
from fastapi import APIRouter, Depends, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession, require_roles
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import MessageOnlyResponse, UserRole
from app.schemas.property import PropertyResponse
from app.schemas.room import RoomResponse
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Rental Applications"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StandardApiResponse[ApplicationResponse])
def apply_for_rental(
    payload: ApplicationCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    app_service = ApplicationService(db)
    application = app_service.submit_application(current_user.id, payload)
    return StandardApiResponse(
        message="Rental application submitted successfully.",
        data=ApplicationResponse.model_validate(application)
    )


@router.get("/my-applications", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[ApplicationResponse]])
def get_my_rental_applications(current_user: CurrentUser, db: DatabaseSession):
    app_service = ApplicationService(db)
    applications = app_service.get_user_applications(current_user.id)

    response_list = []
    for item in applications:
        resp = ApplicationResponse.model_validate(item)
        if item.property:
            resp.property = PropertyResponse.model_validate(item.property)
        if item.room:
            resp.room = RoomResponse.model_validate(item.room)
        response_list.append(resp)

    return StandardApiResponse(
        message="Your submitted applications retrieved.",
        data=response_list
    )


@router.get("/landlord-applications", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[ApplicationResponse]])
def get_landlord_rental_applications(
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.LANDLORD.value, UserRole.ADMIN.value))
):
    app_service = ApplicationService(db)
    applications = app_service.get_landlord_applications(current_user.id)

    response_list = []
    for item in applications:
        resp = ApplicationResponse.model_validate(item)
        if item.property:
            resp.property = PropertyResponse.model_validate(item.property)
        if item.room:
            resp.room = RoomResponse.model_validate(item.room)
        if item.applicant:
            resp.applicant = UserSummaryResponse.model_validate(item.applicant)
        response_list.append(resp)

    return StandardApiResponse(
        message="Applications for your properties retrieved.",
        data=response_list
    )


@router.get("/{application_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[ApplicationResponse])
def get_application_by_id(application_id: int, current_user: CurrentUser, db: DatabaseSession):
    app_service = ApplicationService(db)
    application = app_service.get_application_by_id(application_id, current_user)

    response_data = ApplicationResponse.model_validate(application)
    if application.property:
        response_data.property = PropertyResponse.model_validate(application.property)
    if application.room:
        response_data.room = RoomResponse.model_validate(application.room)
    if application.applicant:
        response_data.applicant = UserSummaryResponse.model_validate(application.applicant)

    return StandardApiResponse(
        message="Application details retrieved.",
        data=response_data
    )


@router.patch("/{application_id}/status", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[ApplicationResponse])
def change_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    app_service = ApplicationService(db)
    updated_application = app_service.update_application_status(application_id, current_user, payload)

    response_data = ApplicationResponse.model_validate(updated_application)
    if updated_application.property:
        response_data.property = PropertyResponse.model_validate(updated_application.property)
    if updated_application.room:
        response_data.room = RoomResponse.model_validate(updated_application.room)
    if updated_application.applicant:
        response_data.applicant = UserSummaryResponse.model_validate(updated_application.applicant)

    return StandardApiResponse(
        message="Application status updated successfully.",
        data=response_data
    )


@router.delete("/{application_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_rental_application(
    application_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    app_service = ApplicationService(db)
    app_service.delete_application(application_id, current_user)
    return StandardApiResponse(
        message="Rental application deleted successfully.",
        data=MessageOnlyResponse(message=f"Application with ID {application_id} has been deleted.")
    )

