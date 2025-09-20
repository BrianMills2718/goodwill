# Claude Code & Repository Structure Decisions

## Project Context
Building an automated arbitrage system for Goodwill to identify profitable opportunities between their online auctions and eBay resale market. Working **for** Goodwill (no legal/TOS concerns).

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

### 3. Directory Structure
```
/
├── CLAUDE.md                    # Current implementation plan (auto-updated)
├── claude_code_and_repo_structuring.md  # This file - architectural decisions
├── src/                         # Main codebase
│   ├── scrapers/               # Goodwill scraping components
│   ├── analysis/               # Price analysis and ML components
│   └── apis/                   # eBay API integration
├── docs/                       # Permanent documentation
│   ├── behavior/               # System requirements and goals
│   ├── architecture/           # Technical design documents
│   └── development_roadmap/    # Phase planning and status tracking
├── investigations/             # Research results and evidence
│   ├── scraping/              # Web scraping research
│   ├── apis/                  # API integration research
│   ├── analysis/              # Algorithm development research
│   └── errors/                # Error pattern analysis
├── tests/                     # All test files
│   ├── unit/                  # Component tests
│   ├── integration/           # API and system integration tests
│   └── e2e/                   # End-to-end workflow tests
├── data/                      # Data pipeline storage
│   ├── raw/                   # Scraped and API data
│   └── processed/             # Cleaned and analyzed data
├── config/                    # Configuration files and settings
├── tools/                     # Utility scripts
├── logs/                      # Structured logging system (see Error Management)
│   ├── errors/                # Error tracking and resolution
│   ├── debug/                 # Component-specific debug logs
│   └── investigation/         # Research session logs
├── output/                    # Generated suggestions and reports
│   └── suggestions/           # Human-approval workflow files
└── .claude/                   # Claude Code configuration
    └── commands/              # Custom slash commands
        └── phase/             # Phase management commands
```

## Claude Code Workflow Integration

### 4. Error Management System
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

**CLAUDE.md Integration**:
- **Prominent error section** always visible to new Claude sessions
- **Concise entries** with log file references, not full tracebacks
- **Clear action items** for investigation and resolution
- **Removal workflow** to prevent error accumulation

### 5. Evidence-Based Development
**Decision**: All claims require documented proof in `investigations/`

**Evidence Structure**:
- **Area-specific directories** (scraping, apis, analysis, errors)
- **findings.md files** for current investigation results
- **Archive system** for completed phases to avoid chronological confusion
- **Raw execution logs** and outputs preserved for all validation claims

**Integration with Phases**:
- **No success declarations** without evidence files
- **Phase completion** requires end-to-end validation with documented proof
- **Evidence references** in phases.md for all completed tasks

### 6. Custom Commands Strategy
**Decision**: Phase-agnostic commands that work throughout project lifecycle

**Key Command**: `/phase:update_plans`
- **Syncs documentation** between CLAUDE.md, phases.md, and phase files
- **Enforces status centralization** (only phases.md tracks completion)
- **Maintains self-contained CLAUDE.md** for new Claude sessions
- **Integrates error tracking** and evidence requirements

**Command Philosophy**:
- **Works at all phases** - not specific to scraping, analysis, or automation
- **Evidence-based updates** - requires proof before marking tasks complete
- **New LLM ready** - updated CLAUDE.md contains everything needed for next steps

### 7. Investigation Workflow
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

### 8. Status Management Rules
**CRITICAL RULE**: Status information lives ONLY in `phases.md`
- **Phase files**: Implementation details, technical patterns, code examples (status-neutral)
- **CLAUDE.md**: Current tasks with status from phases.md + details from phase files
- **Evidence files**: Proof of completion, not status claims
- **No contradictory status** across multiple files

### 9. File Organization Discipline
**Strict Rules**:
- **NO temp files in root** - use logs/temp/ or /tmp/
- **Clean up investigations** within 48 hours - move to appropriate directories
- **Archive completed work** to prevent confusion with current efforts
- **Document file placement** in CLAUDE.md for all new file types

