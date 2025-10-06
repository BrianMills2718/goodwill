#!/usr/bin/env python3
"""
Autonomous TDD Template Setup Script

This script helps you set up the autonomous TDD system in a new project.
"""

import os
import shutil
import sys
from pathlib import Path
import argparse

def setup_template(target_project_dir, project_name=None):
    """Set up the autonomous TDD template in a target project directory"""
    
    target_path = Path(target_project_dir).resolve()
    template_path = Path(__file__).parent
    
    if not target_path.exists():
        print(f"Error: Target directory {target_path} does not exist")
        return False
    
    print(f"Setting up autonomous TDD template in: {target_path}")
    
    # Create necessary directories
    directories = [
        ".claude/hooks",
        "tools/workflow", 
        "docs/behavior",
        "docs/architecture",
        "docs/development_roadmap"
    ]
    
    for dir_path in directories:
        full_path = target_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Copy template files
    files_to_copy = [
        (".claude/hooks/autonomous_tdd.py", ".claude/hooks/autonomous_tdd.py"),
        (".claude/settings.json", ".claude/settings.json"),
        ("tools/workflow/evidence_validator.py", "tools/workflow/evidence_validator.py"),
        ("tools/workflow/state_reconciliation.py", "tools/workflow/state_reconciliation.py"),
        ("CLAUDE.md", "CLAUDE.md"),
        ("docs/behavior/desired_behavior.md", "docs/behavior/desired_behavior.md"),
        ("docs/architecture/system_overview.md", "docs/architecture/system_overview.md"),
        ("docs/development_roadmap/phases.md", "docs/development_roadmap/phases.md"),
    ]
    
    for src, dst in files_to_copy:
        src_path = template_path / src
        dst_path = target_path / dst
        
        if src_path.exists():
            # Check if destination exists and ask user
            if dst_path.exists():
                response = input(f"File {dst} already exists. Overwrite? (y/n): ")
                if response.lower() != 'y':
                    print(f"Skipped: {dst}")
                    continue
            
            shutil.copy2(src_path, dst_path)
            print(f"Copied: {dst}")
        else:
            print(f"Warning: Template file {src} not found")
    
    # If project name provided, customize CLAUDE.md
    if project_name:
        claude_md_path = target_path / "CLAUDE.md"
        if claude_md_path.exists():
            content = claude_md_path.read_text()
            content = content.replace("[PROJECT NAME]", project_name.upper())
            claude_md_path.write_text(content)
            print(f"Customized CLAUDE.md with project name: {project_name}")
    
    print("\n✅ Autonomous TDD Template Setup Complete!")
    print("\nNext steps:")
    print("1. Customize CLAUDE.md with your project details")
    print("2. Update docs/ files with your project requirements")
    print("3. Start Claude Code in the project directory: claude")
    print("4. Press Escape to activate autonomous TDD mode")
    print("5. Create .claude/workflow_override file to stop autonomous mode")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Set up autonomous TDD template in a project")
    parser.add_argument("target_dir", help="Target project directory")
    parser.add_argument("--project-name", help="Project name for customization")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files without asking")
    
    args = parser.parse_args()
    
    success = setup_template(args.target_dir, args.project_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()