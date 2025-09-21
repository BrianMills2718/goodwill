# /explore_within_phase

## Concise Prompt
"Read relevant files for the current task in CLAUDE.md. Identify what we know, what we don't know, and what we need to discover. Do not write any code yet."

## Expanded Prompt (To be developed)
[Full prompt with specific file reading patterns, uncertainty detection templates, and discovery identification criteria]

## Prerequisites
- CLAUDE.md contains current task
- Phase is active (not completed)
- No blocking errors in CLAUDE.md

## Success Criteria  
- All relevant files read
- Known facts documented
- Unknowns identified
- Discoveries queued

## Uncertainty Detection
- Missing dependencies
- Unclear requirements  
- Unknown file locations
- Ambiguous behavior specifications

## Typical Next Command
- If unknowns exist: `/investigate_uncertainties_within_phase`
- If all clear: `/plan_within_phase`

## Hook Triggers
- SessionStart (if new session)
- PostToolUse after `/update_plans_within_phase`