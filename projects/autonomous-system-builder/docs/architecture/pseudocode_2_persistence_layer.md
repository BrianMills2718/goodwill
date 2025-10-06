# Pseudocode Part 2: Persistence Layer Design

## Overview
Define how the information architecture data structures are loaded, saved, synchronized, and maintained across hook executions. This ensures state consistency and enables autonomous operation across multiple hook calls.

## Core Persistence Principles

### 1. Atomic Operations
All state updates must be atomic - either completely succeed or completely fail with rollback.

### 2. Consistency Guarantees  
State files must remain consistent with each other - no partial updates that leave system in invalid state.

### 3. Defensive Loading
Always validate loaded data and provide safe defaults when files are missing or corrupted.

### 4. Change Detection
Track what changed during each hook execution for debugging and rollback purposes.

## File Storage Strategy

### Primary State Files (`.claude/` directory)
```
.claude/
├── session_state.json          # ProjectState - current session information
├── task_graph.json             # TaskGraph - task dependencies and progress  
├── cross_references.json       # CrossReferenceMap - file relationships
├── dependencies.json           # DependencyManifest - external service status
├── session_backup.json         # Backup of session state before each hook call
└── state_integrity.json        # State integrity verification and checksums
```

### Evidence Storage (`logs/evidence/` directory)
```
logs/evidence/
├── session_progress.json       # Overall session progress summary
├── task_evidence/              # Individual task evidence files
│   ├── task_[id]_evidence.json # EvidenceRecord per task
│   └── task_[id]_history.json  # Historical evidence for task
└── validation_results/         # Anti-fabrication validation results
    ├── session_validation.json # Overall session validation status
    └── hook_[num]_validation.json # Per-hook validation results
```

## Persistence Layer Components

### 1. State Manager (`src/config/state_manager.py`)

```python
class StateManager:
    """Manages loading, saving, and synchronizing all system state"""
    
    def __init__(self, project_root: str, config: SystemConfiguration):
        self.project_root = Path(project_root)
        self.config = config
        self.claude_dir = self.project_root / '.claude'
        self.evidence_dir = self.project_root / 'logs' / 'evidence'
        
        # State integrity tracking
        self.state_checksums = {}
        self.change_log = []
        
    def load_complete_state(self) -> CompleteSystemState:
        """Load all system state with validation and defaults"""
        
        # Create backup before any modifications
        self._create_state_backup()
        
        # Load all state components with validation
        project_state = self._load_project_state()
        task_graph = self._load_task_graph() 
        cross_references = self._load_cross_references()
        dependencies = self._load_dependencies()
        
        # Validate state consistency
        self._validate_state_consistency(project_state, task_graph, cross_references, dependencies)
        
        # Create complete state object
        complete_state = CompleteSystemState(
            project_state=project_state,
            task_graph=task_graph, 
            cross_references=cross_references,
            dependencies=dependencies,
            loaded_at=datetime.utcnow()
        )
        
        return complete_state
        
    def save_complete_state(self, state: CompleteSystemState) -> bool:
        """Atomically save all system state with integrity verification"""
        
        try:
            # Validate state before saving
            self._validate_state_before_save(state)
            
            # Create temporary files for atomic write
            temp_files = self._prepare_temp_state_files(state)
            
            # Verify temp files are valid
            self._verify_temp_files(temp_files)
            
            # Atomic move to actual locations
            self._commit_temp_files(temp_files)
            
            # Update integrity checksums
            self._update_state_integrity()
            
            # Log successful state save
            self._log_state_change("save_complete", state)
            
            return True
            
        except Exception as e:
            # Rollback on any failure
            self._rollback_state_changes()
            self._log_state_error("save_failed", e, state)
            return False
```

### 2. Individual State Loaders

