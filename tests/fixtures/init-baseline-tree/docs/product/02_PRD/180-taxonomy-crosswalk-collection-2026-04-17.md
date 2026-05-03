---
prd:
  number: 180
  topic: taxonomy-crosswalk-collection
  created: 2026-04-17
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-17, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. Scope DEFENSIBLE — 9-file cadence exception product-sound. H-PM-1 addressed inline: new Metric 7 (Adopter Resolution Path, outcome-measurable) added after Metric 6; runnable Python snippet in README §Purpose/§Usage per FR-8. H-PM-2 deferred to spec (adopter-facing 'what F-A1 does NOT give you today' signal in README). M-PM-1 resolved inline (US-180-2 AC-4 rewritten to ≥500 primary edges). M-PM-2/M-PM-3/M-PM-4 and LOW items deferred to spec-phase copy edits. Private-governance invariant verified (no SDR-001/BLP-01 references). Persona coverage complete (adopter/maintainer/reviewer). Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-17, status: APPROVED_WITH_CONCERNS, notes: "v1.0 CHANGES_REQUESTED (1 BLOCKING + 4 HIGH + 6 MEDIUM + 5 LOW) all resolved in v1.1. B1 ADR-026→ADR-027 correction: 7 accurate ADR-027 references, 0 stale ADR-026 conflations; ADR-004/ADR-007 lineage note added per advice. H1 Interpretation C encoded end-to-end: FR-1 9 files, FR-2 uniform item shape, FR-3 7-value taxonomy enum, FR-6 catalog in nist-ai-rmf.yaml + mapping rows in crosswalk.yaml with 'No equivalent' omitted. H2 FR-7 expanded to 4 test functions + optional sort-order test; covers taxonomy/confidence/edge_type enum closures + per-item shape + citation non-emptiness. H3 tests/schemas/ subdirectory locked. H4 crosswalk floor reduced to ≥500 primary as Tier 1 default. M1-M6 + Q1-Q5 all resolved with FR cross-references. v1.1 re-review confirmed 5 LOW residual stale-reference cleanups (all fixed inline on v1.2). Zero PII / zero new runtime deps / zero security surface change."}
  techlead_signoff: {agent: team-lead, date: 2026-04-17, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 3 MEDIUM / 2 LOW. H1 crosswalk rate vs floor resolved inline (v1.1 adopted Tier 1 ≥500 primary as default; FR-3 internal contradiction eliminated; Success Metric 2 aligned). H2 Phase 3 compression resolved by distributing NIST + crosswalk + README across Days 2-3 in parallel 3-agent plan (senior-backend-engineer + web-researcher + architect). Timeline floor tightened 3→4d per precedent corridor (PRD 144 <PRD 180 <PRD 145). Day 1 spike numeric tripwire at 38.4s/edge encoded in Risk R1; R3 Tier 1 (≥500 default) / Tier 2 (team-lead-authorizable descope to 300) / Tier 3 (PRD amendment to 150) pre-authorized. R6 added for single-agent execution extending to 5-6d. Dependencies verified Delivered (PRD 144 + PRD 082). No capacity overload. Agent assignments named with valid subagent_type values throughout Phase Breakdown."}
source:
  idea_id: 180
  story_id: null
---

# F-A1 Taxonomy Crosswalk Collection — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-17
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High) — foundation feature; blocks downstream taxonomy-consuming features
**Parent Discovery**: [#180](https://github.com/davidmatousek/tachi/issues/180)

---

## Executive Summary

### The One-Liner
Give tachi a machine-readable, PR-reviewable cross-taxonomy reference — a new `schemas/taxonomy/` directory containing five external framework YAMLs (OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE), two small tachi-internal pseudo-taxonomy YAMLs (tachi control categories, tachi STRIDE+AI categories — per Interpretation C in FR-6), a `crosswalk.yaml` of mapping edges, and a curation `README.md` — so every downstream finding, report, and coverage-attestation feature can resolve taxonomy IDs against a single authored source rather than re-deriving the mapping by hand.

### Problem Statement
Tachi's 11 threat-detection agents (6 STRIDE + 5 AI) cite taxonomy IDs across their `detection-patterns.md` references: **38 unique MITRE ATT&CK techniques**, **7 unique MITRE ATLAS techniques** (including October 2025 agent techniques AML.T0058–T0062), **41 unique CWEs**, and varying subsets of OWASP Top 10 (LLM, Agentic, Web, API, Mobile, ML) items. Feature 144 additionally authored a NIST AI RMF mapping at [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) covering AI 600-1 §2 Generative AI Profile risks × tachi STRIDE+AI categories and tachi control categories × NIST Subcategories (per [ADR-025](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md)).

None of this taxonomy data is currently machine-readable. It lives as prose citations inside agent detection-pattern references. A downstream consumer (e.g., a coverage-attestation report, an ecosystem integration mapping tachi findings to a compliance framework, an adopter programmatically linking tachi output to their SIEM taxonomy) cannot iterate over "every OWASP LLM Top 10 item tachi covers" or "every CWE referenced by more than one agent" without parsing markdown prose. The 11 agents' citations are also **incomplete against the full framework item sets** — for example, CWE Top 25 (2024) items not currently cited by any agent do not appear anywhere in tachi's corpus.

No authoritative external crosswalk exists across OWASP + MITRE ATT&CK + MITRE ATLAS + NIST AI RMF + CWE. MITRE publishes partial ATT&CK↔ATLAS mappings; OWASP publishes LLM↔CWE links within individual LLM Top 10 entries; NIST AI 600-1 cross-references its own AI RMF 1.0 Subcategories; no public crosswalk records primary/related/superseded edges across the full five-framework set at the granularity tachi needs. Tachi must curate its own.

This creates three concrete gaps:
- **Reference gap**: Adopters cannot resolve a tachi finding's taxonomy IDs to stable records without text-parsing agent references
- **Completeness gap**: Framework items tachi does not yet cover are invisible — a coverage-attestation pass has no denominator to measure against
- **Curation gap**: Future taxonomy updates (OWASP LLM Top 10 v2027, CWE Top 25 2026, a new MITRE ATLAS wave) have no documented update procedure; each refresh would be an ad-hoc harvest

### Proposed Solution
Ship a new `schemas/taxonomy/` directory containing **nine files** (**Architect-recommended Interpretation C** resolves Open Question Q1 — see FR-6):

1. **`owasp.yaml`** — ≥60 items spanning OWASP LLM Top 10:2025 (LLM01–LLM10), OWASP Top 10 for Agentic Applications:2026 (ASI01–ASI10), OWASP Top 10:2021 (A01–A10), OWASP API Security Top 10:2023 (API1–API10), OWASP Mobile Top 10:2024 (M1–M10), and OWASP Machine Learning Security Top 10:2023 (ML01–ML10). Per-item record shape: `{id, full_id, name, url, cwe_refs}`.

2. **`mitre-attack.yaml`** — ≥38 techniques. Seed: 38 unique MITRE ATT&CK Enterprise techniques currently cited across the 11 threat-agent `detection-patterns.md` references. External-source curation (ATT&CK Enterprise matrix) closes enumeration gaps.

3. **`mitre-atlas.yaml`** — ≥7 techniques. Seed: 7 unique MITRE ATLAS techniques currently cited, explicitly including the October 2025 agent techniques AML.T0058, T0059, T0060, T0061, T0062. External-source curation (ATLAS matrix) closes enumeration gaps.

4. **`nist-ai-rmf.yaml`** — Catalog of NIST AI RMF 1.0 Subcategories (≥68 entries covering the full AI 100-1 Subcategory set across Govern/Map/Measure/Manage Functions). Per-item record shape matches FR-2 (`{id, full_id, name, url, cwe_refs: []}`). See FR-6 for the relationship between the catalog and the Surface B / Surface C mapping rows in [tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md).

5. **`cwe.yaml`** — ≥50 records. Seed: 41 unique CWEs currently cited across agent detection patterns. Expansion target: full CWE Top 25 (2024) list. Per-item record shape matches FR-2 **except** the `cwe_refs` field is omitted on CWE records (CWE→CWE relations belong in `crosswalk.yaml`, not in `cwe_refs`).

6. **`tachi-control-category.yaml`** *(new under Interpretation C)* — 8 records cataloguing tachi's compensating-control categories (seeded from [control-categories shared reference](../../.claude/skills/tachi-control-analysis/references/)). Carries the FR-2 record shape; serves as the `source.taxonomy = tachi-control-category` target for Surface B mapping edges in `crosswalk.yaml`.

7. **`tachi-stride-ai-category.yaml`** *(new under Interpretation C)* — 11 records cataloguing tachi's STRIDE+AI threat categories (seeded from [stride-categories-shared.md](../../.claude/skills/tachi-shared/references/stride-categories-shared.md)). Carries the FR-2 record shape; serves as the `source.taxonomy = tachi-stride-ai-category` target for Surface C mapping edges in `crosswalk.yaml`.

8. **`crosswalk.yaml`** — Per-edge records of shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`. `edge_type` ∈ closed enum `{primary, related, superseded}`. **F-A1 floor: ≥500 primary edges** (first-pass scope; `related`/`superseded` expansion is a follow-on Issue per Risk R3 Tier 1 adopted as the default scope in this PRD). Surface B mapping rows (~30) and Surface C mapping rows (~24) transcribe verbatim into `crosswalk.yaml` edges per FR-6.

9. **`README.md`** — Curation methodology, per-framework provenance notes, `confidence` calibration rubric (three-level: `high` / `medium` / `low`), canonical-URL conventions per framework (citation hygiene), and update procedure for each framework.

**Scope discipline**: F-A1 is **harvest + curate** — existing agent citations + the authored NIST mapping are the seed; external-source curation closes enumeration gaps. F-A1 does **not** touch [schemas/finding.yaml](../../schemas/finding.yaml), [scripts/](../../scripts/), [.claude/agents/](../../.claude/agents/), [.claude/skills/](../../.claude/skills/), [.claude/commands/](../../.claude/commands/), [templates/](../../templates/), or any runtime pipeline component. The finding-level schema extension that references these YAMLs is a follow-on feature (F-A2); the PDF coverage-attestation surface is a further follow-on (F-B).

### Success Criteria
- All **9 files** listed above exist under `schemas/taxonomy/` and pass YAML parse validation (`yaml.safe_load` against each file returns a dict/list without exception)
- `owasp.yaml` contains ≥60 items across LLM / Agentic / Web / API / Mobile / ML lists with **no duplicate IDs** (duplicate-detection test)
- `mitre-attack.yaml` contains ≥38 techniques (floor = current citation count; growth permitted via external curation)
- `mitre-atlas.yaml` contains ≥7 techniques and explicitly includes AML.T0058, T0059, T0060, T0061, T0062
- `cwe.yaml` contains ≥50 records (41 current citations + CWE Top 25 2024 expansion); `cwe_refs` field is omitted from CWE records
- `nist-ai-rmf.yaml` contains ≥68 Subcategory records covering the full AI RMF 1.0 Govern/Map/Measure/Manage Subcategory catalog; Surface B and Surface C mapping rows from [tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) transcribe verbatim into `crosswalk.yaml` edges (FR-6 Interpretation C) with zero re-derivation — spot-check: pick 5 Surface B rows and 5 Surface C rows; each resolves to exactly one `crosswalk.yaml` edge with matching `source.id` / `target.id` / `relationship`-to-`edge_type` fields
- `tachi-control-category.yaml` contains exactly 8 records (matching the canonical 8 tachi compensating-control categories)
- `tachi-stride-ai-category.yaml` contains exactly 11 records (matching the canonical 6 STRIDE + 5 AI threat categories)
- `crosswalk.yaml` passes an **expanded** referential-integrity test (FR-7) covering: (a) every `source.id` and `target.id` resolves to a record present in the named framework/pseudo-taxonomy YAML (no dangling references); (b) every `source.taxonomy` and `target.taxonomy` value is in the closed 7-value enum `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category}`; (c) every `edge_type` value is in the closed 3-value enum `{primary, related, superseded}`; (d) every `confidence` value is in the closed 3-value enum `{high, medium, low}`; (e) every `citation` is non-empty
- `crosswalk.yaml` contains **≥500 primary edges** in F-A1 (Risk R3 Tier 1 scope adopted as the default; `related` and `superseded` expansion is a follow-on Issue filed on merge)
- `schemas/taxonomy/README.md` documents: (a) harvest + curate methodology, (b) per-framework provenance, (c) `confidence` calibration rubric (high = published cross-reference; medium = inferred one-hop; low = two-hop / thematic), (d) canonical-URL conventions per framework, (e) update procedure per framework
- **Backward-compatibility invariant**: the 5 non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per the [ADR-021](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-determinism.md) determinism convention — verified by [tests/scripts/test_backward_compatibility.py](../../tests/scripts/test_backward_compatibility.py) remaining green in PR CI (Feature 128 bootstrap CI-enforces this, per Architect M2)
- A new public ADR is committed under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) (**expected ADR-027** — ADR-026 is already accepted for Feature 142; authorship must verify the next unused number at commit time and note ADR-004 lineage if absent from on-disk listing) with Status: **Proposed** at end of Day 1 (post-schema-freeze) and **Accepted** at PR merge, documenting the taxonomy schema decision — per-item record shape, per-edge record shape, `taxonomy` enum (7 values including the 2 pseudo-taxonomies), `edge_type` enum, `confidence` enum, and the cadence-exception rationale (single PRD despite aggregating 9 files)

### Timeline
**~4-5 working days** of active implementation (data authoring is the critical path), followed by a brief PR/governance cycle. Team-lead tightened the floor from 3 days to 4 days because the crosswalk-authoring leg dominates Day 3-4 under any authoring-rate assumption. A parallel 3-agent plan (senior-backend-engineer + web-researcher + architect) is the assumed execution shape; single-agent execution extends the budget to 5-6 days (captured in Risk R6).

- **Day 1 (parallel)**: architect freezes schema shape + drafts ADR to **Proposed** status (FR-10 gate); senior-backend-engineer authors `owasp.yaml` (60-80 items); web-researcher begins 50-edge crosswalk spike (**Day 1 gate** — see Risk R1 tripwire)
- **Day 2 (parallel)**: senior-backend-engineer authors MITRE ATT&CK + ATLAS + CWE YAMLs + `tachi-control-category.yaml` + `tachi-stride-ai-category.yaml` + begins `nist-ai-rmf.yaml` Subcategory catalog; web-researcher continues crosswalk citation discovery; architect drafts README.md + cross-reference edits
- **Day 3 (parallel)**: senior-backend-engineer completes `nist-ai-rmf.yaml` + authors ~54 NIST-derived Surface B/C crosswalk edges + assembles crosswalk records; web-researcher continues citation harvest toward the ≥500 primary-edge F-A1 floor
- **Day 4**: FR-7 referential-integrity test authored + backward-compat byte-identity verification + ADR moves from Proposed to Accepted + PR opened
- **Day 5 (buffer)**: ADR review iteration + crosswalk edge-count completion if Day 3 fell short + PR merge cycle

Largest risk is `crosswalk.yaml` edge authoring (scale: ≥500 primary edges with per-edge citation URLs); R1 Day 1 spike **carries a numeric tripwire** (measured >38.4s/edge → invoke R3 Tier 1 by Day 2 end; the PRD has already adopted Tier 1 as default scope, but the tripwire preserves the mechanism for a further Tier 2 or Tier 3 descope if velocity collapses below Tier 1 as well).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Tachi's vision is to be *"the default threat modeling toolkit for any team building agentic AI applications."* A default toolkit must ship a machine-readable taxonomy reference. Every adopter who integrates tachi into a downstream pipeline (CI/CD gate, SIEM ingestion, compliance-report generator) needs to resolve tachi's taxonomy IDs to canonical framework records. Today that resolution requires parsing markdown agent references; the default toolkit should ship the resolution data as a schema.

This also unlocks the **coverage-attestation** leg of the default-toolkit promise: adopters can compute "what percentage of OWASP LLM Top 10:2025 does tachi cover for my architecture?" only after the OWASP LLM Top 10 item list is machine-readable. F-A1 provides the denominator; downstream features (F-A2 finding-level attribution, F-B coverage attestation report section) provide the numerator and the rendering.

### Roadmap Fit
F-A1 is the **foundation feature** for a multi-feature threat-coverage initiative. It depends on no unshipped feature and blocks several downstream features that cannot proceed until taxonomy IDs are machine-readable:

- **F-A1 (this PRD)**: Taxonomy Crosswalk Collection — foundation; blocks all downstream
- **F-A2**: Source Attribution Schema Extension — extends [schemas/finding.yaml](../../schemas/finding.yaml) to reference F-A1 taxonomy IDs as first-class fields. Depends on F-A1.
- **F-B**: Coverage Attestation Report Section — new PDF section rendering coverage matrix per-finding. Depends on F-A2.
- **Multiple downstream gap-closure features**: consume F-A1 YAMLs for taxonomy-ID validation and F-A2 for finding-level citation.

F-A1 ships **as a single PRD** despite aggregating **9 files** (5 external framework YAMLs + 2 tachi pseudo-taxonomy YAMLs + `crosswalk.yaml` + `README.md` per Interpretation C). Foundation data has no natural decomposition boundary below framework-set granularity — splitting along artificial lines (e.g., "OWASP+CWE" vs "MITRE+NIST") would fragment a cohesive dataset and force redundant schema/convention work across PRDs. The work is data authoring over a consolidated dataset, not a set of independent gap-closure decisions. This rationale is recorded in the public ADR authored by this PRD (FR-10).

### Dependency Posture
- **Independent of any unshipped feature**: F-A1 does not require any other feature to land first
- **Blocks multiple features in flight**: F-A2 and F-B cannot proceed until F-A1 ships; downstream gap-closure features that cite taxonomy IDs depend on the YAMLs existing
- **Schema impact**: zero in this PRD — F-A1 does not modify [schemas/finding.yaml](../../schemas/finding.yaml). F-A2 will extend `finding.yaml` to reference F-A1 taxonomy IDs; that schema-extension work is out of scope here.
- **Runtime script impact**: zero — F-A1 does not modify [scripts/tachi_parsers.py](../../scripts/tachi_parsers.py), [scripts/extract-report-data.py](../../scripts/extract-report-data.py), or any other pipeline script
- **Agent impact**: zero — F-A1 does not modify any file under [.claude/agents/](../../.claude/agents/). The 11 threat-detection agents continue to cite taxonomy IDs in their `detection-patterns.md` references as they do today. (Future work may migrate agent references to cite `schemas/taxonomy/` YAMLs as the single source of truth; that migration is out of scope here.)

---

## Target Users & Personas

### Primary Persona: Adopter / Downstream Integration Engineer
**Role**: Security engineer or platform engineer integrating tachi into a larger security workflow (CI/CD gate, SIEM, compliance pipeline, threat-intelligence correlation)
**Experience**: Comfortable reading YAML; familiar with OWASP/MITRE/NIST/CWE taxonomies; not a tachi internals expert
**Goals**: Map tachi findings to their organization's existing taxonomy (e.g., CWE-based vulnerability management, MITRE ATT&CK-based detection engineering) without hand-maintaining a translation table
**Pain Points**: Today must grep tachi agent definitions to find taxonomy IDs; mappings change without warning; no stable record to reference

**Why This Matters to Them**: The adopter's integration code needs to run `yaml.safe_load('schemas/taxonomy/owasp.yaml')` and iterate over records. That integration is fragile today because the data does not exist as a schema.

### Secondary Persona: Tachi Maintainer / Framework Curator
**Role**: Tachi contributor who authors agent detection patterns or builds downstream features consuming taxonomy IDs
**Experience**: Deep tachi internals knowledge; owns the accuracy of cross-taxonomy mappings
**Goals**: Add a new CWE or ATLAS technique citation in an agent reference and have it automatically visible in coverage computations; update a mapping edge (e.g., LLM05↔CWE-1426 relationship changes) in one canonical location
**Pain Points**: Today each new citation must be added to multiple agent references; no canonical crosswalk exists to catch inconsistencies; no update procedure for framework revisions

**Why This Matters to Them**: The maintainer needs a single file per framework and a single crosswalk file. Today the same taxonomy ID may appear in three agent references with inconsistent formatting.

### Tertiary Persona: Reviewer / Coverage Auditor
**Role**: External reviewer (open-source contributor, adopter's security team, external auditor) validating tachi's taxonomy coverage claims
**Experience**: Domain expert in one or more of the five frameworks; does not need tachi codebase expertise
**Goals**: Validate that a taxonomy-coverage claim (e.g., "tachi covers 38 MITRE ATT&CK techniques") is grounded in auditable data; propose additions or corrections via PR
**Pain Points**: Today must read agent definitions to audit coverage; corrections require agent-file PRs which are scoped to detection patterns, not taxonomy records

**Why This Matters to Them**: The reviewer can file a `schemas/taxonomy/owasp.yaml` PR to add a missing LLM Top 10 item without touching any agent; the curation README documents how PRs against the directory are reviewed.

---

## User Stories

### US-180-1: Machine-Readable Taxonomy Records (P0)
**When** I am an adopter integrating tachi output into a downstream system that consumes taxonomy IDs (vulnerability manager, SIEM, compliance report),
**I want to** resolve every OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE ID tachi cites to a stable machine-readable record with canonical ID, display name, source URL, and cross-framework references,
**So I can** programmatically link tachi output to any compliance framework that maps to these taxonomies without re-deriving the mapping by hand.

**Acceptance Criteria**:
- **Given** `schemas/taxonomy/owasp.yaml`, **when** I `yaml.safe_load` it, **then** I get a list of ≥60 records spanning LLM, Agentic, Web, API, Mobile, and ML lists, each with `{id, full_id, name, url, cwe_refs}` fields
- **Given** `schemas/taxonomy/mitre-attack.yaml`, **when** I `yaml.safe_load` it, **then** I get a list of ≥38 techniques seeded from current agent detection-pattern citations
- **Given** `schemas/taxonomy/mitre-atlas.yaml`, **when** I iterate over records, **then** I find AML.T0058, T0059, T0060, T0061, T0062 among the ≥7 techniques
- **Given** `schemas/taxonomy/nist-ai-rmf.yaml`, **when** I compare records to the Surface B and Surface C tables in [tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md), **then** every YAML row traces 1:1 to a table row with matching key fields
- **Given** `schemas/taxonomy/cwe.yaml`, **when** I count records, **then** I find ≥50 (41 current citations + CWE Top 25 2024 expansion)

**Priority**: P0
**Effort**: L (data authoring is the dominant cost; ~60-80 OWASP items + 38 ATT&CK + 7 ATLAS + ~50 CWEs + verbatim NIST transcription)

### US-180-2: Single Authoritative Crosswalk (P0)
**When** I am a tachi maintainer who needs to know how a single threat concept (e.g., "improper output handling") maps across multiple taxonomies,
**I want to** find all cross-framework edges in one canonical crosswalk file with a closed `edge_type` enum and per-edge citation,
**So I can** update mapping data in one place and have downstream features consume consistent edges without duplicating mapping logic.

**Acceptance Criteria**:
- **Given** `schemas/taxonomy/crosswalk.yaml`, **when** I `yaml.safe_load` it, **then** I get a list of edges where each edge has the exact shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`
- **Given** any edge, **when** I check `edge_type`, **then** it is exactly one of `{primary, related, superseded}` (unknown values fail the integrity test)
- **Given** any edge, **when** I look up `source.id` and `target.id`, **then** both resolve to records present in one of the 5 framework YAMLs (zero dangling references)
- **Given** the full crosswalk, **when** I count edges, **then** the total is **≥500 primary edges** per the F-A1 Tier 1 default scope (FR-3); `related` and `superseded` edges are a follow-on Issue scope
- **Given** any edge, **when** I follow `citation`, **then** I reach either a retrievable URL or an internal file path that exists in the repo

