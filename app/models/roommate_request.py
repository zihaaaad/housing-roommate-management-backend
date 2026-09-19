from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class RoommateRequest(Base):
    __tablename__ = "roommate_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="SET NULL"), index=True, nullable=True)
    status = Column(String(50), default="PENDING", index=True, nullable=False)
    message = Column(Text, nullable=False)
    response_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    requester = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="sent_roommate_requests"
    )
    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="received_roommate_requests"
    )
    property = relationship("Property")
