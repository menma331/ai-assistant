from core.db import BaseModel
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Boolean


class UserModel(BaseModel):
    """Модель пользователя."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(type_=Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(type_=Integer)
    value: Mapped[str] = mapped_column(type_=String, nullable=True)
