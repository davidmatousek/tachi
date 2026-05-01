---
prd_reference: docs/product/02_PRD/241-web-api-coverage-attestation-2026-04-29.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-01
    status: APPROVED_WITH_CONCERNS
    notes: "Spec faithfully translates PRD — all 4 user stories preserved verbatim, all 15 PRD SCs preserved (renumbered SC-001..SC-015) plus 3 additive operational SCs (SC-016..SC-018), all four work streams codified in 24 FRs. Out-of-Scope section is explicit and aligned with PRD §Won't Have plus 8 operational additions drawn from research findings. Q-PM-1 (single vs split ADR) correctly carries forward to Plan-Day; Q-Plan-1 + Q-Plan-2 (API6 / API9 host placement) are correctly Plan-Day-deferred per PRD FR-2 dual-candidate language. Three LOW concerns identified (Plan-Day default attestation editorial inference, US-4 Independent Test 'non-AI baselines' framing nit, three additive SCs warranting plan-day acknowledgment) — none blocking; all addressable at plan.md authoring. Full review: .aod/results/product-manager.md."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]

**Feature Branch**: `241-web-api-coverage-attestation`
**Created**: 2026-04-30
**Status**: Draft (PM APPROVED_WITH_CONCERNS — proceeding to /aod.project-plan)
**Input**: User description: "Feature 241 — F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]. Source PRD: docs/product/02_PRD/241-web-api-coverage-attestation-2026-04-29.md."

---

## Overview

This is the **closure feature** for the BLP-01 11-feature initiative (Tier 3 attestation pass + Foundation populator-wiring closure). It runs the final attestation pass that proves tachi's existing detection coverage per-finding inside every PDF security report — by wiring `source_attribution` populators across the eleven remaining BLP-01 host agents (F-A3 closure: nine STRIDE/AI hosts plus `prompt-injection` and `agent-autonomy`), closing the six remaining Partial items in the BLP-01 §6 Coverage Matrix with citation evidence (F-8 audit), expanding the MITRE ATT&CK + ATLAS taxonomy YAMLs to full inventories with tactical-grouped Out-of-Scope annotations, and replacing the hand-curated coverage matrix with pipeline-generated per-taxonomy coverage percentages.

This feature does not introduce new threat agents, does not change the `schemas/finding.yaml` shape (preserved at v1.8 — sixth zero-`finding.yaml`-bump BLP-01 detection feature), and does not expand the rendering surface beyond what F-B (Feature 194) already shipped. It populates inputs the surface already consumes.

The feature ships as **four coordinated work streams**:

1. **Stream 1 (F-A3 Populator Wiring)** — additive `source_attribution` populator wiring on 11 host agents
2. **Stream 2 (Partial Item Audit)** — closure of 6 Partial Web/API items via Primary Source addition or new Indicator categories
3. **Stream 3 (Taxonomy YAML Expansion)** — full-inventory expansion of 3 taxonomy YAMLs with Out-of-Scope annotations
4. **Stream 4 (Rendering Verification)** — pipeline-generated per-framework coverage percentages and 8-baseline regen

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Per-Finding Source Attribution Renders in PDF (Priority: P1)

A compliance-driven adopter (CISO, security auditor, risk committee member) reviews a generated `tachi.security-report` PDF on any of their architectures. They want to trace tachi findings back to the frameworks their compliance program already uses (OWASP Top 10, OWASP API Top 10, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE) without re-authoring the mapping by hand.

**Why this priority**: This is the primary user value of the feature — converting tachi's detection coverage into compliance-team-consumable per-finding attribution. Without this, the F-B Coverage Attestation surface delivered four features ago renders empty on most baselines.

