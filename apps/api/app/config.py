from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "atlasai"
    postgres_user: str = "atlasai"
    postgres_password: str = "atlasai"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
