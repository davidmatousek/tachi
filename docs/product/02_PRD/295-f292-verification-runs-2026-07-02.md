---
prd:
  number: 295
  topic: f292-verification-runs
  created: 2026-07-02
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-07-02, status: APPROVED, notes: "PM author — v1.1 folds full Architect correction set (H1-H3, M1-M4, L1-L3) + Team-Lead concerns; v1.2 folds re-review residuals M-a/L-a as plan-stage notes; issue #295 ACs preserved; fail-closed semantics with false-pass guard"}
  architect_signoff: {agent: architect, date: 2026-07-02, status: APPROVED_WITH_CONCERNS, notes: "v1.0 CHANGES_REQUESTED (3H/4M/3L) → v1.1 all 10 findings verified folded → APPROVED_WITH_CONCERNS (0H/1M/1L residual, plan-altitude, non-blocking): M-a single-agent↔SARIF seam — plan.md must state which path yields the comparison SARIF; L-a AC-2e before/after regen semantics. Details: .aod/results/architect.md"}
  techlead_signoff: {agent: team-lead, date: 2026-07-02, status: APPROVED_WITH_CONCERNS, notes: "0H/2M/3L. Estimate 0.5/1.0/2.0 eng-days independently derived (ICE Effort=2 was optimistic); 1 serial build wave, security-analyst LEAD → tester; no parallel tachi runs (shared orchestrator context). M-1 overflow escape hatch + M-2 US-3 optional-on-T026-success folded. Details: specs/295-f292-verification-runs/feasibility-check.md"}
source:
  idea_id: 295
  story_id: null
---

# F-292 Post-Merge Verification Runs (T017 + T026) — PRD (Quick Start)

