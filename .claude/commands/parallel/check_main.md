Check main instance status (read-only)

## Main Instance Status Check

Get current status of main development instance without interfering.

```bash
MVP_PLAN="/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md"
CLAUDE_MD="/home/brian/projects/autocoder4_cc/CLAUDE.md"

# Main instance status
if [ -f "$MVP_PLAN" ]; then
    echo "=== MAIN INSTANCE STATUS ==="
    grep -E "^\*\*Status\*\*:" "$MVP_PLAN" | head -1
    
    echo -e "\n=== ACTIVE PHASE ==="
    grep -E "^### Phase.*\(.*READY|PROGRESS|CURRENT|ACTIVE" "$MVP_PLAN" | head -1
    
    echo -e "\n=== IMMEDIATE ACTIONS ==="
    grep -A 3 "IMMEDIATE\|Next Immediate\|Current Priority" "$MVP_PLAN" | head -5
else
    echo "❌ MVP_PLAN.md not accessible"
fi

# Current work
if [ -f "$CLAUDE_MD" ]; then
    echo -e "\n=== MAIN CURRENT WORK ==="
    grep -A 2 "^## 🎯|^## Current|^## Immediate" "$CLAUDE_MD" | head -4
    
    echo -e "\n=== PENDING TASKS ==="
    grep -E "^\- \[ \]|^[0-9]+\. \[ \]" "$CLAUDE_MD" | head -3
else
    echo -e "\n⚠️ No CLAUDE.md (main may be between phases)"
fi

# Recent activity
echo -e "\n=== RECENT MAIN EVIDENCE ==="
if [ -d "/home/brian/projects/autocoder4_cc/evidence/current" ]; then
    ls -t /home/brian/projects/autocoder4_cc/evidence/current/*.md 2>/dev/null | head -2 | xargs -I {} basename {} | cut -c1-50
else
    echo "No evidence directory"
fi

# Coordination advice
echo -e "\n=== COORDINATION ADVICE ==="
if [ -f "$MVP_PLAN" ]; then
    CURRENT_PHASE=$(grep -E "^### Phase.*\(.*ACTIVE|CURRENT" "$MVP_PLAN" | head -1)
    
    case "$CURRENT_PHASE" in
        *"3.2"*|*"validation"*) echo "⚠️ Main working on validation - avoid validation changes" ;;
        *"3.3"*|*"component"*) echo "⚠️ Main working on components - avoid component changes" ;;
        *"Docker"*|*"deploy"*) echo "⚠️ Main working on deployment - avoid deployment configs" ;;
        *) echo "✅ No obvious conflicts detected" ;;
    esac
    
    echo -e "\nSafe parallel work areas:"
    echo "  - Documentation improvements"
    echo "  - Investigation work"
    echo "  - Test improvements"
else
    echo "Cannot determine - MVP_PLAN.md not accessible"
fi

echo -e "\n=== SUMMARY FOR PARALLEL WORK ==="
echo "READ-ONLY status from main instance"
echo "Continue parallel work in isolated workspace"
echo "Use this info to avoid conflicts with main development"
echo "Next check: Run /check_main again when needed"
```

## Usage Notes

- **Read-only**: Does not modify any main instance files
- **Coordination**: Shows what main instance is working on
- **Conflict avoidance**: Identifies potential overlap areas
- **Status snapshot**: Current phase and immediate priorities only