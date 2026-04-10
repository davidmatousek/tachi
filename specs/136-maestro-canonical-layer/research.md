# Research Summary: MAESTRO Canonical Layer Correctness Fix (Feature 136)

**Date**: 2026-04-10
**PRD**: `docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md`

This research report grounds the spec in the current tachi codebase state. It is produced before spec writing and informs FR/NFR decisions.

---

## 1. Extraction Pipeline Touch Points (Data-Driven Confirmation)

**Key finding**: The extraction pipeline is fully data-driven. No Python scripts have hardcoded layer name string matching.

| File | What It Does | Hardcoded Layer Names? |
|------|--------------|------------------------|
| `scripts/extract-report-data.py` (lines 375-407) | Reads `maestro_layer` from findings, groups by layer ID, orders via `_MAESTRO_LAYERS.index(lid)` | No — uses layer IDs (L1-L7) only |
| `scripts/extract-infographic-data.py` (lines 1340-1355) | Reads `maestro_layer` from findings via `parse_per_finding_maestro()`, uses `.startswith(lid)` pattern | No — uses layer IDs only |
| `scripts/tachi_parsers.py` (line 43) | Defines `MAESTRO_LAYERS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]` constant | No — uses layer IDs only |

**Implication for spec**: FR-4 (Example Regeneration) is a pure data refresh — no code changes in extraction scripts are needed. Only the upstream orchestrator, the shared reference, and the Typst template need updates. The pipeline flows the new layer name strings through verbatim.

---

## 2. Test Infrastructure from Feature 128

**File**: `tests/scripts/test_backward_compatibility.py`

- **Exists**: Yes
- **Purpose**: Byte-identical PDF guarantee test — compares freshly-generated PDFs against committed baselines
- **SOURCE_DATE_EPOCH**: Line 36 — `SOURCE_DATE_EPOCH = "1700000000"` (matches ADR-021 convention)
- **Baselines tested** (lines 38-44): `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`
- **Explicit exclusion**: `agentic-app` is excluded (line 17 comment) — it's the regeneration target for Feature 128's executive-architecture template

**Implication for spec**: The backward compatibility test is the byte-determinism gate. After FR-1/FR-2/FR-3 edits, running this test against regenerated baselines validates FR-4. Note the agentic-app exclusion — that example's `sample-report/` is manually regenerated and not gated by the backward compatibility test.

**No dedicated MAESTRO layer tests exist** — MAESTRO test coverage is implicit via the backward compatibility test (baseline PDFs include MAESTRO findings sections).

---

## 3. Golden Fixture Inventory

**Location**: `tests/scripts/fixtures/golden/`

| File | MAESTRO References? | Update Needed? |
|------|--------------------|----------------|
| `baseball-card.json` | No | No |
| `maestro-heatmap.json` | `maestro_layer_distribution: []` (line 101) | Regenerate after layer rename |
| `maestro-stack.json` | `maestro_layer_distribution: []` (line 100) | Regenerate after layer rename |
| `risk-funnel.json` | No | No |
| `system-architecture.json` | No | No |

**Implication for spec**: FR-5 (Golden Test Fixture Updates) scope is confirmed — `maestro-heatmap.json` and `maestro-stack.json` only. The fixtures use array-structured data, so regeneration follows the same pattern as example outputs: run the extract scripts and update the committed JSON.

---

## 4. Release-Please Configuration

**Files**: `release-please-config.json`, `.release-please-manifest.json`

- **Current version**: `4.9.2` (from manifest)
- **Release type**: Simple (single package, minor increments)
- **Track**: v4.x.y (minor version bumps for breaking feature work)

**Implication for spec**: A schema enum change (L5/L6/L7 rename) is a breaking change at the enum-value level but triggers a **v4.10.0 minor release** (not a major bump). This resolves the architect's open question about schema bump 1.2 → 1.3 fitting the minor track: it fits cleanly. Plan.md can reference this without requiring a release process change.

---

## 5. ADR-019 Scope and Enum-Value Rule

**File**: `docs/architecture/02_ADRs/ADR-019-shared-definitions-and-model-field-governance.md`

- **Status**: Accepted (2026-04-02)
- **Feature**: 078 (Agent Context Optimization)
- **Scope**: Single-source-of-truth for shared definitions (severity bands, STRIDE categories, finding format); explicit `model:` field governance in agent YAML frontmatter

**Key finding**: ADR-019 does NOT currently contain a rule about enum-value-only breaking changes warranting a minor schema bump. Two possible locations for adding the rule:

1. **ADR-019**: Broader governance document — fits the architect's "one-line rule" recommendation from the PRD review
2. **ADR-020**: MAESTRO-specific — more tightly coupled to the immediate schema change

**Implication for spec**: The spec should define which ADR to update (or create ADR-022 if neither fits). The team-lead review flagged this as a plan.md concern, so the spec can document the addition but defer the specific location decision to plan.md.

---

## 6. Example Regeneration Mechanism

**Finding**: No automated regeneration script or Makefile target exists.

**Current regeneration pattern** (from `test_backward_compatibility.py` lines 65-96):

```bash
SOURCE_DATE_EPOCH=1700000000 python scripts/extract-report-data.py \
  --target-dir <example_dir> \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report

SOURCE_DATE_EPOCH=1700000000 typst compile templates/tachi/security-report/main.typ \
  <example_dir>/security-report.pdf.baseline
```

**Implication for spec**: Regeneration is a manual process per example. The spec should document this workflow and note that plan.md may want to add a `make regenerate-maestro-examples` target to simplify the process.

---

## 7. Hardcoded MAESTRO Layer Name References (Grep Results)

Confirmed hardcoded references that must be updated:

### In Python/script code
**None** — extraction scripts are fully data-driven.

