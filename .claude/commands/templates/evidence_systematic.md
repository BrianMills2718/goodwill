# Evidence Template: [Task Name]

**Date**: $(date)
**Phase**: [Current Phase from CLAUDE.md]
**Task**: [Specific task being validated]
**Status**: [IN_PROGRESS/COMPLETE/BLOCKED]

---

## 🎯 OBJECTIVE

**What was the goal?**
[Clear statement of what was supposed to be accomplished]

**Success criteria:**
- [ ] [Specific measurable criterion 1]
- [ ] [Specific measurable criterion 2]
- [ ] [Specific measurable criterion 3]

---

## 🔧 IMPLEMENTATION

### Commands Executed
```bash
# All commands run during this task
[command 1] 2>&1 | tee "logs/debug_[timestamp]/[task].log"
[command 2] 2>&1 | tee "logs/debug_[timestamp]/[task2].log"
```

### Files Modified
- `[file_path]:[line_numbers]` - [description of change]
- `[file_path]:[line_numbers]` - [description of change]

### Key Changes Made
[Brief description of the actual changes implemented]

---

## 📊 TEST RESULTS

### Baseline Test (Before Changes)
```bash
# Command run to establish baseline
[test_command]
```

**Result**: [PASS/FAIL]
**Output**:
```
[complete output from baseline test]
```

### Validation Test (After Changes) 
```bash
# Command run to validate fix
[test_command]
```

**Result**: [PASS/FAIL]
**Output**:
```
[complete output from validation test]
```

### Regression Test
```bash
# Command to ensure no regressions
./run_core_tests.sh
```

**Result**: [PASS/FAIL]
**Summary**: [brief summary of results]

---

## 🔍 ANALYSIS

### What This Proves
[Analysis of what the test results demonstrate about the system]

### Root Cause (if issue found)
[Explanation of the underlying cause of any problems]

### Fix Validation
[Explanation of how the results prove the fix works]

---

## ✅ VERIFICATION

### Manual Verification Steps
1. [Step 1]: [Result]
2. [Step 2]: [Result]
3. [Step 3]: [Result]

### End-to-End Test
```bash
# Complete workflow test
[e2e_test_command]
```

**Working Example Location**: [path to working example if created]

---

## 📁 ARTIFACTS

### Log Files
- `logs/debug_[timestamp]/[task].log` - [description]
- `logs/debug_[timestamp]/[task2].log` - [description]

### Generated Files  
- `[path]` - [description]
- `[path]` - [description]

### Evidence Files
- `[this_file]` - This evidence document

---

## 🚀 COMPLETION STATUS

### Success Criteria Review
- [✅/❌] [Criterion 1]: [Evidence]
- [✅/❌] [Criterion 2]: [Evidence]  
- [✅/❌] [Criterion 3]: [Evidence]

### Overall Assessment
**Status**: [COMPLETE/PARTIAL/FAILED]
**Confidence**: [HIGH/MEDIUM/LOW]

### Next Actions Required
[What needs to happen next based on these results]

---

## 📝 NOTES

### Unexpected Findings
[Any surprises or unexpected results during implementation]

### Technical Debt Created
[Any shortcuts or technical debt that should be addressed later]

### Lessons Learned
[Key insights that could help with future similar tasks]

---

**Evidence Quality**: [COMPLETE/INCOMPLETE] - All required test output captured with full visibility