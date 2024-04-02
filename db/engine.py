from typing import Any

from sqlalchemy import Insert, Select, Update
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatabaseEngine:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, db_url: str, debug: bool = False) -> None:
        self._engine = create_async_engine(db_url, echo=debug)
        self._session = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=self._engine,
            class_=AsyncSession,
        )

    async def get_one(self, stmt: Select[Any]) -> Any:
        async with self._session() as session:
            return await session.scalar(stmt)

    async def save(self, stmt: Insert | Update) -> Any:
        async with self._session() as session:
            result = await session.scalar(stmt)
            await session.commit()
        return result
