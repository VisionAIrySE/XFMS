# XF Model Source (XFMS)

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![smithery badge](https://smithery.ai/badge/russ-mwq9/xfms)](https://smithery.ai/servers/russ-mwq9/xfms)
[![Part of the Xpansion Framework](https://img.shields.io/badge/part%20of-Xpansion%20Framework-black)](https://xpansion.dev)

**Find the AI model your job really needs, and prove it on your own tasks.**

AI is specialized. There are 450+ models on [OpenRouter](https://openrouter.ai), and the one every vendor calls
"the best" was not measured on your job. XF Model Source works inside the assistant you already use
(Claude Code, Cursor, Cline, Continue, any MCP client) and does three things:

1. **Finds what your job needs.** It asks a few plain questions and turns your answers into the job's real
   requirements: what goes in, what must come back, the format, the cost ceiling, what must never happen.
2. **Narrows the field.** It checks every model against those requirements using independent test scores, each
   model's published capabilities and price, and the results of our own comparisons, then produces a shortlist.
3. **Proves it on your tasks.** A screening round runs about 12 likely models on one of your sample tasks.
   Any model that breaks a must-have is ruled out, and the best six run all your tasks. You get the winner,
   the reasons, and every answer so you can check it yourself.

Scores and claims can't tell you whether a model will follow your exact format or avoid inventing a detail.
So the test, not the leaderboard, makes the final call, and each shortlisted model shows how it has really
done in our own comparisons.

---

## Connect

The server is hosted. There is nothing to install. The address is:

**`https://xfms.xpansion.dev/mcp`**

- **Claude (claude.ai or the desktop app):** Settings, Connectors, Add custom connector, paste the address. Sign in
  with your email when it opens.
- **Claude Code:** run `claude mcp add model-source --transport http https://xfms.xpansion.dev/mcp`, then `/mcp`
  inside Claude Code to sign in.
- **Codex:** run `codex mcp add model-source --url https://xfms.xpansion.dev/mcp`, then
  `codex mcp login model-source` to sign in.
- **ChatGPT:** Settings, Connectors, Advanced, turn on Developer mode, then Create, paste the address and choose
  OAuth. Developer mode is only on some paid ChatGPT plans.
- **Cursor, Windsurf and other assistants:** add an HTTP MCP server at the address (Cursor: `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "model-source": { "url": "https://xfms.xpansion.dev/mcp" }
  }
}
```

- **An assistant that can't open a sign-in page:** sign in at <https://xfms.xpansion.dev/signin> and use the
  personal connection link from your account page as the server address. Treat it like a password.

Sign-in is free and needs only your email. Then ask your assistant: *"Help me pick an AI model for pulling the
invoice number, date, total and vendor out of invoices as JSON, about 2,000 a month. The cheapest one that gets
every field right."*

## What it costs

- **Discovery and the shortlist are free.** Sign-in is free and needs only your email.
- **Comparisons run on your own OpenRouter key,** usually a few cents. You see the most a comparison can cost
  before anything runs, and nothing runs until you say go. Add the key as an `X-OpenRouter-Key` header. It is
  used for that run and never stored.
- **XF Model Watch** (optional, from $19 a month) re-tests your saved jobs every week and emails you only when a
  cheaper or better model passes every one of your checks, plus a warning before your model is retired. Solo
  $19 (3 jobs), Team $49 (10), Agency $149 (40). 14-day money-back. Details: <https://xfms.xpansion.dev/watch>

## Tools

`discover` (finds the job's real requirements), `rank` (the full shortlist with the evidence behind it),
`pick` (the single best proven model), `compare` (the screening round and test on your tasks), `benchmark`,
`field_results` (what has worked for jobs of the same kind), and `watch_job` (XF Model Watch).

## What we keep

No conversations are kept. We log the one-line description you start with and an anonymous ID to count use. Our
own daily comparisons are published at <https://xfms.xpansion.dev>, every answer and every verdict, so the method
can be checked.

## How the shortlist is built

1. **No vendor claims as proof.** A model saying it supports JSON or a long context is a claim. We record how
   often each model actually kept its claims in our own comparisons.
2. **Missing evidence is shown as missing,** never as good.
3. **Your requirements decide.** Must-haves filter; priorities order what is left.
4. **The test decides the winner.** Methodology in [`docs/methodology.md`](docs/methodology.md).

## Honest limits

A comparison uses a handful of your sample tasks, and a model grades part of the answers. Read a result as strong
evidence for your decision, not a guarantee. We can only report on models we have tested, and the ranking before
the test is a shortlist, not a verdict.

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
