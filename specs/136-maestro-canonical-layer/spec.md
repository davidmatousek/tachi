---
prd_reference: docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-10
    status: APPROVED
    notes: "Spec fully implements PRD. All PRD FRs mapped to atomic spec FRs (001-047). All architect concerns from PRD attempt 2 honored (Integration Services third-way bug, historical exclusions, release-please, README lines, ADR-019 rule). No scope drift. 15 SCs measurable."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Canonical Layer Correctness Fix

**Feature Branch**: `136-maestro-canonical-layer`
**Created**: 2026-04-10
**Status**: Approved (PM)
**Input**: PRD 136 — MAESTRO Canonical Layer Correctness Fix
**PRD Reference**: `docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md`
**Research Reference**: `specs/136-maestro-canonical-layer/research.md`

---

## Overview

Tachi ships a MAESTRO seven-layer taxonomy that claims to be "the single source of truth" citing CSA. Three of seven layer names (L5, L6, L7) do not match the canonical CSA Ken Huang taxonomy, the acronym expansion is non-canonical, and a third divergent layer name ("Integration Services") exists in the Typst PDF template that matches neither the shared reference nor the canonical spec. This spec describes a coordinated correctness fix that aligns all layer references with the canonical CSA taxonomy, introduces the missing L5 Evaluation and Observability keyword set, updates downstream artifacts (schema enum, examples, golden fixtures, PDF baselines), and documents the breaking change in CHANGELOG. The fix is scoped to Phase 1 only; Phases 2–4 from the discovery item (cross-layer attack chain analysis, agentic threat patterns, AIVSS evaluation) are explicitly deferred to separate PRDs.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Canonical Shared Reference Alignment (Priority: P1)

As a tachi maintainer, when I read the shared MAESTRO reference file (`.claude/skills/tachi-shared/references/maestro-layers-shared.md`), I see canonical CSA layer names, the canonical acronym expansion, and a keyword set that correctly separates observability components (L5), security/compliance components (L6), and agent-ecosystem / user-facing components (L7). The shared reference no longer contradicts external canonical MAESTRO documentation.

**Why this priority**: This is the foundational correctness fix. All downstream artifacts (schema, examples, Typst templates, CHANGELOG) depend on the shared reference as the single source of truth. Without this, the feature has no meaning.

**Independent Test**: Read the shared reference file after the fix. Verify: (a) line 17 acronym expansion matches canonical CSA; (b) the seven-layer taxonomy table rows for L5/L6/L7 match canonical names; (c) the L5 keyword section contains the new observability keywords; (d) the L6 keyword section contains the (renamed) security keywords; (e) the L7 keyword section contains the merged agent-ecosystem + user-facing keywords. This can be validated by file inspection with no pipeline run required.

**Acceptance Scenarios**:

1. **Given** the shared reference file at `.claude/skills/tachi-shared/references/maestro-layers-shared.md`, **when** a reader opens the file, **then** line 17 reads "Multi-Agent Environment, Security, Threat, Risk, and Outcome" as the MAESTRO acronym expansion (canonical CSA form)
2. **Given** the same file, **when** a reader looks at the Seven-Layer Taxonomy table, **then** row L5 is named "Evaluation and Observability", row L6 is "Security and Compliance", and row L7 is "Agent Ecosystem" — with descriptions and example components that match canonical CSA sources
3. **Given** the Keyword-to-Layer Mapping section, **when** a reader reviews the L5 section, **then** it contains the new observability keywords (audit log, monitoring, observability, telemetry, anomaly detection, SIEM, forensics, behavioral monitoring, metrics, human oversight, log aggregation)
4. **Given** the same section, **when** a reader reviews the L6 section, **then** it contains the security keywords previously under L5 (auth, WAF, firewall, secrets manager, guardrail, content filter, rate limit, encryption, RBAC, IAM, access control, security)
5. **Given** the same section, **when** a reader reviews the L7 section, **then** it contains the union of the previous L6 Agent Ecosystem keywords and the previous L7 User Interface keywords (multi-agent, agent-to-agent, swarm, delegation, coordination, supervisor, sub-agent, agent registry, agent mesh, chat UI, dashboard, admin console, web interface, frontend, user portal, API endpoint, REST API, GraphQL, client, user)
6. **Given** the Ordering Rationale prose, **when** a reader reviews it after the fix, **then** the specificity gradient explanation reflects the new layer order: L1 most specific (foundation model keywords), L7 most general (agent ecosystem catch-all including user interface)
7. **Given** the WARNING note about classification ordering, **when** a reader reviews it, **then** the warning remains in place with text updated to reflect the new layer order

---

### User Story 2 - Observability Layer Classifies Detective Controls (Priority: P1)