### 10. Claude Code Optimization
**Leverage Claude Code Features**:
- **Subagents for complex research** (Goodwill analysis, eBay API investigation)
- **Multi-Claude workflows** for parallel development streams
- **Custom slash commands** for repeated workflows
- **"Think harder" mode** for complex architectural decisions
- **Testing workflows** with iterative improvement cycles

**Session Management**:
- **Self-contained CLAUDE.md** - new sessions need no external context
- **Clear next steps** always documented
- **Error visibility** immediate for any new Claude session
- **Evidence references** for understanding previous work

## Integration Points

### 11. Phase Transitions
**Workflow for completing phases**:
1. **Evidence collection** with end-to-end validation
2. **Update phases.md** to mark tasks complete
3. **Archive investigation files** to avoid future confusion
4. **Update CLAUDE.md** for next phase priorities
5. **Error resolution** before phase completion

### 12. Error Resolution Integration
**When errors block progress**:
1. **Automatic injection** into CLAUDE.md error section
2. **Investigation documentation** in investigations/errors/
3. **Pattern analysis** for recurring issues
4. **Resolution testing** with evidence collection
5. **Knowledge transfer** to prevent future occurrences

## Future Considerations

### 13. Scaling Decisions
**As project grows**:
- **Modular logging** strategy can expand to new components
- **Investigation structure** can add new research areas
- **Phase management** can accommodate additional development streams
- **Error tracking** can scale to multiple parallel development efforts

### 14. Team Collaboration
**Multi-developer readiness**:
- **Shared CLAUDE.md** through git with automatic updates
- **Investigation documentation** provides context for team members
- **Error visibility** prevents duplicate debugging efforts
- **Evidence-based development** enables verification of team member work

## Tools & Tests Curation Strategy

### 15. CLAUDE.md Context Management
**Decision**: Parsimonious tool/test references in CLAUDE.md

**Inclusion Criteria** (tools/tests worth permanent context tokens):
- **High complexity to recreate** - Complex setup, intricate logic, domain-specific knowledge
- **Frequently used across phases** - Core validation, debugging, or analysis tools
- **Project-specific patterns** - Unique to arbitrage workflow, not generic utilities
- **Integration dependencies** - Required for other tools to function properly

**Exclusion Criteria** (delete after use):
- **Simple one-off scripts** - Basic data parsing, simple API calls
- **Generic test patterns** - Standard unit tests, basic validation
- **Debugging utilities** - Temporary investigation scripts
- **Easily recreatable** - Tools that Claude can rebuild quickly from scratch

### 16. Tool Categories for CLAUDE.md

**ALWAYS Document These**:
```markdown
## Essential Tools & Tests (Permanent Context)

### Core Validation Tools
- `tools/validate_scraping.py` - Multi-site scraping health check with rate limit detection
- `tools/profit_calculator.py` - Comprehensive margin analysis including all fees and costs

### Integration Test Suite
- `tests/integration/end_to_end_workflow.py` - Complete pipeline validation (scrape → analyze → suggest)
- `tests/integration/api_connectivity.py` - eBay API health and data quality validation

### Project-Specific Utilities
- `tools/keyword_optimizer.py` - ML-based keyword effectiveness analysis
- `tools/error_injector.py` - Automatic CLAUDE.md error section updates
```

**NEVER Document These** (Claude recreates as needed):
- Simple data parsing scripts
- Basic API test calls
- One-time debugging utilities
- Generic unit tests for individual functions
- Temporary investigation helpers

### 17. Curation Workflow
**When creating new tools/tests**:
1. **Create and use** the tool/test for immediate need
2. **Evaluate permanence** using inclusion criteria
3. **Document in CLAUDE.md** if meets criteria, otherwise delete
4. **Archive significant one-offs** in investigations/ with creation context

**Regular cleanup process**:
- Monthly review of tools/ and tests/ directories
- Remove tools not referenced in CLAUDE.md
- Update CLAUDE.md references if tool complexity changes
- Archive deleted tools documentation in investigations/archived_tools/

### 18. Attention Economics & Reference Tradeoffs
**Key Principle**: Every reference in CLAUDE.md reduces Claude's attention to other instructions

