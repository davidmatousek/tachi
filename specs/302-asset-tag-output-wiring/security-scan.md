# Security Scan Report

**Feature**: 302 — Asset-Tag Output Wiring (F-260b)
**Branch**: `302-asset-tag-output-wiring`
**Commit**: `fadd21c99f89`
**Scan ID**: `06a1d6fa-9223-49a4-86c2-3ad116f516b9`
**Timestamp**: 2026-06-01T11:44:49Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 7 |
| Manifests audited (SCA) | 0 (skipped — no manifests changed) |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

**Security Scan: PASSED — no issues found** (AI-powered analysis; supplement with dedicated SAST tools for production-critical systems).

---

## Scope

SAST analyzed the 7 code files changed on the branch (`git diff --name-only main...HEAD`, filtered to code extensions, `docs/`/`.aod/` excluded):

| File | Role |
|------|------|
| `scripts/populate-affected-assets.py` (NEW, 468 LoC) | Deterministic populator (value authority) — joins component→asset map to findings, writes the `affected_assets` block into `threats.md` |
| `scripts/sarif_common.py` (+49) | Shared `parse_affected_assets` extractor |
| `scripts/generate-threats-sarif.py` (+18) | Adds `result.properties.affected_assets` (snake_case) |
| `scripts/generate-risk-scores-sarif.py` (+12) | Adds `result.properties.affected_assets` (snake_case) |
| `tests/scripts/test_affected_assets_wiring.py` (NEW) | Wiring test suite |
| `tests/scripts/test_sarif_common_affected_assets.py` (NEW) | Extractor test suite |
| `tests/scripts/test_output_integrity.py` (+9) | schema_version 1.8→1.9 fixture update |

SCA: skipped — no dependency manifests (`requirements.txt`, `pyproject.toml`, `package.json`, etc.) changed on the branch.

---

## Findings

No security findings detected.

### OWASP P0 pattern coverage (all PASS)

| OWASP category | Patterns checked | Result |
|----------------|------------------|--------|
| A01 Broken Access Control | path traversal, open-redirect; file IO derived from content | None — file IO is on `argparse`/constant paths (operator-controlled CLI args), never content-derived |
| A02 Cryptographic Failures | password hashing (md5/sha1), insecure random, hardcoded secrets | None (see Observations re: a pre-existing non-crypto fingerprint) |
| A03 Injection | SQL concat, `os.system`/`subprocess`/`eval`/`exec`/`shell=True`, template injection | None — stdlib-only, no shell/exec/DB surface |
| A05 Security Misconfiguration | DEBUG, `pickle`, `yaml.load`, permissive CORS, verbose errors | None |
| A07 Identification & Auth | insecure cookies, plaintext credentials | N/A — no auth/session code |

Imports across the production scripts are stdlib-only: `json`, `re`, `sys`, `argparse`, `pathlib`, `hashlib` (plus local `sarif_common` / `tachi_parsers`). **No network, subprocess, or eval surface added.**

---

## Observations (non-findings)

- **`generate-threats-sarif.py:398` — `hashlib.md5(fid.encode("utf-8")).hexdigest()[:16]`** (`line_hash_for`): a non-cryptographic identity fingerprint of a pipeline-generated finding ID, used to build a SARIF `partialFingerprints` value. This is **not** password/secret hashing (the weak-crypto rubric explicitly excludes checksum/identifier use) and is **pre-existing code** — it is not part of the F-260b diff. Recorded here for audit transparency; **not classified as a finding**.
- **`finding_id` pipe-escaping (defense-in-depth)**: the Step 5 human security review (`.aod/results/security-analyst.md`) noted one LOW — an unescaped `|` in a `finding_id` could break a `threats.md` block row on re-parse. Non-exploitable: finding IDs are pipeline-generated under a fixed prefix grammar (`S-1`, `T-3`, …), never adopter-controlled. Optional hardening only; does not block delivery.

---

## Cross-reference: Step 5 human security review

This automated SAST/SCA scan is the Step 7 layer. The Step 5 human-judgment security review (`.aod/results/security-analyst.md`) independently returned **APPROVED** (0 CRITICAL / 0 HIGH / 0 MEDIUM / 1 non-exploitable LOW), with empirical evidence: ReDoS-resistant regexes (<11ms on 200k-char pathological inputs), injection blocked by the frozen 6-value tag allowlist, SARIF emitted via `json.dumps`, and no network/exec/path-traversal surface. Both layers concur: **production-ready**.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan (no blocking findings).

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (chain_hash `fa01fe92754e246cb4115193c2e30254d11ad4cbba816fcebd659ddfefa7b667`)
- Vulnerability events: `.security/vulnerabilities.jsonl` (no lifecycle events this scan — clean feature-diff scan)
- Risk acceptances: `.security/exceptions.jsonl` (none)
- SARIF report: `.security/reports/fadd21c99f89.sarif` (SARIF 2.1.0, 0 results)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
