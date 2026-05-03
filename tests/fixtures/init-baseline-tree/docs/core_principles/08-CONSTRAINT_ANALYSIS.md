# Constraint Analysis

**Document Type:** Methodology Guide
**Category:** Problem Solving, Continuous Improvement
**Last Updated:** 2026-01-28
**Source:** Theory of Constraints (Eliyahu Goldratt)

---

## What is Constraint Analysis?

**Constraint Analysis** is a systematic approach to identifying and addressing the limiting factors that prevent a system from achieving its goals. Based on Eliyahu Goldratt's Theory of Constraints, it recognizes that every system has at least one constraint that limits its overall performance.

The core question is: **"What's blocking us?"** By identifying the true constraint - whether it's a resource, dependency, policy, or knowledge gap - teams can focus improvement efforts where they matter most rather than optimizing non-bottlenecks.

**Origin:** Developed by Eliyahu Goldratt in "The Goal" (1984). Foundational to Lean manufacturing, DevOps, and agile methodologies.

**Purpose:**
- Surface hidden constraints before they cause delays
- Focus improvement efforts on the actual bottleneck
- Prevent wasted optimization of non-constraints
- Enable proactive resource and dependency planning

---

## When to Use

### Ideal Scenarios
- Project delivery is slower than expected
- Teams report being blocked or waiting frequently
- Resources appear available but throughput remains low
- Recurring delays despite process improvements
- Cross-team dependencies causing unpredictable timelines

### Less Suitable
- Problems with clear, obvious single causes (use direct problem solving)
- Situations requiring immediate tactical response (fix first, analyze later)
- Purely technical bugs with no systemic component
- New projects without established workflows to analyze

---

## The Constraint Analysis Process

### 1. Map the Value Stream (10-15 min)

Identify all steps from request to delivery. Include:
- Work queues and handoffs
- Approval gates and reviews
- External dependencies
- Shared resources

**Output:** Visual flow diagram showing all stages

### 2. Identify the Constraint (15-20 min)

Look for signs of the bottleneck:
- Where does work pile up waiting?
- What step has the longest cycle time?
- Which resource is always at 100% utilization?
- What approval or dependency do people wait for most?

**Constraint Types:**
| Type | Example | Signs |
|------|---------|-------|
| **Resource** | Single expert, limited compute | Queue builds at that resource |
| **Dependency** | External API, third-party approval | Unpredictable wait times |
| **Policy** | Mandatory reviews, approval chains | Work blocked despite availability |
| **Knowledge** | Undocumented process, tribal knowledge | Frequent questions, rework |

### 3. Decide How to Exploit the Constraint (10 min)

Maximize throughput at the constraint without adding resources:
- Remove non-essential work from the constraint
- Ensure constraint is never idle (always has work ready)
- Improve quality of inputs to reduce rework at constraint

### 4. Subordinate Everything Else (10 min)

Align non-constraints to support the constraint:
- Don't overproduce upstream (creates WIP buildup)
- Prioritize what the constraint needs next
- Protect constraint time from interruptions

### 5. Elevate the Constraint (If Needed)

Only after exploitation and subordination:
- Add capacity at the constraint
- Automate constraint activities
- Cross-train to reduce resource constraints

**Warning:** Elevating before exploiting wastes resources and may move the constraint elsewhere without improving throughput.

---

## Best Practices

### Do's

1. **Start with observation, not assumptions** - Watch where work actually accumulates
2. **Distinguish symptoms from constraints** - Slow delivery is a symptom; the constraint causes it
3. **Validate with data** - Measure cycle times, queue depths, utilization rates
4. **Consider policy constraints** - Often the real blocker is a process rule, not a resource
5. **Re-evaluate after changes** - The constraint moves when you improve it
6. **Involve people at the constraint** - They understand the bottleneck best

### Don'ts

1. **Don't optimize everywhere equally** - Improving non-constraints doesn't improve throughput
2. **Don't add resources first** - Exploit the constraint before elevating it
3. **Don't ignore soft constraints** - Approval policies and cultural norms constrain as much as resources
4. **Don't assume the obvious** - The perceived bottleneck often isn't the actual constraint
5. **Don't stop at one constraint** - After fixing one, another emerges

---

## Common Pitfalls

### Pitfall 1: Optimizing Non-Constraints
**Problem:** Team automates a fast step while the actual bottleneck remains untouched.

**Example:** Speeding up code compilation when code review is the constraint.

**Solution:** Map the full value stream and identify where work queues before optimization.

### Pitfall 2: Confusing Busy with Constrained
**Problem:** A resource appears busy but isn't the throughput limiter.

**Example:** Developer is 100% utilized but work piles up waiting for security review.

**Solution:** Track where work *waits*, not where people are busy.

### Pitfall 3: Adding Resources Before Exploiting
**Problem:** Hiring or purchasing to fix a constraint before maximizing existing capacity.

