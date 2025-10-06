# Context Package
"""
Context management and loading for the autonomous TDD system.

Provides smart context loading, cross-reference discovery, and intelligent
context optimization within token limits.
"""

from .smart_context_loader import SmartContextLoader
from .cross_reference_discovery import CrossReferenceDiscovery

__all__ = [
    'SmartContextLoader',
    'CrossReferenceDiscovery'
]