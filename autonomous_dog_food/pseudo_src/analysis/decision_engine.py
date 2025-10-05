#!/usr/bin/env python3
"""
DECISION ENGINE - Foundation Component
LLM-powered analysis and decision-making for autonomous workflow
"""

# RELATES_TO: ../persistence/state_manager.py, ../context/cross_reference_manager.py, ../utils/json_utils.py

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone

class DecisionType(Enum):
    """Types of decisions the engine can make"""
    TASK_SELECTION = "task_selection"
    PHASE_PROGRESSION = "phase_progression"
    ERROR_ANALYSIS = "error_analysis"
    CONTEXT_PRIORITIZATION = "context_prioritization"
    DEPENDENCY_RESOLUTION = "dependency_resolution"
    ESCALATION_TRIGGER = "escalation_trigger"
    IMPLEMENTATION_STRATEGY = "implementation_strategy"

class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"

@dataclass
class DecisionContext:
    """Context information for making decisions"""
    decision_type: DecisionType
    project_state: Dict[str, Any]
    available_options: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    previous_decisions: List[Dict[str, Any]]
    evidence_available: Dict[str, Any]
    time_pressure: str  # 'low', 'medium', 'high'
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['decision_type'] = self.decision_type.value
        return result

@dataclass
class DecisionResult:
    """Result of a decision-making process"""
    decision_type: DecisionType
    selected_option: Dict[str, Any]
    confidence: ConfidenceLevel
    reasoning: str
    alternative_options: List[Dict[str, Any]]
    risks_identified: List[str]
    mitigation_strategies: List[str]
    evidence_used: List[str]
    follow_up_actions: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['decision_type'] = self.decision_type.value
        result['confidence'] = self.confidence.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionResult':
        data_copy = data.copy()
        data_copy['decision_type'] = DecisionType(data_copy['decision_type'])
        data_copy['confidence'] = ConfidenceLevel(data_copy['confidence'])
        return cls(**data_copy)

class DecisionError(Exception):
    """Raised when decision-making fails"""
    pass

