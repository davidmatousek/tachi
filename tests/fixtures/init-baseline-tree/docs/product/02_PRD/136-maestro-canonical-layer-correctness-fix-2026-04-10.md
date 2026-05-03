---
prd:
  number: 136
  topic: maestro-canonical-layer-correctness-fix
  created: 2026-04-10
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-10, status: APPROVED, notes: "Correctness fix scoped tightly to Phase 1; Phases 2-4 explicitly deferred to separate PRDs. PRD authored with full ground-truth verification of example structure, hardcoded references, and canonical CSA sources."}
  architect_signoff: {agent: architect, date: 2026-04-10, status: APPROVED_WITH_CONCERNS, notes: "Attempt 2 approved. H1 (FR-6 completeness) fully resolved including Integration Services third-way bug. M1-M3, L1, L3 fully resolved. L2 (verbatim Ordering Rationale rewrite) deferred to plan.md — acceptable. Remaining conditions for plan.md: verbatim Ordering Rationale text, release-please minor-track verification, FR-9 exclusions extended to specs/084-*/091-*, README line numbers 260-262."}
  techlead_signoff: {agent: team-lead, date: 2026-04-10, status: APPROVED_WITH_CONCERNS, notes: "Attempt 1. Scoped correctly. Timeline realistic at 2-3 working days (not 1). Single-PR at ~29 files reviewable. Wave 0 grep sweep mandatory before foundation edits. Agent assignments: senior-backend-engineer (75%), devops (10% for deterministic PDFs), tester (10% for golden fixtures and pytest). Schema bump 1.3 vs 2.0 cascade into release-please workflow must be verified before build."}
source:
  idea_id: 136
  story_id: null
---

# MAESTRO Canonical Layer Correctness Fix — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-10
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High) — Correctness bug affecting shipped claims

---

## Executive Summary

### The One-Liner
Fix three incorrectly named MAESTRO layers (L5, L6, L7) and a non-canonical acronym expansion so tachi's claim to ship canonical CSA MAESTRO actually matches canonical CSA MAESTRO.

### Problem Statement
Tachi ships a MAESTRO seven-layer taxonomy and explicitly claims (in `maestro-layers-shared.md`) to be "the single source of truth" citing CSA as the authoritative source. Three of seven layer names do not match the canonical CSA Ken Huang taxonomy, and the acronym expansion is non-canonical. Adopters reading the PDF security report see labels that do not match any published MAESTRO documentation on the open web.

| Layer | Canonical CSA MAESTRO | Tachi today | Status |
|-------|------------------------|-------------|--------|
| L1 | Foundation Models | Foundation Model | match |
| L2 | Data Operations | Data Operations | match |
| L3 | Agent Frameworks | Agent Framework | match |
| L4 | Deployment Infrastructure | Deployment Infrastructure | match |
| L5 | **Evaluation and Observability** | Security | **wrong** |
| L6 | **Security and Compliance** | Agent Ecosystem | **wrong** |
| L7 | **Agent Ecosystem** | User Interface | **wrong — invented** |

Additional correctness issues in the same file:
1. Acronym expansion at line 17 reads "Multi-Agent Environment Security Toolkit for Reasoning and Orchestration" but the canonical expansion is "Multi-Agent Environment, Security, Threat, Risk, and Outcome".
2. "L7 User Interface" is invented — canonical MAESTRO has no dedicated UI layer. Human-agent interaction lives inside L7 Agent Ecosystem in canonical MAESTRO.
3. "L5 Evaluation and Observability" is missing entirely — findings related to audit logging, behavioral monitoring, anomaly detection, forensics, and human oversight (typically a mix of STRIDE Repudiation, Tampering, and Information Disclosure findings targeting observability components) have no correct home in the taxonomy and either land as Unclassified or get misrouted.

### Proposed Solution
A targeted bug fix that renames and reassigns L5, L6, and L7 to match the canonical CSA Ken Huang taxonomy, adds an L5 Evaluation and Observability keyword set, corrects the acronym expansion, bumps the schema version, and regenerates all affected example outputs and golden test fixtures. No new features, no new capabilities — just correctness alignment with the canonical spec so that tachi's shipped claim matches reality.

### Success Criteria
- `maestro-layers-shared.md` uses canonical layer names (L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem) and canonical acronym expansion
- `schemas/finding.yaml` enum values match canonical names; schema version is bumped
- All six example outputs (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographics, PDF baselines) regenerate with correct layer assignments
- A finding targeting an observability component (e.g., Audit Logger in agentic-app — known candidate is Tampering T-3, any STRIDE category is acceptable) correctly classifies to "L5 — Evaluation and Observability" (verifying end-to-end population of the new layer)
- CHANGELOG documents the correctness fix with a downstream migration note
- All existing MAESTRO-related regression tests and `/aod.analyze` pass after the fix

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's mission is making threat modeling accessible to teams without deep security expertise. Tachi's core value proposition is being "the first toolkit to natively model AI-specific threat agents... alongside traditional STRIDE." Shipping a non-canonical MAESTRO taxonomy while claiming to be "the single source of truth" directly undermines that value proposition. This PRD is a correctness fix that restores alignment between the shipped claim and the shipped output.

