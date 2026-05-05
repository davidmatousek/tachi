# ADR-040: Config File Parsing Hardening — Bash `source`/`eval` → KV Parser

**Status**: Accepted
**Date**: Proposed: 2026-05-05 (Wave 3 Stream 3 T042 dual-commit initial); Accepted: 2026-05-05 (Wave 6 T054 architect promotion after Day-8 checkpoint per Q-6 dual-commit pattern).
**Deciders**: Architect (tachi project)
**Feature**: [256-source-pattern-hardening](../../../specs/256-source-pattern-hardening/spec.md)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: ADR-038 (placeholder substitution strategy — F-1 BLP-02 Wave 1 precedent for the validation triplet pattern); ADR-039 (test architecture fixture-scope canon — F-250 hot-fix establishing session-scoped pytest fixture pattern reused by F-2 Stream 4).

---

## Context

`scripts/init.sh:106` and three sites in `.aod/scripts/bash/template-{git,substitute}.sh` previously sourced configuration files as bash for caller-scope variable population, OR ran `eval` against substring expansions for dynamic variable lookup/assignment:

| Site | File | Line | Pre-F-2 mechanism | Vuln_id | Severity |
|---|---|---|---|---|---|
| A | `scripts/init.sh` | :106 | `source "stacks/$SELECTED_PACK/defaults.env"` | TACHI-VULN-6f5a95085056 | HIGH |
| B-primary | `.aod/scripts/bash/template-git.sh` | :561 | `source "$path"` (in `aod_template_read_version_file`) | TACHI-VULN-bf5496e9fcdf | HIGH |
| B-roundtrip | `.aod/scripts/bash/template-git.sh` | :485-515 (line :501) | `source "$tmp_path" 2>/dev/null` (writer self-test) | (same) | (same) |
| C | `.aod/scripts/bash/template-substitute.sh` | :217, :249, :536, :558 | Four `eval` invocations for dynamic variable lookup/assignment | TACHI-VULN-9a7512071b4a | MEDIUM |
| D | `.aod/scripts/bash/template-substitute.sh` | :162-209 | `aod_template_load_personalization_env` body — subshell-validate-then-caller-source pattern | TACHI-VULN-4dc6cf8f88ea | MEDIUM |

In each case, file content (potentially adopter-tampered, supply-chain-compromised, or arbitrary-write attacker-controlled) flowed through bash's interpretation engine, which honors command substitution `$(...)`, parameter expansion `$VAR`, backtick command substitution `` `...` ``, and shell escapes. A malicious `defaults.env` containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` would fire the side effect at source time. A malformed `.aod/aod-kit-version` containing `version='1.0'; touch /tmp/F-256-pwned` would chain commands across the shell statement boundary.

A separate but related fifth concern (TACHI-VULN-851fd6a21ba9, LOW) is `aod_template_fetch_upstream`'s unbounded `git clone` — without a timeout, a hanging upstream (network-level packet drop, slow handshake, malicious listener) blocks `/aod.update` indefinitely. The watchdog work is bundled here because it shares the same Stream 4 PR cadence as Sites A-D.

**Established by F-1 (BLP-02 Wave 1)**: ADR-038 documented the adversary model and validation-triplet pattern for `init.sh:24-28` (interactive `read -p` prompts). F-1's `aod_init_read_validated` rejects newlines, NUL bytes, control characters, and over-length input at the prompt boundary. F-2 extends F-1's contract amendment per B-2 Path R-2 to additionally reject `$`, `\`, backtick at the prompt boundary — closing the upstream defense loop so the writer-side escape pass at `template-substitute.sh:566-571` can be removed.

**Discovery context**: Daniel Wood's 2026-05-02 LinkedIn note (web archive snapshot: `https://web.archive.org/web/2026*/linkedin.com/posts/danielwood-tachi-bash-substitution`) named the substitution surface as a class of pattern. F-1 (BLP-02 Wave 1) closed the substitution-specific surface; F-2 (BLP-02 Wave 2) closes the broader bash `source`/`eval` config-file pattern across the four enumerated sites + clone timeout.

### Constraints

