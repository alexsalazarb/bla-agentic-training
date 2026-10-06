---
name: vscore-eval
description: V-Score calibration exam. Use when the user wants to check whether the scorer agents still land the reference ideas in the expected quadrant ("/vscore-eval", "run the eval", "did the rubric change break anything?") — typically after editing a scorer rubric or adding a lesson. Runs every idea in evals/reference-ideas.json through the 8 scorers and prints expected vs actual.
---

# V-Score Eval

Regression tests for the agents: `tests/` proves the math, this proves the calibration.

1. Read `evals/reference-ideas.json` and `memory/lessons.md`.
2. **Fan out** — exactly as in Step 2 of the `vscore` skill, with the same `--samples N` (default 3): N blind instances per criterion, prompt = `idea` + that criterion's lessons only. Claude Code runs at most **20 sub-agents concurrently**, so send waves of ≤ 20 (e.g. one idea's PoC × 3, then its Market × 3) and launch the next wave when one finishes.
3. **Verify** each output as in Step 3 of `vscore` (re-launch an invalid scorer once).
4. **Aggregate** each idea WITHOUT `--save` (eval runs must not pollute the memory bank):
   `python3 scripts/score.py aggregate <<'JSON' … JSON`
5. **Report** a table, then one line per failure saying which criteria pulled it off target:

| id | expected | actual | PoC | Market | borderline | pass |
|---|---|---|---|---|---|---|

A pass on a borderline axis is a **fragile pass** — report it as such, not as solid.

End with `N/M passed`.
