Load next phase from MVP roadmap into CLAUDE.md after current phase completion verified. Archive current phase and setup new phase environment.

## Phase Transition Workflow

1. **Verify Phase Complete** - Check MVP_PLAN.md shows current phase done with evidence
2. **Identify Next Phase** - Find next PENDING/READY phase in roadmap  
3. **Archive Current Work** - Move evidence to archive with timestamp
4. **Generate New CLAUDE.md** - Create comprehensive phase context from phase files
5. **Setup Environment** - Initialize evidence tracking and debug directories
6. **Update Status** - Mark transition in MVP_PLAN.md
7. **Commit Changes** - Document transition in git

## Transition Execution

### 1. Verify Current Phase Complete
```bash
MVP_PLAN="/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md"
CURRENT_PHASE=$(grep -E "^### Phase.*\\(.*ACTIVE|CURRENT|PROGRESS" "$MVP_PLAN" | head -1)

# Check tasks marked complete
INCOMPLETE_TASKS=$(grep -A 20 "$CURRENT_PHASE" "$MVP_PLAN" | grep -E "^- \\[ \\]" | wc -l)
if [ "$INCOMPLETE_TASKS" -gt 0 ]; then
    echo "❌ $INCOMPLETE_TASKS incomplete tasks - complete current phase first"
    exit 1
fi

# Check evidence exists
EVIDENCE_COUNT=$(ls /home/brian/projects/autocoder4_cc/evidence/current/Evidence_*.md 2>/dev/null | wc -l)
if [ "$EVIDENCE_COUNT" -eq 0 ]; then
    echo "❌ No evidence files - cannot verify completion"
    exit 1
fi
```

### 2. Identify Next Phase
```bash
NEXT_PHASE=$(grep -E "^### Phase.*\\(.*PENDING|READY|NEXT" "$MVP_PLAN" | head -1)
if [ -z "$NEXT_PHASE" ]; then
    echo "❌ No next phase found in MVP_PLAN.md"
    exit 1
fi

# Extract phase details
PHASE_NUM=$(echo "$NEXT_PHASE" | grep -o "Phase [0-9]\\+\\.[0-9]\\+" | head -1)
PHASE_NAME=$(echo "$NEXT_PHASE" | sed 's/^### Phase [0-9]\+\.[0-9]\+: //' | sed 's/ (.*//')

# Find phase file
PHASE_FILE_PATTERN=$(echo "$PHASE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
PHASE_FILE=$(find /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/ -name "*${PHASE_FILE_PATTERN}*.md" | head -1)

if [ -z "$PHASE_FILE" ]; then
    echo "❌ Phase file not found for: $PHASE_NAME"
    exit 1
fi
```

### 3. Archive Current Phase
```bash
ARCHIVE_DATE=$(date +%Y%m%d_%H%M%S)
CURRENT_PHASE_CLEAN=$(echo "$CURRENT_PHASE" | sed 's/^### //' | tr ' ' '_' | tr -d '()')
ARCHIVE_DIR="/home/brian/projects/autocoder4_cc/archive/${ARCHIVE_DATE}_${CURRENT_PHASE_CLEAN}"

mkdir -p "$ARCHIVE_DIR/evidence"
cp /home/brian/projects/autocoder4_cc/CLAUDE.md "$ARCHIVE_DIR/CLAUDE_previous_phase.md"
mv /home/brian/projects/autocoder4_cc/evidence/current/* "$ARCHIVE_DIR/evidence/" 2>/dev/null || true

cat > "$ARCHIVE_DIR/ARCHIVAL_REASON.md" << EOF
# Phase Completion Archive

**Archive Date**: $(date)
**Phase Completed**: $CURRENT_PHASE
**Next Phase**: $NEXT_PHASE
**Status**: Phase transition - all tasks marked complete

## Archive Contents
- CLAUDE_previous_phase.md - Previous phase instructions
- evidence/ - All evidence files from completed phase

## Integration Notes
Phase complete and archived. Next phase transition documented in git commit.
EOF
```

