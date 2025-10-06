# Component Dependency Resolution - Architecture Patterns

## Purpose
Resolve circular dependency issues identified during pseudocode implementation (Gaps 7-8 from current_gaps_analysis.md).

## Problem Statement
**Circular Dependencies Identified:**
```
orchestrator/workflow_manager.py → analysis/decision_engine.py
analysis/decision_engine.py → evidence/evidence_collector.py  
evidence/evidence_collector.py → orchestrator/task_decomposer.py
```

**Missing Resolution Patterns:**
- Dependency injection patterns
- Interface abstractions  
- Initialization order specification

## Dependency Resolution Architecture

### 1. Dependency Injection Framework
```python
# Core dependency injection container
class DIContainer:
    """Dependency injection container for autonomous TDD system"""
    
    def __init__(self):
        self._services = {}
        self._factories = {}
        self._singletons = {}
        self._initialization_order = []
        
    def register_service(self, interface: Type, implementation: Type, 
                        singleton: bool = True, dependencies: List[Type] = None):
        """Register service implementation with dependency specification"""
        
        self._services[interface] = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            singleton=singleton,
            dependencies=dependencies or []
        )
        
        if singleton:
            self._singletons[interface] = None
    
    def register_factory(self, interface: Type, factory_func: Callable):
        """Register factory function for complex service creation"""
        self._factories[interface] = factory_func
    
    def resolve(self, interface: Type) -> Any:
        """Resolve service instance with dependency injection"""
        
        # Check if singleton already exists
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]
        
        # Check for factory function
        if interface in self._factories:
            instance = self._factories[interface](self)
            if interface in self._singletons:
                self._singletons[interface] = instance
            return instance
        
        # Standard service resolution
        if interface not in self._services:
            raise DIException(f"Service not registered: {interface}")
        
        registration = self._services[interface]
        
        # Resolve dependencies first
        dependency_instances = {}
        for dep_interface in registration.dependencies:
            dependency_instances[dep_interface] = self.resolve(dep_interface)
        
        # Create instance
        instance = registration.implementation(**dependency_instances)
        
        if registration.singleton:
            self._singletons[interface] = instance
        
        return instance
    
    def initialize_all_services(self) -> InitializationResult:
        """Initialize all services in proper dependency order"""
        
        # Calculate initialization order
        initialization_order = self._calculate_initialization_order()
        
        initialization_results = []
        
        for service_interface in initialization_order:
            try:
                instance = self.resolve(service_interface)
                
                # Call initialization method if exists
                if hasattr(instance, 'initialize'):
                    init_result = instance.initialize()
                    initialization_results.append(ServiceInitResult(
                        service=service_interface,
                        success=True,
                        initialization_result=init_result
                    ))
                else:
                    initialization_results.append(ServiceInitResult(
                        service=service_interface,
                        success=True,
                        message="No initialization method"
                    ))
                    
            except Exception as e:
                initialization_results.append(ServiceInitResult(
                    service=service_interface,
                    success=False,
                    error=str(e)
                ))
                
                # Fail fast on initialization errors
                return InitializationResult(
                    success=False,
                    failed_service=service_interface,
                    error=str(e),
                    partial_results=initialization_results
                )
        
        return InitializationResult(
            success=True,
            initialization_results=initialization_results
        )
```

