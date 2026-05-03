# Security Scan Report

**Feature**: 219 — asi07-tool-abuse-enrichment
**Branch**: 219-asi07-tool-abuse-enrichment
**Commit**: bb35e2457353
**Scan ID**: 0eeb5bf3-2a98-4b67-aac6-6176f7d54603
**Timestamp**: 2026-04-26T14:35:06Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 4 |
| Manifests audited (SCA) | 0 (skipped — no manifest changes per SC-012) |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

---

## Files Scanned (SAST)

1. `scripts/generate-threats-sarif.py` — utility to convert `threats.md` → SARIF 2.1.0 (NEW, F-3 wave 3)
2. `scripts/generate-risk-scores-sarif.py` — utility to convert `risk-scores.md` → SARIF 2.1.0 (NEW, F-3 wave 3)
3. `tests/scripts/test_backward_compatibility.py` — modified test list per F-3 carve-out
4. `tests/scripts/test_tool_abuse_enrichment.py` — extended with T039 live regen validation test (Section E lines 342-402)

## OWASP P0 Patterns Checked

| Pattern | Detected | Notes |
|---|---|---|
| A01: Open Redirect / Path Traversal | 0 | All `os.path.join` uses derive paths from `REPO_ROOT` constants, not user input |
| A02: Hardcoded Secrets | 0 | Zero credential literals in any file |
| A02: Weak Crypto (passwords) | 0 | One MD5 use in `generate-threats-sarif.py:454` for SARIF `partialFingerprints` (finding-ID stable hash, F-2 vintage compat) — **explicitly excluded by OWASP A02 pattern definition (file checksum / fingerprint use)** |
| A02: Insecure Random | 0 | No `random.random()` or `Math.random()` |
| A03: SQL Injection | 0 | No SQL in scope |
| A03: Command Injection | 0 | No `os.system`, `subprocess(shell=True)`, or `exec()` |
| A03: Template Injection | 0 | No template rendering |
| A05: Debug Mode | 0 | No `DEBUG=True` or `app.run(debug=True)` |
| A05: Permissive CORS | 0 | No CORS config |
| A05: Verbose Errors | 0 | No `traceback.format_exc()` returned in HTTP context |
| A05: Default Credentials | 0 | None |
| A07: Insecure Cookie | 0 | Out of scope |
| A07: Plaintext Credentials | 0 | None |

**False positive cleared**: Initial grep flagged 9 `eval/compile` matches — all confirmed as `re.compile()` regex compilation (safe). One `hashlib.md5` use confirmed as fingerprint generator (excluded per A02 pattern definition).

## SCA Analysis

**Status**: SKIPPED — No dependency manifests changed.

`git diff --name-only main...HEAD` confirms zero diff on `pyproject.toml`, `requirements*.txt`, `package.json`, `package-lock.json`, `yarn.lock`, `go.mod`, `Cargo.toml` per F-3 SC-012 (verified at T052). No new external dependencies introduced.

## Findings

No security findings detected.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (entry appended with chain_hash `c810e847ccd256830369f9c59273e3880a9186461ca0d2846e63623f72ba4f9e`)
- SARIF report: `.security/reports/bb35e2457353.sarif` (empty `results[]` per clean-scan path)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
