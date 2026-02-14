#!/usr/bin/env python3
"""
Autonomous Workflow Manager - Orchestrator Layer
Main autonomous workflow coordination and state machine implementation

Based on pseudocode from pseudo_src/orchestrator/workflow_manager.py
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

# Import analysis components
from ..analysis.llm_decision_engine import LLMDecisionEngine, ExecutionContext, DecisionType
from ..context.cross_reference_manager import CrossReferenceManager
from ..utils.json_utilities import JSONUtilities

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
    evidence_generated: Optional[Dict[str, Any]] = None
    context_used: Optional[Dict[str, Any]] = None
    decision_rationale: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
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

class AutonomousWorkflowManager:
    """
    Main autonomous workflow coordination and state machine
    
    Orchestrates the complete autonomous TDD workflow including planning,
    implementation, testing, and quality validation
    """
    
    def __init__(self, project_root: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the autonomous workflow manager"""
        if not project_root:
            raise WorkflowError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        self.config = config or {}
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize workflow state
        self.current_phase = "initialization"
        self.workflow_active = False
        self.iteration_count = 0
        self.max_iterations = self.config.get('max_iterations', 10)
        
        # Initialize components
        self.decision_engine = LLMDecisionEngine(str(self.project_root), config)
        self.cross_ref_manager = CrossReferenceManager(str(self.project_root))
        self.json_utils = JSONUtilities()
        
        # Workflow execution history
        self.execution_history: List[HookResult] = []
    
    def execute_autonomous_workflow(self, initial_requirements: Optional[Dict[str, Any]] = None) -> HookResult:
        """Execute the complete autonomous workflow"""
        try:
            self.logger.info("Starting autonomous workflow execution")
            self.workflow_active = True
            self.iteration_count = 0
            
            # Initialize workflow context
            context = self._build_execution_context(initial_requirements)
            
            # Main workflow loop
            while self.workflow_active and self.iteration_count < self.max_iterations:
                self.iteration_count += 1
                
                # Analyze current situation
                situation = self.decision_engine.analyze_situation(context)
                
                # Make decisions about next steps
                decision = self.decision_engine.make_decision(
                    context, 
                    DecisionType.PHASE_PROGRESSION
                )
                
                # Execute the decided action
                result = self._execute_workflow_action(decision, context)
                
                # Record execution
                self.execution_history.append(result)
                
                # Check for completion or blocking conditions
                if result.status in [HookResultStatus.COMPLETE, HookResultStatus.BLOCK, HookResultStatus.ESCALATE]:
                    self.workflow_active = False
                    return result
                
                # Update context for next iteration
                context = self._update_execution_context(context, result)
                
                # Safety check - prevent infinite loops
                if self.iteration_count >= self.max_iterations:
                    return HookResult(
                        status=HookResultStatus.ESCALATE,
                        message=f"Workflow exceeded maximum iterations ({self.max_iterations})",
                        escalation_required=True,
                        decision_rationale="Safety limit reached"
                    )
            
            # Normal completion
            return HookResult(
                status=HookResultStatus.COMPLETE,
                message="Autonomous workflow completed successfully",
                decision_rationale="All phases completed"
            )
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return HookResult(
                status=HookResultStatus.ERROR,
                message=f"Workflow execution failed: {str(e)}",
                escalation_required=True
            )
        finally:
            self.workflow_active = False
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            'current_phase': self.current_phase,
            'workflow_active': self.workflow_active,
            'iteration_count': self.iteration_count,
            'max_iterations': self.max_iterations,
            'execution_history_length': len(self.execution_history),
            'last_execution_time': datetime.now(timezone.utc).isoformat()
        }
    
    def stop_workflow(self, reason: str = "User requested stop") -> HookResult:
        """Stop the autonomous workflow"""
        self.workflow_active = False
        return HookResult(
            status=HookResultStatus.BLOCK,
            message=f"Workflow stopped: {reason}",
            blocking_reason=reason,
            decision_rationale="User intervention"
        )
    
    def _build_execution_context(self, initial_requirements: Optional[Dict[str, Any]] = None):
        """Build initial execution context"""
        
        # Get available tasks (placeholder)
        available_tasks = self._discover_available_tasks()
        
        # Get recent test results (placeholder)
        test_results = self._get_recent_test_results()
        
        # Build context
        return ExecutionContext(
            current_phase=self.current_phase,
            current_task=None,
            iteration_count=self.iteration_count,
            micro_iteration_count=0,
            macro_iteration_count=0,
            last_test_results=test_results,
            recent_errors=[],
            evidence_collected=initial_requirements or {},
            available_tasks=available_tasks,
            blocking_conditions=[],
            time_constraints=None,
            project_state={}
        )
    
    def _update_execution_context(self, context, result: HookResult):
        """Update execution context based on workflow result"""
        # Update context with new information
        context.iteration_count = self.iteration_count
        
        # Add any evidence generated
        if result.evidence_generated:
            context.evidence_collected.update(result.evidence_generated)
        
        # Update blocking conditions
        if result.blocking_reason:
            context.blocking_conditions.append(result.blocking_reason)
        else:
            context.blocking_conditions = []  # Clear if no current blocking
        
        return context
    
    def _execute_workflow_action(self, decision, context) -> HookResult:
        """Execute a workflow action based on decision"""
        action = decision.action
        
        if action == "proceed_to_next_phase":
            return self._advance_to_next_phase(context)
        elif action == "block_progression":
            return HookResult(
                status=HookResultStatus.BLOCK,
                message="Progression blocked by decision engine",
                blocking_reason=decision.reasoning,
                decision_rationale=decision.reasoning
            )
        elif action == "escalate_blocking_conditions":
            return HookResult(
                status=HookResultStatus.ESCALATE,
                message="Escalating blocking conditions",
                escalation_required=True,
                decision_rationale=decision.reasoning
            )
        else:
            # Default: continue with current approach
            return HookResult(
                status=HookResultStatus.CONTINUE,
                message=f"Continuing with action: {action}",
                decision_rationale=decision.reasoning
            )
    
    def _advance_to_next_phase(self, context) -> HookResult:
        """Advance workflow to next phase"""
        phase_sequence = [
            "initialization", "planning", "architecture", "implementation", 
            "testing", "validation", "completion"
        ]
        
        try:
            current_index = phase_sequence.index(self.current_phase)
            if current_index < len(phase_sequence) - 1:
                next_phase = phase_sequence[current_index + 1]
                self.current_phase = next_phase
                
                return HookResult(
                    status=HookResultStatus.CONTINUE,
                    message=f"Advanced to phase: {next_phase}",
                    decision_rationale=f"Phase progression from {phase_sequence[current_index]} to {next_phase}"
                )
            else:
                return HookResult(
                    status=HookResultStatus.COMPLETE,
                    message="All phases completed",
                    decision_rationale="Reached final phase"
                )
        except ValueError:
            return HookResult(
                status=HookResultStatus.ERROR,
                message=f"Unknown phase: {self.current_phase}",
                decision_rationale="Invalid phase state"
            )
    
    def _discover_available_tasks(self) -> List[str]:
        """Discover available tasks (placeholder implementation)"""
        # This would integrate with actual task discovery logic
        return ["analyze_requirements", "create_tests", "implement_code", "run_validation"]
    
    def _get_recent_test_results(self) -> Optional[Dict[str, Any]]:
        """Get recent test results (placeholder implementation)"""
        # This would integrate with actual test runner
        return None
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of workflow execution"""
        return {
            'total_iterations': self.iteration_count,
            'current_phase': self.current_phase,
            'workflow_active': self.workflow_active,
            'execution_count': len(self.execution_history),
            'last_result': self.execution_history[-1].to_dict() if self.execution_history else None,
            'summary_timestamp': datetime.now(timezone.utc).isoformat()
        }