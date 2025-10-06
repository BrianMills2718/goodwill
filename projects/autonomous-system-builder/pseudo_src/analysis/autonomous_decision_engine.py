# Autonomous Decision Engine - Analysis Layer Pseudocode
# Part of autonomous TDD system analysis components

"""
Autonomous Decision Engine

Core decision-making component that analyzes context, evaluates situations,
and makes autonomous decisions about next actions in the TDD workflow.

Implements the detailed LLM integration patterns and decision logic
established in docs/architecture/llm_integration_patterns.md
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta

# === Configuration and Data Classes ===

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
    confidence_score: float

# === Autonomous Decision Engine Implementation ===

class AutonomousDecisionEngine:
    """
    Core autonomous decision engine for TDD workflow management
    
    Implements sophisticated decision-making using LLM integration patterns
    from docs/architecture/llm_integration_patterns.md and evidence validation
    from docs/architecture/evidence_validation_detailed.md
    """
    
    def __init__(self, config: DecisionEngineConfig):
        self.config = config
        
        # Core components (injected via dependency injection)
        self.llm_integration = None  # Injected via setter
        self.evidence_collector = None  # Injected via setter  
        self.context_loader = None  # Injected via setter
        
        # Decision analyzers
        self.situation_analyzer = SituationAnalyzer(config.analysis_config)
        self.task_selector = TaskSelector(config.task_selection_config)
        self.phase_controller = PhaseProgressionController(config.phase_config)
        self.error_analyzer = ErrorAnalyzer(config.error_analysis_config)
        self.quality_assessor = QualityAssessor(config.quality_config)
        
        # Decision history and learning
        self.decision_history = []
        self.pattern_recognizer = DecisionPatternRecognizer()
        self.performance_tracker = DecisionPerformanceTracker()
        
        # State management
        self.current_context = None
        self.last_decision_time = None
        self.consecutive_failures = 0
    
    def set_llm_integration(self, llm_integration):
        """Setter injection for LLM integration to avoid circular dependencies"""
        self.llm_integration = llm_integration
    
    def set_evidence_collector(self, evidence_collector):
        """Setter injection for evidence collector to avoid circular dependencies"""
        self.evidence_collector = evidence_collector
    
    def set_context_loader(self, context_loader):
        """Setter injection for context loader to avoid circular dependencies"""
        self.context_loader = context_loader
    
    def make_autonomous_decision(self, context: ExecutionContext) -> DecisionResult:
        """
        Make autonomous decision based on current execution context
        
        Args:
            context: Current execution context with all relevant information
            
        Returns:
            DecisionResult with specific action and reasoning
        """
        
        try:
            # Update internal state
            self.current_context = context
            decision_start_time = datetime.now()
            
            # Phase 1: Analyze current situation
            situation_analysis = self.situation_analyzer.analyze_situation(context)
            
            # Phase 2: Determine decision type needed
            decision_type = self._determine_decision_type(context, situation_analysis)
            
            # Phase 3: Generate decision using appropriate analyzer
            decision_result = self._generate_decision(decision_type, context, situation_analysis)
            
            # Phase 4: Validate decision quality
            validation_result = self._validate_decision(decision_result, context)
            
            if not validation_result.valid:
                # Fallback to safe decision
                decision_result = self._generate_fallback_decision(decision_type, context, validation_result.issues)
            
            # Phase 5: Enhance decision with LLM analysis (if available)
            if self.llm_integration:
                enhanced_decision = self._enhance_decision_with_llm(decision_result, context, situation_analysis)
                if enhanced_decision.confidence > decision_result.confidence:
                    decision_result = enhanced_decision
            
            # Phase 6: Track decision for learning
            self._track_decision(decision_result, context, situation_analysis, decision_start_time)
            
            # Phase 7: Update consecutive failure counter
            self._update_failure_tracking(decision_result)
            
            return decision_result
            
        except Exception as e:
            # Emergency fallback decision
            return self._generate_emergency_fallback_decision(context, str(e))
    
    def _determine_decision_type(self, context: ExecutionContext, analysis: SituationAnalysis) -> DecisionType:
        """Determine what type of decision is needed"""
        
        # Check for blocking conditions first
        if context.blocking_conditions:
            return DecisionType.BLOCKING_ESCALATION
        
        # Check for errors that need resolution
        if context.recent_errors and len(context.recent_errors) > 0:
            return DecisionType.ERROR_RESOLUTION
        
        # Check if iteration control is needed
        if (context.micro_iteration_count >= self.config.max_micro_iterations or
            context.macro_iteration_count >= self.config.max_macro_iterations):
            return DecisionType.ITERATION_CONTROL
        
        # Check if phase progression is appropriate
        if self._should_consider_phase_progression(context, analysis):
            return DecisionType.PHASE_PROGRESSION
        
        # Check if quality assessment is needed
        if self._should_assess_quality(context):
            return DecisionType.QUALITY_ASSESSMENT
        
        # Check if context adjustment is needed
        if self._should_adjust_context(context, analysis):
            return DecisionType.CONTEXT_ADJUSTMENT
        
        # Default to task selection
        return DecisionType.TASK_SELECTION
    
    def _generate_decision(self, decision_type: DecisionType, context: ExecutionContext, analysis: SituationAnalysis) -> DecisionResult:
        """Generate decision using appropriate specialized analyzer"""
        
        if decision_type == DecisionType.TASK_SELECTION:
            return self.task_selector.select_next_task(context, analysis)
        
        elif decision_type == DecisionType.PHASE_PROGRESSION:
            return self.phase_controller.evaluate_phase_progression(context, analysis)
        
        elif decision_type == DecisionType.ERROR_RESOLUTION:
            return self.error_analyzer.analyze_and_resolve_errors(context, analysis)
        
        elif decision_type == DecisionType.QUALITY_ASSESSMENT:
            return self.quality_assessor.assess_quality_and_recommend(context, analysis)
        
        elif decision_type == DecisionType.CONTEXT_ADJUSTMENT:
            return self._generate_context_adjustment_decision(context, analysis)
        
        elif decision_type == DecisionType.BLOCKING_ESCALATION:
            return self._generate_blocking_escalation_decision(context, analysis)
        
        elif decision_type == DecisionType.ITERATION_CONTROL:
            return self._generate_iteration_control_decision(context, analysis)
        
        else:
            # Fallback to task selection
            return self.task_selector.select_next_task(context, analysis)
    
    def _enhance_decision_with_llm(self, decision: DecisionResult, context: ExecutionContext, analysis: SituationAnalysis) -> DecisionResult:
        """Enhance decision using LLM analysis"""
        
        try:
            # Prepare context for LLM analysis
            llm_context = self._prepare_llm_context(decision, context, analysis)
            
            # Generate LLM prompt for decision enhancement
            prompt_request = self.llm_integration.generate_decision_enhancement_prompt(
                decision=decision,
                context=llm_context,
                analysis=analysis
            )
            
            # Execute LLM analysis
            llm_result = self.llm_integration.execute_llm_task(prompt_request)
            
            if llm_result.success:
                # Parse LLM response
                enhanced_analysis = self._parse_llm_decision_response(llm_result.response_data)
                
                # Merge LLM insights with original decision
                enhanced_decision = self._merge_llm_insights(decision, enhanced_analysis)
                
                return enhanced_decision
            else:
                # LLM analysis failed, return original decision
                return decision
                
        except Exception as e:
            # LLM enhancement failed, return original decision
            self._log_llm_enhancement_failure(e)
            return decision
    
    def _prepare_llm_context(self, decision: DecisionResult, context: ExecutionContext, analysis: SituationAnalysis) -> Dict[str, Any]:
        """Prepare context for LLM analysis"""
        
        llm_context = {
            'current_decision': {
                'action': decision.action,
                'confidence': decision.confidence,
                'reasoning': decision.reasoning
            },
            'execution_context': {
                'phase': context.current_phase,
                'task': context.current_task,
                'iterations': {
                    'micro': context.micro_iteration_count,
                    'macro': context.macro_iteration_count
                },
                'recent_errors': context.recent_errors[-3:] if context.recent_errors else [],
                'blocking_conditions': context.blocking_conditions
            },
            'situation_analysis': {
                'type': analysis.situation_type,
                'urgency': analysis.urgency_level,
                'complexity': analysis.complexity_assessment,
                'risk_factors': analysis.risk_factors,
                'success_indicators': analysis.success_indicators
            },
            'decision_history': self._get_recent_decision_history(5),
            'performance_metrics': self.performance_tracker.get_recent_metrics()
        }
        
        return llm_context
    
    def _validate_decision(self, decision: DecisionResult, context: ExecutionContext) -> DecisionValidationResult:
        """Validate decision quality and safety"""
        
        validation_issues = []
        
        # Check confidence threshold
        if decision.confidence < self.config.min_decision_confidence:
            validation_issues.append(f"Decision confidence {decision.confidence} below threshold {self.config.min_decision_confidence}")
        
        # Check for infinite loop patterns
        if self._detect_decision_loop(decision, context):
            validation_issues.append("Decision may create infinite loop based on recent history")
        
        # Check for resource constraints
        if self._violates_resource_constraints(decision, context):
            validation_issues.append("Decision violates resource constraints")
        
        # Check for safety constraints
        if self._violates_safety_constraints(decision, context):
            validation_issues.append("Decision violates safety constraints")
        
        # Check for logical consistency
        logical_issues = self._check_logical_consistency(decision, context)
        validation_issues.extend(logical_issues)
        
        return DecisionValidationResult(
            valid=len(validation_issues) == 0,
            issues=validation_issues,
            confidence_adjustment=max(0.0, decision.confidence - 0.1 * len(validation_issues))
        )
    
    def _generate_fallback_decision(self, decision_type: DecisionType, context: ExecutionContext, issues: List[str]) -> DecisionResult:
        """Generate safe fallback decision when primary decision fails validation"""
        
        fallback_action = "continue_current_task"
        reasoning = f"Using fallback decision due to validation issues: {'; '.join(issues)}"
        
        # Safe fallback based on decision type
        if decision_type == DecisionType.ERROR_RESOLUTION:
            fallback_action = "escalate_error_to_user"
            reasoning = "Escalating error resolution to user due to validation failures"
        
        elif decision_type == DecisionType.PHASE_PROGRESSION:
            fallback_action = "continue_current_phase"
            reasoning = "Continuing current phase due to progression validation failures"
        
        elif decision_type == DecisionType.BLOCKING_ESCALATION:
            fallback_action = "escalate_to_user"
            reasoning = "Escalating blocking condition to user"
        
        return DecisionResult(
            decision_type=decision_type,
            action=fallback_action,
            confidence=0.3,  # Low confidence for fallback
            confidence_level=ConfidenceLevel.LOW,
            reasoning=reasoning,
            metadata={'is_fallback': True, 'validation_issues': issues},
            blocking_conditions=context.blocking_conditions
        )

# === Specialized Decision Components ===

class SituationAnalyzer:
    """Analyze current execution situation"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def analyze_situation(self, context: ExecutionContext) -> SituationAnalysis:
        """Analyze current situation and provide assessment"""
        
        # Determine situation type
        situation_type = self._classify_situation_type(context)
        
        # Assess urgency
        urgency_level = self._assess_urgency(context)
        
        # Assess complexity
        complexity_assessment = self._assess_complexity(context)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(context)
        
        # Identify success indicators
        success_indicators = self._identify_success_indicators(context)
        
        # Identify failure indicators
        failure_indicators = self._identify_failure_indicators(context)
        
        # Generate recommended actions
        recommended_actions = self._generate_action_recommendations(context, situation_type, urgency_level)
        
        # Calculate overall confidence
        confidence_score = self._calculate_situation_confidence(context, risk_factors, success_indicators)
        
        return SituationAnalysis(
            situation_type=situation_type,
            urgency_level=urgency_level,
            complexity_assessment=complexity_assessment,
            risk_factors=risk_factors,
            success_indicators=success_indicators,
            failure_indicators=failure_indicators,
            recommended_actions=recommended_actions,
            confidence_score=confidence_score
        )
    
    def _classify_situation_type(self, context: ExecutionContext) -> str:
        """Classify the current situation type"""
        
        if context.blocking_conditions:
            return "blocked"
        
        if context.recent_errors and len(context.recent_errors) > 2:
            return "error_prone"
        
        if context.micro_iteration_count > 3:
            return "iterating"
        
        if not context.available_tasks:
            return "no_tasks"
        
        if context.last_test_results and context.last_test_results.get('success', False):
            return "progressing"
        
        return "normal"

