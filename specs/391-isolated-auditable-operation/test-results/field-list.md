# Field list: what the infographic step sends to Gemini (T005, part 1)

Feature 391 · task T005 part 1 · recorded 2026-11-19 · read-only analysis at HEAD `0ee101b`. The working tree also holds another lane's uncommitted edit to `scripts/extract-report-data.py`; this record does not use it.

## 1. Verdict

- **Beyond R-8: 9 items.** Six are material (X-1 to X-6) and three are minor (X-7 to X-9), listed in section 5. Lane D must not use R-8's parenthetical verbatim until the PM approves the extension (section 6).
- **Droppable R-8 items: none.** Each R-8 item is sent by at least one path (section 4), so none can be dropped under R-8's rule.
- **Client pin:** already settled. The HTTP client form is pinned at `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md:253-266`, so T005's client-pin step does not apply.

## 2. Scope and method

- Read only. No Gemini or other network call, and no extractor, script or pytest run. Reading used the Read tool and grep/sed.
- Three prompt paths were checked, plus the request shape and a command-level instruction:
  1. **Scaffolded templates** `templates/tachi/infographics/infographic-{baseball-card,system-architecture,maestro-heatmap,maestro-stack,risk-funnel}.md`. The extractor returns a `prompt_scaffold` (preamble and postamble, copied verbatim). The agent writes the DATA CONTENT between them (`.claude/agents/tachi/threat-infographic.md:253-257`; `gemini-prompt-construction.md:18`).
  2. **Fallback prompt**, `gemini-prompt-construction.md:328-358`. It is used only when there is no scaffold and the template file cannot be loaded (`gemini-prompt-construction.md:33-39`). `INSTALL_MANIFEST.md:13` ships the templates to adopters, so for installed projects this is an error path.
  3. **Executive-architecture locked block**, `.claude/skills/tachi-infographics/references/executive-architecture.md:140-196`. Test A10 (`tests/scripts/test_gemini_request_contract.py:608-646`) pins the SHA-256 of the block with one K15 amendment paragraph removed. Only that paragraph can change. The slot names are pinned inside the text; the data values are not constrained.
- The request body is one text part with no image or file parts (`gemini-prompt-construction.md:268-288`).
- Placeholder sets were taken from each template's fenced prompt only: baseball-card lines 185-216, system-architecture 289-347, maestro-heatmap 164-196, maestro-stack 196-226, risk-funnel 200-239. No placeholder appears in any scaffold preamble or postamble. Placeholders in layout, zone and spec sections reach Gemini only if the agent copies them into DATA CONTENT.
- Provenance terms: **JSON** = a field in the `scripts/extract-infographic-data.py` output. **Agent** = the threat-infographic agent's own composition from the JSON, the spec sections, or the data-source file (threats.md). **Undefined** = no source found in code or references.

## 3. Field tables by prompt path

### 3.1 Path 1: scaffolded templates

| Placeholder | Where (prompt line) | Source | Maps to |
|---|---|---|---|
| `{project_name}` | all five, title (baseball 202; system-architecture 307; heatmap 182; stack 216; funnel 219) | JSON `metadata.project_name`: threats.md H1, else the architecture.md H1 in the output folder, else `Unknown Project` (`scripts/tachi_parsers.py:603-645`) | R-8: project name |
| `{date}` | all five, title | JSON `metadata.scan_date`, which is the threats.md frontmatter `date` (`scripts/extract-infographic-data.py:667`) | R-8: assessment date |
| `{total_findings}` | baseball 202, 204; system-architecture 307; heatmap 182; stack 216, 222 | JSON `metadata.total_findings` | R-8: severity counts (total) |
| `{critical_count}`, `{high_count}`, `{medium_count}`, `{low_count}` | baseball 204, 210 | JSON `severity_distribution[]` (count per label) | R-8: severity counts |
| `{critical_high_pct}` | baseball 204 | Agent: (critical + high) / total x 100 | R-8: severity counts (derived) |
| `{risk_posture_label}` | baseball 204 | JSON `metadata.risk_posture_label`: CRITICAL RISK, HIGH RISK, MODERATE RISK or LOW RISK (`scripts/tachi_parsers.py:991-1023`) | R-8: overall risk posture |
| `{posture_color}` | baseball 204 | Agent: colour word keyed on `metadata.risk_posture_level`. Hex is barred by the hygiene rule (`gemini-prompt-construction.md:114-120`) | R-8: overall risk posture (rendering only) |
| `{component_count}` | baseball 206; heatmap 182, 184 | Agent: row count of `heat_map[]` (baseball) or `template_data.maestro_heatmap[]` (heatmap) | R-8: component labels (count) |
| `{finding_cards_text}` | baseball 210 | Agent: spec Section 4 rows, at most 5, from JSON `top_findings[]` (`id`, `component`, `threat`, `risk_level`). The one-sentence threat summary is agent-written | R-8: finding IDs with threat descriptions; component labels. X-2 (severity). X-7 (score, tier 1) |
| `{heat_map_cell_grid}` | baseball 207 | Agent: spec Section 3 Cell-Level Grid, component by category, highest severity, built from threats.md finding IDs (`infographic-specifications.md:115-130`). JSON `heat_map[]` has component totals only | X-1 |
| `{category_count}` | baseball 202; system-architecture 307 | Agent: count of category columns. No JSON field | X-1 |
| `{zone_count}` | baseball 212; system-architecture 309 | System-architecture: length of JSON `template_data.trust_zones[]`. Baseball: undefined, because the baseball `template_data` has no zones | R-8: trust-zone labels (count) |
| `{zone_names}` | baseball 212 | Undefined in JSON for baseball. Agent-derived from threats.md Section 2, Trust Zones | R-8: trust-zone labels |
| `{zone_descriptions}` | system-architecture 311 | JSON `template_data.trust_zones[]` (`name`, `trust_level`, `components`). Component finding IDs and per-component counts come from `heat_map[]` and threats.md Section 3 (agent). Zone highest severity is agent-derived | R-8: trust-zone and component labels with short descriptions; finding IDs; severity counts. X-2 (zone highest severity; component colour) |
| `{flow_descriptions}` | system-architecture 317 | JSON `template_data.data_flows[]` (`source`, `destination`, `label` from the Data column, `severity_color` as hex). Flow finding IDs are agent-derived | R-8: data-flow labels. X-2 (flow severity colour) |
| `{flow_annotations}` | baseball 212 | Undefined in JSON for baseball, whose `template_data` has no flows. Agent-derived from threats.md Section 1, Data Flows | R-8: data-flow labels. X-2 (flow colour) |
| `{boundary_descriptions}` | system-architecture 319 | JSON `template_data.boundary_crossings[]` (`from_zone`, `to_zone`, `crossing_point`, `finding_count`). TB-N labels and finding IDs are agent-derived | R-8: trust-boundary labels; finding IDs. X-2 (boundary count) |
| `{correlation_annotations}` | baseball 212 | Undefined in JSON and in code. The zone spec defines "CO-N: description where cross-agent findings overlap" (`templates/tachi/infographics/infographic-baseball-card.md:164`), which points at threats.md Section 4a | X-5 |
| `{finding_legend_entries}` | system-architecture 343 | Agent: one entry per finding in threats.md Section 3, as `[ID] component - short description` (`infographic-system-architecture.md:365-376`). JSON carries only IDs (`allow_list.finding_ids`) and the top-5 text | R-8: finding IDs with threat descriptions; component labels (abbreviated); severity counts (tier headings). X-2 (per-finding severity tiers) |
| `{heatmap_grid}` | heatmap 185 | JSON `template_data.maestro_heatmap[]` (`component`; `layers` L1 to L7 severity or null). At most 10 rows | X-3 |
| `{layer_bands_text}` | stack 219 | JSON `template_data.per_layer_summaries[]` (`layer_id`, `layer_name`, `finding_count`, `highest_severity`, `coverage_state`, and up to 2 `top_findings` with `id` and `threat` cut to 120 characters) | X-3 (layer labels, counts, coverage state). R-8: finding IDs with threat text (120 characters or fewer); severity |
| `{most_exposed_layer}` | stack 220, 222 | JSON `template_data.most_exposed_layer` (`L# - name`) | X-3 |
| `{most_exposed_count}` | stack 222 | Agent. Deliberately not in JSON (extractor note at `main()`, Architect LOW-8) | X-3 |
| `{layers_with_findings}`, `{empty_layers}` | stack 222 | JSON `template_data` (code-computed) | X-3 |
| `{layer_count}` | stack 216; heatmap 182 | Stack: JSON `template_data.layer_count`. Heatmap: constant 7 | X-3 |
| `{tier_1_data}` to `{tier_4_data}` | funnel 223-226 | JSON `template_data.funnel_tiers[]`. Prompt-visible values per `template-specific-formats.md:47-62`: severity counts for tiers 1, 2 and 4; coverage % and mitigated/total for tier 3. Widths and volumes are layout values and are not named | R-8: severity counts (tiers 1, 2, 4). X-4 (tier 3 control figures; stage labels) |
| `{ghost_tier_instructions}` | funnel 228 | Fixed CTA text per state, naming tachi commands (`template-specific-formats.md:106-119`). No analysed data | Fixed text |
| `{sidebar_metrics}` | funnel 233 | JSON `metadata.total_findings`, `template_data.risk_reduction`, `template_data.control_coverage_pct` (`template-specific-formats.md:72-82`) | Total findings: R-8 (severity counts). Risk reduction and control coverage: X-4 |
| Between-tier reduction percentages (instruction, no placeholder) | funnel 235 | JSON `funnel_tiers` and `reduction_percentages` (`scripts/extract-infographic-data.py:1404-1459`) | X-4 |
| `ALLOWED IDS AND NAMES` line, written by the agent inside DATA CONTENT of all five | all five | JSON `allow_list.finding_ids` (baseball and system-architecture: every tier finding ID; stack: per-layer top IDs; heatmap and funnel: none) and `allow_list.component_names` (components, zone names and members, flow endpoints, finding components). Rule at `threat-infographic.md:259-263`; computed at `scripts/extract-infographic-data.py:2025` | R-8: finding IDs; component and trust-zone labels (names only). Sent on the risk-funnel too, which draws no components |
| Fixed template text: MAESTRO layer key (heatmap 192), footers, badges | heatmap, all | Template constants; not analysed data | Fixed text |

