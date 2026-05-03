# Inversion Thinking

**Document Type:** Methodology Guide
**Category:** Decision Making, Risk Assessment
**Last Updated:** 2026-01-28
**Source:** Charlie Munger (Berkshire Hathaway), Carl Jacobi (mathematician)

---

## What is Inversion?

**Inversion** is a mental model that approaches problems backward by asking "What would guarantee failure?" instead of "How do I succeed?" By identifying and eliminating failure conditions, you create a clearer path to success.

**Origin:** The approach traces to mathematician Carl Jacobi's famous advice: "Invert, always invert" (*man muss immer umkehren*). Charlie Munger popularized it in business and investing, famously stating: "All I want to know is where I'm going to die, so I'll never go there."

**Core Question:** "What would guarantee failure?"

**Purpose:**
- Identify hidden risks and failure modes
- Avoid catastrophic mistakes before they happen
- Create robust plans by eliminating obvious failure paths
- Challenge assumptions by approaching problems from the opposite direction

---

## When to Use

### Ideal Scenarios
- Planning high-stakes projects or launches
- Evaluating strategic decisions with irreversible consequences
- Designing systems that must be reliable
- Assessing risks before major investments
- Creating checklists for critical processes

### Less Suitable
- Routine tasks with well-established procedures
- Situations requiring immediate creative ideation (use brainstorming first)
- When you lack sufficient context to identify failure modes
- Problems where success factors are already well-defined

---

## The Inversion Process

### 1. Define the Goal Clearly (5 min)

State what success looks like in specific, measurable terms.

| Good | Bad |
|------|-----|
| "Deploy MCP server to production with zero downtime and <500ms latency" | "Make deployment work" |
| "Ship feature X by Q2 with 95% test coverage" | "Finish the feature" |

### 2. Invert: Ask "What Would Guarantee Failure?" (15-20 min)

Brainstorm all the ways the project could fail catastrophically.

**Prompting questions:**
- What would make this completely impossible?
- What single mistake would doom the entire effort?
- What assumptions, if wrong, would cause total failure?
- What dependencies, if unavailable, would block everything?
- What would make stakeholders lose all confidence?

### 3. List and Prioritize Failure Modes (10 min)

Organize failures by severity and likelihood:

| Severity | Description |
|----------|-------------|
| **Catastrophic** | Project-ending, irreversible damage |
| **Severe** | Major setback, significant recovery effort |
| **Moderate** | Delays or rework, but recoverable |
| **Minor** | Inconvenience, easily addressed |

### 4. Create Anti-Failure Safeguards (15-20 min)

For each high-priority failure mode, define:
1. **Prevention**: How to avoid this failure entirely
2. **Detection**: How to notice it early if it starts happening
3. **Mitigation**: How to limit damage if it occurs

### 5. Validate Completeness (5 min)

Review your safeguards against the original goal:
- Does eliminating these failures make success more likely?
- Are there any obvious gaps remaining?
- Would a reasonable skeptic accept this plan?

---

## Best Practices

### Do's

1. **Be brutally honest** - List embarrassing failures, not just obvious ones
2. **Include human factors** - "Team burns out" is a valid failure mode
3. **Consider dependencies** - What external factors could fail you?
4. **Think about timing** - What could go wrong at each project phase?
5. **Involve diverse perspectives** - Different roles see different failure modes
6. **Document your inversions** - Create institutional memory of risks

### Don'ts

1. **Don't filter prematurely** - Write down all failures before evaluating
2. **Don't stop at the obvious** - "Server crashes" is just the beginning
3. **Don't ignore low-probability catastrophes** - Rare events with severe impact matter
4. **Don't use inversion alone** - Combine with forward-looking planning
5. **Don't paralyze with fear** - The goal is clarity, not avoidance of all action
6. **Don't forget to actually build safeguards** - Analysis without action is wasted

---

## Common Pitfalls

### Pitfall 1: Listing Only Technical Failures

**Problem:** "Database crashes, API times out, server runs out of memory..."

**Solution:** Include non-technical failures: communication breakdown, scope creep, key person leaves, budget cut, regulatory change, customer changes requirements.

**Better List:**
- Database crashes (technical)
- Key architect resigns mid-project (people)
- Customer redefines requirements after 80% complete (process)
- Compliance audit reveals blocking issues (regulatory)

### Pitfall 2: Surface-Level Inversions

**Problem:** "What would cause failure? Not finishing on time."

**Solution:** Go deeper. *Why* would you not finish on time? What specific conditions would cause that?

