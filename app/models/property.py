from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    landlord_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    property_type = Column(String(50), default="APARTMENT", index=True, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), index=True, nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(30), nullable=True)
    country = Column(String(100), default="Bangladesh", nullable=False)
    total_bedrooms = Column(Integer, default=1, nullable=False)
    total_bathrooms = Column(Integer, default=1, nullable=False)
    square_feet = Column(Integer, nullable=True)
    furnished_status = Column(String(50), default="UNFURNISHED", nullable=False)
    is_pet_friendly = Column(Boolean, default=False, index=True, nullable=False)
    is_smoking_allowed = Column(Boolean, default=False, nullable=False)
    parking_available = Column(Boolean, default=False, nullable=False)
    amenities = Column(String(500), default="", nullable=False)
    base_monthly_rent = Column(Float, index=True, nullable=False)
    security_deposit = Column(Float, default=0.0, nullable=False)
    utilities_included = Column(Boolean, default=False, nullable=False)
    available_from = Column(DateTime, index=True, default=lambda: datetime.now(timezone.utc), nullable=False)
    lease_duration_months = Column(Integer, default=12, nullable=False)
    status = Column(String(50), default="AVAILABLE", index=True, nullable=False)
    image_urls = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    landlord = relationship("User", back_populates="properties")
    rooms = relationship("Room", back_populates="property", cascade="all, delete-orphan")
    inquiries = relationship("PropertyInquiry", back_populates="property", cascade="all, delete-orphan")
    applications = relationship("RentalApplication", back_populates="property", cascade="all, delete-orphan")
