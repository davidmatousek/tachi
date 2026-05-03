# Comparative Analysis

**Document Type:** Methodology Guide
**Category:** Decision Making, Option Evaluation
**Last Updated:** 2026-01-28
**Source:** Decision Science, Multi-Criteria Decision Analysis (MCDA)

---

## What is Comparative Analysis?

**Comparative Analysis** is a structured evaluation technique for objectively assessing multiple alternatives against defined criteria. Rather than relying on intuition or preference, it uses weighted scoring to identify the best option among competing choices.

**Origin:** Rooted in operations research and decision science, formalized as Multi-Criteria Decision Analysis (MCDA) in the 1960s-70s. Used extensively in business strategy, technology selection, and policy decisions.

**Purpose:**
- Evaluate alternatives objectively with explicit criteria
- Make trade-offs visible and discussable
- Document decision rationale for future reference
- Reduce bias in option selection

---

## When to Use

### Ideal Scenarios
- Choosing between technology platforms or vendors
- Evaluating multiple implementation approaches
- Comparing build vs buy decisions
- Selecting between cloud providers or hosting options
- Any decision with 2+ viable alternatives

### Less Suitable
- Single obvious choice with no real alternatives
- Decisions driven by non-negotiable constraints
- When criteria cannot be meaningfully weighted
- Exploratory phases before options are defined
- When quantitative data is unavailable for key criteria

---

## The Comparative Analysis Process

### 1. Define the Decision Context (5 min)

State what you're deciding and why it matters.

| Good Context Statement | Bad Context Statement |
|----------------------|----------------------|
| "Select hosting platform for backend API to balance cost, scalability, and operational simplicity" | "Pick a cloud provider" |
| "Choose authentication library that meets security requirements and developer experience goals" | "Need auth somehow" |

### 2. Identify Alternatives (10 min)

List all viable options. Include 3-6 alternatives for meaningful comparison.

**Tips:**
- Include current state as a baseline option
- Consider "do nothing" if applicable
- Add at least one unconventional option
- Verify all options are actually feasible

### 3. Define Evaluation Criteria (15 min)

Select 5-8 criteria that matter for this decision:

| Criteria Category | Examples |
|-------------------|----------|
| **Cost** | Initial cost, ongoing cost, total cost of ownership |
| **Technical** | Performance, scalability, reliability, security |
| **Operational** | Ease of deployment, monitoring, maintenance |
| **Strategic** | Vendor stability, ecosystem, future flexibility |
| **Team** | Learning curve, existing skills, documentation |

### 4. Weight the Criteria (10 min)

Assign weights totaling 100% based on relative importance.

**Weighting Methods:**
- **Direct assignment:** Team agrees on percentages
- **Pairwise comparison:** Compare criteria two at a time
- **Rank ordering:** Rank criteria, distribute weights by rank

### 5. Score Each Alternative (20-30 min)

Rate each alternative against each criterion on a consistent scale (1-5 or 1-10).

**Scoring Guidelines:**
- 1 = Poor / Does not meet requirement
- 3 = Acceptable / Meets minimum requirement
- 5 = Excellent / Exceeds requirement

Use evidence, not opinion. Document why each score was given.

### 6. Calculate Weighted Scores (5 min)

For each alternative: Sum of (Weight x Score) across all criteria.

### 7. Analyze and Decide (10 min)

- Review overall scores
- Check for criteria where one option dominates
- Consider sensitivity: Would different weights change the outcome?
- Make decision and document rationale

---

## Best Practices

### Do's

1. **Include diverse perspectives** - Different stakeholders weight criteria differently
2. **Use evidence for scoring** - Reference benchmarks, documentation, past experience
3. **Document assumptions** - Make scoring rationale explicit
4. **Test sensitivity** - Adjust weights +/-10% to see if outcome changes
5. **Keep criteria independent** - Avoid overlap between criteria
6. **Revisit if context changes** - Decisions age; re-evaluate periodically

### Don'ts

1. **Don't manipulate weights** - Adjusting weights to get desired outcome defeats the purpose
2. **Don't include irrelevant criteria** - Only criteria that differentiate options
3. **Don't score without evidence** - "I feel like" is not a valid score justification
4. **Don't ignore close results** - Similar scores indicate the decision is a toss-up
5. **Don't skip the "why"** - Document reasoning, not just numbers

---

## Common Pitfalls

### Pitfall 1: Criteria Overlap
Including "Performance" and "Speed" as separate criteria double-counts the same attribute.

**Signs:** Criteria feel redundant, same evidence supports multiple scores

**Fix:** Consolidate overlapping criteria. Each should measure something distinct.

### Pitfall 2: Anchoring on Favorites
Unconsciously scoring a preferred option higher across all criteria.

**Signs:** One option wins every criterion, scoring feels like rationalization

**Fix:** Have different people score different alternatives. Compare scores before revealing weights.

### Pitfall 3: Equal Weights Default
Assigning equal weights when criteria actually have different importance.

