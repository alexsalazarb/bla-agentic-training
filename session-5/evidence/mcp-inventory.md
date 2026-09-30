# MCP inventory and real usage

Date: 2026-09-29. Servers from `claude mcp list`. Call counts come from every tool call in my 102 local Claude Code transcripts (`~/.claude/projects/**/*.jsonl`), counted with `jq`, not from memory:

```bash
fd -e jsonl . ~/.claude/projects -X jq -r 'select(.type=="assistant") | .message.content[]?
  | select(.type=="tool_use") | .name | select(startswith("mcp__"))' | sort | uniq -c | sort -rn
```

## Connected servers — top 3 tools

| Server | Transport | #1 | #2 | #3 | Read or write? |
|---|---|---|---|---|---|
| **Atlassian** (Jira/Confluence) | remote | `getJiraIssue` **53** | `addCommentToJiraIssue` 34 | `editJiraIssue` 7 | #1 is a **read** → CLI candidate |
| Engram (memory) | local stdio | `mem_judge` 163 | `mem_save` 142 | `mem_search` 78 | Mostly writes, local, small payloads → keep MCP |
| Firebase | local (npx) | `crashlytics_get_report` 9 | `crashlytics_batch_get_events` 7 | `crashlytics_get_issue` 5 | Reads, but infrequent → keep MCP (complex, infrequent) |
| Claude Docs | remote | `update` 5 | `batch` 2 | `guide` 1 | Writes → keep MCP |
| Figma | remote | 0 | — | — | Designer workflows; unused by me so far |
| Gmail, Google Drive, Google Calendar, Trivago | remote | 0 | — | — | **Connected but never used** |

11 more servers are listed but not authenticated (Slack, Box, Canva, Zapier ×2, Granola, Vercel, Supabase, Apollo, Float, Gamma) and contribute nothing.

## Pick

**`getJiraIssue`** (+ `searchJiraIssuesUsingJql`, same family): my most-called external tool, always the same shape (one key in, summary/status/comments out), read-only. Textbook "frequent, predictable read".

Kept on MCP on purpose:
- `addCommentToJiraIssue` / `editJiraIssue` / `createJiraIssue` — schema-validated **writes**, and comments need ADF for mentions.
- Engram — local process, no network, the calls are writes.
- Firebase Crashlytics — complex and infrequent; setup would not amortize.

## Side finding

5 connected servers with 0 calls. With deferred tool loading their cost is small (≈ tool names only), but it is not zero and it is pure noise in the tool list — candidates for disconnecting.
