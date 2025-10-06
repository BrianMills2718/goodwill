#!/usr/bin/env python3
"""
ANTI-FABRICATION - Evidence System Layer
Detection and prevention of fabricated evidence and false success claims

RELATES_TO: evidence_collector.py, ../persistence/state_manager.py, ../analysis/decision_engine.py
"""

import os
import re
import json
import logging
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Pattern
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

class FabricationType(Enum):
    """Types of fabrication that can be detected"""
    MOCK_DATA_MASQUERADING = "mock_data_masquerading"
    FALSE_TEST_RESULTS = "false_test_results"
    FABRICATED_FILES = "fabricated_files"
    SIMULATED_EXTERNAL_RESPONSES = "simulated_external_responses"
    TAMPERED_TIMESTAMPS = "tampered_timestamps"
    CIRCULAR_VALIDATION = "circular_validation"
    INCOMPLETE_IMPLEMENTATION = "incomplete_implementation"
    HIDDEN_FAILURES = "hidden_failures"

class FabricationSeverity(Enum):
    """Severity levels for fabrication detection"""
    CRITICAL = "critical"    # Clear evidence of intentional fabrication
    HIGH = "high"           # Strong indicators of fabrication
    MEDIUM = "medium"       # Suspicious patterns requiring investigation
    LOW = "low"            # Minor inconsistencies or warnings
    NONE = "none"          # No fabrication detected

@dataclass
class FabricationIndicator:
    """Individual indicator of potential fabrication"""
    indicator_id: str
    fabrication_type: FabricationType
    severity: FabricationSeverity
    description: str
    evidence_location: str
    detection_method: str
    confidence_score: float  # 0.0 to 1.0
    
    # Supporting data
    detected_patterns: List[str] = field(default_factory=list)
    suspicious_values: Dict[str, Any] = field(default_factory=dict)
    context_information: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'indicator_id': self.indicator_id,
            'fabrication_type': self.fabrication_type.value,
            'severity': self.severity.value,
            'description': self.description,
            'evidence_location': self.evidence_location,
            'detection_method': self.detection_method,
            'confidence_score': self.confidence_score,
            'detected_patterns': self.detected_patterns,
            'suspicious_values': self.suspicious_values,
            'context_information': self.context_information
        }

@dataclass
class FabricationReport:
    """Comprehensive report of fabrication detection results"""
    report_id: str
    target_evidence_id: str
    detection_time: str
    overall_fabrication_detected: bool
    highest_severity: FabricationSeverity
    confidence_level: float
    
    # Detected indicators
    fabrication_indicators: List[FabricationIndicator] = field(default_factory=list)
    
    # Analysis summary
    total_indicators: int = 0
    indicators_by_severity: Dict[str, int] = field(default_factory=dict)
    indicators_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)
    investigation_priority: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'target_evidence_id': self.target_evidence_id,
            'detection_time': self.detection_time,
            'overall_fabrication_detected': self.overall_fabrication_detected,
            'highest_severity': self.highest_severity.value,
            'confidence_level': self.confidence_level,
            'fabrication_indicators': [indicator.to_dict() for indicator in self.fabrication_indicators],
            'total_indicators': self.total_indicators,
            'indicators_by_severity': self.indicators_by_severity,
            'indicators_by_type': self.indicators_by_type,
            'recommended_actions': self.recommended_actions,
            'investigation_priority': self.investigation_priority
        }

class AntiFabricationError(Exception):
    """Raised when anti-fabrication operations fail"""
    pass

