# Pseudocode Part 3: Cross-Reference System Logic

## Overview
Define how file relationships are discovered, maintained, and used for intelligent context loading. This enables the autonomous system to understand project structure and load relevant context for any given task.

## Cross-Reference Discovery Principles

### 1. Multi-Source Relationship Detection
Combine multiple techniques to discover file relationships:
- **Explicit Comments**: `# RELATES_TO:` annotations
- **Import Analysis**: Static code analysis for import statements
- **Naming Conventions**: File naming patterns and directory structure
- **Content Analysis**: LLM analysis of file content for conceptual relationships

### 2. Relationship Strength Classification
- **Strong**: Direct imports, explicit annotations, shared data structures
- **Medium**: Cross-reference comments, naming conventions, common patterns
- **Weak**: Conceptual similarity, same domain, inferred relationships

### 3. Bidirectional Consistency
All relationships must be bidirectional and consistent across the project.

## Cross-Reference System Components

### 1. Relationship Discovery Engine (`src/context/cross_reference_manager.py`)

```python
class CrossReferenceManager:
    """Discovers, maintains, and queries file relationships"""
    
    def __init__(self, project_root: str, config: SystemConfiguration):
        self.project_root = Path(project_root)
        self.config = config
        
        # Relationship discovery engines
        self.comment_scanner = CommentBasedScanner()
        self.import_analyzer = ImportAnalyzer() 
        self.naming_analyzer = NamingConventionAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        
        # Relationship validation
        self.relationship_validator = RelationshipValidator()
        
    def discover_all_relationships(self) -> CrossReferenceMap:
        """Scan entire project to discover file relationships"""
        
        # Get all relevant files in project
        project_files = self._scan_project_files()
        
        # Initialize relationship map
        relationship_map = CrossReferenceMap()
        
        # Apply each discovery method
        for file_path in project_files:
            
            # Explicit comment-based relationships
            comment_relations = self.comment_scanner.scan_file(file_path)
            self._add_relationships(relationship_map, file_path, comment_relations, 'medium')
            
            # Import-based relationships (strong)
            import_relations = self.import_analyzer.analyze_imports(file_path)
            self._add_relationships(relationship_map, file_path, import_relations, 'strong')
            
            # Naming convention relationships (weak)
            naming_relations = self.naming_analyzer.find_related_by_naming(file_path, project_files)
            self._add_relationships(relationship_map, file_path, naming_relations, 'weak')
            
            # Content-based conceptual relationships (medium)
            if self.config.cross_reference.enable_content_analysis:
                content_relations = self.content_analyzer.find_conceptual_relationships(file_path, project_files)
                self._add_relationships(relationship_map, file_path, content_relations, 'medium')
        
        # Validate relationship consistency
        self._validate_relationship_consistency(relationship_map)
        
        # Make relationships bidirectional
        self._ensure_bidirectional_relationships(relationship_map)
        
        # Update relationship metadata
        relationship_map.last_updated = datetime.utcnow().isoformat()
        relationship_map.validation_status = 'valid'
        
        return relationship_map
    
    def incremental_relationship_update(self, changed_files: List[str], 
                                      current_map: CrossReferenceMap) -> CrossReferenceMap:
        """Update relationships for only changed files (performance optimization)"""
        
        updated_map = deepcopy(current_map)
        
        for file_path in changed_files:
            
            # Remove existing relationships for this file
            self._remove_file_relationships(updated_map, file_path)
            
            # Re-discover relationships for this file
            if Path(file_path).exists():
                
                comment_relations = self.comment_scanner.scan_file(file_path)
                self._add_relationships(updated_map, file_path, comment_relations, 'medium')
                
                import_relations = self.import_analyzer.analyze_imports(file_path)
                self._add_relationships(updated_map, file_path, import_relations, 'strong')
                
                naming_relations = self.naming_analyzer.find_related_by_naming(file_path, self._get_all_files())
                self._add_relationships(updated_map, file_path, naming_relations, 'weak')
            
            else:
                # File was deleted - clean up all references to it
                self._clean_deleted_file_references(updated_map, file_path)
        
        # Re-validate affected relationships
        self._validate_relationship_consistency(updated_map)
        self._ensure_bidirectional_relationships(updated_map)
        
        updated_map.last_updated = datetime.utcnow().isoformat()
        
        return updated_map
```

