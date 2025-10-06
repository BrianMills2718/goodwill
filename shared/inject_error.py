#!/usr/bin/env python3
"""
Error Injection Tool - Automatically inject errors into CLAUDE.md Active Errors section

TRACEABILITY:
- Phase Plan: /docs/development_roadmap/phase_1_scraping_foundation.md (Section 1.3)
- Architecture: /docs/architecture/system_overview.md (Error Management System)
- Behavior: /docs/behavior/desired_behavior.md (Fail-Fast Principles)

CROSS-REFERENCES:
- Related Files: tools/validate_references.py, tools/load_context.py
- Tests: tests/unit/test_inject_error.py
- Config: None

DEPENDENCIES:
- Imports: os, re, json, datetime, pathlib
- Imported By: Error detection systems, git hooks, validation tools
- Planning: Enables automatic error visibility in CLAUDE.md
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ErrorInjector:
    """Automatically inject errors into CLAUDE.md Active Errors section"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.claude_md = self.project_root / "CLAUDE.md"
        self.error_log_dir = self.project_root / "logs" / "errors" / "active"
        
    def inject_error(self, error_type: str, description: str, **kwargs) -> bool:
        """Inject a new error into CLAUDE.md"""
        error_entry = self._create_error_entry(error_type, description, **kwargs)
        
        # Log the detailed error
        error_log_file = self._log_detailed_error(error_entry)
        
        # Update CLAUDE.md
        success = self._update_claude_md(error_entry, error_log_file)
        
        if success:
            print(f"✅ Error injected into CLAUDE.md: {error_type}")
            return True
        else:
            print(f"❌ Failed to inject error into CLAUDE.md")
            return False
    
    def inject_broken_reference_error(self, source_file: str, target_path: str, 
                                    line_number: int = 0, details: str = "") -> bool:
        """Inject a broken reference error"""
        return self.inject_error(
            error_type="BROKEN_REFERENCE",
            description=f"Reference to {target_path} not found",
            source_file=source_file,
            target_path=target_path,
            line_number=line_number,
            details=details,
            impact=f"Cross-reference broken in {Path(source_file).name}",
            action=f"Update reference to correct path or restore missing file"
        )
    
    def inject_file_move_error(self, old_path: str, new_path: str) -> bool:
        """Inject a file move reference update error"""
        return self.inject_error(
            error_type="REFERENCE_UPDATE_NEEDED",
            description=f"File moved requires reference updates",
            old_path=old_path,
            new_path=new_path,
            impact="Cross-references pointing to old path may be broken",
            action="Update all references from old path to new path",
            details=f"{old_path} → {new_path}"
        )
    
    def inject_import_error(self, source_file: str, import_name: str, error_details: str) -> bool:
        """Inject an import error"""
        return self.inject_error(
            error_type="IMPORT_ERROR",
            description=f"Import failed: {import_name}",
            source_file=source_file,
            import_name=import_name,
            details=error_details,
            impact=f"Code execution blocked in {Path(source_file).name}",
            action="Fix import path or install missing dependency"
        )
    
    def inject_validation_error(self, validator: str, error_details: str) -> bool:
        """Inject a validation error"""
        return self.inject_error(
            error_type="VALIDATION_ERROR",
            description=f"Validation failed: {validator}",
            validator=validator,
            details=error_details,
            impact="Project integrity compromised",
            action="Run validation tool and fix identified issues"
        )
    
    def remove_error(self, error_timestamp: str, resolution: str) -> bool:
        """Remove an error from CLAUDE.md and add to resolved section"""
        if not self.claude_md.exists():
            print("❌ CLAUDE.md not found")
            return False
            
        try:
            with open(self.claude_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find and remove the error entry
            error_pattern = rf"- \*\*{re.escape(error_timestamp)}\*\*.*?(?=- \*\*\d{{4}}-\d{{2}}-\d{{2}}|### Recently Resolved|### Error Resolution|$)"
            
            error_match = re.search(error_pattern, content, re.DOTALL)
            if not error_match:
                print(f"❌ Error with timestamp {error_timestamp} not found")
                return False
            
            error_text = error_match.group(0).strip()
            
            # Remove from active errors
            content = re.sub(error_pattern, "", content, flags=re.DOTALL)
            
            # Add to resolved errors
            resolved_entry = self._create_resolved_entry(error_timestamp, error_text, resolution)
            content = self._add_to_resolved_section(content, resolved_entry)
            
            # Update error status if no more active errors
            if not re.search(r"### Active Errors:\s*\n- \*\*\d{4}-\d{2}-\d{2}", content):
                content = re.sub(
                    r"### Current Error Status: BLOCKED",
                    "### Current Error Status: CLEAR",
                    content
                )
            
            with open(self.claude_md, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Error {error_timestamp} resolved and moved to resolved section")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove error: {e}")
            return False
    
    def _create_error_entry(self, error_type: str, description: str, **kwargs) -> Dict:
        """Create a structured error entry"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        error_entry = {
            'timestamp': timestamp,
            'error_type': error_type,
            'description': description,
            'impact': kwargs.get('impact', 'System functionality affected'),
            'action': kwargs.get('action', 'Investigate and resolve error'),
            'status': kwargs.get('status', 'NEEDS_INVESTIGATION'),
            'details': kwargs.get('details', ''),
            **kwargs
        }
        
        return error_entry
    
    def _log_detailed_error(self, error_entry: Dict) -> Path:
        """Log detailed error information to log file"""
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Use microseconds to ensure unique filenames for rapid successive calls
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        microseconds = now.strftime('%f')[:3]  # First 3 digits of microseconds
        log_file = self.error_log_dir / f"error_{timestamp}_{microseconds}.log"
        
        # Handle any remaining conflicts (unlikely but safe)
        counter = 1
        while log_file.exists():
            log_file = self.error_log_dir / f"error_{timestamp}_{microseconds}_{counter}.log"
            counter += 1
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== ERROR DETAILS ===\n")
            f.write(f"Timestamp: {error_entry['timestamp']}\n")
            f.write(f"Type: {error_entry['error_type']}\n")
            f.write(f"Description: {error_entry['description']}\n")
            f.write(f"Impact: {error_entry['impact']}\n")
            f.write(f"Action Required: {error_entry['action']}\n")
            f.write(f"Status: {error_entry['status']}\n\n")
            
            if error_entry.get('details'):
                f.write(f"=== DETAILED INFORMATION ===\n")
                f.write(f"{error_entry['details']}\n\n")
            
            if error_entry.get('source_file'):
                f.write(f"Source File: {error_entry['source_file']}\n")
            if error_entry.get('line_number'):
                f.write(f"Line Number: {error_entry['line_number']}\n")
            if error_entry.get('target_path'):
                f.write(f"Target Path: {error_entry['target_path']}\n")
            if error_entry.get('old_path') and error_entry.get('new_path'):
                f.write(f"File Move: {error_entry['old_path']} → {error_entry['new_path']}\n")
            
            f.write("\n=== RESOLUTION STEPS ===\n")
            
            if error_entry['error_type'] == 'BROKEN_REFERENCE':
                f.write("1. Check if referenced file was moved or renamed\n")
                f.write("2. Update cross-reference to correct path\n")
                f.write("3. Restore missing file if accidentally deleted\n")
                f.write("4. Run tools/validate_references.py to verify fix\n")
            elif error_entry['error_type'] == 'REFERENCE_UPDATE_NEEDED':
                f.write(f"1. Search for references to: {error_entry.get('old_path', 'old path')}\n")
                f.write(f"2. Replace with: {error_entry.get('new_path', 'new path')}\n")
                f.write("3. Update all cross-reference comments and .ref files\n")
                f.write("4. Run tools/validate_references.py to verify updates\n")
            elif error_entry['error_type'] == 'IMPORT_ERROR':
                f.write("1. Check import path syntax\n")
                f.write("2. Verify imported file exists\n")
                f.write("3. Install missing dependencies if needed\n")
                f.write("4. Test import resolution\n")
            else:
                f.write("1. Analyze the error details above\n")
                f.write("2. Follow the action required\n")
                f.write("3. Test the fix thoroughly\n")
                f.write("4. Remove error from CLAUDE.md when resolved\n")
        
        return log_file
    
    def _update_claude_md(self, error_entry: Dict, log_file: Path) -> bool:
        """Update CLAUDE.md with the new error entry"""
        if not self.claude_md.exists():
            return self._create_claude_md_with_error(error_entry, log_file)
        
        try:
            with open(self.claude_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if error section exists
            if "🚨 ACTIVE ERRORS AND BLOCKERS" not in content:
                content = self._add_error_section(content)
            
            # Update error status to BLOCKED
            content = re.sub(
                r"### Current Error Status: CLEAR",
                "### Current Error Status: BLOCKED",
                content
            )
            
            # Create error entry text
            error_text = self._format_error_entry(error_entry, log_file)
            
            # Insert error into Active Errors section
            active_errors_pattern = r"(### Active Errors:\s*\n)"
            if re.search(active_errors_pattern, content):
                content = re.sub(
                    active_errors_pattern,
                    f"\\1{error_text}\n",
                    content
                )
            else:
                # Add Active Errors section if it doesn't exist
                content = re.sub(
                    r"(### Current Error Status: BLOCKED\s*\n)",
                    f"\\1\n### Active Errors:\n{error_text}\n",
                    content
                )
            
            with open(self.claude_md, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update CLAUDE.md: {e}")
            return False
    
    def _create_claude_md_with_error(self, error_entry: Dict, log_file: Path) -> bool:
        """Create CLAUDE.md with error section if it doesn't exist"""
        error_text = self._format_error_entry(error_entry, log_file)
        
        content = f"""# Current Implementation Plan

## 🚨 ACTIVE ERRORS AND BLOCKERS

### Current Error Status: BLOCKED

### Active Errors:
{error_text}

### Recently Resolved Errors:
(None yet)

### Error Resolution Instructions:
1. Read the detailed log file referenced above
2. Analyze root cause and implement fix
3. Test fix thoroughly with evidence collection
4. Once verified working, remove error entry from this section
5. Move error to "Recently Resolved" with solution summary

## Project Status
(Add current project status here)

## Next Steps
(Add immediate next steps here)
"""
        
        try:
            with open(self.claude_md, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Failed to create CLAUDE.md: {e}")
            return False
    
    def _add_error_section(self, content: str) -> str:
        """Add error section to existing CLAUDE.md"""
        error_section = """
## 🚨 ACTIVE ERRORS AND BLOCKERS

### Current Error Status: CLEAR

### Active Errors:
(None currently)

### Recently Resolved Errors:
(None yet)

### Error Resolution Instructions:
1. Read the detailed log file referenced above
2. Analyze root cause and implement fix
3. Test fix thoroughly with evidence collection
4. Once verified working, remove error entry from this section
5. Move error to "Recently Resolved" with solution summary

"""
        
        # Insert after the first header
        first_header_match = re.search(r'^# .+\n', content, re.MULTILINE)
        if first_header_match:
            insert_pos = first_header_match.end()
            content = content[:insert_pos] + error_section + content[insert_pos:]
        else:
            content = error_section + content
            
        return content
    
    def _format_error_entry(self, error_entry: Dict, log_file: Path) -> str:
        """Format error entry for CLAUDE.md"""
        log_file_rel = log_file.relative_to(self.project_root)
        
        entry = f"- **{error_entry['timestamp']}** {error_entry['error_type']}: {error_entry['description']}\n"
        
        # Include details if present (e.g., file paths for move operations)
        if 'details' in error_entry and error_entry['details']:
            entry += f"  - **Details**: {error_entry['details']}\n"
        
        entry += f"  - **Impact**: {error_entry['impact']}\n"
        entry += f"  - **Log**: `{log_file_rel}`\n"
        entry += f"  - **Action**: {error_entry['action']}\n"
        entry += f"  - **Status**: {error_entry['status']}"
        
        return entry
    
    def _create_resolved_entry(self, timestamp: str, original_error: str, resolution: str) -> str:
        """Create resolved error entry"""
        # Extract error type and description from original error
        match = re.search(r'\*\*.*?\*\* (\w+): (.+)', original_error)
        if match:
            error_type, description = match.groups()
            description = description.split('\n')[0]  # Take only first line
        else:
            error_type = "UNKNOWN"
            description = "Error details not found"
            
        return f"- **{timestamp}** {error_type}: {description} - ✅ RESOLVED\n  - **Resolution**: {resolution}"
    
    def _add_to_resolved_section(self, content: str, resolved_entry: str) -> str:
        """Add entry to resolved errors section"""
        resolved_pattern = r"(### Recently Resolved Errors:\s*\n)(?:\(None yet\)\s*\n)?"
        
        if re.search(resolved_pattern, content):
            content = re.sub(
                resolved_pattern,
                f"\\1{resolved_entry}\n",
                content
            )
        else:
            # Add resolved section if it doesn't exist
            content = re.sub(
                r"(### Active Errors:.*?\n(?:  - .*?\n)*)",
                f"\\1\n### Recently Resolved Errors:\n{resolved_entry}\n",
                content,
                flags=re.DOTALL
            )
            
        return content


def main():
    """Main entry point for command line usage"""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python tools/inject_error.py <error_type> <description> [options]")
        print()
        print("Examples:")
        print("  python tools/inject_error.py BROKEN_REFERENCE 'File not found' --source-file src/test.py --target-path docs/missing.md")
        print("  python tools/inject_error.py FILE_MOVE 'Update references' --old-path old.md --new-path new.md")
        print("  python tools/inject_error.py IMPORT_ERROR 'Cannot import module' --source-file src/main.py --details 'ModuleNotFoundError'")
        sys.exit(1)
    
    error_type = sys.argv[1]
    description = sys.argv[2]
    
    # Parse additional arguments
    kwargs = {}
    i = 3
    while i < len(sys.argv):
        if sys.argv[i].startswith('--'):
            key = sys.argv[i][2:].replace('-', '_')
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                kwargs[key] = sys.argv[i + 1]
                i += 2
            else:
                kwargs[key] = True
                i += 1
        else:
            i += 1
    
    injector = ErrorInjector()
    success = injector.inject_error(error_type, description, **kwargs)
    
    if success:
        print("✅ Error successfully injected into CLAUDE.md")
        sys.exit(0)
    else:
        print("❌ Failed to inject error")
        sys.exit(1)


if __name__ == "__main__":
    main()