from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Information(Base):
    __tablename__ = "information"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Compatibilité avec l'ancienne version
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="INFORMATIONS",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    # Informations détaillées
    presentation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    opening_hours: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    payment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    pickup: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    contact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    additional: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
