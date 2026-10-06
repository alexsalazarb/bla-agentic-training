# V-Score Validator v2 — Spec

> Written before building. Session 7 capstone · Team 5.

## 1. Brief

Given **one idea in plain English**, produce:

- a **PoC Viability** score /100
- a **Market Viability** score /100
- a **verdict** from the Recommendation Matrix
- a **1–10 score + reason for each of the 8 criteria**

No human types a number. Scores are *reasoned out* by agents; arithmetic is done by code.

### Out of scope

- Web research / live market data (scorers reason from the idea text + general knowledge)
- Multi-idea batch scoring, UI, persistence beyond local files

## 2. Pattern: Orchestrator + parallel blind sub-agents

**Why this pattern (our defense):**

1. **Independence = less bias.** Each scorer runs in its own context and never sees the other scores. A great "Pain" score cannot halo-inflate "Willingness to Pay".
2. **Single responsibility.** One criterion, one agent, one rubric. Easy to tune, test and replace one scorer without touching the rest.
3. **Speed.** All 8 are spawned in a single message → they run in parallel.
4. **LLM reasons, code calculates.** Weights, sums and the matrix live in `scripts/score.py` — deterministic and unit-tested. The LLM never does arithmetic.

```
idea (plain English)
        │
        ▼
 /vscore  ORCHESTRATOR (skill)
   0. recall similar past idea  (memory/scores.json)
   1. load lessons              (memory/lessons.md)
   2. fan out — 8 sub-agents in ONE message (parallel, blind)
        │
  ┌─────┴──────── PoC ────────┐  ┌──────── Market ────────────┐
  novelty scope resources outcome  pain pay size moat
  └─────┬───────────────────────┴──┴───────────┬───────────────┘
        ▼   each → {"score": 1-10, "reason": "..."}
   3. scripts/score.py  validate · weight · sum · map → verdict
   4. append run to memory/scores.json
   5. print report (scores, verdict, 8 reasons, similar past idea)
```

## 3. Agent breakdown

| Agent | Axis | Weight | 10 means… | 1 means… |
|---|---|---|---|---|
| `novelty-scorer` | PoC | ×3 | proven, well-understood tech (LOW novelty risk) | unproven research problem |
| `scope-scorer` | PoC | ×4 | one narrow, definable use case | "AI for everything", boundless |
| `resources-scorer` | PoC | ×2 | APIs/tools/data off-the-shelf | needs custom hardware/data/talent |
| `outcome-scorer` | PoC | ×1 | success is binary & visible in a demo | success is vague/unmeasurable |
| `pain-scorer` | Market | ×4 | acute, frequent, costly pain | nice-to-have |
| `pay-scorer` | Market | ×3 | clear buyer with budget, pays today | nobody pays / expects free |
| `size-scorer` | Market | ×2 | large, reachable market | tiny niche |
| `moat-scorer` | Market | ×1 | hard to copy (data, network, IP) | trivially cloned |

> **Novelty is scored as *viability*, not as "coolness".** High novelty = high PoC risk = LOW score. This is the one inverted criterion and it is stated explicitly in its agent definition.

**Contract (every scorer):** input `{idea, rubric, lessons}` → output, and only output:

```json
{"criterion": "<key>", "score": <int 1-10>, "reason": "<1-2 sentences tied to the idea>"}
```

## 4. Math & matrix (unchanged from v1)

```
PoC    = Novelty×3 + Scope×4 + Resources×2 + Outcome×1     (max 100)
Market = Pain×4    + Pay×3   + Size×2      + Moat×1        (max 100)
High   = score ≥ 65
```

| | High Market | Low Market |
|---|---|---|
| **High PoC** | 🚀 Go / Full Speed Ahead | 🔍 Validate Demand |
| **Low PoC** | 🧪 De-risk First | 🛑 Reframe or Shelve |

## 5. Advanced tier (+5)

- **A · Memory bank** — every run appended to `memory/scores.json`. Before scoring, the orchestrator recalls the most similar past idea (token Jaccard similarity) and shows it.
- **B · Self-learning loop** — `/vscore-learn "<outcome>"` turns feedback (e.g. *"market scorers ran hot on B2C ideas"*) into a rule in `memory/lessons.md` under the right criterion. The orchestrator injects those rules into the matching scorer on the next run → the score changes.

## 6. Definition of Done (measurable)

| # | Check | How verified |
|---|---|---|
| D1 | 8 scorer agents exist, one per criterion, each with a trigger-sharp `description` | `.claude/agents/*-scorer.md` (8 files) |
| D2 | Every scorer returns valid JSON `{criterion, score∈[1,10] int, reason≠""}` | `score.py` rejects invalid input (tests) |
| D3 | Weights/sums correct: all 10s → 100/100 · all 1s → 10/10 | `tests/test_score.py` |
| D4 | Matrix correct incl. boundary: exactly 65 → High; 64 → Low | `tests/test_score.py` |
| D5 | All 4 quadrants reachable | `tests/test_score.py` |
| D6 | Live run prints both scores, verdict, and 8 reasons | `/vscore "<idea>"` |
| D7 | Reference ideas land in expected quadrant: Slack bot → Go · translation earbuds → De-risk First · "AI for everything" → Shelve | live runs |
| D8 | Memory: `scores.json` grows by 1 per run; similar idea recalled | live run |
| D10 | Verdicts within ±5 of 65 on either axis are flagged ⚠️ Borderline (low confidence) | `tests/test_score.py` (TestBorderline) |
| D12 | Each criterion = median of N blind samples (default 3); reason taken from the median sample; spread reported | `tests/test_score.py` (TestMedianOfSamples) |
| D11 | Calibration exam: reference ideas re-checked after every rubric/lesson change | `/vscore-eval` |
| D9 | Self-learning: lesson added → next run of same idea shifts that criterion's score | live run |