As a security engineer running tachi on an agentic system with audit logging, behavioral monitoring, and anomaly detection components, when I run the tachi pipeline, the finding targeting the observability component (e.g., Audit Logger) classifies to "L5 — Evaluation and Observability" in the threats.md output. I see a dedicated layer for detective controls in the MAESTRO Findings section of the PDF security report instead of the finding being lost in Unclassified or misrouted to Security.

**Why this priority**: This delivers the core value of the fix — a category of findings that was previously lost now has a canonical home. It is the end-to-end validation that keyword reassignment + schema rename + pipeline propagation all work together correctly.

**Independent Test**: Run the extract-report-data.py script against the regenerated `examples/agentic-app/threats.md` (which contains an Audit Logger component). Verify the Audit Logger component classifies to "L5 — Evaluation and Observability" in the component inventory, and that at least one finding targeting the Audit Logger (known candidate: Tampering T-3, but any STRIDE category is acceptable) inherits that layer value in the finding table. This can be tested independently by manual spot-check of a single example output.

**Acceptance Scenarios**:

1. **Given** the agentic-app example architecture with an Audit Logger component, **when** the tachi orchestrator runs Phase 1 classification after the keyword reassignment, **then** the Audit Logger component classifies to "L5 — Evaluation and Observability" in the component inventory section of `examples/agentic-app/threats.md`
2. **Given** the same example, **when** Phase 3 finding inheritance runs, **then** at least one finding whose `component` field is "Audit Logger" (known candidate: Tampering T-3, but any STRIDE category qualifies) has its `maestro_layer` field set to "L5 — Evaluation and Observability"
3. **Given** the regenerated `examples/agentic-app/sample-report/threats.md` file, **when** a reader searches for "L5 — Evaluation and Observability", **then** at least one row in the component inventory and at least one row in the findings table contains this value
4. **Given** the regenerated `examples/agentic-app/sample-report/security-report.pdf`, **when** a reader views the MAESTRO Findings page, **then** the "L5 — Evaluation and Observability" layer band contains at least one finding and does not show "Integration Services" or "Security" as the layer name anywhere
5. **Given** the `dashboard` keyword (present in L7 per FR-006), **when** the Wave 0 pre-edit grep runs over example component descriptions, **then** no example component is misclassified due to ambiguous `dashboard` matching (the first-match-wins ordering with observability-specific keywords in L5 resolves the ambiguity)

---

### User Story 3 - Schema Enum and Downstream Migration (Priority: P1)

As a downstream tachi adopter who has built dashboards, scripts, or tooling against the `maestro_layer` enum values in `schemas/finding.yaml`, when I upgrade to the next tachi release, I see a CHANGELOG entry clearly documenting the layer name changes, old → new value mapping, and schema version bump so I can update my tooling in a single coordinated release.

**Why this priority**: This is the accountability story. Without explicit migration documentation, downstream users will silently break when upgrading. The CHANGELOG + schema version bump together signal the breaking change.

**Independent Test**: Read CHANGELOG.md after the fix. Verify the entry contains: (a) a label indicating this is a correctness fix, (b) old → new enum value mapping for L5, L6, L7, (c) acronym expansion correction note, (d) schema version bump note, (e) migration guidance for downstream consumers. This can be validated by file inspection with no pipeline run required.

**Acceptance Scenarios**:

1. **Given** the updated `schemas/finding.yaml`, **when** a reader inspects the `maestro_layer` enum values, **then** the three changed values read exactly "L5 — Evaluation and Observability", "L6 — Security and Compliance", "L7 — Agent Ecosystem" (em dash separator with spaces, matching the existing L1–L4 format)
2. **Given** the same schema file, **when** a reader checks the schema version field, **then** it reads 1.3 (bumped from 1.2)
3. **Given** the updated `CHANGELOG.md`, **when** a reader locates the new entry, **then** the entry explicitly labels this as a correctness fix aligning with canonical CSA MAESTRO (not a feature addition)
4. **Given** the same CHANGELOG entry, **when** a reader reviews the migration section, **then** it contains the complete old → new enum value mapping: "L5 — Security" → "L5 — Evaluation and Observability", "L6 — Agent Ecosystem" → "L6 — Security and Compliance", "L7 — User Interface" → "L7 — Agent Ecosystem"
5. **Given** the same CHANGELOG entry, **when** a reader reviews it, **then** it notes the acronym expansion correction from "Multi-Agent Environment Security Toolkit for Reasoning and Orchestration" to "Multi-Agent Environment, Security, Threat, Risk, and Outcome"
6. **Given** the release-please workflow (`release-please-config.json`), **when** the next release is cut, **then** the schema bump 1.2 → 1.3 ships inside tachi v4.10.0 (minor release, not major), consistent with release-please's configured minor version track

