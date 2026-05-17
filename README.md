# XFMS — Xpansion Framework Model Source

[![PyPI](https://img.shields.io/pypi/v/xfms.svg?label=pypi&color=blue)](https://pypi.org/project/xfms/)
[![Python](https://img.shields.io/pypi/pyversions/xfms.svg)](https://pypi.org/project/xfms/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Xpansion Framework](https://img.shields.io/badge/part%20of-Xpansion%20Framework-black)](https://xpansion.dev)

**Pick the right LLM for your task — without the Twitter vibes.**

State what you're using the model for. XFMS aggregates evidence from
eight independent benchmark sources, normalizes it onto a common
scale, lets your intent decide which dimensions matter, and returns
a ranked shortlist with plain-English rationale for every pick.

XFMS is one module of the **[Xpansion Framework](https://xpansion.dev)** —
a unified architecture for governing AI-assisted work.

---

## What this repository is

A **thin Python client** and **command-line tool** for calling the
hosted XFMS API at `xfms.vercel.app`. About 250 lines of code. It
turns a one-liner into a ranked LLM shortlist.

What this repository is **not**: the recommender engine, the score
catalog, or the ingestion pipeline. Those run on the hosted service.
The methodology behind every pick is published in full at
[docs/methodology.md](docs/methodology.md) — every claim there maps
to code that runs at request time, you just don't run it locally.

---

## What you say:

> *"Fixing bugs in our Python codebase."*

## What you get:

```
My pick: GPT-5.5

Strong on structured output and instruction following — the two
dimensions that dominate code-edit work. Beats the Claude family on
Aider Polyglot and matches it on LiveBench reasoning, at roughly
60% of the per-token cost.

Alternatives:
2. claude-sonnet-4.6  — closer on coding quality, higher cost
3. gemini-3-pro       — fastest, slightly weaker on tool use

Inferred weights from your purpose:
  • structured_output_reliability  42.0%  ← BigCodeBench, Aider
  • instruction_following          28.0%  ← LiveBench, Arena
  • factuality                     20.0%  ← MMLU, GPQA
  • coherence                      10.0%  ← LongBench
```

---

## Install

```bash
pip install xfms
```

You need two free keys:

- **Xpansion Framework Model Source access key** — identifies you
  to the hosted API. Request one by submitting your email to the
  signup endpoint:

  ```bash
  curl -X POST https://xfms.vercel.app/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"you@yourdomain.com"}'
  ```

  You'll get a confirmation email; click the button inside and
  your API key arrives in a follow-up email.

- **OpenRouter key** — your BYOK (bring-your-own-key). XFMS makes a
  small LLM call per pick to figure out which benchmarks matter for
  your stated purpose. That call goes through *your* OpenRouter
  account, so your inference cost stays with you (~$0.001 per
  pick). Sign up at [openrouter.ai/keys](https://openrouter.ai/keys).

Configure them once:

```bash
export XFMS_API_KEY=xfms_live_...
export OPENROUTER_API_KEY=sk-or-v1-...
```

## Use

**Command line:**

```bash
xfms rank "writing a tight editorial under a budget"
```

```bash
xfms pick "fixing bugs in our Python codebase"
```

```bash
xfms rank "summarizing a long legal contract" --top-n 3
```

```bash
xfms rank "OCR a handwritten manifest" -c vision -c tool_use
```

**Python:**

```python
from xfms_client import XFMSClient

with XFMSClient() as xfms:
    result = xfms.rank("writing a tight editorial under a budget")
    print(result["models"][0]["name"])
```

Or the one-shot:

```python
from xfms_client import pick
print(pick("fixing bugs in our Python codebase")["name"])
```

---

## Use it inside Claude Desktop, Cursor, or any MCP client

XFMS ships with a built-in **Model Context Protocol** server, which
is just a fancy name for a small program your AI assistant can talk
to. Once it's connected, you can ask Claude Desktop or Cursor
something like *"which model should I use for OCR on shipping
manifests?"* and the assistant calls XFMS for you. No leaving the
chat. No copy-pasting.

Install the package with the MCP extra:

```bash
pip install 'xfms[mcp]'
```

Then drop this block into your client's config file:

**Claude Desktop** — `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

**Cursor** — `~/.cursor/mcp.json`, or paste through *Settings → MCP*:

```json
{
  "mcpServers": {
    "xfms": {
      "command": "xfms-mcp",
      "env": {
        "XFMS_API_KEY": "xfms_live_your_key_here",
        "OPENROUTER_API_KEY": "sk-or-v1-your_key_here"
      }
    }
  }
}
```

Both keys are **yours** — XFMS doesn't sit in the middle of your
inference. Get them here:

- **XFMS key** — free, [request via curl](https://github.com/VisionAIrySE/XFMS#install)
  or visit [xpansion.dev/xfms/get-started](https://xpansion.dev/xfms/get-started).
  Arrives by email after you click the confirmation link.
- **OpenRouter key** — your BYOK. XFMS makes one small classifier
  call per pick to figure out which benchmarks matter for your
  stated purpose. That call runs against *your* OpenRouter account,
  so the inference cost stays with you (~$0.001 per pick). Sign up
  free at [openrouter.ai/keys](https://openrouter.ai/keys).

Restart your client, then ask it:

> *"Use XFMS to pick a model for summarizing long legal contracts."*

Three tools are available to the assistant: **`rank`** (a ranked
shortlist), **`pick`** (the single best pick), and **`discover`**
(which quality dimensions matter for your purpose, without ranking).

**One-click install via Smithery** — the [Smithery registry](https://smithery.ai)
hosts a copy of this config so you can install without hand-editing
JSON. Listed shortly after launch.

---

## Override the system's inference

If you know which quality dimension matters most for your task, say
so — your preference always wins over the LLM's inference:

```bash
xfms rank "code refactor" --leaf-priorities "structured_output_reliability=1.0,factuality=0.5"
```

```python
xfms.rank(
    "code refactor",
    leaf_priorities={"structured_output_reliability": 1.0, "factuality": 0.5},
)
```

---

## Why BYOK

The hosted XFMS endpoint runs your purpose through a small language
model to figure out which benchmarks matter most for your task —
that's how the "inferred weights" block in the response gets built.

That model call goes through *your* OpenRouter account, not ours.
You pay for your own thinking; we pay for keeping the catalog
fresh. It's the right alignment of who's on the hook for what.

Typical cost per pick: about **$0.001** on OpenRouter (one short
classifier call).

---

## How XFMS picks — the four principles

Methodology in full at [`docs/methodology.md`](docs/methodology.md).
The short version:

1. **No provider self-reports.** Every score comes from a
   third-party evaluator running the same protocol across every
   model.
2. **No single-source dependence.** Eight independent benchmark
   sources contribute today; no single leaderboard determines a
   pick.
3. **User intent beats LLM inference.** The system infers weights
   from your purpose, but your stated `leaf_priorities` always
   override the inference.
4. **Honest gaps over invented signal.** Missing data is recorded
   as missing — no interpolation, no synthetic scores. Coverage
   gaps surface on every pick.

---

## Part of the Xpansion Framework

XFMS is one piece of a bigger architecture. The whole picture lives
at [`docs/xpansion-overview.md`](docs/xpansion-overview.md).

**Xpansion is in pre-signup right now.** Early access and founding
licenses are open at [xpansion.dev](https://xpansion.dev).

---

## Local development

```bash
git clone https://github.com/VisionAIrySE/XFMS.git
cd XFMS
python3 -m venv .venv
.venv/bin/pip install -e .[dev]
.venv/bin/python -m pytest tests/ -v
```

The tests mock the HTTP layer so they run offline — no API keys
needed to develop.

---

## License

This client library is MIT-licensed. The recommender engine, the
catalog, and the ingestion pipeline are not open source. See
[`NOTICE`](NOTICE) for the patent reservation language and the
relationship to the broader Xpansion Framework IP.

---

## Contact

- **Russ Wright** — russ@visionairy.biz
- **Xpansion Framework** — [xpansion.dev](https://xpansion.dev)
- **Security disclosures** — see [`SECURITY.md`](SECURITY.md)
