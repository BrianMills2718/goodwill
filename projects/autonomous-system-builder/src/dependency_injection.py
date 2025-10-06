# Dependency Injection System
"""
Dependency injection container and service registration for the autonomous TDD system.

Implements the dependency resolution patterns from 
docs/architecture/dependency_resolution_patterns.md
"""

from typing import Dict, Type, Any, List, Callable, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
import inspect
from datetime import datetime

# === Dependency Injection Interfaces ===

class ITaskDecomposer(Protocol):
    """Interface for task decomposition functionality"""
    
    def decompose_high_level_task(self, task: Any) -> Any:
        """Decompose high-level task into actionable subtasks"""
        ...

class IDecisionEngine(Protocol):
    """Interface for autonomous decision making"""
    
    def make_autonomous_decision(self, context: Any) -> Any:
        """Make autonomous decision based on context"""
        ...

class IEvidenceCollector(Protocol):
    """Interface for evidence collection and validation"""
    
    def collect_task_evidence(self, task_execution: Any) -> Any:
        """Collect evidence from task execution"""
        ...

class IWorkflowManager(Protocol):
    """Interface for workflow coordination"""
    
    def execute_autonomous_cycle(self) -> Any:
        """Execute one autonomous workflow cycle"""
        ...

class IContextLoader(Protocol):
    """Interface for context loading and management"""
    
    def load_context_for_task(self, task: Any) -> Any:
        """Load optimized context for task"""
        ...

class ILLMIntegration(Protocol):
    """Interface for LLM task integration"""
    
    def execute_task_decomposition(self, task: str, context: Dict[str, Any]) -> Any:
        """Execute LLM-driven task decomposition"""
        ...

# === Dependency Injection Implementation ===

class ServiceLifetime(Enum):
    """Service lifetime management"""
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Single instance
    SCOPED = "scoped"       # Instance per scope

@dataclass
class ServiceRegistration:
    """Service registration information"""
    interface: Type
    implementation: Type
    lifetime: ServiceLifetime
    dependencies: List[Type]
    factory_func: Optional[Callable] = None
    instance: Optional[Any] = None

@dataclass
class ServiceInitResult:
    """Result of service initialization"""
    service: Type
    success: bool
    initialization_result: Optional[Any] = None
    message: str = ""
    error: Optional[str] = None

@dataclass
class InitializationResult:
    """Result of complete service initialization"""
    success: bool
    initialization_results: List[ServiceInitResult]
    failed_service: Optional[Type] = None
    error: Optional[str] = None
    partial_results: List[ServiceInitResult] = None