### 2. Comment-Based Relationship Scanner

```python
class CommentBasedScanner:
    """Scans files for explicit RELATES_TO comments"""
    
    RELATES_TO_PATTERNS = [
        r'#\s*RELATES_TO:\s*(.+)',          # Python/bash style
        r'//\s*RELATES_TO:\s*(.+)',         # JavaScript/Java/C++ style  
        r'<!--\s*RELATES_TO:\s*(.+)\s*-->', # HTML/XML style
        r'/\*\s*RELATES_TO:\s*(.+)\s*\*/',  # CSS/multi-line comment style
    ]
    
    def scan_file(self, file_path: str) -> Dict[str, List[str]]:
        """Extract RELATES_TO relationships from file comments"""
        
        relationships = {
            'documents': [],
            'implements': [],
            'tests': [],
            'depends_on': [],
            'configures': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Search for RELATES_TO patterns
            for pattern in self.RELATES_TO_PATTERNS:
                matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    # Parse comma-separated file paths
                    related_files = [f.strip() for f in match.split(',')]
                    
                    # Categorize relationships based on file types and context
                    for related_file in related_files:
                        relationship_type = self._infer_relationship_type(file_path, related_file)
                        if relationship_type in relationships:
                            relationships[relationship_type].append(related_file)
            
        except (FileNotFoundError, UnicodeDecodeError, PermissionError) as e:
            # Log error but don't fail - just return empty relationships
            logging.warning(f"Could not scan {file_path} for relationships: {e}")
        
        return relationships
    
    def _infer_relationship_type(self, source_file: str, target_file: str) -> str:
        """Infer the type of relationship based on file paths and extensions"""
        
        source_path = Path(source_file)
        target_path = Path(target_file)
        
        # Documentation relationships
        if target_path.parts and target_path.parts[0] == 'docs':
            return 'documents'
        
        # Test relationships
        if 'test' in target_path.parts or target_path.stem.startswith('test_'):
            return 'tests'
        
        # Configuration relationships
        if target_path.suffix in ['.json', '.yaml', '.yml', '.toml', '.ini']:
            return 'configures'
        
        # Implementation relationships (same language)
        if source_path.suffix == target_path.suffix and target_path.parts and target_path.parts[0] == 'src':
            return 'implements'
        
        # Default to dependency relationship
        return 'depends_on'
```

### 3. Import Analysis Engine

```python
class ImportAnalyzer:
    """Analyzes source code files for import statements and dependencies"""
    
    def __init__(self):
        self.language_analyzers = {
            '.py': PythonImportAnalyzer(),
            '.js': JavaScriptImportAnalyzer(), 
            '.ts': TypeScriptImportAnalyzer(),
            '.java': JavaImportAnalyzer(),
            '.go': GoImportAnalyzer(),
            '.rs': RustImportAnalyzer()
        }
    
    def analyze_imports(self, file_path: str) -> Dict[str, List[str]]:
        """Analyze import statements to find code dependencies"""
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.language_analyzers:
            return {'depends_on': []}
        
        analyzer = self.language_analyzers[file_extension]
        
        try:
            imports = analyzer.extract_imports(file_path)
            
            # Resolve imports to actual file paths within project
            resolved_imports = self._resolve_import_paths(imports, file_path)
            
            return {'depends_on': resolved_imports}
            
        except Exception as e:
            logging.warning(f"Import analysis failed for {file_path}: {e}")
            return {'depends_on': []}
    
    def _resolve_import_paths(self, imports: List[str], source_file: str) -> List[str]:
        """Resolve import statements to actual file paths within the project"""
        
        resolved_paths = []
        source_dir = Path(source_file).parent
        project_root = self._find_project_root(source_file)
        
        for import_statement in imports:
            
            # Handle relative imports
            if import_statement.startswith('.'):
                resolved_path = self._resolve_relative_import(import_statement, source_dir, project_root)
                if resolved_path:
                    resolved_paths.append(resolved_path)
            
            # Handle absolute imports within project
            else:
                resolved_path = self._resolve_absolute_import(import_statement, project_root)
                if resolved_path:
                    resolved_paths.append(resolved_path)
        
        return resolved_paths

class PythonImportAnalyzer:
    """Python-specific import analysis"""
    
    def extract_imports(self, file_path: str) -> List[str]:
        """Extract Python import statements"""
        
        imports = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse with AST for accuracy
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                    
                    # Handle relative imports
                    if node.level > 0:
                        relative_import = '.' * node.level
                        if node.module:
                            relative_import += node.module
                        imports.append(relative_import)
        
        except (SyntaxError, UnicodeDecodeError) as e:
            # Fall back to regex-based parsing if AST fails
            imports = self._regex_fallback_imports(file_path)
        
        return imports
    
    def _regex_fallback_imports(self, file_path: str) -> List[str]:
        """Fallback regex-based import extraction for malformed Python files"""
        
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
            r'^from\s+(\.+[a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
        ]
        
        imports = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    for pattern in import_patterns:
                        match = re.match(pattern, line)
                        if match:
                            imports.append(match.group(1))
                            break
        except Exception:
            pass
        
        return imports
```

