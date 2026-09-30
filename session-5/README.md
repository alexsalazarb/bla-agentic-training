# Session 5 — Agent Orchestration, MCP & CLI Tools

**Deliverable (1 of 2 this week): integration strategy.** List every MCP server, find the three most-called tools of each, convert one read-heavy candidate into a shell wrapper + skill, and measure the context difference.

- Inventory + real call counts: [`evidence/mcp-inventory.md`](evidence/mcp-inventory.md)
- Wrapper: [`skills/jira-read/scripts/jira-read`](skills/jira-read/scripts/jira-read) (curl + jq, ~100 lines)
- Skill: [`skills/jira-read/SKILL.md`](skills/jira-read/SKILL.md)
- Before/after measurement: [`evidence/measurement.md`](evidence/measurement.md), reproducible with [`evidence/measure.sh`](evidence/measure.sh)

> Context: same as previous sessions — real work on the Syncro MSP mobile app (Flutter + ai-framework), trainer-approved. The wrapper is generic: site, email and token come from a private config file and the macOS Keychain, so nothing here needed sanitizing except ticket keys in the evidence.

## 1. Inventory (Discover + Analyze)

Counted from 102 real transcripts, not guessed. Top external tool by far:

| Server | Top tool | Calls | Verdict |
|---|---|---|---|
| Atlassian | `getJiraIssue` | 53 | **Convert** — frequent, same shape, read-only |
| Atlassian | `addCommentToJiraIssue` | 34 | Keep MCP — schema-validated write, ADF mentions |
| Engram | `mem_judge` / `mem_save` | 163 / 142 | Keep MCP — local, writes |
| Firebase | `crashlytics_get_report` | 9 | Keep MCP — complex, infrequent |
| Gmail, Drive, Calendar, Trivago, Figma | — | 0 | Connected, never used |

## 2. Convert + Wrap

`jira-read issue <KEY>` and `jira-read search '<JQL>'`:

- Asks the API for **13 fields** instead of 156, converts Atlassian Document Format to plain text, keeps the last N comments.
- Site/email from `~/.config/jira-read/env`, token from Keychain. No secret in the repo or the script.
- Non-200 → `HTTP <code>` + Jira's error message on stderr, exit 1. The skill tells the model not to silently fall back to MCP.
- Tested outside Claude Code first: issue, search and 404 paths.

The skill routes **reads → CLI, writes and discovery → MCP**, following the session's rule. It is installed at user level (`~/.claude/skills/jira-read` → symlink to this folder), so the working repo was not touched.

## 3. Measurement

Same prompt, two headless sessions each, one MCP-only and one skill-only:

| | MCP | CLI skill | Δ |
|---|---|---|---|
| Tool calls | 3 (ToolSearch, cloud-ID lookup, getJiraIssue) | 2 (Skill, Bash) | −1 |
| Tool payload | 14,997 chars | 5,965 chars | **−2.5×** |
| Input tokens (cumulative) | ~116k | ~100k | **−15.7k (−13.5%)** |
| Output tokens | ~1,100 | ~720 | −33% |
| Static cost of being connected | ~1.1k tokens | 0 | — |

## 4. Surprising finding (for the room)

**I could not reproduce the 275×.** Claude Code now defers MCP tool schemas behind `ToolSearch`, so a connected server costs ~1.1k tokens of tool names, not 55k. The tax moved: it is paid **per call** (schema load + discovery call + fat payload) and it **compounds**, because every later turn re-sends it. ~9k extra characters of payload became ~15.7k extra input tokens in a 4-turn task.

Second one: **auth is the hidden cost of leaving MCP.** OAuth hid it completely. Four failed attempts before the first HTTP 200 — wrong login email, a secret silently truncated at 128 chars by macOS `getpass()`, an empty secret because Claude Code's `!` has no TTY, and the clipboard holding the command instead of the token. Details in [`evidence/measurement.md`](evidence/measurement.md#findings).

## 5. Takeaways

1. Measure before converting. The headline number came from an older loading model; my real saving is ~13% per read, not 99%.
2. The conversion pays in long sessions with many reads, because the per-call cost is re-sent every turn.
3. Keep MCP for what it is good at — discovery and validated writes — and route the boring 80% through a script.
4. The biggest item in my context is not any tool: it is a ~100k shared baseline. That is the next audit.
