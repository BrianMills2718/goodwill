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
            None: "/load_phase_plans",  # Start by loading phase
            "/load_phase_plans": "/explore",  # Then explore
            "/load_next_phase": "/explore",  # After loading next phase, explore
            "/explore": "/write_tests",
            "/write_tests": "/implement",
            "/implement": "/run_tests",
            "/run_tests": "/doublecheck",
            "/doublecheck": "/commit",
            "/commit": "/explore",  # Start new cycle
            "/close_phase": "/load_next_phase",  # After closing, load next
            "/investigate_uncertainties": "/resolve_blockers",
            "/resolve_blockers": "/explore"  # Reset after resolution
        }
        
        return progression.get(current, "/load_phase_plans")
    
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
            "/load_phase_plans": "Load current development phase from phases.md",
            "/load_next_phase": "Load next phase after completing current",
            "/explore": "Explore codebase and understand requirements",
            "/write_tests": "Write tests for planned implementation",
            "/implement": "Implement the solution",
            "/run_tests": "Run tests and validate implementation",
            "/doublecheck": "Double-check implementation and edge cases",
            "/commit": "Commit completed work",
            "/close_phase": "Complete current phase and archive evidence",
            "/investigate_uncertainties": "Investigate and resolve uncertainties",
            "/resolve_blockers": "Resolve blocking issues"
        }
        return descriptions.get(command, "Execute workflow command")
    
    def update_claude_md_with_instruction(self, next_command, state):
        """Update CLAUDE.md with clear instruction for Claude to execute"""
        if not self.claude_md.exists():
            return
            
        content = self.claude_md.read_text()
        
        # Determine if this is a continuation command
        continuation_commands = ['/explore', '/write_tests', '/implement', '/run_tests', '/doublecheck', '/commit']
        should_continue = (
            state.get('previous_command') == '/load_phase_plans' or
            state.get('previous_command') == '/load_next_phase' or
            next_command in continuation_commands
        )
        
        # Create instruction block with stronger directive for continuation
        if should_continue:
            instruction = f"""
## 🤖 NEXT ACTION REQUIRED

**EXECUTE NOW:** `{next_command}`
**AUTOMATED CONTINUATION - PROCEED IMMEDIATELY**

**Context:** {self.get_command_description(next_command)}
**Previous:** {state.get('previous_command', 'none')}
**Iteration:** {state.get('iteration', 0) + 1}

Claude, this is an automated workflow continuation. Execute {next_command} immediately to maintain workflow momentum.
"""
        else:
            instruction = f"""
## 🤖 NEXT ACTION REQUIRED

**EXECUTE NOW:** `{next_command}`

**Context:** {self.get_command_description(next_command)}
**Previous:** {state.get('previous_command', 'none')}
**Iteration:** {state.get('iteration', 0) + 1}
"""
        
        # Remove old instruction block if exists
        lines = content.split('\n')
        filtered = []
        skip = False
        for line in lines:
            if '## 🤖 NEXT ACTION REQUIRED' in line:
                skip = True
                continue
            if skip and line.startswith('##') and '🤖' not in line:
                skip = False
            if not skip:
                filtered.append(line)
        
        # Find insertion point (after errors section)
        insert_idx = 0
        for i, line in enumerate(filtered):
            if '## Project Overview' in line:
                insert_idx = i
                break
        
        # Insert instruction
        filtered.insert(insert_idx, instruction)
        
        # Write back
        self.claude_md.write_text('\n'.join(filtered))
    
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
        
        # Determine next command - Check for initialization first
        if state.get('current_command') is None or not state.get('phase_loaded'):
            # Need to load phase first
            next_command = "/load_phase_plans"
            if not quiet:
                print(f"\n📍 Starting workflow - loading phase plans")
        elif state.get('iteration', 0) >= 7 and state.get('current_command') == '/resolve_blockers':
            # We're stuck in a loop, break out
            next_command = "/explore"
            if not quiet:
                print(f"\n🔄 Breaking out of loop - resetting to /explore")
        elif context["has_errors"] and state.get('phase_loaded'):
            # Only resolve blockers if we've already loaded phase
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
            "iteration": state.get("iteration", 0) + 1 if next_command == state.get('current_command') else 1,
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
        
        # UPDATE CLAUDE.MD WITH INSTRUCTION
        self.update_claude_md_with_instruction(next_command, new_state)
        
        if not quiet:
            print(f"\n🎯 RECOMMENDED NEXT COMMAND: {next_command}")
            print(f"   {self.get_command_description(next_command)}")
            print(f"\n✅ Command saved to: {self.command_file}")
            print(f"   State saved to: {self.state_file}")
            print(f"   CLAUDE.md updated with instruction")
            print("\n" + "=" * 60)
            print("Claude will see the instruction in CLAUDE.md")
            print("=" * 60)
        
        return next_command
    
    def get_phase_from_command(self, command):
        """Map command to phase"""
        phase_map = {
            "/load_phase_plans": "initialization",
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
    import json
    
    # Check for command line arguments
    quiet = "--quiet" in sys.argv or "-q" in sys.argv
    
    orchestrator = WorkflowOrchestrator()
    command = orchestrator.run(quiet=quiet)
    
    if quiet:
        # Output JSON for Stop hook to prevent Claude from stopping
        # and provide the next instruction
        state = orchestrator.load_state()
        
        # Determine if we should continue automatically
        auto_continue_commands = [
            '/load_phase_plans', '/load_next_phase', '/explore', 
            '/write_tests', '/implement', '/run_tests', '/doublecheck', '/commit'
        ]
        
        if command in auto_continue_commands or state.get('previous_command') in ['/load_phase_plans', '/load_next_phase']:
            # Block stopping and provide direct instruction for Claude to execute
            # The reason becomes Claude's next prompt - phrase it as a direct action!
            
            # Map commands to direct work instructions - just like forever_mode!
            # Tell Claude WHAT TO DO, not what command to run
            action_map = {
                '/load_phase_plans': "Read docs/development_roadmap/phases.md and identify the current phase (Phase 1: Foundation). Update the CLAUDE.md file with the phase details including the four tasks: Scraping Research, eBay API Setup, Technical Infrastructure, and Keyword Research.",
                
                '/explore': "Explore the codebase for Phase 1 requirements. Read docs/behavior/requirements.md and docs/architecture/technical_design.md. Visit shopgoodwill.com to understand their auction structure. Create the file investigations/phase_1_foundation/exploration_notes.md documenting your findings about how to scrape Goodwill listings.",
                
                '/write_tests': "Write tests for the Goodwill scraper. Create the file tests/test_goodwill_scraper.py with pytest tests that verify: fetching 100+ listings, parsing item details (title, current bid, end time), handling pagination, and rate limiting. The tests should fail initially following TDD principles.",
                
                '/implement': "Implement the Goodwill scraper to pass your tests. Create src/scrapers/goodwill_scraper.py with a GoodwillScraper class. Implement methods to fetch listings, parse HTML with BeautifulSoup, handle pagination, and include rate limiting. Make all tests pass.",
                
                '/run_tests': "Run pytest tests/test_goodwill_scraper.py -v and verify all tests pass. Create investigations/phase_1_foundation/test_results.md with the test output showing all tests passing and any coverage metrics.",
                
                '/doublecheck': "Verify the scraper meets Phase 1 requirements. Test manually that it can scrape 100+ real Goodwill listings. Check error handling and rate limiting work. Create investigations/phase_1_foundation/verification_evidence.md documenting that all success criteria are met.",
                
                '/commit': "Commit your implementation. Use git add to stage all new files, then git commit with message 'feat(scraper): Implement Goodwill scraper with pagination and rate limiting'. Create investigations/phase_1_foundation/commit_evidence.md showing the commit was successful.",
                
                '/load_next_phase': "Read phases.md and identify the next uncompleted phase task. Update CLAUDE.md with the next task details and continue the workflow."
            }
            
            instruction = action_map.get(command, f"Continue working on {command} to progress the workflow.")
            
            output = {
                "decision": "block",
                "reason": instruction
            }
        else:
            # Allow stopping for error resolution or investigation
            output = {
                "decision": "approve",
                "reason": f"Review needed before {command}"
            }
        
        print(json.dumps(output))

if __name__ == "__main__":
    main()