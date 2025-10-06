# Iterative Methodology with LLM-Driven Stabilization

## Purpose
This document defines the complete iterative methodology for autonomous TDD development, including problem tracking and LLM-driven stabilization criteria. This replaces previous linear methodology descriptions.

## Complete Enhanced Methodology

### **Phase Structure with Stabilization**

```
1. Overview
2. Behavior + Acceptance Tests
3. Architecture + Contract Integration Tests  
4. External Dependency Research + External Integration Tests
5. Pseudocode + Architecture Review (iterative stabilization)
6. Implementation Plans + Unit Tests + Implementation Integration Tests
7. Create Files & Cross-References
8. Implementation
```

### **Iterative Process Within Each Phase**

```
FOR EACH PHASE:
  1. Draft initial version
  2. LLM problem identification scan
  3. Micro-iterate until phase stability (LLM confidence >0.8)
  4. Check impact on previous phases
  5. If major impact discovered → macro-iteration
  6. Continue until global stability achieved
```

## Three Types of Integration Tests

### **Type A: Contract Integration Tests** (Architecture Phase - BEFORE pseudocode)
- **Purpose**: Define component interfaces and external API contracts
- **Focus**: *"What needs to integrate and how?"*
- **Location**: `tests/integration/test_contracts/`
- **Content**: Interface definitions, API contracts, component boundaries

### **Type B: External Dependency Integration Tests** (External Research Phase)
- **Purpose**: Test real external APIs, authentication, data flows
- **Focus**: *"Do external services actually work as expected?"*
- **Location**: `tests/integration/test_external/`
- **Content**: Real API calls, authentication validation, dependency verification

### **Type C: Implementation Integration Tests** (Post-Pseudocode Phase)
- **Purpose**: Test actual component interactions based on implementation design
- **Focus**: *"Does our implementation design actually integrate correctly?"*
- **Location**: `tests/integration/test_implementation/`
- **Content**: Component interaction validation, pseudocode assumption testing

## Problem Tracking System

### **Problem Record Structure**

```json
{
  "problem_id": "arch_001",
  "phase_discovered": "pseudocode",
  "description": "Circular dependency between orchestrator and analysis components",
  "impact_phases": ["architecture", "implementation"],
  "severity": "high",
  "status": "unresolved",
  "resolution_attempts": 2,
  "discovered_at": "2024-01-15T10:30:00Z",
  "resolution_plan": "Implement dependency injection pattern",
  "estimated_impact": "requires architecture revision"
}
```

### **Global Stability Assessment**

```json
{
  "stability_assessment": {
    "overall_stable": false,
    "total_confidence": 0.7,
    "unstable_phases": ["architecture", "external_dependencies"],
    "critical_problems": 2,
    "minor_problems": 5,
    "macro_iterations_completed": 1,
    "ready_for_implementation": false
  }
}
```

## LLM-Driven Stabilization Criteria

### **Phase-Level Stability Check**

**LLM Stability Assessment Prompt:**
```
Analyze this phase documentation against the problem list:

PHASE: {phase_name}
DOCUMENTATION: {phase_docs}
OPEN_PROBLEMS: {problem_list}

STABILITY CRITERIA:
- No new major architectural decisions needed
- No unresolved circular dependencies  
- All external dependencies researched and accessible
- No conflicts between behavior and implementation complexity
- All open problems have clear resolution paths

ASSESSMENT REQUIRED:
- Is this phase stable enough to proceed? (yes/no)
- Confidence level (0.0-1.0)
- Remaining critical issues (list)
- Impact on other phases (list affected phases)
- Recommended actions (if unstable)

RESPONSE FORMAT: JSON with assessment, confidence, issues, impacts, recommendations
```

### **Global Stability Check**

**Global Assessment Criteria:**
- **Phase-level**: All phases >0.8 confidence
- **Problem count**: <5 total open problems, <2 critical problems
- **Cross-phase consistency**: No unresolved conflicts between phases
- **External validation**: All external dependencies tested and accessible

### **Stabilization Limits and Emergency Procedures**

**Iteration Limits:**
- **Micro-iterations**: 5 per phase (prevent infinite refinement)
- **Macro-iterations**: 3 full cycles (prevent analysis paralysis)
- **Total problem resolution attempts**: 15 across all phases
- **Emergency stability forcing**: After limits exceeded

**Emergency Stability Procedures:**
```
IF macro_iterations > 3:
    Force proceed with documented risks
    Create risk mitigation plan
    
IF problem_resolution_attempts > 15:
    Escalate to human intervention
    Document blocking issues
    
IF external_dependencies_unavailable:
    Clear blocking with alternative solutions
    Document fallback strategies
```

## Implementation Integration Patterns

### **Autonomous System Integration**

