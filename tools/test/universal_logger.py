#!/usr/bin/env python3
"""
Universal hook logger for investigating Claude Code hook behavior.
Logs all hook inputs to help understand actual JSON structure.
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

def main():
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except Exception as e:
        input_data = {"error": f"Could not parse input: {str(e)}"}
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    hook_event = input_data.get("hook_event_name", "unknown")
    
    # Ensure output directory exists
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "/home/brian/projects/goodwill")
    output_dir = Path(project_dir) / "investigations/automated_workflow_planning/hook_inputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save input with full context
    output_file = output_dir / f"{timestamp}_{hook_event}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "hook_event": hook_event,
            "input": input_data,
            "environment": {
                "cwd": os.getcwd(),
                "claude_project_dir": os.environ.get("CLAUDE_PROJECT_DIR", "not set"),
                "env_vars": {k: v for k, v in os.environ.items() if 'CLAUDE' in k}
            },
            "stdin_bytes": len(json.dumps(input_data))
        }, f, indent=2)
    
    # Log to stderr so it appears in transcript
    print(f"Hook logged: {hook_event} → {output_file.name}", file=sys.stderr)
    
    # Return success - continue execution normally
    output = {"continue": True, "suppressOutput": True}
    print(json.dumps(output))

if __name__ == "__main__":
    main()