#!/bin/bash
# Simple bash command logger for testing hooks

# Read JSON from stdin and log the bash command
echo "=== Hook triggered at $(date) ===" >> ~/.claude/bash-command-log.txt
jq -r '"Command: \(.tool_input.command // "unknown") | Description: \(.tool_input.description // "no description")"' >> ~/.claude/bash-command-log.txt 2>&1

# Always exit 0 to not block execution
exit 0