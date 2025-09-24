# Autonomous Claude Code Project Setup Guide

## Overview
This guide enables fully autonomous coding projects using Claude Code with automated workflow orchestration.

## Prerequisites for New Projects

### 1. System Prerequisites
- Claude Code installed and configured
- Python 3.8+ installed
- Git initialized in project directory
- User hooks configured in `~/.claude/settings.json`

### 2. Required Tools Installation

#### Step 1: Install Workflow Tools Package
```bash
# Clone the workflow tools to a shared location
mkdir -p ~/claude-workflow-tools
cp -r /home/brian/projects/goodwill/tools/workflow ~/claude-workflow-tools/

# Make tools executable
chmod +x ~/claude-workflow-tools/workflow/*.py
```

#### Step 2: Configure User-Level Hooks
Add to `~/.claude/settings.json`:
```json
{
  "model": "opus",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/tools/workflow/workflow_orchestrator.py --quiet >> $CLAUDE_PROJECT_DIR/.claude/workflow.log 2>&1"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/tools/workflow/session_recovery.py --json > $CLAUDE_PROJECT_DIR/.claude/session_context.json"
          }
        ]
      }
    ]
  }
}
```

## New Project Setup Script

### Quick Setup (run in new project directory):
```bash
#!/bin/bash
# setup_autonomous_project.sh

PROJECT_NAME=$(basename $(pwd))
WORKFLOW_TOOLS_SOURCE=~/claude-workflow-tools/workflow

# 1. Create required directory structure
mkdir -p .claude
mkdir -p docs/behavior
mkdir -p docs/architecture  
mkdir -p docs/development_roadmap
mkdir -p investigations
mkdir -p research
mkdir -p tests
mkdir -p src
mkdir -p tools/workflow
mkdir -p logs/errors/active

# 2. Copy workflow tools
cp -r $WORKFLOW_TOOLS_SOURCE/* tools/workflow/
chmod +x tools/workflow/*.py

# 3. Create initial CLAUDE.md
cat > CLAUDE.md << 'EOF'
# Project: PROJECT_NAME_PLACEHOLDER

## 🚨 ACTIVE ERRORS AND BLOCKERS
(None currently)

## Project Overview
[Describe project purpose here]

## Common Commands
*To be populated as project develops*

## Workflow State
```json
{
  "workflow_state": {
    "current_command": "/explore",
    "current_phase": "discovery",
    "iteration": 0,
    "confidence": "low"
  }
}
```
EOF

# 4. Replace project name
sed -i "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/g" CLAUDE.md

# 5. Create phases.md
cat > docs/development_roadmap/phases.md << 'EOF'
# Development Phases

## Phase 1: Discovery & Planning
- [ ] Understand requirements
- [ ] Research technical approach
- [ ] Identify uncertainties
- [ ] Create architecture plan

## Phase 2: Core Implementation
- [ ] Build foundational components
- [ ] Create test suite
- [ ] Implement main functionality

## Phase 3: Integration & Testing
- [ ] Integration testing
- [ ] Error handling
- [ ] Performance optimization

## Phase 4: Documentation & Deployment
- [ ] Complete documentation
- [ ] Deployment setup
- [ ] Final validation
EOF

# 6. Create behavior template
cat > docs/behavior/requirements.md << 'EOF'
# Project Requirements

## Core Requirements
1. [Define what the system must do]
2. [Key functionality needed]
3. [Success criteria]

## Constraints
- [Technical constraints]
- [Resource constraints]
- [Timeline constraints]

## Uncertainties
- [Unknown requirements]
- [Technical uncertainties]
- [Integration uncertainties]
EOF

# 7. Create architecture template
cat > docs/architecture/technical_design.md << 'EOF'
# Technical Architecture

## System Overview
[High-level architecture description]

## Components
1. **Component A**: [Purpose and design]
2. **Component B**: [Purpose and design]

## Technology Stack
- Language: [e.g., Python, JavaScript]
- Framework: [e.g., FastAPI, React]
- Database: [e.g., PostgreSQL, MongoDB]
- Testing: [e.g., pytest, jest]

## Integration Points
[External systems and APIs]
EOF

# 8. Create .gitignore
cat > .gitignore << 'EOF'
# Workflow state files
.claude/workflow_state.json
.claude/next_command.txt
.claude/*.log

# Archives (stored externally)
archive/

# Python
__pycache__/
*.pyc
.pytest_cache/

# IDE
.vscode/
.idea/

# Environment
.env
.env.local

# Logs
logs/
*.log
EOF

# 9. Initialize git if needed
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial autonomous project setup"
fi

echo "✅ Autonomous project setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit CLAUDE.md with your project description"
echo "2. Update docs/behavior/requirements.md with actual requirements"
echo "3. Start Claude Code in this directory"
echo "4. Use /explore to begin autonomous workflow"
```

