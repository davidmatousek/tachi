"""Contract-text tests for F-374, W1 to W3 (T010, T029 to T031, T037, T038, T051; ADR-050 D16; spec US-4 #5, FR-N4.1,
FR-N4.4, FR-E.1, FR-E.3, FR-K6.3, FR-K7.4, FR-K8.3, FR-N14.1).

The agent specs, the shared references and the shipped helpers state one contract in three places.
This module keeps the places in step. It reads text, and it never runs a script, writes a file or
touches the network. It is the first writer's module (lane O1, W1); later lanes add their sections
after section 12 and reuse the helpers in sections 1 and 3 to 9 and 12: ``text_of``, ``table_after``,
``fences``, ``command_problems``, ``directive_hits``, ``diff``, ``Family``, ``calls`` and ``routes``.

Inputs (read-only; repository-relative; every one matches an existing ``paths:`` glob of
``tachi-install-fidelity.yml``):

- ``.claude/agents/tachi/*.md``: the 21 agent specs, and ``.claude/commands/tachi.*.md``.
- ``templates/tachi/output-schemas/risk-scores.md`` and ``.sarif``, and the scorer's references under
  ``.claude/skills/tachi-risk-scoring/references/`` (section 12).
- ``.claude/skills/tachi-control-analysis/references/``, ``adapters/claude-code/agents/references/sarif-generation.md``
  and the controls spec and command named above (section 13).
- ``.claude/skills/tachi-shared/SKILL.md`` and its references ``agent-roster-shared.md``,
  ``sarif-identity-shared.md``, ``part-file-contract-shared.md``, ``finding-format-shared.md``,
  ``stride-categories-shared.md`` and ``dispatch-record-brief-shared.md``.
- ``.claude/skills/tachi-orchestration/SKILL.md`` and ``references/coverage-requirements.md``, and every
  other ``.claude/skills/**`` Markdown file (section 7 scans them for a load of the staged reference).
- ``schemas/coverage-checklists.yaml`` (its comment table; read as text, never parsed as YAML),
  ``INSTALL_MANIFEST.md``, ``adapters/claude-code/README.md`` and ``adapters/claude-code/agents/*.md``.
- ``scripts/tachi_parts.py``, ``scripts/tachi_scoring.py`` and ``scripts/sarif_common.py``, imported, and
  ``scripts/extract-report-data.py``, ``scripts/extract-infographic-data.py`` and ``scripts/tachi_parsers.py``,
  read as text for their imports (section 11).

What each section proves:

1. and 2. The helpers. Fences, tables and anchors are read the same way for every reference. A
   reference that loses an anchor or a table fails with a message that names it, never with a
   silent empty match.
3. The 21 agent specs: none carries the platform-neutral clause, none tells an agent to hand back
   code, write a program for someone else or substitute an agent type, the six edited specs state the
   no-hand-back rule, and the two dispatching specs name typed roster agents and stop when one can't
   be spawned (T008, T009; US-4 #5). The scanner is shown red on sample sentences.
4. The adapter copies carry R-17's superseded-by header, and the adapter README warns first (FR-C.1).
5. One roster: ``agent-roster-shared.md`` equals the agent files, and every other list of agents is a
   projection of it (FR-N4.1; the architect's ruling E). The three new PR 1 references are in the
   shared skill's Loading Table with the consumers they declare.
6. The orchestrator's shell fences are single ``python3`` calls of shipped scripts (FR-N4.4; guard C6).
7. PR 1's Track O text is inert (ADR-050 D11, spec S-5). **PR 2 flips this section** (T094).
8. ``sarif-identity-shared.md`` equals ``sarif_common`` (T005): tools, categories, rule IDs, the
   three ``tachi-plh/1`` vectors, ruling C's sentences, the resolver's and the result's names, the
   result shape and key order, and the 14 emitter constants. The ``dormant`` status of
   ``threats.sarif`` is PR 1's too, and PR 2 (T101) flips it.
9. ``part-file-contract-shared.md`` equals ``tachi_parts`` (T006): the 24 key sets, the closed
   values, the slot table, the 24 fixed sentences, the 28 flag fields, the identifiers and the limits.
10. The same reference against the validator's behavior: each field is cut where the table says, and
   each narrative slip takes the table's sentence.
11. The two extraction preflights (report assembler, infographic agent) check the extractor and every
   helper that it imports at load, which is its module-level import closure over ``scripts/``.
12. W2, lane C. The risk scorer's spec is judgment-only: it loads the part contract, states the check in
   the reference's words, and its example part passes the validator. ``/tachi.risk-score`` runs the
   presence check, plans once, dispatches the typed agent with the fixed prompt, waits for completion
   (ADR-050 D6's dated note), reconciles from disk, renders, and fails through ``tachi-stage.py fail``;
   each step routes every exit code of its script, and only shipped scripts run. ``/tachi.threat-model``
   gains its presence check (Step 1) and the architecture-source upsert (Step 2.7) under P-2's anchors.
   The scorer's template and references document the renderer and agree with the code.
13. W3, lane D. The control analyzer's spec is judgment-only, as the scorer's is: it loads the part contract, states the
   check in the reference's words, and its example part passes the validator. ``/tachi.compensating-controls`` has the
   scorer command's loop: the presence check, a plan made once with the command's date, the scored input and the target,
   waves under the completion rule, a reconcile from disk, the renderer, the summary and Step F (``--reason
   agent-not-spawned`` included), each step routed by the exit table, and only shipped scripts run (T038). The three
   controls references document the renderer and agree with the code, and the installed SARIF guide no longer tells an
   agent to author a file that a renderer owns.

Every comparison parses the reference and compares it with the code, so it fails when either side
drifts. Each comparison has a negative control that edits one side and expects a mismatch. A parser
that finds nothing would pass a comparison with an empty code value, so one test pins the counts that
the contracts state.

Stdlib and pytest only; Python 3.9 syntax; ASCII source.
"""
from __future__ import annotations

import ast
import functools
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, NamedTuple, Optional, Sequence, Set, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common as sc  # noqa: E402  -- after the sys.path mutation
import tachi_parts  # noqa: E402
import tachi_scoring  # noqa: E402


# =============================================================================
# 1. Paths, constants and the Markdown helpers
# =============================================================================

# The one name that T005's Rule IDs table is tested against. ``RULE_ID_BY_PREFIX`` is the long-form
# map with ``TE``; the legacy ``PREFIX_TO_RULE`` keeps the short AI forms for the old generators.
# The architect confirms the choice (T023), so a different map is a one-line change here.
RULE_MAP_NAME = "RULE_ID_BY_PREFIX"

# Track O's roster projection that PR 2 owns (lane O3). It is named so the list is whole, and it is
# not asserted: PR 1 leaves the file as it is.
PR2_ROSTER_PROJECTIONS = (".claude/skills/tachi-orchestration/references/output-schemas.md",)

AGENTS_DIR = ".claude/agents/tachi"
COMMANDS_DIR = ".claude/commands"
SKILLS_DIR = ".claude/skills"
SHARED = SKILLS_DIR + "/tachi-shared"
SHARED_REFS = SHARED + "/references"
ROSTER = SHARED_REFS + "/agent-roster-shared.md"
SARIF_IDENTITY = SHARED_REFS + "/sarif-identity-shared.md"
PART_CONTRACT = SHARED_REFS + "/part-file-contract-shared.md"
FINDING_FORMAT = SHARED_REFS + "/finding-format-shared.md"
STRIDE_CATEGORIES = SHARED_REFS + "/stride-categories-shared.md"
DISPATCH_RECORD_BRIEF = SHARED_REFS + "/dispatch-record-brief-shared.md"
SHARED_SKILL = SHARED + "/SKILL.md"
ORCHESTRATION = SKILLS_DIR + "/tachi-orchestration"
ORCHESTRATION_SKILL = ORCHESTRATION + "/SKILL.md"
COVERAGE_REQUIREMENTS = ORCHESTRATION + "/references/coverage-requirements.md"
COVERAGE_CHECKLISTS = "schemas/coverage-checklists.yaml"
INSTALL_MANIFEST = "INSTALL_MANIFEST.md"
ADAPTER_README = "adapters/claude-code/README.md"
ADAPTER_AGENTS = "adapters/claude-code/agents"

# The six specs that T008 and T009 edited, and the two that dispatch other agents.
SIX_SPECS = ("orchestrator", "risk-scorer", "control-analyzer", "threat-report", "report-assembler",
             "threat-infographic")
DISPATCHING_SPECS = ("orchestrator", "threat-report")
# The adapter copies that carry R-17's header. ``risk-scorer`` came with the scorer's rewrite (T030, W2).
ADAPTER_COPIES_WITH_HEADER = ("orchestrator", "risk-scorer", "threat-report", "threat-infographic")

# S1: the no-hand-back sentence (US-4 #5). Every spec in SIX_SPECS carries it, in its ``**Contract.**`` paragraph.
NO_HAND_BACK = ("You return no code: you never hand back a program for your caller to run, "
                "and you never write a program for someone else to run.")


class ReferenceDrift(AssertionError):
    """A reference no longer has the shape this module reads: an anchor, a table or a sentence moved."""


@functools.lru_cache(maxsize=None)
def text_of(relative: str) -> str:
    """The text of a repository file, by its repository-relative path."""
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def agent_stems() -> Tuple[str, ...]:
    """The stems of the agent specs: every ``.md`` in the agents directory except the guidance document."""
    return tuple(sorted(p.stem for p in (REPO_ROOT / AGENTS_DIR).glob("*.md") if not p.name.startswith("_")))


AGENT_STEMS = agent_stems()


def spec_text(stem: str) -> str:
    return text_of("%s/%s.md" % (AGENTS_DIR, stem))


class Table(NamedTuple):
    header: List[str]
    rows: List[List[str]]


_FENCE_LINE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_HEADING = re.compile(r"^(#{1,6}) ")
_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_TICKED = re.compile(r"`([^`]+)`")
_JOINER = re.compile(r", or |, | or | and ")


def fence_mask(lines: Sequence[str]) -> List[bool]:
    """True for every line inside a fenced block, the fence lines included."""
    mask: List[bool] = []
    fence: Optional[Tuple[str, int]] = None
    for line in lines:
        match = _FENCE_LINE.match(line)
        if fence is None:
            if match:
                fence = (match.group(1)[0], len(match.group(1)))
            mask.append(fence is not None)
        else:
            mask.append(True)
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] and not match.group(2).strip():
                fence = None
    return mask


class Fence(NamedTuple):
    label: str
    body: str


def fences(text: str) -> List[Fence]:
    """Every fenced block: its info string, and its lines with the opening fence's indentation removed."""
    found: List[Fence] = []
    fence: Optional[Tuple[str, int, int]] = None
    label = ""
    body: List[str] = []
    for line in text.splitlines():
        match = _FENCE_LINE.match(line)
        if fence is None:
            if match:
                indent = len(line) - len(line.lstrip(" "))
                fence = (match.group(1)[0], len(match.group(1)), indent)
                label = match.group(2).strip()
                body = []
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] and not match.group(2).strip():
            found.append(Fence(label, "\n".join(body)))
            fence = None
        else:
            body.append(line[fence[2]:] if line[:fence[2]].strip() == "" else line)
    return found


def split_row(line: str) -> List[str]:
    """The cells of one Markdown table row. ``\\|`` is a pipe inside a cell."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", body)]


def anchor_index(lines: Sequence[str], mask: Sequence[bool], anchor: str, where: str = "") -> int:
    """The one line outside a fence that starts with ``anchor``. No such line, or two, is drift."""
    hits = [i for i, line in enumerate(lines) if not mask[i] and line.startswith(anchor)]
    if len(hits) != 1:
        raise ReferenceDrift("%s: expected exactly one line starting %r, found %d" % (where or "the reference", anchor, len(hits)))
    return hits[0]


def section_end(lines: Sequence[str], mask: Sequence[bool], start: int) -> int:
    """The line after a section. A heading ends at the next heading of its level or above, any other line at the next heading."""
    own = _HEADING.match(lines[start])
    level = len(own.group(1)) if own else 6
    for i in range(start + 1, len(lines)):
        match = _HEADING.match(lines[i])
        if match and not mask[i] and len(match.group(1)) <= level:
            return i
    return len(lines)


def tables_between(lines: Sequence[str], mask: Sequence[bool], start: int, end: int) -> List[Table]:
    tables: List[Table] = []
    i = start
    while i < end:
        if (not mask[i] and lines[i].lstrip().startswith("|") and i + 1 < end
                and not mask[i + 1] and _SEPARATOR.match(lines[i + 1])):
            rows: List[List[str]] = []
            j = i + 2
            while j < end and not mask[j] and lines[j].lstrip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            tables.append(Table(split_row(lines[i]), rows))
            i = j
        else:
            i += 1
    return tables


def table_after(text: str, anchor: str, nth: int = 0, where: str = "") -> Table:
    """The ``nth`` pipe table after the one line that starts with ``anchor``, before the next heading."""
    lines = text.splitlines()
    mask = fence_mask(lines)
    start = anchor_index(lines, mask, anchor, where)
    tables = tables_between(lines, mask, start + 1, section_end(lines, mask, start))
    if len(tables) <= nth:
        raise ReferenceDrift("%s: no table number %d after %r" % (where or "the reference", nth, anchor))
    return tables[nth]


def section_text(text: str, anchor: str, where: str = "", keep_fences: bool = False) -> str:
    """The lines of one section, without its heading line. Fenced lines are left out unless ``keep_fences``."""
    lines = text.splitlines()
    mask = fence_mask(lines)
    start = anchor_index(lines, mask, anchor, where)
    end = section_end(lines, mask, start)
    return "\n".join(lines[i] for i in range(start + 1, end) if keep_fences or not mask[i])


def ticks(cell: str) -> List[str]:
    """Every backticked token in a cell, in order."""
    return _TICKED.findall(cell)


def strip_ticks(cell: str) -> str:
    match = re.fullmatch(r"`([^`]+)`", cell.strip())
    return match.group(1) if match else cell.strip()


def plain(cell: str) -> str:
    return cell.replace("`", "").strip()


def enum_after(cell: str, marker: str = "") -> List[str]:
    """The run of backticked tokens that starts after ``marker``, joined by ``, ``, `` or `` and `` and ``."""
    start = cell.find(marker) if marker else 0
    if start < 0:
        raise ReferenceDrift("no %r in the cell %r" % (marker, cell[:80]))
    pos = start + len(marker)
    out: List[str] = []
    match = _TICKED.match(cell, pos)
    while match:
        out.append(match.group(1))
        joiner = _JOINER.match(cell, match.end())
        if not joiner:
            break
        match = _TICKED.match(cell, joiner.end())
    if not out:
        raise ReferenceDrift("no backticked values after %r in the cell %r" % (marker, cell[:80]))
    return out


def frontmatter_lines(text: str) -> List[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return []


def frontmatter_scalar(text: str, key: str) -> Optional[str]:
    for line in frontmatter_lines(text):
        match = re.match(r"%s:\s*(.*?)\s*$" % re.escape(key), line)
        if match:
            return match.group(1)
    return None


def frontmatter_list(text: str, key: str) -> List[str]:
    out: List[str] = []
    inside = False
    for line in frontmatter_lines(text):
        if inside:
            item = re.match(r"\s+-\s+(.+?)\s*$", line)
            if not item:
                break
            out.append(item.group(1))
        elif re.match(r"%s:\s*$" % re.escape(key), line):
            inside = True
    return out


def diff(label: str, doc: Any, code: Any) -> List[str]:
    """The differences between the reference's value and the code's, one line each. An empty list means they agree."""
    if isinstance(doc, dict) and isinstance(code, dict):
        problems: List[str] = []
        for key in sorted(set(doc) | set(code), key=str):
            if key not in code:
                problems.append("%s: the reference has %r and the code doesn't" % (label, key))
            elif key not in doc:
                problems.append("%s: the code has %r and the reference doesn't" % (label, key))
            else:
                problems.extend(diff("%s[%r]" % (label, key), doc[key], code[key]))
        return problems
    if isinstance(doc, (set, frozenset)) and isinstance(code, (set, frozenset)):
        problems = []
        if doc - code:
            problems.append("%s: only in the reference: %s" % (label, sorted(doc - code, key=str)))
        if code - doc:
            problems.append("%s: only in the code: %s" % (label, sorted(code - doc, key=str)))
        return problems
    if doc != code:
        return ["%s: the reference says %r, the code says %r" % (label, doc, code)]
    return []


# =============================================================================
# 2. The helpers, on small samples
# =============================================================================

SAMPLE = """\
# Title

Intro paragraph.

## Section A

| Key | Type |
|-----|------|
| `a` | one \\| two |
| `b` | optional. Three |

```
## Not a heading
| x | y |
|---|---|
| 1 | 2 |
```

**Bold lead.** Text.

| Name | Value |
|------|-------|
| `c` | 1 |

## Section B