### 3.2 Path 2: fallback prompt

Only `{description}` has a source that no other path uses. The other placeholders reuse the path 1 sources.

| Placeholder | Line | Source | Maps to |
|---|---|---|---|
| `{project_name}`, `{date}` | 329, 343 | As path 1 | R-8: project name; assessment date |
| `{description}` | 343 | **Undefined.** No JSON field. Spec Section 1 has no system-description row (`infographic-specifications.md:35-46`). The index at `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md:120` maps it to "input format or system description", which is not a row in Section 1 | R-8: one-line system description. Sent only on this path |
| `{total_findings}`, `{critical_count}`, `{high_count}`, `{medium_count}`, `{low_count}`, `{critical_high_pct}`, `{risk_posture_label}`, `{posture_color}`, `{component_count}`, `{finding_cards_text}` | 343-351 | As path 1 | As path 1 |
| `{category_count}`, `{heat_map_cell_grid}` | 343, 348 | As path 1 | X-1 |
| `{zone_count}`, `{zone_names}` | 353 | As path 1. The fallback has no zone field in JSON | R-8: trust-zone labels |
| `{flow_annotations}` | 353 | As path 1 | R-8: data-flow labels. X-2 (colour) |
| `{correlation_annotations}` | 353 | As path 1 | X-5 |
| `ALLOWED IDS AND NAMES` line | 334 | As path 1 | R-8: finding IDs; component and trust-zone labels |

### 3.3 Path 3: executive-architecture locked block

| Slot | Line | Source | Maps to |
|---|---|---|---|
| `<<project_name>>` | 142, 168 | JSON `metadata.project_name` | R-8: project name |
| `<<layer_block>>` | 172 | JSON `layers[]`. `name` is the trust-zone name (`_compute_trust_zones`, Section 2), or the DFD type when no trust zones exist (`_compute_dfd_type_layers`). `components` are names. `layer_overflow` is a count string ("+N more in this layer") | R-8: trust-zone and component labels; severity counts (overflow). X-8 (DFD type names) |
| `<<callout_block>>` | 176 | JSON `callouts[]`: `layer_name`, `finding_id`, `severity`, `affected_component`, `raw_description`. `raw_description` is the full threat text, untruncated (`_extract_description`, `scripts/extract-infographic-data.py:896-902`). The composite score is not in the slot mapping (`executive-architecture.md:131`) | R-8: finding IDs with threat descriptions (full text, not one line). X-2 (per-finding severity). X-9 (mitigation substitution, tier 3) |
| `<<empty_layer_block>>` | 180 | JSON `layers[]` with no Critical or High callout | R-8: trust-zone labels |
| `<<flow_edges_block>>` | 184 | JSON `flow_edges[]`: `source`, `destination`, `data`, `protocol`. Capped at 50 (`_build_flow_edges`) | R-8: component labels; data-flow labels (protocol is a flow attribute) |
| `<<clusters_block>>` | 188 | JSON `clusters[]`: `name` (trust-zone name), `trust_level`, `members` (component names) (`_build_clusters`) | R-8: trust-zone and component labels |
| `<<single_zone_caption>>` | 190 | **Undefined text** (`executive-architecture.md:133, 162`). Emitted only when one layer has components | Agent-written. If it names the zone, it is an R-8 trust-zone label |

Not sent on this path: the assessment date, the one-line system description, the posture label, severity totals, composite or residual scores, the allow-list, `metadata.source_file`, and delta data. The slot table at `executive-architecture.md:127-135` confirms this.

