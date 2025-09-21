#!/usr/bin/env python3
"""
Standalone workflow orchestrator that can be run manually.
Usage: python3 tools/workflow/workflow_orchestrator.py
"""

import json
from pathlib import Path
import re
from datetime import datetime
import sys

class WorkflowOrchestrator:
    def __init__(self):
        self.claude_md = Path("CLAUDE.md")
        self.state_file = Path(".claude/workflow_state.json")
        self.command_file = Path(".claude/next_command.txt")
        
    def extract_state_from_claude_md(self):
        """Extract workflow state from CLAUDE.md"""
        if not self.claude_md.exists():
            return None
            
        content = self.claude_md.read_text()
        
        # Look for workflow state in JSON block
        patterns = [
            r'## WORKFLOW STATE\s*```json\s*\n(.*?)\n```',
            r'```json\s*\n(\{[^}]*"workflow_state"[^}]*\})\s*\n```',
            r'"workflow_state":\s*(\{[^}]*\})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    if pattern == patterns[2]:  # Third pattern captures just the state object
                        return json.loads(match.group(1))
                    else:
                        data = json.loads(match.group(1))
                        if isinstance(data, dict):
                            return data.get("workflow_state", data)
                except:
                    continue
                    
        return None
    
    def load_state(self):
        """Load state from file or CLAUDE.md"""
        # Try state file first
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        
        # Try CLAUDE.md
        state = self.extract_state_from_claude_md()
        if state:
            return state
            
        # Default state
        return {
            "current_command": None,
            "iteration": 0,
            "phase": "exploration",
            "last_updated": datetime.now().isoformat()
        }
    
    def save_state(self, state):
        """Save state to file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state, indent=2))
    
    def determine_next_command(self, state):
        """Determine next command based on current state"""
        current = state.get("current_command")
        iteration = state.get("iteration", 0)
        
        # Check for loop condition
        if iteration >= 7:
            return "/investigate_uncertainties"
        
        # Check for evidence-based progression
        if current == "/implement":
            if not self.check_evidence():
                return "/write_tests"  # Go back if no evidence
        
        # Standard progression
        progression = {
            None: "/explore",
            "/explore": "/write_tests",
            "/write_tests": "/implement",
            "/implement": "/run_tests",
            "/run_tests": "/doublecheck",
            "/doublecheck": "/commit",
            "/commit": "/explore",  # Start new cycle
            "/investigate_uncertainties": "/resolve_blockers",
            "/resolve_blockers": "/explore"  # Reset after resolution
        }
        
        return progression.get(current, "/explore")
    
    def check_evidence(self):
        """Check if required evidence exists for current phase"""
        evidence_paths = [
            Path("investigations/current_work/evidence.json"),
            Path("investigations/evidence.json"),
            Path(".claude/evidence.json")
        ]
        
        for path in evidence_paths:
            if path.exists():
                try:
                    evidence = json.loads(path.read_text())
                    # Check basic evidence requirements
                    if evidence.get("tests_passed") or evidence.get("test_results"):
                        return True
                except:
                    continue
        
        return False
    
    def analyze_current_context(self):
        """Analyze current work context to provide better recommendations"""
        context = {
            "has_errors": False,
            "has_tests": False,
            "has_implementation": False
        }
        
        # Check for active errors in CLAUDE.md
        if self.claude_md.exists():
            content = self.claude_md.read_text()
            if "ACTIVE ERRORS" in content and "Status: BLOCKED" in content:
                context["has_errors"] = True
        
        # Check for test files
        test_patterns = [
            Path("tests"),
            Path("test"),
            Path("src/tests")
        ]
        for pattern in test_patterns:
            if pattern.exists():
                context["has_tests"] = True
                break
        
        # Check for implementation files
        src_patterns = [
            Path("src"),
            Path("lib"),
            Path("tools/workflow")
        ]
        for pattern in src_patterns:
            if pattern.exists() and any(pattern.iterdir()):
                context["has_implementation"] = True
                break
        
        return context
    
    def get_command_description(self, command):
        """Get description for command"""
        descriptions = {
            "/explore": "Explore codebase and understand requirements",
            "/write_tests": "Write tests for planned implementation",
            "/implement": "Implement the solution",
            "/run_tests": "Run tests and validate implementation",
            "/doublecheck": "Double-check implementation and edge cases",
            "/commit": "Commit completed work",
            "/investigate_uncertainties": "Investigate and resolve uncertainties",
            "/resolve_blockers": "Resolve blocking issues"
        }
        return descriptions.get(command, "Execute workflow command")
    
    def run(self, quiet=False):
        """Main orchestration logic"""
        # Load current state
        state = self.load_state()
        
        if not quiet:
            print("=" * 60)
            print("WORKFLOW ORCHESTRATOR")
            print("=" * 60)
            print(f"\n📊 Current State:")
            print(f"  - Command: {state.get('current_command', 'None')}")
            print(f"  - Iteration: {state.get('iteration', 0)}/7")
            print(f"  - Phase: {state.get('phase', 'unknown')}")
        
        # Analyze context
        context = self.analyze_current_context()
        
        # Determine next command
        if context["has_errors"]:
            next_command = "/resolve_blockers"
            if not quiet:
                print(f"\n⚠️  Active errors detected - prioritizing resolution")
        else:
            next_command = self.determine_next_command(state)
        
        # Check for evidence
        has_evidence = self.check_evidence()
        if not quiet:
            print(f"\n📋 Evidence Status: {'✅ Found' if has_evidence else '❌ Missing'}")
        
        # Update state
        new_state = {
            "current_command": next_command,
            "iteration": state.get("iteration", 0) + 1,
            "timestamp": datetime.now().isoformat(),
            "previous_command": state.get("current_command"),
            "phase": self.get_phase_from_command(next_command),
            "has_evidence": has_evidence
        }
        
        # Save state
        self.save_state(new_state)
        
        # Write command to file
        self.command_file.parent.mkdir(parents=True, exist_ok=True)
        self.command_file.write_text(next_command)
        
        if not quiet:
            print(f"\n🎯 RECOMMENDED NEXT COMMAND: {next_command}")
            print(f"   {self.get_command_description(next_command)}")
            print(f"\n✅ Command saved to: {self.command_file}")
            print(f"   State saved to: {self.state_file}")
            print("\n" + "=" * 60)
            print("Execute the command above in Claude Code")
            print("Then run this tool again for the next recommendation")
            print("=" * 60)
        
        return next_command
    
    def get_phase_from_command(self, command):
        """Map command to phase"""
        phase_map = {
            "/explore": "exploration",
            "/write_tests": "test_writing", 
            "/implement": "implementation",
            "/run_tests": "testing",
            "/doublecheck": "validation",
            "/commit": "completion",
            "/investigate_uncertainties": "investigation",
            "/resolve_blockers": "resolution"
        }
        return phase_map.get(command, "unknown")

def main():
    """Main entry point"""
    # Check for command line arguments
    quiet = "--quiet" in sys.argv or "-q" in sys.argv
    
    orchestrator = WorkflowOrchestrator()
    command = orchestrator.run(quiet=quiet)
    
    if quiet:
        # Just print the command for scripting
        print(command)

if __name__ == "__main__":
    main()