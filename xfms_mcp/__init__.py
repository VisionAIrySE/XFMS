"""MCP server for XFMS — wraps the hosted XFMS API as Model
Context Protocol tools.

Part of the Xpansion Framework. See https://xpansion.dev.

Install the optional extra to use this:

    pip install xfms[mcp]

Then run the server (stdio transport — what Claude Desktop, Cursor,
and other local MCP clients expect):

    xfms-mcp

Configuration env vars:
    XFMS_API_KEY        required — request at xpansion.dev/xfms/get-started
    XFMS_BASE_URL       optional — override the hosted endpoint

The hosted endpoint covers all inference cost end-to-end. BYOK was
dropped in v0.4 — no OpenRouter key required from callers.
"""

from xfms_mcp.server import main, server

__all__ = ["main", "server"]
