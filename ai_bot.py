import io
from typing import Optional
from openai import AsyncOpenAI

from dao import user_dao
from core.settings import settings
import hashlib, base64, json


class AIBot:
    def __init__(self, token, assistant_id):
        self.__token = token
        self._client = AsyncOpenAI(api_key=self.__token)
        self.assistant_id = assistant_id
        self.user_threads: dict = {}

    async def voice_to_text(self, voice_file: io.BufferedReader) -> str:
        """Конвертация голосового сообщения в текст."""
        transcription = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=voice_file
        )
        return transcription.text

    async def get_user_assistant(self, user_id) -> Assistant:
        """Получаем или создаем нового AI ассистента."""
        if user_id not in self.assistants:
            self.assistants[user_id] = await self._client.beta.assistants.create(
                name=f"AI Assistant for {user_id}",
                instructions=default_prompt_for_ai,
                model="gpt-4o",
            )
        return self.assistants[user_id]

    async def get_answer_for_message(self, user_id: str, question_text: str) -> Optional[str]:
        """Асинхронное получение ответа от OpenAI.
         Если бот успешно даст ответ на вопрос, мы отправляем его, иначе вернется None."""
        assistant = await self.get_user_assistant(user_id)

        # Создаём новый поток
        thread = await self._client.beta.threads.create()

        # Отправляем сообщение в поток
        await self._client.beta.threads.messages.create(
            thread_id=thread.id,
            content=question_text,
            role="user"
        )

        # Запускаем ассистента
        run = await self._client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=default_prompt_for_ai
        )

        if run.status == "completed":
            messages = await self._client.beta.threads.messages.list(thread_id=thread.id)

            # Ищем последнее сообщение от ассистента
            for message in reversed(messages.data):
                if message.role == "assistant":
                    return message.content[0].text.value  # Получаем текст ответа


    async def text_to_voice(self, text) -> str:
        """Конвертация текста в голос."""
        short_hash = lambda txt: base64.b32encode(hashlib.md5(txt.encode()).digest())[:6].decode()
        speech_file_path = f'voice/upload/{short_hash(text)}.mp3'
        response = await self._client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path


ai_bot = AIBot(settings.settings.open_ai_token)
