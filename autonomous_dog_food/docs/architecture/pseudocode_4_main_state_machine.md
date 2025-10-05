# Pseudocode Part 4: Main State Machine Logic

## Overview
Define the core autonomous workflow that coordinates all system components and manages progression through methodology phases. This is the central orchestrator that turns the hook-based architecture into a coherent autonomous system.

## Context Size Management Strategy (Python Focus)

### Token Budget Management
```python
class ContextSizeManager:
    """Manages context loading within Claude Code token limits"""
    
    # Conservative approach: 150K tokens max (leave 50K buffer for output)
    MAX_CONTEXT_TOKENS = 150_000
    
    # Token estimation multipliers by file type
    TOKEN_MULTIPLIERS = {
        '.py': 1.2,    # Python keywords and symbols
        '.md': 0.8,    # Natural language text
        '.json': 0.6,  # Structured data
        '.yaml': 0.7,  # Configuration files
    }
    
    def estimate_file_tokens(self, file_path: str) -> int:
        """Conservative token estimation: ~4 chars per token"""
        file_size = Path(file_path).stat().st_size
        base_tokens = file_size // 4
        multiplier = self.TOKEN_MULTIPLIERS.get(Path(file_path).suffix, 1.0)
        return int(base_tokens * multiplier)
    
    def load_python_file_intelligently(self, file_path: str, max_tokens: int) -> str:
        """Load Python file with signature-first strategy"""
        
        if self.estimate_file_tokens(file_path) <= max_tokens:
            # File fits entirely - load full content
            with open(file_path, 'r') as f:
                return f.read()
        
        # File too large - use partial loading strategy
        return self._load_python_signatures_and_key_content(file_path, max_tokens)
    
    def _load_python_signatures_and_key_content(self, file_path: str, max_tokens: int) -> str:
        """Load most important parts of Python file within token limit"""
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse with AST to extract signatures
            tree = ast.parse(content)
            
            # Priority order for Python content:
            # 1. Imports (always include)
            # 2. Class and function signatures
            # 3. Docstrings
            # 4. Implementation (if space allows)
            
            result_lines = []
            
            # Add imports first
            imports = self._extract_imports(content)
            result_lines.extend(imports)
            
            # Add class/function signatures with docstrings
            signatures = self._extract_signatures_with_docstrings(tree, content)
            result_lines.extend(signatures)
            
            # Estimate tokens so far
            partial_content = '\n'.join(result_lines)
            current_tokens = len(partial_content) // 4
            
            # If space remains, add some implementation
            if current_tokens < max_tokens * 0.8:  # Leave 20% buffer
                remaining_tokens = int((max_tokens - current_tokens) * 0.8)
                implementation = self._extract_key_implementation(tree, content, remaining_tokens)
                result_lines.extend(implementation)
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            # Fallback: load first N lines within token limit
            return self._load_file_head(file_path, max_tokens)
```

## Main State Machine Architecture

### State Machine Controller (`src/orchestrator/workflow_manager.py`)