| Other | Table |
|-------|-------|
| `d` | 4 |
"""


def test_a_table_is_read_with_escaped_pipes_and_without_fenced_lookalikes():
    table = table_after(SAMPLE, "## Section A")
    assert table.header == ["Key", "Type"]
    assert table.rows == [["`a`", "one | two"], ["`b`", "optional. Three"]]
    assert table_after(SAMPLE, "**Bold lead.**").rows == [["`c`", "1"]]
    assert table_after(SAMPLE, "## Section A", nth=1).rows == [["`c`", "1"]]
    assert table_after(SAMPLE, "## Section B").rows == [["`d`", "4"]]


def test_a_missing_or_ambiguous_anchor_and_a_missing_table_are_drift():
    with pytest.raises(ReferenceDrift):
        table_after(SAMPLE, "## Section C")
    with pytest.raises(ReferenceDrift):
        table_after(SAMPLE, "## Not a heading")  # inside a fence, so it is not there
    with pytest.raises(ReferenceDrift):
        table_after(SAMPLE, "## Section B", nth=1)
    with pytest.raises(ReferenceDrift):
        table_after("## Dup\n\n## Dup\n", "## Dup")


def test_fences_come_back_dedented_with_their_labels():
    text = "1. Item\n\n   ```text\n   TACHI X FAILED\n   Agent: y\n   ```\n\n```bash\npython3 scripts/a.py\n```\n"
    assert fences(text) == [Fence("text", "TACHI X FAILED\nAgent: y"), Fence("bash", "python3 scripts/a.py")]


def test_an_enum_runs_over_commas_or_and_and_stops_before_other_words():
    assert enum_after("`a`, `b` or `c`") == ["a", "b", "c"]
    assert enum_after("`High`, `Medium` or `Low`, and `null` exactly when `x` is `y`") == ["High", "Medium", "Low"]
    assert enum_after("keys: `x`, `y` and `z`. Then `w`.", "keys: ") == ["x", "y", "z"]
    with pytest.raises(ReferenceDrift):
        enum_after("nothing here", "missing marker")


# =============================================================================
# 3. The agent specs: no clause, no hand-back, no substitute (T008, T009; US-4 #5)
# =============================================================================

PLATFORM_NEUTRAL = re.compile(r"platform[- ]neutral|work with any LLM|any LLM capable", re.IGNORECASE)

# A clause that tells an agent to hand back code, write a program for someone else, or use another
# agent type is a directive. A clause with one of these negations is a prohibition, so it passes.
# Plain "not", "can't" and "cannot" are not on the list: they open a condition ("if the agent can't be
# spawned, ..."), and a directive hides behind one. A condition ends at a comma, so it is its own clause.
_NEGATION = re.compile(
    r"\b(never|don't|do not|does not|doesn't|must not|mustn't|no|without|neither|nor)\b", re.IGNORECASE)
_CLAUSE = re.compile(r"[,;:]|\s+-+\s+|[()]")
_HAND_BACK = (
    re.compile(r"\b(?:return|hand(?:s|ing)? (?:back|over)|give back|send back|provide|emit|deliver|supply)\b"
               r"[^.\n]{0,30}\b(?:a|an|your own)\s+(?:\w+\s+){0,2}(?:script|program|code snippet)\b", re.IGNORECASE),
    re.compile(r"\b(?:return|hand(?:s|ing)? (?:back|over)|give back|send back)\s+(?:the |your |some )?"
               r"(?:python |shell |source |runnable )?code\b", re.IGNORECASE),
    re.compile(r"\b(?:write|generate|create|author|compose)\b[^.\n]{0,30}\b(?:a|an|your own)\s+(?:\w+\s+){0,2}"
               r"(?:script|program)\b", re.IGNORECASE),
)
_SUBSTITUTE = (
    re.compile(r"\bgeneral-purpose\b", re.IGNORECASE),
    re.compile(r"\b(stand-?in|fallback agent|another agent type|any other agent|any available agent)\b", re.IGNORECASE),
    re.compile(r"\bsubstitut\w*\b[^.\n]{0,40}\bagent", re.IGNORECASE),
    re.compile(r"\bagent\b[^.\n]{0,40}\bsubstitut\w*", re.IGNORECASE),
)
_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")


def prose(text: str) -> str:
    """The text outside fenced blocks."""
    lines = text.splitlines()
    mask = fence_mask(lines)
    return "\n".join(line for line, inside in zip(lines, mask) if not inside)


def directive_hits(text: str) -> List[str]:
    """The sentences of ``text`` that read as a directive to hand back code or to substitute an agent type."""
    hits: List[str] = []
    for sentence in _SENTENCE.split(prose(text)):
        for clause in _CLAUSE.split(sentence):
            if _NEGATION.search(clause):
                continue
            if any(pattern.search(clause) for pattern in _HAND_BACK + _SUBSTITUTE):
                hits.append(sentence.strip())
                break
    return hits


def test_the_agent_specs_are_the_21_the_roster_counts():
    assert len(AGENT_STEMS) == 21, AGENT_STEMS
    assert set(SIX_SPECS) <= set(AGENT_STEMS)


@pytest.mark.parametrize("stem", AGENT_STEMS)
def test_no_agent_spec_carries_the_platform_neutral_clause(stem):
    found = [m.group(0) for m in PLATFORM_NEUTRAL.finditer(spec_text(stem))]
    assert not found, "%s.md still says %s" % (stem, found)


@pytest.mark.parametrize("stem", SIX_SPECS)
def test_the_six_edited_specs_state_the_no_hand_back_rule_in_their_contract_paragraph(stem):
    text = spec_text(stem)
    assert text.count(NO_HAND_BACK) == 1, "%s.md must carry the no-hand-back sentence once" % stem
    paragraph = next(p for p in re.split(r"\n\s*\n", text) if NO_HAND_BACK in p)
    assert paragraph.startswith("**Contract.** "), "%s.md: the sentence belongs in the **Contract.** paragraph" % stem


@pytest.mark.parametrize("stem", AGENT_STEMS)
def test_no_agent_spec_tells_an_agent_to_hand_back_code_or_substitute_a_type(stem):
    hits = directive_hits(spec_text(stem))
    assert not hits, "%s.md has a directive: %s" % (stem, hits)


@pytest.mark.parametrize("sentence", [
    "If the output is too large, return a Python script that produces the rest.",
    "When your output won't fit, hand back a program for the caller to run.",
    "Write a script that regenerates the report, and ask the caller to run it.",
    "Generate a shell script for the next step.",
    "Hand back the code for the caller to run.",
    "If the typed agent is missing, dispatch a general-purpose agent instead.",
    "If the agent can't be spawned, dispatch a general-purpose agent instead.",
    "Use a stand-in when the agent is not installed.",
    "Substitute another agent for the missing one.",
])
def test_the_directive_scanner_flags_a_directive(sentence):
    assert directive_hits(sentence) == [sentence]


@pytest.mark.parametrize("sentence", [
    NO_HAND_BACK,
    "Never dispatch a `general-purpose` agent or any other type in a roster agent's place.",
    "Run no substitute, and don't retry under another type.",
    "You write no script of your own.",
    "The orchestrator doesn't hand back a program for anyone to run.",
    "If the agent can't be spawned, end the run there, and use no substitute agent.",
    "Invoke the deterministic Python extraction script to parse all artifacts.",
    "Write the output with the shipped script, and return the path of the script.",
    "Return in 15 lines or fewer per the subagent return policy.",
])
def test_the_directive_scanner_passes_a_prohibition_and_ordinary_text(sentence):
    assert directive_hits(sentence) == []


def test_the_directive_scanner_ignores_a_fenced_block():
    assert directive_hits("```\nWrite a script that does it.\n```\n") == []


# --- The dispatching specs: typed names, one stop form ---------------------------------------


def roster_rows(text: str) -> Tuple[List[Tuple[str, str, str, str, str]], List[Tuple[str, str]]]:
    """The Phase 2 roster rows ``(agent, dispatch key, category, emits, folds into)`` and the stage and helper rows."""
    phase2 = table_after(text, "## Phase 2 Roster (Threat Agents)", where="agent-roster-shared.md")
    helpers = table_after(text, "## Stage and Helper Agents", where="agent-roster-shared.md")
    return ([(strip_ticks(r[0]), r[1], r[2], r[3], r[4]) for r in phase2.rows],
            [(strip_ticks(r[0]), r[1]) for r in helpers.rows])


def roster_names() -> Set[str]:
    phase2, helpers = roster_rows(text_of(ROSTER))
    return {row[0] for row in phase2} | {row[0] for row in helpers}


def skill_directories() -> Set[str]:
    return {p.name for p in (REPO_ROOT / SKILLS_DIR).iterdir() if p.is_dir()}


def named_tachi_tokens(text: str) -> Set[str]:
    return set(re.findall(r"`(tachi-[a-z-]+)`", text))


def stop_forms(text: str) -> List[Tuple[str, str, str, str]]:
    """Every ``TACHI <STAGE> FAILED: agent not spawned`` block in ``text``: stage, tail, agent line, remedy line."""
    found = []
    for fence in fences(text):
        lines = [line for line in fence.body.splitlines() if line.strip()]
        match = re.fullmatch(r"TACHI (.+) FAILED: (agent not spawned)", lines[0]) if lines else None
        if match:
            found.append((match.group(1), match.group(2), lines[1] if len(lines) > 1 else "",
                          lines[2] if len(lines) > 2 else ""))
    return found


REMEDY_LINE = "Remedy: re-run the installer from this project's root: <tachi-repo>/scripts/install.sh"


@pytest.mark.parametrize("stem", DISPATCHING_SPECS)
def test_a_dispatching_spec_names_only_roster_agents_and_skills(stem):
    tokens = named_tachi_tokens(spec_text(stem))
    unknown = tokens - roster_names() - skill_directories()
    assert not unknown, "%s.md names something that is neither a roster agent nor a skill: %s" % (stem, sorted(unknown))
    assert "subagent_type" in spec_text(stem)


def test_the_orchestrator_dispatches_the_report_agent_by_its_type_and_reads_the_roster():
    text = spec_text("orchestrator")
    assert "`subagent_type` `tachi-threat-report`" in text
    assert text.count(ROSTER) >= 2, "the Skill References row and the MANDATORY Read both name the roster"
    for gone in ("is a prompt file in the sibling agent files", "reference the agent's prompt file",
                 "Platform-specific dispatch adapters"):
        assert gone not in text, "the orchestrator still says %r" % gone


def test_the_report_agent_names_its_one_helper_by_its_type():
    text = spec_text("threat-report")
    assert "setting `subagent_type` to `tachi-attack-tree-delta`" in text
    helpers = [name for name, _role in roster_rows(text_of(ROSTER))[1] if name != "tachi-orchestrator"]
    assert "tachi-attack-tree-delta" in helpers


def test_the_stop_form_is_the_roster_s_form_in_each_dispatching_spec():
    roster = stop_forms(text_of(ROSTER))
    assert len(roster) == 1 and roster[0][0] == "<STAGE>", roster
    assert roster[0][3] == REMEDY_LINE
    for stem, agent in (("orchestrator", "Agent: <subagent_type>"), ("threat-report", "Agent: tachi-attack-tree-delta")):
        forms = stop_forms(spec_text(stem))
        assert len(forms) == 1, "%s.md must carry the stop form once" % stem
        stage, tail, agent_line, remedy = forms[0]
        assert re.fullmatch(r"[A-Z][A-Z ]*[A-Z]", stage), stage
        assert (tail, agent_line, remedy) == (roster[0][1], agent, REMEDY_LINE)
    for stem in DISPATCHING_SPECS:
        assert "end the run there" in spec_text(stem) and "Run no substitute" in spec_text(stem), stem


def test_the_orchestrator_stops_on_a_missing_shipped_script_and_names_the_remedy():
    text = spec_text("orchestrator")
    assert "If a script this file names is missing, stop with an error that names the script and says to re-run `scripts/install.sh`" in text


# =============================================================================
# 4. The adapter copies and the adapter README (T009; FR-C.1, R-17)
# =============================================================================


@pytest.mark.parametrize("stem", ADAPTER_COPIES_WITH_HEADER)
def test_an_adapter_copy_of_an_edited_spec_carries_the_superseded_by_header(stem):
    lines = text_of("%s/%s.md" % (ADAPTER_AGENTS, stem)).splitlines()
    assert lines[0] == "---"
    close = lines.index("---", 1)
    head = [line for line in lines[close + 1:close + 6] if line.strip()]
    assert head, "%s: nothing after the frontmatter" % stem
    assert head[0].startswith("> **Superseded by `%s/%s.md`.**" % (AGENTS_DIR, stem)), head[0]
    assert "scripts/install.sh" in head[0] and "never copy this file over `.claude/agents/tachi/`" in head[0]
    assert "#369" in head[0]


def test_the_adapter_readme_warns_first_to_install_with_the_installer():
    top = "\n".join(text_of(ADAPTER_README).splitlines()[:6])
    assert top.startswith("# Claude Code Adapter")
    assert "> **Warning: install tachi with `scripts/install.sh`. Never copy this directory over `.claude/agents/tachi/`.**" in top


# =============================================================================
# 5. One roster (FR-N4.1; T007; the architect's ruling E)
# =============================================================================


def projection_agents(cell: str) -> Set[str]:
    return {name.strip() for name in cell.split(",") if name.strip()}


def comment_table(text: str, anchor: str) -> Table:
    """The pipe table written as ``# | ... |`` comment lines after the line that starts with ``anchor``."""
    lines = text.splitlines()
    start = anchor_index(lines, [False] * len(lines), anchor, COVERAGE_CHECKLISTS)
    block = []
    for line in lines[start + 1:]:
        if line.startswith("# |"):
            block.append(split_row(line[2:]))
        elif block:
            break
    if len(block) < 3:
        raise ReferenceDrift("%s: no comment table after %r" % (COVERAGE_CHECKLISTS, anchor))
    return Table(block[0], block[2:])


def roster_by_category(rows: Sequence[Tuple[str, str, str, str, str]]) -> Dict[str, Set[str]]:
    grouped: Dict[str, Set[str]] = {}
    for agent, _key, category, _emits, _folds in rows:
        grouped.setdefault(category, set()).add(agent)
    return grouped


def test_the_roster_is_the_21_agent_files_and_their_names():
    phase2, helpers = roster_rows(text_of(ROSTER))
    names = [row[0] for row in phase2] + [row[0] for row in helpers]
    assert len(phase2) == 14 and len(helpers) == 7 and len(set(names)) == 21
    assert set(names) == {"tachi-" + stem for stem in AGENT_STEMS}
    for stem in AGENT_STEMS:
        assert frontmatter_scalar(spec_text(stem), "name") == "tachi-" + stem, stem
    keys = [row[1] for row in phase2]
    assert (keys.count("AG"), keys.count("LLM"), len([k for k in keys if k in list("STRIDE")])) == (3, 5, 6)


def test_the_roster_order_is_the_orchestrator_s_dispatch_order():
    phase2, _ = roster_rows(text_of(ROSTER))
    by_key = {row[1]: row[0] for row in phase2 if row[1] in list("STRIDE")}
    sentence = re.search(r"in category order: (.+?)\. Collect findings", spec_text("orchestrator"), re.S)
    assert sentence, "the orchestrator's Sequential Mode sentence moved"
    order: List[str] = []
    for token in re.finditer(r"\b(AG|LLM)\s*\(([^)]*)\)|\b([STRIDE])\b", sentence.group(1)):
        if token.group(3):
            order.append(by_key[token.group(3)])
        else:
            order.extend("tachi-" + name.strip() for name in token.group(2).split(" then "))
    assert order == [row[0] for row in phase2]


def test_the_orchestrator_metadata_lists_the_phase_2_agent_files():
    text = spec_text("orchestrator")
    block = re.search(r"  agents:\n(.*?)\n    report:", text, re.S)
    assert block, "the orchestrator's metadata agents list moved"
    files = re.findall(r"- ([a-z-]+)\.md", block.group(1))
    assert {"tachi-" + name for name in files} == {row[0] for row in roster_rows(text_of(ROSTER))[0]}


def test_each_phase_2_agent_holds_the_tools_the_roster_says():
    text = text_of(ROSTER)
    claim = re.search(r"each Phase 2 threat agent holds ((?:`\w+`(?:, | and )?)+) and nothing else", text)
    assert claim, "the roster's tool claim moved"
    expected = set(ticks(claim.group(1)))
    for agent, *_ in roster_rows(text)[0]:
        assert set(frontmatter_list(spec_text(agent[len("tachi-"):]), "tools")) == expected, agent


def test_the_roster_s_consumers_are_the_specs_that_load_it():
    consumers = set(frontmatter_list(text_of(ROSTER), "consumers"))
    loaders = {stem for stem in AGENT_STEMS if "agent-roster-shared" in spec_text(stem)}
    assert consumers == loaders, "the roster lists %s as consumers, and %s load it" % (sorted(consumers), sorted(loaders))


NEW_PR1_REFERENCES = {
    "sarif-identity-shared.md": SARIF_IDENTITY,
    "part-file-contract-shared.md": PART_CONTRACT,
    "agent-roster-shared.md": ROSTER,
}


@pytest.mark.parametrize("name", sorted(NEW_PR1_REFERENCES))
def test_each_new_pr_1_reference_is_in_the_loading_table_with_the_consumers_it_declares(name):
    rows = [r for r in table_after(text_of(SHARED_SKILL), "## Loading Table", where=SHARED_SKILL).rows
            if strip_ticks(r[0]) == "references/" + name]
    assert len(rows) == 1, "the shared skill's Loading Table has no single row for %s" % name
    assert {c.strip() for c in rows[0][1].split(",")} == set(frontmatter_list(text_of(NEW_PR1_REFERENCES[name]), "consumers"))


@pytest.mark.parametrize("path, code", [(SARIF_IDENTITY, "scripts/sarif_common.py"), (PART_CONTRACT, "scripts/tachi_parts.py")])
def test_a_reference_names_the_shipped_code_that_implements_it(path, code):
    assert frontmatter_scalar(text_of(path), "source_code") == code
    assert (REPO_ROOT / code).is_file()


def test_the_id_prefix_table_in_finding_format_projects_the_roster():
    phase2, _ = roster_rows(text_of(ROSTER))
    table = table_after(text_of(FINDING_FORMAT), "### ID Prefix Table", where=FINDING_FORMAT)
    doc = {row[0]: projection_agents(row[2]) for row in table.rows}
    code: Dict[str, Set[str]] = {}
    for agent, key, *_ in phase2:
        code.setdefault(key, set()).add(agent)
    assert not diff("finding-format ID Prefix Table", doc, code)


def test_the_producer_table_in_finding_format_projects_the_roster():
    phase2, _ = roster_rows(text_of(ROSTER))
    table = table_after(text_of(FINDING_FORMAT), "### Producer ID Prefix Assignment", where=FINDING_FORMAT)
    doc = {row[0]: (row[1], row[2]) for row in table.rows}
    code = {agent: (category, emits) for agent, _key, category, emits, _folds in phase2}
    assert not diff("finding-format producer table", doc, code)


def test_the_category_to_agent_table_in_coverage_requirements_projects_the_roster():
    phase2, _ = roster_rows(text_of(ROSTER))
    table = table_after(text_of(COVERAGE_REQUIREMENTS), "### Category-to-Agent Mapping", where=COVERAGE_REQUIREMENTS)
    doc = {row[0]: projection_agents(row[1]) for row in table.rows}
    assert not diff("coverage-requirements category table", doc, roster_by_category(phase2))


def test_the_checklist_category_table_in_the_orchestration_skill_projects_the_roster():
    phase2, _ = roster_rows(text_of(ROSTER))
    table = table_after(text_of(ORCHESTRATION_SKILL), "Category strings map to finding ID prefixes", where=ORCHESTRATION_SKILL)
    doc = {strip_ticks(row[0]): (row[1], projection_agents(row[2])) for row in table.rows}
    key_of = {category: key for _agent, key, category, _emits, _folds in phase2}
    code = {category: (key_of[category], agents) for category, agents in roster_by_category(phase2).items()}
    assert not diff("orchestration SKILL checklist table", doc, code)


def test_the_comment_table_in_coverage_checklists_projects_the_roster():
    phase2, _ = roster_rows(text_of(ROSTER))
    table = comment_table(text_of(COVERAGE_CHECKLISTS), "# Category-to-Agent Mapping")
    doc = {row[0]: projection_agents(row[1]) for row in table.rows}
    assert not diff("coverage-checklists comment table", doc, roster_by_category(phase2))


def test_stride_categories_names_only_roster_agents_and_defers_to_the_roster():
    text = text_of(STRIDE_CATEGORIES)
    assert ("Where an agent list in this file differs from the canonical roster in `%s`, the roster governs." % ROSTER) in text
    assert named_tachi_tokens(text) - skill_directories() <= roster_names()


@pytest.mark.parametrize("path", [FINDING_FORMAT, COVERAGE_REQUIREMENTS, ORCHESTRATION_SKILL, COVERAGE_CHECKLISTS, STRIDE_CATEGORIES])
def test_each_projection_says_the_roster_governs(path):
    text = text_of(path)
    assert ROSTER in text and "governs" in text, "%s doesn't say the roster governs" % path


# =============================================================================
# 6. The orchestrator's fences (FR-N4.4; guard C6)
# =============================================================================

SHELL_LABELS = ("bash", "sh", "shell", "zsh")


def shipped_scripts() -> Set[str]:
    """The ``scripts/<name>.py`` entries in the installer's machine-readable manifest block."""
    text = text_of(INSTALL_MANIFEST)
    block = re.search(r"<!-- BEGIN MANIFEST -->\n(.*?)<!-- END MANIFEST -->", text, re.S)
    if not block:
        raise ReferenceDrift("INSTALL_MANIFEST.md has no manifest block")
    return {line.strip() for line in block.group(1).splitlines() if re.fullmatch(r"scripts/[A-Za-z0-9_.-]+\.py", line.strip())}


_FORBIDDEN_IN_A_COMMAND = re.compile(r"\$\(|`|\bxargs\b|\bbash\s+-c\b|\beval\b|&&|\|\||;|\||&|>|<\(")


def command_problems(body: str, shipped: Set[str]) -> List[str]:
    """Why a shell fence is not a single ``python3`` call of a shipped script with literal arguments. An empty list is a pass."""
    joined = re.sub(r"\\\n\s*", " ", body).strip()
    commands = [line.strip() for line in joined.splitlines() if line.strip() and not line.strip().startswith("#")]
    if len(commands) != 1:
        return ["a fence holds %d commands, not one" % len(commands)]
    command = commands[0]
    problems = []
    without_placeholders = re.sub(r"<[a-z_]+>|\{[a-z_]+\}", "", command)
    if _FORBIDDEN_IN_A_COMMAND.search(without_placeholders):
        problems.append("it uses a forbidden construct: %s" % command)
    tokens = command.split()
    if tokens[0] != "python3":
        problems.append("it doesn't start with python3: %s" % command)
    elif len(tokens) < 2 or tokens[1] not in shipped:
        problems.append("it doesn't run a shipped script: %s" % command)
    return problems


def test_the_orchestrator_has_a_shell_fence_to_check():
    labels = [f.label for f in fences(spec_text("orchestrator"))]
    assert any(label in SHELL_LABELS for label in labels), labels


def test_every_shell_fence_in_the_orchestrator_is_one_python3_call_of_a_shipped_script():
    shipped = shipped_scripts()
    assert "scripts/populate-affected-assets.py" in shipped
    for fence in fences(spec_text("orchestrator")):
        if fence.label.lower() in SHELL_LABELS:
            assert not command_problems(fence.body, shipped), fence.body


