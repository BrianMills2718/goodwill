#!/usr/bin/env python3
"""
Unit tests for inject_error.py

Tests the error injection functionality to ensure reliable operation
of this critical infrastructure tool.
"""

import os
import re
import tempfile
import unittest
from pathlib import Path
import sys

# Add tools directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from inject_error import ErrorInjector


class TestErrorInjector(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.injector = ErrorInjector(self.test_dir)
        
        # Create logs directory
        (self.test_path / "logs" / "errors" / "active").mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test directory"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_inject_basic_error(self):
        """Test basic error injection into new CLAUDE.md"""
        success = self.injector.inject_error(
            "TEST_ERROR",
            "Test error description",
            impact="Test impact",
            action="Test action"
        )
        
        self.assertTrue(success)
        
        # Verify CLAUDE.md was created
        claude_md = self.test_path / "CLAUDE.md"
        self.assertTrue(claude_md.exists())
        
        # Verify content
        content = claude_md.read_text()
        self.assertIn("🚨 ACTIVE ERRORS AND BLOCKERS", content)
        self.assertIn("Current Error Status: BLOCKED", content)
        self.assertIn("TEST_ERROR: Test error description", content)
        self.assertIn("Impact**: Test impact", content)
        self.assertIn("Action**: Test action", content)
    
    def test_inject_error_into_existing_claude_md(self):
        """Test error injection into existing CLAUDE.md"""
        # Create existing CLAUDE.md
        claude_md = self.test_path / "CLAUDE.md"
        claude_md.write_text("""# Existing Project

## Some Section
Content here

## Another Section
More content
""")
        
        success = self.injector.inject_error(
            "NEW_ERROR",
            "New error description"
        )
        
        self.assertTrue(success)
        
        # Verify error section was added
        content = claude_md.read_text()
        self.assertIn("🚨 ACTIVE ERRORS AND BLOCKERS", content)
        self.assertIn("NEW_ERROR: New error description", content)
        self.assertIn("# Existing Project", content)  # Original content preserved
    
    def test_inject_broken_reference_error(self):
        """Test specific broken reference error injection"""
        success = self.injector.inject_broken_reference_error(
            source_file="src/test.py",
            target_path="docs/missing.md",
            line_number=42,
            details="Reference not found"
        )
        
        self.assertTrue(success)
        
        # Verify CLAUDE.md content
        claude_md = self.test_path / "CLAUDE.md"
        content = claude_md.read_text()
        self.assertIn("BROKEN_REFERENCE: Reference to docs/missing.md not found", content)
        self.assertIn("Cross-reference broken in test.py", content)
        
        # Verify error log was created
        error_logs = list((self.test_path / "logs" / "errors" / "active").glob("*.log"))
        self.assertEqual(len(error_logs), 1)
        
        log_content = error_logs[0].read_text()
        self.assertIn("Source File: src/test.py", log_content)
        self.assertIn("Line Number: 42", log_content)
        self.assertIn("Target Path: docs/missing.md", log_content)
        self.assertIn("RESOLUTION STEPS", log_content)
    
    def test_inject_file_move_error(self):
        """Test file move error injection"""
        success = self.injector.inject_file_move_error(
            old_path="docs/old_file.md",
            new_path="docs/new_file.md"
        )
        
        self.assertTrue(success)
        
        # Verify CLAUDE.md content
        claude_md = self.test_path / "CLAUDE.md"
        content = claude_md.read_text()
        self.assertIn("REFERENCE_UPDATE_NEEDED: File moved requires reference updates", content)
        self.assertIn("**Details**: docs/old_file.md → docs/new_file.md", content)
        
        # Verify error log resolution steps
        error_logs = list((self.test_path / "logs" / "errors" / "active").glob("*.log"))
        log_content = error_logs[0].read_text()
        self.assertIn("Search for references to: docs/old_file.md", log_content)
        self.assertIn("Replace with: docs/new_file.md", log_content)
    
    def test_inject_import_error(self):
        """Test import error injection"""
        success = self.injector.inject_import_error(
            source_file="src/main.py",
            import_name="missing_module",
            error_details="ModuleNotFoundError: No module named 'missing_module'"
        )
        
        self.assertTrue(success)
        
        # Verify CLAUDE.md content
        claude_md = self.test_path / "CLAUDE.md"
        content = claude_md.read_text()
        self.assertIn("IMPORT_ERROR: Import failed: missing_module", content)
        self.assertIn("Code execution blocked in main.py", content)
        
        # Verify error log
        error_logs = list((self.test_path / "logs" / "errors" / "active").glob("*.log"))
        log_content = error_logs[0].read_text()
        self.assertIn("ModuleNotFoundError", log_content)
        self.assertIn("Check import path syntax", log_content)
    
    def test_multiple_error_injection(self):
        """Test injecting multiple errors"""
        # Inject first error
        self.injector.inject_error("ERROR_1", "First error")
        
        # Inject second error
        self.injector.inject_error("ERROR_2", "Second error")
        
        # Verify both errors in CLAUDE.md
        claude_md = self.test_path / "CLAUDE.md"
        content = claude_md.read_text()
        self.assertIn("ERROR_1: First error", content)
        self.assertIn("ERROR_2: Second error", content)
        
        # Verify two log files created
        error_logs = list((self.test_path / "logs" / "errors" / "active").glob("*.log"))
        self.assertEqual(len(error_logs), 2)
    
    def test_remove_error(self):
        """Test removing an error and moving to resolved section"""
        # First inject an error
        self.injector.inject_error("TEST_ERROR", "Test error to remove")
        
        claude_md = self.test_path / "CLAUDE.md"
        content = claude_md.read_text()
        
        # Extract timestamp from the error entry
        import re
        timestamp_match = re.search(r'\*\*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\*\*', content)
        self.assertIsNotNone(timestamp_match)
        timestamp = timestamp_match.group(1)
        
        # Remove the error
        success = self.injector.remove_error(timestamp, "Fixed the test error")
        self.assertTrue(success)
        
        # Verify error moved to resolved section
        content = claude_md.read_text()
        self.assertNotIn("### Active Errors:\n- **" + timestamp, content)
        self.assertIn("Recently Resolved Errors:", content)
        self.assertIn("✅ RESOLVED", content)
        self.assertIn("Fixed the test error", content)
        
        # Verify status changed to CLEAR if no more active errors
        self.assertIn("Current Error Status: CLEAR", content)
    
    def test_error_status_management(self):
        """Test error status changes (CLEAR/BLOCKED)"""
        claude_md = self.test_path / "CLAUDE.md"
        
        # Initially create CLAUDE.md with CLEAR status
        claude_md.write_text("""# Test Project

## 🚨 ACTIVE ERRORS AND BLOCKERS

### Current Error Status: CLEAR

### Active Errors:
(None currently)
""")
        
        # Inject error - should change to BLOCKED
        self.injector.inject_error("TEST_ERROR", "Test error")
        
        content = claude_md.read_text()
        self.assertIn("Current Error Status: BLOCKED", content)
        
        # Remove error - should change back to CLEAR
        timestamp_match = re.search(r'\*\*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\*\*', content)
        timestamp = timestamp_match.group(1)
        
        self.injector.remove_error(timestamp, "Fixed")
        
        content = claude_md.read_text()
        self.assertIn("Current Error Status: CLEAR", content)
    
    def test_error_log_structure(self):
        """Test detailed error log file structure"""
        self.injector.inject_broken_reference_error(
            source_file="src/test.py",
            target_path="docs/missing.md",
            line_number=42,
            details="Detailed error information"
        )
        
        # Check log file structure
        error_logs = list((self.test_path / "logs" / "errors" / "active").glob("*.log"))
        self.assertEqual(len(error_logs), 1)
        
        log_content = error_logs[0].read_text()
        
        # Verify required sections
        self.assertIn("=== ERROR DETAILS ===", log_content)
        self.assertIn("=== RESOLUTION STEPS ===", log_content)
        self.assertIn("Type: BROKEN_REFERENCE", log_content)
        self.assertIn("Source File: src/test.py", log_content)
        self.assertIn("Line Number: 42", log_content)
        self.assertIn("Target Path: docs/missing.md", log_content)
        self.assertIn("Detailed error information", log_content)
        
        # Verify resolution steps are specific to error type
        self.assertIn("Check if referenced file was moved", log_content)
        self.assertIn("Update cross-reference to correct path", log_content)
        self.assertIn("Run tools/validate_references.py", log_content)
    
    def test_create_error_entry(self):
        """Test error entry creation with various fields"""
        error_entry = self.injector._create_error_entry(
            "CUSTOM_ERROR",
            "Custom error description",
            source_file="src/test.py",
            impact="Custom impact",
            action="Custom action",
            status="INVESTIGATING",
            custom_field="custom_value"
        )
        
        self.assertEqual(error_entry['error_type'], "CUSTOM_ERROR")
        self.assertEqual(error_entry['description'], "Custom error description")
        self.assertEqual(error_entry['source_file'], "src/test.py")
        self.assertEqual(error_entry['impact'], "Custom impact")
        self.assertEqual(error_entry['action'], "Custom action")
        self.assertEqual(error_entry['status'], "INVESTIGATING")
        self.assertEqual(error_entry['custom_field'], "custom_value")
        self.assertIn('timestamp', error_entry)
    
    def test_format_error_entry(self):
        """Test error entry formatting for CLAUDE.md"""
        error_entry = {
            'timestamp': '2024-01-15 14:30',
            'error_type': 'TEST_ERROR',
            'description': 'Test description',
            'impact': 'Test impact',
            'action': 'Test action',
            'status': 'NEEDS_FIX'
        }
        
        log_file = self.test_path / "logs" / "errors" / "active" / "test.log"
        log_file.write_text("Test log")
        
        formatted = self.injector._format_error_entry(error_entry, log_file)
        
        self.assertIn("**2024-01-15 14:30** TEST_ERROR: Test description", formatted)
        self.assertIn("**Impact**: Test impact", formatted)
        self.assertIn("**Log**: `logs/errors/active/test.log`", formatted)
        self.assertIn("**Action**: Test action", formatted)
        self.assertIn("**Status**: NEEDS_FIX", formatted)


if __name__ == '__main__':
    unittest.main()