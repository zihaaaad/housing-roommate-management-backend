from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import BadRequestException, ForbiddenException, ResourceNotFoundException
from app.models.message import DirectMessage
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import NotificationType
from app.schemas.message import MessageCreate


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def send_direct_message(self, sender: User, payload: MessageCreate) -> DirectMessage:
        if sender.id == payload.receiver_id:
            raise BadRequestException("You cannot send a message to yourself.")

        cleaned_content = payload.content.strip()
        if not cleaned_content:
            raise BadRequestException("Message content cannot be empty.")

        receiver = self.db.query(User).filter(User.id == payload.receiver_id).first()
        if not receiver:
            raise ResourceNotFoundException("User", payload.receiver_id)

        message = DirectMessage(
            sender_id=sender.id,
            receiver_id=payload.receiver_id,
            property_id=payload.property_id,
            content=cleaned_content,
            is_read=False
        )
        self.db.add(message)
        self.db.flush()

        notification = Notification(
            recipient_id=payload.receiver_id,
            title="New Message Received",
            message=f"{sender.full_name}: {payload.content[:50]}...",
            notification_type=NotificationType.SYSTEM_ALERT.value,
            reference_id=str(message.id)
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_conversation_thread(self, current_user_id: int, other_user_id: int) -> List[DirectMessage]:
        messages = self.db.query(DirectMessage).options(
            joinedload(DirectMessage.sender),
            joinedload(DirectMessage.receiver)
        ).filter(
            or_(
                (DirectMessage.sender_id == current_user_id) & (DirectMessage.receiver_id == other_user_id),
                (DirectMessage.sender_id == other_user_id) & (DirectMessage.receiver_id == current_user_id)
            )
        ).order_by(DirectMessage.created_at.asc()).all()

        unread_ids = [m.id for m in messages if m.receiver_id == current_user_id and not m.is_read]
        if unread_ids:
            self.db.query(DirectMessage).filter(DirectMessage.id.in_(unread_ids)).update({"is_read": True}, synchronize_session=False)
            self.db.commit()

        return messages

    def delete_message(self, message_id: int, current_user: User) -> None:
        message = self.db.query(DirectMessage).filter(DirectMessage.id == message_id).first()
        if not message:
            raise ResourceNotFoundException("DirectMessage", message_id)
        if message.sender_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("Only the sender or an admin can delete this message.")
        self.db.delete(message)
        self.db.commit()

    def get_user_conversations(self, current_user_id: int) -> List[dict]:
        messages = self.db.query(DirectMessage).options(
            joinedload(DirectMessage.sender),
            joinedload(DirectMessage.receiver)
        ).filter(
            or_(
                DirectMessage.sender_id == current_user_id,
                DirectMessage.receiver_id == current_user_id
            )
        ).order_by(DirectMessage.created_at.desc()).all()

        conversations_map = {}
        for m in messages:
            partner = m.receiver if m.sender_id == current_user_id else m.sender
            if not partner:
                continue
            partner_id = partner.id
            if partner_id not in conversations_map:
                conversations_map[partner_id] = {
                    "id": partner.id,
                    "full_name": partner.full_name,
                    "username": partner.username,
                    "email": partner.email,
                    "role": partner.role,
                    "avatar_url": partner.avatar_url,
                    "last_message": m.content,
                    "lastMessage": m.content,
                    "last_message_at": m.created_at,
                    "unread_count": 0,
                    "partner": partner
                }
            if m.receiver_id == current_user_id and not m.is_read:
                conversations_map[partner_id]["unread_count"] += 1

        return list(conversations_map.values())

