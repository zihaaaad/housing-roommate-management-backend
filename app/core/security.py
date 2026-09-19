import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
from jose import JWTError, jwt
from app.config import settings
from app.core.exceptions import UnauthorizedException


def hash_password(plain_password: str) -> str:
    encoded_bytes = plain_password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(encoded_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(subject_identifier: str, claims: Optional[Dict[str, Any]] = None) -> str:
    payload: Dict[str, Any] = {}
    if claims:
        payload.update(claims)
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({
        "sub": str(subject_identifier),
        "exp": expiration_time,
        "type": "access"
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject_identifier: str) -> str:
    expiration_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject_identifier),
        "exp": expiration_time,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(encoded_token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(encoded_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_type = payload.get("type")
        if token_type != "access":
            raise UnauthorizedException("Invalid token type for access.")
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid access token or token has expired.")


def decode_refresh_token(encoded_token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(encoded_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise UnauthorizedException("Invalid token type for refresh.")
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid refresh token or token has expired.")


def generate_secure_random_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token_sha256(token_value: str) -> str:
    return hashlib.sha256(token_value.encode("utf-8")).hexdigest()
