---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-29
    status: APPROVED_WITH_CONCERNS
    notes: "Plan faithfully implements the PM-approved spec (FR-001..009 map 1:1, no scope creep/drift). FR-009 surgical and gate-bound (canonical-5-key edits only, hard SC-001/SC-006 dependency from OQ-3 RED; does not breach FR-008 content fence; knowledge-system = add-TECH_STACK + remove-ORCHESTRATION_TARGET dual-edit, others additive-only — re-verified live). FR-006/FR-007 groundwork (99507b2) correctly listed as completed deps, not re-tasked. SC-001..006 preserved; SC-005 byte-parity honestly NOT claimed (behavioral parity + confirmation diff + W-1 spot-check is the oracle). S-1 deliver gate + FR-008 fence preserved. data-model.md/contracts/ omission product-acceptable (bash/CI tooling; intentional code-economy). 2 MINOR non-gating: (1) inherited stale git-describe label v4.44.0-1-g5b64f68 vs live v4.0.0-302-g5b64f68 — SHA 5b64f68 is authoritative+consistent, restore correctness unaffected; (2) FR-002 honest sharpening (names F-256 Site A loader), already reconciled. No veto. Full: .aod/results/product-manager-plan.md"
  architect_signoff:
    agent: architect
    date: 2026-06-29
    status: APPROVED
    notes: "All 5 cut-line decisions ratified against the live tree (HEAD 99507b2 vs 5b64f68); 0 blocking, 2 non-gating obs. OQ-1: manifest IS more hardened at HEAD (user|/merge| vs owned|), stack-active.json unchanged → do-not-revert correct. OQ-2: 0 surviving hardening markers in all 3 HEAD files → clean generic-revert, direct checkout (not 3-way) confirmed. OQ-3/FR-009: loader unchanged, enforces both whitelist bounds (L290-330); all 5 packs missing TECH_STACK, knowledge-system has disallowed ORCHESTRATION_TARGET → suite physically can't go green without FR-009; surgical-not-whole-file scoping verified necessary (TECH_STACK line interleaved with FR-008-fenced comments). MEDIUM-3: update.sh 0 hardening-signal hits, not in CI paths → out-of-scope/untouched correct. LOW-3: branch-vs-5b64f68 = 31 files → restore-commit baseline correct. Also verified bash 3.2 compat (banned-construct hits are avoidance-comments), S-2 sequence, S-1 gate, honest behavioral-not-byte parity (FR-007 xfail live), code-economy omissions. OBS-2: tasks.md should render the 2 [MANUAL-ONLY] oracles (W-1, SC-004) as auditable checklist items. Full: .aod/results/architect-plan.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Restore F-248/F-256 Substitution Hardening