```python
class AutonomousWorkflowManager:
    """Main state machine that orchestrates autonomous TDD workflow"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
        # Load system components
        self.state_manager = StateManager(project_root)
        self.context_manager = ContextSizeManager()
        self.cross_ref_manager = CrossReferenceManager(project_root)
        self.task_decomposer = LLMTaskDecomposer()
        self.error_analyzer = LLMErrorAnalyzer()
        self.evidence_collector = EvidenceCollector()
        
        # State machine configuration
        self.max_iterations = 50  # Safety limit
        self.current_iteration = 0
        
    def execute_autonomous_hook_cycle(self) -> HookResult:
        """Main entry point called by Claude Code Stop hook"""
        
        try:
            # Safety check: prevent infinite loops
            if self.current_iteration >= self.max_iterations:
                return self._escalate_safety_limit_reached()
            
            self.current_iteration += 1
            
            # Load complete system state
            system_state = self.state_manager.load_complete_state()
            
            # Determine current state and next action
            next_action = self._analyze_current_state_and_decide_action(system_state)
            
            # Execute the determined action
            action_result = self._execute_action(next_action, system_state)
            
            # Update system state based on action results
            updated_state = self._update_state_after_action(system_state, action_result)
            
            # Save updated state
            self.state_manager.save_complete_state(updated_state)
            
            # Generate evidence for this hook cycle
            evidence = self._collect_evidence_for_hook_cycle(action_result)
            self.state_manager.save_evidence_record(evidence)
            
            # Update CLAUDE.md with current progress
            self._update_claude_md_progress(updated_state)
            
            # Return result to Claude Code
            return self._format_hook_result(action_result, updated_state)
            
        except Exception as e:
            # Handle any errors in autonomous execution
            return self._handle_autonomous_error(e, system_state if 'system_state' in locals() else None)
    
    def _analyze_current_state_and_decide_action(self, system_state: CompleteSystemState) -> ActionDecision:
        """Core state machine logic - analyze current state and decide next action"""
        
        # Check for blocking conditions first
        if system_state.project_state.blocking_status.is_blocked:
            return self._handle_blocked_state(system_state)
        
        # Determine current methodology phase and step
        current_phase = system_state.project_state.current_phase
        methodology_step = system_state.project_state.methodology_step
        
        # Phase-specific decision logic
        if current_phase == 1:  # Overview phase
            return self._handle_overview_phase(system_state)
        elif current_phase == 2:  # Architecture + Dependency Research
            return self._handle_architecture_phase(system_state)
        elif current_phase == 3:  # File Structure Creation
            return self._handle_file_structure_phase(system_state)
        elif current_phase == 4:  # Pseudocode Documentation
            return self._handle_pseudocode_phase(system_state)
        elif current_phase == 5:  # Implementation Plans + Unit Tests
            return self._handle_implementation_planning_phase(system_state)
        elif current_phase == 6:  # Integration Tests
            return self._handle_integration_testing_phase(system_state)
        elif current_phase == 7:  # Acceptance Tests
            return self._handle_acceptance_testing_phase(system_state)
        elif current_phase == 8:  # Create All Files & Cross-References
            return self._handle_file_creation_phase(system_state)
        elif current_phase == 9:  # Implementation
            return self._handle_implementation_phase(system_state)
        else:
            # Project complete or unknown phase
            return self._handle_completion_or_error_phase(system_state)
```

### Phase-Specific State Handlers

