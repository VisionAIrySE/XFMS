# The Xpansion Framework — In Plain English

XFMS is one module of the **Xpansion Framework** — a unified
architecture for governing AI-assisted work that doesn't require
you to be a developer to understand or trust.

This page tells the whole story: what's broken about working with
AI today, what Xpansion fixes, and how the pieces fit together for
someone who's building things.

> Xpansion is in **pre-signup** right now. Early access is open at
> [xpansion.dev](https://xpansion.dev).

---

## What working with AI gives you that's broken

AI coding assistants and agents are fast. They produce a lot of
output in very little time. The output usually looks reasonable.

That's exactly the problem.

| Problem | What it looks like in real life |
|---|---|
| **Fast output, no contract** | The AI builds *something*, but is it what you actually asked for? You can't tell without reading every line. |
| **Does things you didn't ask for** | The AI "helpfully" deletes a file, renames a function, refactors a section — and breaks something that was working. |
| **Forgets between sessions** | Every conversation starts from zero. The decisions you made last week, the patterns you agreed on — gone. |
| **Claims to be done when it isn't** | "All set!" — except three of the six things you asked for aren't actually working. |
| **Leaks secrets or writes insecure code** | API keys hard-coded. Auth checks skipped. SQL injection back from the dead. |
| **Talks in jargon when you want answers** | You ask a question, you get a wall of acronyms, stack traces, and file paths. |
| **Picks the wrong model for the task** | Uses an expensive frontier model where a cheap one would have been better, or a cheap one where a frontier model was needed. |
| **Drafts forever without alignment** | The AI keeps rewriting code in slight variations without first agreeing with you on what you're actually building. |

Each of those is a known failure mode. None of them get caught by
"prompt engineering" or "better instructions." They need
**guardrails that run at the system level** — checks that fire
automatically, every time, without the AI having to remember.

That's Xpansion.

---

## What Xpansion does about it

Xpansion sits **between you and any AI tool you use** — Claude Code,
Cursor, raw API calls, an agentic workflow — and enforces four
guarantees that the AI on its own does not provide:

1. **Finite intent.** Before any work starts, what you're building
   gets broken down into non-overlapping pieces with binary
   pass-or-fail tests for each one. No ambiguity.
2. **Real-time enforcement.** Every action the AI takes is checked
   against the spec at the moment it happens. Out-of-scope actions
   get blocked; in-scope ones proceed.
3. **Binary verification.** At ship time, every piece of the spec is
   checked against the actual artifacts. No hand-waving. No "looks
   done to me."
4. **Compounding memory.** Every session's decisions and outcomes
   get stored on your own computer as a searchable tree. Next
   session inherits the context.

These four guarantees aren't features you turn on. They're the
**runtime contract** the framework enforces continuously, in the
background, while you work.

---

## The module suite — organized by what they do for you

Xpansion is built as a set of cooperating modules. Each one solves
a specific problem in the AI-assistance workflow. You don't need to
remember the acronyms — you need to know what each piece does for
you.

### Intent — define what "done" looks like first

| Module | What it does for you |
|---|---|
| **XFFI** (Finite Intent) | Before any code gets written, walks you through breaking your idea into specific pieces with pass-or-fail tests for each. You can't accidentally ship "kind of done." |
| **XFAE** (Approach Evaluator) | Challenges the AI's first instinct on *how* to build something. Catches bad approaches before you commit hours to them. |
| **XFCD** (Communication / Contradiction Decomposition) | Stops the AI from drafting endless variations of code without first agreeing with you on what to build. Forces an explicit conversation when there's drift. |

### Boundaries — catch breaks at the moment they happen

| Module | What it does for you |
|---|---|
| **XFBA** (Boundary Auditor) | Watches every code change in real time and stops the ones that would break something. Like a copy editor catching typos before the article goes out. |
| **XSIA** (Systemic Impact Analysis) | Warns you when a small change could ripple through and break things you didn't think about ("you're renaming this function — 12 other files call it"). |
| **XFSA** (Security Auditor) | Watches for security mistakes — leaked keys, unsafe code patterns, SQL injection risks — as you go, not after the breach. |
| **XFRI** (Refinement Intelligence) | The auditor learns from your decisions. If it raises a false alarm and you say "that's fine," it stops raising that same false alarm. |
| **XFA** (Audit umbrella) | One switch to pause every auditor at once for one-off exceptions, then resume. |

### Verification — prove you actually delivered

| Module | What it does for you |
|---|---|
| **XFXA** (eXecution Audit) | At ship time, checks every piece of the spec against the actual artifacts. Each piece is either pass or fail — no "AI says it's done." |

### Memory — carry context across sessions

| Module | What it does for you |
|---|---|
| **XFMT** (Memory Tree) | Saves a snapshot of every meaningful session to your own computer. Next time you start, the framework knows where you left off — what you built, what you decided, what's still open. |
| **XFMTR** (Memory Tree Recall) | Search your memory like a notebook: *"what did we decide about pricing six weeks ago?"* — returns the relevant snapshot. |
| **XFPA** (Process Audit) | Watches which audit findings you accept and which you override. Over time the framework learns your judgment patterns and adapts. |

### Voice — keep the conversation in plain English

| Module | What it does for you |
|---|---|
| **XFVE** (Voice Enforcement) | Keeps the AI's voice human. No jargon walls when you want a clear answer. Lead with what something means, not how it works. |

### Session resources — manage the AI's working memory

| Module | What it does for you |
|---|---|
| **XFTC** (Token Conservation) | The AI has a memory budget for each conversation. When it's running out, XFTC saves a snapshot and starts fresh so you don't lose context. |

### Model selection — pick the right tool for the task

| Module | What it does for you |
|---|---|
| **XFMS** (Model Source — this product) | Picks the right LLM for the task, weighted by evidence aggregated across eight independent benchmark sources. Not vibes. Not vendor self-reports. |
| **xfms-pick** | The walked-discovery interface to XFMS. Asks three or four plain-English questions about your task, then picks. |

### Underlying infrastructure

| Module | What it does for you |
|---|---|
| **Dispatch** | The router. Picks the right tool for each step, fires the right audit at the right time, and connects every module so they work together. |
| **Trajectory Enforcement** | Keeps the AI on-task across long sessions. Catches drift early — when the AI starts solving a slightly different problem than the one you asked about. |

---

## A day in the life — what this looks like for a builder

Imagine you're a founder building an app. You ask the AI to add a
notification feature when a customer signs up. Here's what
Xpansion does, invisibly, in the background, while you talk to the
AI:

**Before any code is written:**

- **XFFI** walks you through breaking the feature down: *"there's
  a database change, an email send, a UI confirmation, and the
  edge case of a duplicate signup — which of those do you actually
  want?"* You decide. The framework records the decision.
- Each piece gets a binary test: *"the email sends within 5 seconds
  of signup. Pass or fail."* The AI now has a contract, not just a
  vibe.
- **XFAE** flags that the AI was about to use a background worker
  pattern that doesn't fit your stack. You pick a different approach
  before the AI commits to it.

**While the AI is working:**

- The AI starts writing code. **XFBA** catches a function with
  wrong argument types — would have crashed at runtime. Fix
  applied before commit.
- The AI proposes deleting an old function. **XSIA** flags twelve
  other files that call it. You decide whether to refactor or keep.
- The AI writes the email send code. **XFSA** notices an API key
  was about to be hard-coded. Flagged before the commit.
- **XFTC** notices the conversation is approaching the AI's memory
  limit. Triggers a snapshot to **XFMT** so nothing gets lost when
  the conversation refreshes.

**At ship time:**

- **XFXA** checks each piece of the original spec. Database
  change: pass. Email send: pass. UI confirmation: pass. Duplicate
  edge case: fail — there's no test for it yet. You know exactly
  what's left.
- **XFMS** picks which model to use for the LLM-powered customer-
  support reply that's part of the feature, based on cost,
  quality, and capability fit for that specific task.

**After ship:**

- **XFMT** stores the full session as a structured snapshot. Next
  week, when you start the next feature, the framework knows what
  patterns you used and what decisions you made.
- **XFCD** notices a change to your email template format. Asks:
  *"keep this pattern as the default for future emails?"* You
  decide. **XFPA** records the decision and starts auto-applying
  it next time.

You worked with the AI like normal. The framework caught every
failure mode in the background. You shipped something that
actually does what you asked, and the next session starts smarter
than this one ended.

---

## Where XFMS fits in

XFMS is the **model-selection layer**. When any other module needs
an LLM call — when XFFI needs to break down intent, when XFMT needs
to summarize a session for the memory tree, when an agent inside
Xpansion needs a model — XFMS picks which one to use based on
evidence, not vibes.

It also stands alone as a tool you can use independently of the
rest of the framework: state a purpose, get a ranked shortlist
with rationale. The methodology behind those picks is documented
at [methodology.md](methodology.md).

---

## Where Xpansion goes next

The four-pillar contract (finite intent, real-time enforcement,
binary verification, compounding memory) generalizes beyond
software work. The same architecture applies to any structured
work context where:

- The intent can be defined with concrete deliverables
- The work can be broken into pieces with pass-or-fail tests
- Prior decisions compound in value when remembered

That means writing, research, design, education, regulated-
industry workflows, and other non-code contexts use the same
underlying framework. Xpansion isn't a coding tool. It's an
**AI-collaboration substrate** that happens to ship with software
development as its first proven context.

---

## How to get on the list

Xpansion is in **pre-signup**. Founding licenses and early access
go to people on the list before public launch.

👉 [xpansion.dev](https://xpansion.dev)

If you want to talk to a human about what you're building or what
problem in your stack Xpansion would actually solve, email Russ
directly: russ@visionairy.biz.

---

## Patents pending

The Xpansion Framework methods — finite intent decomposition, code-
enforced tool gating, binary terminal verification, and local-
sovereign compounding memory — are the subject of pending patent
applications by Russ Wright / Visionairy.

XFMS (this repository) is open under the Functional Source License
1.1 with an Apache 2.0 Future License. Using XFMS does not grant
rights to the broader Xpansion patents. See [`../NOTICE`](../NOTICE)
for the full reservation.

---

## Read more

- [README](../README.md) — XFMS the product
- [methodology.md](methodology.md) — how XFMS picks
- [`../NOTICE`](../NOTICE) — patent reservation
- [xpansion.dev](https://xpansion.dev) — pre-signup
