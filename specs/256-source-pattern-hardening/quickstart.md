# Quickstart: F-2 Source-Pattern Hardening (Maintainer-Facing)

**Feature**: 256
**Date**: 2026-05-04
**Audience**: tachi maintainers + adopters wanting to understand the post-F-2 config-load flow

---

## Post-F-2 Config-Load Flow (Walk-Through)

### 1. Fresh checkout

```bash
git clone https://github.com/davidmatousek/tachi my-project
cd my-project
```

### 2. Run init

```bash
./scripts/init.sh
```

The script sources three bash libraries at the top:

```bash
source .aod/scripts/bash/template-substitute.sh        # F-1 helper
source .aod/scripts/bash/init-input.sh                 # F-1 helper, AMENDED in F-2
source .aod/scripts/bash/template-config-load.sh       # F-2 NEW library
```

### 3. Answer prompts (with F-1 amendment per F-2 contract)

```
Project Name: my-project
Project Description: An AI-powered widget factory
GitHub Organization: my-org
GitHub Repository: my-project
```

**F-1 amendment ripple**: the prompt validator now ALSO rejects `$`, `\`, backtick (alongside the existing newline / NUL / control / over-length checks). If you paste:

```
Project Name: my$project
```

The prompt rejects with `[init] Input rejected: metachar ($, \, backtick) not allowed; please re-enter.` and re-prompts (up to 3 times).

This change unlocks the writer escape pass removal at `template-substitute.sh:566-571` — values are guaranteed metachar-free at the prompt boundary, so the writer round-trip needs no escape pass.

**CHANGELOG migration guidance**: if your previous `PROJECT_NAME` contained `$`, `\`, or backtick, choose a metachar-free name. (This is extremely unlikely in practice — these metachars in a project name are almost always indicators of accidental paste.)

### 4. Pick a stack pack

```
Available stack packs:
  1. nextjs-supabase
  2. fastapi-react
Select: 1
```

### 5. F-2 in action — Site A refactor at `init.sh:106`

The script invokes:

```bash
STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
aod_template_load_kv_file "stacks/nextjs-supabase/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS
```

The loader:
- Reads `stacks/nextjs-supabase/defaults.env` once into a buffer (`cat $path`).
- Iterates per line: skips blank/comment, validates against the strict regex, checks each KEY against the whitelist.
- After all lines parsed, verifies all whitelisted keys are present.
- Assigns `STACK_TECH_STACK=nextjs`, `STACK_TECH_STACK_DATABASE=supabase`, etc. via `printf -v`.

If `defaults.env` contains a malicious line (`CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"`), the loader exits **8** with `[aod] ERROR: disallowed key 'CUSTOM_HOOK' in stacks/nextjs-supabase/defaults.env (line N); allowed: TECH_STACK ...`. The `touch` is **never executed**.

### 6. Subsequent flow

`.aod/personalization.env` is written; `aod_template_load_personalization_env` (post-F-2 collapsed body) calls `aod_template_load_kv_file "$path" "AOD_PERSONALIZATION_" AOD_CANONICAL_PLACEHOLDERS` to load the personalization snapshot via the canonical pattern.

The substitution loop runs (F-1's `aod_template_substitute_placeholders`), then `aod_template_assert_no_residual` (F-1's residual scan), then constitution copy, then self-delete.

### 7. Weekly `/aod.update` (post-F-2)

```bash
/aod.update
```

The flow:

1. `aod_template_fetch_upstream` invokes `git clone` with a 60-second timeout (per F-2 FR-006). The watchdog subshell sleeps 60s, then `kill -TERM`s the clone PID if still alive. SIGINT trap (per L-1) cleans up the watchdog if you Ctrl+C the outer script.
2. **Override the timeout** if needed: `AOD_FETCH_TIMEOUT=600 /aod.update` (10 minutes). Setting `AOD_FETCH_TIMEOUT=0` is **rejected** (Q-3 footgun) — exit 1 with `[aod] ERROR: AOD_FETCH_TIMEOUT must be a positive integer (got: 0)`.
3. `aod_template_read_version_file` parses `.aod/aod-kit-version` via the canonical pattern in **lowercase mode** (`<key_case>=lower` per Q-2.5):
   ```bash
   aod_template_load_kv_file "$path" "" "" lower
   ```
   Existing per-field regex validators at `template-git.sh:568+` run AFTER the load — unchanged.
4. `aod_template_write_version_file`'s belt-and-braces inner round-trip block at `:485-515` (the `:501` source) also routes through `aod_template_load_kv_file` (lowercase mode); existing post-load missing-field detection runs unchanged.

### 8. Adopter migration check

