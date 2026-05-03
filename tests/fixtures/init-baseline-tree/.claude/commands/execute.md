---
description: Execute ad-hoc tasks with automatic agent assignment and parallel orchestration without requiring full Triad workflow.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

Execute ad-hoc tasks with automatic agent assignment and parallel orchestration. Use for quick fixes, updates, and multi-file changes without the full triad workflow.

**Input**: Natural language task description (e.g., "Fix the OAuth bug and update docs")

**Output**: Completed tasks + Architect review (if code changes) + Execution summary

---

## Agent Assignment

See **[Agent Registry](.claude/agents/)** for task-to-agent mapping.

| Pattern | Agent |
|---------|-------|
| api, endpoint, backend, database | senior-backend-engineer |
| component, ui, react, frontend | frontend-developer |
| test, validation, e2e | tester |
| deploy, docker, ci/cd, infrastructure | devops |
| debug, investigate, root cause | debugger |
| security, vulnerability, auth | security-analyst |
| design, mockup, ux | ux-ui-designer |
| research, evaluate, best practice | web-researcher |
| docs/architecture/ | architect |
| docs/devops/ | devops |

---

## Workflow

### Step 1: Parse Tasks
Split user input by "and", ",", "then", ";" into discrete tasks. Classify each by keywords from the Agent Registry.

### Step 2: Assign Agents
Map each task to primary agent using the Agent Registry table.

### Step 3: Compute Waves
- **Wave 1**: Tasks with no dependencies (can run in parallel)
- **Wave 2+**: Tasks that depend on previous waves
- Sequential keywords ("then", "after") create dependencies

### Step 4: Execute
Launch agents in parallel within each wave using Task tool. Wait for wave completion before starting next wave.

### Step 5: Architect Review
If any code was changed, invoke architect agent to review technical decisions.

### Step 6: Summary
Report completed tasks, files modified, wave timings, and any issues.

---

## Examples

**Quick fix**:
```
/execute Fix the login redirect bug and add a test for it
```
→ Wave 1: debugger (fix) → Wave 2: tester (test)

**Parallel work**:
```
/execute Add logging to the API, update the README
```
→ Wave 1: senior-backend-engineer + product-manager (parallel)

**Full stack**:
```
/execute Implement user endpoint, add UI component, deploy to staging
```
→ Wave 1: senior-backend-engineer → Wave 2: frontend-developer → Wave 3: devops

---

## Notes

- Use `/execute` for quick, ad-hoc work (< 1 day effort)
- Use `/aod.*` workflow for larger features requiring governance
- Architect review is automatic for any code changes
- Failed tasks don't halt execution - summary reports all outcomes
