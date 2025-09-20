Implement all tasks in CLAUDE.md with verification. Continue until all tasks complete without stopping.

## Implementation Workflow

Execute tasks systematically with evidence collection and verification.

```bash
# Create implementation session
IMPL_SESSION="logs/implement_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$IMPL_SESSION"

# For complex tasks requiring investigation
# mkdir -p investigation/implementation_[task_name]/{docs,tools,debug}

echo "Implementation session: $IMPL_SESSION"
```

## Core Implementation Loop

### 1. Task Identification and Planning
```bash
# Read current tasks from CLAUDE.md
CLAUDE_MD="/home/brian/projects/autocoder4_cc/CLAUDE.md"

if [ -f "$CLAUDE_MD" ]; then
    # Extract current priority tasks
    grep -A 10 "^## 🎯\|^## Current\|^## Immediate" "$CLAUDE_MD" | head -15 | tee "$IMPL_SESSION/current_tasks.log"
    
    # Extract pending task list
    grep -E "^\- \[ \]|^[0-9]+\. \[ \]" "$CLAUDE_MD" | head -10 | tee "$IMPL_SESSION/task_list.log"
    
    TASK_COUNT=$(wc -l < "$IMPL_SESSION/task_list.log")
    echo "Found $TASK_COUNT pending tasks"
else
    echo "❌ No CLAUDE.md found - run /load_next_phase or /update_plans first"
    exit 1
fi
```

### 2. Systematic Task Execution
```bash
# Execute each task with verification
TASK_NUM=1

while IFS= read -r task; do
    if [ -n "$task" ]; then
        echo "=== TASK $TASK_NUM ===" | tee -a "$IMPL_SESSION/execution.log"
        echo "Task: $task" | tee -a "$IMPL_SESSION/execution.log"
        
        # Extract task description (remove checkbox)
        CLEAN_TASK=$(echo "$task" | sed 's/^- \[ \] *//' | sed 's/^[0-9]*\. \[ \] *//')
        
        # Create task-specific log
        TASK_LOG="$IMPL_SESSION/task_${TASK_NUM}.log"
        
        echo "Implementing: $CLEAN_TASK" | tee "$TASK_LOG"
        echo "Started: $(date)" | tee -a "$TASK_LOG"
        
        # NOTE: LLM implements specific task here based on CLAUDE.md instructions
        # This is where the actual implementation work happens
        echo "Implementation commands for: $CLEAN_TASK" | tee -a "$TASK_LOG"
        
        # Verification step
        echo "Verification needed for: $CLEAN_TASK" | tee -a "$TASK_LOG"
        
        # Mark completion
        echo "Completed: $(date)" | tee -a "$TASK_LOG"
        echo "Status: [SUCCESS/FAILED]" | tee -a "$TASK_LOG"
        
        TASK_NUM=$((TASK_NUM + 1))
    fi
done < "$IMPL_SESSION/task_list.log"
```

### 3. Verification and Evidence Collection
```bash
# Create implementation evidence
EVIDENCE_FILE="evidence/current/Evidence_Implementation_$(date +%Y%m%d).md"

cat > "$EVIDENCE_FILE" << EOF
# Implementation Evidence: $(date)

**Session**: $IMPL_SESSION
**Tasks Completed**: $((TASK_NUM - 1))
**Status**: [IN PROGRESS/COMPLETE]

## Task Summary
$(cat "$IMPL_SESSION/current_tasks.log")

## Implementation Results
$(for i in $(seq 1 $((TASK_NUM - 1))); do
    if [ -f "$IMPL_SESSION/task_${i}.log" ]; then
        echo "### Task $i"
        cat "$IMPL_SESSION/task_${i}.log"
        echo ""
    fi
done)

## Verification
- [ ] All identified tasks completed
- [ ] Each task verified successful
- [ ] Evidence documented
- [ ] No blocking errors

## Files Modified
[List files changed during implementation]

## Testing Results
[Results of any testing performed]

## Next Steps
[What should happen next]
EOF

echo "Implementation evidence: $EVIDENCE_FILE"
```

### 4. Final Verification and Cleanup
```bash
# Count successes vs failures
SUCCESS_COUNT=$(grep -c "Status: SUCCESS" "$IMPL_SESSION"/task_*.log 2>/dev/null || echo 0)
TOTAL_TASKS=$((TASK_NUM - 1))

echo "=== IMPLEMENTATION SUMMARY ===" | tee "$IMPL_SESSION/summary.log"
echo "Total tasks: $TOTAL_TASKS" | tee -a "$IMPL_SESSION/summary.log"
echo "Successful: $SUCCESS_COUNT" | tee -a "$IMPL_SESSION/summary.log"
echo "Session: $IMPL_SESSION" | tee -a "$IMPL_SESSION/summary.log"

if [ "$SUCCESS_COUNT" -eq "$TOTAL_TASKS" ] && [ "$TOTAL_TASKS" -gt 0 ]; then
    echo "✅ All tasks completed successfully" | tee -a "$IMPL_SESSION/summary.log"
    echo "Ready to update MVP_PLAN.md with completions" | tee -a "$IMPL_SESSION/summary.log"
else
    echo "⚠️ $((TOTAL_TASKS - SUCCESS_COUNT)) tasks need attention" | tee -a "$IMPL_SESSION/summary.log"
    echo "Review failed tasks before declaring completion" | tee -a "$IMPL_SESSION/summary.log"
fi

# Show next recommended action
echo ""
echo "=== NEXT STEPS ==="
if [ "$SUCCESS_COUNT" -eq "$TOTAL_TASKS" ] && [ "$TOTAL_TASKS" -gt 0 ]; then
    echo "1. Run /doublecheck to verify all claims"
    echo "2. Use /sync_plans to update planning documents"
    echo "3. Consider /close_phase if phase is complete"
else
    echo "1. Review failed tasks in $IMPL_SESSION/"
    echo "2. Address blocking issues"
    echo "3. Re-run implementation for failed tasks"
fi
```

## File Organization Policy

**Implementation logs**: `logs/implement_*` - Execution traces and debugging
**Investigation work**: `investigation/implementation_[task]/` - Complex analysis
**Evidence files**: `evidence/current/Evidence_Implementation_*.md` - Proof of completion
**Test files**: `tests/debug/` or `tests/integration/` - NEVER in root
**Temporary files**: `investigation/implementation_[task]/temp/` - Clean up after completion

## Success Criteria

- [ ] All tasks from CLAUDE.md identified and attempted
- [ ] Each task verified successful before proceeding
- [ ] Implementation evidence created with full results
- [ ] Clear status (SUCCESS/FAILED) for each task
- [ ] Next steps documented based on results
- [ ] Session archived with complete logs

## Usage Notes

- **Systematic**: Processes all tasks in CLAUDE.md sequentially
- **Verification-focused**: Confirms each task before moving to next
- **Evidence-based**: Documents all implementation work with logs
- **Non-stop execution**: Continues until all tasks attempted
- **Clear outcomes**: Provides specific next steps based on results