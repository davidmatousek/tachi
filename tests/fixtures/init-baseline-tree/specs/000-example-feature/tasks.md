# Tasks: Example Feature

> **Example** -- delete this directory after creating your first real feature with `/aod.tasks`.

**Feature ID**: 000
**Status**: Example
**PM Sign-off**: N/A | **Architect Sign-off**: N/A | **Team-Lead Sign-off**: N/A

---

## Task Breakdown

| ID | Task | Agent | Status | Dependencies | Est. |
|----|------|-------|--------|--------------|------|
| T001 | [Implement core logic] | backend | [ ] | None | 1h |
| T002 | [Create API endpoint] | backend | [ ] | T001 | 1h |
| T003 | [Build UI component] | frontend | [ ] | T002 | 2h |
| T004 | [Write unit tests] | tester | [ ] | T001, T002 | 1h |
| T005 | [Write integration tests] | tester | [ ] | T003 | 1h |
| T006 | [Update documentation] | docs | [ ] | T003 | 30m |

## Execution Waves

- **Wave 1** [P]: T001 (no dependencies)
- **Wave 2** [P]: T002, T004 (depend on T001)
- **Wave 3** [P]: T003 (depends on T002)
- **Wave 4** [P]: T005, T006 (depend on T003)
