"""Messaging routes blueprint.

This blueprint will contain all messaging-related endpoints:
- GET /api/messaging/stats
- POST /api/telegram/message
- GET /api/messaging/chats
- GET /api/messaging/chat/<channel>/<user_id>
- DELETE /api/messaging/chat/<channel>/<user_id>
- POST /api/whatsapp/webhook

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for messaging routes
messaging_bp = Blueprint('messaging', __name__)

# Routes will be registered dynamically by api.py using:
# messaging_bp.add_url_rule()
