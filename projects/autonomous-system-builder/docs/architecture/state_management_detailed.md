# State Management Architecture - Detailed Specification

## Purpose
Detailed state management architecture addressing the complexity gaps discovered during pseudocode implementation (Gap 4 from current_gaps_analysis.md).

## Problem Statement
**Original ADR-002**: Simple hybrid file system with JSON metadata  
**Pseudocode Reality**: Complex state persistence with backup/recovery, consistency validation, corruption detection, atomic operations

## Comprehensive State Management Architecture

### Core State Components

#### 1. State Persistence Layer
```python
class StateManager:
    """Primary state management with atomic operations and consistency validation"""
    
    def __init__(self, project_root: str, config: StateConfig):
        self.project_root = Path(project_root)
        self.state_dir = self.project_root / ".autonomous_state"
        self.backup_dir = self.state_dir / "backups"
        self.config = config
        
        # State files
        self.current_state_file = self.state_dir / "current_state.json"
        self.metadata_file = self.state_dir / "state_metadata.json" 
        self.integrity_file = self.state_dir / "integrity_hashes.json"
        
        # Initialize state directory structure
        self._initialize_state_directory()
    
    def save_state(self, state_data: Dict[str, Any]) -> StateResult:
        """Atomic state save with backup and integrity validation"""
        
        # Pre-save validation
        validation_result = self._validate_state_data(state_data)
        if not validation_result.valid:
            return StateResult(success=False, error=validation_result.error)
        
        # Create backup of current state
        backup_result = self._create_backup()
        if not backup_result.success:
            return StateResult(success=False, error=f"Backup failed: {backup_result.error}")
        
        # Atomic write operation
        temp_file = self.current_state_file.with_suffix('.tmp')
        try:
            # Write to temporary file first
            with temp_file.open('w') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            # Verify integrity of temporary file
            temp_hash = self._calculate_file_hash(temp_file)
            
            # Atomic move to final location
            temp_file.rename(self.current_state_file)
            
            # Update metadata and integrity tracking
            self._update_metadata(state_data, temp_hash)
            self._update_integrity_tracking(temp_hash)
            
            return StateResult(success=True, state_hash=temp_hash)
            
        except Exception as e:
            # Cleanup on failure
            if temp_file.exists():
                temp_file.unlink()
            return StateResult(success=False, error=f"State save failed: {str(e)}")
```

#### 2. Backup and Recovery System
```python
class BackupManager:
    """Manages state backups with configurable retention and recovery"""
    
    def __init__(self, backup_dir: Path, config: BackupConfig):
        self.backup_dir = backup_dir
        self.config = config
        self.max_backups = config.max_backups  # Default: 10
        self.retention_days = config.retention_days  # Default: 30
    
    def create_backup(self, source_file: Path) -> BackupResult:
        """Create timestamped backup with metadata"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"state_backup_{timestamp}.json"
        metadata_file = self.backup_dir / f"backup_metadata_{timestamp}.json"
        
        try:
            # Copy state file
            shutil.copy2(source_file, backup_file)
            
            # Create metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "source_file": str(source_file),
                "backup_file": str(backup_file),
                "file_size": backup_file.stat().st_size,
                "file_hash": self._calculate_file_hash(backup_file),
                "backup_reason": "pre_save_backup"
            }
            
            with metadata_file.open('w') as f:
                json.dump(metadata, f, indent=2)
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return BackupResult(success=True, backup_file=backup_file)
            
        except Exception as e:
            return BackupResult(success=False, error=str(e))
    
    def restore_from_backup(self, backup_timestamp: str) -> RestoreResult:
        """Restore state from specific backup"""
        
        backup_file = self.backup_dir / f"state_backup_{backup_timestamp}.json"
        metadata_file = self.backup_dir / f"backup_metadata_{backup_timestamp}.json"
        
        if not backup_file.exists():
            return RestoreResult(success=False, error=f"Backup file not found: {backup_file}")
        
        # Validate backup integrity
        if metadata_file.exists():
            integrity_valid = self._validate_backup_integrity(backup_file, metadata_file)
            if not integrity_valid:
                return RestoreResult(success=False, error="Backup integrity validation failed")
        
        # Restore operation
        try:
            with backup_file.open('r') as f:
                restored_state = json.load(f)
            
            return RestoreResult(success=True, state_data=restored_state)
            
        except Exception as e:
            return RestoreResult(success=False, error=f"Restore failed: {str(e)}")
```

