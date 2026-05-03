<!--
File: PRODUCT_SPEC_ALIGNMENT.md
Description: Product-Spec Alignment requirements and Product Manager sign-off procedures
Author/Agent: product-manager
Created: 2025-11-19
Last Updated: 2025-11-19
Constitutional Reference: Constitution v1.2.0, Principle X
-->

# Product-Spec Alignment Requirements

**CRITICAL: All Triad artifacts (spec.md, plan.md, tasks.md) require Product Manager sign-off before implementation begins**

## Constitutional Authority

Per **Constitution v1.2.0, Principle X: Product-Spec Alignment (NON-NEGOTIABLE)**:

> ALL Triad artifacts (spec.md, plan.md, tasks.md) MUST receive Product Manager (product-manager) sign-off before implementation begins. Product artifacts in docs/product/ are the strategic foundation that technical specifications must serve.

## Rationale

**Why This Matters**:
- Technical excellence without product alignment wastes resources building the wrong solution
- User needs must drive technical decisions, not the reverse
- Strategic objectives (OKRs) require measurable product outcomes
- Product vision ensures features solve real problems for target users

**What Happens Without Alignment**:
- ❌ Teams build technically impressive solutions to the wrong problems
- ❌ Features ship that don't support business objectives
- ❌ Resources wasted on low-impact work
- ❌ Users don't adopt features because they don't solve real pain points
- ❌ Product roadmap becomes disconnected from implementation

## The Product-Spec Workflow

### Required Workflow (NON-NEGOTIABLE)

```
1. /aod.define <topic>             → Product Manager creates PRD
   │
   ├─ PM researches product context (vision, OKRs, roadmap)
   ├─ PM documents requirements in industry-standard format
   └─ PRD saved to docs/product/02_PRD/NNN-topic-YYYY-MM-DD.md

2. PRD Review & Approval          → Stakeholder validation
   │
   ├─ PM reviews PRD for completeness
   ├─ Stakeholders review and provide feedback
   ├─ PM addresses feedback and finalizes PRD
   └─ PRD marked as "Approved" in INDEX.md

3. /aod.plan                      → Plan stage (chains spec → project-plan → tasks)
   │
   ├─ Step 3a: /aod.spec          → Create spec.md from PRD
   │   ├─ Architect reads approved PRD
   │   ├─ Architect creates spec.md referencing PRD
   │   ├─ spec.md includes source_prd metadata
   │   └─ PM sign-off on spec.md (validates alignment)
   │
   ├─ Step 3b: /aod.project-plan  → Create plan.md from spec
   │   ├─ Architect creates technical plan
   │   ├─ plan.md references product docs
   │   └─ PM + Architect sign-off on plan.md
   │
   └─ Step 3c: /aod.tasks         → Create tasks.md from plan
       ├─ Team Lead breaks down implementation
       ├─ tasks.md prioritization considers user value
       └─ PM + Architect + Team-Lead sign-off on tasks.md

4. /aod.build                     → Execute implementation
   │
   └─ Implementation begins ONLY after all Plan sign-offs approved
```

## Product Manager Sign-Off Checklist

Before approving spec.md, plan.md, or tasks.md, the Product Manager MUST validate:

### Vision Alignment

- [ ] **Product Vision**: Aligns with [docs/product/01_Product_Vision/product-vision.md](../product/01_Product_Vision/product-vision.md)
  - Does this feature support our product vision?
  - Does it move us toward our long-term goals?

- [ ] **Target Users**: Serves target user needs from [docs/product/01_Product_Vision/target-users.md](../product/01_Product_Vision/target-users.md)
  - Which persona(s) benefit from this feature?
  - Does it solve a real pain point for them?

- [ ] **Competitive Positioning**: Fits competitive strategy from [docs/product/01_Product_Vision/competitive-landscape.md](../product/01_Product_Vision/competitive-landscape.md)
  - Does this differentiate us from competitors?
  - Does it strengthen our position in the market?

### Strategic Alignment

- [ ] **OKRs**: Supports current quarter objectives from [docs/product/06_OKRs/](../product/06_OKRs/)
  - Which OKR does this support?
  - How does it move the key results?
  - Is the impact measurable?

