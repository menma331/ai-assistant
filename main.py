import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from core.settings import settings
from handlers.start import start_router
from handlers.ai import ai_router
from redis import Redis

redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)

# Настройка хранилища для FSM
storage = RedisStorage(redis=redis_client)

bot = Bot(token=settings.tg_bot_token)
dp = Dispatcher()



async def start():
    os.makedirs("voice/download", exist_ok=True)
    os.makedirs("voice/upload", exist_ok=True)
    os.makedirs('photos', exist_ok=True)

    logging.basicConfig(level=logging.INFO)  # Чтобы видеть, как бот обрабатывает сообщения

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(ai_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start())
