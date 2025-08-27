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
    """Load database configuration from environment variables."""
    host = os.getenv("POSTGRES_URL", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    dbname = os.getenv("POSTGRES_DB", "postgres")
    return DatabaseConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )
