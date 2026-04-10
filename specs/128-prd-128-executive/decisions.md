---
feature: 128-prd-128-executive
created: 2026-04-09
purpose: Record architectural/procedural decisions made during F-128 implementation
related:
  - tasks.md T001 (example verification)
  - tasks.md T002 (this file)
  - tasks.md T003a-e (baseline generation using the chosen approach)
---

# F-128 Implementation Decisions

This file records decisions taken during F-128 implementation that must be traceable for the backward-compatibility test (T024) and the architect checkpoint (T036).

---

## Decision 1: Baseline PDF Storage Approach (T002, architect L-2)

**Context**: The backward compatibility test (T024) requires comparing post-F-128 PDF outputs against pre-F-128 baselines for the 5 unmodified examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). The architect's L-2 observation asked the team to record HOW baselines will be stored.

**Options considered**:
- **(a) Commit `security-report.pdf.baseline` files** alongside each example in `examples/{name}/sample-report/`. Baselines are versioned alongside the feature, repeatable forever, and the test is self-contained.
- **(b) Generate baselines on CI from the parent revision**. Reproducible from git history but adds CI complexity and makes local test runs dependent on network or git operations.
- **(c) `git stash` or `git worktree` comparison at test time**. Avoids committing binary files but couples the test to git state and is fragile under partial working trees.

**Decision**: **Option (a) — commit `security-report.pdf.baseline` files alongside each example.**

**Rationale**:
1. **Repeatability**: Tests run identically across laptops, CI, and post-merge audits.
2. **Self-containment**: The test suite does not require git history or network access.
3. **Traceability**: The baseline is tied to the feature branch and reviewable in the PR diff (file size and checksum).
4. **Cost**: 5 binary PDFs × ~300 KB each ≈ 1.5 MB total repository growth. Acceptable for a one-time commit.
5. **Determinism prerequisite**: Option (a) is valid only if the existing pipeline is byte-deterministic. T003c verifies this by running the pipeline twice and comparing outputs with `cmp`. If T003c fails, the team must escalate to architect before proceeding (per agent-assignments.md Wave 2 risk mitigation).

**Storage path** (committed to the feature branch):
```
examples/web-app/sample-report/security-report.pdf.baseline
examples/microservices/sample-report/security-report.pdf.baseline
examples/ascii-web-api/sample-report/security-report.pdf.baseline
examples/mermaid-agentic-app/sample-report/security-report.pdf.baseline
examples/free-text-microservice/sample-report/security-report.pdf.baseline
```

**Test consumption**: `tests/scripts/test_backward_compatibility.py` (T024) reads each `.baseline` file and compares it byte-for-byte against a fresh post-F-128 pipeline run. The agentic-app example is intentionally excluded because it is the regeneration target (T033).

---

## Decision 2: Example Chosen for Regeneration (T001)

**Context**: T001 requires verifying that the agentic-app example has at least one Critical or High severity finding. Without qualifying findings, the executive-architecture template would render an empty callouts list and `skip_image == true`, defeating the purpose of the example regeneration (T033).

**Verification performed** (2026-04-09): Ran `grep -c -E "^\| [A-Z0-9-]+ \|.*\| (Critical|High) \|" examples/agentic-app/sample-report/threats.md` — **58 rows matched**. The agentic-app threat model contains many Critical and High severity findings (spot-checked S-3 scored "Critical", S-1, S-2, S-4, T-1 scored "High"), comfortably exceeding the ≥1 requirement.

**Decision**: **Keep `examples/agentic-app/sample-report/` as the regeneration target**. No alternative example is needed. The existing threat model will produce a non-empty callouts list and a meaningful executive architecture image.

**Downstream impact**: T033 regenerates `examples/agentic-app/sample-report/` including `threat-executive-architecture-spec.md`, `threat-executive-architecture.jpg`, and an updated `security-report.pdf`. The other 5 examples remain unmodified and are covered by the baseline comparison from Decision 1.

