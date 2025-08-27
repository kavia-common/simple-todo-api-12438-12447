from app import app

"""
Entrypoint to run the Flask application.
Starts the server with default host 0.0.0.0 and port 3001 for container-based environments.
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
