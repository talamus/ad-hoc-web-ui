"""Application configuration using pydantic-settings"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration using pydantic-settings"""

    # JWT Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=1440, description="Token expiration in minutes (24 hours)"
    )

    # Security Configuration
    secure_cookies: bool = Field(
        default=False, description="Enable secure flag on cookies (HTTPS only)"
    )
    csrf_secret_key: Optional[str] = Field(
        default=None, description="CSRF secret key (defaults to secret_key)"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Enable auto-reload")

    # Application Settings
    app_name: str = Field(default="Ad Hoc Web UI", description="Application name")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./adhoc_users.db", description="Database URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is uppercase"""
        return v.upper()

    @field_validator("csrf_secret_key", mode="after")
    @classmethod
    def default_csrf_key(cls, v: Optional[str], info) -> str:
        """Default CSRF key to secret_key if not provided"""
        if v is None:
            return info.data.get("secret_key", "")
        return v


# Create settings instance
settings = Settings()
