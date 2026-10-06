# Session 7 — The V-Score Validator Capstone (Team 5)

**Deliverable: a team of scorer agents, not a calculator.** Given one idea in plain English, agents reason out a 1–10 score + reason for each of 8 criteria; an orchestrator fans out, aggregates and maps to a verdict.

- Result: **orchestrator skill + 8 blind scorer sub-agents + a tested Python aggregator**, plus both advanced-tier items (memory bank and self-learning loop)
- Evidence: [`evidence/test-run.log`](evidence/test-run.log) (26 tests, all passing) and [`demo/sample-run.md`](demo/sample-run.md) (real runs on the 3 reference ideas + calibration story)

> Context: team capstone (Team 5, breakout room, ~30 min build + 3 min demo). Unlike sessions 3–6, nothing here comes from the private client project — the whole system was built from scratch for the workshop.

## What was asked

| Item | Brief |
|---|---|
| Shift | v1 = human types 1–10, code multiplies. **v2 = human writes the idea; an agent per criterion reasons out each score** |
| Components | A **scorer per criterion** (`{idea, rubric}` → `{score 1–10, reason}`) and an **orchestrator** (fan out, weight, sum, verdict) |
| Math | `PoC = Novelty×3 + Scope×4 + Resources×2 + Outcome×1` · `Market = Pain×4 + Pay×3 + Size×2 + Moat×1` · High = ≥ 65 |
| Matrix | 🚀 Go (high/high) · 🔍 Validate Demand (high PoC, low Market) · 🧪 De-risk First (low PoC, high Market) · 🛑 Reframe or Shelve (low/low) |
| Pattern | Pick one and defend it: single agent + skills · orchestrator + sub-agents · parallel scorers |
| Deliverables | 1 Spec (before building) · 2 Agent/skill definitions · 3 Orchestration · 4 Proof (live run on a judges' idea) |
| Judging | 5 × 5 pts (spec, decomposition, orchestration, verification, demo) + 5 advanced bonus (memory bank / self-learning) |
| Reference ideas | Slack bot → Go · translation earbuds → De-risk First · "AI for everything" → Shelve. Boundaries: all 10s → Go, all 1s → Shelve, exactly 65 → High |

## What we built

Pattern: **orchestrator + parallel blind sub-agents** (combines "most agentic" and "fastest"). Rule: **LLMs reason, code calculates.**

```
idea ─▶ /vscore (skill, main session)
          0 recall similar past idea   ── scripts/score.py recall
          1 load lessons per criterion ── memory/lessons.md
          2 fan out 8 blind scorers in parallel (× N samples)
          3 validate · median · weight · sum · matrix · ⚠️ borderline ── scripts/score.py aggregate --save
          4 report: both scores, verdict, 8 reasons, similar past idea
```

| # | Deliverable | Where |
|---|---|---|
| 1 | Spec — brief, agent breakdown, measurable DoD (D1–D12) | [`SPEC.md`](SPEC.md) |
| 2 | 8 scorer sub-agents, each with a 4-band rubric + 4 calibration examples; the `description` routes exactly one criterion to each | [`.claude/agents/`](.claude/agents/) · overview in [`AGENTS.md`](AGENTS.md) |
| 3 | Orchestrator skill + deterministic aggregator | [`.claude/skills/vscore/SKILL.md`](.claude/skills/vscore/SKILL.md) · [`scripts/score.py`](scripts/score.py) |
| 4 | Proof — runs on the reference ideas | [`demo/sample-run.md`](demo/sample-run.md) |
| +A | Memory bank: every run appended, most similar past idea recalled (token Jaccard) | [`memory/scores.json`](memory/scores.json) |
| +B | Self-learning loop: feedback → one rule under the right criterion → injected into that scorer only | [`.claude/skills/vscore-learn/`](.claude/skills/vscore-learn/SKILL.md) · [`memory/lessons.md`](memory/lessons.md) |
| + | Calibration exam over the reference ideas, re-run after any rubric/lesson change | [`.claude/skills/vscore-eval/`](.claude/skills/vscore-eval/SKILL.md) · [`evals/reference-ideas.json`](evals/reference-ideas.json) |

### Why this pattern

1. **Blindness.** Each scorer has its own context and never sees the other scores, so a strong Pain score can't halo-inflate Willingness to Pay. A single agent with skills shares one context.
2. **Single responsibility.** One criterion, one rubric, one file — tune or replace one scorer without touching the rest.
3. **Speed.** All scorers launch in one message. With `--samples 3` (24 agents) it runs in two waves because of the 20 concurrent sub-agent limit.
4. **Verifiable math.** Weights, the ≥ 65 matrix and the boundary live in Python with tests, not in an LLM adding numbers.

## Results vs. what was asked

| Check | Result |
|---|---|
| Math + matrix: all 10s → 100/100, all 1s → 10/10, 65 → High, 64 → Low, 4 quadrants | ✅ [`tests/test_score.py`](tests/test_score.py) (26 tests) |
| Invalid scorer output rejected (score ∉ [1,10], non-int, empty reason) | ✅ tests |
| "AI for everything" → 🛑 Shelve | ✅ PoC 26 · Market 31 |
| Translation earbuds → 🧪 De-risk First | ✅ PoC 39 · Market 65 — ⚠️ borderline, fragile |
| Slack bot → 🚀 Go | ❌ PoC 85 · Market 63 → 🔍 Validate Demand, ⚠️ borderline. Kept as an honest miss (see below) |
| Memory bank grows 1 entry per run | ✅ 3 runs in `scores.json`, including a fresh idea outside the reference set |
| Self-learning changes the next score | ✅ a Pain lesson moved the Slack bot's Pain 4 → 5 (step 2 of the calibration story) |

## Observations

1. **Tests proved the math; only running the agents exposed calibration.** First uncalibrated run: Slack bot Market = 53, because Pain scored 4 "since competitors exist" — the Moat criterion leaking into Pain.
2. **Noise beat the lesson.** The Pain lesson moved Pain 4 → 5, but run-to-run variance (Pay 7 → 5) swamped it. Adding calibration examples (one per quadrant, never the reference ideas) and **median of 3 blind samples** collapsed the variance: 7/8 criteria unanimous.
3. **We did not tune until the Slack bot said Go.** Three measurement methods all landed Market at 63–64. Pushing it over 65 would be overfitting the rubric to the answer key. Instead the system flags anything within ±5 of 65 as ⚠️ Borderline (low confidence).
4. **Specificity is a trade-off, not a free win.** Richer wording ("EMs with 5+ teams, ~30 min/day") raised Pain 6 → 7 but dropped Size 8 → 6.
5. **Gotcha:** Claude Code loads `.claude/agents/` at startup, so agent edits mid-session need `/exit` → `claude --continue`.

## Run it

```bash
python3 -m unittest discover -s tests -v       # math, matrix, 65 boundary, median, borderline
claude                                         # (re)start Claude Code here — loads agents/skills
> /vscore A Slack bot that summarizes daily standups for managers
> /vscore --samples 1 <idea>                   # fast single-pass (demo-friendly)
> /vscore-learn pain ran cold: penalized existing competitors, that's moat's job
> /vscore-eval                                 # re-check the reference ideas
```

## 3-minute demo script

| Time | Show | Say |
|---|---|---|
| 0:00–0:30 | `SPEC.md` §2–3, §6 | "Orchestrator + 8 blind sub-agents. LLMs reason, code calculates. Here's our measurable DoD." |
| 0:30–1:00 | `.claude/agents/pain-scorer.md` | "One agent per criterion — the description routes it. Rubric + calibration examples. Novelty is inverted." |
| 1:00–1:30 | `.claude/skills/vscore/SKILL.md` + `python3 -m unittest` | "Recall → lessons → 8 agents in one message → validate → `score.py` → verdict. 26 tests prove the math and the 65 boundary." |
| 1:30–2:20 | `/vscore --samples 1 "<judges' idea>"` | 8 agents in parallel → reasons → both scores → verdict (and ⚠️ if borderline). `scores.json` grows. |
| 2:20–3:00 | `demo/sample-run.md` → *Calibration story* | "Tests proved the math; only running the agents exposed calibration. We fixed noise, kept the honest miss, and the system tells you when it's not sure." |

### Likely judge questions

- **"Why not Go on the Slack bot?"** — 3 measurement methods, always Market 63–64, unanimous scorers, flagged borderline. Tuning the rubric to hit Go would be overfitting.
- **"Why is math in Python?"** — The arithmetic is trivial and must be *verifiably* correct. Tests > an LLM adding numbers.
- **"Why sub-agents and not one agent with skills?"** — Blindness. A shared context lets one criterion halo-inflate another.

## Open questions

- Judges' score and the fresh idea used in the live demo — not recorded here.
- This week's mission (apply orchestrator + specialists to a real work task) — to be brought to Session 8.
