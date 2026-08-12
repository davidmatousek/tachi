# schemas/taxonomy/ — Machine-Readable Taxonomy Catalog + Crosswalk

> **Status**: Day 3 final (per-framework provenance counts and retrieval dates resolved by T025).
> **Retrieval date (all external frameworks, this revision)**: 2026-04-17.
>
> **Feature**: [180-taxonomy-crosswalk-collection](../../specs/180-taxonomy-crosswalk-collection/spec.md) (F-A1)
> **ADR**: [ADR-027 Taxonomy Crosswalk Schema](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md)

---

## 1. Purpose

`schemas/taxonomy/` is a machine-readable catalog and crosswalk of the eight taxonomies tachi cites across its agentic-AI threat-modeling output — OWASP (6 published lists), MITRE ATT&CK, MITRE ATLAS, NIST AI RMF 1.0, NIST AI 600-1 (GAI Risks), CWE, plus two tachi pseudo-taxonomies (`tachi-control-category`, `tachi-stride-ai-category`). Every taxonomy ID tachi cites resolves here to a record carrying `{id, full_id, name, url, cwe_refs}`, and every cross-framework mapping (e.g., "what CWEs does OWASP LLM05 relate to?") resolves to a single row in `crosswalk.yaml`.

This is the **foundation data** for downstream features:
- **F-A2** (finding-level source attribution) will extend the finding schema with a `source_attribution` field that cites specific crosswalk edges.
- **F-B** (coverage attestation report section) will render a per-DFD-component-class attestation that a given framework is fully covered.
- Future ecosystem integrations (vulnerability manager, SIEM, compliance dashboard) can consume the YAMLs directly via `yaml.safe_load` without parsing agent markdown prose.

The directory ships **10 files** (9 per spec FR-001, plus the 8th catalog added at F-184): 8 catalog YAMLs + 1 crosswalk YAML + this README. See [ADR-027](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md) for the full schema rationale, the 8-value `taxonomy` enum (extended from 7 at F-184 — see the ADR-027 Revision History), the 3-value `edge_type` / `confidence` enums, and the "Interpretation C" single-feature cadence exception.

### Runnable Python snippet (SC-007)

Copy into a Python 3.11 REPL at repo root. Requires only `pyyaml` from `requirements-dev.txt`:

```python
import yaml
edges = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))
print(f"Total edges: {len(edges)}")
for edge in edges[:3]:
    print(f"  {edge['source']['taxonomy']}:{edge['source']['id']} -> {edge['target']['taxonomy']}:{edge['target']['id']} ({edge['confidence']})")
```

For per-catalog resolution, substitute any of the 8 catalog files:

```python
for taxonomy in ('owasp', 'mitre-attack', 'mitre-atlas', 'nist-ai-rmf', 'nist-ai-600-1',
                 'cwe', 'tachi-control-category', 'tachi-stride-ai-category'):
    records = yaml.safe_load(open(f'schemas/taxonomy/{taxonomy}.yaml'))
    print(f"{taxonomy}: {len(records)} records (example: {records[0]['id']})")
```

### What F-A1 does NOT give you today

F-A1 is the machine-readable **foundation** — it deliberately defers three downstream capabilities to separately-scoped follow-on features. Readers integrating tachi output today should be aware of these gaps:

1. **Finding-level citation** — At F-A1, threat-agent findings in `threats.md` / `threats.sarif` do **not** yet cite specific crosswalk edges. A finding that says "relates to OWASP LLM05" still carries that as free-text metadata, not a structured reference into `crosswalk.yaml`. **F-A2** will extend the finding schema with a `source_attribution` field that resolves to one or more edge IDs in the crosswalk.
2. **Coverage attestation** — At F-A1, no attestation exists that a given DFD component class (e.g., "all `llm_process` components have been evaluated against 100% of OWASP LLM Top 10:2026 items") has been fully mapped. The data to *compute* such an attestation is present in the crosswalk, but no downstream report section renders it. **F-B** will add a coverage-attestation report section consuming these YAMLs.
3. **Agent-reference migration** — At F-A1, the 11 threat-detection agents still carry inline taxonomy citations in their `.claude/skills/tachi-<name>/references/detection-patterns.md` files (per ADR-023). The F-A1 catalog YAMLs harvest those citations *read-only* — no detection agent is modified. Migrating the detection patterns to cite crosswalk edges (removing inline duplication) is a **separate follow-on feature**, not F-A1 scope.

---

## 2. Harvest methodology

The 8 catalog YAMLs are assembled from three source classes:

1. **Agent citation seed** — the 38 ATT&CK / 7 ATLAS / 41 CWE IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files (full frozen list in spec Assumption A1).
2. **External published lists** — the full published item set for each externally-curated framework: OWASP (6 Top 10 lists), NIST AI RMF 1.0 (72 Subcategories — see §3.4 for the FR-021 amendment trail), CWE Top 25 (2025), MITRE ATLAS v5.4 October 2025 agent techniques (AML.T0058–T0062).
3. **Verbatim transcription from `nist-ai-rmf-mapping.md`** — per spec FR-022, every Surface B real-mapping row (27) in `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (authored via Feature 144 / ADR-025) is transcribed verbatim into `crosswalk.yaml` as 27 `tachi-control-category → nist-ai-rmf` edges. "No equivalent" and "Gap" rows are omitted by default. **F-184 amendment**: this bullet originally counted 14 Surface C Overlap rows toward a 41-edge transcription total — stale on both counts. Surface C was **deferred at F-180** (ADR-027 T027 entry: the F-180 FR-022 direction conflated NIST AI 600-1 GAI Risks with AI RMF 1.0 Subcategories) and **transcribed at F-184** as **15 `tachi-stride-ai-category → nist-ai-600-1` `primary` edges**, direction-corrected per the F-184 FR-022 ratification; the 16 legacy `tachi-stride-ai-category → nist-ai-rmf` drift edges were removed in the same change-set (T027 directive completed). Transcription total: 27 Surface B + 15 Surface C = 42 edges. See §3.8 for the `nist-ai-600-1.yaml` provenance.

Curation rule: F-A1 is a **harvest + transcription** feature, not a re-authorship feature. Where a published source is factually incorrect, the correction is filed as a separate ADR-025 (or equivalent) amendment Issue, NOT silently corrected in F-A1 (per spec FR-024).

---

## 3. Per-framework provenance

### 3.1 `owasp.yaml`

- **Seed source**: external published lists (OWASP does not appear in agent citations as canonical IDs at F-A1 merge time).
- **External curation**: 6 OWASP published Top 10 lists (10 items each = 60 records total):
  - OWASP Top 10:2021 (A01–A10) — source: `https://owasp.org/Top10/2021/`
  - OWASP API Security Top 10:2023 (API1–API10) — source: `https://owasp.org/API-Security/editions/2023/en/0x11-t10/`
  - OWASP Top 10 for Agentic Applications:2026 (ASI01–ASI10) — source: OWASP GenAI Security Project, `https://genai.owasp.org/resource/agentic-ai-security-top-10/` (2026 edition published by the OWASP GenAI project)
  - OWASP LLM Top 10:2026 (LLM01–LLM10) — source: OWASP GenAI Security Project, `https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/` (LLM01:2026 through LLM10:2026; single release-resource URL per the 2026 edition — per-entry pages not yet published)
  - OWASP Mobile Top 10:2024 (M1–M10) — source: `https://owasp.org/www-project-mobile-top-10/`
  - OWASP Machine Learning Security Top 10:2023 (ML01–ML10) — source: `https://owasp.org/www-project-machine-learning-security-top-10/`
- **CWE cross-references**: `cwe_refs` populated for Top 10:2021 records only (A01–A10), transcribed from the per-category OWASP pages' "List of Mapped CWEs" sections. LLM / Agentic / Mobile / ML / API records carry `cwe_refs: []` because the respective OWASP sources do not publish per-item CWE cross-references; cross-framework edges for those lists live in `crosswalk.yaml`.
- **Retrieval date**: **2026-04-17** (all 6 lists).
- **Final record count**: **60** (FR-020 floor ≥60 — met exactly).

### 3.2 `mitre-attack.yaml`

- **Seed source**: 38 unique MITRE ATT&CK technique / sub-technique IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files (frozen list per spec Assumption A1): `T1005, T1039, T1068, T1070 (+ .001/.002/.004/.006/.008), T1078 (+ .004), T1195 (+ .001/.002), T1213 (+ .001/.002/.003/.005), T1498 (+ .001/.002), T1499 (+ .001/.002/.003/.004), T1530, T1548 (+ .001/.003/.005), T1550 (+ .001), T1556, T1562 (+ .006), T1565` — source: MITRE ATT&CK Enterprise matrix at `https://attack.mitre.org/`.
- **External curation**: none in F-A1. Growth via external ATT&CK matrix curation is permitted but NOT mandated; the agent-citation seed is the authoritative baseline (see §6.2).
- **Retrieval date**: **2026-04-17** (per-technique pages on `attack.mitre.org`).
- **Final record count**: **38** (FR-015 floor ≥38 — met exactly).

### 3.3 `mitre-atlas.yaml`

- **Seed source**: 7 ATLAS technique IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files: `AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057`. AML.T0058 is additionally cited in tachi's `.claude/skills/tachi-shared/references/finding-format-shared.md`.
- **External curation**: 5 October 2025 agent techniques added per FR-016: `AML.T0058, AML.T0059, AML.T0060, AML.T0061, AML.T0062`.
- **Canonical source**: MITRE ATLAS **v5.4** as of 2026-04-17, primary source `https://atlas.mitre.org/techniques/<id>` (URL pattern, no trailing slash). During T020 harvest on 2026-04-17, WebFetch returned HTTP 404 on individual ATLAS technique pages due to client-side anti-bot gating (confirmed with the known-good seed AML.T0051, which also 404'd via the same client). URL stability was verified by cross-referencing the authoritative MITRE-owned `atlas-data` repository at `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques.yaml` (primary) and MISP galaxy `mitre-atlas-attack-pattern` (secondary). Canonical names for AML.T0058–T0062 were **corrected at commit `be18076`** against `atlas-data/techniques.yaml` after T011's initial harvest produced contaminated names; the name correction did not alter URLs or IDs, so zero crosswalk edge rewrites were needed. See the R7 tripwire resolution in `mitre-atlas.yaml` inline comments lines 18–30.
- **Retrieval date**: **2026-04-17** (MITRE `atlas-data` repo `main` branch snapshot).
- **Final record count**: **12** (FR-016 floor ≥12 — 7 seed + 5 curated, exact match).

### 3.4 `nist-ai-rmf.yaml`

- **Seed source**: external published catalog — **NIST AI RMF 1.0** (NIST AI 100-1, DOI `https://doi.org/10.6028/NIST.AI.100-1`, initial publication January 2023) PLUS the NIST AI Risk Management Playbook pages at `airc.nist.gov` (GOVERN / MAP / MEASURE / MANAGE Functions), which provide the authoritative operational Subcategory enumeration.
- **External curation**: full published Subcategory catalog harvested from the `airc.nist.gov` Playbook pages on 2026-04-17. Breakdown: **GOVERN 19 + MAP 18 + MEASURE 22 + MANAGE 13 = 72 Subcategories** (per Function Tables 1–4). All records share the DOI-anchored URL `https://doi.org/10.6028/NIST.AI.100-1` per the §5 canonical-URL convention; per-Subcategory section anchors are not stable across NIST publication revisions, so the DOI is the reproducible citation.
- **Retrieval date**: **2026-04-17** (airc.nist.gov Playbook page snapshot for all 4 Functions).
- **FR-021 amendment (68 → 72)**: FR-021 originally pinned the count at 68, a historical figure from the initial January 2023 publication of NIST AI 100-1. Day 2 primary-source harvest of the current `airc.nist.gov` Playbook catalog surfaced 72 Subcategories — MEASURE 2.12, MEASURE 2.13, and 2 others were added in subsequent NIST Playbook expansions. Under FR-024 primary-source-correction discipline, the spec was amended 68 → 72 at commit SHA **`9da377c`** rather than descoping the catalog. Both Architect (`.aod/results/architect.md`, Path (a)) and PM (`.aod/results/product-manager.md`, pm_signoff_amendment_1 at `specs/180-taxonomy-crosswalk-collection/spec.md` lines 9–17) concurred. Existing Surface B/C cited Subcategories (`MAP 4.2`, `MEASURE 2.6–2.10`, `MANAGE 1.3`, `MANAGE 2.4`, `GOVERN 1.4`) are within the 68-subset ⊂ 72-superset, so FR-022 transcription fidelity and the 38 already-committed `nist-ai-rmf` crosswalk edges (batch 5, commit `004cd00`) remain intact — zero edits required to ADR-025 or `nist-ai-rmf-mapping.md`. This is the same pinned-with-retrieval-date provenance pattern applied to CWE Top 25 2025 in §3.5.
- **Final record count**: **72** (FR-021 amended — exact; GOVERN 19 + MAP 18 + MEASURE 22 + MANAGE 13).

### 3.5 `cwe.yaml`

- **Seed source**: 41 unique CWE IDs currently cited across the 11 threat-detection agents' `detection-patterns.md` files (frozen at spec time 2026-04-17 per spec Assumption A1): `CWE-20, 22, 77, 78, 89, 90, 117, 200, 209, 215, 223, 250, 266, 269, 285, 287, 290, 306, 345, 352, 384, 400, 407, 494, 502, 522, 532, 538, 613, 639, 770, 776, 778, 779, 862, 863, 917, 918, 943, 1333, 1395`.
- **External curation**: CWE Top 25 (**2025** edition, published **2025-12-11** by MITRE/CISA, source `https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html`) — of the 25 Top 25 IDs, 14 overlap the agent seed and are deduplicated to a single record; **11 net-new CWEs** are added: `CWE-79, 94, 120, 121, 122, 125, 284, 416, 434, 476, 787`. Plus **1 additional CWE** sourced from the OWASP Top 10 A03:2021 / LLM10:2026 cross-references already transcribed into `owasp.yaml`: `CWE-116` (output-encoding companion to CWE-79). Total added via external curation = **12** (11 Top 25 + 1 OWASP-derived).
- **Retrieval date**: **2026-04-17** (CWE Top 25 2025 page + per-CWE definition pages at `https://cwe.mitre.org/data/definitions/<N>.html`).
- **F-A1.2 restoration (Issue #185)**: **40 records** added 2026-06-11 — the T029 drift-edge targets, i.e. every CWE cited by the 67 crosswalk edges that Feature 180's T029 cleanup removed as endpoint-unresolvable. Names transcribed verbatim from the pinned MITRE corpus **cwec v4.20** (released 2026-04-30, retrieved **2026-06-11**; zip SHA-256 pinned in `specs/185-cwe-catalog-expansion/test-results/corpus-pin.md`). Abstraction note (record shape unchanged): **CWE-16, CWE-255, CWE-937, CWE-1035 are MITRE Categories and CWE-693 is a Pillar** — OWASP publishes these IDs directly in its official mappings (CWE-937/CWE-1035 were created by MITRE *as* OWASP Top Ten mapping anchors), and the catalog already carries abstraction precedent (CWE-284, itself a MITRE Pillar, is among the original 53). Status note (architect disposition, Issue #185): CWE-16 and CWE-937 carry v4.20 Status="Obsolete" — Obsolete ≠ Deprecated; both remain canonical, resolvable citation targets per the fidelity-first citation-resolution rationale.
- **Final record count**: **93** (53 original — 41 seed + 12 external-curation — + 40 F-A1.2 restoration; FR-017 floor ≥53 still satisfied).
- **Record-shape exception**: `cwe_refs` is **omitted entirely** on `cwe.yaml` records per FR-003 explicit exclusion — CWE→CWE relations (e.g., `ChildOf`, `CanPrecede`, superseded/related) live ONLY in `crosswalk.yaml`, never as per-record cross-references (per ADR-027 Decision 1).

### 3.6 `tachi-control-category.yaml`

- **Seed source**: `.claude/skills/tachi-control-analysis/references/control-categories.md` — FR-018 frozen 8-value enum. All 8 canonical categories verified at spec time 2026-04-17: `access-control`, `authentication`, `csp-security-headers`, `csrf-protection`, `encryption`, `input-validation`, `logging-audit`, `rate-limiting`.
- **External curation**: none (tachi pseudo-taxonomy — no external publisher).
- **Retrieval date**: **2026-04-17** (repo file at commit baseline; the canonical source lives in-repo).
- **Final record count**: **8** (FR-018 — exact).

### 3.7 `tachi-stride-ai-category.yaml`

- **Seed source**: `.claude/skills/tachi-shared/references/stride-categories-shared.md` — FR-019 frozen 11-value enum. 6 STRIDE categories (`spoofing`, `tampering`, `repudiation`, `information-disclosure`, `denial-of-service`, `elevation-of-privilege`) + 5 AI categories (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`), verified at spec time 2026-04-17.
- **External curation**: none (tachi pseudo-taxonomy — no external publisher).
- **Retrieval date**: **2026-04-17** (repo file at commit baseline; the canonical source lives in-repo).
- **Final record count**: **11** (FR-019 — exact).

### 3.8 `nist-ai-600-1.yaml`

- **Seed source**: external published catalog — **NIST AI 600-1** (Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, July 2024), DOI `https://doi.org/10.6028/NIST.AI.600-1`. Records are transcribed via the Surface C table of `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (authored via Feature 144 / ADR-025), names verbatim from the table per FR-024 transcription discipline. Added at **F-184** as the 8th catalog (ADR-027 Decision 3 extension — see the ADR-027 Revision History).
- **Record composition**: the **12 GAI Risks** of NIST AI 600-1 **§2.1–§2.12**, one record per section. All records share the DOI-anchored URL (same canonical-URL pattern as `nist-ai-rmf.yaml` in §3.4 — per-section anchors are not stable across NIST publication revisions).
- **id convention**: ids are **YAML-quoted strings** (`"2.1"` … `"2.12"`) — unquoted, `2.10` parses as the float `2.1` and collides with `"2.1"`. Records sort in **publication order** (section-numeric §2.1 → §2.12), enforced by the `_sort_key_section` branch of `test_records_sorted`.
- **`cwe_refs` rationale**: `cwe_refs: []` on all 12 records — **no CWE mapping exists for GAI risks** (NIST publishes no CWE cross-references in AI 600-1), so the field stays empty per the ADR-027 Decision 1 unidirectional rule (no inferred cross-references).
- **Retrieval date**: **2026-06-10** (DOI document + in-repo Surface C table verification).
- **Final record count**: **12** (F-184 contract C1 — exact).
- **Gap-row omission**: the two Surface C Gap rows are omitted from `crosswalk.yaml`. The **§2.6 row is endpoint-less** (no STRIDE+AI source category — an edge is un-formable). The **§2.9 × Spoofing row** is omitted because transcribing it would author the crosswalk's **first `low`-confidence edge** — against the F-182 anti-drift precedent (no `low`-padding; see §4.1) — for a row the source table itself tells auditors not to cite.

---

## 4. Confidence calibration rubric

Every edge in `crosswalk.yaml` carries a `confidence` field from the closed 3-value enum:

| Value | Criterion | Example |
|-------|-----------|---------|
| `high` | **Published cross-reference** — the authoritative source explicitly lists the target ID. | OWASP Top 10:2021 A03 (Injection) explicitly lists CWE-79 in its published "List of Mapped CWEs" — any A03→CWE-79 edge is `high`. (Note: OWASP **LLM** pages are prose-only for CWEs — see [§4.1](#41-related--superseded-calibration) caution.) |
| `medium` | **Inferred one-hop** — semantic match without explicit listing, but citable to one authoritative document. | LLM07 relates to CWE-20 ("Improper Input Validation") via category-semantic match documented in the OWASP LLM project README, not via LLM07's explicit CWE list. |
| `high` (NIST transcription) | Any edge derived from `nist-ai-rmf-mapping.md` Surface B or Surface C (verbatim transcription per FR-022). | `tachi-control-category:authentication → nist-ai-rmf:MEASURE-2.7` — Surface B real-mapping row. |
| `low` | **Two-hop or thematic** — curator judgment backed by a non-authoritative document (blog, research paper, internal analysis). | MITRE ATT&CK T1190 relates to OWASP API7 via adversary-objective alignment discussed in a security-research paper, not in any framework's published cross-reference. |

**Anti-drift rule** (verbatim, spec FR-013): **"if the curator cannot articulate a one-sentence citation supporting `high` or `medium`, downgrade to the weaker label."**

This rule inverts the default bias toward confidence inflation — the single most common failure mode in curated cross-framework mappings. The fallback is always `low` (still a valid, shippable value), so the rule does not create pressure to drop edges; it creates pressure to calibrate them honestly. See [ADR-027 Reason 3](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md) for the full rationale.

### 4.1 `related` / `superseded` calibration

> **Feature**: [182-crosswalk-related-superseded-edges](../../specs/182-crosswalk-related-superseded-edges/spec.md) (F-182, BLP-05 Wave 3) — first tranche of `related` edges.

The §4 table and the verbatim anti-drift rule above govern **every** edge type, including `related` and `superseded`. This subsection extends them with per-source-class calibration so a future author can classify a new `related`/`superseded` candidate from the README alone, without re-deriving the methodology — and without falling into the OWASP-LLM→CWE drift trap.

F-182 authored **37 `related` edges** (22 `high` / 15 `medium`) and **0 `superseded` edges**, drawn from four audited published source classes. The achievable `high`/`medium` floor was **37, not the ≥80 target** — the yield-tripwire fired (see "Yield-tripwire outcome" below). Calibrate against these four classes:

| Source class | Authoritative source | Published cross-ref? | `high` rule | `medium` rule | F-182 yield |
|---|---|---|---|---|---|
| **CWE ↔ CWE** | `cwe.mitre.org/data/definitions/<N>.html` (Relationships, with View context) | Yes (view-dependent) | Hierarchical relation (`ChildOf`/`ParentOf`/`PeerOf`) published in the canonical **Research view (View-1000)** — often corroborated across View-1000/1003/1305/1340 | The SAME relation appearing **only** in the Development view (View-700) or a concept view (View-1340), OR a **chaining** relation (`CanFollow`/`CanPrecede`) — weaker/context-specific | **22** (16 high / 6 medium) |
| **OWASP-Web Top 10 → CWE** | `owasp.org/Top10` per-category "List of Mapped CWEs" | Yes (explicit counted list) | `high` by construction (the category page explicitly lists the CWE) | n/a (the list is explicit, so no inference needed) | **0** — see note below |
| **ATLAS → ATT&CK** | `mitre-atlas/atlas-data` `ATLAS.yaml`, `ATT&CK-reference` field | Yes (first-class field) | `high` by construction (explicit published ID cross-reference) | Reference cites a **base** technique but the edge targets a **sub**-technique (one-hop inference) — see the T0016 worked example | **7** (6 high / 1 medium) |
| **OWASP-LLM Top 10 → ATLAS** | `genai.owasp.org/llmrisk/...` "Related Frameworks" list | Partial (relates frameworks, not a hard ID cross-reference) | n/a — the page relates the frameworks but does not publish it as a hard ID cross-reference, so `high` is not reached | Inferred one-hop from the "Related Frameworks" list | **8** (0 high / 8 medium) |

> **2026-edition note (F-362)**: the OWASP-LLM→ATLAS calibration basis above is a **2025-edition artifact**. The 2026 edition currently publishes a single release resource (`https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/`) with **no per-category "Related Frameworks" sections**, and 8 of the 18 `owasp:LLM* → mitre-atlas` edges now cite that interim URL — a re-anchoring that orphans the per-entry evidentiary chain (acknowledged in `specs/362-remap-owasp-llm-top10-2026/crosswalk-disposition-ledger.md`, row 72). The `medium` ceiling for those 8 edges therefore rests on the 2025-edition per-entry lists they were originally calibrated from, pending re-verification against 2026 per-entry pages when OWASP publishes them (tracked with the URL re-anchor work in follow-up F-362b, #364).

**Worked example per source class** (each traces to a real F-182 edge — confidence labels are exactly those authored):

- **CWE↔CWE** — `CWE-20 PeerOf CWE-345` published in **View-1000** → **`high`** (`citation: …/20.html (CWE-20 PeerOf CWE-345, View-1000)`). Contrast `CWE-117 ChildOf CWE-20` appearing **only in View-700** → **`medium`** (Development-view-only), and `CWE-770 CanFollow CWE-20` (a **chaining** relation) → **`medium`** (context-specific). Same `CWE-20`, three different confidence outcomes driven by **view + relation Nature**.
- **OWASP-Web→CWE** — methodology: the OWASP Top 10:2021 per-category "List of Mapped CWEs" → `high` **by construction**. F-182 yielded **0** here *not* because the lane is weak, but because **F-180 already authored every in-catalog OWASP-Web→CWE cross-reference as a `primary` edge** — there was nothing left to add as `related`. This is the lane to mine first when the OWASP-Web catalog is expanded; today it is exhausted.
- **ATLAS→ATT&CK** — `AML.T0016 → T1588` via the `ATT&CK-reference` field → **`high`** (explicit published cross-reference). The companion `AML.T0016 → T1588.002` was authored **`medium`**: the published reference cites the **base** technique `T1588`, not the sub-technique `T1588.002`, so targeting the sub-technique is a one-hop inference. **This high→medium pair is the canonical downgrade-discipline example** — the T005 anti-drift audit demoted it from `high` precisely because the citation supports only the base ID.
- **OWASP-LLM→ATLAS** — `LLM01 → AML.T0054` from the LLM01 page's "Related Frameworks" list → **`medium`** (inferred one-hop). The page *relates* the frameworks but does not publish it as a hard ID cross-reference, so it never reaches `high`. All 8 edges in this class are `medium` for this reason.

#### The CWE View-ID rule (FR-006)

CWE parent/child relations are **view-dependent**: the same CWE has different parents under **View-1000 (Research)**, **View-700 (Development)**, and concept views like **View-1340**. A CWE↔CWE citation **MUST record both the relationship Nature and the View ID** — e.g., `CWE-117 ChildOf CWE-20, View-700`. The View governs confidence: **Research View-1000 is `high`-eligible**; Development-only or concept-only relations are `medium`. Without a View ID a CWE↔CWE relation is **uncalibratable**, and two correct citations from different views can look like a contradiction (they are not — they are different views of the same weakness).

#### OWASP-LLM→CWE caution — the drift trap (FR-004)

OWASP **LLM** risk pages are **prose-only** for CWE references. Confirmed live against the **2025-edition per-entry pages** (the 2026 edition publishes no per-entry pages yet — see the 2026-edition note in §4.1): **9 of the 10 LLM pages published no structured CWE list; only the category now keyed LLM06:2026 (Unbounded Consumption) listed `CWE-400`.** Blogs widely repeat mappings like "LLM10 → CWE-79/89/78," but OWASP itself publishes no structured CWE cross-reference on the LLM pages. Therefore:

- Any **OWASP-LLM→CWE** edge is inferred-from-prose → `low`/inferred, and is **hard-excluded from the `high`/`medium` floor count**.
- This is why F-182 authored **0** OWASP-LLM→CWE edges.
- Contrast this **sharply** with **OWASP-Web→CWE**, which *is* a `high`-confidence lane by construction (the explicit "List of Mapped CWEs" on each Top 10:2021 category page). The asymmetry is the single most important calibration fact for a future author: *Web → CWE is structured and `high`; LLM → CWE is prose and `low`.*

#### `superseded` edge calibration (FR-007 / FR-008)

A `superseded` edge expresses old-item → newer-item lineage and is authorable **only where both endpoints already resolve under the current catalogs**. When authorable, a published deprecation/replacement relation with both endpoints in-catalog → **`high`**. F-182 authored **0** `superseded` edges: the locked catalog snapshot holds **current editions/revisions only**, so the *old* endpoint of any supersession is, by construction, absent. The four deferred classes (OWASP edition-revision lineage, deprecated ATT&CK techniques, ATLAS renames-not-supersessions, deprecated CWEs) are recorded with their follow-ons in [`specs/182-crosswalk-related-superseded-edges/deferred-superseded.md`](../../specs/182-crosswalk-related-superseded-edges/deferred-superseded.md). An empty authored set with documented deferral is an **acceptable outcome**, not a failure — the method is documented here even though the authored set is empty.

#### Authoritative-source list (canonical published source per class)

| Source class | Canonical published source | Verification note |
|---|---|---|
| CWE↔CWE | `https://cwe.mitre.org/data/definitions/<N>.html` (CWE relationships, **with View context**) | Citation records **Nature + View ID** (FR-006) |
| OWASP-Web→CWE | `https://owasp.org/Top10` per-category "List of Mapped CWEs" | Explicit counted list → `high` by construction |
| ATLAS→ATT&CK | `mitre-atlas/atlas-data` `ATLAS.yaml`, `ATT&CK-reference` field | `atlas.mitre.org` technique pages **404 via automated fetch** (anti-bot) — `atlas-data` is the verification source |
| OWASP-LLM→ATLAS | `https://genai.owasp.org/llmrisk/...` "Related Frameworks" | Inferred one-hop → `medium` ceiling (2025-edition per-entry basis — see the 2026-edition note in §4.1; the interim 2026 URL has no per-category lists) |
| OWASP-LLM→CWE | *(none authoritative — prose-only)* | Hard-excluded from `high`/`medium` (FR-004); `low`/inferred only |

#### Yield-tripwire outcome — expect a documented floor, not a mandatory 80

The FR-002 build-start survey found the achievable `high`/`medium` core was **37**, below the ≥80 target band. Per the anti-drift rule, the floor was committed at **37 with NO `low`-padding** to reach 80 — **anti-drift over floor-hitting**. The cause was structural: OWASP-Web→CWE yielded 0 (F-180 exhausted it as `primary`), and the 542-edge primary graph already captured the densest relationships, leaving only beyond-primary edges. The lone `medium` in the ATLAS→ATT&CK class is the T0016 sub-technique downgrade described above. **A future author should treat the 80 target as a band, not a quota: a documented-floor outcome (committed achievable count + written tripwire rationale) is the correct result when the high/medium yield falls short — never pad with `low` edges.** The full survey (per-class yield, tripwire state, the downgrade audit note) is captured in [`specs/182-crosswalk-related-superseded-edges/reference-edges.yaml`](../../specs/182-crosswalk-related-superseded-edges/reference-edges.yaml).

---

## 5. Canonical-URL conventions

| Framework | Catalog YAML | URL pattern |
|-----------|--------------|-------------|
| MITRE ATT&CK | `mitre-attack.yaml` | `https://attack.mitre.org/techniques/T<N>/` (e.g., `https://attack.mitre.org/techniques/T1190/`) |
| MITRE ATLAS | `mitre-atlas.yaml` | `https://atlas.mitre.org/techniques/AML.T<NNNN>` (e.g., `https://atlas.mitre.org/techniques/AML.T0058`) |
| CWE | `cwe.yaml` | `https://cwe.mitre.org/data/definitions/<N>.html` (e.g., `https://cwe.mitre.org/data/definitions/89.html`) |
| NIST AI RMF 1.0 | `nist-ai-rmf.yaml` | `https://doi.org/10.6028/NIST.AI.100-1` (DOI-based; single canonical document URL per Subcategory record) |
| OWASP LLM Top 10:2026 | `owasp.yaml` | `https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/` (single document URL shared across LLM01–LLM10; per-item anchors not yet published for the 2026 edition) |
| OWASP Top 10:2021 | `owasp.yaml` | `https://owasp.org/Top10/2021/A<NN>_2021-<slug>/` |
| OWASP API Security Top 10:2023 | `owasp.yaml` | `https://owasp.org/API-Security/editions/2023/en/0xa<N>-<slug>/` |
| OWASP Mobile Top 10:2024 | `owasp.yaml` | `https://owasp.org/www-project-mobile-top-10/2024-risks/m<N>-<slug>` |
| OWASP ML Security Top 10:2023 | `owasp.yaml` | `https://owasp.org/www-project-machine-learning-security-top-10/docs/ML<NN>_<year>-<slug>` |
| OWASP Agentic Top 10:2026 | `owasp.yaml` | `https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` (single document URL shared across ASI01–ASI10; per-item anchors not stable in the 2026 publication) |
| tachi pseudo-taxonomies | `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml` | Repo-relative path to canonical source reference (e.g., `.claude/skills/tachi-control-analysis/references/control-categories.md`) |

Link-rot monitoring for external URLs is now **live** via the weekly scheduled workflow `.github/workflows/tachi-citation-linkrot.yml` (checker `scripts/check-citation-urls.py`; Issue #183, BLP-05 Wave 3). It probes every external citation URL out-of-band on a schedule and maintains a single self-healing tracking issue (opened when confirmed link-rot appears, updated in place, and auto-closed once all citations are healthy again). The integrity test (`test_citation_shape()` per FR-031) remains regex-only — it verifies URL syntax and performs **no HTTP fetch** (ADR-021 determinism). The live network probe is confined to the scheduled workflow and never runs on the PR / `pytest` path (NFR-001).

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

When NIST AI RMF 2.0 publishes (or the `airc.nist.gov` Playbook pages add/remove Subcategories in the 1.0 lineage): re-harvest the full Subcategory catalog from the authoritative Playbook pages, verify count changes from 72, record the new retrieval date in §3.4, and **re-verify** the Surface B/C transcriptions in `crosswalk.yaml` against the updated `nist-ai-rmf-mapping.md`. Count drift from primary-source expansions is a **FR-024 primary-source correction** (amend the spec to match the authoritative count, do not descope the catalog) — this is the same discipline applied to the 68 → 72 amendment at SHA `9da377c` documented in §3.4. Changes to Surface B/C content MUST go through an ADR-025 amendment Issue per spec FR-024 — F-A1 remains a transcription feature, not a re-authorship feature.

---

## 7. Crosswalk methodology

`crosswalk.yaml` was composed from primary-only edges in F-A1 (per spec FR-025). The `related` and `superseded` edge types were **authorized in the schema but unused at F-A1 merge**, reserved for a follow-on. That follow-on has now begun: **F-182 (BLP-05 Wave 3) authored the first tranche of 37 `related` edges** (22 `high` / 15 `medium`, drawn from four audited published source classes) and **0 `superseded` edges** (catalog-gated — see the deferral disposition). The primary-edge methodology below is unchanged and still governs the 608 `primary` edges (post-F-185 composition: **608 `primary` / 37 `related` / 0 `superseded` = 645 edges** — 15 Surface C edges added and 16 drift edges removed at F-184, then the 67 T029 CWE-blocked edges restored byte-exact at F-185 against the expanded 93-record `cwe.yaml`); for `related`/`superseded` authoring and confidence calibration, see [§4.1 `related` / `superseded` calibration](#41-related--superseded-calibration).

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
