# Architecture Decision Records (ADRs) - Autonomous TDD System

## Purpose
These records capture the fundamental architectural decisions for implementing the autonomous TDD system based on the behaviors defined in `behavior_decisions.md`.

---

## ADR-001: Hook-Based System Architecture

**Decision**: Use **Hook-Only architecture** integrating with Claude Code's existing hook system for autonomous TDD functionality.

**Implementation Approach**:
- **Primary Hook**: Stop hook triggers autonomous analysis and instruction generation
- **All Logic in Hook**: Planning, analysis, testing, and decision-making happens within hook execution
- **Instruction Generation**: Hook analyzes current state and generates next instruction for Claude Code
- **Iterative Control**: Each hook execution provides one focused task, building autonomous session through iterations

**Architecture Flow**:
```
User triggers Stop hook (Escape key)
    ↓
Hook analyzes: project state, test results, current phase, evidence
    ↓
Hook decides: next task based on autonomous TDD methodology
    ↓
Hook generates: specific instruction for Claude Code to execute
    ↓
Claude Code executes instruction → User triggers hook again → Repeat
```

**Rationale**:
- **Native Integration**: Works exactly as Claude Code hooks are designed
- **Simplicity**: No separate processes, coordination, or complex communication
- **Direct Control**: Hook can directly analyze code, run tests, and make decisions
- **Familiar Pattern**: Consistent with existing Claude Code workflow and user habits
- **Easy Deployment**: Single Python file, no additional infrastructure

**Benefits**:
- Seamless user experience within existing Claude Code environment
- Simple installation and configuration
- Direct access to all Claude Code tools and capabilities
- Easy debugging and development
- Stateless operation (no persistent processes)

**Trade-offs Accepted**:
- Each autonomous step requires user trigger (Escape key press)
- Cannot run completely unattended (requires periodic user interaction)
- Hook execution time limits may constrain complex analysis

**Cross-References**: Links to hook implementation patterns, Claude Code integration guides

---

---

## ADR-002: Hybrid File System for Context Management and Cross-References

**Decision**: Use a **Hybrid File System** combining metadata files and embedded comments for context management and cross-reference relationships.

**Implementation Approach**:
- **Metadata Files**: `.claude/cross_references.json` for programmatic relationship storage and fast querying
- **Embedded Comments**: Special comments in source files using format `# RELATES_TO: file1, file2, file3`
- **Hook Discovery**: Hook scans both metadata and embedded references to build context
- **Smart Loading**: Hook uses relationships to load relevant context for current task

**File Structure Example**:
```
docs/behavior/user_authentication.md
# RELATES_TO: docs/architecture/auth_system.md, tests/test_auth.py, src/auth/

.claude/cross_references.json:
{
  "docs/behavior/user_authentication.md": {
    "architecture": ["docs/architecture/auth_system.md"],
    "tests": ["tests/test_auth.py"], 
    "implementation": ["src/auth/"],
    "dependencies": ["docs/behavior/session_management.md"]
  }
}
```

**Context Loading Strategy**:
1. **Current Task Analysis**: Hook identifies files relevant to current task
2. **Relationship Discovery**: Scan embedded comments and metadata for related files
3. **Smart Selection**: Use LLM intelligence to choose most relevant context to load
4. **Context Assembly**: Load selected files into hook context for analysis

**Rationale**:
- **Human Readable**: Developers can see relationships directly in source files
- **Machine Readable**: JSON provides fast programmatic access for hook automation
- **Redundant Safety**: If one system fails, the other provides backup relationships
- **LLM Friendly**: Comments provide context, JSON provides structured data
- **Stateless Compatible**: No persistent cross-session storage required
- **Hook Efficient**: Fast discovery and loading within hook execution time limits

**Benefits**:
- Bidirectional relationship visibility for both humans and automation
- Fast context loading for autonomous decision-making
- Self-documenting codebase with clear file relationships
- Flexible relationship types (architecture, tests, implementation, dependencies)
- Works across any programming language or project structure

**Pre-Creation Strategy**:
- **Complete File Structure Generation**: During planning phase, generate all required files (empty with headers/cross-references)
- **Upfront Cross-Reference Establishment**: All relationships defined before any implementation begins
- **Implementation as Fill-In**: Autonomous implementation phase simply fills in pre-created file structure
- **Complete Context Availability**: Hook always has full project context from the start

