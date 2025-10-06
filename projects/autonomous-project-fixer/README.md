# Autonomous Project Fixer

## 🎯 Purpose
System for autonomously fixing and improving existing codebases that are already started.

**Distinction:** This system is designed for **reactive improvement** of existing projects, while the autonomous-system-builder is designed for **proactive creation** of new projects from scratch.

## 📊 Current Status
**Future Work** - Substantial research and flowchart development completed, but not actively being developed.

## 🔄 V5 Hybrid Intelligence System

### Core Approach
- **Test-Failure Driven**: Responds to failing tests and broken functionality
- **Reactive Problem Solving**: Diagnoses issues and applies fixes
- **Hybrid Intelligence**: Combines programmatic checks with LLM analysis

### Key Flowcharts
- `hook_mermaid_diagram_full5_hybrid_intelligence.txt` - Main decision flowchart
- `hook_mermaid_diagram_full4_w_tdd.txt` - TDD-focused version
- `hook_mermaid_diagram_full2.txt` - Earlier iteration

### Decision Logic
```
Hook Triggered → Test Status → 
├── Tests Pass → Progress Analysis → Commit/Continue
└── Tests Fail → Failure Analysis → SimpleFailure/LLMFailureAnalysis → Fix → Retry
```

## 🎯 Design Philosophy

### When to Use This System
- ✅ Existing codebase with failing tests
- ✅ Broken functionality that needs diagnosis
- ✅ Code quality improvements needed
- ✅ Debugging and error resolution

### When NOT to Use This System
- ❌ Starting new projects from scratch (use autonomous-system-builder)
- ❌ Major architectural changes (requires human planning)
- ❌ Requirements are unclear or changing

## 🏗️ Technical Architecture

### Hybrid Intelligence Classification
- **🤖 Programmatic**: Fast binary checks (file existence, test status)
- **🧠 LLM**: Complex reasoning (failure analysis, strategy selection)  
- **⚡ Hybrid**: Programmatic first, LLM if needed

### Safety Mechanisms
- Iteration limits to prevent infinite loops
- Manual override capabilities
- Escalation to human intervention
- Evidence validation requirements

## 🔮 Future Development

### When to Build This System
After autonomous-system-builder is validated and working, this project fixer system could be valuable for:
- Maintaining and improving autonomous-built projects
- Fixing legacy codebases that can't be rebuilt from scratch
- Continuous improvement of existing systems

### Integration with Autonomous System Builder
- Could use same planning methodology for major improvements
- Could hand off to system builder for major refactoring
- Could serve as maintenance mode for autonomous-built projects

## 📋 Development Priority
**Priority: Low** - Focus remains on completing autonomous-system-builder first.

The project fixer approach (V5) was initially attempted for building the autonomous system but proved incompatible with the planning-driven approach needed for from-scratch development.