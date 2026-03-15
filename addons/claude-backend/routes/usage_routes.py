"""Usage routes blueprint.

This blueprint will contain all usage-related endpoints:
- GET /api/usage_stats
- GET /api/usage_stats/today
- POST /api/usage_stats/reset

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for usage routes
usage_bp = Blueprint('usage', __name__)

# Routes will be registered dynamically by api.py using:
# usage_bp.add_url_rule()
