from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERPER_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    DEFAULT_AI_MODEL: str = "openai/gpt-4o-mini"
    PORT: int = 8000
    
    # In-memory discord settings per spec (configured via UI)
    discord_bot_token: str = ""
    discord_channel_id: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
