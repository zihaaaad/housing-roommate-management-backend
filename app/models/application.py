from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class RentalApplication(Base):
    __tablename__ = "rental_applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), index=True, nullable=True)
    applicant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    proposed_move_in_date = Column(DateTime, nullable=False)
    lease_duration_months = Column(Integer, default=12, nullable=False)
    monthly_income = Column(Float, nullable=False)
    credit_score = Column(Integer, nullable=True)
    employment_status = Column(String(100), nullable=False)
    emergency_contact_name = Column(String(150), nullable=False)
    emergency_contact_phone = Column(String(50), nullable=False)
    status = Column(String(50), default="PENDING", index=True, nullable=False)
    landlord_decision_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    property = relationship("Property", back_populates="applications")
    room = relationship("Room", back_populates="applications")
    applicant = relationship("User", back_populates="rental_applications")
