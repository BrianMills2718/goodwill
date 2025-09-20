Investigate and debug failing tests with systematic analysis. Focus on identifying root causes and actionable fixes.

## Debug Investigation Process

### 1. Identify Failing Tests
Run tests with verbose output to see what's failing:
```bash
echo "🔍 IDENTIFYING TEST FAILURES"
echo "============================"

# Run core tests with detailed output
echo "Core test failures:"
./run_core_tests.sh 2>&1 | grep -E "FAILED|ERROR|❌"

# Run MVP workflow with verbose output  
echo ""
echo "MVP workflow failures:"
python3 test_mvp_workflow.py 2>&1 | grep -E "FAILED|ERROR|❌|Exception"
```

### 2. Systematic Root Cause Analysis
For each failing test, investigate the underlying issue:
```bash
echo ""
echo "🔧 ROOT CAUSE ANALYSIS"
echo "====================="

# Check for import errors
echo "Checking for import issues:"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from autocoder_cc.core.config import Settings
    from autocoder_cc.components.registry import ComponentRegistry  
    from autocoder_cc.blueprint_language.system_generator_refactored import SystemGenerator
    print('✅ Core imports working')
except ImportError as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
"

# Check for configuration issues
echo ""
echo "Checking configuration:"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from autocoder_cc.core.config import Settings
    settings = Settings()
    print(f'✅ Settings loaded: {settings}')
except Exception as e:
    print(f'❌ Config error: {e}')
    import traceback
    traceback.print_exc()
"
```

### 3. Create Debug Evidence
Document the investigation with full details:
```bash
echo ""
echo "📋 CREATING DEBUG EVIDENCE"
echo "========================="

DEBUG_SESSION="logs/debug_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_SESSION"

# Capture detailed test output
echo "Capturing detailed test results..."
./run_core_tests.sh > "$DEBUG_SESSION/core_tests_detailed.log" 2>&1
python3 test_mvp_workflow.py > "$DEBUG_SESSION/mvp_workflow_detailed.log" 2>&1

# Create evidence file
EVIDENCE_FILE="evidence/current/Evidence_Debug_Investigation_$(date +%Y%m%d_%H%M%S).md"

cat > "$EVIDENCE_FILE" << EOF
# Debug Investigation: Test Failures

**Date**: $(date)
**Debug Session**: $DEBUG_SESSION
**Context**: Systematic test failure analysis

## Test Failure Summary
$(./run_core_tests.sh 2>&1 | grep -E "FAILED|ERROR|❌" | head -10)

## Root Cause Analysis
[Add analysis of why tests are failing]

## Detailed Logs
- Core tests: $DEBUG_SESSION/core_tests_detailed.log
- MVP workflow: $DEBUG_SESSION/mvp_workflow_detailed.log

## Recommended Fixes
[Provide specific actionable steps to fix the issues]

## Next Steps
[Outline what should be done next]
EOF

echo "✅ Debug evidence: $EVIDENCE_FILE"
echo "✅ Detailed logs: $DEBUG_SESSION/"
```

### 4. Provide Fix Recommendations
Based on the investigation, provide specific steps to resolve the issues and get tests passing.