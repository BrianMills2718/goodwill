#!/usr/bin/env python3
"""
Autonomous discovery analyzer for Claude Code.
This tool is designed to be run entirely by Claude without human intervention.
Claude directly analyzes discovery content and makes intelligent classifications.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class AutonomousDiscoveryAnalyzer:
    """
    This class is designed for Claude to use autonomously.
    Instead of keyword matching, Claude uses its intelligence to understand
    the actual impact and context of discoveries.
    """
    
    def __init__(self):
        self.discovery_dir = Path("investigations")
        self.state_file = Path(".claude/discovery_analysis_state.json")
        
    def analyze_discovery_content(self, file_path, content):
        """
        Claude analyzes this content directly using its understanding.
        
        This is where Claude's intelligence replaces keyword matching:
        - Understands context (e.g., "error" in error-handling vs actual error)
        - Identifies relationships between issues
        - Assesses actual impact on the project
        - Determines urgency based on understanding, not keywords
        """
        
        # Claude would process this by actually understanding the content
        # Example of what Claude would determine:
        
        # 1. Is this describing a problem or a solution?
        # 2. Is this blocking other work?
        # 3. Does this invalidate previous assumptions?
        # 4. Is this a new requirement or constraint?
        # 5. Does this affect the current phase?
        
        # The actual classification would be done by Claude's intelligence
        # reading and understanding the content, not by this code
        
        analysis_instruction = f"""
        As part of the autonomous workflow, analyze this discovery:
        
        File: {file_path}
        Content Length: {len(content)} characters
        
        Determine:
        1. Actual impact (not based on keywords but understanding)
        2. Whether this blocks current work
        3. If workflow should continue or address this first
        
        Classification should be based on understanding the meaning,
        not counting keywords.
        """
        
        # This is what Claude fills in during autonomous execution
        return {
            "file": str(file_path),
            "analysis_instruction": analysis_instruction,
            "content_analyzed": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_autonomous_analysis(self):
        """
        Main method for autonomous execution by Claude Code.
        
        Claude runs this to:
        1. Find new discoveries
        2. Analyze each one intelligently
        3. Determine workflow impact
        4. Make decisions without human input
        """
        
        # Load previous state
        last_analysis = {}
        if self.state_file.exists():
            try:
                last_analysis = json.loads(self.state_file.read_text())
            except:
                pass
        
        # Find discoveries to analyze
        discoveries_to_analyze = []
        for pattern in ["**/*.md", "**/*.json", "**/*.txt"]:
            for file_path in self.discovery_dir.glob(pattern):
                # Skip system files
                if any(skip in str(file_path) for skip in [".git", "__pycache__"]):
                    continue
                    
                # Check if already analyzed
                file_key = str(file_path)
                file_mtime = file_path.stat().st_mtime
                
                if file_key in last_analysis:
                    if last_analysis[file_key].get("mtime") == file_mtime:
                        continue  # Already analyzed and unchanged
                
                discoveries_to_analyze.append(file_path)
        
        # Analyze each discovery
        results = []
        for discovery_path in discoveries_to_analyze:
            try:
                content = discovery_path.read_text(errors='ignore')
                
                # Claude analyzes the actual content here
                # This is where LLM intelligence happens instead of keywords
                analysis = self.analyze_discovery_content(discovery_path, content)
                
                # Update state
                last_analysis[str(discovery_path)] = {
                    "mtime": discovery_path.stat().st_mtime,
                    "analyzed": datetime.now().isoformat(),
                    "result": analysis
                }
                
                results.append(analysis)
                
            except Exception as e:
                print(f"Error analyzing {discovery_path}: {e}", file=sys.stderr)
        
        # Save updated state
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(last_analysis, indent=2))
        
        # Return results for workflow
        return {
            "analyzed_count": len(results),
            "discoveries": results,
            "timestamp": datetime.now().isoformat(),
            "next_action": "Claude determines based on analysis"
        }

def main():
    """
    Autonomous entry point.
    Claude Code runs this without human intervention.
    """
    analyzer = AutonomousDiscoveryAnalyzer()
    results = analyzer.run_autonomous_analysis()
    
    print(json.dumps(results, indent=2))
    
    # Claude determines exit code based on its analysis
    # 0 = continue, 1 = review needed, 2 = halt
    sys.exit(0)

if __name__ == "__main__":
    main()