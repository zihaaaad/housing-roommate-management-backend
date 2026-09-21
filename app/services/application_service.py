from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session, joinedload
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    ResourceNotFoundException,
)
from app.models.application import RentalApplication
from app.models.notification import Notification
from app.models.property import Property
from app.models.room import Room
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate
from app.schemas.common import NotificationType


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def submit_application(self, applicant_id: int, payload: ApplicationCreate) -> RentalApplication:
        property_record = self.db.query(Property).filter(Property.id == payload.property_id).first()
        if not property_record:
            raise ResourceNotFoundException("Property", payload.property_id)

        if property_record.landlord_id == applicant_id:
            raise BadRequestException("You cannot apply to lease your own property.")

        move_in_date = payload.proposed_move_in_date
        if move_in_date.tzinfo is None:
            move_in_date = move_in_date.replace(tzinfo=timezone.utc)
        if move_in_date < datetime.now(timezone.utc):
            raise BadRequestException("Proposed move-in date must be in the future.")

        if payload.room_id:
            room = self.db.query(Room).filter(
                Room.id == payload.room_id,
                Room.property_id == payload.property_id
            ).first()
            if not room:
                raise ResourceNotFoundException("Room", payload.room_id)
            if not room.is_available:
                raise ConflictException("The selected room is currently unavailable.")

        existing_active_application = self.db.query(RentalApplication).filter(
            RentalApplication.property_id == payload.property_id,
            RentalApplication.applicant_id == applicant_id,
            RentalApplication.status.in_(["PENDING", "UNDER_REVIEW"])
        ).first()

        if existing_active_application:
            raise ConflictException("You already have an active application submitted for this property.")

        application = RentalApplication(
            property_id=payload.property_id,
            room_id=payload.room_id,
            applicant_id=applicant_id,
            proposed_move_in_date=payload.proposed_move_in_date,
            lease_duration_months=payload.lease_duration_months,
            monthly_income=payload.monthly_income,
            credit_score=payload.credit_score,
            employment_status=payload.employment_status,
            emergency_contact_name=payload.emergency_contact_name,
            emergency_contact_phone=payload.emergency_contact_phone,
            status="PENDING"
        )
        self.db.add(application)
        self.db.flush()

        applicant = self.db.query(User).filter(User.id == applicant_id).first()
        applicant_name = applicant.full_name if applicant else "An applicant"
        notification = Notification(
            recipient_id=property_record.landlord_id,
            title="New Rental Application Received",
            message=f"{applicant_name} submitted a rental application for {property_record.title}.",
            notification_type=NotificationType.APPLICATION_UPDATE.value,
            reference_id=str(application.id)
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application_by_id(self, application_id: int, current_user: User) -> RentalApplication:
        application = self.db.query(RentalApplication).options(
            joinedload(RentalApplication.property),
            joinedload(RentalApplication.room),
            joinedload(RentalApplication.applicant)
        ).filter(RentalApplication.id == application_id).first()

        if not application:
            raise ResourceNotFoundException("RentalApplication", application_id)

        is_applicant = application.applicant_id == current_user.id
        is_landlord = application.property.landlord_id == current_user.id
        is_admin = current_user.role == "ADMIN"

        if not (is_applicant or is_landlord or is_admin):
            raise ForbiddenException("Unauthorized to access this rental application.")

        return application

    def update_application_status(
        self,
        application_id: int,
        current_user: User,
        payload: ApplicationStatusUpdate
    ) -> RentalApplication:
        application = self.get_application_by_id(application_id, current_user)
        is_landlord = application.property.landlord_id == current_user.id
        is_applicant = application.applicant_id == current_user.id
        is_admin = current_user.role == "ADMIN"

        target_status = payload.status.value

        if target_status == "WITHDRAWN":
            if not (is_applicant or is_admin):
                raise ForbiddenException("Only the applicant can withdraw this application.")
        else:
            if not (is_landlord or is_admin):
                raise ForbiddenException("Only the property owner or admin can review and update this application.")

        if target_status == "APPROVED":
            if application.room_id:
                room_query = self.db.query(Room).filter(Room.id == application.room_id)
                if self.db.bind and self.db.bind.dialect.name != "sqlite":
                    room_query = room_query.with_for_update()
                room = room_query.first()
                if not room or not room.is_available:
                    raise ConflictException("This room is no longer available for lease.")
                room.is_available = False
                competing_apps = self.db.query(RentalApplication).filter(
                    RentalApplication.room_id == room.id,
                    RentalApplication.id != application.id,
                    RentalApplication.status.in_(["PENDING", "UNDER_REVIEW"])
                ).all()
                for competing in competing_apps:
                    competing.status = "REJECTED"
                    competing.landlord_decision_notes = "Room was leased to another applicant."
                    competing.updated_at = datetime.now(timezone.utc)
            else:
                prop_query = self.db.query(Property).filter(Property.id == application.property_id)
                if self.db.bind and self.db.bind.dialect.name != "sqlite":
                    prop_query = prop_query.with_for_update()
                property_record = prop_query.first()
                if not property_record or property_record.status != "AVAILABLE":
                    raise ConflictException("This property is no longer available for lease.")
                property_record.status = "LEASED"
                competing_apps = self.db.query(RentalApplication).filter(
                    RentalApplication.property_id == property_record.id,
                    RentalApplication.id != application.id,
                    RentalApplication.status.in_(["PENDING", "UNDER_REVIEW"])
                ).all()
                for competing in competing_apps:
                    competing.status = "REJECTED"
                    competing.landlord_decision_notes = "Property was leased to another applicant."
                    competing.updated_at = datetime.now(timezone.utc)

        application.status = target_status
        if payload.landlord_decision_notes:
            application.landlord_decision_notes = payload.landlord_decision_notes
        application.updated_at = datetime.now(timezone.utc)

        recipient_id = application.property.landlord_id if (is_applicant and target_status == "WITHDRAWN") else application.applicant_id
        notification = Notification(
            recipient_id=recipient_id,
            title="Rental Application Status Updated",
            message=f"The application for {application.property.title} was set to {target_status}.",
            notification_type=NotificationType.APPLICATION_UPDATE.value,
            reference_id=str(application.id)
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_user_applications(self, user_id: int) -> List[RentalApplication]:
        return self.db.query(RentalApplication).options(
            joinedload(RentalApplication.property),
            joinedload(RentalApplication.room),
            joinedload(RentalApplication.applicant)
        ).filter(RentalApplication.applicant_id == user_id).order_by(RentalApplication.created_at.desc()).all()

    def get_landlord_applications(self, landlord_id: int) -> List[RentalApplication]:
        return self.db.query(RentalApplication).join(Property).options(
            joinedload(RentalApplication.property),
            joinedload(RentalApplication.room),
            joinedload(RentalApplication.applicant)
        ).filter(Property.landlord_id == landlord_id).order_by(RentalApplication.created_at.desc()).all()

    def delete_application(self, application_id: int, current_user: User) -> None:
        application = self.get_application_by_id(application_id, current_user)
        if application.applicant_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("Only the applicant or an admin can delete this application.")
        self.db.delete(application)
        self.db.commit()

