from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    tg_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN", description="Токен телеграм бота(обязателен)")

    open_ai_token: str = Field(alias="OPEN_AI_TOKEN", description="Токен OpenAI(обязателен)")
    open_ai_assistant_id: str = Field(alias="OPEN_AI_ASSISTANT_ID", description="ID созданного ассистента. Может создаться кодом, либо в панели управления "
                                                                                "OpenAI")
    amplitude_api_key: str = Field(alias="AMPLITUDE_API_KEY", description="АПИ ключ от Amplitude")

    database_connection_string: str = Field(alias="DB_CONNECTION_STRING", description="Строка подключения к базе данных в формате DSN")

    model_config = SettingsConfigDict(env_file='./.env')

settings = Settings()
