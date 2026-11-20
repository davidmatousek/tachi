"""Contract tests for threats.md schema 1.5 and the tachi_version stamp.

Feature 391, Part B2 (plan AD-7 and CF-21; tasks.md T038a and T039, test part),
and X-6 of the P0 architect checkpoint (``test-results/p0-architect-checkpoint.md``,
section 3 row 6) for the SARIF generator's version sourcing.

Schema 1.5 (``schemas/output.yaml``, the single source of the version) declares
the frontmatter keys that producers already wrote and adds one optional key,
``tachi_version``. ``scripts/stamp-tachi-version.py`` is the only writer of that
key. It runs as Step 2.6 of ``/tachi.threat-model``, after the populator re-assert
and before the results are reported. The model never writes the field.

Seven groups, the first six one per T039 case:

  1. Parsers unchanged. ``tachi_parsers`` and ``extract-report-data.py`` behave
     the same on a 1.4 input and on that input as 1.5 plus ``tachi_version``.
  2. Declarations agree. ``output.yaml``, the output template, the output-schemas
     reference and the SARIF specification state one version and one key set.
  3. The bump is additive. Every 1.4 key is still declared and ``tachi_version``
     is optional (and not model-authored).
  4. The stamp. Placement, idempotence, ``--check``, the marker rules, and the
     CF-21 scope decision (it writes ``tachi_version`` and no other key).
  5. Step 2.6 is in ``tachi.threat-model.md`` between Step 2.5 and Step 3.
  6. The consumer guidance is in ``output-schemas.md`` and in the comments of
     ``output.yaml``.
  7. The SARIF generator's version sourcing (X-6). ``generate-threats-sarif.py``
     writes the input's own ``schema_version`` as ``semanticVersion`` (standard
     and code-fenced frontmatter) and falls back to ``output.yaml`` when the input
     declares none.

Exit codes pinned here are the implemented ones, the house convention: 0 stamped,
unchanged or ``--check`` clean; 1 ``--check`` only, when the file would change;
2 every error. The contract text in ``cli-contracts.md`` has 1 and 2 the other way
round; T040 reconciles it.

Hygiene: every run happens in a pytest temporary directory. The repository tree is
only read. The stamp, the extractor and the SARIF generator run with ``cwd`` and every
output under ``tmp_path``, and subprocesses get ``-B`` so no bytecode lands beside the
scripts. No tracked SARIF is regenerated.
Needs pytest and PyYAML (``tests/scripts/conftest.py`` already requires both).
Python 3.9 syntax throughout.

Inputs, for the CI path filter: ``scripts/stamp-tachi-version.py``,
``scripts/tachi_parsers.py``, ``scripts/extract-report-data.py``,
``scripts/generate-threats-sarif.py`` (which also loads ``scripts/sarif_common.py``),
``schemas/output.yaml``, ``templates/tachi/output-schemas/threats.md``,
``.claude/skills/tachi-orchestration/references/output-schemas.md``,
``.claude/skills/tachi-orchestration/references/sarif-specification.md`` and
``.claude/commands/tachi.threat-model.md``. Read as sample data: every
``threats.md`` under ``examples/`` and ``tests/scripts/fixtures/``.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
STAMP_SCRIPT = SCRIPTS_DIR / "stamp-tachi-version.py"
EXTRACT_REPORT_DATA = SCRIPTS_DIR / "extract-report-data.py"
SARIF_GENERATOR = SCRIPTS_DIR / "generate-threats-sarif.py"
OUTPUT_YAML = REPO_ROOT / "schemas" / "output.yaml"
TEMPLATE_MD = REPO_ROOT / "templates" / "tachi" / "output-schemas" / "threats.md"
REPORT_TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
REFERENCES_DIR = REPO_ROOT / ".claude" / "skills" / "tachi-orchestration" / "references"
OUTPUT_SCHEMAS_MD = REFERENCES_DIR / "output-schemas.md"
SARIF_SPEC_MD = REFERENCES_DIR / "sarif-specification.md"
THREAT_MODEL_COMMAND = REPO_ROOT / ".claude" / "commands" / "tachi.threat-model.md"
EXAMPLES_DIR = REPO_ROOT / "examples"
FIXTURES_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures"

# The version schemas/output.yaml declares at this release. Every other check
# compares against the value read from output.yaml, so a drift names its source.
EXPECTED_SCHEMA_VERSION = "1.5"
NEW_KEY = "tachi_version"
ORIGINAL_KEYS = ("schema_version", "date", "input_format", "classification")
FLAG_KEYS = ("has_attack_chains", "has_agentic_patterns", "has_source_attribution")
# The keys producers wrote before 1.5 without output.yaml declaring them.
DE_FACTO_KEYS = ("run_id", "baseline", "coverage_gate") + FLAG_KEYS
KEYS_1_4 = ORIGINAL_KEYS + DE_FACTO_KEYS
BASELINE_SUBKEYS = ("source", "date", "finding_count", "run_id")
COVERAGE_GATE_SUBKEYS = ("status", "gaps")

# output.yaml at 1.1 declared these four keys and these eight sections.
ORIGINAL_FIELDS_1_1 = {
    "schema_version": {"type": "string"},
    "date": {"type": "string", "format": "YYYY-MM-DD"},
    "input_format": {"type": "string", "enum": ["ascii", "free-text", "mermaid", "plantuml", "c4"]},
    "classification": {"type": "string", "default": "confidential"},
}
SECTION_NAMES_1_1 = (
    "System Overview",
    "Trust Boundaries",
    "STRIDE Tables",
    "AI Threat Tables",
    "Correlated Findings",
    "Coverage Matrix",
    "Risk Summary",
    "Recommended Actions",
)

STEP_COMMAND = "python3 scripts/stamp-tachi-version.py --threats {output_dir}/threats.md"
FAILURE_LINE = "tachi_version not stamped (exit N)"
EXPECTED_COMMAND_FRONTMATTER_KEYS = {"description"}


def _import_tachi_parsers():
    """Import ``scripts/tachi_parsers.py`` the way its sibling tests do, minus the bytecode."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    keep = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        import tachi_parsers as module
    finally:
        sys.dont_write_bytecode = keep
    return module


tachi_parsers = _import_tachi_parsers()


# =============================================================================
# Shared helpers
# =============================================================================


def read_text(path):
    """A file as text, with no newline translation."""
    return Path(path).read_bytes().decode("utf-8")


def parser_frontmatter_text(content):
    """The frontmatter the consumers see: ``tachi_parsers``' own extraction, or None."""
    return tachi_parsers._extract_frontmatter_text(content)


def drop_new_key(parsed):
    """A parser result without ``tachi_version``, for 'the same apart from the new key'."""
    return {key: value for key, value in parsed.items() if key != NEW_KEY}


def remove_top_level_tachi_version(text):
    """The text without its first top-level ``tachi_version:`` line, if it has one."""
    return re.sub(r"(?m)^tachi_version[ \t]*:.*\n", "", text, count=1)


def as_schema_14(text):
    """A real example as a 1.4 file: ``schema_version`` forced to 1.4 and no ``tachi_version``."""
    return set_schema_version(remove_top_level_tachi_version(text), "1.4")


def set_schema_version(text, version):
    return re.sub(r'(?m)^schema_version:.*$', 'schema_version: "%s"' % version, text, count=1)


def write_marker(directory, value="v4.48.2-3-gabc1234-dirty"):
    """The marker the installer writes: one line, ``tachi_version: <value>``."""
    path = Path(directory) / "VERSION"
    path.write_bytes(("tachi_version: %s\n" % value).encode("utf-8"))
    return path


@pytest.fixture(scope="module")
def stamp_module():
    """``scripts/stamp-tachi-version.py`` imported once, for the fast in-process runs."""
    keep = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("stamp_tachi_version", STAMP_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = keep
    return module


RUN = dict(capture_output=True, text=True, encoding="utf-8", errors="replace")


def run_stamp(threats, *flags, marker=None, cwd):
    """Run the stamp CLI in a subprocess. ``cwd`` is always a temporary directory."""
    cmd = [sys.executable, "-I", "-B", str(STAMP_SCRIPT), "--threats", str(threats)]
    if marker is not None:
        cmd += ["--marker", str(marker)]
    cmd += list(flags)
    return subprocess.run(cmd, cwd=str(cwd), **RUN)


def stamp_in_process(module, threats, marker, *flags):
    """``main(argv)`` of the stamp, with its output captured: ``(exit code, stdout, stderr)``."""
    out, err = io.StringIO(), io.StringIO()
    argv = ["--threats", str(threats), "--marker", str(marker)] + list(flags)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = module.main(argv)
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def stamp_text(module, workdir, text, value):
    """``text`` stamped by the real script with marker ``value``; the stamped text comes back."""
    workdir.mkdir(parents=True, exist_ok=True)
    threats = workdir / "threats.md"
    threats.write_bytes(text.encode("utf-8"))
    marker = write_marker(workdir, value)
    code, _out, err = stamp_in_process(module, threats, marker)
    assert code == 0, "stamp failed (exit %s): %s" % (code, err)
    return read_text(threats)


# The frontmatter shapes the stamp has to cope with. FM_FULL is a 1.4 file with
# every key a producer wrote; FM_BLOCK_LAST has no schema_version and ends in a
# nested block, which is the case where a line appended at the end must stay at
# column 0 and not join the block above it.
FM_FULL = [
    'schema_version: "1.4"',
    'date: "2026-04-10"',
    'input_format: "mermaid"',
    'classification: "confidential"',
    'run_id: "2026-04-10T10-00-00"',
    "baseline:",
    '  source: "docs/security/old/threats.md"',
    '  date: "2026-04-01"',
    "  finding_count: 12",
    '  run_id: "2026-04-01T09-00-00"',
    "coverage_gate:",
    '  status: "pass"',
    "  gaps: []",
    "has_attack_chains: true",
    "has_agentic_patterns: false",
    "has_source_attribution: true",
]
FM_BLOCK_LAST = [
    'date: "2026-04-10"',
    'input_format: "mermaid"',
    'classification: "confidential"',
    "coverage_gate:",
    '  status: "warn"',
    "  gaps:",
    "    - component: API",
    "      missing_category: Tampering",
    "      resolution: dispatch_failure",
    "baseline:",
    '  source: "docs/security/old/threats.md"',
    '  date: "2026-04-01"',
    "  finding_count: 12",
    '  run_id: "2026-04-01T09-00-00"',
]
# A body with look-alike lines: a quoted example frontmatter further down must
# never be mistaken for the real one.
BODY = [
    "",
    "# Threat Model Report",
    "",
    "Example from the reference (it stays as written):",
    "",
    "```yaml",
    "---",
    'schema_version: "1.2"',
    'tachi_version: "body-example"',
    "---",
    "```",
    "",
    "| Component | Type |",
    "|-----------|------|",
    "| API | Process |",
]
STAMP_VALUE = "v4.48.2-3-gabc1234-dirty"


def stamp_line(value=STAMP_VALUE):
    return 'tachi_version: "%s"' % value


def make_threats(fm, *, fenced=False, eol="\n", final_newline=True, body=BODY):
    """A threats.md as bytes. ``fenced`` puts the frontmatter in a ``yaml`` code fence."""
    head = ["# Threat Model Report", "", "```yaml"] if fenced else []
    tail = ["```"] if fenced else []
    lines = head + ["---"] + list(fm) + ["---"] + tail + list(body)
    text = eol.join(lines)
    if final_newline:
        text += eol
    return text.encode("utf-8")


FENCED_AND_STANDARD = pytest.mark.parametrize("fenced", [False, True], ids=["standard", "fenced"])
LF_AND_CRLF = pytest.mark.parametrize("eol", ["\n", "\r\n"], ids=["lf", "crlf"])


def fresh_threats(tmp_path, data, name="threats.md"):
    path = tmp_path / name
    path.write_bytes(data)
    return path


def project_files(directory):
    return sorted(os.listdir(str(directory)))


# Real files, for the groups that need the shapes producers actually write.
REAL_EXAMPLES = {
    "web-app": EXAMPLES_DIR / "web-app" / "threats.md",
    "ascii-web-api": EXAMPLES_DIR / "ascii-web-api" / "threats.md",
    "baseline-fixture": FIXTURES_DIR / "fidelity_373" / "baseline_resolved_4c" / "threats.md",
    "agentic-app": EXAMPLES_DIR / "agentic-app" / "threats.md",
}


# =============================================================================
# Case 1. Parsers unchanged
# =============================================================================

BODY_PARSERS = (
    tachi_parsers.parse_threats_findings,
    tachi_parsers.parse_threats_severity,
    tachi_parsers.parse_scope_data,
    tachi_parsers.parse_resolved_findings,
    tachi_parsers.delta_status_by_id,
    tachi_parsers.parse_project_name,
)


@pytest.mark.parametrize("name", sorted(REAL_EXAMPLES))
def test_parsers_read_1_4_and_1_5_inputs_alike(name, tmp_path, stamp_module):
    """1.4 input versus the same input as 1.5 plus ``tachi_version``, read by ``tachi_parsers``.

    The 1.5 side is made by the real stamp, so a producer's actual output is what the
    consumers read. Only ``schema_version`` may differ in what ``parse_frontmatter`` returns.
    """
    v14 = as_schema_14(read_text(REAL_EXAMPLES[name]))
    stamped = stamp_text(stamp_module, tmp_path / "prep", v14, STAMP_VALUE)
    v15 = set_schema_version(stamped, "1.5")
    assert stamp_line() in v15 and v15 != v14

    base = tachi_parsers.parse_frontmatter(v14)
    assert base["schema_version"] == "1.4" and base["date"] != "Unknown"  # the reading is not vacuous
    assert drop_new_key(tachi_parsers.parse_frontmatter(stamped)) == base
    assert drop_new_key(tachi_parsers.parse_frontmatter(v15)) == dict(base, schema_version="1.5")

    baseline = tachi_parsers.parse_baseline_frontmatter(v14)
    assert tachi_parsers.parse_baseline_frontmatter(stamped) == baseline
    assert tachi_parsers.parse_baseline_frontmatter(v15) == baseline

    for parse in BODY_PARSERS:
        assert parse(v15) == parse(v14), "%s changed with the 1.5 frontmatter" % parse.__name__
        assert parse(stamped) == parse(v14), "%s changed with tachi_version" % parse.__name__


def _placement_params():
    shapes = {"full": FM_FULL, "block-last": FM_BLOCK_LAST}
    params = []
    for shape, fm in shapes.items():
        spots = {"first": 0, "before-baseline": fm.index("baseline:"), "last": len(fm)}
        if any(line.startswith("schema_version:") for line in fm):
            spots["after-schema-version"] = 1
        for spot, at in spots.items():
            params.append(pytest.param(shape, fm, at, id="%s-%s" % (shape, spot)))
    return params


@FENCED_AND_STANDARD
@pytest.mark.parametrize("shape, fm, at", _placement_params())
def test_frontmatter_readers_ignore_tachi_version_wherever_it_sits(shape, fm, at, fenced):
    """Both frontmatter readers, and PyYAML, see the same data with or without the new key.

    The stamp writes it after ``schema_version`` or at the end of the frontmatter; the
    other positions cover a file whose keys a person reordered.
    """
    without = make_threats(fm, fenced=fenced).decode("utf-8")
    parsed_without = tachi_parsers.parse_frontmatter(without)
    assert parsed_without["date"] == "2026-04-10"
    assert tachi_parsers.parse_baseline_frontmatter(without)["has_baseline"] is True
    baseline_without = tachi_parsers.parse_baseline_frontmatter(without)
    yaml_without = yaml.safe_load(parser_frontmatter_text(without))

    for value in ("v4.48.1", "v4.48.1-2-g3ecba74-dirty", "4.48.1-release-manifest", "unknown"):
        with_key = make_threats(fm[:at] + [stamp_line(value)] + fm[at:], fenced=fenced).decode("utf-8")
        assert drop_new_key(tachi_parsers.parse_frontmatter(with_key)) == parsed_without
        assert tachi_parsers.parse_baseline_frontmatter(with_key) == baseline_without
        assert yaml.safe_load(parser_frontmatter_text(with_key)) == dict(yaml_without, tachi_version=value)


def run_extractor(target_dir, output, cwd):
    cmd = [sys.executable, "-B", str(EXTRACT_REPORT_DATA), "--target-dir", str(target_dir),
           "--template-dir", str(REPORT_TEMPLATE_DIR), "--output", str(output)]
    return subprocess.run(cmd, cwd=str(cwd), **RUN)


def extractor_result(tmp_path, target, label, text):
    """Run the extractor on ``text`` as the only file in ``target``; return what it did."""
    (target / "threats.md").write_bytes(text.encode("utf-8"))
    output = tmp_path / ("report-data-%s.typ" % label)
    proc = run_extractor(target, output, tmp_path)
    assert proc.returncode == 0, "extract-report-data.py exited %s on the %s input:\n%s" % (
        proc.returncode, label, proc.stderr)
    assert output.is_file() and "#let " in output.read_text(encoding="utf-8")
    assert project_files(target) == ["threats.md"], "the extractor wrote beside its input"
    return proc.returncode, proc.stdout, proc.stderr, output.read_bytes()


@pytest.mark.parametrize("name", sorted(REAL_EXAMPLES))
def test_extract_report_data_behaves_the_same_on_1_4_and_1_5(name, tmp_path, stamp_module):
    """``extract-report-data.py`` on 1.4 versus 1.5 plus ``tachi_version``: same exit code, same
    stdout and stderr, same ``report-data.typ`` bytes. The one directory is reused so no path differs."""
    v14 = as_schema_14(read_text(REAL_EXAMPLES[name]))
    v15 = set_schema_version(stamp_text(stamp_module, tmp_path / "prep", v14, STAMP_VALUE), "1.5")
    target = tmp_path / "target"
    target.mkdir()
    as_14 = extractor_result(tmp_path, target, "1.4", v14)
    as_15 = extractor_result(tmp_path, target, "1.5", v15)
    assert as_15 == as_14


def test_the_extractor_comparison_can_see_a_frontmatter_difference(tmp_path):
    """Control for the test above: the extractor does react to ``schema_version`` 1.0.

    Without this the 1.4 versus 1.5 comparison could pass because it cannot tell
    two frontmatters apart.
    """
    text = as_schema_14(read_text(REAL_EXAMPLES["web-app"]))
    target = tmp_path / "target"
    target.mkdir()
    as_14 = extractor_result(tmp_path, target, "1.4", text)
    as_10 = extractor_result(tmp_path, target, "1.0", set_schema_version(text, "1.0"))
    assert "Schema v1.0 detected" in as_10[2] and "Schema v1.0 detected" not in as_14[2]


# =============================================================================
# Case 2. Declarations agree with schemas/output.yaml
# =============================================================================


@pytest.fixture(scope="module")
def schema_doc():
    return yaml.safe_load(read_text(OUTPUT_YAML))


@pytest.fixture(scope="module")
def declared(schema_doc):
    return schema_doc["output"]["frontmatter"]["fields"]


@pytest.fixture(scope="module")
def version(schema_doc):
    """The version output.yaml declares: the single source every document is compared with."""
    return schema_doc["schema_version"]


def markdown_table_rows(text, anchor_pattern):
    """The data rows (cell lists) of the first table after the line matching ``anchor_pattern``."""
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if re.search(anchor_pattern, line)]
    assert starts, "no line matches %r" % anchor_pattern
    rows = []
    for line in lines[starts[0] + 1:]:
        if line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif rows:
            break
    return [row for row in rows if "`" in row[0]]