---

### User Story 4 - Regenerated Example Outputs (Priority: P1)

As a tachi user browsing the `examples/*` directories, when I open any example architecture's threat model outputs (threats.md, security-report.pdf.baseline), I see canonical L5/L6/L7 layer names throughout. No example contains stale layer names like "Security" (for L5), "Agent Ecosystem" (for L6), or "User Interface" (for L7). The examples work as accurate reference implementations of canonical MAESTRO classification.

**Why this priority**: Examples are the primary way users learn what tachi outputs look like. Stale examples would silently teach users the wrong taxonomy and undermine the entire correctness fix.

**Independent Test**: Run the `test_backward_compatibility.py` test after regenerating the five non-agentic-app baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). Verify: (a) all five baselines regenerate byte-deterministically under `SOURCE_DATE_EPOCH=1700000000`; (b) the test passes against the new baselines; (c) a manual grep for old layer names across all example files returns zero matches. The agentic-app sample-report is validated separately via manual spot-check.

**Acceptance Scenarios**:

1. **Given** all six example architectures in `examples/*`, **when** the pipeline regenerates each example's `threats.md` file, **then** every row in the component inventory and findings tables shows canonical layer names — no occurrence of "L5 — Security", "L6 — Agent Ecosystem", "L6 — Integration Services", or "L7 — User Interface" remains
2. **Given** the five non-agentic-app examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice), **when** their `security-report.pdf.baseline` files are regenerated with `SOURCE_DATE_EPOCH=1700000000`, **then** the baselines are byte-deterministic (running the generation twice produces identical bytes)
3. **Given** the five non-agentic-app baselines after regeneration, **when** `test_backward_compatibility.py` runs, **then** the test passes (i.e., the freshly-generated PDFs match the committed baselines byte-for-byte)
4. **Given** the `examples/agentic-app/sample-report/` directory, **when** its full pipeline regenerates (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, security-report.pdf, threat-*.jpg, threat-*-spec.md, risk-scores.sarif, threats.sarif, attack-trees/), **then** every file uses canonical layer names
5. **Given** the `examples/mermaid-agentic-app/` directory (which has threat-report.md and threat-infographic-spec.md in addition to baselines), **when** these files are regenerated, **then** canonical layer names appear throughout
6. **Given** a grep across all `examples/*` files for the old layer names "L5 — Security", "L6 — Agent Ecosystem", "L6 — Integration Services", "L7 — User Interface", **then** zero matches are returned after the fix
7. **Given** a grep across the same files for the old acronym "Multi-Agent Environment Security Toolkit for Reasoning and Orchestration", **then** zero matches are returned after the fix

---

### User Story 5 - Typst Template Canonical Alignment (Priority: P1)

As a tachi adopter generating a PDF security report, when I view the MAESTRO Findings page in the PDF, the layer band labels match canonical CSA MAESTRO names exactly. The pre-existing internal inconsistency where the Typst template used "Integration Services" for L6 (not matching anything) is corrected alongside the canonical rename.

**Why this priority**: The Typst template's fallback dictionary was the source of a pre-existing three-way divergence (template says "Integration Services", shared ref says "Agent Ecosystem", canonical says "Security and Compliance"). Fixing this is load-bearing for every PDF security report tachi generates.

**Independent Test**: Read `templates/tachi/security-report/maestro-findings.typ` and `templates/tachi/security-report/main.typ` after the fix. Verify each hardcoded layer name matches the canonical values. Then regenerate one example PDF baseline and verify the MAESTRO Findings page displays canonical labels.

**Acceptance Scenarios**:

1. **Given** `templates/tachi/security-report/maestro-findings.typ`, **when** a reader inspects lines 132-134 (the fallback dictionary), **then** the values read: `"L5": "Evaluation and Observability"`, `"L6": "Security and Compliance"`, `"L7": "Agent Ecosystem"` — with the "Integration Services" third-way bug corrected
2. **Given** the same file, **when** a reader reads line 121 (the prose describing the MAESTRO layers), **then** it no longer references "User Interface (L7)" and instead references "Agent Ecosystem (L7)" (or equivalent canonical phrasing)
3. **Given** `templates/tachi/security-report/main.typ`, **when** a reader reads line 293 (the executive summary text mentioning MAESTRO), **then** it references canonical L1–L7 names
4. **Given** a regenerated PDF from any example, **when** a reader views the MAESTRO Findings page, **then** all seven layer band labels match canonical CSA names with no occurrence of "Security", "Integration Services", or "User Interface" as layer names

---

