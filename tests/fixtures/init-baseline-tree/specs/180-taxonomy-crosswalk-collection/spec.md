---
prd_reference: docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "Product-sound and ready for /aod.plan Architect review. PRD traceability strong — all PRD FRs map to spec FR-001–041, all 3 PRD User Stories preserved verbatim in priority P1/P1/P2, all PRD Success Criteria preserved in SC-001–013 with tightened predicates. Metric 7 / H-PM-1 preserved in SC-007 + FR-033/FR-034. 9-file structure, 7-value taxonomy enum, 500-edge floor, FR-022 transcription contract intact. Spec-phase refinements (AML.T0058–T0062 recategorization, CWE Top 25 2025, NIST edge count tightening) are spec-grade corrections, not scope changes. US-180-4 (integrity test) and US-180-5 (ADR) are justified story-elevations of PRD FR-7 and FR-10. 3 non-blocking concerns addressed inline: H-PM-2 deferred-to-spec callout added to FR-033 ('What F-A1 does NOT give you today' README subsection); AML.T0059–T0062 curation tripwire added to FR-016 (Day 2 escalation to architect; authorizable descope to ≥8 with AML.T0058 only; <8 requires PRD amendment); SC-013 parse perf clarified (informational bound, no CI, manual time check recorded in tasks.md). No BLOCKING issues. No PRD scope change."
  pm_signoff_amendment_1:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED
    scope: "FR-021 count amendment 68→72 (and dependent SC-002, US1 AS-4 updates)"
    notes: "APPROVED path (a) under FR-024 primary-source-correction discipline. Day 2 harvest of the authoritative NIST AI RMF 1.0 Subcategory catalog from airc.nist.gov GOVERN/MAP/MEASURE/MANAGE Playbook pages (fetched 2026-04-17) surfaced 72 Subcategories (GOVERN 19 + MAP 18 + MEASURE 22 + MANAGE 13) — not the 68 historically cited in the PRD era. The count is a spec-integrity predicate, NOT a user-value capability; no adopter integration story reads 'exactly 68.' Amendment honors PRD FR-5 intent ('the full published catalog') and the feature's FR-006/FR-022/FR-024 verbatim-transcription posture. Architect (see .aod/results/architect.md) concurred on path (a). Existing FR-022 Surface B/C transcribed IDs (MAP 4.2, MEASURE 2.6–2.10, MANAGE 1.3, MANAGE 2.4, GOVERN 1.4) are within the 68-subset ⊂ 72-superset — zero edits required to ADR-025, nist-ai-rmf-mapping.md, or the 38 already-committed batch-5 nist-rmf crosswalk edges (commit 004cd00). ADR-027 (currently Proposed) will record the amendment in its Context section when moving to Accepted at PR merge. Unblocks T022 for Day 3 Wave 3.1."
    decision_artifacts:
      - /Users/david/Projects/tachi/.aod/results/product-manager.md
      - /Users/david/Projects/tachi/.aod/results/architect.md
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
  # Opened 2026-04-17 T027 — Surface C Option (c) scope-narrow amendment; PM concurrence required on FR-022 / SC-008 narrowing + F-A1.1 follow-on acceptance. Architect decision artifact at .aod/results/architect.md.
  pm_signoff_amendment_2:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED
    scope: "Surface C Option (c) scope-narrow: FR-022 41→27 edges (Surface B only), SC-008 Surface C deferred, FR-004 example canonical-format fix, FR-032 sort clarification, F-A1.1 follow-on acceptance"
    notes: "APPROVED Option (c) — Surface C GAI Risk → STRIDE+AI transcription deferred to F-A1.1 follow-on Issue. PM traceability re-verified: no PRD FR broken. PRD FR-1 (9 files) intact; PRD FR-5 catalog at 72 records intact; PRD FR-6 direction ('Each Surface C row becomes an edge from tachi-stride-ai-category to nist-ai-rmf') was structurally ill-specified at PRD time — conflated Surface C target taxonomy (NIST AI 600-1 §2.X GAI Risks) with Surface B target taxonomy (AI RMF Subcategories). Architect's first-principles check at implementation time surfaced the mismatch; Option (c) defers to F-A1.1 with an 8th enum value rather than accommodating textually-wrong edges that would fail FR-030 referential integrity. PRD Success Metric 2 (≥500 primary edges) intact pending Day 4 architect-pre-authorized +31 edge top-up. User-value assessment: Surface B (control → AI RMF Subcategory) 27-edge compliance path delivered; Surface C (STRIDE+AI → GAI Risk) 15-edge threat-taxonomy audit path deferred ~1 day. Net user-value gain vs. pre-F-A1 state (where Surface C had zero pathway anywhere). F-A1.1 scope (0.5-1 day, schema-minor additive release) structurally parallel to the pm_signoff_amendment_1 FR-021 68→72 precedent. 3 non-blocking concerns recorded: C1 Tier 2 fallback (300-edge floor) is team-lead-authorizable per Risk R3 without PM re-gate; C2 team-lead T034 F-A1.1 Issue MUST cite this signoff + architect T027 analysis for decision-trail integrity; C3 README 'What F-A1 does NOT give you today' subsection should gain Surface C line at T028/T031. Applied First Principles lens per governance.md. Minor amendments (FR-004 space-format, FR-032 numeric-within-function NIST sort, FR-022 14→15 dead-letter count correction) all approved. Team-lead re-sign NOT required (scope narrows, no new timeline/resource risk beyond pre-authorized top-up). Unblocks Wave 4.1 Day 4: web-researcher top-up + T028-T035."
    decision_artifacts:
      - /Users/david/Projects/tachi/.aod/results/product-manager.md
      - /Users/david/Projects/tachi/.aod/results/architect.md
---

# Feature Specification: F-A1 Taxonomy Crosswalk Collection

**Feature Branch**: `180-taxonomy-crosswalk-collection`
**Created**: 2026-04-17
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
**Input**: User description: "PRD: 180 - F-A1 Taxonomy Crosswalk Collection"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Machine-Readable Taxonomy Records (Priority: P1)

An adopter integrates tachi output into a downstream system (vulnerability manager, SIEM, compliance report) that consumes taxonomy IDs. They need to resolve every OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE ID tachi cites to a stable machine-readable record — containing canonical ID, display name, source URL, and cross-framework references — so they can programmatically link tachi output to any compliance framework that maps to these taxonomies without re-deriving the mapping by hand.

**Why this priority**: Without machine-readable taxonomy records, every downstream integration is text-parsing agent markdown prose. This blocks F-A2 (finding-level source attribution) and F-B (coverage attestation report section); neither can ship until taxonomy IDs are data-shaped. P1.

