from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataType = TypeVar("DataType")


class PaginationMetadata(BaseModel):
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next_page: bool
    has_prev_page: bool


class StandardApiResponse(BaseModel, Generic[DataType]):
    success: bool = True
    message: str = "Operation completed successfully."
    data: Optional[DataType] = None


class PaginatedApiResponse(BaseModel, Generic[DataType]):
    success: bool = True
    message: str = "Data retrieved successfully."
    data: List[DataType]
    pagination: PaginationMetadata


class ErrorResponsePayload(BaseModel):
    success: bool = False
    error_code: str
    message: str
    errors: Optional[List[dict]] = None
