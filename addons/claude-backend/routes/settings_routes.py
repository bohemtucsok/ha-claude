"""Settings routes blueprint.

This blueprint will contain all settings-related endpoints:
- GET /api/config
- POST /api/config
- GET /api/system_prompt
- POST /api/system_prompt
- GET /api/config/read
- POST /api/config/save
- GET /api/fallback_config
- POST /api/fallback_config
- GET /api/settings
- POST /api/settings

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for settings routes
settings_bp = Blueprint('settings', __name__)

# Routes will be registered dynamically by api.py using:
# settings_bp.add_url_rule()