**Independent Test**: A developer opens a fresh Python 3.11 shell with only `pyyaml` installed, runs `yaml.safe_load(open('schemas/taxonomy/owasp.yaml'))`, iterates the result to find `LLM05`, and confirms the `full_id`, `name`, `url`, and `cwe_refs` fields resolve without consulting any other file — delivering complete value without F-A2 or F-B needing to ship.

**Acceptance Scenarios**:

1. **Given** `schemas/taxonomy/owasp.yaml` exists, **when** I call `yaml.safe_load` on it, **then** I receive a list of ≥60 records spanning OWASP LLM Top 10:2025 (LLM01–LLM10), OWASP Top 10 for Agentic Applications:2026 (ASI01–ASI10), OWASP Top 10:2021 (A01–A10), OWASP API Security Top 10:2023 (API1–API10), OWASP Mobile Top 10:2024 (M1–M10), and OWASP Machine Learning Security Top 10:2023 (ML01–ML10), each with exactly the fields `{id, full_id, name, url, cwe_refs}`.
2. **Given** `schemas/taxonomy/mitre-attack.yaml` exists, **when** I enumerate its records, **then** I receive a list of ≥38 techniques whose `id` values include the 38 MITRE ATT&CK technique IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` references (full frozen list in Assumption A1).
3. **Given** `schemas/taxonomy/mitre-atlas.yaml` exists, **when** I enumerate its records, **then** I find ≥12 ATLAS techniques whose `id` values include BOTH the 7 seed IDs (AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057) AND the 5 externally-curated October 2025 agent technique IDs (AML.T0058, AML.T0059, AML.T0060, AML.T0061, AML.T0062).
4. **Given** `schemas/taxonomy/nist-ai-rmf.yaml` exists, **when** I count records, **then** I find exactly 72 NIST AI RMF 1.0 Subcategory records (GOVERN 19 + MAP 18 + MEASURE 22 + MANAGE 13 = 72, the full published NIST AI RMF 1.0 Subcategory catalog as of 2026-04-17 per FR-021) each with `{id, full_id, name, url, cwe_refs}` fields.
5. **Given** `schemas/taxonomy/cwe.yaml` exists, **when** I count records, **then** I find ≥53 records covering the 41-CWE seed PLUS the 12 net-new additions from CWE Top 25 (2025), with the `cwe_refs` field **omitted** from every record.
6. **Given** `schemas/taxonomy/tachi-control-category.yaml` exists, **when** I count records, **then** I find exactly 8 records matching the canonical slugs `authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`.
7. **Given** `schemas/taxonomy/tachi-stride-ai-category.yaml` exists, **when** I count records, **then** I find exactly 11 records matching the canonical slugs for 6 STRIDE categories + 5 AI categories (seeded from `stride-categories-shared.md`).

---

### User Story 2 - Single Authoritative Crosswalk (Priority: P1)

A tachi maintainer (or future downstream-feature author) needs to know how a single threat concept (e.g., "improper output handling") maps across multiple taxonomies. They find all cross-framework edges in one canonical crosswalk file with a closed `edge_type` enum and per-edge citation — so they can update mapping data in one place and have downstream features consume consistent edges without duplicating mapping logic.

**Why this priority**: Without the crosswalk, every downstream feature that spans two frameworks re-derives the mapping. A single curated crosswalk is the ROI-pivot of F-A1. P1.

**Independent Test**: Load `crosswalk.yaml`, filter to edges where `source.taxonomy == 'owasp' && source.id == 'LLM05'`, and retrieve a non-empty list of target taxonomy IDs with citations — validating that the maintainer can answer "what does LLM05 map to?" from a single file.

**Acceptance Scenarios**:

1. **Given** `schemas/taxonomy/crosswalk.yaml` exists, **when** I `yaml.safe_load` it, **then** I receive a list of edges where each edge carries the exact shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`.
2. **Given** any edge in the crosswalk, **when** I check `edge_type`, **then** it is exactly one of `{primary, related, superseded}`.
3. **Given** any edge, **when** I check `confidence`, **then** it is exactly one of `{high, medium, low}`.
4. **Given** any edge, **when** I check `source.taxonomy` and `target.taxonomy`, **then** each is exactly one of the closed 7-value enum `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category}`.
5. **Given** any edge, **when** I look up `source.id` in the catalog YAML named by `source.taxonomy`, **then** it resolves to a record present in that file (identical check applies to `target.id`).
6. **Given** the full crosswalk, **when** I filter to `edge_type == 'primary'` and count, **then** the total is **≥500** primary edges.
7. **Given** any edge, **when** I examine `citation`, **then** it is a non-empty string that is either URL-shaped (matches URL regex) or resolves to an existing file path relative to the repo root.
8. **Given** the Surface B and Surface C tables in `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`, **when** I grep for every Surface B real-mapping row (27 total) and every Surface C Overlap row (14 total), **then** each row appears as exactly one edge in `crosswalk.yaml` with matching `source.id` / `target.id` / `edge_type` fields (verbatim transcription per FR-022). Surface rows labeled "No equivalent" are **omitted** from the crosswalk.

---

### User Story 3 - Documented Curation Methodology (Priority: P2)

