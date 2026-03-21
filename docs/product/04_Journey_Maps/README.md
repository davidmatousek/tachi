# Customer Journey Maps - tachi

**Last Updated**: 2026-03-21
**Owner**: Product Manager (product-manager)
**Status**: Template - Complete after MVP launch

---

## When to Create This

**Create journey maps AFTER your MVP launches and you have real users.**

Before MVP:
- Your assumptions about user journeys are untested
- You don't know actual pain points vs. imagined ones
- The onboarding flow doesn't exist yet

**Pre-MVP**: Focus on `/aod.define` (includes target users in vision) → build MVP
**Post-MVP**: Map real user journeys based on actual behavior and feedback

> **AOD Lifecycle Note**: This directory is **manually maintained** — no AOD command
> auto-generates or updates journey maps. `/aod.define` reads this directory for
> persona context, but does not write to it. Create journey maps as a team
> activity based on real user research.

---

## Overview

Customer journey maps visualize the end-to-end experience of users interacting with tachi. They help identify pain points, opportunities, and moments that matter.

---

## Journey Map Template

```markdown
# [Persona Name] Journey Map

**Persona**: [Name from target-users.md]
**Scenario**: [What is the user trying to accomplish?]
**Last Updated**: 2026-03-21

## Journey Stages

### 1. Discovery
**What they do**: [Actions taken]
**Thoughts**: [What they're thinking]
**Feelings**: [Emotional state: 😀😐😞]
**Pain Points**: [Frustrations]
**Opportunities**: [How tachi can help]

### 2. Evaluation
[Same structure]

### 3. Onboarding
[Same structure]

### 4. Active Use
[Same structure]

### 5. Advocacy
[Same structure]

## Key Insights
1. [Insight from journey mapping]
2. [Another insight]

## Action Items
- [ ] [Feature to address pain point]
- [ ] [Improvement opportunity]
```

---

## Example Journey Maps

**Common Journeys to Document**:
1. **First-Time User**: From discovery to first success
2. **Power User**: Advanced usage patterns
3. **Team Admin**: Setup and management flows
4. **Enterprise Buyer**: Evaluation to purchase

---

## Best Practices

### DO ✅
- Base on real user research (not assumptions)
- Include emotional states (😀😐😞)
- Identify pain points and opportunities
- Link to user stories and PRDs
- Update after major feature releases

### DON'T ❌
- Create journey maps in isolation (involve users)
- Skip emotion tracking (it reveals priorities)
- Map ideal journeys (map reality, then improve)

---

**Template Instructions**: Create journey maps for each primary persona. Delete this message after creating your first journey map.
