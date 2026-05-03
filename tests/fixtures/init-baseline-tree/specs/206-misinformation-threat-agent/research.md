# Research Summary: `misinformation` Threat Agent (F-2)

**Feature**: Feature 206 — LLM09 Misinformation Detection
**PRD**: `docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md`
**Created**: 2026-04-23
**Scope**: Ground the spec in codebase reality and F-1 precedent; no new derivations.

---

## Knowledge Base Findings

**F-1 (Feature 201) delivery retrospective** — the most directly applicable KB source for F-2:

- **Duration**: Estimated 3-5 days → **actual ~1 day autonomous** (KB-030 compressed-delivery lineage). F-2 PRD envelope is 2 working days with 1 buffer — conservative against F-1 experience.
- **What worked (reuse for F-2)**:
  - ADR-023 lean-agent discipline: 120-line agent file, 5-section canonical shape, tools `Read, Glob, Grep`, zero MAESTRO references
  - Companion skill pattern `.claude/skills/tachi-{name}/references/detection-patterns.md` with 5-category catalog
  - Dual-commit Proposed→Accepted ADR protocol (now validated across 4 features)
  - 22-file zero-edit invariant preserved by construction (grep-audited pre/post)
  - Artifact-level verification carried delivery; E2E regeneration deferred to focused follow-on
- **Surprises**:
  - ADR-026 Complex-Shape Clarifier extended cleanly to regex-alternation prefixes (ADR-030 Decision 8) — now 3 applications, repeating pattern
  - E2E pipeline regeneration (~60 dispatches, 1-3h) is too heavy for main delivery window

**Memory entries relevant to F-2**:
- `project_blp01_threat_coverage.md` — F-2 explicitly identified as LLM09 closure agent; signal class is epistemics/grounding, distinct from F-1's encoding/sanitization class
- `project_tachi_source_of_truth.md` — F-2 must strengthen the upstream machine-readable contract (populate `source_attribution`, emit catalogued IDs only)
- `feedback_separate_aod_tachi.md` — never modify AOD upstream for tachi-specific changes

---

## Codebase Analysis

### F-1 precedent files (direct structural mirror for F-2)

- **`.claude/agents/tachi/output-integrity.md`** — 120 lines (≤150 AI tier cap). Structure: YAML frontmatter (name, description, tools, model) → metadata YAML (category, threat_class, dfd_targets, owasp_references, output_schema) → `## Purpose` → `## Skill References` table → `## Detection Workflow` (single `**MANDATORY**: Read` at start) → optional `## Example Findings` (3 worked examples present).
- **`.claude/skills/tachi-output-integrity/README.md`** — 23 lines; consumers list + purpose header + layout overview.
- **`.claude/skills/tachi-output-integrity/references/detection-patterns.md`** — 14,641 bytes; frontmatter (`consumers: [tachi-output-integrity]`, `last_updated`) + `## Overview` + `## Detection Scope` (Trigger Keywords + Applicable DFD Element Types) + `## Detection Patterns` (5 numbered categories with indicators, worked examples, primary + related citations).

### Orchestrator dispatch integration (additive-edit surfaces)

- **`.claude/agents/tachi/orchestrator.md:296`** — sequential-mode text currently reads `prompt-injection then data-poisoning then model-theft` (pre-F-1 state). **F-1 carry-over**: F-1 extended dispatch to four agents but left prose-tier text at three-agent pre-F-1. F-2 reconciles by extending to **five agents**: `prompt-injection then data-poisoning then model-theft then output-integrity then misinformation`.
- **`.claude/agents/tachi/orchestrator.md:370`** — LLM Threats table row currently `prompt-injection, data-poisoning, model-theft`. F-2 extends to `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation` (same F-1 carry-over reconciliation).
- **`.claude/skills/tachi-orchestration/references/dispatch-rules.md:71-74`** — LLM dispatch list (post-F-1 quartet). F-2 adds 5th entry `misinformation (OWASP LLM09:2025)` with FR-011-style two-part emission activation rule.
- **`.claude/skills/tachi-orchestration/references/dispatch-rules.md:120`** — table row mapping. F-2 extends the agent list consistently with orchestrator.md:370.
- **Edit ownership**: architect (per PRD FR-7; mirrors F-1 HIGH-1 resolution).

