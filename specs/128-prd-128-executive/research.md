# Research Summary: Executive Threat Architecture Infographic (F-128)

**Created**: 2026-04-09
**PRD**: [docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md](../../docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md)

---

## 1. Codebase Analysis

### Existing Infographic Templates (5)

| Template | Extraction | Spec Generation | Notes |
|----------|------------|-----------------|-------|
| baseball-card | `extract-infographic-data.py:1281-1282` (inline) | agent template | Risk summary dashboard |
| system-architecture | `compute_architecture_overlay()` line 587 | agent template | Uses trust zones |
| risk-funnel | `compute_risk_funnel()` line 1291 | agent template | 4-tier funnel |
| maestro-stack | `extract_maestro_data()` line 1117 | agent template | F-091, layered MAESTRO L1-L7 |
| maestro-heatmap | `extract_maestro_data()` line 1117 | agent template | F-091, component x layer grid |

**Dispatch**:
- Argparse choices: `scripts/extract-infographic-data.py:1195`
- Template selection branching: `scripts/extract-infographic-data.py:1274-1334`
- Command shorthand expansion: `.claude/commands/tachi.infographic.md:17,19,162-164`
- `all` shorthand: expands to baseball-card, system-architecture, risk-funnel + conditionally MAESTRO if data present

### F-091 Pattern (most recent template addition)

This is the canonical pattern Feature 128 must follow:

1. **Add template name to argparse choices** in extract-infographic-data.py
2. **Add extraction branch** in the template dispatch (lines 1274-1334)
3. **Implement extraction function** that returns a JSON payload
4. **Update `.claude/commands/tachi.infographic.md`** with new template + alias if needed
5. **Update `.claude/agents/tachi/threat-infographic.md`** with new spec template structure
6. **Update `schemas/infographic.yaml`** with new template enumeration
7. **Update `all` shorthand** to include new template
8. **Regenerate example outputs**

### F-112 Pattern (most recent PDF page sequencing change)

Used for inserting new pages at specific positions:

1. **New Typst page template file**: `templates/tachi/security-report/{page-name}.typ`
2. **Boolean flag** in report-data.typ: `has-{feature-name}` set by extract-report-data.py
3. **Image detection** in extract-report-data.py: looks for specific JPEG with non-zero size
4. **Conditional inclusion** in main.typ: `#if has-{feature-name} { ... }`
5. **Position in main.typ** sequence: insert at specific point
6. **Update artifact detection table** in `.claude/agents/tachi/report-assembler.md`

### Critical Architectural Findings

**`infographic-page()` is ALREADY portrait** (`templates/tachi/security-report/full-bleed.typ:40-86`):
- Uses standard US Letter portrait page
- Standard margins, header, footer
- Image with `width: 100%, fit: "contain"`
- Verifies team-lead concern: "portrait risk is misframed — Typst pages already portrait"
- **Implication**: Can REUSE `infographic-page()` for executive architecture; the real risk is Gemini prompt engineering, not page geometry

**`full-bleed-page()` is the legacy 16:9 landscape function** (`templates/tachi/security-report/full-bleed.typ:95-112`):
- Used for older landscape full-bleed infographics
- Not used in current default page sequence

**Current Executive Summary position** (`templates/tachi/security-report/main.typ`):
- Page 6 (after Cover, Disclaimer, TOC, Methodology, Scope)
- Lines 182-191 in main.typ
- **Insertion target for F-128**: Immediately after line 191, before Attack Path Analysis (line 197)

### DFD Scope Parsing

**`parse_scope_data()` in `scripts/tachi_parsers.py:572-626`**:
- Parses Section 1 (components, data flows) and Section 2 (trust boundaries) of threats.md
- Returns: `components[]`, `data_flows[]`, `trust_boundaries[]`, `boundary_crossings[]`

**`compute_architecture_overlay()` in `scripts/extract-infographic-data.py:587-617`**:
- Currently the only consumer of trust boundary data for visual layering
- Maps components to trust zones via `_compute_trust_zones()` (lines 620-655)
- Sort order: `trusted < semi-trusted < untrusted` (line 584)

**Architectural layers concept resolution**:
- Trust zones from Section 2 are the existing concept of "layers"
- DFD Section 1 components can also be grouped by tier from their `type` field
- MAESTRO layers (L1-L7) are a SEPARATE concept used only by MAESTRO templates
- Feature 128 should use **trust zones first**, fall back to **component grouping by type** if zones absent

### Severity Filtering

- **`select_top_findings()` in extract-infographic-data.py:281-332**: excludes Note, returns top 5 by score descending
- **No existing Critical/High-only filter** — needs to be added for F-128 (one finding per layer)
- Severity ordinal mapping exists in `_SEVERITY_ORDINAL` constant for sorting

### Boolean Gating Pattern

**`extract-report-data.py:797-830`** detects images via `detect_images()`:
- Looks for `threat-{template-name}.jpg`, checks file exists AND size > 0
- Computes relative path from template_dir to target_dir

**`extract-report-data.py:940-942, 1062, 1092-1100`** writes flags:
```python
lines.append(f"#let has-funnel-image = {_typst_bool(art['funnel_image'])}")
lines.append(f"#let has-attack-trees = {_typst_bool(data.get('has_attack_trees', False))}")
```

**`tachi_parsers.py:323-364`** detect_artifacts() — note: MAESTRO image detection NOT in this function (only in extract-report-data.py); attack tree detection IS here. Pattern is divided.

### Example Outputs