def row_keys(row):
    """Top-level key names in a table row's first cell: ``baseline.source`` counts as ``baseline``."""
    return {name.split(".")[0] for name in re.findall(r"`([A-Za-z_][\w.]*)`", row[0])}


def markdown_section(text, heading):
    """The text from the ``### heading`` line to the next ``### `` line."""
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith("### " + heading)]
    assert starts, "no '### %s' heading" % heading
    end = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].startswith("### ")), len(lines))
    return "\n".join(lines[starts[0]:end])


def test_output_yaml_declares_schema_1_5(schema_doc, declared):
    raw = read_text(OUTPUT_YAML)
    header = re.search(r"(?m)^#\s*Version:\s*(\S+)\s*$", raw)
    assert header, "output.yaml lost its '# Version:' header line"
    assert header.group(1) == EXPECTED_SCHEMA_VERSION
    assert schema_doc["schema_version"] == EXPECTED_SCHEMA_VERSION  # a quoted string, not the float 1.5
    assert declared["schema_version"]["value"] == EXPECTED_SCHEMA_VERSION
    assert declared["schema_version"]["type"] == "string"


def test_output_yaml_declares_the_de_facto_keys_and_tachi_version(declared):
    missing = [key for key in ORIGINAL_KEYS + DE_FACTO_KEYS + (NEW_KEY,) if key not in declared]
    assert not missing, "output.yaml does not declare: %s" % ", ".join(missing)
    assert set(declared["baseline"]["fields"]) == set(BASELINE_SUBKEYS)
    assert set(declared["coverage_gate"]["fields"]) == set(COVERAGE_GATE_SUBKEYS)
    assert declared["run_id"]["type"] == "string"
    assert declared["baseline"]["type"] == declared["coverage_gate"]["type"] == "object"
    assert all(declared[key]["type"] == "boolean" for key in FLAG_KEYS)
    assert declared[NEW_KEY]["type"] == "string"


def tracked_threats_files():
    return sorted(EXAMPLES_DIR.rglob("threats.md")) + sorted(FIXTURES_DIR.rglob("threats.md"))


def test_declared_keys_cover_every_tracked_threats_md(declared):
    """Declarations against reality: nothing the tracked files carry is undeclared."""
    undeclared, checked = [], 0
    for path in tracked_threats_files():
        text = parser_frontmatter_text(read_text(path))
        if text is None:
            continue
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            continue  # the parsers tolerate hand-written frontmatter that is not strict YAML
        if not isinstance(data, dict):
            continue
        checked += 1
        name = path.relative_to(REPO_ROOT).as_posix()
        for key in data:
            if key not in declared:
                undeclared.append("%s: key %r" % (name, key))
        for key in ("baseline", "coverage_gate"):
            if isinstance(data.get(key), dict):
                known = declared[key]["fields"]
                undeclared += ["%s: %s.%s" % (name, key, sub) for sub in data[key] if sub not in known]
        for key in FLAG_KEYS:
            if key in data and not isinstance(data[key], bool):
                undeclared.append("%s: %s is not a boolean" % (name, key))
    assert checked >= 10, "only %d tracked threats.md files with frontmatter were found" % checked
    assert not undeclared, "frontmatter that output.yaml does not declare:\n  " + "\n  ".join(undeclared)


