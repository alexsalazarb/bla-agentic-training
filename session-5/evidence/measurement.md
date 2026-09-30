# Measurement — Atlassian MCP vs `jira-read` skill

Date: 2026-09-29 · Claude Code CLI, headless (`claude -p`), run from an empty directory so no project config applies.
Script: [`measure.sh`](measure.sh). Raw stream-json logs are **not** published (they contain names and ticket content); this file summarizes them.

## Task (same prompt in every run)

> Read Jira issue `<TICKET>` and tell me: its status, its assignee, which issues it blocks, and a one-line summary of each of the last 3 comments.

- **MCP run**: Atlassian MCP allowed, `Bash` and `Skill` disallowed.
- **CLI run**: `jira-read` skill + its script allowed, Atlassian MCP disallowed.

Both runs answered correctly (same status, assignee, blocked issue and comment summaries).

## 1. Per-task cost (2 runs each)

| Run | Tool calls | Tool result size (chars) | Input tokens (cumulative, incl. cache) | Output tokens | Cost (USD) |
|---|---|---|---|---|---|
| mcp-1 | ToolSearch → getAccessibleAtlassianResources → getJiraIssue | 14,997 | 115,733 | 1,055 | 0.3139 |
| mcp-2 | same | 14,997 | 116,626 | 1,139 | 0.2519 |
| cli-1 | Skill → Bash (`jira-read issue`) | 5,965 | 100,160 | 719 | 0.3104 |
| cli-2 | same | 5,965 | 100,742 | 723 | 0.2458 |

**Delta per read: ~15,700 input tokens (−13.5%), −2.5× tool payload, −33% output tokens, one fewer tool call.**
Cost is almost identical because both runs are dominated by the shared, cached baseline (~100k tokens of system prompt + instructions). Cost differences between run 1 and 2 are cache warm-up, not the tool.

## 2. Static cost of having the MCP connected

Trivial prompt ("Reply with just: ok"), nothing else called:

| Session | Input tokens |
|---|---|
| Atlassian MCP connected | 37,548 |
| Atlassian MCP disallowed | 36,452 |

**~1,100 tokens** just for being connected — the tool *names* only.

## 3. Raw API payload for context

| What | Size |
|---|---|
| `GET /rest/api/3/issue/<TICKET>` (all fields) | 40,069 bytes, 156 fields (mostly empty custom fields) |
| `jira-read issue <TICKET>` (13 fields, ADF → text, last 5 comments) | 8,799 bytes |

## Findings

1. **The 275× "MCP tax" did not show up here — ~1.1k tokens, not 55k.** Current Claude Code defers MCP tool schemas behind `ToolSearch`: only names sit in context until a tool is needed. The 275× figure assumes every schema is loaded up front.
2. **The real tax is per call, and it is cumulative.** The MCP run needed `ToolSearch` (loads the schemas) + a cloud-ID discovery call + a fatter payload. Every later turn re-sends all of it, so ~9k extra characters of payload became ~15.7k extra input tokens over 4 turns.
3. **The CLI removes discovery every time.** The MCP run called `getAccessibleAtlassianResources` on *every* run to find the cloud ID. The script has the site hard-configured. That call is exactly the "MCP earns its cost in discovery" part — paid again on every read.
4. **Auth is hidden cost you inherit.** With MCP, OAuth was invisible. Moving to CLI surfaced: the login email differs from my work email, macOS `getpass()` silently truncates secrets at 128 chars (Atlassian tokens are 192), interactive prompts don't work from Claude Code's `!` prefix (no TTY → empty secret), and `-w "$(pbpaste)"` stores whatever was copied last (it stored the command itself once). 4 failed attempts before the first HTTP 200.
5. **Where it matters most:** frequent reads in long sessions. At my measured rate (`getJiraIssue` is my #1 external MCP tool) the saving compounds per call and per turn; in a 1-read headless task it is modest.

## Open questions

- Measure a long real session (5–10 reads) to see the compounding effect instead of estimating it.
- Would trimming the ~100k baseline (global instructions) save more than any tool conversion? Probably yes — a finding for the Context Budget Audit exercise.
