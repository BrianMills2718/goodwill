# Claude Code & Repository Structure Decisions (Any Project)

## Project Context Template
[Describe your project's purpose, stakeholders, and constraints here]

## Core Architectural Decisions

### 1. Documentation Structure
**Decision**: Three-tier documentation approach
- **`docs/behavior/`** - WHAT the system should do (requirements, goals, uncertainties)
- **`docs/architecture/`** - HOW to build the system (technical design, components)
- **`docs/development_roadmap/`** - CURRENT STATUS and path forward (phases, progress tracking)

**Rationale**: Separates concerns clearly - behavior defines requirements, architecture defines implementation approach, roadmap tracks execution progress.

### 2. Phase Management Strategy
**Decision**: Dual-file phase tracking
- **`phases.md`** - High-level overview with status checkboxes and references
- **`phase_X_name.md`** - Detailed implementation plans for each phase

**Key Rules**:
- **Status lives ONLY in `phases.md`** - single source of truth for completion tracking
- **Phase files are status-neutral** - contain implementation details, not current state
- **CLAUDE.md references both** - gets status from phases.md, gets details from phase files

**Rationale**: Allows quick status checks while maintaining detailed implementation guidance. Prevents contradictory status claims across multiple files.

### 3. Directory Structure & Organization
```
/
├── CLAUDE.md                    # Current implementation plan (auto-updated)
├── project_architecture.md     # This file - architectural decisions
├── src/                         # Main codebase
│   ├── [component_1]/          # Primary component/module
│   ├── [component_2]/          # Secondary component/module
│   └── [component_3]/          # Additional components as needed
├── docs/                       # Permanent documentation
│   ├── behavior/               # System requirements and goals
│   ├── architecture/           # Technical design documents
│   └── development_roadmap/    # Phase planning and status tracking
├── investigations/             # Technical research and LLM debugging
│   ├── [area_1]/              # Investigation area (e.g., authentication)
│   ├── [area_2]/              # Investigation area (e.g., performance)
│   ├── [area_3]/              # Investigation area (e.g., integration)
│   └── errors/                # Error pattern analysis and debugging
├── research/                  # Domain knowledge and strategy research
│   ├── [domain_1]/            # Domain area (e.g., market analysis)
│   ├── [domain_2]/            # Domain area (e.g., user research)
│   └── [domain_3]/            # Domain area (e.g., competitors)
├── tests/                     # All test files
│   ├── unit/                  # Component tests
│   ├── integration/           # API and system integration tests
│   └── e2e/                   # End-to-end workflow tests
├── data/                      # Data pipeline storage (if applicable)
│   ├── raw/                   # Unprocessed data from external sources
│   └── processed/             # Cleaned and analyzed data
├── config/                    # Configuration files and settings
├── tools/                     # Utility scripts
│   ├── workflow/             # Autonomous workflow tools
│   │   ├── workflow_orchestrator.py
│   │   ├── evidence_validator.py
│   │   ├── discovery_classifier.py
│   │   └── uncertainty_resolver.py
│   ├── validate_references.py
│   ├── load_context.py
│   └── inject_error.py
├── logs/                      # Structured logging system (see Error Management)
│   ├── errors/                # Error tracking and resolution
│   ├── debug/                 # Component-specific debug logs
│   └── investigation/         # Research session logs
├── output/                    # Generated deliverables
│   └── [output_type]/         # Project-specific output directories
├── archive/                   # Mirror structure for archival with provenance
│   ├── ARCHIVAL_STRUCTURE.md  # Archive organization documentation
│   ├── [mirror of all directories] # Same structure as main codebase
│   └── [each dir has ARCHIVAL_REASON.md] # Archival decision records
└── .claude/                   # Claude Code configuration
    └── commands/              # Custom slash commands
        └── [command_group]/   # Grouped custom commands
```

### 4. Directory Purpose & Generalizability
**Decision**: Distinguish between technical investigation and domain research

**Investigations vs Research**:
- **`investigations/`**: Technical research for implementation (LLM debugging, tool building, API analysis)
  - Used heavily by Claude Code for documenting technical discoveries
  - Focus: "How do I build this?" and "Why isn't this working?"
  - Examples: API endpoint discovery, authentication analysis, error debugging
  
- **`research/`**: Domain knowledge and business strategy research  
  - Focus: "What should I build?" and "Why does this matter?"
  - Examples: User needs analysis, competitive research, business requirements

**Data vs Output**:
- **`data/`**: Input data pipeline (raw → processed)
  - `raw/`: Unprocessed data from external sources
  - `processed/`: Cleaned, enriched, analysis-ready data
  
- **`output/`**: Generated deliverables for human consumption
  - Project-specific subdirectories (reports/, exports/, visualizations/)

**Generalizability Assessment**:
- **Universal (works for any project)**: docs/, src/, tests/, tools/, config/, logs/, .claude/
- **Research-heavy projects**: investigations/, research/ 
- **Data projects**: data/raw/, data/processed/
- **Project-specific**: Subdirectories within research/ and output/

**Template for new projects**: Start with universal directories, add investigations/ and research/ for research-heavy work, add data/ for data processing projects.

### 5. Archival System with Provenance
**Decision**: Mirror codebase structure in archive/ with dated files and decision records

**Archival Structure**:
- **Mirror organization**: archive/ maintains same directory structure as main codebase
- **Dated file naming**: Archived files prefixed with YYYYMMDD_ (e.g., `20250920_old_module.py`)
- **Decision records**: Each archive directory contains `ARCHIVAL_REASON.md` documenting rationale

**When to Archive**:
- File replaced by newer approach with different architecture
- Experimental code that didn't work out  
- Outdated documentation or deprecated configurations
- Code no longer needed for current implementation

**Archival Process**:
1. Move file to corresponding archive/ directory with date prefix
2. Create/update ARCHIVAL_REASON.md with context and rationale
3. Update cross-references to point to replacement files
4. Document decision for future reference and learning

**Benefits**:
- **Preserves context** for why changes were made
- **Maintains project history** without cluttering active codebase
- **Enables learning** from previous approaches and decisions
- **Supports rollback** if new approaches prove problematic

## Core Infrastructure Tools

### 6. Cross-Reference Validation System
**Built Tool**: `tools/validate_references.py`
- **Purpose**: Validates all cross-references across Python files, Markdown files, and .ref companion files
- **Features**: Regex-based extraction, broken link detection, structured error reporting
- **Integration**: Git pre-commit hooks block commits with broken references
- **Testing**: Comprehensive unit tests covering all validation scenarios

### 7. Context Loading System  
**Built Tool**: `tools/load_context.py`
- **Purpose**: Loads complete context for any target file before modification
- **Features**: Extracts cross-references, analyzes dependencies, loads full text of related files
- **Usage**: MANDATORY before modifying any file to understand impact
- **Output**: Comprehensive context including behavior docs, architecture docs, phase plans, dependencies

### 8. Error Management System
**Built Tool**: `tools/inject_error.py`
- **Purpose**: Automatically injects errors into CLAUDE.md Active Errors section
- **Features**: Structured error logging, automatic CLAUDE.md updates, resolution tracking
- **Integration**: Fail-fast error handling with detailed log files and resolution instructions
- **Error Types**: Broken references, file moves, import errors, validation failures

### 9. Git Workflow Integration
**Git Hooks Implementation**:
- **Pre-commit hook**: Validates all cross-references before allowing commits
- **Post-commit hook**: Detects file moves and automatically creates reference update tasks
- **Error injection**: Broken references automatically appear in CLAUDE.md for immediate attention

**Benefits**:
- **Prevents broken documentation** from entering the repository
- **Automatic maintenance** of cross-reference integrity
- **Immediate visibility** of issues requiring attention

## Claude Code Workflow Integration

### 10. Error Management Workflow
**Decision**: Fail-fast, fail-loud with automatic CLAUDE.md injection

**Error Flow**:
1. **Error occurs** in any function
2. **Detailed log created** in `logs/errors/active/error_YYYYMMDD_HHMMSS.log`
3. **Concise entry injected** into CLAUDE.md `🚨 ACTIVE ERRORS` section
4. **Summary index updated** in `logs/errors/active/summary.json`
5. **Claude investigates** using structured log format
6. **Error removed** from CLAUDE.md when resolved, moved to resolved logs

**Log Structure**:
- **Individual error logs** with full context, reproduction steps, investigation notes
- **Summary index (JSON)** for quick error overview without reading full logs
- **Hierarchical organization** (active/resolved/daily) for efficient navigation
- **Standardized format** with clear sections for context, traceback, debugging info

### 11. Evidence-Based Development
**Decision**: All claims require documented proof in `investigations/`

**Evidence Structure**:
- **Phase-based organization**: `investigations/[area]/phase_X/findings.md`
- **Test results**: `investigations/[area]/phase_X/test_results.log`
- **Implementation proof**: `investigations/[area]/phase_X/implementation_proof.md`
- **Evidence manifest**: `investigations/[area]/phase_X/evidence.json`
- **Symlink to current**: `investigations/[area]/current_phase → phase_X/`
- **Archive on completion**: `archive/investigations/[area]/YYYYMMDD_phase_X/`
- **Raw execution logs** and outputs preserved for all validation claims

**Evidence JSON Schema** (`evidence.json`):
```json
{
  "phase": "phase_X",
  "area": "scraping",
  "timestamp": "2025-01-20T14:03:00Z",
  "artifacts": {
    "findings": "findings.md",
    "test_results": "test_results.log",
    "implementation_proof": "implementation_proof.md",
    "coverage_report": "coverage/summary.json"
  },
  "metrics": {
    "tests_passed": true,
    "test_count": 42,
    "coverage_percentage": 85,
    "confidence": "high"
  },
  "validation": {
    "cross_references_valid": true,
    "evidence_complete": true,
    "quality_gates_passed": true
  }
}

**Cross-Reference**: See evidence flow in `hook_mermaid_diagram_full3_w_tdd.txt` for visual representation of evidence capture and archival process.

**Integration with Phases**:
- **No success declarations** without evidence files
- **Phase completion** requires end-to-end validation with documented proof
- **Evidence references** in phases.md for all completed tasks

### 12. Custom Commands Strategy
**Decision**: Phase-agnostic commands that work throughout project lifecycle

**Key Command**: `/update_plans_within_phase`
- **Syncs documentation** between CLAUDE.md, phases.md, and phase files
- **Enforces status centralization** (only phases.md tracks completion)
- **Maintains self-contained CLAUDE.md** for new Claude sessions
- **Integrates error tracking** and evidence requirements

**Cross-Reference**: See workflow diagram at `hook_mermaid_diagram_full3_w_tdd.txt` for visual representation of command flow and hook integration.

**Command Philosophy**:
- **Works at all phases** - not specific to any particular phase
- **Evidence-based updates** - requires proof before marking tasks complete
- **New LLM ready** - updated CLAUDE.md contains everything needed for next steps

### 13. Investigation Workflow
**Decision**: Structured research approach using Claude Code subagents

**Investigation Pattern**:
1. **Parallel research** using multiple subagents for complex topics
2. **Structured documentation** in investigations/ with standardized format
3. **Evidence collection** with raw outputs and analysis
4. **Integration into phases** - findings inform detailed implementation plans

**Documentation Requirements**:
- **Exact steps taken** for reproducibility
- **Complete outputs** for verification
- **Analysis of results** and implications for project goals
- **References to related investigations** and patterns

## Implementation Principles

### 14. Status Management Rules
**CRITICAL RULE**: Status information lives ONLY in `phases.md`
- **Phase files**: Implementation details, technical patterns, code examples (status-neutral)
- **CLAUDE.md**: Current tasks with status from phases.md + details from phase files
- **Evidence files**: Proof of completion, not status claims
- **No contradictory status** across multiple files

**Important Distinction - Status vs State**:
- **Status** (phases.md only): Phase/task completion checkboxes, what is "done" vs "pending"
- **State** (CLAUDE.md workflow_state): Ephemeral agent state like current_command, loop_iterations, last_evidence
- Rule: CLAUDE.md may contain **ephemeral agent state** (loop counters, current command) but **never** phase completion status

### 15. File Organization Discipline
**Strict Rules**:
- **NO temp files in root** - use logs/temp/ or /tmp/
- **Clean up investigations** within 48 hours - move to appropriate directories
- **Archive completed work** to prevent confusion with current efforts
- **Document file placement** in CLAUDE.md for all new file types

### 16. Claude Code Optimization
**Leverage Claude Code Features**:
- **Subagents for complex research** 
- **Multi-Claude workflows** for parallel development streams
- **Custom slash commands** for repeated workflows
- **"Think harder" mode** for complex architectural decisions
- **Testing workflows** with iterative improvement cycles

**Session Management**:
- **Self-contained CLAUDE.md** - new sessions need no external context
- **Clear next steps** always documented
- **Error visibility** immediate for any new Claude session
- **Evidence references** for understanding previous work

### 17. Automated Workflow System
**Decision**: Autonomous execution via Claude Code hooks and command orchestration

**Core Components**:
- **`workflow_orchestrator.py`** - Reads CLAUDE.md state, determines next command via Stop hook
- **`evidence_validator.py`** - Validates evidence meets completion criteria via PostToolUse hook
- **`discovery_classifier.py`** - Categorizes findings as minor/major/strategic via PostToolUse hook
- **`uncertainty_resolver.py`** - Orchestrates categorization and resolution logic for `/categorize_uncertainties` command

**State Management**:
- CLAUDE.md contains workflow state in structured JSON block
- Loop iteration counters for breaker logic (max 7 iterations)
- Current command tracking for recovery from session restarts
- Evidence references for validation

**Command Flow Pattern**:
```
/explore → /write_tests → /implement → /run_tests → /doublecheck → (loop if issues)
```

**Complete Command Set** (see `hook_mermaid_diagram_full3_w_tdd.txt` for visual flow):
- `/load_phase_plans` - Entry point: Read phases.md → Update CLAUDE.md state
- `/explore` - Read files, identify unknowns
- `/write_tests` - TDD: Define success criteria first  
- `/implement` - Code to pass tests
- `/run_tests` - Execute test suite
- `/doublecheck` - Verify implementation vs requirements
- `/categorize_uncertainties` - Strategic vs Pre-implementation vs Implementation
- `/review_architecture_behavior` - Check docs for guidance on strategic uncertainties
- `/investigate_pre_impl` - Research unknowns
- `/update_plans_within_phase` - Integrate findings → CLAUDE.md
- `/escalate_to_deferred` - Archive unresolved to investigations/deferred/
- `/close_phase` - Archive evidence, update phases.md
- `/validate_phase_completion` - Verify evidence, test coverage, quality
- `/review_docs_between_phases` - Check architecture/behavior alignment
- `/load_next_phase` - Update CLAUDE.md with next phase

**CLAUDE.md Workflow State Block**:
```json
{
  "workflow_state": {
    "current_command": "/implement",
    "current_phase": "phase_2",
    "loop_iterations": 3,
    "last_evidence": "investigations/scraping/phase_2/findings.md",
    "uncertainties_remaining": 2,
    "confidence": "medium",
    "test_status": "failing"
  }
}
```

### 18. Test-Driven Development Integration
**Decision**: Tests as objective success criteria to constrain optimism

**TDD Workflow**:
1. **Write tests first** - `/write_tests` before `/implement`
2. **Tests as gates** - Implementation blocked until tests defined
3. **Evidence via tests** - Test results become primary evidence
4. **Failure triggers investigation** - Failed tests create uncertainties

**Test Evidence Requirements**:
- All tests must pass for phase completion
- Test logs preserved in `investigations/[area]/phase_X/test_results.log`
- Coverage metrics tracked (minimum 80% for critical paths)

**Automated Testing Requirements**:
- Tests auto-run via PostToolUse hooks after implementation
- Test failures auto-inject as uncertainties in CLAUDE.md
- Coverage tracked and validated before phase completion
- Test results become primary evidence for completion claims

### 19. Claude Code Hook Configuration
**Decision**: Hooks orchestrate autonomous workflow

**Hook Configuration** (`.claude/settings.json`):
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/workflow/session_recovery.py",
        "timeout": 15
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/tools/workflow/workflow_orchestrator.py",
        "timeout": 20
      }]
    }],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {"type": "command", "command": "$CLAUDE_PROJECT_DIR/tools/workflow/evidence_validator.py", "timeout": 30},
          {"type": "command", "command": "$CLAUDE_PROJECT_DIR/tools/workflow/discovery_classifier.py", "timeout": 20}
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {"type": "command", "command": "$CLAUDE_PROJECT_DIR/tools/validate_references.py", "timeout": 15}
        ]
      }
    ]
  }
}
```

**Hook Orchestration Pattern**:
- SessionStart recovers state and resumes workflow from last command
- Stop hook reads state and injects next command via JSON output
- PostToolUse validates evidence and detects discoveries
- PreToolUse ensures cross-references valid before modifications

**Session Recovery Pattern** (SessionStart):
```python
# Read workflow state from CLAUDE.md
state = parse_claude_md_workflow_state()
if state and state.get("current_command"):
    # Check for dirty lock indicating crash
    if os.path.exists(".claude/.lock/stop.lock"):
        print(f"Recovering from {state['current_command']}")
        # Inject context to resume
        return {
            "hookSpecificOutput": {
                "additionalContext": f"Session recovered. Continue from: {state['current_command']}"
            }
        }
```

**Cross-Reference**: See detailed hook integration points in `hook_mermaid_diagram_full3_w_tdd.txt` with dotted lines showing automation connections.

### 20. Command Injection via Hooks
**Decision**: Hooks control Claude through JSON output

**Stop Hook Control Pattern**:
```python
import os, time, json

# Check for recursion protection first
if input_data.get("stop_hook_active"):
    return {"continue": True, "suppressOutput": True}

# Basic lock mechanism to prevent concurrent Stop races
lock_file = ".claude/.lock/stop.lock"
os.makedirs(".claude/.lock", exist_ok=True)
if os.path.exists(lock_file):
    lock_age = time.time() - os.path.getmtime(lock_file)
    if lock_age < 5:  # Lock still fresh
        return {"continue": True, "suppressOutput": True}
    
# Create lock
with open(lock_file, "w") as f:
    f.write(str(time.time()))

# Force Claude to continue with next command
output = {
    "decision": "block",  
    "reason": f"Execute: {next_command}"  # Becomes Claude's next prompt
}

**Evidence Validation Pattern**:
```

**Evidence Validation Pattern** (PreToolUse):
```python
# Use correct field names for PreToolUse
if not references_valid:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Cross-references broken. Fix before editing."
        }
    }
```

**PostToolUse Feedback Pattern**:
```python
# Block on missing evidence in PostToolUse
if evidence_file.is_empty():
    output = {
        "decision": "block",
        "reason": "Evidence validation failed. Rerun tests with verbose output."
    }
```

### 21. Loop Breaking and Recovery
**Decision**: Bounded iteration with escalation strategies

**Loop Breaker Logic**:
- Maximum 7 iterations for any uncertainty resolution loop
- Iteration count tracked in workflow state
- Breaker triggers escalation strategy

**Recovery Strategies**:
1. **Archive and skip**: Move unresolved to `investigations/deferred/` via `/escalate_to_deferred`
2. **Simplify objective**: Reduce scope to achievable subset
3. **Human escalation**: Create detailed report for manual review

**Cross-Reference**: See loop breaking decision point and escalation flow in `hook_mermaid_diagram_full3_w_tdd.txt`.

### 22. Quality Validation Pipeline
**Decision**: Automated quality checks beyond testing

**Quality Gates**:
- **No hardcoded secrets**: Scan for API keys, passwords
- **Cross-reference integrity**: All references must be valid
- **Evidence completeness**: All claims have supporting evidence
- **Test coverage**: Minimum thresholds for critical paths

**Implementation**:
- PostToolUse hooks run quality validators
- Failures block progression and inject errors
- Quality metrics tracked in workflow state

## Tools & Tests Curation Strategy

### 23. Testing vs. CLAUDE.md Reference Strategy
**Key Distinction**: Whether to test something vs. whether to reference it in CLAUDE.md are separate decisions

**Testing Strategy** (What should have tests):
- **Critical Infrastructure**: Tools that break the entire workflow if they fail
- **Complex Logic**: Regex parsing, file system operations, data transformations
- **Integration Points**: API interactions, cross-component workflows
- **Business Logic**: Core domain logic and algorithms
- **Error-Prone Code**: File manipulation, external service calls

**CLAUDE.md Reference Strategy** (Attention economics):
- **High-Value References**: Only tools where recreate cost >> reference cost
- **Critical Dependencies**: Tools that break workflows if missing
- **Cross-Phase Usage**: Tools needed throughout project lifecycle
- **Domain-Specific Logic**: Project-specific insights and algorithms

### 24. Attention Economics & Reference Tradeoffs
**Key Principle**: Every reference in CLAUDE.md reduces Claude's attention to other instructions

**High-value CLAUDE.md references** (worth the attention cost):
- **Recreate Cost >> Reference Cost**: Complex tools that would take significant time/context to rebuild vs. brief reference
- **Frequent Cross-Phase Usage**: Tools needed throughout project lifecycle, not just once
- **Critical Path Dependencies**: Tools that other processes rely on, breaking workflows if recreated incorrectly
- **Domain-Specific Logic**: Project-specific algorithms that embody hard-won insights

**Low-value CLAUDE.md references** (delete rather than reference):
- **Recreate Cost < Reference Cost**: Simple utilities where describing them takes more tokens than rebuilding
- **One-Time Usage**: Tools unlikely to be needed again or in different contexts
- **Generic Patterns**: Standard approaches Claude already knows well
- **Easy Substitution**: Tools with many equivalent alternatives

**Testing vs. CLAUDE.md Decision Matrix**:
| Tool Type | Create Tests? | Reference in CLAUDE.md? | Rationale |
|-----------|---------------|-------------------------|-----------|
| Critical Infrastructure | ✅ Yes | Only if cross-phase | Test for reliability, reference only if frequently used |
| Business Logic | ✅ Yes | ✅ Yes | Both test and reference - core project value |
| Simple Utilities | ❌ No | ❌ No | Neither needed - easy to recreate |
| Integration Points | ✅ Yes | Depends on complexity | Test for reliability, reference if complex |

## Cross-Reference System & Context Loading

### 25. File Cross-Reference Architecture
**Decision**: Comprehensive traceability chain across all documentation and code

**Traceability Flow**:
```
Behavior Docs ↔ Architecture Docs ↔ Phase Plans ↔ Implementation Files
```

**Cross-Reference Patterns**:
- **Code Files**: Include TRACEABILITY comments linking to phase plans, architecture, behavior docs
- **Phase Plans**: Reference implementation files and related documentation  
- **Architecture Docs**: Link to phase plans and behavior requirements
- **Behavior Docs**: Reference architecture implementations and current phases

**Non-Code Files**: Use companion `.ref` files for JSON, config files, etc.

### 26. Context Loading System
**Decision**: Automatic context loading tool for comprehensive file modification awareness

**Core Tool**: `tools/load_context.py`
- **Input**: Any project file path
- **Output**: Complete context including all cross-references and full text of related files
- **Usage**: MANDATORY before modifying any file

**Context Loading Includes**:
- All behavior docs that reference the target file
- All architecture docs that reference the target file
- All phase plans that reference the target file
- All files with dependencies (imports, imported by)
- Full text content of ALL referenced files
- Planning dependencies vs runtime dependencies

**Dependency Types**:
- **Planning Dependencies**: Development order requirements (Phase 1 → Phase 2)
- **Runtime Dependencies**: Import/execution relationships
- **Configuration Dependencies**: Config files used by code files

### 27. Automated Reference Validation
**Decision**: Fail-fast reference validation with automatic error injection

**Validation Tools**:
- **`tools/validate_references.py`**: Check all cross-references are valid file paths
- **Git hooks**: Detect file moves/renames and create update tasks
- **Pre-commit validation**: Block commits with broken references

**Error Integration**:
- **Broken references** → Automatic injection into CLAUDE.md error section
- **File moves** → Auto-created reference update tasks with specific instructions
- **Missing files** → Detailed error logs with search/replace guidance

**Reference Update Workflow**:
1. File moved/renamed detected by git hooks
2. Error automatically injected into CLAUDE.md with update instructions
3. Claude Code sees error and follows provided search/replace guidance
4. Validation tool confirms all references updated
5. Error removed from CLAUDE.md when resolved

### 28. Context Loading Usage Pattern
**Mandatory Workflow for File Modifications**:

```bash
# Step 1: Load complete context before any modification
python tools/load_context.py src/[component]/[file].py > context_[file].txt

# Step 2: Review context file to understand:
# - What behavior requirements this file implements
# - What architecture components it belongs to  
# - What phase plans govern its development
# - What other files depend on it or it depends on
# - Full text of all related documentation

# Step 3: Make modifications with full awareness of impact

# Step 4: Update cross-references if file purpose/location changes

# Step 5: Validate references still work
python tools/validate_references.py
```

### 29. Reference Templates for Reusable Patterns

**Code File Cross-Reference Template**:
```python
"""
[filename].py

TRACEABILITY:
- Phase Plan: /docs/development_roadmap/[phase_file].md (Section X.Y)
- Architecture: /docs/architecture/[arch_file].md ([Component Name])
- Behavior: /docs/behavior/[behavior_file].md ([Requirement Section])

CROSS-REFERENCES:
- Related Files: [list of related files]
- Tests: [list of test files]
- Tools: [list of related tools]
- Config: [list of config files used]

DEPENDENCIES:
- Imports: [list of external imports]
- Imported By: [list of files that import this]
- Planning: Blocks [list], Blocked By [list]
"""
```

**Phase Plan Cross-Reference Template**:
```markdown
## [Section Title]

**Implementation Files:**
- `[file_path]` - [brief description]
- `[file_path]` - [brief description]

**Related Architecture:** [link to architecture doc section]
**Related Behavior:** [link to behavior doc section]
**Dependencies:** [list of planning dependencies]
```

**Non-Code File Reference Template** (`.ref` files):
```markdown
# Cross-References for [filename]

**Traceability:**
- Phase Plan: [path and section]
- Architecture: [path and section]  
- Behavior: [path and section]

**Used By:**
- [list of files that use this config/data]

**Related Files:**
- [list of related configuration or data files]
```

## Integration Points

### 30. Phase Transitions
**Workflow for completing phases**:
1. **Evidence collection** with end-to-end validation
2. **Update phases.md** to mark tasks complete
3. **Archive investigation files** to avoid future confusion
4. **Update CLAUDE.md** for next phase priorities
5. **Error resolution** before phase completion

### 31. Error Resolution Integration
**When errors block progress**:
1. **Automatic injection** into CLAUDE.md error section
2. **Investigation documentation** in investigations/errors/
3. **Pattern analysis** for recurring issues
4. **Resolution testing** with evidence collection
5. **Knowledge transfer** to prevent future occurrences

## Current Implementation Status

### 32. Built and Tested Infrastructure
**✅ Complete and Operational**:
- Cross-reference validation system with git integration
- Context loading for comprehensive file modification awareness
- Error injection and management with automatic CLAUDE.md updates
- Archive system with provenance tracking
- Comprehensive test suite
- File organization guidelines for Claude Code

**✅ Git Workflow Integration**:
- Pre-commit hooks preventing broken reference commits
- Post-commit hooks detecting file moves and creating update tasks
- Automatic error injection into CLAUDE.md for immediate visibility

**✅ Documentation Framework**:
- Complete architectural decision documentation
- Reusable templates for cross-references
- Clear guidelines for file placement and organization
- Evidence-based development requirements

## Future Considerations

### 33. Scaling Decisions
**As project grows**:
- **Modular logging** strategy can expand to new components
- **Investigation structure** can add new research areas
- **Phase management** can accommodate additional development streams
- **Error tracking** can scale to multiple parallel development efforts

### 34. Team Collaboration
**Multi-developer readiness**:
- **Shared CLAUDE.md** through git with automatic updates
- **Investigation documentation** provides context for team members
- **Error visibility** prevents duplicate debugging efforts
- **Evidence-based development** enables verification of team member work

---

*This document captures architectural decisions as they're made. Update when new structural decisions are finalized.*