#### 3. Consistency Validation System
```python
class ConsistencyValidator:
    """Validates state consistency across multiple dimensions"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.validators = {
            'schema': SchemaValidator(),
            'cross_reference': CrossReferenceValidator(),
            'temporal': TemporalValidator(),
            'semantic': SemanticValidator()
        }
    
    def validate_state_consistency(self, state_data: Dict[str, Any]) -> ValidationResult:
        """Comprehensive state consistency validation"""
        
        validation_results = []
        overall_valid = True
        
        # Schema validation
        schema_result = self.validators['schema'].validate(state_data)
        validation_results.append(schema_result)
        if not schema_result.valid:
            overall_valid = False
        
        # Cross-reference validation
        cross_ref_result = self.validators['cross_reference'].validate(state_data)
        validation_results.append(cross_ref_result)
        if not cross_ref_result.valid:
            overall_valid = False
        
        # Temporal consistency validation
        temporal_result = self.validators['temporal'].validate(state_data)
        validation_results.append(temporal_result)
        if not temporal_result.valid:
            overall_valid = False
        
        # Semantic validation
        semantic_result = self.validators['semantic'].validate(state_data)
        validation_results.append(semantic_result)
        if not semantic_result.valid:
            overall_valid = False
        
        return ValidationResult(
            valid=overall_valid,
            component_results=validation_results,
            error_summary=self._summarize_errors(validation_results)
        )
    
    def validate_state_transition(self, old_state: Dict[str, Any], new_state: Dict[str, Any]) -> TransitionResult:
        """Validate that state transition is valid and safe"""
        
        # Detect state changes
        changes = self._detect_state_changes(old_state, new_state)
        
        # Validate each change
        change_validations = []
        for change in changes:
            change_validation = self._validate_single_change(change, old_state, new_state)
            change_validations.append(change_validation)
        
        # Check for dangerous transitions
        dangerous_transitions = self._detect_dangerous_transitions(changes)
        
        return TransitionResult(
            valid=all(cv.valid for cv in change_validations),
            changes=changes,
            change_validations=change_validations,
            dangerous_transitions=dangerous_transitions
        )
```

#### 4. Corruption Detection and Repair
```python
class CorruptionDetector:
    """Detects and repairs state corruption issues"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.repair_strategies = {
            'hash_mismatch': self._repair_hash_mismatch,
            'invalid_json': self._repair_invalid_json,
            'missing_fields': self._repair_missing_fields,
            'circular_references': self._repair_circular_references
        }
    
    def detect_corruption(self, state_file: Path) -> CorruptionReport:
        """Comprehensive corruption detection"""
        
        corruption_issues = []
        
        # File-level checks
        if not state_file.exists():
            corruption_issues.append(CorruptionIssue(
                type='missing_file',
                severity='critical',
                description=f"State file missing: {state_file}"
            ))
            return CorruptionReport(corrupted=True, issues=corruption_issues)
        
        # Hash integrity check
        hash_issue = self._check_hash_integrity(state_file)
        if hash_issue:
            corruption_issues.append(hash_issue)
        
        # JSON format check
        json_issue = self._check_json_format(state_file)
        if json_issue:
            corruption_issues.append(json_issue)
        
        # Load and validate content
        try:
            with state_file.open('r') as f:
                state_data = json.load(f)
            
            # Schema validation
            schema_issues = self._check_schema_compliance(state_data)
            corruption_issues.extend(schema_issues)
            
            # Cross-reference validation
            cross_ref_issues = self._check_cross_references(state_data)
            corruption_issues.extend(cross_ref_issues)
            
            # Semantic validation
            semantic_issues = self._check_semantic_consistency(state_data)
            corruption_issues.extend(semantic_issues)
            
        except Exception as e:
            corruption_issues.append(CorruptionIssue(
                type='read_error',
                severity='critical',
                description=f"Failed to read state file: {str(e)}"
            ))
        
        return CorruptionReport(
            corrupted=len(corruption_issues) > 0,
            issues=corruption_issues,
            repairable=self._assess_repairability(corruption_issues)
        )
    
    def repair_corruption(self, corruption_report: CorruptionReport) -> RepairResult:
        """Attempt to repair detected corruption"""
        
        if not corruption_report.repairable:
            return RepairResult(success=False, error="Corruption not repairable")
        
        repair_results = []
        
        for issue in corruption_report.issues:
            if issue.type in self.repair_strategies:
                repair_result = self.repair_strategies[issue.type](issue)
                repair_results.append(repair_result)
            else:
                repair_results.append(RepairResult(
                    success=False,
                    error=f"No repair strategy for issue type: {issue.type}"
                ))
        
        overall_success = all(rr.success for rr in repair_results)
        
        return RepairResult(
            success=overall_success,
            repair_results=repair_results,
            repaired_issues=len([rr for rr in repair_results if rr.success])
        )
```

