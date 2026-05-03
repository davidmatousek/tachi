---
prd:
  number: 201
  topic: output-integrity-threat-agent
  created: 2026-04-18
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-18, status: APPROVED, notes: "PRD grounded in BLP-01 §7 F-1 spec and Issue #201; 3 user stories preserved verbatim with job-story restructuring; 10 success criteria covering DoD bullets including schema-bump 1.5→1.6 (BLOCKING-2), corrected CWE list (BLOCKING-1), orchestrator carve-out (HIGH-1), tier-grouping consumers placement (HIGH-2), ML09 documentation-only bundling (HIGH-3), agentic_pattern downstream-set clarification (HIGH-4), Outcome A/B timeline envelopes (TL-H1), Day-1-EOD Heuristic A escalation gate (TL-H2). 2 architect BLOCKING findings + 4 architect HIGH + 2 team-lead HIGH all addressed inline before sign-off. Q-set distilled to 5 architect-owned questions with leanings captured. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-18, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 4 HIGH / 4 MEDIUM / 3 LOW. Original review surfaced 2 BLOCKING factual errors (B1 CWE-1336/CWE-73 absent from F-A1 catalog → corrected to CWE-94/CWE-22 only; B2 OI prefix absent from id.pattern regex → schema 1.5→1.6 minor bump added) and 4 HIGH (H1 orchestrator/dispatch-rules edits required → carved out from SC-9, FR-7 expanded; H2 consumers list not alphabetical → tier-grouping placement specified; H3 ML09 bundling overstated → documentation-only scope; H4 agentic_pattern downstream-set → removed from FR-1 metadata). All 6 inline-fixed. Q-leanings: Q1 Outcome B (split — psychology/linguistics primitives don't fit deterministic pattern-matching); Q2 8-12 keywords; Q3 Process only; Q4 agentic-app; Q5 Day 1 Wave 1.1 Proposed. MEDIUM: M1 ASI09 Outcome A pattern category needs CWE pinning at ADR; M2 trigger-keyword false-POSITIVE testing; M3 ADR-030 cross-refs extend to ADR-020/022/026; M4 Q3 interacts with R3. LOW: L1 SC-1 grep command verbatim; L2 SC-9 table format; L3 Q5 sequencing decoupling. Strategic intent and governance posture sound. Full review at .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-18, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 5 MEDIUM / 3 LOW. Calendar verified (cal 4 2026): 2026-04-19 Sun, 2026-04-20 Mon, 2026-04-21 Tue, 2026-04-22 Wed, 2026-04-23 Thu — all weekday labels in Timeline correct. Dependencies on-disk verified: F-A1 (9 files in schemas/taxonomy/), F-A2 (schemas/finding.yaml v1.5 with source_attribution), F-B (templates/tachi/security-report/coverage-attestation.typ) ALL PRESENT. HIGH: TL-H1 Outcome A vs B envelope ambiguity → Timeline restructured with explicit envelopes + 2026-04-23 buffer; TL-H2 Day-1-EOD Heuristic A escalation gate → added to R1 mitigation. MEDIUM: M1 consumers list tier-grouping (resolved with architect H2); M2 tester fixture path convention pending plan; M3 example regen day buffer matching Feature 194; M4 senior-backend-engineer 70-80% load with Outcome A risk; M5 BLP-01 capacity reconciliation — recommend sequential Tier 1 cadence (F-1 first, F-2/F-3/F-5 enter discover only after F-1 merge; F-4 gated regardless). LOW: L1 ADR-030 cross-cite GUIDE-threat-coverage-research §11 if Outcome A; L2 verify regex Day 1 AM (resolved by FR-1 schema bump); L3 surface DoD-bullet-8 as standalone SC for traceability. Capacity check: Feature 194 fully delivered, no spillover into 2026-04-20 week. Ready for /aod.plan. Full review at .aod/results/team-lead.md."}
source:
  idea_id: 201
  story_id: null
---

# F-1 — LLM05 Improper Output Handling: Product Requirements Document

