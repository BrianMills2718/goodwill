#!/usr/bin/env python3
"""
Autonomous Orchestrator Hook

Main entry point that decides between planning process and implementation process
based on current project state. Implements the two-process architecture with
proper handoff between planning and implementation.
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

class AutonomousOrchestrator:
    """Main orchestrator that routes between planning and implementation processes"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.orchestrator_state_file = self.project_root / ".autonomous_state" / "orchestrator_state.json"
        self.planning_state_file = self.project_root / ".autonomous_state" / "planning_state.json"
        self.current_state = self._load_orchestrator_state()
        
    def _load_orchestrator_state(self) -> Dict[str, Any]:
        """Load orchestrator state or initialize"""
        if self.orchestrator_state_file.exists():
            with open(self.orchestrator_state_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "current_process": "planning",  # Start with planning
                "process_history": [],
                "stop_hook_recursion_protection": False,
                "last_updated": time.time()
            }
    
    def _save_orchestrator_state(self):
        """Save orchestrator state"""
        self.orchestrator_state_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_state["last_updated"] = time.time()
        with open(self.orchestrator_state_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)
    
    def _planning_complete(self) -> bool:
        """Check if planning process is complete"""
        if not self.planning_state_file.exists():
            return False
            
        with open(self.planning_state_file, 'r') as f:
            planning_state = json.load(f)
            
        return planning_state.get("current_phase") == "complete"
    
    def _manual_override_active(self) -> bool:
        """Check if manual override is active"""
        override_file = self.project_root / ".workflow_override"
        return override_file.exists()
    
    def _recursion_protection_check(self, input_data: Dict[str, Any]) -> bool:
        """Check for Stop hook recursion"""
        if input_data.get("stop_hook_active"):
            return True
            
        # Check for rapid consecutive calls
        lock_file = self.project_root / ".claude" / ".lock" / "stop.lock"
        if lock_file.exists():
            lock_age = time.time() - lock_file.stat().st_mtime
            if lock_age < 5:  # Lock still fresh
                return True
        
        return False
    
    def _create_stop_lock(self):
        """Create stop hook lock to prevent recursion"""
        lock_dir = self.project_root / ".claude" / ".lock"
        lock_dir.mkdir(parents=True, exist_ok=True)
        
        lock_file = lock_dir / "stop.lock"
        with open(lock_file, 'w') as f:
            f.write(str(time.time()))
    
    def _remove_stop_lock(self):
        """Remove stop hook lock"""
        lock_file = self.project_root / ".claude" / ".lock" / "stop.lock"
        if lock_file.exists():
            lock_file.unlink()
    
    def execute_autonomous_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestrator entry point"""
        
        # Recursion protection
        if self._recursion_protection_check(input_data):
            return {"continue": True, "suppressOutput": True}
        
        # Manual override check
        if self._manual_override_active():
            return {"continue": True, "suppressOutput": True}
        
        # Create lock to prevent concurrent execution
        self._create_stop_lock()
        
        try:
            # Determine which process to execute
            if self._planning_complete():
                process_type = "implementation"
            else:
                process_type = "planning"
            
            # Update current process if changed
            if self.current_state["current_process"] != process_type:
                self.current_state["process_history"].append({
                    "from": self.current_state["current_process"],
                    "to": process_type,
                    "timestamp": time.time()
                })
                self.current_state["current_process"] = process_type
                self._save_orchestrator_state()
            
            # Execute appropriate process
            if process_type == "planning":
                # Import here to avoid circular imports
                from src.hook.planning_process_hook import PlanningProcessHook
                planning_hook = PlanningProcessHook(str(self.project_root))
                result = planning_hook.execute_planning_process()
            else:
                # Import here to avoid circular imports
                from src.hook.implementation_process_hook import ImplementationProcessHook
                implementation_hook = ImplementationProcessHook(str(self.project_root))
                result = implementation_hook.execute_implementation_process()
            
            # Convert result to Claude Code Stop hook format
            if result.get("decision") == "block":
                # Force Claude to continue with the specified instruction
                return {
                    "decision": "block",
                    "reason": result["reason"]
                }
            elif result.get("decision") == "continue":
                # Let Claude continue normally
                return {"continue": True, "suppressOutput": True}
            else:
                # Default to continue
                return {"continue": True, "suppressOutput": True}
                
        except Exception as e:
            # Error handling
            error_msg = f"Autonomous orchestrator error: {str(e)}"
            return {
                "decision": "block",
                "reason": f"**ERROR**: {error_msg}\n\nCheck autonomous system logs for details."
            }
        
        finally:
            # Always remove lock
            self._remove_stop_lock()

def main():
    """Main hook entry point for Claude Code Stop hook"""
    try:
        # HOOK EXECUTION EVIDENCE: Log that Stop hook was actually triggered by Claude Code
        project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        log_hook_execution(project_dir, "stop_hook", "Stop hook triggered by Claude Code")
        
        # Get input data from Claude Code
        input_data = {}
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        
        # Initialize orchestrator
        orchestrator = AutonomousOrchestrator(project_dir)
        
        # Execute autonomous process
        result = orchestrator.execute_autonomous_process(input_data)
        
        # Output result for Claude Code
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        error_result = {
            "continue": True,
            "suppressOutput": True
        }
        print(json.dumps(error_result))
        return 1

if __name__ == "__main__":
    sys.exit(main())