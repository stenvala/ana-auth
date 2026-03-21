# pyproject.toml Setup Reference

## Create pyproject.toml

Create `pyproject.toml` in project root for uv-managed Python dependencies:

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = "<PROJECT_DESCRIPTION>"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    # Web framework
    "fastapi>=0.116.1",
    "uvicorn[standard]>=0.32.0",

    # CLI tools
    "typer>=0.16.1",

    # Process management
    "psutil>=7.0.0",
]

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
extend-select = ["I"]  # Enable import sorting

[tool.ruff.lint.isort]
force-single-line = false
known-first-party = ["api", "shared"]

[tool.coverage.run]
source = ["src"]
omit = [
    "**/__init__.py",
    "**/test_*.py",
    "tests/*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
precision = 1
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"

[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests",
]
asyncio_mode = "auto"
timeout = 60
addopts = "--timeout=60 -W ignore::UserWarning"

[dependency-groups]
dev = [
    # Testing dependencies
    "pytest>=8.4.1",
    "pytest-cov>=6.2.1",
    "pytest-asyncio>=0.25.0",
    "pytest-timeout>=2.3.1",

    # Code quality tools
    "ruff>=0.12.10",
    "mypy>=1.17.1",
]
```

Replace `<project-name>` and `<PROJECT_DESCRIPTION>` with actual values.

## Initialize with uv

```bash
# Initialize uv environment
uv sync

# Install dev dependencies
uv sync --group dev
```

## Common Dependency Groups

### For Database Projects

Add to dependencies:

```toml
dependencies = [
    # ... existing deps ...
    "sqlmodel>=0.0.22",
    "psycopg2-binary>=2.9.9",  # PostgreSQL
]
```

### For HTTP Clients

Add to dependencies:

```toml
dependencies = [
    # ... existing deps ...
    "httpx>=0.28.1",
    "requests>=2.32.5",
]
```

### For Authentication

Add to dependencies:

```toml
dependencies = [
    # ... existing deps ...
    "pyjwt>=2.8.0",
    "bcrypt>=4.1.0",
    "email-validator>=2.1.0",
]
```

### For E2E Testing

Add to dev group:

```toml
[dependency-groups]
dev = [
    # ... existing deps ...
    "pytest-playwright>=0.7.1",
    "pytest-xdist>=3.8.0",
    "playwright>=1.55.0",
]
```

## Usage Commands

```bash
# Install all dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --group dev <package-name>

# Run a command with uv
uv run python script.py
uv run pytest
uv run ruff check src/

# Update dependencies
uv lock --upgrade
uv sync
```
