#!/usr/bin/env python3
"""
SessionStart hook to load phase information and update CLAUDE.md
"""

import json
import sys
from pathlib import Path
import re
from datetime import datetime

def load_current_phase():
    """Load current phase from phases.md"""
    phases_file = Path("docs/development_roadmap/phases.md")
    if not phases_file.exists():
        return None
        
    content = phases_file.read_text()
    
    # Find first unchecked phase item
    for line in content.split('\n'):
        if '- [ ]' in line and 'Phase' in line:
            # Extract phase name
            match = re.search(r'Phase \d+: ([^(]+)', line)
            if match:
                return match.group(1).strip()
    
    return None

def update_claude_md_with_phase(phase):
    """Update CLAUDE.md with current phase information"""
    claude_md = Path("CLAUDE.md")
    if not claude_md.exists():
        return
        
    content = claude_md.read_text()
    
    # Create phase block
    phase_block = f"""
## 📍 CURRENT DEVELOPMENT PHASE

**Active Phase:** {phase}
**Started:** {datetime.now().isoformat()}

To begin work on this phase, execute `/explore` to analyze requirements and current state.
"""
    
    # Remove old phase block if exists
    lines = content.split('\n')
    filtered = []
    skip = False
    for line in lines:
        if '## 📍 CURRENT DEVELOPMENT PHASE' in line:
            skip = True
            continue
        if skip and line.startswith('##') and '📍' not in line:
            skip = False
        if not skip:
            filtered.append(line)
    
    # Find insertion point (after Project Overview)
    insert_idx = 0
    for i, line in enumerate(filtered):
        if '## Common Commands' in line:
            insert_idx = i
            break
    
    # Insert phase block
    filtered.insert(insert_idx, phase_block)
    
    # Write back
    claude_md.write_text('\n'.join(filtered))

def main():
    """SessionStart hook main"""
    # Read hook input
    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}
    
    source = input_data.get('source', 'unknown')
    
    # Load current phase
    phase = load_current_phase()
    
    if phase:
        # Update CLAUDE.md
        update_claude_md_with_phase(phase)
        
        # Provide context to Claude
        print(f"Session started. Current development phase: {phase}")
        print(f"Review CLAUDE.md for phase details and next actions.")
    else:
        print(f"Session started. No active development phase found.")
    
    sys.exit(0)

if __name__ == "__main__":
    main()