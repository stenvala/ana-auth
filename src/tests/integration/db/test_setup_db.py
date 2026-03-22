"""Integration tests for setup_db.py schema management.

Tests the complete database setup lifecycle against local Docker PostgreSQL:
create schema, verify tables and admin user, test idempotency, apply migrations,
and drop schema.
"""

import subprocess
import uuid
from pathlib import Path

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

pytestmark = pytest.mark.integration

PROJECT_NAME = "ana-auth"
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _connect() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(
        host="localhost", port=5432, database="postgres", user="postgres", password="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def _schema_exists(conn: psycopg2.extensions.connection, schema_name: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s;",
        (schema_name,),
    )
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def _table_exists(
    conn: psycopg2.extensions.connection, schema_name: str, table_name: str
) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s;",
        (schema_name, table_name),
    )
    result = cursor.fetchone()
    cursor.close()
    return result is not None


@pytest.fixture()
def test_suffix() -> str:
    return f"test-{uuid.uuid4().hex[:8]}"


@pytest.fixture()
def schema_name(test_suffix: str) -> str:
    return f"{PROJECT_NAME}-{test_suffix}"


@pytest.fixture(autouse=True)
def cleanup_schema(schema_name: str):
    """Ensure test schema is cleaned up after each test."""
    yield
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')
        cursor.close()
    finally:
        conn.close()


def _run_setup_db(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["uv", "run", "python", "setup_db.py", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"setup_db.py {' '.join(args)} failed:\n{result.stderr}\n{result.stdout}")
    return result


def _run_create(suffix: str) -> None:
    _run_setup_db("create", suffix)


def _run_drop(suffix: str) -> None:
    _run_setup_db("drop", suffix, "--confirm")


def _run_update(suffix: str) -> None:
    _run_setup_db("update", suffix)


def test_create_schema_creates_tables(test_suffix: str, schema_name: str) -> None:
    """Creating a schema should create all expected tables."""
    _run_create(test_suffix)

    conn = _connect()
    try:
        assert _schema_exists(conn, schema_name)
        assert _table_exists(conn, schema_name, "user_account")
        assert _table_exists(conn, schema_name, "user_email")
        assert _table_exists(conn, schema_name, "_deployment_log")
    finally:
        conn.close()


def test_create_schema_seeds_admin_user(test_suffix: str, schema_name: str) -> None:
    """Creating a schema should seed the master admin user with primary email."""
    _run_create(test_suffix)

    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(f'SET search_path = "{schema_name}";')

        cursor.execute("SELECT id, user_name FROM user_account WHERE user_name = 'stenvala';")
        admin = cursor.fetchone()
        assert admin is not None, "Admin user 'stenvala' should exist"

        admin_id = admin[0]
        cursor.execute(
            "SELECT email, is_primary, is_verified FROM user_email WHERE user_account_id = %s;",
            (admin_id,),
        )
        email_row = cursor.fetchone()
        assert email_row is not None, "Admin should have an email"
        assert email_row[1] is True, "Admin email should be primary"
        assert email_row[2] is True, "Admin email should be verified"

        cursor.close()
    finally:
        conn.close()


def test_create_schema_is_idempotent(test_suffix: str, schema_name: str) -> None:
    """Running create twice should not fail or duplicate the admin user."""
    _run_create(test_suffix)
    _run_create(test_suffix)

    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(f'SET search_path = "{schema_name}";')

        cursor.execute("SELECT COUNT(*) FROM user_account WHERE user_name = 'stenvala';")
        count = cursor.fetchone()[0]
        assert count == 1, "Admin user should not be duplicated"

        cursor.close()
    finally:
        conn.close()


def test_drop_schema_removes_schema(test_suffix: str, schema_name: str) -> None:
    """Dropping a schema should remove it entirely."""
    _run_create(test_suffix)
    _run_drop(test_suffix)

    conn = _connect()
    try:
        assert not _schema_exists(conn, schema_name)
    finally:
        conn.close()


def test_update_on_current_schema_applies_no_changes(
    test_suffix: str, schema_name: str
) -> None:
    """Running update on an already up-to-date schema should apply no new migrations."""
    _run_create(test_suffix)
    _run_update(test_suffix)

    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(f'SET search_path = "{schema_name}";')

        cursor.execute("SELECT COUNT(*) FROM _deployment_log;")
        count = cursor.fetchone()[0]
        assert count == 1, "Should have exactly one migration (001_initial.sql)"

        cursor.close()
    finally:
        conn.close()
