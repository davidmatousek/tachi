# Security Scan Report

**Feature**: 256 — Source-Pattern Hardening (BLP-02 F-2)
**Branch**: 256-source-pattern-hardening
**Commit**: 9554a6e02884
**Scan ID**: c4556ab6-5acd-4ae4-b55b-fdbdd758b644
**Timestamp**: 2026-05-05T18:29:20Z UTC
**Status**: PASSED

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 10 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

**SCA**: Skipped — no dependency manifests changed (NFR-002 verified at T050: zero new runtime dependencies).

---

## Findings

No security findings detected.

---

## Files Analyzed (SAST)

| File | Type | Notes |
|---|---|---|
| `scripts/init.sh` | bash | Site A migration — `source defaults.env` replaced with `aod_template_load_kv_file` + `STACK_PACK_ALLOWED_KEYS` whitelist. All variables properly quoted; error path uses `>&2` + `exit 1`. No new attack surface. |
| `tests/fixtures/init-baseline-tree/.aod/scripts/bash/template-substitute.sh` | bash | Baseline copy of post-F-2 hardened script. Test fixture; not executed in production. |
| `tests/fixtures/regenerate-config-load-baseline.sh` | bash | Fixture regeneration script. No user input; delegates to F-1's `regenerate-baseline.sh` for byte-identity refresh. No injection surface. |
| `tests/scripts/conftest.py` | python | `hanging_upstream` fixture — local TCP listener on `127.0.0.1` ephemeral port, never writes data. Test-only; no network exposure. |
| `tests/scripts/test_init_input_unit.py` | python | F-1 contract amendment cases. List-form `subprocess.run` only; no `shell=True`. |
| `tests/scripts/test_init_sh_defaults_env.py` | python | Site A end-to-end test. List-form `subprocess.run` only. Asserts `/tmp/F-256-pwned` never created on adversarial fixture. |
| `tests/scripts/test_template_config_load_integration.py` | python | Site B/D integration. List-form `subprocess.run`; LC_ALL=C pinned. |
| `tests/scripts/test_template_config_load_unit.py` | python | 27-case library unit test. List-form `subprocess.run`; LC_ALL=C pinned. |
| `tests/scripts/test_template_git_clone_timeout.py` | python | Stream 4 watchdog test (6 cases) using session-scoped `hanging_upstream` fixture. |
| `tests/scripts/test_template_substitute_lint_no_eval.py` | python | Future-PR-blocker lint: `grep -c '\beval\b' template-substitute.sh` returns 0. |

## OWASP P0 Pattern Analysis

| Category | Patterns Checked | Result |
|---|---|---|
| A01 Broken Access Control | open redirect, path traversal | None — no HTTP handlers; bash scripts validate path arguments |
| A02 Cryptographic Failures | hardcoded secrets, weak crypto, insecure random | None — no crypto operations; no secret literals; SHA256 used only for fixture chain hashing |
| A03 Injection | SQL, command, template | None — all `subprocess.run` use list-form (no `shell=True`); bash uses regex-validated KV parser; eval surface eliminated at template-substitute.sh |
| A05 Security Misconfiguration | debug mode, CORS, verbose errors, defaults | None — no web server config; error paths emit to stderr without leaking traceback |
| A07 Auth Failures | insecure cookie, plaintext credentials | None — no authentication code |

## Note on .aod/ Exclusion

The `/security` skill excludes `.aod/` per its default file filter (rationale: `.aod/` is template scaffolding shared across adopters). For this repo (tachi itself), F-2's primary code lives in `.aod/scripts/bash/` (template-config-load.sh, template-git.sh, template-substitute.sh, init-input.sh).

These files were independently reviewed in Step 5 by:
- **architect**: APPROVED (13/13 checks) — `.aod/results/architect-final-review.md`
- **security-analyst**: APPROVED (15/15 checks; 0 critical/high/medium/low; 5/5 vuln_ids closed) — `.aod/results/security-analyst-final-review.md`
- **code-reviewer**: APPROVED_WITH_CONCERNS (10/10 checks; 2 minor + 3 suggestions) — `.aod/results/code-reviewer-final-review.md`

## Vuln IDs Closed by F-2 (engineering complete; REMEDIATED events at /aod.deliver T059)

| vuln_id | Severity | Site |
|---|---|---|
| TACHI-VULN-6f5a95085056 | HIGH | Site A — `scripts/init.sh:106` defaults.env source |
| TACHI-VULN-bf5496e9fcdf | HIGH | Site B — `template-git.sh` aod-kit-version reader+writer |
| TACHI-VULN-9a7512071b4a | MEDIUM | Site C — `template-substitute.sh` 4× eval invocations |
| TACHI-VULN-4dc6cf8f88ea | MEDIUM | Site D — `template-substitute.sh` 47-line subshell-source |
| TACHI-VULN-851fd6a21ba9 | LOW | Stream 4 — `template-git.sh` unbounded clone |

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl`
- Vulnerability events: `.security/vulnerabilities.jsonl`
- SARIF report: `.security/reports/9554a6e02884.sarif`

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
