# Research Summary: Restore F-248/F-256 Substitution Hardening (#338)

**Date**: 2026-06-29 · **Phase**: BLP-06 Wave 2, F-2 · **Feeds**: spec.md
**Sources**: PRD #338, `.aod/results/architect.md`, `.aod/results/team-lead.md`,
`specs/338-restore-substitution-hardening/feasibility-check.md`, direct tree forensics
(`5b64f68..HEAD`), Explore-agent codebase sweep.

> The research phase for #338 is **verification-focused**, not discovery: the restore source
> is known-good v4.44.0 code (`5b64f68`) and the design is already settled (ADR-038, ADR-040).
> The one genuinely-open question was **OQ-3** (the `defaults.env` gate state) — now resolved
> empirically below.

## Knowledge Base Findings

- **The clobber pattern is recurring** (project memory `aod-update-clobbers-tachi`): the same
  F-248/F-256 hardening surface was clobbered by `/aod.update` once before (resolved `07236cf`,
  2026-06-15) and **regressed again** 2026-06-28. The manifest `owned|`-fix tried at `07236cf`
  did **not** hold → detection (the push gate, FR-006) is the load-bearing control, not the
  manifest classification.
- **Lesson (insurance discipline)**: a `/aod.update` checkpoint + `--dry-run` + `git diff --stat`
  of the at-risk set is now mandatory operator process — referenced by FR-008, not built here.
- **Originating features**: F-248 (substitution surface hardening, ADR-038), F-256 (source-pattern
  hardening, ADR-040). #338 restores them; it does **not** re-design them.

## Codebase Analysis (verified `5b64f68..HEAD`)

**Current reverted state (HEAD) of the 3 in-scope files — confirmed clean generic-revert:**

| File | Hardening at `5b64f68` | At HEAD | Δ |
|------|------------------------|---------|---|
| `.aod/scripts/bash/template-substitute.sh` | F-248 `patsub_replacement` shim (5 hits) + F-256 Site D `aod_template_load_kv_file` delegation | shim **absent** (0 hits); reverted to inline `source` (TACHI-VULN-4dc6cf8f88ea pattern) | ~184Δ |
| `scripts/init.sh` | F-248 param-expansion + input-validation **and** F-256 Site A `aod_template_load_kv_file ... STACK_PACK_ALLOWED_KEYS` loader | reverted to generic `sed` substitution + plain `source defaults.env` (TACHI-VULN-6f5a95085056 pattern) | ~351Δ (−240 lines) |
| `.aod/scripts/bash/template-git.sh` | F-256 `AOD_FETCH_TIMEOUT` bounded-fetch watchdog (3 hits) | watchdog **absent** (0 hits); bare `git clone` | ~114Δ |

- **No surviving tachi/F-248/F-256 markers in the 3 HEAD files** (Architect HIGH-1, re-verified):
  the files are a *complete* generic-revert → restore = `git checkout 5b64f68 -- <3 files>` +
  confirmation diff, **not** a 3-way merge. The genuine Sprint→Loop refresh lives in out-of-scope
  docs; the `defaults.env` entanglement is a whitelist-schema concern (below).
- **Note — init.sh carries BOTH F-248 and F-256 Site A**: the PRD frames init.sh as "F-248
  substitution hardening," but the revert also dropped the **F-256 Site A** `aod_template_load_kv_file`
  loader. Restoring init.sh from `5b64f68` restores both — and re-activates the strict whitelist
  loader, which is what surfaces OQ-3.

**Supporting library (NOT reverted, do not touch):**
- `.aod/scripts/bash/template-config-load.sh` — **unchanged `5b64f68..HEAD`** (empty diff). Provides
  `aod_template_load_kv_file`. Present and intact at HEAD; the restored init.sh sources it.

**Test suite** (`tests/scripts/`, all on the gate `paths`):
- `test_substitute_shim_canary.py` — F-248 `AT&T → AT&T` canary (shim-sensitive; red on bash 5.x without shim).
- `test_template_substitute_unit.py` — F-248 cases 1–3 (`&`, `|`, `\1\2`).
- `test_init_sh_substitution.py` / `test_init_sh_adversarial.py` — F-248 init.sh path + input validation.
- `test_template_git_clone_timeout.py` — F-256 `AOD_FETCH_TIMEOUT` watchdog.
- `test_init_sh_defaults_env.py` — **F-256 Site A** (the OQ-3 test; see below).
- `test_personalized_tree_bytes_match_baseline` (in `test_init_sh_substitution.py`) — `@pytest.mark.xfail(strict=False)` with #329 reason (FR-007 groundwork ✓).

**Groundwork (`99507b2`, branch tip) — verified DONE, do not re-task:**
- FR-006: `tachi-pytest.yml` has `push: branches:[main] paths: *hardening_paths` (single YAML anchor shared with `pull_request`).
- FR-007: baseline byte-identity test xfail'd.

## OQ-3 — `defaults.env` Gate State: RESOLVED **RED** (the load-bearing finding)

