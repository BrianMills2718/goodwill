# Goodwill Arbitrage Project - Automated Workflow

## Integrated Slash Command + Hook Workflow

### Mermaid Diagram

```mermaid
flowchart TD
    %% Session Start
    A[SessionStart Hook] --> B[Load Project Context<br/>- Current phases.md status<br/>- Active errors from CLAUDE.md<br/>- Investigation findings<br/>- Cross-reference validation]
    
    B --> C[MAIN WORKFLOW LOOP]
    
    %% Main Workflow
    C --> D{User Action}
    
    %% Manual Slash Commands
    D -->|Manual| E["/investigate:discovery<br/>Structured investigation"]
    D -->|Manual| F["/phase:update_plans<br/>Sync documentation"]
    D -->|Manual| G["/validate:project<br/>Check consistency"]
    D -->|Manual| H["/status:current<br/>Project orientation"]
    
    %% Investigation Flow
    E --> I[Create findings in<br/>investigations/[area]/]
    I --> J[PostToolUse Hook<br/>Discovery Detection]
    J --> K{Major Discovery?}
    
    K -->|Yes| L[Auto-trigger<br/>/phase:update_plans logic]
    K -->|No| M[Continue current work]
    
    %% Plan Update Flow
    F --> N[Read phases.md status]
    L --> N
    N --> O[Read relevant phase files]
    O --> P[Update CLAUDE.md with<br/>new plans + evidence]
    P --> Q[Mark verified completions<br/>in phases.md]
    Q --> R[Validate cross-references]
    
    %% Validation Flow
    G --> S[tools/validate_references.py]
    R --> S
    S --> T{Issues Found?}
    T -->|Yes| U[Auto-inject errors<br/>into CLAUDE.md]
    T -->|No| V[Continue workflow]
    
    %% Status Flow
    H --> W[Quick project health<br/>- Phase progress<br/>- Active errors<br/>- Recent discoveries]
    
    %% Continuous Automation Hooks
    X[PreToolUse Hook<br/>File Modification] --> Y[Load context with<br/>tools/load_context.py]
    Y --> Z[Validate operation]
    Z --> AA{Allow?}
    AA -->|Yes| BB[Execute operation]
    AA -->|No| CC[Block with feedback]
    
    BB --> DD[PostToolUse Hook<br/>Auto-maintenance]
    DD --> EE[Update cross-references]
    EE --> FF[Detect new discoveries]
    FF --> GG{Discovery Found?}
    GG -->|Yes| J
    GG -->|No| HH[Continue]
    
    %% Stop Hook Orchestration
    M --> II[Stop Hook<br/>Workflow Orchestration]
    V --> II
    W --> II
    HH --> II
    
    II --> JJ{Phase Complete?}
    JJ -->|Yes| KK[Archive evidence<br/>Load next phase]
    JJ -->|No| LL{Major Issues?}
    
    LL -->|Yes| MM[Auto-trigger<br/>/investigate:discovery]
    LL -->|No| NN[Session ready<br/>for next user action]
    
    KK --> NN
    MM --> E
    NN --> C
    
    %% Error Handling
    U --> OO[tools/inject_error.py<br/>Structured error logging]
    CC --> OO
    OO --> PP[Update CLAUDE.md<br/>🚨 ACTIVE ERRORS section]
    PP --> NN
    
    %% Evidence Flow
    I -.-> QQ[investigations/[area]/findings.md]
    KK -.-> RR[Archive to<br/>investigations/[area]/archive_YYYYMMDD/]
    
    classDef slashCommand fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef hookEvent fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef automationTool fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef evidenceFile fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef decisionPoint fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    
    class E,F,G,H slashCommand
    class A,J,DD,II,X hookEvent
    class S,Y,OO automationTool
    class QQ,RR evidenceFile
    class D,K,T,AA,GG,JJ,LL decisionPoint
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     GOODWILL ARBITRAGE - AUTOMATED WORKFLOW                    │
└─────────────────────────────────────────────────────────────────────────────────┘

SessionStart Hook: Load phases.md status into CLAUDE.md
│
▼
┌──────────────────────┐
│   Load Phase Plans   │
│   into CLAUDE.md     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  WITHIN-PHASE LOOP   │◄────────────────────────────────┐
│                      │                                 │
│  ┌─────────────────┐ │                                 │
│  │  /investigate   │ │                                 │
│  │ Execute current │ │                                 │
│  │ phase plans     │ │                                 │
│  └─────────┬───────┘ │                                 │
│            │         │                                 │
│  ┌─────────▼───────┐ │                                 │
│  │  /validate      │ │                                 │
│  │ Verify what was │ │                                 │
│  │ actually done   │ │                                 │
│  └─────────┬───────┘ │                                 │
│            │         │                                 │
│         ┌──▼──┐      │                                 │
│         │Done?│──No──┼──┐                              │
│         └──┬──┘      │  │                              │
│            │Yes      │  │                              │
│            │         │  ▼                              │
│            │         │  ┌─────────────────┐            │
│            │         │  │   /status       │            │
│            │         │  │ Plan for issues │            │
│            │         │  │ found in        │            │
│            │         │  │ validation      │            │
│            │         │  └─────────┬───────┘            │
│            │         │            │                    │
│            │         │  ┌─────────▼───────┐            │
│            │         │  │/phase:update    │            │
│            │         │  │Update CLAUDE.md │            │
│            │         │  │with new plans   │────────────┘
│            │         │  └─────────────────┘
│            │         │
└────────────┼─────────┘
             │
             ▼
┌────────────────────────┐
│    /phase:complete     │
│ • Archive evidence     │
│ • Mark ✅ in phases.md │
│ • Review learnings     │
│ • Validate approach    │
└────────────┬───────────┘
             │
          ┌──▼──┐
          │Good?│──No──┐
          └──┬──┘      │
             │Yes      │
             ▼         │
┌────────────────────────┐ │
│   Load next phase      │ │
│ from phases.md into    │ │
│ CLAUDE.md              │ │
└────────────┬───────────┘ │
             │             │
             ▼             │
        ┌─ Continue ─┐     │
        │ with next  │     │
        │   phase    │     │
        └────────────┘     │
                           │
             ┌─────────────▼─────────────┐
             │    /reassess_plans        │
             │ • Major plan overhaul     │
             │ • Rework roadmap strategy │
             │ • Update phases.md        │
             └─────────────┬─────────────┘
                           │
                           ▼
                     ┌─ Load New ─┐
                     │   Plans    │
                     │into CLAUDE │
                     └────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATIC DISCOVERY DETECTION HOOKS                         │
└─────────────────────────────────────────────────────────────────────────────────┘

PostToolUse Hook Triggers:
│
├─ Write/Edit to investigations/*/findings.md ─► discovery_detector.py
├─ Task completion (subagent finish) ──────────► discovery_detector.py  
├─ Error injection to CLAUDE.md ───────────────► discovery_detector.py
└─ Phase file modifications ───────────────────► discovery_detector.py
│
▼
┌─────────────────────────┐
│   discovery_detector.py │
│ • Scan investigations/  │
│ • Parse new findings    │
│ • Analyze impact scope  │
│ • Classify discovery    │
└─────────┬───────────────┘
          │
   ┌──────▼──────┐
   │   Major     │
   │ Discovery?  │──No─┐
   └──┬──────────┘     │
      │Yes             │
      ▼                ▼
┌─────────────────────┐  ┌─────────────────────────┐
│  Auto-trigger       │  │  Auto-trigger           │
│  /reassess_plans    │  │  /phase:update_plans    │
│ • Rework roadmap    │  │ • Add to existing plan  │
│ • Change strategy   │  │ • Update phases.md      │
│ • Update phases.md  │  │ • Continue workflow     │
└─────────┬───────────┘  └─────────┬───────────────┘
          │                        │
          ▼                        ▼
┌─────────────────────┐  ┌─────────────────────────┐
│   Load new plans    │  │   Continue current      │
│   into CLAUDE.md    │  │   workflow with new     │
└─────────────────────┘  │   issues integrated     │
          │              └─────────┬───────────────┘
          ▼                        │
    ┌─ Back to ─┐                  │
    │Within-Phase│◄─────────────────┘
    │   Loop     │
    └───────────┘

Stop Hook Triggers:
│
├─ End of /investigate command ────► workflow_orchestrator.py
├─ End of /validate command ──────► workflow_orchestrator.py
├─ End of /status command ────────► workflow_orchestrator.py
└─ End of any major operation ────► workflow_orchestrator.py
│
▼
┌─────────────────────────────┐
│   workflow_orchestrator.py  │
│ • Check for new discoveries │
│ • Assess phase completion   │
│ • Trigger appropriate flow  │
└─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                      HOOK CONFIGURATION & TRIGGERS                             │
└─────────────────────────────────────────────────────────────────────────────────┘

.claude/settings.json:
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "command": "$CLAUDE_PROJECT_DIR/tools/load_project_context.py" }] }
    ],
    "PreToolUse": [
      { 
        "matcher": "Edit|Write|MultiEdit", 
        "hooks": [{ "command": "$CLAUDE_PROJECT_DIR/tools/validate_references.py --pre-edit" }]
      }
    ],
    "PostToolUse": [
      { 
        "matcher": "Edit|Write|MultiEdit", 
        "hooks": [{ "command": "$CLAUDE_PROJECT_DIR/tools/discovery_detector.py" }]
      },
      { 
        "matcher": "Task", 
        "hooks": [{ "command": "$CLAUDE_PROJECT_DIR/tools/discovery_detector.py" }]
      }
    ],
    "Stop": [
      { "hooks": [{ "command": "$CLAUDE_PROJECT_DIR/tools/workflow_orchestrator.py" }] }
    ]
  }
}

Hook Execution Flow:
PreToolUse Hook:                    PostToolUse Hook:
├─ Matcher: Edit|Write|MultiEdit    ├─ Matcher: Edit|Write|MultiEdit
├─ Load context (load_context.py)   ├─ Run discovery_detector.py
├─ Validate references              ├─ Auto-trigger plan updates if discoveries
└─ Allow/Block operation            │
                                    ├─ Matcher: Task (subagent completion)
                                    └─ Run discovery_detector.py

Stop Hook:                          SessionStart Hook:
├─ Run workflow_orchestrator.py     ├─ Run load_project_context.py
├─ Check phase completion           ├─ Load phases.md status
├─ Archive completed work           ├─ Inject active errors  
└─ Orchestrate next steps           └─ Load investigation context

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            EVIDENCE FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

investigations/[area]/               investigations/[area]/
│                                   │
├─ findings.md (Active) ────────────┼→ archive_YYYYMMDD/ (Complete)
├─ scraping/findings.md             │  
├─ apis/findings.md                 └─ [Archived when phase complete]
└─ analysis/findings.md
```

