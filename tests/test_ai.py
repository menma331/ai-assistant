# test_ai_bot.py
import base64
import hashlib
import io
import pytest
from unittest.mock import AsyncMock, Mock, patch
from ai_bot import AIBot
from openai.types.beta import Assistant


# Фикстура для создания экземпляра AIBot с замоканным клиентом
@pytest.fixture
def ai_bot():
    with patch('ai_bot.AsyncOpenAI') as MockClient:
        mock_client = MockClient.return_value
        bot = AIBot("fake_token")
        bot._client = mock_client  # Заменяем реальный клиент на мок
        yield bot


# Тест для voice_to_text
@pytest.mark.asyncio
async def test_voice_to_text(ai_bot):
    # Создаем фейковый голосовой файл
    voice_file = io.BufferedReader(io.BytesIO(b"fake audio data"))

    # Мокаем метод transcriptions.create
    ai_bot._client.audio.transcriptions.create = AsyncMock()
    ai_bot._client.audio.transcriptions.create.return_value.text = "Hello, world!"

    # Вызываем метод
    result = await ai_bot.voice_to_text(voice_file)

    # Проверяем результат
    assert result == "Hello, world!"
    ai_bot._client.audio.transcriptions.create.assert_called_once_with(
        model="whisper-1",
        file=voice_file
    )

# Тест для get_user_assistant (существующий ассистент)
@pytest.mark.asyncio
async def test_get_user_assistant_existing(ai_bot):
    user_id = "user123"
    mock_assistant = Mock(spec=Assistant)
    ai_bot.assistants[user_id] = mock_assistant

    # Вызываем метод
    assistant = await ai_bot.get_user_assistant(user_id)

    # Проверяем, что возвращается существующий ассистент и не создается новый
    assert assistant == mock_assistant
    ai_bot._client.beta.assistants.create.assert_not_called()


# Тест для get_answer_for_message (неуспешный случай)
@pytest.mark.asyncio
async def test_get_answer_for_message_failure(ai_bot):
    user_id = "user123"
    question_text = "What is the weather like?"

    # Мокаем ассистента
    mock_assistant = Mock(spec=Assistant)
    mock_assistant.id = "asst_123"
    ai_bot.assistants[user_id] = mock_assistant

    # Мокаем создание потока и запуск с ошибкой
    mock_thread = Mock(id="thread_123")
    ai_bot._client.beta.threads.create = AsyncMock(return_value=mock_thread)
    ai_bot._client.beta.threads.messages.create = AsyncMock()
    mock_run = Mock(status="failed")
    ai_bot._client.beta.threads.runs.create_and_poll = AsyncMock(return_value=mock_run)

    # Вызываем метод
    result = await ai_bot.get_answer_for_message(user_id, question_text)

    # Проверяем результат
    assert result is None


# Тест для text_to_voice
@pytest.mark.asyncio
async def test_text_to_voice(ai_bot):
    text = "Hello, world!"

    # Мокаем создание голосового файла
    ai_bot._client.audio.speech.create = AsyncMock(return_value=Mock(stream_to_file=Mock()))

    # Вызываем метод
    result = await ai_bot.text_to_voice(text)

    # Проверяем результат
    short_hash = base64.b32encode(hashlib.md5(text.encode()).digest())[:6].decode()
    expected_path = f'voice/upload/{short_hash}.mp3'
    assert result == expected_path
    ai_bot._client.audio.speech.create.assert_called_once_with(
        model="tts-1",
        voice="nova",
        input=text
    )