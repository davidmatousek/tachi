# Agent Assignments: F-362 Remap OWASP LLM Top 10 Coverage to the 2026 Edition

**Feature**: #362 | **Draft PR**: #363 (`feat(362):` — release-triggering title verified) | **Branch**: `362-remap-owasp-llm-top10-2026`
**Source**: `specs/362-remap-owasp-llm-top10-2026/tasks.md` (triple-signed 2026-08-06 — PM / Architect / Team-Lead all APPROVED_WITH_CONCERNS)
**Feasibility**: APPROVED_WITH_CONCERNS (C1–C8 all satisfied) — see `feasibility-check.md` and `.aod/results/team-lead.md`
**Estimate**: **4.9 attention-days central** · band 4.0–6.0 · ceiling 10.0 (unexercised)
**Wave plan**: 4 sessions (A/B/C/D) · 14 waves · roster of 5 (`senior-backend-engineer`, `security-analyst`, `tester`, `web-researcher`, `product-manager`)
**Milestones held**: dev-complete 2026-08-13 · deliver 2026-08-14

> **Agent-name provenance**: every `subagent_type` below is an exact entry from the `.claude/agents/_README.md` Agent Roster (13 agents). No generic labels — no `file-agent`, `doc-agent`, or `qa-agent` appears in this document.

---

## 1. Agent Assignment Matrix

All 26 tasks assigned. `[P]` marks tasks that execute in a multi-lane wave.

### Phase 1 — Setup (Session A)

| Task | Story | Agent (`subagent_type`) | [P] | Rationale |
|------|-------|-------------------------|-----|-----------|
| T001 | Setup | `tester` | | Verification battery: 3 suite invocations + literal totals + xfail/xpass census — reads results, edits nothing (KB 15 attribution rule) |
| T002 | Setup | `senior-backend-engineer` | **[P]** | Structured data surgery: 74-row ledger pre-seed parsed from live `crosswalk.yaml`, lane-partitioned sections, σ-oracle 0-endpoint check |
| T003 | Setup | `web-researcher` | | External live verification: ≥3 fetches against genai.owasp.org for the 2026 per-entry URL scheme — the registry's Research-Flow entry role |
| T004 | Setup | `senior-backend-engineer` | **[P]** | Markdown index edit + status-line verify in `docs/architecture/README.md`; ADR-048 already Accepted, so no design authority is exercised |

### Phase 2 — Foundational (Session A)

| Task | Story | Agent (`subagent_type`) | [P] | Rationale |
|------|-------|-------------------------|-----|-----------|
| T005 | Found. | `senior-backend-engineer` | | YAML catalog surgery on `owasp.yaml:439–517` (10 records, slot table, D6 `cwe_refs` fence) + integrity suite green |
| T006 | Found. | `senior-backend-engineer` | | Deterministic bulk transform: single simultaneous σ re-key of 57 `source.id` values against pinned count oracles |
| T007 | Found. | `security-analyst` | | **[MANUAL-ONLY]** 74-edge semantic disposition against 2026 category definitions + anti-drift rule — threat-taxonomy judgment no test can render |

### Phase 3 — User Story 1 (Session B)

| Task | Story | Agent (`subagent_type`) | [P] | Rationale |
|------|-------|-------------------------|-----|-----------|
| T008 | US1 | `senior-backend-engineer` | **[P]** | Persona markdown bucket (9 files) + FR-012c compound form-bug fix at 8 sites + 20 Tier-A dispositions into its own lane section |
| T009 | US1 | `senior-backend-engineer` | **[P]** | Skill-reference bucket (15 files) + 21 Tier-A dispositions into the disjoint lane section (no shared-file write with T008) |
| T010 | US1 | `senior-backend-engineer` | **[P]** | 17 adapter files × 4 formats, all-suffixed-form + FR-002 alias-note obligation — mechanical bucket, per-format checklist in commit message |
| T011 | US1 | `senior-backend-engineer` | **[P]** | 4 legacy mirror files / 31 refs — identical treatment to personas, disjoint file set |
| T012 | US1 | `senior-backend-engineer` | **[P]** | Python + fixture surgery across 7 test modules and 19 fixtures, plus two form-bug classes (LLM sites and the adjacent `ML06:2023`) |
| T013 | US1 | `senior-backend-engineer` | **[P]** | One golden-row token edit plus the FR-007a byte-untouched guard on the F-362b-carved `coverage-attestation.typ:48` |

### Phase 4 — User Story 2 (Session C)