**Auto-Maintenance Requirements**:
- **Autonomous Cross-Reference Creation**: System automatically generates all cross-references during planning
- **Relationship Validation**: Hook validates and maintains consistency between embedded comments and metadata
- **Structure Updates**: System can modify file structure and relationships if planning changes

**Trade-offs Accepted**:
- **Upfront Planning Overhead**: Requires complete architectural analysis before implementation
- **Potential Over-Creation**: May generate files that prove unnecessary during implementation
- **Less Emergent Design**: Reduced flexibility for architecture changes during coding

**Cross-References**: Links to smart loading implementation, relationship maintenance tools, hook context management

---

---

## ADR-003: LLM-Driven Task Decomposition and Orchestration

**Decision**: Use **pure LLM-driven decomposition** for breaking down problems and orchestrating autonomous execution, leveraging Claude Code's intelligence rather than predefined templates.

**⚠️ OUTDATED - SUPERSEDED BY ITERATIVE METHODOLOGY**

This linear methodology has been replaced by the iterative methodology with LLM-driven stabilization documented in `docs/architecture/iterative_methodology_stabilization.md`.

**Original Flow** (for historical reference):
```
1. Overview → 
2. Architecture + Dependency Research → 
3. TENTATIVE FILE STRUCTURE CREATION →
4. PSEUDOCODE/LOGIC DOCUMENTATION → 
5. Implementation Plans + Unit Tests →
6. Integration Tests (informed by pseudocode) →
7. Acceptance Tests (realistic based on implementation possibilities) →
8. CREATE ALL FILES & CROSS-REFERENCES → 
9. Implementation (Fill-in pre-created structure)
```

**Current Methodology**: See `docs/architecture/iterative_methodology_stabilization.md` for the complete iterative approach with problem tracking and stabilization criteria.

**LLM-Driven Decomposition Process**:
1. **Requirements Analysis**: LLM analyzes project overview and behavior specifications
2. **Intelligent Structure Generation**: LLM creates project-specific file structure based on requirements (no templates)
3. **Test Strategy Creation**: LLM generates appropriate acceptance, integration, and unit tests for each layer
4. **Implementation Planning**: LLM creates detailed implementation plans for each component
5. **Cross-Reference Establishment**: LLM identifies and creates all file relationships
6. **Dependency Graph Construction**: LLM determines execution order based on dependencies

**Example Decomposition**:
```
Input: "Build a REST API with user authentication"
LLM Analysis → Custom structure:
├── docs/behavior/user_auth_requirements.md
├── docs/architecture/api_design.md
├── tests/acceptance/test_auth_flow.py
├── tests/integration/test_database.py
├── tests/unit/test_password_hashing.py
├── src/auth/oauth_handler.py
├── src/models/user.py
├── implementation_plans/auth_implementation.md
└── .claude/cross_references.json
```

**Dependency Graph Execution**:
```
Database Models → Database Connection → API Routes → Endpoint Tests
     ↓                    ↓                ↓            ↓
  (Ready)            (Blocked)         (Blocked)    (Blocked)

Hook selects next ready task: "Implement User model in src/models/user.py"
After completion, dependency graph updates automatically
```

**Hook Orchestration Logic**:
1. **Analyze Current State**: What files exist, what's implemented, what tests pass
2. **Check Dependency Graph**: Which tasks are ready (dependencies completed)
3. **Select Next Task**: Pick highest priority ready task that fits context window
4. **Load Context**: Load relevant files based on cross-references
5. **Generate Instruction**: Create specific implementation instruction for Claude Code

**Rationale**:
- **Leverages LLM Intelligence**: Uses Claude Code's natural ability to understand requirements and create appropriate structures
- **No Template Limitations**: Can handle any project type without predefined constraints
- **Project-Specific Optimization**: Structure tailored to actual requirements, not generic patterns
- **Complete Context Availability**: All files and relationships created upfront for perfect context loading
- **Autonomous Progression**: Dependency graph ensures logical implementation order

**Benefits**:
- Intelligent adaptation to any project type or complexity
- No maintenance of template libraries or pattern definitions
- Complete project visibility from the start of implementation
- Natural progression through logical dependency order
- Perfect context loading (all related files always available)

**Trade-offs Accepted**:
- **LLM Dependency**: Success depends on LLM's ability to understand requirements and create good structures
- **Upfront Analysis Time**: Requires comprehensive analysis before any implementation begins
- **Potential Over-Analysis**: May create more complex structures than necessary