- [ ] **Roadmap Timeline**: Fits phase roadmap from [docs/product/03_Product_Roadmap/](../product/03_Product_Roadmap/)
  - Which phase is this feature in?
  - Does the timeline align with roadmap commitments?
  - Are dependencies satisfied?

- [ ] **User Stories**: Delivers on user stories from [docs/product/05_User_Stories/](../product/05_User_Stories/)
  - Which user stories does this implement?
  - Do acceptance criteria match?
  - Is user value clear?

### Quality Standards

- [ ] **Problem Statement**: Clear and user-focused
  - Does the spec explain what user problem we're solving?
  - Is the pain point articulated in user terms?

- [ ] **Success Metrics**: Measurable outcomes defined
  - How will we measure success?
  - Are metrics specific and quantifiable?
  - Do we have baseline and target values?

- [ ] **Scope Boundaries**: Well-defined with clear in/out scope
  - Is MVP scope clearly defined?
  - Are out-of-scope items explicitly listed?
  - Is scope realistic for timeline?

- [ ] **Dependencies**: Identified and documented
  - What must be complete before this work?
  - What external dependencies exist?
  - Are blockers identified?

- [ ] **Technical Constraints**: Realistic and documented
  - Are constraints acknowledged?
  - Is technical approach feasible?
  - Have alternatives been considered?

### Documentation Standards

- [ ] **spec.md**: Has clear user value proposition
  - Does spec lead with user value, not technical details?
  - Are user benefits explicit?

- [ ] **plan.md**: References relevant product docs
  - Does plan reference source PRD?
  - Does plan cite relevant OKRs, roadmap, user stories?

- [ ] **tasks.md**: Prioritization aligns with product priorities
  - Are P0 tasks truly critical for user value?
  - Does sequencing make sense from user perspective?
  - Is MVP scope aligned with PRD?

- [ ] **Traceability**: All artifacts reference source PRD
  - Is source PRD linked in metadata?
  - Can we trace from task → plan → spec → PRD → vision?

## PM Sign-Off Template

Product Manager adds this section to spec.md, plan.md, or tasks.md after validation:

```markdown
---

## Product Manager Sign-Off

**Artifact**: [spec.md / plan.md / tasks.md]
**PM**: product-manager
**Date**: YYYY-MM-DD
**Status**: [✅ Approved / 🟡 Approved with Comments / ❌ Rejected]

### Alignment Validation

#### Vision Alignment
- ✅ Aligns with product vision
- ✅ Serves target user needs (Persona: [Individual Developer / Small Team / Enterprise])
- ✅ Fits competitive positioning

#### Strategic Alignment
- ✅ Supports OKR: [Reference to specific OKR from docs/product/06_OKRs/]
- ✅ Fits roadmap: [Phase X, Week Y]
- ✅ Delivers user stories: [US-001, US-002, etc.]

#### Quality Standards
- ✅ Problem statement is clear and user-focused
- ✅ Success metrics are measurable (Baseline → Target)
- ✅ Scope is well-defined and realistic
- ✅ Dependencies identified
- ✅ Technical constraints documented

#### Documentation Standards
- ✅ User value proposition is clear
- ✅ References product docs appropriately
- ✅ Prioritization aligns with product strategy
- ✅ Traces to source PRD: [docs/product/02_PRD/NNN-topic-date.md]

### Comments

[Any observations, recommendations, or context that engineering should know]

### Approval

**Status**: ✅ Approved for implementation

**Next Step**: [/aod.plan (continues automatically) / /aod.build]

---
```

## Product Manager Veto Authority

The Product Manager has **VETO AUTHORITY** over:

1. **Spec Creation**: Can reject spec.md that doesn't align with product vision
2. **Plan Approval**: Can reject plan.md that doesn't fit roadmap or constraints
3. **Task Prioritization**: Can reorder tasks.md to align with product priorities

### When to Exercise Veto

**Valid Reasons**:
- ✅ Spec solves wrong problem or serves wrong users
- ✅ Plan timeline doesn't fit roadmap commitments
- ✅ Tasks prioritize technical elegance over user value
- ✅ Work doesn't support current quarter OKRs
- ✅ Scope creep threatens delivery commitments
- ✅ Missing critical user stories or acceptance criteria
- ✅ Success metrics are unmeasurable or missing

