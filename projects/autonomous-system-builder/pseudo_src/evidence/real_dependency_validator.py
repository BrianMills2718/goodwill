#!/usr/bin/env python3
"""
REAL DEPENDENCY VALIDATOR - Evidence System Layer
Validation of external dependencies and real service integration

RELATES_TO: evidence_collector.py, anti_fabrication.py, ../config/config_manager.py
"""

import os
import json
import logging
import hashlib
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import urllib.parse

class DependencyType(Enum):
    """Types of external dependencies to validate"""
    PYTHON_PACKAGE = "python_package"
    NPM_PACKAGE = "npm_package"
    SYSTEM_BINARY = "system_binary"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    NETWORK_SERVICE = "network_service"
    ENVIRONMENT_VARIABLE = "environment_variable"

class ValidationMethod(Enum):
    """Methods for validating dependencies"""
    IMPORT_TEST = "import_test"
    VERSION_CHECK = "version_check"
    API_CALL = "api_call"
    CONNECTIVITY_TEST = "connectivity_test"
    EXISTENCE_CHECK = "existence_check"
    FUNCTIONALITY_TEST = "functionality_test"

class DependencyStatus(Enum):
    """Status of dependency validation"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIALLY_AVAILABLE = "partially_available"
    VERSION_MISMATCH = "version_mismatch"
    AUTHENTICATION_REQUIRED = "authentication_required"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"

@dataclass
class DependencyRequirement:
    """Specification for a required dependency"""
    dependency_id: str
    dependency_type: DependencyType
    name: str
    validation_method: ValidationMethod
    
    # Version requirements
    required_version: Optional[str] = None
    minimum_version: Optional[str] = None
    maximum_version: Optional[str] = None
    version_pattern: Optional[str] = None
    
    # Connection details
    endpoint_url: Optional[str] = None
    authentication_required: bool = False
    timeout_seconds: int = 30
    
    # Validation criteria
    expected_response: Optional[str] = None
    success_indicators: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    
    # Optional vs required
    is_critical: bool = True
    fallback_available: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dependency_id': self.dependency_id,
            'dependency_type': self.dependency_type.value,
            'name': self.name,
            'validation_method': self.validation_method.value,
            'required_version': self.required_version,
            'minimum_version': self.minimum_version,
            'maximum_version': self.maximum_version,
            'version_pattern': self.version_pattern,
            'endpoint_url': self.endpoint_url,
            'authentication_required': self.authentication_required,
            'timeout_seconds': self.timeout_seconds,
            'expected_response': self.expected_response,
            'success_indicators': self.success_indicators,
            'failure_indicators': self.failure_indicators,
            'is_critical': self.is_critical,
            'fallback_available': self.fallback_available
        }

@dataclass
class DependencyValidationResult:
    """Result of dependency validation"""
    dependency_id: str
    status: DependencyStatus
    validation_time: str
    
    # Version information
    detected_version: Optional[str] = None
    version_compatible: bool = True
    
    # Validation details
    validation_method_used: ValidationMethod = ValidationMethod.EXISTENCE_CHECK
    validation_duration: float = 0.0
    response_data: Dict[str, Any] = field(default_factory=dict)
    
    # Status details
    status_message: str = ""
    error_details: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Connectivity information
    endpoint_reachable: bool = True
    response_time_ms: Optional[float] = None
    response_size_bytes: Optional[int] = None
    
    # Quality assessment
    confidence_score: float = 1.0  # 0.0 to 1.0
    evidence_quality: str = "high"  # high, medium, low
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dependency_id': self.dependency_id,
            'status': self.status.value,
            'validation_time': self.validation_time,
            'detected_version': self.detected_version,
            'version_compatible': self.version_compatible,
            'validation_method_used': self.validation_method_used.value,
            'validation_duration': self.validation_duration,
            'response_data': self.response_data,
            'status_message': self.status_message,
            'error_details': self.error_details,
            'warnings': self.warnings,
            'endpoint_reachable': self.endpoint_reachable,
            'response_time_ms': self.response_time_ms,
            'response_size_bytes': self.response_size_bytes,
            'confidence_score': self.confidence_score,
            'evidence_quality': self.evidence_quality
        }

class RealDependencyValidatorError(Exception):
    """Raised when dependency validation operations fail"""
    pass

class RealDependencyValidator:
    """
    Validator for external dependencies and real service integration
    
    EVIDENCE SYSTEM COMPONENT: Validates real external dependencies
    Prevents autonomous system from claiming success with mock or fake dependencies
    """
    
    def __init__(self, project_root: str):
        """
        Initialize real dependency validator
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Initializes dependency detection and validation systems
        - Sets up authentication and rate limiting management
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise RealDependencyValidatorError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise RealDependencyValidatorError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise RealDependencyValidatorError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Validation configuration
        self.enable_network_validation = True
        self.enable_version_checking = True
        self.enable_functionality_testing = True
        self.respect_rate_limits = True
        
        # Timeout and retry configuration
        self.default_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Authentication management
        self.api_credentials = {}
        self.rate_limit_tracking = {}
        
        # Dependency cache
        self.validation_cache = {}
        self.cache_expiry_hours = 1
        
        # Validation history
        self.validation_history = []
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def validate_dependencies(self, requirements: List[DependencyRequirement]) -> Dict[str, DependencyValidationResult]:
        """
        Validate multiple dependencies according to requirements
        
        PARAMETERS:
        - requirements: List of dependency requirements to validate
        
        RETURNS: Dictionary mapping dependency IDs to validation results
        
        VALIDATION PROCESS:
        1. Load cached results for recent validations
        2. Group dependencies by validation method for efficiency
        3. Execute validation for each dependency
        4. Assess overall dependency health
        5. Cache results for future use
        """
        
        try:
            self.logger.info(f"Validating {len(requirements)} dependencies")
            
            validation_results = {}
            
            # Process each dependency requirement
            for requirement in requirements:
                try:
                    # Check cache first
                    cached_result = self._get_cached_validation(requirement.dependency_id)
                    if cached_result:
                        validation_results[requirement.dependency_id] = cached_result
                        continue
                    
                    # Perform fresh validation
                    result = self._validate_single_dependency(requirement)
                    validation_results[requirement.dependency_id] = result
                    
                    # Cache the result
                    self._cache_validation_result(result)
                    
                    # Add to history
                    self.validation_history.append(result)
                    
                except Exception as e:
                    # Create error result for failed validation
                    error_result = DependencyValidationResult(
                        dependency_id=requirement.dependency_id,
                        status=DependencyStatus.UNKNOWN,
                        validation_time=datetime.now(timezone.utc).isoformat(),
                        error_details=str(e),
                        status_message=f"Validation failed: {str(e)}",
                        confidence_score=0.0,
                        evidence_quality="low"
                    )
                    
                    validation_results[requirement.dependency_id] = error_result
            
            self.logger.info(f"Dependency validation completed: {len(validation_results)} results")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Dependency validation failed: {str(e)}")
            raise RealDependencyValidatorError(f"Failed to validate dependencies: {str(e)}")
    
    def validate_project_dependencies(self) -> Dict[str, Any]:
        """
        Auto-detect and validate all project dependencies
        
        RETURNS: Comprehensive validation report for all detected dependencies
        
        AUTO-DETECTION PROCESS:
        1. Scan project files for dependency declarations
        2. Parse package managers and configuration files
        3. Extract import statements and API usage
        4. Generate validation requirements automatically
        5. Execute comprehensive validation
        """
        
        try:
            self.logger.info("Auto-detecting project dependencies")
            
            # Detect dependencies from various sources
            detected_requirements = []
            
            # Python dependencies
            python_deps = self._detect_python_dependencies()
            detected_requirements.extend(python_deps)
            
            # JavaScript/Node.js dependencies
            js_deps = self._detect_javascript_dependencies()
            detected_requirements.extend(js_deps)
            
            # System dependencies
            system_deps = self._detect_system_dependencies()
            detected_requirements.extend(system_deps)
            
            # External API dependencies
            api_deps = self._detect_api_dependencies()
            detected_requirements.extend(api_deps)
            
            # Environment variable dependencies
            env_deps = self._detect_environment_dependencies()
            detected_requirements.extend(env_deps)
            
            # Validate all detected dependencies
            validation_results = self.validate_dependencies(detected_requirements)
            
            # Generate comprehensive report
            report = self._generate_validation_report(validation_results, detected_requirements)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Project dependency validation failed: {str(e)}")
            return {
                'error': str(e),
                'total_dependencies': 0,
                'validation_status': 'failed'
            }
    
    def _validate_single_dependency(self, requirement: DependencyRequirement) -> DependencyValidationResult:
        """
        Validate a single dependency according to its requirements
        
        PARAMETERS:
        - requirement: Dependency requirement specification
        
        RETURNS: Detailed validation result
        """
        
        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Validating dependency: {requirement.dependency_id}")
            
            # Choose validation method
            if requirement.validation_method == ValidationMethod.IMPORT_TEST:
                result = self._validate_import_dependency(requirement)
            elif requirement.validation_method == ValidationMethod.VERSION_CHECK:
                result = self._validate_version_dependency(requirement)
            elif requirement.validation_method == ValidationMethod.API_CALL:
                result = self._validate_api_dependency(requirement)
            elif requirement.validation_method == ValidationMethod.CONNECTIVITY_TEST:
                result = self._validate_connectivity_dependency(requirement)
            elif requirement.validation_method == ValidationMethod.EXISTENCE_CHECK:
                result = self._validate_existence_dependency(requirement)
            elif requirement.validation_method == ValidationMethod.FUNCTIONALITY_TEST:
                result = self._validate_functionality_dependency(requirement)
            else:
                result = self._validate_generic_dependency(requirement)
            
            # Calculate validation duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result.validation_duration = duration
            
            # Set validation metadata
            result.validation_method_used = requirement.validation_method
            result.validation_time = start_time.isoformat()
            
            self.logger.debug(f"Dependency validation completed: {requirement.dependency_id} - {result.status.value}")
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNKNOWN,
                validation_time=start_time.isoformat(),
                validation_method_used=requirement.validation_method,
                error_details=str(e),
                status_message=f"Validation error: {str(e)}",
                confidence_score=0.0,
                evidence_quality="low"
            )
            
            return error_result
    
    def _validate_import_dependency(self, requirement: DependencyRequirement) -> DependencyValidationResult:
        """
        Validate dependency by attempting to import it
        
        IMPORT VALIDATION:
        1. Attempt to import the specified module/package
        2. Check for version information if available
        3. Verify basic functionality with simple calls
        4. Detect mock or stub implementations
        """
        
        try:
            # For Python packages
            if requirement.dependency_type == DependencyType.PYTHON_PACKAGE:
                result = self._validate_python_import(requirement)
            else:
                result = DependencyValidationResult(
                    dependency_id=requirement.dependency_id,
                    status=DependencyStatus.UNKNOWN,
                    status_message="Import validation not supported for this dependency type"
                )
            
            return result
            
        except Exception as e:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNAVAILABLE,
                error_details=str(e),
                status_message=f"Import validation failed: {str(e)}",
                confidence_score=0.8,  # High confidence in negative result
                evidence_quality="high"
            )
    
    def _validate_python_import(self, requirement: DependencyRequirement) -> DependencyValidationResult:
        """Validate Python package import"""
        
        try:
            # Execute import test in subprocess to avoid polluting namespace
            import_script = f"""
import sys
try:
    import {requirement.name}
    
    # Get version if available
    version = None
    if hasattr({requirement.name}, '__version__'):
        version = {requirement.name}.__version__
    elif hasattr({requirement.name}, 'version'):
        version = {requirement.name}.version
    elif hasattr({requirement.name}, 'VERSION'):
        version = {requirement.name}.VERSION
    
    # Check if it's a mock implementation
    is_mock = False
    if hasattr({requirement.name}, '__file__'):
        file_path = {requirement.name}.__file__
        is_mock = 'mock' in file_path.lower() or 'fake' in file_path.lower()
    
    print(f"SUCCESS|{{version}}|{{is_mock}}")
    
except ImportError as e:
    print(f"IMPORT_ERROR|{{str(e)}}")
except Exception as e:
    print(f"ERROR|{{str(e)}}")
"""
            
            result = subprocess.run(
                [sys.executable, '-c', import_script],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            output = result.stdout.strip()
            
            if output.startswith('SUCCESS'):
                parts = output.split('|')
                version = parts[1] if len(parts) > 1 and parts[1] != 'None' else None
                is_mock = parts[2] == 'True' if len(parts) > 2 else False
                
                # Check version compatibility
                version_compatible = self._check_version_compatibility(
                    version, requirement.required_version, 
                    requirement.minimum_version, requirement.maximum_version
                )
                
                # Determine status
                if is_mock:
                    status = DependencyStatus.PARTIALLY_AVAILABLE
                    status_message = "Package imported but appears to be a mock implementation"
                    confidence_score = 0.3
                    evidence_quality = "low"
                elif not version_compatible:
                    status = DependencyStatus.VERSION_MISMATCH
                    status_message = f"Version mismatch: detected {version}, required {requirement.required_version}"
                    confidence_score = 0.7
                    evidence_quality = "medium"
                else:
                    status = DependencyStatus.AVAILABLE
                    status_message = f"Package successfully imported"
                    confidence_score = 0.9
                    evidence_quality = "high"
                
                return DependencyValidationResult(
                    dependency_id=requirement.dependency_id,
                    status=status,
                    detected_version=version,
                    version_compatible=version_compatible,
                    status_message=status_message,
                    confidence_score=confidence_score,
                    evidence_quality=evidence_quality,
                    response_data={'is_mock': is_mock, 'import_successful': True}
                )
            
            elif output.startswith('IMPORT_ERROR'):
                error_msg = output.split('|')[1] if '|' in output else "Unknown import error"
                
                return DependencyValidationResult(
                    dependency_id=requirement.dependency_id,
                    status=DependencyStatus.UNAVAILABLE,
                    status_message=f"Import failed: {error_msg}",
                    error_details=error_msg,
                    confidence_score=0.9,
                    evidence_quality="high"
                )
            
            else:
                return DependencyValidationResult(
                    dependency_id=requirement.dependency_id,
                    status=DependencyStatus.UNKNOWN,
                    status_message="Unexpected import test result",
                    error_details=result.stderr,
                    confidence_score=0.2,
                    evidence_quality="low"
                )
            
        except subprocess.TimeoutExpired:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNKNOWN,
                status_message="Import test timeout",
                confidence_score=0.3,
                evidence_quality="low"
            )
        
        except Exception as e:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNKNOWN,
                error_details=str(e),
                status_message=f"Import validation error: {str(e)}",
                confidence_score=0.1,
                evidence_quality="low"
            )
    
    def _validate_api_dependency(self, requirement: DependencyRequirement) -> DependencyValidationResult:
        """
        Validate external API dependency
        
        API VALIDATION:
        1. Test connectivity to API endpoint
        2. Verify authentication if required
        3. Check API response format and content
        4. Measure response time and reliability
        """
        
        if not requirement.endpoint_url:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNKNOWN,
                status_message="No endpoint URL provided for API validation"
            )
        
        try:
            start_time = datetime.now()
            
            # Prepare request headers
            headers = {'User-Agent': 'Autonomous-TDD-Validator/1.0'}
            
            # Add authentication if required
            if requirement.authentication_required:
                auth_result = self._get_api_authentication(requirement)
                if not auth_result['success']:
                    return DependencyValidationResult(
                        dependency_id=requirement.dependency_id,
                        status=DependencyStatus.AUTHENTICATION_REQUIRED,
                        status_message=auth_result['message'],
                        confidence_score=0.8,
                        evidence_quality="high"
                    )
                headers.update(auth_result['headers'])
            
            # Make API request
            response = requests.get(
                requirement.endpoint_url,
                headers=headers,
                timeout=requirement.timeout_seconds
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            # Analyze response
            if response.status_code == 200:
                status = DependencyStatus.AVAILABLE
                status_message = f"API accessible (HTTP {response.status_code})"
                confidence_score = 0.9
                evidence_quality = "high"
            elif response.status_code == 401:
                status = DependencyStatus.AUTHENTICATION_REQUIRED
                status_message = "API requires authentication"
                confidence_score = 0.8
                evidence_quality = "high"
            elif response.status_code == 429:
                status = DependencyStatus.RATE_LIMITED
                status_message = "API rate limit exceeded"
                confidence_score = 0.7
                evidence_quality = "medium"
            elif 400 <= response.status_code < 500:
                status = DependencyStatus.PARTIALLY_AVAILABLE
                status_message = f"API client error (HTTP {response.status_code})"
                confidence_score = 0.6
                evidence_quality = "medium"
            else:
                status = DependencyStatus.UNAVAILABLE
                status_message = f"API server error (HTTP {response.status_code})"
                confidence_score = 0.8
                evidence_quality = "high"
            
            # Check for expected response content
            if requirement.expected_response and status == DependencyStatus.AVAILABLE:
                response_text = response.text
                if requirement.expected_response not in response_text:
                    status = DependencyStatus.PARTIALLY_AVAILABLE
                    status_message += " (unexpected response content)"
                    confidence_score = 0.5
                    evidence_quality = "medium"
            
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=status,
                status_message=status_message,
                endpoint_reachable=True,
                response_time_ms=response_time,
                response_size_bytes=len(response.content),
                confidence_score=confidence_score,
                evidence_quality=evidence_quality,
                response_data={
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content_type': response.headers.get('content-type', ''),
                    'response_preview': response.text[:500] if response.text else ''
                }
            )
            
        except requests.exceptions.Timeout:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNAVAILABLE,
                status_message="API request timeout",
                endpoint_reachable=False,
                confidence_score=0.8,
                evidence_quality="high"
            )
        
        except requests.exceptions.ConnectionError:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNAVAILABLE,
                status_message="Cannot connect to API endpoint",
                endpoint_reachable=False,
                confidence_score=0.9,
                evidence_quality="high"
            )
        
        except Exception as e:
            return DependencyValidationResult(
                dependency_id=requirement.dependency_id,
                status=DependencyStatus.UNKNOWN,
                error_details=str(e),
                status_message=f"API validation error: {str(e)}",
                confidence_score=0.2,
                evidence_quality="low"
            )
    
    def _detect_python_dependencies(self) -> List[DependencyRequirement]:
        """Detect Python package dependencies from project files"""
        
        requirements = []
        
        try:
            # Check requirements.txt
            req_file = self.project_root / 'requirements.txt'
            if req_file.exists():
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            package_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                            
                            requirement = DependencyRequirement(
                                dependency_id=f"python_{package_name}",
                                dependency_type=DependencyType.PYTHON_PACKAGE,
                                name=package_name,
                                validation_method=ValidationMethod.IMPORT_TEST,
                                is_critical=True
                            )
                            
                            requirements.append(requirement)
            
            # Check setup.py and pyproject.toml
            # Implementation would parse these files for dependencies
            
        except Exception as e:
            self.logger.warning(f"Failed to detect Python dependencies: {str(e)}")
        
        return requirements
    
    def _initialize_foundation_components(self):
        """Initialize required foundation components"""
        
        from ..utils.json_utils import JSONUtilities
        
        self.json_utils = JSONUtilities()
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _detect_javascript_dependencies(self) -> List[DependencyRequirement]:
        """Detect JavaScript/Node.js dependencies"""
        return []
    
    def _detect_system_dependencies(self) -> List[DependencyRequirement]:
        """Detect system binary dependencies"""
        return []
    
    def _detect_api_dependencies(self) -> List[DependencyRequirement]:
        """Detect external API dependencies from code"""
        return []
    
    def _detect_environment_dependencies(self) -> List[DependencyRequirement]:
        """Detect required environment variables"""
        return []
    
    def _check_version_compatibility(self, detected: Optional[str], required: Optional[str], 
                                   minimum: Optional[str], maximum: Optional[str]) -> bool:
        """Check if detected version meets requirements"""
        return True  # Simplified for pseudocode
    
    def _get_api_authentication(self, requirement: DependencyRequirement) -> Dict[str, Any]:
        """Get authentication headers for API requests"""
        return {'success': True, 'headers': {}, 'message': 'No auth required'}
    
    def _generate_validation_report(self, results: Dict[str, DependencyValidationResult], 
                                  requirements: List[DependencyRequirement]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        total_deps = len(results)
        available_deps = len([r for r in results.values() if r.status == DependencyStatus.AVAILABLE])
        
        return {
            'total_dependencies': total_deps,
            'available_dependencies': available_deps,
            'availability_rate': (available_deps / total_deps * 100) if total_deps > 0 else 0,
            'validation_status': 'completed',
            'detailed_results': {dep_id: result.to_dict() for dep_id, result in results.items()}
        }