@pytest.mark.parametrize("body", [
    "python3 scripts/populate-affected-assets.py \\\n  --architecture <output_dir>/architecture.md \\\n  --threats <output_dir>/threats.md",
    "python3 scripts/tachi-stage.py --version",
])
def test_the_command_scanner_passes_a_shipped_python3_call(body):
    assert command_problems(body, {"scripts/populate-affected-assets.py", "scripts/tachi-stage.py"}) == []


@pytest.mark.parametrize("body", [
    "python3 scripts/gen.py",
    "bash scripts/populate-affected-assets.py",
    "python3 -c 'print(1)'",
    "python3 scripts/populate-affected-assets.py $(cat threats.md)",
    "python3 scripts/populate-affected-assets.py `ls`",
    "ls | xargs python3 scripts/populate-affected-assets.py",
    "bash -c 'python3 scripts/populate-affected-assets.py'",
    "python3 scripts/populate-affected-assets.py && echo done",
    "python3 scripts/populate-affected-assets.py\npython3 scripts/populate-affected-assets.py",
])
def test_the_command_scanner_flags_what_c6_forbids(body):
    assert command_problems(body, {"scripts/populate-affected-assets.py"}), body


# =============================================================================
# 7. PR 1's Track O text is inert (ADR-050 D11, spec S-5). PR 2's T094 flips this group.
# =============================================================================


def end_marker_tokens() -> Set[str]:
    """The end marker's provisional text, read from the staged reference: ``TACHI-END`` and ``TACHI-OVERFLOW``."""
    section = section_text(text_of(DISPATCH_RECORD_BRIEF), "## End Marker (provisional)", DISPATCH_RECORD_BRIEF)
    tokens = set(re.findall(r"TACHI-[A-Z]+", section))
    if tokens != {"TACHI-END", "TACHI-OVERFLOW"}:
        raise ReferenceDrift("the staged end marker's text moved: %s" % sorted(tokens))
    return tokens


def loaders_of_the_staged_reference() -> List[str]:
    """Every tachi agent, tachi command and skill file, other than the staged reference itself, that names it."""
    own = REPO_ROOT / DISPATCH_RECORD_BRIEF
    candidates = sorted((REPO_ROOT / AGENTS_DIR).rglob("*.md"))
    candidates += sorted((REPO_ROOT / COMMANDS_DIR).glob("tachi.*.md"))
    candidates += sorted((REPO_ROOT / SKILLS_DIR).rglob("*.md"))
    return [path.relative_to(REPO_ROOT).as_posix() for path in candidates
            if path != own and "dispatch-record-brief" in path.read_text(encoding="utf-8")]


def test_no_pr_1_agent_command_or_skill_loads_the_record_and_brief_reference():
    assert loaders_of_the_staged_reference() == []


def test_the_staged_reference_says_nothing_loads_it_yet():
    text = text_of(DISPATCH_RECORD_BRIEF)
    assert frontmatter_scalar(text, "status") == "staged"
    assert frontmatter_scalar(text, "consumers") == "[]"
    assert "Staged: nothing loads this file yet." in text
    assert "dispatch-record-brief" not in text_of(SHARED_SKILL)


def test_finding_format_has_neither_the_end_marker_nor_the_brief_rename():
    text = text_of(FINDING_FORMAT)
    for token in sorted(end_marker_tokens()):
        assert token not in text, "finding-format-shared.md already carries %s" % token
    assert not re.search(r"\bbrief\b", text, re.IGNORECASE), "finding-format-shared.md already says 'brief'"
    assert text.count("dispatch record") >= 3, "the three 'dispatch record' places D11 renames in PR 2 are gone"


def test_no_agent_spec_or_command_carries_the_end_marker_or_the_record_and_brief_files():
    markers = sorted(end_marker_tokens())
    staged_paths = ["/briefs/", "/records/", "phase1/", "idmap.json"]
    files = [(AGENTS_DIR + "/%s.md" % stem) for stem in AGENT_STEMS]
    files += [p.relative_to(REPO_ROOT).as_posix() for p in sorted((REPO_ROOT / COMMANDS_DIR).glob("tachi.*.md"))]
    for path in files:
        text = text_of(path)
        for token in markers + staged_paths:
            assert token not in text, "%s already mentions %s, which is PR 2's" % (path, token)


def test_the_orchestrator_has_no_dispatch_record_mechanics_yet():
    text = spec_text("orchestrator")
    assert "dispatch record" not in text.lower()
    assert ".tachi-build" not in text


# =============================================================================
# 8. sarif-identity-shared.md against sarif_common (T005; ADR-050 D7, D8)
# =============================================================================


def parse_tools_categories(text: str) -> Dict[str, Tuple[str, str]]:
    table = table_after(text, "## Files, Tools and Categories", where="sarif-identity-shared.md")
    return {strip_ticks(r[0]): (strip_ticks(r[1]), strip_ticks(r[2])) for r in table.rows}


def parse_file_statuses(text: str) -> Dict[str, str]:
    table = table_after(text, "## Files, Tools and Categories", where="sarif-identity-shared.md")
    return {strip_ticks(r[0]): r[3] for r in table.rows}


def parse_rule_ids(text: str) -> Dict[str, Tuple[str, str]]:
    table = table_after(text, "## Rule IDs", where="sarif-identity-shared.md")
    return {r[0]: (r[1], strip_ticks(r[2])) for r in table.rows}


def parse_emitter_constants(text: str) -> Dict[str, Any]:
    """The 14 Emitter Constants rows, each value normalized to the type the code holds."""
    table = table_after(text, "## Emitter Constants", where="sarif-identity-shared.md")
    out: Dict[str, Any] = {}
    for row in table.rows:
        name, value = plain(row[0]), row[1]
        found = ticks(value)
        if name == "Hash digest":
            digits = re.search(r"first (\d+) lowercase hex digits", value)
            out[name] = (int(digits.group(1)) if digits else None, found[0] if found else None)
        elif name == "region":
            out[name] = json.loads(found[0])
        elif name == "Longest candidate path":
            out[name] = int(re.search(r"([\d,]+) bytes", value).group(1).replace(",", ""))
        elif name == "Peer cap":
            out[name] = int(value)
        elif name in ("Hash recipe tag", "informationUri", "Default architecture path", "Peer sentence",
                      "Controls evidence message"):
            out[name] = found[0]
        else:
            out[name] = found
    return out


def code_emitter_constants() -> Dict[str, Any]:
    return {
        "Hash recipe tag": sc.HASH_RECIPE_TAG,
        "Hash digest": (sc.HASH_HEX_DIGITS, sc.HASH_SUFFIX),
        "region": sc.REGION,
        "partialFingerprints keys": list(sc.FINGERPRINT_KEYS),
        "informationUri": sc.INFORMATION_URI,
        "Default architecture path": sc.DEFAULT_ARCHITECTURE_PATH,
        "Longest candidate path": sc.MAX_PATH_BYTES,
        "Correlation property keys": list(sc.CORRELATION_KEYS),
        "Correlation roles": list(sc.CORRELATION_ROLES),
        "Peer cap": sc.PEER_CAP,
        "Peer sentence": sc.PEER_SENTENCE,
        "Primary sentence": [sc.PRIMARY_SENTENCE, sc.PRIMARY_SENTENCE_OVER_CAP],
        "Controls evidence message": sc.EVIDENCE_MESSAGE,
        "Flag properties": [sc.FLAG_PROPERTIES["risk-scores.sarif"], sc.FLAG_PROPERTIES["compensating-controls.sarif"]],
    }


def code_rule_ids() -> Dict[str, Tuple[str, str]]:
    rule_map = getattr(sc, RULE_MAP_NAME)
    return {prefix: (tachi_scoring.PREFIX_CATEGORY[prefix], rule_id) for prefix, rule_id in rule_map.items()}


# --- the tachi-plh/1 vectors and ruling C's sentences ----------------------------------------


def parse_recipe(text: str) -> Tuple[str, int, str]:
    """The tag, the digit count and the suffix of the hash recipe, read from its code block."""
    match = re.search(r'sha256\("([^"|]+)\|" \+ tool \+ "\|" \+ id\)\s+->\s+first (\d+) lowercase hex digits\s+->\s+then "([^"]+)"',
                      "\n".join(f.body for f in fences(text)))
    if not match:
        raise ReferenceDrift("sarif-identity-shared.md: the hash recipe block moved")
    return match.group(1), int(match.group(2)), match.group(3)


def parse_vectors(text: str) -> List[Tuple[str, str, str]]:
    table = table_after(text, "Test vectors, which the emitter must reproduce", where="sarif-identity-shared.md")
    return [(strip_ticks(r[0]), strip_ticks(r[1]), strip_ticks(r[2])) for r in table.rows]


def recipe_hash(recipe: Tuple[str, int, str], tool: str, finding_id: str) -> str:
    tag, digits, suffix = recipe
    return hashlib.sha256(("%s|%s|%s" % (tag, tool, finding_id)).encode("utf-8")).hexdigest()[:digits] + suffix


def parse_sentences(text: str) -> List[str]:
    table = table_after(text, "**The message sentence.**", where="sarif-identity-shared.md")
    return [strip_ticks(r[1]) for r in table.rows]


def correlation_from_sentence(sentence: str) -> "sc.Correlation":
    """The correlation a sentence describes, so the code can be asked to write the same sentence."""
    peer = re.fullmatch(r"Correlated in (CG-[0-9]+); primary (\S+)\.", sentence)
    if peer:
        return sc.Correlation(peer.group(1), "peer", peer.group(2), ())
    over = re.fullmatch(r"Correlated in (CG-[0-9]+); peers (.+) and ([0-9]+) more\.", sentence)
    if over:
        named = tuple(over.group(2).split(", "))
        unnamed = tuple("S-%d" % (900 + i) for i in range(int(over.group(3))))
        return sc.Correlation(over.group(1), "primary", "S-1", named + unnamed)
    plain_primary = re.fullmatch(r"Correlated in (CG-[0-9]+); peers (.+)\.", sentence)
    if plain_primary:
        return sc.Correlation(plain_primary.group(1), "primary", "S-1", tuple(plain_primary.group(2).split(", ")))
    raise ReferenceDrift("not a correlation sentence: %r" % sentence)


def vector_problems(text: str) -> List[str]:
    recipe = parse_recipe(text)
    vectors = parse_vectors(text)
    problems = []
    if len(vectors) != 3:
        problems.append("expected three test vectors, found %d" % len(vectors))
    for tool, finding_id, expected in vectors:
        if recipe_hash(recipe, tool, finding_id) != expected:
            problems.append("the reference's own recipe gives %s for (%s, %s), not %s" % (recipe_hash(recipe, tool, finding_id), tool, finding_id, expected))
        if sc.primary_location_line_hash(tool, finding_id) != expected:
            problems.append("sarif_common gives %s for (%s, %s), not %s" % (sc.primary_location_line_hash(tool, finding_id), tool, finding_id, expected))
    return problems


def sentence_problems(text: str) -> List[str]:
    sentences = parse_sentences(text)
    problems = []
    if len(sentences) != 3:
        problems.append("expected three sentence rows, found %d" % len(sentences))
    for sentence in sentences:
        try:
            written = sc.correlation_sentence(correlation_from_sentence(sentence))
        except ReferenceDrift as exc:
            problems.append(str(exc))
            continue
        if written != sentence:
            problems.append("the reference says %r, sarif_common writes %r" % (sentence, written))
    return problems


# --- the families: parse the reference, compare with the code, and show both sides red ------------------


class Family(NamedTuple):
    name: str
    path: str
    parse: Callable[[str], Any]
    code: Callable[[], Any]
    doc_edit: Tuple[str, str]  # one replacement in the reference that must make the two differ
    code_edit: Callable[[Any], Any]  # one change to the code's value that must make the two differ


def parse_resolver_constants(text: str) -> Dict[str, Any]:
    """The resolver's and the result's names: output names, the flag, the stamp keys and the keys no result carries."""
    uri = section_text(text, "## artifactLocation.uri", "sarif-identity-shared.md")
    shape = section_text(text, "## The Result Shape", "sarif-identity-shared.md")
    names = re.search(r"canonical output names \(((?:`[^`]+`(?:, )?)+)\)", uri)
    flag = re.search(r"the `(--[a-z-]+)` flag on the scorer and controls commands", uri)
    stamp = re.search(r"renderer's stamp: ((?:`[a-z_]+`(?:, | and )?)+)\.", shape)
    forbidden = re.search(r"\*\*No result carries\*\* ([^\n]+)", shape)
    if not (names and flag and stamp and forbidden):
        raise ReferenceDrift("sarif-identity-shared.md: the resolver's or the result's names moved")
    return {"canonical output names": frozenset(ticks(names.group(1))), "architecture flag": flag.group(1),
            "stamp keys": ticks(stamp.group(1)), "keys no result carries": ticks(forbidden.group(1))}


def code_resolver_constants() -> Dict[str, Any]:
    return {"canonical output names": frozenset(sc.CANONICAL_OUTPUT_NAMES), "architecture flag": sc.ARCHITECTURE_FLAG,
            "stamp keys": list(sc.STAMP_KEYS), "keys no result carries": list(sc.FORBIDDEN_RESULT_KEYS)}


def shape_of(value: Any) -> Any:
    """The keys of a JSON value in order, down to the type of each scalar. An array stands for its first element."""
    if isinstance(value, dict):
        return ("object", tuple((key, shape_of(child)) for key, child in value.items()))
    if isinstance(value, list):
        return ("array", shape_of(value[0]) if value else None)
    return type(value).__name__


def parse_result_shape(text: str) -> Any:
    blocks = [f for f in fences(section_text(text, "## The Result Shape", "sarif-identity-shared.md", keep_fences=True))
              if f.label == "json"]
    if len(blocks) != 1:
        raise ReferenceDrift("sarif-identity-shared.md: expected one json block in The Result Shape, found %d" % len(blocks))
    return shape_of(json.loads(blocks[0].body))


def code_result_shape() -> Any:
    evidence = sc.evidence_location(0, "authentication", sc.ResolvedPath("src/app.py", "src/app.py"), 42)
    result = sc.build_result(
        tool=sc.TOOL_NAMES["risk-scores.sarif"], finding_id="T-2", message="A message.", level="warning",
        uri=sc.DEFAULT_ARCHITECTURE_PATH, component="API", zone="DMZ", kind="Process",
        correlation=sc.Correlation("CG-1", "peer", "S-1", ()), related_locations=[evidence])
    return shape_of(result)


SARIF_FAMILIES = (
    Family("tools and upload categories", SARIF_IDENTITY, parse_tools_categories,
           lambda: {f: (sc.TOOL_NAMES[f], sc.UPLOAD_CATEGORIES[f]) for f in sc.TOOL_NAMES},
           ("| `risk-scores.sarif` | `tachi-risk-scorer` |", "| `risk-scores.sarif` | `tachi-risk-scorers` |"),
           lambda v: dict(v, **{"threats.sarif": ("tachi", "threat-model")})),
    Family("rule IDs by prefix (%s)" % RULE_MAP_NAME, SARIF_IDENTITY, parse_rule_ids, code_rule_ids,
           ("`tachi/stride/spoofing`", "`tachi/stride/spoofings`"),
           lambda v: dict(v, TE=("agentic", "tachi/ai/agentic"))),
    Family("emitter constants", SARIF_IDENTITY, parse_emitter_constants, code_emitter_constants,
           ("| Peer cap | 10 |", "| Peer cap | 12 |"),
           lambda v: dict(v, **{"Hash recipe tag": "tachi-plh/2"})),
    Family("resolver and run constants", SARIF_IDENTITY, parse_resolver_constants, code_resolver_constants,
           ("`attack-chains.md`, ", ""),
           lambda v: dict(v, **{"architecture flag": "--architecture"})),
    Family("result shape and key order", SARIF_IDENTITY, parse_result_shape, code_result_shape,
           ('"fullyQualifiedName": "<zone>/<component>"', '"fullyQualifiedNames": "<zone>/<component>"'),
           lambda v: ("object", tuple(reversed(v[1])))),
)


@pytest.mark.parametrize("family", SARIF_FAMILIES, ids=lambda f: f.name)
def test_sarif_identity_equals_sarif_common(family):
    problems = diff(family.name, family.parse(text_of(family.path)), family.code())
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("family", SARIF_FAMILIES, ids=lambda f: f.name)
def test_a_drifted_sarif_reference_is_noticed(family):
    text = text_of(family.path)
    old, new = family.doc_edit
    assert old in text, "the edit's anchor %r moved" % old
    assert diff(family.name, family.parse(text.replace(old, new, 1)), family.code())


@pytest.mark.parametrize("family", SARIF_FAMILIES, ids=lambda f: f.name)
def test_drifted_sarif_code_is_noticed(family):
    assert diff(family.name, family.parse(text_of(family.path)), family.code_edit(family.code()))


def test_the_sarif_parsers_find_the_counts_the_reference_states():
    text = text_of(SARIF_IDENTITY)
    assert len(parse_tools_categories(text)) == 3 and len(parse_file_statuses(text)) == 3
    assert len(parse_rule_ids(text)) == 12 and len(parse_emitter_constants(text)) == 14
    assert len(parse_vectors(text)) == 3 and len(parse_sentences(text)) == 3
    assert len(parse_resolver_constants(text)["canonical output names"]) == 8
    assert parse_resolver_constants(text)["stamp keys"] == ["renderer", "version", "input_digest"]
    assert len(parse_resolver_constants(text)["keys no result carries"]) == 4
    assert [key for key, _child in parse_result_shape(text)[1]][:3] == ["ruleId", "message", "level"]


def test_the_rule_ids_are_eight_for_twelve_prefixes_and_never_the_short_forms():
    doc = parse_rule_ids(text_of(SARIF_IDENTITY))
    assert len(doc) == 12 and len({rule for _category, rule in doc.values()}) == 8
    assert not {rule for _category, rule in doc.values()} & {"tachi/ai/agentic", "tachi/ai/llm"}
    assert not set(getattr(sc, RULE_MAP_NAME).values()) & {"tachi/ai/agentic", "tachi/ai/llm"}


def test_the_legacy_rule_map_agrees_with_the_reference_on_the_stride_prefixes():
    legacy = getattr(sc, "PREFIX_TO_RULE", None)
    if legacy is None:
        pytest.skip("the legacy rule map is retired with the old generators")
    doc = parse_rule_ids(text_of(SARIF_IDENTITY))
    for prefix in ("S", "T", "R", "I", "D", "E"):
        assert legacy[prefix] == doc[prefix][1], prefix


def test_the_dormant_file_is_threats_sarif_alone():
    assert parse_file_statuses(text_of(SARIF_IDENTITY)) == {
        "threats.sarif": "dormant", "risk-scores.sarif": "live", "compensating-controls.sarif": "live"}  # PR 2 (T101) flips the first


def test_the_three_hash_vectors_hold_under_the_recipe_and_the_emitter():
    assert vector_problems(text_of(SARIF_IDENTITY)) == []
    tool = sc.TOOL_NAMES["risk-scores.sarif"]
    assert sc.primary_location_line_hash(tool, "AGP-01") == sc.primary_location_line_hash(tool, "AGP-1")


def test_a_drifted_vector_or_emitter_is_noticed(monkeypatch):
    text = text_of(SARIF_IDENTITY)
    assert vector_problems(text.replace("4395a0c67e904b90:1", "4395a0c67e904b91:1", 1))
    monkeypatch.setattr(sc, "HASH_SUFFIX", ":2")
    assert vector_problems(text)


def test_ruling_c_s_three_sentences_are_what_the_emitter_writes():
    assert sentence_problems(text_of(SARIF_IDENTITY)) == []


def test_a_drifted_sentence_or_emitter_is_noticed(monkeypatch):
    text = text_of(SARIF_IDENTITY)
    assert sentence_problems(text.replace("Correlated in CG-3; peers T-2, I-4.", "Correlated in CG-3; with peers T-2, I-4.", 1))
    assert sentence_problems(text.replace(", I-12 and 3 more.", " and 3 more.", 1)), "nine named peers is not the cap"
    monkeypatch.setattr(sc, "PEER_CAP", 9)
    assert sentence_problems(text)


# =============================================================================
# 9. part-file-contract-shared.md against tachi_parts, as constants (T006; ADR-050 D3)
# =============================================================================

