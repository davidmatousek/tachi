# Security Scan Report

**Feature**: 272 — SECURITY.md and Private Disclosure Channel (BLP-02 Wave 3)
**Branch**: main
**Commit**: 7b1cc53e6f57
**Scan ID**: 5345e7a2-5944-486c-b6e7-8e57e238261e
**Timestamp**: 2026-05-08T17:32:45Z UTC
**Status**: PASSED
**Trigger**: Post-merge re-scan (T021, FR-013) after PR #273 squash-merge into main

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 0 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

The squash-merge (`7b1cc53 feat(272): SECURITY.md and private disclosure channel (#273)`) introduced changes only to documentation files (`SECURITY.md`, `CHANGELOG.md`, `README.md`, plus `specs/` and `docs/product/` artifacts). No code-extension files (`.py .js .ts .jsx .tsx .sh .go .rs .java .rb .swift .kt .php .cs .cpp .c .h`) and no dependency manifests (`requirements.txt`, `package.json`, `go.mod`, etc.) were modified. SAST and SCA both correctly skip via Step 1a/1b zero-file paths; clean-scan path (Step 5c) reaches PASSED.

---

## Findings

No security findings detected on the merged main HEAD.

---

## TACHI-VULN-05abc41ad4cc — REMEDIATED

The previously-DETECTED finding `TACHI-VULN-05abc41ad4cc` (INFO, A05 Security Misconfiguration — SECURITY.md missing private disclosure channel guidance) is now REMEDIATED on main per the Step 6c lifecycle rule. The remediation lifecycle is captured in `.security/vulnerabilities.jsonl`:

```
2026-05-02T10:51:56Z DETECTED    scan_id=5cd62414...  file=SECURITY.md  severity=INFO
2026-05-08T17:32:45Z REMEDIATED  scan_id=5345e7a2...  file=SECURITY.md  severity=INFO
```

**Remediation evidence** (delivered in PR #273):

- `SECURITY.md` Section "Reporting a Vulnerability" now references the GitHub *Report a vulnerability* button as primary instruction with the canonical `https://github.com/pratik-saptarshi/tachi-rust/security/advisories/new` fallback URL (FR-001 .. FR-004).
- GitHub Private Vulnerability Reporting (PVR) toggle was confirmed ON at 15:34 UTC 2026-05-08 via repo settings UI (FR-007 + AC-6 + D-5; durable plain-text confirmation captured in PR #273 description and tasks.md T007/T017 result rows).
- README.md `## Community` section now contains a one-line pointer to SECURITY.md (FR-008 + T014).
- CHANGELOG.md F-3 entry (BLP-02 Wave 3) cites TACHI-VULN-05abc41ad4cc closure with INFO + A05 + BLP-02 Wave 3 metadata (FR-009 + T013).

---

## No New Findings Introduced (US3 / SC-006 confirmation)

Comparison against the pre-merge baseline (`.security/vulnerabilities.jsonl` state at scan_id 5cd62414 from 2026-05-02): zero new HIGH or MEDIUM findings, zero new LOW or INFO findings introduced by the F-3 changes. The only delta is the REMEDIATED event above.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan (no blocking findings).

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (chain-hashed entry appended)
- Vulnerability events: `.security/vulnerabilities.jsonl` (REMEDIATED event appended)
- Risk acceptances: `.security/exceptions.jsonl` (no new entries)
- SARIF report: `.security/reports/7b1cc53e6f57.sarif`
- Mirror: `.aod/results/security-scan.md` (task T021 literal path)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems. This re-scan validates the post-merge state of TACHI-VULN-05abc41ad4cc per FR-013; the underlying remediation is documentation-only (SECURITY.md content + GitHub repo settings toggle), so no SAST/SCA pattern detection is invoked.*
