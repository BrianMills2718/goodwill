#!/bin/bash
# One-time installation of Claude Code workflow tools
# Run this once to install the tools system-wide for all projects

set -e

echo "🔧 Claude Code Autonomous Workflow Tools Installer"
echo "================================================="

# Check for required dependencies
echo "📋 Checking dependencies..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required but not found. Aborting." >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git required but not found. Aborting." >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "⚠️  Warning: jq not found. Some hooks may not work properly." >&2; }

# Create tools directory in home
TOOLS_DIR=~/claude-workflow-tools
echo "📦 Installing workflow tools to $TOOLS_DIR..."

# Backup existing tools if present
if [ -d "$TOOLS_DIR" ]; then
    echo "⚠️  Existing tools found. Creating backup..."
    mv "$TOOLS_DIR" "${TOOLS_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create fresh installation
mkdir -p "$TOOLS_DIR/workflow"

# Copy workflow tools
if [ -d "tools/workflow" ]; then
    cp -r tools/workflow/* "$TOOLS_DIR/workflow/"
    echo "✅ Workflow tools copied"
else
    echo "❌ Error: tools/workflow not found in current directory"
    exit 1
fi

# Make all tools executable
chmod +x "$TOOLS_DIR/workflow"/*.py
echo "✅ Tools made executable"

# Create global setup script
cat > ~/setup_autonomous_project.sh << 'EOF'
#!/bin/bash
# Setup script for autonomous Claude Code projects
# Usage: bash ~/setup_autonomous_project.sh [project_name]

set -e

PROJECT_NAME=${1:-$(basename $(pwd))}
WORKFLOW_TOOLS_SOURCE=~/claude-workflow-tools/workflow

echo "🚀 Setting up autonomous project: $PROJECT_NAME"

# Create directory structure
mkdir -p .claude docs/behavior docs/architecture docs/development_roadmap
mkdir -p investigations/current_work research tests src tools/workflow logs/errors/active

# Copy workflow tools
cp -r $WORKFLOW_TOOLS_SOURCE/* tools/workflow/
chmod +x tools/workflow/*.py

# Create CLAUDE.md
cat > CLAUDE.md << EOCLAUD
# Project: $PROJECT_NAME

## Project Overview
[Describe project purpose here]

## Workflow State
\`\`\`json
{
  "workflow_state": {
    "current_command": "/explore",
    "current_phase": "discovery",
    "iteration": 0
  }
}
\`\`\`
EOCLAUD

echo "✅ Project setup complete! Next: Edit CLAUDE.md and run /explore"
EOF

chmod +x ~/setup_autonomous_project.sh
echo "✅ Global setup script created at ~/setup_autonomous_project.sh"

# Check and update Claude Code hooks configuration
echo ""
echo "📝 Checking Claude Code hooks configuration..."

CLAUDE_SETTINGS=~/.claude/settings.json

if [ -f "$CLAUDE_SETTINGS" ]; then
    echo "Found existing settings at $CLAUDE_SETTINGS"
    
    # Check if hooks are configured
    if grep -q '"hooks"' "$CLAUDE_SETTINGS"; then
        echo "✅ Hooks already configured"
        echo "⚠️  Please verify Stop and SessionStart hooks are set up"
    else
        echo "⚠️  No hooks found in settings"
        echo "📌 Add the following hooks configuration to $CLAUDE_SETTINGS:"
    fi
else
    echo "📝 Creating new Claude settings with hooks..."
    mkdir -p ~/.claude
    cat > "$CLAUDE_SETTINGS" << 'EOF'
{
  "model": "opus",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "[ -f \"$CLAUDE_PROJECT_DIR/tools/workflow/workflow_orchestrator.py\" ] && python3 \"$CLAUDE_PROJECT_DIR/tools/workflow/workflow_orchestrator.py\" --quiet >> \"$CLAUDE_PROJECT_DIR/.claude/workflow.log\" 2>&1 || true"
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
            "command": "[ -f \"$CLAUDE_PROJECT_DIR/tools/workflow/session_recovery.py\" ] && python3 \"$CLAUDE_PROJECT_DIR/tools/workflow/session_recovery.py\" --json > \"$CLAUDE_PROJECT_DIR/.claude/session_context.json\" 2>&1 || true"
          }
        ]
      }
    ]
  }
}
EOF
    echo "✅ Created Claude settings with hooks"
fi

# Create external archive directory
ARCHIVE_BASE=~/projects/archive
mkdir -p "$ARCHIVE_BASE"
echo "✅ External archive directory ready at $ARCHIVE_BASE"

# Summary
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📦 Installed components:"
echo "  • Workflow tools: $TOOLS_DIR"
echo "  • Setup script: ~/setup_autonomous_project.sh"
echo "  • Archive location: $ARCHIVE_BASE"
echo ""
echo "🚀 To create a new autonomous project:"
echo "  1. Create and enter project directory:"
echo "     mkdir my-project && cd my-project"
echo "  2. Run setup script:"
echo "     bash ~/setup_autonomous_project.sh"
echo "  3. Configure hooks in Claude Code:"
echo "     /hooks"
echo "  4. Start autonomous workflow:"
echo "     /explore"
echo ""
echo "📚 Documentation:"
echo "  • Setup guide: AUTONOMOUS_SETUP_GUIDE.md"
echo "  • Workflow tools: $TOOLS_DIR/workflow/README.md"
echo ""
echo "⚠️  Important: Restart Claude Code after installation for hooks to take effect"