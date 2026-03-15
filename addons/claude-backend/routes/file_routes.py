"""File routes blueprint.

This blueprint will contain all file-related endpoints:
- GET /api/files/list
- GET /api/files/read

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for file routes
file_bp = Blueprint('files', __name__)

# Routes will be registered dynamically by api.py using:
# file_bp.add_url_rule()