**Better Inversion:**
- Scope expands without timeline adjustment
- Unexpected technical debt in legacy system
- Integration partner delays API access
- Team velocity drops due to context switching

### Pitfall 3: Failing to Create Safeguards

**Problem:** Great list of failures, but no prevention or detection mechanisms.

**Solution:** Every high-priority failure needs at least one safeguard.

| Failure Mode | Prevention | Detection | Mitigation |
|--------------|------------|-----------|------------|
| Key person leaves | Cross-train, document decisions | Weekly 1:1s, engagement surveys | Succession plan, handoff docs |
| Scope creep | Change request process | Scope tracking metrics | Re-baseline with stakeholder |

---

## Example: AI Security Scanner Application

### Goal Statement
"Deploy MCP server to Railway production with zero unplanned downtime and all 27 security agents operational."

### Inversion Analysis

**Question: What would guarantee a failed production deployment?**

| # | Failure Mode | Severity | Category |
|---|--------------|----------|----------|
| 1 | Deploy without testing database connection | Catastrophic | Technical |
| 2 | Environment variables missing or incorrect | Catastrophic | Configuration |
| 3 | No rollback plan exists | Severe | Process |
| 4 | Security agents fail silently without alerting | Severe | Monitoring |
| 5 | SSL certificates expire during deployment window | Moderate | Infrastructure |
| 6 | No health check endpoint configured | Severe | Observability |
| 7 | Deploy on Friday afternoon before holiday | Moderate | Timing |
| 8 | Single person holds all deployment knowledge | Severe | People |

### Safeguards Created

| Failure | Prevention | Detection | Mitigation |
|---------|------------|-----------|------------|
| Missing env vars | Pre-deploy config validation script | Deploy fails fast with clear error | Documented env var checklist |
| No rollback plan | Rollback procedure in deployment guide | N/A | Keep previous version tagged |
| Silent agent failures | Health endpoint checks all 27 agents | Automated monitoring alerts | Agent-level health reporting |
| Solo knowledge holder | Pair deployments, written runbook | Code review requirements | Cross-train second person |

### Outcome
By inverting the deployment goal, we identified 8 failure modes and created specific safeguards. The deployment checklist now includes env var validation, health check verification, and a mandatory rollback test before go-live.

---

## Template

```markdown
# Inversion Analysis: [Project/Decision Name]

**Date:** YYYY-MM-DD | **Facilitator:** [Name] | **Duration:** X min

## Goal Statement
[Specific, measurable description of success]

## Failure Modes
| # | What Would Guarantee Failure? | Severity | Category |
|---|-------------------------------|----------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

## Safeguards
| Failure | Prevention | Detection | Mitigation |
|---------|------------|-----------|------------|
| | | | |
| | | | |
| | | | |

## Validation
- [ ] Does eliminating these failures make success likely?
- [ ] Are there obvious gaps?
- [ ] Would a skeptic accept this plan?

## Actions
| Safeguard to Implement | Owner | Deadline |
|------------------------|-------|----------|
| | | |
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  INVERSION QUICK REFERENCE                      |
+-------------------------------------------------+
|  Core Question: "What would guarantee failure?" |
+-------------------------------------------------+
|  1. Define goal clearly (measurable success)    |
|  2. Invert: List all failure modes              |
|  3. Prioritize by severity and likelihood       |
|  4. Create safeguards (prevent/detect/mitigate) |
|  5. Validate: Does this make success likely?    |
+-------------------------------------------------+
|  SEVERITY LEVELS:                               |
|  - Catastrophic: Project-ending, irreversible   |
|  - Severe: Major setback, hard recovery         |
|  - Moderate: Delays, but recoverable            |
|  - Minor: Inconvenience, easily fixed           |
+-------------------------------------------------+
|  FAILURE CATEGORIES:                            |
|  Technical, People, Process, External,          |
|  Configuration, Timing, Dependencies            |
+-------------------------------------------------+
|  AVOID: Surface-level inversions, ignoring      |
|  non-technical failures, analysis paralysis,    |
|  skipping safeguard implementation              |
+-------------------------------------------------+
```

---

## Related Lenses

- **Pre-Mortem** - Imagines project has already failed (Inversion asks what *would* cause failure)
- **Devil's Advocate** - Argues against a proposal (Inversion systematically lists failure modes)
- **First Principles** - Breaks down to fundamental truths (Inversion challenges by asking what breaks those truths)
- **5 Whys** - Finds root cause AFTER failure (Inversion prevents failure BEFORE it happens)

---

*Part of the AI Security Scanner institutional knowledge base.*
