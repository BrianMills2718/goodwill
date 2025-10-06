# LLM Task Integration - Analysis Layer Pseudocode
# Part of autonomous TDD system analysis components

"""
LLM Task Integration System

Handles integration with Claude Code's Task tool for LLM-driven analysis,
implementing the detailed patterns from docs/architecture/llm_integration_patterns.md
"""

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import subprocess
import time
import threading
from datetime import datetime, timedelta

# === Configuration and Data Classes ===

class TaskType(Enum):
    """Types of LLM tasks"""
    TASK_DECOMPOSITION = "task_decomposition"
    ERROR_ANALYSIS = "error_analysis"
    PROGRESS_ASSESSMENT = "progress_assessment"
    DECISION_ENHANCEMENT = "decision_enhancement"
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_REVIEW = "architecture_review"
    TEST_STRATEGY = "test_strategy"

@dataclass
class LLMTaskRequest:
    """Request for LLM task execution"""
    task_type: TaskType
    prompt: str
    context_data: Dict[str, Any]
    expected_format: str = "structured_json"
    max_response_tokens: int = 4000
    temperature: float = 0.1
    timeout_seconds: int = 300
    retry_count: int = 3
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMTaskResult:
    """Result of LLM task execution"""
    success: bool
    response_data: Optional[Dict[str, Any]] = None
    raw_response: str = ""
    execution_time: float = 0.0
    attempt_number: int = 1
    error: Optional[str] = None
    should_retry: bool = False
    raw_output: str = ""
    raw_error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PromptTemplate:
    """Template for LLM prompts"""
    template_name: str
    system_context: str
    user_prompt_template: str
    expected_response_format: Dict[str, Any]
    example_responses: List[Dict[str, Any]] = field(default_factory=list)
    parameter_schema: Dict[str, Any] = field(default_factory=dict)

# === LLM Task Integration Implementation ===