**Priority**: P0
**Effort**: L (1-2K edges; citation authoring is the scale driver)

### US-180-3: Documented Curation Methodology (P1)
**When** I am a reviewer validating tachi's taxonomy coverage claims (or a future tachi maintainer preparing for an OWASP/MITRE/NIST/CWE framework revision),
**I want to** find a documented harvest + curate methodology, per-framework provenance log, and update procedure shipped alongside the data,
**So I can** audit the data's lineage and execute future taxonomy refreshes with a reproducible process rather than an ad-hoc harvest.

**Acceptance Criteria**:
- **Given** `schemas/taxonomy/README.md`, **when** I read it, **then** it documents the harvest + curate methodology (how items were gathered from agent citations + NIST crosswalk + external sources)
- **Given** the README, **when** I look for per-framework provenance, **then** the README contains **7 catalog sections** (5 external frameworks + 2 tachi pseudo-taxonomies per Interpretation C) each with a provenance note stating (a) seed sources and counts, (b) external-curation sources closing enumeration gaps, (c) what was added beyond the seed
- **Given** the README, **when** I look for update procedures, **then** each framework has a documented procedure for its next revision (e.g., "When OWASP LLM Top 10 v2027 publishes, regenerate `owasp.yaml` by …")
- **Given** the README records current-state citation counts, **when** I cross-check against the 11 agent detection-pattern references, **then** the counts (38 ATT&CK, 7 ATLAS, 41 CWE, full NIST crosswalk) match the documented baseline

