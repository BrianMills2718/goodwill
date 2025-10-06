# Cross-Reference Discovery System - Context System Pseudocode
# Part of autonomous TDD system context management layer

"""
Cross-Reference Discovery System

Discovers and manages bidirectional relationships between files, functions, and concepts
to enable intelligent context loading and navigation for autonomous development.
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import re
import ast
import json
from collections import defaultdict, deque

# === Configuration and Data Classes ===

class ReferenceType(Enum):
    """Types of cross-references"""
    IMPORT = "import"                    # Python imports, require statements
    FUNCTION_CALL = "function_call"      # Function invocations
    CLASS_INHERITANCE = "inheritance"    # Class inheritance relationships
    VARIABLE_USAGE = "variable_usage"    # Variable references
    FILE_INCLUSION = "file_inclusion"    # File includes, markdown links
    DOCUMENTATION_LINK = "doc_link"      # Documentation references
    TEST_COVERAGE = "test_coverage"      # Test to implementation relationships
    CONFIGURATION = "configuration"      # Config file references
    CONCEPTUAL = "conceptual"            # Conceptual relationships

@dataclass
class CrossReference:
    """A cross-reference between two entities"""
    source_file: Path
    target_file: Path
    reference_type: ReferenceType
    source_location: Optional[Tuple[int, int]] = None  # (line, column)
    target_location: Optional[Tuple[int, int]] = None
    source_context: str = ""  # Code/text surrounding the reference
    target_context: str = ""  # Referenced entity context
    confidence: float = 1.0   # Confidence in the reference
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EntityReference:
    """Reference to a specific entity (function, class, variable)"""
    entity_name: str
    entity_type: str  # 'function', 'class', 'variable', 'constant'
    file_path: Path
    location: Tuple[int, int]  # (line, column)
    definition: str  # The actual definition
    signature: Optional[str] = None  # Function/method signature
    docstring: Optional[str] = None  # Documentation
    scope: str = "global"  # 'global', 'class', 'function'

@dataclass
class ReferenceGraph:
    """Graph of all cross-references in the project"""
    cross_references: List[CrossReference] = field(default_factory=list)
    entity_definitions: Dict[str, EntityReference] = field(default_factory=dict)
    file_dependencies: Dict[Path, Set[Path]] = field(default_factory=lambda: defaultdict(set))
    reverse_dependencies: Dict[Path, Set[Path]] = field(default_factory=lambda: defaultdict(set))
    entity_usages: Dict[str, List[CrossReference]] = field(default_factory=lambda: defaultdict(list))

# === Cross-Reference Discovery Engine ===

class CrossReferenceDiscovery:
    """
    Discovers cross-references between files and entities in the project
    
    Implements intelligent cross-reference analysis to support context loading
    and autonomous navigation through complex codebases.
    """
    
    def __init__(self, config: CrossReferenceConfig):
        self.config = config
        self.project_root = Path(config.project_root)
        
        # Discovery engines for different file types
        self.python_analyzer = PythonReferenceAnalyzer()
        self.javascript_analyzer = JavaScriptReferenceAnalyzer()
        self.markdown_analyzer = MarkdownReferenceAnalyzer()
        self.json_analyzer = JSONReferenceAnalyzer()
        
        # Pattern matchers
        self.pattern_matchers = {
            '.py': self.python_analyzer,
            '.js': self.javascript_analyzer,
            '.ts': self.javascript_analyzer,
            '.md': self.markdown_analyzer,
            '.json': self.json_analyzer,
            '.yml': self.json_analyzer,
            '.yaml': self.json_analyzer
        }
        
        # State
        self.reference_graph = ReferenceGraph()
        self.discovery_cache = {}
        self.last_discovery_time = None
    
    def discover_all_references(self) -> ReferenceDiscoveryResult:
        """
        Discover all cross-references in the project
        
        Returns:
            ReferenceDiscoveryResult with complete reference graph
        """
        
        try:
            # Clear previous results
            self.reference_graph = ReferenceGraph()
            
            # Discover all project files
            project_files = self._discover_project_files()
            
            # Phase 1: Discover entity definitions
            definition_results = self._discover_entity_definitions(project_files)
            
            # Phase 2: Discover cross-references
            reference_results = self._discover_cross_references(project_files)
            
            # Phase 3: Build dependency graph
            dependency_results = self._build_dependency_graph()
            
            # Phase 4: Validate and enrich references
            validation_results = self._validate_and_enrich_references()
            
            # Update timestamp
            self.last_discovery_time = datetime.now()
            
            return ReferenceDiscoveryResult(
                success=True,
                reference_graph=self.reference_graph,
                files_analyzed=len(project_files),
                definitions_found=len(self.reference_graph.entity_definitions),
                references_found=len(self.reference_graph.cross_references),
                discovery_time=datetime.now(),
                analysis_results={
                    'definitions': definition_results,
                    'references': reference_results,
                    'dependencies': dependency_results,
                    'validation': validation_results
                }
            )
            
        except Exception as e:
            return ReferenceDiscoveryResult(
                success=False,
                error=f"Reference discovery failed: {str(e)}",
                reference_graph=ReferenceGraph(),
                files_analyzed=0,
                definitions_found=0,
                references_found=0
            )
    
    def _discover_project_files(self) -> List[Path]:
        """Discover all relevant files in the project"""
        
        project_files = []
        
        # Walk project directory
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and self._should_analyze_file(file_path):
                project_files.append(file_path)
        
        return project_files
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed for cross-references"""
        
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            # Exception for common hidden files we want to analyze
            if file_path.name not in ['.gitignore', '.env.example']:
                return False
        
        # Skip binary files
        if file_path.suffix in ['.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe']:
            return False
        
        # Skip large files (> 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return False
        except OSError:
            return False
        
        # Include files with supported extensions
        if file_path.suffix in self.pattern_matchers:
            return True
        
        # Include common config files without extensions
        if file_path.name in ['Dockerfile', 'Makefile', 'requirements.txt', 'setup.cfg']:
            return True
        
        # Include files that look like text
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                # Read first 1KB to check if it's text
                sample = f.read(1024)
                # If it contains mostly printable characters, treat as text
                printable_ratio = sum(1 for c in sample if c.isprintable() or c.isspace()) / len(sample) if sample else 0
                return printable_ratio > 0.8
        except Exception:
            return False
    
    def _discover_entity_definitions(self, project_files: List[Path]) -> EntityDefinitionResult:
        """Discover all entity definitions (functions, classes, variables)"""
        
        definitions_found = 0
        files_processed = 0
        errors = []
        
        for file_path in project_files:
            try:
                # Get appropriate analyzer for file type
                analyzer = self._get_analyzer_for_file(file_path)
                if not analyzer:
                    continue
                
                # Discover entities in file
                file_entities = analyzer.discover_entities(file_path)
                
                # Add entities to graph
                for entity in file_entities:
                    entity_key = f"{entity.file_path}::{entity.entity_name}"
                    self.reference_graph.entity_definitions[entity_key] = entity
                    definitions_found += 1
                
                files_processed += 1
                
            except Exception as e:
                errors.append(f"Error analyzing {file_path}: {str(e)}")
        
        return EntityDefinitionResult(
            definitions_found=definitions_found,
            files_processed=files_processed,
            errors=errors
        )
    
    def _discover_cross_references(self, project_files: List[Path]) -> CrossReferenceResult:
        """Discover cross-references between files and entities"""
        
        references_found = 0
        files_processed = 0
        errors = []
        
        for file_path in project_files:
            try:
                # Get appropriate analyzer for file type
                analyzer = self._get_analyzer_for_file(file_path)
                if not analyzer:
                    continue
                
                # Discover references in file
                file_references = analyzer.discover_references(file_path, self.reference_graph.entity_definitions)
                
                # Add references to graph
                for reference in file_references:
                    self.reference_graph.cross_references.append(reference)
                    
                    # Update entity usage tracking
                    if reference.target_file in self.reference_graph.entity_definitions:
                        entity_key = f"{reference.target_file}::{reference.metadata.get('target_entity', '')}"
                        self.reference_graph.entity_usages[entity_key].append(reference)
                    
                    references_found += 1
                
                files_processed += 1
                
            except Exception as e:
                errors.append(f"Error discovering references in {file_path}: {str(e)}")
        
        return CrossReferenceResult(
            references_found=references_found,
            files_processed=files_processed,
            errors=errors
        )
    
    def _build_dependency_graph(self) -> DependencyGraphResult:
        """Build file dependency graph from cross-references"""
        
        for reference in self.reference_graph.cross_references:
            # Add forward dependency
            self.reference_graph.file_dependencies[reference.source_file].add(reference.target_file)
            
            # Add reverse dependency
            self.reference_graph.reverse_dependencies[reference.target_file].add(reference.source_file)
        
        # Calculate dependency metrics
        total_dependencies = sum(len(deps) for deps in self.reference_graph.file_dependencies.values())
        files_with_dependencies = len([f for f, deps in self.reference_graph.file_dependencies.items() if deps])
        
        # Detect circular dependencies
        circular_dependencies = self._detect_circular_dependencies()
        
        return DependencyGraphResult(
            total_dependencies=total_dependencies,
            files_with_dependencies=files_with_dependencies,
            circular_dependencies=circular_dependencies,
            dependency_graph=dict(self.reference_graph.file_dependencies)
        )
    
    def _detect_circular_dependencies(self) -> List[List[Path]]:
        """Detect circular dependencies in the file dependency graph"""
        
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs_cycle_detection(node: Path, path: List[Path]) -> bool:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                circular_deps.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.reference_graph.file_dependencies.get(node, []):
                if dfs_cycle_detection(neighbor, path + [neighbor]):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for file_path in self.reference_graph.file_dependencies:
            if file_path not in visited:
                dfs_cycle_detection(file_path, [file_path])
        
        return circular_deps
    
    def find_related_files(self, target_file: Path, max_depth: int = 2, max_results: int = 20) -> RelatedFilesResult:
        """
        Find files related to the target file through cross-references
        
        Args:
            target_file: File to find relations for
            max_depth: Maximum depth of relationship traversal
            max_results: Maximum number of related files to return
            
        Returns:
            RelatedFilesResult with scored and prioritized related files
        """
        
        try:
            related_files = {}
            visited = set()
            queue = deque([(target_file, 0, 1.0)])  # (file, depth, relevance_score)
            
            while queue and len(related_files) < max_results:
                current_file, depth, relevance = queue.popleft()
                
                if current_file in visited or depth > max_depth:
                    continue
                
                visited.add(current_file)
                
                # Add to results if not the target file
                if current_file != target_file:
                    related_files[current_file] = {
                        'relevance_score': relevance,
                        'depth': depth,
                        'relationship_types': self._get_relationship_types(target_file, current_file)
                    }
                
                # Find directly connected files
                connected_files = set()
                
                # Forward dependencies
                connected_files.update(self.reference_graph.file_dependencies.get(current_file, []))
                
                # Reverse dependencies  
                connected_files.update(self.reference_graph.reverse_dependencies.get(current_file, []))
                
                # Add connected files to queue with reduced relevance
                for connected_file in connected_files:
                    if connected_file not in visited:
                        # Calculate relevance decay based on depth and relationship strength
                        relationship_strength = self._calculate_relationship_strength(current_file, connected_file)
                        new_relevance = relevance * 0.7 * relationship_strength  # Decay factor
                        
                        if new_relevance > 0.1:  # Minimum relevance threshold
                            queue.append((connected_file, depth + 1, new_relevance))
            
            # Sort by relevance score
            sorted_related = sorted(
                related_files.items(),
                key=lambda x: x[1]['relevance_score'],
                reverse=True
            )
            
            return RelatedFilesResult(
                success=True,
                target_file=target_file,
                related_files=dict(sorted_related[:max_results]),
                total_found=len(sorted_related),
                max_depth_reached=max(info['depth'] for info in related_files.values()) if related_files else 0
            )
            
        except Exception as e:
            return RelatedFilesResult(
                success=False,
                target_file=target_file,
                error=f"Failed to find related files: {str(e)}",
                related_files={},
                total_found=0
            )
    
    def _get_relationship_types(self, source_file: Path, target_file: Path) -> List[ReferenceType]:
        """Get all relationship types between two files"""
        
        relationship_types = set()
        
        for reference in self.reference_graph.cross_references:
            if (reference.source_file == source_file and reference.target_file == target_file) or \
               (reference.source_file == target_file and reference.target_file == source_file):
                relationship_types.add(reference.reference_type)
        
        return list(relationship_types)
    
    def _calculate_relationship_strength(self, source_file: Path, target_file: Path) -> float:
        """Calculate strength of relationship between two files"""
        
        # Count references between files
        reference_count = 0
        reference_types = set()
        
        for reference in self.reference_graph.cross_references:
            if (reference.source_file == source_file and reference.target_file == target_file) or \
               (reference.source_file == target_file and reference.target_file == source_file):
                reference_count += 1
                reference_types.add(reference.reference_type)
        
        # Base strength from reference count
        count_strength = min(1.0, reference_count / 5.0)  # Normalize to 0-1
        
        # Bonus for diverse reference types
        type_diversity_bonus = len(reference_types) * 0.1
        
        # Bonus for strong reference types
        strong_type_bonus = 0.0
        strong_types = {ReferenceType.IMPORT, ReferenceType.CLASS_INHERITANCE, ReferenceType.TEST_COVERAGE}
        if any(ref_type in strong_types for ref_type in reference_types):
            strong_type_bonus = 0.3
        
        total_strength = count_strength + type_diversity_bonus + strong_type_bonus
        return min(1.0, total_strength)

