from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

from app.config import settings
from app.database import engine, Base, check_db_connection
from app.utils.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    global_exception_handler,
)

# ── Logging Configuration ─────────────────────────────────────────────────────
# Configures Python's built-in logger to show timestamps and log levels.
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
# The lifespan context manager runs code at startup and shutdown.
# This is the modern FastAPI way (replaces deprecated @app.on_event).
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    logger.info("🚀 Starting up Inventory & Order Management API...")

    # Create all database tables if they don't exist yet.
    # SQLAlchemy reads all classes that inherit from Base and creates their tables.
    logger.info("📦 Creating database tables if not exists...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables ready.")

    # Check that the database is actually reachable.
    if check_db_connection():
        logger.info("✅ Database connection verified.")
    else:
        logger.error("❌ Cannot connect to database! Check your DATABASE_URL.")

    logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} is ready.")

    yield  # The application runs here

    # ── SHUTDOWN ──
    logger.info("🛑 Shutting down...")
    engine.dispose()  # Close all database connections cleanly
    logger.info("✅ Database connections closed.")


# ── FastAPI App Instance ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Inventory & Order Management System API

A production-ready REST API for managing products, customers, and orders.

### Features
- **Product Management** — Full CRUD with SKU uniqueness and stock tracking
- **Customer Management** — Customer records with unique email enforcement  
- **Order Management** — Order creation with automatic stock deduction and total calculation
- **Dashboard** — Aggregated statistics and low-stock alerts

### Authentication
Currently open for development. JWT authentication can be added in a future phase.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",       # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc UI at http://localhost:8000/redoc
    lifespan=lifespan,
)


# ── CORS Middleware ────────────────────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing.
# Browsers block requests from one domain (localhost:5173) to another
# (localhost:8000) unless the server explicitly allows it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,    # Which frontends can talk to us
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)


# ── Exception Handlers ────────────────────────────────────────────────────────
# Register our custom error handlers so all errors return clean JSON.
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, global_exception_handler)


# ── Routes ────────────────────────────────────────────────────────────────────
# We'll add more routers here in Phases 5, 6, and 7.
# Example: app.include_router(products.router, prefix="/products", tags=["Products"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Returns the API status and database connectivity.",
)
def health_check():
    """
    Simple health check endpoint.
    Used by Docker, Render, and load balancers to verify the service is alive.
    """
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "unreachable",
        "debug_mode": settings.DEBUG,
    }


@app.get(
    "/",
    tags=["System"],
    summary="API root",
)
def root():
    """Root endpoint — useful for confirming the API is running."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health",
    }