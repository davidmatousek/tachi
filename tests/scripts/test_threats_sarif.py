"""Cases for the rewritten ``scripts/generate-threats-sarif.py``, written before the script (F-374 T099; TDD) and extended with it (T100; ADR-050 D1, D7, D8).

They target ``contracts/cli.md`` (the entry and the exit table: 0, 1, 2 and 4), ``contracts/sarif-result.md`` (the result's
shape and ruling C's sentence), ``.claude/skills/tachi-shared/references/sarif-identity-shared.md`` (the shared reference) and
ADR-050 D1 (the surface that PR 2 moves to shipped code), D4 (the write), D7 (identity) and D8 (membership, the N/N rule and
the claim rule), with the cross-read's errata (``test-results/w2-entry-pr2.md``: S1P-A18 to S1P-A21) and the architect's rulings
on T099's readings (S1P-A26 to S1P-A28), never an implementation. T099 wrote sections 1 to 11, red; T100's generator passes them,
and its own cases are section 12. ``generator`` loads the script when a case first asks, and a case fails with a message that
names a missing or an old script, not with an import error at collection.

How they run (ADR-050 D16, H15): the entry is loaded through ``tests/conftest.py``'s ``_load_hyphenated_script`` and driven
in-process through ``main(argv)``, so pytest-cov counts it. The one subprocess case, in section 11, shows what a process alone
shows: the bytecode guard and the output on a real interpreter. Nothing here pins a private helper: a case runs ``main(argv)``,
then reads the exit code, the streams and the file. Fixtures are synthetic (H8).

What these cases assume of the generator (T100's generator follows them; where a contract left a form open, the case says
``# reading:``, and the architect's rulings S1P-A26 to S1P-A28 settled the ones that T099 raised):

1. **The CLI** is ``generate-threats-sarif.py --threats FILE --out DIR [--architecture PATH]`` with ``--help`` and ``--version``.
   ``main(argv=None) -> int``, behind a thin ``__main__`` guard. The exit codes are the table's: 0, and 1 for a missing input,
   2 for a validation, usage or guard failure (an unreadable Section 7, a forbidden character), and 4 for a failed completeness
   or parity check (the emitter's self-check). It never exits 3 or 5.
2. **Where it reads.** ``--threats`` is the compiled ``threats.md``. Findings come from the reference-set wrapper
   (``tachi_parsers.parse_reference_set``, drift forms included), groups from ``parse_correlation_groups`` (the claim rule),
   the zone, the DFD type and the layer from Sections 1 and 2 and the per-finding tables, and ``affected_assets`` from the
   populator's block. ``--architecture`` is a candidate for D7's resolver (``sarif_common.resolve_architecture``): the flag,
   then the body line, then the default. Warnings go to stderr, and the exit stays 0.
3. **Where it writes.** ``<out>/threats.sarif`` and nothing else, atomically and only after the emitter's self-check. A failed
   run leaves an earlier ``threats.sarif`` as it was.
4. **The file** is the shared emitter's: one result per open finding, tachi's own hash with the tool ``Tachi``, no
   ``correlationGroup`` or ``baselineRunId`` in ``partialFingerprints`` (``baseline-run-id`` is a property), and ruling C's
   sentence on a correlated result. Its stamp names ``generate-threats-sarif.py`` (``contracts/cli.md``).

The groups, by what turns them green:

* ``test_harness_*``: no generator needed. They check the synthetic inputs and this module's readers.
* ``test_cli_*``, ``test_refusal_*`` and ``test_failure_*``: the entry, the exit table, intake and the failed write (T100).
* ``test_document_*``, ``test_result_*`` and ``test_reading_*``: the file's envelope and each result (T100).
* ``test_nn_*`` and ``test_membership_*``: D8's counting rule and its member set (T100).
* ``test_correlation_*``, ``test_identity_*`` and ``test_baseline_*``: ruling C, the regroup pair and ``baseline-run-id``.
* ``test_uri_*``, ``test_write_*`` and ``test_module_*``: D7's URI, D4's write and the script's own shape.
* ``test_properties_*``, ``test_rules_*`` and ``test_warning_*`` (section 12, T100's): the exact property set of S1P-A28, the rules, the
  taxonomies and the run's other stderr and exit readings.

The cases that need the cross-file harness (the scorer's and controls files beside this one, FR-E.13's pin and the carrier
chain) are ``test_sarif_identity.py``'s section 22, which builds on the project here.
"""
from __future__ import annotations

import ast
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from ..conftest import _load_hyphenated_script
from .test_render_risk_scores import (
    CATEGORY_NAME, COMPONENTS, DASH, DIGEST, HOSTILE_THREAT, RESOLVED, RESOLVED_IDS, SPECS, ZONES, invoke, make_architecture_md,
    make_threats_md, mitigation_of, spec, tree_state)
from .test_sarif_identity import EXPECTED_RULES, keys_of, message_parts, recipe, results_by, ruling_c

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common as sc  # noqa: E402  -- after the sys.path mutation
import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402

GENERATOR_NAME = "generate-threats-sarif.py"
GENERATOR = SCRIPTS_DIR / GENERATOR_NAME
SARIF = "threats.sarif"
TOOL = "Tachi"  # verbatim, a capital T: a different spelling re-keys every alert (D7)
INFORMATION_URI = "https://github.com/davidmatousek/tachi"
ARCHITECTURE = "docs/security/architecture.md"
BASELINE_RUN_ID = "2026-11-09T10-00-00"
LARGE_ARCH = REPO_ROOT / "tests" / "scripts" / "fixtures" / "large_arch"
PAIR = LARGE_ARCH / "regroup-pair" / "main"
GATED_SUBSET = LARGE_ARCH / "gated-subset"
LEVEL_OF = {"Critical": "error", "High": "error", "Medium": "warning", "Low": "note", "Note": "note"}  # ADR-013 D3, written out again
FIRST_GROUPS = [("CG-1", ["S-2", "S-10", "T-1"]), ("CG-2", ["E-3", "E-5"])]
ZONE_OF = {name: zone for zone, _label, _level, members in ZONES for name in members}
# The kinds that a Section 1 type may be written as. ``External Entity`` and ``Process`` are the closed map's; a Data Store is
# ``data`` where the renderers write it and ``data-store`` where the orchestrator-era generator did, and both read back the same.
KINDS = {"External Entity": ("external-entity",), "Process": ("process",), "Data Store": ("data", "data-store")}


# =============================================================================
# 1. The harness
# =============================================================================


def load_generator():
    """The generator as a loaded module, or a failure that names the missing rewrite (TDD: T100 writes it to these cases)."""
    if not GENERATOR.is_file():
        pytest.fail("scripts/generate-threats-sarif.py does not exist: T100 writes it to these cases (TDD)", pytrace=False)
    module = _load_hyphenated_script("generate_threats_sarif_under_test", GENERATOR_NAME)
    main = getattr(module, "main", None)
    if not callable(main) or "argv" not in inspect.signature(main).parameters:
        pytest.fail("scripts/generate-threats-sarif.py is still the orchestrator-era script, whose main() takes no argv: "
                    "T100 rewrites it to these cases (TDD)", pytrace=False)
    return module


@pytest.fixture(scope="module")
def generator():
    return load_generator()


def finding(finding_id, component, threat, risk="Medium", status="NEW"):
    """A synthetic Section 7 row. The generator reads only these five values, so the scorer's inputs are filler."""
    return spec(finding_id, component, threat, risk, status, "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N", (5, 5, 5, 5), (4, 4, 4, 4),
                ZONE_OF[component], "Trusted", 0, 0)


def with_baseline(text, run_id=BASELINE_RUN_ID):
    """The same ``threats.md`` with a baseline block that names a run: the one place ``baseline-run-id`` comes from."""
    assert text.count("  run_id: null") == 1
    return text.replace("  run_id: null", '  run_id: "%s"' % run_id)


class Project(object):
    """One synthetic project: a working directory, an architecture file, a run directory and its ``threats.md``."""

    def __init__(self, generator_module, root, specs=None, resolved=None, threats_text=None, **threats_options):
        self.generator = generator_module
        self.root = Path(root)
        self.out = self.root / "run"
        self.architecture = self.root / "docs" / "security" / "architecture.md"
        self.threats = self.out / "threats.md"
        self.specs = list(SPECS if specs is None else specs)
        self.resolved = list(RESOLVED if resolved is None else resolved)
        self.last = None
        self.architecture.parent.mkdir(parents=True)
        self.out.mkdir(parents=True)
        self.architecture.write_text(make_architecture_md(), encoding="utf-8")
        self.threats.write_text(make_threats_md(self.specs, self.resolved, **threats_options) if threats_text is None else threats_text,
                                encoding="utf-8")

    def generate(self, architecture=True, extra=(), threats=None):
        """``main(argv)`` in the project's directory. ``architecture`` is ``True`` for the project's own file, a path for another
        candidate, or falsy for no flag. ``threats`` names another input (the default is the project's ``threats.md``)."""
        argv = ["--threats", self.threats if threats is None else threats, "--out", self.out]
        if architecture is True:
            argv += ["--architecture", ARCHITECTURE]
        elif architecture:
            argv += ["--architecture", architecture]
        self.last = invoke(self.generator, argv + list(extra), self.root)
        return self.last

    @property
    def sarif_path(self):
        return self.out / SARIF

    @property
    def sarif_text(self):
        return self.sarif_path.read_text(encoding="utf-8")

    @property
    def sarif(self):
        return json.loads(self.sarif_text)

    @property
    def results(self):
        return results_by(self.sarif)

    @property
    def text(self):
        return self.threats.read_text(encoding="utf-8")


