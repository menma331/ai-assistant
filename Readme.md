![ai_assistant_cover.jpg](doc/ai_assistant_cover.jpg)

# AI Assistant

## Описание проекта

AI Assistant — это голосовой Telegram-бот, построенный на базе библиотеки `aiogram` и асинхронного клиента OpenAI API. Бот принимает голосовые сообщения от пользователей, преобразует их в текст с помощью OpenAI Whisper, генерирует ответы через OpenAI Assistants API и возвращает их в виде голосовых сообщений, озвученных OpenAI TTS API. Дополнительно реализована функция идентификации и сохранения ключевых ценностей пользователя в базе данных PostgreSQL.

### Основные возможности
- Обработка голосовых сообщений пользователей.
- Конвертация речи в текст с использованием OpenAI Whisper.
- Генерация ответов через OpenAI Assistants API с поддержкой function calling.
- Озвучивание ответов с помощью OpenAI TTS (голос "Nova").
- Идентификация и сохранение ценностей пользователя в базе данных (например, "Я ценю честность" → сохранение "честность").
- Валидация ценностей через OpenAI Chat Completions API с использованием structured output.
- Поддержка асинхронного взаимодействия с базой данных через SQLAlchemy и Alembic.
- Поддержка контекста диалога.

---

## Требования

- **Python**: 3.10 или выше.
- **Библиотеки**:
  - `aiogram` — для работы с Telegram API.
  - `openai` — для взаимодействия с OpenAI API.
  - `pydantic-settings` — для управления настройками через `.env`.
  - `sqlalchemy[asyncio]` — для асинхронной работы с базой данных.
  - `asyncpg` — драйвер для PostgreSQL.
  - `alembic` — для миграций базы данных.
- **Токены и настройки**:
  - Telegram Bot API Token (получается через BotFather).
  - OpenAI API Key (получается в аккаунте OpenAI).
  - OpenAI Assistant ID (создаётся в OpenAI Playground или программно).
- **База данных**: PostgreSQL (локально или в облаке, например, на Railway).
- **Файл `.env`** с переменными:
  ```
  TELEGRAM_TOKEN=your_telegram_bot_token
  OPEN_AI_TOKEN=your_openai_api_key
  OPEN_AI_ASSISTANT_ID=your_assistant_id
  DB_CONNECTION_STRING=postgresql+asyncpg://user:password@host:port/dbname
  ```

---

## Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone git@github.com:menma331/ai-assistant.git
   cd ai-assistant
   ```

2. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Создайте файл `.env`** в корневой директории проекта:
      ```
      TELEGRAM_TOKEN=your_telegram_bot_token
      OPEN_AI_TOKEN=your_openai_api_key
      OPEN_AI_ASSISTANT_ID=your_assistant_id
      DB_CONNECTION_STRING=postgresql+asyncpg://user:password@host:port/dbname
      ```

4. **Настройте базу данных**:
   - Установите PostgreSQL локально или используйте облачный сервис.
   - Создайте базу данных:
     ```sql
     CREATE DATABASE ai_assistant_db;
     ```
   - Инициализируйте миграции с помощью Alembic:
     ```bash
     alembic init migrations
     ```
   - Настройте `alembic.ini` и `migrations/env.py` (укажите `sqlalchemy.url` и импортируйте модели).
   - Создайте миграцию:
     ```bash
     alembic revision --autogenerate -m "Create users table"
     ```
   - Примените миграцию:
     ```bash
     alembic upgrade head
     ```

5. **Запустите бота**:
   ```bash
   python bot.py
   ```

---

## Схема работы

![Схема работы AI Assistant](doc/ai_assistant_principle_of_work.png)

1. Пользователь отправляет голосовое сообщение в Telegram.
2. Бот загружает голосовой файл и преобразует его в текст с помощью OpenAI Whisper API.
3. Текст передаётся в OpenAI Assistants API:
   - Если текст содержит упоминание ценностей (например, "Я ценю порядок"), ассистент вызывает функцию `save_value`.
   - Ценность валидируется через OpenAI Chat Completions API (structured output).
   - При успешной валидации ценность сохраняется в PostgreSQL через SQLAlchemy.
4. Ассистент генерирует текстовый ответ (например, "Ценность 'порядок' сохранена").
5. Ответ преобразуется в голосовое сообщение через OpenAI TTS API.
6. Голосовой ответ отправляется пользователю в Telegram.

---

## Структура проекта

```
ai-assistant/
├── ai_bot.py         # Логика взаимодействия с OpenAI API
├── main.py           # Точка входа, запуск бота
├── handlers/         # Обработчики сообщений
│   └── ai.py         # Хэндлер для голосовых сообщений
│   └── start.py      # Обработка стартового сообщения 
├── models/           # Модели SQLAlchemy
│   └── user.py       # Модель UserModel
├── utils/            # Утилиты
│   ├── audio.py      # Загрузка голосовых сообщений
│   └── prompt.py     # Промпты для ассистента
├── core/             # Конфигурация
│   └── settings.py   # Настройки через pydantic-settings
│   └── db.py         # Базовые настройки БД
├── migrations/       # Миграции Alembic
├── doc/              # Документация
│   └── *.png         # Изображения для документации
├── requirements.txt  # Зависимости
└── .env              # Переменные окружения
```

---

## Использование

1. **Запустите бота**:
   ```bash
   python main.py
   ```

2. **Взаимодействие в Telegram**:
   - Отправьте `/start` для инициализации бота.
   - Задайте вопрос голосом, например: "Какой сегодня день?".
   - Упомяните ценность, например: "Я ценю честность".
   - Получите голосовой ответ от бота.

3. **Примеры**:
   - Вопрос: "Какой сегодня день?"
     - Ответ: "Сегодня 13 марта 2025 года."
   - Утверждение: "Я ценю порядок."
     - Ответ: "Ценность 'порядок' успешно сохранена."

---

## Деплой на Railway

1. **Зарегистрируйтесь на [Railway](https://railway.app/)**.
2. **Создайте новый проект** и подключите репозиторий GitHub.
3. **Добавьте сервисы**:
   - **PostgreSQL**: Добавьте базу данных и скопируйте `DATABASE_URL`.
   - **Бот**: Создайте сервис для приложения.
4. **Настройте переменные окружения**:
   - В разделе "Variables" добавьте:
       ```
      TELEGRAM_TOKEN=your_telegram_bot_token
      OPEN_AI_TOKEN=your_openai_api_key
      OPEN_AI_ASSISTANT_ID=your_assistant_id
      DB_CONNECTION_STRING=postgresql+asyncpg://user:password@host:port/dbname
      ```
5. **Запустите деплой**:
   - Railway автоматически соберёт и запустит проект после коммита изменений.

---

## Дополнительные настройки

Этот метод добавляет функцию `save_value` в `tools` ассистента и обновляет инструкции.

### Логирование
Для отладки включите логирование в `main.py`(по умолчанию включено):
```python
import logging
logging.basicConfig(level=logging.INFO)
```

---

## Ограничения и планы

- **Текущие ограничения**:
  - Нет поддержки контекста диалога (история сообщений не сохраняется между сессиями).
  - Ограниченная обработка ошибок API.
- **Планы**:
  - Добавить поддержку долгосрочного контекста через хранение истории в базе данных.
  - Расширить валидацию ценностей с использованием более сложных правил.
  - Оптимизировать производительность для обработки больших объёмов запросов.

---

## Контакты

Если у вас есть вопросы или предложения, свяжитесь с разработчиком:
- Telegram: [@azirafiele](https://t.me/azirafiele)
- GitHub: [menma331](https://github.com/menma331)

---