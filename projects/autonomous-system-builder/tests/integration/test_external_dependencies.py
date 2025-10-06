#!/usr/bin/env python3
"""
External dependency integration tests

LOCKED TESTS: These tests cannot be modified after creation to prevent
anti-fabrication rule violations. Implementation must make these tests pass.

Test Coverage Target: 80% (External dependency integration)
"""

import pytest
import json
import tempfile
import os
import subprocess
import time
import stat
from pathlib import Path
from unittest.mock import patch, Mock, call

# Import will be: from src.context.cross_reference_manager import CrossReferenceManager
# from src.analysis.decision_engine import LLMDecisionEngine
# from src.utils.json_utilities import JSONUtilities
# For now, we'll assume the import structure based on our pseudocode

class TestFileSystemIntegration:
    """Test file system operations with real files (no mocking)"""
    
    def setup_method(self):
        """Set up test environment with realistic file scenarios"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create project structure
        self._create_test_project_structure()
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_cross_reference_discovery_with_real_files(self):
        """Test cross-reference discovery with actual file system operations"""
        # GIVEN: Real project with various file types and cross-references
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # WHEN: Cross-reference discovery scans real files
        start_time = time.time()
        all_references = cross_ref_manager.discover_all_cross_references()
        discovery_time = time.time() - start_time
        
        # THEN: Discovery should work with real file system
        # EVIDENCE: Discovery completes within reasonable time
        assert discovery_time < 30  # Should complete within 30 seconds
        
        # EVIDENCE: References are discovered from actual files
        assert len(all_references) > 0
        
        # Verify specific file references
        main_py_refs = all_references.get('src/main.py', [])
        assert any('test_main.py' in ref.target_file for ref in main_py_refs)
        
        # EVIDENCE: Python imports are correctly parsed
        import_refs = [ref for ref in main_py_refs if ref.reference_type == ReferenceType.IMPORTS]
        assert len(import_refs) > 0
        
        # EVIDENCE: RELATES_TO comments are found
        relates_refs = [ref for ref in main_py_refs if ref.reference_type == ReferenceType.RELATES_TO]
        assert len(relates_refs) > 0
    
    def test_file_operations_with_permission_restrictions(self):
        """Test system handles file permission restrictions correctly"""
        # GIVEN: Files with restricted permissions
        restricted_file = self.project_root / 'src' / 'restricted.py'
        restricted_file.write_text('# Restricted file\nprint("restricted")')
        
        # Make file read-only
        os.chmod(restricted_file, stat.S_IRUSR)
        
        try:
            cross_ref_manager = CrossReferenceManager(str(self.project_root))
            
            # WHEN: Cross-reference discovery encounters restricted files
            all_references = cross_ref_manager.discover_all_cross_references()
            
            # THEN: System should handle permissions gracefully
            # EVIDENCE: Discovery doesn't crash on permission issues
            assert isinstance(all_references, dict)
            
            # EVIDENCE: Accessible files are still processed
            assert len(all_references) > 0
            
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_file, stat.S_IRUSR | stat.S_IWUSR)
    
    def test_large_file_handling(self):
        """Test system handles large files appropriately"""
        # GIVEN: Large file that might stress the system
        large_file = self.project_root / 'src' / 'large_module.py'
        
        # Create large file (but reasonable for testing)
        large_content = [
            '#!/usr/bin/env python3',
            '"""Large module for testing file size handling"""',
            '',
            'RELATES_TO: tests/test_large_module.py',
            ''
        ]
        
        # Add many functions to make it large
        for i in range(1000):
            large_content.extend([
                f'def function_{i}():',
                f'    """Function number {i}"""',
                f'    return "result_{i}"',
                ''
            ])
        
        large_file.write_text('\n'.join(large_content))
        
        # WHEN: Cross-reference manager processes large file
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        start_time = time.time()
        all_references = cross_ref_manager.discover_all_cross_references()
        processing_time = time.time() - start_time
        
        # THEN: Large file should be processed efficiently
        # EVIDENCE: Processing completes within reasonable time
        assert processing_time < 60  # Should complete within 1 minute
        
        # EVIDENCE: Large file references are found
        large_file_refs = all_references.get('src/large_module.py', [])
        assert len(large_file_refs) > 0
        
        # EVIDENCE: File content was actually parsed
        relates_refs = [ref for ref in large_file_refs if ref.reference_type == ReferenceType.RELATES_TO]
        assert any('test_large_module.py' in ref.target_file for ref in relates_refs)
    
    def test_concurrent_file_access(self):
        """Test system handles concurrent file access safely"""
        # GIVEN: Multiple processes potentially accessing same files
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # WHEN: Multiple discovery operations run concurrently
        def run_discovery():
            return cross_ref_manager.discover_all_cross_references()
        
        import threading
        results = []
        errors = []
        
        def discovery_thread():
            try:
                result = run_discovery()
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple discovery threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=discovery_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # THEN: Concurrent access should work safely
        # EVIDENCE: No errors from concurrent access
        assert len(errors) == 0
        
        # EVIDENCE: All threads completed successfully
        assert len(results) == 3
        
        # EVIDENCE: Results are consistent
        for result in results:
            assert isinstance(result, dict)
            assert len(result) > 0
    
    def test_broken_symlinks_and_special_files(self):
        """Test system handles broken symlinks and special files gracefully"""
        # GIVEN: Project with broken symlinks and special files
        
        # Create broken symlink
        broken_link = self.project_root / 'src' / 'broken_link.py'
        try:
            os.symlink('/nonexistent/file.py', broken_link)
        except OSError:
            # Skip test if symlinks not supported
            pytest.skip("Symlinks not supported on this system")
        
        # Create directory that looks like a file
        fake_file = self.project_root / 'src' / 'fake_file.py'
        fake_file.mkdir()
        
        # WHEN: Cross-reference discovery encounters special files
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # THEN: System should handle special files gracefully
        # EVIDENCE: Discovery doesn't crash
        assert isinstance(all_references, dict)
        
        # EVIDENCE: Regular files are still processed
        assert len(all_references) > 0
        
        # EVIDENCE: Broken symlinks don't cause references
        assert 'src/broken_link.py' not in all_references
        assert 'src/fake_file.py' not in all_references
    
    def test_context_loading_with_missing_files(self):
        """Test context loading handles missing referenced files"""
        # GIVEN: Cross-reference manager with some invalid file references
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # Create file that references non-existent file
        invalid_ref_file = self.project_root / 'src' / 'invalid_refs.py'
        invalid_ref_file.write_text('''#!/usr/bin/env python3
"""
File with invalid cross-references for testing

