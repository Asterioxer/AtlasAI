from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
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
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
