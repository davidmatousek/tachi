---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All 15 spec FRs covered, 4 user stories addressed, 6 success criteria achievable. No scope creep. Plan components map cleanly to spec requirements."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. 2 medium concerns addressed in plan revision: (C-1) detect_artifacts() update in tachi_parsers.py now documented, (C-2) narrative/remediation content sourcing now explicit. Low concerns (tempfile usage, page placement, example filtering) noted for implementation."
  techlead_signoff: null
---

# Implementation Plan: Attack Path Pages in Security Report PDF

**Branch**: `112-attack-path-pages` | **Date**: 2026-04-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/112-attack-path-pages/spec.md`

## Summary

Add dedicated pages in the security report PDF that visualize each Critical and High attack path with a rendered Mermaid diagram, narrative explanation, and remediation plan. Extends the existing deterministic extraction pipeline (`extract-report-data.py`) to parse attack tree files, render Mermaid to PNG via `mmdc`, and output structured data for a new Typst page template (`attack-path.typ`). Follows the established conditional page pattern (`has-attack-trees` boolean flag) for backward-compatible inclusion.

## Technical Context

**Language/Version**: Python 3.11 (extraction script), Typst (page template)
**Primary Dependencies**: `tachi_parsers.py` (shared parsing), `mmdc` (Mermaid CLI, optional), Typst compiler
**Storage**: File-based — attack tree `.md` files in, PNG images + `report-data.typ` out
**Testing**: Manual validation against 6 example outputs in `examples/`
**Target Platform**: macOS/Linux (CLI)
**Performance Goals**: <5s per Mermaid render, <30s total overhead for 5 attack path pages
**Constraints**: Typst cannot render Mermaid natively — requires pre-rendering to PNG; A4/Letter page limits diagram complexity
**Scale/Scope**: Typically 2-8 attack path pages per report (Critical + High findings only)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility | PASS | Conditional page inclusion via `has-attack-trees` flag; existing reports unchanged |
| VII. Definition of Done | PASS | Validation against all 6 example outputs |
| IX. Git Workflow | PASS | Feature branch `112-attack-path-pages` |
| X. Product-Spec Alignment | PASS | Spec PM sign-off APPROVED |

## Components

### Component 1: Attack Tree Data Extraction (Python)

**File**: `scripts/extract-report-data.py`

Extend with new function `parse_attack_trees()` that:
1. Scans `{target_dir}/attack-trees/` for `*-attack-tree.md` files
2. Falls back to inline attack trees in `threat-report.md` Section 5
3. For each file: extracts finding ID, component, severity from metadata table; extracts Mermaid code block
4. Cross-references finding ID with parsed findings data to get authoritative severity and mitigation text
5. Filters to Critical and High only
6. Orders by severity (Critical first) then finding ID
7. Returns structured list of attack tree entries

**Also update** `detect_artifacts()` in `scripts/tachi_parsers.py` to add `attack-trees/` directory detection to the canonical artifact detection entry point, returning a boolean `has_attack_trees` and the directory path.

**Narrative and remediation content sourcing** (architect concern C-2):
- **Narrative**: Derived from the attack tree metadata table (Threat field) combined with the node labels in the Mermaid tree. The extraction function constructs a 2-4 sentence narrative: "An attacker targets {component} via {threat}. The attack chain proceeds through {root node label}, branching via {OR/AND gates} into {sub-goal descriptions}. Leaf actions include {leaf node labels}."
- **Remediation**: Sourced from the corresponding finding's `mitigation` field in the parsed findings data (already extracted by existing `parse_threats_findings()` or `parse_risk_scores_findings()`). The mitigation text is split into individual bullet points at sentence or semicolon boundaries.

**New function**: `render_mermaid_to_png()` that:
1. Checks `mmdc` availability via `shutil.which("mmdc")`
2. Creates a `tempfile.TemporaryDirectory()` for all intermediate `.mmd` and `.png` files
3. For each Mermaid code block: writes `{id}.mmd` file, invokes `mmdc -i {id}.mmd -o {id}.png -s 2 -b transparent`
4. On success: copies PNG to `{target_dir}/attack-trees/{id}-attack-tree.png` for Typst consumption
5. On failure: logs warning, sets `has_image = false` for that entry (raw Mermaid text fallback)
6. Temp directory auto-cleaned on exit via context manager

**Output to `report-data.typ`**: New section with:
- `has-attack-trees` (boolean)
- `attack-trees` (array of dicts with: id, component, severity, title, image-path, has-image, mermaid-text, narrative, remediation)

### Component 2: Attack Path Typst Page Template

**New file**: `templates/tachi/security-report/attack-path.typ`

Exports `attack-path-page(entry, classification)` function that renders:
1. **Header**: `report-header()` with classification bar
2. **Finding badge**: Severity-colored box (using `severity-color()`) with finding ID + title
3. **Diagram section** (~60% page height): If `has-image` is true, renders `#image(image-path)` scaled to fit; else renders raw Mermaid code in `#raw()` block with monospace font
4. **Narrative section**: 2-4 sentence explanation text
5. **Remediation section**: Bulleted list of remediation steps
6. **Footer**: Standard `report-footer()`

