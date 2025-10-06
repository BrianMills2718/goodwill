# Sandbox Test Task: Simple Math Utility

## Purpose
Test the autonomous TDD system with a simple, well-defined task before using it on complex eBay API integration.

## Task: Create Simple Math Utility Module

### Requirements
Create a `src/utils/math_helper.py` module with the following functions:

1. **`calculate_profit(selling_price, cost_price, fee_percentage=10.0)`**
   - Calculate profit after fees
   - Return net profit amount
   - Handle edge cases (negative prices, fees > 100%)

2. **`calculate_roi(profit, cost_price)`**
   - Calculate return on investment percentage  
   - Return ROI as decimal (0.25 for 25%)
   - Handle zero cost price edge case

3. **`format_currency(amount)`**
   - Format number as currency string  
   - Return "$XX.XX" format
   - Handle negative amounts with parentheses

### Success Criteria (TDD)
- [ ] All functions have comprehensive test coverage
- [ ] Tests written BEFORE implementation (TDD)
- [ ] All edge cases tested (negative values, zero, large numbers)
- [ ] Code follows project conventions
- [ ] Tests pass with 100% success rate
- [ ] Module properly documented with docstrings

### Expected Test Cases
```python
# test_math_helper.py examples
def test_calculate_profit_basic():
    assert calculate_profit(100.0, 75.0, 10.0) == 15.0  # $100 - $75 - $10 fee

def test_calculate_profit_no_profit():
    assert calculate_profit(50.0, 60.0, 10.0) == -15.0  # Loss scenario

def test_calculate_roi_positive():
    assert calculate_roi(25.0, 100.0) == 0.25  # 25% ROI

def test_format_currency_positive():
    assert format_currency(123.45) == "$123.45"

def test_format_currency_negative():
    assert format_currency(-50.0) == "($50.00)"
```

### Autonomous System Test Goals
1. **Workflow Progression**: Verify explore → write_tests → implement → run_tests → doublecheck → commit cycle
2. **Safety Mechanisms**: Ensure loop limits and stop-hook limits work
3. **Evidence Validation**: Test that evidence files are created and validated
4. **Cross-Session Memory**: Verify attempt history records successes and failures
5. **TDD Adherence**: Confirm tests are written before implementation

### How to Test
1. Update CLAUDE.md current_task to "sandbox_math_utility"
2. Set workflow state to "explore" 
3. Let autonomous system run through complete TDD cycle
4. Verify all safety mechanisms trigger appropriately
5. Check evidence files and attempt history updates

### Success Indicators
- Complete TDD cycle without infinite loops
- All tests pass at the end
- Code is clean and well-documented  
- Evidence files properly created
- Attempt history shows successful completion
- No safety limit violations

### Failure Recovery
If autonomous system gets stuck:
- Manual override file should stop the system
- Attempt history should record failure reasons
- Next session should avoid repeated failing strategies

This sandbox test provides a controlled environment to validate the autonomous TDD system before tackling the complex eBay API integration.