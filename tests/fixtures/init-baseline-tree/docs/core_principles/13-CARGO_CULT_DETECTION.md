# Cargo Cult Detection

**Document Type:** Methodology Guide
**Category:** Validation, Critical Review
**Last Updated:** 2026-02-08
**Source:** Richard Feynman (1974 Caltech commencement address, "Cargo Cult Science")

---

## What is Cargo Cult Detection?

**Cargo Cult Detection** is a validation framework for distinguishing genuine understanding and real results from surface-level imitation of good practice. The name comes from Feynman's analogy to South Pacific islanders who built mock airstrips, control towers, and headsets from wood, hoping to attract cargo planes. They followed every outward form of an airport, but the planes never landed, because they were missing the essential substance behind the forms.

**Origin:** Richard Feynman coined the term "cargo cult science" in his 1974 Caltech commencement address, warning that following the outward forms of scientific investigation without intellectual honesty produces nothing. He identified the missing element as a "kind of leaning over backwards" integrity, where you report everything that might prove you wrong, not just what supports your conclusion.

**Core Question:** "Are we doing this because it works, or because it looks right?"

**Purpose:**
- Detect process theater (activities without outcomes)
- Distinguish real understanding from surface imitation
- Identify "vibe coding" and cargo cult AI adoption
- Ensure practices produce measurable results
- Build intellectual honesty into team culture

---

## When to Use

### Ideal Scenarios
- Evaluating whether adopted processes actually deliver value
- Reviewing AI/agent implementations for substance vs. hype
- Auditing "best practices" that aren't producing results
- Investigating why a well-designed system isn't working
- Challenging "we follow Agile/DevOps/AI-first" claims that feel hollow
- Onboarding to a team where practices seem ritualistic

### Less Suitable
- New initiatives that haven't had time to produce results
- Situations where teams are genuinely learning and iterating
- When the goal is creative brainstorming (this lens is evaluative)
- Low-stakes practices where the cost of analysis exceeds the cost of the practice

---

## The Cargo Cult Detection Process

### 1. Identify the Practice Under Review (5 min)

Name the specific practice, process, or adoption you're evaluating.

| Specific (Good) | Vague (Bad) |
|------------------|-------------|
| "Our AI code review agent comments on all PRs" | "We use AI" |
| "We run daily standups for 15 minutes" | "We do Agile" |
| "We have 90% test coverage" | "We test our code" |

### 2. Surface vs. Substance Analysis (15-20 min)

For each practice, separate the visible activities from the intended outcomes.

**The Feynman Test:** Can you explain *why* this practice works, or do you only know *that* you do it?

| Question | Surface Answer (Cargo Cult) | Substance Answer (Real) |
|----------|----------------------------|------------------------|
| Why do we do this? | "It's best practice" | "It catches X type of errors before production, saving Y hours per week" |
| How do we know it works? | "We do it consistently" | "We measure Z metric and it improved by W% since adoption" |
| What would break if we stopped? | "We'd be less rigorous" | "Specifically, A, B, and C would degrade measurably" |
| Who benefits? | "The team" | "Developer X spends 30% less time on Y task" |

**Warning signs of cargo cult practices:**
- Justification is "everyone does it" or "it's industry standard"
- No one can explain why it works, only that it's required
- Metrics measure activity (we did it) not outcomes (it worked)
- The practice has never been questioned or adjusted
- New team members are told "just do it" without rationale

### 3. Result Verification (10-15 min)

Compare promised outcomes with actual measured outcomes.

| Dimension | Document |
|-----------|----------|
| **Promised Outcome** | What was this practice supposed to achieve? |
| **Measurement** | How are we measuring whether it achieves that? |
| **Actual Result** | What does the data say? |
| **Gap** | Difference between promised and actual |
| **Explanation** | Why does the gap exist? |

**Critical question:** If you can't fill in the "Measurement" row, that's the first cargo cult indicator. Practices without measurement can't be validated.

### 4. Integrity Check (10 min)

Apply Feynman's "leaning over backwards" principle. Are we being honest about what works and what doesn't?

**Integrity questions:**
- Do we report failures as rigorously as successes?
- Do we know what would prove this practice wrong?
- Have we changed the practice based on evidence, or do we keep doing it regardless?
- Could someone outside the team tell whether this practice is working?
- Are we measuring what matters, or what's easy to measure?

