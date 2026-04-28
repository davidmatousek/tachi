# Next Session Handoff — F-6 (Feature 232) ML Top 10 Coverage Bundle

**Branch**: `232-ml-top-10-coverage-bundle`
**Last commit**: `854897c feat(232): Wave 4 invariants — US-2 zero-edit + Disambiguation gate (T038-T041)`
**Progress**: 41/64 tasks complete (64%)
**Waves complete this session**: Wave 3 (model-theft enrichment + walkthrough + fixtures) + Wave 4 (US-2 invariant verification)
**Cumulative waves complete**: Phase 1 verification + Wave 0.0 + Wave 1.0 + Wave 1.1 + Wave 2.1 + Wave 2.2 + Wave 2.3 + Wave 3 + Wave 4 (9 logical waves; 11 of 18 sequential waves per agent-assignments.md)
**Status**: Stopped before heavy Wave 4.0 pipeline regen at coherent breakpoint (under standalone 3-wave ceiling — 2 of 3 used this conversation)

---

## Completed This Session

### Wave 3 — Model-Theft Cat 12/13/14 + Disambiguation + Architect Walkthrough (T026-T037) ✅

- **T026**: model-theft.md metadata 4-line additive append (ML03/ML04/ML06 + AML.T0024); inline `[A,B]` converted to multi-line per F-5 denial-of-service / F-6 Wave 2.1 data-poisoning precedent; pre-existing LLM10:2025 + LLM03:2025 byte-identical
- **T027**: model-theft.md `## Purpose` extension naming predictive-ML extraction (model inversion, membership inference) + predictive-ML artifact supply-chain integrity surfaces alongside existing LLM-extraction (Cat 1-9) and cost-amplification (Cat 10-11 from F-5) surfaces
- **T028**: model-theft.md Detection Workflow Step 5 references list extension with OWASP ML03:2023 + ML04:2023 + ML06:2023 + MITRE ATT&CK T1195 + sub-techniques. Post-edit line count = 105 (target 103-108, well under 150 cap)
- **T029**: Cat 12 — Model Inversion (Predictive ML) authoring. Primary OWASP ML03:2023 + AML.T0024 in references (catalog-resolvable; shared with Cat 13 but disjoint architectural-tells per ADR-035 D-5). 5 indicators (sensitive training data + DP-SGD absent + output-perturbation absent + query-rate throttling absent + extraction-pattern detection absent). Worked example (chest-X-ray classifier black-box optimization). 4 named mitigations (DP-SGD ε ≤ 8.0, output-perturbation noise, query-rate throttling, extraction-pattern detection). Self-review: PASS
- **T030**: Cat 13 — Membership Inference (Predictive ML) authoring. Primary OWASP ML04:2023 + AML.T0024 in references (catalog-resolvable; shared with Cat 12). 5 indicators (confidence values + shadow-model feasibility + label-only mode missing + DP-SGD/truncation absent + training-data minimization not enforced). Worked example (fraud-detection confidence-thresholding). 4 named mitigations (DP-SGD, confidence-output truncation/label-only, query-rate throttling, training-data minimization). Self-review: PASS
- **T031**: Cat 14 — Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering) authoring. Primary OWASP ML06:2023 artifact-side facet per ADR-035 D-4 + MITRE ATT&CK T1195 + T1195.001 + T1195.002 in references (all 4 catalog-resolvable). 5 indicators (no signed-artifact policy + mutable artifact storage + no model-signing + permissive registry IAM + no integrity verification at load). Worked example (MLflow registry compromise via stolen ML-engineering credentials). 4 named mitigations (Sigstore-style attestation, registry IAM with PR review, integrity verification at load time, immutable artifact storage with audit logging). Self-review: PASS
- **T032 (FR-011)**: Pattern Category Disambiguation extension — 4 boundary draws appended after pre-existing F-5 Cat 6/10/11 paragraph: Cat 12 vs Cat 13 (ADR-035 D-5 disjoint architectural-tells with shared AML.T0024); Cat 12/13/14 vs Cat 1-9 (LLM-tier vs predictive-ML topology with disjoint endpoint shapes); Cat 14 vs data-poisoning Cat 10 (ADR-035 D-4 ML06 disjoint architectural-tells with cross-agent surface coexistence); Cat 14 vs Cat 10/11 (artifact-integrity vs economic-attack disjoint topology)
- **T033 (FR-012)**: Primary Sources extension at end of file with 6 new entries (OWASP ML03/ML04/ML06:2023 + MITRE ATT&CK T1195 + T1195.001 + T1195.002)
- **T034 (Architect)**: Integration walkthrough APPROVED — 8 invariants verified PASS at `.aod/results/architect-t034-walkthrough.md` (Cat 10→11→12→13→14 visual continuity post-F-5+post-F-6 confirmed; topology shift from LLM-serving to predictive-ML coherent; ADR-035 D-4 + D-5 carve-outs structurally evident; Heuristic A signal class continuity preserved within model-theft `category: llm` namespace)
- **T035 [P]**: Cat 12 fixture `valid_category_12_model_theft_inversion_finding.yaml` (LLM-12, references = [OWASP ML03:2023, AML.T0024])
- **T036 [P]**: Cat 13 fixture `valid_category_13_model_theft_membership_inference_finding.yaml` (LLM-13, references = [OWASP ML04:2023, AML.T0024])
- **T037 [P]**: Cat 14 fixture `valid_category_14_model_theft_artifact_supply_chain_finding.yaml` (LLM-14, references = [OWASP ML06:2023, T1195, T1195.001, T1195.002])

