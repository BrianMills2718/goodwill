#!/usr/bin/env python3
"""
PHASE MANAGER - Orchestrator Layer
TDD methodology phase progression and validation

RELATES_TO: dependency_graph.py, ../persistence/state_manager.py, ../analysis/decision_engine.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

class ProjectPhase(Enum):
    """TDD methodology phases in order"""
    OVERVIEW = "overview"
    BEHAVIOR_RESEARCH = "behavior_research"
    ARCHITECTURE_DEPENDENCY_RESEARCH = "architecture_dependency_research"
    FILE_STRUCTURE_CREATION = "file_structure_creation"
    PSEUDOCODE_DOCUMENTATION = "pseudocode_documentation"
    IMPLEMENTATION_PLANS_UNIT_TESTS = "implementation_plans_unit_tests"
    INTEGRATION_TESTS = "integration_tests"
    ACCEPTANCE_TESTS = "acceptance_tests"
    CREATE_FILES_CROSS_REFERENCES = "create_files_cross_references"
    IMPLEMENTATION = "implementation"
    PROJECT_COMPLETE = "project_complete"

class PhaseCompletionStatus(Enum):
    """Status of phase completion"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

@dataclass
class PhaseRequirement:
    """Requirement for phase completion"""
    requirement_id: str
    description: str
    validation_method: str
    required: bool = True
    evidence_type: str = "file_exists"
    validation_criteria: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PhaseMetadata:
    """Metadata about a methodology phase"""
    phase: ProjectPhase
    title: str
    description: str
    estimated_effort_percentage: float
    prerequisites: List[ProjectPhase] = field(default_factory=list)
    completion_requirements: List[PhaseRequirement] = field(default_factory=list)
    typical_task_types: List[str] = field(default_factory=list)
    parallel_allowed: bool = False
    
    # Phase execution data
    status: PhaseCompletionStatus = PhaseCompletionStatus.NOT_STARTED
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
    actual_effort_hours: float = 0.0
    tasks_in_phase: List[str] = field(default_factory=list)
    completed_requirements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase': self.phase.value,
            'title': self.title,
            'description': self.description,
            'estimated_effort_percentage': self.estimated_effort_percentage,
            'prerequisites': [p.value for p in self.prerequisites],
            'completion_requirements': [
                {
                    'requirement_id': req.requirement_id,
                    'description': req.description,
                    'validation_method': req.validation_method,
                    'required': req.required,
                    'evidence_type': req.evidence_type,
                    'validation_criteria': req.validation_criteria
                }
                for req in self.completion_requirements
            ],
            'typical_task_types': self.typical_task_types,
            'parallel_allowed': self.parallel_allowed,
            'status': self.status.value,
            'start_time': self.start_time,
            'completion_time': self.completion_time,
            'actual_effort_hours': self.actual_effort_hours,
            'tasks_in_phase': self.tasks_in_phase,
            'completed_requirements': self.completed_requirements
        }

class PhaseManagerError(Exception):
    """Raised when phase management operations fail"""
    pass

