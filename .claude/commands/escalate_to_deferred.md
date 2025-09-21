# /escalate_to_deferred

Escalate unresolvable issues to deferred status.

## What This Command Does

1. Archives the blocking uncertainty
2. Documents what was tried
3. Creates deferred investigation
4. Allows workflow to continue
5. Prevents infinite loops

## When to Use

- When loop_count >= 7
- After multiple investigation attempts
- When blocked by external factors
- To prevent workflow stalling

## Actions

1. Document the blocker thoroughly:
   - What's blocking
   - What was tried
   - Why it failed
   - What's needed to unblock
2. Archive to `investigations/deferred/`
3. Update CLAUDE.md with workaround
4. Mark as deferred in phase plan
5. Find alternative approach if possible
6. Continue with other tasks

## Deferred Structure

```
investigations/deferred/
└── [timestamp]_[issue]/
    ├── blocker_description.md
    ├── attempts_log.md
    ├── requirements_to_unblock.md
    └── workaround_if_any.md
```

## Next Command

- **Workaround found** → Continue with `/explore`
- **Can skip** → Move to next phase task
- **Critical blocker** → `/close_phase` with notes

## Success Criteria

- Blocker documented completely
- Deferred status clear
- Workflow can continue
- Will revisit when unblocked