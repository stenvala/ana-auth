#!/usr/bin/env python3
"""
Infrastructure deployment - uploads systemd services and nginx configuration.
Handles SSL certificate generation via Certbot.
Supports single-domain and multi-domain configurations, API and worker services.
"""

import argparse
import re
import time
from getpass import getpass
from pathlib import Path

import yaml
from fabric import Connection
from invoke import UnexpectedExit


def make_domain_safe(domain: str) -> str:
    """Convert domain to safe identifier for nginx configs."""
    return re.sub(r"[^a-zA-Z0-9]", "_", domain)


def load_config(config_path: Path) -> dict:
    """Load and validate configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    data = yaml.safe_load(config_path.read_text())

    required = ["REMOTE_USER", "REMOTE_HOST", "REMOTE_BASE", "DIR_USER", "DIR_GROUP"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")

    # Resolve {{REMOTE_BASE}} templates in string values
    remote_base = data["REMOTE_BASE"]
    for key, value in data.items():
        if isinstance(value, str) and "{{REMOTE_BASE}}" in value:
            data[key] = value.replace("{{REMOTE_BASE}}", remote_base)

    return data


def get_domains(config: dict) -> list[str]:
    """Get domain list from config (supports DOMAIN or DOMAINS)."""
    if config.get("DOMAINS"):
        return config["DOMAINS"]
    if config.get("DOMAIN"):
        return [config["DOMAIN"]]
    raise ValueError("Config must have DOMAIN or DOMAINS")


def build_replacements(config: dict, domain: str | None = None) -> dict[str, str]:
    """Build template replacement dictionary from config."""
    remote_base = config["REMOTE_BASE"]

    replacements = {
        "REMOTE_BASE": remote_base,
        "DIR_USER": config["DIR_USER"],
        "DIR_GROUP": config["DIR_GROUP"],
        "API_PORT": str(config.get("API_PORT", 8000)),
        "WORKERS": str(config.get("WORKERS", 4)),
        "STAGE": config.get("STAGE", ""),
        "LOG_LEVEL": config.get("LOG_LEVEL", "INFO"),
        "API_SYMLINK": config.get("API_SYMLINK", f"{remote_base}/current-api"),
        "UI_SYMLINK": config.get("UI_SYMLINK", f"{remote_base}/current-ui"),
        "DATA_DIR": config.get("DATA_DIR", f"{remote_base}/data"),
        "DESCRIPTION": config.get(
            "SERVICE_DESCRIPTION",
            config.get("SERVICE_NAME", "app").replace(".service", "").replace("-", " ").title() + " API Service",
        ),
        "WORKER_DESCRIPTION": config.get(
            "WORKER_DESCRIPTION",
            config.get("WORKER_SERVICE_NAME", "worker").replace(".service", "").replace("-", " ").title() + " Service",
        ),
    }

    if domain:
        replacements["DOMAIN"] = domain
        replacements["DOMAIN_SAFE"] = make_domain_safe(domain)

    return replacements


def render_template(template: str, replacements: dict[str, str]) -> str:
    """Render template with {{KEY}} style replacements."""
    result = template
    for key, value in replacements.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def get_connection(config: dict) -> Connection:
    """Get SSH connection with sudo password."""
    remote_user = config["REMOTE_USER"]
    remote_host = config["REMOTE_HOST"]

    print(f"---- REQUEST PASSWORD FOR {remote_user} AT {remote_host} ----")
    password = getpass("Enter sudo password: ")
    c = Connection(f"{remote_user}@{remote_host}", connect_kwargs={"password": password})
    c.config.sudo.password = password
    return c


def upload_service_file(
    c: Connection,
    config: dict,
    service_name: str,
    replacements: dict[str, str],
) -> None:
    """Render and upload a systemd service file."""
    template_path = Path(__file__).parent / service_name
    if not template_path.exists():
        print(f"Template {template_path} not found, skipping")
        return

    print(f"Rendering {service_name}...")
    content = render_template(template_path.read_text(), replacements)

    tmp_file = Path(__file__).parent / f"{service_name}.tmp"
    tmp_file.write_text(content)

    remote_user = config["REMOTE_USER"]
    remote_path = f"/home/{remote_user}/{service_name}"
    print(f"Uploading {service_name}...")
    c.put(str(tmp_file), remote_path)
    tmp_file.unlink()

    c.sudo(f"mv -f {remote_path} /etc/systemd/system/", echo=True)
    c.sudo(f"chown root:root /etc/systemd/system/{service_name}", echo=True)
    c.sudo(f"chmod 644 /etc/systemd/system/{service_name}", echo=True)


def upload_nginx_config(
    c: Connection,
    config: dict,
    domain: str,
    replacements: dict[str, str],
) -> None:
    """Render and upload nginx config for a domain."""
    template_path = Path(__file__).parent / "nginx.template"
    if not template_path.exists():
        print(f"Nginx template not found at {template_path}")
        return

    print(f"Rendering nginx config for {domain}...")
    content = render_template(template_path.read_text(), replacements)

    tmp_file = Path(__file__).parent / f"{domain}.tmp"
    tmp_file.write_text(content)

    remote_user = config["REMOTE_USER"]
    remote_path = f"/home/{remote_user}/{domain}"
    print(f"Uploading nginx config for {domain}...")
    c.put(str(tmp_file), remote_path)
    tmp_file.unlink()

    c.sudo(f"mv -f {remote_path} /etc/nginx/sites-available/", echo=True)
    c.sudo(f"chown root:root /etc/nginx/sites-available/{domain}", echo=True)


def setup_ssl(c: Connection, domain: str, email: str) -> None:
    """Generate or verify SSL certificates for a domain."""
    cert_exists = False
    try:
        c.run(f"ls /etc/letsencrypt/live/{domain}/fullchain.pem", hide=True)
        cert_exists = True
        print(f"SSL certificates already exist for {domain}")
    except UnexpectedExit:
        print(f"SSL certificates do not exist for {domain}, generating...")

    if not cert_exists:
        c.sudo("/bin/systemctl stop nginx", warn=True, echo=True)
        try:
            c.sudo(
                f"certbot certonly --standalone -d {domain} "
                f"--non-interactive --agree-tos -m {email}",
                echo=True,
            )
            print("SSL certificates generated successfully")
        except UnexpectedExit as e:
            print(f"Error: Certbot failed for {domain}: {e}")
            return


def setup_nginx(c: Connection, config: dict) -> None:
    """Set up nginx sites and SSL certificates."""
    domains = get_domains(config)
    email = config.get("EMAIL", "")

    for domain in domains:
        print(f"\n---- Setting up nginx for {domain} ----")
        setup_ssl(c, domain, email)

        # Enable site
        c.sudo(
            f"ln -sfn /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/{domain}",
            warn=True,
            echo=True,
        )

    print("\nTesting and starting nginx...")
    try:
        c.sudo("nginx -t", echo=True)
        c.sudo("/bin/systemctl restart nginx", echo=True)
        print("Nginx started successfully")
    except UnexpectedExit as e:
        print(f"Error: Nginx failed to start: {e}")
        print("Check nginx configuration and SSL certificate paths")


def setup_services(c: Connection, config: dict) -> None:
    """Enable and start systemd services."""
    services = []
    if config.get("SERVICE_NAME"):
        services.append(config["SERVICE_NAME"])
    if config.get("WORKER_SERVICE_NAME"):
        services.append(config["WORKER_SERVICE_NAME"])

    if not services:
        print("No services configured")
        return

    c.sudo("/bin/systemctl daemon-reload", echo=True)

    for service_name in services:
        print(f"\n---- Setting up {service_name} ----")
        c.sudo(f"/bin/systemctl enable {service_name}", echo=True)
        c.sudo(f"/bin/systemctl restart {service_name}", echo=True)
        print("Waiting 5 seconds...")
        time.sleep(5)
        c.sudo(f"/bin/systemctl status {service_name}", echo=True)
        c.sudo(f"/usr/bin/journalctl -u {service_name} -n 10 --no-pager", echo=True)


def main() -> None:
    """Main infrastructure deployment."""
    parser = argparse.ArgumentParser(description="Deploy server infrastructure")
    parser.add_argument(
        "--conf",
        default="conf.yml",
        help="Configuration file (default: conf.yml)",
    )
    args = parser.parse_args()

    config_path = Path(__file__).parent / args.conf
    config = load_config(config_path)
    domains = get_domains(config)

    print("---- START INFRASTRUCTURE DEPLOYMENT ----")
    print(f"Config: {args.conf}")
    print(f"Server: {config['REMOTE_USER']}@{config['REMOTE_HOST']}")
    print(f"Domains: {', '.join(domains)}")

    c = get_connection(config)
    replacements = build_replacements(config)

    # Upload service files
    if config.get("SERVICE_NAME"):
        upload_service_file(c, config, config["SERVICE_NAME"], replacements)

    if config.get("WORKER_SERVICE_NAME"):
        upload_service_file(c, config, config["WORKER_SERVICE_NAME"], replacements)

    # Upload nginx configs (one per domain)
    for domain in domains:
        domain_replacements = build_replacements(config, domain)
        upload_nginx_config(c, config, domain, domain_replacements)

    # Set up nginx and SSL
    setup_nginx(c, config)

    # Set up and start services
    setup_services(c, config)

    print("\n---- INFRASTRUCTURE DEPLOYMENT FINISHED ----")


if __name__ == "__main__":
    main()
