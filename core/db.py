from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from core.settings import settings

engine: AsyncEngine = create_async_engine(settings.database_connection_string, echo=True)
session = async_sessionmaker(engine, class_=AsyncSession)

class BaseModel(DeclarativeBase):
    __abstract__ = True
