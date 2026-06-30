# Security Scan Report

**Feature**: 329 — ordered-frameworks-ci-guard
**Branch**: 329-ordered-frameworks-ci-guard
**Commit**: a5d5644e7557
**Scan ID**: bcd01e45-7e7b-411a-a983-057b40da9fbf
**Timestamp**: 2026-06-30T20:25:53Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 4 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

**SAST scope** (4 code files changed on `main...HEAD`):
`scripts/check-catalog-drift.py`, `scripts/regenerate-ca-baselines.sh`,
`tests/scripts/test_catalog_drift_guard.py`, `tests/scripts/test_init_sh_substitution.py`.

**SCA**: SKIPPED — no dependency manifests changed on this branch.

---

## Findings

No security findings detected.

All inputs in the changed code are hardcoded, repo-relative constants:
the guard's `importlib.exec_module` loads a fixed `__file__`-relative
`scripts/extract-report-data.py` (the established loader-reuse pattern, not
user input — no injection vector); `hashlib.sha256` is content-checksum use
(not password hashing); sidecar JSON I/O reads/writes constant repo paths and
fails closed on any parse/structure error. The regen shell script runs
`set -euo pipefail`, creates a quoted `mktemp -d` temp dir with a cleanup trap,
loops a hardcoded `BASELINE_EXAMPLES` constant, and quotes all
constant-derived paths. No secrets, SQL, command injection, eval, network,
or path traversal reachable from untrusted input.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl`
- Risk acceptances: `.security/exceptions.jsonl`
- SARIF report: `.security/reports/a5d5644e7557.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
