# /doublecheck

Double-check implementation against requirements and edge cases.

## What This Command Does

1. Verifies implementation meets all requirements
2. Checks for edge cases and error handling
3. Reviews code quality and patterns
4. Validates against original phase goals
5. Ensures documentation is complete

## When to Use

- After all tests pass
- Before marking feature complete
- To validate implementation quality
- When verifying phase requirements

## Actions

1. Review original requirements from phases.md
2. Check all acceptance criteria are met
3. Test edge cases manually if needed
4. Review code for quality issues
5. Verify error handling is robust
6. Check documentation is updated
7. Create verification evidence

## Verification Checklist

- [ ] All phase requirements implemented
- [ ] Tests comprehensive and passing
- [ ] Edge cases handled properly
- [ ] Error messages helpful
- [ ] Code follows project patterns
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance acceptable

## Evidence Collection

Create: `investigations/[feature]/verification_evidence.md`
- Requirements checklist
- Edge cases tested
- Quality review notes
- Any remaining concerns

## Next Steps

- **All verified**: Proceed to `/commit`
- **Issues found**: Return to `/write_tests` or `/implement`
- **Phase complete**: Consider `/close_phase`

## Success Criteria

- All requirements verified
- No critical issues found
- Evidence documented
- Ready for commit