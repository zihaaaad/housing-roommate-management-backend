from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(50), nullable=True)
    role = Column(String(50), default="ROOMMATE_SEEKER", index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    hashed_refresh_token = Column(String(255), nullable=True)
    password_reset_token_hash = Column(String(255), nullable=True)
    password_reset_token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="landlord", cascade="all, delete-orphan")
    sent_roommate_requests = relationship(
        "RoommateRequest",
        foreign_keys="[RoommateRequest.requester_id]",
        back_populates="requester",
        cascade="all, delete-orphan"
    )
    received_roommate_requests = relationship(
        "RoommateRequest",
        foreign_keys="[RoommateRequest.recipient_id]",
        back_populates="recipient",
        cascade="all, delete-orphan"
    )
    inquiries = relationship("PropertyInquiry", back_populates="applicant", cascade="all, delete-orphan")
    rental_applications = relationship("RentalApplication", back_populates="applicant", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
    sent_messages = relationship(
        "DirectMessage",
        foreign_keys="[DirectMessage.sender_id]",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_messages = relationship(
        "DirectMessage",
        foreign_keys="[DirectMessage.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
