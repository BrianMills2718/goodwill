#!/usr/bin/env python3
"""
TASK DECOMPOSER - Orchestrator Layer
LLM-driven task breakdown and dependency analysis

RELATES_TO: ../analysis/decision_engine.py, ../persistence/state_manager.py, ../context/cross_reference_manager.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

class TaskComplexity(Enum):
    """Task complexity levels for decomposition strategy"""
    TRIVIAL = "trivial"
    SIMPLE = "simple" 
    MODERATE = "moderate"
    COMPLEX = "complex"
    MASSIVE = "massive"

class TaskType(Enum):
    """Types of tasks in autonomous TDD workflow"""
    OVERVIEW = "overview"
    BEHAVIOR_RESEARCH = "behavior_research"
    ARCHITECTURE_DESIGN = "architecture_design"
    DEPENDENCY_RESEARCH = "dependency_research"
    FILE_STRUCTURE = "file_structure"
    PSEUDOCODE = "pseudocode"
    IMPLEMENTATION_PLANNING = "implementation_planning"
    UNIT_TEST_CREATION = "unit_test_creation"
    INTEGRATION_TEST_CREATION = "integration_test_creation"
    ACCEPTANCE_TEST_CREATION = "acceptance_test_creation"
    FILE_CREATION = "file_creation"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    VALIDATION = "validation"

@dataclass
class TaskDecompositionRequest:
    """Request for task decomposition from LLM"""
    target_description: str
    current_context: Dict[str, Any]
    constraints: Dict[str, Any]
    methodology_phase: str
    parent_task_id: Optional[str] = None
    decomposition_depth: int = 1
    max_subtasks: int = 10
    estimated_complexity: TaskComplexity = TaskComplexity.MODERATE

@dataclass 
class DecomposedTask:
    """Individual task result from decomposition"""
    id: str
    title: str
    description: str
    task_type: TaskType
    complexity: TaskComplexity
    estimated_effort_hours: float
    dependencies: List[str]
    prerequisites: List[str]
    deliverables: List[str]
    acceptance_criteria: List[str]
    evidence_requirements: Dict[str, Any]
    context_files_needed: List[str]
    external_dependencies: List[str]
    methodology_phase: str
    parent_task_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type.value,
            'complexity': self.complexity.value,
            'estimated_effort_hours': self.estimated_effort_hours,
            'dependencies': self.dependencies,
            'prerequisites': self.prerequisites,
            'deliverables': self.deliverables,
            'acceptance_criteria': self.acceptance_criteria,
            'evidence_requirements': self.evidence_requirements,
            'context_files_needed': self.context_files_needed,
            'external_dependencies': self.external_dependencies,
            'methodology_phase': self.methodology_phase,
            'parent_task_id': self.parent_task_id
        }

class TaskDecompositionError(Exception):
    """Raised when task decomposition fails"""
    pass

class LLMTaskDecomposer:
    """
    LLM-driven task decomposition for autonomous TDD workflow
    
    ORCHESTRATOR COMPONENT: Breaks down high-level requirements into actionable tasks
    Uses LLM intelligence to understand project requirements and create task graphs
    """
    
    def __init__(self, project_root: str):
        """
        Initialize LLM task decomposer
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes foundation components for context and decisions
        - Sets up task decomposition configuration
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise TaskDecompositionError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise TaskDecompositionError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise TaskDecompositionError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Task decomposition configuration
        self.max_decomposition_depth = 3
        self.max_tasks_per_level = 15
        self.min_task_effort_hours = 0.5
        self.max_task_effort_hours = 8.0
        
        # Task type patterns for methodology phases
        self.phase_task_patterns = self._initialize_phase_task_patterns()
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def decompose_project_into_tasks(self, project_description: str, 
                                   methodology_requirements: Dict[str, Any]) -> List[DecomposedTask]:
        """
        Main entry point: decompose entire project into task graph
        
        PARAMETERS:
        - project_description: High-level project description and goals
        - methodology_requirements: TDD methodology requirements and constraints
        
        RETURNS: Complete list of decomposed tasks following methodology phases
        
        DECOMPOSITION STRATEGY:
        1. Analyze project scope and complexity
        2. Map to TDD methodology phases
        3. Decompose each phase into specific tasks
        4. Establish dependencies between tasks
        5. Validate task graph completeness
        """
        
        try:
            self.logger.info("Starting project decomposition")
            
            # Analyze project scope and complexity
            project_analysis = self._analyze_project_scope(project_description, methodology_requirements)
            
            # Generate phase-based task breakdown
            all_tasks = []
            
            # Phase 1: Overview and Initial Analysis
            overview_tasks = self._decompose_overview_phase(project_analysis)
            all_tasks.extend(overview_tasks)
            
            # Phase 2: Behavior Research and Requirements
            behavior_tasks = self._decompose_behavior_phase(project_analysis)
            all_tasks.extend(behavior_tasks)
            
            # Phase 3: Architecture and Dependency Research
            architecture_tasks = self._decompose_architecture_phase(project_analysis)
            all_tasks.extend(architecture_tasks)
            
            # Phase 4: File Structure Creation
            file_structure_tasks = self._decompose_file_structure_phase(project_analysis)
            all_tasks.extend(file_structure_tasks)
            
            # Phase 5: Pseudocode Documentation
            pseudocode_tasks = self._decompose_pseudocode_phase(project_analysis)
            all_tasks.extend(pseudocode_tasks)
            
            # Phase 6: Implementation Planning and Unit Tests
            planning_tasks = self._decompose_implementation_planning_phase(project_analysis)
            all_tasks.extend(planning_tasks)
            
            # Phase 7: Integration Tests
            integration_tasks = self._decompose_integration_testing_phase(project_analysis)
            all_tasks.extend(integration_tasks)
            
            # Phase 8: Acceptance Tests
            acceptance_tasks = self._decompose_acceptance_testing_phase(project_analysis)
            all_tasks.extend(acceptance_tasks)
            
            # Phase 9: File Creation and Cross-References
            file_creation_tasks = self._decompose_file_creation_phase(project_analysis)
            all_tasks.extend(file_creation_tasks)
            
            # Phase 10: Implementation
            implementation_tasks = self._decompose_implementation_phase(project_analysis)
            all_tasks.extend(implementation_tasks)
            
            # Establish inter-task dependencies
            tasks_with_dependencies = self._establish_task_dependencies(all_tasks, project_analysis)
            
            # Validate task graph completeness and consistency
            validated_tasks = self._validate_task_graph_completeness(tasks_with_dependencies, project_analysis)
            
            self.logger.info(f"Project decomposition complete: {len(validated_tasks)} tasks created")
            
            return validated_tasks
            
        except Exception as e:
            self.logger.error(f"Project decomposition failed: {str(e)}")
            raise TaskDecompositionError(f"Failed to decompose project: {str(e)}")
    
    def decompose_task_further(self, task: DecomposedTask, 
                              additional_context: Dict[str, Any]) -> List[DecomposedTask]:
        """
        Decompose a specific task into smaller subtasks
        
        PARAMETERS:
        - task: Task to decompose further
        - additional_context: Additional context discovered during execution
        
        RETURNS: List of subtasks that together accomplish the parent task
        
        SUBTASK DECOMPOSITION:
        1. Analyze task complexity and scope
        2. Identify natural breakpoints and dependencies
        3. Create subtasks with clear deliverables
        4. Ensure subtasks maintain parent task's requirements
        """
        
        try:
            self.logger.info(f"Decomposing task: {task.id} - {task.title}")
            
            # Check if task should be decomposed further
            if not self._should_decompose_task(task, additional_context):
                return [task]  # Return original task if no further decomposition needed
            
            # Prepare decomposition request for LLM
            decomposition_request = TaskDecompositionRequest(
                target_description=f"Decompose task: {task.title}\n{task.description}",
                current_context=additional_context,
                constraints={
                    'max_subtasks': self.max_tasks_per_level,
                    'min_effort_hours': self.min_task_effort_hours,
                    'max_effort_hours': self.max_task_effort_hours,
                    'parent_requirements': task.acceptance_criteria,
                    'parent_deliverables': task.deliverables
                },
                methodology_phase=task.methodology_phase,
                parent_task_id=task.id,
                decomposition_depth=1,
                estimated_complexity=task.complexity
            )
            
            # Get LLM decomposition
            subtasks_data = self._query_llm_for_task_decomposition(decomposition_request)
            
            # Parse and validate subtasks
            subtasks = self._parse_decomposition_response(subtasks_data, task)
            
            # Ensure subtasks cover parent task requirements
            validated_subtasks = self._validate_subtask_coverage(subtasks, task)
            
            self.logger.info(f"Task decomposed into {len(validated_subtasks)} subtasks")
            
            return validated_subtasks
            
        except Exception as e:
            self.logger.error(f"Task decomposition failed for {task.id}: {str(e)}")
            # Return original task if decomposition fails
            return [task]
    
    def _analyze_project_scope(self, project_description: str, 
                              methodology_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project scope and complexity to inform decomposition
        
        SCOPE ANALYSIS:
        1. Extract key project components and requirements
        2. Estimate overall complexity and effort
        3. Identify major technical challenges
        4. Map to methodology phase requirements
        """
        
        # Prepare analysis request for LLM
        analysis_prompt = f"""
        Analyze this project for autonomous TDD development:
        
        PROJECT DESCRIPTION:
        {project_description}
        
        METHODOLOGY REQUIREMENTS:
        {json.dumps(methodology_requirements, indent=2)}
        
        Provide analysis in JSON format:
        {{
            "overall_complexity": "simple|moderate|complex|massive",
            "estimated_total_effort_hours": number,
            "major_components": ["component1", "component2", ...],
            "technical_challenges": ["challenge1", "challenge2", ...],
            "external_dependencies": ["dependency1", "dependency2", ...],
            "testing_complexity": "low|medium|high",
            "documentation_needs": ["doc1", "doc2", ...],
            "methodology_customizations": {{
                "requires_extended_pseudocode": boolean,
                "needs_integration_focus": boolean,
                "external_api_complexity": "low|medium|high"
            }}
        }}
        """
        
        try:
            # Query LLM for project analysis
            analysis_response = self.decision_engine._query_llm_for_decision(
                analysis_prompt, "project_scope_analysis"
            )
            
            import json
            analysis_data = json.loads(analysis_response)
            
            # Add calculated metrics
            analysis_data['phase_distribution'] = self._calculate_phase_effort_distribution(analysis_data)
            analysis_data['task_count_estimates'] = self._estimate_task_counts_per_phase(analysis_data)
            
            return analysis_data
            
        except Exception as e:
            self.logger.error(f"Project scope analysis failed: {str(e)}")
            # Return default analysis if LLM analysis fails
            return self._get_default_project_analysis()
    
    def _decompose_overview_phase(self, project_analysis: Dict[str, Any]) -> List[DecomposedTask]:
        """
        Decompose Phase 1: Overview and Initial Analysis
        
        OVERVIEW PHASE TASKS:
        1. Create project overview documentation
        2. Define success criteria and constraints
        3. Establish methodology approach
        """
        
        tasks = []
        
        # Task 1: Create project overview
        overview_task = DecomposedTask(
            id="overview_001",
            title="Create Project Overview Documentation",
            description="Document project goals, scope, and high-level requirements",
            task_type=TaskType.OVERVIEW,
            complexity=TaskComplexity.SIMPLE,
            estimated_effort_hours=2.0,
            dependencies=[],
            prerequisites=[],
            deliverables=["docs/overview.md"],
            acceptance_criteria=[
                "Project goals clearly defined",
                "Success criteria established",
                "Scope boundaries documented",
                "High-level requirements captured"
            ],
            evidence_requirements={
                "file_exists": "docs/overview.md",
                "content_validation": "overview_completeness_check",
                "stakeholder_review": False
            },
            context_files_needed=[],
            external_dependencies=[],
            methodology_phase="overview"
        )
        tasks.append(overview_task)
        
        # Task 2: Define success criteria
        success_criteria_task = DecomposedTask(
            id="overview_002", 
            title="Define Project Success Criteria",
            description="Establish measurable success criteria and validation approach",
            task_type=TaskType.OVERVIEW,
            complexity=TaskComplexity.SIMPLE,
            estimated_effort_hours=1.5,
            dependencies=["overview_001"],
            prerequisites=["Project goals documented"],
            deliverables=["docs/behavior/success_criteria.md"],
            acceptance_criteria=[
                "Success criteria are measurable",
                "Validation approach defined",
                "Quality standards established",
                "Performance requirements specified"
            ],
            evidence_requirements={
                "file_exists": "docs/behavior/success_criteria.md",
                "criteria_measurability": True,
                "validation_approach_complete": True
            },
            context_files_needed=["docs/overview.md"],
            external_dependencies=[],
            methodology_phase="overview"
        )
        tasks.append(success_criteria_task)
        
        return tasks
    
    def _decompose_architecture_phase(self, project_analysis: Dict[str, Any]) -> List[DecomposedTask]:
        """
        Decompose Phase 3: Architecture and Dependency Research
        
        ARCHITECTURE PHASE TASKS:
        1. Design system architecture
        2. Research external dependencies  
        3. Define integration points
        4. Document architecture decisions
        """
        
        tasks = []
        
        # Estimate number of architecture components based on complexity
        complexity = project_analysis.get('overall_complexity', 'moderate')
        major_components = project_analysis.get('major_components', [])
        
        if complexity in ['complex', 'massive'] or len(major_components) > 5:
            # Complex architecture needs multiple tasks
            
            # Task 1: System architecture design
            arch_design_task = DecomposedTask(
                id="architecture_001",
                title="Design System Architecture",
                description="Define overall system architecture and component relationships",
                task_type=TaskType.ARCHITECTURE_DESIGN,
                complexity=TaskComplexity.COMPLEX,
                estimated_effort_hours=4.0,
                dependencies=["behavior_002"],  # Depends on behavior research
                prerequisites=["Requirements analysis complete"],
                deliverables=[
                    "docs/architecture/system_overview.md",
                    "docs/architecture_decisions.md"
                ],
                acceptance_criteria=[
                    "Component architecture defined",
                    "Interface contracts specified",
                    "Data flow documented",
                    "Architecture decisions recorded"
                ],
                evidence_requirements={
                    "architecture_completeness": True,
                    "component_interfaces_defined": True,
                    "decision_records_complete": True
                },
                context_files_needed=["docs/behavior_decisions.md"],
                external_dependencies=[],
                methodology_phase="architecture_dependency_research"
            )
            tasks.append(arch_design_task)
            
            # Task 2: External dependency research
            dependency_research_task = DecomposedTask(
                id="architecture_002",
                title="Research External Dependencies",
                description="Identify and validate all external dependencies and APIs",
                task_type=TaskType.DEPENDENCY_RESEARCH,
                complexity=TaskComplexity.MODERATE,
                estimated_effort_hours=3.0,
                dependencies=["architecture_001"],
                prerequisites=["System architecture defined"],
                deliverables=[
                    "docs/dependencies/external_apis.md",
                    "docs/dependencies/integration_requirements.md"
                ],
                acceptance_criteria=[
                    "All external APIs identified",
                    "Integration requirements documented",
                    "Authentication needs defined",
                    "Rate limits and constraints captured"
                ],
                evidence_requirements={
                    "api_documentation_complete": True,
                    "integration_feasibility_validated": True,
                    "dependency_availability_confirmed": True
                },
                context_files_needed=["docs/architecture/system_overview.md"],
                external_dependencies=project_analysis.get('external_dependencies', []),
                methodology_phase="architecture_dependency_research"
            )
            tasks.append(dependency_research_task)
            
        else:
            # Simple architecture can be combined
            combined_arch_task = DecomposedTask(
                id="architecture_001",
                title="Design Architecture and Research Dependencies",
                description="Define system architecture and research external dependencies",
                task_type=TaskType.ARCHITECTURE_DESIGN,
                complexity=TaskComplexity.MODERATE,
                estimated_effort_hours=3.5,
                dependencies=["behavior_002"],
                prerequisites=["Requirements analysis complete"],
                deliverables=[
                    "docs/architecture/system_overview.md",
                    "docs/architecture_decisions.md",
                    "docs/dependencies/external_dependencies.md"
                ],
                acceptance_criteria=[
                    "System architecture documented",
                    "External dependencies identified",
                    "Integration approach defined",
                    "Architecture decisions recorded"
                ],
                evidence_requirements={
                    "architecture_completeness": True,
                    "dependency_research_complete": True,
                    "integration_approach_defined": True
                },
                context_files_needed=["docs/behavior_decisions.md"],
                external_dependencies=project_analysis.get('external_dependencies', []),
                methodology_phase="architecture_dependency_research"
            )
            tasks.append(combined_arch_task)
        
        return tasks
    
    def _decompose_implementation_phase(self, project_analysis: Dict[str, Any]) -> List[DecomposedTask]:
        """
        Decompose Phase 10: Implementation
        
        IMPLEMENTATION PHASE TASKS:
        - Based on pseudocode and file structure
        - Foundation-first implementation order
        - Component-by-component development
        """
        
        tasks = []
        major_components = project_analysis.get('major_components', [])
        
        # Implementation follows foundation-first order
        foundation_components = [
            "Configuration Management",
            "JSON Utilities", 
            "State Management",
            "Cross-Reference Management",
            "Decision Engine"
        ]
        
        task_id_counter = 1
        
        # Foundation layer implementation
        for component in foundation_components:
            impl_task = DecomposedTask(
                id=f"implementation_{task_id_counter:03d}",
                title=f"Implement {component}",
                description=f"Implement {component} component according to pseudocode specification",
                task_type=TaskType.IMPLEMENTATION,
                complexity=TaskComplexity.MODERATE,
                estimated_effort_hours=4.0,
                dependencies=[f"file_creation_{task_id_counter:03d}"],  # Depends on file creation
                prerequisites=["File structure created", "Pseudocode complete", "Unit tests written"],
                deliverables=[f"src/{component.lower().replace(' ', '_')}.py"],
                acceptance_criteria=[
                    "All unit tests pass",
                    "Implementation matches pseudocode",
                    "Defensive programming implemented",
                    "Error handling complete"
                ],
                evidence_requirements={
                    "unit_tests_pass": True,
                    "code_quality_check": True,
                    "pseudocode_compliance": True,
                    "defensive_programming_validated": True
                },
                context_files_needed=[
                    f"pseudo_src/{component.lower().replace(' ', '_')}.py",
                    f"tests/unit/test_{component.lower().replace(' ', '_')}.py"
                ],
                external_dependencies=[],
                methodology_phase="implementation"
            )
            tasks.append(impl_task)
            task_id_counter += 1
        
        # Orchestration layer implementation (depends on foundation)
        orchestration_components = [
            "Workflow Manager",
            "Task Decomposer", 
            "Dependency Graph",
            "Phase Manager"
        ]
        
        for component in orchestration_components:
            impl_task = DecomposedTask(
                id=f"implementation_{task_id_counter:03d}",
                title=f"Implement {component}",
                description=f"Implement {component} component with foundation dependencies",
                task_type=TaskType.IMPLEMENTATION,
                complexity=TaskComplexity.COMPLEX,
                estimated_effort_hours=5.0,
                dependencies=[f"implementation_{i:03d}" for i in range(1, 6)],  # Depends on foundation
                prerequisites=["Foundation components implemented", "Unit tests passing"],
                deliverables=[f"src/orchestrator/{component.lower().replace(' ', '_')}.py"],
                acceptance_criteria=[
                    "Integration with foundation components works",
                    "All unit tests pass",
                    "Cross-component integration validated",
                    "Error handling and recovery implemented"
                ],
                evidence_requirements={
                    "integration_tests_pass": True,
                    "foundation_integration_validated": True,
                    "error_handling_complete": True
                },
                context_files_needed=[
                    f"pseudo_src/orchestrator/{component.lower().replace(' ', '_')}.py",
                    f"tests/unit/test_orchestrator/test_{component.lower().replace(' ', '_')}.py"
                ],
                external_dependencies=[],
                methodology_phase="implementation"
            )
            tasks.append(impl_task)
            task_id_counter += 1
        
        return tasks
    
    def _query_llm_for_task_decomposition(self, request: TaskDecompositionRequest) -> str:
        """
        Query LLM for task decomposition using decision engine
        
        LLM PROMPT STRUCTURE:
        1. Context about current project and methodology phase
        2. Specific decomposition requirements and constraints
        3. Expected output format (JSON with task specifications)
        """
        
        decomposition_prompt = f"""
        Decompose the following task for autonomous TDD development:
        
        TARGET TASK:
        {request.target_description}
        
        CURRENT CONTEXT:
        {json.dumps(request.current_context, indent=2)}
        
        CONSTRAINTS:
        - Maximum subtasks: {request.max_subtasks}
        - Methodology phase: {request.methodology_phase}
        - Parent task: {request.parent_task_id or "None"}
        - Decomposition depth: {request.decomposition_depth}
        
        Provide decomposition in JSON format:
        {{
            "subtasks": [
                {{
                    "title": "Clear, specific task title",
                    "description": "Detailed description of what needs to be done",
                    "task_type": "overview|behavior_research|architecture_design|...",
                    "complexity": "trivial|simple|moderate|complex|massive", 
                    "estimated_effort_hours": number,
                    "dependencies": ["task_id1", "task_id2"],
                    "prerequisites": ["prerequisite1", "prerequisite2"],
                    "deliverables": ["file1.py", "doc1.md"],
                    "acceptance_criteria": ["criteria1", "criteria2"],
                    "context_files_needed": ["file1.py", "doc1.md"],
                    "external_dependencies": ["api1", "tool1"]
                }}
            ]
        }}
        """
        
        return self.decision_engine._query_llm_for_decision(
            decomposition_prompt, "task_decomposition"
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
    
    def _should_decompose_task(self, task: DecomposedTask, context: Dict[str, Any]) -> bool:
        """Determine if task should be decomposed further"""
        
        # Don't decompose if task is already simple
        if task.complexity in [TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE]:
            return False
        
        # Don't decompose if effort is within acceptable range
        if task.estimated_effort_hours <= self.max_task_effort_hours:
            return False
        
        # Decompose if task is complex and has multiple deliverables
        if (task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.MASSIVE] and 
            len(task.deliverables) > 2):
            return True
        
        # Check if context suggests decomposition is beneficial
        if context.get('force_decomposition', False):
            return True
        
        return False
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _get_default_project_analysis(self) -> Dict[str, Any]:
        """Return default project analysis if LLM analysis fails"""
        return {
            'overall_complexity': 'moderate',
            'estimated_total_effort_hours': 40.0,
            'major_components': ['core', 'api', 'storage'],
            'technical_challenges': ['integration', 'testing'],
            'external_dependencies': [],
            'testing_complexity': 'medium',
            'documentation_needs': ['api', 'setup'],
            'methodology_customizations': {
                'requires_extended_pseudocode': False,
                'needs_integration_focus': True,
                'external_api_complexity': 'medium'
            }
        }