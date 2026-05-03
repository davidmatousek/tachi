# Security Scan Report

**Feature**: 194 — coverage-attestation-report-section
**Branch**: 194-coverage-attestation-report-section
**Commit**: 71890850733e
**Scan ID**: 272fa1da-8da8-43c2-ba12-2f1fde0ec026
**Timestamp**: 2026-04-18T18:00:36Z
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

---

## Files Scanned (SAST)

- `scripts/extract-report-data.py`
- `tests/scripts/generate_pagination_fixture.py`
- `tests/scripts/test_coverage_attestation.py`
- `tests/scripts/test_coverage_attestation_pagination.py`

## Manifests Audited (SCA)

None — no dependency manifest files (`requirements.txt`, `pyproject.toml`, `package.json`, etc.) changed on this branch. SCA step skipped.

---

## Findings

No security findings detected.

Review scope:

- **A01 Broken Access Control**: No redirect or path-traversal surface. Framework name inputs to `_framework_yaml_path()` are constrained to the closed 5-value enum `ORDERED_FRAMEWORKS` (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe); path base anchored to `__file__`.
- **A02 Cryptographic Failures**: No credentials, tokens, or password hashing in scope. `random.Random(194)` in `generate_pagination_fixture.py` is a deterministic test-fixture generator; not used for session IDs, tokens, or nonces.
- **A03 Injection**: No SQL, no `os.system`, no `exec`/`eval`, no template-injection. `subprocess.run` calls in test files use hardcoded `cmd` lists (no user-input interpolation).
- **A05 Security Misconfiguration**: No debug flags, no CORS config, no default credentials.
- **A07 Auth Failures**: No cookies, no auth state, no credential storage.

`yaml.safe_load` (not unsafe `yaml.load`) used throughout for catalog YAML parsing.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- SARIF report: `.security/reports/71890850733e.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