**Signs:** All criteria weighted 20% (for 5 criteria), outcome feels wrong

**Fix:** Force ranking of criteria first. The most important criterion should have highest weight.

### Pitfall 4: Ignoring Qualitative Factors
Some important factors resist quantification but still matter.

**Signs:** Analysis says A, but gut says B, with no way to reconcile

**Fix:** Include qualitative criteria with subjective scores. Document the subjectivity explicitly.

---

## Example: AI Security Scanner Application

### Decision Context
"Select infrastructure platform for AI Security Scanner after GCP deprecation, optimizing for cost, operational simplicity, and developer experience."

### Alternatives
1. **Railway** - Modern PaaS with GitHub integration
2. **Render** - Similar PaaS with strong free tier
3. **Fly.io** - Edge-focused container platform
4. **Keep GCP** - Remain on Google Cloud with optimization

### Criteria and Weights

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Monthly Cost | 25% | Primary driver for migration |
| Operational Simplicity | 25% | Team is small, minimize ops burden |
| Developer Experience | 20% | Fast iteration matters |
| Reliability/Uptime | 15% | Production service needs stability |
| Migration Effort | 15% | One-time cost but still matters |

### Scoring Matrix

| Criterion | Weight | Railway | Render | Fly.io | GCP |
|-----------|--------|---------|--------|--------|-----|
| Monthly Cost | 25% | 5 | 5 | 4 | 2 |
| Operational Simplicity | 25% | 5 | 4 | 3 | 2 |
| Developer Experience | 20% | 5 | 4 | 4 | 3 |
| Reliability/Uptime | 15% | 4 | 4 | 4 | 5 |
| Migration Effort | 15% | 4 | 4 | 3 | 5 |

### Weighted Scores

| Alternative | Calculation | Total |
|-------------|-------------|-------|
| **Railway** | (5x25)+(5x25)+(5x20)+(4x15)+(4x15) | **470** |
| Render | (5x25)+(4x25)+(4x20)+(4x15)+(4x15) | 425 |
| Fly.io | (4x25)+(3x25)+(4x20)+(4x15)+(3x15) | 360 |
| GCP | (2x25)+(2x25)+(3x20)+(5x15)+(5x15) | 310 |

### Decision
**Railway selected** - Highest score (470), wins on cost and operational simplicity which were the primary drivers. GCP reliability advantage (5 vs 4) not enough to overcome 3x cost penalty.

---

## Template

```markdown
# Comparative Analysis: [Decision Name]

**Date:** YYYY-MM-DD | **Participants:** [Names] | **Duration:** X min

## Decision Context
[What are we deciding and why does it matter?]

## Alternatives
1. [Option A] - [Brief description]
2. [Option B] - [Brief description]
3. [Option C] - [Brief description]

## Criteria and Weights

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| | % | |
| | % | |
| | % | |
| **Total** | **100%** | |

## Scoring Matrix (1-5 scale)

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| | % | | | |
| | % | | | |
| | % | | | |

## Weighted Scores

| Alternative | Calculation | Total |
|-------------|-------------|-------|
| Option A | | |
| Option B | | |
| Option C | | |

## Sensitivity Check
[Would +/-10% weight changes alter the outcome?]

## Decision
[Selected option] - [Rationale]

## Score Justifications
[Document why each score was assigned]
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  COMPARATIVE ANALYSIS QUICK REFERENCE           |
+-------------------------------------------------+
|  1. Define decision context clearly             |
|  2. List 3-6 viable alternatives                |
|  3. Select 5-8 evaluation criteria              |
|  4. Assign weights totaling 100%                |
|  5. Score each alternative (1-5 scale)          |
|  6. Calculate: Sum(Weight x Score)              |
|  7. Test sensitivity, analyze, decide           |
+-------------------------------------------------+
|  SCORING GUIDE:                                 |
|  1 = Poor / Does not meet requirement           |
|  3 = Acceptable / Meets minimum                 |
|  5 = Excellent / Exceeds requirement            |
+-------------------------------------------------+
|  CRITERIA CATEGORIES:                           |
|  * Cost (initial, ongoing, TCO)                 |
|  * Technical (performance, security)            |
|  * Operational (deployment, monitoring)         |
|  * Strategic (vendor, ecosystem)                |
|  * Team (skills, learning curve)                |
+-------------------------------------------------+
|  AVOID: Criteria overlap, anchoring bias,       |
|         equal weights default, ignoring "soft"  |
+-------------------------------------------------+
```

---

## Related Lenses

- **Devil's Advocate** - Challenge the top-scoring option before finalizing
- **Opportunity Cost** - Quantify what you lose by not selecting each alternative
- **First Principles** - Question whether the criteria themselves are correct
- **Pre-Mortem** - Imagine the selected option failed, identify risks
- **Pareto Analysis** - Focus on the 20% of criteria driving 80% of the decision

---

*Part of the AI Security Scanner institutional knowledge base.*
