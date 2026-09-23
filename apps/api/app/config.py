from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "atlasai"
    postgres_user: str = "atlasai"
    postgres_password: str = "atlasai"
    redis_url: str = "redis://localhost:6379/0"
    auth_mode: str = "local"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = ""
    jwt_audience: str = ""
    cors_origins: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
