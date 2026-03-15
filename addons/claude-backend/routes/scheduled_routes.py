"""Scheduled tasks routes blueprint.

This blueprint will contain all scheduled task-related endpoints:
- GET /api/scheduled/stats
- GET /api/scheduled/tasks
- POST /api/scheduled/tasks
- DELETE /api/scheduled/tasks/<task_id>
- POST /api/scheduled/tasks/<task_id>/toggle
- POST /api/agent/scheduler
- GET /api/agent/scheduler/sessions
- DELETE /api/agent/scheduler/session/<session_id>

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for scheduled task routes
scheduled_bp = Blueprint('scheduled', __name__)

# Routes will be registered dynamically by api.py using:
# scheduled_bp.add_url_rule()