```python
def _load_project_state(self) -> ProjectState:
    """Load project state with defensive defaults"""
    
    state_file = self.claude_dir / 'session_state.json'
    
    if not state_file.exists():
        # Create new session state
        return self._create_new_session_state()
    
    try:
        with open(state_file, 'r') as f:
            data = json.load(f)
            
        # Validate required fields
        validated_data = self._validate_project_state_schema(data)
        
        # Convert to ProjectState object
        project_state = ProjectState.from_dict(validated_data)
        
        # Update session information
        project_state.last_activity_time = datetime.utcnow().isoformat()
        project_state.total_hook_calls += 1
        
        return project_state
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Handle corrupted state file
        self._log_state_error("corrupted_project_state", e)
        
        # Attempt to restore from backup
        backup_state = self._restore_from_backup('session_state')
        if backup_state:
            return backup_state
            
        # Create new state if backup fails
        return self._create_new_session_state()

def _load_task_graph(self) -> TaskGraph:
    """Load task dependency graph with validation"""
    
    graph_file = self.claude_dir / 'task_graph.json'
    
    if not graph_file.exists():
        # Create empty task graph
        return self._create_empty_task_graph()
    
    try:
        with open(graph_file, 'r') as f:
            data = json.load(f)
            
        # Validate graph structure
        validated_graph = self._validate_task_graph_schema(data)
        
        # Verify task dependencies are valid
        self._verify_task_dependencies(validated_graph)
        
        # Update ready/blocked task lists
        self._update_task_execution_lists(validated_graph)
        
        return TaskGraph.from_dict(validated_graph)
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        self._log_state_error("corrupted_task_graph", e)
        
        # Attempt backup restoration
        backup_graph = self._restore_from_backup('task_graph')
        if backup_graph:
            return backup_graph
            
        # Create empty graph if backup fails
        return self._create_empty_task_graph()

def _load_cross_references(self) -> CrossReferenceMap:
    """Load file cross-reference relationships"""
    
    ref_file = self.claude_dir / 'cross_references.json'
    
    if not ref_file.exists():
        # Scan existing files to build initial cross-reference map
        return self._build_initial_cross_references()
    
    try:
        with open(ref_file, 'r') as f:
            data = json.load(f)
            
        # Validate cross-reference structure
        validated_refs = self._validate_cross_reference_schema(data)
        
        # Verify referenced files still exist
        self._verify_cross_reference_targets(validated_refs)
        
        # Update broken reference list
        self._update_broken_references(validated_refs)
        
        return CrossReferenceMap.from_dict(validated_refs)
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        self._log_state_error("corrupted_cross_references", e)
        
        # Rebuild from file system scan
        return self._build_initial_cross_references()

def _load_dependencies(self) -> DependencyManifest:
    """Load external dependency status"""
    
    dep_file = self.claude_dir / 'dependencies.json'
    
    if not dep_file.exists():
        # Create empty dependency manifest
        return self._create_empty_dependency_manifest()
    
    try:
        with open(dep_file, 'r') as f:
            data = json.load(f)
            
        # Validate dependency structure
        validated_deps = self._validate_dependency_schema(data)
        
        # Refresh dependency validation status
        self._refresh_dependency_validation(validated_deps)
        
        return DependencyManifest.from_dict(validated_deps)
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        self._log_state_error("corrupted_dependencies", e)
        
        # Create empty manifest
        return self._create_empty_dependency_manifest()
```

### 3. State Consistency Validation

```python
def _validate_state_consistency(self, project_state: ProjectState, 
                              task_graph: TaskGraph,
                              cross_references: CrossReferenceMap,
                              dependencies: DependencyManifest) -> None:
    """Validate that all state components are consistent with each other"""
    
    consistency_errors = []
    
    # Validate project state matches task graph
    if project_state.current_phase != self._infer_phase_from_task_graph(task_graph):
        consistency_errors.append("Project phase doesn't match task graph state")
    
    # Validate task graph references valid files
    for task_id, task in task_graph.tasks.items():
        for file_path in task.file_targets:
            if file_path not in cross_references.file_relationships:
                consistency_errors.append(f"Task {task_id} targets unknown file {file_path}")
    
    # Validate dependencies match task requirements
    for task_id, task in task_graph.tasks.items():
        if task.evidence_requirements.external_validation:
            required_deps = self._extract_task_dependencies(task)
            for dep in required_deps:
                if dep not in dependencies.external_services:
                    consistency_errors.append(f"Task {task_id} requires unknown dependency {dep}")
    
    # Validate cross-references point to existing files
    for file_path, relationships in cross_references.file_relationships.items():
        if not (self.project_root / file_path).exists():
            consistency_errors.append(f"Cross-reference map contains non-existent file {file_path}")
    
    # If consistency errors found, attempt auto-repair or fail
    if consistency_errors:
        self._log_consistency_errors(consistency_errors)
        
        if self.config.autonomous_behavior.auto_repair_enabled:
            self._attempt_consistency_repair(project_state, task_graph, cross_references, dependencies)
        else:
            raise StateConsistencyError(f"State consistency validation failed: {consistency_errors}")
```

### 4. Evidence Persistence

