# /session_recovery

Recover workflow state when session restarts.

## What This Command Does

1. Reads workflow state from CLAUDE.md
2. Loads current command and iteration
3. Checks for incomplete work
4. Resumes at correct point
5. Maintains continuity

## When to Use

- Automatically on SessionStart hook
- When Claude Code restarts
- After unexpected interruption
- To resume work

## Actions

1. Read CLAUDE.md for:
   - Current phase
   - Active command
   - Iteration count
   - Pending tasks
2. Load `.claude/workflow_state.json`
3. Check for evidence files
4. Determine resume point
5. Set next command
6. Continue workflow

## Recovery Priority

1. **Active errors** → `/resolve_blockers`
2. **Mid-implementation** → Check test status
3. **Investigation active** → Resume investigation
4. **Clean state** → Continue with next command

## State Sources

- Primary: CLAUDE.md (always in context)
- Secondary: `.claude/workflow_state.json`
- Evidence: `investigations/` directory
- Phase: `docs/development_roadmap/phases.md`

## Next Command

Resume at `current_command` from state, or:
- If unknown → `/explore`
- If errors → `/resolve_blockers`
- If phase complete → `/load_next_phase`

## Success Criteria

- State recovered accurately
- Can continue without data loss
- Workflow resumes smoothly
- No duplicate work