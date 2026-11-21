# Security Scan Report

**Feature**: 391 — Isolated and Auditable Operation (Part A)
**Branch**: 391-isolated-auditable-operation
**Commit**: aea09d85c908
**Scan ID**: 2a133a86-70e2-41be-9035-33420f53a46f
**Timestamp**: 2026-11-21T16:55:09Z UTC
**Status**: PASSED (no blocking findings; one LOW, known and tracked)

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 9 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 1 |
| INFO findings | 0 |

**Scope.** These are the code files changed on the Part A branch against `main` (`git diff --name-only main...HEAD`, code extensions only):
- `scripts/check-agent-privileges.py` (new);
- `scripts/extract-report-data.py`;
- `scripts/extract-infographic-data.py` and `scripts/populate-affected-assets.py` (two lines each);
- five test modules under `tests/scripts/`.

No dependency manifest changed, so SCA did not run. Part B's code (#396) is not in this branch's diff: the `install.sh` marker block, `scripts/stamp-tachi-version.py`, `scripts/generate-threats-sarif.py` and their tests. T047 scans part-b before #396 is marked ready.

**Method.**
- **The screen.** The OWASP P0 patterns ran over every line the branch added in the nine files:
  - **24 command-execution hits.** All are `subprocess.run` with a list of arguments and a fixed executable (`git ls-files` in the guard, `mmdc` in the extractor), with no shell.
  - **45 filesystem-write hits.**
    - The extractor's `--build-dir` and `--remove-build-dir` lifecycle hands `shutil.rmtree` and `copytree` only the resolved path that `_guard_build_dir` returns. That guard keeps the path strictly under the working directory, refuses a symlink below it, requires the `.tachi-build/security-report` suffix, and refuses any overlap with the templates or containment of the target.
    - The guard's `--self-test` writes only inside a `tempfile.TemporaryDirectory`.
    - The tests write under pytest's `tmp_path`.
  - **No hits** for hardcoded secrets, weak hashes, insecure randomness, unsafe deserialization, debug mode or error-trace exposure.
- **Prior reviews.** The feature's own security reviews (`test-results/security-a.md`, `test-results/security-b1.md`, which also holds T042's W3 snippet review) and the T044 code review covered the same code.

---

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM

None.

### LOW / INFO

#### tachi-VULN-d229b69fb5e4: A01: Broken Access Control (link following, CWE-59)

- **Type**: SAST
- **File**: `scripts/extract-report-data.py:2543`. The PNG writes are at `:1015` and `:1704`, through `mmdc -o`.
- **CVSS**: 3.3 LOW (estimated; `CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`). This is outside the P0 table: link following in an operator-run step, not attacker-controlled path input.
- **EPSS**: link-following flaws in local tools are exploited only with prior local write access to the folder they read. Exploitation probability is low without that foothold.
- **KEV**: N/A
- **Description**: Build mode follows symlinks. The custom `report-config.typ` copy and the attack-tree and attack-chain PNG writes resolve through links in the target and output directories. Under Claude Code's sandbox each write is bound by its real path. The runbook's by-hand report build for macOS (§6) runs outside the sandbox.
- **Recommendation**:
  - In build mode, refuse with exit 2, as `_exit_build_dir_error` does, a symlinked `report-config.typ` in the target directory.
  - Refuse the same way any symlink at or under the paths written in the output directory: `attack-trees/`, `attack-chains/` and a corrected infographic copy.
  - This is CR-10 (T044) and the code half of T042's W3-H1, held for maintainer triage (`delivery.md`, Feedback Loop). Until then, the runbook's §6 "Check first" step covers the by-hand build: `find {out} -type l` prints nothing.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan. The one finding is LOW and does not block.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl`
- Risk acceptances: `.security/exceptions.jsonl` (not written; no acceptance)
- SARIF report: `.security/reports/aea09d85c908.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