### 3.4 Sent by instruction, not by placeholder

- **Delta.** When the JSON has a `delta` object (`has_baseline: true`), the command asks the agent to include delta counts (new, updated, unchanged, resolved) and to "Pass delta emphasis directives to Gemini prompts" (`.claude/commands/tachi.infographic.md:171-176`). No template placeholder names it. This is X-6.
- **Delta source.** `delta.baseline_source` is documented as a "baseline file path" (`templates/tachi/output-schemas/threats.md:30`). No instruction sends it, but the field exists and would carry a path if the agent included it.

### 3.5 In the JSON, named by no prompt placeholder

These are sent only if the agent departs from the placeholder contract. They bear on the D-3 sentence (section 7, item 1).

- `top_findings[].score` (composite or residual). Becomes X-7 when a tier-1 finding card shows the residual score (`infographic-specifications.md:156`).
- `template_data.inherent_score`, `residual_score`, `risk_weights`: no placeholder.
- `metadata.risk_posture` (a sentence with counts and component count): spec Section 1 only. Prompts use the label.
- `metadata.agent_count`, `schema_version`, `tier`, `data_source_type`, `template`, `source_file`: no placeholder.
- Component descriptions (threats.md Section 1, Description column) are parsed (`scripts/tachi_parsers.py:1366`) but never emitted to the JSON.
- Hex colours in `severity_distribution[].color` and `data_flows[].severity_color`. The hygiene rule requires colour words (`gemini-prompt-construction.md:114-120, 169`).

## 4. R-8 items: which paths send them (drop check)

R-8's parenthetical has seven items; the labels item is split by label type. The drop rule allows removing an item only if no path sends it.

| R-8 item | Paths that send it | Droppable? |
|---|---|---|
| Project name | All five scaffolds; fallback (`{project_name}`); executive (`<<project_name>>`) | No |
| One-line system description | Fallback only (`{description}`, line 343). No JSON source. Scaffold and executive runs send no description | No: one path sends it |
| Assessment date | All five scaffolds; fallback. Not executive | No |
| Finding IDs with one-line threat descriptions | Baseball (cards; ALLOWED IDs); system-architecture (legend, all IDs); stack (top 2 per layer, 120 characters or fewer); executive (callouts, full text); fallback (cards) | No. "One-line" holds for the summary paths only (section 7) |
| Component labels with short descriptions | Every path (names in zone, flow, grid, layer, cluster, legend and ALLOWED lines) | No |
| Trust-zone labels | Baseball (`{zone_names}`); system-architecture; fallback; executive (layers, clusters) | No |
| Trust-boundary labels | System-architecture (TB-N and crossing names; boundary descriptions) | No |
| Data-flow labels | Baseball, system-architecture and fallback (flow annotations); executive (flow edges) | No |
| Severity counts | Baseball (counts and percentages); system-architecture (zone and tier counts); stack and heatmap (layer counts; total); funnel (tier mixes); executive (overflow counts); fallback | No |
| Overall risk posture | Baseball and fallback (`{risk_posture_label}`) | No |

## 5. Items beyond R-8

