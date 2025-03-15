from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


load_dotenv()

class Settings(BaseSettings):
    tg_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN", description="Токен телеграм бота(обязателен)")

    open_ai_token: str = Field(alias="OPEN_AI_TOKEN", description="Токен OpenAI(обязателен)")
    open_ai_assistant_id: str = Field(alias="OPEN_AI_ASSISTANT_ID", description="ID созданного ассистента. Может создаться кодом, либо в панели управления "
                                                                                "OpenAI")
    vector_store_id:str=Field(alias="VECTOR_STORE_ID", description="Vector store ID")
    amplitude_api_key: str = Field(alias="AMPLITUDE_API_KEY", description="АПИ ключ от Amplitude")

    database_connection_string: str = Field(alias="DB_CONNECTION_STRING", description="Строка подключения к базе данных в формате DSN")

    redis_host: str = Field(alias="REDIS_HOST", description="Redis host")
    redis_port: int = Field(alias="REDIS_PORT", description="Redis port")

    model_config = SettingsConfigDict(env_file='./.env', env_file_encoding="utf-8")

settings = Settings()
