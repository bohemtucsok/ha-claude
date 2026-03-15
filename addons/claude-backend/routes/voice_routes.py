"""Voice routes blueprint.

This blueprint will contain all voice-related endpoints:
- GET /api/voice/stats
- POST /api/voice/transcribe
- POST /api/voice/tts
- GET /api/voice/tts/providers

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for voice routes
voice_bp = Blueprint('voice', __name__)

# Routes will be registered dynamically by api.py using:
# voice_bp.add_url_rule()