## How the Autonomous System Works

### 1. Workflow Commands
The system recognizes these slash commands:
- `/explore` - Discover and understand the problem space
- `/write_tests` - Create test suite based on requirements
- `/implement` - Build the solution
- `/run_tests` - Execute and validate tests
- `/doublecheck` - Verify implementation completeness
- `/commit` - Commit completed work
- `/investigate_uncertainties` - Research unknowns
- `/resolve_blockers` - Fix blocking issues

### 2. Automatic Progression
After each Claude response, the Stop hook triggers:
1. Reads current workflow state from CLAUDE.md
2. Analyzes progress and evidence
3. Determines next logical command
4. Saves recommendation to `.claude/next_command.txt`

### 3. Evidence-Based Transitions
The system requires evidence for phase transitions:
- Test results for implementation validation
- Documentation for completion
- Error resolution for blockers

### 4. Intelligence-Based Analysis
- Uses LLM understanding, not keyword matching
- Comprehends context and relationships
- Makes nuanced decisions about workflow

## Starting an Autonomous Session

### Initial Commands Sequence:
```
1. /explore
   Claude explores the codebase and requirements
   
2. (Automatic) Stop hook suggests next command
   
3. Execute suggested command or provide guidance
   
4. Repeat until project complete
```

### Manual Override:
You can always override the suggested command by using a different slash command or providing specific instructions.

## Project-Specific Customization

### 1. Custom Evidence Requirements
Edit `tools/workflow/evidence_validator.py` to add project-specific evidence schemas.

### 2. Custom Discovery Patterns
Modify `tools/workflow/discovery_classifier_intelligent.py` for project-specific discovery classification.

### 3. Custom Workflow Progression
Adjust `tools/workflow/workflow_orchestrator.py` command progression for your workflow.

## Troubleshooting

### Hooks Not Triggering
1. Run `/hooks` to verify configuration
2. Restart Claude Code session
3. Check `claude --debug` for hook execution details

### Workflow Stuck in Loop
1. Run `python3 tools/workflow/uncertainty_resolver.py`
2. Check `.claude/workflow_history.json` for patterns
3. Reset state: `rm .claude/workflow_state.json`

### Missing Evidence
1. Run `python3 tools/workflow/evidence_validator.py`
2. Create evidence file with required fields
3. Check `investigations/current_work/evidence.json`

## Benefits of This System

1. **Consistent Workflow** - Same process across all projects
2. **Evidence-Based** - Decisions based on actual progress
3. **Self-Documenting** - Automatic tracking of decisions
4. **Intelligent** - Uses LLM comprehension, not rules
5. **Recoverable** - Can resume from any state

## Example Projects Using This System

### Web Application
- Requirements in `docs/behavior/`
- API design in `docs/architecture/`
- Tests drive implementation
- Automatic progression through phases

### Data Pipeline
- Data sources documented
- Processing stages defined
- Tests validate transformations
- Evidence tracks data quality

### CLI Tool
- Command structure planned
- Tests define behavior
- Implementation follows TDD
- Documentation auto-generated

This system transforms Claude Code into an autonomous coding assistant that systematically works through projects with minimal human intervention.