### Schema touchpoints

- **`schemas/finding.yaml:13`** — `schema_version: "1.6"` (F-1 bumped 1.5→1.6 for `OI`). F-2 bumps `1.6 → 1.7` for `MI`.
- **`schemas/finding.yaml:18`** — `pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"` (10 prefixes). F-2 extends to `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$` (11 prefixes). Additive, backward-compatible.
- **`schemas/finding.yaml:30-39`** — `category` enum carries 8 values including `llm`. F-2 reuses `llm` with `MI-{N}` ID prefix — **no enum edit**.
- **`schemas/taxonomy/owasp.yaml`** — LLM09 entry present: `id: LLM09`, `full_id: OWASP-LLM-2025-09`, `name: Misinformation`, `url: https://genai.owasp.org/llmrisk/llm092025-misinformation/`, `cwe_refs: []`. Empty `cwe_refs` means **finding-level CWE attribution is required** (no automatic inheritance via catalog edges).
- **`schemas/taxonomy/cwe.yaml`** — CWE-345 (Insufficient Verification of Data Authenticity) and CWE-223 (Omission of Security-relevant Information) both verified present with `full_id`, `name`, `url`.
- **`schemas/taxonomy/mitre-atlas.yaml`** — 12 AML techniques catalogued (`T0010, T0018, T0020, T0024, T0051, T0054, T0057, T0058, T0059, T0060, T0061, T0062`); **`AML.T0042` CONFIRMED ABSENT**. Pattern-catalog prose retains citation; `source_attribution` MUST NOT cite AML.T0042 (would fail F-A2 referential-integrity validator).

### Consumers list (finding-format-shared.md)

Current order (post-F-1): `orchestrator` → STRIDE-canonical (6) → AI-LLM-original (prompt-injection, data-poisoning, model-theft) → AI-AG (agent-autonomy, tool-abuse) → AI-LLM-new (output-integrity) → infra-consumer (risk-scorer). **F-2 placement**: append `misinformation` as the 2nd AI-LLM-new entry, between `output-integrity` and `risk-scorer`. Architect adjudicates final position at plan time.

### Example architectures

6 baseline architectures in `examples/`: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `agentic-app`. F-1 regenerated `agentic-app` on 2026-04-19. Current architecture has no explicit factual-output component (no medical/legal/financial advisory indicators). F-2 regeneration candidates: (a) extend `agentic-app` with factual-output sub-component, (b) author new `examples/advisory-app/`, (c) extend `mermaid-agentic-app`. Architect adjudicates at plan time (PRD Q4).

---

## Architecture Constraints

### Relevant ADRs (lineage F-2 inherits)

- **ADR-021** — SOURCE_DATE_EPOCH for byte-identical PDF regeneration (5-baseline gate per SC-6).
- **ADR-023** — Lean-agent detection variant + single-point load + zero MAESTRO references + additive-only shared-ref edits. Directly governs FR-1, FR-2, FR-3.
- **ADR-026** — Agentic pattern classification + Complex-Shape Clarifier minor-bump rule (extended by ADR-030 Decision 8 to regex-alternation prefix additions). Directly governs FR-4.
- **ADR-027** — F-A1 taxonomy crosswalk schema. Source of `taxonomy: owasp` enum values in F-2's `source_attribution`.
- **ADR-028** — F-A2 `source_attribution` contract. F-2 is second producer (after F-1) populating the field as production behavior.
- **ADR-029** — F-B coverage attestation PDF section. F-2 findings surface here post-regeneration.
- **ADR-030** — F-1 output-integrity agent — **direct precedent**. Decision 1 scopes F-1 to downstream-execution-sanitization leaving factual-integrity open for F-2. Decision 8 establishes regex-alternation minor-bump rule invoked by F-2's 1.6 → 1.7 bump.

### Governance constraints

