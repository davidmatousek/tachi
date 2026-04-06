# Install Manifest

Canonical list of files and directories that must be copied when installing tachi into a target project. Maintain this file whenever agents, commands, schemas, or templates are added or removed.

## Distributable Directories

| Directory | Purpose | Required By |
|-----------|---------|-------------|
| `.claude/agents/tachi/` | 17 threat analysis agent definitions | All commands |
| `.claude/commands/` (5 files) | Slash command definitions | User invocation |
| `schemas/` | YAML contracts (finding, input, output, scoring) | orchestrator, risk-scorer, control-analyzer |
| `templates/tachi/output-schemas/` | Canonical output format templates | orchestrator, risk-scorer, control-analyzer, threat-report |
| `templates/tachi/infographics/` | Infographic design templates | threat-infographic |
| `templates/tachi/security-report/` | Typst PDF report templates | report-assembler |
| `adapters/claude-code/agents/references/` | SARIF generation and validation guides | risk-scorer, control-analyzer |
| `brand/` | Logo assets for branded PDF reports | report-assembler |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | Full walkthrough with worked examples | User reference |

## Command Files

Copy these 5 files from `.claude/commands/` to the target project's `.claude/commands/`:

| File | Slash Command |
|------|---------------|
| `threat-model.md` | `/threat-model` |
| `risk-score.md` | `/risk-score` |
| `compensating-controls.md` | `/compensating-controls` |
| `infographic.md` | `/infographic` |
| `security-report.md` | `/security-report` |

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
.claude/commands/threat-model.md
.claude/commands/risk-score.md
.claude/commands/compensating-controls.md
.claude/commands/infographic.md
.claude/commands/security-report.md
schemas/
templates/tachi/
adapters/claude-code/agents/references/
brand/
docs/guides/DEVELOPER_GUIDE_TACHI.md
<!-- END MANIFEST -->

## Maintenance Checklist

When adding a new feature, check whether it requires updates to:

- [ ] A new agent file in `.claude/agents/tachi/` -- add to agent table above
- [ ] A new command file in `.claude/commands/` -- add to command table above
- [ ] A new schema in `schemas/` -- add to schema list above
- [ ] A new output template in `templates/tachi/output-schemas/`
- [ ] A new infographic template in `templates/tachi/infographics/`
- [ ] New report page templates in `templates/tachi/security-report/`
- [ ] New reference docs in `adapters/claude-code/agents/references/`
- [ ] Update install instructions in `README.md` and `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- [ ] Update the machine-parseable manifest section (`<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->`)
