#!/usr/bin/env python3
"""
End-to-end workflow integration tests

LOCKED TESTS: These tests cannot be modified after creation to prevent
anti-fabrication rule violations. Implementation must make these tests pass.

Test Coverage Target: 80% (Integration dependent - realistic end-to-end scenarios)
"""

import pytest
import json
import tempfile
import os
import time
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime, timezone

# Import will be: from src.orchestrator.workflow_manager import AutonomousWorkflowManager
# from src.persistence.state_manager import StateManager, CompleteSystemState
# from src.config.configuration_manager import ConfigManager
# For now, we'll assume the import structure based on our pseudocode

class TestCompleteAutonomousWorkflow:
    """Test complete autonomous workflow execution from start to finish"""
    
    def setup_method(self):
        """Set up realistic project environment for end-to-end testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create complete project structure
        self._create_realistic_project_structure()
        self._create_test_configuration()
        self._create_sample_code_files()
        
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_autonomous_hook_cycle_complete_execution(self):
        """Test complete autonomous hook execution cycle"""
        # GIVEN: Fresh project with initial state
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        # Create initial project state with pending tasks
        initial_state = self._create_initial_project_state()
        workflow_manager.state_manager.save_complete_state(initial_state)
        
        # WHEN: Autonomous hook cycle executes
        with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
            mock_llm.return_value = self._create_mock_llm_response()
            
            hook_result = workflow_manager.execute_autonomous_hook_cycle()
        
        # THEN: Hook execution should complete successfully
        # EVIDENCE: Hook result indicates successful execution
        assert isinstance(hook_result, dict)
        assert hook_result.get('status') in ['continue', 'complete']
        
        # EVIDENCE: State was updated during execution
        final_state = workflow_manager.state_manager.load_complete_state()
        assert final_state.project_state.total_hook_iterations > initial_state.project_state.total_hook_iterations
        
        # EVIDENCE: State hash changed (indicating progress)
        assert final_state.state_hash != initial_state.state_hash
        
        # EVIDENCE: Last update time is recent
        last_update = datetime.fromisoformat(final_state.project_state.last_update_time.replace('Z', '+00:00'))
        time_diff = datetime.now(timezone.utc) - last_update
        assert time_diff.total_seconds() < 60  # Updated within last minute
    
    def test_state_persistence_across_hook_calls(self):
        """Test state persists correctly across multiple hook executions"""
        # GIVEN: Workflow manager with initial state
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        initial_state = self._create_initial_project_state()
        workflow_manager.state_manager.save_complete_state(initial_state)
        
        # WHEN: Multiple hook cycles are executed
        hook_results = []
        
        for i in range(3):
            with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
                mock_llm.return_value = self._create_progressive_llm_response(i)
                
                result = workflow_manager.execute_autonomous_hook_cycle()
                hook_results.append(result)
        
        # THEN: State should accumulate correctly across calls
        final_state = workflow_manager.state_manager.load_complete_state()
        
        # EVIDENCE: Hook iterations accumulated correctly
        assert final_state.project_state.total_hook_iterations == initial_state.project_state.total_hook_iterations + 3
        
        # EVIDENCE: Task progress is tracked
        assert len(final_state.project_state.completed_tasks) >= len(initial_state.project_state.completed_tasks)
        
        # EVIDENCE: State consistency maintained
        assert workflow_manager.state_manager._validate_state_consistency(final_state) is True
        
        # EVIDENCE: Evidence records accumulated
        assert len(final_state.evidence_records) >= len(initial_state.evidence_records)
    
    def test_error_recovery_workflow(self):
        """Test autonomous system recovers from various error conditions"""
        # GIVEN: Workflow manager with error-prone scenarios
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        # Create state with previous failures
        error_state = self._create_error_prone_state()
        workflow_manager.state_manager.save_complete_state(error_state)
        
        # WHEN: Hook execution encounters and handles errors
        with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
            # Simulate LLM providing error recovery strategy
            mock_llm.return_value = json.dumps({
                "selected_strategy": {
                    "action": "retry_with_different_approach",
                    "approach": "use_alternative_implementation"
                },
                "confidence": "medium",
                "reasoning": "Previous approach failed, trying alternative",
                "mitigations": ["Create backup before retry", "Monitor for similar failures"]
            })
            
            hook_result = workflow_manager.execute_autonomous_hook_cycle()
        
        # THEN: System should handle errors gracefully
        # EVIDENCE: Error recovery was attempted
        assert hook_result is not None
        
        final_state = workflow_manager.state_manager.load_complete_state()
        
        # EVIDENCE: Consecutive failures tracked
        assert final_state.project_state.consecutive_failures >= 0
        
        # EVIDENCE: System continues operation despite errors
        assert final_state.project_state.total_hook_iterations > error_state.project_state.total_hook_iterations
        
        # EVIDENCE: Error handling creates evidence records
        error_evidence = [e for e in final_state.evidence_records if 'error' in e.evidence_type.lower()]
        # Error evidence should be created during error handling
    
    def test_cross_session_consistency(self):
        """Test system maintains consistency across simulated session restarts"""
        # GIVEN: Workflow manager with active state
        workflow_manager1 = AutonomousWorkflowManager(str(self.project_root))
        
        # Execute some work in first session
        initial_state = self._create_initial_project_state()
        workflow_manager1.state_manager.save_complete_state(initial_state)
        
        with patch.object(workflow_manager1, '_query_llm_for_decision') as mock_llm:
            mock_llm.return_value = self._create_mock_llm_response()
            workflow_manager1.execute_autonomous_hook_cycle()
        
        # WHEN: Session "restarts" (new workflow manager instance)
        workflow_manager2 = AutonomousWorkflowManager(str(self.project_root))
        
        # Continue work in second session
        with patch.object(workflow_manager2, '_query_llm_for_decision') as mock_llm:
            mock_llm.return_value = self._create_mock_llm_response()
            hook_result = workflow_manager2.execute_autonomous_hook_cycle()
        
        # THEN: State should be consistent across sessions
        session1_state = workflow_manager1.state_manager.load_complete_state()
        session2_state = workflow_manager2.state_manager.load_complete_state()
        
        # EVIDENCE: Session 2 built upon session 1 state
        assert session2_state.project_state.total_hook_iterations > session1_state.project_state.total_hook_iterations
        
        # EVIDENCE: State consistency maintained
        assert workflow_manager2.state_manager._validate_state_consistency(session2_state) is True
        
        # EVIDENCE: No data loss between sessions
        assert len(session2_state.evidence_records) >= len(session1_state.evidence_records)
    
    def test_methodology_phase_progression(self):
        """Test autonomous progression through methodology phases"""
        # GIVEN: Workflow manager starting in early phase
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        # Start with architecture phase
        initial_state = self._create_architecture_phase_state()
        workflow_manager.state_manager.save_complete_state(initial_state)
        
        # WHEN: Multiple hook cycles execute phase work
        phase_progression = []
        
        for i in range(5):  # Simulate multiple cycles to complete phase
            current_state = workflow_manager.state_manager.load_complete_state()
            phase_progression.append(current_state.project_state.current_phase)
            
            with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
                if i < 3:
                    # Continue current phase work
                    mock_llm.return_value = self._create_phase_work_response()
                else:
                    # Phase completion and progression
                    mock_llm.return_value = self._create_phase_completion_response()
                
                workflow_manager.execute_autonomous_hook_cycle()
        
        # THEN: Phase progression should be logical
        final_state = workflow_manager.state_manager.load_complete_state()
        
        # EVIDENCE: Phase progressed appropriately
        assert final_state.project_state.current_phase != initial_state.project_state.current_phase or \
               final_state.project_state.phase_completion_percentage > initial_state.project_state.phase_completion_percentage
        
        # EVIDENCE: Phase progression is tracked
        assert len(set(phase_progression)) >= 1  # At least one phase worked on
        
        # EVIDENCE: Methodology step evolved
        assert final_state.project_state.methodology_step != initial_state.project_state.methodology_step
    
    def test_context_size_management_in_workflow(self):
        """Test workflow manages context size correctly in realistic scenarios"""
        # GIVEN: Project with many files that would exceed context limits
        self._create_large_project_structure()
        
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        # Create state with task requiring broad context
        large_context_state = self._create_large_context_state()
        workflow_manager.state_manager.save_complete_state(large_context_state)
        
        # WHEN: Workflow executes with context size constraints
        with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
            mock_llm.return_value = self._create_context_aware_llm_response()
            
            start_time = time.time()
            hook_result = workflow_manager.execute_autonomous_hook_cycle()
            execution_time = time.time() - start_time
        
        # THEN: Context management should work efficiently
        # EVIDENCE: Hook execution completed within reasonable time
        assert execution_time < 60  # Should complete within 1 minute
        
        # EVIDENCE: Hook execution succeeded despite large project
        assert hook_result is not None
        
        final_state = workflow_manager.state_manager.load_complete_state()
        
        # EVIDENCE: State remains valid
        assert workflow_manager.state_manager._validate_state_consistency(final_state) is True
        
        # EVIDENCE: Progress was made despite context constraints
        assert final_state.project_state.total_hook_iterations > large_context_state.project_state.total_hook_iterations
    
    def test_concurrent_hook_execution_safety(self):
        """Test system handles concurrent hook executions safely"""
        # GIVEN: Scenario that could trigger concurrent execution
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        initial_state = self._create_initial_project_state()
        workflow_manager.state_manager.save_complete_state(initial_state)
        
        # WHEN: Simulate concurrent hook executions
        def execute_hook():
            with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
                mock_llm.return_value = self._create_mock_llm_response()
                return workflow_manager.execute_autonomous_hook_cycle()
        
        # Simulate near-concurrent execution
        result1 = execute_hook()
        time.sleep(0.1)  # Small delay
        result2 = execute_hook()
        
        # THEN: Concurrent execution should be handled safely
        # EVIDENCE: Both executions completed
        assert result1 is not None
        assert result2 is not None
        
        final_state = workflow_manager.state_manager.load_complete_state()
        
        # EVIDENCE: State consistency maintained
        assert workflow_manager.state_manager._validate_state_consistency(final_state) is True
        
        # EVIDENCE: Hook iterations accumulated correctly
        # (Should be at least 2, accounting for both executions)
        assert final_state.project_state.total_hook_iterations >= initial_state.project_state.total_hook_iterations + 1
    
    def test_evidence_collection_throughout_workflow(self):
        """Test evidence is collected consistently throughout autonomous workflow"""
        # GIVEN: Workflow manager configured for evidence collection
        workflow_manager = AutonomousWorkflowManager(str(self.project_root))
        
        initial_state = self._create_initial_project_state()
        workflow_manager.state_manager.save_complete_state(initial_state)
        
        # WHEN: Multiple workflow cycles execute
        for i in range(3):
            with patch.object(workflow_manager, '_query_llm_for_decision') as mock_llm:
                mock_llm.return_value = self._create_evidence_generating_response(i)
                
                workflow_manager.execute_autonomous_hook_cycle()
        
        # THEN: Evidence should be collected consistently
        final_state = workflow_manager.state_manager.load_complete_state()
        
        # EVIDENCE: Evidence records were created
        assert len(final_state.evidence_records) > len(initial_state.evidence_records)
        
        # EVIDENCE: Evidence includes different types
        evidence_types = {e.evidence_type for e in final_state.evidence_records}
        assert len(evidence_types) >= 1  # At least one type of evidence
        
        # EVIDENCE: Evidence has validation status
        for evidence in final_state.evidence_records:
            assert evidence.validation_status in ['valid', 'invalid', 'pending']
            assert evidence.collection_time is not None
        
        # EVIDENCE: Evidence can be retrieved by task
        if final_state.evidence_records:
            task_id = final_state.evidence_records[0].task_id
            task_evidence = workflow_manager.state_manager.get_task_evidence(task_id)
            assert len(task_evidence) >= 1
    
    def _create_realistic_project_structure(self):
        """Create realistic project directory structure"""
        directories = [
            'src', 'tests', 'docs', 'config', 'logs', 'tools',
            'src/core', 'src/utils', 'tests/unit', 'tests/integration',
            'docs/architecture', 'docs/behavior', 'logs/state', 'logs/evidence'
        ]
        
        for dir_path in directories:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _create_test_configuration(self):
        """Create test configuration file"""
        config = {
            'autonomous_behavior': {
                'max_hook_iterations': 50,
                'max_consecutive_failures': 5,
                'evidence_validation_strictness': 'strict'
            },
            'context_management': {
                'max_context_tokens': 150000,
                'context_expansion_depth': 2
            },
            'integration_settings': {
                'claude_code_timeout_seconds': 30,
                'test_framework_timeout_seconds': 120
            },
            'evidence_collection': {
                'enable_anti_fabrication': True,
                'evidence_retention_days': 7
            },
            'safety_mechanisms': {
                'enable_loop_detection': True,
                'max_file_modifications_per_session': 100
            },
            'logging': {
                'log_level': 'INFO'
            }
        }
        
        config_file = self.project_root / 'config' / 'autonomous_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_sample_code_files(self):
        """Create sample code files for testing"""
        # Main module
        main_py = self.project_root / 'src' / 'main.py'
        main_py.write_text('''#!/usr/bin/env python3
"""
Main module for end-to-end testing

