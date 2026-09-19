from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException
from app.models.notification import Notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.recipient_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).all()

    def mark_notification_as_read(self, notification_id: int, user_id: int) -> Notification:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == user_id
        ).first()
        if not notification:
            raise ResourceNotFoundException("Notification", notification_id)

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_notifications_as_read(self, user_id: int) -> int:
        updated_count = self.db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return updated_count

    def get_unread_count(self, user_id: int) -> int:
        return self.db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).count()

    def delete_notification(self, notification_id: int, user_id: int) -> None:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == user_id
        ).first()
        if not notification:
            raise ResourceNotFoundException("Notification", notification_id)
        self.db.delete(notification)
        self.db.commit()

    def clear_read_notifications(self, user_id: int) -> int:
        deleted_count = self.db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == True
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count