```python
def _handle_implementation_phase(self, system_state: CompleteSystemState) -> ActionDecision:
    """Handle autonomous implementation execution (Phase 9)"""
    
    task_graph = system_state.task_graph
    
    # Find next ready task to execute
    ready_tasks = self._get_ready_tasks(task_graph)
    
    if not ready_tasks:
        # No ready tasks - check if we're complete or blocked
        if self._all_tasks_complete(task_graph):
            return ActionDecision(
                action_type='advance_phase',
                target='project_complete',
                reasoning='All implementation tasks completed successfully'
            )
        else:
            # Tasks exist but none are ready - analyze blocking
            return self._analyze_task_blocking(task_graph, system_state)
    
    # Select highest priority ready task
    selected_task = self._select_highest_priority_task(ready_tasks)
    
    # Load context for the selected task
    context_bundle = self._load_task_context(selected_task, system_state)
    
    # Check if task requires external dependencies
    if selected_task.evidence_requirements.external_validation:
        dependency_status = self._validate_task_dependencies(selected_task, system_state.dependencies)
        if not dependency_status.all_available:
            return self._handle_missing_dependencies(selected_task, dependency_status)
    
    # Generate implementation instruction for Claude Code
    implementation_instruction = self._generate_implementation_instruction(
        selected_task, 
        context_bundle, 
        system_state
    )
    
    return ActionDecision(
        action_type='implement_task',
        target_task_id=selected_task.id,
        instruction=implementation_instruction,
        context_bundle=context_bundle,
        reasoning=f'Implementing task: {selected_task.title}'
    )

def _handle_file_creation_phase(self, system_state: CompleteSystemState) -> ActionDecision:
    """Handle creating all files and cross-references (Phase 8)"""
    
    # Check if file structure already created
    if self._file_structure_exists(system_state):
        return ActionDecision(
            action_type='advance_phase',
            target='implementation_phase',
            reasoning='File structure already exists, advancing to implementation'
        )
    
    # Generate complete file structure from task graph
    file_creation_plan = self._generate_file_creation_plan(system_state.task_graph)
    
    # Create all directories
    directory_creation = self._create_directory_structure(file_creation_plan)
    
    # Create all files with headers and cross-references
    file_creation = self._create_files_with_cross_references(file_creation_plan, system_state)
    
    # Update cross-reference map
    updated_cross_refs = self._update_cross_reference_map(system_state.cross_references, file_creation_plan)
    
    return ActionDecision(
        action_type='create_files',
        file_creation_plan=file_creation_plan,
        reasoning='Creating complete file structure and cross-references'
    )

def _handle_architecture_phase(self, system_state: CompleteSystemState) -> ActionDecision:
    """Handle architecture and dependency research (Phase 2)"""
    
    # Check what architecture work is complete
    architecture_status = self._assess_architecture_completeness(system_state)
    
    if not architecture_status.dependency_research_complete:
        # Need to research external dependencies
        return self._generate_dependency_research_action(system_state)
    
    elif not architecture_status.integration_tests_defined:
        # Need to define integration tests
        return self._generate_integration_test_definition_action(system_state)
    
    elif not architecture_status.system_architecture_complete:
        # Need to complete system architecture documentation
        return self._generate_architecture_documentation_action(system_state)
    
    else:
        # Architecture phase complete - advance to file structure
        return ActionDecision(
            action_type='advance_phase',
            target='file_structure_phase',
            reasoning='Architecture and dependency research complete'
        )
```

### Task Context Loading Integration

