import os

import aiofiles
import aiohttp

from core.settings import settings


async def save_file(file_path: str, content: bytes):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)


async def download_voice_message(file_id: str, file_path: str, user_id: int) -> str:
    # Формируем URL для скачивания
    download_url = f"https://api.telegram.org/file/bot{settings.tg_bot_token}/{file_path}"

    # Скачиваем файл
    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            if response.ok:
                file_content = await response.read()

                # Сохраняем файл локально
                save_path = f"voice/downloads/{user_id}_{file_id}.mp3"
                await save_file(save_path, file_content)

                return save_path
            else:
                raise FileNotFoundError("File not found")