### Roadmap Fit
This is a corrective patch on prior MAESTRO work:
- **Feature 084**: MAESTRO Layer Mapping — introduced the taxonomy (with the naming bug)
- **Feature 091**: MAESTRO Infographic Templates and PDF Report Section — rendered the taxonomy in user-facing outputs (propagating the naming bug to PDFs)
- **Feature 136 (this PRD)**: Correctness fix — aligns the taxonomy with the canonical CSA spec

This is the load-bearing fix that must ship before any MAESTRO enhancements. Phases 2–4 from the discovery item (cross-layer attack chain analysis, agentic threat pattern expansion, AIVSS evaluation) are explicitly **out of scope** for this PRD and will each get their own `/aod.define` → `/aod.plan` cycle. Those phases build narratives that reference layer names and only make sense against canonical terminology.

---

## Target Users & Personas

### Primary Persona: Tachi Maintainer
- **Role**: Maintains tachi's threat modeling pipeline and shared references
- **Goal**: Ship a MAESTRO implementation whose claims match canonical CSA documentation
- **Pain Point**: Current shared reference claims "single source of truth" but diverges from canonical CSA on three layer names and the acronym expansion

### Primary Persona: Security Engineer Running Tachi
- **Role**: Runs tachi on an agentic system to produce a threat model
- **Goal**: Classify audit logging, behavioral monitoring, and anomaly detection components into an observability layer
- **Pain Point**: No layer exists for detective controls and observability gaps; findings land as Unclassified or get misrouted into the current (incorrect) L5 Security

### Secondary Persona: CISO Reading a Tachi PDF Security Report
- **Role**: Consumes the MAESTRO Findings page in PDF security reports
- **Goal**: Brief the team using standard CSA MAESTRO vocabulary
- **Pain Point**: Current labels don't match external MAESTRO documentation, forcing translation between tachi terminology and published CSA spec

### Secondary Persona: Downstream Tachi Adopter
- **Role**: Has built tooling, dashboards, or scripts against tachi's `maestro_layer` enum values
- **Goal**: Coordinate adoption of the new canonical layer values in a single controlled release
- **Pain Point**: Schema change is a breaking change for anything depending on the enum values

---

## User Stories

### US-136-1: Canonical Shared Reference
**When** I read `.claude/skills/tachi-shared/references/maestro-layers-shared.md`,
**I want to** see canonical CSA MAESTRO layer names and acronym expansion,
**So I can** trust that tachi's "single source of truth" claim matches the external canonical spec.

**Acceptance Criteria**:
- **Given** the shared reference file, **then** L5 is named "Evaluation and Observability", L6 is named "Security and Compliance", L7 is named "Agent Ecosystem"
- **Given** the shared reference file, **then** line 17 reads "Multi-Agent Environment, Security, Threat, Risk, and Outcome" as the acronym expansion
- **Given** the seven-layer taxonomy table, **then** all seven rows show canonical names and descriptions consistent with the CSA blog, Snyk Labs, and Practical DevSecOps sources

### US-136-2: Keyword Reassignment and New L5 Keyword Set
**When** tachi runs Phase 1 classification on an agentic architecture with audit logging, behavioral monitoring, or anomaly detection components,
**I want to** those components to classify into L5 Evaluation and Observability,
**So I can** see a dedicated observability layer in the output instead of Unclassified or misrouted findings.

**Acceptance Criteria**:
- **Given** the canonical layer rename, **then** existing L5 Security keywords (auth, WAF, firewall, secrets manager, guardrail, content filter, rate limit, encryption, RBAC, IAM, access control) move to the new L6 Security and Compliance layer
- **Given** the canonical layer rename, **then** existing L6 Agent Ecosystem keywords (multi-agent, agent-to-agent, swarm, delegation, coordination, supervisor, sub-agent, agent registry, agent mesh) merge with existing L7 User Interface keywords (chat UI, dashboard, admin console, web interface, frontend, user portal, API endpoint, REST API, GraphQL, client, user) into the new L7 Agent Ecosystem layer
- **Given** the canonical layer rename, **then** a new L5 Evaluation and Observability keyword set exists covering: audit log, monitoring, observability, telemetry, anomaly detection, SIEM, forensics, behavioral monitoring, metrics, human oversight, log aggregation
- **Given** the agentic-app example architecture (which contains an Audit Logger component), **when** Phase 1 runs after the keyword reassignment, **then** at least one finding targeting the Audit Logger (regardless of STRIDE category — Tampering T-3 is the known candidate, but any category is acceptable) correctly classifies to "L5 — Evaluation and Observability", validating end-to-end population of the new layer

### US-136-3: Updated Finding Schema
**When** a downstream consumer reads `schemas/finding.yaml`,
**I want to** see canonical layer names in the `maestro_layer` enum with the exact format `"L5 — Evaluation and Observability"`, `"L6 — Security and Compliance"`, `"L7 — Agent Ecosystem"`,
**So I can** validate findings against the canonical taxonomy and migrate downstream tooling in a single coordinated step.

**Acceptance Criteria**:
- **Given** `schemas/finding.yaml`, **then** the `maestro_layer` enum contains the canonical layer values with exact format `"L5 — Evaluation and Observability"`, `"L6 — Security and Compliance"`, `"L7 — Agent Ecosystem"`
- **Given** `schemas/finding.yaml`, **then** the schema version is bumped to reflect the breaking change
- **Given** the schema version bump, **then** CHANGELOG documents the breaking change and the migration path (old enum values → new enum values)

