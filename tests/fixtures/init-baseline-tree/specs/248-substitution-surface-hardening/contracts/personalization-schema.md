# Contract: Personalization Schema (.aod/personalization.env)

**Schema location**: `.aod/personalization.env` (per-adopter; local-only by default per F-248 T028)
**Producers**: `scripts/init.sh` (one-time at adopter init), `aod_template_init_personalization` helper
**Consumers**: `aod_template_load_personalization_env`, `aod_template_substitute_placeholders`, `/aod.update` re-substitution flow
**Schema version**: 1 (F-129 stable; F-248 documents Substitution Strategy decision but does not change schema)

## Fields (Canonical 12 Placeholder Set)

The canonical placeholder set is locked at 12 keys — adding a new placeholder requires updating BOTH `AOD_CANONICAL_PLACEHOLDERS` in `.aod/scripts/bash/template-substitute.sh` AND this schema (lockstep per ADR-038 §Decision M-2 commitment).

| # | Key | Source | Init-time | /aod.update behavior |
|---|-----|--------|-----------|----------------------|
| 1 | `PROJECT_NAME` | `read -p` (validated, max 100) | required | re-substituted from snapshot |
| 2 | `PROJECT_DESCRIPTION` | `read -p` (validated, max 300) | required | re-substituted from snapshot |
| 3 | `GITHUB_ORG` | `read -p` (validated, max 39) | required | re-substituted from snapshot |
| 4 | `GITHUB_REPO` | `read -p` (validated, max 100; defaults to `$PROJECT_NAME` if empty) | required | re-substituted from snapshot |
| 5 | `AI_AGENT` | menu choice (1=claude, 2=cursor, 3=copilot) | required | re-substituted from snapshot |
| 6 | `TECH_STACK` | stack pack discovery OR `read -p` | required | re-substituted from snapshot |
| 7 | `TECH_STACK_DATABASE` | stack pack defaults OR `read -p` | required (defaults "Not yet defined") | re-substituted from snapshot |
| 8 | `TECH_STACK_VECTOR` | stack pack defaults OR fallback | required (defaults "Not yet defined") | re-substituted from snapshot |
| 9 | `TECH_STACK_AUTH` | stack pack defaults OR fallback | required (defaults "Not yet defined") | re-substituted from snapshot |
| 10 | `RATIFICATION_DATE` | `date +%Y-%m-%d` (init-time snapshot) | required (init-only) | preserved verbatim — `/aod.update` MUST NOT recompute |
| 11 | `CURRENT_DATE` | `date +%Y-%m-%d` (init-time snapshot) | required (init-only) | preserved verbatim — `/aod.update` MUST NOT recompute |
| 12 | `CLOUD_PROVIDER` | stack pack defaults OR `read -p` | required (defaults "Not yet defined") | re-substituted from snapshot |

## Value Constraints

Loader (`aod_template_load_personalization_env`) and writer (`aod_template_init_personalization`) enforce these constraints. Violations exit non-zero.

