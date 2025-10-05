#!/usr/bin/env python3
"""
CONFIG MANAGER - Foundation Component (No Dependencies)
Handles loading, validation, and management of system configuration
"""

# RELATES_TO: ../../config/autonomous_config.json, ../utils/json_utils.py

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded"""
    pass

class ConfigManager:
    """
    Manages autonomous TDD system configuration with defensive programming
    
    FOUNDATION COMPONENT: No dependencies on other system components
    Can be imported and used by any other component
    """
    
    def __init__(self, project_root: str):
        """
        Initialize configuration manager
        
        INPUTS:
        - project_root: Absolute path to project directory
        
        VALIDATION:
        - Verify project_root exists and is directory
        - Verify project_root is writable
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise ConfigurationError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise ConfigurationError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise ConfigurationError(f"Project root is not a directory: {project_root}")
        
        if not os.access(self.project_root, os.W_OK):
            raise ConfigurationError(f"No write permission to project root: {project_root}")
        
        # Configuration file paths
        self.config_dir = self.project_root / 'config'
        self.main_config_file = self.config_dir / 'autonomous_config.json'
        self.environment_config_dir = self.config_dir / 'environments'
        
        # Loaded configuration cache
        self._config_cache = None
        self._config_file_mtime = None
    
    def load_configuration(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Load complete system configuration with defaults and environment overrides
        
        LOADING ORDER:
        1. Built-in defaults (always available)
        2. Main config file (config/autonomous_config.json)
        3. Environment-specific config (config/environments/{env}.json)
        4. Environment variable overrides
        
        PARAMETERS:
        - environment: Optional environment name (development, testing, production)
        
        RETURNS: Complete configuration dictionary
        
        CACHING: Configuration is cached and only reloaded if file modified
        """
        
        # Check if cached config is still valid
        if self._is_config_cache_valid():
            return self._config_cache
        
        # STEP 1: Start with built-in defaults
        config = self._get_default_configuration()
        
        # STEP 2: Overlay main configuration file
        if self.main_config_file.exists():
            try:
                main_config = self._load_json_file(self.main_config_file)
                config = self._merge_configurations(config, main_config)
            except Exception as e:
                raise ConfigurationError(f"Failed to load main config: {e}")
        
        # STEP 3: Overlay environment-specific configuration
        if environment:
            env_config_file = self.environment_config_dir / f'{environment}.json'
            if env_config_file.exists():
                try:
                    env_config = self._load_json_file(env_config_file)
                    config = self._merge_configurations(config, env_config)
                except Exception as e:
                    raise ConfigurationError(f"Failed to load environment config: {e}")
        
        # STEP 4: Apply environment variable overrides
        config = self._apply_environment_variable_overrides(config)
        
        # STEP 5: Validate final configuration
        self._validate_configuration(config)
        
        # Cache the loaded configuration
        self._config_cache = config
        if self.main_config_file.exists():
            self._config_file_mtime = self.main_config_file.stat().st_mtime
        
        return config
    
    def save_configuration(self, config: Dict[str, Any], environment: Optional[str] = None) -> bool:
        """
        Save configuration to appropriate file
        
        PARAMETERS:
        - config: Configuration dictionary to save
        - environment: If specified, save to environment-specific file
        
        RETURNS: True if save successful, False otherwise
        
        SAFETY: Creates backup before saving, validates before writing
        """
        
        try:
            # Validate configuration before saving
            self._validate_configuration(config)
            
            # Determine target file
            if environment:
                target_file = self.environment_config_dir / f'{environment}.json'
                target_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                target_file = self.main_config_file
                target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if file exists
            if target_file.exists():
                backup_file = target_file.with_suffix('.json.backup')
                backup_file.write_text(target_file.read_text())
            
            # Write configuration atomically
            temp_file = target_file.with_suffix('.json.tmp')
            
            with open(temp_file, 'w') as f:
                json.dump(config, f, indent=2, sort_keys=True)
            
            # Verify written file is valid JSON
            with open(temp_file, 'r') as f:
                json.load(f)  # Will raise exception if invalid
            
            # Atomic move to final location
            temp_file.replace(target_file)
            
            # Invalidate cache
            self._config_cache = None
            self._config_file_mtime = None
            
            return True
            
        except Exception as e:
            # Clean up temp file if it exists
            temp_file = target_file.with_suffix('.json.tmp')
            if temp_file.exists():
                temp_file.unlink()
            
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation path
        
        EXAMPLES:
        - get_config_value('logging.log_level') → 'INFO'
        - get_config_value('autonomous_behavior.max_hook_iterations') → 50
        - get_config_value('nonexistent.key', 'default') → 'default'
        
        PARAMETERS:
        - key_path: Dot-separated path to configuration value
        - default: Default value if key not found
        
        RETURNS: Configuration value or default
        """
        
        config = self.load_configuration()
        
        # Split key path and traverse configuration
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            
            return current
            
        except (KeyError, TypeError):
            return default
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """
        Get built-in default configuration
        
        RETURNS: Complete default configuration dictionary
        
        NOTE: These defaults ensure system can operate even without config files
        """
        
        return {
            "autonomous_behavior": {
                "max_session_duration_minutes": 120,
                "max_hook_iterations": 50,
                "max_consecutive_failures": 5,
                "evidence_validation_strictness": "strict",
                "auto_escalation_enabled": True,
                "pause_on_uncertainty": False
            },
            "context_management": {
                "max_context_tokens": 150000,
                "context_expansion_depth": 2,
                "enable_content_analysis": False,
                "prioritize_recent_files": True,
                "python_signature_loading": True,
                "partial_file_loading_enabled": True
            },
            "integration_settings": {
                "claude_code_timeout_seconds": 30,
                "test_framework_timeout_seconds": 120,
                "external_service_timeout_seconds": 60,
                "file_operation_timeout_seconds": 10
            },
            "evidence_collection": {
                "enable_anti_fabrication": True,
                "require_real_dependencies": True,
                "evidence_retention_days": 7,
                "detailed_logging": True,
                "mock_detection_enabled": True,
                "network_activity_validation": True
            },
            "safety_mechanisms": {
                "enable_loop_detection": True,
                "enable_resource_monitoring": True,
                "max_file_modifications_per_session": 100,
                "backup_before_modifications": True,
                "disk_space_threshold_mb": 100,
                "max_log_size_mb": 50
            },
            "logging": {
                "log_level": "INFO",
                "structured_format": True,
                "log_rotation": True,
                "max_log_size_mb": 50,
                "debug_components": []
            },
            "cross_reference": {
                "enable_content_analysis": False,
                "relationship_discovery_depth": 2,
                "auto_update_enabled": True,
                "validation_on_load": True
            }
        }
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse JSON file with error handling
        
        PARAMETERS:
        - file_path: Path to JSON file
        
        RETURNS: Parsed JSON data
        
        RAISES: Exception if file cannot be loaded or parsed
        """
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {file_path}: {e}")
        
        except IOError as e:
            raise ConfigurationError(f"Cannot read {file_path}: {e}")
    
    def _merge_configurations(self, base_config: Dict[str, Any], 
                            override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries
        Override config values take precedence over base config
        
        PARAMETERS:
        - base_config: Base configuration (lower priority)
        - override_config: Override configuration (higher priority)
        
        RETURNS: Merged configuration dictionary
        """
        
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if (key in merged and 
                isinstance(merged[key], dict) and 
                isinstance(value, dict)):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_configurations(merged[key], value)
            else:
                # Direct override for non-dict values
                merged[key] = value
        
        return merged
    
    def _apply_environment_variable_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration
        
        ENVIRONMENT VARIABLE FORMAT:
        AUTONOMOUS_TDD_{SECTION}_{KEY} = value
        
        EXAMPLES:
        AUTONOMOUS_TDD_LOGGING_LOG_LEVEL=DEBUG
        AUTONOMOUS_TDD_AUTONOMOUS_BEHAVIOR_MAX_HOOK_ITERATIONS=100
        
        PARAMETERS:
        - config: Base configuration to override
        
        RETURNS: Configuration with environment variable overrides applied
        """
        
        modified_config = config.copy()
        env_prefix = 'AUTONOMOUS_TDD_'
        
        for env_key, env_value in os.environ.items():
            if env_key.startswith(env_prefix):
                # Parse environment variable key
                config_path = env_key[len(env_prefix):].lower().replace('_', '.')
                
                # Convert string value to appropriate type
                typed_value = self._convert_env_value_type(env_value)
                
                # Apply override using dot notation
                self._set_config_value(modified_config, config_path, typed_value)
        
        return modified_config
    
    def _convert_env_value_type(self, value: str) -> Any:
        """
        Convert environment variable string to appropriate Python type
        
        CONVERSION RULES:
        - 'true'/'false' → boolean
        - Numeric strings → int or float
        - Everything else → string
        
        PARAMETERS:
        - value: Environment variable string value
        
        RETURNS: Converted value with appropriate type
        """
        
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # Numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String (default)
        return value
    
    def _set_config_value(self, config: Dict[str, Any], key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation path
        
        PARAMETERS:
        - config: Configuration dictionary to modify
        - key_path: Dot-separated path to set
        - value: Value to set
        """
        
        keys = key_path.split('.')
        current = config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set final value
        current[keys[-1]] = value
    
    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration values are reasonable and complete
        
        VALIDATION CHECKS:
        - Required sections exist
        - Numeric values are positive and within reasonable ranges
        - String values are valid choices
        - Boolean values are actually boolean
        
        PARAMETERS:
        - config: Configuration dictionary to validate
        
        RAISES: ConfigurationError if validation fails
        """
        
        required_sections = [
            'autonomous_behavior',
            'context_management', 
            'integration_settings',
            'evidence_collection',
            'safety_mechanisms',
            'logging'
        ]
        
        # Check required sections exist
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required configuration section: {section}")
            
            if not isinstance(config[section], dict):
                raise ConfigurationError(f"Configuration section {section} must be a dictionary")
        
        # Validate autonomous behavior settings
        ab = config['autonomous_behavior']
        
        max_iterations = ab.get('max_hook_iterations', 0)
        if not isinstance(max_iterations, int) or max_iterations <= 0:
            raise ConfigurationError("max_hook_iterations must be positive integer")
        
        if max_iterations > 1000:
            raise ConfigurationError("max_hook_iterations too high (max 1000)")
        
        strictness = ab.get('evidence_validation_strictness')
        if strictness not in ['strict', 'moderate', 'permissive']:
            raise ConfigurationError("evidence_validation_strictness must be strict/moderate/permissive")
        
        # Validate context management settings
        cm = config['context_management']
        
        max_tokens = cm.get('max_context_tokens', 0)
        if not isinstance(max_tokens, int) or max_tokens <= 1000:
            raise ConfigurationError("max_context_tokens must be integer >= 1000")
        
        if max_tokens > 200000:
            raise ConfigurationError("max_context_tokens too high (max 200000)")
        
        # Validate logging settings
        log = config['logging']
        
        log_level = log.get('log_level', '').upper()
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ConfigurationError("log_level must be DEBUG/INFO/WARNING/ERROR/CRITICAL")
    
    def _is_config_cache_valid(self) -> bool:
        """
        Check if cached configuration is still valid
        
        RETURNS: True if cache is valid, False if needs reload
        """
        
        if self._config_cache is None:
            return False
        
        if not self.main_config_file.exists():
            return True  # No config file, cache is valid
        
        current_mtime = self.main_config_file.stat().st_mtime
        return current_mtime == self._config_file_mtime