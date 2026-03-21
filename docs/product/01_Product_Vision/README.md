# Product Vision - tachi

**Last Updated**: 2026-03-21
**Owner**: Product Manager (product-manager)
**Status**: Template - Customize for your project

---

## Overview

This directory contains the strategic product vision documents for tachi. These documents answer:
- **What** are we building?
- **Why** are we building it?
- **Who** are we building it for?
- **Where** are we positioned in the market?

---

## Documents in This Directory

### 1. product-vision.md (Required)
**Purpose**: Defines the long-term vision and mission of tachi

**Template Structure**:
```markdown
# Product Vision

## Mission Statement
[One sentence: What change do you want to create in the world?]

## Vision Statement
[2-3 sentences: Where will the product be in 3-5 years?]

## Core Value Proposition
[What makes tachi valuable and unique?]

## Success Metrics
[How will you measure if the vision is being achieved?]
```

### 2. target-users.md (Required)
**Purpose**: Documents target user personas and their needs

**Template Structure**:
```markdown
# Target Users

## Primary Persona: [Name]
- **Who**: [Demographics, role, context]
- **Pain Points**: [What problems do they face?]
- **Goals**: [What are they trying to achieve?]
- **How tachi Helps**: [Your solution]

## Secondary Persona: [Name]
[Same structure as primary]

## Anti-Persona: [Who This Is NOT For]
[Clarify who you're explicitly NOT targeting]
```

### 3. competitive-landscape.md (Recommended)
**Purpose**: Maps the competitive environment and positioning

**Template Structure**:
```markdown
# Competitive Landscape

## Direct Competitors
| Competitor | Strengths | Weaknesses | Our Differentiation |
|------------|-----------|------------|---------------------|
| [Name]     | [...]     | [...]      | [...]              |

## Indirect Competitors
[Products that solve similar problems differently]

## Our Unique Positioning
[What makes tachi different and better?]
```

---

## How to Customize

### Step 1: Start with Mission and Vision
1. Copy `product-vision-template.md` to `product-vision.md`
2. Replace `tachi` with your project name
3. Fill in mission statement (one sentence maximum)
4. Write vision statement (2-3 sentences about 3-5 year future)
5. Define core value proposition (why users should care)

### Step 2: Define Target Users
1. Copy `target-users-template.md` to `target-users.md`
2. Identify 1-2 primary personas
3. For each persona, document:
   - Demographics and context
   - Pain points (problems they face)
   - Goals (what they want to achieve)
   - How tachi solves their problems
4. Define anti-personas (who you're NOT building for)

### Step 3: Map Competitive Landscape
1. Copy `competitive-landscape-template.md` to `competitive-landscape.md`
2. Research 3-5 direct competitors
3. Document their strengths and weaknesses
4. Define your unique differentiation
5. Identify indirect competitors (different approaches to same problem)

---

## Integration with Triad Workflow

### PRD References
All PRDs in `docs/product/02_PRD/` must reference this vision:
- PRD problem statements must align with user pain points
- PRD success metrics must ladder up to vision metrics
- PRD user stories must serve defined personas

### Spec Validation
When creating `spec.md` with `/aod.spec`:
- product-manager validates spec aligns with product vision
- Architect ensures technical approach serves user needs
- Team-lead prioritizes work based on persona value

### OKR Alignment
Quarterly OKRs in `docs/product/06_OKRs/` must:
- Support progress toward vision
- Solve pain points for target personas
- Differentiate tachi from competitors

---

## Review Cadence

### Quarterly Review
- **Trigger**: Start of each quarter
- **Owner**: Product Manager
- **Participants**: Full team
- **Questions to Answer**:
  - Is the vision still relevant?
  - Have target personas evolved?
  - Has competitive landscape shifted?
  - Do we need to adjust positioning?

### Annual Deep Dive
- **Trigger**: End of year planning
- **Owner**: Product Manager
- **Participants**: All stakeholders
- **Outcome**: Updated vision for next year

---

## Best Practices

### DO ✅
- Keep mission statement to one sentence (memorable and clear)
- Base personas on real user research, not assumptions
- Update competitive landscape quarterly
- Ensure all PRDs reference vision documents
- Make vision accessible to entire team

### DON'T ❌
- Write vision in technical jargon (focus on user value)
- Create more than 2-3 primary personas (focus is key)
- Ignore changes in competitive landscape
- Let vision documents become stale
- Write vision in isolation (involve team)

---

## Example Vision Structure

```
docs/product/01_Product_Vision/
├── README.md (this file)
├── product-vision.md              # Mission, vision, value proposition
├── target-users.md                # User personas and pain points
├── competitive-landscape.md       # Competitor analysis and positioning
├── market-opportunity.md          # (Optional) Market size and opportunity
└── principles.md                  # (Optional) Product principles and values
```

---

## Related Documentation

**Product Workflow**:
- `docs/product/02_PRD/` - Product Requirements Documents
- `docs/product/03_Product_Roadmap/` - Phase-based roadmap
- `docs/product/05_User_Stories/` - Detailed user stories
- `docs/product/06_OKRs/` - Objectives and Key Results

**Governance**:
- `docs/standards/PRODUCT_SPEC_ALIGNMENT.md` - PM sign-off requirements
- `docs/AOD_TRIAD.md` - PM-Architect-TechLead collaboration

**Agent Tools**:
- `.claude/agents/product-manager.md` - Product Manager agent
- `/aod.define` - Create PRD with Triad governance

---

## Getting Started Checklist

- [ ] Read this README completely
- [ ] Create `product-vision.md` with mission and vision
- [ ] Create `target-users.md` with 1-2 personas
- [ ] Create `competitive-landscape.md` (if applicable)
- [ ] Share vision with team for feedback
- [ ] Link vision docs in first PRD
- [ ] Schedule quarterly review

---

**Template Instructions**: Delete this section after customization. Replace all `{{TEMPLATE_VARIABLES}}` throughout this directory. The vision you define here will guide all product decisions for tachi.

**Last Updated**: 2026-03-21
**Maintained By**: Product Manager (product-manager)
