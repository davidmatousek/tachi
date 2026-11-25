# Install Manifest

Canonical list of files and directories that must be copied when installing tachi into a target project. Maintain this file whenever agents, commands, schemas, or templates are added or removed.

## Distributable Directories

| Directory | Purpose | Required By |
|-----------|---------|-------------|
| `.claude/agents/tachi/` | 21 threat analysis agent definitions | All commands |
| `.claude/commands/` (6 files) | Slash command definitions | User invocation |
| `schemas/` | YAML contracts (finding, input, output, scoring) | orchestrator, risk-scorer, control-analyzer |
| `templates/tachi/output-schemas/` | Canonical output format templates | orchestrator, risk-scorer, control-analyzer, threat-report |
| `templates/tachi/infographics/` | Infographic design templates | threat-infographic |
| `templates/tachi/security-report/` | Typst PDF report templates | report-assembler |
| `scripts/` (15 Python files) | Deterministic extraction, population, SARIF, batch-planning, rendering, joining and assembly scripts, and the helpers they import | report-assembler, threat-infographic, orchestrator, risk-scorer, control-analyzer, threat-report, attack-tree-delta |
| `.claude/skills/tachi-*/` (21 dirs) | Agent skill references (detection patterns, domain knowledge) | All threat agents, infographic, report-assembler |
| `adapters/claude-code/agents/references/` | SARIF generation and validation guides | risk-scorer, control-analyzer |
| `brand/` | Logo assets for branded PDF reports | report-assembler |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | Full walkthrough with worked examples | User reference |
| `docs/guides/ISOLATED_OPERATION_TACHI.md` | Isolated-operation runbook: egress profile, session profile, probes, write locations | User reference |

## Command Files

Copy these 6 files from `.claude/commands/` to the target project's `.claude/commands/`:

| File | Slash Command |
|------|---------------|
| `tachi.threat-model.md` | `/tachi.threat-model` |
| `tachi.risk-score.md` | `/tachi.risk-score` |
| `tachi.compensating-controls.md` | `/tachi.compensating-controls` |
| `tachi.infographic.md` | `/tachi.infographic` |
| `tachi.security-report.md` | `/tachi.security-report` |
| `tachi.architecture.md` | `/tachi.architecture` |

## Agent Files

Copy the entire `.claude/agents/tachi/` directory. Current agents:

| File | Role |
|------|------|
| `orchestrator.md` | Pipeline coordinator |
| `spoofing.md` | STRIDE: Spoofing |
| `tampering.md` | STRIDE: Tampering |
| `repudiation.md` | STRIDE: Repudiation |
| `info-disclosure.md` | STRIDE: Information Disclosure |
| `denial-of-service.md` | STRIDE: Denial of Service |
| `privilege-escalation.md` | STRIDE: Elevation of Privilege |
| `prompt-injection.md` | AI: Prompt Injection |
| `data-poisoning.md` | AI: Data Poisoning |
| `model-theft.md` | AI: Model Theft |
| `output-integrity.md` | AI: Output Integrity |
| `misinformation.md` | AI: Misinformation |
| `agent-autonomy.md` | Agentic: Agent Autonomy |
| `tool-abuse.md` | Agentic: Tool Abuse |
| `human-trust-exploitation.md` | Agentic: Human-Agent Trust Exploitation |
| `threat-report.md` | Narrative report generator |
| `risk-scorer.md` | Quantitative risk scoring |
| `control-analyzer.md` | Compensating controls analysis |
| `threat-infographic.md` | Visual infographic generator |
| `report-assembler.md` | PDF report assembler |
| `attack-tree-delta.md` | Attack tree generation sub-agent (invoked by threat-report for Section 5) |

## Script Files

Copy these 15 Python files from `scripts/` to the target project's `scripts/`:

