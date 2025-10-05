# Tentative File Structure - Autonomous TDD System

## Purpose
This document defines the complete file structure that will be created for the Autonomous TDD System, following our established directory patterns from `ADR-007`. This structure will inform the pseudocode and ensure realistic file path references.

## Complete Directory Structure

```
autonomous_tdd_system/
├── CLAUDE.md                           # Current implementation plan (auto-updated)
├── project_architecture.md             # Architecture decisions for this project
├── README.md                          # Project overview and usage instructions
├── 
├── src/                               # Main autonomous TDD system code
│   ├── hook/                          # Claude Code hook integration
│   │   ├── __init__.py
│   │   ├── autonomous_hook.py         # Main Stop hook implementation
│   │   ├── hook_config.py             # Hook configuration management
│   │   └── hook_utils.py              # Utility functions for hook operations
│   ├── orchestrator/                  # Autonomous workflow orchestration
│   │   ├── __init__.py
│   │   ├── workflow_manager.py        # Main workflow coordination
│   │   ├── task_decomposer.py         # LLM-driven task breakdown
│   │   ├── dependency_graph.py        # Task dependency management
│   │   └── phase_manager.py           # Phase progression logic
│   ├── analysis/                      # LLM analysis and decision making
│   │   ├── __init__.py
│   │   ├── llm_analyzer.py            # Core LLM analysis functions
│   │   ├── error_analyzer.py          # Error analysis and correction
│   │   ├── progress_analyzer.py       # Progress assessment and validation
│   │   └── completion_validator.py    # Evidence-based completion detection
│   ├── context/                       # Context management and loading
│   │   ├── __init__.py
│   │   ├── context_loader.py          # Smart context loading
│   │   ├── cross_reference_manager.py # Cross-reference system
│   │   ├── file_scanner.py            # File relationship discovery
│   │   └── dependency_tracker.py      # External dependency tracking
│   ├── evidence/                      # Evidence collection and validation
│   │   ├── __init__.py
│   │   ├── evidence_collector.py      # Test result and evidence gathering
│   │   ├── anti_fabrication.py        # Mock detection and validation
│   │   ├── test_runner.py             # Test framework integration
│   │   └── real_dependency_validator.py # External service validation
│   ├── config/                        # Configuration management
│   │   ├── __init__.py
│   │   ├── config_manager.py          # Configuration loading and validation
│   │   ├── environment_detector.py    # Project type and environment detection
│   │   └── defaults.py                # Default configuration values
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── file_utils.py              # File system operations
│       ├── logging_utils.py           # Structured logging utilities
│       ├── json_utils.py              # JSON handling and validation
│       └── claude_code_utils.py       # Claude Code API interactions
├── 
├── docs/                              # Permanent documentation
│   ├── behavior/                      # WHAT the system should do
│   │   ├── autonomous_requirements.md # System behavior requirements
│   │   ├── user_workflows.md          # How users interact with system
│   │   ├── error_handling_behavior.md # Expected error handling behavior
│   │   └── success_criteria.md        # What constitutes successful operation
│   ├── architecture/                  # HOW to build the system
│   │   ├── system_overview.md         # High-level system architecture
│   │   ├── hook_integration.md        # Claude Code hook integration design
│   │   ├── llm_decision_trees.md      # LLM decision-making patterns
│   │   ├── context_management.md      # Context loading and cross-reference design
│   │   └── evidence_validation.md     # Evidence collection and validation design
│   ├── dependencies/                  # External service integration
│   │   ├── claude_code_api.md         # Claude Code integration requirements
│   │   ├── test_frameworks.md         # Test framework integration (pytest, jest, etc.)
│   │   ├── file_system_operations.md # File system access patterns
│   │   └── external_tools.md          # WebSearch, Context7 MCP integration
│   └── development_roadmap/           # Current status and phases
│       ├── phases.md                  # High-level phase overview
│       ├── phase_1_hook_system.md     # Hook system implementation
│       ├── phase_2_orchestration.md   # Workflow orchestration
│       └── phase_3_evidence.md        # Evidence validation system
├── 
├── tests/                             # All test files
│   ├── acceptance/                    # User behavior validation tests
│   │   ├── test_autonomous_workflow.py   # End-to-end autonomous operation
│   │   ├── test_error_recovery.py        # Error handling and recovery
│   │   ├── test_evidence_validation.py   # Evidence-based completion
│   │   └── test_user_blocking.py         # Clear blocking and escalation
│   ├── integration/                   # System integration tests
│   │   ├── test_claude_code_integration.py # Hook integration with Claude Code
│   │   ├── test_file_operations.py       # File system operations
│   │   ├── test_external_tools.py        # WebSearch, Context7 integration
│   │   └── test_test_framework_integration.py # pytest, jest integration
│   └── unit/                          # Component tests
│       ├── test_hook/                 # Hook system unit tests
│       │   ├── test_autonomous_hook.py
│       │   ├── test_hook_config.py
│       │   └── test_hook_utils.py
│       ├── test_orchestrator/         # Orchestration unit tests
│       │   ├── test_workflow_manager.py
│       │   ├── test_task_decomposer.py
│       │   ├── test_dependency_graph.py
│       │   └── test_phase_manager.py
│       ├── test_analysis/             # Analysis unit tests
│       │   ├── test_llm_analyzer.py
│       │   ├── test_error_analyzer.py
│       │   ├── test_progress_analyzer.py
│       │   └── test_completion_validator.py
│       ├── test_context/              # Context management unit tests
│       │   ├── test_context_loader.py
│       │   ├── test_cross_reference_manager.py
│       │   ├── test_file_scanner.py
│       │   └── test_dependency_tracker.py
│       ├── test_evidence/             # Evidence system unit tests
│       │   ├── test_evidence_collector.py
│       │   ├── test_anti_fabrication.py
│       │   ├── test_test_runner.py
│       │   └── test_real_dependency_validator.py
│       ├── test_config/               # Configuration unit tests
│       │   ├── test_config_manager.py
│       │   ├── test_environment_detector.py
│       │   └── test_defaults.py
│       └── test_utils/                # Utility unit tests
│           ├── test_file_utils.py
│           ├── test_logging_utils.py
│           ├── test_json_utils.py
│           └── test_claude_code_utils.py
├── 
├── config/                            # Configuration files
│   ├── autonomous_config.json         # Main system configuration
│   ├── hook_config.json              # Hook-specific configuration  
│   ├── logging_config.json           # Logging configuration
│   ├── test_config.json              # Test framework configuration
│   └── environments/                 # Environment-specific configs
│       ├── development.json
│       ├── testing.json
│       └── production.json
├── 
├── logs/                              # Structured logging system
│   ├── evidence/                      # Task completion evidence
│   │   ├── session_progress.json
│   │   ├── task_evidence/
│   │   └── validation_results/
│   ├── errors/                        # Error tracking
│   │   ├── active/
│   │   └── resolved/
│   ├── debug/                         # Component-specific debug logs
│   │   ├── hook_execution/
│   │   ├── llm_decisions/
│   │   ├── context_loading/
│   │   └── file_operations/
│   └── autonomous_sessions/           # Full session logs
│       └── session_[timestamp]/
├── 
├── tools/                             # Utility scripts
│   ├── validate_references.py        # Cross-reference validation
│   ├── load_context.py               # Context loading for modifications
│   ├── inject_error.py               # Error injection to CLAUDE.md
│   ├── setup_autonomous.py           # Initial setup script
│   └── workflow/                     # Autonomous workflow tools
│       ├── workflow_orchestrator.py
│       ├── evidence_validator.py
│       ├── dependency_analyzer.py
│       └── session_manager.py
├── 
├── .claude/                           # Claude Code configuration
│   ├── hooks/                         # Hook files
│   │   └── autonomous_stop.py         # Main autonomous Stop hook
│   ├── cross_references.json         # File relationship metadata
│   ├── dependencies.json             # External dependency manifest
│   ├── session_state.json            # Current autonomous session state
│   ├── task_graph.json               # Current task dependency graph
│   └── commands/                     # Custom slash commands
│       ├── /autonomous-start
│       ├── /autonomous-status
│       └── /autonomous-debug
├── 
├── examples/                          # Example projects and templates
│   ├── web_api_example/              # Example web API project structure
│   ├── data_processing_example/      # Example data processing project
│   └── cli_tool_example/             # Example CLI tool project
├── 
└── .gitignore                        # Git ignore patterns
```

