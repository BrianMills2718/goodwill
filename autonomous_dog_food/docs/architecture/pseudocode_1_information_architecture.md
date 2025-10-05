# Pseudocode Part 1: Information Architecture Foundation

## Overview
Define the fundamental data structures and state representations that underpin the entire autonomous TDD system. This foundation enables all other system components.

## Core Data Structures

### 1. Project State (`ProjectState`)
```json
{
  "project_id": "string - unique identifier for project",
  "session_id": "string - current autonomous session identifier", 
  "current_phase": "integer - current methodology phase (1-9)",
  "methodology_step": "string - current step within phase",
  "project_root": "string - absolute path to project directory",
  "project_type": "string - detected project type (web_api, data_processing, cli_tool, etc.)",
  "autonomous_mode": "boolean - whether currently in autonomous mode",
  "session_start_time": "ISO timestamp - when autonomous session began",
  "last_activity_time": "ISO timestamp - last hook execution time",
  "total_hook_calls": "integer - number of hook executions this session",
  "blocking_status": {
    "is_blocked": "boolean - whether execution is currently blocked",
    "blocking_reason": "string - reason for blocking (missing_credentials, test_failures, etc.)",
    "blocking_details": "object - specific details about blocking condition",
    "escalation_message": "string - message to display to user for unblocking"
  },
  "configuration": {
    "max_hook_iterations": "integer - safety limit for hook calls",
    "max_failure_attempts": "integer - retry limit for failed operations", 
    "evidence_validation_strict": "boolean - strict vs permissive evidence validation",
    "external_dependency_timeout": "integer - seconds to wait for external services",
    "debug_mode": "boolean - whether to generate verbose debug logs"
  }
}
```

### 2. Task Dependency Graph (`TaskGraph`)
```json
{
  "graph_version": "string - version/timestamp of graph generation",
  "total_tasks": "integer - total number of tasks in graph",
  "completed_tasks": "integer - number of completed tasks",
  "current_task_id": "string - ID of currently executing task",
  "tasks": {
    "task_id": {
      "id": "string - unique task identifier",
      "title": "string - human-readable task description",
      "type": "string - task type (file_creation, implementation, test_execution, etc.)",
      "phase": "integer - methodology phase this task belongs to",
      "priority": "integer - execution priority (1-10)",
      "status": "string - pending|in_progress|completed|blocked|failed",
      "dependencies": ["array of task_ids that must complete first"],
      "dependents": ["array of task_ids that depend on this task"],
      "file_targets": ["array of file paths this task will create/modify"],
      "evidence_requirements": {
        "test_passage": "boolean - whether task requires passing tests",
        "file_existence": "boolean - whether task requires file creation",
        "external_validation": "boolean - whether task requires external service calls",
        "integration_proof": "boolean - whether task requires integration evidence"
      },
      "estimated_complexity": "string - simple|moderate|complex",
      "context_requirements": ["array of file paths needed for context"],
      "created_time": "ISO timestamp",
      "started_time": "ISO timestamp or null",
      "completed_time": "ISO timestamp or null",
      "failure_count": "integer - number of times this task has failed",
      "last_error": "string - last error message if task failed"
    }
  },
  "execution_order": ["ordered array of task_ids representing planned execution sequence"],
  "ready_tasks": ["array of task_ids that have all dependencies satisfied"],
  "blocked_tasks": ["array of task_ids that cannot proceed due to dependencies"]
}
```

