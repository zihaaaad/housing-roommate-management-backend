from typing import List
from fastapi import APIRouter, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import MessageOnlyResponse
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["Internal Messaging"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StandardApiResponse[MessageResponse])
def send_message(
    payload: MessageCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    msg_service = MessageService(db)
    message = msg_service.send_direct_message(current_user, payload)

    response_data = MessageResponse.model_validate(message)
    response_data.sender = UserSummaryResponse.model_validate(current_user)
    return StandardApiResponse(
        message="Message sent successfully.",
        data=response_data
    )


@router.get("/conversation/{other_user_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[MessageResponse]])
def get_conversation_history(
    other_user_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    msg_service = MessageService(db)
    messages = msg_service.get_conversation_thread(current_user.id, other_user_id)

    response_list = []
    for m in messages:
        resp = MessageResponse.model_validate(m)
        if m.sender:
            resp.sender = UserSummaryResponse.model_validate(m.sender)
        if m.receiver:
            resp.receiver = UserSummaryResponse.model_validate(m.receiver)
        response_list.append(resp)

    return StandardApiResponse(
        message="Conversation thread retrieved.",
        data=response_list
    )


@router.delete("/{message_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_message(
    message_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    msg_service = MessageService(db)
    msg_service.delete_message(message_id, current_user)
    return StandardApiResponse(
        message="Message deleted successfully.",
        data=MessageOnlyResponse(message=f"Message with ID {message_id} has been deleted.")
    )

