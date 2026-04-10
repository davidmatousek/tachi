---
prd_reference: docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Initial review returned 5 concerns (1H, 1M, 3L). All addressed inline: FR-036 added for skill references; explicit Out of Scope section added with PRD Open Question #2 (severity legend) deferred per PM recommendation; MAESTRO disambiguation added to Architectural Layer entity; PRD Open Question Resolutions section added cross-referencing FR-009/FR-016 for callout rewriting. Full review at .aod/results/product-manager.md."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Executive Threat Architecture Infographic

**Feature Branch**: `128-prd-128-executive`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "PRD: 128 - Executive Threat Architecture Infographic"
**PRD**: [docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md](../../docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate executive-architecture infographic from threat model output (Priority: P1)

A security consultant runs `/tachi.infographic --template executive-architecture` against an existing tachi threat model output folder. The pipeline produces a markdown specification (`threat-executive-architecture-spec.md`) and a JPEG image (`threat-executive-architecture.jpg`) showing the system architecture as ordered horizontal layers, with Critical and High severity findings overlaid as narrative callout boxes pointing at the layers they affect.

**Why this priority**: This is the foundational deliverable. Without the template, none of the downstream PDF integration matters. The infographic is also the standalone artifact a consultant can use in slide decks even before the report integration is complete.

**Independent Test**: Run `/tachi.infographic --template executive-architecture` against `examples/agentic-app/sample-report/`. Verify that `threat-executive-architecture-spec.md` is created with the required sections and that `threat-executive-architecture.jpg` is generated (or that the spec exists even if image generation fails — spec-first principle).

**Acceptance Scenarios**:

1. **Given** a threat model output folder containing `threats.md` with at least one Critical or High finding and trust boundary data, **When** I run `/tachi.infographic --template executive-architecture`, **Then** a spec file `threat-executive-architecture-spec.md` is created in the output folder containing all six required sections (Metadata, Architecture Layers, Threat Callouts, Severity Distribution, Visual Layout Directives, Gemini Prompt Notes)
2. **Given** the spec file exists, **When** the agent invokes Gemini image generation, **Then** a `threat-executive-architecture.jpg` file is produced in the same output folder
3. **Given** image generation fails (Gemini API error or quota exhaustion), **When** the command completes, **Then** the spec file still exists and the command exit code is 0 (spec-first behavior)
4. **Given** a threat model with mixed severity findings (Critical, High, Medium, Low, Note), **When** the extraction runs, **Then** only Critical and High severity findings appear in the threat callouts section
5. **Given** an architectural layer contains multiple Critical/High findings, **When** the extraction runs, **Then** exactly one finding (the highest severity, then lowest finding ID for tie-break) is selected as that layer's callout

---

### User Story 2 - Executive architecture page appears immediately after Executive Summary in PDF report (Priority: P1)

A security consultant runs `/tachi.security-report` after generating the executive-architecture infographic. The compiled PDF places the executive architecture page directly after the Executive Summary, before the Attack Path Analysis section, so a CISO reading only the first few pages of the report sees the visual threat narrative within their normal attention window.

**Why this priority**: This is the entire raison d'être of F-128. The PDF integration is what moves the visual from "page 10+" (where executives don't reach) to "pages 2–3" (where they do). Without this, the new template provides no audience-impact value.

**Independent Test**: Generate the executive-architecture image, then compile the PDF report. Open the PDF and verify the executive architecture page is the page immediately after the Executive Summary. Compare against a baseline PDF (same example, no executive architecture image) to confirm only the new page is added — no other pages move or change.

**Acceptance Scenarios**:

1. **Given** an output folder containing both an Executive Summary and a `threat-executive-architecture.jpg`, **When** the PDF is compiled, **Then** the executive architecture page is the page immediately after the Executive Summary page and immediately before the Attack Path Analysis section divider (or, if no attack paths exist, before the next section)
2. **Given** an output folder with no `threat-executive-architecture.jpg`, **When** the PDF is compiled, **Then** the report renders identically to its current behavior (no blank page, no error, identical page count to a pre-F-128 baseline)
3. **Given** the executive architecture page is included, **When** the page is rendered, **Then** it shows the JPEG full-width with a TOC-visible heading "Executive Threat Architecture", standard header/footer, and a brief descriptive caption
4. **Given** all 6 existing example outputs, **When** the PDF report is compiled WITHOUT running `/tachi.infographic --template executive-architecture` first, **Then** every example PDF is byte-identical to the pre-F-128 baseline

