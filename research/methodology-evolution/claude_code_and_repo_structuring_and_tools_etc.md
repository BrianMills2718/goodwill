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

### 3. Directory Structure & Organization
```
/
├── CLAUDE.md                    # Current implementation plan (auto-updated)
├── claude_code_and_repo_structuring_and_tools_etc.md  # This file - architectural decisions
├── src/                         # Main codebase
│   ├── scrapers/               # Goodwill scraping components
│   ├── analysis/               # Price analysis and ML components
│   └── apis/                   # eBay API integration
├── docs/                       # Permanent documentation
│   ├── behavior/               # System requirements and goals
│   ├── architecture/           # Technical design documents
│   └── development_roadmap/    # Phase planning and status tracking
├── investigations/             # Technical research and LLM debugging
│   ├── scraping/              # Web scraping technical analysis
│   ├── apis/                  # API integration technical research
│   ├── analysis/              # Algorithm development research
│   └── errors/                # Error pattern analysis and debugging
├── research/                  # Domain knowledge and strategy research
│   ├── markets/               # Market analysis, pricing trends, demand data
│   ├── strategies/            # Business strategy research, arbitrage approaches
│   └── competitors/           # Competitive analysis and benchmarking
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
├── archive/                   # Mirror structure for archival with provenance
│   ├── ARCHIVAL_STRUCTURE.md  # Archive organization documentation
│   ├── [mirror of all directories] # Same structure as main codebase
│   └── [each dir has ARCHIVAL_REASON.md] # Archival decision records
└── .claude/                   # Claude Code configuration
    └── commands/              # Custom slash commands
        └── phase/             # Phase management commands
```

### 4. Directory Purpose & Generalizability
**Decision**: Distinguish between technical investigation and domain research

**Investigations vs Research**:
- **`investigations/`**: Technical research for implementation (LLM debugging, tool building, API analysis)
  - Used heavily by Claude Code for documenting technical discoveries
  - Focus: "How do I build this?" and "Why isn't this working?"
  - Examples: API endpoint discovery, scraping technique analysis, error debugging
  
- **`research/`**: Domain knowledge and business strategy research  
  - Focus: "What should I build?" and "Why does this matter?"
  - Examples: Market analysis, competitive research, business requirements

**Data vs Output**:
- **`data/`**: Input data pipeline (raw → processed)
  - `raw/`: Unprocessed data from external sources
  - `processed/`: Cleaned, enriched, analysis-ready data
  
- **`output/`**: Generated deliverables for human consumption
  - Project-specific subdirectories (suggestions/, reports/, analytics/)

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
- **Dated file naming**: Archived files prefixed with YYYYMMDD_ (e.g., `20250920_old_scraper.py`)
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
- **Area-specific directories** (scraping, apis, analysis, errors)
- **findings.md files** for current investigation results
- **Archive system** for completed phases to avoid chronological confusion
- **Raw execution logs** and outputs preserved for all validation claims

**Integration with Phases**:
- **No success declarations** without evidence files
- **Phase completion** requires end-to-end validation with documented proof
- **Evidence references** in phases.md for all completed tasks

### 12. Custom Commands Strategy
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

### 15. File Organization Discipline
**Strict Rules**:
- **NO temp files in root** - use logs/temp/ or /tmp/
- **Clean up investigations** within 48 hours - move to appropriate directories
- **Archive completed work** to prevent confusion with current efforts
- **Document file placement** in CLAUDE.md for all new file types

### 16. Claude Code Optimization
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

## Tools & Tests Curation Strategy

### 17. Testing vs. CLAUDE.md Reference Strategy
**Key Distinction**: Whether to test something vs. whether to reference it in CLAUDE.md are separate decisions

**Testing Strategy** (What should have tests):
- **Critical Infrastructure**: Tools that break the entire workflow if they fail
- **Complex Logic**: Regex parsing, file system operations, data transformations
- **Integration Points**: API interactions, cross-component workflows
- **Business Logic**: Core arbitrage algorithms, profit calculations
- **Error-Prone Code**: File manipulation, external service calls

**CLAUDE.md Reference Strategy** (Attention economics):
- **High-Value References**: Only tools where recreate cost >> reference cost
- **Critical Dependencies**: Tools that break workflows if missing
- **Cross-Phase Usage**: Tools needed throughout project lifecycle
- **Domain-Specific Logic**: Project-specific insights and algorithms

### 18. Attention Economics & Reference Tradeoffs
**Key Principle**: Every reference in CLAUDE.md reduces Claude's attention to other instructions

**High-value CLAUDE.md references** (worth the attention cost):
- **Recreate Cost >> Reference Cost**: Complex tools that would take significant time/context to rebuild vs. brief reference
- **Frequent Cross-Phase Usage**: Tools needed throughout project lifecycle, not just once
- **Critical Path Dependencies**: Tools that other processes rely on, breaking workflows if recreated incorrectly
- **Domain-Specific Logic**: Arbitrage-specific algorithms that embody hard-won insights

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

## Integration Points

### 24. Phase Transitions
**Workflow for completing phases**:
1. **Evidence collection** with end-to-end validation
2. **Update phases.md** to mark tasks complete
3. **Archive investigation files** to avoid future confusion
4. **Update CLAUDE.md** for next phase priorities
5. **Error resolution** before phase completion

### 25. Error Resolution Integration
**When errors block progress**:
1. **Automatic injection** into CLAUDE.md error section
2. **Investigation documentation** in investigations/errors/
3. **Pattern analysis** for recurring issues
4. **Resolution testing** with evidence collection
5. **Knowledge transfer** to prevent future occurrences

## Current Implementation Status

### 26. Built and Tested Infrastructure
**✅ Complete and Operational**:
- Cross-reference validation system with git integration
- Context loading for comprehensive file modification awareness
- Error injection and management with automatic CLAUDE.md updates
- Archive system with provenance tracking
- Comprehensive test suite (39+ test cases)
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

### 27. Scaling Decisions
**As project grows**:
- **Modular logging** strategy can expand to new components
- **Investigation structure** can add new research areas
- **Phase management** can accommodate additional development streams
- **Error tracking** can scale to multiple parallel development efforts

### 28. Team Collaboration
**Multi-developer readiness**:
- **Shared CLAUDE.md** through git with automatic updates
- **Investigation documentation** provides context for team members
- **Error visibility** prevents duplicate debugging efforts
- **Evidence-based development** enables verification of team member work

---

*This document captures architectural decisions as they're made. Update when new structural decisions are finalized.*