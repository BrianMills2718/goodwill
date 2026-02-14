#!/usr/bin/env python3
"""
LLM Decision Engine - Analysis Layer
Core decision-making component for autonomous TDD system

Based on pseudocode from pseudo_src/analysis/autonomous_decision_engine.py
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta

class DecisionType(Enum):
    """Types of decisions the engine can make"""
    TASK_SELECTION = "task_selection"
    PHASE_PROGRESSION = "phase_progression"
    ERROR_RESOLUTION = "error_resolution"
    CONTEXT_ADJUSTMENT = "context_adjustment"
    QUALITY_ASSESSMENT = "quality_assessment"
    BLOCKING_ESCALATION = "blocking_escalation"
    ITERATION_CONTROL = "iteration_control"

class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""
    VERY_HIGH = "very_high"  # 0.9+
    HIGH = "high"           # 0.7-0.9
    MEDIUM = "medium"       # 0.5-0.7
    LOW = "low"            # 0.3-0.5
    VERY_LOW = "very_low"  # <0.3

@dataclass
class ExecutionContext:
    """Context for decision making"""
    current_phase: str
    current_task: Optional[str]
    iteration_count: int
    micro_iteration_count: int
    macro_iteration_count: int
    last_test_results: Optional[Dict[str, Any]]
    recent_errors: List[Dict[str, Any]]
    evidence_collected: Dict[str, Any]
    available_tasks: List[str]
    blocking_conditions: List[str]
    time_constraints: Optional[Dict[str, Any]]
    project_state: Dict[str, Any]

@dataclass
class DecisionResult:
    """Result of autonomous decision"""
    decision_type: DecisionType
    action: str
    confidence: float
    confidence_level: ConfidenceLevel
    reasoning: str
    metadata: Dict[str, Any]
    next_instruction: Optional[str] = None
    blocking_conditions: List[str] = field(default_factory=list)
    estimated_duration: Optional[timedelta] = None
    success_criteria: List[str] = field(default_factory=list)

@dataclass
class SituationAnalysis:
    """Analysis of current execution situation"""
    situation_type: str
    urgency_level: str
    complexity_assessment: str
    risk_factors: List[str]
    success_indicators: List[str]
    failure_indicators: List[str]
    recommended_actions: List[str]

class LLMDecisionEngineError(Exception):
    """Raised when decision engine operations fail"""
    pass

class LLMDecisionEngine:
    """
    Core decision-making component for autonomous TDD system
    
    Analyzes context, evaluates situations, and makes autonomous decisions
    about next actions in the TDD workflow
    """
    
    def __init__(self, project_root: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the LLM decision engine"""
        if not project_root:
            raise LLMDecisionEngineError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        self.config = config or {}
        
        # Decision-making parameters
        self.confidence_thresholds = {
            'proceed': 0.7,
            'escalate': 0.3,
            'block': 0.1
        }
        
        # Decision history for learning
        self.decision_history: List[DecisionResult] = []
        
        # Import utilities
        from ..utils.json_utilities import JSONUtilities
        self.json_utils = JSONUtilities()
    
    def analyze_situation(self, context: ExecutionContext) -> SituationAnalysis:
        """Analyze current execution situation"""
        try:
            # Assess situation type based on context
            situation_type = self._determine_situation_type(context)
            
            # Evaluate urgency
            urgency_level = self._assess_urgency(context)
            
            # Assess complexity
            complexity_assessment = self._assess_complexity(context)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(context)
            
            # Identify success/failure indicators
            success_indicators = self._identify_success_indicators(context)
            failure_indicators = self._identify_failure_indicators(context)
            
            # Generate recommended actions
            recommended_actions = self._generate_recommended_actions(context, situation_type)
            
            return SituationAnalysis(
                situation_type=situation_type,
                urgency_level=urgency_level,
                complexity_assessment=complexity_assessment,
                risk_factors=risk_factors,
                success_indicators=success_indicators,
                failure_indicators=failure_indicators,
                recommended_actions=recommended_actions
            )
            
        except Exception as e:
            raise LLMDecisionEngineError(f"Failed to analyze situation: {str(e)}")
    
    def make_decision(self, context: ExecutionContext, decision_type: DecisionType) -> DecisionResult:
        """Make an autonomous decision based on context"""
        try:
            # First analyze the situation
            situation = self.analyze_situation(context)
            
            # Generate decision based on type
            if decision_type == DecisionType.TASK_SELECTION:
                return self._decide_task_selection(context, situation)
            elif decision_type == DecisionType.PHASE_PROGRESSION:
                return self._decide_phase_progression(context, situation)
            elif decision_type == DecisionType.ERROR_RESOLUTION:
                return self._decide_error_resolution(context, situation)
            elif decision_type == DecisionType.QUALITY_ASSESSMENT:
                return self._decide_quality_assessment(context, situation)
            elif decision_type == DecisionType.BLOCKING_ESCALATION:
                return self._decide_blocking_escalation(context, situation)
            else:
                return self._decide_fallback(context, situation, decision_type)
                
        except Exception as e:
            raise LLMDecisionEngineError(f"Failed to make decision: {str(e)}")
    
    def _determine_situation_type(self, context: ExecutionContext) -> str:
        """Determine the type of situation based on context"""
        # Check for blocking conditions
        if context.blocking_conditions:
            return "blocked"
        
        # Check for recent errors
        if context.recent_errors:
            return "error_recovery"
        
        # Check iteration counts for potential issues
        if context.micro_iteration_count > 5:
            return "iteration_concern"
        
        # Check test results
        if context.last_test_results:
            if context.last_test_results.get('failed', 0) > 0:
                return "test_failures"
            elif context.last_test_results.get('passed', 0) > 0:
                return "progress"
        
        # Default to normal progression
        return "normal_progression"
    
    def _assess_urgency(self, context: ExecutionContext) -> str:
        """Assess urgency level of current situation"""
        # High urgency conditions
        if context.blocking_conditions:
            return "high"
        
        if context.macro_iteration_count >= 3:
            return "high"
        
        if len(context.recent_errors) >= 3:
            return "high"
        
        # Medium urgency conditions
        if context.micro_iteration_count >= 3:
            return "medium"
        
        if context.recent_errors:
            return "medium"
        
        # Low urgency
        return "low"
    
    def _assess_complexity(self, context: ExecutionContext) -> str:
        """Assess complexity of current situation"""
        complexity_score = 0
        
        # Add complexity for blocking conditions
        complexity_score += len(context.blocking_conditions) * 2
        
        # Add complexity for recent errors
        complexity_score += len(context.recent_errors)
        
        # Add complexity for high iteration counts
        if context.micro_iteration_count > 3:
            complexity_score += 2
        
        if context.macro_iteration_count > 1:
            complexity_score += 3
        
        # Add complexity for multiple available tasks
        if len(context.available_tasks) > 5:
            complexity_score += 1
        
        # Classify complexity
        if complexity_score >= 8:
            return "very_high"
        elif complexity_score >= 5:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _identify_risk_factors(self, context: ExecutionContext) -> List[str]:
        """Identify risk factors in current situation"""
        risks = []
        
        if context.blocking_conditions:
            risks.append("blocking_conditions_present")
        
        if context.macro_iteration_count >= 2:
            risks.append("approaching_iteration_limits")
        
        if len(context.recent_errors) >= 2:
            risks.append("recurring_errors")
        
        if context.micro_iteration_count >= 4:
            risks.append("micro_iteration_escalation")
        
        if not context.available_tasks:
            risks.append("no_available_tasks")
        
        return risks
    
    def _identify_success_indicators(self, context: ExecutionContext) -> List[str]:
        """Identify success indicators in current situation"""
        indicators = []
        
        if context.last_test_results and context.last_test_results.get('passed', 0) > 0:
            indicators.append("tests_passing")
        
        if not context.recent_errors:
            indicators.append("no_recent_errors")
        
        if context.available_tasks:
            indicators.append("tasks_available")
        
        if context.micro_iteration_count <= 2:
            indicators.append("low_iteration_count")
        
        return indicators
    
    def _identify_failure_indicators(self, context: ExecutionContext) -> List[str]:
        """Identify failure indicators in current situation"""
        indicators = []
        
        if context.last_test_results and context.last_test_results.get('failed', 0) > 0:
            indicators.append("tests_failing")
        
        if len(context.recent_errors) >= 3:
            indicators.append("multiple_recent_errors")
        
        if context.macro_iteration_count >= 3:
            indicators.append("excessive_macro_iterations")
        
        if context.blocking_conditions:
            indicators.append("blocking_conditions")
        
        return indicators
    
    def _generate_recommended_actions(self, context: ExecutionContext, situation_type: str) -> List[str]:
        """Generate recommended actions based on situation"""
        actions = []
        
        if situation_type == "blocked":
            actions.extend([
                "analyze_blocking_conditions",
                "attempt_automated_resolution",
                "escalate_if_unresolvable"
            ])
        elif situation_type == "error_recovery":
            actions.extend([
                "analyze_error_patterns",
                "apply_error_resolution_strategies",
                "implement_fixes"
            ])
        elif situation_type == "test_failures":
            actions.extend([
                "analyze_test_failures",
                "implement_fixes",
                "run_tests_again"
            ])
        elif situation_type == "iteration_concern":
            actions.extend([
                "review_iteration_strategy",
                "consider_macro_iteration",
                "reassess_approach"
            ])
        else:  # normal_progression
            actions.extend([
                "continue_current_task",
                "monitor_progress",
                "prepare_next_steps"
            ])
        
        return actions
    
    def _decide_task_selection(self, context: ExecutionContext, situation: SituationAnalysis) -> DecisionResult:
        """Decide which task to select next"""
        if not context.available_tasks:
            return DecisionResult(
                decision_type=DecisionType.TASK_SELECTION,
                action="escalate_no_tasks",
                confidence=0.9,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="No available tasks to select",
                metadata={"available_tasks": context.available_tasks},
                blocking_conditions=["no_available_tasks"]
            )
        
        # Simple selection: first available task
        selected_task = context.available_tasks[0]
        
        return DecisionResult(
            decision_type=DecisionType.TASK_SELECTION,
            action="select_task",
            confidence=0.7,
            confidence_level=ConfidenceLevel.HIGH,
            reasoning=f"Selected first available task: {selected_task}",
            metadata={"selected_task": selected_task, "available_tasks": context.available_tasks},
            next_instruction=f"Execute task: {selected_task}"
        )
    
    def _decide_phase_progression(self, context: ExecutionContext, situation: SituationAnalysis) -> DecisionResult:
        """Decide whether to progress to next phase"""
        # Check for blocking conditions
        if context.blocking_conditions:
            return DecisionResult(
                decision_type=DecisionType.PHASE_PROGRESSION,
                action="block_progression",
                confidence=0.9,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="Phase progression blocked by unresolved conditions",
                metadata={"blocking_conditions": context.blocking_conditions},
                blocking_conditions=context.blocking_conditions
            )
        
        # Check test results
        if context.last_test_results:
            failed_tests = context.last_test_results.get('failed', 0)
            if failed_tests > 0:
                return DecisionResult(
                    decision_type=DecisionType.PHASE_PROGRESSION,
                    action="defer_progression",
                    confidence=0.8,
                    confidence_level=ConfidenceLevel.HIGH,
                    reasoning=f"Phase progression deferred due to {failed_tests} failing tests",
                    metadata={"test_results": context.last_test_results}
                )
        
        # Allow progression
        return DecisionResult(
            decision_type=DecisionType.PHASE_PROGRESSION,
            action="proceed_to_next_phase",
            confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            reasoning="Conditions met for phase progression",
            metadata={"current_phase": context.current_phase}
        )
    
    def _decide_error_resolution(self, context: ExecutionContext, situation: SituationAnalysis) -> DecisionResult:
        """Decide how to resolve errors"""
        if not context.recent_errors:
            return DecisionResult(
                decision_type=DecisionType.ERROR_RESOLUTION,
                action="no_action_needed",
                confidence=0.9,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="No recent errors to resolve",
                metadata={}
            )
        
        error_count = len(context.recent_errors)
        
        if error_count >= 3:
            return DecisionResult(
                decision_type=DecisionType.ERROR_RESOLUTION,
                action="escalate_persistent_errors",
                confidence=0.8,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning=f"Escalating {error_count} persistent errors",
                metadata={"error_count": error_count, "errors": context.recent_errors}
            )
        
        return DecisionResult(
            decision_type=DecisionType.ERROR_RESOLUTION,
            action="attempt_automated_fix",
            confidence=0.6,
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=f"Attempting automated resolution of {error_count} errors",
            metadata={"error_count": error_count, "errors": context.recent_errors}
        )
    
    def _decide_quality_assessment(self, context: ExecutionContext, situation: SituationAnalysis) -> DecisionResult:
        """Decide on quality assessment result"""
        # Simple quality assessment based on test results and errors
        quality_score = 0.5  # Base score
        
        # Adjust based on test results
        if context.last_test_results:
            passed = context.last_test_results.get('passed', 0)
            total = context.last_test_results.get('total', 1)
            quality_score += (passed / total) * 0.4
        
        # Reduce for recent errors
        error_penalty = min(len(context.recent_errors) * 0.1, 0.3)
        quality_score -= error_penalty
        
        # Reduce for high iteration counts
        iteration_penalty = min(context.micro_iteration_count * 0.05, 0.2)
        quality_score -= iteration_penalty
        
        quality_score = max(0.0, min(1.0, quality_score))
        
        if quality_score >= 0.8:
            quality_level = "high"
        elif quality_score >= 0.6:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        return DecisionResult(
            decision_type=DecisionType.QUALITY_ASSESSMENT,
            action=f"assess_quality_{quality_level}",
            confidence=0.7,
            confidence_level=ConfidenceLevel.HIGH,
            reasoning=f"Quality assessed as {quality_level} (score: {quality_score:.2f})",
            metadata={"quality_score": quality_score, "quality_level": quality_level}
        )
    
    def _decide_blocking_escalation(self, context: ExecutionContext, situation: SituationAnalysis) -> DecisionResult:
        """Decide whether to escalate blocking conditions"""
        if not context.blocking_conditions:
            return DecisionResult(
                decision_type=DecisionType.BLOCKING_ESCALATION,
                action="no_escalation_needed",
                confidence=0.9,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="No blocking conditions present",
                metadata={}
            )
        
        # Escalate if multiple blocking conditions or high iteration count
        if len(context.blocking_conditions) > 1 or context.macro_iteration_count >= 2:
            return DecisionResult(
                decision_type=DecisionType.BLOCKING_ESCALATION,
                action="escalate_blocking_conditions",
                confidence=0.9,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="Multiple blocking conditions or high iteration count",
                metadata={"blocking_conditions": context.blocking_conditions},
                blocking_conditions=context.blocking_conditions
            )
        
        return DecisionResult(
            decision_type=DecisionType.BLOCKING_ESCALATION,
            action="attempt_resolution",
            confidence=0.6,
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning="Attempting to resolve single blocking condition",
            metadata={"blocking_conditions": context.blocking_conditions}
        )
    
    def _decide_fallback(self, context: ExecutionContext, situation: SituationAnalysis, decision_type: DecisionType) -> DecisionResult:
        """Fallback decision for unhandled decision types"""
        return DecisionResult(
            decision_type=decision_type,
            action="continue_current_approach",
            confidence=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=f"Fallback decision for {decision_type.value}",
            metadata={"fallback": True}
        )
    
    def _confidence_to_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW