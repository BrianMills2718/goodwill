# LLM Integration Patterns - Detailed Architecture

## Purpose
Detailed LLM integration architecture addressing the complexity gaps discovered during pseudocode implementation (Gap 6 from current_gaps_analysis.md).

## Problem Statement
**Original ADR-003**: Simple LLM-driven decomposition  
**Pseudocode Reality**: Complex subprocess execution, timeout handling, prompt engineering, context size management, structured response parsing

## Comprehensive LLM Integration Architecture

### Core LLM Integration Components

#### 1. Subprocess Execution Manager
```python
class LLMSubprocessManager:
    """Secure and robust subprocess execution for LLM integration"""
    
    def __init__(self, config: SubprocessConfig):
        self.config = config
        self.timeout_seconds = config.timeout_seconds  # Default: 300
        self.max_retries = config.max_retries  # Default: 3
        self.security_policy = SecurityPolicy(config.security_settings)
        
    def execute_llm_task(self, task_request: LLMTaskRequest) -> LLMTaskResult:
        """Execute LLM task via Claude Code Task tool with comprehensive error handling"""
        
        # Pre-execution validation
        validation_result = self._validate_task_request(task_request)
        if not validation_result.valid:
            return LLMTaskResult(
                success=False,
                error=f"Task validation failed: {validation_result.error}"
            )
        
        # Security check
        security_result = self.security_policy.validate_task(task_request)
        if not security_result.allowed:
            return LLMTaskResult(
                success=False,
                error=f"Security policy violation: {security_result.reason}"
            )
        
        # Execute with timeout and retry logic
        for attempt in range(self.max_retries):
            try:
                execution_result = self._execute_single_attempt(task_request, attempt)
                
                if execution_result.success:
                    return execution_result
                elif execution_result.should_retry:
                    continue
                else:
                    return execution_result
                    
            except TimeoutError:
                if attempt == self.max_retries - 1:
                    return LLMTaskResult(
                        success=False,
                        error=f"Task execution timeout after {self.max_retries} attempts"
                    )
                continue
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return LLMTaskResult(
                        success=False,
                        error=f"Task execution failed: {str(e)}"
                    )
                continue
        
        return LLMTaskResult(success=False, error="Max retries exceeded")
    
    def _execute_single_attempt(self, task_request: LLMTaskRequest, attempt: int) -> LLMTaskResult:
        """Execute single LLM task attempt with comprehensive monitoring"""
        
        start_time = time.time()
        
        try:
            # Prepare subprocess environment
            env = self._prepare_subprocess_environment()
            
            # Build command
            command = self._build_task_command(task_request)
            
            # Execute subprocess with timeout
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                timeout=self.timeout_seconds
            )
            
            stdout, stderr = process.communicate(timeout=self.timeout_seconds)
            
            execution_time = time.time() - start_time
            
            # Process results
            if process.returncode == 0:
                # Success - parse response
                response_result = self._parse_llm_response(stdout, task_request)
                
                return LLMTaskResult(
                    success=True,
                    response_data=response_result.data,
                    execution_time=execution_time,
                    attempt_number=attempt + 1,
                    raw_output=stdout
                )
            else:
                # Failure - analyze error
                error_analysis = self._analyze_execution_error(
                    process.returncode, stdout, stderr, task_request
                )
                
                return LLMTaskResult(
                    success=False,
                    error=error_analysis.error_message,
                    should_retry=error_analysis.retryable,
                    execution_time=execution_time,
                    attempt_number=attempt + 1,
                    raw_output=stdout,
                    raw_error=stderr
                )
                
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Task execution exceeded {self.timeout_seconds} seconds")
        except Exception as e:
            return LLMTaskResult(
                success=False,
                error=f"Subprocess execution error: {str(e)}",
                should_retry=True,
                execution_time=time.time() - start_time,
                attempt_number=attempt + 1
            )
```

#### 2. Prompt Engineering Framework
```python
class PromptEngineering:
    """Structured prompt engineering for autonomous TDD tasks"""
    
    def __init__(self, config: PromptConfig):
        self.config = config
        self.template_manager = PromptTemplateManager(config.template_dir)
        self.context_optimizer = ContextOptimizer(config.context_limits)
        
    def generate_task_decomposition_prompt(self, 
                                         high_level_task: str,
                                         context_data: Dict[str, Any],
                                         constraints: TaskConstraints) -> PromptRequest:
        """Generate optimized prompt for LLM task decomposition"""
        
        # Load base template
        base_template = self.template_manager.get_template("task_decomposition")
        
        # Optimize context for token limits
        optimized_context = self.context_optimizer.optimize_context(
            context_data, 
            max_tokens=constraints.max_context_tokens
        )
        
        # Build structured prompt
        prompt_sections = {
            "system_context": self._build_system_context(),
            "task_description": self._format_task_description(high_level_task),
            "project_context": optimized_context,
            "constraints": self._format_constraints(constraints),
            "output_format": self._get_output_format_spec("task_decomposition"),
            "examples": self._get_relevant_examples("task_decomposition")
        }
        
        # Validate prompt size
        estimated_tokens = self._estimate_prompt_tokens(prompt_sections)
        if estimated_tokens > constraints.max_total_tokens:
            # Reduce context and try again
            reduced_context = self.context_optimizer.reduce_context(
                optimized_context,
                target_reduction=estimated_tokens - constraints.max_total_tokens
            )
            prompt_sections["project_context"] = reduced_context
        
        # Generate final prompt
        final_prompt = base_template.render(**prompt_sections)
        
        return PromptRequest(
            prompt_text=final_prompt,
            expected_format="structured_json",
            max_response_tokens=constraints.max_response_tokens,
            temperature=0.1,  # Low for structured tasks
            metadata={
                "task_type": "task_decomposition",
                "context_tokens": self._estimate_tokens(optimized_context),
                "total_tokens": self._estimate_tokens(final_prompt)
            }
        )
    
    def generate_error_analysis_prompt(self,
                                     error_data: ErrorData,
                                     context_data: Dict[str, Any],
                                     previous_attempts: List[AttemptHistory]) -> PromptRequest:
        """Generate optimized prompt for LLM error analysis"""
        
        base_template = self.template_manager.get_template("error_analysis")
        
        # Analyze error patterns from previous attempts
        error_patterns = self._analyze_error_patterns(previous_attempts)
        
        # Build error-specific context
        error_context = self._build_error_context(error_data, error_patterns)
        
        # Optimize context for error analysis
        optimized_context = self.context_optimizer.optimize_for_error_analysis(
            context_data, error_context
        )
        
        prompt_sections = {
            "system_context": self._build_error_analysis_system_context(),
            "error_description": self._format_error_description(error_data),
            "error_context": error_context,
            "project_context": optimized_context,
            "previous_attempts": self._format_attempt_history(previous_attempts),
            "analysis_framework": self._get_error_analysis_framework(),
            "output_format": self._get_output_format_spec("error_analysis")
        }
        
        final_prompt = base_template.render(**prompt_sections)
        
        return PromptRequest(
            prompt_text=final_prompt,
            expected_format="structured_json",
            max_response_tokens=2000,  # Error analysis needs detailed response
            temperature=0.2,  # Slightly higher for creative problem solving
            metadata={
                "task_type": "error_analysis",
                "error_type": error_data.error_type,
                "attempt_count": len(previous_attempts)
            }
        )
    
    def generate_progress_assessment_prompt(self,
                                          current_state: ProjectState,
                                          completion_criteria: CompletionCriteria,
                                          evidence_data: EvidenceData) -> PromptRequest:
        """Generate optimized prompt for LLM progress assessment"""
        
        base_template = self.template_manager.get_template("progress_assessment")
        
        # Build evidence summary
        evidence_summary = self._summarize_evidence(evidence_data)
        
        # Build completion tracking
        completion_tracking = self._build_completion_tracking(
            current_state, completion_criteria
        )
        
        prompt_sections = {
            "system_context": self._build_assessment_system_context(),
            "current_state": self._format_current_state(current_state),
            "completion_criteria": self._format_completion_criteria(completion_criteria),
            "evidence_summary": evidence_summary,
            "completion_tracking": completion_tracking,
            "assessment_framework": self._get_assessment_framework(),
            "output_format": self._get_output_format_spec("progress_assessment")
        }
        
        final_prompt = base_template.render(**prompt_sections)
        
        return PromptRequest(
            prompt_text=final_prompt,
            expected_format="structured_json",
            max_response_tokens=1500,
            temperature=0.1,  # Low for objective assessment
            metadata={
                "task_type": "progress_assessment",
                "state_phase": current_state.current_phase,
                "criteria_count": len(completion_criteria.criteria)
            }
        )
```

