# Pareto Analysis (80/20 Rule)

**Document Type:** Methodology Guide
**Category:** Decision Making, Prioritization
**Last Updated:** 2026-01-28
**Source:** Vilfredo Pareto (Italian economist, 1896)

---

## What is Pareto Analysis?

**Pareto Analysis** is a decision-making technique based on the principle that roughly 80% of effects come from 20% of causes. By identifying and focusing on the vital few inputs that drive the majority of outcomes, teams can maximize impact with limited resources.

**Origin:** Named after Vilfredo Pareto, who observed in 1896 that 80% of Italy's land was owned by 20% of the population. Joseph Juran later applied this to quality management, calling it the "vital few and trivial many."

**Core Question:** "What delivers the most value?"

**Purpose:**
- Identify high-impact activities to prioritize
- Eliminate low-value work that consumes resources
- Focus limited resources on maximum ROI activities
- Make data-driven prioritization decisions

---

## When to Use

### Ideal Scenarios

- Backlog prioritization with 50+ items
- Resource allocation with budget constraints
- Bug triage to maximize quality improvement
- Feature selection for MVP scope
- Time management and task prioritization
- Customer complaint analysis

### Less Suitable

- When all items have equal importance (rare)
- Problems requiring root cause analysis (use 5 Whys)
- Decisions requiring qualitative judgment over data
- Situations with insufficient historical data
- When political/stakeholder factors override data

---

## The Pareto Process

### 1. Define the Problem Scope (5 min)

Clearly state what you're analyzing and the metric for measuring impact.

| Good | Bad |
|------|-----|
| "Which user stories deliver the most customer value?" | "What should we build?" |
| "Which bugs affect the most users?" | "What's broken?" |
| "Which features drive 80% of revenue?" | "What's important?" |

### 2. Collect and Categorize Data (15-30 min)

Gather quantitative data for each item:
- **Count occurrences** (bugs, requests, complaints)
- **Measure impact** (revenue, users affected, time saved)
- **Assign values** (story points, business value scores)

### 3. Calculate Percentages and Rank (10 min)

1. Sum the total value across all items
2. Calculate each item's percentage of the total
3. Rank items from highest to lowest percentage
4. Calculate cumulative percentage

### 4. Identify the Vital Few (10 min)

Find where cumulative percentage reaches 80%:
- Items above this line = **Vital Few** (prioritize)
- Items below this line = **Trivial Many** (defer or eliminate)

### 5. Take Action (ongoing)

- Focus resources on the Vital Few
- Defer, delegate, or eliminate the Trivial Many
- Re-evaluate periodically as data changes

---

## Best Practices

### Do's

1. **Use quantitative data** - Base decisions on measurable metrics, not opinions
2. **Update regularly** - Priorities shift; re-analyze quarterly
3. **Validate with stakeholders** - Ensure the 80% aligns with business goals
4. **Combine with other lenses** - Use Constraint Analysis to check feasibility
5. **Document your criteria** - Make the ranking methodology transparent
6. **Consider dependencies** - A low-value item may enable high-value ones

### Don'ts

1. **Don't ignore the 20%** - Some low-frequency items may be critical (security bugs)
2. **Don't use arbitrary numbers** - The ratio varies (could be 70/30 or 90/10)
3. **Don't skip data collection** - Gut feelings lead to bias
4. **Don't set and forget** - Priorities change over time
5. **Don't confuse effort with value** - High-effort items may deliver low value

---

## Common Pitfalls

### Pitfall 1: Ignoring Critical Low-Frequency Items

A security vulnerability affecting 5% of users might be in the "trivial many" by occurrence count, but represents catastrophic risk.

**Solution:** Apply a criticality filter before Pareto ranking. Critical items bypass the 80/20 rule.

### Pitfall 2: Using Wrong Metrics

Ranking features by "number of requests" when revenue impact matters leads to building popular-but-unprofitable features.

**Solution:** Align metrics with business objectives. For B2B SaaS, revenue impact often trumps request count.

### Pitfall 3: Analysis Paralysis

Spending more time analyzing than executing defeats the purpose of prioritization.

**Solution:** Set a time limit (1-2 hours max). Good enough prioritization beats perfect paralysis.

### Pitfall 4: Ignoring Dependencies

Prioritizing a high-value feature that depends on a "trivial" infrastructure item leads to blocked work.

**Solution:** Map dependencies before finalizing priorities. Promote blocking items.

