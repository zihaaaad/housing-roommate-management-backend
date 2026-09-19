from typing import List, Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, ResourceNotFoundException
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import UserProfileUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user

    def get_user_profile(self, user_id: int) -> UserProfile:
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def update_user_profile(self, user_id: int, payload: UserProfileUpdate) -> UserProfile:
        profile = self.get_user_profile(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(profile, key):
                enum_value = value.value if hasattr(value, "value") else value
                setattr(profile, key, enum_value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_user_basic_details(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        user = self.get_user_by_id(user_id)
        if full_name is not None:
            user.full_name = full_name
        if phone_number is not None:
            user.phone_number = phone_number
        if avatar_url is not None:
            user.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(
        self,
        search: Optional[str] = None,
        role: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[User], int]:
        query = self.db.query(User)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_filter),
                    User.email.ilike(search_filter),
                    User.full_name.ilike(search_filter)
                )
            )
        if role:
            query = query.filter(User.role == role)

        total_count = query.count()
        users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return users, total_count

    def toggle_user_active_status(self, user_id: int, is_active: bool) -> User:
        user = self.get_user_by_id(user_id)
        user.is_active = is_active
        if not is_active:
            user.hashed_refresh_token = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user_role(self, user_id: int, new_role: str) -> User:
        user = self.get_user_by_id(user_id)
        user.role = new_role
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int, current_user: User) -> None:
        if user_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("Unauthorized to delete this account.")
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()

