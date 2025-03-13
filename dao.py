from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import session
from models.user import UserModel


class UserDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_user_value(self, user_tg_id: int, value: str):
        """Сохраняет или обновляет ценность пользователя в БД."""
        async with self._session() as sess:
            result = await sess.execute(select(UserModel).where(UserModel.tg_id == user_tg_id))
            user = result.scalars().first()

            if not user:
                user = UserModel(tg_id=user_tg_id, value=value)
                sess.add(user)
            else:
                user.value = value

            await sess.commit()


user_dao = UserDAO(session)