### Wave 4 — US-2 Invariant Verification (T038-T041) ✅

- **T038 (FR-017 / SC-022)**: schema invariant zero-diff verified — `git diff main HEAD -- schemas/finding.yaml` returns 0 lines (schema_version 1.8 + 12-prefix `id.pattern` alternation byte-identical). F-6 = third BLP-01 detection feature reusing existing prefixes per ADR-035 D-6; second feature with zero schema bump after F-5; first feature with zero schema bump at three-host-file scope
- **T039 (FR-019 / SC-021)**: 22-file zero-edit invariant verified — diff across `.claude/agents/tachi/` + `.claude/skills/tachi-*/references/` returns exactly the 6 F-6 targets (tampering + data-poisoning + model-theft agent files + 3 companion detection-patterns.md files); the 11 NOT-edit agent files (spoofing + repudiation + info-disclosure + denial-of-service + privilege-escalation + prompt-injection + agent-autonomy + tool-abuse + output-integrity + misinformation + human-trust-exploitation) return zero-line diff
- **T040 (FR-018 + FR-020 / SC-025)**: orchestrator + consumers-list + dispatch-rules zero functional edit verified — diff across `finding-format-shared.md` + `orchestrator.md` + `dispatch-rules.md` returns 0 lines
- **T041 (FR-011 / SC-014)**: Pattern Category Disambiguation header presence on all 3 F-6 host companions verified — `^## Pattern Category Disambiguation` grep returns 1/1/1 (data-poisoning + tampering + model-theft companions); FR-011 / SC-014 fully satisfied at three-agent scope

**Wave 3+4 cumulative invariants verified green**:
- model-theft.md = 105 lines (target 103-108, ≤150 cap) ✅
- model-theft companion = 307 lines (211 → 307, +96 across Cat 12 + Cat 13 + Cat 14 + Disambiguation extension + Primary Sources extension) ✅
- Zero MAESTRO references in agent + companion ✅
- 14 Pattern Categories present (Cat 1-14) + 1 Disambiguation header on model-theft companion ✅
- Pattern Category Disambiguation: 3 grep matches across 3 F-6 host companions (FR-011 / SC-014 fully satisfied) ✅
- Cat 12/13/14 + Disambiguation + Primary Sources headers all present at correct positions ✅
- Schema invariant: 0 lines diff (third BLP-01 zero-schema-bump feature) ✅
- 22-file zero-edit invariant: only the 6 F-6 targets diff'd; 11 NOT-edit agent files all clean ✅
- Orchestrator + consumers-list + dispatch-rules: 0 lines diff (zero functional edit preserved) ✅
- All ATLAS + ATT&CK references in 3 new fixtures are catalog-resolvable per F-A2 contract (T0024 catalog-resolvable; T1195 + sub-techniques catalog-resolvable; no prose-only entries in references arrays this wave) ✅

---

## Next Actions — Resume at Wave 4.0

**Wave 4.0 — Predictive-ML-App End-to-End Regen** (Day 2 PM Thu 2026-04-30, ~2 hours)

Tasks (T042 sequential pipeline; T043+T044 verification can begin once T042 emits artifacts; T045 sequential after PDF emits):

