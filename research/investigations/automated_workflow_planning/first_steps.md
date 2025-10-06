# First Steps: What to Build Today

## Reality Check

Before building ANY workflow tools, we MUST:
1. Understand what Claude Code actually sends to hooks
2. Verify our command injection approach works
3. Ensure we can parse state reliably

Without these, everything else is speculation.

## Day 1: Hook Investigation (TODAY)

### Step 1: Create Hook Test Infrastructure
```bash
# Create test directory
mkdir -p tools/test
mkdir -p investigations/automated_workflow_planning/hook_inputs

# Create universal hook logger
cat > tools/test/universal_logger.py << 'EOF'
#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Read input from stdin
try:
    input_data = json.load(sys.stdin)
except:
    input_data = {"error": "Could not parse input"}

# Create unique filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
hook_event = input_data.get("hook_event_name", "unknown")
output_dir = Path("investigations/automated_workflow_planning/hook_inputs")
output_dir.mkdir(parents=True, exist_ok=True)

# Save input
output_file = output_dir / f"{timestamp}_{hook_event}.json"
with open(output_file, 'w') as f:
    json.dump({
        "timestamp": timestamp,
        "hook_event": hook_event,
        "input": input_data,
        "environment": {
            "cwd": os.getcwd(),
            "claude_project_dir": os.environ.get("CLAUDE_PROJECT_DIR", "not set")
        }
    }, f, indent=2)

# Log to stderr (visible in transcript)
print(f"Logged {hook_event} to {output_file}", file=sys.stderr)

# Return success
output = {"continue": True, "suppressOutput": True}
print(json.dumps(output))
EOF

chmod +x tools/test/universal_logger.py
```

### Step 2: Configure Test Hooks
```bash
# Create test configuration
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/test/universal_logger.py",
        "timeout": 5
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/test/universal_logger.py",
        "timeout": 5
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/test/universal_logger.py",
        "timeout": 5
      }]
    }],
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/test/universal_logger.py",
        "timeout": 5
      }]
    }]
  }
}
EOF
```

### Step 3: Trigger Each Hook Type
```bash
# Actions to trigger hooks:
# 1. Start new session → SessionStart
# 2. Run any command → PreToolUse, PostToolUse
# 3. Complete response → Stop
# 4. Edit a file → Pre/Post for Edit tool
# 5. Run bash → Pre/Post for Bash tool

# After triggering, analyze:
ls -la investigations/automated_workflow_planning/hook_inputs/
```

### Step 4: Analyze and Document
Create analysis script:
```python
# tools/test/analyze_hooks.py
import json
from pathlib import Path

hook_dir = Path("investigations/automated_workflow_planning/hook_inputs")
hook_types = {}

for file in hook_dir.glob("*.json"):
    with open(file) as f:
        data = json.load(f)
        hook_type = data.get("hook_event", "unknown")
        if hook_type not in hook_types:
            hook_types[hook_type] = []
        hook_types[hook_type].append(data)

# Generate report
for hook_type, samples in hook_types.items():
    print(f"\n{hook_type}: {len(samples)} samples")
    if samples:
        # Show structure of first sample
        print(json.dumps(samples[0], indent=2)[:500])
```

## Day 2: Command Injection Testing

### Test Stop Hook Command Injection
```python
# tools/test/test_stop_injection.py
#!/usr/bin/env python3
import json
import sys

# Read input
input_data = json.load(sys.stdin)

# Test different injection formats
test_formats = [
    {"decision": "block", "reason": "/explore"},
    {"decision": "block", "reason": "Execute: /write_tests"},
    {"decision": "block", "reason": "Please run: /implement"},
    {
        "decision": "block",
        "reason": "Found issues. Execute: /investigate_uncertainties"
    }
]

# Rotate through formats to test each
import random
output = random.choice(test_formats)

# Log what we're trying
with open("/tmp/injection_test.log", "a") as f:
    f.write(f"Testing: {json.dumps(output)}\n")

print(json.dumps(output))
```

## Day 3: State Management Testing

### Test State Extraction
```python
# tools/test/test_state_extraction.py
import re
import json

def extract_workflow_state(content):
    """Extract workflow state from CLAUDE.md content"""
    
    # Method 1: Look for JSON block with workflow_state
    pattern = r'```json\s*\n(.*?"workflow_state".*?)\n```'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        try:
            data = json.loads(match.group(1))
            return data.get("workflow_state", {})
        except:
            pass
    
    # Method 2: Look for workflow state header
    pattern = r'## WORKFLOW STATE\s*\n```json\s*\n(.*?)\n```'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    
    # Method 3: Last resort - find any JSON with current_command
    pattern = r'\{[^{}]*"current_command"[^{}]*\}'
    matches = re.findall(pattern, content)
    
    for match in matches:
        try:
            data = json.loads(match)
            if "current_command" in data:
                return data
        except:
            pass
    
    return None

# Test with current CLAUDE.md
with open("CLAUDE.md") as f:
    content = f.read()
    state = extract_workflow_state(content)
    print(f"Extracted state: {json.dumps(state, indent=2)}")
```

