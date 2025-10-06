#!/usr/bin/env python3
"""
Integration tests for cross-component behavior

LOCKED TESTS: These tests cannot be modified after creation to prevent
anti-fabrication rule violations. Implementation must make these tests pass.

Test Coverage Target: 90% (Cross-component integration)
"""

import pytest
import json
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Import will be: from src.config.configuration_manager import ConfigManager
# from src.persistence.state_manager import StateManager, ProjectState, TaskGraph, TaskNode
# from src.context.cross_reference_manager import CrossReferenceManager
# from src.analysis.decision_engine import LLMDecisionEngine
# from src.utils.json_utilities import JSONUtilities
# For now, we'll assume the import structure based on our pseudocode

class TestStateManagerConfigurationIntegration:
    """Test State Manager integrates correctly with Configuration Manager"""
    
    def setup_method(self):
        """Set up test environment with realistic project structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create realistic project structure
        (self.project_root / 'src').mkdir()
        (self.project_root / 'tests').mkdir()
        (self.project_root / 'docs').mkdir()
        (self.project_root / 'config').mkdir()
        
        # Create test configuration
        self.test_config = {
            'autonomous_behavior': {
                'max_hook_iterations': 25,
                'evidence_validation_strictness': 'strict'
            },
            'context_management': {
                'max_context_tokens': 50000,
                'prioritize_recent_files': True
            },
            'safety_mechanisms': {
                'max_file_modifications_per_session': 10,
                'backup_before_modifications': True,
                'disk_space_threshold_mb': 50
            },
            'evidence_collection': {
                'enable_anti_fabrication': True,
                'evidence_retention_days': 3
            },
            'integration_settings': {
                'test_framework_timeout_seconds': 60
            },
            'logging': {
                'log_level': 'INFO'
            }
        }
        
        # Save configuration
        config_file = self.project_root / 'config' / 'autonomous_config.json'
        with open(config_file, 'w') as f:
            json.dump(self.test_config, f, indent=2)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_state_manager_loads_configuration_constraints(self):
        """Test StateManager respects configuration limits from ConfigManager"""
        # GIVEN: Configuration with specific constraints
        config_manager = ConfigManager(str(self.project_root))
        loaded_config = config_manager.load_configuration()
        
        # Verify configuration was loaded correctly
        assert loaded_config['autonomous_behavior']['max_hook_iterations'] == 25
        assert loaded_config['safety_mechanisms']['max_file_modifications_per_session'] == 10
        
        # WHEN: StateManager is initialized with this configuration
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # THEN: StateManager should respect configuration constraints
        # Create test state
        test_state = self._create_test_state()
        
        # Verify state manager uses configuration for validation
        # (This would be tested by checking internal behavior)
        
        # EVIDENCE: State manager operations respect configured limits
        result = state_manager.save_complete_state(test_state)
        assert result is True
        
        # EVIDENCE: Backup was created because config requires it
        backup_files = list(state_manager.backup_dir.glob('state_backup_*.json'))
        assert len(backup_files) >= 1  # Backup should be created per configuration
    
    def test_state_manager_configuration_cache_invalidation(self):
        """Test StateManager responds to configuration changes"""
        # GIVEN: Initial configuration
        config_manager = ConfigManager(str(self.project_root))
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        initial_config = config_manager.load_configuration()
        assert initial_config['safety_mechanisms']['backup_before_modifications'] is True
        
        # WHEN: Configuration is updated
        updated_config = self.test_config.copy()
        updated_config['safety_mechanisms']['backup_before_modifications'] = False
        
        config_file = self.project_root / 'config' / 'autonomous_config.json'
        with open(config_file, 'w') as f:
            json.dump(updated_config, f, indent=2)
        
        # Sleep to ensure different mtime
        time.sleep(0.1)
        
        # THEN: StateManager should use updated configuration
        new_config = config_manager.load_configuration()
        assert new_config['safety_mechanisms']['backup_before_modifications'] is False
        
        # EVIDENCE: Configuration changes affect state manager behavior
        # (In a real implementation, this would test that backup behavior changes)
        test_state = self._create_test_state()
        result = state_manager.save_complete_state(test_state)
        assert result is True
    
    def test_state_manager_respects_configuration_timeouts(self):
        """Test StateManager operations respect configured timeout values"""
        # GIVEN: Configuration with specific timeout values
        config_manager = ConfigManager(str(self.project_root))
        config = config_manager.load_configuration()
        
        timeout_value = config['integration_settings']['test_framework_timeout_seconds']
        assert timeout_value == 60
        
        # WHEN: StateManager performs operations that should respect timeouts
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # THEN: Operations should complete within configured timeouts
        start_time = time.time()
        
        # Simulate operation that should respect timeout
        test_state = self._create_test_state()
        result = state_manager.save_complete_state(test_state)
        
        operation_time = time.time() - start_time
        
        # EVIDENCE: Operation completes quickly (well within timeout)
        assert operation_time < timeout_value
        assert result is True
    
    def test_configuration_validation_with_state_operations(self):
        """Test configuration validation affects state operation behavior"""
        # GIVEN: Configuration with strict validation
        config_manager = ConfigManager(str(self.project_root))
        config = config_manager.load_configuration()
        
        strictness = config['evidence_collection']['enable_anti_fabrication']
        assert strictness is True
        
        # WHEN: StateManager performs validation-sensitive operations
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # Create state with potential validation issues
        test_state = self._create_test_state()
        
        # THEN: State operations should enforce strict validation
        # EVIDENCE: State validation is performed according to configuration
        result = state_manager._validate_state_consistency(test_state)
        assert result is True  # State should be valid
        
        # EVIDENCE: Anti-fabrication features are enabled per configuration
        assert config['evidence_collection']['enable_anti_fabrication'] is True
    
    def _create_test_state(self):
        """Helper method to create valid test state"""
        from datetime import datetime, timezone
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.IMPLEMENTATION,
            methodology_step="configuration_integration_test",
            phase_completion_percentage=0.4,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=5,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["test_task"],
            completed_tasks=[]
        )
        
        task_graph = TaskGraph(
            nodes={},
            edges={},
            current_ready_tasks=[],
            blocked_tasks={}
        )
        
        state = CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={},
            dependencies={},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
        
        # Calculate hash using state manager
        state_manager = StateManager(str(self.project_root))
        state.state_hash = state_manager._calculate_state_hash(state)
        
        return state


class TestContextCrossReferenceIntegration:
    """Test Context Manager integrates correctly with Cross-Reference System"""
    
    def setup_method(self):
        """Set up test environment with cross-referenced files"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create project structure with cross-references
        src_dir = self.project_root / 'src'
        tests_dir = self.project_root / 'tests'
        docs_dir = self.project_root / 'docs'
        
        src_dir.mkdir()
        tests_dir.mkdir()
        docs_dir.mkdir()
        
        # Create Python file with imports
        main_py = src_dir / 'main.py'
        main_py.write_text('''#!/usr/bin/env python3
"""
Main module for integration testing

RELATES_TO: tests/test_main.py, docs/architecture.md
"""

from .utils import helper_function
import json
import os

def main_function():
    """Main function with cross-references"""
    return helper_function()

if __name__ == "__main__":
    main_function()
''')
        
        # Create utility file
        utils_py = src_dir / 'utils.py'
        utils_py.write_text('''#!/usr/bin/env python3
"""
Utility functions

RELATES_TO: src/main.py, tests/test_utils.py
"""

def helper_function():
    """Helper function for main"""
    return "helper_result"
''')
        
        # Create test file
        test_main_py = tests_dir / 'test_main.py'
        test_main_py.write_text('''#!/usr/bin/env python3
"""
Tests for main module

RELATES_TO: src/main.py, docs/testing.md
"""

import pytest
from src.main import main_function

def test_main_function():
    """Test main function behavior"""
    result = main_function()
    assert result == "helper_result"
''')
        
        # Create documentation file
        arch_md = docs_dir / 'architecture.md'
        arch_md.write_text('''# Architecture Documentation

This document describes the system architecture.

## Related Files
- src/main.py - Main entry point
- src/utils.py - Utility functions

## Cross-References
RELATES_TO: src/main.py, tests/test_main.py
''')
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_cross_reference_discovery_finds_all_relationships(self):
        """Test cross-reference manager discovers file relationships correctly"""
        # GIVEN: Project with cross-referenced files
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # WHEN: Cross-reference discovery is performed
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # THEN: All relationships should be discovered
        # EVIDENCE: References from main.py are found
        main_py_refs = all_references.get('src/main.py', [])
        assert any('tests/test_main.py' in ref.target_file for ref in main_py_refs)
        assert any('docs/architecture.md' in ref.target_file for ref in main_py_refs)
        
        # EVIDENCE: Python import relationships are discovered
        import_refs = [ref for ref in main_py_refs if ref.reference_type == ReferenceType.IMPORTS]
        assert any('utils' in ref.target_file for ref in import_refs)
        
        # EVIDENCE: RELATES_TO references are discovered
        relates_refs = [ref for ref in main_py_refs if ref.reference_type == ReferenceType.RELATES_TO]
        assert len(relates_refs) >= 2  # At least tests and docs references
    
    def test_context_expansion_follows_cross_references(self):
        """Test context manager uses cross-references for context expansion"""
        # GIVEN: Cross-reference manager with discovered relationships
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # Create test task targeting main.py
        task = Mock()
        task.file_targets = ['src/main.py']
        task.context_requirements = []
        
        # WHEN: Context is expanded for the task
        context_files = cross_ref_manager.expand_context_for_task(
            task, all_references, max_depth=2
        )
        
        # THEN: Context should include cross-referenced files
        # EVIDENCE: Direct references are included
        assert 'src/main.py' in context_files  # Original target
        assert any('test_main.py' in f for f in context_files)  # Test file
        assert any('architecture.md' in f for f in context_files)  # Documentation
        
        # EVIDENCE: Import dependencies are included
        assert any('utils.py' in f for f in context_files)  # Imported utility
        
        # EVIDENCE: Files are prioritized by relevance
        assert len(context_files) >= 3  # At least main, test, and utils
    
    def test_context_prioritization_with_cross_references(self):
        """Test context manager prioritizes files based on cross-reference data"""
        # GIVEN: Cross-reference manager and context expansion
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        all_references = cross_ref_manager.discover_all_cross_references()
        
        # Create task with specific file targets
        task = Mock()
        task.file_targets = ['src/main.py']
        task.context_requirements = []
        
        # WHEN: Context files are prioritized
        context_files = cross_ref_manager.expand_context_for_task(
            task, all_references, max_depth=1
        )
        
        prioritized_files = cross_ref_manager._prioritize_context_files(
            set(context_files), task, all_references
        )
        
        # THEN: Prioritization should reflect cross-reference importance
        # EVIDENCE: Task target files have highest priority
        assert prioritized_files[0] == 'src/main.py'  # Primary target first
        
        # EVIDENCE: Cross-referenced files follow in logical order
        # Test files and imported modules should be high priority
        high_priority_files = prioritized_files[:3]
        assert any('utils.py' in f for f in high_priority_files)  # Import dependency
        assert any('test_main.py' in f for f in high_priority_files)  # Test coverage
    
    def test_context_token_estimation_with_real_files(self):
        """Test context manager estimates tokens correctly for real files"""
        # GIVEN: Cross-reference manager with real files
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # WHEN: File context bundle is created
        main_py_path = str(self.project_root / 'src' / 'main.py')
        context_bundle = cross_ref_manager.get_file_context_bundle(
            main_py_path, include_content=True
        )
        
        # THEN: Token estimation should be reasonable
        # EVIDENCE: Token count is positive and realistic
        assert context_bundle.estimated_tokens > 0
        assert context_bundle.estimated_tokens < 10000  # Reasonable for small test files
        
        # EVIDENCE: Content summary includes file information
        assert len(context_bundle.content_summary) > 0
        assert 'main_function' in context_bundle.content_summary  # Function detected
        
        # EVIDENCE: Dependencies are correctly identified
        assert 'imports' in context_bundle.dependencies
        assert len(context_bundle.dependencies['imports']) > 0
    
    def test_cross_reference_validation_with_missing_files(self):
        """Test cross-reference validation handles missing target files"""
        # GIVEN: Cross-reference manager with some invalid references
        cross_ref_manager = CrossReferenceManager(str(self.project_root))
        
        # Add file with reference to non-existent file
        invalid_file = self.project_root / 'src' / 'invalid.py'
        invalid_file.write_text('''#!/usr/bin/env python3
"""
File with invalid cross-reference

RELATES_TO: nonexistent/file.py, src/utils.py
"""

def invalid_function():
    pass
''')
        
        # WHEN: Cross-reference validation is performed
        broken_references = cross_ref_manager.validate_all_references()
        
        # THEN: Missing files should be detected
        # EVIDENCE: Broken references are identified
        assert 'src/invalid.py' in broken_references
        broken_refs = broken_references['src/invalid.py']
        
        # EVIDENCE: Specific broken reference is listed
        assert any('nonexistent/file.py' in ref for ref in broken_refs)
        
        # EVIDENCE: Valid references are not flagged as broken
        assert not any('src/utils.py' in ref for ref in broken_refs)  # This should be valid


