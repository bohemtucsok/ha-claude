"""Agents routes blueprint.

This blueprint will contain all agent-related endpoints:
- GET /api/agents
- POST /api/agents
- GET /api/agents/<agent_id>
- PUT /api/agents/<agent_id>
- DELETE /api/agents/<agent_id>
- POST /api/agents/set
- GET /api/agents/channels
- PUT /api/agents/channels
- GET /api/agents/defaults
- PUT /api/agents/defaults

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for agents routes
agents_bp = Blueprint('agents', __name__)

# Routes will be registered dynamically by api.py using:
# agents_bp.add_url_rule()
