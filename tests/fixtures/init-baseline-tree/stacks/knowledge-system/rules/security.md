# Knowledge System Security Rules

## PII Detection in Master Content

- ALWAYS audit `_Global/VoiceProfile.md` for personally identifiable information before committing — voice attributes describe style patterns, NOT personal facts
- ALWAYS audit `_Global/MasterContent/` files for embedded PII — no real names, addresses, phone numbers, email addresses, or government identifiers unless the builder explicitly intends public disclosure
- ALWAYS scan for PII patterns: phone numbers, email addresses, social security numbers, physical addresses, passport numbers, driver's license numbers
- NEVER store real contact information in VoiceProfile as "examples" — use anonymized placeholders or pattern descriptions instead

## Sensitive Content in Narratives

- ALWAYS review `_Global/Narratives/` files for sensitive personal stories, health information, legal matters, or financial details
- ALWAYS verify sensitive narratives have `sensitivity: high` in frontmatter so commands can filter them from bulk operations
- ALWAYS flag narratives containing: medical conditions, legal proceedings, financial amounts, confidential business information, or personal relationships
- NEVER include narratives with unfiltered sensitive content in automated bulk output generation

## Credential and Secret Scanning

- ALWAYS scan `_Config/Presets/` for API keys, tokens, passwords, or connection strings
- ALWAYS scan `_Config/ContextLoading.yaml` for hardcoded file paths containing user home directories or system-specific paths
- ALWAYS scan `_Config/ProjectMeta.yaml` for credentials in tracking or configuration fields
- NEVER store credentials in any content file — use environment variables referenced by name, not value
- NEVER hardcode absolute file paths — use relative paths from the project root

## Content Audit Patterns

- ALWAYS run a PII scan before the first output generation during validation phase
- ALWAYS include PII detection as a quality dimension in `_Config/ScoringRubric.md` when the domain involves personal information
- ALWAYS re-audit `_Global/` content after any modifications — changes propagate to all subsequent outputs
- ALWAYS verify `.gitignore` excludes files containing PII if the repository is shared
- NEVER skip security review on `_Global/` content changes — these files are source of truth for all outputs

## Output Security

- ALWAYS review generated outputs in `_Output/` for PII leakage from master content
- ALWAYS verify archived outputs in `_Archive/` do not contain unintended PII before sharing or publishing
- NEVER expose `_Output/` or `_Archive/` directories in public repositories without PII review
