# XFMS Methodology

How XFMS decides which model is right for a stated purpose — what
data it uses, where the data comes from, how it gets reconciled
across sources, and how the system handles gaps honestly instead of
hiding them.

This page is the standing answer to *"why should I trust the
picks?"*

---

## The Problem XFMS Was Built To Solve

Most LLM selection happens on vibes — a Twitter thread, a blog post,
a screenshot from a vendor's launch keynote, a friend's offhand
recommendation. That works until it doesn't: the model you picked
based on one benchmark is third-place on three others, and the one
you ignored quietly leads on the dimension your actual task
depends on.

The other common path is to trust a single leaderboard. That's
better than vibes, but every leaderboard measures one thing — Elo
on Arena, accuracy on MMLU, pass-rate on Aider. No single number
captures whether a model can write a tight editorial, refactor a
React component, or stay coherent across a 200-page contract.

**XFMS exists to aggregate evidence across many independent
sources, normalize it onto a common scale, and let the caller's
purpose decide which dimensions matter.**

The methodology below is what makes that aggregation defensible.

---

## Four Principles

### 1. No provider self-reports

XFMS deliberately excludes benchmark numbers that providers publish
about their own models. "Anthropic says Claude scored X on MMLU"
and "OpenAI says GPT-5.5 scored Y on GPQA" are useful for press
releases and unreliable for cross-model comparison — every vendor
benchmarks under slightly different conditions, prompts, and
sampling settings.

Every score in the XFMS catalog comes from a **third-party
evaluator** running the same protocol across every model in the
comparison set. If we can't get a third-party number, we record the
gap rather than fall back to the vendor number.

### 2. Independence from any single source

No single leaderboard determines a pick. Eight independent sources
contribute today (listed below), and the criteria tree weights
multiple leaves per quality dimension so that a model needs
strength across several measures — not just one — to rank high.

If one source goes dark or starts measuring something weird, the
others continue to function. No single point of failure.

### 3. User intent beats LLM inference

XFMS infers which quality dimensions matter for a stated purpose —
*"writing an editorial"* gets weighted toward creative writing
and coherence; *"fixing Python bugs"* gets weighted toward
structured output and instruction following. That inference is the
helpful part.

But the **user's stated preference always overrides the
inference**. If you say "I care most about factuality" — even if
the LLM thinks creative writing matters more — your call wins.
That override is a first-class API surface, not a backdoor.

### 4. Honest gaps over invented signal

Where a model has not been measured on a specific benchmark, XFMS
**does not interpolate, predict, or estimate**. It records the gap.
The ranking math accounts for gaps explicitly (see "Coverage gaps"
below), and the per-pick explanation surfaces which dimensions had
missing data so the caller can judge confidence.

---

## The Eight Benchmark Sources

| Source | What it measures | Why it's in the catalog |
|---|---|---|
| **HuggingFace Open LLM Leaderboard** | General reasoning, math, knowledge, truthfulness — six standardized benchmarks (ARC, HellaSwag, MMLU, TruthfulQA, Winogrande, GSM8K). | Broad coverage across open and proprietary models; one of the most-cited leaderboards in the field. |
| **Artificial Analysis** | Quality index, speed (tokens/sec), price ($ per 1M tokens), context window, hard reasoning (GPQA Diamond). | The only source covering frontier proprietary models (Anthropic, Google, xAI, OpenAI) at depth, without provider self-reports. Powers the cost + latency branches. |
| **LMSys Chatbot Arena** | Human-preference Elo from millions of pairwise blind comparisons. | The gold-standard human-preference signal. The only source that captures "which model do real people pick when they don't know which is which." |
| **LiveBench** | Contamination-resistant benchmarks across reasoning, coding, mathematics, language, data analysis, instruction following — rotated monthly. | Resistant to training-data leakage in a way most static benchmarks are not. Catches models that overfit to public benchmarks. |
| **Creative Writing v3** | Editorial prose, narrative writing, voice consistency. | The dimension most static benchmarks ignore. Picks for writing/editorial tasks rest heavily on this. |
| **EQ-Bench v3** | Emotional intelligence, social reasoning, character coherence. | Surfaces a quality dimension that matters for chat, support, and any task with a human-emotional layer. |
| **BigCodeBench** | Tool-using code generation across hundreds of practical programming tasks. | Distinct signal from Aider — focuses on novel code generation rather than refactoring existing files. |
| **Aider Polyglot** | Refactoring real codebases across multiple languages. | The signal closest to "is this model useful in a working developer's loop?" Tasks come from real GitHub repos. |

