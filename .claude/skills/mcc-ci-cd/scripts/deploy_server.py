#!/usr/bin/env python3
"""
Initial server setup - uploads systemd service and nginx configuration.
Handles SSL certificate generation via Certbot.
Supports both single-domain and multi-domain configurations.
"""

import re
import time
from getpass import getpass
from pathlib import Path

from fabric import Connection
from invoke import UnexpectedExit

from config_loader import Config, load_config


def make_domain_safe(domain: str) -> str:
    """Convert domain to safe identifier for nginx configs."""
    return re.sub(r"[^a-zA-Z0-9]", "_", domain)


def render_template(template: str, replacements: dict[str, str]) -> str:
    """Render template with {{KEY}} style replacements."""
    result = template
    for key, value in replacements.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def generate_service_config(config: Config) -> str:
    """Generate systemd service configuration from template."""
    template_path = Path(__file__).parent / config.service_name
    template = template_path.read_text()

    replacements = {
        "API_SYMLINK": config.api_symlink,
        "REMOTE_BASE": config.remote_base,
        "API_PORT": str(config.api_port),
    }

    return render_template(template, replacements)


def generate_nginx_config(config: Config, domain: str) -> str:
    """Generate nginx configuration from template for a domain."""
    template_path = Path(__file__).parent / "nginx.template"
    template = template_path.read_text()

    replacements = {
        "DOMAIN": domain,
        "DOMAIN_SAFE": make_domain_safe(domain),
        "API_PORT": str(config.api_port),
        "UI_SYMLINK": config.ui_symlink,
    }

    return render_template(template, replacements)


def safe_symlink(c: Connection, source: str, target: str) -> None:
    """Create symlink safely, overwrite if exists."""
    try:
        c.sudo(f"ln -sfn {source} {target}", echo=True)
    except UnexpectedExit as e:
        print(f"Warning: Could not create symlink {target}: {e}")


def get_connection() -> Connection:
    """Get SSH connection with sudo password using configuration."""
    config = load_config()
    remote_user = config.remote_user
    remote_host = config.remote_host

    print(f"---- REQUEST PASSWORD FOR {remote_user} AT {remote_host} ----")
    password = getpass("Enter sudo password: ")
    c = Connection(
        f"{remote_user}@{remote_host}", connect_kwargs={"password": password}
    )
    c.config.sudo.password = password
    return c


def upload_configuration_files(c: Connection) -> None:
    """Upload systemd service and nginx configuration files."""
    config = load_config()
    service_name = config.service_name
    domains = config.domains
    remote_user = config.remote_user

    print("Uploading files...")

    # Generate and upload systemd service file
    print("Generating systemd service config...")
    service_content = generate_service_config(config)
    tmp_service_file = Path(__file__).parent / f"{service_name}.tmp"
    tmp_service_file.write_text(service_content)

    remote_path = f"/home/{remote_user}/{service_name}"
    print(f"Uploading {service_name} to {remote_path}...")
    c.put(str(tmp_service_file), remote_path)
    tmp_service_file.unlink()

    # Generate and upload nginx config for each domain
    for domain in domains:
        print(f"Generating nginx config for {domain}...")
        nginx_content = generate_nginx_config(config, domain)

        # Write to temporary local file
        tmp_file = Path(__file__).parent / f"{domain}.tmp"
        tmp_file.write_text(nginx_content)

        remote_path = f"/home/{remote_user}/{domain}"
        print(f"Uploading {domain} to {remote_path}...")
        c.put(str(tmp_file), remote_path)

        # Clean up temp file
        tmp_file.unlink()

    print("Moving configuration files...")
    c.sudo(f"mv -f /home/{remote_user}/{service_name} /etc/systemd/system/", echo=True)
    c.sudo(f"chown root:root /etc/systemd/system/{service_name}", echo=True)
    c.sudo(f"chmod 644 /etc/systemd/system/{service_name}", echo=True)

    for domain in domains:
        c.sudo(
            f"mv -f /home/{remote_user}/{domain} /etc/nginx/sites-available/", echo=True
        )
        c.sudo(f"chown root:root /etc/nginx/sites-available/{domain}", echo=True)


def setup_backend_daemon(c: Connection) -> None:
    """Set up and start the backend systemd service."""
    config = load_config()
    service_name = config.service_name

    print("Reloading and restarting systemd service...")
    c.sudo("/bin/systemctl daemon-reload", echo=True)
    c.sudo(f"/bin/systemctl enable {service_name}", echo=True)
    c.sudo(f"/bin/systemctl restart {service_name}", echo=True)
    print("Wait 5 seconds and check system status...")
    time.sleep(5)
    c.sudo(f"/bin/systemctl status {service_name}", echo=True)

    print("Recent service logs:")
    c.sudo(f"/usr/bin/journalctl -u {service_name} -n 10 --no-pager", echo=True)


def setup_nginx(c: Connection) -> None:
    """Set up nginx configuration and SSL certificates for all domains."""
    config = load_config()
    domains = config.domains
    email = config.email

    for domain in domains:
        print(f"\n---- Setting up nginx for {domain} ----")

        # First, check if SSL certificates already exist
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

            # Stop nginx if it's running
            c.sudo("/bin/systemctl stop nginx", warn=True, echo=True)

            # Generate certificates using standalone mode (doesn't need nginx)
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

        # Now that certificates exist, enable the nginx site
        print("Ensuring nginx symlink exists...")
        safe_symlink(
            c,
            f"/etc/nginx/sites-available/{domain}",
            f"/etc/nginx/sites-enabled/{domain}",
        )

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
    for domain in domains:
        try:
            c.run(f"ls /etc/letsencrypt/live/{domain}/fullchain.pem", hide=True)
            print(f"Renewing SSL certificates for {domain} using nginx plugin...")
            try:
                c.sudo(
                    f"certbot certonly --nginx -d {domain} "
                    f"--non-interactive --agree-tos -m {email}",
                    warn=True,  # Allow this to fail if not needed
                    echo=True,
                )
            except UnexpectedExit:
                print(
                    f"Certificate renewal not needed for {domain} (this is usually OK)"
                )
        except UnexpectedExit:
            pass


def main(c: Connection) -> None:
    """Main server setup orchestration."""
    print("---- START SERVER SETUP ----")
    upload_configuration_files(c)
    setup_nginx(c)
    setup_backend_daemon(c)
    print("---- SERVER SETUP FINISHED ----")


if __name__ == "__main__":
    main(get_connection())
