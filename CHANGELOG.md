# Changelog

All notable changes to the XFMS client library are documented here.
Versioning follows SemVer once we cut v1.0; pre-1.0 versions are
allowed to introduce breaking changes with a `BREAKING:` note.

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