def reference_of(text):
    """What the shared readers say the file holds: the open findings, the groups and their roles, and the RESOLVED IDs.

    The member set, the claim rule and the roles are the one authority's (``parse_reference_set`` and ``parse_correlation_groups``,
    ADR-050 D8), so a case compares the generator with them and never with a second reading of its own.
    """
    reference = tachi_parsers.parse_reference_set(text)
    ids = [row["id"] for row in reference["open"]]
    canonical = [tp.canonical_finding_id(i) for i in ids]
    groups = tachi_parsers.parse_correlation_groups(text, canonical)["groups"]
    assignments = sc.correlation_assignments([(group["group_id"], group["members"]) for group in groups], canonical)
    status = {tp.canonical_finding_id(row["id"]): row.get("delta_status") for row in reference["open"]}
    return SimpleNamespace(rows=reference["open"], ids=ids, canonical=canonical, groups=groups, assignments=assignments,
                           resolved=[row["id"] for row in reference["resolved"]], status=status)


def strings_of(value, where="$"):
    """Every decoded string of a JSON document, keys included, with its place."""
    if isinstance(value, str):
        yield where, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield where + ".key", key
            for found in strings_of(item, "%s.%s" % (where, key)):
                yield found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            for found in strings_of(item, "%s[%d]" % (where, index)):
                yield found


def check_document(document, reference, uri=ARCHITECTURE):
    """What every run's file must satisfy, whatever its input: N/N, tachi's own hash, the rule, and the emitter's own self-check."""
    results = document["runs"][0]["results"]
    written = [result["partialFingerprints"]["findingId/v1"] for result in results]
    assert len(results) == len(set(written)) == len(reference.rows), "N is the number of results, of distinct findingId/v1 values and of open findings (D8)"
    assert sorted(written, key=tp.finding_sort_key) == sorted(reference.ids, key=tp.finding_sort_key), "findingId/v1 keeps Section 7's spelling"
    for result in results:
        finding_id = result["partialFingerprints"]["findingId/v1"]
        assert result["partialFingerprints"] == {"primaryLocationLineHash": recipe(TOOL, tp.canonical_finding_id(finding_id)),
                                                 "findingId/v1": finding_id}, finding_id
        assert result["ruleId"] == EXPECTED_RULES[tp.canonical_finding_id(finding_id).partition("-")[0]], finding_id
    sc.self_check(results, tool=TOOL, member_ids=reference.ids, assignments=reference.assignments, resolved_ids=reference.resolved, uri=uri)
    for where, text in strings_of(document):
        assert tp.forbidden_character(text) is None, "a forbidden character is in a decoded string of the file, at %s (D3, P0-4)" % where
    return results


def generated(project, uri=ARCHITECTURE, **options):
    """Run the generator, require a clean exit and the checks above, and return the document."""
    res = project.generate(**options)
    assert res.code == 0, res.describe()
    document = project.sarif
    check_document(document, reference_of(project.text), uri)
    return document


def kinds_of(component):
    return KINDS[COMPONENTS[component][0]]


@pytest.fixture(scope="module")
def plain(generator, tmp_path_factory):
    """One clean run over the nine-finding synthetic project: no groups and no baseline. Read-only for the cases below."""
    project = Project(generator, tmp_path_factory.mktemp("plain"))
    generated(project)
    return project


@pytest.fixture(scope="module")
def aware(generator, tmp_path_factory):
    """One clean run over the same findings with Section 4a's groups and a baseline that names a run."""
    text = with_baseline(make_threats_md(SPECS, RESOLVED, groups=FIRST_GROUPS, baseline_source="baseline/threats.md"))
    project = Project(generator, tmp_path_factory.mktemp("aware"), threats_text=text)
    generated(project)
    return project


def test_harness_the_synthetic_project_is_a_valid_reference_set_and_the_oracle_reads_it():
    text = make_threats_md(SPECS, RESOLVED, groups=FIRST_GROUPS, baseline_source="baseline/threats.md")
    reference = reference_of(with_baseline(text))
    assert sorted(reference.ids) == sorted(item["id"] for item in SPECS) and sorted(reference.resolved) == sorted(RESOLVED_IDS)
    assert sorted(reference.assignments) == ["E-3", "E-5", "S-10", "S-2", "T-1"], "both groups survive, filtered to the open findings"
    assert tachi_parsers.parse_baseline_frontmatter(with_baseline(text))["run_id"] == BASELINE_RUN_ID


def test_harness_the_tool_name_and_the_information_uri_are_the_emitters():
    assert sc.TOOL_NAMES[SARIF] == TOOL and sc.INFORMATION_URI == INFORMATION_URI
    assert sc.UPLOAD_CATEGORIES[SARIF] == "threat-model"


# =============================================================================
# 2. The command line and the exit codes (contracts/cli.md; ADR-050 D4)
# =============================================================================


def test_cli_help_and_version_are_supported(generator, tmp_path):
    helped = invoke(generator, ["--help"], tmp_path)
    assert helped.code == 0 and all(flag in helped.out for flag in ("--threats", "--out", "--architecture")), helped.describe()
    versioned = invoke(generator, ["--version"], tmp_path)
    assert versioned.code == 0, versioned.describe()
    assert tp.VERSION in versioned.out + versioned.err  # reading: cli.md says tests may accept either stream
    assert "%d.%d" % sys.version_info[:2] in versioned.out + versioned.err, "the interpreter's version too"


def test_cli_a_missing_required_argument_is_a_usage_error(generator, tmp_path):
    project = Project(generator, tmp_path)
    no_out = invoke(generator, ["--threats", project.threats], tmp_path)
    no_threats = invoke(generator, ["--out", project.out], tmp_path)
    unknown = invoke(generator, ["--threats", project.threats, "--out", project.out, "--no-such-flag"], tmp_path)
    for res in (no_out, no_threats, unknown):
        assert res.code == 2, res.describe()
    assert not project.sarif_path.exists()


def test_cli_a_clean_run_exits_0_prints_one_json_object_and_names_nothing_on_stderr(plain):
    res = plain.last
    assert res.code == 0, res.describe()
    assert res.err == "", "a clean run has no warning: %r" % res.err
    # reading: cli.md's preamble gives every entry but the two renderers one JSON object on stdout
    summary = json.loads(res.out)
    assert isinstance(summary, dict), res.describe()


def test_cli_a_missing_threats_file_exits_1_names_it_and_writes_nothing(generator, tmp_path):
    project = Project(generator, tmp_path)
    project.threats.unlink()
    res = project.generate()
    assert res.code == 1, res.describe()
    assert "threats.md" in res.err, res.describe()
    assert not project.sarif_path.exists()


def test_cli_a_threat_model_with_no_section_7_exits_2_names_the_section_and_writes_nothing(generator, tmp_path):
    """S-12(c): an unreadable Section 7 ends the run, and an empty extraction never passes (KB 22)."""
    text = make_threats_md().replace("## 7. Recommended Actions", "## 7. Something Else")
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 2, res.describe()  # reading: both PR 1 renderers and the planner exit 2 on ReferenceSetError
    assert "Section 7" in res.err, res.describe()
    assert not project.sarif_path.exists()


def test_cli_a_raw_pipe_in_a_cell_exits_2_and_the_remedy_names_the_escape(generator, tmp_path):
    """The wrapper's own refusal (a row with more cells than its header) reaches the user, remedy included (D3, P1-3)."""
    text = make_threats_md().replace("Admin routes skip the role check.", "Admin routes skip | the role check.")
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 2, res.describe()
    assert "&#124;" in res.err, res.describe()
    assert not project.sarif_path.exists()


def test_cli_an_input_that_is_not_strict_utf8_exits_2_and_writes_nothing(generator, tmp_path):
    project = Project(generator, tmp_path)
    project.threats.write_bytes(project.threats.read_bytes() + b"\xff\xfe broken")
    res = project.generate()
    assert res.code == 2, res.describe()  # reading: the renderer's rule ("the threat model input is not strict UTF-8")
    assert not project.sarif_path.exists()


FORBIDDEN = [("\x01", "c0"), ("\x85", "c1"), (chr(0x200e), "lrm"), (chr(0x061c), "alm"), (chr(0x202e), "bidi-override"), (chr(0x2028), "line-separator"),
             (chr(0x2029), "paragraph-separator"), (chr(0xE0041), "tag-character")]


@pytest.mark.parametrize("cell", ["threat", "mitigation"])
@pytest.mark.parametrize("char", [entry[0] for entry in FORBIDDEN], ids=[entry[1] for entry in FORBIDDEN])
def test_refusal_a_forbidden_character_in_a_value_it_takes_exits_2_and_writes_nothing(generator, tmp_path, char, cell):
    """ADR-050 D3's P0-4 and D4's row 2 (S1P-A18: "PR 2's writers call it too"): ``threats.md`` isn't a part, so the generator
    refuses a forbidden character where it takes a value, with exit 2, before any write. D16's hostile inputs name this set."""
    text = make_threats_md()
    # in the middle of the cell: a reader strips whitespace at a cell's edge, and U+0085, U+2028 and U+2029 are whitespace
    old, new = ("Admin routes skip the role check.", "Admin routes skip" + char + " the role check.") if cell == "threat" else (
        "Mitigation text for E-3.", "Mitigation" + char + " text for E-3.")
    assert old in text
    project = Project(generator, tmp_path, threats_text=text.replace(old, new))
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    res = project.generate()
    assert res.code == 2, res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n', "an earlier file is left as it was"


E3_ROW = "| E-3 | NEW | Elevation of Privilege | " + DASH + " | edge-gateway | " + COMPONENTS["edge-gateway"][1] + " |"