## Slash Command Reference

### Primary Workflow Commands
- **`/phase:update_plans`** - Sync CLAUDE.md with phases.md status and phase file details
- **`/investigate:discovery`** - Structured investigation with evidence collection
- **`/validate:project`** - Cross-reference validation and plan consistency check
- **`/status:current`** - Quick project orientation and health check

### Automated Hook Integration
- **SessionStart** - Auto-load project context and current status
- **PreToolUse** - Auto-validate operations and load context  
- **PostToolUse** - Auto-maintain references and detect discoveries
- **Stop** - Auto-orchestrate workflow transitions and phase management

## Key Automation Principles

1. **Slash Commands as User Interface** - Manual triggers for major workflow operations
2. **Hooks as Continuous Automation** - Automatic maintenance and discovery integration
3. **Evidence-Based Transitions** - All phase progression requires documented proof
4. **Cross-Reference Integrity** - Automatic validation and maintenance throughout
5. **Discovery-Driven Updates** - Findings automatically trigger plan revisions
6. **Error Visibility** - Immediate injection into CLAUDE.md for new sessions

## Workflow States

### Active Development
- User runs slash commands manually
- Hooks provide continuous validation and maintenance
- Discoveries trigger automatic plan updates
- Errors surface immediately with structured logging

### Phase Transitions  
- Evidence validation with end-to-end proof
- Automatic archival of completed work
- Next phase loading with updated CLAUDE.md
- Cross-reference updates and validation

### Error Recovery
- Automatic error injection into CLAUDE.md
- Structured error logs with reproduction steps
- Investigation triggered for complex issues
- Resolution tracking and knowledge capture

This creates a self-maintaining, continuously evolving project that integrates manual control with intelligent automation.