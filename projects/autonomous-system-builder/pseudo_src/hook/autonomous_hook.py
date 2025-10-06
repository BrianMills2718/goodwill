#!/usr/bin/env python3
"""
AUTONOMOUS HOOK - Hook Integration Layer
Main Claude Code Stop hook implementation for autonomous TDD workflow

RELATES_TO: ../orchestrator/workflow_manager.py, ../config/config_manager.py, ../persistence/state_manager.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

class AutonomousHookError(Exception):
    """Raised when autonomous hook execution fails"""
    pass

class AutonomousStopHook:
    """
    Main Claude Code Stop hook for autonomous TDD workflow execution
    
    HOOK INTEGRATION COMPONENT: Entry point for autonomous operation
    Integrates with Claude Code's hook system to provide autonomous development
    """
    
    def __init__(self):
        """
        Initialize autonomous stop hook
        
        DEFENSIVE PROGRAMMING:
        - Detects project root from current working directory
        - Validates project structure and configuration
        - Initializes minimal logging for hook operations
        - Sets up error handling and recovery mechanisms
        """
        
        # Detect project root from current working directory
        self.project_root = self._detect_project_root()
        
        if not self.project_root:
            raise AutonomousHookError("Cannot detect project root directory")
        
        # Basic logging setup for hook operations
        self._setup_hook_logging()
        
        # Initialize hook state
        self.hook_execution_count = 0
        self.max_hook_executions = 50  # Safety limit
        self.session_start_time = datetime.now(timezone.utc).isoformat()
        
        # Workflow manager will be initialized on first use
        self._workflow_manager = None
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def execute(self) -> Dict[str, Any]:
        """
        Main hook execution entry point called by Claude Code
        
        RETURNS: Hook result dictionary with status and instructions for Claude Code
        
        HOOK EXECUTION FLOW:
        1. Safety checks and initialization
        2. Load or initialize autonomous workflow manager
        3. Execute one autonomous cycle
        4. Handle errors and generate appropriate responses
        5. Return structured result for Claude Code
        """
        
        try:
            self.logger.info(f"Autonomous hook execution started (count: {self.hook_execution_count + 1})")
            
            # Safety check: prevent infinite hook execution
            if self.hook_execution_count >= self.max_hook_executions:
                return self._generate_safety_limit_response()
            
            self.hook_execution_count += 1
            
            # Initialize workflow manager if not already done
            if self._workflow_manager is None:
                self._workflow_manager = self._initialize_workflow_manager()
            
            # Execute one autonomous workflow cycle
            cycle_result = self._workflow_manager.execute_autonomous_hook_cycle()
            
            # Process cycle result and generate hook response
            hook_response = self._process_cycle_result(cycle_result)
            
            # Log hook execution completion
            self.logger.info(f"Autonomous hook execution completed: {hook_response.get('status', 'unknown')}")
            
            return hook_response
            
        except Exception as e:
            # Handle any errors in hook execution
            self.logger.error(f"Autonomous hook execution failed: {str(e)}")
            return self._generate_error_response(e)
    
    def _detect_project_root(self) -> Optional[Path]:
        """
        Detect project root directory from current working directory
        
        RETURNS: Path to project root or None if not found
        
        DETECTION STRATEGY:
        1. Start from current working directory
        2. Look for project indicators (.claude/, .git/, CLAUDE.md)
        3. Walk up directory tree until found or reach filesystem root
        4. Validate detected root has required structure
        """
        
        current_dir = Path.cwd()
        
        # Look for project indicators
        project_indicators = [
            '.claude',
            '.git',
            'CLAUDE.md',
            'src',
            'docs'
        ]
        
        # Walk up directory tree
        for directory in [current_dir] + list(current_dir.parents):
            # Check if this directory has project indicators
            indicator_count = 0
            for indicator in project_indicators:
                if (directory / indicator).exists():
                    indicator_count += 1
            
            # Require at least 2 indicators to confirm project root
            if indicator_count >= 2:
                return directory
        
        # Fallback to current directory if no clear project root found
        return current_dir
    
    def _setup_hook_logging(self):
        """
        Set up minimal logging for hook operations
        
        LOGGING CONFIGURATION:
        1. Create logs directory if needed
        2. Configure file and console logging
        3. Set appropriate log levels
        4. Ensure log rotation for long-running sessions
        """
        
        # Ensure logs directory exists
        logs_dir = self.project_root / 'logs' / 'hooks'
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        log_file = logs_dir / f'autonomous_hook_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also log to console for debugging
            ]
        )
    
    def _initialize_workflow_manager(self) -> 'AutonomousWorkflowManager':
        """
        Initialize autonomous workflow manager with proper error handling
        
        RETURNS: Initialized workflow manager instance
        
        INITIALIZATION PROCESS:
        1. Import workflow manager class
        2. Create instance with project root
        3. Validate initialization succeeded
        4. Handle import or initialization errors gracefully
        """
        
        try:
            # Import workflow manager (delayed import to avoid circular dependencies)
            from ..orchestrator.workflow_manager import AutonomousWorkflowManager
            
            # Create workflow manager instance
            workflow_manager = AutonomousWorkflowManager(str(self.project_root))
            
            self.logger.info("Autonomous workflow manager initialized successfully")
            return workflow_manager
            
        except ImportError as e:
            self.logger.error(f"Failed to import workflow manager: {str(e)}")
            raise AutonomousHookError(f"Workflow manager import failed: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow manager: {str(e)}")
            raise AutonomousHookError(f"Workflow manager initialization failed: {str(e)}")
    
    def _process_cycle_result(self, cycle_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process workflow cycle result and generate appropriate hook response
        
        PARAMETERS:
        - cycle_result: Result from autonomous workflow cycle execution
        
        RETURNS: Hook response dictionary for Claude Code
        
        RESPONSE PROCESSING:
        1. Extract cycle status and decision
        2. Generate appropriate Claude Code instructions
        3. Format response according to hook protocol
        4. Include context and rationale information
        """
        
        # Extract key information from cycle result
        status = cycle_result.get('status', 'unknown')
        message = cycle_result.get('message', 'No message provided')
        next_command = cycle_result.get('next_command')
        blocking_reason = cycle_result.get('blocking_reason')
        escalation_required = cycle_result.get('escalation_required', False)
        user_action_needed = cycle_result.get('user_action_needed')
        
        # Generate hook response based on status
        if status == 'continue':
            return self._generate_continue_response(message, next_command)
        
        elif status == 'block':
            return self._generate_block_response(message, blocking_reason, user_action_needed)
        
        elif status == 'complete':
            return self._generate_completion_response(message)
        
        elif status == 'escalate':
            return self._generate_escalation_response(message, escalation_required, user_action_needed)
        
        else:
            return self._generate_unknown_status_response(status, message)
    
    def _generate_continue_response(self, message: str, next_command: Optional[str]) -> Dict[str, Any]:
        """
        Generate response for continuing autonomous operation
        
        CONTINUE RESPONSE:
        - Allows Claude Code to continue normal operation
        - Provides guidance or next command if available
        - Includes progress information and context
        """
        
        response = {
            'hook_result': 'continue',
            'message': f"🤖 AUTONOMOUS: {message}",
            'autonomous_guidance': True,
            'hook_execution_count': self.hook_execution_count,
            'session_time': datetime.now(timezone.utc).isoformat()
        }
        
        if next_command:
            response['suggested_command'] = next_command
            response['message'] += f" Suggested: {next_command}"
        
        return response
    
    def _generate_block_response(self, message: str, blocking_reason: Optional[str], 
                                user_action_needed: Optional[str]) -> Dict[str, Any]:
        """
        Generate response for blocking Claude Code operation
        
        BLOCK RESPONSE:
        - Prevents Claude Code from proceeding
        - Provides clear explanation of blocking condition
        - Suggests specific user actions if needed
        """
        
        response = {
            'hook_result': 'block',
            'message': f"🛑 BLOCKED: {message}",
            'blocking_reason': blocking_reason or 'Autonomous system requires attention',
            'autonomous_guidance': True,
            'hook_execution_count': self.hook_execution_count,
            'session_time': datetime.now(timezone.utc).isoformat()
        }
        
        if user_action_needed:
            response['user_action_required'] = user_action_needed
            response['message'] += f" Action needed: {user_action_needed}"
        
        return response
    
    def _generate_completion_response(self, message: str) -> Dict[str, Any]:
        """
        Generate response for successful task/project completion
        
        COMPLETION RESPONSE:
        - Indicates successful completion of autonomous objectives
        - Provides completion summary and evidence
        - Allows normal Claude Code operation to resume
        """
        
        return {
            'hook_result': 'continue',
            'message': f"✅ COMPLETED: {message}",
            'completion_detected': True,
            'autonomous_guidance': True,
            'hook_execution_count': self.hook_execution_count,
            'session_time': datetime.now(timezone.utc).isoformat(),
            'success': True
        }
    
    def _generate_escalation_response(self, message: str, escalation_required: bool,
                                     user_action_needed: Optional[str]) -> Dict[str, Any]:
        """
        Generate response for escalating to user intervention
        
        ESCALATION RESPONSE:
        - Blocks Claude Code operation pending user intervention
        - Provides detailed explanation of escalation reason
        - Suggests specific resolution steps
        """
        
        response = {
            'hook_result': 'block',
            'message': f"⚠️ ESCALATION: {message}",
            'escalation_required': escalation_required,
            'autonomous_guidance': True,
            'hook_execution_count': self.hook_execution_count,
            'session_time': datetime.now(timezone.utc).isoformat(),
            'requires_user_intervention': True
        }
        
        if user_action_needed:
            response['recommended_user_action'] = user_action_needed
        
        return response
    
    def _generate_safety_limit_response(self) -> Dict[str, Any]:
        """
        Generate response when safety limits are reached
        
        SAFETY LIMIT RESPONSE:
        - Blocks further autonomous operation
        - Explains safety limit reached
        - Provides instructions for manual override or reset
        """
        
        return {
            'hook_result': 'block',
            'message': f"🚨 SAFETY LIMIT: Maximum hook executions ({self.max_hook_executions}) reached",
            'safety_limit_reached': True,
            'autonomous_guidance': True,
            'hook_execution_count': self.hook_execution_count,
            'session_time': datetime.now(timezone.utc).isoformat(),
            'user_action_required': 'Review autonomous session progress and reset hook counter if needed',
            'manual_override_instructions': 'Edit .claude/hook_state.json to reset execution count'
        }
    
    def _generate_error_response(self, error: Exception) -> Dict[str, Any]:
        """
        Generate response for hook execution errors
        
        ERROR RESPONSE:
        - Blocks Claude Code operation due to error
        - Provides error details for debugging
        - Suggests recovery actions
        """
        
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'hook_execution_count': self.hook_execution_count,
            'project_root': str(self.project_root)
        }
        
        return {
            'hook_result': 'block',
            'message': f"💥 ERROR: Autonomous hook execution failed - {str(error)}",
            'error_details': error_details,
            'autonomous_guidance': True,
            'session_time': datetime.now(timezone.utc).isoformat(),
            'user_action_required': 'Review error logs and resolve autonomous system issues',
            'recovery_suggestions': [
                'Check logs/hooks/ directory for detailed error information',
                'Verify project structure and configuration',
                'Consider resetting autonomous state if needed'
            ]
        }
    
    def _generate_unknown_status_response(self, status: str, message: str) -> Dict[str, Any]:
        """
        Generate response for unknown workflow status
        
        UNKNOWN STATUS RESPONSE:
        - Handles unexpected status values gracefully
        - Provides fallback behavior
        - Logs issue for debugging
        """
        
        self.logger.warning(f"Unknown workflow status: {status}")
        
        return {
            'hook_result': 'continue',
            'message': f"❓ UNKNOWN STATUS: {status} - {message}",
            'unknown_status': status,
            'autonomous_guidance': True,
            'hook_execution_count': self.hook_execution_count,
            'session_time': datetime.now(timezone.utc).isoformat(),
            'warning': 'Autonomous system returned unknown status'
        }