@pytest.mark.parametrize("cell", ["component", "layer", "zone"])
@pytest.mark.parametrize("char", [chr(0x202e), chr(0xE0041), "\x01"], ids=["bidi-override", "tag-character", "c0"])
def test_refusal_a_forbidden_character_in_a_name_it_writes_into_the_location_never_reaches_the_file(generator, tmp_path, char, cell):
    """The component, its zone and the layer are copied into ``logicalLocations`` and ``properties``. # reading: D4's exit 2 is for an input,
    and the PR 1 renderers refuse these at intake too (their scope places); a generator that only had the output backstop would exit 4, so
    either code passes. What may not happen is a write: the file holds no forbidden character, and an earlier one is as it was."""
    text = make_threats_md()
    assert E3_ROW in text
    edits = {"component": (E3_ROW, E3_ROW.replace("edge-gateway", "edge" + char + "-gateway")),
             "layer": (E3_ROW, E3_ROW.replace("L4", "L4" + char)),
             "zone": ("| Edge DMZ | Semi-trusted |", "| Edge" + char + " DMZ | Semi-trusted |")}
    old, new = edits[cell]
    project = Project(generator, tmp_path, threats_text=text.replace(old, new))
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    res = project.generate()
    assert res.code in (2, 4), res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n', "an earlier file is left as it was"


def test_cli_a_tab_and_a_newline_reference_are_not_forbidden(generator, tmp_path):
    text = make_threats_md().replace("Admin routes skip the role check.", "Admin routes\tskip the role check&#10;at every hop.")
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 0, res.describe()
    assert project.results["E-3"]["message"]["text"] == "Admin routes\tskip the role check\nat every hop."


def seeded(module, monkeypatch, error):
    """Make the emitter's self-check raise ``error``, wherever the generator reaches it from."""
    def boom(*args, **kwargs):
        raise error

    monkeypatch.setattr(sc, "self_check", boom)
    if hasattr(module, "self_check"):
        monkeypatch.setattr(module, "self_check", boom)


def test_failure_a_failed_self_check_exits_4_names_the_problem_and_replaces_no_file(generator, tmp_path, monkeypatch):
    """D4 and D8: the self-check runs before any write, and a failure fails the render (exit 4, "a completeness or parity check failed")."""
    project = Project(generator, tmp_path)
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    seeded(generator, monkeypatch, sc.SelfCheckError(["a seeded problem"]))
    res = project.generate()
    assert res.code == 4, res.describe()
    assert "seeded problem" in res.err, res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n'
    assert sorted(path.name for path in project.out.iterdir()) == ["threats.md", "threats.sarif"], "no staged file is left behind"


def test_failure_an_unexpected_error_is_the_scripts_own_defect_exit_4_with_the_error_named(generator, tmp_path, monkeypatch):
    """The shared entry's outer wrapper, as both PR 1 renderers have it: whatever raised, the run fails closed with a message."""
    project = Project(generator, tmp_path)
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    seeded(generator, monkeypatch, RuntimeError("seeded defect\x07"))
    res = project.generate()
    assert res.code == 4, res.describe()  # reading: _defect's code, in both renderers
    assert "seeded defect" in res.err and "\x07" not in res.err, res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n'


# =============================================================================
# 3. The document (ADR-050 D7; FR-E.7, FR-E.9, FR-E.12)
# =============================================================================


def test_document_is_the_shared_emitters_two_space_ascii_json(plain):
    text, document = plain.sarif_text, plain.sarif
    assert text == json.dumps(document, indent=2, ensure_ascii=True) + "\n", "the bytes are the emitter's: two spaces, ASCII, a final newline"
    assert text.isascii()
    assert document["version"] == "2.1.0" and document["$schema"] == sc.SARIF_SCHEMA_URI
    assert len(document["runs"]) == 1


def test_document_the_tool_is_Tachi_and_the_information_uri_is_real(plain):
    driver = plain.sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "Tachi", "verbatim, with a capital T"
    assert driver["informationUri"] == INFORMATION_URI
    assert driver["informationUri"] != "https://github.com/owner/tachi", "the placeholder is what FR-E.9 retires"


def test_document_no_file_carries_automation_details(plain):
    assert "automationDetails" not in plain.sarif["runs"][0] and "automationDetails" not in plain.sarif_text
    assert "runAutomationDetails" not in plain.sarif_text, "the upload step's category governs, and tachi never writes one (D7)"


def test_document_every_rule_a_result_uses_is_declared_once(plain):
    run = plain.sarif["runs"][0]
    declared = [rule["id"] for rule in run["tool"]["driver"]["rules"]]
    assert len(declared) == len(set(declared))
    assert {result["ruleId"] for result in run["results"]} <= set(declared)
    assert not [rule for rule in declared if rule in ("tachi/ai/agentic", "tachi/ai/llm")], "the short forms are never emitted (D7)"


def test_document_carries_the_provenance_stamp_of_the_generator(plain):
    stamp = plain.sarif["runs"][0]["properties"]["tachi_provenance"]
    assert list(stamp) == ["renderer", "version", "input_digest"]
    assert stamp["renderer"] == GENERATOR_NAME and stamp["version"] == tp.VERSION and DIGEST.match(stamp["input_digest"]), stamp


def test_document_the_input_digest_is_stable_for_one_input_and_changes_with_it(generator, tmp_path):
    project = Project(generator, tmp_path)
    digests = []
    for edit in (None, None, "changed"):
        if edit:
            project.threats.write_text(project.text.replace("Admin routes skip the role check.", "Admin routes skip the role check, still."),
                                       encoding="utf-8")
        assert project.generate().code == 0
        digests.append(project.sarif["runs"][0]["properties"]["tachi_provenance"]["input_digest"])
    assert digests[0] == digests[1] != digests[2], "the same input gives the same digest, and a changed one gives another (FR-E.7, NFR-2)"


# =============================================================================
# 4. One result per open finding: the N/N rule on every committed compiled threats.md (ADR-050 D8)
# =============================================================================

COMMITTED = sorted((REPO_ROOT / "examples").rglob("threats.md")) + sorted(LARGE_ARCH.rglob("threats.md"))


def committed_id(path):
    return path.relative_to(REPO_ROOT).as_posix()


def test_nn_the_committed_threat_models_are_found_so_the_cases_below_never_shrink_to_none():
    assert len(COMMITTED) >= 40
    forms = {tachi_parsers.parse_reference_set(path.read_text(encoding="utf-8"), source=path.name)["form"] for path in COMMITTED}
    assert forms == {"table", "list"}, "the table form and the list drift form are both among them (S-12)"


@pytest.mark.parametrize("path", COMMITTED, ids=committed_id)
def test_nn_one_result_per_open_finding_whatever_the_form_of_section_7(generator, tmp_path, path):
    """N/N on a compiled ``threats.md``, drift forms included: the tracked examples (the numbered-list and range forms among them,
    and a file that lists a finding twice) and every threat model that S-4's fixtures commit. Each run also passes the emitter's own
    self-check, with the groups that the shared parser reads, and every ID of Section 4c stays out."""
    text = path.read_text(encoding="utf-8")
    project = Project(generator, tmp_path, threats_text=text)
    document = generated(project)
    reference = reference_of(text)
    results = results_by(document)
    assert sorted(tp.canonical_finding_id(i) for i in results) == sorted(reference.canonical)
    assert not {tp.canonical_finding_id(i) for i in reference.resolved} & {tp.canonical_finding_id(i) for i in results}, "a RESOLVED finding is not a result"
    for result in document["runs"][0]["results"]:
        assert result["message"]["text"] and result["locations"][0]["logicalLocations"][0]["name"], "a form that lacks a value still writes a result"


def test_nn_the_gated_subset_has_42_results_42_hashes_and_distinct_keys_for_findings_that_share_a_rule_and_a_component(generator, tmp_path):
    """US-6b #2 and FR-E.2's "no two present findings share a key", at the subset's scale: it has findings that share both."""
    text = (GATED_SUBSET / "baseline" / "threats.md").read_text(encoding="utf-8")
    project = Project(generator, tmp_path, threats_text=text)
    document = generated(project)
    results = document["runs"][0]["results"]
    assert len(results) == 42 and len({r["partialFingerprints"]["primaryLocationLineHash"] for r in results}) == 42
    keys = keys_of(results)
    assert len(set(keys.values())) == 42
    sharing = {}
    for result in results:
        component = result["locations"][0]["logicalLocations"][0]["name"]
        sharing.setdefault((result["ruleId"], component), []).append(result["partialFingerprints"]["findingId/v1"])
    shared = [ids for ids in sharing.values() if len(ids) > 1]
    assert shared, "the subset has findings that share a rule and a component"
    for ids in shared:
        assert len({keys[finding_id] for finding_id in ids}) == len(ids), "distinct findings on one component and rule get separate alerts"


def test_nn_two_findings_on_one_rule_and_one_component_get_distinct_keys(generator, tmp_path):
    specs = [finding("S-1", "edge-gateway", "Shared tokens let callers impersonate each other."),
             finding("S-2", "edge-gateway", "A second spoofing path on the same gateway."),
             finding("S-3", "edge-gateway", "A third one, written to be near-identical."),
             finding("AG-1", "planner-agent", "Memory entries are trusted on later runs."),
             finding("AGP-2", "planner-agent", "Workers accept each other's instructions.")]
    project = Project(generator, tmp_path, specs=specs, resolved=[])
    results = generated(project)["runs"][0]["results"]
    assert [r["ruleId"] for r in results if r["partialFingerprints"]["findingId/v1"].startswith("S-")] == ["tachi/stride/spoofing"] * 3
    by_id = results_by(project.sarif)
    hashes = {by_id[i]["partialFingerprints"]["primaryLocationLineHash"] for i in ("S-1", "S-2", "S-3")}
    assert len(hashes) == 3, "the old (rule, component) hash gave these one alert (N12)"
    assert by_id["AG-1"]["ruleId"] == by_id["AGP-2"]["ruleId"] == "tachi/ai/agentic-threats"
    assert by_id["AG-1"]["partialFingerprints"]["primaryLocationLineHash"] != by_id["AGP-2"]["partialFingerprints"]["primaryLocationLineHash"]


