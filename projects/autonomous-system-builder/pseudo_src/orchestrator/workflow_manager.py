#!/usr/bin/env python3
"""
WORKFLOW MANAGER - Orchestrator Layer
Main autonomous workflow coordination and state machine implementation

RELATES_TO: ../persistence/state_manager.py, ../analysis/decision_engine.py, ../context/cross_reference_manager.py
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

class WorkflowError(Exception):
    """Raised when workflow operations fail"""
    pass

class HookResultStatus(Enum):
    """Status values for hook execution results"""
    CONTINUE = "continue"
    BLOCK = "block"
    COMPLETE = "complete"
    ERROR = "error"
    ESCALATE = "escalate"

@dataclass
class HookResult:
    """Result of autonomous hook execution"""
    status: HookResultStatus
    message: str
    next_command: Optional[str] = None
    blocking_reason: Optional[str] = None
    escalation_required: bool = False
    user_action_needed: Optional[str] = None
    evidence_generated: Dict[str, Any] = None
    context_used: Dict[str, Any] = None
    decision_rationale: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'status': self.status.value,
            'message': self.message,
            'next_command': self.next_command,
            'blocking_reason': self.blocking_reason,
            'escalation_required': self.escalation_required,
            'user_action_needed': self.user_action_needed,
            'evidence_generated': self.evidence_generated or {},
            'context_used': self.context_used or {},
            'decision_rationale': self.decision_rationale
        }
        return result

class AutonomousWorkflowManager:
    """
    Main autonomous workflow coordinator - implements the core state machine
    
    ORCHESTRATOR COMPONENT: Coordinates all foundation components
    Provides the main autonomous hook execution logic
    """
    
    def __init__(self, project_root: str):
        """
        Initialize autonomous workflow manager
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes all required foundation components
        - Sets up safety mechanisms and loop detection
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise WorkflowError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise WorkflowError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise WorkflowError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Workflow state and safety mechanisms
        self.current_iteration = 0
        self.max_iterations = 50  # Safety limit from configuration
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.session_start_time = datetime.now(timezone.utc)
        
        # Hook execution state
        self.last_hook_result = None
        self.execution_history = []
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def execute_autonomous_hook_cycle(self) -> Dict[str, Any]:
        """
        Main entry point for autonomous hook execution
        
        Called by Claude Code Stop hook to execute one autonomous cycle
        
        RETURNS: Hook result dictionary for Claude Code
        
        SAFETY FEATURES:
        - Iteration limit enforcement
        - Consecutive failure tracking
        - Exception handling and recovery
        - State consistency validation
        """
        
        try:
            # Safety check: prevent infinite loops
            if self.current_iteration >= self.max_iterations:
                return self._handle_safety_limit_reached().to_dict()
            
            # Safety check: consecutive failure limit
            if self.consecutive_failures >= self.max_consecutive_failures:
                return self._handle_excessive_failures().to_dict()
            
            self.current_iteration += 1
            
            # Log hook execution start
            self.logger.info(f"Starting autonomous hook cycle {self.current_iteration}")
            
            # Load complete system state
            system_state = self.state_manager.load_complete_state()
            
            # Validate state consistency
            if not self.state_manager._validate_state_consistency(system_state):
                return self._handle_state_corruption(system_state).to_dict()
            
            # Determine current state and next action
            next_action = self._analyze_current_state_and_decide_action(system_state)
            
            # Execute the determined action
            action_result = self._execute_action(next_action, system_state)
            
            # Update system state based on action results
            updated_state = self._update_state_after_action(system_state, action_result)
            
            # Save updated state
            save_success = self.state_manager.save_complete_state(updated_state)
            if not save_success:
                return self._handle_state_save_failure().to_dict()
            
            # Generate evidence for this hook cycle
            evidence = self._collect_evidence_for_hook_cycle(action_result)
            if evidence:
                self.state_manager.save_evidence_record(evidence)
            
            # Update execution history
            self._update_execution_history(action_result)
            
            # Reset consecutive failures on success
            self.consecutive_failures = 0
            
            # Log successful completion
            self.logger.info(f"Hook cycle {self.current_iteration} completed successfully")
            
            # Return result to Claude Code
            hook_result = self._format_hook_result(action_result, updated_state)
            self.last_hook_result = hook_result
            
            return hook_result.to_dict()
            
        except Exception as e:
            # Handle any errors in autonomous execution
            self.consecutive_failures += 1
            error_result = self._handle_autonomous_error(e, system_state if 'system_state' in locals() else None)
            self.last_hook_result = error_result
            
            return error_result.to_dict()
    
    def _analyze_current_state_and_decide_action(self, system_state) -> Dict[str, Any]:
        """
        Core state machine logic - analyze current state and decide next action
        
        PARAMETERS:
        - system_state: Complete system state from StateManager
        
        RETURNS: Action decision with type, target, and rationale
        
        DECISION PROCESS:
        1. Check for blocking conditions
        2. Determine current methodology phase and step
        3. Apply phase-specific decision logic
        4. Consider available tasks and dependencies
        5. Factor in error history and failure patterns
        """
        
        # Check for blocking conditions first
        if system_state.project_state.blocking_status.get("is_blocked", False):
            return self._handle_blocked_state(system_state)
        
        # Determine current methodology phase and step
        current_phase = system_state.project_state.current_phase
        methodology_step = system_state.project_state.methodology_step
        
        self.logger.info(f"Analyzing state: Phase {current_phase}, Step {methodology_step}")
        
        # Phase-specific decision logic
        if current_phase == ProjectPhase.OVERVIEW:
            return self._handle_overview_phase(system_state)
        elif current_phase == ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH:
            return self._handle_architecture_phase(system_state)
        elif current_phase == ProjectPhase.FILE_STRUCTURE_CREATION:
            return self._handle_file_structure_phase(system_state)
        elif current_phase == ProjectPhase.PSEUDOCODE_DOCUMENTATION:
            return self._handle_pseudocode_phase(system_state)
        elif current_phase == ProjectPhase.IMPLEMENTATION_PLANS_UNIT_TESTS:
            return self._handle_implementation_planning_phase(system_state)
        elif current_phase == ProjectPhase.INTEGRATION_TESTS:
            return self._handle_integration_testing_phase(system_state)
        elif current_phase == ProjectPhase.ACCEPTANCE_TESTS:
            return self._handle_acceptance_testing_phase(system_state)
        elif current_phase == ProjectPhase.CREATE_FILES_CROSS_REFERENCES:
            return self._handle_file_creation_phase(system_state)
        elif current_phase == ProjectPhase.IMPLEMENTATION:
            return self._handle_implementation_phase(system_state)
        elif current_phase == ProjectPhase.PROJECT_COMPLETE:
            return self._handle_completion_phase(system_state)
        else:
            return self._handle_unknown_phase(system_state)
    
    def _handle_implementation_phase(self, system_state) -> Dict[str, Any]:
        """
        Handle autonomous implementation execution (Phase 9)
        
        IMPLEMENTATION STRATEGY:
        1. Find next ready task to execute
        2. Load context for the selected task
        3. Validate dependencies and prerequisites
        4. Generate implementation instruction for Claude Code
        5. Track task progress and evidence collection
        """
        
        task_graph = system_state.task_graph
        
        # Find next ready task to execute
        ready_tasks = self._get_ready_tasks(task_graph)
        
        if not ready_tasks:
            # No ready tasks - check if we're complete or blocked
            if self._all_tasks_complete(task_graph):
                return {
                    'action_type': 'advance_phase',
                    'target': 'project_complete',
                    'reasoning': 'All implementation tasks completed successfully',
                    'confidence': 'high'
                }
            else:
                # Tasks exist but none are ready - analyze blocking
                return self._analyze_task_blocking(task_graph, system_state)
        
        # Select highest priority ready task
        selected_task = self._select_highest_priority_task(ready_tasks)
        
        self.logger.info(f"Selected task for implementation: {selected_task.id} - {selected_task.title}")
        
        # Load context for the selected task
        context_bundle = self._load_task_context(selected_task, system_state)
        
        # Check if task requires external dependencies
        if selected_task.evidence_requirements.get('external_validation', False):
            dependency_status = self._validate_task_dependencies(selected_task, system_state.dependencies)
            if not dependency_status.get('all_available', True):
                return self._handle_missing_dependencies(selected_task, dependency_status)
        
        # Generate implementation instruction for Claude Code
        implementation_instruction = self._generate_implementation_instruction(
            selected_task, 
            context_bundle, 
            system_state
        )
        
        return {
            'action_type': 'implement_task',
            'target_task_id': selected_task.id,
            'instruction': implementation_instruction,
            'context_bundle': context_bundle,
            'reasoning': f'Implementing task: {selected_task.title}',
            'confidence': 'high',
            'estimated_effort': selected_task.estimated_complexity
        }
    
    def _handle_architecture_phase(self, system_state) -> Dict[str, Any]:
        """
        Handle architecture and dependency research (Phase 2)
        
        ARCHITECTURE WORKFLOW:
        1. Assess architecture completeness
        2. Identify missing dependency research
        3. Define integration test requirements
        4. Complete system architecture documentation
        5. Validate readiness for next phase
        """
        
        # Check what architecture work is complete
        architecture_status = self._assess_architecture_completeness(system_state)
        
        if not architecture_status.get('dependency_research_complete', False):
            # Need to research external dependencies
            return self._generate_dependency_research_action(system_state)
        
        elif not architecture_status.get('integration_tests_defined', False):
            # Need to define integration tests
            return self._generate_integration_test_definition_action(system_state)
        
        elif not architecture_status.get('system_architecture_complete', False):
            # Need to complete system architecture documentation
            return self._generate_architecture_documentation_action(system_state)
        
        else:
            # Architecture phase complete - advance to file structure
            return {
                'action_type': 'advance_phase',
                'target': 'file_structure_phase',
                'reasoning': 'Architecture and dependency research complete',
                'confidence': 'high'
            }
    
    def _handle_file_creation_phase(self, system_state) -> Dict[str, Any]:
        """
        Handle creating all files and cross-references (Phase 8)
        
        FILE CREATION WORKFLOW:
        1. Check if file structure already exists
        2. Generate complete file structure from task graph
        3. Create all directories and files with headers
        4. Establish cross-reference links
        5. Validate file structure completeness
        """
        
        # Check if file structure already created
        if self._file_structure_exists(system_state):
            return {
                'action_type': 'advance_phase',
                'target': 'implementation_phase',
                'reasoning': 'File structure already exists, advancing to implementation',
                'confidence': 'high'
            }
        
        # Generate complete file structure from task graph
        file_creation_plan = self._generate_file_creation_plan(system_state.task_graph)
        
        # Create all directories
        directory_creation = self._create_directory_structure(file_creation_plan)
        
        # Create all files with headers and cross-references
        file_creation = self._create_files_with_cross_references(file_creation_plan, system_state)
        
        # Update cross-reference map
        updated_cross_refs = self._update_cross_reference_map(system_state.cross_references, file_creation_plan)
        
        return {
            'action_type': 'create_files',
            'file_creation_plan': file_creation_plan,
            'reasoning': 'Creating complete file structure and cross-references',
            'confidence': 'high',
            'files_to_create': len(file_creation_plan.get('files', []))
        }
    
    def _execute_action(self, action_decision: Dict[str, Any], system_state) -> Dict[str, Any]:
        """
        Execute the decided action and return results
        
        PARAMETERS:
        - action_decision: Decision from analysis phase
        - system_state: Current system state
        
        RETURNS: Action execution results with evidence and updates
        
        ACTION TYPES:
        - implement_task: Execute specific task implementation
        - advance_phase: Progress to next methodology phase
        - research_dependencies: Investigate external dependencies
        - create_files: Generate file structure
        - analyze_errors: Investigate and resolve errors
        """
        
        action_type = action_decision.get('action_type')
        
        self.logger.info(f"Executing action: {action_type}")
        
        try:
            if action_type == 'implement_task':
                return self._execute_task_implementation(action_decision, system_state)
            
            elif action_type == 'advance_phase':
                return self._execute_phase_advancement(action_decision, system_state)
            
            elif action_type == 'research_dependencies':
                return self._execute_dependency_research(action_decision, system_state)
            
            elif action_type == 'create_files':
                return self._execute_file_creation(action_decision, system_state)
            
            elif action_type == 'analyze_errors':
                return self._execute_error_analysis(action_decision, system_state)
            
            elif action_type == 'escalate':
                return self._execute_escalation(action_decision, system_state)
            
            else:
                return self._execute_unknown_action(action_decision, system_state)
        
        except Exception as e:
            return {
                'execution_status': 'failed',
                'error': str(e),
                'action_type': action_type,
                'recovery_needed': True
            }
    
    def _execute_task_implementation(self, action_decision: Dict[str, Any], system_state) -> Dict[str, Any]:
        """
        Execute specific task implementation
        
        TASK IMPLEMENTATION PROCESS:
        1. Prepare implementation context
        2. Generate Claude Code instructions
        3. Monitor implementation progress
        4. Collect evidence of completion
        5. Update task status and dependencies
        """
        
        task_id = action_decision.get('target_task_id')
        instruction = action_decision.get('instruction')
        context_bundle = action_decision.get('context_bundle')
        
        # Prepare implementation environment
        implementation_env = {
            'task_id': task_id,
            'instruction': instruction,
            'context_files': context_bundle.get('files', []),
            'estimated_tokens': context_bundle.get('estimated_tokens', 0),
            'safety_checks': {
                'max_file_modifications': self.config_manager.get_config_value('safety_mechanisms.max_file_modifications_per_session', 100),
                'backup_before_modifications': self.config_manager.get_config_value('safety_mechanisms.backup_before_modifications', True)
            }
        }
        
        # Execute implementation (in real system, this would trigger Claude Code actions)
        execution_result = {
            'execution_status': 'completed',
            'task_id': task_id,
            'files_modified': [],  # Would be populated by actual implementation
            'tests_run': False,    # Would be updated based on actual test execution
            'evidence_collected': {},
            'implementation_time': time.time()
        }
        
        # Collect evidence of task completion
        evidence = self._collect_task_evidence(task_id, execution_result)
        
        return {
            'action_result': execution_result,
            'evidence_generated': evidence,
            'task_status_update': {
                'task_id': task_id,
                'new_status': 'completed' if execution_result['execution_status'] == 'completed' else 'in_progress'
            }
        }
    
    def _update_state_after_action(self, system_state, action_result: Dict[str, Any]):
        """
        Update system state based on action execution results
        
        STATE UPDATES:
        1. Update project state metadata
        2. Update task graph with new statuses
        3. Update evidence records
        4. Update cross-references if files were created
        5. Update blocking status if resolved
        """
        
        # Create copy of state for modification
        updated_state = system_state
        
        # Update project state metadata
        updated_state.project_state.last_update_time = datetime.now(timezone.utc).isoformat()
        updated_state.project_state.total_hook_iterations = self.current_iteration
        
        # Update task status if task was executed
        task_status_update = action_result.get('task_status_update')
        if task_status_update:
            task_id = task_status_update['task_id']
            new_status = task_status_update['new_status']
            
            if task_id in updated_state.task_graph.nodes:
                updated_state.task_graph.nodes[task_id].status = new_status
                updated_state.task_graph.nodes[task_id].last_updated = datetime.now(timezone.utc).isoformat()
                
                # If task completed, update completion time
                if new_status == 'completed':
                    updated_state.task_graph.nodes[task_id].completion_time = datetime.now(timezone.utc).isoformat()
                    
                    # Add to completed tasks
                    if task_id in updated_state.project_state.current_tasks:
                        updated_state.project_state.current_tasks.remove(task_id)
                    if task_id not in updated_state.project_state.completed_tasks:
                        updated_state.project_state.completed_tasks.append(task_id)
        
        # Update ready tasks list
        updated_state.task_graph.current_ready_tasks = self._calculate_ready_tasks(updated_state.task_graph)
        
        # Add evidence record if generated
        evidence = action_result.get('evidence_generated')
        if evidence:
            updated_state.evidence_records.append(evidence)
        
        # Update phase completion percentage
        completion_percentage = self._calculate_phase_completion(updated_state)
        updated_state.project_state.phase_completion_percentage = completion_percentage
        
        # Calculate new state hash
        updated_state.state_hash = self.state_manager._calculate_state_hash(updated_state)
        
        return updated_state
    
    def _format_hook_result(self, action_result: Dict[str, Any], updated_state) -> HookResult:
        """
        Format hook execution result for Claude Code
        
        HOOK RESULT FORMATTING:
        1. Determine hook status (continue/block/complete)
        2. Generate appropriate message for Claude Code
        3. Include next command if applicable
        4. Add context and rationale information
        """
        
        execution_status = action_result.get('action_result', {}).get('execution_status', 'unknown')
        
        if execution_status == 'completed':
            return HookResult(
                status=HookResultStatus.CONTINUE,
                message=f"Task completed successfully. Iteration {self.current_iteration}.",
                decision_rationale=f"Completed task implementation with evidence collection",
                evidence_generated=action_result.get('evidence_generated', {}),
                context_used={'iteration': self.current_iteration, 'phase': updated_state.project_state.current_phase}
            )
        
        elif execution_status == 'failed':
            return HookResult(
                status=HookResultStatus.BLOCK,
                message=f"Task execution failed. Iteration {self.current_iteration}.",
                blocking_reason=action_result.get('action_result', {}).get('error', 'Unknown error'),
                decision_rationale="Task execution encountered errors requiring attention",
                escalation_required=True
            )
        
        elif execution_status == 'in_progress':
            return HookResult(
                status=HookResultStatus.CONTINUE,
                message=f"Task in progress. Iteration {self.current_iteration}.",
                next_command="Continue task implementation",
                decision_rationale="Task implementation proceeding normally"
            )
        
        else:
            return HookResult(
                status=HookResultStatus.CONTINUE,
                message=f"Workflow continuing. Iteration {self.current_iteration}.",
                decision_rationale="Autonomous workflow proceeding through methodology phases"
            )
    
    def _initialize_foundation_components(self):
        """Initialize all required foundation components"""
        
        from ..config.config_manager import ConfigManager
        from ..persistence.state_manager import StateManager
        from ..context.cross_reference_manager import CrossReferenceManager
        from ..analysis.decision_engine import LLMDecisionEngine
        
        # Initialize in dependency order
        self.config_manager = ConfigManager(str(self.project_root))
        self.state_manager = StateManager(str(self.project_root), config_manager=self.config_manager)
        self.cross_ref_manager = CrossReferenceManager(str(self.project_root))
        self.decision_engine = LLMDecisionEngine(str(self.project_root), config_manager=self.config_manager)
        
        # Load configuration limits
        config = self.config_manager.load_configuration()
        self.max_iterations = config.get('autonomous_behavior', {}).get('max_hook_iterations', 50)
        self.max_consecutive_failures = config.get('autonomous_behavior', {}).get('max_consecutive_failures', 5)
    
    def _handle_safety_limit_reached(self) -> HookResult:
        """Handle case where maximum iteration limit reached"""
        
        return HookResult(
            status=HookResultStatus.ESCALATE,
            message=f"SAFETY LIMIT REACHED: Maximum {self.max_iterations} hook iterations exceeded.",
            blocking_reason='safety_limit_exceeded',
            escalation_required=True,
            user_action_needed="Review autonomous session progress and either reset iteration counter or increase safety limits in configuration."
        )
    
    def _handle_excessive_failures(self) -> HookResult:
        """Handle case where consecutive failure limit reached"""
        
        return HookResult(
            status=HookResultStatus.ESCALATE,
            message=f"EXCESSIVE FAILURES: {self.consecutive_failures} consecutive failures exceeded limit.",
            blocking_reason='consecutive_failure_limit',
            escalation_required=True,
            user_action_needed="Review failure patterns and resolve underlying issues before continuing autonomous operation."
        )
    
    def _handle_autonomous_error(self, error: Exception, system_state=None) -> HookResult:
        """Handle errors in autonomous execution with recovery strategies"""
        
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'iteration': self.current_iteration,
            'consecutive_failures': self.consecutive_failures,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"Autonomous execution error: {error_context}")
        
        # Log error for debugging
        error_log_file = self.project_root / 'logs' / 'errors' / f"autonomous_error_{int(time.time())}.json"
        error_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(error_log_file, 'w') as f:
            import json
            json.dump(error_context, f, indent=2)
        
        # Determine recovery strategy based on error type
        if isinstance(error, StateConsistencyError):
            return HookResult(
                status=HookResultStatus.BLOCK,
                message=f"State corruption detected. Attempting recovery.",
                blocking_reason='state_corruption',
                escalation_required=True,
                user_action_needed="Review state files and restore from backup if necessary."
            )
        
        elif isinstance(error, (FileNotFoundError, PermissionError)):
            return HookResult(
                status=HookResultStatus.BLOCK,
                message=f"File system error: {str(error)}",
                blocking_reason='file_system_error',
                escalation_required=False,
                user_action_needed="Check file permissions and disk space."
            )
        
        else:
            return HookResult(
                status=HookResultStatus.ERROR,
                message=f"Autonomous execution error: {str(error)}",
                blocking_reason='unknown_error',
                escalation_required=True,
                user_action_needed="Review error logs and resolve underlying issue."
            )
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _get_ready_tasks(self, task_graph):
        """Get tasks that are ready for execution"""
        # Implementation would check dependencies and return ready tasks
        return [task for task in task_graph.nodes.values() if task.status == 'pending']
    
    def _select_highest_priority_task(self, ready_tasks):
        """Select highest priority task from ready tasks"""
        return max(ready_tasks, key=lambda t: t.priority)
    
    def _load_task_context(self, task, system_state):
        """Load context bundle for task execution"""
        return self.cross_ref_manager.expand_context_for_task(task, system_state.cross_references)
    
    def _collect_evidence_for_hook_cycle(self, action_result):
        """Collect evidence for this hook execution cycle"""
        if action_result.get('evidence_generated'):
            return EvidenceRecord(
                task_id=action_result.get('task_status_update', {}).get('task_id', 'hook_cycle'),
                evidence_type='hook_execution',
                evidence_data=action_result,
                collection_time=datetime.now(timezone.utc).isoformat(),
                validation_status='valid',
                file_references=[]
            )
        return None