**Cross-References**: Links to dependency graph algorithms, LLM prompt engineering for decomposition, hook orchestration patterns

---

---

## ADR-004: LLM-Driven Error Analysis and Self-Correction

**Decision**: Use **LLM-driven error analysis and correction** with minimal programmatic scaffolding, leveraging Claude Code's intelligence rather than complex retry frameworks.

**Simple Architecture**:
1. **Basic Counters**: Track failure attempts to prevent infinite loops
2. **LLM Analysis**: LLM analyzes all errors and decides corrective action
3. **Clear Escalation**: LLM recognizes when human intervention is required
4. **Configurable Limits**: Simple attempt limits before escalation

**Error Handling Flow**:
```
Error Occurs → LLM analyzes error context → LLM decides action:
├── Fix Implementation Logic (code changes)
├── Fix Test Issues (test corrections) 
├── Refactor Approach (architectural changes)
├── Install Dependency (missing packages)
├── Try New Strategy (different implementation)
├── Clarify Requirements (ambiguous specifications)
└── Escalate to Human (missing credentials, fundamental blockers)
```

**Configuration Example**:
```json
{
  "max_failure_attempts": 5,
  "escalation_triggers": [
    "missing_api_keys", 
    "missing_credentials", 
    "external_service_unavailable"
  ],
  "stop_on_repeated_identical_failures": 3
}
```

**LLM Decision Logic**:
- **Error Analysis**: "What type of error is this? What's the likely cause?"
- **Solution Assessment**: "Can this be fixed with code changes, or does it need human input?"
- **Action Selection**: "What's the best approach to resolve this specific error?"
- **Escalation Decision**: "Is this a blocking issue that requires user intervention?"

**Escalation Criteria** (LLM recognizes these patterns):
- **Missing External Dependencies**: API keys, credentials, external services
- **Fundamental Requirement Ambiguity**: Business logic unclear, conflicting specifications
- **Repeated Identical Failures**: Same error occurring multiple times despite fixes
- **Resource Constraints**: Insufficient permissions, network access, etc.

**Rationale**:
- **Leverages LLM Intelligence**: Uses Claude Code's natural problem-solving abilities
- **Adaptive Response**: Can handle novel error types without predefined rules
- **Context-Aware**: Considers project context, implementation phase, and error history
- **Simple Implementation**: Minimal scaffolding, maximum intelligence
- **Clear Blocking**: Recognizes genuine human-required intervention vs solvable problems

**Benefits**:
- Intelligent error analysis and solution selection
- Handles unexpected error types without predetermined rules
- Natural escalation when human input genuinely needed
- Simple configuration and maintenance
- Adapts to different project types and error patterns

**Trade-offs Accepted**:
- **LLM Dependency**: Success depends on LLM's ability to analyze and solve errors correctly
- **Potential Analysis Time**: Each error requires LLM analysis rather than quick programmatic response
- **No Learning**: Cannot improve error handling based on historical patterns (stateless)

**Cross-References**: Links to LLM prompt engineering for error analysis, escalation trigger patterns, hook error handling integration

---

---

## ADR-005: Existing Test Frameworks with Evidence Validation Layer

**Decision**: Use **existing test frameworks** (pytest, jest, rspec, etc.) enhanced with custom evidence collection and validation to prevent fabrication.

**Framework Integration Strategy**:
- **Language-Specific Frameworks**: pytest (Python), jest (JavaScript), rspec (Ruby), go test (Go), etc.
- **Evidence Collection Layer**: Custom hook integration that captures and validates test results
- **Anti-Fabrication Validation**: Automated detection of mocking, mock data, and fake external interactions
- **Real Dependency Enforcement**: Validation that tests actually interact with real external services

**Layered Test Implementation**:
```
Phase 2 (Behavior): Create acceptance tests using existing frameworks
Phase 3 (Architecture): Create integration tests with real external dependencies  
Phase 4 (Implementation): Create unit tests during TDD implementation
```

**Evidence Collection Process**:
```
Hook triggers test execution:
├── pytest tests/acceptance/ --json-report=evidence/acceptance_results.json
├── pytest tests/integration/ --json-report=evidence/integration_results.json  
└── pytest tests/unit/ --json-report=evidence/unit_results.json

Hook analyzes results:
├── Parse JSON output for pass/fail status
├── Scan test code for mock/stub usage (anti-fabrication)
├── Validate external service interactions (real vs fake)
├── Generate evidence report with concrete proof
└── Update dependency graph based on test completion
```

