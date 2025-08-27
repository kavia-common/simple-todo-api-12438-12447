import os
from dataclasses import dataclass
from urllib.parse import quote_plus

# PUBLIC_INTERFACE
@dataclass
class DatabaseConfig:
    """Holds configuration for connecting to the PostgreSQL database."""
    host: str
    port: str
    user: str
    password: str
    dbname: str

    @property
    def uri(self) -> str:
        """
        Build a SQLAlchemy-compatible PostgreSQL URI.
        Example: postgresql+psycopg://user:pass@host:port/dbname
        """
        return (
            "postgresql+psycopg://"
            f"{quote_plus(self.user)}:{quote_plus(self.password)}@"
            f"{self.host}:{self.port}/{self.dbname}"
        )


# PUBLIC_INTERFACE
def load_db_config_from_env() -> DatabaseConfig:
    """
    Load database configuration from environment variables.

    Required variables (documented in .env.example):
    - POSTGRES_URL
    - POSTGRES_PORT
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB

    Defaults are provided to prevent hard crashes during startup, but note that
    using defaults (localhost/empty password) will likely fail to connect in production.
    """
    # Allow DATABASE_URL override if provided (common in platforms)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # If DATABASE_URL is present, we still want to parse it into fields to keep a single path in code.
        # A lightweight parse using urllib is possible, but to keep dependencies minimal here, we
        # fall back to field-based envs when DATABASE_URL is not used directly elsewhere.
        # For now we'll just return a config from field envs, since db.py builds the URI from fields.
        pass

    host = os.getenv("POSTGRES_URL", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    dbname = os.getenv("POSTGRES_DB", "postgres")

    # Minimal validation/log hints via env flag
    debug = os.getenv("BACKEND_DEBUG", "false").lower() == "true"
    if debug:
        # Print a concise redacted summary to help diagnose startup without leaking secrets
        redacted_pw = "****" if password else "(empty)"
        print(
            "[config] DB env -> "
            f"host={host} port={port} user={user} password={redacted_pw} db={dbname}"
        )

    return DatabaseConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )
