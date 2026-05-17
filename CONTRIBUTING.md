# Contributing to the XFMS client

Thanks for considering a contribution. Keep in mind that this
repository is the **client library** — a thin HTTP wrapper around
the hosted XFMS API. The recommender engine, scoring catalog, and
ingestion pipeline live elsewhere and are not open source.

That means **most product changes don't belong here.** Specifically:

- **Methodology changes** (how scores are aggregated, normalized,
  weighted) — happen on the engine side. They surface in this
  client as different responses, not different code. If you'd like
  to propose a methodology change, open an issue describing the
  problem and we'll evaluate it on the engine side.
- **New benchmark sources** — same as above. The catalog is curated
  on the engine side.
- **Catalog access** — not exposed through this client and won't be.

## What we welcome here

- Bug fixes in the HTTP client logic
- Better error messages
- New CLI flags / subcommands that map to existing API features
- Documentation, examples, onboarding fixes
- Performance improvements with before/after numbers
- Tests covering edge cases the existing suite misses
- Improvements to the methodology / Xpansion overview docs

## Setting up

```bash
git clone https://github.com/VisionAIrySE/XFMS.git
cd XFMS
python3 -m venv .venv
.venv/bin/pip install -e .[dev]
.venv/bin/python -m pytest tests/ -v
```

Tests run offline — they mock the HTTP layer. No API keys needed
for development.

## Submitting a change

1. **Open an issue first** for anything beyond a small docs or
   typo fix. A 5-minute discussion saves a 5-hour rewrite.
2. **Branch from `main`** with a short descriptive name.
3. **Write a test.** Every behavior change needs a test that fails
   before the fix and passes after it.
4. **Run the suite locally** before pushing. CI will run it too.
5. **Open a PR** against `main`.

## License of your contribution

By submitting a contribution, you agree that your contribution is
licensed under the project's [LICENSE](LICENSE) — the MIT License.

XFMS is part of the Xpansion Framework. The Xpansion Framework
methods and processes are subject to pending patent applications.
See [`NOTICE`](NOTICE) for details. Contributing to this client
library does not grant rights to the broader Xpansion IP.

## Conduct

Be direct, be kind, focus on the work.

## Reporting security issues

**Do not open a public issue for a vulnerability.** See
[`SECURITY.md`](SECURITY.md) for the private-disclosure process.

## Contact

- General questions: open a GitHub issue
- Maintainer: Russ Wright — russ@visionairy.biz
- Xpansion Framework: [xpansion.dev](https://xpansion.dev)