**Anti-Fabrication Validation**:
1. **Mock Detection**: Scan test files for mocking libraries (unittest.mock, jest.mock, etc.)
2. **External Service Validation**: Verify tests make real API calls, database connections
3. **Data Validation**: Ensure test data comes from real sources, not hardcoded mock responses
4. **Network Activity Monitoring**: Confirm actual network requests during integration tests

**Example Evidence Structure**:
```json
{
  "test_type": "integration",
  "framework": "pytest", 
  "timestamp": "2024-01-15T10:30:00Z",
  "results": {
    "total_tests": 12,
    "passed": 11,
    "failed": 1,
    "exit_code": 1
  },
  "anti_fabrication_checks": {
    "mock_usage_detected": false,
    "real_external_calls": true,
    "network_activity_confirmed": true,
    "fake_data_patterns": false
  },
  "evidence_quality": "high",
  "blocking_issues": ["test_payment_integration failed - API key invalid"]
}
```

**Language-Specific Integration**:
- **Python**: pytest with custom hooks and JSON reporting
- **JavaScript**: jest with custom reporters and coverage tools
- **Ruby**: rspec with custom formatters
- **Go**: go test with JSON output parsing
- **Others**: LLM intelligently adapts to project-specific test frameworks

**Hook Integration Logic**:
1. **Detect Project Type**: Analyze codebase to determine language and existing test framework
2. **Run Appropriate Tests**: Execute tests using native framework with evidence collection
3. **Validate Results**: Apply anti-fabrication checks and evidence quality assessment
4. **Update Progress**: Mark tasks complete only with high-quality evidence
5. **Block on Issues**: Clear escalation when tests fail due to missing dependencies

**Rationale**:
- **Leverages Existing Ecosystem**: Uses mature, well-tested frameworks developers already know
- **LLM Compatibility**: Claude Code already understands how to write tests for standard frameworks
- **Universal Application**: Works across any programming language or project type
- **Evidence Focus**: Adds fabrication prevention without rebuilding test infrastructure
- **Developer Familiarity**: No learning curve for new testing tools or patterns

**Benefits**:
- Immediate compatibility with existing projects and developer workflows
- Robust test execution using proven frameworks
- Strong anti-fabrication validation prevents mock data success claims
- Clear evidence generation for autonomous progress tracking
- Language-agnostic approach supports universal system goals

**Trade-offs Accepted**:
- **Framework Dependency**: Relies on external test frameworks rather than custom solution
- **Multiple Framework Support**: Must handle different frameworks across languages
- **Evidence Layer Complexity**: Adding validation layer increases system complexity

**Cross-References**: Links to anti-fabrication detection algorithms, test framework integration patterns, evidence validation schemas

---

---

## ADR-006: Architecture Phase External Dependency Research and Documentation

**Decision**: **Determine and document all external dependencies during the Architecture Phase** before any code is written, using internet research and MCP tools to gather comprehensive integration documentation.

**⚠️ OUTDATED - SUPERSEDED BY ITERATIVE METHODOLOGY**

This methodology reference has been replaced. See `docs/architecture/iterative_methodology_stabilization.md` for the current 8-phase iterative approach.

**Original Integration** (for historical reference):
```
1. Overview → 
2. Behavior + Acceptance Tests → 
3. Architecture + Integration Tests + EXTERNAL DEPENDENCY ANALYSIS → 
4. Implementation Plans + Unit Tests →
5. CREATE ALL FILES & CROSS-REFERENCES → 
6. Implementation (Fill-in pre-created structure)
```

**Architecture Phase Dependency Process**:
1. **Requirements Analysis**: LLM analyzes behavior specifications to identify needed external services
2. **Service Research**: Use WebSearch and Context7 MCP to gather comprehensive API documentation
3. **Integration Documentation**: Create detailed dependency specifications with authentication, usage patterns, and examples
4. **Cross-Reference Establishment**: Link dependency docs to relevant implementation files
5. **Availability Validation**: Check service accessibility and document any blockers before implementation
6. **Dependency Manifest Creation**: Generate structured dependency requirements for hook validation

**External Research Tools**:
- **WebSearch**: Find official API documentation, authentication guides, rate limiting info
- **Context7 MCP**: Retrieve up-to-date library documentation and code examples
- **LLM Analysis**: Synthesize research into practical integration specifications

