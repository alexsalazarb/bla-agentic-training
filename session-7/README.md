# V-Score Validator v2 — Team 5

An agent team that scores a plain-English idea on **PoC Viability** and **Market Viability**, and gives a verdict with the reasoning behind each score.

**LLMs reason, code calculates.** 8 blind scorer sub-agents produce `{score, reason}`; a tested Python aggregator does the weights, the ≥65 matrix, and flags low-confidence verdicts.

## Layout

```
SPEC.md                         1 · Spec — brief, agent breakdown, Definition of Done (D1–D12)
AGENTS.md                           Who does what and what makes it fire
.claude/agents/*-scorer.md      2 · 8 blind scorers: rubric + calibration examples
.claude/skills/vscore/          3 · Orchestrator — recall → lessons → fan out → validate → aggregate
.claude/skills/vscore-learn/    + · Self-learning loop → memory/lessons.md
.claude/skills/vscore-eval/         Calibration exam over evals/reference-ideas.json
scripts/score.py                    Validate · median · weight · sum · matrix · borderline · memory
tests/test_score.py                 26 tests
memory/scores.json              + · Memory bank (grows 1 entry per run)
memory/lessons.md               + · Learned rules, injected per scorer
demo/sample-run.md              4 · Real runs + calibration story (backup for the live demo)
```

## Run

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
| 2:20–3:00 | `demo/sample-run.md` → *Calibration story* | "Tests proved the math; only running the agents on reference ideas exposed calibration. We fixed noise (examples + median), kept the honest miss, and the system now tells you when it's not sure." |

### Likely judge questions

- **"Why not Go on the Slack bot?"** — 3 measurement methods, always Market 63–64, unanimous scorers, flagged borderline. Tuning the rubric to hit Go would be overfitting.
- **"Why is math in Python?"** — The brief scores via agents; the arithmetic is trivial and must be *verifiably* correct. Tests > an LLM adding numbers.
- **"Why sub-agents and not one agent with skills?"** — Blindness. A shared context lets one criterion halo-inflate another.
