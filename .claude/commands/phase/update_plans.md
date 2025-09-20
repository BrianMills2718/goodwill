I approve your recommendations. Commit current work, then update our short term and temporary plans in CLAUDE.md as well as our permanent long term plans to get to our goals here /home/brian/projects/goodwill/docs/development_roadmap/phases.md. Clear out resolved tasks/outdated information from CLAUDE.md, and mark them as done in the permanent plans. Populate CLAUDE.md with instructions for resolving the next tasks using evidence-based development practices. The instructions in CLAUDE.md should be detailed enough for a new LLM to implement with no context beyond CLAUDE.md and referenced files. Make sure to include the testing/validation plan in CLAUDE.md as well as the plan to resolve all uncertainties.

## Workflow
1. **Read phases.md**: Check `/docs/development_roadmap/phases.md` for current phase status
2. **Read Relevant Phase File**: Get implementation details from phase files (ignore any status claims)
3. **Update CLAUDE.md**: Remove completed tasks, add new plan details with phase file context
4. **Update phases.md**: Mark verified completions, add new tasks if needed (ONLY place for status)
5. **Verify**: Ensure new LLM could execute from CLAUDE.md alone

## Core CLAUDE.md Requirements

### 1. Development Philosophy Section (Mandatory)
Every CLAUDE.md must include:
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST AND LOUD PRINCIPLES**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured documentation files
- **LLM CAPABILITY IS NOT THE PROBLEM**: Any issues with LLM output quality is caused by bad prompting not by limitations of the LLM
- **CLAUDE CODE OPTIMISM PROBLEM**: Do NOT claim success until 100% proven with evidence
- **TIMEOUTS DO NOT COUNT AS SUCCESS**: Do not declare success if processes timeout or fail

### 1a. Success Validation Principles (Mandatory)
Every CLAUDE.md must include:
- **NO SUCCESS WITHOUT END-TO-END PROOF**: Never declare success until the complete pipeline works from start to finish
- **DEPLOYABILITY GATE**: Code is only complete when it can be executed without errors in a clean environment
- **FAIL-FAST ON IMPORTS**: Any import error or missing dependency immediately invalidates success claims
- **EVIDENCE-BASED SUCCESS**: Success requires demonstrable proof, not just file generation or partial functionality
- **MANDATORY END-TO-END TESTING**: Every claimed solution must include a working example that runs without errors
- **CLEAN ENVIRONMENT VALIDATION**: Test in isolated environment to catch dependency issues
- **ACTUAL USE CASE VERIFICATION**: Don't just test that code exists - test that it accomplishes the stated objective
- **DISTINGUISH PROGRESS FROM COMPLETION**: Clearly separate "made progress" from "achieved objective"
- **NO VICTORY LAPS**: Avoid celebratory language until complete functionality is proven

### 2. Project Structure Section (Mandatory)  
Concisely document:
- All relevant planning documentation in `/docs/`
- Key entry points and main orchestration files in `/src/`
- Module organization and responsibilities
- **Investigation Results**: Reference findings in `/investigations/` directories
- **Data Pipeline**: Current state of `/data/raw/` and `/data/processed/`

### 2a. File Organization Policy (Mandatory)
Every CLAUDE.md must include clear guidance on where to create files:

**Standard Project Structure**:
```
/
├── CLAUDE.md (current implementation plan)
├── src/ (main codebase - scrapers, analysis, etc.)
├── docs/ (permanent documentation)
├── tests/ (all test files - organized by type)
├── investigations/ (research results and evidence collection)
├── data/ (raw and processed data)
├── config/ (configuration files)
├── tools/ (utility scripts)
├── logs/ (application and debug logs)
├── output/ (generated suggestions and reports)
└── .claude/ (Claude Code configuration)
```

