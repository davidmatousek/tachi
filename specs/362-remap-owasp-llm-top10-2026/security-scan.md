# Security Scan Report

**Feature**: 362 — Remap OWASP LLM Top 10 Coverage to the 2026 Edition
**Branch**: 362-remap-owasp-llm-top10-2026
**Commit**: 1dfa38cfb3ea
**Scan ID**: 6030bd91-dfbf-47c0-99e9-e0ee9bfd3684
**Timestamp**: 2026-08-12T14:38:46Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 11 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

SCA: No dependency manifests changed — skipping dependency audit.

---

## Findings

No security findings detected.

**Scope** (code files changed on `362-remap-owasp-llm-top10-2026` vs `main`, per FR-004 filter):

- `scripts/extract-report-data.py`
- `scripts/generate-risk-scores-sarif.py`
- `scripts/generate-threats-sarif.py`
- `tests/scripts/test_backward_compatibility.py`
- `tests/scripts/test_catalog_drift_guard.py`
- `tests/scripts/test_coverage_attestation.py`
- `tests/scripts/test_llm10_unbounded_consumption_enrichment.py`
- `tests/scripts/test_output_integrity.py`
- `tests/scripts/test_owasp_2026_contract.py`
- `tests/scripts/test_source_attribution.py`
- `tests/scripts/test_tool_abuse_enrichment.py`

**Pattern classes checked** (OWASP P0): A01 open redirect / path traversal; A02 hardcoded secrets, weak crypto for passwords, insecure random; A03 SQL/command/template injection; A05 debug mode, permissive CORS, verbose errors, default credentials; A07 insecure cookies, plaintext credentials.

**Dispositions of pattern hits (both benign, both pre-existing — unchanged on this branch)**:
- `subprocess.run` (extract-report-data.py:792, :1425 + 8 test sites): list-form argv, fixed `mmdc` executable, `timeout=30`, `capture_output=True`, no `shell=True` anywhere in scope.
- `hashlib.md5` (generate-threats-sarif.py:418, `line_hash_for`): SARIF `partialFingerprints` line-hash — non-cryptographic identifier use, explicitly excluded from the A02 weak-crypto class (not password hashing).
- All YAML parsing in scope uses `yaml.safe_load` (zero unsafe `yaml.load`). No `eval`/`exec`/`os.system`, no pickle/marshal, no network calls, no debug flags, no credential literals in non-test files.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl` (no events this scan — zero findings; no prior open events on in-scope files)
- SARIF report: `.security/reports/1dfa38cfb3ea.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