# Hook entry point function for Claude Code
def autonomous_stop_hook() -> Dict[str, Any]:
    """
    Entry point function called by Claude Code Stop hook system
    
    RETURNS: Hook result dictionary for Claude Code consumption
    
    ENTRY POINT REQUIREMENTS:
    1. Function must be named according to Claude Code hook conventions
    2. Must return dictionary with appropriate hook result structure
    3. Must handle all errors gracefully without crashing Claude Code
    4. Should be stateless - all state managed through external files
    """
    
    try:
        # Create and execute autonomous hook
        hook = AutonomousStopHook()
        return hook.execute()
        
    except Exception as e:
        # Ultimate fallback - never crash Claude Code
        return {
            'hook_result': 'block',
            'message': f"💥 CRITICAL ERROR: Autonomous hook crashed - {str(e)}",
            'critical_error': True,
            'error_type': type(e).__name__,
            'user_action_required': 'Fix autonomous hook system before continuing',
            'fallback_response': True
        }


# Additional hook utilities and helper functions
class HookStateManager:
    """
    Manages persistent state for hook execution across sessions
    
    HOOK STATE MANAGEMENT:
    - Tracks hook execution counts and limits
    - Manages session state and recovery
    - Provides state reset and recovery mechanisms
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_file = project_root / '.claude' / 'hook_state.json'
        
    def load_hook_state(self) -> Dict[str, Any]:
        """Load hook execution state from disk"""
        
        if not self.state_file.exists():
            return self._get_default_hook_state()
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception:
            return self._get_default_hook_state()
    
    def save_hook_state(self, state: Dict[str, Any]) -> bool:
        """Save hook execution state to disk"""
        
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False
    
    def _get_default_hook_state(self) -> Dict[str, Any]:
        """Get default hook state for new sessions"""
        
        return {
            'execution_count': 0,
            'session_start_time': datetime.now(timezone.utc).isoformat(),
            'last_execution_time': None,
            'max_executions': 50,
            'safety_overrides': {},
            'error_history': []
        }


# Hook configuration and setup utilities
def setup_autonomous_hook(project_root: str) -> bool:
    """
    Set up autonomous hook in Claude Code project
    
    PARAMETERS:
    - project_root: Project root directory path
    
    RETURNS: True if setup successful, False otherwise
    
    SETUP PROCESS:
    1. Create .claude/hooks/ directory
    2. Install autonomous_stop.py hook file
    3. Configure hook settings
    4. Initialize hook state
    """
    
    try:
        project_path = Path(project_root)
        
        # Create hooks directory
        hooks_dir = project_path / '.claude' / 'hooks'
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy this file to hooks directory
        hook_file = hooks_dir / 'autonomous_stop.py'
        
        # In real implementation, would copy the file content
        # For pseudocode, we'll just indicate the setup
        hook_content = f'''# Autonomous Stop Hook
# Generated by autonomous TDD system
# Project: {project_root}

from {__name__} import autonomous_stop_hook

def execute():
    return autonomous_stop_hook()
'''
        
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        # Initialize hook state
        state_manager = HookStateManager(project_path)
        state_manager.save_hook_state(state_manager._get_default_hook_state())
        
        return True
        
    except Exception:
        return False