**File Creation Standards**:
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/` - NEVER in root
- **Investigation Work**: `investigations/[area]/` - research, analysis, prototyping
- **Evidence**: `investigations/[area]/findings.md` (active), archived when phase complete
- **Temporary Files**: `logs/temp/` or `/tmp/` - NEVER in root
- **Code**: `src/[component]/` following modular organization

**Root Directory Rules**:
- **NEVER create temp files in root**: No `temp*.txt`, `debug*.py`, `test_*.py` in project root
- **Clean up after investigations**: Move to appropriate directories within 48 hours
- **Document file placement**: CLAUDE.md must specify where each type of file belongs

### 2b. Phase Status Management (Mandatory)
Every CLAUDE.md must reference current status from phases.md and draw immediate plans from phase files:

**STATUS INTEGRATION TEMPLATE**:
```markdown
## Current Status & Immediate Plans

### Phase Status: [Current Phase from phases.md]
**Source**: `/docs/development_roadmap/phases.md` - ONLY source of status truth

### Active Tasks (from phases.md):
- [ ] [Task from phases.md with current status]
- [ ] [Task from phases.md with current status]

### Immediate Implementation Plan (from [phase_file.md]):
[Copy relevant technical details from current phase file]

#### Next Steps:
1. [Specific actionable step from phase file]
2. [Specific actionable step from phase file]
3. [Specific actionable step from phase file]

### Status Update Protocol:
- Read phases.md for current priorities and completion status
- Read relevant phase_X_name.md for detailed implementation guidance
- Update phases.md ONLY when tasks are verified complete with evidence
- Phase files remain status-neutral (implementation details only)
```

### 2c. Implementation Roadmap Integration (Mandatory)
Every CLAUDE.md must follow the systematic implementation workflow:

**Primary Documentation Structure**:
- **Master Plan**: `/docs/development_roadmap/phases.md` - Central task tracking and status
- **Phase Files**: `/docs/development_roadmap/phase_*.md` - Detailed implementation steps and technical patterns
- **Support Documents**: `/docs/behavior/` and `/docs/architecture/` - Requirements and design

**Workflow Integration Requirements**:
- CLAUDE.md must reference the relevant phase file for current tasks
- Include essential technical patterns and approaches from phase files
- Ensure CLAUDE.md is self-contained (new LLM needs no external context beyond referenced files)
- When discovering new issues: add tasks to phases.md and update relevant phase files

**Documentation Workflow**:
1. **Read phases.md** → identify next uncompleted task (ONLY source of status information)
2. **Read relevant phase file** → get complete implementation details (status-neutral how-to guide)
3. **Update CLAUDE.md** → include immediate tasks with all necessary context from phase files
4. **After completion** → update phases.md to mark tasks complete (ONLY place to update status)

**CRITICAL STATUS RULE**: Status information (phases, priorities, completion state) belongs ONLY in phases.md. Phase files contain implementation details and are status-neutral.

### 2c. Phase File Status Management (Critical)

**Phase Files Must Be Status-Neutral**:
- ❌ **FORBIDDEN**: "Status: ACTIVE", "Timeline: 3-4 hours", "Priority: P0", "BLOCKED", completion estimates
- ❌ **FORBIDDEN**: "Current State", "What's Working", "What's Broken" sections with current reality claims
- ✅ **ALLOWED**: Implementation steps, technical patterns, code examples, debugging approaches
- ✅ **ALLOWED**: "Background", "Requirements", "Implementation Plan", "Testing Strategy"

**Status Centralization Rules**:
- **phases.md**: Contains ALL status, priorities, completion tracking
- **Phase Files**: Contain technical implementation guidance only
- **CLAUDE.md**: References current status from phases.md, copies implementation details from phase files

### 3. Validation Strategy Requirements (Mandatory)
Every CLAUDE.md must include comprehensive validation appropriate to current phase:

**Required Validation Approach**:
- **Evidence Collection**: Document all findings, test results, and analysis in investigations/
- **Full Visibility**: All outputs, validation results, and analysis documented in structured format
- **Evidence-Based Claims**: No success declarations without demonstrable proof
- **Before/After Documentation**: Capture system state before and after changes
- **Persistent Documentation**: All validation and research output must be saved to appropriate directories

**Phase-Appropriate Validation**:
- **Foundation Phase**: Scraping success rates, API connectivity, data quality validation
- **Analysis Phase**: Algorithm accuracy, price prediction validation, confidence scoring
- **Decision Phase**: Suggestion quality, human approval rates, risk assessment accuracy
- **Automation Phase**: End-to-end workflow success, error handling, performance metrics

**Mandatory Validation Workflow**:
1. **Baseline Documentation**: Establish current state with measurable criteria
2. **Implementation Validation**: Collect evidence during changes with detailed outputs
3. **Functional Testing**: Verify each component works as intended
4. **Integration Testing**: Validate components work together
5. **Evidence Collection**: Document all results in structured files with full visibility
6. **Error Analysis**: When issues occur, capture detailed debugging information

### 4. Active Error Tracking Section (Mandatory)
Every CLAUDE.md must include a prominently placed error tracking section:

**ERROR TRACKING TEMPLATE**:
```markdown
## 🚨 ACTIVE ERRORS AND BLOCKERS

