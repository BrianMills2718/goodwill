#!/usr/bin/env python3
"""
TEST RUNNER - Evidence System Layer
Test framework integration and execution management

RELATES_TO: evidence_collector.py, ../config/config_manager.py, ../utils/json_utils.py
"""

import os
import sys
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

class TestFramework(Enum):
    """Supported test frameworks"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"
    GOLANG_TEST = "go_test"
    CARGO_TEST = "cargo_test"
    UNKNOWN = "unknown"

class TestExecutionStatus(Enum):
    """Status of test execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class TestConfiguration:
    """Configuration for test execution"""
    framework: TestFramework
    test_command: List[str]
    test_directory: str
    timeout_seconds: int = 300
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
    # Test selection
    test_patterns: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    test_functions: List[str] = field(default_factory=list)
    
    # Output configuration
    capture_output: bool = True
    verbose_output: bool = False
    generate_coverage: bool = False
    coverage_threshold: float = 0.0
    
    # Quality requirements
    require_all_tests_pass: bool = True
    allow_skipped_tests: bool = True
    max_allowed_failures: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'framework': self.framework.value,
            'test_command': self.test_command,
            'test_directory': self.test_directory,
            'timeout_seconds': self.timeout_seconds,
            'environment_variables': self.environment_variables,
            'test_patterns': self.test_patterns,
            'test_files': self.test_files,
            'test_functions': self.test_functions,
            'capture_output': self.capture_output,
            'verbose_output': self.verbose_output,
            'generate_coverage': self.generate_coverage,
            'coverage_threshold': self.coverage_threshold,
            'require_all_tests_pass': self.require_all_tests_pass,
            'allow_skipped_tests': self.allow_skipped_tests,
            'max_allowed_failures': self.max_allowed_failures
        }

@dataclass
class TestResult:
    """Result of test execution"""
    execution_id: str
    framework: TestFramework
    status: TestExecutionStatus
    
    # Execution metadata
    start_time: str
    end_time: Optional[str] = None
    execution_duration: float = 0.0
    
    # Test counts
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    tests_error: int = 0
    
    # Test output
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    
    # Coverage information
    coverage_percentage: Optional[float] = None
    coverage_report: Dict[str, Any] = field(default_factory=dict)
    
    # Test details
    failed_tests: List[str] = field(default_factory=list)
    error_tests: List[str] = field(default_factory=list)
    skipped_tests: List[str] = field(default_factory=list)
    
    # Performance metrics
    slowest_tests: List[Dict[str, Any]] = field(default_factory=list)
    memory_usage: Optional[float] = None
    
    # Quality assessment
    quality_score: float = 0.0
    quality_issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_id': self.execution_id,
            'framework': self.framework.value,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'execution_duration': self.execution_duration,
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'tests_skipped': self.tests_skipped,
            'tests_error': self.tests_error,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exit_code': self.exit_code,
            'coverage_percentage': self.coverage_percentage,
            'coverage_report': self.coverage_report,
            'failed_tests': self.failed_tests,
            'error_tests': self.error_tests,
            'skipped_tests': self.skipped_tests,
            'slowest_tests': self.slowest_tests,
            'memory_usage': self.memory_usage,
            'quality_score': self.quality_score,
            'quality_issues': self.quality_issues
        }

class TestRunnerError(Exception):
    """Raised when test runner operations fail"""
    pass