```python
class MethodologyStabilizer:
    def __init__(self, project_root: str):
        self.problem_tracker = ProblemTracker()
        self.llm_assessor = LLMStabilityAssessor()
        self.phase_manager = PhaseManager()
    
    def assess_phase_stability(self, phase_name: str, phase_docs: Dict[str, str]) -> Dict[str, Any]:
        """Assess if a phase is stable enough to proceed"""
        
        # Get current problems for this phase
        phase_problems = self.problem_tracker.get_problems_for_phase(phase_name)
        
        # LLM assessment
        llm_assessment = self.llm_assessor.assess_stability(
            phase_name, phase_docs, phase_problems
        )
        
        return {
            'stable': llm_assessment['confidence'] > 0.8,
            'confidence': llm_assessment['confidence'],
            'critical_issues': llm_assessment['critical_issues'],
            'phase_impacts': llm_assessment['phase_impacts'],
            'macro_iteration_needed': len(llm_assessment['phase_impacts']) > 1
        }
    
    def execute_stabilization_cycle(self, current_phase: str) -> Dict[str, Any]:
        """Execute one stabilization cycle for current phase"""
        
        # Check phase stability
        stability = self.assess_phase_stability(current_phase, self.phase_manager.get_phase_docs(current_phase))
        
        if not stability['stable']:
            # Micro-iteration within phase
            self._execute_micro_iteration(current_phase, stability['critical_issues'])
            
        if stability['macro_iteration_needed']:
            # Macro-iteration affecting previous phases
            self._execute_macro_iteration(stability['phase_impacts'])
        
        return stability
    
    def should_proceed_to_implementation(self) -> Tuple[bool, Dict[str, Any]]:
        """Determine if all phases are stable enough for implementation"""
        
        global_assessment = self._assess_global_stability()
        
        proceed = (
            global_assessment['total_confidence'] > 0.8 and
            global_assessment['critical_problems'] == 0 and
            global_assessment['external_dependencies_validated']
        )
        
        return proceed, global_assessment
```

### **Problem Discovery and Tracking**

```python
class ProblemTracker:
    def discover_problems_in_phase(self, phase_name: str, phase_docs: Dict[str, str]) -> List[Problem]:
        """Use LLM to discover problems in phase documentation"""
        
        discovery_prompt = f"""
        Analyze this {phase_name} phase documentation for problems:
        
        {phase_docs}
        
        IDENTIFY:
        - Circular dependencies
        - Missing requirements
        - Conflicting specifications
        - Implementation impossibilities
        - External dependency issues
        - Cross-phase consistency problems
        
        FORMAT: JSON list of problems with id, description, severity, impact_phases
        """
        
        problems_data = self.llm_analyzer.query(discovery_prompt)
        return [Problem.from_dict(p) for p in problems_data['problems']]
    
    def track_resolution_attempt(self, problem_id: str, action_taken: str, result: str):
        """Track attempts to resolve problems"""
        
        self.problems[problem_id].resolution_attempts += 1
        self.problems[problem_id].resolution_history.append({
            'action': action_taken,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
```

## Autonomous Methodology Execution

### **Hook Integration for Stabilization**

The autonomous hook system integrates this methodology:

1. **Phase Execution**: Execute each phase with micro-iteration cycles
2. **Problem Discovery**: LLM scans for problems after each phase draft
3. **Status Tracking**: Update CLAUDE.md iteration section and supporting documentation
4. **Stabilization**: Iterate until LLM confidence >0.8
5. **Cross-Phase Validation**: Check impact on previous phases
6. **Macro-Iteration**: Update affected phases if needed, track in CLAUDE.md
7. **Global Validation**: Ensure all phases stable before implementation
8. **Emergency Limits**: Force proceed if iteration limits exceeded

### **Iteration Tracking System Integration**

**Primary Tracking**: CLAUDE.md iteration section provides:
- Current iteration status (phase, type, counts)
- Active problems tracking with criticality
- Problem discovery history by iteration
- Stabilization decision log with rationale
- Iteration limit tracking and emergency thresholds

**Supporting Documentation**:
- `docs/development_roadmap/current_gaps_analysis.md` - Systematic problem documentation
- `docs/development_roadmap/iteration_tracking_system.md` - LLM decision framework
- `current_problems.json` (future) - Machine-readable problem tracking

**Integration Benefits**:
- **Always in Context**: CLAUDE.md loaded in every LLM session
- **Autonomous Decision Making**: Clear criteria for micro vs macro iterations
- **Problem Visibility**: Critical issues always visible to LLMs
- **History Preservation**: Prevents losing track of iteration cycles
- **Consistency**: Synchronized tracking across all documentation systems

**LLM Operational Workflow**:
1. **Session Start**: Read CLAUDE.md iteration section to understand current state
2. **Problem Assessment**: Update problem tracking as new issues discovered
3. **Iteration Decision**: Use documented criteria to decide micro vs macro iteration
4. **Status Update**: Maintain consistency across CLAUDE.md and supporting docs
5. **Progression Decision**: Use evidence-based criteria for phase advancement

### **Documentation Updates Required**

This methodology replaces and supersedes:
- Linear methodology descriptions in ADR-003
- Conflicting test timing in various ADRs
- Incomplete iteration strategies in existing documents

All autonomous systems should implement this iterative stabilization approach for self-improving planning capabilities.

## Success Metrics

### **Methodology Effectiveness**
- **Problem resolution rate**: >90% of discovered problems resolved within iteration limits
- **False stability rate**: <5% of "stable" phases require major changes later
- **Implementation surprise rate**: <2% of implementations discover new architectural problems

### **Quality Indicators**
- **Global confidence**: >0.8 before proceeding to implementation
- **Critical problems**: 0 unresolved critical issues
- **External validation**: 100% of external dependencies tested and accessible
- **Cross-phase consistency**: 0 unresolved conflicts between phases

This iterative methodology with LLM-driven stabilization ensures comprehensive problem resolution before implementation, preventing the fabrication and overoptimism issues that plague autonomous development systems.