**Documentation Structure**:
```
docs/dependencies/
├── ebay_api_integration.md       # Complete API guide with auth, endpoints, examples
├── stripe_payment_integration.md # Payment processing requirements and patterns
├── database_postgresql.md        # Database setup, connection patterns, schema requirements
└── external_services_summary.md  # Overview of all external dependencies

.claude/dependencies.json:
{
  "external_services": {
    "ebay_api": {
      "type": "rest_api",
      "authentication": "oauth2",
      "required_credentials": ["EBAY_API_KEY", "EBAY_DEV_ID", "EBAY_CERT_ID"],
      "documentation_file": "docs/dependencies/ebay_api_integration.md",
      "validation_endpoint": "https://api.ebay.com/identity/v1/oauth2/token",
      "rate_limits": "5000 calls/day",
      "blocking": true
    }
  }
}
```

**Cross-Reference Integration**:
```
src/payment/stripe_handler.py
# RELATES_TO: docs/dependencies/stripe_payment_integration.md, docs/architecture/payment_design.md

docs/architecture/payment_design.md  
# RELATES_TO: docs/dependencies/stripe_payment_integration.md, src/payment/, tests/integration/test_payments.py
```

**Dependency Research Process**:
1. **Service Identification**: "This project needs payment processing, external APIs, database storage"
2. **Research Execution**: WebSearch for "Stripe API authentication Python" + Context7 for stripe library docs
3. **Documentation Creation**: Synthesize research into practical integration guides with code examples
4. **Validation Planning**: Define how to test each external dependency (real API calls, not mocks)
5. **Blocking Assessment**: Identify credentials, access requirements, potential blockers

**Early Blocking Detection**:
- **Missing Credentials**: Identify required API keys, tokens, certificates during architecture phase
- **Service Limitations**: Document rate limits, access restrictions, cost implications
- **Integration Complexity**: Assess authentication flows, webhook requirements, error handling needs
- **Compatibility Issues**: Check library versions, framework compatibility, system requirements

**Implementation Phase Benefits**:
- **Complete Context**: All dependency information available when writing code
- **No Research Delays**: Implementation proceeds smoothly without mid-task research
- **Proper Error Handling**: Error handling patterns documented before implementation
- **Realistic Planning**: Dependencies inform task breakdown and complexity assessment

**Rationale**:
- **Front-loads Research**: Eliminates dependency discovery during implementation
- **Leverages Research Tools**: Uses WebSearch and Context7 MCP for comprehensive information gathering
- **Prevents Implementation Surprises**: All external requirements known before coding begins
- **Improves Architecture**: Dependency constraints inform architectural decisions
- **Enables Better Planning**: Realistic task estimation with full dependency knowledge

**Benefits**:
- No mid-implementation blocking due to unknown external service requirements
- Comprehensive integration documentation available during coding
- Early identification of missing credentials or access requirements
- Better architectural decisions informed by dependency constraints
- Smoother autonomous implementation with complete context

**Trade-offs Accepted**:
- **Upfront Research Time**: More time spent in architecture phase on dependency research
- **Potential Over-Documentation**: May research dependencies that prove unnecessary
- **Research Tool Dependency**: Success depends on quality of WebSearch and Context7 MCP results

**Cross-References**: Links to WebSearch integration patterns, Context7 MCP usage, dependency validation algorithms, external service integration guides

---

---

## ADR-007: Standardized Directory Structure with LLM-Driven Content Adaptation

**Decision**: Use **standardized directory structure** based on established patterns, with **LLM-driven content adaptation** for project-specific requirements within the standard framework.

**Standardized Directory Structure**:
```
/
├── CLAUDE.md                    # Current implementation plan (auto-updated)
├── project_architecture.md     # This file - architectural decisions  
├── src/                         # Main codebase (LLM adapts subdirectories)
├── docs/                        # Permanent documentation
│   ├── behavior/               # WHAT system should do (requirements, goals)
│   ├── architecture/           # HOW to build system (technical design)
│   ├── dependencies/           # External service integration docs (NEW)
│   └── development_roadmap/    # Current status and phases
├── investigations/             # Technical research and LLM debugging
├── research/                   # Domain knowledge and business strategy
├── tests/                      # All test files
│   ├── acceptance/             # User behavior validation tests
│   ├── integration/            # API and system integration tests  
│   └── unit/                   # Component tests
├── tools/                      # Utility scripts and autonomous workflow tools
│   └── workflow/              # Autonomous TDD system components
├── logs/                       # Structured logging with error injection
├── config/                     # Configuration files and settings
├── .claude/                    # Claude Code configuration
│   ├── cross_references.json  # File relationship metadata
│   ├── dependencies.json      # External dependency manifest
│   └── commands/              # Custom slash commands
└── [project_specific]/        # LLM-determined additional directories
```

