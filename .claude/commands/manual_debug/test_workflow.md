Run focused test workflow for MVP development: $ARGUMENTS

## Quick MVP Test Workflow

### 1. Core System Validation (10 seconds)
```bash
echo "🧪 CORE SYSTEM VALIDATION"
echo "========================"
./run_core_tests.sh
```

### 2. MVP Workflow Test (2 minutes) 
```bash
echo ""
echo "🔧 MVP WORKFLOW VALIDATION"
echo "========================="
python3 test_mvp_workflow.py
```

### 3. Targeted Pain Point Test (if needed)
If core tests pass but specific workflow fails:
```bash
echo ""
echo "🎯 TARGETED TESTING: $ARGUMENTS"
echo "=============================="

# Create test for specific issue if it doesn't exist
TEST_FILE="tests/core/test_$(echo $ARGUMENTS | tr ' ' '_' | tr '[:upper:]' '[:lower:]').py"

if [ ! -f "$TEST_FILE" ]; then
    echo "Creating targeted test: $TEST_FILE"
    cat > "$TEST_FILE" << EOF
#!/usr/bin/env python3
"""
Targeted test for: $ARGUMENTS
Created: $(date)
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_${ARGUMENTS// /_}():
    """Test specific issue: $ARGUMENTS"""
    # TODO: Implement specific test for this issue
    assert True, "Test needs implementation"

if __name__ == "__main__":
    print("Testing: $ARGUMENTS")
    try:
        test_${ARGUMENTS// /_}()
        print("✅ Test passed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
EOF
    echo "Created: $TEST_FILE"
    echo "Edit test and run: python3 $TEST_FILE"
else
    echo "Running existing test: $TEST_FILE"
    python3 "$TEST_FILE"
fi
```

### 4. Evidence Collection
```bash
echo ""
echo "📊 TEST EVIDENCE COLLECTION"
echo "=========================="

# Create evidence file for test results
EVIDENCE_FILE="evidence/current/Evidence_Testing_$(date +%Y%m%d_%H%M%S).md"
echo "Creating: $EVIDENCE_FILE"

cat > "$EVIDENCE_FILE" << EOF
# Test Evidence: $ARGUMENTS

**Date**: $(date)
**Test Type**: MVP Development Workflow
**Context**: $ARGUMENTS

## Core System Validation
\`\`\`
$(./run_core_tests.sh 2>&1)
\`\`\`

## MVP Workflow Test
\`\`\`
$(python3 test_mvp_workflow.py 2>&1)
\`\`\`

## Summary
- Core tests: $(./run_core_tests.sh 2>&1 | grep -E "PASSED|FAILED" | tail -1)
- MVP workflow: $(python3 test_mvp_workflow.py 2>&1 | grep -E "ALL TESTS|ISSUES FOUND" | tail -1)

## Action Items
[Document any issues found and next steps]
EOF

echo "Evidence saved: $EVIDENCE_FILE"
```

## Usage Examples
- `/test-workflow "CLI hanging issues"`
- `/test-workflow "Blueprint generation"`  
- `/test-workflow "Component integration"`
- `/test-workflow` (run full validation)