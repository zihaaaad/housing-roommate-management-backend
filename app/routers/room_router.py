from typing import List
from fastapi import APIRouter, Depends, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession, require_roles
from app.schemas.common import MessageOnlyResponse, UserRole
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.services.room_service import RoomService

router = APIRouter(tags=["Rooms"])


@router.post(
    "/properties/{property_id}/rooms",
    status_code=status.HTTP_201_CREATED,
    response_model=StandardApiResponse[RoomResponse]
)
def add_room_to_property(
    property_id: int,
    payload: RoomCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    room_service = RoomService(db)
    room = room_service.create_room(property_id, current_user, payload)
    return StandardApiResponse(
        message="Room added to property listing.",
        data=RoomResponse.model_validate(room)
    )


@router.get(
    "/properties/{property_id}/rooms",
    status_code=status.HTTP_200_OK,
    response_model=StandardApiResponse[List[RoomResponse]]
)
def get_property_rooms(property_id: int, db: DatabaseSession):
    room_service = RoomService(db)
    rooms = room_service.get_rooms_by_property_id(property_id)
    return StandardApiResponse(
        message="Rooms retrieved successfully.",
        data=[RoomResponse.model_validate(r) for r in rooms]
    )


@router.get(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardApiResponse[RoomResponse]
)
def get_room_details(room_id: int, db: DatabaseSession):
    room_service = RoomService(db)
    room = room_service.get_room_by_id(room_id)
    return StandardApiResponse(
        message="Room details retrieved.",
        data=RoomResponse.model_validate(room)
    )


@router.put(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardApiResponse[RoomResponse]
)
def update_room(
    room_id: int,
    payload: RoomUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    room_service = RoomService(db)
    updated_room = room_service.update_room(room_id, current_user, payload)
    return StandardApiResponse(
        message="Room updated successfully.",
        data=RoomResponse.model_validate(updated_room)
    )


@router.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=StandardApiResponse[MessageOnlyResponse]
)
def delete_room(
    room_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    room_service = RoomService(db)
    room_service.delete_room(room_id, current_user)
    return StandardApiResponse(
        message="Room removed successfully.",
        data=MessageOnlyResponse(message=f"Room with ID {room_id} has been deleted.")
    )
