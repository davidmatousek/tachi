# Core Principles

**Location**: `docs/core_principles/`
**Purpose**: Thinking methodologies for systematic analysis and decision-making

## Thinking Lenses (00-14)

**Selection Guide**: [00-THINKING_LENSES_INDEX.md](00-THINKING_LENSES_INDEX.md) - Start here to find the right methodology

| # | Lens | Core Question | Use When |
|---|------|---------------|----------|
| 00 | [Index & Selection Guide](00-THINKING_LENSES_INDEX.md) | "Which lens do I need?" | Finding the right methodology |
| 01 | [5 Whys](01-FIVE_WHYS_METHODOLOGY.md) | "Why did this happen?" | Root cause analysis after failures |
| 02 | [First Principles](02-FIRST_PRINCIPLES.md) | "What's fundamentally true?" | Challenging inherited assumptions |
| 03 | [Pre-Mortem](03-PRE_MORTEM.md) | "What could go wrong?" | Identifying risks before starting |
| 04 | [Inversion](04-INVERSION.md) | "What guarantees failure?" | Finding critical success factors |
| 05 | [Pareto Analysis](05-PARETO_ANALYSIS.md) | "What delivers most value?" | Prioritizing scope or features |
| 06 | [Systems Thinking](06-SYSTEMS_THINKING.md) | "How do parts interact?" | Understanding complex architectures |
| 07 | [Second-Order Effects](07-SECOND_ORDER_EFFECTS.md) | "What happens after?" | Predicting downstream impacts |
| 08 | [Constraint Analysis](08-CONSTRAINT_ANALYSIS.md) | "What's blocking us?" | Surfacing hidden dependencies |
| 09 | [Devil's Advocate](09-DEVILS_ADVOCATE.md) | "What's wrong with this idea?" | Stress-testing proposals |
| 10 | [Comparative Analysis](10-COMPARATIVE_ANALYSIS.md) | "Which option is best?" | Choosing between alternatives |
| 11 | [Opportunity Cost](11-OPPORTUNITY_COST.md) | "What are we giving up?" | Quantifying trade-offs |
| 12 | [Four Causes](12-FOUR_CAUSES.md) | "Why does this exist?" | Complete system understanding |
| 13 | [Cargo Cult Detection](13-CARGO_CULT_DETECTION.md) | "Is this working or just looking right?" | Detecting process theater |
| 14 | [Golden Mean](14-GOLDEN_MEAN.md) | "How much is the right amount?" | Calibrating process levels |

## Quick Lens Selection by Role

| Role | Common Lenses |
|------|---------------|
| **Developer** | Pre-Mortem (planning), 5 Whys (debugging), First Principles (refactoring), Four Causes (understanding unfamiliar code) |
| **Architect** | First Principles, Systems Thinking, Second-Order Effects, Four Causes (designing systems), Golden Mean (calibrating autonomy) |
| **PM** | Pareto Analysis, Opportunity Cost, Pre-Mortem, Cargo Cult Detection (reviewing practices) |
| **Team Lead** | Constraint Analysis, Pre-Mortem, Golden Mean (setting process levels) |

## Integration with Workflow

1. **Planning**: Use Pre-Mortem to identify risks, Constraint Analysis for hidden blockers
2. **Decision Making**: Use Pareto Analysis to prioritize, Comparative Analysis to choose
3. **Debugging**: Use 5 Whys for root cause analysis
4. **Review**: Use Devil's Advocate to stress-test, Systems Thinking to understand impacts
5. **Understanding**: Use Four Causes for complete system comprehension (material, form, process, purpose)
6. **Validation**: Use Cargo Cult Detection to identify process theater and ensure practices produce real results
7. **Calibration**: Use Golden Mean to find the right balance on spectrum decisions (testing depth, process ceremony, autonomy)

## Related Documentation

- [Project Standards](../standards/README.md) - DoD, naming, git workflow
- [Constitution](../../.aod/memory/constitution.md) - Governance principles
