from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "local"
    sqlite_db_path: str = "./data/app.db"

    openai_api_key: str = ""
    deepseek_api_key: str = ""
    moonshot_api_key: str = ""

    discord_bot_token: str = ""
    discord_guild_id: int = 0
    discord_review_channel_id: int = 0
    discord_skill8_channel_id: int = 0
    discord_skill9_channel_id: int = 0

    telegram_bot_token: str = ""
    telegram_allowed_user_id: int = 0
    telegram_alert_chat_id: int = 0


@lru_cache
def get_settings() -> Settings:
    return Settings()
