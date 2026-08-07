from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    ENV: str = "development"

    DATABASE_URL: str

    ALLOW_ORIGINS: list[str]

    GEMINI_API_KEY: str | None = None

    GEMINI_EMBEDDING_MODEL: str
    GEMINI_EMBEDDING_DIMENSION: int

    GEMINI_MODEL: str

    OPENAI_MODEL: str
    OPENAI_EMBEDDING_MODEL: str
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()