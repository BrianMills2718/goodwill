#!/usr/bin/env python3
"""
Evidence Validator Hook

PostToolUse hook that validates evidence and detects when automation 
should create evidence artifacts for completion claims.
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

def log_hook_execution(project_dir: str, hook_type: str, context: str = ""):
    """Log evidence that hook was actually executed by Claude Code"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_dir = Path(project_dir) / "logs" / "hook_execution_tests"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{hook_type}_{timestamp}.log"
    
    log_data = {
        "hook_type": hook_type,
        "timestamp": timestamp,
        "context": context,
        "executed_at": datetime.now().isoformat(),
        "evidence": "Hook actually executed by Claude Code",
        "argv": sys.argv,
        "environment": {
            "CLAUDE_PROJECT_DIR": os.environ.get('CLAUDE_PROJECT_DIR'),
            "PWD": os.environ.get('PWD')
        }
    }
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)

def main():
    """Evidence validator hook for PostToolUse"""
    try:
        # HOOK EXECUTION EVIDENCE: Log that PostToolUse hook was actually triggered
        project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
        log_hook_execution(str(project_dir), "post_tool_use", "PostToolUse evidence validator triggered")
        
        # Get input data from Claude Code
        input_data = {}
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        
        # Simple evidence validation (full implementation would be more sophisticated)
        tool_name = input_data.get("toolName", "")
        
        # Check if writing to implementation files
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path = input_data.get("parameters", {}).get("file_path", "")
            
            # If writing to src/ directory, should create implementation evidence
            if "src/" in file_path and file_path.endswith(".py"):
                investigations_dir = project_dir / "investigations"
                if not investigations_dir.exists():
                    # Suggest evidence creation
                    return {
                        "decision": "block",
                        "reason": """**EVIDENCE REQUIRED**: Implementation changes detected
                        
                        Create evidence artifacts:
                        1. investigations/[area]/phase_X/findings.md
                        2. investigations/[area]/phase_X/test_results.log  
                        3. investigations/[area]/phase_X/implementation_proof.md
                        4. investigations/[area]/phase_X/evidence.json
                        
                        Document implementation changes with evidence."""
                    }
        
        # Default: allow operation to continue
        return {"continue": True}
        
    except Exception as e:
        # On error, allow operation to continue
        return {"continue": True}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
    sys.exit(0)