**Universal vs Adaptive Components**:

**Universal (Always Present)**:
- **`docs/`**: behavior/, architecture/, dependencies/, development_roadmap/
- **`src/`**: Main codebase (LLM adapts internal structure)
- **`tests/`**: acceptance/, integration/, unit/
- **`tools/`**: Utility scripts and workflow automation
- **`.claude/`**: cross_references.json, dependencies.json
- **`logs/`**: Error injection and debugging logs
- **`config/`**: Configuration management

**LLM-Adaptive (Project-Specific)**:
- **`src/` subdirectories**: LLM determines component organization based on architecture
- **`investigations/`**: Added for research-heavy projects
- **`research/`**: Added for domain analysis projects  
- **`data/`**: Added for data processing projects (raw/, processed/)
- **`output/`**: Added for deliverable generation projects

**LLM Structure Generation Process**:
1. **Analyze Requirements**: LLM reviews behavior and architecture specifications
2. **Apply Base Structure**: Start with universal directory framework
3. **Determine Adaptations**: Add project-specific directories based on needs
4. **Generate src/ Organization**: Create component structure based on architecture
5. **Cross-Reference Integration**: Establish relationships between all directories
6. **Dependency Integration**: Link dependency docs to relevant implementation areas

**Example LLM Adaptations**:

**Web API Project**:
```
src/
├── api/                        # REST endpoint handlers
├── models/                     # Data models and validation
├── services/                   # Business logic services
├── middleware/                 # Authentication, logging, etc.
└── database/                   # Database connection and migrations

docs/dependencies/
├── database_postgresql.md      # Database integration guide
├── auth_service_integration.md # Authentication service docs
└── external_apis_summary.md   # Overview of all external APIs
```

**Data Processing Project**:
```
src/
├── extractors/                 # Data extraction components
├── transformers/               # Data transformation logic
├── loaders/                    # Data loading and persistence
└── pipelines/                  # End-to-end processing workflows

data/                           # Added by LLM for data projects
├── raw/                        # Unprocessed source data
└── processed/                  # Cleaned and analyzed data

docs/dependencies/
├── data_sources_integration.md # External data source APIs
├── storage_systems.md          # Database and file storage
└── processing_libraries.md    # Required data processing libraries
```

**Cross-Reference Integration**:
```
src/api/user_routes.py
# RELATES_TO: docs/behavior/user_management.md, docs/architecture/api_design.md, 
#            docs/dependencies/auth_service_integration.md, tests/integration/test_user_api.py

docs/dependencies/auth_service_integration.md
# RELATES_TO: docs/architecture/security_design.md, src/middleware/auth.py,
#            tests/integration/test_authentication.py, config/auth_config.yaml
```

**Infrastructure Tool Integration**:
- **Cross-Reference Validation**: `tools/validate_references.py` validates all RELATES_TO comments
- **Context Loading**: `tools/load_context.py` loads complete context for any file modification
- **Error Injection**: `tools/inject_error.py` automatically updates CLAUDE.md with structured errors
- **Dependency Validation**: Hook validates external dependencies against `.claude/dependencies.json`

**Rationale**:
- **Consistency**: Standardized structure provides predictable organization across projects
- **Flexibility**: LLM adapts content and specific subdirectories to project needs
- **Tool Integration**: Works with existing cross-reference and error management tools
- **Documentation Standards**: Enforces separation of behavior, architecture, and dependency docs
- **Evidence Collection**: Test structure supports layered testing with evidence validation

**Benefits**:
- Immediate familiarity for developers across different projects
- Consistent cross-reference patterns and tool integration
- Clear separation of concerns in documentation structure
- Automatic dependency research integration during architecture phase
- Built-in error management and debugging support

**Trade-offs Accepted**:
- **Structure Overhead**: May create directories not needed for simple projects
- **Learning Curve**: Developers must understand standardized patterns
- **Tool Dependency**: Relies on specific tools for cross-reference and error management

**Cross-References**: Links to cross-reference validation tools, directory organization patterns, LLM content adaptation strategies

---

---

## ADR-008: Structured Evidence Storage with CLAUDE.md Progress Injection

