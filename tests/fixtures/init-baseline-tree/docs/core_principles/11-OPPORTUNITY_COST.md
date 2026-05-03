# Opportunity Cost

**Document Type:** Methodology Guide
**Category:** Economic Thinking, Resource Allocation
**Last Updated:** 2026-01-28
**Source:** Austrian Economics (Friedrich von Wieser, 1914), Modern Decision Theory

---

## What is Opportunity Cost?

**Opportunity Cost** is the value of the next-best alternative that must be given up when making a choice. Every decision to do X is simultaneously a decision not to do Y, Z, and everything else. Understanding opportunity cost makes these trade-offs explicit.

**Origin:** The concept was formalized by Austrian economist Friedrich von Wieser in 1914, though the underlying idea appears in economics as far back as 1659. The term "opportunity cost" was coined to emphasize that costs are not just what you pay, but what you forgo.

**Purpose:**
- Make hidden trade-offs visible
- Improve resource allocation decisions
- Prevent sunk cost fallacy
- Enable better prioritization

---

## When to Use

### Ideal Scenarios
- Deciding between competing priorities with limited resources
- Evaluating whether to continue or abandon a project
- Assessing feature prioritization trade-offs
- Making build vs buy decisions
- Time allocation decisions (what to work on)

### Less Suitable
- Decisions with no meaningful alternatives
- Situations where all options must be pursued
- When alternatives are incomparable (apples vs oranges)
- Emergency situations requiring immediate action
- Routine decisions with negligible trade-offs

---

## The Opportunity Cost Process

### 1. Identify the Decision (5 min)

Clearly state the choice being made and the resource being allocated.

| Good Decision Statement | Bad Decision Statement |
|------------------------|----------------------|
| "Allocate 2 sprints to Feature A vs Feature B" | "Should we do Feature A?" |
| "Invest $50K in marketing vs engineering hire" | "Need to spend budget" |

**Key Resources:**
- Time (team hours, calendar time)
- Money (budget, investment)
- Attention (management focus, mindshare)
- Capacity (compute, infrastructure)

### 2. List Alternatives (10 min)

Enumerate what else could be done with the same resources.

**For Time:** What other features, fixes, or improvements could be built?
**For Money:** What other investments could be made?
**For Attention:** What other priorities could leadership focus on?

Include at least 3 alternatives. The "do nothing" option counts.

### 3. Estimate Value of Each Alternative (15-20 min)

For each alternative, estimate the expected value:

| Value Dimension | Questions to Ask |
|-----------------|------------------|
| **Revenue Impact** | Will this generate or protect revenue? How much? |
| **Cost Savings** | Will this reduce expenses? By how much? |
| **User Value** | How many users benefit? How significantly? |
| **Strategic Value** | Does this enable future opportunities? |
| **Risk Reduction** | Does this prevent or mitigate risks? |

Use ranges when uncertain: "Revenue impact: $10K-$50K over 12 months"

### 4. Identify the Next-Best Alternative (5 min)

The opportunity cost is the value of the single best alternative forgone.

**Not** the sum of all alternatives.
**Not** the average of alternatives.
**Only** the value of the next-best option you're giving up.

### 5. Make the Trade-off Explicit (10 min)

State the decision as: "By choosing X, we are giving up Y, which would have provided Z value."

This forces acknowledgment of what is sacrificed, not just what is gained.

### 6. Document and Revisit (5 min)

Record the analysis. Opportunity costs change as conditions change. Revisit major decisions quarterly.

---

## Best Practices

### Do's

1. **Consider non-monetary value** - User satisfaction, team morale, learning have real value
2. **Use ranges for estimates** - Precision implies false confidence
3. **Include "do nothing"** - Sometimes the best alternative is inaction
4. **Think in time horizons** - Short-term vs long-term opportunity costs differ
5. **Account for reversibility** - Irreversible decisions have higher opportunity costs
6. **Make trade-offs public** - Stakeholders should know what was sacrificed

### Don'ts

1. **Don't ignore sunk costs** - Past investment is irrelevant to opportunity cost
2. **Don't sum all alternatives** - Opportunity cost is only the next-best option
3. **Don't compare incomparables** - Ensure alternatives use the same resources
4. **Don't forget hidden costs** - Maintenance, support, complexity have opportunity costs
5. **Don't skip the "why not"** - Document why alternatives were rejected

---

## Common Pitfalls

### Pitfall 1: Sunk Cost Fallacy
Continuing a failing project because of past investment, ignoring what else could be done.

**Signs:** "We've already spent 6 months on this" as justification to continue

**Fix:** Ask: "If we started today with no prior investment, would we choose this?" Past costs are gone regardless of future choice.

### Pitfall 2: Invisible Alternatives
Failing to consider what else could be done, making the trade-off invisible.

**Signs:** "We should do X" without discussing Y and Z

**Fix:** Force enumeration of at least 3 alternatives before any decision. "What else could we do with these resources?"