# =============================================================================
# 5. What each result carries (contracts/sarif-result.md)
# =============================================================================


def test_result_each_result_carries_the_findings_own_values(plain):
    results = plain.results
    assert sorted(results) == sorted(item["id"] for item in SPECS)
    for item in SPECS:
        result = results[item["id"]]
        assert result["ruleId"] == EXPECTED_RULES[tp.canonical_finding_id(item["id"]).partition("-")[0]]
        assert result["level"] == LEVEL_OF[item["risk"]], "level keeps ADR-013 D3's mapping; it isn't identity"
        # The file's own text is the reference set's threat text, and ``markdown`` its mitigation (the template maps both, so NFR-1
        # keeps them; D8's fallback reads them back). ``text`` comes first in the key order.
        assert result["message"] == {"text": item["threat"], "markdown": mitigation_of(item)}
        assert list(result["message"]) == ["text", "markdown"]
        assert "relatedLocations" not in result, "no relatedLocations entry names a finding, and this file has no evidence (D8)"
        assert result["locations"][0]["physicalLocation"] == {"artifactLocation": {"uri": ARCHITECTURE}, "region": {"startLine": 1}}
        logical = result["locations"][0]["logicalLocations"]
        assert len(logical) == 1 and list(logical[0]) == ["name", "fullyQualifiedName", "kind"]
        assert logical[0]["name"] == item["component"]
        assert logical[0]["fullyQualifiedName"] == "%s/%s" % (item["zone"], item["component"]), "<zone>/<component>"
        assert logical[0]["kind"] in kinds_of(item["component"]), logical
        properties = result["properties"]
        assert properties["severity"] == item["risk"], "D8's fallback reads Section 7's risk level here (ruled at W3)"
        assert properties["maestro-layer"] == COMPONENTS[item["component"]][1], "the layer is Section 7's cell"
        assert properties["affected_assets"] == [], "always present, and the populator's block gives it (ADR-046 D2)"
        assert not [key for key in properties if key.startswith("correlation-")], "an uncorrelated result carries none"
        assert "baseline-run-id" not in properties, "no baseline, no key"


def test_result_the_fingerprints_are_exactly_the_hash_and_the_id_and_a_regroup_or_baseline_never_reaches_them(aware):
    for result in aware.sarif["runs"][0]["results"]:
        assert list(result["partialFingerprints"]) == ["primaryLocationLineHash", "findingId/v1"], "correlationGroup and baselineRunId moved to properties"
        for forbidden in ("guid", "correlationGuid", "fingerprints", "baselineState"):
            assert forbidden not in result, "no result carries SARIF's own %s" % forbidden


def test_result_a_resolved_finding_appears_nowhere_in_the_file(plain):
    for finding_id in RESOLVED_IDS:
        token = re.compile(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(finding_id))
        assert not token.search(plain.sarif_text), "%s is RESOLVED and appears nowhere (D8, R-30)" % finding_id


def test_result_the_affected_assets_come_from_the_populators_block_in_its_order(generator, tmp_path):
    text = make_threats_md().replace("| S-2 | [] |", "| S-2 | [auth, secrets] |").replace("| T-1 | [] |", "| T-1 | [pii] |")
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    results = project.results
    assert results["S-2"]["properties"]["affected_assets"] == ["auth", "secrets"]
    assert results["T-1"]["properties"]["affected_assets"] == ["pii"]
    assert results["E-3"]["properties"]["affected_assets"] == []


def test_result_with_no_affected_assets_block_every_result_still_carries_the_empty_list(generator, tmp_path):
    project = Project(generator, tmp_path, affected="missing")
    generated(project)
    assert all(result["properties"]["affected_assets"] == [] for result in project.results.values())


def test_result_a_component_that_section_2_does_not_list_gets_the_application_zone_and_the_process_kind(generator, tmp_path):
    specs = [finding("S-1", "edge-gateway", "A listed component."), finding("S-2", "edge-gateway", "An unlisted one.")]
    text = make_threats_md(specs, []).replace("| S-2 | NEW | Spoofing | " + DASH + " | edge-gateway |", "| S-2 | NEW | Spoofing | " + DASH + " | unlisted-service |")
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    logical = project.results["S-2"]["locations"][0]["logicalLocations"][0]
    assert logical == {"name": "unlisted-service", "fullyQualifiedName": "Application Zone/unlisted-service", "kind": "process"}


def test_result_the_zone_is_section_2s_spelling_layer_note_included_and_matched_by_name_case_folded(generator, tmp_path):
    """sarif-result.md: ``<zone>`` is the zone of the Section 2 row that lists the component, by name, case-folded, as Section 2 writes it."""
    text = make_threats_md().replace("| Edge DMZ | Semi-trusted | edge-gateway, auth-broker |", "| Edge DMZ (L4) | Semi-trusted | Edge-Gateway, auth-broker |")
    assert "Edge DMZ (L4)" in text
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    logical = project.results["S-2"]["locations"][0]["logicalLocations"][0]
    assert logical["name"] == "edge-gateway" and logical["fullyQualifiedName"] == "Edge DMZ (L4)/edge-gateway"


def test_reading_the_cells_are_decoded_once_from_d3s_references(generator, tmp_path):
    """From PR 2 on ``threats.md`` is rendered text (S1P cross-read), so a cell may hold D3's references: the readers decode them once."""
    hostile = tp.escape_cell(HOSTILE_THREAT)
    assert "&lt;b&gt;" in hostile and "&#96;" in hostile and "&#123;" in hostile
    specs = [finding("S-1", "edge-gateway", hostile, status="NEW"),
             finding("S-2", "edge-gateway", tp.escape_cell("Write &lt; and a pipe | and a tilde ~ and a hash # as written."), status="NEW")]
    project = Project(generator, tmp_path, specs=specs, resolved=[])
    generated(project)
    results = project.results
    assert results["S-1"]["message"]["text"] == HOSTILE_THREAT
    assert results["S-2"]["message"]["text"] == "Write &lt; and a pipe | and a tilde ~ and a hash # as written.", "decoded once, never twice"


def test_reading_gfms_escaped_pipe_is_a_pipe_in_its_cell(generator, tmp_path):
    text = make_threats_md().replace("Admin routes skip the role check.", "Admin routes skip the role check \\| at every hop.")
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    assert project.results["E-3"]["message"]["text"] == "Admin routes skip the role check | at every hop."


def test_reading_the_file_reads_back_through_the_fallback_reader_as_the_same_findings(aware):
    """D8's fallback reads ``threats.sarif`` when the markdown is absent: members, groups and each member's component, text, level,
    layer and kind come back as the file wrote them (``properties.severity`` is where the level goes, ruled at W3)."""
    reference = reference_of(aware.text)
    read = tachi_parsers.parse_sarif_member_set(aware.sarif_text, with_details=True)
    assert sorted(read["members"], key=tp.finding_sort_key) == sorted(reference.canonical, key=tp.finding_sort_key)
    assert read["groups"] == tachi_parsers.parse_correlation_groups(aware.text, reference.canonical)["groups"], \
        "the correlation properties are Section 4a's groups"
    for item in SPECS:
        details = read["details"][tp.canonical_finding_id(item["id"])]
        assert details["component"] == item["component"] and details["risk_level"] == item["risk"]
        assert details["layer"] == COMPONENTS[item["component"]][1] and details["mitigation"] == mitigation_of(item)
        assert details["threat"].startswith(item["threat"]) and details["kind"] in kinds_of(item["component"])


# =============================================================================
# 6. Membership: RESOLVED findings, repeated findings and what the reference set reads (ADR-050 D8)
# =============================================================================


def test_membership_a_resolved_finding_is_not_a_result_a_reference_or_a_property_value(aware):
    ids = set(aware.results)
    assert not {tp.canonical_finding_id(i) for i in ids} & {tp.canonical_finding_id(i) for i in RESOLVED_IDS}
    for result in aware.sarif["runs"][0]["results"]:
        assert "relatedLocations" not in result
        for key, value in result["properties"].items():
            assert not re.search(r"(?<![A-Za-z0-9-])(S-1|T-3|LLM-2)(?![A-Za-z0-9-])", json.dumps(value)), (result["partialFingerprints"]["findingId/v1"], key)


def test_membership_a_mention_of_a_resolved_finding_in_copied_text_is_not_a_reference(generator, tmp_path):
    """D8, ruled at W3: ``message.text`` and ``message.markdown`` are copied text, and an ID in them is a mention. The run stays clean
    and the ID still appears in no ``findingId/v1`` and no property."""
    text = make_threats_md().replace("Shared tokens let callers impersonate each other.", "Shared tokens let callers impersonate each other, as S-1 once did.")
    text = text.replace("Mitigation text for T-1.", "Mitigation text for T-1, which also closed T-3.")
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    results = project.results
    assert "as S-1 once did" in results["S-2"]["message"]["text"] and "also closed T-3" in results["T-1"]["message"]["markdown"]
    assert "S-1" not in results and "T-3" not in results
    assert not [r for r in results.values() if re.search(r"\bS-1\b|\bT-3\b", json.dumps(r["properties"]))]


def test_membership_a_finding_that_section_7_lists_twice_is_one_result_and_the_first_row_wins(generator, tmp_path):
    text = make_threats_md(repeated=[("S-2", "client-portal")])
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 0, res.describe()  # reading: the generator's codes are 0, 1, 2 and 4 (cli.md), so the repeat is a stderr matter at most
    results = project.results
    assert len(results) == len(SPECS)
    only = results["S-2"]
    assert only["message"]["text"] == "Shared tokens let callers impersonate each other."
    assert only["locations"][0]["logicalLocations"][0]["name"] == "edge-gateway"


