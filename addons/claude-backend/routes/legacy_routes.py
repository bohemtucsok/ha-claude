"""Legacy routes blueprint.

This blueprint will contain all legacy Home Assistant integration endpoints:
- GET /health
- GET /entities
- GET /entity/<entity_id>/state
- POST /message
- POST /service/call
- POST /execute/automation
- POST /execute/script
- POST /conversation/clear
- POST /api/alexa/webhook

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for legacy routes
legacy_bp = Blueprint('legacy', __name__)

# Routes will be registered dynamically by api.py using:
# legacy_bp.add_url_rule()