def test_output_template_agrees_with_output_yaml(version, declared):
    text = read_text(TEMPLATE_MD)
    header = re.search(r"(?m)^\s*Schema version\s*:\s*(\S+)\s*$", text)
    assert header and header.group(1) == version, "template header comment: %s" % (header and header.group(1))
    literals = re.findall(r'(?m)^schema_version:\s*"([^"]+)"\s*$', text)
    assert len(literals) >= 3 and set(literals) == {version}, "template examples say %s" % literals
    rows = markdown_table_rows(text, r"^\*\*Frontmatter fields:\*\*")
    row = next(r for r in rows if "`schema_version`" in r[0])
    assert re.search(r'Always `"%s"`' % re.escape(version), row[2]), "template row says: %s" % row[2]
    keys = set()
    for table_row in rows:
        keys |= row_keys(table_row)
    assert keys == set(declared), "template table and output.yaml differ on %s" % sorted(keys ^ set(declared))
    example = parser_frontmatter_text(text)  # the first example frontmatter in the template
    assert example is not None
    stray = [key for key in re.findall(r"(?m)^([A-Za-z_]\w*):", example) if key not in declared]
    assert not stray, "template example frontmatter has undeclared keys: %s" % stray


def test_output_schemas_reference_agrees_with_output_yaml(version, declared):
    text = read_text(OUTPUT_SCHEMAS_MD)
    section = markdown_section(text, "Frontmatter")
    example = re.search(r"```yaml\n---\n(.*?)\n---\n```", section, re.DOTALL)
    assert example, "the Frontmatter section lost its example block"
    assert re.search(r'(?m)^schema_version:\s*"%s"\s*$' % re.escape(version), example.group(1))
    rows = markdown_table_rows(section, r"^\| Field \|")
    row = next(r for r in rows if "`schema_version`" in r[0])
    assert re.search(r'Always `"%s"`' % re.escape(version), row[2]), "schema_version row: %s" % row[2]
    checklist = re.search(r'(?m)^- \[ \] `schema_version` is `"([^"]+)"`', text)
    assert checklist, "the validation checklist lost its schema_version item"
    assert checklist.group(1) == version, "validation checklist says %s" % checklist.group(1)
    # Every declared key is named in the section: the table, or the prose that points at the template.
    unnamed = [key for key in declared if "`%s`" % key not in section]
    assert not unnamed, "output-schemas.md Frontmatter section does not name: %s" % ", ".join(unnamed)
    table_keys = set()
    for table_row in rows:
        table_keys |= row_keys(table_row)
    assert {"tachi_version", *FLAG_KEYS} <= table_keys


def test_sarif_specification_agrees_with_output_yaml(version):
    text = read_text(SARIF_SPEC_MD)
    current = re.search(r'`semanticVersion`[^\n]*\(currently `"([^"]+)"`\)', text)
    assert current, "the semanticVersion rule lost its '(currently ...)' version"
    assert current.group(1) == version
    example = re.search(r'"semanticVersion":\s*"([^"]+)"', text)
    assert example, "the SARIF example lost its semanticVersion line"
    if re.fullmatch(r"\d+\.\d+", example.group(1)):
        assert example.group(1) == version
    else:
        assert "output.yaml" in example.group(1), "semanticVersion placeholder: %s" % example.group(1)


# =============================================================================
# Case 3. The 1.5 bump is additive
# =============================================================================


def test_every_1_4_key_is_still_declared(declared):
    missing = [key for key in KEYS_1_4 if key not in declared]
    assert not missing, "1.4 keys no longer declared: %s" % ", ".join(missing)


def test_original_field_declarations_are_not_retyped(declared):
    for key, original in ORIGINAL_FIELDS_1_1.items():
        for attribute, value in original.items():
            now = declared[key].get(attribute)
            if attribute == "enum":
                lost = sorted(set(value) - set(now))
                assert not lost, "%s lost enum values: %s" % (key, lost)
            else:
                assert now == value, "%s.%s changed from %r to %r" % (key, attribute, value, now)


def test_sections_and_required_frontmatter_are_kept(schema_doc):
    names = [section["name"] for section in schema_doc["output"]["sections"]]
    removed = [name for name in SECTION_NAMES_1_1 if name not in names]
    assert not removed, "sections removed from output.yaml: %s" % removed
    assert schema_doc["output"]["frontmatter"]["required"] is True


def tachi_version_row(path, anchor, scope_heading=None):
    """The ``tachi_version`` row (cell list) of the frontmatter fields table in ``path``."""
    text = read_text(path)
    if scope_heading:
        text = markdown_section(text, scope_heading)
    return next(r for r in markdown_table_rows(text, anchor) if "`tachi_version`" in r[0])


TEMPLATE_ROW = (TEMPLATE_MD, r"^\*\*Frontmatter fields:\*\*", None)
REFERENCE_ROW = (OUTPUT_SCHEMAS_MD, r"^\| Field \|", "Frontmatter")


def test_tachi_version_is_declared_optional(declared):
    entry = declared[NEW_KEY]
    assert not entry.get("required"), "output.yaml marks tachi_version required, which a 1.4 file lacks"
    assert re.search(r"\babsent\b.{0,60}1\.5", " ".join(entry["description"].split()), re.IGNORECASE), (
        "output.yaml's tachi_version description no longer says it is absent in files from before 1.5")
    for path, anchor, heading in (TEMPLATE_ROW, REFERENCE_ROW):
        row = tachi_version_row(path, anchor, heading)
        assert "optional" in row[1], "%s: tachi_version row type cell is %r" % (path.name, row[1])


def test_tachi_version_is_declared_as_not_model_authored(declared):
    pattern = re.compile(r"(not authored by the model|model never writes)", re.IGNORECASE)
    texts = {
        "output.yaml": declared[NEW_KEY]["description"],
        "template": tachi_version_row(*TEMPLATE_ROW)[2],
        "output-schemas.md": tachi_version_row(*REFERENCE_ROW)[2],
    }
    for where, text in texts.items():
        assert pattern.search(" ".join(text.split())), "%s no longer says the model never writes it" % where
    checklist = "`tachi_version` is not authored here"
    assert checklist in read_text(OUTPUT_SCHEMAS_MD), "the validation checklist lost its tachi_version item"


# =============================================================================
# Case 4. The stamp: placement, idempotence, --check, the marker, scope
# =============================================================================


def stamped_by_cli(tmp_path, data, value=STAMP_VALUE, name="threats.md"):
    """Stamp ``data`` through the CLI; return ``(path, marker, completed process)``."""
    threats = fresh_threats(tmp_path, data, name)
    marker = write_marker(tmp_path, value)
    proc = run_stamp(threats, marker=marker, cwd=tmp_path)
    return threats, marker, proc


@FENCED_AND_STANDARD
@LF_AND_CRLF
def test_stamp_inserts_one_line_right_after_schema_version(tmp_path, fenced, eol):
    before = make_threats(FM_FULL, fenced=fenced, eol=eol)
    threats, _marker, proc = stamped_by_cli(tmp_path, before)
    assert proc.returncode == 0, proc.stderr
    expected = make_threats(FM_FULL[:1] + [stamp_line()] + FM_FULL[1:], fenced=fenced, eol=eol)
    assert threats.read_bytes() == expected  # schema_version and every other byte untouched
    assert project_files(tmp_path) == ["VERSION", "threats.md"]  # no temp file left