**Priority**: P1
**Effort**: M (README authoring is smaller than the YAML authoring but requires accurate provenance accounting)

---

## Functional Requirements

### FR-1: Directory Structure
A new directory `schemas/taxonomy/` is created containing exactly **9 files**: `owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`, `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`, `crosswalk.yaml`, `README.md`. No additional files are introduced at this level. All filenames are lowercase with kebab-case where applicable. **(Q1 resolved: Architect-recommended Interpretation C adopted — two pseudo-taxonomy YAMLs added to preserve FR-2 shape uniformity and referential-integrity across NIST Surface B/C mapping edges.)**

### FR-2: Per-Item Record Shape (framework + pseudo-taxonomy YAMLs)
Each of the 7 item-catalog YAMLs (5 external framework YAMLs + 2 tachi pseudo-taxonomy YAMLs) uses the per-item record shape `{id, full_id, name, url, cwe_refs}`:
- `id` — short canonical ID (e.g., `LLM05`, `T1190`, `AML.T0058`, `CWE-1426`, `MEASURE-2.7`, `prompt-injection-defense`, `spoofing`)
- `full_id` — human-readable long form including framework prefix (e.g., `OWASP-LLM-2025-05`, `ATT&CK-T1190`, `ATLAS-AML.T0058`, `CWE-1426`, `NIST-AI-RMF-MEASURE-2.7`, `TACHI-CONTROL-prompt-injection-defense`, `TACHI-STRIDE-AI-spoofing`)
- `name` — canonical item name from the authoritative source
- `url` — retrievable URL to the authoritative source (for external frameworks) OR the internal file path to the canonical definition (for pseudo-taxonomies, e.g., `.claude/skills/tachi-shared/references/stride-categories-shared.md`)
- `cwe_refs` — optional list of related CWE IDs; populated where the source item publishes cross-references (unidirectional OWASP→CWE only per Q3 resolution); **omitted entirely from `cwe.yaml` records** (CWE→CWE relations belong in `crosswalk.yaml`, not in `cwe_refs`)

