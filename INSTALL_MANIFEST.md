# Install Manifest

Canonical list of files and directories that must be copied when installing tachi into a target project. Maintain this file whenever agents, commands, schemas, or templates are added or removed.

## Distributable Directories

| Directory | Purpose | Required By |
|-----------|---------|-------------|
| `.claude/agents/tachi/` | 18 threat analysis agent definitions | All commands |
| `.claude/commands/` (6 files) | Slash command definitions | User invocation |
| `schemas/` | YAML contracts (finding, input, output, scoring) | orchestrator, risk-scorer, control-analyzer |
| `templates/tachi/output-schemas/` | Canonical output format templates | orchestrator, risk-scorer, control-analyzer, threat-report |
| `templates/tachi/infographics/` | Infographic design templates | threat-infographic |
| `templates/tachi/security-report/` | Typst PDF report templates | report-assembler |
| `.claude/skills/tachi-*/` (18 dirs) | Agent skill references (detection patterns, domain knowledge) | All threat agents, infographic, report-assembler |
| `adapters/claude-code/agents/references/` | SARIF generation and validation guides | risk-scorer, control-analyzer |
| `brand/` | Logo assets for branded PDF reports | report-assembler |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | Full walkthrough with worked examples | User reference |
| `docs/platform-compatibility.md` | Harness matrix, adapter support levels, and fallback behavior | User reference |
| `scripts/` | None distributed: runtime command glue remains repo-internal | report-assembly runtime paths |

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
| `agent-autonomy.md` | Agentic: Agent Autonomy |
| `tool-abuse.md` | Agentic: Tool Abuse |
| `threat-report.md` | Narrative report generator |
| `risk-scorer.md` | Quantitative risk scoring |
| `control-analyzer.md` | Compensating controls analysis |
| `threat-infographic.md` | Visual infographic generator |
| `report-assembler.md` | PDF report assembler |
| `attack-tree-delta.md` | Attack tree generation sub-agent (invoked by threat-report for Section 5) |

## Script Files

No legacy extract-orchestrator scripts are shipped in `tachi-rust` distribution. Output generation now routes through the Rust command layer in `tachi-cli`.

No files are copied in this section by the Rust installer.

Other files in `scripts/` (`check.sh`, `install.sh`, `generate-adapter-version.sh`, `polish-release-notes.sh`, `sync-upstream.sh`) are repository internals and are NOT distributed to target projects.

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
schemas/
templates/tachi/
adapters/claude-code/agents/references/
brand/
docs/guides/DEVELOPER_GUIDE_TACHI.md
docs/platform-compatibility.md
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
- [ ] Update install instructions in `README.md` and `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- [ ] Update compatibility guidance in `README.md`, `docs/platform-compatibility.md`, and `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- [ ] Update the machine-parseable manifest section (`<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->`)
