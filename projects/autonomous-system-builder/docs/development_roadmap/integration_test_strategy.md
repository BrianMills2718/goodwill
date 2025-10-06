# Integration Test Strategy - Phase 6

## Overview

This document defines the integration testing strategy for validating cross-component behavior and end-to-end autonomous workflow functionality. Integration tests verify that our foundation components work together correctly and that external dependencies are properly handled.

## Integration Test Categories

### 1. Cross-Component Integration Tests

#### State Manager ↔ Configuration Manager Integration
- **Test**: State manager uses configuration for timeouts, limits, and validation thresholds
- **Validation**: Configuration changes affect state management behavior
- **Evidence**: State operations respect configured constraints

#### Context Manager ↔ Cross-Reference System Integration  
- **Test**: Context loading uses cross-reference discovery for file relationships
- **Validation**: Context expansion follows cross-reference chains correctly
- **Evidence**: Token limits respected while maximizing relevant context

#### Decision Engine ↔ All Foundation Components Integration
- **Test**: Decision engine uses state, context, and configuration for LLM decisions
- **Validation**: Decisions incorporate all available system information
- **Evidence**: Decision quality improves with better context and state

#### JSON Utilities ↔ All Persistence Operations
- **Test**: All components use JSONUtilities for safe file operations
- **Validation**: Atomic operations, backup creation, and validation work consistently
- **Evidence**: No data corruption during concurrent operations

### 2. External Dependency Integration Tests

#### File System Operations
- **Real File Testing**: No mocking - use actual file system operations
- **Permission Handling**: Test read-only directories, missing files, large files
- **Concurrent Access**: Multiple processes accessing same files
- **Recovery Testing**: Corrupted files, partial writes, disk space issues

#### Claude Code Task Tool Integration (Simulated)
- **Subprocess Simulation**: Test LLM query execution via subprocess calls
- **Timeout Handling**: Test behavior when LLM queries timeout or fail
- **Response Parsing**: Test structured response parsing and error handling
- **Context Size Management**: Test prompt generation within token limits

#### Python Import Discovery
- **Real Module Scanning**: Test Python AST parsing on actual code files
- **Error Handling**: Test behavior with syntax errors, missing modules
- **Performance**: Test scanning large codebases within time limits
- **Accuracy**: Verify import relationships are correctly identified

### 3. End-to-End Workflow Integration Tests

#### Complete Hook Execution Cycle
- **Test**: Full autonomous workflow from state loading to decision execution
- **Validation**: State persistence across hook calls
- **Evidence**: No data loss, consistent progression through methodology phases

#### Multi-Session Consistency
- **Test**: State recovery after system restart or crash
- **Validation**: Cross-session learning and decision history preservation
- **Evidence**: No regression in decision quality across sessions

#### Error Recovery Workflows
- **Test**: System recovery from various failure modes
- **Validation**: Backup restoration, graceful degradation, escalation triggers
- **Evidence**: System continues operation or fails safely with clear error reporting

## Test Implementation Strategy

### Integration Test Structure

```
tests/integration/
├── test_component_integration.py      # Cross-component behavior
├── test_external_dependencies.py      # File system, subprocess integration  
├── test_end_to_end_workflow.py       # Complete autonomous cycles
├── test_persistence_integration.py    # State + Config + JSON integration
├── test_context_integration.py       # Context + Cross-ref + Decision integration
├── fixtures/                         # Test data and mock project structures
│   ├── sample_project/               # Real project structure for testing
│   ├── corrupted_states/             # Invalid state files for recovery testing
│   └── large_codebase/               # Large project for performance testing
└── helpers/                          # Integration test utilities
    ├── project_setup.py              # Create test project structures
    ├── state_generators.py           # Generate test states and scenarios
    └── validation_helpers.py         # Verify integration test results
```

### Anti-Fabrication Principles for Integration Tests

#### No Mocking of Critical Paths
- **File System**: Use real files, directories, and permissions
- **State Persistence**: Use actual JSON files and atomic operations
- **Cross-References**: Scan real code files and documentation
- **Context Loading**: Test with actual large files and token limits

#### Evidence-Based Validation
- **Quantitative Metrics**: Response times, file sizes, token counts
- **State Verification**: Hash validation, consistency checks, backup integrity
- **Behavioral Proof**: Demonstrate actual autonomous decision-making
- **Performance Evidence**: Memory usage, execution time, scalability limits

#### Real-World Scenarios
- **Realistic Project Sizes**: Test with projects of 100+ files
- **Authentic Code Patterns**: Use real Python projects for cross-reference testing
- **Genuine Error Conditions**: Simulate actual failure modes, not contrived scenarios
- **Production Constraints**: Test within actual Claude Code hook time limits

## Integration Test Specifications

### Test 1: State-Configuration Integration

```python
def test_state_manager_respects_configuration_limits():
    """Test state manager operations respect configuration constraints"""
    
    # GIVEN: Configuration with specific limits
    config = {
        'safety_mechanisms': {
            'max_file_modifications_per_session': 5,
            'backup_before_modifications': True
        },
        'context_management': {
            'max_context_tokens': 10000
        }
    }
    
    # WHEN: State manager operates with this configuration
    state_manager = StateManager(project_root, config_manager=config)
    
    # THEN: Operations respect configured limits
    # - File modification counting works
    # - Backup creation follows configuration
    # - Token limits are enforced in context loading
    
    # EVIDENCE: Verify operations stop at configured limits
    # EVIDENCE: Verify backup files are created when configured
```

