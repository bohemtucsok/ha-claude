"""Dashboard routes blueprint.

This blueprint will contain all dashboard-related endpoints:
- GET /dashboard_api/states
- GET /dashboard_api/history
- POST /dashboard_api/services/<domain>/<service>
- GET /custom_dashboards/<name>
- GET /api/dashboard_html/<name>
- GET /custom_dashboards

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

# Routes will be registered dynamically by api.py using:
# dashboard_bp.add_url_rule()