## Day 4: Build Minimal workflow_orchestrator.py

Only AFTER we understand hooks, build minimal version:

```python
# tools/workflow/workflow_orchestrator.py
#!/usr/bin/env python3
import json
import sys
import os
import time
from pathlib import Path

def main():
    # Read input
    input_data = json.load(sys.stdin)
    
    # Check recursion protection
    if input_data.get("stop_hook_active"):
        return {"continue": True, "suppressOutput": True}
    
    # Check lock
    lock_file = Path(".claude/.lock/stop.lock")
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    if lock_file.exists():
        age = time.time() - lock_file.stat().st_mtime
        if age < 5:
            return {"continue": True, "suppressOutput": True}
    
    # Create lock
    lock_file.write_text(str(time.time()))
    
    # Read CLAUDE.md state
    try:
        with open("CLAUDE.md") as f:
            content = f.read()
            # Extract state (using tested method)
            state = extract_workflow_state(content)
    except:
        state = None
    
    # Determine next command
    if not state or not state.get("current_command"):
        next_command = "/load_phase_plans"
    else:
        # Simple progression for now
        progression = {
            "/explore": "/write_tests",
            "/write_tests": "/implement",
            "/implement": "/run_tests",
            "/run_tests": "/doublecheck",
            "/doublecheck": "/explore"  # Loop for now
        }
        current = state.get("current_command")
        next_command = progression.get(current, "/explore")
    
    # Return command injection
    return {
        "decision": "block",
        "reason": f"Execute: {next_command}"
    }

if __name__ == "__main__":
    output = main()
    print(json.dumps(output))
```

## Day 5: Fix Broken References

Before anything else works:
```bash
# See what's broken
python3 tools/validate_references.py > reference_report.txt

# Common fixes:
# 1. Remove references to non-existent files
# 2. Update moved file references  
# 3. Create missing placeholder files
# 4. Update documentation links
```

## Success Criteria for First Steps

### Day 1 Success:
- [ ] Have real JSON samples from each hook type
- [ ] Understand exact field structure
- [ ] Know what CLAUDE_PROJECT_DIR contains
- [ ] Document any missing expected fields

### Day 2 Success:
- [ ] Know which injection format works
- [ ] Understand character limits
- [ ] Have working command injection pattern
- [ ] Document Claude's response to each format

### Day 3 Success:
- [ ] Can extract state from CLAUDE.md reliably
- [ ] Handle corrupted/missing state gracefully
- [ ] State update mechanism tested
- [ ] Token cost measured

### Day 4 Success:
- [ ] Minimal workflow_orchestrator.py works
- [ ] Can progress through basic command sequence
- [ ] Recursion protection verified
- [ ] Lock mechanism tested

### Day 5 Success:
- [ ] All broken references fixed
- [ ] validate_references.py passes
- [ ] Clean baseline established

## What NOT to Do Yet

DO NOT:
- Build complex discovery classification
- Implement quality gates
- Create elaborate error handling
- Design multi-language support
- Build fancy UI/visualizations

Focus on understanding what we're working with first.

## Risk Mitigations

If hooks don't work as expected:
1. **Fallback**: File-based command queue
2. **Alternative**: Manual workflow guidance in CLAUDE.md
3. **Workaround**: External Python script monitoring

If command injection fails:
1. **Fallback**: Write next command to file
2. **Alternative**: Use UserPromptSubmit to inject
3. **Workaround**: Manual command execution

If state parsing unreliable:
1. **Fallback**: Separate state.json file
2. **Alternative**: Simple key-value format
3. **Workaround**: State reconstruction from evidence

## Daily Validation

End of each day, answer:
1. What did we learn that changes our approach?
2. What assumptions were wrong?
3. What new uncertainties emerged?
4. Are we still on viable path?

## Note on Implementation Order

This order is CRITICAL:
1. Understand what we have (hooks, formats)
2. Test core mechanisms (injection, state)
3. Build minimal version
4. Fix existing issues
5. THEN enhance

Skipping steps 1-2 means building on assumptions that might be wrong.