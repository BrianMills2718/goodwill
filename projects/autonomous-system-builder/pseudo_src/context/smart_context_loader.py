# Smart Context Loader - Context System Pseudocode
# Part of autonomous TDD system context management layer

"""
Smart Context Loading System

Intelligently loads and manages project context within Claude Code's token limits,
using the detailed architecture established in docs/architecture/llm_integration_patterns.md
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

# === Configuration and Data Classes ===

@dataclass
class ContextLimits:
    """Context size limits for token management"""
    max_context_tokens: int = 150000  # Conservative limit
    max_total_tokens: int = 190000    # Aggressive limit  
    max_response_tokens: int = 8000   # Response allowance
    safety_margin: int = 5000         # Safety buffer

@dataclass
class FileMetadata:
    """Metadata for context files"""
    path: Path
    size_bytes: int
    estimated_tokens: int
    last_modified: float
    file_type: str
    relevance_score: float
    priority_score: float
    cross_references: List[str]

@dataclass
class ContextChunk:
    """A chunk of context data"""
    content: str
    source_file: Path
    chunk_type: str  # 'full', 'signature', 'summary', 'excerpt'
    estimated_tokens: int
    relevance_score: float
    metadata: Dict[str, Any]

class LoadingStrategy(Enum):
    """Context loading strategies"""
    FULL_FILES = "full_files"
    SIGNATURES_ONLY = "signatures_only" 
    SMART_EXCERPTS = "smart_excerpts"
    SUMMARIZED = "summarized"
    HYBRID = "hybrid"

# === Smart Context Loader Implementation ===

class SmartContextLoader:
    """
    Intelligent context loading with token optimization and relevance scoring
    
    Based on architecture from docs/architecture/llm_integration_patterns.md
    Implements context optimization patterns for LLM token limits
    """
    
    def __init__(self, config: ContextConfig):
        self.config = config
        self.limits = ContextLimits(
            max_context_tokens=config.max_context_tokens,
            max_total_tokens=config.max_total_tokens
        )
        
        # Core components
        self.token_estimator = TokenEstimator()
        self.relevance_scorer = RelevanceScorer(config.relevance_weights)
        self.content_optimizer = ContentOptimizer(self.limits)
        self.cross_reference_analyzer = CrossReferenceAnalyzer()
        
        # Caching
        self.metadata_cache = {}
        self.content_cache = LRUCache(max_size=config.cache_size)
        
        # State tracking
        self.current_context = {}
        self.loading_history = []
    
    def load_context_for_task(self, task: AutonomousTask) -> ContextLoadResult:
        """
        Load optimized context for specific autonomous task
        
        Args:
            task: The autonomous task requiring context
            
        Returns:
            ContextLoadResult with optimized context data
        """
        
        try:
            # Analyze task requirements
            task_analysis = self._analyze_task_requirements(task)
            
            # Discover relevant files
            relevant_files = self._discover_relevant_files(task, task_analysis)
            
            # Score and prioritize files
            prioritized_files = self._prioritize_files(relevant_files, task_analysis)
            
            # Optimize context loading
            optimized_context = self._optimize_context_loading(prioritized_files, task_analysis)
            
            # Validate context fits limits
            validation_result = self._validate_context_limits(optimized_context)
            
            if not validation_result.fits_limits:
                # Apply aggressive optimization
                optimized_context = self._apply_aggressive_optimization(
                    optimized_context, validation_result.tokens_over_limit
                )
            
            # Update state
            self.current_context = optimized_context.context_data
            self.loading_history.append(ContextLoadEvent(
                task_id=task.task_id,
                files_loaded=len(optimized_context.context_data),
                total_tokens=optimized_context.total_tokens,
                strategy_used=optimized_context.strategy_used,
                timestamp=datetime.now()
            ))
            
            return ContextLoadResult(
                success=True,
                context_data=optimized_context.context_data,
                metadata=optimized_context.metadata,
                total_tokens=optimized_context.total_tokens,
                files_loaded=len(optimized_context.context_data),
                strategy_used=optimized_context.strategy_used,
                optimization_applied=optimized_context.optimization_applied
            )
            
        except Exception as e:
            return ContextLoadResult(
                success=False,
                error=f"Context loading failed: {str(e)}",
                context_data={},
                total_tokens=0
            )
    
    def _analyze_task_requirements(self, task: AutonomousTask) -> TaskAnalysis:
        """Analyze task to understand context requirements"""
        
        # Extract file patterns from task description
        file_patterns = self._extract_file_patterns(task.description)
        
        # Determine task type and context needs
        task_type = self._classify_task_type(task)
        
        # Calculate context requirements
        context_requirements = self._calculate_context_requirements(task_type, task)
        
        return TaskAnalysis(
            task_type=task_type,
            file_patterns=file_patterns,
            context_requirements=context_requirements,
            priority_areas=self._identify_priority_areas(task),
            cross_reference_needs=self._assess_cross_reference_needs(task)
        )
    
    def _discover_relevant_files(self, task: AutonomousTask, analysis: TaskAnalysis) -> List[FileMetadata]:
        """Discover files relevant to the task"""
        
        relevant_files = []
        
        # Start with explicitly mentioned files
        explicit_files = self._extract_explicit_files(task.description)
        for file_path in explicit_files:
            if Path(file_path).exists():
                metadata = self._get_file_metadata(Path(file_path))
                metadata.relevance_score = 1.0  # Maximum relevance for explicit files
                relevant_files.append(metadata)
        
        # Discover files by pattern matching
        pattern_files = self._discover_by_patterns(analysis.file_patterns)
        relevant_files.extend(pattern_files)
        
        # Discover by cross-references
        cross_ref_files = self._discover_by_cross_references(explicit_files, analysis.cross_reference_needs)
        relevant_files.extend(cross_ref_files)
        
        # Discover by task type
        task_type_files = self._discover_by_task_type(analysis.task_type)
        relevant_files.extend(task_type_files)
        
        # Remove duplicates and update metadata
        unique_files = self._deduplicate_files(relevant_files)
        
        return unique_files
    
    def _prioritize_files(self, files: List[FileMetadata], analysis: TaskAnalysis) -> List[FileMetadata]:
        """Score and prioritize files for loading"""
        
        for file_metadata in files:
            # Calculate priority score based on multiple factors
            priority_components = {
                'relevance': file_metadata.relevance_score * 0.4,
                'recency': self._calculate_recency_score(file_metadata) * 0.2,
                'size_efficiency': self._calculate_size_efficiency(file_metadata) * 0.2,
                'cross_reference_density': self._calculate_cross_ref_density(file_metadata) * 0.1,
                'task_type_alignment': self._calculate_task_alignment(file_metadata, analysis) * 0.1
            }
            
            file_metadata.priority_score = sum(priority_components.values())
        
        # Sort by priority score (highest first)
        prioritized_files = sorted(files, key=lambda f: f.priority_score, reverse=True)
        
        return prioritized_files
    
    def _optimize_context_loading(self, prioritized_files: List[FileMetadata], analysis: TaskAnalysis) -> OptimizedContext:
        """Optimize context loading based on token limits and task requirements"""
        
        context_data = {}
        total_tokens = 0
        files_processed = 0
        optimization_applied = False
        strategy_used = LoadingStrategy.HYBRID
        
        # Reserve tokens for response and safety margin
        available_tokens = self.limits.max_context_tokens - self.limits.max_response_tokens - self.limits.safety_margin
        
        # Load files in priority order with intelligent strategies
        for file_metadata in prioritized_files:
            if total_tokens >= available_tokens:
                break
            
            # Determine loading strategy for this file
            file_strategy = self._determine_file_strategy(file_metadata, available_tokens - total_tokens, analysis)
            
            # Load file content using determined strategy
            content_result = self._load_file_with_strategy(file_metadata, file_strategy)
            
            if content_result.success:
                # Check if content fits in remaining tokens
                if total_tokens + content_result.estimated_tokens <= available_tokens:
                    context_data[str(file_metadata.path)] = content_result.content
                    total_tokens += content_result.estimated_tokens
                    files_processed += 1
                    
                    if content_result.strategy_applied != LoadingStrategy.FULL_FILES:
                        optimization_applied = True
                else:
                    # Try more aggressive optimization
                    aggressive_result = self._apply_aggressive_file_optimization(
                        file_metadata, available_tokens - total_tokens
                    )
                    
                    if aggressive_result.success and aggressive_result.estimated_tokens <= available_tokens - total_tokens:
                        context_data[str(file_metadata.path)] = aggressive_result.content
                        total_tokens += aggressive_result.estimated_tokens
                        files_processed += 1
                        optimization_applied = True
        
        return OptimizedContext(
            context_data=context_data,
            total_tokens=total_tokens,
            files_loaded=files_processed,
            strategy_used=strategy_used,
            optimization_applied=optimization_applied,
            metadata={
                'available_tokens': available_tokens,
                'files_considered': len(prioritized_files),
                'files_loaded': files_processed,
                'optimization_applied': optimization_applied
            }
        )
    
    def _determine_file_strategy(self, file_metadata: FileMetadata, remaining_tokens: int, analysis: TaskAnalysis) -> LoadingStrategy:
        """Determine optimal loading strategy for a specific file"""
        
        # If file easily fits, load full content
        if file_metadata.estimated_tokens <= remaining_tokens * 0.3:
            return LoadingStrategy.FULL_FILES
        
        # If file is code and task needs signatures, use signatures only
        if (file_metadata.file_type in ['python', 'javascript', 'typescript'] and 
            analysis.task_type in ['implementation', 'architecture_review']):
            return LoadingStrategy.SIGNATURES_ONLY
        
        # If file is large documentation, use smart excerpts
        if (file_metadata.file_type == 'markdown' and 
            file_metadata.estimated_tokens > remaining_tokens * 0.5):
            return LoadingStrategy.SMART_EXCERPTS
        
        # If file is too large but has high priority, summarize
        if (file_metadata.priority_score > 0.7 and 
            file_metadata.estimated_tokens > remaining_tokens):
            return LoadingStrategy.SUMMARIZED
        
        # Default to hybrid approach
        return LoadingStrategy.HYBRID
    
    def _load_file_with_strategy(self, file_metadata: FileMetadata, strategy: LoadingStrategy) -> FileLoadResult:
        """Load file content using specified strategy"""
        
        try:
            # Check cache first
            cache_key = f"{file_metadata.path}:{strategy.value}:{file_metadata.last_modified}"
            cached_result = self.content_cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Load content based on strategy
            if strategy == LoadingStrategy.FULL_FILES:
                content = self._load_full_file(file_metadata.path)
                estimated_tokens = self.token_estimator.estimate_tokens(content)
                
            elif strategy == LoadingStrategy.SIGNATURES_ONLY:
                content = self._extract_signatures(file_metadata.path)
                estimated_tokens = self.token_estimator.estimate_tokens(content)
                
            elif strategy == LoadingStrategy.SMART_EXCERPTS:
                content = self._extract_smart_excerpts(file_metadata.path, file_metadata)
                estimated_tokens = self.token_estimator.estimate_tokens(content)
                
            elif strategy == LoadingStrategy.SUMMARIZED:
                content = self._generate_file_summary(file_metadata.path)
                estimated_tokens = self.token_estimator.estimate_tokens(content)
                
            elif strategy == LoadingStrategy.HYBRID:
                content = self._apply_hybrid_strategy(file_metadata)
                estimated_tokens = self.token_estimator.estimate_tokens(content)
            
            result = FileLoadResult(
                success=True,
                content=content,
                estimated_tokens=estimated_tokens,
                strategy_applied=strategy,
                file_path=file_metadata.path
            )
            
            # Cache result
            self.content_cache.put(cache_key, result)
            
            return result
            
        except Exception as e:
            return FileLoadResult(
                success=False,
                error=f"Failed to load {file_metadata.path} with strategy {strategy}: {str(e)}",
                content="",
                estimated_tokens=0,
                strategy_applied=strategy,
                file_path=file_metadata.path
            )
    
    def _extract_signatures(self, file_path: Path) -> str:
        """Extract function/class signatures from code files"""
        
        if not file_path.exists():
            return f"# File not found: {file_path}"
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract signatures based on file type
            if file_path.suffix == '.py':
                return self._extract_python_signatures(content)
            elif file_path.suffix in ['.js', '.ts']:
                return self._extract_javascript_signatures(content)
            elif file_path.suffix in ['.java']:
                return self._extract_java_signatures(content)
            else:
                # For other files, return first 20 lines as signature
                lines = content.split('\n')
                return '\n'.join(lines[:20]) + '\n...' if len(lines) > 20 else content
                
        except Exception as e:
            return f"# Error extracting signatures from {file_path}: {str(e)}"
    
    def _extract_python_signatures(self, content: str) -> str:
        """Extract Python function and class signatures"""
        
        signatures = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Class definitions
            if stripped.startswith('class '):
                signatures.append(line)
                # Add docstring if present
                if i + 1 < len(lines) and '"""' in lines[i + 1]:
                    j = i + 1
                    while j < len(lines) and not (lines[j].count('"""') >= 2 or (j > i + 1 and '"""' in lines[j])):
                        signatures.append(lines[j])
                        j += 1
                    if j < len(lines):
                        signatures.append(lines[j])
            
            # Function definitions  
            elif stripped.startswith('def '):
                signatures.append(line)
                # Add docstring if present
                if i + 1 < len(lines) and '"""' in lines[i + 1]:
                    j = i + 1
                    while j < len(lines) and not (lines[j].count('"""') >= 2 or (j > i + 1 and '"""' in lines[j])):
                        signatures.append(lines[j])
                        j += 1
                    if j < len(lines):
                        signatures.append(lines[j])
            
            # Import statements
            elif stripped.startswith(('import ', 'from ')):
                signatures.append(line)
            
            # Global variables and constants
            elif stripped and '=' in stripped and not stripped.startswith((' ', '\t')):
                if stripped.isupper() or stripped.startswith(('CONFIG', 'DEFAULT', 'MAX', 'MIN')):
                    signatures.append(line)
        
        return '\n'.join(signatures)
    
    def _extract_smart_excerpts(self, file_path: Path, file_metadata: FileMetadata) -> str:
        """Extract smart excerpts from large files based on relevance"""
        
        if not file_path.exists():
            return f"# File not found: {file_path}"
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections (by headers for markdown, by functions for code)
            sections = self._split_into_sections(content, file_path.suffix)
            
            # Score sections by relevance
            scored_sections = []
            for section in sections:
                relevance_score = self._calculate_section_relevance(section, file_metadata)
                scored_sections.append((section, relevance_score))
            
            # Sort by relevance and select top sections
            scored_sections.sort(key=lambda x: x[1], reverse=True)
            
            # Select sections that fit in reasonable token budget
            selected_sections = []
            estimated_tokens = 0
            max_excerpt_tokens = 2000  # Reasonable limit for excerpts
            
            for section, score in scored_sections:
                section_tokens = self.token_estimator.estimate_tokens(section)
                if estimated_tokens + section_tokens <= max_excerpt_tokens:
                    selected_sections.append(section)
                    estimated_tokens += section_tokens
                else:
                    break
            
            if not selected_sections:
                # If no sections fit, return truncated content
                lines = content.split('\n')
                truncated_lines = lines[:100]  # First 100 lines
                return '\n'.join(truncated_lines) + '\n...[truncated]'
            
            return '\n\n'.join(selected_sections)
            
        except Exception as e:
            return f"# Error extracting excerpts from {file_path}: {str(e)}"
    
    def refresh_context_cache(self) -> CacheRefreshResult:
        """Refresh context cache and metadata"""
        
        try:
            # Clear old cache entries
            self.content_cache.clear_expired()
            
            # Update file metadata for changed files
            updated_files = []
            for file_path, metadata in self.metadata_cache.items():
                current_mtime = Path(file_path).stat().st_mtime
                if current_mtime > metadata.last_modified:
                    updated_metadata = self._get_file_metadata(Path(file_path))
                    self.metadata_cache[file_path] = updated_metadata
                    updated_files.append(file_path)
            
            return CacheRefreshResult(
                success=True,
                files_updated=len(updated_files),
                cache_entries_cleared=self.content_cache.get_cleared_count(),
                updated_files=updated_files
            )
            
        except Exception as e:
            return CacheRefreshResult(
                success=False,
                error=f"Cache refresh failed: {str(e)}"
            )

