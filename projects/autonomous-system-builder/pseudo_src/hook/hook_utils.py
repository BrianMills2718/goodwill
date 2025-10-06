#!/usr/bin/env python3
"""
HOOK UTILS - Hook Integration Layer
Utility functions for autonomous hook operations

RELATES_TO: autonomous_hook.py, hook_config.py, ../utils/json_utils.py
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass
class HookExecutionContext:
    """Context information for hook execution"""
    project_root: str
    execution_count: int
    session_start_time: str
    last_execution_time: Optional[str]
    user_working_directory: str
    claude_code_version: Optional[str] = None
    environment_variables: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_root': self.project_root,
            'execution_count': self.execution_count,
            'session_start_time': self.session_start_time,
            'last_execution_time': self.last_execution_time,
            'user_working_directory': self.user_working_directory,
            'claude_code_version': self.claude_code_version,
            'environment_variables': self.environment_variables or {}
        }

class HookUtilsError(Exception):
    """Raised when hook utility operations fail"""
    pass

class AutonomousHookUtils:
    """
    Utility functions for autonomous hook operations
    
    HOOK INTEGRATION COMPONENT: Common utilities for hook system
    Provides reusable functions for hook execution, monitoring, and recovery
    """
    
    @staticmethod
    def detect_claude_code_environment() -> Dict[str, Any]:
        """
        Detect Claude Code environment and capabilities
        
        RETURNS: Dictionary with environment information
        
        ENVIRONMENT DETECTION:
        1. Check if running within Claude Code session
        2. Detect available tools and capabilities  
        3. Identify Claude Code version and configuration
        4. Check for MCP server integrations
        """
        
        environment_info = {
            'is_claude_code': False,
            'claude_code_version': None,
            'available_tools': [],
            'mcp_servers': [],
            'working_directory': str(Path.cwd()),
            'python_version': sys.version,
            'environment_variables': {}
        }
        
        try:
            # Check for Claude Code environment indicators
            claude_code_indicators = [
                'CLAUDE_CODE_SESSION',
                'CLAUDE_CODE_VERSION', 
                'CLAUDE_WORKSPACE_ROOT'
            ]
            
            for indicator in claude_code_indicators:
                if indicator in os.environ:
                    environment_info['is_claude_code'] = True
                    environment_info['environment_variables'][indicator] = os.environ[indicator]
            
            # Extract Claude Code version if available
            if 'CLAUDE_CODE_VERSION' in os.environ:
                environment_info['claude_code_version'] = os.environ['CLAUDE_CODE_VERSION']
            
            # Detect available tools (would check for specific tool availability)
            available_tools = []
            
            # Check for common tools
            tool_checks = {
                'git': 'git --version',
                'python': 'python --version',
                'pytest': 'pytest --version',
                'npm': 'npm --version',
                'node': 'node --version'
            }
            
            for tool_name, check_command in tool_checks.items():
                try:
                    result = subprocess.run(
                        check_command.split(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        available_tools.append(tool_name)
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    pass
            
            environment_info['available_tools'] = available_tools
            
            # Detect MCP servers (would check for MCP configuration)
            mcp_servers = []
            mcp_config_paths = [
                Path.home() / '.claude' / 'mcp_servers.json',
                Path.cwd() / '.claude' / 'mcp_servers.json'
            ]
            
            for config_path in mcp_config_paths:
                if config_path.exists():
                    try:
                        with open(config_path, 'r') as f:
                            mcp_config = json.load(f)
                            mcp_servers.extend(mcp_config.get('servers', []))
                    except Exception:
                        pass
            
            environment_info['mcp_servers'] = mcp_servers
            
        except Exception as e:
            environment_info['detection_error'] = str(e)
        
        return environment_info
    
    @staticmethod
    def create_hook_execution_context(project_root: str) -> HookExecutionContext:
        """
        Create execution context for current hook invocation
        
        PARAMETERS:
        - project_root: Project root directory path
        
        RETURNS: Hook execution context object
        """
        
        try:
            # Load existing execution state
            state_file = Path(project_root) / '.claude' / 'hook_state.json'
            
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
            else:
                state_data = {}
            
            # Get environment information
            env_info = AutonomousHookUtils.detect_claude_code_environment()
            
            # Create context
            context = HookExecutionContext(
                project_root=project_root,
                execution_count=state_data.get('execution_count', 0) + 1,
                session_start_time=state_data.get('session_start_time', datetime.now(timezone.utc).isoformat()),
                last_execution_time=state_data.get('last_execution_time'),
                user_working_directory=env_info['working_directory'],
                claude_code_version=env_info.get('claude_code_version'),
                environment_variables=env_info.get('environment_variables', {})
            )
            
            return context
            
        except Exception as e:
            # Return minimal context on error
            return HookExecutionContext(
                project_root=project_root,
                execution_count=1,
                session_start_time=datetime.now(timezone.utc).isoformat(),
                last_execution_time=None,
                user_working_directory=str(Path.cwd())
            )
    
    @staticmethod
    def save_hook_execution_state(context: HookExecutionContext, 
                                 hook_result: Dict[str, Any]) -> bool:
        """
        Save hook execution state for persistence across sessions
        
        PARAMETERS:
        - context: Hook execution context
        - hook_result: Result from hook execution
        
        RETURNS: True if save successful, False otherwise
        """
        
        try:
            state_file = Path(context.project_root) / '.claude' / 'hook_state.json'
            
            # Update state data
            state_data = {
                'execution_count': context.execution_count,
                'session_start_time': context.session_start_time,
                'last_execution_time': datetime.now(timezone.utc).isoformat(),
                'last_hook_result': hook_result,
                'context': context.to_dict(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Ensure directory exists
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save state
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def check_hook_safety_limits(context: HookExecutionContext, 
                                config: 'HookConfiguration') -> Tuple[bool, List[str]]:
        """
        Check if hook execution should be allowed based on safety limits
        
        PARAMETERS:
        - context: Current hook execution context
        - config: Hook configuration with safety limits
        
        RETURNS: (is_safe, violation_reasons)
        
        SAFETY CHECKS:
        1. Maximum executions per session limit
        2. Session duration limit
        3. Consecutive failure limit
        4. Rate limiting for LLM queries
        """
        
        violations = []
        
        try:
            # Check execution count limit
            if context.execution_count > config.safety_limits.max_hook_executions_per_session:
                violations.append(f"Exceeded max executions: {context.execution_count} > {config.safety_limits.max_hook_executions_per_session}")
            
            # Check session duration limit
            if context.session_start_time:
                session_start = datetime.fromisoformat(context.session_start_time.replace('Z', '+00:00'))
                session_duration = (datetime.now(timezone.utc) - session_start).total_seconds() / 3600
                
                if session_duration > config.safety_limits.max_session_duration_hours:
                    violations.append(f"Exceeded max session duration: {session_duration:.2f}h > {config.safety_limits.max_session_duration_hours}h")
            
            # Check consecutive failures (would need failure tracking)
            failure_count = AutonomousHookUtils._get_consecutive_failure_count(context.project_root)
            if failure_count > config.safety_limits.max_consecutive_failures:
                violations.append(f"Exceeded max consecutive failures: {failure_count} > {config.safety_limits.max_consecutive_failures}")
            
            # Check rate limiting (would need query tracking)
            query_rate = AutonomousHookUtils._get_recent_query_rate(context.project_root)
            if query_rate > config.safety_limits.max_llm_queries_per_hour:
                violations.append(f"Exceeded LLM query rate limit: {query_rate} > {config.safety_limits.max_llm_queries_per_hour}")
            
        except Exception as e:
            violations.append(f"Safety check error: {str(e)}")
        
        is_safe = len(violations) == 0
        return is_safe, violations
    
    @staticmethod
    def format_hook_response_for_claude_code(status: str, message: str, 
                                           additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format hook response according to Claude Code hook protocol
        
        PARAMETERS:
        - status: Hook result status (continue, block, error)
        - message: Message to display to user
        - additional_data: Additional data to include in response
        
        RETURNS: Properly formatted hook response dictionary
        """
        
        response = {
            'hook_result': status,
            'message': message,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'autonomous_hook': True
        }
        
        # Add additional data if provided
        if additional_data:
            response.update(additional_data)
        
        # Ensure required fields are present
        if 'hook_result' not in response:
            response['hook_result'] = 'continue'
        
        # Validate response structure
        valid_statuses = ['continue', 'block', 'error']
        if response['hook_result'] not in valid_statuses:
            response['hook_result'] = 'continue'
            response['warning'] = f"Invalid hook status corrected to 'continue'"
        
        return response
    
    @staticmethod
    def create_hook_performance_monitor() -> 'HookPerformanceMonitor':
        """
        Create performance monitor for hook execution tracking
        
        RETURNS: Performance monitor instance
        """
        
        return HookPerformanceMonitor()
    
    @staticmethod
    def validate_project_structure_for_hooks(project_root: str) -> Dict[str, Any]:
        """
        Validate project structure is suitable for autonomous hook operation
        
        PARAMETERS:
        - project_root: Project root directory path
        
        RETURNS: Validation result with status and recommendations
        
        VALIDATION CHECKS:
        1. Required directories exist (.claude/, src/, tests/)
        2. Configuration files are present and valid
        3. Project type is supported
        4. External dependencies are available
        """
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            project_path = Path(project_root)
            
            # Check required directories
            required_dirs = ['.claude', 'src', 'docs']
            for dir_name in required_dirs:
                dir_path = project_path / dir_name
                if not dir_path.exists():
                    validation_result['errors'].append(f"Missing required directory: {dir_name}/")
            
            # Check for project configuration
            config_files = ['CLAUDE.md', '.claude/hook_config.json']
            missing_configs = []
            for config_file in config_files:
                if not (project_path / config_file).exists():
                    missing_configs.append(config_file)
            
            if missing_configs:
                validation_result['warnings'].append(f"Missing configuration files: {missing_configs}")
                validation_result['recommendations'].append("Initialize autonomous hook configuration")
            
            # Check project type detection
            project_type = AutonomousHookUtils._detect_project_type(project_path)
            if project_type == 'unknown':
                validation_result['warnings'].append("Could not detect project type")
                validation_result['recommendations'].append("Specify project type in hook configuration")
            
            # Check for version control
            if not (project_path / '.git').exists():
                validation_result['warnings'].append("No git repository detected")
                validation_result['recommendations'].append("Initialize git repository for better change tracking")
            
            # Set overall validation status
            validation_result['valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_result
    
    @staticmethod
    def setup_hook_logging(project_root: str, log_level: str = "INFO") -> bool:
        """
        Set up logging configuration for hook operations
        
        PARAMETERS:
        - project_root: Project root directory path
        - log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
        RETURNS: True if setup successful, False otherwise
        """
        
        try:
            # Create logs directory structure
            logs_dir = Path(project_root) / 'logs'
            hook_logs_dir = logs_dir / 'hooks'
            hook_logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Configure logging
            log_file = hook_logs_dir / f'autonomous_hook_{datetime.now().strftime("%Y%m%d")}.log'
            
            # Set up logger
            logger = logging.getLogger('autonomous_hook')
            logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            
            # Clear existing handlers
            logger.handlers.clear()
            
            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            
            # Console handler for debugging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            logger.info("Hook logging configured successfully")
            return True
            
        except Exception as e:
            print(f"Failed to setup hook logging: {str(e)}")
            return False
    
    @staticmethod
    def _get_consecutive_failure_count(project_root: str) -> int:
        """Get count of consecutive hook execution failures"""
        
        try:
            failure_file = Path(project_root) / '.claude' / 'failure_count.json'
            
            if failure_file.exists():
                with open(failure_file, 'r') as f:
                    failure_data = json.load(f)
                    return failure_data.get('consecutive_failures', 0)
            
            return 0
            
        except Exception:
            return 0
    
    @staticmethod
    def _get_recent_query_rate(project_root: str) -> int:
        """Get recent LLM query rate per hour"""
        
        try:
            # Would implement query rate tracking
            # For pseudocode, return conservative estimate
            return 10
            
        except Exception:
            return 0
    
    @staticmethod
    def _detect_project_type(project_path: Path) -> str:
        """Detect project type from file structure and configuration"""
        
        # Check for Python project indicators
        python_indicators = [
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            'Pipfile',
            '__pycache__'
        ]
        
        for indicator in python_indicators:
            if (project_path / indicator).exists():
                return 'python'
        
        # Check for JavaScript/Node.js project indicators
        js_indicators = [
            'package.json',
            'node_modules',
            'yarn.lock',
            'npm-shrinkwrap.json'
        ]
        
        for indicator in js_indicators:
            if (project_path / indicator).exists():
                return 'javascript'
        
        # Check for other project types
        if (project_path / 'Cargo.toml').exists():
            return 'rust'
        
        if (project_path / 'go.mod').exists():
            return 'go'
        
        if (project_path / 'pom.xml').exists() or (project_path / 'build.gradle').exists():
            return 'java'
        
        return 'unknown'


class HookPerformanceMonitor:
    """
    Performance monitoring for hook execution
    
    HOOK UTILITY: Tracks performance metrics and identifies bottlenecks
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.checkpoints = []
        self.metrics = {}
    
    def checkpoint(self, name: str):
        """Record a performance checkpoint"""
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        self.checkpoints.append({
            'name': name,
            'elapsed_time': elapsed,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    def record_metric(self, name: str, value: Any):
        """Record a performance metric"""
        
        self.metrics[name] = value
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for this execution"""
        
        total_time = time.time() - self.start_time
        
        return {
            'total_execution_time': total_time,
            'checkpoints': self.checkpoints,
            'metrics': self.metrics,
            'performance_score': self._calculate_performance_score(total_time)
        }
    
    def _calculate_performance_score(self, total_time: float) -> str:
        """Calculate performance score based on execution time"""
        
        if total_time < 1.0:
            return 'excellent'
        elif total_time < 5.0:
            return 'good'
        elif total_time < 15.0:
            return 'acceptable'
        else:
            return 'poor'


class HookErrorRecovery:
    """
    Error recovery utilities for hook execution
    
    HOOK UTILITY: Provides error recovery and fallback mechanisms
    """
    
    @staticmethod
    def create_error_recovery_plan(error: Exception, context: HookExecutionContext) -> Dict[str, Any]:
        """
        Create recovery plan for hook execution error
        
        PARAMETERS:
        - error: Exception that occurred during hook execution
        - context: Hook execution context
        
        RETURNS: Recovery plan with suggested actions
        """
        
        error_type = type(error).__name__
        error_message = str(error)
        
        recovery_plan = {
            'error_type': error_type,
            'error_message': error_message,
            'recovery_actions': [],
            'user_action_required': False,
            'automatic_retry': False,
            'fallback_mode': False
        }
        
        # Define recovery strategies based on error type
        if isinstance(error, FileNotFoundError):
            recovery_plan['recovery_actions'].extend([
                'Check project structure and required files',
                'Verify file paths in configuration',
                'Initialize missing project structure if needed'
            ])
            recovery_plan['automatic_retry'] = True
        
        elif isinstance(error, PermissionError):
            recovery_plan['recovery_actions'].extend([
                'Check file and directory permissions',
                'Verify user has write access to project directory',
                'Consider running with appropriate permissions'
            ])
            recovery_plan['user_action_required'] = True
        
        elif isinstance(error, ImportError):
            recovery_plan['recovery_actions'].extend([
                'Check Python dependencies are installed',
                'Verify PYTHONPATH includes required modules',
                'Install missing dependencies'
            ])
            recovery_plan['user_action_required'] = True
        
        elif 'timeout' in error_message.lower():
            recovery_plan['recovery_actions'].extend([
                'Increase timeout limits in configuration',
                'Check for performance issues',
                'Consider breaking down large operations'
            ])
            recovery_plan['automatic_retry'] = True
        
        else:
            recovery_plan['recovery_actions'].extend([
                'Review error logs for detailed information',
                'Check hook configuration and project setup',
                'Consider resetting hook state if needed'
            ])
            recovery_plan['fallback_mode'] = True
        
        return recovery_plan
    
    @staticmethod
    def attempt_error_recovery(recovery_plan: Dict[str, Any], 
                              context: HookExecutionContext) -> bool:
        """
        Attempt automatic error recovery based on recovery plan
        
        PARAMETERS:
        - recovery_plan: Recovery plan from create_error_recovery_plan
        - context: Hook execution context
        
        RETURNS: True if recovery successful, False otherwise
        """
        
        try:
            if recovery_plan.get('automatic_retry', False):
                # Wait briefly before retry
                time.sleep(1)
                return True
            
            if recovery_plan.get('fallback_mode', False):
                # Enable fallback mode in hook state
                return HookErrorRecovery._enable_fallback_mode(context)
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def _enable_fallback_mode(context: HookExecutionContext) -> bool:
        """Enable fallback mode for hook execution"""
        
        try:
            fallback_file = Path(context.project_root) / '.claude' / 'fallback_mode.json'
            
            fallback_data = {
                'enabled': True,
                'enabled_at': datetime.now(timezone.utc).isoformat(),
                'reason': 'Error recovery fallback',
                'context': context.to_dict()
            }
            
            fallback_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(fallback_file, 'w') as f:
                json.dump(fallback_data, f, indent=2)
            
            return True
            
        except Exception:
            return False