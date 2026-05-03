# Feature 082 — Shared Reference Audit

**Purpose**: Pre-Phase-6 baseline audit of `.claude/skills/tachi-shared/references/` files. Informs T042 (finding-format-shared.md producer section), T044 (grep check for inline OWASP 3×3 removal), T045 (stride-categories-shared.md frontmatter update).
**Created**: 2026-04-11
**Branch**: `082-threat-agent-skill`
**Audited by**: senior-backend-engineer (via /aod.build Wave 2, Task T007)
**Method**: Each file read in full; frontmatter `consumers:` list cross-checked against actual Readers via `Grep` for the filename literal across `.claude/agents/tachi/*.md`.

---

## Summary Table

| File | Lines | Orientation | Declared Consumers | Actual Readers | Phase 6 Task | Additive Edit | Delta | Forbidden |
|------|------:|-------------|-------------------:|---------------:|--------------|---------------|-------|-----------|
| severity-bands-shared.md | 110 | Consumer-biased (scoring + visual) | 6 | 6 | none | none | +0 | No |
| finding-format-shared.md | 177 | Consumer-oriented (spec + validation) | 13 | 2 | **T042** (SERIAL) | APPEND `## For Threat Agents (Producers)` | +40 to +60 | No |
| stride-categories-shared.md | 146 | Category-definition neutral | 12 | 1 | T045 (optional) | Frontmatter `consumers:` reality sync | +0 to +5 | No |
| maestro-layers-shared.md | 213 | Consumer-only (orchestrator Phase 1 algorithm) | 4 | 1 | **none** | **NONE** | N/A | **YES (FR-9 / ADR-023 Decision 2)** |

**Aggregate delta**: Net +40 to +65 lines across all 4 files, concentrated in one file (`finding-format-shared.md`). One serial single-writer wave (Phase 6 / T042-T046).

**Key findings at a glance**:
1. `finding-format-shared.md` declares 13 consumers but only 2 agents actually Read it today — 11 threat agents are aspirational. T043 will make this list match reality.
2. `stride-categories-shared.md` declares 12 consumers but only 1 agent actually Reads it — also aspirational. T045 is optional and may resolve naturally once threat agents start Reading it in Phase 2a/2b.
3. `severity-bands-shared.md` consumer list is accurate (6 declared = 6 actual). No action required.
4. `maestro-layers-shared.md` is out of scope for threat agent consumption and remains forbidden for Phase 6 edits.
5. **Duplication hazard**: OWASP 3×3 matrix is present in BOTH `severity-bands-shared.md` (line 72, "OWASP 3x3 Risk Matrix" section using qualitative band names) AND `finding-format-shared.md` (line 126, "Risk Level Computation" section using LOW/MEDIUM/HIGH axes). This is legacy pre-Phase-6 duplication, not a defect introduced by this refactor. T044's grep check must target `.claude/agents/tachi/` only, NOT the shared refs.

---

## File 1: severity-bands-shared.md

### A. Content Orientation

**Consumer-biased, scoring + visual pipeline**. This file serves the risk-scorer and downstream visual output agents (report, infographic). It documents thresholds, SLAs, disposition values, and visual encoding (colors, SARIF levels) — all of which are read AFTER findings are produced. Threat agents do not need any of this content to produce findings.

**Exception**: The file contains an `## OWASP 3x3 Risk Matrix` section (lines 72-82) that IS producer-relevant (threat agents use OWASP 3×3 to compute `risk_level` from likelihood × impact). However, the same matrix is duplicated in `finding-format-shared.md` at line 126-136 under `## Risk Level Computation`, and that location uses LOW/MEDIUM/HIGH axes (the actual `likelihood`/`impact` enum values) which is more directly applicable to producers. Threat agents should Read `finding-format-shared.md` for the matrix, not this file.