RELATES_TO: nonexistent/file.py, src/main.py, another/missing.py
"""

def test_function():
    pass
''')
        
        # WHEN: Context bundle is created for file with invalid references
        context_bundle = cross_ref_manager.get_file_context_bundle(
            str(invalid_ref_file), include_content=True
        )
        
        # THEN: Context loading should handle missing files gracefully
        # EVIDENCE: Context bundle is created despite missing files
        assert context_bundle is not None
        assert context_bundle.target_file == str(invalid_ref_file)
        
        # EVIDENCE: Valid references are still included
        valid_refs = [ref for ref in context_bundle.direct_references 
                     if 'src/main.py' in ref.target_file]
        assert len(valid_refs) > 0
        
        # EVIDENCE: Invalid references are detected but don't crash the system
        all_refs = cross_ref_manager.discover_all_cross_references()
        broken_refs = cross_ref_manager.validate_all_references()
        assert 'src/invalid_refs.py' in broken_refs
    
    def _create_test_project_structure(self):
        """Create realistic test project structure"""
        # Create directories
        directories = ['src', 'tests', 'docs', 'config']
        for dir_name in directories:
            (self.project_root / dir_name).mkdir()
        
        # Create main.py with imports and cross-references
        main_py = self.project_root / 'src' / 'main.py'
        main_py.write_text('''#!/usr/bin/env python3
"""
Main module for integration testing

RELATES_TO: tests/test_main.py, docs/api.md
"""

import json
import os
from .utils import helper_function

def main():
    """Main function"""
    return helper_function()

if __name__ == "__main__":
    main()
''')
        
        # Create utils.py
        utils_py = self.project_root / 'src' / 'utils.py'
        utils_py.write_text('''#!/usr/bin/env python3
"""
Utility functions

RELATES_TO: src/main.py, tests/test_utils.py
"""

def helper_function():
    """Helper function"""
    return "helper_result"
''')
        
        # Create test files
        test_main_py = self.project_root / 'tests' / 'test_main.py'
        test_main_py.write_text('''#!/usr/bin/env python3
"""
Tests for main module