### 4. Context Loading Strategy

```python
class ContextLoader:
    """Loads relevant context for a given task based on cross-references"""
    
    def __init__(self, cross_ref_manager: CrossReferenceManager, config: SystemConfiguration):
        self.cross_ref_manager = cross_ref_manager
        self.config = config
        self.max_context_size = config.context_management.max_context_tokens
        
    def load_context_for_task(self, task: Task, cross_references: CrossReferenceMap) -> ContextBundle:
        """Load relevant context files for executing a specific task"""
        
        # Start with files directly targeted by the task
        primary_files = task.file_targets.copy()
        context_files = set(primary_files)
        
        # Add files based on cross-references (breadth-first expansion)
        context_files.update(self._expand_context_breadth_first(primary_files, cross_references, max_depth=2))
        
        # Add task-specific context requirements
        context_files.update(task.context_requirements)
        
        # Prioritize files by relationship strength and relevance
        prioritized_files = self._prioritize_context_files(context_files, task, cross_references)
        
        # Load files within context size limit
        context_bundle = self._load_files_within_limit(prioritized_files, self.max_context_size)
        
        # Add metadata about loaded context
        context_bundle.task_id = task.id
        context_bundle.loaded_at = datetime.utcnow().isoformat()
        context_bundle.truncated = len(prioritized_files) > len(context_bundle.files)
        
        return context_bundle
    
    def _expand_context_breadth_first(self, starting_files: List[str], 
                                    cross_references: CrossReferenceMap, 
                                    max_depth: int = 2) -> Set[str]:
        """Expand context using breadth-first traversal of cross-references"""
        
        visited = set(starting_files)
        queue = [(file, 0) for file in starting_files]  # (file_path, depth)
        
        while queue:
            current_file, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # Get relationships for current file
            if current_file in cross_references.file_relationships:
                relationships = cross_references.file_relationships[current_file].relationships
                
                # Add related files to context
                for relation_type, related_files in relationships.items():
                    for related_file in related_files:
                        if related_file not in visited:
                            visited.add(related_file)
                            queue.append((related_file, depth + 1))
        
        return visited
    
    def _prioritize_context_files(self, context_files: Set[str], 
                                task: Task, 
                                cross_references: CrossReferenceMap) -> List[str]:
        """Prioritize context files by relevance and relationship strength"""
        
        file_scores = {}
        
        for file_path in context_files:
            score = 0
            
            # Higher priority for task target files
            if file_path in task.file_targets:
                score += 100
            
            # Higher priority for task context requirements
            if file_path in task.context_requirements:
                score += 80
            
            # Priority based on relationship strength
            if file_path in cross_references.file_relationships:
                relationships = cross_references.file_relationships[file_path]
                
                strong_relations = len(relationships.relationship_strength.get('strong', []))
                medium_relations = len(relationships.relationship_strength.get('medium', []))
                weak_relations = len(relationships.relationship_strength.get('weak', []))
                
                score += strong_relations * 10 + medium_relations * 5 + weak_relations * 1
            
            # Priority based on file type relevance
            file_type_score = self._calculate_file_type_relevance(file_path, task)
            score += file_type_score
            
            file_scores[file_path] = score
        
        # Sort by score (highest first)
        return sorted(context_files, key=lambda f: file_scores.get(f, 0), reverse=True)
    
    def _load_files_within_limit(self, prioritized_files: List[str], 
                               max_tokens: int) -> ContextBundle:
        """Load files sequentially until context size limit reached"""
        
        context_bundle = ContextBundle()
        current_token_count = 0
        
        for file_path in prioritized_files:
            
            try:
                # Estimate token count for file
                file_token_count = self._estimate_file_token_count(file_path)
                
                # Check if adding this file would exceed limit
                if current_token_count + file_token_count > max_tokens:
                    # Try to include partial content if possible
                    remaining_tokens = max_tokens - current_token_count
                    if remaining_tokens > 100:  # Minimum useful content
                        partial_content = self._load_partial_file_content(file_path, remaining_tokens)
                        context_bundle.add_file(file_path, partial_content, truncated=True)
                    break
                
                # Load full file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                context_bundle.add_file(file_path, content, truncated=False)
                current_token_count += file_token_count
                
            except Exception as e:
                logging.warning(f"Could not load context file {file_path}: {e}")
                continue
        
        return context_bundle
```

