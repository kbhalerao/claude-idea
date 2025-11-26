"""Configuration for Chief of Staff API"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Couchbase connection
    couchbase_host: str = "macstudio.local"
    couchbase_username: str = "Administrator"
    couchbase_password: str = ""
    couchbase_bucket: str = "chief_of_staff"

    # API settings
    api_prefix: str = "/api/cos"
    debug: bool = False

    # Default user email (for development/testing)
    default_user: str = "kaustubh@codesmriti.dev"

    class Config:
        env_file = ".env"
        env_prefix = "COS_"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
