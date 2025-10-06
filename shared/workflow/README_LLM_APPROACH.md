# LLM-Based Autonomous Discovery Analysis

## The Problem with Keyword Scoring

The original `discovery_classifier.py` uses keyword counting:
- Counts words like "error", "fail", "blocked"
- Misses context (e.g., "error handling" vs actual errors)
- Can't understand relationships or implications
- Treats all "errors" equally regardless of severity

## The LLM-Intelligence Approach

### How It Works in Autonomous Claude Code

When Claude Code runs autonomously, it can directly:

1. **Read and Understand** - Claude reads discovery files and understands their actual meaning
2. **Assess Impact** - Claude determines real impact based on understanding, not keywords
3. **Make Decisions** - Claude decides workflow actions based on comprehension

### Example: How Claude Would Analyze

Instead of counting keywords, Claude would understand:

```markdown
# Discovery: Hook Investigation Failed

We discovered that Claude Code hooks aren't triggering. This blocks 
our entire automation approach but we have a workaround using 
standalone tools.
```

**Keyword Approach Would Say**: "CRITICAL! Contains 'failed' and 'blocks'!"

**Claude's Intelligence Would Understand**: 
- "This is a setback but not blocking because there's a workaround"
- "The standalone tools solution means we can continue"
- "This is MAJOR (needs design change) not CRITICAL (completely blocked)"

### Implementation in Autonomous Workflow

```python
# In autonomous execution, Claude would:

def claude_analyzes_discovery(file_path, content):
    """
    Claude reads and understands the content directly.
    No keyword counting - just comprehension.
    """
    
    # Claude understands:
    # - Is this describing a problem or documenting a solution?
    # - Does this block the current work?
    # - Is this a hypothesis or a confirmed issue?
    # - What's the actual severity based on project context?
    
    # Claude returns its understanding:
    return {
        "level": "major",  # Claude determines based on understanding
        "reasoning": "Hooks don't work but workaround exists",
        "is_blocking": False,  # Claude knows workaround prevents blocking
        "workflow_impact": "continue"  # Can proceed with standalone tools
    }
```

### The Key Difference

**Keyword Scoring**:
- Mechanical counting
- No context understanding
- False positives/negatives
- Can't assess real impact

**LLM Intelligence**:
- Understands meaning
- Considers context
- Assesses actual impact
- Makes nuanced decisions

### How This Integrates with Workflow

1. **Discovery Created** → File saved in `investigations/`
2. **Claude Analyzes** → Reads and understands content
3. **Classification** → Based on understanding, not keywords
4. **Workflow Decision** → Intelligent decision on whether to halt/continue

### Practical Autonomous Execution

During autonomous workflow, Claude would:

```bash
# Claude runs workflow orchestrator
python3 tools/workflow/workflow_orchestrator.py

# Claude sees it needs to check discoveries
# Instead of keyword scoring, Claude:
# 1. Reads each discovery file
# 2. Understands the actual content
# 3. Assesses real impact on project
# 4. Makes intelligent classification

# Claude's internal process (not code, but reasoning):
"This discovery about broken references... let me understand:
- 123 broken references exist
- They're in documentation, not code
- The pre-commit hook catches them
- This doesn't block implementation
- Classification: MINOR, continue workflow"
```

### Benefits for Autonomous Operation

1. **No Human Intervention Needed** - Claude understands context itself
2. **Accurate Classifications** - Based on meaning, not word frequency
3. **Adaptive Decisions** - Considers project state and phase
4. **Reduced False Alarms** - Won't halt for non-blocking issues

### Migration Path

To switch from keyword to LLM approach:

1. **Keep Structure** - Same workflow integration
2. **Replace Scoring** - Remove keyword counting
3. **Add Understanding** - Claude analyzes content directly
4. **Trust Intelligence** - Let Claude's comprehension guide decisions

The key insight: **Claude is already intelligent - we should use that intelligence directly rather than reducing everything to keyword counting.**

## Example Classifications by Claude

Here's how Claude would classify discoveries intelligently:

| Discovery | Keyword Score | Claude's Understanding | Claude's Classification |
|-----------|--------------|----------------------|------------------------|
| "Error handling implemented" | HIGH (has "error") | Describes solution, not problem | INFORMATIONAL |
| "Build fails on import" | HIGH (has "fails") | Actual blocking issue | CRITICAL |
| "Consider refactoring auth" | MEDIUM (has "refactor") | Future optimization | MINOR |
| "Security audit passed" | HIGH (has "security") | Positive result | INFORMATIONAL |
| "Blocked by API rate limits" | HIGH (has "blocked") | Real blocker if no solution | CRITICAL |
| "Blocked by API rate limits (using cache as workaround)" | HIGH (has "blocked") | Has workaround | MAJOR |

The LLM approach understands **context and implications**, not just word presence.