### User Story 6 - Pipeline Documentation and ADR Updates (Priority: P2)

As a contributor reading tachi's agent pipeline documentation and architectural decision records, when I encounter any reference to MAESTRO layers, I see canonical names. ADR-020 includes a revision note pointing forward to Feature 136 so future readers understand the canonical alignment happened after the original feature shipped.

**Why this priority**: Secondary to the data-level correctness but important for contributor onboarding. Stale documentation is a maintenance burden that slowly drifts the team's mental model away from the canonical taxonomy.

**Independent Test**: Grep all `.claude/skills/tachi-orchestration/references/`, `.claude/skills/tachi-shared/references/`, `docs/architecture/02_ADRs/`, and `README.md` for the old layer names. Verify zero stale matches remain (excluding historical PRDs 084 and 091, which are frozen records of what shipped).

**Acceptance Scenarios**:

1. **Given** `.claude/skills/tachi-orchestration/references/dispatch-rules.md`, **when** a reader reads line 149, **then** the example row no longer shows "L7 — User Interface" and instead shows "L7 — Agent Ecosystem"
2. **Given** `.claude/skills/tachi-shared/references/finding-format-shared.md`, **when** a reader reads line 64 (the enum list), **then** the values match the new canonical names
3. **Given** `README.md`, **when** a reader reads the layer table at lines 260-262, **then** rows L5, L6, L7 show canonical names and descriptions
4. **Given** `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md`, **when** a reader reads line 123 (the acronym citation), **then** it shows the canonical acronym expansion
5. **Given** ADR-020, **when** a reader reviews it, **then** a revision note (brief, 1-3 lines) appears near the top pointing to Feature 136 as the source of canonical alignment
6. **Given** the historical PRDs `docs/product/02_PRD/084-*.md` and `docs/product/02_PRD/091-*.md`, **when** inspected after the fix, **then** they remain unchanged (frozen historical records per PRD exclusion)
7. **Given** the historical spec directories `specs/084-*/` and `specs/091-*/`, **when** inspected after the fix, **then** they remain unchanged (frozen historical records per PRD exclusion)

---

### User Story 7 - Wave 0 Pre-Edit Discovery Report (Priority: P2)

As a code reviewer examining the single-coordinated PR for Feature 136, I can read a committed discovery report that documents the results of a pre-edit grep sweep. The report confirms all hardcoded layer name references were found before editing began, giving me confidence that the fix is complete and no references were silently missed.

**Why this priority**: Risk mitigation for the single-coordinated-PR constraint. The discovery report is the audit trail proving scope completeness.

**Independent Test**: Read `specs/136-maestro-canonical-layer/discovery-report.md` after the fix. Verify it contains: (a) the list of grep patterns run, (b) the list of files matched for each pattern, (c) a line count of matches per file, (d) a confirmation statement that every match was addressed in the PR (or an explicit "excluded: historical" annotation).

**Acceptance Scenarios**:

1. **Given** the feature branch, **when** a reader opens `specs/136-maestro-canonical-layer/discovery-report.md`, **then** the report exists and contains sections for each of the 7 required grep patterns from PRD FR-9
2. **Given** the discovery report, **when** a reader reviews each pattern section, **then** it lists every file matched and explicitly annotates each as "updated in this PR" or "historical — excluded per PRD"
3. **Given** the discovery report, **when** a reader checks the `dashboard` keyword pre-validation section, **then** it documents the analysis of example component names and confirms no ambiguous classifications exist (or documents the resolution if any do)
4. **Given** the final PR diff, **when** compared against the discovery report, **then** every file listed as "updated in this PR" in the report appears in the PR diff (no missed files)

---

### User Story 8 - Backward Compatibility Validation Gate (Priority: P1)

As a tachi maintainer reviewing the Feature 136 PR, I can run the existing `test_backward_compatibility.py` against the regenerated baselines and verify it passes — proving byte-determinism under `SOURCE_DATE_EPOCH=1700000000`. The existing test infrastructure from Feature 128 continues to work and catches any non-deterministic changes in the regeneration process.

**Why this priority**: This is the quantitative safety net for the PR. Without this gate, a non-deterministic PDF regeneration would introduce noise that makes the PR unreviewable.

**Independent Test**: After regenerating the five non-agentic-app baselines, run `pytest tests/scripts/test_backward_compatibility.py` with `SOURCE_DATE_EPOCH=1700000000` in the environment. The test must pass. The test must also continue to pass when rerun a second time (idempotency check).

**Acceptance Scenarios**:

1. **Given** the regenerated baselines for web-app, microservices, ascii-web-api, mermaid-agentic-app, and free-text-microservice, **when** `pytest tests/scripts/test_backward_compatibility.py` runs with `SOURCE_DATE_EPOCH=1700000000`, **then** the test passes (all PDFs match their committed baselines byte-for-byte)
2. **Given** the same regenerated baselines, **when** the test runs a second time, **then** it still passes (idempotency verified)
3. **Given** the existing 150+ pytest suite from Feature 128, **when** the full test suite runs after the fix, **then** 100% of tests pass
4. **Given** the `agentic-app` example (which is excluded from test_backward_compatibility.py per Feature 128), **when** its sample-report is manually regenerated and inspected, **then** the MAESTRO Findings section in the PDF shows canonical layer names

---

### Edge Cases

- **What happens if the `dashboard` keyword misclassifies an existing example component?**
  Pre-validation in the Wave 0 grep sweep (User Story 7) checks example component names against the new L5 observability keywords to detect potential ambiguity. If a misclassification is detected, the resolution is to add the component's distinguishing keyword to L5 (e.g., `observability dashboard`) rather than remove `dashboard` from L7.

- **What happens if a regenerated PDF baseline fails byte-determinism?**
  `test_backward_compatibility.py` fails the PR. The contributor must debug the PDF generation pipeline to identify the non-deterministic source (typically a timestamp not covered by `SOURCE_DATE_EPOCH`). The fix is debugged and re-run until determinism is restored.

- **What happens if a hardcoded layer reference is discovered AFTER the PR merges?**
  A follow-up PR is opened. However, the Wave 0 pre-edit grep sweep (FR-041) is designed to catch all references before editing begins, making this edge case rare.

- **What happens if a downstream consumer has hardcoded the old enum values in their dashboard?**
  The CHANGELOG migration note instructs them to update. The schema version bump 1.2 → 1.3 signals the breaking change to any version-aware consumer. Tachi does not provide a runtime compatibility shim for old enum values — this is an intentional correctness fix, not a gradual migration.

- **What happens if a component's description contains BOTH observability keywords and security keywords (e.g., "security audit log")?**
  First-match-wins classification with L1→L7 order resolves this. Since L5 (Evaluation and Observability) evaluates before L6 (Security and Compliance) in the new order, the component classifies as L5. The "audit log" keyword matches first.

- **What happens if a new MAESTRO-aware tool or skill is added AFTER this PR but before it merges, referencing the old layer names?**
  The PR must be rebased and the new references updated before merge. The discovery report (User Story 7) serves as the audit trail for this check.

- **What happens if the Typst template has hardcoded references the Wave 0 grep missed?**
  The grep pattern for "Integration Services" (already a pre-review find) plus "User Interface" plus "L5 — Security" is designed to be exhaustive for the known Typst fallback dictionary pattern. If somehow missed, the regenerated PDF would display a wrong label and catch the error during manual spot-check (User Story 5, acceptance scenario 4).

---

## Requirements *(mandatory)*

### Functional Requirements

**Shared Reference and Classification Algorithm**

- **FR-001**: The shared MAESTRO reference file (`.claude/skills/tachi-shared/references/maestro-layers-shared.md`) MUST use canonical CSA seven-layer taxonomy names: L1 Foundation Models, L2 Data Operations, L3 Agent Frameworks, L4 Deployment Infrastructure, L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem
- **FR-002**: The acronym expansion at line 17 of the shared reference MUST read "Multi-Agent Environment, Security, Threat, Risk, and Outcome" (canonical CSA form)
- **FR-003**: The Seven-Layer Taxonomy table in the shared reference MUST have exactly seven rows with descriptions and example components matching canonical CSA sources for each layer
- **FR-004**: A new L5 keyword section MUST exist covering: audit log, monitoring, observability, telemetry, anomaly detection, SIEM, forensics, behavioral monitoring, metrics, human oversight, log aggregation
- **FR-005**: The L6 keyword section MUST contain the keywords previously assigned to L5 Security: auth, WAF, firewall, secrets manager, guardrail, content filter, rate limit, encryption, RBAC, IAM, access control, security
- **FR-006**: The L7 keyword section MUST contain the union of the previous L6 Agent Ecosystem keywords and the previous L7 User Interface keywords (listed in US-1 Acceptance Scenario 5)
- **FR-007**: The classification algorithm MUST preserve first-match-wins semantics with L1→L7 evaluation order (no change to algorithm itself, only to keyword contents)
- **FR-008**: The Ordering Rationale section in the shared reference MUST explain the new specificity gradient (L1 most specific, L7 Agent Ecosystem broadest catch-all including user-facing components)
- **FR-009**: The shared reference's WARNING note about classification ordering being load-bearing MUST remain in place with updated text reflecting the new layer order
- **FR-010**: The `audit log` keyword MUST appear only in the new L5 section, not in L6 (moved from its previous L5 Security location to the new L5 Evaluation and Observability)
- **FR-011**: The `dashboard` keyword MUST appear only in the new L7 section (disambiguation relies on first-match-wins ordering with L5 observability keywords evaluated first)

