#!/bin/bash
# Setup script for autonomous Claude Code projects
# Usage: bash setup_autonomous_project.sh [project_name]

set -e

# Get project name from argument or current directory
PROJECT_NAME=${1:-$(basename $(pwd))}
WORKFLOW_TOOLS_SOURCE=~/claude-workflow-tools/workflow

echo "🚀 Setting up autonomous project: $PROJECT_NAME"

# Check if workflow tools exist in home directory
if [ ! -d ~/claude-workflow-tools ]; then
    echo "📦 Installing workflow tools to ~/claude-workflow-tools..."
    mkdir -p ~/claude-workflow-tools/workflow
    
    # Find the source of workflow tools
    if [ -d "/home/brian/projects/goodwill/tools/workflow" ]; then
        cp -r /home/brian/projects/goodwill/tools/workflow/* ~/claude-workflow-tools/workflow/
    else
        echo "❌ Error: Could not find workflow tools source"
        echo "Please ensure workflow tools are available at /home/brian/projects/goodwill/tools/workflow"
        exit 1
    fi
    chmod +x ~/claude-workflow-tools/workflow/*.py
fi

# 1. Create required directory structure
echo "📁 Creating directory structure..."
mkdir -p .claude
mkdir -p docs/behavior
mkdir -p docs/architecture  
mkdir -p docs/development_roadmap
mkdir -p investigations/current_work
mkdir -p research
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p src
mkdir -p tools/workflow
mkdir -p logs/errors/active
mkdir -p config

# 2. Copy workflow tools
echo "🔧 Installing workflow tools..."
cp -r $WORKFLOW_TOOLS_SOURCE/* tools/workflow/
chmod +x tools/workflow/*.py

# 3. Create validation tool for cross-references
echo "🔗 Installing cross-reference validator..."
cat > tools/validate_references.py << 'EOF'
#!/usr/bin/env python3
"""Validate cross-references in the codebase."""
import re
import os
from pathlib import Path

def validate_references():
    """Basic reference validation for autonomous projects."""
    errors = []
    project_root = Path.cwd()
    
    # Check Python files for TRACEABILITY sections
    for py_file in project_root.glob("**/*.py"):
        if ".git" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        with open(py_file, 'r') as f:
            content = f.read()
            
        # Check for documentation references
        refs = re.findall(r'"""[\s\S]*?"""', content)
        if refs and "TODO" in content:
            errors.append(f"TODO found in {py_file}")
    
    return errors

if __name__ == "__main__":
    errors = validate_references()
    if errors:
        print(f"Found {len(errors)} issues")
        for error in errors[:10]:
            print(f"  - {error}")
    else:
        print("✅ No reference issues found")
EOF
chmod +x tools/validate_references.py

# 4. Create initial CLAUDE.md
echo "📝 Creating CLAUDE.md..."
cat > CLAUDE.md << EOF
# Project: $PROJECT_NAME

## 🚨 ACTIVE ERRORS AND BLOCKERS
(None currently)

## Project Overview
[Describe project purpose here]

## Common Commands
*To be populated as project develops*

## Code Style & Patterns
- Use type hints for all functions
- Follow TDD approach (tests first)
- Document all public APIs
- Handle errors gracefully

## Testing Approach
- Unit tests for all components
- Integration tests for workflows
- Mock external dependencies
- Maintain >80% coverage

