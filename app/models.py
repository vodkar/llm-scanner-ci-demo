"""ORM models: inventory items and user accounts."""

from enum import StrEnum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.query_utils import DEFAULT_SORT_FIELD


class Role(StrEnum):
    """Access level of a user."""

    USER = "user"
    ADMIN = "admin"


class Item(Base):
    """A stock-keeping unit in the warehouse."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    quantity: Mapped[int] = mapped_column(default=0)

    def to_dict(self) -> dict[str, object]:
        """Return the JSON representation of the item."""
        return {"id": self.id, "name": self.name, "quantity": self.quantity}


class User(Base):
    """An account authenticated by an API token."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)
    token_hash: Mapped[str] = mapped_column(unique=True)
    preferred_sort: Mapped[str] = mapped_column(default=DEFAULT_SORT_FIELD)
    """Item column the user's listings are ordered by."""

    @property
    def is_admin(self) -> bool:
        """Whether the user may perform administrative actions."""
        return self.role is Role.ADMIN
