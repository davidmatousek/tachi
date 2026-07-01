# NEXT-SESSION — Feature 281: CI & Governance Hardening Tail (F-4/F-5 follow-ups)

**Branch**: `281-ci-governance-hardening-tail` · **Draft PR**: [#347](https://github.com/davidmatousek/tachi/pull/347) (`feat(281):` title, correct)
**Progress**: 15/18 tasks (83%). Waves 1–3 complete + committed + pushed. **Standalone 3-wave ceiling reached** — Wave 4 (polish) + finalization (Steps 5–9) remain.
**Split decision**: CARVE-IN held (no trigger fired). No new ADR. Enhancement **#348** filed (high-entropy hex gap).

---

## Next Actions

**All prerequisites are met — no blockers.** In a fresh session run `/aod.build 281`; it auto-resumes at **Wave 4** (T016–T018 are unmarked; T001–T015 are `[X]`).

1. **Wave 4 — Polish** (all off the critical path; gitleaks v8.30.1 is installed locally):
   - **T016** (`senior-backend-engineer`) — Split-valve final confirmation. Re-measure `.gitleaks.toml.adopter-template` LOC (currently **90 ≤ 120** ✓), confirm T010 stayed a throwaway probe (no new committed harness ✓), total effort ≤ 3.0 d ✓. Record the final **CARVE-IN** determination for `/aod.deliver`.
   - **T017** [P] (`tester`) — Regression sweep: `bash tests/fixtures/gitleaks-rule-interaction/run.sh` (**16/16** required) + `pre-commit run --all-files` (**0 findings**). Confirms the #285/#286 gitleaks work introduced no fixture regression.
   - **T018** (`tester`) — Final AC/SC sweep: verify AC-1..AC-7 and SC-1..SC-5; confirm `tachi permissions-verify` is green on clean `main` (US-1 scenario 4) and the §3/§4 doc-greps match the live byte-exact headings.
2. **Step 5 — Final Validation** (last wave → runs after Wave 4): parallel Architect + Code-Review + Security-analyst. *This absorbs the P1 checkpoint (Wave 4 is the last wave).*
3. **Step 6 — Design Quality Gate**: will **skip** (no UI files changed — diff is `.yml`/`.md`/`.toml.adopter-template`).
4. **Step 7 — Security Scan** (`/security` skill): runs on changed code/manifests (the new workflow YAML + adopter template).
5. **Step 8 — Economy Gate**: diff-scoped code-reviewer verdict (advisory). Note `.gitleaks.toml.adopter-template` is 90 LOC, mostly comments.
6. **Step 9 — Report Completion**, then `/aod.deliver 281`.

---

## What shipped (Waves 1–3)

| Wave | Issue | Deliverable | Commit |
|---|---|---|---|
| 1 | #281 (MVP/SC-1) | `.github/workflows/tachi-permissions-verify.yml` — dual-trigger single-anchor gate (jq-guard → `jq empty` → reused #280 AC-2 script → §3/§4 doc-grep), `contents:read`. Smoke-tested (T006). | `f3e3fb7` |
| 1 | #286 (SC-3) | `.gitleaks.toml.adopter-template` (90 LOC, config-valid, 4 sections) | `f3e3fb7` |
| 2 | #285 (SC-2) | `PRECOMMIT_HOOKS.md §3` "Default-rule coverage catalog" (empirical RuleID map; 5/6 covered; hex gap → #348) | `73391c9` |
| 2 | #286 | `PRECOMMIT_HOOKS.md §9.5` + README cross-ref; template validated (T014) | `73391c9` |
| 3 | #287 (SC-4) | `PRECOMMIT_HOOKS.md §10` pin-bump cadence (6-step recipe; Step 5 rule-ID re-derivation load-bearing) + `.github/ISSUE_TEMPLATE/gitleaks-bump.md` + ADR-042 §References wiring | `891d51a` |

**Empirical #285 map** (gitleaks v8.30.1 defaults): `ghp_`→`github-pat`, `AKIA`→`aws-access-token`, `sk-`→`generic-api-key` (no dedicated openai rule), `sk-ant-`→`anthropic-api-key`, PEM→`private-key`, high-entropy-hex→**none** (#348).

## P0 Checkpoint (Waves 1–2): APPROVED_WITH_CONCERNS → GO

All 8 FR-281.x verified faithful; #281 fail-closed + green on live `main` (93↔93 byte-exact); #285 gap honest; #286 within LOC ceiling; CARVE-IN holds. Non-blocking concerns to remember at finalization:
- **[LOW]** `push:[main]` over-triggers on the workflow's own edits — **intended (safe direction), do not "fix."**
- **[Wave-3 — DONE]** #287 rule-ID re-derivation step is present (§10.2 Step 5, marked load-bearing).
- Details: `.aod/results/architect-p0-checkpoint-281.md`

## Notes / gotchas

- Test execution (post-wave 4.5) **skipped every wave** — no source-code files changed (infra/docs feature); this is correct, `summary.json` will show `waves_tested: 0`.
- `.aod/results/` is gitignored (agent result files are not committed).
- Working tree is clean and pushed through `891d51a`.
- Insurance per project memory: this feature does NOT touch the F-248/F-256 hardening surface or `init.sh`/`template-*`/`defaults.env`; no `/aod.update` clobber risk here.
