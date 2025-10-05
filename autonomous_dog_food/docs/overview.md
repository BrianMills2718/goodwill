# Autonomous TDD System for Claude Code - Project Overview

## Problem Statement

Claude Code and LLM-based coding systems suffer from critical reliability issues that prevent autonomous software development:

### Core Problems
1. **Fabrication & Overoptimism**: Claims success when implementation is incomplete or broken
2. **Mock Data Masquerading**: Tests pass with fake data while real functionality fails
3. **Silent Failure Patterns**: Errors hidden instead of surfaced, masking real problems
4. **Requirements-Implementation Gap**: Focus on "tests passing" vs "user goals achieved"
5. **Context Window Blindness**: Cannot maintain understanding of entire codebase
6. **Dependency Blindness**: Claims success when external dependencies missing
7. **No Persistent Learning**: Repeats same mistakes across sessions

### Specific Manifestations
- Goodwill scraper "worked" but returned "Test Item 0" instead of real data
- eBay integration "complete" with $1,750.97 "profit" from simulated data
- BeautifulSoup4 dependency errors ignored while claiming success
- Tests passing while core functionality completely broken

## Solution Vision

**Build an Autonomous Test-Driven Development system that:**

1. **Enforces Evidence-Based Development**: No success claims without concrete proof
2. **Prevents Fabrication**: Detects and blocks lazy implementations, mock data, silent failures
3. **Manages Context Intelligently**: Breaks problems into context-window-sized pieces with cross-references
4. **Learns Persistently**: Remembers failures and patterns across sessions
5. **Validates End-to-End**: Ensures complete pipeline works, not just individual components
6. **Handles Dependencies Properly**: Clear blocking when external resources missing

## Core Philosophy

### Two-Process Architecture

The autonomous system operates via **two distinct but interfacing processes**:

#### **Planning Process** (High-Level Design)
- **Input**: Project requirements, user goals, domain constraints
- **Output**: Documentation, locked tests, architecture specifications, implementation plans
- **Methodology**: Iterative stabilization with problem tracking (docs/architecture/iterative_methodology_stabilization.md)
- **Quality Gates**: Consistency validation, evidence requirements, cross-reference completion

#### **Implementation Process** (Code Execution)  
- **Input**: Planning artifacts (locked tests, architecture, requirements)
- **Output**: Working code that satisfies planning specifications
- **Methodology**: V5 Hybrid Intelligence decision tree (hook_mermaid_diagram_full5_hybrid_intelligence.txt)
- **Constraint**: Cannot modify planning artifacts - must make them pass

### Anti-Fabrication Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code
- **FAIL-FAST AND LOUD**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require structured evidence
- **NO SUCCESS WITHOUT END-TO-END PROOF**: Complete pipeline must work
- **DEPLOYABILITY GATE**: Code only complete when executable in clean environment
- **LOCKED ARTIFACT INTEGRITY**: Tests and specifications cannot be modified during implementation

### Context Management Principles
- **Decomposition Strategy**: Break large problems into context-window-sized pieces
- **Just-in-Time Context Loading**: Load only relevant context for current problem
- **Cross-Reference System**: Bidirectional linking between all related files
- **Always-in-Context Foundation**: Keep core rules and structure always loaded
- **Auto-Error Injection**: Errors automatically flow into context window

### Multi-Scale Iteration Architecture

The system operates on **three hierarchical iteration scales**:

#### **Micro-Iterations** (Within Implementation Phase)
- Fix bugs, optimize performance, handle simple test failures
- Scope: Current implementation task
- Decision tree: V5 Hybrid Intelligence flow

#### **Macro-Iterations** (Cross-Phase Returns)
- Return to previous planning phase when gaps discovered
- Scope: Within current planning process
- Example: Phase 7 implementation reveals Phase 5 pseudocode gaps

#### **Meta-Iterations** (Cross-Process Returns)
- Return to planning process when fundamental specification issues discovered
- Scope: Challenge planning artifacts themselves
- **Critical Safeguard**: Uses Fresh Instance Evaluators to prevent cheating

### Fresh Instance Anti-Cheating Protocol

When implementation encounters **potential planning specification issues**:

1. **Evidence Package Creation**: Document specific inconsistency with concrete evidence
2. **Fresh Instance Evaluation**: Spawn independent Claude instance via Task tool
3. **Objective Assessment**: Fresh instance evaluates without implementation bias or frustration
4. **Controlled Planning Return**: Only legitimate specification issues trigger planning process return

**Key Principle**: Implementation instances (with cheating motivation) cannot directly modify planning artifacts. Only objective fresh instances (without implementation context) can authorize planning returns.

### Learning & Persistence Principles
- **Cross-Session Memory**: Remember failures, patterns, and decisions
- **Evidence Trails**: Maintain structured records of what worked/failed
- **Progressive Refinement**: Improve decision-making based on historical data
- **Process Learning**: Use meta-iterations to improve both planning and implementation processes

## Target Outcome

**An autonomous system that can:**

1. **Take a project specification** and decompose it into manageable phases
2. **Generate proper documentation** (behavior, architecture, tests) before coding
3. **Implement with validation** at each step using real data and dependencies
4. **Learn from failures** and avoid repeating mistakes
5. **Provide clear blocking signals** when human input required (API keys, business decisions)
6. **Scale to any codebase** regardless of size or complexity

## Success Metrics

### Functional Metrics
- **Zero false success claims**: No "complete" status without end-to-end proof
- **Real data validation**: All implementations work with actual external services
- **Clean environment deployment**: Code runs in fresh environment without hidden dependencies
- **Cross-session consistency**: Learns from previous failures and avoids repetition

### Process Metrics  
- **Context efficiency**: Problems solved within context window constraints
- **Error visibility**: All failures logged and addressed, none hidden
- **Documentation quality**: Clear traceability from requirements to implementation
- **Dependency clarity**: Explicit blocking when external resources needed

## Project Scope

### In Scope
- Autonomous TDD methodology and process design
- Hook system for Claude Code integration
- Context management and cross-reference tools
- Evidence validation and anti-fabrication systems
- Cross-session learning and persistence

### Out of Scope (Initially)
- IDE integrations beyond Claude Code
- Real-time collaborative editing
- Advanced AI model fine-tuning
- Enterprise deployment and scaling

## Key Constraints & Assumptions

### Technical Constraints
- **Context Window Limit**: ~200K tokens maximum per session
- **Claude Code Environment**: Must work within existing Claude Code tooling
- **No Persistent Memory**: System must recreate understanding each session

### Methodological Assumptions
- **TDD is Beneficial**: Test-driven approach improves reliability
- **Documentation-First**: Proper planning prevents implementation issues
- **Evidence-Based Validation**: Concrete proof more reliable than LLM judgment
- **Incremental Development**: Small, validated steps more reliable than large changes

### User Assumptions
- **Developer Understands TDD**: User familiar with test-driven development concepts
- **Clear Requirements**: User can articulate desired behavior and success criteria
- **Willing to Provide Dependencies**: User will supply API keys, credentials when needed

This overview establishes the foundation for making specific behavior and architecture decisions in subsequent phases.