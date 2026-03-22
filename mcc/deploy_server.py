#!/usr/bin/env python3
"""Initial server setup for ana-auth.

Uploads systemd services and nginx configurations via Fabric/SSH.
Handles SSL certificate generation via Certbot.
Deploys both prod and dev staging areas in one run.
"""

import re
import sys
import time
from getpass import getpass
from pathlib import Path

from fabric import Connection
from invoke import UnexpectedExit

MCC_DIR = Path(__file__).parent
PROJECT_ROOT = MCC_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
from mcc_config import load_config


def make_domain_safe(domain: str) -> str:
    """Convert domain to safe identifier for nginx configs."""
    return re.sub(r"[^a-zA-Z0-9]", "_", domain)


def render_template(template_path: Path, replacements: dict[str, str]) -> str:
    """Render template with {{KEY}} style replacements."""
    content = template_path.read_text()
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def generate_service_config(config: dict[str, str]) -> str:
    """Generate systemd service configuration from daemon.template."""
    template = MCC_DIR / "daemon.template"
    return render_template(template, config)


def generate_nginx_config(config: dict[str, str]) -> str:
    """Generate nginx configuration from nginx.template."""
    template = MCC_DIR / "nginx.template"
    replacements = dict(config)
    replacements["DOMAIN_SAFE"] = make_domain_safe(config["DOMAIN"])
    return render_template(template, replacements)


def get_connection() -> Connection:
    """Get SSH connection with sudo password using prod configuration."""
    config = load_config("prod", config_dir=MCC_DIR)
    remote_user = config["REMOTE_USER"]
    remote_host = config["REMOTE_HOST"]

    print(f"---- REQUEST PASSWORD FOR {remote_user} AT {remote_host} ----")
    password = getpass("Enter sudo password: ")
    c = Connection(
        f"{remote_user}@{remote_host}", connect_kwargs={"password": password}
    )
    c.config.sudo.password = password
    return c


def upload_configuration_files(
    c: Connection, configs: list[dict[str, str]]
) -> None:
    """Upload systemd service and nginx configuration files."""
    remote_user = configs[0]["REMOTE_USER"]

    print("Uploading configuration files...")

    for config in configs:
        service_name = config["SERVICE_NAME"]
        domain = config["DOMAIN"]

        # Generate and upload systemd service file
        print(f"Generating daemon config for {service_name}...")
        service_content = generate_service_config(config)
        tmp_service_file = MCC_DIR / f"{service_name}.tmp"
        tmp_service_file.write_text(service_content)

        remote_path = f"/home/{remote_user}/{service_name}"
        print(f"Uploading {service_name} to {remote_path}...")
        c.put(str(tmp_service_file), remote_path)
        tmp_service_file.unlink()

        c.sudo(f"mv -f {remote_path} /etc/systemd/system/", echo=True)
        c.sudo(f"chown root:root /etc/systemd/system/{service_name}", echo=True)
        c.sudo(f"chmod 644 /etc/systemd/system/{service_name}", echo=True)

        # Generate and upload nginx config
        print(f"Generating nginx config for {domain}...")
        nginx_content = generate_nginx_config(config)
        tmp_file = MCC_DIR / f"{domain}.tmp"
        tmp_file.write_text(nginx_content)

        remote_path = f"/home/{remote_user}/{domain}"
        print(f"Uploading {domain} to {remote_path}...")
        c.put(str(tmp_file), remote_path)
        tmp_file.unlink()

        c.sudo(f"mv -f {remote_path} /etc/nginx/sites-available/", echo=True)
        c.sudo(f"chown root:root /etc/nginx/sites-available/{domain}", echo=True)


