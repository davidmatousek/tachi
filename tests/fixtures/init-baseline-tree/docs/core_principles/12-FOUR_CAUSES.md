# Four Causes Analysis

**Document Type:** Methodology Guide
**Category:** Understanding, Analysis
**Last Updated:** 2026-02-08
**Source:** Aristotle (Metaphysics, Physics), adapted by Richard Feynman (multiple representations)

---

## What is Four Causes Analysis?

**Four Causes Analysis** is a comprehensive explanatory framework that examines any system, component, or decision through four fundamental questions: What is it made of? What form does it take? What process created it? What is its purpose? An explanation that fails to address all four causes is incomplete.

**Origin:** Aristotle argued in his *Physics* and *Metaphysics* that to truly understand anything, you must account for its material, formal, efficient, and final causes. For over two millennia, this remained the dominant framework for complete explanation in Western thought. The approach resurfaces in modern systems engineering, where understanding components, architecture, process, and purpose is essential for sound design.

**Core Question:** "Why does this exist and what is it for?"

**Purpose:**
- Achieve complete understanding of a system or component
- Expose gaps where purpose is unclear or materials are misunderstood
- Catch the "vibe coding" anti-pattern (building without clarity on any cause)
- Ensure architecture decisions account for all four dimensions
- Bridge the gap between what something *is* and what it's *for*

---

## When to Use

### Ideal Scenarios
- Onboarding to an unfamiliar system or codebase
- Reviewing architecture decisions for completeness
- Designing new agents, services, or components
- Post-incident analysis when "how did we get here?" is unclear
- Evaluating whether a tool or framework fits your actual needs
- Auditing existing systems for purpose drift

### Less Suitable
- Simple debugging with obvious symptoms
- Time-critical incidents requiring immediate action
- Binary go/no-go decisions (use Comparative Analysis)
- Problems where only one dimension matters

---

## The Four Causes Process

### 1. Material Cause: "What is it made of?" (10 min)

Identify every component, dependency, resource, and input the system consumes.

**Questions to ask:**
- What technologies, languages, and frameworks compose this?
- What data does it process or consume?
- What computational resources does it require?
- What external services does it depend on?
- What human skills are required to build and maintain it?

| Layer | Examples |
|-------|----------|
| **Runtime** | Language, framework, runtime version |
| **Data** | Input formats, data stores, training data |
| **Infrastructure** | Compute, memory, network, storage |
| **Dependencies** | Libraries, APIs, external services |
| **Human** | Skills required, team composition |

### 2. Formal Cause: "What shape does it take?" (10 min)

Describe the architecture, structure, and design patterns.

**Questions to ask:**
- What is the overall architecture pattern?
- How are components organized and related?
- What interfaces and contracts exist?
- What design patterns are employed?
- What are the boundaries and interfaces?

| Aspect | Document |
|--------|----------|
| **Architecture** | Monolith, microservices, serverless, agent pipeline |
| **Patterns** | RAG, chain-of-thought, tool-use, event-driven |
| **Interfaces** | API contracts, protocols, message formats |
| **State** | Stateful vs. stateless, state management approach |
| **Boundaries** | Service boundaries, context boundaries, trust boundaries |

### 3. Efficient Cause: "What process creates it?" (10 min)

Identify the workflow, triggers, and mechanisms that bring the system into action.

**Questions to ask:**
- What triggers this system to act?
- What is the build and deployment pipeline?
- What workflow produces the output?
- Who or what initiates changes?
- What feedback loops govern its operation?

| Phase | Document |
|-------|----------|
| **Trigger** | What starts the process (user action, event, schedule) |
| **Build** | How is it assembled (CI/CD, manual, automated) |
| **Execution** | What algorithm or workflow produces results |
| **Feedback** | What signals indicate success or failure |
| **Evolution** | How does it change over time (versioning, learning) |

### 4. Final Cause: "What is its purpose?" (10 min)

Articulate the intended outcome, the user need, and the success criteria.

**Questions to ask:**
- What user need does this fulfill?
- What business goal does it serve?
- What does success look like, measured concretely?
- What would happen if this didn't exist?
- Has the original purpose drifted?

| Dimension | Document |
|-----------|----------|
| **User Need** | The specific problem being solved for the user |
| **Business Goal** | The organizational objective being served |
| **Success Criteria** | Measurable outcomes that define success |
| **Absence Test** | What breaks or degrades without this |
| **Purpose Drift** | Has the current use diverged from original intent |

### 5. Cross-Cause Analysis (10-15 min)

Examine how the four causes relate, conflict, or align.