| Task | Story | Agent (`subagent_type`) | [P] | Rationale |
|------|-------|-------------------------|-----|-----------|
| T014 | US2 | `senior-backend-engineer` | **[P]** | Contract-example re-key in `schemas/finding.yaml` + regex/finding-prefix non-impact confirmations |
| T015 | US2 | `senior-backend-engineer` | **[P]** | Structural emitter fix: derive taxa from the catalog loader at both sites, retired `informationUri`, prefix-map re-key — server-side Python |
| T016 | US2 | `senior-backend-engineer` | **[P]** | Parser stderr warning in `extract-report-data.py` + byte-neutrality proof on well-formed inputs |
| T017 | US2 | `senior-backend-engineer` | **[P]** | Net-new pytest module + same-commit `tachi-pytest.yml` `paths:`/invocation/`&hardening_paths` lockstep — pytest + CI YAML, not BDD/Gherkin (see alternate trigger) |

### Phase 5 — User Story 3 (T018 → Session B; remainder Session C)

| Task | Story | Agent (`subagent_type`) | [P] | Rationale |
|------|-------|-------------------------|-----|-----------|
| T018 | US3 | `security-analyst` | **[P]** | **[MANUAL-ONLY]** 4 absorption records assessed against agent pattern catalogs — detection-evidence judgment; pulled into Session B per F7 |
| T019 | US3 | `security-analyst` | **[P]** | **[MANUAL-ONLY]** 10 verdicts re-derived against 2026 definitions + catalog `# citation:` reconcile — security-coverage canon (FR-009 review gate below) |
| T020 | US3 | `senior-backend-engineer` | **[P]** | D5 consistency function added to the existing drift-guard module + optional `&drift_paths` line — Python, ~0.1d, off the critical path |
| T021 | US3 | `senior-backend-engineer` | **[P]** | Closed-list restatement propagation across 11 doc surfaces — enumerated and mechanical, including the triad-visible `scope.md:24` edit |

### Phase 6 — Polish & Close-out (Session D)

| Task | Story | Agent (`subagent_type`) | [P] | Rationale |
|------|-------|-------------------------|-----|-----------|
| T022 | Polish | `tester` | | Repo-wide sweep battery using verified command forms + ledger completion 41/41 and Tier-B census reconciliation — a verification net, not an edit pass |
| T023 | Polish | `tester` | | Deterministic confirmation of the default-no-regen ruling + "no OTHER baseline source moved" check — verification with a recorded disposition |
| T024 | Polish | `tester` | | Byte-identity proof + full battery on committed HEAD + delta-aware totals reconciliation against T001 — the terminal verification gate |
| T025 | Polish | `senior-backend-engineer` | **[P]** | Hand-curated CHANGELOG Unreleased entry incl. the 10-row σ migration table — markdown authoring against the repo's dual-changelog model |
| T026 | Polish | `product-manager` | **[P]** | **Scope-bearing**: F-362b is declared blocking-before-next-minor with a carve-out disclosure and an 8-item checklist — a scope call, therefore PM-owned (co-lane trigger below) |

**Workload totals**: `senior-backend-engineer` 17 · `security-analyst` 3 · `tester` 4 · `web-researcher` 1 · `product-manager` 1 = **26/26 assigned**.

### Assignment overrides and escalation triggers

| # | Trigger | Action |
|---|---------|--------|
| **T003** | The live evidence does not fall cleanly into either pre-decided D9 branch (per-entry URLs vs interim release-resource page) | `web-researcher` carries **no verdict authority** (registry, `haiku` tier). It records evidence and applies the pre-decided branch only. Ambiguity escalates to `architect` per the registry Research Flow (`web-researcher → architect → team-lead`). |
| **T004** | ADR-048's Status line does not read `Accepted (provisional pre-PR) 2026-08-06` | Stop and escalate to `architect` — the index entry is mechanical, but an ADR status correction is an architect decision. |
| **T017** | Net-new module authoring stalls on the pytest/importlib covering matrix | `tester` is a **BDD/Gherkin specialist** in this repo, so `senior-backend-engineer` is primary for a raw pytest module + GitHub Actions YAML lockstep (same rationale recorded at F-295 T017). Reassign the *covering-matrix design* to `tester` if D2 branch coverage needs a second pass; workflow YAML stays with `senior-backend-engineer` either way. |
| **T019** | — (always) | `security-analyst` **authors**; the FR-009 review gate is discharged by `product-manager`, which is also the agent carrying PM W3's SC-005 re-verification at PR-ready. Author and gate are deliberately different agents. |
| **T026(b)** | The `_canonical()` widening defer-rationale needs technical depth beyond a transcription (incl. the `check-catalog-drift.py:95` vs `:104` false-docstring defect) | `senior-backend-engineer` is already in wave D4 on T025 — draft sub-item (b) as a co-lane contribution rather than a separate task. **This is an absorption, not a T027.** |
| **T026(c)** | T018 surfaced an FR-003 gap | Body content is lifted from `gap-analysis.md` (already authored by `security-analyst` in Session B). No new agent, no new task — pre-authorized absorption. |

