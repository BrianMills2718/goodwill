# Configuration Manager - Utilities Pseudocode
# Part of autonomous TDD system utility components

"""
Configuration Management System

Handles all configuration aspects of the autonomous TDD system including
environment variables, config files, defaults, and validation.
"""

from typing import Dict, List, Optional, Any, Union, Type
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import os
import yaml
from datetime import datetime

# === Configuration Data Classes ===

class ConfigSource(Enum):
    """Sources of configuration values"""
    DEFAULT = "default"
    CONFIG_FILE = "config_file"
    ENVIRONMENT = "environment"
    RUNTIME = "runtime"
    COMMAND_LINE = "command_line"

@dataclass
class ConfigValue:
    """A configuration value with metadata"""
    key: str
    value: Any
    source: ConfigSource
    type_hint: Type
    description: str
    validation_rules: List[str] = field(default_factory=list)
    is_sensitive: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ConfigSchema:
    """Schema definition for configuration"""
    section: str
    required_keys: List[str]
    optional_keys: List[str]
    validation_rules: Dict[str, List[str]]
    defaults: Dict[str, Any]
    type_hints: Dict[str, Type]
    descriptions: Dict[str, str]

@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    invalid_types: List[str] = field(default_factory=list)

# === Configuration Manager Implementation ===

