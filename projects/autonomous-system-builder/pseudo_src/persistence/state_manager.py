#!/usr/bin/env python3
"""
STATE MANAGER - Foundation Component
Manages persistence and consistency of all system state data
"""

# RELATES_TO: ../config/config_manager.py, ../utils/json_utils.py, ../../logs/state/

import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum

class StateError(Exception):
    """Raised when state operations fail"""
    pass

class StateConsistencyError(StateError):
    """Raised when state consistency checks fail"""
    pass

class ProjectPhase(Enum):
    """Valid project phases in autonomous methodology"""
    OVERVIEW = 1
    ARCHITECTURE_DEPENDENCY_RESEARCH = 2  
    FILE_STRUCTURE_CREATION = 3
    PSEUDOCODE_DOCUMENTATION = 4
    IMPLEMENTATION_PLANS_UNIT_TESTS = 5
    INTEGRATION_TESTS = 6
    ACCEPTANCE_TESTS = 7
    CREATE_FILES_CROSS_REFERENCES = 8
    IMPLEMENTATION = 9
    PROJECT_COMPLETE = 10

@dataclass
class ProjectState:
    """Core project state information"""
    current_phase: ProjectPhase
    methodology_step: str
    phase_completion_percentage: float
    session_start_time: str
    last_update_time: str
    total_hook_iterations: int
    consecutive_failures: int
    blocking_status: Dict[str, Any]
    current_tasks: List[str]
    completed_tasks: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        result = asdict(self)
        result['current_phase'] = self.current_phase.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['current_phase'] = ProjectPhase(data_copy['current_phase'])
        return cls(**data_copy)

@dataclass 
class TaskNode:
    """Individual task in the task graph"""
    id: str
    title: str
    description: str
    task_type: str  # 'implementation', 'research', 'testing', 'documentation'
    priority: int   # 1-10 scale
    status: str     # 'pending', 'in_progress', 'completed', 'blocked'
    file_targets: List[str]
    dependencies: List[str]  # Task IDs this task depends on
    context_requirements: List[str]  # Files needed for context
    evidence_requirements: Dict[str, bool]
    estimated_complexity: int  # 1-10 scale
    created_time: str
    last_updated: str
    completion_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskNode':
        return cls(**data)

@dataclass
class TaskGraph:
    """Complete task dependency graph"""
    nodes: Dict[str, TaskNode]  # task_id -> TaskNode
    edges: Dict[str, List[str]]  # task_id -> list of dependent task_ids
    current_ready_tasks: List[str]
    blocked_tasks: Dict[str, str]  # task_id -> blocking_reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodes': {task_id: node.to_dict() for task_id, node in self.nodes.items()},
            'edges': self.edges,
            'current_ready_tasks': self.current_ready_tasks,
            'blocked_tasks': self.blocked_tasks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskGraph':
        nodes = {task_id: TaskNode.from_dict(node_data) 
                for task_id, node_data in data['nodes'].items()}
        return cls(
            nodes=nodes,
            edges=data['edges'],
            current_ready_tasks=data['current_ready_tasks'],
            blocked_tasks=data['blocked_tasks']
        )

@dataclass
class EvidenceRecord:
    """Record of evidence for task completion"""
    task_id: str
    evidence_type: str  # 'test_results', 'file_existence', 'integration_proof'
    evidence_data: Dict[str, Any]
    collection_time: str
    validation_status: str  # 'valid', 'invalid', 'pending'
    file_references: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvidenceRecord':
        return cls(**data)

@dataclass
class CompleteSystemState:
    """Complete state of the autonomous system"""
    project_state: ProjectState
    task_graph: TaskGraph
    cross_references: Dict[str, List[str]]
    dependencies: Dict[str, Any]
    evidence_records: List[EvidenceRecord]
    state_hash: str
    backup_available: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_state': self.project_state.to_dict(),
            'task_graph': self.task_graph.to_dict(),
            'cross_references': self.cross_references,
            'dependencies': self.dependencies,
            'evidence_records': [record.to_dict() for record in self.evidence_records],
            'state_hash': self.state_hash,
            'backup_available': self.backup_available
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompleteSystemState':
        return cls(
            project_state=ProjectState.from_dict(data['project_state']),
            task_graph=TaskGraph.from_dict(data['task_graph']),
            cross_references=data['cross_references'],
            dependencies=data['dependencies'],
            evidence_records=[EvidenceRecord.from_dict(record) for record in data['evidence_records']],
            state_hash=data['state_hash'],
            backup_available=data['backup_available']
        )