### 2. Interface Abstractions
```python
# Abstract interfaces to break circular dependencies

from abc import ABC, abstractmethod
from typing import Protocol

class ITaskDecomposer(Protocol):
    """Interface for task decomposition functionality"""
    
    def decompose_high_level_task(self, task: HighLevelTask) -> TaskDecompositionResult:
        """Decompose high-level task into actionable subtasks"""
        ...
    
    def validate_task_decomposition(self, decomposition: TaskDecomposition) -> ValidationResult:
        """Validate task decomposition is complete and feasible"""
        ...

class IDecisionEngine(Protocol):
    """Interface for autonomous decision making"""
    
    def analyze_current_situation(self, context: ExecutionContext) -> SituationAnalysis:
        """Analyze current execution context and determine next action"""
        ...
    
    def select_next_task(self, available_tasks: List[Task]) -> TaskSelectionResult:
        """Select next task to execute based on priority and dependencies"""
        ...

class IEvidenceCollector(Protocol):
    """Interface for evidence collection and validation"""
    
    def collect_task_evidence(self, task_execution: TaskExecution) -> EvidenceResult:
        """Collect evidence from task execution"""
        ...
    
    def validate_evidence_authenticity(self, evidence: Evidence) -> ValidationResult:
        """Validate evidence authenticity and prevent fabrication"""
        ...

class IWorkflowManager(Protocol):
    """Interface for workflow coordination"""
    
    def execute_autonomous_cycle(self) -> WorkflowResult:
        """Execute one autonomous workflow cycle"""
        ...
    
    def coordinate_phase_progression(self, current_phase: Phase) -> PhaseResult:
        """Coordinate progression through methodology phases"""
        ...

# Concrete implementations with dependency injection

class TaskDecomposer:
    """Concrete task decomposer with injected dependencies"""
    
    def __init__(self, decision_engine: IDecisionEngine, evidence_collector: IEvidenceCollector):
        self.decision_engine = decision_engine
        self.evidence_collector = evidence_collector
        self.llm_integration = None  # Injected later to avoid circular dependency
    
    def set_llm_integration(self, llm_integration):
        """Setter injection for LLM integration to avoid circular dependency"""
        self.llm_integration = llm_integration
    
    def decompose_high_level_task(self, task: HighLevelTask) -> TaskDecompositionResult:
        """Implement task decomposition with injected dependencies"""
        
        # Use decision engine for context analysis
        situation_analysis = self.decision_engine.analyze_current_situation(task.context)
        
        # Use LLM integration for decomposition (injected later)
        if self.llm_integration:
            llm_result = self.llm_integration.generate_task_decomposition(task, situation_analysis)
        else:
            # Fallback decomposition without LLM
            llm_result = self._fallback_decomposition(task)
        
        # Validate decomposition
        validation_result = self.validate_task_decomposition(llm_result.decomposition)
        
        return TaskDecompositionResult(
            decomposition=llm_result.decomposition,
            validation=validation_result,
            situation_analysis=situation_analysis
        )

class DecisionEngine:
    """Concrete decision engine with injected dependencies"""
    
    def __init__(self, evidence_collector: IEvidenceCollector):
        self.evidence_collector = evidence_collector
        self.task_decomposer = None  # Injected later to avoid circular dependency
    
    def set_task_decomposer(self, task_decomposer: ITaskDecomposer):
        """Setter injection for task decomposer to avoid circular dependency"""
        self.task_decomposer = task_decomposer
    
    def analyze_current_situation(self, context: ExecutionContext) -> SituationAnalysis:
        """Implement situation analysis with injected dependencies"""
        
        # Collect current evidence
        current_evidence = self.evidence_collector.collect_current_evidence(context)
        
        # Analyze situation based on evidence
        analysis = SituationAnalysis(
            context=context,
            evidence=current_evidence,
            completion_status=self._assess_completion_status(current_evidence),
            next_action_recommendations=self._generate_action_recommendations(context, current_evidence)
        )
        
        return analysis

class EvidenceCollector:
    """Concrete evidence collector with injected dependencies"""
    
    def __init__(self):
        self.workflow_manager = None  # Injected later to avoid circular dependency
        self.anti_fabrication = AntiFabricationDetector()
    
    def set_workflow_manager(self, workflow_manager: IWorkflowManager):
        """Setter injection for workflow manager to avoid circular dependency"""
        self.workflow_manager = workflow_manager
    
    def collect_task_evidence(self, task_execution: TaskExecution) -> EvidenceResult:
        """Implement evidence collection with injected dependencies"""
        
        # Collect evidence independently
        evidence_items = self._collect_evidence_items(task_execution)
        
        # Use workflow manager for coordination context (if available)
        coordination_context = None
        if self.workflow_manager:
            coordination_context = self.workflow_manager.get_coordination_context()
        
        # Validate evidence
        validation_result = self.anti_fabrication.validate_evidence_authenticity(
            evidence_items, coordination_context
        )
        
        return EvidenceResult(
            evidence_items=evidence_items,
            validation=validation_result,
            coordination_context=coordination_context
        )

class WorkflowManager:
    """Concrete workflow manager with injected dependencies"""
    
    def __init__(self, task_decomposer: ITaskDecomposer, decision_engine: IDecisionEngine):
        self.task_decomposer = task_decomposer
        self.decision_engine = decision_engine
        self.evidence_collector = None  # Injected later to avoid circular dependency
    
    def set_evidence_collector(self, evidence_collector: IEvidenceCollector):
        """Setter injection for evidence collector to avoid circular dependency"""
        self.evidence_collector = evidence_collector
```

