from typing import Any, Optional
from fastapi import HTTPException, status


class ApplicationException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        errors: Optional[Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.errors = errors


class ResourceNotFoundException(ApplicationException):
    def __init__(self, resource_name: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} with identifier {identifier} was not found.",
            error_code="RESOURCE_NOT_FOUND"
        )


class BadRequestException(ApplicationException):
    def __init__(self, detail: str, errors: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST",
            errors=errors
        )


class UnauthorizedException(ApplicationException):
    def __init__(self, detail: str = "Invalid or expired credentials."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED"
        )


class ForbiddenException(ApplicationException):
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="FORBIDDEN"
        )


class ConflictException(ApplicationException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT"
        )
