#!/usr/bin/env python3
"""
Database deployment script for PostgreSQL deployments.
Handles schema deployment with network restrictions and SSH tunneling.
Only used in PostgreSQL mode (single-domain deployments).
"""

import hashlib
import ipaddress
import socket
import subprocess
import time
from pathlib import Path

import psycopg2

from config_loader import Config, load_config


def check_local_network(local_network_cidr: str) -> bool:
    """Check if we're running from the local network."""
    hostname = socket.gethostname()
    local_ips = socket.gethostbyname_ex(hostname)[2]
    network = ipaddress.IPv4Network(local_network_cidr, strict=False)
    return any(ipaddress.IPv4Address(ip) in network for ip in local_ips)


def create_ssh_tunnel(
    remote_host: str,
    remote_user: str,
    db_host: str,
    db_port: int,
    local_port: int = 15432,
) -> subprocess.Popen:
    """Create SSH tunnel to database server."""
    print(
        f"Creating SSH tunnel: localhost:{local_port} -> {db_host}:{db_port} via {remote_user}@{remote_host}"
    )

    tunnel_cmd = [
        "ssh",
        "-N",
        "-L",
        f"{local_port}:{db_host}:{db_port}",
        f"{remote_user}@{remote_host}",
    ]
    tunnel_process = subprocess.Popen(tunnel_cmd)

    print("Waiting for SSH tunnel to establish...")
    time.sleep(3)

    # Test tunnel connectivity
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(5)
    result = test_socket.connect_ex(("localhost", local_port))
    test_socket.close()

    if result == 0:
        print(f"SSH tunnel established successfully on port {local_port}")
        return tunnel_process
    else:
        tunnel_process.terminate()
        raise ConnectionError(f"SSH tunnel failed to establish on port {local_port}")


def get_database_connection(
    config: Config, db_host: str, db_port: int, db_user: str, db_password: str, db_name: str
):
    """Get database connection."""
    print(f"Connecting to database: {db_host}:{db_port}")

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
    )
    conn.autocommit = True
    return conn


def get_schema_name(config: Config, schema_suffix: str = "main") -> str:
    """Generate schema name from configuration."""
    service_name = config.service_name.replace(".service", "")
    return f"{service_name}-{schema_suffix}"


