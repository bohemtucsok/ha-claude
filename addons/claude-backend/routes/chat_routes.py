"""Chat routes blueprint.

This blueprint will contain all chat-related endpoints:
- POST /api/chat
- POST /api/chat/stream
- POST /api/chat/abort
- POST /api/memory/clear

The actual route implementations are in api.py for now,
but they will be registered through this blueprint to avoid
circular imports and decouple route registration.
"""

from flask import Blueprint

# Create blueprint for chat routes
chat_bp = Blueprint('chat', __name__)

# Routes will be registered dynamically by api.py using:
# chat_bp.add_url_rule()