**Invalid Reasons**:
- ❌ Personal preference for different technology
- ❌ Disagreement on implementation details (that's architect's domain)
- ❌ Code style or formatting choices
- ❌ Technical architecture that still serves user needs

### Veto Template

When exercising veto, Product Manager documents:

```markdown
---

## Product Manager Veto - YYYY-MM-DD

**Artifact**: [spec.md / plan.md / tasks.md]
**PM**: product-manager
**Reason**: [Clear explanation of misalignment]

### Required Changes

1. [Specific change needed - be concrete and actionable]
2. [Specific change needed]
3. [Specific change needed]

### Rationale

[Explain how these changes restore product alignment]

**Specific Concerns**:
- [Concern 1: How current approach misses user needs]
- [Concern 2: How it conflicts with OKRs]
- [Concern 3: Timeline/scope/dependency issues]

### Supporting References

- **Product Vision**: [Link to relevant section of vision doc]
- **OKRs**: [Link to OKR that's not supported]
- **Roadmap**: [Link to roadmap showing timeline conflict]
- **User Stories**: [Link to user story requirements]

### Resubmit After

[Clear description of what needs to be fixed before resubmission]

**Expected Timeline**: [When should updated artifact be ready?]

---
```

## Product Artifact Synchronization

Product Manager is responsible for maintaining alignment between:

### Product Artifacts (docs/product/)