class AutonomousTestRunner:
    """
    Test framework integration and execution management for autonomous TDD
    
    EVIDENCE SYSTEM COMPONENT: Executes tests and collects evidence
    Integrates with multiple test frameworks to provide consistent evidence collection
    """
    
    def __init__(self, project_root: str):
        """
        Initialize autonomous test runner
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists and is accessible
        - Detects available test frameworks
        - Initializes test execution configuration
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise TestRunnerError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise TestRunnerError(f"Project root does not exist: {project_root}")
        
        if not self.project_root.is_dir():
            raise TestRunnerError(f"Project root is not a directory: {project_root}")
        
        # Initialize foundation components
        self._initialize_foundation_components()
        
        # Test execution state
        self.active_executions = {}
        self.execution_history = []
        
        # Framework detection
        self.detected_frameworks = self._detect_available_frameworks()
        self.default_framework = self._determine_default_framework()
        
        # Test configuration
        self.test_timeout = 300  # 5 minutes default
        self.max_concurrent_executions = 3
        self.enable_coverage_collection = True
        
        # Test result storage
        self.results_dir = self.project_root / 'logs' / 'test_results'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def execute_tests(self, config: TestConfiguration) -> TestResult:
        """
        Execute tests according to configuration and collect results
        
        PARAMETERS:
        - config: Test execution configuration
        
        RETURNS: Comprehensive test execution results
        
        EXECUTION PROCESS:
        1. Validate test configuration and environment
        2. Set up test execution environment
        3. Execute tests with monitoring and timeout
        4. Parse test output and extract metrics
        5. Generate comprehensive test result report
        """
        
        try:
            execution_id = f"test_{int(datetime.now().timestamp())}_{config.framework.value}"
            
            self.logger.info(f"Starting test execution: {execution_id}")
            
            # Create test result object
            result = TestResult(
                execution_id=execution_id,
                framework=config.framework,
                status=TestExecutionStatus.PENDING,
                start_time=datetime.now(timezone.utc).isoformat()
            )
            
            # Validate test configuration
            validation_result = self._validate_test_configuration(config)
            if not validation_result['valid']:
                result.status = TestExecutionStatus.FAILED
                result.quality_issues.extend(validation_result['errors'])
                return result
            
            # Prepare test execution environment
            test_env = self._prepare_test_environment(config)
            
            # Mark execution as running
            result.status = TestExecutionStatus.RUNNING
            self.active_executions[execution_id] = result
            
            # Execute tests with monitoring
            execution_result = self._execute_test_command(config, test_env)
            
            # Update result with execution data
            result.end_time = datetime.now(timezone.utc).isoformat()
            result.execution_duration = execution_result['duration']
            result.stdout = execution_result['stdout']
            result.stderr = execution_result['stderr']
            result.exit_code = execution_result['exit_code']
            
            # Parse test output based on framework
            parsing_result = self._parse_test_output(config.framework, execution_result)
            self._update_result_with_parsing(result, parsing_result)
            
            # Collect coverage information if enabled
            if config.generate_coverage:
                coverage_result = self._collect_coverage_information(config)
                result.coverage_percentage = coverage_result.get('percentage')
                result.coverage_report = coverage_result.get('report', {})
            
            # Assess test quality
            quality_assessment = self._assess_test_quality(result, config)
            result.quality_score = quality_assessment['score']
            result.quality_issues.extend(quality_assessment['issues'])
            
            # Determine final status
            if execution_result['timeout']:
                result.status = TestExecutionStatus.TIMEOUT
            elif result.exit_code == 0 and result.tests_failed == 0:
                result.status = TestExecutionStatus.COMPLETED
            else:
                result.status = TestExecutionStatus.FAILED
            
            # Save test result
            self._save_test_result(result)
            
            # Clean up active execution
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            self.execution_history.append(result)
            
            self.logger.info(f"Test execution completed: {execution_id} - {result.status.value}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            
            # Return error result
            error_result = TestResult(
                execution_id=f"error_{int(datetime.now().timestamp())}",
                framework=config.framework,
                status=TestExecutionStatus.FAILED,
                start_time=datetime.now(timezone.utc).isoformat(),
                end_time=datetime.now(timezone.utc).isoformat(),
                stderr=f"Test execution error: {str(e)}",
                quality_issues=[f"Execution failed: {str(e)}"]
            )
            
            return error_result
    
    def execute_specific_tests(self, test_files: List[str], 
                              framework: Optional[TestFramework] = None) -> TestResult:
        """
        Execute specific test files or functions
        
        PARAMETERS:
        - test_files: List of specific test files to execute
        - framework: Test framework to use (auto-detect if None)
        
        RETURNS: Test execution results for specified tests
        """
        
        try:
            # Determine framework if not specified
            if framework is None:
                framework = self._detect_framework_for_files(test_files)
            
            # Create configuration for specific tests
            config = self._create_test_configuration_for_files(test_files, framework)
            
            # Execute tests
            return self.execute_tests(config)
            
        except Exception as e:
            self.logger.error(f"Specific test execution failed: {str(e)}")
            
            return TestResult(
                execution_id=f"specific_error_{int(datetime.now().timestamp())}",
                framework=framework or TestFramework.UNKNOWN,
                status=TestExecutionStatus.FAILED,
                start_time=datetime.now(timezone.utc).isoformat(),
                end_time=datetime.now(timezone.utc).isoformat(),
                stderr=f"Specific test execution error: {str(e)}"
            )
    
    def get_test_summary(self, time_range_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get summary of test executions
        
        PARAMETERS:
        - time_range_hours: Only include executions within this time range
        
        RETURNS: Comprehensive summary of test execution history
        """
        
        try:
            # Filter executions by time range if specified
            if time_range_hours:
                cutoff_time = datetime.now(timezone.utc).timestamp() - (time_range_hours * 3600)
                relevant_executions = [
                    result for result in self.execution_history
                    if datetime.fromisoformat(result.start_time.replace('Z', '+00:00')).timestamp() > cutoff_time
                ]
            else:
                relevant_executions = self.execution_history
            
            if not relevant_executions:
                return {
                    'total_executions': 0,
                    'summary': 'No test executions found'
                }
            
            # Calculate summary statistics
            total_executions = len(relevant_executions)
            successful_executions = len([r for r in relevant_executions if r.status == TestExecutionStatus.COMPLETED])
            failed_executions = len([r for r in relevant_executions if r.status == TestExecutionStatus.FAILED])
            
            total_tests = sum(r.tests_run for r in relevant_executions)
            total_passed = sum(r.tests_passed for r in relevant_executions)
            total_failed = sum(r.tests_failed for r in relevant_executions)
            total_skipped = sum(r.tests_skipped for r in relevant_executions)
            
            # Calculate averages
            avg_execution_time = sum(r.execution_duration for r in relevant_executions) / total_executions
            avg_quality_score = sum(r.quality_score for r in relevant_executions) / total_executions
            
            # Framework breakdown
            framework_stats = {}
            for result in relevant_executions:
                framework = result.framework.value
                if framework not in framework_stats:
                    framework_stats[framework] = {'executions': 0, 'success_rate': 0}
                framework_stats[framework]['executions'] += 1
                if result.status == TestExecutionStatus.COMPLETED:
                    framework_stats[framework]['success_rate'] += 1
            
            # Calculate success rates
            for framework_data in framework_stats.values():
                framework_data['success_rate'] = (
                    framework_data['success_rate'] / framework_data['executions'] * 100
                )
            
            summary = {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                'test_statistics': {
                    'total_tests': total_tests,
                    'total_passed': total_passed,
                    'total_failed': total_failed,
                    'total_skipped': total_skipped,
                    'pass_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
                },
                'performance_metrics': {
                    'average_execution_time': avg_execution_time,
                    'average_quality_score': avg_quality_score
                },
                'framework_breakdown': framework_stats,
                'time_range_hours': time_range_hours
            }
            
            return summary
            
        except Exception as e:
            return {
                'error': f"Failed to generate test summary: {str(e)}",
                'total_executions': len(self.execution_history)
            }
    
    def _detect_available_frameworks(self) -> List[TestFramework]:
        """Detect available test frameworks in the project"""
        
        frameworks = []
        
        try:
            # Check for Python test frameworks
            if (self.project_root / 'pytest.ini').exists() or \
               any(self.project_root.glob('**/conftest.py')):
                frameworks.append(TestFramework.PYTEST)
            
            if any(self.project_root.glob('**/test_*.py')) or \
               any(self.project_root.glob('**/*_test.py')):
                if TestFramework.PYTEST not in frameworks:
                    frameworks.append(TestFramework.UNITTEST)
            
            # Check for JavaScript test frameworks
            package_json = self.project_root / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                    
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    all_deps = {**dependencies, **dev_dependencies}
                    
                    if 'jest' in all_deps:
                        frameworks.append(TestFramework.JEST)
                    elif 'mocha' in all_deps:
                        frameworks.append(TestFramework.MOCHA)
                        
                except json.JSONDecodeError:
                    pass
            
            # Check for Go tests
            if any(self.project_root.glob('**/*_test.go')):
                frameworks.append(TestFramework.GOLANG_TEST)
            
            # Check for Rust tests
            if (self.project_root / 'Cargo.toml').exists():
                frameworks.append(TestFramework.CARGO_TEST)
            
            # Check for Java tests
            if any(self.project_root.glob('**/pom.xml')) or \
               any(self.project_root.glob('**/build.gradle')):
                frameworks.append(TestFramework.JUNIT)
            
        except Exception as e:
            self.logger.error(f"Framework detection failed: {str(e)}")
        
        return frameworks if frameworks else [TestFramework.UNKNOWN]
    
    def _determine_default_framework(self) -> TestFramework:
        """Determine the default test framework for the project"""
        
        if TestFramework.PYTEST in self.detected_frameworks:
            return TestFramework.PYTEST
        elif TestFramework.JEST in self.detected_frameworks:
            return TestFramework.JEST
        elif TestFramework.UNITTEST in self.detected_frameworks:
            return TestFramework.UNITTEST
        elif self.detected_frameworks:
            return self.detected_frameworks[0]
        else:
            return TestFramework.UNKNOWN
    
    def _execute_test_command(self, config: TestConfiguration, 
                             test_env: Dict[str, str]) -> Dict[str, Any]:
        """Execute test command with monitoring and timeout handling"""
        
        try:
            start_time = time.time()
            
            # Build complete command
            command = config.test_command.copy()
            
            # Add test-specific arguments
            if config.test_files:
                command.extend(config.test_files)
            elif config.test_patterns:
                for pattern in config.test_patterns:
                    command.extend(['-k', pattern])
            
            # Add verbosity if requested
            if config.verbose_output:
                if config.framework == TestFramework.PYTEST:
                    command.append('-v')
                elif config.framework == TestFramework.JEST:
                    command.append('--verbose')
            
            # Add coverage if requested
            if config.generate_coverage:
                if config.framework == TestFramework.PYTEST:
                    command.extend(['--cov', '.', '--cov-report', 'json'])
                elif config.framework == TestFramework.JEST:
                    command.append('--coverage')
            
            # Execute command
            result = subprocess.run(
                command,
                cwd=self.project_root,
                env=test_env,
                capture_output=config.capture_output,
                text=True,
                timeout=config.timeout_seconds
            )
            
            end_time = time.time()
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'duration': end_time - start_time,
                'timeout': False
            }
            
        except subprocess.TimeoutExpired as e:
            return {
                'stdout': e.stdout or '',
                'stderr': e.stderr or '',
                'exit_code': -1,
                'duration': config.timeout_seconds,
                'timeout': True
            }
        
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'exit_code': -2,
                'duration': 0.0,
                'timeout': False
            }
    
    def _parse_test_output(self, framework: TestFramework, 
                          execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse test output based on framework"""
        
        stdout = execution_result.get('stdout', '')
        stderr = execution_result.get('stderr', '')
        
        if framework == TestFramework.PYTEST:
            return self._parse_pytest_output(stdout, stderr)
        elif framework == TestFramework.JEST:
            return self._parse_jest_output(stdout, stderr)
        elif framework == TestFramework.UNITTEST:
            return self._parse_unittest_output(stdout, stderr)
        else:
            return self._parse_generic_output(stdout, stderr)
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse pytest output for test metrics"""
        
        parsing_result = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
            'tests_error': 0,
            'failed_tests': [],
            'error_tests': [],
            'skipped_tests': []
        }
        
        try:
            lines = stdout.splitlines()
            
            # Look for pytest summary line
            for line in lines:
                if '====' in line and ('passed' in line or 'failed' in line):
                    # Parse line like "==== 5 passed, 2 failed, 1 skipped in 1.23s ===="
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed' and i > 0:
                            parsing_result['tests_passed'] = int(parts[i-1])
                        elif part == 'failed' and i > 0:
                            parsing_result['tests_failed'] = int(parts[i-1])
                        elif part == 'skipped' and i > 0:
                            parsing_result['tests_skipped'] = int(parts[i-1])
                        elif part == 'error' and i > 0:
                            parsing_result['tests_error'] = int(parts[i-1])
            
            # Calculate total tests run
            parsing_result['tests_run'] = (
                parsing_result['tests_passed'] + 
                parsing_result['tests_failed'] + 
                parsing_result['tests_skipped'] + 
                parsing_result['tests_error']
            )
            
            # Extract failed test names
            in_failures = False
            for line in lines:
                if 'FAILURES' in line:
                    in_failures = True
                elif 'ERRORS' in line:
                    in_failures = False
                elif in_failures and line.startswith('_') and '::' in line:
                    test_name = line.split('::')[-1].strip('_')
                    if test_name:
                        parsing_result['failed_tests'].append(test_name)
            
        except Exception as e:
            self.logger.warning(f"Failed to parse pytest output: {str(e)}")
        
        return parsing_result
    
    def _initialize_foundation_components(self):
        """Initialize required foundation components"""
        
        from ..utils.json_utils import JSONUtilities
        
        self.json_utils = JSONUtilities()
    
    def _save_test_result(self, result: TestResult):
        """Save test result to disk"""
        
        try:
            result_file = self.results_dir / f"{result.execution_id}.json"
            result_data = result.to_dict()
            
            self.json_utils.save_json_file(result_data, str(result_file))
            
        except Exception as e:
            self.logger.error(f"Failed to save test result: {str(e)}")
    
    # Additional helper methods would be implemented here
    # These are abbreviated for space but would include full defensive programming
    
    def _validate_test_configuration(self, config: TestConfiguration) -> Dict[str, Any]:
        """Validate test configuration"""
        return {'valid': True, 'errors': []}
    
    def _prepare_test_environment(self, config: TestConfiguration) -> Dict[str, str]:
        """Prepare environment variables for test execution"""
        env = os.environ.copy()
        env.update(config.environment_variables)
        return env
    
    def _parse_jest_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse Jest output"""
        return {'tests_run': 0, 'tests_passed': 0, 'tests_failed': 0}
    
    def _parse_unittest_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse unittest output"""
        return {'tests_run': 0, 'tests_passed': 0, 'tests_failed': 0}
    
    def _parse_generic_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse generic test output"""
        return {'tests_run': 0, 'tests_passed': 0, 'tests_failed': 0}