**Top-level sections** (from `grep -n '^## '`):
1. Severity Band Thresholds (line 21) — composite score → band boundary rules
2. SLA Mappings (line 38) — remediation SLAs per band
3. Disposition Values (line 59) — Mitigate/Review/Accept/Transfer governance values
4. OWASP 3x3 Risk Matrix (line 72) — qualitative likelihood × impact matrix (legacy duplicate of finding-format-shared.md)
5. Color Codes for Visual Output (line 86) — hex color assignments per band
6. SARIF Level Mapping (line 100) — severity → SARIF level

**Line count**: 110 (matches plan.md line 259)

### B. Consumers (declared vs actual)

**Frontmatter declares**:
```yaml
consumers:
  - orchestrator
  - risk-scorer
  - control-analyzer
  - threat-report
  - threat-infographic
  - report-assembler
```

**Actual Readers** (Grep `severity-bands-shared.md` across `.claude/agents/tachi/*.md`): 6 files
- `.claude/agents/tachi/orchestrator.md`
- `.claude/agents/tachi/risk-scorer.md`
- `.claude/agents/tachi/control-analyzer.md`
- `.claude/agents/tachi/threat-report.md`
- `.claude/agents/tachi/threat-infographic.md`
- `.claude/agents/tachi/report-assembler.md`

**Mismatch**: **None**. Frontmatter `consumers:` list is 100% accurate. This is the gold-standard shared reference with perfect declared-to-actual alignment — the result of Feature 075/078 conforming infra agents to the lean pattern.

### C. Additive Edit Plan

**Task**: None (plan.md §1.3 row 1 explicitly lists `+0` lines for this file).

**Rationale**: Threat agents do not read severity bands, SLAs, disposition values, color codes, or SARIF levels — they produce findings with `likelihood` / `impact` / `risk_level` only. The risk-scorer consumes severity bands during scoring. The file is already producer-neutral: threat agents could Read it for the OWASP 3×3 matrix, but that matrix is canonically located in `finding-format-shared.md` (see File 2 below).

**Must remain byte-identical**: Entire file (lines 1-110).

**Risks**: None. No table-of-contents block exists that would need updating.

### D. Prohibitions

No explicit FR or invariant prohibits modification. However, any edit risks breaking the 6 infra agents that Read this file today (R3 mitigation — see plan.md Risk Register). Feature 082 scope is deliberately "no changes" for this file.

---

## File 2: finding-format-shared.md

### A. Content Orientation

**Consumer-oriented, validation-biased**. This file was authored for orchestrator and risk-scorer consumers — it documents what a finding MUST look like for orchestrator to accept it and for risk-scorer to process it. Sections are framed from the perspective of "what the consumer validates" rather than "what the producer constructs":

- `## Required Fields` — describes enum constraints and validation behavior, not construction guidance
- `## Optional Fields` — describes "Present When" conditions (consumer view)
- `## ID Format Conventions` — consumer view of the ID prefix table; the phrase "ID prefix must match category" is validation language
- `## STRIDE Table Format` / `## AI Table Format` — these describe the ORCHESTRATOR's OUTPUT assembly format, not the threat agent's input format
- `## Risk Level Computation` — OWASP 3×3 matrix; applicable to both producer and consumer
- `## Validation Rules` — explicitly consumer-facing ("When a finding does not conform to the schema, the orchestrator applies recovery rules...")
- `## Non-Conforming Finding Handling` — orchestrator recovery logic (sub-section of Validation Rules)
- `## Category Display Name Mapping` — consumer/report-assembly view

**Top-level sections** (from `grep -n '^## '`):
1. Required Fields (line 30)
2. Optional Fields (line 54)
3. ID Format Conventions (line 70)
4. STRIDE Table Format (line 96)
5. AI Table Format (line 112)
6. Risk Level Computation (line 126)
7. Validation Rules (line 140)
8. Category Display Name Mapping (line 164)

**Note**: Sub-heading `### Non-Conforming Finding Handling` under §7 is an `### ` (H3), not `## ` (H2) — it is subordinate to Validation Rules.

