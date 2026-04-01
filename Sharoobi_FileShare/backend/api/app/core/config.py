from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Sharoobi FileShare"
    project_slug: str = "deployhub"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    storage_root: str = "/srv/deployhub"
    admin_static_root: str = "/srv/admin"
    database_url: str = "sqlite:///./deployhub.db"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "change_this_jwt_secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "change_this_admin_password"
    bootstrap_api_token: str = "change_this_bootstrap_token"
    primary_share_path: str = r"H:\\"
    office_share_path: str = r"H:\\Office\\2024"
    driver_share_path: str = r"H:\\driver"
    host_node_name: str = "windows-host"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
