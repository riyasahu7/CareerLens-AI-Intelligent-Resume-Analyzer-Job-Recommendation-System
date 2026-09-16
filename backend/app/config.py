"""
Application configuration.
All secrets and environment-specific values are read from environment
variables so that nothing sensitive is ever committed to source control.
"""

import os
from datetime import timedelta


class Config:
    # ------------------------------------------------------------------ #
    # Core Flask                                                           #
    # ------------------------------------------------------------------ #
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = False
    TESTING: bool = False

    # ------------------------------------------------------------------ #
    # MongoDB                                                              #
    # ------------------------------------------------------------------ #
    MONGO_URI: str = os.environ.get(
        "MONGO_URI", "mongodb://localhost:27017/careerlens"
    )

    # ------------------------------------------------------------------ #
    # JWT                                                                  #
    # ------------------------------------------------------------------ #
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", 3600))
    )

    # ------------------------------------------------------------------ #
    # File uploads                                                         #
    # ------------------------------------------------------------------ #
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "/tmp/careerlens_uploads")
    MAX_CONTENT_LENGTH: int = int(os.environ.get("MAX_UPLOAD_MB", 5)) * 1024 * 1024  # default 5 MB
    ALLOWED_EXTENSIONS: set = {"pdf"}

    # ------------------------------------------------------------------ #
    # LLM (optional — leave blank to disable)                             #
    # ------------------------------------------------------------------ #
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    LLM_ENABLED: bool = bool(os.environ.get("OPENAI_API_KEY", ""))

    # ------------------------------------------------------------------ #
    # CORS                                                                 #
    # ------------------------------------------------------------------ #
    CORS_ORIGINS: list = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Values are read from environment (raises clear error only at runtime)
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "")
    MONGO_URI: str = os.environ.get("MONGO_URI", "")


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MONGO_URI: str = os.environ.get(
        "TEST_MONGO_URI", "mongodb://localhost:27017/careerlens_test"
    )


_config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config() -> Config:
    env = os.environ.get("FLASK_ENV", "development")
    return _config_map.get(env, DevelopmentConfig)()
