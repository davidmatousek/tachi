# Research Summary: F-6 ML Top 10 Coverage Bundle

**Feature**: 232 — ML Top 10 Coverage Bundle (BLP-01 Tier 2 first feature)
**PRD**: [docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md](../../docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md)
**Created**: 2026-04-27
**Status**: Complete (informs spec.md / plan.md / tasks.md authoring at plan day Tuesday 2026-04-28)

---

## Knowledge Base Findings

**Source**: Repo-internal precedent across BLP-01 Tier 1 features (F-1 through F-5).

- **F-3 ADR-032 (single-agent enrichment, ASI07 / `tool-abuse`)** — first execution of the Heuristic A enrichment branch. 7 Decisions; D7 = Pattern Category Disambiguation precedent (Cat 9-10 boundary against Cat 1-8 in `tool-abuse` companion). 2 new pattern categories. Zero schema bump. Zero functional orchestrator/dispatch edits.
- **F-5 ADR-034 (two-agent enrichment, LLM10 / `denial-of-service` + `model-theft`)** — second execution. 9 Decisions; D7 = dual Pattern Category Disambiguation (DoS Cat 9 vs 12/13 + model-theft Cat 6 vs 10/11). 4 new pattern categories. Zero schema bump. Lines 192–204 explicitly forecast F-6 as three-agent execution with no schema bump.
- **Heuristic A signal-class taxonomy** (ADR-030 D1) — same-class scope dictates enrichment over new-agent creation. ML Top 10 items resolve onto three existing signal classes: data-integrity (`tampering`), adversarial-corpus (`data-poisoning`), extraction (`model-theft`).
- **ADR-023 D3 (additive-only edit discipline)** — pre-existing categories preserved byte-identically; new categories appended after the highest existing category number. Verified across F-3 (Cat 9-10 append after Cat 8) and F-5 (DoS Cat 12-13 after Cat 11; MT Cat 10-11 after Cat 9).
- **ADR-027 dual-commit pattern** — ADRs land Proposed at build start, transition Accepted at PR merge with post-merge SHA fill. F-3 ADR-032 (265 lines) and F-5 ADR-034 (333 lines) shipped under this pattern with no de facto length cap.
- **R12 release-please mitigation** (`.claude/rules/git-workflow.md`) — PR title MUST be Conventional-Commit-formatted (`feat(NNN):` for new features). F-212 incident (2026-04-25) failed to trigger release-please; F-1 / F-2 / F-3 / F-4 / F-5 all shipped clean under the two-step Pre-merge + Post-merge enforcement.

**Key lesson**: F-6 is precedent-following (third execution), not precedent-establishing. ADR-034's three-agent forecast removes adjudication overhead.

---

## Codebase Analysis (Empirical Verification)

**Source**: Direct grep + `wc -l` against the post-F-5 file system state (2026-04-27).

### Six target file baselines (all match PRD claims)

| File | `wc -l` | Tier Cap | Margin Post-Edit |
|------|---------|----------|------------------|
| `.claude/agents/tachi/tampering.md` | **51** | 120 (STRIDE) | ≥62 lines |
| `.claude/agents/tachi/data-poisoning.md` | **78** | 150 (AI) | ≥60 lines |
| `.claude/agents/tachi/model-theft.md` | **97** | 150 (AI) | ≥42 lines |
| `tachi-tampering/.../detection-patterns.md` | **190** | (no de facto cap) | n/a |
| `tachi-data-poisoning/.../detection-patterns.md` | **137** | (no de facto cap) | n/a |
| `tachi-model-theft/.../detection-patterns.md` | **211** | (no de facto cap) | n/a |

### Schema invariant (verified)

- `schemas/finding.yaml` `schema_version: "1.8"` — preserved through F-5; F-6 holds at 1.8.
- `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` — `T`, `D`, `LLM` already alternation values. **No new prefix needed.**

### Taxonomy catalog-resolvability (Q3 plan-day verification)

`schemas/taxonomy/owasp.yaml`: ML01-ML10 all present (10 entries via `grep "^- id: ML0\|^- id: ML10"`).

`schemas/taxonomy/mitre-atlas.yaml`:

