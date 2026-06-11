---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-11
    status: APPROVED_WITH_CONCERNS
    notes: "FR-001..FR-008 all covered by W0→W1→W2; ACs reachable; no scope creep; all 3 PM spec-stage conditions correctly wired. D2 accepted (6 gated baselines — disclosure scope verified exact). D3 accepted (also the only no-schema-change option). NEW MED finding verified: main's byte-identity suite ALREADY RED from #186 mitre-atlas 30→36 latent drift — FR-006/W1-3 repairs red→green and absorbs the inherited ATLAS delta. Conditions folded into contract/quickstart/plan at plan stage: regen-contract expected-deltas amended, dual-attribute CHANGELOG, red pre-state recorded, KB process lesson queued. 1 MED + 2 LOW + 1 INFO. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-11
    status: APPROVED_WITH_CONCERNS
    notes: "All 4 ratifications granted: (1) FR-006/C2-interpretation — C2 scoped the D-7 annotation; catalog growth triggers the D-9 regen lane; (2) D2 6-baseline scope; (3) D3 in-scope records; (4) FR-030 wave sequencing + contracts. R1 empirically strengthened: suite FAILS on main today from latent #186 ATLAS drift (pdftotext attributes 100% of delta to ATLAS CA page; not typst drift) — FR-006 is required AND a repair. Central 67/40/0-collision derivation independently re-derived, exact match incl. #186 deferral pair, 34h/32m/1l, D-7 overlap {307,311,319,326,732}. ADR-027-untouched correct; D-7 blockquote+revision-row matches F-184 precedent; first-low-edge byte-exactness correct (0 low edges today); helper-script placement appropriate. 1 MED (contract deltas — folded) + 4 LOW (C2/C3/C5 folded at plan; rest at tasks); no re-review needed before tasks. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Branch**: `185-cwe-catalog-expansion` | **Date**: 2026-06-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/185-cwe-catalog-expansion/spec.md` (PM-approved 2026-06-11)
**PRD**: [docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md](../../docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md) (v1.1)

## Summary

Restore the 67 crosswalk edges Feature 180's T029 cleanup removed solely for missing CWE targets, by (1) architect-dispositioning the 40 missing CWE IDs against the pinned MITRE corpus, (2) inserting the add-set into `schemas/taxonomy/cwe.yaml` (53 → 93 expected), (3) restoring the edges byte-exact from dangling commit `e58f247` via an early checked-in restore-set artifact (578 → 645 edges expected), and (4) intentionally regenerating the 6 byte-identity-gated example report baselines whose Coverage Attestation pages render the CWE record count (spec FR-006, ADR-037 D-9 lane). Mechanism mirrors delivered sibling #186; no schema change, no new ADR, no production-code change — data, baselines, and documentation only.

## Technical Context

**Language/Version**: YAML 1.1 data files; Python 3 (`/usr/bin/python3`, repo-verified) for feature-local harvest/diff/extract scripts — no production code changes
**Primary Dependencies**: `pyyaml` + `pytest` (existing test toolchain), `typst` CLI (baseline regeneration, ADR-021 determinism), `git` (dangling-commit blob recovery), MITRE `cwec_v4.20.xml.zip` (pinned harvest corpus, released 2026-04-30)
**Storage**: flat YAML catalogs — `schemas/taxonomy/cwe.yaml`, `schemas/taxonomy/crosswalk.yaml`; restore-set artifact `specs/185-cwe-catalog-expansion/restored-edges.yaml`; 6 committed PDF baselines `examples/{name}/security-report.pdf.baseline`
**Testing**: `tests/schemas/test_taxonomy_integrity.py` (5 functions, ~1s, green at every data commit); `tests/scripts/test_backward_compatibility.py` (6-example byte-identity, `SOURCE_DATE_EPOCH=1700000000`); scripted all-40 name-diff vs the v4.20 XML (verification wave); full `pytest` at delivery
**Target Platform**: repo-local (macOS dev / Linux CI) — no runtime, no deployment
**Project Type**: single (data-catalog feature; documentation + data + baselines)
**Performance Goals**: integrity suite ≤ ~2s loop preserved; scripted harvest ≤ minutes (single ~50 MB zip download, no per-page fetching)
**Constraints**: FR-030 referential integrity at every intermediate commit (records before edges); FR-032 lexicographic string sort; ≥500-primary floor (541 → 608, never at risk); byte-exact edge restoration (`edge_type`/`confidence`/`citation` unmodified); CA-page-only baseline deltas (D-9); no test edits; no `cwe_refs` on CWE records (ADR-027 Decision 1)
**Scale/Scope**: 40 record dispositions; ≤40 record inserts; ≤67 edge restorations; 6 baseline regens; 7 documentation surfaces; 0 production scripts touched

