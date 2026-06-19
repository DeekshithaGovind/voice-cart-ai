from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://voicecart:voicecart@localhost:5432/voicecart"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"
    whisper_model: str = "base"
    enable_tier3_llm: bool = False
    webhook_url: str = ""
    erp_webhook_url: str = ""
    max_clarification_attempts: int = 2
    order_stream_key: str = "voicecart:orders"
    dashboard_channel: str = "voicecart:dashboard"


settings = Settings()
