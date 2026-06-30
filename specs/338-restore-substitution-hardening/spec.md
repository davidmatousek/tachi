---
prd_reference: docs/product/02_PRD/338-restore-substitution-hardening-2026-06-29.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-29
    status: APPROVED
    notes: "Faithful, complete, traceable derivation of the approved PRD. FR-001..008 map 1:1; US-338.1/2/3 covered; landed groundwork (FR-006/FR-007) correctly cordoned 'do not re-task'; SC-001..006 clear and measurable. The one substantive deviation — FR-009 pulling the TECH_STACK key restoration in-scope — is a PRD-pre-authorized OQ-3 resolution (option a), NOT scope creep: independently re-verified against the live tree (v4.44.0-7-g99507b2) that the restored exact-set whitelist loader (template-config-load.sh L290-330) makes the gated suite physically unable to go green with TECH_STACK absent, so FR-009 is a hard dependency of the PRD's own SC-001. FR-009 correctly bounded to the canonical-5-key surface (= knowledge-system@5b64f68 state); does not breach FR-008's content/docs fence. 2 MINOR/observational findings (P-label band downshift P0/1/2→P1/2/3 with order preserved; FR-002 honestly sharpened to name the F-256 Site A loader init.sh also carries), neither gating. Constitution Principle VIII satisfied. Full: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Restore F-248/F-256 Substitution Hardening

**Feature Branch**: `338-restore-substitution-hardening`
**Created**: 2026-06-29
**Status**: Draft
**Input**: PRD #338 — `docs/product/02_PRD/338-restore-substitution-hardening-2026-06-29.md` (BLP-06 Wave 2, F-2)
**Research**: `specs/338-restore-substitution-hardening/research.md`

> **What this feature is**: a *restoration* of shipped security hardening that a `/aod.update`
> template re-sync (2026-06-28) silently reverted on public `main`, plus a standing guardrail so it
> can never be reverted silently again. The restore source is known-good v4.44.0 code (`5b64f68`);
> this feature does not re-design the hardening (ADR-038 / ADR-040 own that), it puts it back.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Restore the lost hardening to `main` (Priority: P1)

A tachi **adopter** scaffolds a project from current `main` via `scripts/init.sh` / template
substitution. They must get the same safe, hardened behavior the v4.44.0 release advertised: `&`-bearing
values (`AT&T`, `R&D`) stay literal during placeholder substitution, malicious `defaults.env` content
cannot execute, and a hung template upstream cannot block `init` forever.

**Why this priority**: This is the regression. Public `main` is the source-of-truth adopters install
from; it currently ships *less* hardening than the tagged release (the F-248 `AT&T`-corruption class is
back, `defaults.env` `source`-execution is back, clone has no timeout). Restoring it is the entire point
of the feature; everything else is guardrail. P1.

**Independent Test**: Restore the three file bodies + the canonical `defaults.env` key surface, then run
the F-248/F-256 CI-gated suite on both matrix legs (macOS bash 3.2.57 + ubuntu bash 5.x). Green on both
legs + a clean confirmation diff vs `5b64f68` proves the value is delivered.

**Acceptance Scenarios**:

1. **Given** `template-substitute.sh` on `main`, **When** I inspect it, **Then** the F-248
   `patsub_replacement` shim is present (`shopt -u patsub_replacement` guard).
2. **Given** a `{{PROJECT_NAME}}` substitution with an `AT&T`-style value on bash 5.2+, **When** `init`
   runs, **Then** the output is `AT&T`, never `AT{{PROJECT_NAME}}T` (the ADR-038 / F-248 canary passes).
3. **Given** `scripts/init.sh` on `main`, **When** I inspect substitution, **Then** it uses the F-248
   parameter-expansion + input-validation path (not the upstream `sed` path), **and** the F-256 Site A
   `aod_template_load_kv_file ... STACK_PACK_ALLOWED_KEYS` loader (not a plain `source defaults.env`).
