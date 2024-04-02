from uuid import UUID

from sqlalchemy import Uuid, JSON
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from core.dto import Status
from db.engine import Base
from db.mixins import CreatedAtMixin, UpdatedAtMixin


class Task(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    points: Mapped[list[dict]] = mapped_column(type_=JSON, nullable=True)
    status: Mapped[Status] = mapped_column(
        ENUM(
            Status,
            values_callable=lambda x: [e.value for e in Status],
        ),
    )