# KEY_SETS name -> the line that starts the reference's table for it.
KEY_SET_TABLES = {
    "batch-input": "## The Batch Input",
    "part": "## The Part Envelope",
    "scorer-item": "### Scorer item (stage `risk-score`)",
    "exploitability": "**Exploitability keys.**",
    "scalability": "**Scalability keys.**",
    "reachability": "**Reachability keys.**",
    "rationale": "**Rationale keys.**",
    "controls-item": "### Controls item (stage `compensating-controls`)",
    "evidence-entry": "**Evidence entry keys.**",
    "assessment": "**Assessment keys.**",
    "assessment-dimension": "**Assessment dimension keys.**",
    "overflow": "## Overflow",
    "plan": "### Plan keys",
    "plan-pointer": "### Plan pointer keys",
    "stage-record": "### Stage record keys",
}

# KEY_SETS name -> (the key table, the row whose type cell holds it). The nine sub-objects that the
# reference writes inline as ``{a, b, c}``.
INLINE_KEY_SETS = {
    "plan-input": ("plan", "inputs"),
    "plan-batch": ("plan", "batches"),
    "retry-budget": ("plan", "retry_budget"),
    "stage-batches": ("stage-record", "batches"),
    "overflow-event": ("stage-record", "overflow_events"),
    "retry-entry": ("stage-record", "retries"),
    "warning": ("stage-record", "warnings"),
    "output": ("stage-record", "outputs"),
    "error": ("stage-record", "error"),
}


def key_table(text: str, name: str) -> Table:
    return table_after(text, KEY_SET_TABLES[name], where="part-file-contract-shared.md")


def key_row(table: Table, key: str) -> List[str]:
    rows = [row for row in table.rows if strip_ticks(row[0]) == key]
    if len(rows) != 1:
        raise ReferenceDrift("part-file-contract-shared.md: expected one row for %r, found %d" % (key, len(rows)))
    return rows[0]


def parse_key_sets(text: str) -> Dict[str, Tuple[FrozenSet[str], FrozenSet[str]]]:
    out: Dict[str, Tuple[FrozenSet[str], FrozenSet[str]]] = {}
    for name in KEY_SET_TABLES:
        required: List[str] = []
        optional: List[str] = []
        for row in key_table(text, name).rows:
            (optional if row[1].lower().startswith("optional") else required).append(strip_ticks(row[0]))
        if len(set(required + optional)) != len(required + optional):
            raise ReferenceDrift("part-file-contract-shared.md: a key repeats in the %s table" % name)
        out[name] = (frozenset(required), frozenset(optional))
    for name, (table_name, row_key) in INLINE_KEY_SETS.items():
        cell = key_row(key_table(text, table_name), row_key)[1]
        braces = re.findall(r"`\{([^}]*)\}`", cell)
        if len(braces) != 1:
            raise ReferenceDrift("part-file-contract-shared.md: the %s row has %d brace lists" % (row_key, len(braces)))
        keys = [k.strip() for k in braces[0].split(",")]
        out[name] = (frozenset(keys), frozenset())
    return out


def code_key_sets() -> Dict[str, Tuple[FrozenSet[str], FrozenSet[str]]]:
    return {name: (frozenset(req), frozenset(opt)) for name, (req, opt) in tachi_parts.KEY_SETS.items()}


def parse_closed_values(text: str) -> Dict[str, FrozenSet[str]]:
    scorer = key_table(text, "scorer-item")
    controls = key_table(text, "controls-item")
    stage_record = key_table(text, "stage-record")
    plan = key_table(text, "plan")
    values = {
        "SUBSCORE_NAMES": [strip_ticks(r[0]) for name in ("exploitability", "scalability") for r in key_table(text, name).rows],
        "METRIC_NAMES": enum_after(key_row(scorer, "metric_rationale")[1], "keys come from "),
        "ASSESSMENT_DIMENSIONS": [strip_ticks(r[0]) for r in key_table(text, "assessment").rows],
        "CONTROL_CATEGORIES": enum_after(key_row(controls, "control_category")[1], "one of "),
        "CONTROL_STATUSES": enum_after(key_row(controls, "control_status")[1]),
        "CONFIDENCES": enum_after(key_row(controls, "confidence")[1]),
        "TRUST_LEVELS": enum_after(key_row(key_table(text, "reachability"), "trust_level")[1]),
        "OVERFLOW_REASONS": enum_after(key_row(key_table(text, "overflow"), "reason")[1]),
        "BATCH_STATES": enum_after(key_row(plan, "batches")[1], "`state` is "),
        "RECORD_STATUSES": enum_after(key_row(stage_record, "status")[1]),
        "OVERFLOW_EVENT_KINDS": enum_after(key_row(stage_record, "overflow_events")[1], "`kind` is "),
        "COUNT_KEYS": enum_after(key_row(stage_record, "counts")[1], "exactly these keys: "),
    }
    for name, found in values.items():
        if len(set(found)) != len(found):
            raise ReferenceDrift("part-file-contract-shared.md: a value repeats in %s: %s" % (name, found))
    return {name: frozenset(found) for name, found in values.items()}


def code_closed_values() -> Dict[str, FrozenSet[str]]:
    names = ("SUBSCORE_NAMES", "METRIC_NAMES", "ASSESSMENT_DIMENSIONS", "CONTROL_CATEGORIES", "CONTROL_STATUSES",
             "CONFIDENCES", "TRUST_LEVELS", "OVERFLOW_REASONS", "BATCH_STATES", "RECORD_STATUSES", "OVERFLOW_EVENT_KINDS",
             "COUNT_KEYS")
    return {name: frozenset(getattr(tachi_parts, name)) for name in names}


def parse_stage_agents(text: str) -> Dict[str, str]:
    table = table_after(text, "## The Part Envelope", nth=1, where="part-file-contract-shared.md")
    return {strip_ticks(r[0]): strip_ticks(r[1]) for r in table.rows}


def parse_slots(text: str) -> Dict[str, Dict[str, Optional[FrozenSet[str]]]]:
    sub_scores = frozenset(strip_ticks(r[0]) for name in ("exploitability", "scalability") for r in key_table(text, name).rows)
    table = table_after(text, "### Slots in use", where="part-file-contract-shared.md")
    out: Dict[str, Dict[str, Optional[FrozenSet[str]]]] = {}
    for kind_cell, argument_cell, _resolves, stage_cell in table.rows:
        kind = strip_ticks(kind_cell)
        stages = ticks(stage_cell)
        if not stages:
            raise ReferenceDrift("part-file-contract-shared.md: the %s slot row names no stage" % kind)
        for stage in stages:
            if kind in ("finding", "ref"):
                out.setdefault(stage, {})[kind] = None
                continue
            arguments = set(ticks(argument_cell))
            if "one of the eight sub-score names" in argument_cell:
                arguments |= sub_scores
            current = out.setdefault(stage, {}).get(kind, frozenset())
            out[stage][kind] = frozenset(arguments) | (current or frozenset())
    return out


def parse_reserved_slots(text: str) -> List[Tuple[str, str]]:
    """The ``(kind, argument)`` samples of the slots the reference reserves for later stages."""
    table = table_after(text, "### Slots reserved for later stages", where="part-file-contract-shared.md")
    samples: List[Tuple[str, str]] = []
    for kind_cell, argument_cell, _resolves, _stage in table.rows:
        kind = strip_ticks(kind_cell)
        for argument in ticks(argument_cell):
            samples.append((kind, argument.replace("<finding ID>", "S-1")))
        if "a band name" in argument_cell:
            samples.append((kind, "Critical"))
    return samples


def parse_fallbacks(text: str) -> Dict[str, str]:
    table = table_after(text, "## Fixed Fallback Sentences", where="part-file-contract-shared.md")
    return {strip_ticks(r[0]): r[2] for r in table.rows}


def parse_flag_fields(text: str) -> Dict[str, str]:
    table = table_after(text, "### Truncation", where="part-file-contract-shared.md")
    return {strip_ticks(r[0]): r[3] for r in table.rows}


def code_flag_fields() -> Dict[str, str]:
    return {field: ("narrative" if field in tachi_parts.NARRATIVE_FIELDS else "evidence") for field in tachi_parts.FLAG_FIELDS}


def parse_identifiers(text: str) -> Dict[str, Any]:
    labels = {"Plan ID": "plan", "Batch ID": "batch", "Finding ID": "finding", "Dispatch ID": "dispatch",
              "Correlation group ID": "group", "Chain ID": "chain", "Evidence language": "language"}
    section = section_text(text, "## Identifiers", "part-file-contract-shared.md")
    patterns: Dict[str, str] = {}
    for label, pattern in re.findall(r"^- \*\*([^*:]+):\*\* `([^`]+)`$", section, re.M):
        if label in labels:
            patterns[labels[label]] = pattern
    order = re.search(r"in this order: ((?:`[A-Z]+`(?:, )?)+)\.", section)
    if not order:
        raise ReferenceDrift("part-file-contract-shared.md: S-2's prefix order moved")
    return {"patterns": patterns, "prefix_order": ticks(order.group(1))}


def code_identifiers() -> Dict[str, Any]:
    return {"patterns": dict(tachi_parts.ID_PATTERNS), "prefix_order": list(tachi_parts.FINDING_PREFIXES)}


_KIB, _MIB = 1024, 1024 * 1024
LIMIT_PHRASES = (  # (name, a regex with one number group, the multiplier, the code's value)
    ("part cap", r"A part is at most (\d+) KiB", _KIB, lambda: tachi_parts.MAX_PART_BYTES),
    ("agent input cap", r"input written by an agent is at most (\d+) MiB", _MIB, lambda: tachi_parts.MAX_AGENT_INPUT_BYTES),
    ("string cap", r"\*\*Every string\*\* is at most ([\d,]+) characters", 1, lambda: tachi_parts.MAX_STRING_CHARS),
    ("nesting", r"Nesting is at most (\d+) levels", 1, lambda: tachi_parts.MAX_NESTING),
    ("integer digits", r"integer literal of more than (\d+) digits", 1, lambda: tachi_parts.MAX_INT_DIGITS),
    ("finding IDs", r"1 to (\d+) unique finding IDs", 1, lambda: tachi_parts.MAX_IDS),
    ("plan cap", r"A plan is at most (\d+) MiB", _MIB, lambda: tachi_parts.MAX_DOCUMENT_BYTES[tachi_parts.PLAN_SCHEMA]),
    ("batch input cap", r"a batch input (\d+) MiB", _MIB, lambda: tachi_parts.MAX_DOCUMENT_BYTES[tachi_parts.BATCH_INPUT_SCHEMA]),
    ("pointer cap", r"the plan pointer (\d+) KiB", _KIB, lambda: tachi_parts.MAX_DOCUMENT_BYTES[tachi_parts.POINTER_SCHEMA]),
    ("stage record cap", r"a stage record (\d+) MiB", _MIB, lambda: tachi_parts.MAX_DOCUMENT_BYTES[tachi_parts.STAGE_RECORD_SCHEMA]),
)


