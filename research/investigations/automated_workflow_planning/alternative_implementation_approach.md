# Alternative Implementation Approach
## Building Workflow Automation Without Hooks

### Current Situation
- Hooks are not triggering despite correct configuration
- This blocks the entire automated workflow design
- Need alternative approach to maintain project momentum

### Proposed Solution: Hybrid Manual-Automated System

## Phase 1: Build Core Tools Standalone (Week 1)

### 1. workflow_orchestrator.py (Standalone Version)
```python
#!/usr/bin/env python3
"""
Standalone workflow orchestrator that can be run manually.
Usage: python3 tools/workflow/workflow_orchestrator.py
"""

import json
from pathlib import Path
import re
from datetime import datetime

class WorkflowOrchestrator:
    def __init__(self):
        self.claude_md = Path("CLAUDE.md")
        self.state_file = Path(".claude/workflow_state.json")
        
    def extract_state(self):
        """Extract workflow state from CLAUDE.md"""
        if not self.claude_md.exists():
            return None
            
        content = self.claude_md.read_text()
        
        # Look for JSON block with workflow_state
        pattern = r'```json\s*\n(.*?"workflow_state".*?)\n```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get("workflow_state", {})
            except:
                pass
                
        # Fallback: check separate state file
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
                
        return {"current_command": None, "iteration": 0}
    
    def determine_next_command(self, state):
        """Determine next command based on current state"""
        current = state.get("current_command")
        iteration = state.get("iteration", 0)
        
        # Check for loop condition
        if iteration >= 7:
            return "/investigate_uncertainties"
        
        # Standard progression
        progression = {
            None: "/explore",
            "/explore": "/write_tests",
            "/write_tests": "/implement",
            "/implement": "/run_tests",
            "/run_tests": "/doublecheck",
            "/doublecheck": "/commit",
            "/commit": "/explore",  # Start new cycle
            "/investigate_uncertainties": "/resolve_blockers"
        }
        
        return progression.get(current, "/explore")
    
    def check_evidence(self):
        """Check if required evidence exists"""
        evidence_dir = Path("investigations/current_work/evidence.json")
        if evidence_dir.exists():
            try:
                evidence = json.loads(evidence_dir.read_text())
                return evidence.get("tests_passed", False)
            except:
                pass
        return False
    
    def run(self):
        """Main orchestration logic"""
        state = self.extract_state()
        
        print(f"Current State: {json.dumps(state, indent=2)}")
        
        # Check evidence requirements
        if state.get("current_command") == "/implement":
            if not self.check_evidence():
                print("⚠️  Missing required evidence for phase completion")
                next_command = "/run_tests"
            else:
                next_command = self.determine_next_command(state)
        else:
            next_command = self.determine_next_command(state)
        
        # Update state
        new_state = {
            "current_command": next_command,
            "iteration": state.get("iteration", 0) + 1,
            "timestamp": datetime.now().isoformat(),
            "previous_command": state.get("current_command")
        }
        
        # Save state to file (backup approach)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(new_state, indent=2))
        
        # Output recommendation
        print(f"\n📋 RECOMMENDED NEXT COMMAND: {next_command}")
        print(f"Iteration: {new_state['iteration']}/7")
        
        # Write to command file for easy execution
        command_file = Path(".claude/next_command.txt")
        command_file.parent.mkdir(parents=True, exist_ok=True)
        command_file.write_text(next_command)
        
        print(f"\n✅ Next command written to: .claude/next_command.txt")
        print("Execute in Claude Code with the command shown above")
        
        return next_command

if __name__ == "__main__":
    orchestrator = WorkflowOrchestrator()
    orchestrator.run()
```

