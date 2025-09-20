Sync plans with conversation context and validate accuracy. Add discussed issues to MVP_PLAN.md and verify completion claims match evidence.

## Core Actions

1. **Integrate Discussion**: Add newly discussed issues to MVP_PLAN.md
2. **Validate Claims**: Check completed tasks have supporting evidence
3. **Fix Contradictions**: Resolve inconsistencies between documents

## Integration

Based on conversation context, add discovered issues to appropriate sections:

**Immediate blockers** → Current phase tasks in MVP_PLAN.md
**Phase issues** → Current or next phase depending on urgency  
**Future improvements** → Post-MVP section

Use existing phase priority system, don't create new classification.

## Validation

Check key consistency points:
```bash
MVP_PLAN="/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md"
CLAUDE_FILE="/home/brian/projects/autocoder4_cc/CLAUDE.md"

# Verify completion claims have evidence
COMPLETE_TASKS=$(grep -E "✅ COMPLETE|\\[x\\]" "$MVP_PLAN" | wc -l)
EVIDENCE_FILES=$(ls /home/brian/projects/autocoder4_cc/evidence/current/Evidence_*.md 2>/dev/null | wc -l)

if [ "$COMPLETE_TASKS" -gt "$EVIDENCE_FILES" ]; then
    echo "⚠️ $COMPLETE_TASKS tasks marked complete but only $EVIDENCE_FILES evidence files"
    grep -E "✅ COMPLETE|\\[x\\]" "$MVP_PLAN" | head -3
fi

# Check file references work
grep -o '/home/brian/projects/autocoder4_cc/[^`]*' "$CLAUDE_FILE" | while read -r filepath; do
    if [ ! -f "$filepath" ] && [ ! -d "$filepath" ]; then
        echo "❌ Dead link: $filepath"
    fi
done

# Check phase files don't have status (should be status-neutral)
find /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/ -name "phase*.md" -exec grep -l "Status:\|ACTIVE\|BLOCKED" {} \; 2>/dev/null | head -3
```

## Commit Changes
```bash
git add /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md
git add /home/brian/projects/autocoder4_cc/evidence/current/
git add /home/brian/projects/autocoder4_cc/CLAUDE.md 2>/dev/null || true

git commit -m "Sync plans with discussion

Issues integrated: [brief list]
Validation: [OK/issues found]

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Success Criteria
- [ ] Discussion points added to appropriate planning documents
- [ ] Completion claims have supporting evidence files
- [ ] File references in CLAUDE.md work
- [ ] No status information in phase files
- [ ] Changes committed with summary

## Usage Notes
- **Conversation-driven**: Works with what was just discussed, not auto-discovery
- **Evidence-focused**: Ensures completion claims are backed by proof
- **Efficient**: Core validation in ~20 lines of bash, not 200+