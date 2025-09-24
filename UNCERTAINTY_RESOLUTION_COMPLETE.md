# Complete Uncertainty Resolution for V4 Autonomous System

## 1. Tool Integration Points ✅

### Current State Analysis:
- ✅ `evidence_validator.py` exists and works - validates evidence against schema
- ❌ `state_reconciliation.py` does NOT exist - needs to be created
- ✅ `workflow_orchestrator.py` exists - handles state management from CLAUDE.md
- ❌ LLM integration for evidence analysis not implemented

### Required Implementation:

#### A. Create `state_reconciliation.py`:
```python
#!/usr/bin/env python3
"""
State Reconciliation - Validates claimed vs actual project state
Called from PostToolUse hooks to detect automation problems
"""
class StateReconciler:
    def check_claimed_vs_actual(self, claimed_evidence, actual_files):
        # Use LLM to compare claimed progress vs actual file state
        # Return automation_health: "good" | "warning" | "failing"
        pass
```

#### B. Enhance `evidence_validator.py` with LLM analysis:
- Add `analyze_with_llm(evidence_data)` method
- Call LLM to determine if evidence represents real progress
- Return confidence scores and gap identification

#### C. Hook Configuration:
```json
{
  "hooks": {
    "PostToolUse": [{
      "hooks": [{
        "type": "command",
        "command": "python3 tools/workflow/evidence_validator.py --llm-analyze"
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command", 
        "command": "python3 tools/workflow/workflow_orchestrator.py --next-command"
      }]
    }]
  }
}
```

## 2. State Management ✅

### Current State Analysis:
- ✅ `workflow_orchestrator.py` reads CLAUDE.md workflow state
- ❌ Loop counters (`loop_iterations`, `stop_hook_count`) not tracked
- ❌ JSON state format not fully defined in CLAUDE.md

### Required Implementation:

#### A. CLAUDE.md State Format:
```markdown
## Workflow State
```json
{
  "current_phase": "phase_1_foundation",
  "current_command": "/implement",
  "loop_iterations": 3,
  "stop_hook_count": 1,
  "test_status": "passing",
  "confidence": "high",
  "automation_health": "good",
  "last_updated": "2025-09-24T15:30:00Z"
}
```

#### B. State Persistence:
- `workflow_orchestrator.py` updates both `.claude/workflow_state.json` AND CLAUDE.md
- Loop counters increment on each uncertainty resolution cycle
- Stop hook counter increments on each Stop hook call
- Reset counters on successful phase transitions

## 3. Real vs Test Environment ✅

### Current Project State:
- ✅ Phase 1.1 complete (Goodwill scraper with 11/11 tests passing)
- 🔄 Phase 1.2: eBay API Setup (clear success criteria needed)
- 🔄 Phase 1.3: Technical Infrastructure  
- 🔄 Phase 1.4: Keyword Research

### Phase 1.2 Success Criteria (eBay API Setup):
```json
{
  "required_evidence": {
    "api_credentials": "eBay API keys obtained and configured",
    "test_connection": "Successful API connection test with rate limiting",
    "sold_listings_fetch": "Fetch 50+ sold listings for sample items",
    "data_structure": "Parse eBay data into comparable format with Goodwill",
    "integration_tests": "Tests passing for eBay API integration"
  },
  "completion_criteria": {
    "coverage": ">=80%",
    "tests_passing": "100%", 
    "confidence": "high",
    "integration": "Goodwill + eBay data can be compared"
  }
}
```

### Testing Strategy:
1. **Sandbox Mode**: Create `--sandbox` flag for workflow_orchestrator.py
2. **Test Phase**: Create synthetic Phase 1.5 for testing autonomous system
3. **Real Work Validation**: Test on actual Phase 1.2 with clear rollback plan

## 4. Emergency Controls ✅

### Manual Override System:
```bash
# Emergency stop - create override file
echo "MANUAL_MODE" > .claude/workflow_override
# Autonomous system checks this file and stops

# Resume automation - remove override file  
rm .claude/workflow_override
```

### Automation Health Detection:
```python
def detect_automation_health(evidence_history, loop_count):
    """
    Returns: "good" | "warning" | "failing"
    
    "failing" conditions:
    - Same evidence repeated 3+ times
    - Loop count > 5 with no phase progress
    - Test failures increasing over time
    - Git status showing no meaningful changes
    """
```

### Emergency Stop Triggers:
- `stop_hook_count >= 3` → Force manual mode
- `loop_iterations >= 7` → Escalate to deferred  
- `automation_health == "failing"` → Request human intervention
- `.claude/workflow_override` file exists → Stop all automation

## 5. Evidence Standards ✅

### High Confidence Criteria:
```json
{
  "phase_completion": {
    "required": {
      "all_tests_passing": true,
      "coverage_percentage": ">=80%",
      "implementation_complete": true,
      "git_committed": true,
      "evidence_validated": true
    },
    "confidence_levels": {
      "high": "All required + LLM validation confirms real progress",
      "medium": "All required but minor gaps identified",
      "low": "Missing required evidence or contradictions found"
    }
  }
}
```

### LLM Progress Validation:
```python
def validate_real_progress(claimed_evidence, project_files):
    """
    LLM analyzes:
    - Does evidence match actual file changes?
    - Are test results legitimate (not just passing but meaningful)?
    - Is implementation complete or just scaffolding?
    - Does work advance the project goal or just create busywork?
    
    Returns: confidence_score, gap_analysis, recommendations
    """
```

### eBay API Evidence Example:
```json
{
  "phase": "1.2_ebay_api_setup",
  "api_credentials": {
    "app_id": "configured",
    "client_secret": "configured_securely",
    "sandbox_tested": true
  },
  "test_connection": {
    "status": "successful",
    "rate_limit": "5 calls/second implemented",
    "error_handling": "comprehensive"
  },
  "sold_listings_fetch": {
    "sample_queries": ["iPhone 13", "Nike shoes", "Vintage camera"],
    "listings_retrieved": 157,
    "data_structure": "standardized format matching Goodwill"
  },
  "integration_proof": {
    "comparison_test": "Goodwill vs eBay price comparison working",
    "arbitrage_detection": "Basic logic implemented",
    "confidence": "high"
  }
}
```

## Implementation Order:

1. **Create `state_reconciliation.py`** - Basic automation health detection
2. **Enhance CLAUDE.md state format** - Add loop counters and health tracking  
3. **Define Phase 1.2 success criteria** - Clear eBay API completion requirements
4. **Create manual override system** - Emergency stop via file-based control
5. **Add LLM integration to evidence_validator.py** - Real progress validation
6. **Test with Phase 1.2** - Real work with rollback capability

All major uncertainties now have concrete implementation specifications.