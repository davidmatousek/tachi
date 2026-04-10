---
feature: 136-maestro-canonical-layer
generated: 2026-04-10
wave: W0
purpose: Pre-edit discovery sweep for MAESTRO canonical layer correctness fix
exclusions:
  - docs/product/02_PRD/084-*
  - docs/product/02_PRD/091-*
  - specs/084-*/
  - specs/091-*/
  - specs/136-*/
  - .git/
  - archive/
  - node_modules/
  - .venv/
---

# Wave 0 Discovery Report — MAESTRO Canonical Layer Correctness Fix

## Purpose

Enumerate every hardcoded reference that must change to complete the MAESTRO canonical layer rename (L5→L6 shift, L6→L7 shift, new L5, Typst "Integration Services" third-way bug, acronym expansion correction, and schema_version bump 1.2→1.3). Establishes scope discipline before any Wave 1 edits begin.

---

## Pattern 1: `"User Interface"` (T001)

Scope: all files minus exclusions. Catches "L7 — User Interface" label + broader "User Interface" occurrences.

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old Context | Target |
|------|---------|-------------|--------|
| `schemas/finding.yaml` | 132 | `"L7 — User Interface"` enum | W1-T013 |
| `templates/tachi/output-schemas/threats.md` | 135 | L7 — User Interface in example table | W1-T019 |

Non-excluded matches requiring W2 regeneration (replaced automatically by pipeline):

| File | Line(s) | Wave |
|------|---------|------|
| `examples/free-text-microservice/threats.md` | 24, 30 | W2-T028 |
| `examples/mermaid-agentic-app/threats.md` | 24, 80, 94, 172 | W2-T029 |
| `examples/ascii-web-api/threats.md` | 24, 89, 197 | W2-T027 |
| `examples/agentic-app/threats.md` | 18, 88, 108, 231 | W2-T032 |
| `examples/web-app/threats.md` | 18, 92, 112, 204 | W2-T025 |
| `examples/microservices/threats.md` | 18 | W2-T026 |

Excluded references (not in edit scope): `docs/product/02_PRD/084-*`, `docs/product/02_PRD/091-*`, `specs/084-*`, `specs/091-*`, `specs/136-*`.

---

## Pattern 2: `"Security Toolkit for Reasoning and Orchestration"` (T002)

Scope: all files minus exclusions. Catches wrong MAESTRO acronym expansion.

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old Context | Target |
|------|---------|-------------|--------|
| `.claude/skills/tachi-shared/references/maestro-layers-shared.md` | 17 | "Multi-Agent Environment Security Toolkit for Reasoning and Orchestration" | W1-T011 |
| `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` | 123 | Same acronym citation | W1-T017 |
| `docs/architecture/00_Tech_Stack/README.md` | 170 | **NEW — not in original W1 task list**. Standards listing contains wrong acronym expansion | **W1-T024+ (add to scope)** |

Excluded: `docs/product/02_PRD/091-*`, `docs/product/02_PRD/136-*`, `specs/136-*`.

---

## Pattern 3: `"Integration Services"` (T003)

Scope: all files minus exclusions. Catches the pre-existing Typst third-way divergence.

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old Context | Target |
|------|---------|-------------|--------|
| `templates/tachi/security-report/maestro-findings.typ` | 133 | `"L6": "Integration Services"` fallback dict | W1-T014 |

All other matches are in `specs/136-*` (excluded source-of-truth spec/plan/research).

---

## Pattern 4: `"L5 — Security"` and `"L5 Security"` (T004)

Scope: all files minus exclusions. Catches the old L5 layer label (with and without em dash).

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old Context | Target |
|------|---------|-------------|--------|
| `schemas/finding.yaml` | 130 | `"L5 — Security"` enum | W1-T013 |
| `templates/tachi/output-schemas/threats.md` | 279, 321, 521, 569, 571 | 5 occurrences in example tables | W1-T019 |
| `templates/tachi/infographics/infographic-maestro-stack.md` | 24 | L5 — Security in stack layer label | W1-T023 |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | 64 | L5 — Security in inline enum listing | W1-T012 |
| `.claude/skills/tachi-shared/references/maestro-layers-shared.md` | 132 | Section heading `### L5 — Security` | W1-T011 |

Non-excluded matches requiring W2 regeneration:

| File | Line(s) | Wave |
|------|---------|------|
| `examples/web-app/threats.md` | 21, 94, 113, 122, 141, 206 | W2-T025 |
| `examples/ascii-web-api/threats.md` | 26, 98, 106, 116, 133, 198 | W2-T027 |
| `examples/agentic-app/threats.md` | 19, 23, 100, 127, 137, 229 | W2-T032 |

Excluded: `specs/084-*`, `specs/136-*`, `docs/product/02_PRD/*`.

---

## Pattern 5: `"L6 — Agent Ecosystem"` and `"L6 Agent Ecosystem"` (T005)

