---
feature: 206-misinformation-threat-agent
artifact: delivery.md
author: senior-backend-engineer (via /aod.build T057)
date: 2026-04-24
status: Authored pre-merge — finalize post-squash with merge metadata
pr: https://github.com/davidmatousek/tachi/pull/207
triad_signoff:
  pm: APPROVED (2026-04-23, tasks.md frontmatter)
  architect: APPROVED (2026-04-23, tasks.md frontmatter)
  techlead: APPROVED (2026-04-23, tasks.md frontmatter)
---

# Delivery Retrospective — Feature 206 `misinformation` Threat Agent

**BLP-01 Tier 1 F-2** (2nd Tier-1 feature after F-1 Feature 201 `output-integrity`) closing OWASP LLM09:2025 Misinformation on the Coverage Matrix.

## Duration — Estimated vs Actual

| Dimension | PRD / Plan Estimate | Actual | Delta |
|-----------|---------------------|--------|-------|
| Calendar envelope | Mon 2026-04-27 → Wed 2026-04-29 (2 days + buffer) | Thu 2026-04-23 18:25 → Fri 2026-04-24 09:37 | **~3–4 days ahead of schedule** |
| Session count | 2 working days | 2 sessions (Thu PM / Fri AM) | Matches |
| Active work hours | ~16 hours (2 × 8h days) | ~10–12 hours elapsed | **~30% under** |
| Wave count | 6 waves (1.0, 1.1, 2, 3, 4, 5, 6) | 6 waves (same decomposition) | Matches |
| Task count | 62 tasks | 57/62 complete pre-merge; 5 post-merge/contingent | Matches |
| Buffer consumption | Wednesday 2026-04-29 allocated | Buffer untouched (R2 not fired, no regen friction) | Headroom preserved |

The delivery substantially beat the PRD envelope. Two factors drove compression:

1. **F-1 precedent reuse** — the 6-wave structure, ADR template, schema-bump protocol, quintet-reconciliation edit pattern, and pipeline regen sequence were all authored-once at F-1 and re-applied wholesale at F-2. The incremental cost was pattern-catalog authoring (0.5 day) + example regen (2–3 hours) + governance overhead (ADR authoring + SC sweep, ~2 hours).
2. **Clean Wave 4 regen** — byte-identity preserved on all 5 non-factual baselines without re-work; three MI findings surfaced from one architecture extension (Clinical Advisory Sub-Agent Categories 1 + 3 + 4), eliminating any iteration cycle on the emission gate.

## Surprises

### Three MI findings from one architecture extension, not one

The plan anticipated ≥1 MI finding from extending `agentic-app` with a factual-output sub-component. Actual: the Clinical Advisory Sub-Agent extension tripped Categories 1 (Ungrounded Factual Emission), 3 (Overreliance/Missing HITL), and 4 (Retrieval-Grounding Gap) simultaneously. This is a positive signal — a single realistic factual-output surface exercises multiple failure modes — and it validated the three-signal-class discipline (SC-014) more thoroughly than a single-category example would have. The extended architecture also preserved F-1's `OI-4` output-integrity finding and all 5 existing `LLM-{N}` findings, producing a natural three-adjacent-finding rendering (`LLM-{N}`, `OI-{N}`, `MI-{N}`) on the same LLM Process.

### Test-harness fix bundled with feature

`tests/scripts/test_backward_compatibility.py` needed a `DETECTION_AGENT_PATHS` bump (11 → 12) to accommodate the new agent, plus a `--diff-filter=M` scope on the zero-edit invariant check to distinguish modifications from additions (F-2 adds a 13th agent + 13th patterns file as new; the 24 pre-existing files remain byte-identical). This edit is tightly coupled to the agent introduction and was bundled into commit `ec76c00`. A reviewer could legitimately split it into a prep commit, but the coupling argument is strong. Commit-granularity decision worth pre-agreeing at F-3.

### NFR-6 code-review non-blocking suggestion on vendor-category language

Code-reviewer flagged MI-2 mitigation text referencing Westlaw/LexisNexis as illustrative corpus vendors (with "/ equivalent corpus" escape clause) as a non-blocking suggestion. Not an endorsement, not a violation, but a "could be stricter" note. Decision: kept the language as-authored, captured the suggestion in the Wave 5 artifact for future tightening if policy evolves.

