# SDLC Triad Collaboration Guide

**Version**: 1.0
**Effective**: 2025-11-22
**Constitutional Authority**: Principle XI

---

## Overview

The SDLC Triad is a structured collaboration framework ensuring Product, Architecture, and Engineering alignment throughout the development lifecycle. The Triad prevents misalignment errors through clear role boundaries and validation gates.

### The Triad

1. **Product-Manager (Product Manager)**: Defines **What** and **Why**
2. **Architect (System Architect)**: Defines **How** (Strategic/Technical)
3. **Tech-Lead (Engineering Manager)**: Defines **When** and **Who** (Tactical/Resourcing)

---

## Role Responsibilities

### Product-Manager (Product Manager)

**MUST Do**:
- ✅ Define user problems and pain points
- ✅ Articulate business value and ROI
- ✅ Prioritize features based on business impact
- ✅ Create Product Requirements Documents (PRDs)
- ✅ Validate product-market fit
- ✅ Sign off on specs for product alignment

**MUST NOT Do**:
- ❌ Make technical architecture decisions (database choice, tech stack)
- ❌ Estimate development timelines without Tech-Lead input
- ❌ Claim infrastructure status without Architect verification
- ❌ Propose specific technical implementations

**Key Principle**: PM focuses on user value and business outcomes, delegates technical "how" to Architect and timeline "when" to Tech-Lead.

---

### Architect (System Architect)

**MUST Do**:
- ✅ Design system architecture and data models
- ✅ Select technology stack with clear rationale
- ✅ Document current infrastructure state (production.md, staging.md)
- ✅ Provide infrastructure baseline reports for deployment PRDs
- ✅ Validate technical feasibility of product requirements
- ✅ Review PRDs for technical accuracy

**MUST NOT Do**:
- ❌ Manage project timelines or resource allocation
- ❌ Assign agents to implementation tasks
- ❌ Define user problems or business priorities
- ❌ Override PM's feature prioritization

**Key Principle**: Architect owns strategic technical decisions (architecture, technology, current state) but defers tactical execution (timeline, agent assignment) to Tech-Lead.

---

### Tech-Lead (Engineering Manager)

**MUST Do**:
- ✅ Estimate effort and timelines based on Architect's design
- ✅ Assign specialized agents to tasks (backend, frontend, devops)
- ✅ Optimize parallel execution and resource utilization
- ✅ Validate capacity constraints and dependencies
- ✅ Provide feasibility checks for PRD timelines
- ✅ Orchestrate multi-agent implementation workflows

**MUST NOT Do**:
- ❌ Rewrite architecture (unless timeline/budget constraints force it)
- ❌ Change feature priorities or scope
- ❌ Choose technology stack or architectural patterns
- ❌ Define product requirements

**Key Principle**: Tech-Lead owns tactical execution (timeline, resources, agent orchestration) but executes Architect's vision and PM's priorities.

---

## PRD Creation Workflow

### Infrastructure/Deployment PRDs (Sequential Triad)

**Trigger**: PRD topic contains keywords: "deploy", "infrastructure", "production", "staging", "database provisioning", "cloud setup"

**Workflow**:

