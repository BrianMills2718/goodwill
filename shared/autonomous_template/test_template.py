#!/usr/bin/env python3
"""
Test script to validate the autonomous TDD template
"""

import tempfile
import subprocess
import sys
from pathlib import Path

def test_template_setup():
    """Test that template can be set up in a new project"""
    
    print("Testing autonomous TDD template...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_project"
        test_project.mkdir()
        
        # Run setup script
        template_dir = Path(__file__).parent
        setup_script = template_dir / "setup.py"
        
        result = subprocess.run([
            sys.executable, str(setup_script), 
            str(test_project), 
            "--project-name", "TestProject"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Setup failed: {result.stderr}")
            return False
        
        # Verify key files were created
        required_files = [
            ".claude/hooks/autonomous_tdd.py",
            ".claude/settings.json", 
            "tools/workflow/evidence_validator.py",
            "tools/workflow/state_reconciliation.py",
            "CLAUDE.md",
            "docs/behavior/desired_behavior.md"
        ]
        
        for file_path in required_files:
            full_path = test_project / file_path
            if not full_path.exists():
                print(f"❌ Missing file: {file_path}")
                return False
            else:
                print(f"✅ Found: {file_path}")
        
        # Verify CLAUDE.md was customized
        claude_md = test_project / "CLAUDE.md"
        content = claude_md.read_text()
        if "TESTPROJECT" in content:
            print("✅ CLAUDE.md customized with project name")
        else:
            print("❌ CLAUDE.md not customized")
            return False
        
        print("✅ Template setup test passed!")
        return True

def test_hook_syntax():
    """Test that autonomous hook has valid Python syntax"""
    
    template_dir = Path(__file__).parent
    hook_file = template_dir / ".claude" / "hooks" / "autonomous_tdd.py"
    
    if not hook_file.exists():
        print("❌ Hook file not found")
        return False
    
    # Try to compile the hook file
    try:
        with open(hook_file) as f:
            code = f.read()
        compile(code, str(hook_file), 'exec')
        print("✅ Hook file has valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"❌ Hook file syntax error: {e}")
        return False

def main():
    """Run all template tests"""
    
    print("=== Autonomous TDD Template Validation ===\n")
    
    tests = [
        ("Hook Syntax", test_hook_syntax),
        ("Template Setup", test_template_setup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All template validation tests passed!")
        print("\nTemplate is ready for use!")
        return True
    else:
        print("⚠️  Some tests failed - template may need fixes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)