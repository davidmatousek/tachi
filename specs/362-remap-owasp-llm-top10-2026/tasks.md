---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-08-06
    status: APPROVED_WITH_CONCERNS
    notes: "15/15 FRs mapped to tasks; plan-review CRITICAL verified fixed by execution (corrected sweep returns 498 occ / 77 files / 366 bare — exact SC-002/FR-014 baselines); no scope creep (26 = ceiling, F-362b filed not done). Warnings applied in-loop 2026-08-06: W1 OWASP-LLM-2025 hyphenated-form detector added to T022/quickstart; W2 FR-002 alias-note obligation added to T010; W3 SC-005 PM re-verification added to Deliver-Stage Reminders. Full: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-08-06
    status: APPROVED_WITH_CONCERNS
    notes: "Carried conditions 2+5 landed (T017 net-new module placement sound — F-302/F-295 precedent; T026(a) breadcrumb sunset). No-churn boundary holds at task level, zero leaks; every count/line-anchor re-verified exactly at HEAD. 9 findings applied in-loop 2026-08-06: HIGH-1 T020 resequenced after T019; MEDIUM-1 generate-risk-scores-sarif.py added to T017 &hardening_paths lockstep; MEDIUM-2 T023 default-no-regen (xfail(strict=False)/#345); MEDIUM-3 ledger lane-partitioning (T002) + T003 serialized; MEDIUM-4 drift-guard file dropped from T012 re-key list; MEDIUM-5 sweep-form breadth; LOW-1..4 wording, compound σ+suffix fix, ML06:2023 same-pass fix, near-empty-member notes. Full: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-08-06
    status: APPROVED_WITH_CONCERNS
    notes: "Sign-off GRANTED. C1–C8 all satisfied; W5 serialization eliminated (T024 inverted to verification); timeline/capacity vetoes NOT exercised. Estimate re-issued 4.9d central (band 4.0–6.0) — holds dev-complete 2026-08-13 and deliver 2026-08-14. 26-task ceiling = HARD absorption boundary (no T027 without team-lead re-sign-off; pre-authorized absorptions in Notes). Findings applied in-loop 2026-08-06: F2 (=architect HIGH-1), F4 lane-partitioned Tier A, F5 T024 delta-aware reconciliation, F6 dependency edges, F7 T018→Session B (highest-leverage schedule mitigation). F1 reconciled via architect MEDIUM-2: the xfail(strict=False)/#345 trace refutes F1's guaranteed-red premise — default no-regen, T023 re-scoped to confirmation; same-commit obligation mooted. Full: .aod/results/team-lead.md"
---

# Tasks: Remap OWASP LLM Top 10 Coverage to the 2026 Edition

**Input**: Design documents from `/specs/362-remap-owasp-llm-top10-2026/`
**Prerequisites**: plan.md (dual-signed 2026-08-06), spec.md (PM-signed), research.md (incl. Phase 0 decisions D1–D9), data-model.md, contracts/, quickstart.md, ADR-048 (Accepted provisional pre-PR)

**Tests**: Included — the spec explicitly mandates net-new tests (FR-006b lockstep test, FR-012a derived-taxa test, D5 consistency test) and existing-suite gates (integrity suite, byte-identity suite, gated subset).

**Organization**: Grouped by user story. Bucket-scoped per team-lead C-conditions (never file-scoped); 26 tasks = the post-split ceiling. Architect plan-review conditions 2 and 5 land as named tasks (T017, T026). Triple-review edits applied 2026-08-06 (all findings traceable to reviewer IDs inline).

> **Definition of Done** (canonical bar = constitution VII):
> 1. ✅ Pushed to Production — feature deployed and operational.
> 2. ✅ Tested — all automated tests pass (unit, integration, E2E, performance)
> 3. ✅ User Validated — real-world usage confirmed by actual users/stakeholders.

<!-- DOD-ACK -->

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3)
- Exact file paths in descriptions; counts are research-measured at `747805c` (normative)

## Path Conventions
Single project at repo root. Data surfaces: `schemas/`, `.claude/`, `adapters/`, `agents/`, `scripts/`, `tests/`, `templates/`, `docs/`. Feature artifacts: `specs/362-remap-owasp-llm-top10-2026/`.