RELATES_TO: src/main.py
"""

import pytest
from src.main import main

def test_main():
    result = main()
    assert result == "helper_result"
''')
        
        # Create documentation
        api_md = self.project_root / 'docs' / 'api.md'
        api_md.write_text('''# API Documentation

This documents the API.

## Related Files
RELATES_TO: src/main.py, src/utils.py
''')


class TestLLMIntegrationSimulation:
    """Test LLM integration via subprocess simulation (Claude Code Task tool)"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_llm_query_subprocess_execution(self):
        """Test LLM query via subprocess simulation works correctly"""
        # GIVEN: Decision engine configured for subprocess LLM queries
        decision_engine = LLMDecisionEngine(str(self.project_root))
        
        # WHEN: LLM query is executed via subprocess simulation
        test_prompt = "Test prompt for LLM integration"
        
        with patch('subprocess.run') as mock_subprocess:
            # Simulate successful subprocess execution
            mock_subprocess.return_value = Mock(
                stdout='{"selected_task": {"id": "test_task"}, "confidence": "high"}',
                stderr='',
                returncode=0
            )
            
            result = decision_engine._query_llm_for_decision(test_prompt, "task_selection")
        
        # THEN: Subprocess integration should work correctly
        # EVIDENCE: Subprocess was called with correct parameters
        mock_subprocess.assert_called_once()
        
        # EVIDENCE: LLM response was processed correctly
        assert isinstance(result, str)
        assert "selected_task" in result
        assert "confidence" in result
    
    def test_llm_query_timeout_handling(self):
        """Test LLM query handles timeout scenarios correctly"""
        # GIVEN: Decision engine with timeout constraints
        decision_engine = LLMDecisionEngine(str(self.project_root))
        
        # WHEN: LLM query times out
        test_prompt = "Test prompt that will timeout"
        
        with patch('subprocess.run') as mock_subprocess:
            # Simulate subprocess timeout
            mock_subprocess.side_effect = subprocess.TimeoutExpired(
                cmd=['test'], timeout=30
            )
            
            with pytest.raises(DecisionError, match="Failed to query LLM"):
                decision_engine._query_llm_for_decision(test_prompt, "task_selection")
        
        # THEN: Timeout should be handled gracefully
        # EVIDENCE: Subprocess was called with timeout
        mock_subprocess.assert_called_once()
    
    def test_llm_query_error_handling(self):
        """Test LLM query handles various error conditions"""
        # GIVEN: Decision engine that may encounter errors
        decision_engine = LLMDecisionEngine(str(self.project_root))
        
        test_prompt = "Test prompt for error handling"
        
        # Test different error scenarios
        error_scenarios = [
            # Non-zero return code
            Mock(stdout='', stderr='Error occurred', returncode=1),
            # Invalid JSON response
            Mock(stdout='Invalid JSON response', stderr='', returncode=0),
            # Empty response
            Mock(stdout='', stderr='', returncode=0)
        ]
        
        for error_scenario in error_scenarios:
            with patch('subprocess.run', return_value=error_scenario):
                # WHEN: LLM query encounters error
                # THEN: Error should be handled appropriately
                try:
                    result = decision_engine._query_llm_for_decision(test_prompt, "task_selection")
                    # If no exception, should still be valid JSON
                    json.loads(result)
                except DecisionError:
                    # Expected for error scenarios
                    pass
    
    def test_llm_integration_with_context_size_limits(self):
        """Test LLM integration respects context size constraints"""
        # GIVEN: Decision engine with context size management
        decision_engine = LLMDecisionEngine(str(self.project_root))
        
        # Create very large prompt that would exceed token limits
        large_context = {
            'available_options': [{'id': f'task_{i}', 'description': 'x' * 1000} for i in range(200)],
            'project_state': {'large_data': 'y' * 10000},
            'constraints': {'huge_config': 'z' * 5000}
        }
        
        # WHEN: LLM query is made with large context
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(
                stdout='{"selected_task": {"id": "task_1"}, "confidence": "medium"}',
                stderr='',
                returncode=0
            )
            
            prompt = decision_engine._generate_task_selection_prompt(
                DecisionContext(
                    decision_type=DecisionType.TASK_SELECTION,
                    project_state=large_context['project_state'],
                    available_options=large_context['available_options'],
                    constraints=large_context['constraints'],
                    previous_decisions=[],
                    evidence_available={},
                    time_pressure='medium'
                )
            )
            
            result = decision_engine._query_llm_for_decision(prompt, "task_selection")
        
        # THEN: Context size should be managed appropriately
        # EVIDENCE: Prompt was generated (context size management worked)
        assert isinstance(prompt, str)
        
        # EVIDENCE: LLM query completed successfully
        assert isinstance(result, str)
        parsed_result = json.loads(result)
        assert 'selected_task' in parsed_result
    
    def test_llm_interaction_logging(self):
        """Test LLM interactions are logged for debugging"""
        # GIVEN: Decision engine with interaction logging
        decision_engine = LLMDecisionEngine(str(self.project_root))
        
        # Ensure interaction directory exists
        interaction_dir = self.project_root / 'logs' / 'decisions' / 'llm_interactions'
        interaction_dir.mkdir(parents=True, exist_ok=True)
        
        # WHEN: LLM query is executed
        test_prompt = "Test prompt for logging verification"
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(
                stdout='{"test": "response"}',
                stderr='',
                returncode=0
            )
            
            result = decision_engine._query_llm_for_decision(test_prompt, "test_decision")
        
        # THEN: Interaction should be logged
        # EVIDENCE: Log file was created
        log_files = list(interaction_dir.glob('test_decision_*.md'))
        assert len(log_files) >= 1
        
        # EVIDENCE: Log file contains prompt and response
        with open(log_files[0], 'r') as f:
            log_content = f.read()
        
        assert test_prompt in log_content
        assert 'response' in log_content
        assert 'Timestamp' in log_content


