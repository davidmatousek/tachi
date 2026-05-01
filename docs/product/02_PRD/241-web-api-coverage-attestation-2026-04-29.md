---
prd:
  number: 241
  topic: web-api-coverage-attestation
  created: 2026-04-29
  status: Approved with Concerns
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-29, status: APPROVED, notes: "PRD authored as combined F-8 + F-A3 closure feature for BLP-01 Tier 3 attestation pass per user-selected Option A. Four user stories preserved verbatim from Issue #241 (US-241-1..3) plus added US-241-4 for F-A3 closure. 15 success criteria covering F-A3 wiring (SC-1..3) + F-8 attestation (SC-4..10) + cross-cutting (SC-11..15). 5–6 week timeline accepted per Architect Option A budget. Q-PM-1 carry-forward to Plan stage: ADR-027 D1 record-shape extension may warrant separate ADR alongside combined F-8/F-A3 ADR."}
  architect_signoff: {agent: architect, date: 2026-04-29, status: APPROVED_WITH_CONCERNS, notes: "Third-pass review: all v1.0 BLOCKING + v1.1 HIGH-A + v1.0/v1.1 MEDIUM-A/B resolved. F-A3 scope = 11 hosts; SC-1 + Metric 4 = 14/14 detection agents. SC-14 acknowledges taxonomy YAML record-shape extension. test_pyyaml_deferred_import.py codified per KB-037. 6 NEW LOW findings (residual `9 hosts` / `12 files` prose remnants + 1 constraint-line CONTRADICTION at v1.2 line 486 RESOLVED inline by PM in v1.2 follow-up edit). Zero NEW HIGH/BLOCKING. All backward-compat invariants preserved (F-7 28-file zero-edit invariant for non-target files, has-source-attribution gate reuse, SOURCE_DATE_EPOCH byte-identity for non-target baselines, finding.yaml v1.8, F-A2 5-value enum). Full review: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-29, status: APPROVED_WITH_CONCERNS, notes: "Third-pass review: all v1.1 HIGH-R1 + MEDIUM-R1/2/3 + LOW-R2 resolved. Calendar arithmetic verified Day 1 Thu 4/30 → Day 29 Wed 6/10 = 29 working days = 5.8 weeks (Memorial Day Mon 5/25 correctly skipped). Stream 1 sizing absorbs HIGH-A's +2 hosts within Wave 2 (+1 day extension). 5–6 week budget realistic at optimistic/mid; TIGHT at pessimistic (margin shrinks to 0–0.5wk). All 7 agents within 80%/day cap with pair-authoring. NEW: 1 HIGH-R5 (Wave 2 Day 10–11 SBE concentration spike from closure verification + final wirings — recommend Wave 2 Day 10 task isolation + Day 11 buffer; carry to Plan stage spec.md task IDs), 1 MEDIUM-R4 (stale `9 hosts` prose remnants — RESOLVED inline by PM in v1.2 follow-up), 1 LOW-R3 (pessimistic buffer cushion). Full review: .aod/results/team-lead.md."}
source:
  idea_id: 241
  story_id: null
---

# F-8 + F-A3 — Web/API Coverage Attestation + Populator Wiring [Tier 3]: Product Requirements Document

**Status**: Draft (v1.2 — F-A3 host scope expanded 9 → 11 per Architect HIGH-A 2026-04-29; calendar drift normalized + ADR-027 D1 record-shape extension acknowledged + KB-037 pyyaml deferred-import invariant codified per Architect MEDIUM-A/B + Team-Lead HIGH-R1)
**Created**: 2026-04-29
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 3 — final attestation pass closing the 11-feature initiative (F-A3 populator wiring co-shipped per ADR contingency)
**Priority**: P1 (ICE 22 — I:8 C:7 E:7)

---

## 📋 Executive Summary

### The One-Liner

Run the final attestation pass that proves tachi's existing coverage per-finding inside every PDF security report — by **wiring `source_attribution` populators across the eleven remaining BLP-01 host agents (F-A3 closure: nine BLP-01-enriched STRIDE/AI hosts plus `prompt-injection` and `agent-autonomy` per Architect HIGH-A — aggregator at `extract-report-data.py:1112` reads only `finding.source_attribution[].id`, so implicit prefix-attribution does NOT exist)**, closing the six remaining Partial items in BLP-01 §6 Coverage Matrix with citation evidence (F-8 audit), expanding the MITRE ATT&CK + ATLAS taxonomy YAMLs to full inventories with tactical-grouped Out-of-Scope annotations, and replacing the hand-curated coverage matrix with pipeline-generated per-taxonomy coverage percentages. Turns tachi's one-line success statement *"automatically tells you, per engagement, which OWASP / MITRE / NIST / CWE items it detects and which it misses"* into runtime fact across **all eight example baselines**.

### Problem Statement

BLP-01 is at **10/11 features delivered** as of F-7 (Feature 237, merged 2026-04-29 as `e962a0e`). The OWASP four-framework total stands at **40/40 Covered** for detection — LLM Top 10:2025, Agentic Top 10:2026, ML Top 10:2023, and Mobile Top 10:2024 are all closed at the agent layer. **But the Coverage Attestation rendering surface delivered by F-B (Feature 194) renders empty on five of six baselines** because populator wiring was deferred four features in a row (ADR-032 / ADR-034 D-8 / ADR-035 D-10 / ADR-036 D-10) — only three of fourteen detection agents emit `source_attribution` today (the F-1 / F-2 / F-4 net-new agents). F-B's own Team-Lead delivery note (BLP-01 line 1309) names F-A3 explicitly: *"F-A3 populator wiring is the single remaining gate between the machine-readable coverage contract and adopter-visible attested coverage tables."* **Architect's empirical re-review (v1.1, 2026-04-29) confirmed that the aggregator at `scripts/extract-report-data.py:1112` reads only `finding.source_attribution[].id` — no implicit prefix-attribution path exists. F-A3 wiring must therefore extend to all 11 host agents (the 9 STRIDE/AI agents + `prompt-injection` + `agent-autonomy`) for OWASP LLM01, ASI01, ASI06, ASI08, ASI10, LLM06, and LLM10 to render non-Gap on any baseline.**

The §6 Coverage Matrix also still carries six Partial items across the OWASP Web/API space (A05, A06, API6, API8, API9, API10) plus *unverified* MITRE ATT&CK and ATLAS coverage percentages. Adopters reading a `tachi.security-report` PDF today see no per-framework coverage percentage on any framework page, and no per-finding source attribution rendered for OWASP Web/API or anything else.

The hand-curated §6 Coverage Matrix is also a maintenance liability: every time a new pattern category lands, the matrix must be updated by hand, and the BLP-01 strategic-plan memory becomes the source of truth instead of the codebase. F-A1 (Feature 180) supplied the taxonomy YAML inventory; F-A2 (Feature 189) supplied the `source_attribution` schema; F-B (Feature 194) supplied the rendering surface; F-1 through F-7 supplied the AI/Agentic/ML/Mobile detection coverage. **All upstream dependencies are now satisfied — F-8 + F-A3 runs the audit AND wires the populators across the full set, closing BLP-01 cleanly.**

### Proposed Solution

This combined feature ships as **four coordinated work streams** with no new agent files, no schema shape changes, and no orchestrator phase additions:

1. **F-A3 Populator wiring (Stream 1)** — wire `source_attribution` populators across **eleven** BLP-01 host agents that have never emitted `source_attribution`: the nine STRIDE/AI hosts (`tachi-spoofing`, `tachi-tampering`, `tachi-info-disclosure`, `tachi-privilege-escalation`, `tachi-repudiation`, `tachi-denial-of-service`, `tachi-tool-abuse`, `tachi-data-poisoning`, `tachi-model-theft`) plus `tachi-prompt-injection` and `tachi-agent-autonomy` (per Architect v1.1 HIGH-A — aggregator semantics confirmed at `scripts/extract-report-data.py:1112`; no implicit-prefix path exists). Each agent gains inline `source_attribution` examples in its detection workflow consistent with F-1/F-2/F-4 net-new agent precedent (`primary` taxonomy citation per pattern category + `related`/`derived` cross-citations where applicable). Strict adherence to the F-A2 schema enum, the ADR-027 7-value taxonomy catalog, and the F-7 28-file zero-edit invariant on non-detection-tier files outside F-A3 scope. Result: 14 of 14 detection-tier agents emit `source_attribution`.

2. **Six Partial Item completeness-verification (Stream 2)** — additive Primary Source blocks and at most one new Indicator category per Partial item, applied to existing skill-reference `detection-patterns.md` files (`tachi-privilege-escalation`, `tachi-info-disclosure`, `tachi-tampering`, and others as the audit dictates). For each of A05, A06, API6, API8, API9, API10: either close to Covered with a concrete pattern-category pointer + citation-grounded Primary Source block, OR explicitly defer with a new ADR rationale and a follow-on Issue. Architect skim adjudicated 4/6 closeable under existing patterns (A05, A06, API8, API10) and 2/6 (API6 Unrestricted Access to Sensitive Business Flows + API9 Improper Inventory Management) likely require new Indicator categories. Both remain in scope per the *"at most one new Indicator category per Partial item"* allowance. Preserves the Feature 082 / ADR-023 detection-variant contract and stays within tier-cap line counts.

3. **Taxonomy YAML expansion (Stream 3)** — expand `schemas/taxonomy/mitre-attack.yaml` from F-A1's 38-technique seed to the full Enterprise item inventory using **tactical-grouping Out-of-Scope strategy** (architect HIGH adjudication on Q-Architect-3): one Out-of-Scope annotation per ATT&CK tactic group whose threat surface lies outside tachi's design-time scope (e.g., TA0005 Defense Evasion, TA0007 Discovery, TA0008 Lateral Movement, TA0009 Collection, TA0010 Exfiltration, TA0011 Command and Control, TA0040 Impact — runtime/IR layer, not design-time). Per-item Out-of-Scope rationale only on items inside in-scope tactics. Expand `schemas/taxonomy/mitre-atlas.yaml` from F-A1's 7-technique seed to the full ATLAS item inventory; populate `schemas/taxonomy/owasp.yaml` with full A01–A10 + API1–API10 attestation entries — every item attested by at least one agent-plus-pattern-category citation per BLP-01 §8 quality bar.

4. **Report rendering verification (Stream 4)** — extend `scripts/extract-report-data.py` (the F-B aggregator) with pipeline-generated per-framework coverage-percentage computation: `% coverage per taxonomy = |cited_ids| / |taxonomy_ids_not_out_of_scope|`. Surface results via the existing F-B `has-source-attribution` boolean plus new per-framework coverage-percentage Typst variables. Exercise `templates/tachi/security-report/coverage-attestation.typ` end-to-end on **eight example architectures** (the original six plus F-6's `predictive-ml-app` and F-7's `mobile-banking-app`, per Architect Q-Architect-4 MEDIUM finding — otherwise Mobile/ML Top 10 attestation renders 0% Covered on every baseline despite the F-6/F-7 enrichment work) and intentionally update the eight `security-report.pdf.baseline` files under `SOURCE_DATE_EPOCH=1700000000`.

**Three things this combined feature is deliberately NOT:**

1. It is **not** a new threat agent. F-8 + F-A3 is attestation + populator wiring, not enrichment — net-new detection patterns are out of scope unless a Partial item's closure requires a citation-grounded category addition (FR-2 allowance). The F-7 28-file zero-edit-invariant on the detection-tier inventory carries forward (modulo additive `source_attribution` populator edits across 9 agents + Primary Source / Indicator edits to the Partial-item `detection-patterns.md` files).
2. It is **not** a `finding.yaml` schema shape change. `schemas/finding.yaml` v1.8 is preserved; F-8 + F-A3 reuses existing `S/T/I/E/R/AG/LLM/AGP/OI/MI/TE` finding-ID prefixes. **Sixth BLP-01 detection-tier feature with zero `finding.yaml` schema bump** (after F-3 + F-5 + F-6 + F-7). However, **`schemas/taxonomy/*.yaml` records DO gain two new fields** (`out_of_scope: bool` + `out_of_scope_rationale: string`) per Architect MEDIUM-A — this is a record-shape extension to F-A1's ADR-027 D1 contract. The new public per-feature ADR (or its companion sub-ADR) explicitly acknowledges and accepts this extension. The F-A1 taxonomy YAMLs are *populated AND minimally extended*, not redefined.
3. It is **not** a cross-framework reasoning surface. F-B ADR-029 narrowed MVP to per-framework intra-taxonomy attestation; F-8 + F-A3 *populates* that surface rather than expanding it. The crosswalk JOIN remains out-of-MVP scope.

### Success Criteria

#### F-A3 populator-wiring success criteria (Stream 1)

- **SC-1** — All eleven target host agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`, `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`) emit `source_attribution` inline per the F-1/F-2/F-4 net-new agent precedent. Verified via `grep -l "source_attribution" .claude/agents/tachi/*.md` returning **14 of 14** detection-tier files (the original 3 net-new agents + the 11 newly wired). No detection-tier agent remains in F-A3 deferral after this feature.
- **SC-2** — Every BLP-01 host-agent enrichment-feature populates `source_attribution` to at least the **primary** taxonomy citation per pattern category surfaced in F-1 through F-7 detection workflows.
- **SC-3** — Populator wiring is additive only — no functional changes to existing detection logic on the nine target agents; line-count cap from ADR-036 baseline-line-count contract preserved (no host agent exceeds 200 lines).

#### F-8 attestation success criteria (Streams 2–4)

- **SC-4** — Zero Planned items remain in BLP-01 §6 Coverage Matrix across every adopted taxonomy.
- **SC-5** — Zero Partial items remain without an associated open PRD or an explicit deferral note with ADR rationale. Each of A05, A06, API6, API8, API9, API10 is either Covered (with citation evidence) or explicitly Deferred (with ADR + follow-on Issue).
- **SC-6** — Every Covered item in §6 cites at least one tachi agent and at least one detection-pattern category — verified by audit script that walks `schemas/taxonomy/owasp.yaml` and resolves each citation.
- **SC-7** — The F-B Coverage Attestation section renders end-to-end in **all eight example `security-report.pdf` outputs** with non-empty per-finding attribution tables and non-zero coverage-percentage values per taxonomy. Eight examples = `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`, `predictive-ml-app`, `mobile-banking-app` (Architect Q-Architect-4 MEDIUM resolution).
- **SC-8** — `schemas/taxonomy/mitre-attack.yaml` and `schemas/taxonomy/mitre-atlas.yaml` contain the full item inventories. ATT&CK uses **tactical-grouping Out-of-Scope strategy** (per Architect HIGH Q-Architect-3): 5–7 tactic-level Out-of-Scope rationales for design-time-irrelevant tactics, plus per-item Out-of-Scope rationale only on items inside in-scope tactics.
- **SC-9** — Per-framework coverage percentages published in the PDF match those computed against the taxonomy YAML inventories (denominator = `|taxonomy_ids_not_out_of_scope|`; numerator = `|cited_ids|`). Verification: regenerate `security-report.pdf` and cross-check coverage-percent values against an offline audit script.
- **SC-10** — BLP-01 §6 Coverage Matrix is annotated *"historical — superseded by pipeline-generated attestation"* with a pointer to the F-B section. The matrix is no longer the source of truth for coverage claims.

#### Cross-cutting success criteria

- **SC-11** — Public per-feature ADR (next available number) is committed (Proposed → Accepted dual-commit pattern) documenting the combined attestation + populator-wiring scope, the six Partial→Covered reclassifications with their evidence trail, the ATT&CK and ATLAS coverage percentages with their tactical-grouping Out-of-Scope rationale, the F-A3 populator-wiring closure, the eight-baseline scope expansion (Q-Architect-4), and any explicit deferrals with follow-on Issues.
- **SC-12** — Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
- **SC-13** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **SC-14** — `schemas/finding.yaml` unchanged at v1.8 (zero `finding.yaml` shape change). `schemas/taxonomy/*.yaml` record shape gains exactly two new fields (`out_of_scope: bool` default `false`, `out_of_scope_rationale: string` default empty) — this minimal record-shape extension to F-A1's ADR-027 D1 contract is acknowledged and accepted in the new public ADR per Architect MEDIUM-A. Existing F-A1 records that omit these fields parse correctly under the YAML defaults (backward-compat preserved).
- **SC-15** — Existing baselines that previously regenerated byte-identically continue to do so under `SOURCE_DATE_EPOCH=1700000000`, **except** for the eight `security-report.pdf.baseline` files that are intentionally updated with the populated Coverage Attestation section. The intentional update is explicit and documented in the per-feature ADR.

### Timeline

Target: **5–6 working weeks** of active implementation (Architect Option A budget). 5 weeks for the optimistic path with all six Partial items closing cleanly, 6 weeks if 1–2 Partial items defer or if Stream 1 (F-A3 across 11 hosts) hits a per-host pattern-category surface that triggers a meaningful Indicator-tier rewrite.

Delivery window: 2026-04-30 (Day 1) → 2026-06-09 (Tue, Week 6 close), avoiding US Memorial Day (2026-05-25 Mon) within the active build window. Team-Lead's 3.5-week buffer-floor logic applies to the F-8-only scope; with F-A3 added, the floor expands proportionally to 5–6 weeks per Architect's Option A guidance.

The four work streams admit some parallelism: **Stream 1 (F-A3 wiring) and Stream 2 (Partial item audit) advance independently**; Stream 3 (taxonomy expansion) can advance in parallel with Stream 1 + Stream 2; Stream 4 (rendering verification) depends on Streams 1 + 3 completing.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)

tachi's vision — *"Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications"* — is fulfilled in detection (F-1 through F-7), in data (F-A1 + F-A2), and in rendering surface (F-B). F-8 + F-A3 closes the loop by making the BLP-01 one-line success statement true at runtime: *"Tachi automatically tells you, per engagement, which OWASP / MITRE / NIST / CWE items it detects and which it misses."* Adopters evaluating "does tachi cover the frameworks my compliance program needs?" get an honest, per-engagement, machine-generated answer in the PDF — not a marketing claim, not a hand-maintained matrix, not an empty Coverage Attestation section that demonstrates the surface but not the substance.

### BLP-01 Initiative Fit

F-8 + F-A3 is the **Tier 3 attestation pass + Foundation populator-wiring closure** — the final feature in the 11-feature BLP-01 initiative.

```
Tier 0 — Foundation (delivered, except F-A3 deferred 4 times):
  F-A1 (Feature 180, delivered 2026-04-17) — taxonomy YAMLs (supply side)
  F-A2 (Feature 189, delivered 2026-04-17) — source_attribution schema field (demand contract)
  F-B  (Feature 194, delivered 2026-04-18) — Coverage Attestation rendering surface
  F-A3 (DEFERRED 4 features in a row — pulled into THIS PRD per Option A) — populator wiring across 11 hosts (9 STRIDE/AI + prompt-injection + agent-autonomy per Architect HIGH-A)
       │
Tier 1 — AI/Agentic detection coverage (5 features, all delivered):
  F-1 → F-5 — output-integrity, misinformation, tool-abuse enrichment, human-trust-exploitation, LLM10 unbounded consumption
       │
Tier 2 — ML & Mobile detection coverage (2 features, both delivered):
  F-6 — ML Top 10:2023 closure (Feature 232, 2026-04-27)
  F-7 — Mobile Top 10:2024 closure (Feature 237, 2026-04-29)
       │
Tier 3 — Attestation pass (this PRD, #241) co-shipped with F-A3:
  F-8 — Web/API Coverage Attestation
  F-A3 — Populator Wiring (11 hosts; 14/14 detection-tier coverage; accumulated debt cleared)
```

F-A3 deferral lineage (4 ADRs in a row, codified rule):

| ADR | Feature | F-A3 deferral language |
|-----|---------|------------------------|
| ADR-032 | F-3 (`tool-abuse`) | First enrichment-branch defer |
| ADR-034 D-8 | F-5 (`denial-of-service` + `model-theft`) | "F-5 is the first BLP-01 detection feature to defer populator wiring" |
| ADR-035 D-10 | F-6 (`tampering` + `data-poisoning` + `model-theft`) | "F-6 is the second BLP-01 detection feature to defer populator wiring" |
| ADR-036 D-10 | F-7 (5 STRIDE host agents) | "F-7 is the third BLP-01 detection feature to defer populator wiring. Cumulative scope: F-A3 owns populator wiring across 9 unique hosts." |

This PRD is the closure ADR-NNN that resolves the 4-feature deferral chain.

### Recent ADR Lineage

- **ADR-027** (Feature 180, F-A1): establishes the 7-value taxonomy catalog. F-8 + F-A3 expands the *content* of 3 of those YAMLs (`mitre-attack.yaml`, `mitre-atlas.yaml`, `owasp.yaml`) without altering the catalog shape.
- **ADR-028** (Feature 189, F-A2): establishes the `source_attribution` 5-value taxonomy enum with `relationship` 3-value discrimination. Stream 1 (F-A3 wiring) and Stream 4 (rendering) both consume this contract.
- **ADR-029** (Feature 194, F-B): establishes the conditional-inclusion + 3-value classification (Covered / Partial / Gap) MVP. F-8 + F-A3 *populates* the renderer with non-zero values rather than altering the rendering contract.
- **ADR-030 → ADR-036** (F-1 through F-7 detection coverage): each closes one or more OWASP family entries. F-A3 retroactively wires the populator output for the 9 host agents enriched across this lineage.

### Roadmap Fit

- **Phase**: BLP-01 Tier 3 — final closure feature (combined with Foundation F-A3 closure)
- **Week**: Week of 2026-04-30 onwards (5–6 weeks active build)
- **Dependencies**:
  - F-A1 (Feature 180) — **SATISFIED** as of 2026-04-17 (taxonomy YAML inventory)
  - F-A2 (Feature 189) — **SATISFIED** as of 2026-04-17 (source_attribution schema)
  - F-B (Feature 194) — **SATISFIED** as of 2026-04-18 (rendering surface)
  - F-1 through F-7 — **ALL SATISFIED** as of 2026-04-29 (40/40 OWASP four-framework detection coverage)

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **Compliance-Driven Adopter**

- **Role**: CISO, security auditor, risk committee member, or compliance engineer using tachi output to feed a compliance program (SOC 2, ISO 27001, PCI DSS, HIPAA, NIST 800-53, EU AI Act)
- **Goal**: Trace tachi findings back to the frameworks their compliance program already uses (OWASP Top 10, OWASP API Top 10, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE) without re-authoring the mapping
- **Pain Point Today**: tachi's PDF reports already carry findings, but the Coverage Attestation section renders empty on most baselines (F-A3 deferred 4×) and per-finding source attribution is missing for OWASP Web/API. Compliance reviewers must re-author the mapping by hand.
- **Value Delivered**: Every finding renders machine-readable source attribution; every framework page renders an honest coverage percentage with explicit gaps. Compliance reviewers re-frame tachi output against their framework without re-running the pipeline.

### Secondary Persona: **tachi Maintainer**

- **Role**: tachi maintainer closing the BLP-01 initiative
- **Goal**: Retire the hand-maintained §6 Coverage Matrix; clear the 4-feature F-A3 deferral debt; make coverage claims data-driven and PR-reviewable; ensure future threat-coverage features inherit the attestation surface for free
- **Pain Point Today**: §6 Coverage Matrix is the source of truth for coverage claims, but updating it is hand-curation work. Future pattern-category additions to `detection-patterns.md` files don't automatically propagate to the matrix because populator wiring is missing on 9 host agents.
- **Value Delivered**: Coverage is machine-generated from `schemas/taxonomy/*.yaml` × finding `source_attribution` arrays. With F-A3 wired, any new pattern category with a Primary Source block automatically feeds the Coverage Attestation section. Coverage expansion no longer requires blueprint-level bookkeeping.

### Tertiary Persona: **Future Contributor**

- **Role**: External contributor adding a new pattern category or new detection agent
- **Goal**: Understand which frameworks tachi covers without reading the full `_internal/strategy/BLP-01-threat-coverage.md` blueprint
- **Pain Point Today**: Coverage claims live in private strategic-plan memory; contributors lack a public, machine-readable signal of "what's covered, what's partial, what's a gap."
- **Value Delivered**: `schemas/taxonomy/*.yaml` + the F-B Coverage Attestation section in any sample PDF gives contributors a public, data-driven coverage view. The §6 Coverage Matrix annotation pointing to the F-B section makes this explicit.

---

## 📖 User Stories

The three F-8 user stories are preserved verbatim from GitHub Issue #241. A fourth story (US-241-4) is added for the F-A3 populator-wiring scope per Architect Q-Architect-1 BLOCKING resolution.

### US-241-1: Per-Finding Source Attribution Renders in PDF

**When** a tachi adopter reviews a generated `tachi.security-report` PDF and wants stakeholders (CISOs, auditors, risk committees) to trace tachi findings back to the frameworks their compliance programs already use,
**I want to** see every finding's source attribution rendered in the PDF Coverage Attestation section, machine-readable across OWASP Top 10 / API Top 10 / MITRE ATT&CK / MITRE ATLAS / CWE,
**So I can** hand the PDF to my compliance team without re-authoring the framework mapping by hand.

**Acceptance Criteria**:
- **Given** a finding with populated `source_attribution` for OWASP Top 10:2021 (e.g., A01) or API Top 10:2023 (e.g., API1), **when** the per-finding attribution table renders in the PDF, **then** the OWASP cell carries the correct ID with `relationship: primary` rendered bold and `related`/`derived` plain — same rendering contract as F-B.
- **Given** the aggregate Coverage Attestation matrix, **when** the OWASP page renders, **then** all 10 OWASP Top 10:2021 entries (A01–A10) carry visible classification (Covered / Partial / Gap) and a per-framework coverage percentage matching the manual audit script.
- **Given** any of the eight example architectures, **when** `tachi.security-report` runs, **then** the Coverage Attestation section is non-empty (per-finding attribution table has ≥1 row + per-framework coverage-percentage values are non-zero on at least the framework families served by the architecture's detection-tier coverage).

**Priority**: P0
**Effort**: M

### US-241-2: Six Partial Items Close to Covered with Citation Evidence

**When** a tachi maintainer wants the BLP-01 §6 Coverage Matrix to have zero unexplained Partial items,
**I want to** see each of the six Partial Web/API items (A05, A06, API6, API8, API9, API10) re-classified with citation evidence,
**So I can** satisfy the BLP-01 §8 Coverage Matrix Quality Bar that every Covered item cites ≥1 agent and ≥1 detection-pattern category.

**Acceptance Criteria**:
- **Given** A05, A06, API8, API10 (Architect Q2-validated as closeable under existing patterns), **when** the audit completes, **then** each item is Covered with a Primary Source block addition + Indicator extension on the affected `detection-patterns.md` file, OR explicitly Deferred with a new ADR rationale + follow-on Issue.
- **Given** API6, API9 (Architect Q2 flagged as likely requiring new Indicator categories per the *"at most one new Indicator category per Partial item"* allowance), **when** the audit completes, **then** each item is Covered via a new Indicator category in the affected `detection-patterns.md` file (target hosts: `tachi-tool-abuse` or `tachi-privilege-escalation` for API6; `tachi-info-disclosure` or `tachi-repudiation` for API9), OR explicitly Deferred with a new ADR rationale + follow-on Issue.
- **Given** any newly-closed Partial item, **when** running tachi on a representative example architecture (`web-app`, `microservices`, or `ascii-web-api`), **then** at least one finding's `source_attribution` resolves to that OWASP Top 10 or API Top 10 ID per `schemas/taxonomy/owasp.yaml`.
- **Given** the completeness-verification commits, **when** reviewed against the F-7 28-file post-merge inventory, **then** they are additive against existing skill reference files — no new agent files, no schema shape changes beyond what F-A2 already landed.

**Priority**: P0
**Effort**: L

### US-241-3: §6 Coverage Matrix Demoted to Historical; Pipeline-Generated Attestation Takes Over

**When** a tachi maintainer or future contributor wants to know "what fraction of MITRE ATT&CK does tachi cover?",
**I want to** see the answer rendered in the F-B Coverage Attestation section as a pipeline-generated coverage percentage with explicit gaps and Out-of-Scope annotations,
**So I can** trust the answer is data-driven (computed from `schemas/taxonomy/*.yaml` × finding `source_attribution`) and PR-reviewable rather than hand-maintained blueprint prose.

**Acceptance Criteria**:
- **Given** the populated `schemas/taxonomy/mitre-attack.yaml` and `schemas/taxonomy/mitre-atlas.yaml` with full item inventories + tactical-grouped Out-of-Scope annotations, **when** `extract-report-data.py` runs, **then** it computes per-framework coverage percentage as `|cited_ids| / |taxonomy_ids_not_out_of_scope|` and emits values to the Typst data contract.
- **Given** the per-framework coverage percentage, **when** the F-B Coverage Attestation page renders, **then** the percentage matches the manual audit-script computation and the Partial / Gap counts render alongside per F-B's Q1-A resolution.
- **Given** the BLP-01 §6 Coverage Matrix, **when** F-8 + F-A3 closes, **then** the matrix is annotated *"historical — superseded by pipeline-generated attestation"* with a pointer to the F-B section.
- **Given** a future pattern-category addition to any `detection-patterns.md` with a Primary Source block, **when** that finding category is invoked on a downstream architecture, **then** the resulting finding's `source_attribution` automatically feeds the Coverage Attestation section without blueprint-level bookkeeping.

**Priority**: P0
**Effort**: M

### US-241-4: Populator Wiring Closes the F-A3 Deferral Debt

**When** a tachi maintainer runs `tachi.security-report` on any architecture whose findings come from one of the eleven BLP-01 host agents (the nine STRIDE/AI hosts plus `prompt-injection` and `agent-autonomy`),
**I want to** see those findings emit `source_attribution` arrays in their `threats.md` Section 9 YAML output (per ADR-028),
**So I can** drive non-zero per-framework coverage percentages on every framework page tachi attests to (not just the LLM/Agentic surfaces served by F-1/F-2/F-4).

**Acceptance Criteria**:
- **Given** any of the eleven target host agents, **when** the agent emits a finding for any pattern category in its `references/detection-patterns.md`, **then** the finding's `source_attribution` array is populated with at least one `primary` taxonomy citation per the F-1/F-2/F-4 net-new agent precedent.
- **Given** the populator wiring across eleven host agents, **when** the seven non-AI baselines are regenerated, **then** the Coverage Attestation section renders non-empty per-finding attribution tables on each baseline (subject to the architecture's actual detection-tier coverage — e.g., `web-app` exercises STRIDE agents extensively, so the OWASP page renders meaningful coverage; `mobile-banking-app` exercises mobile-specific Indicators, so the OWASP Mobile page renders meaningful coverage).
- **Given** a populator wiring change to all eleven host agents, **when** `grep -l "source_attribution" .claude/agents/tachi/*.md` runs, **then** the count of agents emitting `source_attribution` increases from 3 (F-1/F-2/F-4) to **14 of 14** detection-tier agents (per Architect v1.1 HIGH-A — `prompt-injection` and `agent-autonomy` MUST be wired explicitly because the aggregator at `extract-report-data.py:1112` reads only `finding.source_attribution[].id` with no implicit-prefix path).

**Priority**: P0
**Effort**: L

---

## ⚙️ Functional Requirements

### Core Capabilities

#### FR-1: F-A3 Populator Wiring Across Eleven Host Agents (Stream 1)

**Description**: Wire `source_attribution` populators inline in the Detection Workflow section of each of the eleven target host agents. Each agent gains:
- An explicit `source_attribution` example block in the agent's Detection Workflow Step 5 (References) showing how to populate the array per pattern category
- A reference to the F-A2 schema field with the Pattern Category → Primary Source taxonomy citation map (already present in companion `references/detection-patterns.md` files post-F-7)
- An additive paragraph explaining the F-A3 closure pattern for future contributors

**Eleven host scope** (per Architect v1.1 HIGH-A): nine STRIDE/AI hosts (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`, `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`) plus `prompt-injection` (LLM01 attribution) and `agent-autonomy` (ASI01/06/08/10 + LLM06 attribution).

**Inputs**: Existing 11 host agent files + corresponding `references/detection-patterns.md` Pattern Category → Primary Source maps
**Processing**: Additive edits to host agent files (estimate: 20–40 net new lines per agent within ADR-036 line-count cap)
**Outputs**: 11 updated host agent files; verified via `grep -l "source_attribution"` returning 14 of 14 detection-tier agent files

**Anti-pattern guard**: NO functional changes to existing detection logic. NO removal of existing pattern categories. The wiring is purely additive in how the agent emits findings.

#### FR-2: Six Partial Item Audit (Stream 2)

**Description**: For each of A05, A06, API6, API8, API9, API10, audit existing detection-pattern coverage against the OWASP Top 10:2021 / OWASP API Top 10:2023 specs. Decide closure path:

| Item | Architect Q2 Adjudication | Closure Path |
|------|--------------------------|--------------|
| A05 Security Misconfiguration | CLOSEABLE existing pattern | Primary Source addition + non-mobile Indicator extension on `tachi-privilege-escalation` Pattern Category 11 |
| A06 Vulnerable and Outdated Components | CLOSEABLE existing pattern | Primary Source block on `tachi-tampering` Pattern Category 8 (Software Supply Chain Integrity Failures) |
| API6 Unrestricted Access to Sensitive Business Flows | NEW INDICATOR CATEGORY | New Indicator category in `tachi-tool-abuse` or `tachi-privilege-escalation` |
| API8 Security Misconfiguration | CLOSEABLE existing pattern | API-specific Indicator extension on Pattern Category 11 |
| API9 Improper Inventory Management | NEW INDICATOR CATEGORY | New Indicator category in `tachi-info-disclosure` or `tachi-repudiation` |
| API10 Unsafe Consumption of APIs | CLOSEABLE existing pattern | Primary Source + cross-reference on `tachi-tampering` Pattern Category 9 (Injection) and `tachi-info-disclosure` Pattern Category 7 (SSRF) |

**Inputs**: GUIDE-threat-coverage-research §5/§6 specs + current `detection-patterns.md` files
**Processing**: Manual audit + minor citation-grounded edits (4 closures via Primary Source addition + 2 closures via new Indicator categories)
**Outputs**: Updated `detection-patterns.md` files + ADR documenting closure decisions

#### FR-3: Taxonomy YAML Expansion with Tactical-Grouping (Stream 3)

**Description**: Expand three taxonomy YAMLs from F-A1 seeds to full inventories:
- `schemas/taxonomy/mitre-attack.yaml`: 38 → full ATT&CK Enterprise item inventory (~600 records per Architect Q3) with **tactical-grouping Out-of-Scope strategy**: per-tactic Out-of-Scope rationale on tactics whose threat surface lies outside design-time scope (TA0005 Defense Evasion, TA0007 Discovery, TA0008 Lateral Movement, TA0009 Collection, TA0010 Exfiltration, TA0011 Command and Control, TA0040 Impact). Per-item Out-of-Scope rationale only on items inside in-scope tactics.
- `schemas/taxonomy/mitre-atlas.yaml`: 7 → full ATLAS item inventory with per-item Out-of-Scope annotations (smaller scale; per-item rationale acceptable)
- `schemas/taxonomy/owasp.yaml`: full A01–A10 + API1–API10 entries with every Covered item attesting at least one agent + one detection-pattern category citation

**Inputs**: MITRE ATT&CK Enterprise matrix, MITRE ATLAS matrix, OWASP Top 10:2021, OWASP API Top 10:2023
**Processing**: F-A1 curation contract — schema-conformant YAML records
**Outputs**: Full-inventory YAML files with tactical-grouping (ATT&CK) and per-item (ATLAS, OWASP) Out-of-Scope annotations

**Out-of-Scope rule**: An item or tactic is annotated `out_of_scope: true` with `out_of_scope_rationale: "..."` iff the item's threat surface lies outside tachi's design-time threat-modeling scope (e.g., ATT&CK post-exploitation persistence techniques operating at runtime/IR layer).

#### FR-4: Pipeline-Generated Coverage Percentage (Stream 4)

**Description**: Extend `scripts/extract-report-data.py` with per-framework coverage-percentage computation: for each of 5 framework taxonomies, compute `% coverage = |cited_ids| / |taxonomy_ids_not_out_of_scope|` and emit per-framework Typst variables consumed by `coverage-attestation.typ`.

**Inputs**: Populated `schemas/taxonomy/*.yaml` + parsed `source_attribution` arrays from `parse_threats_findings`
**Processing**: Set-difference computation + tactical-grouping-aware Out-of-Scope filter applied at denominator
**Outputs**: Typst data contract carries new per-framework coverage-percentage variables (e.g., `owasp-coverage-percent`, `mitre-attack-coverage-percent`, `mitre-atlas-coverage-percent`); existing F-B `has-source-attribution` boolean retained as the conditional-inclusion gate.

#### FR-5: Eight Example Baseline Regen (Stream 4)

**Description**: All eight example outputs under `examples/` regenerated end-to-end to exercise F-B + F-8 + F-A3 together; eight `security-report.pdf.baseline` files intentionally updated under `SOURCE_DATE_EPOCH=1700000000`.

Eight examples = original six (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) plus F-6's `predictive-ml-app` and F-7's `mobile-banking-app` (per Architect Q-Architect-4 MEDIUM finding — without these two, Mobile Top 10 and ML Top 10 attestation render 0% Covered everywhere despite the F-6/F-7 enrichment work).

**Inputs**: Populated taxonomies + finding `source_attribution` arrays (post-F-A3) + F-B rendering contract
**Processing**: Standard regen via `make regenerate` (or per-example `tachi.security-report` invocation)
**Outputs**: Eight updated baseline PDFs + eight updated `report-data.typ` data files

#### FR-6: §6 Coverage Matrix Demotion

**Description**: Annotate BLP-01 §6 Coverage Matrix with *"historical — superseded by pipeline-generated attestation"* + pointer to F-B section. Matrix is no longer the source of truth.

#### FR-7: Public Per-Feature ADR

**Description**: Public per-feature ADR (next available number) committed Proposed→Accepted via the dual-commit pattern. ADR documents:
- The combined attestation + populator-wiring scope
- The four coordinated work streams
- F-A3 closure across 9 host agents (clearing 4-feature deferral debt accumulated across ADR-032 / ADR-034 D-8 / ADR-035 D-10 / ADR-036 D-10)
- Six Partial→Covered reclassifications with their evidence trail
- ATT&CK and ATLAS coverage percentages with their tactical-grouping Out-of-Scope rationale
- Eight-baseline scope expansion (Q-Architect-4)
- Any explicit deferrals with follow-on Issues

### Data Requirements

**Touched files** (estimated):

**F-A3 Stream 1 (11 host agents + companion catalogs as needed)**:
- `.claude/agents/tachi/spoofing.md` (additive `source_attribution` populator block)
- `.claude/agents/tachi/tampering.md`
- `.claude/agents/tachi/info-disclosure.md`
- `.claude/agents/tachi/privilege-escalation.md`
- `.claude/agents/tachi/repudiation.md`
- `.claude/agents/tachi/denial-of-service.md`
- `.claude/agents/tachi/tool-abuse.md`
- `.claude/agents/tachi/data-poisoning.md`
- `.claude/agents/tachi/model-theft.md`
- `.claude/agents/tachi/prompt-injection.md` (added per Architect v1.1 HIGH-A)
- `.claude/agents/tachi/agent-autonomy.md` (added per Architect v1.1 HIGH-A)

**F-8 Stream 2 (Partial item audit)**:
- `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` (A05, API8 Primary Source / Indicator extension)
- `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` (API9 likely new Indicator category, API10 SSRF cross-reference)
- `.claude/skills/tachi-tampering/references/detection-patterns.md` (A06 Primary Source, API10 Injection cross-reference)
- `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` (API6 likely new Indicator category)
- `.claude/skills/tachi-repudiation/references/detection-patterns.md` (alternate API9 host candidate)

**F-8 Stream 3 (taxonomy expansion)**:
- `schemas/taxonomy/owasp.yaml` (content expansion)
- `schemas/taxonomy/mitre-attack.yaml` (content expansion: 38 → full Enterprise with tactical-grouping)
- `schemas/taxonomy/mitre-atlas.yaml` (content expansion: 7 → full ATLAS)

**F-8 Stream 4 (rendering)**:
- `scripts/extract-report-data.py` (per-framework coverage-percentage computation)
- 8 `examples/*/security-report.pdf.baseline` files (intentional baseline update)
- 8 `examples/*/report-data.typ` files (regen artifact)

**Closure**:
- `_internal/strategy/BLP-01-threat-coverage.md` (§6 Coverage Matrix demotion annotation)
- `docs/architecture/02_ADRs/ADR-NNN-web-api-coverage-attestation-and-populator-wiring.md` (new public ADR)
- New `tests/scripts/test_coverage_attestation_audit.py`
- New `tests/scripts/test_coverage_percentage_computation.py`
- New `tests/scripts/test_f_a3_populator_wiring.py` (verifies 14 of 14 agents emit `source_attribution`)
- New `tests/scripts/test_pyyaml_deferred_import.py` (per Architect MEDIUM-B / KB-037 — asserts `import yaml` remains inside function bodies in `extract-report-data.py`, NOT at module level, protecting the Feature 128 stdlib-only runtime-script invariant)

**Out-of-Scope file edits**:
- No new agent files
- No `schemas/finding.yaml` edits (schema unchanged at 1.8)
- No orchestrator or dispatch-layer edits
- No new pattern categories beyond at most one Indicator category per Partial item (FR-2 allowance)

### Validation Rules

- **F-A3 wiring audit**: New `tests/scripts/test_f_a3_populator_wiring.py` verifies `grep -l "source_attribution" .claude/agents/tachi/*.md` returns **14 files** (3 pre-existing F-1/F-2/F-4 + 11 newly wired per Architect HIGH-A).
- **Coverage attestation audit**: New `tests/scripts/test_coverage_attestation_audit.py` walks `schemas/taxonomy/*.yaml`, resolves each citation to an existing agent + detection-pattern category, and asserts SC-6.
- **Coverage-percentage cross-check**: New `tests/scripts/test_coverage_percentage_computation.py` independently computes `% coverage = |cited_ids| / |taxonomy_ids_not_out_of_scope|` for each framework against fixture findings; asserts equality with values emitted to the Typst data contract.
- **Baseline byte-identity**: SC-15 — eight baseline PDFs intentionally updated; non-Coverage-Attestation pages of the PDF remain byte-identical when `SOURCE_DATE_EPOCH=1700000000` is held constant.

---

## 🚀 Non-Functional Requirements

### Performance Requirements

- **Pipeline regen impact**: Coverage-percentage computation adds <2s to `extract-report-data.py` runtime per example (set-difference computation over ~700 total taxonomy items with tactical-grouping applied).
- **YAML parse overhead**: Full-inventory ATT&CK YAML may carry 600+ records; parse + index at extraction time should remain <500ms per framework.

### Reliability Requirements

- **Backward compatibility**: F-8 + F-A3 is additive — pre-feature PDF baselines for non-example architectures (i.e., adopter-run pipelines) continue to work; the F-B `has-source-attribution` gate ensures the section is omitted when findings carry no attributions.
- **Out-of-Scope honesty**: Tactical-grouping Out-of-Scope annotations must be defensible — every `out_of_scope: true` tactic carries a documented rationale that an external reviewer (architect, security auditor) could audit.

### Security Requirements

- **No PII**: Taxonomy YAMLs carry no PII; example architectures use synthetic data only.
- **No secrets**: No environment variables, no credentials, no internal infrastructure references in the public ADR or YAMLs.
- **`_internal/` privacy**: §6 Coverage Matrix demotion lives inside `_internal/strategy/BLP-01-threat-coverage.md` (gitignored). Public-facing artifacts (ADR, YAMLs, PDF, F-B section) carry no commercial framing per [SDR-001](../../../_internal/strategy/SDR-001-threat-coverage-strategy.md) Option C governance contract.

### Accessibility Requirements

- **WCAG AA preserved**: F-B's color+icon Gap highlighting (Q5 ux-ui-designer memo) remains in effect; F-8 + F-A3 does not introduce new color treatments.

---

## 📊 Success Metrics

### Primary Metrics (Leading Indicators)

**Metric 1**: BLP-01 §6 Coverage Matrix Planned-item count
- **Baseline**: 0 (as of F-7 closure)
- **Target**: 0 (no regression)
- **Owner**: product-manager

**Metric 2**: BLP-01 §6 Coverage Matrix Partial-item count
- **Baseline**: 6 (A05, A06, API6, API8, API9, API10)
- **Target**: 0 (all six closed Covered or Deferred)
- **Owner**: product-manager

**Metric 3**: PDF Coverage Attestation section non-emptiness across baselines
- **Baseline**: 1 of 7 (only `agentic-app` carries any `source_attribution` today; pre-F-A3)
- **Target**: 8 of 8 (all eight examples render non-empty Coverage Attestation post-F-A3)
- **Owner**: architect (technical), product-manager (sign-off)

**Metric 4**: Detection agents emitting `source_attribution`
- **Baseline**: 3 of 14 (F-1 / F-2 / F-4 only)
- **Target**: **14 of 14** (3 pre-existing + 11 newly wired per Architect HIGH-A)
- **Owner**: architect

### Secondary Metrics (Lagging Indicators)

**Metric 5**: BLP-01 four-framework attestation total
- **Baseline**: 40/40 OWASP four-framework total + 6 Partial Web/API entries
- **Target**: 60/60 if all six Partial items close Covered (40 four-framework + 20 Web/API); count adjusts for any items Deferred

**Metric 6**: Pipeline-generated coverage-percentage accuracy
- **Target**: 0 percentage points |Δ| between PDF-rendered and audit-script-computed coverage % per framework

---

## 🔍 Scope & Boundaries

### In Scope (MVP / Phase 1)

**Must Have (P0)**:
- ✅ F-A3 populator wiring across 9 host agents (Stream 1)
- ✅ Six Partial Web/API item closure (A05, A06, API6, API8, API9, API10)
- ✅ Taxonomy YAML expansion with tactical-grouping Out-of-Scope (ATT&CK) + per-item (ATLAS, OWASP)
- ✅ `extract-report-data.py` per-framework coverage-percentage computation
- ✅ Eight example baseline regen + intentional `security-report.pdf.baseline` update
- ✅ §6 Coverage Matrix annotation with pointer to F-B
- ✅ Public per-feature ADR (Proposed → Accepted dual-commit)
- ✅ Audit script + coverage-percentage cross-check + F-A3 wiring tests

**Should Have (P1)**:
- 🎯 NIST AI RMF + CWE Top 25 inventory expansion if found incomplete during Stream 3 audit (otherwise F-A1 seed retained as-is)

### Out of Scope (Future Phases)

**Could Have (P2)** — Not in MVP:
- 🔮 Cross-framework reasoning surface via `crosswalk.yaml` JOIN (F-B ADR-029 MVP boundary preserved)
- 🔮 New threat agents (this feature is attestation + populator wiring, not enrichment)

**Note** (v1.1 → v1.2 scope expansion): Earlier draft excluded `agent-autonomy` and `prompt-injection` from F-A3 scope on the assumption that finding-ID-prefix attribution was implicit. **Architect's v1.1 HIGH-A invalidated this assumption** (aggregator code reads only the explicit `source_attribution[].id` field). Both agents are now in F-A3 scope per FR-1.

**Won't Have** — Explicitly excluded:
- ❌ AIVSS scoring formula adoption
- ❌ Schema shape change (`schemas/finding.yaml` v1.8 preserved)
- ❌ New finding-ID prefixes
- ❌ Vendor-specific framework adoption

### Assumptions

- A-1 (REVISED post-Architect Q1): F-A3 populator wiring is **REQUIRED** for SC-7 to hold — empirically verified at PRD-review time. F-A3 is now in scope as Stream 1.
- A-2 (PARTIALLY VALID per Architect Q2): 4/6 Partial items close cleanly under existing patterns; 2/6 (API6, API9) require new Indicator categories within FR-2's allowance. Validation passes.
- A-3 (PARTIALLY VALID per Architect Q3): MITRE ATT&CK Enterprise is ~600+ records; tactical-grouping mandatory per Architect HIGH adjudication. Validation passes via FR-3.
- A-4 (RESOLVED per Architect Q4): F-6 + F-7 example architectures (`predictive-ml-app`, `mobile-banking-app`) MUST join the baseline scope — eight baselines total per FR-5.

### Constraints

**Technical Constraints**:
- F-A3 wiring must be **additive only** to the 9 host agents — no functional changes to existing detection logic, no removal of pattern categories.
- Combined feature must preserve the F-7 28-file post-merge detection-tier inventory zero-edit-invariant for files outside the F-A3 Stream 1 + Stream 2 audit scope (i.e., non-target `detection-patterns.md` files for skills not implicated by Stream 2's six Partial item closures remain byte-identical). Note that `agent-autonomy.md` and `prompt-injection.md` ARE in scope per Architect HIGH-A — they receive additive `source_attribution` populator blocks like the other 9 host agents.
- Must reuse the F-B rendering surface as-is (no new Typst pages, no new conditional-inclusion booleans beyond the existing `has-source-attribution`).
- Must preserve `SOURCE_DATE_EPOCH=1700000000` byte-identity for any baseline NOT in the eight-example regen scope.

**Business Constraints**:
- 5–6 week effort budget per Architect Option A.
- Public-only governance per [SDR-001 Option C](../../../_internal/strategy/SDR-001-threat-coverage-strategy.md).

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Calendar model** (Team-Lead HIGH-R1 normalization): Calendar week-based; "Day N" = Nth working day from Day 1 = Thu 2026-04-30. Memorial Day Mon 2026-05-25 is non-working inside Week 5 (4 working days that week). This eliminates the v1.1 calendar drift.

**Week 1 (Days 1–5; Thu 2026-04-30 → Wed 2026-05-06) — F-A3 Wiring Wave 1: 5 STRIDE-heavy hosts**
- Day 1–2 (Thu 4/30 + Fri 5/1): Wire `tachi-spoofing` + `tachi-tampering` + `tachi-info-disclosure`. **Per Team-Lead MEDIUM-R1: pair-author with security-analyst on Days 1–4 to keep senior-backend-engineer load within the 80%/day cap.**
- Day 3–4 (Mon 5/4 + Tue 5/5): Wire `tachi-privilege-escalation` + `tachi-repudiation`
- Day 5 (Wed 5/6): F-A3 wiring smoke test on `web-app` + `agentic-app` + `predictive-ml-app` (per Team-Lead MEDIUM-R2 — three baselines instead of one to surface STRIDE / AI / ML coverage early)
- **Deliverable**: 5 of 11 host agents emit `source_attribution`; smoke test green on three architectures

**Week 2 (Days 6–11; Thu 2026-05-07 → Thu 2026-05-14) — F-A3 Wiring Wave 2: 6 hosts (+1 day for HIGH-A) + Stream 2 audit start**
- Day 6–7 (Thu 5/7 + Fri 5/8): Wire `tachi-denial-of-service` + `tachi-tool-abuse`
- Day 8–9 (Mon 5/11 + Tue 5/12): Wire `tachi-data-poisoning` + `tachi-model-theft`
- Day 10–11 (Wed 5/13 + Thu 5/14): Wire `tachi-prompt-injection` + `tachi-agent-autonomy` (added per Architect HIGH-A); F-A3 closure verification across all 8 baselines
- Day 6–11 (parallel): Begin Stream 2 audit (A05 + A06 closures via Primary Source addition)
- **Deliverable**: 11 of 11 host agents wired (14/14 detection-tier total); F-A3 deferral debt fully cleared; 2 of 6 Partial items closed

**Week 3 (Days 12–16; Fri 2026-05-15 → Thu 2026-05-21) — Stream 2 completion + Stream 3 OWASP/ATLAS**
- Day 12–13 (Fri 5/15 + Mon 5/18): Complete Stream 2 audit — close API6 (new Indicator) + API8 + API9 (new Indicator) + API10
- Day 14–16 (Tue 5/19 + Wed 5/20 + Thu 5/21): Stream 3 — populate `schemas/taxonomy/owasp.yaml` (full A01–A10 + API1–API10); expand `mitre-atlas.yaml` (7 → full ATLAS, ~30 records)
- **Deliverable**: 6 of 6 Partial items closed; 2 of 3 taxonomy YAMLs at full inventory

**Week 4 (Days 17–21; Fri 2026-05-22 → Fri 2026-05-29 — Memorial Day Mon 5/25 lost) — Stream 3 ATT&CK + Stream 4 aggregator**
- Day 17 (Fri 5/22): Begin ATT&CK Enterprise tactical-grouping audit (5–7 tactic-level Out-of-Scope rationales for TA0005/7/8/9/10/11/40)
- *Memorial Day 2026-05-25 — non-working*
- Day 18–19 (Tue 5/26 + Wed 5/27): Complete ATT&CK Enterprise inventory expansion (per-item rationale on in-scope tactics TA0001/2/3/4/6/42)
- Day 20–21 (Thu 5/28 + Fri 5/29): Stream 4 — extend `scripts/extract-report-data.py` with per-framework coverage-percentage computation; add Typst data contract bindings; **enforce KB-037 pyyaml deferred-import invariant inline (per Architect MEDIUM-B — `import yaml` stays inside function bodies)**
- **Deliverable**: All taxonomy YAMLs at full inventory; aggregator extension complete

**Week 5 (Days 22–26; Mon 2026-06-01 → Fri 2026-06-05) — Tests + baseline regen + ADR Proposed**
- Day 22–23 (Mon 6/1 + Tue 6/2): Write four test scripts — `test_coverage_attestation_audit.py`, `test_coverage_percentage_computation.py`, `test_f_a3_populator_wiring.py`, `test_pyyaml_deferred_import.py`
- Day 24–25 (Wed 6/3 + Thu 6/4): Eight example baseline regen + intentional `security-report.pdf.baseline` update (verify non-Coverage-Attestation pages remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`)
- Day 26 (Fri 6/5): §6 Coverage Matrix demotion annotation in `_internal/strategy/BLP-01-threat-coverage.md`; public per-feature ADR Proposed
- **Deliverable**: All four test scripts green; 8 baselines regenerated; ADR Proposed

**Week 6 (Days 27–29 + buffer; Mon 2026-06-08 → Wed 2026-06-10) — ADR Accepted + sign-off + PR merge**
- Day 27 (Mon 6/8): ADR Accepted (post-merge SHA fill-in per ADR-035 D-10 dual-commit governance)
- Day 28 (Tue 6/9): Triple Triad sign-off on tasks.md
- Day 29 (Wed 6/10): PR squash-merge with `feat(241):` Conventional Commit title; release-please PR fires within ~30s per R12 enforcement (verify via `gh pr list --state open --search "release-please" --limit 3`; if empty, push empty `feat(241):` marker commit)
- Buffer (Days 30+): Reserved for Risk 1 (ATT&CK depth) or Risk 3 (1–2 Partial item Deferrals require ADR rationale + follow-on Issue)
- **Deliverable**: Feature delivered; BLP-01 closed; release-please PR open

### Key Milestones

| Milestone | Target | Owner | Status |
|-----------|--------|-------|--------|
| PRD Approval | 2026-04-29 | product-manager | 🟡 In Review |
| Spec Complete | Day 1+1 (2026-05-01 Fri) | architect | 📋 Pending |
| Plan Complete | Day 1+2 (2026-05-04 Mon) | architect + team-lead | 📋 Pending |
| Tasks Complete | Day 1+3 (2026-05-05 Tue) | team-lead | 📋 Pending |
| F-A3 Wave 1 Complete (5 hosts; smoke test on 3 baselines per MEDIUM-R2) | Day 5 (2026-05-06 Wed) | senior-backend-engineer + security-analyst | 📋 Pending |
| F-A3 Wave 2 Complete (6 hosts incl. prompt-injection + agent-autonomy) | Day 11 (2026-05-14 Thu) | senior-backend-engineer | 📋 Pending |
| Stream 2 Complete (6 Partial items closed) | Day 13 (2026-05-18 Mon) | security-analyst | 📋 Pending |
| Stream 3 OWASP + ATLAS Complete | Day 16 (2026-05-21 Thu) | security-analyst | 📋 Pending |
| Stream 3 ATT&CK Complete | Day 19 (2026-05-27 Wed; Memorial Day Mon 5/25 lost in Week 4) | security-analyst | 📋 Pending |
| Stream 4 Aggregator Complete | Day 21 (2026-05-29 Fri) | senior-backend-engineer | 📋 Pending |
| Tests + 8-Baseline Regen Complete | Day 25 (2026-06-04 Thu) | tester + senior-backend-engineer | 📋 Pending |
| ADR Accepted | Day 27 (2026-06-08 Mon) | architect | 📋 Pending |
| PR Squash-Merge + release-please verify | Day 29 (2026-06-10 Wed) | team-lead | 📋 Pending |

Legend: ✅ Complete | 🟢 On Track | 🟡 In Review | 📋 Pending | 🔴 Blocked

---

## ⚠️ Risks & Dependencies

### Technical Risks

**Risk 1**: ATT&CK Enterprise full inventory authoring is larger than budgeted even with tactical-grouping
- **Likelihood**: Medium
- **Impact**: Medium (5–6 week budget could slip to 7 weeks if tactical-grouping insufficient and per-item rationale required for in-scope tactics)
- **Mitigation**: Use tactical-grouping for 5–7 design-time-irrelevant tactics (TA0005, TA0007, TA0008, TA0009, TA0010, TA0011, TA0040). Author per-item Out-of-Scope rationale only on items inside in-scope tactics (TA0001 Initial Access, TA0002 Execution, TA0003 Persistence, TA0004 Privilege Escalation, TA0006 Credential Access, TA0042 Resource Development).
- **Contingency**: If ATT&CK inventory expansion threatens the 6-week budget, defer ATT&CK to a follow-on Issue (open ADR explicitly carrying the deferral); keep ATLAS + OWASP closure + F-A3 wiring + 6 Partial item closure in feature scope.

**Risk 2**: F-A3 populator wiring per host agent is not uniform — some agents have richer pattern-category surfaces requiring more wiring effort
- **Likelihood**: Medium
- **Impact**: Medium (could push Stream 1 from 2 weeks to 2.5 weeks)
- **Mitigation**: Wave 1 (Days 1–5) tackles the 5 most STRIDE-heavy agents first; smoke test on `web-app` baseline at end of Wave 1 surfaces any per-agent issues early. Wave 2 (Days 6–10) tackles the 4 less STRIDE-heavy agents.
- **Contingency**: If Wave 1 smoke test reveals significant per-agent variation, extend Stream 1 to 2.5 weeks and compress Stream 2 audit into Week 3 (reduces parallelism but preserves total budget).

**Risk 3**: 1–2 Partial items (likely API6 or API9) cannot close cleanly under existing patterns + new Indicator allowance
- **Likelihood**: Medium (Architect Q2 explicitly flagged these two)
- **Impact**: Medium (Deferral requires its own ADR rationale + follow-on Issue, reducing BLP-01 four-framework total below 60/60)
- **Mitigation**: Stream 2 audit happens in Week 2–3 (not Week 5) so Deferrals surface early enough to plan around.
- **Contingency**: Each Deferral surfaces as an explicit ADR rationale + Issue; BLP-01 closes at the actual Covered count (e.g., 58/60 if 2 items defer).

**Risk 4**: Baseline regen produces unexpected churn on non-Coverage-Attestation pages of the PDF
- **Likelihood**: Low (F-A3 wiring is additive in agent emission; non-CA pages should not change)
- **Impact**: Medium (would surface as PR-review noise)
- **Mitigation**: Use `SOURCE_DATE_EPOCH=1700000000` byte-identity harness; non-Coverage-Attestation pages must remain byte-identical (assert in CI).
- **Contingency**: Investigate any non-Coverage-Attestation churn as a regression; do not accept baseline updates that span non-target pages.

### Business Risks

**Risk 5**: Out-of-Scope tactical-grouping is contested by external reviewers
- **Likelihood**: Low
- **Impact**: High (would undermine pipeline-generated coverage-percentage credibility)
- **Mitigation**: Architect + PM joint review of tactical-grouping rationale; each `out_of_scope: true` tactic carries a one-line rationale that PM can defend.
- **Contingency**: If contested, denominate using full ATT&CK inventory (no Out-of-Scope filter); coverage percentages will be lower (~5–10%) but uncontested.

### Dependencies

All 10 upstream dependencies are SATISFIED. Spot-check verified by Team-Lead: F-7 = `e962a0e`, F-A1 = `8b7c7bf`.

---

## ❓ Open Questions

### Resolved by Architect Triad Review (2026-04-29)

- [x] **Q-Architect-1**: A-1 INVALIDATED — F-A3 populator wiring IS required. **Resolution**: Option A — F-A3 pulled into combined scope as Stream 1. Budget extended to 5–6 weeks per Architect recommendation.
- [x] **Q-Architect-2**: A-2 PARTIALLY VALID — 4/6 closeable, 2/6 (API6, API9) likely require new Indicator categories within FR-2 allowance. **Resolution**: FR-2 mapping table codifies per-item closure path.
- [x] **Q-Architect-3**: A-3 PARTIALLY VALID — ATT&CK Enterprise ~600 records. **Resolution**: Tactical-grouping Out-of-Scope strategy in FR-3 (5–7 tactic-level rationales for design-time-irrelevant tactics).
- [x] **Q-Architect-4**: F-6 + F-7 examples MUST join baseline scope. **Resolution**: SC-7 expanded to 8 baselines; FR-5 enumerates all eight.
- [x] **Q-TeamLead-1**: 3 vs 4 weeks. **Resolution**: Moot — Option A's 5–6 week budget supersedes; Team-Lead's 3.5-week buffer-floor logic applied proportionally.
- [x] **Q-TeamLead-2**: Agent assignments validated. **Resolution**: senior-backend-engineer leads Stream 1 (F-A3 wiring) + Stream 4 (aggregator); security-analyst leads Stream 2 (audit) + Stream 3 (taxonomy authoring); tester owns the test suite; architect owns the ADR.

### Resolved by Architect Re-Review (v1.1, 2026-04-29)

- [x] **Q-Architect-5** (was Open in v1.1): WIRE `prompt-injection`. **Resolution**: Aggregator at `extract-report-data.py:1112` reads only `finding.source_attribution[].id` — no implicit-prefix path exists. Without explicit wiring, OWASP LLM01 renders Gap on every baseline.
- [x] **Q-Architect-6** (was Open in v1.1): WIRE `agent-autonomy`. **Resolution**: Same aggregator semantics; without wiring, ASI01/06/08/10 + LLM06/10 render Gap, contradicting the BLP-01 §6 10/10 closure claim.

### Open Questions (carry-forward to Plan stage)

- [ ] **Q-PM-1**: Should the public-facing ADR be split into two ADRs (one for F-8 attestation, one for F-A3 populator wiring + ADR-027 D1 record-shape extension), or a single combined ADR? Architect MEDIUM-A recommends "separate ADR alongside ADR-NNN-web-api-coverage-attestation" for the schema-shape extension. - **Owner**: product-manager + architect - **Due**: Day 1 - **Status**: Open

---

## 📚 References

### Product Documentation

- Product Vision: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)
- BLP-01 strategic plan: [_internal/strategy/BLP-01-threat-coverage.md](../../../_internal/strategy/BLP-01-threat-coverage.md) — F-8 + F-A3 §7 epic content (private)
- F-B precedent PRD: [docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md](./194-coverage-attestation-report-section-2026-04-18.md)
- F-7 precedent PRD (most recent BLP-01 closure): [docs/product/02_PRD/237-mobile-top-10-coverage-bundle-2026-04-28.md](./237-mobile-top-10-coverage-bundle-2026-04-28.md)
- F-6 precedent PRD: [docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md](./232-ml-top-10-coverage-bundle-2026-04-27.md)

### Technical Documentation

- Constitution: [.aod/memory/constitution.md](../../../.aod/memory/constitution.md)
- ADR-027 (F-A1 taxonomy catalog)
- ADR-028 (F-A2 source_attribution schema)
- ADR-029 (F-B rendering surface)
- ADR-032 (F-3 first F-A3 deferral)
- ADR-034 D-8 (F-5 second F-A3 deferral)
- ADR-035 D-10 (F-6 third F-A3 deferral)
- ADR-036 D-10 (F-7 fourth F-A3 deferral; cumulative scope statement)
- Architect review: [.aod/results/architect.md](../../../.aod/results/architect.md)
- Team-Lead review: [.aod/results/team-lead.md](../../../.aod/results/team-lead.md)

### External Resources

- [OWASP Top 10:2021](https://owasp.org/Top10/)
- [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [MITRE ATT&CK Enterprise](https://attack.mitre.org/)
- [MITRE ATLAS](https://atlas.mitre.org/)

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [ ] Problem statement is clear and user-focused (closure of BLP-01 §6 Coverage Matrix Web/API Partial items + F-A3 deferral debt + pipeline-generated attestation)
- [ ] Four user stories preserved verbatim from Issue #241 (3 stories) + new US-241-4 for F-A3 closure
- [ ] Success metrics measurable across 15 SCs covering F-A3 wiring + F-8 attestation + cross-cutting
- [ ] Scope realistic for 5–6 week timeline per Architect Option A
- [ ] Risks and dependencies identified
- [ ] Aligns with product vision (closes BLP-01 §10 one-line success statement at runtime)

**Architect**:
- [ ] Four coordinated work streams technically sound (F-A3 wiring + 6 Partial item audit + taxonomy expansion + aggregator extension)
- [ ] No new agent files / no `finding.yaml` schema shape changes / no orchestrator edits — feature is attestation + populator wiring, not enrichment
- [ ] `schemas/taxonomy/*.yaml` ADR-027 D1 record-shape extension (`out_of_scope` + `out_of_scope_rationale` fields) acknowledged in new public ADR per MEDIUM-A
- [ ] F-7 28-file zero-edit-invariant preserved for files outside F-A3 + Stream 2 scope
- [ ] F-A3 wiring scope validated (**11 hosts**: 9 STRIDE/AI + `prompt-injection` + `agent-autonomy`; SC-1 + Metric 4 = 14/14)
- [ ] Tactical-grouping Out-of-Scope strategy adjudicated (5–7 ATT&CK tactics: TA0005/7/8/9/10/11/40 design-time-irrelevant)
- [ ] Eight-baseline scope confirmed (Q-Architect-4 RESOLVED)
- [ ] KB-037 pyyaml deferred-import invariant test included in test suite per MEDIUM-B

**Team-Lead** (team-lead):
- [ ] 5–6 week budget realistic given F-A3 (11 hosts) + F-8 combined scope
- [ ] Calendar normalized: Day N = Nth working day from Day 1 = Thu 2026-04-30; Memorial Day Mon 2026-05-25 inside Week 4 yields 4 working days that week (HIGH-R1 RESOLVED)
- [ ] Agent assignments validated (senior-backend-engineer + security-analyst pair-author Days 1–4 per MEDIUM-R1; tester + architect, all within 80%/day cap)
- [ ] Stream parallelism captured in Phase Breakdown (F-A3 Wave 1 → 3-baseline smoke test per MEDIUM-R2 → Wave 2 with HIGH-A +1 day → Stream 2 start)
- [ ] All upstream dependencies (F-A1, F-A2, F-B, F-1 through F-7) verified satisfied
- [ ] Release-please R12 verification: Day 29 PR squash-merge with `feat(241):` Conventional Commit title; verify release-please PR fires within ~30s post-merge per `.claude/rules/git-workflow.md`

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | 📋 Pending | - | - |
| Architect | architect | 📋 Pending | - | - |
| Engineering Lead | team-lead | 📋 Pending | - | - |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-29 | product-manager | Initial PRD — F-8 BLP-01 Tier 3 attestation pass (3-week scope) |
| 1.1 | 2026-04-29 | product-manager | F-A3 pulled into scope per Architect Q-Architect-1 BLOCKING resolution (Option A). Budget extended 3w → 5–6w. Tactical-grouping Out-of-Scope strategy for ATT&CK per Q-Architect-3 HIGH. Eight-baseline scope per Q-Architect-4 MEDIUM. Four user stories (US-241-1..4); 15 success criteria; four coordinated work streams. |
| 1.2 | 2026-04-29 | product-manager | F-A3 host scope expanded 9 → 11 per Architect HIGH-A (`prompt-injection` + `agent-autonomy` MUST wire; aggregator at `extract-report-data.py:1112` reads only explicit `source_attribution[].id` field). SC-1 + Metric 4 = 14/14 (was 12/14). Phase Breakdown Wave 2 absorbs +1 day. Calendar normalized to working-day model from Day 1 = Thu 2026-04-30 per Team-Lead HIGH-R1 (eliminates 2-day drift on milestones). ADR-027 D1 record-shape extension acknowledged per Architect MEDIUM-A (taxonomy YAML records gain `out_of_scope` + `out_of_scope_rationale` fields). KB-037 pyyaml deferred-import invariant codified per Architect MEDIUM-B (new `test_pyyaml_deferred_import.py`). Stream 1 Wave 1 pair-authoring per Team-Lead MEDIUM-R1; Day 5 smoke test expanded to 3 baselines per MEDIUM-R2; release-please R12 verification per LOW-R2. |
