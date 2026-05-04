# Research Summary: Issue #250 Hot-Fix — Adversarial Unit Extraction

**Date**: 2026-05-04
**Spec**: `specs/250-adversarial-unit-extraction-hotfix/spec.md`
**PRD**: `docs/product/02_PRD/250-adversarial-unit-extraction-hotfix-2026-05-04.md`

This research grounds the spec in the codebase, KB lessons, architecture constraints, and external best practices. Findings below were gathered via four parallel Explore/web/general-purpose agents on 2026-05-04.

---

## Knowledge Base Findings

**Sole KB entry** lives in `docs/INSTITUTIONAL_KNOWLEDGE.md` (Entry 1, written 2026-05-04 from F-248 retrospective). The PRD's hot-fix is the explicitly named follow-up.

Key principles applicable to this spec:

- **Performance corollary** (line 69): *"when a test invokes a heavy mechanism per parametrized case, ask if a unit-level test against the underlying function can prove the same invariant. F-248's 14 adversarial init.sh runs collapse to ~14 unit-test invocations."* — directly authorizes the extraction.
- **Symmetric-scope pattern** (line 67): tests must walk the same category as the runtime invariant they protect; do not over-scope defensively.
- **Spec language tightening** (line 71): anchor scope in named manifest categories, not vague phrases.

**macos-latest CI timeout history**: single documented incident — CI run `25314246672` (commit `219dfee`, F-248 closing run) timed out at 300s on first init.sh invocation. Classified as runner-perf flake, not regression. Closure used admin-override squash-merge.

**No prior pytest+subprocess shell-helper pattern** exists in the repo — F-250 establishes it.

**Reference**: `specs/248-substitution-surface-hardening/delivery.md` retrospective (lines 91-93 "Surprise Log") names the 17-init.sh-runs-too-many flake; "Next Steps" item 1 schedules this hot-fix.

---

## Codebase Analysis

| Item | Finding |
|------|---------|
| `tests/scripts/test_init_sh_adversarial.py` | 289 lines total. Extract block: lines 41-162 (ADVERSARIAL_CASES table + `_ids` + `adversarial_run` fixture + `test_adversarial_input`). Preserve: lines 1-39 (imports/header), 165-227 (case 13), 229-288 (`test_no_residual_placeholders_after_init`). |
| `aod_template_substitute_placeholders` | `.aod/scripts/bash/template-substitute.sh` — exists; `shopt -u patsub_replacement 2>/dev/null \|\| true` shim **present and active at line 64** (load-bearing per AC-5). |
| `aod_init_read_validated` | `.aod/scripts/bash/init-input.sh` — exists, full contract from line 88. Uses `printf -v "$var_name"` (caller-scope write — pipe-subshell trap risk, R-1). |
| `tests/scripts/init_sh_helpers.py` | 228 lines, 7 public functions: `clone_into_tmpdir`, `run_init_in_clone`, `build_canonical_stdin`, `discover_pack_count`, `files_in_tree`, `cleanup`, plus `InitRun` dataclass. Module docstring states it is not collected as a test module. New unit modules MUST NOT import from it (AC-4). |
| `pyproject.toml` pytest config | `testpaths=["tests"]`, `python_files=["test_*.py"]`, `python_functions=["test_*"]`, `addopts="-ra --strict-markers"`, `markers=["slow: ..."]`. |
| `tests/scripts/conftest.py` | 93 lines — defines `schema` and `id_pattern` fixtures + helpers; no init.sh-specific fixtures. |
| Other init.sh-invoking tests | `test_init_sh_constitution.py` (1), `test_init_sh_self_delete.py` (1 shared fixture), `test_init_sh_substitution.py` (1). After hot-fix: 5 invocations remain (4 unchanged + case 13 in adversarial.py). |

**Naming convention to follow**: `tests/scripts/test_template_substitute_unit.py` (8 cases) and `tests/scripts/test_init_input_unit.py` (4 cases) — matches existing `test_*.py` pattern.

---

## Architecture Constraints

