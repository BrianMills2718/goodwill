# /investigate_uncertainties

Investigate and resolve uncertainties that block progress.

## What This Command Does

1. Identifies specific uncertainties
2. Researches solutions
3. Documents findings
4. Updates plans based on discoveries
5. Breaks out of stuck loops

## When to Use

- When stuck in a loop (7+ iterations)
- When requirements are unclear
- When technical approach is uncertain
- When external research is needed

## Actions

1. List all current uncertainties
2. Categorize by type:
   - Technical (how to implement)
   - Requirements (what to build)
   - Architecture (design decisions)
   - External (APIs, libraries)
3. Research each uncertainty
4. Document findings
5. Update plans with decisions
6. Create clear next steps

## Investigation Process

```
For each uncertainty:
1. Define the question clearly
2. Research potential solutions
3. Evaluate options
4. Make decision or escalate
5. Document rationale
```

## Evidence Collection

Create: `investigations/uncertainties/[timestamp]_investigation.md`
- Questions investigated
- Research findings
- Decisions made
- Remaining unknowns
- Updated approach

## Next Command

After resolving uncertainties:
- Return to `/explore` with new understanding
- Or proceed to `/write_tests` if ready

## Success Criteria

- Key uncertainties resolved
- Decisions documented
- Clear path forward
- No longer stuck in loop