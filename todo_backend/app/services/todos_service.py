from typing import Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session


def _row_to_dict(row) -> Dict:
    """Convert SQLAlchemy Row to dict."""
    # row is a RowMapping in future=True mode
    return dict(row)


# PUBLIC_INTERFACE
def list_todos(db: Session) -> List[Dict]:
    """Return all todos."""
    result = db.execute(text("SELECT id, title, description, status FROM todos ORDER BY id ASC"))
    return [_row_to_dict(r) for r in result.mappings().all()]


# PUBLIC_INTERFACE
def create_todo(db: Session, title: str, description: str = "", status: str = "pending") -> Dict:
    """Create a new todo and return it."""
    if status not in ("pending", "done"):
        raise ValueError("Invalid status. Allowed values: 'pending', 'done'.")

    res = db.execute(
        text(
            """
            INSERT INTO todos (title, description, status)
            VALUES (:title, :description, :status)
            RETURNING id, title, description, status
            """
        ),
        {"title": title, "description": description or "", "status": status},
    )
    db.commit()
    row = res.mappings().first()
    return dict(row)


# PUBLIC_INTERFACE
def get_todo(db: Session, todo_id: int) -> Optional[Dict]:
    """Get a single todo by id."""
    res = db.execute(
        text("SELECT id, title, description, status FROM todos WHERE id = :id"),
        {"id": todo_id},
    )
    row = res.mappings().first()
    return dict(row) if row else None


# PUBLIC_INTERFACE
def update_todo(
    db: Session, todo_id: int, fields: Dict
) -> Optional[Dict]:
    """
    Update a todo by id with provided fields.
    Returns the updated todo or None if not found.
    """
    allowed_fields = {"title", "description", "status"}
    update_fields = {k: v for k, v in fields.items() if k in allowed_fields}

    if not update_fields:
        # Nothing to update
        current = get_todo(db, todo_id)
        return current

    if "status" in update_fields and update_fields["status"] not in ("pending", "done"):
        raise ValueError("Invalid status. Allowed values: 'pending', 'done'.")

    sets = []
    params: Dict[str, str] = {"id": todo_id}
    for idx, (k, v) in enumerate(update_fields.items()):
        key = f"v{idx}"
        sets.append(f"{k} = :{key}")
        params[key] = v

    sql = text(f"UPDATE todos SET {', '.join(sets)} WHERE id = :id RETURNING id, title, description, status")
    res = db.execute(sql, params)
    db.commit()
    row = res.mappings().first()
    return dict(row) if row else None


# PUBLIC_INTERFACE
def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo by id. Returns True if a row was deleted."""
    res = db.execute(text("DELETE FROM todos WHERE id = :id"), {"id": todo_id})
    db.commit()
    return res.rowcount > 0
