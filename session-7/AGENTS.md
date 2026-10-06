# Agents & Skills

Who does what, and what makes each one fire.

## Entry points (skills — run in the main session)

The orchestrator lives in the **main session**, not in a sub-agent: sub-agents cannot spawn other sub-agents.

| Command | File | Fires when… | Does |
|---|---|---|---|
| `/vscore <idea> [--samples N]` | `.claude/skills/vscore/SKILL.md` | the user wants an idea scored / a Go-No-Go verdict | recall → load lessons → fan out N×8 blind scorers → validate → `score.py` → report |
| `/vscore-learn <outcome>` | `.claude/skills/vscore-learn/SKILL.md` | the user says a scorer was wrong or reports how an idea turned out | writes one generalizable rule to `memory/lessons.md` under the right criterion |
| `/vscore-eval` | `.claude/skills/vscore-eval/SKILL.md` | after changing a rubric or lesson ("did I break anything?") | runs `evals/reference-ideas.json` through the scorers, expected vs actual |

## Scorers (sub-agents — one per criterion, blind)

Each returns ONLY `{"criterion", "score": 1-10, "reason"}`. Each has a 4-band rubric plus 4 calibration examples (one per quadrant).

| Agent | Axis | × | Scores… |
|---|---|---|---|
| `novelty-scorer` | PoC | 3 | how **proven** the tech is — inverted: commodity = 10, research = 1 |
| `scope-scorer` | PoC | 4 | how narrowly it can be cut into one PoC |
| `resources-scorer` | PoC | 2 | whether tools/APIs/data are ready today |
| `outcome-scorer` | PoC | 1 | whether success is visible in a demo |
| `pain-scorer` | Market | 4 | how acute, frequent and costly the problem is |
| `pay-scorer` | Market | 3 | whether a specific buyer will pay |
| `size-scorer` | Market | 2 | whether the reachable market is big enough |
| `moat-scorer` | Market | 1 | how defensible it is against copycats |

The `description` frontmatter of each scorer says *"Use ONLY when the /vscore orchestrator needs the '<key>' criterion scored … Do not use for other criteria."* — that is what routes each criterion to exactly one agent.

## Deterministic code

| File | Role |
|---|---|
| `scripts/score.py aggregate [--save]` | validate → median of samples → weight → sum → matrix → ⚠️ borderline (±5 of 65) → report; `--save` appends to the memory bank |
| `scripts/score.py recall "<idea>"` | most similar past run (token Jaccard) |
| `tests/test_score.py` | 26 tests: weights, 65/64 boundary, 4 quadrants, validation, median, borderline, memory |

## Memory

| File | Written by | Read by |
|---|---|---|
| `memory/scores.json` | `score.py aggregate --save` | `score.py recall` (Step 0 of `/vscore`) |
| `memory/lessons.md` | `/vscore-learn` | `/vscore` Step 1 → injected into the matching scorer only |

## Gotchas

- **Agent edits need a restart.** Claude Code loads `.claude/agents/` at startup; edits mid-session are not picked up. `/exit` → `claude --continue`.
- **Max 20 concurrent sub-agents.** `--samples 3` (24 agents) runs in two waves: PoC × 3, then Market × 3.
