# Workflow Automation Tools

## Overview

Complete workflow management system for Claude Code projects. Currently operates in **manual mode** due to hooks not triggering. When hooks become available, these tools can be wrapped for full automation.

## Tools

### 1. workflow_orchestrator.py
**Purpose**: Manages workflow progression and state
```bash
python3 tools/workflow/workflow_orchestrator.py
```
- Determines next command based on current state
- Detects active errors and prioritizes resolution
- Tracks iteration count to prevent infinite loops
- Saves state to `.claude/workflow_state.json`

### 2. evidence_validator.py
**Purpose**: Validates evidence for phase transitions
```bash
python3 tools/workflow/evidence_validator.py [phase]
python3 tools/workflow/evidence_validator.py --create [phase]
```
- Checks required fields for each phase
- Creates evidence templates
- Ensures phase transitions are evidence-based

### 3. discovery_classifier.py
**Purpose**: Analyzes discoveries and their impact
```bash
python3 tools/workflow/discovery_classifier.py
python3 tools/workflow/discovery_classifier.py [file]
python3 tools/workflow/discovery_classifier.py --report
```
- Scans investigations/ for new discoveries
- Scores impact (critical/major/minor/informational)
- Recommends workflow adjustments

### 4. uncertainty_resolver.py
**Purpose**: Detects and resolves workflow issues
```bash
python3 tools/workflow/uncertainty_resolver.py
python3 tools/workflow/uncertainty_resolver.py --record
```
- Detects 5 types of loops
- Identifies blocking uncertainties
- Suggests resolution strategies
- Tracks resolution history

### 5. session_recovery.py
**Purpose**: Recovers from interrupted sessions
```bash
python3 tools/workflow/session_recovery.py
python3 tools/workflow/session_recovery.py --json
```
- Detects incomplete work
- Analyzes session state
- Recommends recovery actions
- Preserves context across sessions

## Manual Workflow

### Standard Progression
```bash
# 1. Check session state
python3 tools/workflow/session_recovery.py

# 2. Get next command
python3 tools/workflow/workflow_orchestrator.py

# 3. Execute recommended command in Claude Code
# (Command saved in .claude/next_command.txt)

# 4. Validate evidence if needed
python3 tools/workflow/evidence_validator.py

# 5. Check for issues
python3 tools/workflow/uncertainty_resolver.py

# 6. Repeat
```

### Quick Commands
```bash
# Get next command only
python3 tools/workflow/workflow_orchestrator.py --quiet

# Check all systems
python3 tools/workflow/uncertainty_resolver.py && \
python3 tools/workflow/discovery_classifier.py && \
python3 tools/workflow/evidence_validator.py
```

## State Files

All tools share common state files in `.claude/`:

- `workflow_state.json` - Current workflow state
- `workflow_history.json` - Command history
- `next_command.txt` - Recommended next command
- `recovery_context.json` - Session recovery data
- `uncertainty_resolution.txt` - Resolution recommendation
- `discovery_classifications.json` - Discovery analysis
- `evidence.json` - Phase evidence

## Workflow Commands

The system recognizes these workflow commands:

- `/explore` - Explore codebase and requirements
- `/write_tests` - Write tests for implementation
- `/implement` - Implement the solution
- `/run_tests` - Run tests and validate
- `/doublecheck` - Validate edge cases
- `/commit` - Commit completed work
- `/investigate_uncertainties` - Investigate issues
- `/resolve_blockers` - Fix blocking problems

## Loop Detection

The uncertainty resolver detects:

1. **Command loops** - Same command repeating
2. **Alternating loops** - Two commands alternating
3. **Error loops** - Same error repeating
4. **No progress** - No files created
5. **Iteration limit** - Max 7 iterations

## Evidence Requirements

Each phase requires specific evidence:

### explore
- Required: areas_investigated, key_findings
- Optional: discovery_count, uncertainties_identified

### write_tests
- Required: test_files_created, test_count
- Optional: coverage_target, test_framework

### implement
- Required: files_modified, implementation_complete
- Optional: lines_added, dependencies_added

### run_tests
- Required: test_results, tests_passed
- Optional: coverage_percentage, failure_analysis

### doublecheck
- Required: validation_complete, edge_cases_tested
- Optional: performance_checked, security_reviewed

### commit
- Required: commit_message, files_committed
- Optional: commit_hash, branch_name

## Future: Hook Integration

When Claude Code hooks work, create wrapper:

```python
#!/usr/bin/env python3
# tools/workflow/stop_hook.py
import json
import sys
from workflow_orchestrator import WorkflowOrchestrator

input_data = json.load(sys.stdin)
orchestrator = WorkflowOrchestrator()
next_command = orchestrator.run(quiet=True)

output = {
    "decision": "block",
    "reason": f"Execute: {next_command}"
}
print(json.dumps(output))
```

Then update `.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/workflow/stop_hook.py"
      }]
    }]
  }
}
```

## Troubleshooting

### Tools not finding files
- Check working directory is project root
- Verify `.claude/` directory exists

### Workflow stuck
- Run `uncertainty_resolver.py` to detect loops
- Check `.claude/workflow_history.json` for patterns
- Reset with: `rm .claude/workflow_state.json`

### Evidence validation failing
- Create template: `evidence_validator.py --create [phase]`
- Check required fields for phase
- Ensure evidence file in correct location

## Development Status

✅ Complete:
- All 5 core tools implemented
- Manual workflow operational
- State persistence working
- Loop detection active

⚠️ Known Issues:
- Claude Code hooks not triggering
- 123 broken cross-references in codebase
- Active errors in CLAUDE.md need resolution

🔄 Next Steps:
- Fix broken references
- Resolve active errors
- Test hook integration when available
- Build actual Goodwill scraping implementation