### US-136-4: Regenerated Example Outputs
**When** I browse `examples/*` after the fix,
**I want to** see all six example architectures reflect the canonical layer names throughout threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographics, and PDF baselines,
**So I can** use the examples as accurate reference implementations of canonical MAESTRO classification.

**Acceptance Criteria**:
- **Given** all six example directories, **when** the pipeline regenerates outputs, **then** every `threats.md`, `risk-scores.md`, `compensating-controls.md`, and `threat-report.md` shows canonical L5/L6/L7 names in every component and finding row
- **Given** all six example infographic folders, **when** regenerated, **then** `maestro-stack.json` and `maestro-heatmap.json` reference canonical layer names
- **Given** all six `security-report.pdf.baseline` files, **when** regenerated with `SOURCE_DATE_EPOCH=1700000000`, **then** the new baselines are byte-deterministic and reflect canonical layer names on the MAESTRO Findings page
- **Given** `tests/scripts/fixtures/golden/maestro-stack.json` and `tests/scripts/fixtures/golden/maestro-heatmap.json`, **then** both golden fixtures match the canonical layer names

### US-136-5: CHANGELOG Migration Note
**When** a downstream adopter reviews CHANGELOG after upgrading,
**I want to** see a clear migration note explaining the layer name changes, the schema version bump, and any required downstream updates,
**So I can** update dashboards, scripts, or any tooling that depends on the old enum values in a single coordinated release.

**Acceptance Criteria**:
- **Given** CHANGELOG.md after the fix, **then** a new entry documents the three layer rename (L5, L6, L7), the acronym expansion correction, and the schema version bump
- **Given** the CHANGELOG entry, **then** it explicitly lists old → new enum value mappings for downstream migration
- **Given** the CHANGELOG entry, **then** it calls out this is a correctness fix (not a feature) aligning with canonical CSA MAESTRO

---

## Functional Requirements

### FR-1: Shared Reference Rewrite
**Description**: Update `.claude/skills/tachi-shared/references/maestro-layers-shared.md` to canonical CSA MAESTRO taxonomy.

**Changes**:
- Line 17: Replace acronym expansion with "Multi-Agent Environment, Security, Threat, Risk, and Outcome"
- Seven-Layer Taxonomy table (lines 48-57): Rename L5 to "Evaluation and Observability", L6 to "Security and Compliance", L7 to "Agent Ecosystem"; update descriptions and example components for each renamed layer
- Keyword-to-Layer Mapping (lines 60-179): Reassign and add keywords per US-136-2
- Ordering Rationale (lines 34-42): Rewrite the specificity gradient explanation to reflect the new layer order (L1 most specific, L7 Agent Ecosystem broadest catch-all)
- WARNING note about classification ordering must remain, updated for the new layer order

**Outputs**: Updated `maestro-layers-shared.md` that matches canonical CSA spec across all three sources (CSA blog, Snyk Labs, Practical DevSecOps).

### FR-2: Schema Enum Update
**Description**: Update `schemas/finding.yaml` to use canonical layer names and bump schema version.

**Changes**:
- `maestro_layer` field enum values: update L5, L6, L7 to canonical names with the format `"L5 — Evaluation and Observability"`, `"L6 — Security and Compliance"`, `"L7 — Agent Ecosystem"` (em dash separator, matching existing L1–L4 format)
- Schema version bump (from 1.2 to 1.3, subject to architect review)
- Schema comments/documentation updated to reflect the canonical taxonomy alignment

### FR-3: Keyword Reassignment Logic
**Description**: Reorder and reassign keyword tables in `maestro-layers-shared.md` to match the new canonical layer semantics.

**Keyword Reassignment**:

| Layer | New Keywords |
|-------|--------------|
| L5 Evaluation and Observability (**NEW**) | audit log, monitoring, observability, telemetry, anomaly detection, SIEM, forensics, behavioral monitoring, metrics, human oversight, log aggregation |
| L6 Security and Compliance (was L5 Security) | auth, WAF, firewall, secrets manager, guardrail, content filter, rate limit, encryption, RBAC, IAM, access control, security |
| L7 Agent Ecosystem (was L6 Agent Ecosystem + L7 User Interface merged) | multi-agent, agent-to-agent, swarm, delegation, coordination, supervisor, sub-agent, agent registry, agent mesh, chat UI, dashboard, admin console, web interface, frontend, user portal, API endpoint, REST API, GraphQL, client, user |

**Business Rules**:
- `audit log` keyword moves from L5 Security to L5 Evaluation and Observability (because observability keywords take precedence)
- `dashboard` keyword is ambiguous (could be observability dashboard or user dashboard) — document the classification ordering resolves this via first-match-wins order; observability-specific keywords (monitoring, SIEM, metrics) classify first, generic `dashboard` in L7 catches the rest
- The L1→L7 classification order is preserved; however, the new L5 catches observability/detective findings first before they fall into L6 Security or the broader L7 Agent Ecosystem

### FR-4: Example Output Regeneration
**Description**: Regenerate downstream artifacts for all six example architectures. Each example has a different level of pipeline artifacts — regenerate what actually exists, not a uniform matrix across all six.

