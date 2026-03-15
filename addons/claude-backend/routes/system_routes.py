"""System routes blueprint.

This blueprint will contain all system-related endpoints:
- GET /api/system/features
- GET /api/ha_logs
- POST /api/browser-errors
- GET /api/browser-errors
- POST /api/addon/restart

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for system routes
system_bp = Blueprint('system', __name__)

# Routes will be registered dynamically by api.py using:
# system_bp.add_url_rule()