class TaskSelector:
    """Select next task for execution"""
    
    def __init__(self, config: TaskSelectionConfig):
        self.config = config
        self.task_prioritizer = TaskPrioritizer()
        self.dependency_analyzer = TaskDependencyAnalyzer()
    
    def select_next_task(self, context: ExecutionContext, analysis: SituationAnalysis) -> DecisionResult:
        """Select the most appropriate next task"""
        
        if not context.available_tasks:
            return DecisionResult(
                decision_type=DecisionType.TASK_SELECTION,
                action="no_tasks_available",
                confidence=1.0,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="No tasks available for selection",
                metadata={'available_tasks': []},
                blocking_conditions=["no_available_tasks"]
            )
        
        # Prioritize tasks based on multiple factors
        prioritized_tasks = self.task_prioritizer.prioritize_tasks(
            context.available_tasks, context, analysis
        )
        
        # Check task dependencies
        dependency_analysis = self.dependency_analyzer.analyze_dependencies(
            prioritized_tasks, context
        )
        
        # Select highest priority task that can be executed
        selected_task = None
        selection_reasoning = []
        
        for task in prioritized_tasks:
            if self._can_execute_task(task, dependency_analysis, context):
                selected_task = task
                selection_reasoning.append(f"Selected '{task}' - highest priority executable task")
                break
            else:
                blocking_deps = dependency_analysis.get_blocking_dependencies(task)
                selection_reasoning.append(f"Skipped '{task}' - blocked by: {blocking_deps}")
        
        if not selected_task:
            return DecisionResult(
                decision_type=DecisionType.TASK_SELECTION,
                action="all_tasks_blocked",
                confidence=0.9,
                confidence_level=ConfidenceLevel.HIGH,
                reasoning="All available tasks are blocked by dependencies",
                metadata={
                    'available_tasks': context.available_tasks,
                    'blocking_analysis': dependency_analysis.get_summary()
                },
                blocking_conditions=["all_tasks_have_blocking_dependencies"]
            )
        
        # Calculate confidence based on task clarity and dependencies
        confidence = self._calculate_task_selection_confidence(selected_task, dependency_analysis, context)
        
        return DecisionResult(
            decision_type=DecisionType.TASK_SELECTION,
            action=f"execute_task:{selected_task}",
            confidence=confidence,
            confidence_level=self._confidence_to_level(confidence),
            reasoning="; ".join(selection_reasoning),
            metadata={
                'selected_task': selected_task,
                'task_priority_score': self.task_prioritizer.get_priority_score(selected_task),
                'dependency_analysis': dependency_analysis.get_task_analysis(selected_task)
            },
            next_instruction=f"Execute task: {selected_task}"
        )