---

### User Story 3 - The `all` shorthand includes the executive-architecture template (Priority: P2)

A security consultant runs `/tachi.infographic --template all` to generate every infographic in a single invocation. The expansion now includes `executive-architecture` alongside the existing 5 templates, so consultants get the full set without remembering to add it explicitly.

**Why this priority**: This is convenience and discoverability — consultants who use the `all` shorthand should not need to learn a new flag. P2 because the standalone template selection (US-1) already exposes the feature; the `all` integration accelerates adoption.

**Independent Test**: Run `/tachi.infographic --template all` against an example threat model. Verify that 6 spec files are produced (one per template) and that the executive-architecture spec is among them.

**Acceptance Scenarios**:

1. **Given** the `all` shorthand is invoked, **When** template expansion runs, **Then** the expanded list includes `executive-architecture` along with `baseball-card`, `system-architecture`, `risk-funnel`, and any conditionally-included MAESTRO templates
2. **Given** the `executive-architecture` shorthand is invoked directly (not via `all`), **When** dispatched, **Then** it maps to a single template (it is not a compound shorthand like `maestro` which expands to two templates)
3. **Given** an `exec` alias exists, **When** I run `/tachi.infographic --template exec`, **Then** it dispatches to `executive-architecture` (P1 of PRD-128 includes this alias as Should Have)

---

### User Story 4 - Template gracefully handles threat models with no qualifying findings (Priority: P2)

A security consultant runs the executive-architecture template against a threat model that contains only Medium, Low, and Note severity findings (no Critical or High). The extraction script reports "no qualifying findings" and exits without error. No spec file is corrupted, no malformed image is produced, and downstream PDF compilation continues normally.

**Why this priority**: Reliability is essential. The pipeline must not fail or produce garbage when input data does not meet the template's filtering criteria. P2 because most real assessments include Critical/High findings; this is a defensive scenario.

**Independent Test**: Construct a synthetic threat model with only Medium-and-below severity findings. Run the executive-architecture template. Verify the script exits cleanly with an informational message and no JPEG is produced.

**Acceptance Scenarios**:

1. **Given** a threat model with 0 Critical and 0 High severity findings, **When** the extraction runs, **Then** the spec file is created with an empty `Threat Callouts` section and a `skip_image: true` flag in the metadata
2. **Given** `skip_image: true` in the spec, **When** the agent processes the spec, **Then** no Gemini image generation is attempted
3. **Given** no `threat-executive-architecture.jpg` exists, **When** the PDF report is compiled, **Then** the executive architecture page is omitted (boolean gating works as expected)

---

### Edge Cases

- **Empty threat model**: Threat model with no findings at all → extraction returns empty payload, spec is generated with explanatory note, no image, page omitted from PDF
- **No trust boundaries in threats.md**: Section 2 missing or empty → fall back to grouping components by DFD type from Section 1; if Section 1 also missing, exit with error code 2 (validation failure)
- **Single architectural layer**: Threat model with only one trust zone → spec produces one layer with one callout (if any C/H finding exists); the layout still renders correctly as a single horizontal band
- **All findings concentrated in one layer**: All 12 Critical/High findings sit in one trust zone → only the top 1 is shown for that layer (one-callout-per-layer rule); the other 11 are NOT shown (executive simplicity); a metadata field records the total filtered count
- **Layer name longer than 50 characters**: Truncate to 50 with ellipsis in spec output; Gemini prompt includes a hint to use a shortened label
- **Callout finding description longer than 25 words**: Extraction outputs the raw description; the agent's Gemini prompt instructs the model to rewrite to ≤25 words plain English (rewriting happens at image-generation time, not extraction time, per architect concern)
- **Image generation fails after spec creation**: Spec file remains in output folder; PDF compilation skips the executive architecture page because the JPEG is missing; user can re-run image generation independently
- **Layers with zero qualifying findings**: Layer is shown in the architecture diagram (so the system structure is complete) but has no callout box
- **Output folder permissions denied**: Extraction script exits with code 2 (validation failure) and prints a clear error message
- **Backward compatibility regression**: Re-running PDF compilation on any of the 6 existing examples WITHOUT generating the executive-architecture image must produce a byte-identical PDF to the pre-F-128 baseline

