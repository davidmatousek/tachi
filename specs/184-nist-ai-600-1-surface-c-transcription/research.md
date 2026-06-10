# Research Summary: NIST AI 600-1 Surface C Transcription (F-184)

**Date**: 2026-06-10 | **Branch**: `184-nist-ai-600-1-surface-c-transcription` | **PRD**: `docs/product/02_PRD/184-nist-ai-600-1-surface-c-transcription-2026-06-10.md` (v1.2, Triad-approved)

Four parallel research lanes (KB, codebase, architecture, web) + direct reads of the binding Triad review records (`.aod/results/architect.md`, `.aod/results/team-lead.md`).

---

## Knowledge Base Findings

- **KB Entry 13 (F-186, MITRE expansion)** — `docs/INSTITUTIONAL_KNOWLEDGE.md` lines ~521–548: extract recovery/reference sources to checked-in artifacts BEFORE editing; keep human-auditable annotations out of the byte-exact insertion payload. *F-184 analog: the FR-3 15-pair and FR-7 16-edge lists are already pre-enumerated in the PRD — no extraction artifact needed.*
- **KB Entry 14 (F-182, related/superseded edges)**: for pure-data changes, reuse the existing integrity suite as the acceptance oracle (no new tests); commit documented floors, never pad. *F-184 analog: fixed-count contract (15 add / 16 remove), no yield uncertainty.*
- **F-180 process patterns** (`specs/180-taxonomy-crosswalk-collection/{spec,plan,tasks}.md`):
  - Catalog authoring grain: **one task per catalog YAML, one commit per file**.
  - Edge batching: ~50 edges per commit to avoid pre-commit hook (gitleaks) timeout (Risk R8). *F-184's 15 additions + 16 removals are far below the threshold — single-commit edge change-set is safe.*
  - Test discipline (T029 precedent): **fix the YAML, never the test** when integrity fails.
  - ID-format gotchas normalized at T029: NIST `MEASURE 2.7` (space, not dash); STRIDE slugs `info-disclosure` / `privilege-escalation` (canonical short forms — FR-3 table already uses them).

## Codebase Analysis

### `tests/schemas/test_taxonomy_integrity.py` (the single enum enforcement point — verified)
- `CATALOG_FILENAMES` lines 13–21 (7 files); `TAXONOMY_ENUM` lines 23–31 (7 stems).
- `_sort_key_nist` lines 63–77 — docstring "Numeric-within-function sort key so `MEASURE 2.2` precedes `MEASURE 2.10`"; **cannot parse space-less `2.X` ids** (falls back to string sort) → separate `_sort_key_section` is required (OQ-1/C4 ruling).
- Catalogs fixture docstring line 82: `"Load all 7 catalog YAMLs once. ..."` → stale at 8.
- Assert strings lines 241 + 245: `"not in 7-value enum ..."` → stale at 8.
- `test_records_sorted` lines 288–304 — dispatch: `if filename == "nist-ai-rmf.yaml": key=_sort_key_nist else: lexicographic`; its docstring (line 289) names the sort branches → needs the new branch named.
- 5 test functions: `test_framework_yamls_load` (shape, unique ids, URL regex-or-repo-file), `test_crosswalk_loads` (parse, no dup `{source,target,edge_type}` triples, `PRIMARY_EDGE_FLOOR = 500`), `test_crosswalk_referential_integrity` (closed enum + endpoint resolution), `test_citation_shape` (URL-shaped or repo file exists; no HTTP per ADR-021), `test_records_sorted`.
- **Architect M1×C4 normative stale-string inventory** (binding, `.aod/results/architect.md` lines 47–54): (1) fixture docstring L82 — update; (2) `test_records_sorted` docstring L289 — update to name new branch; (3) assert strings L241/L245 — update; (4) NEW `_sort_key_section` docstring — author; (5) **`_sort_key_nist` code AND docstring — byte-untouched**.

### `schemas/taxonomy/` (7 catalogs + crosswalk + README)
- Shape template: `nist-ai-rmf.yaml` — `{id, full_id, name, url, cwe_refs: []}`, shared DOI `https://doi.org/10.6028/NIST.AI.100-1` (FR-033 convention), house-style header (~44 lines: composition, shape, cwe_refs rationale, URL pattern, ID format, sort convention, amendment notes).
- `crosswalk.yaml`: header lines 1–8 carries enums + count line "542 primary + 37 related + 0 superseded" → update to 541/37/0. Edge shape `{source:{taxonomy,id}, target:{taxonomy,id}, edge_type, confidence, citation}`.
- **16 drift edges located**: region ~lines 1751–1869 (T016 Batch 5 block; 2 more in Day-1 Slice 4 region). Architect's fresh YAML parse (HEAD `f57a9c1`) verified **exactly 16** `tachi-stride-ai-category → nist-ai-rmf` edges, pair-level 1:1 vs FR-7 list, all primary/high. Removal should be executed by **filter on the edge class** (source.taxonomy + target.taxonomy), not by line ranges.
- Surface B edges (`tachi-control-category → nist-ai-rmf`, 27 edges incl. ~lines 1661–1750) — **stay untouched**.
- Crosswalk EOF region carries a Surface-C-deferred comment (~lines 2002–2005) noting §2.X ids absent from the 7-value enum — supersede/remove when transcription lands.
- Catalog counts on disk: owasp 60, mitre-attack (large), mitre-atlas 36, nist-ai-rmf 72, cwe 53, tachi-control-category 8, tachi-stride-ai-category 11 (all 9 FR-3 source ids verified present by Team-Lead).
- `README.md`: §1 snippet tuple of 7 stems (lines ~26–41); §2 harvest bullet 3 (line 59) — **stale**: says "every Surface C Overlap row (14) ... transcribed ... as 41 edges" (F-180 pre-deferral text; actual count 15, Surface C never shipped) → FR-5 §2 amendment note corrects the narrative; §3.1–§3.7 provenance subsections (new §3.8 follows the pattern; §3.4 nist-ai-rmf is the closest model); confidence rubric line 136 already names "Surface B or Surface C" for `high` NIST transcription (no change); FR-024 correction-routing paragraph at line 269; edge-type composition statement lines ~241–251 → 541/37/0.

