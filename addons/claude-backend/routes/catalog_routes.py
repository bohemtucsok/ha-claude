"""Catalog routes blueprint.

This blueprint will contain all catalog-related endpoints:
- GET /api/catalog/stats
- GET /api/catalog/models
- GET /api/get_models

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for catalog routes
catalog_bp = Blueprint('catalog', __name__)

# Routes will be registered dynamically by api.py using:
# catalog_bp.add_url_rule()
