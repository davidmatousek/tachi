# Next Session Handoff — F-6 (Feature 232) ML Top 10 Coverage Bundle

**Branch**: `232-ml-top-10-coverage-bundle`
**Last commit**: `1738e30 feat(232): Wave 1.0+1.1 — ADR-035 + tampering enrichment (T009-T016)`
**Progress**: 16/64 tasks complete (25%)
**Waves complete**: Phase 1 verification + Wave 0.0 + Wave 1.0+1.1 (3 logical waves)
**Status**: Stopped at standalone wave ceiling per `/aod.build` continuation rule

---

## Completed This Session

### Phase 1 — Verification Gates (T001-T006) ✅

All 6 baseline assumptions verified:
- T001: Line counts 51/78/97/190/137/211 (tampering / data-poisoning / model-theft + companions)
- T002: Schema 1.8, `id.pattern` regex `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` unchanged
- T003: ATLAS catalog-resolvability 0/4/0/4/4/0 (T0015/T0019/T0031 absent — 3 of 6 prose-only at 3x F-5 T1496 scale)
- T004: ADR-035 next-available (ADR-034 highest pre-F-6)
- T005: Zero MAESTRO references in all 6 target files
- T006: Consumers list contains all 3 host agents

### Wave 0.0 — Predictive-ML-App Architecture (T007-T008) ✅

- T007: Authored `examples/predictive-ml-app/architecture.md` (102 lines) — fictional fraud-detection ML application exhibiting all 5 predictive-ML topology indicators (training pipeline + fine-tuning step on HuggingFace pretrained weights + MLflow MLOps registry + prediction-API + active-learning feedback loop)
- T008: Authored `examples/predictive-ml-app/README.md` (45 lines) — F-6 mutation target documentation

### Wave 1.0+1.1 — ADR-035 + Tampering Enrichment (T009-T016) ✅

- T009: Architect re-verification — all 6 baseline assumptions intact at three-agent scope (covered by Phase 1 + ADR-035 D-1)
- T010: ADR-035 Proposed at `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md` (319 lines, 10 D-numbered Decisions, 7 closure rows + 4 reference rows in canonical mapping table)
- T011: tampering.md metadata — append OWASP ML01:2023 + AML.T0015 to owasp_references
- T012: tampering.md Purpose extension — adversarial input manipulation surface for predictive ML
- T013: tampering.md Detection Workflow Step 5 references extension
- T014: tampering companion Pattern Category 10 (Adversarial Input Manipulation, Predictive ML) — 5 indicators, worked example, named adversarial-defense mitigations
- T015: tampering companion Pattern Category Disambiguation subsection (Cat 10 vs Cat 1-9) + Primary Sources extension (OWASP ML01:2023)
- T016: tampering Cat 10 fixture YAML at `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_10_tampering_adversarial_input_finding.yaml`

**Invariants verified green** (all):
- tampering.md = 55 lines (target 54-58, ≤120 cap) ✅
- Zero MAESTRO references ✅
- Pattern Category Disambiguation present (1 grep match on tampering companion) ✅
- Schema invariant: 0 lines diff ✅
- Consumers list: 0 lines diff ✅
- Orchestrator + dispatch-rules: 0 lines diff ✅

---

## Next Actions — Resume at Wave 2.1

**Wave 2.1 — Data-Poisoning Cat 8 Checkpoint T-NN-1** (Day 1 PM Wed 2026-04-29, ~90 min)

Tasks (sequential within data-poisoning files; T023 fixture parallel with T020):
- T017: data-poisoning.md metadata 7-line additive append (ML06/07/08 + ATLAS T0018/T0019/T0020/T0031)
- T018: data-poisoning.md Purpose extension naming predictive-ML training poisoning + transfer-learning supply-chain + feedback-loop skewing surfaces
- T019: data-poisoning.md Step 5 references extension; verify ≤150 lines (target 84-90)
- **T020 (T-NN-1)**: data-poisoning companion **Pattern Category 8 — Transfer Learning Supply Chain (Predictive ML)** — primary OWASP ML07:2023, AML.T0018 in references, AML.T0019 prose-only; 5 indicators (fine-tuning step on pretrained weights + no checksum verification + adapter merged without integrity verification + provenance metadata absent + model-card review missing); worked example (HuggingFace Hub fine-tuning without `revision=` checksum pinning); named mitigations (signed-weight-artifact policy, allowlist of trusted sources, fine-tuning hash-pinning, model-card provenance review). **Self-review checkpoint** before T-NN-2.
- T023 [P]: data-poisoning Cat 8 fixture YAML

Then proceed to:

**Wave 2.2 — Cat 9 Checkpoint T-NN-2** (~90 min)
- T021 (T-NN-2): Pattern Category 9 Feedback-Loop Model Skewing + T024 [P] fixture

**Wave 2.3 — Cat 10 Checkpoint T-NN-3** (~90 min)
- T022 (T-NN-3): Pattern Category 10 Predictive-ML Supply Chain Completeness + Disambiguation + Primary Sources extension + T025 [P] fixture

Reference design at `specs/232-ml-top-10-coverage-bundle/contracts/finding-contract.md` lines 58-130 for D-{N} fixture shapes.

---

## Prerequisites Verified

- Branch `232-ml-top-10-coverage-bundle` matches NNN-* pattern ✅
- All three Triad sign-offs APPROVED in tasks.md frontmatter ✅
- agent-assignments.md present ✅
- GitHub Issue #232 moved to "Build" board ✅
- PR #233 (draft) open with `feat(232): ML Top 10 Coverage Bundle` Conventional Commits title ✅
- 4 incomplete checklist items are bookkeeping only — work migrated to tasks.md/plan.md (T020/T021/T022 = T-L MEDIUM-2, T048/T049 = T-L LOW-1, T009 = Architect LOW-1, plan.md Q3 RESOLVED = Architect LOW-2/LOW-3)

---

## Resume Instructions

Start a new conversation and run `/aod.build`:

```bash
claude "Resume F-6 (Feature 232) ML Top 10 Coverage Bundle implementation (branch: 232-ml-top-10-coverage-bundle). Phase 1 + Wave 0.0 + Wave 1.0+1.1 complete (16/64 tasks, 3 waves). Run /aod.build to continue with Wave 2.1 (data-poisoning T017-T020 + T023 fixture)."
```

The command will automatically resume from Wave 2.1.

---

## Critical Path Status

```
T007 ✅ → T009 ✅ → T010 ✅ → T011-T015 ✅ → [NEXT: T017-T022] → T026-T033 → T042-T045 → T048 → T049 → T054 → T055-T058 → T059
```

**4 of 12 critical-path nodes complete** (T007 + T009 + T010 + T011-T015 grouped).

## Risks Active

- **R3 (Day 1 PM authoring quality slip)**: Mitigated by team-lead MEDIUM-2 sequential T-NN-1/2/3 checkpoints with rollback (~90 min each). Wave 2.1 next session.
- **R5 (Heuristic A 3-agent emergent issues)**: Pre-named deferral pair = data-poisoning Cat 10 (T022) + model-theft Cat 14 (T031) per spec OoS-15. Architect re-verifies at Wave 1.0 confirmed Heuristic A protocol distinctness intact at three-agent scope.
- **R10 (ATLAS catalog gap propagation 3x)**: Already absorbed at PRD/plan time + ADR-035 Constraint section. AML.T0015/T0019/T0031 prose-only verified at fixture-authoring discipline (T016 already correctly omits T0015 from references array).