| ID | Item | Paths | Source | Weight | Proposed clause (if approved) |
|---|---|---|---|---|---|
| X-1 | Threat-category labels (S, T, R, I, D, E, AG, LLM), the component-by-category severity grid, and the category count | Baseball 202, 207; system-architecture 307; fallback 343, 348 | Agent, from threats.md Section 3 finding IDs | Material | "threat-category labels and the component-by-category severity grid" |
| X-2 | Severity levels, not only counts: the severity of each finding shown (cards, callouts, legend tiers, layer bands); the highest severity of each component, zone and data flow; finding counts per zone and per boundary crossing | Baseball (flow colour, cards); system-architecture (zone, component and flow colour; legend tiers; counts); executive (callout severity); fallback | JSON `template_data` (trust_zones, data_flows, boundary_crossings) and agent | Material, low sensitivity. The PM may fold it into "finding IDs ... and severities" | "finding IDs with threat descriptions and severities; severity levels for components, zones and flows; finding counts per zone and boundary crossing" |
| X-3 | MAESTRO-layer labels, per-layer counts and coverage states (findings, clean, not applicable), the most exposed layer, and the component-by-layer severity grid. Conditional: threats.md has MAESTRO data. `all` adds these two templates only then; `maestro` always runs them (`tachi.infographic.md:166-168`) | Stack 216-222; heatmap 182-185 | JSON `template_data.per_layer_summaries`, `maestro_heatmap`, `most_exposed_layer`, and counts | Material | "MAESTRO-layer labels, per-layer counts and coverage states, and the component-by-layer severity grid" |
| X-4 | Compensating-control figures and funnel stage labels: risk-reduction %, control-coverage %, mitigated/total counts, between-tier reduction %, and the labels Inherent Risk Scored, Controls Applied, Residual Risk, Unmitigated Risk. Percentages and control counts are non-null only on compensating-control runs with volumes available. Stage labels appear on every funnel run | Funnel 223-235 | JSON `template_data.risk_reduction`, `control_coverage_pct`, `funnel_tiers`, `reduction_percentages` | Material. The PM may read "risk reduction" as part of "overall risk posture" | "control-coverage and risk-reduction percentages, control counts and funnel stage labels, on compensating-control runs" |
| X-5 | Correlation groups: CO-N labels and descriptions of cross-agent finding overlaps | Baseball 212; fallback 353 | Undefined in JSON. The baseball zone spec (line 164) points at threats.md Section 4a | Material. No source is defined, so a path can send it, and the docs lane cannot show that none does | "correlation-group labels where findings overlap across threat agents" |
| X-6 | Delta status: counts of new, updated, unchanged and resolved findings, and a NEW-finding emphasis directive | Any template on baseline runs. Command instruction, not a placeholder | JSON `delta.delta_counts` | Material on baseline runs | "on baseline runs, finding-status counts (new, updated, unchanged, resolved)" |
| X-7 | Per-finding numeric risk score on finding cards. Residual score on tier 1 (`infographic-specifications.md:156`) | Baseball 210; fallback 351 (conditional) | JSON `top_findings[].score` | Minor, conditional | "per-finding risk scores where the tier shows them" |
| X-8 | DFD element-type labels used as layer names when the threat model has no trust zones (External Entity, Process, Data Store and similar). Also the single-zone caption text, which the reference does not define | Executive 172, 190 (conditional) | JSON `layers[]` with `source_kind: dfd_type` | Minor. The PM may fold it into "component labels" | "component type labels where no trust zones are defined" |
| X-9 | Mitigation text in place of threat text. When a tier-3 finding's Threat cell is empty, `_extract_description` uses its Mitigation cell as `raw_description` | Executive 176 (tier 3 only) | `scripts/extract-infographic-data.py:896-902`; `scripts/tachi_parsers.py:1225` | Minor. Edge case and a defect | None. The docs must not describe callout text as threat text only. A fix is a follow-up, not T005 |

## 6. Proposed wording for PM approval

**Option A (full).** Replaces R-8's parenthetical in PRD v1.4. The PM strikes any clause not approved, and Lane D writes only the approved text.

> (the project name, a one-line system description and the assessment date; finding IDs with threat descriptions and severities; component, trust-zone, trust-boundary and data-flow labels with short descriptions, and component type labels where no trust zones are defined; severity counts and levels for findings, components, zones and flows, with finding counts per zone and boundary crossing; per-finding risk scores on compensating-control runs; the overall risk posture; threat-category labels and the component-by-category severity grid; MAESTRO-layer labels, per-layer counts, coverage states and the component-by-layer severity grid; control-coverage and risk-reduction percentages, control counts and funnel stage labels on compensating-control runs; correlation-group labels; finding-status counts (new, updated, unchanged, resolved) on baseline runs)

**Option B (short).** Keeps the D-3 parenthetical short and moves the full field table into the runbook (T016): "(derived threat-model content: the labels, finding descriptions, counts and posture listed in the runbook's field table)". This needs the runbook table to exist before the sentence ships in six documents.

**R-8 wording change for the PM's notice.** "One-line threat descriptions" becomes "threat descriptions" in both options. The executive-architecture callouts send the full threat text (`executive-architecture.md:131`; `scripts/extract-infographic-data.py:896-902`). "One-line" holds only for the summary paths. "One-line system description" stays, because the fallback path is the only sender and the drop rule keeps it.

## 7. Notes for the docs lane

1. **"tachi sends nothing else"** (D-3 in `docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md:139-141`). DATA CONTENT is the agent's composition, and the reference gives the agent creative control over it (`gemini-prompt-construction.md:18`). No code checks the request body against the placeholder list. The sentence describes the template contract, not a mechanical guarantee. The PM should decide whether to keep it with "as specified by the templates", soften it, or add a check (a follow-up, not T005).
2. **Free-text provenance.** Finding descriptions, component and zone names, flow labels and the project name come from the adopter's architecture, through threats.md and the architecture.md H1. They are not closed labels. Do not describe the content as "labels only".
3. **Correction to the R-8 evidence.** The PM ruling (`.aod/results/pm-tasks-391.md` section 10) cites the fallback's `{description}` at `gemini-prompt-construction.md:330`. The placeholder is at line 343, and it belongs to the generic fallback, not to the baseball card. Lane D should cite line 343. The other R-8 evidence cites check out: `infographic-baseball-card.md:13-14` (title and date), `infographic-system-architecture.md:307`, and lines 311, 317 and 319 for the zone, flow and boundary placeholders.
4. **Normal runs.** Installed projects receive the template files (`INSTALL_MANIFEST.md:13`), so the scaffold path is the normal path. Scaffold and executive runs send no one-line system description, so the sentence should not imply that every run sends one.