class DIContainer:
    """
    Dependency injection container for autonomous TDD system
    
    Implements the DI patterns from docs/architecture/dependency_resolution_patterns.md
    with circular dependency resolution and initialization order management.
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceRegistration] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._initialization_order: List[Type] = []
        self._is_initialized = False
    
    def register_service(
        self, 
        interface: Type, 
        implementation: Type,
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
        dependencies: Optional[List[Type]] = None
    ):
        """
        Register service implementation with dependency specification
        
        Args:
            interface: Service interface type
            implementation: Concrete implementation type
            lifetime: Service lifetime management
            dependencies: List of constructor dependencies
        """
        
        dependencies = dependencies or []
        
        # Validate implementation implements interface
        if not issubclass(implementation, interface) and not self._implements_protocol(implementation, interface):
            # For protocols, we'll trust the registration
            pass
        
        registration = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            lifetime=lifetime,
            dependencies=dependencies
        )
        
        self._services[interface] = registration
    
    def register_factory(self, interface: Type, factory_func: Callable, lifetime: ServiceLifetime = ServiceLifetime.SINGLETON):
        """
        Register factory function for complex service creation
        
        Args:
            interface: Service interface type
            factory_func: Factory function that takes DIContainer as parameter
            lifetime: Service lifetime management
        """
        
        registration = ServiceRegistration(
            interface=interface,
            implementation=type(None),  # Placeholder
            lifetime=lifetime,
            dependencies=[],
            factory_func=factory_func
        )
        
        self._services[interface] = registration
    
    def resolve(self, interface: Type) -> Any:
        """
        Resolve service instance with dependency injection
        
        Args:
            interface: Service interface to resolve
            
        Returns:
            Service instance
        """
        
        if interface not in self._services:
            raise DIException(f"Service not registered: {interface}")
        
        registration = self._services[interface]
        
        # Check for existing singleton
        if registration.lifetime == ServiceLifetime.SINGLETON and interface in self._singletons:
            return self._singletons[interface]
        
        # Check for existing scoped instance
        if registration.lifetime == ServiceLifetime.SCOPED and interface in self._scoped_instances:
            return self._scoped_instances[interface]
        
        # Create new instance
        instance = self._create_instance(registration)
        
        # Store instance based on lifetime
        if registration.lifetime == ServiceLifetime.SINGLETON:
            self._singletons[interface] = instance
        elif registration.lifetime == ServiceLifetime.SCOPED:
            self._scoped_instances[interface] = instance
        
        return instance
    
    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create service instance with dependency resolution"""
        
        # Use factory function if provided
        if registration.factory_func:
            return registration.factory_func(self)
        
        # Resolve constructor dependencies
        dependency_instances = {}
        for dep_interface in registration.dependencies:
            dependency_instances[dep_interface] = self.resolve(dep_interface)
        
        # Create instance with dependencies
        if dependency_instances:
            # Map dependencies to constructor parameters
            constructor_args = self._map_dependencies_to_constructor(
                registration.implementation, dependency_instances
            )
            instance = registration.implementation(**constructor_args)
        else:
            instance = registration.implementation()
        
        return instance
    
    def _map_dependencies_to_constructor(self, implementation: Type, dependencies: Dict[Type, Any]) -> Dict[str, Any]:
        """Map resolved dependencies to constructor parameters"""
        
        # Get constructor signature
        sig = inspect.signature(implementation.__init__)
        constructor_args = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Find matching dependency by type annotation
            param_type = param.annotation
            if param_type in dependencies:
                constructor_args[param_name] = dependencies[param_type]
        
        return constructor_args
    
    def initialize_all_services(self) -> InitializationResult:
        """Initialize all services in proper dependency order"""
        
        if self._is_initialized:
            return InitializationResult(
                success=True,
                initialization_results=[],
                error="Services already initialized"
            )
        
        try:
            # Calculate initialization order
            self._initialization_order = self._calculate_initialization_order()
            
            initialization_results = []
            
            for service_interface in self._initialization_order:
                try:
                    # Resolve service instance (triggers creation)
                    instance = self.resolve(service_interface)
                    
                    # Call initialization method if exists
                    if hasattr(instance, 'initialize'):
                        init_result = instance.initialize()
                        initialization_results.append(ServiceInitResult(
                            service=service_interface,
                            success=True,
                            initialization_result=init_result,
                            message="Initialized successfully"
                        ))
                    else:
                        initialization_results.append(ServiceInitResult(
                            service=service_interface,
                            success=True,
                            message="No initialization method required"
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
            
            # Resolve circular dependencies with setter injection
            self._resolve_circular_dependencies()
            
            self._is_initialized = True
            
            return InitializationResult(
                success=True,
                initialization_results=initialization_results
            )
            
        except Exception as e:
            return InitializationResult(
                success=False,
                error=f"Service initialization failed: {str(e)}"
            )
    
    def _calculate_initialization_order(self) -> List[Type]:
        """Calculate initialization order using topological sort"""
        
        # Build dependency graph
        in_degree = {}
        for service in self._services:
            in_degree[service] = 0
        
        # Calculate in-degrees
        for service, registration in self._services.items():
            for dependency in registration.dependencies:
                if dependency in in_degree:
                    in_degree[service] += 1
        
        # Topological sort
        queue = [service for service, degree in in_degree.items() if degree == 0]
        initialization_order = []
        
        while queue:
            current_service = queue.pop(0)
            initialization_order.append(current_service)
            
            # Update in-degrees for dependent services
            for service, registration in self._services.items():
                if current_service in registration.dependencies:
                    in_degree[service] -= 1
                    if in_degree[service] == 0:
                        queue.append(service)
        
        # Check for circular dependencies
        if len(initialization_order) != len(self._services):
            remaining_services = [s for s in self._services if s not in initialization_order]
            raise CircularDependencyError(
                f"Circular dependency detected among services: {remaining_services}"
            )
        
        return initialization_order
    
    def _resolve_circular_dependencies(self):
        """Resolve circular dependencies using setter injection"""
        
        # This would implement setter injection for services that have circular dependencies
        # Based on the patterns established in dependency_resolution_patterns.md
        
        # For now, we'll implement a simple version that looks for set_* methods
        for interface, instance in self._singletons.items():
            for dep_interface in self._services[interface].dependencies:
                setter_method_name = f"set_{dep_interface.__name__.lower().replace('i', '', 1)}"
                
                if hasattr(instance, setter_method_name):
                    dep_instance = self._singletons.get(dep_interface)
                    if dep_instance:
                        getattr(instance, setter_method_name)(dep_instance)
    
    def _implements_protocol(self, implementation: Type, protocol: Type) -> bool:
        """Check if implementation satisfies protocol"""
        # Simplified protocol checking
        return True  # In real implementation, this would check protocol compliance
    
    def clear_scoped_instances(self):
        """Clear scoped instances (for scope management)"""
        self._scoped_instances.clear()

# === Service Registration Helper ===

def configure_autonomous_services(container: DIContainer):
    """Configure all autonomous TDD system services"""
    
    # Register utility services (no dependencies)
    from .utils.json_utilities import JSONUtilities
    from .config.configuration_manager import ConfigurationManager
    
    container.register_service(
        interface=JSONUtilities,
        implementation=JSONUtilities,
        lifetime=ServiceLifetime.SINGLETON,
        dependencies=[]
    )
    
    container.register_service(
        interface=ConfigurationManager,
        implementation=ConfigurationManager,
        lifetime=ServiceLifetime.SINGLETON,
        dependencies=[]
    )
    
    # Register core interfaces (will be implemented in actual files)
    # These registrations would be completed when the actual implementations are created
    
    # Example of how circular dependencies would be resolved:
    container.register_factory(IWorkflowManager, create_workflow_manager)

def create_workflow_manager(container: DIContainer) -> Any:
    """Factory function for workflow manager with circular dependency resolution"""
    
    # This would create the workflow manager and resolve circular dependencies
    # Implementation would follow the pattern from dependency_resolution_patterns.md
    
    # For now, return a placeholder
    class PlaceholderWorkflowManager:
        def execute_autonomous_cycle(self):
            return {"status": "placeholder"}
    
    return PlaceholderWorkflowManager()

# === Exceptions ===

class DIException(Exception):
    """Base exception for dependency injection errors"""
    pass

class CircularDependencyError(DIException):
    """Exception raised when circular dependencies are detected"""
    pass

class ServiceNotRegisteredException(DIException):
    """Exception raised when requested service is not registered"""
    pass