```
Step 0: PM Analyzes Product Need
├─ Read product vision, OKRs, user stories
├─ Identify problem (What) and business value (Why)
├─ Determine if infrastructure vs feature work
└─ Output: Problem statement draft

Step 0.5: Architect Provides Baseline (INFRASTRUCTURE ONLY)
├─ Read: production.md, staging.md, STATUS.md, git log
├─ Document: What exists? What's operational? Completion %?
├─ Create: specs/{feature-id}/architect-baseline.md
└─ Output: Infrastructure baseline report handed to PM

Step 1: PM Drafts PRD (via /aod.define)
├─ Reads architecture docs
├─ Incorporate Architect baseline into "Current State" section
├─ Define product requirements (What & Why) but NOT timeline
├─ Mark timeline as "TBD - pending Tech-Lead feasibility"
└─ Output: Draft PRD with infrastructure baseline

Step 2: Tech-Lead Feasibility Review
├─ Read: Draft PRD + Architect baseline
├─ Estimate: Effort, timeline, agent assignments
├─ Validate: Capacity available, dependencies satisfied
├─ Create: specs/{feature-id}/feasibility-check.md
└─ Output: Timeline estimate (High/Medium/Low confidence)

Step 3: Architect Technical Review
├─ Read: Draft PRD + Feasibility check
├─ Validate: Infrastructure claims match baseline
├─ Confirm: Technical approach is feasible
├─ Create: docs/agents/architect/{date}_{feature}_prd-review_ARCH.md
└─ Output: Approve OR request corrections

Step 4: PM Finalizes PRD
├─ Incorporate: Tech-Lead timeline + Architect feedback
├─ Validate: Product requirements still achievable
├─ Publish: Approved PRD with triple validation
└─ Output: Final PRD ready for /aod.plan
```

**Timeline**: ~2-4 hours for full Triad review cycle

---

### Feature PRDs (Parallel Triad)

**Trigger**: PRD topic is greenfield feature work (no infrastructure keywords)

**Workflow**:

```
Step 0: PM Analyzes Product Need
└─ Same as infrastructure workflow

Step 1: PM Drafts PRD (via /aod.define)
├─ Define product requirements
├─ Mark timeline as "TBD"
└─ Output: Draft PRD

Step 2: Parallel Reviews
├─ [Architect] Technical feasibility review
│   └─ Validate: Tech approach feasible, dependencies identified
│
└─ [Tech-Lead] Feasibility review
    └─ Estimate: Timeline, agents, capacity

Step 3: PM Finalizes PRD
├─ Incorporate: Both reviews in parallel
└─ Output: Final PRD with dual validation
```

**Timeline**: ~1-2 hours for parallel Triad review

---

## Document Handoff Standards

### Triad Artifacts

| Document | Location | Owner | When Created | Purpose |
|----------|----------|-------|--------------|---------|
| **Architect Baseline** | `specs/{feature-id}/architect-baseline.md` | Architect | Step 0.5 (infrastructure PRDs only) | Document current infrastructure state |
| **Draft PRD** | `docs/product/02_PRD/{NNN}-{topic}-{date}.md` | PM | Step 1 | Product requirements (What & Why) |
| **Feasibility Check** | `specs/{feature-id}/feasibility-check.md` | Tech-Lead | Step 2 | Timeline, agents, capacity validation |
| **Architect Review** | `docs/agents/architect/{date}_{feature}_prd-review_ARCH.md` | Architect | Step 3 | Technical validation report |
| **Final PRD** | `docs/product/02_PRD/{NNN}-{topic}-{date}.md` (updated) | PM | Step 4 | Approved PRD with Triad input |

### Artifact Templates

**Architect Baseline Template** (`specs/{feature-id}/architect-baseline.md`):

```markdown
# Architect Baseline Report: {Feature Name}

**Feature**: {NNN-feature-name}
**Date**: {YYYY-MM-DD}
**Architect**: Claude (architect agent)

---

## Infrastructure Inventory

**What Exists**:
- Backend: [status, URL if deployed]
- Frontend: [status, URL if deployed]
- Database: [name, status, region]
- Environment Variables: [count configured, scope]
- Custom Domains: [status, SSL certificates]
- Monitoring: [analytics, logging, alerts]

**Operational Status**:
- Production deployment: [% complete]
- Staging environment: [status]
- Infrastructure configuration: [% complete]

**Completion Percentage**:
- Infrastructure setup: [X%]
- Code development: [Y%]
- Testing/validation: [Z%]

---

## Remaining Work

**Infrastructure**:
- [ ] [Task 1]: [description]
- [ ] [Task 2]: [description]

**Code**:
- [ ] [Task 1]: [description]

**Validation**:
- [ ] [Task 1]: [description]

---

## Baseline Summary

**Already Done**: [X% complete]
**Remaining**: [Y% effort needed]
**Timeline Impact**: [How current state affects timeline]
```

