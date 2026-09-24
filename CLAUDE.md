# CLAUDE.md — bla-agentic-training

Public repo with my deliverables for the BLA Agentic Engineering Training. Each session's deliverable is distilled from my real work on the Syncro MSP mobile app (Flutter + ai-framework). The working repo stays private.

## Never-ever rules

1. **This repo is PUBLIC.** Before committing, never include:
   - Jira cloud IDs, custom field IDs, account IDs or ticket keys (`SE-12345`)
   - Internal or staging URLs, the Atlassian site, Firebase or GCP project names
   - Signing material: keystores, passwords, Apple Team/App IDs, SHA-256 fingerprints
   - People's names. Use roles instead ("backend lead", "product owner").

   Replace these with `<PLACEHOLDERS>` or generalize.
2. Copies of private files must say so in a comment at the top ("Public copy: IDs replaced...").
3. Every deliverable needs **evidence that it works**: a commit diff, a log or a screenshot, stored in `session-N/evidence/`.
4. Conventional commits, with no AI attribution lines.

## Structure

```
session-N/
├── README.md     ← what was asked, what I built, observations
├── evidence/     ← diffs, logs, screenshots
└── <artifacts>   ← skills/, memory-bank/, hooks, etc.
```

## Pre-commit check

Run this sanitization scan and review every hit before committing:

```bash
rg -n -i 'SE-[0-9]|customfield_[0-9]|atlassian\.net|cloudId: *[0-9a-f]|[0-9a-f]{8}-[0-9a-f]{4}-|keystore|password|sha-?256' .
```

## Writing style

English. Short sections, tables over prose, facts only. Mark unknowns as open questions instead of guessing.