def test_membership_a_group_names_the_open_findings_only_and_the_sentence_names_no_resolved_id(generator, tmp_path):
    groups = [("CG-1", ["S-2", "S-1", "T-1"])]  # S-1 is RESOLVED: Section 4c lists it
    project = Project(generator, tmp_path, groups=groups)
    generated(project)
    results = project.results
    assert message_parts(results["S-2"]["message"]["text"])[1] == ruling_c("CG-1", "S-2", ["T-1"])
    assert message_parts(results["T-1"]["message"]["text"])[1] == ruling_c("CG-1", "S-2")
    assert "S-1" not in project.sarif_text.replace("S-10", "")


def test_membership_the_claim_rule_and_a_finding_that_two_groups_list_exits_0_and_reports_nothing_more(generator, tmp_path):
    """The maestro-reference sample lists AG-7 in CG-1 and CG-2. CG-1 claims it and CG-2 falls away, so E-7 carries nothing. The generator
    applies the rule and reports nothing more (S1P-A19: ``check-threat-model.py`` makes that report once, so the codes stay 0, 1, 2 and 4)."""
    text = (REPO_ROOT / "examples" / "maestro-reference" / "threats.md").read_text(encoding="utf-8")
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 0, res.describe()
    assert "correlation-member-repeated" not in res.err and "correlation-member-repeated" not in res.out
    results = project.results
    assert results["AG-7"]["properties"]["correlation-group"] == "CG-1"
    assert results["E-7"]["properties"].get("correlation-group") is None
    assert message_parts(results["E-7"]["message"]["text"])[1] is None


def test_membership_the_drift_forms_are_read_where_the_value_is_not_in_the_form(generator, tmp_path):
    """The numbered-list form carries no component, threat or status. The generator still writes one result for each finding and the
    values it has: the level the subheading names. # reading: the placeholder strings are open (the scorer's are `Unspecified` and
    `No threat description.`); a result needs non-empty text because the emitter refuses an empty one."""
    text = (REPO_ROOT / "examples" / "consumer-agent-app" / "sample-report" / "threats.md").read_text(encoding="utf-8")
    reference = reference_of(text)
    assert tachi_parsers.parse_reference_set(text)["form"] == "list"
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    results = project.results
    levels = {tp.canonical_finding_id(row["id"]): row["risk_level"] for row in reference.rows}
    assert levels["TE-5"] == "Critical" and results["TE-5"]["level"] == "error" and results["TE-5"]["properties"]["severity"] == "Critical"
    assert results["S-2"]["level"] == "warning" and results["R-2"]["level"] == "note"


# =============================================================================
# 7. Correlation: the properties, the groups and ruling C's sentence (ADR-050 D8; the full cap cases are test_sarif_identity.py's)
# =============================================================================


def test_correlation_each_member_carries_its_group_its_role_and_its_primary_and_nothing_else_does(aware):
    results = aware.results
    expected = {"S-2": ("CG-1", "primary", "S-2"), "S-10": ("CG-1", "peer", "S-2"), "T-1": ("CG-1", "peer", "S-2"),
                "E-3": ("CG-2", "primary", "E-3"), "E-5": ("CG-2", "peer", "E-3")}
    for finding_id, result in results.items():
        properties = result["properties"]
        got = tuple(properties.get(key) for key in sc.CORRELATION_KEYS)
        assert got == expected.get(finding_id, (None, None, None)), finding_id
        if finding_id not in expected:
            assert not [key for key in properties if key.startswith("correlation-")]


def test_correlation_each_correlated_result_ends_with_ruling_cs_sentence_and_the_rest_do_not(aware):
    results = aware.results
    sentences = {"S-2": ruling_c("CG-1", "S-2", ["S-10", "T-1"]), "S-10": ruling_c("CG-1", "S-2"), "T-1": ruling_c("CG-1", "S-2"),
                 "E-3": ruling_c("CG-2", "E-3", ["E-5"]), "E-5": ruling_c("CG-2", "E-3")}
    for item in SPECS:
        own, sentence = message_parts(results[item["id"]]["message"]["text"])
        assert sentence == sentences.get(item["id"]), item["id"]
        assert own == item["threat"], "the file's own text comes first, then one space and the sentence"
        assert results[item["id"]]["message"]["markdown"] == mitigation_of(item), "ruling C's sentence goes on text alone"


def test_correlation_a_regroup_changes_the_text_and_never_a_key(generator, tmp_path):
    first = Project(generator, tmp_path / "a", groups=FIRST_GROUPS)
    second = Project(generator, tmp_path / "b", groups=[("CG-1", ["T-1", "S-2"]), ("CG-3", ["S-10", "E-3", "AG-1"])])
    keys, texts = [], []
    for project in (first, second):
        generated(project)
        keys.append(keys_of(project.sarif["runs"][0]["results"]))
        texts.append({i: r["message"]["text"] for i, r in project.results.items()})
    assert keys[0] == keys[1], "a new primary and a dissolved group leave every key alone"
    assert texts[0]["T-1"] != texts[1]["T-1"] and texts[0]["E-5"] != texts[1]["E-5"]
    assert texts[0]["R-1"] == texts[1]["R-1"], "an uncorrelated finding's text doesn't change"


# =============================================================================
# 8. Identity: the regroup pair, an unchanged re-run and baseline-run-id (US-6b; FR-E.2; ADR-050 D7)
# =============================================================================


@pytest.fixture(scope="module")
def outcomes():
    return json.loads((PAIR / "expected-outcomes.json").read_text(encoding="utf-8"))


def copy_pair(root):
    """The scenario, copied: the three runs are generated beside their own ``threats.md`` (``--out run1``, ``run2``, ``run3``)."""
    scenario = Path(root) / "pair"
    shutil.copytree(str(PAIR), str(scenario))
    return scenario


def generate_pair(generator_module, scenario, plant=None):
    """Run the generator on run1, run2 and run3 in order. ``plant(scenario, name)``, when given, runs before each one."""
    runs = {}
    for name in ("run1", "run2", "run3"):
        if plant is not None:
            plant(scenario, name)
        res = invoke(generator_module, ["--threats", scenario / name / "threats.md", "--out", scenario / name,
                                        "--architecture", "architecture/architecture.md"], scenario)
        assert res.code == 0, res.describe()
        text = (scenario / name / SARIF).read_text(encoding="utf-8")
        threats = (scenario / name / "threats.md").read_text(encoding="utf-8")
        document = json.loads(text)
        runs[name] = SimpleNamespace(text=text, document=document, results=results_by(document), threats=threats,
                                     reference=reference_of(threats), res=res)
    return runs


@pytest.fixture(scope="module")
def pair(generator, tmp_path_factory):
    return generate_pair(generator, copy_pair(tmp_path_factory.mktemp("pair")))


def test_identity_the_regroup_pair_keeps_every_key_and_drops_none(pair, outcomes):
    """US-6b #1: run 2 regroups carried findings and changes a primary, with a NEW peer and an UPDATED one. Every carried finding keeps
    its run-1 key, and none drops out. Run 3 is the unchanged re-run of run 2's input."""
    keys = {name: keys_of(run.document["runs"][0]["results"]) for name, run in pair.items()}
    for name, run in pair.items():
        assert set(keys[name]) == set(outcomes["runs"][name]["findings"]), "%s holds the fixture's findings" % name
        assert len(set(keys[name].values())) == len(keys[name]), "no two present findings share a key (the F-012 lesson)"
    assert set(keys["run1"]) < set(keys["run2"]) and set(keys["run2"]) - set(keys["run1"]) == {"D-1"}, "no carried finding drops out"
    for finding_id, key in keys["run1"].items():
        assert keys["run2"][finding_id] == key, "%s keeps its key across the regroup" % finding_id
    assert keys["run3"] == keys["run2"], "an unchanged re-run's keys are identical"


def test_identity_the_regroup_changes_roles_and_sentences_and_leaves_a_carried_findings_own_text(pair):
    run1, run2, run3 = pair["run1"].results, pair["run2"].results, pair["run3"].results
    role = lambda results, finding_id: results[finding_id]["properties"].get("correlation-role")  # noqa: E731
    assert role(run1, "I-1") == "primary" and role(run2, "I-1") == "peer", "I-1 was CG-1's primary and is now T-1's peer"
    assert role(run1, "T-1") is None and role(run2, "T-1") == "primary", "T-1 was ungrouped and is now the primary"
    assert role(run1, "E-1") is None and role(run2, "E-1") == "peer" and "D-1" not in run1 and role(run2, "D-1") == "peer"
    assert role(run1, "R-1") == role(run2, "R-1") == "primary", "CG-2 is unchanged"
    for finding_id in run1:
        own_1, own_2 = message_parts(run1[finding_id]["message"]["text"])[0], message_parts(run2[finding_id]["message"]["text"])[0]
        assert own_1 == own_2, "%s: a regroup changes the sentence and never the file's own text" % finding_id
    for finding_id in ("T-1", "I-1", "LLM-1", "E-1"):
        assert run1[finding_id]["message"]["text"] != run2[finding_id]["message"]["text"], "%s: its group changed, so its text did (ruling C)" % finding_id
    assert {i: r["message"]["text"] for i, r in run3.items()} == {i: r["message"]["text"] for i, r in run2.items()}


def test_identity_the_pairs_baseline_run_id_is_each_carried_findings_baseline_and_empty_for_a_new_one(pair):
    for name, run in pair.items():
        for finding_id, result in run.results.items():
            status = run.reference.status[tp.canonical_finding_id(finding_id)]
            expected = "" if status == "NEW" else "2026-11-09T10-00-00"
            assert result["properties"]["baseline-run-id"] == expected, (name, finding_id, status)
        assert "baselineRunId" not in run.text and "correlationGroup" not in run.text, "both moved to properties (D7)"