A reviewer (open-source contributor, adopter's security team, external auditor) validates tachi's taxonomy coverage claims, or a future tachi maintainer prepares for an OWASP/MITRE/NIST/CWE framework revision. They find a documented harvest + curate methodology, per-framework provenance log, and update procedure shipped alongside the data — so they can audit the data's lineage and execute future taxonomy refreshes with a reproducible process rather than an ad-hoc harvest.

**Why this priority**: The README is authorship documentation, not primary consumer data. P2 (supporting; discovery and auditability, not core integration value).

**Independent Test**: Open `schemas/taxonomy/README.md` alone (without opening any YAML); confirm that a reader can (a) understand the directory's purpose, (b) find the per-framework provenance, (c) find the confidence calibration rubric, (d) find the update procedure for each framework — delivering the audit path even if the YAMLs themselves are not open in a second tab.

**Acceptance Scenarios**:

1. **Given** `schemas/taxonomy/README.md` exists, **when** I read its §Purpose, **then** it documents why `schemas/taxonomy/` exists and what downstream features consume it (F-A2, F-B, ecosystem integrations), AND contains a runnable Python snippet demonstrating the resolution pattern for all 7 catalog YAMLs (per Success Metric 7 / PM H-PM-1).
2. **Given** the README, **when** I look for per-framework provenance, **then** I find 7 catalog sections (5 external frameworks + 2 tachi pseudo-taxonomies) each documenting (a) seed source + count, (b) external-curation source, (c) what was added beyond the seed.
3. **Given** the README, **when** I look for the `confidence` calibration rubric, **then** I find a three-level rubric (`high` = published cross-reference; `medium` = inferred one-hop; `low` = two-hop / thematic) with an **anti-drift rule** stating the curator must downgrade if they cannot articulate a one-sentence citation supporting `high` or `medium`.
4. **Given** the README, **when** I look for canonical-URL conventions, **then** I find per-framework URL patterns (e.g., ATT&CK `https://attack.mitre.org/techniques/T<N>/`, ATLAS `https://atlas.mitre.org/techniques/AML.T<NNNN>`, CWE `https://cwe.mitre.org/data/definitions/<N>.html`, NIST DOI-based URLs, OWASP list URLs).
5. **Given** the README, **when** I look for update procedures, **then** I find 5 per-framework sections each documenting the procedure for the next framework revision (e.g., "When OWASP LLM Top 10 v2027 publishes …").
6. **Given** the README records current-state citation counts, **when** I cross-check against the 11 agent detection-pattern references, **then** the counts (38 ATT&CK / 7 ATLAS seed / 41 CWE) match the documented baseline as of 2026-04-17.

---

### User Story 4 - Referential Integrity Test Suite (Priority: P1)

A code reviewer (or CI system) needs to confirm that F-A1 data is internally consistent — every crosswalk edge resolves to existing records, every enum value is in the closed domain, every citation is non-empty, every catalog record carries required fields — before merging the PR.

**Why this priority**: Without a mechanical integrity check, drift creeps in silently as the data grows. CI enforcement is the only durable mechanism. P1.

**Independent Test**: Run `pytest tests/schemas/test_taxonomy_integrity.py` on a freshly-cloned repo; all tests pass green without any additional setup beyond existing `requirements-dev.txt` dependencies.

**Acceptance Scenarios**:

1. **Given** a fresh clone with `pip install -r requirements-dev.txt`, **when** I run `pytest tests/schemas/test_taxonomy_integrity.py`, **then** all tests pass.
2. **Given** the test suite, **when** I enumerate test functions, **then** I find at least 4 test functions: `test_framework_yamls_load`, `test_crosswalk_loads`, `test_crosswalk_referential_integrity`, `test_citation_shape`.
3. **Given** any framework YAML, **when** the integrity test runs, **then** every record has the FR-003 required fields `{id, full_id, name, url}` (+ `cwe_refs` on `owasp.yaml`, omitted on `cwe.yaml`), every `id` is unique within its file, and every `url` either matches a URL-regex or resolves to an existing repo file.
4. **Given** the crosswalk, **when** the referential-integrity test runs, **then** every `source.id` resolves to a record in the file named by `source.taxonomy`, every `target.id` resolves similarly, and every enum field is in its closed domain (7-value taxonomy, 3-value edge_type, 3-value confidence).
5. **Given** any citation, **when** the citation-shape test runs, **then** every `citation` value is non-empty AND (URL-regex match OR existing-file-path).
6. **Given** a deliberately-corrupted fixture (e.g., edge with `edge_type: invalid`), **when** the test suite runs, **then** it fails with a clear error identifying the violating record.

---

### User Story 5 - Public ADR on Merge (Priority: P2)

A future tachi contributor (or external reviewer) needs to understand **why** the `schemas/taxonomy/` schema is shaped the way it is — the per-item record shape, per-edge shape, enum domains, and why F-A1 ships as a single PRD despite aggregating 9 files. They find a public ADR committed alongside the data that records the decision and rationale — so future schema changes can cite the ADR and reason about drift against the original decision.

**Why this priority**: The ADR is governance-layer documentation. Shipping the YAMLs without the ADR would ship decision-data without decision-rationale. P2 (supporting; governance hygiene, not core consumer value).

**Independent Test**: A future contributor proposing a new `edge_type` value opens the ADR, reads the current 3-value enum rationale, and can construct a written case for/against extension without inferring the decision context from commit messages.

**Acceptance Scenarios**:

1. **Given** `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` exists at merge time, **when** I open it, **then** it has Status: **Accepted**, follows the ADR-000 template structure (Status / Date / Deciders / Context / Decision / Rationale / Related ADRs), and documents the `schemas/taxonomy/` schema decisions.
2. **Given** the ADR, **when** I look for enum documentation, **then** I find the `taxonomy` enum (7 values), `edge_type` enum (3 values), `confidence` enum (3 values) each listed with their authorized values and rationale.
3. **Given** the ADR, **when** I look for the scope-exception rationale, **then** I find a section documenting why F-A1 ships as a single PRD despite aggregating 9 files (foundation data has no natural decomposition boundary below framework-set granularity).
4. **Given** the ADR, **when** I look for related-ADR cross-references, **then** I find ADR-020 (MAESTRO classification), ADR-021 (SOURCE_DATE_EPOCH determinism — invoked by FR-034), ADR-023 (skill-references pattern), ADR-024 (OWASP AIVSS — peer-framework precedent), ADR-025 (NIST AI RMF — FR-022 source).
5. **Given** the ADR history during implementation, **when** I check the commit log, **then** I find a commit tagging Status: **Proposed** at end of Day 1 (post-schema-freeze) and a subsequent commit tagging Status: **Accepted** at PR merge.
6. **Given** the ADR-004 listing gap at PRD creation, **when** I verify at commit time, **then** I confirm ADR-004 remains absent from the on-disk listing and ADR-027 is the next unused number (no silent reclamation of ADR-004).

---

### Edge Cases

- **What happens when** a Surface B or Surface C row in `nist-ai-rmf-mapping.md` is found to be factually incorrect during FR-022 verbatim transcription? **Resolution**: Per PRD FR-6, the correction is filed as a separate ADR-025 amendment Issue, NOT silently corrected during F-A1. F-A1 is a transcription feature, not a re-authorship feature.
- **What happens when** CWE Top 25 (2025) list differs from CWE Top 25 (2024) list (**confirmed at spec time — it does**)? **Resolution**: `cwe.yaml` targets the 2025 list (per PRD Assumption A3 fallback); README `cwe.yaml` provenance section documents "authored against CWE Top 25 (2025), retrieved 2026-04-17".
- **What happens when** a new MITRE ATLAS wave (v5.4 February 2026 observed) publishes techniques beyond AML.T0058–T0062 between spec and merge? **Resolution**: F-A1 targets the 7 seed + 5 curated October-2025 agent techniques (12 total minimum); growth toward full ATLAS v5.4 catalog is a follow-on Issue per PRD FR-5 ("growth via external ATLAS matrix curation is permitted but not mandated in F-A1").
- **What happens when** OWASP LLM Top 10 v2027 publishes mid-flight? **Resolution**: Spec validates at merge time; if v2027 publishes before merge, `owasp.yaml` re-targets per PRD Risk R2 mitigation (`README` records the version, and re-authorship is a spec-phase amendment). As of 2026-04-17, v2027 is not announced — R2 LOW probability.
- **What happens when** the Day 1 crosswalk-authoring spike measures >38.4s/edge? **Resolution**: PRD Risk R3 Tier 2 fallback (300-edge floor, team-lead-authorizable) or Tier 3 (150-edge floor, PRD-amendment-required) triggers. tasks.md must record the Day 1 spike outcome in its progress log.
- **What happens when** a crosswalk edge cites an internal file path that is later removed from the repo? **Resolution**: `test_citation_shape()` catches this at CI time by asserting file-path citations resolve to existing paths. Citation rot for URL-shaped citations is out of scope (PRD Out of Scope: Citation URL link-rot monitoring).
- **What happens when** the crosswalk contains a duplicate edge (same `{source, target, edge_type}` triple)? **Resolution**: `test_crosswalk_loads()` asserts uniqueness of the 3-tuple per edge; duplicates fail the test.
- **What happens when** an edge's `source.taxonomy` is `cwe` but `target.taxonomy` is also `cwe`? **Resolution**: Permitted — CWE→CWE relations live in the crosswalk (not in a per-record `cwe_refs` field on cwe.yaml records). The edge gets `edge_type: related` or `superseded` per the relationship's nature.

## Requirements *(mandatory)*

### Functional Requirements

#### Directory + File Structure

- **FR-001**: A new directory `schemas/taxonomy/` MUST be created at the repo root containing exactly **9 files**: `owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`, `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`, `crosswalk.yaml`, `README.md`. No additional files at this level.
- **FR-002**: All filenames MUST be lowercase with kebab-case separators. Filenames MUST match exactly (no casing variants, no `.yml`-vs-`.yaml` variants; `.yaml` is canonical).

#### Per-Item Record Shape (7 catalog YAMLs)

- **FR-003**: Each record in the 7 item-catalog YAMLs (5 external framework YAMLs + 2 tachi pseudo-taxonomy YAMLs) MUST carry the shape `{id, full_id, name, url, cwe_refs}` where `cwe_refs` is a (possibly empty) list of CWE IDs — except `cwe_refs` MUST be omitted entirely from `cwe.yaml` records (CWE→CWE relations live in `crosswalk.yaml`, not as per-record cross-references).
- **FR-004**: `id` MUST be the short canonical ID per the authoritative source (e.g., `LLM05`, `T1190`, `AML.T0058`, `CWE-1426`, `MEASURE 2.7`, `prompt-injection`, `spoofing`); uniqueness of `id` within each catalog YAML MUST be enforced by the integrity test (FR-026). **Amendment 2026-04-17**: NIST example corrected from `MEASURE-2.7` (dash) to `MEASURE 2.7` (space) to match the authoritative `nist-ai-rmf.yaml` `id` convention per FR-011 (catalog is authoritative). Architect decision at T027 per `.aod/results/architect.md` §5.4.
- **FR-005**: `full_id` MUST be a human-readable long form with framework prefix (e.g., `OWASP-LLM-2025-05`, `ATT&CK-T1190`, `ATLAS-AML.T0058`, `CWE-1426`, `NIST-AI-RMF-MEASURE-2.7`, `TACHI-CONTROL-prompt-injection`, `TACHI-STRIDE-AI-spoofing`).
- **FR-006**: `name` MUST be the canonical item name from the authoritative source (verbatim from the source; no paraphrase).
- **FR-007**: `url` MUST be either a retrievable URL to the authoritative source (for external frameworks) OR an internal file path to the canonical definition (for pseudo-taxonomies, e.g., `.claude/skills/tachi-shared/references/stride-categories-shared.md`).
- **FR-008**: `cwe_refs` (where present) MUST be populated only where the source item publishes cross-references to CWE (unidirectional OWASP→CWE only; Q3 resolution). For non-OWASP catalogs where the source does not publish cross-references, `cwe_refs` MAY be an empty list `[]` but MUST NOT carry inferred references.

#### Per-Edge Record Shape (crosswalk.yaml)

- **FR-009**: Every edge in `crosswalk.yaml` MUST carry the shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`. No additional top-level keys per edge.
- **FR-010**: `source.taxonomy` and `target.taxonomy` MUST each be one of the closed **7-value** enum `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category}` (the 7 catalog YAML filename stems).
- **FR-011**: `source.id` and `target.id` MUST each resolve to a record present in the corresponding catalog YAML (no dangling references — FR-028).
- **FR-012**: `edge_type` MUST be one of the closed enum `{primary, related, superseded}`. No free-text edge descriptions.
- **FR-013**: `confidence` MUST be one of the closed enum `{high, medium, low}`. The calibration rubric MUST be documented in `README.md` (FR-031) and MUST include the **anti-drift rule**: "if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label."
- **FR-014**: `citation` MUST be a non-empty string AND MUST be either URL-shaped (matches URL-regex) OR an internal file path that resolves to an existing file relative to the repo root. Enforced by FR-029.

#### Seed Content (confirmed against detection-patterns.md at spec time)

- **FR-015**: `mitre-attack.yaml` MUST seed from the 38 unique MITRE ATT&CK techniques currently cited across the 11 threat-detection agents' `detection-patterns.md` references (full list pinned in Assumption A1). Growth via external ATT&CK matrix curation is permitted but not mandated in F-A1.
- **FR-016**: `mitre-atlas.yaml` MUST contain ≥12 records: (a) 7 seed techniques currently cited (AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057) PLUS (b) 5 externally-curated October 2025 agent techniques (AML.T0058, AML.T0059, AML.T0060, AML.T0061, AML.T0062). The PRD wording "currently cited including AML.T0058-T0062" is corrected here — these 5 ATLAS IDs are NOT in current detection-patterns.md citations and come via external curation. **Curation tripwire** (per PM MEDIUM concern): if any of AML.T0058–T0062 cannot be resolved to a stable citation URL on atlas.mitre.org by Day 2 end (plan-phase scheduling), the implementing agent MUST escalate to architect; architect may authorize a conditional descope to ≥8 records (7 seed + AML.T0058 only, since AML.T0058 has already been cited in tachi via `finding-format-shared.md:229`). A descope below ≥8 requires PRD amendment.
- **FR-017**: `cwe.yaml` MUST contain ≥53 records: 41 seed CWEs currently cited + 12 net-new CWEs from CWE Top 25 (2025). Spec targets the CWE Top 25 **2025** list (published 2025-12-11) per PRD Assumption A3 fallback. The 13-CWE overlap between seed and Top 25 is deduplicated to a single record.
- **FR-018**: `tachi-control-category.yaml` MUST contain exactly 8 records seeded from `.claude/skills/tachi-control-analysis/references/control-categories.md`: `authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`.
- **FR-019**: `tachi-stride-ai-category.yaml` MUST contain exactly 11 records seeded from `.claude/skills/tachi-shared/references/stride-categories-shared.md`: the 6 STRIDE categories (`spoofing`, `tampering`, `repudiation`, `information-disclosure`, `denial-of-service`, `elevation-of-privilege`) + the 5 AI categories (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`).