**Schema Updates**

- **FR-012**: The `schemas/finding.yaml` `maestro_layer` enum MUST contain the canonical values "L5 — Evaluation and Observability", "L6 — Security and Compliance", "L7 — Agent Ecosystem" (em dash separator with spaces)
- **FR-013**: The `schemas/finding.yaml` schema version MUST be bumped from 1.2 to 1.3 to signal the breaking enum-value change
- **FR-014**: The schema file comments or documentation MUST reflect the canonical alignment (e.g., a brief note indicating Feature 136 aligned the enum with canonical CSA)
- **FR-015**: The `.claude/skills/tachi-shared/references/finding-format-shared.md` file at line 64 MUST match the new schema enum values

**Typst Template Updates**

- **FR-016**: The `templates/tachi/security-report/maestro-findings.typ` fallback dictionary at lines 132-134 MUST read `"L5": "Evaluation and Observability"`, `"L6": "Security and Compliance"`, `"L7": "Agent Ecosystem"` — correcting the pre-existing third divergent name "Integration Services"
- **FR-017**: The same file's prose at line 121 MUST reference canonical layer names (not "User Interface (L7)")
- **FR-018**: The `templates/tachi/security-report/main.typ` prose at line 293 MUST reference canonical L1–L7 names
- **FR-019**: The Typst templates MUST preserve their data-driven structure — fallback dictionary values are used only when `layer-name` data is absent

**Pipeline Documentation Updates**

- **FR-020**: The `.claude/skills/tachi-orchestration/references/dispatch-rules.md` example at line 149 MUST reference canonical layer names (e.g., "L7 — Agent Ecosystem" instead of "L7 — User Interface")
- **FR-021**: Any pipeline reference documents that mention specific L5/L6/L7 layer names MUST be updated to canonical names (discovered via Wave 0 grep sweep)

**Repository Documentation**

- **FR-022**: The repository `README.md` layer table at lines 260-262 MUST show canonical L5/L6/L7 names with updated descriptions
- **FR-023**: `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` line 123 MUST show the canonical acronym expansion
- **FR-024**: ADR-020 MUST include a revision note (brief, 1-3 lines) pointing to Feature 136 as the canonical alignment fix — placed either in a new "Revision History" section or as a note near the top of the document
- **FR-025**: A one-line rule MUST be added to ADR-019 (or another designated location — decided in plan.md) stating that enum-value-only breaking changes warrant a minor schema bump (x.y+1), not a major bump, provided schema shape and required fields are unchanged

**Example Output Regeneration**

- **FR-026**: All six example architectures in `examples/*` MUST have their `threats.md` files regenerated with canonical layer names in the component inventory and findings tables
- **FR-027**: The five non-agentic-app example `security-report.pdf.baseline` files MUST be regenerated with `SOURCE_DATE_EPOCH=1700000000` to maintain byte-determinism
- **FR-028**: The `examples/agentic-app/sample-report/` directory MUST have its full pipeline regenerated: threats.md, risk-scores.md, risk-scores.sarif, compensating-controls.md, threat-report.md, security-report.pdf, threat-*.jpg infographic images, threat-*-spec.md infographic specs, threats.sarif, attack-trees/
- **FR-029**: The `examples/mermaid-agentic-app/` directory's `threats.md`, `threat-report.md`, `threat-infographic-spec.md`, `security-report.pdf.baseline`, and `attack-trees/` MUST be regenerated
- **FR-030**: After regeneration, running a grep over all `examples/*` files for the old layer names ("L5 — Security", "L6 — Agent Ecosystem", "L6 — Integration Services", "L7 — User Interface") MUST return zero matches

**Golden Test Fixtures**

- **FR-031**: The golden fixtures `tests/scripts/fixtures/golden/maestro-heatmap.json` and `tests/scripts/fixtures/golden/maestro-stack.json` MUST be regenerated to reflect canonical layer names (specifically the `maestro_layer_distribution` array contents)
- **FR-032**: All existing pytest tests (150+ tests from Feature 128 bootstrap) MUST continue to pass after the regeneration

**Backward Compatibility Validation**

- **FR-033**: `tests/scripts/test_backward_compatibility.py` MUST pass against the regenerated baselines with `SOURCE_DATE_EPOCH=1700000000` set in the environment
- **FR-034**: The test MUST pass idempotently (a second run produces the same result)
- **FR-035**: The `examples/agentic-app/` regeneration MUST be manually spot-checked for canonical layer name display in the PDF (per the exclusion in `test_backward_compatibility.py`)