def test_identity_an_unchanged_rerun_of_the_generator_keeps_its_keys_and_its_bytes(generator, tmp_path):
    project = Project(generator, tmp_path, groups=FIRST_GROUPS)
    generated(project)
    first = project.sarif_path.read_bytes()
    assert project.generate().code == 0
    assert project.sarif_path.read_bytes() == first, "the same input gives the same bytes (NFR-2)"


def test_identity_a_rescore_a_new_component_and_a_new_threat_text_leave_the_key_alone(generator, tmp_path):
    """D7: the hash is a function of the tool and the ID alone, so an UPDATED finding's new component, a re-score and new prose re-key
    nothing. The file's text, level, location and properties may all change, and its identity fields may not."""
    first = Project(generator, tmp_path / "a", groups=FIRST_GROUPS)
    generated(first)
    text = first.text
    row = "| E-3 | NEW | Elevation of Privilege | " + DASH + " | edge-gateway |"
    assert row in text
    text = text.replace(row, "| E-3 | UPDATED | Elevation of Privilege | " + DASH + " | auth-broker |")
    text = text.replace("Admin routes skip the role check.", "Admin routes skip the role check, and so do the audit routes.")
    text = text.replace("| Admin routes skip the role check, and so do the audit routes. | High |",
                        "| Admin routes skip the role check, and so do the audit routes. | Critical |")
    assert "audit routes. | Critical |" in text
    second = Project(generator, tmp_path / "b", groups=FIRST_GROUPS, threats_text=text)
    generated(second)
    changed, kept = first.results["E-3"], second.results["E-3"]
    assert changed["locations"][0]["logicalLocations"][0]["name"] == "edge-gateway"
    assert kept["locations"][0]["logicalLocations"][0]["name"] == "auth-broker" and kept["level"] == "error" and changed["level"] == "error"
    assert kept["properties"]["severity"] == "Critical" and changed["properties"]["severity"] == "High"
    assert kept["message"]["text"] != changed["message"]["text"]
    assert keys_of(second.sarif["runs"][0]["results"]) == keys_of(first.sarif["runs"][0]["results"]), "no key moved"


def test_identity_the_generators_bytes_do_not_depend_on_an_earlier_file_in_the_run_directory(generator, tmp_path):
    project = Project(generator, tmp_path, groups=FIRST_GROUPS)
    generated(project)
    clean = project.sarif_path.read_bytes()
    legacy = (GATED_SUBSET / "baseline" / "threats.sarif").read_bytes()
    project.sarif_path.write_bytes(legacy)  # a model-authored file from an older run, with hashes of its own
    assert project.generate().code == 0
    assert project.sarif_path.read_bytes() == clean, "an earlier threats.sarif is replaced, never read"


def test_baseline_run_id_is_a_property_empty_for_a_new_finding_and_never_a_fingerprint(aware):
    for item in SPECS:
        result = aware.results[item["id"]]
        expected = "" if item["status"] == "NEW" else BASELINE_RUN_ID
        assert result["properties"]["baseline-run-id"] == expected, item["id"]
        assert list(result["partialFingerprints"]) == ["primaryLocationLineHash", "findingId/v1"]
    assert "baselineRunId" not in aware.sarif_text, "today's partialFingerprints key is gone: it changes on every re-assessment (D7)"


def test_baseline_the_gated_subset_names_its_baseline_run(generator, tmp_path):
    text = (GATED_SUBSET / "baseline" / "threats.md").read_text(encoding="utf-8")
    run_id = tachi_parsers.parse_baseline_frontmatter(text)["run_id"]
    assert run_id == "2026-09-21T09-12-00"
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    reference = reference_of(text)
    counted = {"": 0, run_id: 0}
    for finding_id, result in project.results.items():
        value = result["properties"]["baseline-run-id"]
        assert value == ("" if reference.status[tp.canonical_finding_id(finding_id)] == "NEW" else run_id), finding_id
        counted[value] += 1
    new = sum(1 for status in reference.status.values() if status == "NEW")
    assert 0 < new < 42 and counted == {"": new, run_id: 42 - new}, "the subset has NEW findings and carried ones, and every carried one names the run"


def baseline_expectation(text):
    """``None`` when the file names no baseline run (a case can say nothing), ``False`` for a first run, else the run ID."""
    baseline = tachi_parsers.parse_baseline_frontmatter(text)
    if baseline["run_id"]:
        return baseline["run_id"]
    return False if baseline["source"] is None else None


@pytest.mark.parametrize("path", COMMITTED, ids=committed_id)
def test_baseline_run_id_on_every_committed_threat_model(generator, tmp_path, path):
    """First runs carry no ``baseline-run-id``. A baseline-aware file's UNCHANGED and UPDATED findings carry its baseline's run ID,
    and its NEW ones the empty string. # reading: a file whose Status column is absent, or whose baseline names no run, says nothing."""
    text = path.read_text(encoding="utf-8")
    expected = baseline_expectation(text)
    reference = reference_of(text)
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    for finding_id, result in project.results.items():
        value = result["properties"].get("baseline-run-id")
        status = reference.status[tp.canonical_finding_id(finding_id)]
        if expected is False:
            assert value is None, (finding_id, "a first run has no baseline run to name")
        elif expected and status:
            assert value == ("" if status == "NEW" else expected), (finding_id, status)


# =============================================================================
# 9. The architecture path (ADR-050 D7; the carrier chain, case by case, is test_sarif_identity.py's section 22)
# =============================================================================


def test_uri_the_flag_is_resolved_in_code_so_an_absolute_path_becomes_the_repo_relative_spelling(generator, tmp_path):
    project = Project(generator, tmp_path)
    res = project.generate(architecture=str(project.architecture))
    assert res.code == 0, res.describe()
    assert {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.results.values()} == {ARCHITECTURE}
    assert res.err == ""


def test_uri_a_candidate_that_fails_a_check_falls_back_with_a_warning_and_the_run_goes_on(generator, tmp_path):
    project = Project(generator, tmp_path)
    res = project.generate(architecture="docs/security/../../elsewhere.md")
    assert res.code == 0, res.describe()  # nothing in D7 stops a run, and the generator has no warning code
    assert {r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for r in project.results.values()} == {ARCHITECTURE}
    expected = sc.resolve_architecture("docs/security/../../elsewhere.md", threats_text=project.text, run_dir=str(project.out), root=str(tmp_path))
    assert expected.warnings and expected.source == "default"
    for warning in expected.warnings:
        assert warning["code"] in res.err or warning["detail"] in res.err, "each warning is on stderr: %s" % warning["code"]


# =============================================================================
# 10. The write (ADR-050 D4: only shipped steps write canonical files, atomically, after full validation)
# =============================================================================


def test_write_a_run_adds_threats_sarif_under_out_and_changes_nothing_else(generator, tmp_path):
    project = Project(generator, tmp_path)
    before = tree_state(project.root)
    assert project.generate().code == 0
    after = tree_state(project.root)
    assert {path for path in after if after.get(path) != before.get(path)} == {"run/threats.sarif"}, "the declared-paths check sees one new file"
    assert sorted(path.name for path in project.out.iterdir()) == ["threats.md", "threats.sarif"], "no staged or temporary file is left behind"


def test_write_a_later_run_replaces_an_earlier_file_whole(generator, tmp_path):
    project = Project(generator, tmp_path)
    project.sarif_path.write_text("a file that is far longer than the next one will be " * 4000, encoding="utf-8")
    assert project.generate().code == 0
    json.loads(project.sarif_text)  # whole and valid: nothing of the earlier file remains


@pytest.mark.parametrize("failure", ["missing-input", "no-section-7", "forbidden-character"])
def test_write_a_refused_input_leaves_an_earlier_file_as_it_was(generator, tmp_path, failure):
    project = Project(generator, tmp_path)
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    if failure == "missing-input":
        project.threats.unlink()
    elif failure == "no-section-7":
        project.threats.write_text(project.text.replace("## 7. Recommended Actions", "## 7. Something Else"), encoding="utf-8")
    else:
        project.threats.write_text(project.text.replace("Admin routes skip the role check.", "Admin routes" + chr(0x202e) + " skip the role check."), encoding="utf-8")
    assert project.generate().code in (1, 2)
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n'
    assert sorted(path.name for path in project.out.iterdir()) in (["threats.sarif"], ["threats.md", "threats.sarif"])


# =============================================================================
# 11. The module: the guard, the entry's shape and the pieces that don't survive (ADR-049 D8; ADR-050 D1, D16)
# =============================================================================

SOURCE = GENERATOR


def parsed():
    return ast.parse(SOURCE.read_text(encoding="utf-8"))


def test_module_the_bytecode_guard_comes_before_every_local_import():
    body = parsed().body
    guard = [i for i, node in enumerate(body)
             if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "sys.dont_write_bytecode"]
    assert guard, "the entry sets sys.dont_write_bytecode (contracts/cli.md, ADR-049 D8)"
    local = [i for i, node in enumerate(body)
             if (isinstance(node, ast.Import) and any(alias.name.split(".")[0].startswith(("tachi_", "sarif_")) for alias in node.names))
             or (isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0].startswith(("tachi_", "sarif_")))]
    assert local, "it imports the shared emitter and the parsers"
    assert guard[0] < min(local) and body[guard[0]].value.value is True


def test_module_the_entrys_work_is_in_main_with_an_argv_behind_a_thin_guard():
    tree = parsed()
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    assert [arg.arg for arg in main.args.args] == ["argv"] and len(main.args.defaults) == 1, "main(argv=None)"
    assert ast.dump(main.args.defaults[0]) == ast.dump(ast.Constant(value=None))
    guard = tree.body[-1]
    assert isinstance(guard, ast.If) and "__main__" in ast.unparse(guard.test), "the last statement is the __main__ guard"
    assert len(guard.body) == 1 and "main(" in ast.unparse(guard.body[0]), "thin: one statement that calls main"


