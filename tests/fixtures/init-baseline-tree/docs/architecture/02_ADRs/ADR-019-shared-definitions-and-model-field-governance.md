# ADR-019: Shared Cross-Agent Definitions and Model Field Governance

**Status**: Accepted
**Date**: 2026-04-02
**Deciders**: Architect
**Feature**: 078 (Agent Context Optimization)

---

## Context

Feature 078 restructured all 6 methodology and report agents from monolithic prompts to lean definitions with on-demand skill references, extending the pattern established in ADR-002 (prompt segmentation). During restructuring, two architectural issues emerged that ADR-002 did not address:

1. **Cross-agent definition drift**: Severity band thresholds, STRIDE+AI category definitions, and finding format specifications were duplicated across multiple agent prompts. When one agent was updated (e.g., severity band boundaries in Feature 074), other agents retained stale copies. This caused inconsistent risk classifications between the orchestrator, risk-scorer, and control-analyzer.

2. **Implicit model assignment**: All 17 agent definitions inherited their model selection implicitly from the Claude Code runtime default. There was no mechanism to (a) verify which model an agent was designed for, (b) track model assignments across the agent set, or (c) intentionally assign different models to different task types (e.g., cheaper models for leaf agents, more capable models for orchestration).

**Constraints**:
- Shared definitions must be loadable via the existing Read tool pattern (no new infrastructure)
- Model field must be compatible with Claude Code's YAML frontmatter parsing
- Existing pipeline behavior must not regress
- Changes must apply across all 17 agents consistently

---

## Decision

We will:

1. **Create a `tachi-shared` skill directory** containing canonical reference files for definitions consumed by multiple agents. Each shared file is the single source of truth -- individual agents Read from this location rather than carrying inline copies.

2. **Add an explicit `model:` field to all 17 agent YAML frontmatter**, enabling intentional model-to-task matching and providing a discoverable audit surface for model assignments.

The shared definitions structure:

```
.claude/skills/tachi-shared/
  SKILL.md                          # Metadata + consumer mapping table
  references/
    severity-bands-shared.md        # Consumers: orchestrator, risk-scorer, control-analyzer
    stride-categories-shared.md     # Consumers: orchestrator, all 6 STRIDE agents
    finding-format-shared.md        # Consumers: all 17 agents
```

The model field convention:

```yaml
# In every agent's YAML frontmatter
model: sonnet    # Intentional model assignment
```

---

## Rationale

**Reasons**:
1. **Single-source-of-truth eliminates drift**: When severity band thresholds change, one file update propagates to all consuming agents. No agent carries a stale copy.
2. **Grep-auditable model assignments**: `grep "^model:" .claude/agents/tachi/*.md` shows all model assignments in one command, enabling cost tracking and intentional model selection.
3. **Extends existing pattern naturally**: Shared definitions use the same Read-tool loading mechanism as agent-to-skill references (ADR-002). No new infrastructure required.
4. **Low adoption cost**: Adding `model: sonnet` to frontmatter is a one-line change per agent. Creating shared reference files is a content move, not a behavioral change.
5. **Prevents future drift by design**: New agents must reference shared definitions rather than embedding copies, enforced by the best practices document (`_TACHI_AGENT_BEST_PRACTICES.md`).

---

## Alternatives Considered

### Alternative 1: Inline Definitions with Linting
**Pros**:
- No shared files to manage
- Each agent is self-contained

**Cons**:
- Linting catches drift after the fact, not at authoring time
- N agents means N copies to update for every definition change
- No tooling exists for cross-agent definition validation in the current stack

**Why Not Chosen**: Prevention is more reliable than detection. The shared file pattern eliminates the drift category entirely.

### Alternative 2: Model Field in a Central Configuration File
**Pros**:
- Single file for all model assignments
- Easy to review in one place

**Cons**:
- Separates model assignment from the agent it governs
- Claude Code reads frontmatter from agent files, not from an external config
- Adds indirection -- contributors must cross-reference two files

**Why Not Chosen**: Co-locating model assignment with the agent definition keeps governance visible at the point of use, aligned with Claude Code's frontmatter parsing.

---

## Consequences

### Positive
- Zero cross-agent drift for severity bands, categories, and finding format
- All 17 model assignments discoverable via single grep command
- Shared definitions independently editable without touching agent prompts
- Best practices document prevents regression in future agent authoring

### Negative
- Agents now have a runtime dependency on shared reference files (missing file = Read error)
- Contributors must know to check `tachi-shared` before duplicating definitions
- Model field is currently uniform (`sonnet` for all) -- the governance value is preparatory

### Mitigation
- Each agent's navigation table lists shared references with explicit paths, making dependencies discoverable
- Best practices document codifies the shared-first convention for new agents
- Model field governance enables future differentiation (e.g., cheaper models for leaf agents) without structural changes

---

## Related Decisions

- [ADR-002](ADR-002-prompt-segmentation.md): Prompt segmentation pattern that this decision extends to cross-agent shared content
- [On-Demand Reference File Segmentation](../03_patterns/README.md#pattern-on-demand-reference-file-segmentation): Pattern documentation (Example 4 added for Feature 078)

---

## References

- `.claude/skills/tachi-shared/` -- Shared definitions skill directory
- `.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md` -- Agent authoring conventions
- `specs/078-agent-context-optimization/spec.md` -- Feature specification
