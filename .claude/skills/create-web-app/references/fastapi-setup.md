# FastAPI Setup Reference

## 1. Create Directory Structure

```
src/
└── api/
    ├── __init__.py
    └── main.py
```

## 2. Create API Package Init

Create `src/api/__init__.py`:

```python
"""FastAPI application package."""
```

## 3. Create Main Application

Create `src/api/main.py`:

```python
"""
FastAPI main application.

Entry point for the backend API.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    print("Starting API server...")
    yield
    print("Shutting down API server...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="<PROJECT_NAME> API",
        description="Backend API for <PROJECT_NAME>",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Add CORS middleware for Angular dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:<UI_PORT>",
            "http://127.0.0.1:<UI_PORT>",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


# Create the application instance
app = create_app()


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "<PROJECT_NAME>-api",
        "version": "1.0.0",
    }


@app.get("/api/hello")
async def hello_world() -> Dict[str, str]:
    """Hello world endpoint."""
    return {"message": "Hello, World!"}
```

Replace `<PROJECT_NAME>` with the actual project name and `<UI_PORT>` with the configured UI port.

## 4. Running the API

Run with uvicorn:

```bash
# From project root
uv run uvicorn api.main:app --host 0.0.0.0 --port <API_PORT> --reload

# Or from src directory
cd src
uv run uvicorn api.main:app --host 0.0.0.0 --port <API_PORT> --reload
```

## 5. Verify Setup

After starting the API:

- Health check: `http://localhost:<API_PORT>/api/health`
- Hello world: `http://localhost:<API_PORT>/api/hello`
- API docs: `http://localhost:<API_PORT>/api/docs`
- ReDoc: `http://localhost:<API_PORT>/api/redoc`

## 6. Adding Routers (Future)

When adding more endpoints, create routers in `src/api/routers/`:

```python
# src/api/routers/example_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/items")
async def get_items():
    return {"items": []}
```

Then include in `main.py`:

```python
from api.routers import example_router

app.include_router(
    example_router.router,
    prefix="/api/example",
    tags=["Example"]
)
```
