from typing import List, Optional
from fastapi import APIRouter, Query, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import MessageOnlyResponse
from app.schemas.roommate import (
    RoommateMatchResponse,
    RoommateRequestCreate,
    RoommateRequestResponse,
    RoommateRequestStatusUpdate,
)
from app.services.roommate_matching_service import RoommateMatchingService

router = APIRouter(prefix="/roommates", tags=["Roommate Matching & Requests"])


@router.get("/matches", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[RoommateMatchResponse]])
def get_roommate_recommendations(
    current_user: CurrentUser,
    db: DatabaseSession,
    city: Optional[str] = Query(default=None),
    min_score: float = Query(default=0.0, ge=0.0, le=100.0),
    limit: int = Query(default=20, ge=1, le=100)
):
    matching_service = RoommateMatchingService(db)
    matches = matching_service.find_compatible_roommates(
        current_user=current_user,
        target_city=city,
        minimum_score=min_score,
        limit=limit
    )
    return StandardApiResponse(
        message="Roommate recommendations generated.",
        data=matches
    )


@router.post("/requests", status_code=status.HTTP_201_CREATED, response_model=StandardApiResponse[RoommateRequestResponse])
def send_request(
    payload: RoommateRequestCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    matching_service = RoommateMatchingService(db)
    request_record = matching_service.send_roommate_request(current_user, payload)
    return StandardApiResponse(
        message="Roommate request sent successfully.",
        data=RoommateRequestResponse.model_validate(request_record)
    )


@router.put("/requests/{request_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[RoommateRequestResponse])
def respond_to_request(
    request_id: int,
    payload: RoommateRequestStatusUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    matching_service = RoommateMatchingService(db)
    updated_request = matching_service.update_request_status(request_id, current_user, payload)

    response_data = RoommateRequestResponse.model_validate(updated_request)
    if updated_request.requester:
        response_data.requester = UserSummaryResponse.model_validate(updated_request.requester)
    if updated_request.recipient:
        response_data.recipient = UserSummaryResponse.model_validate(updated_request.recipient)

    return StandardApiResponse(
        message="Roommate request updated.",
        data=response_data
    )


@router.get("/requests/received", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[RoommateRequestResponse]])
def get_received_requests(current_user: CurrentUser, db: DatabaseSession):
    matching_service = RoommateMatchingService(db)
    requests = matching_service.get_user_roommate_requests(current_user.id, folder_type="received")

    result_list = []
    for r in requests:
        resp = RoommateRequestResponse.model_validate(r)
        if r.requester:
            resp.requester = UserSummaryResponse.model_validate(r.requester)
        if r.recipient:
            resp.recipient = UserSummaryResponse.model_validate(r.recipient)
        result_list.append(resp)

    return StandardApiResponse(
        message="Received roommate requests retrieved.",
        data=result_list
    )


@router.get("/requests/sent", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[RoommateRequestResponse]])
def get_sent_requests(current_user: CurrentUser, db: DatabaseSession):
    matching_service = RoommateMatchingService(db)
    requests = matching_service.get_user_roommate_requests(current_user.id, folder_type="sent")

    result_list = []
    for r in requests:
        resp = RoommateRequestResponse.model_validate(r)
        if r.requester:
            resp.requester = UserSummaryResponse.model_validate(r.requester)
        if r.recipient:
            resp.recipient = UserSummaryResponse.model_validate(r.recipient)
        result_list.append(resp)

    return StandardApiResponse(
        message="Sent roommate requests retrieved.",
        data=result_list
    )


@router.delete("/requests/{request_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_request(
    request_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    matching_service = RoommateMatchingService(db)
    matching_service.delete_roommate_request(request_id, current_user)
    return StandardApiResponse(
        message="Roommate request deleted successfully.",
        data=MessageOnlyResponse(message=f"Roommate request with ID {request_id} has been deleted.")
    )
