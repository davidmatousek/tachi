# Thinking Lenses Selection Guide

**Document Type:** Navigation Index
**Last Updated:** 2026-02-08
**Total Lenses:** 14

---

## Quick Reference: Problem to Lens Mapping

Use this table to find the right thinking methodology for your situation.

| Problem Type | Recommended Lens | File | Time Est. |
|--------------|------------------|------|-----------|
| **Why did this fail?** | 5 Whys | [01-FIVE_WHYS_METHODOLOGY.md](01-FIVE_WHYS_METHODOLOGY.md) | 30-45 min |
| **What assumptions are we making?** | First Principles | [02-FIRST_PRINCIPLES.md](02-FIRST_PRINCIPLES.md) | 45-60 min |
| **What could go wrong?** | Pre-Mortem | [03-PRE_MORTEM.md](03-PRE_MORTEM.md) | 15-30 min |
| **What would guarantee failure?** | Inversion | [04-INVERSION.md](04-INVERSION.md) | 20-30 min |
| **What delivers the most value?** | Pareto Analysis | [05-PARETO_ANALYSIS.md](05-PARETO_ANALYSIS.md) | 30-45 min |
| **How do components interact?** | Systems Thinking | [06-SYSTEMS_THINKING.md](06-SYSTEMS_THINKING.md) | 45-60 min |
| **What happens next?** | Second-Order Effects | [07-SECOND_ORDER_EFFECTS.md](07-SECOND_ORDER_EFFECTS.md) | 30-45 min |
| **What's blocking us?** | Constraint Analysis | [08-CONSTRAINT_ANALYSIS.md](08-CONSTRAINT_ANALYSIS.md) | 30-45 min |
| **What's wrong with this idea?** | Devil's Advocate | [09-DEVILS_ADVOCATE.md](09-DEVILS_ADVOCATE.md) | 30-45 min |
| **Which option is best?** | Comparative Analysis | [10-COMPARATIVE_ANALYSIS.md](10-COMPARATIVE_ANALYSIS.md) | 45-60 min |
| **What are we giving up?** | Opportunity Cost | [11-OPPORTUNITY_COST.md](11-OPPORTUNITY_COST.md) | 20-30 min |
| **Why does this exist?** | Four Causes | [12-FOUR_CAUSES.md](12-FOUR_CAUSES.md) | 45-60 min |
| **Is this working or just looking right?** | Cargo Cult Detection | [13-CARGO_CULT_DETECTION.md](13-CARGO_CULT_DETECTION.md) | 45-60 min |
| **How much is the right amount?** | Golden Mean | [14-GOLDEN_MEAN.md](14-GOLDEN_MEAN.md) | 45-60 min |

---

## Lens Categories

### Problem Solving (Post-Hoc)
When something has already happened and you need to understand or fix it.

| Lens | Core Question | Best For |
|------|---------------|----------|
| **5 Whys** | "Why did this happen?" | Root cause analysis after failures |
| **Constraint Analysis** | "What blocked us?" | Identifying hidden dependencies |

### Decision Making (Pre-Hoc)
When you're planning or evaluating before taking action.

| Lens | Core Question | Best For |
|------|---------------|----------|
| **Pre-Mortem** | "What could go wrong?" | Identifying risks before starting |
| **Inversion** | "What guarantees failure?" | Finding critical success factors |
| **Pareto Analysis** | "What delivers most value?" | Prioritizing scope or features |
| **Opportunity Cost** | "What are we sacrificing?" | Quantifying trade-offs |
| **Comparative Analysis** | "Which option is best?" | Choosing between alternatives |

### Understanding Systems (Analytical)
When you need to comprehend how things work together.

| Lens | Core Question | Best For |
|------|---------------|----------|
| **First Principles** | "What's fundamentally true?" | Challenging inherited assumptions |
| **Systems Thinking** | "How do parts interact?" | Understanding complex architectures |
| **Second-Order Effects** | "What happens after?" | Predicting downstream impacts |
| **Four Causes** | "Why does this exist?" | Complete system understanding (material, form, process, purpose) |

