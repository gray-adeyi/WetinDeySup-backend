import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL")

database_engine = AsyncEngine(create_engine(DATABASE_URL))


async def initialize_database():
    """Creates all the tables in the database."""
    async with database_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Provides a database session"""
    async_session = sessionmaker(
        database_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session()