**No NEEDS CLARIFICATION markers** — all unknowns resolved in [research.md](research.md) (spec-stage research + plan-stage decisions D1–D6).

## Constitution Check

*GATE: evaluated against `.aod/memory/constitution.md` (governance tier: standard). Re-checked post-Phase-1 — still passing.*

| Principle | Verdict | Evidence |
|---|---|---|
| I. General-Purpose Architecture | PASS | Catalog grows for all consumers; no example-specific or per-report special-casing. New records carry no `out_of_scope` flags (Decision D3 — honest coverage denominators). |
| II. API-First Design | N/A | No API surface; data contract (record/edge shapes) frozen per ADR-027. |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Monotonic data growth — consumers see more records/edges, never different shapes. The byte-identity suite is this principle's enforcement arm: FR-006 **restores it to green** via the D-9 intentional-regen lane (CA-page-only deltas) — plan review found it already red on main from inherited #186 ATLAS drift, which W1-3 absorbs and dual-attributes. |
| IV. Concurrency & Data Integrity | PASS | Single-writer repo workflow; FR-030 referential integrity enforced by test at every commit; dedupe re-check before insertion. |
| V. Privacy & Data Isolation | PASS | Public MITRE/OWASP identifiers only; no PII, no telemetry, local-first unchanged. |
| VI. Testing Excellence | PASS | Existing suites are the sole structural oracles (no test edits needed — verified: no exact-count assertions; attestation tests use synthetic fixtures). Name-diff script adds verification coverage for the one surface tests cannot see (record names). |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec SC-001..SC-006 + PRD DoD enumerated; `/aod.analyze` gate before delivery. |
| VIII. Observability & RCA | PASS | Decision trail: per-ID dispositions on Issue #185, provenance headers, lineage block, ADR-037 annotation. |
| IX. Git Workflow (NON-NEGOTIABLE) | PASS | Feature branch `185-cwe-catalog-expansion`; draft PR #328 open; conventional-commit title `feat(185):` set at creation. |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | PASS | PRD v1.1 Triad-approved → spec PM-approved (FR-006 delta explicitly PM-accepted, architect ratification requested at this plan review). |

**Violations requiring Complexity Tracking**: none.

## Project Structure

### Documentation (this feature)

```
specs/185-cwe-catalog-expansion/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Spec-stage research + plan Decisions D1–D6
├── data-model.md        # Record/edge/artifact/disposition entity model
├── quickstart.md        # Verification + regeneration runbook
├── contracts/
│   ├── restored-edges.schema.md      # Restore-set artifact contract (mirrors #186)
│   └── baseline-regen.contract.md    # D-9 regen recipe + CA-only-delta invariants
├── checklists/requirements.md        # Spec quality checklist (done)
├── restored-edges.yaml  # BUILD artifact — extracted W0, committed before data edits
├── scripts/             # BUILD artifacts — feature-local, no production caller
│   ├── harvest_cwe_names.py          # cwec_v4.20.xml → 40-ID name/type/status table
│   ├── extract_restore_set.py        # e58f247 blob diff → 67-edge restore-set
│   └── name_diff.py                  # inserted records vs harvest — 0-mismatch gate
└── tasks.md             # Task breakdown (/aod.tasks output — next step)
```

### Source Code (repository root)

```
schemas/taxonomy/
├── cwe.yaml             # +add-set records (53 → 93 expected), header provenance block
├── crosswalk.yaml       # +restored edges (578 → 645 expected), header lineage line
└── README.md            # §3.5 composition/count update

examples/                # 6 byte-identity-gated baselines regenerated (FR-006)
├── web-app/security-report.pdf.baseline
├── microservices/security-report.pdf.baseline
├── ascii-web-api/security-report.pdf.baseline
├── mermaid-agentic-app/security-report.pdf.baseline
├── free-text-microservice/security-report.pdf.baseline
└── maestro-reference/security-report.pdf.baseline

docs/architecture/02_ADRs/ADR-037-…md   # D-7 annotation (blockquote + revision row, docs-only)
specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md  # residual-resolved trail entry
CHANGELOG.md             # feat(185) entry
```