**Line count**: 177 (matches plan.md line 260)

### B. Consumers (declared vs actual)

**Frontmatter declares**:
```yaml
consumers:
  - orchestrator
  - spoofing
  - tampering
  - repudiation
  - info-disclosure
  - denial-of-service
  - privilege-escalation
  - prompt-injection
  - data-poisoning
  - model-theft
  - agent-autonomy
  - tool-abuse
  - risk-scorer
```
(13 declared consumers — orchestrator + 11 threat agents + risk-scorer)

**Actual Readers** (Grep `finding-format-shared.md` across `.claude/agents/tachi/*.md`): **2 files**
- `.claude/agents/tachi/orchestrator.md`
- `.claude/agents/tachi/risk-scorer.md`

**Mismatch**: **MAJOR**. 11 threat agents are declared as consumers but NONE of them actually Read this file today. This is aspirational — it was added to the frontmatter during Feature 078 in anticipation of a future refactor (Feature 082!) that would make threat agents conform to the lean pattern.

**Implication for T043**: T043 is designed to fix this gap by adding a `## Skill References` Read-always row in all 11 threat agent files pointing to this shared file. Post-T043, frontmatter and actual readers will align (13 declared = 13 actual).

### C. Additive Edit Plan

**Task**: **T042** (Phase 6, single-writer, serial, separate commit)

**Edit**: APPEND a new `## For Threat Agents (Producers)` section AFTER the existing `## Category Display Name Mapping` section (which ends at file EOF, line 177). New section becomes the 9th `## ` heading.

**Expected delta**: +40 to +60 lines (per plan.md line 260). Mid-range target: ~50 lines.

**Proposed content of the producer section** (to be authored in T042; T007 specifies what the section should contain):

1. **Opening narrative** (3-5 lines): "The preceding sections describe the finding IR from the consumer's perspective (orchestrator validation, risk-scorer aggregation). This section gives threat agents a producer's view — how to construct each field when emitting a finding."

2. **ID prefix assignment table (producer view)**: One-row-per-agent table showing which ID prefix each agent owns. Different from the existing consumer-side "ID Prefix Table" (which is keyed by prefix): the producer view is keyed by agent name and answers "if I am tachi-spoofing, what prefix do I use?" Format:
   ```
   | Agent | ID Prefix | Category Enum | First ID | Example |
   |-------|-----------|---------------|----------|---------|
   | tachi-spoofing | S | spoofing | S-1 | S-3 |
   | tachi-tampering | T | tampering | T-1 | T-2 |
   | ...                                           |
   | tachi-prompt-injection | LLM | llm | LLM-1 | LLM-4 |
   ```
   Roughly 8-12 lines.

3. **Field construction guidance** (per field, 1-2 lines each, roughly 15-20 lines total):
   - `id`: Start at `{PREFIX}-1` and increment sequentially within your agent's category. Never skip numbers.
   - `category`: Use the exact enum string (lowercase, hyphenated) matching your agent's category. Do not use display names.
   - `component`: Copy verbatim from the dispatch record's target component name.
   - `threat`: One sentence stating what the attacker does and which trust assumption they violate. No marketing language.
   - `likelihood` / `impact`: Use UPPERCASE LOW/MEDIUM/HIGH only. Do not hedge with values like "MODERATE" or "LOW-MEDIUM".
   - `risk_level`: Compute via OWASP 3×3 (see §Risk Level Computation). Produce one of: Critical, High, Medium, Low, Note.
   - `mitigation`: Cite a specific technology or configuration (e.g., "Enforce mTLS with certificate pinning"), not generic advice (e.g., "improve authentication").
   - `references` (REQUIRED for agentic/llm): At least one OWASP LLM/Agentic, MCP, or CVE citation.
   - `dfd_element_type`: Copy from the dispatch record; never infer.