**Decision**: Use **established structured logging system** with **evidence files** and **automatic CLAUDE.md injection** for progress tracking and validation, leveraging existing infrastructure tools.

**Evidence Storage Strategy**:
```
logs/
├── evidence/                   # Task completion evidence
│   ├── task_[id]_evidence.json # Structured evidence per task
│   ├── session_progress.json   # Overall session progress tracking
│   └── validation_results.json # Anti-fabrication validation results
├── errors/                     # Error tracking (existing system)
│   ├── active/                # Current errors needing attention
│   └── resolved/              # Historical error resolution
└── debug/                     # Component-specific debug logs
```

**Evidence File Structure**:
```json
{
  "task_id": "implement_user_authentication",
  "timestamp": "2024-01-15T10:30:00Z",
  "phase": "implementation",
  "evidence_type": "completion",
  "validation_results": {
    "tests_passed": true,
    "real_dependencies_used": true,
    "no_mock_data_detected": true,
    "external_service_calls_verified": true
  },
  "test_evidence": {
    "acceptance_tests": {"passed": 5, "failed": 0, "exit_code": 0},
    "integration_tests": {"passed": 8, "failed": 1, "exit_code": 1}, 
    "unit_tests": {"passed": 12, "failed": 0, "exit_code": 0}
  },
  "anti_fabrication_checks": {
    "mock_usage_detected": false,
    "hardcoded_responses": false,
    "network_activity_confirmed": true,
    "real_api_calls": true
  },
  "completion_status": "blocked",
  "blocking_reason": "Integration test failed - missing API key for payment service",
  "next_action": "escalate_missing_credentials"
}
```

**CLAUDE.md Progress Injection**:
```markdown
## 🎯 CURRENT AUTONOMOUS PROGRESS

**Session Status**: BLOCKED - Missing external dependencies
**Completed Tasks**: 5/12 (41.7%)
**Current Task**: implement_user_authentication
**Blocking Issue**: Payment service API key required

### Completed ✅
- [x] Database schema design (evidence: logs/evidence/task_001_evidence.json)
- [x] User model implementation (evidence: logs/evidence/task_002_evidence.json)

### In Progress 🔄  
- [ ] User authentication (BLOCKED: missing STRIPE_API_KEY)

### Pending ⏳
- [ ] Payment integration (depends on authentication)
- [ ] Email notifications (depends on user system)
```

**Progress Tracking Integration**:

**Hook Progress Analysis**:
1. **Evidence Collection**: Hook runs tests, captures results in evidence files
2. **Anti-Fabrication Validation**: Verify real dependencies, no mock data usage
3. **Progress Calculation**: Count completed vs total tasks from dependency graph
4. **CLAUDE.md Update**: Inject current progress into context for next iteration
5. **Blocking Detection**: Identify and escalate missing credentials or dependencies

**Evidence Validation Process**:
```
Hook execution:
├── Run appropriate tests (pytest, jest, etc.)
├── Capture results in evidence file
├── Apply anti-fabrication checks
├── Update dependency graph completion status
├── Calculate overall progress percentage
├── Inject progress summary into CLAUDE.md
└── Block execution if credentials missing
```

**Infrastructure Tool Integration**:
- **Evidence Generation**: Extends existing `tools/inject_error.py` pattern for progress injection
- **Structured Logging**: Uses established `logs/` directory structure and JSON format
- **Cross-Reference Updates**: Updates `.claude/cross_references.json` with completion status
- **Dependency Validation**: Validates against `.claude/dependencies.json` manifest

**Stateless Session Evidence**:
- **Session-Only Storage**: Evidence files valid only for current autonomous session
- **No Cross-Session Persistence**: Each session starts fresh (BDR-006 compliance)
- **Session Progress File**: `logs/evidence/session_progress.json` tracks current session only
- **Evidence Cleanup**: Previous session evidence archived or cleaned up

**Anti-Fabrication Evidence Requirements**:
- **Test Execution Proof**: Actual test framework output, not LLM claims
- **External Service Validation**: Network activity logs, API response validation
- **Mock Detection**: Scan code for mocking libraries, flag any usage
- **Real Data Verification**: Confirm data comes from external sources, not hardcoded responses

**Progress Blocking and Escalation**:
```
Evidence shows missing credentials:
├── Create blocking evidence file
├── Inject specific error into CLAUDE.md
├── Provide clear escalation message to user
└── Halt autonomous execution until resolved

Example blocking message:
"BLOCKED: Payment integration requires STRIPE_API_KEY environment variable.
Please set STRIPE_API_KEY and restart autonomous session."
```

