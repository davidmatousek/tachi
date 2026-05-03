---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 5 user stories covered, all 20 FRs addressed, no scope creep. MVP strategy aligns with product priorities."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED
    notes: "Dependencies ordered correctly, parallel opportunities valid, template pattern compliance maintained, data extraction paths match data-model.md. 3 low-severity observations."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED
    notes: "24 tasks appropriate for scope. Critical path identified. Parallelization maximized. Single-session estimate realistic. 2 low/info observations."
---

# Tasks: Risk Reduction Funnel Infographic Template

**Input**: Design documents from `/specs/053-risk-reduction-funnel/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Organization**: Tasks grouped by user story. No tests requested in spec — test tasks omitted.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

**Purpose**: Read reference templates and understand existing patterns before authoring

- [X] T001 Read existing template `.claude/agents/tachi/templates/infographic-baseball-card.md` to establish 9-section pattern, style table format, color palette, typography, and Gemini prompt structure
- [X] T002 [P] Read existing template `.claude/agents/tachi/templates/infographic-system-architecture.md` to understand zone specification depth and spatial layout conventions
- [X] T003 [P] Read infographic agent `.claude/agents/tachi/threat-infographic.md` to understand template registry format, data extraction methodology, and Available Templates table structure
- [X] T004 [P] Read infographic command `.claude/commands/infographic.md` to understand valid template list, argument parsing, and `--template all` behavior

---

## Phase 2: Foundational (Template Skeleton + Registration)

**Purpose**: Create the template file with 9-section skeleton and register it in agent + command so `--template risk-funnel` is invocable. MUST complete before user story work.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create template file `.claude/agents/tachi/templates/infographic-risk-funnel.md` with 9-section skeleton: (1) frontmatter comment with purpose statement, (2) empty ASCII layout placeholder, (3) style table (dark theme #1E293B, 16:9 landscape, card radius 12px, shadow), (4) color palette table (Critical=#DC2626, High=#EA580C, Medium=#CA8A04, Low=#2563EB, Note=#6B7280, ghost=#475569 at 20% opacity, sidebar bg=#334155), (5) typography table matching baseball-card pattern, (6) zone specification headings (Header, Funnel, Metrics Sidebar, Footer), (7) empty Gemini prompt placeholder, (8) Gemini API config block (gemini-3-pro-image-preview, fallback gemini-3.1-flash-image-preview, 16:9, 2K), (9) accessibility section (color+label, 4.5:1 contrast)
- [X] T006 [P] Register `risk-funnel` in infographic agent template registry at `.claude/agents/tachi/threat-infographic.md` — add `risk-funnel: .claude/agents/tachi/templates/infographic-risk-funnel.md` to the `templates:` block in Metadata YAML, update description to mention three templates, add row to Available Templates table: `risk-funnel` | `threat-risk-funnel-spec.md` + `threat-risk-funnel.jpg` | 4-tier vertical funnel showing progressive risk reduction
- [X] T007 [P] Register `risk-funnel` as valid `--template` value in infographic command at `.claude/commands/infographic.md` — add `risk-funnel` to valid values list, update invalid template error message to include `risk-funnel`, update `all` description to note three templates generated

**Checkpoint**: `--template risk-funnel` is now recognized. Template file exists with structure but empty content.

---

## Phase 3: User Story 1 — Full Pipeline Funnel (Priority: P0) MVP

**Goal**: Populate the template with 4-tier vertical funnel layout, zone specifications, and Gemini prompt so that running `/infographic --template risk-funnel` with `compensating-controls.md` produces a complete 4-tier funnel spec.

**Independent Test**: Run `/infographic --template risk-funnel` against any example with `compensating-controls.md` present. Verify spec contains 4 solid funnel tiers, all 6 schema sections, and data-driven tier widths.

### Implementation for User Story 1

- [X] T008 [US1] Write the ASCII layout diagram in `.claude/agents/tachi/templates/infographic-risk-funnel.md` showing 16:9 landscape with Header (~8%), Funnel zone (~62%) containing 4 trapezoid tiers (100%/~75%/~50%/~30% widths), Metrics Sidebar (~20% width, right-aligned), and Footer (~5%). Use the exact diagram from plan.md Component 1 as reference.
- [X] T009 [US1] Write zone specification for HEADER in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — Title "Risk Reduction Funnel" (32px bold, #F8FAFC), project name from `{project_name}`, date from `{date}`, CONFIDENTIAL badge (pill, red bg, white text)
- [X] T010 [US1] Write zone specification for FUNNEL in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — 4 tiers as trapezoids narrowing top-to-bottom: Tier 1 "Threats Identified" (100% width, data: total finding count + qualitative severity from threats.md §6), Tier 2 "Inherent Risk Scored" (~75%, composite score distribution from risk-scores.md §2), Tier 3 "Controls Applied" (~50%, control coverage % from compensating-controls.md §1), Tier 4 "Residual Risk" (~30%, residual severity from compensating-controls.md §2). Specify tier width proportionality with minimum 10% narrowing per tier. Specify gradient connectors between tiers.
- [X] T011 [US1] Write zone specification for FOOTER in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — centered gray text (12px, #94A3B8): "Generated by Tachi Threat Modeling Framework — Risk Reduction Funnel"
- [X] T012 [US1] Write the Gemini Prompt Template section in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — single code block opening with aesthetic intent ("Create a premium, photorealistic 3D risk reduction funnel with glass-like translucent material, soft ambient lighting, and executive boardroom quality"), then per-tier instructions with `{project_name}`, `{date}`, `{total_findings}`, `{tier_1_data}` through `{tier_4_data}`, `{sidebar_metrics}` placeholders. Specify exact hex colors per severity. Use professional business language, no attack terminology.
- [X] T013 [US1] Add funnel-specific data extraction instructions to agent `.claude/agents/tachi/threat-infographic.md` — add a new section "### Risk Funnel Template: Data Extraction" describing: (a) Section 5 uses "funnel-tier" format with tier table (Tier, Label, Width, Severity Counts, Render State), (b) Tier width calculation from data-model.md, (c) data extraction paths per tier from spec FR-017 through FR-020, (d) 4-tier mode instructions when data_source_type is compensating-controls
- [X] T014 [US1] Update `all` template behavior in agent `.claude/agents/tachi/threat-infographic.md` — change sequential generation from "first Baseball Card, then System Architecture" to "first Baseball Card, then System Architecture, then Risk Funnel"

**Checkpoint**: Full 4-tier funnel generates from `compensating-controls.md`. All 6 schema sections present. This is the MVP.

---

## Phase 4: User Story 2 + User Story 3 — Graceful Degradation (Priority: P0)

**Goal**: Add ghost tier rendering and conditional tier labels so the funnel degrades gracefully: 3 solid + 1 ghost from `risk-scores.md`, 1 solid + 3 ghost from `threats.md`.

**Independent Test**: Run `/infographic --template risk-funnel` with only `risk-scores.md` (3-tier) and then with only `threats.md` (1-tier). Verify correct tier counts, ghost tier rendering, and enhancement tips.

### Implementation for User Story 2 (3-tier mode)

- [X] T015 [US2] Add ghost tier specification to FUNNEL zone in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — define ghost tier rendering: dashed border (#475569 Slate-600), 20% opacity fill, CTA text inside tier (white text, 14px), no data content. Specify that ghost tiers maintain funnel shape (same widths as if data were present).
- [X] T016 [US2] Add 3-tier mode instructions to agent `.claude/agents/tachi/threat-infographic.md` in the "Risk Funnel Template: Data Extraction" section — when data_source_type is risk-scores: Tier 1 solid (threats.md §6), Tier 2 solid (risk-scores.md §2), Tier 3 solid with conditional label "Unmitigated Risk" (uses Tier 2 severity data), Tier 4 ghost with CTA "Run /compensating-controls to complete the funnel". Enhancement tip: "Run `/compensating-controls` to unlock the full 4-tier risk reduction funnel"

### Implementation for User Story 3 (1-tier mode)

- [X] T017 [US3] Add 1-tier mode instructions to agent `.claude/agents/tachi/threat-infographic.md` in the "Risk Funnel Template: Data Extraction" section — when data_source_type is threats: Tier 1 solid (threats.md §6 total count + severity distribution), Tiers 2-4 ghost with CTAs: Tier 2 "Run /risk-score", Tier 3 "Run /compensating-controls", Tier 4 "Complete the pipeline". Enhancement tip: "Run `/risk-score` to begin quantifying your risk reduction funnel"
- [X] T018 [US2] [US3] Add ghost tier rendering instructions to Gemini Prompt Template in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — add `{ghost_tier_instructions}` placeholder with conditional rendering: "For tiers marked as ghost, render as translucent dashed outlines with white CTA text centered inside. Ghost tiers should be visually distinct but maintain the funnel shape."

**Checkpoint**: All 3 data source modes produce correct funnel specs. Ghost tiers render with CTAs.

---

## Phase 5: User Story 4 — Funnel Metrics Sidebar (Priority: P1)

**Goal**: Add a right-aligned metrics panel showing aggregate statistics alongside the funnel.

**Independent Test**: Generate funnels in all 3 modes and verify sidebar contains appropriate metrics: full stats in 4-tier mode, partial in 3-tier, minimal in 1-tier.

### Implementation for User Story 4

- [X] T019 [US4] Write zone specification for METRICS SIDEBAR in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — right-aligned panel (~20% width), dark card background (#334155), 12px rounded corners. Content varies by mode: (a) 4-tier: Total Findings, Risk Reduction %, Control Coverage %, severity breakdown per tier, (b) 3-tier: Total Findings, severity distribution, "Risk Reduction: N/A — run /compensating-controls", (c) 1-tier: Total Findings, qualitative severity counts only
- [X] T020 [US4] Add sidebar data extraction to agent `.claude/agents/tachi/threat-infographic.md` in the "Risk Funnel Template: Data Extraction" section — describe how to populate sidebar metrics from each data source: risk_reduction_pct from compensating-controls.md §1 (delta between inherent and residual), control_coverage_pct from compensating-controls.md §1, severity_breakdown per tier from tier data
- [X] T021 [US4] Add `{sidebar_metrics}` placeholder population instructions to Gemini Prompt Template in `.claude/agents/tachi/templates/infographic-risk-funnel.md` — per-mode sidebar content with metric labels and values, percentage annotations between tiers showing stage-to-stage reduction

**Checkpoint**: Metrics sidebar renders with mode-appropriate content in all 3 data source modes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, edge cases, backward compatibility verification

- [X] T022 [P] Add edge case handling to agent `.claude/agents/tachi/threat-infographic.md` in the "Risk Funnel Template: Data Extraction" section — (a) empty threats.md: single tier "0 Threats Identified" with review message, (b) all same severity: uniform tier coloring with minimum 10% narrowing, (c) 100+ findings: aggregate counts only in tier labels, (d) zero risk reduction: Tier 4 width = Tier 2 width, sidebar note "0% risk reduction"
- [X] T023 [P] Verify existing templates are unaffected — confirm `baseball-card` and `system-architecture` template files unchanged, `corporate-white` alias still resolves to `baseball-card`, all existing output patterns preserved
- [X] T024 Run quickstart.md validation — follow the steps in `specs/053-risk-reduction-funnel/quickstart.md` against example threat model output to verify end-to-end flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — read-only reference gathering
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — core template + agent content
- **US2+US3 (Phase 4)**: Depends on US1 — adds degradation to existing content
- **US4 (Phase 5)**: Depends on US1 — adds sidebar zone to existing template
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **US1 (Full 4-tier)**: Foundational required. No other story dependencies. This IS the MVP.
- **US2+US3 (Graceful Degradation)**: Depends on US1 (builds on the 4-tier template content)
- **US4 (Metrics Sidebar)**: Depends on US1 (builds on the template zone structure). Can run in parallel with US2+US3.
- **US5 (Registration)**: Part of Foundational phase — no story dependencies

### Within Each Phase

- Tasks within a phase follow listed order unless marked [P]
- Template file edits are sequential (same file)
- Agent file edits are sequential (same file)
- Template + agent + command edits can run in parallel (different files)

### Parallel Opportunities

- Phase 1: T001-T004 all [P] — read 4 reference files simultaneously
- Phase 2: T006 + T007 [P] — agent and command registration in parallel (T005 first)
- Phase 4: US4 (sidebar) can run in parallel with US2+US3 (ghost tiers) since they edit different zones of the template
- Phase 6: T022 + T023 [P] — edge cases and backward compat checks in parallel

---

## Parallel Example: Phase 2 (Foundational)

```
# Sequential first:
T005: Create template skeleton (must exist before registration)

