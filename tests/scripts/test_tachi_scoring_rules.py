"""Tests for ``scripts/tachi_scoring_rules.py``, parts 1 and 2 (F-374 T042 and T043; ADR-050 D2, D5, D9 and D10).

Part 1 holds R-6's baseline resolver, R-26's tolerant reader and S-13's one tag source, which the renderer's
whole-file render (T028) and the scorer's planner (T044) need first. Part 2 (T043) holds R-25's asset outcome, D10's
vector check, R-31's routing, peers, overrides and scoring date, and ruling A's tag-driven band rule. Lane R1t's
T041 adds the golden-level cases to
``test_render_risk_scores.py``; these are the direct unit cases for the functions themselves, so the slice is
proven before the renderer exists.

The module is a helper, so the tests import it; there is no entry to drive. Every fixture here is synthetic,
except two read-only inputs that exist to prove the reader on real v4.48.4 output: the committed baseline
under ``tests/scripts/fixtures/large_arch/`` and the shipped ``examples/*/risk-scores.md`` files. Those are
only read, so no extractor or renderer runs and no tracked file changes.

Sections
--------
1. Module hygiene and the frozen signatures
2. ``check_run_file`` (R-6, NFR-10)
3. ``resolve_baseline`` (R-6)
4. ``read_baseline_scores``: the file, and the legacy forms
5. ``read_baseline_scores``: the renderer's Scoring Inputs, and decoding
6. ``read_baseline_scores``: the SARIF fallback and the unreadable cases
7. ``recompute_tags`` and ``select_tag_source`` (S-13)
8. ``asset_outcome`` and ``cvss_chain`` (R-25, D10)
9. ``check_carried_vector`` (D10, ruling A)
10. ``route_scorer_units`` and ``peer_divergence`` (R-31, D8's groups through ``parse_correlation_groups``)
11. ``original_scoring_date``, ``classify_band_change`` and ``governance_for`` (R-5, R-31, ruling A)

The decoder is the shipped one, ``tachi_parsers.decode_references`` (T033): the round-trip cases write a value
with ``tachi_parts.escape_cell`` and read it back through the reader, so they pin the two halves together.

Standard library and pytest only, and Python 3.9 syntax.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import os
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
MODULE = SCRIPTS_DIR / "tachi_scoring_rules.py"
FIXTURES = REPO_ROOT / "tests" / "scripts" / "fixtures" / "large_arch"
EXAMPLES = REPO_ROOT / "examples"

_keep_bytecode_flag = sys.dont_write_bytecode
sys.dont_write_bytecode = True  # a .pyc under scripts/ would dirty the tree under test (ADR-049 D8)
sys.path.insert(0, str(SCRIPTS_DIR))
try:
    import tachi_parsers  # noqa: E402  -- after the path change, by design
    import tachi_parts  # noqa: E402
    import tachi_scoring_rules as rules  # noqa: E402
finally:
    sys.dont_write_bytecode = _keep_bytecode_flag

D = Decimal

def _symlink(target, link):
    try:
        os.symlink(str(target), str(link))
    except (OSError, NotImplementedError):  # pragma: no cover  (a platform without symlinks)
        pytest.skip("this platform cannot create a symlink")


# =============================================================================
# 1. Module hygiene and the frozen signatures
# =============================================================================

ALLOWED_IMPORTS = {
    "__future__", "json", "os", "re", "stat", "sys", "dataclasses", "datetime", "decimal", "pathlib", "typing",
    "tachi_parsers", "tachi_parts", "tachi_scoring",
}


def _tree():
    return ast.parse(MODULE.read_text(encoding="utf-8"), filename=str(MODULE))


def test_module_parses_with_the_python_39_grammar_and_opens_with_the_future_import():
    source = MODULE.read_text(encoding="utf-8")
    ast.parse(source, filename=str(MODULE), feature_version=(3, 9))
    body = [node for node in _tree().body if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))]
    assert isinstance(body[0], ast.ImportFrom) and body[0].module == "__future__"
    assert [alias.name for alias in body[0].names] == ["annotations"]


def test_module_imports_only_the_standard_library_and_the_three_helpers_at_module_level():
    """D5: it never imports ``sarif_common``, an entry script or ``yaml``. A function-level import would hide
    a dependency from F-373's S-13 import gate and ``_import_closure``, so every import is a top-level statement."""
    tree = _tree()
    toplevel = {id(node) for node in tree.body}
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        assert id(node) in toplevel, "an import inside a function or a block at line %d" % node.lineno
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        else:
            names.add(node.module.split(".")[0])
    assert names <= ALLOWED_IMPORTS, sorted(names - ALLOWED_IMPORTS)
    assert {"tachi_parsers", "tachi_parts", "tachi_scoring"} <= names


def test_module_turns_bytecode_off_before_its_local_imports():
    tree = _tree()
    setting, first_local = None, None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "attr", "") == "dont_write_bytecode" for t in node.targets):
            setting = node.lineno
        if isinstance(node, ast.Import) and node.names[0].name.startswith("tachi_") and first_local is None:
            first_local = node.lineno
    assert setting is not None and first_local is not None and setting < first_local


def test_module_reads_no_clock():
    """No function reads the clock, so every date is a parameter (D5; module-signatures.md)."""
    source = MODULE.read_text(encoding="utf-8")
    for needle in (".now(", ".today(", "time.time", "utcnow", "perf_counter"):
        assert needle not in source, needle


def _fields(cls):
    return tuple(f.name for f in dataclasses.fields(cls))


def test_the_frozen_dataclasses_keep_their_field_names_and_order():
    """A rename, removal or reorder needs an architect amendment (contracts/module-signatures.md, "The freeze")."""
    assert _fields(rules.PathCheck) == ("path", "reason")
    assert _fields(rules.InputIssue) == ("finding_id", "field", "cause", "detail")
    assert _fields(rules.TagSource) == ("source", "tags", "warning", "cause")
    assert _fields(rules.BaselineScores) == (
        "readable", "reason", "form", "rows", "resolved_rows", "ids_in_any_row", "frontmatter_date", "issues")
    assert _fields(rules.BaselineRow) == (
        "finding_id", "form", "cvss_vector", "vector_source", "score_bounds", "subscores", "zone", "trust_level",
        "auth_barriers", "network_boundaries", "tags_used", "scored_on", "stored", "band", "owner", "sla",
        "disposition", "review_date", "narrative", "legacy_prose", "flags")
    # BaselineResolution keeps its four frozen fields first. `file_reasons` is T042's additive field (a default, last).
    assert _fields(rules.BaselineResolution)[:4] == ("run_dir", "origin", "files", "reason")
    assert _fields(rules.BaselineResolution)[4:] == ("file_reasons",)


@pytest.mark.parametrize("cls", [rules.PathCheck, rules.BaselineResolution, rules.InputIssue, rules.BaselineRow,
                                 rules.BaselineScores, rules.TagSource])
def test_the_dataclasses_are_frozen(cls):
    assert cls.__dataclass_params__.frozen


def _signature(function):
    return [(p.name, p.kind.name, p.default is inspect.Parameter.empty) for p in inspect.signature(function).parameters.values()]


def test_the_frozen_function_signatures_hold():
    keyword = "KEYWORD_ONLY"
    assert _signature(rules.check_run_file) == [("candidate", "POSITIONAL_OR_KEYWORD", True), ("cwd", keyword, True), ("expected_name", keyword, True)]
    assert _signature(rules.resolve_baseline) == [("flag", keyword, True), ("baseline_source", keyword, True), ("cwd", keyword, True)]
    assert _signature(rules.read_baseline_scores) == [("md_path", "POSITIONAL_OR_KEYWORD", True), ("sarif_path", keyword, False)]
    assert _signature(rules.recompute_tags) == [("architecture_text", "POSITIONAL_OR_KEYWORD", True), ("open_rows", "POSITIONAL_OR_KEYWORD", True), ("matcher", "POSITIONAL_OR_KEYWORD", True)]
    assert _signature(rules.select_tag_source) == [("open_ids", keyword, True), ("block", keyword, True), ("recomputed", keyword, True)]
    assert rules.BASELINE_FILE_NAMES == ("threats.md", "risk-scores.md", "risk-scores.sarif",
                                         "compensating-controls.md", "compensating-controls.sarif")


# =============================================================================
# 2. check_run_file (R-6, NFR-10)
# =============================================================================

@pytest.fixture
def project(tmp_path):
    """A working directory with one baseline run directory in it, and a sibling directory outside it."""
    root = tmp_path / "proj"
    run = root / "baseline-runs" / "2026-09-21"
    run.mkdir(parents=True)
    for name in ("threats.md", "risk-scores.md", "risk-scores.sarif"):
        (run / name).write_text("x\n", encoding="utf-8")
    (tmp_path / "elsewhere").mkdir()
    (tmp_path / "elsewhere" / "threats.md").write_text("x\n", encoding="utf-8")
    return root


def _check(project, candidate, name="threats.md"):
    return rules.check_run_file(candidate, cwd=project, expected_name=name)


def test_a_regular_file_with_its_name_under_the_working_directory_passes(project):
    run = project / "baseline-runs" / "2026-09-21"
    for candidate in ("baseline-runs/2026-09-21/threats.md", "./baseline-runs//2026-09-21/./threats.md", str(run / "threats.md")):
        checked = _check(project, candidate)
        assert checked.reason is None, candidate
        assert checked.path is not None and os.path.samefile(str(checked.path), str(run / "threats.md"))
        assert checked.path.is_absolute()


@pytest.mark.parametrize("candidate", [None, "", "   ", "\t\n"])
def test_nothing_given_is_absent(project, candidate):
    assert _check(project, candidate) == rules.PathCheck(None, "absent")


@pytest.mark.parametrize("candidate", [
    "none (first run \u2014 stateless mode)",   # the shipped consumer-agent-app's baseline.source
    "none", "first run", "baseline: none", "https://example.com/threats.md",
    "C:\\runs\\threats.md", "runs\\threats.md", "back`tick/threats.md", "a\x00b/threats.md", "a/" * 3000 + "threats.md",
])
def test_free_text_and_unusable_syntax_are_free_text(project, candidate):
    assert _check(project, candidate) == rules.PathCheck(None, "free-text")


def test_a_candidate_that_is_not_text_is_the_same_as_none_given(project):
    assert _check(project, 42).reason == "absent"


@pytest.mark.parametrize("candidate", ["baseline-runs/2026-09-21/risk-scores.md", "previous-run.md", ".", "./", "baseline-runs/2026-09-21/",
                                       "baseline-runs/2026-09-21/Threats.md", "baseline-runs/2026-09-21/threats.md.bak",
                                       "N/A"])  # a slash makes N/A path-shaped: a file called "A"
def test_a_file_with_another_name_is_the_wrong_name(project, candidate):
    assert _check(project, candidate).reason == "wrong-name"


@pytest.mark.parametrize("candidate", ["../elsewhere/threats.md", "baseline-runs/../../elsewhere/threats.md", ".."])
def test_a_parent_reference_is_outside_the_working_directory(project, candidate):
    assert _check(project, candidate).reason == "outside-working-directory"


def test_an_absolute_path_elsewhere_is_outside_the_working_directory(project, tmp_path):
    assert _check(project, str(tmp_path / "elsewhere" / "threats.md")).reason == "outside-working-directory"
    assert _check(project, "/nonexistent-root-374/run/threats.md").reason == "outside-working-directory"


def test_a_file_that_does_not_exist_is_missing(project):
    assert _check(project, "baseline-runs/2026-10-01/threats.md").reason == "missing"
    assert _check(project, "baseline-runs/2026-09-21/compensating-controls.md", "compensating-controls.md").reason == "missing"


def test_a_directory_with_the_expected_name_is_not_a_regular_file(project):
    (project / "odd" / "threats.md").mkdir(parents=True)
    assert _check(project, "odd/threats.md").reason == "not-regular-file"


def test_a_symlink_anywhere_on_the_path_is_refused(project):
    run = project / "baseline-runs" / "2026-09-21"
    (project / "linked-threats").mkdir()
    _symlink(run / "threats.md", project / "linked-threats" / "threats.md")
    _symlink(project / "baseline-runs", project / "linked-dir")
    assert _check(project, "linked-threats/threats.md").reason == "symlink"   # the file is a link
    assert _check(project, "linked-dir/2026-09-21/threats.md").reason == "symlink"  # a directory above it is a link


def test_the_working_directory_itself_may_be_a_symlink(project, tmp_path):
    _symlink(project, tmp_path / "proj-link")
    checked = rules.check_run_file("baseline-runs/2026-09-21/threats.md", cwd=tmp_path / "proj-link", expected_name="threats.md")
    assert checked.reason is None, "only what lies below the working directory may not be a link"


