from typing import List
from fastapi import APIRouter, Depends, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession, require_roles
from app.models.user import User
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import MessageOnlyResponse, UserRole
from app.schemas.inquiry import InquiryCreate, InquiryResponse, InquiryStatusUpdate
from app.schemas.property import PropertyResponse
from app.services.inquiry_service import InquiryService

router = APIRouter(prefix="/inquiries", tags=["Viewings & Inquiries"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StandardApiResponse[InquiryResponse])
def schedule_property_viewing(
    payload: InquiryCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    inquiry_service = InquiryService(db)
    inquiry = inquiry_service.schedule_viewing(current_user.id, payload)
    return StandardApiResponse(
        message="Viewing scheduled successfully.",
        data=InquiryResponse.model_validate(inquiry)
    )


@router.get("/my-inquiries", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[InquiryResponse]])
def get_my_submitted_inquiries(current_user: CurrentUser, db: DatabaseSession):
    inquiry_service = InquiryService(db)
    inquiries = inquiry_service.get_user_inquiries(current_user.id)

    response_list = []
    for item in inquiries:
        resp = InquiryResponse.model_validate(item)
        if item.property:
            resp.property = PropertyResponse.model_validate(item.property)
        response_list.append(resp)

    return StandardApiResponse(
        message="Your viewing inquiries retrieved.",
        data=response_list
    )


@router.get("/landlord-inquiries", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[InquiryResponse]])
def get_landlord_received_inquiries(
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.LANDLORD.value, UserRole.ADMIN.value))
):
    inquiry_service = InquiryService(db)
    inquiries = inquiry_service.get_landlord_inquiries(current_user.id)

    response_list = []
    for item in inquiries:
        resp = InquiryResponse.model_validate(item)
        if item.property:
            resp.property = PropertyResponse.model_validate(item.property)
        if item.applicant:
            resp.applicant = UserSummaryResponse.model_validate(item.applicant)
        response_list.append(resp)

    return StandardApiResponse(
        message="Received viewing inquiries retrieved.",
        data=response_list
    )


@router.get("/{inquiry_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[InquiryResponse])
def get_inquiry_by_id(inquiry_id: int, current_user: CurrentUser, db: DatabaseSession):
    inquiry_service = InquiryService(db)
    inquiry = inquiry_service.get_inquiry_by_id(inquiry_id, current_user)

    response_data = InquiryResponse.model_validate(inquiry)
    if inquiry.property:
        response_data.property = PropertyResponse.model_validate(inquiry.property)
    if inquiry.applicant:
        response_data.applicant = UserSummaryResponse.model_validate(inquiry.applicant)

    return StandardApiResponse(
        message="Inquiry details retrieved.",
        data=response_data
    )


@router.patch("/{inquiry_id}/status", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[InquiryResponse])
def update_inquiry_status(
    inquiry_id: int,
    payload: InquiryStatusUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    inquiry_service = InquiryService(db)
    updated_inquiry = inquiry_service.update_inquiry_status(inquiry_id, current_user, payload)

    response_data = InquiryResponse.model_validate(updated_inquiry)
    if updated_inquiry.property:
        response_data.property = PropertyResponse.model_validate(updated_inquiry.property)
    if updated_inquiry.applicant:
        response_data.applicant = UserSummaryResponse.model_validate(updated_inquiry.applicant)

    return StandardApiResponse(
        message="Inquiry status updated.",
        data=response_data
    )


@router.delete("/{inquiry_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_inquiry(
    inquiry_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    inquiry_service = InquiryService(db)
    inquiry_service.delete_inquiry(inquiry_id, current_user)
    return StandardApiResponse(
        message="Viewing inquiry deleted successfully.",
        data=MessageOnlyResponse(message=f"Inquiry with ID {inquiry_id} has been deleted.")
    )

