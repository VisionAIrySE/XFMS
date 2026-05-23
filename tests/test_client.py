"""Tests for the XFMS client library.

These tests mock the HTTP layer so they run offline. The point is
to verify the request shape, the env-var resolution, and the error
handling — not to test the hosted API itself.
"""

from __future__ import annotations

import json
import os
import pytest
import httpx

from xfms_client import XFMSClient, XFMSError, __version__


# ── helpers ──────────────────────────────────────────────────────────


class _MockTransport(httpx.BaseTransport):
    """Captures requests + returns canned responses for testing."""

    def __init__(self, status: int = 200, body: dict | None = None,
                 raise_exc: Exception | None = None):
        self.status = status
        self.body = body or {"status": "ok", "models": [], "catalog_size": 0,
                              "filtered_out": 0}
        self.raise_exc = raise_exc
        self.calls: list[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if self.raise_exc:
            raise self.raise_exc
        return httpx.Response(
            self.status,
            content=json.dumps(self.body).encode(),
            request=request,
            headers={"content-type": "application/json"},
        )


def _client_with_transport(transport: _MockTransport,
                           **env: str) -> XFMSClient:
    """Build a client that uses the mock transport."""
    for k, v in env.items():
        os.environ[k] = v
    os.environ.setdefault("XFMS_API_KEY", "test-xfms-key")
    c = XFMSClient()
    c._http = httpx.Client(transport=transport)
    return c


# ── version ──────────────────────────────────────────────────────────


def test_version_is_exported():
    assert isinstance(__version__, str)
    assert __version__.count(".") >= 1


# ── env var resolution ──────────────────────────────────────────────


def test_missing_xfms_key_raises_helpful_error(monkeypatch):
    monkeypatch.delenv("XFMS_API_KEY", raising=False)
    # also block the secrets file fallback
    monkeypatch.setattr(
        "xfms_client.client.Path",
        lambda *_: type("FakePath", (), {
            "expanduser": lambda self: self,
            "is_file": lambda self: False,
        })(),
    )
    with pytest.raises(XFMSError, match="No XFMS API key found"):
        XFMSClient()


def test_explicit_api_key_wins_over_env(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "env-key")
    c = XFMSClient(api_key="explicit-key")
    assert c._api_key == "explicit-key"


def test_base_url_defaults_to_hosted(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    monkeypatch.delenv("XFMS_BASE_URL", raising=False)
    c = XFMSClient()
    assert c._base_url == "https://xfms.xpansion.dev"


def test_base_url_env_override(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    monkeypatch.setenv("XFMS_BASE_URL", "http://localhost:8000")
    c = XFMSClient()
    assert c._base_url == "http://localhost:8000"


# ── request shape ────────────────────────────────────────────────────


def test_rank_sends_xfms_auth_header(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "xfms_live_abc")
    t = _MockTransport(body={"status": "ranked", "models": [
        {"model_id": "openai/gpt-5.5", "name": "GPT-5.5", "total_score": 0.9}
    ], "catalog_size": 1, "filtered_out": 0})
    c = _client_with_transport(t)
    c.rank("test purpose")
    assert t.calls, "request was not sent"
    req = t.calls[-1]
    assert req.headers["authorization"] == "Bearer xfms_live_abc"
    # BYOK was dropped in v0.4 — no OR header should ever be sent.
    assert "x-openrouter-key" not in {h.lower() for h in req.headers.keys()}


def test_rank_body_includes_required_decisions(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(body={"status": "ranked", "models": [],
                              "catalog_size": 0, "filtered_out": 0})
    c = _client_with_transport(t)
    c.rank("test", quality=0.95, cost=0.1, capabilities=["vision"])
    body = json.loads(t.calls[-1].content)
    branches = {d["branch"]: d for d in body["decisions"]}
    assert branches["capability"]["type"] == "required"
    assert branches["capability"]["required"] == ["vision"]
    assert branches["quality"]["value"] == 0.95
    assert branches["cost"]["value"] == 0.1
    assert branches["latency"]["type"] == "dontcare"
    assert body["decision_source"] == "manual"


def test_rank_carries_leaf_priorities(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(body={"status": "ranked", "models": [],
                              "catalog_size": 0, "filtered_out": 0})
    c = _client_with_transport(t)
    c.rank("test", leaf_priorities={"factuality": 1.0})
    body = json.loads(t.calls[-1].content)
    assert body["leaf_priorities"] == {"factuality": 1.0}


def test_pick_returns_first_model(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(body={
        "status": "ranked",
        "models": [
            {"model_id": "openai/gpt-5.5", "name": "GPT-5.5", "total_score": 0.9},
            {"model_id": "anthropic/claude-opus-4.7", "name": "Claude Opus", "total_score": 0.85},
        ],
        "catalog_size": 2, "filtered_out": 0,
    })
    c = _client_with_transport(t)
    m = c.pick("test")
    assert m["model_id"] == "openai/gpt-5.5"


def test_pick_raises_on_empty_picks(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(body={"status": "low_confidence", "models": [],
                              "catalog_size": 0, "filtered_out": 0})
    c = _client_with_transport(t)
    with pytest.raises(XFMSError, match="No model"):
        c.pick("test")


# ── error handling ───────────────────────────────────────────────────


def test_401_raises_auth_error(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(status=401, body={"detail": "bad token"})
    c = _client_with_transport(t)
    with pytest.raises(XFMSError, match="Authentication failed"):
        c.rank("test")


def test_402_raises_openrouter_error(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(status=402, body={"detail": "OR key rejected"})
    c = _client_with_transport(t)
    with pytest.raises(XFMSError, match="OpenRouter"):
        c.rank("test")


def test_429_raises_rate_limit_error(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(status=429, body={"detail": "slow down"})
    c = _client_with_transport(t)
    with pytest.raises(XFMSError, match="Rate limit"):
        c.rank("test")


def test_network_error_surfaces_cleanly(monkeypatch):
    monkeypatch.setenv("XFMS_API_KEY", "k")
    t = _MockTransport(raise_exc=httpx.ConnectError("connection refused"))
    c = _client_with_transport(t)
    with pytest.raises(XFMSError, match="network error"):
        c.rank("test")


def test_compare_posts_to_compare_endpoint_with_model_ids(monkeypatch):
    """The compare() method must hit /compare and pass through the
    supplied model_ids as-is — NOT call /rank or /rank-ab and let the
    engine pick its own candidates."""
    monkeypatch.setenv("XFMS_API_KEY", "k")
    body = {
        "status": "compared",
        "purpose": "schedule a meeting",
        "model_ids_requested": ["a/free", "b/free"],
        "model_ids_tested": ["a/free", "b/free"],
        "invalid_model_ids": [],
        "ab_result": {
            "test_queries": ["q1"],
            "aggregates": [],
            "cost_winner_id": "a/free",
            "latency_winner_id": "a/free",
            "overall_winner_id": "a/free",
            "commentary": "ok",
            "incongruity_detected": False,
            "queries_executed": 1,
        },
        "refusal_reason": None,
    }
    t = _MockTransport(status=200, body=body)
    c = _client_with_transport(t)

    result = c.compare(
        "schedule a meeting", ["a/free", "b/free"], primary=["cost"]
    )

    assert len(t.calls) == 1
    req = t.calls[0]
    assert req.url.path == "/compare"
    sent = json.loads(req.content.decode())
    assert sent["purpose"] == "schedule a meeting"
    assert sent["model_ids"] == ["a/free", "b/free"]
    assert sent["primary"] == ["cost"]
    assert sent["decision_source"] == "manual"
    assert result["status"] == "compared"
    assert result["model_ids_tested"] == ["a/free", "b/free"]
