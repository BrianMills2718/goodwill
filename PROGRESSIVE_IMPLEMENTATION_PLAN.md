# Progressive Implementation Plan: Working Hook → V4 Autonomous System

## Current Working Components Analysis

### What We Have That Works:
1. **Working TDD Hook** (`reference_hooks/tdd_workflow.py`):
   - ✅ Basic state management (workflow_state.txt)
   - ✅ Proper JSON output for Claude Code Stop hooks
   - ✅ Clear workflow cycle: load_phase → explore → write_tests → implement → run_tests → doublecheck → commit
   - ❌ **Issue**: No loop prevention - caused infinite loops

2. **Safety Pattern Examples** (`test_hooks/`):
   - ✅ `counter_hook.py` - Shows iteration counting and stop conditions
   - ✅ `simple_block_hook.py` - Basic blocking pattern

3. **Current Project State**:
   - ✅ Phase 1.1 complete (working Goodwill scraper with 11/11 tests passing)
   - 🔄 Need to complete Phase 1: eBay API (1.2), Technical Infrastructure (1.3), Keyword Research (1.4)

## Progressive Implementation Phases

### **Phase A: Add Basic Safety** (Week 1)
**Goal**: Make the working hook safe by adding simple loop prevention

**Tasks**:
1. Copy `reference_hooks/tdd_workflow.py` → `.claude/hooks/safe_tdd_workflow_v1.py`
2. Add iteration counter (pattern from `counter_hook.py`)
3. Add max iterations limit (7 iterations like v4 spec)
4. Add stop-hook counter (3 stop-hook limit like v4 spec)
5. Test with Phase 1.2 (eBay API setup) to verify it stops appropriately

**Success Criteria**:
- Hook runs for max 7 iterations then stops
- Hook stops after 3 consecutive Stop hook blocks
- Completes at least one TDD cycle without infinite loops
- Advances Phase 1 progress

### **Phase B: Add Health Monitoring** (Week 2)  
**Goal**: Add basic project health and progress validation

**Tasks**:
1. Add git status monitoring before each step
2. Add file/directory existence checks
3. Add basic test results validation
4. Add progress evidence collection
5. Add simple state reconciliation (if tests fail, don't advance)

**Success Criteria**:
- Detects when tests are failing and adjusts workflow
- Validates that files exist before marking tasks complete  
- Can recover from basic failures (e.g., missing files)

### **Phase C: Add State Reconciliation** (Week 3)
**Goal**: Add intelligent state management and recovery

**Tasks**:
1. Add state validation between workflow steps
2. Add recovery from failed states  
3. Add manual override capability via files
4. Add phase completion validation
5. Add uncertainty escalation (if stuck, escalate to deferred)

**Success Criteria**:
- Can detect and recover from workflow failures
- Provides manual override when needed
- Properly validates phase completion before advancing

### **Phase D: Add Evidence Validation** (Week 4)
**Goal**: Add LLM-based intelligent validation (full v4 features)

**Tasks**:
1. Add LLM-based evidence checking using workflow orchestrator
2. Add reality checks against actual project state  
3. Add intelligent uncertainty resolution
4. Add full automation health monitoring
5. Add evidence-based decision making

**Success Criteria**:
- Uses LLM to validate that evidence matches claims
- Can make intelligent decisions about workflow progression
- Full v4 autonomous system capabilities

## Implementation Strategy

**Start Small**: Begin with Phase A using the working hook as foundation
**Test Each Phase**: Verify each enhancement works before adding the next
**Incremental Value**: Each phase should provide immediate value to the project
**Real Work**: Test on actual Phase 1 tasks (eBay API, etc.) not synthetic examples

## Current Next Step

**Phase A, Task 1**: Copy the working TDD hook and add basic iteration counting to prevent infinite loops, then test with Phase 1.2 (eBay API setup).