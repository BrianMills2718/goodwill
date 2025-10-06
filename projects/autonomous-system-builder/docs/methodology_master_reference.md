# Autonomous TDD Methodology - Master Reference

## 🎯 CURRENT METHODOLOGY

**Authoritative Source**: `docs/architecture/iterative_methodology_stabilization.md`

**Last Updated**: 2024-01-15 (supersedes all previous methodology descriptions)

## Complete 8-Phase Iterative Process

```
1. Overview
2. Behavior + Acceptance Tests
3. Architecture + Contract Integration Tests  
4. External Dependency Research + External Integration Tests
5. Pseudocode + Architecture Review (iterative stabilization)
6. Implementation Plans + Unit Tests + Implementation Integration Tests
7. Create Files & Cross-References
8. Implementation
```

## Key Features

### **Three Types of Integration Tests**
- **Contract Integration Tests**: Component interfaces (Architecture Phase)
- **External Integration Tests**: Real API testing (External Dependency Phase)
- **Implementation Integration Tests**: Component interactions (Post-Pseudocode)

### **LLM-Driven Stabilization**
- Problem tracking across all phases
- Micro-iterations within phases (max 5)
- Macro-iterations across phases (max 3)
- Stability confidence >0.8 required to proceed

### **Emergency Limits**
- 15 total problem resolution attempts
- Force proceed with documented risks if limits exceeded
- Human escalation for persistent blocking issues

## Superseded Documentation

**⚠️ OUTDATED REFERENCES** (archived for historical purposes):
- ADR-003 linear methodology (lines 129-140)
- ADR-006 methodology integration (lines 384-391)  
- BDR-007 planning phase (line 161)

**All future autonomous systems MUST use the iterative methodology.**

## Implementation Priority

1. **Immediate**: Update all autonomous systems to use iterative methodology
2. **Next**: Implement problem tracking and stabilization assessment
3. **Future**: Validate methodology effectiveness with metrics

For complete details, see: `docs/architecture/iterative_methodology_stabilization.md`