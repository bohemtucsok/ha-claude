"""OAuth routes blueprint.

This blueprint will contain all OAuth-related endpoints:
- GET /api/oauth/codex/start
- POST /api/oauth/codex/exchange
- GET /api/oauth/codex/status
- POST /api/oauth/codex/revoke
- GET /api/oauth/copilot/start
- GET /api/oauth/copilot/poll
- GET /api/oauth/copilot/status
- POST /api/oauth/copilot/revoke
- POST /api/session/claude_web/store
- GET /api/session/claude_web/status
- POST /api/session/claude_web/clear
- POST /api/session/chatgpt_web/store
- GET /api/session/chatgpt_web/status
- POST /api/session/chatgpt_web/clear

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for OAuth routes
oauth_bp = Blueprint('oauth', __name__)

# Routes will be registered dynamically by api.py using:
# oauth_bp.add_url_rule()