class ErrorAnalyzer:
    """Analyze and resolve errors"""
    
    def __init__(self, config: ErrorAnalysisConfig):
        self.config = config
        self.error_classifier = ErrorClassifier()
        self.resolution_strategist = ErrorResolutionStrategist()
    
    def analyze_and_resolve_errors(self, context: ExecutionContext, analysis: SituationAnalysis) -> DecisionResult:
        """Analyze errors and recommend resolution strategy"""
        
        if not context.recent_errors:
            return DecisionResult(
                decision_type=DecisionType.ERROR_RESOLUTION,
                action="no_errors_to_resolve",
                confidence=1.0,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                reasoning="No recent errors require resolution",
                metadata={'error_count': 0}
            )
        
        # Classify errors by type and severity
        error_classification = self.error_classifier.classify_errors(context.recent_errors)
        
        # Analyze error patterns
        error_patterns = self._analyze_error_patterns(context.recent_errors)
        
        # Determine resolution strategy
        resolution_strategy = self.resolution_strategist.determine_strategy(
            error_classification, error_patterns, context
        )
        
        # Calculate resolution confidence
        confidence = self._calculate_resolution_confidence(
            error_classification, resolution_strategy, context
        )
        
        return DecisionResult(
            decision_type=DecisionType.ERROR_RESOLUTION,
            action=resolution_strategy.action,
            confidence=confidence,
            confidence_level=self._confidence_to_level(confidence),
            reasoning=resolution_strategy.reasoning,
            metadata={
                'error_classification': error_classification.get_summary(),
                'error_patterns': error_patterns,
                'resolution_strategy': resolution_strategy.get_details()
            },
            next_instruction=resolution_strategy.next_instruction,
            estimated_duration=resolution_strategy.estimated_duration
        )

# === Supporting Classes ===

@dataclass
class DecisionValidationResult:
    """Result of decision validation"""
    valid: bool
    issues: List[str]
    confidence_adjustment: float

class DecisionPatternRecognizer:
    """Recognize patterns in decision making"""
    
    def detect_decision_loops(self, recent_decisions: List[DecisionResult]) -> List[str]:
        """Detect potentially problematic decision loops"""
        # Implementation for loop detection
        pass

class DecisionPerformanceTracker:
    """Track decision performance over time"""
    
    def track_decision_outcome(self, decision: DecisionResult, outcome: str, duration: timedelta):
        """Track the outcome of a decision"""
        # Implementation for performance tracking
        pass
    
    def get_recent_metrics(self) -> Dict[str, Any]:
        """Get recent performance metrics"""
        # Implementation for metrics retrieval
        pass

# This pseudocode implements a comprehensive autonomous decision engine
# that can analyze situations, make informed decisions, and learn from outcomes
# while maintaining safety and validation checks throughout the process.