4. **Risk level computation example** (5-8 lines): Worked example showing a finding with `likelihood: HIGH`, `impact: MEDIUM` computing to `risk_level: High` via the matrix.

5. **Reference linking conventions** (3-5 lines): Prefer stable identifiers over URLs (e.g., `CWE-918`, `OWASP LLM01:2025`, `AML.T0051`). URLs only when no stable identifier exists.

**Must remain byte-identical**: All existing content lines 1-177 (frontmatter + all 8 existing `## ` sections). The new section is APPENDED at what is currently EOF (after the last Category Display Name Mapping table row). The frontmatter is NOT touched by T042 — T043 handles the logical consumer-alignment via threat agent edits, not via frontmatter edits (the frontmatter already lists all 11 threat agents).

**Risks**:
- **R-AUD-1**: The file has no table-of-contents or index block, so appending a new top-level section does NOT require TOC sync. Confirmed by full-file read.
- **R-AUD-2**: Risk that a contributor writing the T042 section might inadvertently update the existing `## Risk Level Computation` section to link to the new producer section. This would create a backward cross-reference and risk byte-level drift. Mitigation: T042 commit discipline — separate commit, diff review against pre-Phase-6 baseline.
- **R-AUD-3**: Risk that the producer section introduces terminology that conflicts with the existing consumer section (e.g., calling `id` a "finding code" in one place and "finding ID" in another). Mitigation: the producer section should cross-reference the consumer sections by name rather than restating.
- **R-AUD-4**: OWASP 3×3 is already present in `## Risk Level Computation` using LOW/MEDIUM/HIGH axes. Do NOT duplicate the matrix table in the producer section — cross-reference it (e.g., "See §Risk Level Computation above for the OWASP 3×3 matrix"). This keeps the new section focused on producer guidance rather than restating canonical definitions.

### D. Prohibitions

None. This file is the PRIMARY additive target for Phase 6. It is explicitly NOT forbidden by any FR or invariant.

---

## File 3: stride-categories-shared.md

### A. Content Orientation

**Category-definition neutral** (producer-leaning). This file documents STRIDE and AI category definitions, ID prefixes, agent mappings, the DFD applicability matrix, AI keyword dispatch rules, and cross-category correlation rules. Content is mostly orchestrator-facing (dispatch + correlation logic is orchestrator-only), but the category definitions themselves are usable by threat agents as well — they describe what each category means and which trust assumption each undermines.

Threat agents would benefit from reading the `## STRIDE Categories (6)` and `## AI Categories (5)` tables to ground their category-specific detection patterns. They would NOT benefit from reading `## DFD Element-to-Category Applicability Matrix`, `## AI Keyword Dispatch Rules`, `## Coverage Checklist Category Mapping`, or `## Correlation Rules` — those are orchestrator dispatch + correlation logic.

**Top-level sections** (from `grep -n '^## '`):
1. STRIDE Categories (6) (line 28) — producer-relevant
2. AI Categories (5) (line 41) — producer-relevant
3. DFD Element-to-Category Applicability Matrix (line 62) — orchestrator dispatch logic
4. AI Keyword Dispatch Rules (line 79) — orchestrator dispatch logic
5. Coverage Checklist Category Mapping (line 117) — orchestrator coverage evaluation
6. Correlation Rules (line 134) — orchestrator correlation logic

**Line count**: 146 (matches plan.md line 261)

### B. Consumers (declared vs actual)

**Frontmatter declares**:
```yaml
consumers:
  - orchestrator
  - spoofing
  - tampering
  - repudiation
  - info-disclosure
  - denial-of-service
  - privilege-escalation
  - prompt-injection
  - data-poisoning
  - model-theft
  - agent-autonomy
  - tool-abuse
```
(12 declared consumers — orchestrator + 11 threat agents)

**Actual Readers** (Grep `stride-categories-shared.md` across `.claude/agents/tachi/*.md`): **1 file**
- `.claude/agents/tachi/orchestrator.md`

