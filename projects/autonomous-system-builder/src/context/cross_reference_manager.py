#!/usr/bin/env python3
"""
Cross-Reference Manager - Foundation Component
Manages file relationships and context expansion for autonomous system

Based on pseudocode from pseudo_src/context/cross_reference_manager.py
"""

import re
import ast
import os
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
    
    Foundation component that provides context loading and relationship discovery
    """
    
    def __init__(self, project_root: str):
        """Initialize cross-reference manager"""
        # Validate inputs
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
        
        # Import JSON utilities
        from ..utils.json_utilities import JSONUtilities
        self.json_utils = JSONUtilities()
        
        # Reference extraction patterns
        self._initialize_reference_patterns()
        
        # In-memory cache for performance
        self._reference_cache: Optional[Dict[str, List[CrossReference]]] = None
        self._context_cache: Optional[Dict[str, FileContextBundle]] = None
    
    def discover_all_cross_references(self, force_refresh: bool = False) -> Dict[str, List[CrossReference]]:
        """Discover all cross-references in the project"""
        try:
            # Check if we can use cached references
            if not force_refresh and self._reference_cache is not None:
                return self._reference_cache
            
            # Get all files to scan
            files_to_scan = self._get_scannable_files()
            
            # Scan files for cross-references
            all_references = {}
            
            for file_path in files_to_scan:
                try:
                    file_refs = self._scan_file_for_references(file_path)
                    if file_refs:
                        rel_path = str(file_path.relative_to(self.project_root))
                        all_references[rel_path] = file_refs
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Warning: Failed to scan {file_path}: {e}")
                    continue
            
            # Cache the results
            self._reference_cache = all_references
            self._save_reference_cache(all_references)
            
            return all_references
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to discover cross-references: {str(e)}")
    
    def get_context_for_task(self, task_files: List[str], max_context_tokens: int = 50000) -> FileContextBundle:
        """Get context bundle for specific task files"""
        if not task_files:
            raise CrossReferenceError("task_files cannot be empty")
        
        # Discover references if not cached
        if self._reference_cache is None:
            self.discover_all_cross_references()
        
        # Collect all related files
        all_related_files = set(task_files)
        direct_references = []
        
        # Find direct references from task files
        for task_file in task_files:
            if task_file in self._reference_cache:
                file_refs = self._reference_cache[task_file]
                direct_references.extend(file_refs)
                # Add target files to related set
                for ref in file_refs:
                    all_related_files.add(ref.target_file)
        
        # Estimate tokens and prioritize files
        prioritized_files = self._prioritize_files_by_relevance(
            list(all_related_files), task_files, max_context_tokens
        )
        
        # Create context bundle
        primary_file = task_files[0] if task_files else ""
        return FileContextBundle(
            target_file=primary_file,
            direct_references=direct_references,
            transitive_references=[],  # Could implement transitive discovery
            content_summary=f"Context for {len(prioritized_files)} files",
            dependencies={'files': prioritized_files},
            estimated_tokens=min(max_context_tokens, len(prioritized_files) * 1000)  # Rough estimate
        )
    
    def _initialize_reference_patterns(self):
        """Initialize regex patterns for finding different types of references"""
        self.patterns = {
            ReferenceType.IMPORTS: [
                r'from\s+([a-zA-Z0-9_.]+)\s+import',  # Python imports
                r'import\s+([a-zA-Z0-9_.]+)',
                r'#include\s*[<"]([^>"]+)[>"]',  # C/C++ includes
            ],
            ReferenceType.RELATES_TO: [
                r'#\s*RELATES_TO:\s*([^\n]+)',  # Comment-based relationships
                r'//\s*RELATES_TO:\s*([^\n]+)',
            ],
            ReferenceType.TRACEABILITY: [
                r'#\s*TRACE:\s*([^\n]+)',
                r'//\s*TRACE:\s*([^\n]+)',
            ],
            ReferenceType.TESTS: [
                r'test[_/]([^/\s]+)',  # Test file references
                r'spec[_/]([^/\s]+)',  # Spec file references
            ],
            ReferenceType.CONFIG: [
                r'config[_/]([^/\s]+)',  # Config file references
                r'\.config|\.env|\.yaml|\.json',  # Config file extensions
            ]
        }
    
    def _get_scannable_files(self) -> List[Path]:
        """Get list of files to scan for cross-references"""
        scannable_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.js', '.ts', '.c', '.cpp', '.h', '.hpp'}
        exclude_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache', 'venv', 'env'}
        
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix.lower() in scannable_extensions:
                    files.append(file_path)
        
        return files
    
    def _scan_file_for_references(self, file_path: Path) -> List[CrossReference]:
        """Scan a single file for cross-references"""
        references = []
        
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            rel_source = str(file_path.relative_to(self.project_root))
            
            # Scan for each reference type
            for ref_type, patterns in self.patterns.items():
                for pattern in patterns:
                    for line_num, line in enumerate(lines, 1):
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            target = match.group(1) if match.groups() else match.group(0)
                            
                            # Clean and validate target
                            target = self._clean_reference_target(target, ref_type)
                            if target:
                                ref = CrossReference(
                                    source_file=rel_source,
                                    target_file=target,
                                    reference_type=ref_type,
                                    context=line.strip(),
                                    line_number=line_num
                                )
                                references.append(ref)
            
            return references
            
        except Exception as e:
            raise CrossReferenceError(f"Failed to scan file {file_path}: {str(e)}")
    
    def _clean_reference_target(self, target: str, ref_type: ReferenceType) -> Optional[str]:
        """Clean and validate reference target"""
        if not target or not target.strip():
            return None
        
        target = target.strip()
        
        # Remove quotes and brackets
        target = target.strip('\'"<>')
        
        # For imports, convert module paths to file paths
        if ref_type == ReferenceType.IMPORTS:
            # Convert python module to file path
            if '.' in target and not target.endswith('.py'):
                target = target.replace('.', '/') + '.py'
        
        # For RELATES_TO, split on commas and clean
        if ref_type == ReferenceType.RELATES_TO:
            # Take first target if multiple
            target = target.split(',')[0].strip()
        
        return target if target else None
    
    def _prioritize_files_by_relevance(self, files: List[str], task_files: List[str], max_tokens: int) -> List[str]:
        """Prioritize files by relevance to task"""
        # Simple prioritization: task files first, then by file type importance
        task_set = set(task_files)
        
        prioritized = []
        
        # Add task files first
        for f in files:
            if f in task_set:
                prioritized.append(f)
        
        # Add remaining files, prioritizing certain types
        remaining = [f for f in files if f not in task_set]
        
        # Sort by file type importance
        def file_priority(file_path: str) -> int:
            if file_path.endswith('.py'):
                return 0  # Highest priority
            elif file_path.endswith('.md'):
                return 1
            elif file_path.endswith('.json'):
                return 2
            else:
                return 3
        
        remaining.sort(key=file_priority)
        prioritized.extend(remaining)
        
        # Limit by estimated tokens (rough)
        estimated_tokens = 0
        result = []
        for file_path in prioritized:
            # Rough estimate: 1000 tokens per file
            if estimated_tokens + 1000 > max_tokens:
                break
            result.append(file_path)
            estimated_tokens += 1000
        
        return result
    
    def _save_reference_cache(self, references: Dict[str, List[CrossReference]]):
        """Save references to cache file"""
        try:
            # Convert to serializable format
            serializable = {}
            for file_path, refs in references.items():
                serializable[file_path] = [ref.to_dict() for ref in refs]
            
            self.json_utils.safe_save_json(self.reference_cache_file, serializable)
        except Exception:
            # Fail silently - caching is not critical
            pass
    
    def _load_reference_cache(self) -> Optional[Dict[str, List[CrossReference]]]:
        """Load references from cache file"""
        try:
            if not self.reference_cache_file.exists():
                return None
            
            data = self.json_utils.safe_load_json(self.reference_cache_file)
            if not data:
                return None
            
            # Convert back to CrossReference objects
            result = {}
            for file_path, refs_data in data.items():
                refs = [CrossReference.from_dict(ref_data) for ref_data in refs_data]
                result[file_path] = refs
            
            return result
        except Exception:
            # If cache is corrupted, return None to force refresh
            return None