```python
def _load_task_context(self, task: Task, system_state: CompleteSystemState) -> ContextBundle:
    """Load relevant context for task execution within token limits"""
    
    # Start with task-specific files
    primary_files = task.file_targets + task.context_requirements
    
    # Expand context using cross-references (limited depth)
    context_files = self.cross_ref_manager.expand_context_for_task(
        task, 
        system_state.cross_references,
        max_depth=2
    )
    
    # Prioritize files by relevance
    prioritized_files = self._prioritize_context_files(context_files, task)
    
    # Load files within token limit using intelligent strategies
    context_bundle = ContextBundle()
    remaining_tokens = self.context_manager.MAX_CONTEXT_TOKENS
    
    for file_path in prioritized_files:
        if remaining_tokens <= 1000:  # Reserve minimum tokens for output
            break
        
        # Load file intelligently based on type
        if file_path.endswith('.py'):
            file_content = self.context_manager.load_python_file_intelligently(file_path, remaining_tokens)
        else:
            file_content = self.context_manager.load_generic_file_within_limit(file_path, remaining_tokens)
        
        if file_content:
            context_bundle.add_file(file_path, file_content)
            remaining_tokens -= len(file_content) // 4  # Rough token estimation
    
    # Add system context (configuration, current state summary)
    system_context = self._generate_system_context_summary(system_state, remaining_tokens // 2)
    context_bundle.add_system_context(system_context)
    
    return context_bundle

def _generate_implementation_instruction(self, task: Task, context_bundle: ContextBundle, system_state: CompleteSystemState) -> str:
    """Generate specific implementation instruction for Claude Code"""
    
    instruction_parts = []
    
    # Task description and requirements
    instruction_parts.append(f"TASK: {task.title}")
    instruction_parts.append(f"TYPE: {task.type}")
    instruction_parts.append(f"PRIORITY: {task.priority}")
    
    # Files to create or modify
    if task.file_targets:
        instruction_parts.append(f"TARGET FILES: {', '.join(task.file_targets)}")
    
    # Evidence requirements
    if task.evidence_requirements:
        evidence_reqs = []
        if task.evidence_requirements.test_passage:
            evidence_reqs.append("passing tests")
        if task.evidence_requirements.file_existence:
            evidence_reqs.append("file creation")
        if task.evidence_requirements.external_validation:
            evidence_reqs.append("external service integration")
        if task.evidence_requirements.integration_proof:
            evidence_reqs.append("end-to-end integration proof")
        
        instruction_parts.append(f"EVIDENCE REQUIRED: {', '.join(evidence_reqs)}")
    
    # Anti-fabrication reminders
    instruction_parts.append("ANTI-FABRICATION REQUIREMENTS:")
    instruction_parts.append("- NO HARDCODED VALUES: Use configuration/environment variables")
    instruction_parts.append("- NO MOCKING: Use real external dependencies only")
    instruction_parts.append("- DEFENSIVE PROGRAMMING: Validate inputs, handle edge cases")
    instruction_parts.append("- COMPREHENSIVE LOGGING: Log decisions and state changes")
    
    # Context files available
    if context_bundle.files:
        instruction_parts.append("AVAILABLE CONTEXT:")
        for file_path in context_bundle.files.keys():
            instruction_parts.append(f"- {file_path}")
    
    # Current system state summary
    instruction_parts.append(f"CURRENT PHASE: {system_state.project_state.current_phase}")
    instruction_parts.append(f"SESSION ITERATION: {self.current_iteration}")
    
    return '\n'.join(instruction_parts)
```

### Error Handling and Recovery

```python
def _handle_autonomous_error(self, error: Exception, system_state: CompleteSystemState = None) -> HookResult:
    """Handle errors in autonomous execution with recovery strategies"""
    
    error_context = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'iteration': self.current_iteration,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Analyze error type and determine recovery strategy
    if isinstance(error, StateConsistencyError):
        # State corruption - attempt recovery from backup
        return self._handle_state_corruption_error(error, error_context)
    
    elif isinstance(error, ExternalDependencyError):
        # Missing external dependencies - block and escalate
        return self._handle_dependency_error(error, error_context)
    
    elif isinstance(error, ContextSizeError):
        # Context too large - reduce context and retry
        return self._handle_context_size_error(error, error_context)
    
    elif isinstance(error, TaskExecutionError):
        # Task execution failed - analyze and decide retry vs escalate
        return self._handle_task_execution_error(error, error_context, system_state)
    
    else:
        # Unknown error - escalate to human
        return self._escalate_unknown_error(error, error_context)

def _escalate_safety_limit_reached(self) -> HookResult:
    """Handle case where maximum iteration limit reached"""
    
    return HookResult(
        status='blocked',
        message=f"SAFETY LIMIT REACHED: Maximum {self.max_iterations} hook iterations exceeded. "
                f"Manual intervention required to reset or increase limits.",
        blocking_reason='safety_limit_exceeded',
        escalation_required=True,
        user_action_needed="Review autonomous session progress and either reset iteration counter or increase safety limits in configuration."
    )
```

## Cross-References
```
# RELATES_TO: pseudocode_1_information_architecture.md (data structures used),
#            pseudocode_2_persistence_layer.md (state loading/saving),
#            pseudocode_3_cross_reference_logic.md (context loading strategies),
#            ../behavior_decisions.md (BDR-001: zero human intervention),
#            ../architecture_decisions.md (ADR-001: hook-only architecture)
```

## Next Foundation Component
After main state machine, the next component is **Decision Component Logic** - the LLM-powered analysis and decision-making that drives task selection, error analysis, and progress assessment.