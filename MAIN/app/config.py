
# This file defines all configuration values the app needs
# (DB connection info, app name, etc.)

# pydantic_settings: Automatically reads environment variables and validates
# their types
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "college_service_request_db"

    # Application name
    APP_NAME: str = "College Service Request System API"

    # Load values from the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Shared settings object that all other files can import
settings = Settings()