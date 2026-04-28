# Next Session Handoff — F-6 (Feature 232) ML Top 10 Coverage Bundle

**Branch**: `232-ml-top-10-coverage-bundle`
**Last commit**: `3e28366 feat(232): Wave 2.3 — data-poisoning Cat 10 + Disambiguation + Primary Sources (T022+T025)`
**Progress**: 25/64 tasks complete (39%)
**Waves complete this session**: Wave 2.1 + Wave 2.2 + Wave 2.3 (3 sequential team-lead MEDIUM-2 checkpoints)
**Cumulative waves complete**: Phase 1 verification + Wave 0.0 + Wave 1.0 + Wave 1.1 + Wave 2.1 + Wave 2.2 + Wave 2.3 (7 logical waves; 6 of 18 sequential waves per agent-assignments.md)
**Status**: Stopped at standalone 3-wave ceiling per `/aod.build` continuation rule

---

## Completed This Session

### Wave 2.1 — Data-Poisoning Metadata + Purpose + Step 5 + Cat 8 Checkpoint T-NN-1 (T017-T020 + T023) ✅

- T017: data-poisoning.md metadata 7-line additive append (ML06/07/08 + ATLAS T0018/T0019/T0020/T0031); inline `[A,B,C]` converted to multi-line list per F-5 denial-of-service precedent; pre-existing 3 LLM entries preserved byte-identical
- T018: data-poisoning.md `## Purpose` extension with 2-line additive paragraph naming transfer-learning supply-chain, feedback-loop skewing, and predictive-ML supply-chain completeness surfaces alongside existing LLM/RAG poisoning categories (1–7)
- T019: data-poisoning.md Detection Workflow Step 5 references inline parenthetical extension with OWASP ML06:2023/ML07:2023/ML08:2023 + ATLAS AML.T0019/T0031 exemplars; verified post-edit line count = 90 (target 84-90, well under 150 cap)
- **T020 (T-NN-1 / TEAM-LEAD MEDIUM-2 CHECKPOINT)**: data-poisoning companion Pattern Category 8 — Transfer Learning Supply Chain (Predictive ML) appended after Cat 7. Primary OWASP ML07:2023 + AML.T0018 in references (catalog-resolvable); AML.T0019 prose-only in mitigation (catalog-absent). 5 indicators (fine-tuning step on pretrained weights from public registry + checksum-absent + adapter integrity absent + provenance metadata absent + model-card review missing). Worked example (HuggingFace Hub `from_pretrained` without `revision=` SHA pinning + upstream maintainer compromise + backdoored revision merged into production fraud-detection model). 4 named mitigations (signed-weight-artifact policy, allowlist of trusted sources, fine-tuning hash-pinning, model-card provenance review). Self-review: PASS
- T023 [P]: Cat 8 fixture `valid_category_8_data_poisoning_transfer_learning_finding.yaml` (D-8). references: [OWASP ML07:2023, AML.T0018]; T0019 prose-only (3 prose mentions, 0 in references array per F-A2 contract)

### Wave 2.2 — Data-Poisoning Cat 9 Checkpoint T-NN-2 (T021 + T024) ✅

- **T021 (T-NN-2 / TEAM-LEAD MEDIUM-2 CHECKPOINT)**: data-poisoning companion Pattern Category 9 — Feedback-Loop Model Skewing (Active Learning / Online Learning) appended after Cat 8. Primary OWASP ML08:2023 + AML.T0020 in references (catalog-resolvable); AML.T0031 prose-only in mitigation (catalog-absent). 5 indicators (active-learning loopback without integrity controls + HITL labeler-trust absent + online-learning drift injection + recommendation clickstream tamper-detection absent + drift-detection alarms missing). Worked example (content-recommendation platform retraining nightly from clickstream events + bot-network click-stream tampering + 2-week drift toward target product category + held-out evaluation contaminated by same loopback). 4 named mitigations (feedback-data integrity gates with KS/PSI/KL drift detection, labeler-trust scoring with reputation weighting, canary audits with clean baseline anchored outside loopback path, drift-detection alarms on production inference distributions). Self-review: PASS
- T024 [P]: Cat 9 fixture `valid_category_9_data_poisoning_feedback_loop_finding.yaml` (D-9). references: [OWASP ML08:2023, AML.T0020]; T0031 prose-only (3 prose mentions, 0 in references array per F-A2 contract)

