# First Principles Thinking

**Document Type:** Methodology Guide
**Category:** Understanding, Analysis
**Last Updated:** 2026-01-28
**Source:** Aristotle (classical philosophy), Elon Musk (modern application)

---

## What is First Principles?

**First Principles Thinking** is a reasoning approach that deconstructs complex problems into their most fundamental truths, then rebuilds solutions from the ground up. Instead of reasoning by analogy ("how did others solve this?"), you reason from foundational truths ("what do we know is absolutely true?").

**Origin:** Aristotle defined a first principle as "the first basis from which a thing is known." In modern times, Elon Musk popularized the approach for innovation, describing it as "boiling things down to the most fundamental truths and reasoning up from there."

**Purpose:**
- Challenge inherited assumptions and "best practices"
- Discover novel solutions invisible to conventional thinking
- Avoid cargo cult engineering (copying without understanding)
- Make decisions based on truths, not conventions

**Core Question:** "What is fundamentally true here?"

---

## When to Use

### Ideal Scenarios
- Evaluating proposals that seem unnecessarily complex
- Challenging "we've always done it this way" thinking
- Making build vs. buy decisions
- Questioning technology stack choices
- Identifying hidden assumptions in requirements
- Simplifying over-engineered solutions

### Less Suitable
- Time-critical decisions requiring immediate action
- Well-established problems with proven solutions
- Low-stakes choices where conventions work fine
- Situations where consensus matters more than optimization

---

## The First Principles Process

### 1. Identify the Proposal or Assumption (5 min)

State what you're analyzing. Be specific about the claim or approach being evaluated.

| Good | Bad |
|------|-----|
| "We need Redis for session management" | "We need caching" |
| "Users require OAuth for authentication" | "We need security" |

### 2. Deconstruct to Fundamental Truths (15-20 min)

Ask: "What do we know is absolutely, undeniably true?"

**Decomposition questions:**
- What are the core requirements? (not solutions)
- What constraints are real vs. assumed?
- What would a solution need to accomplish at minimum?
- What physics/logic/business rules are immutable?

**Example decomposition:**
- Claim: "We need Redis for session management"
- Fundamental truths:
  - Sessions require persistent storage
  - Session lookups must be fast (<100ms)
  - Sessions must survive server restarts
  - We already have PostgreSQL with connection pooling

### 3. Challenge Each Assumption (10-15 min)

For each component of the proposal, ask:
- "Is this actually required, or just conventional?"
- "What evidence supports this?"
- "What would happen if we removed this?"

**Warning signs of unfounded assumptions:**
- "Everyone uses X for this"
- "It's industry best practice"
- "That's how we did it at my last company"
- "The blog post recommended it"

### 4. Rebuild from First Principles (15-20 min)

Given only the fundamental truths, design the simplest solution:
- Start with nothing
- Add only what the truths require
- Stop when requirements are met
- Resist adding "nice to haves"

### 5. Compare and Decide (10 min)

Evaluate the first-principles solution against the original proposal:
- Which is simpler?
- Which has fewer dependencies?
- Which is easier to maintain?
- What does each cost (time, money, complexity)?

---

## Best Practices

### Do's

1. **Start with "What problem are we solving?"** - Define the actual need, not the assumed solution
2. **Separate requirements from solutions** - "Fast lookups" is a requirement; "Redis" is a solution
3. **Question authority gently** - "Help me understand why X is necessary" invites collaboration
4. **Document your reasoning** - Show the decomposition so others can verify logic
5. **Accept when conventions are correct** - Sometimes best practices ARE first principles
6. **Quantify when possible** - "Fast" is vague; "<50ms p95" is measurable

### Don'ts

1. **Don't dismiss experience** - Conventions often encode hard-won wisdom
2. **Don't confuse contrarianism with first principles** - Disagreeing isn't the same as reasoning
3. **Don't over-apply** - Not every decision needs deconstruction
4. **Don't ignore constraints** - Time, budget, and team skills are real
5. **Don't be arrogant** - "I reasoned from first principles" isn't a trump card
6. **Don't skip validation** - Your reasoning might have errors; test conclusions

---

## Common Pitfalls

### Pitfall 1: False Fundamentals

Mistaking preferences or conventions for fundamental truths.

**Wrong:** "We need a NoSQL database because document storage is fundamental."
**Right:** "We need persistent storage. Documents are one option; relational tables are another."

**Prevention:** Ask "Is this a requirement or a solution?" repeatedly.

### Pitfall 2: Analysis Paralysis

Deconstructing everything leads to never deciding.

**Wrong:** Spending 3 days analyzing whether to use tabs or spaces.
**Right:** Apply first principles to high-impact decisions; use conventions for low-stakes choices.

**Prevention:** Set time boxes. If first principles doesn't reveal a clear winner in 30 minutes, the decision probably isn't important enough.

### Pitfall 3: Reinventing Wheels

Assuming conventional solutions are wrong because they're conventional.

**Wrong:** "Everyone uses PostgreSQL, so let's build our own database."
**Right:** "PostgreSQL is conventional AND satisfies our fundamental requirements."

**Prevention:** Remember that first principles often validates conventions. The goal is clarity, not novelty.

