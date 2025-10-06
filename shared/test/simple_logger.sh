#!/bin/bash
# Simple logger to test if hooks are being called at all

TIMESTAMP=$(date +%Y%m%d_%H%M%S_%N)
LOG_FILE="/home/brian/projects/goodwill/investigations/automated_workflow_planning/hook_inputs/${TIMESTAMP}_bash.log"

# Log that hook was called
echo "Hook called at ${TIMESTAMP}" >> "$LOG_FILE"
echo "PWD: $(pwd)" >> "$LOG_FILE"
echo "CLAUDE_PROJECT_DIR: $CLAUDE_PROJECT_DIR" >> "$LOG_FILE"
echo "All env vars with CLAUDE:" >> "$LOG_FILE"
env | grep CLAUDE >> "$LOG_FILE"

# Read stdin and log it
echo "STDIN content:" >> "$LOG_FILE"
cat >> "$LOG_FILE"

# Return success
echo '{"continue": true, "suppressOutput": true}'