# === File-Specific Analyzers ===

class PythonReferenceAnalyzer:
    """Analyze Python files for cross-references"""
    
    def discover_entities(self, file_path: Path) -> List[EntityReference]:
        """Discover Python entities (functions, classes, variables)"""
        
        entities = []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse Python AST
            tree = ast.parse(content)
            
            # Visit AST nodes to find entities
            visitor = PythonEntityVisitor(file_path)
            visitor.visit(tree)
            
            entities.extend(visitor.entities)
            
        except Exception as e:
            # Fallback to regex-based analysis if AST parsing fails
            entities.extend(self._regex_based_entity_discovery(file_path, content))
        
        return entities
    
    def discover_references(self, file_path: Path, known_entities: Dict[str, EntityReference]) -> List[CrossReference]:
        """Discover cross-references in Python file"""
        
        references = []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse Python AST
            tree = ast.parse(content)
            
            # Visit AST nodes to find references
            visitor = PythonReferenceVisitor(file_path, known_entities)
            visitor.visit(tree)
            
            references.extend(visitor.references)
            
        except Exception as e:
            # Fallback to regex-based analysis if AST parsing fails
            references.extend(self._regex_based_reference_discovery(file_path, content, known_entities))
        
        return references

class PythonEntityVisitor(ast.NodeVisitor):
    """AST visitor to discover Python entities"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.entities = []
        self.current_class = None
        self.current_function = None
    
    def visit_ClassDef(self, node):
        """Visit class definition"""
        entity = EntityReference(
            entity_name=node.name,
            entity_type='class',
            file_path=self.file_path,
            location=(node.lineno, node.col_offset),
            definition=ast.get_source_segment(self._get_source(), node) or f"class {node.name}",
            docstring=ast.get_docstring(node),
            scope='global' if not self.current_class else 'class'
        )
        self.entities.append(entity)
        
        # Visit class body
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definition"""
        # Generate function signature
        args = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(args)})"
        
        entity = EntityReference(
            entity_name=node.name,
            entity_type='function',
            file_path=self.file_path,
            location=(node.lineno, node.col_offset),
            definition=ast.get_source_segment(self._get_source(), node) or f"def {signature}",
            signature=signature,
            docstring=ast.get_docstring(node),
            scope='class' if self.current_class else 'global'
        )
        self.entities.append(entity)
        
        # Visit function body
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