class StateManager:
    """
    Manages all system state persistence with defensive programming
    
    FOUNDATION COMPONENT: Depends only on ConfigManager and JSONUtilities
    Provides state management for entire autonomous system
    """
    
    def __init__(self, project_root: str, config_manager=None):
        """
        Initialize state manager
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        - config_manager: Optional ConfigManager instance (will create if None)
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is writable
        - Creates state directories if they don't exist
        - Initializes backup system
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise StateError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise StateError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise StateError(f"Project root is not a directory: {project_root}")
        
        # Initialize configuration
        if config_manager is None:
            from ..config.config_manager import ConfigManager
            self.config_manager = ConfigManager(project_root)
        else:
            self.config_manager = config_manager
        
        # State storage paths
        self.state_dir = self.project_root / 'logs' / 'state'
        self.backup_dir = self.state_dir / 'backups'
        self.current_state_file = self.state_dir / 'current_state.json'
        self.state_history_dir = self.state_dir / 'history'
        
        # Create directories if they don't exist
        for directory in [self.state_dir, self.backup_dir, self.state_history_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # JSON utilities for safe operations
        from ..utils.json_utils import JSONUtilities
        self.json_utils = JSONUtilities()
    
    def load_complete_state(self) -> CompleteSystemState:
        """
        Load complete system state with validation and error recovery
        
        RETURNS: Complete system state object
        
        DEFENSIVE PROGRAMMING:
        - Attempts state recovery if corruption detected
        - Falls back to backup if primary state invalid
        - Creates default state if no valid state found
        - Validates state consistency after loading
        """
        
        try:
            # Attempt to load primary state file
            if self.current_state_file.exists():
                state_data = self.json_utils.safe_load_json(
                    self.current_state_file,
                    validate_schema=self._get_state_schema()
                )
                
                if state_data:
                    system_state = CompleteSystemState.from_dict(state_data)
                    
                    # Validate state consistency
                    if self._validate_state_consistency(system_state):
                        return system_state
                    else:
                        # State validation failed - attempt recovery
                        return self._attempt_state_recovery()
            
            # No primary state - attempt backup recovery
            backup_state = self._load_most_recent_backup()
            if backup_state:
                return backup_state
            
            # No valid state found - create default
            return self._create_default_state()
            
        except Exception as e:
            # All recovery attempts failed
            raise StateError(f"Failed to load system state: {e}")
    
    def save_complete_state(self, system_state: CompleteSystemState) -> bool:
        """
        Save complete system state with backup and validation
        
        PARAMETERS:
        - system_state: Complete system state to save
        
        RETURNS: True if save successful, False otherwise
        
        SAFETY FEATURES:
        - Creates backup before overwriting current state
        - Validates state before saving
        - Uses atomic write operations
        - Maintains state history for debugging
        """
        
        try:
            # DEFENSIVE PROGRAMMING: Validate state before saving
            self._validate_state_consistency(system_state)
            
            # Update state metadata
            system_state.project_state.last_update_time = datetime.now(timezone.utc).isoformat()
            system_state.state_hash = self._calculate_state_hash(system_state)
            
            # Create backup of current state if it exists
            if self.current_state_file.exists():
                self._create_state_backup()
                system_state.backup_available = True
            
            # Save to history for debugging
            self._save_state_to_history(system_state)
            
            # Save current state atomically
            state_data = system_state.to_dict()
            success = self.json_utils.safe_save_json(
                self.current_state_file,
                state_data,
                backup=False,  # We handle our own backup
                validate_schema=self._get_state_schema(),
                atomic=True
            )
            
            if success:
                # Verify saved state can be loaded back
                verification_state = self.json_utils.safe_load_json(self.current_state_file)
                if verification_state and verification_state.get('state_hash') == system_state.state_hash:
                    return True
                else:
                    raise StateError("State verification failed after save")
            
            return False
            
        except Exception as e:
            raise StateError(f"Failed to save system state: {e}")
    
    def save_evidence_record(self, evidence: EvidenceRecord) -> bool:
        """
        Save evidence record with validation and indexing
        
        PARAMETERS:
        - evidence: Evidence record to save
        
        RETURNS: True if save successful
        
        FEATURES:
        - Validates evidence data completeness
        - Maintains evidence index for fast lookup
        - Creates task-specific evidence files
        """
        
        try:
            # Validate evidence record
            if not evidence.task_id:
                raise StateError("Evidence record must have task_id")
            
            if not evidence.evidence_type:
                raise StateError("Evidence record must have evidence_type")
            
            # Create evidence directory structure
            evidence_dir = self.state_dir / 'evidence' / evidence.task_id
            evidence_dir.mkdir(parents=True, exist_ok=True)
            
            # Save evidence record
            evidence_file = evidence_dir / f"{evidence.evidence_type}_{int(datetime.now().timestamp())}.json"
            evidence_data = evidence.to_dict()
            
            success = self.json_utils.safe_save_json(
                evidence_file,
                evidence_data,
                atomic=True
            )
            
            if success:
                # Update evidence index
                self._update_evidence_index(evidence)
                return True
            
            return False
            
        except Exception as e:
            raise StateError(f"Failed to save evidence record: {e}")
    
    def get_task_evidence(self, task_id: str) -> List[EvidenceRecord]:
        """
        Get all evidence records for a specific task
        
        PARAMETERS:
        - task_id: Task ID to get evidence for
        
        RETURNS: List of evidence records
        """
        
        try:
            evidence_dir = self.state_dir / 'evidence' / task_id
            if not evidence_dir.exists():
                return []
            
            evidence_records = []
            for evidence_file in evidence_dir.glob('*.json'):
                evidence_data = self.json_utils.safe_load_json(evidence_file)
                if evidence_data:
                    evidence_records.append(EvidenceRecord.from_dict(evidence_data))
            
            # Sort by collection time
            evidence_records.sort(key=lambda x: x.collection_time)
            return evidence_records
            
        except Exception as e:
            raise StateError(f"Failed to load evidence for task {task_id}: {e}")
    
    def _validate_state_consistency(self, system_state: CompleteSystemState) -> bool:
        """
        Validate internal consistency of system state
        
        PARAMETERS:
        - system_state: State to validate
        
        RETURNS: True if consistent, False otherwise
        
        CONSISTENCY CHECKS:
        - All task dependencies exist in task graph
        - Current ready tasks are actually ready
        - Evidence records reference valid tasks
        - Cross-references point to existing files
        """
        
        try:
            # Validate task graph consistency
            task_graph = system_state.task_graph
            
            # Check all task dependencies exist
            for task_id, task in task_graph.nodes.items():
                for dep_id in task.dependencies:
                    if dep_id not in task_graph.nodes:
                        return False
            
            # Check ready tasks are actually ready
            for ready_task_id in task_graph.current_ready_tasks:
                if ready_task_id not in task_graph.nodes:
                    return False
                
                task = task_graph.nodes[ready_task_id]
                # Task should not be completed or blocked
                if task.status in ['completed', 'blocked']:
                    return False
                
                # All dependencies should be completed
                for dep_id in task.dependencies:
                    dep_task = task_graph.nodes[dep_id]
                    if dep_task.status != 'completed':
                        return False
            
            # Validate evidence records reference valid tasks
            for evidence in system_state.evidence_records:
                if evidence.task_id not in task_graph.nodes:
                    return False
            
            # Validate project state
            project_state = system_state.project_state
            if project_state.current_phase not in ProjectPhase:
                return False
            
            # State hash should match calculated hash
            calculated_hash = self._calculate_state_hash(system_state)
            if system_state.state_hash != calculated_hash:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _calculate_state_hash(self, system_state: CompleteSystemState) -> str:
        """
        Calculate SHA-256 hash of system state for change detection
        
        PARAMETERS:
        - system_state: State to hash
        
        RETURNS: SHA-256 hash string
        """
        
        try:
            # Create hashable representation
            state_dict = system_state.to_dict()
            # Remove hash field to avoid circular dependency
            state_dict.pop('state_hash', None)
            
            return self.json_utils.calculate_json_hash(state_dict)
            
        except Exception as e:
            raise StateError(f"Failed to calculate state hash: {e}")
    
    def _create_state_backup(self) -> bool:
        """
        Create backup of current state file
        
        RETURNS: True if backup created successfully
        """
        
        try:
            if not self.current_state_file.exists():
                return True  # Nothing to backup
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"state_backup_{timestamp}.json"
            
            shutil.copy2(self.current_state_file, backup_file)
            
            # Clean up old backups (keep last 10)
            backup_files = sorted(self.backup_dir.glob('state_backup_*.json'))
            if len(backup_files) > 10:
                for old_backup in backup_files[:-10]:
                    old_backup.unlink()
            
            return True
            
        except Exception as e:
            raise StateError(f"Failed to create state backup: {e}")
    
    def _load_most_recent_backup(self) -> Optional[CompleteSystemState]:
        """
        Load most recent valid backup state
        
        RETURNS: System state from backup or None if no valid backup
        """
        
        try:
            backup_files = sorted(self.backup_dir.glob('state_backup_*.json'), reverse=True)
            
            for backup_file in backup_files:
                try:
                    backup_data = self.json_utils.safe_load_json(
                        backup_file,
                        validate_schema=self._get_state_schema()
                    )
                    
                    if backup_data:
                        backup_state = CompleteSystemState.from_dict(backup_data)
                        
                        if self._validate_state_consistency(backup_state):
                            return backup_state
                
                except Exception:
                    continue  # Try next backup
            
            return None
            
        except Exception:
            return None
    
    def _attempt_state_recovery(self) -> CompleteSystemState:
        """
        Attempt to recover from state corruption
        
        RETURNS: Recovered system state
        
        RECOVERY STRATEGIES:
        1. Load from most recent backup
        2. Reconstruct from history files
        3. Create minimal default state
        """
        
        # Try backup recovery first
        backup_state = self._load_most_recent_backup()
        if backup_state:
            return backup_state
        
        # Try to reconstruct from history
        history_state = self._reconstruct_from_history()
        if history_state:
            return history_state
        
        # Create minimal default state
        return self._create_default_state()
    
    def _create_default_state(self) -> CompleteSystemState:
        """
        Create default system state for new projects
        
        RETURNS: Default system state
        """
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        project_state = ProjectState(
            current_phase=ProjectPhase.OVERVIEW,
            methodology_step="initial_overview",
            phase_completion_percentage=0.0,
            session_start_time=current_time,
            last_update_time=current_time,
            total_hook_iterations=0,
            consecutive_failures=0,
            blocking_status={"is_blocked": False, "reason": None},
            current_tasks=[],
            completed_tasks=[]
        )
        
        task_graph = TaskGraph(
            nodes={},
            edges={},
            current_ready_tasks=[],
            blocked_tasks={}
        )
        
        system_state = CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph,
            cross_references={},
            dependencies={},
            evidence_records=[],
            state_hash="",
            backup_available=False
        )
        
        # Calculate initial hash
        system_state.state_hash = self._calculate_state_hash(system_state)
        
        return system_state
    
    def _save_state_to_history(self, system_state: CompleteSystemState) -> None:
        """
        Save state to history for debugging and recovery
        
        PARAMETERS:
        - system_state: State to save to history
        """
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.state_history_dir / f"state_{timestamp}.json"
            
            state_data = system_state.to_dict()
            self.json_utils.safe_save_json(history_file, state_data, atomic=True)
            
            # Clean up old history files (keep last 50)
            history_files = sorted(self.state_history_dir.glob('state_*.json'))
            if len(history_files) > 50:
                for old_file in history_files[:-50]:
                    old_file.unlink()
            
        except Exception:
            # Don't fail if history save fails
            pass
    
    def _reconstruct_from_history(self) -> Optional[CompleteSystemState]:
        """
        Attempt to reconstruct valid state from history files
        
        RETURNS: Reconstructed state or None
        """
        
        try:
            history_files = sorted(self.state_history_dir.glob('state_*.json'), reverse=True)
            
            for history_file in history_files[:10]:  # Check last 10 history files
                try:
                    history_data = self.json_utils.safe_load_json(history_file)
                    if history_data:
                        history_state = CompleteSystemState.from_dict(history_data)
                        if self._validate_state_consistency(history_state):
                            return history_state
                except Exception:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _update_evidence_index(self, evidence: EvidenceRecord) -> None:
        """
        Update evidence index for fast lookup
        
        PARAMETERS:
        - evidence: Evidence record to index
        """
        
        try:
            index_file = self.state_dir / 'evidence' / 'index.json'
            
            # Load existing index
            if index_file.exists():
                index_data = self.json_utils.safe_load_json(index_file, default={})
            else:
                index_data = {}
            
            # Add evidence to index
            if evidence.task_id not in index_data:
                index_data[evidence.task_id] = []
            
            evidence_entry = {
                'evidence_type': evidence.evidence_type,
                'collection_time': evidence.collection_time,
                'validation_status': evidence.validation_status
            }
            
            index_data[evidence.task_id].append(evidence_entry)
            
            # Save updated index
            self.json_utils.safe_save_json(index_file, index_data, atomic=True)
            
        except Exception:
            # Don't fail if index update fails
            pass
    
    def _get_state_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for state validation
        
        RETURNS: JSON schema for system state
        """
        
        return {
            "type": "object",
            "required": ["project_state", "task_graph", "cross_references", "dependencies", "evidence_records"],
            "properties": {
                "project_state": {
                    "type": "object",
                    "required": ["current_phase", "methodology_step"]
                },
                "task_graph": {
                    "type": "object", 
                    "required": ["nodes", "edges", "current_ready_tasks", "blocked_tasks"]
                },
                "cross_references": {"type": "object"},
                "dependencies": {"type": "object"},
                "evidence_records": {"type": "array"},
                "state_hash": {"type": "string"},
                "backup_available": {"type": "boolean"}
            }
        }