**Mismatch**: **MAJOR**. 11 threat agents are declared as consumers but NONE of them actually Read this file today. As with finding-format-shared.md, this was added aspirationally during Feature 078 in anticipation of a future refactor.

**Implication for T045**: T045 (optional) addresses this gap by adding the file to threat agents' Skill References tables during Phase 6. However, per plan.md line 261, "content is already category-definition and the frontmatter already lists 11 threat agents as consumers (aspirationally)". T045's language ("may be N/A if frontmatter already matches") suggests that the Phase 6 team may decide to resolve this naturally by having T026/T028/T030/T032/T034/T036/T038/T040 (individual agent extraction tasks) register this file in their Skill References tables. If Phase 2a/2b tasks already handle the registration, T045 becomes a no-op.

### C. Additive Edit Plan

**Task**: T045 (Phase 6, optional, depends on T007).

**Edit**: Potentially **frontmatter-only update** to the `consumers:` list — adding any threat agent not already declared. Based on this audit, the list already names all 11 threat agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse). **No frontmatter change required** — T045 is very likely a no-op.

**Expected delta**: +0 lines (most likely) to +5 lines (if content comments are added clarifying producer consumption scope — not planned).

**Must remain byte-identical**: All content lines (lines 22-146, i.e., body after frontmatter). Frontmatter is already aligned with the post-Feature-082 state.

**Risks**:
- **R-AUD-5**: Contributors may misread T045 as requiring a content change. Mitigation: T045 task description should explicitly say "frontmatter consumers list only — no body edits".
- **R-AUD-6**: Because threat agents will start Reading this file during Phase 2a/2b (T010, T012, T024, T026, T028, T030, T032, T034, T036, T038, T040), the actual-reader count will jump from 1 to 12. No frontmatter update is needed to accommodate this — it is already populated.

### D. Prohibitions

None. This file is safe for additive edits but likely needs NO edits at all.

---

## File 4: maestro-layers-shared.md

### A. Content Orientation

**Consumer-only — orchestrator Phase 1 algorithm authority**. This file documents the CSA MAESTRO seven-layer taxonomy, the layer classification algorithm (keyword matching with L1-L7 evaluation order), the full keyword-to-layer mapping tables, and the output formats for Phase 1 component inventory and Phase 3 finding inheritance. **This entire file is orchestrator-owned**: the classification runs in orchestrator Phase 1, and layer values are inherited by findings in Phase 3 Table Assembly via component lookup — threat agents are NEVER involved in MAESTRO classification.

**Top-level sections** (from `grep -n '^## '`):
1. Classification Algorithm (line 21) — orchestrator Phase 1 matching rules + ordering rationale
2. Seven-Layer Taxonomy (line 50) — canonical L1-L7 definitions
3. Keyword-to-Layer Mapping (line 64) — full keyword tables (L1 through L7)
4. Output Format (line 196) — Phase 1 component inventory + Phase 3 finding inheritance

**Line count**: 213 (matches plan.md line 262)

**Note**: The file contains multiple `### ` (H3) sub-headings (e.g., `### Rules`, `### Ordering Rationale`, `### L1 — Foundation Model`, etc.) that were NOT captured by the `^## ` grep because they are H3-level. They document sub-structures of each H2 section.

### B. Consumers (declared vs actual)

**Frontmatter declares**:
```yaml
consumers:
  - orchestrator
  - risk-scorer
  - control-analyzer
  - threat-report
```
(4 declared consumers)

**Actual Readers** (Grep `maestro-layers-shared.md` across `.claude/agents/tachi/*.md`): **1 file**
- `.claude/agents/tachi/orchestrator.md`

