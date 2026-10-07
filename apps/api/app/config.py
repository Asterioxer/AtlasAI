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

    llm_provider: str = "deterministic"
    llm_model: str = "Qwen/Qwen3-4B-Instruct-2507:cheapest"
    llm_endpoint: str = "https://router.huggingface.co/v1/chat/completions"
    hf_token: str = ""
    llm_timeout_seconds: float = 90.0

    # Embeddings are independently configurable from generation. This lets
    # AtlasAI use a hosted semantic encoder without coupling retrieval to the
    # chat model/provider.
    embedding_provider: str = "deterministic"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_endpoint: str = ""
    embedding_dimensions: int = 384
    embedding_timeout_seconds: float = 60.0
    embedding_batch_size: int = 16

    max_upload_bytes: int = 25 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