**Rationale**:
- **Leverages Existing Infrastructure**: Uses established logging and injection patterns
- **Concrete Evidence**: Provides objective proof of completion, not subjective claims
- **Anti-Fabrication Focus**: Validates real functionality rather than test passage
- **Clear Progress Visibility**: CLAUDE.md injection provides immediate progress context
- **Stateless Compliance**: Works without cross-session persistence requirements

**Benefits**:
- Immediate progress visibility in CLAUDE.md context
- Objective evidence validation prevents false completion claims
- Seamless integration with existing error management and logging systems
- Clear blocking and escalation when human intervention required
- Structured evidence supports autonomous decision-making

**Trade-offs Accepted**:
- **Session-Only Evidence**: Progress tracking resets each session
- **Evidence Storage Overhead**: Structured evidence files consume disk space
- **Validation Complexity**: Anti-fabrication checks add processing time

**Cross-References**: Links to evidence validation algorithms, CLAUDE.md injection patterns, structured logging systems, anti-fabrication detection methods

---

## ADR-009: Autonomous Status Tracking and Progress Management

**Decision**: Implement **structured status tracking system** that enables LLMs to autonomously assess methodology progress and make progression decisions.

**Problem**: 
- LLMs need systematic way to track progress across 8-phase iterative methodology
- Status scattered across multiple files (CLAUDE.md, todo lists, individual components)
- No programmatic way for autonomous systems to assess "where we are" and "what's next"
- Critical for autonomous operation without human guidance

**Solution Components**:

1. **Centralized Status Tracker** (`docs/development_roadmap/methodology_status_tracker.md`)
   - Phase-by-phase completion tracking with evidence
   - Overall progress percentages and blocking conditions
   - Critical path analysis and bottleneck identification

2. **LLM Decision Framework**
   - When to continue current phase vs advance
   - When to escalate/block for human input
   - Automated status assessment function

3. **Evidence-Based Progression**
   - Concrete completion criteria per phase
   - Required evidence files for phase completion
   - No subjective "feels complete" assessments

**Implementation Requirements**:
- Status tracker updated after major milestone completion
- Programmatic status assessment function callable by LLMs
- Clear blocking conditions and escalation triggers
- Integration with existing CLAUDE.md and todo systems

**Benefits**:
- **Autonomous Decision Making**: LLMs can assess progress without human guidance
- **Consistency**: Standardized progression criteria across all phases
- **Visibility**: Clear understanding of current status and next actions
- **Accountability**: Evidence-based completion prevents false progress claims

**Integration Points**:
- CLAUDE.md references status tracker for high-level status
- Todo lists track task-level progress within phases
- Individual components reference completion criteria
- Hook system uses status assessment for autonomous decisions

**Rationale**:
- Essential for autonomous methodology execution
- Prevents getting lost in complex 8-phase iterative process
- Enables systematic progress without human navigation
- Supports evidence-based anti-fabrication principles

**Implementation Integration**:
- Iteration tracking integrated into iterative methodology (docs/architecture/iterative_methodology_stabilization.md)
- CLAUDE.md section provides always-in-context status for LLM sessions
- Supporting documentation provides detailed frameworks and automation support
- Hook system uses iteration status for autonomous progression decisions

**Cross-References**: Links to iterative methodology documentation, hook implementation, evidence validation system

---

## Architecture Decision Records Complete

All 9 Architecture Decision Records have been completed, providing a comprehensive architectural foundation for the autonomous TDD system.

**Summary of Architectural Decisions**:
1. **ADR-001**: Hook-Only System Architecture  
2. **ADR-002**: Hybrid File System for Context Management
3. **ADR-003**: LLM-Driven Task Decomposition and Orchestration
4. **ADR-004**: LLM-Driven Error Analysis and Self-Correction
5. **ADR-005**: Existing Test Frameworks with Evidence Validation
6. **ADR-006**: Architecture Phase External Dependency Research
7. **ADR-007**: Standardized Directory Structure with LLM Content Adaptation
8. **ADR-008**: Structured Evidence Storage with CLAUDE.md Progress Injection
9. **ADR-009**: Autonomous Status Tracking and Progress Management

**Cross-References**:
- Links from: `behavior_decisions.md` (behavior requirements that drove these decisions)
- Links from: `architecture_questions.md` (questions that these decisions resolve)
- Links to: Implementation specifications and detailed design documents