@FENCED_AND_STANDARD
@LF_AND_CRLF
def test_stamp_appends_at_the_end_of_the_frontmatter_without_schema_version(tmp_path, fenced, eol):
    before = make_threats(FM_BLOCK_LAST, fenced=fenced, eol=eol)
    threats, _marker, proc = stamped_by_cli(tmp_path, before)
    assert proc.returncode == 0, proc.stderr
    assert threats.read_bytes() == make_threats(FM_BLOCK_LAST + [stamp_line()], fenced=fenced, eol=eol)
    # At column 0, so the nested baseline block above is not extended.
    after = tachi_parsers.parse_baseline_frontmatter(threats.read_bytes().decode("utf-8"))
    assert after == tachi_parsers.parse_baseline_frontmatter(before.decode("utf-8"))
    assert after["has_baseline"] is True


PLACEMENT_EDGES = [
    pytest.param(['date: "2026-04-10"', 'schema_version: "1.4"'],
                 ['date: "2026-04-10"', 'schema_version: "1.4"', stamp_line()],
                 {}, id="schema-version-is-the-last-key"),
    pytest.param(['schema_version:', '  "1.4"', 'date: "2026-04-10"'],
                 ['schema_version:', '  "1.4"', stamp_line(), 'date: "2026-04-10"'],
                 {}, id="multi-line-schema-version-stays-whole"),
    pytest.param(FM_FULL, FM_FULL[:1] + [stamp_line()] + FM_FULL[1:],
                 {"final_newline": False}, id="no-final-newline"),
    pytest.param(FM_FULL, FM_FULL[:1] + [stamp_line()] + FM_FULL[1:],
                 {"body": (), "final_newline": False}, id="frontmatter-only-file"),
]


@pytest.mark.parametrize("fm, expected_fm, options", PLACEMENT_EDGES)
def test_stamp_placement_edge_cases(tmp_path, fm, expected_fm, options):
    threats, _marker, proc = stamped_by_cli(tmp_path, make_threats(fm, **options))
    assert proc.returncode == 0, proc.stderr
    assert threats.read_bytes() == make_threats(expected_fm, **options)


def test_stamp_keeps_body_bytes_it_cannot_decode(tmp_path):
    """The file is handled as bytes: a body that is not valid UTF-8 comes through unchanged."""
    tail = b"\xff\xfe\x00 not utf-8 \x80\n"
    threats, _marker, proc = stamped_by_cli(tmp_path, make_threats(FM_FULL) + tail)
    assert proc.returncode == 0, proc.stderr
    assert threats.read_bytes() == make_threats(FM_FULL[:1] + [stamp_line()] + FM_FULL[1:]) + tail


SCHEMA_LINE = 'schema_version: "1.4"'
DATE_LINE = 'date: "2026-04-10"'
CLASS_LINE = 'classification: "confidential"'
STALE_FIELD_CASES = [
    pytest.param([SCHEMA_LINE, DATE_LINE, 'tachi_version: "v0.0.1"', CLASS_LINE],
                 [SCHEMA_LINE, DATE_LINE, stamp_line(), CLASS_LINE],
                 id="stale-value-updated-where-it-stands"),
    pytest.param([SCHEMA_LINE, 'tachi_version: v0.0.1', DATE_LINE],
                 [SCHEMA_LINE, stamp_line(), DATE_LINE],
                 id="unquoted-value-rewritten-quoted"),
    pytest.param([SCHEMA_LINE, 'tachi_version: "a"', DATE_LINE, 'tachi_version: "b"'],
                 [SCHEMA_LINE, stamp_line(), DATE_LINE],
                 id="duplicates-collapse-to-one"),
    pytest.param([SCHEMA_LINE, "baseline:", '  tachi_version: "nested"', '  source: "x"'],
                 [SCHEMA_LINE, stamp_line(), "baseline:", '  tachi_version: "nested"', '  source: "x"'],
                 id="a-nested-key-of-that-name-is-left-alone"),
]


@pytest.mark.parametrize("fm, expected_fm", STALE_FIELD_CASES)
def test_stamp_updates_an_existing_field_in_place(tmp_path, fm, expected_fm):
    threats, _marker, proc = stamped_by_cli(tmp_path, make_threats(fm))
    assert proc.returncode == 0, proc.stderr
    assert threats.read_bytes() == make_threats(expected_fm)


@FENCED_AND_STANDARD
def test_stamp_is_idempotent(tmp_path, fenced):
    """The second run changes nothing, not even the file's modification time."""
    threats, marker, first = stamped_by_cli(tmp_path, make_threats(FM_FULL, fenced=fenced))
    assert first.returncode == 0, first.stderr
    stamped = threats.read_bytes()
    assert stamped != make_threats(FM_FULL, fenced=fenced)  # the first run did write

    long_ago = 946684800 * 10 ** 9  # 2000-01-01T00:00:00Z; a rewrite would move it to "now"
    os.utime(str(threats), ns=(long_ago, long_ago))
    for _ in range(2):
        again = run_stamp(threats, marker=marker, cwd=tmp_path)
        assert again.returncode == 0, again.stderr
        assert threats.read_bytes() == stamped
        assert threats.stat().st_mtime_ns == long_ago, "an already stamped file was rewritten"
    assert project_files(tmp_path) == ["VERSION", "threats.md"]


def test_stamp_is_deterministic_across_copies(tmp_path):
    """Nothing time- or path-dependent reaches the file: two copies stamped apart end up identical."""
    data = make_threats(FM_FULL)
    results = []
    for name in ("one", "two"):
        directory = tmp_path / name
        directory.mkdir()
        threats, _marker, proc = stamped_by_cli(directory, data)
        assert proc.returncode == 0, proc.stderr
        results.append(threats.read_bytes())
    assert results[0] == results[1]


def test_check_reports_drift_with_exit_1_and_writes_nothing(tmp_path):
    before = make_threats(FM_FULL)
    threats = fresh_threats(tmp_path, before)
    marker = write_marker(tmp_path)
    proc = run_stamp(threats, "--check", marker=marker, cwd=tmp_path)
    assert proc.returncode == 1
    assert proc.stderr.strip(), "a --check finding says why on stderr"
    assert threats.read_bytes() == before
    assert project_files(tmp_path) == ["VERSION", "threats.md"]


def test_check_passes_on_a_stamped_file_and_flags_a_stale_value(tmp_path):
    threats, marker, first = stamped_by_cli(tmp_path, make_threats(FM_FULL), value="v1.0.0")
    assert first.returncode == 0, first.stderr
    stamped = threats.read_bytes()

    clean = run_stamp(threats, "--check", marker=marker, cwd=tmp_path)
    assert clean.returncode == 0, clean.stderr
    assert threats.read_bytes() == stamped

    write_marker(tmp_path, "v2.0.0")  # the install moved on; the file is now stale
    stale = run_stamp(threats, "--check", marker=marker, cwd=tmp_path)
    assert stale.returncode == 1
    assert threats.read_bytes() == stamped  # --check never writes

    fixed = run_stamp(threats, marker=marker, cwd=tmp_path)
    assert fixed.returncode == 0, fixed.stderr
    assert threats.read_bytes() == make_threats(FM_FULL[:1] + [stamp_line("v2.0.0")] + FM_FULL[1:])
    assert run_stamp(threats, "--check", marker=marker, cwd=tmp_path).returncode == 0


