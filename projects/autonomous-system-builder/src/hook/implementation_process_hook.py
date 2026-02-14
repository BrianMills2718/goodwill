#!/usr/bin/env python3
"""
V6 Implementation Process Hook

Implements the V6 hybrid intelligence implementation flowchart as a Claude Code hook
to autonomously execute implementation with planning artifact integration.

This hook implements the V6 flowchart from:
hook_mermaid_diagram_full6_hybrid_intelligence.txt
"""

import sys
import json
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class ImplementationProcessHook:
    """Implements the V6 implementation flowchart as an autonomous hook"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / ".autonomous_state" / "implementation_state.json"
        self.planning_state_file = self.project_root / ".autonomous_state" / "planning_state.json"
        self.error_log_dir = self.project_root / "logs" / "errors" / "active"
        self.investigations_dir = self.project_root / "investigations"
        self.current_state = self._load_implementation_state()
        
    def _load_implementation_state(self) -> Dict[str, Any]:
        """Load current implementation state or initialize"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "current_mode": "planning_input_check",
                "loop_iterations": 0,
                "stop_hook_count": 0,
                "implementation_targets": [],
                "task_graph": {},
                "current_component": None,
                "test_status": "unknown",
                "evidence_path": None,
                "automation_health": "good",
                "last_updated": time.time()
            }
    
    def _save_implementation_state(self):
        """Save current implementation state"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_state["last_updated"] = time.time()
        with open(self.state_file, 'w') as f:
            json.dump(self.current_state, f, indent=2)
    
    def _manual_override_exists(self) -> bool:
        """🤖 Check if manual override file exists"""
        override_file = self.project_root / ".workflow_override"
        return override_file.exists()
    
    def _planning_artifacts_available(self) -> bool:
        """🤖 Check if planning artifacts are available"""
        planning_state_file = self.planning_state_file
        if not planning_state_file.exists():
            return False
            
        with open(planning_state_file, 'r') as f:
            planning_state = json.load(f)
            
        return planning_state.get("planning_artifacts_locked", False)
    
    def _check_iteration_limits(self) -> Tuple[bool, str, str]:
        """🤖 Check iteration limits"""
        loop_limit = 7
        stop_hook_limit = 3
        
        if self.current_state["loop_iterations"] >= loop_limit:
            return False, "uncertainty_resolution", f"Loop iterations >= {loop_limit}"
        
        if self.current_state["stop_hook_count"] >= stop_hook_limit:
            return False, "stop_hook", f"Stop hooks >= {stop_hook_limit}"
            
        return True, "within_limits", "All limits OK"
    
    def _run_tests(self) -> Dict[str, Any]:
        """🤖 Run test suite and return results"""
        try:
            # Run pytest and capture results
            result = subprocess.run(
                ["python", "-m", "pytest", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests_passing": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "return_code": 1,
                "stdout": "",
                "stderr": "Test execution timed out",
                "tests_passing": False
            }
        except Exception as e:
            return {
                "return_code": 1,
                "stdout": "",
                "stderr": f"Test execution error: {str(e)}",
                "tests_passing": False
            }
    
    def _inject_error_to_claude_md(self, error_type: str, error_msg: str):
        """🤖 Inject error into CLAUDE.md Active Errors section"""
        claude_md_path = self.project_root / "CLAUDE.md"
        
        # Create error log
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        error_log_file = self.error_log_dir / f"error_{timestamp}.log"
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
        
        with open(error_log_file, 'w') as f:
            f.write(f"Error Type: {error_type}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Message: {error_msg}\n")
            f.write(f"Implementation State: {json.dumps(self.current_state, indent=2)}\n")
        
        # Update error summary JSON
        summary_file = self.error_log_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary = json.load(f)
        else:
            summary = {"active_errors": []}
        
        summary["active_errors"].append({
            "type": error_type,
            "message": error_msg,
            "timestamp": timestamp,
            "log_file": str(error_log_file.name)
        })
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Inject into CLAUDE.md (simplified - real implementation would parse and update)
        error_entry = f"\n🚨 **{error_type.upper()}**: {error_msg} (Log: {error_log_file.name})\n"
        
        if claude_md_path.exists():
            content = claude_md_path.read_text()
            if "🚨 ACTIVE ERRORS" in content:
                # Add to existing errors section
                content = content.replace("🚨 ACTIVE ERRORS", f"🚨 ACTIVE ERRORS{error_entry}")
            else:
                # Add new errors section at top
                content = f"## 🚨 ACTIVE ERRORS{error_entry}\n\n" + content
            claude_md_path.write_text(content)
    
    def _quality_validation_pipeline(self) -> Tuple[bool, Optional[str]]:
        """🤖 Execute quality validation pipeline"""
        
        # Cross-reference integrity check (simplified)
        try:
            result = subprocess.run(
                ["python", "tools/validate_references.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self._inject_error_to_claude_md("cross_reference", "Cross-reference validation failed")
                return False, "cross_reference_error"
        except:
            self._inject_error_to_claude_md("cross_reference", "Cross-reference validation tool failed")
            return False, "cross_reference_error"
        
        # Evidence completeness check
        if self.current_state.get("evidence_path"):
            evidence_path = Path(self.current_state["evidence_path"])
            required_files = ["findings.md", "test_results.log", "implementation_proof.md", "evidence.json"]
            
            for req_file in required_files:
                if not (evidence_path / req_file).exists():
                    self._inject_error_to_claude_md("evidence", f"Missing evidence file: {req_file}")
                    return False, "evidence_incomplete"
        
        # State consistency check (simplified)
        test_results = self._run_tests()
        claimed_status = self.current_state.get("test_status", "unknown")
        actual_status = "passing" if test_results["tests_passing"] else "failing"
        
        if claimed_status != "unknown" and claimed_status != actual_status:
            self._inject_error_to_claude_md("state_consistency", 
                f"Claimed test status ({claimed_status}) != actual ({actual_status})")
            return False, "state_inconsistent"
        
        # Automation health check
        if self.current_state["loop_iterations"] > 5:
            self.current_state["automation_health"] = "warning"
        elif self.current_state["loop_iterations"] > 3:
            self.current_state["automation_health"] = "good"
        else:
            self.current_state["automation_health"] = "excellent"
        
        if self.current_state["automation_health"] == "warning":
            self._inject_error_to_claude_md("automation_health", "Automation health degrading - high iteration count")
            return False, "automation_unhealthy"
        
        return True, None
    
    def _select_implementation_mode(self) -> str:
        """🧠 LLM: Select implementation mode (simplified heuristic for now)"""
        
        # Check if we have task graph and planning artifacts
        has_task_graph = bool(self.current_state.get("task_graph"))
        has_planning = self._planning_artifacts_available()
        
        # Check test status
        test_results = self._run_tests()
        has_failing_tests = not test_results["tests_passing"]
        
        if has_planning and has_task_graph and not has_failing_tests:
            return "task_graph_mode"
        elif has_failing_tests:
            return "tdd_mode"
        elif has_planning and has_failing_tests:
            return "hybrid_mode"
        else:
            return "fallback_tdd_mode"
    
    def _execute_task_graph_mode(self) -> Dict[str, Any]:
        """Execute task-graph driven implementation"""
        # Load next task from graph (simplified)
        task_graph = self.current_state.get("task_graph", {})
        
        if not task_graph:
            return {
                "decision": "block",
                "reason": "Task graph not available. Loading task graph from planning artifacts..."
            }
        
        # Find next available task
        for task_id, task in task_graph.items():
            if task.get("status") == "ready":
                self.current_state["current_component"] = task_id
                self._save_implementation_state()
                return {
                    "decision": "block", 
                    "reason": f"**EXECUTE**: Implement component {task_id}\n\n{task.get('description', '')}"
                }
        
        # No ready tasks - check for completed work
        return {
            "decision": "continue",
            "reason": "All task graph components complete. Running tests to verify implementation."
        }
    
    def _execute_tdd_mode(self) -> Dict[str, Any]:
        """Execute TDD failure-driven implementation"""
        test_results = self._run_tests()
        
        if test_results["tests_passing"]:
            return {
                "decision": "continue", 
                "reason": "All tests passing. Implementation phase may be complete."
            }
        
        # Analyze test failures (simplified)
        stderr = test_results.get("stderr", "")
        stdout = test_results.get("stdout", "")
        
        if "ImportError" in stderr or "ModuleNotFoundError" in stderr:
            return {
                "decision": "block",
                "reason": "**EXECUTE**: Fix import errors\n\nResolve missing imports and module dependencies."
            }
        elif "FAILED" in stdout:
            return {
                "decision": "block", 
                "reason": "**EXECUTE**: Fix failing tests\n\nImplement functionality to make tests pass."
            }
        else:
            return {
                "decision": "block",
                "reason": "**EXECUTE**: Debug test execution issues\n\nResolve test execution problems."
            }
    
    def _execute_hybrid_mode(self) -> Dict[str, Any]:
        """Execute hybrid planning+TDD mode"""
        # Check both planning progress and test status
        task_graph_result = self._execute_task_graph_mode()
        tdd_result = self._execute_tdd_mode()
        
        # Prioritize based on context (simplified heuristic)
        if "Fix failing tests" in tdd_result["reason"]:
            return tdd_result  # Fix broken tests first
        else:
            return task_graph_result  # Follow planning when tests are stable
    
    def execute_implementation_process(self) -> Dict[str, Any]:
        """Main entry point - execute V6 implementation flowchart"""
        
        # Manual override check
        if self._manual_override_exists():
            return {
                "decision": "block",
                "reason": "**STOP**: Manual override active\nRemove .workflow_override to resume"
            }
        
        # Planning input check
        if not self._planning_artifacts_available():
            # Fall back to safety limits and basic TDD
            within_limits, limit_type, limit_msg = self._check_iteration_limits()
            if not within_limits:
                return self._handle_escalation(limit_type, limit_msg)
            
            # Run quality validation
            quality_ok, quality_error = self._quality_validation_pipeline()
            if not quality_ok:
                return {
                    "decision": "block",
                    "reason": f"Quality validation failed: {quality_error}"
                }
            
            # Execute basic TDD mode
            return self._execute_tdd_mode()
        
        # Full planning-integrated flow
        within_limits, limit_type, limit_msg = self._check_iteration_limits()
        if not within_limits:
            return self._handle_escalation(limit_type, limit_msg)
        
        # Quality validation pipeline
        quality_ok, quality_error = self._quality_validation_pipeline() 
        if not quality_ok:
            return {
                "decision": "block",
                "reason": f"Quality validation failed: {quality_error}"
            }
        
        # Select and execute implementation mode
        mode = self._select_implementation_mode()
        self.current_state["current_mode"] = mode
        
        if mode == "task_graph_mode":
            result = self._execute_task_graph_mode()
        elif mode == "tdd_mode":
            result = self._execute_tdd_mode()
        elif mode == "hybrid_mode":
            result = self._execute_hybrid_mode()
        else:  # fallback_tdd_mode
            result = self._execute_tdd_mode()
        
        # Update iteration count and save state
        self.current_state["loop_iterations"] += 1
        self._save_implementation_state()
        
        return result
    
    def _handle_escalation(self, limit_type: str, limit_msg: str) -> Dict[str, Any]:
        """Handle escalation when limits are exceeded"""
        
        if limit_type == "uncertainty_resolution":
            # Escalation strategies: archive, simplify, human
            return {
                "decision": "block",
                "reason": f"""**ESCALATE**: {limit_msg}
                
                Choose escalation strategy:
                1. Archive unresolved issues to investigations/deferred/
                2. Simplify objective to achievable subset
                3. Request human intervention
                
                Manual intervention may be required."""
            }
        
        elif limit_type == "stop_hook":
            # Create manual override and escalate
            override_file = self.project_root / ".workflow_override"
            override_file.write_text(f"Manual override created due to stop hook loop limit\nTimestamp: {time.time()}")
            
            return {
                "decision": "block",
                "reason": f"""**ESCALATE**: {limit_msg}
                
                Stop hook loop detected. Manual override created.
                Remove .workflow_override to continue manually."""
            }
        
        else:
            return {
                "decision": "block",
                "reason": f"**ESCALATE**: {limit_msg}\nHuman intervention required"
            }

def main():
    """Main hook entry point for Claude Code"""
    try:
        # Get input data from Claude Code
        input_data = {}
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        
        # Initialize implementation process hook
        project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        hook = ImplementationProcessHook(project_dir)
        
        # Increment stop hook count for this execution
        hook.current_state["stop_hook_count"] += 1
        
        # Execute implementation process
        result = hook.execute_implementation_process()
        
        # Output result for Claude Code
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        error_result = {
            "decision": "block",
            "reason": f"Implementation process hook error: {str(e)}"
        }
        print(json.dumps(error_result))
        return 1

if __name__ == "__main__":
    sys.exit(main())