**Source**: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`, `pyproject.toml`, `.github/workflows/tachi-pytest.yml`, `docs/standards/DEFINITION_OF_DONE.md`.

| Constraint | Value |
|------------|-------|
| Python | `>=3.9` declared; CI pins 3.11 |
| pytest | `>=8.0` |
| bash compatibility floor | 3.2.57 (macOS gate); no bash 4+ features |
| Process substitution `< <(...)` | bash 2.04+ — **safe** |
| `printf -v` | bash 3.1+ — **safe** |
| `shopt -u patsub_replacement` | bash 5.2+ only — already guarded with `2>/dev/null \|\| true` |
| CI matrix | `[macos-latest, ubuntu-latest]` — both must be green |
| Outer pytest timeout | `--timeout=360` (current) |
| Inner subprocess timeout | 300s |
| Naming | `test_*.py` (enforced) |

**ADR-038 bearing**:
- D-1: Bash parameter expansion `${content//\{\{KEY\}\}/value}` — literal replacement, byte-literal, locale-independent.
- D-5: Validation triplet pattern (regex-validate → reject → `printf -v` safe assignment) — the contract `aod_init_read_validated` exposes.
- D-6: Residual-placeholder scan on PERSONALIZED-category files only.

**ADR-038 §Test Coverage** itemizes the 8 metachar + 4 input-rejection + 1 file-identity adversarial case set this hot-fix is splitting.

---

## Industry Research

**Source**: Greg's Wiki BashFAQ/024, GNU Bash Reference Manual, pytest documentation.

1. **Process substitution is the canonical fix** for caller-scope writes from a piped function. `< <(producer)` keeps the consumer in the parent shell so `printf -v` lands.
2. **`subprocess.run(["bash", "-c", "set -euo pipefail; source helper.sh; helper_func args"], capture_output=True, text=True, env={...}, timeout=10, check=False)`** is the standard pattern. Pitfalls:
   - Avoid `check=True` when asserting on exit codes
   - Pin `env={"LC_ALL": "C", "PATH": os.environ["PATH"]}` for determinism (matches `init_sh_helpers.run_init_in_clone` line 137 baseline)
   - Use `text=True`
   - Capture stderr separately from stdout
   - Avoid `shell=True`
3. **bash 3.2 vs 5.x**: process substitution and `printf -v` both safe. Guard `shopt -u patsub_replacement` with `2>/dev/null || true` (already done in `template-substitute.sh:64`).
4. **Pytest parametrize patterns**:
   - Use explicit human-readable `ids=[...]` for grep/`-k` filtering
   - Set `timeout=` per-call on `subprocess.run`, not via pytest-timeout, so `TimeoutExpired` is assertable
   - Pin `env=` per-call (don't mutate `os.environ` via fixtures) — keeps tests parallel-safe
   - Defer subprocess creation to test body, not parametrize values

**Sources**:
- https://mywiki.wooledge.org/BashFAQ/024
- https://www.gnu.org/software/bash/manual/html_node/Process-Substitution.html
- https://docs.pytest.org/en/stable/example/parametrize.html

---

## Recommendations for Spec

The PRD is unusually specific (architect baseline embedded verbatim). The spec inherits its constraints rather than re-deriving them. Spec recommendations:

1. **User stories** mirror the two PRD personas (US-1 adopter, US-2 maintainer) and stay technology-agnostic — describe the value, not the bash mechanics.
2. **Functional requirements** focus on the *outcomes* the hot-fix delivers (CI completes inside the standard window, regression detection preserved, helper-scoped failure traces) rather than the implementation details (which are PRD/plan/tasks scope).
3. **Acceptance criteria** restate the PRD's AC-1..AC-8 in Given/When/Then form so they are independently testable in CI.
4. **Edge cases** highlight the load-bearing invariants:
   - Pipe-subshell trap (R-1) — silent false-pass risk
   - Locale drift (R-4) — case 6 multibyte UTF-8
   - Future helper-invocation drift (R-5) — backstopped by case 13 + Test-1
5. **Success criteria** mirror PRD §Success Metrics table — quantitative thresholds only, no implementation framing.
6. **Key entities** are *test modules* and the *helper functions they exercise*, named at the contract layer (no internal mechanism).
7. **Scope guardrails** — explicit non-goals carried from PRD (Path C, session fixtures, synthetic 5-file tree).
8. **Open questions** — resolve OQ-1 (clean delete) and OQ-2 (`fix(250):` prefix) inline per PRD PM stance; flag TC-1..TC-4 as tasks.md-level concerns.

No `[NEEDS CLARIFICATION]` markers required — the PRD's three-Triad-sign-off depth resolves all open questions.
