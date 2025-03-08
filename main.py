import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from settings import settings
from handlers.start import start_router
from handlers.ai import ai_router

bot = Bot(token=settings.tg_bot_token)
dp = Dispatcher()



async def start():
    os.makedirs("voice/download", exist_ok=True)
    os.makedirs("voice/upload", exist_ok=True)

    logging.basicConfig(level=logging.INFO)  # Чтобы видеть, как бот обрабатывает сообщения

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(ai_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start())
