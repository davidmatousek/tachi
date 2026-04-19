# Security Scan Report

**Feature**: 201 — `output-integrity` threat agent (OWASP LLM05:2025)
**Branch**: `201-output-integrity-threat-agent`
**Commit**: `a5e75b646f74`
**Scan ID**: `feae2e4c-45d2-4fbe-92ac-133c54fe58ef`
**Timestamp**: 2026-04-19T02:14:31Z UTC
**Status**: PASSED

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

---

## Findings

No security findings detected.

---

## Files Scanned (SAST)

| File | Language | Type |
|------|----------|------|
| `tests/scripts/test_output_integrity.py` | Python | Test |

**Analysis notes**: The single Python file changed is a pytest test suite covering the Feature 201 schema regex extension and F-A2 referential-integrity fixture-driven validation. Analyzed for OWASP Top 10 patterns (A01 broken access control, A02 cryptographic failures, A03 injection, A05 security misconfiguration, A07 identification/authentication failures). No matches:

- **A02 (hardcoded secrets)**: none — file contains no credential literals
- **A03 (injection)**: none — no SQL, no shell, no template evaluation; all test inputs are static fixture YAML
- **A03 (YAML unsafe deserialization)**: **safe** — uses `yaml.safe_load()` exclusively (verified line 42), avoiding the CWE-20 / CWE-502 arbitrary-code-execution path of `yaml.load()` without Loader
- **A01 (path traversal)**: none — uses `pathlib.Path` with fixed `REPO_ROOT` derivation and static `SCHEMA_PATH` + `FIXTURE_DIR` constants; no user-input-driven file access
- **A02 (weak crypto)**: none — no hashing or encryption performed in test file

## Manifests Audited (SCA)

No dependency manifests changed on this branch. `pyproject.toml`, `requirements-dev.txt`, `requirements.txt`, `package.json` show empty diff vs main — SC-008 zero-runtime-dependency-additions predicate green.

Skipped per SC-008 zero-diff.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan — clean pass.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (appended — chain_hash `025b40c7...`)
- SARIF report: `.security/reports/a5e75b646f74.sarif`
- CycloneDX SBOM: not generated (no manifests changed)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
