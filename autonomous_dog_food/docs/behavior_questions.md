# Behavior Question Records (BQRs) - Autonomous TDD System

## Purpose
These questions identify fundamental behavior decisions that must be resolved before defining the desired system behavior. Each question will lead to a Behavior Decision Record (BDR).

---

## BQR-001: Autonomy Level and Human Interaction

**Question**: How autonomous should the system be, and when should it require human intervention?

**Options**:
A) **Full Autonomy**: System runs completely independently until completion or permanent blocking
B) **Checkpoint Autonomy**: System autonomously completes phases but requires human approval between phases  
C) **Guided Autonomy**: Human can intervene at any point, system asks for guidance when uncertain
D) **Supervised Autonomy**: Human must approve all major decisions, system executes approved plans

**Context**: 
- Full autonomy risks expensive mistakes or infinite loops
- Too much human interaction defeats the purpose of automation
- Some decisions (API keys, business logic) genuinely require human input
- Safety mechanisms needed to prevent runaway behavior

**Impact Areas**: Error handling, decision escalation, safety mechanisms, user experience

---

## BQR-002: Scope and Project Type Compatibility

**Question**: Should the system be designed for any codebase/project type, or specialize for certain domains?

**Options**:
A) **Universal System**: Works on any software project (web, mobile, data science, etc.)
B) **Domain-Specific**: Optimized for specific types (e.g., web scraping, API integration)
C) **Template-Based**: Configurable templates for common project patterns
D) **Learning System**: Starts general, learns and specializes based on usage patterns

**Context**:
- Different project types have different TDD patterns
- Web scraping (like Goodwill) has unique challenges (external dependencies, rate limiting)
- API projects need different validation than algorithmic projects
- Specialization might improve success rate but limit applicability

**Impact Areas**: Architecture design, test strategies, validation approaches, user adoption

---

## BQR-003: Failure Modes and Recovery Strategies

**Question**: How should the system behave when it encounters problems it cannot solve?

**Options**:
A) **Fail-Fast**: Stop immediately when encountering any blocking issue
B) **Graceful Degradation**: Continue with reduced functionality when possible
C) **Alternative Strategies**: Try multiple approaches before giving up
D) **Human Escalation**: Document problem and request human guidance

**Context**:
- Current Claude Code often fabricates solutions instead of admitting failure
- Some problems are genuinely unsolvable without human input (missing credentials)
- Other problems might be solvable with different approaches
- Clear failure signals more valuable than fake progress

**Impact Areas**: Error handling, user trust, debugging experience, system reliability

---

## BQR-004: External Dependency Management

**Question**: How should the system handle external dependencies (APIs, databases, services)?

**Options**:
A) **Real Dependencies Only**: Never use mocks, fail if real services unavailable
B) **Staged Validation**: Use mocks during development, require real validation before completion
C) **Dependency Detection**: Automatically detect and flag when dependencies are mocked vs real
D) **User Configuration**: Let user specify which dependencies should be real vs mocked

**Context**:
- Goodwill project demonstrated the fabrication risk of mock dependencies
- Some external services are expensive or rate-limited for testing
- Development often needs to progress before all external services are available
- False success claims primarily come from mock data masquerading as real implementation

**Impact Areas**: Test strategy, validation requirements, development workflow, cost management

---

## BQR-005: Context Window and Memory Management

**Question**: How should the system manage the context window limitation and maintain project understanding?

**Options**:
A) **Decomposition-First**: Always break problems into context-window-sized pieces
B) **Smart Loading**: Load relevant context just-in-time for each task
C) **Summary Generation**: Create and maintain project summaries to compress context
D) **Hybrid Approach**: Combine decomposition, smart loading, and summaries

**Context**:
- Context window is hard constraint (~200K tokens)
- Human programmers maintain mental model of entire codebase
- Cross-file dependencies can be missed when context is limited
- Some problems genuinely require understanding of multiple components

**Impact Areas**: Architecture design, problem decomposition, cross-reference system, performance

---

## BQR-006: Learning and Persistence Across Sessions

**Question**: What should the system remember and learn from previous sessions?

**Options**:
A) **Stateless**: Each session starts fresh, no memory of previous work
B) **Error Learning**: Remember what failed and avoid repeating mistakes
C) **Pattern Learning**: Learn successful patterns and apply to similar problems
D) **Full Memory**: Comprehensive history of all decisions, attempts, and outcomes

**Context**:
- Current Claude Code repeats same mistakes across sessions
- Learning from failures could prevent repeated fabrication patterns
- Too much memory might create incorrect assumptions
- Privacy and storage concerns with persistent data

**Impact Areas**: System reliability, user experience, storage requirements, privacy

---

## BQR-007: Test Strategy and Validation Timing

**Question**: When should tests be written, and how should validation be structured?

**Options**:
A) **Classic TDD**: Tests before implementation, strict red-green-refactor
B) **Behavior-First**: Acceptance criteria and behavior tests before unit tests
C) **Layered Testing**: Different test types at different phases (unit → integration → acceptance)
D) **Evidence-Based**: Tests designed to produce concrete evidence of functional success

**Context**:
- Traditional TDD assumes known requirements
- Our process includes behavior definition before architecture
- Anti-fabrication requires tests that detect real vs mock functionality
- Different project types might need different test strategies

**Impact Areas**: Development workflow, validation quality, fabrication prevention, user guidance

---

## BQR-008: Progress Measurement and Success Criteria

**Question**: How should the system measure and report progress towards completion?

**Options**:
A) **Binary States**: Tasks are either complete or incomplete, no partial credit
B) **Progress Percentages**: Quantitative measurement of completion status
C) **Evidence-Based Status**: Completion determined by concrete evidence validation
D) **Multi-Dimensional**: Separate tracking for implementation, testing, integration, validation

**Context**:
- Current systems often claim "90% complete" when actual progress is much less
- False progress reports undermine user trust
- Some work (research, exploration) is hard to quantify
- Clear success criteria essential for autonomous operation

**Impact Areas**: User experience, trust, project planning, autonomous decision-making

---

## Next Steps

Each of these questions needs to be resolved through analysis, discussion, or experimentation, resulting in Behavior Decision Records (BDRs) that will guide the detailed behavior specification.

**Cross-References**:
- Links to: `behavior_decisions.md` (once BDRs are created)
- Links to: `architecture_questions.md` (architectural implications)
- Links to: `overview.md` (problem context and constraints)