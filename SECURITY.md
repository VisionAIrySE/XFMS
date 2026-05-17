# Security Policy

If you find a security issue in the XFMS client library — anything
that could expose caller API keys, leak data through the client, or
compromise a system that depends on the client — **please report
it privately first.** Do not open a public GitHub issue.

**Email:** russ@visionairy.biz

Include in the report:

- What the issue is, in plain English
- How to reproduce it (sample code, request, environment)
- What you think the impact is

You'll get a reply within **3 business days** acknowledging the
report. If the issue is confirmed, we'll work toward a fix and
coordinate disclosure with you before any public mention.

## What the client library handles that's sensitive

- **`XFMS_API_KEY`** — your access token for the hosted API.
  Anyone with this token can hit the API as you and use your rate
  limit / mailing list signup.
- **`OPENROUTER_API_KEY`** — your OpenRouter key. Leaking this
  lets someone burn through your OpenRouter balance.

The client reads these from environment variables (or a `.env`
file you load yourself). It never logs them, never sends them
anywhere except the configured `XFMS_BASE_URL`.

## Out of scope

These are not security issues for this repository:

- Bugs or vulnerabilities in the hosted XFMS API — report those
  privately to russ@visionairy.biz, but they're not addressable by
  changes to this repo.
- An LLM model returning low-quality picks. That's a methodology
  question; open a regular GitHub issue.
- The hosted demo endpoint being slow or rate-limited.

## Scope

This policy covers the client library code in this repository.
Vulnerabilities in upstream dependencies (httpx, etc.) should be
reported to those projects directly.
