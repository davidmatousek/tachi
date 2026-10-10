# Security Scan Report

**Feature**: 373 — Adopter Install + Output Fidelity Fixes
**Branch**: 373-adopter-install-output-fidelity
**Commit**: c2212fbd8500
**Scan ID**: fce40a85-d8a7-46d2-bcbe-4cf339ca9704
**Timestamp**: 2026-10-10T19:17:08Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 15 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

SCA: No dependency manifests changed — skipping dependency audit.

---

## Scan history (this feature)

This report is the third of three scans in `/aod.build` Step 7. Scan 3 is authoritative: it ran at the commit that ships.

| # | Scan ID | Commit | Status | Result |
|---|---|---|---|---|
| 1 | `69885bc9-20ae-44b8-98c6-d7c21c9aacb7` | `276dd2849db0` | FINDINGS | 1 HIGH: `tachi-VULN-217a46966920`. At the gate the maintainer chose **(A) Fix now**, so nothing was acknowledged |
| 2 | `64d7e752-c228-4287-af66-5c502bca7e66` | `eb5d3febfaa0` | PASSED | 0 findings. The HIGH is remediated. See the method correction below |
| 3 | `fce40a85-d8a7-46d2-bcbe-4cf339ca9704` | `c2212fbd8500` | **PASSED** | 0 findings at the final code tip. It follows the code review's D-1 (`17419ae`) and D-2 (`02e42eb`) refinements of the two fixes |

**Method correction.** Scans 1 and 2 used a shell pattern screen. Its Python-file and hardcoded-secret checks passed the file list through an unquoted zsh variable, which zsh does not word-split. So those checks read no file, and their zero counts carry no evidence. Three things in scans 1 and 2 were valid:
- the `install.sh` checks, which used a literal path;
- the `subprocess` call review, which used command substitution;
- the manual read that found the HIGH.

Scan 3 reran every pattern in Python over the 15 files. Every file was read (17,240 lines), so scan 3 is the evidence for this report. The Step 5 security-analyst and code reviews reached the same conclusion independently.

**`tachi-VULN-217a46966920`** (scan 1; HIGH 7.5, estimated; A01 Broken Access Control, CWE-22 path traversal; KEV N/A):
- **Location.** `scripts/extract-report-data.py:879` (also `:889`) at `276dd28`. The ID source is `_parse_attack_tree_file`.
- **Defect.** Attack-tree finding IDs were read from `attack-trees/*.md`, either from the `Finding ID` cell or from the heading token. They were used unvalidated to build the `.mmd` temp path and the rendered PNG path. An ID containing `../` therefore wrote outside the temp and `attack-trees/` directories. Reproduced in scratch: the extractor attempted to write `<tmp>/../../../escaped-ctf.mmd`, then aborted the report run on the uncaught error. Under pytest's temp root, the old code really did write outside its test directory.
- **Scope.** The code predates F-373 and is also in released v4.48.0. It is reachable only through crafted or injected attack-tree files in the target directory.
- **EPSS context.** Path traversal vulnerabilities are actively exploited in 5–12% of exposed systems; automated scanners commonly detect and exploit them.
- **Remediation** (`1961ee9` tests, `eb5d3fe` fix):
  - finding IDs must match `^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*$` where they are parsed, and any other ID is skipped with a warning;
  - both write sites assert that the resolved path stays under its base directory.
- **Verification:**
  - every real attack-tree ID in the tracked examples passes;
  - `oracle-diff.md` shows 0 JSON, `.typ` or stderr changes at `eb5d3fe`;
  - the scratch repro now exits 0 with one warning and no write.

**Also remediated before this scan** (from the Step 5 security-analyst review, not a SAST pattern finding): **SEC-K3-07** (MEDIUM).
- **Defect.** A tab or newline byte in the project path desynced `install.sh`'s pre-flight. That hid symlinks, even without `--follow-symlinks`.
- **Fix.** `install.sh` now refuses such paths, fail-closed, before any classification or write (`6dbf919` tests, `dec0fbd` fix).

---

## Findings

No security findings detected.

Scan 3 screened all 15 changed code files (17,240 lines) for every OWASP P0 pattern family in the skill (A01, A02, A03, A05, A07). It found 0 injection, secret, crypto, debug or cookie matches, and `shell=True` appears nowhere.

The attack-tree traversal sites in `extract-report-data.py` are now guarded:
- ID validation at `:689` (attack-tree files) and `:772` (the `threat-report.md` inline fallback, D-2);
- containment checks at `:929-930` and `:948`.

`install.sh`'s delimiter-byte guard (`:264`) now also covers the raw `--source` value (D-1).

`subprocess` is called 18 times:
- **2 in product code**, `extract-report-data.py:941` and `:1600`. Both use an argument list with a fixed `mmdc` executable and no shell, so neither is command injection.
- **16 in test harnesses**, which invoke the scripts under test.

`install.sh:542` has one `rm -f`. It removes only fixed deprecated-command names under the project root, skips linked paths, and runs after the K3 pre-flight.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan. Scan 1's HIGH was fixed, not acknowledged.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (three entries, chained and verified)
- Vulnerability events: `.security/vulnerabilities.jsonl` (`tachi-VULN-217a46966920`: DETECTED, then REMEDIATED)
- Risk acceptances: `.security/exceptions.jsonl` (none)
- SARIF reports:
  - `.security/reports/276dd2849db0.sarif` (scan 1, 1 result);
  - `.security/reports/eb5d3febfaa0.sarif` (scan 2, clean);
  - `.security/reports/c2212fbd8500.sarif` (scan 3, clean).

**Integrity note (pre-existing, not this feature).** A verification pass over `scan-log.jsonl` found that entry 34 (`338-restore-substitution-hardening`, 2026-06-30) does not match the chain-hash rule. The entries after it verify against its stored hash. Entry 5 is a chain restart that verifies as a first entry. The log is append-only, so it is left as is; this is recorded for follow-up.

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
