"""Main application module for Ad Hoc Web UI"""

import re
import time
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette_csrf import CSRFMiddleware

from .__init__ import __version__
from .config import settings
from .database import init_db
from .routes import auth, pages

# Application startup time
startup_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: cleanup if needed


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# Initialize FastAPI app
app = FastAPI(title=settings.app_name, version=__version__, lifespan=lifespan)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CSRF protection middleware
app.add_middleware(
    CSRFMiddleware,
    secret=settings.csrf_secret_key,
    cookie_name="csrf_token",
    cookie_samesite="lax",
    cookie_httponly=False,  # Must be False so JavaScript can read it
    header_name="X-CSRF-Token",
    exempt_urls=[re.compile(r"^/health$")],  # Exempt health check from CSRF
)

# Get the app directory path
APP_DIR = Path(__file__).parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
pages.set_templates(templates)

# Include routers
app.include_router(auth.router)
app.include_router(pages.router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "uptime": time.time() - startup_time}


def main():
    """Run the application"""
    from .logging import UVICORN_LOG_CONFIG
    global startup_time

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_config=UVICORN_LOG_CONFIG,
    )


if __name__ == "__main__":
    main()