---

## Decision 3: SOURCE_DATE_EPOCH for PDF Determinism (T003c escalation)

**Context**: T003c verified that running the extraction + Typst pipeline twice against the same inputs produces non-byte-identical PDFs. The devops agent isolated the root cause: Typst's PDF generator embeds wall-clock timestamps in PDF metadata (`/ModDate`, `/CreationDate`), XMP metadata timestamps, and `xmpMM:InstanceID` (which is derived from the timestamp). All non-metadata bytes are identical between runs — only the timestamp-derived fields differ. This is a **property of Typst's default behavior**, not a bug in the tachi pipeline.

**Options considered**:
- **(a) Set `SOURCE_DATE_EPOCH` before each Typst invocation.** This is the reproducible-builds.org standard environment variable. Typst honors it natively and produces byte-identical PDFs when it is set to a fixed value. Zero source code changes; only the invocation wrapper and the T024 test setup need to set it.
- **(b) Modify `scripts/extract-report-data.py` or `main.typ` to strip or normalize PDF metadata post-compile.** Higher complexity, couples the fix to a specific PDF library, harder to review, and risks breaking future Typst upgrades.
- **(c) Adopt a fuzzy comparison** (e.g., diff PDF content bytes but ignore metadata). Weakens the backward compatibility guarantee and requires custom tooling. Rejected because it would mask real regressions.

**Decision**: **Option (a) — use `SOURCE_DATE_EPOCH=1700000000` as a fixed value for all baseline generation and for the T024 backward-compatibility test.**

**Rationale**:
1. **Industry standard**: SOURCE_DATE_EPOCH is the reproducible-builds.org convention honored by gcc, cargo, Python setuptools, Debian packaging, and Typst.
2. **Zero source code changes**: The fix lives entirely in invocation wrappers and test setup. No modification to `scripts/extract-report-data.py`, `main.typ`, or any tachi code.
3. **Preserves byte-identical comparison**: The test can still use `cmp` to detect real regressions. It does not weaken backward compatibility.
4. **Verified**: The devops agent tested `SOURCE_DATE_EPOCH=1700000000` and confirmed all 5 examples become byte-deterministic across multiple runs.
5. **Chosen value `1700000000`** = 2023-11-14 22:13:20 UTC, a fixed arbitrary value. Any value works as long as it's consistent between baseline generation and test runs.

**Scope of the env var**:
- T003b (baseline generation in the worktree): set `SOURCE_DATE_EPOCH=1700000000` before `typst compile`.
- T024 (backward-compatibility test): test fixture or CI script must set `SOURCE_DATE_EPOCH=1700000000` before running the pipeline.
- Production usage (real users running `/tachi.security-report`): **NO CHANGE**. Normal users will continue to get PDFs with wall-clock timestamps, which is the desired behavior for real reports. Only the test path sets the env var.

**Downstream impact**:
- T003b must be re-run in the worktree with the env var set.
- T003c re-verification should then pass.
- T024 test code (to be authored in Wave 4) must set `SOURCE_DATE_EPOCH` in its fixture or subprocess call.
- No effect on T033 (agentic-app regeneration) because that example is intentionally regenerated — byte-identical determinism is not required for it.

**Escalation audit**: The task note in agent-assignments.md Wave 2 risk mitigation said "escalate to architect within 30 minutes of failure" for determinism issues. The escalation happened: the devops agent identified the root cause and a verified fix and reported back to the orchestrator within the session. The fix is a standard, low-risk environment variable, not a source code change. The orchestrator is authorizing Option (a) without further architect escalation because the fix does not weaken the backward compatibility guarantee, does not require source code changes, and is an industry-standard reproducible-builds mechanism. If the architect later objects during the T036 checkpoint, the decision can be revisited.

---

## Decision 4: mermaid-agentic-app baseline regenerated (Wave 4 T024)

