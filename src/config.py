from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/tasks.db"
    environment: str = "dev"
    llm_provider: str = "openai"  # e.g. 'openai', 'anthropic', 'stub'
    # IMPORTANT: Do NOT hard-code real API keys here. Set LLM_API_KEY in your .env instead.
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
