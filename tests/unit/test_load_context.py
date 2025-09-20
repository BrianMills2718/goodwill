#!/usr/bin/env python3
"""
Unit tests for load_context.py

Tests the context loading functionality to ensure reliable operation
of this critical infrastructure tool.
"""

import os
import tempfile
import unittest
from pathlib import Path
import sys

# Add tools directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from load_context import ContextLoader


class TestContextLoader(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.loader = ContextLoader(self.test_dir)
        
        # Create basic directory structure
        (self.test_path / "docs" / "behavior").mkdir(parents=True)
        (self.test_path / "docs" / "architecture").mkdir(parents=True)
        (self.test_path / "docs" / "development_roadmap").mkdir(parents=True)
        (self.test_path / "src").mkdir(parents=True)
        (self.test_path / "tools").mkdir(parents=True)
        (self.test_path / "tests" / "unit").mkdir(parents=True)
        (self.test_path / "config").mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test directory"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_load_context_for_python_file(self):
        """Test loading context for Python file with TRACEABILITY"""
        # Create referenced files
        behavior_file = self.test_path / "docs" / "behavior" / "requirements.md"
        behavior_file.write_text("# Requirements doc")
        
        arch_file = self.test_path / "docs" / "architecture" / "design.md" 
        arch_file.write_text("# Design doc")
        
        phase_file = self.test_path / "docs" / "development_roadmap" / "phase1.md"
        phase_file.write_text("# Phase 1")
        
        related_file = self.test_path / "src" / "helper.py"
        related_file.write_text("# Helper module")
        
        # Create target Python file
        target_file = self.test_path / "src" / "main.py"
        target_file.write_text('''"""
Main module

TRACEABILITY:
- Phase Plan: docs/development_roadmap/phase1.md
- Architecture: docs/architecture/design.md
- Behavior: docs/behavior/requirements.md

CROSS-REFERENCES:
- Related Files: src/helper.py
- Tests: tests/unit/test_main.py
- Config: config/settings.json

DEPENDENCIES:
- Imports: os, sys, json
- Imported By: None
- Planning: None
"""

import os
import sys

def main():
    pass
''')
        
        # Create config file
        config_file = self.test_path / "config" / "settings.json"
        config_file.write_text('{"test": true}')
        
        context = self.loader.load_full_context("src/main.py")
        
        # Verify context structure
        self.assertEqual(context['target_file'], "src/main.py")
        self.assertEqual(context['file_type'], ".py")
        
        # Verify cross-references were found
        refs = context['cross_references']
        self.assertIn("docs/behavior/requirements.md", refs['behavior_docs'])
        self.assertIn("docs/architecture/design.md", refs['architecture_docs'])
        self.assertIn("docs/development_roadmap/phase1.md", refs['phase_plans'])
        self.assertIn("src/helper.py", refs['related_files'])
        
        # Verify full texts were loaded
        self.assertIn("docs/behavior/requirements.md", context['full_texts'])
        self.assertIn("# Requirements doc", context['full_texts']['docs/behavior/requirements.md'])
    
    def test_load_context_for_markdown_file(self):
        """Test loading context for Markdown file with cross-references"""
        # Create referenced files
        arch_file = self.test_path / "docs" / "architecture" / "system.md"
        arch_file.write_text("# System architecture")
        
        impl_file = self.test_path / "src" / "implementation.py"
        impl_file.write_text("# Implementation")
        
        # Create target markdown file
        target_file = self.test_path / "docs" / "development_roadmap" / "phase1.md"
        target_file.write_text('''# Phase 1 Plan

## Implementation Files
- `src/implementation.py` - Main implementation
- `src/missing.py` - This file doesn't exist

## Related Architecture
[System Design](../architecture/system.md)

## Dependencies
This phase depends on completing the design phase.
''')
        
        context = self.loader.load_full_context("docs/development_roadmap/phase1.md")
        
        # Verify cross-references
        refs = context['cross_references']
        self.assertIn("docs/architecture/system.md", refs['architecture_docs'])
        self.assertIn("src/implementation.py", refs['related_files'])
        
        # Verify full text loading
        self.assertIn("docs/architecture/system.md", context['full_texts'])
        self.assertIn("# System architecture", context['full_texts']['docs/architecture/system.md'])
    
    def test_load_context_with_ref_file(self):
        """Test loading context using .ref companion file"""
        # Create target JSON file and its .ref companion
        json_file = self.test_path / "config" / "settings.json"
        json_file.write_text('{"setting": "value"}')
        
        ref_file = self.test_path / "config" / "settings.json.ref"
        ref_file.write_text('''# Cross-References for settings.json

**Traceability:**
- Phase Plan: docs/development_roadmap/config_phase.md
- Architecture: docs/architecture/config_design.md
- Behavior: docs/behavior/config_requirements.md

**Used By:**
- src/main.py
- src/config_loader.py
''')
        
        # Create some referenced files
        phase_file = self.test_path / "docs" / "development_roadmap" / "config_phase.md"
        phase_file.write_text("# Config phase")
        
        main_file = self.test_path / "src" / "main.py"
        main_file.write_text("# Main file")
        
        context = self.loader.load_full_context("config/settings.json")
        
        # Verify references from .ref file were found
        refs = context['cross_references']
        self.assertIn("docs/development_roadmap/config_phase.md", refs['phase_plans'])
        self.assertIn("src/main.py", refs['related_files'])
    
    def test_dependency_analysis_python(self):
        """Test Python dependency analysis"""
        # Create target and imported files
        target_file = self.test_path / "src" / "main.py"
        target_file.write_text('''"""Main module"""

import os
import json
from src.helper import utility_func
from tools.validator import validate

def main():
    pass
''')
        
        helper_file = self.test_path / "src" / "helper.py"
        helper_file.write_text('''"""Helper module"""
from src.main import main

def utility_func():
    pass
''')
        
        validator_file = self.test_path / "tools" / "validator.py"
        validator_file.write_text('''"""Validator module"""

def validate():
    pass
''')
        
        context = self.loader.load_full_context("src/main.py")
        
        # Verify import analysis
        deps = context['dependencies']
        runtime_deps = deps['runtime_deps']
        
        self.assertIn("os", runtime_deps['imports'])
        self.assertIn("json", runtime_deps['imports'])
        self.assertIn("src.helper", runtime_deps['imports'])
        self.assertIn("tools.validator", runtime_deps['imports'])
        
        # Verify files that import this module
        self.assertIn("src/helper.py", deps['imported_by_files'])
    
    def test_find_related_files(self):
        """Test finding related test and tool files"""
        # Create target file
        target_file = self.test_path / "src" / "data_processor.py"
        target_file.write_text("# Data processor")
        
        # Create related test files
        test_file1 = self.test_path / "tests" / "unit" / "test_data_processor.py"
        test_file1.write_text("# Test for data processor")
        
        test_file2 = self.test_path / "tests" / "integration" / "test_data_processor_integration.py"
        test_file2.write_text("# Integration test")
        
        # Create related tool file
        tool_file = self.test_path / "tools" / "data_processor_tool.py"
        tool_file.write_text("# Tool for data processor")
        
        # Create test directory structure
        (self.test_path / "tests" / "integration").mkdir(parents=True)
        
        context = self.loader.load_full_context("src/data_processor.py")
        
        # Verify related files were found
        related = context['related_files']
        self.assertIn("tests/unit/test_data_processor.py", related['test_files'])
        self.assertIn("tools/data_processor_tool.py", related['tool_files'])
    
    def test_find_references_to_file(self):
        """Test finding files that reference the target file"""
        # Create target file
        target_file = self.test_path / "src" / "utilities.py"
        target_file.write_text("# Utilities module")
        
        # Create files that reference the target
        ref_file1 = self.test_path / "src" / "main.py"
        ref_file1.write_text('''"""Main module"""
from src.utilities import helper_func

def main():
    pass
''')
        
        ref_file2 = self.test_path / "docs" / "development_roadmap" / "phase1.md"
        ref_file2.write_text('''# Phase 1

## Implementation Files
- `src/utilities.py` - Utility functions
- `src/main.py` - Main application
''')
        
        context = self.loader.load_full_context("src/utilities.py")
        
        # Verify files that reference target were found
        refs_to_target = context['cross_references']['references_to_target']
        self.assertIn("src/main.py", refs_to_target)
        self.assertIn("docs/development_roadmap/phase1.md", refs_to_target)
    
    def test_format_context_output(self):
        """Test context output formatting"""
        # Create simple context
        context = {
            'target_file': 'src/test.py',
            'cross_references': {
                'behavior_docs': ['docs/behavior/test.md'],
                'architecture_docs': [],
                'phase_plans': ['docs/development_roadmap/phase1.md'],
                'related_files': ['src/helper.py'],
                'references_to_target': ['src/main.py']
            },
            'dependencies': {
                'runtime_deps': {'imports': ['os', 'sys'], 'imported_by': [], 'config_files': []},
                'planning_deps': {'blocks': [], 'blocked_by': []},
                'imported_by_files': ['src/main.py'],
                'config_files': []
            },
            'related_files': {
                'test_files': ['tests/unit/test_test.py'],
                'tool_files': []
            },
            'full_texts': {
                'docs/behavior/test.md': '# Test behavior doc',
                'docs/development_roadmap/phase1.md': '# Phase 1 plan'
            }
        }
        
        output = self.loader.format_context_output(context)
        
        # Verify output structure
        self.assertIn("FULL CONTEXT FOR: src/test.py", output)
        self.assertIn("CROSS-REFERENCES:", output)
        self.assertIn("DEPENDENCIES:", output)
        self.assertIn("FULL TEXT OF ALL REFERENCED FILES", output)
        self.assertIn("# Test behavior doc", output)
        self.assertIn("# Phase 1 plan", output)
    
    def test_error_context_for_missing_file(self):
        """Test error context when target file doesn't exist"""
        context = self.loader.load_full_context("nonexistent/file.py")
        
        self.assertIn('error', context)
        self.assertEqual(context['error'], 'File does not exist')
    
    def test_module_to_file_path_conversion(self):
        """Test conversion of Python module names to file paths"""
        # Create test file
        test_file = self.test_path / "src" / "submodule" / "helper.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Helper")
        
        # Test conversion
        result = self.loader._module_to_file_path("src.submodule.helper")
        self.assertEqual(result, "src/submodule/helper.py")
        
        # Test non-existent module
        result = self.loader._module_to_file_path("nonexistent.module")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()