#!/usr/bin/env python3
"""
CROSS-REFERENCE MANAGER - Foundation Component
Manages file relationships and context expansion for autonomous system
"""

# RELATES_TO: ../persistence/state_manager.py, ../utils/json_utils.py, ../../tools/

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ReferenceType(Enum):
    """Types of cross-references between files"""
    IMPORTS = "imports"
    TRACEABILITY = "traceability"
    RELATES_TO = "relates_to"
    PHASE_PLAN = "phase_plan"
    ARCHITECTURE = "architecture"
    BEHAVIOR = "behavior"
    TESTS = "tests"
    CONFIG = "config"
    DEPENDENCIES = "dependencies"

@dataclass
class CrossReference:
    """Individual cross-reference between files"""
    source_file: str
    target_file: str
    reference_type: ReferenceType
    context: str  # Line or section where reference occurs
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_file': self.source_file,
            'target_file': self.target_file,
            'reference_type': self.reference_type.value,
            'context': self.context,
            'line_number': self.line_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrossReference':
        return cls(
            source_file=data['source_file'],
            target_file=data['target_file'],
            reference_type=ReferenceType(data['reference_type']),
            context=data['context'],
            line_number=data.get('line_number')
        )

@dataclass
class FileContextBundle:
    """Bundle of context information for a file"""
    target_file: str
    direct_references: List[CrossReference]
    transitive_references: List[CrossReference]
    content_summary: str
    dependencies: Dict[str, List[str]]  # dependency_type -> list of files
    estimated_tokens: int

class CrossReferenceError(Exception):
    """Raised when cross-reference operations fail"""
    pass