| Check | Honest Answer |
|-------|---------------|
| We report failures openly | Yes / No / Sometimes |
| We know what would prove us wrong | Yes / No / Haven't thought about it |
| We've adjusted based on evidence | Yes / No / Never changed it |
| External observer would see results | Yes / No / Only if we explain it |
| We measure outcomes, not activities | Yes / No / We measure activities |

### 5. Verdict and Action (10 min)

Classify the practice and determine next steps.

| Classification | Description | Action |
|----------------|-------------|--------|
| **Genuine Practice** | Produces measurable results, team understands why it works | Keep and refine |
| **Partial Cargo Cult** | Has some value but includes ritualistic elements | Strip to essentials, add measurement |
| **Full Cargo Cult** | Activities without outcomes, no one can explain why | Stop or redesign from first principles |
| **Unknown** | Insufficient measurement to determine | Add measurement before judging |

---

## Best Practices

### Do's

1. **Start with outcomes** - Ask "What result does this produce?" before "How well do we do it?"
2. **Measure what matters** - Outcome metrics (bugs caught, time saved) over activity metrics (tests written, meetings held)
3. **Apply to yourself first** - Your own practices are the easiest to cargo cult
4. **Be kind, be honest** - The goal is improvement, not blame
5. **Look for partial cargo cults** - Most practices have real and ritualistic elements mixed together
6. **Revisit regularly** - A genuine practice can become cargo cult over time as context changes

### Don'ts

1. **Don't assume all practices are cargo cults** - Many conventions encode genuine wisdom
2. **Don't confuse "new" with "cargo cult"** - New practices need time to show results
3. **Don't weaponize this lens** - "That's cargo cult" is not a substitute for constructive feedback
4. **Don't demand perfection** - Some practices are valuable even without perfect measurement
5. **Don't skip the honesty check** - The hardest part is being honest about your own practices
6. **Don't only look at others** - Teams are most blind to their own cargo cults

---

## Common Pitfalls

### Pitfall 1: Confusing Activity with Outcome

**Problem:** "We're doing great. We have 95% test coverage, daily standups, and weekly retrospectives."

**Solution:** Restate in outcome terms. "Our production defect rate has dropped 40% since adopting these practices" is evidence. "We have 95% coverage" is activity. Coverage that doesn't catch real bugs is a cargo cult metric.

**Detection:** Ask "If we removed this practice and nothing measurably changed, would anyone notice?"

### Pitfall 2: The Measurement Cargo Cult

**Problem:** Team adds dashboards, KPIs, and monitoring but never acts on the data. Measurement itself becomes the ritual.

**Solution:** For every metric, define: "If this metric shows X, we will do Y." If no action is tied to the metric, it's decorative.

**Detection:** Ask "When did we last change behavior because of this metric?"

### Pitfall 3: Cargo Cult Detection as Cargo Cult

**Problem:** Team runs this framework as a checkbox exercise without genuine intellectual honesty. They "detect" easy targets while ignoring their own sacred cows.

**Solution:** Apply this lens to itself. "Are we doing cargo cult detection because it produces real insight, or because it looks rigorous?" If the answer is uncomfortable, you're doing it right.

**Detection:** If every review concludes "our practices are genuine," you're probably not being honest enough.

### Pitfall 4: Throwing Out Babies with Bathwater

**Problem:** Identifying cargo cult elements leads to abandoning entire practices, including the parts that work.

**Solution:** Most practices are partial cargo cults. Separate the elements that produce results from the elements that are ritualistic. Keep the former, remove the latter.

**Detection:** Before removing a practice, ask: "Is there a core of genuine value here that we should preserve?"

---

## Example: AI Agent Adoption Review

### Context
A development team adopted an AI coding agent 6 months ago. Leadership reports "great success" but developers seem skeptical.

### Cargo Cult Detection Analysis

**Step 1: Practice Under Review**
"AI coding agent generates code for all new feature development. Team reports 90% success rate."

**Step 2: Surface vs. Substance**

| Question | What Leadership Says | What Evidence Shows |
|----------|---------------------|---------------------|
| Why do we use it? | "AI-first is our strategy" | No documented rationale for specific use cases |
| How do we know it works? | "90% of generated code passes tests" | Tests were written by the same agent; no independent validation |
| What would break without it? | "We'd be slower" | No baseline measurement of pre-agent velocity |
| Who benefits? | "Everyone" | 3 of 8 developers report it helps; 5 say it creates extra review work |

**Step 3: Result Verification**