Scope: all files minus exclusions. Catches the old L6 layer label.

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old Context | Target |
|------|---------|-------------|--------|
| `schemas/finding.yaml` | 131 | `"L6 — Agent Ecosystem"` enum | W1-T013 |
| `templates/tachi/infographics/infographic-maestro-stack.md` | 22 | L6 — Agent Ecosystem in stack label | W1-T023 |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | 64 | L6 — Agent Ecosystem in inline enum | W1-T012 |
| `.claude/skills/tachi-shared/references/maestro-layers-shared.md` | 150 | Section heading `### L6 — Agent Ecosystem` | W1-T011 |

Excluded: `specs/091-*` (091 code-review references are historical).

---

## Pattern 6: `"L7 — User Interface"` and `"L7 User Interface"` (T006)

Scope: all files minus exclusions. Catches the old L7 layer label.

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old Context | Target |
|------|---------|-------------|--------|
| `templates/tachi/output-schemas/threats.md` | 135 | L7 — User Interface in example table | W1-T019 |
| `schemas/finding.yaml` | 132 | `"L7 — User Interface"` enum | W1-T013 |
| `templates/tachi/infographics/infographic-maestro-stack.md` | 20, 113 | L7 — User Interface in stack label + caption | W1-T023 |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | 149 | Example dispatch row | W1-T016 |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | 64 | L7 — User Interface in inline enum | W1-T012 |
| `.claude/skills/tachi-shared/references/maestro-layers-shared.md` | 164 | Section heading `### L7 — User Interface` | W1-T011 |

Non-excluded matches requiring W2 regeneration:

| File | Line(s) | Wave |
|------|---------|------|
| `examples/free-text-microservice/threats.md` | 24, 30 | W2-T028 |
| `examples/mermaid-agentic-app/threats.md` | 24, 80, 94, 172 | W2-T029 |
| `examples/ascii-web-api/threats.md` | 24, 89, 197 | W2-T027 |
| `examples/agentic-app/threats.md` | 18, 88, 108, 231 | W2-T032 |
| `examples/web-app/threats.md` | 18, 92, 112, 204 | W2-T025 |
| `examples/microservices/threats.md` | 18 | W2-T026 |

Excluded: `specs/084-*`, `specs/136-*`, `docs/product/02_PRD/084-*`, `docs/product/02_PRD/136-*`.

---

## Pattern 7: Dashboard Keyword Pre-Validation (T007)

Scope: `examples/*/threats.md` and `examples/*/architecture.md`.

**Purpose**: Verify "dashboard" as a keyword does not trigger misclassification when MAESTRO keyword mappings shift L5/L6/L7 during Wave 1.

Matches found:

| File | Line(s) | Context | Component? | Resolution |
|------|---------|---------|------------|------------|
| `examples/free-text-microservice/threats.md` | 93, 225 | "Stripe dashboard for anomaly monitoring" | No — monitoring reference in remediation text | No ambiguity. Not a component name. |
| `examples/microservices/threats.md` | 107, 271 | "payment reconciliation against provider dashboard" | No — monitoring reference in remediation text | No ambiguity. Not a component name. |

**Resolution**: No "dashboard" occurrences classify a component. All 4 matches are monitoring/remediation references inside finding rows. No action needed; no risk of misclassification during Wave 1 keyword shift.

---

## Pattern 8: `schema_version: "1.2"` and `schema_version: 1.2` (T008)

Scope: all files minus exclusions. Catches hardcoded schema version that must bump to 1.3.

Non-excluded matches requiring W1 edits:

| File | Line(s) | Old | Target |
|------|---------|-----|--------|
| `schemas/finding.yaml` | 13 | `schema_version: "1.2"` | W1-T013 |
| `templates/tachi/output-schemas/threats.md` | 21, 57, 77, 99 | 4 occurrences | W1-T019 (architect estimated ~5; actual 4) |
| `.claude/skills/tachi-orchestration/references/output-schemas.md` | 26 | **NEW — not in original W1 task list**. `schema_version: "1.2"` | **W1-T024+ (add to scope)** |
| `docs/architecture/00_Tech_Stack/README.md` | 173 | **NEW**. Documentation reference: "`schema_version: "1.2"` frontmatter" in Output Templates section | **W1-T024+ (add to scope)** |

Non-excluded matches requiring W2 regeneration:

| File | Line(s) | Wave |
|------|---------|------|
| `examples/web-app/threats.md` | 2 | W2-T025 |
| `examples/microservices/threats.md` | 2 | W2-T026 |
| `examples/mermaid-agentic-app/threats.md` | 7 | W2-T029 |
| `examples/ascii-web-api/threats.md` | 7 | W2-T027 |
| `examples/free-text-microservice/threats.md` | 7 | W2-T028 |
| `examples/agentic-app/threats.md` | 2 | W2-T032 |

