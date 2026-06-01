from sqlalchemy import String, Integer
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database import Base
from app.models.base import TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    phone_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    orders = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete"
    )