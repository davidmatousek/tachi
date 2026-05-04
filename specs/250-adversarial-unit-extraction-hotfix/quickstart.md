# Quickstart: Adversarial Unit Extraction Hot-Fix

**Branch**: `250-adversarial-unit-extraction-hotfix`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**For**: build agents authoring the new test modules; reviewers verifying the hot-fix

---

## 1 — Run the new unit modules locally

```bash
# From repo root, on the feature branch:
python -m pytest tests/scripts/test_template_substitute_unit.py tests/scripts/test_init_input_unit.py \
    --durations=0 \
    --timeout=15 \
    -v
```

**Expected output**:
- All 13 tests pass (8 substitute + 1 canary + 4 input-rejection)
- `--durations=0` summary shows every test ≤ 2.0s wall time on macOS dev hardware
- No `init.sh` invocations triggered (verify with `pgrep -af "scripts/init.sh"` during the run — should be empty)

If a test exceeds 2s on dev hardware: investigate. Fixed targets in spec FR-012 / SC-001 are CI-side observations (macOS-latest with 4× slowdown headroom), so dev hardware should be well under.

---

## 2 — Verify zero init.sh references in the new modules

```bash
grep -E "run_init_in_clone|clone_into_tmpdir|init_sh_helpers|scripts/init.sh" \
    tests/scripts/test_template_substitute_unit.py \
    tests/scripts/test_init_input_unit.py
```

**Expected**: zero matches. If any match appears, the new module is invoking an integration helper or `init.sh` directly — both are forbidden by FR-003.

---

## 3 — Verify integration backstop preservation

```bash
git diff main -- tests/scripts/test_init_sh_adversarial.py
```

**Expected**:
- Exactly one contiguous deletion block (lines 41-162 in the pre-hot-fix file)
- No additions
- No whitespace-only changes outside the deletion block
- `from init_sh_helpers import build_canonical_stdin, clone_into_tmpdir, run_init_in_clone` line is **preserved** (case 13 still uses these)

```bash
git diff main -- tests/scripts/init_sh_helpers.py \
    .aod/scripts/bash/template-substitute.sh \
    .aod/scripts/bash/init-input.sh
```

**Expected**: zero changes. These three files are byte-identical to `main` (FR-005, FR-019, FR-021).

---

## 4 — Run the deliberate-fault verification matrix on bash 5.x (FR-010 / SC-006)

This is a **one-shot manual verification**, not a permanent CI step. It must be run on a bash 5.x dev workstation before the PR is marked ready.

```bash
# 1. Locally remove the shim (DO NOT COMMIT)
sed -i.bak '/shopt -u patsub_replacement/d' .aod/scripts/bash/template-substitute.sh

# 2. Run the new unit module on bash 5.x
python -m pytest tests/scripts/test_template_substitute_unit.py -v --tb=short

# 3. Record the PASS/FAIL matrix in .aod/results/deliberate-fault-matrix-250.md
```

**Expected matrix (per spec FR-010)**:

| Case | Expected under fault | Reason |
|------|----------------------|--------|
| case_1_ampersand | **FAIL** | `&` triggers patsub_replacement backref → `AT{{PROJECT_NAME}}T` corruption |
| case_2_pipe | PASS | pure parameter expansion, no `&` |
| case_3_backref | **FAIL** | `\1\2` triggers patsub_replacement backref handling |
| case_4_single_quoted | PASS | pure parameter expansion |
| case_5_double_quoted | PASS | pure parameter expansion |
| case_6_multibyte | **FAIL** | bash 5.x `patsub_replacement` mishandles multibyte boundaries |
| case_7_newline_in_value | PASS | pure parameter expansion |
| case_8_empty_value | PASS | pure parameter expansion |

```bash
# 4. Restore the shim and verify all cases pass under normal state
mv .aod/scripts/bash/template-substitute.sh.bak .aod/scripts/bash/template-substitute.sh
python -m pytest tests/scripts/test_template_substitute_unit.py -v
```

**Expected**: 8/8 PASS under normal state.

The matrix output (PASS/FAIL per case) MUST be recorded in `.aod/results/deliberate-fault-matrix-250.md` with:
- bash version under test (`bash --version`)
- timestamp
- command outputs
- the matrix table

This is the audit artifact for SC-006 / `[MANUAL-ONLY]`.

---

## 5 — Verify post-merge CI green-rate (US-1, FR-015, SC-004)

After the hot-fix lands on `main`:

```bash
# 1. Wait for the post-merge CI run to complete
gh run list --branch main --limit 1 --json status,conclusion,workflowName,databaseId

# 2. Check init.sh-suite step duration on macos-latest
gh run view <RUN_ID> --json jobs | jq '.jobs[] | select(.name | contains("macos-latest"))'

# 3. Verify ≤ 15 min on macos-latest (FR-016 / SC-002)
# 4. Verify both legs green (FR-015)
```

**Sustained verification**:
- Track 5 consecutive merges to `main` after the hot-fix
- Confirm `macos-latest` 5/5 green-rate (SC-004)
- Confirm CI savings ≥ 25 min vs baseline run `25314246672` (FR-016 / SC-005)

The baseline run for comparison is GitHub Actions run `25314246672` (commit `219dfee`, F-248 closing run). Tasks.md MUST URL+SHA pin this baseline with measured minutes (TC-2).

---

## 6 — Verify release-please patch-bump opens

After the squash-merge with PR title `fix(250): extract adversarial unit tests — eliminate cold-cache CI flake`:

```bash
gh pr list --state open --search "release-please" --limit 3
```

**Expected**: a release-please PR open within ~30s of the squash-merge.

If empty, push a release-marker commit per `.claude/rules/git-workflow.md` belt-and-suspenders rule:

```bash
git commit --allow-empty -m "fix(250): extract adversarial unit tests — release marker"
git push origin main
```

---

## 7 — Diagnose canary failure (R-1)

If `test_init_input_unit.py::test_canary_positive_path` fails on first run:

1. Check stdout — does it contain `declare -- result=""` (empty)?
2. If yes: pipe-subshell regression. The test is invoking `aod_init_read_validated` via `printf | helper` somewhere — find the offending line and replace with `helper < <(printf ...)`.
3. The error message in the canary already names this diagnosis — prefer the test's own stderr over external interpretation.

**Reference**: contracts/aod_init_read_validated.md "Caller-scope write semantics — load-bearing constraint (R-1)".
