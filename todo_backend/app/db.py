from typing import Optional
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from .config import get_sqlite_config

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _get_engine() -> Engine:
    """Create the global SQLAlchemy engine for SQLite if needed."""
    global _engine
    if _engine is None:
        cfg = get_sqlite_config()
        # For SQLite, 'future=True' enables 2.x style and 'check_same_thread=False' allows usage across threads if needed
        _engine = create_engine(
            cfg.uri,
            connect_args={"check_same_thread": False},
            future=True,
        )
    return _engine


def get_db_session() -> Session:
    """Get a SQLAlchemy ORM Session bound to the global engine."""
    global _SessionLocal
    engine = _get_engine()
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return _SessionLocal()


def _try_init_schema(engine: Engine) -> None:
    """
    Initialize DB schema for SQLite. Creates the 'todos' table if it does not exist.
    """
    # Use SQLite-compatible DDL with AUTOINCREMENT and CHECK constraint
    create_table_sql = text(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'done'))
        );
        """
    )
    try:
        with engine.begin() as conn:
            conn.execute(create_table_sql)
        print("[db] SQLite schema initialization ensured.")
    except OperationalError as e:
        print(f"[db] Warning: SQLite not reachable during init: {e}")
    except Exception as e:
        print(f"[db] Warning: Unexpected error during DB init: {e}")


def init_db() -> None:
    """
    Initialize the database schema required by the application.
    Creates the 'todos' table if it does not exist.
    """
    engine = _get_engine()
    # Retain a small retry loop for robustness, though SQLite should be immediate.
    retries = int(os.getenv("DB_INIT_RETRIES", "1"))
    delay = float(os.getenv("DB_INIT_RETRY_DELAY", "0.1"))
    for attempt in range(1, retries + 1):
        try:
            _try_init_schema(engine)
            break
        except Exception as e:
            print(f"[db] init attempt {attempt}/{retries} failed: {e}")
        if attempt < retries:
            time.sleep(delay)
