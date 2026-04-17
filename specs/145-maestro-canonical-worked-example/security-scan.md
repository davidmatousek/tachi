# Security Scan Report

**Feature**: 145 — Canonical MAESTRO Worked Example
**Branch**: 145-maestro-canonical-worked-example
**Commit**: b793ab198ea5
**Scan ID**: 166a57ae-efe7-41b9-b2ff-fddf0e858fb7
**Timestamp**: 2026-04-17T14:29:52Z UTC
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

### Scan Scope

**SAST** — 1 Python file analyzed:
- `tests/scripts/test_backward_compatibility.py` (+1 line surgical change: `"maestro-reference"` added as 6th entry in `BASELINE_EXAMPLES` list, lines 38–45)

Full-file review against OWASP P0 patterns (A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection, A05 Security Misconfiguration, A07 Authentication Failures). All `subprocess.run()` invocations use list-form argv (not shell strings) with controlled constant paths — no command injection surface. No user-input handling, credentials, crypto primitives, network endpoints, authentication, or cookie handling in the test harness.

**SCA** — SKIPPED (no dependency manifests changed; no additions to `requirements*.txt`, `pyproject.toml`, `package.json`, etc.). Feature 145 is a content-authoring feature with zero runtime dependency deltas, consistent with SC-014 constraint (no net-new runtime dependencies).

### Feature 145 Scan Characteristics

Feature 145 is a **content-authoring feature** (zero source code, zero new schema types, zero new agents, zero new runtime dependencies). The delivered artifacts under `examples/maestro-reference/` are:

- Markdown narrative files (threats.md, threat-report.md, README.md, attack-trees/*.md)
- SARIF JSON files (emitted by the tachi pipeline, schema 2.1.0)
- PNG/JPEG images (rendered from Mermaid source + generated infographics)
- PDF (Typst compilation output)
- A YAML frontmatter block on `architecture.md` (Feature 120 v1.0)

None of the above are executable code. The architecture.md describes a **synthetic healthcare CDSS reference scenario** for threat-modeling teaching — see README.md Section 2 and architecture.md header disclaimer (security-analyst T036 APPROVED 2026-04-17).

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl`
- Risk acceptances: `.security/exceptions.jsonl` (not written — no acknowledgments)
- SARIF report: `.security/reports/b793ab198ea5.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
