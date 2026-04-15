# Backlog Execution Plan

**Date**: 2026-04-10
**Source**: GitHub Issues (live), not BACKLOG.md snapshot
**Scope**: All 15 open issues in Discover stage
**Purpose**: Sequenced execution order by criticality and dependencies

---

## Quick State — Execution Order

Run each `/aod.define` in order. Items on the same line can run in parallel.

| # | Command | Issue | Title |
|---|---------|-------|-------|
| **Wave 0 — Correctness fixes (week 1, parallel) — BOTH DELIVERED 2026-04-11** ||||
| ~~1~~ | ~~`/aod.define 130`~~ **[DONE]** | [#130](https://github.com/davidmatousek/tachi/issues/130) | ~~Fix attack path Mermaid rendering when mmdc is not installed~~ — **DELIVERED 2026-04-11 via wave-based autonomous orchestration (~1.5h wall-clock); shipped Option 2 (mmdc hard prerequisite) not Option 1 (pymmdc); authored ADR-022 as first tachi CLI-prerequisite ADR; v4.10.1 auto-cut by release-please** |
| ~~2~~ | ~~`/aod.run 136`~~ **[DONE]** | [#136](https://github.com/davidmatousek/tachi/issues/136) | ~~MAESTRO Phase 1: canonical L5-L7 layer naming fix~~ — **DELIVERED 2026-04-11 via `/aod.run` (calibration successful, several hours wall-clock)** |
| **Wave 1 — Foundation work (weeks 2-4, parallel)** ||||
| ~~3~~ | ~~`/aod.define 82`~~ **[DONE]** | [#82](https://github.com/davidmatousek/tachi/issues/82) | ~~Enrich 11 threat agents via skill references~~ — **DELIVERED 2026-04-12. All 11 STRIDE+AI threat agents migrated to lean + skill references pattern. 11 companion skill directories created. +30 new detection pattern categories. 68 tasks across 18 waves. See CLAUDE.md Feature 082 entry for full details.** |
| ~~4~~ | ~~`/aod.define 141`~~ **[DONE]** | [#141](https://github.com/davidmatousek/tachi/issues/141) | ~~MAESTRO Phase 2: cross-layer attack chain analysis~~ — **DELIVERED 2026-04-12. Cross-layer attack chain correlation engine (orchestrator Phase 3.5), attack-chains.md artifact, threat report Section 6 narrative, PDF chain diagram pages, schema (attack-chain.yaml v1.0), parser (parse_attack_chains), 800+ lines test coverage. 34 tasks across 7 waves. PR #159, v4.13.0.** |
| **Wave 2 — Sequential follow-on (week 5) — DELIVERED 2026-04-14** ||||
| ~~5~~ | ~~`/aod.define 129`~~ **[DONE]** | [#129](https://github.com/davidmatousek/tachi/issues/129) | ~~Attack tree delta sub-agent (must wait for #82)~~ — **DELIVERED 2026-04-14 via PR #162. New leaf agent `tachi-attack-tree-delta` extracts Section 5 generation from threat-report (-56 lines). Deterministic Rule 1 (carry-forward) / Rule 2 (fresh + per-finding Rule 3 reconciliation) / no-baseline fallback dispatch on `delta_counts`. Rule 3 structural similarity algorithm with named constants (LEAF_MATCH_THRESHOLD=0.70, TREE_SIMILARITY_THRESHOLD=0.80, NODE_COUNT_VARIANCE=0.20). `attack_tree_count` definition unified across schema/template/sub-agent (reverses Feature 104 metric). 13 tasks complete, ~1 day wall-clock against 1-2 day estimate, smooth sailing per retrospective. Sidecar bugfix PR #164 added auto-detection of newest `docs/security/<timestamp>/` run directory across the four downstream tachi commands.** |
| **Wave 3 — ADR spikes (week 5, run alongside Wave 2 as a pair)** ||||
| 6 | `/aod.define 143` | [#143](https://github.com/davidmatousek/tachi/issues/143) | MAESTRO Phase 4: OWASP AIVSS evaluation ADR |
| 7 | `/aod.define 144` | [#144](https://github.com/davidmatousek/tachi/issues/144) | MAESTRO companion: NIST AI RMF integration ADR |
| **Wave 4 — MAESTRO enhancements (weeks 6-8)** ||||
| 8 | ~~*(re-scope check)*~~ **DONE 2026-04-14** | [#98](https://github.com/davidmatousek/tachi/issues/98) | ~~MAESTRO coverage matrix — investigate whether #141 subsumed this~~ — **NOT subsumed. Shrunk from 2-3 weeks to ~1 day. Real gap: every layer-aware view (threats.md "Risk by MAESTRO Layer", PDF MAESTRO Layer Analysis page, maestro-stack infographic) silently omits layers with zero findings (per `output-schemas.md` spec rule and `extract-report-data.py:388` filter). Reviewers cannot tell "analyzed but clean" from "not applicable" or "never analyzed." Fix: invert the omission rule across the 3 enforcement points; activate the existing dead-code empty-layer branch in `maestro-findings.typ:151-155`. Reschedule from Wave 4 to Wave 5 opportunistic. See [#98 comment](https://github.com/davidmatousek/tachi/issues/98#issuecomment-4247897465).** |
| 9 | `/aod.define 142` | [#142](https://github.com/davidmatousek/tachi/issues/142) | MAESTRO Phase 3: agentic threat pattern expansion |
| 10 | `/aod.define 145` | [#145](https://github.com/davidmatousek/tachi/issues/145) | MAESTRO canonical worked example |
| **Wave 5 — Nice-to-haves (weeks 9+, opportunistic)** ||||
| 11 | `/aod.define 55` | [#55](https://github.com/davidmatousek/tachi/issues/55) | Security Progression Summary (multi-run trends) |
| 12 | *(re-scope check)* | [#69](https://github.com/davidmatousek/tachi/issues/69) | Expand example datasets — fold into #145 if overlap |
| 13 | `/aod.validate 126` | [#126](https://github.com/davidmatousek/tachi/issues/126) | Auto-detect architecture drift (needs body and ICE first) |
| 14 | `/aod.validate 62` | [#62](https://github.com/davidmatousek/tachi/issues/62) | Custom brand presets (needs body and ICE first) |
| 15 | `/aod.define 46` | [#46](https://github.com/davidmatousek/tachi/issues/46) | Sync upstream AOD Kit (maintenance, quarterly cadence) |

**Immediate actions today**:
1. ~~Run `/aod.define 130`~~ **DONE 2026-04-11** — P0 validated bug shipped in ~1.5h via wave-based autonomous orchestration. Flagship "show to exec board" use case unblocked on fresh installs.
2. ~~Run `/aod.run 136`~~ **DONE 2026-04-11** — `/aod.run` calibration succeeded; shipped correctly in several hours. MAESTRO Phases 2, 3, 5 and the #98 re-scope check are now unblocked.
3. ~~Post re-scope comments on #98 and #69 to prevent duplicate work~~ **DONE 2026-04-12** — scope overlap flag posted on #98 (gated on #141), scope adjacency flag posted on #69 (gated on #145).
4. ~~Run `/aod.validate 126` and `/aod.validate 62` to get bodies and ICE scores on stub issues~~ **DONE 2026-04-12** — #126 "Auto-detect architecture drift" scored ICE 17 (I:9 C:5 E:3), #62 "Custom brand presets" scored ICE 16 (I:6 C:5 E:5). Both above defer gate, both remain Wave 5 opportunistic.

**All immediate actions complete.** Waves 0, 1, and 2 fully delivered.

**Next up now that Waves 0, 1, 2 are fully delivered**:
- **#129 DELIVERED 2026-04-14** — attack tree delta sub-agent shipped as PR #162. Parent-leaf decomposition with structured JSON manifest IPC. Rule 3 reconciliation now actually fires (the original bug — it never fired in practice). Sidecar PR #164 added auto-detection of newest `docs/security/<timestamp>/` run directory across the four downstream tachi commands.
- **Recommended next: Wave 3 ADR pair — `/aod.define 143` + `/aod.define 144`** (OWASP AIVSS ADR + NIST AI RMF ADR). Pure research/documentation scope, paired research phase, single `/aod.define` cycle covers both in ~1 week vs 2 weeks if sequenced. Both reference canonical MAESTRO complementary frameworks.
- **#98 re-scope check DONE 2026-04-14** — NOT subsumed by #141. Shrunk from 2-3 weeks to ~1 day; rescheduled to Wave 5 opportunistic. Gap is real: layer-aware views silently omit zero-finding layers, hiding "analyzed but clean" vs "not applicable." Fix is a 3-point omission-rule inversion. See [#98 comment](https://github.com/davidmatousek/tachi/issues/98#issuecomment-4247897465).
- **Wave 4 (after Wave 3)**: #142 (MAESTRO Phase 3 agentic patterns), #145 (MAESTRO canonical worked example). Both unblocked, both benefit from Phase 2 chains being in place.
- **ADR-022 (Feature 130 output) establishes new precedent** — any future CLI prerequisite (third-party binary, renderer, compiler required at runtime) now follows the defense-in-depth two-gate pattern: shell-level preflight in the command file + Python-level `shutil.which` raise at the function boundary, gated on input detection, with a Future Work clause for helper extraction once a third CLI prereq is added.

---

## Execution Mode Notes

Default posture is manual orchestration (user acts as orchestrator) to minimize context rot on complex work. Exception: small, surgical fixes with explicit DoD and no unresolved decisions are safe candidates for `/aod.run` autonomous execution. The backlog was audited for `/aod.run` suitability on 2026-04-10.

### Safe autonomous execution via `/aod.run`

| Issue | Why it qualifies | Calibration result |
|-------|------------------|--------------------|
| [#136](https://github.com/davidmatousek/tachi/issues/136) MAESTRO L5-L7 fix | Mechanical rename + keyword reassignment + regenerate examples. DoD explicit down to file paths. Zero architectural decisions. | **Delivered 2026-04-11.** `/aod.run` completed the full lifecycle successfully but took several hours wall-clock time for a ~1 day scope. Work shipped correctly; tier assignment validated. |
| [#130](https://github.com/davidmatousek/tachi/issues/130) Mermaid rendering fix | Small surgical scope; seed decision (Option 2: mmdc hard dependency, NOT Option 1: pymmdc) captured in PRD before Build. Wave-based manual orchestration across Setup/Foundational/US1/US2/US3/CI&Docs/Polish. | **Delivered 2026-04-11 in ~1.5h wall-clock** against a 1-2d PRD estimate — the compression came from parallel wave execution on disjoint work streams (preflight gate, mid-render aggregator, docs sync, CI workflow, ADR-022 authorship). Second calibration data point: surgical bug fixes with clear scope ship dramatically faster than time-box estimates suggest when wave parallelism is applied. |

**Calibration finding**: `/aod.run` and wave-based manual orchestration both work for small surgical scopes, but the trade-off differs. `/aod.run` trades wall-clock time for attention budget (good for overnight, parallel to other manual work, or context-protecting the user). Wave-based manual orchestration on a small scope like #130 can compress a 1-2d estimate to ~1.5h wall-clock when wave parallelism is exploited across disjoint work streams, but it requires active attention throughout. Prefer `/aod.run` when attention matters more than elapsed time; prefer wave-based manual orchestration when speed matters and attention is available. The tier-assignment heuristic still holds — if the issue body lets a senior engineer execute without clarifying questions, the work can ship either way — but set duration expectations explicitly.

### Workable with a seed decision up front

These can run via `/aod.run` if the one open design decision is pre-seeded in the run arguments so the agent does not have to ask.

| Issue | Seed decision required |
|-------|------------------------|
| ~~[#130](https://github.com/davidmatousek/tachi/issues/130) Mermaid fix~~ **[DONE 2026-04-11]** | ~~Confirm Option 1 (pymmdc) from the body's recommended options before running~~ — **Delivered Option 2 (mmdc hard dependency) instead**, after research.md rejected pymmdc as a GPL-3.0 Node.js wrapper rather than a pure-Python renderer (spec 112 research had a factual error corrected in this PR). See ADR-022 for the full rejected-alternatives analysis. |
| [#145](https://github.com/davidmatousek/tachi/issues/145) MAESTRO worked example | Pre-select the domain (healthcare, autonomous research, or supply-chain) before running |

### Research phase via `/aod.run`, review ADR before Build

These are small ADR-only scopes where `/aod.run` can handle research and drafting, but the decision belongs to you. Pause after Plan, review the ADR draft, then let Build commit.

| Issue | Why pause before Build |
|-------|------------------------|
| [#143](https://github.com/davidmatousek/tachi/issues/143) AIVSS ADR | Output is literally a decision document; review before committing |
| [#144](https://github.com/davidmatousek/tachi/issues/144) NIST AI RMF ADR | Same — review draft before Build commits the ADR |

### Manual orchestration (avoid `/aod.run`)

| Issue | Reason |
|-------|--------|
| ~~[#82](https://github.com/davidmatousek/tachi/issues/82) Enrich 11 threat agents~~ | **DELIVERED 2026-04-12** |
| ~~[#141](https://github.com/davidmatousek/tachi/issues/141) MAESTRO Phase 2 chains~~ | **DELIVERED 2026-04-12** — chose rule-based correlation |
| ~~[#129](https://github.com/davidmatousek/tachi/issues/129) Attack tree delta sub-agent~~ | **DELIVERED 2026-04-14** — Triad-governed manual orchestration; Rule 3 named-constant heuristics designed in spec, ~1 day wall-clock |
| [#142](https://github.com/davidmatousek/tachi/issues/142) MAESTRO Phase 3 patterns | Central ADR unresolved (extend agents vs new tier vs hybrid) |
| [#55](https://github.com/davidmatousek/tachi/issues/55) Security Progression Summary | Novel capability; multiple design decisions |
| [#46](https://github.com/davidmatousek/tachi/issues/46) Upstream AOD sync | Three-way manual merge review per file is the entire job |

### Not yet executable

| Issue | Action needed first |
|-------|---------------------|
| [#98](https://github.com/davidmatousek/tachi/issues/98) MAESTRO coverage matrix | Re-scope after #141 lands |
| [#69](https://github.com/davidmatousek/tachi/issues/69) Expand example datasets | Re-scope after #145 lands |
| ~~[#126](https://github.com/davidmatousek/tachi/issues/126) Architecture drift detection~~ | ~~`/aod.validate 126` to add body and ICE~~ — **DONE 2026-04-12**, ICE 17 (I:9 C:5 E:3). Ready for `/aod.define 126` when scheduled. |
| ~~[#62](https://github.com/davidmatousek/tachi/issues/62) Custom brand presets~~ | ~~`/aod.validate 62` to add body and ICE~~ — **DONE 2026-04-12**, ICE 16 (I:6 C:5 E:5). Ready for `/aod.define 62` when scheduled. |

### Heuristic for future `/aod.run` decisions

If the issue body would let a good senior engineer execute without asking a clarifying question, `/aod.run` can probably execute it too. If they would need to come back and ask, so will the agent — and context rot accumulates while it tries to work around the absence of your answer. Pre-seeding the open decision in the run arguments is an acceptable workaround for small, bounded scopes.

---

## Backlog Snapshot

15 open issues, all in Discover stage. Nothing in Define, Plan, Build, or Deliver.

Composition:

- **6 MAESTRO items** — the family captured during the CSA compliance audit on 2026-04-10: #136 (parent), #141, #142, #143, #144, #145
- **2 critical correctness items** — #130 Mermaid bug (validated, ICE 27), #136 MAESTRO L5-L7 naming (ICE 21)
- **1 foundational refactor** — #82 threat agent skill externalization (ICE 24)
- **1 incremental correctness fix** — #129 attack tree delta sub-agent
- **1 adjacent MAESTRO enhancement** — #98 coverage matrix (retro item, may overlap with #141)
- **1 market differentiator** — #55 Security Progression Summary (ICE 19)
- **3 unscoped nice-to-haves** — #62 brand presets, #69 expand examples, #126 architecture drift
- **1 tooling maintenance** — #46 upstream AOD Kit sync (9 new files plus 21 differing files)

---

## Key Observations

Three scheduling constraints that change the naive ICE-sorted order.

### ~~#130 is validated P0 and has been idling~~ **DELIVERED 2026-04-11**

~~ICE 27, already has a user story and PM validation on the issue, and the failure was directly observed in a real adopter run at `/Users/david/Projects/second-brain-mcp/docs/security/2026-04-09T19-13-20/`. It blocks the flagship "show to exec board" use case on any fresh install without Node.js installed globally. This issue has been sitting in Discover while it is effectively ready for Define. It should ship before anything else because it is the cheapest and highest-impact fix in the backlog.~~

**Delivered 2026-04-11 via PR #148** (squash commit `d35a667`), auto-released as **v4.10.1** by release-please. Shipped Option 2 (mmdc hard prerequisite with defense-in-depth preflight gates) after research.md factual correction rejected Option 1 (pymmdc is a GPL-3.0 Node.js wrapper, not a pure-Python renderer). Key outputs: **ADR-022** (first tachi ADR governing CLI-prerequisite posture), new fresh-install CI workflow `.github/workflows/tachi-mmdc-preflight.yml`, 7-location canonical install command consistency, backward-compatibility preserved (5/5 byte-deterministic baselines unchanged). Post-delivery `/aod.document` simplify pass extracted `_build_error_record()` helper and consolidated 8 test fixtures, netting -138 lines across the two modified files. Adopter trust restored — the second-brain-mcp observation pattern that originally surfaced this bug is now impossible because the text-fallback Typst branch is deleted outright.

### #82 and #129 have a file-level conflict on threat-report.md

#82 refactors all 11 threat agents (including threat-report.md) from the current inline-knowledge Pattern B to the lean-plus-skill-references Pattern A proven by control-analyzer. #129 extracts attack tree generation out of threat-report.md into a dedicated sub-agent. If scheduled in parallel, they will conflict both in merge and in the cognitive model of how threat-report.md is structured. #82 should land first so that #129 extracts from the refactored lean version rather than the current 300-line monolith. This is the only forced sequential dependency in Wave 1.

### #98 MAESTRO coverage matrix may be partially subsumed by #141

#141 Phase 2 cross-layer attack chains will necessarily expose which MAESTRO layers have findings and which do not, because attack chains reference layer transitions. #98's original ask was "show which layers have threat coverage," which may become a trivial extension of Phase 2 output rather than a standalone feature. Do not schedule #98 until after #141 ships and the scope has been re-evaluated. It may close as duplicate or shrink to a one-day follow-on.

---

## Execution Waves

### Wave 0 — Correctness fixes (week 1) — **BOTH DELIVERED 2026-04-11**

Both items are P0 and ship in parallel because they touch disjoint code paths. Both delivered same day.

| Order | Issue | Why now | Estimated effort | Actual result |
|-------|-------|---------|------------------|---------------|
| ~~1~~ | ~~[#130](https://github.com/davidmatousek/tachi/issues/130) Mermaid rendering fix~~ | P0 validated bug; blocks flagship "show to exec board" use case on fresh installs; already has user story and DoD on the issue | 1-2 days | **DELIVERED 2026-04-11** — PR #148, ~1.5h wall-clock via wave-based manual orchestration, shipped as v4.10.1 |
| ~~2~~ | ~~[#136](https://github.com/davidmatousek/tachi/issues/136) MAESTRO L5-L7 correctness~~ | P0 correctness; tachi currently ships non-canonical taxonomy while citing CSA as single source of truth | ~1 day | **DELIVERED 2026-04-11** — PR #146 via `/aod.run`, several hours wall-clock, shipped as v4.10.0 — unblocks [#141](https://github.com/davidmatousek/tachi/issues/141), [#142](https://github.com/davidmatousek/tachi/issues/142), [#145](https://github.com/davidmatousek/tachi/issues/145) |

~~Run `/aod.define 130` and `/aod.define 136` back to back. Triad can pick up both in the same week. Ship within five business days.~~ **Shipped within 24h** — #136 delivered via `/aod.run` overnight, #130 delivered same-day via wave-based manual orchestration. Both Wave 0 targets closed.

### Wave 1 — Foundation work (weeks 2-4)

Both items run in parallel because they touch different parts of the pipeline. #82 rewrites threat agent internals. #141 adds post-finding correlation logic in the orchestrator.

| Order | Issue | Why this wave | Effort | Conflict notes |
|-------|-------|---------------|--------|----------------|
| ~~3~~ | ~~[#82](https://github.com/davidmatousek/tachi/issues/82) Enrich 11 threat agents via skill refs~~ | ~~ICE 24; architectural foundation for every future threat agent improvement; detection quality lift across the entire STRIDE+AI tier~~ | ~~2-4 weeks~~ | **DELIVERED 2026-04-12** — 18-wave build, 68 tasks, all 11 agents migrated to lean pattern with skill references |
| ~~4~~ | ~~[#141](https://github.com/davidmatousek/tachi/issues/141) MAESTRO Phase 2 cross-layer chains~~ | ~~ICE 20; defining MAESTRO capability; unblocks #145 and re-scopes #98~~ | ~~2-3 weeks~~ | **DELIVERED 2026-04-12** — PR #159, 34 tasks across 7 waves, rule-based correlation (not LLM-assisted). Unblocks #145, #142, #98 re-scope |

### Wave 2 — Sequential follow-on to Wave 1 (week 5) — **DELIVERED 2026-04-14**

| Order | Issue | Why this slot | Effort | Actual result |
|-------|-------|---------------|--------|---------------|
| ~~5~~ | ~~[#129](https://github.com/davidmatousek/tachi/issues/129) Attack tree delta sub-agent~~ | ~~Correctness fix for delta reconciliation (Rule 3 never fires in practice); important for incremental threat modeling quality~~ | ~~1-2 weeks~~ | **DELIVERED 2026-04-14** — PR #162, ~1 day wall-clock against 1-2d estimate. New leaf agent extracts Section 5 generation; deterministic Rule 1/2/3 dispatch; named-constant heuristics; `attack_tree_count` unification reverses Feature 104. Sidecar PR #164 fixed cwd auto-detection bug across the four downstream tachi commands. |

### Wave 3 — ADR spikes (week 5, pair, run alongside Wave 2)

These two are pure documentation and research work with overlapping research phases. They can happen during the same weeks as Wave 1 or Wave 2 implementation without competing for engineering resources.

| Order | Issue | Why now | Effort | Pairing |
|-------|-------|---------|--------|---------|
| 6 | [#143](https://github.com/davidmatousek/tachi/issues/143) OWASP AIVSS ADR | ICE 22 but tiny scope (ADR only); canonical MAESTRO references AIVSS as companion scoring framework | ~1 week | Pair with #144 |
| 7 | [#144](https://github.com/davidmatousek/tachi/issues/144) NIST AI RMF ADR | ICE 20; canonical MAESTRO references NIST AI RMF alongside AIVSS as complementary framework | ~1 week | Pair with #143 |

Run both as a single `/aod.define` cycle because the research phase overlaps almost entirely: read canonical MAESTRO sources, evaluate external framework integration depth, commit ADRs. One week total for both paired versus two weeks if sequenced.

### Wave 4 — MAESTRO enhancements (weeks 6-8)

| Order | Issue | Rationale | Effort | Dependency |
|-------|-------|-----------|--------|------------|
| ~~8~~ | ~~**Re-scope check on [#98](https://github.com/davidmatousek/tachi/issues/98)**~~ **DONE 2026-04-14** | ~~Before doing work, verify whether #141 Phase 2 subsumed the coverage matrix ask~~ — **Investigation complete. NOT subsumed; shrunk from 2-3 weeks to ~1 day; rescheduled to Wave 5 opportunistic. Real gap: every layer-aware view filters out zero-finding layers, so reviewers can't distinguish "analyzed but clean" from "not applicable." Fix is a 3-point omission-rule inversion + dead-code activation in `maestro-findings.typ:151-155`.** | ~~1 hour investigation~~ | ~~After #141~~ |
| 9 | [#142](https://github.com/davidmatousek/tachi/issues/142) MAESTRO Phase 3 agentic patterns | ICE 18; benefits from #141 in place so patterns can intersect with chains | 2-3 weeks | After #141 ideally; independent of #82 |
| 10 | [#145](https://github.com/davidmatousek/tachi/issues/145) MAESTRO canonical worked example | Headline demonstration artifact; value multiplied by #141 being visible in output | ~1 week | After #141 strongly preferred; after #136 required |

### Wave 5 — Market differentiators and nice-to-haves (weeks 9+, opportunistic)

| Order | Issue | Why here | Effort | Notes |
|-------|-------|----------|--------|-------|
| 11 | [#55](https://github.com/davidmatousek/tachi/issues/55) Security Progression Summary | ICE 19; unique market differentiator (no other threat modeling tool has multi-run comparison); needs multi-run data to demo | 2-3 weeks | Standalone — can slot anywhere after Wave 0 |
| 12 | **Re-scope check on [#69](https://github.com/davidmatousek/tachi/issues/69)** vs [#145](https://github.com/davidmatousek/tachi/issues/145) | Fold into #145 if scope overlaps; close-as-duplicate if redundant | 1 hour investigation | After #145 |
| 13 | [#126](https://github.com/davidmatousek/tachi/issues/126) Auto-detect architecture drift | Currently a stub — no body, no ICE; needs `/aod.validate 126` to score before sequencing | Unknown — needs scoping | Independent |
| 14 | [#62](https://github.com/davidmatousek/tachi/issues/62) Custom brand presets | Currently a stub — no body; UX nicety; could potentially consolidate with #46 upstream sync if upstream has related work | Small | Independent |
| 15 | [#46](https://github.com/davidmatousek/tachi/issues/46) Sync upstream AOD Kit | Maintenance sync; 9 new files plus 21 differing files; not urgent but debt compounds with every upstream release | 1-2 weeks | Schedule on a quarterly cadence |

---

## Dependency Graph

```
#130 [DONE 2026-04-11] ─── independent, shipped first (v4.10.1, ADR-022 authored)

#136 [DONE 2026-04-11] ─┬─ #141 [DONE 2026-04-12] ─┬─ #142 (UNBLOCKED)
                        │                          ├─ #145 (UNBLOCKED)
                        │                          └─ #98 (RE-SCOPE NOW — may be subsumed)
                        ├─ #142 (UNBLOCKED — canonical layers + chains in place)
                        └─ #145 (UNBLOCKED — canonical layers + chains in place)

#82 [DONE 2026-04-12] ─── #129 [DONE 2026-04-14] ─── (Wave 2 closed)

#143 ─┬─ pair (overlapping research phase) — RECOMMENDED NEXT
#144 ─┘

#55, #126, #62, #46 ─── all independent
#69 ─── overlaps #145, re-scope after #145 lands
```

**Waves 0, 1, 2 fully delivered** — all 5 prerequisite items closed by 2026-04-14. Wave 3 (#143 + #144 ADR pair) is the recommended next item. Wave 4 (#142, #145, #98 re-scope) follows.

---

## Cross-Reference Maintenance Actions

Before starting implementation, post the following comments on GitHub to prevent duplicate work and to surface blockers to future contributors.

### Post to #98

> **Scope overlap flag**: Issue #141 (MAESTRO Phase 2 cross-layer attack chain analysis) may partially or fully subsume this issue. Cross-layer chains will necessarily expose which MAESTRO layers have findings. Do not start work on #98 until #141 ships; at that point, re-evaluate whether this issue closes as duplicate or shrinks to a small follow-on.

### Post to #69

> **Scope adjacency flag**: Issue #145 (MAESTRO canonical worked example) adds a new example purpose-built to demonstrate seven-layer coverage. Re-scope this issue after #145 ships to determine whether the remaining "broader test coverage" intent still justifies a standalone feature or whether #145 covers it.

### Run on #126 and #62

Both issues are currently stubs with no body and no ICE score. Run:

```bash
/aod.validate 126
/aod.validate 62
```

to capture body, evidence, and ICE scoring before sequencing them into a wave.

---

## Risks and Anti-Patterns to Avoid

**Do not parallelize #82 and #129.** The threat-report.md file conflict is real and will cost more in merge pain and cognitive overhead than the sequencing costs in wall-clock time. Hold the line on Wave 2 waiting for #82.

**Do not start #145 before #141.** The worked example depends on Phase 2 cross-layer attack chains being visible in output. Shipping #145 before #141 means regenerating it after #141 lands, doubling the work.

**Do not ICE-sort the backlog and execute from the top.** #143 has ICE 22 which is higher than #141 ICE 20, but #141 is the defining MAESTRO capability and #143 is a documentation-only ADR. ICE is a starting heuristic, not a schedule. The wave structure in this document accounts for dependencies, strategic value, and parallelism opportunities that ICE cannot capture.

**Do not let MAESTRO items crowd out #82 and #130.** The backlog has six MAESTRO items because we just did a compliance audit on 2026-04-10. That is intentional capture, not intentional prioritization. #130 is a P0 validated bug affecting every adopter, and #82 is the foundational quality lift for every future threat agent improvement. Neither should be delayed by MAESTRO enhancements.

**Do not schedule #46 AOD sync reactively.** The upstream sync accumulates debt with every upstream release — currently 9 new files plus 21 differing files. Set a quarterly cadence and stick to it rather than waiting for a pain point to force the sync.

---

## Revision Notes

This plan is a snapshot as of 2026-04-10. Re-generate or revise when:

- A wave completes and new issues land in Discover
- ~~#130 ships (unblocks flagship "show to exec board" use case on fresh installs)~~ **Triggered 2026-04-11 — PR #148, v4.10.1, ADR-022 authored, precedent set for future CLI-prerequisite enforcement**
- ~~#136 ships (several downstream items become actionable)~~ **Triggered 2026-04-11 — #141, #142, #145 now actionable**
- **Wave 0 fully delivered 2026-04-11** — both correctness fixes closed same day
- **Wave 1 fully delivered 2026-04-12** — #82 (68 tasks, 18 waves) and #141 (34 tasks, 7 waves) both shipped same day. All foundation work complete. Waves 2-5 are now the active frontier.
- ~~#141 ships (re-scope #98 and #69; #142 and #145 become high-priority)~~ **Triggered 2026-04-12 — PR #159, #142 and #145 now high-priority, #98 re-scope actionable**
- ~~#82 ships (#129 becomes unblocked)~~ **Triggered 2026-04-12 — #129 now unblocked, Wave 2 is actionable**
- ~~#129 ships (closes Wave 2)~~ **Triggered 2026-04-14 — PR #162, ~1 day wall-clock; sidecar PR #164 fixed cwd auto-detection bug across four tachi commands. Wave 3 (#143 + #144 ADR pair) is the recommended next item.**
- **Wave 2 fully delivered 2026-04-14** — Wave 3 ADR pair is the active frontier; Wave 4 (#142, #145, #98 re-scope) follows.
- A critical bug enters the backlog that pre-empts Wave 0

Source of truth is always GitHub Issues, not this file or BACKLOG.md.
