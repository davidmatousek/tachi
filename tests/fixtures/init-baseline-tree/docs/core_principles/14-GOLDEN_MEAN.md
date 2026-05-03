# Golden Mean Analysis

**Document Type:** Methodology Guide
**Category:** Decision Making, Calibration
**Last Updated:** 2026-02-08
**Source:** Aristotle (Nicomachean Ethics), with practical wisdom (phronesis) principles

---

## What is Golden Mean Analysis?

**Golden Mean Analysis** is a calibration framework for finding the right balance on a spectrum where both too little and too much cause problems. Unlike choosing between discrete options (Comparative Analysis) or quantifying trade-offs (Opportunity Cost), the Golden Mean helps you find the contextual sweet spot on a continuous scale.

**Origin:** Aristotle argued in the *Nicomachean Ethics* that virtue lies at the desirable middle between two extremes of deficiency and excess. Courage is the mean between cowardice and recklessness. Generosity is the mean between stinginess and extravagance. Critically, the mean is not a mathematical midpoint. It varies by context, by person, and by situation. Finding the mean requires *phronesis* (practical wisdom) developed through experience and reflection.

**Core Question:** "Where is the right balance between too little and too much?"

**Purpose:**
- Calibrate agent autonomy, testing depth, documentation level, and other spectrum decisions
- Avoid both under-engineering and over-engineering
- Identify when you've drifted toward an extreme
- Build feedback loops that maintain balance over time
- Make "how much?" decisions with structured reasoning

---

## When to Use

### Ideal Scenarios
- Deciding how much autonomy to give an AI agent
- Calibrating testing depth (too little vs. too much)
- Setting documentation levels for a project
- Determining process ceremony (too loose vs. too rigid)
- Establishing alert thresholds (false negatives vs. alert fatigue)
- Balancing security controls with usability
- Deciding how much abstraction to introduce

### Less Suitable
- Binary either/or decisions (use Comparative Analysis)
- Problems with a clear single right answer
- Situations where an extreme is genuinely correct (security of financial data is not a "find the middle" problem)
- When you lack experience with both extremes

---

## The Golden Mean Process

### 1. Identify the Quality Being Calibrated (5 min)

Name the positive quality you're trying to achieve. Frame it as something where both too little and too much are problematic.

| Good Framing | Bad Framing |
|--------------|-------------|
| "Agent autonomy level" | "Should we use agents?" (binary) |
| "Testing depth" | "Should we test?" (not a spectrum) |
| "Documentation thoroughness" | "Documentation" (too vague) |
| "Code review rigor" | "Code quality" (not specific to a calibration) |

### 2. Define the Extremes (10 min)

Map both ends of the spectrum with concrete symptoms and consequences.

**Deficiency (too little):**
- What does it look like when we have too little of this quality?
- What are the visible symptoms?
- What are the consequences?
- Who suffers?

**Excess (too much):**
- What does it look like when we have too much of this quality?
- What are the visible symptoms?
- What are the consequences?
- Who suffers?

| Dimension | Deficiency (Too Little) | Excess (Too Much) |
|-----------|------------------------|-------------------|
| **Looks like** | | |
| **Symptoms** | | |
| **Consequences** | | |
| **Who suffers** | | |

### 3. Assess Current Position (10 min)

Determine where you currently sit on the spectrum using evidence, not feelings.

**Evidence collection:**
- What do metrics say? (Quantitative)
- What do team members say? (Qualitative)
- What do incidents or friction points reveal? (Behavioral)
- What does an outsider see? (External perspective)

**Position indicators:**

| Signal | Points Toward Deficiency | Points Toward Excess |
|--------|--------------------------|----------------------|
| Team feedback | "We need more X" | "X is slowing us down" |
| Incidents | Problems from lack of X | Problems from too much X |
| Velocity | Fast but fragile | Thorough but slow |
| Quality | Gaps and misses | Diminishing returns |

### 4. Find the Contextual Mean (15-20 min)

The mean is not the midpoint. It depends on your specific context. Consider:

**Context factors that shift the mean:**

| Factor | Shifts Mean Toward More | Shifts Mean Toward Less |
|--------|------------------------|------------------------|
| **Risk level** | High stakes, irreversible | Low stakes, reversible |
| **Team experience** | Junior team, new domain | Senior team, familiar domain |
| **System maturity** | Production, customer-facing | Prototype, internal tool |
| **Pace requirements** | Can afford thoroughness | Must move fast |
| **Regulatory environment** | Heavily regulated | Minimal compliance needs |

