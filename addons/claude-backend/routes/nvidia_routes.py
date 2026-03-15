"""NVIDIA routes blueprint.

This blueprint will contain all NVIDIA-related endpoints:
- POST /api/nvidia/test_model
- POST /api/nvidia/test_models

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for NVIDIA routes
nvidia_bp = Blueprint('nvidia', __name__)

# Routes will be registered dynamically by api.py using:
# nvidia_bp.add_url_rule()
