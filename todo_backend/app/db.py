from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from .config import load_db_config_from_env

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _get_engine() -> Engine:
    """Create the global SQLAlchemy engine if needed."""
    global _engine
    if _engine is None:
        db_cfg = load_db_config_from_env()
        _engine = create_engine(db_cfg.uri, future=True)
    return _engine


def get_db_session() -> Session:
    """Get a SQLAlchemy ORM Session bound to the global engine."""
    global _SessionLocal
    engine = _get_engine()
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return _SessionLocal()


def init_db() -> None:
    """
    Initialize the database schema required by the application.
    Creates the 'todos' table if it does not exist.
    """
    engine = _get_engine()
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
    with engine.begin() as conn:
        conn.execute(create_table_sql)
