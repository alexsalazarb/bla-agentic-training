---
name: jira-read
description: >
  Read Jira issues and run JQL searches through a local curl + jq script instead of the Atlassian MCP.
  Trigger: whenever you need to READ Jira — view a ticket, its status, description or comments, check
  what a ticket says, list my tickets, or search by JQL (e.g. "check PROJ-123", "qué dice el ticket",
  "what's the status of", "my open tickets"). Not for writes.
license: MIT
metadata:
  author: alex-salazar
  version: "1.0"
---

## When to use

| Need | Use |
|------|-----|
| Read one issue (summary, status, assignee, links, description, comments) | `jira-read issue <KEY>` |
| More or fewer comments | `jira-read issue <KEY> --comments 10` |
| List / search issues | `jira-read search '<JQL>' --max 20` |
| **Write**: add comment, create, edit, transition, link | Atlassian MCP (schema-validated writes, ADF mentions) |
| Explore unknown fields, Confluence, issue-type metadata | Atlassian MCP (discovery) |

Always prefer this skill over `getJiraIssue` / `searchJiraIssuesUsingJql` for reads: it returns only
the fields that matter (~8 KB for a ticket with 5 comments instead of ~40 KB of raw JSON with 150+ fields).

## Commands

The script lives next to this file: `scripts/jira-read`. Run it with Bash:

```bash
~/.claude/skills/jira-read/scripts/jira-read issue PROJ-123
~/.claude/skills/jira-read/scripts/jira-read issue PROJ-123 --comments 2
~/.claude/skills/jira-read/scripts/jira-read search 'assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC' --max 10
```

`search` prints one tab-separated line per issue: `KEY  status  type  assignee  updated  summary`.
Need the details of one of them? Follow up with `issue <KEY>`.

## Output (issue)

```
PROJ-123 · Task · In Progress · High
Summary:  ...
Assignee: ...  |  Reporter: ...
Labels:   ...  |  Parent: ...
Updated:  ...  |  Created: ...
Links:    blocks PROJ-124; split from PROJ-100
## Description
...plain text (ADF converted)...
## Comments (last 5 of N)
--- Author · date · id 12345
...
```

## Errors

- `HTTP 401` → token missing/expired/truncated. Tell the user; do not retry. The token lives in the macOS
  Keychain item `atlassian-api-token` (the user rotates it; never print it).
- `HTTP 404` → wrong key or no permission. Ask the user to confirm the key.
- `set JIRA_SITE` / `set JIRA_EMAIL` → config missing in `~/.config/jira-read/env`. Tell the user.
- On any error, do NOT fall back silently to the MCP for the same read — report it first.

## Rules

- Read-only. Never build curl write calls by hand; use the MCP for writes.
- Never echo the token or the config file contents.
- Quote JQL in single quotes.