class LLMDecisionEngine:
    """
    LLM-powered decision engine for autonomous workflow
    
    FOUNDATION COMPONENT: Depends on JSON utilities and file operations
    Provides intelligent decision-making for task selection, error analysis, etc.
    """
    
    def __init__(self, project_root: str, config_manager=None):
        """
        Initialize decision engine
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        - config_manager: Optional ConfigManager instance
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists
        - Initializes decision history tracking
        - Sets up LLM interaction mechanisms
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise DecisionError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise DecisionError(f"Project root does not exist: {project_root}")
        
        # Configuration
        if config_manager is None:
            from ..config.config_manager import ConfigManager
            self.config_manager = ConfigManager(project_root)
        else:
            self.config_manager = config_manager
        
        # Decision storage
        self.decision_dir = self.project_root / 'logs' / 'decisions'
        self.decision_dir.mkdir(parents=True, exist_ok=True)
        
        self.decision_history_file = self.decision_dir / 'decision_history.json'
        self.llm_interaction_dir = self.decision_dir / 'llm_interactions'
        self.llm_interaction_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON utilities
        from ..utils.json_utils import JSONUtilities
        self.json_utils = JSONUtilities()
        
        # Decision patterns and strategies
        self._initialize_decision_strategies()
        
        # Decision history cache
        self._decision_history: Optional[List[DecisionResult]] = None
    
    def make_task_selection_decision(self, available_tasks: List[Dict[str, Any]], project_state: Dict[str, Any]) -> DecisionResult:
        """
        Select the best task to execute next
        
        PARAMETERS:
        - available_tasks: List of tasks ready for execution
        - project_state: Current state of the project
        
        RETURNS: Decision result with selected task
        
        DECISION FACTORS:
        - Task priority and dependencies
        - Resource availability
        - Risk assessment
        - Project phase requirements
        """
        
        try:
            # Prepare decision context
            context = DecisionContext(
                decision_type=DecisionType.TASK_SELECTION,
                project_state=project_state,
                available_options=available_tasks,
                constraints=self._get_task_selection_constraints(project_state),
                previous_decisions=self._get_recent_decisions(DecisionType.TASK_SELECTION, limit=5),
                evidence_available=self._gather_task_evidence(available_tasks),
                time_pressure=self._assess_time_pressure(project_state)
            )
            
            # Generate LLM prompt for task selection
            prompt = self._generate_task_selection_prompt(context)
            
            # Get LLM decision
            llm_response = self._query_llm_for_decision(prompt, "task_selection")
            
            # Parse and validate LLM response
            decision_data = self._parse_llm_decision_response(llm_response, available_tasks)
            
            # Create decision result
            decision = DecisionResult(
                decision_type=DecisionType.TASK_SELECTION,
                selected_option=decision_data['selected_task'],
                confidence=ConfidenceLevel(decision_data['confidence']),
                reasoning=decision_data['reasoning'],
                alternative_options=decision_data.get('alternatives', []),
                risks_identified=decision_data.get('risks', []),
                mitigation_strategies=decision_data.get('mitigations', []),
                evidence_used=decision_data.get('evidence_used', []),
                follow_up_actions=decision_data.get('follow_up_actions', []),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Save decision to history
            self._save_decision_to_history(decision)
            
            return decision
            
        except Exception as e:
            raise DecisionError(f"Failed to make task selection decision: {e}")
    
    def analyze_error_and_suggest_recovery(self, error_info: Dict[str, Any], project_state: Dict[str, Any]) -> DecisionResult:
        """
        Analyze error and suggest recovery strategy
        
        PARAMETERS:
        - error_info: Information about the error that occurred
        - project_state: Current state of the project
        
        RETURNS: Decision result with recovery strategy
        
        ANALYSIS AREAS:
        - Error type and severity
        - Root cause analysis
        - Impact on project timeline
        - Recovery options and risks
        """
        
        try:
            # Prepare decision context
            context = DecisionContext(
                decision_type=DecisionType.ERROR_ANALYSIS,
                project_state=project_state,
                available_options=self._generate_error_recovery_options(error_info),
                constraints=self._get_error_recovery_constraints(project_state),
                previous_decisions=self._get_recent_decisions(DecisionType.ERROR_ANALYSIS, limit=3),
                evidence_available=error_info,
                time_pressure=self._assess_error_urgency(error_info)
            )
            
            # Generate LLM prompt for error analysis
            prompt = self._generate_error_analysis_prompt(context, error_info)
            
            # Get LLM analysis
            llm_response = self._query_llm_for_decision(prompt, "error_analysis")
            
            # Parse response
            decision_data = self._parse_llm_decision_response(llm_response, context.available_options)
            
            # Create decision result
            decision = DecisionResult(
                decision_type=DecisionType.ERROR_ANALYSIS,
                selected_option=decision_data['selected_strategy'],
                confidence=ConfidenceLevel(decision_data['confidence']),
                reasoning=decision_data['reasoning'],
                alternative_options=decision_data.get('alternatives', []),
                risks_identified=decision_data.get('risks', []),
                mitigation_strategies=decision_data.get('mitigations', []),
                evidence_used=decision_data.get('evidence_used', []),
                follow_up_actions=decision_data.get('follow_up_actions', []),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Save decision to history
            self._save_decision_to_history(decision)
            
            return decision
            
        except Exception as e:
            raise DecisionError(f"Failed to analyze error and suggest recovery: {e}")
    
    def decide_phase_progression(self, current_phase: Dict[str, Any], completion_evidence: Dict[str, Any]) -> DecisionResult:
        """
        Decide whether to advance to next phase
        
        PARAMETERS:
        - current_phase: Information about current phase
        - completion_evidence: Evidence of phase completion
        
        RETURNS: Decision result on phase progression
        
        EVALUATION CRITERIA:
        - Completion of all phase requirements
        - Quality of deliverables
        - Risk assessment for next phase
        - Resource readiness
        """
        
        try:
            # Generate progression options
            progression_options = [
                {"action": "advance_phase", "target_phase": current_phase.get('next_phase')},
                {"action": "complete_remaining_tasks", "current_phase": current_phase},
                {"action": "improve_quality", "focus_areas": []},
                {"action": "gather_more_evidence", "missing_evidence": []}
            ]
            
            # Prepare decision context
            context = DecisionContext(
                decision_type=DecisionType.PHASE_PROGRESSION,
                project_state={"current_phase": current_phase},
                available_options=progression_options,
                constraints=self._get_phase_progression_constraints(current_phase),
                previous_decisions=self._get_recent_decisions(DecisionType.PHASE_PROGRESSION, limit=3),
                evidence_available=completion_evidence,
                time_pressure=self._assess_phase_time_pressure(current_phase)
            )
            
            # Generate LLM prompt
            prompt = self._generate_phase_progression_prompt(context, completion_evidence)
            
            # Get LLM decision
            llm_response = self._query_llm_for_decision(prompt, "phase_progression")
            
            # Parse response
            decision_data = self._parse_llm_decision_response(llm_response, progression_options)
            
            # Create decision result
            decision = DecisionResult(
                decision_type=DecisionType.PHASE_PROGRESSION,
                selected_option=decision_data['selected_action'],
                confidence=ConfidenceLevel(decision_data['confidence']),
                reasoning=decision_data['reasoning'],
                alternative_options=decision_data.get('alternatives', []),
                risks_identified=decision_data.get('risks', []),
                mitigation_strategies=decision_data.get('mitigations', []),
                evidence_used=decision_data.get('evidence_used', []),
                follow_up_actions=decision_data.get('follow_up_actions', []),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Save decision to history
            self._save_decision_to_history(decision)
            
            return decision
            
        except Exception as e:
            raise DecisionError(f"Failed to decide phase progression: {e}")
    
    def prioritize_context_files(self, available_files: List[str], task_info: Dict[str, Any], token_limit: int) -> DecisionResult:
        """
        Prioritize context files within token limit
        
        PARAMETERS:
        - available_files: List of available context files
        - task_info: Information about the task requiring context
        - token_limit: Maximum tokens available for context
        
        RETURNS: Decision result with prioritized file list
        
        PRIORITIZATION FACTORS:
        - Direct relevance to task
        - Cross-reference frequency
        - File freshness and accuracy
        - Implementation dependencies
        """
        
        try:
            # Prepare file options with metadata
            file_options = []
            for file_path in available_files:
                file_info = self._get_file_metadata(file_path)
                file_options.append({
                    "file_path": file_path,
                    "estimated_tokens": file_info.get('estimated_tokens', 1000),
                    "relevance_score": file_info.get('relevance_score', 0),
                    "last_modified": file_info.get('last_modified'),
                    "file_type": file_info.get('file_type'),
                    "cross_reference_count": file_info.get('cross_reference_count', 0)
                })
            
            # Prepare decision context
            context = DecisionContext(
                decision_type=DecisionType.CONTEXT_PRIORITIZATION,
                project_state={"token_limit": token_limit, "task": task_info},
                available_options=file_options,
                constraints={"max_tokens": token_limit, "min_files": 1},
                previous_decisions=self._get_recent_decisions(DecisionType.CONTEXT_PRIORITIZATION, limit=3),
                evidence_available={"task_requirements": task_info, "file_metadata": file_options},
                time_pressure="medium"
            )
            
            # Generate LLM prompt
            prompt = self._generate_context_prioritization_prompt(context)
            
            # Get LLM decision
            llm_response = self._query_llm_for_decision(prompt, "context_prioritization")
            
            # Parse response
            decision_data = self._parse_llm_decision_response(llm_response, file_options)
            
            # Create decision result
            decision = DecisionResult(
                decision_type=DecisionType.CONTEXT_PRIORITIZATION,
                selected_option={"prioritized_files": decision_data['selected_files']},
                confidence=ConfidenceLevel(decision_data['confidence']),
                reasoning=decision_data['reasoning'],
                alternative_options=decision_data.get('alternatives', []),
                risks_identified=decision_data.get('risks', []),
                mitigation_strategies=decision_data.get('mitigations', []),
                evidence_used=decision_data.get('evidence_used', []),
                follow_up_actions=decision_data.get('follow_up_actions', []),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Save decision to history
            self._save_decision_to_history(decision)
            
            return decision
            
        except Exception as e:
            raise DecisionError(f"Failed to prioritize context files: {e}")
    
    def _query_llm_for_decision(self, prompt: str, decision_type: str) -> str:
        """
        Query LLM for decision-making via Claude Code subagent
        
        PARAMETERS:
        - prompt: Formatted prompt for LLM
        - decision_type: Type of decision for logging
        
        RETURNS: LLM response text
        
        IMPLEMENTATION:
        - Uses Claude Code Task tool to spawn decision subagent
        - Implements timeout and error handling
        - Logs all interactions for debugging
        """
        
        try:
            # Create interaction log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            interaction_file = self.llm_interaction_dir / f"{decision_type}_{timestamp}.md"
            
            # Save prompt to interaction log
            with open(interaction_file, 'w') as f:
                f.write(f"# LLM Decision Interaction - {decision_type}\n\n")
                f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
                f.write(f"**Prompt**:\n```\n{prompt}\n```\n\n")
            
            # Query LLM via subprocess (simulating Claude Code Task tool integration)
            # In real implementation, this would use the Task tool
            result = self._simulate_llm_query(prompt, decision_type)
            
            # Log response
            with open(interaction_file, 'a') as f:
                f.write(f"**Response**:\n```\n{result}\n```\n\n")
            
            return result
            
        except Exception as e:
            raise DecisionError(f"Failed to query LLM for decision: {e}")
    
    def _simulate_llm_query(self, prompt: str, decision_type: str) -> str:
        """
        Simulate LLM query for pseudocode purposes
        
        In real implementation, this would use the Task tool to spawn
        a Claude Code subagent for decision-making
        """
        
        # This is pseudocode - in real implementation would use:
        # task_result = task_tool.spawn_agent("general-purpose", prompt)
        
        # For now, return structured response format
        if decision_type == "task_selection":
            return json.dumps({
                "selected_task": {"id": "task_001", "title": "Implement core feature"},
                "confidence": "high",
                "reasoning": "Task has highest priority and all dependencies are ready",
                "alternatives": [{"id": "task_002", "title": "Update documentation"}],
                "risks": ["Complex implementation may take longer than estimated"],
                "mitigations": ["Break task into smaller subtasks"],
                "evidence_used": ["dependency analysis", "priority matrix"],
                "follow_up_actions": ["Load context for implementation", "Run unit tests"]
            })
        
        elif decision_type == "error_analysis":
            return json.dumps({
                "selected_strategy": {"action": "retry_with_different_approach", "approach": "use_alternative_library"},
                "confidence": "medium",
                "reasoning": "Original library has known compatibility issues",
                "alternatives": [{"action": "skip_and_escalate", "reason": "too complex"}],
                "risks": ["Alternative library may have different API"],
                "mitigations": ["Test alternative thoroughly before committing"],
                "evidence_used": ["error logs", "library documentation"],
                "follow_up_actions": ["Research alternative library", "Update dependencies"]
            })
        
        elif decision_type == "phase_progression":
            return json.dumps({
                "selected_action": {"action": "advance_phase", "target_phase": "implementation"},
                "confidence": "high",
                "reasoning": "All phase requirements completed with evidence",
                "alternatives": [{"action": "improve_quality", "focus": "documentation"}],
                "risks": ["May discover issues in next phase"],
                "mitigations": ["Maintain ability to rollback changes"],
                "evidence_used": ["test results", "completion checklist"],
                "follow_up_actions": ["Archive current phase", "Initialize next phase"]
            })
        
        elif decision_type == "context_prioritization":
            return json.dumps({
                "selected_files": [
                    {"file_path": "src/core/main.py", "priority": 1, "estimated_tokens": 2000},
                    {"file_path": "docs/architecture.md", "priority": 2, "estimated_tokens": 1500},
                    {"file_path": "tests/test_core.py", "priority": 3, "estimated_tokens": 1000}
                ],
                "confidence": "high", 
                "reasoning": "Selected files provide complete context for task implementation",
                "alternatives": [{"include_additional": "src/utils/helpers.py"}],
                "risks": ["May need additional context during implementation"],
                "mitigations": ["Load additional files if needed"],
                "evidence_used": ["file relevance analysis", "token estimation"],
                "follow_up_actions": ["Monitor token usage during implementation"]
            })
        
        else:
            return json.dumps({
                "error": f"Unknown decision type: {decision_type}"
            })
    
    def _generate_task_selection_prompt(self, context: DecisionContext) -> str:
        """Generate LLM prompt for task selection decision"""
        
        prompt_parts = [
            "# Task Selection Decision",
            "",
            "You are an autonomous TDD system making a task selection decision.",
            "",
            "## Project State:",
            json.dumps(context.project_state, indent=2),
            "",
            "## Available Tasks:",
            json.dumps(context.available_options, indent=2),
            "",
            "## Constraints:",
            json.dumps(context.constraints, indent=2),
            "",
            "## Previous Decisions:",
            json.dumps(context.previous_decisions, indent=2),
            "",
            "## Evidence Available:",
            json.dumps(context.evidence_available, indent=2),
            "",
            "## Decision Required:",
            "Select the best task to execute next based on:",
            "- Task priority and dependencies",
            "- Resource availability and constraints", 
            "- Risk assessment and mitigation strategies",
            "- Project phase requirements",
            "- Learning from previous decisions",
            "",
            "## Response Format:",
            "Provide response as JSON with these exact fields:",
            "```json",
            "{",
            '  "selected_task": {"id": "...", "title": "...", "reasoning": "..."},',
            '  "confidence": "high|medium|low|uncertain",',
            '  "reasoning": "Detailed explanation of decision logic",',
            '  "alternatives": [{"id": "...", "title": "...", "why_not_selected": "..."}],',
            '  "risks": ["List of identified risks"],',
            '  "mitigations": ["List of mitigation strategies"],',
            '  "evidence_used": ["List of evidence that influenced decision"],',
            '  "follow_up_actions": ["List of immediate next steps"]',
            "}",
            "```"
        ]
        
        return '\n'.join(prompt_parts)
    
    def _generate_error_analysis_prompt(self, context: DecisionContext, error_info: Dict[str, Any]) -> str:
        """Generate LLM prompt for error analysis and recovery"""
        
        prompt_parts = [
            "# Error Analysis and Recovery Decision",
            "",
            "You are an autonomous TDD system analyzing an error and suggesting recovery.",
            "",
            "## Error Information:",
            json.dumps(error_info, indent=2),
            "",
            "## Project State:",
            json.dumps(context.project_state, indent=2),
            "",
            "## Recovery Options:",
            json.dumps(context.available_options, indent=2),
            "",
            "## Constraints:",
            json.dumps(context.constraints, indent=2),
            "",
            "## Previous Error Decisions:",
            json.dumps(context.previous_decisions, indent=2),
            "",
            "## Analysis Required:",
            "1. Analyze the root cause of the error",
            "2. Assess the impact on project timeline",
            "3. Evaluate recovery options and their risks",
            "4. Select the best recovery strategy",
            "",
            "## Anti-Fabrication Rules:",
            "- NO MOCK DATA: Recovery must work with real dependencies",
            "- NO SHORTCUTS: Address root cause, not just symptoms", 
            "- EVIDENCE REQUIRED: Recovery success must be verifiable",
            "",
            "## Response Format:",
            "Provide response as JSON with these exact fields:",
            "```json",
            "{",
            '  "selected_strategy": {"action": "...", "details": "...", "timeline": "..."},',
            '  "confidence": "high|medium|low|uncertain",',
            '  "reasoning": "Root cause analysis and recovery justification",',
            '  "alternatives": [{"action": "...", "why_not_selected": "..."}],',
            '  "risks": ["List of risks with selected strategy"],',
            '  "mitigations": ["List of risk mitigation approaches"],',
            '  "evidence_used": ["List of evidence analyzed"],',
            '  "follow_up_actions": ["List of verification steps"]',
            "}",
            "```"
        ]
        
        return '\n'.join(prompt_parts)
    
    def _generate_phase_progression_prompt(self, context: DecisionContext, completion_evidence: Dict[str, Any]) -> str:
        """Generate LLM prompt for phase progression decision"""
        
        prompt_parts = [
            "# Phase Progression Decision",
            "",
            "You are an autonomous TDD system deciding whether to advance to the next phase.",
            "",
            "## Current Phase:",
            json.dumps(context.project_state, indent=2),
            "",
            "## Completion Evidence:",
            json.dumps(completion_evidence, indent=2),
            "",
            "## Progression Options:",
            json.dumps(context.available_options, indent=2),
            "",
            "## Constraints:",
            json.dumps(context.constraints, indent=2),
            "",
            "## Success Criteria:",
            "- All phase requirements must be complete",
            "- Evidence must be comprehensive and verifiable", 
            "- Quality standards must be met",
            "- Dependencies for next phase must be ready",
            "",
            "## Anti-Fabrication Rules:",
            "- NO ADVANCEMENT WITHOUT EVIDENCE: Every requirement needs proof",
            "- NO PARTIAL COMPLETION: Phase must be fully done",
            "- REAL FUNCTIONALITY: Evidence must show actual working features",
            "",
            "## Response Format:",
            "Provide response as JSON with these exact fields:",
            "```json",
            "{",
            '  "selected_action": {"action": "advance_phase|complete_remaining|improve_quality|gather_evidence", "details": "..."},',
            '  "confidence": "high|medium|low|uncertain",',
            '  "reasoning": "Detailed analysis of completion status and readiness",',
            '  "alternatives": [{"action": "...", "why_not_selected": "..."}],',
            '  "risks": ["List of risks with advancing/not advancing"],',
            '  "mitigations": ["List of risk mitigation strategies"],',
            '  "evidence_used": ["List of evidence evaluated"],',
            '  "follow_up_actions": ["List of next steps based on decision"]',
            "}",
            "```"
        ]
        
        return '\n'.join(prompt_parts)
    
    def _generate_context_prioritization_prompt(self, context: DecisionContext) -> str:
        """Generate LLM prompt for context file prioritization"""
        
        prompt_parts = [
            "# Context File Prioritization Decision",
            "",
            "You are an autonomous TDD system prioritizing context files within token limits.",
            "",
            "## Task Information:",
            json.dumps(context.project_state.get('task', {}), indent=2),
            "",
            "## Available Files:",
            json.dumps(context.available_options, indent=2),
            "",
            "## Constraints:",
            json.dumps(context.constraints, indent=2),
            "",
            "## Prioritization Strategy:",
            "1. Include files directly required for task implementation",
            "2. Add files with high cross-reference frequency",
            "3. Include recent/modified files for current context",
            "4. Balance breadth vs depth within token limit",
            "",
            "## Selection Criteria:",
            "- Direct relevance to current task",
            "- Implementation dependencies (imports, etc.)",
            "- Documentation and planning references",
            "- Test files and validation context",
            "",
            "## Response Format:",
            "Provide response as JSON with these exact fields:",
            "```json",
            "{",
            '  "selected_files": [{"file_path": "...", "priority": 1, "estimated_tokens": 1000, "inclusion_reason": "..."}],',
            '  "confidence": "high|medium|low|uncertain",',
            '  "reasoning": "Logic for file selection and prioritization",',
            '  "alternatives": [{"file_path": "...", "why_not_included": "..."}],',
            '  "risks": ["List of risks with selected context"],',
            '  "mitigations": ["List of strategies if context insufficient"],',
            '  "evidence_used": ["List of factors considered"],',
            '  "follow_up_actions": ["List of context monitoring steps"]',
            "}",
            "```"
        ]
        
        return '\n'.join(prompt_parts)
    
    def _parse_llm_decision_response(self, llm_response: str, available_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse and validate LLM decision response"""
        
        try:
            # Extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise DecisionError("No JSON found in LLM response")
            
            json_str = llm_response[json_start:json_end]
            decision_data = json.loads(json_str)
            
            # Validate required fields exist
            required_fields = ['confidence', 'reasoning']
            for field in required_fields:
                if field not in decision_data:
                    raise DecisionError(f"Missing required field: {field}")
            
            # Validate confidence level
            if decision_data['confidence'] not in ['high', 'medium', 'low', 'uncertain']:
                decision_data['confidence'] = 'uncertain'
            
            return decision_data
            
        except json.JSONDecodeError as e:
            raise DecisionError(f"Invalid JSON in LLM response: {e}")
        except Exception as e:
            raise DecisionError(f"Failed to parse LLM response: {e}")
    
    def _save_decision_to_history(self, decision: DecisionResult) -> None:
        """Save decision to history for learning and analysis"""
        
        try:
            # Load existing history
            if self._decision_history is None:
                self._decision_history = self._load_decision_history()
            
            # Add new decision
            self._decision_history.append(decision)
            
            # Keep only recent decisions (last 100)
            if len(self._decision_history) > 100:
                self._decision_history = self._decision_history[-100:]
            
            # Save to disk
            history_data = [decision.to_dict() for decision in self._decision_history]
            self.json_utils.safe_save_json(self.decision_history_file, history_data, atomic=True)
            
        except Exception:
            # Don't fail if history save fails
            pass
    
    def _load_decision_history(self) -> List[DecisionResult]:
        """Load decision history from disk"""
        
        try:
            if not self.decision_history_file.exists():
                return []
            
            history_data = self.json_utils.safe_load_json(self.decision_history_file, default=[])
            return [DecisionResult.from_dict(item) for item in history_data]
            
        except Exception:
            return []
    
    def _get_recent_decisions(self, decision_type: DecisionType, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent decisions of specified type"""
        
        if self._decision_history is None:
            self._decision_history = self._load_decision_history()
        
        # Filter by type and get most recent
        filtered_decisions = [
            decision.to_dict() for decision in self._decision_history
            if decision.decision_type == decision_type
        ]
        
        return filtered_decisions[-limit:] if filtered_decisions else []
    
    def _initialize_decision_strategies(self) -> None:
        """Initialize decision-making strategies and patterns"""
        
        # Task selection strategies
        self.task_selection_strategies = {
            'priority_first': 'Select highest priority task first',
            'dependency_order': 'Follow dependency chain order',
            'risk_minimization': 'Select tasks with lowest risk',
            'resource_optimization': 'Select tasks matching available resources'
        }
        
        # Error recovery strategies  
        self.error_recovery_strategies = {
            'retry_with_backoff': 'Retry operation with exponential backoff',
            'alternative_approach': 'Try different implementation approach',
            'dependency_update': 'Update dependencies and retry',
            'escalate_to_human': 'Escalate complex issues to human',
            'skip_and_defer': 'Skip task and defer to later phase'
        }
        
        # Phase progression criteria
        self.phase_progression_criteria = {
            'all_tasks_complete': 'All phase tasks marked complete',
            'evidence_validated': 'All evidence validated and verified',
            'quality_gates_passed': 'Quality gates and tests passing',
            'dependencies_ready': 'Next phase dependencies available'
        }
    
    def _get_task_selection_constraints(self, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get constraints for task selection"""
        
        return {
            'max_parallel_tasks': 1,  # Autonomous system processes one task at a time
            'resource_availability': project_state.get('resources', {}),
            'time_constraints': project_state.get('deadlines', {}),
            'dependency_requirements': project_state.get('dependencies', {})
        }
    
    def _get_error_recovery_constraints(self, project_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get constraints for error recovery"""
        
        return {
            'max_retry_attempts': 3,
            'escalation_threshold': 'medium',
            'time_budget': project_state.get('time_remaining', 'unlimited'),
            'quality_requirements': project_state.get('quality_standards', {})
        }
    
    def _get_phase_progression_constraints(self, current_phase: Dict[str, Any]) -> Dict[str, Any]:
        """Get constraints for phase progression"""
        
        return {
            'evidence_completeness_threshold': 0.95,
            'quality_score_threshold': 0.8,
            'dependency_readiness_required': True,
            'rollback_capability_required': True
        }
    
    def _gather_task_evidence(self, available_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gather evidence for task selection decision"""
        
        evidence = {
            'task_count': len(available_tasks),
            'priority_distribution': {},
            'dependency_analysis': {},
            'resource_requirements': {}
        }
        
        # Analyze task priorities
        for task in available_tasks:
            priority = task.get('priority', 'medium')
            evidence['priority_distribution'][priority] = evidence['priority_distribution'].get(priority, 0) + 1
        
        return evidence
    
    def _generate_error_recovery_options(self, error_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate possible error recovery options"""
        
        error_type = error_info.get('type', 'unknown')
        
        options = []
        
        if error_type in ['dependency_missing', 'import_error']:
            options.extend([
                {'action': 'install_dependency', 'target': error_info.get('missing_item')},
                {'action': 'use_alternative', 'alternative': 'built-in library'},
                {'action': 'skip_and_defer', 'reason': 'dependency unavailable'}
            ])
        
        elif error_type in ['syntax_error', 'type_error']:
            options.extend([
                {'action': 'fix_syntax', 'approach': 'automated'},
                {'action': 'rewrite_section', 'scope': 'minimal'},
                {'action': 'escalate_to_debug', 'tools': ['detailed_analysis']}
            ])
        
        elif error_type in ['test_failure', 'assertion_error']:
            options.extend([
                {'action': 'fix_implementation', 'strategy': 'minimal_change'},
                {'action': 'update_test', 'justification': 'requirements_changed'},
                {'action': 'investigate_deeper', 'tools': ['debugging', 'logging']}
            ])
        
        else:
            options.extend([
                {'action': 'retry_operation', 'attempts': 1},
                {'action': 'escalate_to_human', 'reason': 'unknown_error'},
                {'action': 'skip_and_continue', 'impact': 'assess_later'}
            ])
        
        return options
    
    def _assess_time_pressure(self, project_state: Dict[str, Any]) -> str:
        """Assess time pressure for decision-making"""
        
        iterations = project_state.get('total_hook_iterations', 0)
        failures = project_state.get('consecutive_failures', 0)
        
        if failures > 3:
            return 'high'
        elif iterations > 30:
            return 'medium'
        else:
            return 'low'
    
    def _assess_error_urgency(self, error_info: Dict[str, Any]) -> str:
        """Assess urgency of error resolution"""
        
        error_type = error_info.get('type', 'unknown')
        severity = error_info.get('severity', 'medium')
        
        if severity == 'critical' or error_type in ['system_failure', 'data_corruption']:
            return 'high'
        elif severity == 'high' or error_type in ['test_failure', 'build_failure']:
            return 'medium'
        else:
            return 'low'
    
    def _assess_phase_time_pressure(self, current_phase: Dict[str, Any]) -> str:
        """Assess time pressure for phase progression"""
        
        completion_percentage = current_phase.get('completion_percentage', 0)
        time_spent = current_phase.get('time_spent_hours', 0)
        
        if completion_percentage > 0.9 and time_spent > 8:
            return 'high'  # Should advance soon
        elif completion_percentage > 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get metadata for context file prioritization"""
        
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                return {'estimated_tokens': 0, 'relevance_score': 0}
            
            file_size = path_obj.stat().st_size
            estimated_tokens = file_size // 4  # Rough estimation
            
            # Get file type
            file_type = path_obj.suffix or 'unknown'
            
            # Estimate relevance based on file type and name
            relevance_score = 0
            if 'test' in file_path.lower():
                relevance_score += 10
            if file_type == '.py':
                relevance_score += 20
            if file_type == '.md':
                relevance_score += 15
            if 'main' in file_path.lower() or 'core' in file_path.lower():
                relevance_score += 25
            
            return {
                'estimated_tokens': estimated_tokens,
                'relevance_score': relevance_score,
                'last_modified': path_obj.stat().st_mtime,
                'file_type': file_type,
                'cross_reference_count': 0  # Would be filled by cross-reference manager
            }
            
        except Exception:
            return {'estimated_tokens': 1000, 'relevance_score': 0}