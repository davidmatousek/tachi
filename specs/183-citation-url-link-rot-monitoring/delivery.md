# Delivery Retrospective — Feature 183: Citation-URL Link-Rot Monitoring

**Feature**: F-183 — Citation-URL Link-Rot Monitoring (Scheduled CI Check)
**Delivered**: 2026-06-15
**PR**: #330 (squash-merge `0a33d70`)
**Release**: v4.44.0 (release-please PR #331)
**Initiative**: BLP-05 "Framework-Mapping & Output-Fidelity", Wave 3 (integrity sub-wave) — **final feature → BLP-05 COMPLETE 6/6**
**Lifecycle**: define → plan → build → **deliver** (document pending)

---

## 1. What shipped

A weekly **scheduled** GitHub Actions workflow that keeps the framework-crosswalk catalog's cited authority URLs verifiably live:

- **`.github/workflows/tachi-citation-linkrot.yml`** — `schedule` (`17 9 * * 1`, Mondays 09:17 UTC) + `workflow_dispatch` (boolean `inject_sentinel_rot`). Least-privilege (`contents: read` + `issues: write`), ambient `GITHUB_TOKEN`, no PAT/secret. Combined `actions/cache@v4` persists the ledger run-over-run.
- **`scripts/check-citation-urls.py`** — zero-new-dependency stdlib checker (`urllib` + `concurrent.futures` + already-present `pyyaml`). Discovers in-scope URLs (crosswalk `citation` + catalog `url`, `^https?://` filter), classifies, renders a delimited machine block, and reconciles one self-healing tracking issue via native `gh`.
- **`tests/schemas/test_citation_linkrot_parity.py`** — 17 offline tests (parity both-surfaces/both-directions, NFR-001 egress boundary, full classifier matrix).
- **README note** (`schemas/taxonomy/README.md`) — link-rot deferral replaced with the live-monitor reference.

### User stories (4/4)
| Story | Delivered |
|-------|-----------|
| US1 — Weekly confirmed-rot signal | ✓ 404/410 detection with per-source back-references |
| US2 — Never blocks a merge & determinism preserved | ✓ scheduled-only (no `pull_request`/`push`); offline parity guard; NFR-001 boundary |
| US3 — Trustworthy, low-false-positive signal | ✓ 403/401/429 = needs-review; 5xx/timeout = transient, never reported |
| US4 — One self-healing tracking issue | ✓ single sentinel-titled issue; opens/updates/self-closes; deterministic sentinel |

---

## 2. Metrics

| Metric | Value |
|--------|-------|
| Tasks | **21/21** (T001–T020 in build; T021 validated during delivery) |
| Estimated effort | 2.0–3.0 eng-days (Team-Lead) |
| Actual effort | **~1 day** (spec 2026-06-14 → deliver 2026-06-15) — under estimate |
| Offline tests | **22/22 pass** (17 new + 5 pre-existing `test_taxonomy_integrity.py`), 0 regressions |
| NFR-001 proof | module passes 17/17 under an outer egress block (no socket / no DNS / no subprocess) |
| Monitored URL set | **930 unique** (parity surface-A == surface-B union, both directions) |
| Runtime dependency delta | **0** (stdlib + existing `pyyaml`) |
| ADR | **0 created** (deliberate — derivative of accepted ADR-021, below ADR bar) |

### Build-Wave Test Results
| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-01 | 5 | 5 | 0 | pass (regression baseline) |
| wave-02 | 22 | 22 | 0 | pass (17 new offline + 5 pre-existing) |
| wave-03 | — | — | — | review-only (skipped: code-reviewer ∥ security-analyst) |

**Build Summary** (`test-results/summary.json`): **pass** — 22/22 cumulative, 0 regressions, coverage intentionally null (live-fetch/`gh`/main paths are deliver-adjacent, validated by T021).

### E2E gate
**N/A** — no Playwright in this project. The offline suite + the live T021 dispatch are the validation surface.

---

## 3. T021 live-dispatch validation (deliver-adjacent, executed during delivery)

Run live against `main` after merge (the workflow must be on the default branch for `workflow_dispatch`). Two runs per `quickstart.md` §4:

| Run | Input | Outcome | Branch validated |
|-----|-------|---------|------------------|
| **1** (`27551693237`) | `inject_sentinel_rot=true` | Exactly **one** tracking issue **#332** created; sentinel `https://example.invalid/tachi-linkrot-sentinel` named (404 + `(sentinel): validation`); grouped-by-host; `<!--linkrot:start/end-->` machine block; full source back-references | **create** (`rot>0 & no issue → gh issue create`) ✓ |
| **2** (`27552304453`) | `inject_sentinel_rot=false` | #332 edited in place (42→**41** findings, **sentinel dropped — no leak into a non-injected run**); dated delta comment posted; ledger restored from Run 1 via `restore-keys` | **edit/delta** (`rot>0 & open → gh issue edit + comment`) + ledger accumulation + sentinel-no-leak ✓ |

**Self-close branch** (`rot==0 & open → close`) was **not exercised live** — correctly, because the live catalog holds 41 real confirmed-rot URLs (see §4). A monitor that refuses to self-close while real rot exists is the feature working as designed. Self-close remains validated by offline render tests (T012) + code review (T020).

Other contracts confirmed live: monitor-not-gate exit-code (both runs GREEN despite 41 findings), least-privilege permissions sufficient, native `gh` issue lifecycle, no marketplace action.

---

## 4. Headline outcome — the monitor's first live run found 41 real dead citations

On its very first live sweep the monitor surfaced **41 genuine confirmed-rot (404) citation URLs** in the crosswalk catalog — all introduced during the recent BLP-05 Wave 2 expansion. Verified real (not bot-blocks): both the checker UA and a browser UA return identical 404s, with redirects followed to final status.

| Fix-class | Count | Detail | Origin |
|-----------|-------|--------|--------|
| MITRE ATLAS technique pages | ~38 | `https://atlas.mitre.org/techniques/AML.Txxxx` all 404 (ATLAS URL scheme changed) | #186 |
| NIST AI RMF DOI | 1 (~75 citing records) | `https://doi.org/10.6028/NIST.AI.100-1` → redirects to `nvlpubs.nist.gov/.../NIST.AI.100-1.pdf` → 404 (target moved) | #184 |
| OWASP GenAI LLM URLs | 4 | `genai.owasp.org/llmrisk/llm02|llm03|llm05/...` + `resource/agentic-ai-top-10-vulnerabilities/` 404 (site restructured) | crosswalk |

**Disposition**: Fixing citation URLs is **out of scope for #183** (it monitors; humans remediate — per `.claude/rules/scope.md`). Live state is tracked in self-healing issue **#332**; the remediation work item is filed as backlog **#333** (stage:discover). When the URLs are corrected, a subsequent scheduled run will self-close #332.

---

## 5. Surprises

- **The monitor proved its value within minutes of going live** — 41 real dead links on the first sweep, not the zero-or-handful the deterministic-sentinel design assumed. The deliver-adjacent T021 run was the thing that surfaced them; deferring it would have shipped an unvalidated integration *and* missed the signal.
- **The clean two-run "create → self-close" lifecycle couldn't complete as scripted** — real rot blocked the self-close. Re-framed (correctly) as the feature working, not a test failure.

---

## 6. Lessons learned

Captured as **KB Entry 17** (`docs/INSTITUTIONAL_KNOWLEDGE.md`): *When a feature's only true integration test is deliver-adjacent (`[MANUAL-ONLY]`), run it at delivery rather than deferring it — and expect a brand-new monitor to find real pre-existing defects on first run; pre-decide the disposition.* Corollary: citation URLs added during rapid catalog expansion (#184/#185/#186) were never validated against live endpoints; the monitor is now the systemic guard, but authoring-time reachability checks would shift it left.

---

## 7. Follow-ups

| Item | Where | Status |
|------|-------|--------|
| Remediate 41 dead citation URLs | **#333** (backlog, stage:discover) + live tracker **#332** | open |
| `link-rot` label not attached to #332 (best-effort path; label exists in repo) | minor cosmetic; issue found by title sentinel, not label | observation |
| Node.js 20→24 action-runtime deprecation (`actions/cache@v4`, `checkout@v4`, `setup-python@v5`) | repo-wide (all workflows), GitHub auto-updates pinned majors | observation, non-blocking |

---

## 8. Definition of Done

- [x] All in-build tasks complete (T001–T020); T021 live-validated during delivery
- [x] Offline suite green, network-free (NFR-001 proven)
- [x] PR #330 squash-merged to `main`; branch deleted
- [x] Release-please PR #331 (`chore(main): release 4.44.0`) opened — release gate satisfied
- [x] Closure docs updated (Product / Architecture / DevOps agents)
- [x] Retrospective complete; KB Entry 17 added; remediation #333 filed
- [x] Live integration validated (T021 Run 1 + Run 2)
- [ ] Issue #183 → `stage:done` + closed (Command Step 10)
- [ ] `/aod.document` post-delivery quality review (Command Step 13)
