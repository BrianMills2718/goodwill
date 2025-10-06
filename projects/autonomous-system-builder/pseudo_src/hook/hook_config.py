#!/usr/bin/env python3
"""
HOOK CONFIG - Hook Integration Layer
Configuration management for autonomous hook system

RELATES_TO: autonomous_hook.py, ../config/config_manager.py, ../utils/json_utils.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

class HookTriggerMode(Enum):
    """Modes for hook triggering"""
    AUTOMATIC = "automatic"  # Hook triggers automatically on conditions
    MANUAL = "manual"       # Hook only triggers on explicit user action
    CONDITIONAL = "conditional"  # Hook triggers based on specific conditions
    DISABLED = "disabled"   # Hook is disabled

class HookExecutionPolicy(Enum):
    """Policies for hook execution behavior"""
    STRICT = "strict"           # Strict adherence to methodology and safety limits
    PERMISSIVE = "permissive"   # More flexible execution with warnings
    DEVELOPMENT = "development" # Development mode with enhanced debugging
    PRODUCTION = "production"   # Production mode with conservative safety

@dataclass
class SafetyLimits:
    """Safety limits for autonomous hook execution"""
    max_hook_executions_per_session: int = 50
    max_consecutive_failures: int = 5
    max_session_duration_hours: float = 8.0
    max_file_modifications_per_session: int = 100
    max_llm_queries_per_hour: int = 30
    require_user_confirmation_for_major_changes: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'max_hook_executions_per_session': self.max_hook_executions_per_session,
            'max_consecutive_failures': self.max_consecutive_failures,
            'max_session_duration_hours': self.max_session_duration_hours,
            'max_file_modifications_per_session': self.max_file_modifications_per_session,
            'max_llm_queries_per_hour': self.max_llm_queries_per_hour,
            'require_user_confirmation_for_major_changes': self.require_user_confirmation_for_major_changes
        }

@dataclass
class HookBehaviorSettings:
    """Settings for autonomous hook behavior"""
    trigger_mode: HookTriggerMode = HookTriggerMode.AUTOMATIC
    execution_policy: HookExecutionPolicy = HookExecutionPolicy.STRICT
    enable_learning_mode: bool = True
    enable_cross_session_memory: bool = True
    enable_progress_tracking: bool = True
    enable_evidence_validation: bool = True
    
    # Interaction settings
    verbose_logging: bool = True
    show_decision_rationale: bool = True
    include_context_in_responses: bool = False
    enable_user_guidance: bool = True
    
    # Methodology settings
    enforce_phase_ordering: bool = True
    require_test_first_development: bool = True
    enable_anti_fabrication_checks: bool = True
    allow_methodology_customization: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trigger_mode': self.trigger_mode.value,
            'execution_policy': self.execution_policy.value,
            'enable_learning_mode': self.enable_learning_mode,
            'enable_cross_session_memory': self.enable_cross_session_memory,
            'enable_progress_tracking': self.enable_progress_tracking,
            'enable_evidence_validation': self.enable_evidence_validation,
            'verbose_logging': self.verbose_logging,
            'show_decision_rationale': self.show_decision_rationale,
            'include_context_in_responses': self.include_context_in_responses,
            'enable_user_guidance': self.enable_user_guidance,
            'enforce_phase_ordering': self.enforce_phase_ordering,
            'require_test_first_development': self.require_test_first_development,
            'enable_anti_fabrication_checks': self.enable_anti_fabrication_checks,
            'allow_methodology_customization': self.allow_methodology_customization
        }

@dataclass
class HookConfiguration:
    """Complete configuration for autonomous hook system"""
    safety_limits: SafetyLimits = field(default_factory=SafetyLimits)
    behavior_settings: HookBehaviorSettings = field(default_factory=HookBehaviorSettings)
    
    # Project-specific settings
    project_root: str = ""
    project_type: str = "python"  # python, javascript, java, etc.
    methodology_variant: str = "standard_tdd"
    
    # Integration settings
    claude_code_integration: Dict[str, Any] = field(default_factory=dict)
    external_tool_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Logging and debugging
    log_level: str = "INFO"
    enable_performance_monitoring: bool = True
    save_decision_logs: bool = True
    
    # Environment and context
    environment: str = "development"  # development, testing, production
    configuration_version: str = "1.0.0"
    last_updated: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'safety_limits': self.safety_limits.to_dict(),
            'behavior_settings': self.behavior_settings.to_dict(),
            'project_root': self.project_root,
            'project_type': self.project_type,
            'methodology_variant': self.methodology_variant,
            'claude_code_integration': self.claude_code_integration,
            'external_tool_configuration': self.external_tool_configuration,
            'log_level': self.log_level,
            'enable_performance_monitoring': self.enable_performance_monitoring,
            'save_decision_logs': self.save_decision_logs,
            'environment': self.environment,
            'configuration_version': self.configuration_version,
            'last_updated': self.last_updated
        }

class HookConfigError(Exception):
    """Raised when hook configuration operations fail"""
    pass

class AutonomousHookConfigManager:
    """
    Configuration manager for autonomous hook system
    
    HOOK INTEGRATION COMPONENT: Manages hook-specific configuration
    Handles loading, validation, and updating of hook settings
    """
    
    def __init__(self, project_root: str):
        """
        Initialize hook configuration manager
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes configuration file paths
        - Sets up configuration validation rules
        - Provides fallback default configuration
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise HookConfigError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise HookConfigError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise HookConfigError(f"Project root is not a directory: {project_root}")
        
        # Configuration file paths
        self.hook_config_file = self.project_root / '.claude' / 'hook_config.json'
        self.user_overrides_file = self.project_root / '.claude' / 'hook_user_overrides.json'
        self.environment_config_dir = self.project_root / 'config' / 'environments'
        
        # Current configuration
        self.current_config: Optional[HookConfiguration] = None
        
        # Configuration validation rules
        self.validation_rules = self._initialize_validation_rules()
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def load_hook_configuration(self, environment: Optional[str] = None) -> HookConfiguration:
        """
        Load complete hook configuration with environment and user overrides
        
        PARAMETERS:
        - environment: Specific environment configuration (development/testing/production)
        
        RETURNS: Complete hook configuration object
        
        CONFIGURATION LOADING ORDER:
        1. Load default configuration
        2. Apply environment-specific overrides
        3. Apply user-specific overrides
        4. Validate final configuration
        5. Cache loaded configuration
        """
        
        try:
            self.logger.info("Loading hook configuration")
            
            # Start with default configuration
            config = self._get_default_hook_configuration()
            
            # Apply environment-specific configuration if specified
            if environment:
                env_config = self._load_environment_configuration(environment)
                if env_config:
                    config = self._merge_configurations(config, env_config)
            
            # Load base hook configuration file
            if self.hook_config_file.exists():
                base_config = self._load_configuration_file(self.hook_config_file)
                config = self._merge_configurations(config, base_config)
            
            # Apply user overrides
            if self.user_overrides_file.exists():
                user_config = self._load_configuration_file(self.user_overrides_file)
                config = self._merge_configurations(config, user_config)
            
            # Set project-specific settings
            config.project_root = str(self.project_root)
            config.last_updated = datetime.now(timezone.utc).isoformat()
            
            # Validate final configuration
            validation_result = self._validate_configuration(config)
            if not validation_result['valid']:
                raise HookConfigError(f"Invalid configuration: {validation_result['errors']}")
            
            # Cache configuration
            self.current_config = config
            
            self.logger.info("Hook configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load hook configuration: {str(e)}")
            
            # Return safe default configuration on failure
            default_config = self._get_default_hook_configuration()
            default_config.project_root = str(self.project_root)
            return default_config
    
    def save_hook_configuration(self, config: HookConfiguration, 
                               save_as_user_override: bool = False) -> bool:
        """
        Save hook configuration to disk
        
        PARAMETERS:
        - config: Configuration object to save
        - save_as_user_override: If True, save as user override instead of base config
        
        RETURNS: True if save successful, False otherwise
        
        CONFIGURATION SAVING:
        1. Validate configuration before saving
        2. Create backup of existing configuration
        3. Save to appropriate file (base config or user overrides)
        4. Verify saved configuration can be loaded
        """
        
        try:
            # Validate configuration before saving
            validation_result = self._validate_configuration(config)
            if not validation_result['valid']:
                self.logger.error(f"Cannot save invalid configuration: {validation_result['errors']}")
                return False
            
            # Choose target file
            target_file = self.user_overrides_file if save_as_user_override else self.hook_config_file
            
            # Create backup of existing configuration
            if target_file.exists():
                backup_file = target_file.with_suffix('.backup')
                backup_file.write_text(target_file.read_text())
            
            # Ensure directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            config_data = config.to_dict()
            
            # Use JSON utilities for safe saving
            from ..utils.json_utils import JSONUtilities
            json_utils = JSONUtilities()
            
            success = json_utils.save_json_file(config_data, str(target_file))
            
            if success:
                self.logger.info(f"Hook configuration saved to {target_file}")
                self.current_config = config
                return True
            else:
                self.logger.error("Failed to save hook configuration")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving hook configuration: {str(e)}")
            return False
    
    def get_safety_limits(self) -> SafetyLimits:
        """Get current safety limits configuration"""
        
        if self.current_config is None:
            self.load_hook_configuration()
        
        return self.current_config.safety_limits if self.current_config else SafetyLimits()
    
    def get_behavior_settings(self) -> HookBehaviorSettings:
        """Get current behavior settings configuration"""
        
        if self.current_config is None:
            self.load_hook_configuration()
        
        return self.current_config.behavior_settings if self.current_config else HookBehaviorSettings()
    
    def update_safety_limit(self, limit_name: str, new_value: Union[int, float, bool]) -> bool:
        """
        Update specific safety limit setting
        
        PARAMETERS:
        - limit_name: Name of safety limit to update
        - new_value: New value for the limit
        
        RETURNS: True if update successful, False otherwise
        """
        
        try:
            if self.current_config is None:
                self.load_hook_configuration()
            
            if not self.current_config:
                return False
            
            # Validate limit name exists
            if not hasattr(self.current_config.safety_limits, limit_name):
                self.logger.error(f"Unknown safety limit: {limit_name}")
                return False
            
            # Update the limit
            setattr(self.current_config.safety_limits, limit_name, new_value)
            
            # Validate updated configuration
            validation_result = self._validate_configuration(self.current_config)
            if not validation_result['valid']:
                self.logger.error(f"Invalid safety limit update: {validation_result['errors']}")
                return False
            
            # Save updated configuration
            return self.save_hook_configuration(self.current_config, save_as_user_override=True)
            
        except Exception as e:
            self.logger.error(f"Failed to update safety limit: {str(e)}")
            return False
    
    def reset_to_defaults(self, component: Optional[str] = None) -> bool:
        """
        Reset configuration to defaults
        
        PARAMETERS:
        - component: Specific component to reset (safety_limits, behavior_settings, or None for all)
        
        RETURNS: True if reset successful, False otherwise
        """
        
        try:
            if component is None:
                # Reset entire configuration
                self.current_config = self._get_default_hook_configuration()
                self.current_config.project_root = str(self.project_root)
            
            elif component == "safety_limits":
                if self.current_config:
                    self.current_config.safety_limits = SafetyLimits()
            
            elif component == "behavior_settings":
                if self.current_config:
                    self.current_config.behavior_settings = HookBehaviorSettings()
            
            else:
                self.logger.error(f"Unknown configuration component: {component}")
                return False
            
            # Save reset configuration
            if self.current_config:
                return self.save_hook_configuration(self.current_config)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {str(e)}")
            return False
    
    def _get_default_hook_configuration(self) -> HookConfiguration:
        """Get default hook configuration for new projects"""
        
        return HookConfiguration(
            safety_limits=SafetyLimits(),
            behavior_settings=HookBehaviorSettings(),
            project_type="python",
            methodology_variant="standard_tdd",
            claude_code_integration={
                'hook_timeout_seconds': 30,
                'max_response_size': 10000,
                'enable_hook_chaining': False
            },
            external_tool_configuration={
                'enable_web_search': True,
                'enable_context7_integration': True,
                'enable_file_system_operations': True
            },
            log_level="INFO",
            enable_performance_monitoring=True,
            save_decision_logs=True,
            environment="development",
            configuration_version="1.0.0"
        )
    
    def _load_configuration_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        
        try:
            from ..utils.json_utils import JSONUtilities
            json_utils = JSONUtilities()
            
            config_data = json_utils.load_json_file(str(config_file))
            return config_data if config_data else {}
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration file {config_file}: {str(e)}")
            return {}
    
    def _load_environment_configuration(self, environment: str) -> Optional[Dict[str, Any]]:
        """Load environment-specific configuration"""
        
        env_file = self.environment_config_dir / f"{environment}.json"
        
        if not env_file.exists():
            self.logger.info(f"No environment configuration found for: {environment}")
            return None
        
        return self._load_configuration_file(env_file)
    
    def _merge_configurations(self, base_config: HookConfiguration, 
                             override_data: Dict[str, Any]) -> HookConfiguration:
        """Merge configuration override data into base configuration"""
        
        try:
            # Convert base config to dict for easier merging
            base_data = base_config.to_dict()
            
            # Deep merge override data
            merged_data = self._deep_merge_dicts(base_data, override_data)
            
            # Convert back to configuration object
            return self._dict_to_configuration(merged_data)
            
        except Exception as e:
            self.logger.error(f"Failed to merge configurations: {str(e)}")
            return base_config
    
    def _deep_merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_configuration(self, config_data: Dict[str, Any]) -> HookConfiguration:
        """Convert dictionary to HookConfiguration object"""
        
        # Create safety limits
        safety_data = config_data.get('safety_limits', {})
        safety_limits = SafetyLimits(
            max_hook_executions_per_session=safety_data.get('max_hook_executions_per_session', 50),
            max_consecutive_failures=safety_data.get('max_consecutive_failures', 5),
            max_session_duration_hours=safety_data.get('max_session_duration_hours', 8.0),
            max_file_modifications_per_session=safety_data.get('max_file_modifications_per_session', 100),
            max_llm_queries_per_hour=safety_data.get('max_llm_queries_per_hour', 30),
            require_user_confirmation_for_major_changes=safety_data.get('require_user_confirmation_for_major_changes', True)
        )
        
        # Create behavior settings
        behavior_data = config_data.get('behavior_settings', {})
        behavior_settings = HookBehaviorSettings(
            trigger_mode=HookTriggerMode(behavior_data.get('trigger_mode', 'automatic')),
            execution_policy=HookExecutionPolicy(behavior_data.get('execution_policy', 'strict')),
            enable_learning_mode=behavior_data.get('enable_learning_mode', True),
            enable_cross_session_memory=behavior_data.get('enable_cross_session_memory', True),
            enable_progress_tracking=behavior_data.get('enable_progress_tracking', True),
            enable_evidence_validation=behavior_data.get('enable_evidence_validation', True),
            verbose_logging=behavior_data.get('verbose_logging', True),
            show_decision_rationale=behavior_data.get('show_decision_rationale', True),
            include_context_in_responses=behavior_data.get('include_context_in_responses', False),
            enable_user_guidance=behavior_data.get('enable_user_guidance', True),
            enforce_phase_ordering=behavior_data.get('enforce_phase_ordering', True),
            require_test_first_development=behavior_data.get('require_test_first_development', True),
            enable_anti_fabrication_checks=behavior_data.get('enable_anti_fabrication_checks', True),
            allow_methodology_customization=behavior_data.get('allow_methodology_customization', False)
        )
        
        # Create complete configuration
        return HookConfiguration(
            safety_limits=safety_limits,
            behavior_settings=behavior_settings,
            project_root=config_data.get('project_root', ''),
            project_type=config_data.get('project_type', 'python'),
            methodology_variant=config_data.get('methodology_variant', 'standard_tdd'),
            claude_code_integration=config_data.get('claude_code_integration', {}),
            external_tool_configuration=config_data.get('external_tool_configuration', {}),
            log_level=config_data.get('log_level', 'INFO'),
            enable_performance_monitoring=config_data.get('enable_performance_monitoring', True),
            save_decision_logs=config_data.get('save_decision_logs', True),
            environment=config_data.get('environment', 'development'),
            configuration_version=config_data.get('configuration_version', '1.0.0'),
            last_updated=config_data.get('last_updated', '')
        )
    
    def _validate_configuration(self, config: HookConfiguration) -> Dict[str, Any]:
        """Validate hook configuration for consistency and safety"""
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate safety limits
            if config.safety_limits.max_hook_executions_per_session <= 0:
                validation_result['errors'].append("max_hook_executions_per_session must be positive")
            
            if config.safety_limits.max_consecutive_failures <= 0:
                validation_result['errors'].append("max_consecutive_failures must be positive")
            
            if config.safety_limits.max_session_duration_hours <= 0:
                validation_result['errors'].append("max_session_duration_hours must be positive")
            
            # Validate project settings
            if not config.project_root:
                validation_result['errors'].append("project_root cannot be empty")
            
            if config.project_type not in ['python', 'javascript', 'java', 'typescript', 'go', 'rust']:
                validation_result['warnings'].append(f"Unknown project type: {config.project_type}")
            
            # Set validation result
            validation_result['valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize configuration validation rules"""
        
        return {
            'safety_limits': {
                'max_hook_executions_per_session': {'type': int, 'min': 1, 'max': 1000},
                'max_consecutive_failures': {'type': int, 'min': 1, 'max': 20},
                'max_session_duration_hours': {'type': float, 'min': 0.1, 'max': 24.0}
            },
            'behavior_settings': {
                'trigger_mode': {'type': str, 'values': ['automatic', 'manual', 'conditional', 'disabled']},
                'execution_policy': {'type': str, 'values': ['strict', 'permissive', 'development', 'production']}
            }
        }