| ATLAS technique | Catalog status | F-6 disposition |
|-----------------|----------------|-----------------|
| AML.T0015 — Evade ML Model | **NOT IN CATALOG** | Prose-only in mitigation narrative |
| AML.T0018 — Backdoor ML Model | Present | `references` array |
| AML.T0019 — Publish Poisoned Datasets | **NOT IN CATALOG** | Prose-only in mitigation narrative |
| AML.T0020 — Poison Training Data | Present | `references` array |
| AML.T0024 — Exfiltration via ML Inference API | Present | `references` array |
| AML.T0031 — Erode ML Model Integrity | **NOT IN CATALOG** | Prose-only in mitigation narrative |

**3 of 6 ATLAS entries are catalog-missing.** F-6 ships with prose-only fallback at 3x the F-5 T1496 precedent scale; defers catalog augmentation to F-A1.1 follow-on.

`schemas/taxonomy/mitre-attack.yaml`: T1195 + T1195.001 + T1195.002 all present (verified for ML06 supply-chain citations).

### ADR numbering

`docs/architecture/02_ADRs/` — ADR-034 is the highest committed; **ADR-035 is the next-available number** for F-6.

### Backward-compatibility test infrastructure

`tests/scripts/test_backward_compatibility.py` already implements:
- `DETECTION_AGENT_PATHS` (10 entries; F-6 removes `tampering.md` + `data-poisoning.md` → 8 entries).
- `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (3 entries today; F-6 adds 2: tampering + data-poisoning companions).
- 6-baseline test loop: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. **`agentic-app` and `consumer-agent-app` intentionally excluded** as mutation targets.

### Consumers list & dispatch (zero edit needed)

- `.claude/skills/tachi-shared/references/finding-format-shared.md` — all three hosts (`tampering`, `data-poisoning`, `model-theft`) present.
- `.claude/agents/tachi/orchestrator.md` — all three hosts present in dispatch tables.
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — `data-poisoning` + `model-theft` referenced; `tampering` is in the implicit STRIDE block.

### `agentic-app` predictive-ML signal grep (HIGH-1 architect finding)

Negative grep on 13 indicators (MLOps, model-registry, feature-store, fine-tuning, HuggingFace, active-learning, classifier, prediction-API, training-pipeline, feedback-loop, adversarial, model-inversion, membership-inference) — **zero matches** in `examples/agentic-app/architecture.md`. New `examples/predictive-ml-app/` authoring is the **default plan-day path**, not contingency.

---

## Architecture Constraints

- **ADR-021** — byte-identity invariant under `SOURCE_DATE_EPOCH=1700000000` for non-mutation baselines. Non-negotiable.
- **ADR-023 D1** — tier caps: STRIDE ≤ 120, AI ≤ 150, hard ceiling 180. F-6 margins all ≥42 lines (tightest case: `model-theft.md` at 97 → ~108 post-edit).
- **ADR-023 D3** — additive-only edit discipline; pre-existing categories byte-identical pre/post edit (grep-checkable invariant).
- **ADR-027** — ADR Proposed → Accepted dual-commit pattern with post-merge SHA fill.
- **ADR-028 D6** — `source_attribution` populator wiring deferred to F-A3; F-6 cites references in prose-level `references:` array only.
- **ADR-030 D1** — Heuristic A signal-class taxonomy in LLM tier; F-6 inherits at three-agent scope.
- **ADR-032** — F-3 single-agent enrichment precedent (lines 84 + 182 forecast).
- **ADR-034** — F-5 two-agent enrichment precedent; lines 192–204 explicitly forecast F-6 as three-agent execution with no schema bump.
- **SDR-001 D4** — enrichment-branch rule for same-class scope (locked; cannot ship F-6 as new agents without re-opening Heuristic A on every prior consolidation).
- **R12 release-please mitigation** — `feat(232):` Conventional Commit title required at draft PR creation and re-verified at `/aod.deliver`.

### Dependencies (all satisfied)

- F-A1 (taxonomy crosswalk) — Issue #180 CLOSED 2026-04-17.
- F-A2 (`source_attribution` schema) — Issue #189 CLOSED 2026-04-18.
- F-3 (ASI07 enrichment) — Issue #219 CLOSED 2026-04-26.
- F-5 (LLM10 enrichment) — Issue #229 CLOSED 2026-04-27.

---

## Industry Research

**Source**: OWASP Machine Learning Security Top 10:2023 + MITRE ATLAS framework.

### OWASP ML Top 10:2023 — six closure targets

- **ML01 Input Manipulation Attack** — adversarial perturbations, FGSM/PGD-style attacks, decision-boundary attacks, physical-world adversarial patches. Mitigations: adversarial training, input-validation barriers (statistical anomaly detection), confidence-thresholding with HITL escalation.
- **ML03 Model Inversion Attack** — reconstruction of training-data inputs from model outputs (white-box gradient inversion or black-box query optimization), attribute-inference attacks. Mitigations: differential privacy (DP-SGD with bounded ε), output-perturbation noise, query-rate throttling, model-extraction detection.
- **ML04 Membership Inference Attack** — confidence-thresholding attacks, shadow-model attacks, label-only attacks against APIs returning only predicted class. Mitigations: DP-SGD, confidence-output truncation or label-only response mode for sensitive endpoints, training-data minimization.
- **ML06 AI Supply Chain Attacks** — two-facet split: (a) corpus-side (datasets, feature stores, training-data path), (b) artifact-side (model registry, weight artifact storage, serving-time integrity). Mitigations: signed-artifact policy, registry IAM, model-card review gates.
- **ML07 Transfer Learning Attack** — fine-tuning on untrusted pretrained weights from public registries (HuggingFace Hub, TensorFlow Hub) without checksum verification, adapter poisoning. Mitigations: signed-weight-artifact policy, allowlist of trusted sources, fine-tuning hash-pinning.
- **ML08 Model Skewing** — active-learning pipelines without integrity controls, label-flipping in HITL labeling, online-learning drift injection, recommendation-system feedback loops without tamper-detection. Mitigations: feedback-data integrity gates, labeler-trust scoring, periodic retraining-data audit.

### MITRE ATLAS framework cross-references

- **AML.T0015 Evade ML Model** — ML01 cite (catalog-missing; prose-only).
- **AML.T0018 Backdoor ML Model** — ML07 cite (present in catalog).
- **AML.T0019 Publish Poisoned Datasets** — ML07 cite (catalog-missing; prose-only).
- **AML.T0020 Poison Training Data** — ML08 cite (present in catalog).
- **AML.T0024 Exfiltration via ML Inference API** — ML03/ML04 cite (present in catalog; shared between Cat 12 + Cat 13).
- **AML.T0031 Erode ML Model Integrity** — ML08 cite (catalog-missing; prose-only).

### MITRE ATT&CK T1195 (Supply Chain Compromise)

T1195 + T1195.001 (Compromise Software Dependencies) + T1195.002 (Compromise Software Supply Chain) all present in `schemas/taxonomy/mitre-attack.yaml`. Used for ML06 corpus-side (Cat 10) and ML06 artifact-side (Cat 14) supply-chain citations.

---

## Recommendations for Spec / Plan / Tasks

Based on architect APPROVED_WITH_CONCERNS deferred MEDIUMs (3-6) + team-lead APPROVED_WITH_CONCERNS deferred MEDIUMs (1-3):

### Spec.md scope (this artifact)

1. **Promote three User Stories from PRD** (US-232-1 / US-232-2 / US-232-3) with P0 priority; preserve PRD acceptance criteria with grep-checkable invariants.
2. **Expand 9 PRD FRs to ~24-26 spec FRs** that promote PRD's "deliberately NOT" framings into enforceable invariants (mirrors F-5's 8 PRD → 22 spec expansion and F-3's 5 PRD → 21 spec expansion).
3. **Pattern Category Disambiguation requirement** (architect MEDIUM-3) — explicit FR per host companion, mirroring F-3 D7 + F-5 D7 precedent. Three disambiguation subsections required: tampering Cat 10 vs Cat 1-9; data-poisoning Cat 8/9/10 vs Cat 1-7; model-theft Cat 12/13/14 vs Cat 1-11.
4. **R5 deferral pair pre-naming** (team-lead MEDIUM-1) — encode in Out-of-Scope / Risks section: if R5 (Heuristic A three-agent emergent issues) triggers, defer `data-poisoning` Cat 10 + `model-theft` Cat 14 (both ML06 facets) together to follow-on PR.
5. **predictive-ml-app/ authoring** (architect HIGH-1, MEDIUM-6) — encode as default mutation target in FR-7 acceptance criteria. Effort: ~4-6 hours architect/senior-backend-engineer at plan day.
6. **22-file zero-edit invariant** — encode as enforceable FR with explicit enumeration of the 22 non-target files (12 other agents + 10 other companions).
7. **Schema invariant** — encode `schema_version "1.8"` and unchanged regex as enforceable FR (third no-bump enrichment after F-3 + F-5).
8. **Conventional Commits + delivery retrospective** — FR for `feat(232):` PR title + delivery retrospective at `specs/232-ml-top-10-coverage-bundle/delivery.md` (mirrors F-1/F-2/F-3/F-4/F-5 precedent).

### Plan.md scope (next artifact)

9. **ML06 disjoint architectural-tells** (architect MEDIUM-4) — encode as ADR-035 D-numbered decision: corpus-side Cat 10 owns dataset-repos / feature-stores / training-data path; artifact-side Cat 14 owns model-registry / weight-artifact-storage / serving-time integrity.
10. **ML03 vs ML04 disjoint tells** (architect MEDIUM-5) — Cat 12 model-inversion = white-box gradient inversion + black-box optimization for **input reconstruction**; Cat 13 membership-inference = confidence-thresholding + shadow-model attacks for **training-set membership determination**. Shared AML.T0024 citation acceptable but architectural-tells distinguishable.
11. **Day 2 PM tester engagement explicit** (team-lead MEDIUM-3) — wave assignments must explicitly engage tester for early-signal byte-identity spot-check on 1–2 baselines (preserves SC-13 owner separation precedent from F-3/F-4/F-5).

### Tasks.md scope (third artifact)

12. **Day 1 PM category-by-category checkpoints** (team-lead MEDIUM-2) — three sequential ~90-minute checkpoint tasks: T-NN-1 = `data-poisoning` Cat 8 land + self-review; T-NN-2 = Cat 9 land + self-review; T-NN-3 = Cat 10 land + self-review.
13. **Day 3 AM split annotation** (team-lead LOW-1) — AM-1 = full 6-baseline regen verification (tester); AM-2 = ADR-035 SHA fill (architect).
14. **Q3 plan-day allocation** (team-lead LOW-3) — architect allocates ~30 minutes at plan day to verify 6 MITRE ATLAS AML.T entries against `schemas/taxonomy/mitre-atlas.yaml`. Already done at PRD-time research (3 of 6 missing); architect re-verifies at plan day to allow late-merge ADR-A1.1 catalog entries to alter F-6's prose-only set.

---

## References

- PRD: [docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md](../../docs/product/02_PRD/232-ml-top-10-coverage-bundle-2026-04-27.md)
- Architect review: [.aod/results/architect.md](../../.aod/results/architect.md)
- Team-lead review: [.aod/results/team-lead.md](../../.aod/results/team-lead.md)
- F-5 spec precedent: [specs/229-llm10-unbounded-consumption-verification/spec.md](../229-llm10-unbounded-consumption-verification/spec.md)
- F-3 spec precedent: [specs/219-asi07-tool-abuse-enrichment/spec.md](../219-asi07-tool-abuse-enrichment/spec.md)
- ADR-023: [docs/architecture/02_ADRs/ADR-023-lean-agent-additive-skill-references.md](../../docs/architecture/02_ADRs/ADR-023-lean-agent-additive-skill-references.md)
- ADR-032 (F-3): [docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md](../../docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md)
- ADR-034 (F-5): [docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md](../../docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md)
- BLP-01 strategy: `_internal/strategy/BLP-01-threat-coverage.md` §F-6, §6 Coverage Matrix
- OWASP ML Top 10:2023: https://owasp.org/www-project-machine-learning-security-top-10/
- MITRE ATLAS: https://atlas.mitre.org/
