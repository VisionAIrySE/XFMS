"""Command-line tool: `xfms rank "<purpose>"` and friends.

Wraps the Python client in an argparse interface so people can use
XFMS from the terminal without writing code.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .client import XFMSClient, XFMSError


def _format_rank(resp: dict[str, Any]) -> str:
    lines: list[str] = []

    # Strict-mode clarification (or vague-purpose clarification) short-circuits
    # the ranked-list shape and surfaces a question for the user instead.
    if resp.get("status") == "clarification_needed":
        lines.append("Clarification needed before XFMS can rank confidently:")
        reason = resp.get("clarification_reason") or ""
        if reason:
            lines.append(f"  Reason: {reason}")
        for q in resp.get("clarification_questions", []) or []:
            lines.append(f"  • {q}")
        return "\n".join(lines)

    lines.append(f"Status: {resp.get('status', '?')}")
    lines.append(
        f"Catalog: {resp.get('catalog_size', '?')} models — "
        f"{resp.get('filtered_out', 0)} dropped by capability filter"
    )

    mode = resp.get("ranking_mode")
    primary_branches = resp.get("primary_branches") or []
    if mode == "lexicographic" and primary_branches:
        lines.append(
            f"Ranking mode: lexicographic on {', '.join(primary_branches)} "
            "(your primary driver wins; other dimensions only break ties)"
        )

    ta = resp.get("tier_ambiguity")
    if ta and ta.get("branches"):
        lines.append("")
        lines.append("Tie-breaker question (you named multiple co-equal drivers):")
        if ta.get("question"):
            lines.append(f"  {ta['question']}")
        if ta.get("hint"):
            lines.append(f"  → {ta['hint']}")

    auto_caps = resp.get("auto_inferred_capabilities") or []
    if auto_caps:
        lines.append(f"Auto-inferred capabilities: {', '.join(auto_caps)}")
        rationale = resp.get("auto_inferred_capabilities_rationale")
        if rationale:
            lines.append(f"  Reason: {rationale}")

    latent = resp.get("latent_requirements") or []
    if latent:
        lines.append("")
        lines.append("Latent-requirement suggestions (you didn't ask, but maybe should):")
        for lr in latent:
            cap = lr.get("capability", "?")
            conf = lr.get("confidence", "medium")
            reason = lr.get("reason", "")
            lines.append(f"  • {cap}  [{conf} confidence]")
            if reason:
                lines.append(f"    {reason}")
        lines.append(
            "  → Re-run with -c " + " -c ".join(lr["capability"] for lr in latent) +
            " to enforce these as hard requirements."
        )

    banner = resp.get("banner")
    if banner:
        lines.append(banner)

    iw = resp.get("inferred_quality_weights")
    if iw:
        lines.append("")
        lines.append("Inferred quality weights from your purpose:")
        for w in iw:
            bms = ", ".join(w.get("contributing_benchmarks", [])[:3])
            lines.append(
                f"  • {w['leaf']:32s} {w['weight'] * 100:5.1f}%   ← {bms}"
            )

    lines.append("")
    lines.append("Top picks:")
    for i, m in enumerate(resp.get("models", []), start=1):
        prov = m.get("provider") or "-"
        lines.append(
            f"  {i:>2}. {m['total_score']:.3f}  {m['name']}  "
            f"({m['model_id']})  via {prov}"
        )

    ab = resp.get("ab_result")
    if ab and ab.get("queries_executed"):
        lines.append("")
        lines.append("─── A/B probe ───")
        lines.append(
            f"Ran {ab['queries_executed']} test queries against the top picks."
        )
        if ab.get("incongruity_detected"):
            lines.append("Incongruity detected: picks traded wins, probe expanded for confidence.")
        for a in ab.get("aggregates", []):
            lines.append(
                f"  • {a['model_name']:32s}  "
                f"avg_latency={a['avg_latency_ms']:>6.0f} ms  "
                f"total_cost=${a['total_cost_usd']:.5f}  "
                f"successes={a['success_count']}"
            )
        commentary = ab.get("commentary") or ""
        if commentary:
            lines.append("")
            lines.append("Commentary:")
            lines.append("  " + commentary)

    explanation = resp.get("explanation")
    if explanation:
        lines.append("")
        lines.append("─── Explanation ───")
        lines.append(explanation)
    return "\n".join(lines)


def _format_pick(model: dict[str, Any]) -> str:
    out: list[str] = [
        f"Pick: {model['name']}  ({model['model_id']})",
        f"Score: {model['total_score']:.3f}",
    ]
    prov = model.get("provider")
    if prov:
        out.append(f"Best provider route: {prov}")
    return "\n".join(out)


def _parse_leaf_priorities(raw: str | None) -> dict[str, float] | None:
    if not raw:
        return None
    out: dict[str, float] = {}
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise SystemExit(f"--leaf-priorities entry {part!r} missing '='")
        leaf, weight = part.split("=", 1)
        out[leaf.strip()] = float(weight.strip())
    return out or None


def _cmd_health(c: XFMSClient, args: argparse.Namespace) -> int:
    r = c.health()
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"Status: {r.get('status', '?')}")
        print(f"Mode:   {r.get('mode', '?')}")
    return 0


def _cmd_rank(c: XFMSClient, args: argparse.Namespace) -> int:
    r = c.rank(
        args.purpose,
        quality=args.quality,
        cost=args.cost,
        latency=args.latency,
        privacy=args.privacy,
        capabilities=args.capability or None,
        primary=args.primary or None,
        top_n=args.top_n,
        infer_quality_weights=not args.no_infer,
        infer_capabilities=not args.no_infer_caps,
        leaf_priorities=_parse_leaf_priorities(args.leaf_priorities),
        decision_source=args.source,
        explain=not args.no_explain,
        ab=getattr(args, "ab", False),
        clarify_when_ambiguous=getattr(args, "strict_priorities", False),
    )
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(_format_rank(r))
    return 0


def _cmd_pick(c: XFMSClient, args: argparse.Namespace) -> int:
    m = c.pick(
        args.purpose,
        quality=args.quality,
        cost=args.cost,
        latency=args.latency,
        privacy=args.privacy,
        capabilities=args.capability or None,
        primary=args.primary or None,
        infer_quality_weights=not args.no_infer,
        infer_capabilities=not args.no_infer_caps,
        leaf_priorities=_parse_leaf_priorities(args.leaf_priorities),
        decision_source=args.source,
        clarify_when_ambiguous=getattr(args, "strict_priorities", False),
    )
    if args.json:
        print(json.dumps(m, indent=2))
    else:
        print(_format_pick(m))
    return 0


_VALID_CAPABILITIES = (
    "vision", "audio_in", "image_out", "tool_use", "function_calling",
    "structured_outputs", "streaming", "context_window_min", "max_output_min",
)

_VALID_LEAVES = (
    "factuality", "coherence", "structured_output_reliability",
    "instruction_following", "creative_writing", "human_preference",
)

_VALID_PRIMARY_BRANCHES = ("cost", "quality", "latency", "privacy")


def _add_decision_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--capability", "-c", action="append", metavar="NAME",
        choices=list(_VALID_CAPABILITIES),
        help=(
            "Hard requirement: model must support this capability. "
            "Repeatable: -c vision -c tool_use. "
            "Valid: " + ", ".join(_VALID_CAPABILITIES) + "."
        ),
    )
    p.add_argument(
        "--quality", "-q", type=float, default=0.8,
        help="Quality weight, 0.0-1.0 (default 0.8). Maps to the `quality` column.",
    )
    p.add_argument(
        "--cost", type=float, default=0.3,
        help="Cost weight, 0.0-1.0 (default 0.3). Lower cost wins. Maps to the `cost` column.",
    )
    p.add_argument(
        "--latency", type=float, default=None,
        help="Latency weight, 0.0-1.0 (default don't care). Lower latency wins. Maps to the `latency` column.",
    )
    p.add_argument(
        "--privacy", type=float, default=None,
        help="Privacy weight, 0.0-1.0 (default don't care). Maps to the `privacy` column.",
    )
    p.add_argument(
        "--primary", action="append", metavar="BRANCH",
        choices=list(_VALID_PRIMARY_BRANCHES),
        help=(
            "Mark BRANCH as the SOLE ranking dimension (repeatable). When "
            "set, the engine switches to lexicographic ordering: the primary "
            "wins; other dimensions only break ties. "
            "Valid: " + ", ".join(_VALID_PRIMARY_BRANCHES) + ". "
            "Example: --primary cost (picks the cheapest)."
        ),
    )
    p.add_argument(
        "--source", default="manual",
        choices=["xffi", "discovery", "snapshot", "manual"],
        help="Where the decision values came from (default 'manual').",
    )
    p.add_argument(
        "--leaf-priorities", default=None, metavar="K=V,K=V",
        help=(
            "Override the LLM-inferred per-leaf quality weights. "
            "Format: 'factuality=0.5,instruction_following=0.5'. "
            "Valid leaves: " + ", ".join(_VALID_LEAVES) + "."
        ),
    )
    p.add_argument(
        "--no-infer", action="store_true",
        help="Skip per-leaf weight inference (use default leaf weights).",
    )
    p.add_argument(
        "--no-infer-caps", action="store_true",
        help="Skip capability auto-inference (no auto-promotion of dontcare).",
    )
    p.add_argument(
        "--strict-priorities", action="store_true",
        help=(
            "When the engine detects two or more co-equal drivers in your "
            "input (e.g. 'cheap but high quality too'), STOP and ask you "
            "which dimension breaks ties — instead of silently picking a "
            "weighted blend. Without this flag, the engine blends and "
            "surfaces the ambiguity as advisory text."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="xfms",
        description="XFMS — Xpansion Framework Model Source. Pick the right LLM for your task.",
    )
    p.add_argument("--base-url",
                   help="Override the XFMS server URL "
                        "(default: $XFMS_BASE_URL or https://xfms.vercel.app).")
    p.add_argument("--api-key",
                   help="Override the XFMS API key (default: $XFMS_API_KEY).")
    p.add_argument("--openrouter-key",
                   help="Override the OpenRouter key (default: $OPENROUTER_API_KEY).")
    p.add_argument("--json", action="store_true",
                   help="Emit raw JSON instead of human-readable output.")
    sub = p.add_subparsers(dest="command", required=True)

    health = sub.add_parser("health", help="Check the hosted endpoint is up.")
    health.set_defaults(func=_cmd_health)

    rank = sub.add_parser(
        "rank",
        help="Rank models for a purpose. Returns top N with full breakdown.",
        description=(
            "Returns a ranked shortlist of models with weights, scores, "
            "and the plain-English explanation. Use this when you want "
            "to see and compare alternatives. (Use `pick` instead when "
            "you just want a single answer.)"
        ),
    )
    rank.add_argument("purpose", help="What you're using the model for.")
    rank.add_argument("--top-n", "-n", type=int, default=5,
                      help="How many picks to return (default 5).")
    rank.add_argument("--no-explain", action="store_true",
                      help="Suppress the plain-English explanation.")
    rank.add_argument(
        "--ab", action="store_true",
        help=(
            "Run an A/B probe after ranking: hit the top 3 picks with "
            "5 generated test queries (expanding to 10 or 15 on "
            "incongruity) and return real-world cost/latency stats "
            "plus commentary on who won. Slower (~5-30s) but grounds "
            "the recommendation in actual model behavior."
        ),
    )
    _add_decision_args(rank)
    rank.set_defaults(func=_cmd_rank)

    pick = sub.add_parser(
        "pick",
        help="Return only the top pick (concise, no alternatives).",
        description=(
            "Returns a single best pick — concise output, no ranked list. "
            "Use this when you've already settled on the criteria and "
            "just want one answer. (Use `rank` to see and compare "
            "alternatives.)"
        ),
    )
    pick.add_argument("purpose", help="What you're using the model for.")
    _add_decision_args(pick)
    pick.set_defaults(func=_cmd_pick)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with XFMSClient(
            api_key=args.api_key,
            openrouter_api_key=args.openrouter_key,
            base_url=args.base_url,
        ) as client:
            return args.func(client, args)
    except XFMSError as e:
        print(f"xfms: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
