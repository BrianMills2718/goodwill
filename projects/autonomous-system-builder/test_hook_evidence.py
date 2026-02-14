#!/usr/bin/env python3
"""
Hook Integration Test Script
Creates observable evidence files when hooks execute
"""

import json
import time
from datetime import datetime
from pathlib import Path

def log_hook_execution(hook_type: str, context: str = ""):
    """Log that a hook actually executed"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_dir = Path("logs/hook_execution_tests")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"{hook_type}_{timestamp}.log"
    
    log_data = {
        "hook_type": hook_type,
        "timestamp": timestamp,
        "context": context,
        "executed_at": datetime.now().isoformat(),
        "test_evidence": "Hook actually executed by Claude Code"
    }
    
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"Hook execution logged: {log_file}")
    return str(log_file)

if __name__ == "__main__":
    # Test direct execution vs hook execution
    log_hook_execution("direct_execution", "Running test script directly")