### 5. Relationship Validation and Maintenance

```python
def validate_cross_references(self, cross_references: CrossReferenceMap) -> ValidationReport:
    """Validate cross-reference integrity and identify issues"""
    
    validation_report = ValidationReport()
    
    # Check for broken references (files that don't exist)
    for file_path, relationships in cross_references.file_relationships.items():
        
        # Verify source file exists
        if not Path(file_path).exists():
            validation_report.add_error(f"Source file {file_path} in cross-reference map does not exist")
            continue
        
        # Verify all referenced files exist
        for relation_type, related_files in relationships.relationships.items():
            for related_file in related_files:
                if not Path(related_file).exists():
                    validation_report.add_warning(f"Referenced file {related_file} does not exist")
                    cross_references.broken_references.append(f"{file_path} -> {related_file}")
    
    # Check for bidirectional consistency
    for file_path, relationships in cross_references.file_relationships.items():
        for relation_type, related_files in relationships.relationships.items():
            for related_file in related_files:
                
                # Check if reverse relationship exists
                if related_file in cross_references.file_relationships:
                    reverse_relationships = cross_references.file_relationships[related_file].relationships
                    reverse_relation_type = self._get_reverse_relation_type(relation_type)
                    
                    if reverse_relation_type not in reverse_relationships or file_path not in reverse_relationships[reverse_relation_type]:
                        validation_report.add_warning(f"Missing reverse relationship: {related_file} should reference {file_path}")
    
    # Check for circular dependencies
    circular_deps = self._detect_circular_dependencies(cross_references)
    for circular_dep in circular_deps:
        validation_report.add_error(f"Circular dependency detected: {' -> '.join(circular_dep)}")
        cross_references.circular_dependencies.append(circular_dep)
    
    # Update validation status
    if validation_report.has_errors():
        cross_references.validation_status = 'invalid'
    elif validation_report.has_warnings():
        cross_references.validation_status = 'valid_with_warnings'
    else:
        cross_references.validation_status = 'valid'
    
    return validation_report
```

## Performance Optimizations

### Caching Strategies
- **Relationship Cache**: Cache discovered relationships to avoid re-scanning unchanged files
- **Content Hash Cache**: Use file content hashes to detect changes efficiently
- **Import Resolution Cache**: Cache import path resolutions for faster lookups

### Incremental Updates
- **File Change Detection**: Only re-analyze files that have changed since last scan
- **Dependency Invalidation**: When a file changes, only re-analyze files that depend on it
- **Lazy Loading**: Only load cross-references when actually needed for context

### Memory Management
- **Streaming Analysis**: Process large files in chunks to avoid memory bloat
- **Context Size Limits**: Enforce hard limits on context size to prevent memory issues
- **Garbage Collection**: Clean up unused relationship data periodically

## Cross-References
```
# RELATES_TO: pseudocode_1_information_architecture.md (CrossReferenceMap data structure),
#            pseudocode_2_persistence_layer.md (cross-reference state persistence),
#            architecture_decisions.md (ADR-002: hybrid file system for context management),
#            tentative_file_structure.md (cross-reference storage location)
```

## Next Foundation Component
After cross-reference system, the next foundation component is **Main State Machine Logic** - the overall workflow that coordinates all system components and manages autonomous progression through methodology phases.