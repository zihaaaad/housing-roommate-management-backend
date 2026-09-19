from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.config import settings
from app.core.exceptions import BadRequestException, ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_secure_random_token,
    hash_password,
    hash_token_sha256,
    verify_password,
)
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    RefreshTokenResponse,
    ResetPasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserSummaryResponse,
)


class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, payload: UserRegisterRequest) -> User:
        normalized_email = payload.email.strip().lower()
        normalized_username = payload.username.strip().lower()

        existing_email = self.db.query(User).filter(func.lower(User.email) == normalized_email).first()
        if existing_email:
            raise ConflictException("An account with this email already exists.")

        existing_username = self.db.query(User).filter(func.lower(User.username) == normalized_username).first()
        if existing_username:
            raise ConflictException("An account with this username already exists.")

        hashed_password = hash_password(payload.password)
        new_user = User(
            email=normalized_email,
            username=normalized_username,
            full_name=payload.full_name.strip(),
            phone_number=payload.phone_number.strip() if payload.phone_number else None,
            role=payload.role.value,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True
        )
        self.db.add(new_user)
        self.db.flush()

        initial_profile = UserProfile(
            user_id=new_user.id,
            bio="",
            occupation="",
            budget_min=0.0,
            budget_max=0.0
        )
        self.db.add(initial_profile)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_and_login(self, payload: UserLoginRequest) -> AuthTokenResponse:
        identifier = payload.username_or_email.strip().lower()
        user = self.db.query(User).filter(
            (func.lower(User.username) == identifier) | (func.lower(User.email) == identifier)
        ).first()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedException("Invalid username/email or password.")

        if not user.is_active:
            raise UnauthorizedException("Your account is currently disabled.")

        token_claims = {
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
        access_token = create_access_token(str(user.id), token_claims)
        refresh_token = create_refresh_token(str(user.id))

        user.hashed_refresh_token = hash_token_sha256(refresh_token)
        self.db.commit()

        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserSummaryResponse.model_validate(user)
        )

    def refresh_access_token(self, refresh_token: str) -> RefreshTokenResponse:
        token_payload = decode_refresh_token(refresh_token)
        user_id = token_payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token subject.")

        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise UnauthorizedException("User account is inactive or not found.")

        provided_token_hash = hash_token_sha256(refresh_token)
        if user.hashed_refresh_token != provided_token_hash:
            raise UnauthorizedException("Refresh token is invalid or has been revoked.")

        token_claims = {
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
        new_access_token = create_access_token(str(user.id), token_claims)
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def initiate_password_reset(self, payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
        user = self.db.query(User).filter(User.email == payload.email).first()
        if not user:
            return ForgotPasswordResponse(
                message="If the email exists, a password reset link has been sent."
            )

        raw_reset_token = generate_secure_random_token()
        user.password_reset_token_hash = hash_token_sha256(raw_reset_token)
        user.password_reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        self.db.commit()

        return ForgotPasswordResponse(
            message="If the email exists, a password reset link has been sent.",
            reset_token=raw_reset_token
        )

    def complete_password_reset(self, payload: ResetPasswordRequest) -> None:
        token_hash = hash_token_sha256(payload.reset_token)
        user = self.db.query(User).filter(
            User.password_reset_token_hash == token_hash
        ).first()

        if not user or not user.password_reset_token_expires_at:
            raise BadRequestException("Invalid or expired password reset token.")

        token_expiration = user.password_reset_token_expires_at
        if token_expiration.tzinfo is None:
            token_expiration = token_expiration.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > token_expiration:
            raise BadRequestException("Password reset token has expired.")

        user.hashed_password = hash_password(payload.new_password)
        user.password_reset_token_hash = None
        user.password_reset_token_expires_at = None
        user.hashed_refresh_token = None
        self.db.commit()

    def change_password(self, user_id: int, payload: ChangePasswordRequest) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UnauthorizedException("User not found.")

        if not verify_password(payload.current_password, user.hashed_password):
            raise BadRequestException("Current password verification failed.")

        user.hashed_password = hash_password(payload.new_password)
        user.hashed_refresh_token = None
        self.db.commit()
