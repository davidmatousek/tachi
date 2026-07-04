# Security Scan Report

**Feature**: 295 — f292-verification-runs
**Branch**: 295-f292-verification-runs
**Commit**: ad4e730f54b7
**Scan ID**: c0dada31-8005-46aa-8305-f49f6d3cef9d
**Timestamp**: 2026-07-03T20:02:38Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 3 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

SCA: No dependency manifests changed — skipping dependency audit.

Files scanned: `scripts/generate-threats-sarif.py` (FR-014 URI derivation), `tests/scripts/test_affected_assets_wiring.py` (+4 FR-014 assertions), `specs/295-f292-verification-runs/tools/assemble_oi_sarif.py` (specs-scoped verification tool; yaml.safe_load only, fail-closed CLI).

---

## Findings

No security findings detected.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl` (no events this scan; pre-existing open INFO tachi-VULN-e9b741b0e343 is out of this diff's scope and untouched per repo precedent)
- SARIF report: `.security/reports/ad4e730f54b7.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
