# Changelog

All notable changes to the XFMS client library are documented here.
Versioning follows SemVer once we cut v1.0; pre-1.0 versions are
allowed to introduce breaking changes with a `BREAKING:` note.

---

## [0.3.2] — 2026-05-17 — names-first phrasing in Xpansion section

Docs-only patch. Caught on the 0.3.1 PyPI page review: the
sibling-module list led with acronyms (`XFFI`, `XFBA`, `XSIA`, ...)
instead of the plain-English canonical names. Non-technical builders
read acronyms as jargon — the XFVE voice rule applies to docs too.

### Changed

- README's "Part of the Xpansion Framework" section now leads with
  the canonical full names (Finite Intent, Boundary Auditor,
  Systemic Impact Analysis, Token Conservation, Execution Audit,
  Memory Tree, Security Auditor). The acronym appears in parens as
  a code reference. Added Memory Tree and Security Auditor (omitted
  in 0.3.1).

---

## [0.3.1] — 2026-05-17 — README polish + Claude Code coverage

Docs-only release. No code changes; bumped to refresh the PyPI
project page after substantial README updates.

### Changed

- README hero example refreshed to show the actual 0.3.0 output
  (ranked picks with provider routes, inferred quality weights, plain-
  English explanation, A/B probe block with commentary).
- "What's new in 0.3.0" callout added near the top so the launch
  features (`--primary`, `--ab`, `--strict-priorities`, latent-
  requirement suggestions, deterministic cache) are visible without
  scrolling.
- MCP section now leads with **Claude Code** (Anthropic's official
  CLI) and shows the one-line `claude mcp add xfms` install command.
  Desktop and Cursor follow.
- "Part of the Xpansion Framework" section materially expanded —
  explains what Xpansion is, names the sibling modules (Dispatch,
  XFFI, XFBA, XSIA, XFTC, XFXA), and frames XFMS as the first
  module to ship public + free.

---

## [0.3.0] — 2026-05-17 — trust spine + priority tiers + A/B probe

The big launch-day release. Three architectural additions land together
and the engine is materially smarter about who it picks and why.

### Added

- **Priority tiers (`--primary`)** — mark a dimension as the SOLE
  ranking axis. When set, the engine switches from weighted-sum
  blending to lexicographic ordering: primary wins, other dimensions
  only break ties. Sacrosanct user preference. `xfms rank "cheapest
  model" --primary cost` now actually picks the cheapest, not the
  cheapest-weighted blend.
- **A/B probe (`--ab`)** — after ranking, run the top 3 picks against
  5 generated test queries (expanding to 10 or 15 on incongruity) and
  surface real-world cost/latency stats plus plain-English commentary.
  Slower (~5-30s) but grounds the recommendation in actual model
  behavior, not just benchmarks. Powered by the new `/rank-ab`
  endpoint.
- **Latent-requirement suggestions** — heuristic depth probe surfaces
  capabilities the user didn't ask for but probably needs (e.g.,
  streaming for real-time chat). The Koinonos lesson, made visible.
- **Trust spine** — internal: every LLM call now routes through a
  unified wrapper with temperature locked at 0, a Supabase-backed
  content cache, and a Pydantic schema requiring structured reasoning
  steps before any answer field. Same input always produces the same
  recommendation. Eliminates the "same question, different answer"
  failure mode beta users flagged.
- **CLI clarity** — valid enum lists (capabilities + quality leaves)
  shown inline in `--help`. Description fields explain when to use
  `rank` vs `pick`. Output labels match the flag names. Latent-
  requirement suggestions surfaced in the response.

### Changed

- README updated with examples for `--primary`, `--ab`, and
  latent-requirement suggestions.
- `xfms_client.rank()` accepts `primary` and `ab` parameters.

### Internal

- Engine: trust spine landed in commits `dffecb9` and `51f845e`.
  Priority tiers + heuristic depth probe in `0625106`. A/B runner +
  endpoint in `d98f556`. Vercel route allowlist in `3925123`.
- 301+ engine tests passing.

---

## [0.1.0] — 2026-05-16 — initial public release

First public release of the XFMS client.

### Added

- **`XFMSClient`** — Python class for calling the hosted XFMS API
  with BYOK semantics. Carries both an XFMS access key and the
  caller's OpenRouter key; the OpenRouter key is sent per-request
  so inference cost rides with the caller.
- **`xfms` CLI** — `rank`, `pick`, `health` subcommands. Configures
  via env vars (`XFMS_API_KEY`, `OPENROUTER_API_KEY`) or flags.
- **Convenience functions** — `rank()` and `pick()` at the module
  level for one-shot use without managing a client.
- **15 client tests** covering env-var resolution, request shape,
  leaf-priorities pass-through, error handling (401, 402, 429,
  network errors), and version exports.
- **`docs/methodology.md`** — the standing answer to "why should I
  trust the picks?". Four principles, eight benchmark sources,
  score normalization, name resolution, coverage gates.
- **`docs/xpansion-overview.md`** — the broader Xpansion Framework
  story in builder-value terms.

### Honest scope

- The client is a thin HTTP wrapper. The recommender engine, score
  catalog, and ingestion pipeline run on the hosted side and are
  not open source.
- The repository ships ~250 lines of client code + docs. The whole
  thing is meant to be readable in one sitting.
- BYOK is the contract — there is no free-tier inference. Sign-up
  is free; running picks costs whatever your OpenRouter charges
  for the inference call (~$0.001).

---

## Versioning policy

Pre-1.0 (current): breaking changes allowed but must be flagged
with `BREAKING:` in the changelog entry. Client-side API contract
breaks (e.g. function signatures changing) get called out
prominently.

Post-1.0 (planned): strict SemVer. Breaking changes only in major
versions.