**Status**: Approved (v1.2 — Architect re-review APPROVED_WITH_CONCERNS; residuals M-a/L-a folded as plan-stage notes)
**Created**: 2026-07-02
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (BLP-06 Wave 3 — maintenance/consolidation tail; last open work item besides deferred #325)
**Source**: [Issue #295](https://github.com/davidmatousek/tachi/issues/295) (type:retro — F-292 post-merge tail, parent [#292](https://github.com/davidmatousek/tachi/issues/292))

## Problem

F-292 (Output-Integrity Cross-Sink Refinement) shipped 2026-05-14 (PR #293, squash `0629fa2`, v4.36.0) with two success criteria left **empirically unverified**: both require user-initiated `tachi.threat-model` skill invocations that cannot run autonomously from `/aod.build` or `/aod.deliver`. Per KB Entry 7, they were deferred to dedicated Issue #295 (tasks T017 + T026 marked `[X]`-deferred in `specs/292-*/tasks.md`):

- **SC-003 (T017)**: the Gap 3 Cross-Agent Handoff Sinks cross-link prose is *claimed* navigational-only (no new `output-integrity` emissions on multi-agent baselines, per `contracts/cross-link-no-emission-contract.md`), but the §3 verification diff was never run or logged.
- **SC-015 (T026)**: `examples/multi-tenant-rag-app/` is listed in `examples/README.md` as *the* Cat 6 (Vector/Search-DSL Injection) trigger fixture, yet ships **only `architecture.md`** — zero committed evidence it actually emits a Cat 6 finding, unlike every other listed example (`web-app/` etc. carry committed `threats.md`).

Verified current state (PM code-read 2026-07-02; load-bearing claims independently re-verified by Architect review):
- The `/tmp` captures prescribed by contract §3 are gone; 7 weeks and 10 releases (v4.37–v4.46) have passed. **Pre-292 anchors survive in git history**: `git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif` and `git show 0629fa2~1:examples/agentic-app/threats.md` — both carrying the same **4 distinct OI findings** (OI-1..OI-4; threats.md shows 8 `| OI-` rows because each finding appears in two tables).
- **The documented verification procedure is itself broken** (Architect review discovery, 2026-07-02): contract §3's extraction filter `select(.ruleId | startswith("OI-"))` matches **zero** results on the real anchor SARIF — ruleIds are `tachi/ai/llm`-style; the OI identifiers live at `results[].partialFingerprints["findingId/v1"]`. Run as documented, T017 would have diffed empty-vs-empty and **false-passed**. This latent defect survived precisely because T017 was deferred — executing the verification correctly is now *more* justified, not less.
- The committed `examples/agentic-app/` artifacts were fully regenerated 2026-06-02 (`ac07085`, F-098 MAESTRO — post-292) and still carry the same 4 OI findings — informal evidence the invariant held, but never verified at OI-subset content level nor logged as SC-003 closure.
- Intervening features legitimately touched output surfaces: F-260b asset tags (current SARIF carries `affected_assets`; the 2026-05 anchor does not), F-098/#311 MAESTRO annotations, #184–#186 crosswalk expansions. A naive whole-object byte-diff against the stale anchor is structurally noisy.

## Solution

Execute the two deferred verification runs with **honest, achievable verification semantics**, produce durable records, and add a purpose-built reproducibility check for the new baseline:

1. **T017 (SC-003)** — **primary path: single-agent run** — dispatch only the `tachi-output-integrity` agent against `examples/agentic-app/architecture.md` (OI findings are owned solely by that agent; the prose under test lives only in `output-integrity.md` + its `detection-patterns.md`). This sidesteps orchestrator context-overflow entirely — no 14-agent dispatch, no correlation phase, no narrative. *Fallback*: scoped full run (SARIF + threats.md, narrative phase skipped). Extract the OI-scoped subset with the **corrected** filter (see Verification Semantics), diff against the pre-292 git-history anchor, attribute any delta, log SC-003 closure. *Escape hatch (Team-Lead M-1)*: if two run attempts fail on tooling grounds, file the tooling defect and close with the staged-partial record — the feature cannot run open-ended.
2. **T026 (SC-015)** — full pipeline on `examples/multi-tenant-rag-app/architecture.md` (**multi-agent**: LLM Query Synthesizer + LLM Answer Generator + RAG Retriever; 7 small components / 101 lines — overflow risk genuinely low; staged per-skill invocations as fallback) under `SOURCE_DATE_EPOCH=1700000000`. Artifact authoring tiers (matches production reality): `threats.md`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif` are committed as **LLM-authored** artifacts; `threats.sarif` is **script-generated** from the committed `threats.md` via `generate-threats-sarif.py` — so its byte-identity claim is structural, not aspirational.
3. **Durable reproducibility check (US-3)** — a **purpose-built SARIF-regen byte-identity test**: run `generate-threats-sarif.py` on the committed `examples/multi-tenant-rag-app/threats.md` under `SOURCE_DATE_EPOCH=1700000000` and assert byte-identity against the committed `threats.sarif`. **Explicitly NOT `BASELINE_EXAMPLES` membership**: that suite enforces *PDF* byte-identity (each member requires a committed `security-report.pdf.baseline` — excluded from this feature's scope) and its F-142 multi-agent-gate test asserts every finding carries `agentic_pattern: none`, which a multi-agent RAG example rightly cannot satisfy (mermaid-agentic-app is already skip-carved for the same reason). Honest durability rationale: an uncovered reproducibility claim can decay; this check covers exactly the claim SC-015 makes, no more.

**Enabler (in scope, Architect-endorsed)**: `generate-threats-sarif.py:481` hardcodes `"uri": "examples/agentic-app/sample-report/threats.md"`; derive the URI from the input path (~1-line change + covering assertion) so the new example's SARIF is not semantically mislabeled. This is a prerequisite for *executing* the verification, not a verification-failure fix — the fix-vs-file boundary below applies to what the runs *discover*, not to enablers the runs *require*.

**Verification semantics (fail-closed, false-pass-guarded)**:
- **Corrected OI extraction (supersedes contract §3)**: `jq '.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))'`. The SARIF `partialFingerprints["findingId/v1"]` set is the **authoritative anchor**; `threats.md` OI rows are the human-readable cross-check. A defect is filed against contract §3's broken filter (fix-vs-file — it is a committed artifact carrying a non-working procedure).
- **False-pass guard**: the extracted OI subset MUST be non-empty on *both* sides before any diff is trusted — expected cardinality **4 distinct OI findingIds** per the anchor. An empty extraction is a gate ERROR (broken filter/run), never a PASS.
- **Hard gate = emission-level identity (named decision D-1, Architect-blessed)**: FR-007's "count or content" is operationalized as {**OI finding count, findingId set, per-finding sink/flow identity**}. Other finding fields (severity, CWE list, message prose, `affected_assets`, MAESTRO annotations) are relegated to the attributable-drift bucket *by design* — they legitimately drift via #184–#186 crosswalk, F-098/#311 MAESTRO, and F-260b asset tags. Any non-identical delta in the gate fields, or any byte-delta not attributable to a named intervening commit/feature, **fails the gate** (fail-closed).
- **Byte-identity is claimed only where it is structural**: SC-015 clause b narrows to `threats.sarif` — regenerable byte-identically from `threats.md` by script. `risk-scores.sarif` carries **no regen claim**: `generate-risk-scores-sarif.py` has no CLI, reads hardcoded agentic-app paths, and gates on `>=80` findings — a 7-component example cannot clear it. Parameterizing that generator is net-new work, filed as a follow-up enhancement, not smuggled into this feature.
- **Fix-vs-file boundary**: these runs *assess*. Any verification failure (F-292-attributable emission delta, missing Cat 6 finding, non-reproducing artifact) is filed as a new defect Issue with the evidence — never fixed inline under #295.

## User Stories

1. **US-1 (P0, T017/SC-003)** — When I maintain the `output-integrity` agent after F-292's cross-link prose landed, I want the no-emission invariant verified empirically on the contract's named fixture, so SC-003 stops being an untested claim and future detection-pattern edits inherit a logged, *working* procedure for scoped no-emission verification.
   - AC-1a: Given current HEAD, when the `tachi-output-integrity` agent runs single-agent against `examples/agentic-app/architecture.md` (scoped full run as fallback) under `SOURCE_DATE_EPOCH=1700000000`, then the run completes and the corrected extraction (`partialFingerprints["findingId/v1"]` filter) yields a **non-empty** OI subset — expected 4 findingIds; an empty extraction is a gate ERROR, not a pass. *Plan-stage note (Architect M-a)*: the single-agent path emits findings text, not a SARIF — plan.md MUST state which path yields the comparison SARIF (a SARIF-generation step over the assembled findings, or the scoped-full fallback's native SARIF).
   - AC-1b: Given the pre-292 anchor (`git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif`, OI subset extracted with the same corrected filter), when the fresh OI subset is diffed against it, then OI finding count (4), findingId set, and per-finding sink/flow identification are identical (hard gate per D-1), and byte-level deltas (if any) are each attributed to a named intervening commit/feature; zero deltas remain attributable to F-292 prose.
   - AC-1c: Given the diff outcome, when verification concludes, then a durable SC-003 verification record (commands, anchor SHAs, corrected filter, diff result, attribution table) is committed and linked from Issue #295, and the Issue AC checkbox for T017 is checked.
   - AC-1d: Given a delta attributable to F-292 (or unattributable), when the gate fails, then a defect Issue is filed with the evidence and #295 records the failure honestly — no inline fix, no silent pass.
   - AC-1e: Given contract §3's broken extraction filter (matches zero results on the real SARIF shape), when US-1 lands, then a defect Issue is filed against the contract documenting the corrected filter (disposition of the archived artifact decided there).

2. **US-2 (P0, T026/SC-015)** — When I browse `examples/multi-tenant-rag-app/` as an adopter evaluating tachi's Cat 6 coverage, I want committed pipeline artifacts demonstrating the vector/search-DSL injection finding, so the flagship F-292 fixture shows expected output like every other listed example instead of an architecture file with no evidence.
   - AC-2a: Given current HEAD, when the pipeline runs over `examples/multi-tenant-rag-app/architecture.md` under `SOURCE_DATE_EPOCH=1700000000`, then at least one `output-integrity` finding under the Cat 6 pattern surface is emitted (SC-015 clause a; expected shape: LLM-synthesized Pinecone metadata filter omitting the `tenant_id` clause, CWE-943 primary).
   - AC-2b: Given the run output, when artifacts are committed, then the set is: `threats.md`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif` (LLM-authored) + `threats.sarif` (script-generated from the committed `threats.md` via the URI-corrected `generate-threats-sarif.py`).
   - AC-2c: Given the committed artifacts, when `generate-threats-sarif.py` re-derives `threats.sarif` from `threats.md` under `SOURCE_DATE_EPOCH=1700000000`, then the result is byte-identical to the committed file (SC-015 clause b, narrowed to the structurally regenerable artifact). `risk-scores.sarif` carries no byte-identity claim (generator gap filed as follow-up enhancement).
   - AC-2d: Given `examples/README.md`, when artifacts land, then the existing `multi-tenant-rag-app` row (SC-015 clause c — already listed) remains accurate (component count 7, Cat 6 trigger description).
   - AC-2e: Given the URI enabler, when `generate-threats-sarif.py` derives the source URI from its input path, then the new example's SARIF references `examples/multi-tenant-rag-app/threats.md` (not agentic-app), a covering assertion exists, and agentic-app regeneration output is byte-unchanged — compared **script-output-before vs script-output-after** the URI change (Architect L-a: never vs the LLM-authored committed SARIF, which is a different authoring tier).

3. **US-3 (P1, durable reproducibility check — optional-on-T026-success)** — When a future change touches the threats-SARIF generator or the committed baseline, I want a purpose-built byte-identity test covering the multi-tenant-rag-app regen claim, so SC-015 clause b is CI-checked instead of decaying as an unenforced one-time claim.
   - AC-3a: Given the committed `threats.md` + `threats.sarif` pair, when the new test runs `generate-threats-sarif.py` under `SOURCE_DATE_EPOCH=1700000000`, then it asserts byte-identity and is green in the standard pytest invocation.
   - AC-3b: Given the check lands, then the PR body states what the test covers (SARIF-regen byte-identity for this baseline only) and what it deliberately does not (PDF byte-identity, `BASELINE_EXAMPLES` membership — see Scope Out), so the maintenance surface is explicit.
   - AC-3c (structural gate, Team-Lead M-2): US-3 proceeds only if AC-2c passes; a T026 gate-failure defers US-3 to the follow-up defect Issue without counting as a US-3 failure.

**Issue #295 acceptance mapping**: T017 checkbox → US-1 (AC-1a–AC-1c); T026 checkbox → US-2 (AC-2a–AC-2c). US-3 is this PRD's durability addition (defer-able per AC-3c without breaking issue closure).

## Success Metrics

- **SC-1 (SC-003 closure)**: F-292-attributable OI-subset deltas on `agentic-app`: unknown → **0**, verified with a non-empty 4-findingId extraction on both sides and a committed verification record. (Ideal outcome: byte-identical OI subsets; minimum: gate-field identity with full drift attribution.)
- **SC-2 (SC-015 clause a)**: committed evidence of a Cat 6 `output-integrity` finding on `multi-tenant-rag-app`: 0 artifacts → ≥1 finding in committed `threats.md`/`threats.sarif`.
- **SC-3 (SC-015 clause b, narrowed)**: `threats.sarif` deterministic-regen byte-identity: unverified → verified, and CI-enforced by the purpose-built check if US-3 lands.
- **SC-4 (initiative closure)**: Issue #295 both ACs checked; BLP-06 Wave 3 work items complete (only deferred #325 tail remains in the initiative).

## Scope

**In (P0)**: T017 single-agent verification run (scoped-full fallback; 2-attempt escape hatch) + corrected-filter OI-subset diff vs git-history anchor + fail-closed attribution + committed verification record; T026 pipeline run + artifact commit per authoring tiers + `threats.sarif` regen verification; the ~1-line `generate-threats-sarif.py` URI derivation + covering assertion (enabler); defect filings: contract §3 broken filter (AC-1e), any gate failure (AC-1d), `generate-risk-scores-sarif.py` parameterization gap (follow-up enhancement).
**In (P1)**: US-3 purpose-built SARIF-regen byte-identity test; `examples/README.md` row accuracy check.
**Out**:
- **`BASELINE_EXAMPLES` membership for `multi-tenant-rag-app`** — the suite is PDF byte-identity (requires a `security-report.pdf.baseline`, itself out of scope) and its F-142 multi-agent-gate test would redden on a multi-agent example (mermaid-agentic-app precedent: skip-carved). Revisit only if a PDF baseline is ever added.
- `security-report.pdf.baseline` / infographic / report-assembly tier for `multi-tenant-rag-app` (Gemini API dependency, non-deterministic image bytes).
- `risk-scores.sarif` regen verification / parameterizing `generate-risk-scores-sarif.py` (no CLI, hardcoded paths, `>=80`-finding gate — net-new generator work; filed as enhancement).
- `maestro-reference` counter-test (contract §6 optional secondary fixture; 18 components — overflow territory; SC-003's letter names `agentic-app`).
- `compensating-controls` artifacts for the new baseline (needs a target codebase scan; the example ships an architecture description only).
- Any inline fix to `detection-patterns.md`, agent files, or the archived contract if verification fails (fix-vs-file — new Issue).
- Backfilling or re-verifying `agentic-app` committed baseline artifacts (already regenerated 2026-06-02 under F-098).

## Timeline

Derived from the team-lead estimate in `specs/295-f292-verification-runs/feasibility-check.md` (`estimate.planning_days`): **1.0 eng-day central (0.5 floor / 2.0 ceiling)**, independently derived bottom-up (~0.7–0.75d attention + one snag; ICE Effort=2 judged optimistic). Single serial build wave — security-analyst leads T017 then T026; tester owns US-3; no parallel tachi runs (shared orchestrator context). v1.1 scope deltas offset within the central estimate: T017's single-agent primary path (M3) *removes* the dominant overflow re-run driver the ceiling was priced for, while US-3's purpose-built test + the 1-line URI enabler add modest bounded work in exchange. Dev Complete target: 1 attention-day from plan approval (wall-clock may exceed one calendar day on async re-runs — Team-Lead L-1).

## Risks

- **R-1 Anchor staleness / drift misattribution**: 7 weeks of legitimate output-surface changes (asset tags, MAESTRO annotations, crosswalk growth) produce byte-deltas a naive diff would misread. *Mitigation*: emission-level hard gate (D-1) + per-delta attribution to named commits (bounded walk over ~3 feature-classes via `git log -p 0629fa2..HEAD -- <surface files>`) + fail-closed rule. Anchor is git-history-pinned.
- **R-2 False-pass (new, Architect H1 class)**: a broken extraction filter diffs empty-vs-empty and reports PASS — the worst outcome for a verification feature. *Mitigation*: corrected filter specified in the ACs; non-empty guard with expected cardinality 4 pinned on both sides; contract defect filed so the broken procedure cannot be reused.
- **R-3 Orchestrator context overflow**: known constraint on complex archs. *Mitigation*: T017 primary path is a single-agent (output-integrity-only) run — no orchestrator fan-out at all; scoped full run as fallback; 2-attempt escape hatch files a tooling defect rather than running open-ended. T026's arch is small (7 components); staged per-skill invocations as fallback.
- **R-4 LLM-run nondeterminism**: fresh pipeline output is LLM-authored; prose-level byte-identity across a 7-week gap is not structurally guaranteed. *Mitigation*: gate on emission-level fields (D-1) for the fresh-run diff; byte-identity claimed only for the script-regenerable `threats.sarif`.
- **R-5 Verification failure discovered**: a real F-292-attributable emission, a missing Cat 6 finding, or a non-reproducing artifact would fail the gates. *Mitigation*: defect-filing protocol (AC-1d/AC-2c); #295 closes honestly with the record either way — the deliverable is the *verification*, not a green result.
- **R-6 Scope-creep pressure at the generator seam**: the risk-scores generator gap invites "just parameterize it while we're here." *Mitigation*: explicit Out item + filed enhancement; the only in-scope generator change is the 1-line URI derivation with a covering assertion (AC-2e).

## Open Questions

- [x] OQ-1: T017 anchor choice — **Answered 2026-07-02 (Architect)**: `git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif` ratified as authoritative anchor (immediate parent of the F-292 squash); `threats.md` (4 findings across 8 rows) as human cross-check; `test-output/` dated captures are partial (2026-04-23 holds OI-4 only). Extraction MUST use the corrected `partialFingerprints` filter.
- [x] OQ-2 + OQ-3 (resolved jointly per Architect L3): US-3 enforcement surface and T026 artifact tier — **Answered 2026-07-02 (Architect Option A)**: purpose-built SARIF-regen byte-identity test; `BASELINE_EXAMPLES` join rejected (PDF-suite false premise + F-142 gate). Artifact tier: `threats.md`/`threat-report.md`/`risk-scores.md`/`risk-scores.sarif` LLM-authored + `threats.sarif` script-generated (regen-verified); no PDF baseline.
- [ ] OQ-4: Disposition of the archived contract §3 (annotate vs correct the archived F-292 artifact) — decided in the AC-1e defect Issue. — Owner: Architect — Due: defect-Issue triage — Status: Open (does not block this feature)
- [ ] OQ-5 (Architect M-a residual): Which T017 path yields the comparison SARIF — the single-agent run emits findings text (the agent has Read/Glob/Grep only, no SARIF emission); options are a SARIF-generation step over the assembled findings or the scoped-full fallback's native SARIF. — Owner: Architect — Due: /aod.plan — Status: Open (non-blocking for PRD)

## References

- [Issue #295](https://github.com/davidmatousek/tachi/issues/295) · parent [#292](https://github.com/davidmatousek/tachi/issues/292) · PR #293 (squash `0629fa2`, v4.36.0)
- Contract: `specs/292-output-integrity-cross-sink-refinement/contracts/cross-link-no-emission-contract.md` (§3 procedure — extraction filter defective per Architect review 2026-07-02; §6 counter-tests)
- Spec anchors: F-292 SC-003 (`specs/292-*/spec.md:179`), SC-015 (`specs/292-*/plan.md:238`, M-3 resolution), T017/T026 (`specs/292-*/tasks.md:108,153`)
- Generators: `scripts/generate-threats-sarif.py` (argparse input/output; hardcoded URI at :481 — AC-2e enabler), `scripts/generate-risk-scores-sarif.py` (no CLI; hardcoded paths :39–41; `>=80` gate — Out, filed)
- Suite reality: `tests/scripts/test_backward_compatibility.py:45` (`BASELINE_EXAMPLES` = PDF byte-identity, 6 members), `:375` (F-142 multi-agent-gate test; mermaid-agentic-app skip precedent :383–397)
- Fixtures: `examples/agentic-app/` (regen 2026-06-02 `ac07085`), `examples/multi-tenant-rag-app/architecture.md` (created at `0629fa2`), `examples/README.md:15`
- Reviews: `.aod/results/architect.md` (v1.0 CHANGES_REQUESTED 3H/4M/3L — all folded; v1.1 re-review APPROVED_WITH_CONCERNS, residuals M-a/L-a plan-altitude), `specs/295-f292-verification-runs/feasibility-check.md` (Team-Lead, 0.5/1.0/2.0)
- Institutional: KB Entry 7 (post-merge deferral pattern); orchestrator context-limit note (F-292-era verification runs); output authoring tiers (production threats.md + SARIFs are LLM-authored; `generate-*-sarif.py` are regeneration-only)
- Governance: `.aod/memory/constitution.md`; `.claude/rules/code-economy.md` (one runnable check → US-3; rung 1 → R-6)
- Initiative: BLP-06 integrity & hardening — Wave 3 (final work item; #325 tail separately deferred)

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-07-02 | PM author — v1.1/v1.2 fold both reviewer correction sets + re-review residuals; issue ACs preserved; false-pass guard added |
| Architect | architect | 🟡 Approved with Comments | 2026-07-02 | v1.0 CHANGES_REQUESTED (3H/4M/3L) → v1.1 all findings verified folded → APPROVED_WITH_CONCERNS; residuals M-a (comparison-SARIF path → OQ-5) + L-a (AC-2e semantics, folded); details `.aod/results/architect.md` |
| Engineering Lead | team-lead | 🟡 Approved with Comments | 2026-07-02 | Estimate 0.5/1.0/2.0 independent; serial single wave; M-1 escape hatch + M-2 US-3 gate folded; details `specs/295-f292-verification-runs/feasibility-check.md` |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending
