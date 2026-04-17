# schemas/taxonomy/ — Machine-Readable Taxonomy Catalog + Crosswalk

> **Status**: Draft (Day 2 authoring). Provenance counts and retrieval dates are stubs here and will be finalized by T025 on Day 3.
>
> **Feature**: [180-taxonomy-crosswalk-collection](../../specs/180-taxonomy-crosswalk-collection/spec.md) (F-A1)
> **ADR**: [ADR-027 Taxonomy Crosswalk Schema](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md)

---

## 1. Purpose

`schemas/taxonomy/` is a machine-readable catalog and crosswalk of the seven taxonomies tachi cites across its agentic-AI threat-modeling output — OWASP (6 published lists), MITRE ATT&CK, MITRE ATLAS, NIST AI RMF 1.0, CWE, plus two tachi pseudo-taxonomies (`tachi-control-category`, `tachi-stride-ai-category`). Every taxonomy ID tachi cites resolves here to a record carrying `{id, full_id, name, url, cwe_refs}`, and every cross-framework mapping (e.g., "what CWEs does OWASP LLM05 relate to?") resolves to a single row in `crosswalk.yaml`.

This is the **foundation data** for downstream features:
- **F-A2** (finding-level source attribution) will extend the finding schema with a `source_attribution` field that cites specific crosswalk edges.
- **F-B** (coverage attestation report section) will render a per-DFD-component-class attestation that a given framework is fully covered.
- Future ecosystem integrations (vulnerability manager, SIEM, compliance dashboard) can consume the YAMLs directly via `yaml.safe_load` without parsing agent markdown prose.

The directory ships **9 files** (per spec FR-001): 7 catalog YAMLs + 1 crosswalk YAML + this README. See [ADR-027](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md) for the full schema rationale, the 7-value `taxonomy` enum, the 3-value `edge_type` / `confidence` enums, and the "Interpretation C" single-feature cadence exception.

### Runnable Python snippet (SC-007)

Copy into a Python 3.11 REPL at repo root. Requires only `pyyaml` from `requirements-dev.txt`:

```python
import yaml
edges = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))
print(f"Total edges: {len(edges)}")
for edge in edges[:3]:
    print(f"  {edge['source']['taxonomy']}:{edge['source']['id']} -> {edge['target']['taxonomy']}:{edge['target']['id']} ({edge['confidence']})")
```

For per-catalog resolution, substitute any of the 7 catalog files:

```python
for taxonomy in ('owasp', 'mitre-attack', 'mitre-atlas', 'nist-ai-rmf', 'cwe',
                 'tachi-control-category', 'tachi-stride-ai-category'):
    records = yaml.safe_load(open(f'schemas/taxonomy/{taxonomy}.yaml'))
    print(f"{taxonomy}: {len(records)} records (example: {records[0]['id']})")
```

### What F-A1 does NOT give you today

F-A1 is the machine-readable **foundation** — it deliberately defers three downstream capabilities to separately-scoped follow-on features. Readers integrating tachi output today should be aware of these gaps:

1. **Finding-level citation** — At F-A1, threat-agent findings in `threats.md` / `threats.sarif` do **not** yet cite specific crosswalk edges. A finding that says "relates to OWASP LLM05" still carries that as free-text metadata, not a structured reference into `crosswalk.yaml`. **F-A2** will extend the finding schema with a `source_attribution` field that resolves to one or more edge IDs in the crosswalk.
2. **Coverage attestation** — At F-A1, no attestation exists that a given DFD component class (e.g., "all `llm_process` components have been evaluated against 100% of OWASP LLM Top 10:2025 items") has been fully mapped. The data to *compute* such an attestation is present in the crosswalk, but no downstream report section renders it. **F-B** will add a coverage-attestation report section consuming these YAMLs.
3. **Agent-reference migration** — At F-A1, the 11 threat-detection agents still carry inline taxonomy citations in their `.claude/skills/tachi-<name>/references/detection-patterns.md` files (per ADR-023). The F-A1 catalog YAMLs harvest those citations *read-only* — no detection agent is modified. Migrating the detection patterns to cite crosswalk edges (removing inline duplication) is a **separate follow-on feature**, not F-A1 scope.

---

## 2. Harvest methodology

The 7 catalog YAMLs are assembled from three source classes:

1. **Agent citation seed** — the 38 ATT&CK / 7 ATLAS / 41 CWE IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files (full frozen list in spec Assumption A1).
2. **External published lists** — the full published item set for each externally-curated framework: OWASP (6 Top 10 lists), NIST AI RMF 1.0 (68 Subcategories from NIST AI 100-1 Tables 1–4), CWE Top 25 (2025), MITRE ATLAS v5.x October 2025 agent techniques (AML.T0058–T0062).
3. **Verbatim transcription from `nist-ai-rmf-mapping.md`** — per spec FR-022, every Surface B real-mapping row (27) and every Surface C Overlap row (14) in `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (authored via Feature 144 / ADR-025) is transcribed verbatim into `crosswalk.yaml` as 41 edges. "No equivalent" and "Gap" rows are omitted by default.

Curation rule: F-A1 is a **harvest + transcription** feature, not a re-authorship feature. Where a published source is factually incorrect, the correction is filed as a separate ADR-025 (or equivalent) amendment Issue, NOT silently corrected in F-A1 (per spec FR-024).

---

## 3. Per-framework provenance

### 3.1 `owasp.yaml`

- **Seed source**: external published lists (OWASP does not appear in agent citations as canonical IDs).
- **External curation**: 6 OWASP published Top 10 lists:
  - OWASP Top 10:2021 (A01–A10)
  - OWASP API Security Top 10:2023 (API1–API10)
  - OWASP Top 10 for Agentic Applications:2026 (ASI01–ASI10)
  - OWASP LLM Top 10:2025 (LLM01–LLM10)
  - OWASP Mobile Top 10:2024 (M1–M10)
  - OWASP Machine Learning Security Top 10:2023 (ML01–ML10)
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-020): ≥60 items.

### 3.2 `mitre-attack.yaml`

- **Seed source**: 38 unique MITRE ATT&CK technique IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files (spec Assumption A1).
- **External curation**: growth via external ATT&CK matrix curation is permitted but NOT mandated in F-A1.
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-015): ≥38 techniques.

### 3.3 `mitre-atlas.yaml`

- **Seed source**: 7 ATLAS technique IDs currently cited across the 11 threat-detection agents: AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057.
- **External curation**: 5 October 2025 agent techniques from `atlas.mitre.org` (AML.T0058, AML.T0059, AML.T0060, AML.T0061, AML.T0062). AML.T0058 additionally appears in tachi's `finding-format-shared.md`.
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-016): ≥12 records (7 seed + 5 curated). A curation tripwire (per spec FR-016) escalates to architect if any of AML.T0058–T0062 cannot be resolved to a stable citation URL by Day 2 end.

### 3.4 `nist-ai-rmf.yaml`

- **Seed source**: external published catalog — NIST AI 100-1 Tables 1–4 (Govern / Map / Measure / Manage Functions × 18 Categories × 68 Subcategories).
- **External curation**: full published Subcategory catalog.
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-021): exactly 68 records.

### 3.5 `cwe.yaml`

- **Seed source**: 41 unique CWE IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files (spec Assumption A1).
- **External curation**: CWE Top 25 (**2025**, published 2025-12-11) — 12 net-new CWEs beyond the agent seed (the 13-CWE overlap between seed and Top 25 is deduplicated to a single record).
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-017): ≥53 records.
- **Record-shape exception**: `cwe_refs` is **omitted entirely** on `cwe.yaml` records — CWE→CWE relations live in `crosswalk.yaml`, not as per-record cross-references (per ADR-027 Decision 1).

### 3.6 `tachi-control-category.yaml`

- **Seed source**: `.claude/skills/tachi-control-analysis/references/control-categories.md`.
- **External curation**: none (tachi pseudo-taxonomy).
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-018): exactly 8 records — `authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`.

### 3.7 `tachi-stride-ai-category.yaml`

- **Seed source**: `.claude/skills/tachi-shared/references/stride-categories-shared.md`.
- **External curation**: none (tachi pseudo-taxonomy).
- **Retrieval date**: *(T025 to finalize)*
- **Target count** (FR-019): exactly 11 records — 6 STRIDE categories (`spoofing`, `tampering`, `repudiation`, `information-disclosure`, `denial-of-service`, `elevation-of-privilege`) + 5 AI categories (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`).

---

## 4. Confidence calibration rubric

