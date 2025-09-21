# /close_phase

Close the current phase and prepare for transition.

## What This Command Does

1. Verifies all phase requirements complete
2. Archives evidence to external location
3. Updates phases.md with completion
4. Creates phase summary
5. Prepares for next phase

## When to Use

- When all phase tasks are complete
- After final `/commit` for the phase
- When ready to move to next phase
- After verifying all requirements met

## Actions

1. Verify phase completion checklist
2. Create phase summary document
3. Archive all evidence:
   ```bash
   mv investigations/phase_X/ /home/brian/projects/archive/goodwill/$(date +%Y%m%d)_phase_X/
   ```
4. Update phases.md - mark items complete
5. Update CLAUDE.md - clear phase-specific content
6. Create transition document
7. Identify next phase

## Phase Completion Checklist

- [ ] All tasks in phase complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Evidence archived
- [ ] No blocking issues
- [ ] Requirements verified

## Evidence Archival

Archive structure:
```
/home/brian/projects/archive/goodwill/
└── YYYYMMDD_phase_name/
    ├── evidence/
    ├── test_results/
    ├── implementation/
    └── summary.md
```

## Next Command

After closing phase:
- `/load_phase_plans` to load next phase
- Or project complete if last phase

## Success Criteria

- Phase marked complete in phases.md
- Evidence archived externally
- Summary document created
- Ready for next phase