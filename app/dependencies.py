from typing import Annotated, Callable, Optional, Sequence
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.database import get_db_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_current_authenticated_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DatabaseSession
) -> User:
    token_payload = decode_access_token(token)
    user_id_string = token_payload.get("sub")
    if not user_id_string:
        raise UnauthorizedException("Invalid user identifier in token.")

    user = db.query(User).filter(User.id == int(user_id_string)).first()
    if not user:
        raise UnauthorizedException("User associated with this token no longer exists.")
    if not user.is_active:
        raise UnauthorizedException("User account has been deactivated.")

    return user


CurrentUser = Annotated[User, Depends(get_current_authenticated_user)]


def get_optional_authenticated_user(
    db: DatabaseSession,
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False))
) -> Optional[User]:
    if not token:
        return None
    try:
        token_payload = decode_access_token(token)
        user_id_string = token_payload.get("sub")
        if not user_id_string:
            return None
        user = db.query(User).filter(User.id == int(user_id_string)).first()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


OptionalCurrentUser = Annotated[Optional[User], Depends(get_optional_authenticated_user)]


def require_roles(*allowed_roles: Sequence[str]) -> Callable[[User], User]:
    def role_validator(current_user: CurrentUser) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Access denied. Requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_validator
