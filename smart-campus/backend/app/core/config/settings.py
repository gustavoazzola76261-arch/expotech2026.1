from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Smart Campus API"

    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True

    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_THIS"

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()