### 4. Generate New CLAUDE.md
```bash
CLAUDE_FILE="/home/brian/projects/autocoder4_cc/CLAUDE.md"

# Read phase file content
PHASE_CONTENT=$(cat "$PHASE_FILE")
NEXT_PHASE_TASKS=$(grep -A 50 "$NEXT_PHASE" "$MVP_PLAN" | sed '/^### Phase/,1d' | sed '/^### /,$d')

# Create comprehensive CLAUDE.md
cat > "$CLAUDE_FILE" << EOF
# CLAUDE.md - $PHASE_NAME

**Current Phase**: $PHASE_NUM - $PHASE_NAME
**Status**: ACTIVE - Started $(date +%Y-%m-%d)
**Reference**: $PHASE_FILE

---

## 🧠 CODING PHILOSOPHY

**Core Development Principles (NON-NEGOTIABLE)**:
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST AND LOUD PRINCIPLES**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files
- **DON'T EDIT GENERATED SYSTEMS**: Fix the autocoder itself, not generated outputs
- **VALIDATION + SELF-HEALING**: Every validator must have coupled self-healing capability
- **LLM CAPABILITY IS NOT THE PROBLEM**: Any issues with LLM output quality is caused by bad prompting not by limitations of the LLM
- **CLAUDE CODE OPTIMISM PROBLEM**: Do NOT claim success until 100% proven with evidence
- **TIMEOUTS DO NOT COUNT AS SUCCESS IN TESTING**: Do not declare success if the tests timeout

## ✅ SUCCESS VALIDATION PRINCIPLES

**Mandatory Success Criteria**:
- **NO SUCCESS WITHOUT END-TO-END PROOF**: Never declare success until the complete pipeline works from start to finish
- **DEPLOYABILITY GATE**: Code is only complete when it can be executed without errors in a clean environment
- **FAIL-FAST ON IMPORTS**: Any import error or missing dependency immediately invalidates success claims
- **EVIDENCE-BASED SUCCESS**: Success requires demonstrable proof, not just file generation or partial functionality
- **MANDATORY END-TO-END TESTING**: Every claimed solution must include a working example that runs without errors
- **CLEAN ENVIRONMENT VALIDATION**: Test in isolated environment to catch dependency issues
- **ACTUAL USE CASE VERIFICATION**: Don't just test that code exists - test that it accomplishes the stated objective
- **DISTINGUISH PROGRESS FROM COMPLETION**: Clearly separate "made progress" from "achieved objective"
- **NO VICTORY LAPS**: Avoid celebratory language until complete functionality is proven

---

## 🏗️ CODEBASE STRUCTURE

**AutoCoder** current state for $PHASE_NAME:
[To be filled from phase file context]

### Key Planning Documentation
- **MVP Master Plan**: \`/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md\` - Central task tracking and status
- **Phase Details**: \`$PHASE_FILE\` - Detailed implementation steps
- **Testing Strategy**: \`/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/testing_strategy/README.md\` - Dual framework testing approach
- **Current Evidence**: \`/home/brian/projects/autocoder4_cc/evidence/current/\` - Active investigation evidence
- **Completed Evidence**: \`/home/brian/projects/autocoder4_cc/evidence/completed/\` - Previous phase evidence (archived)

### Implementation Roadmap Integration (MANDATORY)
This CLAUDE.md follows the systematic implementation workflow:
- **Primary Status**: MVP_PLAN.md tracks all task completion status ($PHASE_NAME current)
- **Current Work**: $PHASE_NAME
- **Evidence Collection**: All investigation results documented with full visibility
- **Success Criteria**: No success without demonstrated end-to-end functionality

---

## 🧪 TESTING INTEGRATION

### When to Test (autonomous decisions)
- **Before**: Modifying core pipeline files → \`./run_core_tests.sh\` (baseline)
- **During**: Import/generation errors → \`python3 test_mvp_workflow.py\` (diagnose)  
- **After**: Implementing fixes → Re-run failing command (validate)
- **Completion**: Claiming task done → Create working example (prove)

### Core System Files (test when modifying):
\`blueprint_language/system_generator_refactored.py\`, \`llm_providers/prompt_manager.py\`, \`cli/main.py\`, \`components/registry.py\`, \`recipes/expander.py\`

### Test Evidence (always required):
\`\`\`bash
# Pattern for all testing:
[test_command] 2>&1 | tee "logs/debug_\$(date +%H%M%S)/[task].log"
# Create evidence/current/Evidence_[Task]_[Date].md with full output
\`\`\`

### Proof Standards:
- **Fix claims**: Must re-run previously failing command successfully
- **Feature claims**: Must demonstrate working end-to-end example
- **Phase completion**: Must create \`/tmp/phase_validation/\` with working system

---

## 🎯 CURRENT PHASE PRIORITIES

$NEXT_PHASE_TASKS

---

## 🔧 IMPLEMENTATION INSTRUCTIONS

[Implementation details from $PHASE_FILE]

$PHASE_CONTENT

---

## 📋 NEXT IMPLEMENTER INSTRUCTIONS

1. **Start with first task** - Begin implementation following phase file details
2. **Follow evidence-based development** - create evidence files for all testing
3. **Use exact commands provided** - capture full output visibility
4. **Reference detailed implementation** - see \`$PHASE_FILE\` for complete technical details
5. **Update MVP_PLAN.md status** - mark completed tasks as ✅ COMPLETE
6. **Verify success criteria** - no success without end-to-end proof

### Critical Files for Reference
- **This file**: Immediate implementation instructions
- **MVP_PLAN.md**: Status tracking and task organization  
- **$PHASE_FILE**: Complete technical implementation details
- **testing_strategy/README.md**: Testing framework usage guide

---

**Previous Phase**: ✅ COMPLETE - $CURRENT_PHASE archived  
**Current Phase**: 🚧 READY TO START - $PHASE_NAME  
**Evidence Required**: Full visibility with raw execution logs for all claims
EOF
```

