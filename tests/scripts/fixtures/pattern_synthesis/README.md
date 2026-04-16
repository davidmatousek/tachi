# Pattern Synthesis Test Fixtures

Fixtures for `tests/scripts/test_pattern_synthesis.py` — exercising the
Phase 3.6 pattern synthesis engine (Feature 142) deterministically.

## Contents

- `arch_*.yaml` — synthetic Phase 1 architecture abstracts (component
  inventory + data flow graph + architecture description). One per
  baseline example plus the `single_agent_with_fine_tuning` synthetic
  case (architect LOW-5) and the `agentic_app_extended` case (post-T020).

- `threats_pre_f142.md` — pre-Feature-142 threats.md snapshot (Section 7
  findings table WITHOUT the Pattern column). Used to exercise
  backward-compat parsing (FR-017 default `none`).

- `threats_post_f142.md` — post-Feature-142 threats.md snapshot (Section
  7 findings table WITH the Pattern column, including `—` empties and
  canonical pattern enum values).

- `rules.yaml` — test-local structured copy of the classification rules
  R-01 through R-06. Mirrors
  `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md`
  Section 3. Kept in-repo (vs reading the markdown rule table at test
  time) so the test suite can exercise tied-priority cases and synthetic
  rule variants without edits to the shared reference.

## Fixture Files Are Synthetic

These fixtures do NOT duplicate real `examples/<name>/` content. They are
deliberately small synthetic abstractions so the test suite runs fast
and failures point to synthesis-engine logic bugs (not parser or
example-architecture drift).
