import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    PROJECT_NAME: str = "Housing & Roommate Management Platform"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "e5b542c10bd817f140d17e68551e8d298296e5a30f3f565510297aabb35b2c3d"
    REFRESH_SECRET_KEY: str = "9f82d8c36b69b2d847120a112048f075d9e54d6a8946e3a5c2d3a778ef1092ab"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./housing_roommates.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                return json.loads(value)
            return [origin.strip() for origin in value.split(",")]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = ApplicationSettings()
