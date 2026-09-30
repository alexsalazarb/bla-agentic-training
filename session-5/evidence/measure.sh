#!/usr/bin/env bash
# Runs the same Jira read task via MCP-only and CLI-skill-only sessions, N times each.
set -uo pipefail
cd "$(dirname "$0")"
KEY="${1:?usage: measure.sh <ISSUE-KEY> [runs]}"
N="${2:-2}"
PROMPT="Read Jira issue $KEY and tell me: its status, its assignee, which issues it blocks, and a one-line summary of each of the last 3 comments."

run() {
  local mode="$1" i="$2"
  local out="run-$mode-$i.jsonl"
  if [[ "$mode" == "mcp" ]]; then
    claude -p "$PROMPT" --output-format stream-json --verbose \
      --allowedTools "mcp__claude_ai_Atlassian__getJiraIssue mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql mcp__claude_ai_Atlassian__getAccessibleAtlassianResources ToolSearch" \
      --disallowedTools "Bash Skill Edit Write NotebookEdit Agent Workflow" > "$out" 2>/dev/null
  else
    claude -p "$PROMPT" --output-format stream-json --verbose \
      --allowedTools "Skill Bash(~/.claude/skills/jira-read/scripts/jira-read:*) Bash($HOME/.claude/skills/jira-read/scripts/jira-read:*) Read" \
      --disallowedTools "mcp__claude_ai_Atlassian Edit Write NotebookEdit Agent Workflow" > "$out" 2>/dev/null
  fi
}

for i in $(seq 1 "$N"); do run mcp "$i"; run cli "$i"; done

printf 'run\tturns\tinput+cache_tokens\toutput_tokens\tcost_usd\ttool_calls\ttool_result_chars\tresult_ok\n'
for f in run-*.jsonl; do
  jq -rs --arg f "${f%.jsonl}" '
    (map(select(.type=="result")) | last) as $r
    | ([.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name]) as $calls
    | ([.[] | select(.type=="user") | .message.content[]? | select(type=="object" and .type=="tool_result")
        | (.content | if type=="string" then length else (map(.text // "" | length) | add // 0) end)] | add // 0) as $chars
    | [$f, $r.num_turns,
       (($r.usage.input_tokens // 0) + ($r.usage.cache_read_input_tokens // 0) + ($r.usage.cache_creation_input_tokens // 0)),
       $r.usage.output_tokens, ($r.total_cost_usd | . * 10000 | round / 10000),
       ($calls | join(",")), $chars, ($r.is_error | not)] | @tsv' "$f"
done
