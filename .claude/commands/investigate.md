Systematic investigation and debugging of specific problem: $ARGUMENTS

## 🚨 IMPORTANT: IGNORE CLAUDE.md

**This is a PARALLEL INVESTIGATION TASK** - You should IGNORE the main CLAUDE.md file completely.

- **Another LLM instance is actively working on CLAUDE.md** - That's the main development instance
- **CLAUDE.md contains main development instructions** - NOT relevant to this investigation
- **You are a secondary instance** - Focus ONLY on this investigation topic
- **Work in isolated workspace** - Don't interfere with main development
- **This is independent work** - Separate from current phase objectives

## Investigation Setup

Create organized workspace for systematic investigation:

```bash
# Parse investigation topic
TOPIC="$ARGUMENTS"
INVESTIGATION_NAME="investigation_$(echo "$TOPIC" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')"
INVESTIGATION_DIR="investigation/$INVESTIGATION_NAME"
INVESTIGATION_SESSION="$INVESTIGATION_DIR/session_$(date +%Y%m%d_%H%M%S)"

# Create workspace structure
mkdir -p "$INVESTIGATION_DIR"/{docs,tools,debug,temp,evidence}
mkdir -p "$INVESTIGATION_SESSION"

# Create README
cat > "$INVESTIGATION_DIR/README.md" << EOF
# Investigation: $TOPIC

**Started**: $(date)
**Purpose**: Systematic investigation of $TOPIC
**Session**: $INVESTIGATION_SESSION

## Investigation Structure
- docs/ - Analysis documentation and findings
- tools/ - Investigation scripts and utilities
- debug/ - Debug output and logs
- temp/ - Temporary files (clean up after investigation)
- evidence/ - Evidence files and proof
- session_*/ - Timestamped investigation sessions

## Current Session
Active session: $INVESTIGATION_SESSION
EOF

# Create task instructions for parallel instance
cat > "$INVESTIGATION_DIR/TASK_INSTRUCTIONS.md" << EOF
# PARALLEL INVESTIGATION TASK: $TOPIC

## 🚨 CRITICAL: IGNORE CLAUDE.md

**DO NOT READ OR FOLLOW /home/brian/projects/autocoder4_cc/CLAUDE.md**

The main CLAUDE.md contains instructions for the primary development instance (another LLM) working on the main phase objectives. You are a secondary instance working on a SEPARATE, PARALLEL investigation task.

## Your Task Focus

**Investigation Topic**: $TOPIC
**Workspace**: $INVESTIGATION_DIR
**Objective**: Investigate and resolve the specific issue described in the topic

## Work Instructions

1. **Focus solely on this investigation** - ignore main development work
2. **Work in this investigation directory** - don't modify main codebase unless necessary
3. **Document findings** in evidence/ and docs/ subdirectories
4. **Create tools and scripts** in tools/ subdirectory as needed
5. **Capture all debug output** in debug/ subdirectory

## Success Criteria

- [ ] Problem reproduced and analyzed
- [ ] Root cause identified
- [ ] Solution developed and tested
- [ ] Evidence documented with full command outputs
- [ ] Findings ready for integration into main development

## Coordination

When investigation is complete, findings can be integrated into main development using /sync_plans command.

**Remember**: This is independent investigation work - stay focused on the investigation topic only.
EOF
```

## Investigation Patterns

Choose approach based on investigation type:

### For Timeout Issues
```bash
cd "$INVESTIGATION_SESSION"

# Test with timeouts and monitoring
timeout 30s [command_that_hangs] 2>&1 | tee timeout_test.log
strace -e trace=network timeout 10s [command] 2>&1 | tee strace.log
ps aux | grep [process] | tee process_monitor.log

# Analyze patterns
grep -E "connect|timeout|hang" *.log > timeout_analysis.txt
```

### For Import Errors
```bash
cd "$INVESTIGATION_SESSION"

# Test imports systematically
python3 -c "import sys; print(sys.path)" > python_path.log
python3 -c "import [module]" 2>&1 | tee import_test.log
find /home/brian/projects/autocoder4_cc -name "*.py" -exec grep -l "import [module]" {} \; > import_usage.log

# Check dependencies
pip list | grep [relevant] > dependencies.log
```

### For LLM Generation Issues  
```bash
cd "$INVESTIGATION_SESSION"

# Test generation pipeline
python3 -c "from autocoder_cc.blueprint_language.system_generator_refactored import SystemGenerator; sg = SystemGenerator(); print('OK')" 2>&1 | tee generator_test.log

# Check prompts and templates
find /home/brian/projects/autocoder4_cc/prompts -name "*.txt" -exec head -5 {} \; > prompt_samples.log

# Test with minimal example
echo "Simple test blueprint" > test.yaml
python3 autocoder_cc/cli/main.py generate -b test.yaml -o test_output 2>&1 | tee minimal_test.log
```

### For Integration Problems
```bash
cd "$INVESTIGATION_SESSION"

# Test component connections
python3 -c "
from autocoder_cc.components.component_registry import component_registry
comp = component_registry.create_component('Store', 'test', {})
print(f'Created: {comp.__class__.__name__}')
" 2>&1 | tee component_test.log

# Check port system
grep -r "InputPort\|OutputPort" /home/brian/projects/autocoder4_cc/autocoder_cc/components/ > port_usage.log
```

## Evidence Documentation

Document all findings systematically:

```bash
cd "$INVESTIGATION_DIR"

# Create evidence file
cat > "evidence/Evidence_${TOPIC}_$(date +%Y%m%d).md" << EOF
# Investigation Evidence: $TOPIC

**Date**: $(date)
**Session**: $INVESTIGATION_SESSION
**Status**: [IN PROGRESS/COMPLETE]

## Problem Statement
[Describe the issue being investigated]

## Reproduction Steps
[Exact commands to reproduce the problem]

## Findings
[Key discoveries and observations]

## Root Cause Analysis
[What is causing the issue]

## Solution
[Proposed fix or workaround]

## Testing Results
[Evidence that solution works]

## Integration Recommendations
[How to integrate findings into main development]
EOF
```

## Completion and Handoff

When investigation is complete:

```bash
# Archive session
ARCHIVE_DIR="$INVESTIGATION_DIR/archive/session_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"
cp -r "$INVESTIGATION_SESSION"/* "$ARCHIVE_DIR/"

# Create handoff summary
cat > "$INVESTIGATION_DIR/HANDOFF_SUMMARY.md" << EOF
# Investigation Complete: $TOPIC

**Completion Date**: $(date)
**Status**: RESOLVED/PARTIALLY_RESOLVED/NEEDS_ESCALATION

## Executive Summary
[2-3 sentence summary of investigation results]

## Key Findings
[Most important discoveries]

## Recommended Actions
[What main development should do with these findings]

## Evidence Files
[List of evidence files with key findings]

**Integration Path**: Use /sync_plans to integrate findings into main roadmap
EOF
```

## Usage Notes

- **Parallel Work**: Independent of main development instance
- **Workspace Isolation**: All work stays in investigation directory
- **Evidence-Based**: Document everything with command outputs
- **Integration Ready**: Findings can be integrated via /sync_plans
- **Topic-Specific**: Patterns adapt to investigation type (timeout, import, LLM, integration)

## Success Criteria

- [ ] Investigation workspace created and organized
- [ ] Problem systematically analyzed with evidence
- [ ] Root cause identified or escalation path documented
- [ ] Findings documented with integration recommendations
- [ ] Handoff summary created for main development team