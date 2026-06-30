# Security Scan Report

**Feature**: 338 — Restore F-248/F-256 Substitution Hardening
**Branch**: `338-restore-substitution-hardening`
**Commit**: 18a39ed3b010
**Scan ID**: a08760ca-77fa-4fb1-bf15-9f14717fed86
**Timestamp**: 2026-06-30T14:47:28Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 2 |
| Manifests audited (SCA) | 1 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

**Security Scan: PASSED — no issues found** (AI-powered analysis; supplement with dedicated SAST tools for production-critical systems).

---

## Scope

SAST (`git diff --name-only main...HEAD`, code files, excluding `.aod/` and `docs/`):
- `scripts/init.sh` — the restored F-248/F-256 hardening (parameter-expansion substitution + `STACK_PACK_ALLOWED_KEYS` whitelist loader). **Byte-identical to shipped v4.44.0 (`5b64f68`)** — see W-1 spot-check in `tasks.md` T007.
- `tests/scripts/test_init_sh_substitution.py` — test module (FR-007 xfail groundwork).

> The two other restored hardening scripts (`.aod/scripts/bash/template-substitute.sh`, `.aod/scripts/bash/template-git.sh`) live under `.aod/` and are excluded from SAST per the skill's directory-exclusion rule. Both are byte-identical to `5b64f68` (T007) and ADD hardening (the F-248 `patsub_replacement` shim and the F-256 `AOD_FETCH_TIMEOUT` watchdog).

SCA (dependency manifests in the branch diff):
- `stacks/nextjs-supabase/scaffold/package.json` — the #336 dep-floor raise (`next >=16.2.3 → >=16.2.6`, `vitest >=4.0.0 → >=4.1.0`). This commit (`f1f396d`) deliberately raised the floors *past* vulnerable ranges; it is not part of the #338 restore commit (named in FR-008 / SC-004 as an on-branch out-of-scope delta).

---

## Findings

No security findings detected.

### SAST analysis
- `scripts/init.sh`: no OWASP P0 patterns. No `eval`/`os.system`, no hardcoded secrets, no unsafe RNG for security use. The four `bash -c` invocations are **fixed-string** (`source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board`) with no user-input interpolation — not command injection (A03). The restored substitution path uses bash parameter-expansion (ADR-038) specifically to avoid `sed` metacharacter corruption, and the F-256 loader replaces `source defaults.env` with the `aod_template_load_kv_file` whitelist parser (ADR-040) — i.e., this diff **adds** injection-resistance rather than introducing risk. Code is byte-identical to v4.44.0, which already shipped through this gate.
- `tests/scripts/test_init_sh_substitution.py`: test module. Adversarial strings (e.g. `CUSTOM_HOOK="$(touch /tmp/...)"`) are test fixtures asserting the loader's reject path, not application vulnerabilities.

### SCA analysis
- `stacks/nextjs-supabase/scaffold/package.json`: all dependency ranges carry real floors (`next >=16.2.6`, `react >=19.0.0`, `vitest >=4.1.0`, `zod >=3.23.0`, `prisma >=7.0.0`, `playwright >=1.55.1`, etc.). No unsafe wildcard ranges (`*`, `latest`, `>=0.0.0`). No KEV-listed or known-vulnerable package at the declared floors (training cutoff January 2026). This is a **scaffold template** manifest (adopter starting point), so open-ended `>=` floors are intentional; resolved versions are pinned in the adopter's lock file.

> SCA findings are based on Claude training knowledge (cutoff: January 2026). Supplement with real-time CVE scanning (npm audit, pip-audit, Snyk) for production workloads.

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan (no CRITICAL/HIGH findings).

---

## Vulnerability lifecycle note

This is a **diff-scoped** scan (only files changed on the feature branch vs `main`). Pre-existing entries in `.security/vulnerabilities.jsonl` from other features' scans (e.g. an INFO note in `specs/185-*/`) are **out of this scan's scope** and were intentionally **not** marked `REMEDIATED` — a diff-scoped clean scan provides no evidence that out-of-scope findings were fixed. No new `DETECTED` events were written (0 in-scope findings). The vulnerability log is therefore unchanged this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (PASSED entry, chained)
- SARIF report: `.security/reports/18a39ed3b010.sarif` (0 results, SARIF 2.1.0)
- CycloneDX SBOM: `.security/reports/sca-2026-06-30.cdx.json` (17 scaffold components)
- Vulnerability events: `.security/vulnerabilities.jsonl` (unchanged — see note above)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
*SCA findings are based on Claude training knowledge (cutoff: January 2026). Supplement with real-time CVE scanning (npm audit, pip-audit, Snyk) for production workloads.*