class TestPythonImportDiscovery:
    """Test Python import discovery with real module scanning"""
    
    def setup_method(self):
        """Set up test environment with Python modules"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create Python package structure
        self._create_python_package_structure()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_python_import_discovery_with_real_modules(self):
        """Test import discovery with actual Python files and AST parsing"""
        # GIVEN: Real Python package with various import patterns
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # WHEN: Import discovery is performed
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # THEN: Import relationships should be correctly discovered
        # EVIDENCE: Main module imports are found
        main_refs = all_references.get('src/mypackage/main.py', [])
        import_refs = [ref for ref in main_refs if ref.reference_type == ReferenceType.IMPORTS]
        
        assert len(import_refs) > 0
        
        # EVIDENCE: Relative imports are resolved correctly
        relative_imports = [ref for ref in import_refs if 'utils' in ref.target_file]
        assert len(relative_imports) > 0
        
        # EVIDENCE: Standard library imports are ignored (or handled appropriately)
        stdlib_imports = [ref for ref in import_refs if 'json' in ref.target_file or 'os' in ref.target_file]
        # Standard library imports might not be included (implementation dependent)
        
        # EVIDENCE: Package imports work correctly
        package_refs = all_references.get('src/mypackage/__init__.py', [])
        assert len(package_refs) >= 0  # Package might have imports
    
    def test_python_ast_parsing_with_syntax_errors(self):
        """Test AST parsing handles syntax errors gracefully"""
        # GIVEN: Python file with syntax errors
        syntax_error_file = self.project_root / 'src' / 'mypackage' / 'broken.py'
        syntax_error_file.write_text('''#!/usr/bin/env python3
"""
File with syntax errors for testing

RELATES_TO: src/mypackage/main.py
"""

def broken_function(
    # Missing closing parenthesis - syntax error
    return "broken"

import json  # This import should still be found via regex fallback
''')
        
        # WHEN: Cross-reference discovery processes file with syntax errors
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # THEN: System should handle syntax errors gracefully
        # EVIDENCE: Discovery doesn't crash on syntax errors
        assert isinstance(all_references, dict)
        
        # EVIDENCE: File with syntax error is still processed for other references
        broken_refs = all_references.get('src/mypackage/broken.py', [])
        
        # Should find RELATES_TO reference even with syntax error
        relates_refs = [ref for ref in broken_refs if ref.reference_type == ReferenceType.RELATES_TO]
        assert len(relates_refs) > 0
        
        # Might find import via regex fallback
        import_refs = [ref for ref in broken_refs if ref.reference_type == ReferenceType.IMPORTS]
        # Import discovery might work via regex fallback even with syntax errors
    
    def test_complex_import_patterns(self):
        """Test discovery of complex Python import patterns"""
        # GIVEN: File with complex import patterns
        complex_imports_file = self.project_root / 'src' / 'mypackage' / 'complex_imports.py'
        complex_imports_file.write_text('''#!/usr/bin/env python3
"""
File with complex import patterns

