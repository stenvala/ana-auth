"""E2E test conftest -- Playwright fixtures with schema isolation."""

import subprocess
import uuid
from pathlib import Path
from typing import Generator

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlmodel import Session

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
BASE_URL = "http://localhost:4200"


@pytest.fixture(scope="session")
def e2e_schema_suffix() -> Generator[str, None, None]:
    """Create an isolated E2E test schema and tear it down after the session."""
    suffix = f"e2e-{uuid.uuid4().hex[:8]}"

    subprocess.run(
        ["uv", "run", "python", "setup_db.py", "create", suffix],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    yield suffix

    conn = psycopg2.connect(
        host="localhost", port=5432, database="postgres", user="postgres", password="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f'DROP SCHEMA IF EXISTS "ana-auth-{suffix}" CASCADE;')
    cursor.close()
    conn.close()


@pytest.fixture(scope="session")
def e2e_base_url() -> str:
    """Base URL for the running Angular dev server."""
    return BASE_URL


@pytest.fixture(scope="function")
def e2e_db_session(e2e_schema_suffix: str) -> Generator[Session, None, None]:
    """Database session for E2E test data setup."""
    schema_name = f"ana-auth-{e2e_schema_suffix}"
    test_engine = create_engine(
        f"{DATABASE_URL}?options=-csearch_path%3D{schema_name}"
    )
    try:
        with Session(test_engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
    finally:
        test_engine.dispose()
