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

    async def save_value(self, user_id: int, value: str) -> bool:
        """Сохранение ценности в БД после валидации."""
        if not value.strip():
            return False
        is_valid = await self.validate_value(value)
        if is_valid:
            await user_dao.save_user_value(user_tg_id=user_id, value=value)
            return True
        return False

    async def get_answer_for_message(self, user_id: int, question_text: str) -> Optional[str]:
        thread_id = await self.get_user_thread(user_id=user_id)
        await self._client.beta.threads.messages.create(
            thread_id=thread_id,
            content=question_text,
            role="user"
        )

        run = await self._client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

        if run.status == "completed":
            messages = await self._client.beta.threads.messages.list(thread_id=thread_id)
            for message in reversed(messages.data):
                if message.role == "assistant":
                    return message.content[0].text.value
        elif run.status == "requires_action":
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.function.name == "save_value":
                    value = json.loads(tool_call.function.arguments)["value"]
                    print(f"Для пользователя {user_id} определена ценность: {value}")
                    success = await self.save_value(user_id, value)
                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"success": success})
                        }
                    )
            await self._client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            messages = await self._client.beta.threads.messages.list(thread_id=thread_id)
            for message in reversed(messages.data):
                if message.role == "assistant":
                    return message.content[0].text.value

        return "Спасибо ! Ваше сообщение обработано"

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


    # Функция для определения настроения через OpenAI Vision
    async def detect_mood_from_image(self, base64_image):
        """Определение эмоций пользователя."""
        response = await self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the emotion on the person's face in this image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=50
        )

        mood_description = response.choices[0].message.content
        print(mood_description)
        return mood_description

ai_bot = AIBot(settings.open_ai_token, settings.open_ai_assistant_id)
