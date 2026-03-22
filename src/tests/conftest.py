"""Root test conftest -- schema fixtures and shared constants."""

import subprocess
import uuid
from pathlib import Path
from typing import Generator

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlmodel import Session

from shared.db.db_context import DBContext

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TEST_PASSWORD = "TestPassword123!"
TEST_PASSWORD_HASH = "$2b$12$9/Q1gX12QfY.e5p1mdBmjeXA0JNVNGFy9GzscTN5MF7Y1kODSoP2a"


@pytest.fixture(scope="session")
def test_schema_suffix() -> Generator[str, None, None]:
    """Create an isolated test schema and tear it down after the session."""
    suffix = f"test-{uuid.uuid4().hex[:8]}"

    subprocess.run(
        ["uv", "run", "python", "setup_db.py", "create", suffix],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    yield suffix

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f'DROP SCHEMA IF EXISTS "ana-auth-{suffix}" CASCADE;')
    cursor.close()
    conn.close()

    DBContext.dispose_all()


@pytest.fixture()
def db_session(test_schema_suffix: str) -> Generator[Session, None, None]:
    """Provide a database session connected to the test schema."""
    db = DBContext(schema_suffix=test_schema_suffix)
    with db.get_session() as session:
        yield session
