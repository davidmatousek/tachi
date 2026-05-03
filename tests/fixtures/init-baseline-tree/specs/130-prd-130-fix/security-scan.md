# Security Scan Report

**Feature**: 130 — Fix Attack Path Mermaid Rendering When mmdc Is Not Installed
**Branch**: 130-prd-130-fix
**Commit**: 2c97e8091c13
**Scan ID**: 65936668-f62b-4548-a9bd-e503c6e114ff
**Timestamp**: 2026-04-11T15:47:02Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 3 |
| Manifests audited (SCA) | 0 (skipped — no dependency manifests changed) |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

---

## Scanned Files

### SAST (3 files)

| File | Language | LOC | Notes |
|---|---|---:|---|
| `scripts/extract-report-data.py` | Python | 1515 | Feature 130 changes in `render_mermaid_to_png()` and `_render_single()` — preflight gate + mid-render aggregator |
| `scripts/install.sh` | Shell | 245 | Feature 130 added mmdc courtesy warning |
| `tests/scripts/test_mmdc_preflight.py` | Python | 339 | New pytest file for preflight + mid-render tests (9 tests) |

### SCA (0 manifests)

Skipped — no dependency manifests changed on this feature branch. Verified via `git diff --name-only main...HEAD`. Feature 130 is a correctness bug fix and adds no runtime or dev dependencies.

---

## Findings

No security findings detected.

### OWASP P0 Pattern Review (all clean)

| Category | Pattern | Result |
|---|---|---|
| A01 Broken Access Control | Open redirect, path traversal | No new patterns introduced. Pre-existing `fid_lower`-based file path construction in `_render_single` (moved from nested function to module level) operates on threat-model finding IDs — trusted input for a local dev toolkit. No user-facing attack surface. |
| A02 Cryptographic Failures | Hardcoded secrets, weak crypto, insecure random | N/A — no credentials, no crypto operations, no random number generation |
| A03 Injection | SQL, command, template injection | `subprocess.run(["mmdc", ...])` uses list argv form — NOT shell=True. Command injection impossible. No SQL, no template rendering of user input. |
| A05 Security Misconfiguration | Debug mode, CORS, verbose errors, default credentials | N/A — no web surface. `RuntimeError` messages emit mmdc stderr excerpts (first 200 bytes) for developer-facing diagnostics; not transmitted to users or logged to persistent storage. |
| A07 Authentication Failures | Insecure cookies, plaintext credentials | N/A — no auth, no sessions, no credentials |

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan (no blocking findings).

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- SARIF report: `.security/reports/2c97e8091c13.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