#### External Curation for Enumeration Coverage

- **FR-020**: `owasp.yaml` MUST contain ≥60 items spanning 6 OWASP lists: LLM Top 10:2025 (10 items), Agentic Top 10:2026 (10 items), Top 10:2021 (10 items), API Security Top 10:2023 (10 items), Mobile Top 10:2024 (10 items), ML Top 10:2023 (10 items) — a minimum-floor baseline of 60 items covering the full published item list from each of the 6 OWASP lists.
- **FR-021**: `nist-ai-rmf.yaml` MUST contain exactly 72 NIST AI RMF 1.0 Subcategory records — the full published NIST AI RMF 1.0 Subcategory catalog as of 2026-04-17, per airc.nist.gov GOVERN/MAP/MEASURE/MANAGE Playbook pages fetched 2026-04-17. Composition: GOVERN 19 + MAP 18 + MEASURE 22 + MANAGE 13 = 72 Subcategories. **Spec-amendment note (2026-04-17)**: Amended 68→72 under FR-024 primary-source-correction discipline after the Day 2 harvest surfaced the authoritative count differs from the PRD-era historical reference. Existing Surface B/C rows transcribed per FR-022 (cited Subcategories MAP 4.2, MEASURE 2.6–2.10, MANAGE 1.3, MANAGE 2.4, GOVERN 1.4) are within the 68-subset ⊂ 72-superset — FR-022 transcription fidelity preserved; no ADR-025 / `nist-ai-rmf-mapping.md` edits required.