def get_schema_checksum(schema_file: Path) -> str:
    """Calculate SHA-256 checksum of schema file."""
    with open(schema_file, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def _parse_sql_statements(sql: str) -> list[str]:
    """Parse SQL statements, respecting dollar-quoted strings like $$ ... $$"""
    statements: list[str] = []
    current_stmt = ""
    i = 0

    while i < len(sql):
        # Check for dollar quote start (e.g., $$, $tag$, etc.)
        if sql[i] == "$":
            # Find the end of the dollar quote marker
            j = i + 1
            while j < len(sql) and (sql[j].isalnum() or sql[j] == "_"):
                j += 1
            if j < len(sql) and sql[j] == "$":
                # Found a complete dollar quote marker
                quote_marker = sql[i : j + 1]
                current_stmt += quote_marker
                i = j + 1

                # Find the closing dollar quote
                while i < len(sql):
                    if sql[i : i + len(quote_marker)] == quote_marker:
                        current_stmt += quote_marker
                        i += len(quote_marker)
                        break
                    current_stmt += sql[i]
                    i += 1
            else:
                current_stmt += sql[i]
                i += 1
        elif sql[i] == ";":
            # End of statement (outside dollar quotes)
            stmt = current_stmt.strip()
            if stmt:
                statements.append(stmt)
            current_stmt = ""
            i += 1
        else:
            current_stmt += sql[i]
            i += 1

    # Add any remaining statement
    stmt = current_stmt.strip()
    if stmt:
        statements.append(stmt)

    return statements


def ensure_system_admin_user(cursor) -> None:
    """Ensure system admin user exists in the database."""
    admin_sql_file = Path(__file__).parent / "ensure_system_admin.sql"
    if admin_sql_file.exists():
        print("Ensuring system admin user exists...")
        with open(admin_sql_file, "r") as f:
            admin_sql = f.read()
        cursor.execute(admin_sql)
        print("System admin user ensured")
    else:
        print(
            "Warning: ensure_system_admin.sql not found - skipping admin user creation"
        )


def deploy_schema(
    config: Config,
    db_host: str,
    db_port: int,
    db_user: str,
    db_password: str,
    db_name: str,
    schema_suffix: str = "main",
) -> None:
    """Deploy database schema from SQL file to the correct schema."""
    schema_name = get_schema_name(config, schema_suffix)

    # Read and checksum schema file
    schema_file = Path(__file__).parent.parent / "dist" / "db" / "create_schema.sql"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    with open(schema_file, "r") as f:
        schema_sql = f.read()

    schema_version = get_schema_checksum(schema_file)
    print(f"Schema version (checksum): {schema_version}")
    print(f"Target schema: {schema_name}")
    print(f"Schema file size: {len(schema_sql)} bytes")

    # Connect and deploy
    conn = get_database_connection(config, db_host, db_port, db_user, db_password, db_name)

    with conn.cursor() as cur:
        # Create schema if it doesn't exist
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)",
            (schema_name,),
        )
        if not cur.fetchone()[0]:
            print(f"Creating schema: {schema_name}")
            cur.execute(f'CREATE SCHEMA "{schema_name}"')
        else:
            print(f"Schema {schema_name} already exists")

        # Set search path to target schema
        cur.execute(f'SET search_path = "{schema_name}"')

        # Create deployment log table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS _deployment_log (
                id SERIAL PRIMARY KEY,
                deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                schema_version TEXT,
                notes TEXT
            )
        """
        )

        # Check if already deployed
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM _deployment_log WHERE schema_version = %s)",
            (schema_version,),
        )
        if cur.fetchone()[0]:
            print(
                f"Schema version {schema_version} already deployed to {schema_name} - skipping schema deployment"
            )
        else:
            # Deploy schema
            print(f"Applying new schema to schema: {schema_name}")
            print("Parsing schema SQL into individual statements...")

            # Parse statements respecting dollar-quoted strings (e.g., $$ ... $$)
            statements = _parse_sql_statements(schema_sql)
            print(f"Found {len(statements)} SQL statements to execute")

            for idx, statement in enumerate(statements, 1):
                try:
                    print(
                        f"  [{idx}/{len(statements)}] Executing statement ({len(statement)} chars)..."
                    )
                    # Show first 80 chars of statement for debugging
                    preview = statement[:80].replace("\n", " ").replace("  ", " ")
                    print(f"    Preview: {preview}...")
                    cur.execute(statement)
                except Exception as e:
                    print(f"  ERROR in statement {idx}:")
                    print(f"    Statement preview: {preview}...")
                    print(f"    Full error: {e}")
                    raise

            print(f"Schema applied successfully to {schema_name}")

            # Log deployment
            cur.execute(
                "INSERT INTO _deployment_log (schema_version, notes) VALUES (%s, %s)",
                (
                    schema_version,
                    f"Schema deployment via deploy_database.py to {schema_name}",
                ),
            )
            print(f"Deployment logged successfully with version {schema_version}")

        # Always ensure system admin user exists (even if schema wasn't updated)
        ensure_system_admin_user(cur)

    conn.close()


def list_project_schema(
    config: Config,
    db_host: str,
    db_port: int,
    db_user: str,
    db_password: str,
    db_name: str,
    schema_suffix: str = "main",
) -> None:
    """List the project schema and tables."""
    schema_name = get_schema_name(config, schema_suffix)
    conn = get_database_connection(config, db_host, db_port, db_user, db_password, db_name)

    with conn.cursor() as cur:
        # Check if schema exists and list tables
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)",
            (schema_name,),
        )
        if not cur.fetchone()[0]:
            print(f"Schema {schema_name} does not exist")
            return

        print(f"\n=== PROJECT SCHEMA: {schema_name} ===")
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """,
            (schema_name,),
        )

        tables = cur.fetchall()
        if tables:
            print(f"Tables in {schema_name}:")
            for (table,) in tables:
                # Get row count for each table
                cur.execute(f'SELECT COUNT(*) FROM "{schema_name}"."{table}"')
                count = cur.fetchone()[0]
                print(f"  {table} ({count} rows)")
        else:
            print(f"No tables found in {schema_name}")

        # Show deployment log
        print(f"\n=== DEPLOYMENT LOG ({schema_name}) ===")
        cur.execute(f'SET search_path = "{schema_name}"')
        cur.execute(
            "SELECT deployed_at, schema_version, notes FROM _deployment_log ORDER BY deployed_at DESC LIMIT 10"
        )
        logs = cur.fetchall()

        for deployed_at, version, notes in logs:
            print(f"{deployed_at}: {version} - {notes}")

    conn.close()


def main() -> None:
    """Main database deployment function."""
    config = load_config()

    # Check if this is SQLite mode (multi-domain)
    if config.domains:
        print("SQLite mode detected - database operations handled by deploy_api.py")
        print("Use deploy_api.py for SQLite schema and migration deployments")
        return

    print("Error: PostgreSQL mode requires DB_HOST configuration")
    print("This script is for PostgreSQL deployments only")


if __name__ == "__main__":
    main()
