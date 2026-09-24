# Session 3 — Skills, Hooks & Commands

**Deliverable:** one skill from my own workflow, plus one observation on over-triggering and under-triggering.

- Skill: [`skills/syncro-create-ticket/SKILL.md`](skills/syncro-create-ticket/SKILL.md) (contextual `SKILL.md`)
- Evidence: [`evidence/commit-7d8040a.diff`](evidence/commit-7d8040a.diff), the real commit from my working repo

> Context: I work on the Syncro MSP mobile app (Flutter) with the ai-framework. The trainer approved using this project. The working repo is private, so this is a sanitized copy: Jira IDs and internal URLs are replaced with `<PLACEHOLDERS>`.

## 1. The repeated context

I create Jira tickets for the Syncro mobile team several times a week. The fixed fields never change: project `SE`, label `mobile`, team Sculpin (a custom field), plus the title format `Mobile App: {Title}`. Without a skill, I restated these every time or corrected the model when it guessed.

## 2. Why a SKILL.md and not a /command

I want the skill to fire from natural phrases like "crea un spike para X" or "create a bug ticket". It should also fire from `/create-plan` when I ask for a ticket in the same message. That calls for semantic triggering, so I chose a contextual `SKILL.md`.

## 3. Observation: under-triggering

**The skill almost never fired on its own.** The file started with `# syncro-create-ticket` and had no YAML frontmatter. Every trigger phrase lived in the body.

The model decides whether to load a skill from its `description` alone, and reads the body only after the skill is loaded. So this is the skill list it received:

```
Before:
- syncro-create-ticket: syncro-create-ticket

After:
- syncro-create-ticket: Creates a Jira issue (spike, bug, feature/story, task) in the SE
  project for the Syncro mobile team... Trigger: "create a ticket", "crea un spike", ...
```

**Fix:** add frontmatter with `name` and a `description` that carries the triggers. The skill list updated in the same session.

## 4. Contrast: over-triggering

Two other workflow skills have the opposite risk:

| Skill | Risk | Cost of a mistake | Fix |
|---|---|---|---|
| `syncro-create-ticket` | Under-triggering | I type the slash command by hand | Broad description with triggers |
| `syncro-create-qa-build` | Over-triggering | Force-push to two shared remotes | `disable-model-invocation: true` |
| `syncro-create-release` | Over-triggering | Signed production build | `disable-model-invocation: true` |

`syncro-create-qa-build` triggers on "nuevo build" or "crear build". A casual question like "when is the new build coming?" could match. For that blast radius a better description is not enough, so the flag removes the skill from the model's list entirely. It runs only when I type `/syncro-create-qa-build`. This is the same "soft rule vs. hard enforcement" idea from the session, applied to skills.

## 5. Trigger reliability test

Each phrase ran in a fresh headless session (`claude -p`), with write, shell and Jira tools blocked so a trigger could not cause side effects. Details and tool-call traces: [`evidence/trigger-test-2026-09-24.md`](evidence/trigger-test-2026-09-24.md).

| Phrase | Expected | Result |
|---|---|---|
| "crea un spike para investigar el crash de login" | Fires `syncro-create-ticket` | ✅ Fired (`Skill` call, type spike) |
| "I need to report a bug in Jira" | Fires `syncro-create-ticket` | ✅ Fired (`Skill` call, type bug) |
| "what is a spike?" | Does not fire | ✅ Not fired; plain answer |
| "when is the new build coming?" | Does not run `syncro-create-qa-build` | ✅ Not invoked; read-only answer |
| `/syncro-create-qa-build` | Runs normally | ✅ Ran; stopped at the sandbox (no shell) |

5/5 as expected, but only one run per phrase, so this is not a reliability rate. The `init` event still lists the flagged skill in its catalog; the proof that it is hidden is behavioral (row 4).

## 6. Takeaways

1. A contextual skill lives or dies by its `description`. Triggers written only in the body are invisible to the model.
2. The cost of a mistake is asymmetric. Guard destructive skills against over-triggering, and give harmless ones broad descriptions to avoid under-triggering.
3. For destructive actions, use a structural lock (`disable-model-invocation`), not prose like "do not trigger automatically".
4. I had applied this exact fix weeks earlier, but never committed it, and it was lost. A guardrail that is not committed does not exist.
