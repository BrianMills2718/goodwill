Close current phase after completion validation and determine next steps

## Phase Closure Workflow

After /doublecheck confirms all tasks are done, this command handles complete phase closure:

### 1. Archive Completed Work
**Update `/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md`:**
- Mark current phase as ✅ COMPLETE with timestamp
- Update completion time and actual vs estimated duration
- Add achievement summary with key learnings

**Archive Evidence Files:**
```bash
# Move current phase evidence to completed archive
mv /home/brian/projects/autocoder4_cc/evidence/current/Evidence_Phase*_*.md \
   /home/brian/projects/autocoder4_cc/evidence/completed/
```

### 2. Review Learnings & Validate Approach
**Assess What Was Learned:**
- What unexpected issues were discovered?
- What assumptions proved incorrect?
- What new dependencies were identified?
- What technical debt was uncovered?

**Check Impact on Remaining Phases:**
Review each remaining phase in `/home/brian/projects/autocoder4_cc/docs/implementation_roadmap/mvp/MVP_PLAN.md`:
- [ ] Do the planned approaches still make sense?
- [ ] Are there new blockers that weren't known before?
- [ ] Have priorities shifted based on discoveries?
- [ ] Are time estimates still realistic?

**Check for Architecture Changes:**
- [ ] Did implementation reveal architectural issues?
- [ ] Are the component abstractions still appropriate?
- [ ] Do the planned integrations still work?

### 3. Create Git Checkpoint
```bash
git add -A
git commit -m "CLOSE: Phase [X] - [Brief description]

Achievements:
- [Key achievement 1]
- [Key achievement 2]

Learnings:
- [Key learning 1]
- [Key learning 2]

Evidence archived to evidence/completed/"

# Create git tag for known-good state
git tag phase-[X]-complete -m "Phase [X] completed and validated"
```

### 4. Decision Output

**DECISION: CONTINUE** (if approach still valid)
```
✅ Phase [X] closed successfully

Achievements:
- [What was completed]

Learnings that don't affect roadmap:
- [Minor adjustments noted]

Ready for: /load_next
```

**DECISION: REASSESS** (if major issues found)
```
⚠️ Phase [X] closed with concerns

Achievements:
- [What was completed]

Learnings that invalidate current approach:
- [Critical issue 1]
- [Blocker for next phase]

Required: /reassess_plans because [specific reason]
```

## Success Criteria
- [ ] Current phase marked COMPLETE in MVP_PLAN.md
- [ ] Evidence files moved to completed archive
- [ ] Learnings documented and assessed
- [ ] Git commit and tag created
- [ ] Clear decision: continue with /load_next OR reassess with /reassess_plans

## Example Usage
```
/close_phase Phase 3.1 LLM Timeout Investigation

Output:
✅ Phase 3.1 closed successfully

Achievements:
- Identified root cause of LLM timeout in asyncio layer
- Created reproducible test case
- Enhanced debugging infrastructure

Learnings that don't affect roadmap:
- Timeout was in HTTP client, not asyncio.wait_for
- litellm doesn't properly propagate timeouts

Ready for: /load_next (Phase 3.2: LLM Pipeline Fixes)
```