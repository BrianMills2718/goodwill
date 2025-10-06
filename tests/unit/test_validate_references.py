#!/usr/bin/env python3
"""
Unit tests for validate_references.py

Tests the cross-reference validation functionality to ensure reliable
operation of this critical infrastructure tool.
"""

import os
import tempfile
import unittest
from pathlib import Path
import sys

# Add tools directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from validate_references import ReferenceValidator


class TestReferenceValidator(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.validator = ReferenceValidator(self.test_dir)
        
        # Create basic directory structure
        (self.test_path / "docs" / "behavior").mkdir(parents=True)
        (self.test_path / "docs" / "architecture").mkdir(parents=True)
        (self.test_path / "src").mkdir(parents=True)
        (self.test_path / "tools").mkdir(parents=True)
        (self.test_path / "logs" / "errors" / "active").mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test directory"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_valid_python_traceability(self):
        """Test validation of valid Python file with TRACEABILITY section"""
        # Create referenced files
        behavior_file = self.test_path / "docs" / "behavior" / "test.md"
        behavior_file.write_text("# Test behavior doc")
        
        # Create Python file with valid references
        py_file = self.test_path / "src" / "test.py"
        py_file.write_text('''"""
Test module

TRACEABILITY:
- Phase Plan: docs/behavior/test.md
- Architecture: docs/behavior/test.md
- Behavior: docs/behavior/test.md

CROSS-REFERENCES:
- Related Files: tools/test_tool.py
- Tests: None
- Config: None
"""

def test_function():
    pass
''')
        
        # Should find no broken references
        broken_refs = self.validator.validate_all_references()
        # Only broken ref should be the missing tools/test_tool.py
        self.assertEqual(len(broken_refs), 1)
        self.assertEqual(broken_refs[0]['target_path'], 'tools/test_tool.py')
    
    def test_broken_python_reference(self):
        """Test detection of broken reference in Python file"""
        py_file = self.test_path / "src" / "test.py"
        py_file.write_text('''"""
Test module

TRACEABILITY:
- Phase Plan: docs/missing/file.md
- Architecture: docs/architecture/missing.md
"""

def test_function():
    pass
''')
        
        broken_refs = self.validator.validate_all_references()
        self.assertEqual(len(broken_refs), 2)
        
        # Check that both missing files are detected
        missing_files = {ref['target_path'] for ref in broken_refs}
        self.assertIn('docs/missing/file.md', missing_files)
        self.assertIn('docs/architecture/missing.md', missing_files)
    
    def test_markdown_link_validation(self):
        """Test validation of markdown links"""
        # Create directory structure
        (self.test_path / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
        (self.test_path / "docs" / "behavior").mkdir(parents=True, exist_ok=True)
        (self.test_path / "src").mkdir(parents=True, exist_ok=True)
        
        # Create target file
        target_file = self.test_path / "docs" / "architecture" / "target.md"
        target_file.write_text("# Target doc")
        
        # Create markdown file with links
        md_file = self.test_path / "docs" / "behavior" / "test.md"
        md_file.write_text('''# Test Doc

[Valid Link](../architecture/target.md)
[Broken Link](../missing/file.md)

Implementation files:
- `src/existing.py` - Valid reference
- `src/missing.py` - Broken reference
''')
        
        # Create one of the referenced files
        (self.test_path / "src" / "existing.py").write_text("# Existing file")
        
        broken_refs = self.validator.validate_all_references()
        
        # Should find 2 broken references: missing/file.md and src/missing.py
        self.assertEqual(len(broken_refs), 2)
        broken_paths = {ref['target_path'] for ref in broken_refs}
        self.assertIn('docs/missing/file.md', broken_paths)  # Resolved from ../missing/file.md
        self.assertIn('src/missing.py', broken_paths)
    
    def test_ref_file_validation(self):
        """Test validation of .ref companion files"""
        # Create config directory and .ref file
        (self.test_path / "config").mkdir(parents=True, exist_ok=True)
        ref_file = self.test_path / "config" / "settings.json.ref"
        ref_file.write_text('''# Cross-References for settings.json

**Traceability:**
- Phase Plan: docs/behavior/valid.md
- Architecture: docs/missing/invalid.md

**Used By:**
- src/valid.py
- src/missing.py
''')
        
        # Create some of the referenced files
        (self.test_path / "docs" / "behavior" / "valid.md").write_text("# Valid")
        (self.test_path / "src" / "valid.py").write_text("# Valid")
        
        broken_refs = self.validator.validate_all_references()
        
        # Should find 2 broken references
        self.assertEqual(len(broken_refs), 2)
        broken_paths = {ref['target_path'] for ref in broken_refs}
        self.assertIn('docs/missing/invalid.md', broken_paths)
        self.assertIn('src/missing.py', broken_paths)
    
    def test_file_path_extraction(self):
        """Test extraction of file paths from text"""
        text = '''
        Phase Plan: /docs/behavior/test.md
        Architecture: docs/architecture/system.md
        Related: src/main.py
        Config: config/settings.json
        '''
        
        # Create the referenced files with directories
        (self.test_path / "docs" / "behavior").mkdir(parents=True, exist_ok=True)
        (self.test_path / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
        (self.test_path / "src").mkdir(parents=True, exist_ok=True)
        (self.test_path / "config").mkdir(parents=True, exist_ok=True)
        
        (self.test_path / "docs" / "behavior" / "test.md").write_text("# Test")
        (self.test_path / "docs" / "architecture" / "system.md").write_text("# System")
        (self.test_path / "src" / "main.py").write_text("# Main")
        (self.test_path / "config" / "settings.json").write_text("{}")
        
        self.validator._validate_references_in_text(text, self.test_path / "test.py")
        
        # Should find no broken references since all files exist
        self.assertEqual(len(self.validator.broken_refs), 0)
    
    def test_skip_patterns(self):
        """Test that certain files are skipped during validation"""
        # Create files in directories that should be skipped
        git_dir = self.test_path / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        (git_dir / "pre-commit").write_text("#!/bin/bash")
        
        cache_dir = self.test_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "test.pyc").write_text("compiled")
        
        # These should be skipped
        self.assertTrue(self.validator._should_skip_file(git_dir / "pre-commit"))
        self.assertTrue(self.validator._should_skip_file(cache_dir / "test.pyc"))
        
        # Regular files should not be skipped
        regular_file = self.test_path / "src" / "test.py"
        self.assertFalse(self.validator._should_skip_file(regular_file))
    
    def test_error_report_generation(self):
        """Test generation of detailed error reports"""
        # Create src directory and add some broken references
        (self.test_path / "src").mkdir(parents=True, exist_ok=True)
        test_file = self.test_path / "src" / "test.py"
        test_file.write_text("# Test file")
        
        self.validator._add_broken_ref(
            source_file=test_file,
            target_path="docs/missing.md",
            line_number=10,
            error_type="BROKEN_REFERENCE",
            details="Test error"
        )
        
        error_file = self.validator._generate_error_report()
        
        # Verify error file was created
        self.assertTrue(error_file.exists())
        
        # Verify content
        content = error_file.read_text()
        self.assertIn("CROSS-REFERENCE VALIDATION ERRORS", content)
        self.assertIn("src/test.py", content)
        self.assertIn("docs/missing.md", content)
        self.assertIn("RESOLUTION STEPS", content)
    
    def test_is_file_reference(self):
        """Test file reference detection"""
        # Valid file references
        self.assertTrue(self.validator._is_file_reference("docs/test.md"))
        self.assertTrue(self.validator._is_file_reference("src/main.py"))
        self.assertTrue(self.validator._is_file_reference("config/settings.json"))
        
        # Invalid file references (URLs, anchors, etc.)
        self.assertFalse(self.validator._is_file_reference("https://example.com"))
        self.assertFalse(self.validator._is_file_reference("#section"))
        self.assertFalse(self.validator._is_file_reference("mailto:test@example.com"))
        self.assertFalse(self.validator._is_file_reference("docs/directory/"))


if __name__ == '__main__':
    unittest.main()