# Security Scan Report (Part B)

**Feature**: 391 — Isolated and Auditable Operation (Part B, B2 only)
**Branch**: 391-isolated-auditable-operation-part-b
**Commit**: 644f12f49bbc (T047 merge of `origin/main` at `0b54bb5`, after Part A's delivery)
**Scan ID**: c8eec611-33d5-4a0e-b350-84085688ac9c
**Timestamp**: 2026-11-21T19:32:29Z UTC
**Status**: PASSED (no findings)

Standalone `/security` run at T047, because Part A's scan (`security-scan.md`, run `aea09d85c908`) did not cover B2's code. Scope: the code files that `git diff origin/main...HEAD` lists in this worktree, so Part A's files, already scanned, are not re-counted.

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 5 |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 0 |
| LOW findings | 0 |
| INFO findings | 0 |

SCA: No dependency manifests changed — skipping dependency audit.

---

## Findings

No security findings detected.

### What was reviewed (one batch of five files, OWASP P0 patterns A01, A02, A03, A05, A07)

| File | Review notes |
|---|---|
| `scripts/stamp-tachi-version.py` (new, 297 lines) | No subprocess, `exec` or `eval`. The marker value is accepted only when it matches `[A-Za-z0-9][A-Za-z0-9._+~-]{0,127}` on exactly one line, so nothing that a double-quoted YAML scalar would need escaped reaches `threats.md`; a malformed or absent marker stamps `unknown`. The threats file is read as bytes after an `S_ISREG` check; the marker is checked with `lstat`, so a symbolic link reads as `unknown`. The write goes through a temp file opened `O_WRONLY|O_CREAT|O_EXCL` at mode 0600, then `chmod` to the original mode and `os.replace`; a read-only target is refused rather than replaced. Paths come from the command line of a local CLI, not from an untrusted boundary. `traceback` is used only for a line number in an internal-error message. |
| `scripts/install.sh` (B2 hunks: marker guard and write) | The version string is allow-listed by a spelled-out `case` pattern (a letter or digit first, then letters, digits and `._+~-`) and capped at 128 characters before it is written, so no newline or shell metacharacter reaches the marker file. `git -C "$SOURCE_DIR" describe` and `git rev-parse` run with quoted, script-owned paths; the release-manifest fallback is read with `sed` and filtered by the same allow-list. `marker_guard` refuses a symbolic link at the marker, a non-regular file, an unresolvable path and a path inside the source clone; `rm -f` runs only when neither `templates` nor `templates/tachi` is a link. The write uses `set -C` (noclobber, so an existing file or link at the temp name fails instead of being written through) and `mv -f`; a failed write dies with a message and removes the temp file. |
| `scripts/generate-threats-sarif.py` (B2 hunks) | `semanticVersion` is read from the input's frontmatter by a bounded regex (`[^"\s#]+`) through the parsers' own frontmatter splitter, with `schemas/output.yaml` as the fallback, and is emitted through `json.dumps`, so it is escaped. No new I/O surface. |
| `tests/scripts/test_tachi_version_marker.py` (new) | Every `subprocess.run` takes an argument list; the one `bash -c` runs README.md's own manual-install loop with its `TACHI=` line rewritten through `shlex.quote`, under a hermetic environment (isolated git config, `HOME` in the temp dir, `GIT_CEILING_DIRECTORIES`, no network). Temp dirs are removed with `shutil`. The only credential-like literal is the test identity `test@example.invalid`. |
| `tests/scripts/test_threats_schema_contract.py` (new) | Argument-list subprocesses run under `tmp_path` with `-I -B`; YAML is read with `yaml.safe_load`; the stamp module is imported from the repository tree. No secrets, no shell. |

Not SAST-scoped by extension, read for completeness: `.github/workflows/tachi-pytest.yml` (a `py39-floor` job pinned to `ubuntu-24.04`, `contents: read`, no secrets, no `pull_request_target`) and `schemas/output.yaml` (data only).

---

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

## Lifecycle note

`.security/vulnerabilities.jsonl` is unchanged. The skill's REMEDIATED rule (a previously recorded `vuln_id` absent from this scan) was not applied to `tachi-VULN-d229b69fb5e4` (Part A's LOW in `scripts/extract-report-data.py`, tracked as #416): that file is outside this scan's scope, not remediated.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (chain hash continues from the Part A entry `aea09d85c908`)
- Vulnerability events: `.security/vulnerabilities.jsonl` (no new events)
- Risk acceptances: `.security/exceptions.jsonl` (absent; none recorded)
- SARIF report: `.security/reports/644f12f49bbc.sarif` (zero results)

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
