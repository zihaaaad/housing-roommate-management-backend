from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    ResourceNotFoundException,
)
from app.models.inquiry import PropertyInquiry
from app.models.notification import Notification
from app.models.property import Property
from app.models.user import User
from app.schemas.common import NotificationType
from app.schemas.inquiry import InquiryCreate, InquiryStatusUpdate


class InquiryService:
    def __init__(self, db: Session):
        self.db = db

    def schedule_viewing(self, applicant_id: int, payload: InquiryCreate) -> PropertyInquiry:
        property_record = self.db.query(Property).filter(Property.id == payload.property_id).first()
        if not property_record:
            raise ResourceNotFoundException("Property", payload.property_id)

        if property_record.landlord_id == applicant_id:
            raise BadRequestException("You cannot schedule a viewing for your own property.")

        viewing_date = payload.scheduled_viewing_date
        if viewing_date.tzinfo is None:
            viewing_date = viewing_date.replace(tzinfo=timezone.utc)
        if viewing_date < datetime.now(timezone.utc):
            raise BadRequestException("Scheduled viewing date must be in the future.")

        existing_active = self.db.query(PropertyInquiry).filter(
            PropertyInquiry.property_id == payload.property_id,
            PropertyInquiry.applicant_id == applicant_id,
            PropertyInquiry.status.in_(["PENDING", "CONFIRMED"])
        ).first()
        if existing_active:
            raise ConflictException("You already have an active viewing inquiry for this property.")

        inquiry = PropertyInquiry(
            property_id=payload.property_id,
            applicant_id=applicant_id,
            scheduled_viewing_date=payload.scheduled_viewing_date,
            notes=payload.notes,
            status="PENDING"
        )
        self.db.add(inquiry)
        self.db.flush()

        applicant = self.db.query(User).filter(User.id == applicant_id).first()
        applicant_name = applicant.full_name if applicant else "A tenant"
        notification = Notification(
            recipient_id=property_record.landlord_id,
            title="New Property Viewing Request",
            message=f"{applicant_name} requested a viewing for {property_record.title} on {payload.scheduled_viewing_date.strftime('%Y-%m-%d %H:%M')}.",
            notification_type=NotificationType.BOOKING_UPDATE.value,
            reference_id=str(inquiry.id)
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(inquiry)
        return inquiry

    def get_inquiry_by_id(self, inquiry_id: int, current_user: User) -> PropertyInquiry:
        inquiry = self.db.query(PropertyInquiry).options(
            joinedload(PropertyInquiry.property),
            joinedload(PropertyInquiry.applicant)
        ).filter(PropertyInquiry.id == inquiry_id).first()

        if not inquiry:
            raise ResourceNotFoundException("PropertyInquiry", inquiry_id)

        is_applicant = inquiry.applicant_id == current_user.id
        is_landlord = inquiry.property.landlord_id == current_user.id
        is_admin = current_user.role == "ADMIN"

        if not (is_applicant or is_landlord or is_admin):
            raise ForbiddenException("You are not authorized to view this inquiry.")

        return inquiry

    def update_inquiry_status(
        self,
        inquiry_id: int,
        current_user: User,
        payload: InquiryStatusUpdate
    ) -> PropertyInquiry:
        inquiry = self.get_inquiry_by_id(inquiry_id, current_user)
        is_landlord = inquiry.property.landlord_id == current_user.id
        is_applicant = inquiry.applicant_id == current_user.id
        is_admin = current_user.role == "ADMIN"

        if payload.status.value == "CANCELLED":
            if not (is_applicant or is_landlord or is_admin):
                raise ForbiddenException("Unauthorized to cancel this viewing inquiry.")
        else:
            if not (is_landlord or is_admin):
                raise ForbiddenException("Only the property owner can update viewing status.")

        inquiry.status = payload.status.value
        if payload.landlord_notes:
            inquiry.landlord_notes = payload.landlord_notes

        recipient_id = inquiry.property.landlord_id if (is_applicant and payload.status.value == "CANCELLED") else inquiry.applicant_id
        notification = Notification(
            recipient_id=recipient_id,
            title="Viewing Schedule Updated",
            message=f"Viewing schedule for {inquiry.property.title} was set to {payload.status.value}.",
            notification_type=NotificationType.BOOKING_UPDATE.value,
            reference_id=str(inquiry.id)
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(inquiry)
        return inquiry

    def get_user_inquiries(self, user_id: int) -> List[PropertyInquiry]:
        return self.db.query(PropertyInquiry).options(
            joinedload(PropertyInquiry.property),
            joinedload(PropertyInquiry.applicant)
        ).filter(PropertyInquiry.applicant_id == user_id).order_by(PropertyInquiry.created_at.desc()).all()

    def get_landlord_inquiries(self, landlord_id: int) -> List[PropertyInquiry]:
        return self.db.query(PropertyInquiry).join(Property).options(
            joinedload(PropertyInquiry.property),
            joinedload(PropertyInquiry.applicant)
        ).filter(Property.landlord_id == landlord_id).order_by(PropertyInquiry.created_at.desc()).all()

    def delete_inquiry(self, inquiry_id: int, current_user: User) -> None:
        inquiry = self.get_inquiry_by_id(inquiry_id, current_user)
        self.db.delete(inquiry)
        self.db.commit()

