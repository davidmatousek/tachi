---
feature: 082-threat-agent-skill
delivered: 2026-04-11
pr: 151
merge_commit: 6f9a40d
issue: 82
status: delivered
---

# Feature 082 — Delivery Retrospective

**Feature**: Threat Agent Skill References — Externalize Detection Knowledge for All 11 Threat Agents
**Delivered**: 2026-04-11
**PR**: [#151](https://github.com/davidmatousek/tachi/pull/151) (merged via squash, commit `6f9a40d`)
**GitHub Issue**: [#82](https://github.com/davidmatousek/tachi/issues/82)

---

## Definition of Done

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All tasks complete | PASS | 68/68 (66 original + T055a/b/c/d inline + T062/T063 delivery workflow) |
| Triple sign-off on tasks.md | PASS | PM + Architect + Team-Lead APPROVED_WITH_CONCERNS; 4 LOW items addressed inline |
| Phase gates passed | PASS | Phase 1a/1b, Phase 1 Combined, Phase 3 full regression, Phase 6/7 audits, Phase 8 re-baseline |
| Enrichment floor (SC-006) | PASS | +30 new categories vs ≥22 floor = **+8 margin** |
| Shared reference additive-only | PASS | T046 verified; Wave 16 SC-004 remediation removed 22 inline brand-name mentions |
| PDF backward-compatibility | PASS | 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) |
| Full pytest suite | PASS | T061 full regression green |
| Security scan | PASS | T060 complete (commit 6dd9b26) |
| Zero new runtime deps (SC-014) | PASS | Empty diff on pyproject.toml, requirements*.txt, package.json |
| Agent line caps (FR-10) | PASS | STRIDE 50-54 lines (≤120), AI 78-114 lines (≤150) |

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| **Tasks** | 68 total |
| **Waves** | 18 |
| **Estimated effort** | 32h realistic (team-lead bounds: 22h optimistic / 45h pessimistic) |
| **Actual wall-clock** | ~5.4h (first commit 2026-04-11 17:59 EDT → merge 23:22 EDT) |
| **Compression ratio** | ~17% of realistic estimate — **5.9× velocity** |
| **Agents touched** | 11 threat agents + shared refs |
| **New skill directories** | 11 (under `.claude/skills/tachi-<name>/references/`) |
| **New ADR** | 1 (ADR-023 — detection variant of lean-agent pattern) |
| **Enrichment categories added** | 30 (vs ≥22 floor, +8 margin) |

---

## Scope Delivered

### Agent Refactor
- **6 STRIDE agents**: spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation — 113-141 → **50-54 lines**
- **5 AI agents**: prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy — 167-201 → **78-114 lines** (3 were over the 180-line hard cap pre-refactor)
- All 11 agents now load detection patterns at invocation start via a single `**MANDATORY**: Read` directive — no phase-gated loads (new **detection variant** of the lean-agent pattern, sibling to the methodology variant used by control-analyzer)

### Companion Skill Directories
11 new directories under `.claude/skills/tachi-<name>/references/`:
- `tachi-spoofing/`, `tachi-tampering/`, `tachi-repudiation/`, `tachi-info-disclosure/`, `tachi-denial-of-service/`, `tachi-privilege-escalation/`
- `tachi-prompt-injection/`, `tachi-data-poisoning/`, `tachi-model-theft/`, `tachi-tool-abuse/`, `tachi-agent-autonomy/`

Each hosts a `detection-patterns.md` reference file that is byte-preserved from the pre-refactor agent content plus enriched categories.

### ADR-023 (new, Status: Accepted)
`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` — four decisions:
1. Detection variant is a sibling to the methodology variant (second documented lean-agent shape)
2. MAESTRO classification remains orchestrator-owned — zero threat-agent involvement (FR-9 / INV-5)
3. Shared reference edits are additive-only (no infra-agent regressions)
4. `finding-format-shared.md` gains a "For Threat Agents" producer section while preserving existing consumer sections

Cross-refs: ADR-014 (optional external APIs), ADR-020 (MAESTRO classification), ADR-021 (determinism), ADR-022 (CLI prerequisite).

### Enrichment Sources
- OWASP Top 10 2021
- OWASP LLM Top 10 2025 (LLM01-LLM10:2025)
- OWASP AI Exchange
- MITRE ATT&CK v15+
- MITRE ATLAS v5.1+ (including Oct 2025 agent techniques AML.T0058-T0062: context poisoning, memory corruption, agent-in-the-middle, excessive agency runtime, cascading agent failures)
- CWE Top 25 2024
- NIST AI 600-1

### Shared Reference Consolidation (Phase 6)
- `finding-format-shared.md` gains "For Threat Agents" producer section
- Existing consumer sections (Risk Scorer / Control Analyzer / Threat Report) untouched
- OWASP 3×3 risk matrix canonicalized to `severity-bands-shared.md:72` (Unicode ×)
- Wave 16 SC-004 remediation: removed 22 inline "OWASP 3×3" brand-name mentions from agent prose

---

## Phase-by-Phase Gate Outcomes

| Phase | Wave | Gate | Outcome |
|-------|------|------|---------|
| Phase 1a (2-agent regression) | W5 | Architect + Team-Lead | **PASS** (T020) |
| Phase 1b (2-agent enrichment) | W6 | Architect + Team-Lead | **PASS** (T021) — "±2 tolerance interpretation (b)" ruling |
| Phase 1 Combined | W8 | Architect + Team-Lead | **PASS** + ADR-023 → Accepted |
| Phase 3 Full Regression (T050) | W15 | Architect + Team-Lead | **PASS** — 39+ new findings predicted via Option B+ |
| Phase 6 Shared Ref Consolidation (T042-T046) | W12 | — | PASS, additive-only invariant preserved |
| Phase 7 Overlap Audit (T047) | W13 | — | **PASS** |
| Phase 7 Security Review (T048) | W13 | — | CHANGES_REQUESTED → T048a rebuilds |
| Phase 7 Primary-source Rebuilds (T048a) | W13.5 | — | **PASS** — all 5 byte-verbatim |
| Phase 7 Enrichment Tally (T049) | W14 | — | **PASS** — 30 / 22 floor +8 margin |
| Phase 8 Re-baseline (T056/T057) | W17 | — | T056 no-op + T057 agentic-app +8 findings |
| Phase 8 Test Regression (T055d/T061) | W18 | — | **PASS** — full pytest green |

---

## Option B+ Gate Methodology

Phase 1a / 1b and Phase 3 regression gates used **content-equivalence + DFD-vs-pattern matching** rather than live orchestrator invocation. The method was ratified by the T021 joint architect + team-lead gate approval under the "±2 tolerance interpretation (b)" ruling: pre-existing pattern categories must delta=0, new categories can have any non-negative delta from enrichment.

**Ground truth validation**: T057 live regeneration on `agentic-app` (Wave 17) confirmed exactly **+8 new findings** (22 baseline → 30) — consistent with the Option B+ prediction. The paper gate matched reality.

---

## Retrospective

### What Surprised Us
**Velocity — 5.4h actual vs 32h estimate.** Wall-clock from first commit to merge was ~17% of the realistic team-lead estimate, a 5.9× compression. AI-assisted execution within the 18-wave build structure ran many tasks concurrently per wave, and the Option B+ gate methodology (paper gates instead of live regenerations) removed a large amount of wait time that would otherwise have accumulated across Phase 1a/1b/3. The gate methodology was the dominant accelerator.

### Feedback / Follow-ups
**No new ideas** — feature is complete as scoped. All 68 tasks closed, enrichment floor exceeded, all phase gates passed, zero de-scopes carried into Phase 8.

### Key Lesson Learned
**Enrichment — primary-source attribution matters.**

**Why**: T048 security review (Wave 13) flagged 5 detection categories for primary-source realignment. Downstream credibility (the threat-report narrative, compensating-controls analyst recommendations, risk-scorer severity justifications) depends on citing authoritative primaries — OWASP / MITRE / NIST — rather than secondary summaries. T048a (Wave 13.5) rebuilt all 5 byte-verbatim preserving substance, but the lesson is to cite primaries in the *first* draft to avoid the rebuild cycle.

**How to apply**: When adding new pattern categories to any detection skill reference, cite the primary source (OWASP LLM v2025 section ID, MITRE ATLAS technique ID, NIST AI 600-1 subsection) in the same commit as the content. Don't defer attribution to a later review pass.

### Blockers Encountered
- **T048 primary-source gaps** — 5 categories flagged; resolved in Wave 13.5 via byte-verbatim rebuilds (all substance preserved)
- **Wave 16 SC-004 naming** — 22 inline "OWASP 3×3" brand-name mentions survived Phase 6 content extraction because the audit matched on content rather than names; resolved by T051 grep remediation (naming-only diff, zero substance change)

Neither blocker delayed delivery — both resolved in-wave with no downstream impact.

---

## Documentation Updates (Delivery Workflow)

Three documentation agents ran in parallel after merge:

| Agent | Files Updated | Notes |
|-------|---------------|-------|
| product-manager | `docs/product/02_PRD/INDEX.md`, `docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md`, `docs/product/06_OKRs/README.md` | PRD marked Delivered; OKRs Feature Delivery Log updated |
| architect | `docs/architecture/README.md`, `docs/architecture/00_Tech_Stack/README.md`, `docs/architecture/03_patterns/README.md` | ADR-023 referenced; detection variant added to On-Demand Reference File Segmentation pattern (Example 5) |
| devops | (none — no-op) | Content-only refactor; zero DevOps surface area (SC-014 verified empty diff on infra files) |

CLAUDE.md "Recent Changes" entry for Feature 082 was already pre-written during the build phase and verified by architect — no update needed.

---

## References

- Spec: [specs/082-threat-agent-skill/spec.md](spec.md)
- Plan: [specs/082-threat-agent-skill/plan.md](plan.md)
- Tasks: [specs/082-threat-agent-skill/tasks.md](tasks.md)
- ADR-023: [docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)
- PR: [#151](https://github.com/davidmatousek/tachi/pull/151)
- Issue: [#82](https://github.com/davidmatousek/tachi/issues/82)
- Merge commit: `6f9a40d`

---

🤖 Retrospective generated by `/aod.deliver`
