Major roadmap overhaul when discoveries invalidate current plans:

## Roadmap Reassessment Process

When major discoveries require fundamental changes to the project approach.

### 1. Document What Changed
**Triggering Discovery:**
- What was discovered that invalidates current plans?
- Why wasn't this known earlier?
- How does this affect the project fundamentally?

**Impact Assessment:**
- Which phases are affected?
- What work becomes unnecessary?
- What new work is now required?
- Are the MVP goals still achievable?

### 2. Reassess Project Goals
**Original Goals Review:**
- Can we still achieve the original MVP objectives?
- Do we need to reduce scope?
- Should we pivot to a different approach?
- Is the timeline still realistic?

### 3. Design New Approach
**Architecture Changes:**
- What architectural changes are needed?
- Which components need redesign?
- What technical debt must be addressed first?

**New Phase Structure:**
- What phases should be added/removed/reordered?
- What are the new dependencies between phases?
- What investigations are needed before proceeding?

### 4. Update Roadmap Documents

**`/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md` Updates:**
- Archive current roadmap section with explanation
- Create new roadmap section with revised phases
- Update timelines and priorities
- Document why the change was necessary

**Create/Update Phase Files:**
- Archive obsolete phase files
- Create new phase files for new approach
- Update existing phase files with new context

### 5. Risk Mitigation
**New Risks Identified:**
- What new risks does the revised approach introduce?
- What fallback options exist?
- How can we validate the new approach early?

**Create Investigation Tasks:**
- What unknowns need investigation?
- What prototypes would reduce risk?
- What can be tested before full commitment?

### 6. Update `/home/brian/projects/autocoder4_cc/CLAUDE.md`
Clear current plans and add:
```markdown
## 🔄 ROADMAP REASSESSMENT IN PROGRESS

**Trigger**: [What caused the reassessment]
**Previous Approach**: [Brief summary of what we were doing]
**New Approach**: [Brief summary of new direction]

### Immediate Actions
1. [First investigation/prototype needed]
2. [Second critical task]
3. [Risk mitigation step]

### Success Criteria for New Approach
- [ ] [Validation that new approach will work]
- [ ] [Evidence that blocker is resolved]
```

### 7. Commit Reassessment
```bash
git add -A
git commit -m "REASSESS: Major roadmap change due to [discovery]

Trigger: [What was discovered]
Impact: [What this changes]
New approach: [Brief summary]

See /home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md for revised roadmap"

# Tag the pivot point
git tag reassessment-[date] -m "Major pivot due to [discovery]"
```


## Output
Document the reassessment results in:
- `/home/brian/projects/autocoder4_cc/evidence/current/Evidence_Reassessment_[date].md`
- Updated `/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md` with new roadmap
- Updated `/home/brian/projects/autocoder4_cc/CLAUDE.md` with new immediate actions