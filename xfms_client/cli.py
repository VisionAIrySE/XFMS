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
    lines.append(f"Status: {resp.get('status', '?')}")
    lines.append(
        f"Catalog: {resp.get('catalog_size', '?')} models — "
        f"{resp.get('filtered_out', 0)} dropped by capability filter"
    )
    auto_caps = resp.get("auto_inferred_capabilities") or []
    if auto_caps:
        lines.append(f"Auto-inferred capabilities: {', '.join(auto_caps)}")
        rationale = resp.get("auto_inferred_capabilities_rationale")
        if rationale:
            lines.append(f"  Reason: {rationale}")
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
        top_n=args.top_n,
        infer_quality_weights=not args.no_infer,
        infer_capabilities=not args.no_infer_caps,
        leaf_priorities=_parse_leaf_priorities(args.leaf_priorities),
        decision_source=args.source,
        explain=not args.no_explain,
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
        infer_quality_weights=not args.no_infer,
        infer_capabilities=not args.no_infer_caps,
        leaf_priorities=_parse_leaf_priorities(args.leaf_priorities),
        decision_source=args.source,
    )
    if args.json:
        print(json.dumps(m, indent=2))
    else:
        print(_format_pick(m))
    return 0


def _add_decision_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--capability", "-c", action="append",
                   help="Required capability (repeatable: -c vision -c tools)")
    p.add_argument("--quality", "-q", type=float, default=0.8,
                   help="Quality weight (default 0.8).")
    p.add_argument("--cost", type=float, default=0.3,
                   help="Cost weight (default 0.3).")
    p.add_argument("--latency", type=float, default=None,
                   help="Latency weight (default 'don't care').")
    p.add_argument("--privacy", type=float, default=None,
                   help="Privacy weight (default 'don't care').")
    p.add_argument("--source", default="manual",
                   choices=["xffi", "discovery", "snapshot", "manual"],
                   help="Decision-source attestation (default 'manual').")
    p.add_argument("--leaf-priorities", default=None,
                   help="Override LLM-inferred leaf weights. "
                        "Format: 'factuality=0.5,instruction_following=0.5'.")
    p.add_argument("--no-infer", action="store_true",
                   help="Skip per-leaf weight inference.")
    p.add_argument("--no-infer-caps", action="store_true",
                   help="Skip capability auto-inference.")


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

    rank = sub.add_parser("rank", help="Rank models for a purpose.")
    rank.add_argument("purpose", help="What you're using the model for.")
    rank.add_argument("--top-n", "-n", type=int, default=5,
                      help="How many picks to return (default 5).")
    rank.add_argument("--no-explain", action="store_true",
                      help="Suppress the plain-English explanation.")
    _add_decision_args(rank)
    rank.set_defaults(func=_cmd_rank)

    pick = sub.add_parser("pick", help="Return only the top pick.")
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
