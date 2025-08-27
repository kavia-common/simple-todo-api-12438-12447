#!/bin/bash
cd /home/kavia/workspace/code-generation/simple-todo-api-12438-12447/todo_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

