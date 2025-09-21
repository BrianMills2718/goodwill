# /load_next_phase

Load the next phase after completing current one.

## What This Command Does

1. Reads next phase from phases.md
2. Updates CLAUDE.md with new phase
3. Clears previous phase state
4. Sets up for new phase work
5. Begins new TDD cycle

## When to Use

- After `/close_phase` completes
- When transitioning phases
- To start next development cycle
- After phase archival

## Actions

1. Read `docs/development_roadmap/phases.md`
2. Find next uncompleted phase
3. Update CLAUDE.md with:
   - New phase name and goals
   - Phase tasks
   - Success criteria
   - Timeline
4. Clear workflow state
5. Set command to `/explore`
6. Initialize new evidence structure

## Phase Loading Process

```
1. Mark previous phase complete in phases.md
2. Identify next phase (first unchecked)
3. Extract phase details
4. Update CLAUDE.md sections
5. Reset iteration counters
6. Begin exploration
```

## Next Command

- Always → `/explore` to understand new phase
- Begin new TDD cycle

## Success Criteria

- Next phase loaded
- CLAUDE.md updated
- Clean state for new work
- Ready to explore requirements