**Status**: Approved
**Created**: 2026-04-18
**Spec**: TBD (will land at `specs/201-output-integrity-threat-agent/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 1 — first downstream Tier 1 consumer of the Foundation tier (F-A1 + F-A2 + F-B)
**Priority**: P1

---

## 📋 Executive Summary

### The One-Liner

Ship a new `output-integrity` AI-tier threat agent that detects XSS, SQLi, command injection, SSRF, template injection, and path-traversal vulnerabilities triggered by **unsafe handling of LLM-generated output** flowing into browsers, databases, shells, file systems, template engines, and external HTTP clients — closing the LLM05:2025 detection gap that input-side `prompt-injection` does not cover.

### Problem Statement

Tachi's 11 detection agents cover the *input* side of the LLM boundary comprehensively (`prompt-injection` for direct/indirect/jailbreak/system-prompt-leakage/cross-plugin attacks), but the *output* side — what happens when LLM-generated text is rendered in a browser, executed as SQL, passed to a shell, embedded in a template, written to a file, or sent as an outbound HTTP request — has **no detection ownership today**. The OWASP LLM Top 10:2025 lists LLM05 Improper Output Handling as a top-10 risk, with primary CWE references CWE-79 (XSS), CWE-89 (SQLi), CWE-918 (SSRF), and CWE-94/CWE-1336 (template/code injection). Across tachi's 6 example architectures, zero findings cite LLM05; per the BLP-01 Coverage Matrix audit, LLM05 is **Planned (Gap)** today.

A security analyst evaluating an architecture where an LLM generates HTML for a web UI, synthesizes SQL for a reporting dashboard, builds shell commands for an automation agent, or constructs URLs for an outbound HTTP call gets **no signal from tachi** that the output crosses an unsanitized trust boundary into a downstream-execution sink. The same architecture that surfaces 6 prompt-injection findings on the input side surfaces zero output-handling findings — an asymmetry that misrepresents the actual LLM attack surface.

The closely-related OWASP Machine Learning Security Top 10:2023 — specifically **ML09 Output Integrity Attack** — captures the predictive-ML counterpart (tampered classifier output corrupting downstream decisions) and is also Planned today. BLP-01 §4 bundles ML09 with LLM05 because both share the **output-side detection signal class** per Heuristic A — same agent, same pattern catalog, distinct primary citations.

There is also an open scope question on the OWASP Agentic Top 10:2026 **ASI09 Human-Agent Trust Exploitation** item: when an LLM-output-bearing agent uses misleading tone, overconfident claims, false authority signaling, or manipulative persuasion against a *human* downstream consumer, is that a sub-pattern of `output-integrity` (output crosses into a "human execution sink") or a distinct agent (`trust-exploitation`, planned as F-4)? The Heuristic A signal-class taxonomy in `GUIDE-threat-coverage-research §11` makes this decidable — but the decision **must be made in this feature's ADR before F-4 enters `/aod.discover`** per BLP-01 §8 blocking gate. The PRD frames the question; the architect adjudicates in plan/build via the public ADR.

### Proposed Solution

Author one new AI-tier threat agent and its companion skill-references directory, conforming exactly to the ADR-023 detection-variant lean pattern that the 11 existing threat agents already follow:

1. **`.claude/agents/tachi/output-integrity.md`** — new lean agent file, ≤150 lines (AI tier cap, ≤180 hard ceiling), 5-section canonical shape: YAML frontmatter → metadata YAML → `## Purpose` → `## Skill References` table → `## Detection Workflow` (single `**MANDATORY**: Read` directive at workflow start). Optional 6th `## Example Findings` section per AI-tier convention. **Zero MAESTRO references** anywhere in the file or its companion (ADR-023 Decision 2 — orchestrator owns layer inheritance).
2. **`.claude/skills/tachi-output-integrity/`** — new companion skill directory with `README.md` (consumers + purpose header) and `references/detection-patterns.md` (≥5 pattern categories with trigger keywords, applicable DFD element types, indicators per category, primary-source citations per category, and one worked example per category). Pattern categories cover the full LLM05 surface: client-side execution sinks (XSS / DOM injection), server-side execution sinks (SQLi / command injection), SSRF from LLM-synthesized URLs, template/expression injection, and path traversal + unsafe file writes — plus the bundled ML09 Output Integrity Attack predictive-ML counterpart.
3. **Additive-only edit to `.claude/skills/tachi-shared/references/finding-format-shared.md`** — extend the `consumers:` frontmatter list to include `output-integrity`. Per ADR-023 Decision 3, all existing `## ` headings remain byte-identical pre/post edit; the body is unchanged. This is the minimum-touch wiring that lets the orchestrator's finding-correlation surface treat `output-integrity` as a registered producer.
4. **`schemas/finding.yaml`** — minor additive bump **1.5 → 1.6** to extend the `id.pattern` regex with the `OI` prefix. Verified at PRD time: `schemas/finding.yaml:18` enumerates 8 specific prefixes (`S|T|R|I|D|E|AG|LLM|AGP`) — `OI` is absent. The bump is additive (regex broadens; existing IDs remain valid), follows the ADR-026 minor-bump rule for additive enum/regex extensions, and is independent of the F-A2 1.4→1.5 lineage. The new agent emits `category: llm` (existing enum value, unchanged) with sequential `OI-{N}` finding IDs. **(BLOCKING-2 architect-fix during PRD review.)**
5. **`docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`** — public per-feature ADR documenting (a) the new-agent decision, (b) the Heuristic A scope resolution for ASI09, (c) the lean-agent shape conformance per ADR-023, (d) the LLM05 + ML09 bundling rationale per BLP-01 §4. Authored under the Proposed → Accepted dual-commit pattern that ADR-027 / ADR-028 / ADR-029 established as the default protocol for BLP-01 features.
6. **Example regeneration** on the architecture that exercises the new flow (likely `agentic-app` or a newly-extended example), as the AC-3 independent-test demonstration. The 5 non-agentic-app baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

The new agent activates when any DFD `Process` element matches trigger keywords for LLM-output-to-downstream-sink flows (e.g., `LLM output`, `rendered HTML`, `model output to SQL`, `template engine`, `outbound HTTP from agent`, `command construction`). When no component exhibits an LLM-output-to-downstream-execution flow, the agent emits **zero findings — no speculation** (matching the established AI-agent convention).

**Three things the solution is deliberately NOT:**

1. It is **not** a re-scoping of `prompt-injection`. Input-side and output-side are distinct detection signal classes per Heuristic A. `prompt-injection` continues to own input-handling; `output-integrity` owns output-handling. The two agents may both fire on a single LLM Process component when both surfaces are present — that is correct behavior, not duplication.
2. It is **not** a new finding `category` value. Findings emit `category: llm` (existing enum), distinguished from `prompt-injection`'s `LLM-{N}` IDs via the `OI-{N}` ID prefix (mirroring how Feature 142 added `AGP-{N}` for agentic-pattern-synthesis findings without bumping the category enum).
3. It is **not** a runtime-behavior change for the **infrastructure-tier consumer** agents (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) — they read `category: llm` (existing enum value) and process `OI-{N}` findings through the same code paths they already use for `LLM-{N}` findings. Two orchestrator-tier files **do** receive minimal additive edits (`orchestrator.md` dispatch list + `dispatch-rules.md` LLM trio → quartet) — these are explicitly carved out from the 22-file detection-tier zero-edit invariant per Feature 142 precedent. Net change is **purely additive** to the dispatch surface; no existing dispatch ordering or downstream consumer logic is modified (HIGH-1 architect-fix during PRD review).

### Success Criteria

- **SC-1** — `.claude/agents/tachi/output-integrity.md` exists, is **≤150 lines** (AI tier cap; hard ceiling 180), and passes the ADR-023 structural-diff check: exactly **one** `**MANDATORY**: Read` directive under a `## Detection Workflow` section heading; **zero** MAESTRO references (grep-checkable across the agent file AND its companion `detection-patterns.md`).
- **SC-2** — Companion `.claude/skills/tachi-output-integrity/references/detection-patterns.md` ships with **≥5 pattern categories**, each carrying (a) at least one worked example, (b) at least one primary-source citation (OWASP LLM05:2025 minimum), (c) trigger keywords, and (d) applicable DFD element types. Pattern categories collectively cover client-side execution, server-side execution, SSRF, template/expression injection, and path traversal — plus the ML09 predictive-ML counterpart.
- **SC-3** — `.claude/skills/tachi-shared/references/finding-format-shared.md` `consumers:` frontmatter is extended to include `output-integrity` via an **additive-only edit**; all existing `## ` headings are byte-identical pre/post edit (ADR-023 Decision 3 grep check verifies this).
- **SC-4** — The new agent is invoked by orchestrator dispatch when at least one `Process` component in the architecture matches the trigger-keyword set; verified by **at least 1 new `OI-{N}` finding produced** against an example architecture exercising LLM-output-to-downstream flow. Zero findings on architectures with no qualifying Process — no speculation.
- **SC-5** — Public per-feature **ADR-030** is committed under `docs/architecture/02_ADRs/` documenting (a) the new-agent decision, (b) the Heuristic A scope resolution for ASI09 (subsume into `output-integrity` OR forward-reference `trust-exploitation` as F-4 standalone), (c) lean-agent shape conformance per ADR-023, (d) LLM05 + ML09 bundling rationale, (e) zero-MAESTRO-reference invariant proof. Authored under the dual-commit Proposed → Accepted pattern (ADR-027 / ADR-028 / ADR-029 precedent). **The Heuristic A determination is captured in the ADR BEFORE F-4 enters `/aod.discover`** per BLP-01 §8 blocking gate.
- **SC-6** — All 5 existing non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (zero-impact-when-absent invariant — no qualifying Process in those baselines, so zero new findings emit, so the threats.md / risk-scores.md / compensating-controls.md content is unchanged, so the PDF is byte-identical).
- **SC-7** — Example regeneration lands on an architecture that exercises the new flow (`agentic-app` is the leading candidate; alternative is a newly-extended example, decided by the architect at plan time). The regenerated example shows ≥1 `OI-{N}` finding with concrete mitigations and OWASP LLM05:2025 citation.
- **SC-8** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies — `pyyaml` and `pytest` already declared per Feature 128.
- **SC-9** — **22-file zero-edit invariant preserved** on the existing detection tier (ADR-023 lineage, extended by F-A1 / F-A2 / F-B): zero edits to the 11 existing threat-detection agent files (`.claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md`) or to their 11 companion `detection-patterns.md` reference files. The new agent and its companion are **additions**, not edits to the existing 22. **Carve-out**: the 22-file invariant covers the *detection tier*; orchestrator-tier files (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`) are explicitly **not** in scope of the invariant and ARE expected to receive minimal additive edits to register the new agent in the dispatch trio (see FR-7 / H1 architect finding).
- **SC-10** — **Source attribution** populated on every emitted `OI-{N}` finding using the F-A2 `source_attribution` schema field (Feature 189). Each finding cites at minimum `{taxonomy: owasp, id: LLM05, relationship: primary}`, plus relevant CWE entries (CWE-22 / CWE-78 / CWE-79 / CWE-89 / CWE-94 / CWE-918 per pattern category) as `relationship: related`. **Verified at PRD time**: all 6 CWE IDs are present as top-level records in `schemas/taxonomy/cwe.yaml`; the originally-considered CWE-1336 (template injection) and CWE-73 (path traversal) are **not** in the curated catalog — F-1 cites CWE-94 (code injection) for template injection and CWE-22 alone for path traversal to satisfy the F-A2 referential-integrity validator. This makes F-1 the **first net-new producer** of `source_attribution` in the tachi codebase post-F-A2 (independent of F-A3 wiring on the existing 22 agents). Validates the F-A2 contract end-to-end on a real production-path finding flow. **(BLOCKING-1 architect-fix during PRD review.)**

### Timeline

Target window: **2026-04-20 (Monday) → 2026-04-22 (Wednesday)** with a **2026-04-23 (Thursday) buffer** if Outcome A (subsume ASI09) is chosen. Calendar verified at PRD time (`cal 4 2026`): 2026-04-19 = Sunday, 2026-04-20 = Monday, 2026-04-21 = Tuesday, 2026-04-22 = Wednesday, 2026-04-23 = Thursday. Day 1 = first working day after PRD approval.

Two effort envelopes per the Heuristic A outcome (TL-H1 team-lead-fix during PRD review):

- **Outcome B envelope (split — ASI09 → F-4)**: **2 working days realistic**, 1.5 days aspirational. 5 pattern categories, no human-trust research, no sixth-pattern indicator authoring. Delivery 2026-04-20 → 2026-04-21.
- **Outcome A envelope (subsume — ASI09 in F-1)**: **3-3.5 working days realistic**, 3 days aspirational. 6 pattern categories including human-trust indicator research (R9). Delivery 2026-04-20 → 2026-04-22 with Thursday buffer if R5 (regeneration friction) materializes.

Either envelope front-loads Heuristic A determination at Day 1 Wave 1.0 (architect sole owner, 30-60 minute ruling, captured in ADR-030 Proposed commit). Pattern authoring proceeds Day 1 PM with the determination locked. Tester fixture authoring (Day 1 AM) and senior-backend-engineer agent file skeleton + ADR-030 boilerplate (Day 1 AM) proceed in parallel since neither depends on the Heuristic A outcome — saves ~0.25-0.5 day wall-clock time.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

Tachi's vision — automated threat modeling extending STRIDE with AI-specific threat agents for agentic applications — describes a *symmetrical* LLM detection surface: input-side and output-side both modeled, both reported, both mitigated. Today the surface is **asymmetric**: input-side (`prompt-injection`) is comprehensive across 5 pattern categories; output-side has zero detection ownership. F-1 closes the asymmetry. An adopter evaluating "does tachi cover the LLM threat surface end-to-end?" today must answer "no, the output side is missing"; post-F-1 the answer is "yes — input via `prompt-injection`, output via `output-integrity`, with both fired in concert on architectures where both surfaces are present."

### BLP-01 Initiative Fit

**Reference**: `BLP-01 threat coverage` — F-1 is the **first Tier 1 feature** in the BLP-01 initiative and the first net-new threat detection agent shipped under the BLP-01 governance umbrella (foundation tier F-A1 / F-A2 / F-B was supply-and-demand contract authoring; F-1 is the first Tier 1 consumer that adds a new detection signal class).

F-1's place in the BLP-01 chain:

```
F-A1 (Feature 180, delivered 2026-04-17)
  │  Supply: 7 framework YAML catalogs + 526-edge crosswalk
  ▼
F-A2 (Feature 189, delivered 2026-04-17)
  │  Demand contract: source_attribution field on findings
  ▼
F-B  (Feature 194, delivered 2026-04-18)
  │  Adopter-facing renderer: per-finding citation table + per-framework coverage matrix in PDF
  ▼
F-1 (this PRD, #201) ◄────── FIRST TIER 1 FEATURE
  │  New output-integrity agent — first net-new detection signal class under BLP-01
  ▼
F-2 (LLM09 Misinformation, parallel-eligible with F-1)
F-3 (ASI07 Inter-Agent Communication, parallel-eligible)
F-4 (ASI09 Human-Agent Trust Exploitation, GATED on F-1 Heuristic A resolution)
F-5 (LLM10 Unbounded Consumption, parallel-eligible)
  ▼
F-6, F-7 (Tier 2 ML + Mobile bundles)
F-8 (Tier 3 Web/API attestation)
```

**F-4 is blocked by F-1's Heuristic A resolution.** The ASI09 scope question — "subsume Human-Agent Trust Exploitation into `output-integrity` OR ship `trust-exploitation` as a standalone agent in F-4" — must be adjudicated in ADR-030 before F-4 can enter `/aod.discover`. This is an explicit BLP-01 §8 blocking gate. F-2, F-3, and F-5 are not gated on F-1.

**F-1 is the first net-new producer of `source_attribution` in the tachi codebase** — every `OI-{N}` finding cites OWASP LLM05:2025 as primary plus relevant CWEs as related, exercising the F-A2 contract on the production path independent of F-A3 (which wires the existing 22 agents to populate `source_attribution`). This is a meaningful end-to-end validation moment for the BLP-01 Foundation tier.

### Recent ADR Lineage

- **ADR-023** (Threat Agent Skill References Pattern, Accepted 2026-04-11): defines the lean-agent detection variant that F-1's new agent file MUST conform to. Decision 1 (single-point load), Decision 2 (zero MAESTRO references), Decision 3 (additive-only shared-reference edits) are all directly invoked. SC-1 + SC-3 + SC-9 trace to this ADR.
- **ADR-021** (SOURCE_DATE_EPOCH determinism, Accepted earlier): SC-6 byte-identity gate on the 5 non-agentic baselines uses this harness.
- **ADR-027** (Taxonomy Crosswalk Schema, Accepted 2026-04-17): F-1 cites OWASP LLM05 from `schemas/taxonomy/owasp.yaml`. The 5-value taxonomy enum (Decision 3) is the source of `taxonomy: owasp` in F-1's `source_attribution` records.
- **ADR-028** (Source Attribution Schema Extension, Accepted 2026-04-17): SC-10 is direct consumption of this contract — F-1 emits `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, ...]` per finding. F-1 is the first agent in the codebase to populate the field as a production behavior (not a fixture).
- **ADR-029** (Coverage Attestation Report Section, Accepted 2026-04-18): F-1's findings will surface in F-B's per-finding attribution table and the per-framework coverage matrix when the regenerated example is included in a security-report PDF run. F-B's `has-source-attribution` boolean will fire `true` on the regenerated `agentic-app` (or alternative) example post-F-1.
- **Feature 082 precedent** (Threat Agent Skill References — Detection Tier Lean Refactor, delivered 2026-04-11): the 11-agent refactor that produced ADR-023. F-1 is the **first net-new agent** authored under that pattern (vs. the 11 agents that were retrofitted). Sets the precedent that all future threat-detection agents land in lean+skill-references shape from authoring rather than from refactor.

### Roadmap Fit

- **Phase**: BLP-01 Tier 1 (AI/Agentic gaps, depth + breadth)
- **Week**: Week of 2026-04-20 — immediate follow-on to Feature 194 (F-B) delivery
- **Dependencies**:
  - F-A1 (Feature 180) — **SATISFIED** as of 2026-04-17 (verified: `schemas/taxonomy/` populated)
  - F-A2 (Feature 189) — **SATISFIED** as of 2026-04-17 (verified: `schemas/finding.yaml` v1.5 carries `source_attribution`; parser round-trips)
  - F-B (Feature 194) — **SATISFIED** as of 2026-04-18 (verified: `templates/tachi/security-report/coverage-attestation.typ` exists; `has-source-attribution` boolean wired)

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **Security Analyst**

- **Role**: Application security engineer or external consultant performing threat modeling on an LLM-integrated system
- **Goal**: Surface the full LLM threat surface — input-side (prompt injection) AND output-side (downstream-execution sinks) — with concrete, mitigation-bearing findings rooted in OWASP LLM Top 10 vocabulary
- **Pain Point Today**: Tachi reports prompt-injection findings on the input side but is silent on the output side. The analyst must hand-author the LLM05 portion of the threat model, citing OWASP LLM05:2025 manually, with no architectural-context-aware finding generation.
- **Value Delivered**: Per-component `OI-{N}` findings with stack-specific mitigations (HTML entity encoding, JSON string escaping, parameterized SQL, allowlist-based path validation, etc.) emitted automatically when the architecture exhibits LLM-output-to-downstream-sink flow. Coverage Matrix shows LLM05:2025 + ML09:2023 as Covered (and conditionally ASI09 if Heuristic A subsumes it).

### Secondary Persona: **Developer Integrating an LLM into a Web Application**

- **Role**: Backend or full-stack developer wiring an LLM into a customer-facing application or internal automation
- **Goal**: Address tachi findings without researching the output-handling pattern from primary OWASP / CWE sources
- **Pain Point Today**: Generic security advice ("sanitize output") doesn't translate to a concrete code change. Developers want named technologies (e.g., "use `parameterized queries` for DB writes from LLM output", "use `HTML entity encoding` before rendering LLM output in the browser DOM").
- **Value Delivered**: Each `OI-{N}` finding's `mitigation` field names specific encodings, libraries, or patterns matched to the detected sink type — server-side execution sinks get parameterized-query / structured-IR guidance; client-side execution sinks get HTML entity encoding / Content Security Policy guidance; SSRF flags get allowlist + outbound-egress-control guidance.

### Tertiary Persona: **Adopter Running tachi on an Agentic Application**

- **Role**: Tachi adopter whose architecture includes both machine-victim and human-victim downstream consumers of LLM output
- **Goal**: Get a coherent answer on whether tachi covers the human-trust-exploitation surface (ASI09) — either subsumed under `output-integrity` (one agent, broader scope) or surfaced via a forthcoming `trust-exploitation` agent (F-4)
- **Pain Point Today**: ASI09 is Planned in the Coverage Matrix; the adopter has no signal on which feature closes it or when
- **Value Delivered**: ADR-030 makes the Heuristic A determination explicit. If subsumed: F-1's `detection-patterns.md` ships a sixth pattern category covering Human-Trust Exploitation via LLM Output; adopters see ASI09 transition Planned → Covered immediately on F-1 merge. If split: F-1 explicitly forward-references `trust-exploitation` (F-4) in its `## Purpose` section and ASI09 stays Planned pending F-4 delivery — but the path is unblocked.

### Quaternary Persona: **Tachi Maintainer**

- **Role**: Maintainer preserving backward compatibility, byte-identity baselines, and the 22-file zero-edit invariant established by Feature 082 / ADR-023
- **Goal**: Ship a new threat agent without regressing any of the 5 byte-identity baselines and without touching any of the 22 existing detection-tier files
- **Pain Point Today**: New detection agents have historically been a high-risk surface because dispatch wiring + shared-reference consumption + finding-correlation register all touch infrastructure files
- **Value Delivered**: The lean-agent + skill-references pattern (ADR-023) makes new-agent authoring **purely additive** — one new agent file + one new companion skill directory + one additive frontmatter edit. SC-3, SC-6, and SC-9 collectively guarantee no infrastructure-tier regression by construction.

---

## 📖 User Stories

All three user stories are preserved verbatim from GitHub Issue #201 (which sourced them from BLP-01 §7, F-1). Job-story restructuring applied to align with the Feature 194 PRD precedent; acceptance criteria preserved verbatim where they specify testable predicates.

### US-201-1: LLM-Output-to-Downstream-Sink Detection

**When** a security analyst threat-models an architecture where LLM output flows into a browser, SQL query, shell, template engine, file write, or HTTP client without post-model sanitization,
**I want** tachi to flag those components with concrete `OI-{N}` findings citing OWASP LLM05:2025,
**So I can** catch the XSS/SQLi/SSRF/template-injection/path-traversal surface that input-side `prompt-injection` detection does not cover.

**Acceptance Criteria**:

- **Given** an architecture that includes an LLM Process whose output is rendered as HTML in a browser-facing component without declared output encoding, **when** the orchestrator dispatches `output-integrity`, **then** an `OI-N` finding emits with `category: llm`, `references` citing `OWASP LLM05:2025`, and `source_attribution` containing `{taxonomy: owasp, id: LLM05, relationship: primary}` plus `{taxonomy: cwe, id: CWE-79, relationship: related}`.
- **Given** an architecture where an LLM-generated string is passed as a SQL fragment, shell command, or file path to a downstream Process, **when** `output-integrity` runs, **then** a finding emits with `mitigation` field naming **specific** technologies — `parameterized queries`, `allowlist-based sanitization`, `structured intermediate representations`, or `command-line arg vector construction (no shell interpolation)` — not generic "sanitize output" prose.
- **Given** an architecture where an LLM is used to synthesize HTTP requests to external services, **when** `output-integrity` runs, **then** an SSRF finding emits on the outbound-call boundary with `references` citing `OWASP LLM05:2025` plus `{taxonomy: cwe, id: CWE-918, relationship: related}` in `source_attribution`.
- **Given** an architecture with **no** component exhibiting an LLM-output-to-downstream-execution flow, **when** `output-integrity` runs, **then** **zero findings** emit — no speculation. The agent's behavior matches the established AI-tier convention (zero-finding outcome on architectures lacking the trigger surface).

**Priority**: P0
**Effort**: M

### US-201-2: Stack-Specific Mitigation Guidance

**When** a developer reads an `OI-{N}` finding and needs to address it in their codebase,
**I want** the mitigation field to name specific encodings, libraries, or patterns matched to the detected sink type,
**So I can** apply the fix without re-deriving the output-handling pattern from primary OWASP/CWE sources.

**Acceptance Criteria**:

- **Given** an `OI-N` finding for a client-side execution sink (XSS / DOM injection), **when** the `mitigation` field is read, **then** it names at least one specific encoding mechanism — e.g., `HTML entity encoding`, `Content Security Policy with strict directive set`, `safe DOM APIs (textContent, not innerHTML)`, or `framework-native escape helpers (React {}, Vue v-text)`.
- **Given** an `OI-N` finding for a server-side execution sink (SQLi / command injection), **when** the `mitigation` field is read, **then** it names at least one specific defensive pattern — e.g., `parameterized SQL queries`, `JSON string escaping`, `command-line arg vector (subprocess.run(..., shell=False))`, or `allowlist-based input validation against a closed enum`.
- **Given** any `OI-N` finding, **when** its `references` array is inspected, **then** at least one entry is `OWASP LLM05:2025` (primary), and `source_attribution` carries that as `relationship: primary`. CWE references — CWE-79 (XSS), CWE-89 (SQLi), CWE-918 (SSRF), CWE-94 (code injection), CWE-22 (path traversal) — appear in `source_attribution` as `relationship: related` per applicable pattern category.
- **Given** the agent's output across pattern categories, **when** threat descriptions are inspected, **then** they distinguish between **server-side execution** (SQLi, command injection, SSRF — runs on tachi's server / backend) and **client-side execution** (XSS, DOM injection — runs in user browser). The categorization aligns with OWASP LLM05:2025's threat-class taxonomy.

**Priority**: P0
**Effort**: M

### US-201-3: Heuristic A Resolution for ASI09 Scope

**When** an adopter runs tachi on an agentic application where an LLM-bearing agent uses misleading tone, overconfident claims, false authority signaling, or manipulative persuasion against a *human* downstream consumer,
**I want** ADR-030 to make an explicit Heuristic A determination on whether ASI09 Human-Agent Trust Exploitation is covered by `output-integrity` or by a future `trust-exploitation` agent (F-4),
**So I can** see ASI09's coverage status (Covered or Planned-with-clear-owner) rather than the ambiguous Planned-with-no-owner state the Coverage Matrix shows today.

**Acceptance Criteria**:

- **Given** the public ADR-030 at the time of F-1 merge, **when** the architect's Heuristic A determination is read, **then** it explicitly resolves one of two outcomes:
  - **Outcome A (subsume)**: ASI09 falls under `output-integrity` because human-victim output handling is the same detection signal class as machine-victim output handling (per Heuristic A — the signal is "LLM output crosses an unsanitized boundary into a downstream consumer", with humans treated as a downstream consumer alongside browsers/SQL/shells). In this case the companion `detection-patterns.md` ships a **sixth pattern category** "Human-Trust Exploitation via LLM Output" with at least one worked example (e.g., LLM output overconfidently claims authoritative medical/legal/financial advice without uncertainty signaling), primary source `OWASP ASI09:2026`, and trigger keywords for human-facing LLM output paths. F-4 closes as N/A on F-1 merge.
  - **Outcome B (split)**: ASI09 stays scope-distinct because human-victim signal class is meaningfully different (psychology + linguistics primitives vs. encoding + sanitization primitives) and warrants its own agent. In this case F-1's `## Purpose` section explicitly forward-references `trust-exploitation` (F-4) as the future owner, lists ASI09 as out-of-scope, and the detection-patterns ship the original 5 categories without a sixth. F-4 unblocks for `/aod.discover` on F-1 merge.
- **Given** the resolution, **when** ADR-030's Decisions section is inspected, **then** the chosen Outcome is justified with explicit reference to GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy (the worked-example reference for the ASI09-into-F-1-or-F-4 decision tree).
- **Given** the chosen Outcome, **when** the BLP-01 Coverage Matrix is updated post-F-1 merge, **then** ASI09:2026 transitions Planned → Covered (Outcome A) OR remains Planned with explicit "F-4 owner" annotation (Outcome B) — the ambiguity is resolved either way.
- **Given** ADR-030 acceptance, **when** F-4's `/aod.discover` invocation is attempted, **then** the Heuristic A determination is already in place and the BLP-01 §8 blocking gate ("F-1 resolves F-4 scoping") is satisfied.

**Priority**: P0
**Effort**: S (the determination itself is a 30-60 minute architect ruling; the documentation in the ADR is a few paragraphs; the conditional sixth pattern category if Outcome A is chosen is one additional pattern in the catalog)

---

## ⚙️ Functional Requirements

### FR-1 — New Lean Agent File `output-integrity.md`

- **File**: `.claude/agents/tachi/output-integrity.md`
- **Length**: ≤150 lines (AI tier cap per ADR-023). Hard ceiling: 180 lines.
- **Shape (5-section canonical, optional 6th `Example Findings`)**:
  1. YAML frontmatter (`name`, `description`, `tools`, `model`)
  2. Metadata YAML block (`category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM05:2025, OWASP ML09:2023]`, `output_schema: ../../../schemas/finding.yaml`). **Note**: `agentic_pattern` is **not** declared in the agent metadata — it is set downstream by orchestrator Phase 3.6 per ADR-026 (HIGH-4 architect-fix during PRD review).
  3. `## Purpose` — describes the output-handling threat surface, lists the 5 sink categories, and explicitly resolves ASI09 scope per Heuristic A (Outcome A subsumes; Outcome B forward-references `trust-exploitation`)
  4. `## Skill References` — table with 3 rows: (a) `detection-patterns.md` (this agent's companion), (b) `severity-bands-shared.md` (OWASP 3×3 risk matrix), (c) `finding-format-shared.md` (canonical finding IR + producer-audience section)
  5. `## Detection Workflow` — exactly **one** `**MANDATORY**: Read` directive at section start pointing at the companion `detection-patterns.md`. Numbered steps (5-6 typical) walk the agent through pattern matching → indicator collection → severity computation → finding emission with `source_attribution`
  6. (Optional) `## Example Findings` — 2-3 example findings demonstrating the canonical shape with `OI-{N}` IDs, `category: llm`, `source_attribution` populated

- **Trigger keywords** (declared in metadata or discoverable from `## Detection Workflow` step 2):
  - `LLM output`
  - `rendered HTML` / `model output to browser`
  - `model output to SQL` / `LLM-generated query`
  - `template engine` / `template injection`
  - `outbound HTTP from agent` / `LLM-synthesized URL`
  - `command construction` / `shell from LLM`
  - `file path from model` / `LLM-generated path`
- **DFD targets**: `Process` (primary; the LLM-bearing component). Optionally `Data Flow` for boundary-crossing output flows (decided by the architect at plan time).
- **MAESTRO references**: **ZERO** anywhere in the file (ADR-023 Decision 2 invariant). Grep-checkable.

### FR-2 — New Companion Skill Directory `tachi-output-integrity/`

- **Directory**: `.claude/skills/tachi-output-integrity/`
- **Files**:
  - `README.md` — consumers + purpose header (mirror `.claude/skills/tachi-prompt-injection/README.md` shape)
  - `references/detection-patterns.md` — the pattern catalog
- **`detection-patterns.md` shape** (mirror `prompt-injection/references/detection-patterns.md`):
  - Frontmatter (`name`, `description`, `consumers: [tachi-output-integrity]`, `last_updated: 2026-04-22` (or actual merge date))
  - `## Overview` — one-paragraph description of the pattern catalog scope
  - `## Detection Scope` — `### Trigger Keywords` (case-insensitive list) + `### Applicable DFD Element Types`
  - `## Detection Patterns` — numbered list of **≥5** pattern categories. Each category specifies: name, primary OWASP/CWE source, indicators (3-6 bullet points), and at least one worked example
- **Required pattern categories** (≥5; sixth conditional on Heuristic A Outcome A; CWE IDs verified present in `schemas/taxonomy/cwe.yaml`):
  1. **Client-Side Execution Sinks (XSS / DOM Injection)** — primary `OWASP LLM05:2025`, related `CWE-79`. Indicators: LLM output rendered as `innerHTML`, no Content Security Policy, no framework escape helpers, missing HTML entity encoding pre-render.
  2. **Server-Side Execution Sinks (SQLi / Command Injection)** — primary `OWASP LLM05:2025`, related `CWE-89` (SQLi), `CWE-78` (OS command injection), `CWE-94` (code injection). Indicators: LLM output concatenated into SQL string, shell command interpolation, missing parameterized-query usage, missing arg-vector construction.
  3. **SSRF from LLM-Synthesized URLs** — primary `OWASP LLM05:2025`, related `CWE-918`. Indicators: LLM output used as URL for outbound HTTP, no allowlist enforcement, no egress firewall, missing scheme validation.
  4. **Template / Expression Injection** — primary `OWASP LLM05:2025`, related `CWE-94` (Improper Control of Generation of Code — covers template-engine code injection). Indicators: LLM output passed to Jinja2 / Handlebars / EJS / Mustache template render without escape mode, server-side template engine receiving model output verbatim. (CWE-1336 is the more-specific template-injection CWE but is **not** present in F-A1's curated `cwe.yaml` catalog at PRD time; CWE-94 is the in-catalog parent — BLOCKING-1 architect-fix during PRD review.)
  5. **Path Traversal + Unsafe File Writes** — primary `OWASP LLM05:2025`, related `CWE-22`. Indicators: LLM output used as file path, no canonicalization, no allowlist directory enforcement, write operations to model-supplied paths. (CWE-73 was originally proposed but is **not** present in F-A1's curated `cwe.yaml` catalog at PRD time; CWE-22 alone covers path traversal — BLOCKING-1 architect-fix during PRD review.)
  6. **(CONDITIONAL — only if Heuristic A Outcome A)** **Human-Trust Exploitation via LLM Output** — primary `OWASP ASI09:2026`. Indicators: LLM output emits authoritative claims without uncertainty signaling, no source-citation requirement, no human-in-the-loop on consequential output, missing tone/persuasion classifier on output. (Omitted entirely if Outcome B chosen.)
- **ML09:2023 bundling — documentation-only, not pattern-level**: The pattern catalog primarily detects LLM05 surfaces (output sanitization). OWASP ML09:2023 Output Integrity Attack (predictive-ML output tampering) is a related but distinct signal class. F-1's contribution to ML09 closure is **documentation-only**: ADR-030 records the bundling rationale per BLP-01 §4, the Coverage Matrix transitions ML09 to Covered citing F-1 as the closure path, and the agent's `## Purpose` notes that classifier-output-tampering scenarios are surfaced when they exhibit the same output-handling indicators (e.g., classifier output passed to a SQL query without sanitization). ML09 is **not** added as a per-pattern primary citation — pattern primary remains OWASP LLM05:2025 (HIGH-3 architect-fix during PRD review).

### FR-3 — Additive-Only Edit to `finding-format-shared.md`

- **File**: `.claude/skills/tachi-shared/references/finding-format-shared.md`
- **Edit**: extend the `consumers:` frontmatter list to include `output-integrity`. **Insertion convention**: tier-grouping per Feature 082 precedent (the list is NOT alphabetical — verified at PRD time: order is `orchestrator` → STRIDE-canonical (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) → AI-LLM (prompt-injection, data-poisoning, model-theft) → AI-AG (agent-autonomy, tool-abuse) → infra-consumer (risk-scorer)). The natural placement for `output-integrity` is **after `tool-abuse` and before `risk-scorer`** — appended to the AI tier as the new AI-LLM-side detection agent. Architect adjudicates the final placement at plan time (HIGH-2 architect-fix + MEDIUM-1 team-lead-fix during PRD review).
- **Invariant**: all existing `## ` headings remain **byte-identical** pre/post edit. Body content is unchanged. Only the frontmatter consumer list changes.
- **Enforcement**: ADR-023 Decision 3 grep check verifies byte-identity on `## ` headings; manual inspection verifies the body diff is empty outside the consumer list addition.

### FR-4 — Source Attribution on Every `OI-{N}` Finding

- Every emitted `OI-{N}` finding **MUST** include a non-empty `source_attribution` array per the F-A2 schema (Feature 189).
- Minimum: `{taxonomy: owasp, id: LLM05, relationship: primary}` on every finding.
- Per pattern category, additional CWE entries as `relationship: related` (CWE IDs verified present in `schemas/taxonomy/cwe.yaml` at PRD time):
  - Client-side execution: `{taxonomy: cwe, id: CWE-79, relationship: related}`
  - Server-side execution: `{taxonomy: cwe, id: CWE-89, relationship: related}` (SQLi) AND/OR `{taxonomy: cwe, id: CWE-78, relationship: related}` (command injection) AND/OR `{taxonomy: cwe, id: CWE-94, relationship: related}` (code injection)
  - SSRF: `{taxonomy: cwe, id: CWE-918, relationship: related}`
  - Template injection: `{taxonomy: cwe, id: CWE-94, relationship: related}` (CWE-1336 absent from F-A1 catalog at PRD time — CWE-94 is the in-catalog parent)
  - Path traversal: `{taxonomy: cwe, id: CWE-22, relationship: related}` (CWE-73 absent from F-A1 catalog at PRD time — CWE-22 alone covers the surface)
- **No ML09 in `source_attribution`** — ML09 bundling is documentation-only per FR-2 ML09:2023 bundling note (HIGH-3 architect-fix during PRD review). `source_attribution` carries only resolvable taxonomy IDs that pass F-A2 referential-integrity validation.
- **F-1 is the first net-new producer of `source_attribution` in the codebase post-F-A2** — independent of F-A3 wiring on the existing 22 agents. Validates the F-A2 contract end-to-end on a real production-path finding flow.

### FR-5 — New ADR-030 Public Per-Feature ADR

- **File**: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- **Status**: Proposed → Accepted dual-commit (ADR-027 / ADR-028 / ADR-029 precedent — the protocol is now the default for BLP-01 features). Initial Proposed commit at Day 1 Wave 1.1 schema-lock; transitions Accepted at PR merge with provisional merge-date; post-merge SHA fill records the squash commit.
- **Required body items**:
  1. **Decision** statement — adopt new `output-integrity` agent for LLM05 closure
  2. **Heuristic A scope resolution** for ASI09 — Outcome A (subsume) OR Outcome B (split, forward-reference F-4). Justification with explicit reference to GUIDE-threat-coverage-research §11.
  3. **Lean-agent shape conformance** per ADR-023 — single-point load, ≤150 lines, zero MAESTRO references
  4. **LLM05 + ML09 bundling rationale** per BLP-01 §4 — same output-side detection signal class
  5. **Cross-references** to ADR-023 (lean shape), ADR-021 (determinism), ADR-027 (taxonomy), ADR-028 (source_attribution contract), ADR-029 (coverage attestation)
  6. **22-file zero-edit invariant** preserved — explicit grep-auditable enumeration
  7. **Commercial framing omitted** per blueprint governance — no Layer 2, no tachi Cloud, no commercial roadmap. Public ADR stands on technical merits alone.
  8. **Revision history** table tracking Proposed → Accepted transition with dates

### FR-6 — Example Regeneration

- Identify the architecture that exercises the new flow. **Leading candidate**: `examples/agentic-app/architecture.md` (extended in Feature 142 with second LLM agent + learning loop + inter-agent communication channel — already exercises LLM Process boundaries).
- **Alternative**: extend a different example architecture to add an LLM-output-to-downstream-sink flow (e.g., extend `examples/web-app/` with an LLM-content-generation component whose output renders in a browser). Architect adjudicates at plan time.
- The regenerated example MUST surface ≥1 `OI-{N}` finding with concrete mitigations, OWASP LLM05:2025 citation, and populated `source_attribution`.
- All other example PDFs regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` (SC-6).

### FR-7 — Orchestrator Dispatch Registration

- **Architect verification at PRD time** (HIGH-1 architect-fix during PRD review): orchestrator agent discovery is **not** purely directory-walk. `.claude/agents/tachi/orchestrator.md` (lines 32-44) hardcodes the 11-agent dispatch list, and `.claude/skills/tachi-orchestration/references/dispatch-rules.md` (lines 70-73) hardcodes the LLM dispatch trio. Two minimal additive edits are required to register `output-integrity`:
  1. **`.claude/agents/tachi/orchestrator.md`** — add `output-integrity` to the dispatch list (one line addition; preserves alphabetical or tier-grouped ordering as established in the file).
  2. **`.claude/skills/tachi-orchestration/references/dispatch-rules.md`** — extend the LLM dispatch trio to a quartet (`prompt-injection`, `data-poisoning`, `model-theft`, `output-integrity`) and add the trigger-keyword rules for `output-integrity` activation.
- These edits are explicitly **out of scope** of the 22-file detection-tier zero-edit invariant (SC-9 carve-out). Orchestrator-tier files have always been editable for additive agent registration; this is the same pattern Feature 142 used to register Phase 3.6 synthesis output.
- **Zero edits to risk-scorer, control-analyzer, threat-report, threat-infographic, or report-assembler** — those infrastructure agents read `category: llm` (existing enum value); `OI-{N}` findings flow through them without any consumer-side edit.
- Verify via: a `/tachi.threat-model` invocation against the regenerated example architecture surfaces ≥1 `OI-{N}` finding without any further pipeline-config edit.

---

## 🚫 Non-Functional Requirements

### NFR-1 — Determinism

The new agent's output MUST be deterministic per ADR-021. Same architecture input → same finding set → same finding ordering. Pattern matching is keyword-based + structural (DFD-element-type filtering); no LLM-judgment in pattern selection. Severity computation uses the OWASP 3×3 matrix from `severity-bands-shared.md` deterministically.

### NFR-2 — Backward Compatibility

The 5 non-agentic example PDF baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` (SC-6). No qualifying Process in those baselines means zero new findings, which means unchanged threats.md / risk-scores.md / compensating-controls.md content, which means byte-identical PDFs.

### NFR-3 — Tier-Cap Compliance

Agent file ≤150 lines (AI tier cap per ADR-023, FR-10 in Feature 082 spec). Hard ceiling 180 lines. Companion `detection-patterns.md` has no formal line cap but should remain in the ~150-300 line range typical of the existing 11 companion files for readability.

### NFR-4 — Zero New Dependencies

Empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` (SC-8). The new agent uses only existing tachi infrastructure (orchestrator dispatch, shared references, schema, parser).

### NFR-5 — Security & Privacy

The agent reads architecture descriptions and emits findings. No network calls, no file writes outside the standard finding-emission path, no execution of LLM-output content (the agent only **describes** the threat, never reproduces or executes attack payloads). The pattern catalog uses anonymized worked examples — no real-world adopter data.

---

## 🧱 Architecture & Design Decisions (Open for Architect)

The following decisions are **architect-owned** and adjudicated during `/aod.plan` (project-plan / spec stages) or in ADR-030 directly. PM frames the trade-off space; architect picks. Bracketed "[arch]" tags mark decisions explicitly delegated.

### Q1 — ASI09 Heuristic A Resolution [arch]

**Question**: Does ASI09 Human-Agent Trust Exploitation fold into `output-integrity` (Outcome A) or stay scope-distinct as a future `trust-exploitation` agent (Outcome B, F-4)?

**PM framing**:
- **Outcome A** simplifies the BLP-01 Tier 1 cadence (5 features → 4 features; F-4 closes N/A). One agent owns "LLM output crosses an unsanitized boundary into a downstream consumer" regardless of consumer type (browser, SQL, shell, human). The sixth pattern category captures the human-victim case.
- **Outcome B** preserves a clear scope boundary between **encoding/sanitization primitives** (machine victims — `output-integrity`) and **psychology/linguistics primitives** (human victims — `trust-exploitation`). F-4 ships as a separate Tier 1 feature; F-1 explicitly forward-references it.

**Decision blocker**: BLP-01 §8 — F-4 cannot enter `/aod.discover` until F-1's Heuristic A determination is captured in ADR-030.

**Reference**: GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy (worked example for the ASI09 decision tree).

### Q2 — Trigger Keyword Set Final Form [arch]

**Question**: The PRD lists 7 trigger keywords (`LLM output`, `rendered HTML`, `model output to SQL`, `template engine`, `outbound HTTP from agent`, `command construction`, `file path from model`). Is this the right set, or should it expand/contract?

**PM framing**: The set is a starting point. Architect may add patterns observed in real architectures (e.g., `model output to file`, `LLM-driven response`) or trim patterns that produce false positives during the example-regeneration smoke test.

### Q3 — DFD Target Set: Process Only, or Also Data Flow? [arch]

**Question**: Should the agent target only `Process` elements (the LLM-bearing component) or also `Data Flow` elements (the boundary the output crosses)?

**PM framing**: The 11 existing AI-tier agents target `Process` exclusively. Adding `Data Flow` would be a precedent break; the rationale would be "the threat surface is the boundary, not the producer." The architect adjudicates.

### Q4 — Example Architecture for Regeneration [arch]

**Question**: Use `examples/agentic-app/` (Feature 142 already extended it with multi-agent + learning loop) or extend a different example (e.g., `examples/web-app/`) to introduce the new flow?

**PM framing**: `agentic-app` is the established "regeneration target for new AI agents" per Features 084 / 142 / 145 precedent. Using it again preserves the convention. Extending a non-agentic example would broaden the demonstration but adds scope.

### Q5 — ADR-030 Sequencing [arch]

**Question**: Author ADR-030 as Proposed at Day 1 Wave 1.1 (mirrors ADR-027 / ADR-028 / ADR-029) or only at Day 3 EOD before merge?

**PM framing**: The dual-commit pattern is now the default for BLP-01 features. Day 1 Proposed commit unblocks parallel pattern-catalog authoring downstream of the Heuristic A determination. Recommended: follow the established protocol.

---

## 🚫 Out of Scope (Explicit)

The following items are **explicitly out of scope** for F-1. Each carries a forward-reference to the feature that DOES own it.

1. **Wiring the existing 22 detection-tier files (11 agents + 11 companion `detection-patterns.md`) to populate `source_attribution`** — that is **F-A3** (not yet shipped, separate Tier 1 follow-on outside BLP-01 scope sequence). F-1 is **additive-only** to the agent fleet; F-1's `source_attribution` population on `OI-{N}` findings is a new producer at the new agent boundary, not a retrofit.
2. **`trust-exploitation` agent for ASI09 (Outcome B path)** — that is **F-4**, gated on F-1's Heuristic A resolution per BLP-01 §8 blocking gate. F-1 either subsumes ASI09 (Outcome A — F-4 closes N/A) or unblocks F-4 with explicit forward-reference (Outcome B).
3. **`misinformation` agent for LLM09** — that is **F-2**, parallel-eligible with F-1, separate PRD, separate detection signal class (factual integrity, not output handling).
4. **`tool-abuse` enrichment for ASI07 inter-agent communication** — that is **F-3**, parallel-eligible with F-1, enriches an existing agent rather than authoring a new one.
5. **`denial-of-service` + `model-theft` enrichment for LLM10** — that is **F-5**, parallel-eligible with F-1.
6. **OWASP ML Top 10 bundle (10 items beyond ML09)** — that is **F-6**, Tier 2 follow-on. ML09 ships in F-1 because it shares the output-side signal class; the other 9 ML items have distinct detection signal classes.
7. **OWASP Mobile Top 10 bundle** — that is **F-7**, Tier 2.
8. **Web/API attestation** — that is **F-8**, Tier 3.
9. **Cross-feature reasoning (e.g., "an OI-N finding + a related LLM-N finding compose into a chained-attack narrative")** — Feature 141 cross-layer attack chains already covers this; the orchestrator's Phase 3.5 chain correlation will pick up `OI-{N}` findings automatically when they participate in cross-MAESTRO-layer chains. F-1 does not need any chain-correlation changes; the existing infrastructure handles it.
10. **PDF report Section 4b "Findings by Agentic Pattern" entry** — F-1 findings emit `agentic_pattern: none` (no pattern synthesis in this feature). Section 4b remains untouched.
11. **Coverage Matrix update in `BLP-01-threat-coverage.md`** — that document lives in `_internal/strategy/` (gitignored). Updates to the Coverage Matrix happen post-merge in a separate documentation commit on the private side. F-1 does not touch the public `docs/` representation of coverage (that comes via F-B's per-framework coverage matrix in the PDF, which auto-renders from `source_attribution` data — F-1 gets credit on F-B's matrix automatically once findings flow through).

---

## ⚠️ Risks & Mitigations

### R1 — Heuristic A Ambiguity Blocks Pattern Authoring

**Risk**: If the architect cannot decide Outcome A vs Outcome B early in Day 1, the pattern catalog cannot be finalized (Outcome A requires a 6th pattern category; Outcome B requires the 5-category set to forward-reference F-4).
**Likelihood**: Medium (Heuristic A is a real judgment call with arguments on both sides).
**Impact**: Medium (pattern authoring blocks; team-lead may have to reschedule Day 1 work to other tracks).
**Mitigation**: Front-load the Heuristic A determination at Day 1 Wave 1.0 (architect sole owner, 30-60 minute ruling, captured in ADR-030 Proposed commit). Pattern authoring proceeds Day 1 PM with the determination locked. Tester fixture authoring (Day 1 AM) and senior-backend-engineer agent file skeleton (Day 1 AM) proceed in parallel since neither depends on the Heuristic A outcome.
**Hard escalation gate (TL-H2 team-lead-fix during PRD review)**: If the Heuristic A determination is **not** committed to ADR-030 Proposed by Day 1 EOD (Monday 2026-04-20), `/aod.tasks` MUST surface an explicit user-tie-break escalation step before Day 2 AM. Drift past Day 1 EOD cascades into Day 3 overload (pattern authoring + example regen + triple sign-off concentrated in a single day) — the Day-1-EOD hard gate prevents the cascade.

### R2 — Orchestrator Dispatch Registration Edits

**Risk**: ~~Auto-discovery may fail.~~ **Resolved at PRD time per HIGH-1 architect-fix**: orchestrator dispatch is hardcoded (orchestrator.md lines 32-44 + dispatch-rules.md lines 70-73). Two minimal additive edits are required (FR-7) — not auto-discovery. Original risk reframed as: edits to orchestrator-tier files might inadvertently affect dispatch ordering for other agents.
**Likelihood**: Low (the additive edits append `output-integrity` to existing lists; established pattern from Feature 142 Phase 3.6 registration).
**Impact**: Medium (a misordered dispatch list could change finding-emission order in a regenerated example, breaking byte-identity on the regenerated artifact only — the 5 non-agentic baselines are unaffected since none of their architectures match the new agent's trigger keywords).
**Mitigation**: Architect verifies the additive edit position at plan time; tester runs a structured pre-vs-post diff on the regenerated example to confirm only the expected new findings appear. Architect also confirms the orchestrator's component-classification logic (in `orchestrator.md` Phase 1) does not need updating — `output-integrity` agent activates on existing `Process` element types with `category: llm`, which the orchestrator already classifies correctly.

### R3 — Pattern False Positives on Architectures Without Real Output Sinks

**Risk**: Trigger keywords like `LLM output` are over-broad; an LLM Process whose output is purely returned to a calling agent (no downstream sink) might match and produce a false-positive finding.
**Likelihood**: Medium.
**Impact**: Medium (false positives degrade adopter trust; over-firing the agent on non-qualifying architectures contradicts US-201-1's "zero findings — no speculation" criterion).
**Mitigation**: Pattern indicators MUST require **both** a trigger keyword match AND a structural indicator of the downstream sink (e.g., the LLM's output flowing into a Data Flow whose target is a browser-facing component, a database, a shell, etc.). The `## Detection Workflow` step 3 explicitly requires "collect any indicators present" — a keyword match alone is insufficient.

### R4 — `source_attribution` Validation Failures on F-1 Findings

**Risk**: F-1 is the first net-new producer of `source_attribution`. If the F-A2 referential-integrity validation (`validate_source_attribution` in `tachi_parsers.py`) rejects an `OI-{N}` finding because of a malformed taxonomy / id / relationship value, the finding fails parser validation and is dropped or surfaced as an error.
**Likelihood**: Low (the F-A2 contract is well-specified; the agent's pattern catalog explicitly lists valid taxonomy IDs from `schemas/taxonomy/owasp.yaml` and `schemas/taxonomy/cwe.yaml`).
**Impact**: High (SC-10 fails; F-1's contribution to F-B's coverage matrix is invisible).
**Mitigation**: The orchestrator's Phase 4 invocation of `validate_source_attribution` (per ADR-028 Decision 5) catches this at parse time. Agent worked examples MUST cite valid IDs from the F-A1 catalogs. Plan stage includes a fixture-test asserting `validate_source_attribution([OI-1, OI-2, ...])` returns no errors.

### R5 — Example Regeneration Surface Larger Than Expected

**Risk**: Regenerating `examples/agentic-app/` with the new agent active surfaces unexpected interactions with Feature 142 agentic-pattern synthesis, Feature 141 cross-layer chains, or other recently-added pipeline phases. The regenerated PDF deviates from expectations beyond the new `OI-{N}` findings alone.
**Likelihood**: Low-medium (the pipeline is well-tested but `agentic-app` is the most complex example).
**Impact**: Medium (may require re-baselining additional artifacts; team-lead schedule absorbs the contingency).
**Mitigation**: Day 3 example regeneration includes a structured pre-vs-post diff review. Acceptable diffs: new `OI-{N}` findings + their cascade effects (risk score, control analysis, attack chain entries). Unexpected diffs (changes to existing finding fields, baseline-status transitions, cross-pipeline drift) require root-cause analysis before merge.

### R6 — `consumers:` Frontmatter Edit Position

**Risk**: ~~Alphabetical insertion mismatch.~~ **Resolved at PRD time per HIGH-2 architect-fix + MEDIUM-1 team-lead-fix**: the `consumers:` list is **not** alphabetical — it uses tier-grouping (orchestrator → STRIDE-canonical → AI-LLM → AI-AG → infra-consumer). Original risk reframed as: misplacing `output-integrity` outside its natural tier-grouping position could obscure the additive-edit-discipline signal for future reviewers.
**Likelihood**: Low (the tier-grouping pattern is documented in FR-3 and verifiable by inspection).
**Impact**: Low (cosmetic; ADR-023 Decision 3 grep check still passes).
**Mitigation**: Plan stage verifies insertion **after `tool-abuse` and before `risk-scorer`** (appended to AI tier) — the natural tier-canonical position for the new AI-LLM-side detection agent.

### R7 — `agentic-app` Already at Capacity for "First Example to Regenerate" Pattern

**Risk**: `agentic-app` has been the regeneration target for Features 084 (MAESTRO), 142 (agentic patterns), 145 (canonical worked example). Repeated regeneration on a single example creates cumulative-state risk — each regeneration baseline reflects the latest agent fleet, and rolling back individual contributions becomes harder over time.
**Likelihood**: Low.
**Impact**: Low.
**Mitigation**: The architect may choose Q4 alternative (extend a different example) if the cumulative-state cost exceeds the convention-preservation benefit. PM-default is `agentic-app`; architect may override.

### R8 — ML09 Bundling Scope

**Risk**: BLP-01 §4 bundles ML09:2023 with LLM05:2025 because both share the output-side signal class. But ML09 covers **predictive-ML output tampering** (a tampered classifier emits wrong labels), while LLM05 covers **generative-LLM output handling** (raw text concatenated into downstream sinks). Adopters may find the bundling unintuitive if pattern categories blur the predictive-vs-generative distinction.
**Likelihood**: Low-medium.
**Impact**: Low (per HIGH-3 architect-fix: ML09 bundling is documentation-only, not pattern-level — `source_attribution` does not carry ML09; pattern primary remains LLM05).
**Mitigation**: Pattern categories detect LLM05 surfaces only. ML09 closure is recorded in ADR-030 + Coverage Matrix as F-1's documentation-only contribution. The companion `detection-patterns.md` `## Overview` section documents the bundling rationale (one paragraph referencing BLP-01 §4) without claiming pattern-level ML09 detection.

### R9 — Heuristic A Outcome A Pattern Category Authoring Time

**Risk**: If Heuristic A resolves Outcome A (subsume ASI09), the sixth pattern category "Human-Trust Exploitation via LLM Output" requires authoring research that the security-analyst agent and architect have not yet front-loaded. This may extend Day 2 pattern authoring by 0.5-1 day.
**Likelihood**: Low-medium (depends on Heuristic A outcome).
**Impact**: Medium (timeline slip; team-lead schedule absorbs).
**Mitigation**: If Outcome A is the architect's leaning at Day 1 AM, the security-analyst agent does parallel research on the human-trust pattern indicators during Day 1 PM, surfacing 3-5 indicators ready for Day 2 authoring. If Outcome B is chosen, no extra research is needed.

---

## 📦 Deliverables Summary

| Artifact | Path | Net change |
|---|---|---|
| New agent file | `.claude/agents/tachi/output-integrity.md` | +new file (≤150 lines) |
| New companion README | `.claude/skills/tachi-output-integrity/README.md` | +new file |
| New pattern catalog | `.claude/skills/tachi-output-integrity/references/detection-patterns.md` | +new file |
| Shared-reference frontmatter edit | `.claude/skills/tachi-shared/references/finding-format-shared.md` | +1 line in `consumers:` list (additive-only per ADR-023 Decision 3) |
| Public ADR | `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` | +new file (Proposed → Accepted dual-commit) |
| Example regeneration | `examples/agentic-app/` (or alternative per Q4) | regenerated artifacts including ≥1 `OI-{N}` finding |
| Backward-compat baselines | `examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/security-report.pdf.baseline` | byte-identical regen under `SOURCE_DATE_EPOCH=1700000000` (no change to committed baselines) |
| Schema | `schemas/finding.yaml` | **MINOR BUMP 1.5 → 1.6** (additive: `id.pattern` regex extended to include `OI` prefix per ADR-026 minor-bump rule; `category: llm` enum unchanged). BLOCKING-2 architect-fix during PRD review. |
| Orchestrator dispatch list | `.claude/agents/tachi/orchestrator.md` | +1 line (add `output-integrity` to dispatch list). HIGH-1 architect-fix during PRD review; carved out from SC-9 22-file invariant. |
| Dispatch rules | `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | +N lines (extend LLM dispatch trio → quartet; add `output-integrity` trigger-keyword rules). HIGH-1 architect-fix; carved out from SC-9. |
| Tests | `tests/scripts/test_output_integrity.py` (or similar) | +new fixture-driven tests for finding emission + `source_attribution` validation |
| Existing 22 detection-tier files | `.claude/agents/tachi/{11 existing}.md` + `.claude/skills/tachi-{11 existing}/references/detection-patterns.md` | **ZERO CHANGES** (SC-9 / ADR-023 lineage invariant) |

---

## 🔁 Open Questions Summary (architect-owned, for /aod.plan)

Architect leanings captured during PRD review listed in the Default column.

| # | Question | Owner | Architect Leaning | Decided By |
|---|---|---|---|---|
| Q1 | ASI09 Heuristic A resolution — Outcome A (subsume) or Outcome B (split / forward-ref F-4)? | architect | **Outcome B (split)** — psychology/linguistics primitives don't fit deterministic pattern-matching | ADR-030, Day 1 Wave 1.0 (hard escalation gate Day 1 EOD per R1) |
| Q2 | Trigger keyword set final form (PRD proposes 7) | architect | curate 8-12 keywords at Plan time | Day 1 plan, refinable Day 2 |
| Q3 | DFD target set: `Process` only, or also `Data Flow`? | architect | `Process` only (precedent-preserving across 11 existing AI agents) | Day 1 plan |
| Q4 | Example regeneration target — `agentic-app` or alternative? | architect | `agentic-app` (Features 084 / 142 / 145 precedent) | Day 1 plan |
| Q5 | ADR-030 sequencing — Proposed Day 1 Wave 1.1 or only Day 3 EOD? | architect | Proposed Day 1 Wave 1.1 (BLP-01 default per ADR-027 / ADR-028 / ADR-029) | Day 1 plan |

---

## 📚 References

- [GitHub Issue #201](https://github.com/davidmatousek/tachi/issues/201) — source of user stories and Tier 1 framing
- [BLP-01 Threat Coverage Blueprint](../../../_internal/strategy/BLP-01-threat-coverage.md) §7 F-1 (private) — full F-1 specification including DoD, Coverage Matrix transitions, governance contract
- [GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy](../../../_internal/strategy/GUIDE-threat-coverage-research.md#11-heuristic-a-signal-class-taxonomy) (private) — worked example for ASI09-into-F-1-or-F-4 decision tree
- [SDR-001 Threat Coverage Strategy](../../../_internal/strategy/SDR-001-threat-coverage-strategy.md) (private) — Option C governance contract: public per-feature ADR with narrow technical scope
- [OWASP LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/) — canonical taxonomy entry
- [OWASP ML09:2023 Output Integrity Attack](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML09_2023-Output_Integrity_Attack) — predictive-ML counterpart bundled per BLP-01 §4
- [OWASP ASI09:2026 Human-Agent Trust Exploitation](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — relevant for Heuristic A scope question
- [ADR-023 Threat Agent Skill References Pattern](../../architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) — lean-agent shape requirements F-1 conforms to
- [ADR-021 SOURCE_DATE_EPOCH Determinism](../../architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) — SC-6 byte-identity gate
- [ADR-027 Taxonomy Crosswalk Schema](../../architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md) — taxonomy enum source
- [ADR-028 Source Attribution Schema Extension](../../architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md) — `source_attribution` contract F-1 produces
- [ADR-029 Coverage Attestation Report Section](../../architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md) — downstream consumer of F-1's `source_attribution` data
- [Feature 082 PRD](./082-threat-agent-skill-references-2026-04-11.md) — 11-agent refactor that produced ADR-023; F-1 is the first net-new agent under that pattern
- [`prompt-injection.md`](../../../.claude/agents/tachi/prompt-injection.md) — structural template for the new agent (5-section canonical shape)
- [`prompt-injection/references/detection-patterns.md`](../../../.claude/skills/tachi-prompt-injection/references/detection-patterns.md) — pattern catalog template
- [`finding-format-shared.md`](../../../.claude/skills/tachi-shared/references/finding-format-shared.md) — canonical finding IR + producer-audience section
- [`severity-bands-shared.md`](../../../.claude/skills/tachi-shared/references/severity-bands-shared.md) — OWASP 3×3 risk matrix