Each source is run on its own cadence (daily for LMSys Arena, weekly
for most others, monthly for LiveBench). The catalog refresh
documentation lives in the scraper module and is publicly inspectable.

---

## How Scores Get To A Common Scale

Every benchmark publishes scores in its own native unit —
percentages, Elo ratings, raw accuracy counts, pass-rates. To rank
across sources, XFMS normalizes every score to the **0..1 range**
before any weighting math runs.

The rules are unit-specific and recorded with each score:

- **Percent** (e.g., MMLU accuracy 87.3%) → divide by 100.
- **Elo** (LMSys Arena, range roughly 1000..1600 across frontier
  models) → `(score - 1000) / (1600 - 1000)`, clamped to 0..1.
- **Pass-rate** (Aider polyglot, e.g., 78% of tasks completed
  successfully) → divide by 100.
- **Quality index** (Artificial Analysis, 0..100 scale) → divide by
  100.
- **Raw / index** (anything else, treated as 0..100-shaped) → divide
  by 100 as a defensive default.

The unit of every benchmark is stored alongside the score, so
normalization is explicit and reproducible. No silent guessing — if
a unit doesn't match a known rule, the catalog flags it and a human
reviews it.

---

## How Model Names Get Resolved Across Sources

This is the part that quietly determines whether the picks are
trustworthy. Every benchmark source uses its own naming convention —
HuggingFace might call a model `meta-llama/Llama-3.3-70B-Instruct`,
Artificial Analysis might use `Llama 3.3 70B`, LMSys Arena might say
`llama-3.3-70b-instruct-turbo`. If those three names don't resolve
to the same canonical model in the catalog, the scores get split
across phantom entries and the ranking collapses.

XFMS resolves names through a **three-pass matcher**:

### Pass 1: Cache

Every confirmed mapping is stored locally. The first time a source
calls a model `llama-3.3-70b-instruct-turbo`, the matcher decides
what to map it to and records the decision. Subsequent runs are
instant lookups — no re-deciding.

### Pass 2: Deterministic matching

Where the source's name is a clean prefix or suffix of a canonical
ID — or vice versa — the matcher resolves it without an LLM call.
This handles the easy cases (90%+ of inbound names) at zero cost
and zero ambiguity.

### Pass 3: LLM disambiguator

When the deterministic pass can't decide, the matcher calls an LLM
to compare the inbound name against the candidate canonical IDs.
The LLM returns one of three results:

1. **Confident match** — the inbound name resolves to a specific
   canonical ID.