# === Supporting Classes ===

class TokenEstimator:
    """Estimate token count for content"""
    
    def estimate_tokens(self, content: str) -> int:
        """Estimate token count using simple heuristics"""
        # Rough approximation: 1 token ≈ 4 characters for English text
        # Adjust for code (more structured) vs prose (more varied)
        
        if not content:
            return 0
        
        # Basic character count
        char_count = len(content)
        
        # Adjust for content type
        if self._is_code_content(content):
            # Code is typically more token-dense
            return int(char_count / 3.5)
        else:
            # Natural language text
            return int(char_count / 4)
    
    def _is_code_content(self, content: str) -> bool:
        """Heuristically determine if content is code"""
        code_indicators = ['{', '}', '(', ')', ';', 'def ', 'class ', 'function', 'import ', 'from ']
        code_count = sum(1 for indicator in code_indicators if indicator in content)
        return code_count >= 3

class RelevanceScorer:
    """Score file relevance for given tasks"""
    
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights
    
    def calculate_relevance(self, file_path: Path, task: AutonomousTask) -> float:
        """Calculate relevance score for file given task"""
        
        relevance_factors = {
            'path_match': self._calculate_path_match(file_path, task),
            'content_keywords': self._calculate_keyword_match(file_path, task),
            'file_type_relevance': self._calculate_file_type_relevance(file_path, task),
            'recent_modification': self._calculate_recency_factor(file_path)
        }
        
        # Weighted sum of relevance factors
        total_score = sum(
            factor_score * self.weights.get(factor_name, 1.0)
            for factor_name, factor_score in relevance_factors.items()
        )
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, total_score))
    
    def _calculate_path_match(self, file_path: Path, task: AutonomousTask) -> float:
        """Calculate how well file path matches task requirements"""
        # Implementation details for path matching logic
        pass

# === Data Classes for Results ===

@dataclass
class ContextLoadResult:
    """Result of context loading operation"""
    success: bool
    context_data: Dict[str, str]
    total_tokens: int
    files_loaded: int = 0
    strategy_used: Optional[LoadingStrategy] = None
    optimization_applied: bool = False
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

@dataclass  
class OptimizedContext:
    """Optimized context with metadata"""
    context_data: Dict[str, str]
    total_tokens: int
    files_loaded: int
    strategy_used: LoadingStrategy
    optimization_applied: bool
    metadata: Dict[str, Any]

@dataclass
class FileLoadResult:
    """Result of loading individual file"""
    success: bool
    content: str
    estimated_tokens: int
    strategy_applied: LoadingStrategy
    file_path: Path
    error: Optional[str] = None

# This pseudocode implements the smart context loading system with intelligent
# token management, relevance scoring, and multiple loading strategies to work
# within Claude Code's context limits while maximizing useful information.