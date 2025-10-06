# JSON Utilities - Utilities Pseudocode
# Part of autonomous TDD system utility components

"""
JSON Utilities System

Provides safe JSON operations with validation, atomic writes, schema validation,
and error handling for the autonomous TDD system's data persistence needs.
"""

from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import tempfile
import shutil
import hashlib
from datetime import datetime
import jsonschema

# === Configuration and Data Classes ===

class JSONValidationMode(Enum):
    """JSON validation modes"""
    NONE = "none"           # No validation
    BASIC = "basic"         # Basic JSON syntax validation
    SCHEMA = "schema"       # Full schema validation
    STRICT = "strict"       # Strict schema + additional checks

@dataclass
class JSONSchema:
    """JSON schema definition"""
    name: str
    schema: Dict[str, Any]
    version: str = "1.0"
    description: str = ""
    strict_mode: bool = False

@dataclass
class JSONOperationResult:
    """Result of JSON operation"""
    success: bool
    data: Optional[Any] = None
    file_path: Optional[Path] = None
    checksum: Optional[str] = None
    validation_passed: bool = False
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    operation_time: Optional[datetime] = None
    backup_created: bool = False

@dataclass
class JSONSafetyConfig:
    """Configuration for JSON safety features"""
    create_backups: bool = True
    verify_checksums: bool = True
    atomic_writes: bool = True
    schema_validation: bool = True
    max_file_size_mb: int = 100
    encoding: str = "utf-8"
    indent: int = 2
    ensure_ascii: bool = False

# === JSON Utilities Implementation ===