### Calibration (Spectrum Decisions)
When you need to find the right amount, not choose between options.

| Lens | Core Question | Best For |
|------|---------------|----------|
| **Golden Mean** | "Where's the right balance?" | Calibrating autonomy, testing depth, process ceremony |

### Validation (Critical Review)
When you need to test or challenge ideas.

| Lens | Core Question | Best For |
|------|---------------|----------|
| **Devil's Advocate** | "What's the strongest counter-argument?" | Stress-testing proposals |
| **Cargo Cult Detection** | "Is this working or just looking right?" | Detecting process theater and ritualistic practices |

---

## Decision Tree: Which Lens Do I Need?

```
START: What are you trying to do?
│
├─ Fix a problem → Is it already broken?
│   ├─ Yes → 5 Whys
│   └─ No, but might break → Pre-Mortem or Inversion
│
├─ Make a decision → How many options?
│   ├─ Many (prioritize) → Pareto Analysis
│   ├─ Few (choose one) → Comparative Analysis
│   └─ One (validate it) → Devil's Advocate
│
├─ Understand something → What specifically?
│   ├─ Why it works that way → First Principles
│   ├─ How parts connect → Systems Thinking
│   ├─ What happens if we change it → Second-Order Effects
│   └─ Complete picture (material, form, process, purpose) → Four Causes
│
├─ Calibrate something → Finding the right amount?
│   └─ How much is enough? → Golden Mean
│
├─ Validate a practice → Is it actually working?
│   ├─ Challenge the logic → Devil's Advocate
│   └─ Check for process theater → Cargo Cult Detection
│
├─ Plan something → What's the concern?
│   ├─ Risks → Pre-Mortem
│   ├─ Trade-offs → Opportunity Cost
│   └─ Dependencies → Constraint Analysis
│
└─ Not sure → Start with Pre-Mortem (lowest risk to run)
```

---

## Lens Relationships

Some lenses work well together or as follow-ups to each other.

### Natural Sequences

**Risk Discovery**: Pre-Mortem → Inversion → Constraint Analysis
- Start by imagining failure
- Then identify what guarantees it
- Finally, surface hidden blockers

**Decision Quality**: First Principles → Comparative Analysis → Opportunity Cost
- Deconstruct assumptions
- Compare options objectively
- Quantify what you're giving up

**Post-Mortem Analysis**: 5 Whys → Systems Thinking → Second-Order Effects
- Find root cause
- Understand system interactions
- Predict if fix has side effects

**Complete Understanding**: Four Causes → Systems Thinking → First Principles
- Understand why it exists (purpose, material, form, process)
- Map how parts interact
- Challenge whether each part is truly necessary

**Calibration Cycle**: Golden Mean → Cargo Cult Detection → Golden Mean
- Set the initial balance point
- Check whether the practice is producing real results
- Recalibrate based on evidence

### Complementary Pairs

| Lens A | Pairs Well With | Why |
|--------|-----------------|-----|
| Pre-Mortem | Inversion | Both find failures from different angles |
| First Principles | Devil's Advocate | Challenge, then validate |
| Pareto Analysis | Opportunity Cost | Prioritize, then understand trade-offs |
| Systems Thinking | Second-Order Effects | Understand, then predict |
| Four Causes | Systems Thinking | Understand purpose, then map interactions |
| Golden Mean | Cargo Cult Detection | Calibrate, then verify it's working |
| Cargo Cult Detection | First Principles | Detect theater, then rebuild from fundamentals |

---

## When NOT to Use These Lenses

### Time-Critical Situations
If you have less than 5 minutes to decide, skip formal methodology and use intuition. Document why afterward.

### Already-Decided Situations
If leadership has already committed, use lenses only for implementation planning—not to question the decision.