### 3. Service Registration and Initialization Order
```python
def configure_dependency_injection() -> DIContainer:
    """Configure dependency injection container with proper service registration"""
    
    container = DIContainer()
    
    # Register core services with dependencies
    container.register_service(
        interface=IEvidenceCollector,
        implementation=EvidenceCollector,
        singleton=True,
        dependencies=[]  # No constructor dependencies
    )
    
    container.register_service(
        interface=IDecisionEngine,
        implementation=DecisionEngine,
        singleton=True,
        dependencies=[IEvidenceCollector]  # Constructor dependency only
    )
    
    container.register_service(
        interface=ITaskDecomposer,
        implementation=TaskDecomposer,
        singleton=True,
        dependencies=[IDecisionEngine, IEvidenceCollector]  # Constructor dependencies
    )
    
    container.register_service(
        interface=IWorkflowManager,
        implementation=WorkflowManager,
        singleton=True,
        dependencies=[ITaskDecomposer, IDecisionEngine]  # Constructor dependencies
    )
    
    # Register factory for complex initialization with circular dependencies
    container.register_factory(IAutonomousSystem, create_autonomous_system)
    
    return container

def create_autonomous_system(container: DIContainer) -> AutonomousSystem:
    """Factory function to create autonomous system with circular dependency resolution"""
    
    # Resolve all services
    evidence_collector = container.resolve(IEvidenceCollector)
    decision_engine = container.resolve(IDecisionEngine)
    task_decomposer = container.resolve(ITaskDecomposer)
    workflow_manager = container.resolve(IWorkflowManager)
    
    # Resolve circular dependencies with setter injection
    evidence_collector.set_workflow_manager(workflow_manager)
    decision_engine.set_task_decomposer(task_decomposer)
    task_decomposer.set_llm_integration(container.resolve(ILLMIntegration))
    workflow_manager.set_evidence_collector(evidence_collector)
    
    # Create autonomous system
    autonomous_system = AutonomousSystem(
        workflow_manager=workflow_manager,
        decision_engine=decision_engine,
        task_decomposer=task_decomposer,
        evidence_collector=evidence_collector
    )
    
    return autonomous_system

def initialize_autonomous_system() -> AutonomousSystem:
    """Initialize complete autonomous system with dependency resolution"""
    
    # Configure dependency injection
    container = configure_dependency_injection()
    
    # Initialize all services in proper order
    initialization_result = container.initialize_all_services()
    
    if not initialization_result.success:
        raise SystemInitializationError(
            f"Failed to initialize service: {initialization_result.failed_service}",
            error=initialization_result.error
        )
    
    # Create autonomous system with resolved dependencies
    autonomous_system = container.resolve(IAutonomousSystem)
    
    return autonomous_system
```

