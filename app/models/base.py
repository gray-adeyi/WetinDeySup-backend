import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    # TODO: default_factory=uuid.uuid4 is raising errors
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, type_=Uuid)
