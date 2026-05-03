# PRD-000: Example Feature Template

**Status**: Example
**Created**: 2026-03-21
**PM**: product-manager
**Related Spec**: N/A

---

## Problem Statement

**User Problem**: [Describe the pain point or need from the user's perspective]

**Current State**: [How do users solve this problem today? What are the limitations?]

**Desired State**: [What would the ideal solution look like?]

---

## Target Users

**Primary Persona**: [Name from target-users.md]
- **Pain Point**: [Specific problem this solves]
- **User Value**: [How this improves their experience]

**Secondary Persona**: [Name] (optional)
- [Same structure]

---

## Success Metrics

**Leading Indicators** (measure adoption):
- [Metric 1]: Baseline → Target
- [Metric 2]: Baseline → Target

**Lagging Indicators** (measure impact):
- [Business metric]: Baseline → Target
- [User satisfaction]: Baseline → Target

---

## Requirements

### Functional Requirements

**FR-1: [Requirement Name]**
- **Description**: [What the feature must do]
- **User Story**: As a [persona], I want [capability] so that [benefit]
- **Acceptance Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2

**FR-2: [Another Requirement]**
- [Same structure]

### Non-Functional Requirements

**NFR-1: Performance**
- [Specific performance target, e.g., "<200ms response time"]

**NFR-2: Security**
- [Security requirements, e.g., "All data encrypted at rest"]

**NFR-3: Scalability**
- [Scalability requirement, e.g., "Support 10,000 concurrent users"]

---

## Scope

### In Scope
- ✅ [Feature/capability that IS included]
- ✅ [Another in-scope item]

### Out of Scope
- ❌ [Feature/capability that IS NOT included]
- ❌ [Another out-of-scope item]
- 📍 **Future Consideration**: [Items for later phases]

---

## Dependencies

### Prerequisites
- [What must exist before this can be built?]
- [External dependencies or integrations]

### Blockers
- [Current blockers or risks]

---

## Timeline

**Estimated Effort**: [From Tech-Lead feasibility check]
- Optimistic: [X days]
- Realistic: [Y days]
- Pessimistic: [Z days]

**Target Delivery**: [Quarter or date]

---

## Triad Validation

### Architect Baseline (Infrastructure PRDs only)
- **Report**: `specs/000-example-feature/architect-baseline.md`
- **Status**: ✅ Complete

### Tech-Lead Feasibility
- **Report**: `specs/000-example-feature/feasibility-check.md`
- **Timeline Estimate**: [X days realistic]
- **Confidence**: [High/Medium/Low]

### Architect Technical Review
- **Report**: `docs/agents/architect/{{DATE}}_000_prd-review_ARCH.md`
- **Verdict**: ✅ APPROVED
- **Inaccuracies**: 0

---

## Sign-Off

**PM Approval**: ✅ Approved on 2026-03-21

**Next Step**: Create spec with `/aod.spec`

---

**Template Instructions**: This is an annotated example. Delete this PRD after creating your first real PRD. Use `/aod.define <topic>` to generate a new PRD with automatic Triad validation.
