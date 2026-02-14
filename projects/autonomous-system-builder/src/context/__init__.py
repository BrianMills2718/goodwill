# Context Package
"""
Context management and loading for the autonomous TDD system.

Provides smart context loading, cross-reference discovery, and intelligent
context optimization within token limits.
"""

from .cross_reference_manager import CrossReferenceManager, CrossReference, ReferenceType, FileContextBundle

__all__ = [
    'CrossReferenceManager',
    'CrossReference', 
    'ReferenceType',
    'FileContextBundle'
]