from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False)
    room_name = Column(String(100), nullable=False)
    room_type = Column(String(50), default="SINGLE", nullable=False)
    monthly_rent = Column(Float, index=True, nullable=False)
    security_deposit = Column(Float, default=0.0, nullable=False)
    is_available = Column(Boolean, default=True, index=True, nullable=False)
    private_bathroom = Column(Boolean, default=False, nullable=False)
    square_feet = Column(Integer, nullable=True)
    available_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    property = relationship("Property", back_populates="rooms")
    applications = relationship("RentalApplication", back_populates="room")