def setup_backend_daemons(
    c: Connection, configs: list[dict[str, str]]
) -> None:
    """Set up and start all backend systemd services."""
    print("Reloading systemd daemon...")
    c.sudo("/bin/systemctl daemon-reload", echo=True)

    for config in configs:
        service_name = config["SERVICE_NAME"]
        print(f"\nEnabling and starting {service_name}...")
        c.sudo(f"/bin/systemctl enable {service_name}", echo=True)
        c.sudo(f"/bin/systemctl restart {service_name}", echo=True)
        print(f"Wait 5 seconds and check {service_name} status...")
        time.sleep(5)
        c.sudo(f"/bin/systemctl status {service_name}", echo=True)

        print(f"Recent logs for {service_name}:")
        c.sudo(
            f"/usr/bin/journalctl -u {service_name} -n 10 --no-pager", echo=True
        )


def setup_nginx(c: Connection, configs: list[dict[str, str]]) -> None:
    """Set up nginx configuration and SSL certificates."""
    for config in configs:
        domain = config["DOMAIN"]
        email = config.get("EMAIL", f"admin@{domain}")

        print(f"\n---- Setting up nginx for {domain} ----")

        # Check if SSL certificates already exist
        cert_exists = False
        try:
            c.run(f"ls /etc/letsencrypt/live/{domain}/fullchain.pem", hide=True)
            cert_exists = True
            print("SSL certificates already exist")
        except UnexpectedExit:
            print("SSL certificates do not exist, will generate them")

        if not cert_exists:
            print(
                "First-time deployment: generating SSL certificates with standalone mode..."
            )
            c.sudo("/bin/systemctl stop nginx", warn=True, echo=True)

            try:
                c.sudo(
                    f"certbot certonly --standalone -d {domain} "
                    f"--non-interactive --agree-tos -m {email}",
                    echo=True,
                )
                print("SSL certificates generated successfully")
            except UnexpectedExit as e:
                print(f"Error: Certbot failed: {e}")
                print(f"Cannot proceed without SSL certificates for {domain}")
                continue

        print("Ensuring nginx symlink exists...")
        try:
            c.sudo(
                f"ln -sfn /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/{domain}",
                echo=True,
            )
        except UnexpectedExit as e:
            print(f"Warning: Could not create symlink: {e}")

    print("\nTesting and starting nginx...")
    try:
        c.sudo("nginx -t", echo=True)
        c.sudo("/bin/systemctl restart nginx", echo=True)
        print("Nginx started successfully with SSL")
    except UnexpectedExit as e:
        print(f"Error: Nginx failed to start: {e}")
        print("Check nginx configuration and SSL certificate paths")
        return

    # Renew certificates for domains that had existing certs
    for config in configs:
        domain = config["DOMAIN"]
        email = config.get("EMAIL", f"admin@{domain}")
        try:
            c.run(f"ls /etc/letsencrypt/live/{domain}/fullchain.pem", hide=True)
            print(f"Renewing SSL certificates for {domain} using nginx plugin...")
            try:
                c.sudo(
                    f"certbot certonly --nginx -d {domain} "
                    f"--non-interactive --agree-tos -m {email}",
                    warn=True,
                    echo=True,
                )
            except UnexpectedExit:
                print(
                    f"Certificate renewal not needed for {domain} (this is usually OK)"
                )
        except UnexpectedExit:
            pass


def main(c: Connection) -> None:
    """Main server setup orchestration for both prod and dev staging areas."""
    prod_config = load_config("prod", config_dir=MCC_DIR)
    dev_config = load_config("dev", config_dir=MCC_DIR)
    configs = [prod_config, dev_config]

    print("---- START SERVER SETUP ----")

    # Ensure base directories exist
    for config in configs:
        c.run(f"mkdir -p {config['REMOTE_BASE']}/logs", echo=True)
        c.run(f"mkdir -p {config['REMOTE_BASE']}/backup", echo=True)

    upload_configuration_files(c, configs)
    setup_nginx(c, configs)
    setup_backend_daemons(c, configs)
    print("---- SERVER SETUP FINISHED ----")


if __name__ == "__main__":
    main(get_connection())
