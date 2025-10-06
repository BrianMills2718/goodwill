# Evidence Package
"""
Evidence collection and validation for the autonomous TDD system.

Provides evidence collection, anti-fabrication detection, and validation
to prevent false success claims.
"""

from .evidence_collector import EvidenceCollector
from .anti_fabrication import AntiFabricationDetector
from .test_runner import TestRunner

__all__ = [
    'EvidenceCollector',
    'AntiFabricationDetector',
    'TestRunner'
]