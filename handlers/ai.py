import os

from aiogram import Router, F
from aiogram.enums import ContentType, ChatAction
from aiogram.types import Message, FSInputFile

from ai_bot import ai_bot
from utils.audio import download_voice_message

ai_router = Router()


@ai_router.message(F.content_type == ContentType.VOICE)
async def handle_voice_message(message: Message) -> None:
    """Обработка голосового сообщения от пользователя.

    Последовательность действий:\n
    1) Скачиваем голосовое
    2) Конвертируем в текст
    3) Получаем ответ на вопрос с помощью AI Assistants
    4) Конвертируем текстовый ответ в ГС
    5) Отправляем голосовой ответ пользователю
    """
    error_message_text = ("Произошла непредвиденная ошибка не сервере."
                                  " Свяжитесь с <a href='https://t.me/azirafiele'>разработчиком</a>.")
    file_id = message.voice.file_id
    bot = message.bot
    file = await bot.get_file(file_id)
    file_path = file.file_path

    user_id = message.from_user.id
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.RECORD_VOICE)
    user_voice_message_path = await download_voice_message(file_id=file_id, file_path=file_path, user_id=user_id)
    if not user_voice_message_path:
        await message.answer(text=error_message_text, parse_mode="HTML")
        return

    with open(user_voice_message_path, 'rb') as audio_file:
        user_voice_text = await ai_bot.voice_to_text(audio_file)

    if not user_voice_text:
        await message.answer(text=error_message_text, parse_mode="HTML")

    os.remove(user_voice_message_path)

    answer_for_message = await ai_bot.get_answer_for_message(user_id=user_id, question_text=user_voice_text)

    if not answer_for_message:
        await message.answer(text='Не могу дать ответ на ваш вопрос.')

    voice_answer_path = await ai_bot.text_to_voice(answer_for_message)

    await message.answer_voice(voice=FSInputFile(path=voice_answer_path))

    os.remove(voice_answer_path)