```python
def save_evidence_record(self, evidence: EvidenceRecord) -> bool:
    """Save evidence with integrity verification"""
    
    try:
        # Determine evidence file path
        evidence_file = self.evidence_dir / 'task_evidence' / f'task_{evidence.task_id}_evidence.json'
        
        # Ensure evidence directory exists
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate evidence before saving
        self._validate_evidence_schema(evidence)
        
        # Create atomic write with temp file
        temp_file = evidence_file.with_suffix('.tmp')
        
        with open(temp_file, 'w') as f:
            json.dump(evidence.to_dict(), f, indent=2, default=str)
        
        # Verify temp file is valid
        with open(temp_file, 'r') as f:
            json.load(f)  # Verify it's valid JSON
        
        # Atomic move to final location
        temp_file.rename(evidence_file)
        
        # Update evidence index
        self._update_evidence_index(evidence)
        
        # Log evidence save
        self._log_evidence_save(evidence)
        
        return True
        
    except Exception as e:
        self._log_state_error("evidence_save_failed", e, evidence)
        return False

def load_task_evidence_history(self, task_id: str) -> List[EvidenceRecord]:
    """Load all evidence records for a specific task"""
    
    evidence_files = list((self.evidence_dir / 'task_evidence').glob(f'task_{task_id}_evidence*.json'))
    evidence_records = []
    
    for evidence_file in sorted(evidence_files):
        try:
            with open(evidence_file, 'r') as f:
                data = json.load(f)
            
            evidence = EvidenceRecord.from_dict(data)
            evidence_records.append(evidence)
            
        except Exception as e:
            self._log_state_error("evidence_load_failed", e, evidence_file)
    
    return evidence_records
```

### 5. State Backup and Recovery

```python
def _create_state_backup(self) -> None:
    """Create backup of current state before modifications"""
    
    backup_timestamp = datetime.utcnow().isoformat()
    backup_dir = self.claude_dir / 'backups' / backup_timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup all state files
    state_files = [
        'session_state.json',
        'task_graph.json', 
        'cross_references.json',
        'dependencies.json'
    ]
    
    for state_file in state_files:
        source = self.claude_dir / state_file
        if source.exists():
            backup_target = backup_dir / state_file
            shutil.copy2(source, backup_target)
    
    # Update backup index
    self._update_backup_index(backup_timestamp)
    
    # Clean up old backups if needed
    self._cleanup_old_backups()

def _rollback_state_changes(self) -> bool:
    """Rollback to most recent backup if current state is corrupted"""
    
    try:
        # Find most recent backup
        backup_index = self._load_backup_index()
        if not backup_index:
            return False
        
        latest_backup = backup_index[-1]
        backup_dir = self.claude_dir / 'backups' / latest_backup
        
        # Restore state files from backup
        state_files = [
            'session_state.json',
            'task_graph.json',
            'cross_references.json', 
            'dependencies.json'
        ]
        
        for state_file in state_files:
            backup_source = backup_dir / state_file
            if backup_source.exists():
                target = self.claude_dir / state_file
                shutil.copy2(backup_source, target)
        
        self._log_state_change("rollback_successful", latest_backup)
        return True
        
    except Exception as e:
        self._log_state_error("rollback_failed", e)
        return False
```

## Persistence Error Handling

### Error Recovery Strategy
1. **Validation Errors**: Attempt to repair invalid data, fallback to defaults
2. **File Corruption**: Restore from most recent backup, rebuild if necessary  
3. **Consistency Errors**: Auto-repair if possible, escalate to user if not
4. **Save Failures**: Rollback changes, retry with exponential backoff

### Safety Mechanisms
- **Atomic Operations**: All state updates are atomic (complete success or rollback)
- **Backup Before Changes**: Always backup before modifying state
- **Integrity Verification**: Verify data integrity after saves
- **Change Logging**: Log all state changes for debugging and audit

## Performance Considerations

### Optimization Strategies
- **Lazy Loading**: Only load state components when needed
- **Incremental Updates**: Only save changed portions of large state objects
- **Compression**: Compress large evidence files to save disk space
- **Indexing**: Maintain indexes for fast task and evidence lookups

### Resource Limits
- **Maximum Evidence Files**: Limit evidence retention to prevent disk bloat
- **Backup Retention**: Auto-cleanup old backups based on age and count
- **Memory Usage**: Stream large files instead of loading entirely into memory

## Cross-References
```
# RELATES_TO: pseudocode_1_information_architecture.md (data structures being persisted),
#            architecture_decisions.md (ADR-008: structured evidence storage),
#            behavior_decisions.md (BDR-009: defensive programming requirements),
#            tentative_file_structure.md (file storage locations)
```

## Next Foundation Component
After persistence layer, the next foundation component is **Cross-Reference System Logic** - how file relationships are discovered, maintained, and used for intelligent context loading.