# Uncertainty Cascade Pattern

## Core Principle
Every uncertainty must be categorized and resolved before proceeding. Strategic uncertainties cascade upward to documentation review.

## Uncertainty Categories

### 1. Investigate Before Implementing
**Resolution Path**: 
- Trigger `/investigate_uncertainties_within_phase`
- Use subagents for research
- Document findings in investigations/
- Return to current command after resolution

**Examples**:
- Unknown API endpoints
- Unclear library behavior
- Missing documentation
- Unverified assumptions

### 2. Resolve Through Implementation and Testing
**Resolution Path**:
- Continue with implementation
- Add specific tests for uncertainty
- Document results
- Verify in `/doublecheck_implementation_within_phase`

**Examples**:
- Performance characteristics
- Edge case behavior
- Integration effects
- Error handling paths

### 3. Strategic Clarification Needed
**Resolution Path**:
- Cascade up to `/review_against_architecture_within_phase`
- Then `/review_against_behavior_within_phase`
- Repeat until confidence high
- May require user input if truly strategic

**Examples**:
- Core business logic questions
- Architectural decisions
- Behavior specifications
- Priority conflicts

## Cascade Flow

```
Uncertainty Detected
        ↓
Categorize (1, 2, or 3)
        ↓
Category 1 → Investigate → Document → Resume
Category 2 → Implement → Test → Verify
Category 3 → Review Architecture
              ↓
        Still Uncertain?
              ↓
        Review Behavior
              ↓
        Still Uncertain?
              ↓
        User Clarification
```

## Confidence Levels

### High Confidence
- Documentation clearly addresses the question
- Multiple sources confirm approach
- Tests validate assumptions
- No conflicting information

### Medium Confidence  
- Documentation partially addresses question
- Some validation available
- Minor conflicts resolvable
- Assumptions seem reasonable

### Low Confidence
- Documentation silent or unclear
- No validation available
- Conflicts present
- Assumptions questionable

## Escalation Triggers

**Immediate Escalation** (Category 3):
- Conflicts between behavior and architecture docs
- Missing critical specifications
- Decisions affecting multiple phases
- Security or compliance questions

**Investigation Required** (Category 1):
- Technical unknowns
- External dependencies
- Tool capabilities
- Performance requirements

**Implementation Resolution** (Category 2):
- Detailed behavior under specific conditions
- Error handling strategies
- Optimization approaches
- UI/UX decisions

## Documentation Requirements

For each uncertainty resolution:
1. Document the original uncertainty
2. Record investigation steps
3. Note findings and evidence
4. State final resolution
5. Update relevant documentation if needed

## Automation Hooks

**PostToolUse Hook on doublecheck commands**:
- Parse output for uncertainty categories
- Trigger appropriate resolution path
- Track resolution status
- Resume workflow after resolution

**Stop Hook after investigation**:
- Check if uncertainties resolved
- Determine next command based on resolution
- Update state tracking
- Continue workflow

## State Tracking

In `/tmp/goodwill_uncertainty_state.json`:
```json
{
  "pending_uncertainties": [
    {
      "id": "uuid",
      "description": "uncertainty description",
      "category": 1|2|3,
      "detected_in": "command_name",
      "resolution_path": "investigation|implementation|review",
      "status": "pending|investigating|resolved",
      "resolution": "resolution description if resolved"
    }
  ],
  "cascade_level": "implementation|architecture|behavior|user",
  "confidence": "high|medium|low"
}
```

## Key Rules

1. **Never skip uncertainty resolution** - All uncertainties must be addressed
2. **Strategic uncertainties always cascade up** - Don't guess on strategic questions
3. **Document everything** - Uncertainty resolution is valuable knowledge
4. **High confidence before proceeding** - Don't move forward with doubts
5. **Iterative resolution** - Keep reviewing until confidence is high