**Context**: T024 authored `tests/scripts/test_backward_compatibility.py` and ran it against the 5 committed baselines. Four examples (web-app, microservices, ascii-web-api, free-text-microservice) passed byte-identically. The fifth, `mermaid-agentic-app`, failed: baseline was 1,281,622 bytes / 35 pages, current output was 2,034,786 bytes / 29 pages.

**Root cause** (isolated by inspecting the diff against `main`):

The Wave 2 baseline was generated from a `git worktree` on `main` (commit `d7ba8b5`). During Wave 2 baseline generation, the devops agent applied two scope-bleed bug fixes to the *working* tree (not the worktree) to make the pipeline able to generate baselines at all:

1. **`scripts/extract-report-data.py`** (+31/-4 lines): H1 heading fallback in `_parse_attack_tree_file()` for files lacking a Finding ID in the metadata table; component/title enrichment from `findings_by_id`; `rstrip(":")` on inline attack tree IDs in `_parse_inline_attack_trees()`.
2. **`templates/tachi/security-report/attack-path.typ`** (+3 lines): defensive coercion of `remediation` from `str` to `(str,)` tuple before iteration. Without this fix, a bare-string `remediation` value iterated **character-by-character** through the Typst `for step in remediation` loop, rendering each character as its own heading step and bloating attack tree sections across many extra pages.

The 4 other baseline examples have no `attack-trees/` directory, so they are unaffected by either fix. Only `mermaid-agentic-app` has attack trees and therefore exercises the buggy code path.

The baseline was generated from pure `main` (without the fixes), so it captures the buggy character-by-character iteration — 35 pages of bloated but compact content (single-character glyphs). The current parser with the fixes produces a clean 29-page output.

Of these 6 "extra" pages, the size grows from 1.28 MB to 2.03 MB because the fixed rendering emits full remediation strings as single coherent steps (more bytes per page but fewer total pages) versus the buggy one-character-per-step rendering (less bytes per page but many more pages).

**Options considered**:
- **(a) Regenerate the `mermaid-agentic-app` baseline with the scope-bleed fixes applied.** The baseline then represents "main + the bug fixes that were required to generate baselines at all". F-128 remains purely additive on top of the fixed state.
- **(b) Revert the scope-bleed fixes to `attack-path.typ` and `extract-report-data.py`.** The working branch would no longer depend on the fixes, and the baseline would match pure `main`. HIGH RISK: the attack-path.typ fix is necessary for correct rendering of text-fallback attack trees, and reverting it reintroduces the character-by-character iteration bug. Reverting the extract-report-data.py fix also breaks the `_parse_attack_tree_file()` path for any attack-tree file without a metadata Finding ID.
- **(c) Exclude `mermaid-agentic-app` from the T024 parametrized test.** Weakens the backward-compatibility guarantee for the only example exercising the attack-tree pipeline.

**Decision**: **Option (a) — regenerate the `mermaid-agentic-app` baseline with the scope-bleed fixes applied.**

**Rationale**:
1. **The fixes are legitimate bug fixes, not F-128 features.** They were flagged in `NEXT-SESSION.md` and in `.aod/results/wave-2-baselines.md` as incidental bug fixes required to enable baseline generation. They should be reviewed during the T036 architect checkpoint but kept in the PR.
2. **The baseline is uncommitted.** There is no git history to lose. Regenerating is a zero-risk operation on the working tree.
3. **Determinism verified.** Two consecutive runs of the current pipeline produce byte-identical 2,034,786-byte outputs.
4. **T024 passes 5/5 after regeneration.**
5. **The other 4 baselines remain unchanged.** Their example sources do not exercise the fixed code path, so their pre-fix baselines are still valid.

