---
name: vscore-learn
description: V-Score self-learning loop. Use when the user reports how a past V-Score run turned out or says a scorer was wrong ("/vscore-learn <outcome>", "the market scorer ran hot", "pay was too generous for B2C") — turns that outcome into a reusable rule in memory/lessons.md that the matching scorer applies on the next run.
---

# V-Score Learn

Input: `$ARGUMENTS` = an outcome or correction in plain English.

1. **Capture** — identify which criterion(s) it is about (`novelty, scope, resources, outcome, pain, pay, size, moat`). Ambiguous → ask and stop.
2. **Extract a pattern** — read `memory/scores.json`. Find the run(s) the outcome refers to and any other runs showing the same pattern. Cite them.
3. **Write a rule** — append ONE bullet under `## <criterion>` in `memory/lessons.md`:
   - generalizable (about a class of ideas, not one idea)
   - actionable (says which direction to move the score and when)
   - format: `- <rule> _(from: "<idea>", <YYYY-MM-DD>)_`
   Do not duplicate an existing rule — refine it instead.
4. **Confirm** — show the diff and tell the user: re-run `/vscore` on the same idea to see the score move.
