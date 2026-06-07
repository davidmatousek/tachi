> **SUPERSEDED (2026-06-07) — Feature DELIVERED.** This was a mid-build snapshot taken at W2 ("9/15, resume at W3"); W3–W4 subsequently completed and the feature shipped via PR #323 (squash `349e160`). Retained for history only. **Authoritative closure record: [delivery.md](delivery.md).** Final state: 37 `related` / 0 `superseded` (4 deferred classes), integrity 5/5, primary 542 preserved.

# NEXT-SESSION Handoff — F-182 Crosswalk `related` + `superseded` Edges

**Branch**: `182-crosswalk-related-superseded-edges` · **Draft PR**: #323 · **Date**: 2026-06-07
**Stopped at**: standalone 3-wave ceiling (W0+W1+W2 done). Resume with `/aod.build 182` → auto-resumes at **W3**.
**Last commit**: `0289a7c` (pushed). Working tree clean except this file.

## Status: 9/15 tasks complete (T001–T009). US1 MVP + US2 shipped; integrity 5/5 green.

| Wave | Tasks | Status |
|------|-------|--------|
| W0 Setup | T001 baseline | ✅ 542/0/0; catalogs 53/36/701/60; 5 passed |
| W1 Foundational | T002 harvest, T003 architect gate | ✅ tripwire FIRED (core=37<80); architect APPROVED floor=37 |
| W2 US1+US2 | T004 author, T005 audit, T006 verify, T007 survey, T008 defer, T009 verify | ✅ +37 related (22 high/15 med); superseded=0 + deferral; 5/5 |
| **W3 US3** | **T010 README rubric, T011 verify** | ⏳ **NEXT** |
| W4 Close | T012 provenance+CHANGELOG, T013 diff-guard, T014 final gate, T015 deliver-time | ⏳ pending |

## Key result — YIELD-TRIPWIRE FIRED (documented achievable floor = 37, not ≥80)

This is the **spec-sanctioned outcome** (FR-002 "anti-drift over floor-hitting"; A2; team-lead watch-item). NOT a failure. Architect authorized it at T003. Cause: the floor fell short because **OWASP-Web→CWE yields 0** — F-180 already authored *every* in-catalog CWE cross-ref as a `primary` edge — and the 542-edge primary graph (34 cwe→cwe, 25 atlas→attack, 58 owasp→atlas) already captured the dense relationships; only beyond-primary edges remain. **No low-padding** (all 37 are high/medium).

Per-class authored (after T005 audit): CWE↔CWE 22 · ATLAS→ATT&CK 7 · OWASP-LLM→ATLAS 8 · OWASP-Web→CWE 0. Confidence: 22 high / 15 medium.

## Remaining work (W3 + W4)

**T010 [US3] (senior-backend-engineer)** — extend `schemas/taxonomy/README.md` rubric (FR-009): add a `related`/`superseded` calibration section with a worked example **per audited source class**, the **CWE View-ID rule** (parents are view-dependent), an explicit **"OWASP-LLM→CWE is prose-only → low/inferred" caution** (confirmed live: 9/10 LLM pages publish no structured CWE list; only LLM10 lists CWE-400), and the authoritative-source list. Keep the existing primary rubric + anti-drift rule intact. The README confidence rubric is around L128–141 (anti-drift rule L139).
**T011 [US3] (code-reviewer)** — confirm the rubric is self-sufficient (a new author can calibrate from README alone) AND that its examples match the confidence labels actually used in the 37 authored edges (SC-006).
**T012 (s-b-engineer)** — add an F-182 **header provenance note** to `schemas/taxonomy/crosswalk.yaml` (top of file, mirroring the F-186 convention) + a `feat(182)` **CHANGELOG.md** entry (BLP-05 F-3 sibling-h3 cluster: `### Crosswalk related/superseded edge expansion (BLP-05 F-3 #182)`). Note the tripwire outcome (37) honestly.
**T013 (code-reviewer)** — no-migration diff-guard, runs AFTER T012: `git diff main...HEAD` touches ONLY `crosswalk.yaml`, `README.md`, `CHANGELOG.md`, `specs/182-*`; **0** catalog/test/schema_version/ADR change; primary == 542 (SC-005). (`.aod/results/` is gitignored — won't appear.)
**T014 (tester)** — final gate: `pytest tests/schemas/test_taxonomy_integrity.py` → 5 passed; `/aod.analyze` clean.
**T015** — deliver-time (close #182 `stage:done` via `/aod.deliver`); NOT a build task.

Then `/aod.build` Steps 5–8: final validation (architect+code-reviewer), design gate (auto-skip, no UI), security scan (auto-skip, no code/manifest change — only YAML/MD), completion report.

## Gotchas for next session
- **Append-only authoring**: never re-dump crosswalk.yaml (would reformat 542 edges → huge diff). The 37 related edges are appended after a `# ─── F-182` section comment at EOF.
- **Citation shape**: integrity `test_citation_shape` uses `re.match("^https?://")` (prefix) — citations carry `(Nature, View-N)` / `(ATT&CK-reference …)` / `(Related Frameworks …)` after the URL; no `": "` so they're clean plain scalars. T012's provenance note must not break this.
- **atlas.mitre.org technique pages 404 via WebFetch** (anti-bot) — verify ATLAS→ATT&CK against `raw.githubusercontent.com/mitre-atlas/atlas-data/.../dist/ATLAS.yaml` `ATT&CK-reference` field instead.
- **Harvest evidence**: `specs/182-*/reference-edges.yaml` (FR-012, 37 candidates + survey block + audit note). `/tmp/182-harvest/` has the raw per-lane harvest + assembler (transient).
- Agent results: `.aod/results/architect.md` (T003), `.aod/results/code-reviewer.md` (T005).

## Resume prompt
```
Resume F-182 crosswalk edge expansion (branch: 182-crosswalk-related-superseded-edges).
Waves W0-W2 complete (US1 MVP + US2; 37 related edges, tripwire floor=37, 5/5 green,
committed 0289a7c). Run /aod.build 182 to continue with W3 (T010 README rubric).
```
