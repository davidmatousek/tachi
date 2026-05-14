# Security Scan Report

**Feature**: 292 — Output-Integrity Cross-Sink Refinement
**Branch**: `292-output-integrity-cross-sink-refinement`
**Commit**: `0b5528d0f72d`
**Scan ID**: `94ef844e-c976-4f20-be20-cb543b12ae14`
**Timestamp**: 2026-05-14T16:52:36Z UTC
**Status**: PASSED

> **Note**: This is the SECOND scan on this branch. The first scan (`81f2eb2d-0e96-4130-a956-d7f4cd264937`, commit `d72ac2bf6d6c`, 2026-05-14T16:05:02Z) ran before the T035 carve-out commit added `tests/scripts/test_backward_compatibility.py` to the diff. This rescan brings SAST into scope on the 1 newly-added code file.

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 1 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

**SAST**: PASSED — 1 file scanned (`tests/scripts/test_backward_compatibility.py`). The F-292 carve-out edits (move `output-integrity.md` out of `DETECTION_AGENT_PATHS`; add `DETECTION_PATTERN_REF_F292_OUTPUT_INTEGRITY_HOST` to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS`; update assert count from 2 to 1; add docblock paragraph) modify only data-structure literals and docblock prose. Zero matches against OWASP P0 patterns (A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection, A05 Security Misconfiguration, A07 Identification & Authentication Failures). Existing `subprocess.run()` calls in the file (lines 98, 114, 261, 278) are unchanged by the F-292 diff and continue to pass argument-vector form (`shell=False` implicit), which is injection-safe.

**SCA**: SKIPPED — No dependency manifests changed on this branch.

---

## Findings

No security findings detected.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (2 entries this feature: scan_id `81f2eb2d-...` at commit `d72ac2bf6d6c`, scan_id `94ef844e-...` at commit `0b5528d0f72d`)
- Vulnerability events: `.security/vulnerabilities.jsonl` (no new entries this scan)
- Risk acceptances: `.security/exceptions.jsonl` (no acceptances)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
