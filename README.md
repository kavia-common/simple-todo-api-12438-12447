# simple-todo-api-12438-12447

Backend: Flask app in todo_backend, default port 3001.

Database: Local file-based SQLite database (todos.db) created automatically on first run. No external DB or environment variables are required.

To run locally:
1) Install requirements: pip install -r todo_backend/requirements.txt
2) Start: python -m todo_backend.run (or python todo_backend/run.py)
3) Health check: GET http://localhost:3001/
4) Docs: http://localhost:3001/docs

Notes:
- The SQLite database file (todos.db) will be created in the todo_backend/ directory on first startup if it doesn't exist.
- CRUD endpoints remain the same: POST /todos, GET /todos, PUT /todos/{id}, DELETE /todos/{id}.