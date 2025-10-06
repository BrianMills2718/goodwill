# Autonomous Test-Driven Development System

A comprehensive autonomous TDD system for Claude Code that prevents fabrication, enforces evidence-based development, and manages context intelligently within token limits.

## 🎯 Purpose

This system solves critical reliability issues in LLM-based coding systems:
- **Fabrication & Overoptimism**: Claims success when implementation is incomplete
- **Mock Data Masquerading**: Tests pass with fake data while real functionality fails  
- **Silent Failure Patterns**: Errors hidden instead of surfaced
- **Context Window Blindness**: Cannot maintain understanding of entire codebase

## 🏗️ Architecture

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code
- **FAIL-FAST AND LOUD**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require concrete proof
- **NO SUCCESS WITHOUT END-TO-END PROOF**: Complete pipeline must work

### System Components

```
src/
├── hook/                    # Claude Code hook integration
├── orchestrator/           # Workflow coordination  
├── analysis/               # LLM-driven decision making
├── context/                # Smart context loading
├── evidence/               # Evidence collection & validation
├── persistence/            # State management & backup
├── config/                 # Configuration management
└── utils/                  # Utility functions
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd autonomous_dog_food

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Configuration

1. **Main Configuration**: Edit `config/autonomous_tdd.json`
2. **Environment Variables**: Set `AUTONOMOUS_TDD_*` variables for overrides
3. **User Configuration**: Create `config/user_config.json` for personal settings

### Basic Usage

```python
from src.dependency_injection import DIContainer, configure_autonomous_services

# Initialize dependency injection
container = DIContainer()
configure_autonomous_services(container)

# Initialize all services
result = container.initialize_all_services()
if result.success:
    print("Autonomous TDD system ready!")
else:
    print(f"Initialization failed: {result.error}")
```

## 📋 Development Methodology

### 8-Phase Iterative Process

1. **Overview** - Project definition and scope
2. **Behavior + Acceptance Tests** - User behavior validation
3. **Architecture + Contract Integration Tests** - System design
4. **External Dependency Research + External Integration Tests** - External service integration
5. **Implementation Plans + Unit Tests + Implementation Integration Tests** - TDD foundation
6. **Create Files & Cross-References** - File structure and relationships
7. **Implementation** - Actual code development
8. **Validation & Documentation** - End-to-end validation

### Iteration Management

- **Micro-iterations**: Within phases (max 5)
- **Macro-iterations**: Across phases (max 3) 
- **LLM-driven stabilization**: Confidence > 0.8 required to proceed
- **Problem tracking**: Systematic gap identification and resolution

## 🔧 Key Features

### Evidence-Based Validation
- Anti-fabrication detection
- Timestamp validation
- External service verification
- Evidence chain tracking

### Smart Context Management
- Token-aware context loading
- Cross-reference discovery
- Intelligent file prioritization
- Context optimization strategies

### Autonomous Decision Making
- LLM-driven task decomposition
- Situation analysis and decision trees
- Error resolution strategies
- Phase progression logic

### State Management
- Atomic operations with backup/recovery
- Consistency validation
- Corruption detection and repair
- Cross-session persistence

## 🛡️ Safety Mechanisms

### Anti-Fabrication Rules
- No mock data in success claims
- Real external service validation
- Timestamp authenticity checking
- Evidence chain integrity

### Resource Protection
- Memory limit enforcement (500MB default)
- Execution timeouts (5 minutes default)
- Concurrent task limits (3 parallel max)
- Emergency stop thresholds

### Iteration Limits
- Max 5 micro-iterations per phase
- Max 3 macro-iterations total
- Emergency intervention at 15 problems
- Manual override capabilities

## 📊 Configuration

### Core Settings

```json
{
  "system": {
    "project_root": ".",
    "log_level": "INFO",
    "max_memory_mb": 2048,
    "timeout_seconds": 300
  },
  "llm": {
    "max_context_tokens": 150000,
    "max_response_tokens": 4000,
    "temperature": 0.1,
    "max_retries": 3
  },
  "safety": {
    "max_micro_iterations": 5,
    "max_macro_iterations": 3,
    "emergency_stop_threshold": 15,
    "backup_enabled": true
  }
}
```

### Environment Variables

```bash
# System configuration
export AUTONOMOUS_TDD_PROJECT_ROOT="/path/to/project"
export AUTONOMOUS_TDD_LOG_LEVEL="DEBUG"
export AUTONOMOUS_TDD_MAX_MEMORY_MB="4096"

# LLM configuration  
export AUTONOMOUS_TDD_MAX_CONTEXT_TOKENS="180000"
export AUTONOMOUS_TDD_TEMPERATURE="0.1"

# Safety configuration
export AUTONOMOUS_TDD_MAX_MICRO_ITERATIONS="3"
export AUTONOMOUS_TDD_EMERGENCY_STOP_THRESHOLD="10"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests  
pytest tests/acceptance/    # Acceptance tests
```

### Test Structure

- **Unit Tests**: Component-level testing with 95%+ coverage
- **Integration Tests**: Cross-component interaction validation
- **Acceptance Tests**: End-to-end user scenario validation
- **Locked Tests**: Immutable tests that prevent cheating

## 📈 Monitoring

### Logging

Structured JSON logging with autonomous system context:

```python
from src.utils.logging_setup import get_logger, log_autonomous_event

logger = get_logger(__name__)
log_autonomous_event(
    logger=logger,
    event_type="task_start",
    message="Starting task decomposition",
    task_id="task_123",
    phase="phase_5",
    iteration_count=2
)
```

### Performance Tracking

- Memory usage monitoring
- Execution time tracking  
- LLM call performance
- Context loading efficiency
- Decision quality metrics

## 🔍 Troubleshooting

### Common Issues

1. **Configuration Errors**: Check config file syntax and environment variables
2. **Memory Limits**: Reduce context size or increase memory allocation
3. **Timeout Issues**: Increase timeout settings or optimize operations
4. **Dependency Errors**: Verify all dependencies are installed and accessible

### Debug Mode

Enable debug mode for verbose logging:

```bash
export AUTONOMOUS_TDD_DEBUG_MODE="true"
export AUTONOMOUS_TDD_LOG_LEVEL="DEBUG"
```

### State Recovery

If system state becomes corrupted:

```bash
# Backup current state
cp -r .autonomous_state .autonomous_state.backup

# Reset to clean state
rm -rf .autonomous_state
# System will reinitialize on next run
```

## 📚 Documentation

- **Architecture**: `docs/architecture/` - Detailed system design
- **API Reference**: `docs/api/` - Component interfaces and usage
- **Development Guide**: `docs/development/` - Contributing guidelines
- **Examples**: `examples/` - Usage examples and tutorials

## 🤝 Contributing

1. **Follow TDD**: Write tests before implementation
2. **Use Type Hints**: Full type annotation required
3. **Document Changes**: Update relevant documentation
4. **Test Coverage**: Maintain 95%+ coverage
5. **Evidence-Based**: Provide concrete proof of functionality

## 📄 License

MIT License - see `LICENSE` file for details.

## 🙏 Acknowledgments

Built using the autonomous TDD methodology with iterative stabilization and evidence-based validation to ensure reliable, fabrication-free development.