### Current Error Status: [CLEAR/BLOCKED]

### Active Errors:
- **[TIMESTAMP]** [ERROR_TYPE]: [Brief description]
  - **Impact**: [What functionality is broken]
  - **Log**: `logs/errors/active/error_YYYYMMDD_HHMMSS.log`
  - **Action**: [Clear next step for investigation/resolution]
  - **Status**: [INVESTIGATING/NEEDS_FIX/BLOCKED]

### Recently Resolved Errors:
- **[TIMESTAMP]** [ERROR_TYPE]: [Brief description] - ✅ RESOLVED
  - **Resolution**: [How it was fixed]
  - **Evidence**: [Link to evidence file]

### Error Resolution Instructions:
1. Read the detailed log file referenced above
2. Analyze root cause and implement fix
3. Test fix thoroughly with evidence collection
4. Once verified working, remove error entry from this section
5. Move error to "Recently Resolved" with solution summary
```

**ERROR INJECTION REQUIREMENTS**:
- **Automatic Error Capture**: All functions must log detailed errors to `logs/errors/active/error_YYYYMMDD_HHMMSS.log`
- **CLAUDE.md Auto-Update**: Error injection script must update the Active Errors section with concise entries
- **No Silent Failures**: Any caught exception must be logged and surfaced
- **Structured Log Format**: Use hierarchical log structure for efficient Claude navigation
- **Impact Assessment**: Document what functionality is broken by each error

### 5. Essential Tools & Tests Section (Mandatory)
Every CLAUDE.md must include curated tools/tests using attention economics:

**TOOLS & TESTS TEMPLATE**:
```markdown
## Essential Tools & Tests (Permanent Context)

### Core Validation Tools
- `[tool_path]` - [Brief description of complex, frequently-used functionality]
- `[tool_path]` - [Brief description of project-specific logic]

### Integration Test Suite  
- `[test_path]` - [Brief description of critical end-to-end validation]
- `[test_path]` - [Brief description of cross-component integration]

### Project-Specific Utilities
- `[utility_path]` - [Brief description of domain-specific algorithms]

### Cross-Reference & Context Tools
- `tools/load_context.py` - Load all cross-references and full text for any file before modification
- `tools/validate_references.py` - Check all cross-references are valid and report broken links

### Context Loading Usage
```bash
# MANDATORY: Before modifying any file, load complete context
python tools/load_context.py [target_file] > context_[filename].txt
# This loads: behavior docs, architecture docs, phase plans, dependencies, and FULL TEXT
```

