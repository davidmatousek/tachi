# Security Analyst — Knowledge System Supplement

## Stack Context

Knowledge systems manage domain expertise in markdown and YAML files. Security concerns center on content rather than application vulnerabilities: personally identifiable information (PII) in master content, sensitive personal stories in narratives, and credentials accidentally pasted into configuration files.

Key security surfaces:
- `_Global/VoiceProfile.md` — may contain PII if voice attributes include personal facts
- `_Global/MasterContent/` — may contain contact details, government IDs, or personal identifiers
- `_Global/Narratives/` — may contain sensitive stories (health, legal, financial)
- `_Config/Presets/` — may contain pasted API keys, tokens, or passwords
- `_Config/ContextLoading.yaml` — may contain hardcoded paths with user home directories

## Conventions

- ALWAYS scan VoiceProfile.md for PII — voice attributes describe style patterns, not personal facts (no addresses, phone numbers, government IDs)
- ALWAYS audit MasterContent files for embedded personal contact details or government identifiers
- ALWAYS review Narratives for sensitive content — flag health information, legal matters, financial details
- ALWAYS check that sensitive narratives have `sensitivity: high` in frontmatter for command filtering
- ALWAYS scan Presets and ContextLoading.yaml for hardcoded credentials, tokens, or system paths
- ALWAYS verify PII detection is included as a quality dimension in ScoringRubric.md when the domain involves personal information

## Anti-Patterns

- **PII in VoiceProfile** (Source: PersonalResumeBuilder): Real phone number and email address included in VoiceProfile as "contact style" examples. VoiceProfile should describe communication patterns, not contain actual contact information.
- **Credentials in Presets** (Source: PersonalResumeBuilder): API key for a formatting service pasted into a preset file. Presets configure output behavior; credentials belong in environment variables.
- **Unfiltered sensitive narratives** (Source: PersonalResumeBuilder): A personal health narrative was included in all generated resumes regardless of relevance or sensitivity, because narratives lacked filtering metadata. Mark sensitive narratives with `sensitivity: high` in frontmatter.

## Guardrails

- Security review covers content safety, not application security (there is no application code)
- Recommend `sensitivity` frontmatter fields for narrative filtering — do not mandate removal of all sensitive content
- PII audit should run before first output generation and after any `_Global/` content changes
- Content is stored on local filesystem — no network-based data exposure concerns unless the builder adds external integrations