class LLMTaskIntegration:
    """
    Integration with Claude Code Task tool for LLM-driven analysis
    
    Implements the subprocess execution, prompt engineering, and response parsing
    patterns from docs/architecture/llm_integration_patterns.md
    """
    
    def __init__(self, config: LLMIntegrationConfig):
        self.config = config
        
        # Core components
        self.subprocess_manager = LLMSubprocessManager(config.subprocess_config)
        self.prompt_engineer = PromptEngineer(config.prompt_config)
        self.response_parser = ResponseParser(config.parsing_config)
        self.security_policy = SecurityPolicy(config.security_config)
        
        # Template management
        self.template_manager = PromptTemplateManager(config.template_directory)
        
        # Performance tracking
        self.performance_tracker = LLMPerformanceTracker()
        self.execution_history = []
        
        # Resource management
        self.active_tasks = {}
        self.task_queue = []
        self.max_concurrent_tasks = config.max_concurrent_tasks
    
    def execute_task_decomposition(self, high_level_task: str, context_data: Dict[str, Any]) -> LLMTaskResult:
        """Execute LLM-driven task decomposition"""
        
        # Generate optimized prompt
        prompt_request = self.prompt_engineer.generate_task_decomposition_prompt(
            high_level_task=high_level_task,
            context_data=context_data,
            constraints=TaskConstraints(
                max_context_tokens=self.config.max_context_tokens,
                max_total_tokens=self.config.max_total_tokens,
                max_response_tokens=2000
            )
        )
        
        # Create task request
        task_request = LLMTaskRequest(
            task_type=TaskType.TASK_DECOMPOSITION,
            prompt=prompt_request.prompt_text,
            context_data=context_data,
            expected_format="structured_json",
            max_response_tokens=2000,
            temperature=0.1,
            metadata={
                'high_level_task': high_level_task,
                'context_tokens': prompt_request.metadata.get('context_tokens', 0)
            }
        )
        
        # Execute task
        return self._execute_llm_task(task_request)
    
    def execute_error_analysis(self, error_data: Dict[str, Any], context_data: Dict[str, Any], previous_attempts: List[Dict[str, Any]]) -> LLMTaskResult:
        """Execute LLM-driven error analysis"""
        
        # Generate error analysis prompt
        prompt_request = self.prompt_engineer.generate_error_analysis_prompt(
            error_data=ErrorData(**error_data),
            context_data=context_data,
            previous_attempts=[AttemptHistory(**attempt) for attempt in previous_attempts]
        )
        
        # Create task request
        task_request = LLMTaskRequest(
            task_type=TaskType.ERROR_ANALYSIS,
            prompt=prompt_request.prompt_text,
            context_data=context_data,
            expected_format="structured_json",
            max_response_tokens=2000,
            temperature=0.2,  # Slightly higher for creative problem solving
            metadata={
                'error_type': error_data.get('error_type', 'unknown'),
                'attempt_count': len(previous_attempts)
            }
        )
        
        # Execute task
        return self._execute_llm_task(task_request)
    
    def execute_progress_assessment(self, current_state: Dict[str, Any], completion_criteria: Dict[str, Any], evidence_data: Dict[str, Any]) -> LLMTaskResult:
        """Execute LLM-driven progress assessment"""
        
        # Generate progress assessment prompt
        prompt_request = self.prompt_engineer.generate_progress_assessment_prompt(
            current_state=ProjectState(**current_state),
            completion_criteria=CompletionCriteria(**completion_criteria),
            evidence_data=EvidenceData(**evidence_data)
        )
        
        # Create task request
        task_request = LLMTaskRequest(
            task_type=TaskType.PROGRESS_ASSESSMENT,
            prompt=prompt_request.prompt_text,
            context_data={'current_state': current_state, 'criteria': completion_criteria, 'evidence': evidence_data},
            expected_format="structured_json",
            max_response_tokens=1500,
            temperature=0.1,  # Low for objective assessment
            metadata={
                'phase': current_state.get('current_phase', 'unknown'),
                'criteria_count': len(completion_criteria.get('criteria', []))
            }
        )
        
        # Execute task
        return self._execute_llm_task(task_request)
    
    def execute_decision_enhancement(self, decision_data: Dict[str, Any], context_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> LLMTaskResult:
        """Execute LLM-driven decision enhancement"""
        
        # Generate decision enhancement prompt
        prompt_request = self.prompt_engineer.generate_decision_enhancement_prompt(
            decision=DecisionData(**decision_data),
            context=context_data,
            analysis=SituationAnalysisData(**analysis_data)
        )
        
        # Create task request
        task_request = LLMTaskRequest(
            task_type=TaskType.DECISION_ENHANCEMENT,
            prompt=prompt_request.prompt_text,
            context_data=context_data,
            expected_format="structured_json",
            max_response_tokens=1800,
            temperature=0.15,  # Slightly higher for decision refinement
            metadata={
                'original_confidence': decision_data.get('confidence', 0.0),
                'decision_type': decision_data.get('decision_type', 'unknown')
            }
        )
        
        # Execute task
        return self._execute_llm_task(task_request)
    
    def _execute_llm_task(self, task_request: LLMTaskRequest) -> LLMTaskResult:
        """Execute LLM task with comprehensive error handling and monitoring"""
        
        # Track task start
        task_id = self._generate_task_id(task_request)
        execution_start = time.time()
        
        try:
            # Security validation
            security_result = self.security_policy.validate_task(task_request)
            if not security_result.allowed:
                return LLMTaskResult(
                    success=False,
                    error=f"Security policy violation: {security_result.reason}",
                    execution_time=time.time() - execution_start
                )
            
            # Resource availability check
            if not self._check_resource_availability(task_request):
                return LLMTaskResult(
                    success=False,
                    error="Insufficient resources for task execution",
                    execution_time=time.time() - execution_start,
                    should_retry=True
                )
            
            # Execute task with subprocess manager
            execution_result = self.subprocess_manager.execute_llm_task(task_request)
            
            if execution_result.success:
                # Parse and validate response
                parsing_result = self.response_parser.parse_llm_response(
                    raw_response=execution_result.raw_output,
                    expected_format=task_request.expected_format,
                    task_metadata=task_request.metadata
                )
                
                if parsing_result.success:
                    # Success - track performance and return result
                    execution_time = time.time() - execution_start
                    self.performance_tracker.track_successful_execution(task_request, execution_time)
                    
                    return LLMTaskResult(
                        success=True,
                        response_data=parsing_result.parsed_data,
                        raw_response=execution_result.raw_output,
                        execution_time=execution_time,
                        attempt_number=execution_result.attempt_number,
                        metadata={
                            'task_id': task_id,
                            'parsing_validated': True,
                            'performance_score': self.performance_tracker.calculate_performance_score(execution_time, task_request)
                        }
                    )
                else:
                    # Parsing failed
                    return LLMTaskResult(
                        success=False,
                        error=f"Response parsing failed: {parsing_result.error}",
                        raw_response=execution_result.raw_output,
                        execution_time=time.time() - execution_start,
                        should_retry=True
                    )
            else:
                # Execution failed
                return LLMTaskResult(
                    success=False,
                    error=execution_result.error,
                    raw_output=execution_result.raw_output,
                    raw_error=execution_result.raw_error,
                    execution_time=time.time() - execution_start,
                    should_retry=execution_result.should_retry,
                    attempt_number=execution_result.attempt_number
                )
                
        except Exception as e:
            # Unexpected error
            return LLMTaskResult(
                success=False,
                error=f"Unexpected error during LLM task execution: {str(e)}",
                execution_time=time.time() - execution_start,
                should_retry=False
            )
        finally:
            # Clean up resources
            self._cleanup_task_resources(task_id)
    
    def _check_resource_availability(self, task_request: LLMTaskRequest) -> bool:
        """Check if resources are available for task execution"""
        
        # Check concurrent task limit
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return False
        
        # Check memory constraints
        estimated_memory = self._estimate_task_memory_usage(task_request)
        if estimated_memory > self.config.max_memory_per_task:
            return False
        
        # Check timeout constraints
        if task_request.timeout_seconds > self.config.max_task_timeout:
            return False
        
        return True
    
    def _estimate_task_memory_usage(self, task_request: LLMTaskRequest) -> int:
        """Estimate memory usage for task"""
        
        # Base memory for subprocess
        base_memory = 50 * 1024 * 1024  # 50MB base
        
        # Memory for context data
        context_size = len(json.dumps(task_request.context_data))
        context_memory = context_size * 3  # Rough estimate
        
        # Memory for prompt
        prompt_memory = len(task_request.prompt) * 2
        
        total_estimated = base_memory + context_memory + prompt_memory
        return total_estimated
    
    def _generate_task_id(self, task_request: LLMTaskRequest) -> str:
        """Generate unique task ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        task_type = task_request.task_type.value
        return f"{task_type}_{timestamp}"
    
    def _cleanup_task_resources(self, task_id: str):
        """Clean up resources for completed task"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

# === Supporting Classes ===

class LLMSubprocessManager:
    """Manage subprocess execution for LLM tasks"""
    
    def __init__(self, config: SubprocessConfig):
        self.config = config
        self.timeout_seconds = config.timeout_seconds
        self.max_retries = config.max_retries
        self.security_policy = SecurityPolicy(config.security_settings)
    
    def execute_llm_task(self, task_request: LLMTaskRequest) -> LLMTaskResult:
        """Execute LLM task via subprocess with timeout and retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                execution_result = self._execute_single_attempt(task_request, attempt)
                
                if execution_result.success:
                    return execution_result
                elif execution_result.should_retry and attempt < self.max_retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return execution_result
                    
            except subprocess.TimeoutExpired:
                if attempt == self.max_retries - 1:
                    return LLMTaskResult(
                        success=False,
                        error=f"Task execution timeout after {self.max_retries} attempts",
                        should_retry=False
                    )
                continue
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return LLMTaskResult(
                        success=False,
                        error=f"Task execution failed: {str(e)}",
                        should_retry=False
                    )
                continue
        
        return LLMTaskResult(
            success=False,
            error="Max retries exceeded",
            should_retry=False
        )
    
    def _execute_single_attempt(self, task_request: LLMTaskRequest, attempt: int) -> LLMTaskResult:
        """Execute single attempt of LLM task"""
        
        start_time = time.time()
        
        try:
            # Prepare subprocess environment
            env = self._prepare_subprocess_environment()
            
            # Build Claude Code Task command
            command = self._build_task_command(task_request)
            
            # Execute subprocess
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                timeout=task_request.timeout_seconds
            )
            
            stdout, stderr = process.communicate(timeout=task_request.timeout_seconds)
            execution_time = time.time() - start_time
            
            if process.returncode == 0:
                # Success
                return LLMTaskResult(
                    success=True,
                    raw_output=stdout,
                    execution_time=execution_time,
                    attempt_number=attempt + 1
                )
            else:
                # Process failed
                error_analysis = self._analyze_execution_error(
                    process.returncode, stdout, stderr, task_request
                )
                
                return LLMTaskResult(
                    success=False,
                    error=error_analysis.error_message,
                    should_retry=error_analysis.retryable,
                    raw_output=stdout,
                    raw_error=stderr,
                    execution_time=execution_time,
                    attempt_number=attempt + 1
                )
                
        except subprocess.TimeoutExpired:
            raise  # Re-raise timeout for retry logic
        except Exception as e:
            return LLMTaskResult(
                success=False,
                error=f"Subprocess execution error: {str(e)}",
                should_retry=True,
                execution_time=time.time() - start_time,
                attempt_number=attempt + 1
            )
    
    def _build_task_command(self, task_request: LLMTaskRequest) -> List[str]:
        """Build command for Claude Code Task tool execution"""
        
        # This would build the actual command to invoke Claude Code's Task tool
        # The exact command structure would depend on Claude Code's implementation
        
        command = [
            "claude-code",  # Claude Code CLI
            "task",         # Task subcommand
            "--prompt", task_request.prompt,
            "--format", task_request.expected_format,
            "--max-tokens", str(task_request.max_response_tokens),
            "--temperature", str(task_request.temperature)
        ]
        
        # Add context data as JSON file if provided
        if task_request.context_data:
            context_file = self._write_context_to_temp_file(task_request.context_data)
            command.extend(["--context-file", str(context_file)])
        
        return command
    
    def _prepare_subprocess_environment(self) -> Dict[str, str]:
        """Prepare environment for subprocess execution"""
        
        env = os.environ.copy()
        
        # Add any required environment variables
        env['CLAUDE_CODE_TASK_MODE'] = 'autonomous'
        env['CLAUDE_CODE_OUTPUT_FORMAT'] = 'json'
        
        return env

class PromptEngineer:
    """Advanced prompt engineering for LLM tasks"""
    
    def __init__(self, config: PromptConfig):
        self.config = config
        self.template_manager = PromptTemplateManager(config.template_dir)
        self.context_optimizer = ContextOptimizer(config.context_limits)
    
    def generate_task_decomposition_prompt(self, high_level_task: str, context_data: Dict[str, Any], constraints: TaskConstraints) -> PromptRequest:
        """Generate optimized prompt for task decomposition"""
        
        # Implementation matches patterns from llm_integration_patterns.md
        # This would include context optimization, template rendering, etc.
        pass
    
    def generate_error_analysis_prompt(self, error_data: ErrorData, context_data: Dict[str, Any], previous_attempts: List[AttemptHistory]) -> PromptRequest:
        """Generate optimized prompt for error analysis"""
        
        # Implementation for error analysis prompt generation
        pass

class LLMPerformanceTracker:
    """Track LLM task performance and optimization opportunities"""
    
    def __init__(self):
        self.execution_history = []
        self.performance_metrics = {}
    
    def track_successful_execution(self, task_request: LLMTaskRequest, execution_time: float):
        """Track successful task execution for performance analysis"""
        
        self.execution_history.append({
            'task_type': task_request.task_type,
            'execution_time': execution_time,
            'timestamp': datetime.now(),
            'context_size': len(json.dumps(task_request.context_data)),
            'prompt_size': len(task_request.prompt),
            'success': True
        })
    
    def calculate_performance_score(self, execution_time: float, task_request: LLMTaskRequest) -> float:
        """Calculate performance score for task execution"""
        
        # Base score from execution time
        time_score = max(0, 1.0 - (execution_time / 60.0))  # Normalize to 60 seconds
        
        # Adjust for task complexity
        complexity_factor = self._assess_task_complexity(task_request)
        
        return time_score * complexity_factor
    
    def _assess_task_complexity(self, task_request: LLMTaskRequest) -> float:
        """Assess task complexity for performance scoring"""
        
        # Base complexity by task type
        complexity_scores = {
            TaskType.TASK_DECOMPOSITION: 0.8,
            TaskType.ERROR_ANALYSIS: 0.9,
            TaskType.PROGRESS_ASSESSMENT: 0.6,
            TaskType.DECISION_ENHANCEMENT: 0.7,
            TaskType.CODE_ANALYSIS: 0.9,
            TaskType.ARCHITECTURE_REVIEW: 1.0,
            TaskType.TEST_STRATEGY: 0.8
        }
        
        base_complexity = complexity_scores.get(task_request.task_type, 0.7)
        
        # Adjust for context size
        context_size = len(json.dumps(task_request.context_data))
        size_factor = min(1.0, context_size / 10000)  # Normalize to 10KB
        
        return base_complexity * (1.0 + size_factor * 0.3)

# === Data Classes for LLM Integration ===

@dataclass
class ErrorData:
    """Error data for LLM analysis"""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AttemptHistory:
    """History of previous attempts"""
    attempt_number: int
    action_taken: str
    result: str
    timestamp: datetime

@dataclass
class ProjectState:
    """Current project state for analysis"""
    current_phase: str
    completed_tasks: List[str]
    pending_tasks: List[str]
    last_test_results: Dict[str, Any]

@dataclass
class CompletionCriteria:
    """Completion criteria for progress assessment"""
    criteria: List[str]
    success_thresholds: Dict[str, Any]

@dataclass
class EvidenceData:
    """Evidence data for progress assessment"""
    test_results: Dict[str, Any]
    file_changes: List[str]
    performance_metrics: Dict[str, Any]

# This pseudocode implements comprehensive LLM task integration with Claude Code,
# including subprocess management, prompt engineering, response parsing, and
# performance tracking for autonomous TDD workflow execution.