- **T042 (FR-014)**: Regenerate `examples/predictive-ml-app/` end-to-end via pipeline:
  ```bash
  cd examples/predictive-ml-app
  SOURCE_DATE_EPOCH=1700000000 /tachi.threat-model
  SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score
  SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls
  SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all
  SOURCE_DATE_EPOCH=1700000000 /tachi.security-report
  ```
  This is the heavy pipeline operation — 5 slash commands sequentially producing threats.md + risk-scores.md + compensating-controls.md + 6 infographic JPEGs + security-report.pdf. Expected ≥6 new ML findings spanning Cat 8/9/10 (D-prefix) + Cat 10 (T-prefix from tampering) + Cat 12/13/14 (LLM-prefix from model-theft) covering 6 closed ML Top 10 items per US-1 acceptance scenarios.

- **T043 [tester]**: Verify aggregate ≥6 new ML findings on `predictive-ml-app/`:
  ```bash
  grep -c "^- id: T-" examples/predictive-ml-app/sample-report/threats.md   # ≥1 (Cat 10 tampering)
  grep -c "^- id: D-" examples/predictive-ml-app/sample-report/threats.md   # ≥1 (Cat 8/9/10 data-poisoning)
  grep -c "^- id: LLM-" examples/predictive-ml-app/sample-report/threats.md # ≥1 (Cat 12/13/14 model-theft)
  ```
  Aggregate ≥6 covering 6 closed ML Top 10 items (SC-019)

- **T044 [tester]**: Verify references-array carries OWASP ML primaries:
  ```bash
  grep -E "OWASP ML0[1-9]:2023|OWASP ML10:2023" examples/predictive-ml-app/sample-report/threats.md  # ≥6 distinct citations
  ```
  ≥6 distinct OWASP ML0X:2023 citations across the 6 closed items (SC-023)

- **T045**: Commit `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` as F-6 mutation target baseline (excluded from byte-identity loop in `tests/scripts/test_backward_compatibility.py` per FR-014; mirrors agentic-app + consumer-agent-app precedent from F-1/F-4)

**Wave 4.1 — Tester Early-Signal Spot-Check (parallel with Wave 4.0; ~1 hour)** — T046-T047

- **T046 [P] [tester]**: Early-signal byte-identity spot-check on `examples/web-app/` — regenerate via pipeline under `SOURCE_DATE_EPOCH=1700000000`; verify `diff -q examples/web-app/sample-report/security-report.pdf examples/web-app/sample-report/security-report.pdf.baseline` returns identical (FR-025 / SC-018; team-lead MEDIUM-3)
- **T047 [P] [tester]**: Early-signal byte-identity spot-check on `examples/maestro-reference/` — regenerate via pipeline; verify byte-identical against baseline (FR-025 / SC-018)

After Wave 4.0 + 4.1, proceed to:

**Wave 5.0 — Tester Full 6-Baseline Verification** (Day 3 AM, ~2 hours) + **Wave 5.1 — Architect ADR-035 Accepted** (~30 min, parallel with 5.0): T048-T049

**Wave 5.2** — Test Infrastructure + Code-Review (~2 hours): T050-T053
**Wave 5.3** — Coverage Matrix Six-Row Update (~30 min): T054
**Wave 5.4** — Triple Sign-Off (~30 min): T055-T058
**Wave 5.5** — Close-Out + Release-Please + Retrospective (~2 hours): T059-T064

---

## Prerequisites Verified

- Branch `232-ml-top-10-coverage-bundle` matches NNN-* pattern ✅
- All three Triad sign-offs APPROVED in tasks.md frontmatter ✅
- agent-assignments.md present ✅
- GitHub Issue #232 stage:build label set ✅
- PR #233 (draft) open with `feat(232): ML Top 10 Coverage Bundle` Conventional Commits title ✅
- Wave 0.0 predictive-ml-app architecture description present and verified at Wave 1.0 architect re-verification ✅
- 4 incomplete checklist items remain bookkeeping only — work migrated to tasks.md/plan.md ✅

---

## Resume Instructions

Start a new conversation and run `/aod.build`:

```bash
claude "Resume F-6 (Feature 232) ML Top 10 Coverage Bundle implementation (branch: 232-ml-top-10-coverage-bundle). Wave 3+4 complete (41/64 tasks, 9 logical waves). Run /aod.build to continue with Wave 4.0 (predictive-ml-app pipeline regen T042-T045) + Wave 4.1 (tester spot-checks T046-T047)."
```