def test_module_the_retired_pieces_are_gone_and_the_shared_emitter_is_used():
    """ADR-050 D7: ``generate-threats-sarif.py``'s ``md5`` hash and its ``artifact_uri_for`` don't survive, and the legacy short-form
    rule map goes with its last user (contracts/sarif-result.md)."""
    tree = parsed()
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} | {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names}
    assert not functions & {"artifact_uri_for", "line_hash_for"}, functions
    assert not {"md5", "PREFIX_TO_RULE"} & (names | imported), "the md5 hash and the legacy short-form rule map are not used"
    assert {"build_result", "self_check"} <= names | imported, "results come from the shared emitter, and its self-check runs before the write"
    assert "resolve_architecture" in names | imported, "the URI is resolved in code (D7)"


def test_module_it_reads_no_clock_no_random_and_loads_no_yaml():
    tree = parsed()
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not attributes & {"today", "now", "utcnow", "time", "monotonic", "random", "randint", "shuffle"}, "the bytes depend on the input alone (NFR-2)"
    imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imports |= {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not imports & {"yaml", "random"}, imports


def test_module_a_fresh_interpreter_runs_it_writes_the_same_bytes_and_leaves_no_bytecode(generator, tmp_path):
    """What a process alone shows (H15): the script runs as a script, with the interpreter's bytecode writing on, and nothing under the
    copied scripts or the project is compiled (ADR-049 D8), because the guard precedes every local import. The file it writes is the
    one the in-process run wrote, so nothing in the bytes comes from the interpreter's state."""
    project = Project(generator, tmp_path / "project", groups=FIRST_GROUPS)
    assert project.generate().code == 0
    in_process = project.sarif_path.read_bytes()
    copied = tmp_path / "scripts"
    copied.mkdir()
    for path in SCRIPTS_DIR.glob("*.py"):
        shutil.copyfile(str(path), str(copied / path.name))
    project.sarif_path.unlink()
    env = {key: value for key, value in os.environ.items() if key != "PYTHONDONTWRITEBYTECODE"}
    done = subprocess.run([sys.executable, str(copied / GENERATOR_NAME), "--threats", str(project.threats), "--out", str(project.out),
                           "--architecture", ARCHITECTURE], cwd=str(project.root), env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr
    assert project.sarif_path.read_bytes() == in_process
    assert not list(tmp_path.rglob("*.pyc")) and not list(tmp_path.rglob("__pycache__")), "no bytecode is written (ADR-049 D8)"
    version = subprocess.run([sys.executable, str(copied / GENERATOR_NAME), "--version"], cwd=str(tmp_path), env=env, capture_output=True,
                             text=True, timeout=120)
    assert version.returncode == 0 and tp.VERSION in version.stdout + version.stderr


# =============================================================================
# 12. The property set, the rules and the readings that T100 adds (S1P-A28; sarif-specification.md's non-identity text)
# =============================================================================
#
# ``contracts/sarif-result.md`` holds this file's exact property set: the keys that its own contract names (``sarif-specification.md``'s
# non-identity text and the orchestrator's Phase 4 rules), and no other. Sections 1 to 11 pin what T099 could pin before the script. These cases
# pin the rest of what the generator writes: that set, the tags, the placeholders of a drift form, the driver, its rules and its taxonomies,
# and the readings that only stderr and the exit code show. Each states its source, and none reads the script's own tables.

CONTRACTED_KEYS = {"tags", "maestro-layer", "severity", "baselineState", "affected_assets"}
DROPPED_KEYS = ("likelihood", "impact", "owasp_id", "maestro-pattern", "asi07_emission", "feature", "pattern_category")  # no contract names them (PM W3 ruling 2)
SECURITY_SEVERITY = {"Critical": 9.0, "High": 8.0, "Medium": 5.0, "Low": 2.0, "Note": 0.1}  # sarif-specification.md's severity table
UNKNOWN_RISK_SEVERITY = 5.0  # a risk level that is none of the five words counts as a Medium, the ``warning`` that level_for_band gives it


def test_properties_a_result_holds_exactly_the_keys_its_contract_names(plain, aware):
    """S1P-A28, the one case that pins the exact set. A first-run result holds the five keys that this file's own contract names. A baseline-aware
    result adds ``baseline-run-id``, and a group member the emitter's three ``correlation-*`` keys. ``likelihood``, ``impact``, ``owasp_id``, the
    ``maestro-pattern`` property and AG-8's three markers, which no contract names, are written nowhere."""
    for result in plain.results.values():
        assert set(result["properties"]) == CONTRACTED_KEYS
    members = {"S-2", "S-10", "T-1", "E-3", "E-5"}
    for finding_id, result in aware.results.items():
        expected = CONTRACTED_KEYS | {"baseline-run-id"} | (set(sc.CORRELATION_KEYS) if finding_id in members else set())
        assert set(result["properties"]) == expected, finding_id
    for result in list(plain.results.values()) + list(aware.results.values()):
        assert not [key for key in DROPPED_KEYS if key in result["properties"]]


def test_properties_baselineState_follows_the_status_in_a_baseline_aware_run_and_is_new_in_a_run_with_no_baseline(plain, aware):
    """S1P-A28: ``new``, ``unchanged`` or ``updated`` from the finding's status, and ``new`` on every result of a run with no baseline, whatever
    a row says. ``absent`` never occurs, because RESOLVED findings are no result (D8). It lives in ``properties``: SARIF's own key stays forbidden."""
    word = {"NEW": "new", "UPDATED": "updated", "UNCHANGED": "unchanged"}
    assert {item["status"] for item in SPECS} == set(word), "the project holds all three statuses, so the two runs below differ"
    for item in SPECS:
        assert aware.results[item["id"]]["properties"]["baselineState"] == word[item["status"]], item["id"]
        assert plain.results[item["id"]]["properties"]["baselineState"] == "new", item["id"]
    assert not [r for r in list(plain.results.values()) + list(aware.results.values()) if "baselineState" in r]


@pytest.mark.parametrize("example", ["consumer-agent-app/sample-report", "predictive-ml-app/sample-report"])
def test_properties_a_drift_form_gives_baselineState_new_and_the_placeholders_for_what_it_lacks(generator, tmp_path, example):
    """S1P-A28 ("for a finding whose form gives no status") and the placeholders (``module-signatures.md``): the numbered-list form carries no
    status, component or threat. Each of its results is new, in the component ``Unspecified`` with ``No threat description.``, where the shared
    emitter's own fallbacks apply (the application zone and the process kind). The file still has one result for each finding."""
    text = (REPO_ROOT / "examples" / example / "threats.md").read_text(encoding="utf-8")
    assert tachi_parsers.parse_reference_set(text)["form"] == "list"
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    assert len(project.results) > 10
    for finding_id, result in project.results.items():
        assert result["properties"]["baselineState"] == "new", finding_id
        assert result["locations"][0]["logicalLocations"] == [{"name": "Unspecified", "fullyQualifiedName": "Application Zone/Unspecified", "kind": "process"}]
        assert message_parts(result["message"]["text"])[0] == "No threat description.", finding_id


def test_properties_the_tags_are_the_category_tags_then_the_layer_then_the_pattern(generator, tmp_path):
    """S1P-A28: ``security``, then ``stride`` or ``ai``, then the category's own tag, as the generator has always written them, with ``TE`` taking
    ``AG``'s plus ``human-trust-exploitation``; then ``maestro-layer:<L1 to L7, or Unclassified>``; then ``maestro-pattern:<value>`` when the
    pattern isn't ``none`` (``multiple`` included). All twelve prefixes, written out here from the contract."""
    category = {
        "S": ["security", "stride", "spoofing"], "T": ["security", "stride", "tampering"], "R": ["security", "stride", "repudiation"],
        "I": ["security", "stride", "information-disclosure"], "D": ["security", "stride", "denial-of-service"],
        "E": ["security", "stride", "elevation-of-privilege"], "AG": ["security", "ai", "agentic"],
        "AGP": ["security", "ai", "agentic", "agentic-pattern"], "TE": ["security", "ai", "agentic", "human-trust-exploitation"],
        "LLM": ["security", "ai", "llm"], "OI": ["security", "ai", "llm", "output-integrity"], "MI": ["security", "ai", "llm", "misinformation"]}
    assert set(category) == set(tp.FINDING_PREFIXES)
    specs = [finding("%s-1" % prefix, "planner-agent", "A threat for %s." % prefix) for prefix in category]
    specs.append(finding("S-2", "planner-agent", "A finding that no layer reaches."))
    text = make_threats_md(specs, [])
    patterns = {"AG-1": "trust_exploitation", "TE-1": "multiple"}
    for finding_id, pattern in patterns.items():
        row = "| %s | NEW | %s | %s |" % (finding_id, CATEGORY_NAME[finding_id.partition("-")[0]], DASH)
        assert row in text
        text = text.replace(row, row.replace(DASH, pattern))
    row = "| S-2 | NEW | Spoofing | %s | planner-agent | %s |" % (DASH, COMPONENTS["planner-agent"][1])
    assert row in text
    text = text.replace(row, "| S-2 | NEW | Spoofing | %s | unlisted-service |  |" % DASH)  # a component that Section 1 doesn't list, and no layer cell
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    for prefix, tags in category.items():
        finding_id = "%s-1" % prefix
        extra = ["maestro-pattern:" + patterns[finding_id]] if finding_id in patterns else []
        assert project.results[finding_id]["properties"]["tags"] == tags + ["maestro-layer:L3"] + extra, prefix
    unclassified = project.results["S-2"]["properties"]
    assert unclassified["tags"] == category["S"] + ["maestro-layer:Unclassified"] and unclassified["maestro-layer"] == "Unclassified"


def test_rules_one_for_each_category_with_a_result_with_its_help_and_the_highest_severity_among_its_results(plain):
    """``sarif-specification.md``, "Rule Definition Templates": only the categories that have a result get a rule, each with ``help`` and a
    ``security-severity`` that is the highest value among its findings, by the severity table. The shared rule table's order of keys
    (``id``, the two descriptions, ``help``, ``properties``, ``relationships``) is the order of every shipped ``threats.sarif``."""
    expected = {}
    for item in SPECS:
        rule = EXPECTED_RULES[tp.canonical_finding_id(item["id"]).partition("-")[0]]
        expected[rule] = max(expected.get(rule, 0.0), SECURITY_SEVERITY[item["risk"]])
    rules = plain.sarif["runs"][0]["tool"]["driver"]["rules"]
    assert [rule["id"] for rule in rules] and {rule["id"] for rule in rules} == set(expected) and len(rules) == len(expected)
    assert "tachi/stride/information-disclosure" not in expected, "the project has no such finding, so it has no such rule"
    for rule in rules:
        assert list(rule) == ["id", "shortDescription", "fullDescription", "help", "properties", "relationships"], rule["id"]
        assert sorted(rule["help"]) == ["markdown", "text"] and rule["help"]["text"] and rule["help"]["markdown"], rule["id"]
        assert list(rule["properties"]) == ["tags", "security-severity"] and rule["properties"]["tags"][0] == "security", rule["id"]
        assert rule["properties"]["security-severity"] == "%.1f" % expected[rule["id"]], rule["id"]
        assert rule["relationships"], rule["id"]


def test_rules_a_finding_with_no_risk_level_is_a_warning_and_counts_as_a_medium(generator, tmp_path):
    """A form that names no risk level (the numbered list under no priority subheading) has no word for ``level`` or for its rule. The shared
    emitter's default for an unknown band is ``warning``, and the rule counts such a finding as a Medium, the severity that ``warning`` has.
    # reading: no contract names a default for a blank risk level. The retired generator wrote ``note``; this one takes the shared helper's."""
    text = (REPO_ROOT / "examples" / "predictive-ml-app" / "sample-report" / "threats.md").read_text(encoding="utf-8")
    project = Project(generator, tmp_path, threats_text=text)
    generated(project)
    blank = {finding_id: result for finding_id, result in project.results.items() if result["properties"]["severity"] == ""}
    assert blank and all(result["level"] == "warning" for result in blank.values())
    highest = {}
    for result in project.results.values():
        value = SECURITY_SEVERITY.get(result["properties"]["severity"], UNKNOWN_RISK_SEVERITY)
        highest[result["ruleId"]] = max(highest.get(result["ruleId"], 0.0), value)
    for rule in project.sarif["runs"][0]["tool"]["driver"]["rules"]:
        assert float(rule["properties"]["security-severity"]) == highest[rule["id"]], rule["id"]


def test_document_the_driver_carries_the_release_and_the_two_taxonomies_in_their_stable_order(plain):
    """``sarif-specification.md``, "SARIF Taxonomies" and its Rule 5: exactly two entries, OWASP at index 0 and CWE at 1, which never reorder, and
    every relationship of a rule names one of them. ``semanticVersion`` is tachi's release version, as in the other two files.
    # reading: PM W3 ruling 2c names the scorer's and controls files, and ``sarif-result.md`` leaves this driver to its own template (T101),
    # which still shows the orchestrator-era value. The retired generator wrote the constant ``1.7``."""
    run = plain.sarif["runs"][0]
    driver = run["tool"]["driver"]
    assert list(driver) == ["name", "semanticVersion", "informationUri", "supportedTaxonomies", "rules"]
    assert driver["semanticVersion"] == tp.VERSION
    assert [(entry["name"], entry["version"]) for entry in run["taxonomies"]] == [("OWASP", "2021"), ("CWE", "4.13")]
    assert driver["supportedTaxonomies"] == [{"name": "OWASP", "index": 0}, {"name": "CWE", "index": 1}]
    declared = {entry["name"] for entry in run["taxonomies"]}
    for rule in driver["rules"]:
        assert {link["target"]["toolComponent"]["name"] for link in rule["relationships"]} <= declared, rule["id"]


def test_cli_an_out_that_is_not_a_directory_exits_1_and_names_it(generator, tmp_path):
    """S1P-A42: ``--out`` is checked first, with the words that every entry shares, and it is exit 1 for an entry whose codes include 1."""
    project = Project(generator, tmp_path)
    res = invoke(generator, ["--threats", project.threats, "--out", project.out / "missing"], tmp_path)
    assert res.code == 1, res.describe()
    assert "--out is not a directory" in res.err and "Remedy: create it or correct --out" in res.err, res.describe()
    assert sorted(path.name for path in project.out.iterdir()) == ["threats.md"]


def test_cli_an_input_over_the_16_mib_cap_exits_2_and_writes_nothing(generator, tmp_path, monkeypatch):
    """D3 step 2's cap is read when the script runs, so a case sets a small one instead of writing 16 MiB."""
    project = Project(generator, tmp_path)
    monkeypatch.setattr(tp, "MAX_AGENT_INPUT_BYTES", 1000)
    res = project.generate()
    assert res.code == 2 and "is over 1000 bytes" in res.err, res.describe()
    assert not project.sarif_path.exists()


@pytest.mark.parametrize("where", ["the baseline run ID", "an asset tag"])
def test_refusal_a_forbidden_character_in_the_baseline_run_id_or_an_asset_tag_exits_2_and_writes_nothing(generator, tmp_path, where):
    """Two more values that the generator copies into the file, and so checks where it takes them (P0-4): the run ID that the frontmatter's
    baseline block names, which ``baseline-run-id`` carries, and a tag of the populator's block, which ``affected_assets`` copies."""
    text = with_baseline(make_threats_md(baseline_source="baseline/threats.md"))
    if where == "the baseline run ID":
        text = text.replace('run_id: "%s"' % BASELINE_RUN_ID, 'run_id: "%s%s"' % (BASELINE_RUN_ID, chr(0x202e)))
    else:
        text = text.replace("| S-2 | [] |", "| S-2 | [auth%s] |" % chr(0x202e))
    assert chr(0x202e) in text
    project = Project(generator, tmp_path, threats_text=text)
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    res = project.generate()
    assert res.code == 2 and "U+202E" in res.err, res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n', "an earlier file is left as it was"


def test_failure_a_file_that_cannot_be_written_exits_4_and_the_earlier_one_stays(generator, tmp_path, monkeypatch):
    project = Project(generator, tmp_path)
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')

    def refuse(path, data, mode_of=None):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(tp, "atomic_write", refuse)
    res = project.generate()
    assert res.code == 4, res.describe()
    assert "threats.sarif could not be written (Permission denied)" in res.err and "Remedy:" in res.err, res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n'


def test_failure_a_forbidden_character_that_reaches_the_document_is_stopped_by_the_backstop_with_exit_4(generator, tmp_path, monkeypatch):
    """Every value that the generator takes is checked where it is taken, so nothing reaches the document with a forbidden character by
    construction. The backstop looks at every decoded string of the finished document all the same (NFR-10, P0-4), and it is shown here by
    putting one where intake can't: through the emitter's own result."""
    project = Project(generator, tmp_path)
    project.sarif_path.write_bytes(b'{"earlier": "run"}\n')
    real = sc.build_result

    def tainted(**kwargs):
        result = real(**kwargs)
        result["properties"]["maestro-layer"] += chr(0x202e)
        return result

    monkeypatch.setattr(sc, "build_result", tainted)
    res = project.generate()
    assert res.code == 4 and "U+202E" in res.err, res.describe()
    assert project.sarif_path.read_bytes() == b'{"earlier": "run"}\n'


def test_warning_a_finding_that_section_7_lists_twice_is_named_on_stderr_and_the_exit_stays_0(generator, tmp_path):
    project = Project(generator, tmp_path, threats_text=make_threats_md(repeated=[("S-2", "client-portal")]))
    res = project.generate()
    assert res.code == 0 and "duplicate-finding-id" in res.err and "S-2" in res.err, res.describe()
    assert len(project.results) == len(SPECS)


def test_warning_a_drift_form_names_what_it_lacks_on_stderr_and_the_exit_stays_0(generator, tmp_path):
    text = (REPO_ROOT / "examples" / "consumer-agent-app" / "sample-report" / "threats.md").read_text(encoding="utf-8")
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 0, res.describe()
    assert "value-not-in-form" in res.err, res.describe()
    assert all(name in res.err for name in ("component", "threat", "delta_status")), res.describe()  # the three values the list form lacks (S-12(b))


def test_warning_a_malformed_row_of_section_4a_is_named_on_stderr_and_its_findings_stay_uncorrelated(generator, tmp_path):
    """The claim rule's own report belongs to ``check-threat-model.py`` (S1P-A19). A row that the shared parser skips is a different matter: it
    changes which findings correlate, so the run says so, and every other group still holds."""
    text = make_threats_md(groups=[("CG-X", ["S-2", "T-1"]), ("CG-2", ["E-3", "E-5"])])  # CG-X is not a group ID
    project = Project(generator, tmp_path, threats_text=text)
    res = project.generate()
    assert res.code == 0 and "correlation-row-skipped" in res.err, res.describe()
    results = project.results
    assert "correlation-group" not in results["S-2"]["properties"] and "correlation-group" not in results["T-1"]["properties"]
    assert results["E-3"]["properties"]["correlation-group"] == "CG-2" and results["E-5"]["properties"]["correlation-role"] == "peer"
