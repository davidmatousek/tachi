# ADR-027: Taxonomy Crosswalk Schema

**Status**: Accepted
**Date**: 2026-04-17 (Proposed); 2026-04-21 (Accepted — provisional, pending PR merge)
**Accepted-commit-SHA**: `<pending-T039-post-merge-fill>`
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 180 (F-A1 Taxonomy Crosswalk Collection)
**Related ADRs**: [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (skill-references pattern), [ADR-024](ADR-024-owasp-aivss-evaluation.md) (OWASP AIVSS posture), [ADR-025](ADR-025-nist-ai-rmf-evaluation.md) (NIST AI RMF posture)

---

## Context

Tachi's agentic-AI threat-modeling pipeline cites external taxonomy identifiers across every stage of its output: OWASP list items (LLM Top 10:2025, Agentic Top 10:2026, Top 10:2021, API Security Top 10:2023, Mobile Top 10:2024, ML Security Top 10:2023), MITRE ATT&CK techniques (38 unique, drawn from the 11 threat-detection agents' `detection-patterns.md` references), MITRE ATLAS techniques (7 seed plus 5 externally-curated October 2025 agent techniques AML.T0058–T0062), NIST AI RMF 1.0 Subcategories (68 across Govern/Map/Measure/Manage Functions, per ADR-025), and CWEs (41 cited plus 12 net-new CWE Top 25 2025 additions).

At present these taxonomy IDs live as citation strings embedded in agent markdown prose (`detection-patterns.md` references, shared references, threat-report narratives, compensating-control evidence). This is sufficient for a human reader but prevents **programmatic** consumption — an adopter integrating tachi output into a downstream system (vulnerability manager, SIEM, compliance dashboard) must text-parse agent prose to resolve a single ID, and any cross-framework mapping (e.g., "what CWEs does OWASP LLM05 relate to?") must be re-derived by hand for every integration.

The PRD 180 cost/benefit analysis concluded that a **machine-readable foundation** under `schemas/taxonomy/` is a prerequisite for the downstream F-A2 (finding-level source attribution) and F-B (coverage attestation report section) features, neither of which can ship until taxonomy IDs are data-shaped. PRD 180 approved three Triad sign-offs (PM, Architect, Team-Lead — all APPROVED_WITH_CONCERNS) for delivering the following as a single feature:

1. **7 catalog YAMLs** — one file per taxonomy, each a list of records per a uniform shape
2. **1 crosswalk YAML** — a single list of directed cross-framework edges with closed enums for edge semantics and confidence
3. **1 README.md** — curation methodology, per-framework provenance, anti-drift confidence calibration rubric, canonical-URL conventions, and update procedure
4. A **referential-integrity pytest suite** — CI enforcement of enum closure, referential integrity, citation shape, and record uniqueness
5. **This ADR** — recording the schema decisions and the scope/cadence rationale

The per-file cadence question was explicit: should F-A1 ship as 9 separate features (one per YAML plus README plus tests plus ADR), or as a single feature? The **single-feature cadence exception** was approved on the rationale that foundation data has no natural decomposition boundary below framework-set granularity — splitting across 9 PRDs would duplicate scope overhead without delivering partial value, since consumers need the full set to resolve cross-framework edges.

### Constraints

