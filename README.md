# BLA Agentic Engineering Training — Alex Salazar

This is the repo for all my work in the BLA Agentic Engineering Training. Every session deliverable lives here.

## Why a separate repo

The exercises come from my real work on a client project: the **Syncro MSP mobile app** (Flutter), built with the ai-framework (plans, SDD, KB layers and Engram memory). The trainer approved using this project.

The client's source code and working repo are **private and stay private**. This repo exists so I never have to share them:

| Stays in the private client repo | Published here |
|---|---|
| Source code, app configuration, build and signing setup | Nothing from these |
| Internal IDs, URLs, ticket keys, people's names | `<PLACEHOLDERS>` and roles ("backend lead") |
| Original skills, memories, KB docs | Sanitized copies, each marked "Public copy" at the top |
| Real commits and logs | Only the evidence a deliverable needs, reviewed before publishing |

Before each push, everything here goes through the sanitization scan defined in [`CLAUDE.md`](CLAUDE.md).

## Sessions

| Session | Topic | Deliverable |
|---|---|---|
| 3 | Skills, Hooks & Commands | [Skill + triggering observation](session-3/) |
| 4 | Memory & Self-Improvement | [memory-bank + self-improvement loop](session-4/) |
| 5 | Agent Orchestration, MCP & CLI Tools | [MCP inventory + Jira CLI wrapper/skill + before/after measurement](session-5/) |
| 6 | Designer & QA Workflows (QA track) | [Test generation workflow: 18 tests for an untested utility](session-6/) |
| 7 | Capstone (Team 5) | [V-Score Validator v2: orchestrator + 8 blind scorer sub-agents, tested aggregator, memory + self-learning](session-7/) |

Each session folder contains a `README.md` (what was asked, what I built, what I observed), an `evidence/` folder, and the artifacts.

Repo rules for humans and agents: [`CLAUDE.md`](CLAUDE.md)
