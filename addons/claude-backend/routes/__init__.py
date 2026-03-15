"""Blueprint registration for Flask routes."""

from flask import Flask
from routes.chat_routes import chat_bp


def register_blueprints(app: Flask) -> None:
    """Register all Flask blueprints with the app.

    This function is called during app initialization to set up route blueprints.
    Currently registers the chat blueprint.
    Additional blueprints will be registered in future phases.
    """
    # Register chat routes blueprint
    app.register_blueprint(chat_bp)
