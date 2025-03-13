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

    async def get_user_thread(self, user_id: int) -> str:
        """Получение пользовательского треда, либо создание."""
        if user_id not in self.user_threads:
            thread = await self._client.beta.threads.create()
            self.user_threads[user_id] = thread.id
        return self.user_threads[user_id]

    async def validate_value(self, value: str) -> bool:
        """Валидация ценности через Completions API с structured_output."""
        response = await self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": ("Ты валидатор ценностей. Проверь, является ли следующее утверждение осмысленной ценностью. "
                                "Ценность должна быть понятным словом или фразой, отражающей важный принцип или убеждение (например, 'семья', 'честность', "
                                "'свобода'). "
                                "Она не должна быть пустой, бессмысленным набором букв (например, 'sfgsdg', '123abc'), случайным звуком или несуществующим "
                                "словом. "
                                "Верни только JSON с boolean."
                                )
                },
                {
                    "role": "user",
                    "content": f"Проверь: '{value}'"
                }
            ],
            max_tokens=10,
            functions=[
                {
                    "name": "validate",
                    "description": "Returns a boolean indicating if the value is valid",
                    "parameters": {
                        "type": "object",
                        "properties": {"result": {"type": "boolean"}},
                        "required": ["result"]
                    }
                }
            ],
            function_call={"name": "validate"}
        )
        result = json.loads(response.choices[0].message.function_call.arguments)
        return result["result"]

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