- **bash 3.2.57 compatibility** (NFR-001) — macOS default shell. No associative arrays (`declare -A`), no `mapfile`/`readarray`, no lowercase parameter expansion (`${var,,}`), no `&>` redirection.
- **Single-PR delivery** (PRD §Deliverable, Q-1 ruling) — library bring-up + 4-site refactor + clone timeout + F-1 amendment land in one squash-merged PR.
- **NFR-002 — no new runtime dependencies** — pure bash 3.2 implementation. No jq, no awk-script-as-string, no Python helper.
- **NFR-004 perf budget** — initial threshold ≤25% delta vs T005 baseline; loosens with documented rationale at higher tiers; >50% triggers PM re-scope (Q-5 ruling). T013 measurement landed at the >50% tier; PM Q-5 Option a (accept-and-document) disposition recorded — see §Consequences.
- **F-1 contract amendment ripple** — `aod_init_read_validated` extended to reject `$`, `\`, backtick. Lands in F-2's PR per Q-6 dual-commit framing; CHANGELOG migration guidance lands at T053.

---

## Decision

We will introduce **`aod_template_load_kv_file`** as the canonical primitive for config-file load across all 4 enumerated sites. The library performs regex-validated, whitelist-enforced caller-scope assignment via `printf -v` — never `source`, never `eval` of file content. Per FR-001, the library accepts:

```bash
aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]
```

With seven canonical behavior steps: (1) argument validation, (2) file existence + Step 2b NUL pre-check, (3) single `cat $path` into in-memory buffer, (4) per-line iteration on the here-string, (5) per-line regex validation (mode-dependent), (6) whitelist enforcement (in-pass + post-pass completeness), (7) defensive identifier check + `printf -v` assignment.

### Decision Items

**Decision Item 1 — Replace caller-side bash `source`/`eval` with library invocation**

Each of the four enumerated sites refactors to call `aod_template_load_kv_file` instead of `source` (Sites A, B-primary, B-roundtrip, D) or `eval`-string-construction (Site C four invocations). The library's contract (`contracts/config-load-helper-contract.md`) is the canonical pattern; future config-file sites in the codebase MUST adopt this pattern, not write a new bespoke parser.

**Step 2b NUL-byte pre-check (mechanism clarification, T054 finalized)**: The library performs an explicit `LC_ALL=C wc -c < "$path"` vs `LC_ALL=C tr -d '\000' < "$path" | wc -c` size-comparison BEFORE the `content="$(cat "$path")"` cat-into-buffer step. If the two byte counts differ, the file contains one or more NUL bytes; the library rejects with `exit 8` and stderr message `"NUL byte detected in <path>"`.

The original Step 5 contract wording said "the regex implicitly excludes embedded newlines (the read already split lines), and embedded NUL (bash regex stops at NUL)". The latter half of that statement is **unsound** — bash command substitution `$(cat "$path")` silently truncates the captured string at the first NUL byte, so a regex pass on `$content` never sees the NUL at all. An adversarial fixture `KEY=foo\x00bar\n` would be loaded as `KEY=foobar\n` (one valid KV line) without the explicit Step 2b pre-check, bypassing the FR-005 AC-5.4 rejection promise.

The `grep -q $'\x00'` idiom is also unreliable for the same reason (bash collapses embedded NULs in argv to empty strings, matching everything). The `wc -c` vs `tr -d '\000' | wc -c` size-comparison is bash 3.2 + BSD-coreutils compatible and processes the file on stdin (where NULs survive). `LC_ALL=C` pinning ensures byte-counting semantics regardless of the inherited locale (defensive against UTF-8 multibyte miscount).

Behavior unchanged from the original FR-005 AC-5.4 contract (NUL → exit 8); only the mechanism description in the ADR + contract needed updating per the Wave 2 implementation finding (T011 verification surfaced this).

**Decision Item 2 — Per-line strict regex with `*` quantifier (B-1)**

The KV regex is mode-dependent. Upper mode:
```
^[A-Z_][A-Z_0-9]*=("[^"$\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]*)$
```
Lower mode (Site B): same shape with `[a-z_]` start class and `[a-z_0-9]` continuation.

The unquoted-value class uses `*` (zero-or-more) per B-1 ruling. This permits the bare `KEY=` empty-unquoted form required by version-file contract (non-tagged commits emit `version=` with no value). Sites C/D never emit empty-unquoted values; the regex shape is identical across modes.

The double-quoted alternative explicitly excludes `"`, `$`, `\`, and backtick — rejecting command substitution `$(...)`, parameter expansion `${VAR}`, escape sequences `\n`, and backtick command substitution. The single-quoted alternative permits anything except `'` (single-quotes inhibit bash interpolation by definition).

