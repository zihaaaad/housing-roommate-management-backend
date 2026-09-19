from app.routers.application_router import router as application_router
from app.routers.auth_router import router as auth_router
from app.routers.inquiry_router import router as inquiry_router
from app.routers.message_router import router as message_router
from app.routers.notification_router import router as notification_router
from app.routers.property_router import router as property_router
from app.routers.room_router import router as room_router
from app.routers.roommate_router import router as roommate_router
from app.routers.user_router import router as user_router

__all__ = [
    "auth_router",
    "user_router",
    "property_router",
    "room_router",
    "roommate_router",
    "inquiry_router",
    "application_router",
    "notification_router",
    "message_router",
]
