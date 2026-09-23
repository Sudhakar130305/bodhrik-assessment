from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        Enum("admin", "teacher", "parent", "student", name="user_role"),
        nullable=False,
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    parent: Mapped["User | None"] = relationship(
        "User",
        remote_side=[id],
        back_populates="children",
    )

    children: Mapped[list["User"]] = relationship(
        "User",
        back_populates="parent",
    )