#### 3. Context Size Management System
```python
class ContextOptimizer:
    """Intelligent context size management for LLM token limits"""
    
    def __init__(self, limits: ContextLimits):
        self.limits = limits
        self.max_context_tokens = limits.max_context_tokens  # 150K conservative
        self.max_total_tokens = limits.max_total_tokens      # 190K aggressive
        self.tokenizer = TokenEstimator()
        
    def optimize_context(self, 
                        context_data: Dict[str, Any], 
                        max_tokens: int) -> OptimizedContext:
        """Intelligently optimize context to fit within token limits"""
        
        # Estimate current context size
        current_tokens = self._estimate_context_tokens(context_data)
        
        if current_tokens <= max_tokens:
            # Context already fits
            return OptimizedContext(
                data=context_data,
                token_count=current_tokens,
                optimization_applied=False
            )
        
        # Apply optimization strategies
        optimization_result = self._apply_optimization_strategies(
            context_data, current_tokens, max_tokens
        )
        
        return optimization_result
    
    def _apply_optimization_strategies(self, 
                                     context_data: Dict[str, Any],
                                     current_tokens: int,
                                     target_tokens: int) -> OptimizedContext:
        """Apply multiple optimization strategies in priority order"""
        
        strategies = [
            self._strategy_remove_low_priority_files,
            self._strategy_truncate_large_files,
            self._strategy_extract_signatures_only,
            self._strategy_summarize_content,
            self._strategy_remove_comments_and_whitespace
        ]
        
        optimized_data = context_data.copy()
        tokens_saved = 0
        strategies_applied = []
        
        for strategy in strategies:
            if current_tokens - tokens_saved <= target_tokens:
                break
                
            strategy_result = strategy(optimized_data, target_tokens - (current_tokens - tokens_saved))
            
            if strategy_result.tokens_saved > 0:
                optimized_data = strategy_result.optimized_data
                tokens_saved += strategy_result.tokens_saved
                strategies_applied.append(strategy_result.strategy_name)
        
        final_tokens = current_tokens - tokens_saved
        
        return OptimizedContext(
            data=optimized_data,
            token_count=final_tokens,
            optimization_applied=True,
            strategies_applied=strategies_applied,
            tokens_saved=tokens_saved,
            fits_limit=final_tokens <= target_tokens
        )
    
    def _strategy_remove_low_priority_files(self, 
                                           context_data: Dict[str, Any], 
                                           tokens_needed: int) -> StrategyResult:
        """Remove files with low relevance to current task"""
        
        # Priority scoring based on file type, recency, and relevance
        file_priorities = self._calculate_file_priorities(context_data)
        
        # Sort by priority (lowest first for removal)
        sorted_files = sorted(file_priorities.items(), key=lambda x: x[1])
        
        optimized_data = context_data.copy()
        tokens_saved = 0
        files_removed = []
        
        for file_path, priority in sorted_files:
            if tokens_saved >= tokens_needed:
                break
                
            if priority < 0.3:  # Low priority threshold
                file_tokens = self._estimate_file_tokens(context_data[file_path])
                
                if file_path in optimized_data:
                    del optimized_data[file_path]
                    tokens_saved += file_tokens
                    files_removed.append(file_path)
        
        return StrategyResult(
            strategy_name="remove_low_priority_files",
            optimized_data=optimized_data,
            tokens_saved=tokens_saved,
            metadata={"files_removed": files_removed}
        )
    
    def _strategy_extract_signatures_only(self, 
                                         context_data: Dict[str, Any], 
                                         tokens_needed: int) -> StrategyResult:
        """Extract only function/class signatures from large files"""
        
        optimized_data = context_data.copy()
        tokens_saved = 0
        files_processed = []
        
        for file_path, file_content in context_data.items():
            if tokens_saved >= tokens_needed:
                break
                
            if self._is_code_file(file_path):
                original_tokens = self._estimate_file_tokens(file_content)
                
                if original_tokens > 1000:  # Only process large files
                    signature_content = self._extract_signatures(file_content, file_path)
                    signature_tokens = self._estimate_file_tokens(signature_content)
                    
                    if signature_tokens < original_tokens:
                        optimized_data[file_path] = signature_content
                        tokens_saved += (original_tokens - signature_tokens)
                        files_processed.append(file_path)
        
        return StrategyResult(
            strategy_name="extract_signatures_only",
            optimized_data=optimized_data,
            tokens_saved=tokens_saved,
            metadata={"files_processed": files_processed}
        )
```

