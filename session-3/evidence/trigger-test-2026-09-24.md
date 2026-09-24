<!-- Public copy: absolute paths generalized; raw stream-json logs kept private (they include memory search results with names). -->

# Trigger reliability test — 2026-09-24

## Setup

- Each phrase ran in a **fresh headless session**: `claude -p "<phrase>" --output-format stream-json --verbose --no-session-persistence`
- Claude Code 2.1.281, model Opus 5.5, run from the working repo root (same skills as the real setup)
- **Sandboxed** so a positive trigger could not cause side effects: `--permission-mode default` plus
  `--disallowedTools Bash Edit Write NotebookEdit Agent Workflow mcp__claude_ai_Atlassian`
  (no Jira ticket can be created, no build can be bumped or pushed)
- Detection: the `tool_use` events in the stream. A model-invoked skill shows up as a `Skill` tool call.
  A user-typed slash command injects the skill body directly, so it shows up as the model following the skill's steps.

## Results

| # | Phrase | Tool calls observed (in order) | Verdict |
|---|---|---|---|
| 1 | "crea un spike para investigar el crash de login" | `Skill(syncro-create-ticket, args="spike: investigar el crash de login")` → `ToolSearch("atlassian jira createJiraIssue")` | ✅ Fired, spike type inferred |
| 2 | "I need to report a bug in Jira" | `Skill(syncro-create-ticket, args="bug")` → `ToolSearch("atlassian jira create issue")` | ✅ Fired, bug type inferred |
| 3 | "what is a spike?" | none; plain explanation of spikes in 1 turn | ✅ Did not fire |
| 4 | "when is the new build coming?" | `mem_search("release build version")` → `Grep(pubspec version)` → `Grep(.plans, "next build / ETA")` | ✅ `syncro-create-qa-build` not invoked; answered read-only |
| 5 | `/syncro-create-qa-build` | skill body loaded → `Grep(pubspec version)` → `Read(.git/HEAD)`; then stopped: no shell to bump/commit/push | ✅ Ran normally (up to the sandbox wall) |

In runs 1 and 2 the skill then tried to reach Jira and reported the connector missing. That was the sandbox working as intended, not a skill failure.

## Notes

- The `init` event lists `syncro-create-qa-build` in `skills` even with `disable-model-invocation: true`. That field is the full catalog, so it does **not** prove the skill is hidden from the model. The behavioral evidence is run 4: a phrase semantically close to "new build" did not invoke it.
- Run 4 is the dangerous case from §4. Without the flag, "new build" sits close to the skill's triggers ("nuevo build", "crear build").
- One run per phrase. It shows the triggers work, not a reliability rate. Repeat N times per phrase to measure a rate.
