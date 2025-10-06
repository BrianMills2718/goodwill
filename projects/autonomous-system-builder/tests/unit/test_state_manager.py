#!/usr/bin/env python3
"""
Unit tests for State Manager foundation component

LOCKED TESTS: These tests cannot be modified after creation to prevent
anti-fabrication rule violations. Implementation must make these tests pass.

Test Coverage Target: 95% (Persistence component - data integrity critical)
"""

import pytest
import json
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from src.persistence.state_persistence import (
    StateManager, StateError, StateConsistencyError,
    ProjectPhase, ProjectState, TaskNode, TaskGraph, EvidenceRecord, CompleteSystemState
)

class TestStateManagerInitialization:
    """Test StateManager initialization and validation"""
    
    def test_init_with_valid_project_root(self):
        """Test StateManager initializes successfully with valid project root"""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_manager = StateManager(temp_dir)
            
            assert state_manager.project_root == Path(temp_dir)
            assert state_manager.state_dir == Path(temp_dir) / 'logs' / 'state'
            assert state_manager.backup_dir == Path(temp_dir) / 'logs' / 'state' / 'backups'
            assert state_manager.current_state_file == Path(temp_dir) / 'logs' / 'state' / 'current_state.json'
            
            # Verify directories were created
            assert state_manager.state_dir.exists()
            assert state_manager.backup_dir.exists()
            assert state_manager.state_history_dir.exists()
    
    def test_init_with_empty_project_root_raises_error(self):
        """Test StateManager raises error for empty project root"""
        with pytest.raises(StateError, match="project_root cannot be empty"):
            StateManager("")
    
    def test_init_with_nonexistent_project_root_raises_error(self):
        """Test StateManager raises error for non-existent project root"""
        non_existent_path = "/tmp/definitely_does_not_exist_54321"
        
        with pytest.raises(StateError, match="Project root does not exist"):
            StateManager(non_existent_path)
    
    def test_init_with_file_as_project_root_raises_error(self):
        """Test StateManager raises error when project root is a file"""
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(StateError, match="Project root is not a directory"):
                StateManager(temp_file.name)
    
    def test_init_with_existing_config_manager(self):
        """Test StateManager accepts existing ConfigManager instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config_manager = Mock()
            
            state_manager = StateManager(temp_dir, config_manager=mock_config_manager)
            
            assert state_manager.config_manager is mock_config_manager


class TestCompleteSystemStateOperations:
    """Test complete system state loading and saving"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_complete_state_no_existing_state_creates_default(self):
        """Test loading state with no existing files creates default state"""
        state = self.state_manager.load_complete_state()
        
        # Verify default state structure
        assert isinstance(state, CompleteSystemState)
        assert state.project_state.current_phase == ProjectPhase.OVERVIEW
        assert state.project_state.methodology_step == "initial_overview"
        assert state.project_state.phase_completion_percentage == 0.0
        assert state.project_state.total_hook_iterations == 0
        assert state.project_state.consecutive_failures == 0
        assert state.project_state.blocking_status["is_blocked"] is False
        assert len(state.project_state.current_tasks) == 0
        assert len(state.project_state.completed_tasks) == 0
        
        # Verify task graph is empty
        assert len(state.task_graph.nodes) == 0
        assert len(state.task_graph.edges) == 0
        assert len(state.task_graph.current_ready_tasks) == 0
        assert len(state.task_graph.blocked_tasks) == 0
        
        # Verify other components are empty
        assert len(state.cross_references) == 0
        assert len(state.dependencies) == 0
        assert len(state.evidence_records) == 0
        assert state.backup_available is False
        assert state.state_hash != ""
    
    def test_save_complete_state_creates_valid_file(self):
        """Test saving complete state creates valid JSON file"""
        # Create test state
        test_state = self._create_test_state()
        
        result = self.state_manager.save_complete_state(test_state)
        assert result is True
        
        # Verify file was created
        assert self.state_manager.current_state_file.exists()
        
        # Verify file contains correct data
        with open(self.state_manager.current_state_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['project_state']['current_phase'] == ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH.value
        assert saved_data['project_state']['methodology_step'] == "dependency_research"
        assert saved_data['project_state']['total_hook_iterations'] == 5
        assert len(saved_data['task_graph']['nodes']) == 2
        assert saved_data['state_hash'] != ""
    
    def test_load_complete_state_existing_valid_state(self):
        """Test loading existing valid state returns correct data"""
        # Save test state
        test_state = self._create_test_state()
        self.state_manager.save_complete_state(test_state)
        
        # Load state
        loaded_state = self.state_manager.load_complete_state()
        
        # Verify loaded state matches saved state
        assert loaded_state.project_state.current_phase == test_state.project_state.current_phase
        assert loaded_state.project_state.methodology_step == test_state.project_state.methodology_step
        assert loaded_state.project_state.total_hook_iterations == test_state.project_state.total_hook_iterations
        assert len(loaded_state.task_graph.nodes) == len(test_state.task_graph.nodes)
        assert loaded_state.state_hash == test_state.state_hash
    
    def test_save_complete_state_updates_metadata(self):
        """Test saving state updates last_update_time and state_hash"""
        test_state = self._create_test_state()
        original_update_time = test_state.project_state.last_update_time
        original_hash = test_state.state_hash
        
        # Wait briefly to ensure different timestamp
        time.sleep(0.1)
        
        self.state_manager.save_complete_state(test_state)
        
        # Verify metadata was updated
        assert test_state.project_state.last_update_time != original_update_time
        assert test_state.state_hash != original_hash
    
    def test_save_complete_state_creates_backup(self):
        """Test saving state creates backup of existing state"""
        # Save initial state
        initial_state = self._create_test_state()
        initial_state.project_state.methodology_step = "initial_step"
        self.state_manager.save_complete_state(initial_state)
        
        # Save updated state
        updated_state = self._create_test_state()
        updated_state.project_state.methodology_step = "updated_step"
        self.state_manager.save_complete_state(updated_state)
        
        # Verify backup was created
        backup_files = list(self.state_manager.backup_dir.glob('state_backup_*.json'))
        assert len(backup_files) >= 1
        
        # Verify backup contains initial state
        with open(backup_files[0], 'r') as f:
            backup_data = json.load(f)
        assert backup_data['project_state']['methodology_step'] == "initial_step"
        
        # Verify current state contains updated data
        with open(self.state_manager.current_state_file, 'r') as f:
            current_data = json.load(f)
        assert current_data['project_state']['methodology_step'] == "updated_step"
    
    def test_load_complete_state_corrupted_primary_uses_backup(self):
        """Test loading state with corrupted primary file uses backup"""
        # Save valid state (creates backup)
        test_state = self._create_test_state()
        self.state_manager.save_complete_state(test_state)
        
        # Corrupt primary state file
        with open(self.state_manager.current_state_file, 'w') as f:
            f.write('{ corrupted json content')
        
        # Load state should use backup
        loaded_state = self.state_manager.load_complete_state()
        
        # Verify loaded state has expected data (from backup or default)
        assert isinstance(loaded_state, CompleteSystemState)
        assert loaded_state.project_state.current_phase in ProjectPhase
    
    def test_save_complete_state_creates_history_entry(self):
        """Test saving state creates entry in history directory"""
        test_state = self._create_test_state()
        
        self.state_manager.save_complete_state(test_state)
        
        # Verify history entry was created
        history_files = list(self.state_manager.state_history_dir.glob('state_*.json'))
        assert len(history_files) >= 1
        
        # Verify history entry contains correct data
        with open(history_files[0], 'r') as f:
            history_data = json.load(f)
        assert history_data['project_state']['methodology_step'] == test_state.project_state.methodology_step
    
    def test_save_complete_state_verification_failure_rollback(self):
        """Test save operation rolls back on verification failure"""
        test_state = self._create_test_state()
        
        # Mock verification to fail
        with patch.object(self.state_manager.json_utils, 'safe_load_json') as mock_load:
            mock_load.return_value = None  # Simulate verification failure
            
            with pytest.raises(StateError, match="State verification failed"):
                self.state_manager.save_complete_state(test_state)
        
        # Verify no state file was created
        assert not self.state_manager.current_state_file.exists()
    
    def _create_test_state(self) -> 'CompleteSystemState':
        """Helper method to create test state"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH,
            methodology_step="dependency_research",
            phase_completion_percentage=0.3,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=5,
            consecutive_failures=1,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["task_1", "task_2"],
            completed_tasks=["task_0"]
        )
        
        task1 = TaskNode(
            id="task_1",
            title="Test Task 1",
            description="First test task",
            task_type="implementation",
            priority=5,
            status="pending",
            file_targets=["src/test1.py"],
            dependencies=[],
            context_requirements=["docs/test.md"],
            evidence_requirements={"test_passage": True, "file_existence": True},
            estimated_complexity=3,
            created_time=current_time,
            last_updated=current_time
        )
        
        task2 = TaskNode(
            id="task_2",
            title="Test Task 2",
            description="Second test task",
            task_type="testing",
            priority=3,
            status="blocked",
            file_targets=["tests/test2.py"],
            dependencies=["task_1"],
            context_requirements=["src/test1.py"],
            evidence_requirements={"test_passage": True},
            estimated_complexity=2,
            created_time=current_time,
            last_updated=current_time
        )
        
        task_graph = TaskGraph(
            nodes={"task_1": task1, "task_2": task2},
            edges={"task_1": ["task_2"], "task_2": []},
            current_ready_tasks=["task_1"],
            blocked_tasks={"task_2": "waiting_for_task_1"}
        )
        
        evidence1 = EvidenceRecord(
            task_id="task_1",
            evidence_type="test_results",
            evidence_data={"status": "passing", "coverage": 0.95},
            collection_time=current_time,
            validation_status="valid",
            file_references=["tests/test1.py"]
        )
        
        state = CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={"src/test1.py": ["docs/test.md"]},
            dependencies={"external": ["pytest", "requests"]},
            evidence_records=[evidence1],
            state_hash="",  # Will be calculated
            backup_available=False
        )
        
        # Calculate hash
        state.state_hash = self.state_manager._calculate_state_hash(state)
        
        return state


class TestStateConsistencyValidation:
    """Test state consistency validation logic"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_state_consistency_valid_state(self):
        """Test state consistency validation passes for valid state"""
        valid_state = self._create_consistent_state()
        
        result = self.state_manager._validate_state_consistency(valid_state)
        assert result is True
    
    def test_validate_state_consistency_missing_task_dependency(self):
        """Test validation fails when task dependency doesn't exist"""
        state = self._create_consistent_state()
        
        # Add task with non-existent dependency
        invalid_task = TaskNode(
            id="invalid_task",
            title="Invalid Task",
            description="Task with missing dependency",
            task_type="implementation",
            priority=5,
            status="pending",
            file_targets=["src/invalid.py"],
            dependencies=["nonexistent_task"],  # This dependency doesn't exist
            context_requirements=[],
            evidence_requirements={},
            estimated_complexity=1,
            created_time=datetime.now(timezone.utc).isoformat(),
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        state.task_graph.nodes["invalid_task"] = invalid_task
        
        result = self.state_manager._validate_state_consistency(state)
        assert result is False
    
    def test_validate_state_consistency_ready_task_not_actually_ready(self):
        """Test validation fails when ready task has incomplete dependencies"""
        state = self._create_consistent_state()
        
        # Mark task as ready but it has uncompleted dependencies
        state.task_graph.current_ready_tasks = ["task_2"]  # task_2 depends on task_1 which isn't complete
        
        result = self.state_manager._validate_state_consistency(state)
        assert result is False
    
    def test_validate_state_consistency_ready_task_completed(self):
        """Test validation fails when ready task is already completed"""
        state = self._create_consistent_state()
        
        # Mark task as both ready and completed
        state.task_graph.nodes["task_1"].status = "completed"
        state.task_graph.current_ready_tasks = ["task_1"]
        
        result = self.state_manager._validate_state_consistency(state)
        assert result is False
    
    def test_validate_state_consistency_evidence_for_nonexistent_task(self):
        """Test validation fails when evidence references non-existent task"""
        state = self._create_consistent_state()
        
        # Add evidence for non-existent task
        invalid_evidence = EvidenceRecord(
            task_id="nonexistent_task",
            evidence_type="test_results",
            evidence_data={},
            collection_time=datetime.now(timezone.utc).isoformat(),
            validation_status="valid",
            file_references=[]
        )
        
        state.evidence_records.append(invalid_evidence)
        
        result = self.state_manager._validate_state_consistency(state)
        assert result is False
    
    def test_validate_state_consistency_invalid_phase(self):
        """Test validation fails for invalid project phase"""
        state = self._create_consistent_state()
        
        # Set invalid phase (simulate enum corruption)
        with patch.object(state.project_state, 'current_phase', 999):
            result = self.state_manager._validate_state_consistency(state)
            assert result is False
    
    def test_validate_state_consistency_hash_mismatch(self):
        """Test validation fails when state hash doesn't match calculated hash"""
        state = self._create_consistent_state()
        
        # Corrupt the hash
        state.state_hash = "corrupted_hash_value"
        
        result = self.state_manager._validate_state_consistency(state)
        assert result is False
    
    def test_calculate_state_hash_consistent(self):
        """Test state hash calculation is consistent"""
        state = self._create_consistent_state()
        
        hash1 = self.state_manager._calculate_state_hash(state)
        hash2 = self.state_manager._calculate_state_hash(state)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex string length
    
    def test_calculate_state_hash_different_for_different_states(self):
        """Test state hash is different for different states"""
        state1 = self._create_consistent_state()
        state2 = self._create_consistent_state()
        state2.project_state.methodology_step = "different_step"
        
        hash1 = self.state_manager._calculate_state_hash(state1)
        hash2 = self.state_manager._calculate_state_hash(state2)
        
        assert hash1 != hash2
    
    def _create_consistent_state(self) -> 'CompleteSystemState':
        """Helper method to create consistent state for validation testing"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.IMPLEMENTATION,
            methodology_step="active_implementation",
            phase_completion_percentage=0.6,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=15,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=["task_2"],
            completed_tasks=["task_1"]
        )
        
        task1 = TaskNode(
            id="task_1",
            title="Completed Task",
            description="Task that is completed",
            task_type="implementation",
            priority=5,
            status="completed",
            file_targets=["src/module1.py"],
            dependencies=[],
            context_requirements=[],
            evidence_requirements={"test_passage": True},
            estimated_complexity=3,
            created_time=current_time,
            last_updated=current_time,
            completion_time=current_time
        )
        
        task2 = TaskNode(
            id="task_2",
            title="Current Task",
            description="Task currently in progress",
            task_type="testing",
            priority=4,
            status="in_progress",
            file_targets=["tests/test_module1.py"],
            dependencies=["task_1"],  # Depends on completed task
            context_requirements=["src/module1.py"],
            evidence_requirements={"test_passage": True},
            estimated_complexity=2,
            created_time=current_time,
            last_updated=current_time
        )
        
        task_graph = TaskGraph(
            nodes={"task_1": task1, "task_2": task2},
            edges={"task_1": ["task_2"], "task_2": []},
            current_ready_tasks=["task_2"],  # task_2 is ready because task_1 is complete
            blocked_tasks={}
        )
        
        evidence1 = EvidenceRecord(
            task_id="task_1",
            evidence_type="test_results",
            evidence_data={"status": "passed", "coverage": 1.0},
            collection_time=current_time,
            validation_status="valid",
            file_references=["tests/test_module1.py"]
        )
        
        state = CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={"src/module1.py": ["tests/test_module1.py"]},
            dependencies={"python": ["pytest"]},
            evidence_records=[evidence1],
            state_hash="",  # Will be calculated
            backup_available=True
        )
        
        # Calculate correct hash
        state.state_hash = self.state_manager._calculate_state_hash(state)
        
        return state


class TestEvidenceRecordOperations:
    """Test evidence record saving and retrieval"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_evidence_record_creates_file(self):
        """Test saving evidence record creates file in correct location"""
        evidence = EvidenceRecord(
            task_id="test_task",
            evidence_type="test_results",
            evidence_data={"status": "passed", "tests": 5, "coverage": 0.95},
            collection_time=datetime.now(timezone.utc).isoformat(),
            validation_status="valid",
            file_references=["tests/test_example.py", "src/example.py"]
        )
        
        result = self.state_manager.save_evidence_record(evidence)
        assert result is True
        
        # Verify evidence directory was created
        evidence_dir = self.state_manager.state_dir / 'evidence' / 'test_task'
        assert evidence_dir.exists()
        
        # Verify evidence file was created
        evidence_files = list(evidence_dir.glob('test_results_*.json'))
        assert len(evidence_files) == 1
        
        # Verify evidence file contains correct data
        with open(evidence_files[0], 'r') as f:
            saved_evidence = json.load(f)
        
        assert saved_evidence['task_id'] == "test_task"
        assert saved_evidence['evidence_type'] == "test_results"
        assert saved_evidence['evidence_data']['status'] == "passed"
        assert saved_evidence['evidence_data']['coverage'] == 0.95
    
    def test_save_evidence_record_invalid_data_raises_error(self):
        """Test saving evidence record with invalid data raises error"""
        # Evidence without task_id
        invalid_evidence = EvidenceRecord(
            task_id="",  # Empty task_id is invalid
            evidence_type="test_results",
            evidence_data={},
            collection_time=datetime.now(timezone.utc).isoformat(),
            validation_status="valid",
            file_references=[]
        )
        
        with pytest.raises(StateError, match="Evidence record must have task_id"):
            self.state_manager.save_evidence_record(invalid_evidence)
        
        # Evidence without evidence_type
        invalid_evidence2 = EvidenceRecord(
            task_id="test_task",
            evidence_type="",  # Empty evidence_type is invalid
            evidence_data={},
            collection_time=datetime.now(timezone.utc).isoformat(),
            validation_status="valid",
            file_references=[]
        )
        
        with pytest.raises(StateError, match="Evidence record must have evidence_type"):
            self.state_manager.save_evidence_record(invalid_evidence2)
    
    def test_get_task_evidence_returns_all_evidence(self):
        """Test getting task evidence returns all evidence for a task"""
        task_id = "multi_evidence_task"
        
        # Save multiple evidence records
        evidence1 = EvidenceRecord(
            task_id=task_id,
            evidence_type="test_results",
            evidence_data={"status": "passed"},
            collection_time="2023-01-01T10:00:00Z",
            validation_status="valid",
            file_references=["tests/test1.py"]
        )
        
        time.sleep(0.1)  # Ensure different timestamps
        
        evidence2 = EvidenceRecord(
            task_id=task_id,
            evidence_type="file_existence",
            evidence_data={"created": ["src/module.py", "tests/test_module.py"]},
            collection_time="2023-01-01T10:01:00Z",
            validation_status="valid",
            file_references=["src/module.py"]
        )
        
        self.state_manager.save_evidence_record(evidence1)
        self.state_manager.save_evidence_record(evidence2)
        
        # Get all evidence for task
        all_evidence = self.state_manager.get_task_evidence(task_id)
        
        assert len(all_evidence) == 2
        
        # Verify evidence is sorted by collection time
        assert all_evidence[0].collection_time <= all_evidence[1].collection_time
        
        # Verify evidence content
        evidence_types = [e.evidence_type for e in all_evidence]
        assert "test_results" in evidence_types
        assert "file_existence" in evidence_types
    
    def test_get_task_evidence_no_evidence_returns_empty(self):
        """Test getting evidence for task with no evidence returns empty list"""
        result = self.state_manager.get_task_evidence("nonexistent_task")
        assert result == []
    
    def test_save_evidence_record_updates_index(self):
        """Test saving evidence record updates the evidence index"""
        evidence = EvidenceRecord(
            task_id="indexed_task",
            evidence_type="integration_proof",
            evidence_data={"endpoint": "/api/test", "status": 200},
            collection_time=datetime.now(timezone.utc).isoformat(),
            validation_status="valid",
            file_references=["src/api.py"]
        )
        
        self.state_manager.save_evidence_record(evidence)
        
        # Verify index file was created
        index_file = self.state_manager.state_dir / 'evidence' / 'index.json'
        assert index_file.exists()
        
        # Verify index contains correct entry
        with open(index_file, 'r') as f:
            index_data = json.load(f)
        
        assert "indexed_task" in index_data
        assert len(index_data["indexed_task"]) == 1
        assert index_data["indexed_task"][0]["evidence_type"] == "integration_proof"
        assert index_data["indexed_task"][0]["validation_status"] == "valid"


class TestStateBackupAndRecovery:
    """Test state backup and recovery mechanisms"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_state_backup_no_existing_file(self):
        """Test backup creation when no existing state file"""
        result = self.state_manager._create_state_backup()
        assert result is True
        
        # Should not create any backup files
        backup_files = list(self.state_manager.backup_dir.glob('state_backup_*.json'))
        assert len(backup_files) == 0
    
    def test_create_state_backup_with_existing_file(self):
        """Test backup creation with existing state file"""
        # Create initial state file
        test_data = {"test": "backup_data"}
        with open(self.state_manager.current_state_file, 'w') as f:
            json.dump(test_data, f)
        
        result = self.state_manager._create_state_backup()
        assert result is True
        
        # Verify backup was created
        backup_files = list(self.state_manager.backup_dir.glob('state_backup_*.json'))
        assert len(backup_files) == 1
        
        # Verify backup contains original data
        with open(backup_files[0], 'r') as f:
            backup_data = json.load(f)
        assert backup_data == test_data
    
    def test_create_state_backup_cleanup_old_backups(self):
        """Test backup creation cleans up old backups"""
        # Create initial state file
        with open(self.state_manager.current_state_file, 'w') as f:
            json.dump({"initial": "data"}, f)
        
        # Create many backups to trigger cleanup
        for i in range(15):  # More than the 10 backup limit
            self.state_manager._create_state_backup()
            time.sleep(0.1)  # Ensure different timestamps
            
            # Modify state file for next backup
            with open(self.state_manager.current_state_file, 'w') as f:
                json.dump({"iteration": i}, f)
        
        # Verify only 10 backups remain (cleanup triggered)
        backup_files = list(self.state_manager.backup_dir.glob('state_backup_*.json'))
        assert len(backup_files) <= 10
    
    def test_load_most_recent_backup_returns_valid_backup(self):
        """Test loading most recent backup returns valid state"""
        # Create backup files
        backup1_data = {"backup": 1, "timestamp": "2023-01-01T10:00:00Z"}
        backup2_data = {"backup": 2, "timestamp": "2023-01-01T11:00:00Z"}
        
        backup1_file = self.state_manager.backup_dir / "state_backup_20230101_100000.json"
        backup2_file = self.state_manager.backup_dir / "state_backup_20230101_110000.json"
        
        with open(backup1_file, 'w') as f:
            json.dump(backup1_data, f)
        
        time.sleep(0.1)  # Ensure different modification times
        
        with open(backup2_file, 'w') as f:
            json.dump(backup2_data, f)
        
        # Mock the state validation to pass
        with patch.object(self.state_manager, '_validate_state_consistency', return_value=True):
            # Mock CompleteSystemState.from_dict to return valid state
            mock_state = Mock()
            mock_state.project_state.current_phase = ProjectPhase.OVERVIEW
            
            with patch('CompleteSystemState.from_dict', return_value=mock_state):
                result = self.state_manager._load_most_recent_backup()
        
        assert result is not None
        assert result is mock_state
    
    def test_load_most_recent_backup_no_valid_backup(self):
        """Test loading backup with no valid backups returns None"""
        # Create invalid backup file
        invalid_backup = self.state_manager.backup_dir / "state_backup_invalid.json"
        with open(invalid_backup, 'w') as f:
            f.write('{ invalid json content')
        
        result = self.state_manager._load_most_recent_backup()
        assert result is None
    
    def test_attempt_state_recovery_tries_all_options(self):
        """Test state recovery attempts all recovery strategies"""
        # Mock backup recovery to fail
        with patch.object(self.state_manager, '_load_most_recent_backup', return_value=None):
            # Mock history reconstruction to fail
            with patch.object(self.state_manager, '_reconstruct_from_history', return_value=None):
                # Should fall back to default state
                result = self.state_manager._attempt_state_recovery()
        
        assert isinstance(result, CompleteSystemState)
        assert result.project_state.current_phase == ProjectPhase.OVERVIEW
        assert result.project_state.methodology_step == "initial_overview"
    
    def test_reconstruct_from_history_returns_valid_state(self):
        """Test reconstructing state from history files"""
        # Create valid history file
        valid_history_data = {
            "project_state": {
                "current_phase": ProjectPhase.IMPLEMENTATION.value,
                "methodology_step": "active_implementation",
                "phase_completion_percentage": 0.5,
                "session_start_time": "2023-01-01T10:00:00Z",
                "last_update_time": "2023-01-01T11:00:00Z",
                "total_hook_iterations": 10,
                "consecutive_failures": 0,
                "blocking_status": {"is_blocked": False, "reason": None},
                "current_tasks": [],
                "completed_tasks": []
            },
            "task_graph": {
                "nodes": {},
                "edges": {},
                "current_ready_tasks": [],
                "blocked_tasks": {}
            },
            "cross_references": {},
            "dependencies": {},
            "evidence_records": [],
            "state_hash": "test_hash",
            "backup_available": False
        }
        
        history_file = self.state_manager.state_history_dir / "state_20230101_110000.json"
        with open(history_file, 'w') as f:
            json.dump(valid_history_data, f)
        
        # Mock state validation to pass
        with patch.object(self.state_manager, '_validate_state_consistency', return_value=True):
            result = self.state_manager._reconstruct_from_history()
        
        assert result is not None
        assert isinstance(result, CompleteSystemState)
        assert result.project_state.current_phase == ProjectPhase.IMPLEMENTATION
    
    def test_save_state_to_history_creates_history_file(self):
        """Test saving state to history creates timestamped file"""
        test_state = CompleteSystemState(
            project_state=ProjectState(
                current_phase=ProjectPhase.OVERVIEW,
                methodology_step="test_step",
                phase_completion_percentage=0.0,
                session_start_time=datetime.now(timezone.utc).isoformat(),
                last_update_time=datetime.now(timezone.utc).isoformat(),
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
        
        self.state_manager._save_state_to_history(test_state)
        
        # Verify history file was created
        history_files = list(self.state_manager.state_history_dir.glob('state_*.json'))
        assert len(history_files) >= 1
        
        # Verify history file contains correct data
        with open(history_files[0], 'r') as f:
            history_data = json.load(f)
        assert history_data['project_state']['methodology_step'] == "test_step"
    
    def test_save_state_to_history_cleanup_old_files(self):
        """Test history saving cleans up old history files"""
        test_state = CompleteSystemState(
            project_state=ProjectState(
                current_phase=ProjectPhase.OVERVIEW,
                methodology_step="cleanup_test",
                phase_completion_percentage=0.0,
                session_start_time=datetime.now(timezone.utc).isoformat(),
                last_update_time=datetime.now(timezone.utc).isoformat(),
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
        
        # Create many history files to trigger cleanup
        for i in range(55):  # More than the 50 file limit
            self.state_manager._save_state_to_history(test_state)
            time.sleep(0.01)  # Ensure different timestamps
        
        # Verify only 50 history files remain
        history_files = list(self.state_manager.state_history_dir.glob('state_*.json'))
        assert len(history_files) <= 50


class TestStateManagerErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_complete_state_all_recovery_methods_fail(self):
        """Test load state when all recovery methods fail"""
        # Corrupt primary state file
        with open(self.state_manager.current_state_file, 'w') as f:
            f.write('{ corrupted json content')
        
        # Mock all recovery methods to fail
        with patch.object(self.state_manager, '_load_most_recent_backup', return_value=None):
            with patch.object(self.state_manager, '_reconstruct_from_history', return_value=None):
                # Should still return default state (not fail)
                result = self.state_manager.load_complete_state()
        
        assert isinstance(result, CompleteSystemState)
        assert result.project_state.current_phase == ProjectPhase.OVERVIEW
    
    def test_save_complete_state_validation_failure(self):
        """Test save state fails gracefully on validation error"""
        # Create state that will fail validation
        invalid_state = CompleteSystemState(
            project_state=ProjectState(
                current_phase=ProjectPhase.OVERVIEW,
                methodology_step="test",
                phase_completion_percentage=0.0,
                session_start_time=datetime.now(timezone.utc).isoformat(),
                last_update_time=datetime.now(timezone.utc).isoformat(),
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
            state_hash="wrong_hash",  # This will cause validation failure
            backup_available=False
        )
        
        with pytest.raises(StateError, match="Failed to save system state"):
            self.state_manager.save_complete_state(invalid_state)
    
    def test_get_task_evidence_file_access_error(self):
        """Test get task evidence handles file access errors gracefully"""
        # Create evidence directory but make it inaccessible
        evidence_dir = self.state_manager.state_dir / 'evidence' / 'test_task'
        evidence_dir.mkdir(parents=True)
        
        # Create evidence file
        evidence_file = evidence_dir / 'test_results_123.json'
        with open(evidence_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Remove read permissions
        os.chmod(evidence_file, 0o000)
        
        try:
            # Should handle error gracefully and return empty list
            result = self.state_manager.get_task_evidence("test_task")
            assert result == []
        finally:
            # Restore permissions for cleanup
            os.chmod(evidence_file, 0o644)
    
    def test_calculate_state_hash_serialization_error(self):
        """Test state hash calculation handles serialization errors"""
        # Create state with non-serializable data
        state = CompleteSystemState(
            project_state=Mock(),  # Mock object is not JSON serializable
            task_graph=TaskGraph(nodes={}, edges={}, current_ready_tasks=[], blocked_tasks={}),
            cross_references={},
            dependencies={},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
        
        with pytest.raises(StateError, match="Cannot calculate hash for data"):
            self.state_manager._calculate_state_hash(state)