# /categorize_uncertainties

Categorize uncertainties using LLM intelligence to determine resolution approach.

## What This Command Does

1. Analyzes current uncertainties intelligently
2. Categorizes by type (strategic, technical, external)
3. Determines appropriate resolution path
4. Documents categorization rationale

## When to Use

- When `/doublecheck` finds issues
- When stuck in implementation
- When requirements unclear
- Triggered by uncertainty detection

## Actions

1. List all current uncertainties
2. Use LLM understanding to categorize:
   - **Strategic**: Architecture/design decisions
   - **Technical**: Implementation approach
   - **External**: APIs, libraries, dependencies
3. Document each uncertainty's category
4. Determine resolution path

## Next Command Based on Category

- **Strategic** → `/review_architecture_behavior`
- **Technical** → `/investigate_pre_impl`
- **Loop detected** → `/escalate_to_deferred`
- **Resolved** → Return to previous command

## Success Criteria

- All uncertainties categorized
- Clear resolution path identified
- No ambiguity about next steps