**Actual Example Structure** (verified 2026-04-10):

| Example | Artifacts to Regenerate |
|---------|-------------------------|
| `examples/agentic-app/` | `threats.md`, **plus** full pipeline in `sample-report/`: `threats.md`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `threat-report.md`, `security-report.pdf`, `threat-*.jpg` infographic images, `threat-*-spec.md` infographic specs, `threats.sarif`, `attack-trees/` |
| `examples/mermaid-agentic-app/` | `threats.md`, `threat-report.md`, `threat-infographic-spec.md`, `security-report.pdf.baseline`, `attack-trees/` |
| `examples/ascii-web-api/` | `threats.md`, `security-report.pdf.baseline` |
| `examples/free-text-microservice/` | `threats.md`, `security-report.pdf.baseline` |
| `examples/microservices/` | `threats.md`, `security-report.pdf.baseline` |
| `examples/web-app/` | `threats.md`, `security-report.pdf.baseline` |

**Note**: No example has an `infographics/` subdirectory. Infographic JSON data lives in golden fixtures (`tests/scripts/fixtures/golden/`) and in the `sample-report/` directory for agentic-app. Infographic JPEG images are stored alongside `threats.md` with names like `threat-baseball-card.jpg`. The full multi-artifact pipeline only exists in `agentic-app/sample-report/`.

**Realistic file-touch count**: ~29 files (6 threats.md + 5 PDF baselines + 1 full sample-report dir with ~10 files + mermaid-agentic-app variations), not the "42 files × 6 examples" the prior PRD draft implied.

**Business Rules**:
- All regenerations must be byte-deterministic (use `SOURCE_DATE_EPOCH=1700000000` for PDFs per ADR-021)
- At least one finding targeting an observability component (e.g., Audit Logger in agentic-app — known candidate is Tampering T-3, but any category qualifies) across the examples must classify into L5 Evaluation and Observability
- Regeneration must use the canonical layer names everywhere — no partial/transition state
- The `sample-report/` directory for agentic-app must regenerate with the new canonical layer names in all files (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, security-report.pdf)
- Test backward compatibility: run `test_backward_compatibility.py` (from Feature 128 pytest bootstrap) against regenerated baselines with `SOURCE_DATE_EPOCH=1700000000` to confirm byte-determinism

### FR-5: Golden Test Fixture Updates
**Description**: Update `tests/scripts/fixtures/golden/*.json` for MAESTRO-related golden fixtures.

**Affected Fixtures**:
- `tests/scripts/fixtures/golden/maestro-stack.json`
- `tests/scripts/fixtures/golden/maestro-heatmap.json`

**Business Rules**:
- Both golden fixtures match the canonical layer names exactly
- The 150+ existing pytest tests continue to pass after the update (tests should be self-consistent with the new canonical names)

### FR-6: Typst Template Update (MANDATORY — not optional review)
**Description**: Update `templates/tachi/security-report/maestro-findings.typ` and `templates/tachi/security-report/main.typ` — both contain hardcoded layer name references confirmed by pre-review grep (2026-04-10).

**Verified Hardcoded References** (pre-review grep, 2026-04-10):