**CHANGELOG and Migration**

- **FR-036**: `CHANGELOG.md` MUST have a new entry explicitly labeled as a correctness fix (not a feature addition)
- **FR-037**: The CHANGELOG entry MUST include the complete old → new enum value mapping: "L5 — Security" → "L5 — Evaluation and Observability", "L6 — Agent Ecosystem" → "L6 — Security and Compliance", "L7 — User Interface" → "L7 — Agent Ecosystem"
- **FR-038**: The CHANGELOG entry MUST note the acronym expansion correction
- **FR-039**: The CHANGELOG entry MUST note the schema version bump 1.2 → 1.3
- **FR-040**: The CHANGELOG entry MUST reference Feature 136 / PR number for traceability

**Wave 0 Pre-Edit Discovery**

- **FR-041**: Before any file edits begin, a discovery sweep MUST run using the 7 grep patterns specified in PRD FR-9: (1) "User Interface", (2) "Security Toolkit for Reasoning and Orchestration", (3) "Integration Services", (4) "L5 — Security" and "L5 Security", (5) "L6 — Agent Ecosystem" and "L6 Agent Ecosystem", (6) "L7 — User Interface" and "L7 User Interface", (7) "dashboard" matches in example component names for pre-validation
- **FR-042**: The discovery sweep results MUST be captured in `specs/136-maestro-canonical-layer/discovery-report.md` as a committed audit trail
- **FR-043**: The discovery report MUST explicitly exclude historical PRDs (`docs/product/02_PRD/084-*.md`, `docs/product/02_PRD/091-*.md`) and historical spec directories (`specs/084-*/`, `specs/091-*/`) from the update scope
- **FR-044**: The discovery report MUST include a `dashboard` keyword pre-validation section documenting whether any example component names trigger the first-match-wins ambiguity — and if so, the resolution chosen

**Historical Exclusions**

- **FR-045**: Prior PRDs at `docs/product/02_PRD/084-*.md` and `docs/product/02_PRD/091-*.md` MUST NOT be modified — they are frozen historical records
- **FR-046**: Historical spec directories at `specs/084-*/` and `specs/091-*/` MUST NOT be modified — they are frozen historical records
- **FR-047**: Internal Python variable names in scripts (e.g., any `security_layer` identifiers) are out of scope and MUST NOT be renamed in this PR — only user-facing strings and data files change

---

### Key Entities

- **MAESTRO Layer**: A canonical categorization assigned to an architectural component during Phase 1 classification. Entity value is a string in the format "L{N} — {CanonicalName}" where N is 1-7 or "Unclassified". After this fix, the seven canonical names are: Foundation Models, Data Operations, Agent Frameworks, Deployment Infrastructure, Evaluation and Observability, Security and Compliance, Agent Ecosystem.
- **Keyword Table**: A per-layer list of strings used for case-insensitive substring matching during Phase 1 classification. Evaluated in L1→L7 order; first match wins. Each keyword belongs to exactly one layer.
- **Finding**: A threat model output row that inherits a `maestro_layer` value from its target component during Phase 3. Schema-defined enum value, propagated unchanged through risk-scorer, control-analyzer, threat-report, infographic, and PDF pipelines.
- **Component Inventory**: The Phase 1 output listing architectural components with their assigned MAESTRO layers. Rendered as a table in `threats.md`.
- **Example Architecture**: A committed reference architecture in `examples/*` used for regression testing and user documentation. Six exist (agentic-app, ascii-web-api, free-text-microservice, mermaid-agentic-app, microservices, web-app). Each has at minimum a `threats.md` and `security-report.pdf.baseline`. Only agentic-app has a full `sample-report/` pipeline.
- **Discovery Report**: A committed audit trail (`specs/136-maestro-canonical-layer/discovery-report.md`) documenting the pre-edit grep sweep results and scope completeness for Feature 136.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Correctness**

- **SC-001**: 100% of L5/L6/L7 references in the shared reference file (`.claude/skills/tachi-shared/references/maestro-layers-shared.md`) match canonical CSA MAESTRO names
- **SC-002**: 100% of enum values in `schemas/finding.yaml` `maestro_layer` field match canonical CSA MAESTRO names with em dash format
- **SC-003**: 100% of `examples/*/threats.md` component inventory rows and finding table rows show canonical layer names — measured by a grep that returns zero matches for old layer names across all example files
- **SC-004**: The `examples/agentic-app/sample-report/` directory shows at least one finding targeting the Audit Logger component with `maestro_layer: "L5 — Evaluation and Observability"` in both `threats.md` and `security-report.pdf`
- **SC-005**: The `templates/tachi/security-report/maestro-findings.typ` fallback dictionary no longer contains the divergent "Integration Services" name — instead shows "Security and Compliance" for L6