## Key File Purposes

### Core System Files
- **`src/hook/autonomous_hook.py`**: Main Stop hook implementation that orchestrates the autonomous workflow
- **`src/orchestrator/workflow_manager.py`**: Central coordinator for autonomous session management
- **`src/analysis/llm_analyzer.py`**: Core LLM decision-making and analysis functions
- **`src/context/context_loader.py`**: Smart context loading based on cross-references and current task

### Configuration & State
- **`config/autonomous_config.json`**: Main system configuration (retry limits, blocking conditions, etc.)
- **`.claude/session_state.json`**: Current autonomous session state and progress
- **`.claude/task_graph.json`**: Current task dependency graph and completion status
- **`.claude/cross_references.json`**: File relationship metadata for context loading

### Evidence & Validation
- **`src/evidence/evidence_collector.py`**: Collects test results and validates evidence quality
- **`src/evidence/anti_fabrication.py`**: Detects mock usage and validates real dependencies
- **`logs/evidence/`**: Structured evidence files for task completion validation

### Integration Points
- **`.claude/hooks/autonomous_stop.py`**: Claude Code Stop hook entry point
- **`src/evidence/test_runner.py`**: Integration with pytest, jest, and other test frameworks
- **`docs/dependencies/`**: External service integration documentation

## Cross-Reference Patterns

All files will include `# RELATES_TO:` comments linking to:
- Related documentation files
- Dependent implementation files  
- Associated test files
- Configuration files

Example:
```python
# src/hook/autonomous_hook.py
# RELATES_TO: docs/architecture/hook_integration.md, config/hook_config.json, 
#            tests/integration/test_claude_code_integration.py, .claude/hooks/autonomous_stop.py
```

This structure provides the foundation for writing detailed pseudocode that references actual file paths and realistic system organization.