Excluded: `specs/084-*`, `specs/104-*`, `specs/136-*`.

---

## New Files Added to W1 Scope (Not in Original Task List)

Wave 0 discovery revealed 2 files outside the original 14-file Wave 1 task list that require canonical updates:

1. **`docs/architecture/00_Tech_Stack/README.md`**
   - Line 170: wrong MAESTRO acronym expansion ("Security Toolkit for Reasoning and Orchestration")
   - Line 173: documentation reference to `schema_version: "1.2"` — needs bump
   - **Proposed handling**: Add to W1 as supplementary edit alongside T024 or create T024a. Within scope discipline (≤45 file threshold).

2. **`.claude/skills/tachi-orchestration/references/output-schemas.md`**
   - Line 26: `schema_version: "1.2"` in frontmatter example
   - **Proposed handling**: Add to W1 as supplementary edit. Single-line change.

Both additions are minor (total ~3 line edits across both files) and do not constitute scope creep — they were simply not discovered during PRD/spec drafting. Discovery report documents them per Wave 0 purpose.

---

## File Count Summary

### Wave 1 (Foundation Edits)

| Original plan | Count |
|---------------|-------|
| 14 foundation files in T011-T024 | 14 |
| **New from W0 discovery** | 2 |
| **W1 revised total** | **16** |

### Wave 2 (Regeneration)

| Category | Files |
|----------|-------|
| `examples/web-app/` — threats.md + security-report.pdf.baseline | 2 |
| `examples/microservices/` — threats.md + security-report.pdf.baseline | 2 |
| `examples/ascii-web-api/` — threats.md + security-report.pdf.baseline | 2 |
| `examples/free-text-microservice/` — threats.md + security-report.pdf.baseline | 2 |
| `examples/mermaid-agentic-app/` — threats.md + threat-report.md + threat-infographic-spec.md + attack-trees/* + security-report.pdf.baseline | ~6 |
| `examples/agentic-app/sample-report/` — full pipeline (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, security-report.pdf, infographic JPEGs, attack-trees/) | ~10 |
| `tests/scripts/fixtures/golden/maestro-heatmap.json` | 1 |
| `tests/scripts/fixtures/golden/maestro-stack.json` | 1 |
| **W2 total** | **~26** |

### Wave 3 (Documentation)

| File | Purpose |
|------|---------|
| `CHANGELOG.md` | Migration note under v4.10.0 unreleased heading |
| `specs/136-maestro-canonical-layer/discovery-report.md` | This file (already committed in W0) |

**W3 total**: 2 (CHANGELOG + this report)

### Grand Total

| Wave | Files |
|------|-------|
| W1 | 16 |
| W2 | ~26 |
| W3 | 2 |
| **Total touched by this PR** | **~44** |

**Within threshold**: 44 ≤ 45. Scope discipline verified. No architect consultation required per tasks.md T010 gate.

---

## Wave 0 Exit Gate Checklist

- [x] All 8 grep patterns executed and recorded
- [x] `specs/136-maestro-canonical-layer/discovery-report.md` committed (this file)
- [x] Each grep pattern has a section with matched files + line counts
- [x] Annotations per file indicate wave target (W1 edit, W2 regen, or historical/excluded)
- [x] `dashboard` keyword pre-validation documented with resolution
- [x] Total file count ≤45 (actual: ~44)
- [x] New scope items (Tech_Stack README, output-schemas.md) explicitly flagged
- [x] Branch protection confirmed — feature branch `136-maestro-canonical-layer`, not `main`

## Handover to Wave 1

Wave 1 foundation edits can now begin. Sequential order per tasks.md T011→T024 + 2 supplementary edits:
1. T011 — maestro-layers-shared.md (canonical rewrite)
2. T012 — finding-format-shared.md (enum line 64)
3. T013 — schemas/finding.yaml (schema bump + enum values)
4. T014 — maestro-findings.typ (fix Integration Services third-way bug)
5. T015 — main.typ (prose line 293)
6. T016 — dispatch-rules.md (line 149 example)
7. T017 — ADR-020-maestro-layer-classification.md (acronym + Revision History)
8. T018 — README.md (lines 260-262 layer table)
9. T019 — output-schemas/threats.md (~5 schema_version + layer names)
10. T020 — output-schemas/risk-scores.md (layer names)
11. T021 — output-schemas/compensating-controls.md (layer names)
12. T022 — output-schemas/threat-report.md (layer names)
13. T023 — infographics/infographic-maestro-stack.md (lines 20, 22, 24, 113)
14. T024 — infographics/infographic-maestro-heatmap.md (lines ~34-35, 140-141)
15. **T024a (new)** — docs/architecture/00_Tech_Stack/README.md (lines 170, 173 supplementary)
16. **T024b (new)** — .claude/skills/tachi-orchestration/references/output-schemas.md (line 26)

**End of Wave 0 Discovery Report.**