| File | Line | Current (Wrong) | Must Become |
|------|------|-----------------|-------------|
| `templates/tachi/security-report/maestro-findings.typ` | 121 | "from Foundation Model (L1) through User Interface (L7)" prose | "from Foundation Models (L1) through Agent Ecosystem (L7)" |
| `templates/tachi/security-report/maestro-findings.typ` | 132 | `"L5": "Security"` | `"L5": "Evaluation and Observability"` |
| `templates/tachi/security-report/maestro-findings.typ` | 133 | `"L6": "Integration Services"` (third divergent name — neither canonical nor matching the shared ref's "Agent Ecosystem") | `"L6": "Security and Compliance"` |
| `templates/tachi/security-report/maestro-findings.typ` | 134 | `"L7": "User Interface"` | `"L7": "Agent Ecosystem"` |
| `templates/tachi/security-report/main.typ` | 293 | "from Foundation Model (L1) through User Interface (L7)" prose | "from Foundation Models (L1) through Agent Ecosystem (L7)" |

**Critical Finding**: The Typst template fallback dictionary contains a **third divergent layer name** — "Integration Services" — which exists in neither the canonical CSA spec nor the current shared reference. This is a pre-existing internal inconsistency that must also be fixed as part of this correctness PRD.

### FR-6b: Additional Hardcoded References (Discovered During Review)

Pre-review grep confirmed the following additional files contain hardcoded layer name references that must be updated:

| File | Line | Reference Type | Action |
|------|------|----------------|--------|
| `schemas/finding.yaml` | 131-132 | Enum values "L6 — Agent Ecosystem", "L7 — User Interface" | Already in FR-2 — explicit |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | 64 | Layer enum list | Update to canonical names |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | 149 | Example "User \| External Entity \| L7 — User Interface" | Update to "L7 — Agent Ecosystem" |
| `README.md` | 260-262 | L6/L7 layer table in repo README | Update to canonical names |
| `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` | 123 | Acronym expansion citation | Update to canonical; add revision note |

**Discovery Requirement**: Before any file edits begin, a mandatory Wave 0 codebase-wide grep sweep must run to catch any additional hardcoded references missed by the pre-review grep. See FR-9 below.

### FR-7: CHANGELOG Entry with Migration Note
**Description**: Document the correctness fix in `CHANGELOG.md`.

**Entry Structure**:
- Clearly label as a correctness fix (not a feature)
- List the three layer renames (L5, L6, L7) with old → new mapping
- Document the acronym expansion correction
- Note the schema version bump
- Provide downstream migration guidance (tooling that depends on old enum values needs to update)

### FR-8: Pipeline Validation
**Description**: Validate the fix via existing tooling.

**Validations**:
- `/aod.analyze` passes with no MAESTRO-related inconsistencies
- Existing pytest suite (150+ tests from Feature 128 bootstrap) passes
- **`test_backward_compatibility.py` explicitly run** against regenerated baselines with `SOURCE_DATE_EPOCH=1700000000` — this is the byte-determinism gate per ADR-021
- Example regeneration is idempotent (rerunning produces the same byte-deterministic output)
- Manual spot-check: an agentic-app finding targeting the Audit Logger component classifies to "L5 — Evaluation and Observability" (Tampering T-3 is the known candidate; any finding against Audit Logger qualifies)

### FR-9: Mandatory Wave 0 Pre-Edit Discovery Sweep
**Description**: Before any file edits begin, a codebase-wide grep sweep must run to catch any hardcoded layer references the pre-review may have missed. This guards the single-coordinated-PR constraint against partial updates.

**Required Grep Patterns** (run before editing anything):

1. `"User Interface"` — catches all L7 wrong-name references
2. `"Security Toolkit for Reasoning and Orchestration"` — catches the wrong acronym expansion
3. `"Integration Services"` — catches the Typst third-way bug anywhere it may be copy-pasted
4. `"L5 — Security"` and `"L5 Security"` (with and without em dash) — catches wrong L5 label
5. `"L6 — Agent Ecosystem"` and `"L6 Agent Ecosystem"` (with and without em dash) — catches wrong L6 label
6. `"L7 — User Interface"` and `"L7 User Interface"` (with and without em dash) — catches wrong L7 label
7. `dashboard` keyword matches in example architecture component names (pre-validation for FR-3 ambiguity — confirm whether any existing component names would be misclassified under the new ordering)

**Exclusions**: The following historical records are **not** updated — they document the original feature at the time it was shipped:
- `docs/product/02_PRD/084-*` (historical PRD)
- `docs/product/02_PRD/091-*` (historical PRD)
- `specs/084-*/` (historical spec directory)
- `specs/091-*/` (historical spec directory)

Only a one-line historical-note annotation is added to ADR-020 pointing forward to Feature 136 as the canonical-alignment fix.

**Output**: A discovery report listing all matches, used as input to the plan.md tasks breakdown. The discovery report should be committed alongside the fix as a reviewable audit trail.

---

## Non-Functional Requirements

### Backward Compatibility
- **Intentionally breaking** at the schema enum level — this is a correctness fix and the old values were wrong
- Downstream tooling depending on the old enum values must update (CHANGELOG documents the migration)
- Schema version bump signals the breaking change to any version-aware consumers
- **All six example PDF baselines will be regenerated** — every `examples/*/security-report.pdf.baseline` file changes as part of this PRD, plus the `sample-report/security-report.pdf` for agentic-app. This is expected and documented in the PRD scope; `test_backward_compatibility.py` is explicitly re-run after baseline regeneration with `SOURCE_DATE_EPOCH=1700000000` to confirm byte-determinism of the new baselines.
- Schema bump 1.2 → 1.3 targets the tachi minor version track (expected v4.10.0 per release-please-config.json — to be verified in plan.md)

### Performance
- No performance impact — this is a taxonomy rename, not an algorithm change
- Classification algorithm remains first-match-wins on an ordered keyword table (no new logic)

### Reliability
- All existing test coverage must continue to pass
- Manual verification that at least one Repudiation finding correctly classifies to the new L5

### Documentation Consistency
- Every reference to MAESTRO layer names in the codebase must be updated in a single coordinated PR
- No half-state where the shared reference is canonical but example outputs still show old names

---

## Success Metrics

### Primary Metrics (Correctness)
- **Canonical Match**: Every layer name in `maestro-layers-shared.md`, `schemas/finding.yaml`, and all example outputs matches the CSA canonical taxonomy exactly
- **Schema Integrity**: Schema version bumped; enum values match canonical names
- **End-to-End L5 Population**: At least one finding targeting an observability component (e.g., Audit Logger in agentic-app) across the examples correctly classifies to "L5 — Evaluation and Observability", regardless of STRIDE category

### Secondary Metrics (Regression Safety)
- **Test Pass Rate**: 100% of existing pytest tests pass after the fix (currently 150+ tests)
- **PDF Baseline Determinism**: All six `security-report.pdf.baseline` files regenerate byte-deterministically with `SOURCE_DATE_EPOCH=1700000000`
- **`/aod.analyze` Clean**: No MAESTRO-related inconsistencies flagged

### Adoption Metric
- **CHANGELOG Clarity**: Migration note is actionable — a downstream adopter reading it can update their tooling in a single step

---

## Scope & Boundaries

### In Scope (P0 — Must Have)
- Rename L5, L6, L7 in `maestro-layers-shared.md` to canonical CSA names
- Correct the acronym expansion at line 17
- Add new L5 Evaluation and Observability keyword set
- Reassign existing L5 Security keywords to new L6 Security and Compliance
- Merge existing L6 Agent Ecosystem + L7 User Interface keywords into new L7 Agent Ecosystem
- Rewrite the ordering rationale (specificity gradient) for the new layer order
- Update `schemas/finding.yaml` enum values and bump schema version
- Regenerate all six example outputs (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographics, PDF baselines)
- Update golden test fixtures (`maestro-stack.json`, `maestro-heatmap.json`)
- Review and update `templates/tachi/security-report/maestro-findings.typ` if hardcoded references exist
- Add CHANGELOG entry with old → new enum mapping and downstream migration note

### In Scope (P1 — Should Have)
- Spot-check validation: one agentic-app example finding targeting the Audit Logger classifies to "L5 — Evaluation and Observability" (Tampering T-3 is the known candidate)
- **Minimal** ADR-020 update in Phase 1: fix the acronym citation at line 123 + add a revision note that layer naming was corrected in Feature 136. Full ADR rewrite (with cross-layer analysis context) is **deferred** to Phase 2.
- Add a one-line rule to ADR-019 (or the schema versioning doc): "Enum-value-only breaking changes warrant a minor schema bump (x.y+1), not a major bump, provided schema shape and required fields are unchanged"
- Discovery report (from FR-9 Wave 0 sweep) committed alongside the fix as an audit trail

### Out of Scope — Explicitly Deferred to Separate PRDs
- **Phase 2**: Cross-layer attack chain analysis and correlation logic — separate `/aod.define` cycle
- **Phase 3**: Agentic threat pattern expansion (Agent Collusion, Emergent Behavior, Temporal Attacks, etc.) — separate `/aod.define` cycle
- **Phase 4**: OWASP AIVSS evaluation ADR — separate `/aod.define` cycle
- New infographic templates for cross-layer chains
- New Typst pages for agentic patterns
- Changes to any STRIDE or AI threat agent dispatch logic
- Changes to composite scoring formulas
- Retroactive renaming of variable or function names that contain "security_and_compliance" or similar (only user-facing strings change)

### Assumptions
- The three canonical sources (CSA blog, Snyk Labs, Practical DevSecOps) agree on the canonical seven-layer ordering and naming (verified 2026-04-10 in the discovery item)
- The canonical format uses " — " (em dash with spaces) as a separator, matching existing tachi format for L1–L4
- Keyword classification is first-match-wins and layer order matters — this behavior is preserved
- Example regeneration uses `SOURCE_DATE_EPOCH=1700000000` per ADR-021 for byte-determinism
- The agentic-app example contains an Audit Logger component and a finding targeting it (Tampering T-3 per pre-review grep) that can validate L5 population after keyword reassignment — this does **not** need to be a STRIDE Repudiation finding; any category is acceptable
- No example component is named literally "dashboard" without additional observability qualifying keywords (pre-validated in FR-9 Wave 0 grep sweep — if a component name causes misclassification, the plan.md tasks include a keyword-order tuning task before finalizing FR-3)
- The release-please workflow in `release-please-config.json` targets the minor version track (v4.x.y) — schema bump 1.2 → 1.3 fits the minor track without forcing a major release (to be confirmed during plan.md by the architect)

### Constraints
- Must be a single coordinated change — no half-state across files
- Must follow the deterministic pipeline convention (no LLM in classification)
- Must preserve the first-match-wins classification algorithm
- Must not introduce any new dependencies
- Must respect the existing format `"L{N} — {Name}"` (em dash separator)

---

## Risks & Dependencies

### Technical Risks

**Risk 1: Keyword Reassignment Breaks Existing Classifications Silently**
- **Likelihood**: High
- **Impact**: Medium (example outputs will differ; this is expected)
- **Mitigation**: Regenerate all six example outputs and manually review that each component lands in the correct new layer. Document the diff in the PR description.
- **Contingency**: If a component misclassifies, iterate on keyword ordering or add specific keywords to nudge the correct layer

**Risk 2: Schema Version Bump Breaks Downstream Tools**
- **Likelihood**: Low (tachi is primarily consumed through its commands, not directly via schemas)
- **Impact**: Medium (any tooling hardcoded against enum values will break)
- **Mitigation**: CHANGELOG clearly documents the breaking change and provides old → new mapping; schema version bump signals the change to version-aware consumers
- **Contingency**: None — this is a correctness fix and the old values were wrong

**Risk 3: PDF Baseline Regeneration Non-Determinism**
- **Likelihood**: Low (ADR-021 convention is established)
- **Impact**: Medium (test diff noise would make the PR hard to review)
- **Mitigation**: Use `SOURCE_DATE_EPOCH=1700000000` for all PDF regenerations per ADR-021
- **Contingency**: If byte-determinism breaks, debug the PDF generation and fix before merging

**Risk 4: `dashboard` Keyword Ambiguity**
- **Likelihood**: Medium
- **Impact**: Low (existing components classify one way or another; first-match-wins resolves)
- **Mitigation**: The generic `dashboard` keyword belongs only in L7 Agent Ecosystem per FR-3. Observability-specific keywords (monitoring, SIEM, metrics, telemetry, audit log, observability) in L5 are evaluated first due to the L1→L7 order. A component named "metrics dashboard" matches `metrics` (L5) before `dashboard` (L7) and correctly classifies to L5. A component named only "admin dashboard" matches `dashboard` (L7) and correctly classifies to L7.
- **Pre-validation**: FR-9 Wave 0 grep sweep confirms no example component name contains only "dashboard" with an observability meaning that would require a different resolution
- **Contingency**: If an example misclassifies, add the misclassified component name's distinguishing keyword to L5 (e.g., add `observability dashboard` as an explicit L5 keyword) rather than removing the generic `dashboard` from L7

**Risk 5: Ordering Rationale Rewrite Complexity**
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**: Existing rationale is three sentences; rewrite is small
- **Contingency**: Defer the rewrite as a follow-up if time-constrained (but PR would be incomplete)

### Dependencies

**Internal Dependencies** (all delivered):
- **Feature 084** (MAESTRO Layer Mapping): Provides the taxonomy this PRD corrects
- **Feature 091** (MAESTRO Infographic Templates): Provides the downstream infographic outputs to regenerate
- **Feature 104** (Downstream Baseline Propagation): Provides the propagation framework (values flow through risk-scorer, control-analyzer, threat-report, infographics, PDF)
- **ADR-021** (SOURCE_DATE_EPOCH for deterministic PDFs): Provides the convention for regenerating byte-deterministic PDF baselines

**External Dependencies**:
- CSA canonical MAESTRO sources (verified 2026-04-10 in the discovery item): CSA blog, Snyk Labs, Practical DevSecOps
- No external code or library dependencies

All dependencies are satisfied.

---

## Open Questions

- [x] Should the schema version bump be 1.2 → 1.3 (minor) or 1.2 → 2.0 (major)? — **Resolved by architect review**: 1.3 minor bump, with a one-line rule added to ADR-019 (or the schema versioning doc) stating "Enum-value-only breaking changes warrant a minor schema bump (x.y+1), not a major bump, provided schema shape and required fields are unchanged". CHANGELOG migration note documents the breaking change for downstream consumers.
- [x] Should `ADR-020` (MAESTRO as taxonomy overlay) be updated in this PRD, or deferred to the Phase 2 cross-layer analysis PRD? — **Resolved by architect review**: Minimal update in Phase 1 (fix acronym citation at line 123 + add a revision note). Full rewrite deferred to Phase 2.
- [x] Is there any existing code (variable names, function names, comments) that uses the old layer names and should be renamed? — **Resolved**: Scope limited to user-facing strings and data files. Internal variable names (e.g., any `security_layer` Python variables) are out of scope and will be handled in future refactors if needed.
- [x] Does the `dashboard` keyword reassignment need deeper testing beyond the six examples? — **Resolved**: Six examples provide sufficient regression coverage. FR-9 Wave 0 grep pre-validates no example component name triggers the ambiguity.
- [ ] Does the release-please workflow (`release-please-config.json`) target a minor or major version track for the next release, and is a 1.2 → 1.3 schema bump consistent with that? — architect — Must verify in plan.md before Wave 1 foundation edits begin
- [ ] Should the discovery report from FR-9 Wave 0 be committed as `specs/136-*/discovery-report.md` or as a PR artifact outside the specs directory? — team-lead — Recommendation: Commit as `specs/136-maestro-framework-compliance/discovery-report.md` for traceability

---

## References

### Canonical Sources (verified 2026-04-10)
- [CSA Blog: Agentic AI Threat Modeling Framework — MAESTRO (2025-02-06)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)
- [Snyk Labs: MAESTRO — Layered Threat Modeling for Agentic AI Ecosystems](https://labs.snyk.io/resources/maestro-threat-modeling/)
- [Practical DevSecOps: MAESTRO — An Agentic AI Threat Modeling Framework](https://www.practical-devsecops.com/maestro-agentic-ai-threat-modeling-framework/)
- [CSA Blog: Threat Modeling OpenAI's Responses API with MAESTRO (2025-03-24)](https://cloudsecurityalliance.org/blog/2025/03/24/threat-modeling-openai-s-responses-api-with-the-maestro-framework)

**Note**: The original Ken Huang Medium article is no longer accessible (404 as of 2026-04-10). Canonical definitions are verified against the three independent sources above, which all agree on L5/L6/L7 ordering and naming.

### Related PRDs
- [F-084 — MAESTRO Layer Mapping](084-maestro-layer-mapping-2026-04-05.md) (introduced the taxonomy — referenced for context)
- [F-091 — MAESTRO Infographic Templates and PDF Report Section](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md) (infographic templates — referenced for regeneration scope)
- [F-104 — Downstream Baseline Propagation](104-downstream-baseline-propagation-2026-04-08.md) (propagation framework — referenced for pipeline flow)

### Architecture Decision Records
- **ADR-020**: MAESTRO as Taxonomy Overlay — may need a note about canonical alignment
- **ADR-021**: SOURCE_DATE_EPOCH for Deterministic PDF Comparison — convention reused for baseline regeneration

### Affected Files (Phase 1 scope — verified 2026-04-10 via pre-review grep)

**Foundation (must come first — Wave 1)**:
- `.claude/skills/tachi-shared/references/maestro-layers-shared.md` (layer rename, keyword reassignment, acronym fix at line 17, ordering rationale rewrite)
- `schemas/finding.yaml` (enum values at lines 131-132, schema version bump 1.2 → 1.3)
- `.claude/skills/tachi-shared/references/finding-format-shared.md` (layer enum list at line 64)

**Typst templates (must update — contains third divergent bug)**:
- `templates/tachi/security-report/maestro-findings.typ` (prose at line 121, fallback dict at lines 132-134 — includes fixing "Integration Services" third-way bug to "Security and Compliance")
- `templates/tachi/security-report/main.typ` (prose at line 293)

**Pipeline documentation**:
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md` (line 149 example)

**Architecture decision records**:
- `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` (line 123 acronym + add revision note pointing to Feature 136)
- `docs/architecture/02_ADRs/ADR-019` or schema versioning doc (add one-line rule: enum-value-only changes warrant minor bump)

**Repo-level docs**:
- `README.md` (lines 260-262 layer table)

**Example regeneration** (realistic count per FR-4):
- `examples/agentic-app/threats.md` (regenerate)
- `examples/agentic-app/sample-report/*` (full pipeline regeneration: threats.md, risk-scores.md, risk-scores.sarif, compensating-controls.md, threat-report.md, security-report.pdf, threat-*.jpg, threat-*-spec.md, threats.sarif, attack-trees/)
- `examples/mermaid-agentic-app/threats.md`, `threat-report.md`, `threat-infographic-spec.md`, `security-report.pdf.baseline`, `attack-trees/`
- `examples/ascii-web-api/threats.md`, `security-report.pdf.baseline`
- `examples/free-text-microservice/threats.md`, `security-report.pdf.baseline`
- `examples/microservices/threats.md`, `security-report.pdf.baseline`
- `examples/web-app/threats.md`, `security-report.pdf.baseline`

**Test fixtures** (verify MAESTRO-related fixtures in the existing Feature 128 pytest bootstrap):
- `tests/scripts/fixtures/golden/*.json` — any golden JSON file with a MAESTRO layer reference (confirm scope in Wave 0)
- `tests/scripts/test_backward_compatibility.py` — re-run with `SOURCE_DATE_EPOCH=1700000000` against regenerated baselines (no file change, but validation gate)

**Release documentation**:
- `CHANGELOG.md` (new entry with old → new enum mapping and downstream migration note)

**Audit trail** (new file created by Wave 0 discovery):
- `specs/136-maestro-framework-compliance/discovery-report.md` (FR-9 Wave 0 grep sweep output)

**Historical records — NOT updated** (explicit exclusion):
- `docs/product/02_PRD/084-maestro-layer-mapping-2026-04-07.md` — historical PRD frozen at feature ship
- `docs/product/02_PRD/091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md` — historical PRD frozen at feature ship
- Internal variable names in Python scripts (e.g., any `security_layer` identifiers) — out of scope per Open Question resolution

**Total realistic file-touch**: ~29 files (6 threats.md + 5 top-level baselines + 10 files in agentic-app sample-report + 4 files in mermaid-agentic-app + 6 foundation files + 3 docs/ADRs + CHANGELOG + discovery report), verified via pre-review ground-truth check.

### Technical Documentation
- [Architecture README](../../../docs/architecture/README.md)
- [Constitution](../../../.aod/memory/constitution.md)

---

## Approval

### PM Sign-off
- **Approver**: product-manager
- **Date**: 2026-04-10
- **Status**: APPROVED
- **Notes**: Correctness fix scoped tightly to Phase 1; Phases 2-4 explicitly deferred to separate PRDs. PRD authored with full ground-truth verification of example structure, hardcoded references, and canonical CSA sources.

### Architect Sign-off
- **Approver**: architect
- **Date**: 2026-04-10
- **Status**: APPROVED_WITH_CONCERNS (attempt 2)
- **Notes**: H1 (FR-6 completeness) fully resolved including Integration Services third-way bug. H2, M1, M2, M3, L1, L3 fully resolved. L2 (verbatim Ordering Rationale rewrite) deferred to plan.md — acceptable. Remaining conditions for plan.md: verbatim Ordering Rationale text, release-please minor-track verification, FR-9 exclusions extended to specs/084-*/091-*, README line numbers 260-262.

### Team-Lead Sign-off
- **Approver**: team-lead
- **Date**: 2026-04-10
- **Status**: APPROVED_WITH_CONCERNS
- **Notes**: Scoped correctly as Phase 1 correctness fix with right deferrals. Timeline realistic at 2-3 working days (not the ~1 day Issue #136 estimate). Wave 0 grep sweep mandatory before foundation edits. Agent assignments: senior-backend-engineer (75% — shared ref + schema + templates + regeneration + changelog), devops (10% — deterministic PDF baselines per ADR-021), tester (10% — golden fixtures + pytest + manual L5 spot-check). Schema bump 1.3 vs 2.0 cascade into release-please workflow must be verified before build (plan.md open question). Single-PR at ~29 files reviewable with 1h budgeted for PR description authoring.
