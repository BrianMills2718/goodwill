Run systematic debugging workflow for hanging or error issues: $ARGUMENTS

## Debug Session Setup

Create organized debug session for issue investigation:

```bash
# Create debug session (choose location based on issue scope)
ISSUE_NAME=$(echo "$ARGUMENTS" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

# For specific issue investigation
DEBUG_SESSION="investigation/debug_${ISSUE_NAME}/session_$(date +%Y%m%d_%H%M%S)"

# For general system debugging  
# DEBUG_SESSION="logs/debug_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$DEBUG_SESSION"
cd "$DEBUG_SESSION"
```

## Core Debug Workflow

### 1. LLM and System Connectivity
```bash
# Test basic LLM connectivity
export PYTHONPATH=/home/brian/projects/autocoder4_cc
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
try:
    from autocoder_cc.llm_providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider()
    print('✅ LLM provider initialized')
except Exception as e:
    print(f'❌ LLM provider failed: {e}')
" 2>&1 | tee llm_connectivity.log

# Test system generator
python3 -c "
from autocoder_cc.blueprint_language.system_generator_refactored import SystemGenerator
sg = SystemGenerator()
print('✅ System generator OK')
" 2>&1 | tee system_generator.log
```

### 2. Blueprint Processing Debug
```bash
# Test blueprint parsing
cat > test_blueprint.yaml << 'EOF'
name: debug_test
version: "1.0.0"
components:
  - name: simple_test
    type: Source
    description: Basic test component
EOF

# Test generation with timeout
timeout 60s python3 /home/brian/projects/autocoder4_cc/autocoder_cc/cli/main.py generate \
  -b test_blueprint.yaml \
  -o debug_output 2>&1 | tee generation_debug.log

# Check what was generated
if [ -d debug_output ]; then
    find debug_output -type f -name "*.py" | head -5 | tee generated_files.log
    echo "Generation: SUCCESS" >> debug_summary.log
else
    echo "Generation: FAILED" >> debug_summary.log
fi
```

### 3. Component System Debug
```bash
# Test component registry
python3 -c "
from autocoder_cc.components.component_registry import component_registry
try:
    comp = component_registry.create_component('Source', 'test', {})
    print(f'✅ Component created: {comp.__class__.__name__}')
except Exception as e:
    print(f'❌ Component creation failed: {e}')
" 2>&1 | tee component_debug.log

# Test recipe system
python3 -c "
from autocoder_cc.recipes.registry import RECIPE_REGISTRY
print(f'Recipes available: {len(RECIPE_REGISTRY)}')
print(f'Recipe types: {list(RECIPE_REGISTRY.keys())[:5]}')
" 2>&1 | tee recipe_debug.log
```

### 4. Error Analysis
```bash
# Aggregate error patterns
grep -E "ERROR|FAILED|Exception|Traceback" *.log > error_patterns.log 2>/dev/null || true
grep -E "timeout|hang|stuck" *.log > timeout_patterns.log 2>/dev/null || true
grep -E "import|module|ModuleNotFound" *.log > import_issues.log 2>/dev/null || true

# Create debug summary
cat > debug_summary.log << EOF
Debug Session: $(date)
Issue: $ARGUMENTS
Session: $DEBUG_SESSION

=== COMPONENT STATUS ===
LLM Provider: $(grep -q "LLM provider initialized" llm_connectivity.log && echo "OK" || echo "FAILED")
System Generator: $(grep -q "System generator OK" system_generator.log && echo "OK" || echo "FAILED")
Blueprint Generation: $(grep -q "SUCCESS" debug_summary.log && echo "OK" || echo "FAILED")
Component Registry: $(grep -q "Component created" component_debug.log && echo "OK" || echo "FAILED")

=== ERROR SUMMARY ===
$(wc -l error_patterns.log 2>/dev/null | cut -d' ' -f1 || echo "0") total errors found
$(wc -l timeout_patterns.log 2>/dev/null | cut -d' ' -f1 || echo "0") timeout/hang issues
$(wc -l import_issues.log 2>/dev/null | cut -d' ' -f1 || echo "0") import issues

=== NEXT STEPS ===
$(if [ -s error_patterns.log ]; then echo "- Review error_patterns.log for specific failures"; fi)
$(if [ -s timeout_patterns.log ]; then echo "- Investigate timeout_patterns.log for hanging issues"; fi)
$(if [ -s import_issues.log ]; then echo "- Fix import_issues.log dependency problems"; fi)
EOF
```

### 5. Advanced Debugging (If Needed)

For persistent issues, run targeted analysis:

```bash
# Process monitoring for hangs
if grep -q "timeout\|hang" *.log; then
    echo "=== HANG ANALYSIS ===" >> debug_summary.log
    ps aux | grep python > process_status.log
    netstat -tlnp | grep python > network_status.log
fi

# Memory and resource analysis
if grep -q "Memory\|Resource" *.log; then
    echo "=== RESOURCE ANALYSIS ===" >> debug_summary.log
    free -h > memory_status.log
    df -h > disk_status.log
fi

# LLM API analysis
if grep -q "API\|OpenAI\|provider" *.log; then
    echo "=== API ANALYSIS ===" >> debug_summary.log
    curl -s https://status.openai.com/api/v2/status.json | jq '.status.description' > api_status.log 2>/dev/null || echo "API status check failed"
fi
```

## Evidence Creation

Document debug session results:

```bash
# Create evidence file
EVIDENCE_FILE="/home/brian/projects/autocoder4_cc/evidence/current/Evidence_Debug_$(date +%Y%m%d)_${ISSUE_NAME}.md"

cat > "$EVIDENCE_FILE" << EOF
# Debug Evidence: $ARGUMENTS

**Date**: $(date)
**Session**: $DEBUG_SESSION
**Issue**: $ARGUMENTS

## Debug Summary
$(cat debug_summary.log)

## Key Log Files
- llm_connectivity.log - LLM provider testing
- system_generator.log - System generator testing  
- generation_debug.log - Blueprint generation testing
- component_debug.log - Component registry testing
- error_patterns.log - Aggregated error analysis
- debug_summary.log - Session summary

## Findings
[Document specific issues found]

## Resolution Steps
[Document what needs to be fixed]

## Testing Results
[Document any fixes tested]
EOF
```

## Success Criteria

- [ ] Debug session created with organized file structure
- [ ] Core system components tested (LLM, generator, components)
- [ ] Error patterns identified and categorized
- [ ] Debug summary created with status and next steps
- [ ] Evidence file created with findings and recommendations

## Usage Notes

- **Issue-Specific**: Debug session organized around specific problem
- **Systematic**: Tests core components in logical order
- **Evidence-Based**: All findings documented with log files
- **Actionable**: Provides clear next steps based on findings