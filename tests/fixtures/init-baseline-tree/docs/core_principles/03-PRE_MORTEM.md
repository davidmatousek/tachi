# Pre-Mortem Analysis Methodology

**Document Type:** Methodology Guide
**Category:** Decision Making, Risk Prevention
**Last Updated:** 2026-01-28
**Source:** Gary Klein (Cognitive Psychologist), "Performing a Project Premortem" (HBR 2007)

---

## What is Pre-Mortem?

A **Pre-Mortem** is a prospective hindsight technique where you imagine a project has already failed and work backward to identify what caused the failure. Unlike a post-mortem (which analyzes actual failures), a pre-mortem proactively surfaces risks before they materialize.

**Origin:** Developed by psychologist Gary Klein. Based on research showing that imagining an event has already occurred increases the ability to identify reasons for future outcomes by 30%.

**Core Question:** "What could go wrong?"

**Purpose:**
- Surface hidden risks before implementation begins
- Overcome optimism bias and groupthink
- Enable proactive mitigation strategies
- Create psychological safety to voice concerns

---

## When to Use

### Ideal Scenarios
- Before starting major feature development
- Before critical deployments or migrations
- When team consensus feels "too easy"
- Before customer-facing launches
- When stakes are high and failure is costly

### Less Suitable
- After problems have already occurred (use 5 Whys instead)
- For routine, well-understood tasks
- When immediate action is required
- For simple, low-risk decisions

---

## The Pre-Mortem Process

### 1. Set the Scene (2 min)

Announce: "Imagine it's [future date]. This project has **failed spectacularly**. Not just missed a deadline - completely failed."

**Key elements:**
- Use vivid, specific language ("catastrophic failure")
- Set a specific future date (launch day + 1 week)
- Emphasize that failure is assumed, not possible

### 2. Individual Silent Brainstorm (5-10 min)

Each participant writes down reasons for the failure **independently and silently**.

**Prompt:** "Write 3-5 reasons why this project failed. Be specific. Include technical, process, and people factors."

**Why silent?** Prevents anchoring bias and groupthink. Junior team members can voice concerns without social pressure.

### 3. Round-Robin Sharing (10-15 min)

Go around the room - each person shares **one reason at a time** until all reasons are captured.

**Rules:**
- No debate or defense during sharing
- Facilitator records all reasons verbatim
- Duplicates are noted but not dismissed
- Continue until all unique reasons are shared

### 4. Categorize and Prioritize (10 min)

Group failure reasons into categories and assess likelihood/impact.

| Category | Example Reasons |
|----------|----------------|
| **Technical** | Database migration corrupts data |
| **Process** | No rollback plan documented |
| **Dependencies** | Third-party API changes without notice |
| **Communication** | Stakeholders had different expectations |
| **Resources** | Key engineer on vacation during launch |

**Prioritize by:** Likelihood (High/Med/Low) x Impact (High/Med/Low)

### 5. Develop Mitigations (15-20 min)

For high-priority risks, create specific mitigation actions.

| Risk | Mitigation | Owner | Deadline |
|------|------------|-------|----------|
| No rollback plan | Document rollback procedure | DevOps | Before deploy |
| Data migration failure | Test migration on staging first | Backend | 3 days before |

---

## Best Practices

### Do's

1. **Make failure vivid and specific** - "Complete failure" not "some issues"
2. **Enforce silent brainstorming** - Prevents groupthink and anchoring
3. **Include diverse perspectives** - Junior engineers often spot risks seniors miss
4. **Focus on controllable factors** - "Our API has no rate limiting" not "Aliens invade"
5. **Document and track mitigations** - Pre-mortems without follow-up are theater
6. **Run before major decisions are final** - Early enough to change course

### Don'ts

1. **Don't allow debate during sharing** - Record all concerns without judgment
2. **Don't dismiss "unlikely" risks** - Low-probability, high-impact events matter
3. **Don't let optimists dominate** - Pre-mortems specifically counter optimism bias
4. **Don't skip the silent brainstorm** - Verbal brainstorming reduces unique ideas by 40%
5. **Don't do it once and forget** - Revisit risks as project evolves

---

## Common Pitfalls

### Pitfall 1: Anchoring on First Ideas

"The first person mentions 'database issues' and everyone's risks become database-related."

**Solution:** Enforce silent individual brainstorming before any sharing. Each person develops ideas independently first.

### Pitfall 2: Social Pressure to Be Positive

"Junior engineer doesn't want to seem negative by listing risks the senior architect hasn't mentioned."

