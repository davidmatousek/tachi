# Product Roadmap - tachi

**Last Updated**: 2026-03-21
**Owner**: Product Manager (product-manager)
**Status**: Template - Complete after MVP launch

---

## When to Create This

**Create your roadmap AFTER your MVP launches.**

Before MVP, you don't have enough information:
- No real user feedback
- No usage data
- No validated assumptions
- Priorities will change

**Pre-MVP**: Focus on `/aod.define` → build MVP
**Post-MVP**: Create roadmap based on what you learned

> **AOD Lifecycle Note**: Roadmap documents can be auto-generated via `/aod.roadmap`,
> which scans completed PRDs in `docs/product/02_PRD/` and scaffolds a quarterly roadmap
> in this directory with PM sign-off. `/aod.define` also reads this directory for phase
> context when creating PRDs. You can still create and maintain roadmap files manually.

---

## Overview

This directory contains the product roadmap for tachi, organized by phases or quarters. The roadmap shows **When** features will be delivered and **Why** they're prioritized in that order.

---

## Roadmap Structure

### Phase-Based Roadmap
```
docs/product/03_Product_Roadmap/
├── README.md (this file)
├── phase-1-mvp.md          # Minimum Viable Product
├── phase-2-growth.md       # Growth and scaling features
├── phase-3-optimization.md # Performance and polish
└── phase-4-platform.md     # Platform capabilities
```

### Time-Based Roadmap
```
docs/product/03_Product_Roadmap/
├── README.md (this file)
├── 2025-Q1.md             # Q1 features and goals
├── 2025-Q2.md             # Q2 features and goals
├── 2025-Q3.md             # Q3 features and goals
└── 2025-Q4.md             # Q4 features and goals
```

**Choose the approach that fits your project**: Phase-based for startups/new projects, time-based for established products.

---

## Roadmap Template

### Phase-Based Template
```markdown
# Phase N: [Phase Name]

**Timeline**: [Duration estimate]
**Status**: [Not Started | In Progress | Complete]
**Goal**: [One sentence: What does this phase achieve?]

## Objectives
1. [Objective 1]
2. [Objective 2]

## Features
| Feature | PRD | Status | Owner |
|---------|-----|--------|-------|
| [Name]  | PRD-NNN | [status] | [PM] |

## Success Criteria
- [Metric 1]: Target value
- [Metric 2]: Target value

## Dependencies
- [What must be complete before this phase?]

## Risks
- [Risk 1]: [Mitigation strategy]
```

### Quarter-Based Template
```markdown
# tachi Roadmap - YYYY-QN

**Quarter**: [Q1/Q2/Q3/Q4] YYYY
**Theme**: [One word theme for the quarter]
**Status**: [Planning | In Progress | Complete]

## Quarter Objectives
1. [Objective 1 aligned with OKRs]
2. [Objective 2]

## Planned Features
[Same table structure as phase-based]

## Stretch Goals
[Features we'll tackle if ahead of schedule]

## Not This Quarter
[Features explicitly deferred to later]
```

---

## Integration with Other Docs

### Connects to Product Vision
- Roadmap phases implement the product vision incrementally
- Each phase moves closer to vision goals
- Early phases solve highest-priority pain points

### Drives PRD Creation
- Each roadmap feature requires a PRD
- PRD timelines must align with roadmap phases
- Roadmap provides context for prioritization

### Aligns with OKRs
- Quarter roadmaps align with quarterly OKRs
- Feature delivery dates support key result targets
- Roadmap adjusts based on OKR progress

---

## Best Practices

### DO ✅
- Keep roadmap at feature level (not task level)
- Review and update monthly
- Make trade-offs explicit (what's NOT in the phase)
- Align with quarterly OKRs
- Share roadmap with entire team

### DON'T ❌
- Commit to specific dates too far in advance
- Include every idea (focus on top priorities)
- Ignore dependencies between features
- Set roadmap in stone (be flexible)
- Hide roadmap changes (communicate adjustments)

---

**Template Instructions**: Choose phase-based OR time-based structure. Delete this message and create your first roadmap document.

**Maintained By**: Product Manager (product-manager)
