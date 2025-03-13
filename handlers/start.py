from aiogram import Router, F
from aiogram.types import Message

start_router = Router()


@start_router.message(F.text == '/start')
async def handle_start(message: Message) -> None:
    """Обработка команды /start"""
    author_telegram_link = "https://t.me/azirafiele"
    answer_text = (f"Добро пожаловать в бота разработанного <a href='{author_telegram_link}'>Роман Алексеевичем</a>.\n\n"
                   f"Бот способен ответить на любой ваш вопрос. Просто запишите голосовое сообщение")
    await message.answer(text=answer_text, parse_mode="HTML", link_preview_options=None)


