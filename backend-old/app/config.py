from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_PRO_MONTHLY: str
    STRIPE_PRICE_PRO_YEARLY: str
    STRIPE_PRICE_BUSINESS: str

    RESEND_API_KEY: str
    EMAIL_FROM: str = "noreply@pontevpn.com"

    REDIS_URL: str = "redis://localhost:6379"
    APP_URL: str = "https://pontevpn.com"
    API_URL: str = "https://api.pontevpn.com"
    ENVIRONMENT: str = "production"
    VPN_SERVERS_API_SECRET: str

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Apple OAuth
    APPLE_CLIENT_ID: str = ""
    APPLE_TEAM_ID: str = ""
    APPLE_KEY_ID: str = ""
    APPLE_PRIVATE_KEY_PATH: str = ""

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"

    class Config:
        env_file = ".env"


settings = Settings()