Every edge in `crosswalk.yaml` carries a `confidence` field from the closed 3-value enum:

| Value | Criterion | Example |
|-------|-----------|---------|
| `high` | **Published cross-reference** — the authoritative source explicitly lists the target ID. | OWASP LLM05 explicitly lists CWE-79, CWE-89, CWE-116 in its published cross-references — any LLM05→CWE-79 edge is `high`. |
| `medium` | **Inferred one-hop** — semantic match without explicit listing, but citable to one authoritative document. | LLM05 relates to CWE-20 ("Improper Input Validation") via category-semantic match documented in the OWASP LLM project README, not via LLM05's explicit CWE list. |
| `high` (NIST transcription) | Any edge derived from `nist-ai-rmf-mapping.md` Surface B or Surface C (verbatim transcription per FR-022). | `tachi-control-category:authentication → nist-ai-rmf:MEASURE-2.7` — Surface B real-mapping row. |
| `low` | **Two-hop or thematic** — curator judgment backed by a non-authoritative document (blog, research paper, internal analysis). | MITRE ATT&CK T1190 relates to OWASP API7 via adversary-objective alignment discussed in a security-research paper, not in any framework's published cross-reference. |

**Anti-drift rule** (verbatim, spec FR-013): **"if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label."**

This rule inverts the default bias toward confidence inflation — the single most common failure mode in curated cross-framework mappings. The fallback is always `low` (still a valid, shippable value), so the rule does not create pressure to drop edges; it creates pressure to calibrate them honestly. See [ADR-027 Reason 3](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md) for the full rationale.

---

## 5. Canonical-URL conventions

| Framework | Catalog YAML | URL pattern |
|-----------|--------------|-------------|
| MITRE ATT&CK | `mitre-attack.yaml` | `https://attack.mitre.org/techniques/T<N>/` (e.g., `https://attack.mitre.org/techniques/T1190/`) |
| MITRE ATLAS | `mitre-atlas.yaml` | `https://atlas.mitre.org/techniques/AML.T<NNNN>` (e.g., `https://atlas.mitre.org/techniques/AML.T0058`) |
| CWE | `cwe.yaml` | `https://cwe.mitre.org/data/definitions/<N>.html` (e.g., `https://cwe.mitre.org/data/definitions/89.html`) |
| NIST AI RMF 1.0 | `nist-ai-rmf.yaml` | `https://doi.org/10.6028/NIST.AI.100-1` (DOI-based; single canonical document URL per Subcategory record) |
| OWASP LLM Top 10:2025 | `owasp.yaml` | `https://genai.owasp.org/llmrisk/llm<NN>-<slug>/` (e.g., `https://genai.owasp.org/llmrisk/llm05-improper-output-handling/`) |
| OWASP Top 10:2021 | `owasp.yaml` | `https://owasp.org/Top10/2021/A<NN>_2021-<slug>/` |
| OWASP API Security Top 10:2023 | `owasp.yaml` | `https://owasp.org/API-Security/editions/2023/en/0xa<N>-<slug>/` |
| OWASP Mobile Top 10:2024 | `owasp.yaml` | `https://owasp.org/www-project-mobile-top-10/2024-risks/m<N>-<slug>` |
| OWASP ML Security Top 10:2023 | `owasp.yaml` | `https://owasp.org/www-project-machine-learning-security-top-10/docs/ML<NN>_<year>-<slug>` |
| OWASP Agentic Top 10:2026 | `owasp.yaml` | OWASP GenAI project URL (per-item; finalize in T025) |
| tachi pseudo-taxonomies | `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml` | Repo-relative path to canonical source reference (e.g., `.claude/skills/tachi-control-analysis/references/control-categories.md`) |

Link-rot monitoring for external URLs is **out of F-A1 scope** (follow-on Issue filed on F-A1 PR merge). The integrity test (`test_citation_shape()` per FR-031) verifies URL syntax via regex only — no HTTP fetch (ADR-021 determinism).

---

## 6. Update procedure

### 6.1 OWASP

When a new edition of any OWASP list publishes (e.g., OWASP LLM Top 10 v2027): re-harvest the item set, update `owasp.yaml` records with new IDs / names / URLs, and re-author any affected `crosswalk.yaml` edges citing the superseded IDs. Record the retrieval date in §3.1 and the superseded version's last-retrieval date in the git commit message.