**Structure Decision**: single-project data feature. No `src/` changes — `scripts/extract-report-data.py`, templates, tests, and agents are all untouched. Feature-local helper scripts live under `specs/185-cwe-catalog-expansion/scripts/` (committed for reproducibility; regeneration-only tier, no production caller — house precedent).

## Phase 0: Research

Complete — [research.md](research.md) carries the spec-stage findings (KB/codebase/architecture/web, 4 parallel agents, 2026-06-11) plus the plan-stage decisions below. No open unknowns.

**Plan decisions (D1–D6)** — recorded in research.md with rationale/alternatives:

- **D1 — Harvest source**: pinned `cwec_v4.20.xml.zip` (comprehensive dictionary; includes all Categories/Pillars). Per-view CSVs REJECTED (omit Categories → false-reject CWE-16/255/937/1035); per-page scraping REJECTED as primary (40 fetches, R7-class risk) but retained as spot-check for 8 sentinel IDs.
- **D2 — Baseline regen scope = the 6 `BASELINE_EXAMPLES` only.** The 2 F-241 sample-report baselines (`predictive-ml-app`, `mobile-banking-app`) are explicitly excluded from byte-identity gating as "regeneration mutation targets" (test docstring) — no test compares their PDF bytes; regenerating them touches surfaces owned by other features' pipelines with zero gating benefit. Their CA pages go stale-by-design (already the documented status of those artifacts); noted in CHANGELOG. Alternative (regen all 8) REJECTED for blast-radius control. **Architect ratification requested.**
- **D3 — New records enter in-scope** (no `out_of_scope` keys): CA-page coverage percentages for the `cwe` framework drop honestly (denominator 53 → 93). Marking entering records out-of-scope to preserve percentages REJECTED as data falsification; the catalog's existing 53 carry no such flags either.
- **D4 — Helper scripts committed** under `specs/185-cwe-catalog-expansion/scripts/` for reproducibility (PRD's `/tmp/derive185.py` evidence script is re-homed as `extract_restore_set.py`). No production caller — consistent with the repo's regeneration-only script tier.
- **D5 — Extraction parallel to disposition** (W0 twin tracks): restore-set extraction is disposition-independent (team-lead C3); committing it first closes the dangling-object window (Risk 185.1).
- **D6 — Wave shape**: W0 (architect disposition ∥ extraction) → W1 (data: records → edges → baselines, strictly sequenced, integrity-green at each commit) → W2 (verification: name-diff ∥ review sweep; docs closure). Matches the PRD team-lead proposal with baseline regen appended to W1.

## Phase 1: Design & Contracts

Artifacts generated this phase:

- **[data-model.md](data-model.md)** — entities: CWE catalog record (shape, sort key, validation), crosswalk edge (tuple key, near-key, resolution rule), restore-set artifact (provenance header + working annotations stripped on insert), disposition record (per-ID verdict on Issue #185), CA baseline (regen inputs/invariants). State transitions: missing-ID → dispositioned → added; T029-removed edge → extracted → restored (or recorded-out per reject/defer).
- **[contracts/restored-edges.schema.md](contracts/restored-edges.schema.md)** — restore-set artifact contract mirroring `specs/186-mitre-catalog-expansion/contracts/restored-edges.schema.md`: header provenance (blob SHAs, filter definition, counts), edge entry shape byte-copied from blob, `_blocked_on` working annotation convention, strip-on-insert rule, byte-exactness verification method (field-level diff vs `git show e58f247:schemas/taxonomy/crosswalk.yaml`).
- **[contracts/baseline-regen.contract.md](contracts/baseline-regen.contract.md)** — per-example regen recipe (exact commands from the test body: `extract-report-data.py --target-dir … --output … --template-dir …` then `typst compile … --root .`, both under `SOURCE_DATE_EPOCH=1700000000`); D-9 invariants: deltas confined to Coverage Attestation pages (verified via per-page text-layer diff old-vs-new before commit), page count stable unless CA rows force pagination, byte-identity re-established by the suite against the new baselines; typst-version drift tripwire (Risk R6).
- **[quickstart.md](quickstart.md)** — runbook: run integrity suite, extract restore set, harvest names, run name-diff, regen + verify baselines, full-suite gate.

**Agent context update**: `.aod/scripts/bash/update-agent-context.sh` is absent in this repo (known gotcha — orchestrated runs skip it). No agent-context change needed: no new technology introduced.

## Implementation Approach (wave sequence → /aod.tasks)

| Wave | Owner | Work | Gate |
|---|---|---|---|
| **W0-a** | architect | Download + pin `cwec_v4.20.xml.zip`; scripted harvest of the 40 IDs (name, abstraction/type, status); publish 40-line add/reject/defer disposition on Issue #185 incl. Category/Pillar rationale (lead: add-all-40; none deprecated at v4.20) | Disposition comment live before any catalog/crosswalk edit |
| **W0-b** (∥ W0-a) | senior-backend-engineer | `extract_restore_set.py`: e58f247→991e1ee removed-set, filter `target.taxonomy==cwe ∧ target.id ∉ frozen-53` → exactly 67 edges; write `restored-edges.yaml` + schema contract; commit | Artifact committed (Risk 185.1 closed); 67/65+2 counts re-verified |
| **W1-1** | senior-backend-engineer | Insert add-set records into `cwe.yaml` (scripted lexicographic merge from harvest); header F-A1.2 provenance block (v4.20 + retrieval date + Category/Pillar annotations); README §3.5 | Integrity suite 5/5 |
| **W1-2** | senior-backend-engineer | Restore add-set-targeted edges from `restored-edges.yaml` (strip working annotations; byte-exact); exact-tuple + near-key dedupe re-check vs live crosswalk (0 required); crosswalk header lineage line | Integrity suite 5/5; counts 578→645 / 541→608 (add-all) |
| **W1-3** | senior-backend-engineer | Regenerate the 6 gated baselines per contract; per-page text diff old-vs-new → CA-page-only deltas (expected: cwe 53→93 + inherited mitre-atlas 30→36); restore `report-data.typ` after final run | `test_backward_compatibility.py` 6/6 green — **red→green flip** (main is 6/6 FAIL today from #186 latent drift); D-9 invariants hold |
| **W2-a** (∥ W2-b) | tester | `name_diff.py` all-40 vs harvest (0 mismatches); spot-check 8 sentinels (5 Cat/Pillar + 3 AI CWEs) on live pages; full pytest run | SC-002, SC-004, SC-005 evidence |
| **W2-b** | code-reviewer | No-excluded-edge-returns check (1 other-drift + 20 non-CWE + 25 dedupe stay out); stale-count grep sweep; byte-exactness field diff on restored edges | SC-003 evidence |
| **W2-c** | senior-backend-engineer | Docs closure: CHANGELOG `feat(185)` (dual-attributing the baseline regen: F-185 CWE + absorbed #186 ATLAS delta); ADR-037 D-7 annotation (prospective-only wording — emitted attributions to date used the substitutions correctly); F-180 NEXT-SESSION residual entry; PRD v1.2 errata (PM condition); KB process lesson (check `ORDERED_FRAMEWORKS` membership for any catalog-growth feature); Issue #185 disposition cross-link | FR-007 surfaces complete |

Sequencing invariants: W1-1 strictly before W1-2 (records before edges — FR-030 green at every commit); W1-2 before W1-3 (baselines capture final data); reject/defer outcomes from W0-a shrink W1 scope without rework (any add-set ⊆ 40).

## Risks (carried from spec/PRD + plan-new)

| # | Risk | L×I | Mitigation |
|---|---|---|---|
| 185.1 | Dangling commits GC'd before extraction | Low×High | W0-b extract-first commit (proven #186 pattern); verified present 2026-06-11 |
| 185.2 | Name contamination on harvested records (R7 mode) | Med×Med | D1 single-source v4.20 harvest; scripted all-40 name-diff (W2-a); 8-sentinel spot-checks; CWE-1039 rename case proves necessity |
| 185.3 | Category/Pillar policy reversal shrinks add-set | Low×Med | FR-001 lead posture with precedent rationale; plan handles add-set ⊆ 40; rejected-ID edges recorded, not dropped |
| 185.4 | Over-restore re-introduces T029 drift | Low×Med | 67-edge filter (never the 88/113 diff); named exclusions; W2-b no-return check |
| 185.5 | Crosswalk baseline shift between plan and build | Low×Low | W0-b re-derives from blobs + live file; collision check re-run at W1-2 |
| R6 (new) | Baseline regen drift beyond CA pages (typst version / environment) | Low×Med | Contract per-page text diff before commit; if non-CA deltas appear, halt and pin typst version to the one that produced current baselines (ADR-021); suite re-gates vs new baselines |

## Complexity Tracking

No constitution violations — table not required.
