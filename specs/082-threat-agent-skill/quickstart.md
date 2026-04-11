# Quickstart: Feature 082 — Threat Agent Skill References

**Audience**: Contributors who will implement, review, or extend Feature 082
**Status**: Phase 1 design artifact
**Parent**: [plan.md](./plan.md)

## The 60-Second Summary

tachi has 17 agents. 6 infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) use a **lean + skill references** pattern — agent files are orchestration-only, domain knowledge lives in `.claude/skills/tachi-*/references/*.md` files loaded via `**MANDATORY**: Read` directives. 11 threat detection agents (6 STRIDE + 5 AI) use a **self-contained** pattern — detection patterns, finding templates, and OWASP 3×3 matrices are all inline in the agent files.

Feature 082 moves the 11 threat agents onto the lean pattern — as a **sibling variant** of the methodology variant. The difference: detection agents have a **single-point load** (one `**MANDATORY**: Read` directive at the start of `## Detection Workflow`), not phase-gated loads like control-analyzer.

After the refactor, all 17 agents follow one architectural pattern with two documented shapes: methodology (phase-gated) and detection (single-point).

Additionally, each extracted reference file is opportunistically enriched with ≥2 new detection pattern categories citing primary sources (OWASP/CWE/MITRE ATT&CK/MITRE ATLAS/NIST). Aggregate floor: ≥22 new categories across all 11 agents. De-scopable per agent.

## The 5-Minute Walkthrough

### 1. What changes

**Before** (current state — example: `.claude/agents/tachi/spoofing.md`, 113 lines):

```
---
name: spoofing
description: STRIDE spoofing threat detection
model: sonnet
tools: [Read, Glob, Grep]
---
<metadata YAML block>

## Purpose
...5-line paragraph...

## Detection Scope
<39 lines of inline pattern tables with OWASP/CWE/MITRE citations>

## Finding Template
<16 lines of inline finding field guidance>

<inline OWASP 3×3 risk matrix — 9 lines>

## References
<14 lines of citation list>
```

**After** (target state — `.claude/agents/tachi/spoofing.md`, ≤120 lines, typical ~70-90):

```
---
name: spoofing
description: STRIDE spoofing threat detection
model: sonnet
tools: [Read, Glob, Grep]
---
<metadata YAML block — unchanged>

## Purpose
<1-3 lines — much shorter>

## Skill References
| Reference | File | Load When | Purpose |
|-----------|------|-----------|---------|
| Detection patterns | .claude/skills/tachi-spoofing/references/detection-patterns.md | Always, at detection start | Threat patterns + OWASP/CWE/MITRE citations |
| Finding format | .claude/skills/tachi-shared/references/finding-format-shared.md | Always, at detection start | Producer finding construction guidance |
| Severity bands | .claude/skills/tachi-shared/references/severity-bands-shared.md | Always, at detection start | OWASP 3×3 risk matrix |

## Detection Workflow
**MANDATORY**: Read `.claude/skills/tachi-spoofing/references/detection-patterns.md` — load pattern catalog before analysis.
**MANDATORY**: Read `.claude/skills/tachi-shared/references/finding-format-shared.md` — load finding construction guidance.
**MANDATORY**: Read `.claude/skills/tachi-shared/references/severity-bands-shared.md` — load OWASP 3×3 matrix.

1. Iterate dispatched components
2. Match against loaded detection patterns
3. Construct findings using shared producer format
4. Emit findings to orchestrator

## Empty Results Handling
<preserved as-is from pre-refactor>

## Output Handoff
<preserved as-is from pre-refactor>
```

And a new companion directory:

```
.claude/skills/tachi-spoofing/references/detection-patterns.md  (~150-250 lines)
```

Containing the pre-refactor inline patterns **plus** ≥2 new enriched categories (e.g., OAuth token replay from OWASP A07 + cloud-IAM role chain abuse from MITRE ATT&CK T1078.004).

### 2. Why this shape instead of control-analyzer's phased shape

Control-analyzer is a methodology agent. It has 6 sequential phases (Parse → Discover → Detect → Classify → Recommend → Output) and loads different skill references at different phase boundaries. A phased skill-reference structure matches its actual pipeline shape.

Threat detection agents have one effective phase: match trigger → apply patterns → emit findings. Forcing them into a phased shape would be wrong — the agent file would pretend to have phases it doesn't have. Instead, we use **single-point load**: one `**MANDATORY**: Read` directive at the start of `## Detection Workflow`, and all detection knowledge is loaded there. The section name matters: use `## Detection Workflow`, not `## Phase Workflow`, to avoid implying multi-phase structure.

This is the **sibling variant** of the lean pattern. ADR-023 records it as the second lean-agent shape in tachi.

### 3. Phase 1 prototype gate

You will not touch 9 agents until 2 prototype agents (spoofing from STRIDE, prompt-injection from AI) pass validation in two sub-phases:

- **Phase 1a** (refactor-only): Extract without adding new patterns. Re-run pipeline on all 6 examples. Expected: **zero** new findings. If you see new findings from Phase 1a, you accidentally changed detection semantics — stop and diagnose.
- **Phase 1b** (enrichment): Add ≥2 new pattern categories per prototype agent. Re-run pipeline. Expected: **≥1** new finding surfaces on the prototype agents' example surface — otherwise enrichment is theater.

The gate is real. Feature 078's T014 gate (predecessor pattern) caught a clamping bug on its first iteration. Max 2 gate iterations before the feature is escalated for PRD re-scoping (fallback: ship STRIDE-only PRD 082, defer AI agents to PRD 083).

### 4. Phase 2 parallelization and serialization

Phase 2 extracts 9 agents in parallel waves — **but** shared reference consolidation is NOT parallelized.

- **Parallel (OK)**: Editing `.claude/agents/tachi/<agent>.md` and creating `.claude/skills/tachi-<agent>/references/*.md` for different agents simultaneously. Different files, no conflicts.
- **Serial (MUST)**: Editing `.claude/skills/tachi-shared/references/finding-format-shared.md`. Single writer wave (Phase 2c). If two parallel tracks both tried to append a producer section, they would conflict.
- **Serial (MUST)**: Cross-agent overlap audit (Phase 2d). Requires reading all 11 reference files to find duplications — cannot be parallelized.

### 5. Shared reference edits are additive-only

This is the single most important constraint. `.claude/skills/tachi-shared/references/*.md` files are already consumed by 6 infrastructure agents in production. A breaking edit would silently regress the infra tier. Therefore:

- **NEVER** modify existing content in a shared reference file
- **ALWAYS** append new sections (new `## ` headings) after existing content
- **ESCALATE** if existing content must change — create a new file alongside, don't edit

`finding-format-shared.md` needs a new `## For Threat Agents (Producers)` section. Append it. Do not touch anything that exists there today.

### 6. MAESTRO is off-limits to threat agents

Threat agents do NOT reference MAESTRO. MAESTRO inheritance runs orchestrator-side in Phase 3 Table Assembly — the orchestrator attaches `maestro_layer` to each finding based on the component inventory. Threat agents produce findings without `maestro_layer`; the orchestrator adds it on merge.

If you see a contributor trying to add `maestro-layers-shared.md` to a threat agent's Skill References table, reject the change in code review. This is verified post-refactor by `grep -l "maestro" .claude/agents/tachi/<threat-agent>.md` returning zero matches.

### 7. Per-agent commit discipline

Each of the 11 agent extractions is a separate commit (or a self-contained cluster of commits scoped to one agent). Why: if Phase 2 or Phase 3 surfaces an issue with a specific agent, that one agent can be reverted without touching the others. Verified via `git log --oneline` showing ≥11 agent-specific commit messages in the refactor PR.

Shared reference edits (Phase 2c) are their own commit. ADR-023 is its own commit. Example regeneration + re-baseline is its own commit (or per-example commits).

### 8. Byte-deterministic PDF re-baseline is expected

Any edit to a `tachi-shared/references/*.md` file will flow through to infrastructure agents, which write to the report pipeline. Per ADR-021 (SOURCE_DATE_EPOCH determinism), this diffs the 5 byte-deterministic example PDFs at the byte level even if content is equivalent. Re-baselining is **expected**, not an incident. The process mirrors Feature 136:

```bash
SOURCE_DATE_EPOCH=1700000000 <regenerate 5 non-agentic examples>
```

Commit the new `*.pdf.baseline` files in the same PR as the refactor.

The `agentic-app` example is NOT byte-deterministic (Feature 128 convention). Its PDF is regenerated with Gemini JPEGs and doesn't need byte re-baseline.

### 9. Primary source set for enrichment

Allowed sources for citing new detection pattern categories:

| Source | Use for |
|--------|---------|
| OWASP Top 10 (2021+) | STRIDE baseline |
| OWASP LLM Top 10 (v2025+) | AI agents (canonical LLM reference) |
| OWASP AI Exchange (CC0) | AI agents (best — zero attribution needed) |
| MITRE ATT&CK (v15+) | STRIDE industrial-grade coverage |
| MITRE ATLAS (v5.1+ Nov 2025) | AI adversarial (includes Oct 2025 agent techniques AML.T0058-T0062) |
| CWE Top 25 (2024+) | STRIDE weaknesses (SSRF, resource exhaustion, authorization) |
| NIST AI RMF / AI 600-1 | AI framing only (supporting citation, NOT sole source) |

Every new pattern category must cite at least one source with a canonical URL or identifier. NIST alone is not sufficient — it's framing-oriented, not detection-signature-oriented.

### 10. What tests to run at each phase gate

