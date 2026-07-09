from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/agentops"

    llm_provider: str = "openrouter"
    llm_model: str = "openai/gpt-oss-20b:free"
    openrouter_api_key: str = ""

    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def testing(self) -> bool:
        return self.app_env == "test"


settings = Settings()
