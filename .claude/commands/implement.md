# /implement

Implement the code to make tests pass following TDD approach.

## What This Command Does

1. Reads failing tests to understand requirements
2. Implements minimal code to pass tests
3. Follows existing code patterns
4. Documents implementation decisions
5. Creates evidence of implementation

## When to Use

- After writing tests (`/write_tests`)
- When tests are failing and need implementation
- To add functionality defined by tests

## Actions

1. Run tests to see what's failing
2. Implement the minimal code to make tests pass
3. Follow existing patterns in the codebase
4. Add appropriate error handling
5. Document complex logic if needed
6. Ensure code follows project style guide
7. Create implementation evidence in investigations/

## TDD Implementation Guidelines

- **Red**: Start with failing tests
- **Green**: Write just enough code to pass
- **Refactor**: Clean up while keeping tests green
- Don't over-engineer
- Follow YAGNI (You Aren't Gonna Need It)
- Make it work first, then make it clean

## Evidence Collection

Create evidence file: `investigations/[feature]/implementation_evidence.md`
- What was implemented
- Which tests now pass
- Design decisions made
- Any discoveries or issues

## Next Command

After implementation, proceed to `/run_tests` to verify all tests pass.