**Phase 1a gate**:
```bash
# Line count check
wc -l .claude/agents/tachi/spoofing.md .claude/agents/tachi/prompt-injection.md
# Expected: spoofing ≤120, prompt-injection ≤150

# Full pipeline regeneration
for example in web-app microservices ascii-web-api mermaid-agentic-app free-text-microservice agentic-app; do
    /tachi.threat-model examples/$example/
done

# Content-level diff
diff <(pre-refactor threats.md) <(post-refactor threats.md)
# Expected: zero new findings (refactor is transparent)
```

**Phase 1b gate**:
```bash
# Same regeneration + diff
# Expected: ≥1 new finding on prototype agents' example surface (enrichment is working)
# Expected: no dropped findings (enrichment is additive)
```

**Phase 3 gate**:
```bash
# Full regression + byte-determinism re-baseline
SOURCE_DATE_EPOCH=1700000000 ./regenerate-5-byte-deterministic-examples.sh
# Commit new *.pdf.baseline files
```

### 11. Files you will touch

- **11 threat agent files** at `.claude/agents/tachi/*.md` (modify in place)
- **11 new companion skill directories** at `.claude/skills/tachi-<agent-name>/references/` (create with ≥1 reference file each, typically `detection-patterns.md`)
- **1 shared reference file** at `.claude/skills/tachi-shared/references/finding-format-shared.md` (append new section in Phase 2c only)
- **1 new ADR** at `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` (create in Phase 1)
- **1 tech stack doc** at `docs/architecture/00_Tech_Stack/README.md` (update agent inventory section in Phase 3)
- **6 example `threats.md` files** regenerated in Phase 3 + **5 example `security-report.pdf.baseline` files** re-baselined
- **CHANGELOG.md** (auto-generated by release-please on merge)

### 12. Files you will NOT touch

- `scripts/*.py` — no code changes, stdlib-only convention preserved
- `schemas/finding.yaml` — stays at v1.3
- `templates/tachi/security-report/*.typ` — no Typst template changes
- `.github/workflows/tachi.threat-model.yml` — no CI workflow changes
- `orchestrator.md` — the orchestrator is unchanged; interface with threat agents is byte-identical
- `control-analyzer.md` — used as reference pattern only, not modified
- Any `tachi-shared/references/*.md` file OTHER than appending producer section to `finding-format-shared.md`
- `maestro-layers-shared.md` — off-limits to threat agents (FR-9)

## Common pitfalls

**Pitfall 1**: "I'll fix the consumer-oriented content in `finding-format-shared.md` while I'm there." — NO. Existing content is untouchable. Append a new section.

**Pitfall 2**: "I'll add MAESTRO to the AI agents' skill references — it's cleaner." — NO. MAESTRO is orchestrator-owned. Threat agents stay MAESTRO-agnostic.

**Pitfall 3**: "I'll extract 6 agents in parallel and edit `finding-format-shared.md` in each track." — NO. Shared reference edits are Phase 2c only, single writer.

**Pitfall 4**: "The 150-line target is aspirational; I'll go over on a few agents." — NO. The hard ceiling is 180 for any agent. Tier targets (STRIDE ≤120, AI ≤150) are enforced. Stretch targets (≤90 / ≤130) are bonus.

**Pitfall 5**: "The `## Detection Workflow` section should really be `## Phase Workflow` for consistency with control-analyzer." — NO. Detection agents have one phase, not six. Naming matters.

**Pitfall 6**: "I'll add 3 new pattern categories to every agent — uniform distribution is cleaner." — Consider it, but remember: the floor is **aggregate** ≥22. If one agent's enrichment research is slow, de-scope its enrichment and make up the floor on other agents. Do not let enrichment scope block the architectural refactor.

**Pitfall 7**: "The byte-deterministic PDFs diffed — something must be wrong." — If your diff came AFTER a shared reference edit, it's expected. Re-baseline (R6 is the mitigation). If it came from a refactor-only Phase 1a change with zero shared ref edits, something IS wrong — investigate.

## Where to find more context

- **Spec**: [spec.md](./spec.md) — 20 FR, 14 SC, 5 user stories, full traceability to PRD 082
- **Plan**: [plan.md](./plan.md) — technical context, components, data flow, tech stack, constitution check
- **Data model**: [data-model.md](./data-model.md) — file entities and invariants
- **Research**: [research.md](./research.md) — codebase inventory, architecture context, primary source evaluation
- **PRD**: [../../docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](../../docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)
- **Architect PRD review**: `.aod/results/architect.md`
- **Team-lead PRD review**: `.aod/results/team-lead.md`
- **Reference implementation** (methodology variant): `.claude/agents/tachi/control-analyzer.md` (427 lines, 3 phase-gated reads)
- **Feature 078 precedent**: `specs/078-agent-context-optimization/tasks.md` (T014 prototype gate)
- **Feature 136 precedent**: CLAUDE.md "Recent Changes" section for the `maestro-layers-shared.md` re-baseline pattern
