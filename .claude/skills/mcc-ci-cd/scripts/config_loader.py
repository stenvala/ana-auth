"""Configuration loader for MCC deployment scripts."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import yaml


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""


@dataclass
class Config:
    """Deployment configuration container."""

    # Server
    remote_user: str
    remote_host: str
    remote_base: str
    dir_user: str
    dir_group: str

    # Build paths
    local_api_dir: Path
    local_ui_dir: Path

    # Remote paths (resolved from templates)
    api_remote_builds: str
    api_symlink: str
    ui_remote_builds: str
    ui_symlink: str

    # Deployment
    keep_builds: int
    service_name: str
    email: str
    api_port: int

    # Domains (multi-domain SQLite)
    domains: list[str] = field(default_factory=list)

    # Backup
    backup_enabled: bool = True
    backup_retention_daily: int = 7
    backup_retention_weekly: int = 4
    backup_path: str | None = None

    def iter_domains(self) -> Iterator[str]:
        """Iterate over configured domains."""
        yield from self.domains

    def get_domain_db_path(self, domain: str) -> str:
        """Get SQLite database path for a domain."""
        return f"{self.remote_base}/domains/{domain}/data.db"

    def get_domains_dir(self) -> str:
        """Get domains directory path."""
        return f"{self.remote_base}/domains"


def _resolve_templates(value: str, remote_base: str) -> str:
    """Replace {{REMOTE_BASE}} with actual value."""
    return value.replace("{{REMOTE_BASE}}", remote_base)


def load_config(config_path: Path | None = None) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to conf.yml (default: mcc/conf.yml)

    Returns:
        Validated Config object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ConfigurationError: If configuration is invalid
    """
    if config_path is None:
        config_path = Path(__file__).parent / "conf.yml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Copy conf.yml.template to conf.yml and customize it."
        )

    with open(config_path) as f:
        data = yaml.safe_load(f)

    # Validate required fields
    required = ["REMOTE_USER", "REMOTE_HOST", "REMOTE_BASE", "DIR_USER", "DIR_GROUP"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        raise ConfigurationError(f"Missing required configuration: {', '.join(missing)}")

    # Validate domains
    if not data.get("DOMAINS"):
        raise ConfigurationError("DOMAINS must be configured with at least one domain")

    remote_base = data["REMOTE_BASE"]

    # Build config object
    config = Config(
        # Server
        remote_user=data["REMOTE_USER"],
        remote_host=data["REMOTE_HOST"],
        remote_base=remote_base,
        dir_user=data["DIR_USER"],
        dir_group=data["DIR_GROUP"],
        # Build paths
        local_api_dir=Path(data.get("LOCAL_API_DIR", "../dist/api")),
        local_ui_dir=Path(data.get("LOCAL_UI_DIR", "../dist/ui")),
        # Remote paths
        api_remote_builds=_resolve_templates(
            data.get("API_REMOTE_BUILDS", "{{REMOTE_BASE}}/api"), remote_base
        ),
        api_symlink=_resolve_templates(
            data.get("API_SYMLINK", "{{REMOTE_BASE}}/current-api"), remote_base
        ),
        ui_remote_builds=_resolve_templates(
            data.get("UI_REMOTE_BUILDS", "{{REMOTE_BASE}}/ui"), remote_base
        ),
        ui_symlink=_resolve_templates(
            data.get("UI_SYMLINK", "{{REMOTE_BASE}}/current-ui"), remote_base
        ),
        # Deployment
        keep_builds=data.get("KEEP_BUILDS", 10),
        service_name=data.get("SERVICE_NAME", "accounts.service"),
        email=data.get("EMAIL", ""),
        api_port=data.get("API_PORT", 7325),
        # Domains
        domains=data.get("DOMAINS", []),
        # Backup
        backup_enabled=data.get("BACKUP_ENABLED", True),
        backup_retention_daily=data.get("BACKUP_RETENTION_DAILY", 7),
        backup_retention_weekly=data.get("BACKUP_RETENTION_WEEKLY", 4),
        backup_path=_resolve_templates(
            data.get("BACKUP_PATH", "{{REMOTE_BASE}}/backups"), remote_base
        )
        if data.get("BACKUP_PATH")
        else f"{remote_base}/backups",
    )

    return config


if __name__ == "__main__":
    # Test configuration loading
    try:
        cfg = load_config()
        print("Configuration loaded successfully!")
        print(f"  Remote: {cfg.remote_user}@{cfg.remote_host}")
        print(f"  Base: {cfg.remote_base}")
        print(f"  Domains: {', '.join(cfg.domains)}")
        print(f"  API Port: {cfg.api_port}")
    except (FileNotFoundError, ConfigurationError) as e:
        print(f"Error: {e}")