### Simple Problems
If the solution is obvious and low-risk, executing is faster than analyzing. "Analysis paralysis" wastes time.

### Emotionally-Charged Discussions
Lenses work best with data. If the team is emotional, address feelings first before applying analytical frameworks.

---

## Agent Usage Guidance

AI agents can apply these methodologies during analysis. When invoking a lens:

### For Agents

1. **Read** the relevant methodology guide fully before starting
2. **Follow** the step-by-step process exactly as documented
3. **Use** the template structure for output formatting
4. **Include** evidence at each step (code snippets, data, references)
5. **Cross-reference** related lenses noted in the guide

### Example Agent Invocation

```
"Apply Pre-Mortem analysis to the proposed authentication refactor.
Follow the process in docs/core_principles/03-PRE_MORTEM.md.
Output should follow the template format in that guide."
```

### Recommended Agent-Lens Pairings

| Agent | Recommended Lenses |
|-------|-------------------|
| **Architect** | First Principles, Systems Thinking, Second-Order Effects, Four Causes |
| **Debugger** | 5 Whys, Constraint Analysis |
| **Head-Honcho** | Pareto Analysis, Opportunity Cost, Pre-Mortem, Cargo Cult Detection |
| **Team-Lead** | Constraint Analysis, Pre-Mortem |
| **Code-Reviewer** | Devil's Advocate, Inversion, Cargo Cult Detection |

---

## Quick Lookup by Role

### Developer
Starting a feature? → **Pre-Mortem** first
Debugging? → **5 Whys** or **Constraint Analysis**
Refactoring? → **First Principles** + **Second-Order Effects**
Understanding unfamiliar code? → **Four Causes** (why does this exist?)

### Architect
Reviewing proposal? → **First Principles** + **Devil's Advocate**
Designing system? → **Systems Thinking** + **Four Causes**
Post-incident? → **5 Whys** + **Systems Thinking**
Calibrating agent autonomy? → **Golden Mean**

### Product Manager
Prioritizing backlog? → **Pareto Analysis**
Cutting scope? → **Opportunity Cost**
Go/no-go decision? → **Pre-Mortem** + **Comparative Analysis**
Reviewing adopted processes? → **Cargo Cult Detection**

### Team Lead
Estimating? → **Constraint Analysis**
Planning? → **Pre-Mortem** + **Constraint Analysis**
Choosing tools? → **Comparative Analysis** + **Opportunity Cost**
Setting process levels? → **Golden Mean** (how much ceremony?)

---

## All Lenses Summary

| # | Lens | Core Question | Category | Lines |
|---|------|---------------|----------|-------|
| 01 | 5 Whys | "Why did this happen?" | Problem Solving | ~220 |
| 02 | First Principles | "What's fundamentally true?" | Understanding | ~250 |
| 03 | Pre-Mortem | "What could go wrong?" | Decision Making | ~250 |
| 04 | Inversion | "What guarantees failure?" | Decision Making | ~250 |
| 05 | Pareto Analysis | "What delivers most value?" | Decision Making | ~250 |
| 06 | Systems Thinking | "How do parts interact?" | Understanding | ~250 |
| 07 | Second-Order Effects | "What happens next?" | Understanding | ~250 |
| 08 | Constraint Analysis | "What's blocking us?" | Problem Solving | ~250 |
| 09 | Devil's Advocate | "What's wrong with this?" | Validation | ~250 |
| 10 | Comparative Analysis | "Which option is best?" | Decision Making | ~250 |
| 11 | Opportunity Cost | "What are we giving up?" | Decision Making | ~250 |
| 12 | Four Causes | "Why does this exist?" | Understanding | ~280 |
| 13 | Cargo Cult Detection | "Is this working or looking right?" | Validation | ~280 |
| 14 | Golden Mean | "Where's the right balance?" | Calibration | ~280 |

---

*Part of the Agentic-Oriented Development thinking methodology collection.*
