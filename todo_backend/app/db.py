from typing import Optional
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from .config import load_db_config_from_env

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _get_engine() -> Engine:
    """Create the global SQLAlchemy engine if needed."""
    global _engine
    if _engine is None:
        db_cfg = load_db_config_from_env()
        # Add connection args/timeouts for better failure behavior
        connect_args = {
            # psycopg3 supports options via connect_timeout in seconds
            "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
        }
        pool_pre_ping = True  # detect stale connections
        _engine = create_engine(
            db_cfg.uri,
            connect_args=connect_args,
            pool_pre_ping=pool_pre_ping,
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
    Attempt to initialize DB schema. Non-fatal: if DB is unavailable,
    we log and proceed so the app can still start (health endpoint works).
    """
    create_table_sql = text(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT DEFAULT '' NOT NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'done')) DEFAULT 'pending'
        );
        """
    )
    try:
        with engine.begin() as conn:
            conn.execute(create_table_sql)
        print("[db] Schema initialization ensured.")
    except OperationalError as e:
        print(f"[db] Warning: Database not reachable during init: {e}")
    except Exception as e:
        print(f"[db] Warning: Unexpected error during DB init: {e}")


def init_db() -> None:
    """
    Initialize the database schema required by the application.
    Creates the 'todos' table if it does not exist.

    This function is resilient: it won't crash app startup if DB is briefly unavailable.
    It will attempt a few retries to give DB time to come up in containerized environments.
    """
    engine = _get_engine()
    retries = int(os.getenv("DB_INIT_RETRIES", "5"))
    delay = float(os.getenv("DB_INIT_RETRY_DELAY", "2.0"))
    for attempt in range(1, retries + 1):
        try:
            _try_init_schema(engine)
            break
        except Exception as e:
            # _try_init_schema already logs; this is an extra safety catch
            print(f"[db] init attempt {attempt}/{retries} failed: {e}")
        if attempt < retries:
            time.sleep(delay)