### Attention Economics Notes:
- Only include tools where recreate cost >> reference cost
- Delete tools that are simple utilities Claude can rebuild quickly
- Focus on arbitrage-specific logic and critical dependencies
- Monthly cleanup of unreferenced tools in directories
```

**TOOL CURATION REQUIREMENTS**:
- **High-Value Only**: Include only tools that justify the attention cost
- **Brief References**: Concise descriptions that enable finding and understanding purpose
- **Regular Cleanup**: Remove tools not worth permanent context from directories
- **Attention Budget**: Every reference competes for Claude's focus on core instructions

### 5. Evidence Structure Requirements
```
investigations/
├── scraping/
│   ├── goodwill_analysis.md     # Site structure, capabilities, limitations
│   ├── findings.md              # Current investigation results
│   └── data_samples/            # Example scraped data
├── apis/
│   ├── ebay_research.md         # API capabilities and integration
│   └── findings.md              # Current API investigation results
├── analysis/
│   ├── algorithm_validation.md  # Analysis accuracy and performance
│   └── findings.md              # Current analysis results
├── errors/
│   ├── current_errors.md        # Active error investigation
│   └── error_patterns.md        # Common error types and solutions
└── [other_areas]/
    └── findings.md              # Area-specific investigation results
```

**ERROR LOGGING STRUCTURE**:
```
logs/
├── errors/
│   ├── error_YYYYMMDD_HHMMSS.log  # Individual error logs with full context
│   ├── error_summary.json         # Machine-readable error tracking
│   └── daily_YYYYMMDD.log         # Daily error aggregation
└── debug/
    └── [component]_debug.log      # Component-specific debug logs
