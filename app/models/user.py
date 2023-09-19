from datetime import datetime
from typing import Optional, Self
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Table, Column

from app.db import get_session
from app.models.base import Base
from app.utils import verify_password

users_to_groups = Table(
    "users_to_groups",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("group_id", ForeignKey("groups.id")),
)


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str | None] = mapped_column(unique=True)
    display_name: Mapped[str | None] = mapped_column()
    password: Mapped[str] = mapped_column()
    profile_image_url: Mapped[str | None] = mapped_column()
    groups: Mapped[list["Group"]] = relationship(
        secondary=users_to_groups, back_populates="members", viewonly=True
    )

    async def save(self) -> Self:
        async with get_session() as db:
            db.add(self)
            await db.commit()
            await db.refresh(self)
        return self

    @classmethod
    async def authenticate(cls, email: str, password: str) -> Optional["User"]:
        query = select(User).where(User.email == email)
        async with get_session() as db:
            user = (await db.execute(query)).scalar_one_or_none()
        is_correct_password = False
        if user:
            is_correct_password = verify_password(password, user.password)
        if is_correct_password:
            return user

    @classmethod
    async def get_by_id(cls, id: UUID) -> Optional["User"]:
        query = select(User).where(User.id == id)
        user = None
        async with get_session() as db:
            user = (await db.execute(query)).scalar_one_or_none()
        return user

    @classmethod
    async def new(cls, email: EmailStr, password: str, **kwargs) -> "User":
        new_user = cls(id=uuid4(), email=email, password=password, **kwargs)
        async with get_session() as db:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
        return new_user


# Group is the same as My People from the figma file
class Group(Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column()
    cover_image_url: Mapped[str | None] = mapped_column()
    members: Mapped[list[User]] = relationship(
        secondary=users_to_groups, back_populates="groups"
    )
    events: Mapped[list["Event"]] = relationship(back_populates="group")


class Event(Base):
    __tablename__ = "events"
    title: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    start: Mapped[datetime] = mapped_column()
    end: Mapped[datetime] = mapped_column()
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"))
    group: Mapped[Group] = relationship(back_populates="events")
    cover_image_url: Mapped[str | None] = mapped_column()
