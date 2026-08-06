# Backlog

> Auto-generated from GitHub Issues on 2026-08-06T23:03:58Z.
> Source of truth: GitHub Issues with `stage:*` labels.
> Regenerate: `/aod.status` or `.aod/scripts/bash/backlog-regenerate.sh`

## Discover

| # | Title | ICE | Evidence | Updated |
|---|-------|-----|----------|---------|
| #361 | Extend tachi detection coverage for GhostCommit primitives (encoded exfil, convention-file trust, committed-file dormancy) | Impact: 7, Confidence: 7, Effort: 6 = **20** | Team Observation: coverage mapping of tachi's detection-p... | 2026-07-13 |
| #360 | Harden tachi's own agents against ingested-repo-text prompt injection (GhostCommit self-exposure) | Impact: 8, Confidence: 8, Effort: 8 = **24** | Team Observation: grounded file:line code analysis of tac... | 2026-07-13 |
| #349 | Anthropic jailbreak-severity framework alignment (capability-gain risk lens) | Impact: 6, Confidence: 3, Effort: 8 = **17** (P2) | Team observation — prompted by Anthropic's 2026-07-01 Cla... | 2026-07-01 |
| #346 | Harden read_sidecar against non-dict sidecar member entries (F-329 S-1) | Impact: —, Confidence: —, Effort: — = **Not yet scored** | Retrospective: Emerged during delivery of Feature 329 (OR... | 2026-06-30 |
| #345 | Regenerate init.sh-substitution baseline (tests/fixtures/init-baseline-tree/) — re-tag from #329 | — | — | 2026-06-30 |
| #342 | Deliver-stage preflight: guard against stale/diverged local main and behind-main feature branch | Impact: —, Confidence: —, Effort: — = **Not yet scored** | Retrospective: Emerged during delivery of Feature 338 (Re... | 2026-06-30 |
| #168 | Track OWASP AIVSS v1.0 release and first external adopter case study | Impact: —, Confidence: —, Effort: — = **Not yet scored** | Retrospective: Emerged during delivery of Feature 143 (MA... | 2026-06-01 |
| #126 | Auto-detect architecture drift | | Dimension | Score | Rationale | | — | 2026-05-05 |
| #62 | Custom brand presets — user-definable brand identity via config file | | Dimension | Score | Rationale | | — | 2026-05-05 |

## Define

| # | Title | PRD | Updated |
|---|-------|-----|---------|
| — | *No items in this stage* | | |

## Plan

| # | Title | Spec | Plan | Tasks | Updated |
|---|-------|------|------|-------|---------|
| — | *No items in this stage* | | |

## Build

| # | Title | Progress | Updated |
|---|-------|----------|---------|
| — | *No items in this stage* | | |

## Deliver

| # | Title | Delivered | Retro | Updated |
|---|-------|-----------|-------|---------|
| — | *No items in this stage* | | |

## Document

| # | Title | Status | Updated |
|---|-------|--------|---------|
| — | *No items in this stage* | | |

## Untracked

> These issues have no `stage:*` label. Add a label to track them in the lifecycle.

| # | Title | State | Updated |
|---|-------|-------|---------|
| #362 | Remap OWASP LLM Top 10 coverage to the 2026 edition | OPEN | 2026-08-06 |
| #357 | enhancement: parameterize generate-risk-scores-sarif.py (CLI args, configurable paths, findings-count gate) to support additional example baselines | OPEN | 2026-07-03 |
| #356 | defect(tachi-orchestrator): Phase-3 compilation can absorb output-integrity findings into the LLM-N sequence, dropping the OI- prefix carve-out and CWE citations (F-295 T026 gate FAIL) | OPEN | 2026-07-03 |
| #355 | defect: examples/agentic-app/sample-report/threats.md duplicates output-integrity findings under legacy LLM-5/6/7 and current OI-1/2/3 IDs | OPEN | 2026-07-03 |
| #354 | defect(292): cross-link-no-emission-contract.md §3/§6 — broken ruleId filter + non-executable invocation | OPEN | 2026-07-03 |
| #348 | gitleaks: no default rule covers hex-encoded generic high-entropy secrets | OPEN | 2026-07-01 |
| #333 | Remediate dead citation URLs surfaced by the link-rot monitor (#332) | CLOSED | 2026-06-29 |
| #332 | [link-rot] Taxonomy citation link-rot — open findings | CLOSED | 2026-06-29 |
| #325 | Crosswalk: 4 citation-unsupported tachi-control-category → nist-ai-rmf edges (T029 survivors, Surface B non-table extras) | OPEN | 2026-06-10 |
| #299 | docs: surface /tachi.architecture as the recommended Step 4 path in the Developer Guide | CLOSED | 2026-05-30 |
| #289 | chore: BLP-02 initiative closure tracker (post-5/5 outstanding items + follow-up Issues) | CLOSED | 2026-05-11 |
| #280 | [chore] Pre-commit hook for .claude/settings.json + CLAUDE_PERMISSIONS.md AC-2 cross-check (post-F-4 follow-up) | CLOSED | 2026-07-01 |
| #276 | [chore] release-please manifest-vs-tag discrepancy investigation (post-F-3 follow-up) | CLOSED | 2026-05-10 |
| #275 | [chore] PVR-toggle posture probe (post-F-3 follow-up) | CLOSED | 2026-05-10 |
| #268 | fix: disentangle tachi-scanner from AOD-Kit positioning in .claude/rules/scope.md | CLOSED | 2026-05-07 |
| #266 | fix: retitle CONTRIBUTING.md for tachi (currently labeled 'AOD Kit' with stale clone URL) | CLOSED | 2026-05-07 |
| #264 | feat: adopt dual-frame public positioning (harness reframe) | CLOSED | 2026-05-07 |
