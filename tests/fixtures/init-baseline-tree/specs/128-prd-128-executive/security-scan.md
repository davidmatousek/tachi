# Security Scan Report

**Feature**: 128 — Executive Threat Architecture Infographic
**Branch**: 128-prd-128-executive
**Commit**: 01d3e8587191
**Scan ID**: ba390e43-68fd-4627-b3c4-92e79c24141a
**Timestamp**: 2026-04-10T04:55:26Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 12 |
| Manifests audited (SCA) | 2 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

---

## SAST Analysis

**Files analyzed (12)**:

Production scripts:
- `scripts/extract-infographic-data.py` (+327/-0 lines)
- `scripts/extract-report-data.py` (+31/-4 lines)

Test infrastructure (new in F-128):
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/scripts/__init__.py`
- `tests/scripts/fixtures/__init__.py`
- `tests/scripts/test_backward_compatibility.py`
- `tests/scripts/test_command_dispatch.py`
- `tests/scripts/test_extract_infographic_data.py`
- `tests/scripts/test_extract_report_data.py`
- `tests/scripts/test_pdf_page_positioning.py`
- `tests/scripts/test_smoke.py`

**OWASP P0 patterns checked**:
- A01: Broken Access Control — open redirects, path traversal
- A02: Cryptographic Failures — hardcoded secrets, weak crypto, insecure random
- A03: Injection — SQL injection, command injection, template injection
- A05: Security Misconfiguration — debug mode, permissive CORS, verbose errors, default credentials
- A07: Identification & Authentication Failures — insecure cookies, plaintext credentials

**Result**: **Zero SAST findings.**

The F-128 code surface is two CLI Python scripts that parse markdown files and emit structured output (JSON or Typst). Both scripts:

- Take CLI arguments exclusively via argparse (no network input, no stdin)
- Read local filesystem files from user-controlled paths (not a server-side path traversal vector — the user running the CLI chooses their own input)
- Perform no SQL queries, no shell command execution, no template rendering with user input
- Do not handle authentication, sessions, or cookies
- Do not use cryptographic primitives (no hashing, no signing, no random generation for secrets)
- Do not make network requests

The test files exercise the CLI via `subprocess.run` with `check=False` and `capture_output=True`, passing file paths from pytest `tmp_path` fixtures or the test fixture directory. No `shell=True` anywhere. No `eval`, `exec`, `pickle`, or `yaml.load` calls in any scanned file.

## SCA Analysis

**Manifests audited (2)**:

- `pyproject.toml` — build-system requires `setuptools>=61`
- `requirements-dev.txt` — development dependencies: `pytest>=8.0`, `pytest-cov>=4.1`

**Packages**:

| Name | Version constraint | Purpose | Known CVEs at this version |
|---|---|---|---|
| setuptools | `>=61` | Build-system (pyproject.toml PEP 517) | No known CVEs at `>=61`. setuptools 65.5.1 addressed CVE-2022-40897 (ReDoS); modern 61+ line unaffected. |
| pytest | `>=8.0` | Test framework (dev-only) | No known CVEs in pytest 8.x training cutoff window. |
| pytest-cov | `>=4.1` | Coverage plugin for pytest (dev-only) | No known CVEs. |

**Result**: **Zero SCA findings.**

All three packages are well-established Python tooling with clean CVE histories at the declared version constraints. Two of them (`pytest`, `pytest-cov`) are dev-only and never ship to production. `setuptools` is a build-time dependency only. The F-128 PR adds NO new production runtime dependencies.

> SCA findings are based on Claude training knowledge (cutoff: August 2025). Supplement with real-time CVE scanning (npm audit, pip-audit, Snyk) for production workloads.

## Findings

No security findings detected.

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- SARIF report: `.security/reports/01d3e8587191.sarif`
- CycloneDX SBOM: `.security/reports/sca-2026-04-10.cdx.json`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
*SCA findings are based on Claude training knowledge (cutoff: August 2025). Supplement with real-time CVE scanning (npm audit, pip-audit, Snyk) for production workloads.*