**Example:** Adding a second reviewer when the first reviewer spends 40% of time on non-review tasks.

**Solution:** First remove waste and protect constraint time, then consider adding capacity.

### Pitfall 4: Ignoring Policy Constraints
**Problem:** Assuming all constraints are resource-based when policies create artificial bottlenecks.

**Example:** Mandatory 3-day security review for all changes, regardless of risk level.

**Solution:** Question policies that create wait time: "What risk does this policy mitigate? Is there a lighter-weight alternative?"

---

## Example: AI Security Scanner Application

### Problem Statement
"PyPI package upload consistently fails with 403 errors, causing 8+ hours of troubleshooting per release."

### Constraint Analysis

**Step 1: Map the Value Stream**
```
Code Change → Version Bump → Build Package → Upload to PyPI → Verify Installation
                                    ↓
                              [BLOCKED HERE]
```

**Step 2: Identify the Constraint**
| Stage | Cycle Time | Wait Time | Signs |
|-------|------------|-----------|-------|
| Code Change | 30 min | 0 | No queue |
| Version Bump | 5 min | 0 | No queue |
| Build Package | 2 min | 0 | No queue |
| **Upload to PyPI** | **Variable** | **8+ hours** | **Repeated failures** |
| Verify Installation | 5 min | 0 | No queue |

**Constraint Identified:** PyPI upload step - but what's the *actual* constraint?

**Step 3: Root Cause of Constraint**
| Constraint Type | Analysis | Finding |
|-----------------|----------|---------|
| Resource | Is twine/upload capacity limited? | No - PyPI handles many uploads |
| Dependency | Is PyPI API unreliable? | No - works for others |
| **Policy** | Are we following correct procedures? | **Partially** |
| **Knowledge** | Do we understand token formatting? | **No - gap identified** |

**Actual Constraint:** Knowledge gap about token formatting requirements (whitespace sensitivity, `tr -d '\n\r'` required)

**Step 4: Exploit the Constraint**
- Document exact working command sequence
- Create pre-upload checklist with token validation
- Add `tr -d '\n\r'` to token retrieval step

**Step 5: Subordinate Other Steps**
- Clean build directory before every upload (support constraint)
- Validate package with `twine check` before upload attempt
- Increment version only after successful upload

### Solutions Implemented
1. **Documented procedure:** Exact command sequence in INSTITUTIONAL_KNOWLEDGE.md
2. **Token cleaning:** `tr -d '\n\r'` removes hidden whitespace
3. **Pre-upload validation:** Clean build + twine check before upload
4. **Result:** Upload time reduced from 8+ hours to <5 minutes

---

## Template

```markdown
# Constraint Analysis: [System/Process Name]

**Date:** YYYY-MM-DD | **Analyst:** [Name] | **Duration:** X min

## Value Stream Map
[List or diagram of all steps from request to delivery]

## Constraint Identification
| Stage | Cycle Time | Wait Time | Utilization | Queue Depth |
|-------|------------|-----------|-------------|-------------|
| | | | | |

**Identified Constraint:** [Stage or resource name]

## Constraint Type Classification
- [ ] Resource constraint (person, tool, compute)
- [ ] Dependency constraint (external system, approval)
- [ ] Policy constraint (process rule, requirement)
- [ ] Knowledge constraint (documentation, expertise)

## Exploitation Strategy
[How to maximize throughput at constraint without adding resources]

## Subordination Changes
[How other steps will change to support the constraint]

## Elevation Plan (if needed)
[Additional capacity or automation to add after exploitation]

## Success Metrics
| Metric | Before | Target | After |
|--------|--------|--------|-------|
| | | | |
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  CONSTRAINT ANALYSIS QUICK REFERENCE            |
|-------------------------------------------------|
|  Core Question: "What's blocking us?"           |
|-------------------------------------------------|
|  1. Map value stream (all steps, queues)        |
|  2. Identify constraint (where work waits)      |
|  3. Exploit (maximize without adding resources) |
|  4. Subordinate (align others to constraint)    |
|  5. Elevate (add capacity only if needed)       |
|-------------------------------------------------|
|  CONSTRAINT TYPES:                              |
|  - Resource: Person, tool, compute at 100%      |
|  - Dependency: External system, approval        |
|  - Policy: Process rule creating wait time      |
|  - Knowledge: Missing documentation/expertise   |
|-------------------------------------------------|
|  KEY INSIGHT: Improving non-constraints         |
|  does NOT improve system throughput.            |
+-------------------------------------------------+
```

---

## Related Lenses

- **Pre-Mortem** - Anticipate constraints before they materialize; use Constraint Analysis when they've already appeared
- **Systems Thinking** - Understand how constraints interact with other system components
- **Second-Order Effects** - Consider what new constraints emerge after fixing the current one

---

*Part of the AI Security Scanner institutional knowledge base.*