### R2 did not fire

The PRD flagged `agentic-app` extend-in-place as carrying cumulative-state risk (F-1 already regenerated the same architecture; F-2 re-regenerates). Actual: byte-identity preserved on all 5 non-factual baselines; `agentic-app` regen produced clean output with no surprise drift on prior F-1 findings. Q4 fallback to new `advisory-app` was not needed. Buffer day preserved.

## Patterns Validated (Two-Execution-Deep: F-1 + F-2)

The following architectural patterns are now validated across two independent detection-agent features and can be treated as **stable** for F-3/F-4/F-5:

| Pattern | Source | F-1 Application | F-2 Application | Verdict |
|---------|--------|-----------------|-----------------|---------|
| Lean-agent shape (≤150 lines, 1 MANDATORY Read, zero MAESTRO) | ADR-023 | `output-integrity.md` 120 lines | `misinformation.md` 120 lines | **STABLE** — scales to 7 AI-tier agents |
| Companion skill catalog with 5 pattern categories | ADR-023 + F-1 convention | `tachi-output-integrity/` 151-line catalog | `tachi-misinformation/` 5-category catalog | **STABLE** — category count is a scope knob, catalog shape is fixed |
| Regex-alternation minor-bump rule | ADR-030 Decision 8 | 1.5 → 1.6 (`OI` prefix) | 1.6 → 1.7 (`MI` prefix) | **STABLE** — 2nd application confirms precedent; F-3 is 3rd application at 1.7 → 1.8 |
| Proposed → Accepted dual-commit ADR | ADR-027/028/029/030/031 | ADR-030 lifecycle | ADR-031 lifecycle (this feature) | **STABLE** — 5 consecutive BLP-01 ADRs conform |
| Additive-only shared-reference edits | ADR-023 Decision 3 | `finding-format-shared.md` consumers list | `finding-format-shared.md` consumers list (2nd consumer insert) | **STABLE** — zero `## ` heading drift, both times |
| F-A2 referential-integrity contract | ADR-028 | 1st producer | 2nd producer | **STABLE** — validator works identically against independent populators |
| Two-part emission gate (keyword + structural indicator) | F-1 FR-011 | sink-presence gate on output-integrity | factual-output-indicator gate on misinformation | **STABLE** — keyword-only dispatch, agent self-gates emission |
| 24-file zero-edit invariant | ADR-023 Decision 2 | 22 → 23 (F-1 adds 1 agent + 1 skill) — actually 22 → 24 via ADR-030 | 24 → 26 (F-2 adds 1 agent + 1 skill) | **STABLE** — invariant scales by +2 per new detection-tier feature |
| Heuristic A signal-class partition | ADR-030 Decision 1 + ADR-031 Decision 2 | stated carve-out (factual-integrity left open) | operationalized with 3rd distinct agent | **STABLE** — three-way partition auditable at vocabulary/CWE/mitigation levels |
| Orchestrator 5-callsite quintet reconciliation | MEDIUM-3 / MEDIUM-4 architect-owned | quartet reconciliation at F-1 | quintet reconciliation at F-2 | **STABLE** — 5-callsite pattern grows +1 callsite touch per feature; architect-owned |

## Lessons for F-3 / F-4 / F-5

### Scheduling

1. **PRD 2-day envelope is conservative**. F-1 and F-2 both compressed. F-3 onward can safely plan a 1.5-day envelope + 0.5-day buffer if F-1/F-2 pattern reuse is honored.
2. **R5 (code-review for NFR-6) belongs at Wave 2.2 PM, not buffer**. HIGH-1 budget model held — 0 blocking violations on 8 examples in ~30 minutes.
3. **HIGH-2 retrospective slotting**: pre-merge authoring is viable (this document authored pre-merge). Defer to buffer only if residual capacity is genuinely absent.
4. **Heuristic A verification memo (T004)**: architect thin-slice ownership (~30 min) is cheap and high-leverage — continue gating Wave 1.1 on it.

### Architecture