## Requirements *(mandatory)*

### Functional Requirements

#### Extraction (`scripts/extract-infographic-data.py`)

- **FR-001**: System MUST add `executive-architecture` to the argparse `--template` choices alongside the existing 5 templates
- **FR-002**: System MUST add a new template dispatch branch in the extraction logic that builds an executive-architecture data payload when the template is selected
- **FR-003**: System MUST parse architectural layers from the threat model output, using trust boundaries (threats.md Section 2) as the primary source and component grouping by DFD type (threats.md Section 1) as a fallback when no trust boundaries exist
- **FR-004**: System MUST filter findings to Critical and High severity only when building the executive-architecture payload
- **FR-005**: System MUST select at most one finding per architectural layer, ranked by severity descending (Critical before High), then by composite risk score descending (if available from compensating-controls or risk-scores tier), then by finding ID ascending for deterministic tie-breaking
- **FR-006**: System MUST follow the existing tier detection order (compensating-controls.md > risk-scores.md > threats.md) when sourcing finding data
- **FR-007**: System MUST output a JSON payload structured as: `layers[]` (ordered list of layer name + component list + component count), `callouts[]` (one entry per layer that has a qualifying finding, containing finding ID, severity, layer reference, raw description), `severity_distribution` (Critical/High counts only), `metadata` (template name, tier source, source file path, generation timestamp, total filtered count, qualifying layer count)
- **FR-008**: System MUST emit `skip_image: true` in the metadata when zero Critical/High findings exist, and produce a spec file with an empty callouts section and an explanatory note
- **FR-009**: System MUST NOT rewrite finding descriptions during extraction; raw descriptions are passed through unchanged for downstream processing by the agent
- **FR-010**: System MUST NOT modify the existing extraction branches for the other 5 templates
- **FR-011**: System MUST exit with code 0 on success, code 1 if `threats.md` is missing, code 2 on validation failure (e.g., no scope data parseable from threats.md)
- **FR-012**: System extraction logic for executive-architecture MUST add no more than 2 seconds of runtime to the script when invoked

#### Spec Generation (`.claude/agents/tachi/threat-infographic.md`)

- **FR-013**: System MUST add `executive-architecture` to the agent's available templates list with a one-line description of its purpose
- **FR-014**: System MUST define a six-section spec structure for the executive-architecture template: Metadata, Architecture Layers, Threat Callouts, Severity Distribution, Visual Layout Directives, Gemini Prompt Construction Notes
- **FR-015**: System MUST construct the Gemini prompt to specify: portrait orientation, ordered horizontal architecture layers (top to bottom following trust hierarchy: trusted → semi-trusted → untrusted), pastel layer fills, red dashed-border callout boxes with warning icons connected to the layers they affect, plain-English narrative inside callouts (≤25 words per callout, jargon-free), large readable typography suitable for projection or printing
- **FR-016**: System MUST instruct the Gemini prompt to rewrite raw finding descriptions to ≤25 words in plain English, removing technical jargon
- **FR-017**: System MUST produce the spec file at `{output_folder}/threat-executive-architecture-spec.md`
- **FR-018**: System MUST produce the image (when not skipped) at `{output_folder}/threat-executive-architecture.jpg`

#### Command Dispatch (`.claude/commands/tachi.infographic.md`)

- **FR-019**: System MUST add `executive-architecture` to the valid template list in the command's argument validation
- **FR-020**: System MUST add `exec` as an alias that dispatches to `executive-architecture` (single template, not compound)
- **FR-021**: System MUST include `executive-architecture` in the `all` shorthand expansion alongside the existing base templates, before the conditional MAESTRO additions
- **FR-022**: System MUST NOT change the behavior of the existing `maestro` compound shorthand or the existing template names

#### Schema (`schemas/infographic.yaml`)

- **FR-023**: System MUST add `executive-architecture` to the schema's template enumeration
- **FR-024**: System MUST document the six-section structure for the executive-architecture template in the schema, including the portrait orientation directive (distinct from the existing 16:9 landscape default)

#### PDF Report Integration

