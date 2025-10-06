#!/usr/bin/env python3
"""
Enhanced Autonomous TDD Hook with Safety Features
Template-ready design for any project using Claude Code

Safety Features:
- Loop iteration limiting (max 7 cycles)
- Stop-hook counting (max 3 consecutive stops)
- Automation health monitoring
- Manual override capability
- Project-agnostic documentation reading
"""
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class AutonomousTDDHook:
    def __init__(self):
        # Get project root from Claude Code environment
        self.project_root = os.environ.get('CLAUDE_PROJECT_DIR')
        if not self.project_root:
            print("Error: CLAUDE_PROJECT_DIR not set", file=sys.stderr)
            sys.exit(1)
        
        self.project_root = Path(self.project_root)
        self.claude_dir = self.project_root / '.claude'
        self.state_file = self.claude_dir / 'workflow_state.txt'
        self.override_file = self.claude_dir / 'workflow_override'
        self.health_script = self.project_root / 'tools' / 'workflow' / 'state_reconciliation.py'
        self.attempt_history_file = self.claude_dir / 'attempt_history.json'
        
        # Safety limits
        self.MAX_LOOP_ITERATIONS = 7
        self.MAX_STOP_HOOK_COUNT = 3
        
    def check_manual_override(self):
        """Check if manual override is active"""
        if self.override_file.exists():
            return {
                "decision": "approve",
                "reason": "Manual override active - stopping autonomous mode. Remove .claude/workflow_override to resume."
            }
        return None
    
    def check_automation_health(self):
        """Check automation health using state reconciliation"""
        if not self.health_script.exists():
            return "no_health_script"
        
        try:
            # Use absolute path and simpler call
            cmd = f"cd {self.project_root} && python3 tools/workflow/state_reconciliation.py --health"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "health_check_failed"
        except:
            return "health_check_exception"
    
    def get_loop_counters(self):
        """Get current loop iteration and stop hook counts"""
        counter_file = self.claude_dir / 'loop_counters.json'
        
        if counter_file.exists():
            try:
                with open(counter_file) as f:
                    data = json.load(f)
                return data.get('loop_iterations', 0), data.get('stop_hook_count', 0)
            except:
                pass
        
        return 0, 0
    
    def update_loop_counters(self, loop_iterations, stop_hook_count):
        """Update loop counters"""
        counter_file = self.claude_dir / 'loop_counters.json'
        
        data = {
            'loop_iterations': loop_iterations,
            'stop_hook_count': stop_hook_count,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(counter_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_attempt_history(self):
        """Load cross-session attempt history"""
        if self.attempt_history_file.exists():
            try:
                with open(self.attempt_history_file) as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "failed_strategies": [],
            "successful_patterns": [],
            "insights": [],
            "session_count": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def save_attempt_history(self, history):
        """Save cross-session attempt history"""
        self.claude_dir.mkdir(exist_ok=True)
        history["last_updated"] = datetime.now().isoformat()
        with open(self.attempt_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def record_strategy_failure(self, strategy, reason, phase=None):
        """Record a failed strategy to prevent repetition"""
        history = self.load_attempt_history()
        
        failure_record = {
            "strategy": strategy,
            "reason": reason,
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        }
        
        # Avoid duplicates
        for existing in history["failed_strategies"]:
            if existing["strategy"] == strategy and existing.get("phase") == phase:
                existing["reason"] = reason  # Update reason
                existing["timestamp"] = failure_record["timestamp"]
                break
        else:
            history["failed_strategies"].append(failure_record)
        
        # Keep only recent failures (last 20)
        history["failed_strategies"] = history["failed_strategies"][-20:]
        
        self.save_attempt_history(history)
    
    def record_strategy_success(self, strategy, outcome, phase=None):
        """Record a successful strategy for future reference"""
        history = self.load_attempt_history()
        
        success_record = {
            "strategy": strategy,
            "outcome": outcome,
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        }
        
        # Avoid duplicates
        for existing in history["successful_patterns"]:
            if existing["strategy"] == strategy and existing.get("phase") == phase:
                existing["outcome"] = outcome
                existing["timestamp"] = success_record["timestamp"]
                break
        else:
            history["successful_patterns"].append(success_record)
        
        # Keep only recent successes (last 20)  
        history["successful_patterns"] = history["successful_patterns"][-20:]
        
        self.save_attempt_history(history)
    
    def add_insight(self, insight):
        """Add a strategic insight from experience"""
        history = self.load_attempt_history()
        
        insight_record = {
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        }
        
        # Avoid exact duplicates
        if not any(existing["insight"] == insight for existing in history["insights"]):
            history["insights"].append(insight_record)
        
        # Keep only recent insights (last 15)
        history["insights"] = history["insights"][-15:]
        
        self.save_attempt_history(history)
    
    def get_historical_context(self, current_phase=None):
        """Get historical context for current situation"""
        history = self.load_attempt_history()
        
        # Filter for current phase if specified
        relevant_failures = [
            f for f in history["failed_strategies"] 
            if not current_phase or f.get("phase") == current_phase
        ]
        
        relevant_successes = [
            s for s in history["successful_patterns"]
            if not current_phase or s.get("phase") == current_phase
        ]
        
        context = ""
        if relevant_failures:
            context += "\\n\\nPrevious failed approaches to avoid:"
            for failure in relevant_failures[-3:]:  # Last 3 failures
                context += f"\\n- {failure['strategy']}: {failure['reason']}"
        
        if relevant_successes:
            context += "\\n\\nPrevious successful patterns:"
            for success in relevant_successes[-2:]:  # Last 2 successes
                context += f"\\n- {success['strategy']}: {success['outcome']}"
        
        if history["insights"]:
            context += "\\n\\nKey insights from experience:"
            for insight in history["insights"][-2:]:  # Last 2 insights
                context += f"\\n- {insight['insight']}"
        
        return context
    
    def check_safety_limits(self):
        """Check if safety limits have been exceeded"""
        loop_iterations, stop_hook_count = self.get_loop_counters()
        
        # Check stop hook limit
        if stop_hook_count >= self.MAX_STOP_HOOK_COUNT:
            # Record this as a failed strategy
            current_step = self.get_current_step()
            self.record_strategy_failure(
                strategy=f"repeated_{current_step}_attempts",
                reason=f"Hit {stop_hook_count} consecutive stop hooks without progress",
                phase=current_step
            )
            self.add_insight("Multiple consecutive stop hooks indicate stuck workflow - may need different approach or manual intervention")
            
            return {
                "decision": "approve",
                "reason": f"Safety limit reached: {stop_hook_count} consecutive stop hooks. Taking manual break to prevent infinite loops."
            }
        
        # Check loop iteration limit  
        if loop_iterations >= self.MAX_LOOP_ITERATIONS:
            # Record this as a failed strategy - couldn't complete in reasonable iterations
            self.record_strategy_failure(
                strategy="full_tdd_cycle_completion",
                reason=f"Could not complete work within {loop_iterations} iterations",
                phase="full_cycle"
            )
            self.add_insight(f"Work requiring more than {self.MAX_LOOP_ITERATIONS} iterations may need task breakdown or different approach")
            
            return {
                "decision": "approve", 
                "reason": f"Safety limit reached: {loop_iterations} loop iterations completed. Escalating to manual review for complex issues."
            }
        
        return None
    
    def get_current_step(self):
        """Get current workflow step"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return f.read().strip()
            except:
                pass
        return "load_phase"
    
    def set_current_step(self, step):
        """Set current workflow step"""
        self.claude_dir.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            f.write(step)
    
    def get_next_step(self, current_step):
        """Determine next TDD step"""
        workflow = {
            "load_phase": "explore",
            "explore": "write_tests",
            "write_tests": "implement", 
            "implement": "run_tests",
            "run_tests": "doublecheck",
            "doublecheck": "commit",
            "commit": "explore"  # New cycle
        }
        return workflow.get(current_step, "load_phase")
    
    def read_project_docs(self):
        """Read project documentation to understand current goals (template-ready)"""
        docs = {}
        
        # Try to read common documentation locations
        doc_paths = {
            'phases': ['docs/development_roadmap/phases.md', 'docs/phases.md', 'PHASES.md'],
            'behavior': ['docs/behavior/desired_behavior.md', 'docs/requirements.md', 'REQUIREMENTS.md'],
            'architecture': ['docs/architecture/system_overview.md', 'docs/architecture.md', 'ARCHITECTURE.md'],
            'claude_md': ['CLAUDE.md', 'README.md']
        }
        
        for doc_type, paths in doc_paths.items():
            for path in paths:
                doc_file = self.project_root / path
                if doc_file.exists():
                    try:
                        with open(doc_file) as f:
                            docs[doc_type] = f.read()
                        break
                    except:
                        continue
        
        return docs
    
    def generate_instruction(self, step, project_docs):
        """Generate context-aware instruction based on project docs"""
        
        # Default template-ready instructions
        base_instructions = {
            "load_phase": "Read project documentation to understand current phase and requirements. Update CLAUDE.md with phase status and next tasks.",
            
            "explore": "Explore the codebase and requirements for the current phase. Read relevant documentation and existing code. Create investigation notes documenting your findings.",
            
            "write_tests": "Write comprehensive tests following TDD principles. Tests should cover the requirements and initially fail. Use appropriate testing framework for the project.",
            
            "implement": "Implement the code to make your tests pass. Follow project conventions and architecture patterns. Focus on making tests pass with clean, maintainable code.",
            
            "run_tests": "Run the test suite and verify all tests pass. Create evidence of test results including coverage metrics if available.",
            
            "doublecheck": "Verify the implementation meets requirements. Test edge cases and error handling. Create verification documentation showing success criteria are met.",
            
            "commit": "Commit your changes with a clear, descriptive commit message. Stage relevant files and create evidence of successful commit."
        }
        
        instruction = base_instructions.get(step, f"Continue working on {step}")
        
        # Enhance instruction with project-specific context if available
        if 'claude_md' in project_docs and project_docs['claude_md']:
            claude_content = project_docs['claude_md']
            
            # Check for sandbox test mode first
            if 'sandbox_math_utility' in claude_content:
                if step == "explore":
                    instruction += " Focus on the sandbox math utility task: create src/utils/math_helper.py with profit calculation, ROI, and currency formatting functions."
                elif step == "write_tests":
                    instruction += " Write tests for math_helper.py functions: calculate_profit, calculate_roi, format_currency. Include edge cases and follow TDD principles."
                elif step == "implement":
                    instruction += " Implement math_helper.py functions to make the tests pass. Focus on clean, simple code for the sandbox test."
            elif 'Phase 1' in claude_content and 'eBay API' in claude_content:
                # Add Goodwill-specific context for real project work
                if step == "explore":
                    instruction += " Focus on Phase 1.2 eBay API integration requirements."
                elif step == "write_tests":
                    instruction += " Write tests for eBay API connection, data fetching, and integration with existing Goodwill scraper."
                elif step == "implement":
                    instruction += " Implement eBay API integration for sold listings comparison with Goodwill items."
        
        return instruction
    
    def process_workflow_cycle(self):
        """Process one cycle of the autonomous TDD workflow"""
        
        # 0. Increment session count on first run
        loop_iterations, stop_hook_count = self.get_loop_counters()
        if loop_iterations == 0 and stop_hook_count == 0:
            history = self.load_attempt_history()
            history["session_count"] = history.get("session_count", 0) + 1
            self.save_attempt_history(history)
        
        # 1. Check manual override first
        override_result = self.check_manual_override()
        if override_result:
            # Record manual override as insight about autonomous limitations
            current_step = self.get_current_step()
            self.add_insight(f"Manual override used during {current_step} phase - autonomous system may need enhancement for this scenario")
            return override_result
        
        # 2. Check safety limits
        safety_result = self.check_safety_limits()
        if safety_result:
            return safety_result
        
        # 3. Check automation health
        health = self.check_automation_health()
        if health == "failing":
            # Record health failure as strategy issue
            current_step = self.get_current_step()
            self.record_strategy_failure(
                strategy=f"autonomous_workflow_health",
                reason="Automation health check failed - may indicate stuck or ineffective progress patterns",
                phase=current_step
            )
            self.add_insight("Health failures often indicate need for manual intervention or different approach to current task")
            
            return {
                "decision": "approve",
                "reason": "Automation health failing - stopping for manual review. Check state_reconciliation.py report for details."
            }
        
        # 4. Update counters
        loop_iterations, stop_hook_count = self.get_loop_counters()
        
        # Get current workflow step
        current_step = self.get_current_step()
        next_step = self.get_next_step(current_step)
        
        # If we're starting a new cycle (commit -> explore), increment loop counter
        if current_step == "commit" and next_step == "explore":
            loop_iterations += 1
        
        # Increment stop hook counter (will be reset if we complete a cycle)
        stop_hook_count += 1
        
        # Reset stop hook counter if we complete a full cycle  
        if next_step == "explore" and current_step == "commit":
            stop_hook_count = 0
            # Record successful TDD cycle completion
            self.record_strategy_success(
                strategy="complete_tdd_cycle",
                outcome=f"Successfully completed TDD cycle in {loop_iterations + 1} iterations",
                phase="full_cycle"
            )
        
        # Update counters
        self.update_loop_counters(loop_iterations, stop_hook_count)
        
        # 5. Update workflow state
        self.set_current_step(next_step)
        
        # 6. Read project documentation for context
        project_docs = self.read_project_docs()
        
        # 7. Generate instruction with historical context
        instruction = self.generate_instruction(next_step, project_docs)
        
        # 8. Add historical context to avoid repeated failures
        historical_context = self.get_historical_context(next_step)
        if historical_context:
            instruction += historical_context
        
        # 9. Add context about progress and safety
        context = f"\\n\\n[Autonomous TDD - Cycle {loop_iterations + 1}/{self.MAX_LOOP_ITERATIONS}, Step: {next_step}, Health: {health}]"
        
        return {
            "decision": "block",
            "reason": instruction + context
        }

def main():
    """Main entry point for the autonomous TDD hook"""
    try:
        hook = AutonomousTDDHook()
        result = hook.process_workflow_cycle()
        print(json.dumps(result))
    except Exception as e:
        # Fail safely - always allow stopping rather than crash
        error_result = {
            "decision": "approve",
            "reason": f"Autonomous hook error: {e}. Stopping for safety."
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()