**Mismatch**: MODERATE. Risk-scorer, control-analyzer, and threat-report are declared consumers but do not currently Read this file via `## Skill References`. They DO consume the MAESTRO layer value through finding records (the `maestro_layer` field populated by orchestrator Phase 3 inheritance) rather than by Reading the taxonomy file directly. This is a legacy Feature 084/091/136 frontmatter quirk — downstream agents reference `maestro_layer` in their templates and documentation but obtain the values from finding records, not from this reference file. **Out of scope for Feature 082 to fix.**

**Implication for Feature 082**: **Zero**. This file is forbidden from threat-agent consumption regardless. The orchestrator-only Reader count today (1) matches the desired end state for threat agents (0 of 11 threat agents Read this file).

### C. Additive Edit Plan

**NONE**.

This file is **FORBIDDEN** from modification in Feature 082 per FR-9 / ADR-023 Decision 2. MAESTRO classification is orchestrator-owned, and threat agents MUST remain MAESTRO-agnostic. Adding a producer-oriented section to this file would violate that boundary by implying threat agents should consume MAESTRO content.

### D. Prohibitions

**FORBIDDEN** for threat-agent consumption. Enforcement points (from tasks.md):

1. **FR-9** (spec.md): "Threat agents MUST NOT reference MAESTRO content" (spec invariant).
2. **ADR-023 Decision 2** (plan.md line 273): "MAESTRO layer inheritance runs entirely in orchestrator Phase 3 Table Assembly. Threat agents MUST remain MAESTRO-agnostic. A contributor who adds MAESTRO references to any threat agent reference file MUST have the change rejected in code review."
3. **T014** (Phase 1a grep check): Zero MAESTRO matches in prototype files (spoofing, prompt-injection). Pattern: `grep -rn "MAESTRO\|maestro-layers\|L[1-7]" .claude/agents/tachi/{spoofing,prompt-injection}.md .claude/skills/tachi-{spoofing,prompt-injection}/` returns zero.
4. **T054** (Phase 8 grep check): Zero MAESTRO matches across all 11 threat agents. Pattern: `grep -rn "maestro-layers\|maestro_layer\|MAESTRO" .claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,agent-autonomy,tool-abuse}.md .claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,agent-autonomy,tool-abuse}/` returns zero.

**Contributor-error risk**: A well-intentioned contributor extending the Phase 6 "shared ref consolidation" pattern might think maestro-layers-shared.md also needs a producer section analogous to finding-format-shared.md. **It does NOT**. Code review must actively reject any such PR and cite ADR-023 Decision 2.

**Search-and-replace risk**: If a contributor runs a global find/replace across `.claude/skills/tachi-shared/references/` (e.g., updating `schema_version` or renaming a taxonomy), maestro-layers-shared.md will be caught in the sweep. Mitigation: `git diff` inspection before commit. Changes to this file during Feature 082 must be rejected at PR review regardless of intent.

---

## Risks and Mitigations

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---------|-------------|:----------:|:------:|------------|
| R-AUD-1 | T042 accidentally modifies existing `## Risk Level Computation` section while appending producer section | Low | High | Separate commit for T042; diff review against pre-edit baseline; T046 regression check catches silent drift |
| R-AUD-2 | T042 producer section duplicates OWASP 3×3 matrix instead of cross-referencing | Medium | Low | Explicit guidance in this audit (§File 2.C risk R-AUD-4); reviewer checks for duplicate matrix tables |
| R-AUD-3 | T044 grep check for inline OWASP 3×3 finds legacy duplicate in `severity-bands-shared.md` and flags it as a violation | High | Medium | T044 scope MUST be limited to `.claude/agents/tachi/` only, NOT `.claude/skills/tachi-shared/references/`. Legacy duplication between severity-bands-shared.md and finding-format-shared.md is pre-existing and out of scope. |
| R-AUD-4 | T045 misinterpreted as requiring content changes instead of frontmatter-only | Medium | Low | T045 task description explicit on "frontmatter consumers list only" |
| R-AUD-5 | Contributor adds MAESTRO references to maestro-layers-shared.md as part of "shared ref consolidation" | Medium | High | FR-9 + T014 + T054 + ADR-023 Decision 2. Code review rejects any PR touching this file during Feature 082. |
| R-AUD-6 | R3 activation: T042 additive edit unexpectedly changes infra agent output (regression) | Low | High | T046 regression check comparing `examples/web-app/` pipeline output pre/post Phase 6. If any infra agent output diverges byte-wise beyond whitespace, roll back T042 and use `tachi-shared-threat/` isolation directory (R3 contingency from plan.md). |
| R-AUD-7 | stride-categories-shared.md body contains orchestrator-only content (dispatch rules, correlation rules) that threat agents should NOT rely on | Medium | Low | Threat agents read `## STRIDE Categories (6)` and `## AI Categories (5)` sections only (producer-relevant). Ignore dispatch, correlation, coverage-checklist sections (orchestrator-only). T042-T046 do NOT touch this file's content; no formal enforcement needed, but audit this in post-Phase-6 review. |

