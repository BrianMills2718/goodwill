# TDD Workflow Commands

## Main Workflow Sequence

The autonomous TDD workflow follows this sequence:

1. **`/load_phase_plans`** - Load current phase from phases.md
2. **`/explore`** - Understand requirements and codebase
3. **`/write_tests`** - Write tests first (TDD red phase)
4. **`/implement`** - Write code to pass tests (TDD green phase)
5. **`/run_tests`** - Verify tests pass
6. **`/doublecheck`** - Verify against requirements
7. **`/commit`** - Commit with evidence

## Support Commands

- **`/investigate_uncertainties`** - Research unknowns (when stuck)
- **`/resolve_blockers`** - Fix blocking issues
- **`/close_phase`** - Complete phase and transition

## Command Flow

```
/load_phase_plans
    ↓
/explore
    ↓
/write_tests ←─────┐
    ↓              │
/implement         │ (if tests fail)
    ↓              │
/run_tests ────────┘
    ↓ (if tests pass)
/doublecheck
    ↓
/commit
    ↓
(repeat or /close_phase)
```

## Automation

The workflow is automated through:
1. Stop hooks that run `workflow_orchestrator.py`
2. Orchestrator updates CLAUDE.md with next command
3. Claude sees instruction in CLAUDE.md and executes
4. Process repeats automatically

## Evidence Structure

Each command creates evidence in:
```
investigations/[feature]/
├── exploration_notes.md
├── test_design.md
├── implementation_evidence.md
├── test_results.md
└── verification_evidence.md
```

Evidence is archived to `/home/brian/projects/archive/goodwill/` when phases complete.