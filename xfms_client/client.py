"""HTTP client for the XFMS hosted API.

This is a thin wrapper. It takes your purpose, POSTs to /rank,
and returns the response. Nothing strategic lives here — the
math, the catalog, and the ranking logic all run on the hosted
side, including the inference call that figures out which
benchmarks matter for your purpose.

You only need an XFMS access token to use the hosted API (free,
request one at xpansion.dev/xfms/get-started). The hosted endpoint
covers its own inference cost — there's no OpenRouter key required.
Power users CAN supply one to route inference through their own
OpenRouter account, but it's optional.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

_DEFAULT_BASE_URL = "https://xfms.vercel.app"
_DEFAULT_TIMEOUT = 30.0


class XFMSError(Exception):
    """Raised when the API returns an error or the call fails."""


def _resolve_api_key(explicit: str | None) -> str:
    """Find the XFMS API key in: arg → env → secrets file."""
    if explicit:
        return explicit.strip()
    env = os.environ.get("XFMS_API_KEY", "").strip()
    if env:
        return env
    secrets_path = Path("~/.claude/secrets/xfms_api_key.txt").expanduser()
    if secrets_path.is_file():
        contents = secrets_path.read_text().strip()
        if contents:
            return contents
    raise XFMSError(
        "No XFMS API key found. Set the XFMS_API_KEY environment "
        "variable, or pass api_key=... to XFMSClient. Request one at "
        "https://xpansion.dev/xfms/get-started."
    )


def _resolve_openrouter_key(explicit: str | None) -> str | None:
    """Find the caller's OpenRouter key if one was provided.

    Returns None when no key is set anywhere — the hosted endpoint
    covers inference with its own key in that case. Power users
    can supply one via arg, env, or secrets file to route inference
    through their own OpenRouter account instead.
    """
    if explicit:
        return explicit.strip()
    env = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env:
        return env
    return None


class XFMSClient:
    """Client for the hosted XFMS API at xfms.vercel.app.

    Only one credential is required:

    - `api_key` — your XFMS access token. Free, request at
      xpansion.dev/xfms/get-started. Identifies your account for
      rate limiting and the Xpansion mailing list.

    Optional override:

    - `openrouter_api_key` — if you want the small inference call
      XFMS makes (to figure out which benchmarks matter for your
      purpose) to route through your OWN OpenRouter account. By
      default the hosted endpoint covers it with its own key, and
      you owe nothing for inference.
    """

    def __init__(
        self,
        api_key: str | None = None,
        openrouter_api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ):
        self._api_key = _resolve_api_key(api_key)
        self._or_key: str | None = _resolve_openrouter_key(openrouter_api_key)
        self._base_url = (
            base_url or os.environ.get("XFMS_BASE_URL") or _DEFAULT_BASE_URL
        ).rstrip("/")
        self._timeout = timeout
        self._http = httpx.Client(timeout=timeout)

    # ── context manager so `with XFMSClient() as x:` cleans up ─────────

    def __enter__(self) -> "XFMSClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # ── public API surface ─────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Confirm the hosted endpoint is reachable."""
        r = self._http.get(f"{self._base_url}/health")
        r.raise_for_status()
        return r.json()

    def rank(
        self,
        purpose: str,
        *,
        quality: float = 0.8,
        cost: float = 0.3,
        latency: float | None = None,
        privacy: float | None = None,
        capabilities: list[str] | None = None,
        primary: list[str] | None = None,
        top_n: int = 5,
        infer_quality_weights: bool = True,
        infer_capabilities: bool = True,
        leaf_priorities: dict[str, float] | None = None,
        decision_source: str = "manual",
        explain: bool = True,
        ab: bool = False,
        clarify_when_ambiguous: bool = False,
    ) -> dict[str, Any]:
        """Rank the catalog for a stated purpose.

        `primary` — list of branch names ("cost", "quality", "latency",
            "privacy") to mark as primary tier. When primary is set, the
            engine switches from weighted-sum blending to lexicographic
            ordering — the primary dimension is the sole ranking axis
            and other dimensions only break ties. Sacrosanct user
            preference: "I want the cheapest model" actually picks the
            cheapest.

        `ab` — when True, hits the /rank-ab endpoint which runs the top
            3 picks against 5 generated test queries (expanding to 10
            or 15 on incongruity) and returns the result with an
            `ab_result` block containing real-world cost/latency stats
            plus plain-English commentary about who won what.
        """
        primary_set = {b.strip().lower() for b in (primary or []) if b and b.strip()}
        decisions: list[dict[str, Any]] = []
        if capabilities:
            decisions.append({
                "branch": "capability",
                "type": "required",
                "required": list(capabilities),
            })
        else:
            decisions.append({"branch": "capability", "type": "dontcare"})

        def _weight_dec(branch: str, value: float) -> dict[str, Any]:
            d: dict[str, Any] = {"branch": branch, "type": "weight", "value": value}
            if branch in primary_set:
                d["tier"] = "primary"
            return d

        decisions.append(_weight_dec("quality", quality))
        decisions.append(_weight_dec("cost", cost))
        decisions.append(
            _weight_dec("latency", latency) if latency is not None
            else {"branch": "latency", "type": "dontcare"}
        )
        decisions.append(
            _weight_dec("privacy", privacy) if privacy is not None
            else {"branch": "privacy", "type": "dontcare"}
        )

        body: dict[str, Any] = {
            "purpose": purpose,
            "decision_source": decision_source,
            "decisions": decisions,
            "top_n": top_n,
            "infer_quality_weights": infer_quality_weights,
            "infer_capabilities": infer_capabilities,
            "explain": explain,
            "clarify_when_ambiguous": clarify_when_ambiguous,
        }
        if leaf_priorities:
            body["leaf_priorities"] = leaf_priorities

        endpoint = "/rank-ab" if ab else "/rank"
        return self._post(endpoint, body)

    def pick(self, purpose: str, **kwargs: Any) -> dict[str, Any]:
        """Return only the top pick. Same shape as rank() with
        top_n=1, but returns the single model dict directly."""
        result = self.rank(purpose, top_n=1, **kwargs)
        models = result.get("models") or []
        if not models:
            raise XFMSError(
                "No model met the criteria. Full response: "
                + json.dumps(result, indent=2)[:500]
            )
        return models[0]

    def discover(self, purpose: str, **kwargs: Any) -> dict[str, Any]:
        """Walk the discovery tree without ranking. Useful for
        seeing which dimensions matter for a stated purpose before
        committing to weights."""
        body = {"purpose": purpose, "decision_source": "manual", **kwargs}
        return self._post("/discover", body)

    # ── transport ──────────────────────────────────────────────────────

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": "xfms-python-client/0.1",
        }
        if self._or_key:
            headers["X-OpenRouter-Key"] = self._or_key
        try:
            r = self._http.post(
                f"{self._base_url}{path}",
                headers=headers,
                json=body,
            )
        except httpx.HTTPError as e:
            raise XFMSError(f"network error calling {path}: {e}") from e

        if r.status_code == 401:
            raise XFMSError(
                "Authentication failed. Check XFMS_API_KEY (it must "
                "be a key issued by xpansion.dev/xfms/get-started)."
            )
        if r.status_code == 402:
            raise XFMSError(
                "Inference call failed at the hosted endpoint. If you "
                "supplied your own OpenRouter key, confirm it is valid "
                "and funded; otherwise this is a server-side issue at "
                "xfms.vercel.app — please report it."
            )
        if r.status_code == 429:
            raise XFMSError(
                "Rate limit hit. XFMS API keys are rate-limited; "
                "wait and retry, or contact russ@visionairy.biz for "
                "a higher limit."
            )
        if r.status_code >= 400:
            raise XFMSError(
                f"XFMS API error {r.status_code}: {r.text[:500]}"
            )
        return r.json()


# ── module-level convenience functions ────────────────────────────────


def rank(purpose: str, **kwargs: Any) -> dict[str, Any]:
    """One-shot rank without managing a client object."""
    with XFMSClient() as c:
        return c.rank(purpose, **kwargs)


def pick(purpose: str, **kwargs: Any) -> dict[str, Any]:
    """One-shot pick (top-1) without managing a client object."""
    with XFMSClient() as c:
        return c.pick(purpose, **kwargs)