### 2. evidence_validator.py (Standalone Version)
```python
#!/usr/bin/env python3
"""
Validate evidence for phase transitions.
Usage: python3 tools/workflow/evidence_validator.py [phase]
"""

import json
import sys
from pathlib import Path

class EvidenceValidator:
    def __init__(self):
        self.evidence_schema = {
            "explore": ["discovery_count", "areas_investigated"],
            "write_tests": ["test_files", "coverage_percentage"],
            "implement": ["files_modified", "tests_passed"],
            "run_tests": ["test_results", "failure_analysis"],
            "doublecheck": ["validation_checks", "edge_cases_tested"]
        }
    
    def validate(self, phase=None):
        """Validate evidence for given phase"""
        evidence_file = Path("investigations/current_work/evidence.json")
        
        if not evidence_file.exists():
            print(f"❌ No evidence file found at {evidence_file}")
            return False
        
        try:
            evidence = json.loads(evidence_file.read_text())
        except Exception as e:
            print(f"❌ Failed to parse evidence file: {e}")
            return False
        
        # Determine phase
        if not phase:
            state_file = Path(".claude/workflow_state.json")
            if state_file.exists():
                state = json.loads(state_file.read_text())
                phase = state.get("current_command", "").replace("/", "")
        
        if phase not in self.evidence_schema:
            print(f"⚠️  Unknown phase: {phase}")
            return True  # Don't block on unknown phases
        
        # Check required fields
        required_fields = self.evidence_schema[phase]
        missing = []
        
        for field in required_fields:
            if field not in evidence:
                missing.append(field)
        
        if missing:
            print(f"❌ Missing required evidence fields: {missing}")
            return False
        
        print(f"✅ Evidence valid for phase: {phase}")
        return True
    
    def generate_template(self, phase):
        """Generate evidence template for phase"""
        if phase not in self.evidence_schema:
            return {}
        
        template = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        for field in self.evidence_schema[phase]:
            template[field] = None
        
        return template

if __name__ == "__main__":
    validator = EvidenceValidator()
    phase = sys.argv[1] if len(sys.argv) > 1 else None
    validator.validate(phase)
```

### 3. Manual Execution Workflow

Until hooks work, use this workflow:

```bash
# Step 1: Run orchestrator to get next command
python3 tools/workflow/workflow_orchestrator.py

# Step 2: Execute the recommended command in Claude Code
# (Command will be in .claude/next_command.txt)

# Step 3: After command completion, validate evidence
python3 tools/workflow/evidence_validator.py

# Step 4: Repeat
```

## Phase 2: Create Helper Scripts (Week 1-2)

### Watch Script (Run Outside Claude Code)
```bash
#!/bin/bash
# tools/workflow/watch.sh
# Monitors for changes and suggests next actions

while true; do
    # Check if CLAUDE.md changed
    if [ "CLAUDE.md" -nt ".claude/last_check" ]; then
        echo "Change detected, running orchestrator..."
        python3 tools/workflow/workflow_orchestrator.py
        touch .claude/last_check
    fi
    sleep 5
done
```

### Quick Command Script
```bash
#!/bin/bash
# tools/workflow/next.sh
# Quick way to get next command

python3 tools/workflow/workflow_orchestrator.py | grep "RECOMMENDED" | cut -d: -f2
```

## Phase 3: Gradual Hook Integration (When Working)

When hooks start working:
1. Keep standalone tools as-is
2. Add thin wrapper for hook integration
3. Tools remain testable independently

```python
# tools/workflow/hook_wrapper.py
#!/usr/bin/env python3
"""Thin wrapper for hook integration"""

import json
import sys
from workflow_orchestrator import WorkflowOrchestrator

# Read hook input
input_data = json.load(sys.stdin)

# Run orchestrator
orchestrator = WorkflowOrchestrator()
next_command = orchestrator.run()

# Return hook response
output = {
    "decision": "block",
    "reason": f"Execute: {next_command}"
}
print(json.dumps(output))
```

## Advantages of This Approach

1. **Not Blocked**: Can proceed immediately without hooks
2. **Testable**: Tools can be tested independently
3. **Incremental**: Can add automation gradually
4. **Visible**: Clear what's happening at each step
5. **Debuggable**: Easy to troubleshoot issues
6. **Portable**: Works in any environment

## Implementation Order

### Today (Day 1):
1. ✅ Document hook investigation findings
2. ⬜ Build standalone workflow_orchestrator.py
3. ⬜ Build standalone evidence_validator.py
4. ⬜ Test manual workflow

### Tomorrow (Day 2):
1. ⬜ Build discovery_classifier.py
2. ⬜ Build uncertainty_resolver.py
3. ⬜ Create helper scripts

### Day 3-5:
1. ⬜ Fix 120 broken references
2. ⬜ Create comprehensive test suite
3. ⬜ Test full workflow manually
4. ⬜ Document usage patterns

## Success Criteria

Even without hooks, we achieve:
- ✅ Systematic workflow progression
- ✅ Evidence-based phase transitions
- ✅ Loop detection and breaking
- ✅ State persistence across sessions
- ✅ Clear command recommendations

The only thing we lose is full automation - user must manually execute recommended commands.

## Migration Path

When hooks work:
1. No tool changes needed
2. Add hook wrappers
3. Update .claude/settings.json
4. Full automation achieved

This approach ensures we can make progress regardless of hook availability.