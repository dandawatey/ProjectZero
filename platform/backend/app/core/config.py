from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "ProjectZero Factory API"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/projectzero"

    # Temporal
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "projectzero-factory"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # JIRA
    jira_base_url: str = ""
    jira_user_email: str = ""
    jira_api_token: str = ""
    jira_board_id: str = ""
    jira_story_points_field: str = "customfield_10016"
    # Health monitor: seconds between keep-alive pings
    jira_health_interval: int = 60
    # Circuit breaker: failures before opening
    jira_circuit_breaker_threshold: int = 3
    # Circuit breaker: seconds before half-open retry
    jira_circuit_breaker_timeout: int = 30

    # Confluence
    confluence_base_url: str = ""
    confluence_api_token: str = ""
    # Space key where product pages live
    confluence_space_key: str = "PZF"
    # Parent page title under which product pages are created
    confluence_parent_page_title: str = "ProjectZero Products"
    # Health monitor interval (seconds)
    confluence_health_interval: int = 60

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # JWT / Auth
    jwt_secret_key: str = "changeme-set-JWT_SECRET_KEY-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # OAuth2 / Social login
    frontend_url: str = "http://localhost:3000"
    oauth_redirect_base_url: str = "http://localhost:8000"
    # Google OAuth2
    google_client_id: str = ""
    google_client_secret: str = ""
    # Microsoft / Azure AD OAuth2
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    microsoft_tenant_id: str = "common"
    # Company SSO — OIDC (set discovery URL to your IdP)
    sso_client_id: str = ""
    sso_client_secret: str = ""
    sso_discovery_url: str = ""   # e.g. https://login.example.com/.well-known/openid-configuration
    sso_display_name: str = "Company SSO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
