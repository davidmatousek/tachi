# NEXT-SESSION Handoff — Feature 329 (ORDERED_FRAMEWORKS Catalog-Drift CI Guard)

**Generated**: 2026-06-30 · **Branch**: `329-ordered-frameworks-ci-guard` · **Draft PR**: #344 (`feat(329):` title — correct)
**Stop reason**: standalone 3-wave ceiling (W1/W2/W3 executed this session; `orchestrated == false`). Resume runs **Wave 4** only.
**Progress**: **14/16 tasks** (87.5%). Committed `4786292`, pushed to `origin/329-ordered-frameworks-ci-guard`.

---

## How to resume

```
claude "Resume Feature 329 (branch: 329-ordered-frameworks-ci-guard). Waves 1–3 complete (14/16 tasks). Run /aod.build to continue with Wave 4."
```

`/aod.build` Step 0h auto-detects this handoff and resumes at the first unmarked task. All prerequisites below are MET — answer **Yes** to the handoff prompt.

---

## Next Actions (Wave 4 — Acceptance + Deliver — 2 tasks)

### T015 [tester] — Integration + quickstart negative checks `[MANUAL-ONLY]`
Run `specs/329-ordered-frameworks-ci-guard/quickstart.md` negative probes against the **live tree**:
1. **Drift caught**: add/rename a record `id` in a member catalog (e.g. `schemas/taxonomy/cwe.yaml`), then `python3 scripts/check-catalog-drift.py` → **expect exit 1** naming the framework; `git checkout -- schemas/taxonomy/<member>.yaml` to revert.
2. **Count-neutral ignored**: change only a citation string (no `(id, out_of_scope)` change) → **expect exit 0**; revert.
3. Confirm guard green on the clean tree (`--check` exit 0); both workflow triggers live; sidecar emitted by the regen script.
- **Use `.venv/bin/python`** (the default homebrew `python3` 3.14 lacks pyyaml — see Interpreter note).

### T016 [devops] — Deliver gate (KB-18 / constitution VII)
1. **KB18/#342 hazard (MANDATORY)**: before any merge/push, verify branch-current AND local `main` == `origin/main` via a **full-tree diff**. `git reset --hard` is permission-blocked in this env — use `git checkout -B main origin/main` if local main is stale. (Per [[project_aod_update_clobbers_tachi]] a stale unpushed local-main clobber nearly re-shipped at a prior deliver.)
2. PR #344 title is already `feat(329): ordered-frameworks catalog-drift CI guard` (release-triggering — verified). Mark ready: `gh pr ready 344`.
3. Merge via **devops** with squash-merge (the `feat(329):` title becomes the commit subject).
4. **Post-merge**: verify a release-please PR opens within ~30s (`gh pr list --state open --search "release-please"`). If empty, push an empty `feat(329):` release-marker commit to `main`. (Per [[feedback_aod_deliver_release_gate]].)

---

## Deliver-stage advisories carried from the P1 architect checkpoint (`.aod/results/architect-p1-checkpoint.md`)

- **A1' — first-run CI observability**: `tachi-catalog-drift.yml` has no green-on-`main` history yet; this push (`4786292`) is its **first PR fire**. Confirm it ran **green on PR #344** before marking ready / merging — a path-filter typo or runner-pyyaml surprise would surface there (the A2 pyyaml install closes the silent-no-op mode). Check: `gh pr checks 344`.
- **A2' — coupled commit-set**: the sidecar + workflow are a coupled pair; all 11 write-set members were committed together in `4786292` (already satisfied — do NOT partial-ship).

---

## State that is already DONE (do not redo)

| Item | State |
|---|---|
| **T003 pre-state go/no-go** | **GREEN** — `test_backward_compatibility.py` = 13 passed, 1 skip (the documented mermaid-agentic-app SC-003 skip). Main is green; **no baseline remediation needed** (OQ-3 green path). |
| **Guard** `scripts/check-catalog-drift.py` | fingerprint core (loader reuse, C-2 isinstance fail-closed) + `--check`/`--emit`; `--check` exit 0 on clean tree. |
| **Regen** `scripts/regenerate-ca-baselines.sh` | renders 6 baselines into a temp dir, emits sidecar last; T007 reproduced all 6 **byte-identically** (no baseline changes). |
| **Sidecar** `examples/ca-baseline-fingerprints.json` | regen-emitted, 5 frameworks, committed. |
| **Tests** `tests/scripts/test_catalog_drift_guard.py` | **15/15 green** (live gate + grow/swap/flip catch + #333/non-member/clean ignore + future-member dynamic + fail-closed quartet). |
| **Workflow** `.github/workflows/tachi-catalog-drift.yml` | dual-trigger PR + push:[main], single ubuntu-latest, contents:read, **installs pyyaml**, single-source `&drift_paths` anchor. |
| **ADR-037 D-14** | new decision appended; D-9 body byte-unchanged; mapping table (14 rows) + revision-history row. |
| **Docs** | KB Entry 15 CI-backstop annotation; CHANGELOG `feat(329)` Unreleased entry. |
| **OQ-6** | issue **#345** filed; `test_init_sh_substitution.py` xfail re-pointed #329→#345 (string-only, NO fixture regen). |
| **P0 + P1 architect checkpoints** | both **APPROVED, 0 blocking**. |

---

## Interpreter note (important)

The default `python3` here is homebrew 3.14 and is **externally-managed (PEP 668) without pyyaml/pytest**. Use **`.venv/bin/python`** (3.12, carries pytest 9.1.0 + pyyaml 6.0.3 + pytest-timeout) for all local runs. The regen script honors a `PYTHON` override: `PYTHON=.venv/bin/python scripts/regenerate-ca-baselines.sh`. CI (`ubuntu-latest`) installs its own pyyaml, so this is a local-only concern.

## Definition of Done (constitution VII) — closed at W4
1. Pushed to Production — guard merged to `main` (post-green, via devops) on PR + `push:[main]`.
2. Tested — `test_catalog_drift_guard.py` green (live gate + 15 cases) in the dedicated workflow.
3. User Validated — quickstart negatives (T015): probe drift → caught; citation-only → ignored; sidecar emitted by regen; guard green on clean tree.

After deliver: `/aod.deliver FEATURE: 329` then `/aod.document`.
