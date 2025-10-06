# Critical Uncertainties Requiring Resolution

## Immediate Blockers (Must Resolve Before Any Implementation)

### 1. Hook JSON I/O Verification
**Status**: UNRESOLVED
**Blocking**: ALL workflow tools

**What We Don't Know**:
- Exact JSON structure Claude Code sends to hooks
- Whether stop_hook_active field actually exists
- Format of tool_input for different tools
- Maximum size limits on JSON responses

**Investigation Plan**:
```bash
# Step 1: Create minimal test hook
mkdir -p tools/test
cat > tools/test/log_hook.py << 'EOF'
#!/usr/bin/env python3
import json, sys, datetime

# Log input
input_data = json.load(sys.stdin)
timestamp = datetime.datetime.now().isoformat()

# Save to investigation directory
with open(f'investigations/automated_workflow_planning/hook_inputs/{timestamp}.json', 'w') as f:
    json.dump({
        'timestamp': timestamp,
        'hook_input': input_data,
        'stdin_size': len(sys.stdin.read()) if hasattr(sys.stdin, 'read') else 'unknown'
    }, f, indent=2)

# Return success
print(json.dumps({"continue": True, "suppressOutput": True}))
EOF

chmod +x tools/test/log_hook.py

# Step 2: Configure in .claude/settings.json
# Step 3: Trigger each hook type
# Step 4: Analyze collected JSONs
```

**Success Criteria**:
- Have actual JSON samples from all hook types
- Understand field structure and limits
- Verify assumed fields exist

### 2. CLAUDE.md State Parsing Reliability
**Status**: UNRESOLVED  
**Blocking**: workflow_orchestrator.py

**What We Don't Know**:
- How to reliably extract JSON from CLAUDE.md
- Whether Claude preserves JSON formatting
- How to handle corrupted state blocks
- Token cost of state in context

**Investigation Plan**:
```python
# Test state extraction patterns
import re
import json

def extract_workflow_state(claude_md_content):
    """Extract workflow_state JSON from CLAUDE.md"""
    patterns = [
        r'```json\n\{[\s\S]*?"workflow_state"[\s\S]*?\}\n```',
        r'"workflow_state":\s*\{[^}]*\}',
        r'## WORKFLOW STATE\n```json\n([\s\S]*?)\n```'
    ]
    # Test each pattern
    # Handle malformed JSON
    # Implement fallback strategies
```

**Success Criteria**:
- Reliable extraction function with 100% success rate
- Graceful handling of malformed state
- Default state for missing blocks

### 3. Command Injection Limits
**Status**: UNRESOLVED
**Blocking**: workflow_orchestrator.py

**What We Don't Know**:
- Character limit on Stop hook "reason" field
- How Claude interprets the injected command
- Whether multi-line commands work
- How to handle command parameters

**Investigation Plan**:
```python
# Test command formats
test_cases = [
    {"decision": "block", "reason": "/explore"},
    {"decision": "block", "reason": "Execute: /explore"},
    {"decision": "block", "reason": "/explore --verbose"},
    {"decision": "block", "reason": "/explore\nWith context"},
    {"decision": "block", "reason": "X" * 1000},  # Length test
]
# Test each format and observe Claude's response
```

**Success Criteria**:
- Know exact format that works
- Understand length limits
- Have fallback for complex commands

## Strategic Uncertainties (Need User Decision)

### 4. Failure Recovery Philosophy
**Status**: NEEDS USER INPUT
**Blocking**: Error handling design

**Options**:
1. **Aggressive Recovery**: Try to continue no matter what
   - Pro: Maximum automation
   - Con: May hide critical issues
   
2. **Conservative Recovery**: Stop on any uncertainty
   - Pro: Safe, no hidden failures
   - Con: Requires more manual intervention
   
3. **Graduated Recovery**: Different strategies by error type
   - Pro: Balanced approach
   - Con: Complex to implement

**Recommendation**: Start with Conservative, evolve to Graduated

