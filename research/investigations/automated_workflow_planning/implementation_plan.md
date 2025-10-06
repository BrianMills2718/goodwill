# Comprehensive Implementation Plan for Autonomous Workflow System

## Current State Assessment

### What Exists (Working)
1. **validate_references.py** - Cross-reference validation
2. **load_context.py** - Context loading for file modifications
3. **inject_error.py** - Error injection into CLAUDE.md
4. **Comprehensive design documentation** - Architecture and workflow specifications

### What's Missing (Must Build)
1. **5 Core workflow tools** - None exist yet
2. **Hook configuration** - No .claude/settings.json
3. **Evidence validation system** - Schema defined but not implemented
4. **120 broken references** - Need fixing
5. **Test infrastructure** - No tests for workflow system

## Critical Uncertainties to Resolve

### Category 1: Strategic Uncertainties (Need User Clarification)

#### 1.1 Workflow State Storage
**Uncertainty**: Should workflow state live in CLAUDE.md or separate file?
- **Option A**: Keep in CLAUDE.md as designed (single source of truth)
- **Option B**: Separate state/workflow_state.json (cleaner, avoids merge conflicts)
- **Impact**: Affects all tool implementations
- **Recommendation**: Start with CLAUDE.md, refactor if needed

#### 1.2 Error Recovery Strategy
**Uncertainty**: How aggressive should automatic recovery be?
- **Option A**: Always try to continue (may hide issues)
- **Option B**: Fail fast on any uncertainty (may be too conservative)
- **Option C**: Configurable thresholds (complex but flexible)
- **Impact**: Affects workflow_orchestrator.py design
- **Recommendation**: Option C with conservative defaults

#### 1.3 Evidence Requirements
**Uncertainty**: What constitutes "sufficient" evidence for phase completion?
- Must all tests pass? (100% or threshold?)
- Required coverage percentage? (80% as suggested?)
- Manual review requirements?
- **Impact**: Affects evidence_validator.py strictness
- **Recommendation**: Configurable per phase with defaults

### Category 2: Technical Uncertainties (Investigate Before Implementing)

#### 2.1 Hook JSON I/O Format
**Uncertainty**: Exact format of hook input/output JSON
- What fields does Claude Code actually provide?
- How to parse workflow state from CLAUDE.md reliably?
- **Investigation Needed**: Create test hook to log actual JSON structure
- **Risk**: Tools may fail if format assumptions wrong

#### 2.2 Command Injection Mechanism
**Uncertainty**: How to reliably inject commands via Stop hook
- Does `"decision": "block"` with `"reason"` always work?
- Character limits on reason field?
- How to handle multi-line commands?
- **Investigation Needed**: Test various command formats
- **Risk**: Workflow may stall if injection fails

#### 2.3 Context Window Management
**Uncertainty**: How to handle CLAUDE.md growth
- When to compact?
- What to preserve vs archive?
- How to maintain continuity after compaction?
- **Investigation Needed**: Measure token usage patterns
- **Risk**: Context overflow could break workflow

#### 2.4 Cross-Session State Persistence
**Uncertainty**: How to ensure state survives session restarts
- File locking across processes?
- Atomic writes for concurrent access?
- State corruption recovery?
- **Investigation Needed**: Test session recovery scenarios
- **Risk**: State loss could require manual intervention

### Category 3: Implementation Uncertainties (Resolve Through Building)

#### 3.1 Discovery Classification Thresholds
**Uncertainty**: What makes a discovery "major" vs "minor"?
- Keyword-based classification?
- Impact on existing code?
- Test failure correlation?
- **Approach**: Start simple, refine based on usage

#### 3.2 Loop Detection Patterns
**Uncertainty**: How to detect workflow is stuck beyond iteration count?
- Same error repeating?
- No progress metrics?
- Oscillating between states?
- **Approach**: Implement basic counter, add patterns later

#### 3.3 Quality Gate Integration
**Uncertainty**: How to run language-specific quality checks?
- Python: pytest, flake8, black
- JavaScript: jest, eslint, prettier
- Language detection method?
- **Approach**: Start with Python only, generalize later

## Implementation Phases

### Phase 0: Foundation (Week 1)
**Goal**: Establish testing and validation infrastructure

1. **Create test harness for hooks**
   - Build mock hook environment
   - Capture actual JSON formats
   - Test command injection patterns

2. **Fix critical broken references** (120 currently)
   - Run validate_references.py
   - Fix or remove broken links
   - Establish clean baseline

3. **Set up evidence structure**
   - Create investigations/test_area/phase_1/
   - Implement evidence.json creation
   - Test archival process

**Uncertainties to Resolve**:
- Hook JSON formats (2.1)
- Command injection mechanism (2.2)

### Phase 1: Core Tools (Week 2-3)
**Goal**: Build minimal working workflow

1. **workflow_orchestrator.py**
   - Parse CLAUDE.md state
   - Determine next command logic
   - Implement Stop hook integration
   - Add recursion protection
   - Basic lock mechanism

