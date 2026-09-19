from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class PropertyInquiry(Base):
    __tablename__ = "property_inquiries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), index=True, nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    scheduled_viewing_date = Column(DateTime, index=True, nullable=False)
    status = Column(String(50), default="PENDING", index=True, nullable=False)
    notes = Column(Text, nullable=True)
    landlord_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    property = relationship("Property", back_populates="inquiries")
    applicant = relationship("User", back_populates="inquiries")