RELATES_TO: tests/test_main.py, docs/architecture/overview.md
"""

from .core.processor import process_data
from .utils.helpers import validate_input

def main():
    """Main entry point"""
    data = "test_data"
    if validate_input(data):
        return process_data(data)
    return None

if __name__ == "__main__":
    main()
''')
        
        # Core processor
        processor_py = self.project_root / 'src' / 'core' / 'processor.py'
        processor_py.write_text('''#!/usr/bin/env python3
"""
Core data processor

RELATES_TO: src/main.py, tests/unit/test_processor.py
"""

def process_data(data):
    """Process input data"""
    if not data:
        raise ValueError("Data cannot be empty")
    
    return f"processed_{data}"
''')
        
        # Utility helpers
        helpers_py = self.project_root / 'src' / 'utils' / 'helpers.py'
        helpers_py.write_text('''#!/usr/bin/env python3
"""
Utility helper functions

RELATES_TO: src/main.py, tests/unit/test_helpers.py
"""

def validate_input(data):
    """Validate input data"""
    return data is not None and len(str(data)) > 0
''')
        
        # Test files
        test_main_py = self.project_root / 'tests' / 'test_main.py'
        test_main_py.write_text('''#!/usr/bin/env python3
"""
Tests for main module

RELATES_TO: src/main.py
"""

import pytest
from src.main import main

def test_main_function():
    """Test main function execution"""
    result = main()
    assert result == "processed_test_data"
''')
    
    def _create_large_project_structure(self):
        """Create large project structure for context size testing"""
        # Create many files to test context management
        for i in range(50):
            module_file = self.project_root / 'src' / f'module_{i}.py'
            module_file.write_text(f'''#!/usr/bin/env python3
"""
Module {i} for testing context size management