---

## Phase 1: Setup (W0 — gate + Foundational artifacts)

**Purpose**: Pre-state evidence, ledger scaffolds, URL-scheme gate, ADR hygiene — before any remap edit

- [X] T001 Pre-state capture: run `python -m pytest tests/scripts/test_backward_compatibility.py -q` and `python -m pytest tests/schemas/test_taxonomy_integrity.py -q` plus the gated 15-module subset invocation (read exact command from `.github/workflows/tachi-pytest.yml`); record LITERAL totals incl. the ~19 known out-of-gate failures AND current xfail/xpass counts (#345's xfail is expected present) in `specs/362-remap-owasp-llm-top10-2026/test-results-prestate.md` (KB 15 attribution rule; quickstart §0)
- [X] T002 [P] Scaffold both disposition ledgers per `contracts/disposition-ledgers.md`: `specs/362-remap-owasp-llm-top10-2026/crosswalk-disposition-ledger.md` (74 rows pre-seeded from live `schemas/taxonomy/crosswalk.yaml`, header with a reserved `### URL policy (T003)` block) and `specs/362-remap-owasp-llm-top10-2026/bare-code-ledger.md` with Tier A **pre-partitioned into two lane sections** — `### Tier A — personas (T008)` and `### Tier A — skill references (T009)` — under an append-only-to-your-own-section rule (architect MEDIUM-3 / team-lead F4; 20+21 = 41 occurrences / 8 files), plus the Tier B skeleton (censuses 366 in-scope + 103 carve-out); re-verify **0 owasp-LLM target endpoints** in the crosswalk and record in the ledger header (architect plan MEDIUM-2, σ oracle precondition)
- [X] T003 D9 URL-scheme gate (after T002 — writes into the ledger header T002 scaffolds): live-verify the 2026 per-entry URL scheme on genai.owasp.org (≥3 sample fetches); record verdict + the chosen anchor policy (per-entry URLs vs interim release-resource-page) in the crosswalk ledger's `### URL policy (T003)` block; **no URL may be authored anywhere before this task completes** (blocks T005 `url` fields and T007 re-anchors)
- [X] T004 [P] ADR index + hygiene: add ADR-048 entry to `docs/architecture/README.md` ADR index; verify ADR-048 Status line reads `Accepted (provisional pre-PR) 2026-08-06` with `**Accepted-commit-SHA**` placeholder (architect LOW-1 — applied at plan, verify only); do NOT rewrite the index's historical 030/031/034/045 prose (D7 retained-historical)

**Checkpoint**: pre-state recorded; ledgers exist with lane sections; URL policy decided; no remap edit has occurred

---

## Phase 2: Foundational (W1 — the id/name source of truth all stories consume)

**Purpose**: Catalog + crosswalk are the canonical mapping surfaces; every downstream surface derives from them

**CRITICAL**: No user-story work until this phase is green

- [X] T005 Catalog surgery in `schemas/taxonomy/owasp.yaml:439–517`: all 10 LLM records per data-model.md §2 slot table — `full_id` → `OWASP-LLM-2026-NN`, verbatim 2026 `name` (LLM08 = "Hidden Context Exposure"), `url` per T003 policy, `# citation:` re-attested to the category now in each slot (comment follows category, not slot; e.g. LLM03 cites tool-abuse/agent-autonomy); `cwe_refs` per D6 fence (resolve-only against `cwe.yaml`; growth → follow-up issue; default `[]`); `id`/order/`out_of_scope` untouched; then `python -m pytest tests/schemas/test_taxonomy_integrity.py -q` green
- [ ] T006 Crosswalk mechanical σ-permutation in `schemas/taxonomy/crosswalk.yaml` (requires T002's recorded 0-target-endpoint check): single simultaneous pass re-keying the 57 non-hold `source.id` values per data-model.md §1 (never sequential — dedupe-key collision); verify 645 edges, 0 duplicates, primary floor ≥500, post-σ per-2026-id counts exactly `8/9/7/8/6/11/4/6/7/8` (data-model §3); integrity suite green
- [ ] T007 Crosswalk 74-edge human disposition: re-validate `target`/`confidence` against 2026 category definitions (acute: LLM08 broadened hidden-context scope; LLM01 cross-modal; anti-drift rule — no articulable one-sentence citation ⇒ downgrade) and re-anchor the 54 year-slugged `citation` URLs per T003 policy (interim-anchor substitutions recorded per-edge in ledger rows — pre-authorized absorption, never a new task); complete `crosswalk-disposition-ledger.md` 74/74 rows [MANUAL-ONLY: per-edge semantic review is curator judgment — no test detects a wrong-meaning edge]

**Checkpoint**: catalog + crosswalk fully 2026; integrity suite green; ledger 74/74

---

## Phase 3: User Story 1 — Findings cite the current standard (Priority: P1) MVP

**Goal**: Every authored contract surface (personas, skills, adapters, mirrors, tests, templates) cites 2026 by category

**Independent Test**: spec US-1 ACs — integrity suite green; per-surface checklists complete; Tier-A bare dispositions done for the touched files; zero suffixed-2025 refs in the touched buckets

- [ ] T008 [P] [US1] Personas bucket: the 9 LLM-ref-bearing personas in `.claude/agents/tachi/` (of 22 files in the directory — architect LOW-1) — 2026 codes/names per σ, Hidden Context Exposure alias note at first mention, ADR-048 token grammar in `owasp_references`/prose; **FR-012c compound form-bug fix at all 8 sites — strip the `:2025` suffix AND apply σ** (architect LOW-2): `prompt-injection.md:65,93,120` → `id: LLM01` (σ-hold), `data-poisoning.md:77,105` → `id: LLM04`, `model-theft.md:75,127` → `id: LLM04`, `denial-of-service.md:134` → `id: LLM06`; record Tier-A bare dispositions (20 occurrences / 5 files) in your `### Tier A — personas (T008)` section of `bare-code-ledger.md`
- [ ] T009 [P] [US1] Skill references bucket: all 15 files (13 `references/` + 2 READMEs incl. `tachi-orchestration/references/sarif-specification.md` help.markdown templates and `tachi-shared` files) — 2026 codes/names/alias notes; record Tier-A bare dispositions (21 occurrences / 3 files) in your `### Tier A — skill references (T009)` section of `bare-code-ledger.md`
- [ ] T010 [US1] Adapters bucket: 17 files across `adapters/{claude-code,copilot,cursor,generic}/` (118 refs, all suffixed-form) with an explicit per-format checklist in the task commit message, **including the FR-002 alias-note obligation — "Hidden Context Exposure (System Prompt Leakage, 2025 name)" at first category mention in each of the 4 adapter files presenting it (PM W2)**; sequenced after T008/T009 (FR-013); `adapters/github-actions/` carries 0 LLM refs — verify and note
- [ ] T011 [P] [US1] Legacy mirrors bucket: `agents/ai/data-poisoning.md`, `agents/ai/model-theft.md`, `agents/ai/prompt-injection.md`, `agents/orchestrator.md` (31 refs) — same treatment as personas (research-corrected: 4 files, not ~9)
- [ ] T012 [US1] Tests + fixtures bucket: re-key 2025 assertions in 7 test files (`tests/scripts/test_llm10_unbounded_consumption_enrichment.py` 35 refs, `test_coverage_attestation.py` — 16 bare refs, **0 suffixed** — `test_output_integrity.py`, `test_source_attribution.py`, `test_tool_abuse_enrichment.py`, `generate_pagination_fixture.py`, `test_backward_compatibility.py:19` docstring — the latter two members are bare/docstring-only, no suffixed re-keys there (architect LOW-4)); `test_catalog_drift_guard.py` is **verify-only** — its LLM ids are synthetic and edition-agnostic (`:51`, `:204`), nothing to re-key, and T020 owns that file (architect MEDIUM-4); + 19 fixture files (13 suffixed / 6 bare-only; incl. `web_api_coverage_attestation/stream_1_f_a3_wiring/{prompt_injection,denial_of_service}_wired.md:36` form-bug fixes AND the same-pass adjacent fix in `data_poisoning_wired.md:36`: `id: "ML06:2023"` → bare `id: ML06` — same ADR-028 violation class, non-LLM framework, rung-2 economy (architect LOW-3)); no file renames (no `tachi-pytest.yml` `paths:` churn); ledger-disposition any fixture deliberately exercising legacy forms
- [ ] T013 [US1] Templates bucket: `templates/tachi/output-schemas/threats.md:365` golden row → 2026 token; verify no other LLM refs in `templates/` outside the F-362b-carved `coverage-attestation.typ:48` (must remain byte-untouched — FR-007a)

**Checkpoint**: US-1 independently verifiable — all authored surfaces 2026; gated subset green locally

---

## Phase 4: User Story 2 — Downstream consumers survive the transition (Priority: P2)

**Goal**: The machine-readable contract (finding.yaml, emitters, parsers) moves in lockstep with ADR-048's grammar

**Independent Test**: spec US-2 ACs — ADR-048 Accepted (done); grammar enforceable: net-new tests green in CI-gated modules; zero hardcoded taxa in the risk-scores emitter

- [ ] T014 [P] [US2] Contract examples: `schemas/finding.yaml` — `:109` references example → `"OWASP LLM01:2026"`; `:330–332` source_attribution examples re-keyed (LLM05 → LLM10 per σ; verify CWE/ATLAS companions still current); confirm `:18` id-pattern regex and `:26` `LLM-1` finding-prefix are unaffected
- [ ] T015 [US2] Emitters structural fix in `scripts/generate-risk-scores-sarif.py`: replace hardcoded taxa at BOTH sites (`TAXONOMIES` `:453` and `supported_taxonomies()` `:495–520`) with taxa derived from `schemas/taxonomy/owasp.yaml` via the existing loader; fix retired `informationUri` (both sites) → `https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/`; re-key `_OWASP_REFERENCE_BY_PREFIX` `:234` (OI → `OWASP LLM10:2026`, MI → `OWASP LLM07:2026`); update 2023-era rule prose in `scripts/generate-threats-sarif.py:66,259–260,271`
- [ ] T016 [P] [US2] Parser warning: add unmatched-`source_attribution`-ref stderr warning to `scripts/extract-report-data.py::classify_framework_items` (`:1174–1201`); verify byte-neutrality (stderr only; identical `{id, classification}` output for well-formed inputs)
- [ ] T017 [US2] Net-new CI-gated test module `tests/scripts/test_owasp_2026_contract.py` (architect condition 2 — placement assigned HERE): (a) `normalize_owasp_id` covering matrix per D2 (`OWASP LLM01:2025`→`LLM-01`, `OWASP LLM10:2026`→`LLM-10`, breadcrumb-suffixed string→passthrough pinned, ASI/MCP/CWE branches, unknown→passthrough pinned); (b) FR-012a derived-taxa test asserting risk-scores taxa == catalog records (both former hardcoded sites); SAME COMMIT: add the module to `.github/workflows/tachi-pytest.yml` `paths:` + pytest invocation (KB 3 lockstep) **AND add `scripts/generate-risk-scores-sarif.py` to `&hardening_paths`** so the exact file FR-012a guards triggers its own gate (architect MEDIUM-1; optional one-liner: `schemas/taxonomy/owasp.yaml` too); record resulting CI status (gated) **and the expected test-count delta** in the commit message (team-lead F5)

**Checkpoint**: US-2 independently verifiable — contract + emitters + tests green, CI-gated

---

## Phase 5: User Story 3 — The coverage claim stays honest (Priority: P3)

**Goal**: Per-category verdicts re-derived from evidence against 2026 definitions; every restatement carries the honest number

**Independent Test**: spec US-3 ACs — gap-analysis artifact complete; OWASP_COVERAGE.md review-gated; zero stale headlines

- [ ] T018 [US3] Gap analysis → `specs/362-remap-owasp-llm-top10-2026/gap-analysis.md`: 4 absorption records per data-model.md §7 (cross-modal→LLM01, model-artifact authenticity→LLM04, fine-tuning subversion→LLM05, insecure generated code at scale→LLM10) — each: existing-detection evidence (agent + pattern-catalog citation) OR gap→follow-up issue + verdict impact. **No Phase-3 dependency — run in the Session-B window (team-lead F7: moves any Partial-downgrade discovery one session earlier)** [MANUAL-ONLY: evidence assessment against pattern catalogs is analyst judgment]
- [ ] T019 [US3] Coverage re-derivation + `docs/standards/OWASP_COVERAGE.md` hand-update: all 10 LLM verdicts with 2026-definition evidence; matrix row per data-model §6; headline + anchor URL; immutable-ADR editorial note (030/045→LLM10:2026, 031→LLM07:2026, 034→LLM06:2026); **reconcile the 10 catalog `# citation:` comments against the re-derived verdicts** (architect MEDIUM-4 from plan review — last wave touching coverage truth reconciles both manual surfaces) [MANUAL-ONLY: hand-authored canon; review gate per FR-009]
- [ ] T020 [US3] D5 consistency test — **sequenced IN or AFTER T019's commit** (the assertion is false-by-construction between T005 and T019 and would redden `tachi-catalog-drift.yml` across three phases; architect HIGH-1 / team-lead F2): add function to `tests/scripts/test_catalog_drift_guard.py` asserting `OWASP_COVERAGE.md` LLM-row edition matches catalog `full_id` edition prefix (CI-gated by `tachi-catalog-drift.yml` — whole-module invocation, zero paths churn; architect plan HIGH-1 corrected placement); optionally add `docs/standards/OWASP_COVERAGE.md` to `&drift_paths` (one line); **declare the expected test-count delta in the commit message** (team-lead F5)
- [ ] T021 [US3] Restatement sweep (closed list): `README.md` ×5 (`:7` poster alt-text + poster-image disposition per PM W3 — regenerate-or-annotate on downgrade, no-op if 50/50 holds; `:19`, `:24`, `:48`, `:390`), `.claude/rules/scope.md:24` (live hit is `:24` only — architect MEDIUM-5 note; a Partial downgrade here is a triad-visible governance edit), `docs/guides/DEVELOPER_GUIDE_TACHI.md:1805,1815`, `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` (in scope — only the base CONSUMER_GUIDE is immutable), `docs/architecture/01_system_design/README.md:130` (**the single init-baseline-tree-mirrored source this feature touches — see T023 for the no-regen ruling**), `docs/INTERFACE-CONTRACT.md`, `docs/architecture/{00_Tech_Stack,03_patterns}/README.md`, `docs/guides/prompts/developer-guide-prompt.md`, `schemas/taxonomy/README.md`, `schemas/taxonomy/cwe.yaml:17` comment

**Checkpoint**: coverage truth consistent end-to-end; D5 test green in CI

---

## Phase 6: Polish & Cross-Cutting Close-out (W5)

**Purpose**: The nets that catch what per-surface work missed, the byte-identity proof, and the paper trail

- [ ] T022 Repo-wide sweep + bare-ledger completion using the VERIFIED command forms in quickstart.md §3: `git grep -nP` suffixed scan; **`git grep -nE 'LLM[[:space:]]+2025|OWASP-LLM-2025'` for the spaced-prose + hyphenated full_id form classes (4 pre-remap hits — architect MEDIUM-5 / PM W1)**; `-oP … | wc -l` occurrence counts; sanity rule: each command must produce hits pre-remap; every remaining hit outside exclusions ledger-dispositioned (SC-002 per D7 = zero undispositioned); complete `bare-code-ledger.md` Tier A 41/41 (union of both lane sections) + Tier B census reconciliation (Σ = 366 in-scope + 103 carve-out)
- [ ] T023 `tests/fixtures/init-baseline-tree/` disposition — **default: DO NOT regenerate** (architect MEDIUM-2, reconciling team-lead F1): the only content-comparing test (`tests/scripts/test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline`) is `@pytest.mark.xfail(strict=False)` under pre-existing staleness tracked in open issue **#345**, so T021's edit to the single mirrored source (`docs/architecture/01_system_design/README.md`) **cannot redden this PR**; a literal regen would land a ~57-file unrelated diff AND silently XPASS #345 without closing it (absorbing another feature's fixture surface — a PM scope call, not builder discretion). Confirm no OTHER baseline source moved; record in delivery notes: "no regen — #345 owns the fixture surface; F-362's one mirrored-source edit noted on #345". Regenerating anyway requires deleting the xfail marker + closing #345 in the same commit — PM approval required
- [ ] T024 Byte-identity + full verification battery on committed HEAD: `test_backward_compatibility.py` green with ZERO baseline bytes changed (FR-007a no-churn proof); integrity suite green; gated subset green; totals reconciled against T001 pre-state **plus the declared T017/T020 deltas** (team-lead F5; xfail/xpass counts expected unchanged — #345's xfail persists); note in evidence that `tachi-catalog-drift.yml` green on the PR is EXPECTED and uninformative (architect MEDIUM-1 from plan review)
- [ ] T025 Changelog: hand-curated Unreleased entry per the repo's dual-changelog model — remap summary, full σ migration table (10 rows old→new token), Hidden Context Exposure rename, ADR-048 hard-cutover policy + one-release breadcrumb convention, F-362b carve-out disclosure incl. mid-window wrong-attribution risk (NEW-3), consumer migration guidance
- [ ] T026 File follow-up issues (architect condition 5 lands here): (a) **F-362b** — blocking-before-next-minor; body checklist: `examples/**` re-key (47 files) + example `source_attribution` σ re-key + unconditional CA-baseline regen + fingerprint-sidecar re-emit (FR-007b causal binding) + 4 non-gated sample-report baselines + `templates/tachi/security-report/coverage-attestation.typ:48` page-title fix + **breadcrumb sunset** (architect MEDIUM-3 from plan review) + mid-window wrong-attribution note + F-362b bare-code ledger (103 transferred refs); (b) `_canonical()` widening — "decided: defer, with rationale" incl. the false-docstring defect (`check-catalog-drift.py:95` vs `:104`); (c) any FR-003 gap issues from T018 (pre-authorized absorption — filed here, never new tasks); (d) non-blocking: note `/aod.score #362` E:5 re-score for PM (team-lead measured landing)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: T001 first (pre-state before ANY edit); then T002 + T004 in parallel; **T003 after T002** (writes into the ledger header T002 scaffolds — architect MEDIUM-3)
- **Phase 2 (Foundational)**: T005 → T006 → T007 (strict serial: catalog names inform edge dispositions; σ before disposition) — BLOCKS all stories. **Cross-phase edges (team-lead F6): T003 → T005 and T003 → T007** (no URL authored before the scheme gate) **and T002 → T006** (the 0-target-endpoint check is the σ oracle precondition)
- **Phase 3 (US1)**: after Phase 2. T008/T009/T011 parallel (ledger lanes disjoint by T002's sections); T010 after T008+T009 (FR-013 sequencing); T012/T013 after T008 (fixtures mirror persona content)
- **Phase 4 (US2)**: after Phase 2; independent of Phase 3 — T014/T016 parallel; T015 → T017 (test asserts the fixed emitter)
- **Phase 5 (US3)**: T018 → T019 → T021 (evidence before verdicts before restatements); **T018 has no Phase-3 dependency — run it in the Session-B window (team-lead F7)**; **T020 in or after T019's commit** (architect HIGH-1 / team-lead F2 — never between T005 and T019)
- **Phase 6 (Polish)**: after Phases 3–5 complete; T022 → T023 → T024 serial (sweep before fixture disposition before final battery); T025/T026 parallel after T024

### Critical Path (team-lead F7 corrected)

**T001 → T005 → T006 → T007 → T018 → T019 → T021 → T022 → T024 → T025/T026** — the human-judgment chain T018→T019→T021 paces the feature (three serial tasks, two [MANUAL-ONLY]-cored, one review-gated canon, with a downgrade branch cascading to 11 restatement surfaces), not T010's mechanical 17-file bucket. T007's 74-edge disposition remains the densest single task. Neither bottleneck compresses by parallelization.

### Parallel Opportunities

- After T001: T002 + T004 together (T003 follows T002)
- After Phase 2: US1 lanes (T008, T009, T011) + US2 lanes (T014, T016) — up to 5 concurrent buckets; T018 may join the same window (different files, no Phase-3 dependency); peak load stays ≤70% per the feasibility wave model (no agent >80%)
- T015 can start with US1 in flight (different files)
- If the curator is solo, cap concurrency at 4 lanes and prioritize T008/T009 (they carry ~all of the wave's semantic review burden — team-lead advisory)

---

## Parallel Example: Post-Foundational fan-out

```bash
# After T007 completes, launch the wave together (T020 deliberately absent — it lands with T019):
Task: "T008 Personas bucket: the 9 LLM-ref-bearing personas in .claude/agents/tachi/ ..."
Task: "T009 Skill references bucket: 15 files ..."
Task: "T011 Legacy mirrors bucket: 4 files ..."
Task: "T014 Contract examples: schemas/finding.yaml ..."
Task: "T016 Parser warning: scripts/extract-report-data.py ..."
Task: "T018 Gap analysis: 4 absorption records ..."
```

---

## Implementation Strategy

### MVP First (Foundational + User Story 1)

1. Phase 1 (T001–T004) then Phase 2 (T005–T007) — the source of truth flips to 2026
2. Phase 3 (T008–T013) — every authored surface follows
3. **STOP and VALIDATE**: US-1 independent test (integrity suite + bucket checklists + local gated subset) — this alone delivers the core product truth (findings cite the current standard)

### Incremental Delivery

1. + Phase 4 (US2) → contract/emitters/tests, CI-gated — consumers get the documented transition
2. + Phase 5 (US3) → coverage truth re-derived — the claim is honest
3. + Phase 6 → sweep nets, byte-identity proof, changelog, follow-ups — delivery-clean per KB 16

### Session Strategy (team-lead C-plan + KB clean-session phasing, F7 amendment adopted)

- Session A (~1.6d): Phase 1 + Phase 2 (T001–T007) — serial spine, T007 dominates
- Session B (~1.15d): Phase 3 (T008–T013) **+ T018 pulled forward** (any Partial-downgrade discovery lands with two sessions of runway instead of one)
- Session C (~1.35d): Phase 4 (T014–T017) + Phase 5 remainder (T019, T020, T021)
- Session D (~0.9d): Phase 6 (T022–T026) + deliver prep

### Deliver-Stage Reminders (not tasks — /aod.deliver checklist inputs)

- Live link-rot `workflow_dispatch` (`no_cache: true`) — validates the 54 re-anchored URLs + 10 record URLs (KB 17; expect #332 tracker churn; new rot → file, don't absorb)
- **SC-005 PM re-verification (PM W3): PM confirms every restatement surface carries the re-derived number and any Partial downgrade is published, not suppressed — before the PR is marked ready**
- KB 18 hygiene: branch current, `main`==`origin/main` full-tree diff before merge/doc-push
- `feat(362):` PR title; release-please verification post-merge
- ADR-048 `Accepted-commit-SHA` post-merge fill

---

## Notes

- Counts are research-measured at `747805c` and normative (spec discrepancy table); ledger completion bars per `contracts/disposition-ledgers.md`
- Bucket-scoped tasks: a bucket's per-file checklist lives in its commit message / ledger rows, not as sub-tasks
- Commit after each task or logical group; the byte-identity harness clones committed HEAD
- [MANUAL-ONLY] cores: T007 (edge semantics), T018 (evidence), T019 (canon review) — these are the honest human bottlenecks; do not fake-automate them
- **26-task ceiling = hard absorption boundary (team-lead ruling)**: work discovered in-loop is absorbed into an existing task's scope or filed as a follow-up issue — never added as T027 without team-lead re-sign-off. Pre-authorized absorptions: T003 interim-anchor substitutions → T007 ledger rows; FR-003 gaps → T026(c); a T019 Partial-downgrade cascade → T021 (closed restatement list, mechanical propagation)
