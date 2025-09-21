# /investigate_pre_impl

Investigate technical unknowns before implementation.

## What This Command Does

1. Researches technical solutions
2. Tests approaches with small experiments
3. Evaluates libraries and tools
4. Documents technical findings
5. Creates implementation plan

## When to Use

- When categorized as technical uncertainty
- Before implementing complex features
- When evaluating multiple approaches
- For API/library research

## Actions

1. Define technical questions clearly
2. Research potential solutions
3. Create small test scripts if needed
4. Evaluate pros/cons of approaches
5. Document findings and decisions
6. Update implementation strategy

## Investigation Areas

- Library capabilities
- API limitations
- Performance considerations
- Security implications
- Integration challenges

## Evidence Collection

Create: `investigations/technical/pre_impl_research.md`
- Technical questions
- Solutions evaluated
- Test results
- Recommended approach
- Implementation notes

## Next Command

- **Solution found** → `/update_plans_within_phase`
- **Multiple attempts** → Check loop count
- **Loop >= 7** → `/escalate_to_deferred`
- **Ready** → Return to `/write_tests`

## Success Criteria

- Technical approach validated
- Implementation path clear
- Risks identified
- Evidence documented