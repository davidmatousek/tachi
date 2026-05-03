---
name: aod-lens
description: Routes to 14 structured thinking methodologies (lenses) for systematic analysis. Use this skill when you need to think through problems, apply thinking lenses, reason through decisions, or perform systematic analysis. Auto-selects appropriate lens based on context - 5 Whys for failures, Pre-Mortem for risks, First Principles for assumptions, Systems Thinking for architecture, Four Causes for understanding, Cargo Cult Detection for validation, Golden Mean for calibration.
---

# Thinking Lens Skill

Router that selects and applies thinking methodologies from `docs/core_principles/`.

## Keyword → Lens Routing

| Keywords | Lens | File |
|----------|------|------|
| "failed", "broke", "why did", "root cause" | 5 Whys | `01-FIVE_WHYS_METHODOLOGY.md` |
| "assumptions", "fundamentally", "from scratch" | First Principles | `02-FIRST_PRINCIPLES.md` |
| "risks", "could go wrong", "before we start" | Pre-Mortem | `03-PRE_MORTEM.md` |
| "guarantee failure", "avoid", "anti-patterns" | Inversion | `04-INVERSION.md` |
| "prioritize", "most value", "80/20" | Pareto Analysis | `05-PARETO_ANALYSIS.md` |
| "architecture", "interact", "components" | Systems Thinking | `06-SYSTEMS_THINKING.md` |
| "consequences", "downstream", "side effects" | Second-Order Effects | `07-SECOND_ORDER_EFFECTS.md` |
| "blocked", "bottleneck", "dependencies" | Constraint Analysis | `08-CONSTRAINT_ANALYSIS.md` |
| "challenge", "critique", "wrong with this" | Devil's Advocate | `09-DEVILS_ADVOCATE.md` |
| "compare", "choose between", "options" | Comparative Analysis | `10-COMPARATIVE_ANALYSIS.md` |
| "trade-off", "giving up", "sacrifice" | Opportunity Cost | `11-OPPORTUNITY_COST.md` |
| "explain", "purpose", "why does this exist", "complete picture" | Four Causes | `12-FOUR_CAUSES.md` |
| "going through motions", "process theater", "cargo cult", "actually working", "vibe coding" | Cargo Cult Detection | `13-CARGO_CULT_DETECTION.md` |
| "how much", "balance", "calibrate", "sweet spot", "too much", "too little", "spectrum" | Golden Mean | `14-GOLDEN_MEAN.md` |

## Workflow

1. **Route**: Match user keywords to lens using table above
2. **Load**: Read full methodology from `docs/core_principles/[FILE]`
3. **Apply**: Follow the step-by-step process and use template from that file

If ambiguous, ask:
> "Would you like to focus on **risks** (Pre-Mortem), **root cause** (5 Whys), or **trade-offs** (Opportunity Cost)?"

## Quick Reference

| Problem Type | Lens |
|--------------|------|
| Something failed | 5 Whys |
| Planning something risky | Pre-Mortem |
| Choosing between options | Comparative Analysis |
| Understanding a system | Systems Thinking |
| Prioritizing work | Pareto Analysis |
| Understanding why something exists | Four Causes |
| Checking if a practice is actually working | Cargo Cult Detection |
| Finding the right balance/amount | Golden Mean |
| Not sure | Pre-Mortem (safest default) |

## Hand-offs

| Situation | Route To |
|-----------|----------|
| Need to fix code after analysis | `debugger` skill |
| Document root cause in KB | `retrospective` skill |
| Security issue found | `security-pattern-scanner` skill |

## Lens Index

See `docs/core_principles/00-THINKING_LENSES_INDEX.md` for complete guide.
