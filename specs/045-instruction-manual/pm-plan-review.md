# PM Plan Review: 045 — End-to-End tachi Instruction Manual

**Reviewer**: product-manager
**Date**: 2026-03-28
**Artifact**: `specs/045-instruction-manual/plan.md`
**Verdict**: APPROVED

---

## Review Scope

Evaluated plan.md against:
- PRD: `docs/product/02_PRD/045-instruction-manual-2026-03-28.md`
- Spec: `specs/045-instruction-manual/spec.md`
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- Existing assets: `DEVELOPER_GUIDE_TACHI.md` (1,366 lines), `GUIDE_PROMPT.md` (633 lines)

---

## 1. Requirements Coverage (FR-001 through FR-015)

All 15 functional requirements are addressed in the plan. Traceability below:

| FR | Description | Plan Coverage | Status |
|----|-------------|---------------|--------|
| FR-001 | Prompt spec: /risk-score docs | Phase 1, Component 1 item 1 (~80-100 lines) | COVERED |
| FR-002 | Prompt spec: /compensating-controls docs | Phase 1, Component 1 item 2 (~80-100 lines) | COVERED |
| FR-003 | Prompt spec: standalone /infographic docs | Phase 1, Component 1 item 3 (~60-80 lines) | COVERED |
| FR-004 | Prompt spec: post-pipeline enrichment workflow | Phase 1, Component 1 item 4 (~40-60 lines) | COVERED |
| FR-005 | Correct agent count and template names | Phase 1, Component 1 item 5 (factual corrections) | COVERED |
| FR-006 | Rename GUIDE_PROMPT.md to developer-guide-prompt.md | Phase 2, explicit git mv command | COVERED |
| FR-007 | Developer guide: 3 new command sections | Phase 3, Component 2 items 3-6 | COVERED |
| FR-008 | Developer guide: post-pipeline workflow + data flow diagram | Phase 3, Component 2 item 2 (ASCII/Mermaid) | COVERED |
| FR-009 | Quick Start: introduce all 4 commands, 5-minute target | Phase 3, Component 2 item 1 (What's Next callout) | COVERED |
| FR-010 | Extend OpenClaw worked example through all 4 commands | Phase 3, Component 2 item 6 (Steps 11-13) | COVERED |
| FR-011 | Appendix B: post-pipeline output structures | Phase 3, Component 2 item 7 (~80-100 lines) | COVERED |
| FR-012 | Consistent per-command section template | Per-Command Section Template block in plan | COVERED |
| FR-013 | All acronyms defined on first use | Phase 3 implicitly; Appendix C glossary additions | COVERED |
| FR-014 | Copy-pasteable code blocks (minimal + flagged) | Component 1/2 invocation sections both specify this | COVERED |
| FR-015 | Both integration paths documented | Existing guide already covers this; plan preserves it | COVERED |

**Finding**: 15/15 FRs are explicitly addressed. No gaps.

---

## 2. User Story Alignment

| User Story | Plan Phase | Assessment |
|------------|-----------|------------|
| US-1: Complete Pipeline Guide | Phases 1+3 (new command sections + pipeline workflow) | ADDRESSED - All 4 commands covered with inputs/outputs/dependencies |
| US-2: Output Interpretation | Phase 3 items 3-6 (each section includes "Understanding the Output") | ADDRESSED - Per-command section template mandates interpretation |
| US-3: Quick Start | Phase 3 item 1 (What's Next callout) | ADDRESSED - see note below |
| US-4: Prompt Spec Update | Phase 1 + Phase 2 | ADDRESSED - Full update then rename |
| US-5: OpenClaw Extension | Phase 1 item 6 + Phase 3 item 6 | ADDRESSED - Extended in both spec and guide |
| US-6: Appendix Updates | Phase 3 items 7-8 | ADDRESSED - Appendix B + C expansions |

**Note on US-3 (Quick Start)**: The plan correctly keeps the Quick Start focused on `/threat-model` to hit the 5-minute target, then adds a "What's Next" callout introducing the 3 enrichment commands. This is the right approach. Loading the Quick Start with all 4 commands would violate the 5-minute constraint. The PRD's FR-4 specifies 5-6 steps ending with "Run `/threat-model`" and "Read results" -- the plan is aligned.

---

## 3. Quick Start 5-Minute Target Achievability

The plan's approach to the Quick Start target is sound:

- **What it does**: Keeps the existing Quick Start flow (clone, copy, verify, create architecture, run `/threat-model`, read results) and adds a "What's Next" callout after Step 6
- **Why it works**: The Quick Start is already the existing guide's Part 1. The plan correctly identifies that the 5-minute target applies to the first threat model, not the full pipeline
- **Risk**: Minimal. The existing Quick Start already runs `/threat-model` in a focused flow. Adding a callout with pointers does not add execution time
- **Validation**: Phase 4, step 3 explicitly validates Quick Start completability

**Assessment**: Achievable. The plan correctly scopes the 5-minute target to `/threat-model` and uses the remaining 3 commands as a teaser, not a requirement.

---

## 4. Scope Boundaries

### No Scope Creep

The plan stays within PRD-defined boundaries:
- No code changes, no agent modifications, no command changes
- Only modifies 2 files: prompt spec and developer guide
- No new example architectures
- No README.md changes
- No CI/CD tutorials

### Nothing Missing

Every PRD "In Scope" item has a corresponding plan phase:
- Prompt spec update: Phase 1
- Prompt spec rename: Phase 2
- Developer guide update: Phase 3
- OpenClaw extension: Phase 1 item 6 + Phase 3 item 6
- Quick Start enhancements: Phase 3 item 1
- Appendix updates: Phase 3 items 7-8
- Validation: Phase 4

The plan's "Out of Scope" matches the PRD's "Out of Scope" exactly.

---

## 5. Phase Sequencing

The phase ordering is correct and respects the source-of-truth constraint:

1. **Phase 1 (Prompt Spec Update)** -- Must come first because the prompt spec is the source of truth for guide content. Updating the guide before the spec would create drift.
2. **Phase 2 (Rename)** -- Logically follows Phase 1. Rename after content update is correct (avoids confusion about which file is being edited during Phase 1).
3. **Phase 3 (Developer Guide Update)** -- After Phase 1+2, so the guide draws from the completed, renamed spec. The plan explicitly states this dependency.
4. **Phase 4 (Validation)** -- Final phase. All 6 validation checks are appropriate.

**Assessment**: Sequencing is correct. The spec-before-guide dependency is respected.

---

## 6. OpenClaw Worked Example Extension

The plan's approach to extending the OpenClaw example is sound:

- **In the prompt spec** (Phase 1 item 6, ~40-60 lines): Add `/risk-score`, `/compensating-controls`, and `/infographic` steps with sample output
- **In the developer guide** (Phase 3 item 6, ~100-120 lines): Add Steps 11-13 continuing the existing worked example
- **Continuity**: The plan correctly extends the existing example rather than creating a parallel one. This preserves the "single thread" narrative that reduces cognitive load for users.
- **Validation**: Phase 4, step 4 explicitly validates OpenClaw consistency across all 4 command steps

**Assessment**: Sound. Single-example continuity is the right choice per PRD US-045-5.

---

## 7. Product Vision Alignment

tachi's vision: "The default threat modeling toolkit for any team building agentic AI applications."

This plan directly supports the vision by:
- Lowering the barrier to entry (comprehensive documentation for the full pipeline)
- Making the full value accessible (users currently stop at `/threat-model` without knowing about enrichment commands)
- Supporting the target user (developers who need security without deep security expertise)

The plan is the bridge between "toolkit exists" and "toolkit is usable."

---

## 8. Risk Assessment Review

The plan identifies 3 risks. All are appropriate:

1. **Guide drift from actual behavior** (Medium/High): Mitigation is cross-referencing against command specs in `adapters/claude-code/commands/`. This is the right source of truth.
2. **Guide length** (Low/Medium): Quick Start provides immediate value. The plan estimates ~2,186-2,371 total lines, which is long but acceptable for a comprehensive reference guide.
3. **Spec-guide divergence** (Medium/Medium): Phase ordering (spec first, guide second) is the correct mitigation.

No missing risks identified.

---

## 9. Constitution Check

The plan's constitution check is thorough. All 11 principles evaluated, with appropriate PASS/N/A markings. The docs-only exception for testing (Principle VI) and deployment (Principle VII) is correctly invoked.

---

## 10. Minor Observations (Non-Blocking)

1. **Line count estimates are ranges**: Component 1 estimates ~300-400 new lines; Component 2 estimates ~820-1,005 new lines. These are reasonable ranges for a documentation feature. Actuals may vary without product impact.
2. **Per-command section template**: The plan defines a consistent 6-part structure (What It Does, Prerequisites, Running the Command, Understanding the Output, Scoring/Analysis Details, What to Do Next). This is well-structured and supports FR-012.
3. **Data flow diagram**: The ASCII diagram in the plan clearly shows all 4 commands with their inputs, outputs, and dependencies. This diagram should appear in the guide (FR-008), and the plan commits to including it in Phase 3, item 2.

---

## Sign-off

**STATUS**: APPROVED

The plan is well-structured, correctly sequenced, and fully aligned with the PRD and spec. All 15 functional requirements are addressed, all 6 user stories are served, the Quick Start 5-minute target is achievable with the proposed approach, scope boundaries match the spec exactly with no creep and nothing missing, phase sequencing respects the source-of-truth constraint, and the OpenClaw extension approach is sound. No changes requested.

---

*Reviewed by: product-manager*
*Date: 2026-03-28*
