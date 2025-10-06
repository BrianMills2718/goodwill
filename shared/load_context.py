#!/usr/bin/env python3
"""
Context Loading Tool - Load all cross-references and full text for comprehensive file modification awareness

TRACEABILITY:
- Phase Plan: /docs/development_roadmap/phase_1_foundation.md (Section 1.3)
- Architecture: /docs/architecture/system_overview.md (Context Loading System)
- Behavior: /docs/behavior/desired_behavior.md (Evidence-Based Development)

CROSS-REFERENCES:
- Related Files: tools/validate_references.py, tools/inject_error.py
- Tests: tests/unit/test_load_context.py
- Config: None

DEPENDENCIES:
- Imports: os, re, json, ast, sys, pathlib
- Imported By: CLAUDE.md workflow, file modification protocols
- Planning: Enables comprehensive context awareness before modifications
"""

import os
import re
import json
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class ContextLoader:
    """Loads complete context for any file including all cross-references and dependencies"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.context = {}
        
    def load_full_context(self, target_file: str) -> Dict:
        """Load complete context for a target file"""
        target_path = Path(target_file)
        if not target_path.is_absolute():
            target_path = self.project_root / target_file
            
        if not target_path.exists():
            return self._create_error_context(target_file, "File does not exist")
            
        print(f"🔍 Loading complete context for: {target_file}")
        
        context = {
            'target_file': str(target_path.relative_to(self.project_root)),
            'absolute_path': str(target_path),
            'file_type': target_path.suffix,
            'cross_references': self._find_all_cross_references(target_path),
            'dependencies': self._analyze_dependencies(target_path),
            'related_files': self._find_related_files(target_path),
            'full_texts': {}
        }
        
        # Load full text of all referenced files
        all_ref_files = set()
        all_ref_files.update(context['cross_references'].get('behavior_docs', []))
        all_ref_files.update(context['cross_references'].get('architecture_docs', []))
        all_ref_files.update(context['cross_references'].get('phase_plans', []))
        all_ref_files.update(context['cross_references'].get('related_files', []))
        all_ref_files.update(context['dependencies'].get('imports_files', []))
        all_ref_files.update(context['dependencies'].get('imported_by_files', []))
        all_ref_files.update(context['dependencies'].get('config_files', []))
        all_ref_files.update(context['related_files'].get('test_files', []))
        
        # Load full text content
        for ref_file in all_ref_files:
            context['full_texts'][ref_file] = self._load_file_content(ref_file)
            
        return context
    
    def _find_all_cross_references(self, target_path: Path) -> Dict:
        """Find all cross-references for the target file"""
        refs = {
            'behavior_docs': [],
            'architecture_docs': [],
            'phase_plans': [],
            'related_files': [],
            'references_to_target': []
        }
        
        # 1. If target is Python file, extract TRACEABILITY section
        if target_path.suffix == '.py':
            refs.update(self._extract_python_traceability(target_path))
        
        # 2. If target is Markdown file, extract cross-references
        elif target_path.suffix == '.md':
            refs.update(self._extract_markdown_references(target_path))
        
        # 3. Find all files that reference this target file
        refs['references_to_target'] = self._find_references_to_file(target_path)
        
        # 4. Check for companion .ref file
        ref_file = target_path.with_suffix(target_path.suffix + '.ref')
        if ref_file.exists():
            refs.update(self._extract_ref_file_references(ref_file))
            
        return refs
    
    def _extract_python_traceability(self, py_file: Path) -> Dict:
        """Extract cross-references from Python TRACEABILITY section"""
        refs = {'behavior_docs': [], 'architecture_docs': [], 'phase_plans': [], 'related_files': []}
        
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
                refs['behavior_docs'].extend(self._extract_file_paths(traceability_text, 'behavior'))
                refs['architecture_docs'].extend(self._extract_file_paths(traceability_text, 'architecture'))
                refs['phase_plans'].extend(self._extract_file_paths(traceability_text, 'development_roadmap'))
            
            # Extract CROSS-REFERENCES section
            cross_ref_match = re.search(
                r'CROSS-REFERENCES:(.*?)(?=DEPENDENCIES:|"""|\'\'\')', 
                content, 
                re.DOTALL
            )
            
            if cross_ref_match:
                cross_ref_text = cross_ref_match.group(1)
                refs['related_files'].extend(self._extract_file_paths(cross_ref_text, 'src'))
                refs['related_files'].extend(self._extract_file_paths(cross_ref_text, 'tools'))
                
        except Exception as e:
            print(f"⚠️  Could not extract traceability from {py_file}: {e}")
            
        return refs
    
    def _extract_markdown_references(self, md_file: Path) -> Dict:
        """Extract cross-references from Markdown files"""
        refs = {'behavior_docs': [], 'architecture_docs': [], 'phase_plans': [], 'related_files': []}
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find markdown links [text](path)
            md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_path in md_links:
                if self._is_file_reference(link_path):
                    # Resolve relative paths
                    resolved_path = self._resolve_relative_path(md_file, link_path)
                    if resolved_path:
                        self._categorize_reference(resolved_path, refs)
            
            # Find file references in backticks
            file_refs = re.findall(r'`([^`]+\.[a-zA-Z]+)`', content)
            for ref in file_refs:
                if self._is_file_reference(ref):
                    self._categorize_reference(ref, refs)
                    
        except Exception as e:
            print(f"⚠️  Could not extract references from {md_file}: {e}")
            
        return refs
    
    def _extract_ref_file_references(self, ref_file: Path) -> Dict:
        """Extract references from .ref companion file"""
        refs = {'behavior_docs': [], 'architecture_docs': [], 'phase_plans': [], 'related_files': []}
        
        try:
            with open(ref_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract file paths from .ref file
            file_refs = re.findall(r'[/]?[a-zA-Z_][a-zA-Z0-9_/]*\.[a-zA-Z]+', content)
            for ref in file_refs:
                if self._is_file_reference(ref):
                    self._categorize_reference(ref, refs)
                    
        except Exception as e:
            print(f"⚠️  Could not extract references from {ref_file}: {e}")
            
        return refs
    
    def _analyze_dependencies(self, target_path: Path) -> Dict:
        """Analyze planning and runtime dependencies"""
        deps = {
            'planning_deps': {'blocks': [], 'blocked_by': []},
            'runtime_deps': {'imports': [], 'imported_by': [], 'config_files': []},
            'imports_files': [],
            'imported_by_files': [],
            'config_files': []
        }
        
        if target_path.suffix == '.py':
            deps.update(self._analyze_python_dependencies(target_path))
        elif target_path.suffix == '.md':
            deps.update(self._analyze_markdown_dependencies(target_path))
            
        return deps
    
    def _analyze_python_dependencies(self, py_file: Path) -> Dict:
        """Analyze Python file dependencies"""
        deps = {
            'runtime_deps': {'imports': [], 'imported_by': [], 'config_files': []},
            'imports_files': [],
            'imported_by_files': [],
            'config_files': []
        }
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            deps['runtime_deps']['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            deps['runtime_deps']['imports'].append(node.module)
                            
                            # Check if importing from local project files
                            if node.module.startswith(('src.', 'tools.', 'config.')):
                                local_file = self._module_to_file_path(node.module)
                                if local_file:
                                    deps['imports_files'].append(local_file)
                                    
            except SyntaxError:
                print(f"⚠️  Could not parse Python file: {py_file}")
            
            # Find files that import this module
            deps['imported_by_files'] = self._find_files_that_import(py_file)
            
            # Find config file references
            config_patterns = [
                r'config/[^\s\'"]+\.[a-zA-Z]+',
                r'["\'][^"\']*\.json["\']',
                r'["\'][^"\']*\.yaml["\']',
                r'["\'][^"\']*\.yml["\']'
            ]
            
            for pattern in config_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    clean_match = match.strip('\'"')
                    if self.project_root.joinpath(clean_match).exists():
                        deps['config_files'].append(clean_match)
                        
        except Exception as e:
            print(f"⚠️  Could not analyze dependencies for {py_file}: {e}")
            
        return deps
    
    def _analyze_markdown_dependencies(self, md_file: Path) -> Dict:
        """Analyze Markdown file dependencies (phase relationships)"""
        deps = {'planning_deps': {'blocks': [], 'blocked_by': []}}
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for phase dependency patterns
            # "Phase 1 must complete before Phase 2"
            # "Depends on Phase X"
            # "Blocks Phase Y"
            
            phase_patterns = [
                r'(?:depends on|requires|blocked by).*?(phase_\d+[^.\s]*\.md)',
                r'(?:blocks|enables).*?(phase_\d+[^.\s]*\.md)'
            ]
            
            for pattern in phase_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if 'depends on' in pattern or 'blocked by' in pattern:
                        deps['planning_deps']['blocked_by'].append(match)
                    else:
                        deps['planning_deps']['blocks'].append(match)
                        
        except Exception as e:
            print(f"⚠️  Could not analyze markdown dependencies for {md_file}: {e}")
            
        return deps
    
    def _find_related_files(self, target_path: Path) -> Dict:
        """Find related files (tests, tools, etc.)"""
        related = {'test_files': [], 'tool_files': []}
        
        target_name = target_path.stem
        
        # Find test files
        test_patterns = [
            f"test_{target_name}.py",
            f"test_{target_name}_*.py",
            f"{target_name}_test.py"
        ]
        
        test_dirs = ['tests', 'test']
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                for pattern in test_patterns:
                    related['test_files'].extend([str(f.relative_to(self.project_root)) 
                                                for f in test_path.rglob(pattern)])
        
        # Find related tools
        tools_dir = self.project_root / 'tools'
        if tools_dir.exists():
            for tool_file in tools_dir.glob('*.py'):
                if target_name in tool_file.stem or tool_file.stem in target_name:
                    related['tool_files'].append(str(tool_file.relative_to(self.project_root)))
                    
        return related
    
    def _find_references_to_file(self, target_path: Path) -> List[str]:
        """Find all files that reference the target file"""
        references = []
        target_relative = str(target_path.relative_to(self.project_root))
        
        # Search all text files for references to this file
        for file_path in self.project_root.rglob('*'):
            if (file_path.suffix in ['.py', '.md', '.ref'] and 
                file_path != target_path and
                not self._should_skip_file(file_path)):
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for various ways the file might be referenced
                    found_reference = False
                    
                    # 1. Direct path reference (e.g., "src/utilities.py")
                    if target_relative in content:
                        found_reference = True
                    
                    # 2. Filename only (e.g., "utilities.py")  
                    elif target_path.name in content:
                        found_reference = True
                    
                    # 3. Python import style (e.g., "src.utilities")
                    elif file_path.suffix == '.py':
                        # Convert path to import style: src/utilities.py -> src.utilities
                        import_style = target_relative.replace('/', '.').replace('.py', '')
                        if import_style in content:
                            found_reference = True
                    
                    if found_reference:
                        references.append(str(file_path.relative_to(self.project_root)))
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
                    
        return references
    
    def _extract_file_paths(self, text: str, path_type: str) -> List[str]:
        """Extract file paths of a specific type from text"""
        paths = []
        
        # Pattern for different path types
        patterns = {
            'behavior': r'/docs/behavior/[^\s]+\.md|docs/behavior/[^\s]+\.md',
            'architecture': r'/docs/architecture/[^\s]+\.md|docs/architecture/[^\s]+\.md',
            'development_roadmap': r'/docs/development_roadmap/[^\s]+\.md|docs/development_roadmap/[^\s]+\.md',
            'src': r'/src/[^\s]+\.py|src/[^\s]+\.py',
            'tools': r'/tools/[^\s]+\.py|tools/[^\s]+\.py'
        }
        
        if path_type in patterns:
            matches = re.findall(patterns[path_type], text)
            for match in matches:
                clean_path = match.strip().lstrip('/')
                if (self.project_root / clean_path).exists():
                    paths.append(clean_path)
                    
        return paths
    
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
    
    def _categorize_reference(self, ref_path: str, refs: Dict):
        """Categorize a reference path into the appropriate category"""
        clean_path = ref_path.strip().lstrip('/')
        
        if 'docs/behavior/' in clean_path:
            refs['behavior_docs'].append(clean_path)
        elif 'docs/architecture/' in clean_path:
            refs['architecture_docs'].append(clean_path)
        elif 'docs/development_roadmap/' in clean_path:
            refs['phase_plans'].append(clean_path)
        elif clean_path.startswith(('src/', 'tools/', 'config/')):
            refs['related_files'].append(clean_path)
    
    def _is_file_reference(self, path: str) -> bool:
        """Check if a path looks like a file reference"""
        if any(path.startswith(prefix) for prefix in ['http', 'https', '#', 'mailto:']):
            return False
        return '.' in Path(path).name and not path.endswith('/')
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv']
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _module_to_file_path(self, module_name: str) -> Optional[str]:
        """Convert Python module name to file path"""
        file_path = module_name.replace('.', '/') + '.py'
        if (self.project_root / file_path).exists():
            return file_path
        return None
    
    def _find_files_that_import(self, target_file: Path) -> List[str]:
        """Find Python files that import the target file"""
        importing_files = []
        target_module = str(target_file.relative_to(self.project_root)).replace('/', '.').replace('.py', '')
        
        for py_file in self.project_root.rglob('*.py'):
            if py_file == target_file or self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if f'from {target_module}' in content or f'import {target_module}' in content:
                    importing_files.append(str(py_file.relative_to(self.project_root)))
                    
            except (UnicodeDecodeError, PermissionError):
                continue
                
        return importing_files
    
    def _load_file_content(self, file_path: str) -> str:
        """Load full content of a file"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return f"ERROR: File not found - {file_path}"
                
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            return f"ERROR: Could not read {file_path} - {e}"
    
    def _create_error_context(self, target_file: str, error_msg: str) -> Dict:
        """Create error context when target file doesn't exist"""
        return {
            'target_file': target_file,
            'error': error_msg,
            'cross_references': {},
            'dependencies': {},
            'related_files': {},
            'full_texts': {}
        }
    
    def format_context_output(self, context: Dict) -> str:
        """Format context for human-readable output"""
        if 'error' in context:
            return f"❌ ERROR: {context['error']}"
            
        output = []
        output.append("=" * 80)
        output.append(f"FULL CONTEXT FOR: {context['target_file']}")
        output.append("=" * 80)
        output.append("")
        
        # Cross-references section
        output.append("CROSS-REFERENCES:")
        refs = context['cross_references']
        if refs.get('behavior_docs'):
            output.append(f"- Behavior: {', '.join(refs['behavior_docs'])}")
        if refs.get('architecture_docs'):
            output.append(f"- Architecture: {', '.join(refs['architecture_docs'])}")
        if refs.get('phase_plans'):
            output.append(f"- Phase Plans: {', '.join(refs['phase_plans'])}")
        if refs.get('related_files'):
            output.append(f"- Related Files: {', '.join(refs['related_files'])}")
        if refs.get('references_to_target'):
            output.append(f"- References to This File: {', '.join(refs['references_to_target'])}")
        output.append("")
        
        # Dependencies section
        output.append("DEPENDENCIES:")
        deps = context['dependencies']
        if deps.get('runtime_deps', {}).get('imports'):
            output.append(f"- Imports: {', '.join(deps['runtime_deps']['imports'])}")
        if deps.get('imported_by_files'):
            output.append(f"- Imported By: {', '.join(deps['imported_by_files'])}")
        if deps.get('config_files'):
            output.append(f"- Config Files: {', '.join(deps['config_files'])}")
        
        planning = deps.get('planning_deps', {})
        if planning.get('blocks'):
            output.append(f"- Planning: Blocks {', '.join(planning['blocks'])}")
        if planning.get('blocked_by'):
            output.append(f"- Planning: Blocked By {', '.join(planning['blocked_by'])}")
        output.append("")
        
        # Related files section
        related = context['related_files']
        if related.get('test_files'):
            output.append(f"- Test Files: {', '.join(related['test_files'])}")
        if related.get('tool_files'):
            output.append(f"- Tool Files: {', '.join(related['tool_files'])}")
        output.append("")
        
        # Full text of all referenced files
        output.append("=" * 80)
        output.append("FULL TEXT OF ALL REFERENCED FILES")
        output.append("=" * 80)
        output.append("")
        
        for file_path, content in context['full_texts'].items():
            if content and not content.startswith('ERROR:'):
                output.append(f"--- {file_path} ---")
                output.append(content)
                output.append("")
                output.append("-" * 40)
                output.append("")
            elif content.startswith('ERROR:'):
                output.append(f"⚠️  {file_path}: {content}")
                output.append("")
        
        return '\n'.join(output)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python tools/load_context.py <target_file> [project_root]")
        print()
        print("Examples:")
        print("  python tools/load_context.py src/scrapers/goodwill_scraper.py")
        print("  python tools/load_context.py docs/development_roadmap/phase_1_foundation.md")
        sys.exit(1)
    
    target_file = sys.argv[1]
    project_root = sys.argv[2] if len(sys.argv) > 2 else "."
    
    loader = ContextLoader(project_root)
    context = loader.load_full_context(target_file)
    
    # Output formatted context
    print(loader.format_context_output(context))


if __name__ == "__main__":
    main()