- **24-file zero-edit invariant** (22 original + F-1's 2) on the detection tier. F-2 is purely additive; no edits to existing 24 files.
- **Orchestrator-tier carve-out** (SC-9 explicit exception): `orchestrator.md` and `dispatch-rules.md` receive minimal additive edits per FR-7.
- **Zero new dependencies**: empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **Referential integrity**: F-A2 validator rejects any `source_attribution` entry whose `{taxonomy, id}` is not in the catalog. AML.T0042 prose-only per confirmed-absent status.
- **Public ADR governance**: ADR-031 under `docs/architecture/02_ADRs/` with zero commercial framing (no Layer 2, no tachi Cloud).

---

## Industry Research

**OWASP LLM Top 10:2025 — LLM09 Misinformation**
- Canonical sub-classes: (a) hallucination / ungrounded factual emission, (b) citation fabrication, (c) overreliance on auto-action in high-stakes decisions
- Primary source: `https://genai.owasp.org/llmrisk/llm092025-misinformation/`
- Detection grounded in architectural indicators, not runtime monitoring (aligns with tachi's static-architecture scope)

**NIST AI 600-1 §2.4 Hallucination** — prose reference for regulatory-risk-register context; no catalog ID for `source_attribution`.

**MITRE ATLAS AML.T0042 Verify Attack** — relevant for adversarial-grounding context; confirmed absent from curated catalog → prose-only reference.

**CWE mappings (verified in catalog)**:
- CWE-345 (Insufficient Verification of Data Authenticity) — primary CWE for misinformation and citation fabrication
- CWE-223 (Omission of Security-relevant Information) — applicable to missing disclosure / grounding labels / HITL absence

**Relation to F-1 signal class (Heuristic A)**:
- F-1 `output-integrity` scope: downstream-execution-sanitization (bytes/strings/syntax primitives; machine-victim)
- F-2 `misinformation` scope: factual-integrity (factual-content primitives; human-victim and decision-cascade victim)
- Both agents may fire on a single LLM Process simultaneously — this is correct behavior per disjoint signal classes

---

## Recommendations for Spec

1. **Mirror F-1 spec verbatim where possible** — use `specs/201-output-integrity-threat-agent/spec.md` as the structural template; F-2 spec sections map 1:1 to F-1 sections.

2. **Preserve PRD's 3 user stories** (US-206-1, US-206-2, US-206-3) — they are already structured with Given/When/Then acceptance criteria and independently-testable predicates.

3. **Map PRD FR-1 through FR-7 to spec FR-001 through ~FR-019** — elaborate with testable predicates per the F-1 precedent (F-1 spec has FR-001 through FR-019 mapping to PRD FR-1 through FR-7).

4. **Translate PRD SC-1 through SC-10 into spec SC-1 through SC-12** — add verifiable success criteria for (a) 24-file zero-edit grep proof, (b) AML.T0042 absent-from-catalog confirmation, (c) byte-identity proof on 5 non-factual baselines.

5. **Carry forward PRD Q1-Q5** as architect-owned decisions — do NOT re-adjudicate in spec; defer to `/aod.project-plan`.

6. **Capture edge cases** — LLM keyword match without factual-output indicator (zero-emission), `agentic-app` regeneration interaction with F-1 OI findings, referential-integrity failure on absent catalog IDs, three-agent simultaneous emission on same LLM Process (correct behavior, not duplication).

7. **Include source attribution requirement** on every `MI-{N}` finding per PRD FR-5 — minimum `{taxonomy: owasp, id: LLM09, relationship: primary}`; CWE-345/CWE-223 as `relationship: related` per pattern category.

8. **Explicitly list 22-file zero-edit invariant extensions** — spec SC-9 enumerates the 24 files preserved (22 original detection-tier + F-1's 2). Orchestrator-tier carve-out explicit.

9. **Two-part emission gate** per PRD FR-7 — agent dispatched on LLM keyword match but self-gates emission to require BOTH keyword AND at least one factual-output indicator. Mirrors F-1 FR-011 zero-speculation discipline.

10. **No implementation details** — spec is WHAT and WHY only. Line counts, file paths, workflow steps belong to plan.md, not spec.md. (Exception: file paths from PRD are preserved where they define the contract surface, matching F-1 spec precedent.)
