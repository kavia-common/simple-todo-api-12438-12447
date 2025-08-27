import os
from dataclasses import dataclass

# PUBLIC_INTERFACE
@dataclass
class SQLiteConfig:
    """Configuration for the embedded SQLite database."""
    db_path: str

    @property
    def uri(self) -> str:
        """
        Build a SQLAlchemy-compatible SQLite URI using the file-based database.
        Example: sqlite:///absolute/or/relative/path/to/todos.db
        """
        # Ensure URI uses three slashes for relative/absolute filesystem paths
        return f"sqlite:///{self.db_path}"


# PUBLIC_INTERFACE
def get_sqlite_config() -> SQLiteConfig:
    """
    Provide the SQLite configuration for the application.
    The database file is stored under the todo_backend directory as 'todos.db'.
    No environment variables are needed; this works out-of-the-box.
    """
    # Determine base directory (this file is under .../todo_backend/app/)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "todos.db")
    return SQLiteConfig(db_path=db_path)