RELATES_TO: src/mypackage/utils.py
"""

# Various import patterns
import json
import os.path
from pathlib import Path
from ..utils import helper_function
from .submodule import SubClass
import typing as t
from typing import Dict, List, Optional

# Conditional imports
try:
    import numpy as np
except ImportError:
    np = None

# Import within function
def dynamic_import():
    import datetime
    return datetime.now()
''')
        
        # Create submodule for import testing
        submodule_file = self.project_root / 'src' / 'mypackage' / 'submodule.py'
        submodule_file.write_text('''#!/usr/bin/env python3
"""Submodule for import testing"""

class SubClass:
    pass
''')
        
        # WHEN: Complex imports are discovered
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # THEN: Complex import patterns should be handled
        complex_refs = all_references.get('src/mypackage/complex_imports.py', [])
        import_refs = [ref for ref in complex_refs if ref.reference_type == ReferenceType.IMPORTS]
        
        # EVIDENCE: Various import types are discovered
        assert len(import_refs) > 0
        
        # EVIDENCE: Relative imports are resolved
        relative_imports = [ref for ref in import_refs if 'submodule' in ref.target_file]
        assert len(relative_imports) > 0
        
        # EVIDENCE: Parent directory imports work
        parent_imports = [ref for ref in import_refs if 'utils' in ref.target_file]
        assert len(parent_imports) > 0
    
    def test_import_discovery_performance(self):
        """Test import discovery performance with many files"""
        # GIVEN: Many Python files to test scalability
        for i in range(20):  # Create moderate number for testing
            module_file = self.project_root / 'src' / 'mypackage' / f'module_{i}.py'
            module_file.write_text(f'''#!/usr/bin/env python3
"""Module {i} for performance testing"""

import json
from .utils import helper_function
from .module_{(i + 1) % 20} import function_{(i + 1) % 20}

def function_{i}():
    return "result_{i}"
''')
        
        # WHEN: Import discovery processes many files
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        start_time = time.time()
        all_references = cross_ref_manager.discover_all_cross_references()
        discovery_time = time.time() - start_time
        
        # THEN: Discovery should complete efficiently
        # EVIDENCE: Discovery completes within reasonable time
        assert discovery_time < 30  # Should complete within 30 seconds
        
        # EVIDENCE: All modules were processed
        module_refs = [key for key in all_references.keys() if 'module_' in key]
        assert len(module_refs) >= 15  # Most modules should be found
        
        # EVIDENCE: Import relationships are discovered
        total_import_refs = 0
        for refs in all_references.values():
            import_refs = [ref for ref in refs if ref.reference_type == ReferenceType.IMPORTS]
            total_import_refs += len(import_refs)
        
        assert total_import_refs > 20  # Should find many import relationships
    
    def _create_python_package_structure(self):
        """Create realistic Python package structure"""
        # Create package directories
        package_dir = self.project_root / 'src' / 'mypackage'
        package_dir.mkdir(parents=True)
        
        # Create __init__.py
        init_file = package_dir / '__init__.py'
        init_file.write_text('''#!/usr/bin/env python3
"""MyPackage - Test package for import discovery"""

from .main import main_function
from .utils import helper_function

__version__ = "1.0.0"
''')
        
        # Create main.py with various imports
        main_file = package_dir / 'main.py'
        main_file.write_text('''#!/usr/bin/env python3
"""
Main module with various import patterns

RELATES_TO: src/mypackage/utils.py, tests/test_main.py
"""

import json
import os
from pathlib import Path
from .utils import helper_function
from ..otherpackage import other_function

def main_function():
    """Main function using imports"""
    return helper_function()
''')
        
        # Create utils.py
        utils_file = package_dir / 'utils.py'
        utils_file.write_text('''#!/usr/bin/env python3
"""
Utility functions

RELATES_TO: src/mypackage/main.py
"""

import re
from typing import Optional

def helper_function() -> str:
    """Helper function"""
    return "helper_result"
''')
        
        # Create other package for cross-package imports
        other_package_dir = self.project_root / 'src' / 'otherpackage'
        other_package_dir.mkdir(parents=True)
        
        other_init = other_package_dir / '__init__.py'
        other_init.write_text('''#!/usr/bin/env python3
"""Other package for import testing"""

def other_function():
    return "other_result"
''')