### 4. Initialization Order Specification
```python
class InitializationOrderCalculator:
    """Calculate safe initialization order for services with dependencies"""
    
    def __init__(self, service_registrations: Dict[Type, ServiceRegistration]):
        self.services = service_registrations
        self.dependency_graph = self._build_dependency_graph()
    
    def calculate_initialization_order(self) -> List[Type]:
        """Calculate initialization order using topological sort"""
        
        # Topological sort to resolve dependency order
        in_degree = {}
        for service in self.services:
            in_degree[service] = 0
        
        # Calculate in-degrees
        for service, registration in self.services.items():
            for dependency in registration.dependencies:
                if dependency in in_degree:
                    in_degree[service] += 1
        
        # Queue for services with no dependencies
        queue = [service for service, degree in in_degree.items() if degree == 0]
        initialization_order = []
        
        while queue:
            current_service = queue.pop(0)
            initialization_order.append(current_service)
            
            # Update in-degrees for dependent services
            for service, registration in self.services.items():
                if current_service in registration.dependencies:
                    in_degree[service] -= 1
                    if in_degree[service] == 0:
                        queue.append(service)
        
        # Check for circular dependencies
        if len(initialization_order) != len(self.services):
            remaining_services = [s for s in self.services if s not in initialization_order]
            raise CircularDependencyError(
                f"Circular dependency detected among services: {remaining_services}"
            )
        
        return initialization_order
    
    def _build_dependency_graph(self) -> Dict[Type, List[Type]]:
        """Build dependency graph for visualization and analysis"""
        
        graph = {}
        for service, registration in self.services.items():
            graph[service] = registration.dependencies.copy()
        
        return graph
    
    def detect_circular_dependencies(self) -> List[List[Type]]:
        """Detect all circular dependency cycles"""
        
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs_cycle_detection(node, path):
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if dfs_cycle_detection(neighbor, path):
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for service in self.services:
            if service not in visited:
                dfs_cycle_detection(service, [])
        
        return cycles
```

### 5. Hook Integration with Dependency Injection
```python
def autonomous_hook_with_dependency_injection():
    """Autonomous hook using dependency injection for clean architecture"""
    
    try:
        # Initialize autonomous system with dependency resolution
        autonomous_system = initialize_autonomous_system()
        
        # Execute autonomous cycle
        cycle_result = autonomous_system.execute_cycle()
        
        return HookResult(
            status="success" if cycle_result.success else "error",
            message=cycle_result.message,
            next_instruction=cycle_result.next_instruction
        )
        
    except CircularDependencyError as e:
        return HookResult(
            status="error",
            message=f"Circular dependency error: {str(e)}",
            requires_fix=True
        )
    except SystemInitializationError as e:
        return HookResult(
            status="error", 
            message=f"System initialization failed: {str(e)}",
            requires_fix=True
        )
    except Exception as e:
        return HookResult(
            status="error",
            message=f"Autonomous system error: {str(e)}",
            requires_investigation=True
        )
```

## Benefits of This Architecture

### 1. Circular Dependency Resolution
- **Interface abstractions** break compile-time circular dependencies
- **Dependency injection** enables runtime composition without circular references
- **Setter injection** resolves circular dependencies safely after construction

### 2. Clean Architecture
- **Single Responsibility**: Each component has clear, focused responsibilities
- **Dependency Inversion**: Components depend on abstractions, not concretions
- **Open/Closed Principle**: Easy to extend without modifying existing code

### 3. Testability
- **Mockable interfaces** enable unit testing in isolation
- **Dependency injection** allows test doubles to be injected
- **Clear separation** makes component boundaries explicit

### 4. Maintainability
- **Explicit dependencies** make component relationships clear
- **Initialization order** prevents runtime dependency issues
- **Error handling** provides clear failure modes and recovery

This dependency resolution architecture completely eliminates the circular dependency issues identified in gaps 7-8, providing a clean, testable, and maintainable foundation for the autonomous TDD system.