**Feasibility Check Template** (`specs/{feature-id}/feasibility-check.md`):

```markdown
# Feasibility Check: {Feature Name}

**Feature**: {NNN-feature-name}
**Date**: {YYYY-MM-DD}
**Tech-Lead**: Claude (team-lead agent)

---

## Effort Estimation

**Work Streams**:
1. {Stream 1}: [effort estimate in hours/days]
2. {Stream 2}: [effort estimate]
3. {Stream 3}: [effort estimate]

**Total Effort**: [X hours/days]
**Confidence Level**: [High/Medium/Low]

---

## Agent Assignment Preview

**Agents Required**:
- {Agent 1 (e.g., devops)}: [X hours] - [tasks]
- {Agent 2 (e.g., backend)}: [Y hours] - [tasks]
- {Agent 3 (e.g., frontend)}: [Z hours] - [tasks]

**Workload Distribution**: [Balanced / {Agent} overloaded]

---

## Timeline Estimate

**Critical Path**: {Path description}
**Dependencies**: {Blocking dependencies}
**Parallel Opportunities**: {Tasks that can run concurrently}

**Realistic Timeline**:
- **Optimistic**: [X days] (all parallel, no blockers)
- **Realistic**: [Y days] (some serial, normal blockers)
- **Pessimistic**: [Z days] (dependencies delay, capacity constraints)

**Recommendation**: [Timeline range with confidence level]

---

## Risk Assessment

**Timeline Risks**:
- {Risk 1}: [likelihood/impact/mitigation]

**Capacity Risks**:
- {Risk 1}: [likelihood/impact/mitigation]

**Dependency Risks**:
- {Risk 1}: [likelihood/impact/mitigation]
```

---

## Veto Authority & Escalation

### When to Exercise Veto

**Architect Veto**:
- PRD claims "database doesn't exist" but baseline shows database operational
- PRD proposes technology that violates architecture principles
- PRD timeline assumes infrastructure doesn't exist when it's deployed

**Tech-Lead Veto**:
- PRD estimates "2 weeks" but feasibility check shows "4 weeks minimum"
- PRD ignores capacity constraints (all agents at 100% utilization)
- PRD timeline doesn't account for dependencies or current state

**PM Veto**:
- plan.md technical design doesn't solve user problem defined in PRD
- tasks.md prioritizes technical elegance over user value delivery

### Escalation Process

**Level 1: Triad Negotiation** (~30 minutes)
- Example: PM wants 2-week timeline, Tech-Lead says 4 weeks
- Discussion: PM explains business urgency, Tech-Lead explains capacity constraints
- Compromise: Identify scope reduction to hit 3-week timeline

**Level 2: Constitution Arbitration** (~15 minutes)
- Check: Constitution Principle IX (realistic timelines)
- Ruling: Defer to Tech-Lead's capacity-based estimate (constitutional requirement)
- Outcome: 4-week timeline accepted, or PM reduces scope

**Level 3: User Decision** (variable)
- Present: PM position (business need for 2 weeks) vs Tech-Lead position (capacity allows 4 weeks)
- Options: (A) Accept 4 weeks, (B) Reduce scope for 3 weeks, (C) Add resources for 2 weeks
- User decides: Final call, documented in PRD with rationale

---

## Success Metrics

**PRD Quality**:
- Technical inaccuracies: <3 per PRD
- Architect review time: <30 min for standard PRDs
- Infrastructure status accuracy: >95%

**Timeline Accuracy**:
- PRD estimate within 20% of actual delivery (measured post-implementation)
- Example: PRD says "2-4 hours", actual delivery is 3 hours → 100% accuracy

**Triad Efficiency**:
- Triad workflow cycle time: <2 hours for feature PRDs, <4 hours for infrastructure PRDs
- Review round-trips: <2 iterations to reach approval
- Escalation rate: <10% of PRDs require user decision