### Surface C source table (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`)
- Surface C table lines ~36–66: **15 Overlap rows / 2 Gap rows (§2.6 endpoint-less; §2.9×Spoofing) / 8 No-equivalent rows** — Team-Lead re-verified 15 Overlap 1:1 vs FR-3; Architect re-verified at HEAD.
- Audit-guidance line (~81) instructs citing Overlap rows for §§2.4, 2.9, 2.10, 2.12.
- Stale prose line (~70–72): "8 of 11 STRIDE+AI categories overlap" — table yields 9 → OQ-4 routes a one-line ADR-025 amendment note at delivery (never a silent edit here).

## Architecture Constraints

- **ADR-027** (`docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`): Decision 3 heading "### Decision 3 — 7-value `taxonomy` enum" (line ~81) closes the enum "for F-A1"; extension governed via ADR amendment; **the T027 Revision History entry pre-scopes exactly this follow-on** (8th enum value, `nist-ai-600-1.yaml` 12 records, 15 Surface C edges). Revision History has 4 entries — established amendment instrument (OQ-3 ruling: revision entry, NOT standalone ADR). Index blurb at `docs/architecture/README.md:54`.
- **ADR-025**: Surface C structure source; "8 of 11" prose lives in its companion reference; ADR-025 has no amendment-notes subsection yet (Revision History only, lines ~257–280) — the OQ-4 one-line note lands at delivery. Maintenance triggers (lines ~237–254) govern re-evaluation; no re-verification vs the NIST PDF in scope.
- **ADR-028**: 5-value `source_attribution` enum (`ADR-028-...md:100–108`) — **explicitly NOT extended** (Architect M2).
- **Sweep exemption (Architect C2)**: `docs/architecture/01_system_design/README.md` carries "7-value"/"7 catalog" statements (lines 21, 120) AND ships byte-identical inside `tests/fixtures/init-baseline-tree/`; `tests/scripts/test_init_sh_substitution.py` enforces byte-identity → **exempt from sweep**.
- Constitution III (backward compatibility): FR-7 removal framed as disclosed correction of defective shipped data (CHANGELOG + ADR-027 revision entry + PM re-sign carried by the PRD).

## Industry / External Research (light check — per PRD, external re-verification out of scope)

- NIST AI 600-1 July 2024 edition **still current** as of 2026-06-10 (no revision/withdrawal). DOI `https://doi.org/10.6028/NIST.AI.600-1` confirmed canonical. §2 confirmed = 12 GAI risks (2.1–2.12). Details: `.aod/results/web-researcher.md`.
- **Naming discrepancy (FR-024 routing observation)**: NIST's PDF titles §2.6 "Harmful Bias **and** Homogenization"; the in-repo Surface C table (the verbatim transcription source) and PRD FR-1 say "**or**". §2.6 is a Gap row (endpoint-less, never transcribed as an edge) but it IS a catalog record name. **Disposition**: FR-1's pre-enumerated names are the binding contract (transcribe the reference verbatim, "or"); the and/or nit routes with the OQ-4 ADR-025 amendment note at delivery — never a silent divergence from the reference.

## Recommendations for Spec

1. Encode the **M1×C4 normative stale-string inventory** verbatim in the test-surgery FR (architect ruling: plan/tasks MUST carry the inventory, not the literal PRD FR-2 sentence).
2. Use **541/578** everywhere (Team-Lead Q3 wave-gate figures 557/594 are stale v1.0 numbers — FR-7 changed the arithmetic).
3. Execute FR-7 removal as an **edge-class filter** (`source.taxonomy == tachi-stride-ai-category AND target.taxonomy == nist-ai-rmf`), verified by count (16) and pair-list match — not line-range surgery; also retire/supersede the EOF "Surface C DEFERRED" comment block in `crosswalk.yaml`.
4. Quote **all** §2.X ids — 12 catalog records + 30 edge endpoint references (float-coercion: unquoted `2.10` → `2.1`); pin the rule in the catalog header comment.
5. Ordering: catalog + test surgery land **before/with** the edge change-set (FR-3 + FR-7 as one coherent change-set) so integrity never breaks mid-sequence; single-commit edge change-set is safe (31 net edge lines ≪ the ~50-edge batching threshold).
6. Test invocation pinned to `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py` (default `python3` lacks pytest/pyyaml; baseline 5/5 in ~1s verified by Team-Lead).
7. README §3.8 should mirror §3.4's provenance pattern; §2 bullet-3 amendment corrects the stale "(14) → 41 edges" claim as part of the FR-5 note.
8. Record the §2.6 "and/or" observation for the delivery-time OQ-4 ADR-025 note; do NOT alter FR-1 names.
9. No new tests, no schema scripts, no web-researcher lane, no security-analyst lane (data-layer YAML — per Team-Lead Q3).
