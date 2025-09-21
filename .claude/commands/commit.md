# /commit

Commit completed work with evidence.

## What This Command Does

1. Stages completed implementation
2. Creates meaningful commit message
3. References tests and evidence
4. Updates workflow state
5. Prepares for next cycle

## When to Use

- After `/doublecheck` verification
- When feature is complete and tested
- To checkpoint working implementation
- Before starting new feature

## Actions

1. Review changes with `git status` and `git diff`
2. Stage relevant files
3. Create descriptive commit message
4. Reference issue/phase if applicable
5. Include test evidence in message
6. Commit the changes
7. Update workflow state

## Commit Message Format

```
feat(component): Brief description

- Implemented [feature] with TDD approach
- All tests passing (X tests)
- Meets requirements from Phase Y
- Evidence in investigations/[feature]/

Closes #issue (if applicable)
```

## Evidence Archival

Before committing:
1. Move evidence to archive:
   ```bash
   mv investigations/[feature]/ /home/brian/projects/archive/goodwill/[date]_[feature]/
   ```
2. Update evidence references in commit

## Next Steps After Commit

- **More tasks in phase**: Return to `/explore`
- **Phase complete**: Proceed to `/close_phase`
- **New phase ready**: Use `/load_phase_plans`

## Success Criteria

- Clean commit with all changes
- Meaningful commit message
- Evidence archived
- Workflow state updated
- Ready for next task