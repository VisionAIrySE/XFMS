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
Top picks:
   1. 0.842  GPT-5.5                 (openai/gpt-5.5)         via OpenAI
   2. 0.811  Claude Opus 4.7         (anthropic/claude-opus-4.7) via Anthropic
   3. 0.798  Gemini 3.1 Pro Preview  (google/gemini-3.1-pro-preview) via Google

Inferred quality weights from your purpose:
  • structured_output_reliability  42.0%  ← BigCodeBench, Aider Polyglot
  • instruction_following          28.0%  ← LiveBench, Tau-Bench
  • factuality                     20.0%  ← MMLU, GPQA
  • coherence                      10.0%  ← LongBench

─── Explanation ───
Picked GPT-5.5: strong on structured output and instruction following —
the two dimensions that dominate code-edit work. Beats Claude on Aider
Polyglot and matches it on LiveBench reasoning, at roughly 60% of the
per-token cost.
```

Want to see how the picks actually behave on your kind of query? Add `--ab`:

```
─── A/B probe ───
Ran 5 test queries against the top picks.
  • GPT-4o-mini  avg_latency=5579 ms  total_cost=$0.00156  successes=5
  • GPT-5.5      avg_latency=8190 ms  total_cost=$0.07640  successes=5
  • GPT-5.4      avg_latency=8783 ms  total_cost=$0.03493  successes=5

Commentary:
  Across 5 real test queries, GPT-4o-mini was both cheapest ($0.0016 total)
  and fastest (5579 ms avg). Clear winner — 98% cheaper and 36% faster
  than the slowest pick.
```

---

## What XFMS does for you

Beyond ranking, XFMS gives you these levers to honor what you actually meant:

- **`--primary <branch>`** — sacrosanct user preference. When you say
  *"cheapest model, period"*, the engine switches to lexicographic
  ranking: cost wins, other dimensions only break ties. No more
  weighted-blend surprises.
- **`--ab`** — runs the top 3 picks against 5 real test queries
  (expanding to 10 or 15 if results trade off) and surfaces commentary
  on who won what. Grounds the recommendation in actual model behavior,
  not just benchmarks.
- **`--strict-priorities`** — when you name two co-equal drivers
  ("cheap but high quality too"), the engine refuses to silently
  blend; it asks you which way to break the tie.
- **Latent-requirement suggestions** — engine surfaces capabilities
  you didn't ask for but probably need (streaming for real-time chat,
  vision for OCR), so you don't get burned by what you didn't know.
- **Deterministic by design** — every internal model call is content-
  cached; same input always returns the same answer. The "I got
  different picks for the same question" failure mode is gone.

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

That's it — the hosted endpoint covers inference. There's no
OpenRouter key to provision, no per-pick cost on you, no second
account to manage. Configure the one key:

```bash
export XFMS_API_KEY=xfms_live_...
```

(Power users CAN supply their own OpenRouter key via
`OPENROUTER_API_KEY` or `--openrouter-key` to route inference
through their own account — but it's purely optional.)

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

When you actually mean **"the cheapest model, period"** — make cost the
*primary* dimension and the engine switches to lexicographic ordering.
The cheapest model wins; other dimensions only break ties:

```bash
xfms rank "cheapest model that can parse a 5-page PDF" --primary cost
```

When you want to **see how the picks actually behave on your kind of query**
— add `--ab` and the engine runs the top 3 picks against 5 generated test
queries (expanding to 10 or 15 if the picks trade wins), then surfaces
real-world cost/latency plus plain-English commentary:

```bash
xfms rank "summarizing 50-page commercial leases" --ab
```

The A/B output ends with a one-paragraph summary along the lines of *"On
the test queries, Model X was 60% cheaper but Model Y was 30% faster —
they trade off."* You decide.

If XFMS detects something you didn't ask for but probably need — like
streaming for a real-time chat use case — it surfaces a **latent-
requirement suggestion** at the top of the response. The Koinonos lesson:
sometimes you don't know what you don't know. Accept and re-run with `-c`,
or ignore and ship.

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

## Use it inside Claude Code, Cursor, or any MCP client

XFMS speaks **Model Context Protocol** (MCP) — the standard your
AI assistant uses to call external tools. Once connected, you can
ask the assistant *"which model should I use for OCR on shipping
manifests?"* and it calls XFMS for you. No leaving the chat. No
copy-pasting between windows.

### Hosted install — one line, no install required

The XFMS engine hosts the MCP server itself at
**`https://xfms.vercel.app/mcp/`**. No `pip install`, no
OpenRouter key — just point your MCP client at the URL:

**Claude Code:**

```bash
claude mcp add xfms --transport http https://xfms.vercel.app/mcp/ \
  --header "Authorization: Bearer xfms_live_your_key_here"
```

