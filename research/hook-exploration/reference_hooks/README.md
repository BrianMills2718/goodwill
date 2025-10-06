# Claude Code Hook Reference Examples

## Working TDD Workflow Hook

This directory contains working examples extracted from the legacy `.claude` configurations before archival.

### Files:
- `tdd_workflow.py` - Complete autonomous TDD workflow hook that implements the forever_mode pattern
- `working_hook_settings.json` - Settings configuration that worked with the TDD workflow

### Key Implementation Details:

**Hook Structure:**
- Uses Stop hook to prevent Claude from stopping
- Returns JSON with `{"decision": "block", "reason": "instruction"}`
- Implements state management with workflow_state.txt
- Cycles through: load_phase → explore → write_tests → implement → run_tests → doublecheck → commit

**Settings Configuration:**
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command", 
        "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/tdd_workflow.py"
      }]
    }]
  }
}
```

**State Management:**
- Reads/writes to `.claude/workflow_state.txt`
- Uses project root from `$CLAUDE_PROJECT_DIR` environment variable
- Simple state machine with predefined transitions

This hook successfully implemented autonomous TDD cycles but needed the loop prevention mechanisms documented in the v4 architecture to prevent infinite loops.