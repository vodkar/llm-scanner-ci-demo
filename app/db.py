"""SQLAlchemy engine, session factory and declarative base."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH: Final[Path] = Path(__file__).with_name("inventory.db")

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base of the ORM models."""


@contextmanager
def session_scope() -> Iterator[Session]:
    """Open a session that commits on success and rolls back on error."""
    with SessionLocal.begin() as session:
        yield session


def init_db() -> None:
    """Create missing tables."""
    Base.metadata.create_all(engine)
