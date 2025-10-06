# Persistence Package
"""
State persistence and management for the autonomous TDD system.

Provides state management, backup/recovery, and data persistence
with integrity validation.
"""

from .state_persistence import (
    StateManager, StateError, StateConsistencyError,
    ProjectPhase, ProjectState, TaskNode, TaskGraph, 
    EvidenceRecord, CompleteSystemState
)

__all__ = [
    'StateManager',
    'StateError', 
    'StateConsistencyError',
    'ProjectPhase',
    'ProjectState', 
    'TaskNode',
    'TaskGraph',
    'EvidenceRecord',
    'CompleteSystemState'
]