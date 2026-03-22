"""Database context manager with schema-based multitenancy."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from shared.config import Config


class DBContext:
    """Database context manager for PostgreSQL with schema-based multitenancy.

    Uses PostgreSQL search_path to route queries to the correct schema.
    Engine is cached per schema suffix for connection pooling.
    """

    _engines: dict[str, Engine] = {}

    def __init__(self, schema_suffix: str | None = None) -> None:
        self.schema_suffix = schema_suffix or Config.SCHEMA_SUFFIX

    def _get_engine(self) -> Engine:
        """Get or create database engine for the configured schema."""
        if self.schema_suffix not in DBContext._engines:
            schema_name = Config.get_schema_name(self.schema_suffix)
            base_url = Config.get_database_url()
            url = f"{base_url}?options=-c%20search_path%3D{schema_name}"

            DBContext._engines[self.schema_suffix] = create_engine(
                url,
                echo=False,
                pool_size=50,
                max_overflow=30,
                pool_recycle=3600,
                pool_pre_ping=True,
            )

        return DBContext._engines[self.schema_suffix]

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic commit/rollback."""
        engine = self._get_engine()
        with Session(engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    @classmethod
    def dispose_all(cls) -> None:
        """Dispose all cached engines."""
        for engine in cls._engines.values():
            engine.dispose()
        cls._engines.clear()
