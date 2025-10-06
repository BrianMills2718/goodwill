# Autonomous TDD Template

## Overview

This template provides an autonomous Test-Driven Development (TDD) workflow system using Claude Code hooks. The system provides intelligent TDD coaching with cross-session memory, safety mechanisms, and historical learning.

## What It Does

**✅ Proven Capabilities:**
- Provides intelligent TDD workflow coaching (explore → write_tests → implement → run_tests → doublecheck → commit)
- Cross-session memory (learns from failures and successes across different Claude sessions)
- Safety mechanisms (prevents infinite loops with iteration and stop-hook limits)
- Historical learning (avoids repeated failed strategies, applies successful patterns)
- Project-agnostic design (reads project documentation to understand context)

**⚠️ Current Limitations:**
- Acts as a "TDD coach" providing instructions rather than directly implementing code
- Requires human to follow the TDD instructions and create actual files
- Gets stuck at `run_tests` phase without real test files to execute

## Installation

### 1. Copy Template Files
```bash
# Copy to your project root
cp -r tools/autonomous_template/.claude ./
cp -r tools/autonomous_template/tools/workflow ./tools/
```

### 2. Configure for Your Project
Edit the copied files to match your project:
- Update `CLAUDE.md` with your project goals
- Modify `docs/` structure to match your project
- Customize autonomous hook context detection

### 3. Enable Hooks
The `.claude/settings.json` file will automatically enable hooks when you start Claude Code in the project directory.

## Usage

### Starting Autonomous Mode
1. Start Claude Code in your project: `claude`
2. Press Escape to trigger the Stop hook
3. Follow the TDD instructions provided
4. Press Escape again to advance to the next TDD phase

### Safety Controls
- **Manual Override**: Create `.claude/workflow_override` file to stop autonomous mode
- **Iteration Limits**: System stops after 7 TDD cycles for manual review
- **Stop Hook Limits**: System stops after 3 consecutive hooks without progress
- **Cross-Session Memory**: Learns from failures to avoid repeated mistakes

### Working with the System
The autonomous system provides structured TDD guidance:

1. **Explore Phase**: Research requirements and understand the current task
2. **Write Tests Phase**: Create comprehensive tests following TDD principles
3. **Implement Phase**: Build code to make the tests pass
4. **Run Tests Phase**: Execute tests and verify they pass
5. **Doublecheck Phase**: Verify implementation meets all requirements
6. **Commit Phase**: Commit changes with clear messages

## Template Components

### Core Files
- `.claude/hooks/autonomous_tdd.py` - Main autonomous workflow hook
- `.claude/settings.json` - Claude Code hook configuration
- `tools/workflow/evidence_validator.py` - Progress validation system
- `tools/workflow/state_reconciliation.py` - Health monitoring

### State Management
- `.claude/workflow_state.txt` - Current TDD phase
- `.claude/loop_counters.json` - Safety iteration tracking
- `.claude/attempt_history.json` - Cross-session learning data

### Documentation Templates
- `docs/behavior/desired_behavior.md` - Project requirements template
- `docs/architecture/system_overview.md` - Technical architecture template  
- `docs/development_roadmap/phases.md` - Development phases template

## Customization

### Project-Specific Context
The autonomous hook reads your project documentation to provide contextual TDD guidance. Key files it looks for:

- `CLAUDE.md` - Main project context and current phase
- `docs/development_roadmap/phases.md` - Development phases and tasks
- `docs/behavior/desired_behavior.md` - Requirements and goals
- `docs/architecture/` - Technical architecture information

### Hook Customization
Edit `.claude/hooks/autonomous_tdd.py` to customize:
- TDD phase instructions for your domain
- Project-specific context detection logic
- Safety limits and iteration counts
- Historical learning patterns

## Validation Results

**Successfully Tested On:**
- ✅ Sandbox math utility implementation (simple functions)
- ✅ Complex eBay API integration project (external APIs, authentication)
- ✅ Cross-session failure learning and avoidance
- ✅ Safety mechanism activation and recovery
- ✅ Professional TDD workflow adherence

**Consistent Behavior:**
- Provides intelligent, context-aware TDD coaching
- Learns from failures and applies successful patterns
- Operates safely within defined iteration limits
- Adapts to different project types and complexity levels

## Best Practices

### Getting Started
1. **Start Simple**: Test the system with a simple task first
2. **Follow Instructions**: The system provides professional TDD guidance
3. **Monitor Progress**: Watch for safety limit activations
4. **Learn from History**: Review `.claude/attempt_history.json` for insights

### Troubleshooting
- **System Stuck**: Check if manual override file exists (`.claude/workflow_override`)
- **No Instructions**: Verify `CLAUDE.md` has current task information
- **Wrong Context**: Update project documentation for better context detection
- **Safety Limits Hit**: Review attempt history for failure patterns

## Architecture

The autonomous system uses hybrid intelligence:
- 🤖 **Programmatic**: Fast checks (file existence, counters, git status)
- 🧠 **LLM**: Human-like judgment (progress analysis, strategy decisions)  
- ⚡ **Hybrid**: Programmatic first, escalate to LLM when complex

This template represents an MVP autonomous TDD system. Future enhancements can add actual code generation, deeper failure analysis, and more sophisticated progress validation.

## License

This template is part of the Goodwill arbitrage project and is provided as-is for autonomous development experimentation.