# SC-A3 evidence (T030): the privilege guard on a throwaway PR

| Item | Value |
|---|---|
| Task | T030 (`tasks.md`); spec SC-003 (PRD SC-A3) |
| PR | #398, `391-sc-a3-evidence` → `main`. A throwaway, closed unmerged |
| Content under test | The Part A tip `41c998e`, plus one commit |
| Red commit | `a1d1df8`: adds `WebFetch` to the `tools:` list of `.claude/agents/tachi/spoofing.md` |
| Green commit | `aaa2d84`: reverts `a1d1df8`. The tree is again the Part A tip's |
| Date | 2026-11-20 |

**Why the base is `main`, not the Part A branch.** Path-filtered `pull_request` workflows look at the PR's diff. After the revert, a PR against the Part A branch would have an empty diff, so no workflow would run and the green leg could not be shown. Against `main` the PR still carries Part A's diff, so the same workflows run on both commits. R-8 still holds: #392 and part-b were never used.

## Results

| Workflow, job | Red `a1d1df8` | Green `aaa2d84` |
|---|---|---|
| `tachi permissions-verify`: the guard, `--self-test` | **failure** (run 44746447415) | success (run 44746605459) |
| `tachi install fidelity`, `manifest-completeness` | **failure** (run 44746447299): `test_installed_agent_tools_match_matrix[install-sh]` and `[manual-loop]` (SC-A4) | success (run 44746605677) |
| `tachi install fidelity`, `report-posture` and `extraction-fidelity` | success | success |
| `tachi pytest`, both legs | **failure** (run 44746447360) on both legs. In `test_agent_privilege_guard.py`, the four live-tree cases fail, and its 140 mutation cases error by design: their fixture refuses a live copy that is not green. Every other module passes | success (run 44746605558), both legs |
| `gitleaks`, `mmdc preflight`, `maestro coverage`, `catalog-drift` | success | success |

## The guard's output

Red (`a1d1df8`), the guard step in `tachi permissions-verify`:

```
[391] C1 roster           PASS  21 agents, 1 allow-listed document(s)
[391] C2 tools            FAIL  1 finding(s)
[391] C3 model            PASS  21 agents
[391] C4 frontmatter keys PASS  21 agents
[391] C5 command keys     PASS  6 commands
[391] C6 bash families    PASS  3 Bash-capable agents
[391] C7 write locations  PASS  21 paths
[391] C8 M1 a tool (Bash) added to tachi-agent-autonomy: detected by C2
[391] C8 M2 a planted agent with name: helper: detected by C1
[391] C8 M3 an unlisted .md file without frontmatter: detected by C1
[391] C8 M4 a duplicate of the name tachi-agent-autonomy: detected by C1
[391] C8 M5 the allow-listed document with planted frontmatter: detected by C1
[391] C8 self-test        PASS
[391] FAIL C2 .claude/agents/tachi/spoofing.md: tools differ from the section 8 row 'tachi-spoofing': file has ['Glob', 'Grep', 'Read', 'WebFetch'], matrix has ['Glob', 'Grep', 'Read'] (added ['WebFetch'], removed [])
[391] RESULT: drift (exit 1)
[391] HINT: a deliberate privilege change edits the file and docs/standards/CLAUDE_PERMISSIONS.md (and the runbook's section 5 for write paths) in the same commit
```

Green (`aaa2d84`):

```
[391] C1 roster           PASS  21 agents, 1 allow-listed document(s)
[391] C2 tools            PASS  21 agents
[391] C3 model            PASS  21 agents
[391] C4 frontmatter keys PASS  21 agents
[391] C5 command keys     PASS  6 commands
[391] C6 bash families    PASS  3 Bash-capable agents
[391] C7 write locations  PASS  21 paths
[391] C8 M1 a tool (Bash) added to tachi-agent-autonomy: detected by C2
[391] C8 M2 a planted agent with name: helper: detected by C1
[391] C8 M3 an unlisted .md file without frontmatter: detected by C1
[391] C8 M4 a duplicate of the name tachi-agent-autonomy: detected by C1
[391] C8 M5 the allow-listed document with planted frontmatter: detected by C1
[391] C8 self-test        PASS
[391] RESULT: pass (exit 0)
```

## What this shows, against SC-003

- **The PR leg, live.** A tool added to one agent turns CI red: the guard (C2), and the install-fidelity assertion that installed agents match §8 on both install paths (SC-A4). Reverting it turns CI green.
- **The self-test red path runs on every run.** C8 planted its five mutations and detected each one on both commits, including the red one, where the live tree was already drifted.
- **The other synthetic cases** that SC-003 names (a tool removal, a model change, an added key, a command-frontmatter change and the three roster negatives) are shown by `tests/scripts/test_agent_privilege_guard.py` (T026), which `tachi-pytest.yml` runs on every PR and every push to `main`.
- **The `push:[main]` lag.** The workflow's push leg (`push: branches: [main]`, the same `&verify_paths` list) cannot be shown before the feature merges, because the guard steps reach `main` only with #392. The first push to `main` after that merge is the first push-leg run of the guard. `/aod.deliver` records its run id here (`feasibility-check.md` (e): the `push:[main]` evidence arrives only at merge).

## Cleanup

PR #398 is closed unmerged and its remote branch is deleted. The local branch `391-sc-a3-evidence` stays, because `git branch -D` is denied in this repository (R-8); the maintainer removes it.