### Pitfall 4: Ignoring Trade-offs

First principles reveals the minimum; production may need more.

**Wrong:** "First principles says we only need X, so ignore scalability."
**Right:** "First principles says X is sufficient now; we should plan for Y when scale demands it."

**Prevention:** Distinguish between current needs and future requirements.

---

## Example: AI Security Scanner Application

### Proposal
"We need Redis for session management, rate limiting, and token caching" (Feature 015 planning).

### First Principles Analysis

**Step 1: Identify the Proposal**
The proposal claims we need Redis (a separate in-memory data store) for three use cases: sessions, rate limiting, and token caching.

**Step 2: Deconstruct to Fundamental Truths**

| Use Case | Fundamental Need | Actual Requirement |
|----------|------------------|-------------------|
| Sessions | Persistent storage, fast lookup | <100ms lookup, survive restarts |
| Rate Limiting | Track request counts per IP | Count requests in time window |
| Token Cache | Store/retrieve tokens quickly | Fast read for validation |

**Additional truths:**
- We already have PostgreSQL 15 in production
- PostgreSQL supports indexes for fast lookups
- PostgreSQL has connection pooling
- Adding Redis means: new infrastructure, monitoring, cost, complexity

**Step 3: Challenge Assumptions**

| Assumption | Challenge | Finding |
|------------|-----------|---------|
| "Redis is faster" | By how much? Do we need that speed? | PostgreSQL indexed query: 15ms. Requirement: <100ms. |
| "Rate limiting needs Redis" | Why? | In-memory SimpleRateLimiter works; no persistence needed for rate limits |
| "Industry uses Redis" | Is our scale similar? | No - we're not Twitter. Our load doesn't require Redis-level performance |

**Step 4: Rebuild from First Principles**

Solution without Redis:
- **Sessions**: PostgreSQL `user_sessions` table with index
- **Rate Limiting**: In-memory `SimpleRateLimiter` (resets on restart is acceptable)
- **Token Cache**: PostgreSQL `token_blacklist` table with index

**Step 5: Compare and Decide**

| Factor | With Redis | PostgreSQL-Only |
|--------|-----------|-----------------|
| Infrastructure | 2 data stores | 1 data store |
| Monthly cost | +$50-200 (Memorystore) | $0 additional |
| Complexity | Higher (2 systems) | Lower (1 system) |
| Performance | ~5ms lookup | ~15ms lookup |
| Requirement | <100ms | <100ms |

### Outcome

First principles analysis revealed PostgreSQL was **sufficient** for all use cases. Feature 015 implemented PostgreSQL-only architecture, resulting in:
- 46x faster than required (p95: 0.39ms vs 18ms Redis baseline)
- $50-200/month cost savings
- Simplified operations (one database to manage)
- Zero Redis connection errors in production

**Time saved:** 2 weeks of unnecessary Redis infrastructure work.

---

## Template

```markdown
# First Principles Analysis: [Topic]

**Date:** YYYY-MM-DD | **Analyst:** [Name] | **Duration:** X min

## Proposal Being Analyzed
[State the claim, assumption, or approach being evaluated]

## Fundamental Truths
| # | Truth | Evidence |
|---|-------|----------|
| 1 | | |
| 2 | | |
| 3 | | |

## Assumptions Challenged
| Assumption | Challenge | Finding |
|------------|-----------|---------|
| | | |
| | | |

## First Principles Solution
[Describe the solution built from fundamental truths only]

## Comparison
| Factor | Original Proposal | First Principles |
|--------|------------------|------------------|
| Complexity | | |
| Cost | | |
| Time | | |

## Decision
[Which approach and why]

## Validation
- [ ] Does this satisfy all fundamental requirements?
- [ ] Have we avoided adding unnecessary complexity?
- [ ] Is the reasoning documented for review?
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  FIRST PRINCIPLES QUICK REFERENCE               |
+-------------------------------------------------+
|  CORE QUESTION: "What is fundamentally true?"   |
+-------------------------------------------------+
|  1. State the proposal/assumption               |
|  2. Decompose to fundamental truths             |
|  3. Challenge each assumption with evidence     |
|  4. Rebuild solution from truths only           |
|  5. Compare: simpler? cheaper? sufficient?      |
+-------------------------------------------------+
|  DECOMPOSITION QUESTIONS:                       |
|  - What are the REAL requirements?              |
|  - What constraints are facts vs assumptions?   |
|  - What would minimum viable look like?         |
+-------------------------------------------------+
|  RED FLAGS (unfounded assumptions):             |
|  X "Everyone does it this way"                  |
|  X "It's best practice"                         |
|  X "The blog said so"                           |
+-------------------------------------------------+
|  AVOID: Contrarianism, analysis paralysis,      |
|         reinventing wheels, ignoring trade-offs |
+-------------------------------------------------+
```

---

## Related Lenses

- **Inversion** - Ask "What would guarantee failure?" to identify hidden requirements
- **Systems Thinking** - Understand how components interact after first principles identifies them
- **Constraint Analysis** - Identify which constraints are real (use with Step 2)
- **5 Whys** - Use AFTER first principles identifies a problem to find root cause

---

*Part of the AI Security Scanner institutional knowledge base.*
