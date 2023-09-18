from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Table, Column

from app.models.base import Base

users_to_groups = Table(
    "users_to_groups",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("group_id", ForeignKey("groups.id")),
)


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    display_name: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    profile_image_url: Mapped[str | None] = mapped_column()
    groups: Mapped[list["Group"]] = relationship(secondary=users_to_groups)


# Group is the same as My People from the figma file
class Group(Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column()
    cover_image_url: Mapped[str | None] = mapped_column()
    members: Mapped[list[User]] = relationship(secondary=users_to_groups)
    events: Mapped[list["Event"]] = relationship(back_populates="group")


class Event(Base):
    __tablename__ = "events"
    title: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    start: Mapped[datetime] = mapped_column()
    end: Mapped[datetime] = mapped_column()
    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id"))
    group: Mapped[Group] = relationship()
    cover_image_url: Mapped[str | None] = mapped_column()