class MarkdownReferenceAnalyzer:
    """Analyze Markdown files for cross-references"""
    
    def discover_entities(self, file_path: Path) -> List[EntityReference]:
        """Discover Markdown entities (headers, links)"""
        
        entities = []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Find headers
                header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if header_match:
                    level = len(header_match.group(1))
                    title = header_match.group(2)
                    
                    entity = EntityReference(
                        entity_name=title,
                        entity_type=f'header_h{level}',
                        file_path=file_path,
                        location=(line_num, 0),
                        definition=line,
                        scope='global'
                    )
                    entities.append(entity)
        
        except Exception as e:
            pass  # Skip files that can't be read
        
        return entities
    
    def discover_references(self, file_path: Path, known_entities: Dict[str, EntityReference]) -> List[CrossReference]:
        """Discover cross-references in Markdown file"""
        
        references = []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Find markdown links: [text](path) or [text](path#anchor)
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                for match in re.finditer(link_pattern, line):
                    link_text = match.group(1)
                    link_path = match.group(2)
                    
                    # Resolve relative paths
                    if not link_path.startswith(('http://', 'https://', 'mailto:')):
                        target_path = self._resolve_markdown_path(file_path, link_path)
                        
                        if target_path and target_path.exists():
                            reference = CrossReference(
                                source_file=file_path,
                                target_file=target_path,
                                reference_type=ReferenceType.DOCUMENTATION_LINK,
                                source_location=(line_num, match.start()),
                                source_context=line.strip(),
                                confidence=0.9,
                                metadata={'link_text': link_text, 'link_path': link_path}
                            )
                            references.append(reference)
        
        except Exception as e:
            pass  # Skip files that can't be analyzed
        
        return references
    
    def _resolve_markdown_path(self, source_file: Path, link_path: str) -> Optional[Path]:
        """Resolve markdown link path to actual file"""
        
        # Remove anchor if present
        if '#' in link_path:
            link_path = link_path.split('#')[0]
        
        # Handle relative paths
        if link_path.startswith('./') or not link_path.startswith('/'):
            resolved_path = source_file.parent / link_path
        else:
            # Absolute path from project root
            resolved_path = source_file.parent  # This would need project root context
        
        return resolved_path.resolve() if resolved_path else None

# === Data Classes for Results ===

@dataclass
class ReferenceDiscoveryResult:
    """Result of complete reference discovery process"""
    success: bool
    reference_graph: ReferenceGraph
    files_analyzed: int
    definitions_found: int
    references_found: int
    discovery_time: Optional[datetime] = None
    error: Optional[str] = None
    analysis_results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RelatedFilesResult:
    """Result of finding files related to a target file"""
    success: bool
    target_file: Path
    related_files: Dict[Path, Dict[str, Any]]
    total_found: int
    max_depth_reached: int = 0
    error: Optional[str] = None

# This pseudocode implements a comprehensive cross-reference discovery system
# that can analyze multiple file types and build a complete graph of relationships
# to support intelligent context loading and autonomous navigation.