from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, ResourceNotFoundException
from app.models.property import Property
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
    def __init__(self, db: Session):
        self.db = db

    def create_room(self, property_id: int, current_user: User, payload: RoomCreate) -> Room:
        property_record = self.db.query(Property).filter(Property.id == property_id).first()
        if not property_record:
            raise ResourceNotFoundException("Property", property_id)

        if property_record.landlord_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("You can only add rooms to your own properties.")

        room_data = payload.model_dump()
        if "room_type" in room_data and hasattr(room_data["room_type"], "value"):
            room_data["room_type"] = room_data["room_type"].value

        new_room = Room(
            property_id=property_id,
            **room_data
        )
        self.db.add(new_room)
        self.db.commit()
        self.db.refresh(new_room)
        return new_room

    def get_room_by_id(self, room_id: int) -> Room:
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ResourceNotFoundException("Room", room_id)
        return room

    def update_room(self, room_id: int, current_user: User, payload: RoomUpdate) -> Room:
        room = self.get_room_by_id(room_id)
        property_record = self.db.query(Property).filter(Property.id == room.property_id).first()

        if property_record.landlord_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("You can only modify rooms of your own properties.")

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(room, key):
                enum_value = value.value if hasattr(value, "value") else value
                setattr(room, key, enum_value)

        self.db.commit()
        self.db.refresh(room)
        return room

    def delete_room(self, room_id: int, current_user: User) -> None:
        room = self.get_room_by_id(room_id)
        property_record = self.db.query(Property).filter(Property.id == room.property_id).first()

        if property_record.landlord_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException("You can only delete rooms of your own properties.")

        self.db.delete(room)
        self.db.commit()

    def get_rooms_by_property_id(self, property_id: int) -> List[Room]:
        return self.db.query(Room).filter(Room.property_id == property_id).all()
