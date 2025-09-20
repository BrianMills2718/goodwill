Run quick validation tests before/after changes: $ARGUMENTS

## Fast Pre-Change Validation
```bash
echo "⚡ QUICK TEST: $ARGUMENTS"
echo "========================"

# Core system health (10 seconds)
echo "Core system validation:"
./run_core_tests.sh

# Component import check (5 seconds)
echo ""
echo "Import validation:"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from autocoder_cc.core.config import Settings
    from autocoder_cc.components.registry import ComponentRegistry
    from autocoder_cc.blueprint_language.system_generator_refactored import SystemGenerator
    print('✅ Critical imports working')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Syntax check on recent changes
echo ""
echo "Syntax validation:"
find . -name "*.py" -mtime -1 -not -path "./archive/*" -exec python3 -m py_compile {} \; 2>&1 | head -10
echo "Recent Python files syntax: OK"
```

## Quick Post-Change Validation  
```bash
echo ""
echo "🔄 POST-CHANGE VALIDATION"
echo "========================="

# Re-run core tests
echo "Re-validating core system:"
./run_core_tests.sh | tail -3

# Check for new import issues
echo ""
echo "Checking for new issues:"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    # Test critical paths after changes
    from autocoder_cc.cli.main import main
    print('✅ CLI imports working')
except Exception as e:
    print(f'❌ CLI broken: {e}')
    sys.exit(1)
"
```

## Usage Examples
- `/quick-test "before refactoring component registry"`
- `/quick-test "after fixing import issues"`
- `/quick-test` (general validation)