---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-30
    status: APPROVED
    notes: "Faithful, scope-disciplined decomposition of the dual-approved plan. All 4 user stories (US1 catch-drift, US2 don't-false-red, US3 guard-trunk, US4 future-member) fully + independently delivered; all 8 FRs and 8 SCs map 1:1 to delivering+verifying tasks. Scope clean: (a)-deferral preserved (no task wires the full byte-identity suite into CI — T003 runs it locally only, T010 invokes only the fingerprint guard, T012 routes the rationale to ADR-037 D-14); OQ-6 init.sh xfail correctly a re-tag follow-up (T014, NOT a fixture regen); NFR-004 disjointness honored with the sole spec-authorized T003-red contingency in T007. Both carried Architect concerns encoded (C-2→T004, C-1→T012). All load-bearing claims re-verified @ 644b532. 0 blockers/critical/warnings. 3 LOW (no task change): analyze may note the deliberate 7→8 SC split; T014 issue # replaces #329 in the reason once filed (FOLDED into T014); don't broaden T006's regen loop beyond the 6 baseline dirs. Full: .aod/results/product-manager-tasks.md"
  architect_signoff:
    agent: architect
    date: 2026-06-30
    status: APPROVED
    notes: "Technically faithful decomposition, re-verified against the live tree (ORDERED_FRAMEWORKS@1077, loader@1089-1090, list(data)@1131, the loader's isinstance guard@1135, all 4 target artifacts absent, both CI pattern sources, the 6-example regen recipe, the OQ-6 xfail). Critical path T004→T005→T006→T007→T008 acyclic and correctly ordered; T003's verdict gates ONLY T007 (green→emit-from-tree / red→also regen), never T004/T005/T006. Same-file [P] discipline clean (T008/T009/T011 sequential on the test module; T004/T005/T006 sequential on the guard; T012/T013/T014 [P] disjoint). Determinism boundary leak-free — rendering confined to T003+T006/T007, never tests or CI. FR-007 cache_clear() in all 3 test tasks. T010 = maestro skeleton (single ubuntu-latest, contents:read, Py3.11) + pytest dual-trigger anchor (PR + push:[main]) with a complete path filter incl. the loader source. C-1 encoded YES (T012 = new D-14 + Revision-History + D-9 forward-pointer, NOT a D-9 rewrite). C-2 encoded YES (T004 mandates the isinstance(r,dict) guard; contract §2 implements it with the correct 'raw mode not isinstance-filtered upstream' nuance). 0 critical/warning; 2 LOW build-stage advisories (importlib spec_from_file_location mechanics; T006 same-file --emit sequencing — already serialized). Full: .aod/results/architect-tasks.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-30
    status: APPROVED_WITH_CONCERNS
    notes: "FEASIBLE_WITH_MODIFICATIONS. The 16-task breakdown is honest for an M (1.5 eng-day) feature, not padded: 5 net-new build artifacts (guard, regen script, test module, workflow), 3 [MANUAL-ONLY] rendering-gates (discrete because rendering is forbidden everywhere else — NFR-001), 3 docs/closeout, rest setup/deliver. Traces 1:1 to floor 1.0 / plan 1.5 / ceiling 3.0. Critical path T004→T005→T006→T007→T008→T010→T015→T016 correct and minimal; the only sequential same-file chain (T008→T009→T011) is unavoidable for one engineer. [P]/Track-A∥B intra-track disjoint-file only — no false cross-agent fan-out. T003 go/no-go front-loaded, gates ONLY T007, RED-path remediation bounded inside T007 as the ceiling-day driver (my C1/C2). All 3 [MANUAL-ONLY] tasks (T003/T007/T015) flagged. Load-bearing facts verified live; write-set disjoint (only #344 + release-please open). No timeline/capacity blocker. 3 LOW carry-forwards (all mitigated): C-A live xfail text is 'Pre-existing baseline-fixture staleness…' — read current before the optional T014 edit (FOLDED into T014); C-B FR-2 regen lane is the variance driver — watch T006/T007 wall-clock; C-C cache_clear present on every synthetic case. Full: .aod/results/team-lead-tasks.md"
---

# Tasks: ORDERED_FRAMEWORKS Catalog-Drift CI Guard