```

**CRITICAL**: 
- Evidence files must contain current phase work (archive completed phases)
- Raw execution logs and outputs required for all claims
- No success declarations without demonstrable proof from validation
- Archive completed phases to avoid chronological confusion
- All evidence must include: exact steps taken, complete outputs, analysis of results, implications for project goals

---

## New Issue Discovery and Integration Protocol

### Adding Newly Discovered Issues
When implementation reveals new problems or requirements:

1. **Assess Scope and Priority**
   - Determine if issue blocks current task or can be deferred
   - Assign priority: P0 (blocker), P1 (critical), P2 (important), P3 (nice-to-have)

2. **Update phases.md**
   - Find appropriate phase or create new phase section
   - Add task with clear description, priority, and acceptance criteria
   - Reference detailed implementation approach in relevant phase file

3. **Update Phase Files**
   - Add detailed investigation/implementation plans to relevant phase file
   - Include technical patterns, debugging approaches, and code examples
   - Ensure phase file is self-contained for implementation

4. **Integration Check**
   - Verify new task integrates logically with existing phase structure
   - Update task dependencies and sequencing as needed
   - Ensure phase files contain all technical context needed

### Phase File Maintenance
- **Technical Patterns**: Include working code examples and exact file paths
- **Investigation Approaches**: Document proven research and analysis methods
- **Implementation Steps**: Step-by-step instructions with commands and expected outputs
- **Dependencies**: Clear prerequisites and integration points
- **STATUS NEUTRALITY**: Phase files contain implementation details ONLY - no status claims, completion estimates, or "ACTIVE"/"BLOCKED" declarations
- **IMPLEMENTATION FOCUS**: Phase files describe HOW to implement, not WHEN or WHETHER it's been done

## Success Criteria for Plan Update
- [ ] CLAUDE.md contains only current phase tasks with detailed implementation instructions
- [ ] phases.md status accurately reflects completed vs pending work  
- [ ] All resolved tasks marked as ✅ COMPLETE with evidence file references
- [ ] No contradictory status claims between CLAUDE.md and phases.md
- [ ] New LLM can execute next steps using only CLAUDE.md + referenced files
- [ ] All outdated/resolved information removed from active sections
- [ ] Evidence files properly organized in investigations/ directories
- [ ] Phase files contain complete technical context for their tasks
- [ ] New issues properly integrated into phases.md with phase file details
- [ ] **STATUS CENTRALIZATION**: Only phases.md contains status information - phase files are status-neutral
- [ ] **VALIDATION SETUP**: Appropriate validation approach documented for current phase
- [ ] **EVIDENCE VISIBILITY**: Clear instructions for finding and analyzing previous investigation results
- [ ] **PERSISTENT DOCUMENTATION**: All research and validation commands save output to appropriate directories
- [ ] **ERROR TRACKING SECTION**: CLAUDE.md includes prominent Active Errors section with current status
- [ ] **ERROR INJECTION READY**: All code implements fail-fast error handling with automatic CLAUDE.md updates
- [ ] **NO SILENT FAILURES**: Every function logs errors to structured error files
- [ ] **ERROR CONTEXT**: All errors include file path, function name, full traceback, and impact assessment
- [ ] **TOOLS & TESTS SECTION**: CLAUDE.md includes curated tools/tests using attention economics
- [ ] **ATTENTION BUDGET**: Only high-value tools referenced where recreate cost >> reference cost
- [ ] **PHASE STATUS INTEGRATION**: CLAUDE.md draws status from phases.md and plans from phase files
- [ ] **IMMEDIATE PLANS**: Clear next steps copied from relevant phase file implementation details

## Conflict Resolution Protocol
**When CLAUDE.md and phases.md contradict each other:**
1. Check investigation files for actual proof of completion
2. If evidence exists: Update the plan that's wrong
3. If no evidence: Mark as uncertain and require investigation

**When investigation files contradict claims:**
1. Trust the investigation files over status claims
2. Update both CLAUDE.md and phases.md to match evidence
3. If evidence is incomplete: Mark status as "NEEDS VERIFICATION"

**When multiple investigation files contradict:**
1. Use the most recent evidence with actual execution logs/outputs
2. Archive contradictory older evidence
3. Document the contradiction resolution in current findings

## Evidence Management Workflow
**Archive when:**
- Phase is completely finished and verified working
- All tasks in that phase marked ✅ COMPLETE in phases.md
- No ongoing work references that evidence

**Keep active when:**
- Phase is active or has pending tasks
- Evidence is referenced by current CLAUDE.md instructions
- Investigation is ongoing

**Archiving Process:**
1. Verify phase completion with end-to-end validation
2. Update phases.md to mark phase as ✅ COMPLETE
3. Archive evidence: create `investigations/[area]/archive_YYYYMMDD/` and move completed files
4. Update CLAUDE.md to reference current phase evidence

## Validation Checklist
**Before completing plan update, verify:**

### Cross-Reference Consistency
- [ ] All ✅ COMPLETE items in phases.md have corresponding evidence in investigations/
- [ ] CLAUDE.md next actions match phases.md current priorities  
- [ ] No "achieved" claims without supporting evidence
- [ ] File paths in CLAUDE.md actually exist and are current

### Completeness Check
- [ ] CLAUDE.md has detailed next steps for current blocking issues
- [ ] All mandatory sections present (Development Philosophy, Success Validation, Project Structure, Implementation Roadmap Integration)
- [ ] Comprehensive validation plan included with phase-appropriate requirements
- [ ] Evidence structure matches actual file organization in investigations/
- [ ] Validation workflow includes appropriate testing for current phase
- [ ] All commands specified with expected evidence collection
- [ ] Implementation roadmap workflow properly referenced and followed
- [ ] Phase files contain complete technical context for current tasks

### New LLM Test
- [ ] CLAUDE.md + referenced files contain everything needed for next steps
- [ ] No references to external context or previous conversations
- [ ] All file paths work and point to current information

## Issue Integration Template

### When Adding New Discovered Issues to phases.md
Use this standardized format for consistency:
```markdown
#### [Priority] [Task Name] ([Phase])
**Root Cause**: [Brief description of underlying issue]
**Issue Details**:
- [Specific problem description]
- [Impact on system functionality]
**Impact**: [Effect on project progress]
**Priority**: [P0-P3] - [Justification]
**Implementation Guide**: See [phase_file.md](phase_file.md) for detailed steps
```