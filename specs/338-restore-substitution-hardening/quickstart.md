# Quickstart: Verify the F-248/F-256 Hardening Restore (#338)

**Audience**: builder + deliverer. This is the acceptance recipe for the restore. Run from repo root on the
`338-restore-substitution-hardening` branch.

> **S-1 (load-bearing)**: do NOT `git push` the branch or open/ready the PR until step 4 is green locally.
> The FR-006 `push:[main]` gate would otherwise redden `main` on the branch's own behalf.

## 1. Restore the 3 file bodies (clean generic-revert — FR-001..004)

```bash
git checkout 5b64f68 -- \
  scripts/init.sh \
  .aod/scripts/bash/template-substitute.sh \
  .aod/scripts/bash/template-git.sh
```

Confirm the hardening markers are back (expect non-zero counts):
```bash
grep -c patsub_replacement .aod/scripts/bash/template-substitute.sh   # expect 5
grep -c AOD_FETCH_TIMEOUT  .aod/scripts/bash/template-git.sh           # expect 3
grep -c STACK_PACK_ALLOWED_KEYS scripts/init.sh                       # expect >=1 (F-256 Site A loader)
```

## 2. Restore the canonical defaults.env key surface (FR-009 — surgical, NOT whole-file)

For each shipped pack, ensure the key set EXACTLY equals the canonical 5
(`TECH_STACK, TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH, CLOUD_PROVIDER`):

- Add `TECH_STACK="<pack>"` to all 5 (values = `5b64f68`): `nextjs` / `fastapi-react` /
  `fastapi-react-local` / `swiftui-cloudkit` / `knowledge-system`.
- Remove `ORCHESTRATION_TARGET` from `stacks/knowledge-system/defaults.env` (disallowed by the whitelist).

Verify each pack's key set:
```bash
for p in nextjs-supabase fastapi-react fastapi-react-local swiftui-cloudkit knowledge-system; do
  echo "== $p =="; grep -oE '^[A-Z_]+=' stacks/$p/defaults.env | tr -d '=' | sort
done
# Each must list exactly: CLOUD_PROVIDER TECH_STACK TECH_STACK_AUTH TECH_STACK_DATABASE TECH_STACK_VECTOR
```

## 3. Byte spot-check vs 5b64f68 (W-1 — closes the xfail'd byte-baseline gap, FR-005)

```bash
for f in scripts/init.sh .aod/scripts/bash/template-substitute.sh .aod/scripts/bash/template-git.sh; do
  git diff 5b64f68 -- "$f" >/dev/null && echo "OK $f" || echo "DELTA $f"
done
# Expect: the 3 bodies are byte-identical to 5b64f68 (clean checkout). Any delta must be the
# generic->hardened direction only; investigate anything else before proceeding.
```

## 4. Run the F-248/F-256 gated suite — both legs (FR-005 / SC-001 / SC-006)

```bash
python -m pip install 'pytest>=8' 'pytest-timeout>=2' 'pyyaml>=6'
python -m pytest tests/scripts/ -v --timeout=1080
```

**Green criteria**:
- `test_substitute_shim_canary.py` passes (`AT&T → AT&T`, never `AT{{PROJECT_NAME}}T`) — SC-002.
- `test_init_sh_defaults_env.py` passes (5/5 packs exit 0 under the restored loader) — SC-006.
- `test_template_git_clone_timeout.py` passes (`AOD_FETCH_TIMEOUT` watchdog) — FR-003.
- `test_init_sh_substitution.py` / `test_init_sh_adversarial.py` pass.
- `test_personalized_tree_bytes_match_baseline` is **xfail** (FR-007, #329) — expected, not a failure.
- Locally this runs bash 3.2 (macOS) or 5.x (Linux); CI runs **both** matrix legs — both must be green.

## 5. Deliver gate (S-1) + release verification

Only after steps 1-4 are green:
- Merge through devops (per deployment policy). Conventional-commit PR title: `fix(338): ...` or
  `feat(338): ...` so release-please opens a release PR.
- SC-004 audit: the restore commit's diff touches only the 8 in-scope paths; every other branch delta is
  named in FR-008.
- Confirm release-please opened a PR within ~30s of the squash-merge; push an empty `fix(338): … — release
  marker` if it didn't.

## Do-NOT list (FR-008 scope fence)

- Do NOT revert `.aod/template-manifest.txt` (more hardened at HEAD than `5b64f68`).
- Do NOT touch `scripts/update.sh` (not a hardening surface).
- Do NOT reconcile the docs Sprint→Loop refresh or fix the #329 baseline drift (separate follow-ups).
- Do NOT re-implement FR-006/FR-007 (landed in `99507b2`).
