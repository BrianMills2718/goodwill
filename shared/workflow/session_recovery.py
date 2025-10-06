#!/usr/bin/env python3
"""
Recover workflow state after session restart.
Usage: python3 tools/workflow/session_recovery.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

class SessionRecovery:
    def __init__(self):
        self.state_file = Path(".claude/workflow_state.json")
        self.history_file = Path(".claude/workflow_history.json")
        self.recovery_file = Path(".claude/recovery_context.json")
        self.evidence_paths = [
            Path("investigations/current_work/evidence.json"),
            Path("investigations/evidence.json"),
            Path(".claude/evidence.json")
        ]
        
    def detect_incomplete_work(self):
        """Detect if previous session left work incomplete"""
        indicators = []
        
        # Check workflow state
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                last_updated = datetime.fromisoformat(state.get("timestamp", datetime.now().isoformat()))
                time_since = datetime.now() - last_updated
                
                if time_since < timedelta(hours=24):
                    indicators.append({
                        "type": "recent_state",
                        "command": state.get("current_command"),
                        "iteration": state.get("iteration"),
                        "time_ago": str(time_since).split('.')[0]
                    })
                
                # Check if evidence exists for phase
                if not state.get("has_evidence"):
                    indicators.append({
                        "type": "missing_evidence",
                        "phase": state.get("phase"),
                        "description": "Previous phase lacks required evidence"
                    })
            except:
                pass
        
        # Check for partial files (files with TODO markers)
        todo_files = []
        for pattern in ["src/**/*.py", "tests/**/*.py", "tools/**/*.py"]:
            for file_path in Path(".").glob(pattern):
                try:
                    content = file_path.read_text()
                    if "TODO" in content or "FIXME" in content:
                        todo_count = content.count("TODO") + content.count("FIXME")
                        todo_files.append({
                            "file": str(file_path),
                            "count": todo_count
                        })
                except:
                    continue
        
        if todo_files:
            indicators.append({
                "type": "incomplete_code",
                "files": todo_files[:5],  # Top 5
                "total": len(todo_files)
            })
        
        # Check for test failures
        test_results_files = [
            Path(".pytest_cache/lastfailed"),
            Path("test_results.json"),
            Path(".claude/test_results.json")
        ]
        
        for test_file in test_results_files:
            if test_file.exists():
                try:
                    # Check file age
                    file_age = datetime.now() - datetime.fromtimestamp(test_file.stat().st_mtime)
                    if file_age < timedelta(hours=24):
                        indicators.append({
                            "type": "test_failures",
                            "file": str(test_file),
                            "age": str(file_age).split('.')[0]
                        })
                except:
                    pass
        
        # Check for uncommitted changes
        git_status = Path(".git")
        if git_status.exists():
            # This would normally use git commands, but we'll check for indicators
            indicators.append({
                "type": "git_check_needed",
                "description": "Check git status for uncommitted changes"
            })
        
        return indicators
    
    def build_recovery_context(self, indicators):
        """Build context for session recovery"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "recovery_type": "session_restart",
            "indicators": indicators
        }
        
        # Add workflow state
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                context["last_state"] = state
            except:
                pass
        
        # Add recent history
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text())
                context["recent_history"] = history[-5:] if history else []
            except:
                pass
        
        # Add evidence status
        for evidence_path in self.evidence_paths:
            if evidence_path.exists():
                try:
                    evidence = json.loads(evidence_path.read_text())
                    context["evidence_status"] = {
                        "exists": True,
                        "phase": evidence.get("phase"),
                        "complete": evidence.get("status") == "completed"
                    }
                    break
                except:
                    pass
        
        # Build recovery recommendations
        recommendations = []
        
        if indicators:
            # Priority 1: Recent state exists
            recent = [i for i in indicators if i["type"] == "recent_state"]
            if recent:
                cmd = recent[0].get("command", "/explore")
                recommendations.append({
                    "priority": 1,
                    "action": f"Continue from last command: {cmd}",
                    "command": cmd,
                    "reason": f"Session interrupted {recent[0]['time_ago']} ago"
                })
            
            # Priority 2: Missing evidence
            missing = [i for i in indicators if i["type"] == "missing_evidence"]
            if missing:
                recommendations.append({
                    "priority": 2,
                    "action": "Complete evidence for previous phase",
                    "command": "/run_tests",
                    "reason": "Evidence validation required"
                })
            
            # Priority 3: Test failures
            failures = [i for i in indicators if i["type"] == "test_failures"]
            if failures:
                recommendations.append({
                    "priority": 3,
                    "action": "Fix test failures",
                    "command": "/run_tests",
                    "reason": "Recent test failures detected"
                })
            
            # Priority 4: Incomplete code
            incomplete = [i for i in indicators if i["type"] == "incomplete_code"]
            if incomplete:
                recommendations.append({
                    "priority": 4,
                    "action": f"Complete TODOs in {incomplete[0]['total']} files",
                    "command": "/implement",
                    "reason": "Incomplete implementation detected"
                })
        else:
            # No indicators - fresh start
            recommendations.append({
                "priority": 1,
                "action": "Start fresh workflow",
                "command": "/explore",
                "reason": "No incomplete work detected"
            })
        
        context["recommendations"] = sorted(recommendations, key=lambda x: x["priority"])
        
        return context
    
    def save_recovery_context(self, context):
        """Save recovery context to file"""
        self.recovery_file.parent.mkdir(parents=True, exist_ok=True)
        self.recovery_file.write_text(json.dumps(context, indent=2))
    
    def generate_summary(self, context):
        """Generate human-readable recovery summary"""
        lines = []
        lines.append("=" * 60)
        lines.append("SESSION RECOVERY ANALYSIS")
        lines.append("=" * 60)
        
        # Session status
        indicators = context.get("indicators", [])
        if indicators:
            lines.append(f"\n📊 Incomplete Work Detected: {len(indicators)} indicators")
            
            for indicator in indicators:
                if indicator["type"] == "recent_state":
                    lines.append(f"\n🕐 Last Session:")
                    lines.append(f"   - Command: {indicator['command']}")
                    lines.append(f"   - Iteration: {indicator['iteration']}")
                    lines.append(f"   - Time ago: {indicator['time_ago']}")
                elif indicator["type"] == "missing_evidence":
                    lines.append(f"\n⚠️  Missing Evidence:")
                    lines.append(f"   - Phase: {indicator['phase']}")
                    lines.append(f"   - {indicator['description']}")
                elif indicator["type"] == "incomplete_code":
                    lines.append(f"\n📝 Incomplete Code:")
                    lines.append(f"   - Files with TODOs: {indicator['total']}")
                    for file_info in indicator["files"][:3]:
                        lines.append(f"   - {file_info['file']}: {file_info['count']} TODOs")
                elif indicator["type"] == "test_failures":
                    lines.append(f"\n❌ Test Failures:")
                    lines.append(f"   - File: {indicator['file']}")
                    lines.append(f"   - Age: {indicator['age']}")
        else:
            lines.append("\n✅ No incomplete work detected")
        
        # Recommendations
        recommendations = context.get("recommendations", [])
        if recommendations:
            lines.append(f"\n🎯 RECOVERY RECOMMENDATIONS:")
            for rec in recommendations[:3]:  # Top 3
                lines.append(f"\n{rec['priority']}. {rec['action']}")
                lines.append(f"   Command: {rec['command']}")
                lines.append(f"   Reason: {rec['reason']}")
            
            # Save top command
            if recommendations:
                command_file = Path(".claude/recovery_command.txt")
                command_file.parent.mkdir(parents=True, exist_ok=True)
                command_file.write_text(recommendations[0]["command"])
                lines.append(f"\n✅ Top command saved to: {command_file}")
        
        lines.append("\n" + "=" * 60)
        lines.append("Run workflow_orchestrator.py to continue")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def recover(self):
        """Main recovery function"""
        # Detect incomplete work
        indicators = self.detect_incomplete_work()
        
        # Build recovery context
        context = self.build_recovery_context(indicators)
        
        # Save context
        self.save_recovery_context(context)
        
        # Generate and print summary
        summary = self.generate_summary(context)
        print(summary)
        
        # Return status code
        if indicators:
            return 1  # Incomplete work found
        return 0  # Clean state

def main():
    """Main entry point"""
    recovery = SessionRecovery()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Session Recovery - Analyze and recover from interrupted sessions")
            print("\nUsage:")
            print("  python3 session_recovery.py          # Analyze current state")
            print("  python3 session_recovery.py --json   # Output JSON context")
            sys.exit(0)
        elif sys.argv[1] == "--json":
            # Output JSON for integration
            indicators = recovery.detect_incomplete_work()
            context = recovery.build_recovery_context(indicators)
            print(json.dumps(context, indent=2))
            sys.exit(0)
    
    # Run recovery analysis
    exit_code = recovery.recover()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()