ERROR_INPUTS = [
    pytest.param(b"# A threat model\n\nNo frontmatter here.\n", id="no-frontmatter"),
    pytest.param(b'---\nschema_version: "1.4"\ndate: "2026-04-10"\n\n# never closed\n',
                 id="unterminated-frontmatter"),
    pytest.param(b"", id="empty-file"),
]


@pytest.mark.parametrize("check", [False, True], ids=["stamp", "check"])
@pytest.mark.parametrize("data", ERROR_INPUTS)
def test_errors_exit_2_and_write_nothing(tmp_path, data, check):
    """An error is exit 2 whether or not --check is given, so it never reads as 'would change' (1)."""
    threats = fresh_threats(tmp_path, data)
    marker = write_marker(tmp_path)
    proc = run_stamp(threats, *(["--check"] if check else []), marker=marker, cwd=tmp_path)
    assert proc.returncode == 2, proc.stderr
    assert "frontmatter" in proc.stderr
    assert threats.read_bytes() == data
    assert project_files(tmp_path) == ["VERSION", "threats.md"]


@pytest.mark.parametrize("check", [False, True], ids=["stamp", "check"])
def test_a_missing_threats_file_exits_2(tmp_path, check):
    marker = write_marker(tmp_path)
    proc = run_stamp(tmp_path / "absent.md", *(["--check"] if check else []), marker=marker, cwd=tmp_path)
    assert proc.returncode == 2
    assert project_files(tmp_path) == ["VERSION"]


MALFORMED_MARKERS = [
    pytest.param(None, id="absent"),
    pytest.param(b"", id="empty"),
    pytest.param(b"version: v1.0.0\n", id="wrong-key"),
    pytest.param(b'tachi_version: "v1.0.0"\n', id="quoted-value"),
    pytest.param(b"tachi_version: v 1\n", id="space-in-the-value"),
    pytest.param(b"tachi_version: " + b"a" * 129 + b"\n", id="value-over-128-characters"),
    pytest.param(b"tachi_version: v1\ntachi_version: v2\n", id="two-lines"),
    pytest.param(b"\xff\xfe tachi_version: v1\n", id="not-utf-8"),
    pytest.param("a directory, not a file", id="a-directory"),
]


