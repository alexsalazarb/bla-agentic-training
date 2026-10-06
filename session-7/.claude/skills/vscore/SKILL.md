---
name: vscore
description: V-Score orchestrator. Use when the user wants to score, validate, or get a Go/No-Go verdict on a product or PoC idea written in plain English ("/vscore <idea>", "score this idea", "is this worth building?"). Fans out to 8 blind scorer sub-agents in parallel, then weights, sums and maps to the PoC × Market recommendation matrix.
---

# V-Score Orchestrator

You COORDINATE. You never score a criterion yourself and you never do the arithmetic yourself.

Input: `$ARGUMENTS` = the idea in plain English. If empty, ask for the idea and stop.

Optional flag `--samples N` (default **3**): how many blind scorers per criterion. The aggregator takes the median, which damps run-to-run variance. Use `--samples 1` for a fast single-pass run.

## Step 0 — Recall (memory bank)

```bash
python3 scripts/score.py recall "<idea>"
```

Keep the result for the report (most similar past idea, its scores and verdict).

## Step 1 — Load lessons (self-learning)

Read `memory/lessons.md`. For each criterion, collect the bullet rules under its `## <criterion>` heading (may be empty).

## Step 2 — Fan out (PARALLEL, BLIND)

Launch **N independent instances of each scorer** (N = `--samples`, default 3). Every instance is blind to the others, including its own siblings.

Claude Code runs at most **20 sub-agents concurrently**, so:
- N = 1 → all 8 in ONE message.
- N = 3 → two waves: **wave 1 = the 4 PoC scorers × 3 (12 agents) in one message**, then **wave 2 = the 4 Market scorers × 3 (12 agents) in one message**.

Never launch them one by one.

| subagent_type | criterion |
|---|---|
| `novelty-scorer` | novelty |
| `scope-scorer` | scope |
| `resources-scorer` | resources |
| `outcome-scorer` | outcome |
| `pain-scorer` | pain |
| `pay-scorer` | pay |
| `size-scorer` | size |
| `moat-scorer` | moat |

Each prompt contains ONLY:

```
idea: <idea verbatim>
lessons:
- <rules for THIS criterion only, or "none">
```

Never pass one scorer's output, other criteria, or your own opinion to another scorer. Blindness is the point.

## Step 3 — Verify scorer output

Parse each response as JSON `{"criterion", "score", "reason"}`. If a scorer returns invalid JSON, a non-integer, a value outside 1-10, or an empty reason → re-launch **that instance only** once, telling it what was wrong. Never patch the number yourself, and never pick the median yourself — the aggregator does it.

## Step 4 — Aggregate (deterministic code)

Pipe the payload to the aggregator; `--save` appends the run to the memory bank:

```bash
python3 scripts/score.py aggregate --save <<'JSON'
{"idea": "<idea>", "scores": {
  "novelty":   {"score": N, "reason": "..."},
  "scope":     {"score": N, "reason": "..."},
  "resources": {"score": N, "reason": "..."},
  "outcome":   {"score": N, "reason": "..."},
  "pain":      {"score": N, "reason": "..."},
  "pay":       {"score": N, "reason": "..."},
  "size":      {"score": N, "reason": "..."},
  "moat":      {"score": N, "reason": "..."}
}}
JSON
```

With N > 1, send every instance's output as `samples` instead (the aggregator takes the median and keeps the reason of the median sample):

```json
"pain": {"samples": [{"score": 6, "reason": "..."}, {"score": 8, "reason": "..."}, {"score": 7, "reason": "..."}]}
```

If it exits non-zero, go back to Step 3 for the criterion it names.

## Step 5 — Report

Print the aggregator's markdown verbatim (both scores, 8 reasons, verdict), then:

- **Similar past idea** (from Step 0): idea, PoC/Market, verdict — or "first of its kind".
- **Lessons applied**: which criteria had lessons injected this run.
- **Disagreement**: any criterion whose samples spread ≥ 3 points — the scorers read the idea differently there; name it.
- One plain-language sentence on the verdict: what the team should do next. If the aggregator flagged **⚠️ Borderline**, say so explicitly and name which heavy criterion (×3/×4) on that axis would flip the verdict with a one-point change.