#### 4. Structured Response Parsing System
```python
class ResponseParser:
    """Parse and validate structured LLM responses"""
    
    def __init__(self, config: ParsingConfig):
        self.config = config
        self.validators = {
            "task_decomposition": TaskDecompositionValidator(),
            "error_analysis": ErrorAnalysisValidator(),
            "progress_assessment": ProgressAssessmentValidator()
        }
    
    def parse_llm_response(self, 
                          raw_response: str, 
                          expected_format: str,
                          task_metadata: Dict[str, Any]) -> ParseResult:
        """Parse and validate LLM response according to expected format"""
        
        try:
            # Extract JSON from response (handles markdown code blocks)
            json_content = self._extract_json_content(raw_response)
            
            # Parse JSON
            parsed_data = json.loads(json_content)
            
            # Validate against expected schema
            validation_result = self._validate_response_schema(
                parsed_data, expected_format, task_metadata
            )
            
            if not validation_result.valid:
                return ParseResult(
                    success=False,
                    error=f"Schema validation failed: {validation_result.error}",
                    raw_response=raw_response
                )
            
            # Apply format-specific processing
            processed_data = self._process_format_specific_data(
                parsed_data, expected_format
            )
            
            return ParseResult(
                success=True,
                parsed_data=processed_data,
                raw_response=raw_response,
                validation_passed=True
            )
            
        except json.JSONDecodeError as e:
            # Attempt fallback parsing strategies
            fallback_result = self._attempt_fallback_parsing(raw_response, expected_format)
            
            if fallback_result.success:
                return fallback_result
            
            return ParseResult(
                success=False,
                error=f"JSON parsing failed: {str(e)}",
                raw_response=raw_response
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Response parsing error: {str(e)}",
                raw_response=raw_response
            )
    
    def _extract_json_content(self, raw_response: str) -> str:
        """Extract JSON content from various response formats"""
        
        # Strategy 1: Look for markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, raw_response, re.DOTALL)
        
        if matches:
            return matches[0]
        
        # Strategy 2: Look for bare JSON objects
        json_object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_object_pattern, raw_response, re.DOTALL)
        
        if matches:
            # Return the largest match (most likely to be complete)
            return max(matches, key=len)
        
        # Strategy 3: Try to find JSON-like content
        # Remove common prefixes and suffixes
        cleaned = raw_response.strip()
        for prefix in ["Here's the", "The result is", "Response:"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned
    
    def _validate_response_schema(self, 
                                 parsed_data: Dict[str, Any], 
                                 expected_format: str,
                                 task_metadata: Dict[str, Any]) -> ValidationResult:
        """Validate parsed response against expected schema"""
        
        if expected_format not in self.validators:
            return ValidationResult(
                valid=False,
                error=f"No validator for format: {expected_format}"
            )
        
        validator = self.validators[expected_format]
        return validator.validate(parsed_data, task_metadata)
```

## Security Architecture

### Subprocess Security Policy
```python
class SecurityPolicy:
    """Security policy for LLM subprocess execution"""
    
    def __init__(self, settings: SecuritySettings):
        self.settings = settings
        self.allowed_commands = settings.allowed_commands
        self.blocked_patterns = settings.blocked_patterns
        
    def validate_task(self, task_request: LLMTaskRequest) -> SecurityResult:
        """Validate task request against security policy"""
        
        # Check command whitelist
        if not self._is_command_allowed(task_request.command):
            return SecurityResult(
                allowed=False,
                reason=f"Command not in whitelist: {task_request.command}"
            )
        
        # Check for blocked patterns
        blocked_pattern = self._check_blocked_patterns(task_request)
        if blocked_pattern:
            return SecurityResult(
                allowed=False,
                reason=f"Blocked pattern detected: {blocked_pattern}"
            )
        
        # Validate arguments
        arg_validation = self._validate_arguments(task_request.arguments)
        if not arg_validation.valid:
            return SecurityResult(
                allowed=False,
                reason=f"Invalid arguments: {arg_validation.error}"
            )
        
        return SecurityResult(allowed=True)
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is in allowed whitelist"""
        return command in self.allowed_commands
    
    def _check_blocked_patterns(self, task_request: LLMTaskRequest) -> Optional[str]:
        """Check for security-sensitive patterns in task request"""
        
        content_to_check = f"{task_request.command} {task_request.arguments} {task_request.prompt}"
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, content_to_check, re.IGNORECASE):
                return pattern
        
        return None
```

## Error Handling and Recovery

### LLM Integration Error Categories
1. **Subprocess Errors**: Command execution failures, timeout, permissions
2. **Parsing Errors**: Invalid JSON, schema violations, format mismatches  
3. **Context Errors**: Token limit exceeded, context optimization failures
4. **Security Errors**: Policy violations, blocked commands, unsafe content

### Recovery Strategies
1. **Retry with Backoff**: Transient failures with exponential backoff
2. **Fallback Parsing**: Alternative parsing strategies for malformed responses
3. **Context Reduction**: Aggressive context optimization when token limits exceeded
4. **Graceful Degradation**: Continue with reduced LLM functionality

## Performance Optimization

### Execution Time Optimization
- **Parallel Execution**: Multiple LLM tasks in parallel where possible
- **Caching**: Cache LLM responses for identical requests
- **Context Reuse**: Reuse optimized context across similar tasks

### Token Efficiency
- **Smart Context Selection**: Prioritize most relevant context
- **Progressive Loading**: Load context incrementally as needed
- **Compression**: Use abbreviated formats for large context data

This detailed LLM integration architecture addresses all complexity gaps identified in the pseudocode analysis, providing robust subprocess execution, prompt engineering, context management, and response parsing required for autonomous LLM-driven development.