Run the core validation tests and analyze results. Focus on providing clear evidence of what's working vs broken.

## Test Execution Instructions

### 1. Run Core System Tests
Execute the fast core validation tests:
```bash
echo "🧪 RUNNING CORE TESTS"
echo "===================="
./run_core_tests.sh
```

### 2. Run MVP Workflow Validation  
Test the main pipeline functionality:
```bash
echo ""
echo "🔧 MVP WORKFLOW VALIDATION"
echo "========================="
python3 test_mvp_workflow.py
```

### 3. Evidence Collection
Create evidence file with test results:
```bash
echo ""
echo "📊 COLLECTING TEST EVIDENCE"
echo "=========================="

# Create evidence session
EVIDENCE_FILE="evidence/current/Evidence_Manual_Test_$(date +%Y%m%d_%H%M%S).md"

cat > "$EVIDENCE_FILE" << EOF
# Manual Test Execution Results

**Date**: $(date)
**Triggered**: Manual test run
**Context**: User-requested test validation

## Core Tests Results
\`\`\`
$(./run_core_tests.sh 2>&1)
\`\`\`

## MVP Workflow Results  
\`\`\`
$(python3 test_mvp_workflow.py 2>&1)
\`\`\`

## Analysis
- Core tests: $(./run_core_tests.sh 2>&1 | tail -1)
- MVP workflow: $(python3 test_mvp_workflow.py 2>&1 | grep -E "ALL TESTS|ISSUES FOUND|SUCCESS|FAILED" | tail -1)

## Recommendations
[Analyze results and provide next steps]
EOF

echo "✅ Evidence saved: $EVIDENCE_FILE"
```

### 4. Result Analysis
Analyze the test results and provide actionable feedback on what needs attention.