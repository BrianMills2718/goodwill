# AutoCoder4_CC Command Workflow

## Integrated Command Workflow

### Mermaid Diagram

```mermaid
flowchart TD
    A[Read MVP_PLAN.md for current phase] --> B[Load Phase Plans into CLAUDE.md]
    
    B --> C[WITHIN-PHASE LOOP]
    
    C --> D[/implement<br/>Execute plans]
    D --> E[/doublecheck<br/>Verify what was actually done]
    E --> F{Done?}
    
    F -->|No| G[/plan<br/>Plan for issues found in doublecheck]
    G --> H[/update_plans<br/>Update CLAUDE with new plans]
    H --> D
    
    F -->|Yes| I[/close_phase<br/>• Archive evidence<br/>• Mark ✅ in MVP_PLAN<br/>• Review learnings<br/>• Validate approach]
    I --> K{Good?}
    
    K -->|Yes| L[/load_next_phase<br/>Load next phase from MVP_PLAN into CLAUDE]
    L --> M[Continue with next phase]
    M --> C
    
    K -->|No| N[/reassess_plans<br/>• Major plan overhaul<br/>• Rework roadmap strategy<br/>• Update MVP_PLAN.md]
    N --> O[Load New Plans into CLAUDE.md]
    O --> P[Back to Within-Phase Loop]
    P --> C
    
    %% Discovery Integration
    D -.-> Q{Major Discovery?}
    E -.-> Q
    G -.-> Q
    
    Q -->|Yes| R[/reassess_plans<br/>• Rework roadmap<br/>• Change strategy<br/>• Update MVP_PLAN]
    Q -->|No| S[/integrate_discovery<br/>• Add to existing plan<br/>• Update phase files<br/>• Continue workflow]
    
    R --> T[Load new plans into CLAUDE.md]
    T --> U[Back to Within-Phase Loop]
    U --> C
    
    S --> V[Continue current workflow with new issues integrated]
    V --> C
    
    %% Evidence Flow
    I --> W[evidence/current/Evidence_Phase_*.md]
    W --> X[evidence/completed/Evidence_Phase_*.md]
    
    classDef commandBox fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef decisionBox fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef evidenceBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class D,G,H,I,L,N,R,S commandBox
    class F,K,Q decisionBox
    class W,X evidenceBox
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AUTOCODER4_CC WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────────┘

Start: Read MVP_PLAN.md for current phase
│
▼
┌─────────────────────┐
│   Load Phase Plans  │
│   into CLAUDE.md    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────┐
│  WITHIN-PHASE LOOP   │◄────────────────────────────────┐
│                      │                                 │
│  ┌─────────────────┐ │                                 │
│  │   /implement    │ │                                 │
│  │  Execute plans  │ │                                 │
│  └─────────┬───────┘ │                                 │
│            │         │                                 │
│  ┌─────────▼───────┐ │                                 │
│  │  /doublecheck   │ │                                 │
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
│            │         │  │     /plan       │            │
│            │         │  │ Plan for issues │            │
│            │         │  │ found in        │            │
│            │         │  │ doublecheck     │            │
│            │         │  └─────────┬───────┘            │
│            │         │            │                    │
│            │         │  ┌─────────▼───────┐            │
│            │         │  │  /update_plans  │            │
│            │         │  │ Update CLAUDE   │            │
│            │         │  │ with new plans  │────────────┘
│            │         │  └─────────────────┘
│            │         │
└────────────┼─────────┘
             │
             ▼
┌────────────────────────┐
│     /close_phase       │
│ • Archive evidence     │
│ • Mark ✅ in MVP_PLAN  │
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
│   /load_next_phase     │ │
│ Load next phase from   │ │
│ MVP_PLAN into CLAUDE   │ │
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
             │ • Update MVP_PLAN.md      │
             └─────────────┬─────────────┘
                           │
                           ▼
                     ┌─ Load New ─┐
                     │   Plans    │
                     │into CLAUDE │
                     └────────────┘
                           │
                           ▼
                     ┌─ Back to  ─┐
                     │Within-Phase│
                     │    Loop    │
                     └────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│              DISCOVERY INTEGRATION (Can trigger from anywhere)                   │
└─────────────────────────────────────────────────────────────────────────────────┘

Discovery During /implement, /doublecheck, or /plan:
                           │
                    ┌──────▼──────┐
                    │   Major     │
                    │ Discovery?  │──No─┐
                    └──┬──────────┘     │
                       │Yes             │
                       ▼                ▼
            ┌─────────────────────┐  ┌─────────────────────────┐
            │  /reassess_plans    │  │  /integrate_discovery   │
            │ • Rework roadmap    │  │ • Add to existing plan  │
            │ • Change strategy   │  │ • Update phase files    │
            │ • Update MVP_PLAN   │  │ • Continue workflow     │
            └─────────┬───────────┘  └─────────┬───────────────┘
                      │                        │
                      ▼                        ▼
            ┌─────────────────────┐  ┌─────────────────────────┐
            │   Load new plans    │  │   Continue current      │
            │   into CLAUDE.md    │  │   workflow with new     │
            └─────────────────────┘  │   issues integrated     │
                      │              └─────────────────────────┘
                      ▼
                ┌─ Back to ─┐
                │Within-Phase│
                │   Loop     │
                └───────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            EVIDENCE FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

evidence/current/               evidence/completed/
│                               │
├─ Evidence_Phase110_*.md ──────┼→ [Phase complete]
├─ Evidence_Phase2_*.md         │  Archive old evidence
└─ [Active work evidence]       └─ Evidence_Phase110_*.md
```

## Command Reference

### Phase Execution Commands
- **`/implement`** - Execute current CLAUDE.md plans
- **`/doublecheck`** - Verify completion claims vs reality  
- **`/plan`** - Create plan for remaining issues from doublecheck
- **`/update_plans`** - Update CLAUDE.md with new plans, mark verified completions

### Phase Transition Commands
- **`/close_phase`** - Archive evidence, mark phase done, validate next approach
- **`/load_next_phase`** - Load next phase from MVP_PLAN.md into CLAUDE.md

### Discovery Management Commands  
- **`/reassess_plans`** - Major plan overhaul when discoveries require strategy changes
- **`/integrate_discovery`** - Add new issues to roadmap without disrupting current work

### Investigation & Analysis Commands (Can be used anytime)
- **`/investigate`** - Systematic debugging with organized project structure
- **`/status`** - Quick project status and orientation check
- **`/categorize_uncertanties`** - Flexible uncertainty analysis outside workflow
- **`/validate_plans`** - Cross-check consistency between all documents

## Key Principles

1. **Single Source of Truth**: Only MVP_PLAN.md contains status information
2. **Evidence-Based**: No completion claims without proof
3. **Phase Isolation**: Complete one phase fully before moving to next
4. **Discovery Integration**: Handle new discoveries without losing current progress
5. **Evidence Archival**: Keep current work separate from completed phases