### Integration with Autonomous System

#### State Management in Hook Cycle
```python
def autonomous_hook_cycle_with_state():
    """Integration of state management with autonomous hook cycle"""
    
    # Initialize state manager
    state_manager = StateManager(project_root, config)
    
    # Load current state
    current_state = state_manager.load_current_state()
    
    # Corruption detection
    corruption_report = state_manager.detect_corruption()
    if corruption_report.corrupted:
        if corruption_report.repairable:
            repair_result = state_manager.repair_corruption(corruption_report)
            if not repair_result.success:
                return HookResult(status="error", message="State corruption detected and repair failed")
        else:
            return HookResult(status="error", message="Unrecoverable state corruption detected")
    
    # Execute autonomous logic with state
    autonomous_result = execute_autonomous_logic(current_state)
    
    # Update state atomically
    new_state = autonomous_result.updated_state
    state_result = state_manager.save_state(new_state)
    
    if not state_result.success:
        return HookResult(status="error", message=f"State save failed: {state_result.error}")
    
    return HookResult(status="success", new_state_hash=state_result.state_hash)
```

## Configuration Management

### State Configuration Schema
```python
@dataclass
class StateConfig:
    """Configuration for state management system"""
    
    # Backup settings
    max_backups: int = 10
    retention_days: int = 30
    backup_on_save: bool = True
    
    # Validation settings
    enable_schema_validation: bool = True
    enable_cross_reference_validation: bool = True
    enable_temporal_validation: bool = True
    strict_mode: bool = False
    
    # Corruption detection
    enable_hash_checking: bool = True
    enable_automatic_repair: bool = True
    corruption_scan_interval: int = 3600  # seconds
    
    # Performance settings
    state_cache_size: int = 100
    async_backup: bool = True
    compression_enabled: bool = False
```

## Error Handling and Recovery

### Error Categories and Strategies
1. **Transient Errors** (network, disk space): Retry with exponential backoff
2. **Corruption Errors**: Attempt repair, fallback to backup restoration  
3. **Validation Errors**: Log and continue with degraded functionality
4. **Critical Errors**: Escalate to human intervention

### Recovery Workflows
1. **Graceful Degradation**: Continue operation with reduced state functionality
2. **Backup Restoration**: Restore from most recent valid backup
3. **State Reconstruction**: Rebuild state from evidence files and current project status
4. **Emergency Mode**: Operate stateless until state can be restored

## Performance Considerations

### Optimization Strategies
- **Lazy Loading**: Load state components only when needed
- **Incremental Saves**: Save only changed state portions
- **Compressed Backups**: Use compression for backup storage
- **Async Operations**: Non-blocking backup and validation operations

### Memory Management
- **State Caching**: Cache frequently accessed state data
- **Memory Limits**: Respect 500MB memory constraints
- **Garbage Collection**: Explicit cleanup of temporary state objects

## Security Considerations

### Access Control
- **File Permissions**: Restrict state file access to current user
- **Directory Security**: Secure state directory with appropriate permissions
- **Backup Security**: Encrypt sensitive state data in backups

### Data Protection
- **Sensitive Data Filtering**: Remove credentials and secrets from state
- **Audit Logging**: Log all state modifications with timestamps
- **Integrity Verification**: Cryptographic hashes for tamper detection

This detailed state management architecture addresses all complexity gaps identified in the pseudocode analysis, providing robust state persistence, backup/recovery, consistency validation, and corruption handling required for autonomous operation.