#### NIST AI RMF Mapping (Interpretation C Transcription)

- **FR-022**: Every Surface B real-mapping row in `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (27 rows confirmed at spec time) MUST transcribe verbatim into `crosswalk.yaml` as an edge from `tachi-control-category` to `nist-ai-rmf`. **Amendment 2026-04-17 (Option c per architect T027 decision)**: Surface C GAI Risk → STRIDE+AI Category transcription is OUT OF SCOPE for F-A1. Implementation surfaced that Surface C row identifiers (NIST AI 600-1 §2.X GAI Risks) are structurally distinct from AI RMF Subcategories (per ADR-025 three-surface structure) and cannot be represented under the closed 7-value taxonomy enum (FR-010) nor in `nist-ai-rmf.yaml` (which holds AI RMF 1.0 Subcategories only). Surface C transcription is deferred to F-A1.1 follow-on Issue (filed by team-lead at T034), which will add `nist-ai-600-1` as the 8th taxonomy enum value, author `schemas/taxonomy/nist-ai-600-1.yaml` with 12 GAI risk records (§§2.1–2.12), and transcribe the 15 Surface C Overlap rows (row count corrected from 14 to 15 per architect re-count; see `.aod/results/architect.md` §5.2) as `tachi-stride-ai-category → nist-ai-600-1` edges. **Total NIST-derived crosswalk edges in F-A1: 27** (Surface B only; down from the original estimated 41 because Surface C is now deferred). Architect decision artifact: `.aod/results/architect.md` (T027 Surface C decision Option (c)).
- **FR-023**: Surface cell rows labeled "No equivalent" (8 rows on Surface C) MUST be OMITTED from `crosswalk.yaml`. Surface rows labeled "Gap" (2 rows on Surface C) SHOULD be omitted unless the curator can articulate a `confidence: low` case with citation (default: omit to preserve positive-only edge representation).
- **FR-024**: If the implementing agent discovers a Surface B or Surface C row is factually inaccurate during transcription, the correction MUST be filed as a separate ADR-025 amendment Issue (NOT made silently in F-A1). F-A1 is a transcription feature, not a re-authorship feature.

#### Crosswalk Edge Count

- **FR-025**: `crosswalk.yaml` MUST contain ≥**500** primary edges (`edge_type: primary`) at merge time (PRD Risk R3 Tier 1 default scope). `related` and `superseded` expansion is a follow-on Issue filed on F-A1 PR merge, not part of F-A1 scope.
- **FR-026**: Fallback tiers pre-authorized per PRD Risk R3: Tier 2 (300-edge floor, team-lead-authorizable, no PRD amendment) triggered if Day 2 end crosswalk count is <200 edges. Tier 3 (150-edge floor, PRD amendment required) triggered if Day 3 end crosswalk count is <100 edges. Triggers recorded in tasks.md.

#### Referential Integrity Test

- **FR-027**: A pytest test file MUST be authored at `tests/schemas/test_taxonomy_integrity.py`. A new test subdirectory MUST be bootstrapped with `tests/schemas/__init__.py` (empty file).
- **FR-028**: `test_framework_yamls_load()` MUST assert: each of the 7 catalog YAMLs parses via `yaml.safe_load`; every record has FR-003 required fields; every `id` is unique within its own file; every `url` matches a URL-shape regex OR (for pseudo-taxonomies) resolves to an existing file path.
- **FR-029**: `test_crosswalk_loads()` MUST assert: `crosswalk.yaml` parses; every edge has FR-009 required fields; no duplicate edges (same `{source, target, edge_type}` triple).
- **FR-030**: `test_crosswalk_referential_integrity()` MUST assert: every edge's `source.id` resolves to an `id` in the catalog YAML named by `source.taxonomy`; every `target.id` resolves similarly; every `source.taxonomy` and `target.taxonomy` is in the closed 7-value enum; every `edge_type` is in the closed 3-value enum; every `confidence` is in the closed 3-value enum.
- **FR-031**: `test_citation_shape()` MUST assert: every `citation` is non-empty; each citation is either URL-shaped (regex-only, no HTTP fetch — preserves ADR-021 determinism) OR resolves to an existing file path relative to the repo root.
- **FR-032**: An optional test `test_records_sorted()` SHOULD assert stable record ordering: alphabetical by `id` within each catalog YAML; lexicographic on `{source.taxonomy, source.id, target.taxonomy, target.id}` for crosswalk edges. A failing sort assertion fails the suite. **Amendment 2026-04-17**: `nist-ai-rmf.yaml` records are sorted **numeric-within-function** (first by `function` in alphabetical order: GOVERN, MANAGE, MAP, MEASURE; then by numeric `X.Y` parsed as a 2-tuple of ints — so `MEASURE 2.2` precedes `MEASURE 2.10`). This matches the NIST publication convention and the human-readable expectation. Other catalogs default to lexicographic sort on the `id` field. Architect decision at T027 per `.aod/results/architect.md` §5.3.

#### README Documentation

- **FR-033**: `schemas/taxonomy/README.md` MUST document: (a) §Purpose with runnable Python snippet demonstrating the resolution path for all 7 catalog YAMLs (per Success Metric 7 / PM H-PM-1) AND an explicit "What F-A1 does NOT give you today" subsection naming the downstream-feature capabilities (finding-level citation via F-A2, coverage attestation render via F-B, agent-reference migration) that F-A1 deliberately defers (per PM H-PM-2 deferred-to-spec concern); (b) §Harvest methodology; (c) §Per-framework provenance (7 sections, one per catalog YAML); (d) §`confidence` calibration rubric with anti-drift rule; (e) §Canonical-URL conventions per framework; (f) §Update procedure per external framework (5 sections); (g) §Crosswalk methodology; (h) §Single-source-of-truth cross-reference to `nist-ai-rmf-mapping.md` (per ADR-020/ADR-023 pattern — do not restate Surface B/C content inline).
- **FR-034**: The README's runnable Python snippet MUST load correctly in a fresh Python 3.11 environment with only `pyyaml` installed (no additional dependencies). The snippet must demonstrate loading and resolving a record for each of the 7 catalog YAMLs.

#### Backward Compatibility + Scope Discipline

- **FR-035**: F-A1 MUST add files only. No existing file under `schemas/` (excluding new `schemas/taxonomy/`), `scripts/`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `templates/`, or `tests/` (excluding new `tests/schemas/`) MAY be modified. Exception: 2 cross-reference links MAY be added to `README.md` (top-level) and `docs/architecture/00_Tech_Stack/README.md` per FR-038.
- **FR-036**: The 5 non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Enforcement: `tests/scripts/test_backward_compatibility.py` stays green in PR CI.
- **FR-037**: No changes to `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, or `package.json` (zero new runtime dependencies; Q7 resolved — pyyaml is already declared in `requirements-dev.txt`).

