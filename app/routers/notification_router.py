from typing import List
from fastapi import APIRouter, Query, status
from app.core.response import StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import MessageOnlyResponse
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[NotificationResponse]])
def get_my_notifications(
    current_user: CurrentUser,
    db: DatabaseSession,
    unread_only: bool = Query(default=False)
):
    notif_service = NotificationService(db)
    notifications = notif_service.get_user_notifications(current_user.id, unread_only=unread_only)
    return StandardApiResponse(
        message="Notifications retrieved.",
        data=[NotificationResponse.model_validate(n) for n in notifications]
    )


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[NotificationResponse])
def mark_single_notification_read(
    notification_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    notif_service = NotificationService(db)
    notification = notif_service.mark_notification_as_read(notification_id, current_user.id)
    return StandardApiResponse(
        message="Notification marked as read.",
        data=NotificationResponse.model_validate(notification)
    )


@router.post("/mark-all-read", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def mark_all_as_read(current_user: CurrentUser, db: DatabaseSession):
    notif_service = NotificationService(db)
    updated_count = notif_service.mark_all_notifications_as_read(current_user.id)
    return StandardApiResponse(
        message="All notifications marked as read.",
        data=MessageOnlyResponse(message=f"{updated_count} notifications marked as read.")
    )


@router.get("/unread-count", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[dict])
def get_unread_notification_count(current_user: CurrentUser, db: DatabaseSession):
    notif_service = NotificationService(db)
    count = notif_service.get_unread_count(current_user.id)
    return StandardApiResponse(
        message="Unread count calculated.",
        data={"unread_count": count}
    )


@router.delete("/clear-read", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def clear_read_notifications(current_user: CurrentUser, db: DatabaseSession):
    notif_service = NotificationService(db)
    deleted_count = notif_service.clear_read_notifications(current_user.id)
    return StandardApiResponse(
        message="Read notifications cleared.",
        data=MessageOnlyResponse(message=f"{deleted_count} read notifications cleared.")
    )


@router.delete("/{notification_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_single_notification(
    notification_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    notif_service = NotificationService(db)
    notif_service.delete_notification(notification_id, current_user.id)
    return StandardApiResponse(
        message="Notification deleted successfully.",
        data=MessageOnlyResponse(message=f"Notification with ID {notification_id} has been deleted.")
    )

