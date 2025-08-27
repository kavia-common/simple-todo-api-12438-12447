from http import HTTPStatus
from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify

from ..db import get_db_session
from ..schemas import TodoCreateSchema, TodoUpdateSchema, TodoSchema
from ..services.todos_service import list_todos, create_todo, update_todo, delete_todo, get_todo

blp = Blueprint(
    "Todos",
    "todos",
    url_prefix="/todos",
    description="CRUD operations for Todo items",
)


@blp.route("", methods=["GET", "POST"])
class TodosCollection(MethodView):
    """
    Handles listing all todos (GET) and creating a new todo (POST).
    """

    # PUBLIC_INTERFACE
    @blp.response(HTTPStatus.OK, TodoSchema(many=True), description="List all todos")
    def get(self):
        """Return list of all todos."""
        db = get_db_session()
        try:
            todos = list_todos(db)
            return todos
        finally:
            db.close()

    # PUBLIC_INTERFACE
    @blp.arguments(TodoCreateSchema, as_kwargs=True)
    @blp.response(HTTPStatus.CREATED, TodoSchema, description="Created todo")
    def post(self, title: str, description: str = "", status: str = "pending"):
        """
        Create a new todo item.

        Parameters:
        - title: string, required
        - description: string, optional
        - status: 'pending' | 'done', optional

        Returns:
        - JSON representation of the created todo, with HTTP 201.
        """
        db = get_db_session()
        try:
            todo = create_todo(db, title=title, description=description, status=status)
            return todo, HTTPStatus.CREATED
        except ValueError as ve:
            return jsonify({"message": str(ve)}), HTTPStatus.BAD_REQUEST
        finally:
            db.close()


@blp.route("/<int:todo_id>", methods=["PUT", "DELETE"])
class TodoItem(MethodView):
    """
    Handles updating and deleting a specific todo by ID.
    """

    # PUBLIC_INTERFACE
    @blp.arguments(TodoUpdateSchema)
    @blp.response(HTTPStatus.OK, TodoSchema, description="Updated todo")
    def put(self, json_body, todo_id: int):
        """
        Update an existing todo by id.

        Path params:
        - todo_id: integer

        Body:
        - any of title, description, status

        Returns:
        - JSON of updated todo on success, 404 if not found.
        """
        db = get_db_session()
        try:
            # Check existence first
            if get_todo(db, todo_id) is None:
                return jsonify({"message": "Todo not found"}), HTTPStatus.NOT_FOUND

            updated = update_todo(db, todo_id, json_body or {})
            if updated is None:
                return jsonify({"message": "Todo not found"}), HTTPStatus.NOT_FOUND
            return updated
        except ValueError as ve:
            return jsonify({"message": str(ve)}), HTTPStatus.BAD_REQUEST
        finally:
            db.close()

    # PUBLIC_INTERFACE
    @blp.alt_response(HTTPStatus.NO_CONTENT, description="Todo deleted")
    def delete(self, todo_id: int):
        """
        Delete a todo by id.

        Returns:
        - 204 No Content on success
        - 404 Not Found if the todo does not exist
        """
        db = get_db_session()
        try:
            ok = delete_todo(db, todo_id)
            if not ok:
                return jsonify({"message": "Todo not found"}), HTTPStatus.NOT_FOUND
            return "", HTTPStatus.NO_CONTENT
        finally:
            db.close()