**Regression Safety**

- **SC-006**: `test_backward_compatibility.py` passes against the five regenerated non-agentic-app baselines with `SOURCE_DATE_EPOCH=1700000000`
- **SC-007**: 100% of the existing 150+ pytest tests continue to pass after the fix (no regressions)
- **SC-008**: `/aod.analyze` passes with zero MAESTRO-related inconsistencies flagged

**Traceability and Auditability**

- **SC-009**: The Wave 0 discovery report at `specs/136-maestro-canonical-layer/discovery-report.md` exists and documents every grep pattern match
- **SC-010**: CHANGELOG.md contains a new entry with the complete old → new enum value mapping for downstream migration
- **SC-011**: Schema version in `schemas/finding.yaml` is bumped to 1.3

**Scope Discipline**

- **SC-012**: Historical PRDs 084 and 091 remain unchanged after the PR merges
- **SC-013**: The PR contains no changes to the Python extraction scripts (`scripts/extract-*.py`) — confirming data-driven pipeline
- **SC-014**: The PR scope is limited to the files listed in PRD "Affected Files" section (plus Wave 0 discoveries) — no scope creep into Phase 2/3/4 work

**Release Coordination**

- **SC-015**: The schema bump 1.2 → 1.3 ships inside tachi v4.10.0 (minor release), consistent with release-please configuration

---

## Assumptions

- The three canonical sources (CSA blog, Snyk Labs, Practical DevSecOps) agree on canonical L5/L6/L7 ordering and naming (verified 2026-04-10 in the discovery item)
- The canonical format uses " — " (em dash with spaces) as a separator, matching existing tachi format for L1–L4
- The extraction scripts (`scripts/extract-report-data.py`, `scripts/extract-infographic-data.py`, `scripts/tachi_parsers.py`) are fully data-driven — no Python code changes are needed (verified in research.md section 1)
- The release-please workflow targets minor version track (v4.9.2 → v4.10.0) — a 1.3 schema bump fits without forcing a major tachi release (verified in research.md section 4)
- The `test_backward_compatibility.py` test from Feature 128 continues to work as the byte-determinism gate with `SOURCE_DATE_EPOCH=1700000000` (verified in research.md section 2)
- The `examples/agentic-app/` directory is excluded from `test_backward_compatibility.py` and is manually validated via spot-check (Audit Logger finding → L5 — Evaluation and Observability)
- The classification algorithm's first-match-wins semantics resolve the `dashboard` keyword ambiguity — observability-specific keywords in L5 evaluate before the generic `dashboard` in L7 (pre-validated in Wave 0)
- No example component is named literally "dashboard" in a way that triggers L7 classification when L5 is semantically correct (pre-validated in Wave 0; if found, add a qualifying keyword to L5)

---

## Out of Scope — Explicitly Deferred

- **Phase 2**: Cross-layer attack chain analysis and orchestrator correlation logic (separate PRD)
- **Phase 3**: Agentic threat pattern expansion — Agent Collusion, Emergent Behavior, Temporal Attacks (separate PRD)
- **Phase 4**: OWASP AIVSS evaluation architectural decision record (separate PRD)
- Python variable names in extraction scripts containing `security_layer` or equivalent — not updated
- Historical PRDs (084, 091) and historical spec directories (specs/084-*, specs/091-*)
- New infographic templates for cross-layer chains
- New Typst pages for agentic patterns
- Changes to STRIDE or AI threat agent dispatch logic
- Changes to composite scoring formulas or CVSS mappings
- Any runtime compatibility shim for old enum values (breaking change is intentional)
- Automatic data migration of past threat model outputs (users regenerate their threat models against the new enum)

---

## Dependencies

**Delivered** (no action needed):
- Feature 084 (MAESTRO Layer Mapping) — introduced the taxonomy being corrected
- Feature 091 (MAESTRO Infographic Templates and PDF Report Section) — downstream infographic outputs
- Feature 104 (Downstream Baseline Propagation) — propagation framework for `maestro_layer` field
- Feature 128 (Executive Threat Architecture Infographic) — introduced `test_backward_compatibility.py` and `SOURCE_DATE_EPOCH` convention
- ADR-021 (SOURCE_DATE_EPOCH for Deterministic PDF Comparison) — convention reused for baseline regeneration

**External** (no code dependencies):
- CSA canonical MAESTRO sources (CSA blog, Snyk Labs, Practical DevSecOps) — reference material only
