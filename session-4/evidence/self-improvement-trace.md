# Evidence: self-improvement loop traces

<!-- Public copy: ticket keys and internal paths are generalized. The source files live in my private working repo. -->

Two real traces from my working repo show corrections turning into rules. The mechanism is the ai-framework's `log-mistake` skill plus my agent's feedback memory, since the course's `self:extract-insights` script is not available in my workspace.

## Trace 1: a rule promoted after three recurrences (Reflexion, supervised)

**Source:** `docs/kb-container/ai-patterns/mistake-log.md` (the `log-mistake` skill appends to it every time I correct the agent)

| Date | Signal (failure) | What was logged |
|---|---|---|
| 2026-06-04 | I corrected the agent: a bugfix was committed on an unrelated plan branch | Entry: "independent bugfixes branch from `develop`" |
| 2026-06-24 | I corrected the agent again: a feature branch was created from `main` | Entry: "`main` is vestigial (3 commits); base is `develop`" |
| 2026-09-09 | Recurrence: the `/create-plan` template itself defaulted to "Base Branch: main" | Recurrence note on the same entry. The executing agent caught it via a `git log` / merge-base check and self-corrected |

The skill's threshold rule is: *"If an error appears 3+ times, add it to AGENTS.md 'Things to Avoid'."* On the third occurrence the rule was **promoted**:

```markdown
<!-- docs/kb-projects/syncro-flutter/AGENTS.md — Things to Avoid -->
12. **Branching/basing work off `main`** - `main` is vestigial (3 commits, no Flutter source).
    ALWAYS branch from `develop`. This is a 3x-recurring mistake (2026-06-04, 2026-06-24,
    2026-09-09 in mistake-log.md) — verify with `git log --oneline -3 main` vs
    `git log --oneline -3 develop` before creating any branch if in doubt.
```

Commit trail in the private repo:

| Commit | Date | Change |
|---|---|---|
| `8ba4a17` | 2026-04-13 | First mistake-log entry (always use `fvm flutter`) |
| `d883e16` | 2026-06-04 | Log: bugfix on the wrong branch |
| `7c94746` | 2026-08-25 | Log: probed the shell for a CLI tool instead of checking the KB first |
| `cfd5c2c` | 2026-09-09 | Third recurrence: rule promoted to AGENTS.md "Things to Avoid" #12 |

**Mapping to the session's lifecycle:** mistake-log entry = **Proposed**. My approval plus promotion to AGENTS.md = **Accepted**. The rule is then loaded at every session start as semantic memory.

## Trace 2: a rule born and applied in a single session (2026-09-23)

1. **Signal:** I noticed that skill frontmatter said `author: gentleman-programming` instead of my name.
2. **Reflect:** the agent traced the root cause to the global `skill-creator` template, which hardcodes that value.
3. **Rule proposed and accepted:** the agent saved a feedback memory:
   > *Skills the user writes must set `metadata.author: alex-salazar`. Why: the skill-creator template hardcodes `gentleman-programming`. How to apply: override the template default on user-authored skills.*
4. **Applied:** fixed in all 4 skills in the same commit as the Session 3 deliverable (see [`../../session-3/evidence/commit-7d8040a.diff`](../../session-3/evidence/commit-7d8040a.diff)).

The same session also caught a **regression**. A fix applied weeks earlier had never been committed and was lost. The agent recorded it in memory as "always check the flag in the files, don't assume it's in place".

## Gaps compared with the session's model

| Session model | My setup | Gap |
|---|---|---|
| Score each session automatically (tool errors, retries) | Only human corrections trigger a log | No automatic scoring |
| Extract rules by comparing high- and low-quality runs | Human-noticed patterns, with a 3x threshold | No trajectory comparison |
| Unused rules archived after 60 days | Not implemented | Rules only accumulate. `mistake-log.md` has no expiry |
| Rules injected via the `UserPromptSubmit` hook | Rules loaded from AGENTS.md at session start | Works, but it's soft enforcement |
