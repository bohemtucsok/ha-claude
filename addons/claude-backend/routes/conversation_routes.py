"""Conversation routes blueprint.

This blueprint will contain all conversation-related endpoints:
- GET /api/conversations
- GET /api/conversations/<session_id>
- DELETE /api/conversations/<session_id>
- GET /api/snapshots
- POST /api/snapshots/restore
- DELETE /api/snapshots/<snapshot_id>
- GET /api/snapshots/<snapshot_id>/download
- POST /api/conversation/process

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for conversation routes
conversation_bp = Blueprint('conversations', __name__)

# Routes will be registered dynamically by api.py using:
# conversation_bp.add_url_rule()
