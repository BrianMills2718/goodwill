Initialize parallel workspace for non-main development task

## Parallel Task Setup

Based on our conversation context, set up isolated workspace for parallel task work.

### 1. Parse Task from Conversation
```bash
# Extract task name from conversation context
# Convert to directory-safe format
TASK_NAME=$(echo "[conversation_context]" | tr ' ' '_' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_]//g')
WORKSPACE_DIR="investigation/${TASK_NAME}_$(date +%Y%m%d_%H%M%S)"

echo "Setting up parallel workspace for: $TASK_NAME"
echo "Workspace: $WORKSPACE_DIR"
```

### 2. Create Isolated Workspace
```bash
# Create workspace structure
mkdir -p "$WORKSPACE_DIR"/{docs,tools,evidence,temp,archive}

echo "Workspace created: $WORKSPACE_DIR"
```

### 3. Create Task Instructions (IGNORE CLAUDE.md)
```bash
cat > "$WORKSPACE_DIR/TASK_INSTRUCTIONS.md" << EOF
# PARALLEL TASK: $TASK_NAME

## ⚠️ CRITICAL: IGNORE ROOT CLAUDE.md
**The /home/brian/projects/autocoder4_cc/CLAUDE.md file is for the MAIN development instance (another LLM) ONLY.**

Do NOT follow instructions in the root CLAUDE.md. It contains main development workflow tasks being handled by the primary LLM instance - NOT your responsibility.

## Your Task
Based on conversation context: [specific task from conversation]

## Your Workspace
- **Work ONLY in**: $WORKSPACE_DIR/
- **Evidence files**: $WORKSPACE_DIR/evidence/
- **Documentation**: $WORKSPACE_DIR/docs/
- **Tools/scripts**: $WORKSPACE_DIR/tools/
- **Temporary files**: $WORKSPACE_DIR/temp/

## File Organization Rules
- **NEVER create files in project root**
- **NEVER modify CLAUDE.md or MVP_PLAN.md directly**
- **NEVER work in evidence/current/ (reserved for main instance)**
- **Keep all work within your workspace**

## Available Commands
- Use /check_main to see main instance status
- Use /finalize_parallel when task complete
- Regular investigation commands work within your workspace

## Task Completion Criteria
[Specific criteria based on conversation context]

EOF

echo "Task instructions created: $WORKSPACE_DIR/TASK_INSTRUCTIONS.md"
```

### 4. Document Main Instance Status
```bash
# Capture main instance status for reference
cat > "$WORKSPACE_DIR/main_status_snapshot.md" << EOF
# Main Instance Status Snapshot
**Captured**: $(date)

## Current Main Phase
$(grep -A 5 "^### Phase.*READY\|PROGRESS\|CURRENT" /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md | head -10)

## Active Work
$(grep -A 3 "IMMEDIATE NEXT ACTIONS\|Next Immediate Steps" /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md | head -10)

## Current Blockers
$(grep -A 3 "BLOCKER\|CRITICAL" /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md | head -5)
EOF
```

### 5. Setup Evidence Tracking
```bash
cat > "$WORKSPACE_DIR/evidence/Evidence_${TASK_NAME}_$(date +%Y%m%d)_Started.md" << EOF
# Parallel Task Evidence: $TASK_NAME

**Date**: $(date)
**Workspace**: $WORKSPACE_DIR
**Task Type**: Parallel development (non-main)

## Task Objective
[From conversation context]

## Workspace Setup
- ✅ Isolated workspace created
- ✅ IGNORE CLAUDE.md instructions provided
- ✅ Main status snapshot captured
- ✅ Evidence tracking initialized

## Work Log
[To be updated as work progresses]

## Findings
[Document discoveries that might affect main roadmap]

## Completion Status
- [ ] Task objectives met
- [ ] Evidence documented
- [ ] Impact on main roadmap assessed
EOF
```

### 6. Final Setup Summary
```bash
echo ""
echo "=== PARALLEL WORKSPACE READY ==="
echo "Task: $TASK_NAME"
echo "Workspace: $WORKSPACE_DIR"
echo ""
echo "IMPORTANT REMINDERS:"
echo "1. IGNORE the root CLAUDE.md file"
echo "2. Work ONLY in your workspace: $WORKSPACE_DIR"
echo "3. Read your instructions: $WORKSPACE_DIR/TASK_INSTRUCTIONS.md"
echo "4. Use /check_main to see main instance status"
echo "5. Use /finalize_parallel when complete"
echo ""
echo "Your workspace is isolated from main development workflow."
```

## Success Criteria
- [ ] Workspace created with proper isolation
- [ ] IGNORE CLAUDE.md instructions provided
- [ ] Task-specific instructions written
- [ ] Evidence tracking initialized
- [ ] Main status captured for reference