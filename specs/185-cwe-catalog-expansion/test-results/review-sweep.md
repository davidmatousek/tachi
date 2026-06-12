# T017 Review Sweep — F-185 CWE Catalog Expansion (W2 Track 3)

**Executor**: code-reviewer | **Date**: 2026-06-11 | **Branch**: `185-cwe-catalog-expansion`
**Verdict**: PASS — Part A 46/46 no-return; Part B 1 stale hit fixed, 8 hits deferred to T018, 30 historical left as-is, 18 false positives.

---

## Part A — No-excluded-edge-returns check: **PASS (46/46)**

### Method

All counts derived by YAML parse (never grep-count, per T001/T013 erratum). Anchors:

| Blob | Ref | Edges | Role |
|---|---|---|---|
| source | `git show e58f247:schemas/taxonomy/crosswalk.yaml` | 551 | pre-T029 |
| control | `git show 991e1ee:schemas/taxonomy/crosswalk.yaml` | 438 | post-T029 |
| frozen-53 | `git show e6e0b29:schemas/taxonomy/cwe.yaml` | 53 records | extraction-time catalog (the live cwe.yaml the script saw at T005; live is now 93 — using live would misclassify) |
| pre-F185 | `git show 6369ca6:schemas/taxonomy/crosswalk.yaml` | 578 | parent of edge-insertion commit `9d0616d` |
| live | working tree `schemas/taxonomy/crosswalk.yaml` | 645 | post-W1-2 |

Full T029 removal set re-derived by **multiset subtraction** (Counter of full-content JSON keys, source − control): **113 instances** (= 551 − 438 ✓).

### Classification reconciliation (material methodology note)

The header's `1 other-drift + 20 non-CWE + 25 dedupe` exclusion line is **hardcoded prose** in `extract_restore_set.py` (emit section, lines 184–185), not computed output — only the 67-edge artifact filter is executable logic (content set-semantics: `content_key not in control_keys` AND cwe-target AND not-frozen). A pure content-semantics split of the residual 46 yields 10/22/14, NOT 1/20/25. The header split reproduces **exactly** under tuple-survival semantics, consistent with the script's own dedupe doctrine ("edges whose exact content survives in the control blob are dedupe collapses, NOT removals") extended to tuple level:

- **dedupe collapse (25)** = removed instance whose tuple `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` survives in control — **14** exact-content twins + **11** T029 remove-and-reauthor replacements (same tuple, re-authored confidence/citation already present in control)
- **other-drift cwe-target (1)** = tuple fully gone from control, cwe target in frozen-53: `mitre-attack:T1190 -> cwe:CWE-20`
- **non-CWE-target (20)** = tuple fully gone from control, non-cwe target (15 `mitre-atlas -> mitre-attack`, 5 `tachi-control-category -> nist-ai-rmf`)

Derived artifact class (67) content-matches committed `restored-edges.yaml` exactly (`_blocked_on` stripped). 67 + 1 + 20 + 25 = 113 ✓.

### No-return instrument and result

The invariant F-185 owns: **W1-2 inserted only the 67 artifact edges and nothing else.** Checked via the F-185 delta:

```
live(645) − preF185(578)  =  exactly the 67 artifact edges (content multiset)   ✓
preF185(578) − live(645)  =  ∅ (F-185 removed nothing)                          ✓
excluded-edge instances in delta (by content OR tuple): 0 of 46                 ✓
for all 46 excluded tuples: live tuple-count == preF185 tuple-count             ✓
artifact-in-live: 67/67 present, 0 duplicated                                   ✓
```

**Result: 46/46 excluded instances show NO RETURN via F-185.**

### Per-edge adjudication of live tuple occupancy

Literal tuple-absence from live holds mechanically for only **5/46** (the 5 `tachi-control-category -> nist-ai-rmf` removals: `error-handling->MEASURE 2.6`, `monitoring-alerting->MEASURE 2.7`, `monitoring-alerting->MEASURE 3.2`, `secrets-management->MEASURE 2.10`, `secrets-management->MEASURE 2.7` — content+tuple ctl=0 pre=0 live=0). The other **41/46** have a same-tuple live edge whose occupancy **pre-dates F-185** (tuple count identical at preF185 and live for every one). Provenance buckets:

| Bucket | n | Provenance | Resolution |
|---|---|---|---|
| Exact-content dedupe twin | 14 | Twin survived T029's collapse in control blob (991e1ee); content ctl=pre=live=1 | Per task caveat + script dedupe semantics: the SURVIVING twin legitimately exists; removed instance not re-duplicated (live multiplicity 1 ≤ control 1 for all 14) |
| T029 remove-and-reauthor | 11 | Replacement with same tuple, re-authored content, already in control blob — T029 itself swapped them (e.g. `owasp:A01->CWE-285`, `A02->CWE-522`, `A03->CWE-89`, `A07->CWE-287`, `A08->CWE-502`, `LLM02->CWE-200`, `LLM03->CWE-1395`, `LLM04->CWE-20`, `LLM05->CWE-79`, `ASI01->AML.T0061`, `ASI05->AML.T0058`); content ctl=0 but tuple ctl=1 | These are the W0-b header's reauthor-style "dedupe collapses"; occupancy is the T029 replacement, not a return |
| Intervening-feature re-add | 16 | 15 `mitre-atlas->mitre-attack` + `mitre-attack:T1190->cwe:CWE-20`; content ctl=0, pre=1 — entered via commit `93fbd17` = **F-186** (PR #321, "+16 edges 526→542", count matches exactly; verified `git log -S`) | Governed re-addition delivered 2026-06-07, four days before F-185's branch; not a return via F-185 |

The dedupe caveat in the task brief is resolved exactly as prescribed: removed dedupe instances whose tuples equal their surviving twins' tuples are classified via the extraction script's own semantics (survival = not a removal) and checked for re-duplication instead of mechanical tuple absence — **0 re-duplications found**.

Verifier: `/tmp/t017_part_a_v2.py` (transient; full stdout reproduced in `.aod/results/185-w2-track3.md`). Re-runnable from the pinned SHAs above.

---

## Part B — Stale-count grep sweep

### Command

```
grep -rnE "53 record|53-record|578" docs/ schemas/ --include="*.md" --include="*.yaml"
```

(specs/ excluded per task; docs/ and schemas/ contain no specs/ paths.) **57 hits across 12 files.**

### Classification summary

| Class | Hits | Action |
|---|---|---|
| (a) genuinely stale | 1 | **FIXED** (uncommitted — orchestrator bookkeeps) |
| (b) historical/lineage — correct as-is | 30 | left |
| (c) T018-owned | 8 | **DEFERRED to T018** (explicit list below) |
| false positive (pattern substring) | 18 | none |

### (a) FIXED — 1 hit

- **`schemas/taxonomy/README.md:254`** (§7 Crosswalk methodology): present-tense current-state claim *"still governs the 541 `primary` edges (post-F-184 composition: 541/37/0 = 578 edges...)"* — stale after W1-2 (T009 scoped to §3.5 records; T012 scoped to crosswalk header; §7 was covered by neither). **Fix applied**: now reads *"still governs the 608 `primary` edges (post-F-185 composition: **608 primary / 37 related / 0 superseded = 645 edges** — 15 Surface C edges added and 16 drift edges removed at F-184, then the 67 T029 CWE-blocked edges restored byte-exact at F-185 against the expanded 93-record cwe.yaml)"*. Numbers verified against live YAML parse (608 primary / 37 related / 645 total). NOT committed per track rules.

### (c) T018-DEFERRED — explicit and unambiguous list (orchestration rule C4)

T018 owns these surfaces; T017 made **no edits** to any of them:

1. **`docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md`** — 7 hits at lines **65, 127, 146, 150, 300, 367, 388**. All are "53-record `cwe.yaml`" / "catalog growth beyond 53 records (BLP-02 envelope candidate)" / "53 records UNCHANGED" claims woven into the ratified D-7 substitution-rule text. These are decision-time context now superseded by F-185 (catalog 93; 5/8 substitution CWEs now cataloged: 307/311/319/326/732). Per architect C3 (read `.aod/results/architect.md` restatement first): handle via the **D-7 annotation blockquote + Revision History row with prospective-only wording incl. the trigger-taxonomy clause** — do NOT rewrite the ratified lines in place. The 7 line anchors above tell the annotation where the superseded predicate appears.
2. **`docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md:355`** — the *"CWE substitution rule (ADR-037 D-7 inline extension)"* mirror paragraph ("absent from the 53-record `cwe.yaml` inventory", "catalog growth beyond 53 records is reserved for follow-on features in the BLP-02 envelope"). **ADR-037-adjacent**: it mirrors the exact D-7 predicate T018 is annotating. T018 should decide whether the D-7 annotation needs a matching one-line pointer here or whether ADR-037's Revision History suffices as the single authority (recommendation: pointer or deliberate leave, but decided in T018, not here). Note: `ADR-027:373` (F-184 Revision History entry, "542 → 541/37/0 = 578") is pure history — leave (class b, not deferred).
3. **`CHANGELOG.md`** — outside this sweep's grep scope (repo root, not docs//schemas/), listed for completeness: T018 owns the `feat(185)` entry; no count surfaces were checked or touched there by T017.

(`specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md` is also T018-owned but under specs/, outside this sweep's scope by instruction.)

### (b) Historical/lineage — correct as-is, left (30 hits)

| File | Hits | Why correct as-is |
|---|---|---|
| `docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md` (12: lines 34, 49, 66, 88, 90, 190, 192, 227, 246, 313, 318, 334) | 12 | F-185's own PRD: pre-feature baseline ("today's 578", "cwe.yaml 53 records") and expectation arrows ("578 → 645", "53→93") — point-in-time product record; expectations match delivered reality. T019 owns the v1.2 errata (different scope: FR-006/O-R-P); no count is wrong as authored. |
| `docs/product/02_PRD/184-nist-ai-600-1-surface-c-transcription-2026-06-10.md` (8) | 8 | F-184 PRD documenting its own 542→578 arithmetic — immutable historical record. |
| `docs/product/02_PRD/182-crosswalk-related-superseded-edges-2026-06-07.md` (3) | 3 | F-182 PRD — point-in-time record. |
| `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md:373` | 1 | F-184 Revision History entry ("moves 542 → 541/37/0 = 578") — revision history is history. |
| `schemas/taxonomy/crosswalk.yaml:25` | 1 | F-185's OWN provenance header line "(578 -> 645; ...)" — correct lineage arrow written by W1-2. (File is also a do-not-touch surface for this track.) |
| `schemas/taxonomy/crosswalk.yaml:3735` | 1 | F-180 Batch 8 (T024) authoring-time comment "All 20 edges are within the 53-record CWE catalog" — provenance of the authoring constraint; remains factually true (53 ⊂ 93). (Do-not-touch surface regardless.) |
| `docs/architecture/00_Tech_Stack/README.md:118` | 1 | "Edge composition **after F-184**: 541/37/0 = 578" + F-241-segment "beyond 53 records" — explicitly feature-anchored lineage in the per-feature stamped paragraph chain. **Deliver-flow note (not T018)**: `/aod.deliver` close-out appends the F-185 segment here per convention (cf. F-184 close commit `9580844`); flagged so it is not lost. |
| `docs/product/06_OKRs/README.md:3` | 1 | "Last Updated" delivery-log entry for F-184 (=578 outcome) — historical log; deliver flow prepends the F-185 entry at close. |
| `docs/product/05_User_Stories/README.md:3` | 1 | Same pattern — F-184 delivery log. |
| `docs/product/02_PRD/INDEX.md:3` | 1 | "Last Updated" PRD-185-approval entry ("0 collisions vs current 578; expected 53→93, 578→645") — correct at approval time; deliver flow updates at close. |

### False positives — 18 hits

- `schemas/taxonomy/mitre-attack.yaml` (18 hits, lines 3754–3792): ATT&CK technique family **T1578**/T1578.001–.005 ids, `full_id`s and URLs — "578" substring matches, not count-bearing. No action.

### Sweep arithmetic

18 false-positive + 1 fixed + 30 historical + 8 T018-deferred = **57/57 hits classified**.

---

## Rules compliance

- Files edited: `schemas/taxonomy/README.md` only (1 line; .md — not `schemas/taxonomy/*.yaml` data). NOT committed.
- Untouched per rules: all `schemas/taxonomy/*.yaml`, `tests/`, `tasks.md`, `CHANGELOG.md`, ADR-037, `examples/` baselines, everything under `specs/` except this file. No pytest run. No commits.
- Working-tree baseline deltas observed in `git diff --stat` (6 `examples/*/security-report.pdf.baseline`) belong to T014 (parallel track) — not touched by T017.