If your existing project was set up before F-2 and your `PROJECT_NAME` / `PROJECT_DESCRIPTION` contains `$`, `\`, or backtick (in the legacy `.aod/personalization.env`), the F-2 amendment of the F-1 prompt validator means a **re-init** would now reject those values at prompt time. Migration: choose a metachar-free name on next re-init.

---

## What F-2 Did NOT Change

- **No `finding.yaml` schema change** (NFR-005, ninth feature in a row).
- **No new agent files** in `.claude/agents/`.
- **No orchestrator changes**.
- **No new runtime dependencies** (NFR-002, empty diff on `pyproject.toml` / `requirements*.txt` / `package.json`).
- **No new workflow files** — the existing pytest CI matrix on macos-latest + ubuntu-latest runs the new tests.
- **`.aod/personalization.env` gitignore posture** — F-2 inherits F-1's gitignore-default; no F-2 change.

---

## What F-2 Added

| Artifact | Path | Purpose |
|---|---|---|
| New library | `.aod/scripts/bash/template-config-load.sh` | Canonical config-load primitive (`aod_template_load_kv_file`) |
| New contract | `contracts/stack-pack-defaults-schema.md` | Canonical key set for `stacks/<pack>/defaults.env` |
| New ADR | `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` | Public architectural record (dual-commit Proposed → Accepted) |
| New tests | 5 files in `tests/scripts/test_template_*.py` + `test_init_sh_defaults_env.py` | Test-1 through Test-5 from PRD §Regression Protection Plan |
| New fixtures | `tests/fixtures/config-load/{valid,adversarial}/` | Adversarial corpus for Test-2 |
| New env var | `AOD_FETCH_TIMEOUT` | Override default 60-second clone timeout |
| New CHANGELOG entry | `CHANGELOG.md` v4.x | Documents new library + 4 refactored sites + clone timeout + F-1 contract amendment |

---

## What F-2 Modified

| File | Modification |
|---|---|
| `scripts/init.sh` | Line 106: `source defaults.env` → `aod_template_load_kv_file` call with whitelist; library source added at top alongside `template-substitute.sh` + `init-input.sh` sources |
| `.aod/scripts/bash/template-git.sh` | Lines 561 + 501 (in `:485-515`): `source $path` / `source $tmp_path` → `aod_template_load_kv_file` calls (lowercase mode); lines 102-104: `git clone` wrapped with watchdog timeout + SIGINT trap |
| `.aod/scripts/bash/template-substitute.sh` | Lines 217, 249, 536, 558: `eval` invocations → `${!var}` indirect / `printf -v`; lines 162-209: `aod_template_load_personalization_env` body collapsed to library delegation; lines 566-571: writer escape pass REMOVED |
| `.aod/scripts/bash/init-input.sh` | F-1's `aod_init_read_validated` extended to additionally reject `$`, `\`, backtick at prompt boundary (per B-2 Path R-2) |
| `tests/scripts/conftest.py` | Session-scoped `hanging_upstream` pytest fixture added (per F-250 ADR-039 fixture-scope canon) |
| `CHANGELOG.md` | v4.x entry for F-2 changes + F-1 contract amendment migration guidance |
| `.security/vulnerabilities.jsonl` | 5 `REMEDIATED` events appended post-merge with squash-merge SHA |

---

## Verification (Post-Merge)

After F-2 squash-merges to `main`, run:

```bash
# Verify the library exists
ls -l .aod/scripts/bash/template-config-load.sh

# Verify zero eval in template-substitute.sh
grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh
# Expected: 0

# Verify zero source-of-config in init.sh
grep -n 'source.*defaults\.env' scripts/init.sh
# Expected: zero matches

# Verify ADR-040 exists with Status: Accepted
grep '^**Status**: Accepted' docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md
# Expected: matches

# Verify 5 REMEDIATED events
grep -c '"event_type":"REMEDIATED"' .security/vulnerabilities.jsonl  # Tally before vs after F-2
# Expected: increase by 5

# Run the F-2 test suite
pytest tests/scripts/test_template_config_load_unit.py -v
pytest tests/scripts/test_template_config_load_integration.py -v
pytest tests/scripts/test_template_git_clone_timeout.py -v
pytest tests/scripts/test_init_sh_defaults_env.py -v
pytest tests/scripts/test_template_substitute_lint_no_eval.py -v
# Expected: all pass on macOS bash 3.2.57 + ubuntu-latest bash 5.x
```

---

## Troubleshooting

### Symptom: `init.sh` exits with `[aod] ERROR: disallowed key 'X' in stacks/...`

Cause: your stack pack contains a key not in the canonical 5 (`TECH_STACK`, `TECH_STACK_DATABASE`, `TECH_STACK_VECTOR`, `TECH_STACK_AUTH`, `CLOUD_PROVIDER`).

Fix: remove the key from your pack OR propose the addition as a lockstep contract update (per `contracts/stack-pack-defaults-schema.md` lockstep rule).

### Symptom: `init.sh` exits with `[aod] ERROR: malformed line N in stacks/...`

Cause: a value contains shell metacharacters (`$`, `\`, backtick, `;`, `|`, etc.) outside of a quoted string.

Fix: quote the value (single-quote preserves literal characters; double-quote with no metachars; or use the allowlisted unquoted charset).

### Symptom: `/aod.update` hangs

Cause: upstream remote is hanging (DNS resolves but TCP doesn't, or HTTPS handshake stalls).

Fix: F-2's clone timeout terminates the clone after 60s by default. Override with `AOD_FETCH_TIMEOUT=N` (positive integer). The post-F-2 behavior: exit 9 + cleaned-up partial checkout + clear timeout error message.

### Symptom: `aod_template_read_version_file` returns exit 8

Cause: `.aod/aod-kit-version` is malformed (corrupted partial fetch, disk corruption, supply-chain compromise of the upstream tag).

Fix: re-run `/aod.update` to re-fetch from upstream. The exit-8 behavior closes TACHI-VULN-bf5496e9fcdf — ensures malformed content is rejected BEFORE any bash interpretation.

---

## Cross-References

- Spec: [spec.md](spec.md)
- Plan: [plan.md](plan.md)
- Loader contract: [contracts/config-load-helper-contract.md](contracts/config-load-helper-contract.md)
- Stack-pack schema: [contracts/stack-pack-defaults-schema.md](contracts/stack-pack-defaults-schema.md)
- ADR-040 (post-Stream-3 commit): TBD `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md`
- F-1 walkthrough (analogous structure): [specs/248-substitution-surface-hardening/quickstart.md](../248-substitution-surface-hardening/quickstart.md)
