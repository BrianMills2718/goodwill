Show current project status and orientation

## Quick Status Check

Display current phase, progress, and immediate next steps from MVP_PLAN.md and CLAUDE.md.

```bash
# Current phase and status
MVP_PLAN="/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md"
CLAUDE_MD="/home/brian/projects/autocoder4_cc/CLAUDE.md"

if [ -f "$MVP_PLAN" ]; then
    echo "=== MVP STATUS ==="
    grep -E "^\*\*Status\*\*:|^Status:" "$MVP_PLAN" | head -1
    
    echo -e "\n=== ACTIVE PHASE ==="
    grep -E "^### Phase [0-9].*\(.*CURRENT|ACTIVE|READY" "$MVP_PLAN" | head -1
    
    echo -e "\n=== TASK PROGRESS ==="
    COMPLETED=$(grep -c "^\- \[x\]" "$MVP_PLAN" 2>/dev/null || echo 0)
    PENDING=$(grep -c "^\- \[ \]" "$MVP_PLAN" 2>/dev/null || echo 0)
    echo "Completed: $COMPLETED, Pending: $PENDING"
else
    echo "❌ MVP_PLAN.md not found"
fi

if [ -f "$CLAUDE_MD" ]; then
    echo -e "\n=== CURRENT WORK ==="
    grep -A 3 "^## 🎯 CURRENT\|^## Current Priority\|^## Immediate" "$CLAUDE_MD" | head -6
    
    echo -e "\n=== NEXT TASKS ==="
    grep -E "^\- \[ \]|^[0-9]+\. \[ \]" "$CLAUDE_MD" | head -3
else
    echo -e "\n⚠️ No CLAUDE.md - run /load_next_phase or /update_plans"
fi

# Recent evidence
echo -e "\n=== RECENT EVIDENCE ==="
if [ -d "/home/brian/projects/autocoder4_cc/evidence/current" ]; then
    ls -t /home/brian/projects/autocoder4_cc/evidence/current/Evidence_*.md 2>/dev/null | head -3 | xargs -I {} basename {} | sed 's/Evidence_//' | sed 's/_[0-9]*.md//'
else
    echo "No evidence directory"
fi

# Show blockers if any
echo -e "\n=== KNOWN BLOCKERS ==="
if [ -f "$MVP_PLAN" ]; then
    grep -A 1 -E "BLOCKER|BLOCKED|P0.*Critical" "$MVP_PLAN" | head -3 || echo "None found"
else
    echo "Cannot check - MVP_PLAN.md missing"
fi

# Quick recommendations
echo -e "\n=== RECOMMENDED ACTIONS ==="
if [ -f "$CLAUDE_MD" ]; then
    if grep -q "CURRENT\|Priority\|Immediate" "$CLAUDE_MD"; then
        echo "✅ Continue current work in CLAUDE.md"
    else
        echo "⚠️ Run /update_plans to refresh current tasks"
    fi
else
    echo "🔄 Run /load_next_phase to setup current phase"
fi

# Show if debugging is active
if [ -d "/home/brian/projects/autocoder4_cc/logs" ]; then
    RECENT_DEBUG=$(find /home/brian/projects/autocoder4_cc/logs -name "debug_*" -mtime -1 2>/dev/null | wc -l)
    if [ "$RECENT_DEBUG" -gt 0 ]; then
        echo "🔍 $RECENT_DEBUG recent debug sessions found"
    fi
fi
```

## Usage Notes

- **Quick orientation** without deep context loading
- **Shows priorities** from both MVP_PLAN.md and CLAUDE.md  
- **Task counts** give progress sense
- **Blockers highlighted** if present
- **Actionable recommendations** based on current state