### 5. Evidence Completeness Standards
**Status**: NEEDS USER INPUT
**Blocking**: evidence_validator.py

**Questions**:
- Is 80% test coverage sufficient?
- Must ALL tests pass or acceptable failure rate?
- Are integration tests required?
- Manual review checkpoints?

**Recommendation**: 
- 80% coverage minimum
- 100% test pass for phase completion
- Integration tests for phase boundaries
- No manual review for MVP

### 6. Multi-Session Coordination
**Status**: NEEDS USER INPUT
**Blocking**: State management

**Questions**:
- Support multiple concurrent sessions?
- How to handle conflicting state updates?
- Session ownership model?

**Recommendation**: 
- Single session only for MVP
- File lock prevents concurrent access
- Multi-session in post-MVP

## Technical Uncertainties (Resolve Through Testing)

### 7. Discovery Impact Classification
**Status**: NEEDS TESTING
**Blocking**: discovery_classifier.py

**Approach**:
```python
# Scoring system for discoveries
impact_score = {
    'breaks_tests': 10,
    'changes_architecture': 8,
    'adds_dependency': 5,
    'performance_impact': 3,
    'documentation_only': 1
}

# Thresholds
MAJOR_THRESHOLD = 8
MINOR_THRESHOLD = 3
```

**Test with real discoveries to calibrate**

### 8. Loop Detection Beyond Counter
**Status**: NEEDS TESTING
**Blocking**: uncertainty_resolver.py

**Patterns to Detect**:
- Same error message repeating
- Alternating between two states
- No new files created in N iterations
- Test results unchanged

**Implementation approach**: Start simple, add patterns as needed

### 9. Context Window Limits
**Status**: NEEDS TESTING
**Blocking**: Workflow sustainability

**Measurements Needed**:
- Current CLAUDE.md token count
- Growth rate per operation
- Compaction effectiveness
- Minimum viable context

**Test Approach**:
```python
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4")

def measure_context():
    claude_md = open("CLAUDE.md").read()
    tokens = len(encoding.encode(claude_md))
    return tokens

# Track over time
# Identify growth patterns
# Design compaction strategy
```

## Resolution Priority

### Must Resolve First (Blockers):
1. **Hook JSON I/O format** - Nothing works without this
2. **Command injection mechanism** - Core to automation
3. **CLAUDE.md state parsing** - Required for state management

### Need User Decision:
4. **Recovery philosophy** - Affects all error handling
5. **Evidence standards** - Defines "done"
6. **Session coordination** - Architectural impact

### Can Resolve During Implementation:
7. **Discovery classification** - Refine through usage
8. **Loop detection patterns** - Enhance over time
9. **Context limits** - Monitor and adjust

## Investigation Timeline

### Day 1-2: Hook Testing
- Set up test hooks
- Collect JSON samples
- Document findings

### Day 3-4: State Management Testing  
- Test CLAUDE.md parsing
- Implement state extraction
- Test corruption recovery

### Day 5: Command Injection Testing
- Test injection formats
- Find limits and constraints
- Develop reliable pattern

### Day 6-7: User Decision Points
- Document options clearly
- Get user input on strategic decisions
- Update design based on decisions

## Risk Assessment

### High Risk (Could block entire project):
- Hook JSON format different than expected
- Command injection doesn't work as designed
- Context window too small for state

### Medium Risk (Requires redesign):
- State parsing unreliable
- Session recovery fails
- Discovery classification too noisy

### Low Risk (Can work around):
- Quality gates language-specific
- Loop detection imperfect
- Evidence validation too strict/loose

## Next Actions

1. **Create tools/test directory** for investigations
2. **Build hook test framework** 
3. **Document actual JSON formats**
4. **Test command injection patterns**
5. **Get user decisions on strategic points**
6. **Update implementation plan** based on findings

## Success Metrics

- All blockers resolved with working solutions
- User decisions documented
- Technical approaches validated
- No high-risk unknowns remaining
- Clear implementation path forward