**Branch**: `338-restore-substitution-hardening` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/338-restore-substitution-hardening/spec.md` (PM-approved 2026-06-29)
**Research**: [research.md](./research.md) (Phase 0 — complete; OQ-3 resolved empirically)

## Summary

Restore the F-248 (placeholder-substitution) and F-256 (source-pattern + clone-timeout) hardening that a
2026-06-28 `/aod.update` template re-sync silently reverted on public `main`. The restore source is
known-good v4.44.0 code (`5b64f68`). For the three in-scope file bodies the operation is a **clean
generic-revert** — `git checkout 5b64f68 -- <3 files>` + a confirmation diff (NOT a 3-way merge) — because
the files were reverted completely to upstream-generic with no surviving in-file change to preserve. A
fourth, gate-blocking surface — the canonical `defaults.env` key set (FR-009) — is pulled in-scope because
the restored loader requires it (OQ-3, resolved RED in research.md). The standing guardrail (FR-006 push
gate) and the unrelated-staleness quarantine (FR-007 xfail) already landed in `99507b2` and are NOT
re-implemented here. Acceptance is the F-248/F-256 CI-gated suite green on both bash-version matrix legs +
a confirmation/byte diff vs `5b64f68`.

## Technical Context

**Language/Version**: bash, constrained to **3.2.57+** (F-248 NFR-001 — macOS `/bin/bash` is the hard
compatibility floor: no `mapfile`, no associative arrays, no `${var,,}`).
**Primary Dependencies**: none added. Existing pytest harness only (`pytest>=8`, `pytest-timeout>=2`,
`pyyaml>=6`), installed by CI. Restored `init.sh` sources the already-present, unchanged
`.aod/scripts/bash/template-config-load.sh` (provides `aod_template_load_kv_file`).
**Storage**: N/A (no datastore). Operates on tracked shell scripts + `stacks/*/defaults.env` config files.
**Testing**: pytest matrix in `.github/workflows/tachi-pytest.yml` — two legs: `macos-latest` (bash 3.2.57,
strict compat gate) + `ubuntu-latest` (bash 5.x, modern reference). The suite IS the behavioral oracle.
**Target Platform**: developer/CI shells (macOS bash 3.2 + Linux bash 5.x). The artifact is the tachi
adopter-scaffolding tooling that runs on `main`.
**Project Type**: single (CLI/tooling + test harness). No frontend, no backend, no API.
**Performance Goals**: N/A as a target; the ADR-038 substitution-time tradeoff (parameter-expansion vs
`sed`) is already accepted design, not re-litigated here.
**Constraints**: bash 3.2.57 compat (hard); **S-1 deliver gate** (do NOT push the branch / open the PR
until the restore is green locally — the FR-006 `push:[main]` gate would otherwise redden `main`).
**Scale/Scope**: 3 file-body restores + 5 `defaults.env` key-surface fixes (1 line/file) + verification. M
effort, cut-line-bound (not LOC-bound); single Plan→Build→Deliver cycle, do not split.

## Constitution Check

*GATE: must pass before build. Re-checked post-design (below).*

| Principle | Relevance | Status |
|-----------|-----------|--------|
| I. General-Purpose Architecture | The hardening is domain-agnostic bash/templating; restoration adds no domain logic | ✅ PASS |
| III. Backward Compatibility (NON-NEGOTIABLE) | Restore RE-ESTABLISHES v4.44.0 behavior; `init.sh` output stays byte-deterministic where the live suite asserts it (the one xfail'd baseline is pre-existing #329, guarded by the W-1 manual byte spot-check so the restore can't silently change output) | ✅ PASS |
| VI. Testing Excellence (NON-NEGOTIABLE) | Behavioral coverage exists and gates the work (canary + adversarial + clone-timeout + config-load); restore is accepted only on 2/2 green legs | ✅ PASS |
| VII. Definition of Done (NON-NEGOTIABLE) | Deliver via DoD: pushed to main (post-green), tested (CI both legs), validated (confirmation diff + canary) | ✅ PASS (gated at deliver) |
| IX. Git Workflow (NON-NEGOTIABLE) | On feature branch `338-*`; no direct-main commit; conventional-commit PR title; S-1 pre-push CI-green checkpoint | ✅ PASS |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | PM sign-off on spec ✓; PM+Architect dual sign-off on this plan (in progress); triple on tasks next | ✅ in progress |
| Code-Economy laziness ladder | Rung 2 (reuse) / rung 1 (spec requires it — shipped-regression fix): restore tested known-good code, zero net-new abstraction, zero new deps (rung 5) | ✅ PASS |
| II API-First · IV Concurrency · V Privacy · VIII Observability | No API, no concurrency, no user-data, no service runtime in this surface | N/A |

**No violations** → Complexity Tracking table intentionally empty. No over-engineering: the restore is the
minimum that satisfies the spec + safety carve-outs; `data-model.md` and `contracts/` are omitted because
the feature introduces no data model and no API (forcing those artifacts would be cargo-cult generation —
see Project Structure).

## Implementation Approach

### Restore surface (what changes, and how)

| # | Target | Method | Acceptance |
|---|--------|--------|------------|
| 1 | `.aod/scripts/bash/template-substitute.sh` | `git checkout 5b64f68 -- <file>` (whole body) | `test_substitute_shim_canary.py` + `test_template_substitute_unit.py` green; patsub shim present |
| 2 | `scripts/init.sh` | `git checkout 5b64f68 -- <file>` (whole body — restores BOTH F-248 substitution AND F-256 Site A loader) | `test_init_sh_substitution.py` / `test_init_sh_adversarial.py` green (modulo FR-007 xfail) |
| 3 | `.aod/scripts/bash/template-git.sh` | `git checkout 5b64f68 -- <file>` (whole body) | `test_template_git_clone_timeout.py` green; `AOD_FETCH_TIMEOUT` watchdog present |
| 4 (FR-009) | `stacks/{nextjs-supabase,fastapi-react,fastapi-react-local,swiftui-cloudkit,knowledge-system}/defaults.env` | add `TECH_STACK="<pack>"` (5b64f68 values); **remove** disallowed `ORCHESTRATION_TARGET` from `knowledge-system` | `test_init_sh_defaults_env.py` green both legs; 5/5 packs exit 0 under the restored loader |

> **FR-009 values** (from `5b64f68`): `nextjs-supabase`→`nextjs`, `fastapi-react`→`fastapi-react`,
> `fastapi-react-local`→`fastapi-react-local`, `swiftui-cloudkit`→`swiftui-cloudkit`,
> `knowledge-system`→`knowledge-system`. Each pack's resulting key set must EXACTLY equal the canonical 5
> (`TECH_STACK, TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH, CLOUD_PROVIDER`) — the loader
> enforces both bounds (unknown-key reject + missing-key completeness). For `defaults.env` files 1-4 the
> fix is purely additive (add `TECH_STACK`); `knowledge-system` is add `TECH_STACK` + remove
> `ORCHESTRATION_TARGET` (i.e. restore it to its `5b64f68` state). **Surgical key edits, NOT a whole-file
> checkout** of `defaults.env` — those files also carry legit non-key content that is out of scope (FR-008).

### Build sequence (S-2, single wave — no parallelism)

1. Restore the 3 file bodies (surface 1-3) from `5b64f68`.
2. Apply the FR-009 canonical-key edits (surface 4).
3. Run the F-248/F-256 gated suite locally on bash 3.2 (macOS) and, if reachable, bash 5.x — else rely on CI.
4. **W-1 byte spot-check**: diff the 3 restored bodies vs `5b64f68` (expect generic→hardened direction only,
   near-empty noise) — closes the gap left by the xfail'd byte-identity baseline (FR-007).
5. **SC-004 audit**: the restore commit's diff (branch-vs-`main`-pre-restore) touches only the 8 in-scope
   paths (3 scripts + 5 defaults.env); every other branch delta is named in FR-008.
6. Deliver gate (**S-1**): push/PR only after the restore is green locally; merge via devops; verify release-please.

### Cut-line decisions ratified at plan (architect to confirm)

- **OQ-1 — restore surface = 3 file bodies + FR-009 keys.** Do **NOT** revert `.aod/template-manifest.txt`
  (HEAD's `user|init.sh` / `merge|` libs is *more* hardened than `5b64f68`'s `owned|` — reverting regresses
  it). `.aod/stack-active.json` is adopter state, out-of-surface.
- **OQ-2 — method = direct restore + confirmation diff**, not a 3-way merge (the 3 files are a clean
  generic-revert; verified zero surviving tachi/F-248/F-256 markers at HEAD).
- **OQ-3 — RESOLVED RED → FR-009 pulled in-scope.** The restored exact-set whitelist loader
  (`template-config-load.sh` L290-330, unchanged) makes the gated suite physically unable to go green with
  `TECH_STACK` absent. Minimal canonical-key restoration is therefore a hard dependency of SC-001/SC-006.
- **`scripts/update.sh` (architect MEDIUM-3)** — classified **out-of-scope / untouched**: its
  `5b64f68..HEAD` delta carries no hardening signal (it is the legit upstream refresh). Named in FR-008 so
  SC-004 stays auditable; not restored, not modified.
- **SC-004 measurement baseline (architect LOW-3)** — measured as the **restore commit's** diff
  (branch-vs-`main`-pre-restore), NOT branch-vs-`5b64f68` (the branch sits atop a ~30-file update delta).

### Parity oracle (SC-005, honest framing)

Suite-green proves **behavioral** parity (canary `AT&T→AT&T`, adversarial rejection, clone-timeout,
config-load). **Byte**-identity is NOT asserted this cycle (the baseline test is xfail'd under #329). The
FR-004 confirmation diff + the W-1 manual byte spot-check vs `5b64f68` are the complementary parity guard.

## Risks & Mitigations

| Risk | L / I | Mitigation |
|------|-------|------------|
| FR-009 mis-scoped (whole-file checkout of `defaults.env` would pull out-of-scope content) | L / M | FR-009 is **surgical key edits only**; confirmation against `5b64f68` key set; SC-004 audit |
| bash 3.2.57 regression in restored code | L / M | macOS matrix leg is a hard gate; code is known-good v4.44.0 (already passed this leg) |
| Premature push reddens `main` | M / H | S-1 deliver-gate: no push/PR until green locally; merge through devops |
| Byte change in init.sh output absorbed by xfail | L / M | W-1 manual byte spot-check vs `5b64f68` as FR-005 acceptance |
| Re-clobber on next `/aod.update` | M / H | Detection via FR-006 push gate (landed); operator `--dry-run`/`git diff --stat` insurance (process, referenced not built) |

## Project Structure

### Documentation (this feature)
```
specs/338-restore-substitution-hardening/
├── spec.md              # PM-approved
├── research.md          # Phase 0 — complete (OQ-3 resolved)
├── plan.md              # This file
├── quickstart.md        # Verification recipe (Phase 1 — the one applicable design artifact)
├── feasibility-check.md # Team-Lead (from /aod.define)
└── tasks.md             # /aod.tasks output (next)
```
**Omitted by design**: `data-model.md` (no data entities — operates on shell scripts + KV config files;
see spec Key Entities) and `contracts/` (no API surface). Omission is intentional code-economy, not a gap.

### Source code (restore surface — repository root)
```
scripts/init.sh                                   # restore (F-248 substitution + F-256 Site A loader)
.aod/scripts/bash/template-substitute.sh          # restore (F-248 patsub shim + Site D loader)
.aod/scripts/bash/template-git.sh                 # restore (F-256 AOD_FETCH_TIMEOUT watchdog)
stacks/*/defaults.env  (5 packs)                  # FR-009 canonical-key surgical edits
# UNCHANGED / NAMED-UNTOUCHED:
.aod/scripts/bash/template-config-load.sh         # present + unchanged; restored init.sh sources it
.aod/template-manifest.txt                        # do NOT revert (more hardened at HEAD)
scripts/update.sh                                 # not a hardening surface; untouched (SC-004 auditability)
.github/workflows/tachi-pytest.yml                # FR-006 gate — landed 99507b2, do not re-task
tests/scripts/*                                   # the behavioral oracle (one baseline xfail'd, FR-007)
```
**Structure Decision**: in-place restoration of existing tooling files; no new modules, directories, or
abstractions. This is a regression fix on shipped code, not greenfield design.

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*