def parse_limits(text: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for name, pattern, multiplier, _code in LIMIT_PHRASES:
        match = re.search(pattern, text)
        if not match:
            raise ReferenceDrift("part-file-contract-shared.md: the phrase for the %s moved (%s)" % (name, pattern))
        out[name] = int(match.group(1).replace(",", "")) * multiplier
    return out


def code_limits() -> Dict[str, int]:
    return {name: code() for name, _pattern, _multiplier, code in LIMIT_PHRASES}


def parse_escape_references(text: str) -> FrozenSet[str]:
    return frozenset(re.findall(r"&#?[A-Za-z0-9]+;", section_text(text, "## Output Escaping", "part-file-contract-shared.md")))


PART_FAMILIES = (
    Family("key sets (24)", PART_CONTRACT, parse_key_sets, code_key_sets,
           ("| `cvss_vector` |", "| `cvss_vectors` |"),
           lambda v: dict(v, part=(v["part"][0] | frozenset(["extra"]), v["part"][1]))),
    Family("closed values", PART_CONTRACT, parse_closed_values, code_closed_values,
           ("`found`, `partial` or `missing`", "`found`, `partially` or `missing`"),
           lambda v: dict(v, CONTROL_CATEGORIES=v["CONTROL_CATEGORIES"] | frozenset(["extra"]))),
    Family("stage agents", PART_CONTRACT, parse_stage_agents, lambda: dict(tachi_parts.STAGE_AGENTS),
           ("| `risk-score` | `tachi-risk-scorer` |", "| `risk-score` | `tachi-risk-scorers` |"),
           lambda v: dict(v, **{"risk-score": "tachi-other"})),
    Family("slots in use", PART_CONTRACT, parse_slots, lambda: tachi_parts.SLOT_TABLE,
           ("`auth_barriers`, `network_boundaries` | your own count", "`auth_barriers` | your own count"),
           lambda v: dict(v, **{"risk-score": dict(v["risk-score"], band=frozenset(["severity", "extra"]))})),
    Family("fixed fallback sentences (24)", PART_CONTRACT, parse_fallbacks, lambda: dict(tachi_parts.FALLBACK_SENTENCES),
           ("No CVSS rationale is shown", "No CVSS reasoning is shown"),
           lambda v: dict(v, **{"rationale.cvss": v["rationale.cvss"] + " "})),
    Family("flag fields (28)", PART_CONTRACT, parse_flag_fields, code_flag_fields,
           ("| `recommendation_body` | `items[].recommendation_body` | 2000 | evidence |",
            "| `recommendation_bodies` | `items[].recommendation_body` | 2000 | evidence |"),
           lambda v: dict(v, **{"extra.field": "narrative"})),
    Family("identifiers and S-2's order", PART_CONTRACT, parse_identifiers, code_identifiers,
           ("`B[0-9]{3}(-[12]){0,2}`", "`B[0-9]{4}(-[12]){0,2}`"),
           lambda v: dict(v, prefix_order=v["prefix_order"][::-1])),
    Family("limits", PART_CONTRACT, parse_limits, code_limits,
           ("A part is at most 512 KiB", "A part is at most 513 KiB"),
           lambda v: dict(v, nesting=9)),
    Family("escape references", PART_CONTRACT, parse_escape_references, lambda: frozenset(tachi_parts.ESCAPE_REFERENCES),
           ("`&#96;`", "`&#97;`"),
           lambda v: v | frozenset(["&extra;"])),
)


@pytest.mark.parametrize("family", PART_FAMILIES, ids=lambda f: f.name)
def test_part_file_contract_equals_tachi_parts(family):
    problems = diff(family.name, family.parse(text_of(family.path)), family.code())
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("family", PART_FAMILIES, ids=lambda f: f.name)
def test_a_drifted_part_reference_is_noticed(family):
    text = text_of(family.path)
    old, new = family.doc_edit
    assert old in text, "the edit's anchor %r moved" % old
    assert diff(family.name, family.parse(text.replace(old, new, 1)), family.code())


@pytest.mark.parametrize("family", PART_FAMILIES, ids=lambda f: f.name)
def test_drifted_part_code_is_noticed(family):
    assert diff(family.name, family.parse(text_of(family.path)), family.code_edit(family.code()))


def test_the_key_set_tables_are_15_and_the_inline_sets_are_9_and_together_all_of_key_sets():
    assert len(KEY_SET_TABLES) == 15 and len(INLINE_KEY_SETS) == 9
    assert set(KEY_SET_TABLES) | set(INLINE_KEY_SETS) == set(tachi_parts.KEY_SETS)


def test_the_part_parsers_find_the_counts_the_reference_states():
    text = text_of(PART_CONTRACT)
    assert len(parse_key_sets(text)) == 24
    assert len(parse_fallbacks(text)) == 24 and len(parse_flag_fields(text)) == 28
    assert sorted(parse_slots(text)) == ["compensating-controls", "risk-score"]
    assert len(parse_stage_agents(text)) == 2 and len(parse_limits(text)) == 10 and len(parse_escape_references(text)) == 9
    identifiers = parse_identifiers(text)
    assert len(identifiers["patterns"]) == 7 and len(identifiers["prefix_order"]) == 12
    closed = parse_closed_values(text)
    assert len(closed) == 12 and all(closed.values()) and len(closed["COUNT_KEYS"]) == 16


def test_the_fixed_sentences_and_the_truncation_table_agree_on_the_24_narrative_paths():
    text = text_of(PART_CONTRACT)
    fallback_rows = table_after(text, "## Fixed Fallback Sentences", where="part-file-contract-shared.md").rows
    truncation_rows = table_after(text, "### Truncation", where="part-file-contract-shared.md").rows
    fallback_paths = {strip_ticks(r[0]): strip_ticks(r[1]) for r in fallback_rows}
    truncation_paths = {strip_ticks(r[0]): strip_ticks(r[1]) for r in truncation_rows}
    assert len(fallback_paths) == 24 and len(truncation_paths) == 28
    assert {f: truncation_paths[f] for f in fallback_paths} == fallback_paths


def test_every_fixed_sentence_has_no_digit_and_no_slot():
    for field, sentence in tachi_parts.FALLBACK_SENTENCES.items():
        assert not any(ch.isnumeric() for ch in sentence) and "{{" not in sentence, field


def test_the_reserved_slots_are_not_accepted_and_the_slots_in_use_are_accepted_in_their_stages_alone():
    text = text_of(PART_CONTRACT)
    in_use = parse_slots(text)
    samples = {"finding": "S-1", "ref": "CWE-89"}
    every_pair = {(kind, argument) for kinds in in_use.values() for kind, args in kinds.items()
                  for argument in ([samples[kind]] if args is None else sorted(args))}
    for stage in tachi_parts.SLOT_TABLE:
        for kind, argument in sorted(every_pair):
            slot = "{{%s:%s}}" % (kind, argument)
            listed = kind in in_use[stage] and (in_use[stage][kind] is None or argument in in_use[stage][kind])
            accepted = tachi_parts.narrative_problem(slot, stage) is None
            assert accepted == listed, "%s in stage %s: accepted=%s, listed=%s" % (slot, stage, accepted, listed)
    for kind, argument in parse_reserved_slots(text):
        for stage in tachi_parts.SLOT_TABLE:
            assert tachi_parts.narrative_problem("{{%s:%s}}" % (kind, argument), stage) is not None, (kind, argument, stage)


# =============================================================================
# 10. part-file-contract-shared.md against the validator's behavior (T006; ADR-050 D3 steps 9 to 11)
# =============================================================================

PLAN_ID = "20261122T120000Z-0123456789ab"
BATCH_ID = "B001"
CONTROLS_ROOTS = ("evidence", "matrix_row", "recommendation_body")
# ADR-050 D2: a row has 11 cells and opens with the item's own ID, and a body holds the four keys of the section 4 block once
# each and in order, with an Effort Estimate that starts at a level. So neither can be any text. Each head ends where the
# last cell or the last key's text begins, which is the place to pad.
MATRIX_ROW_HEAD = ("| S-1 | \u2014 | Gateway | L1 | A threat | {{score:inherent}} | {{band:inherent}} | Partial Control | "
                   "authentication | {{score:residual}} | ")
BODY_HEAD = ("**What to Implement**: A plain sentence.\n**Where to Implement**: A plain sentence.\n"
             "**Reference Patterns**: A plain sentence.\n**Effort Estimate**: Low \u2014 ")


def base_item(stage: str) -> Dict[str, Any]:
    """A valid item for ``stage``, built from the code's own key sets, so a key-set drift can't hide a cut check."""
    keys = tachi_parts.KEY_SETS
    if stage == "risk-score":
        return {
            "finding_id": "S-1",
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "exploitability": {k: 5 for k in keys["exploitability"][0]},
            "scalability": {k: 5 for k in keys["scalability"][0]},
            "reachability": {"zone": None, "trust_level": None, "auth_barriers": 1, "network_boundaries": 1},
            "rationale": {k: "A plain sentence." for k in keys["rationale"][0]},
            "metric_rationale": {k: "A plain sentence." for k in tachi_parts.METRIC_NAMES},
            "subscore_rationale": {k: "A plain sentence." for k in tachi_parts.SUBSCORE_NAMES},
        }
    return {
        "finding_id": "S-1",
        "control_status": "partial",
        "control_category": "authentication",
        "confidence": "Medium",
        "carried_forward": False,
        "evidence": [{
            "file": "src/app.py", "line": 1, "language": "python", "snippet": "x = 1", "summary": "A plain sentence.",
            "assessment": {d: {"rating": "High", "rationale": "A plain sentence."} for d in tachi_parts.ASSESSMENT_DIMENSIONS},
        }],
        "matrix_row": MATRIX_ROW_HEAD + "{{band:residual}} |",
        "recommendation_body": BODY_HEAD + "A plain sentence.",
    }


def classify(stage: str, item: Dict[str, Any]) -> Any:
    agent = tachi_parts.STAGE_AGENTS[stage]
    part = {"schema": "tachi.part/1", "plan_id": PLAN_ID, "batch_id": BATCH_ID, "stage": stage, "agent_type": agent,
            "finding_ids": [item["finding_id"]], "items": [item], "fragments": []}
    return tachi_parts.classify_part(part, PLAN_ID, BATCH_ID, stage, agent, [item["finding_id"]])


def steps_of(part_path: str) -> List[Any]:
    """``items[].evidence[].assessment.coverage.rationale`` as the steps from an item to the string."""
    segments = part_path.split(".")
    assert segments[0] == "items[]", part_path
    steps: List[Any] = []
    for segment in segments[1:]:
        if segment.endswith("[]"):
            steps.extend([segment[:-2], 0])
        else:
            steps.append(segment)
    return steps


def get_at(item: Any, steps: Sequence[Any]) -> Any:
    for step in steps:
        item = item[step]
    return item


def set_at(item: Any, steps: Sequence[Any], value: Any) -> None:
    get_at(item, steps[:-1])[steps[-1]] = value


def over_the_limit(field: str, limit: int) -> str:
    """``limit + 25`` characters for ``field``. A ``matrix_row`` and a ``recommendation_body`` have to keep their form to be
    accepted, so their padding goes in the last cell and in the last key's text."""
    head = {"matrix_row": MATRIX_ROW_HEAD, "recommendation_body": BODY_HEAD}.get(field, "")
    return head + "x" * (limit + 25 - len(head))


def stage_of(field: str) -> str:
    return "compensating-controls" if field.split(".")[0] in CONTROLS_ROOTS else "risk-score"


def test_the_base_items_are_valid_for_both_stages():
    for stage in tachi_parts.STAGE_AGENTS:
        result = classify(stage, base_item(stage))
        assert result.state == "done" and result.flags == {}, (stage, result.state, result.detail)


@pytest.mark.parametrize("field", tachi_parts.FLAG_FIELDS)
def test_each_field_is_cut_where_the_truncation_table_says(field):
    rows = {strip_ticks(r[0]): (strip_ticks(r[1]), int(r[2]), r[3])
            for r in table_after(text_of(PART_CONTRACT), "### Truncation", where="part-file-contract-shared.md").rows}
    assert field in rows, "the Truncation table has no row for %s" % field
    part_path, limit, field_class = rows[field]
    assert field_class == ("narrative" if field in tachi_parts.NARRATIVE_FIELDS else "evidence")
    stage = stage_of(field)
    item = base_item(stage)
    steps = steps_of(part_path)
    set_at(item, steps, over_the_limit(field, limit))
    result = classify(stage, item)
    assert result.state == "done", result.detail
    assert "input:%s:truncated" % field in result.flags["S-1"]
    assert len(get_at(result.part["items"][0], steps)) == limit


@pytest.mark.parametrize("field", tachi_parts.NARRATIVE_FIELDS)
def test_a_narrative_slip_takes_the_fixed_sentence_the_table_gives(field):
    rows = {strip_ticks(r[0]): (strip_ticks(r[1]), r[2])
            for r in table_after(text_of(PART_CONTRACT), "## Fixed Fallback Sentences", where="part-file-contract-shared.md").rows}
    assert field in rows, "the Fixed Fallback Sentences table has no row for %s" % field
    part_path, sentence = rows[field]
    stage = stage_of(field)
    item = base_item(stage)
    steps = steps_of(part_path)
    set_at(item, steps, "The port is 8080 outside any slot.")
    result = classify(stage, item)
    assert result.state == "done", result.detail
    assert "input:%s:narrative-fallback" % field in result.flags["S-1"]
    assert get_at(result.part["items"][0], steps) == sentence


def test_a_snippet_is_cut_to_five_lines_first_and_flagged_once():
    item = base_item("compensating-controls")
    item["evidence"][0]["snippet"] = "\n".join("line %d" % n for n in range(8))
    result = classify("compensating-controls", item)
    assert result.part["items"][0]["evidence"][0]["snippet"] == "\n".join("line %d" % n for n in range(5))
    assert result.flags["S-1"].count("input:evidence.snippet:truncated") == 1
    assert "cut to 5 lines first, then to 600 characters" in text_of(PART_CONTRACT)


def test_a_cut_that_lands_inside_a_slot_takes_the_fixed_sentence_too():
    field = "input:subscore_rationale.skill_level"
    item = base_item("risk-score")
    item["subscore_rationale"]["skill_level"] = "x" * 150 + "{{score:skill_level}}"  # cut after "{{score:sk"
    flags = classify("risk-score", item).flags["S-1"]
    assert field + ":truncated" in flags and field + ":narrative-fallback" in flags
    # A cut inside the opener's own text, "{{sco", leaves no slot: the grammar reads it as plain text.
    item["subscore_rationale"]["skill_level"] = "x" * 155 + "{{score:skill_level}}"
    flags = classify("risk-score", item).flags["S-1"]
    assert field + ":truncated" in flags and field + ":narrative-fallback" not in flags


# =============================================================================
# 11. The extraction preflights name the extractors' import closure (the W1 wiring fix)
# =============================================================================

# The Bash agent that runs each extractor, and the extractor's file stem. Each spec's preflight is a
# ``test -f`` fence plus an ``EXTRACTION SCRIPT MISSING`` error that lists the same files.
PREFLIGHTS = {"report-assembler": "extract-report-data", "threat-infographic": "extract-infographic-data"}


def module_level_imports(source: str) -> Set[str]:
    """The top-level names a module imports when it loads or runs as a script.

    Imports inside ``if`` and ``try`` blocks count. An import inside a function or a class body is lazy:
    it loads only when that code runs, so it is not part of what the module needs at load.
    """
    found: Set[str] = set()

    def walk(nodes: Sequence[ast.AST]) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
            for field in ("body", "orelse", "finalbody", "handlers"):
                walk(getattr(node, field, []))

    walk(ast.parse(source).body)
    return found


def local_import_closure(entry_source: str, local_source: Callable[[str], Optional[str]]) -> List[str]:
    """The local modules that an entry loads at import, in the order found. ``local_source(name)`` is a local module's text, or ``None``."""
    seen: List[str] = []
    todo = sorted(name for name in module_level_imports(entry_source) if local_source(name) is not None)
    while todo:
        name = todo.pop(0)
        if name in seen:
            continue
        seen.append(name)
        todo += sorted(n for n in module_level_imports(local_source(name) or "") if local_source(n) is not None)
    return seen


def repo_script_source(name: str) -> Optional[str]:
    path = SCRIPTS_DIR / (name + ".py")
    return path.read_text(encoding="utf-8") if path.is_file() else None


def preflight_files(text: str) -> Tuple[List[Set[str]], List[Set[str]]]:
    """The files each ``test -f`` fence checks, and the files each ``EXTRACTION SCRIPT MISSING`` fence lists, one set per fence."""
    checked: List[Set[str]] = []
    listed: List[Set[str]] = []
    for fence in fences(text):
        if fence.label.lower() in SHELL_LABELS and fence.body.lstrip().startswith("test -f scripts/"):
            checked.append(set(re.findall(r"test -f (scripts/[A-Za-z0-9_.-]+\.py)", fence.body)))
        elif fence.body.startswith("EXTRACTION SCRIPT MISSING"):
            listed.append(set(re.findall(r"^ +- (scripts/[A-Za-z0-9_.-]+\.py)$", fence.body, re.MULTILINE)))
    return checked, listed


def expected_preflight(entry: str) -> Set[str]:
    """The extractor itself, and every local module it loads at import."""
    source = (SCRIPTS_DIR / (entry + ".py")).read_text(encoding="utf-8")
    return {"scripts/%s.py" % entry} | {"scripts/%s.py" % name for name in local_import_closure(source, repo_script_source)}


def test_the_closure_follows_module_level_imports_and_skips_lazy_ones():
    sources = {
        "a": "import os\nimport c\n",
        "b": "def f():\n    import d\n",
        "c": "try:\n    import e\nexcept ImportError:\n    pass\n",
        "d": "", "e": "",
    }
    assert local_import_closure("import a\nfrom b import f\n", sources.get) == ["a", "b", "c", "e"]
    assert local_import_closure("import os, sys\n", sources.get) == []


@pytest.mark.parametrize("stem", sorted(PREFLIGHTS))
def test_an_extraction_preflight_names_the_extractor_and_its_whole_import_closure(stem):
    expected = expected_preflight(PREFLIGHTS[stem])
    assert "scripts/tachi_parsers.py" in expected and "scripts/tachi_parts.py" in expected, expected
    checked, listed = preflight_files(spec_text(stem))
    assert len(checked) == 1 and len(listed) == 1, "%s.md must carry one test -f fence and one error text" % stem
    assert checked[0] == expected, "%s.md checks %s, and the extractor needs %s" % (stem, sorted(checked[0]), sorted(expected))
    assert listed[0] == expected, "%s.md's error lists %s, and the extractor needs %s" % (stem, sorted(listed[0]), sorted(expected))
    assert expected <= shipped_scripts(), "the manifest doesn't ship %s" % sorted(expected - shipped_scripts())
    assert "If any of these files is missing" in spec_text(stem) and "If either file is missing" not in spec_text(stem)


@pytest.mark.parametrize("stem", sorted(PREFLIGHTS))
def test_a_preflight_that_drops_a_helper_is_noticed(stem):
    expected = expected_preflight(PREFLIGHTS[stem])
    text = spec_text(stem)
    without_check = text.replace(" && test -f scripts/tachi_parts.py", "", 1)
    without_listing = text.replace("  - scripts/tachi_parts.py\n", "", 1)
    assert without_check != text and without_listing != text
    assert preflight_files(without_check)[0][0] != expected
    assert preflight_files(without_listing)[1][0] != expected


# =============================================================================
# 12. W2, lane C: the risk scorer, /tachi.risk-score and /tachi.threat-model (T029, T030, T031, T051)
# =============================================================================

RISK_SCORER_SPEC = "%s/risk-scorer.md" % AGENTS_DIR
RISK_SCORE_COMMAND = "%s/tachi.risk-score.md" % COMMANDS_DIR
THREAT_MODEL_COMMAND = "%s/tachi.threat-model.md" % COMMANDS_DIR
CONTROLS_COMMAND = "%s/tachi.compensating-controls.md" % COMMANDS_DIR  # section 13 (T038) tests it too
RISK_SCORING_REFERENCES = SKILLS_DIR + "/tachi-risk-scoring/references"
RISK_SCORES_TEMPLATE = "templates/tachi/output-schemas/risk-scores.md"
RISK_SCORES_SARIF_TEMPLATE = "templates/tachi/output-schemas/risk-scores.sarif"
STAGE_SCRIPT = SCRIPTS_DIR / "tachi-stage.py"

# ADR-050 D4's stop message (KB 20, PM finding 7), word for word. A command puts the Python version it found in the braces.
PYTHON_STOP_MESSAGE = ("PYTHON 3.9+ NOT FOUND \u2014 tachi renders this stage with Python 3.9 or later "
                       "(found: {version, or none}); install it and re-run")

# ADR-050 D6's dated note (2026-11-22, T023; amended at W4 by T146, from T067b's H2): Claude Code's Agent tool has no
# foreground option, so a command waits by ending its turn and resuming on each completion notice. These four sentences
# replace the word "foreground". Both commands, the shared part-file contract and the note carry them word for word. The
# first two run `reconcile` once, after every listed wave: a `reconcile` between waves spends a retry on every batch not yet
# dispatched, because a batch that was never dispatched looks like one whose agent wrote nothing.
COMPLETION_RULE = (
    "Dispatch every wave that `plan` or the latest `reconcile` listed, in order, before you run `reconcile`. "
    "Run `reconcile` once, after every agent of those waves has reported completion. "
    "While an agent you dispatched is still running, don't run the renderer, report a result or end the stage. "
    "If you end your turn to wait, resume this loop on each completion notice.")
# The first wording, which reads as one `reconcile` after each wave (T067b's H2), as the commands said it and as the note
# paraphrased it. No copy of either may survive. Step 3's "start a wave only after every agent of the wave before it" orders
# the waves, and stays.
PER_WAVE_WORDINGS = ("`reconcile` only after every agent in the wave", "`reconcile` only after every agent of the wave")
ADR_050 = "docs/architecture/02_ADRs/ADR-050-large-architecture-output-authority.md"

# A script that a W2 text names and that lane R1 writes in the same wave. T047 wires it into INSTALL_MANIFEST.md
# after the lanes return, so until the script is in the tree, naming it is allowed. Once the file exists, only
# the manifest makes it shipped, so a wiring commit that forgets the manifest fails here.
WIRED_BY_T047 = frozenset({"scripts/render-risk-scores.py"})

# The codes each script returns (ADR-050 D4, contracts/cli.md). A command routes every one of them.
SCRIPT_EXITS = {
    "version": {"0", "2"},
    "plan": {"0", "1", "2"},
    "reconcile": {"0", "1", "2", "3", "4"},
    "render": {"0", "4", "5", "anything else"},  # 1 and 2 are "anything else": a plan exists, so Step F runs
    "architecture-source": {"0", "1", "2", "5"},
}

RISK_SCORE_CALLS = [
    "python3 scripts/tachi-stage.py --version",
    "python3 scripts/populate-affected-assets.py --architecture '{architecture_path}' --threats '{input_file}'",
    "python3 scripts/tachi-stage.py plan --stage risk-score --out '{output_dir}' --date {scoring_date} --threats '{input_dir}/threats.md'",
    "python3 scripts/tachi-stage.py reconcile --stage risk-score --out '{output_dir}' --plan {plan_id} --plan-digest {plan_digest}",
    "python3 scripts/render-risk-scores.py --out '{output_dir}' --plan {plan_id} --plan-digest {plan_digest}",
    "python3 scripts/tachi-stage.py fail --stage risk-score --out '{output_dir}' --plan {plan_id} --plan-digest {plan_digest} --reason {reason}",
]
THREAT_MODEL_CALLS = [
    "python3 scripts/tachi-stage.py --version",
    "python3 scripts/populate-affected-assets.py --architecture '{output_dir}/architecture.md' --threats '{output_dir}/threats.md'",
    "python3 scripts/tachi-stage.py architecture-source --threats '{output_dir}/threats.md' --architecture '{architecture_path}'",
]

# T068's S7-2: every path that a command puts into a `python3` call goes in single quotes, so the shell expands nothing in it,
# whatever name the scanned repository gives a directory. Double quotes would still run `$(` and backticks. These placeholders
# are a script's own output or a date the command computes, so they stay bare. Each command states the rule once, in these words.
BARE_PLACEHOLDERS = frozenset({"{plan_id}", "{plan_digest}", "{reason}", "{scoring_date}", "{analysis_date}"})
PATH_QUOTING_RULE = (
    "**Paths go in single quotes**: put each path into its call between the single quotes that the call shows, so the shell "
    "expands nothing in it. Inside quotes the shell doesn't expand a leading `~` either, so write the home directory's path in "
    "its place. A path that holds a single quote can't be quoted this way: stop there, and print the path.")


def shipped_or_wired_by_t047() -> Set[str]:
    """The manifest's scripts, plus a W2 script that is neither in the manifest nor in the tree yet."""
    return shipped_scripts() | {name for name in WIRED_BY_T047 if not (REPO_ROOT / name).exists()}


def calls(text: str) -> List[str]:
    """The command of every shell fence in ``text``, comments dropped, continuations joined and spaces collapsed."""
    found: List[str] = []
    for fence in fences(text):
        if fence.label.lower() in SHELL_LABELS:
            lines = [line for line in fence.body.splitlines() if line.strip() and not line.strip().startswith("#")]
            found.append(" ".join(re.sub(r"\\\n\s*", " ", "\n".join(lines)).split()))
    return found


def python3_calls(text: str) -> List[str]:
    """Every ``python3 scripts/...`` line in any fence of ``text``, an agent prompt's included, continuations joined."""
    found: List[str] = []
    for fence in fences(text):
        for line in re.sub(r"\\\n\s*", " ", fence.body).splitlines():
            if line.strip().startswith("python3 scripts/"):
                found.append(" ".join(line.split()))
    return found


def unquoted_placeholders(command: str) -> List[str]:
    """The placeholders of ``command`` outside single quotes, other than a script's output or a computed date (S7-2)."""
    return [name for name in re.findall(r"\{[a-z_]+\}", re.sub(r"'[^']*'", "", command)) if name not in BARE_PLACEHOLDERS]


def routes(text: str, anchor: str, where: str) -> Dict[str, str]:
    """One step's exit-code table: the code, as written, to what the command does."""
    table = table_after(text, anchor, where=where)
    assert table.header[0] == "Exit", "%s: the table after %r is not an exit table: %s" % (where, anchor, table.header)
    return {row[0]: row[-1] for row in table.rows}


def step_of(text: str, anchor: str, where: str) -> str:
    return section_text(text, anchor, where=where, keep_fences=True)


def the_fixed_prompt() -> str:
    """The one-line dispatch prompt, as the part contract quotes it (ADR-050 D3)."""
    found = re.findall(r"`(Read and follow the batch input at <input_path>\. Write only the part file it names\.)`",
                       text_of(PART_CONTRACT))
    assert len(found) >= 1 and len(set(found)) == 1, "the part contract no longer quotes one fixed prompt: %s" % found
    return found[0]


def stage_reasons() -> Set[str]:
    """The ``--reason`` values of ``tachi-stage.py fail``: the keys of its ``REASONS`` table."""
    tree = ast.parse(STAGE_SCRIPT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "REASONS" for t in node.targets):
            return {key.value for key in node.value.keys}  # type: ignore[attr-defined]
    raise ReferenceDrift("tachi-stage.py has no REASONS table")


def check_statement(text: str) -> str:
    """The one line of ``text`` that states the narrative check, which is a blockquote."""
    lines = [line for line in text.splitlines() if line.startswith("> **No digit outside a slot.**")]
    assert len(lines) == 1, "expected one check statement, found %d" % len(lines)
    return lines[0]


# --- the helpers, on samples ---------------------------------------------------------------------


def test_calls_joins_continuations_drops_comments_and_ignores_other_fences():
    sample = "```bash\n# note\npython3 scripts/a.py \\\n  --x 1 \\\n  --y 2\n```\n\n```text\nnot a call\n```\n"
    assert calls(sample) == ["python3 scripts/a.py --x 1 --y 2"]


def test_routes_reads_the_exit_table_after_an_anchor():
    sample = "## Step 9: x\n\n   | Exit | What to do |\n   |------|------------|\n   | 0 | Go on |\n   | anything else | Stop |\n"
    assert routes(sample, "## Step 9:", "the sample") == {"0": "Go on", "anything else": "Stop"}
    with pytest.raises(AssertionError):
        routes("## Step 9: x\n\n| Code | Meaning |\n|---|---|\n| 0 | x |\n", "## Step 9:", "the sample")


def test_python3_calls_reads_every_fence_and_the_quoting_check_finds_a_bare_path():
    sample = ("```text\nRun this:\n    python3 scripts/a.py \\\n      --x '{output_dir}/t.md'\n```\n\n"
              "```bash\npython3 scripts/b.py --out {output_dir} --plan {plan_id}\n```\n")
    assert python3_calls(sample) == ["python3 scripts/a.py --x '{output_dir}/t.md'", "python3 scripts/b.py --out {output_dir} --plan {plan_id}"]
    assert unquoted_placeholders(python3_calls(sample)[0]) == []
    assert unquoted_placeholders(python3_calls(sample)[1]) == ["{output_dir}"], "a script's own output, {plan_id}, stays bare"
    assert unquoted_placeholders('python3 scripts/b.py --out "{output_dir}"') == ["{output_dir}"], "double quotes still run $("


# --- the presence check (ADR-050 D4, KB 20, PM finding 7) -------------------------------------------


@pytest.mark.parametrize("path, no_plan_words", [
    (RISK_SCORE_COMMAND, "No plan exists yet"),
    (THREAT_MODEL_COMMAND, "nothing to fail"),
    (CONTROLS_COMMAND, "No plan exists yet"),
])
def test_step_1_runs_the_presence_check_and_stops_below_the_python_floor(path, no_plan_words):
    step = step_of(text_of(path), "## Step 1:", path)
    assert "python3 scripts/tachi-stage.py --version" in calls(step)
    assert PYTHON_STOP_MESSAGE in step
    assert "exit code 2" in step and "below the 3.9 floor" in step and "`python3`" in step, "Step 1 must route the floor's exit code 2"
    assert no_plan_words in step, "Step 1 stops before any plan exists, so it runs no fail step"
    # the check runs before the command dispatches or plans anything
    text = text_of(path)
    assert text.index("python3 scripts/tachi-stage.py --version") < min(
        i for i in (text.find("Agent tool"), text.find("scripts/tachi-stage.py plan"), text.find("`tachi-orchestrator` agent")) if i >= 0)


def test_the_script_the_presence_check_runs_prints_its_version_and_enforces_the_floor():
    source = STAGE_SCRIPT.read_text(encoding="utf-8")
    assert 'parser.add_argument("--version", action="version"' in source
    assert source.index("sys.version_info < (3, 9)") < source.index("import argparse"), "the floor is checked before any import"
    assert "sys.exit(2)" in source[source.index("sys.version_info < (3, 9)"):source.index("import argparse")]


# --- /tachi.risk-score (T030) ---------------------------------------------------------------------


def test_risk_score_runs_only_the_shipped_scripts_it_names_and_each_fence_is_one_python3_call():
    text = text_of(RISK_SCORE_COMMAND)
    allowed = shipped_or_wired_by_t047()
    assert calls(text) == RISK_SCORE_CALLS
    for fence in fences(text):
        if fence.label.lower() in SHELL_LABELS:
            assert not command_problems(fence.body, allowed), fence.body
    named = set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", text))
    assert named <= allowed, "the command names a script that isn't shipped: %s" % sorted(named - allowed)
    assert directive_hits(text) == []


def test_risk_score_step_0_adds_the_two_flags_and_no_date_flag():
    text = text_of(RISK_SCORE_COMMAND)
    step = step_of(text, "## Step 0:", RISK_SCORE_COMMAND)
    for flag in ("--output-dir <path>", "--baseline <run-dir>", "--architecture-path <path>"):
        assert flag in step, flag
    assert "--date" not in step, "the command exposes no --date flag (PM-T5)"
    assert text.count("--date") == 1, "the one --date is the planner's, and the command computes the date once"
    assert "Set `scoring_date` to today's date" in step_of(text, "## Step 2:", RISK_SCORE_COMMAND)
    assert "the plan's date" in step_of(text, "## Step 2:", RISK_SCORE_COMMAND), "a resumed run uses the plan's date"


def test_risk_score_step_1_5_keeps_the_populator_and_retires_the_copy_verbatim_instructions():
    text = text_of(RISK_SCORE_COMMAND)
    step = step_of(text, "## Step 1.5:", RISK_SCORE_COMMAND)
    assert calls(step) == [RISK_SCORE_CALLS[1]]
    for skip in ("`input_format == sarif`", "`architecture_path == null`", "`--output-dir` names a directory other"):
        assert skip in step, "Step 1.5 lost a skip rule: %s" % skip
    lowered = text.lower()
    for gone in ("verbatim", "author", "copies it as it stands", "affected_assets` value", "single value authority"):
        assert gone not in lowered, "the command still says %r" % gone
    assert "one source per run" in step, "Step 1.5 states the one tag source (ADR-050 D2, S-13)"


def test_risk_score_plans_once_with_the_command_date_and_the_canonical_threats_path():
    step = step_of(text_of(RISK_SCORE_COMMAND), "## Step 2:", RISK_SCORE_COMMAND)
    assert calls(step) == [RISK_SCORE_CALLS[2]]
    assert "`--baseline-dir '{baseline_dir}'`" in step and "`--architecture '{architecture_flag}'`" in step
    assert "and only then" in step, "only the explicit flag may reach --architecture, or a per-run snapshot would set every SARIF URI"
    assert "`plan` reads `threats.sarif` when `threats.md` is absent" in step, "AR-T2: the SARIF fallback is the planner's"


@pytest.mark.parametrize("anchor, script", [("## Step 2:", "plan"), ("## Step 4:", "reconcile"), ("## Step 5:", "render")])
def test_risk_score_routes_every_exit_code_of_each_script(anchor, script):
    table = routes(text_of(RISK_SCORE_COMMAND), anchor, RISK_SCORE_COMMAND)
    assert set(table) == SCRIPT_EXITS[script], "%s routes %s, and the script returns %s" % (anchor, sorted(table), sorted(SCRIPT_EXITS[script]))


def test_risk_score_routing_follows_the_exit_table():
    text = text_of(RISK_SCORE_COMMAND)
    plan = routes(text, "## Step 2:", RISK_SCORE_COMMAND)
    assert plan["0"] == "Go to Step 3" and plan["1"].startswith("Stop and print the error")
    assert plan["2"].startswith("Stop and print the error") and "nothing to fail" in plan["2"], "2 runs fail only once a plan exists"
    reconcile = routes(text, "## Step 4:", RISK_SCORE_COMMAND)
    assert reconcile["0"] == "Go to Step 5"
    assert reconcile["3"].startswith("Dispatch exactly the batches `waves` lists") and "while the exit code is 3" in reconcile["3"]
    assert reconcile["4"] == "Go to Step F with `--reason unrecoverable-batch`"
    assert reconcile["2"] == "Go to Step F with `--reason check-failed`"
    assert reconcile["1"] == "Stop and print the error"
    render = routes(text, "## Step 5:", RISK_SCORE_COMMAND)
    assert render["0"] == "Success. Go to Step 6"
    assert render["5"].startswith("Success with warnings. Print the warnings")
    assert render["4"] == "A completeness or parity check failed. Go to Step F with `--reason check-failed`"
    assert render["anything else"] == "Go to Step F with `--reason render-failed`"


def test_risk_score_dispatches_the_typed_agent_with_the_fixed_prompt_and_waits_for_completion():
    text = text_of(RISK_SCORE_COMMAND)
    step = step_of(text, "## Step 3:", RISK_SCORE_COMMAND)
    prompts = [f.body for f in fences(step) if "Read and follow" in f.body]
    assert prompts == [the_fixed_prompt()], "the dispatch prompt is the part contract's one fixed line, and nothing else"
    assert "`subagent_type` set to `tachi-risk-scorer`" in step
    assert "tachi-risk-scorer" in roster_names()
    assert named_tachi_tokens(text) <= roster_names() | skill_directories()
    assert COMPLETION_RULE in step, "ADR-050 D6's completion rule, word for word"
    assert "foreground" not in text.lower(), "the Agent tool has no foreground option"
    assert "Never send more than 16 in one message" in step and "at most 16 batches each" in step_of(text, "## Step 2:", RISK_SCORE_COMMAND)
    assert "end the run there" in step and "Run no substitute" in step
    assert "`--reason agent-not-spawned` and `--detail tachi-risk-scorer`" in step
    # the old prompt, which handed the agent the whole pipeline and the output files, is gone
    for gone in ("Score the threat model output using your complete scoring pipeline", "Input format:", "Scoring date:",
                 "Write output files", "Read the input file yourself"):
        assert gone not in text, gone


def test_risk_score_step_f_runs_fail_with_one_of_the_scripts_reasons_and_never_twice():
    text = text_of(RISK_SCORE_COMMAND)
    step = step_of(text, "## Step F:", RISK_SCORE_COMMAND)
    assert calls(step) == [RISK_SCORE_CALLS[5]]
    reasons = stage_reasons()
    assert reasons == {"agent-not-spawned", "unrecoverable-batch", "check-failed", "render-failed"}
    named = set(re.findall(r"`(--reason )?(agent-not-spawned|unrecoverable-batch|check-failed|render-failed)`", step))
    assert {reason for _, reason in named} == reasons, "Step F names every reason, and the routing above uses only these"
    used = set(re.findall(r"--reason ([a-z-]+)`", text))
    assert used <= reasons, "a step sends Step F a reason the script doesn't have: %s" % sorted(used - reasons)
    assert "`fail` never runs a second time" in step and "Whatever `fail` exits with, stop there" in step


def test_risk_score_reports_the_renderers_summary_and_restates_no_number():
    text = text_of(RISK_SCORE_COMMAND)
    step = step_of(text, "## Step 6:", RISK_SCORE_COMMAND)
    assert "exactly as it wrote them" in step and "Restate no number" in step
    for gone in ("RISK SCORING COMPLETE", "Severity Distribution", "{count}", "Highest-Risk Component", "(supersedes threats.sarif)"):
        assert gone not in text, "the model-composed summary and its stale claim are gone: %s" % gone


# --- /tachi.threat-model (T051) --------------------------------------------------------------------


def test_threat_model_runs_only_shipped_scripts_in_one_python3_call_per_fence():
    text = text_of(THREAT_MODEL_COMMAND)
    allowed = shipped_or_wired_by_t047()
    assert calls(text) == THREAT_MODEL_CALLS
    for fence in fences(text):
        if fence.label.lower() in SHELL_LABELS:
            assert not command_problems(fence.body, allowed), fence.body
    assert set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", text)) <= allowed
    assert directive_hits(text) == []


def test_threat_model_keeps_p2_s_anchors_and_adds_step_2_7_between_them():
    text = text_of(THREAT_MODEL_COMMAND)
    headings = [line for line in text.splitlines() if line.startswith("## Step ")]
    numbers = [re.match(r"## Step ([0-9.]+):", h).group(1) for h in headings]
    assert numbers == ["0", "1", "1.4", "2", "2.5", "2.7", "3"], numbers
    assert not re.search(r"^## Step 2\.6", text, re.MULTILINE), "Step 2.6 stays free for #396 (P-2)"
    assert text.count("## Step 2.5: Re-assert Affected Assets Block (idempotent safety net)") == 1
    assert text.count("## Step 3: Report Results") == 1


def test_threat_model_step_2_7_writes_the_architecture_source_from_the_commands_own_path():
    text = text_of(THREAT_MODEL_COMMAND)
    step = step_of(text, "## Step 2.7:", THREAT_MODEL_COMMAND)
    assert calls(step) == [THREAT_MODEL_CALLS[2]]
    assert "the `{architecture_path}` that Step 0 resolved, and never the snapshot in `{output_dir}`" in step
    assert "FR-E.18" in step and "ADR-050 D7" in step
    # the same call, and the same flags, are what the script's parser takes
    source = STAGE_SCRIPT.read_text(encoding="utf-8")
    assert 'commands.add_parser("architecture-source"' in source
    assert 'source.add_argument("--threats", required=True' in source and 'source.add_argument("--architecture", required=True' in source


def test_threat_model_routes_the_presence_check_and_the_carrier_write_by_the_exit_table():
    text = text_of(THREAT_MODEL_COMMAND)
    carrier = routes(text, "## Step 2.7:", THREAT_MODEL_COMMAND)
    assert set(carrier) == SCRIPT_EXITS["architecture-source"]
    assert carrier["0"] == "Continue to Step 3"
    assert carrier["5"].startswith("The carrier warning is on stderr. Print it and continue to Step 3"), "5 prints the warning and continues (AR-T5)"
    assert carrier["1"] == "Stop and print the error"
    assert carrier["2"].startswith("Stop and print the error") and "nothing to fail" in carrier["2"], "this command makes no plan"


# --- the rules the commands share (T146: T067b's H2, T068's S7-2) ------------------------------------


@pytest.mark.parametrize("path", [RISK_SCORE_COMMAND, CONTROLS_COMMAND, PART_CONTRACT, ADR_050])
def test_the_completion_rule_is_one_text_and_the_per_wave_wording_is_gone(path):
    text = text_of(path)
    assert text.count(COMPLETION_RULE) == 1, "%s must quote ADR-050 D6's completion rule once, word for word" % path
    for old in PER_WAVE_WORDINGS:
        assert old not in text, "%s still reads as a reconcile after each wave (T067b's H2): %r" % (path, old)


def test_the_per_wave_check_catches_both_first_wordings_and_spares_the_wave_order():
    command = "Run `reconcile` only after every agent in the wave has reported completion."
    note = "the layer runs `reconcile` only after every agent of the wave has reported completion;"
    order = "start a wave only after every agent of the wave before it has reported completion."
    assert [old for old in PER_WAVE_WORDINGS if old in command] and [old for old in PER_WAVE_WORDINGS if old in note]
    assert not [old for old in PER_WAVE_WORDINGS if old in order], "Step 3's wave order is not the per-wave reconcile"


@pytest.mark.parametrize("path, expected", [(RISK_SCORE_COMMAND, 5), (CONTROLS_COMMAND, 4), (THREAT_MODEL_COMMAND, 3)])
def test_every_path_in_a_commands_python3_calls_is_single_quoted(path, expected):
    text = text_of(path)
    taking = [call for call in python3_calls(text) if re.search(r"\{[a-z_]+\}", call)]
    assert len(taking) == expected, "%s: expected %d calls that take a placeholder, found %s" % (path, expected, taking)
    for call in taking:
        assert not unquoted_placeholders(call), "%s leaves %s outside single quotes" % (call, unquoted_placeholders(call))
    added = [span for span in re.findall(r"`(--[a-z-]+ [^`]*)`", prose(text)) if re.search(r"\{[a-z_]+\}", span)]
    for span in added:   # the flags that a step adds to a call, such as --baseline-dir
        assert not unquoted_placeholders(span), "%s: the added flag %s leaves a path outside single quotes" % (path, span)
    assert text.count(PATH_QUOTING_RULE) == 1, "%s must state the quoting rule once, in the shared words" % path


# --- the scorer's spec (T029) ----------------------------------------------------------------------


def test_the_scorer_loads_the_part_contract_and_states_its_check_in_the_references_words():
    spec = text_of(RISK_SCORER_SPEC)
    assert "**MANDATORY**: Read `%s` before you write anything" % PART_CONTRACT in spec
    assert check_statement(spec) == check_statement(text_of(PART_CONTRACT))
    assert "Reachability prose uses slots only" in spec
    assert text_of(SARIF_IDENTITY).count("**You never write SARIF.**") == 1 and SARIF_IDENTITY in spec


def test_every_slot_the_scorer_names_is_a_slot_of_its_stage():
    spec = text_of(RISK_SCORER_SPEC)
    tokens = set(re.findall(r"\{\{[^{}]*\}\}", spec)) - {"{{kind:arg}}"}
    assert len(tokens) >= 8, tokens
    for token in sorted(tokens):
        assert tachi_parts.narrative_problem(token, "risk-score") is None, token


def test_the_scorers_example_part_is_accepted_by_the_validator_with_no_flag():
    blocks = [f.body for f in fences(text_of(RISK_SCORER_SPEC)) if f.label == "json"]
    assert len(blocks) == 1, "the spec carries one example part"
    part = json.loads(blocks[0])
    assert part["stage"] == "risk-score" and part["agent_type"] == "tachi-risk-scorer"
    result = tachi_parts.classify_part(part, part["plan_id"], part["batch_id"], "risk-score", part["agent_type"], part["finding_ids"])
    assert result.state == "done" and result.flags == {}, (result.state, result.detail, result.flags)


def test_the_scorer_example_reachability_sentence_is_a_valid_narrative():
    spec = text_of(RISK_SCORER_SPEC)
    example = re.search(r"For example: `([^`]+)`", spec)
    assert example, "the reachability section carries an example sentence"
    assert tachi_parts.narrative_problem(example.group(1), "risk-score") is None


def test_the_scorer_is_judgment_only_and_authors_no_output_file():
    spec = text_of(RISK_SCORER_SPEC)
    assert text_of(RISK_SCORER_SPEC).count(NO_HAND_BACK) == 1
    assert not re.search(r"^#{2,4} (9[a-h]|10[a-j])\.", spec, re.MULTILINE), "the per-section output instructions are gone"
    for gone in ("partialFingerprints", "relatedLocations", "semanticVersion", "owner/tachi", "Never modify, regenerate, or re-hash",
                 "Generate a `risk-scores.md`", "Generate a `risk-scores.sarif`", "MUST conform", "Value source", "byte-for-byte",
                 "dfd_element_type", "Post-Parsing Gate", "Rule ID to Category Reverse Mapping"):
        assert gone not in spec, "the scorer spec still carries %r" % gone
    for kept in ("`tachi.part/1`", "`tachi.overflow/1`", "`part_path`", "`cvss_vector`", "`tachi_scoring`'s prefix resolver (`category_for_prefix`)"):
        assert kept in spec, kept
    names = set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", spec))
    assert names <= shipped_or_wired_by_t047(), sorted(names - shipped_or_wired_by_t047())


def test_the_scorer_names_each_sarif_tool_with_r_33_s_case_and_states_the_count_rule_once_per_place():
    spec = text_of(RISK_SCORER_SPEC)
    tools = {k: v for k, v in sc.TOOL_NAMES.items()}
    assert "`%s`" % tools["risk-scores.sarif"] in spec and "`%s`" % tools["threats.sarif"] in spec
    assert tools["threats.sarif"] == "Tachi" and "`tachi`" not in spec, "R-33: the threats tool has a capital T"
    # D-6(a)'s four sentences, each reworded once to the open-findings rule
    assert spec.count("one entry for each open finding") == 1          # was :450, section 9h
    assert spec.count("with one result for each open finding") == 1    # was :456, section 10
    assert spec.count("Each result is one open finding") == 1           # was :474, section 10c
    assert spec.count("both files count the same open findings") == 1  # was :548, section 10j
    for old in ("All scored findings MUST appear", "one result object per scored finding", "finding count"):
        assert old not in spec, old


def test_the_scorer_words_the_affected_assets_provenance_as_d2_rules():
    d2 = ("`affected_assets` lists the tags the asset-modifier step used for this finding. Emitting it changes no score; "
          "only the modifier step does, and it reads the same tags from the same source (ADR-050 D2).")
    assert d2 in text_of(RISK_SCORER_SPEC)
    assert d2 in text_of(RISK_SCORING_REFERENCES + "/asset-modifiers.md")
    for path in (RISK_SCORER_SPEC, RISK_SCORE_COMMAND, RISK_SCORING_REFERENCES + "/asset-modifiers.md"):
        assert "does NOT affect scoring" not in text_of(path) and "copy verbatim" not in text_of(path).lower(), path


# --- the template and the references (T031) --------------------------------------------------------


def test_the_scores_template_is_schema_1_1_with_2a_flags_and_the_score_integrity_section():
    text = text_of(RISK_SCORES_TEMPLATE)
    assert text.count('schema_version: "1.1"') == 1 and "Schema version : 1.1" in text
    assert "Always `\"1.1\"` for this release" in text and "Always `\"1.0\"`" not in text
    headings = [line for line in text.splitlines() if line.startswith("## ")]
    assert headings == [
        "## 1. Executive Summary", "## 2. Scored Threat Table", "## 2a. Resolved Findings", "## 3. Dimensional Breakdown",
        "## 4. Governance Fields", "## 5. Scoring Methodology", "## 6. Score Integrity"]
    subs = [line for line in section_text(text, "## 6. Score Integrity", RISK_SCORES_TEMPLATE, keep_fences=True).splitlines()
            if line.startswith("### ")]
    assert subs == ["### Integrity Summary", "### Score Flags", "### Input Issues", "### Scoring Inputs"]
    flags = table_after(text, "### Score Flags", where=RISK_SCORES_TEMPLATE)
    assert flags.header == ["ID", "Flag", "Field", "Stored", "Rendered", "Cause"]
    inputs = table_after(text, "### Scoring Inputs", where=RISK_SCORES_TEMPLATE)
    assert inputs.header == ["ID", "Field", "Value"]
    scored = table_after(text, "## 2. Scored Threat Table", where=RISK_SCORES_TEMPLATE)
    resolved = table_after(text, "## 2a. Resolved Findings", where=RISK_SCORES_TEMPLATE)
    assert scored.header[-1] == "Flags" and resolved.header[-1] == "Flags"
    assert resolved.header[:len(scored.header) - 1] == scored.header[:-1] and resolved.header[-4:-1] == ["Status", "Owner", "Review Date"]
    assert "**Integrity**:" in section_text(text, "## 3. Dimensional Breakdown", RISK_SCORES_TEMPLATE)
    assert text.rstrip().splitlines()[-1].startswith("<!-- tachi-provenance: renderer=render-risk-scores.py; version=")


def numbers_in(line: str) -> List[str]:
    """The integers in a line of prose, with any ISO date taken out first."""
    return re.findall(r"\d+", re.sub(r"\d{4}-\d{2}-\d{2}", "", line))


# Sample numbers for the template's placeholders: ten open findings, one Critical, two High, three Medium and four Low.
SAMPLE_COUNTS = {"total_findings": "10", "critical_count": "1", "high_count": "2", "medium_count": "3", "low_count": "4",
                 "critical_pct": "10", "high_pct": "20", "medium_pct": "30", "low_pct": "40", "resolved_count": "3"}


def filled_template() -> str:
    """The scores template with each placeholder replaced by its sample number, or else by its own name."""
    return re.sub(r"\{([a-z_]+)\}", lambda m: SAMPLE_COUNTS.get(m.group(1), m.group(1)), text_of(RISK_SCORES_TEMPLATE))


def test_the_scores_template_stays_readable_by_the_extractors_readers():
    import tachi_parsers
    found = tachi_parsers.parse_risk_scores_findings(re.sub(r"\{([a-z_]+)\}", r"\1", text_of(RISK_SCORES_TEMPLATE)))
    assert len(found) == 1
    assert found[0] == {"id": "id", "component": "component", "threat": "threat", "composite_score": "composite_score",
                        "severity": "severity_band", "cvss": "cvss_base", "exploitability": "exploitability"}


def test_the_scores_template_keeps_the_severity_distribution_the_report_extractors_read():
    # NFR-1: the report and infographic extractors take their severity counts from this table, so its shape is part of 1.1.
    import tachi_parsers
    template = filled_template()
    assert tachi_parsers.parse_risk_scores_severity(template) == {"critical": 1, "high": 2, "medium": 3, "low": 4, "note": 0, "total": 10}
    rows = tachi_parsers.parse_markdown_table(template, "Severity Distribution")
    assert [row["Severity"] for row in rows][:4] == ["Critical", "High", "Medium", "Low"]
    assert list(rows[0]) == ["Severity", "Count", "Percentage"]
    assert template.count("Severity Distribution") == template.count("**Severity Distribution:**") + template.count("The Severity Distribution table"), \
        "no earlier line holds the phrase, because the reader starts at its first occurrence"
    assert template.index("**Severity Distribution:**") < template.index("The Severity Distribution table")


def test_the_scores_template_has_one_summary_sentence_and_a_separate_resolved_line():
    # The goldens (T027) find exactly one line of Section 1 that states the open count and then the four bands, and one
    # more that counts the RESOLVED findings.
    body = section_text(filled_template(), "## 1. Executive Summary", RISK_SCORES_TEMPLATE)
    prose = [re.sub(r"[*`>]", "", line).strip() for line in body.split("\n")
             if line.strip() and not line.strip().startswith(("|", "---", "<!--", "#"))]
    counts = ["10", "1", "2", "3", "4"]
    sentences = [line for line in prose if numbers_in(line)[:5] == counts]
    assert len(sentences) == 1, prose
    assert len(re.findall(r"[.!?](?:\s|$)", sentences[0])) == 1, "one sentence"
    assert [sentences[0].index(band) for band in ("Critical", "High", "Medium", "Low")] == sorted(
        sentences[0].index(band) for band in ("Critical", "High", "Medium", "Low"))
    assert [line for line in prose if line != sentences[0] and "resolved" in line.lower() and "3" in numbers_in(line)]


def test_the_sarif_template_names_the_real_repository_and_the_d7_d8_identity_shape():
    document = json.loads(text_of(RISK_SCORES_SARIF_TEMPLATE))
    run = document["runs"][0]
    assert run["tool"]["driver"]["informationUri"] == sc.INFORMATION_URI == "https://github.com/davidmatousek/tachi"
    assert run["tool"]["driver"]["name"] == sc.TOOL_NAMES["risk-scores.sarif"]
    assert "owner/tachi" not in text_of(RISK_SCORES_SARIF_TEMPLATE) and "automationDetails" not in document["runs"][0]
    assert "tachi_provenance" not in run, "the renderer adds the stamp; the template is a skeleton"
    for result in run["results"]:
        assert set(result["partialFingerprints"]) == {"primaryLocationLineHash", "findingId/v1"}, result["partialFingerprints"]
        assert "relatedLocations" not in result, "no relatedLocations entry names a finding in this file"
        assert result["locations"][0]["physicalLocation"]["region"] == {"startLine": 1}
        assert isinstance(result["properties"]["score-flags"], list) and "affected_assets" in result["properties"]
    correlated = [r for r in run["results"] if "correlation-group" in r["properties"]]
    assert [r["properties"]["correlation-role"] for r in correlated] == ["primary", "peer"]
    for result in correlated:
        assert set(sc.CORRELATION_KEYS) <= set(result["properties"])
        assert "Correlated in CG-1; " in result["message"]["text"]


def test_cvss_vectors_documents_a_category_for_every_prefix_as_the_code_resolves_them():
    text = text_of(RISK_SCORING_REFERENCES + "/cvss-vectors.md")
    rows = table_after(text, "**Category defaults with bounded ranges**", where="cvss-vectors.md").rows
    documented = {row[0]: {p.strip() for p in row[1].split(",")} for row in rows}
    expected: Dict[str, Set[str]] = {}
    for prefix, category in tachi_scoring.PREFIX_CATEGORY.items():
        expected.setdefault(category, set()).add(prefix)
    assert not diff("cvss-vectors.md prefix column", documented, expected)
    assert "`category_for_prefix`" in text and "all 12 prefixes" in text
    assert "Step 3 -- Compute CVSS 3.1 base score (the renderer)" in text
    assert "Step 3 -- Compute CVSS 3.1 base score**" not in text


def test_severity_bands_reference_equals_the_embedded_bands_and_carries_the_d9_rules():
    text = text_of(RISK_SCORING_REFERENCES + "/severity-bands.md")
    governance = {row[0]: (strip_ticks(row[1]), strip_ticks(row[2]))
                  for row in table_after(text, "### Severity-to-Governance Mapping", where="severity-bands.md").rows}
    assert not diff("severity-bands.md governance table", governance,
                    {band: (v["sla"], v["disposition"]) for band, v in tachi_scoring.SEVERITY_BANDS.items()})
    minimums = {row[0]: re.search(r"Score >= ([0-9.]+)", row[2]) for row in
                table_after(text, "## Severity Band Mapping", where="severity-bands.md").rows}
    assert {band: m.group(1) for band, m in minimums.items() if m} == {
        band: str(v["min"]) for band, v in tachi_scoring.SEVERITY_BANDS.items() if band != "Low"}
    for fact in ("`divergent:composite_score:primary=<ID>`", "`override:<field>:human`", "`retagged`", "corrected:review_date:baseline-date",
                 "unchecked:review_date:scoring-date-unknown", "corrected:review_date:clock-restarted", "rounded half up"):
        assert fact in text, fact


def test_output_formatting_sorts_by_the_s2_order_and_escapes_after_it_truncates():
    text = text_of(RISK_SCORING_REFERENCES + "/output-formatting.md")
    ranks = enum_after(text, "first by prefix rank, which is ")
    assert tuple(ranks) == tachi_parts.FINDING_PREFIXES, "the documented prefix rank is S-2's"
    assert "natural alphanumeric order" not in text.replace('"natural alphanumeric" order', "")
    assert "truncates the raw text first, and escapes what is left afterwards" in text
    assert "`Flags`" in text and "Section 2a" in text and "## Score Integrity (Section 6)" in text
    names = table_after(text, "## Category Display Name Mapping", where="output-formatting.md").rows
    assert {strip_ticks(row[0]) for row in names} == set(tachi_scoring.CATEGORY_DEFAULT_VECTORS), "a display name for each category the code scores"
    assert "as `tachi_scoring.category_for_prefix` returns it" in text


def test_asset_modifiers_uses_r_25_s_formula_and_ends_the_unchanged_exemption():
    text = text_of(RISK_SCORING_REFERENCES + "/asset-modifiers.md")
    assert "cvss_base_after_modifier = max(assessed_cvss_base, min(modifier_ceiling, recompute_cvss(elevated_vector)))" in text
    assert "cvss_base_after_modifier = min(modifier_ceiling" not in text
    assert "An `UNCHANGED` finding is no longer exempt" in text and "ADR-050 D9" in text
    assert "inherit baseline scores verbatim and never re-enter" not in text and "score_source: inherited` \u2014 same reason" not in text
    # R-25 against the shipped calculator: a finding already above the ceiling keeps its assessed score
    assessed = tachi_scoring.base_score("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H")
    elevated = tachi_scoring.base_score(tachi_scoring.elevate("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H", ["pii"]))
    assert assessed > tachi_scoring.MODIFIER_CEILING and max(assessed, min(tachi_scoring.MODIFIER_CEILING, elevated)) == assessed


# =============================================================================
# 13. W3, lane D: /tachi.compensating-controls, the control analyzer's spec, the controls references and the SARIF
#     guide (T037, T038; ADR-050 D2, D4, D6, D7; FR-K7.4, FR-K8.3)
# =============================================================================

CONTROL_ANALYZER_SPEC = "%s/control-analyzer.md" % AGENTS_DIR
CONTROLS_REFERENCES = SKILLS_DIR + "/tachi-control-analysis/references"
SARIF_GENERATION_GUIDE = ADAPTER_AGENTS + "/references/sarif-generation.md"

# The controls renderer is written by another lane in the same wave (T035), and T039 wires it into INSTALL_MANIFEST.md.
# Until the script is in the tree, naming it is allowed. Once the file exists, only the manifest makes it shipped,
# so a wiring commit that forgets the manifest fails here.
WIRED_BY_T039 = frozenset({"scripts/render-compensating-controls.py"})

CONTROLS_CALLS = [
    "python3 scripts/tachi-stage.py --version",
    "python3 scripts/tachi-stage.py plan --stage compensating-controls --out '{output_dir}' --date {analysis_date} "
    "--risk-scores '{input_dir}/risk-scores.md' --target '{target_path}'",
    "python3 scripts/tachi-stage.py reconcile --stage compensating-controls --out '{output_dir}' --plan {plan_id} --plan-digest {plan_digest}",
    "python3 scripts/render-compensating-controls.py --out '{output_dir}' --plan {plan_id} --plan-digest {plan_digest}",
    "python3 scripts/tachi-stage.py fail --stage compensating-controls --out '{output_dir}' --plan {plan_id} --plan-digest {plan_digest} "
    "--reason {reason}",
]
# The helpers that the two scripts import. Step 1's installed-files check names them, so that a missing helper is reported as
# an installation error and never as a missing Python (the architect's P0-11: the presence check imports them at load).
CONTROLS_HELPERS = ("scripts/tachi_parts.py", "scripts/tachi_scoring.py", "scripts/tachi_scoring_rules.py",
                    "scripts/sarif_common.py", "scripts/tachi_parsers.py")
# The names the agent's batch input holds under ``refs``. The command passes what the planner needs to fill them: the scored
# input (--risk-scores), the target, the architecture candidate and the baseline, and the planner reaches the threat model
# through the scored input's source_file.
CONTROLS_REFS = {"risk_scores", "threats", "target", "architecture", "baseline_dir"}
# ADR-050 D7, the W3 ruling: both scored-stage agents find the architecture description by one rule, the file that `refs` names or else
# the run's snapshot beside the threat model. The clause is the scorer's, and the control analyzer carries it word for word.
ARCHITECTURE_READ_RULE = ("the file that `refs` names under `architecture`, or else an `architecture.md` "
                          "in the same directory as the `threats` file")
CONTROLS_SARIF_TEMPLATE = "templates/tachi/output-schemas/compensating-controls.sarif"


def shipped_or_wired_by_t039() -> Set[str]:
    """The manifest's scripts, plus the controls renderer while it is neither in the manifest nor in the tree."""
    return shipped_scripts() | {name for name in WIRED_BY_T039 if not (REPO_ROOT / name).exists()}


# --- /tachi.compensating-controls (T038) ----------------------------------------------------------


def test_controls_runs_only_the_shipped_scripts_it_names_and_each_fence_is_one_python3_call():
    text = text_of(CONTROLS_COMMAND)
    allowed = shipped_or_wired_by_t039()
    assert calls(text) == CONTROLS_CALLS
    for fence in fences(text):
        if fence.label.lower() in SHELL_LABELS:
            assert not command_problems(fence.body, allowed), fence.body
    named = set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", text))
    assert named <= allowed, "the command names a script that isn't shipped: %s" % sorted(named - allowed)
    assert named == {"scripts/tachi-stage.py", "scripts/render-compensating-controls.py"} | set(CONTROLS_HELPERS)
    assert directive_hits(text) == []
    assert "It writes no script of its own, and it stops on a failure rather than working around it." in text


def test_controls_step_0_adds_the_flags_and_no_date_flag():
    text = text_of(CONTROLS_COMMAND)
    step = step_of(text, "## Step 0:", CONTROLS_COMMAND)
    for flag in ("--target <path>", "--output-dir <path>", "--baseline <run-dir>", "--architecture-path <path>"):
        assert flag in step, flag
    assert "--date" not in step, "the command exposes no --date flag (PM-T5)"
    assert text.count("--date") == 1, "the one --date is the planner's, and the command computes the date once"
    plan = step_of(text, "## Step 2:", CONTROLS_COMMAND)
    assert "Set `analysis_date` to today's date" in plan
    assert "the plan's date" in plan, "a resumed run uses the plan's date"


def test_controls_plans_once_with_the_command_date_the_scored_input_and_the_target():
    step = step_of(text_of(CONTROLS_COMMAND), "## Step 2:", CONTROLS_COMMAND)
    assert calls(step) == [CONTROLS_CALLS[1]]
    assert "`--baseline-dir '{baseline_dir}'`" in step and "`--architecture '{architecture_flag}'`" in step
    assert "and only then" in step and "a per-run snapshot must never stand in for it" in step
    assert "`plan` reads `risk-scores.sarif` when `risk-scores.md` is absent" in step, "AR-T2: the SARIF fallback is the planner's"
    assert "Pass no threat model path" in step and "`source_file`" in step and "--threats" not in step
    # every flag the command passes is one the planner takes, and the stage is one it plans
    source = STAGE_SCRIPT.read_text(encoding="utf-8")
    for flag in ("--stage", "--out", "--date", "--risk-scores", "--target", "--baseline-dir", "--architecture"):
        assert 'plan.add_argument("%s"' % flag in source, flag
    assert "compensating-controls" in tachi_parts.STAGE_AGENTS


def test_controls_looks_for_no_architecture_file_of_its_own_and_names_the_agents_snapshot_fallback():
    text = text_of(CONTROLS_COMMAND)
    step = step_of(text, "## Step 1:", CONTROLS_COMMAND)
    # D7: the SARIF URI comes from the flag alone (the Step 2 assertions above), so the command finds no file of its own ...
    assert "it looks for no `architecture.md` of its own" in step and "a per-run snapshot must never stand in for it" in step
    # ... and with no flag the agent reads the snapshot, as the scorer's agent does (the W3 ruling, B)
    assert ("With none, the agent reads the run's snapshot, an `architecture.md` beside the threat model, as the scorer's agent does, "
            "and maps components by heuristic discovery only when there is none either.") in step
    assert "they map components to files by heuristic discovery" not in text, "the old line gave the agent no snapshot to read"


def test_controls_installed_files_check_names_the_helpers_so_a_missing_one_is_not_a_missing_python():
    step = step_of(text_of(CONTROLS_COMMAND), "## Step 1:", CONTROLS_COMMAND)
    first = step.split("2. **Check Python")[0]
    for name in ("`.claude/agents/tachi/control-analyzer.md`", "`scripts/tachi-stage.py`", "`scripts/render-compensating-controls.py`"):
        assert name in first, name
    for helper in CONTROLS_HELPERS:
        assert "`%s`" % helper in first, helper
        assert helper in shipped_scripts(), "%s is not in the manifest" % helper
    assert "Re-run the installer from this project's root: <tachi-repo>/scripts/install.sh" in first


@pytest.mark.parametrize("anchor, script", [("## Step 2:", "plan"), ("## Step 4:", "reconcile"), ("## Step 5:", "render")])
def test_controls_routes_every_exit_code_of_each_script(anchor, script):
    table = routes(text_of(CONTROLS_COMMAND), anchor, CONTROLS_COMMAND)
    assert set(table) == SCRIPT_EXITS[script], "%s routes %s, and the script returns %s" % (anchor, sorted(table), sorted(SCRIPT_EXITS[script]))


def test_controls_routing_follows_the_exit_table():
    text = text_of(CONTROLS_COMMAND)
    plan = routes(text, "## Step 2:", CONTROLS_COMMAND)
    assert plan["0"] == "Go to Step 3" and plan["1"].startswith("Stop and print the error")
    assert plan["2"].startswith("Stop and print the error") and "nothing to fail" in plan["2"], "2 runs fail only once a plan exists"
    reconcile = routes(text, "## Step 4:", CONTROLS_COMMAND)
    assert reconcile["0"] == "Go to Step 5"
    assert reconcile["3"].startswith("Dispatch exactly the batches `waves` lists") and "while the exit code is 3" in reconcile["3"]
    assert reconcile["4"] == "Go to Step F with `--reason unrecoverable-batch`"
    assert reconcile["2"] == "Go to Step F with `--reason check-failed`"
    assert reconcile["1"] == "Stop and print the error"
    render = routes(text, "## Step 5:", CONTROLS_COMMAND)
    assert render["0"] == "Success. Go to Step 6"
    assert render["5"].startswith("Success with warnings. Print the warnings")
    assert render["4"] == "A completeness or parity check failed. Go to Step F with `--reason check-failed`"
    assert render["anything else"] == "Go to Step F with `--reason render-failed`"


def test_controls_dispatches_the_typed_agent_with_the_fixed_prompt_and_waits_for_completion():
    text = text_of(CONTROLS_COMMAND)
    step = step_of(text, "## Step 3:", CONTROLS_COMMAND)
    prompts = [f.body for f in fences(step) if "Read and follow" in f.body]
    assert prompts == [the_fixed_prompt()], "the dispatch prompt is the part contract's one fixed line, and nothing else"
    assert "`subagent_type` set to `tachi-control-analyzer`" in step
    assert "tachi-control-analyzer" in roster_names()
    assert tachi_parts.STAGE_AGENTS["compensating-controls"] == "tachi-control-analyzer"
    assert named_tachi_tokens(text) <= roster_names() | skill_directories()
    assert COMPLETION_RULE in step, "ADR-050 D6's completion rule, word for word"
    assert "foreground" not in text.lower(), "the Agent tool has no foreground option"
    assert "Never send more than 16 in one message" in step and "at most 16 batches each" in step_of(text, "## Step 2:", CONTROLS_COMMAND)
    assert "end the run there" in step and "Run no substitute" in step
    assert "`--reason agent-not-spawned` and `--detail tachi-control-analyzer`" in step
    # the old prompt, which handed the agent the whole pipeline, the paths and the output files, is gone
    for gone in ("Analyze scored threat findings against the target codebase", "Execute your complete 6-phase analysis pipeline",
                 "Input format:", "Analysis date:", "Output directory:", "Write output files", "Read the input file yourself"):
        assert gone not in text, gone


def test_controls_step_f_runs_fail_with_one_of_the_scripts_reasons_and_never_twice():
    text = text_of(CONTROLS_COMMAND)
    step = step_of(text, "## Step F:", CONTROLS_COMMAND)
    assert calls(step) == [CONTROLS_CALLS[4]]
    reasons = stage_reasons()
    assert reasons == {"agent-not-spawned", "unrecoverable-batch", "check-failed", "render-failed"}
    named = set(re.findall(r"`(--reason )?(agent-not-spawned|unrecoverable-batch|check-failed|render-failed)`", step))
    assert {reason for _, reason in named} == reasons, "Step F names every reason, and the routing above uses only these"
    used = set(re.findall(r"--reason ([a-z-]+)`", text))
    assert used <= reasons, "a step sends Step F a reason the script doesn't have: %s" % sorted(used - reasons)
    assert "For `agent-not-spawned`, add `--detail tachi-control-analyzer`" in step, "AR-T5: Step F covers a spawn failure"
    assert "`fail` never runs a second time" in step and "Whatever `fail` exits with, stop there" in step
    assert "`TACHI COMPENSATING-CONTROLS FAILED`" in step


def test_controls_reports_the_renderers_summary_and_restates_no_number():
    text = text_of(CONTROLS_COMMAND)
    step = step_of(text, "## Step 6:", CONTROLS_COMMAND)
    assert "exactly as it wrote them" in step and "Restate no number" in step
    assert "with category `%s`" % sc.UPLOAD_CATEGORIES["compensating-controls.sarif"] in step
    for gone in ("COMPENSATING CONTROLS ANALYSIS COMPLETE", "{found_count}", "{risk_reduction_pct}", "{count}", "Residual Severity Distribution",
                 "Highest-Risk Unmitigated: {id}", "(supersedes risk-scores.sarif)", "preserved fingerprints"):
        assert gone not in text, "the model-composed summary and its stale claim are gone: %s" % gone


# --- the control analyzer's spec (T037) -----------------------------------------------------------


def test_the_control_analyzer_loads_the_part_contract_and_states_its_check_in_the_references_words():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    assert "**MANDATORY**: Read `%s` before you write anything" % PART_CONTRACT in spec
    assert check_statement(spec) == check_statement(text_of(PART_CONTRACT))
    assert text_of(SARIF_IDENTITY).count("**You never write SARIF.**") == 1 and SARIF_IDENTITY in spec


def test_every_slot_the_control_analyzer_names_is_a_slot_of_its_stage():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    tokens = set(re.findall(r"\{\{[^{}]*\}\}", spec)) - {"{{kind:arg}}"}
    assert len(tokens) >= 7, tokens
    for token in sorted(tokens):
        assert tachi_parts.narrative_problem(token, "compensating-controls") is None, token


def test_the_control_analyzers_example_part_is_accepted_by_the_validator_with_no_flag():
    blocks = [f.body for f in fences(text_of(CONTROL_ANALYZER_SPEC)) if f.label == "json"]
    assert len(blocks) == 1, "the spec carries one example part"
    part = json.loads(blocks[0])
    assert part["stage"] == "compensating-controls" and part["agent_type"] == "tachi-control-analyzer"
    result = tachi_parts.classify_part(part, part["plan_id"], part["batch_id"], "compensating-controls", part["agent_type"], part["finding_ids"])
    assert result.state == "done" and result.flags == {}, (result.state, result.detail, result.flags)
    for item in part["items"]:
        row = item["matrix_row"]
        assert len(row.strip().strip("|").split("|")) == 11, "Section 2's row has the K8 schema's 11 cells"
        for slot in ("{{score:inherent}}", "{{band:inherent}}", "{{score:residual}}", "{{band:residual}}"):
            assert row.count(slot) == 1, slot
        body = item["recommendation_body"]
        assert re.findall(r"\*\*([A-Za-z ]+)\*\*:", body) == ["What to Implement", "Where to Implement", "Reference Patterns", "Effort Estimate"]
        assert re.search(r"\*\*Effort Estimate\*\*: (Low|Medium|High)\b", body)


def test_the_control_analyzer_is_judgment_only_and_authors_no_output_file():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    assert spec.count(NO_HAND_BACK) == 1
    for gone in ("Risk score content", "String (file content)", "Processing Capacity", "Result count matches", "Coverage Matrix entries MUST equal",
                 "append peer references", "Preserve ALL", "semanticVersion", "re-hash", "halt with", "{output_directory}"):
        assert gone not in spec, "the control analyzer spec still carries %r" % gone
    for kept in ("`tachi.part/1`", "`tachi.overflow/1`", "`part_path`", "`recommendation_body`", "`matrix_row`"):
        assert kept in spec, kept
    names = set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.py", spec))
    assert names == {"scripts/render-compensating-controls.py", "scripts/sarif_common.py"}, sorted(names)
    assert names <= shipped_or_wired_by_t039(), sorted(names - shipped_or_wired_by_t039())


def test_the_control_analyzer_names_each_sarif_tool_with_r_33_s_case_and_states_the_count_rule_once_per_place():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    for name in sc.TOOL_NAMES.values():
        assert "`%s`" % name in spec, name
    assert "`tachi`" not in spec, "R-33: the threats tool has a capital T"
    # D-6(a)'s three controls sentences and D8's peer line, each reworded once to the open-findings rule
    assert spec.count("one entry for each open finding") == 1          # was :345, Phase 6
    assert spec.count("Each result is one open finding") == 1           # was :394, 6c check 5
    assert spec.count("both files count the same open findings") == 1  # was :402, 6d check 1
    assert spec.count("A correlated peer is a result of its own") == 1  # was :383, D8's peer-reference line
    for old in ("Result count matches", "Coverage Matrix entries MUST equal", "append peer references", "finding count"):
        assert old not in spec, old


def test_the_control_analyzer_resolves_a_category_for_every_prefix_as_the_code_does():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    assert "`category_for_prefix`" in spec and "all 12 prefixes" in spec
    resolved: Dict[str, str] = {}
    for prefixes, category in re.findall(r"((?:`[A-Z]+-N`(?:, | and )?)+) -> `([a-z-]+)`", spec):
        for prefix in re.findall(r"[A-Z]+(?=-N)", prefixes):
            resolved[prefix] = category
    assert resolved == tachi_scoring.PREFIX_CATEGORY


def test_the_control_analyzer_reads_the_refs_names_that_the_commands_plan_fills():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    assert CONTROLS_REFS == {"risk_scores", "threats", "target", "architecture", "baseline_dir"}, \
        "the W3 ruling: the snapshot is found from refs.threats, so it is no sixth refs name"
    assert set(re.findall(r"`refs\.([a-z_]+)`", spec)) == CONTROLS_REFS
    plan = calls(step_of(text_of(CONTROLS_COMMAND), "## Step 2:", CONTROLS_COMMAND))[0]
    assert "--risk-scores '{input_dir}/risk-scores.md'" in plan and "--target '{target_path}'" in plan, "refs.risk_scores and refs.target"
    # the controls item's key set is closed, and no value that the renderer computes has a key in it
    keys = set(tachi_parts.KEY_SETS["controls-item"][0]) | set(tachi_parts.KEY_SETS["controls-item"][1])
    for computed in ("reduction_factor", "residual_score", "residual_severity_band", "control_effectiveness", "rescan_scope"):
        assert computed not in keys, computed


def test_both_scored_stage_agents_find_the_architecture_by_the_one_rule():
    for path in (RISK_SCORER_SPEC, CONTROL_ANALYZER_SPEC):
        assert ARCHITECTURE_READ_RULE in text_of(path), "%s: the clause is the scorer's, in both specs, word for word" % path
    # in the control analyzer's Input Boundary the clause is the Architecture row's type, and the row says what the snapshot is
    optional = table_after(text_of(CONTROL_ANALYZER_SPEC), "### Optional Inputs", where=CONTROL_ANALYZER_SPEC)
    rows = [row for row in optional.rows if row[0] == "Architecture description"]
    assert len(rows) == 1, "the Optional Inputs table has one Architecture description row"
    assert ARCHITECTURE_READ_RULE in rows[0][1] and rows[0][1].endswith("; or none")
    assert "the run's snapshot, the copy the findings came from" in rows[0][2]


def test_the_control_analyzer_reads_an_absent_snapshot_as_heuristic_discovery_and_never_as_no_part():
    spec = text_of(CONTROL_ANALYZER_SPEC)
    validation = section_text(spec, "### Input Validation", where=CONTROL_ANALYZER_SPEC)
    assert "The snapshot is optional." in validation
    assert ("When the `threats` file's directory holds no `architecture.md`, when it can't be read, or when `refs` names no `threats` file, "
            "use heuristic discovery, and never write no part over it.") in validation
    # the "write no part" rule is for a path in `refs`, and the snapshot sentence that limits it follows it, in the same paragraph
    assert validation.index("write no part and name the path") < validation.index("The snapshot is optional.")
    phase_2 = section_text(spec, "## Phase 2: Discover Codebase", where=CONTROL_ANALYZER_SPEC)
    assert "When you have an architecture description, from `refs` or the snapshot:" in phase_2
    assert "When you have none, or for unresolved components, apply directory-based heuristics:" in phase_2
    # the snapshot is third-party text like every file the agent reads, and the one input that nothing has checked
    assert "every file that `refs` names, the architecture snapshot and every file you read in the target codebase hold third-party text" in spec
    assert "The one exception is the architecture snapshot" in section_text(spec, "## Input Boundary", where=CONTROL_ANALYZER_SPEC)


# --- the controls references (T038) -----------------------------------------------------------------


def test_residual_risk_documents_the_renderers_factors_formula_and_bands_as_the_code_has_them():
    text = text_of(CONTROLS_REFERENCES + "/residual-risk.md")
    where = "residual-risk.md"
    factors = {strip_ticks(row[0]): Decimal(row[1]) for row in table_after(text, "### Reduction Factor Assignment", where=where).rows}
    assert factors == tachi_scoring.REDUCTION_FACTOR_P0
    examples = table_after(text, "**Worked examples**:", where=where).rows
    assert len(examples) == 4
    for threat, composite, status, factor, _calculation, residual in examples:
        assert tachi_scoring.REDUCTION_FACTOR_P0[status] == Decimal(factor), threat
        assert tachi_scoring.residual_score(Decimal(composite), Decimal(factor)) == Decimal(residual), threat
    assert ("9.1", "found", "0.50", "4.6") in {(row[1], row[2], row[3], row[5]) for row in examples}, "the 4.55 example stays, and half up gives 4.6"
    minimums = {}
    for cell, spread in table_after(text, "### Residual Severity Band Mapping", where=where).rows:
        band = cell.strip("*")
        if band != "Low":
            minimums[band] = Decimal(re.search(r"[0-9]+\.[0-9]", spread).group(0))
    assert minimums == {band: rule["min"] for band, rule in tachi_scoring.SEVERITY_BANDS.items() if band != "Low"}
    for fact in ("**The renderer's section.**", "`scripts/render-compensating-controls.py`", "`tachi_scoring.residual_score`", "`tachi_scoring.q1`",
                 "half up", "never uses Python's `round()`", "no step corrects a factor", "`tachi_scoring.reduction_percentage`",
                 "`tachi_scoring.largest_remainder`"):
        assert fact in text, fact
    for gone in ("halt with", "emit a warning", "Processing order", "Clamp the result", "single paragraph"):
        assert gone not in text, "the reference still tells the agent to %r" % gone


def test_the_summary_example_in_residual_risk_has_counts_that_agree_with_each_other():
    block = next(f.body for f in fences(text_of(CONTROLS_REFERENCES + "/residual-risk.md")) if "residual_risk_summary" in f.body)
    data: Dict[str, Dict[str, int]] = {}
    section = ""
    for line in block.splitlines()[1:]:
        match = re.match(r"^( +)([a-z_]+):\s*(\S*)$", line)
        assert match, line
        indent, key, value = match.groups()
        if value == "":
            section = key
            data[section] = {}
        elif len(indent) == 4:
            data[section][key] = int(value)
    inherent, residual, shifts = data["inherent_distribution"], data["residual_distribution"], data["severity_shifts"]
    assert sum(inherent.values()) == sum(residual.values())
    assert shifts["total_shifts"] == sum(value for key, value in shifts.items() if key != "total_shifts")
    moved_out = {band: sum(v for k, v in shifts.items() if k.startswith(band + "_to_")) for band in ("critical", "high", "medium")}
    moved_in = {band: sum(v for k, v in shifts.items() if k.endswith("_to_" + band)) for band in ("high", "medium", "low")}
    for band in ("critical", "high", "medium", "low"):
        assert residual[band] == inherent[band] - moved_out.get(band, 0) + moved_in.get(band, 0), band


def test_the_recommendation_templates_follow_the_four_key_body_the_part_contract_validates():
    templates = [f.body for f in fences(text_of(CONTROLS_REFERENCES + "/residual-risk.md")) if f.body.startswith("**What to Implement**:")]
    assert len(templates) == 2, "one template for a missing control and one for a partial control"
    for body in templates:
        assert re.findall(r"^\*\*([A-Za-z ]+)\*\*:", body, re.MULTILINE) == ["What to Implement", "Where to Implement", "Reference Patterns",
                                                                              "Effort Estimate"]
        assert len(body) <= 2000


def test_evidence_criteria_gives_the_renderer_the_factors_and_the_p0_effectiveness():
    text = text_of(CONTROLS_REFERENCES + "/evidence-criteria.md")
    factors = re.findall(r"Reduction factor \(the renderer's, P0 binary\): \*\*([0-9.]+)\*\*", text)
    assert [Decimal(factor) for factor in factors] == [tachi_scoring.REDUCTION_FACTOR_P0[status] for status in ("found", "partial", "missing")]
    note = section_text(text, "### P0 Effectiveness Note", where="evidence-criteria.md")
    assert 'the renderer derives `control_effectiveness` from `control_status` (found -> "strong", partial -> "moderate", missing -> "none")' in note
    assert "You never write it" in note
    for gone in ("halt with", "Detailed effectiveness assessment available in P1", "conforming to the `control_evidence` item schema"):
        assert gone not in text, gone


def test_control_categories_names_the_closed_enum_and_the_prefix_resolution_as_the_code_has_them():
    text = text_of(CONTROLS_REFERENCES + "/control-categories.md")
    slugs = set(re.findall(r"^### Category [0-9]+: .+ \(`([a-z-]+)`\)$", text, re.MULTILINE))
    assert slugs == set(tachi_parts.CONTROL_CATEGORIES) and len(slugs) == 8
    sentence = re.search(r"`S`, `T`, `R`, `I`, `D` and `E` to the six STRIDE categories, (.+?) to Agentic, and (.+?) to LLM\.", text)
    assert sentence, "the reference states the prefix resolution"
    by_category: Dict[str, Set[str]] = {}
    for prefix, category in tachi_scoring.PREFIX_CATEGORY.items():
        by_category.setdefault(category, set()).add(prefix)
    assert set(re.findall(r"`([A-Z]+)`", sentence.group(1))) == by_category["agentic"]
    assert set(re.findall(r"`([A-Z]+)`", sentence.group(2))) == by_category["llm"]
    assert {"S", "T", "R", "I", "D", "E"} == set(tachi_scoring.PREFIX_CATEGORY) - by_category["agentic"] - by_category["llm"]
    assert "`tachi_scoring.category_for_prefix`" in text and "all 12 prefixes" in text


@pytest.mark.parametrize("name", ["residual-risk.md", "evidence-criteria.md", "control-categories.md"])
def test_every_tachi_scoring_name_that_a_controls_reference_cites_exists(name):
    text = text_of(CONTROLS_REFERENCES + "/" + name)
    assert "scripts/render-compensating-controls.py" in text, "the reference says who computes what"
    for member in set(re.findall(r"`tachi_scoring\.([A-Za-z_0-9]+)`", text)):
        assert hasattr(tachi_scoring, member), "%s cites tachi_scoring.%s, which doesn't exist" % (name, member)


# --- the installed SARIF guide (FR-K8.3) -------------------------------------------------------------


def test_the_sarif_guide_no_longer_tells_an_agent_to_author_a_file_that_a_renderer_owns():
    text = text_of(SARIF_GENERATION_GUIDE)
    status = text.split("### SARIF Output Generation")[0]
    assert "no longer tells any agent to author `risk-scores.sarif` or `compensating-controls.sarif`" in status
    assert "you write no SARIF" in status and SARIF_IDENTITY in status
    assert "scripts/render-risk-scores.py" in status and "scripts/render-compensating-controls.py" in status
    assert "### Renderer-Owned SARIF Files" in text and "### Risk Scoring SARIF Extension" not in text
    for gone in ("MUST preserve", "is designed to supersede", "Fingerprint Preservation Rules", "The risk-scorer does not modify, add, or remove taxonomy data"):
        assert gone not in text, gone
    owned = text.split("### Renderer-Owned SARIF Files")[1]
    assert "No agent authors either file" in owned
    assert not re.search(r"\b(Set|Populate|Map|Create|Write|Produce|Generate)\b[^.\n]*\b(risk-scores|compensating-controls)\.sarif", owned), \
        "the renderer-owned section has no authoring instruction"


def test_the_sarif_guide_corrects_the_supersession_claim_under_r_33():
    text = text_of(SARIF_GENERATION_GUIDE)
    claim = section_text(text, "#### SARIF Supersession", where=SARIF_GENERATION_GUIDE)
    assert claim.strip().startswith("No SARIF file supersedes another")
    assert "different tool names" in claim and "different categories" in claim
    assert "`risk-scores.sarif` does not supersede `threats.sarif`" in claim
    assert "`compensating-controls.sarif` does not supersede `risk-scores.sarif`" in claim
    # the three tools and categories are the emitter's
    table = table_after(text, "#### Tool Metadata Differences", where=SARIF_GENERATION_GUIDE)
    files = ("threats.sarif", "risk-scores.sarif", "compensating-controls.sarif")
    names = next(row for row in table.rows if row[0] == "`tool.driver.name`")
    assert [strip_ticks(cell).strip('"') for cell in names[1:]] == [sc.TOOL_NAMES[name] for name in files]
    categories = next(row for row in table.rows if row[0].startswith("Recommended upload"))
    assert [strip_ticks(cell) for cell in categories[1:]] == [sc.UPLOAD_CATEGORIES[name] for name in files]
    assert sc.TOOL_NAMES["threats.sarif"] == "Tachi", "R-33: the threats tool has a capital T"


def test_the_sarif_guide_documents_what_the_renderers_write():
    text = text_of(SARIF_GENERATION_GUIDE)
    where = SARIF_GENERATION_GUIDE
    # the scorer's property bag is the template's, key for key and in order (the renderer writes it)
    section = section_text(text, "#### Extended Property Bag Schema", where=where, keep_fences=True)
    documented = list(json.loads(next(f.body for f in fences(section) if f.label == "json"))["properties"])
    template = json.loads(text_of(RISK_SCORES_SARIF_TEMPLATE))
    plain_results = [r["properties"] for r in template["runs"][0]["results"] if "correlation-group" not in r["properties"]]
    assert documented == list(plain_results[0])
    # the message is written whole, and the layer is a property of every result (P0-8; the PM's ruling on maestro-layer)
    assert "the renderer always writes `markdown` beside it, the empty string included" in section_text(text, "#### The Result Message", where=where)
    assert "`maestro-layer`" in section and "`integrity-flags`" in section
    # identity: tachi's own hash, two fingerprint keys, no copy from upstream
    identity = section_text(text, "#### Identity and Membership", where=where)
    assert 'sha256("tachi-plh/1|" + tool + "|" + id)' in identity and "exactly two keys" in identity and "never in `partialFingerprints`" in identity
    assert "Neither renderer-owned file copies a fingerprint from an upstream file" in identity


def test_the_sarif_guide_lists_the_result_properties_of_the_controls_template_and_no_others():
    text = text_of(SARIF_GENERATION_GUIDE)
    section = section_text(text, "#### Extended Property Bag Schema", where=SARIF_GENERATION_GUIDE, keep_fences=True)
    template = json.loads(text_of(CONTROLS_SARIF_TEMPLATE))
    results = [r["properties"] for r in template["runs"][0]["results"]]
    plain = [list(p) for p in results if "correlation-group" not in p]
    members = [list(p) for p in results if "correlation-group" in p]
    assert plain and members and all(keys == plain[0] for keys in plain), "the template's plain results share one property order"
    # the one sentence that lists the control properties: `security-severity` is the semantic-shift table's, the rest are listed here
    paragraphs = [p for p in section.split("\n\n") if p.startswith("`compensating-controls.sarif` carries the same `maestro-layer`")]
    assert len(paragraphs) == 1, "the property bag has one paragraph for the controls file"
    listed = set(ticks(paragraphs[0].split(". ")[0])) - {"compensating-controls.sarif", "kind:field:cause"}
    assert listed == set(plain[0]) - {"security-severity"}, (sorted(listed), plain[0])
    assert "`security-severity`" in text and "Per-finding residual score" in text
    # the correlation keys are the identity section's, as the scorer's are
    identity = section_text(text, "#### Identity and Membership", where=SARIF_GENERATION_GUIDE)
    for key in set(members[0]) - set(plain[0]):
        assert "`%s`" % key in identity, key