| Dimension | Finding |
|-----------|---------|
| **Promised Outcome** | Faster feature delivery, higher code quality |
| **Measurement** | "Success rate" defined as "code that passes tests" |
| **Actual Result** | 90% passes tests, but 35% of "passing" code requires significant revision during review |
| **Gap** | Effective success rate is closer to 58%, not 90% |
| **Explanation** | Agent-written tests don't cover edge cases; "passing tests" ≠ "production ready" |

**Step 4: Integrity Check**

| Check | Honest Answer |
|-------|---------------|
| We report failures openly | **No.** Leadership only tracks the 90% metric |
| We know what would prove us wrong | **No.** No defined failure criteria |
| We've adjusted based on evidence | **No.** Same prompts and workflow since day one |
| External observer would see results | **No.** Velocity metrics haven't measurably changed |
| We measure outcomes, not activities | **No.** Measuring "code generated" not "features shipped" |

**Step 5: Verdict**

**Classification: Partial Cargo Cult**

The agent has genuine value for specific tasks (boilerplate CRUD operations, test scaffolding) but the team is treating it as a universal tool. The "90% success rate" metric is a cargo cult metric that measures activity (code that compiles and passes its own tests) rather than outcome (production-ready code that ships).

### Recommended Actions

| Action | Purpose |
|--------|---------|
| Define "success" as "merged without major revision" | Outcome metric replaces activity metric |
| Identify agent-suitable vs. human-suitable tasks | Stop using agent for complex logic it consistently gets wrong |
| Establish pre-agent baseline for velocity | Measure actual impact instead of assuming improvement |
| Create developer feedback channel | Act on the 5-of-8 who report extra work |
| Set 3-month reassessment | If revised metrics don't show improvement, redesign approach |

---

## Template

```markdown
# Cargo Cult Detection: [Practice/Process Name]

**Date:** YYYY-MM-DD | **Reviewer:** [Name] | **Duration:** X min

## Practice Under Review
[Specific description of what you're evaluating]

## Surface vs. Substance
| Question | What We Say | What Evidence Shows |
|----------|-------------|---------------------|
| Why do we do this? | | |
| How do we know it works? | | |
| What would break without it? | | |
| Who benefits? | | |

## Result Verification
| Dimension | Finding |
|-----------|---------|
| Promised Outcome | |
| Measurement | |
| Actual Result | |
| Gap | |
| Explanation | |

## Integrity Check
| Check | Honest Answer |
|-------|---------------|
| We report failures openly | |
| We know what would prove us wrong | |
| We've adjusted based on evidence | |
| External observer would see results | |
| We measure outcomes, not activities | |

## Verdict
- [ ] Genuine Practice (keep and refine)
- [ ] Partial Cargo Cult (strip to essentials)
- [ ] Full Cargo Cult (stop or redesign)
- [ ] Unknown (add measurement first)

## Recommended Actions
| Action | Purpose | Owner | Deadline |
|--------|---------|-------|----------|
| | | | |
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  CARGO CULT DETECTION QUICK REFERENCE           |
+-------------------------------------------------+
|  Core Question: "Are we doing this because it   |
|                  works, or because it looks      |
|                  right?"                         |
+-------------------------------------------------+
|  1. Name the practice specifically              |
|  2. Separate surface (activity) from substance  |
|     (outcomes)                                  |
|  3. Verify results: promised vs. actual         |
|  4. Integrity check: are we being honest?       |
|  5. Verdict: genuine, partial cult, full cult    |
+-------------------------------------------------+
|  CARGO CULT WARNING SIGNS:                      |
|  - "Everyone does it" justification             |
|  - No one can explain WHY it works              |
|  - Metrics measure activity, not outcomes       |
|  - Practice never questioned or adjusted        |
|  - New members told "just do it"                |
+-------------------------------------------------+
|  FEYNMAN'S PRINCIPLE:                           |
|  "The first principle is that you must not fool |
|   yourself, and you are the easiest person to   |
|   fool."                                        |
+-------------------------------------------------+
|  AVOID: Weaponizing, skipping self-review,      |
|  demanding perfection, throwing out genuine      |
|  practices mixed with ritualistic elements      |
+-------------------------------------------------+
```

---

## Related Lenses

- **First Principles** - Use to rebuild a practice from fundamentals after detecting cargo cult elements
- **Devil's Advocate** - Challenges proposals logically; Cargo Cult Detection challenges whether practices produce actual results
- **Inversion** - Asks "What guarantees failure?"; Cargo Cult Detection asks "Are we already failing without realizing it?"
- **Four Causes** - Provides complete understanding of a system; Cargo Cult Detection checks whether that understanding is genuine or performative

---

*Part of the Agentic-Oriented Development thinking methodology collection.*
