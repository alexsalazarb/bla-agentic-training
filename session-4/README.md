# Session 4 — Memory & Self-Improvement

**Deliverables:**
1. A `memory-bank/` for a project I work on now: five files, each under 200 lines. See [`memory-bank/`](memory-bank/).
2. The self-improvement loop run on my own session history, with at least one rule approved in supervised mode. See [`evidence/self-improvement-trace.md`](evidence/self-improvement-trace.md).

> Context: the project is the Syncro MSP mobile app (Flutter). The memory-bank is distilled from my real KB, plans and git history. The working repo is private, so identifiers are generalized.

## 1. memory-bank/

| File | Tier | Update cadence |
|---|---|---|
| [`project_brief.md`](memory-bank/project_brief.md) | Semantic | On scope changes |
| [`product_context.md`](memory-bank/product_context.md) | Semantic | On new product areas |
| [`tech_context.md`](memory-bank/tech_context.md) | Semantic | On stack or convention changes |
| [`active_context.md`](memory-bank/active_context.md) | Episodic | Every session end |
| [`progress.md`](memory-bank/progress.md) | Episodic | Every session end |

## 2. How my real setup maps to the four tiers

I already run a layered memory system through the ai-framework. The memory-bank above is a compact, portable view of it.

| Tier | Question | Where it lives in my working repo |
|---|---|---|
| Working | "What am I doing right now?" | Context window |
| Episodic | "What did we do recently?" | Active plans (`.plans/`), verbose commit bodies, session summaries in Engram |
| Semantic | "What do we know?" | Project `AGENTS.md`, KB docs (`docs/kb-projects/`), `conventions.md`, `mistake-log.md` |
| Resource | "What can I do?" | `.claude/skills`, agents, MCP servers (Atlassian, Firebase, Engram), hooks |

**Hybrid strategy:** Markdown (the KB) is the source of truth. **Engram** is the searchable archive: a local SQLite store with FTS5 full-text search, fed from session summaries and KB docs. It uses keyword search, not vectors, but it plays the same role: a query-on-demand index, so nothing loads every session.

Its hooks automate parts of the session ritual:

| Hook | What it does |
|---|---|
| `SessionStart` (startup/clear) | Starts the memory server, opens a session, imports new KB chunks, injects the memory protocol |
| `UserPromptSubmit` | On the first message, loads the memory tools |
| `SessionStart` (compact) | After compaction, tells the agent to persist the compacted summary |
| `SubagentStop` | Passively captures sub-agent output |
| `Stop` | Marks the session as ended |

## 3. Self-improvement loop

The course script `npm run self:extract-insights` is not in the shared playground repo or in my workspace. Open question for the trainer: where does it live? Meanwhile, I document the equivalent loop I already run:

- **Signal:** I correct the agent.
- **Reflect:** the `log-mistake` skill writes a mistake/correction/prevention entry.
- **Promote (supervised):** at 3 recurrences, the rule goes into `AGENTS.md` "Things to Avoid".

Two real traces are in the evidence file. One rule was promoted after three recurrences (branch from `develop`, never `main`). One was born and applied in a single session (skill author metadata).

## 4. Observations

- **The regression is the lesson.** A guardrail I added in early September was lost because it was never committed. Memory that is not in git is working memory in disguise.
- **Mistake logs only grow.** My setup has no "Unused → Archived" step, so `mistake-log.md` will eventually become the graveyard the slide warns about. Next step: a periodic review that archives entries with no recurrence for 60 days.
- **Episodic and semantic separation holds up.** Plans (episodic) get archived when merged, while the KB (semantic) stays. When a plan's status drifted from git reality, the fix was to check `git log develop`, not to trust the note.
