#!/usr/bin/env python3
"""
Start the autonomous workflow system
Usage: python3 tools/workflow/start_workflow.py
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

def clear_errors():
    """Clear the active errors that are actually workflow tool issues"""
    claude_md = Path("CLAUDE.md")
    if not claude_md.exists():
        return
        
    content = claude_md.read_text()
    
    # Remove the workflow tool errors
    lines = content.split('\n')
    filtered = []
    skip_error = False
    
    for line in lines:
        # Skip the workflow tool reference errors
        if 'REFERENCE_UPDATE_NEEDED' in line or 'BROKEN_REFERENCE: Test error injection' in line:
            skip_error = True
            continue
        if skip_error and line.strip().startswith('-'):
            continue
        if skip_error and not line.strip():
            skip_error = False
            continue
        filtered.append(line)
    
    # Clean up the error section
    cleaned = []
    for i, line in enumerate(filtered):
        if '### Active Errors:' in line and i+1 < len(filtered) and filtered[i+1].strip() == '(None currently)':
            # Skip duplicate "(None currently)"
            continue
        cleaned.append(line)
    
    claude_md.write_text('\n'.join(cleaned))

def initialize_workflow():
    """Initialize the workflow system"""
    print("🚀 Starting Autonomous Workflow System")
    print("=" * 60)
    
    # Clear workflow tool errors
    print("📝 Clearing workflow tool reference errors...")
    clear_errors()
    
    # Reset workflow state to start with phase loading
    state = {
        "current_command": None,  # Will trigger /load_phase_plans
        "iteration": 0,
        "timestamp": datetime.now().isoformat(),
        "previous_command": None,
        "phase": "initialization",
        "has_evidence": False,
        "phase_loaded": False
    }
    
    state_file = Path(".claude/workflow_state.json")
    state_file.parent.mkdir(exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2))
    print("✅ Workflow state initialized")
    
    # Run orchestrator to set first command
    print("\n📊 Running workflow orchestrator...")
    result = subprocess.run(
        [sys.executable, "tools/workflow/workflow_orchestrator.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    print("\n" + "=" * 60)
    print("🎯 WORKFLOW STARTED!")
    print("=" * 60)
    print("\nThe autonomous workflow is now active.")
    print("CLAUDE.md has been updated with the first instruction.")
    print("\nThe Stop hook will automatically suggest next commands.")
    print("Just follow the instructions in CLAUDE.md to proceed.")
    print("\nTo check workflow status at any time, run:")
    print("  python3 tools/workflow/workflow_orchestrator.py")

if __name__ == "__main__":
    initialize_workflow()