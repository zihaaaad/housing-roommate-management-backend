from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session, joinedload, selectinload
from app.core.exceptions import BadRequestException, ForbiddenException, ResourceNotFoundException
from app.models.property import Property
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyFilterParams, PropertyUpdate


class PropertyService:
    def __init__(self, db: Session):
        self.db = db

    def create_property(self, landlord_id: int, payload: PropertyCreate) -> Property:
        data = payload.model_dump()
        if "property_type" in data and hasattr(data["property_type"], "value"):
            data["property_type"] = data["property_type"].value
        if "furnished_status" in data and hasattr(data["furnished_status"], "value"):
            data["furnished_status"] = data["furnished_status"].value

        new_property = Property(
            landlord_id=landlord_id,
            **data
        )
        self.db.add(new_property)
        self.db.commit()
        self.db.refresh(new_property)
        return new_property

    def get_property_by_id(self, property_id: int) -> Property:
        property_record = self.db.query(Property).options(
            joinedload(Property.landlord),
            selectinload(Property.rooms)
        ).filter(Property.id == property_id).first()

        if not property_record:
            raise ResourceNotFoundException("Property", property_id)
        return property_record

    def update_property(self, property_id: int, current_user: User, payload: PropertyUpdate) -> Property:
        property_record = self.get_property_by_id(property_id)

        if property_record.landlord_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("You can only modify your own property listings.")

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(property_record, key):
                enum_value = value.value if hasattr(value, "value") else value
                setattr(property_record, key, enum_value)

        property_record.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(property_record)
        return property_record

    def delete_property(self, property_id: int, current_user: User) -> None:
        property_record = self.get_property_by_id(property_id)

        if property_record.landlord_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("You can only delete your own property listings.")

        self.db.delete(property_record)
        self.db.commit()

    def list_properties_extended(self, filters: PropertyFilterParams) -> Tuple[List[Property], int]:
        if filters.min_rent is not None and filters.max_rent is not None and filters.min_rent > filters.max_rent:
            raise BadRequestException("Minimum rent cannot exceed maximum rent.")

        if filters.available_from_start and filters.available_from_end and filters.available_from_start > filters.available_from_end:
            raise BadRequestException("Start availability date cannot be after end date.")

        query = self.db.query(Property).options(
            joinedload(Property.landlord),
            selectinload(Property.rooms)
        )

        if filters.search:
            search_text = f"%{filters.search.strip()}%"
            conditions = [
                Property.title.ilike(search_text),
                Property.description.ilike(search_text),
                Property.city.ilike(search_text),
                Property.address.ilike(search_text)
            ]
            if filters.search.strip().isdigit():
                conditions.append(Property.id == int(filters.search.strip()))
            query = query.filter(or_(*conditions))

        if filters.property_type:
            query = query.filter(Property.property_type == filters.property_type.value)

        if filters.status:
            query = query.filter(Property.status == filters.status.value)
        else:
            query = query.filter(Property.status == "AVAILABLE")

        if filters.city:
            query = query.filter(Property.city.ilike(f"%{filters.city.strip()}%"))

        if filters.min_rent is not None:
            query = query.filter(Property.base_monthly_rent >= filters.min_rent)

        if filters.max_rent is not None:
            query = query.filter(Property.base_monthly_rent <= filters.max_rent)

        if filters.min_bedrooms is not None:
            query = query.filter(Property.total_bedrooms >= filters.min_bedrooms)

        if filters.min_bathrooms is not None:
            query = query.filter(Property.total_bathrooms >= filters.min_bathrooms)

        if filters.is_pet_friendly is not None:
            query = query.filter(Property.is_pet_friendly == filters.is_pet_friendly)

        if filters.furnished_status:
            query = query.filter(Property.furnished_status == filters.furnished_status.value)

        if filters.available_from_start:
            query = query.filter(Property.available_from >= filters.available_from_start)

        if filters.available_from_end:
            query = query.filter(Property.available_from <= filters.available_from_end)

        sort_column_map = {
            "created_at": Property.created_at,
            "base_monthly_rent": Property.base_monthly_rent,
            "title": Property.title,
            "available_from": Property.available_from
        }
        target_sort_column = sort_column_map.get(filters.sort_by, Property.created_at)
        ordering_function = desc if filters.sort_order.lower() == "desc" else asc
        query = query.order_by(ordering_function(target_sort_column))

        total_count = query.count()
        offset_value = (filters.page - 1) * filters.limit
        results = query.offset(offset_value).limit(filters.limit).all()

        return results, total_count

    def get_landlord_properties(self, landlord_id: int) -> List[Property]:
        return self.db.query(Property).filter(Property.landlord_id == landlord_id).order_by(Property.created_at.desc()).all()
