#!/usr/bin/env python3
"""
Cross-Reference Validation Tool

TRACEABILITY:
- Phase Plan: /docs/development_roadmap/phase_1_scraping_foundation.md (Section 1.3)
- Architecture: /docs/architecture/system_overview.md (Cross-Reference System)
- Behavior: /docs/behavior/desired_behavior.md (Evidence-Based Development)

CROSS-REFERENCES:
- Related Files: tools/load_context.py, tools/inject_error.py
- Tests: tests/unit/test_validate_references.py
- Config: None

DEPENDENCIES:
- Imports: os, re, json, datetime, pathlib
- Imported By: Git hooks, CLAUDE.md validation workflow
- Planning: Enables cross-reference system integrity
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from typing import List, Dict, Set, Tuple


class ReferenceValidator:
    """Validates all cross-references in the project"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.broken_refs = []
        self.error_log_dir = self.project_root / "logs" / "errors" / "active"
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
        
    def validate_all_references(self) -> List[Dict]:
        """Main validation function - checks all cross-references"""
        print("🔍 Validating cross-references...")
        
        # Validate Python file TRACEABILITY sections
        self._validate_python_references()
        
        # Validate Markdown file cross-references
        self._validate_markdown_references()
        
        # Validate .ref companion files
        self._validate_ref_files()
        
        # Generate error report
        if self.broken_refs:
            self._generate_error_report()
            self._inject_errors_to_claude_md()
            return self.broken_refs
        else:
            print("✅ All cross-references are valid")
            return []
    
    def _validate_python_references(self):
        """Validate TRACEABILITY sections in Python files"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract TRACEABILITY section
                traceability_match = re.search(
                    r'TRACEABILITY:(.*?)(?=CROSS-REFERENCES:|DEPENDENCIES:|"""|\'\'\')', 
                    content, 
                    re.DOTALL
                )
                
                if traceability_match:
                    traceability_text = traceability_match.group(1)
                    self._validate_references_in_text(traceability_text, py_file)
                    
                # Extract CROSS-REFERENCES section
                cross_ref_match = re.search(
                    r'CROSS-REFERENCES:(.*?)(?=DEPENDENCIES:|"""|\'\'\')', 
                    content, 
                    re.DOTALL
                )
                
                if cross_ref_match:
                    cross_ref_text = cross_ref_match.group(1)
                    self._validate_references_in_text(cross_ref_text, py_file)
                    
            except Exception as e:
                self._add_broken_ref(
                    source_file=py_file,
                    target_path="ERROR",
                    line_number=0,
                    error_type="FILE_READ_ERROR",
                    details=f"Could not read file: {e}"
                )
    
    def _validate_markdown_references(self):
        """Validate cross-references in Markdown files"""
        md_files = list(self.project_root.rglob("*.md"))
        
        for md_file in md_files:
            if self._should_skip_file(md_file):
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Find markdown links [text](path)
                    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
                    for link_text, link_path in md_links:
                        if self._is_file_reference(link_path):
                            # Resolve relative paths for markdown links
                            resolved_path = self._resolve_relative_path(md_file, link_path)
                            if resolved_path:
                                self._validate_single_reference(resolved_path, md_file, line_num)
                            else:
                                # If we can't resolve it, validate the original path
                                self._validate_single_reference(link_path, md_file, line_num)
                    
                    # Find direct file references in **Implementation Files:** sections
                    if '`' in line and any(ext in line for ext in ['.py', '.md', '.json']):
                        file_refs = re.findall(r'`([^`]+\.[a-zA-Z]+)`', line)
                        for ref in file_refs:
                            if self._is_file_reference(ref):
                                self._validate_single_reference(ref, md_file, line_num)
                                
            except Exception as e:
                self._add_broken_ref(
                    source_file=md_file,
                    target_path="ERROR",
                    line_number=0,
                    error_type="FILE_READ_ERROR",
                    details=f"Could not read file: {e}"
                )
    
    def _validate_ref_files(self):
        """Validate .ref companion files"""
        ref_files = list(self.project_root.rglob("*.ref"))
        
        for ref_file in ref_files:
            try:
                with open(ref_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._validate_references_in_text(content, ref_file)
                
            except Exception as e:
                self._add_broken_ref(
                    source_file=ref_file,
                    target_path="ERROR", 
                    line_number=0,
                    error_type="FILE_READ_ERROR",
                    details=f"Could not read .ref file: {e}"
                )
    
    def _validate_references_in_text(self, text: str, source_file: Path):
        """Extract and validate file references from text"""
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find file paths that look like references
            # Patterns: /docs/..., docs/..., src/..., tools/..., etc.
            file_patterns = [
                r'/docs/[^\s]+\.md',
                r'docs/[^\s]+\.md', 
                r'/src/[^\s]+\.py',
                r'src/[^\s]+\.py',
                r'/tools/[^\s]+\.py',
                r'tools/[^\s]+\.py',
                r'/config/[^\s]+\.[a-zA-Z]+',
                r'config/[^\s]+\.[a-zA-Z]+',
                r'/tests/[^\s]+\.py',
                r'tests/[^\s]+\.py'
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    self._validate_single_reference(match, source_file, line_num)
    
    def _validate_single_reference(self, ref_path: str, source_file: Path, line_num: int):
        """Validate a single file reference"""
        # Clean up the path
        clean_path = ref_path.strip('`').strip()
        
        # Convert to absolute path
        if clean_path.startswith('/'):
            abs_path = self.project_root / clean_path.lstrip('/')
        else:
            abs_path = self.project_root / clean_path
        
        # Check if file exists
        if not abs_path.exists():
            self._add_broken_ref(
                source_file=source_file,
                target_path=clean_path,
                line_number=line_num,
                error_type="BROKEN_REFERENCE",
                details=f"Referenced file does not exist: {abs_path}"
            )
    
    def _resolve_relative_path(self, base_file: Path, relative_path: str) -> Optional[str]:
        """Resolve relative path from base file to absolute project path"""
        try:
            # If already absolute or starts with project paths, return as-is
            if not relative_path.startswith('../') and not relative_path.startswith('./'):
                return relative_path.lstrip('/')
            
            # Get directory of base file relative to project root
            base_dir = base_file.parent
            
            # Resolve the relative path
            resolved = (base_dir / relative_path).resolve()
            
            # Convert back to relative path from project root
            if resolved.is_relative_to(self.project_root):
                return str(resolved.relative_to(self.project_root))
            else:
                return None
                
        except Exception:
            return None
    
    def _is_file_reference(self, path: str) -> bool:
        """Check if a path looks like a file reference"""
        # Skip URLs, anchors, and other non-file references
        if any(path.startswith(prefix) for prefix in ['http', 'https', '#', 'mailto:']):
            return False
        
        # Must have a file extension
        return '.' in Path(path).name and not path.endswith('/')
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during validation"""
        skip_patterns = [
            '.git',
            '__pycache__',
            '.pytest_cache',
            'node_modules',
            '.venv',
            'venv'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _add_broken_ref(self, source_file: Path, target_path: str, line_number: int, 
                       error_type: str, details: str):
        """Add a broken reference to the list"""
        self.broken_refs.append({
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'source_file': str(source_file.relative_to(self.project_root)),
            'target_path': target_path,
            'line_number': line_number,
            'details': details,
            'impact': f"Cross-reference broken in {source_file.name}"
        })
    
    def _generate_error_report(self):
        """Generate detailed error report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        error_file = self.error_log_dir / f"error_{timestamp}.log"
        
        with open(error_file, 'w') as f:
            f.write("=== CROSS-REFERENCE VALIDATION ERRORS ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total Errors: {len(self.broken_refs)}\n\n")
            
            for i, error in enumerate(self.broken_refs, 1):
                f.write(f"=== ERROR {i} ===\n")
                f.write(f"Type: {error['error_type']}\n")
                f.write(f"Source File: {error['source_file']}\n")
                f.write(f"Line Number: {error['line_number']}\n")
                f.write(f"Target Path: {error['target_path']}\n")
                f.write(f"Details: {error['details']}\n")
                f.write(f"Impact: {error['impact']}\n\n")
            
            f.write("=== RESOLUTION STEPS ===\n")
            f.write("1. Check if referenced files were moved or renamed\n")
            f.write("2. Update cross-reference comments to correct paths\n")
            f.write("3. Restore missing files if they were accidentally deleted\n")
            f.write("4. Run this tool again to verify fixes\n")
        
        print(f"📝 Error report saved to: {error_file}")
        return error_file
    
    def _inject_errors_to_claude_md(self):
        """Inject errors into CLAUDE.md (placeholder for now)"""
        claude_md = self.project_root / "CLAUDE.md"
        
        if claude_md.exists():
            print(f"⚠️  {len(self.broken_refs)} broken references found!")
            print("   Run tools/inject_error.py to add these to CLAUDE.md")
        else:
            print("📝 CLAUDE.md not found - errors logged to files only")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    validator = ReferenceValidator(project_root)
    broken_refs = validator.validate_all_references()
    
    if broken_refs:
        print(f"\n❌ Validation failed: {len(broken_refs)} broken references")
        sys.exit(1)
    else:
        print("\n✅ All cross-references are valid")
        sys.exit(0)


if __name__ == "__main__":
    main()