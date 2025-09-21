# /doublecheck_implementation_within_phase

## Concise Prompt
"Verify what was actually implemented vs the plan. Test functionality. Determine all uncertainties about what was done. Categorize uncertainties and give recommendations."

## Uncertainty Categorization Template
"Determine all uncertainties and things that need to be investigated by those which:
1. We should investigate before implementing further
2. We should resolve through implementation and testing
3. Need strategic clarification from the user
Give recommendations for each."

## Expanded Prompt (To be developed)
[Full prompt with verification checklist, testing patterns, and uncertainty analysis framework]

## Prerequisites
- Implementation completed
- Plan document available for comparison
- Test environment ready

## Success Criteria
- Implementation verified against plan
- All deviations documented
- Uncertainties categorized
- Recommendations provided

## Uncertainty Detection
- Plan vs implementation mismatches
- Unexpected behaviors
- Missing functionality
- Performance issues
- Integration problems

## Typical Next Command
- If strategic uncertainties: `/review_against_architecture_within_phase`
- If implementation uncertainties: `/investigate_uncertainties_within_phase`
- If all verified: `/test_within_phase`

## Hook Triggers
- PostToolUse after `/implement_within_phase`
- Stop hook (to ensure verification happens)