**High-value references** (worth the attention cost):
- **Recreate Cost >> Reference Cost**: Complex tools that would take significant time/context to rebuild vs. brief reference
- **Frequent Cross-Phase Usage**: Tools needed throughout project lifecycle, not just once
- **Critical Path Dependencies**: Tools that other processes rely on, breaking workflows if recreated incorrectly
- **Domain-Specific Logic**: Arbitrage-specific algorithms that embody hard-won insights

**Low-value references** (delete rather than reference):
- **Recreate Cost < Reference Cost**: Simple utilities where describing them takes more tokens than rebuilding
- **One-Time Usage**: Tools unlikely to be needed again or in different contexts
- **Generic Patterns**: Standard approaches Claude already knows well
- **Easy Substitution**: Tools with many equivalent alternatives

**Attention Budget Tradeoffs**:
- **Tool complexity vs reference brevity**: Complex tools justify longer descriptions, simple tools don't justify any reference
- **Usage frequency vs context pollution**: Frequently-used tools earn their permanent place, rarely-used tools pollute context
- **Uniqueness vs standard patterns**: Project-specific insights deserve attention, generic code patterns don't
- **Dependency criticality vs standalone value**: Tools that break workflows if missing justify references, nice-to-haves don't

## Cross-Reference System & Context Loading

### 19. File Cross-Reference Architecture
**Decision**: Comprehensive traceability chain across all documentation and code

**Traceability Flow**:
```
Behavior Docs ↔ Architecture Docs ↔ Phase Plans ↔ Python Files
```

**Cross-Reference Patterns**:
- **Python Files**: Include TRACEABILITY comments linking to phase plans, architecture, behavior docs
- **Phase Plans**: Reference implementation files and related documentation  
- **Architecture Docs**: Link to phase plans and behavior requirements
- **Behavior Docs**: Reference architecture implementations and current phases

**Non-Code Files**: Use companion `.ref` files for JSON, config files, etc.

### 20. Context Loading System
**Decision**: Automatic context loading tool for comprehensive file modification awareness

**Core Tool**: `tools/load_context.py`
- **Input**: Any project file path
- **Output**: Complete context including all cross-references and full text of related files
- **Usage**: MANDATORY before modifying any file

**Context Loading Includes**:
- All behavior docs that reference the target file
- All architecture docs that reference the target file
- All phase plans that reference the target file
- All Python files with dependencies (imports, imported by)
- Full text content of ALL referenced files
- Planning dependencies vs runtime dependencies

**Dependency Types**:
- **Planning Dependencies**: Development order requirements (Phase 1 → Phase 2)
- **Runtime Dependencies**: Import/execution relationships (profit_analyzer.py imports goodwill_scraper.py)
- **Configuration Dependencies**: Config files used by code files

### 21. Automated Reference Validation
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

### 22. Context Loading Usage Pattern
**Mandatory Workflow for File Modifications**:

```bash
# Step 1: Load complete context before any modification
python tools/load_context.py src/scrapers/goodwill_scraper.py > context_goodwill_scraper.txt

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

**Context Output Structure**:
```
=== FULL CONTEXT FOR: [target_file] ===

CROSS-REFERENCES:
- Behavior: [list of behavior docs with sections]
- Architecture: [list of architecture docs with sections]
- Phase Plans: [list of phase plans with sections]
- Related Files: [list of related Python files]

DEPENDENCIES:
- Planning: [what this blocks, what blocks this]
- Runtime: [imports, imported by, config files]
- Testing: [test files that cover this file]

=== FULL TEXT OF ALL REFERENCED FILES ===
[Complete content of all cross-referenced files]
```

### 23. Reference Templates for Reusable Patterns

**Python File Cross-Reference Template**:
```python
"""
[filename].py

TRACEABILITY:
- Phase Plan: /docs/development_roadmap/[phase_file].md (Section X.Y)
- Architecture: /docs/architecture/[arch_file].md ([Component Name])
- Behavior: /docs/behavior/[behavior_file].md ([Requirement Section])

CROSS-REFERENCES:
- Related Files: [list of related Python files]
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

---

*This document captures architectural decisions as they're made. Update when new structural decisions are finalized.*