---

## Phase 6 Sequencing Recommendation

Per plan.md line 297 and tasks.md line 272 ("Phase 6 US3 Shared Ref Dedup (T042-T046) — 1-2h SERIAL SINGLE-WRITER"), the Phase 6 order is:

1. **T042** (single-writer, separate commit) — Append `## For Threat Agents (Producers)` section to `finding-format-shared.md`. Roughly 30-60 minutes.
2. **T043** (depends on T042) — Update all 11 threat agent `## Skill References` tables to Read `finding-format-shared.md`. Per-agent commits or one consolidated commit scoped to "shared-ref Read registration". Roughly 30-45 minutes.
3. **T044** (can run parallel to T043 but logically follows T042-T043) — Grep check `grep -rn "OWASP 3×3" .claude/agents/tachi/` returns zero. Scope MUST exclude shared reference files (see R-AUD-3). Roughly 10 minutes.
4. **T045** (optional, depends on T007) — This audit confirms `stride-categories-shared.md` frontmatter already lists all 11 threat agents. **T045 is likely a no-op**; the team may elect to skip it entirely or make it a rubber-stamp confirmation task. Roughly 5 minutes.
5. **T046** (depends on T042, T043, T044) — Infrastructure agent regression check via `/tachi.threat-model` on `examples/web-app/`. Compares `compensating-controls.md`, `risk-scores.md`, `threat-report.md` byte-wise (whitespace tolerant) against pre-Phase-6 baseline. **Gate criterion**: if any infra agent output diverges, R3 contingency activates — roll back T042 and switch to `tachi-shared-threat/` isolation. Roughly 15-20 minutes.

**Total Phase 6 wall-clock**: 1.5-2.5 hours realistic; 1-2 hours if T045 is skipped.

**Critical property**: Phase 6 tasks have NO `[P]` parallel markers in tasks.md (verified — see tasks.md line 193-197). All 5 tasks are serial, single-writer to prevent concurrent edits to the same file. T042 MUST complete before T043 can register Reads to the updated file. T046 MUST run last because its gate criterion depends on the full set of Phase 6 edits being in place.

---

## Completion Checklist

- [x] All 4 files read in full (line counts verified via `wc -l`)
- [x] Frontmatter `consumers:` extracted for each file
- [x] Actual Readers verified via `Grep` across `.claude/agents/tachi/*.md` (filename literal)
- [x] Summary table populated with lines/orientation/declared-actual/task mapping
- [x] T042 producer section content outlined with expected structure and line budget
- [x] T044 grep scope clarified (agents only, not shared refs) — addresses OWASP 3×3 duplicate
- [x] T045 determined likely no-op (frontmatter already aligned)
- [x] FR-9 / ADR-023 Decision 2 boundary loudly documented for maestro-layers-shared.md
- [x] Phase 6 sequencing recommendation provided
- [x] Risk register with 7 audit-derived risks and mitigations
- [x] No shared reference files modified during this audit
