# adapters/

Platform-specific adapters that configure tachi's threat modeling for different environments, toolchains, and output targets. Adapters control how threat findings are formatted, scored, and integrated with external systems.

## Contents

- `ContextLoading.yaml` — Defines when and how agents load context (architecture inputs, reference data, terms)
- `ScoringRubric.md` — Threat severity scoring criteria (likelihood, impact, risk rating)
- `ProjectMeta.yaml` — Project-level metadata (name, version, default output format)
- `Terms/` — Domain terminology files for consistent threat language
- `Presets/` — Output presets for different audiences (security team, executive summary, compliance)