**Question**: does the gated `test_init_sh_defaults_env.py` pass after the restore, with the F-2
`TECH_STACK` key absent from `defaults.env`?

**Empirical answer — NO, it would FAIL.** The library `aod_template_load_kv_file`
(`template-config-load.sh`, unchanged at HEAD) enforces `STACK_PACK_ALLOWED_KEYS` as an **exact set**:

- **In-pass whitelist check** (L290-304): any key *not* in the allowed set → `return 8` ("disallowed key").
- **Post-pass completeness check** (L314-330): any allowed key *missing* → `return 8` ("required key missing").

The restored init.sh (`5b64f68:scripts/init.sh:139`) calls it with the canonical 5-key set:
```bash
STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
```

**Current `stacks/*/defaults.env` key sets (HEAD):**

| Pack (Case-1 tested?) | Keys present | vs canonical 5 | Restored-loader result |
|---|---|---|---|
| `nextjs-supabase` ✅ | 4 (no `TECH_STACK`) | missing `TECH_STACK` | **exit 8** (completeness) |
| `fastapi-react` ✅ | 4 (no `TECH_STACK`) | missing `TECH_STACK` | **exit 8** (completeness) |
| `fastapi-react-local` | 4 (no `TECH_STACK`) | missing `TECH_STACK` | exit 8 |
| `swiftui-cloudkit` | 4 (no `TECH_STACK`) | missing `TECH_STACK` | exit 8 |
| `knowledge-system` | 4 canonical + `ORCHESTRATION_TARGET` | missing `TECH_STACK` **and** extra disallowed key | **exit 8** (both checks) |

`test_init_sh_defaults_env.py` Case 1 runs `nextjs-supabase` + `fastapi-react` through init.sh and
asserts `returncode == 0`. Both exit 8 under the restored loader → **the gated suite cannot go green
(FR-005/SC-001) until `TECH_STACK` is restored.**

**Restore target (`5b64f68`) values** — exactly the canonical 5 keys per pack:
`nextjs` / `fastapi-react` / `fastapi-react-local` / `swiftui-cloudkit` / `knowledge-system`;
`knowledge-system@5b64f68` had **no** `ORCHESTRATION_TARGET`.

**Resolution (PRD OQ-3 option a, pre-authorized "pull TECH_STACK in-scope, 1 line/file")**: the
minimal canonical-5-key restoration is pulled **IN-scope** as a new requirement — restore
`TECH_STACK="<pack>"` to all 5 shipped packs and remove the disallowed `ORCHESTRATION_TARGET` from
`knowledge-system`. Both halves are needed: the missing key fails the completeness check; the extra
key fails the whitelist check (and `knowledge-system` is tachi's own active stack). This amends the
PRD FR-008 fence (which had tentatively scoped `TECH_STACK` OUT pending OQ-3).

## Architecture Constraints

- **bash 3.2.57+** (F-248 NFR-001): no `mapfile`, no associative arrays, no `${var,,}`. macOS matrix
  leg is the hard gate. Restored code is known-good from v4.44.0 (already passed this leg).
- **ADR-038** (`docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`): bash
  parameter-expansion over `sed` to avoid `&`/`|`/`\1` metacharacter corruption.
- **ADR-040** (`docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md`): `source`/`eval`
  → `aod_template_load_kv_file` KV parser (the whitelist loader at the heart of OQ-3).
- **Do NOT revert the manifest** (Architect MEDIUM-2 / OQ-1): `.aod/template-manifest.txt` is *more*
  hardened at HEAD (`user|init.sh`, `merge|` libs) than at `5b64f68` (`owned|`). Reverting regresses it.

## Recommendations for Spec

- Restore exactly the **3 file bodies** from `5b64f68` (FR-001..004) — clean checkout + confirmation diff.
- **Add a new FR** for the canonical-5-key `defaults.env` restoration (OQ-3 resolution) — restore
  `TECH_STACK` to all 5 packs + remove `ORCHESTRATION_TARGET` from `knowledge-system`. Gate-green depends on it.
- **Soften** the parity claim: byte-parity is NOT asserted (baseline test xfail'd, #329); behavioral
  parity (canary + adversarial + clone-timeout + config-load) + the FR-004 confirmation diff is the oracle.
  Add a **manual byte spot-check** (W-1) of the 3 restored bodies vs `5b64f68`.
- **Define SC-004's baseline** as the *restore commit's* diff (branch-vs-`main`-pre-restore), NOT
  branch-vs-`5b64f68` (the branch sits atop a ~30-file update delta).
- **Name `scripts/update.sh`** as explicitly-untouched (not a hardening surface) so SC-004 stays auditable.
- **Carry S-1**: do not push the branch / open the PR until the restore is green locally (the FR-006
  `push:[main]` gate would otherwise redden `main`). Encode as the final deliver-gate task.
- Do **not** re-task the FR-006/FR-007 groundwork (`99507b2`) — list as completed dependencies.
