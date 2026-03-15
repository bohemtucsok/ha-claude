"""Memory routes blueprint.

This blueprint will contain all memory-related endpoints:
- GET /api/memory
- GET /api/memory/search
- GET /api/memory/stats
- DELETE /api/memory/<conversation_id>
- POST /api/memory/cleanup
- POST /api/memory/clear

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for memory routes
memory_bp = Blueprint('memory', __name__)

# Routes will be registered dynamically by api.py using:
# memory_bp.add_url_rule()
