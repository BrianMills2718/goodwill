# /load_phase_plans

Load the current development phase from phases.md and update CLAUDE.md with the active phase information.

## What This Command Does

1. Reads `docs/development_roadmap/phases.md` to find the current phase
2. Identifies the first unchecked task item (- [ ])
3. Updates CLAUDE.md with the current phase information
4. Sets the workflow state to begin exploration

## When to Use

- At the start of a new session
- After completing a phase
- When transitioning between phases

## Actions

1. Read phases.md and identify current phase
2. Update CLAUDE.md with phase details
3. Load any phase-specific requirements
4. Set workflow state to exploration
5. Report the loaded phase and next steps

## Next Command

After loading the phase, the next command will be `/explore` to begin understanding the requirements and codebase for that phase.