"""MCP routes blueprint.

This blueprint will contain all MCP (Model Context Protocol) endpoints:
- GET /api/mcp/servers
- GET /api/mcp/server/<server_name>/status
- POST /api/mcp/server/<server_name>/reconnect
- POST /api/mcp/server/<server_name>/start
- POST /api/mcp/server/<server_name>/stop
- GET /api/mcp/tools
- GET /api/mcp/diagnostics
- POST /api/mcp/test/<server_name>/<tool_name>
- POST /api/mcp/install
- GET /api/mcp/server/<server_name>/tools
- GET /api/mcp/conversations/<session_id>/messages

The actual route implementations are in api.py,
but they will be registered through this blueprint.
"""

from flask import Blueprint

# Create blueprint for MCP routes
mcp_bp = Blueprint('mcp', __name__)

# Routes will be registered dynamically by api.py using:
# mcp_bp.add_url_rule()