**Cursor** (`~/.cursor/mcp.json`) — or paste through *Settings → MCP*:

```json
{
  "mcpServers": {
    "xfms": {
      "url": "https://xfms.vercel.app/mcp/",
      "headers": {
        "Authorization": "Bearer xfms_live_your_key_here"
      }
    }
  }
}
```

**Continue / Cline / any other MCP host** — same URL + bearer header
pattern; check your host's docs for the JSON config shape.

You need one key — the free XFMS access token. Request it at
[xpansion.dev/xfms/get-started](https://xpansion.dev/xfms/get-started)
or via [curl](https://github.com/VisionAIrySE/XFMS#install); it
arrives by email after you click the confirmation link. The hosted
endpoint pays for the small inference call XFMS makes internally —
when your host supports MCP sampling (Claude Code does), the call
routes through *your host's* LLM and we don't pay either. Either
way, you don't.

Restart your client, then ask it:

> *"Use XFMS to pick a model for summarizing long legal contracts."*

### Offline install — pip-installed local MCP server

For air-gapped environments or local development, the `xfms`
Python package also ships a stdio MCP server you can install
locally:

```bash
pip install 'xfms[mcp]'
```

Then register it with your host (uses `xfms-mcp` as the command):

```bash
claude mcp add xfms -- xfms-mcp \
  --env XFMS_API_KEY=xfms_live_your_key_here
```

The local server hits the same hosted endpoint, so the inference-cost
behavior is identical to the hosted MCP install above.

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

XFMS doesn't stand alone — it's the model-selection layer of the
**[Xpansion Framework](https://xpansion.dev)**.

### The Xpansion thesis

> **Humans communicate with intent compressed by contextual experience.
> AI simply predicts patterns in language. Xpansion is the execution
> layer that bridges them.**

Every sentence a human types carries lifetimes of context that the
speaker assumes the other side will decompress — what counts as "good
enough," which constraints are non-negotiable, what failures last
month taught them, what their house style demands. AI doesn't share
that context. It predicts patterns in language, filling in the gaps
with whatever's plausible to its training data. The result reads as
plausible but isn't intent-honoring: sessions lose context, security
holes ship silently, contracts break without warning, and there's no
way to verify that what was built actually matches what was asked
for. **They don't know what they don't know, and neither does AI.**

Xpansion closes the gap. It **decompresses finite intent upfront**,
**enforces it through code-driven AI behavior**, and **delivers
binary-verified results against the intent across persistent
memory** that survives every session boundary.

### Model Source — the model-selection enforcement

When you say *"the best model for this task"*, you're compressing
a lot: what counts as *best* depends on whether you care about
factual reasoning or coherent prose, whether cost matters more
than latency, whether you actually need vision or just text,
whether the call has to stream, whether a particular benchmark
dominates your real workload. AI on its own predicts the pattern
— *what model do most people pick for queries that look like
this?* — and gives you a plausible-sounding answer that's often
wrong for *you*.

XFMS does the decompression. It takes your stated purpose, infers
which benchmarks actually map to it, honors your stated primary
preferences without silently overriding them, surfaces the latent
requirements you didn't know to ask about (streaming for real-time
chat, vision for OCR), and probes the top picks against your real
query to verify the recommendation — not predict it. Then it
tells you, in plain English, why it picked what it picked.

### One module per enforcement

The rest of the Xpansion stack enforces the same decompress-
enforce-verify contract for different parts of the work:

- **Dispatch** (`Dispatch`) — runtime task router. Watches what
  kind of work you're doing and routes it to the right tool.
- **Finite Intent** (`XFFI`) — turns *"build me a feature"* into a
  finite spec with binary terminals *before* any code gets written.
  Stops scope drift at the source.
- **Boundary Auditor** (`XFBA`) — checks every code edit against
  contracts. Stops broken function signatures and mismatched types
  from ever reaching production.
- **Systemic Impact Analysis** (`XSIA`) — maps the blast radius of
  a proposed change before it lands. Tells you what else might
  break.
- **Token Conservation** (`XFTC`) — manages how much of the
  conversation has to stay in the assistant's working memory.
  Prevents context loss in long sessions.
- **Execution Audit** (`XFXA`) — verifies every promise from the
  spec was actually met before declaring a task done. The final
  binary check.
- **Memory Tree** (`XFMT`) — session snapshots that stay
  searchable across conversations. Your assistant remembers what
  you decided last week.
- **Security Auditor** (`XFSA`) — static + AI security scanning on
  every code edit. Catches secrets, injection paths, and unsafe
  patterns before they ship.

The full picture, with the rest of the modules, lives at
[xpansion.dev](https://xpansion.dev).

**Xpansion is in pre-signup right now.** Early access and founding
licenses are open at [xpansion.dev](https://xpansion.dev). XFMS is
the first piece to ship public + free — the rest follow.

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