---

## 2. Parallel Execution Waves

14 waves across 4 sessions. Every ordering constraint from tasks.md §Dependencies is honored, including the four that live only in task prose.

```
SESSION A (~1.60d) — Phase 1 + Phase 2 · the serial spine
│
├─ A1  T001                                    [tester]                     — pre-state gate, BLOCKS every edit
├─ A2  T002 [P] ∥ T004 [P]                     [SBE ×2 lanes]
├─ A3  T003                                    [web-researcher]             — AFTER T002 (writes the ledger's URL-policy block)
├─ A4  T005                                    [SBE]                        — AFTER T003 (no url authored before the gate)
├─ A5  T006                                    [SBE]                        — AFTER T005 · AFTER T002 (σ-oracle precondition)
└─ A6  T007                                    [security-analyst]           — AFTER T006 · AFTER T003 (54 re-anchors)

SESSION B (~1.15d) — Phase 3 + T018 pulled forward (F7)
│
├─ B1  T008 [P] ∥ T009 [P] ∥ T011 [P] ∥ T018 [P]   [SBE ×3 + security-analyst]   — 4 lanes = solo-curator cap exactly
└─ B2  T010 [P] ∥ T012 [P] ∥ T013 [P]              [SBE ×3]                      — T010 AFTER T008+T009 (FR-013); T012/T013 AFTER T008

SESSION C (~1.35d) — Phase 4 + Phase 5 remainder
│
├─ C1  T014 [P] ∥ T015 [P] ∥ T016 [P] ∥ T019 [P]   [SBE ×3 + security-analyst]   — 4 lanes = cap; T019 AFTER T018 (Session B)
└─ C2  T017 [P] ∥ T020 [P] ∥ T021 [P]              [SBE ×3]                      — T017 AFTER T015; T020 in-or-after T019's commit; T021 AFTER T019

SESSION D (~0.90d) — Phase 6 + deliver prep
│
├─ D1  T022                                    [tester]                     — sweep first
├─ D2  T023                                    [tester]                     — AFTER T022
├─ D3  T024                                    [tester]                     — AFTER T023 · terminal battery on committed HEAD
└─ D4  T025 [P] ∥ T026 [P]                     [SBE ∥ product-manager]      — AFTER T024
```

### Dependency edges enforced by this wave map

| Edge | Source | Where enforced |
|------|--------|----------------|
| T002 → T003 | Architect MEDIUM-3 (T003 writes into the header T002 scaffolds) | A2 → A3 |
| T003 → T005, T003 → T007 | Team-Lead F6 (no URL authored before the scheme gate) | A3 → A4, A3 → A6 |
| T002 → T006 | Team-Lead F6 (0-target-endpoint check is the σ oracle) | A2 → A5 |
| T005 → T006 → T007 | Strict serial: names inform dispositions; σ before disposition | A4 → A5 → A6 |
| T008+T009 → T010 | FR-013 sequencing | B1 → B2 |
| T008 → T012, T008 → T013 | Fixtures mirror persona content | B1 → B2 |
| T015 → T017 | The test asserts the fixed emitter | C1 → C2 |
| T018 → T019 → T021 | Evidence → verdicts → restatements (the true critical path) | B1 → C1 → C2 |
| **T019 → T020** | **Architect HIGH-1 / Team-Lead F2** — never between T005 and T019 | C1 → C2 |
| T022 → T023 → T024 | Sweep → fixture disposition → final battery | D1 → D2 → D3 |
| T024 → T025, T024 → T026 | Changelog and issues describe a verified end state | D3 → D4 |

