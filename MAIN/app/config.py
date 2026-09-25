# This file defines all configuration values the app needs
# (DB connection info, app name, etc)

# pydantic_settings: automatically reads environment variables and validates
# their types
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "college_service"

    # Gives the app a name
    APP_NAME: str = "College Service Request App API"

    # Informs pydatic-settings to load values from .env file
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

# Shared settings Object that all other files can import
settings = Settings()