### 5. Setup New Phase Environment
```bash
# Recreate evidence directory
mkdir -p /home/brian/projects/autocoder4_cc/evidence/current

# Create initial evidence file
PHASE_CLEAN=$(echo "$PHASE_NAME" | tr ' ' '_')
EVIDENCE_FILE="/home/brian/projects/autocoder4_cc/evidence/current/Evidence_${PHASE_CLEAN}_$(date +%Y%m%d)_Started.md"

cat > "$EVIDENCE_FILE" << EOF
# $PHASE_NAME Evidence Log

**Date**: $(date)
**Phase**: $PHASE_NUM - $PHASE_NAME
**Status**: Started
**Reference**: $PHASE_FILE

## Phase Objectives
[From MVP_PLAN.md and phase file]

## Implementation Progress
- [ ] Phase environment setup complete
- [ ] First task identified and planned
- [ ] Evidence tracking initialized

## Work Log
$(date): Phase transition completed, environment setup

## Findings
[To be updated as work progresses]

## Testing Results
[To be updated with systematic framework and standard test suite results]

## Completion Status
- [ ] All phase objectives met
- [ ] End-to-end functionality verified
- [ ] Evidence documented with full visibility
EOF

# Create debug session directory
DEBUG_DIR="/home/brian/projects/autocoder4_cc/logs/debug_${PHASE_CLEAN}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_DIR"
```

### 6. Update MVP_PLAN.md Status
```bash
# Mark previous phase complete
sed -i "s/$CURRENT_PHASE/$CURRENT_PHASE (✅ COMPLETE - $(date +%Y-%m-%d))/" "$MVP_PLAN"

# Mark new phase active
sed -i "s/$NEXT_PHASE/$NEXT_PHASE (🚧 ACTIVE - Started $(date +%Y-%m-%d))/" "$MVP_PLAN"
```

### 7. Commit Phase Transition
```bash
git add /home/brian/projects/autocoder4_cc/CLAUDE.md
git add /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md
git add /home/brian/projects/autocoder4_cc/evidence/current/
git add /home/brian/projects/autocoder4_cc/archive/

git commit -m "PHASE TRANSITION: Start $PHASE_NAME

Previous: $CURRENT_PHASE ✅ COMPLETE
Current: $NEXT_PHASE 🚧 ACTIVE

Archive: $ARCHIVE_DIR
Phase File: $PHASE_FILE
Evidence: $EVIDENCE_FILE
Debug: $DEBUG_DIR

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Success Criteria
- [ ] Current phase completion verified with evidence
- [ ] Next phase identified and validated
- [ ] Previous phase evidence archived with documentation
- [ ] CLAUDE.md contains complete new phase context with mandatory sections
- [ ] MVP_PLAN.md status correctly updated (previous COMPLETE, new ACTIVE)
- [ ] Evidence tracking initialized for new phase
- [ ] Debug environment prepared
- [ ] Git commit documents transition comprehensively

## Usage Notes
- **Evidence-Based**: Requires proof of completion before transition
- **Comprehensive**: New CLAUDE.md is self-contained for fresh LLM
- **Archival**: Previous work preserved with clear documentation
- **Status Management**: Only MVP_PLAN.md contains status information
- **Technical Context**: Phase files provide complete implementation guidance