from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from dotenv import load_dotenv

from .routes.health import blp as health_blp
from .routes.todos import blp as todos_blp
from .db import init_db

# Initialize environment variables from .env if present
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# API and OpenAPI settings
app.config["API_TITLE"] = "Todo CRUD API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Delay DB initialization until after app creation to avoid import-time crashes.
# We keep an eager call here but with resilience (init_db is now tolerant of failures).
print("[app] Starting Todo CRUD API; initializing database schema (non-fatal if DB down)...")
init_db()

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(todos_blp)
