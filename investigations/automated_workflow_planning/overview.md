# Automated Workflow Planning Investigation

## Task Overview

Create a fully automated development workflow for the Goodwill arbitrage project that uses Claude Code hooks to orchestrate the entire development lifecycle from project inception to completion, minimizing manual intervention while maintaining evidence-based development practices.

## Core Objectives

### 1. Automate the Proven Workflow Pattern
Implement the "explore, plan, code, commit" workflow as an automated sequence:
- **Explore**: Automatically investigate unknowns and gather context
- **Plan**: Generate structured implementation plans with extended thinking
- **Code**: Execute plans with continuous verification  
- **Commit**: Validate and commit with proper evidence

### 2. Integrate Discovery Detection
Build automatic discovery detection and classification:
- Monitor `investigations/` for new findings
- Classify discoveries (minor update vs major pivot)
- Automatically integrate discoveries into workflow
- Trigger appropriate response (continue vs reassess)

### 3. Create Self-Correcting Loops
Implement error detection and correction cycles:
- Automatic verification after implementation
- Error identification and root cause analysis
- Plan generation for fixes
- Re-execution until successful

### 4. Phase Management Automation
Automate phase transitions based on evidence:
- Completion detection through evidence validation
- Automatic archival of completed work
- Next phase loading and context switching
- Progress tracking in phases.md

## Current Assets

### Existing Infrastructure
1. **Documentation Structure**
   - Three-tier: behavior/ → architecture/ → development_roadmap/
   - Phase management: phases.md (status) + phase files (implementation)
   - CLAUDE.md as self-contained execution context

2. **Built Tools**
   - `validate_references.py` - Cross-reference validation
   - `load_context.py` - Context loading before modifications
   - `inject_error.py` - Automatic error injection to CLAUDE.md

3. **Established Patterns**
   - Evidence-based development in investigations/
   - Archive system with provenance tracking
   - Fail-fast error management

### Existing Workflow (Manual)
From `.claude/workflow_diagram.md`:
- Within-phase loop: implement → doublecheck → plan → update_plans
- Phase transitions: close_phase → load_next_phase
- Discovery handling: reassess_plans vs integrate_discovery

## Gaps to Address

### 1. Missing Automation Tools
**Need to build:**
- `discovery_detector.py` - Scan investigations/ for new findings
- `workflow_orchestrator.py` - Decide next command based on state
- `phase_completion_checker.py` - Validate phase completion with evidence
- `plan_classifier.py` - Determine if changes are minor or major

### 2. Undefined Command Mappings
**Need to define:**
- Which hooks trigger which commands
- How commands chain together automatically
- Decision logic for workflow branches
- State management between commands

### 3. Integration Points
**Need to connect:**
- Slash commands as manual entry points
- Hooks as automatic triggers
- Tools as execution engines
- Evidence as decision inputs

## Design Constraints

### 1. Claude Code Hook Limitations
- Hooks can only trigger shell commands
- Limited to PreToolUse, PostToolUse, Stop, SessionStart events
- Cannot directly invoke slash commands (must use tools)
- 60-second timeout for hook execution

### 2. State Management
- No persistent state between sessions
- Must use files for state tracking
- CLAUDE.md as primary state container
- phases.md as completion tracking

### 3. Evidence Requirements
- All decisions must be evidence-based
- Discoveries must be documented in investigations/
- Completion requires end-to-end validation
- Archives must maintain provenance

## Success Criteria

### 1. Minimal Manual Intervention
- User provides initial goal
- System automatically progresses through phases
- Manual input only for major strategic decisions
- Automatic error recovery and correction

### 2. Continuous Discovery Integration
- Discoveries detected without manual scanning
- Automatic classification and integration
- Plan updates triggered by findings
- No lost insights or ignored errors

### 3. Evidence Trail
- Complete documentation of all decisions
- Reproducible investigation paths
- Archived evidence for completed phases
- Clear provenance for all changes

### 4. Self-Maintaining
- Cross-references stay valid
- Errors surface immediately
- Plans stay synchronized
- Context remains complete

## Investigation Plan

### Phase 1: Command Structure Design
- Map out all required commands
- Define trigger conditions for each
- Establish command chaining logic
- Document state transitions

### Phase 2: Hook Configuration Design
- Define hook matchers for each trigger
- Create hook command scripts
- Design JSON output for decision control
- Plan error handling strategies

### Phase 3: Tool Development
- Build discovery_detector.py
- Build workflow_orchestrator.py
- Build phase_completion_checker.py
- Build plan_classifier.py

### Phase 4: Integration Testing
- Test individual command flows
- Test discovery detection and integration
- Test error correction loops
- Test phase transitions

### Phase 5: Full Workflow Testing
- End-to-end test from project start
- Test with various discovery scenarios
- Test error recovery paths
- Validate evidence generation

## Next Steps

1. Create detailed command flow diagram
2. Design state machine for workflow orchestration
3. Prototype key automation tools
4. Test integration with existing infrastructure
5. Build complete hook configuration
6. Validate with real project scenarios