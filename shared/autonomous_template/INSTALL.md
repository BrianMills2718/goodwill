# Autonomous TDD Template Installation

## Quick Start

### Option 1: Automated Setup
```bash
# From the goodwill project directory
python3 tools/autonomous_template/setup.py /path/to/your/new/project --project-name "MyProject"
```

### Option 2: Manual Setup  
```bash
# Copy template to your project
cp -r tools/autonomous_template/.claude /path/to/your/project/
cp -r tools/autonomous_template/tools/workflow /path/to/your/project/tools/
cp -r tools/autonomous_template/docs /path/to/your/project/
cp tools/autonomous_template/CLAUDE.md /path/to/your/project/
```

## Configuration

### 1. Project Context (Required)
Edit `CLAUDE.md` in your project:
- Replace `[PROJECT NAME]` with your project name
- Update project overview and goals  
- Define current phase and tasks
- Set success criteria

### 2. Project Documentation (Recommended)
Customize these files for better autonomous guidance:
- `docs/behavior/desired_behavior.md` - Requirements and user stories
- `docs/architecture/system_overview.md` - Technical architecture
- `docs/development_roadmap/phases.md` - Development phases and tasks

### 3. Hook Customization (Optional)
Edit `.claude/hooks/autonomous_tdd.py` to:
- Add project-specific context detection
- Customize TDD phase instructions
- Adjust safety limits and behavior

## Usage

### Starting Autonomous Mode
1. Start Claude Code in your project directory:
   ```bash
   cd /path/to/your/project
   claude
   ```

2. Trigger the autonomous system:
   - Press `Escape` to activate the Stop hook
   - Follow the TDD instructions provided
   - Press `Escape` again to advance to next phase

### Safety Controls
- **Manual Override**: `touch .claude/workflow_override` to stop autonomous mode
- **Resume**: `rm .claude/workflow_override` to resume autonomous mode
- **Status**: Check `.claude/attempt_history.json` for learning history

### Monitoring Progress
The system maintains state in these files:
- `.claude/workflow_state.txt` - Current TDD phase
- `.claude/loop_counters.json` - Safety iteration tracking  
- `.claude/attempt_history.json` - Cross-session learning data

## System Behavior

### TDD Workflow Phases
1. **Explore**: Research and understand requirements
2. **Write Tests**: Create comprehensive test suite (TDD)
3. **Implement**: Build code to make tests pass
4. **Run Tests**: Execute and verify test results
5. **Doublecheck**: Verify implementation completeness
6. **Commit**: Commit changes with clear messages

### Safety Mechanisms
- **Loop Limit**: Stops after 7 complete TDD cycles
- **Stop Hook Limit**: Stops after 3 consecutive hooks without progress
- **Manual Override**: Immediate stop when override file exists
- **Health Monitoring**: Tracks automation effectiveness

### Cross-Session Learning
The system learns from:
- **Failed Strategies**: Avoids repeating unsuccessful approaches
- **Successful Patterns**: Applies proven techniques
- **Insights**: Accumulates strategic knowledge over time

## Troubleshooting

### System Not Responding
- Verify `.claude/settings.json` exists and is valid JSON
- Check that Claude Code hooks are enabled
- Ensure `.claude/hooks/autonomous_tdd.py` is executable

### Wrong Instructions
- Update `CLAUDE.md` with current task information
- Customize project context detection in autonomous hook
- Check documentation files for correct project information

### Safety Limits Hit
- Review `.claude/attempt_history.json` for failure patterns
- Consider breaking down complex tasks
- Use manual override to reset and try different approach

### No Progress Made
- Verify you're following the TDD instructions provided
- Create actual test files and implementations as guided
- Check that evidence files are being created properly

## Advanced Configuration

### Custom Context Detection
Edit the `generate_instruction()` method in `autonomous_tdd.py` to add project-specific context detection:

```python
# Check for your project patterns
if 'your_project_keyword' in claude_content:
    if step == "explore":
        instruction += " Focus on your specific requirements."
    # Add more customization...
```

### Integration with CI/CD
The autonomous system can be integrated with continuous integration:
- Monitor `.claude/attempt_history.json` for failure patterns
- Use safety limits to prevent runaway processes
- Extract insights for development process improvements

## Template Contents

```
autonomous_template/
├── README.md              # Main documentation
├── INSTALL.md             # This installation guide  
├── setup.py               # Automated setup script
├── .claude/
│   ├── hooks/
│   │   └── autonomous_tdd.py    # Main autonomous hook
│   └── settings.json            # Hook configuration
├── tools/workflow/
│   ├── evidence_validator.py    # Progress validation
│   └── state_reconciliation.py # Health monitoring
├── docs/                        # Documentation templates
│   ├── behavior/
│   ├── architecture/
│   └── development_roadmap/
└── CLAUDE.md             # Project context template
```

This template provides a complete autonomous TDD coaching system with safety mechanisms, cross-session learning, and project-agnostic design.