Follows patterns from `maestro-findings.typ`: imports `shared.typ`, exports single function, severity badge helper.

### Component 3: Main Orchestrator Update

**File**: `templates/tachi/security-report/main.typ`

Changes:
1. Add `#import "attack-path.typ": attack-path-page` to imports section
2. Add backward-compatible defaults for new variables:
   ```typst
   #let has-attack-trees = if has-attack-trees != none { has-attack-trees } else { false }
   #let attack-trees = if attack-trees != none { attack-trees } else { () }
   ```
3. Insert attack path pages after Executive Summary (line ~187), before infographic pages:
   ```typst
   #if has-attack-trees and attack-trees.len() > 0 {
     section-divider("Attack Path Analysis", classification: classification)
     for entry in attack-trees {
       page(...)[#attack-path-page(entry: entry, classification: classification)]
     }
   }
   ```

### Component 4: Artifact Detection Updates

**File**: `.claude/commands/security-report.md`
- Add `attack-trees/` directory to artifact detection table (optional)
- Add attack path pages to page listing display

**File**: `.claude/agents/tachi/report-assembler.md`
- Add `attack-trees/` to artifact detection step
- Pass `--attack-trees-dir` flag to extraction script (or auto-detect in script)

### Component 5: Example Output Regeneration

Regenerate all 6 example report outputs with the new attack path pages to validate end-to-end pipeline and serve as regression baselines.

## Data Flow

```
attack-trees/*.md ──┐
                     ├──> extract-report-data.py ──> mmdc (PNG) ──> report-data.typ ──> main.typ ──> PDF
threat-report.md ───┘                                                                    ↑
                                                                              attack-path.typ
```

1. **Input**: `attack-trees/{id}-attack-tree.md` files (primary) or `threat-report.md` Section 5 (fallback)
2. **Extraction**: `parse_attack_trees()` in `extract-report-data.py` reads metadata + Mermaid blocks
3. **Rendering**: `render_mermaid_to_png()` converts Mermaid to PNG via `mmdc` subprocess
4. **Data binding**: Attack tree entries written to `report-data.typ` as Typst array
5. **Template**: `attack-path.typ` renders each entry as a portrait page
6. **Orchestration**: `main.typ` conditionally includes section divider + pages

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Extraction | Python 3.11 | Extends existing `extract-report-data.py` |
| Rendering | `mmdc` (Mermaid CLI) | Standard tool for Mermaid-to-image; already used in threat-report references |
| Template | Typst | Extends existing PDF report template system |
| Image format | PNG @ 2x | Per architect guidance; consistent with existing infographic handling |

## Project Structure

### Documentation (this feature)

```
specs/112-attack-path-pages/
├── plan.md              # This file
├── research.md          # Codebase and industry research
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── tasks.md             # Task breakdown (generated by /aod.tasks)
```

### Source Code (repository root)

```
scripts/
└── extract-report-data.py       # EXTEND: parse_attack_trees(), render_mermaid_to_png()

templates/tachi/security-report/
├── attack-path.typ               # NEW: attack path page template
├── main.typ                      # MODIFY: import + page sequencing
└── report-data.typ               # AUTO-GENERATED: new attack tree variables

.claude/
├── agents/tachi/
│   └── report-assembler.md       # MODIFY: artifact detection
└── commands/
    └── security-report.md        # MODIFY: artifact detection table

examples/
├── agentic-app/sample-report/    # REGENERATE: with attack path pages
├── cloud-native/sample-report/   # REGENERATE
├── data-pipeline/sample-report/  # REGENERATE
├── healthcare-ai/sample-report/  # REGENERATE
├── iot-fleet/sample-report/      # REGENERATE
└── rag-chatbot/sample-report/    # REGENERATE
```

**Structure Decision**: No new directories. Extends existing `scripts/`, `templates/`, `.claude/` structure. Single new file: `attack-path.typ`.

## Complexity Tracking

No constitution violations. All changes follow established patterns (conditional page template, extraction script extension, artifact detection update).
