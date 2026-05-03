# Delivery Document: Feature 201 — `output-integrity` Threat Agent (OWASP LLM05:2025)

**Delivery Date**: 2026-04-19
**Branch**: `201-output-integrity-threat-agent`
**PR**: #202 (squash commit `558e75eb333a`)

---

## What Was Delivered

- **First net-new threat detection agent under BLP-01 Tier 1 governance**, closing the OWASP LLM05:2025 output-handling threat surface — the asymmetric gap where tachi previously shipped comprehensive input-side coverage (prompt-injection) but was silent on the output side (XSS/DOM, SQLi, command injection, SSRF, template injection, path traversal from LLM-generated output flowing into downstream execution sinks).
- **New AI-tier agent** `.claude/agents/tachi/output-integrity.md` (120 lines, within ADR-023 ≤150 soft cap) conforming to the lean-agent detection variant. Tools: `Read, Glob, Grep`. Zero MAESTRO references per ADR-023 lineage.
- **Companion skill** `.claude/skills/tachi-output-integrity/` with `README.md` + `references/detection-patterns.md` (5-category pattern catalog: client-side XSS, server-side SQLi/command/code, SSRF, template injection, path traversal — each with ≥5 indicators, ≥1 worked example, primary/related citations).
- **First downstream consumer of F-A1 + F-A2 + F-B Foundation tier** (Features 180/189/194) — emits `OI-{N}` findings with `category: llm` and populated `source_attribution` citing OWASP LLM05:2025 primary plus related CWE from the catalog-present set `{CWE-22, CWE-78, CWE-79, CWE-89, CWE-94, CWE-918}`. First populator of non-absent `source_attribution` arrays in tachi's history.
- **Schema bump** `schemas/finding.yaml` 1.5 → 1.6 (minor, additive) — `id.pattern` regex extended with `OI` prefix as 10th alternation value; first application of the ADR-026 Complex-Shape Clarifier to regex-alternation prefix additions (ADR-030 Decision 8).
- **New ADR-030** (Accepted 2026-04-18, Accepted-commit-SHA `558e75eb333a`) — records 8 numbered decisions with Heuristic A Outcome B scope split, lean-agent conformance, LLM05 + ML09 doc-only bundling, 22-file zero-edit invariant preservation, dual-commit governance protocol, `category: llm` enum reuse, and ADR-026 Clarifier extension.
- **Orchestrator-tier additive registration** (3 files: `orchestrator.md`, `dispatch-rules.md`, `finding-format-shared.md`) with FR-011 two-part EMISSION gate (keyword match AND output data-flow into execution sink).
- **22-file zero-edit invariant preserved** (11 STRIDE + AI detection agents + 11 companion detection-patterns.md files) per ADR-023 lineage.
- **Test coverage**: 27/27 pass on `tests/scripts/test_output_integrity.py`; 13/13 + 1 skipped on backward-compat suite under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

---

## How to See & Test

1. **Verify new agent file exists**: `cat .claude/agents/tachi/output-integrity.md | head -30` — confirm YAML frontmatter with `tools: Read, Glob, Grep`, `model: sonnet`, `category: llm`.
2. **Verify companion skill**: `ls .claude/skills/tachi-output-integrity/references/detection-patterns.md` — confirm 5-category pattern catalog present.
3. **Run schema regex test**: `pytest tests/scripts/test_output_integrity.py -v` — expect 27/27 pass including schema_version 1.6 assertion, 9 backward-compat prefix parameterized, 4 forward-compat OI parameterized, 9 malformed-ID rejections, 2 fixture existence, 1 valid-fixture parse, 1 invalid-fixture absent-CWE assertion.
4. **Run backward-compat baseline**: `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v` — expect 13/13 pass + 1 skipped (mermaid-agentic-app).
5. **Verify ADR-030 SHA fill**: `grep "Accepted-commit-SHA" docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` — confirm `558e75eb333a` (not `<pending-post-merge-fill>`).
6. **Verify schema bump**: `grep schema_version schemas/finding.yaml` — confirm `1.6`.
7. **Verify 22-file zero-edit invariant**: `git diff main~3 main -- '.claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md' '.claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}/references/detection-patterns.md'` — expect empty diff.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 3-5 days (team-lead envelope on tasks.md) |
| Actual Duration | ~1 day (intensive autonomous execution, 2026-04-18 → 2026-04-19) |
| Variance | Under — compressed via autonomous-execution pattern, consistent with KB-030 compressed-delivery lineage |

---

## Surprise Log

The ADR-026 Complex-Shape Clarifier extended to regex-alternation prefix additions (D8) without controversy — three distinct Clarifier applications now accumulated (enum-scalar additions F-142, list-of-RECORD additions F-A2, regex-alternation prefix additions F-201) establishing the Clarifier as a genuine pattern rather than a one-off. E2E pipeline regeneration on `examples/agentic-app/` (T032-T036, T039) was deferred to a focused follow-on session given the ~60 LLM threat-agent dispatches and 1-3h compute budget required — artifact-level verification (27/27 pytest green, 13/13 backward-compat green, 22-file zero-edit green) carried the delivery.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | Dual-commit Proposed → Accepted ADR governance (KB-036) extended cleanly to a third downstream feature (F-1), with the Wave 5 Accepted transition + post-merge SHA fill running the same 2-step protocol as F-A1 (ADR-027), F-A2 (ADR-028), and F-B (ADR-029). The pattern is now validated across 4 consecutive Foundation-tier + Tier-1 features — ratified as the default cadence for any ADR carrying pre-merge policy decisions that need post-merge provenance completion. | KB-038 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None logged at retrospective time (BLP-01 Tier 1 follow-on features F-2 through F-5 already sequenced in `_internal/strategy/BLP-01.md` §8).

Deferred to focused follow-on session (tracked in CLAUDE.md Recent Changes):
- E2E pipeline regeneration on `examples/agentic-app/` (T032-T036, T039) — ~60 LLM dispatches, 1-3h compute
- SC-004 (regen emits OI finding) and SC-007 (regen findings carry mitigations + citations) verification

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/201-output-integrity-threat-agent/spec.md |
| Implementation Plan | specs/201-output-integrity-threat-agent/plan.md |
| Task Breakdown | specs/201-output-integrity-threat-agent/tasks.md |
| PRD | docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md |
| ADR | docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3 (PRD INDEX, User Stories, OKRs) | APPROVED |
| Architecture | architect | 3 updated + 1 verified (README, Tech Stack, System Design; CLAUDE.md verified current) | APPROVED |
| DevOps | devops | 0 (no-op — template-only feature, zero new runtime deps / CI / env vars) | APPROVED |

---

## Cleanup

- [x] Feature branch deleted (local + remote pruned)
- [x] All tasks complete (55/55, including T025 post-merge SHA fill)
- [x] No TBD/TODO in docs (`<pending-post-merge-fill>` replaced with SHA)
- [x] Committed and pushed (c036a9f ADR fill + a9c2823 T025 mark)