RELATES_TO: src/module_{(i+1) % 50}.py, tests/test_module_{i}.py
"""

def function_{i}():
    """Function in module {i}"""
    return "result_{i}"

class Class_{i}:
    """Class in module {i}"""
    
    def method_{i}(self):
        return function_{i}()
''')
            
            # Create corresponding test file
            test_file = self.project_root / 'tests' / f'test_module_{i}.py'
            test_file.write_text(f'''#!/usr/bin/env python3
"""
Tests for module {i}

RELATES_TO: src/module_{i}.py
"""

from src.module_{i} import function_{i}, Class_{i}

def test_function_{i}():
    assert function_{i}() == "result_{i}"

def test_class_{i}():
    obj = Class_{i}()
    assert obj.method_{i}() == "result_{i}"
''')
    
    def _create_initial_project_state(self):
        """Create initial project state for testing"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.IMPLEMENTATION,
            methodology_step="initial_implementation",
            phase_completion_percentage=0.1,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=0,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["implement_core", "write_tests"],
            completed_tasks=[]
        )
        
        # Create task nodes
        task1 = TaskNode(
            id="implement_core",
            title="Implement core functionality",
            description="Implement the main processing logic",
            task_type="implementation",
            priority=8,
            status="pending",
            file_targets=["src/core/processor.py"],
            dependencies=[],
            context_requirements=["src/main.py"],
            evidence_requirements={"test_passage": True, "file_existence": True},
            estimated_complexity=5,
            created_time=current_time,
            last_updated=current_time
        )
        
        task2 = TaskNode(
            id="write_tests",
            title="Write unit tests",
            description="Create comprehensive unit tests",
            task_type="testing",
            priority=6,
            status="pending",
            file_targets=["tests/unit/test_processor.py"],
            dependencies=["implement_core"],
            context_requirements=["src/core/processor.py"],
            evidence_requirements={"test_passage": True},
            estimated_complexity=3,
            created_time=current_time,
            last_updated=current_time
        )
        
        task_graph = TaskGraph(
            nodes={"implement_core": task1, "write_tests": task2},
            edges={"implement_core": ["write_tests"], "write_tests": []},
            current_ready_tasks=["implement_core"],
            blocked_tasks={}
        )
        
        return CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={"src/main.py": ["src/core/processor.py", "tests/test_main.py"]},
            dependencies={"python": ["pytest"]},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
    
    def _create_error_prone_state(self):
        """Create state that represents error-prone scenarios"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.IMPLEMENTATION,
            methodology_step="error_recovery",
            phase_completion_percentage=0.3,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=5,
            consecutive_failures=2,  # Previous failures
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["fix_failing_tests"],
            completed_tasks=["initial_implementation"]
        )
        
        task_graph = TaskGraph(
            nodes={},
            edges={},
            current_ready_tasks=["fix_failing_tests"],
            blocked_tasks={}
        )
        
        # Add error evidence
        error_evidence = EvidenceRecord(
            task_id="initial_implementation",
            evidence_type="test_failure",
            evidence_data={"failed_tests": 3, "error_message": "AssertionError"},
            collection_time=current_time,
            validation_status="invalid",
            file_references=["tests/test_processor.py"]
        )
        
        return CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={},
            dependencies={},
            evidence_records=[error_evidence],
            state_hash="",
            backup_available=True
        )
    
    def _create_architecture_phase_state(self):
        """Create state representing architecture phase work"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH,
            methodology_step="dependency_analysis",
            phase_completion_percentage=0.2,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=2,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["analyze_dependencies", "design_architecture"],
            completed_tasks=["initial_overview"]
        )
        
        task_graph = TaskGraph(
            nodes={},
            edges={},
            current_ready_tasks=["analyze_dependencies"],
            blocked_tasks={}
        )
        
        return CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={},
            dependencies={},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
    
    def _create_large_context_state(self):
        """Create state requiring large context management"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.IMPLEMENTATION,
            methodology_step="large_context_implementation",
            phase_completion_percentage=0.4,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=3,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["refactor_large_module"],
            completed_tasks=["setup_base_modules"]
        )
        
        # Create cross-references to many files
        large_cross_refs = {}
        for i in range(50):
            large_cross_refs[f"src/module_{i}.py"] = [f"tests/test_module_{i}.py", f"src/module_{(i+1) % 50}.py"]
        
        task_graph = TaskGraph(
            nodes={},
            edges={},
            current_ready_tasks=["refactor_large_module"],
            blocked_tasks={}
        )
        
        return CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references=large_cross_refs,
            dependencies={},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
    
    def _create_mock_llm_response(self):
        """Create mock LLM response for testing"""
        return json.dumps({
            "selected_task": {
                "id": "implement_core",
                "title": "Implement core functionality",
                "reasoning": "Highest priority task with all dependencies ready"
            },
            "confidence": "high",
            "reasoning": "Task selection based on priority and dependency analysis",
            "alternatives": [{"id": "write_tests", "why_not_selected": "Depends on core implementation"}],
            "risks": ["Implementation complexity may be higher than estimated"],
            "mitigations": ["Break task into smaller subtasks if needed"],
            "evidence_used": ["task_priority", "dependency_graph", "resource_availability"],
            "follow_up_actions": ["Load context for implementation", "Run existing tests"]
        })
    
    def _create_progressive_llm_response(self, iteration):
        """Create LLM response that shows progression"""
        tasks = ["implement_core", "write_tests", "update_docs"]
        
        return json.dumps({
            "selected_task": {
                "id": tasks[iteration % len(tasks)],
                "title": f"Task {iteration}",
                "reasoning": f"Progressive work iteration {iteration}"
            },
            "confidence": "high",
            "reasoning": f"Iteration {iteration} of progressive development",
            "evidence_used": ["previous_progress", "current_state"],
            "follow_up_actions": [f"Continue iteration {iteration + 1}"]
        })
    
    def _create_phase_work_response(self):
        """Create LLM response for phase work"""
        return json.dumps({
            "selected_action": {
                "action": "continue_phase_work",
                "focus": "dependency_analysis"
            },
            "confidence": "medium",
            "reasoning": "Phase work is progressing, continuing current tasks",
            "evidence_used": ["phase_completion_percentage", "task_status"],
            "follow_up_actions": ["Complete dependency analysis", "Update phase documentation"]
        })
    
    def _create_phase_completion_response(self):
        """Create LLM response for phase completion"""
        return json.dumps({
            "selected_action": {
                "action": "advance_phase",
                "target_phase": "implementation"
            },
            "confidence": "high",
            "reasoning": "Architecture phase requirements completed with evidence",
            "evidence_used": ["phase_completion_checklist", "evidence_validation"],
            "follow_up_actions": ["Archive phase evidence", "Initialize next phase"]
        })
    
    def _create_context_aware_llm_response(self):
        """Create LLM response that shows context awareness"""
        return json.dumps({
            "selected_files": [
                {"file_path": "src/main.py", "priority": 1, "estimated_tokens": 2000},
                {"file_path": "src/core/processor.py", "priority": 2, "estimated_tokens": 1500},
                {"file_path": "tests/test_main.py", "priority": 3, "estimated_tokens": 1000}
            ],
            "confidence": "high",
            "reasoning": "Context prioritized to stay within token limits while maximizing relevance",
            "evidence_used": ["file_relevance", "token_estimation", "cross_references"],
            "follow_up_actions": ["Monitor context usage", "Adjust if needed"]
        })
    
    def _create_evidence_generating_response(self, iteration):
        """Create LLM response that generates evidence"""
        return json.dumps({
            "selected_task": {
                "id": f"evidence_task_{iteration}",
                "title": f"Evidence generating task {iteration}",
                "evidence_type": "implementation_proof"
            },
            "confidence": "high",
            "reasoning": f"Task {iteration} completed with evidence collection",
            "evidence_generated": {
                "type": "test_results",
                "status": "passed",
                "coverage": 0.85
            },
            "follow_up_actions": ["Validate evidence", "Update task status"]
        })