| Rule | Loader behavior | Writer behavior |
|------|-----------------|-----------------|
| Every canonical key MUST be set | exit 8 listing missing keys | exit 8 listing missing keys |
| Values MAY contain `&`, `\\`, `\|`, `/`, `$`, regex metachars, quotes | accepted; passed through bash param expansion verbatim | quoted with `\\` / `\$` / `\"` / `` \` `` escapes for source-ability |
| Values MUST NOT contain literal newline | exit 8 | exit 8 |
| Values MUST NOT contain NUL bytes | bash truncates at C-string boundary; defense-in-depth via writer `case` check | exit 8 |

## Substitution Strategy (F-248 Decision Record)

**Decision**: Substitution uses bash parameter expansion `${content//\{\{KEY\}\}/value}` instead of sed `s|{{KEY}}|value|g`.

**Rationale** (FR-001 + FR-005 + Wave 2 Test-2 cases 1-13):

1. **Metacharacter literal-preservation**: bash parameter expansion treats both pattern and replacement as LITERAL strings — no regex metachar interpretation. Adversarial values like `AT&T` (ampersand), `Cats & Dogs`, `\1\2 backref`, regex metachars `.*+?^$()`, pipes `|`, slashes `/` all survive verbatim. sed interprets `&` as match-substitution and `\1` as backreference, corrupting these values.

2. **Single-branch cross-platform**: bash parameter expansion behavior is identical on macOS bash 3.2 and Linux bash 5.x. The original sed approach required `OSTYPE` branching (`sed -i ''` on macOS, `sed -i` on GNU). One branch reduces complexity.

3. **Closed placeholder contract** (FR-004): post-substitution residual `\{\{[A-Z_]+\}\}` patterns indicate either an upstream-introduced placeholder NOT in the canonical 12 (unknown-placeholder halt) or a substitution bug. The residual scan is scoped to PERSONALIZED-category files per `.aod/template-manifest.txt` (the categories that re-substitute on `/aod.update`); non-personalized files (stack scaffolds, brand archetypes, deployment-time docs, agent-doc examples) legitimately contain non-canonical `{{KEY}}` tokens used by parallel templating systems.

**Trade-off** (NFR-004 PM disposition pending at `/aod.deliver`):

bash parameter expansion is structurally slower than sed-batched substitution at init time. The substitute helper is called once per file (~3260 text files post-binary-skip), each invocation forking ~6-8 subprocesses. Old sed used `find ... -exec sed -i '' -e ... +` argv-batching across ~1000 files per sed invocation. T021 measured +658% delta vs T008 sed-baseline (50.7s vs 6.7s).

The trade-off favors correctness over speed:
- init.sh runs ONCE per adopter project (one-time cost)
- The metachar corruption defects sed introduces are functional, not cosmetic
- 50s init vs 7s init adds ~43s to first-run experience; not a recurring cost

PM judgment input at `/aod.deliver`: accept the regression with documented rationale in ADR-038 §Consequences, OR re-scope to defer perf optimization to BLP-02 Wave 2.

## Posture: Local-Only by Default (F-248 T028)

`.aod/personalization.env` ships gitignored by default per `.gitignore:222`:

```
.aod/personalization.env
```

**Rationale** (FR-006):

1. **Multi-tenant safety**: a fork of an adopter repo MUST NOT inherit the original adopter's `PROJECT_NAME`, `GITHUB_ORG`, etc. Forking → re-init re-personalizes; committed `.env` would leak personalization across forks.

2. **Defense layer 1** (multi-hop chain layer 2): even if a misconfigured CI re-runs init.sh on a personalized adopter project, the snapshot already exists → re-init pre-flight check halts (FR-003); the snapshot's gitignored status prevents accidental commit of the (potentially stale) .env.

3. **Bootstrap-safe**: a fresh clone has no `.aod/personalization.env`. Running `init.sh` writes it. The version pin (`.aod/aod-kit-version`) IS committed (template's anchor for `/aod.update`); only the per-adopter snapshot is local-only.

### Opt-In Path: Committing personalization.env (Adopter Choice)

Adopters who explicitly want personalization version-controlled (e.g., for bisect-friendly init reproducibility on shared dev environments) can override the default:

```bash
# 1. Remove from .gitignore (delete or comment line 222)
# 2. Force-add the file
git add -f .aod/personalization.env
git commit -m "chore: opt-in commit personalization.env for env reproducibility"
```

**Migration command** (for adopters previously committing the file by accident, who want to re-establish local-only default):

```bash
git rm --cached .aod/personalization.env
git commit -m "chore: gitignore .aod/personalization.env per F-248 default posture"
```

This stops tracking the file without deleting the local copy. The next `/aod.update` re-substitutes from the local snapshot as usual.

## Read Protocol

Order of operations consumer libraries follow:

1. `source .aod/scripts/bash/template-substitute.sh` (idempotent guard)
2. `aod_template_load_personalization_env .aod/personalization.env` — sets `AOD_PERSONALIZATION_<KEY>` env vars; exits 8 on missing/invalid
3. For each file requiring substitution: `aod_template_substitute_placeholders <src> <dest>` (in-place when src=dest)
4. (Optional, for personalized-category files only) `aod_template_assert_no_residual <file>` — halts on orphan canonical-12 placeholders

`/aod.update` follows steps 1-4 for each personalized file in `.aod/template-manifest.txt`. `init.sh` follows step 1 + step 2 once + steps 3-4 in loops over the canonical-tree (step 3 whole-tree, step 4 personalized-only per F-248 T020 FR-004 scope).

## Stability Contract

- **Schema version 1 stable**: any change to the canonical 12 keys requires a major schema bump (e.g., `schema_version: 2`) and explicit ADR with migration plan.
- **Field renames forbidden**: existing keys are immutable identifiers; new placeholders are append-only.
- **Default values may evolve**: "Not yet defined" sentinel may change wording in future releases without schema bump (display-only).
- **Substitution strategy is fixed at bash parameter expansion** (F-248 ADR-038); reverting to sed requires a full ADR with metachar-corruption test plan.
