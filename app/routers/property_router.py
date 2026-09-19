from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.core.response import PaginatedApiResponse, PaginationMetadata, StandardApiResponse
from app.dependencies import CurrentUser, DatabaseSession, require_roles
from app.models.user import User
from app.schemas.auth import UserSummaryResponse
from app.schemas.common import FurnishedStatus, MessageOnlyResponse, PropertyStatus, PropertyType, UserRole
from app.schemas.property import (
    PropertyCreate,
    PropertyDetailResponse,
    PropertyFilterParams,
    PropertyResponse,
    PropertyUpdate,
)
from app.schemas.room import RoomResponse
from app.services.property_service import PropertyService

router = APIRouter(prefix="/properties", tags=["Properties & Listings"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StandardApiResponse[PropertyResponse])
def create_property(
    payload: PropertyCreate,
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.LANDLORD.value, UserRole.ADMIN.value))
):
    property_service = PropertyService(db)
    property_record = property_service.create_property(current_user.id, payload)
    return StandardApiResponse(
        message="Property listing created successfully.",
        data=PropertyResponse.model_validate(property_record)
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedApiResponse[PropertyResponse])
def list_properties(
    db: DatabaseSession,
    search: Optional[str] = Query(default=None),
    property_type: Optional[PropertyType] = Query(default=None),
    property_status: Optional[PropertyStatus] = Query(default=None, alias="status"),
    city: Optional[str] = Query(default=None),
    min_rent: Optional[float] = Query(default=None, ge=0),
    max_rent: Optional[float] = Query(default=None, ge=0),
    min_bedrooms: Optional[int] = Query(default=None, ge=0),
    min_bathrooms: Optional[int] = Query(default=None, ge=0),
    is_pet_friendly: Optional[bool] = Query(default=None),
    furnished_status: Optional[FurnishedStatus] = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    filters = PropertyFilterParams(
        search=search,
        property_type=property_type,
        status=property_status,
        city=city,
        min_rent=min_rent,
        max_rent=max_rent,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        is_pet_friendly=is_pet_friendly,
        furnished_status=furnished_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )
    property_service = PropertyService(db)
    properties, total_items = property_service.list_properties_extended(filters)
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

    return PaginatedApiResponse(
        message="Properties retrieved successfully.",
        data=[PropertyResponse.model_validate(p) for p in properties],
        pagination=PaginationMetadata(
            page=page,
            limit=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next_page=page < total_pages,
            has_prev_page=page > 1
        )
    )


@router.get("/my-listings", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[List[PropertyResponse]])
def get_my_property_listings(
    db: DatabaseSession,
    current_user: User = Depends(require_roles(UserRole.LANDLORD.value, UserRole.ADMIN.value))
):
    property_service = PropertyService(db)
    properties = property_service.get_landlord_properties(current_user.id)
    return StandardApiResponse(
        message="Landlord listings retrieved.",
        data=[PropertyResponse.model_validate(p) for p in properties]
    )


@router.get("/{property_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[PropertyDetailResponse])
def get_property_details(property_id: int, db: DatabaseSession):
    property_service = PropertyService(db)
    property_record = property_service.get_property_by_id(property_id)

    response_data = PropertyDetailResponse.model_validate(property_record)
    if property_record.landlord:
        response_data.landlord = UserSummaryResponse.model_validate(property_record.landlord)
    if property_record.rooms:
        response_data.rooms = [RoomResponse.model_validate(r) for r in property_record.rooms]

    return StandardApiResponse(
        message="Property details retrieved.",
        data=response_data
    )


@router.put("/{property_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[PropertyResponse])
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    property_service = PropertyService(db)
    updated_property = property_service.update_property(property_id, current_user, payload)
    return StandardApiResponse(
        message="Property listing updated successfully.",
        data=PropertyResponse.model_validate(updated_property)
    )


@router.delete("/{property_id}", status_code=status.HTTP_200_OK, response_model=StandardApiResponse[MessageOnlyResponse])
def delete_property(
    property_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    property_service = PropertyService(db)
    property_service.delete_property(property_id, current_user)
    return StandardApiResponse(
        message="Property listing deleted successfully.",
        data=MessageOnlyResponse(message=f"Property with ID {property_id} has been removed.")
    )
