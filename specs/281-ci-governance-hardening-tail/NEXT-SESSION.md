# NEXT-SESSION — Feature 281: CI & Governance Hardening Tail (F-4/F-5 follow-ups)

**Branch**: `281-ci-governance-hardening-tail` · **Draft PR**: [#347](https://github.com/davidmatousek/tachi/pull/347) (`feat(281):` title, correct)
**Status**: ✅ **BUILD COMPLETE — 18/18 tasks (100%). All 4 waves done. Steps 5–9 (Final Validation + gates + completion) PASSED.**
**Split decision**: CARVE-IN CONFIRMED (T016 — no build-time trigger fired). No new ADR. Enhancement **#348** filed (high-entropy hex gap).

---

## Next Action

**Run `/aod.deliver 281`** — the feature is code-complete and all gates are green. Deliver will:
- Re-verify the PR #347 title is `feat(281):` (it is), squash-merge, push `main`.
- Verify a release-please PR opens within ~30s; if not, push an empty `feat(281):` marker (per `.claude/rules/git-workflow.md`).
- Record the CARVE-IN determination (from T016 / `.aod/results/senior-backend-engineer.md`).

Then `/aod.document` for the post-delivery quality review.

---

## Final Validation & Gates (Step 5–8)

| Gate | Result |
|---|---|
| Architect (Final + absorbed P1 checkpoint) | **APPROVED** (0 blocking; 2 non-blocking advisories) |
| Code Review | **APPROVED** (no over-build) |
| Security (analyst review) | **APPROVED** — 0 findings (0 C/H/M/L) |
| Design Quality Gate | Skipped (no UI files changed) |
| Security Scan (`/security`) | Skipped (no code files / manifests changed); audit artifact written |
| Economy Gate | **Passed** — no over-build found (AC-2 script reused verbatim, zero net-new deps) |
| Test execution (per-wave 4.5) | Skipped every wave (infra/docs; `summary.json` → `waves_tested: 0`) |

## What shipped (Waves 1–4)

| Wave | Issue | Deliverable | Commit |
|---|---|---|---|
| 1 | #281 (MVP/SC-1) | `.github/workflows/tachi-permissions-verify.yml` — dual-trigger single-anchor gate (jq-guard → `jq empty` → reused #280 AC-2 script → §3/§4 doc-grep), `contents:read`. | `f3e3fb7` |
| 1 | #286 (SC-3) | `.gitleaks.toml.adopter-template` (90 LOC, config-valid, 4 sections) | `f3e3fb7` |
| 2 | #285 (SC-2) | `PRECOMMIT_HOOKS.md §3` default-rule coverage catalog (5/6 covered; hex gap → #348) | `73391c9` |
| 2 | #286 | `PRECOMMIT_HOOKS.md §9.5` + README cross-ref; template validated | `73391c9` |
| 3 | #287 (SC-4) | `PRECOMMIT_HOOKS.md §10` pin-bump cadence + `.github/ISSUE_TEMPLATE/gitleaks-bump.md` + ADR-042 §References | `891d51a` |
| 4 | polish | T016 split-valve CARVE-IN confirmed · T017 regression 16/16 + pre-commit 0 findings · T018 AC 7/7 SC 5/5 · security-scan + economy-check artifacts | (this session) |

## Verification highlights (Wave 4)

- **T017 regression**: `tests/fixtures/gitleaks-rule-interaction/run.sh` = **16/16**; gitleaks pre-commit hook = **0 findings**; overall pre-commit green.
- **T018 AC/SC sweep**: AC **7/7**, SC **5/5**; the four workflow steps green on clean tree — jq guard PASS, `jq empty` rc=0, AC-2 crosscheck **93↔93 byte-exact**, §3/§4 doc-greps match (lines 50/112); adopter-template config-valid.
- **T016 split-valve**: template **90 LOC ≤120**, T010 stayed throwaway (0 new `tests/` files), effort **2.0 d ≤3.0 d** → CARVE-IN.

## Notes / gotchas

- `.aod/results/` is gitignored (agent result files not committed).
- This feature does NOT touch the F-248/F-256 hardening surface or `init.sh`/`template-*`/`defaults.env` — no `/aod.update` clobber risk.
- Non-blocking architect advisories (no action for this delivery): FR-281.7 jq-guard is forward-looking insurance vs runner drift; `gitleaks-bump.md` §10 anchor is a heading-slug deep link that a future §10 rename would silently break.
