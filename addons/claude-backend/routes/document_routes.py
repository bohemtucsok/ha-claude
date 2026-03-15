"""Document routes blueprint.

This blueprint will contain all document-related endpoints:
- POST /api/documents/upload
- GET /api/documents
- GET /api/documents/<doc_id>
- GET /api/documents/search
- DELETE /api/documents/<doc_id>
- GET /api/documents/stats
- POST /api/rag/index
- GET /api/rag/search
- GET /api/rag/stats

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for document routes
document_bp = Blueprint('documents', __name__)

# Routes will be registered dynamically by api.py using:
# document_bp.add_url_rule()
