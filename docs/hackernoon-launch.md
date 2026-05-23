# I Built a Free MCP That Picks the Right LLM From 350+ — Because Picking by Twitter Thread Is Not a Strategy

*By Russ Wright, Founder, [Xpansion Framework](https://xpansion.dev)*

---

Last week one of the first people to try XFMS — a friend, building a personal assistant — fired off a compare call against three free OpenRouter models and watched it hang for an hour.

I dug in. The hosted endpoint was on Vercel. Vercel has a 300-second ceiling on serverless functions that nobody documents loudly. Free-tier OpenRouter inference is rate-limited to the point where three models against five test prompts can take six minutes. The math doesn't work. The thing died silently every time someone tried it.

That's a launch story I could have spun. I'm telling it because it's true, and because it surfaces the real problem XFMS exists to solve: **nobody verifies LLM picks against the actual workload, and that's the part that bites.** You can pick by benchmark. You can pick by tweet. You can pick by whatever was hot on Hacker News that morning. Until you run your real query through the candidates and measure what comes out the other side, you're guessing.

I rebuilt the host on Fly the next morning. Then I rewrote the cost model so people could actually use it. Now I'm telling you about it.

## The state of LLM picking is embarrassing

There are about three hundred and fifty production-grade LLMs on OpenRouter right now. There are eight independent benchmark suites running them through structured evaluations — LMSYS Arena, Aider Polyglot, LiveBench, BigCodeBench, MMLU, GPQA, Tau-Bench, LongBench. None of the eight agrees with the other seven on which model is "best" because best is contextual. Nobody synthesizes them. Nobody normalizes their scores. Nobody asks *what are you actually building* before picking.

So instead we get the current state: a developer types *"what's the best LLM for X?"* into a chat, gets back a confident answer that reflects a single source of training data from last year, and ships. Or they ask Twitter. Or they ask the LLM itself which LLM to use, which is a wonderful way to get a plausible-sounding wrong answer.

I built XFMS because that's not a strategy, that's an emotion. Picking foundation models by vibes is fine if you're tinkering. It is not fine if you're shipping production systems whose cost, latency, and quality you'll be answering for at the next standup.

## What XFMS does

It's a hosted Model Context Protocol server — meaning a small remote tool your AI assistant can call inside any conversation. You install it once by pasting a URL into your assistant's config (Claude Code, Cursor, Continue, Cline — they all speak the same protocol). Then you ask your assistant *"which model should I use for X?"* and it calls XFMS for you. No leaving the chat. No copy-pasting between leaderboard tabs.

You tell it what you're doing. It tells you which model to use, why, and what the alternatives are.

```
You: "Pick a model for fixing bugs in our Python codebase."

XFMS:
Top picks:
   1. 0.842  GPT-5.5                 (openai/gpt-5.5)         via OpenAI
   2. 0.811  Claude Opus 4.7         (anthropic/claude-opus-4.7) via Anthropic
   3. 0.798  Gemini 3.1 Pro Preview  (google/gemini-3.1-pro-preview) via Google

Inferred quality weights from your purpose:
  • structured_output_reliability  42%  ← BigCodeBench, Aider Polyglot
  • instruction_following          28%  ← LiveBench, Tau-Bench
  • factuality                     20%  ← MMLU, GPQA
  • coherence                      10%  ← LongBench

Picked GPT-5.5: strong on structured output and instruction following —
the two dimensions that dominate code-edit work. Beats Claude on Aider
Polyglot and matches it on LiveBench reasoning, at roughly 60% of the
per-token cost.
```

Every weight has a source. Every pick has a reason. And if you tell me *"cheapest model, period,"* the engine drops the weighted blending and uses lexicographic ranking — cost wins, the other dimensions only break ties. Your stated preference is sacrosanct. The recommender stops second-guessing you the moment you take a position.

## Where Twitter loses

Picking from benchmarks is better than picking from tweets. But benchmarks aren't your workload. So XFMS has a `compare` tool that takes two-to-five models you name, generates test prompts shaped like the work you actually do, runs them against every candidate in parallel, and tells you who won.

```
─── A/B probe ───
Ran 3 test queries against the named candidates.
  • OpenAI: gpt-oss-120b (free)   avg_latency=8087 ms  total_cost=$0.0000  successes=3
  • Z.ai: GLM 4.5 Air (free)      avg_latency=5863 ms  total_cost=$0.0000  successes=3

Commentary:
  Across 3 real test queries, GLM 4.5 Air was 27% faster (5863 ms vs
  8087 ms avg). Both cost $0.00 — they're on OpenRouter's free tier.
  Clear latency winner with no quality compromise on these prompts.
```

That's live output from a real call I made before sitting down to write this. Average benchmark scores have gpt-oss ahead. The probe against representative queries — *the kind of queries I'd actually send* — said GLM was 27% faster with equal success rate. For this kind of work. Yours might come out the other way; that's the point.

This is where "evidence over vibes" gets uncomfortable. Sometimes the cheap model wins. Sometimes the prestigious one is wrong. The probe will tell you. If the top picks trade off and there's no clean winner, the probe auto-expands from five to ten to fifteen test queries before declaring one. It digs harder until something separates.

There's a `benchmark` tool that does the same probe against XFMS's own top three picks instead of models you name — for when you want the recommendation and the verification in one shot. There's a `discover` tool that shows which quality dimensions the engine would weigh for a stated purpose without ranking anything, so you can see how the engine reads your phrasing before you commit.

## The four rules I refuse to break

The full methodology is at [`docs/methodology.md`](https://github.com/VisionAIrySE/XFMS/blob/main/docs/methodology.md). The short version:

1. **No provider self-reports.** Every score comes from a third-party evaluator running the same protocol across every model.
2. **No single-source dependence.** Eight independent benchmark sources contribute today. No single leaderboard determines a pick.
3. **User intent beats engine inference.** XFMS infers weights from your purpose. Your stated priorities always override the inference.
4. **Honest gaps over invented signal.** Missing data is recorded as missing — no interpolation, no synthetic scores. Coverage gaps surface on every pick.

Rule four is the boring one and the most important. Half the leaderboard sites quietly extrapolate missing scores. I won't. If a model hasn't been tested on the dimension you care about, you'll see that before you commit.

## Install — one line for the free tools, one header for the live probes

XFMS is hosted. Nothing to install on your machine.

**The three free tools** — `rank`, `pick`, `discover` — work with no key:

```bash
claude mcp add xfms --transport http https://xfms.xpansion.dev/mcp/
```

Your assistant does the small internal thinking work via MCP sampling. Nobody pays anything to anyone.

**The two live A/B tools** — `compare` and `benchmark` — actually run test queries against the real candidate models on OpenRouter. That inference cost rides with you, not me. They require your OpenRouter key in a header:

```bash
claude mcp add xfms --transport http https://xfms.xpansion.dev/mcp/ \
  --header "X-OpenRouter-Key: sk-or-v1-your-key-here"
```

Cursor's config:

```json
{
  "mcpServers": {
    "xfms": {
      "url": "https://xfms.xpansion.dev/mcp/",
      "headers": { "X-OpenRouter-Key": "sk-or-v1-your-key-here" }
    }
  }
}
```

**I do not mark up your inference.** The discovery tools are free because your assistant pays for the small thinking work. The A/B tools cost exactly what your OpenRouter account costs, and not a cent more. There's no membership tier on me, no per-pick fee, no metering middleman. You target an OpenRouter model picker — I assume you already have a key. [Grab one here](https://openrouter.ai/keys) if not.

The key travels encrypted, gets used once per request, is never logged on my side, is never persisted. Same posture as every other API key in any MCP config.

## Where this stands today

- XFMS is in public beta. Eight benchmark sources today; I'm working toward fifteen.
- The recommender engine, the catalog, and the ingestion pipeline are hosted and not open source — that's where the real work lives, and it stays mine. The thin Python wrapper that talks to those endpoints is open on GitHub at [github.com/VisionAIrySE/XFMS](https://github.com/VisionAIrySE/XFMS), MIT-licensed, ~250 lines — for inspection, or for the rare case you want to script against XFMS from Python directly. Most users go through the hosted MCP and never touch it.
- A/B probes against paid models take about a wall-clock minute. Probes against free-tier OpenRouter models take three to five because the free tier is heavily rate-limited from their side. XFMS automatically caps free-tier probes at three queries to keep them inside the deploy's timeout. The MCP tool tells your assistant about this up front so it can warn you before running.

## Why this is one of seven

XFMS is the first piece of the **[Xpansion Framework](https://xpansion.dev)** to ship public and free. The rest is in pre-signup.

The thesis I'm building Xpansion on is one sentence: *humans communicate with intent compressed by contextual experience. AI predicts patterns in language. Xpansion is the execution layer that bridges them.*

Every sentence a person types carries context the speaker assumes the other side will decompress — what counts as good enough, which constraints are non-negotiable, what last quarter's incident taught them, what their house style demands. AI doesn't share that context. It predicts patterns. It fills in plausible answers. The result reads as fine and isn't. Sessions lose memory. Security holes ship silently. Specs drift. Nobody verifies the work matched the ask. They don't know what they don't know, and neither does the AI.

Xpansion closes the gap. **Xpansion code-enforces AI to do what it can't be relied on to do reliably on its own.** It decompresses finite intent upfront. It enforces that intent through code-driven AI behavior. It binary-verifies the result against the intent. And it carries the intent across persistent memory that survives every session boundary.

XFMS is one specific enforcement of that contract — *the right model for the work you actually described, not the model Twitter happens to be celebrating this week.* The siblings cover the rest of the contract for other parts of the work:

- **Finite Intent (XFFI)** turns *"build me a feature"* into a finite spec with binary terminals before any code gets written.
- **Boundary Auditor (XFBA)** checks every code edit against contracts. Stops broken signatures from reaching production.
- **Systemic Impact Analysis (XSIA)** maps the blast radius of a change before it lands.
- **Token Conservation (XFTC)** keeps long sessions from silently losing context.
- **Execution Audit (XFXA)** verifies every promise from the spec was met before a task ships.
- **Memory Tree (XFMT)** stores session snapshots that stay searchable across conversations.
- **Security Auditor (XFSA)** runs static and AI security scanning on every edit.

Every few times you use XFMS, the answer comes back with a one-line note about one of those siblings. That's my pitch — read it, ignore it, or drop your email at [xpansion.dev](https://xpansion.dev) for the launch heads-up. Never sold.

Founding Pro is $15/month for the first 250 builders, $29 after that.

## TL;DR

You're picking LLMs by vibes. Stop. XFMS reads eight independent benchmark sources, weights them against your actual purpose, surfaces the recommendation with a sentence of plain-English rationale, and runs an A/B probe against your kind of query so the pick is verified, not vibed.

Hosted MCP server. One URL into your AI assistant. The three discovery tools are free, no setup. The two A/B tools use your own OpenRouter key — no markup, no membership, no middleman.

`https://xfms.xpansion.dev/mcp/`

Try it on your next *"which model should I use?"* moment.

---

*Russ Wright is the founder of [Xpansion Framework](https://xpansion.dev). XFMS is the first module to ship public and free. The rest is in pre-signup.*
