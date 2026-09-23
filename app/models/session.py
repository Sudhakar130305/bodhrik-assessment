from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LearningSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    child_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    teacher = relationship(
        "User",
        foreign_keys=[teacher_id],
    )

    child = relationship(
        "User",
        foreign_keys=[child_id],
    )

    evaluations = relationship(
        "Evaluation",
        back_populates="session",
        cascade="all, delete-orphan",
    )