#### Documentation Cross-References

- **FR-038**: Exactly 2 cross-reference links MUST be added to existing documentation files: (a) top-level `README.md` gains a single link to `schemas/taxonomy/README.md` in the appropriate section; (b) `docs/architecture/00_Tech_Stack/README.md` gains a single link under Schemas or Conventions. Zero other documentation files are modified.

#### Public ADR on Merge

- **FR-039**: A new public ADR MUST be committed at `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` (verify ADR-027 is the next unused number at commit time; spec confirms ADR-004 remains absent from the on-disk listing and ADR-027 stands as the next unused number).
- **FR-040**: The ADR MUST use the `ADR-000-template.md` section structure (Status / Date / Deciders / Context / Decision / Rationale / Alternatives Considered / Related ADRs). Content: per-item record shape (FR-003), per-edge record shape (FR-009), 7-value taxonomy enum (FR-010), 3-value edge_type enum (FR-012), 3-value confidence enum (FR-013), Interpretation C rationale (Q1 resolution — 9 files over 7), scope-exception rationale (single PRD despite 9 files), cadence-exception rationale (foundation data without natural decomposition boundary), cross-references to ADR-020 / ADR-021 / ADR-023 / ADR-024 / ADR-025.
- **FR-041**: The ADR MUST be in Status: **Proposed** at end of Day 1 (post-schema-freeze, post-OWASP authoring). The ADR MUST move to Status: **Accepted** at PR merge. Day 1 commit tag: Proposed. Merge commit tag: Accepted.

### Key Entities *(data involved)*

