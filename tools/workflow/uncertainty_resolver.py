#!/usr/bin/env python3
"""
Detect and resolve workflow uncertainties and loops.
Usage: python3 tools/workflow/uncertainty_resolver.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

class UncertaintyResolver:
    def __init__(self):
        self.state_file = Path(".claude/workflow_state.json")
        self.history_file = Path(".claude/workflow_history.json")
        self.uncertainties_file = Path("investigations/automated_workflow_planning/uncertainties_to_resolve.md")
        self.resolutions_file = Path(".claude/uncertainty_resolutions.json")
        
        # Loop detection parameters
        self.MAX_ITERATIONS = 7
        self.LOOP_DETECTION_WINDOW = 5  # Check last N commands
        self.ERROR_REPEAT_THRESHOLD = 3  # Same error N times = loop
        
    def load_history(self):
        """Load workflow history"""
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text())
            except:
                pass
        return []
    
    def save_history(self, entry):
        """Add entry to workflow history"""
        history = self.load_history()
        history.append(entry)
        
        # Keep last 50 entries
        if len(history) > 50:
            history = history[-50:]
        
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(history, indent=2))
    
    def detect_loops(self):
        """Detect various loop patterns"""
        history = self.load_history()
        
        if len(history) < 2:
            return None, "Not enough history"
        
        # Pattern 1: Same command repeating
        recent_commands = [h.get("command") for h in history[-self.LOOP_DETECTION_WINDOW:]]
        if recent_commands and all(c == recent_commands[0] for c in recent_commands):
            return "command_loop", f"Command '{recent_commands[0]}' repeated {len(recent_commands)} times"
        
        # Pattern 2: Alternating between two commands
        if len(recent_commands) >= 4:
            if (recent_commands[-1] == recent_commands[-3] and 
                recent_commands[-2] == recent_commands[-4]):
                return "alternating_loop", f"Alternating between '{recent_commands[-1]}' and '{recent_commands[-2]}'"
        
        # Pattern 3: Same error repeating
        recent_errors = []
        for h in history[-self.LOOP_DETECTION_WINDOW:]:
            if h.get("error"):
                # Create hash of error to detect duplicates
                error_hash = hashlib.md5(h["error"].encode()).hexdigest()[:8]
                recent_errors.append(error_hash)
        
        if len(recent_errors) >= self.ERROR_REPEAT_THRESHOLD:
            # Check if same error hash appears multiple times
            from collections import Counter
            error_counts = Counter(recent_errors)
            most_common = error_counts.most_common(1)
            if most_common and most_common[0][1] >= self.ERROR_REPEAT_THRESHOLD:
                return "error_loop", f"Same error repeated {most_common[0][1]} times"
        
        # Pattern 4: No progress (no new files created)
        if len(history) >= 5:
            recent_files = set()
            for h in history[-5:]:
                if h.get("files_created"):
                    recent_files.update(h["files_created"])
            if not recent_files:
                return "no_progress", "No new files created in last 5 iterations"
        
        # Pattern 5: Iteration limit
        current_state = {}
        if self.state_file.exists():
            try:
                current_state = json.loads(self.state_file.read_text())
            except:
                pass
        
        iteration = current_state.get("iteration", 0)
        if iteration >= self.MAX_ITERATIONS:
            return "iteration_limit", f"Reached maximum iterations ({self.MAX_ITERATIONS})"
        
        return None, "No loops detected"
    
    def identify_uncertainties(self):
        """Identify current uncertainties blocking progress"""
        uncertainties = []
        
        # Check for unresolved errors in CLAUDE.md
        claude_md = Path("CLAUDE.md")
        if claude_md.exists():
            content = claude_md.read_text()
            if "ACTIVE ERRORS" in content and "Status: BLOCKED" in content:
                uncertainties.append({
                    "type": "active_error",
                    "description": "Active errors in CLAUDE.md need resolution",
                    "priority": "critical",
                    "action": "Review and fix errors listed in CLAUDE.md"
                })
        
        # Check for missing evidence
        evidence_file = Path("investigations/current_work/evidence.json")
        if not evidence_file.exists():
            uncertainties.append({
                "type": "missing_evidence",
                "description": "No evidence file for current phase",
                "priority": "major",
                "action": "Create evidence file with required fields"
            })
        
        # Check for broken references (known issue)
        if Path("tools/validate_references.py").exists():
            # We know there are 123 broken references
            uncertainties.append({
                "type": "broken_references",
                "description": "123 broken cross-references in codebase",
                "priority": "major",
                "action": "Run tools/validate_references.py and fix broken references"
            })
        
        # Check for hook configuration issues
        if not Path(".claude/settings.json").exists():
            uncertainties.append({
                "type": "missing_hooks",
                "description": "No hook configuration found",
                "priority": "minor",
                "action": "Hooks not working - using manual workflow"
            })
        
        # Check uncertainties document
        if self.uncertainties_file.exists():
            content = self.uncertainties_file.read_text()
            if "UNRESOLVED" in content:
                # Count unresolved items
                unresolved_count = content.count("UNRESOLVED")
                uncertainties.append({
                    "type": "documented_uncertainties",
                    "description": f"{unresolved_count} documented uncertainties need resolution",
                    "priority": "major",
                    "action": f"Review {self.uncertainties_file}"
                })
        
        return uncertainties
    
    def suggest_resolution(self, loop_type=None, uncertainties=None):
        """Suggest resolution strategy"""
        strategies = []
        
        if loop_type:
            loop_name, loop_desc = loop_type
            
            if loop_name == "command_loop":
                strategies.append({
                    "strategy": "force_progression",
                    "action": "Skip to next command in workflow",
                    "command": "/investigate_uncertainties"
                })
            elif loop_name == "alternating_loop":
                strategies.append({
                    "strategy": "break_alternation",
                    "action": "Jump to different phase",
                    "command": "/doublecheck"
                })
            elif loop_name == "error_loop":
                strategies.append({
                    "strategy": "escalate_error",
                    "action": "Document error and skip",
                    "command": "/document_blocker"
                })
            elif loop_name == "no_progress":
                strategies.append({
                    "strategy": "change_approach",
                    "action": "Try different implementation strategy",
                    "command": "/explore"
                })
            elif loop_name == "iteration_limit":
                strategies.append({
                    "strategy": "force_completion",
                    "action": "Document current state and reset",
                    "command": "/commit"
                })
        
        # Add strategies for uncertainties
        if uncertainties:
            critical = [u for u in uncertainties if u["priority"] == "critical"]
            if critical:
                strategies.insert(0, {
                    "strategy": "resolve_critical",
                    "action": f"Fix critical issue: {critical[0]['description']}",
                    "command": "/resolve_blockers"
                })
        
        return strategies
    
    def record_resolution(self, uncertainty_type, resolution):
        """Record how an uncertainty was resolved"""
        resolutions = []
        if self.resolutions_file.exists():
            try:
                resolutions = json.loads(self.resolutions_file.read_text())
            except:
                pass
        
        resolutions.append({
            "timestamp": datetime.now().isoformat(),
            "type": uncertainty_type,
            "resolution": resolution
        })
        
        # Keep last 20 resolutions
        if len(resolutions) > 20:
            resolutions = resolutions[-20:]
        
        self.resolutions_file.parent.mkdir(parents=True, exist_ok=True)
        self.resolutions_file.write_text(json.dumps(resolutions, indent=2))
    
    def analyze(self):
        """Main analysis function"""
        print("=" * 60)
        print("UNCERTAINTY RESOLVER")
        print("=" * 60)
        
        # Detect loops
        loop_type = self.detect_loops()
        if loop_type[0]:
            print(f"\n🔄 LOOP DETECTED: {loop_type[0]}")
            print(f"   {loop_type[1]}")
        else:
            print(f"\n✅ No loops detected")
        
        # Identify uncertainties
        uncertainties = self.identify_uncertainties()
        if uncertainties:
            print(f"\n⚠️  UNCERTAINTIES FOUND: {len(uncertainties)}")
            for u in uncertainties:
                emoji = {
                    "critical": "🔴",
                    "major": "🟠",
                    "minor": "🟡"
                }.get(u["priority"], "🔵")
                print(f"\n{emoji} {u['type'].upper()}")
                print(f"   {u['description']}")
                print(f"   Action: {u['action']}")
        else:
            print(f"\n✅ No uncertainties identified")
        
        # Suggest resolutions
        strategies = self.suggest_resolution(loop_type if loop_type[0] else None, uncertainties)
        
        if strategies:
            print(f"\n🎯 SUGGESTED RESOLUTIONS:")
            for i, strategy in enumerate(strategies, 1):
                print(f"\n{i}. {strategy['strategy'].upper()}")
                print(f"   {strategy['action']}")
                print(f"   Command: {strategy['command']}")
            
            # Write top recommendation to file
            top_command = strategies[0]["command"]
            command_file = Path(".claude/uncertainty_resolution.txt")
            command_file.parent.mkdir(parents=True, exist_ok=True)
            command_file.write_text(top_command)
            print(f"\n✅ Top recommendation saved to: {command_file}")
        else:
            print(f"\n✅ No specific resolutions needed - continue workflow")
        
        print("\n" + "=" * 60)
        
        # Return exit code based on severity
        if loop_type[0] or any(u["priority"] == "critical" for u in uncertainties):
            return 2  # Critical
        elif uncertainties:
            return 1  # Warning
        return 0  # OK

def main():
    """Main entry point"""
    resolver = UncertaintyResolver()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uncertainty Resolver - Detect and resolve workflow issues")
            print("\nUsage:")
            print("  python3 uncertainty_resolver.py           # Analyze current state")
            print("  python3 uncertainty_resolver.py --record  # Record a resolution")
            sys.exit(0)
        elif sys.argv[1] == "--record":
            # Interactive resolution recording
            uncertainty_type = input("Uncertainty type: ")
            resolution = input("How was it resolved: ")
            resolver.record_resolution(uncertainty_type, resolution)
            print("✅ Resolution recorded")
            sys.exit(0)
    
    # Run analysis
    exit_code = resolver.analyze()
    
    # Also update history with current analysis
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "command": "uncertainty_analysis",
        "loops_detected": resolver.detect_loops()[0] is not None,
        "uncertainties_count": len(resolver.identify_uncertainties())
    }
    resolver.save_history(history_entry)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()