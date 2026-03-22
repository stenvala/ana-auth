#!/usr/bin/env python3
"""Server infrastructure setup for ana-auth.

Renders templates and deploys systemd/nginx configs via SSH.
Run from local machine to set up both prod and dev stages.
"""

import subprocess
import sys
from pathlib import Path

MCC_DIR = Path(__file__).parent
PROJECT_ROOT = MCC_DIR.parent

# Add project root to path for imports
sys.path.insert(0, str(PROJECT_ROOT))
from mcc_config import load_config


def render_template(template_path: Path, config: dict[str, str]) -> str:
    """Replace {{KEY}} placeholders in a template with config values."""
    content = template_path.read_text()
    for key, value in config.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def _ssh_run(config: dict[str, str], cmd: str) -> None:
    """Run a command on the remote server via SSH."""
    remote = f"{config['REMOTE_USER']}@{config['REMOTE_HOST']}"
    print(f"SSH: {cmd}")
    subprocess.run(["ssh", remote, cmd], check=True)


def _upload_file(config: dict[str, str], content: str, remote_path: str) -> None:
    """Upload content to a file on the remote server."""
    remote = f"{config['REMOTE_USER']}@{config['REMOTE_HOST']}"
    print(f"Uploading: {remote_path}")
    subprocess.run(
        ["ssh", remote, f"cat > /tmp/_mcc_upload"],
        input=content,
        text=True,
        check=True,
    )
    subprocess.run(
        ["ssh", remote, f"sudo mv /tmp/_mcc_upload {remote_path}"],
        check=True,
    )


def generate_service_config(config: dict[str, str]) -> str:
    """Render the systemd service template for a stage."""
    template = MCC_DIR / "daemon.template"
    return render_template(template, config)


def generate_nginx_config(config: dict[str, str]) -> str:
    """Render the nginx config template for a stage."""
    template = MCC_DIR / "nginx.template"
    return render_template(template, config)


def upload_configuration_files(config: dict[str, str]) -> None:
    """Upload systemd and nginx configs to the remote server."""
    service_name = config["SERVICE_NAME"]
    domain = config["DOMAIN"]

    # Upload systemd service
    service_content = generate_service_config(config)
    _upload_file(
        config,
        service_content,
        f"/etc/systemd/system/{service_name}",
    )

    # Upload nginx config
    nginx_content = generate_nginx_config(config)
    _upload_file(
        config,
        nginx_content,
        f"/etc/nginx/sites-available/{domain}",
    )


def setup_backend_daemons(config: dict[str, str]) -> None:
    """Enable and restart the systemd service."""
    service_name = config["SERVICE_NAME"]
    _ssh_run(config, f"sudo systemctl daemon-reload")
    _ssh_run(config, f"sudo systemctl enable {service_name}")
    _ssh_run(config, f"sudo systemctl restart {service_name}")
    print(f"Service {service_name} enabled and restarted.")


def setup_nginx(config: dict[str, str]) -> None:
    """Set up nginx with SSL via certbot."""
    domain = config["DOMAIN"]

    # Create symlink in sites-enabled
    _ssh_run(
        config,
        f"sudo ln -sf /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/{domain}",
    )

    # Test nginx config
    _ssh_run(config, "sudo nginx -t")

    # Check if SSL cert exists; if not, obtain one
    _ssh_run(
        config,
        f'test -d /etc/letsencrypt/live/{domain} || sudo certbot certonly --standalone -d {domain} --non-interactive --agree-tos --email admin@{domain.split(".", 1)[1] if "." in domain else domain}',
    )

    # Restart nginx
    _ssh_run(config, "sudo systemctl restart nginx")
    print(f"Nginx configured for {domain}.")


def setup_stage(stage: str) -> None:
    """Full infrastructure setup for a single stage."""
    config = load_config(stage, config_dir=MCC_DIR)
    print(f"\n{'=' * 40}")
    print(f"SETTING UP: {stage} ({config['DOMAIN']})")
    print(f"{'=' * 40}")

    # Ensure base directories exist
    _ssh_run(config, f"mkdir -p {config['REMOTE_BASE']}/logs")

    upload_configuration_files(config)
    setup_backend_daemons(config)
    setup_nginx(config)

    print(f"\nInfrastructure setup complete for {stage}.")


def main() -> None:
    """Set up server infrastructure for both prod and dev stages."""
    print("ana-auth server infrastructure setup")
    print("=" * 40)

    for stage in ["prod", "dev"]:
        setup_stage(stage)

    print("\n\nAll stages configured successfully.")


if __name__ == "__main__":
    main()