**Formulate your mean:**
- Given these context factors, the right level is: [specific description]
- This means we will: [concrete actions]
- This means we will NOT: [what we're deliberately skipping]

### 5. Build Feedback Loops (10 min)

The mean drifts over time. Build mechanisms to detect drift and adjust.

**Feedback mechanisms:**

| Mechanism | Frequency | Detects |
|-----------|-----------|---------|
| **Leading indicator** | Real-time | Early drift toward either extreme |
| **Team retrospective** | Weekly/biweekly | Qualitative sense of balance |
| **Incident correlation** | Per incident | Whether incidents relate to calibration |
| **Periodic reassessment** | Monthly/quarterly | Context changes requiring recalibration |

**Drift detection questions:**
- Have any incidents been caused by too little or too much of this quality?
- Is the team complaining about either extreme?
- Has our context changed (new regulations, new team members, new scale)?
- Are we still getting value from our current calibration?

---

## Best Practices

### Do's

1. **Name both extremes explicitly** - You can't find the middle if you haven't mapped the edges
2. **Use context, not averages** - The mean for a bank's security is different from a startup's
3. **Build in adjustment** - Set a review date when you define the mean
4. **Collect evidence from both sides** - Talk to people who want more AND people who want less
5. **Accept that the mean moves** - As teams grow, systems mature, and context changes, recalibrate
6. **Start slightly toward deficiency** - It's easier to add more than to remove excess

### Don'ts

1. **Don't split the difference** - The mean is not always the midpoint; it's contextual
2. **Don't treat all spectrums equally** - Some qualities (like security of sensitive data) warrant being closer to excess
3. **Don't set and forget** - The golden mean requires ongoing attention
4. **Don't ignore legitimate extremes** - Sometimes the right answer IS at one end
5. **Don't use this to avoid commitment** - "Let's be moderate" is not always wisdom; sometimes decisiveness matters
6. **Don't average opinions** - If half the team wants more and half wants less, that doesn't mean the middle is right

---

## Common Pitfalls

### Pitfall 1: False Equivalence of Extremes

**Problem:** Assuming both extremes are equally bad. "Too much security" and "too little security" are not symmetrical risks. Under-securing a payment system is catastrophically worse than over-securing it.

**Solution:** Assess the asymmetry of consequences. If one extreme is dramatically worse than the other, the mean should shift away from the dangerous extreme.

**Detection:** Ask "If I had to err, which side would I rather err on?" If the answer is obvious, the mean isn't in the center.

### Pitfall 2: Ignoring the Contextual Shift

**Problem:** Setting a "golden mean" once and never revisiting it. What was balanced for a 5-person startup is not balanced for a 500-person company.

**Solution:** Tie recalibration to context triggers: team size changes, system scale changes, regulatory changes, major incidents.

**Detection:** Ask "Has anything significant changed since we last calibrated this?"

### Pitfall 3: Analysis as Procrastination

**Problem:** Using "finding the balance" as an excuse to avoid committing to a position.

**Solution:** Set a time box. If you can't determine the mean in 30 minutes, pick the best-guess position and set a 2-week review. Action with adjustment beats perfect calibration.

**Detection:** If the team has discussed "how much X" more than three times without deciding, you're procrastinating.

### Pitfall 4: Confusing Process with Outcome

**Problem:** Calibrating the amount of *process* (meetings, reviews, documentation) when the real spectrum is the *outcome* (quality, reliability, speed).

**Solution:** Frame the spectrum as an outcome, not a process. Instead of "how many code reviews?" ask "what level of code quality do we need, and what's the minimum review process to achieve it?"

---

## Example: AI Agent Autonomy Calibration

### Context
A development team is deploying an AI coding agent and needs to determine the right level of autonomy.

### Golden Mean Analysis

**Step 1: Quality Being Calibrated**
Agent Autonomy: The degree of independent decision-making granted to the AI coding agent.

**Step 2: Define the Extremes**

| Dimension | Deficiency (Too Constrained) | Excess (Too Autonomous) |
|-----------|------------------------------|------------------------|
| **Looks like** | Agent requires human approval for every action, including reading files | Agent independently creates PRs, modifies CI, changes dependencies |
| **Symptoms** | Developers spend more time approving than the agent saves; constant interruptions | Unexpected changes in production; trust erosion; "who changed this?" confusion |
| **Consequences** | Agent adoption drops; team reverts to manual work; investment wasted | Production incidents from unapproved changes; security vulnerabilities; audit failures |
| **Who suffers** | Developers (frustration), business (no ROI on AI investment) | Users (reliability), security team (exposure), developers (cleanup) |

**Step 3: Current Position Assessment**

| Signal | Evidence |
|--------|----------|
| Team feedback | "The agent asks for permission too often for trivial things" (leaning toward deficiency) |
| Incidents | Zero agent-caused incidents (could mean well-calibrated OR too constrained) |
| Velocity | Agent saves ~20% of time, but approval overhead eats back ~8% |
| Quality | Agent output quality is high when it does act |

**Assessment:** Currently slightly over-constrained. Net time savings are only 12% when they should be higher.

**Step 4: Contextual Mean**

| Factor | Our Context | Implication |
|--------|-------------|-------------|
| Risk level | Internal tools (medium risk) | Can afford more autonomy than customer-facing |
| Team experience | Senior team, familiar with codebase | Less oversight needed |
| System maturity | Established codebase, good test coverage | Safety net exists for catching issues |
| Pace requirements | Quarterly releases, not time-critical | Can accept some review overhead |
| Regulatory | No specific AI regulations apply | Fewer compliance constraints |

**The Mean for Our Context:**

| Agent CAN autonomously | Agent MUST request approval | Agent MUST notify (no wait) |
|------------------------|----------------------------|-----------------------------|
| Read any file in repo | Merge to main | Dependency version updates |
| Create/switch branches | Modify CI/CD config | Refactoring existing code |
| Generate code changes | Access secrets/credentials | Creating new files |
| Run tests and linters | Delete files or branches | |
| Create draft PRs | External API calls | |

**Step 5: Feedback Loops**

| Mechanism | Frequency | What We Watch |
|-----------|-----------|---------------|
| Agent action log review | Weekly | Are autonomous actions causing issues? |
| Developer satisfaction survey | Monthly | Do developers feel the balance is right? |
| Incident correlation | Per incident | Was an agent action involved? |
| Autonomy expansion review | Quarterly | Should we grant more autonomy based on track record? |

**Drift triggers for recalibration:**
- Any production incident caused by agent action (shift toward less autonomy)
- Developer approval fatigue > 20% of agent interactions (shift toward more autonomy)
- New team members join (temporarily shift toward less autonomy until they're familiar)
- Regulatory requirements change (recalibrate immediately)

### Outcome
The team adjusted from "approve everything" to a tiered autonomy model. Net time savings increased from 12% to 28%. Zero incidents in the first quarter. The quarterly review will assess whether to expand autonomous actions further.

---

## Template

```markdown
# Golden Mean Analysis: [Quality Being Calibrated]

**Date:** YYYY-MM-DD | **Analyst:** [Name] | **Duration:** X min

## Quality Being Calibrated
[Name the spectrum: what quality, and why both extremes are problematic]

## Extremes
| Dimension | Deficiency (Too Little) | Excess (Too Much) |
|-----------|------------------------|-------------------|
| Looks like | | |
| Symptoms | | |
| Consequences | | |
| Who suffers | | |

## Current Position
| Signal | Evidence | Leans Toward |
|--------|----------|--------------|
| Team feedback | | Deficiency / Excess |
| Incidents | | Deficiency / Excess |
| Velocity | | Deficiency / Excess |
| Quality | | Deficiency / Excess |

**Assessment:** Currently [over-constrained / well-balanced / over-extended]

## Contextual Mean
| Factor | Our Context | Shifts Mean Toward |
|--------|-------------|-------------------|
| Risk level | | More / Less |
| Team experience | | More / Less |
| System maturity | | More / Less |
| Pace requirements | | More / Less |
| Regulatory | | More / Less |

**The Mean:** [Specific description of the right balance for this context]

## Feedback Loops
| Mechanism | Frequency | Detects |
|-----------|-----------|---------|
| | | |

**Recalibration triggers:**
- [Specific events that should trigger reassessment]

## Actions
| Adjustment | Rationale | Review Date |
|------------|-----------|-------------|
| | | |
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  GOLDEN MEAN QUICK REFERENCE                    |
+-------------------------------------------------+
|  Core Question: "Where is the right balance     |
|                  between too little and too      |
|                  much?"                          |
+-------------------------------------------------+
|  1. Name the quality being calibrated           |
|  2. Define both extremes (deficiency + excess)  |
|  3. Assess current position with evidence       |
|  4. Find contextual mean (not the midpoint!)    |
|  5. Build feedback loops for drift detection     |
+-------------------------------------------------+
|  KEY PRINCIPLE:                                 |
|  The mean is NOT the midpoint. It depends on:   |
|  - Risk level of the domain                     |
|  - Team experience and maturity                 |
|  - System criticality                           |
|  - Pace requirements                            |
|  - Regulatory environment                       |
+-------------------------------------------------+
|  COMMON SPECTRUMS:                              |
|  - Agent autonomy (constrained ↔ independent)   |
|  - Testing depth (minimal ↔ exhaustive)         |
|  - Documentation (sparse ↔ comprehensive)       |
|  - Process ceremony (none ↔ bureaucratic)       |
|  - Abstraction level (concrete ↔ over-abstract) |
+-------------------------------------------------+
|  AVOID: Splitting the difference, set-and-      |
|  forget, false equivalence of extremes,         |
|  confusing process with outcome                 |
+-------------------------------------------------+
```

---

## Related Lenses

- **Comparative Analysis** - Chooses between discrete options; Golden Mean calibrates a continuous spectrum
- **Opportunity Cost** - Quantifies what you give up; Golden Mean finds where giving up is minimized on both sides
- **Cargo Cult Detection** - Can reveal when "balance" is actually just following convention without measuring outcomes
- **Four Causes** - Understanding purpose (final cause) helps determine what "enough" means for each quality

---

*Part of the Agentic-Oriented Development thinking methodology collection.*
