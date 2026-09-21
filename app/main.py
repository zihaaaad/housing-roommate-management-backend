from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.exceptions import ApplicationException
from app.core.response import ErrorResponsePayload
from app.database import Base, engine
import app.models
from app.routers import (
    application_router,
    auth_router,
    inquiry_router,
    message_router,
    notification_router,
    property_router,
    room_router,
    roommate_router,
    user_router,
    ws_router,
)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        from seed import seed_database
        seed_database(drop_existing=False)
    except Exception:
        pass
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API for Housing and Roommate Management Platform",
    lifespan=lifespan
)

has_wildcard_origin = "*" in settings.CORS_ORIGINS or settings.CORS_ORIGINS == ["*"]

if has_wildcard_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exception: ApplicationException):
    payload = ErrorResponsePayload(
        success=False,
        error_code=exception.error_code,
        message=exception.detail,
        errors=exception.errors
    )
    return JSONResponse(
        status_code=exception.status_code,
        content=payload.model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    formatted_errors = []
    for error in exception.errors():
        field_location = " -> ".join([str(loc) for loc in error.get("loc", [])])
        formatted_errors.append({
            "field": field_location,
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "value_error")
        })

    payload = ErrorResponsePayload(
        success=False,
        error_code="VALIDATION_ERROR",
        message="One or more fields failed request validation.",
        errors=formatted_errors
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump()
    )


@app.exception_handler(Exception)
async def generic_unhandled_exception_handler(request: Request, exception: Exception):
    payload = ErrorResponsePayload(
        success=False,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload.model_dump()
    )


api_prefix = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=api_prefix)
app.include_router(user_router, prefix=api_prefix)
app.include_router(property_router, prefix=api_prefix)
app.include_router(room_router, prefix=api_prefix)
app.include_router(roommate_router, prefix=api_prefix)
app.include_router(inquiry_router, prefix=api_prefix)
app.include_router(application_router, prefix=api_prefix)
app.include_router(notification_router, prefix=api_prefix)
app.include_router(message_router, prefix=api_prefix)
app.include_router(ws_router, prefix=api_prefix)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Health"])
def root_endpoint():
    return {
        "message": "Welcome to Housing & Roommate Management Platform API",
        "documentation": "/docs",
        "version": "1.0.0"
    }
