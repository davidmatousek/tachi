# Security Scan Report

**Feature**: 185 — CWE Catalog Expansion (F-A1.2)
**Branch**: 185-cwe-catalog-expansion
**Commit**: 015a6ce1a4cc
**Scan ID**: c042010b-6013-467d-8908-6fd7f4fccff9
**Timestamp**: 2026-06-11T23:51:15Z UTC
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
| INFO findings | 1 |

SCA: No dependency manifests changed — skipping dependency audit (`uv.lock` is a lockfile outside the manifest detection set).

---

## Findings

### CRITICAL
None.

### HIGH
None.

### MEDIUM
None.

### LOW / INFO

#### tachi-VULN-e9b741b0e343: A05: Security Misconfiguration (hardening note)

- **Type**: SAST
- **File**: `specs/185-cwe-catalog-expansion/scripts/harvest_cwe_names.py:79` (also `name_diff.py:144`)
- **CVSS**: n/a INFO (estimated)
- **EPSS**: n/a — hardening note, no exploitable surface in current usage
- **KEV**: N/A
- **Description**: Stdlib xml.etree used to parse the MITRE corpus in harvest_cwe_names.py and name_diff.py. Input is SHA-256-pinned with chain-of-custody verification (name_diff.py provenance guards), and both scripts are regeneration-only with no production caller, so exposure is negligible. defusedxml would harden against crafted-XML resource exhaustion if these scripts are ever pointed at untrusted corpora.
- **Recommendation**: Optional: parse with defusedxml.ElementTree, or keep the SHA-pin provenance guard as the compensating control (current state).

Files scanned: `specs/185-cwe-catalog-expansion/scripts/extract_restore_set.py` (clean — list-form subprocess args from constants, yaml.safe_load), `scripts/harvest_cwe_names.py` (INFO above), `scripts/name_diff.py` (INFO above; checksum-only sha256 is legitimate; zip member hashed without extraction), `tests/scripts/test_coverage_attestation.py` (two-line expectation refresh, no security surface).

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl`
- Risk acceptances: `.security/exceptions.jsonl` (none recorded)
- SARIF report: `.security/reports/015a6ce1a4cc.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
