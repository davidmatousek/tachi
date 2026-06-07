---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking. Full spec→plan traceability — all 15 spec FRs (FR-001..015) reachable in a named wave, no drops (built the full FR→wave matrix). Zero scope creep: every Out-of-Scope line held (no catalog expansion, no #183, no schema/test/ADR change, superseded remainder deferred), disjoint write-set confirmed (crosswalk.yaml + README.md + specs/182-* only). US1 (≥80 related floor, guaranteed deliverable) correctly modeled shippable independent of US2 (superseded, may be empty) + US3 (README rubric). Anti-drift-over-floor-hitting honored at every layer (W0 yield-tripwire → no low-padding pathway anywhere; FR-004 OWASP-LLM→CWE hard-excluded). Wave→FR mapping explicit + /aod.tasks-ready (matches PRD Team-Lead agent plan verbatim). Live-state verified: 542 primary/0/0, F-186 analog structure confirmed. 3 non-blocking observations: (1) W0 architect re-confirmation is belt-and-suspenders (not net-new analysis); (2) optional PRD v1.2 changelog one-liner for source-class audit (no amendment required); (3) deferred-superseded.md must ship even if superseded set=0 (plan handles correctly). Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking. All load-bearing claims re-verified PASS against live repo: 542 primary/0 related/0 superseded; 5 integrity functions; EDGE_TYPE/CONFIDENCE enums + PRIMARY_EDGE_FLOOR=500; test_records_sorted catalog-only (not the crosswalk); catalog counts cwe 53/atlas 36/attack 701/owasp 60; ADR-027 no-extra-keys freeze; PR #323 feat(182) draft. Constitution Check correct (PASS, no violations, no schema/ADR). Additive-only integrity STRUCTURALLY guaranteed — the reference-edges.yaml annotation-key-stripping design is backstopped by test_crosswalk_loads extras-forbidden assertions at both edge and endpoint level (a stray source_class/disposition key would fail the suite). Four-class source constraint technically correct + anti-drift-sound (OWASP-LLM→CWE demoted to low, View-ID rule for view-dependent CWE parents). Wave sequence sound: FR-002 yield-tripwire is a correct build-time gate (not a planning blocker); FR-014 anti-drift citation audit correctly separated from shape-only test_citation_shape (content vs structure). All PRD-stage concerns (C1 542-baseline, C2 sort-misattribution, C3 floor→80) resolved as recommended. 3 non-blocking observations; no residual technical gap before /aod.tasks. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Crosswalk `related` + `superseded` Edge Expansion — First Tranche (F-182)

**Branch**: `182-crosswalk-related-superseded-edges` | **Date**: 2026-06-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/182-crosswalk-related-superseded-edges/spec.md`
**Initiative**: BLP-05 Wave 3 (Crosswalk Integrity & Edges) · P2 (Light)

## Summary

Author the **first tranche of non-primary crosswalk edges** into `schemas/taxonomy/crosswalk.yaml`: a committed floor of **≥80 `high`/`medium`-confidence `related` edges** (band 80–150, 150 hard ceiling) harvested from four **audited published source classes** (CWE↔CWE, OWASP-Web→CWE, ATLAS→ATT&CK, OWASP-LLM→ATLAS), plus the `superseded` edges authorable under current catalogs (opportunistic; deferred remainder documented). A build-start survey validates achievable yield with a **yield-tripwire** (anti-drift over floor-hitting). The 5-function taxonomy integrity suite is the structural acceptance gate; an **anti-drift citation audit** is the content gate. Pure additive data change: **no schema change, no test change, no new ADR, no ADR-027 change; the ≥500 primary floor (542) is preserved.**

## Technical Context

**Language/Version**: Python 3.11 (test + tooling only; the feature payload is static YAML data)
**Primary Dependencies**: `pyyaml`, `pytest` (existing); web sources for harvest (cwe.mitre.org, owasp.org/Top10, genai.owasp.org, atlas-data)
**Storage**: static YAML — `schemas/taxonomy/crosswalk.yaml` (+ feature-local `reference-edges.yaml`)
**Testing**: `pytest tests/schemas/test_taxonomy_integrity.py` (5 functions; `5 passed` on `main`)
**Target Platform**: repo data files + CI (`tachi-pytest.yml`)
**Project Type**: single (data-layer change in the existing repo)
**Performance Goals**: N/A (static data; integrity suite runs ~1s)
**Constraints**: FR-010 referential integrity (inviolable); ADR-027 edge shape (no extra keys); `confidence` anti-drift rule; 5-tuple uniqueness; ≥500 primary-edge floor; harvest-don't-invent
**Scale/Scope**: +80–150 `related` edges; +0–k `superseded` edges (k may be 0); 542 primary edges unchanged
**Unknowns**: 1 — the exact achievable `high`/`medium` count and per-class composition. Modeled as a **build-start survey gate (FR-002)**, not a planning blocker; the plan tolerates a yield-tripwire outcome (documented achievable floor) without rework.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Rationale |
|-----------|---------|-----------|
| I. General-Purpose Architecture | PASS | Taxonomy data, not core logic; no new domain coupling. |
| II. API-First Design | N/A | No API/UI surface. The crosswalk *is* the machine-readable contract (consumed via existing SARIF/reports); shape unchanged. |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Purely additive non-primary edges; **no `schema_version` change**; consumers see more edges, never different shapes. Monotonic. |
| IV. Concurrency & Data Integrity | PASS (by-test) | Static YAML, no runtime state. `test_crosswalk_referential_integrity` + 5-tuple uniqueness are the data-integrity guarantees; never left dangling. |
| V. Privacy & Data Isolation | N/A | Public framework IDs + public authority URLs; no PII/secrets. |
| VI. Testing Excellence | PASS | The 5-function integrity suite is the structural oracle (FR-013); no new code paths. The anti-drift citation audit (FR-014) adds a content check, not a new test file. |
| VII. Definition of Done (NON-NEGOTIABLE) | DEFERRED | Satisfied at `/aod.deliver` (DoD checklist in spec/PRD). |
| VIII. Product-Spec Alignment (NON-NEGOTIABLE) | PASS | spec.md PM-approved (APPROVED); this command obtains plan.md PM + Architect dual sign-off. |
| IX. Git Workflow (NON-NEGOTIABLE) | PASS | On feature branch `182-crosswalk-related-superseded-edges`; draft PR #323 open. |

**Result: PASS — no violations. Complexity Tracking not required.**

## Project Structure

### Documentation (this feature)

```
specs/182-crosswalk-related-superseded-edges/
├── plan.md                          # This file (/aod.project-plan output)
├── spec.md                          # PM-approved specification
├── research.md                      # Authoritative-publication audit + Phase-0 decisions (D1–D6)
├── data-model.md                    # 5 entities (related edge, superseded edge, source class, ref-edges artifact, deferred-set)
├── quickstart.md                    # survey → author → verify (reproducible)
├── contracts/
│   └── reference-edges.schema.md    # harvest-artifact shape + 9-invariant integrity acceptance contract
├── reference-edges.yaml             # (build output, FR-012) checked-in harvest captured BEFORE crosswalk edit
├── deferred-superseded.md           # (build output, FR-008) per-class deferral rationale (exists even if authored set = 0)
├── checklists/requirements.md       # spec quality checklist (PASS)
└── tasks.md                         # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
schemas/taxonomy/
├── crosswalk.yaml        # +80–150 related edges, +0–k superseded edges (FR-001/007); header provenance note (FR-015)
├── README.md             # rubric extension: related/superseded calibration + source list + View-ID rule + OWASP-LLM→CWE caution (FR-009)
├── cwe.yaml              # UNCHANGED (53 records) — endpoint catalog only
├── mitre-atlas.yaml      # UNCHANGED (36) — endpoint catalog only
├── mitre-attack.yaml     # UNCHANGED (701) — endpoint catalog only
└── owasp.yaml            # UNCHANGED (60) — endpoint catalog only

tests/schemas/
└── test_taxonomy_integrity.py   # UNCHANGED gate (5 functions) — must stay green (FR-013)
```

**Structure Decision**: Single-project data-layer change. No new modules, services, or interfaces. New repo artifacts are the checked-in `reference-edges.yaml` (FR-012) and `deferred-superseded.md` (FR-008) under the feature's specs directory; the production payload is edits to `crosswalk.yaml` + `README.md` only (disjoint from #184/#185 catalog edits).

## Phase 0: Research

**Complete.** See [research.md](research.md) — an authoritative-publication audit of the candidate `related` source classes plus six Phase-0 decisions (D1–D6). Key resolved decisions:

- **D1 — four audited published source classes** carry the `high`/`medium` floor; OWASP-LLM→CWE is prose-only → `low`/excluded (drift trap). *Alternative rejected*: treating OWASP-LLM→CWE like OWASP-Web→CWE.
- **D2 — survey-first, spike-conditional floor with a yield-tripwire**; ≥80 (lowered from PRD v1.0's 120 because high-conf core ≈ 65). *Alternative rejected*: fixed pre-survey floor (risks padding or miss).
- **D5 — pure additive: no schema/test/ADR/ADR-027 change**; ≥500 primary floor untouched. *Alternative rejected*: extending the test to enforce a `related` floor (couples data volume to the structural gate).
- **D6 — CWE↔CWE citations record Nature + View ID** (parents are view-dependent).

The single remaining unknown (achievable yield) is a build-start survey gate (FR-002), not a planning blocker.

## Phase 1: Design & Contracts

**Complete.** Generated:
- [data-model.md](data-model.md) — 5 entities (related edge, superseded edge, audited source class, reference-edges artifact, deferred-set disposition) with shapes, validation rules, and the candidate-relation state machine.
- [contracts/reference-edges.schema.md](contracts/reference-edges.schema.md) — the `reference-edges.yaml` harvest-artifact shape + the 9-invariant integrity acceptance contract (structural suite + the FR-014 content audit).
- [quickstart.md](quickstart.md) — survey → harvest → author → verify, reproducible by any engineer.

**No API contracts** (data-layer feature; no endpoints). **Agent-context update**: `update-agent-context.sh` is absent in this repo (known) — skipped gracefully; no new technology to register.

**Post-design Constitution re-check: PASS** (design introduced no new violations; the two new artifacts are feature-local specs files, not production schema).

## Implementation Approach (wave sequence → /aod.tasks)

Sequenced per the PRD Team-Lead agent plan: no-migration gate first, survey/harvest before authoring, verify + anti-drift audit last. `/aod.tasks` finalizes agent assignments + parallel waves.

**Wave 0 — No-Migration Gate + Survey (architect, web-researcher)** *(blocks bulk authoring)*
- architect: re-confirm the additive-only posture (no schema/test/ADR/ADR-027 change) before any edit — the structural gate the Architect already verified at spec time.
- web-researcher: build-start **survey** (FR-002) of the four source classes against current catalog counts → compute achievable `high`/`medium` core. If core < 80, set the **yield-tripwire** → proceed with a documented achievable floor (no `low`-padding).

**Wave 1 — Harvest & Author (web-researcher ‖ senior-backend-engineer)** *(after Wave 0)*
1. FR-012: finalize the checked-in `reference-edges.yaml` harvest **first** (audit evidence base; authoring source). Harvest of a not-yet-authored source class can overlap authoring of an already-harvested one (the ‖).
2. FR-001/003/004/005/006: author the ≥80 (or floor) `related` edges into `crosswalk.yaml` — source-class-constrained, confidence-calibrated, CWE↔CWE citations carry Nature + View ID, annotation keys stripped on promotion. 0 `high`/`medium` from OWASP-LLM→CWE.
3. FR-007/008: survey `superseded` pairs; author the catalog-authorable set (may be 0); write `deferred-superseded.md` (per-class rationale, exists even if empty).
4. FR-013: run the integrity suite after each batch; keep 5/5 green.

**Wave 2 — Verify & Audit (tester, code-reviewer)** *(after Wave 1)*
- tester: 5/5 integrity green; `related` count ∈ [80,150] (or documented floor); `primary` still 542; 0 duplicates; all endpoints resolve.
- code-reviewer: **anti-drift citation audit (FR-014)** — every `high`/`medium` edge's citation supports its label (downgrade those that don't); 0 `high`/`medium` from OWASP-LLM→CWE; README rubric extension correct (FR-009); diff touches only `crosswalk.yaml` + `README.md` + specs artifacts (FR-011 no schema/test/ADR change).

**Close — Documentation (FR-015)**
- `crosswalk.yaml` header provenance note (F-186 convention); CHANGELOG `feat(182)` entry (BLP-05 F-3 sibling-h3 cluster); `/aod.analyze` clean; close Issue #182 `stage:done`.

## Risks (carried from spec/PRD)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Yield shortfall — high/medium core < 80 | Medium | Medium | FR-002 build-start survey + yield-tripwire → documented achievable floor; **no** `low`-padding (anti-drift). |
| Confidence inflation (drift) — `high` on weak citations | Medium | High | FR-014 anti-drift citation audit (code-reviewer) downgrades unsupported labels; FR-004 hard-excludes OWASP-LLM→CWE from high/medium. |
| #185 cwe.yaml expansion lands mid-flight → CWE pool shifts | Medium | Low | A1: author against a frozen catalog snapshot or sequence #182 after #185; disjoint write-sets limit collision to read-time. |
| Over-reach into catalog expansion (adding records to author more edges) | Low | Medium | FR-011 + Out-of-Scope: edges only against existing records; catalog expansion is Wave 2 (#184/#185). |
| Accidental primary-floor disturbance | Low | High | FR-011: only non-primary edges added; tester asserts `primary` == 542; `test_crosswalk_loads` enforces ≥500. |
| CWE view-ambiguity → contradictory-looking citations | Low | Low | FR-006: citations record Nature + View ID. |

## Complexity Tracking

*No Constitution Check violations — section intentionally empty.*
