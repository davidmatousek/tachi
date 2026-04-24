# ADR-031: `misinformation` Threat Agent (OWASP LLM09:2025 Coverage)

**Status**: Accepted
**Date**: 2026-04-23 (Proposed); 2026-04-24 (Accepted — provisional, post-merge SHA fill at T025)
**Deciders**: Architect (tachi project)
**Feature**: [206-misinformation-threat-agent](../../../specs/206-misinformation-threat-agent/spec.md)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (lean-agent detection variant — 24-file zero-edit invariant now 22 original + F-1's 2), [ADR-026](ADR-026-pattern-classification-mechanism.md) (minor-bump rule — extended by ADR-030 Decision 8; F-2 is the 2nd recorded application), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy enum source), [ADR-028](ADR-028-source-attribution-schema-extension.md) (F-A2 `source_attribution` contract — F-2 is second net-new producer after F-1), [ADR-029](ADR-029-coverage-attestation-report-section.md) (F-B downstream consumer — `has-source-attribution` fires true on regen), [ADR-030](ADR-030-output-integrity-agent.md) (F-1 precedent — Decision 1 scope bounds leaving factual-integrity to F-2; Decision 8 regex-alternation minor-bump rule F-2 invokes as 2nd application)

---

## Context

Tachi's agentic-AI threat-modeling pipeline ships, post-F-1 (Feature 201 merged 2026-04-19), 6 AI-tier detection agents covering the input-side (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`) and the output-sanitization surface (`output-integrity` — LLM05:2025). What remains silent is the **factual-integrity** signal class: LLM output that is syntactically well-formed and encoded safely for its downstream sink, yet factually ungrounded — emitting fabricated claims, hallucinated citations, or decision-critical recommendations without a declared grounding, verification, HITL, or calibration mechanism. OWASP LLM09:2025 (Misinformation) names this threat class as one of the top 10 LLM application risks for 2025, and ADR-030's Coverage Matrix analysis (at F-1 merge) explicitly recorded LLM09:2025 as **Planned** with F-2 named as the closure feature.

BLP-01 (Better LLM Protection initiative, documented in `_internal/strategy/BLP-01.md`) identifies the factual-integrity gap as Tier 1 priority F-2, following F-1 (`output-integrity` / LLM05) as the second net-new AI-tier agent under the ADR-023 lean pattern. F-2 is the **second net-new producer of `source_attribution`** in the tachi codebase (F-1 was the first) and the second trigger of the F-B `has-source-attribution: true` rendering path on regenerated example architectures. The BLP-01 Tier 1 Foundation infrastructure (F-A1 taxonomy catalogs per ADR-027, F-A2 source_attribution contract per ADR-028, F-B coverage-attestation section per ADR-029) is already shipped; F-2 is a pure consumer of that infrastructure with zero new runtime dependencies.

The feature introduces one new AI-tier agent `misinformation` plus a companion skill directory `tachi-misinformation/` with a pattern catalog covering five factual-integrity categories (Ungrounded Factual Emission, Citation Fabrication, Overreliance / Missing HITL on Decision-Critical Output, Retrieval-Grounding Gaps, Confidence-Calibration Absence). The agent file shape mirrors F-1's `output-integrity.md` verbatim per ADR-023's lean-agent detection variant. The schema `schemas/finding.yaml` receives a **second regex-alternation prefix addition** — `id.pattern` gains `MI` as an 11th alternation value — which is the second application of the ADR-030 Decision 8 regex-alternation minor-bump rule (first application: F-1's 1.5 → 1.6 bump; F-2's 1.6 → 1.7 bump preserves backward compatibility identically). The ADR-031 Proposed commit at Wave 1.1 is the schema-lock point that unblocks parallel Wave 2 authoring of the pattern catalog and the agent file.

PRD 206 was approved 2026-04-23 with full Triad sign-off (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS — all 6 HIGH/MEDIUM concerns resolved inline before sign-off). The spec was PM-approved same day with 1:1 PRD-to-spec FR mapping preserved. The **Heuristic A three-way scope question** — how `misinformation` (factual-integrity) partitions distinctly from both `prompt-injection` (input-side attacker injection) and `output-integrity` (downstream execution-sink sanitization) — was verified at T004 by the architect and recorded in `.aod/results/heuristic-a-verification.md`. The three-way partition is an **inheritance** of ADR-030 Decision 1's scope bounds (which explicitly left factual-integrity open for F-2), not a re-adjudication. Decision 2 below records the inheritance with explicit cross-reference to ADR-030.

### Constraints

- **24-file zero-edit invariant** (spec SC-009, FR-013 — ADR-023 lineage extended by F-1): F-2 MUST NOT edit any file under `.claude/agents/tachi/stride/` (6 files), `.claude/agents/tachi/ai/` (5 files), `.claude/agents/tachi/output-integrity.md` (1 file — F-1's agent), or `.claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy,output-integrity}/references/detection-patterns.md` (12 files). ADR-023 Decision 2 stabilized the original 22-file scope in Feature 082; F-1 added one new agent file plus one new companion skill at Feature 201 without reopening any of the 22. The invariant is now **22 original + F-1's 2 = 24 files**. F-2 preserves this by construction and adds one new agent (the 13th AI-tier file by authorship, the 7th AI-tier file in scope) and one new companion skill directory without reopening any of the 24 frozen files.
- **Byte-identity backward compatibility** (spec SC-006, FR-009 — ADR-021 lineage): the 5 non-factual example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. The F-A2 `has-source-attribution` conditional Section 9 already returns `false` on all 5 baselines post-F-1 (F-1's OI emission is confined to `agentic-app`). F-2's two-part emission gate (FR-011 — keyword match AND factual-output indicator both required) ensures zero `MI-{N}` findings on the 5 non-factual baselines, preserving byte-identity by construction.
- **Zero new runtime or developer dependencies** (spec SC-008): empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `package.json`. `pyyaml` and `pytest` remain developer-only per Feature 128 precedent. No new CLI prerequisite, no new LLM-judgment pathway.
- **F-A2 referential-integrity contract** (spec SC-010 — ADR-028 Decision 5 lineage): every emitted `MI-{N}` finding's `source_attribution` array MUST resolve every `(taxonomy, id)` pair against `schemas/taxonomy/{taxonomy}.yaml`. F-2 is the second net-new producer the validator at `scripts/tachi_parsers.py:826` enforces against. Pattern catalog worked examples MUST cite only catalog-resolvable IDs — MITRE ATLAS `AML.T0042 Verify Attack` is CONFIRMED ABSENT from the F-A1 catalog at PRD time and remains **prose-only** in the pattern catalog's Primary Sources list (FR-007 / FR-012).
- **Zero MAESTRO references** in agent file and companion skill (spec FR-010): grep-auditable invariant, identical to F-1 convention. MAESTRO layer assignment happens at orchestrator Phase 1 (Feature 084 / ADR-020) — F-2 agent does not author its own layer; `misinformation` findings inherit L5 Evaluation and Observability layer by orchestrator classification.
- **Heuristic A three-way scope discipline** (research.md §"Relation to F-1 signal class", plan.md Open Questions Q1, `.aod/results/heuristic-a-verification.md`): F-2 inherits the ADR-030 Decision 1 carve-out. `prompt-injection` owns the input-side attacker-injection signal class (machine-attacker, input primitives); `output-integrity` owns the downstream-execution-sanitization signal class (machine-victim, bytes/strings/syntax primitives) per ADR-030 Decision 1; `misinformation` owns the factual-integrity signal class (human-victim and decision-cascade-victim, factual-content primitives). Decision 2 below records the inheritance with explicit ADR-030 Decision 1 cross-reference.
- **Two-part emission gate** (spec FR-011 — zero-speculation discipline inherited from F-1): the agent dispatches on any LLM keyword match (same trigger logic as the other five LLM agents) but MUST only emit an `MI-{N}` finding when BOTH (a) the dispatched Process matches an LLM keyword AND (b) at least one factual-output indicator is structurally present in the component's description or connected Data Flows. If an LLM keyword matches but no factual-output indicator is present, the agent MUST emit zero findings for that component — dispatch still happens, but the agent self-gates emission to prevent false positives on LLM components whose output is purely stylistic.

---

## Decision

We adopt the new `misinformation` AI-tier threat agent per the 9 numbered decisions below. The agent ships with a companion skill directory, a regex-alternation schema bump from 1.6 to 1.7 (2nd application of ADR-030 Decision 8), one public per-feature ADR (this ADR), and one regenerated example (`agentic-app` extended with a factual-output sub-component per Q4 PM leaning; architect may invoke Q4 fallback to new `advisory-app` at 0.5-day buffer consumption if cumulative-state cost exceeds convention-preservation benefit). The 24-file zero-edit invariant (22 original + F-1's 2) and the 5-baseline byte-identity gate are preserved by construction. Eight of the nine decisions operationalize architectural questions raised in the PRD + spec + plan for F-2 specifically; Decision 8 records F-2 as the second application of the ADR-030 Decision 8 regex-alternation minor-bump rule, and Decision 9 records the deliberate CWE-1039 exclusion per architect MEDIUM-3 scope-discipline ruling.

### Decision 1 — Adopt new `misinformation` AI-tier agent for LLM09:2025 closure

We introduce `misinformation` as the 7th AI-tier threat agent under `.claude/agents/tachi/misinformation.md`, governed by the ADR-023 lean-agent detection variant and mirroring the F-1 `output-integrity.md` shape verbatim. The agent's canonical shape is 5 sections (YAML frontmatter → metadata YAML block → `## Purpose` → `## Skill References` table → `## Detection Workflow`) with an optional `## Example Findings` section, a ≤150-line soft target / ≤180-line hard ceiling, and exactly one `**MANDATORY**: Read` directive loading the companion pattern catalog at detection start.

The agent emits findings with `MI-{N}` ID prefix (per schema 1.7 regex extension, Decision 8 below) and `category: llm` (no new category enum value — LLM09 bundles cleanly under the existing `llm` category, mirroring F-1's Decision 7 enum-reuse discipline). Every finding carries a populated `source_attribution` array citing OWASP LLM09:2025 as `relationship: primary` plus one or more relevant CWEs (CWE-345 Insufficient Verification of Data Authenticity, and/or CWE-223 Omission of Security-relevant Information) as `relationship: related`. Mitigation text names a specific grounding, verification, HITL, or calibration mechanism matched to the pattern category — no generic "ground the LLM" or "add verification" prose.

The 6 existing AI-tier agents (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`, `output-integrity`) are NOT modified. `misinformation` is a sibling, not a refactor target. ADR-023's zero-edit invariant holds — the 12 frozen detection-tier agent files plus the 12 companion skill-reference files (24 total per F-1's extension) remain byte-identical at F-2 merge.

F-2 closes LLM09:2025 on the BLP-01 Coverage Matrix: the Planned row at ADR-030 merge transitions to Covered at F-2 merge with Feature 206 named as the closure feature (SC-013).

### Decision 2 — Heuristic A three-way scope inheritance from ADR-030 Decision 1

We adopt the **three-way signal-class partition** for LLM-tier agents recorded by the architect at T004 in `.aod/results/heuristic-a-verification.md`, with explicit inheritance from ADR-030 Decision 1. The three AI-tier agents concerned with LLM-output surfaces partition cleanly along orthogonal axes:

| Agent | Signal class | Victim model | Primitive type | OWASP primary | Example |
|---|---|---|---|---|---|
| `prompt-injection` | Input-side attacker injection | Machine-attacker (model behavior) | Input primitives — adversarial instructions embedded in user input, retrieved context, or upstream tool output | LLM01:2025, LLM07:2025 | User message concatenated into system prompt without delimiter enforcement; RAG-retrieved document embeds "ignore previous instructions" payload |
| `output-integrity` | Downstream-execution-sanitization | Machine-victim (execution sink) | Bytes / strings / syntax primitives — LLM output flows unsanitized into browser, SQL client, shell, template engine, HTTP client, or file writer | LLM05:2025 | LLM output rendered as raw HTML without entity encoding (XSS); LLM-generated WHERE clause concatenated into SQL query string without parameterization (SQLi) |
| `misinformation` (this feature) | Factual-integrity | Human-victim + decision-cascade-victim | Factual-content primitives — architecture-level absence of grounding / verification / HITL / calibration layer for factual, citation-bearing, or decision-critical output | LLM09:2025 | LLM emits clinical summary without RAG grounding or citation verification (ungrounded factual emission); LLM output drives auto-approve on high-stakes decision without HITL (overreliance) |

**Authority acknowledgment — inheritance, not re-adjudication**: **ADR-030 Decision 1 explicitly bounded F-1 scope to downstream-execution-sanitization (machine-victim, bytes/strings/syntax primitives) and explicitly left the factual-integrity signal class open for F-2.** The ADR-030 Context section named LLM09:2025 as Planned with F-2 as the closure feature, and ADR-030 Decision 2 Outcome B rationale (`.aod/results/heuristic-a-decision.md`) explicitly cited F-2 misinformation (GUIDE-threat-coverage-research §11 Worked Example 4) as a distinguishing case when preserving the signal-class discipline. F-2 therefore does **not** re-adjudicate Heuristic A — it inherits the resolution already recorded in ADR-030 and operationalizes it for LLM09:2025. This distinction matters for provenance: the three-way partition is authoritative because ADR-030 set it, not because F-2 claimed it.

**Rationale — disjointness is verifiable at three levels**: the T004 architect memo documents three orthogonal disjointness checks that confirm no subsume-into-output-integrity signal has emerged: (a) **detection vocabulary disjointness** — `output-integrity` trigger-keyword set interrogates sink presence (`renderer`, `innerHTML`, `SQL`, `shell`, `template`, `path` — byte/syntax signals); `misinformation` trigger-keyword set (Decision 4 below) interrogates factual-output emission (`citation`, `recommendation`, `advisory`, `grounding`, `RAG`, `hallucination`) and high-stakes domain signals (`medical`, `legal`, `financial`, `clinical` — content-semantic signals); no keyword overlap; (b) **CWE mapping disjointness** — `output-integrity` cites CWE-22/78/79/89/94/918 (encoding/sanitization weaknesses); `misinformation` cites CWE-345 + CWE-223 (data-authenticity / security-relevant-information omission weaknesses); no CWE overlap; (c) **mitigation taxonomy disjointness** — `output-integrity` mitigations name encoding libraries, parameterized queries, URL allowlists; `misinformation` mitigations name RAG grounding, citation verification, HITL gates, confidence calibration; no mitigation vocabulary overlap. An architecture that exercises all three surfaces on the same LLM Process correctly produces three adjacent findings (`LLM-{N}`, `OI-{N}`, `MI-{N}`) — this is **disjoint coverage, not duplication**; SC-014 verifies the three-signal-class discipline on the regenerated example in Wave 4.

**Forward scope marker**: the `trust-exploitation` agent (F-4, forward-referenced by ADR-030 Decision 2 Outcome B) owns a fourth distinct signal class (psychology/linguistics primitives for human-victim output — authority claims, urgency framing, false reassurance, mimicry of trusted roles — ASI09:2026). F-2 `misinformation` and F-4 `trust-exploitation` are sibling human-victim agents but operate on different primitive types (factual-content vs linguistic-stylistic); they do not subsume one another. The agent's `## Purpose` section forward-references `prompt-injection` and `output-integrity` as adjacent-but-distinct concerns per FR-008.

### Decision 3 — Lean-agent shape conformance per ADR-023 detection variant

The `misinformation` agent file strictly conforms to the ADR-023 lean-agent detection variant established in Feature 082 for the 11 original detection-tier agents and extended by F-1 for `output-integrity`. Specifically:

- **Single-point load**: exactly one `**MANDATORY**: Read` directive under `## Detection Workflow` section start. No phase-gated loads (unlike the ADR-023 methodology variant used by control-analyzer).
- **Line count discipline**: ≤150 lines soft target (AI tier cap per ADR-023), ≤180 lines hard ceiling. The target applies to the agent file only; companion skill files are not bound by the cap.
- **Zero MAESTRO references**: grep-auditable invariant per spec FR-010. MAESTRO layer classification is orchestrator-owned per Feature 084 / ADR-020; `misinformation` does not author its own layer field.
- **No `agentic_pattern` in metadata**: pattern classification is orchestrator Phase 3.6-owned per Feature 142 / ADR-026. Per spec FR-016, `misinformation` does NOT assign `agentic_pattern` on emitted findings — the orchestrator assigns `none` via default for single-agent factual-output surfaces, or `multi-agent` if the factual-output emission arises from an agentic pattern orchestration.
- **Canonical 5-section shape**: YAML frontmatter (name, description, tools, model) → metadata YAML block (category, threat_class, dfd_targets, owasp_references, output_schema) → `## Purpose` → `## Skill References` table → `## Detection Workflow`. Optional `## Example Findings` section permitted (2-3 worked examples typical for AI-tier agents).
- **Two-part emission gate step explicit in Detection Workflow**: per FR-011, the workflow step enumerates the two-part gate (LLM keyword match AND factual-output indicator) as a correctness BLOCKER — keyword match alone MUST NOT emit. This is the same zero-speculation discipline F-1 inherited from the 11 original detection agents and formalized in its US1 Acceptance Scenario 4.

ADR-023 Decision 3's `## `-heading byte-identity enforcement on shared-reference edits applies at Wave 3 T028: the `finding-format-shared.md` `consumers:` frontmatter list extension is additive-only; zero edits to any body `## ` heading. F-1 already validated this invariant on the same file at Feature 201; F-2 is the second additive consumer-list extension post-F-1.

### Decision 4 — Pattern category scope: 5 categories per Q1 PRD decision

The companion `detection-patterns.md` ships with exactly **5 pattern categories** per the PRD Q1 architect decision (PM leaning confirmed at plan time):

1. **Ungrounded Factual Emission** — primary OWASP LLM09:2025, related CWE-345. Indicators: LLM-backed summarizer or analyst emits factual claims, citations, or domain-specific assertions without RAG, retrieval-strength declaration, or confidence-calibration layer.
2. **Citation Fabrication** — primary OWASP LLM09:2025, related CWE-345. Indicators: RAG pipeline present, but emitted citations are not verified against retrieved source URIs; decoder produces plausible-looking citations that do not resolve.
3. **Overreliance / Missing HITL on Decision-Critical Output** — primary OWASP LLM09:2025, related CWE-223 + optional CWE-345. Indicators: LLM output drives automated approve/deny, triage/classify, or content-moderation ruling without human-in-the-loop review gate or risk-threshold escalation; consumer-facing high-stakes (HIGH/CRITICAL) distinguished from internal low-stakes (MEDIUM or below) via OWASP 3×3.
4. **Retrieval-Grounding Gaps** — primary OWASP LLM09:2025, related CWE-345. Indicators: RAG declared but retrieval-strength metric (hit-rate, recall@k) absent; retrieval corpus not versioned or lacks staleness policy; per-query retrieval-score threshold absent.
5. **Confidence-Calibration Absence** — primary OWASP LLM09:2025, related CWE-345. Indicators: LLM output emitted without calibration layer (temperature scaling + ECE monitor); no refusal pattern for low-confidence queries; calibrated-confidence not exposed on output.

Each category MUST include 3-6 indicators, ≥1 anti-indicator (per architect MEDIUM-5 discipline — a structural feature whose presence MUST NOT trigger the pattern), ≥1 worked example with clearly-fictional framing per NFR-6 (hypothetical clinical-decision-support / generic legal-research / synthetic financial-advisory — no real institutional names, no real clinician/lawyer/advisor identities), primary/related citations, trigger keywords, and applicable DFD element types.

**Q1 deferred candidates**: two candidates surfaced at PRD time — "Model-Specific Hallucination Patterns" and "Feedback-Loop Overreliance" — are deliberately **not** included in F-2's 5-category ship. "Model-Specific" introduces model-family coupling that ages poorly as foundation models iterate; its detection signal is better expressed as a catalog enrichment in follow-on F-2.1 scope. "Feedback-Loop" overlaps with F-3 ASI07 inter-agent communication scope; forcing it into F-2 would violate the Heuristic A signal-class discipline by mixing factual-integrity primitives with inter-agent-coordination primitives. Both deferred candidates are explicitly out-of-scope per spec Out-of-Scope items 8 and 9.

### Decision 5 — 24-file zero-edit invariant preserved with grep-auditable enumeration

F-2 preserves the ADR-023 24-file zero-edit invariant as extended by F-1 at Feature 201 merge (ADR-030 Decision 5). The 24 frozen files, enumerated for grep audit per spec SC-009 and quickstart.md Step 7:

**6 STRIDE agent files**:

```
.claude/agents/tachi/stride/spoofing.md
.claude/agents/tachi/stride/tampering.md
.claude/agents/tachi/stride/repudiation.md
.claude/agents/tachi/stride/info-disclosure.md
.claude/agents/tachi/stride/denial-of-service.md
.claude/agents/tachi/stride/privilege-escalation.md
```

**6 AI agent files** (5 original + F-1's `output-integrity.md`):

```
.claude/agents/tachi/ai/prompt-injection.md
.claude/agents/tachi/ai/data-poisoning.md
.claude/agents/tachi/ai/model-theft.md
.claude/agents/tachi/ai/agent-autonomy.md
.claude/agents/tachi/ai/tool-abuse.md
.claude/agents/tachi/output-integrity.md
```

**12 companion `detection-patterns.md` files** (11 original + F-1's `tachi-output-integrity/`):

```
.claude/skills/tachi-spoofing/references/detection-patterns.md
.claude/skills/tachi-tampering/references/detection-patterns.md
.claude/skills/tachi-repudiation/references/detection-patterns.md
.claude/skills/tachi-info-disclosure/references/detection-patterns.md
.claude/skills/tachi-denial-of-service/references/detection-patterns.md
.claude/skills/tachi-privilege-escalation/references/detection-patterns.md
.claude/skills/tachi-prompt-injection/references/detection-patterns.md
.claude/skills/tachi-data-poisoning/references/detection-patterns.md
.claude/skills/tachi-model-theft/references/detection-patterns.md
.claude/skills/tachi-tool-abuse/references/detection-patterns.md
.claude/skills/tachi-agent-autonomy/references/detection-patterns.md
.claude/skills/tachi-output-integrity/references/detection-patterns.md
```

The T050 pre-merge grep audit (`git diff main --stat` on these 24 paths) MUST return zero lines. Orchestrator-tier edits (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`) and shared-reference edits (`.claude/skills/tachi-shared/references/finding-format-shared.md`) are carved out as additive-only per ADR-023 Decision 3 and are NOT part of the 24-file invariant scope. The orchestrator-tier edits include **5 F-1 carry-over reconciliation callsites** (architect-owned per MEDIUM-4) — orchestrator.md:296, orchestrator.md:370, dispatch-rules.md LLM-list, dispatch-rules.md:120, and dispatch-rules.md trigger-keyword rules section — all extending the post-F-1 quartet to the full five-agent quintet (`prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`) in a single edit.

### Decision 6 — Proposed → Accepted dual-commit governance protocol

ADR-031 follows the Proposed → Accepted dual-commit pattern established in ADR-027 Decision 8, ADR-028 Decision 7, ADR-029's Governance Protocol, and ADR-030 Decision 6. Lifecycle:

1. **Day 1 Wave 1.1 (Proposed commit)**: This ADR commits with `Status: Proposed` after the architect Heuristic A verification at T004 and the schema lock at T006. The Proposed commit is the schema-lock signal that unblocks parallel Wave 2 authoring of the pattern catalog, the agent file, and the mitigation text. All 9 decisions land at Proposed time — no decision is deferred to Accepted.
2. **Day 2 Wave 5 (Accepted transition, pre-PR)**: At T022, this ADR transitions from `Status: Proposed` to `Status: Accepted` with a provisional Accepted-date recorded in Revision History. Wave 4 regeneration completion (T037) plus Wave 5 SC sweep (T042-T054) are the pre-conditions; the ADR Accepted commit is atomic with the provisional PR row in Revision History.
3. **Post-merge (SHA fill)**: At T025, after PR squash-merge to `main`, a new Revision History row records "Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed". The provisional Accepted-date is preserved (not retconned to the UTC merge date) per ADR-027 T039 / ADR-028 T036 / ADR-029 T044 / ADR-030 post-merge-fill guidance.

Rationale: the dual-commit pattern lets architectural decisions reach Proposed status early (unblocking parallel work) without committing to an Accepted seal before the feature's implementation waves verify the decisions hold. The SHA fill is the last post-merge bookkeeping step and serves as the ADR's provenance anchor. F-2 is the fifth consecutive BLP-01 ADR using this protocol (ADR-027 F-A1, ADR-028 F-A2, ADR-029 F-B, ADR-030 F-1, ADR-031 F-2).

### Decision 7 — Post-merge SHA fill recording squash commit

At T025 (post-merge), the ADR Revision History table gains a new row recording the PR squash-merge commit short SHA. The row format mirrors the ADR-027/028/029/030 post-merge convention exactly:

```
| YYYY-MM-DD | Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed |
```

The `YYYY-MM-DD` date is the actual UTC merge date (recorded from `gh pr view --json mergedAt`). The `{SHORT_SHA}` is the first 12 characters of the squash-merge commit SHA (recorded from `gh pr view --json mergeCommit.oid`). The provisional Accepted-date from the T022 Wave 5 transition row is NOT retroactively corrected — the provisional date reflects the Wave 5 authoring-time projection, and the paired SHA-fill row satisfies the "provisional date AND SHA-fill post-merge" pattern; correcting the date would retcon the Wave 5 transition record without adding provenance value beyond what the new SHA row provides (per ADR-027 T039 / ADR-028 T036 / ADR-029 T044 / ADR-030 post-merge precedent).

### Decision 8 — Schema bump 1.6 → 1.7 as 2nd recorded application of ADR-030 Decision 8

**F-2 is the second recorded application of the ADR-030 Decision 8 regex-alternation minor-bump rule.** The first application was F-1's `schemas/finding.yaml` 1.5 → 1.6 bump that added the `OI` prefix to the `id.pattern` regex alternation. F-2 invokes the identical rule for the `MI` prefix addition at 1.6 → 1.7:

```yaml
# Pre-1.7 (post-F-1 state)
id:
  pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"

# Post-1.7
id:
  pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"
```

The three additive-compatibility conditions from ADR-026 (originally for enum-typed scalar fields, extended by ADR-028 Decision 1 to list-of-RECORD fields, extended by ADR-030 Decision 8 to regex-alternation prefix additions) hold identically for F-2's `MI` addition:

| ADR-026 Condition (as extended by ADR-030 Decision 8) | How Decision 8 of ADR-031 Satisfies It |
|-------------------|------------------------------|
| (a) Additive | All 10 pre-existing regex alternation values (`S`, `T`, `R`, `I`, `D`, `E`, `AG`, `LLM`, `AGP`, `OI`) remain valid. `MI` is appended as the 11th alternation value. No removal, rename, or re-typing of any existing prefix. |
| (b) Has default (regex-field equivalent — acceptance-domain expansion) | The `id` field is a REQUIRED string field (no default) but its acceptance domain EXPANDS rather than narrowing. A parser reading a post-1.7 finding against a pre-1.7 regex would fail on `MI-{N}` IDs but still succeed on the 10 pre-existing prefixes. All pre-1.7 valid IDs remain valid in 1.7. |
| (c) Schema shape unchanged | Top-level `finding:` mapping remains a single-key document. No new field is added, removed, or re-typed. The `id` field's shape (string with pattern) is unchanged; only the pattern's internal acceptance domain expands. |

**Explicit cross-reference to ADR-030 Decision 8**: this ADR-031 Decision 8 does **not** extend the ADR-030 rule or modify its scope — it is a **pure second application** of the rule within the same scope boundary ADR-030 Decision 8 authorized. Future threat-agent family introductions (F-3 `tool-abuse` enrichment, F-4 `trust-exploitation`, F-5 `denial-of-service` + `model-theft` enrichment per BLP-01 §8) that need their own ID prefix MAY cite ADR-030 Decision 8 (via this ADR-031's 2nd-application precedent) to invoke the minor-bump rule identically. The rule's scope boundary is preserved: **Decision 8 does NOT authorize regex-pattern rewrites that REMOVE or RENAME existing alternation values, or that narrow the acceptance domain in any way**. Those remain major-bump changes regardless of the alternation-addition precedent.

**Precedent chain for future readers**: ADR-026 (Feature 142) established the minor-bump rule for enum-typed scalar field additions; ADR-028 (Feature 189) extended it to list-of-RECORD fields under the Complex-Shape Clarifier; ADR-030 Decision 8 (Feature 201) extended it to regex-alternation prefix additions; ADR-031 Decision 8 (this feature) records the **second application** of that rule without further extension. The three-step extension sequence (scalar → list-of-record → regex-alternation) is now considered closed — any further extension to a new typing surface requires explicit future-ADR authorship.

### Decision 9 — CWE-1039 deliberate exclusion per architect MEDIUM-3

CWE-1039 (Automated Recognition Mechanism with Inadequate Detection or Handling of Adversarial Input Perturbations — "model evasion" / "automated recognition adversarial input") is **deliberately excluded** from F-2's pattern catalog and from the `source_attribution` citation list for every emitted `MI-{N}` finding.

**Rationale — CWE-1039 is a model-robustness primitive, not a factual-content primitive**: CWE-1039 describes weaknesses in automated recognition systems (image classifiers, speech recognizers, content filters, biometric verifiers) where an attacker crafts adversarial input perturbations that cause the model to misclassify. The victim model is **machine-victim under adversarial input** (the classifier is deceived by adversarial example), and the primitive type is **model-robustness** (how the model responds to perturbed input). This is structurally distinct from F-2's scope, which covers **human-victim and decision-cascade-victim under ungrounded output** (the human or downstream automated decision is deceived by factually-wrong LLM output) and operates on **factual-content primitives** (architecture-level absence of grounding/verification/HITL/calibration).

**Why the distinction matters — Heuristic A signal-class discipline**: allowing CWE-1039 into F-2's pattern catalog would mix model-robustness primitives with factual-content primitives in a single agent's detection vocabulary. This mirrors the ADR-030 Decision 2 Outcome A rejection reasoning at F-1: mixing disjoint primitive types within one agent degrades the quality of both halves, forces the trigger-keyword set to span two disjoint semantic spaces, and sets a dangerous precedent that subsequent BLP-01 features could subsume arbitrary CWE coverage into the nearest existing AI-tier agent. The architect MEDIUM-3 ruling at PRD review explicitly named CWE-1039 as the test case for preserving Heuristic A scope discipline in F-2.

**What CWE-1039 coverage would look like if scoped**: adversarial-perturbation detection would belong in a distinct future agent concerned with **adversarial-ML robustness** (MITRE ATLAS AML.TA0005 Evasion Attacks tactic — techniques AML.T0015 Evasion Attacks, AML.T0019 Publish Poisoned Datasets, AML.T0043 Craft Adversarial Data, etc.). That agent would have its own CWE mapping centered on CWE-1039 and adjacent adversarial-ML weaknesses, its own trigger-keyword set interrogating ML-pipeline indicators (training data provenance, input-validation layers on model endpoints, adversarial-example detection mechanisms), and its own mitigation taxonomy (adversarial training, input perturbation detection, certified robustness bounds). No such agent is in the BLP-01 roadmap today; if one is proposed in the future, it would be a sibling to F-2 with a distinct ID prefix (e.g., `AR-{N}` for "adversarial robustness") and a distinct companion skill catalog, not an extension of F-2's scope.

**Enforcement**: pattern catalog prose at `.claude/skills/tachi-misinformation/references/detection-patterns.md` MUST NOT cite CWE-1039 in any pattern category's primary or related citation fields. Worked examples MUST NOT frame adversarial-perturbation scenarios as misinformation findings. Agent `## Purpose` prose MUST NOT claim coverage of adversarial-ML robustness or evasion-attack detection. The F-A2 referential-integrity validator enforces positive citations (what MAY appear in `source_attribution`); Decision 9 enforces the negative citation (what MUST NOT appear) at authoring-time via senior-backend-engineer + code-reviewer double-check at Wave 2.2 PM (T055).

---

## Alternatives Considered

### Alternative 1 — Subsume factual-integrity into `output-integrity` (collapse F-2 into F-1)

Add 5 new pattern categories to F-1's companion skill covering factual-integrity signals, forgo the `misinformation` agent entirely, and widen `output-integrity`'s scope to cover both downstream-execution-sanitization AND factual-integrity.

**Why Not Chosen**: directly violates ADR-030 Decision 1's scope bounds, which explicitly restricted F-1 to downstream-execution-sanitization and left factual-integrity open for F-2. ADR-030 Decision 2 Outcome B rationale cited F-2 misinformation as the distinguishing case when preserving signal-class discipline. Subsuming would force `output-integrity`'s trigger-keyword set to span byte/syntax signals AND factual-content signals — two disjoint semantic spaces — degrading the quality of both halves. The three-check disjointness verification in Decision 2 above (vocabulary, CWE mapping, mitigation taxonomy) makes the subsume option structurally unsound.

### Alternative 2 — Defer LLM09 coverage to a post-Tier-1 feature

Ship F-2 with a narrower scope covering only 2-3 highest-priority patterns (e.g., only Ungrounded Factual Emission + Overreliance) and defer the remaining patterns to F-2.1 or a post-BLP-01-Tier-1 feature.

**Why Not Chosen**: LLM09:2025 is a top-10 OWASP risk for 2025; shipping partial coverage would leave the Coverage Matrix in a Planned-with-partial-F-2 state that is harder to reason about than Planned. The 5-category scope is bounded and well-documented in the OWASP LLM09:2025 reference; authoring all 5 categories costs ~0.5 day more than authoring 2-3 (the marginal cost is trigger-keyword and worked-example authoring, not new architectural scope). Deferring creates two follow-on features (F-2.1 + the deferred patterns) rather than one, doubling governance overhead.

### Alternative 3 — New category enum value `misinformation` or `factual-integrity`

Introduce a new top-level category value distinct from `llm` for `MI-{N}` findings, enabling downstream aggregators to discriminate purely on category.

**Why Not Chosen**: detailed in ADR-030 Decision 7 rationale (inherited verbatim here). Adding a new category value forces edits to the downstream infrastructure tier (`risk-scorer`, `control-analyzer`, `threat-report`, `threat-infographic`, `report-assembler`) to handle the new value — violating spec FR-014. The ID-prefix distinction + `source_attribution` semantic filter accomplishes the same discrimination without touching the infrastructure tier. F-2 reuses `category: llm` identically to F-1's Decision 7 precedent; the `llm` category is now the producer for three ID-prefix families (`LLM-{N}`, `OI-{N}`, `MI-{N}`) — a meaningful demonstration that the prefix-plus-category pattern scales without category-enum inflation (SC per FR-019).

### Alternative 4 — Inline pattern catalog in agent file (no companion skill)

Author the 5 pattern categories directly inside `misinformation.md` rather than externalizing them to a companion `detection-patterns.md`.

**Why Not Chosen**: violates the ADR-023 lean-agent shape. F-1 followed the lean + skill-references pattern at Feature 201 with 120 lines in the agent file and a ~250-line companion catalog; F-2 matches for pattern-continuity. Inlining would push `misinformation.md` above the 150-line soft target (5 pattern categories each with 3-6 indicators, anti-indicators per MEDIUM-5, worked examples with clearly-fictional framing per NFR-6 would consume 250+ lines). The lean + skill-references pattern is the tachi standard; F-2 conforms.

### Alternative 5 — Extend F-1 `output-integrity`'s schema 1.6 regex to include `MI` prefix (no schema bump)

Piggyback on F-1's schema 1.6 bump by extending the regex at F-2 merge time without incrementing the schema version — argue that regex alternation additions do not require version bumps at all.

**Why Not Chosen**: violates ADR-026 + ADR-030 Decision 8 minor-bump discipline. The schema_version field's purpose is to signal acceptance-domain changes to downstream parsers; extending the regex without bumping would silently change the acceptance domain in a version that was previously locked at 1.6 with a specific regex. Parsers pinned at 1.6 would fail on `MI-{N}` IDs without warning, because the 1.6 contract did not include `MI`. The minor-bump discipline (1.6 → 1.7) is the explicit signal that acceptance domain expanded. This alternative was rejected at PRD time on the grounds that schema versioning is cheap; silent expansion is expensive.

---

## Consequences

### Positive

- **LLM09:2025 factual-integrity threat surface closed**. F-2 ships the first detection-tier coverage of OWASP LLM09:2025, completing the LLM-tier threat-surface coverage for BLP-01 Tier 1: input-side via 5 original agents, output-sanitization via F-1, factual-integrity via F-2. The 5 pattern categories cover the full LLM09 sub-class taxonomy (factual-emission, citation-integrity, decision-overreliance + two architectural-grounding primitives).
- **Heuristic A three-way signal-class discipline validated via a second independent feature**. F-1's ADR-030 Decision 1 stated the three-way partition as a carve-out; F-2 operationalizes it with a second distinct agent. The three-level disjointness verification (vocabulary, CWE, mitigation) in Decision 2 makes the partition auditable rather than claimed.
- **F-A2 contract proven end-to-end against a second real producer**. F-1 was the first net-new `source_attribution` producer; F-2 is the second. If the F-A2 referential-integrity validator works correctly on `MI-{N}` findings (every LLM09 primary + CWE-345/CWE-223 related citation resolves against F-A1 catalogs), the F-A2 contract is proven against two independent detection-tier populators — meaningful evidence that the Foundation tier generalizes.
- **F-B coverage-attestation surface gains its second TRUE trigger on regenerated `agentic-app`**. Post-F-1, `has-source-attribution: true` fires on `agentic-app` for `OI-{N}` findings. Post-F-2 regen, the same boolean fires again for the combined `OI-{N}` + `MI-{N}` emission, and the F-B coverage-attestation section renders per-framework coverage against OWASP (LLM05 + LLM09 both Covered) and CWE (CWE-22/78/79/89/94/918 from F-1 + CWE-345/CWE-223 from F-2). The 5 non-factual baselines still emit `has-source-attribution: false` (byte-identity preserved).
- **ADR-023 lean-agent pattern scales to 7 AI-tier agents**. F-2 is the second net-new addition to the AI tier since Feature 082 stabilized the 5 original agents under ADR-023. Conformance to the detection variant (single-point load, ≤150 lines, zero MAESTRO) is grep-auditable; the template scales cleanly to a 7th member.
- **ADR-030 Decision 8 regex-alternation rule validated as a durable precedent via 2nd application**. Decision 8 above applies the ADR-030 rule identically to a second threat-agent family. Future BLP-01 Tier 1 features (F-3, F-4, F-5) that need their own ID prefix can cite the 2nd-application precedent in addition to the ADR-030 1st-application precedent. The rule is stable; the scope boundary (no removal, rename, or acceptance-domain narrowing) holds.
- **Zero regression on the 24-file detection tier**. ADR-023 stabilization + F-1 extension both hold. The 12 frozen detection-tier agent files and the 12 frozen companion skill-reference files are byte-identical at F-2 merge. F-2 is a net-new addition, not a refactor.
- **SC-006 byte-identity preserved by construction**. The 5 non-factual baselines do not qualify for the `misinformation` trigger (no factual-output indicators in their DFDs, verified by T012 pre-check). The two-part emission gate (FR-011) guarantees zero findings on non-qualifying architectures. The 5 baselines regenerate byte-identically.
- **Zero new runtime or developer dependencies**. Empty diffs on all dependency manifests. `pyyaml` and `pytest` remain developer-only. Consistent with Features 128 / 180 / 189 / 194 / 201.
- **Determinism preserved**. No new orchestrator phase, no new LLM-judgment step, no new HTTP fetch. The agent's pattern matching is a pure function of the architecture input + the companion `detection-patterns.md` rules. ADR-021 byte-identity harness consumes no new knobs.
- **CWE-1039 deliberate exclusion preserves Heuristic A scope discipline forward-compatibly**. Decision 9 documents the model-robustness vs factual-content primitive distinction and names where CWE-1039 coverage would belong (future adversarial-robustness agent with AR-{N} prefix) if scoped. This forestalls the scope-creep risk of adversarial-ML coverage leaking into F-2 during Wave 2 authoring.

### Negative / risks

- **F-A1 catalog gap for AML.T0042 Verify Attack** → pattern-catalog prose-only citation. The MITRE ATLAS `AML.T0042` technique is semantically relevant to F-2's citation-fabrication category but is CONFIRMED ABSENT from `schemas/taxonomy/mitre-atlas.yaml` at PRD time (architect-verified; catalog carries 12 AML techniques, T0042 not among them). Mitigation: retain prose-only citation in pattern catalog's Primary Sources list; `source_attribution` anchors on LLM09 + CWE-345 + CWE-223 only; F-A2 referential-integrity validator rejects any AML.T0042 entry (validated at Wave 4 T038). If a future catalog-enrichment feature populates AML.T0042, the pattern-catalog citation upgrades from prose-only to `source_attribution` entry as a separate additive change.
- **NIST AI 600-1 §2.4 Hallucination section-level ID not catalogued** → same prose-only pattern as AML.T0042. Section-level IDs are not currently populated in `schemas/taxonomy/nist-ai-rmf.yaml`. Mitigation: prose-only citation in pattern catalog; `source_attribution` does not cite NIST section-level IDs until a future catalog-population feature lands.
- **Pattern category list bounded at 5 per Q1; catalog enrichment follow-ons deferred**. "Model-Specific Hallucination Patterns" (Q1 candidate A) deferred to F-2.1; "Feedback-Loop Overreliance" (Q1 candidate B) deferred to F-3 ASI07 scope. Adopters whose architectures exercise these patterns specifically will see Gap classifications on LLM09 items they consider applicable. Mitigated by (a) Decision 4 explicit scope rationale documenting the deferrals, (b) the two deferred patterns are not OWASP-named sub-classes of LLM09:2025 (they are pattern-catalog enrichments), and (c) adopter demand for either pattern triggers a follow-on feature rather than an F-2 scope expansion.
- **Regeneration target extension on `agentic-app` carries cumulative-state risk**. F-1 regenerated `agentic-app` on 2026-04-19; F-2 extends the same architecture with a factual-output sub-component. If Wave 4 regeneration surfaces friction (e.g., extended baseline produces byte-identity failure on other SC-006 baselines due to subtle dispatch reordering), Q4 fallback to new `advisory-app` consumes 0.5 day of buffer capacity per PRD R2. Mitigated by Wave 3 EOD T031 decision-gate review and explicit buffer-day allocation per PRD HIGH-1 budget model.

### Neutral

- **New `MI-{N}` finding prefix adds 1 category to the existing taxonomy** (ID prefix alternation values now total 11: `S|T|R|I|D|E|AG|LLM|AGP|OI|MI`). No new `category` enum value — `category: llm` is now the producer for three ID-prefix families per Decision 1.
- **Schema 1.7 is backward-compatible with 1.6 (strict regex extension)** per Decision 8. Future threat-agent family additions (F-3, F-4, F-5) that need their own prefix follow the same minor-bump path; each bump is an additive alternation step (1.7 → 1.8 → 1.9 → ...) without acceptance-domain narrowing.
- **F-2 ships solo in the 2026-04-27 → 2026-04-29 window** per team-lead PRD-time backlog verification (no F-3/F-4/F-5 at stage:define or later, no competing PRs). If the calendar shifts and F-3 or F-5 enter build concurrently, team-lead enforces serialization on the 4 additive-edit surfaces (schema bump, dispatch-rules, finding-format-shared, orchestrator dispatch) per PRD R8.
- **MAESTRO Layer 5 inheritance** per ADR-020 lineage. `MI-{N}` findings will inherit L5 Evaluation and Observability layer via orchestrator Phase 1 keyword classification. The agent does not author its own layer field; this is correct per ADR-020 Decision and ADR-023 Decision 2.
- **Forward-compatibility for F-4 `trust-exploitation`**. F-4 will be a separate AI-tier agent with its own `TE-{N}` or similarly-prefixed ID (requiring a third Decision-8-style regex alternation addition — the 3rd application of the ADR-030 Decision 8 rule) and its own companion skill. F-2 does not pre-design F-4 beyond the `## Purpose` forward-reference establishing the human-victim signal class partition between factual-content primitives (F-2 scope) and psychology/linguistics primitives (F-4 scope).

---

## Cross-References

- **ADR-021**: Determinism baseline (SOURCE_DATE_EPOCH). F-2's Wave 4 regeneration gate (T039) uses `SOURCE_DATE_EPOCH=1700000000` to verify 5-baseline byte-identity. The agent's pattern matching is deterministic (pure function of architecture input + pattern catalog); no new determinism knobs introduced.
- **ADR-023**: Lean-agent pattern (≤150 lines, single MANDATORY Read, zero MAESTRO) + 22-file zero-edit invariant. F-2 is the second net-new AI-tier agent since Feature 082 stabilized the pattern (F-1 was first). Decision 3 confirms conformance; Decision 5 confirms the 24-file invariant preservation (22 original + F-1's 2). ADR-023 Decision 3's `## `-heading byte-identity enforcement applies at Wave 3 T028 on the `finding-format-shared.md` additive edit.
- **ADR-026**: Pattern classification mechanism; minor-bump rule origin (extended by ADR-030 Decision 8 to regex-alternation prefix additions). F-2's Decision 8 is the 2nd application of the regex-alternation extension — no further extension, pure precedent application.
- **ADR-027**: F-A1 taxonomy enum source (`schemas/taxonomy/owasp.yaml`, `cwe.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`). F-2's `source_attribution` citations resolve against OWASP (LLM09) and CWE (CWE-345, CWE-223). F-2 is read-only against the F-A1 catalog; no edits to `schemas/taxonomy/`. ADR-027 Decision 3's 7-value taxonomy enum and Decision 5's closed-domain constraint both apply to F-2's attribution emissions.
- **ADR-028**: F-A2 `source_attribution` contract — F-2 is the **second net-new producer** of `source_attribution` data after F-1. Every `MI-{N}` finding carries `{taxonomy: owasp, id: LLM09, relationship: primary}` plus ≥1 `{taxonomy: cwe, id: CWE-345 or CWE-223, relationship: related}` entry. F-A2's referential-integrity validator at `scripts/tachi_parsers.py:826` enforces the contract on every emission.
- **ADR-029**: F-B coverage-attestation report section — F-B is the downstream consumer. F-2's regenerated `agentic-app` trips `has-source-attribution: true` (already true post-F-1; F-2 adds `MI-{N}` findings on top of existing `OI-{N}` + `LLM-{N}` baseline). The F-B conditional Section 9 rendering now aggregates coverage across OWASP (LLM01 + LLM05 + LLM09) and CWE (F-1's CWE-22/78/79/89/94/918 + F-2's CWE-345/CWE-223). F-2 does not edit F-B's renderer logic; the coverage expansion is a downstream consequence of F-2's detection-tier emission.
- **ADR-030**: F-1 precedent — **Decision 1 scope bounds** (F-1 limited to downstream-execution-sanitization, leaving factual-integrity open for F-2; F-2 inherits this carve-out per this ADR's Decision 2); **Decision 8 regex-alternation minor-bump rule** (ADR-030 established the rule with F-1's 1.5 → 1.6 bump as the first application; F-2 invokes the same rule as the 2nd application at 1.6 → 1.7 per this ADR's Decision 8).

---

## References

- Spec: [`specs/206-misinformation-threat-agent/spec.md`](../../../specs/206-misinformation-threat-agent/spec.md) — 3 user stories (US-206-1/2/3), 19 FRs, 14 SCs
- Plan: [`specs/206-misinformation-threat-agent/plan.md`](../../../specs/206-misinformation-threat-agent/plan.md) — 6-wave structure, Q1-Q5 architect decisions resolved, 5-callsite F-1 carry-over reconciliation
- Tasks: [`specs/206-misinformation-threat-agent/tasks.md`](../../../specs/206-misinformation-threat-agent/tasks.md) — 62 tasks across 10 phases, triple sign-off APPROVED
- Heuristic A verification memo: [`.aod/results/heuristic-a-verification.md`](../../../.aod/results/heuristic-a-verification.md) — architect T004 ruling for three-way signal-class inheritance from ADR-030 Decision 1
- PRD: [`docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md`](../../product/02_PRD/206-misinformation-threat-agent-2026-04-23.md)
- Schema: [`schemas/finding.yaml`](../../../schemas/finding.yaml) — 1.6 → 1.7 bump per Decision 8
- F-A1 catalog YAMLs: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml) (LLM09 entry), [`schemas/taxonomy/cwe.yaml`](../../../schemas/taxonomy/cwe.yaml) (CWE-345, CWE-223 entries) — read-only source for `source_attribution` resolution; `schemas/taxonomy/mitre-atlas.yaml` has AML.T0042 CONFIRMED ABSENT → prose-only citation in pattern catalog
- F-A2 parser + validator: [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) — `parse_threats_findings` + `validate_source_attribution` (unchanged; regex-agnostic — accepts any prefix matching `id.pattern`)
- Feature 082 (ADR-023 lean-agent stabilization): [`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`](ADR-023-threat-agent-skill-references-pattern.md)
- Feature 189 (F-A2 direct precedent): [`docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`](ADR-028-source-attribution-schema-extension.md)
- Feature 194 (F-B direct precedent): [`docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`](ADR-029-coverage-attestation-report-section.md)
- Feature 201 (F-1 direct precedent — F-2 mirrors F-1's ADR template and agent shape): [`docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`](ADR-030-output-integrity-agent.md)
- BLP-01 Tier 1 F-2 framing: `_internal/strategy/BLP-01.md` §8 (F-2 misinformation placement; F-3/F-4/F-5 forward references), §4 (documentation-only framework bundling pattern applies to AML.T0042 prose-only citation)
- GUIDE-threat-coverage-research §11 — Heuristic A signal-class distinction (input-side attacker-injection / downstream-execution-sanitization / factual-integrity / psychology-linguistics — Worked Example 4 distinguishes F-2 from F-1)

---

## Revision History

| Date | Status | SHA | Author | Note |
|------|--------|-----|--------|------|
| 2026-04-23 | Proposed | b916a23 | architect (Feature 206) | Initial proposal — Wave 1.1 schema-lock commit. Records 9 numbered decisions covering the new AI-tier agent adoption for LLM09:2025 closure (D1), Heuristic A three-way scope inheritance from ADR-030 Decision 1 with disjointness verification at vocabulary/CWE/mitigation levels (D2), lean-agent shape conformance per ADR-023 detection variant (D3), 5-category pattern scope with Q1 deferrals (D4), 24-file zero-edit invariant preservation with grep-auditable enumeration (22 original + F-1's 2) (D5), Proposed → Accepted dual-commit governance per ADR-027/028/029/030 precedent (D6), post-merge SHA fill recording squash commit (D7), schema bump 1.6 → 1.7 as 2nd recorded application of ADR-030 Decision 8 regex-alternation minor-bump rule (D8), and CWE-1039 deliberate exclusion per architect MEDIUM-3 scope-discipline ruling (D9). Heuristic A inheritance verified by architect at T004 (`.aod/results/heuristic-a-verification.md`); ADR-030 Decision 1 + Decision 8 cross-references explicit at Decisions 2 and 8. Authored at Day 1 Wave 1.1 after T004 Heuristic A verification and T006 schema bump; serves as the schema-lock signal that unblocks parallel Wave 2 authoring of the pattern catalog, agent file, and mitigation text. Status transitions to Accepted at Wave 5 T022 per Decision 6; post-merge SHA fill at T025 per Decision 7. |
| 2026-04-24 | Proposed → Accepted | PR #207 pending merge | provisional (architect, Feature 206) | Wave 5 T022 transition. Pre-conditions satisfied: Wave 4 regeneration pipeline complete (T032–T037 green on `examples/agentic-app/` with 3 `MI-{N}` findings surfaced at commit `ec76c00`); backward-compat byte-identity pass on 5 non-factual baselines (T039, 6/6 including `agentic-app` post-F-1 baseline); F-A2 referential-integrity validation green (T038 / 19/19 misinformation tests); three-signal-class discipline verified (T040 artifact at `.aod/results/wave4-three-signal-class-check.md`); companion pattern catalog + agent file structural compliance (Wave 2 gates T018/T021); orchestrator registration + 5-callsite quintet reconciliation (Wave 3 gates T026/T027/T030). Provisional Accepted-date per Decision 6 dual-commit protocol — post-merge T025 SHA fill row will record the squash-merge commit SHA; the provisional date is preserved (not retconned) per ADR-027/028/029/030 precedent. SC sweep T042–T054 in progress concurrent with this transition; NFR-6 compliance double-check at T055 gates PR open at T056. |

[Post-merge fill by T025 — add "Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed" row per Decision 7]