- Primary example: `examples/agentic-app/sample-report/`
- Currently has: baseball-card, system-architecture, risk-funnel images
- **Missing**: MAESTRO images (F-091 not regenerated); will need executive-architecture image after F-128
- Test output: `examples/agentic-app/test-output/2026-03-25T12-53-57/` (older, no MAESTRO)

---

## 2. Architecture Constraints

### Mandatory ADRs

- **ADR-014: Spec-First Architecture** — specification markdown is primary deliverable; image generation is best-effort
- **ADR-016: Standalone Command Pattern** — `/tachi.infographic` is decoupled from pipeline orchestrator
- **ADR-017: Deterministic Extraction** — Python scripts only, byte-identical output on identical input, NO LLM in extraction
- **ADR-019: Schema-First Development** — schemas/*.yaml define structures before code

### Constitution Principles (apply to F-128)

- **III. Backward Compatibility (NON-NEGOTIABLE)**: All existing reports without `threat-executive-architecture.jpg` must render identically
- **VI. Testing Excellence**: ≥80% unit test coverage for extraction script
- **VII. Definition of Done (NON-NEGOTIABLE)**: Pushed → Tested → User Validated
- **IX. Git Workflow**: Feature branch `128-*`, conventional commits
- **X. Product-Spec Alignment**: PRD-128 has Triad sign-offs (PM APPROVED, Architect/Tech-Lead APPROVED_WITH_CONCERNS, all resolvable in plan)

### Pipeline Constraints

- **Tier detection order**: compensating-controls.md > risk-scores.md > threats.md (3-tier)
- **Largest Remainder Method** for percentages (deterministic, sums to exactly 100)
- **Cross-output consistency**: severity counts MUST match `extract-report-data.py` output
- **Exit codes**: 0=success, 1=missing threats.md, 2=validation failure
- **JSON output format** from extraction script (consumed by agent)

---

## 3. Industry Research

**Source**: [The Executive Security Dashboard (Medium)](https://medium.com/@SecurityArchitect/the-executive-security-dashboard-visualizing-what-matters-without-the-noise-d46efb31c5aa), [10 Cybersecurity Dashboard Design Examples (DesignMonks)](https://www.designmonks.co/blog/10-cybersecurity-dashboard-design-examples-for-design-inspiration), [9 Tips for Creating an Excellent CISO Dashboard (Vistrada)](https://vistrada.com/resources/insights/tips-for-creating-an-excellent-ciso-dashboard)

### Executive Dashboard Design Principles

1. **Time budget**: Executives spend 2–5 minutes reviewing security artifacts. Visuals must communicate the gist within 30 seconds.
2. **Decision-grade, not pretty**: The goal is empowering governance decisions, not aesthetics.
3. **Status indicators**: Traffic light (R/Y/G) and severity color coding work universally.
4. **Trend over absolute counts**: Direction matters more than magnitude for executive audiences.
5. **Business language**: Translate technical findings into operational/economic language CISOs and boards understand.
6. **Show fewer things**: Failed dashboards try to show everything; effective ones surface the 3–5 things that drive decisions.

### Application to F-128

- **One callout per architectural layer** (max ~5–6 layers): Aligns with "show fewer things"
- **Critical/High only**: Filters to decision-grade findings, removes noise
- **Plain English ≤25 words**: Removes technical jargon for executive audience
- **Pages 2–3 placement**: Within the 2–5 minute attention window
- **Architecture diagram with overlays**: Visual narrative ("here is the system, here is where it breaks") matches executive cognition

---

## 4. Knowledge Base Findings

No prior bug fixes or KB entries directly relevant to F-128 (this is a net-new template + page). Lessons applicable from related features:

- **F-091 (MAESTRO templates)**: Boolean gating pattern works well; example regeneration is the slowest part of the build
- **F-112 (Attack path pages)**: Conditional page insertion has been validated for early-page positioning
- **F-071 (Deterministic extraction)**: Adding new template branches to extract-infographic-data.py is low-risk if dispatch pattern is followed exactly

---

## 5. Recommendations for Spec

### Architectural Decisions (resolve Triad concerns)

1. **Reuse `infographic-page()`** — it's already portrait, a new function is unnecessary
2. **Define "architectural layer"** = trust zone from threats.md Section 2 (with fallback to component grouping by DFD type if no zones)
3. **Callout text generation** = generated by extraction (one Critical/High finding per layer with the finding's title/description) and rewritten to ≤25 words plain English by the agent + Gemini prompt
4. **Severity mini-legend on the page** = include a small key in the Typst page (not in the Gemini image) for clarity

### Scope Boundaries

- New extraction branch in extract-infographic-data.py (additive, no changes to existing branches)
- New spec template section in threat-infographic.md agent
- New Typst page that REUSES `infographic-page()` for layout
- New `has-executive-architecture` boolean
- New entries in detect_images() and report-data.typ
- Schema update for new template enumeration
- Regenerate `agentic-app` example only (not all 6 examples)

### Out of Scope

- Custom layer ordering UI
- Multi-page executive architecture (single page only)
- Animated/interactive variants
- Changes to existing 5 templates or their positioning

### Testing Strategy

- Unit tests for new extraction function (Critical/High filtering, layer grouping, callout text generation)
- Integration test: run full /tachi.infographic + /tachi.security-report on agentic-app, verify executive-architecture appears between Executive Summary and Attack Paths
- Backward compatibility test: run report on examples WITHOUT executive-architecture image, verify identical PDF output
- Edge case: 0 Critical/High findings produces graceful skip
- Edge case: 0 trust zones falls back to component grouping