4. **Given** a stack pack whose `defaults.env` contains `CUSTOM_HOOK="$(touch /tmp/pwned)"`, **When**
   `init` loads it, **Then** the load is rejected (exit 8) and `/tmp/pwned` is never created.
5. **Given** `template-git.sh` on `main`, **When** a clone targets an unresponsive upstream, **Then** the
   F-256 `AOD_FETCH_TIMEOUT` watchdog bounds the fetch.
6. **Given** each shipped stack pack (`nextjs-supabase`, `fastapi-react`, `fastapi-react-local`,
   `swiftui-cloudkit`, `knowledge-system`), **When** `init` runs against it under the restored loader,
   **Then** it loads cleanly (exit 0) — its `defaults.env` key set exactly equals the canonical 5
   (`TECH_STACK`, `TECH_STACK_DATABASE`, `TECH_STACK_VECTOR`, `TECH_STACK_AUTH`, `CLOUD_PROVIDER`).
7. **Given** the F-248 + F-256 CI-gated suite, **When** it runs on `main`, **Then** both matrix legs are green.

---

### User Story 2 — Make a future direct-to-`main` clobber visible immediately (Priority: P2) — ✅ landed (`99507b2`)

A tachi **maintainer** runs `/aod.update` (or any direct-to-`main` push). If it reverts a hardening-surface
file, CI must fail on the push so the regression is caught on `main` in minutes instead of shipping
silently to adopters.

**Why this priority**: Detection of recurrence. This is the second occurrence of this exact clobber; the
manifest-classification fix tried last time did not hold, so an automated red-build signal is the
load-bearing control. P2 because the groundwork already landed — this story is documented for traceability.

**Independent Test**: Inspect `tachi-pytest.yml` triggers; confirm a `push: branches:[main]` trigger reuses
the `pull_request` `paths` via a single YAML anchor.

**Acceptance Scenarios**:

1. **Given** `tachi-pytest.yml`, **When** I inspect its triggers, **Then** it has a `push: branches:[main]`
   trigger whose `paths` is the same YAML anchor as `pull_request` (no third drift-prone path list).
2. **Given** a direct-to-`main` push touching a hardening-surface path, **When** CI runs, **Then** the
   F-248/F-256 suite executes (not skipped by the path filter).

---

### User Story 3 — Land the restore green without masking unrelated staleness (Priority: P3) — ✅ landed (`99507b2`)