1. **01_Product_Vision/** - Strategic direction
   - product-vision.md
   - target-users.md
   - competitive-landscape.md

2. **02_PRD/** - Product requirements
   - NNN-topic-YYYY-MM-DD.md (individual PRDs)
   - INDEX.md (PRD registry)

3. **03_Product_Roadmap/** - Phase planning
   - phase-1-mvp.md
   - phase-2-brain.md
   - phase-3-strategist.md
   - phase-4-platform.md

4. **04_Customer_Journey_Maps/** - User experience flows
   - developer-journey.md
   - team-journey.md
   - first-time-user.md
   - enterprise-journey.md

5. **05_User_Stories/** - Feature user stories
   - phase-1-stories.md
   - phase-2-stories.md
   - phase-3-stories.md
   - phase-4-stories.md

6. **06_OKRs/** - Objectives & Key Results
   - YYYY-QN.md (quarterly OKRs)

### Triad Artifacts (.aod/)

1. **constitution.md** - Governance principles
2. **spec.md** - Feature specification
3. **plan.md** - Technical plan
4. **tasks.md** - Implementation tasks

### Synchronization Requirements

**When product vision changes**:
- PM reviews all in-flight specs
- PM updates affected specs or marks them for revision
- PM communicates changes to engineering team

**When OKRs change**:
- PM validates all in-flight work still aligns
- PM reprioritizes work if needed
- PM updates roadmap if timeline shifts

**When roadmap changes**:
- PM updates affected plans and timelines
- PM communicates impacts to stakeholders
- PM adjusts task prioritization

**When user stories change**:
- PM validates affected specs and acceptance criteria
- PM ensures specs still deliver required user value
- PM updates PRDs if requirements evolved

**Bi-Directional Traceability**:

```
Product Vision
    ↓
  OKRs ←→ Roadmap
    ↓         ↓
User Stories ← Customer Journeys
    ↓
  PRD (docs/product/02_PRD/NNN-topic-date.md)
    ↓
spec.md (.aod/spec.md)
    ↓
plan.md (.aod/plan.md)
    ↓
tasks.md (.aod/tasks.md)
    ↓
Implementation
```

Every artifact must trace upward to product vision and downward to implementation.

## Enforcement Mechanisms

### 1. Constitutional Mandate

Constitution v1.2.0, Principle X makes PM sign-off **NON-NEGOTIABLE**.

### 2. Workflow Integration

Triad commands enforce PM sign-off:
- `/aod.plan` requires approved PRD (chains spec → project-plan → tasks with governance gates at each step)
- `/aod.build` requires PM-approved tasks.md

### 3. Pull Request Requirements

PRs without PM approval are blocked from merge:
- PR checklist includes "PM Sign-Off: ✅"
- CI/CD checks for PM approval section in artifacts
- CODEOWNERS includes product-manager for product docs

### 4. Artifact Metadata

All Triad artifacts include metadata:

```yaml
---
source_prd: docs/product/02_PRD/NNN-topic-YYYY-MM-DD.md
pm_approved: true
pm_approval_date: YYYY-MM-DD
pm_approver: product-manager
---
```

### 5. Validation Commands

Use `/aod.analyze` to validate product-spec consistency:
- Checks PRD → spec → plan → tasks traceability
- Validates all artifacts have PM sign-off
- Identifies misalignments and missing approvals

## Tools & Skills

### Available to Product Manager

**Skills**:
- `kb-query` - Search knowledge base for similar features
- `root-cause-analyzer` - Dig into complex requirement ambiguities

**Commands**:
- `/aod.define <topic>` - Create new PRD
- `/aod.plan` - Plan stage orchestrator (chains spec → project-plan → tasks)
- `/aod.analyze` - Validate product-spec consistency
- `/aod.clarify` - Ask clarifying questions

**Agents**:
- `product-manager` - Product Manager with alignment validation expertise

## Common Alignment Issues

### Issue 1: Spec Doesn't Reference User Value

**Symptom**: spec.md leads with technical implementation, buries user benefits

**Fix**: Require spec to lead with:
1. User problem being solved
2. Target persona(s)
3. User value delivered
4. Success metrics

**PM Action**: Veto until user-focused problem statement added

### Issue 2: Plan Timeline Doesn't Match Roadmap

**Symptom**: plan.md proposes 8-week implementation for 4-week roadmap slot

**Fix**: Options:
1. Descope plan to fit timeline
2. Update roadmap if higher priority
3. Split into multiple phases

**PM Action**: Veto with required timeline alignment

### Issue 3: Tasks Prioritize Technical Debt Over User Value

**Symptom**: tasks.md has P0 refactoring before P1 user features

**Fix**: Reorder tasks to prioritize:
1. P0: User-visible features from PRD
2. P1: Technical enablers for P0 features
3. P2: Technical debt that doesn't block users

**PM Action**: Veto with required reprioritization

### Issue 4: Missing Success Metrics

**Symptom**: spec.md has no measurable success criteria

**Fix**: Add success metrics:
- Leading indicators (usage, adoption)
- Lagging indicators (business impact)
- User satisfaction (NPS, CSAT)

**PM Action**: Veto until metrics defined

### Issue 5: Scope Creep

**Symptom**: spec.md includes features marked out-of-scope in PRD

**Fix**: Remove out-of-scope items, create follow-up PRD for future phase

**PM Action**: Veto with scope enforcement

## Success Criteria

Product-Spec Alignment is successful when:

1. ✅ **Every spec has a PRD**: No technical work starts without product context
2. ✅ **Alignment is maintained**: Product docs and Triad artifacts stay in sync
3. ✅ **User value is clear**: Every feature has measurable user impact
4. ✅ **Strategy drives execution**: OKRs and roadmap guide prioritization
5. ✅ **Quality is high**: Specs are complete, unambiguous, and feasible
6. ✅ **Team is aligned**: Engineering understands "why" and "who" not just "what"
7. ✅ **Traceability exists**: Can trace from vision → OKR → PRD → spec → plan → tasks → code
8. ✅ **PM veto is rare**: Most specs pass first review (indicates good upfront alignment)

## References

### Constitutional Authority
- [Constitution v1.2.0, Principle X](./.aod/memory/constitution.md#x-product-spec-alignment-non-negotiable)

### Product Manager Documentation
- [product-manager Agent](./.claude/agents/product-manager.md)

### Related Core Principles
- [Definition of Done](./DEFINITION_OF_DONE.md)
- [Five Whys Methodology](./FIVE_WHYS_METHODOLOGY.md)
- [Git Workflow](./GIT_WORKFLOW.md)

### Product Documentation
- [Product Vision](../product/01_Product_Vision/)
- [PRDs](../product/02_PRD/)
- [Roadmap](../product/03_Product_Roadmap/)
- [User Stories](../product/05_User_Stories/)
- [OKRs](../product/06_OKRs/)

---

**Remember**: The Product Manager's approval is not a rubber stamp. It's a critical quality gate ensuring we build the right product, not just build the product right.