- **FR-025**: System MUST add image detection for `threat-executive-architecture.jpg` to the existing detection function in `scripts/extract-report-data.py`, following the same exists-and-non-zero-size pattern used for `threat-baseball-card.jpg`, `threat-system-architecture.jpg`, etc.
- **FR-026**: System MUST set a new boolean `has-executive-architecture` in the generated `report-data.typ` file based on detection success
- **FR-027**: System MUST set a new string `executive-architecture-image-path` in `report-data.typ` containing the relative path from template directory to the JPEG
- **FR-028**: System MUST add a Typst page rendering call in `templates/tachi/security-report/main.typ` that REUSES the existing `infographic-page()` function (which is already portrait), gated by `#if has-executive-architecture`, positioned immediately after the Executive Summary page and immediately before the Attack Path Analysis conditional block
- **FR-029**: System MUST include a TOC-visible heading "Executive Threat Architecture" and a brief descriptive caption on the rendered page
- **FR-030**: System MUST update the artifact detection table in `.claude/agents/tachi/report-assembler.md` to document the new `threat-executive-architecture.jpg` artifact and the `has-executive-architecture` flag

#### Backward Compatibility

- **FR-031**: System MUST render all 6 existing example PDFs byte-identical to their pre-F-128 baseline when the executive-architecture image is absent
- **FR-032**: System MUST NOT introduce any new required dependencies, new environment variables, or new file format requirements
- **FR-033**: System MUST preserve the existing infographic spec format for the other 5 templates without changes

#### Example Regeneration

- **FR-034**: System MUST regenerate the `examples/agentic-app/sample-report/` example outputs with the new template (spec file + JPEG) and an updated PDF report
- **FR-035**: System MUST NOT regenerate the other 5 examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice); they remain on the pre-F-128 baseline to validate backward compatibility

#### Documentation

- **FR-036**: System MUST update `.claude/skills/tachi-infographics/` reference files to document the new `executive-architecture` template alongside the existing 5 templates, including its purpose, parameters, output artifacts, and the PDF positioning behavior

### Out of Scope

The following items are explicitly excluded from F-128 to maintain executive simplicity, scope discipline, and backward compatibility:

- **Interactive or animated infographic variants**: All infographics in tachi are static images. Interactive variants are deferred indefinitely.
- **Custom architectural layer ordering configuration**: Layer order is derived deterministically from the trust hierarchy (trusted → semi-trusted → untrusted) parsed from `threats.md` Section 2. No user-facing override is provided.
- **Multi-page executive architecture**: The executive architecture infographic is constrained to a single PDF page. If a system has too many layers to fit on one page, the spec includes guidance to truncate or aggregate at extraction time rather than spill onto a second page.
- **Changes to the existing 5 infographic templates or their PDF positioning**: The other 5 templates (`baseball-card`, `system-architecture`, `risk-funnel`, `maestro-stack`, `maestro-heatmap`) and their existing page positions in the PDF report remain unchanged.
- **Mini severity legend or color-key on the executive architecture page**: PM decision on PRD Open Question #2 — *deferred*. Rationale: an executive-audience visual prioritizes the "show fewer things" principle from executive dashboard design research; red dashed-border callouts with warning icons are universally read as "warning / attack surface" without requiring a legend. If post-launch usability feedback shows that executives cannot distinguish Critical from High severity without a legend, a follow-up feature can add one.
- **Changes to the Gemini API integration or any new image-generation dependencies**: F-128 reuses the existing Gemini integration via the `tachi-threat-infographic` agent.
- **Changes to the threat model output schema (`threats.md`)**: All required data is parsed from existing fields. No new sections or fields are added.

### Key Entities

