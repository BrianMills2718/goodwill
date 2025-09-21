# /update_plans_within_phase

Update plans within current phase based on findings.

## What This Command Does

1. Integrates investigation findings
2. Updates CLAUDE.md with discoveries
3. Adjusts phase approach if needed
4. Creates checkpoint commit
5. Resets loop counter

## When to Use

- After successful investigation
- When approach changes needed
- To document major decisions
- Before returning to main flow

## Actions

1. Summarize investigation findings
2. Update CLAUDE.md with:
   - New understanding
   - Adjusted approach
   - Discovered requirements
3. Update phase tasks if needed
4. Create evidence checkpoint
5. Commit if significant changes
6. Reset workflow state

## Updates to Make

- CLAUDE.md project notes
- Phase-specific approach
- Known constraints
- Technical decisions
- Next immediate steps

## Evidence Collection

Create: `investigations/plans/updated_approach.md`
- What changed
- Why it changed
- Impact on timeline
- New requirements

## Next Command

- Return to main TDD flow
- Usually → `/explore` or `/write_tests`
- Continue from where left off

## Success Criteria

- Plans reflect new knowledge
- CLAUDE.md updated
- Clear path forward
- Loop counter reset