**Lane-collision hazards closed**: T008/T009 write disjoint pre-partitioned sections of `bare-code-ledger.md` (F4, via T002's scaffold), and the T012/T020 same-file collision on `test_catalog_drift_guard.py` is dissolved by the F2 re-sequence — T012 commits in B2, T020 lands in C2, never concurrent (F3).

**Critical path** (F7-corrected): `T001 → T005 → T006 → T007 → T018 → T019 → T021 → T022 → T024 → T025/T026`. It runs through three serial human-judgment tasks, two `[MANUAL-ONLY]`-cored. **Neither T007 nor the T018→T019 chain compresses by parallelization** — adding lanes there would only manufacture unreviewed output.

**Solo-curator drop-order**: B1 and C1 sit exactly at the 4-lane advisory cap. If the cap must tighten to 3, drop `T011` from B1 and `T014` from C1 (0.08d each, lowest semantic burden) and re-seat them in the following wave. **Never** drop T008 or T009 — those two carry essentially the whole wave's semantic review burden.

---

## 3. Quality Gates Between Waves

| Boundary | Gate | Type | Failure disposition |
|----------|------|------|---------------------|
| A1 → A2 | Pre-state recorded in `test-results-prestate.md` with **literal** totals, the ~19 known out-of-gate failures, and current xfail/xpass counts | **Blocking prerequisite** | No remap edit may occur first — a missing pre-state destroys T024's reconciliation base |
| A2 → A3 | Both ledgers exist; Tier-A **lane sections present**; `0 owasp-LLM target endpoints` recorded in the crosswalk header | Blocking | Absent lane sections re-open the F4 lost-write hazard — rescaffold before B1 |
| A3 → A4 | **URL-scheme gate closed**: verdict + anchor policy written to `### URL policy (T003)` | **Hard gate** | **No URL may be authored anywhere** until closed. Ambiguous evidence ⇒ escalate to `architect`, do not guess |
| A4 → A5 | `tests/schemas/test_taxonomy_integrity.py` green after catalog surgery | Blocking | Red integrity suite ⇒ stop; the catalog is the source of truth every later surface derives from |
| A5 → A6 | σ-permutation oracles: **645 edges · 0 duplicates · primary floor ≥500 · per-2026-id counts exactly `8/9/7/8/6/11/4/6/7/8`**; integrity suite green | **Fail-closed** | Any oracle miss ⇒ the pass was sequential, not simultaneous (dedupe-key collision) — revert and redo as one pass |
| **A6 → B (Phase 2 checkpoint)** | **Integrity suite green + `crosswalk-disposition-ledger.md` 74/74 complete** | **Phase gate — blocks all user-story work** | Incomplete ledger ⇒ no US1/US2/US3 dispatch. Interim-anchor substitutions recorded per-edge here, never as a new task |
| B1 → B2 | T008/T009 lane sections filled (20 + 21 = 41 Tier-A occurrences); per-file checklists present in commit messages | Checkpoint | — |
| **B close (Session B gate)** | **Per-bucket checklists complete in each commit message** (incl. T010's per-format checklist and the FR-002 alias-note obligation) **+ local gated 15-module subset green** | **Session gate** | Bucket checklist absent ⇒ the bucket is not auditable; a bucket's per-file trail lives in the commit message, not in sub-tasks |
| B close | `gap-analysis.md` complete (4 absorption records) — **any Partial-downgrade signal is raised here** | Risk gate | A downgrade discovered now has **two sessions of runway** (the entire point of F7). Cascade absorbs into T021's closed list; FR-003 gaps absorb into T026(c) |
| C1 → C2 | **FR-009 review gate on `OWASP_COVERAGE.md`** discharged by `product-manager`; catalog `# citation:` comments reconciled against the re-derived verdicts | **Review gate** | Unreviewed canon does not proceed. A published Partial downgrade is acceptable; a suppressed one is not |
| **C close (Session C gate)** | **CI-gated tests green**: `tachi-pytest.yml` (16 modules incl. the net-new `test_owasp_2026_contract.py`) **and** `tachi-catalog-drift.yml` (the D5 assertion is now true — doc row and catalog both 2026); **declared test-count deltas present in T017's and T020's commit messages** | **Session gate** | Red drift guard here means T020 landed early — re-sequence, never silence. T021's `cwe.yaml:17` edit re-fires `&drift_paths` and must stay green |
| D1 → D2 | Sweep **sanity rule**: every command form produces hits pre-remap (suffixed `git grep -nP`, the spaced-prose/hyphenated `LLM[[:space:]]+2025\|OWASP-LLM-2025` form class, `-oP … \| wc -l` counts); **zero undispositioned residue** outside exclusions (SC-002 per D7); Tier A 41/41; Tier B Σ = 366 in-scope + 103 carve-out | **Fail-closed** | A command producing no pre-remap hits is a broken command, not a clean repo — fix the form and re-run |
| D2 → D3 | Default **no-regen** confirmed; no OTHER baseline source moved; disposition recorded in delivery notes ("#345 owns the fixture surface") | Deterministic confirmation | Regenerating anyway requires deleting the xfail marker **and** closing #345 in the same commit — **PM approval required**, not builder discretion |
| **D3 (terminal gate)** | **Byte-identity: `test_backward_compatibility.py` green with ZERO baseline bytes changed** (FR-007a no-churn proof); integrity suite green; gated subset green; **delta-aware reconciliation = T001 pre-state + declared T017/T020 deltas**; xfail/xpass unchanged (#345's xfail persists) | **Fail-closed terminal gate** | Unattributable delta ⇒ stop before merge. Record that `tachi-catalog-drift.yml` green on this PR is **EXPECTED and uninformative** |
| D4 → deliver | Changelog entry landed; F-362b + 3 follow-up issues filed | Checkpoint | Hands off to `/aod.deliver`: live link-rot `workflow_dispatch` (`no_cache: true`), **PM SC-005 re-verification before PR-ready**, KB 18 branch/`main` hygiene, `feat(362):` title confirmed on PR #363, release-please verification, ADR-048 SHA fill |

---

## 4. Time Estimates Per Wave

Attention-days at AOD agent-orchestrated pace, decomposed from the signed structural walk (Ph1 0.30 / Ph2 1.30 / Ph3 0.80 / Ph4 0.60 / Ph5 1.10 / Ph6 0.90) with **T018's 0.35 relocated from Session C into Session B** per F7. Phase budgets are unchanged; only the session boundary moves.

| Wave | Tasks | Agents | Attention-days | Wall-clock (pacing lane) |
|------|-------|--------|----------------|--------------------------|
| A1 | T001 | tester | 0.08 | 0.08 |
| A2 | T002 (0.12) ∥ T004 (0.04) | SBE ×2 | 0.16 | 0.12 |
| A3 | T003 | web-researcher | 0.06 | 0.06 |
| A4 | T005 | SBE | 0.22 | 0.22 |
| A5 | T006 | SBE | 0.18 | 0.18 |
| A6 | **T007** | security-analyst | **0.90** | 0.90 |
| **Session A** | T001–T007 | | **1.60** | ~1.56 |
| B1 | T008 (0.22) ∥ T009 (0.20) ∥ T011 (0.08) ∥ **T018 (0.35)** | SBE ×3 + security-analyst | 0.85 | 0.35 |
| B2 | T010 (0.12) ∥ T012 (0.14) ∥ T013 (0.04) | SBE ×3 | 0.30 | 0.14 |
| **Session B** | T008–T013 + T018 | | **1.15** | ~0.49 |
| C1 | T014 (0.08) ∥ T015 (0.22) ∥ T016 (0.10) ∥ **T019 (0.50)** | SBE ×3 + security-analyst | 0.90 | 0.50 |
| C2 | T017 (0.20) ∥ T020 (0.10) ∥ T021 (0.15) | SBE ×3 | 0.45 | 0.20 |
| **Session C** | T014–T017 + T019–T021 | | **1.35** | ~0.70 |
| D1 | T022 | tester | 0.35 | 0.35 |
| D2 | T023 | tester | 0.08 | 0.08 |
| D3 | T024 | tester | 0.20 | 0.20 |
| D4 | T025 (0.15) ∥ T026 (0.12) | SBE ∥ product-manager | 0.27 | 0.15 |
| **Session D** | T022–T026 | | **0.90** | ~0.78 |
| | **Σ 26 tasks** | | **5.00 raw → 4.9 central** | |

**Reconciliation notes**:
- Σ = 5.00 raw; the signed estimate is **4.9 central (band 4.0–6.0)** — the same rounding applied in `.aod/results/team-lead.md`.
- Phase 5's internal split is pinned here as T018 0.35 / T019 0.50 / T020 0.10 / T021 0.15 = **1.10**, matching the phase budget. The review's driver line quoted T021 at 0.25 as a rounded figure; the exact split above is normative for wave sizing.
- Wall-clock totals are shorter than attention-days in Sessions B and C because the fan-out waves run 3–4 lanes. Sessions A and D are near-serial by construction (a serial spine and a serial verification chain), so their two columns nearly coincide.

**Ceiling driver (the single schedule risk that can breach 2026-08-13)**: a **Partial downgrade at T019** — priced at **+0.5 to +0.8d**, cascading to T021's 11 restatement surfaces, the triad-visible `.claude/rules/scope.md` edit, and the README poster regenerate-or-annotate decision. Pulling T018 into Session B is the mitigation: the signal now arrives in the B-close gate with two sessions of runway rather than late in Session C with one. **Timeline veto not exercised.**

---

## 5. Load Check

**Model**: an agent instance's wave load = its attention-days in that wave ÷ the wave window, where **window = pacing lane × 1.25**. The 25% margin is deliberate gate/snag absorption headroom, so the pacing lane sits at exactly 80% by design and every other lane sits below it.

| Wave | Peak agent | Peak load | Other lanes | Lanes |
|------|-----------|-----------|-------------|-------|
| A1 | `tester` (T001) | **80%** | — | 1 |
| A2 | `senior-backend-engineer` (T002) | **80%** | SBE (T004) 27% | 2 |
| A3 | `web-researcher` (T003) | **80%** | — | 1 |
| A4 | `senior-backend-engineer` (T005) | **80%** | — | 1 |
| A5 | `senior-backend-engineer` (T006) | **80%** | — | 1 |
| A6 | `security-analyst` (T007) | **80%** | — | 1 |
| B1 | `security-analyst` (T018) | **80%** | SBE (T008) 50% · SBE (T009) 45% · SBE (T011) 18% | **4 (at cap)** |
| B2 | `senior-backend-engineer` (T012) | **80%** | SBE (T010) 67% · SBE (T013) 22% | 3 |
| C1 | `security-analyst` (T019) | **80%** | SBE (T015) 35% · SBE (T016) 16% · SBE (T014) 13% | **4 (at cap)** |
| C2 | `senior-backend-engineer` (T017) | **80%** | SBE (T021) 60% · SBE (T020) 40% | 3 |
| D1 | `tester` (T022) | **80%** | — | 1 |
| D2 | `tester` (T023) | **80%** | — | 1 |
| D3 | `tester` (T024) | **80%** | — | 1 |
| D4 | `senior-backend-engineer` (T025) | **80%** | `product-manager` (T026) 63% | 2 |

**Peak per-agent load across all 14 waves: 80%. The 80% ceiling is met, never exceeded. Capacity veto not exercised.**

Three observations that matter more than the percentages:

1. **`senior-backend-engineer` carries 17 of 26 tasks, but never more than one lane per wave.** The concentration is across the feature, not within any wave — each parallel `senior-backend-engineer` lane is a separately dispatched instance with a disjoint file set. No instance is ever asked to hold two tasks concurrently. This is a bucket-scoped-work profile, not an overload.
2. **The genuinely constrained resource is not agent capacity — it is the single-threaded human review funnel.** Two `[MANUAL-ONLY]` cores (T007, T018) plus one review-gated canon (T019) account for 1.75 of the 5.00 attention-days and cannot be parallelized. Every remaining lane could be widened at will and the feature would not finish sooner. B1 and C1 are therefore capped at 4 lanes on the solo-curator advisory, with `T008`/`T009` protected in the drop-order because they carry the wave's semantic burden.
3. **The 26-task ceiling is a hard absorption boundary.** In-loop discoveries are absorbed into an existing task or filed as a follow-up issue — never added as T027 without team-lead re-sign-off. Pre-authorized absorptions: T003 interim-anchor substitutions → T007 ledger rows; FR-003 gaps → T026(c); a T019 Partial-downgrade cascade → T021's closed restatement list; the T026(b) technical rationale → the `senior-backend-engineer` co-lane in D4.

---

## 6. Sign-off

**Team-Lead: APPROVED** — assignment matrix covers all 26 tasks with exact registry agent names; the 14-wave map honors every dependency edge in `tasks.md` §Dependencies including the four that live only in task prose (T002→T003, T003→T005/T007, T002→T006, T019→T020); the two lane-collision hazards (F3, F4) are structurally closed; quality gates are fail-closed at the four points where a silent pass would be expensive (σ oracles, sweep sanity rule, FR-009 review, byte-identity); estimates reconcile to the signed 4.9-day structural walk; peak per-agent wave load is 80% with none exceeding it.

**Timeline veto: NOT exercised. Capacity veto: NOT exercised.**

Hand off to `orchestrator` for Session-A dispatch. Dispatch precondition: T001 completes and commits before any remap edit is attempted.