- **Zero runtime surface-area touch** (PRD FR-035, spec FR-035): no modifications to `scripts/`, `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, `templates/`, or existing `schemas/*.yaml`. Only additive changes plus exactly 2 cross-reference link edits to top-level `README.md` and `docs/architecture/00_Tech_Stack/README.md`.
- **Zero new runtime dependencies** (spec FR-037): `pyyaml` is already declared in `requirements-dev.txt` (confirmed at spec time). No changes to `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, or `package.json`.
- **Byte-identity backward compatibility** (spec FR-036): the 5 non-agentic example PDFs must regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. No runtime pipeline code reads `schemas/taxonomy/` in F-A1 — enforced by the zero-runtime-touch invariant.
- **Interpretation C transcription** (spec FR-022): every Surface B real-mapping row (27) and every Surface C Overlap row (14) in `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (authored via Feature 144 / ADR-025) must transcribe verbatim into `crosswalk.yaml`. "No equivalent" and "Gap" rows are omitted by default.
- **Anti-drift confidence calibration** (spec FR-013): the three-level confidence enum must carry an explicit anti-drift rule to prevent the common failure mode of curators defaulting to `high` without published cross-reference support.
- **ADR numbering hygiene** (spec FR-039, Assumption A7): ADR-004 is historically absent from the on-disk listing (verified at spec time). ADR-027 is the next unused number and is not a silent reclamation of ADR-004.

---

## Decision

We adopt the **`schemas/taxonomy/` directory schema** as specified below. The directory contains exactly 9 files (7 catalog YAMLs + 1 crosswalk YAML + 1 README), each carrying a contract enforced by the `tests/schemas/test_taxonomy_integrity.py` pytest suite and documented in this ADR.

### Decision 1 — Per-item record shape (catalog YAMLs)

Every record in the 7 catalog YAMLs MUST carry the shape:

```yaml
- id: <short-canonical-id>           # e.g., LLM05, T1190, AML.T0058, CWE-89, MEASURE-2.7, authentication, spoofing
  full_id: <framework-prefixed-id>   # e.g., OWASP-LLM-2025-05, ATT&CK-T1190, ATLAS-AML.T0058, CWE-89, NIST-AI-RMF-MEASURE-2.7
  name: <verbatim-canonical-name>    # no paraphrase; as published by the authoritative source
  url: <retrievable-url-or-repo-path># URL for external frameworks; internal path for tachi pseudo-taxonomies
  cwe_refs: [<cwe-id>, ...]          # list of CWE IDs; OMITTED entirely on cwe.yaml records
```

**Unidirectional OWASP→CWE `cwe_refs` rule** (spec FR-008): the `cwe_refs` field is populated only where the source framework explicitly publishes cross-references to CWE. OWASP is the only external source publishing direct CWE cross-references as part of its Top 10 item definitions, so only `owasp.yaml` records carry meaningful `cwe_refs` content. The 5 non-cwe non-owasp catalogs (`mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`) MAY carry empty `cwe_refs: []` but MUST NOT carry inferred cross-references. `cwe.yaml` records OMIT the `cwe_refs` field entirely — CWE→CWE relations live in `crosswalk.yaml`, not as per-record cross-references.

Rationale for the uniform shape: downstream consumers (F-A2, F-B) can iterate any catalog YAML without per-file schema logic. A single `load_catalog(path) → list[record]` path resolves every catalog.

Rationale for omitting `cwe_refs` on `cwe.yaml`: CWE→CWE relationships (supersession, aliases, variants) are inherently many-to-many and directional. Encoding them as per-record `cwe_refs` lists duplicates the information in both directions and forces every CWE update to touch multiple records. The crosswalk representation (one edge per relationship with explicit `edge_type`) avoids the duplication.

### Decision 2 — Per-edge record shape (crosswalk.yaml)

Every edge in `crosswalk.yaml` MUST carry the shape:

```yaml
- source:
    taxonomy: <7-value-enum>   # owasp | mitre-attack | mitre-atlas | nist-ai-rmf | cwe | tachi-control-category | tachi-stride-ai-category
    id: <id-resolving-in-source-catalog>
  target:
    taxonomy: <7-value-enum>
    id: <id-resolving-in-target-catalog>
  edge_type: <3-value-enum>    # primary | related | superseded
  confidence: <3-value-enum>   # high | medium | low
  citation: <non-empty-string> # URL-shaped OR repo-relative file path
```

No additional top-level keys per edge. Same-taxonomy pairs are permitted (e.g., CWE→CWE supersession). Referential integrity is enforced by the pytest suite: every `source.id` MUST resolve to an `id` in the catalog YAML named by `source.taxonomy`; identical rule for `target.id` / `target.taxonomy`.

Rationale for the 5-field shape: each field carries a single semantic responsibility (source identity, target identity, mapping kind, curator confidence, evidence). The nested `source`/`target` structure with `{taxonomy, id}` pairs makes referential integrity check trivial (one dict lookup per side). The closed enums on `edge_type` and `confidence` make every edge programmatically queryable without free-text parsing.

### Decision 3 — 7-value `taxonomy` enum

The `taxonomy` field on both `source` and `target` is a closed enum with exactly 7 values — the filename stems of the 7 catalog YAMLs:

| Value | Catalog YAML |
|-------|--------------|
| `owasp` | `owasp.yaml` |
| `mitre-attack` | `mitre-attack.yaml` |
| `mitre-atlas` | `mitre-atlas.yaml` |
| `nist-ai-rmf` | `nist-ai-rmf.yaml` |
| `cwe` | `cwe.yaml` |
| `tachi-control-category` | `tachi-control-category.yaml` |
| `tachi-stride-ai-category` | `tachi-stride-ai-category.yaml` |

The enum is closed for F-A1. Extension (e.g., a new external framework catalog, or a new tachi pseudo-taxonomy) is governed by a future ADR amending this one; the integrity test MUST fail on any unknown value.

Rationale for filename-stem convention: a curator reading an edge's `source.taxonomy: mitre-attack` can resolve the catalog file (`schemas/taxonomy/mitre-attack.yaml`) by string concatenation with zero lookup logic. The integrity test uses the same convention (`load(f"schemas/taxonomy/{edge.source.taxonomy}.yaml")`).

Rationale for 5 external + 2 tachi-pseudo split: the 5 external frameworks are the published taxonomies that tachi output cites. The 2 tachi pseudo-taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) represent tachi's own published taxonomies — the 8 canonical control-category slugs (`authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`) and the 11 STRIDE+AI category slugs (6 STRIDE + 5 AI). Treating them as first-class taxonomy participants lets crosswalk edges map external IDs to tachi's internal categories (e.g., `owasp → tachi-stride-ai-category` edges for OWASP-to-STRIDE mappings; NIST Surface B edges as `tachi-control-category → nist-ai-rmf`).

### Decision 4 — 3-value `edge_type` enum

The `edge_type` field is a closed enum with exactly 3 values:

| Value | Semantics | F-A1 Scope |
|-------|-----------|------------|
| `primary` | Canonical / most-direct mapping — the relationship a reader would expect to find when asking "what does X map to?" | In scope (≥500 edges at F-A1 merge, per spec FR-025) |
| `related` | Thematic or partial mapping — the two items are semantically adjacent but not a canonical mapping | Out of F-A1 scope (follow-on Issue) |
| `superseded` | Historical mapping replaced by a newer framework item — e.g., a CWE deprecated in favor of another | Out of F-A1 scope (follow-on Issue) |

F-A1 ships `primary` edges only (≥500 at merge, with tiered fallbacks per spec FR-025 / FR-026: Tier 2 = 300-edge floor team-lead-authorizable, Tier 3 = 150-edge floor PRD-amendment-required). The `related` and `superseded` expansion is a documented follow-on Issue filed on F-A1 PR merge.

Rationale for the 3-value enum (vs a free-text mapping-description field): free-text descriptions force every downstream consumer to re-interpret mapping semantics. The 3-value enum makes every edge filterable (e.g., "show me all primary mappings from OWASP LLM05") without parsing prose. Reserving `related` and `superseded` as **authorized-but-out-of-scope** values (rather than removing them) lets F-A1 data validate cleanly while enabling the follow-on expansion to extend the crosswalk without schema migration.

### Decision 5 — 3-value `confidence` enum with anti-drift rule

The `confidence` field is a closed enum with exactly 3 values:

| Value | Criterion | Example |
|-------|-----------|---------|
| `high` | Published cross-reference — the authoritative source explicitly lists the target ID | OWASP LLM05 explicitly lists CWE-79, CWE-89, CWE-116 in its published cross-references |
| `medium` | Inferred one-hop — semantic match without explicit listing, citable to one authoritative document | LLM05 relates to CWE-20 via category-semantic match documented in OWASP LLM project README |
| `low` | Two-hop or thematic — curator judgment with citation to a non-authoritative document (blog, paper, internal analysis) | ATT&CK T1190 relates to OWASP API7 via adversary-objective alignment discussed in a security-research paper |

**Anti-drift rule** (spec FR-013): "if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label." This rule is documented prominently in `schemas/taxonomy/README.md` (spec FR-033 section §Confidence Calibration Rubric) and MUST be referenced in any future curation-guideline document.

Rationale for the 3-value enum and anti-drift rule: the common failure mode in curated cross-framework mappings is **confidence inflation** — curators defaulting to `high` because it feels more authoritative, without published cross-reference backing. Once the inflation enters the data, downstream consumers cannot distinguish explicit mappings from curator opinions. The anti-drift rule forces curators to articulate citation evidence before claiming `high` or `medium`; the fallback is always `low` (which is still a valid, shippable value), so the rule does not create pressure to drop edges. This is the single most important data-quality guardrail in F-A1.

### Decision 6 — Citation non-empty + resolvable

Every edge's `citation` field MUST be a non-empty string that is either URL-shaped (matches `^https?://` regex) OR a repo-relative file path that resolves to an existing file. Enforced by `test_citation_shape()` in the pytest suite.

Rationale: an edge without an evidence trail is an unattributed opinion. Forcing every edge to carry a citation (even if `low` confidence) makes the data self-auditing — a reviewer can click any citation and trace the curator's reasoning. The URL-regex vs file-path dual mode preserves ADR-021 determinism (no HTTP fetch at test time; URL-regex is a syntax check, file-path is a local-FS check). Citation URL link-rot monitoring is out of F-A1 scope (documented in spec Out of Scope) — link-rot is a follow-on Issue filed on F-A1 PR merge.

### Decision 7 — Interpretation C (single-feature cadence exception)

F-A1 ships as **a single PRD** despite aggregating 9 files (7 catalog YAMLs + crosswalk + README, plus the integrity test suite and this ADR). The per-file alternative — 9 separate features — was rejected on the rationale that:

1. **Foundation data has no natural decomposition boundary below framework-set granularity.** The crosswalk is single-file by nature (every edge lives in one list), so splitting the catalog YAMLs across 7 features would still leave the crosswalk as one feature. Downstream consumers (F-A2, F-B) need the full set to resolve cross-framework edges; partial catalog-set delivery provides no partial value.
2. **Per-file PRD overhead would exceed authoring overhead.** The PRD + plan + tasks + review cycle cost for each of 7 framework catalogs plus crosswalk plus README is estimated 3-4x the cost of authoring the data itself. The cadence exception is a practical efficiency decision.
3. **The single-PRD cadence is bounded to foundation-data features.** This decision does not set precedent for downstream gap-closure features (e.g., F-A2 finding-level source attribution is a runtime-schema extension with clear per-finding-field boundaries and ships as a separate PRD). The cadence exception applies specifically to curated-data-set features where the data does not decompose below framework-set granularity.

This rationale is labeled "Interpretation C" in PRD 180 to distinguish it from two alternatives considered at PRD time: Interpretation A (9 separate features, one per artifact) and Interpretation B (3 separate features: external frameworks + tachi pseudo-taxonomies + crosswalk). Interpretation C was selected as the PRD scope resolution.

### Decision 8 — ADR governance (Proposed → Accepted dual-commit)

This ADR is authored in **Status: Proposed** at end of Day 1 (after schema freeze and `owasp.yaml` authoring) and moves to **Status: Accepted** at PR merge. The dual-commit convention mirrors the precedent set by ADR-024 and ADR-025 (both first committed Proposed, then accepted at merge). The Day 1 Proposed commit serves as the authoritative schema-lock point that unblocks parallel authoring in Waves 1.2 and beyond; the Accepted commit at PR merge captures the final decision record.

---

## Rationale

### Reason 1 — Uniform per-item record shape enables single-path catalog resolution

Decision 1's uniform `{id, full_id, name, url, cwe_refs}` shape (with `cwe_refs` omitted on `cwe.yaml`) lets downstream consumers iterate any of the 7 catalog YAMLs with a single `load_catalog(path) → list[record]` code path. If each catalog carried a distinct shape (e.g., OWASP adds a `category` field, ATT&CK adds a `tactic` field, NIST adds a `function`/`category`/`subcategory` split), every downstream consumer would need per-framework parsing logic. The uniform shape defers framework-specific metadata to `full_id` (which encodes framework provenance) and `url` (which resolves to the canonical source page carrying full framework context).

This reduces the adopter's integration cost from "7 per-framework parsers" to "1 generic catalog parser". The Success Metric 7 runnable Python snippet (spec FR-033, FR-034) demonstrates this single-path resolution across all 7 catalogs in a single `pyyaml.safe_load` invocation per file.

### Reason 2 — Closed enums at the schema layer prevent downstream free-text parsing

Decisions 3 (taxonomy), 4 (edge_type), and 5 (confidence) all specify closed enums. Free-text alternatives for any of the three would force downstream consumers to parse and interpret mapping semantics from prose, which is both error-prone and inconsistent across consumers. Closed enums make every edge programmatically filterable, sortable, and joinable with zero interpretation logic.

The `edge_type` enum specifically authorizes two out-of-F-A1-scope values (`related`, `superseded`) so that downstream follow-on expansion can ship without a schema migration. This is the same principle used by `schemas/finding.yaml` — authorizing the full enum space at the schema-freeze point, then filling in additional values in follow-on features.

### Reason 3 — Anti-drift confidence rule mitigates the dominant data-quality failure mode

Decision 5's anti-drift rule addresses the single most common failure mode in curated cross-framework mappings: **confidence inflation**. Curators default to `high` because it feels more authoritative, without published cross-reference backing. Once inflation enters the data, downstream consumers cannot distinguish explicit mappings from curator opinions. Over time, confidence inflation erodes the value of the `confidence` field entirely — the crosswalk becomes "everything is high-confidence" and the enum loses its filter power.

The anti-drift rule ("if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label") inverts the default bias. The fallback is always `low` (still a valid, shippable value), so the rule does not create pressure to drop edges — it creates pressure to calibrate them honestly. The rule is documented prominently in the README and is enforced socially (code-review surface area) rather than mechanically (the integrity test does not attempt to validate confidence values against external sources per ADR-021 determinism).

### Reason 4 — Interpretation C cadence exception preserves foundation-data coherence

Decision 7's single-feature cadence is a practical efficiency decision bounded to foundation-data features. Splitting the data across 9 PRDs would triple the authoring overhead without delivering partial value (since downstream consumers need the full set). The cadence exception is documented in this ADR and does NOT set precedent for downstream gap-closure features — future features with clear per-artifact boundaries (e.g., F-A2 runtime schema extension, F-B report section) ship as separate PRDs.

The cadence exception is bounded by three criteria: (a) the feature produces curated reference data, (b) the data does not decompose below framework-set granularity, (c) downstream consumers need the full set. Features meeting all three criteria may invoke this precedent by citing ADR-027 in their PRD scope rationale. Features failing any criterion ship per standard PRD cadence.

### Reason 5 — Zero runtime surface-area touch preserves backward compatibility

F-A1 adds files only. No existing runtime code reads `schemas/taxonomy/` — the integrity test consumes the data in CI, but the production pipeline (orchestrator, 11 threat-detection agents, risk-scorer, control-analyzer, threat-report, infographic, report-assembler) does not load any `schemas/taxonomy/` YAML. This is enforced by the spec FR-035 zero-runtime-touch constraint and the SC-005 empty-diff verification (`git diff main..HEAD -- scripts/ .claude/agents/ templates/ schemas/*.yaml` — excluding new `schemas/taxonomy/`).

The byte-identity backward-compatibility invariant (spec FR-036 / SC-004) is thus preserved by construction: the 5 non-agentic example PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` because none of the runtime inputs change.

---

## Alternatives Considered

### Alternative 1 — Distinct per-framework record shapes

Each of the 7 catalog YAMLs carries a framework-specific record shape (e.g., OWASP records add `category`, ATT&CK records add `tactic`/`platforms`, NIST records add `function`/`category`/`subcategory`). Downstream consumers parse each catalog with per-framework logic.

**Pros**:
- Per-framework metadata (tactic, category, function) is first-class in the data
- Matches each framework's native data model more closely

**Cons**:
- Every downstream consumer needs 7 per-framework parsers
- The Success Metric 7 runnable Python snippet (FR-034) would need 7 distinct code paths
- Framework-specific fields that rarely get queried (e.g., ATT&CK `platforms`) would still pay the schema complexity cost
- Adding an 8th framework in a future ADR would require a full per-framework shape authoring pass

**Why Not Chosen**: the uniform shape's single-parser simplicity outweighs the framework-specific metadata benefit. Framework-specific metadata is available via the canonical source URL (`url` field) — downstream consumers needing ATT&CK `tactic` can fetch it from the `url` or from a separate per-framework metadata catalog in a future feature. The crosswalk edges carry the cross-framework relationships that are the primary consumer need.

### Alternative 2 — Combined per-record `relationships` field (no separate crosswalk)

Each catalog record carries an inline `relationships` list pointing to IDs in other catalogs (e.g., `owasp.yaml` LLM05 record carries `relationships: [{taxonomy: cwe, id: CWE-79, confidence: high}, ...]`). No separate `crosswalk.yaml` file.

**Pros**:
- Relationships travel with their source record
- Single-file catalog load gives both records and relationships

**Cons**:
- Bidirectional relationships must be duplicated in both records (e.g., LLM05→CWE-79 AND CWE-79→LLM05) or arbitrarily chosen as unidirectional
- Updating a relationship requires editing both catalogs (or remembering which direction is canonical)
- Filtering all edges of a single `edge_type` (e.g., "show me all `superseded` edges") requires iterating every catalog's every record
- Same-taxonomy relationships (e.g., CWE→CWE supersession) conflict with the "relationships live on source record" pattern

**Why Not Chosen**: the single `crosswalk.yaml` file makes every edge addressable in a single iteration and avoids the bidirectional-duplication problem. The `cwe_refs` field on `owasp.yaml` records is a deliberate narrow exception (Decision 1, FR-008) for the single case where an authoritative source explicitly publishes cross-references inline — all other relationships live in `crosswalk.yaml`.

### Alternative 3 — Open-ended `edge_type` free-text field

The `edge_type` field accepts any curator-provided string describing the relationship (e.g., "mitigates", "instance-of", "exploits", "supersedes", "related-by-adversary-objective").

**Pros**:
- Rich mapping vocabulary
- Curators can capture nuanced relationship semantics

**Cons**:
- No downstream filterability without free-text parsing or enum-normalization
- Curators converge on inconsistent vocabularies over time
- Every new edge type requires downstream consumer updates to filter logic
- "Free-text relationship description" is a well-known antipattern in curated ontology work

**Why Not Chosen**: the closed 3-value enum (`primary`, `related`, `superseded`) covers the dominant relationship kinds at the semantic granularity downstream consumers actually query. The `citation` field carries the free-text evidence (via the cited URL or document), and any richer relationship semantics can be captured in the `citation` body. If future use cases require a richer edge-type vocabulary, a future ADR can extend the enum with explicit new values — but the closed-enum default is the safer starting point.

### Alternative 4 — Per-file PRDs (9 separate features)

F-A1 ships as 9 separate PRDs: one per catalog YAML (7), plus one for the crosswalk, plus one for the README-and-tests-and-ADR.

**Pros**:
- Smaller per-feature scope
- Each framework catalog has its own review cycle
- Per-framework blockers (e.g., ATLAS citation availability) don't block other catalogs

**Cons**:
- 9x the PRD + plan + tasks + review overhead for the same data
- Downstream consumers (F-A2, F-B) cannot start integration until the full set ships, so partial delivery provides no partial value
- The crosswalk is single-file by nature and cannot decompose — at least one PRD covers multi-catalog data regardless
- Per-framework blockers are better mitigated by per-framework tripwires within a single PRD (as F-A1 does with the ATLAS AML.T0058-T0062 curation tripwire per FR-016) than by full PRD decomposition

**Why Not Chosen**: the per-PRD overhead cost is estimated 3-4x the data-authoring cost, and downstream partial-value is zero. The cadence exception (Decision 7) is the practical efficiency choice, bounded to foundation-data features per the Reason 4 criteria.

### Alternative 5 — JSON/JSON-LD/RDF instead of YAML

The catalogs and crosswalk ship in JSON (or richer semantic formats like JSON-LD or RDF/SKOS).

**Pros**:
- JSON is machine-readable by any language's standard library
- JSON-LD / RDF / SKOS carry semantic-web interoperability with external ontology tools
- Some taxonomy publishers (MITRE) provide RDF/SKOS downloads

**Cons**:
- YAML is more human-authorable and review-friendly for the curation-heavy authoring phase
- Tachi's pipeline already uses YAML schemas (`schemas/finding.yaml`, `schemas/attack-chain.yaml`, `schemas/infographic.yaml`, `schemas/report.yaml`) — adding a different format for taxonomy data would fragment the schema surface
- JSON-LD/RDF/SKOS add semantic-web tooling overhead without clear F-A1 adopter demand
- `pyyaml` is already declared in `requirements-dev.txt`; adding `json-ld` or `rdflib` would violate the zero-new-runtime-dependency constraint (spec FR-037)

**Why Not Chosen**: YAML matches tachi's existing schema surface, is human-authorable for the curation workload, and imposes zero new dependencies. Future format exports (JSON-LD, RDF, SKOS) are listed as explicit out-of-scope items in spec 180 — a follow-on feature may emit alternate-format views derived from the YAML source of truth, preserving YAML as the authoring format.

---

## Consequences

### Positive

- **Machine-readable foundation for F-A2 and F-B**. The uniform catalog shape and crosswalk schema make cross-framework ID resolution a single-statement `yaml.safe_load` for adopters. Success Metric 7 is directly achievable.
- **Closed-enum filterability**. Every edge is programmatically filterable by `taxonomy`, `edge_type`, and `confidence` without free-text parsing.
- **Anti-drift confidence calibration**. The FR-013 rule prevents confidence inflation — the dominant failure mode in curated mapping data.
- **Zero runtime surface-area impact**. The byte-identity backward-compatibility invariant holds by construction (FR-036 / SC-004).
- **Follow-on expansion enabled at the schema layer**. The `edge_type` enum authorizes `related` and `superseded` at the schema-freeze point; follow-on expansion ships without schema migration.
- **CI-enforced data quality**. The pytest suite (FR-027 through FR-032) catches referential drift, enum violations, duplicate edges, and broken citations before PR merge — a durable mechanism against silent data rot.
- **Interpretation C cadence exception documented and bounded**. Foundation-data features meeting the Reason 4 criteria may invoke this precedent; other features ship per standard cadence.
- **Zero new dependencies**. `pyyaml` was already in `requirements-dev.txt` (spec Assumption A6); `pyproject.toml` and manifest diffs are empty at merge.

### Negative

- **Curation drift risk** — the crosswalk is curated by humans and can drift as external frameworks evolve (new OWASP versions, new ATT&CK techniques, new ATLAS waves, new CWE Top 25 editions). Mitigated by: (a) the FR-013 anti-drift confidence rule, (b) the integrity test suite catching referential breakage on every PR, (c) the README §Update Procedure (FR-033 section f) documenting per-framework refresh playbooks, (d) follow-on Issues filed on F-A1 PR merge for citation URL link-rot monitoring and `related`/`superseded` expansion.
- **Single-feature cadence exception adds PRD-scope authoring complexity** — PRD 180 is larger than a typical tachi PRD because it covers 9 files. Mitigated by: (a) the Interpretation C rationale explicitly bounds the exception to foundation-data features, (b) per-framework tripwires (ATLAS curation, Day 1 crosswalk spike, R3 Tier 1/2/3 edge-count fallbacks) let individual catalog issues descope without cascading to the full PRD, (c) the 3-agent parallel execution plan (architect + senior-backend-engineer + web-researcher) absorbs the scope in 4-5 working days per PRD Timeline.
- **Canonical-URL link-rot risk**. External framework URLs (OWASP, MITRE, NIST, CWE) can change over time. F-A1 mitigates this at authoring time (documented canonical-URL conventions per FR-033 section e) but does not monitor link-rot periodically. Link-rot monitoring is an explicit out-of-scope follow-on Issue filed on F-A1 PR merge.
- **NIST Surface B/C factual-error discovery risk**. If FR-022 verbatim transcription surfaces a factually-incorrect Surface B or Surface C row in `nist-ai-rmf-mapping.md`, the correction is deferred to an ADR-025 amendment Issue, NOT silently corrected during F-A1 (per spec FR-024). F-A1 is a transcription feature, not a re-authorship feature. This preserves the audit trail but introduces a delay between error discovery and correction.
- **ADR scope breadth**. This ADR documents schema decisions across 8 distinct contracts (per-item shape, per-edge shape, 3 enums, citation rule, cadence exception, governance protocol). The breadth is larger than a typical single-decision ADR. Mitigated by the explicit Decision 1-8 numbering and cross-links from each decision to its rationale.

### Neutral

- **Authoring convention divergence from existing tachi schemas**. `schemas/finding.yaml`, `schemas/attack-chain.yaml`, `schemas/infographic.yaml`, and `schemas/report.yaml` use JSON-Schema-style declarations (top-level `$schema`, `properties`, `required` keys). The F-A1 YAMLs are **data files** (lists of records), not schema-declaration files — the shape is documented in this ADR and enforced by the pytest suite, not by an embedded JSON-Schema header. This is a deliberate choice matching the YAML-as-data convention used by curated-taxonomy data sets (vs YAML-as-schema used for in-flight structural declarations).
- **The `cwe_refs` field asymmetry between `owasp.yaml` (populated) and 5 non-cwe non-owasp catalogs (empty `[]` but key-present) and `cwe.yaml` (field omitted entirely)** is explicit in the schema. Downstream parsers MUST handle all three cases. The integrity test enforces the asymmetry.
- **Interpretation C cadence exception precedent**. Future foundation-data features may cite this ADR to invoke the single-PRD cadence. Each citation is a documented-and-reviewed decision in the citing feature's PRD; this ADR does not grant blanket permission.

---

## Related Decisions

- [ADR-020](ADR-020-maestro-layer-classification.md): MAESTRO layer classification. The `nist-ai-rmf.yaml` catalog (68 Subcategory records) + `tachi-control-category.yaml` + `tachi-stride-ai-category.yaml` catalogs underpin future MAESTRO-aware crosswalk expansion. Crosswalk edges from `nist-ai-rmf` to other taxonomies are structurally compatible with MAESTRO layer annotation in follow-on features.
- [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md): SOURCE_DATE_EPOCH determinism. F-A1's integrity test (`test_citation_shape()`) uses URL-regex matching (no HTTP fetch) and file-path existence (local-FS only) — preserving ADR-021 determinism. The byte-identity backward-compatibility invariant (FR-036) holds by construction under the zero-runtime-touch constraint.
- [ADR-023](ADR-023-threat-agent-skill-references-pattern.md): Skill-references pattern. The 11 threat-detection agents' `detection-patterns.md` references (the seed source for 38 ATT&CK / 7 ATLAS / 41 CWE citations in spec Assumption A1) are structured per ADR-023. F-A1 does NOT modify any detection agent or shared reference — the seed citations are harvested read-only.
- [ADR-024](ADR-024-owasp-aivss-evaluation.md): OWASP AIVSS evaluation. AIVSS is a peer agentic-AI scoring framework documented as a documentation-only posture (not a runtime dependency). F-A1 does NOT include an AIVSS catalog — AIVSS IDs are not currently cited in tachi output. If future PRDs cite AIVSS, a follow-on F-A1 extension may add `aivss.yaml` as an 8th catalog with a corresponding enum value addition (governed by a future ADR amending this one).
- [ADR-025](ADR-025-nist-ai-rmf-evaluation.md): NIST AI RMF evaluation. The `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` file (authored via Feature 144 / ADR-025) is the **verbatim-transcription source** for 41 crosswalk edges per spec FR-022 (27 Surface B real-mapping rows + 14 Surface C Overlap rows). F-A1 does NOT re-author any Surface B/C content — corrections to Surface B/C are deferred to ADR-025 amendment Issues per spec FR-024.
- [ADR-026](ADR-026-pattern-classification-mechanism.md): Agentic pattern classification mechanism. Feature 142's `agentic_pattern` enum on `schemas/finding.yaml` is independent of F-A1 — agentic patterns are finding-level metadata, while F-A1 provides framework-level taxonomy records. Future features may emit crosswalk edges from agentic-pattern indicators to external framework IDs; the crosswalk schema supports this without extension.

---

## References

- Spec: [`specs/180-taxonomy-crosswalk-collection/spec.md`](../../../specs/180-taxonomy-crosswalk-collection/spec.md) — FR-001 through FR-041, SC-001 through SC-013
- Data model: [`specs/180-taxonomy-crosswalk-collection/data-model.md`](../../../specs/180-taxonomy-crosswalk-collection/data-model.md) — 2 entities, 3 enums, 11 validation rules, 5 test-coverage traceability entries
- Catalog record contract: [`specs/180-taxonomy-crosswalk-collection/contracts/catalog-record.yaml`](../../../specs/180-taxonomy-crosswalk-collection/contracts/catalog-record.yaml)
- Crosswalk edge contract: [`specs/180-taxonomy-crosswalk-collection/contracts/crosswalk-edge.yaml`](../../../specs/180-taxonomy-crosswalk-collection/contracts/crosswalk-edge.yaml)
- PRD: [`docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`](../../product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md)
- Tasks: [`specs/180-taxonomy-crosswalk-collection/tasks.md`](../../../specs/180-taxonomy-crosswalk-collection/tasks.md) — 5-phase execution plan, Wave 1.1 schema-lock gate, tripwire decisions
- NIST AI RMF mapping reference: [`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`](../../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) — FR-022 verbatim-transcription source
- 11 threat-detection agents' `detection-patterns.md` files under `.claude/skills/tachi-<name>/references/` — seed source for 38 ATT&CK / 7 ATLAS / 41 CWE citations (spec Assumption A1)
- OWASP LLM Top 10:2025 — [`https://genai.owasp.org/llm-top-10/`](https://genai.owasp.org/llm-top-10/)
- OWASP Top 10 for Agentic Applications:2026 — OWASP GenAI project
- OWASP Top 10:2021 — [`https://owasp.org/Top10/`](https://owasp.org/Top10/)
- OWASP API Security Top 10:2023 — [`https://owasp.org/API-Security/`](https://owasp.org/API-Security/)
- OWASP Mobile Top 10:2024 — [`https://owasp.org/www-project-mobile-top-10/`](https://owasp.org/www-project-mobile-top-10/)
- OWASP ML Security Top 10:2023 — [`https://owasp.org/www-project-machine-learning-security-top-10/`](https://owasp.org/www-project-machine-learning-security-top-10/)
- MITRE ATT&CK Enterprise matrix — [`https://attack.mitre.org/`](https://attack.mitre.org/)
- MITRE ATLAS matrix (v5.4 current as of 2026-04-17) — [`https://atlas.mitre.org/`](https://atlas.mitre.org/)
- CWE Top 25 (2025) published 2025-12-11 — [`https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html`](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)
- NIST AI 100-1 (NIST AI RMF 1.0) — [`https://doi.org/10.6028/NIST.AI.100-1`](https://doi.org/10.6028/NIST.AI.100-1)

---

## Revision History

**2026-04-17 (Proposed — Feature 180, Wave 1.1 schema lock)**: Records the `schemas/taxonomy/` schema decisions for the F-A1 Taxonomy Crosswalk Collection feature. Documents 8 numbered decisions covering per-item record shape (with unidirectional OWASP→CWE `cwe_refs` rule), per-edge record shape, 7-value `taxonomy` enum, 3-value `edge_type` enum (with follow-on `related`/`superseded` authorization), 3-value `confidence` enum (with anti-drift rule), citation non-empty-and-resolvable rule, Interpretation C single-feature cadence exception (bounded to foundation-data features), and Proposed→Accepted dual-commit governance protocol. Authored at end of Day 1 after schema freeze and preceding parallel catalog authoring in Wave 1.2. Status transitions to Accepted at PR merge per Decision 8 (spec FR-041).

**2026-04-17 (Proposed — Feature 180, Wave 3.2 T027 Surface C decision)**: Records the Surface C out-of-scope decision under **Option (c) — keep Surface C out-of-scope for F-A1**. Implementation at Wave 3.1 T023 surfaced a structural blocker: Surface C rows in `nist-ai-rmf-mapping.md` use NIST AI 600-1 §2.X GAI Risk identifiers, which are structurally distinct from AI RMF Subcategories (per ADR-025 three-surface structure: Surface A Functions × pipeline phases; Surface B Subcategories × control categories; Surface C GAI risks × STRIDE+AI categories). The closed 7-value `taxonomy` enum in Decision 3 has no `nist-ai-600-1` value, and `nist-ai-rmf.yaml` contains AI RMF 1.0 Subcategories only (not AI 600-1 GAI Risks). Options evaluated: (a) expand enum to 8-value + author `nist-ai-600-1.yaml` — rejected on budget + scope-change-not-correction grounds; (b) amend FR-022 direction — rejected as dependent on (a); (c) defer Surface C to F-A1.1 — **selected** on budget-realism + FR-024 transcription-not-re-authorship discipline + ADR-025 structural soundness grounds; (d) correct the reference file — rejected because the reference file is not conflated, the conflation is in F-A1's spec FR-022 direction. Spec amendments at `.aod/spec.md` / `specs/180-taxonomy-crosswalk-collection/spec.md`: FR-004 example corrected (`MEASURE-2.7` → `MEASURE 2.7`); FR-022 narrowed to Surface B only (27 edges, down from estimated 41); FR-032 clarified for numeric-within-function NIST sort; SC-008 narrowed to Surface B only. PM re-sign slot opened at `pm_signoff_amendment_2`. T029 cleanup: REMOVE all 22 Surface B drifted edges + all 16 Surface C drifted edges (38 edges total); web-researcher Day 4 pre-T029 top-up target ≥540 primary edges to land post-T029 at ≥502 (Tier 1 HOLDS). Follow-on Issue F-A1.1 filed at T034 scopes: adding `nist-ai-600-1` as the 8th enum value, authoring `schemas/taxonomy/nist-ai-600-1.yaml` (12 GAI risk records), transcribing the 15 Surface C Overlap rows as `tachi-stride-ai-category → nist-ai-600-1` edges. Status remains Proposed; Accepted transition remains at T032 PR merge per Decision 8. Architect decision artifact: `.aod/results/architect.md` (T027).

**2026-04-17 (Accepted — Feature 180, Wave 4.2 T032 status transition)**: Status transition **Proposed → Accepted** per T032 at end of Day 4 Wave 4.2, honoring the Decision 8 dual-commit governance protocol (Proposed at Day 1 Wave 1.1 schema-lock; Accepted at PR merge-time). Accepted-date recorded as provisional **2026-04-21** (T032 authoring date + 4 days, targeting Day 5 merge window); date will be corrected to the actual merge date at T039 post-merge update if it differs. Merge commit SHA placeholder `<pending-T039-post-merge-fill>` will be replaced with the squash-merge commit SHA at T039 per FR-041 and Architect post-merge-SHA-fill suggestion recorded in `specs/180-taxonomy-crosswalk-collection/tasks.md` §T032. This transition is independent of T029 drift remediation (senior-backend-engineer Option (d) MIX plan per `.aod/results/architect.md` §T029 — running in parallel); ADR-027 does not reference the specific edge count or drift scope, so the transition is safe at this point in the Day 4 cadence. All 8 Decisions (Decision 1–8) are preserved in their ratified form; the T027 Surface C amendment recorded above is the only substantive content update since Proposed authoring. Post-merge, T039 will update both the Accepted-date line (if the merge slips or accelerates) and the Accepted-commit-SHA placeholder per the strengthened-provenance suggestion.
