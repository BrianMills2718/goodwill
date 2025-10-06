#!/usr/bin/env python3
"""
DEPENDENCY GRAPH - Orchestrator Layer
Task dependency management and execution order calculation

RELATES_TO: ../persistence/state_manager.py, task_decomposer.py, ../utils/json_utils.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json

class DependencyType(Enum):
    """Types of dependencies between tasks"""
    HARD_DEPENDENCY = "hard_dependency"  # Must complete before this task can start
    SOFT_DEPENDENCY = "soft_dependency"  # Preferred to complete first, but not required
    PARALLEL_COMPATIBLE = "parallel_compatible"  # Can run in parallel
    RESOURCE_CONFLICT = "resource_conflict"  # Cannot run simultaneously due to resource conflicts
    ORDERING_PREFERENCE = "ordering_preference"  # Preferred order but flexible

class TaskStatus(Enum):
    """Status of tasks in dependency graph"""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskNode:
    """Node in the task dependency graph"""
    id: str
    title: str
    description: str
    task_type: str
    complexity: str
    estimated_effort_hours: float
    status: TaskStatus = TaskStatus.PENDING
    methodology_phase: str = ""
    
    # Dependency relationships
    hard_dependencies: Set[str] = field(default_factory=set)
    soft_dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)  # Tasks that depend on this one
    resource_conflicts: Set[str] = field(default_factory=set)
    
    # Execution metadata
    priority: int = 1  # 1=lowest, 10=highest
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
    last_updated: Optional[str] = None
    
    # Task data
    deliverables: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    evidence_requirements: Dict[str, Any] = field(default_factory=dict)
    context_files_needed: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'complexity': self.complexity,
            'estimated_effort_hours': self.estimated_effort_hours,
            'status': self.status.value,
            'methodology_phase': self.methodology_phase,
            'hard_dependencies': list(self.hard_dependencies),
            'soft_dependencies': list(self.soft_dependencies),
            'dependents': list(self.dependents),
            'resource_conflicts': list(self.resource_conflicts),
            'priority': self.priority,
            'start_time': self.start_time,
            'completion_time': self.completion_time,
            'last_updated': self.last_updated,
            'deliverables': self.deliverables,
            'acceptance_criteria': self.acceptance_criteria,
            'evidence_requirements': self.evidence_requirements,
            'context_files_needed': self.context_files_needed,
            'external_dependencies': self.external_dependencies
        }

@dataclass
class TaskDependencyGraph:
    """Complete task dependency graph for project"""
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependent_task_ids]
    
    # Graph metadata
    creation_time: str = ""
    last_updated: str = ""
    total_tasks: int = 0
    completed_tasks: int = 0
    
    # Current state
    current_ready_tasks: List[str] = field(default_factory=list)
    current_blocked_tasks: List[str] = field(default_factory=list)
    current_in_progress_tasks: List[str] = field(default_factory=list)
    
    # Execution order cache
    _topological_order_cache: Optional[List[str]] = None
    _critical_path_cache: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodes': {task_id: node.to_dict() for task_id, node in self.nodes.items()},
            'edges': self.edges,
            'creation_time': self.creation_time,
            'last_updated': self.last_updated,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'current_ready_tasks': self.current_ready_tasks,
            'current_blocked_tasks': self.current_blocked_tasks,
            'current_in_progress_tasks': self.current_in_progress_tasks
        }

class DependencyGraphError(Exception):
    """Raised when dependency graph operations fail"""
    pass

class TaskDependencyManager:
    """
    Task dependency graph management and execution order calculation
    
    ORCHESTRATOR COMPONENT: Manages task relationships and execution sequencing
    Calculates optimal execution order while respecting dependencies
    """
    
    def __init__(self, project_root: str):
        """
        Initialize task dependency manager
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes JSON utilities for safe graph persistence
        - Sets up dependency analysis configuration
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise DependencyGraphError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise DependencyGraphError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise DependencyGraphError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Dependency graph storage
        self.graph_file_path = self.project_root / '.claude' / 'task_graph.json'
        self.graph_backup_dir = self.project_root / '.claude' / 'task_graph_backups'
        
        # Current dependency graph
        self.current_graph: Optional[TaskDependencyGraph] = None
        
        # Graph analysis configuration
        self.max_parallel_tasks = 3
        self.priority_weight_factor = 0.3
        self.soft_dependency_weight = 0.1
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def create_dependency_graph(self, tasks: List['DecomposedTask']) -> TaskDependencyGraph:
        """
        Create complete dependency graph from decomposed tasks
        
        PARAMETERS:
        - tasks: List of decomposed tasks from task decomposer
        
        RETURNS: Complete dependency graph with all relationships established
        
        GRAPH CREATION PROCESS:
        1. Convert tasks to graph nodes
        2. Establish dependency relationships
        3. Validate graph for cycles and consistency
        4. Calculate execution order and priorities
        5. Save graph for persistence
        """
        
        try:
            self.logger.info(f"Creating dependency graph from {len(tasks)} tasks")
            
            # Initialize new graph
            graph = TaskDependencyGraph(
                creation_time=datetime.now(timezone.utc).isoformat(),
                last_updated=datetime.now(timezone.utc).isoformat(),
                total_tasks=len(tasks)
            )
            
            # Convert tasks to graph nodes
            for task in tasks:
                node = self._convert_task_to_node(task)
                graph.nodes[task.id] = node
            
            # Establish dependency relationships
            self._establish_dependencies(graph, tasks)
            
            # Build edge relationships for fast lookup
            self._build_edge_relationships(graph)
            
            # Validate graph consistency
            self._validate_graph_consistency(graph)
            
            # Calculate initial execution state
            self._update_graph_execution_state(graph)
            
            # Cache the graph
            self.current_graph = graph
            
            # Save graph to disk
            self._save_graph_to_disk(graph)
            
            self.logger.info("Dependency graph created successfully")
            return graph
            
        except Exception as e:
            self.logger.error(f"Dependency graph creation failed: {str(e)}")
            raise DependencyGraphError(f"Failed to create dependency graph: {str(e)}")
    
    def load_dependency_graph(self) -> Optional[TaskDependencyGraph]:
        """
        Load dependency graph from disk storage
        
        RETURNS: Loaded dependency graph or None if not found
        
        LOADING PROCESS:
        1. Check if graph file exists
        2. Load and validate JSON structure
        3. Reconstruct graph objects from data
        4. Validate graph consistency
        """
        
        try:
            if not self.graph_file_path.exists():
                self.logger.info("No existing dependency graph found")
                return None
            
            # Load graph data from disk
            graph_data = self.json_utils.load_json_file(str(self.graph_file_path))
            
            if not graph_data:
                self.logger.warning("Empty dependency graph file")
                return None
            
            # Reconstruct graph from data
            graph = self._reconstruct_graph_from_data(graph_data)
            
            # Validate loaded graph
            self._validate_graph_consistency(graph)
            
            # Update execution state
            self._update_graph_execution_state(graph)
            
            # Cache the graph
            self.current_graph = graph
            
            self.logger.info(f"Dependency graph loaded: {graph.total_tasks} tasks")
            return graph
            
        except Exception as e:
            self.logger.error(f"Failed to load dependency graph: {str(e)}")
            return None
    
    def get_ready_tasks(self, graph: Optional[TaskDependencyGraph] = None) -> List[TaskNode]:
        """
        Get all tasks that are ready for execution (dependencies satisfied)
        
        PARAMETERS:
        - graph: Dependency graph to analyze (uses current if None)
        
        RETURNS: List of tasks ready for execution, sorted by priority
        
        READY TASK CRITERIA:
        1. Task status is PENDING
        2. All hard dependencies are COMPLETED
        3. No resource conflicts with in-progress tasks
        4. External dependencies are available
        """
        
        if graph is None:
            graph = self.current_graph
        
        if not graph:
            return []
        
        ready_tasks = []
        in_progress_tasks = self._get_tasks_by_status(graph, TaskStatus.IN_PROGRESS)
        
        for task_id, node in graph.nodes.items():
            if self._is_task_ready(node, graph, in_progress_tasks):
                ready_tasks.append(node)
        
        # Sort by priority (highest first), then by soft dependency satisfaction
        ready_tasks.sort(key=lambda task: (
            -task.priority,  # Higher priority first
            -self._calculate_readiness_score(task, graph)  # Higher readiness score first
        ))
        
        # Update graph cache
        graph.current_ready_tasks = [task.id for task in ready_tasks]
        
        return ready_tasks
    
    def get_critical_path(self, graph: Optional[TaskDependencyGraph] = None) -> List[str]:
        """
        Calculate critical path through dependency graph
        
        PARAMETERS:
        - graph: Dependency graph to analyze (uses current if None)
        
        RETURNS: List of task IDs representing the critical path
        
        CRITICAL PATH CALCULATION:
        1. Find longest path through dependency graph
        2. Consider task effort estimates for path length
        3. Account for resource constraints and parallelization
        """
        
        if graph is None:
            graph = self.current_graph
        
        if not graph:
            return []
        
        # Use cached critical path if available
        if graph._critical_path_cache is not None:
            return graph._critical_path_cache
        
        try:
            # Calculate critical path using longest path algorithm
            critical_path = self._calculate_longest_path(graph)
            
            # Cache the result
            graph._critical_path_cache = critical_path
            
            return critical_path
            
        except Exception as e:
            self.logger.error(f"Critical path calculation failed: {str(e)}")
            return []
    
    def get_topological_order(self, graph: Optional[TaskDependencyGraph] = None) -> List[str]:
        """
        Get topological ordering of all tasks
        
        PARAMETERS:
        - graph: Dependency graph to analyze (uses current if None)
        
        RETURNS: List of task IDs in valid execution order
        
        TOPOLOGICAL SORT:
        1. Kahn's algorithm for dependency ordering
        2. Tie-breaking using priority and readiness scores
        3. Validation that all tasks are included
        """
        
        if graph is None:
            graph = self.current_graph
        
        if not graph:
            return []
        
        # Use cached topological order if available
        if graph._topological_order_cache is not None:
            return graph._topological_order_cache
        
        try:
            # Calculate topological order using Kahn's algorithm
            topological_order = self._kahn_topological_sort(graph)
            
            # Cache the result
            graph._topological_order_cache = topological_order
            
            return topological_order
            
        except Exception as e:
            self.logger.error(f"Topological sort failed: {str(e)}")
            return []
    
    def update_task_status(self, task_id: str, new_status: TaskStatus, 
                          completion_evidence: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update task status and recalculate graph state
        
        PARAMETERS:
        - task_id: ID of task to update
        - new_status: New status for the task
        - completion_evidence: Evidence of task completion (if completed)
        
        RETURNS: True if update successful, False otherwise
        
        STATUS UPDATE PROCESS:
        1. Validate status transition is valid
        2. Update task node with new status and timestamps
        3. Recalculate ready tasks and dependencies
        4. Save updated graph to disk
        """
        
        if not self.current_graph:
            self.logger.error("No current dependency graph available")
            return False
        
        if task_id not in self.current_graph.nodes:
            self.logger.error(f"Task {task_id} not found in dependency graph")
            return False
        
        try:
            task_node = self.current_graph.nodes[task_id]
            old_status = task_node.status
            
            # Validate status transition
            if not self._is_valid_status_transition(old_status, new_status):
                self.logger.error(f"Invalid status transition: {old_status} -> {new_status}")
                return False
            
            # Update task status and metadata
            task_node.status = new_status
            task_node.last_updated = datetime.now(timezone.utc).isoformat()
            
            if new_status == TaskStatus.IN_PROGRESS:
                task_node.start_time = datetime.now(timezone.utc).isoformat()
            elif new_status == TaskStatus.COMPLETED:
                task_node.completion_time = datetime.now(timezone.utc).isoformat()
                self.current_graph.completed_tasks += 1
            
            # Store completion evidence if provided
            if completion_evidence and new_status == TaskStatus.COMPLETED:
                # Evidence would be stored via evidence system
                pass
            
            # Recalculate graph execution state
            self._update_graph_execution_state(self.current_graph)
            
            # Invalidate cached orders
            self.current_graph._topological_order_cache = None
            self.current_graph._critical_path_cache = None
            
            # Save updated graph
            self._save_graph_to_disk(self.current_graph)
            
            self.logger.info(f"Task {task_id} status updated: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update task status: {str(e)}")
            return False
    
    def get_blocking_tasks(self, task_id: str, graph: Optional[TaskDependencyGraph] = None) -> List[str]:
        """
        Get all tasks that are blocking the specified task
        
        PARAMETERS:
        - task_id: ID of task to check blocking for
        - graph: Dependency graph to analyze (uses current if None)
        
        RETURNS: List of task IDs that must complete before this task can start
        """
        
        if graph is None:
            graph = self.current_graph
        
        if not graph or task_id not in graph.nodes:
            return []
        
        task_node = graph.nodes[task_id]
        blocking_tasks = []
        
        # Check hard dependencies
        for dep_id in task_node.hard_dependencies:
            if dep_id in graph.nodes:
                dep_node = graph.nodes[dep_id]
                if dep_node.status != TaskStatus.COMPLETED:
                    blocking_tasks.append(dep_id)
        
        return blocking_tasks
    
    def _convert_task_to_node(self, task: 'DecomposedTask') -> TaskNode:
        """Convert DecomposedTask to TaskNode"""
        
        node = TaskNode(
            id=task.id,
            title=task.title,
            description=task.description,
            task_type=task.task_type.value if hasattr(task.task_type, 'value') else str(task.task_type),
            complexity=task.complexity.value if hasattr(task.complexity, 'value') else str(task.complexity),
            estimated_effort_hours=task.estimated_effort_hours,
            methodology_phase=task.methodology_phase,
            deliverables=task.deliverables,
            acceptance_criteria=task.acceptance_criteria,
            evidence_requirements=task.evidence_requirements,
            context_files_needed=task.context_files_needed,
            external_dependencies=task.external_dependencies
        )
        
        # Set priority based on task type and complexity
        node.priority = self._calculate_task_priority(task)
        
        return node
    
    def _establish_dependencies(self, graph: TaskDependencyGraph, tasks: List['DecomposedTask']):
        """Establish dependency relationships between tasks"""
        
        # Build task ID to task mapping for lookup
        task_map = {task.id: task for task in tasks}
        
        for task in tasks:
            if task.id not in graph.nodes:
                continue
            
            node = graph.nodes[task.id]
            
            # Add hard dependencies from task specification
            for dep_id in task.dependencies:
                if dep_id in graph.nodes:
                    node.hard_dependencies.add(dep_id)
                    # Add reverse relationship
                    graph.nodes[dep_id].dependents.add(task.id)
            
            # Add methodology phase dependencies
            phase_deps = self._get_phase_dependencies(task.methodology_phase, task_map)
            for dep_id in phase_deps:
                if dep_id in graph.nodes and dep_id != task.id:
                    node.hard_dependencies.add(dep_id)
                    graph.nodes[dep_id].dependents.add(task.id)
            
            # Add resource conflict relationships
            conflicts = self._identify_resource_conflicts(task, tasks)
            for conflict_id in conflicts:
                if conflict_id in graph.nodes:
                    node.resource_conflicts.add(conflict_id)
                    graph.nodes[conflict_id].resource_conflicts.add(task.id)
    
    def _is_task_ready(self, task: TaskNode, graph: TaskDependencyGraph, 
                      in_progress_tasks: List[TaskNode]) -> bool:
        """Check if task is ready for execution"""
        
        # Task must be pending
        if task.status != TaskStatus.PENDING:
            return False
        
        # All hard dependencies must be completed
        for dep_id in task.hard_dependencies:
            if dep_id in graph.nodes:
                dep_node = graph.nodes[dep_id]
                if dep_node.status != TaskStatus.COMPLETED:
                    return False
        
        # Check for resource conflicts with in-progress tasks
        for in_progress_task in in_progress_tasks:
            if in_progress_task.id in task.resource_conflicts:
                return False
        
        # Check external dependencies (would integrate with external systems)
        if not self._external_dependencies_available(task):
            return False
        
        return True
    
    def _kahn_topological_sort(self, graph: TaskDependencyGraph) -> List[str]:
        """Perform topological sort using Kahn's algorithm"""
        
        # Calculate in-degrees
        in_degree = {task_id: 0 for task_id in graph.nodes}
        
        for task_id, node in graph.nodes.items():
            for dep_id in node.hard_dependencies:
                if dep_id in in_degree:
                    in_degree[task_id] += 1
        
        # Initialize queue with tasks having no dependencies
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        queue.sort(key=lambda tid: -graph.nodes[tid].priority)  # Sort by priority
        
        result = []
        
        while queue:
            # Select highest priority task
            current_task = queue.pop(0)
            result.append(current_task)
            
            # Update in-degrees of dependent tasks
            current_node = graph.nodes[current_task]
            for dependent_id in current_node.dependents:
                if dependent_id in in_degree:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)
                        # Re-sort queue by priority
                        queue.sort(key=lambda tid: -graph.nodes[tid].priority)
        
        # Check for cycles
        if len(result) != len(graph.nodes):
            remaining_tasks = [tid for tid in graph.nodes if tid not in result]
            raise DependencyGraphError(f"Circular dependency detected involving tasks: {remaining_tasks}")
        
        return result
    
    def _initialize_foundation_components(self):
        """Initialize required foundation components"""
        
        from ..utils.json_utils import JSONUtilities
        
        self.json_utils = JSONUtilities()
    
    def _save_graph_to_disk(self, graph: TaskDependencyGraph):
        """Save dependency graph to disk with backup"""
        
        try:
            # Create backup of existing graph
            if self.graph_file_path.exists():
                self._backup_existing_graph()
            
            # Ensure directory exists
            self.graph_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save graph data
            graph_data = graph.to_dict()
            self.json_utils.save_json_file(graph_data, str(self.graph_file_path))
            
            self.logger.debug("Dependency graph saved to disk")
            
        except Exception as e:
            self.logger.error(f"Failed to save dependency graph: {str(e)}")
            raise
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _calculate_task_priority(self, task: 'DecomposedTask') -> int:
        """Calculate task priority based on type and complexity"""
        
        # Base priority by task type
        type_priorities = {
            'overview': 9,
            'behavior_research': 8,
            'architecture_design': 7,
            'dependency_research': 7,
            'file_structure': 6,
            'pseudocode': 5,
            'implementation_planning': 4,
            'unit_test_creation': 4,
            'integration_test_creation': 3,
            'acceptance_test_creation': 3,
            'file_creation': 2,
            'implementation': 1,
            'testing': 1,
            'validation': 1
        }
        
        base_priority = type_priorities.get(task.task_type.value if hasattr(task.task_type, 'value') else str(task.task_type), 5)
        
        # Adjust for complexity
        complexity_adjustments = {
            'trivial': 0,
            'simple': 0,
            'moderate': 1,
            'complex': 2,
            'massive': 3
        }
        
        complexity_adj = complexity_adjustments.get(task.complexity.value if hasattr(task.complexity, 'value') else str(task.complexity), 1)
        
        return min(10, base_priority + complexity_adj)
    
    def _external_dependencies_available(self, task: TaskNode) -> bool:
        """Check if external dependencies are available"""
        # In real implementation, would check external systems
        return True
    
    def _get_tasks_by_status(self, graph: TaskDependencyGraph, status: TaskStatus) -> List[TaskNode]:
        """Get all tasks with specified status"""
        return [node for node in graph.nodes.values() if node.status == status]