2. **evidence_validator.py**
   - Parse evidence.json
   - Validate against schema
   - Check test results
   - PostToolUse integration

3. **session_recovery.py**
   - Read workflow state on SessionStart
   - Detect incomplete work
   - Inject recovery context

**Uncertainties to Resolve**:
- Workflow state storage (1.1)
- Cross-session persistence (2.4)

### Phase 2: Discovery System (Week 3-4)
**Goal**: Implement discovery detection and classification

1. **discovery_classifier.py**
   - Monitor investigations/ writes
   - Classify impact levels
   - Trigger plan updates
   - PostToolUse integration

2. **uncertainty_resolver.py**
   - Parse uncertainty categories
   - Route to appropriate handlers
   - Track resolution attempts
   - Implement loop breaking

**Uncertainties to Resolve**:
- Discovery classification thresholds (3.1)
- Loop detection patterns (3.2)

### Phase 3: Hook Configuration (Week 4)
**Goal**: Wire everything together

1. **Create .claude/settings.json**
   - All hooks with proper JSON structure
   - Correct timeouts
   - Proper matchers

2. **Integration testing**
   - Test full workflow execution
   - Verify loop breaking
   - Test error recovery
   - Session recovery validation

**Uncertainties to Resolve**:
- Error recovery strategy (1.2)
- Context window management (2.3)

### Phase 4: Quality & Testing (Week 5)
**Goal**: Production readiness

1. **Quality gates**
   - Language-specific test runners
   - Coverage measurement
   - Security scanning (basic)

2. **Comprehensive testing**
   - Unit tests for each tool
   - Integration test suite
   - Failure scenario testing
   - Performance profiling

**Uncertainties to Resolve**:
- Evidence requirements (1.3)
- Quality gate integration (3.3)

## Risk Mitigation Strategies

### High-Risk Areas

1. **Command Injection Failure**
   - **Mitigation**: Implement fallback to file-based command queue
   - **Detection**: Log all injection attempts
   - **Recovery**: Manual command execution path

2. **Infinite Loops Despite Protection**
   - **Mitigation**: External monitoring script
   - **Detection**: Timestamp-based progress tracking
   - **Recovery**: Kill switch via file flag

3. **State Corruption**
   - **Mitigation**: State backups before each modification
   - **Detection**: Schema validation on read
   - **Recovery**: Restore from backup

4. **Context Window Overflow**
   - **Mitigation**: Aggressive archiving strategy
   - **Detection**: Token counting before operations
   - **Recovery**: Auto-compaction trigger

## Success Criteria

### Minimum Viable Implementation
- [ ] Can execute a simple task from start to finish
- [ ] Handles basic errors without human intervention
- [ ] Recovers from session restart
- [ ] Prevents infinite loops
- [ ] Generates valid evidence

### Production Ready
- [ ] Handles all error scenarios gracefully
- [ ] Maintains state across multiple sessions
- [ ] Processes discoveries automatically
- [ ] Completes full phase transitions
- [ ] Passes comprehensive test suite

## Investigation Tasks (Do First)

### Task 1: Hook JSON Format Discovery
```bash
# Create test hook to log actual formats
cat > tools/test_hook.py << 'EOF'
#!/usr/bin/env python3
import json, sys
input_data = json.load(sys.stdin)
with open('/tmp/hook_test.json', 'w') as f:
    json.dump(input_data, f, indent=2)
print(json.dumps({"continue": True}))
EOF

# Add to .claude/settings.json and trigger
```

### Task 2: Command Injection Testing
```python
# Test various command formats
test_commands = [
    "/explore",
    "/write_tests",
    "Execute: /implement",
    "Continue with: /doublecheck",
    "Multi\nLine\nCommand"
]
# Test each in Stop hook
```

### Task 3: State Parsing Reliability
```python
# Test CLAUDE.md parsing edge cases
test_cases = [
    "Malformed JSON in workflow_state",
    "Missing workflow_state block",
    "Concurrent state modifications",
    "Large state objects"
]
```

## Decision Points Requiring User Input

1. **State Storage Location** - CLAUDE.md vs separate file?
2. **Error Recovery Aggressiveness** - Conservative vs aggressive?
3. **Evidence Strictness** - What's required for phase completion?
4. **Language Support Priority** - Python only or multi-language?
5. **Manual Intervention Points** - Where should system request help?

## Next Immediate Actions

1. **Investigate hook JSON formats** (Task 1)
2. **Test command injection** (Task 2)  
3. **Fix broken references** (current count: 120)
4. **Create mock workflow_orchestrator.py** for testing
5. **Set up test evidence structure**

## Estimated Timeline

- **Week 1**: Foundation and investigation
- **Week 2-3**: Core tool implementation
- **Week 3-4**: Discovery system
- **Week 4**: Hook configuration and integration
- **Week 5**: Testing and quality gates
- **Total**: 5 weeks to production-ready system

## Critical Path

1. Hook format investigation → 
2. workflow_orchestrator.py → 
3. Hook configuration → 
4. Integration testing → 
5. Production deployment

Without step 1, everything else is guesswork.