### FR-3: Per-Edge Record Shape (crosswalk.yaml)
Every edge in `crosswalk.yaml` uses the record shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`:
- `source.taxonomy` and `target.taxonomy` ∈ closed **7-value** enum `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category}` (the 7 item-catalog YAML filename stems — 5 external frameworks + 2 tachi pseudo-taxonomies per Interpretation C)
- `source.id` and `target.id` — must resolve to a record present in the corresponding catalog YAML (no dangling references per FR-7)
- `edge_type` ∈ closed enum `{primary, related, superseded}` — no free-text edge descriptions
- `confidence` ∈ closed enum `{high, medium, low}` (calibration rubric documented in README per FR-8: `high` = published cross-reference; `medium` = inferred one-hop; `low` = two-hop / thematic)
- `citation` — non-empty string (enforced by FR-7); must be either a retrievable URL shape (regex-validated) or an internal repo file path (existence-validated)

### FR-4: Seed from Existing Citations
The 3 external framework YAMLs with pre-existing tachi citation baselines (`mitre-attack.yaml`, `mitre-atlas.yaml`, `cwe.yaml`) are seeded from the current 11 threat-detection agents' `detection-patterns.md` references:
- `mitre-attack.yaml` seed: the 38 unique MITRE ATT&CK techniques currently cited across the 11 references
- `mitre-atlas.yaml` seed: the 7 unique MITRE ATLAS techniques currently cited (explicitly including AML.T0058, T0059, T0060, T0061, T0062)
- `cwe.yaml` seed: the 41 unique CWEs currently cited

**Assumption A1 validation**: re-verify these counts via grep at spec time (not just PRD time) to confirm 38 / 7 / 41 still holds after any recent agent-reference edits. The seed harvest is the starting set; external-source curation closes enumeration gaps above each seed count. The `README.md` records the seed counts as a traceable baseline (US-180-3 AC-3).

Pseudo-taxonomies (`tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`) seed from their respective canonical shared references ([stride-categories-shared.md](../../.claude/skills/tachi-shared/references/stride-categories-shared.md) + [tachi-control-analysis references](../../.claude/skills/tachi-control-analysis/references/)).

### FR-5: External Curation for Enumeration Coverage
Each framework YAML is expanded beyond its seed to close documented enumeration gaps:
- `owasp.yaml`: ≥60 items spanning 6 OWASP lists (LLM Top 10:2025, Agentic Top 10:2026, Top 10:2021, API Security Top 10:2023, Mobile Top 10:2024, ML Top 10:2023)
- `mitre-attack.yaml`: starts at 38 seed; growth via external ATT&CK matrix curation is permitted but not mandated in F-A1
- `mitre-atlas.yaml`: starts at 7 seed; growth via external ATLAS matrix curation is permitted but not mandated in F-A1
- `cwe.yaml`: 41 seed + full CWE Top 25 (2024) expansion → ≥50 records
- `nist-ai-rmf.yaml`: ≥68 Subcategory records covering the full AI RMF 1.0 Subcategory catalog (sourced from NIST AI 100-1 Tables 1-4) — this is the **catalog** per Interpretation C, not the Surface B/C mapping rows (which live in `crosswalk.yaml`)

### FR-6: NIST AI RMF Mapping (Interpretation C)
**Q1 resolved** in favor of **Architect-recommended Interpretation C (hybrid)**:
- `nist-ai-rmf.yaml` carries the **per-Subcategory catalog** of NIST AI RMF 1.0 Subcategories (≥68 records) using the uniform FR-2 record shape. This is a catalog of NIST items, structurally parallel to the other 4 external framework YAMLs. Source: NIST AI 100-1 Tables 1-4 (the published Govern/Map/Measure/Manage Subcategory enumeration).
- The **Surface B and Surface C mapping rows** in [tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) transcribe **verbatim** into `crosswalk.yaml` edges. Each Surface B row becomes an edge from `tachi-control-category` to `nist-ai-rmf`; each Surface C row becomes an edge from `tachi-stride-ai-category` to `nist-ai-rmf`.
- Surface cell rows labeled "No equivalent" are **omitted** from `crosswalk.yaml` — absence of an edge is the positive-only representation of "no equivalent" (avoids sentinel-row explosion).
- Estimated edge additions from the NIST surfaces: ~30 Surface B edges + ~24 Surface C edges = ~54 NIST-derived edges counted toward the ≥500 primary-edge F-A1 floor.

If the PRD author or implementing agent discovers that a Surface B or Surface C row is factually inaccurate during transcription, the correction is filed as a **separate ADR-025 amendment Issue**, not made silently during F-A1 transcription. F-A1 is a transcription feature, not a re-authorship feature.

### FR-7: Referential Integrity Test (Expanded)
A test at `tests/schemas/test_taxonomy_integrity.py` (**Q2 resolved**: new `tests/schemas/` subdirectory preserves the semantic boundary between Python script tests in `tests/scripts/` and YAML data tests in `tests/schemas/`; new `tests/schemas/__init__.py` bootstraps the subdirectory). The test suite contains four test functions:

- **`test_framework_yamls_load()`**: each of the 7 catalog YAMLs parses via `yaml.safe_load`; every record carries all FR-2 required fields (`id`, `full_id`, `name`, `url`; `cwe_refs` required on `owasp.yaml` and optional/empty on others except omitted on `cwe.yaml`); every `id` is unique within its own file; every `url` value matches a URL-shape regex (no HTTP fetch) OR (for pseudo-taxonomies) resolves to an existing file path in the repo
- **`test_crosswalk_loads()`**: `crosswalk.yaml` parses; every edge carries all FR-3 required fields (`source.taxonomy`, `source.id`, `target.taxonomy`, `target.id`, `edge_type`, `confidence`, `citation`); no duplicate edges (same `{source, target, edge_type}` triple)
- **`test_crosswalk_referential_integrity()`**: every edge's `source.id` resolves to an `id` in the catalog YAML named by `source.taxonomy`; every `target.id` resolves similarly; every `source.taxonomy` and `target.taxonomy` is in the closed 7-value enum; every `edge_type` is in the closed 3-value enum; every `confidence` is in the closed 3-value enum
- **`test_citation_shape()`**: every `citation` is non-empty; each citation is either URL-shaped (regex-only, no HTTP fetch — preserves ADR-021 determinism) or resolves to an existing file path relative to the repo root

An optional fifth test `test_records_sorted()` (per Architect NFR-3 recommendation) asserts stable record ordering (alphabetical by `id` within each catalog YAML; lexicographic on `{source.taxonomy, source.id, target.taxonomy, target.id}` for crosswalk edges). Failing CI / local `make test` on any violation.

### FR-8: Curation README
`schemas/taxonomy/README.md` documents:
- **Purpose**: why `schemas/taxonomy/` exists and what downstream features consume it (F-A2 finding attribution; F-B coverage attestation; ecosystem integrations)
- **Harvest methodology**: how items were gathered (seed from 11 agent detection-pattern references + NIST mapping + CWE Top 25 external source)
- **Per-framework provenance**: 7 sections (one per catalog YAML — 5 external frameworks + 2 pseudo-taxonomies) each stating (a) seed source and count, (b) external-curation sources, (c) what was added beyond the seed
- **`confidence` calibration rubric**: three levels with examples — `high` (published cross-reference, e.g., OWASP LLM Top 10 §05 explicitly lists CWE-1426); `medium` (inferred one-hop, e.g., LLM05 relates to CWE-79 via category-semantic match without explicit listing); `low` (two-hop or thematic, e.g., ATT&CK T1190 relates to OWASP API7 via adversary-objective alignment requiring curator judgment). **Anti-drift rule**: if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label.
- **Canonical-URL conventions per framework**: ATT&CK `https://attack.mitre.org/techniques/T<N>/`; ATLAS `https://atlas.mitre.org/techniques/AML.T<NNNN>`; CWE `https://cwe.mitre.org/data/definitions/<N>.html`; NIST DOI-based URLs; OWASP list URLs rather than search anchors. Reduces citation rot probability.
- **Update procedure**: 5 sections (one per external framework) each stating the procedure for the next framework revision — e.g., "When OWASP LLM Top 10 v2027 publishes: (1) fetch the new list, (2) compare to `owasp.yaml` LLM section, (3) update or deprecate affected records using `edge_type: superseded` on the crosswalk …"
- **Crosswalk methodology**: how edges are authored, how `edge_type` is assigned, how `confidence` is calibrated, what counts as a valid `citation`
- **Single-source-of-truth cross-reference** (per Architect L5 + [ADR-020](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) / [ADR-023](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) patterns): the README links to [tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) as the NIST Surface B/C authoring source rather than restating Surface B/C content inline

### FR-9: Backward Compatibility Invariant
F-A1 **adds files only**. No existing file under [schemas/](../../schemas/) (excluding the new `schemas/taxonomy/` directory), [scripts/](../../scripts/), [.claude/agents/](../../.claude/agents/), [.claude/skills/](../../.claude/skills/), [.claude/commands/](../../.claude/commands/), [templates/](../../templates/), or [tests/](../../tests/) (excluding new `tests/schemas/`) is modified (**per Architect M1**: explicit scope widening covers `.claude/skills/` and `.claude/commands/` which were implicit in the original draft). **No existing file under `.claude/skills/*/references/*.md` is modified** — new skill references may be added to F-A1 only if required by the authorship workflow and documented explicitly.