## 8. Cross-lane observations (outside T005)

- The command writes the extractor output to `/tmp/infographic-{template_name}.json` (`.claude/commands/tachi.infographic.md:163`). The agent's example uses `/tmp/infographic-data.json` (`.claude/agents/tachi/threat-infographic.md:170`). Relevant to the write-set audit (T004) and D-4.
- `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md:121-123` names `{maestro_layer_distribution}` and `{maestro_heatmap}`. The maestro templates use `{layer_bands_text}` and `{heatmap_grid}`. This record uses the template names.
- `.claude/agents/tachi/threat-infographic.md:33-35` lists three templates. The command routes five plus the two MAESTRO templates. The command is the routing authority as read.
- The agent writes the request body to a file beside its intermediates (`gemini-prompt-construction.md:266`). Retention is not specified. If kept, that file is the audit record of what was sent. Relevant to the runbook claims (T016).
- The ALLOWED line sends component names on the risk-funnel path, although that template draws no components.

## 9. Files read (repo-relative)

- Task and governance: `specs/391-isolated-auditable-operation/tasks.md:75`; `.aod/results/pm-tasks-391.md` section 10 (R-8); `docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md:139-141`; `INSTALL_MANIFEST.md:13`.
- Templates: `templates/tachi/infographics/infographic-{baseball-card,system-architecture,maestro-heatmap,maestro-stack,risk-funnel}.md` (prompt fences and zone specs); `templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md`; `templates/tachi/output-schemas/threats.md:29-33`.
- Skill references: `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md`, `executive-architecture.md`, `infographic-specifications.md`, `template-specific-formats.md`.
- Agent and command: `.claude/agents/tachi/threat-infographic.md`; `.claude/commands/tachi.infographic.md`.
- Code, read and not run: `scripts/extract-infographic-data.py`; `scripts/tachi_parsers.py`; `tests/scripts/test_gemini_request_contract.py` (class at line 608).

## 10. PM ruling (T005, part 2)

Product manager, 2026-11-19. This section rules on sections 5 to 8 under R-8's escalation rule (`tasks.md` T005; `agent-assignments.md` §9). It is recorded as PRD v1.4 (D-3, §1 item 2, the FR-6 audiences, and the version history). The wording is PM-owned and needs no Triad re-review, as with v1.3.

**Decision: Option A, refined.** The full list stays inline in the sentence, corrected for the defects listed in 10.4. Lane D writes 10.1 and 10.3 verbatim. Any other change to either text comes back to the PM, except the one pre-ruled fallback in 10.1. The runbook pointer sentence (10.1) is in Lane D's own words, within the content stated there.

### 10.1 Approved D-3 sentence (verbatim, ready to paste)

> Your Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run. If you set `GEMINI_API_KEY` and run `/tachi.infographic`, Google's Gemini API (`generativelanguage.googleapis.com`) also receives image prompts made of tachi's fixed layout instructions and derived threat-model content, including names and descriptions taken from your architecture (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description). By design, tachi sends nothing else, but an AI agent following tachi's templates writes each prompt, and no code checks it against this list before it is sent. Claude Code's own operational traffic, such as usage metrics, error reports and feature-flag fetches, is separate from tachi; it is governed by Claude Code's privacy and telemetry settings, and setting `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns these off.

How Lane D uses it:

- **Every document.** Use the same text in all six documents. As in v1.3, "privacy and telemetry settings" links to the public Claude Code docs page that Lane D cites at the W1 re-read.
- **Sweep anchor.** SC-A2's presence check can anchor on the substring "By design, tachi sends nothing else".
- **Pre-ruled fallback (no PM round trip).** The switch is named on the basis of `plan.md:162` and the session profile's `env` key. If the W1 docs re-read shows that `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` does not turn off one of the three named examples:
  - Lane D removes that example from the "such as" list;
  - the runbook names that example's own switch;
  - the sweep record notes the change.
