# Hook System Package
"""
Claude Code hook integration for the autonomous TDD system.

Provides autonomous orchestrator and flowchart implementations.
"""

from .autonomous_orchestrator import AutonomousOrchestrator
from .planning_process_hook import PlanningProcessHook
from .implementation_process_hook import ImplementationProcessHook
from .evidence_validator import main as evidence_validator

__all__ = [
    'AutonomousOrchestrator',
    'PlanningProcessHook', 
    'ImplementationProcessHook',
    'evidence_validator'
]