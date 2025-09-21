# /validate_phase_completion

Validate that current phase is truly complete.

## What This Command Does

1. Verifies all phase requirements met
2. Checks evidence completeness
3. Validates test coverage
4. Confirms quality standards
5. Ensures nothing missed

## When to Use

- After phase tasks appear complete
- Before `/close_phase`
- When confidence == High needed
- For final phase verification

## Validation Checklist

### Requirements
- [ ] All phase tasks from phases.md complete
- [ ] Success criteria achieved
- [ ] Acceptance tests passing

### Evidence
- [ ] Implementation evidence exists
- [ ] Test results documented
- [ ] Verification complete
- [ ] No unresolved issues

### Quality
- [ ] Code coverage >= 80%
- [ ] No critical bugs
- [ ] Documentation updated
- [ ] Follows project patterns

### Readiness
- [ ] Can demo the feature
- [ ] Edge cases handled
- [ ] Error handling robust
- [ ] Performance acceptable

## Actions

1. Run comprehensive test suite
2. Review all evidence files
3. Check phases.md requirements
4. Verify success criteria
5. Document validation results

## Next Command

- **All validated** → `/close_phase`
- **Gaps found** → Return to appropriate command
- **Minor issues** → `/doublecheck` to fix

## Success Criteria

- All checkboxes checked
- Confidence == High
- Ready for phase closure
- No doubts about completeness