### Test 2: Context-CrossReference Integration

```python
def test_context_loading_follows_cross_references():
    """Test context manager uses cross-reference discovery for expansion"""
    
    # GIVEN: Real project with cross-references
    project_structure = create_test_project_with_cross_references()
    
    # WHEN: Context is loaded for a specific task
    cross_ref_manager = CrossReferenceManager(project_root)
    context_manager = ContextManager(cross_ref_manager)
    
    task = create_test_task_targeting_core_file()
    context = context_manager.load_task_context(task, token_limit=5000)
    
    # THEN: Context includes files discovered via cross-references
    # EVIDENCE: Verify cross-referenced files are included
    # EVIDENCE: Verify token limit is respected
    # EVIDENCE: Verify file prioritization works correctly
```

### Test 3: End-to-End Autonomous Cycle

```python
def test_complete_autonomous_hook_execution():
    """Test complete autonomous workflow from start to finish"""
    
    # GIVEN: Fresh project state and realistic task graph
    initial_state = create_realistic_project_state()
    save_state_to_filesystem(initial_state)
    
    # WHEN: Autonomous hook executes complete cycle
    workflow_manager = AutonomousWorkflowManager(project_root)
    hook_result = workflow_manager.execute_autonomous_hook_cycle()
    
    # THEN: State progresses correctly and evidence is collected
    final_state = load_state_from_filesystem()
    
    # EVIDENCE: State hash changed (progress made)
    # EVIDENCE: Task graph updated with new task statuses  
    # EVIDENCE: Evidence records created for completed tasks
    # EVIDENCE: Decision history shows rational progression
    # EVIDENCE: No corrupted state files or data loss
```

### Test 4: Multi-Component Decision Making

```python
def test_decision_engine_integrates_all_system_information():
    """Test decision engine incorporates state, context, and configuration"""
    
    # GIVEN: Complex system state with multiple considerations
    system_state = create_complex_system_state()
    context_bundle = create_large_context_bundle()
    configuration = create_realistic_configuration()
    
    # WHEN: Decision engine makes task selection decision
    decision_engine = LLMDecisionEngine(project_root, configuration)
    decision = decision_engine.make_task_selection_decision(
        available_tasks=system_state.task_graph.current_ready_tasks,
        project_state=system_state.project_state
    )
    
    # THEN: Decision reflects all available information
    # EVIDENCE: Decision reasoning mentions state factors
    # EVIDENCE: Decision considers configuration constraints
    # EVIDENCE: Decision incorporates context analysis
    # EVIDENCE: Decision quality metrics are reasonable
```

## Performance and Scalability Integration Tests

### Large Project Handling

```python
def test_system_performance_with_large_project():
    """Test system handles projects with 1000+ files"""
    
    # GIVEN: Large project structure (1000+ files)
    large_project = create_large_test_project(file_count=1000)
    
    # WHEN: System performs full cross-reference discovery
    start_time = time.time()
    cross_refs = cross_ref_manager.discover_all_cross_references()
    discovery_time = time.time() - start_time
    
    # THEN: Performance within acceptable limits
    # EVIDENCE: Discovery completes within 60 seconds
    # EVIDENCE: Memory usage stays under 500MB
    # EVIDENCE: All cross-references are accurately discovered
    # EVIDENCE: No file corruption or permission errors
```

### Concurrent Operations

```python
def test_concurrent_state_operations():
    """Test system handles concurrent hook executions safely"""
    
    # GIVEN: Multiple simulated hook processes
    processes = []
    
    # WHEN: Multiple processes attempt state operations simultaneously
    for i in range(5):
        p = Process(target=simulate_autonomous_hook_cycle, args=(project_root,))
        processes.append(p)
        p.start()
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    # THEN: State remains consistent
    final_state = load_state_from_filesystem()
    
    # EVIDENCE: State consistency validation passes
    # EVIDENCE: No corrupted state files
    # EVIDENCE: All processes completed successfully
    # EVIDENCE: State changes are properly serialized
```

## Integration Test Success Criteria

### Functional Requirements
- [ ] All cross-component interfaces work correctly
- [ ] External dependencies are properly handled
- [ ] End-to-end workflows complete successfully
- [ ] State persistence maintains consistency across sessions
- [ ] Error recovery mechanisms function as designed

### Performance Requirements  
- [ ] Cross-reference discovery: < 60 seconds for 1000+ files
- [ ] Context loading: < 10 seconds within token limits
- [ ] State operations: < 5 seconds for save/load cycles
- [ ] Decision making: < 30 seconds for LLM-powered decisions
- [ ] Memory usage: < 500MB for typical project sizes

### Quality Requirements
- [ ] No data corruption under any test scenario
- [ ] All error conditions produce clear, actionable error messages
- [ ] System degrades gracefully when limits are exceeded
- [ ] Evidence collection captures all necessary validation data
- [ ] Integration test coverage: 90%+ of cross-component interactions

### Anti-Fabrication Validation
- [ ] No test mocking of critical system components
- [ ] All file operations use real file system
- [ ] All state operations use actual persistence mechanisms
- [ ] All context operations respect genuine token limits
- [ ] All performance metrics measured on realistic workloads

This integration testing strategy ensures that our autonomous TDD system components work together effectively while maintaining our anti-fabrication principles and evidence-based validation approach.