**Input**: Design documents from `specs/329-ordered-frameworks-ci-guard/`
**Prerequisites**: plan.md (PM+Architect approved), spec.md (PM approved), research.md, contracts/sidecar.contract.md, quickstart.md
**Feature**: #329 · BLP-06 Wave 2, CI-hardening-tail lead (P1) · Branch `329-ordered-frameworks-ci-guard`

**Tests**: AUTHORED here. FR-007 explicitly requires a synthetic unit test (the guard's entire value is trustworthiness) — so the test module is a deliverable, not pre-existing. No live PDF rendering in any test or CI path (NFR-001).

> **Definition of Done** (constitution VII):
> 1. ✅ Pushed to Production — guard merged to `main` (post-green, via devops) on PR + `push:[main]`.
> 2. ✅ Tested — `tests/scripts/test_catalog_drift_guard.py` green (live-tree gate + 6 synthetic cases) in the dedicated workflow.
> 3. ✅ User Validated — quickstart negative checks (probe drift → caught; citation-only edit → ignored); sidecar emitted by the regen script; guard green on a clean tree.

<!-- DOD-ACK -->

## Format: `[ID] [P?] [Story] Description`
- **[P]**: different files, no dependency on an incomplete task
- Include exact file paths

## Path Conventions
Single project (CI/CD tooling). Build surface at repo root: `scripts/`, `tests/scripts/`, `.github/workflows/`, `examples/`, `docs/architecture/02_ADRs/`.

---

## Phase 1: Setup

**Purpose**: Confirm preconditions before touching the tree.

- [X] T001 [P] Confirm preconditions in repo root: on branch `329-ordered-frameworks-ci-guard`; live refs present — `ORDERED_FRAMEWORKS` at `scripts/extract-report-data.py:1077` (`("owasp","mitre-attack","mitre-atlas","nist-ai-rmf","cwe")`) and `_load_framework_yaml_records(framework_name, in_scope_only=False)` `@functools.lru_cache` at `:1089-1090`; confirm NO existing `examples/ca-baseline-fingerprints.json` (this feature creates it).
- [X] T002 [P] Verify local verification deps: `python3 -m pip install 'pytest>=8' 'pytest-timeout>=2' 'pyyaml>=6'` (matches `tachi-pytest.yml`/`tachi-maestro-coverage.yml`); confirm `typst --version` is 0.14.2 (used ONLY by T003 + the regen script — never in CI).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The go/no-go gate + the shared fingerprint core that every user story depends on. **No user-story work that emits the sidecar or asserts the live tree can complete until T003's verdict is known and T004 exists.**

- [X] T003 Pre-state go/no-go gate (OQ-3 / Risk-4 — front-loaded to hour-zero): run `python3 -m pytest tests/scripts/test_backward_compatibility.py -q` locally and **record the literal pre-state totals** (KB-15). **GREEN** → proceed; the sidecar (T007) is emitted from the current tree and the guard goes green immediately. **RED** → a bounded baseline remediation (T007 also regenerates the 6 baselines via the new script, in this same change-set) precedes guard-green. Git evidence (F-185 `2aa1bf5` regenerated + absorbed #186's ATLAS delta; only count-neutral member edits since — #333) ⇒ green highly likely. **[MANUAL-ONLY]** local rendering check — CI never renders (NFR-001).
- [X] T004 Fingerprint core in `scripts/check-catalog-drift.py` (FR-001 / FR-004 + Architect C-2): `importlib`-load `_load_framework_yaml_records` + `ORDERED_FRAMEWORKS` from the hyphenated `scripts/extract-report-data.py` (the established loader-reuse pattern — never re-implement the YAML walk); `member_fingerprint(fw)` → `raw_fingerprint` + `in_scope_fingerprint` as `sha256` over the **ordered, never-sorted** list of canonical `[id, bool(out_of_scope)]` tuples (raw vs `in_scope_only=True`), **with an `isinstance(r, dict)` guard mirroring the loader so a non-dict record fails closed, not AttributeError (C-2)**, plus `raw_count`/`in_scope_count`; `all_fingerprints()` iterating `ORDERED_FRAMEWORKS` dynamically (FR-004). Shared by US1/US2/US4.

**Checkpoint**: T003 verdict recorded; fingerprint core importable. User stories can proceed.

---

## Phase 3: User Story 1 — Catch drift-without-regen → fail (Priority: P1) MVP

**Goal**: A live member whose render-coupled fingerprint ≠ its regen-emitted sidecar fingerprint makes the guard exit non-zero, naming the framework, expected-vs-actual, and the regen entry point — covering the F-186 grow, the constant-count ID-swap (HIGH-2), and the `out_of_scope`-flip (HIGH-3).

**Independent Test**: synthetic fixture — mutate a member's in-scope record set without re-emitting the sidecar → guard exits 1 naming the framework; no CI, no rendering.

- [X] T005 [US1] `--check` mode (the CI gate) in `scripts/check-catalog-drift.py` (FR-006/FR-008): `read_sidecar(path)` **fail-closed** on missing/partial/unparseable or any live member absent from `frameworks` (FR-008/Risk-5); `find_drift(live, sidecar)` keyed on raw OR in-scope fingerprint mismatch (never a file-diff — FR-003); `format_failure(drift)` naming the framework(s), expected-vs-actual fingerprints + human-readable count summary, and the regen entry point (FR-006); exit 1 on drift, 0 on clean. (Same file as T004 → sequential.)
- [X] T006 [US1] Regen script `scripts/regenerate-ca-baselines.sh` (FR-002 / OQ-1 — load-bearing): formalize the `specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md` recipe — loop the 6 `BASELINE_EXAMPLES` under `SOURCE_DATE_EPOCH=1700000000`, run `extract-report-data.py … && typst compile …`, `git checkout -- templates/tachi/security-report/report-data.typ` (D-9 invariant 5); add `--emit` mode to `check-catalog-drift.py` that writes `examples/ca-baseline-fingerprints.json` (`sort_keys`, trailing newline) as the script's **FINAL step** — the cheat-resistance (sidecar un-advanceable without a real regen; manifest fallback declined).
- [X] T007 [US1] One real local regen/byte-compare cycle (depends on T003 verdict, T005, T006): run `scripts/regenerate-ca-baselines.sh`; confirm it reproduces the 6 baselines (byte-compare; absorbs the remediation if T003 was RED) AND emits a correct `examples/ca-baseline-fingerprints.json`; `python3 scripts/check-catalog-drift.py` exits 0 on the resulting clean tree. **[MANUAL-ONLY]** local rendering + byte-compare review.
- [X] T008 [US1] Author `tests/scripts/test_catalog_drift_guard.py` — live gate + catch cases (depends on T004, T005): `test_live_tree_fingerprints_match_sidecar` (computes live fingerprints, reads the committed sidecar, asserts equality; **fails** not skips on missing sidecar — FR-008); `test_grow_detected`; `test_id_swap_detected` (constant-count, HIGH-2); `test_out_of_scope_flip_detected` (HIGH-3). **Each case calls `_load_framework_yaml_records.cache_clear()`** (or monkeypatches the loader) to prevent a stale-cache false-green (FR-007/Risk-3).

**Checkpoint**: guard catches drift; sidecar committed; live-tree case green on the clean tree → MVP functional.

---

## Phase 4: User Story 2 — Don't false-red on count-neutral edits (Priority: P1)

**Goal**: An edit that leaves every member's in-scope `(id, out_of_scope)` fingerprint unchanged (the #333 citation-string class) keeps the guard green — a guard that false-reds is worse than no guard (NFR-001).

**Independent Test**: apply a citation-string-only edit (real #333 shape) to a member fixture → guard passes.

- [X] T009 [US2] Add ignore cases to `tests/scripts/test_catalog_drift_guard.py` (depends on T008 — same file, sequential): `test_citation_edit_ignored` (citation-string-only change, no `(id, out_of_scope)` delta → pass; FR-003, the real #333 shape — `mitre-atlas` 36→36 / `nist-ai-rmf` 72→72); `test_non_member_change_ignored` (`nist-ai-600-1` edit → pass); `test_clean_tree_passes`. Each case `cache_clear()`.

**Checkpoint**: US1 + US2 both proven by the one test module — catch AND precision.

---

## Phase 5: User Story 3 — Guard the trunk, not just PRs (Priority: P2)

**Goal**: A catalog-edit that reaches `main` via a direct push (not a PR) still reddens CI — the #338 direct-to-main lesson reused.

**Independent Test**: inspect the workflow triggers — both `pull_request` and `push: branches:[main]` present, resolving one shared path-filter list via a YAML anchor.

- [X] T010 [US3] CI workflow `.github/workflows/tachi-catalog-drift.yml` (FR-005; depends on T008 existing): `tachi-maestro-coverage.yml` skeleton — single `runs-on: ubuntu-latest` (load-bearing for NFR-001, not a CI-minute saving), `permissions: contents: read`, Python 3.11, `pip install 'pytest>=8' 'pytest-timeout>=2' 'pyyaml>=6'` — PLUS the `tachi-pytest.yml` dual-trigger: `pull_request` + `push: branches:[main]` both resolving a single-source `&drift_paths`/`*drift_paths` anchor (F-250 lock-step). Runs `python3 -m pytest tests/scripts/test_catalog_drift_guard.py`. Path filter (`&drift_paths`): `schemas/taxonomy/*.yaml`, `examples/*/security-report.pdf.baseline`, `examples/ca-baseline-fingerprints.json`, `scripts/regenerate-ca-baselines.sh`, `specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md`, `scripts/extract-report-data.py`, `scripts/check-catalog-drift.py`, `tests/scripts/test_catalog_drift_guard.py`, `.github/workflows/tachi-catalog-drift.yml`.

**Checkpoint**: both triggers live; a direct-to-main drift reddens `main`.

---

## Phase 6: User Story 4 — Future member coverage is automatic (Priority: P3)

**Goal**: Adding a 6th framework to `ORDERED_FRAMEWORKS` extends guard coverage with zero guard-code change.

**Independent Test**: stub a synthetic 6th member into the framework tuple → guard fingerprints it automatically.

- [X] T011 [US4] Add dynamic-coverage case to `tests/scripts/test_catalog_drift_guard.py` (depends on T008 — same file, sequential): `test_future_member_covered_dynamically` — monkeypatch `ORDERED_FRAMEWORKS` to include a synthetic 6th member → `all_fingerprints()` includes it with no guard-code edit (FR-004). `cache_clear()`.

**Checkpoint**: all four user stories independently proven.

---

## Phase 7: Polish, Docs & Deliver Gate

**Purpose**: Governance trail, the carried Architect concern C-1, the OQ-6 follow-up, and the KB-18 deliver gate.

- [X] T012 [P] ADR-037 amendment (OQ-5 / Architect C-1) in `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md`: add a **NEW decision D-14** (count→fingerprint guard + sidecar contract + the (a) full-byte-identity-in-CI deferral rationale) + a Revision-History row + a one-line forward-pointer at/after D-9 — **do NOT rewrite D-9's body text** (preserves ADR-037's Accepted/byte-unchanged discipline).
- [X] T013 [P] Docs note + CHANGELOG: record that KB-15's define-time "grep `ORDERED_FRAMEWORKS`" checklist is now CI-backstopped (the relevant taxonomy/architecture doc) and add a `CHANGELOG.md` Unreleased entry for the guard.
- [X] T014 [P] File the OQ-6 follow-up: open a backlog issue to re-tag the init.sh-substitution xfail (`tests/scripts/test_init_sh_substitution.py:35`, `strict=False`) to a dedicated `init-baseline-tree` fixture-regen item — an orthogonal surface to the CA-PDF baselines. **Read the current reason text first** (it begins "Pre-existing baseline-fixture staleness…" and contains "Tracked for fixture regen under #329"); on the optional edit, replace the "#329" reference with the newly-filed issue number (do NOT leave a stale #329 pointer, PM/TL LOW). Do NOT regenerate the init.sh fixture here.
- [ ] T015 Integration + quickstart negative checks (depends on T007, T009, T010, T011): guard green on the clean tree; both triggers live; run `quickstart.md` negative checks — probe a record add/rename → `--check` exits 1 naming the framework, then revert; citation-string-only edit → `--check` exits 0, then revert. **[MANUAL-ONLY]** negative-probe direction review.
- [ ] T016 Deliver gate (KB-18 / constitution VII; depends on T015, T012, T013): verify branch is current and local `main`==`origin/main` via a full-tree diff **before** any merge or direct-to-main doc push (`git checkout -B main origin/main` if stale — `git reset --hard` is permission-blocked in this env); merge to `main` via **devops** with a Conventional-Commit `feat(329):` PR title (release-triggering); verify a release-please PR opens within ~30s, else push an empty `feat(329):` release marker.

---

## Dependencies & Execution Order

### Phase order
- **Setup (P1)**: T001 ∥ T002 — start immediately.
- **Foundational (P2)**: T003 (front-loaded, independent assessment — informs T007) ∥ T004 (fingerprint core).
- **User Stories (P3–P6)**: after T004. Critical path T004 → T005 → T006 → T007 → T008 → (T009 ∥-blocked-same-file, T011) ; T010 after T008.
- **Polish/Deliver (P7)**: T012 ∥ T013 ∥ T014 anytime after design is settled; T015 after T007/T009/T010/T011; T016 last.

### Key dependencies
- T004 blocks T005, T008 (fingerprint core).
- T005 + T006 → T007 (the regen cycle needs `--emit` and `--check`).
- T007 produces the committed sidecar that T008's live-tree case asserts against.
- T003's verdict only gates T007 (green → emit-from-tree; red → T007 also regenerates baselines). It does NOT block T004/T005/T006.
- T008, T009, T011 share `tests/scripts/test_catalog_drift_guard.py` → **sequential** (not [P] with each other).
- T010 needs the test module (T008) to exist; full green after T009/T011.
- T016 after T015 + the doc tasks.

### Parallel opportunities
- Setup: T001 ∥ T002.
- Foundational: T003 ∥ T004.
- Docs: T012 ∥ T013 ∥ T014 (different files).
- **No cross-agent wave fan-out** (feasibility-check): one engineer (senior-backend profile); the [P] markers are intra-track, disjoint-file only. Optional thin tracks: Track A (T004→T005→T006→T007 guard+regen) ∥ Track B (T008 test scaffolding, stubbing the sidecar path) per the plan's M1∥M2.

---

## Parallel Example: Setup + Foundational

```bash
# T001 and T002 touch nothing in the build surface — run together:
Task: "Confirm preconditions: branch, live ORDERED_FRAMEWORKS + loader refs, no existing sidecar"
Task: "Verify deps: pytest/pytest-timeout/pyyaml + typst 0.14.2"

# T003 (assessment) and T004 (fingerprint core) are independent:
Task: "Pre-state go/no-go: run test_backward_compatibility.py, record totals (OQ-3)"
Task: "Build fingerprint core in scripts/check-catalog-drift.py (FR-001/FR-004 + C-2 isinstance guard)"
```

---

## Implementation Strategy

### MVP First (User Story 1)
1. Setup (T001 ∥ T002) → Foundational (T003 ∥ T004).
2. US1: T005 → T006 → T007 → T008. **STOP & VALIDATE**: guard catches drift, sidecar committed, live-tree case green.
3. Demo: the guard fails on a probed drift and passes on the clean tree.

### Incremental Delivery
1. + US2 (T009) → count-neutral edits stay green (the trust property).
2. + US3 (T010) → the dual-trigger workflow goes live (PR + push:[main]).
3. + US4 (T011) → dynamic future-member coverage proven.
4. + Polish (T012–T014) → ADR/docs/CHANGELOG + OQ-6 follow-up.
5. Integration (T015) → Deliver gate (T016).

### Notes
- [P] = different files, no incomplete dependency (intra-track only here).
- Tests are a deliverable (FR-007) — authored in T008/T009/T011, never rendering PDFs (NFR-001).
- Reuse the loader (T004 importlib) — never re-implement the YAML walk (code-economy rung 2).
- Sidecar is emitted ONLY by the regen script (T006/T007) — never hand-edited (OQ-1/Risk-1).
- C-2 isinstance guard (T004) and C-1 new-D-14-not-D-9-rewrite (T012) are the carried Architect concerns — both encoded as tasks.
- Honor the deliver gate (T016): no merge/push until the guard is green locally and `main`==`origin/main` is verified (KB-18).