A pre-existing, unrelated baseline-fixture test (`test_personalized_tree_bytes_match_baseline`, red since
*before* the clobber, tracked under #329) must be quarantined so green CI reads as "hardening restored,"
not a conflation with fixture-staleness — without permanently hiding it.

**Why this priority**: Read-clarity of the green signal. P3 because the groundwork already landed;
documented for traceability.

**Acceptance Scenarios**:

1. **Given** `test_personalized_tree_bytes_match_baseline`, **When** the suite runs, **Then** it is
   `xfail(strict=False)` with a #329 reason.
2. **Given** a future fixture regen that fixes the staleness, **When** the suite runs, **Then** the test
   **XPASSes** (the signal to delete the marker).

---

### Edge Cases

- **Extra non-whitelisted key after restore**: `knowledge-system/defaults.env` currently carries a
  re-added `ORCHESTRATION_TARGET` (not in the canonical 5). Under the restored whitelist loader the in-pass
  check rejects it (exit 8) — so the restore MUST remove it, not just add `TECH_STACK` (FR-009).
- **`&`-bearing value on bash 5.2+ without the shim**: substitutes to corrupted `AT{{PROJECT_NAME}}T` —
  exactly the F-248 regression the shim closes (AC 1.2).
- **Unresponsive clone upstream**: without the watchdog, `init` hangs indefinitely; with FR-003 restored,
  `AOD_FETCH_TIMEOUT` (default 60s) bounds it (AC 1.5).
- **Premature push of the branch**: the FR-006 `push:[main]` gate would redden `main` on the branch's own
  behalf if pushed/merged before the restore is green — addressed by the deliver-gate constraint (FR-008 / S-1).
- **Restore introduces a byte change in init.sh output**: the xfail'd baseline test would absorb it
  silently — caught instead by the W-1 manual byte spot-check (FR-005), since green CI alone no longer
  proves byte parity.
- **bash 3.2.57 incompatibility in restored code**: caught by the macOS matrix leg (hard gate); risk is
  Low — the code is known-good from v4.44.0, which already passed this leg.

---

## Requirements *(mandatory)*

### Functional Requirements

> **Traceability**: FR-001…FR-008 map 1:1 to PRD #338 FR-001…FR-008. **FR-009 is new** — it records the
> OQ-3 resolution (the `defaults.env` gate state, resolved RED in research.md) and supersedes FR-008's
> bullet-2 fence on the `TECH_STACK` key. Acceptance Criteria use Given/When/Then; `[MANUAL-ONLY]` marks ACs
> that cannot be automated.

- **FR-001 — Restore the F-248 `patsub_replacement` shim (`template-substitute.sh`)**: `.aod/scripts/bash/template-substitute.sh`
  MUST restore the F-248 shim that disables bash 5.2+ `patsub_replacement`, so `&` in a replacement value
  is literal.
  - **AC**: **Given** the restored file, **When** `test_substitute_shim_canary.py` runs on bash 5.x, **Then** it is green (`AT&T → AT&T`).

- **FR-002 — Restore the F-248 substitution + F-256 Site A loader (`scripts/init.sh`)**: `scripts/init.sh`
  MUST restore the F-248 parameter-expansion + input-validation substitution path (replacing the
  upstream-generic `sed` path) **and** the F-256 Site A `aod_template_load_kv_file ... STACK_PACK_ALLOWED_KEYS`
  loader (replacing the plain `source "stacks/$PACK/defaults.env"`).
  - **AC**: **Given** the restored init.sh, **When** the `test_init_sh_substitution.py` / `test_init_sh_adversarial.py` suite runs, **Then** it is green (modulo the #329 xfail, FR-007).

- **FR-003 — Restore the F-256 git-clone-timeout hardening (`template-git.sh`)**: `.aod/scripts/bash/template-git.sh`
  MUST restore the F-256 `AOD_FETCH_TIMEOUT` bounded-fetch watchdog.
  - **AC**: **Given** the restored file, **When** `test_template_git_clone_timeout.py` runs, **Then** it is green.

- **FR-004 — Restore method = clean generic-revert + confirmation diff**: the restore of the three
  in-scope files MUST be a **direct restore of the three file bodies from `5b64f68`** followed by a
  **confirmation diff**, NOT a 3-way hand-merge. (Verified: the three HEAD files are a complete
  generic-revert with zero surviving tachi/F-248/F-256 markers — there is no in-file legit change to
  preserve. The reconciliation caution applies only to the out-of-scope docs/`defaults.env`-content
  surface fenced by FR-008.)
  - **AC**: **Given** the restored three files, **When** diffed against `5b64f68`, **Then** the delta is the
    generic→hardened direction only, with no discarded non-hardening upstream change. `[MANUAL-ONLY]` confirmation-diff review.

- **FR-005 — CI-green on both matrix legs + byte spot-check**: after the restore, the F-248 + F-256
  CI-gated suite MUST pass on **both** matrix legs (macOS bash 3.2.57 — strict compatibility; ubuntu bash 5.x —
  modern reference). Green CI proves the *behavioral* assertions; the FR-004 confirmation diff is the
  complementary *parity* oracle. A manual byte spot-check of the three restored bodies vs `5b64f68` is part
  of acceptance (the byte-identity baseline test is xfail'd under FR-007, so green CI alone does not prove byte parity).
  - **AC**: **Given** the restore, **When** the gated suite runs on both legs, **Then** 2/2 legs are green; **and** **Given** the three restored bodies, **When** byte-compared to `5b64f68`, **Then** they match. `[MANUAL-ONLY]` byte spot-check.

- **FR-006 — Gate `tachi-pytest` on direct main pushes** *(✅ landed `99507b2`)*: `tachi-pytest.yml` MUST
  run on `push:[main]` (not only `pull_request`), reusing the PR `paths` via a single YAML anchor. *Done in
  groundwork; documented for traceability — do not re-task.*
  - **AC**: **Given** `tachi-pytest.yml`, **When** triggers are inspected, **Then** `push:[main]` is present and shares the `pull_request` `paths` anchor.

- **FR-007 — Quarantine the pre-existing baseline staleness** *(✅ landed `99507b2`)*:
  `test_personalized_tree_bytes_match_baseline` MUST be `xfail(strict=False)` with a #329 reason. *Done in
  groundwork; documented for traceability — do not re-task.*
  - **AC**: **Given** the suite, **When** it runs, **Then** the baseline test is xfail (and XPASSes only after a future #329 fixture regen).

- **FR-008 — Scope fence (constraint)**: this feature MUST NOT undertake (each a separate follow-up):
  - the broader **content** reconciliation of `docs/devops/CI_CD_GUIDE.md`, `docs/devops/README.md`,
    `docs/standards/README.md`, `AOD_GUIDE_INDEX.md`, `AOD_QUICKSTART.md` (the real Sprint→Loop refresh);
  - the **#329** enrichment-cap / byte-identity baseline drift (FR-007 only quarantines it, does not fix it);
  - `.aod/template-manifest.txt` — MUST NOT be reverted (HEAD's `user|init.sh` / `merge|` libs is *more*
    hardened than `5b64f68`'s `owned|`; reverting regresses it — OQ-1);
  - `scripts/update.sh` — NOT a hardening surface (no hardening signal in its `5b64f68..HEAD` delta); left
    explicitly untouched, named here for SC-004 auditability;
  - **preventing** a future `/aod.update` re-clobber *at the source* — this feature provides *detection*
    (FR-006); the complementary operator-process insurance (mandatory checkpoint + `--dry-run` +
    `git diff --stat` the at-risk set) is referenced, not built.
  - **Superseded**: the PRD's tentative fence on the `TECH_STACK` key is lifted — see FR-009 (OQ-3 resolved RED).

- **FR-009 — Restore the canonical `defaults.env` key surface (OQ-3 resolution; pulled in-scope)**: to
  satisfy FR-005 (the gated `test_init_sh_defaults_env.py` cannot go green otherwise — research.md), each
  shipped stack pack's `defaults.env` MUST present **exactly** the canonical 5 keys the restored loader's
  `STACK_PACK_ALLOWED_KEYS` requires. Concretely: restore `TECH_STACK="<pack>"` to all five packs
  (`nextjs-supabase`→`nextjs`, `fastapi-react`, `fastapi-react-local`, `swiftui-cloudkit`,
  `knowledge-system`) and remove the disallowed `ORCHESTRATION_TARGET` from `knowledge-system`. This is the
  PRD-sanctioned OQ-3 "option a" (1 line/file). Values are the `5b64f68` values.
  - **AC**: **Given** the restored packs, **When** `init` runs against each under the restored loader, **Then** each loads cleanly (exit 0) and `test_init_sh_defaults_env.py` is green on both legs.

### Key Entities *(artifacts this feature operates on — no new data model)*

- **Hardening file bodies (3)**: `.aod/scripts/bash/template-substitute.sh`, `scripts/init.sh`,
  `.aod/scripts/bash/template-git.sh` — restored verbatim from `5b64f68`.
- **Canonical `defaults.env` key surface**: the 5 shipped packs' `defaults.env`; key set must exactly equal
  `{TECH_STACK, TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH, CLOUD_PROVIDER}` (FR-009).
- **CI gate**: `.github/workflows/tachi-pytest.yml` — the 2-runner bash-version matrix with the
  `pull_request` + `push:[main]` shared-anchor `paths` (FR-006).
- **Test suite**: `tests/scripts/` F-248/F-256 modules — the behavioral oracle; one baseline test xfail'd (FR-007).
- **Restore reference**: `5b64f68` (`v4.44.0-1-g5b64f68`) — last-good source of truth.
- **Untouched-but-named**: `scripts/update.sh`, `.aod/template-manifest.txt` (named for SC-004 / OQ-1; not modified).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (CI green)**: the F-248/F-256 CI-gated suite passes on `main` on **both** matrix legs. **Target: 2/2 legs green.**
- **SC-002 (canary)**: `test_substitute_shim_canary.py` passes — `AT&T → AT&T`. **Target: pass (F-248 regression class closed).**
- **SC-003 (gate live)** *(✅ landed)*: `tachi-pytest.yml` has a `push:[main]` trigger that fires on a hardening-surface path change. **Target: present & firing.**
- **SC-004 (scope discipline)**: the **restore commit's** diff (measured branch-vs-`main`-pre-restore, NOT
  branch-vs-`5b64f68`) touches only in-scope hardening surfaces (the 3 files + the 5 `defaults.env` per FR-009);
  every out-of-scope delta already on the branch is named in FR-008. **Target: 0 unaccounted out-of-scope files in the restore commit.**
- **SC-005 (parity to v4.44.0)**: the restored three file bodies reproduce last-good v4.44.0 behavior,
  validated by the FR-004 confirmation diff vs `5b64f68` + the canary/adversarial/clone-timeout/config-load
  suites. **Behavioral parity is the asserted target; full byte-parity is NOT claimed this cycle** (the
  byte-identity baseline test is xfail'd under #329). **Target: behavioral parity + confirmation-diff clean.**
- **SC-006 (defaults.env loads clean — OQ-3)**: under the restored loader, all 5 shipped packs load cleanly
  and `test_init_sh_defaults_env.py` is green on both legs. **Target: 5/5 packs exit 0; defaults.env suite green.**

---

## Assumptions

- The F-248/F-256 hardening at `5b64f68` (`v4.44.0-1-g5b64f68`) is the correct last-good reference and
  reproduces v4.44.0 behavior (shim/watchdog/loader verified intact there; gone on `main`).
- Suite-green proves **behavioral** parity (canary + adversarial + clone-timeout + config-load); **byte**-identity
  is NOT asserted this cycle (baseline xfail'd under #329). The FR-004 confirmation diff is the parity oracle.
- The three in-scope files are a clean generic-revert (verified) — restore is checkout + confirmation diff.
- `template-config-load.sh` is unchanged `5b64f68..HEAD` and present at HEAD (the restored init.sh sources it) — no library restoration needed.
- OQ-3 resolved **RED** (research.md): the restored loader requires the canonical 5-key set exactly, so
  FR-009's `defaults.env` key restoration is a hard dependency of SC-001/SC-006, not optional.

## Dependencies

- **Last-good reference**: `5b64f68` — the restore source (verified intact).
- **In-branch groundwork**: `99507b2` (FR-006 push gate + FR-007 xfail; = branch tip) — US-2 / US-3 done; list as completed deps, do not re-task.
- **Design rationale (honor, do not re-litigate)**: ADR-038 (F-248 substitution strategy), ADR-040 (F-256 config-file parsing hardening).
- **Tracking ref**: #329 (enrichment-cap / byte-identity drift; fixture regen) — the FR-007 xfail's pointer.

## Out of Scope

Per FR-008: broader docs/devops Sprint→Loop content reconciliation; `.aod/template-manifest.txt` revert
(do NOT — it is more hardened at HEAD); `scripts/update.sh` (not a hardening surface; untouched); the #329
baseline-drift fix; source-prevention of a future `/aod.update` re-clobber (detection only). **Note**: the
`TECH_STACK` key restoration, tentatively out-of-scope in the PRD, is pulled IN-scope as FR-009 because OQ-3
resolved RED.