**Solution:** Emphasize that finding risks is the goal, not a sign of pessimism. The team that finds more risks is doing better work.

### Pitfall 3: Generating Risks Without Mitigations

"Team lists 20 failure modes, feels good about being thorough, then never addresses any of them."

**Solution:** End every pre-mortem with assigned owners and deadlines for top 3-5 mitigations.

---

## Example: AI Security Scanner Application

### Context
Feature 014: Complete Quota and Usage Display Fix - Dashboard pages showing incorrect quota values to users.

### Hypothetical Pre-Mortem (Before Implementation)

**Scenario:** "It's November 1st. Feature 014 has failed. Users are still seeing wrong quota values, and some PRO users have been blocked from using paid features."

### Failure Reasons Identified

| # | Failure Reason | Category | Likelihood | Impact |
|---|----------------|----------|------------|--------|
| 1 | Frontend fallback values don't match database tier_quotas | Technical | High | High |
| 2 | SQL queries use hardcoded subscription tier instead of reading from DB | Technical | High | Critical |
| 3 | Backend API works but frontend never calls it correctly | Integration | Medium | High |
| 4 | Cache serves stale tier data after user upgrades | Technical | Medium | Medium |
| 5 | No E2E test verifies actual displayed values match database | Process | High | High |

### Mitigations Developed

| Risk | Mitigation | Owner |
|------|------------|-------|
| Hardcoded tier values | Audit all SQL queries for hardcoded 'free' tier | Backend |
| Missing E2E tests | Add Playwright test: login as PRO, verify quota shows correct limit | Tester |
| Stale cache | Add Cache-Control: no-store header to quota endpoints | Backend |
| Frontend fallback inaccuracy | Create TIER_DEFAULTS constant matching database values | Frontend |

### What Actually Happened (Post-Mortem)

Risks #1, #2, and #5 materialized in production:
- SQL queries had `'free' as subscription_tier` hardcoded (FRONTEND-QUOTA-002)
- Frontend used `tier === 'free' ? 1 : 3` instead of database values (FRONTEND-QUOTA-001)
- No E2E test caught either issue before production

**Lesson:** A pre-mortem would have surfaced these risks. The team would have audited SQL queries and added E2E tests before launch.

---

## Template

```markdown
# Pre-Mortem: [Project/Feature Name]

**Date:** YYYY-MM-DD | **Facilitator:** [Name] | **Duration:** X min

## The Scenario
"It's [future date]. This project has failed catastrophically. Here's why..."

## Failure Reasons (Silent Brainstorm Results)

| # | Failure Reason | Category | Likelihood | Impact |
|---|----------------|----------|------------|--------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

## Top Risks (Prioritized)
1. [Highest priority risk]
2. [Second priority risk]
3. [Third priority risk]

## Mitigations

| Risk | Mitigation Action | Owner | Deadline |
|------|-------------------|-------|----------|
| | | | |
| | | | |
| | | | |

## Follow-Up
- [ ] Mitigations assigned and tracked
- [ ] Revisit risks at [checkpoint date]
- [ ] Update if project scope changes
```

---

## Quick Reference Card

```
+---------------------------------------------------+
|  PRE-MORTEM QUICK REFERENCE                       |
+---------------------------------------------------+
|  1. Set the scene: "The project has FAILED"       |
|  2. Silent brainstorm (5-10 min, individually)    |
|  3. Round-robin sharing (no debate)               |
|  4. Categorize: Technical, Process, Dependencies  |
|  5. Prioritize: Likelihood x Impact               |
|  6. Develop mitigations with owners/deadlines     |
+---------------------------------------------------+
|  KEY PRINCIPLES:                                  |
|  - Failure is assumed, not possible               |
|  - Silent brainstorm prevents groupthink          |
|  - All concerns recorded without judgment         |
|  - Mitigations must have owners and deadlines     |
+---------------------------------------------------+
|  AVOID: Debating during sharing, skipping         |
|         silent brainstorm, generating risks       |
|         without mitigations                       |
+---------------------------------------------------+
```

---

## Related Lenses

- **5 Whys** - Use AFTER problems occur to find root cause (Pre-Mortem is for BEFORE)
- **First Principles** - Decompose assumptions that underlie identified risks
- **Inversion** - Related technique: "What would guarantee failure?" then avoid those actions
- **Constraint Analysis** - Identify which constraints could cause the failures imagined

---

*Part of the AI Security Scanner institutional knowledge base.*
