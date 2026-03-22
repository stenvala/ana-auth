"""Configuration loader for MCC pipeline with template variable resolution."""

import re
import sys
from pathlib import Path

import yaml


def load_config(stage: str, config_dir: Path | None = None) -> dict[str, str]:
    """Load and resolve stage configuration from YAML file.

    Reads mcc/conf-{stage}.yml, resolves {{VAR}} template variables,
    and returns a flat dictionary of resolved values.
    """
    if config_dir is None:
        config_dir = Path(__file__).parent / "mcc"

    config_path = config_dir / f"conf-{stage}.yml"
    if not config_path.exists():
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        print(f"Invalid configuration format in {config_path}")
        sys.exit(1)

    # Convert all values to strings
    config: dict[str, str] = {k: str(v) for k, v in raw.items()}

    return _resolve_templates(config)


def _resolve_templates(config: dict[str, str]) -> dict[str, str]:
    """Resolve {{VAR}} template variables with cycle detection."""
    resolved: dict[str, str] = {}

    for key in config:
        if key not in resolved:
            _resolve_key(key, config, resolved, set())

    return resolved


def _resolve_key(
    key: str,
    config: dict[str, str],
    resolved: dict[str, str],
    resolving: set[str],
) -> str:
    """Resolve a single key, detecting cycles."""
    if key in resolved:
        return resolved[key]

    if key in resolving:
        cycle = " -> ".join(resolving) + f" -> {key}"
        msg = f"Cycle detected in template variables: {cycle}"
        raise ValueError(msg)

    resolving.add(key)
    value = config[key]

    def replace_var(match: re.Match) -> str:
        var_name = match.group(1)
        if var_name not in config:
            return match.group(0)  # Leave unresolved if not in config
        return _resolve_key(var_name, config, resolved, resolving)

    resolved_value = re.sub(r"\{\{(\w+)\}\}", replace_var, value)
    resolved[key] = resolved_value
    resolving.discard(key)
    return resolved_value