The 5 non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per [ADR-021](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-determinism.md). The backward-compatibility test `tests/scripts/test_backward_compatibility.py` **runs in PR CI per the Feature 128 bootstrap**; green state is enforced at the merge gate, not by manual verification (per Architect M2).

The 6th example (`agentic-app`) similarly regenerates byte-identically because F-A1 does not touch any runtime script or agent. (Note: `agentic-app` is intentionally non-baselined in the byte-identity suite per the Feature 128/142 convention; the backward-compat harness baselines only the 5 non-agentic examples.)

### FR-10: Public ADR on Merge
A new public ADR is authored and committed under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) using the next available ADR number (**expected ADR-027** as of this PRD's creation date — ADR-026 is already accepted for Feature 142 per [the committed `ADR-026-pattern-classification-mechanism.md`](../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md); authorship must verify the next unused number at commit time). **ADR-004 lineage note**: ADR-004 is absent from the on-disk listing at PRD creation time; spec-phase authorship should verify whether ADR-004 is historically reserved/skipped (in which case ADR-027 stands as the next available) or whether ADR-004 should be reclaimed first. ADR content:
- **Decision**: introduce `schemas/taxonomy/` with the per-item and per-edge record shapes specified in FR-2 and FR-3
- **Scope-exception rationale**: documents why F-A1 ships as a single PRD despite aggregating 9 files (foundation data has no natural decomposition boundary below framework-set granularity)
- **Enum domains**: `taxonomy` enum (7 filename stems — 5 external frameworks + 2 tachi pseudo-taxonomies per Interpretation C), `edge_type` enum (3 values), `confidence` enum (3 values) all committed in the ADR
- **Interpretation C rationale**: documents why Q1 resolved in favor of the hybrid approach (preserves FR-2 uniformity; preserves FR-6 verbatim transcription contract by moving mapping rows to crosswalk edges; makes `tachi-control-category` and `tachi-stride-ai-category` first-class referential-integrity targets)
- **Related ADRs**: [ADR-020](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) (shared-reference-as-single-source-of-truth pattern), [ADR-021](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-determinism.md) (determinism convention invoked by FR-9), [ADR-023](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) (skill-references pattern, per Architect L5), [ADR-025](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) (NIST AI RMF mapping source for FR-6), [ADR-024](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md) (precedent for publishing a peer-framework reference without wiring it into runtime behavior)
- **Status**: **Proposed** at end of Day 1 (post-schema-freeze / post-OWASP authoring — Architect Q5 resolution); **Accepted** at PR merge

---

## Non-Functional Requirements

### NFR-1: Parse Performance
Each framework YAML must `yaml.safe_load` in <100ms on commodity hardware (≤500 records per file; simple record shapes). `crosswalk.yaml` at 1-2K edges must load in <500ms. These bounds are well within headroom — this NFR is a sanity check, not a performance ceiling.

### NFR-2: In-Memory Footprint
Full taxonomy index (all 5 framework YAMLs + `crosswalk.yaml`) must fit in <10MB of process memory when loaded as Python dicts — trivial at the specified scale (~500 nodes + ~2K edges), but explicitly bounded to prevent scope creep in future iterations.

### NFR-3: Determinism
YAML files are authored with stable record ordering (alphabetical by `id` within each framework file; lexicographic on `{source.taxonomy, source.id, target.taxonomy, target.id}` for crosswalk edges). Determinism is a repo hygiene property (diff review, PR audit) — it does **not** affect the ADR-021 byte-identity backward-compat invariant (which is about runtime PDF generation, not YAML source).

### NFR-4: Zero New Runtime Dependencies
F-A1 ships data, not code. No changes to [pyproject.toml](../../pyproject.toml), [requirements.txt](../../requirements.txt), `requirements-dev.txt`, or [package.json](../../package.json). If a taxonomy-integrity test is added under `tests/schemas/`, it uses the existing pytest harness bootstrapped in Feature 128 — no new test-framework dependencies.

### NFR-5: Documentation Discoverability
`schemas/taxonomy/README.md` is linked from:
- The top-level [README.md](../../README.md) — a single cross-reference in the appropriate section (Pipeline Schemas or equivalent — exact location deferred to spec phase)
- [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md) — a single cross-reference under Schemas or Conventions

Zero other documentation files are modified beyond these two cross-references.

---

## Scope & Boundaries

### In Scope (F-A1)
- ✅ 5 external framework YAMLs (`owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`)
- ✅ 2 tachi pseudo-taxonomy YAMLs (`tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`) — per Interpretation C
- ✅ `crosswalk.yaml` with **≥500 primary edges** (Risk R3 Tier 1 default scope; `related`/`superseded` expansion is a follow-on Issue)
- ✅ `schemas/taxonomy/README.md`
- ✅ `tests/schemas/test_taxonomy_integrity.py` + `tests/schemas/__init__.py` (Q2 resolved — new subdirectory)
- ✅ Public ADR (expected ADR-027) on merge
- ✅ 2 cross-reference links in top-level [README.md](../../README.md) and [docs/architecture/00_Tech_Stack/README.md](../../docs/architecture/00_Tech_Stack/README.md)

### Out of Scope (Explicitly Excluded — Future Features)
- ❌ **`related` and `superseded` crosswalk edges**: F-A1 default scope is **Risk R3 Tier 1 (primary-only, ≥500 edges)** per Architect H4 + Team-Lead H1 resolution. `related` and `superseded` edge expansion (to reach the original 1,000-2,000 aspiration) is a follow-on Issue filed on F-A1 merge, not part of this PRD's Definition of Done.
- ❌ **F-A2 schema extension**: `source_attribution` field addition to [schemas/finding.yaml](../../schemas/finding.yaml) is a separate PRD. `finding.yaml` is not modified in F-A1.
- ❌ **F-B coverage attestation**: a new PDF report section rendering coverage matrix per-finding is a separate PRD. No Typst template or `extract-report-data.py` change is in F-A1.
- ❌ **Agent reference migration**: migrating the 11 threat-detection agents' `detection-patterns.md` files to cite `schemas/taxonomy/` YAMLs as the single source of truth is not in F-A1. The YAMLs ship as a parallel authoritative reference; agent references continue to cite taxonomy IDs in prose as they do today.
- ❌ **Full external-source curation**: F-A1 scope is "seed + fill documented enumeration gaps" (≥60 OWASP, ≥50 CWE including Top 25 2024, etc.). Complete coverage of each framework's full item catalog is deferred to downstream features (F-8 attestation audit) that will grow the YAMLs as concrete coverage claims are validated.
- ❌ **Multi-language taxonomy support**: YAMLs are English-only. Internationalization is out of scope.
- ❌ **Runtime pipeline integration**: no agent, orchestrator, script, or template consumes `schemas/taxonomy/` YAMLs at runtime in F-A1. Integration begins in F-A2.
- ❌ **Citation URL link-rot monitoring**: no CI check validates URL reachability. Link-rot monitoring is a recommended follow-on Issue (per Team-Lead "Additional Risk Not Surfaced"); `schemas/taxonomy/README.md` documents canonical-URL conventions (FR-8) to reduce rot probability but does not enforce periodic re-validation.

### Won't Have (Explicitly Declined)
- ❌ **Non-YAML formats**: JSON-LD, RDF, SKOS, or other semantic-web formats are not generated. YAML is the single source of truth; conversions (if ever needed) are downstream.
- ❌ **Interactive crosswalk browser**: no web UI, no static HTML page, no browsable interface. YAMLs are PR-reviewable as text; browsing is out of scope.
- ❌ **Automated crosswalk inference**: no LLM-based edge generation, no similarity-scored auto-mapping. Every edge is human-authored with a citation; mechanical derivation is declined to preserve curator accountability.

### Assumptions
- **A1**: The 11 threat-detection agents' `detection-patterns.md` files are the authoritative seed source for ATT&CK/ATLAS/CWE citation counts. Counts harvested at F-A1 time (2026-04-17) are a pinned baseline; subsequent agent-reference edits do not invalidate F-A1.
- **A2**: PRD 144 / ADR-025 Surface B and Surface C tables are stable and authoritative at F-A1 time. No amendment is in flight as of PRD creation.
- **A3**: CWE Top 25 (2024) is the current authoritative Top 25 list. If CWE Top 25 (2025) publishes between F-A1 spec and merge, the `cwe.yaml` Top 25 expansion targets the latest published list at merge time (documented in the README provenance note).
- **A4**: The ≥500 primary-edge floor for `crosswalk.yaml` (Risk R3 Tier 1 default scope) is achievable in the 4-5 day parallel timeline given an authoring rate at or below the Day 1 spike tripwire (38.4s/edge). If the tripwire fires, further descope via Risk R3 Tier 2 (300 edges, team-lead-authorizable) or Tier 3 (150 edges, PRD amendment) is pre-authorized. The original 1,000+ edge aspiration is a follow-on Issue target, not an F-A1 commitment (see Risk R3 Clarification).

**Validation Needed**:
- [ ] A1: verify current seed counts by grepping the 11 `detection-patterns.md` references at spec time (not just PRD time) to confirm 38 / 7 / 41 still holds
- [ ] A2: confirm no ADR-025 amendment Issue is in flight before F-A1 spec starts
- [ ] A3: check [cwe.mitre.org/top25/](https://cwe.mitre.org/top25/) for the current Top 25 year at spec time
- [ ] A4: first-day spike on 50 edges to calibrate per-edge authoring time; if projection exceeds 5 days, invoke Risk R3 mitigation

### Constraints

**Technical Constraints**:
- **No runtime script changes**: FR-9 backward-compatibility invariant is a hard constraint; F-A1 must not touch any `scripts/*.py` or agent `*.md` file
- **YAML parse cleanliness**: all 8 YAML files (5 external framework YAMLs + 2 pseudo-taxonomy YAMLs + `crosswalk.yaml`) must parse via `yaml.safe_load` without errors; malformed records block merge
- **Referential integrity**: FR-7 integrity test must pass before PR merge

**Business Constraints**:
- **Timeline**: 4-5 working day target (parallel 3-agent execution); Risk R3 Tier 2/Tier 3 authorizes further scope-reduction on `crosswalk.yaml` edge counts if Day 1 spike tripwire fires (Tier 1 ≥500 primary-only is already adopted as default)
- **Single-PRD cadence exception**: this PRD deliberately aggregates 5 framework YAMLs + crosswalk into one delivery. The cadence exception is documented in FR-10 ADR and is bounded to foundation-data features; it does not set precedent for downstream gap-closure features.

**External Dependencies** (all authored pre-F-A1, no runtime fetches):
- OWASP Top 10 for LLM Applications 2025 — public list at [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/)
- OWASP Top 10 for Agentic Applications 2026 — public list at [genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- OWASP Top 10:2021, OWASP API Security Top 10:2023, OWASP Mobile Top 10:2024, OWASP Machine Learning Security Top 10:2023 — public lists at owasp.org
- MITRE ATT&CK Enterprise at [attack.mitre.org](https://attack.mitre.org/)
- MITRE ATLAS at [atlas.mitre.org](https://atlas.mitre.org/)
- CWE Top 25 (2024) at [cwe.mitre.org/top25](https://cwe.mitre.org/top25/)
- NIST AI RMF 1.0 + AI 600-1 Generative AI Profile — already-fetched and synthesized in PRD 144 / ADR-025 / [tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md)

---

## Success Metrics

### Metric 1: File Completeness
- **Definition**: **9 files** exist under `schemas/taxonomy/` with correct filenames (per Interpretation C: 5 external framework YAMLs + 2 pseudo-taxonomy YAMLs + crosswalk + README)
- **Baseline**: 0
- **Target**: 9
- **Timeline**: PR merge
- **Owner**: senior-backend-engineer (authorship) / code-reviewer (verification in PR)

### Metric 2: Record Count Floors
- **Definition**: Per-file record count meets or exceeds the PRD floor
- **Baseline**: not applicable (files do not exist)
- **Target**: `owasp.yaml` ≥60, `mitre-attack.yaml` ≥38, `mitre-atlas.yaml` ≥7 (incl. AML.T0058-T0062), `nist-ai-rmf.yaml` ≥68 (full AI RMF 1.0 Subcategory catalog), `cwe.yaml` ≥50, `tachi-control-category.yaml` = 8 (exact), `tachi-stride-ai-category.yaml` = 11 (exact), `crosswalk.yaml` ≥500 primary edges (Risk R3 Tier 1 default)
- **Timeline**: PR merge
- **Owner**: code-reviewer

### Metric 3: Referential Integrity Test Pass Rate
- **Definition**: FR-7 integrity test passes
- **Baseline**: test does not exist
- **Target**: test exists and passes in CI / local `make test`
- **Timeline**: PR merge
- **Owner**: implementing agent

### Metric 4: Backward-Compatibility Byte-Identity
- **Definition**: 5 non-agentic example PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` — i.e., `tests/scripts/test_backward_compatibility.py` stays green
- **Baseline**: currently green
- **Target**: still green at PR merge
- **Timeline**: PR merge
- **Owner**: implementing agent

### Metric 5: Zero-Surface-Area Runtime Diff
- **Definition**: `git diff main..HEAD -- scripts/ .claude/agents/ templates/ schemas/*.yaml` (excluding `schemas/taxonomy/`) returns empty output at PR merge
- **Baseline**: not applicable
- **Target**: empty diff
- **Timeline**: PR merge
- **Owner**: reviewer (manual verification) — a pre-merge checklist item on the PR

### Metric 6: Public ADR Committed
- **Definition**: a new ADR (**expected ADR-027** per FR-10) is committed under [docs/architecture/02_ADRs/](../../docs/architecture/02_ADRs/) with Status: **Proposed** at end of Day 1 (Architect Q5 resolution) and **Accepted** at PR merge
- **Baseline**: 0 new ADRs
- **Target**: 1
- **Timeline**: Proposed by end of Day 1; Accepted at PR merge
- **Owner**: architect (authorship)

### Metric 7: Adopter Resolution Path (outcome-measurable, per PM H-PM-1)
- **Definition**: post-merge, an adopter integration can resolve a tachi taxonomy ID to a canonical record in ≤1 code statement per framework. Example: `owasp_records = yaml.safe_load(open('schemas/taxonomy/owasp.yaml'))` followed by `record = next(r for r in owasp_records if r['id'] == 'LLM05')` — the two-line idiom is a single Python expression in spirit; the target is that a reader of `schemas/taxonomy/README.md` learns the resolution pattern without consulting any other file
- **Baseline**: not measurable today (no machine-readable records exist; adopters must grep agent markdown prose)
- **Target**: README §Purpose or §Usage section contains a runnable Python code snippet demonstrating the resolution path for all 7 catalog YAMLs (5 external frameworks + 2 pseudo-taxonomies); snippet loads correctly in a fresh Python 3.11 environment with only `pyyaml` installed
- **Timeline**: PR merge
- **Owner**: architect (README authorship) + code-reviewer (runnable-snippet verification in PR)

---

## Timeline & Milestones

### Phase Breakdown (3-agent parallel execution assumed)
**Phase 1: Schema Freeze + OWASP + Day 1 Crosswalk Spike** (Day 1)
- **architect**: freezes schema shape (FR-2 record shape, FR-3 edge shape, 7-value taxonomy enum per Interpretation C); drafts ADR-027 to **Proposed** status (Q5 gate — Proposed ADR is the Phase 1 deliverable, not an optional enhancement)
- **senior-backend-engineer**: authors `owasp.yaml` (60-80 items across 6 OWASP lists); sets up `tests/schemas/` subdirectory + `__init__.py` + test skeleton
- **web-researcher**: executes **50-edge crosswalk spike** on a diverse slice (10 OWASP↔CWE + 10 ATT&CK↔CWE + 10 ATT&CK↔ATLAS + 10 LLM↔NIST + 10 Agentic↔MITRE). **Day 1 gate** measures wall-clock time per edge; projection = (50 edges) / measured_seconds extrapolated to 500. **Numeric tripwire** per Team-Lead H1: measured >38.4s/edge → further R3 descope escalation (from Tier 1 default to Tier 2 or Tier 3) triggered at end of Day 2
- **Deliverable**: committed `owasp.yaml`; ADR in Proposed state; Day 1 spike outcome recorded in spec.md with tripwire decision logged

**Phase 2: MITRE + CWE + Pseudo-Taxonomies + NIST Catalog** (Day 2)
- **senior-backend-engineer** (parallel): `mitre-attack.yaml` (38 agent citations) + `mitre-atlas.yaml` (7 agent citations incl. AML.T0058-T0062) + `cwe.yaml` (41 seed + CWE Top 25 2024 → ≥50 records) + `tachi-control-category.yaml` (8 records from control-analysis shared ref) + `tachi-stride-ai-category.yaml` (11 records from stride-categories-shared.md) + **begins `nist-ai-rmf.yaml` Subcategory catalog** (≥68 records from AI 100-1 Tables 1-4)
- **web-researcher** (parallel): continues crosswalk citation discovery; targets ~200 edges by end of Day 2
- **architect** (parallel): drafts README.md (FR-8 methodology + calibration rubric + canonical-URL conventions + update procedures); drafts cross-reference edits to top-level README.md + docs/architecture/00_Tech_Stack/README.md
- **Deliverable**: 5 YAMLs committed (3 MITRE/CWE + 2 pseudo-taxonomies); `nist-ai-rmf.yaml` in progress; ~200 crosswalk edges in progress; README draft

**Phase 3: NIST + Crosswalk Assembly** (Day 3)
- **senior-backend-engineer**: completes `nist-ai-rmf.yaml` Subcategory catalog; authors ~54 NIST-derived Surface B/C crosswalk edges (verbatim per FR-6); assembles crosswalk records from web-researcher citation batches
- **web-researcher**: completes citation harvest — target ≥500 primary edges by end of Day 3
- **architect**: finalizes README.md + cross-references; coordinates on integrity test fixtures
- **Deliverable**: all 9 YAMLs committed; crosswalk at ≥500 primary edges; README finalized

**Phase 4: Testing + ADR-Accepted + PR** (Day 4)
- **senior-backend-engineer**: authors FR-7 expanded referential-integrity test suite (4 test functions + optional 5th for sort order); runs it locally; fixes any violations
- **code-reviewer**: runs `SOURCE_DATE_EPOCH=1700000000` regeneration + backward-compat byte-identity verification (Metric 4)
- **architect**: ADR moves from Proposed to **Accepted**; authors PR description with Interpretation C rationale; opens PR
- **Deliverable**: green tests, ADR-Accepted, PR opened

**Phase 5: Review + Buffer** (Day 5)
- PR review cycle; ADR review iteration; crosswalk edge-count completion if Day 3 fell short
- **Deliverable**: merged PR

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-17 | product-manager | 🟡 In Review |
| Spec Complete | +1 day from PRD approval | architect | 📋 Pending |
| Tasks Complete (Triad sign-off) | +1 day from spec | team-lead | 📋 Pending |
| Implementation Phase 1 done (schema + OWASP + ADR Proposed + Day 1 spike) | +1 day from tasks | architect + senior-backend-engineer + web-researcher | 📋 Pending |
| Implementation Phase 4 done (tests + ADR Accepted + PR open) | +4 days from tasks | senior-backend-engineer + code-reviewer + architect | 📋 Pending |
| PR merged | +5 days from tasks | architect (PR owner) | 📋 Pending |

---

## Risks & Dependencies

### Technical Risks

**Risk R1: `crosswalk.yaml` citation authoring rate below projection**
- **Likelihood**: Medium (baked partially into scope via R3 Tier 1 default)
- **Impact**: Medium (timeline slip to 6-7 days if further descope required)
- **Description**: Each edge requires a retrievable URL or internal file path justifying the edge. URL-source authoring is slower than ID-list authoring. At ≥500 primary edges × 30-60 seconds/edge = 4-8 hours of citation discovery, which fits comfortably within the Day 2-3 budget. **Risk R1 materializes** if the actual per-edge rate is significantly above the 60s upper bound (e.g., unfamiliar frameworks, ambiguous edges requiring cross-reference research).
- **Mitigation — Day 1 spike with numeric tripwire (per Team-Lead H1)**:
  - **Spike scope**: web-researcher authors 50 crosswalk edges on a **diverse slice** (10 OWASP↔CWE + 10 ATT&CK↔CWE + 10 ATT&CK↔ATLAS + 10 LLM↔NIST + 10 Agentic↔MITRE) to avoid homogeneous-slice underestimation
  - **Tripwire formula**: Projected rate = `(50 edges) / measured_seconds`. Projected hours to 500 edges = `(500 × measured_seconds) / (50 × 3600)`
  - **Threshold 1** (Tier 1 stays adequate): measured ≤38.4s/edge → continue with R3 Tier 1 default (≥500 primary edges achievable by Day 3)
  - **Threshold 2** (escalate to Tier 2 or Tier 3): measured >38.4s/edge → invoke R3 Tier 2 at end of Day 2 OR R3 Tier 3 at end of Day 3 (architect + team-lead re-sign for Tier 3)
- Allow `citation` to point to an internal repo file (existing `detection-patterns.md` reference) when the edge is supported by an existing tachi agent citation — reuses work rather than re-sourcing externally

**Risk R2: Framework revision publishes mid-flight**
- **Likelihood**: Low
- **Impact**: Low-Medium (spec-phase amendment required; YAML re-authored against newer list)
- **Description**: OWASP LLM Top 10 v2027 or CWE Top 25 2025 or a new MITRE ATLAS wave publishes between PRD approval and PR merge. YAMLs must be authored against a specific snapshot.
- **Mitigation**:
  - README documents the revision version per framework (e.g., "`owasp.yaml` LLM section: authored against OWASP LLM Top 10:2025, retrieved YYYY-MM-DD")
  - If a revision publishes mid-flight: spec-phase amendment decision — either re-author against the newer list (if it's early in implementation) or document the version in README and defer the revision update to a follow-on Issue (if late)

**Risk R3: Further scope-reduction on crosswalk.yaml edge count (Tier 1 already adopted as default scope)**
- **Likelihood**: Low-Medium (Tier 1 is the scope; further descopes only trigger if Day 1 spike tripwire fires)
- **Impact**: Low (Tier 2 is team-lead-authorizable without PRD amendment; Tier 3 requires PRD amendment + architect/team-lead re-sign)
- **Description**: F-A1 has already baked in Risk R3 Tier 1 as the default scope — `primary`-only edges at a ≥500 floor. The fallback ranking covers further descope tiers if the Day 1 spike tripwire indicates the Tier 1 floor is itself unachievable.
- **Mitigation — pre-authorized fallback tiers**:
  1. **Tier 1 (already default F-A1 scope)**: `primary`-only edges at ≥500 floor. No amendment required. `related` + `superseded` expansion is a follow-on Issue filed on F-A1 PR merge.
  2. **Tier 2 (team-lead authorizable, no PRD amendment)**: reduce floor from 500 to 300 primary edges. Team-lead records the descope rationale in tasks.md; no architect re-sign required because this does not change schema contracts or ADR decisions. Triggered if Day 2 end crosswalk count is <40% of the 500 floor (<200 edges).
  3. **Tier 3 (last resort — PRD amendment)**: reduce floor from 300 to 150 primary edges OR defer crosswalk.yaml entirely to a follow-on PRD (keeping `crosswalk.yaml` as an empty-list placeholder per FR-3). Requires architect + team-lead re-sign on amended PRD. Triggered if Day 3 end crosswalk count is <100 edges.

**Clarification on FR-3 floor alignment** (per Team-Lead H1): the original 1,000-2,000 edge range in an earlier PRD draft has been **replaced** by the Tier 1 ≥500 floor as the Success Metric 2 and FR-3 canonical target. The 1,000+ aspiration is a **follow-on Issue target**, not an F-A1 commitment. This removes the internal contradiction flagged by the team-lead review.

**Risk R4: nist-ai-rmf-mapping.md contains a latent error**
- **Likelihood**: Low
- **Impact**: Low (authorship workflow correctly isolates this)
- **Description**: During FR-6 verbatim transcription, the implementing agent finds a row in Surface B or C that is factually incorrect against NIST AI RMF 1.0 or AI 600-1.
- **Mitigation**: FR-6 explicitly states corrections are filed as separate ADR-025 amendment Issues, not made silently in F-A1. The transcription is verbatim by contract; correction is a separate review cycle.

**Risk R6: Single-agent execution extends wall-clock to 5-6 days**
- **Likelihood**: Low-Medium (depends on agent availability at implementation time)
- **Impact**: Low (timeline extends; quality preserved)
- **Description**: The 4-5 day timeline assumes 3-agent parallel execution (senior-backend-engineer + web-researcher + architect). If only one agent is available to own all phases sequentially, wall-clock extends to 5-6 days as serialized YAML authoring + citation discovery + ADR authorship + testing.
- **Mitigation**: tasks.md explicitly declares the 3-agent wave structure per Phase Breakdown. If single-agent execution is unavoidable, team-lead signs off on a 5-6 day budget at tasks.md time (not a PRD amendment — this is an execution-shape adjustment within the same scope).

### Business Risks

**Risk R5: Crosswalk curation quality is judged insufficient**
- **Likelihood**: Low-Medium (depends on reviewer expertise)
- **Impact**: Medium (re-work on edge `confidence` assignments; possible PR cycle extension)
- **Description**: An external reviewer (or PM/architect at review time) judges that crosswalk edges lack citation rigor, or `confidence` values are inconsistently assigned.
- **Mitigation**:
  - README documents the curation methodology explicitly (FR-8) so reviewers have a yardstick
  - First-pass edges get `confidence: medium` as a conservative default unless the curator has strong evidence for `high` (explicit framework cross-reference) or `low` (inference across two+ hops)
  - `citation` requirement per edge prevents free-text fabrication at the record level

### Dependencies

**Internal Dependencies**:
- **[.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md)** (owner: architect, status: Delivered via PRD 144 / ADR-025, required for: FR-6 NIST YAML transcription) — confirmed stable at PRD creation time (2026-04-17)
- **11 threat-detection agents' `detection-patterns.md` references** (owner: detection-tier refactor under PRD 082, status: Delivered, required for: FR-4 seed harvest) — the 38 / 7 / 41 citation counts are a pinned baseline at F-A1 time

**External Dependencies** (all already published; no blocking external dependency at merge time):
- OWASP, MITRE, CWE public lists (see Constraints: External Dependencies)

**Dependency Graph**:
```
F-A1 (this PRD)
  ├─ Depends on: PRD 144 / ADR-025 (NIST AI RMF mapping) — Delivered
  ├─ Depends on: PRD 082 (threat-agent detection-patterns seed) — Delivered
  └─ Blocks: F-A2 (source_attribution schema extension)
           → Blocks: F-B (coverage attestation report section)
                  → Blocks: multiple downstream gap-closure features
```

---

## Open Questions

### Resolved at PRD Time (architect review 2026-04-17)

- [x] **Q1** — NIST record shape. **Resolved: Architect-recommended Interpretation C (hybrid)** — `nist-ai-rmf.yaml` carries the per-Subcategory catalog in FR-2 uniform shape; Surface B / Surface C mapping rows move to `crosswalk.yaml` edges; two new pseudo-taxonomy YAMLs (`tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`) preserve referential integrity. FR-1 grows from 7 files to 9. See FR-1, FR-2, FR-3, FR-6, FR-10 for encoded resolution.
- [x] **Q2** — Test harness location. **Resolved: `tests/schemas/test_taxonomy_integrity.py`** (new subdirectory) — preserves semantic boundary between Python script tests in `tests/scripts/` and YAML data tests in `tests/schemas/`. Requires new `tests/schemas/__init__.py` bootstrap. See FR-7.
- [x] **Q3** — `cwe_refs` direction. **Resolved: Unidirectional OWASP→CWE only**; omit the field from `cwe.yaml` records entirely (CWE→CWE relations belong in `crosswalk.yaml`). See FR-2.
- [x] **Q4** — `confidence` location. **Resolved: Per-edge only** (in `crosswalk.yaml`); three-level calibration rubric (`high` / `medium` / `low`) with anti-drift rule documented in `schemas/taxonomy/README.md` per FR-8.
- [x] **Q5** — ADR timing. **Resolved: ADR-during-implementation with Phase 1 pre-commit gate** — ADR drafted to **Proposed** status at end of Day 1 (after schema freeze and OWASP authoring); **Accepted** at PR merge per FR-10. Spec-phase authorship must verify ADR-004 lineage absence (see FR-10 note) before assuming ADR-027.

### Remaining Open Questions (all deferred to spec/plan phase — none block PRD approval)
- [ ] **Q6** *(new, from Team-Lead recommendations)* — Exact Day 1 spike 50-edge composition. PRD recommends 10 each across 5 diverse source-taxonomy pairs; spec phase may adjust if initial authoring reveals a more representative mix — Owner: team-lead — Due: spec phase — Status: Open
- [ ] **Q7** *(new)* — Whether `pyyaml` is formally declared in `requirements-dev.txt` or only present transitively via the pytest ecosystem — if transitive, FR-7 test may need an explicit dependency declaration — Owner: senior-backend-engineer — Due: spec phase — Status: Open

### Design Questions
- (none at PRD time — this is a data-authoring feature with no UX surface)

---

## References

### Product Documentation
- [Product Vision](../01_Product_Vision/product-vision.md)
- [PRD INDEX](./INDEX.md)

### Parent Discovery & Upstream PRDs
- **GitHub Issue #180**: [F-A1 — Taxonomy Crosswalk Collection [Foundation]](https://github.com/davidmatousek/tachi/issues/180)
- **PRD 144**: [NIST AI RMF Evaluation ADR](./144-nist-ai-rmf-evaluation-adr-2026-04-15.md) — source of `nist-ai-rmf-mapping.md` Surface B + Surface C tables (FR-6 source)
- **PRD 082**: [Threat Agent Skill References](./082-threat-agent-skill-references-2026-04-11.md) — source of agent `detection-patterns.md` references (FR-4 seed harvest)
- **PRD 143**: [OWASP AIVSS Evaluation ADR](./143-maestro-aivss-evaluation-adr-2026-04-14.md) — precedent for peer-framework reference without runtime wiring (FR-10 ADR cross-reference)

### Architecture Documentation
- [ADR-020: MAESTRO Layer Classification](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — shared-reference-as-single-source-of-truth pattern F-A1 inherits
- [ADR-021: SOURCE_DATE_EPOCH Determinism](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-determinism.md) — FR-9 backward-compat invariant convention
- [ADR-024: OWASP AIVSS Evaluation](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md) — peer-framework-reference-without-runtime-wiring precedent
- [ADR-025: NIST AI RMF Evaluation](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) — FR-6 source-of-truth reference

### Data Sources (External)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP Top 10:2021](https://owasp.org/Top10/)
- [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP Mobile Top 10:2024](https://owasp.org/www-project-mobile-top-10/)
- [OWASP Machine Learning Security Top 10:2023](https://owasp.org/www-project-machine-learning-security-top-10/)
- [MITRE ATT&CK Enterprise](https://attack.mitre.org/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [CWE Top 25 (2024)](https://cwe.mitre.org/top25/)

### Data Sources (Internal — Seeds)
- [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) — FR-6 verbatim source
- [.claude/skills/tachi-*/references/detection-patterns.md](../../.claude/skills/) (11 files across the threat-detection agents) — FR-4 seed source

---

## Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [ ] Problem statement is clear and user-focused (three concrete gaps: reference, completeness, curation)
- [ ] User stories have measurable acceptance criteria (3 stories; each with AC tied to YAML record counts and structural properties)
- [ ] Success metrics are defined and measurable (6 metrics; each with baseline, target, timeline, owner)
- [ ] Scope is realistic for timeline (4-5 days with 3-agent parallel execution; R3 Tier 1 ≥500-edge default already adopted; Tier 2/Tier 3 pre-authorized further descope fallbacks)
- [ ] Risks and dependencies identified (5 risks; pre-authorized scope-reduction ranking for R3)
- [ ] Aligns with product vision (default-toolkit promise; machine-readable taxonomy enables downstream integrations)

**Architect**:
- [ ] Technical requirements are clear (per-item record shape, per-edge record shape, enum domains specified in FR-2 / FR-3)
- [ ] Non-functional requirements are realistic (parse performance, memory footprint, determinism, zero-new-deps, doc discoverability)
- [ ] Dependencies are accurate (PRD 144 and PRD 082 confirmed Delivered; external framework URLs listed)
- [ ] Technical risks are identified (crosswalk authoring rate, framework revision mid-flight, NIST mapping latent error)
- [ ] Architecture approach is sound (FR-9 additive-only invariant; FR-10 public ADR)

**Engineering Lead** (team-lead):
- [ ] Requirements are implementable (data authoring over a specified record shape; no runtime pipeline changes)
- [ ] Effort estimates are reasonable (4-5 days with 5-phase breakdown; Day 5 buffer for crosswalk authoring completion / ADR review cycle; R6 captures single-agent execution extending to 5-6 days)
- [ ] Team capacity is available (single critical path: data-authoring agent; no parallel-agent coordination required)
- [ ] Timeline is realistic (Day 1 spike de-risks crosswalk authoring rate; Risk R3 fallback is pre-authorized)

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | 🟡 APPROVED_WITH_CONCERNS | 2026-04-17 | 0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. H-PM-1 addressed inline (Metric 7 outcome-measurable added). Scope defensible. Ready for /aod.plan. |
| Architect | architect | 🟡 APPROVED_WITH_CONCERNS | 2026-04-17 | v1.0 CHANGES_REQUESTED (B1 + 4 HIGH) all resolved in v1.1. Interpretation C adopted (9 files). FR-7 4-test structure. ADR-027 corrected. v1.2 cleaned up 5 residual LOW items. |
| Engineering Lead | team-lead | 🟡 APPROVED_WITH_CONCERNS | 2026-04-17 | Timeline tightened 3→4d. R3 Tier 1-3 pre-authorized. Day 1 spike at 38.4s/edge tripwire. 3-agent parallel plan encoded. R6 single-agent risk added. |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-17 | product-manager | Initial PRD authored from Issue #180 + PRD 144/082/143 precedent |
| 1.1 | 2026-04-17 | product-manager | Addressed architect CHANGES_REQUESTED (B1 ADR-026→ADR-027 correction; H1 Interpretation C adopted — 9 files, 2 new pseudo-taxonomy YAMLs, 7-value taxonomy enum; H2 FR-7 expanded to 4 test functions covering full enum closures + per-item shape + citation shape; H3 `tests/schemas/` subdirectory locked; H4 crosswalk floor reduced to ≥500 primary edges as Tier 1 default). Addressed team-lead APPROVED_WITH_CONCERNS (H1 timeline floor tightened 3→4 days; H2 Phase 3 compression relieved by distributing NIST + crosswalk + README across Days 2-3; R3 Tier 1-Tier 3 pre-authorization clarified; numeric tripwire on Day 1 spike at 38.4s/edge threshold; 3-agent parallel execution encoded in phase breakdown with named `subagent_type` values; R6 single-agent execution risk added). Q1-Q5 resolved; Q6-Q7 deferred to spec. |
| 1.2 | 2026-04-17 | product-manager | Post-review cleanup after Architect v1.1 APPROVED_WITH_CONCERNS + PM APPROVED_WITH_CONCERNS: fixed 5 LOW residual stale references (Roadmap Fit "7 files" → "9 files"; US-180-2 AC-4 "1,000-2,000 range" → "≥500 primary edges"; US-180-3 AC-2 "5 frameworks" → "7 catalog sections"; Assumption A4 rewritten for Tier 1 alignment; Technical Constraints "6 YAML files" → "8 YAML files"; Timeline drift corrected in Constraints / PRD Review Checklist lines 600/613; Executive Summary tightened to 4-5 days). Addressed PM H-PM-1 inline: new Metric 7 (Adopter Resolution Path — outcome-measurable) added with runnable Python snippet requirement in README §Purpose/§Usage per FR-8. Triad sign-offs frozen at APPROVED_WITH_CONCERNS × 3; PRD status advances Draft → Approved. Ready for /aod.plan. |