- **Catalog YAML (framework or pseudo-taxonomy)**: A YAML file under `schemas/taxonomy/` representing one taxonomy. Carries a list of records each shaped `{id, full_id, name, url, cwe_refs}` (or without `cwe_refs` on `cwe.yaml`). Catalogs: `owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`, `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`.
- **Crosswalk edge**: A record in `crosswalk.yaml` representing one directed mapping between two taxonomy items. Shaped `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`. The full crosswalk is a list of ≥500 primary edges plus optional related/superseded edges.
- **Taxonomy**: A string identifier in the closed 7-value enum corresponding to the filename stem of each catalog YAML. Referenced by edges via `source.taxonomy` and `target.taxonomy`.
- **Edge type**: A string identifier in the closed 3-value enum `{primary, related, superseded}`. `primary` denotes the canonical / most-direct mapping; `related` denotes a thematic or partial mapping; `superseded` denotes a historical mapping replaced by a newer framework item.
- **Confidence**: A string identifier in the closed 3-value enum `{high, medium, low}`. Calibrated per the README rubric with anti-drift rule.
- **Citation**: A non-empty string that is either a retrievable URL or an internal repo file path. Every edge carries exactly one citation.
- **README**: `schemas/taxonomy/README.md` — human-readable curation documentation and audit trail for the directory.
- **ADR-027**: Public architectural decision record committed alongside F-A1 at `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`. Records the schema decisions and rationale.
- **Integrity test suite**: `tests/schemas/test_taxonomy_integrity.py` — pytest module asserting referential integrity, enum closure, field shape, citation validity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 9 files exist under `schemas/taxonomy/` with canonical filenames (FR-001, FR-002). Verification: `ls schemas/taxonomy/ | sort` returns exactly the 9 canonical filenames.
- **SC-002**: Record count floors met per file: `owasp.yaml` ≥60, `mitre-attack.yaml` ≥38, `mitre-atlas.yaml` ≥12 (7 seed + 5 curated AML.T0058–T0062), `nist-ai-rmf.yaml` = 72 exactly (per FR-021, amended 2026-04-17), `cwe.yaml` ≥53, `tachi-control-category.yaml` = 8 exactly, `tachi-stride-ai-category.yaml` = 11 exactly, `crosswalk.yaml` ≥500 primary edges (per PRD Risk R3 Tier 1 default).
- **SC-003**: Integrity test `tests/schemas/test_taxonomy_integrity.py` exists and passes green on a fresh clone via `pytest tests/schemas/` (FR-027 through FR-032).
- **SC-004**: Backward-compatibility invariant preserved: `tests/scripts/test_backward_compatibility.py` remains green in PR CI — the 5 non-agentic example PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` (FR-036).
- **SC-005**: Zero-surface-area runtime diff: `git diff main..HEAD -- scripts/ .claude/agents/ templates/ schemas/*.yaml` (excluding `schemas/taxonomy/`) returns empty output at PR merge (FR-035).
- **SC-006**: Public ADR-027 committed in Status: Accepted at PR merge, following the ADR-000-template.md structure and documenting per-item shape, per-edge shape, 7-value taxonomy enum, 3-value edge_type enum, 3-value confidence enum, Interpretation C rationale, scope/cadence exception rationale, and all related-ADR cross-references (FR-039, FR-040, FR-041).
- **SC-007**: Adopter resolution path is ≤1 statement per framework (per PM Metric 7 / H-PM-1): `schemas/taxonomy/README.md` §Purpose or §Usage contains a runnable Python snippet that loads correctly in a fresh Python 3.11 environment with only `pyyaml` installed and demonstrates the resolution pattern for all 7 catalog YAMLs (FR-033, FR-034).
- **SC-008**: NIST Surface B verbatim transcription complete: every Surface B real-mapping row (27) appears as exactly one crosswalk edge with matching source.id / target.id / edge_type; "No equivalent" rows are omitted (FR-022, FR-023). **Amendment 2026-04-17**: Surface C transcription is deferred to F-A1.1 follow-on Issue per FR-022 Option (c) architect decision at T027; SC-008 verification is Surface B-only for F-A1.
- **SC-009**: ATLAS seed + curation coverage complete: `mitre-atlas.yaml` contains all 7 seed IDs (AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057) AND all 5 external-curation IDs (AML.T0058, AML.T0059, AML.T0060, AML.T0061, AML.T0062).
- **SC-010**: Day 1 spike outcome recorded: tasks.md progress log contains the measured per-edge authoring time from the 50-edge diverse-slice spike AND the resulting tier decision (continue R3 Tier 1 default / escalate to Tier 2 / escalate to Tier 3) per PRD Risk R1 tripwire.
- **SC-011**: Documentation discoverability: exactly 2 cross-reference links added to top-level `README.md` and `docs/architecture/00_Tech_Stack/README.md`; zero other documentation files modified (FR-038).
- **SC-012**: Zero new runtime dependencies: `git diff main..HEAD -- pyproject.toml requirements.txt requirements-dev.txt package.json` returns empty (FR-037, confirming Q7 resolution that pyyaml is already declared).
- **SC-013**: Parse performance sanity check (informational bound, no formal CI test): each catalog YAML loads via `yaml.safe_load` in <100ms on commodity hardware; `crosswalk.yaml` at ≥500 edges loads in <500ms. Verification procedure: single-run `time python -c "import yaml; yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))"` at implementation time and record in tasks.md. Not CI-enforced (bound, not ceiling — prevents scope creep in future iterations).

## Assumptions

- **A1 (PINNED at spec time, 2026-04-17)**: The 11 threat-detection agents' `detection-patterns.md` files are the authoritative seed source for ATT&CK/ATLAS/CWE citation counts. **Counts verified at spec time**: 38 ATT&CK techniques, 7 ATLAS techniques (the 7 non-T0058-T0062 IDs), 41 CWEs. Subsequent agent-reference edits do not invalidate F-A1; the README provenance section pins these counts as the baseline. **Correction from PRD FR-4 wording**: AML.T0058–T0062 are NOT in current detection-patterns.md citations; they come via external curation under FR-016.

  Full seed IDs (frozen at spec time):
  - **ATT&CK (38)**: T1005, T1039, T1068, T1070, T1070.001, T1070.002, T1070.004, T1070.006, T1070.008, T1078, T1078.004, T1195, T1195.001, T1195.002, T1213, T1213.001, T1213.002, T1213.003, T1213.005, T1498, T1498.001, T1498.002, T1499, T1499.001, T1499.002, T1499.003, T1499.004, T1530, T1548, T1548.001, T1548.003, T1548.005, T1550, T1550.001, T1556, T1562, T1562.006, T1565
  - **ATLAS (7 seed)**: AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057
  - **CWE (41)**: CWE-20, CWE-22, CWE-77, CWE-78, CWE-89, CWE-90, CWE-117, CWE-200, CWE-209, CWE-215, CWE-223, CWE-250, CWE-266, CWE-269, CWE-285, CWE-287, CWE-290, CWE-306, CWE-345, CWE-352, CWE-384, CWE-400, CWE-407, CWE-494, CWE-502, CWE-522, CWE-532, CWE-538, CWE-613, CWE-639, CWE-770, CWE-776, CWE-778, CWE-779, CWE-862, CWE-863, CWE-917, CWE-918, CWE-943, CWE-1333, CWE-1395

- **A2 (VALIDATED at spec time)**: No ADR-025 amendment Issue is in flight. FR-022 Surface B/C verbatim transcription is stable. If an amendment lands during implementation, the spec is unaffected — the transcription uses the file state at merge-time commit.

- **A3 (UPDATED at spec time)**: CWE Top 25 **2025** (published 2025-12-11) is the current authoritative list, not 2024 as PRD drafted. Spec targets 2025 list; README provenance records "authored against CWE Top 25 (2025), retrieved 2026-04-17". If CWE Top 25 (2026) publishes before F-A1 merge (improbable within a 5-day timeline), target the newer list at merge-time and update README provenance.

- **A4 (DEFERRED to Day 1 spike)**: The ≥500 primary-edge floor is achievable given authoring rate ≤38.4s/edge. The Day 1 spike (50 edges, diverse slice composition pinned per A5) validates or invalidates this; tripwire fires R3 Tier 2 or Tier 3 escalation per PRD.

- **A5 (Q6 resolved at spec time)**: Day 1 50-edge spike composition is 10 OWASP↔CWE + 10 ATT&CK↔CWE + 10 ATT&CK↔ATLAS + 10 LLM↔NIST + 10 Agentic↔MITRE as PRD recommended. Spec reserves the right for web-researcher to adjust mid-spike if the first 5 edges reveal homogeneous-slice bias (e.g., all OWASP↔CWE edges citing the same OWASP list), but the baseline composition stands.

- **A6 (Q7 resolved at spec time)**: `pyyaml` is already declared in `requirements-dev.txt` (verified at spec time). FR-031 `test_citation_shape()` and FR-028 `test_framework_yamls_load()` use the existing pytest harness bootstrapped in Feature 128 — no new dependency declaration is required.

- **A7 (ADR numbering)**: ADR-004 is historically absent from `docs/architecture/02_ADRs/` on-disk listing at spec creation (verified at spec time; existing ADRs are 000, 001, 002, 003, 005, 006, 007, …, 026). Spec does not attempt to silently reclaim ADR-004; ADR-027 is the target number. Authorship re-verifies at commit time; if ADR-027 is taken by an unrelated in-flight feature, the next unused number is used.

- **A8 (Feature cadence)**: F-A1 ships as a single PRD despite aggregating 9 files. The cadence exception is documented in ADR-027 (FR-040) and is bounded to foundation-data features; it does not set precedent for downstream gap-closure features.

### Constraints

**Technical Constraints**:
- **Zero runtime surface-area touch** (FR-035): no modifications to `scripts/`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `templates/`, `tests/scripts/`, or existing `schemas/*.yaml`. Exception: 2 cross-reference links in top-level `README.md` + `docs/architecture/00_Tech_Stack/README.md` (FR-038).
- **Zero new runtime dependencies** (FR-037): no changes to `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `package.json`.
- **YAML parse cleanliness**: all 8 YAML files MUST parse via `yaml.safe_load` without errors (FR-028).
- **Referential integrity**: FR-030 test suite MUST pass before PR merge.

**Business Constraints**:
- **Timeline**: 4-5 working day target (PRD Timeline §), parallel 3-agent execution assumed. R6 single-agent execution extends to 5-6 days.
- **Single-PRD cadence exception**: documented in ADR-027. Does not set precedent for downstream gap-closure features.

**External Dependencies** (all published at spec time; no runtime fetch required):
- OWASP LLM Top 10:2025, OWASP Agentic Top 10:2026, OWASP Top 10:2021, OWASP API Security Top 10:2023, OWASP Mobile Top 10:2024, OWASP ML Security Top 10:2023
- MITRE ATT&CK Enterprise matrix (https://attack.mitre.org/)
- MITRE ATLAS matrix (https://atlas.mitre.org/) — includes AML.T0058–T0062
- CWE Top 25 (2025) (https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)
- NIST AI 100-1 Tables 1–4 (NIST AI RMF 1.0 Subcategory catalog)
- `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (FR-022 verbatim source — authored via PRD 144)

### Out of Scope (per PRD)

- `related` and `superseded` crosswalk edges beyond primary edges (follow-on Issue on merge)
- F-A2 schema extension (`source_attribution` field on `schemas/finding.yaml`) — separate PRD
- F-B coverage attestation report section — separate PRD
- Agent reference migration (citing `schemas/taxonomy/` from `detection-patterns.md`) — future work
- Full external-source curation beyond PRD floors — grow via downstream attestation audit features
- Multi-language taxonomy support
- Runtime pipeline integration of `schemas/taxonomy/` YAMLs
- Citation URL link-rot monitoring (documented canonical-URL conventions reduce rot probability but no periodic re-validation)
- Non-YAML formats (JSON-LD, RDF, SKOS)
- Interactive crosswalk browser (web UI)
- Automated crosswalk inference (LLM-based edge generation)

---

## Dependencies

**Internal Dependencies** (verified at spec time):
- `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` — owner: architect; status: **Delivered** via PRD 144 / ADR-025 (2026-04-16); required for FR-022 verbatim transcription
- 11 threat-detection agents' `detection-patterns.md` references — owner: detection-tier refactor under PRD 082; status: **Delivered** (2026-04-13); required for FR-015 seed harvest
- `.claude/skills/tachi-control-analysis/references/control-categories.md` — owner: control-analyzer stack; status: Delivered; required for FR-018 seed
- `.claude/skills/tachi-shared/references/stride-categories-shared.md` — owner: shared references; status: Delivered; required for FR-019 seed
- `docs/architecture/02_ADRs/ADR-000-template.md` — ADR template; required for FR-040 ADR-027 authoring
- `tests/scripts/test_backward_compatibility.py` — owner: Feature 128 pytest harness; status: Delivered; required for FR-036 byte-identity invariant enforcement in PR CI
- `pyproject.toml` + `requirements-dev.txt` — pytest harness config; required for FR-027 test bootstrap

**External Dependencies** (all already published; no blocking at merge time):
- OWASP public lists (6 separate lists; stable URLs documented above)
- MITRE ATT&CK Enterprise + MITRE ATLAS public matrices (stable; v5.4 ATLAS current as of 2026-04-17)
- CWE Top 25 (2025) — MITRE/CISA published 2025-12-11
- NIST AI 100-1 (NIST AI RMF 1.0) — NIST published 2023-01-26 (stable)

**Blocks**:
- F-A2 (source_attribution schema extension) — depends on F-A1
- F-B (coverage attestation report section) — depends on F-A2
- Multiple downstream gap-closure features — depend on F-A1

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs) — YAML is data format, not implementation
- [x] Focused on user value and business needs (3 personas: adopter, maintainer, reviewer)
- [x] Written for non-technical stakeholders (abstractions: catalog, edge, taxonomy, confidence; no Python/YAML internals)
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain — PRD's 7 Open Questions (Q1–Q7) resolved at PRD time + spec-phase research
- [x] Requirements are testable and unambiguous (41 FRs; each cites a measurable predicate)
- [x] Success criteria are measurable (13 SCs; each has verification method)
- [x] Success criteria are technology-agnostic (SC-013 parse time references commodity hardware, not a specific lib version)
- [x] All acceptance scenarios are defined (5 user stories with ≥6 scenarios each)
- [x] Edge cases are identified (8 edge cases)
- [x] Scope is clearly bounded (In Scope / Out of Scope sections per PRD)
- [x] Dependencies and assumptions identified (8 assumptions A1–A8; 7 internal + 4 external dependencies)

### Feature Readiness
- [x] All functional requirements have clear acceptance criteria (each FR traces to ≥1 user story acceptance scenario)
- [x] User scenarios cover primary flows (adopter integration, maintainer curation, reviewer audit, CI enforcement, ADR governance)
- [x] Feature meets measurable outcomes defined in Success Criteria (SC-001 through SC-013 enumerate quantitative checks)
- [x] No implementation details leak into specification (spec says "pytest" and "YAML" as data format constraints, not implementation language choices)

---

## Execution Status

- [x] User description parsed (PRD 180 Approved status, all 3 Triad sign-offs APPROVED_WITH_CONCERNS)
- [x] Key concepts extracted (9 files, per-item record shape, per-edge record shape, 7-value taxonomy enum, 3-value edge_type + confidence enums, FR-022 verbatim transcription, Day 1 spike with tripwire, R3 Tier 1-3 fallbacks, ADR-027 dual-commit)
- [x] Ambiguities resolved (Q6 Day 1 spike composition pinned to PRD-recommended 5-slice; Q7 pyyaml already in requirements-dev.txt)
- [x] User scenarios defined (5 user stories with priority ranking)
- [x] Requirements generated (41 FRs across 9 sections)
- [x] Entities identified (9 key entities: catalog YAML, edge, taxonomy, edge_type, confidence, citation, README, ADR-027, integrity test suite)
- [x] Review checklist passed