### 6.2 MITRE ATT&CK

When a new ATT&CK matrix version publishes: re-harvest the 38-technique seed from `detection-patterns.md` files, add any new techniques cited by agent enrichment, and update URLs. The agent-citation seed is the authoritative baseline — growth beyond the seed is out of F-A1 scope unless the agent layer cites new techniques.

### 6.3 MITRE ATLAS

When a new ATLAS wave publishes (e.g., v5.5 with new agent techniques beyond AML.T0058–T0062): add new technique records via external curation; update the retrieval date in §3.3. The 7 seed + 5 curated baseline is preserved — additions are additive.

### 6.4 CWE

When CWE Top 25 publishes a new edition (e.g., 2026 list): diff the new list against the current `cwe.yaml`, add net-new CWE records, and retain the existing 41-CWE agent-citation seed (which is independent of the Top 25 churn). Record the new Top 25 retrieval date in §3.5.

### 6.5 NIST AI RMF

When NIST AI RMF 2.0 publishes: re-harvest the full Subcategory catalog, verify count changes from 68, and **re-verify** the Surface B/C transcriptions in `crosswalk.yaml` against the updated `nist-ai-rmf-mapping.md`. Changes to Surface B/C content MUST go through an ADR-025 amendment Issue per spec FR-024 — F-A1 remains a transcription feature, not a re-authorship feature.

---

## 7. Crosswalk methodology

`crosswalk.yaml` is composed from primary-only edges in F-A1 (per spec FR-025). `related` and `superseded` edge types are **authorized in the schema but out of F-A1 scope** — they ship as a follow-on Issue filed on F-A1 PR merge.

Day 1 authoring spike (per spec Assumption A5) seeded the crosswalk with **5-slice composition**: 10 OWASP↔CWE + 10 ATT&CK↔CWE + 10 ATT&CK↔ATLAS + 10 LLM↔NIST + 10 Agentic↔MITRE. This 50-edge spike validated the per-edge authoring rate against the ≥500-edge target (spec Risk R3 tiered fallback: Tier 2 = 300-edge floor team-lead-authorizable, Tier 3 = 150-edge floor PRD-amendment-required).

Priority harvest order (Day 2–3):
1. OWASP→CWE edges (published cross-references in OWASP item pages — `high` confidence by construction).
2. ATT&CK→CWE edges (MITRE "Related Weaknesses" on technique pages — `high` by construction).
3. ATT&CK→ATLAS bridge edges (MITRE cross-references — `high` or `medium`).
4. NIST Surface B/C verbatim transcription (41 edges from `nist-ai-rmf-mapping.md` — `high` by construction per FR-022).
5. LLM / Agentic cross-framework inferred edges (`medium` or `low` per confidence rubric).

Citation rules per edge:
- **URL-shaped** citation (matches `^https?://`): preferred for external framework cross-references.
- **Repo-relative file path**: used for NIST transcription edges (`citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`) and tachi pseudo-taxonomy edges.
- Every edge MUST carry exactly one non-empty citation (enforced by `test_citation_shape()` per FR-031).

Deduplication: the 3-tuple `{source, target, edge_type}` MUST be unique across the full crosswalk (enforced by `test_crosswalk_loads()` per FR-029).

---

## 8. Single-source-of-truth cross-reference

NIST Surface B/C mappings in `crosswalk.yaml` are transcribed **verbatim** from [`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) (authored via Feature 144 / ADR-025). F-A1 is a transcription feature, not a re-authorship feature.

**For factual corrections to Surface B/C content: file a separate ADR-025 amendment Issue. Do NOT silent-correct in F-A1.**

Per spec FR-024: if the implementing agent discovers a Surface B or Surface C row is factually inaccurate during transcription, the correction MUST be filed as a separate ADR-025 amendment Issue. The F-A1 crosswalk edges transcribe the current `nist-ai-rmf-mapping.md` state at merge-time commit — any subsequent correction lands in a follow-on PR that updates both `nist-ai-rmf-mapping.md` AND the corresponding crosswalk edges together.

This preserves the audit trail that `nist-ai-rmf-mapping.md` is the single source of truth for Surface B/C content. Downstream consumers (F-A2 findings, F-B coverage reports) citing these edges can reason about the provenance via the `citation` field pointing at `nist-ai-rmf-mapping.md` — the file rev is resolvable via git history.