2. **No match** — the inbound name doesn't correspond to anything
   in the catalog (often a model the catalog hasn't ingested yet).
3. **Variant qualifier** — the inbound name is the same model as a
   canonical ID but with a settings difference (e.g.,
   `claude-opus-4-7-thinking` is the same model as
   `anthropic/claude-opus-4.7` but with the "thinking" setting
   enabled). The score is recorded under the variant tag so it
   doesn't collapse into the base model's score.

A **bidirectional qualifier validator** runs after the LLM's call to
catch over-eager matches (e.g., the LLM saying `gemini-3-pro`
matches `google/gemini-3-pro-image-preview` would be rejected
because "image-preview" is a release-style qualifier that materially
changes what the model is).

Every match decision is stored with its **decided_by** trace —
`cache`, `deterministic`, or `llm` — so the audit trail is complete.

---

## Coverage Gaps — What Happens When Data Is Thin

A model that exists in the catalog will almost never have scores on
every benchmark. New releases haven't been measured yet on some
sources; smaller open models often aren't tested on Aider Polyglot;
some proprietary models opt out of leaderboards entirely.

XFMS handles this with a **coverage gate** in the ranking math.

For a given purpose, the system infers which quality dimensions
matter and what weight each should get. Then it computes how much
of that intended weight is actually backed by data for each model:

- **If at least 50% of the intended weight has data**, the present
  weights are renormalized to sum to 1.0. The model is scored on
  what's measured.
- **Below 50%**, the system uses the original weights as-is —
  missing benchmarks count as zero. The model can still rank, but
  it's competing on a thin base and the pick comes with a low-
  confidence banner.

The 50% threshold is the line between "we have enough signal to
fairly compare this model" and "we don't, and the user should know."

Every pick surfaces which leaves had data and which didn't, in the
explanation. No silent zero-fills.

---

## The User Always Wins

The recommender does a lot of inference — purpose to leaf weighting,
benchmark to leaf mapping, quality dimension prioritization. Every
one of those inferences is **overridable** by the caller:

- **`leaf_priorities`** on `/rank` lets the caller say "weight
  factuality and instruction following equally, ignore the LLM's
  inferred weights for the quality branch." The override fully
  replaces the LLM's per-leaf weights at scoring time.
- **`decision_source`** on `/rank` is a required attestation: every
  call has to declare whether the parameters came from a walked
  discovery, a finite intent spec, a session snapshot, or were
  manually fabricated. If a caller fabricates weights, the audit
  trail records it as manual. Honest gaps over hidden assumptions.
- **`/discover`** walks the caller through the decision tree one
  question at a time, with no scoring — useful when the caller
  wants to understand the dimensions before committing to weights.

---

## Freshness

The catalog refreshes on independent cadences per source. The
benchmark records table stores `measured_at` (when the third-party
evaluator ran the test) and `captured_at` (when XFMS pulled the
record). Both timestamps are public on every score.

Stale data is data — XFMS does not drop scores because they're old.
A score from three months ago is still better than no score. But
the timestamps make staleness visible, and the catalog ingestion
cron documentation describes how to refresh each source on demand.

---

## Honest Gaps — What XFMS Does Not Do

To set expectations clearly:

- **XFMS does not run benchmarks itself.** Every score comes from a
  third-party evaluator. We are an aggregator + reconciler + ranker,
  not a measurement service.
- **XFMS does not estimate scores for models that haven't been
  measured.** No interpolation, no synthetic scores, no
  "comparable-model" defaults.
- **XFMS does not verify that the third-party evaluator's protocol
  is correct.** We trust each source to measure what they claim to
  measure. If a source publishes bad numbers, our picks will reflect
  them.
- **XFMS does not test whether a recommended model actually
  performs better on the caller's specific task.** That's the role
  of an A/B bench — a separate workflow in the toolchain that runs
  the actual prompts against the shortlist.
- **XFMS does not currently filter by provider** (e.g., "show me
  only models hosted in the EU" or "exclude provider X"). That's
  noted as a manual post-filter; provider-exclusion is on the
  roadmap.

---

## Where The Methodology Lives

This page is the canonical methodology spec. Every claim on this
page corresponds to code that runs at request time on the hosted
XFMS service.

**The engine that implements this methodology is not open source.**
This repository ships only the client library — a thin HTTP wrapper
that calls the hosted endpoint. The scoring math, the catalog, the
ingestion pipeline, and the inference layer all run on the hosted
side.

For transparency, the moving parts on the hosted side:

- The **API surface** at `xfms.vercel.app` carries every `/rank`
  call. The decision-source receipt gate and the user-leaf-priority
  override are enforced there — no call reaches the ranker without
  attested provenance, and any priorities the caller passes
  override the LLM-inferred weights.
- The **ranker** runs the score normalization, coverage-gated
  renormalization, and weighted sum described above.
- The **inference layer** runs the small LLM call that translates
  your stated purpose into per-leaf weights. That call uses your
  OpenRouter key (BYOK).
- The **ingestion pipeline** runs separately on a private schedule,
  pulling fresh data from the eight benchmark sources weekly (LMSys
  Arena daily). It writes to a private catalog database that the
  engine reads at request time.

Disagreements about methodology can be raised as GitHub issues on
this repository. If a change is warranted, the methodology page
gets updated here and the engine implementation follows.

---

## Changing The Methodology

This page is the canonical methodology spec. If a contributor wants
to change how XFMS reconciles, normalizes, or aggregates, the change
lands here first — in a PR that explains the rationale — and then
in the code. Methodology drift without a doc update is a regression.

Questions, disagreements, or proposed improvements: open an issue
on the XFMS repo or email russ@visionairy.biz.
