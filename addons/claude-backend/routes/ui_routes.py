"""UI routes blueprint.

This blueprint will contain all UI-related endpoints:
- GET /
- GET /ui_bootstrap.js
- GET /ui_main.js
- GET /api/ui_ping
- GET /api/status

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for UI routes
ui_bp = Blueprint('ui', __name__)

# Routes will be registered dynamically by api.py using:
# ui_bp.add_url_rule()
