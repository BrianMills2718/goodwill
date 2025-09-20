Debug issue using systematic testing approach: $ARGUMENTS

## Quick Issue Diagnosis

### 1. Establish Baseline
```bash
echo "🔍 DEBUGGING: $ARGUMENTS"
echo "========================"

# Quick core validation
echo "Core system status:"
./run_core_tests.sh | tail -3

# MVP workflow check  
echo "MVP workflow status:"
python3 test_mvp_workflow.py | tail -5
```

### 2. Targeted Investigation
```bash
echo ""
echo "🎯 TARGETED TESTING"
echo "==================="

# Create specific test for the issue if needed
ISSUE_NAME=$(echo "$ARGUMENTS" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
TEST_FILE="tests/debug/test_${ISSUE_NAME}.py"

if [ ! -f "$TEST_FILE" ]; then
    echo "Creating debug test: $TEST_FILE"
    mkdir -p tests/debug
    cat > "$TEST_FILE" << EOF
#!/usr/bin/env python3
"""
Debug test for: $ARGUMENTS
Created: $(date)
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_${ISSUE_NAME}():
    """Reproduce and test fix for: $ARGUMENTS"""
    # TODO: Add specific reproduction steps
    print("Testing: $ARGUMENTS")
    
    # Add your test logic here
    assert True, "Replace with actual test"

if __name__ == "__main__":
    try:
        test_${ISSUE_NAME}()
        print("✅ Test passed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
EOF
    echo "📝 Edit $TEST_FILE to reproduce the issue"
else
    echo "Running existing debug test: $TEST_FILE"
    python3 "$TEST_FILE"
fi
```

### 3. Evidence Collection
```bash
echo ""
echo "📊 COLLECTING DEBUG EVIDENCE"
echo "==========================="

# Create evidence file
DEBUG_SESSION="logs/debug_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_SESSION"

echo "Debug session: $DEBUG_SESSION"

# Capture system state
echo "=== System State ===" > "$DEBUG_SESSION/debug_evidence.log"
echo "Issue: $ARGUMENTS" >> "$DEBUG_SESSION/debug_evidence.log"
echo "Date: $(date)" >> "$DEBUG_SESSION/debug_evidence.log"
echo "" >> "$DEBUG_SESSION/debug_evidence.log"

echo "=== Core Tests ===" >> "$DEBUG_SESSION/debug_evidence.log"
./run_core_tests.sh >> "$DEBUG_SESSION/debug_evidence.log" 2>&1

echo "=== MVP Workflow ===" >> "$DEBUG_SESSION/debug_evidence.log"
python3 test_mvp_workflow.py >> "$DEBUG_SESSION/debug_evidence.log" 2>&1

echo "Evidence saved: $DEBUG_SESSION/debug_evidence.log"
```

## Usage Examples
- `/debug-with-tests "CLI hanging on generation"`
- `/debug-with-tests "Import errors in component"`
- `/debug-with-tests "Blueprint parsing fails"`