### Wave 2.3 — Data-Poisoning Cat 10 + Disambiguation + Primary Sources Checkpoint T-NN-3 (T022 + T025) ✅

- **T022 (T-NN-3 / TEAM-LEAD MEDIUM-2 CHECKPOINT)**: data-poisoning companion Pattern Category 10 — Predictive-ML Supply Chain Completeness (Datasets, Feature Stores, MLOps Registry) appended after Cat 9. Primary OWASP ML06:2023 corpus-side facet per ADR-035 D-4 disjoint architectural-tells + MITRE ATT&CK T1195 + T1195.001 + T1195.002 in references (all 4 catalog-resolvable). 5 indicators (dataset-repo without checksum manifest + feature-store without IAM-enforced write-audit + MLOps registry without signed-artifact promotion policy + model-card or datasheet metadata absent + dataset-checksum manifest absent). Worked example (predictive-ML team trains fraud-detection classifier from corpus stitched from public Kaggle dataset + Feast feature store + vendor S3 bucket + attacker compromises any one of three surfaces; no single integrity check across the three would catch it). 4 named mitigations (signed-artifact policy at MLOps registry boundary, IAM-enforced feature-store write-audit, dataset-checksum manifest with reproducibility verification, model-card review gate before promotion). Self-review: PASS
- **T022 cont (FR-011)**: Pattern Category Disambiguation subsection appended explicit boundary between Cat 8/9/10 (predictive-ML training-pipeline surfaces) and Cat 1-7 (LLM/RAG-tier poisoning). Cross-agent disambiguation: Cat 10 (D, corpus-side ML06) vs model-theft Cat 14 (LLM, artifact-side ML06) per ADR-035 D-4 disjoint architectural-tells.
- **T022 cont (FR-012)**: Primary Sources extension at end of file with 6 new entries (OWASP ML06/07/08:2023 + MITRE ATT&CK T1195 + T1195.001 + T1195.002).
- T025 [P]: Cat 10 fixture `valid_category_10_data_poisoning_corpus_supply_chain_finding.yaml` (D-10). references: [OWASP ML06:2023, T1195, T1195.001, T1195.002] (all 4 catalog-resolvable per F-A2 contract; no prose-only ATLAS cross-references in this fixture)

**Wave 2.x cumulative invariants verified green**:
- data-poisoning.md = 90 lines (target 84-90, ≤150 cap) ✅
- data-poisoning companion = 240 lines (137 → 240, +103 across Cat 8 + Cat 9 + Cat 10 + Disambiguation + Primary Sources extension) ✅
- Zero MAESTRO references in agent + companion ✅
- Pattern Category Disambiguation: 1 grep match (FR-011 / SC-014 partial — tampering + data-poisoning satisfied; model-theft remaining at Wave 3) ✅
- Cat 8/9/10 headers present with ML07/08/06:2023 markers (12 ML06/07/08:2023 references in companion) ✅
- 7 ATLAS prose-only references (T0019 + T0031 + T0015) all properly excluded from references arrays per F-A2 contract ✅
- Schema invariant: 0 lines diff ✅
- Consumers list: 0 lines diff ✅
- Orchestrator + dispatch-rules: 0 lines diff ✅

---

## Next Actions — Resume at Wave 3

**Wave 3 — Model-Theft Edits + Pattern Categories 12/13/14 + Architect Walkthrough** (Day 2 AM Thu 2026-04-30, ~4 hours)

Tasks (sequential within model-theft files; T035/36/37 fixtures parallel; T034 walkthrough after T033):

