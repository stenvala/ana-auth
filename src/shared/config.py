"""Environment configuration."""

import os


class Config:
    """Application configuration from environment variables."""

    SCHEMA_SUFFIX: str = os.environ.get("SCHEMA_SUFFIX", "main")
    DB_HOST: str = os.environ.get("DB_HOST", "localhost")
    DB_PORT: int = int(os.environ.get("DB_PORT", "5432"))
    DB_USER: str = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "postgres")
    DB_NAME: str = os.environ.get("DB_NAME", "postgres")
    ENV_TYPE: str = os.environ.get("ENV_TYPE", "LOCAL")
    LOG_ROOT: str = os.environ.get("LOG_ROOT", "logs")
    STAGE: str = os.environ.get("STAGE", "local")
    API_PORT: int = int(os.environ.get("API_PORT", "6784"))

    @classmethod
    def get_schema_name(cls, suffix: str | None = None) -> str:
        """Get full schema name for the given suffix."""
        return f"ana-auth-{suffix or cls.SCHEMA_SUFFIX}"

    @classmethod
    def get_database_url(cls) -> str:
        """Get base PostgreSQL connection URL (without schema)."""
        return (
            f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