### 3. Evidence Collection (`EvidenceRecord`)
```json
{
  "evidence_id": "string - unique evidence identifier",
  "task_id": "string - associated task ID",
  "collection_time": "ISO timestamp",
  "evidence_type": "string - completion|progress|validation|failure",
  "validation_status": "string - valid|invalid|pending|fabrication_detected",
  "test_evidence": {
    "framework": "string - pytest|jest|rspec|go_test|etc.",
    "execution_command": "string - exact command executed",
    "exit_code": "integer - test framework exit code",
    "stdout": "string - test output",
    "stderr": "string - test error output", 
    "execution_time_seconds": "number - test execution duration",
    "test_counts": {
      "total": "integer",
      "passed": "integer", 
      "failed": "integer",
      "skipped": "integer"
    },
    "failed_tests": ["array of failed test names with details"]
  },
  "anti_fabrication_checks": {
    "mock_usage_detected": "boolean - whether mocking libraries found in code",
    "mock_patterns": ["array of detected mock patterns"],
    "hardcoded_responses": "boolean - whether hardcoded test data detected",
    "network_activity_verified": "boolean - whether real external calls confirmed",
    "external_service_calls": ["array of confirmed external API calls"],
    "real_data_sources": ["array of confirmed real data sources"],
    "fabrication_risk_score": "integer 0-10 - risk of fabricated success"
  },
  "file_evidence": {
    "files_created": ["array of file paths created"],
    "files_modified": ["array of file paths modified"],
    "files_deleted": ["array of file paths deleted"],
    "file_existence_verified": "boolean - whether required files exist",
    "content_validation": {
      "non_empty_files": "integer - count of non-empty files created",
      "implementation_detected": "boolean - whether actual implementation vs stubs found",
      "cross_references_valid": "boolean - whether file cross-references are valid"
    }
  },
  "external_dependency_evidence": {
    "dependencies_tested": ["array of external dependencies validated"],
    "api_calls_successful": "boolean - whether external API calls succeeded", 
    "credentials_valid": "boolean - whether required credentials are present and valid",
    "service_availability": ["array of external services confirmed available"],
    "integration_proof": "boolean - whether end-to-end integration demonstrated"
  },
  "completion_assessment": {
    "completion_percentage": "number 0-100 - percentage of task completed",
    "completion_confidence": "string - low|medium|high",
    "blocking_issues": ["array of issues preventing completion"],
    "next_steps": ["array of recommended next actions"],
    "escalation_required": "boolean - whether human intervention needed"
  }
}
```

### 4. Cross-Reference Map (`CrossReferenceMap`)
```json
{
  "last_updated": "ISO timestamp",
  "validation_status": "string - valid|invalid|pending_validation",
  "file_relationships": {
    "file_path": {
      "file_type": "string - source|documentation|test|configuration",
      "relationships": {
        "documents": ["files this file documents or specifies"],
        "implements": ["files this file implements"],
        "tests": ["files that test this file"],
        "depends_on": ["files this file imports or requires"],
        "referenced_by": ["files that reference this file"],
        "configures": ["files this file configures"],
        "configured_by": ["files that configure this file"]
      },
      "relationship_strength": {
        "strong": ["files with explicit imports or direct dependencies"],
        "medium": ["files with cross-reference comments"],
        "weak": ["files with naming convention relationships"]
      },
      "last_modified": "ISO timestamp",
      "content_hash": "string - SHA-256 hash for change detection"
    }
  },
  "broken_references": ["array of file paths with invalid cross-references"],
  "orphaned_files": ["array of file paths with no relationships"],
  "circular_dependencies": ["array of circular dependency chains detected"]
}
```

### 5. External Dependencies (`DependencyManifest`)
```json
{
  "manifest_version": "string - version of dependency manifest",
  "last_updated": "ISO timestamp",
  "validation_status": "string - valid|invalid|blocked",
  "external_services": {
    "service_id": {
      "service_name": "string - human-readable service name",
      "service_type": "string - rest_api|database|file_system|cli_tool",
      "required": "boolean - whether service is required vs optional",
      "authentication": {
        "auth_type": "string - api_key|oauth2|basic|none",
        "required_credentials": ["array of required environment variables"],
        "validation_endpoint": "string - URL for testing credentials",
        "test_method": "string - method for validating service availability"
      },
      "integration_details": {
        "base_url": "string - service base URL",
        "rate_limits": "string - documented rate limiting",
        "timeout_seconds": "integer - recommended timeout",
        "retry_strategy": "string - recommended retry approach"
      },
      "validation_status": {
        "credentials_valid": "boolean - whether credentials are present and valid",
        "service_available": "boolean - whether service is accessible",
        "integration_tested": "boolean - whether integration has been tested",
        "last_validation_time": "ISO timestamp",
        "validation_error": "string - last validation error if any"
      },
      "documentation_file": "string - path to integration documentation",
      "code_usage": ["array of file paths that use this service"]
    }
  },
  "blocking_dependencies": ["array of service_ids that are blocking execution"],
  "optional_dependencies": ["array of service_ids that are optional"],
  "dependency_resolution_order": ["array of service_ids in resolution order"]
}
```

