# ADR-010: Minimal-Return Architecture for Subagent Context Optimization

**Status**: Accepted (Partially Superseded)
**Date**: 2026-03-04
**Superseded By**: Feature 093 — Relocate Governance Results (2026-03-19)
**Supersession Scope**: Directory location only. `.claude/results/` → `.aod/results/`. All other decisions (file-based offloading, overwrite semantics, 10-line cap, convention-based enforcement) remain in effect. Cause: Claude Code platform write-protection on `.claude/` directory triggers interactive permission prompts, breaking autonomous governance flows.
**Deciders**: Architect, product-manager, team-lead
**Feature**: 073 — Minimal-Return Architecture for Subagent Context Optimization
**PR**: #74

---

## Context

AOD Kit governance workflows invoke subagents (product-manager, architect, team-lead) via the Agent/Task tool to perform Triad reviews at spec/plan/tasks boundaries. Each reviewer was returning its complete findings inline to the calling orchestrator — 500 to 2,000 tokens per return. In a single Triad review cycle (3 reviewers), this consumed 1,500 to 6,000 tokens in the main context before any implementation work could begin.

In full `/aod.run` lifecycle sessions (10+ delegations across Discover → Define → Plan → Build → Deliver), cumulative subagent return overhead was exhausting the context window within 30-60 minutes — well before the Build stage. Governance was becoming a liability: the more thorough the review, the more context it consumed, the shorter the remaining implementation window.

The challenge was to eliminate this overhead without losing any review content — the detailed rationale, specific concerns, and recommendations that make governance reviews valuable.

---

## Decision

We will implement a **file-based offloading architecture** for subagent returns:

1. **Subagents write detailed findings** to `.claude/results/{agent-name}.md` before returning
2. **Subagents return only** a brief status summary (STATUS + ITEMS + DETAILS path) to the main context, capped at 10 lines
3. **The main agent reads** the results file on-demand when it needs to act on specific findings
4. **CLAUDE.md** contains a project-wide "Subagent Return Policy" establishing this as the convention
5. **Each P0/P1 agent prompt** contains a "Return Format (STRICT)" section for agent-level enforcement
6. **`.claude/results/`** is gitignored as ephemeral session artifacts

---

## Rationale

**Why file offloading rather than inline truncation?**

Truncating returns would lose information. The governance reviews are valuable precisely because they are thorough. The goal is not to reduce what agents produce, but to change where it lives: disk vs. main context.

**Why `.claude/results/` rather than `.aod/results/`?**

`.aod/` contains persistent governance artifacts (spec.md, plan.md, tasks.md). Results files are ephemeral — session-scoped scratch space. Placing them in `.claude/results/` signals their transient nature and keeps `.aod/` semantically clean as the durable artifact store.

**Why overwrite semantics (not append)?**

Each subagent invocation produces a fresh review. Appending would accumulate stale reviews from prior invocations, increasing file size over a session and potentially confusing the main agent about which findings are current. Overwrite ensures the file always reflects the most recent review.

**Why convention-based rather than code-enforced?**

There is no runtime enforcement mechanism available in the Claude Code CLI environment — compliance must be achieved through prompt engineering. The two-layer approach (CLAUDE.md policy + per-agent return format blocks) provides reinforcement: the project-wide policy is discoverable, and the per-agent block is unavoidable at invocation time.

**Why cap at 10 lines rather than token count?**

Token counts are not directly measurable in Claude Code CLI sessions. Line count is a practical, observable proxy. 10 lines of brief return content (STATUS, ITEMS, file path, 1-2 contextual lines) maps to approximately 100-200 tokens — well within the target ceiling.

---

## Alternatives Considered

### Alternative 1: Response compression prompting

Instruct each reviewer to provide a "concise summary" rather than a full review, keeping everything inline.

**Pros**:
- Simpler implementation (no new files or directories)
- No change to calling workflow

**Cons**:
- Information loss — compressed summaries omit the rationale and specific concerns that make reviews actionable
- Model compliance is unreliable for compression instructions under adversarial framing ("be thorough")
- No structural guarantee of brevity

**Why Not Chosen**: Violates the core requirement of zero information loss.

### Alternative 2: Structured return format (STATUS + key findings, inline)

Define a rigid return schema that requires each reviewer to bullet the 3 most important findings, capped at 30 lines.

**Pros**:
- Still inline — no file I/O
- Forces structure and brevity

**Cons**:
- 30 lines × 3 reviewers = 90+ lines of review overhead per Triad cycle
- Limits finding count arbitrarily — reviewers with 5 genuine findings must drop 2
- No home for rationale, recommendations, or follow-up context

**Why Not Chosen**: Still consumes substantial context and creates artificial finding limits.

### Alternative 3: Separate review session per reviewer

Invoke each reviewer in a fully isolated session with no shared context.

**Pros**:
- Zero context overhead in the main orchestrator
- Reviewers have full context budget for their work

**Cons**:
- Loses orchestration continuity — the main agent can't correlate findings across reviewers
- Requires inter-session artifact passing via disk (essentially the same mechanism without the benefits)
- Complex coordination for approval aggregation

**Why Not Chosen**: The overhead is in the return, not the invocation. Isolation solves the wrong problem.

---

## Consequences

### Positive
- Triad review cycle cost drops from 1,500-6,000 tokens to less than 600 tokens (10x+ reduction)
- Main agent sustains coherent orchestration for 90+ minutes (vs. 30-60 minutes prior)
- Zero information loss — complete review content available on-demand via results files
- Pattern generalizes to any subagent type, not just governance reviewers
- Results files are structured and discoverable, supporting future tooling (diff, summary, audit)

### Negative
- Adds a file write step to every governance review — minor I/O overhead
- Main agent must Read the results file when acting on findings — one additional tool call per CHANGES_REQUESTED response
- Convention-based enforcement means non-compliant returns degrade gracefully rather than failing loudly

### Mitigation
- `.claude/results/` directory creation is handled by each subagent (self-healing, no pre-init required)
- The on-demand Read step (main agent reading results) is low-cost: one Read call adds approximately 2 seconds, saving hundreds of tokens
- Non-compliance degrades to current behavior (verbose inline returns), not to broken governance

---

## Related Decisions

- ADR-002: Prompt Segmentation — similar principle of deferring content to disk until needed
- ADR-006: Non-Fatal Observability Operations — non-compliance in return format is non-fatal

---

## References

- `specs/073-prd-073-minimal/spec.md` — Feature specification (12 functional requirements)
- `docs/product/02_PRD/073-minimal-return-architecture-2026-03-04.md` — Product requirements document
- `.claude/results/` — Runtime directory for ephemeral results (gitignored)
- `CLAUDE.md` — "Subagent Return Policy" section (project-wide convention)

---

**Template Instructions**: This ADR documents the accepted decision. Update status to Deprecated if superseded by a future context management ADR.