### In shared reference files
- `.claude/skills/tachi-shared/references/maestro-layers-shared.md` lines 17, 34-42, 54-56, 132-149, 150-163, 164-179 (primary target)
- `.claude/skills/tachi-shared/references/finding-format-shared.md` line 64 (enum list)
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md` line 149 (example row)

### In schema
- `schemas/finding.yaml` lines 131-132 (enum values)

### In Typst templates
- `templates/tachi/security-report/maestro-findings.typ` lines 121 (prose), 132-134 (fallback dict — contains third divergent name "Integration Services")
- `templates/tachi/security-report/main.typ` line 293 (prose)

### In documentation
- `README.md` lines 260-262 (layer table)
- `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` line 123 (acronym citation)

### In examples
- All six `examples/*/threats.md` files (component inventory MAESTRO Layer column)
- `examples/agentic-app/sample-report/*` (full pipeline: threats.md, risk-scores.md, compensating-controls.md, threat-report.md, security-report.pdf, threat-*.jpg, threat-*-spec.md)
- `examples/mermaid-agentic-app/threat-report.md`, `threat-infographic-spec.md`
- All six `examples/*/security-report.pdf.baseline` files (regenerate via test framework)

### In test fixtures
- `tests/scripts/fixtures/golden/maestro-heatmap.json`
- `tests/scripts/fixtures/golden/maestro-stack.json`

**Total unique files identified**: ~29 (aligns with team-lead's realistic count from PRD review)

---

## 8. Critical Discoveries

### Discovery 1: Third Divergent Layer Name in Typst Template
`templates/tachi/security-report/maestro-findings.typ` lines 132-134 contain:
```typst
"L5": "Security",
"L6": "Integration Services",    // ← NOT EVEN MATCHING SHARED REF
"L7": "User Interface",
```

The "Integration Services" name exists nowhere else in the codebase. This is a pre-existing internal inconsistency — the Typst template diverged from the shared reference during Feature 091 development. The shared ref calls L6 "Agent Ecosystem" but the Typst template calls it "Integration Services". **Neither is correct per canonical CSA MAESTRO** (correct: "Security and Compliance").

This elevates the correctness scope: we are fixing three divergent references in three places, not just aligning with canonical.

### Discovery 2: agentic-app Sample Report Is Full Pipeline
`examples/agentic-app/sample-report/` contains the only full-pipeline example output in the repo:
- `threats.md` + `threats.sarif`
- `risk-scores.md` + `risk-scores.sarif`
- `compensating-controls.md`
- `threat-report.md`
- `security-report.pdf`
- `threat-*.jpg` (infographic images: baseball-card, risk-funnel, system-architecture, executive-architecture)
- `threat-*-spec.md` (infographic specs)
- `attack-trees/`

Other 5 examples have only `threats.md` + `security-report.pdf.baseline` at their top level. This non-uniformity was verified during the PRD review.

### Discovery 3: Repudiation Finding Does Not Naturally Land in L5
Per the architect's PRD review, the agentic-app example's Audit Logger component has a **Tampering** finding (T-3), not a Repudiation finding. The PRD was corrected to accept any STRIDE category targeting an observability component. Spec acceptance criteria must preserve this flexibility.

---

## 9. Recommendations for Spec

Based on the research, the spec should:

1. **Confirm the data-driven extraction pipeline**: Explicitly state that no Python/script code changes are needed in `scripts/extract-*.py` — only data file and template updates.

2. **Document the backward compatibility test as the byte-determinism gate**: Every regeneration must re-run `test_backward_compatibility.py` with `SOURCE_DATE_EPOCH=1700000000`.

3. **Call out the agentic-app exclusion**: Since agentic-app is excluded from the backward compatibility test, its `sample-report/` regeneration is manually validated via spot-check (Audit Logger finding → L5 — Evaluation and Observability).

4. **Pin the release track**: Note that the schema bump targets v4.10.0 minor, consistent with release-please-config.json, and this avoids a major version change.

5. **Acknowledge no automated regen script**: Either add a `make regenerate-maestro-examples` target in plan.md, or document the manual command sequence in the spec for tasks.md to follow.

6. **Handle the Typst template third-way bug explicitly**: The spec must treat `templates/tachi/security-report/maestro-findings.typ` lines 132-134 as a 3-value fix (not 2), because "Integration Services" is a third divergent name that needs correcting to "Security and Compliance".

7. **Set scope boundary firmly around the 6 example architectures**: Historical PRDs (084, 091) and historical specs (specs/084-*, specs/091-*) are explicitly excluded. Only the living taxonomy and example outputs are updated.

8. **Wave 0 pre-edit grep is non-negotiable**: Before any file edits begin, the mandatory grep sweep must run with the 7 patterns from PRD FR-9 to catch any missed references. This is the primary risk mitigation for the single-coordinated-PR constraint.

9. **Defer ADR-019 vs ADR-020 decision to plan.md**: The spec documents that a one-line rule must be added somewhere; plan.md decides exactly where.

10. **Do not touch internal Python variable names**: Per the PRD open-question resolution, only user-facing strings and data files change. Any Python variables like `security_layer` or similar are out of scope.

---

## Summary

The research confirms the PRD's scope is accurate and implementable in a single coordinated PR. The main risks are:

- **Risk A** (low): Hidden hardcoded references not yet found — mitigated by FR-9 Wave 0 grep
- **Risk B** (low): `dashboard` keyword misclassifies an example component — mitigated by pre-validation in FR-9
- **Risk C** (medium): PDF baselines fail byte-determinism after regeneration — mitigated by explicit `test_backward_compatibility.py` validation
- **Risk D** (low): Typst template fallback dictionary update missed — mitigated by FR-6 explicit line-by-line table

The research surfaces no new blockers. Proceed to spec drafting.