@pytest.mark.parametrize("content", MALFORMED_MARKERS)
def test_a_missing_or_malformed_marker_stamps_unknown_and_warns(tmp_path, content):
    """An install that skipped the marker line reads ``unknown``; the run itself does not fail."""
    marker = tmp_path / "VERSION"
    if isinstance(content, str):  # the one non-bytes case: the marker path is a directory
        marker.mkdir()
    elif content is not None:
        marker.write_bytes(content)
    threats = fresh_threats(tmp_path, make_threats(FM_FULL))
    proc = run_stamp(threats, marker=marker, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert threats.read_bytes() == make_threats(FM_FULL[:1] + [stamp_line("unknown")] + FM_FULL[1:])
    assert "warning" in proc.stderr.lower() and "unknown" in proc.stderr
    assert run_stamp(threats, "--check", marker=marker, cwd=tmp_path).returncode == 0


def test_the_tracked_placeholder_marker_reads_unknown_without_a_warning(tmp_path):
    threats = fresh_threats(tmp_path, make_threats(FM_FULL))
    marker = write_marker(tmp_path, "unknown")
    proc = run_stamp(threats, marker=marker, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert stamp_line("unknown").encode() in threats.read_bytes()
    assert "warning" not in proc.stderr.lower()


VALID_MARKERS = [
    pytest.param(b"tachi_version: v4.48.1\n", "v4.48.1", id="release-tag"),
    pytest.param(b"tachi_version: v4.48.1-2-g3ecba74-dirty\n", "v4.48.1-2-g3ecba74-dirty", id="git-describe"),
    pytest.param(b"tachi_version: 4.48.1-release-manifest\n", "4.48.1-release-manifest",
                 id="release-manifest"),
    pytest.param(b"tachi_version: v4.48.1\r\n", "v4.48.1", id="crlf"),
    pytest.param(b"tachi_version: v4.48.1", "v4.48.1", id="no-final-newline"),
    pytest.param(b"tachi_version: " + b"a" * 128 + b"\n", "a" * 128, id="128-characters"),
]


@pytest.mark.parametrize("content, expected", VALID_MARKERS)
def test_a_valid_marker_is_copied_verbatim(tmp_path, content, expected):
    marker = tmp_path / "VERSION"
    marker.write_bytes(content)
    threats = fresh_threats(tmp_path, make_threats(FM_FULL))
    proc = run_stamp(threats, marker=marker, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert threats.read_bytes() == make_threats(FM_FULL[:1] + [stamp_line(expected)] + FM_FULL[1:])
    assert "warning" not in proc.stderr.lower()


def test_the_default_marker_is_templates_tachi_version_under_the_working_directory(tmp_path):
    """Step 2.6 passes no --marker and runs from the project root: the default is cwd-relative."""
    project = tmp_path / "project"
    (project / "templates" / "tachi").mkdir(parents=True)
    write_marker(project / "templates" / "tachi", "v7.7.7")
    threats = fresh_threats(project, make_threats(FM_FULL))
    proc = run_stamp(threats, cwd=project)
    assert proc.returncode == 0, proc.stderr
    assert stamp_line("v7.7.7").encode() in threats.read_bytes()

    bare = tmp_path / "bare"  # a project whose install skipped the marker
    bare.mkdir()
    other = fresh_threats(bare, make_threats(FM_FULL))
    proc = run_stamp(other, cwd=bare)
    assert proc.returncode == 0, proc.stderr
    assert stamp_line("unknown").encode() in other.read_bytes()
    assert "warning" in proc.stderr.lower()


@pytest.mark.parametrize("value", ["1234567", "1.50", "true", "null", "0x1f", "1e5"])
def test_the_stamped_value_always_reads_back_as_a_yaml_string(tmp_path, value):
    """``git describe --always`` can print an all-digit hash; unquoted it would parse as a number."""
    threats, _marker, proc = stamped_by_cli(tmp_path, make_threats(FM_FULL), value=value)
    assert proc.returncode == 0, proc.stderr
    data = yaml.safe_load(parser_frontmatter_text(threats.read_bytes().decode("utf-8")))
    assert data[NEW_KEY] == value and isinstance(data[NEW_KEY], str)


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits")
def test_stamp_keeps_the_file_mode(tmp_path):
    threats = fresh_threats(tmp_path, make_threats(FM_FULL))
    threats.chmod(0o640)
    marker = write_marker(tmp_path)
    assert run_stamp(threats, marker=marker, cwd=tmp_path).returncode == 0
    assert stat.S_IMODE(threats.stat().st_mode) == 0o640
    assert project_files(tmp_path) == ["VERSION", "threats.md"]


def test_json_summary(tmp_path):
    threats = fresh_threats(tmp_path, make_threats(FM_FULL))
    marker = write_marker(tmp_path, "v3.1.4")
    first = json.loads(run_stamp(threats, "--json", marker=marker, cwd=tmp_path).stdout)
    assert first["status"] == "stamped" and first["tachi_version"] == "v3.1.4"
    assert first["warnings"] == [] and first["check"] is False
    second = json.loads(run_stamp(threats, "--json", marker=marker, cwd=tmp_path).stdout)
    assert second["status"] == "unchanged"
    write_marker(tmp_path, "v3.1.5")
    stale = run_stamp(threats, "--json", "--check", marker=marker, cwd=tmp_path)
    assert stale.returncode == 1 and json.loads(stale.stdout)["status"] == "stale"


def test_the_stamp_writes_no_key_but_tachi_version(tmp_path):
    """CF-21 (decision in t038a-measurement.md): ``schema_version`` stays model-authored.

    Writing it from ``schemas/output.yaml`` was measured and is not zero-churn: five
    infographic goldens embed a ``schema_version``. So the stamp never touches that line and
    the ``--schema-version-from-template`` flag is not built. Building it means re-measuring,
    regenerating those goldens and updating this test, in one reviewed change.
    """
    stale_schema = ['schema_version: "1.1"'] + FM_FULL[1:]
    threats, _marker, proc = stamped_by_cli(tmp_path, make_threats(stale_schema))
    assert proc.returncode == 0, proc.stderr
    still_1_1 = make_threats(stale_schema[:1] + [stamp_line()] + stale_schema[1:])
    assert threats.read_bytes() == still_1_1

    other = tmp_path / "other"
    other.mkdir()
    before = make_threats(FM_FULL)
    path = fresh_threats(other, before)
    flagged = run_stamp(path, "--schema-version-from-template", marker=write_marker(other), cwd=other)
    assert flagged.returncode == 2 and "schema-version-from-template" in flagged.stderr
    assert path.read_bytes() == before


def test_stamp_is_lossless_on_every_tracked_threats_md(tmp_path, stamp_module):
    """The stamp finds frontmatter in exactly the files the parsers do, and changes only one line.

    Runs over every ``threats.md`` under ``examples/`` and ``tests/scripts/fixtures/``:
    a file whose frontmatter the parsers read gains one line (after ``schema_version``)
    and nothing else; a file without gets exit 2 and is untouched. ``--check`` then
    passes and a second run is byte-identical.
    """
    marker = write_marker(tmp_path, "v4.48.2")
    wanted = (stamp_line("v4.48.2")).encode("utf-8")
    problems, with_frontmatter, without = [], 0, 0
    for index, source in enumerate(tracked_threats_files()):
        name = source.relative_to(REPO_ROOT).as_posix()
        text = remove_top_level_tachi_version(read_text(source))
        before = text.encode("utf-8")
        work = tmp_path / ("%03d.md" % index)
        work.write_bytes(before)
        code, _out, err = stamp_in_process(stamp_module, work, marker)

        if parser_frontmatter_text(text) is None:
            without += 1
            if code != 2 or work.read_bytes() != before:
                problems.append("%s: the parsers see no frontmatter, the stamp exited %s" % (name, code))
            continue
        with_frontmatter += 1
        if code != 0:
            problems.append("%s: the parsers see frontmatter, the stamp exited %s (%s)" % (
                name, code, err.strip()))
            continue
        lines_before = before.splitlines(keepends=True)
        lines_after = work.read_bytes().splitlines(keepends=True)
        added = [i for i, line in enumerate(lines_after) if line.rstrip(b"\r\n") == wanted]
        anchors = [i for i, line in enumerate(lines_before) if re.match(rb"schema_version[ \t]*:", line)]
        if len(added) != 1 or lines_after[:added[0]] + lines_after[added[0] + 1:] != lines_before:
            problems.append("%s: the stamp changed more than one line" % name)
        elif anchors and added[0] != anchors[0] + 1:
            problems.append("%s: the line is not right after schema_version" % name)
        after_text = work.read_bytes().decode("utf-8")
        if tachi_parsers.parse_frontmatter(after_text) != tachi_parsers.parse_frontmatter(text):
            problems.append("%s: parse_frontmatter reads the stamped file differently" % name)
        snapshot = work.read_bytes()
        if stamp_in_process(stamp_module, work, marker, "--check")[0] != 0:
            problems.append("%s: --check fails right after the stamp" % name)
        if stamp_in_process(stamp_module, work, marker)[0] != 0 or work.read_bytes() != snapshot:
            problems.append("%s: a second run changed the file" % name)
    assert with_frontmatter >= 10, "only %d tracked threats.md files have frontmatter" % with_frontmatter
    assert not problems, "the stamp misbehaves on tracked files (%d with frontmatter, %d without):\n  %s" % (
        with_frontmatter, without, "\n  ".join(problems))


def module_level_imports(tree):
    """Import and ImportFrom nodes that run at import time: the S-13 walk in
    ``test_install_manifest_completeness.py``, which never descends into def or class bodies."""
    nodes = []

    def walk(statements):
        for node in statements:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                nodes.append(node)
            elif isinstance(node, ast.If):
                walk(node.body)
                walk(node.orelse)
            elif isinstance(node, ast.Try) or type(node).__name__ == "TryStar":
                walk(node.body)
                for handler in node.handlers:
                    walk(handler.body)
                walk(node.orelse)
                walk(node.finalbody)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                walk(node.body)

    walk(tree.body)
    return nodes


def test_the_stamp_script_imports_only_the_standard_library():
    """P0B0-8: the distributable stamp must not need PyYAML (CI installs it, so CI would not notice)."""
    if sys.version_info < (3, 10):
        pytest.skip("sys.stdlib_module_names needs Python >= 3.10")
    tree = ast.parse(read_text(STAMP_SCRIPT), filename=str(STAMP_SCRIPT))
    foreign = []
    for node in module_level_imports(tree):
        tops = ([alias.name.split(".")[0] for alias in node.names] if isinstance(node, ast.Import)
                else [(node.module or "").split(".")[0] if node.level == 0 else "<relative>"])
        foreign += ["line %d: %s" % (node.lineno, top) for top in tops if top not in sys.stdlib_module_names]
    assert not foreign, "stamp-tachi-version.py imports outside the standard library: %s" % foreign


@pytest.mark.parametrize("path", [STAMP_SCRIPT, Path(__file__)], ids=["stamp-script", "this-module"])
def test_python_3_9_syntax(path):
    """Both files parse with the Python 3.9 grammar (CI adds a 3.9 run)."""
    ast.parse(read_text(path), filename=str(path), feature_version=(3, 9))


# =============================================================================
# Case 5. Step 2.6 is in tachi.threat-model.md, between Step 2.5 and Step 3
# =============================================================================


@pytest.fixture(scope="module")
def command_text():
    return read_text(THREAT_MODEL_COMMAND)


def level_2_headings(text):
    """``(line index, heading line)`` for each ``## `` heading outside a code fence."""
    found, in_fence = [], False
    for index, line in enumerate(text.split("\n")):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            found.append((index, line))
    return found


def step_2_6_body(text):
    lines = text.split("\n")
    headings = level_2_headings(text)
    starts = [i for i, (_index, line) in enumerate(headings) if line.startswith("## Step 2.6:")]
    assert len(starts) == 1, "expected exactly one '## Step 2.6:' heading, found %d" % len(starts)
    start = headings[starts[0]][0]
    end = headings[starts[0] + 1][0] if starts[0] + 1 < len(headings) else len(lines)
    return "\n".join(lines[start:end])


def test_the_command_frontmatter_has_only_the_expected_keys(command_text):
    """Step 2.6 is a body edit: the command's frontmatter (unchanged from 97db2e6) is just ``description``."""
    assert command_text.startswith("---\n")
    block = command_text.split("\n---\n", 1)[0]
    keys = set(re.findall(r"(?m)^([A-Za-z][\w-]*):", block))
    assert keys == EXPECTED_COMMAND_FRONTMATTER_KEYS


def test_step_2_6_sits_between_step_2_5_and_step_3(command_text):
    steps = [line for _index, line in level_2_headings(command_text) if line.startswith("## Step ")]
    labels = [re.match(r"## Step ([\d.]+):", line).group(1) for line in steps]
    assert labels.count("2.6") == 1, "Step 2.6 headings: %s" % labels
    position = labels.index("2.6")
    assert labels[position - 1:position + 2] == ["2.5", "2.6", "3"], "step order: %s" % labels
    assert labels == sorted(labels, key=lambda label: [int(part) for part in label.split(".")]), labels


def test_step_2_6_runs_the_stamp_exactly_as_specified(command_text):
    body = step_2_6_body(command_text)
    blocks = re.findall(r"```bash\n(.*?)\n```", body, re.DOTALL)
    assert len(blocks) == 1, "Step 2.6 holds %d bash blocks, expected one" % len(blocks)
    # Exactly the T039 command: no --schema-version-from-template (CF-21), no other flag.
    assert [line for line in blocks[0].split("\n") if line.strip()] == [STEP_COMMAND]


def test_step_2_6_reports_a_failure_and_carries_on(command_text):
    body = " ".join(step_2_6_body(command_text).split())
    assert FAILURE_LINE in body, "Step 2.6 lost the line it adds to the Step 3 summary"
    assert re.search(r"do not retry", body, re.IGNORECASE)
    assert re.search(r"never writes? or edits? `?tachi_version`?", body, re.IGNORECASE)


# =============================================================================
# Case 6. Consumer guidance: output-schemas.md and the comments of output.yaml
# =============================================================================


def plain(text):
    """Lower-case prose, without markdown emphasis or code ticks, whitespace collapsed."""
    return " ".join(re.sub(r"[`*]", "", text).split()).lower()


def output_yaml_comments():
    return "\n".join(match.group(1) for match in re.finditer(r"(?m)^\s*#(.*)$", read_text(OUTPUT_YAML)))


GUIDANCE_SOURCES = {
    "output-schemas.md": lambda: read_text(OUTPUT_SCHEMAS_MD),
    "output.yaml comments": output_yaml_comments,
}


@pytest.mark.parametrize("source", sorted(GUIDANCE_SOURCES))
def test_consumer_guidance_is_present(source):
    text = plain(GUIDANCE_SOURCES[source]())
    assert "feature-detect tachi_version" in text, "%s: no 'feature-detect tachi_version'" % source

    phrases = re.finditer(r"declared, not ordinal", text)
    leads = [text[max(0, found.start() - 220):found.start()] for found in phrases]
    assert any("schema_version" in lead and "1.5" in lead for lead in leads), (
        "%s: no 'schema_version older than 1.5 is declared, not ordinal'" % source)

    assert re.search(r"tachi_version: unknown.{0,200}skip\w* the (version-)?marker", text), (
        "%s: no 'unknown: the install skipped the marker line'" % source)
    assert "model-authored" in text and "declared-only" in text, (
        "%s: no 'schema_version stays model-authored and declared-only' (CF-21)" % source)


def test_the_two_guidance_texts_point_at_each_other():
    """output.yaml names the reference file by a path that exists; the reference names output.yaml."""
    pointer = re.search(r"(\.claude/skills/\S+?/output-schemas\.md)", output_yaml_comments())
    assert pointer, "the output.yaml guidance comment no longer says where the same text lives"
    assert (REPO_ROOT / pointer.group(1)).resolve() == OUTPUT_SCHEMAS_MD.resolve()
    assert "schemas/output.yaml" in read_text(OUTPUT_SCHEMAS_MD)


# =============================================================================
# Case 7. The SARIF generator takes semanticVersion from the input first
# =============================================================================

# X-6 of the P0 architect checkpoint. ``generate-threats-sarif.py`` writes the SARIF's
# ``runs[0].tool.driver.semanticVersion`` from the ``schema_version`` the input's own
# frontmatter declares, so a regenerated SARIF agrees with the file it came from. Only when the
# input declares none does it use the version ``schemas/output.yaml`` declares. The three cases
# below pin that order. Each runs the real script (its ``main``) as a subprocess on a file under
# ``tmp_path`` and reads the SARIF it writes there: nothing under the repository is written.

# Not the version output.yaml declares (each case that relies on that asserts it), so a SARIF
# that says 1.4 can only have taken it from the input.
DECLARED_VERSION = "1.4"
# The two headings ``parse_findings`` needs. The version does not depend on a finding: no rows.
SARIF_SECTIONS = ["", "## 3. STRIDE Threat Tables", "", "## 5. Coverage Matrix"]
# BODY ends in a quoted example frontmatter that says schema_version 1.2. It is not the input's
# declaration, so a reader that took the version from anywhere but the frontmatter would return it.
SARIF_BODY = BODY + SARIF_SECTIONS


def sarif_semantic_version(tmp_path, data):
    """``semanticVersion`` of the SARIF the real generator writes for ``data``, a threats.md as bytes."""
    threats = fresh_threats(tmp_path, data)
    sarif = tmp_path / "threats.sarif"
    cmd = [sys.executable, "-I", "-B", str(SARIF_GENERATOR), str(threats), str(sarif)]
    proc = subprocess.run(cmd, cwd=str(tmp_path), **RUN)
    assert proc.returncode == 0, "generate-threats-sarif.py exited %s:\n%s" % (proc.returncode, proc.stderr)
    runs = json.loads(sarif.read_text(encoding="utf-8"))["runs"]
    assert len(runs) == 1
    return runs[0]["tool"]["driver"]["semanticVersion"]


def test_sarif_semantic_version_is_the_inputs_declared_schema_version(tmp_path, version):
    """An input declaring ``schema_version`` 1.4 gives ``semanticVersion`` 1.4, not output.yaml's."""
    assert DECLARED_VERSION != version, "the declared version must differ from output.yaml's"
    frontmatter = ['schema_version: "%s"' % DECLARED_VERSION] + FM_FULL[1:]
    found = sarif_semantic_version(tmp_path, make_threats(frontmatter, body=SARIF_BODY))
    assert found == DECLARED_VERSION, "semanticVersion is %r; the input declares %r and output.yaml %r" % (
        found, DECLARED_VERSION, version)


def test_sarif_semantic_version_falls_back_to_output_yaml_without_a_declaration(tmp_path, version):
    """An input with no ``schema_version`` gives the version ``schemas/output.yaml`` declares.

    ``version`` is parsed from output.yaml (the ``version`` fixture), never written here, so the
    case follows a bump of the schema. The body's quoted example frontmatter is not a declaration.
    """
    assert not any(line.startswith("schema_version") for line in FM_BLOCK_LAST)
    assert any(line.startswith("schema_version") for line in SARIF_BODY), "the body lost its look-alike line"
    found = sarif_semantic_version(tmp_path, make_threats(FM_BLOCK_LAST, body=SARIF_BODY))
    assert found == version, "semanticVersion is %r; the input declares none, so output.yaml's %r" % (
        found, version)


def test_sarif_semantic_version_is_read_from_fenced_frontmatter(tmp_path, version):
    """The code-fenced form (a ``---`` block inside a ``yaml`` fence) is honoured as in the first case."""
    assert DECLARED_VERSION != version, "the declared version must differ from output.yaml's"
    frontmatter = ['schema_version: "%s"' % DECLARED_VERSION] + FM_FULL[1:]
    data = make_threats(frontmatter, fenced=True, body=SARIF_BODY)
    text = data.decode("utf-8")
    # The input really is the fenced shape, and the reader the generator uses finds the declaration in it.
    reader_sees = parser_frontmatter_text(text)
    assert not text.startswith("---"), "a fenced input does not open with the frontmatter itself"
    assert reader_sees and 'schema_version: "%s"' % DECLARED_VERSION in reader_sees
    found = sarif_semantic_version(tmp_path, data)
    assert found == DECLARED_VERSION, "semanticVersion is %r; the fenced input declares %r and output.yaml %r" % (
        found, DECLARED_VERSION, version)