### 6. Configuration Schema (`SystemConfiguration`)
```json
{
  "config_version": "string - configuration schema version",
  "environment": "string - development|testing|production",
  "logging": {
    "log_level": "string - DEBUG|INFO|WARNING|ERROR",
    "structured_format": "boolean - whether to use JSON logging",
    "log_rotation": "boolean - whether to rotate log files",
    "max_log_size_mb": "integer - maximum log file size",
    "debug_components": ["array of components to enable debug logging for"]
  },
  "autonomous_behavior": {
    "max_session_duration_minutes": "integer - maximum autonomous session length",
    "max_hook_iterations": "integer - safety limit for hook calls",
    "max_consecutive_failures": "integer - failure limit before escalation",
    "evidence_validation_strictness": "string - strict|moderate|permissive",
    "auto_escalation_enabled": "boolean - whether to auto-escalate on blocking",
    "pause_on_uncertainty": "boolean - whether to pause when uncertain"
  },
  "integration_settings": {
    "claude_code_timeout_seconds": "integer - timeout for Claude Code operations",
    "test_framework_timeout_seconds": "integer - timeout for test execution",
    "external_service_timeout_seconds": "integer - timeout for external API calls",
    "file_operation_timeout_seconds": "integer - timeout for file operations"
  },
  "evidence_collection": {
    "enable_anti_fabrication": "boolean - whether to enable fabrication detection",
    "require_real_dependencies": "boolean - whether to require real external services",
    "evidence_retention_days": "integer - how long to keep evidence files",
    "detailed_logging": "boolean - whether to enable detailed evidence logging"
  },
  "safety_mechanisms": {
    "enable_loop_detection": "boolean - whether to detect infinite loops",
    "enable_resource_monitoring": "boolean - whether to monitor resource usage",
    "max_file_modifications_per_session": "integer - safety limit for file changes",
    "backup_before_modifications": "boolean - whether to backup files before changes"
  }
}
```

## Information Flow Patterns

### Hook Call Information Flow
```
1. Hook triggered → Load ProjectState from .claude/session_state.json
2. Load TaskGraph from .claude/task_graph.json  
3. Load CrossReferenceMap from .claude/cross_references.json
4. Load DependencyManifest from .claude/dependencies.json
5. Load SystemConfiguration from config/autonomous_config.json
6. Execute autonomous logic with all state information
7. Update state based on decisions and actions
8. Save updated state back to respective JSON files
9. Generate evidence record for this hook execution
10. Update CLAUDE.md with current progress/status
```

### State Persistence Strategy
- **Session State**: Persisted after every hook call
- **Task Graph**: Updated when tasks change status
- **Evidence**: Accumulated in separate files, never deleted during session
- **Cross-References**: Updated when files are created/modified
- **Dependencies**: Updated when validation status changes

## Cross-References
```
# RELATES_TO: behavior_decisions.md (BDR-006: no cross-session persistence),
#            architecture_decisions.md (ADR-008: structured evidence storage),
#            tentative_file_structure.md (data structure storage locations)
```

## Next Foundation Component
After information architecture, the next foundation component is **Persistence Layer Design** - how these data structures are loaded, saved, and synchronized between hook calls.