---

## Common Patterns

### Pattern 1: Infrastructure Already Complete

**Scenario**: PM proposes PRD for "deploying infrastructure" but Architect baseline shows infrastructure 100% operational.

**Triad Response**:
- Architect baseline: "Infrastructure complete [date]"
- PM revises PRD: Scope from "multi-week infrastructure setup" → "deployment finalization"
- Tech-Lead feasibility: "Devops agent, [X hours], high confidence"
- Result: Accurate PRD, no wasted effort

### Pattern 2: Timeline Misalignment

**Scenario**: PM proposes "2-week deadline" but Tech-Lead feasibility shows "4 weeks minimum".

**Triad Response**:
- Tech-Lead feasibility: "4 weeks realistic, 6 weeks pessimistic"
- PM evaluates: Business need vs capacity constraint
- Options: (A) Accept 4 weeks, (B) Reduce scope for 3 weeks, (C) Add resources
- Result: Realistic timeline in final PRD

### Pattern 3: Technical Infeasibility

**Scenario**: PM proposes feature requiring real-time capabilities but Architect review identifies technical limitations.

**Triad Response**:
- Architect review: "Real-time feature not supported in current infrastructure"
- Architect proposes: (A) Add support (4 weeks), (B) Use alternative approach (2 weeks, trade-offs)
- PM decides: Accept alternative for MVP, add full support in later phase
- Result: Technically feasible PRD with clear trade-offs

---

## Tools & Commands

**Manual Triad Invocation**:
```bash
# Request Architect baseline (infrastructure PRDs)
# Use Task tool to invoke architect agent

# Request Tech-Lead feasibility
# Use Task tool to invoke team-lead agent

# Request Architect review
# Use Task tool to invoke architect agent
```

**Automated Triad (Future)**:
```bash
# Auto-invoke Triad for PRD creation
/aod.define <topic>

# What it does:
# 1. Auto-detect infrastructure vs feature work
# 2. Invoke Architect baseline if infrastructure
# 3. PM drafts PRD
# 4. Invoke Tech-Lead feasibility
# 5. Invoke Architect review
# 6. Present all reviews to PM for incorporation
```

---

## FAQ

**Q: Does every PRD need full Triad review?**
A: Infrastructure PRDs (deploy, infrastructure, production keywords) require full Triad (baseline + feasibility + technical review). Feature PRDs use simplified Triad (feasibility + technical review, no baseline).

**Q: How long does Triad review add to PRD creation?**
A: ~1-2 hours for feature PRDs (parallel reviews), ~2-4 hours for infrastructure PRDs (sequential with baseline). This prevents downstream errors that cost 10-20x more to fix.

**Q: Can PM skip Triad review if timeline is urgent?**
A: No. Constitution Principle XI mandates Triad review for all PRDs. Urgency doesn't override quality gates. However, PM can request expedited reviews (target <1 hour for simple PRDs).

**Q: What if Triad disagrees and can't reach consensus?**
A: Use 3-level escalation: (1) Negotiate (~30 min), (2) Constitution arbitration (~15 min), (3) User decision (variable). Most disagreements resolve at Level 1 or 2.

**Q: Who has final authority: PM, Architect, or Tech-Lead?**
A: Domain-specific: PM for product priorities, Architect for technical feasibility, Tech-Lead for timeline/capacity. Constitution provides tie-breaking rules. User has ultimate authority via Level 3 escalation.

---

## Related Documents

- **Constitution**: `.aod/memory/constitution.md` Principle XI
- **Product-Spec Alignment**: `docs/standards/PRODUCT_SPEC_ALIGNMENT.md`
- **Definition of Done**: `docs/standards/DEFINITION_OF_DONE.md`

---

**Version**: 2.0
**Last Updated**: 2026-01-31
**Maintained By**: SDLC Triad (product-manager, architect, team-lead)