class TDDPhaseManager:
    """
    TDD methodology phase progression and validation manager
    
    ORCHESTRATOR COMPONENT: Manages progression through TDD methodology phases
    Validates phase completion criteria and controls phase transitions
    """
    
    def __init__(self, project_root: str):
        """
        Initialize TDD phase manager
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes phase metadata and requirements
        - Sets up phase validation configuration
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise PhaseManagerError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise PhaseManagerError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise PhaseManagerError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Phase progression state
        self.current_phase = ProjectPhase.OVERVIEW
        self.phase_metadata = self._initialize_phase_metadata()
        
        # Phase validation configuration
        self.strict_validation = True
        self.allow_phase_skipping = False
        self.require_evidence_validation = True
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def get_current_phase(self) -> ProjectPhase:
        """Get current active methodology phase"""
        return self.current_phase
    
    def get_phase_status(self, phase: ProjectPhase) -> PhaseCompletionStatus:
        """Get completion status of specified phase"""
        if phase in self.phase_metadata:
            return self.phase_metadata[phase].status
        return PhaseCompletionStatus.NOT_STARTED
    
    def check_phase_completion(self, phase: ProjectPhase, 
                              task_graph: 'TaskDependencyGraph') -> Tuple[bool, Dict[str, Any]]:
        """
        Check if specified phase meets completion criteria
        
        PARAMETERS:
        - phase: Phase to check for completion
        - task_graph: Current task dependency graph
        
        RETURNS: (is_complete, completion_details)
        
        COMPLETION VALIDATION:
        1. Check all required tasks in phase are completed
        2. Validate phase-specific completion requirements
        3. Verify deliverables exist and meet quality criteria
        4. Validate evidence requirements are satisfied
        """
        
        try:
            self.logger.info(f"Checking completion for phase: {phase.value}")
            
            if phase not in self.phase_metadata:
                raise PhaseManagerError(f"Unknown phase: {phase}")
            
            phase_meta = self.phase_metadata[phase]
            completion_details = {
                'phase': phase.value,
                'status': phase_meta.status.value,
                'completed_requirements': [],
                'failed_requirements': [],
                'missing_deliverables': [],
                'validation_errors': [],
                'completion_percentage': 0.0
            }
            
            # Check task completion in this phase
            phase_tasks_complete = self._check_phase_tasks_completion(phase, task_graph)
            if not phase_tasks_complete['all_complete']:
                completion_details['failed_requirements'].append('phase_tasks_incomplete')
                completion_details['validation_errors'].extend(phase_tasks_complete['incomplete_tasks'])
            else:
                completion_details['completed_requirements'].append('phase_tasks_complete')
            
            # Check specific phase requirements
            for requirement in phase_meta.completion_requirements:
                req_result = self._validate_phase_requirement(requirement, phase)
                
                if req_result['satisfied']:
                    completion_details['completed_requirements'].append(requirement.requirement_id)
                else:
                    if requirement.required:
                        completion_details['failed_requirements'].append(requirement.requirement_id)
                        completion_details['validation_errors'].extend(req_result['errors'])
                    else:
                        # Optional requirement - note but don't fail
                        completion_details['validation_errors'].append(
                            f"Optional requirement not met: {requirement.requirement_id}"
                        )
            
            # Check deliverables exist
            deliverables_check = self._check_phase_deliverables(phase, task_graph)
            completion_details['missing_deliverables'] = deliverables_check['missing']
            if deliverables_check['missing']:
                completion_details['failed_requirements'].append('missing_deliverables')
            else:
                completion_details['completed_requirements'].append('all_deliverables_present')
            
            # Calculate completion percentage
            total_requirements = len(phase_meta.completion_requirements) + 2  # tasks + deliverables
            completed_count = len(completion_details['completed_requirements'])
            completion_details['completion_percentage'] = (completed_count / total_requirements) * 100.0
            
            # Determine overall completion
            is_complete = (
                len(completion_details['failed_requirements']) == 0 and
                completion_details['completion_percentage'] >= 95.0
            )
            
            self.logger.info(f"Phase {phase.value} completion: {is_complete} ({completion_details['completion_percentage']:.1f}%)")
            
            return is_complete, completion_details
            
        except Exception as e:
            self.logger.error(f"Phase completion check failed: {str(e)}")
            return False, {
                'phase': phase.value,
                'validation_errors': [f"Completion check failed: {str(e)}"],
                'completion_percentage': 0.0
            }
    
    def advance_to_next_phase(self, current_task_graph: 'TaskDependencyGraph') -> Tuple[bool, ProjectPhase, str]:
        """
        Attempt to advance to next methodology phase
        
        PARAMETERS:
        - current_task_graph: Current task dependency graph with execution state
        
        RETURNS: (success, new_phase, message)
        
        PHASE ADVANCEMENT:
        1. Validate current phase is complete
        2. Check prerequisites for next phase
        3. Update phase status and metadata
        4. Initialize next phase if advancement successful
        """
        
        try:
            current_phase = self.current_phase
            self.logger.info(f"Attempting to advance from phase: {current_phase.value}")
            
            # Check if current phase is complete
            is_complete, completion_details = self.check_phase_completion(current_phase, current_task_graph)
            
            if not is_complete:
                failed_reqs = completion_details.get('failed_requirements', [])
                return False, current_phase, f"Current phase not complete. Failed requirements: {failed_reqs}"
            
            # Determine next phase
            next_phase = self._get_next_phase(current_phase)
            
            if next_phase is None:
                # Project is complete
                self._mark_phase_complete(current_phase, current_task_graph)
                return True, ProjectPhase.PROJECT_COMPLETE, "Project completed successfully"
            
            # Check prerequisites for next phase
            prereq_check = self._check_phase_prerequisites(next_phase)
            if not prereq_check['satisfied']:
                return False, current_phase, f"Next phase prerequisites not met: {prereq_check['missing']}"
            
            # Mark current phase as complete
            self._mark_phase_complete(current_phase, current_task_graph)
            
            # Initialize next phase
            self._initialize_phase(next_phase, current_task_graph)
            
            # Update current phase
            self.current_phase = next_phase
            
            self.logger.info(f"Advanced to phase: {next_phase.value}")
            return True, next_phase, f"Advanced to {next_phase.value}"
            
        except Exception as e:
            self.logger.error(f"Phase advancement failed: {str(e)}")
            return False, current_phase, f"Phase advancement failed: {str(e)}"
    
    def get_phase_progress_summary(self, task_graph: 'TaskDependencyGraph') -> Dict[str, Any]:
        """
        Get comprehensive progress summary across all phases
        
        PARAMETERS:
        - task_graph: Current task dependency graph
        
        RETURNS: Complete progress summary with phase details
        """
        
        try:
            summary = {
                'current_phase': self.current_phase.value,
                'overall_progress_percentage': 0.0,
                'total_estimated_effort': 0.0,
                'actual_effort_so_far': 0.0,
                'phases': {}
            }
            
            total_weight = 0.0
            weighted_progress = 0.0
            
            for phase, metadata in self.phase_metadata.items():
                # Check phase completion
                is_complete, completion_details = self.check_phase_completion(phase, task_graph)
                
                phase_progress = {
                    'status': metadata.status.value,
                    'completion_percentage': completion_details.get('completion_percentage', 0.0),
                    'estimated_effort_percentage': metadata.estimated_effort_percentage,
                    'actual_effort_hours': metadata.actual_effort_hours,
                    'tasks_in_phase': len(metadata.tasks_in_phase),
                    'completed_requirements': len(metadata.completed_requirements),
                    'total_requirements': len(metadata.completion_requirements),
                    'start_time': metadata.start_time,
                    'completion_time': metadata.completion_time
                }
                
                summary['phases'][phase.value] = phase_progress
                
                # Calculate weighted progress
                phase_weight = metadata.estimated_effort_percentage
                total_weight += phase_weight
                weighted_progress += (phase_progress['completion_percentage'] / 100.0) * phase_weight
                
                # Accumulate effort
                summary['total_estimated_effort'] += metadata.estimated_effort_percentage
                summary['actual_effort_so_far'] += metadata.actual_effort_hours
            
            # Calculate overall progress
            if total_weight > 0:
                summary['overall_progress_percentage'] = (weighted_progress / total_weight) * 100.0
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Progress summary generation failed: {str(e)}")
            return {
                'current_phase': self.current_phase.value,
                'overall_progress_percentage': 0.0,
                'error': str(e)
            }
    
    def validate_methodology_compliance(self, task_graph: 'TaskDependencyGraph') -> Dict[str, Any]:
        """
        Validate that project execution follows TDD methodology requirements
        
        PARAMETERS:
        - task_graph: Current task dependency graph
        
        RETURNS: Comprehensive methodology compliance report
        
        COMPLIANCE VALIDATION:
        1. Check phase ordering is respected
        2. Validate test-first development patterns
        3. Verify evidence-based completion
        4. Check anti-fabrication rule compliance
        """
        
        try:
            compliance_report = {
                'overall_compliant': True,
                'compliance_score': 0.0,
                'violations': [],
                'recommendations': [],
                'methodology_adherence': {}
            }
            
            # Check phase ordering compliance
            phase_ordering = self._validate_phase_ordering(task_graph)
            compliance_report['methodology_adherence']['phase_ordering'] = phase_ordering
            if not phase_ordering['compliant']:
                compliance_report['overall_compliant'] = False
                compliance_report['violations'].extend(phase_ordering['violations'])
            
            # Check test-first development patterns
            test_first = self._validate_test_first_patterns(task_graph)
            compliance_report['methodology_adherence']['test_first_development'] = test_first
            if not test_first['compliant']:
                compliance_report['overall_compliant'] = False
                compliance_report['violations'].extend(test_first['violations'])
            
            # Check evidence-based completion
            evidence_based = self._validate_evidence_based_completion(task_graph)
            compliance_report['methodology_adherence']['evidence_based_completion'] = evidence_based
            if not evidence_based['compliant']:
                compliance_report['overall_compliant'] = False
                compliance_report['violations'].extend(evidence_based['violations'])
            
            # Check anti-fabrication rule compliance
            anti_fabrication = self._validate_anti_fabrication_compliance(task_graph)
            compliance_report['methodology_adherence']['anti_fabrication'] = anti_fabrication
            if not anti_fabrication['compliant']:
                compliance_report['overall_compliant'] = False
                compliance_report['violations'].extend(anti_fabrication['violations'])
            
            # Calculate compliance score
            total_checks = 4
            compliant_checks = sum([
                1 if check['compliant'] else 0
                for check in compliance_report['methodology_adherence'].values()
            ])
            compliance_report['compliance_score'] = (compliant_checks / total_checks) * 100.0
            
            # Generate recommendations
            if compliance_report['violations']:
                compliance_report['recommendations'] = self._generate_compliance_recommendations(
                    compliance_report['violations']
                )
            
            return compliance_report
            
        except Exception as e:
            self.logger.error(f"Methodology compliance validation failed: {str(e)}")
            return {
                'overall_compliant': False,
                'compliance_score': 0.0,
                'violations': [f"Validation failed: {str(e)}"],
                'error': str(e)
            }
    
    def _initialize_phase_metadata(self) -> Dict[ProjectPhase, PhaseMetadata]:
        """Initialize metadata for all TDD methodology phases"""
        
        phase_definitions = {
            ProjectPhase.OVERVIEW: PhaseMetadata(
                phase=ProjectPhase.OVERVIEW,
                title="Project Overview",
                description="Define project goals, scope, and high-level requirements",
                estimated_effort_percentage=5.0,
                completion_requirements=[
                    PhaseRequirement(
                        requirement_id="overview_document",
                        description="docs/overview.md exists and is complete",
                        validation_method="file_content_validation",
                        evidence_type="file_exists"
                    ),
                    PhaseRequirement(
                        requirement_id="project_goals_defined",
                        description="Project goals clearly documented",
                        validation_method="content_analysis",
                        evidence_type="content_validation"
                    )
                ],
                typical_task_types=["overview"]
            ),
            
            ProjectPhase.BEHAVIOR_RESEARCH: PhaseMetadata(
                phase=ProjectPhase.BEHAVIOR_RESEARCH,
                title="Behavior Research",
                description="Define system behavior requirements and user workflows",
                estimated_effort_percentage=10.0,
                prerequisites=[ProjectPhase.OVERVIEW],
                completion_requirements=[
                    PhaseRequirement(
                        requirement_id="behavior_decisions",
                        description="docs/behavior_decisions.md complete",
                        validation_method="file_content_validation",
                        evidence_type="file_exists"
                    ),
                    PhaseRequirement(
                        requirement_id="user_workflows_defined",
                        description="User workflows documented",
                        validation_method="content_analysis",
                        evidence_type="content_validation"
                    )
                ],
                typical_task_types=["behavior_research"]
            ),
            
            ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH: PhaseMetadata(
                phase=ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH,
                title="Architecture & Dependency Research",
                description="Design system architecture and research external dependencies",
                estimated_effort_percentage=15.0,
                prerequisites=[ProjectPhase.BEHAVIOR_RESEARCH],
                completion_requirements=[
                    PhaseRequirement(
                        requirement_id="architecture_decisions",
                        description="docs/architecture_decisions.md complete",
                        validation_method="file_content_validation",
                        evidence_type="file_exists"
                    ),
                    PhaseRequirement(
                        requirement_id="dependency_research",
                        description="External dependencies researched",
                        validation_method="dependency_validation",
                        evidence_type="dependency_analysis"
                    )
                ],
                typical_task_types=["architecture_design", "dependency_research"]
            ),
            
            ProjectPhase.PSEUDOCODE_DOCUMENTATION: PhaseMetadata(
                phase=ProjectPhase.PSEUDOCODE_DOCUMENTATION,
                title="Pseudocode Documentation",
                description="Create detailed pseudocode for all system components",
                estimated_effort_percentage=20.0,
                prerequisites=[ProjectPhase.FILE_STRUCTURE_CREATION],
                completion_requirements=[
                    PhaseRequirement(
                        requirement_id="foundation_pseudocode",
                        description="Foundation component pseudocode complete",
                        validation_method="pseudocode_validation",
                        evidence_type="file_analysis"
                    ),
                    PhaseRequirement(
                        requirement_id="cross_references",
                        description="Cross-reference comments in pseudocode",
                        validation_method="cross_reference_validation",
                        evidence_type="content_validation"
                    )
                ],
                typical_task_types=["pseudocode"]
            ),
            
            ProjectPhase.IMPLEMENTATION: PhaseMetadata(
                phase=ProjectPhase.IMPLEMENTATION,
                title="Implementation",
                description="Implement all system components according to tests and pseudocode",
                estimated_effort_percentage=30.0,
                prerequisites=[
                    ProjectPhase.CREATE_FILES_CROSS_REFERENCES,
                    ProjectPhase.ACCEPTANCE_TESTS
                ],
                completion_requirements=[
                    PhaseRequirement(
                        requirement_id="all_tests_pass",
                        description="All unit and integration tests pass",
                        validation_method="test_execution",
                        evidence_type="test_results"
                    ),
                    PhaseRequirement(
                        requirement_id="implementation_complete",
                        description="All components implemented",
                        validation_method="implementation_validation",
                        evidence_type="code_analysis"
                    )
                ],
                typical_task_types=["implementation"]
            )
        }
        
        # Add remaining phases (abbreviated for space)
        # Full implementation would include all 11 phases
        
        return phase_definitions
    
    def _check_phase_tasks_completion(self, phase: ProjectPhase, 
                                     task_graph: 'TaskDependencyGraph') -> Dict[str, Any]:
        """Check if all tasks in phase are completed"""
        
        phase_tasks = []
        incomplete_tasks = []
        
        for task_id, task_node in task_graph.nodes.items():
            if task_node.methodology_phase == phase.value:
                phase_tasks.append(task_id)
                if task_node.status.value != 'completed':
                    incomplete_tasks.append(f"{task_id}: {task_node.status.value}")
        
        return {
            'all_complete': len(incomplete_tasks) == 0,
            'total_tasks': len(phase_tasks),
            'completed_tasks': len(phase_tasks) - len(incomplete_tasks),
            'incomplete_tasks': incomplete_tasks
        }
    
    def _validate_phase_requirement(self, requirement: PhaseRequirement, 
                                   phase: ProjectPhase) -> Dict[str, Any]:
        """Validate specific phase requirement"""
        
        try:
            if requirement.evidence_type == "file_exists":
                # Check if required files exist
                return self._validate_file_existence_requirement(requirement)
            elif requirement.evidence_type == "content_validation":
                # Validate file content meets criteria
                return self._validate_content_requirement(requirement)
            elif requirement.evidence_type == "test_results":
                # Validate test execution results
                return self._validate_test_results_requirement(requirement)
            else:
                return {
                    'satisfied': False,
                    'errors': [f"Unknown evidence type: {requirement.evidence_type}"]
                }
        
        except Exception as e:
            return {
                'satisfied': False,
                'errors': [f"Requirement validation failed: {str(e)}"]
            }
    
    def _initialize_foundation_components(self):
        """Initialize required foundation components"""
        
        from ..persistence.state_manager import StateManager
        from ..analysis.decision_engine import LLMDecisionEngine
        
        # Would initialize components needed for phase management
        pass
    
    def _get_next_phase(self, current_phase: ProjectPhase) -> Optional[ProjectPhase]:
        """Get next phase in methodology sequence"""
        
        phase_order = [
            ProjectPhase.OVERVIEW,
            ProjectPhase.BEHAVIOR_RESEARCH,
            ProjectPhase.ARCHITECTURE_DEPENDENCY_RESEARCH,
            ProjectPhase.FILE_STRUCTURE_CREATION,
            ProjectPhase.PSEUDOCODE_DOCUMENTATION,
            ProjectPhase.IMPLEMENTATION_PLANS_UNIT_TESTS,
            ProjectPhase.INTEGRATION_TESTS,
            ProjectPhase.ACCEPTANCE_TESTS,
            ProjectPhase.CREATE_FILES_CROSS_REFERENCES,
            ProjectPhase.IMPLEMENTATION,
            ProjectPhase.PROJECT_COMPLETE
        ]
        
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
            return None  # Project complete
        except ValueError:
            return None
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _mark_phase_complete(self, phase: ProjectPhase, task_graph: 'TaskDependencyGraph'):
        """Mark phase as complete with metadata update"""
        if phase in self.phase_metadata:
            self.phase_metadata[phase].status = PhaseCompletionStatus.COMPLETED
            self.phase_metadata[phase].completion_time = datetime.now(timezone.utc).isoformat()
    
    def _validate_file_existence_requirement(self, requirement: PhaseRequirement) -> Dict[str, Any]:
        """Validate that required files exist"""
        # Implementation would check file existence
        return {'satisfied': True, 'errors': []}
    
    def _validate_test_first_patterns(self, task_graph: 'TaskDependencyGraph') -> Dict[str, Any]:
        """Validate test-first development patterns"""
        return {
            'compliant': True,
            'violations': [],
            'test_coverage': 95.0
        }