---

## Example: AI Security Scanner Application

### Problem Statement
"From a backlog of 55 user stories, identify which 20% will deliver 80% of customer value for the next sprint."

### Pareto Analysis

**Step 1: Define Metric**
Customer Value Score (1-10) x User Reach (% of users affected)

**Step 2: Data Collection**

| Story ID | Description | Value Score | User Reach | Impact Score |
|----------|-------------|-------------|------------|--------------|
| US-042 | Real-time scan notifications | 9 | 80% | 720 |
| US-018 | API key rotation | 8 | 70% | 560 |
| US-031 | Dashboard scan history | 7 | 75% | 525 |
| US-007 | Export reports to PDF | 6 | 60% | 360 |
| US-055 | Custom scan schedules | 8 | 40% | 320 |
| ... | (50 more items) | ... | ... | ... |

**Step 3: Rank and Calculate Cumulative %**

| Rank | Story ID | Impact Score | % of Total | Cumulative % |
|------|----------|--------------|------------|--------------|
| 1 | US-042 | 720 | 15.2% | 15.2% |
| 2 | US-018 | 560 | 11.8% | 27.0% |
| 3 | US-031 | 525 | 11.1% | 38.1% |
| 4 | US-007 | 360 | 7.6% | 45.7% |
| 5 | US-055 | 320 | 6.8% | 52.5% |
| 6 | US-012 | 290 | 6.1% | 58.6% |
| 7 | US-029 | 270 | 5.7% | 64.3% |
| 8 | US-044 | 250 | 5.3% | 69.6% |
| 9 | US-003 | 230 | 4.9% | 74.5% |
| 10 | US-051 | 200 | 4.2% | 78.7% |
| 11 | US-008 | 180 | 3.8% | **82.5%** |
| ... | (44 more) | ... | ... | ... |

**Step 4: Identify Vital Few**
- **11 stories (20%)** deliver **82.5% of customer value**
- Focus sprint capacity on US-042 through US-008
- Defer remaining 44 stories to future sprints

### Outcome
- Sprint scope reduced from 55 to 11 stories
- Team delivers 82.5% of potential value with 20% of the work
- Clear prioritization rationale for stakeholder communication

---

## Template

```markdown
# Pareto Analysis: [Decision Context]

**Date:** YYYY-MM-DD | **Analyst:** [Name] | **Metric:** [Value Measure]

## Problem Statement
[What are you prioritizing and why?]

## Data Collection
| Item | Description | [Metric 1] | [Metric 2] | Impact Score |
|------|-------------|------------|------------|--------------|
| | | | | |

## Ranked Results
| Rank | Item | Impact Score | % of Total | Cumulative % |
|------|------|--------------|------------|--------------|
| | | | | |

## Vital Few (Top 20%)
[List items that deliver 80% of value]

## Trivial Many (Bottom 80%)
[List items to defer or eliminate]

## Actions
| Priority | Item | Owner | Timeline |
|----------|------|-------|----------|
| | | | |

## Dependencies to Promote
[Any low-ranking items that block high-ranking ones]
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  PARETO ANALYSIS QUICK REFERENCE                |
+-------------------------------------------------+
|  1. Define scope and success metric             |
|  2. Collect quantitative data for all items     |
|  3. Calculate impact score for each item        |
|  4. Rank highest to lowest                      |
|  5. Calculate cumulative percentage             |
|  6. Draw line at 80% cumulative                 |
|  7. Focus on Vital Few above the line           |
+-------------------------------------------------+
|  THE 80/20 PRINCIPLE:                           |
|  - 20% of features deliver 80% of value         |
|  - 20% of bugs cause 80% of user complaints     |
|  - 20% of customers generate 80% of revenue     |
+-------------------------------------------------+
|  WATCH OUT FOR:                                 |
|  - Critical items in the "trivial" category     |
|  - Dependencies that block high-value items     |
|  - Wrong metrics leading to wrong priorities    |
+-------------------------------------------------+
```

---

## Related Lenses

- **Opportunity Cost** - After identifying the Vital Few, analyze what you give up by not doing the Trivial Many
- **Comparative Analysis** - Compare multiple prioritization approaches to validate Pareto results
- **Constraint Analysis** - Check if the Vital Few are feasible given resource constraints
- **5 Whys** - Use when a Vital Few item keeps failing to understand root cause

---

*Part of the AI Security Scanner institutional knowledge base.*