class JSONUtilities:
    """
    Safe JSON operations with comprehensive error handling and validation
    
    Provides atomic operations, schema validation, backup creation,
    and integrity checking for reliable JSON data persistence.
    """
    
    def __init__(self, config: JSONSafetyConfig):
        self.config = config
        
        # Schema registry
        self.schemas: Dict[str, JSONSchema] = {}
        
        # Operation tracking
        self.operation_history = []
        self.checksum_cache = {}
        
        # Error tracking
        self.error_count = 0
        self.last_error_time = None
        
        # Initialize with default schemas
        self._initialize_default_schemas()
    
    def safe_load_json(self, file_path: Path, schema_name: Optional[str] = None, 
                      validation_mode: JSONValidationMode = JSONValidationMode.BASIC) -> JSONOperationResult:
        """
        Safely load JSON file with validation and error handling
        
        Args:
            file_path: Path to JSON file
            schema_name: Name of schema for validation
            validation_mode: Level of validation to perform
            
        Returns:
            JSONOperationResult with loaded data or error information
        """
        
        operation_start = datetime.now()
        
        try:
            # Check file existence and accessibility
            if not file_path.exists():
                return JSONOperationResult(
                    success=False,
                    error=f"JSON file does not exist: {file_path}",
                    file_path=file_path,
                    operation_time=operation_start
                )
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                return JSONOperationResult(
                    success=False,
                    error=f"JSON file too large: {file_size_mb:.1f}MB > {self.config.max_file_size_mb}MB",
                    file_path=file_path,
                    operation_time=operation_start
                )
            
            # Load file content
            try:
                with file_path.open('r', encoding=self.config.encoding) as f:
                    raw_content = f.read()
            except Exception as e:
                return JSONOperationResult(
                    success=False,
                    error=f"Failed to read JSON file: {str(e)}",
                    file_path=file_path,
                    operation_time=operation_start
                )
            
            # Calculate checksum
            content_checksum = self._calculate_checksum(raw_content)
            
            # Parse JSON
            try:
                parsed_data = json.loads(raw_content)
            except json.JSONDecodeError as e:
                return JSONOperationResult(
                    success=False,
                    error=f"Invalid JSON syntax: {str(e)}",
                    file_path=file_path,
                    checksum=content_checksum,
                    operation_time=operation_start
                )
            
            # Perform validation based on mode
            validation_result = self._validate_json_data(parsed_data, schema_name, validation_mode)
            
            if not validation_result.valid and validation_mode in [JSONValidationMode.SCHEMA, JSONValidationMode.STRICT]:
                return JSONOperationResult(
                    success=False,
                    error=f"JSON validation failed: {'; '.join(validation_result.errors)}",
                    data=parsed_data,  # Return data even if validation failed
                    file_path=file_path,
                    checksum=content_checksum,
                    validation_passed=False,
                    warnings=validation_result.warnings,
                    operation_time=operation_start
                )
            
            # Update checksum cache
            self.checksum_cache[str(file_path)] = content_checksum
            
            # Track successful operation
            self._track_operation("load", file_path, True)
            
            return JSONOperationResult(
                success=True,
                data=parsed_data,
                file_path=file_path,
                checksum=content_checksum,
                validation_passed=validation_result.valid,
                warnings=validation_result.warnings,
                operation_time=operation_start
            )
            
        except Exception as e:
            # Unexpected error
            self._track_operation("load", file_path, False, str(e))
            return JSONOperationResult(
                success=False,
                error=f"Unexpected error loading JSON: {str(e)}",
                file_path=file_path,
                operation_time=operation_start
            )
    
    def safe_save_json(self, data: Any, file_path: Path, schema_name: Optional[str] = None,
                      create_backup: Optional[bool] = None, atomic: Optional[bool] = None) -> JSONOperationResult:
        """
        Safely save data as JSON with atomic writes and backup creation
        
        Args:
            data: Data to save as JSON
            file_path: Target file path
            schema_name: Name of schema for validation
            create_backup: Override config for backup creation
            atomic: Override config for atomic writes
            
        Returns:
            JSONOperationResult with save status and metadata
        """
        
        operation_start = datetime.now()
        
        # Use config defaults if not overridden
        create_backup = create_backup if create_backup is not None else self.config.create_backups
        atomic = atomic if atomic is not None else self.config.atomic_writes
        
        try:
            # Validate data before saving
            if schema_name:
                validation_result = self._validate_json_data(data, schema_name, JSONValidationMode.SCHEMA)
                if not validation_result.valid:
                    return JSONOperationResult(
                        success=False,
                        error=f"Data validation failed: {'; '.join(validation_result.errors)}",
                        data=data,
                        file_path=file_path,
                        validation_passed=False,
                        warnings=validation_result.warnings,
                        operation_time=operation_start
                    )
            
            # Serialize data to JSON
            try:
                json_content = json.dumps(
                    data, 
                    indent=self.config.indent,
                    ensure_ascii=self.config.ensure_ascii,
                    separators=(',', ': '),
                    sort_keys=True
                )
            except (TypeError, ValueError) as e:
                return JSONOperationResult(
                    success=False,
                    error=f"JSON serialization failed: {str(e)}",
                    data=data,
                    file_path=file_path,
                    operation_time=operation_start
                )
            
            # Calculate checksum
            content_checksum = self._calculate_checksum(json_content)
            
            # Create backup if requested and file exists
            backup_created = False
            if create_backup and file_path.exists():
                backup_result = self._create_backup(file_path)
                backup_created = backup_result.success
                if not backup_created:
                    # Log warning but continue
                    pass
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file (atomic or direct)
            if atomic:
                write_result = self._atomic_write_json(json_content, file_path)
            else:
                write_result = self._direct_write_json(json_content, file_path)
            
            if not write_result.success:
                return JSONOperationResult(
                    success=False,
                    error=write_result.error,
                    data=data,
                    file_path=file_path,
                    checksum=content_checksum,
                    backup_created=backup_created,
                    operation_time=operation_start
                )
            
            # Verify written file if checksums enabled
            if self.config.verify_checksums:
                verification_result = self._verify_written_file(file_path, content_checksum)
                if not verification_result.valid:
                    return JSONOperationResult(
                        success=False,
                        error=f"File verification failed: {verification_result.error}",
                        data=data,
                        file_path=file_path,
                        checksum=content_checksum,
                        backup_created=backup_created,
                        operation_time=operation_start
                    )
            
            # Update checksum cache
            self.checksum_cache[str(file_path)] = content_checksum
            
            # Track successful operation
            self._track_operation("save", file_path, True)
            
            return JSONOperationResult(
                success=True,
                data=data,
                file_path=file_path,
                checksum=content_checksum,
                validation_passed=True,
                backup_created=backup_created,
                operation_time=operation_start
            )
            
        except Exception as e:
            # Unexpected error
            self._track_operation("save", file_path, False, str(e))
            return JSONOperationResult(
                success=False,
                error=f"Unexpected error saving JSON: {str(e)}",
                data=data,
                file_path=file_path,
                operation_time=operation_start
            )
    
    def validate_json_against_schema(self, data: Any, schema_name: str) -> JSONValidationResult:
        """
        Validate JSON data against registered schema
        
        Args:
            data: Data to validate
            schema_name: Name of registered schema
            
        Returns:
            JSONValidationResult with validation status and details
        """
        
        if schema_name not in self.schemas:
            return JSONValidationResult(
                valid=False,
                errors=[f"Schema '{schema_name}' not registered"],
                schema_name=schema_name
            )
        
        schema = self.schemas[schema_name]
        
        try:
            # Validate against JSON schema
            jsonschema.validate(instance=data, schema=schema.schema)
            
            # Additional strict mode checks if enabled
            if schema.strict_mode:
                strict_validation = self._perform_strict_validation(data, schema)
                if not strict_validation.valid:
                    return strict_validation
            
            return JSONValidationResult(
                valid=True,
                schema_name=schema_name,
                schema_version=schema.version
            )
            
        except jsonschema.ValidationError as e:
            return JSONValidationResult(
                valid=False,
                errors=[str(e)],
                schema_name=schema_name,
                schema_version=schema.version,
                validation_path=list(e.absolute_path) if hasattr(e, 'absolute_path') else []
            )
        except Exception as e:
            return JSONValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"],
                schema_name=schema_name
            )
    
    def _atomic_write_json(self, json_content: str, target_path: Path) -> WriteResult:
        """Perform atomic write using temporary file and move"""
        
        try:
            # Create temporary file in same directory
            temp_dir = target_path.parent
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding=self.config.encoding,
                dir=temp_dir,
                delete=False,
                suffix='.tmp',
                prefix=f"{target_path.name}_"
            ) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(json_content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Force write to disk
            
            # Atomic move to final location
            shutil.move(str(temp_path), str(target_path))
            
            return WriteResult(success=True)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'temp_path' in locals() and temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            
            return WriteResult(
                success=False,
                error=f"Atomic write failed: {str(e)}"
            )
    
    def _direct_write_json(self, json_content: str, target_path: Path) -> WriteResult:
        """Perform direct write (non-atomic)"""
        
        try:
            with target_path.open('w', encoding=self.config.encoding) as f:
                f.write(json_content)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            return WriteResult(success=True)
            
        except Exception as e:
            return WriteResult(
                success=False,
                error=f"Direct write failed: {str(e)}"
            )
    
    def _create_backup(self, file_path: Path) -> BackupResult:
        """Create backup of existing file"""
        
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.parent / f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            
            return BackupResult(
                success=True,
                backup_path=backup_path
            )
            
        except Exception as e:
            return BackupResult(
                success=False,
                error=f"Backup creation failed: {str(e)}"
            )
    
    def _verify_written_file(self, file_path: Path, expected_checksum: str) -> VerificationResult:
        """Verify written file matches expected content"""
        
        try:
            if not file_path.exists():
                return VerificationResult(
                    valid=False,
                    error="File does not exist after write"
                )
            
            # Read written file and calculate checksum
            with file_path.open('r', encoding=self.config.encoding) as f:
                written_content = f.read()
            
            actual_checksum = self._calculate_checksum(written_content)
            
            if actual_checksum != expected_checksum:
                return VerificationResult(
                    valid=False,
                    error=f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
                )
            
            return VerificationResult(valid=True)
            
        except Exception as e:
            return VerificationResult(
                valid=False,
                error=f"Verification failed: {str(e)}"
            )
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content"""
        return hashlib.sha256(content.encode(self.config.encoding)).hexdigest()
    
    def _validate_json_data(self, data: Any, schema_name: Optional[str], 
                           validation_mode: JSONValidationMode) -> JSONValidationResult:
        """Validate JSON data according to specified mode"""
        
        if validation_mode == JSONValidationMode.NONE:
            return JSONValidationResult(valid=True)
        
        if validation_mode == JSONValidationMode.BASIC:
            # Basic validation - just check if it's JSON-serializable
            try:
                json.dumps(data)
                return JSONValidationResult(valid=True)
            except (TypeError, ValueError) as e:
                return JSONValidationResult(
                    valid=False,
                    errors=[f"Data not JSON-serializable: {str(e)}"]
                )
        
        if validation_mode in [JSONValidationMode.SCHEMA, JSONValidationMode.STRICT]:
            if not schema_name:
                return JSONValidationResult(
                    valid=False,
                    errors=["Schema name required for schema validation"]
                )
            
            return self.validate_json_against_schema(data, schema_name)
        
        return JSONValidationResult(valid=True)
    
    def _initialize_default_schemas(self):
        """Initialize default JSON schemas for autonomous TDD system"""
        
        # Configuration schema
        config_schema = JSONSchema(
            name="autonomous_config",
            description="Configuration for autonomous TDD system",
            schema={
                "type": "object",
                "properties": {
                    "system": {
                        "type": "object",
                        "properties": {
                            "project_root": {"type": "string"},
                            "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                            "debug_mode": {"type": "boolean"},
                            "max_memory_mb": {"type": "integer", "minimum": 100, "maximum": 8192},
                            "timeout_seconds": {"type": "integer", "minimum": 30, "maximum": 3600"}
                        },
                        "required": ["project_root"]
                    }
                },
                "required": ["system"]
            }
        )
        self.register_schema(config_schema)
        
        # Task decomposition result schema
        task_result_schema = JSONSchema(
            name="task_decomposition_result",
            description="Result of LLM task decomposition",
            schema={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "description": {"type": "string"},
                                "priority": {"type": "integer", "minimum": 1, "maximum": 10},
                                "estimated_duration": {"type": "string"},
                                "dependencies": {"type": "array", "items": {"type": "string"}},
                                "success_criteria": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["id", "description", "priority"]
                        }
                    },
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "reasoning": {"type": "string"}
                },
                "required": ["tasks", "confidence", "reasoning"]
            }
        )
        self.register_schema(task_result_schema)
        
        # Evidence collection schema
        evidence_schema = JSONSchema(
            name="evidence_collection",
            description="Evidence collection result",
            schema={
                "type": "object",
                "properties": {
                    "evidence_id": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "evidence_type": {"type": "string"},
                    "evidence_data": {"type": "object"},
                    "validation_result": {
                        "type": "object",
                        "properties": {
                            "authentic": {"type": "boolean"},
                            "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "fabrication_indicators": {"type": "array"}
                        },
                        "required": ["authentic", "confidence_score"]
                    }
                },
                "required": ["evidence_id", "timestamp", "evidence_type", "evidence_data", "validation_result"]
            }
        )
        self.register_schema(evidence_schema)
    
    def register_schema(self, schema: JSONSchema):
        """Register a JSON schema for validation"""
        self.schemas[schema.name] = schema
    
    def _track_operation(self, operation_type: str, file_path: Path, success: bool, error: Optional[str] = None):
        """Track JSON operation for monitoring and debugging"""
        
        operation_record = {
            'timestamp': datetime.now(),
            'operation_type': operation_type,
            'file_path': str(file_path),
            'success': success,
            'error': error
        }
        
        self.operation_history.append(operation_record)
        
        # Keep only recent operations (last 100)
        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-100:]
        
        # Update error tracking
        if not success:
            self.error_count += 1
            self.last_error_time = datetime.now()

# === Supporting Classes and Data Classes ===

@dataclass
class JSONValidationResult:
    """Result of JSON validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_name: Optional[str] = None
    schema_version: Optional[str] = None
    validation_path: List[str] = field(default_factory=list)

@dataclass
class WriteResult:
    """Result of file write operation"""
    success: bool
    error: Optional[str] = None

@dataclass
class BackupResult:
    """Result of backup operation"""
    success: bool
    backup_path: Optional[Path] = None
    error: Optional[str] = None

@dataclass
class VerificationResult:
    """Result of file verification"""
    valid: bool
    error: Optional[str] = None

# This pseudocode implements comprehensive JSON utilities with atomic operations,
# schema validation, backup creation, and integrity checking for reliable
# data persistence in the autonomous TDD system.