class ConfigurationManager:
    """
    Comprehensive configuration management for autonomous TDD system
    
    Handles configuration loading, validation, environment overrides,
    and runtime updates with support for multiple sources and formats.
    """
    
    def __init__(self, config_dir: Path, project_root: Path):
        self.config_dir = Path(config_dir)
        self.project_root = Path(project_root)
        
        # Configuration storage
        self.config_values: Dict[str, ConfigValue] = {}
        self.config_schemas: Dict[str, ConfigSchema] = {}
        
        # File paths
        self.main_config_file = self.config_dir / "autonomous_tdd.json"
        self.user_config_file = self.config_dir / "user_config.json"
        self.env_config_file = self.config_dir / "env_config.yaml"
        
        # State tracking
        self.load_order = []
        self.validation_cache = {}
        self.last_reload_time = None
        
        # Initialize with default schemas
        self._initialize_default_schemas()
    
    def load_configuration(self, reload: bool = False) -> ConfigLoadResult:
        """
        Load configuration from all sources in priority order
        
        Priority order (highest to lowest):
        1. Command line arguments
        2. Environment variables
        3. User config file
        4. Main config file  
        5. Default values
        
        Args:
            reload: Force reload even if already loaded
            
        Returns:
            ConfigLoadResult with load status and any errors
        """
        
        try:
            if not reload and self.config_values and self.last_reload_time:
                # Configuration already loaded
                return ConfigLoadResult(
                    success=True,
                    sources_loaded=[],
                    values_loaded=len(self.config_values),
                    message="Configuration already loaded (use reload=True to force reload)"
                )
            
            # Clear existing configuration if reloading
            if reload:
                self.config_values.clear()
                self.load_order.clear()
            
            load_results = []
            
            # 1. Load default values first (lowest priority)
            default_result = self._load_default_values()
            load_results.append(default_result)
            
            # 2. Load main config file
            if self.main_config_file.exists():
                main_config_result = self._load_config_file(self.main_config_file, ConfigSource.CONFIG_FILE)
                load_results.append(main_config_result)
            
            # 3. Load user config file (overrides main config)
            if self.user_config_file.exists():
                user_config_result = self._load_config_file(self.user_config_file, ConfigSource.CONFIG_FILE)
                load_results.append(user_config_result)
            
            # 4. Load environment-specific config
            if self.env_config_file.exists():
                env_config_result = self._load_env_config_file()
                load_results.append(env_config_result)
            
            # 5. Load environment variables (highest priority)
            env_result = self._load_environment_variables()
            load_results.append(env_result)
            
            # 6. Validate complete configuration
            validation_result = self._validate_complete_configuration()
            
            # Update state
            self.last_reload_time = datetime.now()
            
            # Aggregate results
            total_values = len(self.config_values)
            sources_loaded = [result.source for result in load_results if result.success]
            errors = [error for result in load_results for error in result.errors]
            
            if validation_result.valid:
                return ConfigLoadResult(
                    success=True,
                    sources_loaded=sources_loaded,
                    values_loaded=total_values,
                    validation_result=validation_result,
                    load_time=datetime.now(),
                    errors=errors
                )
            else:
                return ConfigLoadResult(
                    success=False,
                    sources_loaded=sources_loaded,
                    values_loaded=total_values,
                    validation_result=validation_result,
                    load_time=datetime.now(),
                    errors=errors + validation_result.errors
                )
                
        except Exception as e:
            return ConfigLoadResult(
                success=False,
                error=f"Configuration loading failed: {str(e)}",
                sources_loaded=[],
                values_loaded=0
            )
    
    def get_config_value(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get configuration value with fallback and validation
        
        Args:
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found
            required: Raise exception if key not found and no default
            
        Returns:
            Configuration value
        """
        
        try:
            # Handle nested keys (e.g., "database.host")
            config_value = self._get_nested_value(key)
            
            if config_value is not None:
                return config_value.value
            
            # Key not found
            if required and default is None:
                raise ConfigKeyError(f"Required configuration key '{key}' not found")
            
            return default
            
        except Exception as e:
            if required:
                raise ConfigKeyError(f"Error retrieving required configuration key '{key}': {str(e)}")
            return default
    
    def set_config_value(self, key: str, value: Any, source: ConfigSource = ConfigSource.RUNTIME) -> bool:
        """
        Set configuration value at runtime
        
        Args:
            key: Configuration key
            value: Value to set
            source: Source of the configuration
            
        Returns:
            True if value was set successfully
        """
        
        try:
            # Validate value if schema exists
            validation_result = self._validate_single_value(key, value)
            if not validation_result.valid:
                raise ConfigValidationError(f"Invalid value for key '{key}': {validation_result.errors}")
            
            # Get type hint and description from schema
            type_hint = self._get_type_hint_for_key(key)
            description = self._get_description_for_key(key)
            
            # Create or update config value
            config_value = ConfigValue(
                key=key,
                value=value,
                source=source,
                type_hint=type_hint,
                description=description,
                last_updated=datetime.now()
            )
            
            self.config_values[key] = config_value
            
            # Add to load order if not already present
            if key not in self.load_order:
                self.load_order.append(key)
            
            return True
            
        except Exception as e:
            self._log_config_error(f"Failed to set config value '{key}': {str(e)}")
            return False
    
    def _load_default_values(self) -> ConfigLoadResult:
        """Load default configuration values"""
        
        defaults_loaded = 0
        errors = []
        
        for section_name, schema in self.config_schemas.items():
            for key, default_value in schema.defaults.items():
                full_key = f"{section_name}.{key}" if section_name != "root" else key
                
                try:
                    config_value = ConfigValue(
                        key=full_key,
                        value=default_value,
                        source=ConfigSource.DEFAULT,
                        type_hint=schema.type_hints.get(key, type(default_value)),
                        description=schema.descriptions.get(key, "No description available")
                    )
                    
                    self.config_values[full_key] = config_value
                    self.load_order.append(full_key)
                    defaults_loaded += 1
                    
                except Exception as e:
                    errors.append(f"Failed to load default value for '{full_key}': {str(e)}")
        
        return ConfigLoadResult(
            success=len(errors) == 0,
            source=ConfigSource.DEFAULT,
            values_loaded=defaults_loaded,
            errors=errors
        )
    
    def _load_config_file(self, config_file: Path, source: ConfigSource) -> ConfigLoadResult:
        """Load configuration from JSON or YAML file"""
        
        try:
            with config_file.open('r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    raw_config = json.load(f)
                elif config_file.suffix.lower() in ['.yml', '.yaml']:
                    raw_config = yaml.safe_load(f)
                else:
                    return ConfigLoadResult(
                        success=False,
                        error=f"Unsupported config file format: {config_file.suffix}",
                        source=source
                    )
            
            # Flatten nested configuration
            flattened_config = self._flatten_config_dict(raw_config)
            
            values_loaded = 0
            errors = []
            
            for key, value in flattened_config.items():
                try:
                    # Validate value
                    validation_result = self._validate_single_value(key, value)
                    if not validation_result.valid:
                        errors.extend(validation_result.errors)
                        continue
                    
                    # Get metadata from schema
                    type_hint = self._get_type_hint_for_key(key)
                    description = self._get_description_for_key(key)
                    
                    # Create config value
                    config_value = ConfigValue(
                        key=key,
                        value=value,
                        source=source,
                        type_hint=type_hint,
                        description=description
                    )
                    
                    # Override existing value (later sources have higher priority)
                    self.config_values[key] = config_value
                    
                    if key not in self.load_order:
                        self.load_order.append(key)
                    
                    values_loaded += 1
                    
                except Exception as e:
                    errors.append(f"Failed to process key '{key}' from {config_file}: {str(e)}")
            
            return ConfigLoadResult(
                success=len(errors) == 0,
                source=source,
                values_loaded=values_loaded,
                errors=errors,
                file_path=str(config_file)
            )
            
        except Exception as e:
            return ConfigLoadResult(
                success=False,
                error=f"Failed to load config file {config_file}: {str(e)}",
                source=source,
                file_path=str(config_file)
            )
    
    def _load_environment_variables(self) -> ConfigLoadResult:
        """Load configuration from environment variables"""
        
        # Environment variable prefix for autonomous TDD system
        env_prefix = "AUTONOMOUS_TDD_"
        
        values_loaded = 0
        errors = []
        
        for env_key, env_value in os.environ.items():
            if env_key.startswith(env_prefix):
                # Convert environment variable name to config key
                config_key = env_key[len(env_prefix):].lower().replace('_', '.')
                
                try:
                    # Convert string value to appropriate type
                    converted_value = self._convert_env_value(config_key, env_value)
                    
                    # Validate value
                    validation_result = self._validate_single_value(config_key, converted_value)
                    if not validation_result.valid:
                        errors.extend(validation_result.errors)
                        continue
                    
                    # Get metadata from schema
                    type_hint = self._get_type_hint_for_key(config_key)
                    description = self._get_description_for_key(config_key)
                    
                    # Create config value
                    config_value = ConfigValue(
                        key=config_key,
                        value=converted_value,
                        source=ConfigSource.ENVIRONMENT,
                        type_hint=type_hint,
                        description=description,
                        is_sensitive=self._is_sensitive_key(config_key)
                    )
                    
                    # Override existing value (environment has high priority)
                    self.config_values[config_key] = config_value
                    
                    if config_key not in self.load_order:
                        self.load_order.append(config_key)
                    
                    values_loaded += 1
                    
                except Exception as e:
                    errors.append(f"Failed to process environment variable '{env_key}': {str(e)}")
        
        return ConfigLoadResult(
            success=len(errors) == 0,
            source=ConfigSource.ENVIRONMENT,
            values_loaded=values_loaded,
            errors=errors
        )
    
    def _convert_env_value(self, config_key: str, env_value: str) -> Any:
        """Convert environment variable string to appropriate type"""
        
        # Get expected type from schema
        expected_type = self._get_type_hint_for_key(config_key)
        
        if expected_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif expected_type == int:
            return int(env_value)
        elif expected_type == float:
            return float(env_value)
        elif expected_type == list:
            # Comma-separated values
            return [item.strip() for item in env_value.split(',') if item.strip()]
        elif expected_type == dict:
            # JSON string
            return json.loads(env_value)
        else:
            # String (default)
            return env_value
    
    def _flatten_config_dict(self, config_dict: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        """Flatten nested configuration dictionary"""
        
        flattened = {}
        
        for key, value in config_dict.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                nested_flattened = self._flatten_config_dict(value, full_key)
                flattened.update(nested_flattened)
            else:
                flattened[full_key] = value
        
        return flattened
    
    def _initialize_default_schemas(self):
        """Initialize default configuration schemas"""
        
        # Core system configuration schema
        self.config_schemas["system"] = ConfigSchema(
            section="system",
            required_keys=["project_root"],
            optional_keys=["log_level", "debug_mode", "max_memory_mb", "timeout_seconds"],
            validation_rules={
                "project_root": ["path_exists"],
                "log_level": ["in:DEBUG,INFO,WARNING,ERROR"],
                "max_memory_mb": ["min:100", "max:8192"],
                "timeout_seconds": ["min:30", "max:3600"]
            },
            defaults={
                "log_level": "INFO",
                "debug_mode": False,
                "max_memory_mb": 2048,
                "timeout_seconds": 300
            },
            type_hints={
                "project_root": str,
                "log_level": str,
                "debug_mode": bool,
                "max_memory_mb": int,
                "timeout_seconds": int
            },
            descriptions={
                "project_root": "Root directory of the project",
                "log_level": "Logging level for the system",
                "debug_mode": "Enable debug mode with verbose output",
                "max_memory_mb": "Maximum memory usage in megabytes",
                "timeout_seconds": "Default timeout for operations in seconds"
            }
        )
        
        # LLM integration configuration schema
        self.config_schemas["llm"] = ConfigSchema(
            section="llm",
            required_keys=[],
            optional_keys=["max_context_tokens", "max_response_tokens", "temperature", "max_retries"],
            validation_rules={
                "max_context_tokens": ["min:1000", "max:200000"],
                "max_response_tokens": ["min:100", "max:8000"],
                "temperature": ["min:0.0", "max:2.0"],
                "max_retries": ["min:1", "max:10"]
            },
            defaults={
                "max_context_tokens": 150000,
                "max_response_tokens": 4000,
                "temperature": 0.1,
                "max_retries": 3
            },
            type_hints={
                "max_context_tokens": int,
                "max_response_tokens": int,
                "temperature": float,
                "max_retries": int
            },
            descriptions={
                "max_context_tokens": "Maximum tokens for LLM context",
                "max_response_tokens": "Maximum tokens for LLM response",
                "temperature": "Temperature for LLM generation",
                "max_retries": "Maximum retry attempts for failed LLM calls"
            }
        )
        
        # Evidence collection configuration schema
        self.config_schemas["evidence"] = ConfigSchema(
            section="evidence",
            required_keys=[],
            optional_keys=["evidence_directory", "max_evidence_files", "compression_enabled"],
            validation_rules={
                "max_evidence_files": ["min:10", "max:10000"],
                "compression_enabled": ["bool"]
            },
            defaults={
                "evidence_directory": ".autonomous_state/evidence",
                "max_evidence_files": 1000,
                "compression_enabled": True
            },
            type_hints={
                "evidence_directory": str,
                "max_evidence_files": int,
                "compression_enabled": bool
            },
            descriptions={
                "evidence_directory": "Directory for storing evidence files",
                "max_evidence_files": "Maximum number of evidence files to keep",
                "compression_enabled": "Enable compression for evidence storage"
            }
        )

# === Supporting Classes ===

class ConfigKeyError(Exception):
    """Exception raised when configuration key is not found"""
    pass

class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails"""
    pass

@dataclass
class ConfigLoadResult:
    """Result of configuration loading operation"""
    success: bool
    sources_loaded: List[ConfigSource] = field(default_factory=list)
    values_loaded: int = 0
    validation_result: Optional[ConfigValidationResult] = None
    load_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    error: Optional[str] = None
    source: Optional[ConfigSource] = None
    file_path: Optional[str] = None

# This pseudocode implements a comprehensive configuration management system
# that handles multiple configuration sources, validation, type conversion,
# and environment overrides for the autonomous TDD system.