**Independent Test**: Run `tachi.security-report` on any of the eight example architectures (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`, `predictive-ml-app`, `mobile-banking-app`); inspect the Coverage Attestation section of the resulting PDF; verify per-finding attribution table is non-empty and per-framework coverage percentages are non-zero on at least one framework family served by the architecture's detection-tier coverage.

**Acceptance Scenarios**:

1. **Given** a finding emitted by any of the eleven F-A3-wired host agents with populated `source_attribution` for OWASP Top 10:2021 (e.g., A01) or API Top 10:2023 (e.g., API1), **when** the per-finding attribution table renders in the PDF, **then** the OWASP cell carries the correct ID with `relationship: primary` rendered bold and `related`/`derived` rendered plain.
2. **Given** the aggregate Coverage Attestation matrix on the OWASP page, **when** any of the eight example architectures generates a report, **then** all 10 OWASP Top 10:2021 entries (A01–A10) carry visible classification (Covered / Partial / Gap) and a per-framework coverage percentage that matches the manual audit-script computation.
3. **Given** any of the eight example architectures, **when** `tachi.security-report` runs, **then** the Coverage Attestation section is non-empty (per-finding attribution table has ≥1 row AND per-framework coverage-percentage values are non-zero on at least the framework families served by the architecture's detection-tier coverage).
4. **Given** an architecture with mixed STRIDE + AI surfaces (e.g., `mermaid-agentic-app`), **when** findings emit attribution arrays from multiple host agents simultaneously, **then** the per-finding rows render without duplication and the per-framework aggregate counts add up correctly.

---

### User Story 2 — Six Partial Web/API Items Close to Covered with Citation Evidence (Priority: P1)

A tachi maintainer wants the BLP-01 §6 Coverage Matrix to have zero unexplained Partial items. Each of the six Partial Web/API items (A05, A06, API6, API8, API9, API10) is re-classified with citation evidence so the matrix satisfies the BLP-01 §8 Quality Bar (every Covered item cites ≥1 agent and ≥1 detection-pattern category).

**Why this priority**: Closing these six items is one of two structural prerequisites for retiring the §6 Coverage Matrix as the source of truth. Without closure, the matrix can't be safely demoted; with closure, the pipeline-generated attestation becomes the authoritative coverage signal.

**Independent Test**: For each of the six items, run a representative example architecture (`web-app`, `microservices`, or `ascii-web-api`) and verify at least one finding's `source_attribution` resolves to that OWASP Top 10 or API Top 10 ID per `schemas/taxonomy/owasp.yaml`. For any item explicitly Deferred, verify a follow-on Issue exists with the deferral ADR rationale referenced.

**Acceptance Scenarios**:

1. **Given** A05 (Security Misconfiguration), A06 (Vulnerable and Outdated Components), API8 (Security Misconfiguration), or API10 (Unsafe Consumption of APIs), **when** the audit completes, **then** each item is Covered with a Primary Source block addition + Indicator extension on the affected `detection-patterns.md` file, OR explicitly Deferred with a new ADR rationale + follow-on Issue.
2. **Given** API6 (Unrestricted Access to Sensitive Business Flows) or API9 (Improper Inventory Management), **when** the audit completes, **then** each item is Covered via a new Indicator category in the affected companion catalog (target hosts: `tachi-tool-abuse` or `tachi-privilege-escalation` for API6; `tachi-info-disclosure` or `tachi-repudiation` for API9), OR explicitly Deferred with a new ADR rationale + follow-on Issue.
3. **Given** any newly-closed Partial item, **when** running tachi on a representative example architecture, **then** at least one finding's `source_attribution` array resolves to that OWASP Top 10 or API Top 10 ID per `schemas/taxonomy/owasp.yaml`.
4. **Given** the completeness-verification edits, **when** reviewed against the F-7 28-file post-merge detection-tier inventory, **then** they are additive against existing skill-reference files only — no new agent files, no `schemas/finding.yaml` shape changes.

---

### User Story 3 — §6 Coverage Matrix Demoted to Historical; Pipeline-Generated Attestation Takes Over (Priority: P1)

A tachi maintainer or future contributor wants to know "what fraction of MITRE ATT&CK does tachi cover?". The answer comes from the F-B Coverage Attestation section as a pipeline-generated coverage percentage with explicit gaps and Out-of-Scope annotations — not from blueprint prose memory.

**Why this priority**: This is the closure outcome that retires the hand-maintained matrix as a maintenance liability. Future pattern-category additions automatically propagate to the attestation surface without blueprint-level bookkeeping. This story is the structural reason the BLP-01 initiative ends after F-241 — the matrix is no longer the source of truth, and the attestation surface inherits future coverage expansions automatically.

**Independent Test**: Inspect `_internal/strategy/BLP-01-threat-coverage.md` §6 — verify the matrix carries the *"historical — superseded by pipeline-generated attestation"* annotation and a pointer to the F-B Coverage Attestation section. Run an audit script that computes per-framework coverage percentages from `schemas/taxonomy/*.yaml` × finding `source_attribution` arrays on each baseline architecture; verify the audit-computed values match the PDF-rendered values within 0 percentage points.

**Acceptance Scenarios**:

1. **Given** the populated `schemas/taxonomy/mitre-attack.yaml` and `schemas/taxonomy/mitre-atlas.yaml` with full item inventories + tactical-grouped Out-of-Scope annotations, **when** the report aggregator runs, **then** it computes per-framework coverage percentage as `|cited_ids| / |taxonomy_ids_not_out_of_scope|` and emits values to the Typst data contract.
2. **Given** the per-framework coverage percentage, **when** the F-B Coverage Attestation page renders, **then** the percentage matches the manual audit-script computation and the Partial / Gap counts render alongside per F-B's classification contract.
3. **Given** the BLP-01 §6 Coverage Matrix, **when** F-241 closes, **then** the matrix carries a *"historical — superseded by pipeline-generated attestation"* annotation with a pointer to the F-B Coverage Attestation section.
4. **Given** a future pattern-category addition to any companion `detection-patterns.md` with a Primary Source block, **when** that finding category is invoked on a downstream architecture, **then** the resulting finding's `source_attribution` automatically feeds the Coverage Attestation section without blueprint-level bookkeeping.

---

### User Story 4 — Populator Wiring Closes the F-A3 Deferral Debt (Priority: P1)

A tachi maintainer runs `tachi.security-report` on any architecture whose findings come from one of the eleven BLP-01 host agents (the nine STRIDE/AI hosts plus `prompt-injection` and `agent-autonomy`). Those findings emit `source_attribution` arrays in their `threats.md` Section 9 YAML output (per ADR-028 contract), driving non-zero per-framework coverage percentages on every framework page tachi attests to — not just the LLM/Agentic surfaces served by the three F-1/F-2/F-4 net-new agents.

**Why this priority**: F-A3 has been deferred four features in a row (ADR-032 / ADR-034 D-8 / ADR-035 D-10 / ADR-036 D-10). Without closure, the OWASP LLM01 / ASI01 / ASI06 / ASI08 / ASI10 / LLM06 / LLM10 entries render Gap on every baseline — the aggregator at the report extraction layer reads only `finding.source_attribution[].id` directly with no implicit prefix-attribution path. F-A3 closure is the single remaining gate between the machine-readable coverage contract and adopter-visible attested coverage.

**Independent Test**: Run `grep -l "source_attribution" .claude/agents/tachi/*.md` and verify the count returns 14 of 14 detection-tier files (3 pre-existing F-1/F-2/F-4 + 11 newly wired). Regenerate any of the seven non-AI baselines and verify the Coverage Attestation section renders non-empty per-finding attribution tables.

**Acceptance Scenarios**:

1. **Given** any of the eleven target host agents, **when** the agent emits a finding for any pattern category in its companion `references/detection-patterns.md`, **then** the finding's `source_attribution` array is populated with at least one `primary` taxonomy citation per the F-1/F-2/F-4 net-new agent precedent.
2. **Given** the populator wiring across eleven host agents, **when** the eight example baselines are regenerated, **then** the Coverage Attestation section renders non-empty per-finding attribution tables on each baseline (subject to the architecture's actual detection-tier coverage — e.g., `web-app` exercises STRIDE agents extensively so the OWASP page renders meaningful coverage; `mobile-banking-app` exercises mobile-specific Indicators so the OWASP Mobile page renders meaningful coverage).
3. **Given** a populator wiring change to all eleven host agents, **when** `grep -l "source_attribution" .claude/agents/tachi/*.md` runs, **then** the count of agents emitting `source_attribution` increases from 3 (F-1/F-2/F-4) to 14 of 14 detection-tier agents.
4. **Given** the populator-wiring edits, **when** reviewed against the ADR-036 200-line agent-file cap, **then** no host agent's file exceeds 200 lines post-wiring.

---

### Edge Cases

- **Risk 1 (ATT&CK inventory authoring overrun)**: What happens if MITRE ATT&CK Enterprise full-inventory expansion (~600 records) cannot complete within the 5–6 week budget even with tactical-grouping Out-of-Scope strategy? *Tactical-grouping covers 5–7 design-time-irrelevant tactics (TA0005 / TA0007 / TA0008 / TA0009 / TA0010 / TA0011 / TA0040) at the tactic-level Out-of-Scope rationale; per-item rationale only on items inside in-scope tactics (TA0001 / TA0002 / TA0003 / TA0004 / TA0006 / TA0042). If the budget still threatens, ATT&CK expansion is deferred to a follow-on Issue with explicit ADR rationale; ATLAS + OWASP closure + F-A3 wiring + 6 Partial item closure remain in feature scope.*
- **Risk 2 (F-A3 per-agent variance)**: What happens if some host agents have richer pattern-category surfaces requiring more wiring effort than others? *Wave 1 (Days 1–5) tackles 5 STRIDE-heavy agents first with pair-authoring (senior-backend-engineer + security-analyst) to keep load within 80%/day cap; Day 5 smoke test on three baselines (`web-app` + `agentic-app` + `predictive-ml-app`) surfaces per-agent variance early. Wave 2 (Days 6–11) tackles the remaining 6 agents with one extra day absorbed for `prompt-injection` + `agent-autonomy` per Architect HIGH-A.*
- **Risk 3 (1–2 Partial items can't close cleanly)**: What happens if API6 or API9 cannot close under existing patterns + the at-most-one-new-Indicator-category allowance? *Each non-closing item surfaces as an explicit ADR rationale + follow-on Issue; BLP-01 closes at the actual Covered count (e.g., 58/60 if 2 items defer). Stream 2 audit happens in Week 2–3 (not Week 5) so deferrals surface early enough to plan around.*
- **Risk 4 (non-Coverage-Attestation page churn)**: What happens if baseline regen produces unexpected churn on non-Coverage-Attestation pages of the PDF? *The `SOURCE_DATE_EPOCH=1700000000` byte-identity harness asserts non-Coverage-Attestation pages remain byte-identical; any non-CA-page churn is treated as a regression and investigated before accepting the baseline update.*
- **Risk 5 (tactical-grouping rationale contested)**: What happens if external reviewers contest the tactical-grouping Out-of-Scope rationale on ATT&CK? *Each `out_of_scope: true` tactic carries a one-line rationale defensible by an external auditor. Contingency: if contested, denominate using full ATT&CK inventory (no Out-of-Scope filter); coverage percentages will be lower (~5–10%) but uncontested. Architect + PM joint-review the tactical-grouping rationale before ADR Acceptance.*
- **`agentic-app` and `consumer-agent-app` deliberate exclusion**: Out-of-scope per Stream 4 baseline scope (FR-005). These two example directories exist but lack `security-report.pdf.baseline` files by prior feature scope (F-3 / F-4 PRD boundaries); F-241 does not introduce baselines for them.
- **Findings that cite a taxonomy ID resolving to an `out_of_scope: true` record**: How does the Coverage Attestation section handle citations to Out-of-Scope items? *The aggregator denominator excludes Out-of-Scope records, so Out-of-Scope citations don't inflate the coverage percentage; the cited Out-of-Scope item still renders on the per-finding attribution table for traceability but doesn't appear in the per-framework aggregate denominator.*
- **Catalog-resolvable vs prose-only ATLAS / ATT&CK references**: How does the spec handle ATLAS / ATT&CK techniques that don't yet appear in the catalog YAMLs? *Per F-7 / F-6 precedent: prose-only references appear in finding `references:` arrays as narrative context only; catalog-resolvable references appear in `source_attribution` arrays. F-241 expands the catalogs so the prose-only / catalog-resolvable boundary shifts toward catalog-resolvable for ATT&CK + ATLAS.*

---

## Requirements *(mandatory)*

### Functional Requirements

#### Stream 1 — F-A3 Populator Wiring (11 host agents)

- **FR-001** (Wave 1, Day 1–5): Wire `source_attribution` inline in the Detection Workflow / Example Findings block of the five STRIDE-heavy host agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`) per the F-1/F-2/F-4 net-new agent precedent. Each agent gains a `source_attribution` example block citing one `primary` taxonomy + ≥1 `related` CWE per pattern category in its companion catalog.
- **FR-002** (Wave 2, Day 6–11): Wire `source_attribution` inline in the remaining six host agents (`denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`) per the same precedent. The two AI/agentic hosts (`prompt-injection`, `agent-autonomy`) are wired explicitly because the report aggregator reads only the `source_attribution` array directly with no implicit prefix-attribution path.
- **FR-003** (Wave 1 Day 5 smoke test): Run F-A3 wiring smoke test on three baselines (`web-app` + `agentic-app` + `predictive-ml-app`) at end of Wave 1 to surface per-agent variance early across STRIDE / AI / ML coverage families before Wave 2 begins.
- **FR-004**: Populator wiring is additive only — no functional changes to existing detection logic, no removal of existing pattern categories, no modifications to companion `detection-patterns.md` Pattern Category → Primary Source maps. Each host agent's file remains under the ADR-036 200-line cap post-wiring.
- **FR-005**: At feature close, `grep -l "source_attribution" .claude/agents/tachi/*.md` returns 14 of 14 detection-tier files. No detection-tier agent remains in F-A3 deferral.

#### Stream 2 — Six Partial Web/API Item Closure

- **FR-006** (A05, A06, API8, API10 — Architect Q-Architect-2 closeable under existing patterns): Close each item via Primary Source addition + Indicator extension on the affected companion `detection-patterns.md` file. Target hosts: `tachi-privilege-escalation` (A05, API8), `tachi-tampering` (A06), `tachi-tampering` + `tachi-info-disclosure` (API10 cross-reference for Injection + SSRF surfaces).
- **FR-007** (API6, API9 — Architect Q-Architect-2 likely require new Indicator categories): Close each item via at most one new Indicator category in the affected companion catalog (target hosts: `tachi-tool-abuse` or `tachi-privilege-escalation` for API6; `tachi-info-disclosure` or `tachi-repudiation` for API9). Each new Indicator category carries citation evidence (Primary Source block) per the F-A1 schema and BLP-01 §8 Quality Bar.
- **FR-008** (Deferral path for any non-closing item): If any of the six items cannot close under existing patterns + the at-most-one-new-Indicator-category allowance, the item is explicitly Deferred with a new ADR rationale + follow-on Issue. The deferral surfaces during Stream 2 audit (Week 2–3), not at feature close.

#### Stream 3 — Taxonomy YAML Expansion

- **FR-009**: Expand `schemas/taxonomy/mitre-attack.yaml` from 38 records to the full ATT&CK Enterprise item inventory using **tactical-grouping Out-of-Scope strategy**: tactic-level Out-of-Scope rationale on the design-time-irrelevant tactics (TA0005 Defense Evasion, TA0007 Discovery, TA0008 Lateral Movement, TA0009 Collection, TA0010 Exfiltration, TA0011 Command and Control, TA0040 Impact). Per-item Out-of-Scope rationale only on items inside in-scope tactics (TA0001 Initial Access, TA0002 Execution, TA0003 Persistence, TA0004 Privilege Escalation, TA0006 Credential Access, TA0042 Resource Development).
- **FR-010**: Expand `schemas/taxonomy/mitre-atlas.yaml` from 12 records to the full ATLAS item inventory (~30 records target) with per-item Out-of-Scope annotations where applicable.
- **FR-011**: Audit `schemas/taxonomy/owasp.yaml` (already populated at 60 records: A01–A10, API1–API10, ASI01–ASI10, LLM01–LLM10, M1–M10, ML01–ML10) for citation completeness — every Covered item attests at least one agent + one detection-pattern category citation per BLP-01 §8 Quality Bar. No new OWASP rows are added; the audit confirms each existing row carries a defensible citation chain.
- **FR-012**: Each taxonomy YAML record gains exactly two new fields per the F-A1 ADR-027 D1 record-shape extension: `out_of_scope: bool` (default `false`) and `out_of_scope_rationale: string` (default empty). Existing F-A1 records that omit these fields parse correctly under YAML defaults (backward-compat preserved).

#### Stream 4 — Pipeline-Generated Coverage Percentage and Baseline Regen

- **FR-013**: Extend the report aggregator with per-framework coverage-percentage computation: for each of 5 framework taxonomies (OWASP, ATT&CK, ATLAS, NIST AI RMF, CWE), compute `% coverage = |cited_ids| / |taxonomy_ids_not_out_of_scope|` with the Out-of-Scope filter applied at the denominator. Existing partial / gap counts and rendering contract preserved unchanged.
- **FR-014**: Aggregator extension preserves the stdlib-only module-load invariant: any new YAML / library imports remain inside function bodies (deferred imports), not at module level. A new test asserts this invariant holds.
- **FR-015**: Regenerate all eight example baselines under `SOURCE_DATE_EPOCH=1700000000`: six pre-existing baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) plus two net-new baselines (`predictive-ml-app`, `mobile-banking-app`).
- **FR-016**: Non-Coverage-Attestation pages of all eight baseline PDFs remain byte-identical under fixed-epoch regen. The eight `security-report.pdf.baseline` files are intentionally updated only on Coverage Attestation pages with the populated section.

#### Cross-Cutting Requirements

- **FR-017**: Public per-feature ADR (ADR-037, next available) is committed Proposed → Accepted via the dual-commit pattern. ADR documents:
  - Combined attestation + populator-wiring scope across four work streams
  - F-A3 closure across 11 host agents (clearing the 4-feature deferral debt accumulated across ADR-032 / ADR-034 D-8 / ADR-035 D-10 / ADR-036 D-10)
  - Six Partial→Covered reclassifications with their evidence trail (or explicit deferrals with follow-on Issues)
  - ATT&CK + ATLAS coverage percentages with their tactical-grouping Out-of-Scope rationale
  - Eight-baseline scope expansion (Q-Architect-4 resolution)
  - The taxonomy YAML record-shape +2-field extension acknowledged per Architect MEDIUM-A
- **FR-018**: BLP-01 §6 Coverage Matrix in `_internal/strategy/BLP-01-threat-coverage.md` is annotated *"historical — superseded by pipeline-generated attestation"* with a pointer to the F-B Coverage Attestation section. The matrix is no longer the source of truth for coverage claims.
- **FR-019**: Four new test scripts land under `tests/scripts/`:
  - F-A3 populator wiring audit (asserts 14/14 detection-tier agents emit `source_attribution`)
  - Coverage attestation audit (walks taxonomy YAMLs, resolves each citation to an existing agent + detection-pattern category)
  - Coverage-percentage cross-check (independently computes coverage % from fixture findings; asserts equality with aggregator output)
  - Stdlib-only module-load invariant audit (asserts YAML imports remain in function bodies)
- **FR-020**: `schemas/finding.yaml` shape unchanged at v1.8. Sixth zero-`finding.yaml`-bump BLP-01 detection feature (after F-3, F-5, F-6, F-7). Existing finding-ID prefixes (`S/T/I/E/R/AG/LLM/AGP/OI/MI/TE`) are reused; no new prefixes introduced.
- **FR-021**: F-7 28-file detection-tier zero-edit invariant preserved for non-target files: any companion `detection-patterns.md` not implicated by the Stream 2 six-Partial-item audit remains byte-identical.
- **FR-022**: Zero new runtime dependencies (empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`).
- **FR-023**: Zero functional orchestrator / dispatch-layer edits. All eleven target host agents already registered in dispatch + consumers list.
- **FR-024**: PR squash-merge uses `feat(241):` Conventional Commit title per `.claude/rules/git-workflow.md` two-step (Plan-stage + Deliver-stage) enforcement; release-please PR fires within ~30s post-merge per R12 verification.

### Key Entities *(include if feature involves data)*

- **Source Attribution Array**: A `source_attribution` field on each finding (introduced by ADR-028, schema v1.6) carrying a list of `{taxonomy, id, relationship}` records. `taxonomy` is one of 5 enum values (`owasp | mitre-attack | mitre-atlas | nist-ai-rmf | cwe`); `relationship` is one of 3 enum values (`primary | related | derived`).
- **Eleven F-A3 Target Host Agents**: The host agents that have never emitted `source_attribution` and require populator wiring — `spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`, `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`. Combined with the 3 net-new agents (F-1 `output-integrity`, F-2 `misinformation`, F-4 `human-trust-exploitation`), this completes the 14-agent detection tier.
- **Six Partial Web/API Items**: A05 (Security Misconfiguration), A06 (Vulnerable and Outdated Components), API6 (Unrestricted Access to Sensitive Business Flows), API8 (Security Misconfiguration), API9 (Improper Inventory Management), API10 (Unsafe Consumption of APIs). Each closes via Primary Source addition or new Indicator category, or surfaces explicit Deferral.
- **Three Taxonomy YAML Catalogs**: `owasp.yaml` (60 records, citation-completeness audit only), `mitre-attack.yaml` (38 → full Enterprise inventory with tactical-grouping), `mitre-atlas.yaml` (12 → ~30 record full inventory). Each record gains 2 new optional fields per the ADR-027 D1 record-shape extension.
- **Eight Example Architectures**: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`, `predictive-ml-app`, `mobile-banking-app`. The first six are pre-existing baselines; the last two are net-new baselines added per Architect Q-Architect-4 MEDIUM resolution.
- **Public Per-Feature ADR (ADR-037)**: The next available ADR documenting combined F-8 + F-A3 scope, four work streams, F-A3 closure, six Partial item dispositions, tactical-grouping rationale, eight-baseline scope, and the taxonomy YAML record-shape extension.
- **BLP-01 §6 Coverage Matrix**: The hand-curated matrix in `_internal/strategy/BLP-01-threat-coverage.md` that F-241 demotes from source-of-truth status to historical-only; replaced by pipeline-generated attestation in the F-B Coverage Attestation section.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**F-A3 populator-wiring success criteria**:

- **SC-001**: All eleven target host agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`, `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`) emit `source_attribution` inline per the F-1/F-2/F-4 net-new agent precedent. Verified via grep returning **14 of 14** detection-tier files (3 pre-existing + 11 newly wired).
- **SC-002**: Every BLP-01 host-agent enrichment-feature populates `source_attribution` to at least the **primary** taxonomy citation per pattern category surfaced in F-1 through F-7 detection workflows.
- **SC-003**: Populator wiring is additive only — no functional changes to existing detection logic on the eleven target agents; ADR-036 baseline-line-count cap preserved (no host agent exceeds 200 lines).

**F-8 attestation success criteria**:

- **SC-004**: Zero Planned items remain in BLP-01 §6 Coverage Matrix across every adopted taxonomy.
- **SC-005**: Zero Partial items remain without an associated open PRD or an explicit deferral note with ADR rationale. Each of A05, A06, API6, API8, API9, API10 is either Covered (with citation evidence) or explicitly Deferred (with ADR + follow-on Issue).
- **SC-006**: Every Covered item in §6 cites at least one tachi agent and at least one detection-pattern category — verified by audit script that walks `schemas/taxonomy/owasp.yaml` and resolves each citation.
- **SC-007**: The F-B Coverage Attestation section renders end-to-end in **all eight example `security-report.pdf` outputs** with non-empty per-finding attribution tables and non-zero coverage-percentage values per taxonomy. Eight examples: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`, `predictive-ml-app`, `mobile-banking-app`.
- **SC-008**: `schemas/taxonomy/mitre-attack.yaml` and `schemas/taxonomy/mitre-atlas.yaml` contain the full item inventories. ATT&CK uses tactical-grouping Out-of-Scope strategy: 5–7 tactic-level Out-of-Scope rationales for design-time-irrelevant tactics, plus per-item Out-of-Scope rationale only on items inside in-scope tactics.
- **SC-009**: Per-framework coverage percentages published in the PDF match those computed against the taxonomy YAML inventories (denominator = `|taxonomy_ids_not_out_of_scope|`; numerator = `|cited_ids|`). Verification: regenerate `security-report.pdf` and cross-check coverage-percent values against an offline audit script with 0 percentage point delta.
- **SC-010**: BLP-01 §6 Coverage Matrix is annotated *"historical — superseded by pipeline-generated attestation"* with a pointer to the F-B section. The matrix is no longer the source of truth for coverage claims.

**Cross-cutting success criteria**:

- **SC-011**: Public per-feature ADR (ADR-037) is committed Proposed → Accepted via the dual-commit pattern, documenting the combined attestation + populator-wiring scope, the six Partial→Covered reclassifications with their evidence trail, the ATT&CK + ATLAS coverage percentages with their tactical-grouping Out-of-Scope rationale, the F-A3 populator-wiring closure, the eight-baseline scope expansion, and any explicit deferrals with follow-on Issues.
- **SC-012**: Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
- **SC-013**: Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **SC-014**: `schemas/finding.yaml` unchanged at v1.8 (zero `finding.yaml` shape change). `schemas/taxonomy/*.yaml` record shape gains exactly two new fields (`out_of_scope: bool` default `false`, `out_of_scope_rationale: string` default empty); the minimal record-shape extension to F-A1's ADR-027 D1 contract is acknowledged and accepted in the new public ADR. Existing F-A1 records that omit these fields parse correctly under YAML defaults (backward-compat preserved).
- **SC-015**: Existing baselines that previously regenerated byte-identically continue to do so under `SOURCE_DATE_EPOCH=1700000000`, **except** for the eight `security-report.pdf.baseline` files that are intentionally updated with the populated Coverage Attestation section. The intentional update is explicit and documented in the per-feature ADR.

**Operational success criteria**:

- **SC-016**: PR squash-merged with `feat(241):` Conventional Commit title; release-please PR fires within ~30s post-merge per R12 verification.
- **SC-017**: All four new test scripts (`test_f_a3_populator_wiring.py`, `test_coverage_attestation_audit.py`, `test_coverage_percentage_computation.py`, `test_pyyaml_deferred_import.py`) land green at delivery.
- **SC-018**: Stream 1 Wave 1 Day 5 smoke test passes on three baselines (`web-app` + `agentic-app` + `predictive-ml-app`) — surfaces per-agent variance early across STRIDE / AI / ML coverage families.

---

## Assumptions

- **A-1 (REVISED post-Architect Q1)**: F-A3 populator wiring is **REQUIRED** for SC-007 to hold. Empirically verified at PRD-review time — the report aggregator reads only `finding.source_attribution[].id` directly, with no implicit prefix-attribution path. F-A3 is in scope as Stream 1.
- **A-2 (PARTIALLY VALID per Architect Q-Architect-2)**: 4/6 Partial items (A05, A06, API8, API10) close cleanly under existing patterns; 2/6 (API6, API9) require new Indicator categories within FR-007's at-most-one-new-Indicator-category allowance. Validation passes.
- **A-3 (PARTIALLY VALID per Architect Q-Architect-3)**: MITRE ATT&CK Enterprise is ~600+ records; tactical-grouping Out-of-Scope strategy mandatory per Architect HIGH adjudication. Validation passes via FR-009.
- **A-4 (RESOLVED per Architect Q-Architect-4)**: F-6 + F-7 example architectures (`predictive-ml-app`, `mobile-banking-app`) MUST join the baseline scope. Eight baselines total per FR-015.
- **A-5**: Aggregator already computes coverage percentage at the F-B layer; F-241's incremental work is to wire the Out-of-Scope denominator filter and ensure all eight baselines exercise the surface end-to-end. (Verified during research at `_build_per_framework_aggregate()` line 1144 of `extract-report-data.py`.)
- **A-6**: All 11 companion `references/detection-patterns.md` files exist with Pattern Category → Primary Source maps already populated through F-7. F-A3 wiring requires no companion-catalog edits beyond Stream 2's six Partial item closures.
- **A-7**: Calendar model (Team-Lead HIGH-R1 normalization): "Day N" = Nth working day from Day 1 = Thu 2026-04-30. Memorial Day Mon 2026-05-25 is non-working inside Week 5 (4 working days that week). Delivery window: Day 1 (Thu 2026-04-30) → Day 29 (Wed 2026-06-10).
- **A-8**: All 10 upstream dependencies (F-A1 / F-A2 / F-B / F-1..F-7) are SATISFIED as of 2026-04-29.

---

## Plan-Day Decision Deferrals

The following PRD-level questions carry forward to the Plan stage for resolution during `/aod.project-plan`:

| ID | Question | PRD Default | Owner | Resolves At |
|----|----------|-------------|-------|-------------|
| Q-PM-1 | Should the public-facing ADR be split into two ADRs (one for F-8 attestation, one for F-A3 populator wiring + ADR-027 D1 record-shape extension), or a single combined ADR-037? | Single combined ADR-037 (PM v1.2 default; Architect MEDIUM-A recommends "separate ADR alongside ADR-037" for the schema-shape extension). | product-manager + architect | Day 1 (during plan.md authoring) |
| Q-Plan-1 | Which Stream 2 closure path does API6 take — `tachi-tool-abuse` Indicator addition vs `tachi-privilege-escalation` Indicator addition? Both are in-scope per FR-007; which architectural fit is stronger? | `tachi-tool-abuse` (PRD §6 Indicator placement default) | architect | Day 1 (during plan.md authoring); reaffirmed Day 12 of build (Stream 2 audit) |
| Q-Plan-2 | Which Stream 2 closure path does API9 take — `tachi-info-disclosure` Indicator addition vs `tachi-repudiation` Indicator addition? | `tachi-info-disclosure` (PRD §6 Indicator placement default) | architect | Day 1 (during plan.md authoring); reaffirmed Day 13 of build (Stream 2 audit) |

---

## Out of Scope (Explicit)

The following are explicitly **NOT** in scope for F-241:

1. **No new threat agents** — F-241 is attestation + populator wiring, not enrichment. Net-new detection patterns are out of scope unless a Partial item's closure requires a citation-grounded category addition (FR-007 allowance). The F-7 28-file detection-tier zero-edit invariant carries forward for files outside Stream 2 + Stream 1 wiring scope.
2. **No `schemas/finding.yaml` shape change** — schema preserved at v1.8. F-241 reuses existing `S/T/I/E/R/AG/LLM/AGP/OI/MI/TE` finding-ID prefixes. Zero new finding-ID prefixes introduced.
3. **No cross-framework reasoning surface** — F-B ADR-029 narrowed MVP to per-framework intra-taxonomy attestation. F-241 *populates* that surface rather than expanding it. The cross-framework crosswalk JOIN remains out-of-MVP scope.
4. **No new orchestrator or dispatch-layer edits** — all eleven target host agents already registered in dispatch + consumers list.
5. **No new runtime dependencies** — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.
6. **No new agent files** — file count on `.claude/agents/tachi/*.md` unchanged at 14 detection-tier files post-feature.
7. **No `agentic-app` or `consumer-agent-app` baselines** — these example directories exist (per F-3 and F-4 PRD scope) but lack `security-report.pdf.baseline` files; F-241 does not introduce baselines for them. Eight-baseline scope is bounded to: 6 pre-existing + `predictive-ml-app` + `mobile-banking-app`.
8. **No AIVSS scoring formula adoption** — adopters wanting AIVSS-style risk math compute it externally on tachi's machine-readable output.
9. **No vendor-specific framework adoption** beyond the OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE 5-value taxonomy enum already established by ADR-028.
10. **No NIST AI RMF or CWE Top 25 record-count expansion** unless found incomplete during Stream 3 audit (Should Have / P1, not Must Have / P0; if found incomplete, the F-A1 seed is retained as-is and the gap surfaces as a follow-on Issue rather than a Stream 3 expansion task).
11. **No expansion of the F-B rendering surface** — no new Typst pages, no new conditional-inclusion booleans beyond the existing `has-source-attribution`.
12. **No demotion or removal of the §6 Coverage Matrix file itself** — the file remains in `_internal/strategy/BLP-01-threat-coverage.md` and continues to be readable; only its source-of-truth status is demoted via the *"historical — superseded"* annotation (FR-018).
