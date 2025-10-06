#!/usr/bin/env python3
"""
Integration tests for the complete tools workflow

Tests the interaction between validate_references.py, load_context.py, 
and inject_error.py to ensure they work together correctly.
"""

import os
import tempfile
import unittest
from pathlib import Path
import sys

# Add tools directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from validate_references import ReferenceValidator
from load_context import ContextLoader
from inject_error import ErrorInjector


class TestToolsWorkflow(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with realistic project structure"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create realistic project structure
        (self.test_path / "docs" / "behavior").mkdir(parents=True)
        (self.test_path / "docs" / "architecture").mkdir(parents=True)
        (self.test_path / "docs" / "development_roadmap").mkdir(parents=True)
        (self.test_path / "src" / "scrapers").mkdir(parents=True)
        (self.test_path / "src" / "analysis").mkdir(parents=True)
        (self.test_path / "tools").mkdir(parents=True)
        (self.test_path / "tests" / "unit").mkdir(parents=True)
        (self.test_path / "config").mkdir(parents=True)
        (self.test_path / "logs" / "errors" / "active").mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.validator = ReferenceValidator(self.test_dir)
        self.loader = ContextLoader(self.test_dir)
        self.injector = ErrorInjector(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_complete_workflow_with_valid_references(self):
        """Test complete workflow with all valid references"""
        # Create a realistic project with valid cross-references
        self._create_valid_project_structure()
        
        # 1. Validate references - should pass
        broken_refs = self.validator.validate_all_references()
        self.assertEqual(len(broken_refs), 0, "Should have no broken references")
        
        # 2. Load context for main scraper
        context = self.loader.load_full_context("src/scrapers/goodwill_scraper.py")
        
        # Verify context loaded correctly
        self.assertEqual(context['target_file'], "src/scrapers/goodwill_scraper.py")
        self.assertIn("docs/behavior/scraping_requirements.md", context['cross_references']['behavior_docs'])
        self.assertIn("docs/architecture/scraper_design.md", context['cross_references']['architecture_docs'])
        self.assertIn("docs/development_roadmap/phase1.md", context['cross_references']['phase_plans'])
        
        # Verify full text was loaded
        self.assertIn("docs/behavior/scraping_requirements.md", context['full_texts'])
        self.assertIn("# Scraping Requirements", context['full_texts']['docs/behavior/scraping_requirements.md'])
        
        # 3. No errors should be injected since validation passed
        claude_md = self.test_path / "CLAUDE.md"
        self.assertFalse(claude_md.exists(), "No CLAUDE.md should be created for valid project")
    
    def test_workflow_with_broken_references_and_error_injection(self):
        """Test workflow when validation finds broken references"""
        # Create project with broken references
        self._create_project_with_broken_references()
        
        # 1. Validate references - should find broken refs
        broken_refs = self.validator.validate_all_references()
        self.assertGreater(len(broken_refs), 0, "Should find broken references")
        
        # 2. Inject errors for broken references
        for broken_ref in broken_refs:
            if broken_ref['error_type'] == 'BROKEN_REFERENCE':
                success = self.injector.inject_broken_reference_error(
                    source_file=broken_ref['source_file'],
                    target_path=broken_ref['target_path'],
                    line_number=broken_ref['line_number'],
                    details=broken_ref['details']
                )
                self.assertTrue(success)
        
        # 3. Verify CLAUDE.md was created with errors
        claude_md = self.test_path / "CLAUDE.md"
        self.assertTrue(claude_md.exists())
        
        content = claude_md.read_text()
        self.assertIn("🚨 ACTIVE ERRORS AND BLOCKERS", content)
        self.assertIn("Current Error Status: BLOCKED", content)
        self.assertIn("BROKEN_REFERENCE:", content)
        
        # 4. Load context for file with broken references
        context = self.loader.load_full_context("src/scrapers/broken_scraper.py")
        
        # Should still load context but missing files should be empty or not present
        self.assertEqual(context['target_file'], "src/scrapers/broken_scraper.py")
        missing_file_content = context['full_texts'].get('docs/missing/file.md', '')
        # Missing file should be empty or not present in context
        self.assertEqual(missing_file_content, '')
    
    def test_file_move_detection_and_reference_updates(self):
        """Test workflow for handling file moves"""
        # Create valid project
        self._create_valid_project_structure()
        
        # 1. Validate - should be clean initially
        broken_refs = self.validator.validate_all_references()
        self.assertEqual(len(broken_refs), 0)
        
        # 2. Simulate file move by renaming a file
        old_file = self.test_path / "docs" / "development_roadmap" / "phase1.md"
        new_file = self.test_path / "docs" / "development_roadmap" / "phase1_foundation.md"
        old_file.rename(new_file)
        
        # 3. Validate again - should find broken references
        broken_refs = self.validator.validate_all_references()
        self.assertGreater(len(broken_refs), 0, "Should find broken references after file move")
        
        # 4. Inject file move error
        success = self.injector.inject_file_move_error(
            old_path="docs/development_roadmap/phase1.md",
            new_path="docs/development_roadmap/phase1_foundation.md"
        )
        self.assertTrue(success)
        
        # 5. Verify error log contains update instructions
        error_logs = list((self.test_path / "logs" / "errors" / "active").glob("*.log"))
        self.assertGreater(len(error_logs), 0)
        
        log_content = error_logs[-1].read_text()  # Most recent log
        self.assertIn("Search for references to: docs/development_roadmap/phase1.md", log_content)
        self.assertIn("Replace with: docs/development_roadmap/phase1_foundation.md", log_content)
        
        # 6. Simulate fixing references by updating the source file
        scraper_file = self.test_path / "src" / "scrapers" / "goodwill_scraper.py"
        content = scraper_file.read_text()
        updated_content = content.replace(
            "docs/development_roadmap/phase1.md",
            "docs/development_roadmap/phase1_foundation.md"
        )
        scraper_file.write_text(updated_content)
        
        # 7. Validate again - should be clean after fix
        validator_after_fix = ReferenceValidator(self.test_dir)
        broken_refs_after_fix = validator_after_fix.validate_all_references()
        self.assertEqual(len(broken_refs_after_fix), 0, "Should have no broken references after fix")
    
    def test_context_loading_with_complex_dependencies(self):
        """Test context loading with complex dependency relationships"""
        # Create project with complex dependencies
        self._create_complex_dependency_project()
        
        # Load context for main orchestrator
        context = self.loader.load_full_context("src/orchestrator.py")
        
        # Verify all dependency types were detected
        deps = context['dependencies']
        
        # Runtime dependencies
        self.assertIn("src.scrapers.goodwill_scraper", deps['runtime_deps']['imports'])
        self.assertIn("src.analysis.profit_calculator", deps['runtime_deps']['imports'])
        
        # Files that import this module
        self.assertIn("src/main.py", deps['imported_by_files'])
        
        # Config file dependencies
        self.assertIn("config/orchestrator_settings.json", deps['config_files'])
        
        # Verify full context includes all related files
        full_texts = context['full_texts']
        self.assertIn("src/scrapers/goodwill_scraper.py", full_texts)
        self.assertIn("src/analysis/profit_calculator.py", full_texts)
        self.assertIn("config/orchestrator_settings.json", full_texts)
    
    def test_error_resolution_workflow(self):
        """Test complete error resolution workflow"""
        # Create project with broken reference
        self._create_project_with_broken_references()
        
        # 1. Validate and inject errors
        broken_refs = self.validator.validate_all_references()
        for broken_ref in broken_refs:
            if broken_ref['error_type'] == 'BROKEN_REFERENCE':
                self.injector.inject_broken_reference_error(
                    source_file=broken_ref['source_file'],
                    target_path=broken_ref['target_path'],
                    line_number=broken_ref['line_number']
                )
                break  # Just test with one error
        
        # 2. Verify error in CLAUDE.md
        claude_md = self.test_path / "CLAUDE.md"
        content = claude_md.read_text()
        
        # Extract timestamp for error resolution
        import re
        timestamp_match = re.search(r'\*\*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\*\*', content)
        self.assertIsNotNone(timestamp_match)
        timestamp = timestamp_match.group(1)
        
        # 3. Fix all broken references by creating the missing files
        missing_files = [
            ("docs/missing/file.md", "# Fixed missing file"),
            ("docs/architecture/nonexistent.md", "# Architecture doc"),
            ("docs/behavior/missing_requirements.md", "# Requirements doc"),
            ("src/missing/helper.py", "# Helper module\ndef helper(): pass"),
            ("tests/unit/test_missing.py", "# Missing test\ndef test_placeholder(): pass"),
            ("config/missing.json", '{"config": "placeholder"}')
        ]
        
        for file_path, content in missing_files:
            missing_file = self.test_path / file_path
            missing_file.parent.mkdir(parents=True, exist_ok=True)
            missing_file.write_text(content)
        
        # 4. Validate that fix worked
        validator_after_fix = ReferenceValidator(self.test_dir)
        broken_refs_after_fix = validator_after_fix.validate_all_references()
        self.assertEqual(len(broken_refs_after_fix), 0)
        
        # 5. Resolve the error
        success = self.injector.remove_error(timestamp, "Created missing file")
        self.assertTrue(success)
        
        # 6. Verify error moved to resolved section
        content = claude_md.read_text()
        self.assertIn("Recently Resolved Errors:", content)
        self.assertIn("✅ RESOLVED", content)
        self.assertIn("Created missing file", content)
        self.assertIn("Current Error Status: CLEAR", content)
    
    def _create_valid_project_structure(self):
        """Create a realistic project structure with valid cross-references"""
        # Behavior docs
        behavior_file = self.test_path / "docs" / "behavior" / "scraping_requirements.md"
        behavior_file.write_text("# Scraping Requirements\n\nRequirements for web scraping.")
        
        # Architecture docs
        arch_file = self.test_path / "docs" / "architecture" / "scraper_design.md"
        arch_file.write_text("# Scraper Design\n\nArchitecture for scraping system.")
        
        # Phase plan
        phase_file = self.test_path / "docs" / "development_roadmap" / "phase1.md"
        phase_file.write_text("# Phase 1\n\nInitial development phase.")
        
        # Main scraper with valid references
        scraper_file = self.test_path / "src" / "scrapers" / "goodwill_scraper.py"
        scraper_file.write_text('''"""
Goodwill scraper module

TRACEABILITY:
- Phase Plan: docs/development_roadmap/phase1.md
- Architecture: docs/architecture/scraper_design.md
- Behavior: docs/behavior/scraping_requirements.md

CROSS-REFERENCES:
- Related Files: src/analysis/profit_calculator.py
- Tests: tests/unit/test_goodwill_scraper.py
- Config: config/scraper_settings.json

DEPENDENCIES:
- Imports: requests, beautifulsoup4
- Imported By: src/orchestrator.py
- Planning: Blocks Phase 2
"""

import requests
from bs4 import BeautifulSoup

def scrape_goodwill():
    pass
''')
        
        # Related files
        calculator_file = self.test_path / "src" / "analysis" / "profit_calculator.py"
        calculator_file.write_text("# Profit calculator")
        
        test_file = self.test_path / "tests" / "unit" / "test_goodwill_scraper.py"
        test_file.write_text("# Test for scraper")
        
        config_file = self.test_path / "config" / "scraper_settings.json"
        config_file.write_text('{"setting": "value"}')
        
        orchestrator_file = self.test_path / "src" / "orchestrator.py"
        orchestrator_file.write_text('''"""Orchestrator module"""
from src.scrapers.goodwill_scraper import scrape_goodwill

def orchestrate():
    pass
''')
    
    def _create_project_with_broken_references(self):
        """Create project with intentionally broken references"""
        # Create file with broken references
        broken_scraper = self.test_path / "src" / "scrapers" / "broken_scraper.py"
        broken_scraper.write_text('''"""
Broken scraper with invalid references

TRACEABILITY:
- Phase Plan: docs/missing/file.md
- Architecture: docs/architecture/nonexistent.md
- Behavior: docs/behavior/missing_requirements.md

CROSS-REFERENCES:
- Related Files: src/missing/helper.py
- Tests: tests/unit/test_missing.py
- Config: config/missing.json
"""

def broken_function():
    pass
''')
        
        # Create some valid files to ensure validator works correctly
        valid_file = self.test_path / "docs" / "behavior" / "valid.md"
        valid_file.write_text("# Valid file")
    
    def _create_complex_dependency_project(self):
        """Create project with complex dependency relationships"""
        # Main orchestrator that imports multiple modules
        orchestrator = self.test_path / "src" / "orchestrator.py"
        orchestrator.write_text('''"""
Main orchestrator module

TRACEABILITY:
- Phase Plan: docs/development_roadmap/orchestration_phase.md
- Architecture: docs/architecture/system_design.md
- Behavior: docs/behavior/orchestration_requirements.md
"""

import json
from src.scrapers.goodwill_scraper import GoodwillScraper
from src.analysis.profit_calculator import calculate_profit

# Config file reference
with open("config/orchestrator_settings.json") as f:
    config = json.load(f)

def orchestrate():
    pass
''')
        
        # Scraper module
        scraper = self.test_path / "src" / "scrapers" / "goodwill_scraper.py"
        scraper.write_text('''"""Goodwill scraper"""

class GoodwillScraper:
    def scrape(self):
        pass
''')
        
        # Analysis module
        calculator = self.test_path / "src" / "analysis" / "profit_calculator.py"
        calculator.write_text('''"""Profit calculator"""

def calculate_profit(item_price, sold_price):
    return sold_price - item_price
''')
        
        # Main module that imports orchestrator
        main = self.test_path / "src" / "main.py"
        main.write_text('''"""Main application"""
from src.orchestrator import orchestrate

def main():
    orchestrate()
''')
        
        # Config file
        config = self.test_path / "config" / "orchestrator_settings.json"
        config.write_text('{"max_items": 100, "timeout": 30}')
        
        # Referenced docs
        (self.test_path / "docs" / "development_roadmap" / "orchestration_phase.md").write_text("# Orchestration Phase")
        (self.test_path / "docs" / "architecture" / "system_design.md").write_text("# System Design")
        (self.test_path / "docs" / "behavior" / "orchestration_requirements.md").write_text("# Orchestration Requirements")


if __name__ == '__main__':
    unittest.main()