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
import hashlib
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
        self.test_integrity_file = self.claude_dir / 'test_integrity.json'
        
        # Safety limits
        self.MAX_LOOP_ITERATIONS = 7
        self.MAX_STOP_HOOK_COUNT = 3
        self.MAX_CONTINUATION_COUNT = 20  # New: limit total continuations per session
        
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
        """Get current loop iteration, stop hook counts, and continuation count"""
        counter_file = self.claude_dir / 'loop_counters.json'
        
        if counter_file.exists():
            try:
                with open(counter_file) as f:
                    data = json.load(f)
                return (data.get('loop_iterations', 0), 
                       data.get('stop_hook_count', 0),
                       data.get('continuation_count', 0))
            except:
                pass
        
        return 0, 0, 0
    
    def update_loop_counters(self, loop_iterations, stop_hook_count, test_failure_count=None, continuation_count=None):
        """Update loop counters including test failures and continuations"""
        counter_file = self.claude_dir / 'loop_counters.json'
        
        # Load existing data to preserve values if not specified
        existing_data = {}
        if counter_file.exists():
            try:
                with open(counter_file) as f:
                    existing_data = json.load(f)
            except:
                pass
        
        data = {
            'loop_iterations': loop_iterations,
            'stop_hook_count': stop_hook_count,
            'continuation_count': continuation_count if continuation_count is not None else existing_data.get('continuation_count', 0),
            'test_failure_count': test_failure_count if test_failure_count is not None else existing_data.get('test_failure_count', 0),
            'last_updated': datetime.now().isoformat()
        }
        
        with open(counter_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def increment_test_failure_count(self):
        """Increment test failure counter"""
        current_count = self.get_recent_failure_count()
        loop_iterations, stop_hook_count, continuation_count = self.get_loop_counters()
        self.update_loop_counters(loop_iterations, stop_hook_count, current_count + 1, continuation_count)
    
    def reset_test_failure_count(self):
        """Reset test failure counter (when tests pass)"""
        loop_iterations, stop_hook_count, continuation_count = self.get_loop_counters()
        self.update_loop_counters(loop_iterations, stop_hook_count, 0, continuation_count)
    
    def increment_continuation_count(self):
        """Increment continuation counter each time we trigger autonomous continuation"""
        loop_iterations, stop_hook_count, continuation_count = self.get_loop_counters()
        self.update_loop_counters(loop_iterations, stop_hook_count, None, continuation_count + 1)
        return continuation_count + 1
    
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
    
    def is_project_complete(self):
        """🧠 LLM DECISION: Check if project work is actually complete"""
        # Read CLAUDE.md to understand current tasks and completion criteria
        project_docs = self.read_project_docs()
        
        if 'claude_md' not in project_docs:
            return {
                "complete": False,
                "reason": "No CLAUDE.md found - cannot determine completion status",
                "confidence": "low"
            }
        
        claude_content = project_docs['claude_md'].lower()
        
        # Simple heuristic checks for project completion indicators
        completion_indicators = [
            "project complete",
            "all phases complete", 
            "implementation finished",
            "ready for deployment",
            "all tasks completed",
            "mvp complete"
        ]
        
        blocking_indicators = [
            "current task",
            "next steps",
            "todo",
            "in progress", 
            "needs implementation",
            "🔄",
            "pending",
            "blocked"
        ]
        
        has_completion_signals = any(indicator in claude_content for indicator in completion_indicators)
        has_blocking_signals = any(indicator in claude_content for indicator in blocking_indicators)
        
        # Check test status as additional completion indicator
        test_results = self.run_tests_check()
        tests_passing = test_results["status"] == "passing"
        
        if has_completion_signals and not has_blocking_signals and tests_passing:
            return {
                "complete": True,
                "reason": "Project completion indicators found, no blocking tasks, tests passing",
                "confidence": "high"
            }
        elif has_blocking_signals:
            return {
                "complete": False,
                "reason": "Active tasks or blockers detected in CLAUDE.md",
                "confidence": "high"
            }
        elif not tests_passing:
            return {
                "complete": False,
                "reason": "Tests failing - implementation not complete",
                "confidence": "high"
            }
        else:
            return {
                "complete": False,
                "reason": "Unclear completion status - continue to be safe",
                "confidence": "low"
            }
    
    def check_safety_limits(self):
        """Check if safety limits have been exceeded"""
        loop_iterations, stop_hook_count, continuation_count = self.get_loop_counters()
        
        # Check continuation count limit (new primary safety mechanism)
        if continuation_count >= self.MAX_CONTINUATION_COUNT:
            self.record_strategy_failure(
                strategy="autonomous_continuation_completion",
                reason=f"Could not complete work within {continuation_count} autonomous continuations",
                phase="autonomous_mode"
            )
            self.add_insight(f"Work requiring more than {self.MAX_CONTINUATION_COUNT} continuations may need manual intervention or task breakdown")
            
            return {
                "decision": "approve",
                "reason": f"🛑 CONTINUATION LIMIT REACHED: {continuation_count}/{self.MAX_CONTINUATION_COUNT} autonomous continuations completed. Manual review required to prevent infinite loops."
            }
        
        # Check stop hook limit (secondary safety mechanism)
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
    
    def run_tests_check(self):
        """🤖 PROGRAMMATIC: Run pytest and get return code"""
        try:
            # Look for common test patterns
            test_paths = []
            for test_dir in ['tests/', 'test/', 'src/tests/', 'src/test/']:
                test_path = self.project_root / test_dir
                if test_path.exists():
                    test_paths.append(str(test_path))
            
            if not test_paths:
                return {"status": "no_tests", "returncode": -1, "output": "No test directories found"}
            
            # Run pytest with minimal output for decision making
            cmd = ['python', '-m', 'pytest', '--tb=short', '-q'] + test_paths
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            return {
                "status": "passing" if result.returncode == 0 else "failing",
                "returncode": result.returncode,
                "output": result.stdout + result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "returncode": -1, "output": "Tests timed out after 60 seconds"}
        except Exception as e:
            return {"status": "error", "returncode": -1, "output": f"Test execution error: {e}"}
    
    def check_git_changes(self):
        """🤖 PROGRAMMATIC: Check for git changes since last commit"""
        try:
            # Check for unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            unstaged = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Check for staged changes
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            staged = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Check for untracked files
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--exclude-standard'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            untracked = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "has_changes": bool(unstaged or staged or untracked),
                "unstaged": [f for f in unstaged if f],
                "staged": [f for f in staged if f],
                "untracked": [f for f in untracked if f]
            }
            
        except Exception as e:
            return {"has_changes": True, "error": f"Git check error: {e}"}
    
    def analyze_progress_quality(self, git_changes, test_results):
        """🧠 LLM DECISION: Analyze if changes represent real progress vs busywork"""
        # Simplified heuristic analysis (later can be enhanced with LLM)
        
        if not git_changes["has_changes"]:
            return {
                "quality": "stagnation",
                "reason": "No file changes detected",
                "confidence": "high"
            }
        
        # Look for meaningful file changes
        meaningful_files = []
        scaffolding_files = []
        
        all_files = git_changes["unstaged"] + git_changes["staged"] + git_changes["untracked"]
        
        for file in all_files:
            if any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c']):
                meaningful_files.append(file)
            elif any(file.endswith(ext) for ext in ['.md', '.txt', '.json', '.yml', '.yaml']):
                scaffolding_files.append(file)
        
        # Analyze based on file types and test status
        if test_results["status"] == "passing" and meaningful_files:
            return {
                "quality": "real_progress",
                "reason": f"Tests passing with meaningful code changes: {', '.join(meaningful_files[:3])}",
                "confidence": "high"
            }
        elif test_results["status"] == "failing" and meaningful_files:
            return {
                "quality": "implementation_in_progress",
                "reason": f"Active implementation detected: {', '.join(meaningful_files[:3])}, tests failing as expected in TDD",
                "confidence": "medium"
            }
        elif scaffolding_files and not meaningful_files:
            return {
                "quality": "scaffolding",
                "reason": f"Only documentation/config changes: {', '.join(scaffolding_files[:3])}",
                "confidence": "medium"
            }
        else:
            return {
                "quality": "unclear",
                "reason": "Mixed or unclear progress indicators",
                "confidence": "low"
            }
    
    def assess_commit_readiness(self, test_results, progress_analysis):
        """🧠 LLM DECISION: Determine if work is ready for commit"""
        # Simplified heuristic (later can be enhanced with LLM)
        
        if test_results["status"] == "passing" and progress_analysis["quality"] == "real_progress":
            return {
                "ready": True,
                "action": "commit",
                "reason": "Tests passing with meaningful progress - ready to commit"
            }
        elif test_results["status"] == "failing" and progress_analysis["quality"] == "implementation_in_progress":
            return {
                "ready": False,
                "action": "continue_implement",
                "reason": "Implementation in progress - continue until tests pass"
            }
        elif progress_analysis["quality"] == "scaffolding":
            return {
                "ready": False,
                "action": "continue_implement", 
                "reason": "Only scaffolding changes - need actual implementation"
            }
        else:
            return {
                "ready": False,
                "action": "investigate",
                "reason": "Unclear progress state - investigate what needs to be done"
            }
    
    def process_v5_decision_tree(self):
        """V5 Hybrid Intelligence Decision Tree with Anti-Cheating"""
        
        # 🤖 PROGRAMMATIC: Manual Override Check
        override_result = self.check_manual_override()
        if override_result:
            current_step = self.get_current_step()
            self.add_insight(f"Manual override used during {current_step} phase - autonomous system may need enhancement for this scenario")
            return override_result
        
        # 🧠 LLM: Project Completion Check (FIRST - before incrementing counters)
        completion_status = self.is_project_complete()
        if completion_status["complete"]:
            return {
                "decision": "approve",
                "reason": f"✅ PROJECT COMPLETE: {completion_status['reason']} (confidence: {completion_status['confidence']}). No further autonomous continuation needed."
            }
        
        # 🤖 PROGRAMMATIC: Increment continuation count (every time hook runs)
        new_continuation_count = self.increment_continuation_count()
        
        # 🤖 PROGRAMMATIC: Safety Limits Check
        safety_result = self.check_safety_limits()
        if safety_result:
            return safety_result
        
        # 🤖 PROGRAMMATIC: Test Integrity Check (Anti-Cheating)
        integrity_check = self.check_test_integrity()
        if integrity_check["violations"]:
            violation_types = [v["type"] for v in integrity_check["violations"]]
            violation_files = [v["file"] for v in integrity_check["violations"]]
            
            # Record anti-cheating violation
            self.record_strategy_failure(
                strategy="test_integrity_maintained",
                reason=f"Test integrity violated: {', '.join(violation_types)} in {', '.join(violation_files[:3])}{'...' if len(violation_files) > 3 else ''}",
                phase="anti_cheating"
            )
            self.add_insight("Test file modifications detected - violates locked TDD principle")
            
            return {
                "decision": "approve",
                "reason": f"🚫 TEST INTEGRITY VIOLATION: {len(integrity_check['violations'])} violations detected ({', '.join(violation_types)}). Locked TDD requires immutable tests. Manual review required."
            }
        
        # 🤖 PROGRAMMATIC: Test Status Check
        test_results = self.run_tests_check()
        
        if test_results["status"] == "passing":
            # TESTS PASSING PATH
            
            # Reset test failure counter on success
            self.reset_test_failure_count()
            
            # 🤖 PROGRAMMATIC: Git Changes Check
            git_changes = self.check_git_changes()
            
            if git_changes["has_changes"]:
                # 🧠 LLM: Analyze Progress Quality
                progress_analysis = self.analyze_progress_quality(git_changes, test_results)
                
                if progress_analysis["quality"] == "real_progress":
                    # 🧠 LLM: Assess Commit Readiness
                    commit_assessment = self.assess_commit_readiness(test_results, progress_analysis)
                    
                    if commit_assessment["ready"]:
                        return {
                            "decision": "block",
                            "reason": f"✅ COMMIT READY ({new_continuation_count}/{self.MAX_CONTINUATION_COUNT}): {commit_assessment['reason']}. Execute git commit with meaningful message."
                        }
                    else:
                        return {
                            "decision": "block", 
                            "reason": f"🔄 CONTINUE WORK ({new_continuation_count}/{self.MAX_CONTINUATION_COUNT}): {commit_assessment['reason']}. Continue implementation to complete the work."
                        }
                        
                elif progress_analysis["quality"] == "scaffolding":
                    return {
                        "decision": "block",
                        "reason": f"📝 SCAFFOLDING DETECTED ({new_continuation_count}/{self.MAX_CONTINUATION_COUNT}): {progress_analysis['reason']}. Move to actual implementation work."
                    }
                else:
                    return {
                        "decision": "block",
                        "reason": f"🔍 UNCLEAR PROGRESS ({new_continuation_count}/{self.MAX_CONTINUATION_COUNT}): {progress_analysis['reason']}. Investigate current state and next steps."
                    }
            else:
                # No changes - stagnation analysis
                return {
                    "decision": "block",
                    "reason": "⚠️ NO CHANGES DETECTED: Tests passing but no file changes since last commit. Continue with next implementation task."
                }
        
        else:
            # TESTS FAILING PATH
            
            # Increment test failure counter
            self.increment_test_failure_count()
            failure_count = self.get_recent_failure_count()
            
            if failure_count < 3:
                # Analyze failure type
                failure_analysis = self.analyze_test_failures(test_results)
                
                if failure_analysis["type"] == "simple":
                    return {
                        "decision": "block",
                        "reason": f"🔧 SIMPLE ERROR ({failure_count}/3): {failure_analysis['reason']}. Fix and rerun tests."
                    }
                else:
                    return {
                        "decision": "block",
                        "reason": f"🐛 COMPLEX FAILURE ({failure_count}/3): {failure_analysis['reason']}. Debug and fix implementation."
                    }
            else:
                # Repeated failures - record and escalate
                self.record_strategy_failure(
                    strategy="test_failure_resolution",
                    reason=f"3 consecutive test failures: {test_results.get('output', '')[:200]}...",
                    phase="test_debugging"
                )
                self.add_insight("3+ consecutive test failures may indicate fundamental implementation issue requiring manual review")
                
                return {
                    "decision": "approve",
                    "reason": f"🚨 REPEATED FAILURES: {failure_count} consecutive test failures. Escalating for manual review."
                }
    
    def get_recent_failure_count(self):
        """Get count of recent test failures"""
        # Simplified - track in counters file
        counter_file = self.claude_dir / 'loop_counters.json'
        if counter_file.exists():
            try:
                with open(counter_file) as f:
                    data = json.load(f)
                return data.get('test_failure_count', 0)
            except:
                pass
        return 0
    
    def analyze_test_failures(self, test_results):
        """🤖→🧠 HYBRID: Analyze test failure patterns"""
        output = test_results.get("output", "")
        
        # 🤖 PROGRAMMATIC: Check for simple error patterns
        simple_patterns = [
            ("syntax error", "SyntaxError"),
            ("import error", "ImportError"),
            ("module not found", "ModuleNotFoundError"),
            ("file not found", "FileNotFoundError"),
            ("indentation", "IndentationError")
        ]
        
        for pattern_name, pattern in simple_patterns:
            if pattern.lower() in output.lower():
                return {
                    "type": "simple",
                    "reason": f"{pattern_name} detected in test output"
                }
        
        # 🧠 LLM: Complex failure analysis (simplified heuristic for now)
        if "AssertionError" in output:
            return {
                "type": "complex",
                "reason": "Logic error - assertion failures indicate implementation issues"
            }
        elif "TypeError" in output:
            return {
                "type": "complex", 
                "reason": "Type error - may indicate API or interface issues"
            }
        else:
            return {
                "type": "complex",
                "reason": "Unknown test failure pattern - requires investigation"
            }
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def get_test_files(self):
        """Find all test files in the project"""
        test_files = []
        test_patterns = ['test_*.py', '*_test.py', 'tests.py']
        
        # Check common test directories
        test_dirs = ['tests/', 'test/', 'src/tests/', 'src/test/']
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                for pattern in test_patterns:
                    test_files.extend(test_path.rglob(pattern))
        
        # Also check for test files in root
        for pattern in test_patterns:
            test_files.extend(self.project_root.glob(pattern))
        
        return [str(f.relative_to(self.project_root)) for f in test_files]
    
    def initialize_test_integrity(self):
        """Initialize test file integrity tracking"""
        test_files = self.get_test_files()
        integrity_data = {
            "initialized": datetime.now().isoformat(),
            "files": {}
        }
        
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    integrity_data["files"][test_file] = {
                        "hash": file_hash,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
        
        # Save integrity data
        self.claude_dir.mkdir(exist_ok=True)
        with open(self.test_integrity_file, 'w') as f:
            json.dump(integrity_data, f, indent=2)
        
        return integrity_data
    
    def check_test_integrity(self):
        """🤖 PROGRAMMATIC: Check if test files have been modified"""
        # Load existing integrity data
        if not self.test_integrity_file.exists():
            # Initialize on first run
            self.initialize_test_integrity()
            return {"status": "initialized", "violations": []}
        
        try:
            with open(self.test_integrity_file) as f:
                integrity_data = json.load(f)
        except Exception:
            # Reinitialize if corrupted
            self.initialize_test_integrity()
            return {"status": "reinitialized", "violations": []}
        
        violations = []
        current_test_files = self.get_test_files()
        
        # Check existing files for modifications
        for test_file, file_data in integrity_data["files"].items():
            file_path = self.project_root / test_file
            
            if not file_path.exists():
                violations.append({
                    "type": "deleted",
                    "file": test_file,
                    "reason": "Test file was deleted"
                })
                continue
            
            current_hash = self.calculate_file_hash(file_path)
            if current_hash != file_data["hash"]:
                violations.append({
                    "type": "modified",
                    "file": test_file,
                    "reason": "Test file content has been modified"
                })
        
        # Check for new test files
        for test_file in current_test_files:
            if test_file not in integrity_data["files"]:
                violations.append({
                    "type": "added",
                    "file": test_file,
                    "reason": "New test file added"
                })
        
        return {
            "status": "checked",
            "violations": violations,
            "total_files": len(integrity_data["files"]),
            "current_files": len(current_test_files)
        }
    
    def evaluate_plan_modification(self, original_requirements, proposed_changes, context=""):
        """🧠 Fresh Instance Evaluator: Detect cheating in plan modifications"""
        
        # Use Task tool to spawn fresh Claude instance for objective evaluation
        evaluation_prompt = f"""
# PLAN MODIFICATION EVALUATION

## Context
You are a fresh Claude Code instance evaluating whether a plan modification request is legitimate or represents "cheating" (scope reduction/quality compromise).

## Original Requirements
{original_requirements}

## Proposed Changes
{proposed_changes}

## Additional Context
{context}

## Evaluation Criteria

**✅ APPROVE if changes are:**
- Adding necessary technical steps discovered during implementation
- Adding missing prerequisites or dependencies  
- Adding error handling or edge cases
- Clarifying requirements without reducing scope
- Adding integration steps or configuration

**❌ REJECT if changes are:**
- Removing original requirements or functionality
- Lowering quality standards or test coverage
- Simplifying to avoid complex implementation
- Using mock/fake data instead of real implementation
- Postponing difficult parts "for later"
- Reducing scope to make task easier

## Required Response Format
You MUST respond with exactly this JSON format:

```json
{{
  "decision": "APPROVE" | "REJECT",
  "reasoning": "Brief explanation of why this is legitimate addition vs scope reduction",
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "recommendation": "Specific advice for proceeding"
}}
```

Evaluate carefully - this prevents autonomous systems from cheating by reducing scope when tasks become difficult.
"""
        
        return {
            "evaluator_type": "fresh_instance_subagent",
            "prompt": evaluation_prompt,
            "original_requirements": original_requirements,
            "proposed_changes": proposed_changes
        }
    
    def process_workflow_cycle(self):
        """Process one cycle using V5 hybrid intelligence decision tree"""
        
        # Increment session count on first run
        loop_iterations, stop_hook_count, continuation_count = self.get_loop_counters()
        if loop_iterations == 0 and stop_hook_count == 0:
            history = self.load_attempt_history()
            history["session_count"] = history.get("session_count", 0) + 1
            self.save_attempt_history(history)
        
        # Use V5 decision tree
        return self.process_v5_decision_tree()

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