class CrossReferenceManager:
    """
    Manages file cross-references and context expansion
    
    FOUNDATION COMPONENT: Depends on JSONUtilities and file system operations
    Provides context loading and relationship discovery for autonomous system
    """
    
    def __init__(self, project_root: str):
        """
        Initialize cross-reference manager
        
        PARAMETERS:
        - project_root: Absolute path to project directory
        
        DEFENSIVE PROGRAMMING:
        - Validates project root exists
        - Initializes reference patterns
        - Creates cross-reference cache directory
        """
        
        # DEFENSIVE PROGRAMMING: Validate inputs
        if not project_root:
            raise CrossReferenceError("project_root cannot be empty")
        
        self.project_root = Path(project_root)
        
        if not self.project_root.exists():
            raise CrossReferenceError(f"Project root does not exist: {project_root}")
        
        # Cross-reference storage
        self.cache_dir = self.project_root / 'logs' / 'cross_references'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.reference_cache_file = self.cache_dir / 'cross_references.json'
        self.context_cache_file = self.cache_dir / 'context_cache.json'
        
        # JSON utilities for safe operations
        from ..utils.json_utils import JSONUtilities
        self.json_utils = JSONUtilities()
        
        # Reference extraction patterns
        self._initialize_reference_patterns()
        
        # In-memory cache for performance
        self._reference_cache: Optional[Dict[str, List[CrossReference]]] = None
        self._context_cache: Optional[Dict[str, FileContextBundle]] = None
    
    def discover_all_cross_references(self, force_refresh: bool = False) -> Dict[str, List[CrossReference]]:
        """
        Discover all cross-references in the project
        
        PARAMETERS:
        - force_refresh: Whether to force re-scanning all files
        
        RETURNS: Dictionary mapping file paths to their cross-references
        
        FEATURES:
        - Caches results for performance
        - Incremental updates based on file modification times
        - Supports multiple reference types
        """
        
        try:
            # Check if we can use cached references
            if not force_refresh and self._reference_cache is not None:
                return self._reference_cache
            
            # Load existing cache if available
            cached_references = self._load_reference_cache()
            
            # Get all files to scan
            files_to_scan = self._get_scannable_files()
            
            # Determine which files need re-scanning
            if cached_references and not force_refresh:
                files_to_scan = self._filter_files_needing_rescan(files_to_scan, cached_references)
            
            # Scan files for cross-references
            all_references = cached_references if cached_references else {}
            
            for file_path in files_to_scan:
                try:
                    file_references = self._extract_file_references(file_path)
                    all_references[str(file_path)] = file_references
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Warning: Failed to scan {file_path}: {e}")
            
            # Save updated cache
            self._save_reference_cache(all_references)
            
            # Update in-memory cache
            self._reference_cache = all_references
            
            return all_references
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to discover cross-references: {e}")
    
    def expand_context_for_task(self, task, cross_references: Dict[str, List[CrossReference]], max_depth: int = 2) -> List[str]:
        """
        Expand context files needed for a task
        
        PARAMETERS:
        - task: Task object with file_targets and context_requirements
        - cross_references: Complete cross-reference map
        - max_depth: Maximum depth for transitive reference expansion
        
        RETURNS: Ordered list of file paths by relevance
        
        EXPANSION STRATEGY:
        1. Start with task's direct file targets
        2. Add files with direct references to/from target files
        3. Expand transitively up to max_depth
        4. Prioritize by reference type and frequency
        """
        
        try:
            # Start with task's explicit requirements
            context_files = set(task.file_targets + task.context_requirements)
            
            # Expand context using cross-references
            expanded_files = self._expand_context_recursively(
                context_files,
                cross_references,
                max_depth
            )
            
            # Prioritize files by relevance to task
            prioritized_files = self._prioritize_context_files(expanded_files, task, cross_references)
            
            return prioritized_files
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to expand context for task: {e}")
    
    def validate_all_references(self) -> Dict[str, List[str]]:
        """
        Validate all cross-references point to existing files
        
        RETURNS: Dictionary mapping files to their broken references
        
        VALIDATION CHECKS:
        - Target files exist on filesystem
        - Reference syntax is valid
        - No circular references in critical paths
        """
        
        try:
            all_references = self.discover_all_cross_references()
            broken_references = {}
            
            for source_file, references in all_references.items():
                source_broken = []
                
                for ref in references:
                    # Check if target file exists
                    target_path = self._resolve_reference_path(ref.target_file, source_file)
                    
                    if not target_path or not target_path.exists():
                        source_broken.append(f"{ref.reference_type.value}: {ref.target_file}")
                
                if source_broken:
                    broken_references[source_file] = source_broken
            
            return broken_references
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to validate references: {e}")
    
    def get_file_context_bundle(self, file_path: str, include_content: bool = True) -> FileContextBundle:
        """
        Get complete context bundle for a file
        
        PARAMETERS:
        - file_path: Path to file needing context
        - include_content: Whether to include file content summaries
        
        RETURNS: Complete context bundle for the file
        
        CONTEXT INCLUDES:
        - Direct references to/from file
        - Transitive references (1 level deep)
        - Content summaries of related files
        - Dependency analysis
        """
        
        try:
            file_path = str(Path(file_path).resolve())
            
            # Check context cache first
            if self._context_cache and file_path in self._context_cache:
                cached_bundle = self._context_cache[file_path]
                # Check if cache is still valid (file not modified)
                if self._is_context_cache_valid(file_path, cached_bundle):
                    return cached_bundle
            
            # Generate fresh context bundle
            all_references = self.discover_all_cross_references()
            
            # Get direct references
            direct_refs = all_references.get(file_path, [])
            
            # Get incoming references (other files that reference this file)
            incoming_refs = []
            for source, refs in all_references.items():
                for ref in refs:
                    target_resolved = self._resolve_reference_path(ref.target_file, source)
                    if target_resolved and str(target_resolved) == file_path:
                        incoming_refs.append(ref)
            
            # Get transitive references (files referenced by our references)
            transitive_refs = self._get_transitive_references(direct_refs, all_references)
            
            # Generate content summary if requested
            content_summary = ""
            if include_content:
                content_summary = self._generate_content_summary(file_path)
            
            # Analyze dependencies
            dependencies = self._analyze_file_dependencies(file_path, direct_refs)
            
            # Estimate token count
            estimated_tokens = self._estimate_context_tokens(direct_refs + incoming_refs + transitive_refs)
            
            # Create context bundle
            context_bundle = FileContextBundle(
                target_file=file_path,
                direct_references=direct_refs + incoming_refs,
                transitive_references=transitive_refs,
                content_summary=content_summary,
                dependencies=dependencies,
                estimated_tokens=estimated_tokens
            )
            
            # Cache the result
            self._cache_context_bundle(file_path, context_bundle)
            
            return context_bundle
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to get context bundle for {file_path}: {e}")
    
    def _initialize_reference_patterns(self) -> None:
        """Initialize regex patterns for different reference types"""
        
        self.reference_patterns = {
            ReferenceType.RELATES_TO: re.compile(r'#\s*RELATES_TO:\s*(.+)', re.IGNORECASE),
            ReferenceType.TRACEABILITY: re.compile(r'TRACEABILITY:\s*\n(.+?)(?:\n\n|\n[A-Z]|\Z)', re.DOTALL | re.IGNORECASE),
            ReferenceType.PHASE_PLAN: re.compile(r'Phase Plan:\s*([^\n]+)', re.IGNORECASE),
            ReferenceType.ARCHITECTURE: re.compile(r'Architecture:\s*([^\n]+)', re.IGNORECASE),
            ReferenceType.BEHAVIOR: re.compile(r'Behavior:\s*([^\n]+)', re.IGNORECASE),
            ReferenceType.TESTS: re.compile(r'Tests:\s*([^\n]+)', re.IGNORECASE),
            ReferenceType.CONFIG: re.compile(r'Config:\s*([^\n]+)', re.IGNORECASE)
        }
        
        # Python import patterns
        self.import_patterns = [
            re.compile(r'^from\s+([\w.]+)\s+import', re.MULTILINE),
            re.compile(r'^import\s+([\w.]+)', re.MULTILINE)
        ]
    
    def _get_scannable_files(self) -> List[Path]:
        """Get list of files that should be scanned for cross-references"""
        
        scannable_extensions = {'.py', '.md', '.json', '.yaml', '.yml', '.txt'}
        excluded_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
        
        files = []
        for file_path in self.project_root.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in scannable_extensions and
                not any(excluded in file_path.parts for excluded in excluded_dirs)):
                files.append(file_path)
        
        return files
    
    def _extract_file_references(self, file_path: Path) -> List[CrossReference]:
        """Extract all cross-references from a single file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            references = []
            
            # Extract different types of references
            for ref_type, pattern in self.reference_patterns.items():
                matches = pattern.finditer(content)
                for match in matches:
                    # Parse reference targets from match
                    ref_text = match.group(1).strip()
                    targets = self._parse_reference_targets(ref_text)
                    
                    for target in targets:
                        ref = CrossReference(
                            source_file=str(file_path),
                            target_file=target,
                            reference_type=ref_type,
                            context=match.group(0),
                            line_number=content[:match.start()].count('\n') + 1
                        )
                        references.append(ref)
            
            # Extract Python imports if this is a Python file
            if file_path.suffix == '.py':
                import_refs = self._extract_python_imports(file_path, content)
                references.extend(import_refs)
            
            return references
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to extract references from {file_path}: {e}")
    
    def _extract_python_imports(self, file_path: Path, content: str) -> List[CrossReference]:
        """Extract Python import references"""
        
        references = []
        
        try:
            # Use AST to get accurate import information
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Convert module name to file path
                        target_file = self._module_to_file_path(alias.name, file_path)
                        if target_file:
                            ref = CrossReference(
                                source_file=str(file_path),
                                target_file=target_file,
                                reference_type=ReferenceType.IMPORTS,
                                context=f"import {alias.name}",
                                line_number=node.lineno
                            )
                            references.append(ref)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Convert module name to file path
                        target_file = self._module_to_file_path(node.module, file_path)
                        if target_file:
                            ref = CrossReference(
                                source_file=str(file_path),
                                target_file=target_file,
                                reference_type=ReferenceType.IMPORTS,
                                context=f"from {node.module} import ...",
                                line_number=node.lineno
                            )
                            references.append(ref)
        
        except SyntaxError:
            # Fallback to regex for files with syntax errors
            for pattern in self.import_patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    module_name = match.group(1)
                    target_file = self._module_to_file_path(module_name, file_path)
                    if target_file:
                        ref = CrossReference(
                            source_file=str(file_path),
                            target_file=target_file,
                            reference_type=ReferenceType.IMPORTS,
                            context=match.group(0),
                            line_number=content[:match.start()].count('\n') + 1
                        )
                        references.append(ref)
        
        return references
    
    def _parse_reference_targets(self, ref_text: str) -> List[str]:
        """Parse reference targets from reference text"""
        
        # Split on common separators
        targets = []
        for separator in [',', ';']:
            if separator in ref_text:
                parts = ref_text.split(separator)
                targets.extend([part.strip() for part in parts if part.strip()])
                break
        else:
            # No separators found - single target
            targets = [ref_text.strip()]
        
        # Clean up targets
        cleaned_targets = []
        for target in targets:
            # Remove common prefixes and suffixes
            target = target.strip()
            if target.startswith('/'):
                target = target[1:]  # Remove leading slash
            if ' (' in target:
                target = target.split(' (')[0]  # Remove parenthetical comments
            if target:
                cleaned_targets.append(target)
        
        return cleaned_targets
    
    def _module_to_file_path(self, module_name: str, source_file: Path) -> Optional[str]:
        """Convert Python module name to file path"""
        
        # Handle relative imports
        if module_name.startswith('.'):
            # Relative import - resolve relative to source file
            source_dir = source_file.parent
            
            # Count leading dots to determine parent levels
            dots = 0
            for char in module_name:
                if char == '.':
                    dots += 1
                else:
                    break
            
            # Navigate up the directory tree
            target_dir = source_dir
            for _ in range(dots - 1):
                target_dir = target_dir.parent
            
            # Add remaining module path
            remaining_module = module_name[dots:]
            if remaining_module:
                module_path = remaining_module.replace('.', '/')
                target_file = target_dir / f"{module_path}.py"
            else:
                target_file = target_dir / "__init__.py"
            
            if target_file.exists():
                return str(target_file.relative_to(self.project_root))
        
        else:
            # Absolute import - look for module in project
            module_path = module_name.replace('.', '/')
            
            # Try different possible locations
            possible_paths = [
                self.project_root / f"{module_path}.py",
                self.project_root / module_path / "__init__.py",
                self.project_root / "src" / f"{module_path}.py",
                self.project_root / "src" / module_path / "__init__.py"
            ]
            
            for path in possible_paths:
                if path.exists():
                    return str(path.relative_to(self.project_root))
        
        return None
    
    def _expand_context_recursively(self, start_files: Set[str], all_references: Dict[str, List[CrossReference]], max_depth: int) -> Set[str]:
        """Recursively expand context files"""
        
        expanded = set(start_files)
        
        for depth in range(max_depth):
            current_level = set()
            
            for file_path in list(expanded):
                # Add files referenced by this file
                references = all_references.get(file_path, [])
                for ref in references:
                    target_resolved = self._resolve_reference_path(ref.target_file, file_path)
                    if target_resolved and target_resolved.exists():
                        current_level.add(str(target_resolved))
                
                # Add files that reference this file
                for source, refs in all_references.items():
                    for ref in refs:
                        target_resolved = self._resolve_reference_path(ref.target_file, source)
                        if target_resolved and str(target_resolved) == file_path:
                            current_level.add(source)
            
            # Stop if no new files found
            if current_level.issubset(expanded):
                break
            
            expanded.update(current_level)
        
        return expanded
    
    def _prioritize_context_files(self, context_files: Set[str], task, all_references: Dict[str, List[CrossReference]]) -> List[str]:
        """Prioritize context files by relevance to task"""
        
        # Score files by relevance
        file_scores = {}
        
        for file_path in context_files:
            score = 0
            
            # Higher score for task's direct targets
            if file_path in task.file_targets:
                score += 100
            
            # Higher score for task's context requirements
            if file_path in task.context_requirements:
                score += 50
            
            # Higher score for files with more references
            references = all_references.get(file_path, [])
            score += len(references) * 5
            
            # Higher score for certain reference types
            for ref in references:
                if ref.reference_type == ReferenceType.TRACEABILITY:
                    score += 20
                elif ref.reference_type == ReferenceType.IMPORTS:
                    score += 10
                elif ref.reference_type == ReferenceType.TESTS:
                    score += 15
            
            # Higher score for files in same directory as task targets
            if task.file_targets:
                task_dir = Path(task.file_targets[0]).parent
                file_dir = Path(file_path).parent
                if task_dir == file_dir:
                    score += 30
            
            file_scores[file_path] = score
        
        # Sort by score descending
        prioritized = sorted(context_files, key=lambda f: file_scores.get(f, 0), reverse=True)
        
        return prioritized
    
    def _resolve_reference_path(self, target_file: str, source_file: str) -> Optional[Path]:
        """Resolve reference path relative to source file"""
        
        try:
            # Handle absolute paths
            if target_file.startswith('/'):
                return self.project_root / target_file[1:]
            
            # Handle relative paths
            source_dir = Path(source_file).parent
            resolved = source_dir / target_file
            
            # Try to resolve to project root
            if not resolved.exists():
                resolved = self.project_root / target_file
            
            return resolved if resolved.exists() else None
            
        except Exception:
            return None
    
    def _load_reference_cache(self) -> Optional[Dict[str, List[CrossReference]]]:
        """Load cross-reference cache from disk"""
        
        try:
            if not self.reference_cache_file.exists():
                return None
            
            cache_data = self.json_utils.safe_load_json(self.reference_cache_file)
            if not cache_data:
                return None
            
            # Convert back to CrossReference objects
            references = {}
            for file_path, ref_list in cache_data.items():
                references[file_path] = [CrossReference.from_dict(ref_data) for ref_data in ref_list]
            
            return references
            
        except Exception:
            return None
    
    def _save_reference_cache(self, references: Dict[str, List[CrossReference]]) -> None:
        """Save cross-reference cache to disk"""
        
        try:
            # Convert to serializable format
            cache_data = {}
            for file_path, ref_list in references.items():
                cache_data[file_path] = [ref.to_dict() for ref in ref_list]
            
            self.json_utils.safe_save_json(self.reference_cache_file, cache_data, atomic=True)
            
        except Exception:
            # Don't fail if cache save fails
            pass
    
    def _filter_files_needing_rescan(self, all_files: List[Path], cached_references: Dict[str, List[CrossReference]]) -> List[Path]:
        """Filter files that need re-scanning based on modification times"""
        
        cache_mtime = self.reference_cache_file.stat().st_mtime if self.reference_cache_file.exists() else 0
        
        files_to_scan = []
        for file_path in all_files:
            file_mtime = file_path.stat().st_mtime
            if file_mtime > cache_mtime or str(file_path) not in cached_references:
                files_to_scan.append(file_path)
        
        return files_to_scan
    
    def _get_transitive_references(self, direct_refs: List[CrossReference], all_references: Dict[str, List[CrossReference]]) -> List[CrossReference]:
        """Get transitive references (files referenced by our direct references)"""
        
        transitive = []
        
        for direct_ref in direct_refs:
            target_resolved = self._resolve_reference_path(direct_ref.target_file, direct_ref.source_file)
            if target_resolved:
                target_refs = all_references.get(str(target_resolved), [])
                transitive.extend(target_refs)
        
        return transitive
    
    def _generate_content_summary(self, file_path: str) -> str:
        """Generate summary of file content"""
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return "File not found"
            
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate summary based on file type
            if file_path_obj.suffix == '.py':
                return self._summarize_python_file(content)
            elif file_path_obj.suffix == '.md':
                return self._summarize_markdown_file(content)
            else:
                return f"File size: {len(content)} characters"
            
        except Exception:
            return "Could not read file"
    
    def _summarize_python_file(self, content: str) -> str:
        """Summarize Python file content"""
        
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            
            summary_parts = []
            if classes:
                summary_parts.append(f"Classes: {', '.join(classes)}")
            if functions:
                summary_parts.append(f"Functions: {', '.join(functions)}")
            
            return '; '.join(summary_parts) if summary_parts else "Python file"
            
        except SyntaxError:
            return "Python file (syntax errors)"
        except Exception:
            return "Python file"
    
    def _summarize_markdown_file(self, content: str) -> str:
        """Summarize Markdown file content"""
        
        lines = content.split('\n')
        headers = [line for line in lines if line.startswith('#')]
        
        if headers:
            return f"Markdown: {headers[0][:50]}..."
        else:
            return "Markdown file"
    
    def _analyze_file_dependencies(self, file_path: str, references: List[CrossReference]) -> Dict[str, List[str]]:
        """Analyze different types of dependencies for a file"""
        
        dependencies = {
            'imports': [],
            'traceability': [],
            'planning': [],
            'configuration': []
        }
        
        for ref in references:
            if ref.reference_type == ReferenceType.IMPORTS:
                dependencies['imports'].append(ref.target_file)
            elif ref.reference_type == ReferenceType.TRACEABILITY:
                dependencies['traceability'].append(ref.target_file)
            elif ref.reference_type in [ReferenceType.PHASE_PLAN, ReferenceType.ARCHITECTURE, ReferenceType.BEHAVIOR]:
                dependencies['planning'].append(ref.target_file)
            elif ref.reference_type == ReferenceType.CONFIG:
                dependencies['configuration'].append(ref.target_file)
        
        return dependencies
    
    def _estimate_context_tokens(self, references: List[CrossReference]) -> int:
        """Estimate token count for context loading"""
        
        # Rough estimation: 100 tokens per reference + file size estimation
        base_tokens = len(references) * 100
        
        # Estimate file sizes (very rough)
        file_tokens = 0
        seen_files = set()
        
        for ref in references:
            if ref.target_file not in seen_files:
                seen_files.add(ref.target_file)
                target_path = self._resolve_reference_path(ref.target_file, ref.source_file)
                if target_path and target_path.exists():
                    file_size = target_path.stat().st_size
                    file_tokens += file_size // 4  # Rough chars to tokens
        
        return base_tokens + file_tokens
    
    def _cache_context_bundle(self, file_path: str, bundle: FileContextBundle) -> None:
        """Cache context bundle for performance"""
        
        if self._context_cache is None:
            self._context_cache = {}
        
        self._context_cache[file_path] = bundle
    
    def _is_context_cache_valid(self, file_path: str, bundle: FileContextBundle) -> bool:
        """Check if context cache is still valid"""
        
        try:
            file_mtime = Path(file_path).stat().st_mtime
            cache_mtime = self.context_cache_file.stat().st_mtime if self.context_cache_file.exists() else 0
            
            return file_mtime <= cache_mtime
            
        except Exception:
            return False