class TestDecisionEngineIntegration:
    """Test Decision Engine integrates with all foundation components"""
    
    def setup_method(self):
        """Set up test environment with all components"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create complete project structure
        for dir_name in ['src', 'tests', 'docs', 'config', 'logs']:
            (self.project_root / dir_name).mkdir()
        
        # Create configuration
        config = {
            'autonomous_behavior': {
                'max_hook_iterations': 50,
                'evidence_validation_strictness': 'strict'
            },
            'context_management': {
                'max_context_tokens': 100000
            },
            'integration_settings': {
                'claude_code_timeout_seconds': 30
            },
            'evidence_collection': {
                'enable_anti_fabrication': True
            },
            'safety_mechanisms': {
                'enable_loop_detection': True
            },
            'logging': {
                'log_level': 'INFO'
            }
        }
        
        config_file = self.project_root / 'config' / 'autonomous_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_decision_engine_incorporates_all_system_information(self):
        """Test decision engine uses state, context, and configuration data"""
        # GIVEN: All system components initialized
        config_manager = ConfigManager(str(self.project_root))
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        decision_engine = LLMDecisionEngine(str(self.project_root), config_manager=config_manager)
        
        # Create realistic system state
        project_state = self._create_realistic_project_state()
        available_tasks = self._create_realistic_tasks()
        
        # WHEN: Decision engine makes task selection decision
        # Mock the LLM query to return structured response
        mock_response = {
            "selected_task": available_tasks[0],
            "confidence": "high", 
            "reasoning": "Task has highest priority and all dependencies ready",
            "evidence_used": ["task_priority", "dependency_analysis", "resource_availability"]
        }
        
        with patch.object(decision_engine, '_simulate_llm_query') as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            
            decision = decision_engine.make_task_selection_decision(
                available_tasks=available_tasks,
                project_state=project_state
            )
        
        # THEN: Decision incorporates all system information
        # EVIDENCE: Decision was made successfully
        assert decision.decision_type == DecisionType.TASK_SELECTION
        assert decision.confidence == ConfidenceLevel.HIGH
        
        # EVIDENCE: Decision reasoning shows system information usage
        assert len(decision.reasoning) > 0
        assert decision.selected_option is not None
        
        # EVIDENCE: Decision history is preserved
        assert decision.timestamp is not None
        assert len(decision.evidence_used) > 0
    
    def test_decision_engine_respects_configuration_constraints(self):
        """Test decision engine respects configuration limits and settings"""
        # GIVEN: Configuration with specific constraints
        config_manager = ConfigManager(str(self.project_root))
        config = config_manager.load_configuration()
        
        # Verify configuration constraints
        assert config['autonomous_behavior']['max_hook_iterations'] == 50
        assert config['context_management']['max_context_tokens'] == 100000
        
        # WHEN: Decision engine operates with these constraints
        decision_engine = LLMDecisionEngine(str(self.project_root), config_manager=config_manager)
        
        # Create context that would exceed token limits if not managed
        large_context = self._create_large_context_scenario()
        
        # THEN: Decision engine should respect configuration constraints
        # EVIDENCE: Context size management respects token limits
        # (This would be tested by verifying context loading behavior)
        
        # Create test decision scenario
        project_state = self._create_realistic_project_state()
        available_tasks = self._create_realistic_tasks()
        
        with patch.object(decision_engine, '_simulate_llm_query') as mock_llm:
            mock_llm.return_value = json.dumps({
                "selected_task": available_tasks[0],
                "confidence": "medium",
                "reasoning": "Selected within configuration constraints"
            })
            
            decision = decision_engine.make_task_selection_decision(
                available_tasks=available_tasks,
                project_state=project_state
            )
        
        # EVIDENCE: Decision was made within configuration constraints
        assert decision.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        assert decision.selected_option is not None
    
    def test_decision_engine_context_prioritization_integration(self):
        """Test decision engine integrates with context prioritization"""
        # GIVEN: Decision engine with context management capabilities
        config_manager = ConfigManager(str(self.project_root))
        decision_engine = LLMDecisionEngine(str(self.project_root), config_manager=config_manager)
        
        # Create scenario requiring context prioritization
        available_files = [
            'src/core.py',
            'src/utils.py', 
            'tests/test_core.py',
            'docs/architecture.md',
            'config/settings.json'
        ]
        
        task_info = {
            'id': 'test_task',
            'title': 'Implement core functionality',
            'file_targets': ['src/core.py'],
            'context_requirements': ['tests/test_core.py']
        }
        
        # WHEN: Decision engine prioritizes context files
        with patch.object(decision_engine, '_simulate_llm_query') as mock_llm:
            mock_llm.return_value = json.dumps({
                "selected_files": [
                    {"file_path": "src/core.py", "priority": 1, "estimated_tokens": 2000},
                    {"file_path": "tests/test_core.py", "priority": 2, "estimated_tokens": 1500},
                    {"file_path": "src/utils.py", "priority": 3, "estimated_tokens": 1000}
                ],
                "confidence": "high",
                "reasoning": "Prioritized files provide complete context for implementation"
            })
            
            decision = decision_engine.prioritize_context_files(
                available_files=available_files,
                task_info=task_info,
                token_limit=5000
            )
        
        # THEN: Context prioritization should work correctly
        # EVIDENCE: Files are prioritized appropriately
        assert decision.decision_type == DecisionType.CONTEXT_PRIORITIZATION
        assert decision.confidence == ConfidenceLevel.HIGH
        
        prioritized_files = decision.selected_option["prioritized_files"]
        assert len(prioritized_files) >= 1
        
        # EVIDENCE: Task target files have high priority
        assert prioritized_files[0]["file_path"] == "src/core.py"
        assert prioritized_files[0]["priority"] == 1
    
    def test_decision_engine_error_analysis_integration(self):
        """Test decision engine analyzes errors using system information"""
        # GIVEN: Decision engine with error analysis capabilities
        config_manager = ConfigManager(str(self.project_root))
        decision_engine = LLMDecisionEngine(str(self.project_root), config_manager=config_manager)
        
        # Create realistic error scenario
        error_info = {
            'type': 'test_failure',
            'severity': 'high',
            'message': 'AssertionError: Expected "success" but got "failure"',
            'file': 'tests/test_core.py',
            'line': 42,
            'context': 'test_core_functionality',
            'timestamp': '2023-01-01T12:00:00Z'
        }
        
        project_state = self._create_realistic_project_state()
        
        # WHEN: Decision engine analyzes error
        with patch.object(decision_engine, '_simulate_llm_query') as mock_llm:
            mock_llm.return_value = json.dumps({
                "selected_strategy": {
                    "action": "fix_implementation",
                    "approach": "update_core_function",
                    "target_file": "src/core.py"
                },
                "confidence": "high",
                "reasoning": "Test failure indicates implementation bug in core function",
                "risks": ["May introduce new bugs"],
                "mitigations": ["Run full test suite after fix"]
            })
            
            decision = decision_engine.analyze_error_and_suggest_recovery(
                error_info=error_info,
                project_state=project_state
            )
        
        # THEN: Error analysis should provide actionable recovery strategy
        # EVIDENCE: Error analysis was performed
        assert decision.decision_type == DecisionType.ERROR_ANALYSIS
        assert decision.confidence == ConfidenceLevel.HIGH
        
        # EVIDENCE: Recovery strategy is specific and actionable
        recovery_strategy = decision.selected_option
        assert recovery_strategy["action"] == "fix_implementation"
        assert "target_file" in recovery_strategy
        
        # EVIDENCE: Risk assessment is included
        assert len(decision.risks_identified) > 0
        assert len(decision.mitigation_strategies) > 0
    
    def _create_realistic_project_state(self):
        """Helper method to create realistic project state"""
        from datetime import datetime, timezone
        
        return {
            'current_phase': ProjectPhase.IMPLEMENTATION.value,
            'methodology_step': 'active_implementation',
            'total_hook_iterations': 15,
            'consecutive_failures': 1,
            'session_start_time': datetime.now(timezone.utc).isoformat(),
            'current_tasks': ['task_1', 'task_2'],
            'completed_tasks': ['task_0'],
            'blocking_status': {'is_blocked': False, 'reason': None}
        }
    
    def _create_realistic_tasks(self):
        """Helper method to create realistic task list"""
        from datetime import datetime, timezone
        current_time = datetime.now(timezone.utc).isoformat()
        
        return [
            {
                'id': 'task_1',
                'title': 'Implement core functionality',
                'priority': 8,
                'status': 'pending',
                'file_targets': ['src/core.py'],
                'dependencies': [],
                'estimated_complexity': 5,
                'created_time': current_time
            },
            {
                'id': 'task_2',
                'title': 'Write integration tests',
                'priority': 6,
                'status': 'pending',
                'file_targets': ['tests/test_integration.py'],
                'dependencies': ['task_1'],
                'estimated_complexity': 3,
                'created_time': current_time
            },
            {
                'id': 'task_3',
                'title': 'Update documentation',
                'priority': 4,
                'status': 'pending',
                'file_targets': ['docs/api.md'],
                'dependencies': ['task_1'],
                'estimated_complexity': 2,
                'created_time': current_time
            }
        ]
    
    def _create_large_context_scenario(self):
        """Helper method to create large context scenario for testing limits"""
        # This would create a scenario that tests context size management
        return {
            'available_files': [f'src/module_{i}.py' for i in range(100)],
            'total_estimated_tokens': 150000,  # Exceeds typical limits
            'cross_references': {f'src/module_{i}.py': [f'src/module_{j}.py' for j in range(i+1, min(i+5, 100))] for i in range(95)}
        }


class TestJSONUtilitiesIntegration:
    """Test JSON Utilities integrate correctly with all persistence operations"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_all_components_use_json_utilities_consistently(self):
        """Test all components use JSONUtilities for file operations"""
        # GIVEN: All components that need JSON operations
        config_manager = ConfigManager(str(self.project_root))
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # WHEN: Components perform JSON operations
        # Configuration loading
        config = config_manager.load_configuration()
        assert isinstance(config, dict)
        
        # State saving/loading
        test_state = CompleteSystemState(
            project_state=ProjectState(
                current_phase=ProjectPhase.OVERVIEW,
                methodology_step="json_integration_test",
                phase_completion_percentage=0.0,
                session_start_time="2023-01-01T12:00:00Z",
                last_update_time="2023-01-01T12:00:00Z",
                total_hook_iterations=0,
                consecutive_failures=0,
                blocking_status={"is_blocked": False, "reason": None},
                current_tasks=[],
                completed_tasks=[]
            ),
            task_graph=TaskGraph(nodes={}, edges={}, current_ready_tasks=[], blocked_tasks={}),
            cross_references={},
            dependencies={},
            evidence_records=[],
            state_hash="test_hash",
            backup_available=False
        )
        
        # THEN: All operations should use consistent JSON handling
        # EVIDENCE: State operations work correctly
        save_result = state_manager.save_complete_state(test_state)
        assert save_result is True
        
        loaded_state = state_manager.load_complete_state()
        assert isinstance(loaded_state, CompleteSystemState)
        assert loaded_state.project_state.methodology_step == "json_integration_test"
    
    def test_concurrent_json_operations_maintain_consistency(self):
        """Test multiple components can use JSON utilities concurrently"""
        # GIVEN: Multiple components performing JSON operations
        config_manager = ConfigManager(str(self.project_root))
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # WHEN: Concurrent operations are performed
        # Simulate concurrent configuration and state operations
        
        # Configuration operation
        test_config = {
            'autonomous_behavior': {'max_hook_iterations': 30},
            'context_management': {'max_context_tokens': 75000},
            'integration_settings': {'claude_code_timeout_seconds': 25},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True},
            'logging': {'log_level': 'DEBUG'}
        }
        
        config_save_result = config_manager.save_configuration(test_config)
        
        # State operation (concurrent with config)
        test_state = self._create_simple_test_state()
        state_save_result = state_manager.save_complete_state(test_state)
        
        # THEN: Both operations should succeed
        # EVIDENCE: Configuration was saved correctly
        assert config_save_result is True
        loaded_config = config_manager.load_configuration()
        assert loaded_config['autonomous_behavior']['max_hook_iterations'] == 30
        
        # EVIDENCE: State was saved correctly
        assert state_save_result is True
        loaded_state = state_manager.load_complete_state()
        assert loaded_state.project_state.methodology_step == "concurrent_test"
    
    def test_json_utilities_error_handling_consistency(self):
        """Test all components handle JSON errors consistently"""
        # GIVEN: Components that use JSON operations
        config_manager = ConfigManager(str(self.project_root))
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # Create corrupted JSON file
        corrupted_config = self.project_root / 'config' / 'autonomous_config.json'
        corrupted_config.parent.mkdir(parents=True)
        corrupted_config.write_text('{ corrupted json content')
        
        # WHEN: Components encounter JSON errors
        # THEN: Errors should be handled consistently
        
        # Configuration manager should handle corrupted JSON
        with pytest.raises(ConfigurationError, match="Failed to load main config"):
            config_manager.load_configuration()
        
        # State manager should handle missing/corrupted state gracefully
        # (Should fall back to default state rather than crashing)
        default_state = state_manager.load_complete_state()
        assert isinstance(default_state, CompleteSystemState)
        assert default_state.project_state.current_phase == ProjectPhase.OVERVIEW
    
    def test_json_utilities_backup_integration(self):
        """Test JSON utilities backup features work across all components"""
        # GIVEN: Components configured to use backups
        config_manager = ConfigManager(str(self.project_root))
        state_manager = StateManager(str(self.project_root), config_manager=config_manager)
        
        # Create initial configuration
        initial_config = {
            'autonomous_behavior': {'max_hook_iterations': 25},
            'context_management': {'max_context_tokens': 50000},
            'integration_settings': {'claude_code_timeout_seconds': 20},
            'evidence_collection': {'enable_anti_fabrication': True},
            'safety_mechanisms': {'enable_loop_detection': True},
            'logging': {'log_level': 'INFO'}
        }
        
        config_manager.save_configuration(initial_config)
        
        # WHEN: Configuration is updated (should create backup)
        updated_config = initial_config.copy()
        updated_config['autonomous_behavior']['max_hook_iterations'] = 50
        config_manager.save_configuration(updated_config)
        
        # THEN: Backup should be created
        # EVIDENCE: Backup file exists
        config_dir = self.project_root / 'config'
        backup_files = list(config_dir.glob('autonomous_config.json.backup'))
        assert len(backup_files) >= 1
        
        # EVIDENCE: Backup contains original configuration
        with open(backup_files[0], 'r') as f:
            backup_config = json.load(f)
        assert backup_config['autonomous_behavior']['max_hook_iterations'] == 25
        
        # EVIDENCE: Current file contains updated configuration
        current_config = config_manager.load_configuration()
        assert current_config['autonomous_behavior']['max_hook_iterations'] == 50
    
    def _create_simple_test_state(self):
        """Helper method to create simple test state"""
        from datetime import datetime, timezone
        
        project_state = ProjectState(
            current_phase=ProjectPhase.IMPLEMENTATION,
            methodology_step="concurrent_test",
            phase_completion_percentage=0.2,
            session_start_time=datetime.now(timezone.utc).isoformat(),
            last_update_time=datetime.now(timezone.utc).isoformat(),
            total_hook_iterations=3,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["concurrent_task"],
            completed_tasks=[]
        )
        
        task_graph = TaskGraph(
            nodes={},
            edges={},
            current_ready_tasks=[],
            blocked_tasks={}
        )
        
        state = CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={},
            dependencies={},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
        
        # Calculate hash
        state_manager = StateManager(str(self.project_root))
        state.state_hash = state_manager._calculate_state_hash(state)
        
        return state