"""MCP server for XFMS — exposes the hosted XFMS API as Model
Context Protocol tools so AI assistants (Claude Desktop, Cursor,
Continue, Windsurf, etc.) can pick the right LLM for any stated
purpose without leaving the chat.

XFMS is one module of the Xpansion Framework — a unified
architecture for governing AI-assisted work. See
https://xpansion.dev for the full framework.

Three tools are exposed:

    rank      — return a ranked shortlist of LLMs for a purpose
    pick      — return the single best LLM for a purpose
    discover  — show which quality dimensions matter for a purpose,
                without ranking

All three call the hosted XFMS endpoint at xfms.vercel.app. The
caller's OpenRouter key is sent per request (BYOK) so the inference
cost stays with them.
"""

from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "xfms_mcp requires the optional 'mcp' extra. Install with: "
        "pip install xfms[mcp]"
    ) from e

from xfms_client import XFMSClient, XFMSError


server = FastMCP("xfms")


def _client() -> XFMSClient:
    """Build a fresh client per call so live env-var changes are
    picked up between tool invocations."""
    return XFMSClient()


# ── tools ─────────────────────────────────────────────────────────────


@server.tool()
def rank(
    purpose: str,
    top_n: int = 5,
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    """Rank LLMs for a stated purpose. Returns a shortlist with
    plain-English rationale per pick, plus the dimension weights
    XFMS inferred from the purpose.

    Use this when the user asks "which model should I use for
    [task]?" or wants to compare a few options before committing.
    Pass a concrete purpose, not a vague label — "fixing bugs in a
    Python codebase" works; "coding" does not.

    Args:
        purpose: One sentence describing what the model will be used
            for. Examples: "fixing bugs in a Python codebase",
            "summarizing long legal contracts", "OCR on handwritten
            shipping manifests".
        top_n: How many models to return. Default 5.
        capabilities: Optional list of required capabilities. Allowed
            values: "vision", "audio_in", "tool_use",
            "structured_outputs".
    """
    try:
        with _client() as c:
            return c.rank(
                purpose,
                top_n=top_n,
                capabilities=capabilities,
                decision_source="mcp",
            )
    except XFMSError as e:
        return {"error": str(e)}


@server.tool()
def pick(purpose: str) -> dict[str, Any]:
    """Return the single best LLM for a stated purpose. Use when
    the user wants a one-shot recommendation rather than a
    shortlist.

    Args:
        purpose: One sentence describing what the model will be used
            for.
    """
    try:
        with _client() as c:
            return c.pick(purpose, decision_source="mcp")
    except XFMSError as e:
        return {"error": str(e)}


@server.tool()
def discover(purpose: str) -> dict[str, Any]:
    """Show which quality dimensions matter for a stated purpose,
    WITHOUT ranking any models. Useful when the user wants to
    understand how XFMS interprets their purpose — which benchmarks
    will drive the recommendation — before committing to a pick.

    Args:
        purpose: One sentence describing the task.
    """
    try:
        with _client() as c:
            return c.discover(purpose, decision_source="mcp")
    except XFMSError as e:
        return {"error": str(e)}


# ── entry point ───────────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server over stdio. This is what Claude Desktop
    and Cursor invoke when the server is registered in their config."""
    server.run()


if __name__ == "__main__":  # pragma: no cover
    main()