### Pitfall 3: Overvaluing Certainty
Choosing a known, lower-value option over an uncertain, higher-value option due to risk aversion.

**Signs:** Choosing safe features over innovative ones systematically

**Fix:** Use expected value (probability x outcome) to compare. Account for upside, not just downside.

### Pitfall 4: Ignoring Compound Effects
Missing how today's opportunity cost compounds over time.

**Signs:** Prioritizing quick wins over foundational work repeatedly

**Fix:** Model long-term impact. A 2-week investment in tooling might save 100 hours over 12 months.

---

## Example: AI Security Scanner Application

### Decision Context
"Should we delay Feature 023 (Tier System) by 2 weeks to fix performance issues affecting scan speed?"

### Resource Being Allocated
2 weeks of engineering time (1 senior engineer)

### Alternatives

| Alternative | Description |
|-------------|-------------|
| **A: Fix Performance** | Address scan speed issues now |
| **B: Ship Tier System** | Complete Feature 023 as planned |
| **C: Do Both Partially** | 1 week each, incomplete work |
| **D: Do Nothing** | Ship Tier System, ignore performance |

### Value Estimation

| Alternative | Revenue Impact | User Value | Strategic Value | Risk |
|-------------|---------------|------------|-----------------|------|
| A: Fix Performance | $0 direct | High (faster scans) | Medium (quality reputation) | Tier System delayed 2 weeks |
| B: Ship Tier System | $5K-15K MRR (paid tiers) | Medium (upgrade path) | High (monetization) | Performance debt compounds |
| C: Do Both Partially | Partial of each | Low (nothing complete) | Low (incomplete) | High (technical debt) |
| D: Do Nothing | $5K-15K MRR | Medium | High | Performance complaints grow |

### Next-Best Alternative
If we choose **A: Fix Performance**, the next-best alternative is **B: Ship Tier System**.

**Opportunity Cost:** $5K-15K in delayed MRR revenue over the delay period, plus 2 weeks delay in strategic monetization capability.

### Trade-off Statement
"By choosing to fix performance issues now, we are giving up 2 weeks of Tier System development, which would have generated $5K-15K in new MRR and enabled our monetization strategy. We accept this trade-off because performance issues are causing user churn that threatens our user base foundation."

### Decision
**Choose A: Fix Performance** - The long-term value of user retention exceeds the short-term value of delayed revenue. Performance issues compound (users leave, bad reviews) while revenue delay is recoverable.

---

## Template

```markdown
# Opportunity Cost Analysis: [Decision Name]

**Date:** YYYY-MM-DD | **Analyst:** [Name] | **Resource:** [Time/Money/Attention]

## Decision Statement
[What choice are we making? What resource is being allocated?]

## Alternatives

| # | Alternative | Description |
|---|-------------|-------------|
| A | | |
| B | | |
| C | | |
| D | Do Nothing | |

## Value Estimation

| Alternative | Revenue | User Value | Strategic | Risk/Cost |
|-------------|---------|------------|-----------|-----------|
| A | | | | |
| B | | | | |
| C | | | | |
| D | | | | |

## Next-Best Alternative
[Which single alternative is the next-best option?]

## Opportunity Cost
[Value of next-best alternative being given up]

## Trade-off Statement
"By choosing [X], we are giving up [Y], which would have provided [Z value].
We accept this trade-off because [rationale]."

## Decision
[Selected option] - [Brief rationale]

## Revisit Date
[When to re-evaluate this decision]
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  OPPORTUNITY COST QUICK REFERENCE               |
+-------------------------------------------------+
|  1. Identify the decision and resource          |
|  2. List alternatives (minimum 3)               |
|  3. Estimate value of each alternative          |
|  4. Identify the NEXT-BEST alternative          |
|  5. State trade-off explicitly:                 |
|     "By choosing X, we give up Y (value Z)"     |
|  6. Document and set revisit date               |
+-------------------------------------------------+
|  KEY INSIGHT:                                   |
|  Opportunity cost = Value of NEXT-BEST option   |
|  (not sum of all alternatives)                  |
+-------------------------------------------------+
|  VALUE DIMENSIONS:                              |
|  * Revenue impact                               |
|  * Cost savings                                 |
|  * User value                                   |
|  * Strategic value                              |
|  * Risk reduction                               |
+-------------------------------------------------+
|  AVOID: Sunk cost fallacy, invisible            |
|         alternatives, overvaluing certainty     |
+-------------------------------------------------+
```

---

## Related Lenses

- **Comparative Analysis** - Structured evaluation of alternatives opportunity cost identifies
- **Pareto Analysis** - Find the 20% of options delivering 80% of value
- **First Principles** - Question whether the alternatives are the right ones
- **Pre-Mortem** - Consider what happens if the chosen option fails
- **Inversion** - Ask "what would make this the wrong choice?"

---

*Part of the AI Security Scanner institutional knowledge base.*
