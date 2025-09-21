# Command Structure with Systematic Uncertainty Resolution

## Core Principle: Double-Check Everything

Every command includes uncertainty detection using the pattern:
> "Determine all uncertainties and things that need to be investigated by those which:
> 1. We should investigate before implementing
> 2. We should resolve through implementation and testing  
> 3. Need strategic clarification from the user
> Give recommendations for each."

## Within-Phase Commands (Inner Loop)

### /explore_within_phase
**Prompt**: "Read relevant files for the current task in CLAUDE.md. Identify what we know, what we don't know, and what we need to discover. Do not write any code yet."

### /investigate_uncertainties_within_phase
**Prompt**: "For each uncertainty identified, use subagents to investigate. Document findings in investigations/[area]/. Determine which uncertainties remain unresolved."

### /doublecheck_investigations_within_phase
**Prompt**: "Review investigation findings. Determine all uncertainties and things that need to be investigated by those which we should investigate before implementing, those which we should resolve through implementation and testing, and those which you need strategic clarification from me for. Give recommendations for each."

### /review_against_architecture_within_phase
**Prompt**: "IF strategic uncertainties exist: Review docs/architecture/ for guidance on these uncertainties. Determine if architecture documentation addresses them. Identify any gaps or conflicts. Categorize remaining uncertainties using the same three categories."

### /review_against_behavior_within_phase
**Prompt**: "IF strategic uncertainties remain: Review docs/behavior/ for guidance. Determine if behavior documentation addresses them. Identify any gaps or conflicts. Categorize remaining uncertainties. Repeat until all architecture/behavior confidence is high."

### /plan_within_phase
**Prompt**: "Create detailed implementation plan for current task, incorporating all investigation findings and resolved uncertainties. Use 'think harder' mode. Document plan structure."

### /doublecheck_plan_within_phase
**Prompt**: "Review the plan. Determine all uncertainties about the plan itself. Categorize by: investigate before implementing, resolve through implementation, or need strategic clarification. Give recommendations."

### /implement_within_phase
**Prompt**: "Execute the plan in code. As you implement, explicitly verify each assumption. Document any new discoveries or uncertainties that emerge."

### /doublecheck_implementation_within_phase
**Prompt**: "Verify what was actually implemented vs the plan. Test functionality. Determine all uncertainties about what was done. Categorize uncertainties and give recommendations."

### /test_within_phase
**Prompt**: "Run comprehensive tests. Document results. Identify any failures or unexpected behaviors."

### /doublecheck_tests_within_phase
**Prompt**: "Review test results. Determine if implementation meets requirements. Identify remaining uncertainties. Categorize and recommend next steps."

### /commit_within_phase
**Prompt**: "IF all tests pass and no blocking uncertainties: Commit changes with detailed message explaining what was done and why."

### /update_plans_within_phase
**Prompt**: "Update CLAUDE.md with: resolved uncertainties as facts, new discoveries as context, remaining work as next tasks. Ensure self-contained for next session."

## Between-Phase Commands (Outer Loop)

### /complete_phase
**Prompt**: "Verify all phase objectives met with evidence. Archive evidence to investigations/[phase]/archive_YYYYMMDD/. Update phases.md marking phase complete."

### /doublecheck_phase_completion
**Prompt**: "Review phase evidence. Verify completeness. Determine any uncertainties about whether phase is truly complete. Categorize uncertainties and give recommendations."

### /review_architecture_between_phases
**Prompt**: "Review entire docs/architecture/ in context of completed phase. Determine if phase results validate or challenge architectural decisions. Identify needed updates. Categorize any strategic uncertainties."

### /review_behavior_between_phases  
**Prompt**: "Review entire docs/behavior/ in context of completed phase. Determine if phase results align with desired behavior. Identify gaps or conflicts. Categorize any strategic uncertainties."

### /review_roadmap_between_phases
**Prompt**: "Review docs/development_roadmap/ in light of phase completion. Determine if roadmap remains valid. Identify needed adjustments. Categorize strategic uncertainties."

### /doublecheck_strategic_alignment
**Prompt**: "Review all documentation together. Ensure behavior→architecture→roadmap alignment. Determine uncertainties about project direction. Categorize and recommend."

### /update_strategy_between_phases
**Prompt**: "IF strategic changes needed: Update relevant documentation with discoveries and decisions. Ensure all docs remain synchronized."

### /load_next_phase
**Prompt**: "Load next phase from phases.md into CLAUDE.md. Include context from completed phases. Set up for new within-phase loop."

### /doublecheck_next_phase_readiness
**Prompt**: "Review loaded phase plans. Verify prerequisites met. Determine uncertainties about readiness to proceed. Categorize and recommend."

## Discovery Integration Commands (Triggered Automatically)

### /detect_discovery
**Prompt**: "Scan investigations/ for new findings. Classify each discovery by impact: minor (continue), major (adjust plans), blocking (reassess strategy)."

### /doublecheck_discovery_classification  
**Prompt**: "Review discovery classifications. Verify impact assessments. Determine uncertainties about how to integrate discoveries. Categorize and recommend."

### /integrate_minor_discovery
**Prompt**: "Add minor discoveries to current plans without disrupting flow. Update CLAUDE.md with new context."

### /integrate_major_discovery
**Prompt**: "Adjust current phase plans to accommodate major discovery. Trigger review against architecture/behavior if needed."

### /handle_blocking_discovery
**Prompt**: "Stop current work. Document blocking issue. Trigger full strategic review cycle."

## Error Management Commands

### /detect_errors
**Prompt**: "Scan logs/errors/ for new issues. Classify by severity and impact."

### /doublecheck_error_impact
**Prompt**: "Review error classifications. Determine uncertainties about error causes and fixes. Categorize by investigation needs."

### /inject_errors_to_claude
**Prompt**: "Update CLAUDE.md with active errors requiring attention. Include resolution recommendations."

## Automation Orchestration Commands

### /assess_current_state
**Prompt**: "Read CLAUDE.md and phases.md. Determine current position in workflow. Identify what just completed and what should happen next."

### /determine_next_command
**Prompt**: "Based on current state and any pending uncertainties, determine the next command to execute. Consider both within-phase and between-phase contexts."

### /doublecheck_next_command
**Prompt**: "Verify the next command choice is correct. Check for any blocking conditions. Confirm prerequisites are met."

## Key Patterns

1. **Every action has a doublecheck** - No assumptions without verification
2. **Uncertainties cascade upward** - Strategic uncertainties trigger architecture/behavior review
3. **Resolution before progression** - Don't move forward with unresolved blocking uncertainties
4. **Documentation synchronization** - Keep all layers aligned (behavior→architecture→roadmap→implementation)
5. **Evidence-based transitions** - Phase completion requires documented proof

## State Tracking

Track in `/tmp/goodwill_workflow_state.json`:
- Current phase
- Current command
- Pending uncertainties
- Discovery queue
- Error queue
- Last completed action

## Trigger Conditions

Each command specifies:
- Prerequisites (what must be true before execution)
- Success criteria (what must be true after execution)
- Uncertainty thresholds (when to escalate)
- Next command logic (what typically follows)