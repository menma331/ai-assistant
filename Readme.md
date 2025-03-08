![ai_assistant_cover.jpg](doc/ai_assistant_cover.jpg)
# AI Assistant

## Описание проекта

AI Assistant — голосовой Telegram-бот на базе Aiogram и асинхронного клиента OpenAI API. Принимает голосовые сообщения, преобразует их в текст, генерирует ответы на вопросы через OpenAI Assistants API и озвучивает их с помощью OpenAI TTS API.

### Основные возможности
- Обработка голосовых сообщений.
- Конвертация речи в текст через OpenAI Whisper.
- Генерация ответов с помощью Assistants API.
- Озвучивание ответов через OpenAI TTS.
- Поддержка контекста диалога(планируется).

---

## Требования
- Python 3.10+
- Библиотеки: `aiogram`, `openai`, `pydantic-settings`
- Токены: 
  - Telegram Bot API Token
  - OpenAI API Key
- Файл `.env` с переменными `TELEGRAM_TOKEN` и `OPENAI_API_KEY`

---

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:menma331/ai-assistant.git
   cd ai-assistant
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Создайте файл `.env`:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Запустите бота:
   ```bash
   python bot.py
   ```

---

## Схема работы

![Схема работы AI Assistant](doc/ai_assistant_principle_of_work.png)

1. Пользователь отправляет голосовое сообщение.
2. Голос преобразуется в текст через OpenAI Whisper API.
3. Текст отправляется в Assistants API для генерации ответа.
4. Ответ озвучивается через OpenAI TTS API.
5. Голосовое сообщение отправляется пользователю.

---

## Структура проекта

- `bot.py` — логика бота.
- `config.py` — конфигурация через PydanticSettings.
- `doc/` — документация и схема (`ai_assistant_principle_of_work.png`).
- `.env` — файл с токенами.
- `.gitignore` — исключение `.env`.

---

## Использование

1. Запустите бота.
2. Отправьте `/start` в Telegram.
3. Задайте вопрос голосом.
4. Получите голосовой ответ.

---

## Деплой на Railway

1. Зарегистрируйтесь на [Railway](https://railway.app/).
2. Подключите репозиторий.
3. Добавьте переменные `TELEGRAM_TOKEN` и `OPENAI_API_KEY`.
4. Запустите деплой.

---