- T026: model-theft.md metadata 4-line additive append (ML03/ML04/ML06 corpus-side + AML.T0024); pre-existing LLM10:2025 + LLM03:2025 byte-identical. **Note**: model-theft.md currently uses inline format `owasp_references: [OWASP LLM10:2025, OWASP LLM03:2025]` — convert to multi-line per F-5 denial-of-service / F-6 Wave 2.1 data-poisoning precedent.
- T027: model-theft.md `## Purpose` extension naming predictive-ML extraction (model inversion + membership inference) + predictive-ML artifact supply-chain integrity surfaces alongside existing LLM-extraction + cost-amplification (F-5) surfaces
- T028: model-theft.md Step 5 references append + line-count cap verify (≤150, target 103-108)
- T029: Cat 12 — Model Inversion (Predictive ML) authoring. Primary OWASP ML03:2023 + AML.T0024 in references (catalog-resolvable; shared with Cat 13 but disjoint architectural-tells per ADR-035 D-5). 5 indicators (prediction API serving classifier with sensitive training data + DP-SGD on training absent + output-perturbation noise injection absent + query-rate throttling per tenant absent + model-extraction-pattern detection absent). Worked example (medical-imaging classifier serving `/predict` endpoint without DP-SGD and without per-tenant query throttling; attacker performs gradient-inversion). 4 named mitigations (DP-SGD with bounded ε ≤ 8.0, output-perturbation noise injection, query-rate throttling, model-extraction-pattern detection).
- T030: Cat 13 — Membership Inference (Predictive ML) authoring. Primary OWASP ML04:2023 + AML.T0024 in references (catalog-resolvable; shared with Cat 12). 5 indicators (prediction API returning confidence values + shadow-model attack feasibility + label-only response mode missing + DP-SGD absent + confidence-output truncation absent + training-data minimization not enforced). Worked example (fraud-detection classifier API returning prediction confidence values; attacker uses confidence-thresholding). 4 named mitigations (DP-SGD, confidence-output truncation or label-only response mode, query-rate throttling, training-data minimization).
- T031: Cat 14 — Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering) authoring. Primary OWASP ML06:2023 artifact-side facet per ADR-035 D-4 + MITRE ATT&CK T1195 + sub-techniques in references. 5 indicators (MLOps model registry with no signed-artifact policy + weight tampering surface mutable artifact storage + missing model-signing or attestation policy + registry IAM with promotion-gate review absent + integrity verification at model-load time absent). Worked example (MLflow model registry promoting models without signed-artifact policy; attacker compromises registry credentials and pushes backdoored model checkpoint). 4 named mitigations (model-signing with cryptographic attestation — Sigstore-style or KMS-backed, registry IAM with promotion-gate review, integrity verification at model-load time, immutable artifact storage with audit logging).
- T032: model-theft companion Pattern Category Disambiguation subsection (Cat 12 vs Cat 13 disjoint architectural-tells per ADR-035 D-5; Cat 12/13/14 vs Cat 1-9 LLM-tier extraction; Cat 14 vs Cat 10/11 cost-DoW from F-5)
- T033: Primary Sources extension on model-theft companion with OWASP ML03:2023 + ML04:2023 + ML06:2023 (FR-012)
- **T034**: Architect integration walkthrough — re-read model-theft companion Cat 10 → 11 → 12 → 13 → 14 visual continuity (post-F-5 + post-F-6); confirm no narrative gaps or inconsistencies between F-5's Cat 10/11 cost-DoW carve-out and F-6's Cat 12/13/14 predictive-ML surfaces (team-lead C-2)
- T035 [P]: Cat 12 fixture (`valid_category_12_model_theft_inversion_finding.yaml`); references: [OWASP ML03:2023, AML.T0024]
- T036 [P]: Cat 13 fixture (`valid_category_13_model_theft_membership_inference_finding.yaml`); references: [OWASP ML04:2023, AML.T0024]
- T037 [P]: Cat 14 fixture (`valid_category_14_model_theft_artifact_supply_chain_finding.yaml`); references: [OWASP ML06:2023, T1195, T1195.001, T1195.002]

Reference design at `specs/232-ml-top-10-coverage-bundle/contracts/finding-contract.md` lines 151-244 for Cat 12/13/14 fixture shapes.

After Wave 3, proceed to:

**Wave 4.0 — Predictive-ML-App End-to-End Regen** (Day 2 PM, ~2 hours): T042-T045
**Wave 4.1 — Tester Spot-Check (parallel)**: T046-T047
**Wave 5.0 — Tester Full 6-Baseline Verification + Wave 5.1 — ADR-035 Accepted (parallel, Day 3 AM)**: T048-T049

Plus US-2 invariant verification waves (T038-T041) interleaved per agent-assignments.md.

---

## Prerequisites Verified

- Branch `232-ml-top-10-coverage-bundle` matches NNN-* pattern ✅
- All three Triad sign-offs APPROVED in tasks.md frontmatter ✅
- agent-assignments.md present ✅
- GitHub Issue #232 stage:build label updated (warning ignored — board move succeeded) ✅
- PR #233 (draft) open with `feat(232): ML Top 10 Coverage Bundle` Conventional Commits title ✅
- 4 incomplete checklist items remain bookkeeping only — work migrated to tasks.md/plan.md (T020/T021/T022 = T-L MEDIUM-2 covered this session, T048/T049 = T-L LOW-1 future, T009 = Architect LOW-1 covered, plan.md Q3 RESOLVED = Architect LOW-2/LOW-3 covered)

---

## Resume Instructions

Start a new conversation and run `/aod.build`:

```bash
claude "Resume F-6 (Feature 232) ML Top 10 Coverage Bundle implementation (branch: 232-ml-top-10-coverage-bundle). Wave 2.x complete (25/64 tasks, 7 logical waves). Run /aod.build to continue with Wave 3 (model-theft enrichment T026-T034 + T035-T037 fixtures)."
```

The command will automatically resume from Wave 3.

---

## Critical Path Status

```
T007 ✅ → T009 ✅ → T010 ✅ → T011-T015 ✅ → T017-T022 ✅ → [NEXT: T026-T033] → T042-T045 → T048 → T049 → T054 → T055-T058 → T059
```

**5 of 12 critical-path nodes complete** (T007 + T009 + T010 + T011-T015 + T017-T022 grouped).

## Risks Active

- **R3 (Day 1 PM authoring quality slip)**: ✅ MITIGATED — Wave 2.1/2.2/2.3 sequential T-NN-1/2/3 checkpoints with rollback all PASSED; no rollback used; team-lead MEDIUM-2 fully discharged
- **R5 (Heuristic A 3-agent emergent issues)**: Pre-named deferral pair = data-poisoning Cat 10 (T022) ✅ delivered + model-theft Cat 14 (T031) pending. Architect re-verified Heuristic A protocol distinctness intact at three-agent scope at Wave 1.0; data-poisoning enrichment branch held discipline through 3 sequential category appends.
- **R10 (ATLAS catalog gap propagation 3x)**: ✅ MITIGATED at fixture-authoring discipline — T0019 (Cat 8 fixture) + T0031 (Cat 9 fixture) + T0015 (tampering Cat 10 fixture from Wave 1.1) all correctly omit catalog-absent ATLAS techniques from references arrays; prose-only fallback consistently applied. T0024 (Cat 12/13 — pending Wave 3) is catalog-resolvable per Q3 matrix.

## Files Modified This Session

- `.claude/agents/tachi/data-poisoning.md` (78 → 90 lines, metadata multi-line + Purpose extension + Step 5 references append)
- `.claude/skills/tachi-data-poisoning/references/detection-patterns.md` (137 → 240 lines, Cat 8 + Cat 9 + Cat 10 + Disambiguation + Primary Sources extension)
- `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_8_data_poisoning_transfer_learning_finding.yaml` (new — 32 lines, D-8)
- `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_9_data_poisoning_feedback_loop_finding.yaml` (new — 31 lines, D-9)
- `tests/scripts/fixtures/ml_top_10_coverage_bundle/valid_category_10_data_poisoning_corpus_supply_chain_finding.yaml` (new — 33 lines, D-10)
- `specs/232-ml-top-10-coverage-bundle/tasks.md` ([X] marks for T017-T025; 25 of 64 tasks now complete)