# Then parallel:
T006: Register in agent (threat-infographic.md)
T007: Register in command (infographic.md)
```

## Parallel Example: Phase 4 + Phase 5

```
# These can run in parallel (different template zones + different agent sections):
Track A (US2+US3): T015 → T016 → T017 → T018  (ghost tiers)
Track B (US4):     T019 → T020 → T021           (metrics sidebar)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (read reference files)
2. Complete Phase 2: Foundational (skeleton + registration)
3. Complete Phase 3: User Story 1 (full 4-tier funnel)
4. **STOP and VALIDATE**: Run `/infographic --template risk-funnel` with compensating-controls data
5. Verify: 4 solid tiers, all 6 schema sections, Gemini prompt, correct data extraction

### Incremental Delivery

1. Setup + Foundational → Template registered, skeleton ready
2. Add US1 (4-tier) → Test with compensating-controls.md → **MVP!**
3. Add US2+US3 (graceful degradation) → Test with risk-scores.md and threats.md
4. Add US4 (metrics sidebar) → Test sidebar rendering across all 3 modes
5. Polish → Edge cases, backward compat, quickstart validation

---

## Summary

| Phase | Tasks | Parallel | Files |
|-------|-------|----------|-------|
| Setup | T001-T004 | 4 parallel reads | 4 reference files |
| Foundational | T005-T007 | T006+T007 parallel | 3 files |
| US1 (4-tier) | T008-T014 | Sequential (same files) | 2 files |
| US2+US3 (degradation) | T015-T018 | Sequential (same files) | 2 files |
| US4 (sidebar) | T019-T021 | Sequential (same files) | 2 files |
| Polish | T022-T024 | T022+T023 parallel | 2 files |
| **Total** | **24 tasks** | **10 parallel slots** | **3 target files** |