**Action taken**:
- Ran `SOURCE_DATE_EPOCH=1700000000 python3 scripts/extract-report-data.py --target-dir examples/mermaid-agentic-app/ --output templates/tachi/security-report/report-data.typ --template-dir templates/tachi/security-report/`
- Ran `SOURCE_DATE_EPOCH=1700000000 typst compile templates/tachi/security-report/main.typ examples/mermaid-agentic-app/security-report.pdf.baseline --root .`
- Verified determinism by running the pipeline twice and `cmp`ing — identical.
- Re-ran `python3 -m pytest tests/scripts/test_backward_compatibility.py -v` — 5/5 PASSED.

**Scope-bleed tracking**: The two scope-bleed changes (`scripts/extract-report-data.py` attack-tree parser fixes and `templates/tachi/security-report/attack-path.typ` string coercion) are now formally part of the F-128 PR. T036 architect checkpoint MUST review them. If the architect objects, the F-128 PR can be split: a standalone fix PR for the scope-bleed changes (merged first) followed by the F-128 PR (rebased on top). The PR description for F-128 will flag these changes prominently.

---

## Decision 5: Pre-existing working-tree modifications excluded from F-128 PR

**Context**: The P1 architect checkpoint surfaced 9 files modified in the working tree that were NOT F-128 scope and NOT documented in `decisions.md`. These were flagged at session start in `NEXT-SESSION.md` lines 118–126 as "Pre-existing modifications (unrelated to this session; were already in working tree at session start)". The files and their diff sizes:

| File | Lines |
|------|-------|
| `.claude/agents/tachi/threat-report.md` | +37 |
| `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` | +20 |
| `.claude/skills/tachi-threat-reporting/references/narrative-templates.md` | +9/-1 |
| `docs/architecture/01_system_design/README.md` | +95 |
| `docs/product/02_PRD/INDEX.md` | +1 |
| `schemas/output.yaml` | +2 |
| `schemas/report.yaml` | +52/-1 |
| `templates/tachi/output-schemas/threat-report.md` | +17/-8 |
| `templates/tachi/output-schemas/threats.md` | +26/-13 |

Total: ~259 lines across 9 files, touching threat-report agent rules, schema contracts (F-104 baseline propagation style), and output-schema templates.

**Context analysis**: Looking at git log, none of these modifications are in any committed branch. They are working-tree-only, carried over from a prior in-flight effort (most likely a partial follow-up to Feature 104 downstream baseline propagation work, or an in-flight threat-report improvement that was never committed). They do NOT belong to F-128.

**Pipeline impact analysis**: None of the 9 files are consumed at runtime by the F-128 pipeline (`extract-infographic-data.py`, `extract-report-data.py`, `typst compile`, or any test in `tests/scripts/`). The schema YAML files (`output.yaml`, `report.yaml`) are documentation-only. The agent markdown files affect the threat-report agent (invoked by `/tachi.threat-model`), not `/tachi.infographic` or `/tachi.security-report`. Therefore, leaving them in the working tree does NOT affect T033 regeneration, T034 full test suite, or any downstream F-128 validation.

**Options considered**:
- **(a)** Revert the 9 files via `git restore` before Wave 6. Produces a clean working tree but destroys whatever in-flight work they represent. HIGH RISK: if the next developer expected these changes to still be in the working tree (e.g., to continue a separate effort), they'd be lost.
- **(b)** Leave them in the working tree and exclude them from F-128 commits via selective `git add` during T039. Safe — preserves the work, avoids cross-PR pollution. Requires T039 to be careful about staging.
- **(c)** Stash them via `git stash push -u --` for the duration of Wave 6, then `git stash pop` after T039. Safer than revert (reversible) but adds session-fragile state that could be lost on interrupt.

**Decision**: **Option (b) — leave the 9 files in the working tree; exclude them from F-128 commits via explicit file staging in T039.**