- **Runbook only (FR-4).** One pointer sentence follows the D-3 text. It says the field-level specification is the installed prompt sources:
  - `templates/tachi/infographics/` (the five scaffolded templates);
  - `.claude/skills/tachi-infographics/references/executive-architecture.md` (the executive-architecture prompt);
  - `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` (the request form and the fallback prompt);
  - `.claude/commands/tachi.infographic.md` (the baseline instruction).

  It is a pointer, not a copied table, so it cannot drift from the prompts it describes. All four paths are installed (`INSTALL_MANIFEST.md:13, 16, 30`).

### 10.2 Approved parenthetical alone

(the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description)

How it covers sections 4 and 5:

| Field-list items | Clause |
|---|---|
| R-8 project name; R-8 assessment date | "the project name and assessment date" |
| R-8 component, trust-zone, trust-boundary and data-flow labels with short descriptions; X-8 | "the names, types and short descriptions of components, trust zones, trust boundaries and data flows" |
| R-8 finding IDs with threat descriptions; X-2 (per-finding severity); X-7; X-9 | "finding IDs, descriptions, severities and risk scores". The word is "descriptions", not "threat descriptions" or "one-line". The executive-architecture callouts send the full text, which Gemini shortens at render time (`executive-architecture.md:131`), and X-9 sends mitigation text |
| X-5 | "correlation groups of related findings and their descriptions" |
| R-8 severity counts; X-1; X-2 (component, zone and flow severity; zone and boundary counts); X-3 | "finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer". "Analysis coverage" covers the grid's analysed-with-no-findings and not-applicable cells and the MAESTRO coverage states |
| R-8 overall risk posture | "the overall risk posture" |
| X-4 (figures) | "control-coverage and risk-reduction figures from compensating-control runs" |
| X-6 | "counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked" |
| R-8 one-line system description | "and, if a template cannot be loaded, a one-line system description" (note 4: normal runs send none) |
| X-4 funnel stage labels; ghost-tier text; the MAESTRO layer key; footers and badges | Fixed template text, not project data. Covered by "tachi's fixed layout instructions" in the lead-in |
| Section 3.5 JSON fields that no placeholder names, including `metadata.source_file` and `delta.baseline_source` | Not listed, because the design does not send them. The residual risk is covered by the agent disclosure in sentence 3 |

### 10.3 Audiences text for the profile's `autoMode.environment` entry

The audiences sentence:

> Audiences: the security team; Google's Gemini API for the derived infographic prompt only (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description).

The whole entry, which replaces `contracts/session-profile.md:31`. Its first sentence is unchanged.

```text
"Sensitive data locations & audiences: the run's output directory and the architecture file hold confidential threat models. Audiences: the security team; Google's Gemini API for the derived infographic prompt only (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description).",
```

- The `hard_deny` sentence is unchanged and stays byte-exact against PRD FR-6. Its phrase "the derived infographic prompt" now means this list.
- The contract line is updated before T006 pre-stages the profile. T016 ships it in the runbook's profile block.

### 10.4 Rulings

1. **Option A, refined, rather than Option A as drafted.** Option A as drafted (section 6) has five defects. Each would make the published sentence untrue or misleading:
   - "finding IDs with threat descriptions" is false where X-9 sends mitigation text;
   - "correlation-group labels" leaves out the free-text descriptions that X-5 sends;
   - an unconditioned "one-line system description" implies that every run sends one (note 4);
   - "funnel stage labels" lists fixed template text beside project data, which blurs what is sensitive;
   - nothing tells the reader that names and descriptions come from their own architecture (note 2).

   The refined list runs to about 90 words, against about 115.
