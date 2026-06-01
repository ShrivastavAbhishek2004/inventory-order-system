from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

from app.config import settings


# ── Engine ────────────────────────────────────────────────────────────────────
# The engine is the core interface to the database.
# pool_pre_ping=True checks the connection is alive before using it.
# pool_size controls how many connections to keep open simultaneously.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,     # Reconnects automatically if connection drops
    pool_size=10,           # Keep up to 10 connections open
    max_overflow=20,        # Allow 20 extra connections under heavy load
    pool_recycle=3600,      # Recycle connections every hour (prevents stale connections)
    echo=settings.DEBUG,    # Print SQL queries to console in DEBUG mode (very helpful!)
)


# ── Session Factory ───────────────────────────────────────────────────────────
# SessionLocal creates individual database sessions (think of a session as a
# conversation with the database — it starts, does work, then ends).
SessionLocal = sessionmaker(
    autocommit=False,   # We manually commit (safer, allows rollback on errors)
    autoflush=False,    # We manually flush (more control over when SQL runs)
    bind=engine,
)


# ── Base Class ────────────────────────────────────────────────────────────────
# All our SQLAlchemy models (Product, Customer, Order) will inherit from Base.
# SQLAlchemy uses this to know which classes represent database tables.
class Base(DeclarativeBase):
    pass


# ── Dependency ────────────────────────────────────────────────────────────────
# This function is a FastAPI "dependency" — it's injected into route functions
# automatically. It opens a DB session, gives it to the route, and always
# closes it afterwards (even if an error occurs, thanks to try/finally).
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db          # The route function receives this db session
    finally:
        db.close()        # Always close the session when done


# ── Health Check Helper ───────────────────────────────────────────────────────
def check_db_connection() -> bool:
    """Returns True if the database is reachable, False otherwise."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False