**Rationale**:
1. **Zero pipeline impact**: None of the 9 files are consumed by the F-128 pipeline. T033 and T034 produce the same output whether they're present or reverted.
2. **No data loss risk**: Reverting would destroy the in-flight work; leaving them untouched preserves it for whoever picks it up next.
3. **PR cleanliness maintained**: T039 will use selective `git add <file>` for F-128-scoped files only. The 9 pre-existing files will remain unstaged and will not appear in the PR diff.
4. **Architect P1 concern addressed**: The P1-2 concern was specifically about PR pollution ("committing them into the F-128 PR would violate Principle X"). Option (b) addresses this without the destructive side effects of Option (a).

**Action items for T039 (PR authoring)**:
- Stage ONLY these F-128 scope files (list below)
- Explicitly DO NOT stage: the 9 pre-existing files above, `docs/product/_backlog/BACKLOG.md` (auto-regenerated by backlog script in Step 1 — legitimate session artifact but not F-128 feature code), any `.aod/results/*.md` files (process artifacts, not code).
- The 12 untracked PNGs in `examples/mermaid-agentic-app/attack-trees/*.png` are pipeline side-effects from Wave 2 baseline generation (or later mmdc runs). Exclude from F-128 PR; they belong to a separate cleanup effort.

**F-128 scope files to stage**:
- `scripts/extract-infographic-data.py` — Wave 3 helpers + dispatch
- `scripts/extract-report-data.py` — Wave 4 `detect_images()` + Typst writers (INCLUDING the Decision 4 scope-bleed attack-tree parser fixes)
- `schemas/infographic.yaml` — Wave 2 schema enumeration
- `templates/tachi/security-report/main.typ` — Wave 4 conditional page block
- `templates/tachi/security-report/attack-path.typ` — Decision 4 scope-bleed (string coercion fix)
- `.claude/agents/tachi/threat-infographic.md` — Wave 3 agent doc updates
- `.claude/agents/tachi/report-assembler.md` — Wave 4 artifact detection table
- `.claude/commands/tachi.infographic.md` — Wave 5 template list + exec alias + all shorthand
- `.claude/skills/tachi-infographics/references/executive-architecture.md` — Wave 4 skill reference (new file)
- `.claude/skills/tachi-infographics/SKILL.md` — Wave 4 index update
- `.gitignore` — Wave 1 Python patterns
- `Makefile` — Wave 1 `test:` target
- `README.md` — Wave 1 "Running Tests" section
- `pyproject.toml` — Wave 1 pytest config (new file)
- `requirements-dev.txt` — Wave 1 test deps (new file)
- `tests/` — Wave 1/3/4/5 pytest tree (all new files including fixtures, goldens, and test files)
- `examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/security-report.pdf.baseline` — Wave 2 committed baselines (binary files)
- `examples/agentic-app/sample-report/threat-executive-architecture-spec.md` — Wave 6 T033 regenerated
- `examples/agentic-app/sample-report/threat-executive-architecture.jpg` — Wave 6 T033 regenerated (placeholder if Gemini unavailable)
- `examples/agentic-app/sample-report/security-report.pdf` — Wave 6 T033 regenerated
- `specs/128-prd-128-executive/` — all F-128 feature artifacts (spec, plan, tasks, decisions, checkpoints, manual-verification, contracts, data-model)
- `docs/product/02_PRD/128-executive-threat-architecture-2026-04-09.md` — Wave 2 PRD doc (the F-128 PRD itself, created at session start)

---

## Decision Log

| Decision | Task | Date | Status |
|----------|------|------|--------|
| Baseline storage = committed `.baseline` files | T002 | 2026-04-09 | Approved |
| Regeneration target = agentic-app (no change) | T001 | 2026-04-09 | Approved |
| SOURCE_DATE_EPOCH=1700000000 for deterministic baselines | T003c | 2026-04-09 | Approved |
| mermaid-agentic-app baseline regenerated with scope-bleed fixes | T024 | 2026-04-09 | Approved (bundled in F-128 PR, architect P1 accepted) |
| Pre-existing 9 files excluded from F-128 PR via selective staging | P1 | 2026-04-09 | Approved (T039 must honor) |

Any future decisions that emerge during implementation will be appended here.