## Workflow State
\`\`\`json
{
  "workflow_state": {
    "current_command": "/explore",
    "current_phase": "discovery",
    "iteration": 0,
    "confidence": "low"
  }
}
\`\`\`
EOF

# 5. Create phases.md
echo "📋 Creating development phases..."
cat > docs/development_roadmap/phases.md << 'EOF'
# Development Phases

## Phase 1: Discovery & Planning
- [ ] Understand requirements
- [ ] Research technical approach  
- [ ] Identify uncertainties
- [ ] Create architecture plan
- [ ] Define success criteria

## Phase 2: Foundation
- [ ] Set up project structure
- [ ] Create core interfaces
- [ ] Write initial test suite
- [ ] Implement basic functionality

## Phase 3: Core Implementation
- [ ] Build main components
- [ ] Implement business logic
- [ ] Add error handling
- [ ] Create integration points

## Phase 4: Testing & Validation
- [ ] Complete test coverage
- [ ] Integration testing
- [ ] Performance testing
- [ ] Edge case handling

## Phase 5: Polish & Documentation
- [ ] Complete documentation
- [ ] Code cleanup
- [ ] Performance optimization
- [ ] Deployment preparation
EOF

# 6. Create behavior template
echo "📖 Creating requirements template..."
cat > docs/behavior/requirements.md << EOF
# $PROJECT_NAME Requirements

## Core Requirements
1. [Define what the system must do]
2. [Key functionality needed]
3. [Success criteria]

## User Stories
- As a [user type], I want to [action] so that [benefit]
- As a [user type], I want to [action] so that [benefit]

## Constraints
- **Technical**: [Language, framework, platform constraints]
- **Performance**: [Speed, memory, scalability requirements]
- **Security**: [Authentication, authorization, data protection]
- **Timeline**: [Deadlines and milestones]

## Uncertainties to Resolve
- [ ] [Unknown requirement or technical question]
- [ ] [Integration uncertainty]
- [ ] [Performance characteristic to determine]

## Success Metrics
- [How we measure success]
- [Key performance indicators]
- [Quality benchmarks]
EOF

# 7. Create architecture template
echo "🏗️ Creating architecture template..."
cat > docs/architecture/technical_design.md << EOF
# $PROJECT_NAME Technical Architecture

## System Overview
[High-level architecture description]

## Technology Stack
- **Language**: [e.g., Python 3.11]
- **Framework**: [e.g., FastAPI, Django, Flask]
- **Database**: [e.g., PostgreSQL, SQLite, MongoDB]
- **Testing**: [e.g., pytest, unittest]
- **CI/CD**: [e.g., GitHub Actions, Jenkins]

## Component Architecture

### Component A: [Name]
- **Purpose**: [What it does]
- **Interfaces**: [APIs, protocols]
- **Dependencies**: [What it needs]

### Component B: [Name]
- **Purpose**: [What it does]
- **Interfaces**: [APIs, protocols]
- **Dependencies**: [What it needs]

## Data Flow
1. [Step 1 of data flow]
2. [Step 2 of data flow]
3. [Step 3 of data flow]

## Integration Points
- **External APIs**: [List of external services]
- **Internal APIs**: [Service boundaries]
- **Data Sources**: [Databases, files, streams]

## Security Considerations
- [Authentication approach]
- [Authorization model]
- [Data encryption]

## Scalability Plan
- [Horizontal scaling approach]
- [Caching strategy]
- [Performance targets]
EOF

# 8. Create initial test structure
echo "🧪 Creating test structure..."
cat > tests/__init__.py << 'EOF'
"""Test suite for the project."""
EOF

cat > tests/test_placeholder.py << 'EOF'
"""Placeholder test file to establish structure."""
import pytest

def test_placeholder():
    """Placeholder test - replace with real tests."""
    assert True, "Replace this with actual tests"

# TODO: Add actual test cases as implementation progresses
EOF

# 9. Create .gitignore
echo "🚫 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Workflow state files
.claude/workflow_state.json
.claude/next_command.txt
.claude/*.log
.claude/discovery_classifications.json
.claude/recovery_context.json
.claude/uncertainty_resolutions.json
.claude/workflow_history.json

# Archives (stored externally)  
archive/
/home/brian/projects/archive/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.pytest_cache/
htmlcov/
.coverage

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
*.key
*.pem
secrets/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Project specific
output/
data/processed/
temp/
EOF

# 10. Create evidence template
echo "📊 Creating evidence template..."
mkdir -p investigations/current_work
cat > investigations/current_work/evidence_template.json << 'EOF'
{
  "phase": "discovery",
  "timestamp": "ISO 8601 timestamp",
  "status": "in_progress",
  "areas_investigated": [],
  "key_findings": [],
  "test_files_created": [],
  "test_count": 0,
  "files_modified": [],
  "implementation_complete": false,
  "test_results": null,
  "tests_passed": false,
  "validation_complete": false,
  "edge_cases_tested": false
}
EOF

# 11. Initialize git if needed
if [ ! -d .git ]; then
    echo "🎯 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial autonomous project setup for $PROJECT_NAME"
fi

# 12. Create quick start guide
cat > QUICKSTART.md << EOF
# Quick Start Guide for $PROJECT_NAME

## Autonomous Workflow Commands

1. **Start exploration**: \`/explore\`
   - Claude will analyze requirements and codebase

2. **Check workflow state**: 
   \`\`\`bash
   python3 tools/workflow/workflow_orchestrator.py
   \`\`\`

3. **Validate evidence**:
   \`\`\`bash
   python3 tools/workflow/evidence_validator.py
   \`\`\`

4. **Check for uncertainties**:
   \`\`\`bash
   python3 tools/workflow/uncertainty_resolver.py
   \`\`\`

## Workflow Progression

The system will automatically suggest next steps after each command.
Follow the suggested commands or override with your own.

## First Steps

1. Edit \`docs/behavior/requirements.md\` with actual requirements
2. Update \`CLAUDE.md\` with project description
3. Run \`/explore\` to begin autonomous workflow

## Monitoring Progress

- Check \`.claude/next_command.txt\` for recommendations
- Review \`.claude/workflow_state.json\` for current state
- Look at \`investigations/\` for research findings
EOF

echo ""
echo "✅ Autonomous project setup complete!"
echo ""
echo "📚 Created files:"
echo "  - CLAUDE.md (project context)"
echo "  - QUICKSTART.md (usage guide)"
echo "  - docs/behavior/requirements.md (requirements template)"
echo "  - docs/architecture/technical_design.md (architecture template)"
echo "  - docs/development_roadmap/phases.md (development phases)"
echo "  - tools/workflow/* (automation tools)"
echo ""
echo "🚀 Next steps:"
echo "  1. Edit docs/behavior/requirements.md with your actual requirements"
echo "  2. Update CLAUDE.md with your project description"
echo "  3. Configure hooks if not already done: claude /hooks"
echo "  4. Start Claude Code and run: /explore"
echo ""
echo "The autonomous workflow will guide you through the rest!"