The command will automatically resume from Wave 4.0.

---

## Critical Path Status

```
T007 ✅ → T009 ✅ → T010 ✅ → T011-T015 ✅ → T017-T022 ✅ → T026-T033 ✅ → [NEXT: T042-T045] → T048 → T049 → T054 → T055-T058 → T059
```

**6 of 12 critical-path nodes complete** (T007 + T009 + T010 + T011-T015 + T017-T022 + T026-T033 grouped).

## Risks Active

- **R3 (Day 1 PM authoring quality slip)**: ✅ FULLY MITIGATED — Wave 2.1/2.2/2.3 sequential T-NN-1/2/3 checkpoints all PASSED (Day 1 PM); Wave 3 T-N-1/2/3 model-theft checkpoints all PASSED (Day 2 AM); zero rollback used; team-lead MEDIUM-2 fully discharged
- **R5 (Heuristic A 3-agent emergent issues)**: ✅ FULLY MITIGATED — Both pre-named deferral pair items delivered (data-poisoning Cat 10 = T022 ✅ + model-theft Cat 14 = T031 ✅; both ML06:2023 facets with disjoint architectural-tells per ADR-035 D-4); Heuristic A protocol distinctness preserved at three-host-file scope; T034 architect walkthrough APPROVED 8/8 invariants
- **R10 (ATLAS catalog gap propagation 3x)**: ✅ FULLY MITIGATED — All ATLAS catalog-absent techniques (T0019 + T0031 + T0015) properly omitted from references arrays in 4 fixtures; prose-only fallback consistently applied. Wave 3 fixtures (Cat 12/13/14) used only catalog-resolvable references (T0024 + ML06:2023 + T1195 + sub-techniques) with zero prose-only entries
- **R11 (Wave 4.0 pipeline regen failure)**: NEW ACTIVE — Wave 4.0 requires running 5 slash commands sequentially against `examples/predictive-ml-app/` baseline; if pipeline emits fewer than 6 new ML findings (T043 gate) or missing OWASP ML primaries (T044 gate), the architecture description may need refinement. Mitigation: predictive-ml-app architecture was Wave 0.0-locked at PRD time covering all 6 closed ML Top 10 items with explicit DFD elements per pattern category

## Files Modified This Session

- `.claude/agents/tachi/model-theft.md` (97 → 105 lines, metadata multi-line + Purpose extension + Step 5 references append)
- `.claude/skills/tachi-model-theft/references/detection-patterns.md` (211 → 307 lines, Cat 12 + Cat 13 + Cat 14 + Disambiguation extension + Primary Sources extension)
- `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_12_model_theft_inversion_finding.yaml` (new — 28 lines, LLM-12)
- `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_13_model_theft_membership_inference_finding.yaml` (new — 28 lines, LLM-13)
- `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_14_model_theft_artifact_supply_chain_finding.yaml` (new — 30 lines, LLM-14)
- `specs/232-ml-top-10-coverage-bundle/tasks.md` ([X] marks for T026-T037 + T038-T041; 41 of 64 tasks now complete)
- `specs/232-ml-top-10-coverage-bundle/NEXT-SESSION.md` (this file)

## Cumulative Files Touched (F-6 to date — Waves 0.0 → 4)

Source files (6 F-6 targets):
1. `.claude/agents/tachi/tampering.md`
2. `.claude/agents/tachi/data-poisoning.md`
3. `.claude/agents/tachi/model-theft.md`
4. `.claude/skills/tachi-tampering/references/detection-patterns.md`
5. `.claude/skills/tachi-data-poisoning/references/detection-patterns.md`
6. `.claude/skills/tachi-model-theft/references/detection-patterns.md`

ADR (Wave 1.0):
- `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md`

Fixtures (8 new under `tests/scripts/fixtures/ml_top_10_coverage_bundle/`):
- T-10 (tampering Cat 10) + D-8/D-9/D-10 (data-poisoning Cat 8/9/10) + LLM-12/LLM-13/LLM-14 (model-theft Cat 12/13/14)

Examples (Wave 0.0):
- `examples/predictive-ml-app/` (architecture description + DFD)

Specs:
- `specs/232-ml-top-10-coverage-bundle/` (spec.md + plan.md + tasks.md + agent-assignments.md + research.md + data-model.md + contracts/finding-contract.md + quickstart.md + checklists/requirements.md + NEXT-SESSION.md)
