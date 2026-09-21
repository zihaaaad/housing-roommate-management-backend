from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        Index("idx_profiles_city_budget", "preferred_city", "budget_min", "budget_max"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    bio = Column(Text, nullable=True)
    occupation = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    budget_min = Column(Float, default=0.0, nullable=False)
    budget_max = Column(Float, default=0.0, nullable=False)
    preferred_city = Column(String(100), index=True, nullable=True)
    preferred_neighborhood = Column(String(150), nullable=True)
    cleanliness_level = Column(String(50), default="MODERATE", nullable=False)
    sleep_schedule = Column(String(50), default="FLEXIBLE", nullable=False)
    smoking_habit = Column(String(50), default="NON_SMOKER", nullable=False)
    pet_habit = Column(String(50), default="PET_FRIENDLY", nullable=False)
    party_habit = Column(String(50), default="OCCASIONALLY", nullable=False)
    dietary_preference = Column(String(50), default="ANY", nullable=False)
    work_status = Column(String(50), default="HYBRID", nullable=False)
    move_in_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User", back_populates="profile")
