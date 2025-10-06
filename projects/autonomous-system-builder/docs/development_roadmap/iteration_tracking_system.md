# Iteration Tracking System - Micro/Macro Cycle Management

## Purpose
Systematic tracking for micro/macro iterations to ensure LLMs can autonomously manage the iterative methodology without losing track of cycles, problems, and stabilization decisions.

## Tracking Integration Strategy

### Primary Tracking Location: CLAUDE.md Extension

**Rationale**: CLAUDE.md is always in LLM context, making it the optimal location for iteration tracking that LLMs need to reference constantly.

**Proposed Addition to CLAUDE.md**:

```markdown
## 🔄 ITERATION TRACKING

### Current Iteration Status
- **Methodology Phase**: Phase 5 (Implementation Plans + Unit Tests)
- **Iteration Type**: MACRO-ITERATION (returning to Phase 3 for stabilization)
- **Iteration Count**: Macro: 1, Micro: 3
- **Stability Assessment**: UNSTABLE (13 gaps identified, confidence < 0.8)

### Active Problems Tracking
**Critical Problems** (blocking progression):
- [ ] Missing 3 pseudocode components (gaps 1-3)
- [ ] Architecture underspecification (gaps 4-6) 
- [ ] Circular dependency resolution (gaps 7-8)

**Problem History**:
- **Iteration 1**: Initial Phase 5 entry
- **Iteration 2**: Discovered missing pseudocode
- **Iteration 3**: Status tracker integration added
- **Iteration 4**: Gap analysis revealed 13 problems → MACRO-ITERATION triggered

### Stabilization Decision Log
- **2024-01-15**: 13 gaps identified, macro-iteration to Phase 3 decided
- **Next Decision Point**: After architecture stabilization complete

### Iteration Limits Tracking
- **Micro-iterations this phase**: 3/5 (would have exceeded limit)
- **Macro-iterations total**: 1/3 
- **Emergency intervention threshold**: 15 total problems (currently 13)
```

## Supporting Documentation Structure

### 1. Problem Tracking (`docs/development_roadmap/problems/`)

**`current_problems.json`** - Machine-readable problem tracking:
```json
{
  "iteration_metadata": {
    "current_phase": "phase_5",
    "iteration_type": "macro",
    "macro_count": 1,
    "micro_count": 3,
    "last_assessment": "2024-01-15T10:30:00Z"
  },
  "active_problems": [
    {
      "id": "gap_001",
      "category": "implementation",
      "description": "Missing context system pseudocode",
      "phase_impact": ["phase_5"],
      "severity": "critical",
      "effort_hours": "6-8",
      "discovered_iteration": "micro_2"
    }
  ],
  "resolved_problems": [],
  "stability_assessment": {
    "confidence": 0.3,
    "stable": false,
    "macro_iteration_needed": true,
    "critical_issue_count": 8
  }
}
```

**`problem_history.md`** - Human-readable problem evolution:
```markdown
## Problem Discovery Timeline

### Micro-Iteration 1 (Phase 5 Entry)
- Started with implementation plans
- Assumed pseudocode foundation complete

### Micro-Iteration 2 (Pseudocode Gap Discovery)  
- Discovered 3 missing pseudocode components
- Continued with available components

### Micro-Iteration 3 (Status Tracker Addition)
- Added ADR-009 for status tracking
- Integration impacts unclear

### Macro-Iteration 1 (Stabilization Trigger)
- Comprehensive gap analysis: 13 problems identified
- Architecture underspecification revealed
- Decision: Return to Phase 3 for stabilization
```

### 2. Iteration Decision Framework (`docs/methodology/iteration_decisions.md`)

**LLM Decision Tree**:
```markdown
## Iteration Decision Framework

### Continue Micro-Iteration When:
- ✅ Problem count ≤ 5
- ✅ Problems contained within current phase
- ✅ Confidence > 0.6
- ✅ Micro-iteration count < 5

### Trigger Macro-Iteration When:
- ❌ Problem count > 5 
- ❌ Problems affect previous phases
- ❌ Confidence ≤ 0.6
- ❌ Architecture gaps discovered

### Emergency Intervention When:
- ❌ Macro-iteration count > 3
- ❌ Total problem count > 15
- ❌ No progress after 2 macro-iterations
```

## LLM Workflow Integration

### Session Start Checklist
1. **Read CLAUDE.md iteration section** - understand current iteration state
2. **Load current_problems.json** - get machine-readable problem status  
3. **Assess continuation criteria** - micro vs macro iteration decision
4. **Update iteration tracking** - increment counters, log decisions

### Problem Discovery Workflow
1. **Document in current_problems.json** - structured problem recording
2. **Update CLAUDE.md iteration section** - visible status change
3. **Assess stabilization trigger** - check iteration decision framework
4. **Log decision in problem_history.md** - track decision rationale

### Stabilization Assessment Workflow
1. **Count active problems** - check against thresholds
2. **Evaluate phase impacts** - single vs multi-phase problems
3. **Calculate confidence score** - based on known vs unknown factors
4. **Make iteration decision** - continue micro vs trigger macro
5. **Update all tracking systems** - maintain consistency

## Automation Support

### Status Update Script
```python
def update_iteration_status(phase, iteration_type, problem_count, confidence):
    """Update all iteration tracking systems consistently"""
    
    # Update CLAUDE.md iteration section
    update_claude_md_iteration_section(phase, iteration_type, problem_count)
    
    # Update current_problems.json
    update_problems_json(iteration_type, confidence)
    
    # Log iteration decision
    log_iteration_decision(iteration_type, problem_count, confidence)
    
    # Check intervention thresholds
    check_emergency_intervention_needed()
```

### Problem Assessment Script  
```python
def assess_stabilization_needed(current_problems):
    """LLM-callable function to assess if stabilization needed"""
    
    problem_count = len(current_problems)
    phase_impacts = count_phase_impacts(current_problems)
    confidence = calculate_confidence_score(current_problems)
    
    return {
        "macro_iteration_needed": problem_count > 5 or phase_impacts > 1,
        "continue_micro": problem_count <= 5 and phase_impacts <= 1,
        "emergency_intervention": problem_count > 15,
        "confidence": confidence
    }
```

## Integration with Existing Systems

### CLAUDE.md Integration
- **Iteration section added** to existing structure
- **Problem counts visible** in context window
- **Decision history available** for LLM reference

### Status Tracker Integration  
- **Phase completion tied to iteration stability** 
- **Cannot advance phase with unstable iterations**
- **Evidence includes iteration stability assessment**

### Todo System Integration
- **Active problems become todos** during micro-iterations
- **Macro-iteration triggers todo reorganization**
- **Completed todos reduce problem counts**

## Success Metrics

### Iteration Effectiveness
- **Problem resolution rate** - problems solved per iteration
- **Stability convergence** - confidence scores improving over iterations
- **Phase progression** - successful advancement after stabilization

### LLM Autonomy
- **Correct iteration decisions** - micro vs macro choices align with criteria
- **Problem tracking accuracy** - all gaps documented systematically  
- **Status consistency** - tracking systems remain synchronized

This iteration tracking system ensures LLMs can autonomously manage the complex micro/macro iteration cycles while maintaining clear visibility into progress, problems, and stabilization decisions.