**Key questions:**
- Does the material (what it's made of) actually serve the final cause (its purpose)?
- Does the formal cause (architecture) fit the efficient cause (how it's built)?
- Is there a mismatch between any causes that explains dysfunction?
- Which cause is least understood? That's your biggest risk.

| Alignment Check | Question |
|-----------------|----------|
| Material ↔ Final | Do the components serve the purpose, or are they leftover from a different goal? |
| Formal ↔ Efficient | Does the architecture support the build/deploy process, or fight it? |
| Material ↔ Formal | Do the technologies fit the architecture, or create friction? |
| Efficient ↔ Final | Does the workflow produce the intended outcome reliably? |

---

## Best Practices

### Do's

1. **Start with Final Cause** - Understanding purpose first prevents rabbit holes in the other three
2. **Be specific in each cause** - "Uses AI" is not a material cause; "Uses GPT-4 via OpenAI API with 128K context window" is
3. **Look for mismatches** - The most valuable insight often comes from causes that contradict each other
4. **Include human elements** - Team skills, organizational structure, and decision-making processes are causes too
5. **Document gaps** - "Unknown" is a valid and important finding
6. **Use for agent design** - Map material (tools/models), formal (architecture), efficient (workflow), final (user outcome)

### Don'ts

1. **Don't skip Final Cause** - Building without clear purpose is the definition of vibe coding
2. **Don't confuse material and formal** - "React" is material (what it's made of); "component architecture" is formal (what shape it takes)
3. **Don't list without analyzing** - The value is in cross-cause relationships, not just inventories
4. **Don't assume causes are static** - Purpose drifts, materials get updated, processes evolve
5. **Don't over-detail** - This is about understanding, not exhaustive documentation

---

## Common Pitfalls

### Pitfall 1: Missing Final Cause (Vibe Coding)

**Problem:** Team builds a sophisticated agent with great tools and architecture but cannot articulate what user need it serves or how to measure success.

**Solution:** Before any design work, write one sentence: "This exists to [specific outcome] for [specific user] measured by [specific metric]." If you cannot fill in the blanks, you don't have a final cause yet.

**Detection:** Ask any team member "Why does this exist?" If answers vary significantly, the final cause is unclear.

### Pitfall 2: Material-Purpose Mismatch

**Problem:** Using enterprise-grade infrastructure (material cause) for a prototype that just needs to prove a concept (final cause).

**Solution:** Let the final cause drive material decisions. Ask: "Given what this needs to accomplish, what is the minimum material that serves that purpose?"

**Detection:** If the cost or complexity of materials exceeds the value of the purpose, there's a mismatch.

### Pitfall 3: Ignoring Efficient Cause

**Problem:** Beautiful architecture (formal) and clear purpose (final) but no understanding of how it actually gets built, deployed, or maintained.

**Solution:** Map the complete lifecycle: Who builds it? How is it deployed? What triggers it? How does it evolve? The efficient cause is where plans meet reality.

**Detection:** If the team can describe what it should look like but not how to get it there, the efficient cause is missing.

### Pitfall 4: Confusing Causes with Each Other

**Problem:** Listing "uses microservices" under every cause instead of distinguishing material (containers, orchestration tools), formal (service boundaries, communication patterns), efficient (CI/CD pipeline, deployment process), and final (independent scalability, team autonomy).

**Solution:** Use the strict question for each cause: Made of? Shaped as? Built by? Exists for?

---

## Example: AI Coding Agent Design

### Context
Evaluating an AI coding agent that generates pull requests from issue descriptions.

### Four Causes Analysis

**Material Cause: What is it made of?**

| Component | Specifics |
|-----------|-----------|
| Model | Claude Sonnet 4.5, 200K context window |
| Tools | File read/write, git operations, test runner, linter |
| Data | Repository codebase, issue description, coding standards doc |
| Infrastructure | Runs in CI environment, 8GB RAM, 10-min timeout |
| Dependencies | GitHub API, language server, package registry |
| Human | Developer reviews output, writes issue descriptions |

**Formal Cause: What shape does it take?**

| Aspect | Design |
|--------|--------|
| Architecture | Single-agent with tool-use loop |
| Pattern | Plan-then-execute with validation gate |
| Interface | Input: GitHub issue. Output: Pull request with tests |
| State | Stateless per invocation, context from repo + issue |
| Boundaries | Cannot modify CI config, cannot merge, cannot access secrets |

**Efficient Cause: What process creates it?**

| Phase | Mechanism |
|-------|-----------|
| Trigger | New issue labeled "agent-ready" |
| Planning | Agent reads issue, explores relevant code, creates plan |
| Execution | Agent writes code changes, creates tests |
| Validation | Agent runs tests, linter, checks diff size |
| Output | Creates PR with description linking to issue |
| Feedback | Developer review comments feed back into next iteration |

**Final Cause: What is its purpose?**

| Dimension | Answer |
|-----------|--------|
| User Need | Reduce time from issue to initial PR for well-defined tasks |
| Business Goal | Free developer time for complex design work |
| Success Criteria | 70% of agent PRs merged with minor edits; avg 2hr vs 6hr manual |
| Absence Test | Without it, developers spend 60% of time on routine implementation |
| Purpose Drift Risk | Agent scope creeping to complex architectural tasks it's not suited for |

### Cross-Cause Analysis

| Alignment | Finding |
|-----------|---------|
| Material ↔ Final | 200K context may be insufficient for large repos. Purpose requires understanding full codebase, but material limits what the agent can "see." **Action:** Implement smart context selection. |
| Formal ↔ Efficient | Plan-then-execute pattern fits CI trigger well. No mismatch. |
| Material ↔ Formal | Tool boundaries (no secrets access) align with stateless architecture. Good fit. |
| Efficient ↔ Final | 10-min timeout may conflict with "well-defined tasks" that touch many files. **Action:** Define task complexity limits for agent-eligible issues. |

### Outcome
The Four Causes analysis revealed two mismatches: context window vs. codebase size, and execution timeout vs. task complexity. Both were invisible when looking at individual causes but became clear in cross-cause analysis. The team added context selection logic and task complexity scoring before deployment.

---

## Template

```markdown
# Four Causes Analysis: [System/Component Name]

**Date:** YYYY-MM-DD | **Analyst:** [Name] | **Duration:** X min

## Material Cause: What is it made of?
| Component | Specifics |
|-----------|-----------|
| Model/Runtime | |
| Tools/Libraries | |
| Data/Inputs | |
| Infrastructure | |
| Dependencies | |
| Human Skills | |

## Formal Cause: What shape does it take?
| Aspect | Design |
|--------|--------|
| Architecture | |
| Patterns | |
| Interfaces | |
| State Management | |
| Boundaries | |

## Efficient Cause: What process creates it?
| Phase | Mechanism |
|-------|-----------|
| Trigger | |
| Build/Assembly | |
| Execution | |
| Validation | |
| Feedback/Evolution | |

## Final Cause: What is its purpose?
| Dimension | Answer |
|-----------|--------|
| User Need | |
| Business Goal | |
| Success Criteria | |
| Absence Test | |
| Purpose Drift Risk | |

## Cross-Cause Analysis
| Alignment | Finding |
|-----------|---------|
| Material ↔ Final | |
| Formal ↔ Efficient | |
| Material ↔ Formal | |
| Efficient ↔ Final | |

## Key Insights
1. [Mismatches discovered]
2. [Gaps identified]
3. [Recommendations]
```

---

## Quick Reference Card

```
+-------------------------------------------------+
|  FOUR CAUSES QUICK REFERENCE                    |
+-------------------------------------------------+
|  Core Question: "Why does this exist and        |
|                  what is it for?"                |
+-------------------------------------------------+
|  1. MATERIAL:  What is it made of?              |
|     (tech, data, infra, dependencies, people)   |
|  2. FORMAL:    What shape does it take?          |
|     (architecture, patterns, interfaces)        |
|  3. EFFICIENT: What process creates it?          |
|     (triggers, workflows, build, feedback)      |
|  4. FINAL:     What is its purpose?              |
|     (user need, business goal, success metric)  |
|  5. CROSS-CAUSE: Where do causes conflict?       |
+-------------------------------------------------+
|  KEY INSIGHT:                                   |
|  The most valuable finding is usually a         |
|  mismatch BETWEEN causes, not within them       |
+-------------------------------------------------+
|  VIBE CODING TEST:                              |
|  Can you articulate all four causes clearly?    |
|  If not, you're building without understanding  |
+-------------------------------------------------+
|  AVOID: Skipping final cause, confusing         |
|  material with formal, listing without          |
|  analyzing cross-cause relationships            |
+-------------------------------------------------+
```

---

## Related Lenses

- **First Principles** - Deconstructs assumptions (Four Causes provides the complete picture that First Principles then challenges)
- **Systems Thinking** - Maps interactions between components (Four Causes explains why each component exists)
- **Constraint Analysis** - Identifies blockers (often found in material or efficient cause gaps)
- **Comparative Analysis** - Compares options (use Four Causes to fully understand each option first)

---

*Part of the Agentic-Oriented Development thinking methodology collection.*