2. **Option B is not acceptable for the six-document sweep.**
   - At the decision point (README's key instruction, AC-A1.2), the reader would get a pointer rather than a statement of what is sent.
   - Five documents would depend for their truth on a hand-maintained runbook table that no guard checks.
   - "The labels" invites the "labels only" reading.

   With the refined Option A, the runbook needs no field table, only the pointer sentence in 10.1.
3. **"tachi sends nothing else": qualified, not dropped.**
   - G1 requires every such statement to say that tachi sends nothing else, so the claim stays, as "By design, tachi sends nothing else". The same sentence then states the mechanism: an AI agent following tachi's templates writes each prompt, and no code checks it against the list.
   - I rejected "as specified by its templates" on two grounds. The baseline instruction lives in the command and the executive-architecture prompt in a skill reference, so "templates" alone is not accurate. It would also hide the residual risk that a security reader needs to know.
   - The host half of the claim (no other host) is also by design. The runbook's sandbox allow-list enforces it when the profile is used. Nothing enforces the content half, hence the disclosure.
4. **Mechanical request check: yes, as a follow-up (FU-1), not in 391.** A data-handling claim that adopters rely on should not rest on a model following its instructions. tachi already uses deterministic steps for claims like this: D-9's version stamp, and the SHA-256 pin on the executive-architecture block in test A10. Building the check now would add code to a feature whose docs lane is waiting only on wording.
5. **The host is named in the sentence** (`generativelanguage.googleapis.com`), so the D-3 sentence itself meets AC-A1.2's "to which host".
6. **Claude Code's switch is named in the sentence**: `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, per `plan.md:162` and the profile's `env` key, with the pre-ruled fallback in 10.1.

### 10.5 Dispositions: section 7 notes

| Note | Disposition |
|---|---|
| 1. "tachi sends nothing else" | Ruled in 10.4, item 3. Follow-up FU-1 |
| 2. Free-text provenance | Accepted. The lead-in says "including names and descriptions taken from your architecture", and the list says "names" and "descriptions", not "labels". Lane D must not paraphrase the list as labels anywhere (the README key instruction, `scope.md`, `SECURITY.md`) |
| 3. R-8 citation | Accepted and checked. `{description}` is at `gemini-prompt-construction.md:343`, in the generic fallback prompt, not the baseball card. R-8's ":330" is an error in the PM's local review file, which stays as written. Lane D cites :343 |
| 4. Normal runs | Accepted. The list says the system description is sent only "if a template cannot be loaded". No document may say that every run sends one |

### 10.6 Dispositions: section 8 observations

| Observation | Product-relevant? | Disposition |
|---|---|---|
| `/tmp/infographic-{template_name}.json` (command) vs `/tmp/infographic-data.json` (agent example) | Yes, through FR-7's write claim | T004 audits both names, and the FR-7a relocation covers both. The runbook's write claim ships only once neither name writes to the shared `/tmp`. The architect owns this |
| The request and response files written "beside its other intermediates" (`gemini-prompt-construction.md:266`) | Yes: auditability and write confinement | T004 includes both files in the write-set audit. After FR-7a they must sit under the output directory or the per-user temp directory. If W2's write listing shows the request file kept in the output directory, the runbook may add one sentence naming it as the record of what was sent. The key is not in that file: it travels in a curl config on standard input (`:253-263`, `:266`). If the file is not kept, the runbook says nothing, and retention joins FU-1. No build work is added to 391 |
| The ALLOWED line sends component names on the risk-funnel, which draws none | Yes: data minimisation | D-3 stays true, because component names are on the list. The fix is FU-3 |
| Placeholder-name drift in `INFOGRAPHIC_TEMPLATES.md`; the three-template list in `threat-infographic.md:33-35` | No, for 391 | The D-3 list covers all six templates the command routes (`tachi.infographic.md:166-169`). `all` runs baseball-card, system-architecture, risk-funnel and executive-architecture, plus maestro-stack and maestro-heatmap when threats.md has MAESTRO data. The drift goes into FU-3 |

### 10.7 Other copies of the v1.3 wording

| Location | Action |
|---|---|
| `contracts/session-profile.md:31` | **Required.** Replace it with 10.3 before T006 pre-stages the profile |
| `quickstart.md:5` ("tachi sends nothing else.") | Align it with sentence 3 of 10.1 when the file is next edited. It is not on the Wording Rules surface and does not block Lane D |
| `plan.md:184` (AD-15 quotes the v1.3 list) | A historical decision record, superseded by PRD v1.4. No edit |
| `spec.md:34` (US1 narrative); `tasks.md:75` (quotes R-8); PRD G1 (`:67`) | Consistent summaries or historical quotes; the PRD governs (`spec.md:18`). No edit |

### 10.8 Follow-up issue titles (not created here; filed at delivery, T045)

- **FU-1: "Check the Gemini infographic request against its documented field list before sending".** This makes "nothing else" mechanical. Its own PRD chooses between two approaches:
  - build DATA CONTENT by script from the extractor output (the executive-architecture locked-block pattern);
  - validate the request file against the extractor JSON and the allow-list before `curl`, failing closed.

  Either way, the request file stays in the output directory as the record of what was sent.
- **FU-2: "Executive-architecture callouts send mitigation text when a finding's threat text is empty".** Defect X-9 (`scripts/extract-infographic-data.py:896-902`; `scripts/tachi_parsers.py:1225`).
- **FU-3: "Give every infographic placeholder a defined source and send only what each template draws".** It covers:
  - the placeholders with no JSON source: `{correlation_annotations}`, the fallback `{description}`, and the baseball `{zone_names}` and `{flow_annotations}`;
  - the risk-funnel's ALLOWED line;
  - the drift in `INFOGRAPHIC_TEMPLATES.md` and `threat-infographic.md:33-35`.

### 10.9 Wording check

10.1 to 10.3 have zero Pattern A hits and zero Pattern B hits, and do not name the unreleased fix.
