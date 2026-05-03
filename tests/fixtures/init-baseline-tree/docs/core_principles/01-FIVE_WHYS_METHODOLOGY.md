# 5 Whys Root Cause Analysis Methodology

**Document Type:** Methodology Guide
**Category:** Problem Solving, Continuous Improvement
**Last Updated:** 2026-01-28
**Source:** Atlassian Team Playbook, Toyota Production System

---

## What is 5 Whys?

The **5 Whys** is an iterative interrogative technique to identify root causes. By repeatedly asking "Why?" (typically 3-7 times), you move beyond symptoms to discover underlying systemic issues.

**Origin:** Developed by Sakichi Toyoda (Toyota). Core practice in Lean manufacturing and Six Sigma.

**Purpose:**
- Identify root causes, not symptoms
- Prevent problem recurrence
- Focus on processes, not people

---

## When to Use

### Ideal Scenarios ✅
- Recurring problems despite fixes
- Post-mortem analysis after incidents
- Projects that underperform expectations
- Team retrospectives

### Less Suitable ❌
- Complex problems with multiple root causes (use Fishbone Diagram)
- Problems requiring quantitative analysis
- Situations needing immediate action
- Obvious single-step root causes

---

## The 5 Whys Process

### 1. Define the Problem Statement (5 min)

Be **specific**, **factual**, **singular**, and **measurable**.

| Good | Bad |
|------|-----|
| "Test pass rate remained at 8.26% after implementing 20 step definitions" | "Tests don't work" |
| "Deployment failed at 3:42 PM with error X" | "Deployment is broken" |

### 2. Ask "Why?" Iteratively (30-45 min)

For each answer:
1. Brainstorm possible causes
2. Select the most likely/impactful
3. Turn it into the next "Why?"
4. Repeat until you reach a **root cause**

**Root cause signs:**
- ✅ Fixing it prevents recurrence
- ✅ It's a process/system issue, not a person
- ✅ Further "whys" become repetitive
- ✅ Team agrees it's fundamental

### 3. Validate the Root Cause

Ask two questions:
1. "If we fix this, will the problem go away?" → Must be YES
2. "Can we reproduce by reintroducing this cause?" → Must be YES

### 4. Implement Solutions (15 min)

- Focus on systemic fixes, not patches
- Assign owners and deadlines
- Track progress and follow up

---

## Best Practices

### Do's ✅

1. **Create blame-free environment** - Focus on systems, not individuals
2. **Use data and facts** - Base answers on evidence, not assumptions
3. **Ask "Why?" about processes** - "Why did the process allow this?"
4. **Go deep enough** - Don't stop at surface-level answers
5. **Document everything** - Record questions, answers, and evidence
6. **Validate the root cause** - Test with the two validation questions

### Don'ts ❌

1. **Don't blame people** - "Why did Bob fail?" → Wrong. Ask about the process.
2. **Don't accept vague answers** - "Communication was poor" → Not actionable
3. **Don't stop too soon** - "We were busy" is not a root cause
4. **Don't skip implementation** - Analysis without action is wasted effort

---

## Common Pitfalls

### Pitfall 1: Stopping at Symptoms
❌ "Server crashed" → "Memory ran out" → STOP

✅ Keep asking: Why no monitoring? Why no alerts? Why isn't it in the deployment checklist?

**Root Cause:** "Deployment checklist lacks monitoring setup"

### Pitfall 2: Blaming People
❌ "Engineer forgot to test"

✅ "Why was deployment possible without test validation?"

**Root Cause:** "Pipeline lacks automated test gates"

### Pitfall 3: Accepting "Human Error"
❌ "Data deleted by mistake"

✅ "Why was it possible to delete production data without confirmation?"

**Root Cause:** "Database lacks delete protection mechanisms"

---

## Example: Real-World Application

### Problem Statement
"After implementing 20 step definitions (~1,022 lines), the BDD test pass rate remained at 8.26% with zero improvement."

### 5 Whys Analysis

| # | Why? | Answer | Evidence |
|---|------|--------|----------|
| 1 | Why no improvement? | Steps didn't match actual patterns | 346 undefined steps remain |
| 2 | Why wrong patterns? | Analysis used stale data | Old file vs current dry-run |
| 3 | Why stale data? | Workflow prioritized speed | Plan says "grep output from old file" |
| 4 | Why prioritize speed? | No validation checkpoint | No freshness requirements |
| **5** | **Why no checkpoint?** | **Workflow assumed perfect execution** | **No automated checks** |

### Root Cause
**"Workflow lacks defensive validation gates, allowing stale data to propagate without detection."**

### Solutions Implemented
1. Data freshness requirements (<1 hour old)
2. Incremental validation gates (test every 3-5 steps)
3. Pattern verification against feature files

---

## Template

```markdown
# 5 Whys: [Problem Name]

**Date:** YYYY-MM-DD | **Facilitator:** [Name] | **Duration:** X min

## Problem Statement
[Specific, measurable description]

## Analysis
| # | Why? | Answer | Evidence |
|---|------|--------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

## Root Cause
[Systemic issue identified]

## Validation
- [ ] If we fix this, will the problem go away?
- [ ] Can we reproduce by reintroducing this cause?

## Solutions
| Solution | Owner | Deadline |
|----------|-------|----------|
| | | |
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  5 WHYS QUICK REFERENCE                         │
├─────────────────────────────────────────────────┤
│  1. Define specific problem statement           │
│  2. Ask "Why?" - brainstorm answers             │
│  3. Select most likely cause                    │
│  4. Turn answer into next "Why?"                │
│  5. Repeat until root cause found (3-7 times)   │
│  6. Validate: "If we fix this, will it          │
│     prevent recurrence?"                        │
│  7. Implement solutions with owners/deadlines   │
├─────────────────────────────────────────────────┤
│  ROOT CAUSE SIGNS:                              │
│  ✓ Process/system issue (not person)            │
│  ✓ Fixing it prevents recurrence                │
│  ✓ Team agrees it's fundamental                 │
├─────────────────────────────────────────────────┤
│  AVOID: Blaming people, stopping too soon,      │
│         vague answers, skipping implementation  │
└─────────────────────────────────────────────────┘
```

---

## Related Lenses

- **Pre-Mortem** - Use BEFORE problems occur (5 Whys is for AFTER)
- **First Principles** - Challenge assumptions that led to the problem
- **Pareto Analysis** - Identify which 20% of causes drive 80% of problems

---

*Part of the AI Security Scanner institutional knowledge base.*
