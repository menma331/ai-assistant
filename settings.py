from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    tg_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN", description="Токен телеграм бота(обязателен)")
    open_ai_token: str = Field(alias="OPEN_AI_TOKEN", description="Токен OpenAI(обязателен)")

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()