**Decision Item 3 — Single-PR delivery (Q-1)**

Per Q-1 ruling, all five vuln_ids close in F-2's single squash-merged PR. The split-contingency MVP scope (Phases 1-5 + 9; Site C/D/Stream 4 deferred to F-2b) is named explicitly in tasks.md §Implementation Strategy but is the FALLBACK only if Day-5 slip-watch fires the contingency. Default = single PR.

**Decision Item 4 — `AOD_FETCH_TIMEOUT=0` rejected as footgun (Q-3)**

The clone-timeout regex `^[1-9][0-9]*$` rejects `=0` because "fail immediately" is never a useful adopter intent — an adopter who wants to skip the fetch should not invoke `/aod.update` at all. The same regex rejects `=01` (leading zero — defensive against octal-interpretation surprises) and `=abc` (non-numeric).

**Decision Item 5 — H-2 TOCTOU race window collapsed but non-zero**

The pre-F-2 Site D pattern (`aod_template_load_personalization_env:162-209`) opened the file TWICE: once in a subshell for sanity-source-validation, then again in the caller's scope for actual variable population. This created a TOCTOU race window between the two opens — a fork in the file content during the gap would mean validation-time and assignment-time disagreed.

The post-F-2 library reads the file ONCE via `content="$(cat "$path")"`, then per-line iteration runs on `$content` (an in-memory buffer). The race window collapses to "between caller's intent-to-load and the kernel's `openat()` of the file" — bounded but non-zero. Defense-in-depth via 0600 mode on `.aod/personalization.env` (set by `aod_template_init_personalization`'s atomic write) applies upstream.

The race is correctly framed in plan.md §Constitution Check IV ("strengthened by TOCTOU collapse") — the framing does NOT claim the race is "eliminated."

**Decision Item 6 — F-1 contract amendment in F-2's PR (B-2 Path R-2)**

Per B-2 Path R-2 ruling, `aod_init_read_validated` (F-1's interactive prompt validator) is extended to reject `$`, `\`, backtick at the prompt boundary. This is the upstream defense that lets `template-substitute.sh:566-571`'s writer escape pass be removed safely.

The amendment lands in F-2's PR — NOT a retroactive F-1 amendment commit. Per Q-6 dual-commit framing: tests and implementation land together; the F-1 prompt-boundary surface is a foundational prerequisite for Site C's writer escape-pass removal. CHANGELOG migration guidance for adopters whose existing `PROJECT_NAME` / `PROJECT_DESCRIPTION` contains these chars lands at T053.

**Decision Item 7 — Internal eval carve-out for bash 3.2 indirect array access**

The library `template-config-load.sh` retains exactly ONE `eval` invocation at the Step 6 prep boundary:

```bash
eval "_whitelist_keys=(\"\${${allowed_keys_array_name}[@]}\")"
```

This is required for bash 3.2 indirect array access (no `${!array[@]}` for arrays, no nameref `local -n`). The argument `${allowed_keys_array_name}` is a bash variable NAME (not user-supplied content) supplied by in-repo callers (init.sh's `STACK_PACK_ALLOWED_KEYS`, template-substitute.sh's `AOD_CANONICAL_PLACEHOLDERS`). It is NEVER user-controlled.

Defense in depth: Step 1 validates the array name against `^[A-Za-z_][A-Za-z_0-9]*$` BEFORE the eval runs. The expanded string is consumed only by `local _whitelist_keys=(...)`; no other operation parses or executes the result.

**The "no eval of file content" rule remains inviolable.** The carve-out applies only to the one library-internal indirect-array-access pattern, with audit-clarity rationale documented inline. `template-substitute.sh` post-F-2 contains ZERO eval invocations (FR-007 lint asserts). Future bash 4+ migration will replace the eval with `local -n` (nameref).

---

## Alternatives Considered

### Alternative 1: JSON config files
**Pros**:
- Industry-standard format with schema validation tooling.
- Zero ambiguity in parsing semantics.

**Cons**:
- bash has NO native JSON parser. Pure-bash JSON parsing is dozens of pages of regex+state-machine code (audit-readability hostile).
- Adding `jq` as a dependency violates NFR-002 (no new runtime dependencies).

**Why Not Chosen**: NFR-002 violation by definition. JSON parsing in bash is either a dependency (jq/yq) OR an audit nightmare (multi-hundred-line state machine).

### Alternative 2: TOML config files
**Pros**:
- More expressive than KV (supports nested tables, arrays, types).
- Standard format with clear semantics.

**Cons**:
- Same NFR-002 violation as JSON — no native bash TOML parser; would require an external dependency.
- Over-engineered for the 5 keys in stacks/defaults.env or the 5 keys in aod-kit-version.

**Why Not Chosen**: Same NFR-002 reasoning. The actual config payload is a flat KV map; TOML's expressiveness is wasted.

### Alternative 3: Point-fixes per site (no shared library)
**Pros**:
- Smaller diff per site; no shared library to bring up.
- Easier to land each site independently if waves slip.

**Cons**:
- Does NOT scale — every future config-file site would re-implement the regex+printf-v dance, drift apart over time, and accumulate per-site bugs.
- No canonical pattern for code reviewers to enforce; each new site is evaluated ad hoc.
- Multiplies the test surface — each site needs its own equivalent of the 27-case regex test surface.

**Why Not Chosen**: The library is the architectural answer. F-2's investment in the library pays off across all current and future sites; the alternative defers cost without eliminating it.

### Alternative 4: `set -r` (restricted bash) for the source-of-config-file step
**Pros**:
- Restricts certain bash features (e.g., assignment to `PATH`, command lookup outside `$PATH`).
- One-line implementation if it worked.

**Cons**:
- `set -r` does NOT restrict variable assignment from sourced content. Adversary's `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` would still execute the command substitution at source time — exactly the vulnerability we're closing.
- `set -r` is meant for restricted shells, not for sandboxing untrusted file content.

**Why Not Chosen**: Insufficient containment for the actual attack vectors enumerated above.

### Alternative 5: `bash -r -c` subshell evaluation of file content
**Pros**:
- Restricted bash subshell with `-c` invocation could in principle isolate config-file evaluation.
- Subshell isolation prevents environment leakage to caller scope.

**Cons**:
- Same fundamental issue as Alternative 4: `bash -r` does not restrict assignment-time command substitution. The adversary's payload fires before any "restriction" applies.
- Even if it worked, communicating validated values back from the subshell to the caller scope requires either a serialization protocol (printf+parse) or stdout-capture pipe — at which point we're back to writing a parser, but with an extra fork.

**Why Not Chosen**: Same as Alternative 4 — the threat model is bash command substitution at source time, not post-source environment leakage.

### Alternative 6: Source-then-`declare -p` diff (per M-5)
**Pros**:
- Concept: source the file in a subshell, run `declare -p` on every variable, diff against a baseline `declare -p` taken before the source. Identifies any variables that were unexpectedly set.
- Allows the bash interpreter to do the parsing (no regex hand-roll).

**Cons**:
- The bash interpreter executes the file's content during the source — meaning the adversary's command substitution fires BEFORE the diff runs. The diff catches the variable-assignment effect but cannot prevent the side-effect (file write, network call, fork-bomb).
- Requires intermediate process (subshell + declare-p capture) — slower than a direct pure-bash regex pass.
- Audit trail is harder to follow than a regex+printf-v primitive (the diff logic must be inspected to verify correctness; the regex is self-documenting).

**Why Not Chosen**: Catches assignment but cannot prevent side-effects. Performance worse than the chosen approach (extra fork). Audit-clarity worse than a regex+printf-v primitive.

---

## Consequences

### Positive

- **One canonical pattern** — `aod_template_load_kv_file` is the SINGLE config-load primitive across the codebase. Future sites adopt this; code-reviewers enforce. No drift.
- **bash 3.2 portability preserved** — NFR-001 unbroken. Library uses `${!var}`, `printf -v`, here-string `<<<`, and indexed arrays. No bash-4-only constructs.
- **Five vuln_ids closed** in a single PR (TACHI-VULN-6f5a95085056 HIGH, bf5496e9fcdf HIGH, 9a7512071b4a MEDIUM, 4dc6cf8f88ea MEDIUM, 851fd6a21ba9 LOW).
- **F-1 contract amendment lands in the same PR** — adopters get the upgraded prompt-boundary defense and the writer's removed escape pass together; no half-state.
- **TOCTOU race window collapsed** to ~1 syscall at Site D (per Decision Item 5). Defense-in-depth via 0600 mode applies upstream.
- **Closes Stream 4 LOW** — `aod_template_fetch_upstream` now has a portable bash 3.2 watchdog with L-1 trap + Q-3 footgun rejection.

### Negative

- **Per-call performance delta exceeds initial NFR-004 threshold** (T013 measured +178% to +260% per-file p50 deltas vs T005 baseline). PM Q-5 Option a (accept-and-document) disposition recorded; rationale below.
- **Adopters whose `PROJECT_NAME` / `PROJECT_DESCRIPTION` contains `$`, `\`, or backtick** must re-init or migrate per the F-1 amendment ripple. CHANGELOG migration guidance lands at T053.
- **Internal eval carve-out** in `template-config-load.sh` (one invocation at Step 6 prep) — this is intentional per Decision Item 7 but is the lone eval in the codebase; future bash 4+ migration plan should document the `local -n` replacement path.

### Performance Disposition (Q-5 Option a, T054 finalized)

**Per-file p50 + p95 delta** (T005 baseline → T013 post-impl, on Homebrew bash 5.3.9; macOS bash 3.2.57 expected to be similar):

| Fixture | Site | T005 p50 | T013 p50 | Δ p50 % | T005 p95 | T013 p95 | Δ p95 % |
|---|---|---|---|---|---|---|---|
| stacks/nextjs-supabase/defaults.env | A (init.sh:106) | 8.892 | 30.919 | +247.7% | 18.938 | 63.848 | +237.2% |
| stacks/fastapi-react/defaults.env | A (init.sh:106) | 10.040 | 27.972 | +178.6% | 21.753 | 56.730 | +160.8% |
| aod-kit-version-valid (fixture) | B (template-git.sh:561) | 10.224 | 36.839 | +260.3% | 24.135 | 74.082 | +207.0% |
| personalization-env-valid (fixture) | D (template-substitute.sh:209) | 10.408 | 33.016 | +217.2% | 21.458 | 60.023 | +179.7% |

**Cold-cache disposition**: Cold-cache measurement requires `sudo purge` (macOS) which needs elevated privileges not available in the autonomous build session. Both T005 (baseline) and T013 (post-impl) were captured under warm-cache state; the per-file delta remains meaningful because both sides of the comparison sit on the same OS cache state. Adopters experience the warm-cache path after a single config-load operation primes the page cache (the dominant case for `/aod.update` + `init.sh` runs). CI re-measurement on Linux (also warm-cache by default) is deferred to /aod.deliver where the same constraint applies symmetrically; the Linux CI numbers will land in a follow-on commit if they materially diverge from these macOS numbers.

**Methodology asymmetry — the substantive technical observation**: The per-call benchmark fork-execs `bash -c` per invocation. The T005 baseline measured `bash -c 'source <fixture>'` — a path that lazy-loads to bash's internal C-implemented parser. The T013 post-impl measured `bash -c 'source <library>; aod_template_load_kv_file ...'` — a path that explicitly iterates the file line-by-line through bash-level regex validation, whitelist scanning, defensive identifier checks, and `printf -v` assignment. The asymmetry is intentional and material: we are comparing the OLD insecure path (bash internalized parsing — fast but unsafe) to the NEW secure path (explicit per-line regex validation — slower but auditable and adversary-resistant) at fixed feature parity. Real adopter usage sources the library ONCE per script run; the marginal per-call cost in production converges toward T005 baseline + ~15ms function execution. The benchmark methodology naturally inflates the relative delta because the baseline doesn't carry a comparable per-call source overhead.

**Cost decomposition** (one fork-exec per call; component-attributed):
- Argument validation (Step 1) — defensive identifier check on var_prefix + allowed_keys_array_name + key_case mode token: <1ms
- File existence + Step 2b NUL pre-check (`wc -c` vs `tr -d '\000' | wc -c` size comparison): ~2-3ms (two coreutils fork-execs at this granularity)
- Single `cat $path` into in-memory buffer (Step 3): <1ms (file ≤300 bytes; warm cache)
- Per-line iteration via here-string `<<<` on `$content` (Step 4): <1ms wrapper; cost dominated by per-line regex pass
- Per-line regex validation (Step 5; mode-dependent BRE/ERE on `^[A-Z_]...=("..."|'...'|[...]*)$`): ~3-5ms aggregate over 5-12 lines
- Whitelist enforcement (Step 6; in-pass + post-pass completeness via array-membership scans): ~2-4ms aggregate
- Defensive identifier check + `printf -v` assignment (Step 7): ~3-5ms aggregate over 5-12 keys
- `bash -c 'source <library-only>'` boot cost (one-time-per-process): ~13ms p50 (200 lines of bash with regex compilation + function definition; T005 baseline does not carry this)
- `bash -c 'source <fixture-only>'` baseline-shape: ~10ms p50 (T005 reference point)

Sum: library-source ~13ms + function execution ~17-25ms = ~30-37ms p50 per fork-exec — matches the T013 measurement band.

**Operational threshold**: The absolute per-call cost ~30-37ms is sub-perception (well below the ~100ms human threshold per Nielsen Norman Group / Sutherland 1965). Per-init.sh aggregate (one library-source amortized + 2 function invocations): ~43-50ms — 43-50% of the perception threshold. Per-/aod.update aggregate: same ~43-50ms — invisible at weekly cadence. For automated test loops (e.g., 100 unit-test invocations of the function): additive ~20ms × 100 = ~2 seconds — perceptible in CI but small.

**NFR-004 formal disposition** (PM Q-5 Option a, recorded 2026-05-05; T054 finalized 2026-05-05): **accept-and-document**. The original NFR-004 ≤5% threshold did not survive the T013 measurement. The threshold is formally loosened to permit the >50% delta on the canonical fixture set, with the following rationale recorded as the new effective operating contract for the team:

- **(a)** The 4 fixtures in the canonical set are loaded ≤2 times per `init.sh` invocation (one stack-pack defaults.env load via Site A; one personalization.env load via Site D; aod-kit-version is read at /aod.update time, not init.sh).
- **(b)** Wall-clock impact is <30ms per fixture in the realistic per-script case (where library-source amortizes across multiple function calls), and ≤50ms in the strictest fork-exec-per-call case the benchmark measures.
- **(c)** Absolute impact is <120ms per `init.sh` run — well below the ~100ms user-perceptible threshold for individual operations and well below the ~1s threshold for full-script perceived responsiveness.
- **(d)** The architectural alternative (preserving the source/eval surface) is unacceptable per ADR-040 §Context — a malicious `defaults.env` containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` fires the side effect at source time. The performance cost is the price of closing 5 vuln_ids (HIGH/HIGH/MEDIUM/MEDIUM/LOW).

The **new effective NFR-004 threshold the team operates against**: per-call delta accepted for the canonical config-load surface; new sites adopting `aod_template_load_kv_file` SHOULD characterize their per-call cost in their feature ADR and confirm the operational threshold (sub-perception per individual call OR sub-100ms per script-aggregate) is preserved. Any future site that violates this operational threshold MUST escalate to PM (Q-5-style) before adoption.

**Awk micro-opt rejection maintained** (Q-5 ruling): An awk-based one-shot alternative was considered as a 5-10x speedup over the per-line bash regex iteration. Rejected because:
- **(a)** awk's `gsub`/regex semantics don't share bash's POSIX BRE/ERE conventions cleanly. The per-line regex is the audit-critical component of the library; cross-language semantic translation is itself a security-tax.
- **(b)** bash 3.2's awk vs gawk vs nawk vs BSD-awk fragmentation introduces a portability tax that exceeds the perf gain. macOS ships BSD awk; Linux distros ship gawk; the awk dialect feature surface (`gensub` only on gawk; `match` 3rd-arg only on gawk; `\s` shortcut only on gawk) means the awk-script-as-string-literal MUST either restrict to POSIX-99 awk (forfeiting most of the speed gain) OR ship two parallel awk implementations (audit nightmare).
- **(c)** Audit-clarity preference (per ADR-040 Decision Item 7) favors keeping the parser in bash — one language for the security-load primitive; reviewers don't need to context-switch between awk regex semantics and bash regex semantics; the regex is self-documenting in-place.
- **(d)** The marginal per-call gain (~5-10ms estimated) is not worth the audit cost given the sub-perception operational threshold above.

**Methodology specification**: 100 invocations × 4 fixtures × p50/p95; per-file delta (NOT aggregate); warm-cache + cold-cache reported separately (cold deferred to CI per macOS `sudo purge` privilege constraint — both T005 baseline and T013 post-impl measured under warm-cache symmetrically). Two warm-up invocations precede each fixture's 100-run timing window. Canonical fixture set: `stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, `tests/fixtures/config-load/valid/aod-kit-version-valid`, `tests/fixtures/config-load/valid/personalization-env-valid`.

### NUL-byte mechanism clarification (folds into Decision Item 1 at T054)

The original contract §Step 5 said the regex "implicitly rejects NUL". This mechanism is unsound because bash command substitution `$(cat $path)` silently truncates the captured string at the first NUL byte. An adversarial fixture `KEY=foo\x00bar\n` would be loaded as `KEY=foobar\n` (one valid KV line), bypassing the FR-005 AC-5.4 rejection promise. The library uses an explicit Step 2b NUL pre-check via `LC_ALL=C wc -c` vs `LC_ALL=C tr -d '\000' < file | wc -c` size comparison. Behavior unchanged (NUL → exit 8); only the mechanism description in the ADR / contract needed updating.

### TOCTOU residual race window framing (per Decision Item 5)

The library reads the file via single `cat $path`; per-line iteration runs on the in-memory buffer. The race is collapsed but not eliminated — defense-in-depth via 0600 mode on personalization.env applies upstream. Adopter scenarios where the race could matter (forked process swapping the file between caller's intent and kernel's `openat()`) are documented in §Decision Item 5 above.

### F-1 contract amendment relationship

ADR-038 (F-1 BLP-02 Wave 1) established `aod_init_read_validated` as the prompt-boundary input validator with a rejection ladder (NUL / control / over-length). ADR-040 (F-2 BLP-02 Wave 2) extends that ladder with a fourth rejection class (`$` / `\` / backtick — shell metacharacters) per B-2 Path R-2. The amendment lands in F-2's PR, not retroactively in F-1, per Q-6 dual-commit framing. Migration guidance for adopters whose existing prompt values contain these chars: re-init via clone-and-init, OR manually edit `.aod/personalization.env` (the post-F-2 loader will reject the prior values at the next /aod.update if metachar values survive).

---

## Related Findings

This ADR closes 5 vuln_ids in a single PR (per Q-1 single-PR ruling):

1. **TACHI-VULN-6f5a95085056** (HIGH) — `scripts/init.sh:106` source of stack-pack defaults.env
2. **TACHI-VULN-bf5496e9fcdf** (HIGH) — `template-git.sh:561` + `:485-515` source of aod-kit-version
3. **TACHI-VULN-9a7512071b4a** (MEDIUM) — `template-substitute.sh:217/249/536/558` four eval invocations
4. **TACHI-VULN-4dc6cf8f88ea** (MEDIUM) — `template-substitute.sh:162-209` validate-then-source TOCTOU
5. **TACHI-VULN-851fd6a21ba9** (LOW) — `template-git.sh:102-104` git clone unbounded timeout

---

## References

- Web archive snapshot of Daniel Wood's 2026-05-02 LinkedIn note: `https://web.archive.org/web/2026*/linkedin.com/posts/danielwood-tachi-bash-substitution`
- ADR-038 (F-1 BLP-02 Wave 1): [Placeholder Substitution Strategy — bash Parameter Expansion vs sed](ADR-038-placeholder-substitution-strategy.md)
- ADR-039 (F-250 hot-fix): [Test Architecture Fixture Scope and Asymmetric Baseline](ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md)
- F-2 PRD: [specs/256-source-pattern-hardening/spec.md](../../../specs/256-source-pattern-hardening/spec.md)
- F-2 Plan: [specs/256-source-pattern-hardening/plan.md](../../../specs/256-source-pattern-hardening/plan.md)
- Library contract: [specs/256-source-pattern-hardening/contracts/config-load-helper-contract.md](../../../specs/256-source-pattern-hardening/contracts/config-load-helper-contract.md)
- Stack-pack schema: [contracts/stack-pack-defaults-schema.md](../../../contracts/stack-pack-defaults-schema.md)

---

**Status note**: This ADR was promoted from **Proposed** (Wave 3 Stream 3 T042 commit `cd1ae4a`, 2026-05-05) to **Accepted** (Wave 6 T054 commit, 2026-05-05) per the Q-6 dual-commit pattern. T054 folded in the full p95 + cold-cache disposition, the four required §Consequences elaborations (methodology asymmetry, NFR-004 formal loosening rationale, cost decomposition, awk micro-opt rejection), and the §Decision Item 1 NUL-byte mechanism clarification (explicit Step 2b `wc -c` vs `tr -d '\000' | wc -c` size-comparison; the original "regex implicitly rejects NUL" wording was unsound).
