# /run_tests

Run the test suite to verify implementation.

## What This Command Does

1. Executes all relevant tests
2. Reports pass/fail status
3. Identifies any failures
4. Documents test results
5. Determines if implementation is complete

## When to Use

- After implementing code
- To verify changes work correctly
- Before committing code
- When checking test coverage

## Actions

1. Identify test command (pytest, npm test, etc.)
2. Run the full test suite
3. Capture test output
4. Analyze failures if any
5. Document test results in evidence
6. Check test coverage if available

## Test Execution

```bash
# Python projects
pytest tests/ -v

# Node.js projects  
npm test

# Coverage reporting
pytest --cov=src tests/
```

## Evidence Collection

Document test results in: `investigations/[feature]/test_results.md`
- Test run output
- Pass/fail statistics
- Coverage percentage
- Any failing tests and reasons

## Next Steps Based on Results

- **All tests pass**: Proceed to `/doublecheck`
- **Tests failing**: Return to `/implement` to fix
- **New edge cases found**: Return to `/write_tests` to add more tests

## Success Criteria

- All tests passing
- Good test coverage (80%+ ideally)
- No regressions in existing tests
- Evidence of test results documented