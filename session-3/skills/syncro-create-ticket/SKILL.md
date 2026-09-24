---
name: syncro-create-ticket
description: >
  Creates a Jira issue (spike, bug, feature/story, task) in the SE project for the Syncro mobile team,
  applying fixed conventions (project SE, label mobile, team Sculpin) so the user is never asked for them.
  Trigger: "create a ticket", "crea un ticket", "nuevo ticket", "crea un spike", "crea un bug",
  "crea un feature", any request to open a Jira issue for Syncro mobile, or /create-plan when the user
  explicitly asks for a Jira ticket in the same message.
license: Apache-2.0
metadata:
  author: alex-salazar
  version: "1.0"
---

<!-- Public copy: IDs and internal URLs are replaced with <PLACEHOLDERS>. The private original holds the real values. -->

# syncro-create-ticket

## Context Required
LOW-CONTEXT: No codebase reading needed. Collects ticket details from the conversation.

## Triggers

### Automatic
- When executing `/create-plan` AND the user explicitly requests Jira ticket creation in the same message

### Manual
- "create a ticket" / "crea un ticket" / "nuevo ticket"
- "create a spike" / "crea un spike"
- "create a bug ticket" / "crea un bug"
- "create a feature ticket" / "crea un feature"
- Any request to open a Jira issue for the Syncro mobile project

---

## Syncro Ticket Conventions (fixed — never ask the user for these)

| Field        | Value                                          |
|--------------|------------------------------------------------|
| Jira Project | `SE` — Syncro Engineering                      |
| Cloud ID     | `<JIRA_CLOUD_ID>`                              |
| Label        | `mobile`                                       |
| Team         | Sculpin (`<TEAM_CUSTOM_FIELD>`, id `<TEAM_OPTION_ID>` — set via `additional_fields`) |

### Issue Type Mapping

| User requests | Jira issue type |
|---------------|-----------------|
| spike         | Task            |
| task          | Task            |
| feature       | Story           |
| bug           | Bug             |

Default when not specified: **Task**

### Title Format

| Target       | Format                          | Example                                      |
|--------------|---------------------------------|----------------------------------------------|
| General / FE | `Mobile App: {Title}`           | `Mobile App: Offline Mode Support`           |
| Backend (BE) | `Mobile App: BE - {Title}`      | `Mobile App: BE - Unified Counters Endpoint` |

---

## Instructions

### Step 1: Collect Required Information

Gather from the conversation. Ask ONLY what is missing — do not re-ask what was already provided.

**Required:**
- `type` — spike | task | feature | bug (default: task if omitted)
- `target` — general/FE or BE? (determines title prefix)
- `title` — raw title, without format applied yet
- `description` — background, context, objective

**Optional (include only if provided or requested):**
- `acceptance_criteria` — list of conditions that define done

Do NOT ask for project, team, labels, or cloud ID — always fixed.

### Step 2: Build the Ticket

1. Apply title format based on target
2. Map type to Jira issue type name
3. Compose description in markdown:

```markdown
## Description

{description content}

## Acceptance Criteria

{acceptance criteria — omit this entire section if not provided}
```

### Step 3: Create via Atlassian MCP

Call `mcp__claude_ai_Atlassian__createJiraIssue` with:

```
cloudId:              <JIRA_CLOUD_ID>
projectKey:           SE
issueTypeName:        {mapped Jira type}
summary:              {formatted title}
contentFormat:        markdown
description:          {composed description}
additional_fields:    { "labels": ["mobile"], "<TEAM_CUSTOM_FIELD>": { "id": "<TEAM_OPTION_ID>" } }
responseContentFormat: markdown
```

### Step 4: Report Result

Return to the user:
- Ticket key + clickable URL: `[SE-XXXXX](https://<JIRA_SITE>/browse/SE-XXXXX)`

---

## Output

- One-line ticket reference with clickable link
- Team assignment reminder
- No files created or modified