| File | Purpose | Invoked By |
|------|---------|------------|
| `extract-report-data.py` | Parses tachi artifacts and generates `report-data.typ` for Typst compilation; also renders attack-tree Mermaid blocks to PNG via mmdc | report-assembler (via `/tachi.security-report`) |
| `extract-infographic-data.py` | Parses tachi artifacts and generates infographic specification JSON | threat-infographic (via `/tachi.infographic`) |
| `tachi_parsers.py` | Shared parser helpers imported by the extraction and population scripts, `sarif_common.py`, `tachi_scoring_rules.py`, `tachi-stage.py`, the two renderers and the four threat-model scripts | extract-report-data.py, extract-infographic-data.py, populate-affected-assets.py, sarif_common.py, tachi_scoring_rules.py, tachi-stage.py, render-risk-scores.py, render-compensating-controls.py, join-threats-md.py, attack-chains.py, assemble-report.py, generate-threats-sarif.py |
| `populate-affected-assets.py` | Deterministically joins architecture `[asset:...]` tags to findings by component and upserts the `## Affected Assets` block into `threats.md`; `render-risk-scores.py` loads it by path for the same component join | orchestrator (via `/tachi.threat-model`), `/tachi.risk-score`, render-risk-scores.py |
| `tachi_parts.py` | Shared helper for the batched stages: the part-file loader and validators, identifier allow-lists, path guards, atomic writes and the stamped version. Imported, never run | tachi_parsers.py, sarif_common.py, tachi_scoring_rules.py, tachi-stage.py, render-risk-scores.py, render-compensating-controls.py, join-threats-md.py, attack-chains.py, assemble-report.py, generate-threats-sarif.py |
| `tachi_scoring.py` | Shared helper: the CVSS 3.1 calculator, scoring constants and stored-value arithmetic. Imported, never run | sarif_common.py, tachi_scoring_rules.py, tachi-stage.py, render-risk-scores.py, render-compensating-controls.py, assemble-report.py, generate-threats-sarif.py |
| `tachi_scoring_rules.py` | Shared helper: the rules that decide which values the scoring arithmetic runs on (baseline resolution and reading, the asset-tag source, which findings go to the scorer agent, and each carried value's governance). The planner and the renderers both apply it, and the report assembler resolves its baseline directory through it. Imported, never run | tachi-stage.py, render-risk-scores.py, render-compensating-controls.py, assemble-report.py |
| `sarif_common.py` | Shared SARIF helpers and emitter: the rule map, result identity and location resolver. Imported, never run | tachi-stage.py, render-risk-scores.py, render-compensating-controls.py, generate-threats-sarif.py |
| `tachi-stage.py` | Plans, reconciles and fails a batched stage, so that a stage with more findings than one agent can write is split into batches and resumed from the files on disk; its `architecture-source` command writes the architecture body line into `threats.md` | `/tachi.risk-score`, `/tachi.compensating-controls`, orchestrator (via `/tachi.threat-model`) |
| `render-risk-scores.py` | Renders `risk-scores.md` and `risk-scores.sarif` from the scorer agent's part files: it computes every score, band, total and identity, checks both files against the threat model, and only then moves them onto their names | `/tachi.risk-score` |
| `render-compensating-controls.py` | Renders `compensating-controls.md` and `compensating-controls.sarif` from the control-analyzer agent's part files and the scorer's `risk-scores.md`: it takes each inherent score from that file, computes every residual score, band, total and identity, checks both files against the scored findings and the threat model, and only then moves them onto their names | `/tachi.compensating-controls` |
| `join-threats-md.py` | Joins the orchestrator's `threats-md` part files into `threats.md`: it writes the frontmatter and every heading, header, fixed table and note, puts the parts' rows between them, checks the staged file against the section manifest and the parts, and only then moves it onto its name | orchestrator (via `/tachi.threat-model`) |
| `attack-chains.py` | Forms Phase 3.5's attack chains from Section 7 and the Phase 1 inventory (`plan`), renders `attack-chains.md` and the outcome record in `threats.md` from the orchestrator's narratives (`render`), and checks the record against the file (`check`) | orchestrator (via `/tachi.threat-model`: `plan` and `render`), `/tachi.threat-model` (`check`) |
| `assemble-report.py` | Copies and merges the attack trees (`trees`), and builds `threat-report.md` from the threat-report agent's part files, with its tables, numbering and roadmap written in code (`report`); each mode checks everything before it writes | orchestrator (via `/tachi.threat-model`: `trees`), `/tachi.threat-model` (`report`) |
| `generate-threats-sarif.py` | Generates `threats.sarif` from the compiled `threats.md` through the shared emitter, so that no agent writes the file | `/tachi.threat-model` |

Dependency note: stdlib-only at import; PyYAML is imported lazily for the PDF coverage-attestation page. `tachi_parts.py`, `tachi_scoring.py`, `tachi_scoring_rules.py`, `sarif_common.py`, `tachi-stage.py`, `render-risk-scores.py`, `render-compensating-controls.py`, `join-threats-md.py`, `attack-chains.py`, `assemble-report.py` and `generate-threats-sarif.py` run on Python 3.9 and later, and `tachi-stage.py`, the two renderers and the four threat-model scripts each refuse an older interpreter before they import anything.

**Critical**: If a script is missing, the report and infographic agents stop with `EXTRACTION SCRIPT MISSING` and name the missing files, and a pipeline step that runs `populate-affected-assets.py` fails at that step. The scripts also import each other when they load: `tachi_parsers.py` imports `tachi_parts.py`; `sarif_common.py` and `tachi_scoring_rules.py` each import `tachi_parts.py`, `tachi_scoring.py` and `tachi_parsers.py`; `tachi-stage.py`, `render-risk-scores.py` and `render-compensating-controls.py` each import all five helpers; `join-threats-md.py` and `attack-chains.py` each import `tachi_parts.py` and `tachi_parsers.py`; `assemble-report.py` imports those two and `tachi_scoring.py` and `tachi_scoring_rules.py`; and `generate-threats-sarif.py` imports `sarif_common.py`, `tachi_parts.py`, `tachi_parsers.py` and `tachi_scoring.py`. A project that has a script but lacks a file it imports fails with an import error, so a partial copy breaks the report and infographic scripts too. `render-risk-scores.py` also loads `populate-affected-assets.py` by path when it runs, and stops with exit code 1 and the file's name when that file is not installed. Always include these files when distributing tachi.

Every other file in `scripts/` is tachi-internal and is NOT distributed to target projects.

## Schema Files

Copy the entire `schemas/` directory. Current schemas:

- `finding.yaml` -- individual finding structure
- `input.yaml` -- architecture input format
- `output.yaml` -- threats.md output structure
- `report.yaml` -- narrative report structure
- `risk-scoring.yaml` -- scoring methodology and weights
- `compensating-controls.yaml` -- controls analysis structure
- `infographic.yaml` -- infographic specification structure
- `security-report.yaml` -- PDF report configuration

## Machine-Parseable Manifest

The install script parses this section automatically. One path per line — directories end with `/`, files do not. Lines starting with `#` are comments and are skipped.

<!-- BEGIN MANIFEST -->
.claude/agents/tachi/
.claude/commands/tachi.threat-model.md
.claude/commands/tachi.risk-score.md
.claude/commands/tachi.compensating-controls.md
.claude/commands/tachi.infographic.md
.claude/commands/tachi.security-report.md
.claude/commands/tachi.architecture.md
.claude/skills/tachi-shared/
.claude/skills/tachi-infographics/
.claude/skills/tachi-orchestration/
.claude/skills/tachi-risk-scoring/
.claude/skills/tachi-report-assembly/
.claude/skills/tachi-threat-reporting/
.claude/skills/tachi-control-analysis/
.claude/skills/tachi-spoofing/
.claude/skills/tachi-tampering/
.claude/skills/tachi-repudiation/
.claude/skills/tachi-info-disclosure/
.claude/skills/tachi-denial-of-service/
.claude/skills/tachi-privilege-escalation/
.claude/skills/tachi-prompt-injection/
.claude/skills/tachi-agent-autonomy/
.claude/skills/tachi-tool-abuse/
.claude/skills/tachi-data-poisoning/
.claude/skills/tachi-model-theft/
.claude/skills/tachi-output-integrity/
.claude/skills/tachi-misinformation/
.claude/skills/tachi-human-trust-exploitation/
schemas/
templates/tachi/
scripts/extract-report-data.py
scripts/extract-infographic-data.py
scripts/tachi_parsers.py
scripts/populate-affected-assets.py
scripts/tachi_parts.py
scripts/tachi_scoring.py
scripts/sarif_common.py
scripts/tachi-stage.py
scripts/tachi_scoring_rules.py
scripts/render-risk-scores.py
scripts/render-compensating-controls.py
scripts/join-threats-md.py
scripts/attack-chains.py
scripts/assemble-report.py
scripts/generate-threats-sarif.py
adapters/claude-code/agents/references/
brand/
docs/guides/DEVELOPER_GUIDE_TACHI.md
docs/guides/ISOLATED_OPERATION_TACHI.md
<!-- END MANIFEST -->

## Maintenance Checklist

When adding a new feature, check whether it requires updates to:

- [ ] A new agent file in `.claude/agents/tachi/` -- add to agent table above
- [ ] A new command file in `.claude/commands/` -- add to command table above
- [ ] A new schema in `schemas/` -- add to schema list above
- [ ] A new output template in `templates/tachi/output-schemas/`
- [ ] A new infographic template in `templates/tachi/infographics/`
- [ ] New report page templates in `templates/tachi/security-report/`
- [ ] A new distributable Python script in `scripts/` -- add to script table above
- [ ] New reference docs in `adapters/claude-code/agents/references/`
- [ ] Manual install blocks derive from this manifest; no edit needed in `README.md` or `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- [ ] Update the machine-parseable manifest section (`<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->`)
