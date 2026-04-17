# Research Summary: F-A1 Taxonomy Crosswalk Collection (Feature 180)

**Created**: 2026-04-17
**PRD**: `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
**Research conducted during**: `/aod.spec` Step 2 (research phase) for branch `180-taxonomy-crosswalk-collection`

This document grounds the spec in codebase reality + validates the four PRD assumptions (A1–A4) before spec authorship.

---

## 1. Assumption Validation

### A1: Seed citation counts across 11 detection-patterns.md files — **PARTIAL VALIDATION**

PRD claimed: 38 ATT&CK techniques, 7 ATLAS techniques (including AML.T0058–T0062), 41 CWEs.

Grep findings (11 files, `.claude/skills/tachi-*/references/detection-patterns.md`):

| Taxonomy | PRD Claim | Actual | Status |
|----------|-----------|--------|--------|
| MITRE ATT&CK techniques | 38 unique | **38 unique** | ✓ MATCH |
| MITRE ATLAS techniques | 7 unique | **7 unique** (T0010, T0018, T0020, T0024, T0051, T0054, T0057) | ✓ count match |
| Unique CWEs | 41 unique | **41 unique** | ✓ MATCH |
| **AML.T0058–T0062 presence in detection-patterns.md** | must be present | **ONLY AML.T0058 in `finding-format-shared.md:229` (as example)** — AML.T0059/T0060/T0061/T0062 absent | ⚠ MISS |

**Resolution for spec**: The PRD's Success Criteria says "`mitre-atlas.yaml` contains ≥7 techniques and explicitly includes AML.T0058, T0059, T0060, T0061, T0062". The PRD's FR-4 wording ("7 unique MITRE ATLAS techniques currently cited (explicitly including AML.T0058–T0062)") is inaccurate against the current detection-patterns.md state. Spec will recategorize AML.T0058–T0062 as **external curation additions** (not seed citations). mitre-atlas.yaml target: **7 seed (T0010/T0018/T0020/T0024/T0051/T0054/T0057) + 5 externally-curated (T0058–T0062) = ≥12 records**.

**Full seed ID lists** (frozen at spec time per Assumption A1):

- **ATT&CK (38)**: T1005, T1039, T1068, T1070, T1070.001, T1070.002, T1070.004, T1070.006, T1070.008, T1078, T1078.004, T1195, T1195.001, T1195.002, T1213, T1213.001, T1213.002, T1213.003, T1213.005, T1498, T1498.001, T1498.002, T1499, T1499.001, T1499.002, T1499.003, T1499.004, T1530, T1548, T1548.001, T1548.003, T1548.005, T1550, T1550.001, T1556, T1562, T1562.006, T1565
- **ATLAS (7)**: AML.T0010, AML.T0018, AML.T0020, AML.T0024, AML.T0051, AML.T0054, AML.T0057
- **CWE (41)**: CWE-20, CWE-22, CWE-77, CWE-78, CWE-89, CWE-90, CWE-117, CWE-200, CWE-209, CWE-215, CWE-223, CWE-250, CWE-266, CWE-269, CWE-285, CWE-287, CWE-290, CWE-306, CWE-345, CWE-352, CWE-384, CWE-400, CWE-407, CWE-494, CWE-502, CWE-522, CWE-532, CWE-538, CWE-613, CWE-639, CWE-770, CWE-776, CWE-778, CWE-779, CWE-862, CWE-863, CWE-917, CWE-918, CWE-943, CWE-1333, CWE-1395

### A2: No ADR-025 amendment in flight — **VALIDATED**

ADR-025 Status: Accepted (2026-04-16). No pending amendment issue linked. Re-evaluation is trigger-based per ADR-025 Consequences (≥3 adopter machine-readable-tagging requests, NIST AI RMF 2.0 publication, or SP 800-53 AI Overlay GA — none currently fire). FR-6 verbatim-transcription contract is stable.

### A3: CWE Top 25 current year — **UPDATE REQUIRED**

CWE Top 25 **2025** is now current (published 2025-12-11 by MITRE/CISA). PRD references CWE Top 25 (2024). Spec targets **CWE Top 25 (2025)** per PRD Assumption A3 fallback ("the `cwe.yaml` Top 25 expansion targets the latest published list at merge time").

**2025 Top 25** (rank, ID, name):
1. CWE-79 XSS; 2. CWE-89 SQL Injection; 3. CWE-352 CSRF; 4. CWE-862 Missing Authorization; 5. CWE-787 Out-of-bounds Write; 6. CWE-22 Path Traversal; 7. CWE-416 Use After Free; 8. CWE-125 Out-of-bounds Read; 9. CWE-78 OS Command Injection; 10. CWE-94 Code Injection; 11. CWE-120 Buffer Overflow; 12. CWE-434 Unrestricted File Upload; 13. CWE-476 NULL Pointer Dereference; 14. CWE-121 Stack Buffer Overflow; 15. CWE-502 Deserialization of Untrusted Data; 16. CWE-122 Heap Buffer Overflow; 17. CWE-863 Incorrect Authorization; 18. CWE-20 Improper Input Validation; 19. CWE-284 Improper Access Control; 20. CWE-200 Exposure of Sensitive Information; 21. CWE-306 Missing Authentication for Critical Function; 22. CWE-918 SSRF; 23. CWE-77 Command Injection; 24. CWE-639 Authorization Bypass Through User-Controlled Key; 25. CWE-770 Allocation of Resources Without Limits

**Overlap with seed**: 13 of 25 already in seed (CWE-20, 22, 77, 78, 89, 200, 306, 352, 502, 639, 770, 862, 863, 918). **Net new CWEs from Top 25 (2025)**: 12 (CWE-79, 94, 120, 121, 122, 125, 284, 416, 434, 476, 787). Target `cwe.yaml` size: **41 seed + 12 net new = ≥53 records** (exceeds ≥50 PRD floor).

Source: https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html

### A4: Crosswalk edge authoring rate — **DEFERRED TO DAY 1 SPIKE**

Day 1 spike (50 edges, diverse slice) with 38.4s/edge tripwire is the validation mechanism per PRD Risk R1. Spec will pin the spike composition per Open Question Q6 resolution.

---

## 2. Codebase Patterns

### 2.1 Existing `schemas/` directory (10 files)

Files: `finding.yaml`, `attack-chain.yaml`, `report.yaml`, `infographic.yaml`, `security-report.yaml`, `risk-scoring.yaml`, `input.yaml`, `output.yaml`, `compensating-controls.yaml`, `coverage-checklists.yaml`.

**Conventions to adopt**:
- Header comment block declaring Producers / Consumers / Version
- Top-level `schema_version: "X.Y"` field
- ADR cross-references in comments for consequential changes
- Singular root objects (`finding:`, `chain:`, `report:`)
- `snake_case` IDs; `enum:` lists for closed value sets

### 2.2 Canonical seed source for pseudo-taxonomies

**tachi-control-category.yaml seeds** (8 records, from `.claude/skills/tachi-control-analysis/references/control-categories.md`):
`authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`

**tachi-stride-ai-category.yaml seeds** (11 records, from `.claude/skills/tachi-shared/references/stride-categories-shared.md`):
STRIDE (6): `spoofing`, `tampering`, `repudiation`, `information-disclosure`, `denial-of-service`, `elevation-of-privilege`
AI (5): `prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`

### 2.3 FR-6 Surface B / Surface C actual edge counts

Re-counted against `nist-ai-rmf-mapping.md`:
- **Surface B**: 27 real-mapping rows (all 8 control categories × relevant Subcategories; 0 "No equivalent")
- **Surface C**: 14 real-mapping rows (Overlap only; 8 "No equivalent" rows omitted; 2 "Gap" rows optionally omitted)
- **Total NIST-derived crosswalk edges**: **~41 edges** (PRD estimate was ~54; actual is ~13 lower)

**Distinct NIST Subcategories referenced**: 9 (GOVERN-1.4, GOVERN-1.6, MAP-4.2, MEASURE-2.6, MEASURE-2.7, MEASURE-2.8, MEASURE-2.10, MANAGE-1.3, MANAGE-2.4)

**NIST AI RMF 1.0 full Subcategory catalog**: **68 Subcategories** confirmed (across 4 Functions × 18 Categories per ADR-025 Context). PRD floor ≥68 matches full catalog enumeration.

### 2.4 Backward-compatibility test harness

**File**: `tests/scripts/test_backward_compatibility.py`
**6 baseline examples**: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference` (added in Feature 145)
**Convention**: `SOURCE_DATE_EPOCH=1700000000` per ADR-021; byte-identity cmp on generated PDFs

