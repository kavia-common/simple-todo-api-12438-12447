# simple-todo-api-12438-12447

Backend: Flask app in todo_backend, default port 3001.

Environment variables required for DB connectivity (see todo_backend/.env.example):
- POSTGRES_URL
- POSTGRES_PORT
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB

To run locally:
1) Copy todo_backend/.env.example to todo_backend/.env and fill values.
2) Install requirements: pip install -r todo_backend/requirements.txt
3) Start: python -m todo_backend.run (or python todo_backend/run.py)
4) Health check: GET http://localhost:3001/
Docs: http://localhost:3001/docs