5. **One architecture extension can trigger multiple categories simultaneously**. Plan for this at F-3+: pick an architecture extension that exercises ≥3 categories to validate the full pattern catalog in one regen cycle.
6. **Byte-identity preservation is robust when the two-part emission gate is strict**. Keyword-only dispatch with structural-indicator self-gating on emission keeps non-qualifying baselines at zero findings by construction.
7. **Commit-granularity for test-harness bumps**: F-3 will need a 13→14 detection agent bump. Decide upfront whether to split or bundle — coupling argument favors bundling.

### Ledger

8. **MEDIUM-3 quintet → sextet at F-3**. 5-callsite reconciliation pattern extends by +1 touch: each new detection agent adds a 6th agent to orchestrator.md:296 / orchestrator.md:370 / dispatch-rules.md LLM list / dispatch-rules.md:120 / dispatch-rules.md trigger-keyword rules. Architect-ownership (MEDIUM-4) should persist through F-5.
9. **ADR-030 Decision 8 rule boundary is preserved, not extended**. F-3's schema bump (1.7 → 1.8, e.g., adding `TE` for trust-exploitation) is the 3rd application of the same rule — not a new extension. Cite ADR-030 Decision 8 + ADR-031 Decision 8 (2nd-application precedent) when authoring F-3's ADR.
10. **Catalog enrichment follow-ons deferred cleanly**. F-2's Q1 decisions deferred "Model-Specific Hallucination Patterns" and "Feedback-Loop Overreliance" to F-2.1 / F-3 / F-6 scope, preserving the 5-category ship. Similar deferral discipline at F-3+ keeps wave timing tight.

### Quality Gates

11. **SC sweep structure is a reusable template**. T042–T054 delegates ~6 of 13 SCs to prior-wave results (T018, T029, T039, T038, T006, T040) — only ~7 SCs needed fresh grep audits at Wave 5. F-3's SC count will be similar; delegate where earlier waves already verified.
12. **F-A2 validator is regex-agnostic** (`parse_threats_findings` accepts any `id.pattern` match). New prefix additions require zero validator changes. F-3's `TE` prefix onward will inherit this transparently.

## Follow-Ups (non-blocking)

1. **R-8 cross-section dedup in `scripts/tachi_parsers.py`** — defensive dedup patch to `parse_compensating_controls_md()` for R-8's deliberate cross-section placement. Follow-up tachi-tooling PR; not blocking.
2. **Medium-severity attack-tree PNG renders** — `LLM-14`, `MI-1`, `MI-2`, `MI-3` lack `.png` renders because `parse_attack_trees` filters to Critical/High. Not a bug; consistent with existing policy. Manual `mmdc` pass would produce them if desired.
3. **NFR-6 vendor-category language** — Westlaw/LexisNexis mention in MI-2 mitigation is illustrative with escape clause. Acceptable per current policy; tighten if policy evolves.

## Triad Sign-Off Confirmation

The feature inherits triple sign-off from `tasks.md` frontmatter (2026-04-23):

- **PM**: APPROVED — scope, user-value, requirements, SCs all validated
- **Architect**: APPROVED — lean-agent conformance, ADR lineage, quintet reconciliation, F-A2 contract all technically sound
- **Team-Lead**: APPROVED — 62 tasks fit 2-day envelope, critical path no-cycles, parallelization honored

Post-merge close-out chains T025 (ADR SHA fill) + T058 (Coverage Matrix transition) + final polish.

## Post-Merge Actions

- **T025**: Add `{MERGE_DATE} | Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed` row to ADR-031 Revision History
- **T058**: Transition `_internal/strategy/BLP-01-threat-coverage.md` LLM09:2025 row from `**Planned** | New misinformation agent | T1 | TBD (F-2)` to `**Covered** | F-2 (Feature 206) | T1 | {MERGE_DATE}`
- **`/aod.deliver 206`**: Chains T025 + T058 + retrospective finalization (merge metadata fill on this document)

---

**Delivered**: 2026-04-24 — Draft PR #207 open, 57/62 tasks complete pre-merge, 5 tasks post-merge/contingent. F-2 BLP-01 Tier 1 closes LLM09:2025.