The spec's FR-9 backward-compat invariant requires this test to stay green. Since F-A1 is data-authoring only (no runtime script touch), byte-identity is automatic.

### 2.5 pytest harness (Feature 128 bootstrap)

- `pyproject.toml`: `[tool.pytest.ini_options]` with testpaths=["tests"], `--strict-markers`, `slow` marker
- `requirements-dev.txt`: pytest>=8.0, pytest-cov>=4.1, pyyaml>=6.0 (pyyaml is already declared — **resolves Open Question Q7**)
- `tests/conftest.py`: session-scoped `_load_hyphenated_script` helper
- **F-A1 adds**: `tests/schemas/__init__.py` + `tests/schemas/test_taxonomy_integrity.py`

### 2.6 ADR template & next number

`docs/architecture/02_ADRs/` contains ADR-000 (template) + ADR-001 through ADR-026 **with ADR-004 missing** (historically skipped/reserved — no existing ADR-004 file). The next unused sequential number is **ADR-027**. Filename convention: `ADR-NNN-kebab-case-title.md`.

**ADR-004 handling per PRD FR-10**: spec should not attempt to reclaim ADR-004 silently. ADR-027 is the committed target number.

---

## 3. Recommendations for spec.md

1. **Reframe FR-4 ATLAS seed**: acknowledge that AML.T0058–T0062 come from external curation (not seed citations). Spec FR-4 (mitre-atlas section) target: 7 seed + 5 external = ≥12 records.
2. **Update Top 25 target to 2025**: `cwe.yaml` floor ≥53 records (was ≥50 in PRD). Still satisfies PRD ≥50 floor.
3. **Tighten NIST edge count** per actual surface counts: ~41 NIST-derived edges (not ~54). Non-NIST edges must reach ≥459 primary edges to hit the ≥500 floor (was assumed ~446 non-NIST).
4. **Close Q7**: pyyaml is in requirements-dev.txt — no new dependency declaration needed.
5. **Pin Q6 (Day 1 spike composition)**: 10 OWASP↔CWE + 10 ATT&CK↔CWE + 10 ATT&CK↔ATLAS + 10 LLM↔NIST + 10 Agentic↔MITRE (PRD-recommended composition stands; no adjustment required unless first 5 edges reveal homogeneous-slice bias).
6. **Adopt existing schema conventions**: header block, `schema_version`, enum lists, snake_case IDs.
7. **Citation hygiene**: use canonical URL patterns documented in FR-8 to minimize rot probability; internal-path citations use paths relative to repo root (matches existing ADR cross-reference convention).

---

## 4. Knowledge Base references

No kb-query integration ran at spec time; relevant prior features for context:
- Feature 082 — threat-agent skill references refactor (source of the 11 detection-patterns.md files F-A1 seeds from)
- Feature 128 — pytest harness bootstrap (F-A1 extends via `tests/schemas/`)
- Feature 144 — NIST AI RMF documentation-only spike (FR-6 verbatim source)
- Feature 143 — OWASP AIVSS documentation-only spike (precedent for peer-framework publication without runtime wiring)
- Feature 145 — MAESTRO canonical worked example (precedent for additive-only content feature with zero runtime/schema touch)

---

**Research outcome**: The PRD is substantially accurate. Three spec-phase refinements are needed: (1) recategorize AML.T0058–T0062 as external curation, (2) target CWE Top 25 (2025), (3) tighten NIST edge count estimate from ~54 to ~41. These refinements do not affect PRD scope, Triad sign-offs, or the ≥500 primary-edge floor.