- **Architectural Layer**: A grouping of system components by trust zone (preferred) or by DFD component type (fallback). Has a name (e.g., "Untrusted Edge", "Application Tier", "Data Store"), a list of contained components, and a position in the trust hierarchy (untrusted at top or bottom — direction TBD by Gemini prompt design). Source: parsed from threats.md Section 2 trust boundaries. **Distinct from MAESTRO layers**: an Architectural Layer is a trust-zone grouping derived from DFD scope data and is NOT the same concept as a MAESTRO layer (CSA seven-layer agentic AI taxonomy: L1 Foundation Model through L7 User Interface) introduced in Feature 084. The two concepts coexist independently — F-128 uses Architectural Layers exclusively; the MAESTRO templates (`maestro-stack`, `maestro-heatmap`) continue to use MAESTRO layers exclusively.
- **Threat Callout**: A narrative annotation attached to one architectural layer, representing the single highest-severity Critical/High finding affecting that layer. Contains the finding's ID, severity, raw description (rewritten by Gemini to ≤25 words plain English), and a visual link to the layer.
- **Executive Architecture Spec**: A markdown file (`threat-executive-architecture-spec.md`) containing six sections: Metadata, Architecture Layers, Threat Callouts, Severity Distribution, Visual Layout Directives, Gemini Prompt Construction Notes. Conforms to the `infographic.yaml` schema (with extensions for the new template).
- **Executive Architecture Image**: A JPEG file (`threat-executive-architecture.jpg`) generated by Gemini from the spec file, in portrait orientation, depicting the layered architecture with overlaid threat callouts. Optional artifact (spec-first behavior); image generation failure does not block spec creation.
- **Has-Executive-Architecture Flag**: A boolean variable in the generated `report-data.typ` file, set by `extract-report-data.py` based on the detected presence of `threat-executive-architecture.jpg`. Used by `main.typ` to conditionally include the executive architecture page in the compiled PDF.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a threat model with at least one Critical or High finding and parseable scope data is processed, the executive-architecture spec file is generated successfully on 100% of runs
- **SC-002**: When the executive-architecture image exists, it appears in the compiled PDF on the page immediately following the Executive Summary on 100% of runs (verified across all examples that have the image generated)
- **SC-003**: When the executive-architecture image is absent, the compiled PDF is byte-identical to the pre-F-128 baseline on 100% of the 5 examples not selected for regeneration (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice)
- **SC-004**: A non-technical reader (CISO, board member) viewing only the first 3 pages of a regenerated agentic-app PDF can identify the system's most exposed architectural layer in under 30 seconds without consulting any other section
- **SC-005**: The extraction script's runtime for the executive-architecture template is within 2 seconds of the baseline runtime measured before the addition (no performance regression to other templates)
- **SC-006**: All existing automated tests for the 5 prior infographic templates continue to pass without modification
- **SC-007**: When invoked with `--template all`, the command produces 6 spec files instead of the previous 5 (or 5+MAESTRO when applicable) with no manual intervention required
- **SC-008**: When invoked against a synthetic threat model with zero Critical/High findings, the script exits cleanly with code 0 and produces a spec file with `skip_image: true`, and no JPEG is generated
- **SC-009**: When invoked against a threat model with no parseable scope data, the script exits with code 2 and prints an actionable error message identifying the missing Section 1/Section 2 content

### Assumptions

- Trust boundaries in threats.md Section 2 are sufficient to derive meaningful "architectural layers" for executive presentation. If real-world examples reveal that trust zones are too coarse or too fine, the fallback to component grouping by DFD type provides a second option.
- Gemini API can produce a coherent layered architecture diagram with overlay callouts via prompt engineering. If image quality is insufficient, the spec-first principle ensures the markdown spec is still usable for manual diagram creation.
- The existing `infographic-page()` Typst function (already portrait) is suitable for the executive architecture page without modification. If the layout needs adjustment (e.g., a custom header style), a minor variant function may be added later, but is not required by F-128.
- Re-running the agentic-app example through the full pipeline produces consistent enough output that the regenerated example can be checked into the repository as the new baseline.
- One Critical/High finding per layer is sufficient executive-level granularity. Showing more than one callout per layer would clutter the visual and contradict the "show fewer things" executive design principle.

### PRD Open Question Resolutions

The PRD listed two open questions at the time of sign-off. Both are resolved here so the spec is unambiguous before plan generation:

- **PRD Open Question #1** *(architect, was TBD)*: "Should the callout text be auto-generated from finding descriptions or require a narrative rewrite?"
  - **Resolution**: Split between extraction and image generation. Extraction (FR-009) passes raw finding descriptions through unchanged. The agent's Gemini prompt (FR-016) instructs the model to rewrite each description to ≤25 words in plain English, removing technical jargon. This keeps extraction deterministic per ADR-017 and places the natural-language rewriting where the LLM already operates.
- **PRD Open Question #2** *(product-manager, was TBD)*: "Should the page include a mini severity legend/key?"
  - **Resolution**: **Deferred out of scope** for F-128 (see Out of Scope section above). Rationale: red dashed-border callouts with warning icons are universally read as "warning / attack surface" without requiring a legend, and an executive-audience visual prioritizes the "show fewer things" principle. Revisit only if usability feedback shows confusion between Critical and High.
