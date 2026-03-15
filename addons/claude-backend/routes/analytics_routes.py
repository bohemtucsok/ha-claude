"""Analytics routes blueprint.

This blueprint will contain all analytics-related endpoints:
- GET /api/cache/semantic/stats
- POST /api/cache/semantic/clear
- GET /api/tools/optimizer/stats
- GET /api/quality/stats
- GET /api/image/stats
- POST /api/image/analyze

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for analytics routes
analytics_bp = Blueprint('analytics', __name__)

# Routes will be registered dynamically by api.py using:
# analytics_bp.add_url_rule()
