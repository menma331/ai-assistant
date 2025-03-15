import io
import json
import base64
import hashlib
from openai import AsyncOpenAI
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dao import user_dao
from core.settings import settings
from utils.prompt import default_prompt_for_ai


class UserState(StatesGroup):
    """Хранение thread_id"""
    thread = State()

class AIBot:
    def __init__(self, token: str, assistant_id: str):
        self.__token = token
        self._client = AsyncOpenAI(api_key=self.__token)
        self.assistant_id = assistant_id

    async def voice_to_text(self, voice_file: io.BufferedReader) -> str:
        """Конвертация голосового сообщения в текст."""
        transcription = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=voice_file
        )
        return transcription.text

    async def get_user_thread(self, user_id: int, state: FSMContext) -> str:
        """Получение или создание thread_id, хранимого в состоянии FSM."""
        data = await state.get_data()
        thread_id = data.get("thread_id")
        if not thread_id:
            thread = await self._client.beta.threads.create()
            thread_id = thread.id
            await state.update_data(thread_id=thread_id)
        return thread_id

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

    async def get_answer_for_message(self, user_id: int, question_text: str, state: FSMContext) -> str:
        thread_id = await self.get_user_thread(user_id=user_id, state=state)
        await self._client.beta.threads.messages.create(
            thread_id=thread_id,
            content=question_text,
            role="user"
        )

        run = await self._client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            instructions=default_prompt_for_ai + 'Если вопрос о тревожности, ответь информацией из документа.'
        )

        if run.status == "completed":
            messages = await self._client.beta.threads.messages.list(thread_id=thread_id)
            answer = messages.data[0].content[0].text.value

            file_sources = set()
            # try:
            #     source = messages.data[0].content[0]
            answer_annotations = messages.data[0].content[0].text.annotations
            for annotation in answer_annotations: # Получаем все использованные источники в последнем ответе
                if annotation.type == "file_citation":
                    file_sources.add(annotation.file_citation.file_id)

            if file_sources:
                file_names = []
                for file_id in file_sources:
                    try:
                        file_info = await self._client.files.retrieve(file_id)
                        file_names.append(file_info.filename)
                    except Exception as e:
                        print(f"Ошибка получения имени файла: {e}")

                if file_names:
                    answer += f"\nИсточник: {', '.join(file_names)}"
            return answer

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
            answer = messages.data[0].content[0].text.value
            if hasattr(run, "file_ids") and run.file_ids:
                try:
                    file_info = await self._client.files.retrieve(run.file_ids[0])
                    file_name = file_info.filename
                    answer += f"\n(Источник: {file_name})"
                except Exception as e:
                    print(f"Ошибка получения имени файла: {e}")
            return answer

        return "Необходимые действия были выполнены. У вас есть какой-то вопрос?"

    async def text_to_voice(self, text: str) -> str:
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

    async def detect_mood_from_image(self, base64_image: str) -> str:
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