def test_a_relative_candidate_means_the_working_directory_not_the_process_directory(project, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert _check(project, "baseline-runs/2026-09-21/threats.md").reason is None


def test_the_controls_planner_can_check_a_source_file_with_the_threats_name(project):
    """Controls reach ``threats.md`` through ``risk-scores.md``'s ``source_file``, under the same checks (D8, D9)."""
    assert _check(project, "baseline-runs/2026-09-21/threats.md", "threats.md").reason is None
    assert _check(project, "baseline-runs/2026-09-21/risk-scores.md", "threats.md").reason == "wrong-name"


# =============================================================================
# 3. resolve_baseline (R-6)
# =============================================================================

def _resolve(project, flag=None, source=None):
    return rules.resolve_baseline(flag=flag, baseline_source=source, cwd=project)


def test_baseline_source_gives_its_directory_and_the_files_that_pass(project):
    run = project / "baseline-runs" / "2026-09-21"
    resolution = _resolve(project, source="baseline-runs/2026-09-21/threats.md")
    assert resolution.origin == "baseline.source" and resolution.reason is None
    assert os.path.samefile(str(resolution.run_dir), str(run))
    assert set(resolution.files) == {"threats.md", "risk-scores.md", "risk-scores.sarif"}
    assert all(path.name == name for name, path in resolution.files.items())
    assert resolution.file_reasons == {"compensating-controls.md": "missing", "compensating-controls.sarif": "missing"}


def test_the_flag_comes_first_and_a_directory_is_its_own_run_directory(project):
    other = project / "baseline-runs" / "2026-10-01"
    other.mkdir()
    (other / "threats.md").write_text("x\n", encoding="utf-8")
    resolution = _resolve(project, flag="baseline-runs/2026-10-01", source="baseline-runs/2026-09-21/threats.md")
    assert resolution.origin == "flag"
    assert os.path.samefile(str(resolution.run_dir), str(other))
    assert set(resolution.files) == {"threats.md"}


def test_a_file_path_given_to_the_flag_counts_as_its_directory(project):
    run = project / "baseline-runs" / "2026-09-21"
    for flag in ("baseline-runs/2026-09-21/risk-scores.md", str(run / "threats.md")):
        resolution = _resolve(project, flag=flag)
        assert resolution.origin == "flag" and os.path.samefile(str(resolution.run_dir), str(run)), flag
        assert "risk-scores.md" in resolution.files


def test_the_flag_may_name_the_working_directory_itself(project):
    (project / "threats.md").write_text("x\n", encoding="utf-8")
    resolution = _resolve(project, flag=".")
    assert os.path.samefile(str(resolution.run_dir), str(project)) and set(resolution.files) == {"threats.md"}


def test_a_path_object_is_accepted_wherever_text_is(project):
    run = project / "baseline-runs" / "2026-09-21"
    assert _check(project, run / "threats.md").reason is None
    assert os.path.samefile(str(_resolve(project, flag=run).run_dir), str(run))
    assert _resolve(project, source=run / "threats.md").origin == "baseline.source"


def test_a_blank_flag_is_not_given_so_the_source_applies(project):
    assert _resolve(project, flag="  ", source="baseline-runs/2026-09-21/threats.md").origin == "baseline.source"


@pytest.mark.parametrize("flag,reason", [
    ("baseline-runs/none-here", "missing"),
    ("../elsewhere", "outside-working-directory"),
    ("https://example.com/run", "free-text"),
])
def test_a_flag_that_does_not_resolve_has_no_run_directory_and_a_reason(project, flag, reason):
    resolution = _resolve(project, flag=flag, source="baseline-runs/2026-09-21/threats.md")
    assert (resolution.run_dir, resolution.origin, resolution.reason, dict(resolution.files)) == (None, "flag", reason, {}), (
        "a failed flag does not fall back to baseline.source: the command named a baseline and it must be said")


def test_an_absolute_flag_outside_the_working_directory_is_refused(project, tmp_path):
    assert _resolve(project, flag=str(tmp_path / "elsewhere")).reason == "outside-working-directory"


@pytest.mark.parametrize("source,reason", [
    ("none (first run \u2014 stateless mode)", "free-text"),
    ("baseline-runs/2026-09-21/risk-scores.md", "wrong-name"),
    ("baseline-runs/2026-10-01/threats.md", "missing"),
    ("../elsewhere/threats.md", "outside-working-directory"),
])
def test_baseline_source_that_fails_means_a_fresh_score_with_the_reason(project, source, reason):
    resolution = _resolve(project, source=source)
    assert (resolution.run_dir, resolution.origin, resolution.reason, dict(resolution.files)) == (None, "baseline.source", reason, {})


def test_naming_nothing_is_a_first_run(project):
    assert _resolve(project) == rules.BaselineResolution(None, None, {}, "not-named")
    assert _resolve(project, source="   ").reason == "not-named"


def test_a_symlinked_file_in_the_run_directory_is_refused_and_reported(project):
    run = project / "baseline-runs" / "2026-09-21"
    (run / "risk-scores.sarif").unlink()
    _symlink(run / "risk-scores.md", run / "risk-scores.sarif")
    resolution = _resolve(project, flag="baseline-runs/2026-09-21")
    assert "risk-scores.sarif" not in resolution.files
    assert resolution.file_reasons["risk-scores.sarif"] == "symlink"
    assert "risk-scores.md" in resolution.files


def test_a_symlinked_run_directory_yields_no_usable_file(project):
    _symlink(project / "baseline-runs" / "2026-09-21", project / "run-link")
    resolution = _resolve(project, flag="run-link")
    assert resolution.run_dir is not None and dict(resolution.files) == {}
    assert set(resolution.file_reasons.values()) == {"symlink"}
    assert set(resolution.file_reasons) == set(rules.BASELINE_FILE_NAMES)


def test_a_directory_in_place_of_a_baseline_file_is_not_a_regular_file(project):
    run = project / "baseline-runs" / "2026-09-21"
    (run / "compensating-controls.md").mkdir()
    assert _resolve(project, flag="baseline-runs/2026-09-21").file_reasons["compensating-controls.md"] == "not-regular-file"


# =============================================================================
# 4. read_baseline_scores: the file, and the legacy forms
# =============================================================================

V1 = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L"
V2 = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L"
V3 = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L"

# The v4.48.4 form: `## N.` headings, a Source column, `### ID — component` subsections, the metric and sub-score
# tables with a rationale column, a Reachability paragraph, a peer with only a score line, and AGP-01's spelling.
V4484 = """---
schema_version: "1.0"
date: "2026-10-20"
source_file: "threats.md"
---

# Risk Scores Report

## 1. Executive Summary

**3** threats scored

---

## 2. Scored Threat Table

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| E-1 | fresh | gateway | Object identifiers are trusted | 9.1 | 7.0 | 8.5 | 7.0 | 8.0 | High | 7d | Mitigate |
| LLM-1 | fresh | gateway | History is replayed | 5.4 | 8.0 | 8.0 | 7.0 | 6.9 | Medium | 30d | Review |
| AGP-01 | fresh | worker | The bus is shared | 9.9 | 4.5 | 5.0 | 2.0 | 6.0 | Medium | 30d | Review |

---

## 3. Dimensional Breakdown

### E-1 \u2014 gateway

**Threat**: Object identifiers are trusted without an ownership check.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 8.0 (High)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `%(v1)s`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Scope (S) | Changed | Impact crosses a boundary |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

gateway sits in the Edge DMZ. The zone baseline is 6.5
and the refinement for this finding gives 7.0.

---

### LLM-1 \u2014 gateway

**Threat**: History is replayed.

**Correlation Group**: Scores inherited from primary finding E-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `%(v2)s`

---

## 4. Governance Fields

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| E-1 | High | alice | 14d | Accept | 2026-11-03 |
| LLM-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AGP-01 | Medium | Unassigned | 30d | Review | 2026-11-19 |

---

## 5. Scoring Methodology

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
""" % {"v1": V1, "v2": V2}

# A drift form shipped in tachi's samples: `## Section N:` headings, the Exploit, Scale, Reach and Disp aliases,
# `### ID: title` subsections, `**CVSS Vector**:` and a `**Scoring Rationale**:` list. S-2 has no vector.
DRIFT = """---
schema_version: "1.0"
date: "2026-04-16"
---

# Risk Scores

## Section 1: Executive Summary

**Total findings scored**: 2

## Section 2: Scored Threat Table

| ID | Component | Threat | CVSS | Exploit | Scale | Reach | Composite | Severity | SLA | Disp |
|----|-----------|--------|------|---------|-------|-------|-----------|----------|-----|------|
| **S-1** | Physician | Replay of credentials | 9.1 | 8.0 | 6.8 | 9.0 | 8.4 | High | 7d | Mitigate |
| S-2 | Patient | Identity spoofing | 7.5 | 6.8 | 6.3 | 9.0 | 7.4 | High | 7d | Mitigate |

## Section 3: Dimensional Breakdown

### S-1: Attacker may replay credentials

**Component**: Physician
**Composite Score**: 8.4 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 8.0 | 0.30 | 2.40 |

**CVSS Vector**: `%(v3)s`

**Scoring Rationale**:
- **CVSS**: Network replay with no authentication; scored 9.1.
- **Exploitability**: Well documented; scored 8.0.
- **Scalability**: Scriptable across accounts.
- **Reachability**: External entity in the Untrusted zone.

---

### S-2: Attacker may spoof a patient

**Component**: Patient

## Section 4: Governance Fields

Scoring date: 2026-04-16.

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|----|-----------|----------|-------|-----|-------------|-------------|
| S-1 | Physician | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| S-2 | Patient | High | R&D lead | 7d | Mitigate | 2026-04-23 |
""" % {"v3": V3}


def _write(tmp_path, text, name="risk-scores.md"):
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8") if isinstance(text, str) else text)
    return path


def _read(tmp_path, text, **kwargs):
    return rules.read_baseline_scores(_write(tmp_path, text), **kwargs)


def test_the_v4484_form_is_read_row_by_row(tmp_path):
    scores = _read(tmp_path, V4484)
    assert scores.readable and scores.reason is None and scores.form == "legacy"
    assert list(scores.rows) == ["E-1", "AGP-1", "LLM-1"], "canonical IDs, in S-2 order"
    assert scores.resolved_rows == {} and scores.issues == ()
    assert scores.frontmatter_date == date(2026, 10, 20)
    assert scores.ids_in_any_row == frozenset({"E-1", "LLM-1", "AGP-1"})

    row = scores.rows["E-1"]
    assert (row.finding_id, row.form, row.cvss_vector, row.vector_source) == ("E-1", "legacy", V1, "md")
    assert row.stored == {"cvss_base": D("9.1"), "exploitability": D("7.0"), "scalability": D("8.5"),
                          "reachability": D("7.0"), "composite": D("8.0")}
    assert all(isinstance(value, Decimal) for value in row.stored.values())
    assert (row.band, row.owner) == ("High", "alice")
    # §4 holds the human edits, so it outranks §2's default SLA and disposition columns.
    assert (row.sla, row.disposition, row.review_date) == ("14d", "Accept", date(2026, 11, 3))
    assert (row.zone, row.trust_level) == ("Edge DMZ", "Semi-Trusted")
    assert (row.subscores, row.score_bounds, row.tags_used, row.scored_on, row.auth_barriers, row.network_boundaries) == (None,) * 6
    assert row.narrative == {} and row.flags == ()


def test_the_legacy_prose_comes_back_as_text_by_field_name(tmp_path):
    prose = _read(tmp_path, V4484).rows["E-1"].legacy_prose
    assert prose == {
        "metric_rationale.AV": "Reachable over the network",
        "metric_rationale.S": "Impact crosses a boundary",
        "subscore_rationale.known_techniques": "Documented and widely used",
        "subscore_rationale.attack_complexity": "Needs some preparation",
        "subscore_rationale.scriptability": "Fully automatable",
        "rationale.reachability": "gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.",
    }
    assert all(set(name.split(".")[0:1]) <= {"rationale", "metric_rationale", "subscore_rationale"} for name in prose)
    assert all(name in tachi_parts.NARRATIVE_FIELDS for name in prose), "the renderer's own field names"


def test_a_peer_with_only_a_score_line_has_its_vector_and_a_row_without_a_section_3(tmp_path):
    scores = _read(tmp_path, V4484)
    assert scores.rows["LLM-1"].cvss_vector == V2 and scores.rows["LLM-1"].legacy_prose == {}
    assert scores.rows["AGP-1"].cvss_vector is None and scores.rows["AGP-1"].vector_source is None, "no §3 subsection, no SARIF"


def test_the_drift_form_is_read_through_its_aliases_and_labels(tmp_path):
    scores = _read(tmp_path, DRIFT)
    assert list(scores.rows) == ["S-1", "S-2"] and scores.issues == ()
    row = scores.rows["S-1"]
    assert row.cvss_vector == V3 and row.vector_source == "md"
    assert row.stored["exploitability"] == D("8.0") and row.stored["scalability"] == D("6.8") and row.stored["reachability"] == D("9.0")
    assert (row.sla, row.disposition, row.band, row.review_date) == ("7d", "Mitigate", "High", date(2026, 4, 23))
    assert row.legacy_prose == {
        "rationale.cvss": "Network replay with no authentication; scored 9.1.",
        "rationale.exploitability": "Well documented; scored 8.0.",
        "rationale.scalability": "Scriptable across accounts.",
        "rationale.reachability": "External entity in the Untrusted zone.",
    }
    assert scores.rows["S-2"].cvss_vector is None, "a row with no vector is kept: it is `unverifiable` later (R-7)"
    assert scores.rows["S-2"].owner == "R&D lead"


@pytest.mark.parametrize("heading", ["## 2. Scored Threat Table", "## Section 2: Scored Threat Table", "## SECTION 2 \u2014 Scored Threat Table"])
def test_both_heading_forms_find_the_scored_table(tmp_path, heading):
    text = V4484.replace("## 2. Scored Threat Table", heading)
    assert list(_read(tmp_path, text).rows) == ["E-1", "AGP-1", "LLM-1"]


def test_a_vector_label_may_put_its_colon_inside_the_bold(tmp_path):
    text = V4484.replace("**Vector**: `%s`" % V2, "**Vector:** `%s`" % V2)
    assert _read(tmp_path, text).rows["LLM-1"].cvss_vector == V2


def test_an_id_cell_that_is_not_one_finding_id_yields_no_row_but_an_issue(tmp_path):
    text = V4484.replace("| LLM-1 | fresh |", "| R-1..R-7 | fresh |").replace("| AGP-01 | fresh |", "| LLM-3, LLM-4 | fresh |")
    scores = _read(tmp_path, text)
    assert list(scores.rows) == ["E-1"]
    causes = [(issue.finding_id, issue.field, issue.cause) for issue in scores.issues if "Section 2" in issue.detail]
    assert causes == [(None, "id", "not-a-finding-id")] * 2
    assert "'R-1..R-7'" in scores.issues[0].detail


def test_placeholder_id_cells_are_dropped_silently(tmp_path):
    text = V4484.replace("| LLM-1 | fresh |", "| \u2014 | fresh |")
    scores = _read(tmp_path, text)
    assert list(scores.rows) == ["E-1", "AGP-1"] and not [i for i in scores.issues if "Section 2" in i.detail]


def test_a_repeated_id_keeps_the_first_row_and_two_spellings_are_one_id(tmp_path):
    text = V4484.replace("| AGP-01 | fresh | worker | The bus is shared | 9.9 | 4.5 | 5.0 | 2.0 | 6.0 | Medium | 30d | Review |",
                         "| AGP-01 | fresh | worker | The bus is shared | 9.9 | 4.5 | 5.0 | 2.0 | 6.0 | Medium | 30d | Review |\n"
                         "| AGP-1 | fresh | worker | A later copy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | Low | 90d | Review |")
    scores = _read(tmp_path, text)
    assert scores.rows["AGP-1"].stored["composite"] == D("6.0")
    assert [(i.finding_id, i.cause) for i in scores.issues] == [("AGP-1", "duplicate-id")]


def test_a_malformed_row_is_an_issue_and_the_other_rows_are_kept(tmp_path):
    text = V4484.replace("| LLM-1 | fresh | gateway | History is replayed | 5.4 | 8.0 | 8.0 | 7.0 | 6.9 | Medium | 30d | Review |",
                         "| LLM-1 | fresh | gateway |")
    scores = _read(tmp_path, text)
    assert list(scores.rows) == ["E-1", "AGP-1"]
    assert [(i.cause, i.finding_id) for i in scores.issues if i.cause == "malformed-row"] == [("malformed-row", None)]


def test_a_row_without_the_scores_it_needs_is_an_issue_and_is_scored_fresh(tmp_path):
    text = V4484.replace("| 5.4 | 8.0 | 8.0 | 7.0 | 6.9 |", "| 5.4 | n/a | 8.0 | 7.0 | 6.9 |")
    scores = _read(tmp_path, text)
    assert "LLM-1" not in scores.rows
    assert [(i.finding_id, i.cause) for i in scores.issues] == [("LLM-1", "incomplete-row")]
    assert "LLM-1" in scores.ids_in_any_row, "the ID is still one the baseline used (ruling B)"


def test_a_row_may_lack_its_cvss_score_when_a_vector_can_check_it(tmp_path):
    text = V4484.replace("| 5.4 | 8.0 | 8.0 | 7.0 | 6.9 |", "| \u2014 | 8.0 | 8.0 | 7.0 | 6.9 |")
    row = _read(tmp_path, text).rows["LLM-1"]
    assert row.stored["cvss_base"] is None and row.cvss_vector == V2
    no_vector = V4484.replace("| 9.9 | 4.5 | 5.0 | 2.0 | 6.0 |", "| \u2014 | 4.5 | 5.0 | 2.0 | 6.0 |")
    assert "AGP-1" not in _read(tmp_path, no_vector).rows, "no CVSS score and no vector leaves nothing to carry"


def test_stored_values_are_verbatim_even_when_they_are_wrong(tmp_path):
    """A seeded error must reach the renderer as written, so that it can be compared and corrected (SC-4)."""
    text = V4484.replace("| 9.1 | 7.0 | 8.5 | 7.0 | 8.0 | High |", "| 9.1 | 7.0 | 8.5 | 7.0 | 8.55 | Critical |")
    row = _read(tmp_path, text).rows["E-1"]
    assert row.stored["composite"] == D("8.55") and row.band == "Critical"
    huge = V4484.replace("| 9.1 | 7.0 | 8.5 | 7.0 | 8.0 | High |", "| 91 | 7.0 | 8.5 | 7.0 | 8.0 | High |")
    assert _read(tmp_path, huge).rows["E-1"].stored["cvss_base"] == D("91")


@pytest.mark.parametrize("cell", ["NaN", "Infinity", "1e1", "1_0", "9.1*", "high", "", "-1.0", "\u0669.1"])
def test_a_cell_that_is_not_a_plain_number_is_not_a_stored_score(tmp_path, cell):
    text = V4484.replace("| 9.1 | 7.0 | 8.5 | 7.0 | 8.0 | High |", "| %s | 7.0 | 8.5 | 7.0 | 8.0 | High |" % cell)
    assert _read(tmp_path, text).rows["E-1"].stored["cvss_base"] is None


def test_the_band_is_normalized_and_an_unknown_band_is_none(tmp_path):
    text = V4484.replace("| 8.0 | High | 7d |", "| 8.0 | **high** | 7d |").replace("| 6.9 | Medium | 30d |", "| 6.9 | Severe | 30d |")
    scores = _read(tmp_path, text)
    assert scores.rows["E-1"].band == "High"
    assert scores.rows["LLM-1"].band == "Medium", "§4's Severity column backs up an unreadable §2 band"


def test_governance_cells_are_none_when_empty_a_dash_or_not_a_date(tmp_path):
    text = V4484.replace("| LLM-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |", "| LLM-1 | Medium | \u2014 | | n/a | 2026-13-45 |")
    row = _read(tmp_path, text).rows["LLM-1"]
    assert row.owner is None and row.review_date is None
    assert (row.sla, row.disposition) == ("30d", "Review"), "§2's columns back up an empty §4 cell"


def test_an_sla_is_kept_as_written(tmp_path):
    text = V4484.replace("| LLM-1 | Medium | Unassigned | 30d |", "| LLM-1 | Medium | Unassigned | 24h |")
    assert _read(tmp_path, text).rows["LLM-1"].sla == "24h"
    text = V4484.replace("| LLM-1 | Medium | Unassigned | 30d |", "| LLM-1 | Medium | Unassigned | 30 days |")
    assert _read(tmp_path, text).rows["LLM-1"].sla == "30 days", "an unparseable SLA is the renderer's fallback to make, not the reader's"


def test_ids_that_appear_only_in_section_3_or_section_4_are_still_ids_the_baseline_used(tmp_path):
    text = V4484.replace("| AGP-01 | Medium | Unassigned | 30d | Review | 2026-11-19 |",
                         "| AGP-01 | Medium | Unassigned | 30d | Review | 2026-11-19 |\n| S-77 | Low | bob | 90d | Review | 2027-01-18 |")
    text = text.replace("## 4. Governance Fields", "### D-9 \u2014 a heading with no row\n\n## 4. Governance Fields")
    scores = _read(tmp_path, text)
    assert {"S-77", "D-9"} <= scores.ids_in_any_row
    assert "S-77" not in scores.rows and "D-9" not in scores.rows


def test_section_2a_rows_are_the_resolved_rows_with_their_own_governance(tmp_path):
    text = V4484.replace("---\n\n## 3. Dimensional Breakdown", """---

## 2a. Resolved Findings

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Status | Owner | Review Date | Flags |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|--------|-------|-------------|-------|
| S-9 | inherited | gateway | Old finding | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | Medium | 30d | Review | RESOLVED | carol | 2026-09-01 | resolved |

---

## 3. Dimensional Breakdown""", 1)
    scores = _read(tmp_path, text)
    assert list(scores.rows) == ["E-1", "AGP-1", "LLM-1"], "a resolved finding is never one of the open rows"
    row = scores.resolved_rows["S-9"]
    assert (row.owner, row.review_date, row.sla, row.disposition, row.band) == ("carol", date(2026, 9, 1), "30d", "Review", "Medium")
    assert row.stored["composite"] == D("5.0") and row.cvss_vector is None and row.form == "legacy"
    assert "S-9" in scores.ids_in_any_row


def test_a_file_with_only_resolved_rows_is_readable(tmp_path):
    text = "## 2a. Resolved Findings\n\n| ID | Composite | Owner |\n|---|---|---|\n| S-9 | 5.0 | carol |\n"
    scores = _read(tmp_path, text)
    assert scores.readable and scores.rows == {} and list(scores.resolved_rows) == ["S-9"]


def test_crlf_line_endings_and_a_byte_order_mark_are_read_the_same(tmp_path):
    text = "\ufeff" + V4484.replace("\n", "\r\n")
    scores = _read(tmp_path, text)
    assert list(scores.rows) == ["E-1", "AGP-1", "LLM-1"] and scores.frontmatter_date == date(2026, 10, 20)
    assert scores.rows["E-1"].cvss_vector == V1 and scores.rows["E-1"].owner == "alice"


def test_headings_inside_a_code_fence_are_not_sections(tmp_path):
    text = V4484.replace("## 4. Governance Fields", "```\n## 2. Scored Threat Table\n| ID | CVSS |\n| X-1 | 1 |\n```\n\n## 4. Governance Fields")
    assert list(_read(tmp_path, text).rows) == ["E-1", "AGP-1", "LLM-1"]


def test_an_invalid_vector_in_section_3_is_an_issue_and_leaves_the_vector_unset(tmp_path):
    text = V4484.replace(V2, "CVSS:3.1/AV:N/AC:L")
    scores = _read(tmp_path, text)
    assert scores.rows["LLM-1"].cvss_vector is None
    assert [(i.finding_id, i.field, i.cause) for i in scores.issues] == [("LLM-1", "cvss_vector", "invalid-value")]


def test_the_frontmatter_date_is_none_when_missing_or_invalid(tmp_path):
    assert _read(tmp_path, V4484.replace('date: "2026-10-20"', 'date: "someday"')).frontmatter_date is None
    assert _read(tmp_path, V4484.replace('date: "2026-10-20"\n', "")).frontmatter_date is None
    fenced = '```yaml\n---\ndate: "2026-02-03"\n---\n```\n\n' + V4484.split("\n---\n\n", 1)[1]
    assert _read(tmp_path, fenced).frontmatter_date == date(2026, 2, 3), "frontmatter inside a code fence is read too"


# ---- the real v4.48.4 output, read-only -------------------------------------------------------------------------

def test_the_committed_gated_subset_baseline_reads_in_full():
    folder = FIXTURES / "gated-subset" / "baseline"
    scores = rules.read_baseline_scores(folder / "risk-scores.md", sarif_path=folder / "risk-scores.sarif")
    assert scores.readable and scores.form == "legacy" and len(scores.rows) == 42 and scores.issues == ()
    assert "AGP-1" in scores.rows and "AGP-01" not in scores.rows
    assert all(row.cvss_vector is not None and row.vector_source == "md" and row.flags == () for row in scores.rows.values())
    assert all(None not in row.stored.values() for row in scores.rows.values())
    primaries = [row for row in scores.rows.values() if row.legacy_prose]
    assert primaries and all(row.zone and row.trust_level in tachi_parts.TRUST_LEVELS for row in primaries)
    assert scores.frontmatter_date == date(2026, 10, 20)


def test_the_committed_full_size_baseline_reads_every_finding():
    folder = FIXTURES / "baseline"
    text = (folder / "risk-scores.md").read_text(encoding="utf-8")
    table = text.split("## 2. Scored Threat Table", 1)[1].split("\n## 3.", 1)[0]
    ids = {tachi_parts.canonical_finding_id(line.split("|")[1].strip()) for line in table.splitlines()
           if line.startswith("| ") and tachi_parts.id_matches("finding", line.split("|")[1].strip())}
    scores = rules.read_baseline_scores(folder / "risk-scores.md", sarif_path=folder / "risk-scores.sarif")
    assert len(ids) == 408 and set(scores.rows) == ids and scores.ids_in_any_row == ids and scores.issues == ()


# The shipped samples, each read in its own form. A sample is only read here, never rendered. The expectations come
# from an independent, simpler reading of the same file, not from numbers pinned in this module.
SHIPPED = [
    "agentic-app/sample-report", "consumer-agent-app/sample-report", "mobile-banking-app/sample-report",
    "predictive-ml-app/sample-report", "maestro-reference",
]


def _first_cells(text, number):
    """The first cell of every row of the first table under ``## N.`` or ``## Section N:``, header and rule dropped."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if re.match(r"^## (?:Section )?%d[.:]" % number, line))
    cells = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            cells.append(line.strip().split("|")[1].strip().replace("**", ""))
        elif cells:
            break
    return cells[2:]


@pytest.mark.parametrize("folder", SHIPPED, ids=[name.split("/")[0] for name in SHIPPED])
def test_each_shipped_sample_is_readable_in_its_own_form(folder):
    base = EXAMPLES / folder
    text = (base / "risk-scores.md").read_text(encoding="utf-8")
    scores = rules.read_baseline_scores(base / "risk-scores.md", sarif_path=base / "risk-scores.sarif")
    scored, governance = _first_cells(text, 2), _first_cells(text, 4)
    ids = {tachi_parts.canonical_finding_id(cell) for cell in scored if tachi_parts.id_matches("finding", cell)}
    not_ids = [cell for cell in scored + governance if cell and not tachi_parts.id_matches("finding", cell) and cell.strip("-\u2013\u2014")]
    assert scores.readable and scores.form == "legacy" and set(scores.rows) == ids
    assert [issue.cause for issue in scores.issues].count("not-a-finding-id") == len(not_ids)
    assert {issue.cause for issue in scores.issues} <= {"not-a-finding-id", "duplicate-id"}
    assert all(key == tachi_parts.canonical_finding_id(key) for key in scores.rows)
    assert all(row.band in ("Critical", "High", "Medium", "Low") and row.form == "legacy" for row in scores.rows.values())
    assert all(None not in row.stored.values() for row in scores.rows.values())
    assert all(row.sla and row.disposition for row in scores.rows.values()), "§2's columns back up §4"
    if not governance or all(tachi_parts.id_matches("finding", cell) for cell in governance):
        assert all(row.review_date is not None and row.owner for row in scores.rows.values()), "a per-finding §4 gives every row its owner and date"


def test_the_predictive_ml_sample_lists_what_it_could_not_read():
    """Its §2 has `R-1..R-7` in one cell and its §4 has multi-ID and prose rows: each yields no row and one issue."""
    base = EXAMPLES / "predictive-ml-app" / "sample-report"
    scores = rules.read_baseline_scores(base / "risk-scores.md")
    assert {issue.cause for issue in scores.issues} == {"not-a-finding-id"}
    assert any("'R-1..R-7'" in issue.detail for issue in scores.issues)
    assert not any(key.startswith("R-") for key in scores.rows), "the grouped repudiation rows are not read, and are scored fresh"
    assert all(row.cvss_vector is None and row.legacy_prose == {} for row in scores.rows.values()), "it has no §3 subsections"


def test_the_maestro_sample_takes_a_vector_from_its_markdown_or_else_its_sarif():
    """The legacy-format variant: vectors on only some markdown rows, and the full vectors in the SARIF (R-26, S-4)."""
    base = EXAMPLES / "maestro-reference"
    text = (base / "risk-scores.md").read_text(encoding="utf-8")
    md = {}
    for block in text.split("\n### ")[1:]:
        label = re.match(r"([A-Z]+-[0-9]+)", block)
        vector = re.search(r"\*\*CVSS Vector\*\*: `(CVSS:3\.1/[^`]+)`", block)
        if label and vector:
            md.setdefault(tachi_parts.canonical_finding_id(label.group(1)), vector.group(1))
    sarif = {}
    for result in json.loads((base / "risk-scores.sarif").read_text(encoding="utf-8"))["runs"][0]["results"]:
        if result["properties"].get("cvss-vector"):
            sarif.setdefault(tachi_parts.canonical_finding_id(result["partialFingerprints"]["findingId/v1"]), result["properties"]["cvss-vector"])
    scores = rules.read_baseline_scores(base / "risk-scores.md", sarif_path=base / "risk-scores.sarif")
    assert md and sarif and set(md) & set(scores.rows) and (set(sarif) - set(md)) & set(scores.rows), "both sources are in play"
    for finding_id, row in scores.rows.items():
        if finding_id in md:
            assert (row.cvss_vector, row.vector_source) == (md[finding_id], "md")
        elif finding_id in sarif:
            assert (row.cvss_vector, row.vector_source) == (sarif[finding_id], "sarif")
        else:
            assert (row.cvss_vector, row.vector_source) == (None, None)
        expect_flag = finding_id in md and finding_id in sarif and md[finding_id] != sarif[finding_id]
        assert (row.flags == ("input:cvss_vector:sources-disagree",)) == expect_flag


def test_a_literal_pipe_in_a_legacy_cell_shifts_the_columns_so_the_row_is_not_read(tmp_path):
    """Seven cells where the header has six: reading them would take the Threat's second half for a score, and the
    scores after it for the wrong columns. Such a row is an issue and is scored fresh, never inherited shifted."""
    text = V4484.replace("| LLM-1 | fresh | gateway | History is replayed |", "| LLM-1 | fresh | gateway | History | is replayed |")
    scores = _read(tmp_path, text)
    assert "LLM-1" not in scores.rows and list(scores.rows) == ["E-1", "AGP-1"]
    assert [(i.cause, i.finding_id) for i in scores.issues] == [("malformed-row", None)]
    assert "LLM-1" in scores.ids_in_any_row, "§3 and §4 still name it"


def test_the_issue_list_is_capped_and_says_how_many_were_not_listed(tmp_path):
    bad = "".join("| bad-%d | fresh | c | t | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | Low | 90d | Review |\n" % n for n in range(rules.ISSUE_LIMIT + 50))
    scores = _read(tmp_path, V4484.replace("| E-1 | fresh |", bad + "| E-1 | fresh |"))
    assert len(scores.issues) == rules.ISSUE_LIMIT + 1
    assert scores.issues[-1] == rules.InputIssue(None, "issues", "truncated", "50 more issues were not listed")
    assert list(scores.rows) == ["E-1", "AGP-1", "LLM-1"], "a capped list never costs a row"
    unreadable = _read(tmp_path, "## 2. Scored Threat Table\n\n| ID | CVSS |\n|--|--|\n" + "| x | 1 |\n" * (rules.ISSUE_LIMIT + 5))
    assert unreadable.reason == "no-rows" and unreadable.issues[-1].cause == "truncated"


# =============================================================================
# 5. read_baseline_scores: the renderer's Scoring Inputs, and decoding
# =============================================================================

NARRATIVE = "Reachable from the network & **no** barrier; see {{score:cvss_base}} | `code` <b>x</b>\nsecond line &lt;kept&gt;"


def _inputs(finding_id="T-12", **overrides):
    """A complete set of persisted inputs for one finding, as (ID, field, value) rows (the renderer's step-1 inputs)."""
    values = {
        "cvss_vector": V2,
        "exploitability.known_techniques": "8", "exploitability.attack_complexity": "7",
        "exploitability.tooling_availability": "6", "exploitability.skill_level": "5",
        "scalability.scriptability": "4", "scalability.target_scope": "3",
        "scalability.resource_requirements": "2", "scalability.detection_difficulty": "1",
        "reachability.zone": "Edge DMZ", "reachability.trust_level": "Semi-Trusted",
        "reachability.auth_barriers": "1", "reachability.network_boundaries": "0",
        "rationale.cvss": NARRATIVE, "rationale.exploitability": "Well known.",
        "metric_rationale.AV": "Network.", "subscore_rationale.skill_level": "Little skill.",
        "score_bounds": "6.2,8.2", "tags": "auth,pii", "scored_on": "2026-11-01",
    }
    values.update(overrides)
    return [(finding_id, name, value) for name, value in values.items() if value is not None]


def _escaped(rows):
    """The renderer's write: each value escaped as a table cell, slots kept (D3)."""
    return [(i, n, tachi_parts.escape_cell(v, keep_slots=True)) for i, n, v in rows]


def _renderer_doc(inputs, *, resolved="", extra_rows="", date_line='date: "2026-11-22"'):
    table = "| ID | Field | Value |\n|---|---|---|\n" + "\n".join("| %s | %s | %s |" % row for row in inputs)
    return """---
schema_version: "1.1"
%(date)s
---

# Risk Scores Report

## 1. Executive Summary

One templated sentence.

## 2. Scored Threat Table

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Flags |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|-------|
| T-12 | fresh | api | A threat | 5.4 | 6.5 | 2.5 | 7.0 | 5.6 | Medium | 30d | Review | \u2014 |
%(extra)s
%(resolved)s
## 3. Dimensional Breakdown

### T-12 \u2014 api

**Score**: 5.4 | **Vector**: `%(v)s`

#### Reachability

**Score**: 7.0 | **Trust Zone**: Some Other Zone (Trusted)

A paragraph that the renderer form must not read as legacy prose.

## 4. Governance Fields

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| T-12 | Medium | R&amp;D &#124; lead | 30d | Review | 2026-12-22 |

## 5. Scoring Methodology

Text.

## 6. Score Integrity

### Integrity Summary

None.

### Score Flags

| ID | Flag | Field | Stored | Rendered | Cause |
|----|------|-------|--------|----------|-------|

### Input Issues

None.

### Scoring Inputs

%(table)s
""" % {"date": date_line, "extra": extra_rows, "resolved": resolved, "v": V1, "table": table}


def test_a_renderer_form_row_is_read_from_its_scoring_inputs(tmp_path):
    scores = _read(tmp_path, _renderer_doc(_escaped(_inputs())))
    assert scores.readable and scores.form == "renderer" and scores.issues == ()
    row = scores.rows["T-12"]
    assert (row.form, row.cvss_vector, row.vector_source) == ("renderer", V2, "md"), "§6's vector, not §3's"
    assert row.subscores == {"known_techniques": 8, "attack_complexity": 7, "tooling_availability": 6, "skill_level": 5,
                             "scriptability": 4, "target_scope": 3, "resource_requirements": 2, "detection_difficulty": 1}
    assert tuple(row.subscores) == tachi_parts.SUBSCORE_NAMES, "keyed by the eight bare names, in contract order"
    assert (row.zone, row.trust_level, row.auth_barriers, row.network_boundaries) == ("Edge DMZ", "Semi-Trusted", 1, 0)
    assert row.score_bounds == (D("6.2"), D("8.2")) and all(isinstance(x, Decimal) for x in row.score_bounds)
    assert row.tags_used == ("auth", "pii") and row.scored_on == date(2026, 11, 1)
    assert row.stored["composite"] == D("5.6") and row.band == "Medium" and row.sla == "30d"
    assert row.legacy_prose == {}, "a renderer-form row carries narrative, never legacy prose"
    assert row.owner == "R&D | lead", "§4's owner is decoded once"


def test_narrative_text_is_decoded_once_and_nothing_else_changes_it(tmp_path):
    row = _read(tmp_path, _renderer_doc(_escaped(_inputs()))).rows["T-12"]
    assert row.narrative["rationale.cvss"] == NARRATIVE, "the round trip: bold, a slot, `|`, a newline and a literal `&lt;` all survive"
    assert row.narrative["rationale.exploitability"] == "Well known."
    assert set(row.narrative) == {"rationale.cvss", "rationale.exploitability", "metric_rationale.AV", "subscore_rationale.skill_level"}


def test_a_value_is_decoded_exactly_once(tmp_path, monkeypatch):
    calls = []

    def tracer(text):
        calls.append(text)
        return text

    monkeypatch.setattr(tachi_parsers, "decode_references", tracer)  # a spy: it counts the calls and decodes nothing
    rows = _inputs(**{"rationale.cvss": "abc", "rationale.exploitability": "def", "tags": "pii"})
    row = _read(tmp_path, _renderer_doc(rows)).rows["T-12"]
    assert (row.narrative["rationale.cvss"], row.narrative["rationale.exploitability"]) == ("abc", "def")
    assert calls.count("abc") == 1 and calls.count("def") == 1 and calls.count("pii") == 1, "one decode for each value"
    calls.clear()
    legacy = _read(tmp_path, V4484).rows["E-1"]
    assert legacy.legacy_prose["metric_rationale.AV"] == "Reachable over the network"
    assert calls.count("Reachable over the network") == 1, "legacy prose is decoded too, once"


def test_a_literal_reference_in_text_survives_a_write_and_a_read(tmp_path):
    for original in ("a &lt; b", "&amp;lt;", "&#10;", "tab\tand | pipe", "{{{score:x}} and {{ok}}", "100% & more"):
        rows = _inputs(**{"rationale.cvss": original})
        assert _read(tmp_path, _renderer_doc(_escaped(rows))).rows["T-12"].narrative["rationale.cvss"] == original, original


def test_no_tags_row_means_none_were_recorded_and_an_empty_row_means_none_were_used(tmp_path):
    assert _read(tmp_path, _renderer_doc(_escaped(_inputs(tags=None)))).rows["T-12"].tags_used is None
    assert _read(tmp_path, _renderer_doc(_escaped(_inputs(tags="")))).rows["T-12"].tags_used == ()
    assert _read(tmp_path, _renderer_doc(_escaped(_inputs(tags="pii, AUTH, pii")))).rows["T-12"].tags_used == ("auth", "pii")


def test_optional_inputs_may_be_absent(tmp_path):
    rows = _inputs(**{"score_bounds": None, "scored_on": None, "reachability.zone": None, "reachability.trust_level": None})
    row = _read(tmp_path, _renderer_doc(_escaped(rows))).rows["T-12"]
    assert (row.form, row.score_bounds, row.scored_on, row.zone, row.trust_level) == ("renderer", None, None, None, None)


@pytest.mark.parametrize("name,value", [
    ("cvss_vector", "CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L"),
    ("exploitability.skill_level", "11"), ("exploitability.skill_level", "07"), ("scalability.target_scope", "x"),
    ("reachability.auth_barriers", "-1"), ("reachability.trust_level", "semi-trusted"), ("reachability.zone", "z" * 121),
    ("score_bounds", "8.2,6.2"), ("score_bounds", "6.2"), ("score_bounds", "6.25,8.2"), ("score_bounds", "6.2,10.1"),
    ("tags", "pii,bogus"), ("scored_on", "2026-02-30"), ("scored_on", "yesterday"),
])
def test_a_value_that_fails_its_class_is_an_issue_and_the_row_falls_back_to_legacy_when_it_was_required(tmp_path, name, value):
    scores = _read(tmp_path, _renderer_doc(_escaped(_inputs(**{name: value}))))
    issues = [issue for issue in scores.issues if issue.cause == "invalid-value"]
    assert [(i.finding_id, i.field) for i in issues] == [("T-12", name)]
    row = scores.rows["T-12"]
    required = name == "cvss_vector" or name in tachi_parts.SUBSCORE_NAMES or name.split(".")[-1] in tachi_parts.SUBSCORE_NAMES
    assert (row.form == "legacy") == required
    if not required:
        assert row.form == "renderer" and getattr(row, {"score_bounds": "score_bounds", "scored_on": "scored_on", "tags": "tags_used",
                                                        "reachability.auth_barriers": "auth_barriers", "reachability.trust_level": "trust_level",
                                                        "reachability.zone": "zone"}[name]) is None


def test_incomplete_inputs_make_a_legacy_row_with_an_issue_and_keep_the_vector(tmp_path):
    rows = [row for row in _inputs() if row[1] != "scalability.target_scope"]
    scores = _read(tmp_path, _renderer_doc(_escaped(rows)))
    row = scores.rows["T-12"]
    assert row.form == "legacy" and row.subscores is None and row.narrative == {} and row.tags_used is None
    assert row.cvss_vector == V2, "the vector that was there is still the best vector"
    assert [(i.finding_id, i.field, i.cause) for i in scores.issues] == [("T-12", "scoring_inputs", "incomplete-inputs")]
    assert "scalability.target_scope" in scores.issues[0].detail
    assert scores.form == "legacy", "no row is renderer form"
    assert (row.zone, row.trust_level) == ("Some Other Zone", "Trusted"), "a legacy row's zone is §3's line"


def test_inputs_without_any_sub_score_are_a_carried_legacy_finding_not_an_issue(tmp_path):
    """A legacy finding that a renderer run carried has no sub-scores to persist, so its inputs may be just a vector."""
    rows = [("T-12", "cvss_vector", V2), ("T-12", "tags", "pii"), ("T-12", "scored_on", "2026-11-01")]
    scores = _read(tmp_path, _renderer_doc(_escaped(rows)))
    row = scores.rows["T-12"]
    assert scores.issues == () and scores.form == "legacy"
    assert (row.form, row.cvss_vector, row.tags_used, row.scored_on, row.subscores) == ("legacy", V2, None, None, None)


def test_unknown_duplicate_and_foreign_input_rows_are_issues(tmp_path):
    rows = _inputs() + [("T-12", "evidence.0.snippet", "x"), ("T-12", "cvss_vector", V3), ("AGP-01", "tags", "pii"),
                        ("not-an-id", "tags", "pii"), ("T-99", "tags", "pii")]
    scores = _read(tmp_path, _renderer_doc(_escaped(rows)))
    causes = sorted(((i.finding_id or "", i.cause) for i in scores.issues))
    assert causes == [("", "not-a-finding-id"), ("T-12", "duplicate-field"), ("T-12", "unknown-field")]
    assert scores.rows["T-12"].cvss_vector == V2, "the first of a repeated field wins"
    assert {"AGP-1", "T-99"} <= scores.ids_in_any_row and "T-99" not in scores.rows


def test_a_scoring_inputs_table_without_the_three_columns_is_not_read(tmp_path):
    text = _renderer_doc(_escaped(_inputs())).replace("| ID | Field | Value |", "| ID | Name | Text |")
    scores = _read(tmp_path, text)
    assert scores.rows["T-12"].form == "legacy" and scores.rows["T-12"].cvss_vector == V1, "§3's vector"
    assert [i.cause for i in scores.issues] == ["unknown-form"]


def test_a_short_scoring_inputs_row_is_malformed(tmp_path):
    text = _renderer_doc(_escaped(_inputs())) + "| T-12 | tags |\n"
    assert "malformed-row" in [i.cause for i in _read(tmp_path, text).issues]


def test_ids_in_the_scoring_inputs_may_be_spelled_with_leading_zeros(tmp_path):
    rows = _escaped(_inputs("AGP-01"))
    text = _renderer_doc(rows).replace("| T-12 | fresh |", "| AGP-01 | fresh |")
    assert _read(tmp_path, text).rows["AGP-1"].form == "renderer"


# =============================================================================
# 6. read_baseline_scores: the SARIF fallback and the unreadable cases
# =============================================================================

def _sarif(*results):
    return json.dumps({"version": "2.1.0", "runs": [{"results": [
        {"partialFingerprints": {"findingId/v1": ident}, "properties": props} for ident, props in results]}]})


def test_a_vector_missing_from_the_markdown_comes_from_the_sarif_by_finding_id(tmp_path):
    sarif = _write(tmp_path, _sarif(("AGP-01", {"cvss-vector": V3}), ("E-1", {"cvss-vector": V1})), "risk-scores.sarif")
    scores = _read(tmp_path, V4484, sarif_path=sarif)
    assert (scores.rows["AGP-1"].cvss_vector, scores.rows["AGP-1"].vector_source) == (V3, "sarif")
    assert (scores.rows["E-1"].cvss_vector, scores.rows["E-1"].vector_source, scores.rows["E-1"].flags) == (V1, "md", ())


def test_a_disagreement_uses_the_markdown_and_flags_it(tmp_path):
    sarif = _write(tmp_path, _sarif(("E-1", {"cvss-vector": V3})), "risk-scores.sarif")
    row = _read(tmp_path, V4484, sarif_path=sarif).rows["E-1"]
    assert (row.cvss_vector, row.vector_source, row.flags) == (V1, "md", ("input:cvss_vector:sources-disagree",))


def test_the_renderer_forms_markdown_vector_is_checked_against_the_sarif_too(tmp_path):
    sarif = _write(tmp_path, _sarif(("T-12", {"cvss-vector": V3})), "risk-scores.sarif")
    row = _read(tmp_path, _renderer_doc(_escaped(_inputs())), sarif_path=sarif).rows["T-12"]
    assert row.form == "renderer" and row.cvss_vector == V2 and row.flags == ("input:cvss_vector:sources-disagree",)


def test_a_sarif_vector_that_is_null_invalid_or_foreign_is_ignored(tmp_path):
    sarif = _write(tmp_path, _sarif(("AGP-01", {"cvss-vector": None}), ("LLM-1", {"cvss-vector": "CVSS:3.1/bad"}),
                                    ("nope", {"cvss-vector": V3}), ("D-5", {"cvss-vector": V3})), "risk-scores.sarif")
    scores = _read(tmp_path, V4484, sarif_path=sarif)
    assert scores.rows["AGP-1"].cvss_vector is None and scores.rows["LLM-1"].cvss_vector == V2
    assert "D-5" not in scores.rows and scores.issues == ()


def test_the_first_sarif_result_for_an_id_wins_and_odd_shapes_are_skipped(tmp_path):
    body = {"runs": [{"results": [
        "not-a-result", {"partialFingerprints": "x"}, {"partialFingerprints": {"findingId/v1": "AGP-1"}, "properties": []},
        {"partialFingerprints": {"findingId/v1": "AGP-01"}, "properties": {"cvss-vector": V3}},
        {"partialFingerprints": {"findingId/v1": "AGP-1"}, "properties": {"cvss-vector": V1}}]}, "x", {"results": 3}]}
    sarif = _write(tmp_path, json.dumps(body), "risk-scores.sarif")
    assert _read(tmp_path, V4484, sarif_path=sarif).rows["AGP-1"].cvss_vector == V3
    for shape in ([], {"runs": 3}, "text", 7, None):
        sarif = _write(tmp_path, json.dumps(shape), "shape.sarif")
        assert _read(tmp_path, V4484, sarif_path=sarif).rows["AGP-1"].cvss_vector is None


@pytest.mark.parametrize("content", [b"{not json", b"\xff\xfe\x00", b"[" * 100000])
def test_an_unreadable_sarif_is_one_issue_and_the_rows_are_still_read(tmp_path, content):
    sarif = _write(tmp_path, content, "risk-scores.sarif")
    scores = _read(tmp_path, V4484, sarif_path=sarif)
    assert [(i.field, i.cause) for i in scores.issues] == [("cvss_vector", "unreadable-sarif")]
    assert list(scores.rows) == ["E-1", "AGP-1", "LLM-1"]


def test_a_sarif_path_that_does_not_exist_is_one_issue(tmp_path):
    scores = _read(tmp_path, V4484, sarif_path=tmp_path / "absent.sarif")
    assert [(i.field, i.cause) for i in scores.issues] == [("cvss_vector", "unreadable-sarif")]


def _unreadable(scores, reason):
    assert (scores.readable, scores.reason, scores.form) == (False, reason, None)
    assert (dict(scores.rows), dict(scores.resolved_rows), scores.frontmatter_date) == ({}, {}, None)


def test_a_missing_file_a_directory_a_link_and_none_are_missing(tmp_path):
    target = _write(tmp_path, V4484)
    _symlink(target, tmp_path / "link.md")
    (tmp_path / "dir.md").mkdir()
    for path in (tmp_path / "absent.md", tmp_path / "dir.md", tmp_path / "link.md", None):
        _unreadable(rules.read_baseline_scores(path), "missing")


def test_a_file_that_is_not_utf8_is_unreadable(tmp_path):
    _unreadable(_read(tmp_path, b"\xff\xfe## 2. Scored\n"), "not-utf8")
    _unreadable(_read(tmp_path, V4484.encode("utf-8") + b"\xc3\x28"), "not-utf8")


def test_a_file_over_the_cap_is_unreadable_and_a_file_at_the_cap_is_not(tmp_path, monkeypatch):
    data = V4484.encode("utf-8")
    monkeypatch.setattr(tachi_parts, "MAX_AGENT_INPUT_BYTES", len(data))
    assert _read(tmp_path, data).readable
    monkeypatch.setattr(tachi_parts, "MAX_AGENT_INPUT_BYTES", len(data) - 1)
    _unreadable(_read(tmp_path, data), "too-large")


def test_the_cap_is_the_16_mib_of_the_agent_input_limit():
    assert tachi_parts.MAX_AGENT_INPUT_BYTES == 16 * 1024 * 1024


def test_a_file_that_yields_no_row_is_unreadable_and_says_what_it_could_not_read(tmp_path):
    scores = _read(tmp_path, "# Notes\n\nNothing tabular here.\n")
    _unreadable(scores, "no-rows")
    assert scores.ids_in_any_row == frozenset() and scores.issues == ()
    only_bad = V4484.replace("| E-1 | fresh |", "| ?? | fresh |").replace("| LLM-1 | fresh |", "| ?? | fresh |").replace("| AGP-01 | fresh |", "| ?? | fresh |")
    scores = _read(tmp_path, only_bad)
    _unreadable(scores, "no-rows")
    assert [i.cause for i in scores.issues].count("not-a-finding-id") >= 3
    assert {"E-1", "LLM-1", "AGP-1"} <= scores.ids_in_any_row, "§4 still names the IDs, and ruling B counts them"


def test_a_section_without_a_table_yields_no_rows_and_no_issue(tmp_path):
    scores = _read(tmp_path, "## 2. Scored Threat Table\n\nNo findings.\n\n## 4. Governance Fields\n\nNone.\n")
    assert (scores.readable, scores.reason, scores.issues) == (False, "no-rows", ())


def test_a_table_without_an_id_column_is_one_issue(tmp_path):
    scores = _read(tmp_path, "## 2. Scored Threat Table\n\n| Component | CVSS |\n|---|---|\n| api | 5.0 |\n")
    assert scores.reason == "no-rows" and [i.cause for i in scores.issues] == ["no-id-column"]


def test_a_scoring_inputs_heading_without_a_table_changes_nothing(tmp_path):
    text = V4484.replace("## 5. Scoring Methodology", "### Scoring Inputs\n\nNothing persisted.\n\n## 5. Scoring Methodology")
    scores = _read(tmp_path, text)
    assert scores.issues == () and scores.form == "legacy" and list(scores.rows) == ["E-1", "AGP-1", "LLM-1"]


def test_a_read_error_after_the_open_is_a_missing_file(tmp_path, monkeypatch):
    path = _write(tmp_path, V4484)

    def broken(descriptor, size):
        raise OSError("input/output error")

    monkeypatch.setattr(os, "read", broken)
    _unreadable(rules.read_baseline_scores(path), "missing")


def test_a_path_may_be_text_or_a_path_object(tmp_path):
    path = _write(tmp_path, V4484)
    assert rules.read_baseline_scores(str(path)).rows.keys() == rules.read_baseline_scores(path).rows.keys()


def test_reading_never_raises_on_hostile_input(tmp_path):
    hostile = [
        "## 2. Scored Threat Table\n|\n|||\n| ID |\n| S-1 |\n",
        "## 2. Scored Threat Table\n\n| ID | CVSS |\n|---|---|\n| S-1 | 9.9 |\n",
        "## 6. Score Integrity\n### Scoring Inputs\n| ID | Field | Value |\n|---|---|---|\n| S-1 | cvss_vector |\n| S-1 | tags | &#0; |\n",
        "#" * 5000 + "\n" + "| " * 5000,
        "## 2. Scored Threat Table\n\n| ID | Composite |\n|---|---|\n| S-1 | 8.0 |\n### S-1\n**Vector**: `" + "CVSS:3.1/" * 500 + "`\n",
        "\x00\x01\x02 ## 2. \u202e",
    ]
    for text in hostile:
        scores = _read(tmp_path, text)
        assert isinstance(scores, rules.BaselineScores)


# =============================================================================
# 7. recompute_tags and select_tag_source (S-13)
# =============================================================================

ARCHITECTURE = '''```mermaid
flowchart LR
    Gateway["API Gateway<br/>[asset:auth]"]
    Vault[("Secrets Vault<br/>[asset:secrets,pii]")]
    Worker["Worker Pool"]
    Gateway --> Worker
```
'''


@pytest.fixture(scope="module")
def populator():
    return _load_hyphenated_script("populate_affected_assets_rules_test", "populate-affected-assets.py")


ROWS = [
    {"id": "S-1", "component": "API Gateway"},
    {"id": "AGP-01", "component": "secrets vault"},   # the matcher is case-insensitive, and the ID is spelled with a zero
    {"id": "T-2", "component": "Worker Pool"},        # a component with no tags
    {"id": "I-3", "component": "A Thing Nobody Drew"},  # a component nothing matches
    {"id": "E-4", "component": ""},
]


def test_recompute_tags_is_the_populators_join_over_the_open_rows(populator):
    tags = rules.recompute_tags(ARCHITECTURE, ROWS, populator.match_component)
    assert dict(tags) == {"S-1": ("auth",), "AGP-1": ("pii", "secrets"), "T-2": (), "I-3": (), "E-4": ()}
    assert list(tags) == ["S-1", "AGP-1", "T-2", "I-3", "E-4"], "one entry per open ID, in the rows' order, canonical"
    assert all(isinstance(value, tuple) for value in tags.values())


def test_recompute_tags_agrees_with_the_populators_own_block(populator):
    """The recomputation must equal what ``populate-affected-assets.py`` writes for the same findings (D2)."""
    threats = ("## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation |\n|---|---|---|---|---|\n"
               + "".join("| %s | %s | t | High | m |\n" % (row["id"], row["component"]) for row in ROWS if row["component"]))
    expected = {tachi_parts.canonical_finding_id(finding_id): tuple(tags)
                for finding_id, tags in populator.compute_affected_assets(ARCHITECTURE, threats)}
    open_rows = tachi_parsers.parse_threats_findings(threats)
    assert dict(rules.recompute_tags(ARCHITECTURE, open_rows, populator.match_component)) == expected
    assert expected["AGP-1"] == ("pii", "secrets")


def test_recompute_tags_uses_the_matcher_it_is_given_and_never_calls_it_without_a_component_name():
    seen = []

    def matcher(component, keys):
        seen.append((component, list(keys)))
        return "API Gateway" if component == "gw" else "Not In The Map"

    tags = rules.recompute_tags(ARCHITECTURE, [{"id": "S-1", "component": " gw "}, {"id": "S-2", "component": "x"}], matcher)
    assert dict(tags) == {"S-1": ("auth",), "S-2": ()}, "a matched name that is not in the map gives no tags"
    assert seen[0] == ("gw", ["API Gateway", "Secrets Vault"]), "the name is stripped, and the keys are the map's"


def test_recompute_tags_keeps_the_first_of_a_repeated_id_and_refuses_a_bad_id(populator):
    rows = [{"id": "S-1", "component": "API Gateway"}, {"id": "S-01", "component": "Secrets Vault"}]
    assert dict(rules.recompute_tags(ARCHITECTURE, rows, populator.match_component)) == {"S-1": ("auth",)}
    with pytest.raises(ValueError):
        rules.recompute_tags(ARCHITECTURE, [{"id": "X-1", "component": "API Gateway"}], populator.match_component)


def test_an_architecture_with_no_tags_recomputes_empty_tags_for_every_row(populator):
    tags = rules.recompute_tags("```mermaid\nflowchart LR\n  A[\"Plain\"]\n```\n", ROWS, populator.match_component)
    assert set(tags.values()) == {()}


IDS = ["S-1", "AGP-1", "T-2"]
FRESH = {"S-1": ("auth",), "AGP-1": ("pii", "secrets"), "T-2": ()}


def _select(block, recomputed=FRESH, ids=IDS):
    return rules.select_tag_source(open_ids=ids, block=block, recomputed=recomputed)


def test_a_block_that_equals_the_recomputation_is_the_source():
    source = _select({"S-1": ["auth"], "AGP-01": ["pii", "secrets"], "T-2": []})
    assert (source.source, source.warning, source.cause) == ("block", None, None)
    assert dict(source.tags) == FRESH, "keyed by canonical ID: the block's AGP-01 is AGP-1"


def test_tag_order_case_and_repeats_do_not_make_a_block_differ():
    assert _select({"S-1": ["AUTH", "auth"], "AGP-1": ["secrets", "pii"], "T-2": []}).source == "block"


def test_a_block_key_that_is_not_a_finding_id_is_ignored():
    source = _select({"S-1": ["auth"], "AGP-1": ["pii", "secrets"], "T-2": [], "junk": ["safety"], "": ["pii"]})
    assert source.source == "block" and set(source.tags) == set(IDS)


def test_extra_ids_in_the_block_are_ignored():
    source = _select({"S-1": ["auth"], "AGP-1": ["pii", "secrets"], "T-2": [], "D-9": ["safety"]})
    assert source.source == "block" and set(source.tags) == set(IDS)


@pytest.mark.parametrize("block,cause", [
    ({}, "block-absent"),
    ({"S-1": ["auth"], "AGP-1": ["pii", "secrets"]}, "block-missing-id"),
    ({"S-1": ["auth"], "AGP-1": ["pii"], "T-2": []}, "block-differs"),
    ({"S-1": ["auth"], "AGP-1": ["pii", "secrets"], "T-2": ["safety"]}, "block-differs"),
    ({"S-1": ["auth", "bogus"], "AGP-1": ["pii", "secrets"], "T-2": []}, "block-differs"),
    ({"AGP-1": ["pii"], "AGP-01": ["pii"], "S-1": ["auth"], "T-2": []}, "block-differs"),
], ids=["absent", "missing-id", "differs", "extra-tag", "unknown-tag", "two-spellings"])
def test_a_stale_block_is_replaced_by_the_recomputation_with_a_warning(block, cause):
    source = _select(block)
    assert (source.source, source.cause) == ("recomputed", cause)
    assert dict(source.tags) == FRESH and source.warning and "recomputed" in source.warning


def test_one_source_is_chosen_for_the_whole_run_and_the_two_are_never_mixed():
    """The block is right for S-1 and wrong for AGP-1: every finding takes the recomputation, S-1 included."""
    source = _select({"S-1": ["safety"], "AGP-1": ["pii", "secrets"], "T-2": []})
    assert source.source == "recomputed" and source.tags["S-1"] == ("auth",)
    source = _select({"S-1": ["auth"], "AGP-1": ["secrets"], "T-2": []})
    assert source.source == "recomputed" and source.tags["AGP-1"] == ("pii", "secrets")


def test_with_no_architecture_file_the_block_is_used_and_recorded_as_unverified():
    source = _select({"S-1": ["auth"], "AGP-01": ["secrets", "pii"]}, recomputed=None)
    assert (source.source, source.cause, source.warning) == ("block-unverified", "no-architecture-file", None)
    assert dict(source.tags) == {"S-1": ("auth",), "AGP-1": ("pii", "secrets"), "T-2": ()}, "an open ID the block misses has no tags"


def test_an_unverified_block_never_hands_the_modifier_a_tag_outside_the_closed_six():
    source = _select({"S-1": ["auth", "Bogus"], "AGP-1": ["pii"]}, recomputed=None)
    assert source.tags["S-1"] == ("auth",) and "bogus" in source.warning
    assert all(tag in tachi_parsers.VALID_ASSET_TAGS for tags in source.tags.values() for tag in tags)
    assert tachi_parts is not None and rules.tachi_scoring.elevate(V1, source.tags["S-1"])


@pytest.mark.parametrize("block", [{}, {"S-1": ["auth"], "AGP-1": ["pii"], "AGP-01": ["pii"]}], ids=["no-block", "unusable-block"])
def test_with_neither_source_no_finding_is_elevated_and_the_run_warns(block):
    source = _select(block, recomputed=None)
    assert (source.source, source.cause) == ("none", "no-tag-source")
    assert dict(source.tags) == {"S-1": (), "AGP-1": (), "T-2": ()}
    assert source.warning and "no finding was elevated" in source.warning


def test_every_outcome_has_one_entry_for_each_open_id_in_the_given_order():
    for source in (_select({}), _select({}, recomputed=None), _select({"S-1": ["auth"]}, recomputed=None),
                   _select({"S-1": ["auth"], "AGP-1": ["pii", "secrets"], "T-2": []})):
        assert list(source.tags) == IDS
        assert all(isinstance(tags, tuple) for tags in source.tags.values())


def test_the_causes_fit_a_stage_record_code():
    pattern = re.compile(r"[a-z0-9:_.-]{1,64}")
    for block, recomputed in (({}, FRESH), ({"S-1": ["auth"]}, FRESH), ({"S-1": ["pii"], "AGP-1": [], "T-2": []}, FRESH),
                              ({"S-1": ["auth"]}, None), ({}, None)):
        cause = _select(block, recomputed=recomputed).cause
        assert pattern.fullmatch(cause), cause


def test_an_open_id_that_is_not_a_finding_id_raises():
    with pytest.raises(ValueError):
        rules.select_tag_source(open_ids=["X-1"], block={}, recomputed={})


def test_the_recomputation_feeds_the_selector_end_to_end(populator):
    fresh = rules.recompute_tags(ARCHITECTURE, ROWS, populator.match_component)
    ids = list(fresh)
    assert rules.select_tag_source(open_ids=ids, block=dict(fresh), recomputed=fresh).source == "block"
    assert rules.select_tag_source(open_ids=ids, block={}, recomputed=fresh).source == "recomputed"


# =============================================================================
# 8. asset_outcome and cvss_chain (R-25, D10)
# =============================================================================

TAMPER = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L"        # base 7.1; pii elevates it to 8.3
TAMPER_PII = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L"
MAXV = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"          # base 10.0; every tag is a no-op
LOW = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:N"          # base 0.0
X3 = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N"           # base 7.2; pii gives 9.3, auth gives 10.0
X1 = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N"           # base 5.0; auth gives 9.6
ABOVE = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L"        # base 9.4, already above the ceiling; safety gives 9.8


def test_the_vectors_these_cases_use_have_the_scores_they_are_chosen_for():
    scoring = rules.tachi_scoring
    assert [scoring.base_score(v) for v in (TAMPER, TAMPER_PII, MAXV, LOW, X3, X1, ABOVE)] == [
        D("7.1"), D("8.3"), D("10.0"), D("0.0"), D("7.2"), D("5.0"), D("9.4")]
    assert scoring.base_score(scoring.elevate(X3, ["pii"])) == D("9.3") and scoring.base_score(scoring.elevate(X3, ["auth"])) == D("10.0")
    assert scoring.base_score(scoring.elevate(X1, ["auth"])) == D("9.6") and scoring.base_score(scoring.elevate(ABOVE, ["safety"])) == D("9.8")
    assert scoring.elevate(MAXV, ["pii", "safety"]) == MAXV


def _chain(vector, tags=(), bounds=None):
    return rules.cvss_chain(vector, tags=tags, score_bounds=bounds)


def test_without_tags_the_chain_is_the_base_clamped_to_its_bounds():
    chain = _chain(TAMPER)
    assert chain == rules.CvssChain(D("7.1"), None, D("7.1"), False, None, None, D("7.1"), None)
    clamped = _chain(MAXV, bounds=(D("6.1"), D("8.1")))
    assert (clamped.base, clamped.assessed, clamped.cvss_base, clamped.clamp_cause) == (D("10.0"), D("8.1"), D("8.1"), "bound")
    assert _chain(LOW, bounds=(D("6.1"), D("8.1"))).cvss_base == D("6.1")
    assert _chain(TAMPER, bounds=(D("6.1"), D("8.1"))).clamp_cause is None, "inside its bounds nothing is clamped"


def test_a_tag_raises_the_score_to_the_elevated_vectors_and_records_both():
    chain = _chain(TAMPER, ["pii"])
    assert (chain.forced, chain.elevated_vector, chain.elevated_base) == (True, TAMPER_PII, D("8.3"))
    assert (chain.assessed, chain.cvss_base, chain.clamp_cause) == (D("7.1"), D("8.3"), None)


def test_the_ceiling_cuts_an_elevated_score_and_says_so():
    chain = _chain(X3, ["pii"])
    assert (chain.elevated_base, chain.cvss_base, chain.clamp_cause) == (D("9.3"), D("9.2"), "ceiling")
    assert _chain(X1, ["auth"]).cvss_base == D("9.2")


def test_a_finding_assessed_above_the_ceiling_keeps_its_score(  ):
    """R-25: the modifier never lowers a score, so 9.4 stays 9.4 although the elevated 9.8 is capped at 9.2."""
    chain = _chain(ABOVE, ["safety"])
    assert (chain.assessed, chain.elevated_base, chain.cvss_base, chain.clamp_cause) == (D("9.4"), D("9.8"), D("9.4"), None)


def test_a_no_op_tag_still_counts_as_forcing_and_a_bound_clamp_gives_way_to_the_modifier():
    chain = _chain(MAXV, ["pii"])
    assert (chain.forced, chain.elevated_vector, chain.cvss_base, chain.clamp_cause) == (True, MAXV, D("10.0"), None)
    lifted = _chain(MAXV, ["pii"], bounds=(D("6.1"), D("8.1")))
    assert (lifted.assessed, lifted.cvss_base, lifted.clamp_cause) == (D("8.1"), D("9.2"), "ceiling"), (
        "the modifier follows the clamp and is meant to exceed it (asset-modifiers.md:22)")
    kept = _chain(TAMPER, ["financial"], bounds=(D("6.1"), D("8.1")))
    assert kept.elevated_vector == TAMPER and kept.cvss_base == D("7.1")


def test_a_bound_that_beats_a_smaller_modifier_result_is_the_cause():
    chain = _chain(X1, ["pii"], bounds=(D("8.0"), D("9.0")))   # base 5.0 -> 8.0, and pii gives 7.7: the bound wins
    assert (chain.assessed, chain.elevated_base, chain.cvss_base, chain.clamp_cause) == (D("8.0"), D("7.7"), D("8.0"), "bound")


def test_every_chain_score_is_a_one_decimal_decimal():
    for vector in (TAMPER, MAXV, LOW, X3, X1, ABOVE):
        for tags in ((), ("pii",), ("auth", "safety")):
            for bounds in (None, (D("3.3"), D("5.3"))):
                score = _chain(vector, tags, bounds).cvss_base
                assert isinstance(score, Decimal) and score == score.quantize(D("0.1")) and rules.tachi_scoring.band(score)


def test_asset_outcome_is_the_larger_of_the_assessed_and_the_capped_elevated_score():
    outcome = rules.asset_outcome
    assert outcome(D("7.1"), TAMPER, ["pii"]) == D("8.3")
    assert outcome(D("9.4"), ABOVE, ["safety"]) == D("9.4")
    assert outcome(D("7.2"), X3, ["pii", "auth"]) == D("9.2")
    assert outcome(D("9.5"), MAXV, ["pii"]) == D("9.5") and outcome(D("5.0"), MAXV, ["pii"]) == D("9.2")
    assert outcome(D("7.1"), TAMPER, []) == D("7.1") and outcome(D("7.1"), TAMPER, ()) == D("7.1")
    assert outcome(7, TAMPER, ()) == D("7")


def test_a_score_is_never_a_float_and_a_tag_or_vector_outside_the_contract_raises():
    with pytest.raises(TypeError):
        rules.asset_outcome(7.1, TAMPER, ["pii"])
    with pytest.raises(TypeError):
        rules.asset_outcome(True, TAMPER, [])
    with pytest.raises(ValueError):
        rules.asset_outcome(D("7.1"), TAMPER, ["bogus"])
    with pytest.raises(ValueError):
        _chain("CVSS:3.1/AV:N", ["pii"])
    with pytest.raises(ValueError):
        _chain(TAMPER, ["bogus"])


# =============================================================================
# 9. check_carried_vector (D10, ruling A)
# =============================================================================

def make_row(finding_id="T-1", **overrides):
    """A BaselineRow with every field given, so a case names only what it is about."""
    fields = dict(
        finding_id=finding_id, form="legacy", cvss_vector=TAMPER, vector_source="md", score_bounds=None, subscores=None,
        zone=None, trust_level=None, auth_barriers=None, network_boundaries=None, tags_used=None, scored_on=None,
        stored={"cvss_base": D("7.1"), "exploitability": D("6.0"), "scalability": D("6.0"), "reachability": D("6.0"),
                "composite": D("6.3")},
        band="Medium", owner="alice", sla="30d", disposition="Review", review_date=date(2026, 12, 1), narrative={},
        legacy_prose={}, flags=())
    fields.update(overrides)
    stored = fields["stored"]
    if "cvss_base" in overrides:
        fields["stored"] = dict(stored, cvss_base=overrides.pop("cvss_base"))
    return rules.BaselineRow(**{k: v for k, v in fields.items() if k != "cvss_base"})


def _check_vector(row, tags=()):
    return rules.check_carried_vector(row, tags=tags)


def _renderer_row(stored, **overrides):
    values = dict(form="renderer", cvss_vector=TAMPER, stored={"cvss_base": stored, "exploitability": D("6.0"), "scalability": D("6.0"),
                                                            "reachability": D("6.0"), "composite": D("6.3")},
                  subscores={name: 5 for name in tachi_parts.SUBSCORE_NAMES}, tags_used=(), score_bounds=None, scored_on=date(2026, 11, 1))
    values.update(overrides)
    return make_row(**values)


def test_a_renderer_row_whose_stored_score_the_chain_gives_passes():
    assert _check_vector(_renderer_row(D("7.1"))) == rules.VectorCheck(D("7.1"), None, "renderer")
    assert _check_vector(_renderer_row(D("8.3"), tags_used=("pii",)), ["pii"]) == rules.VectorCheck(D("8.3"), None, "renderer")
    bounded = _renderer_row(D("8.1"), cvss_vector=MAXV, score_bounds=(D("6.1"), D("8.1")))
    assert _check_vector(bounded) == rules.VectorCheck(D("8.1"), None, "renderer"), "the stored bounds are part of the chain"


def test_a_renderer_row_whose_stored_score_is_wrong_is_corrected_to_the_chain():
    assert _check_vector(_renderer_row(D("9.0"))) == rules.VectorCheck(D("7.1"), "corrected:cvss_base:vector", "renderer")
    assert _check_vector(_renderer_row(D("7.15"))).flag == "corrected:cvss_base:vector", "an off-grid stored score is wrong"
    assert _check_vector(_renderer_row(D("9.0"), tags_used=("pii",)), ["pii"]).flag == "corrected:cvss_base:vector"


def test_a_renderer_row_that_only_its_tags_moved_is_retagged_never_corrected():
    added = _check_vector(_renderer_row(D("7.1"), tags_used=()), ["pii"])
    assert added == rules.VectorCheck(D("8.3"), "retagged:cvss_base:asset-tags", "renderer")
    removed = _check_vector(_renderer_row(D("8.3"), tags_used=("pii",)), [])
    assert removed == rules.VectorCheck(D("7.1"), "retagged:cvss_base:asset-tags", "renderer")
    assert _check_vector(_renderer_row(D("7.1"), tags_used=None), ["pii"]).flag == "retagged:cvss_base:asset-tags", (
        "no recorded tags means none were used")
    assert _check_vector(_renderer_row(D("5.0"), tags_used=()), ["pii"]).flag == "corrected:cvss_base:vector", (
        "a value that no tag set explains stays a correction")


def test_a_missing_stored_score_is_rendered_from_the_chain_and_flagged_as_missing():
    assert _check_vector(_renderer_row(None), ["pii"]) == rules.VectorCheck(D("8.3"), "input:cvss_base:missing", "renderer")
    assert _check_vector(make_row(cvss_base=None), ["pii"]) == rules.VectorCheck(D("8.3"), "input:cvss_base:missing", "6")


def test_a_row_with_no_vector_is_unverifiable_and_keeps_its_score():
    for form in ("legacy", "renderer"):
        check = _check_vector(make_row(form=form, cvss_vector=None, vector_source=None, cvss_base=D("6.6")), ["pii"])
        assert check == rules.VectorCheck(D("6.6"), "unverifiable:cvss_base:no-vector", "1")


PREFIXES = tachi_parts.FINDING_PREFIXES


def _bounds_of(prefix):
    scoring = rules.tachi_scoring
    return scoring.bounds(scoring.default_score(scoring.category_for_prefix(prefix)))


def _clamp_to(score, bounds):
    return max(bounds[0], min(score, bounds[1]))


@pytest.mark.parametrize("prefix", PREFIXES)
def test_d10s_legacy_list_for_each_of_the_12_prefixes_without_tags(prefix):
    """A wrong-vector score is corrected, an own-bound clamp passes, another category's bound value is unchecked."""
    finding = "%s-1" % prefix
    base_high, base_low = D("10.0"), D("0.0")
    for vector, base in ((MAXV, base_high), (LOW, base_low)):
        own = _clamp_to(base, _bounds_of(prefix))
        for stored in {base, own}:
            check = _check_vector(make_row(finding, cvss_vector=vector, cvss_base=stored))
            assert (check.cvss_base, check.flag, check.step) == (stored, None, "3"), (prefix, vector, stored)
        others = {_clamp_to(base, _bounds_of(other)) for other in PREFIXES} - {base, own}
        for stored in others:
            check = _check_vector(make_row(finding, cvss_vector=vector, cvss_base=stored))
            assert (check.cvss_base, check.flag, check.step) == (stored, "unchecked:cvss_base:bound-n17c", "5"), (prefix, stored)
        wrong = _check_vector(make_row(finding, cvss_vector=vector, cvss_base=D("2.2")))
        assert (wrong.cvss_base, wrong.flag, wrong.step) == (base, "corrected:cvss_base:vector", "6")


def test_the_own_category_is_the_prefixs_so_oi_mi_and_te_score_like_llm_and_agentic():
    assert _bounds_of("OI") == _bounds_of("MI") == _bounds_of("LLM") and _bounds_of("TE") == _bounds_of("AGP") == _bounds_of("AG")
    s_low = _bounds_of("S")[0]
    assert _check_vector(make_row("S-1", cvss_vector=LOW, cvss_base=s_low)).flag is None
    assert _check_vector(make_row("D-1", cvss_vector=LOW, cvss_base=s_low)).flag == "unchecked:cvss_base:bound-n17c", (
        "7.2 is the spoofing floor, so for a DoS finding it is another category's clamp")


def test_legacy_step_2_a_forcing_tag_on_a_vector_that_already_carries_its_bits_is_unchecked():
    for stored in (D("9.5"), D("10.0")):
        check = _check_vector(make_row(cvss_vector=MAXV, cvss_base=stored), ["pii"])
        assert (check.cvss_base, check.flag, check.step) == (stored, "unchecked:cvss_base:assessed-unrecorded", "2")
    assert _check_vector(make_row(cvss_vector=MAXV, cvss_base=D("9.5")), []).flag == "corrected:cvss_base:vector", (
        "without the tag the same stored score is just wrong")
    assert _check_vector(make_row("E-1", cvss_vector=MAXV, cvss_base=D("10.0")), []).step == "3"


def test_legacy_step_3_the_documented_outcomes_pass_under_this_runs_tags():
    assert _check_vector(make_row(cvss_vector=ABOVE, cvss_base=D("9.4")), ["safety"]).step == "3", "assessed above 9.2 keeps it"
    check = _check_vector(make_row(cvss_vector=ABOVE, cvss_base=D("9.2")), ["safety"])
    assert (check.cvss_base, check.flag, check.step) == (D("9.2"), None, "3"), "an old capped score passes"
    assert _check_vector(make_row(cvss_vector=X3, cvss_base=D("9.2")), ["auth"]).flag is None
    assert _check_vector(make_row(cvss_vector=TAMPER, cvss_base=D("8.3")), ["pii"]).step == "3"


def test_legacy_step_4_a_stored_score_without_the_elevation_becomes_the_elevated_one_retagged():
    check = _check_vector(make_row(cvss_vector=TAMPER, cvss_base=D("7.1")), ["pii"])
    assert (check.cvss_base, check.flag, check.step) == (D("8.3"), "retagged:cvss_base:asset-tags", "4")
    clamped = _check_vector(make_row("S-1", cvss_vector=TAMPER, cvss_base=_bounds_of("S")[0]), ["pii"])
    assert (clamped.cvss_base, clamped.flag, clamped.step) == (D("8.3"), "retagged:cvss_base:asset-tags", "4"), (
        "the own-bound clamp 7.2 is the other candidate a")


def test_legacy_step_5_a_score_between_the_ceiling_and_the_elevated_score_is_unchecked():
    check = _check_vector(make_row(cvss_vector=X3, cvss_base=D("9.5")), ["auth"])
    assert (check.cvss_base, check.flag, check.step) == (D("9.5"), "unchecked:cvss_base:assessed-unrecorded", "5")
    assert _check_vector(make_row(cvss_vector=X3, cvss_base=D("9.5")), []).flag == "corrected:cvss_base:vector"


def test_legacy_step_6_corrects_to_the_outcome_under_this_runs_tags():
    check = _check_vector(make_row(cvss_vector=X3, cvss_base=D("3.0")), ["pii"])
    assert (check.cvss_base, check.flag, check.step) == (D("9.2"), "corrected:cvss_base:vector", "6")
    assert _check_vector(make_row(cvss_vector=X3, cvss_base=D("3.0")), []).cvss_base == D("7.2")
    assert _check_vector(make_row(cvss_vector=TAMPER, cvss_base=D("91"))).flag == "corrected:cvss_base:vector"


def test_the_legacy_rule_is_the_same_whether_the_vector_came_from_the_markdown_or_the_sarif():
    assert _check_vector(make_row(vector_source="sarif", cvss_base=D("7.1"))).flag is None


# =============================================================================
# 10. route_scorer_units and peer_divergence (R-31; D8's groups from parse_correlation_groups)
# =============================================================================

SECTION_4A = """## 4a. Correlated Findings

| Group | Findings | Component |
|---|---|---|
| CG-1 | S-1, T-2, I-3 | api |
| CG-2 | D-1, D-2 | db |
| CG-3 | T-2, E-5 | api |

## 5. Coverage Matrix
"""


def _routing(statuses, baseline_ids=(), groups_text=SECTION_4A, ids_in_any_row=()):
    rows = [{"id": finding_id, "component": "c", "delta_status": status} for finding_id, status in statuses.items()]
    groups = tachi_parsers.parse_correlation_groups(groups_text, member_ids=[canonical for canonical in
                                                                          (tachi_parts.canonical_finding_id(i) for i in statuses)])["groups"]
    baseline = rules.BaselineScores(True, None, "legacy", {i: make_row(i) for i in baseline_ids}, {},
                                    frozenset(ids_in_any_row) | frozenset(baseline_ids), None, ())
    return rules.route_scorer_units(rows, groups=groups, baseline=baseline)


def test_only_non_peers_that_need_judgment_go_to_the_agent():
    routing = _routing({"S-1": "NEW", "T-2": "UPDATED", "I-3": "NEW", "D-1": "UPDATED", "D-2": "UNCHANGED", "E-5": "NEW", "R-1": "UPDATED"},
                       baseline_ids=("D-1", "D-2", "R-1"))
    # CG-1: primary S-1 with peers T-2 and I-3. CG-2: primary D-1 with peer D-2. CG-3 never forms: T-2 is claimed by CG-1.
    assert routing.to_agent == ("S-1", "D-1", "E-5", "R-1")
    assert routing.copy_primary == {"T-2": "S-1", "I-3": "S-1"}
    assert routing.carried == ("D-2",) and routing.carried_peers == {"D-2": "D-1"}


def test_an_unchanged_finding_is_carried_when_its_row_is_usable_and_goes_to_the_agent_when_it_is_not():
    routing = _routing({"S-1": "UNCHANGED", "T-2": "UNCHANGED", "I-3": "UNCHANGED", "R-1": "UNCHANGED", "R-2": "UNCHANGED"},
                       baseline_ids=("S-1", "T-2", "R-1"))
    assert routing.carried == ("S-1", "T-2", "R-1")
    assert routing.carried_peers == {"T-2": "S-1"}, "a carried peer keeps its own score; the divergence check compares it with S-1's"
    assert routing.copy_primary == {"I-3": "S-1"}, "an unchanged peer with no usable row copies its primary"
    assert routing.to_agent == ("R-2",)


def test_a_new_finding_is_never_carried_even_when_the_baseline_used_its_id():
    """Ruling B: a reissued ID goes to the agent (a non-peer) or copies its primary (a peer), never `carried`."""
    routing = _routing({"S-1": "NEW", "R-1": "NEW", "T-2": "NEW"}, baseline_ids=("S-1", "R-1", "T-2"))
    assert routing.carried == () and routing.to_agent == ("S-1", "R-1") and routing.copy_primary == {"T-2": "S-1"}


def test_a_row_without_a_usable_status_counts_as_new():
    rows = [{"id": "R-1", "component": "c"}, {"id": "R-2", "component": "c", "delta_status": ""},
            {"id": "R-3", "component": "c", "delta_status": "**[UNCHANGED]**"}, {"id": "R-4", "component": "c", "delta_status": "—"}]
    baseline = rules.BaselineScores(True, None, "legacy", {i: make_row(i) for i in ("R-1", "R-2", "R-3", "R-4")}, {}, frozenset(), None, ())
    routing = rules.route_scorer_units(rows, groups=[], baseline=baseline)
    assert routing.carried == ("R-3",) and routing.to_agent == ("R-1", "R-2", "R-4")


def test_without_a_baseline_every_non_peer_goes_to_the_agent_and_every_peer_copies():
    for baseline in (None, rules.BaselineScores(False, "missing", None, {}, {}, frozenset(), None, ())):
        rows = [{"id": "S-1", "component": "c", "delta_status": "UNCHANGED"}, {"id": "T-2", "component": "c", "delta_status": "UNCHANGED"}]
        groups = tachi_parsers.parse_correlation_groups(SECTION_4A, member_ids=["S-1", "T-2"])["groups"]
        routing = rules.route_scorer_units(rows, groups=groups, baseline=baseline)
        assert (routing.to_agent, routing.carried, routing.copy_primary) == (("S-1",), (), {"T-2": "S-1"})


def test_the_groups_are_used_as_the_parser_gives_them_and_a_spelling_with_a_zero_is_one_id():
    text = "## 4a. Correlated Findings\n\n| Group | Findings |\n|---|---|\n| CG-1 | AGP-01, LLM-2 |\n"
    rows = [{"id": "AGP-01", "component": "c", "delta_status": "NEW"}, {"id": "LLM-2", "component": "c", "delta_status": "NEW"}]
    groups = tachi_parsers.parse_correlation_groups(text, member_ids=["AGP-01", "LLM-2"])["groups"]
    routing = rules.route_scorer_units(rows, groups=groups, baseline=None)
    assert routing.to_agent == ("AGP-1",) and routing.copy_primary == {"LLM-2": "AGP-1"}


def test_a_peer_whose_primary_is_not_an_open_finding_is_scored_like_any_other():
    rows = [{"id": "T-2", "component": "c", "delta_status": "NEW"}]
    routing = rules.route_scorer_units(rows, groups=[{"group_id": "CG-1", "primary": "S-1", "members": ["S-1", "T-2"]}], baseline=None)
    assert routing.to_agent == ("T-2",) and routing.copy_primary == {}


def test_the_partition_covers_every_open_finding_exactly_once():
    statuses = {"S-1": "UPDATED", "T-2": "UNCHANGED", "I-3": "NEW", "D-1": "UNCHANGED", "D-2": "UPDATED", "R-1": "NEW", "E-5": "UNCHANGED"}
    routing = _routing(statuses, baseline_ids=("T-2", "D-1", "E-5"))
    parts = list(routing.to_agent) + list(routing.carried) + list(routing.copy_primary)
    assert sorted(parts) == sorted(statuses) and len(parts) == len(set(parts))
    assert set(routing.carried_peers) <= set(routing.carried)


def test_a_divergent_peer_is_flagged_with_its_primary_and_an_equal_one_is_not():
    assert rules.peer_divergence(peer_composite=D("6.3"), primary_id="S-1", primary_composite=D("7.0")) == "divergent:composite_score:primary=S-1"
    assert rules.peer_divergence(peer_composite=D("7.0"), primary_id="S-1", primary_composite=D("7.00")) is None
    with pytest.raises(TypeError):
        rules.peer_divergence(peer_composite=7.0, primary_id="S-1", primary_composite=D("7.0"))


# =============================================================================
# 11. original_scoring_date, classify_band_change and governance_for (R-5, R-31, ruling A)
# =============================================================================

RUN = date(2026, 11, 22)


def test_the_original_scoring_date_is_the_stored_scored_on_date_or_the_review_date_less_the_sla():
    assert rules.original_scoring_date(make_row(scored_on=date(2026, 11, 1)), baseline_date=None) == rules.ScoringDate(date(2026, 11, 1), None)
    legacy = make_row(review_date=date(2026, 12, 1), sla="30d")
    assert rules.original_scoring_date(legacy, baseline_date=date(2026, 1, 1)) == rules.ScoringDate(date(2026, 11, 1), None)
    hours = make_row(review_date=date(2026, 11, 2), sla="24h")
    assert rules.original_scoring_date(hours, baseline_date=None).value == date(2026, 11, 1)


def test_the_fallback_rungs_when_the_dates_are_missing_or_unparseable():
    for row in (make_row(review_date=None), make_row(sla=None), make_row(sla="30 days"), make_row(review_date=date(1, 1, 5), sla="30d")):
        assert rules.original_scoring_date(row, baseline_date=date(2026, 10, 20)) == rules.ScoringDate(
            date(2026, 10, 20), "corrected:review_date:baseline-date")
        assert rules.original_scoring_date(row, baseline_date=None) == rules.ScoringDate(None, "unchecked:review_date:scoring-date-unknown")


@pytest.mark.parametrize("stored,rendered,with_tags,expected", [
    ("High", "High", "High", "none"), (None, "High", None, "none"), ("Bogus", "High", "Bogus", "none"),
    ("Medium", "High", "Medium", "retagged-up"), ("High", "Medium", "High", "retagged-down"),
    ("Low", "Critical", "Low", "retagged-up"), ("Critical", "Low", "Critical", "retagged-down"),
    ("Medium", "High", "High", "corrected"), ("Medium", "High", "Low", "corrected"), ("Medium", "High", None, "corrected"),
])
def test_a_band_change_the_baselines_tags_explain_is_a_retag_and_any_other_is_a_correction(stored, rendered, with_tags, expected):
    assert rules.classify_band_change(stored_band=stored, rendered_band=rendered, band_with_baseline_tags=with_tags) == expected


def test_classify_band_change_refuses_a_rendered_band_that_is_not_one():
    with pytest.raises(ValueError):
        rules.classify_band_change(stored_band="High", rendered_band="Severe", band_with_baseline_tags="High")


def _governance(status="UNCHANGED", band="Medium", change="none", row="default", baseline_date=None, run=RUN):
    row = make_row() if row == "default" else row
    return rules.governance_for(status, rendered_band=band, run_date=run, row=row, band_change=change, baseline_date=baseline_date)


def test_a_new_finding_is_unassigned_and_starts_its_clock_on_the_run_date():
    for band, sla, disposition, review in (("Critical", "24h", "Mitigate", date(2026, 11, 23)), ("High", "7d", "Mitigate", date(2026, 11, 29)),
                                           ("Medium", "30d", "Review", date(2026, 12, 22)), ("Low", "90d", "Review", date(2027, 2, 20))):
        assert _governance("NEW", band, row=None) == rules.Governance("Unassigned", sla, disposition, review, RUN, ())


def test_a_new_finding_never_takes_the_owner_of_a_baseline_row_that_reused_its_id():
    row = make_row(owner="alice", sla="14d", disposition="Accept")
    assert _governance("NEW", "High", row=row) == rules.Governance("Unassigned", "7d", "Mitigate", date(2026, 11, 29), RUN, ())


def test_a_finding_with_no_baseline_row_is_fresh_whatever_its_status():
    for status in ("UPDATED", "UNCHANGED"):
        assert _governance(status, "Low", row=None) == rules.Governance("Unassigned", "90d", "Review", date(2027, 2, 20), RUN, ())


def test_when_the_band_holds_the_stored_review_date_and_owner_are_kept_without_a_flag():
    row = make_row(owner="alice", review_date=date(2026, 12, 1), sla="30d")
    result = _governance(row=row)
    assert result == rules.Governance("alice", "30d", "Review", date(2026, 12, 1), date(2026, 11, 1), ())
    assert _governance(row=make_row(owner=None)).owner == "Unassigned"
    assert _governance(row=make_row(scored_on=date(2026, 11, 3), form="renderer")).scored_on == date(2026, 11, 3)


def test_a_corrected_band_counts_the_new_sla_from_the_original_scoring_date():
    """R-5: High is 7d, counted from the date the finding was first scored, 2026-11-01 (review 12-01 less 30d)."""
    result = _governance(band="High", change="corrected", row=make_row(review_date=date(2026, 12, 1), sla="30d"))
    assert (result.sla, result.disposition, result.review_date, result.scored_on) == ("7d", "Mitigate", date(2026, 11, 8), date(2026, 11, 1))
    assert result.flags == ("corrected:remediation_sla:follows-band", "corrected:review_date:follows-band", "corrected:risk_disposition:follows-band")
    stored = _governance(band="High", change="corrected", row=make_row(form="renderer", scored_on=date(2026, 11, 15), review_date=date(2026, 12, 15)))
    assert stored.review_date == date(2026, 11, 22) and stored.scored_on == date(2026, 11, 15)


def test_a_retag_up_takes_the_run_date_plus_the_new_sla_unless_the_stored_date_is_earlier():
    """Ruling A: tagging never makes a finding overdue on the day, and a higher band never gets more time."""
    sooner = _governance(band="High", change="retagged-up", row=make_row(scored_on=date(2026, 11, 20), form="renderer", review_date=date(2026, 12, 20)))
    assert (sooner.review_date, sooner.scored_on) == (date(2026, 11, 29), RUN)
    assert sooner.flags == ("retagged:remediation_sla:asset-tags", "retagged:review_date:asset-tags", "retagged:risk_disposition:asset-tags")
    earlier = _governance(band="High", change="retagged-up", row=make_row(scored_on=date(2026, 10, 1), form="renderer", review_date=date(2026, 10, 31)))
    assert (earlier.review_date, earlier.scored_on) == (date(2026, 10, 31), date(2026, 10, 1)), "overdue already: kept, never later"
    assert "retagged:review_date:asset-tags" not in earlier.flags and "retagged:remediation_sla:asset-tags" in earlier.flags
    assert _governance(band="High", change="retagged-up", row=make_row(review_date=date(2026, 11, 29), sla="30d")).review_date == date(2026, 11, 29)


def test_a_retag_down_keeps_the_original_scoring_date_so_a_missed_deadline_stays_missed():
    result = _governance(band="Medium", change="retagged-down", row=make_row(band="High", sla="7d", disposition="Mitigate",
                                                                             review_date=date(2026, 11, 17)))
    assert (result.review_date, result.scored_on) == (date(2026, 12, 10), date(2026, 11, 10))
    assert result.flags == ("retagged:remediation_sla:asset-tags", "retagged:review_date:asset-tags", "retagged:risk_disposition:asset-tags")
    missed = _governance(band="Medium", change="retagged-down", row=make_row(band="High", sla="7d", disposition="Mitigate", review_date=date(2026, 9, 8)))
    assert missed.review_date == date(2026, 10, 1) and missed.review_date < RUN, "never moved to the run date"


def test_no_value_that_follows_a_tag_moved_band_is_called_a_correction():
    for change in ("retagged-up", "retagged-down"):
        flags = _governance(band="High" if change == "retagged-up" else "Low", change=change, row=make_row()).flags
        assert flags and all(flag.startswith("retagged:") for flag in flags), flags


def test_overrides_are_carried_verbatim_and_flagged_and_the_owner_never_is():
    row = make_row(band="High", owner="bob", sla="14d", disposition="Accept", review_date=date(2026, 11, 20))
    result = _governance(band="Critical", change="corrected", row=row)
    assert (result.owner, result.sla, result.disposition) == ("bob", "14d", "Accept")
    assert result.flags == ("override:remediation_sla:human", "override:risk_disposition:human")
    assert result.review_date == date(2026, 11, 20), "an SLA override still keeps its review date, even through a correction"
    assert not any("owner" in flag for flag in result.flags)


@pytest.mark.parametrize("disposition", ["Accept", "accept", " Transfer "])
def test_accept_and_transfer_are_overrides_whatever_the_band(disposition):
    flags = _governance(row=make_row(disposition=disposition)).flags
    assert flags == ("override:risk_disposition:human",)


def test_a_disposition_or_sla_that_differs_from_the_stored_bands_default_is_an_override_and_the_rest_follow_the_band():
    assert _governance(band="High", row=make_row(band="High", sla="7d", disposition="Review")).flags == ("override:risk_disposition:human",)
    follows = _governance(band="High", change="corrected", row=make_row(band="Medium", sla="30d", disposition="Review"))
    assert (follows.sla, follows.disposition) == ("7d", "Mitigate") and not any(f.startswith("override") for f in follows.flags)
    composite_band = _governance(row=make_row(band=None, sla="14d"))
    assert composite_band.flags == ("override:remediation_sla:human",), "the stored band is read from the stored composite, 6.3 Medium"


def test_an_updated_finding_keeps_its_owner_and_overrides_and_a_band_change_restarts_its_clock():
    row = make_row(owner="carol", sla="14d", disposition="Accept", band="High", review_date=date(2026, 11, 28))
    kept = _governance("UPDATED", "Critical", "corrected", row)
    assert (kept.owner, kept.review_date, kept.sla) == ("carol", date(2026, 11, 28), "14d"), "an SLA override keeps its date"
    plain = make_row(owner="carol", band="Medium", sla="30d", disposition="Review", review_date=date(2026, 12, 1))
    restarted = _governance("UPDATED", "High", "corrected", plain)
    assert restarted == rules.Governance("carol", "7d", "Mitigate", date(2026, 11, 29), RUN, ()), "fresh values carry no follows-band flag"
    held = _governance("UPDATED", "Medium", "none", plain)
    assert (held.review_date, held.scored_on, held.flags) == (date(2026, 12, 1), date(2026, 11, 1), ())


def test_each_fallback_rung_when_the_original_scoring_date_is_unknown():
    unknown = make_row(sla=None, review_date=date(2026, 12, 1), disposition=None)
    rung1 = _governance(band="High", change="corrected", row=unknown, baseline_date=date(2026, 10, 20))
    assert rung1.review_date == date(2026, 10, 27) and "corrected:review_date:baseline-date" in rung1.flags
    rung2 = _governance(band="High", change="corrected", row=unknown)
    assert rung2.review_date == date(2026, 12, 1) and "unchecked:review_date:scoring-date-unknown" in rung2.flags
    rung3 = _governance(band="High", change="corrected", row=make_row(sla=None, review_date=None))
    assert rung3.review_date == date(2026, 11, 29) and rung3.scored_on == RUN and "corrected:review_date:clock-restarted" in rung3.flags
    assert all(flag.split(":")[1] != "review_date" or flag.count("follows-band") == 0 for flag in rung3.flags), "no second flag on a date a rung explains"


def test_a_missing_review_date_is_filled_and_flagged_as_missing_never_silently():
    row = make_row(form="renderer", scored_on=date(2026, 11, 1), review_date=None)
    result = _governance(row=row)
    assert (result.review_date, result.scored_on, result.flags) == (date(2026, 12, 1), date(2026, 11, 1), ("input:review_date:missing",))
    up = _governance(band="High", change="retagged-up", row=make_row(review_date=None))
    assert (up.review_date, up.scored_on) == (date(2026, 11, 29), RUN) and "input:review_date:missing" in up.flags


def test_an_sla_override_that_is_not_parseable_still_gets_a_review_date_and_is_carried_as_written():
    row = make_row(band="High", sla="a week", disposition="Mitigate", review_date=None)
    result = _governance(band="High", row=row)
    assert result.sla == "a week" and "override:remediation_sla:human" in result.flags
    assert result.review_date == date(2026, 11, 29), "counted with the band's own SLA, since 'a week' has no days"


def test_governance_refuses_a_status_band_or_change_it_does_not_know():
    for kwargs in (dict(status="RESOLVED"), dict(band="Severe"), dict(change="retagged")):
        with pytest.raises(ValueError):
            _governance(**kwargs)


def test_governance_is_the_same_for_the_same_inputs():
    row = make_row(band="Medium", review_date=date(2026, 12, 1))
    assert _governance(band="High", change="corrected", row=row) == _governance(band="High", change="corrected", row=row)


def test_a_stored_band_that_cannot_be_read_leaves_only_accept_and_transfer_as_overrides():
    off_grid = make_row(band=None, sla="14d", stored={"cvss_base": D("7.1"), "exploitability": D("6.0"), "scalability": D("6.0"),
                                                    "reachability": D("6.0"), "composite": D("6.35")})
    result = _governance(row=off_grid)
    assert result.sla == "30d" and result.flags == ("corrected:remediation_sla:follows-band",)
    assert _governance(row=make_row(band=None, disposition="Accept", stored={"composite": None})).flags == ("override:risk_disposition:human",)


def test_a_review_date_past_the_end_of_the_calendar_is_an_error_not_a_wrong_date():
    last = date(9999, 12, 31)
    with pytest.raises(ValueError):
        _governance("NEW", "High", row=None, run=last)
    with pytest.raises(ValueError):
        _governance("UPDATED", "High", "corrected", make_row(), run=last)