class AntiFabricationDetector:
    """
    Detection system for fabricated evidence and false success claims
    
    EVIDENCE SYSTEM COMPONENT: Prevents autonomous system from claiming false success
    Uses multiple detection methods to identify patterns of fabrication and deception
    """
    
    def __init__(self, project_root: str):
        """
        Initialize anti-fabrication detector
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes detection patterns and baselines
        - Sets up fabrication monitoring systems
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise AntiFabricationError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise AntiFabricationError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise AntiFabricationError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Detection configuration
        self.enable_mock_detection = True
        self.enable_timestamp_analysis = True
        self.enable_pattern_analysis = True
        self.enable_external_verification = True
        
        # Detection patterns
        self.mock_patterns = self._initialize_mock_detection_patterns()
        self.suspicious_patterns = self._initialize_suspicious_patterns()
        self.fabrication_keywords = self._initialize_fabrication_keywords()
        
        # Baseline establishment
        self.project_baseline = None
        self.file_integrity_hashes = {}
        
        # Detection storage
        self.detection_history = []
        self.false_positive_patterns = set()
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def detect_fabrication(self, evidence: 'EvidenceRecord') -> FabricationReport:
        """
        Comprehensive fabrication detection for evidence record
        
        PARAMETERS:
        - evidence: Evidence record to analyze for fabrication
        
        RETURNS: Detailed fabrication detection report
        
        DETECTION PROCESS:
        1. Analyze evidence content for fabrication patterns
        2. Check for mock data masquerading as real data
        3. Validate timestamps and chronological consistency
        4. Cross-reference with external systems where possible
        5. Assess overall fabrication risk and confidence
        """
        
        try:
            self.logger.info(f"Analyzing evidence for fabrication: {evidence.evidence_id}")
            
            # Create fabrication report
            report = FabricationReport(
                report_id=f"fabrication_{evidence.evidence_id}_{int(datetime.now().timestamp())}",
                target_evidence_id=evidence.evidence_id,
                detection_time=datetime.now(timezone.utc).isoformat(),
                overall_fabrication_detected=False,
                highest_severity=FabricationSeverity.NONE,
                confidence_level=0.0
            )
            
            # Mock data detection
            mock_indicators = self._detect_mock_data_masquerading(evidence)
            report.fabrication_indicators.extend(mock_indicators)
            
            # Test result fabrication detection
            test_indicators = self._detect_false_test_results(evidence)
            report.fabrication_indicators.extend(test_indicators)
            
            # File fabrication detection
            file_indicators = self._detect_fabricated_files(evidence)
            report.fabrication_indicators.extend(file_indicators)
            
            # Timestamp tampering detection
            timestamp_indicators = self._detect_timestamp_tampering(evidence)
            report.fabrication_indicators.extend(timestamp_indicators)
            
            # External response simulation detection
            external_indicators = self._detect_simulated_external_responses(evidence)
            report.fabrication_indicators.extend(external_indicators)
            
            # Circular validation detection
            circular_indicators = self._detect_circular_validation(evidence)
            report.fabrication_indicators.extend(circular_indicators)
            
            # Implementation completeness analysis
            implementation_indicators = self._detect_incomplete_implementation(evidence)
            report.fabrication_indicators.extend(implementation_indicators)
            
            # Hidden failure detection
            hidden_failure_indicators = self._detect_hidden_failures(evidence)
            report.fabrication_indicators.extend(hidden_failure_indicators)
            
            # Analyze indicators and generate report summary
            self._analyze_fabrication_indicators(report)
            
            # Generate recommendations
            self._generate_fabrication_recommendations(report)
            
            self.logger.info(f"Fabrication analysis complete: {report.total_indicators} indicators found")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Fabrication detection failed: {str(e)}")
            
            # Return error report
            error_report = FabricationReport(
                report_id=f"fabrication_error_{int(datetime.now().timestamp())}",
                target_evidence_id=evidence.evidence_id,
                detection_time=datetime.now(timezone.utc).isoformat(),
                overall_fabrication_detected=True,  # Err on side of caution
                highest_severity=FabricationSeverity.HIGH,
                confidence_level=0.0
            )
            
            error_indicator = FabricationIndicator(
                indicator_id="detection_error",
                fabrication_type=FabricationType.HIDDEN_FAILURES,
                severity=FabricationSeverity.HIGH,
                description=f"Fabrication detection failed: {str(e)}",
                evidence_location=evidence.evidence_id,
                detection_method="error_handling",
                confidence_score=1.0
            )
            
            error_report.fabrication_indicators.append(error_indicator)
            error_report.total_indicators = 1
            
            return error_report
    
    def _detect_mock_data_masquerading(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """
        Detect mock data being presented as real production data
        
        MOCK DATA INDICATORS:
        1. Common mock values (test@example.com, localhost, 127.0.0.1)
        2. Sequential or pattern-based identifiers
        3. Unrealistic data distributions
        4. Mock library usage patterns
        """
        
        indicators = []
        
        try:
            evidence_data = evidence.evidence_data
            
            # Convert evidence data to searchable text
            evidence_text = json.dumps(evidence_data, indent=2).lower()
            
            # Check for common mock patterns
            for pattern_name, pattern_regex in self.mock_patterns.items():
                matches = pattern_regex.findall(evidence_text)
                
                if matches:
                    confidence = min(0.8, len(matches) * 0.2)  # Higher confidence with more matches
                    
                    indicator = FabricationIndicator(
                        indicator_id=f"mock_{pattern_name}_{evidence.evidence_id}",
                        fabrication_type=FabricationType.MOCK_DATA_MASQUERADING,
                        severity=FabricationSeverity.HIGH if confidence > 0.6 else FabricationSeverity.MEDIUM,
                        description=f"Mock data pattern detected: {pattern_name}",
                        evidence_location=evidence.evidence_id,
                        detection_method="pattern_matching",
                        confidence_score=confidence,
                        detected_patterns=[pattern_name],
                        suspicious_values={'matches': matches}
                    )
                    
                    indicators.append(indicator)
            
            # Check for mock library imports in code evidence
            if evidence.evidence_type.value in ['file_content', 'test_execution']:
                mock_library_patterns = [
                    r'from\s+unittest\.mock\s+import',
                    r'import\s+mock',
                    r'@mock\.patch',
                    r'@patch\(',
                    r'Mock\(\)',
                    r'MagicMock\(\)'
                ]
                
                for pattern in mock_library_patterns:
                    if re.search(pattern, evidence_text, re.IGNORECASE):
                        indicator = FabricationIndicator(
                            indicator_id=f"mock_library_{evidence.evidence_id}",
                            fabrication_type=FabricationType.MOCK_DATA_MASQUERADING,
                            severity=FabricationSeverity.MEDIUM,
                            description="Mock library usage detected in evidence",
                            evidence_location=evidence.evidence_id,
                            detection_method="code_analysis",
                            confidence_score=0.7,
                            detected_patterns=[pattern]
                        )
                        
                        indicators.append(indicator)
                        break  # Only add one indicator for mock library usage
            
            # Check for unrealistic success rates
            if 'success' in evidence_data or 'passed' in evidence_data:
                success_indicators = self._analyze_success_patterns(evidence_data)
                indicators.extend(success_indicators)
            
        except Exception as e:
            # If mock detection fails, that's suspicious too
            error_indicator = FabricationIndicator(
                indicator_id=f"mock_detection_error_{evidence.evidence_id}",
                fabrication_type=FabricationType.HIDDEN_FAILURES,
                severity=FabricationSeverity.MEDIUM,
                description=f"Mock detection analysis failed: {str(e)}",
                evidence_location=evidence.evidence_id,
                detection_method="error_analysis",
                confidence_score=0.5
            )
            
            indicators.append(error_indicator)
        
        return indicators
    
    def _detect_false_test_results(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """
        Detect fabricated or manipulated test execution results
        
        FALSE TEST INDICATORS:
        1. Tests claiming 100% success with no historical failures
        2. Execution times that are unrealistically fast or consistent
        3. Test output that doesn't match expected patterns
        4. Missing error details for failed assertions
        """
        
        indicators = []
        
        try:
            if evidence.evidence_type.value != 'test_execution':
                return indicators
            
            evidence_data = evidence.evidence_data
            
            # Check for suspicious test timing
            execution_duration = evidence_data.get('execution_duration', 0)
            
            if execution_duration < 0.1 and evidence_data.get('tests_run', 0) > 0:
                indicator = FabricationIndicator(
                    indicator_id=f"suspicious_timing_{evidence.evidence_id}",
                    fabrication_type=FabricationType.FALSE_TEST_RESULTS,
                    severity=FabricationSeverity.MEDIUM,
                    description="Test execution time suspiciously fast",
                    evidence_location=evidence.evidence_id,
                    detection_method="timing_analysis",
                    confidence_score=0.6,
                    suspicious_values={'execution_duration': execution_duration}
                )
                
                indicators.append(indicator)
            
            # Check for perfect success rates without historical context
            tests_passed = evidence_data.get('tests_passed', 0)
            tests_failed = evidence_data.get('tests_failed', 0)
            tests_run = evidence_data.get('tests_run', 0)
            
            if tests_run > 0 and tests_failed == 0 and tests_passed == tests_run:
                # Perfect test results - check for supporting evidence
                perfect_success_indicator = self._analyze_perfect_test_results(evidence)
                if perfect_success_indicator:
                    indicators.append(perfect_success_indicator)
            
            # Check for missing test output details
            stdout = evidence_data.get('stdout', '')
            stderr = evidence_data.get('stderr', '')
            
            if tests_run > 0 and len(stdout) < 10 and len(stderr) < 10:
                indicator = FabricationIndicator(
                    indicator_id=f"missing_output_{evidence.evidence_id}",
                    fabrication_type=FabricationType.FALSE_TEST_RESULTS,
                    severity=FabricationSeverity.MEDIUM,
                    description="Test execution has suspiciously little output",
                    evidence_location=evidence.evidence_id,
                    detection_method="output_analysis",
                    confidence_score=0.5,
                    suspicious_values={
                        'stdout_length': len(stdout),
                        'stderr_length': len(stderr),
                        'tests_run': tests_run
                    }
                )
                
                indicators.append(indicator)
            
            # Check for fabricated test framework output
            if stdout and not self._validate_test_framework_output(stdout):
                indicator = FabricationIndicator(
                    indicator_id=f"invalid_framework_output_{evidence.evidence_id}",
                    fabrication_type=FabricationType.FALSE_TEST_RESULTS,
                    severity=FabricationSeverity.HIGH,
                    description="Test output doesn't match expected framework patterns",
                    evidence_location=evidence.evidence_id,
                    detection_method="framework_validation",
                    confidence_score=0.8
                )
                
                indicators.append(indicator)
            
        except Exception as e:
            error_indicator = FabricationIndicator(
                indicator_id=f"test_analysis_error_{evidence.evidence_id}",
                fabrication_type=FabricationType.HIDDEN_FAILURES,
                severity=FabricationSeverity.LOW,
                description=f"Test result analysis failed: {str(e)}",
                evidence_location=evidence.evidence_id,
                detection_method="error_analysis",
                confidence_score=0.3
            )
            
            indicators.append(error_indicator)
        
        return indicators
    
    def _detect_fabricated_files(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """
        Detect files that have been fabricated or artificially created
        
        FABRICATED FILE INDICATORS:
        1. Files with impossible timestamps
        2. Files created too quickly in sequence
        3. Files with suspicious content patterns
        4. Files that don't match expected project structure
        """
        
        indicators = []
        
        try:
            if evidence.evidence_type.value != 'file_existence':
                return indicators
            
            evidence_data = evidence.evidence_data
            
            # Check file timestamps
            creation_time = evidence_data.get('creation_time')
            modification_time = evidence_data.get('modification_time')
            
            if creation_time and modification_time:
                # Check for impossible timestamp relationships
                if modification_time < creation_time:
                    indicator = FabricationIndicator(
                        indicator_id=f"impossible_timestamps_{evidence.evidence_id}",
                        fabrication_type=FabricationType.TAMPERED_TIMESTAMPS,
                        severity=FabricationSeverity.HIGH,
                        description="File modification time is before creation time",
                        evidence_location=evidence.evidence_id,
                        detection_method="timestamp_validation",
                        confidence_score=0.9,
                        suspicious_values={
                            'creation_time': creation_time,
                            'modification_time': modification_time
                        }
                    )
                    
                    indicators.append(indicator)
                
                # Check for files created in the future
                current_time = datetime.now().timestamp()
                if creation_time > current_time + 60:  # More than 1 minute in future
                    indicator = FabricationIndicator(
                        indicator_id=f"future_timestamp_{evidence.evidence_id}",
                        fabrication_type=FabricationType.TAMPERED_TIMESTAMPS,
                        severity=FabricationSeverity.HIGH,
                        description="File creation time is in the future",
                        evidence_location=evidence.evidence_id,
                        detection_method="timestamp_validation",
                        confidence_score=0.8,
                        suspicious_values={'creation_time': creation_time}
                    )
                    
                    indicators.append(indicator)
            
            # Check for suspicious file sizes
            file_size = evidence_data.get('file_size', 0)
            file_path = evidence_data.get('file_path', '')
            
            if file_size == 0 and file_path.endswith(('.py', '.js', '.java', '.cpp')):
                indicator = FabricationIndicator(
                    indicator_id=f"empty_code_file_{evidence.evidence_id}",
                    fabrication_type=FabricationType.FABRICATED_FILES,
                    severity=FabricationSeverity.MEDIUM,
                    description="Code file is empty or has zero size",
                    evidence_location=evidence.evidence_id,
                    detection_method="file_analysis",
                    confidence_score=0.6,
                    suspicious_values={'file_size': file_size, 'file_path': file_path}
                )
                
                indicators.append(indicator)
            
            # Check file content for fabrication patterns
            content_preview = evidence_data.get('content_preview', '')
            if content_preview:
                content_indicators = self._analyze_file_content_for_fabrication(content_preview, evidence)
                indicators.extend(content_indicators)
            
        except Exception as e:
            error_indicator = FabricationIndicator(
                indicator_id=f"file_analysis_error_{evidence.evidence_id}",
                fabrication_type=FabricationType.HIDDEN_FAILURES,
                severity=FabricationSeverity.LOW,
                description=f"File analysis failed: {str(e)}",
                evidence_location=evidence.evidence_id,
                detection_method="error_analysis",
                confidence_score=0.3
            )
            
            indicators.append(error_indicator)
        
        return indicators
    
    def _initialize_mock_detection_patterns(self) -> Dict[str, Pattern]:
        """Initialize regex patterns for mock data detection"""
        
        patterns = {}
        
        # Email patterns
        patterns['mock_emails'] = re.compile(r'test@example\.com|user@test\.com|mock@mock\.com|fake@fake\.com', re.IGNORECASE)
        
        # URL patterns
        patterns['mock_urls'] = re.compile(r'localhost|127\.0\.0\.1|example\.com|test\.com|mock\.api', re.IGNORECASE)
        
        # ID patterns
        patterns['sequential_ids'] = re.compile(r'"id":\s*[123456789]+|"user_id":\s*[123456789]+', re.IGNORECASE)
        
        # Phone patterns
        patterns['mock_phones'] = re.compile(r'555-\d{4}|\(555\)\s*\d{3}-\d{4}|1234567890', re.IGNORECASE)
        
        # Name patterns
        patterns['mock_names'] = re.compile(r'john doe|jane doe|test user|mock user|fake name', re.IGNORECASE)
        
        # Response patterns
        patterns['mock_responses'] = re.compile(r'"success":\s*true|"status":\s*"ok"|"result":\s*"success"', re.IGNORECASE)
        
        return patterns
    
    def _initialize_suspicious_patterns(self) -> List[str]:
        """Initialize patterns that indicate potential fabrication"""
        
        return [
            'mock',
            'fake',
            'test_data',
            'dummy',
            'placeholder',
            'example',
            'sample_data',
            'fabricated',
            'artificial',
            'generated'
        ]
    
    def _initialize_fabrication_keywords(self) -> List[str]:
        """Initialize keywords that suggest fabrication"""
        
        return [
            'simulate',
            'pretend',
            'assume',
            'hypothetical',
            'theoretical',
            'pseudo',
            'virtual',
            'emulated'
        ]
    
    def _analyze_fabrication_indicators(self, report: FabricationReport):
        """Analyze indicators and update report summary"""
        
        report.total_indicators = len(report.fabrication_indicators)
        
        # Count by severity
        severity_counts = {}
        for indicator in report.fabrication_indicators:
            severity = indicator.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        report.indicators_by_severity = severity_counts
        
        # Count by type
        type_counts = {}
        for indicator in report.fabrication_indicators:
            fab_type = indicator.fabrication_type.value
            type_counts[fab_type] = type_counts.get(fab_type, 0) + 1
        
        report.indicators_by_type = type_counts
        
        # Determine highest severity
        if report.fabrication_indicators:
            severities = [indicator.severity for indicator in report.fabrication_indicators]
            severity_order = [FabricationSeverity.CRITICAL, FabricationSeverity.HIGH, 
                            FabricationSeverity.MEDIUM, FabricationSeverity.LOW, FabricationSeverity.NONE]
            
            for severity in severity_order:
                if severity in severities:
                    report.highest_severity = severity
                    break
        
        # Calculate overall confidence
        if report.fabrication_indicators:
            confidence_scores = [indicator.confidence_score for indicator in report.fabrication_indicators]
            report.confidence_level = max(confidence_scores)
        
        # Determine overall fabrication status
        critical_indicators = [i for i in report.fabrication_indicators if i.severity == FabricationSeverity.CRITICAL]
        high_indicators = [i for i in report.fabrication_indicators if i.severity == FabricationSeverity.HIGH]
        
        report.overall_fabrication_detected = (
            len(critical_indicators) > 0 or 
            len(high_indicators) >= 2 or
            report.confidence_level > 0.8
        )
    
    def _initialize_foundation_components(self):
        """Initialize required foundation components"""
        
        from ..utils.json_utils import JSONUtilities
        
        self.json_utils = JSONUtilities()
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _analyze_success_patterns(self, evidence_data: Dict[str, Any]) -> List[FabricationIndicator]:
        """Analyze patterns in success/failure rates"""
        return []
    
    def _analyze_perfect_test_results(self, evidence: 'EvidenceRecord') -> Optional[FabricationIndicator]:
        """Analyze evidence for suspiciously perfect test results"""
        return None
    
    def _validate_test_framework_output(self, output: str) -> bool:
        """Validate that test output matches expected framework patterns"""
        return True
    
    def _analyze_file_content_for_fabrication(self, content: str, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """Analyze file content for fabrication indicators"""
        return []
    
    def _detect_timestamp_tampering(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """Detect evidence of timestamp manipulation"""
        return []
    
    def _detect_simulated_external_responses(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """Detect simulated external API responses"""
        return []
    
    def _detect_circular_validation(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """Detect circular validation patterns"""
        return []
    
    def _detect_incomplete_implementation(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """Detect incomplete implementations masquerading as complete"""
        return []
    
    def _detect_hidden_failures(self, evidence: 'EvidenceRecord') -> List[FabricationIndicator]:
        """Detect hidden or suppressed failure information"""
        return []
    
    def _generate_fabrication_recommendations(self, report: FabricationReport):
        """Generate recommendations based on fabrication detection results"""
        
        if report.overall_fabrication_detected:
            report.recommended_actions.append("Investigate evidence authenticity before accepting results")
            report.investigation_priority = "high"
        
        if report.highest_severity == FabricationSeverity.CRITICAL:
            report.recommended_actions.append("Immediately halt autonomous execution and investigate")
            report.investigation_priority = "critical"
        
        if 'mock_data_masquerading' in report.indicators_by_type:
            report.recommended_actions.append("Verify real data is being used instead of mock data")
        
        if 'false_test_results' in report.indicators_by_type:
            report.recommended_actions.append("Re-run tests in clean environment to verify results")