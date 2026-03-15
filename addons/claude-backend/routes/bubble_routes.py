"""Bubble routes blueprint.

This blueprint will contain all Bubble-related endpoints:
- GET /api/bubble/status
- POST /api/bubble/register
- POST /api/set_model
- POST /api/bubble/device-id
- GET /api/bubble/config
- GET /api/bubble/devices
- POST /api/bubble/devices
- PATCH /api/bubble/devices/<device_id>
- DELETE /api/bubble/devices/<device_id>

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for Bubble routes
bubble_bp = Blueprint('bubble', __name__)

# Routes will be registered dynamically by api.py using:
# bubble_bp.add_url_rule()
