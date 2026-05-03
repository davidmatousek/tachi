"""Command dispatch tests for the ``tachi.infographic`` command file.

Verifies that ``.claude/commands/tachi.infographic.md`` registers the new
``executive-architecture`` template in the two user-reachable places: the
``all`` shorthand expansion, and the short ``exec`` alias (matching the
existing alias convention: ``corporate-white`` → ``baseball-card``,
``maestro`` → maestro pair).

These are file-content assertions — the command file is hand-authored
markdown with prose, YAML-ish fragments, and bullet lists, and a full AST
parse would be brittle. Simple substring checks verify the user-facing
contract without coupling to formatting.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_FILE = REPO_ROOT / ".claude" / "commands" / "tachi.infographic.md"


def _read_command_file() -> str:
    """Read the infographic command file. Fails loudly if missing."""
    assert COMMAND_FILE.exists(), (
        f"Command file not found: {COMMAND_FILE}. This test asserts content, "
        f"not existence — the file must be present in the checked-out tree."
    )
    return COMMAND_FILE.read_text(encoding="utf-8")


def test_all_shorthand_includes_executive_architecture() -> None:
    """The ``all`` shorthand must expand to include ``executive-architecture``.

    The command file describes the ``all`` shorthand expansion in two places:

    * Step 0 parse list (around line 17) — the catalog of valid ``--template``
      values
    * Step 2 agent prompt (around line 163) — the explicit expansion rule
      that tells the agent which templates to loop over when ``template ==
      "all"``

    We assert that the expansion rule (Step 2) lists ``executive-architecture``
    as one of the templates ``all`` expands to. This is the load-bearing check
    — if the expansion rule omits the template, users running the default
    command never see the executive infographic even though it exists.

    Strategy: find the ``"all" expands to`` block and assert
    ``executive-architecture`` appears inside it. We use a regex to isolate
    the expansion sentence so we don't get a false pass from an unrelated
    mention elsewhere in the file.
    """
    content = _read_command_file()

    # Locate the expansion sentence so we only assert membership against the
    # expansion text, not any unrelated mention elsewhere in the file.
    match = re.search(
        r'"all"\s+expands\s+to:\s*([^\n]+)',
        content,
        re.IGNORECASE,
    )
    assert match is not None, (
        "Could not find the `\"all\" expands to:` expansion block in "
        f"{COMMAND_FILE}. The command file may have been restructured — "
        "update this test's regex to match the new format."
    )

    expansion_text = match.group(1)
    assert "executive-architecture" in expansion_text, (
        "`all` shorthand expansion does not include `executive-architecture`. "
        f"Found expansion: {expansion_text!r}. "
        "Expected `executive-architecture` to be listed alongside "
        "baseball-card, system-architecture, and risk-funnel so that "
        "`/tachi.infographic` (default template=all) generates the executive "
        "infographic. Fix in .claude/commands/tachi.infographic.md Step 2."
    )


def test_exec_alias_dispatches_to_executive_architecture() -> None:
    """The ``exec`` alias must map to ``executive-architecture``.

    Accepts any format: a dedicated resolution rule, a one-line mapping, or an
    entry in an Aliases line. The test asserts (1) ``exec`` appears as a standalone
    token and (2) at least one line containing standalone ``exec`` also mentions
    ``executive-architecture``, proving the mapping is explicit.
    """
    content = _read_command_file()

    # Negative lookahead so `exec` inside `executive-architecture` does not match.
    standalone_exec_pattern = re.compile(r"\bexec\b(?!utive-architecture)")

    matching_lines: list[str] = []
    for line in content.splitlines():
        if standalone_exec_pattern.search(line):
            matching_lines.append(line)

    assert matching_lines, (
        "No standalone `exec` token found in "
        f"{COMMAND_FILE}. Document `exec` as an alias for "
        "`executive-architecture` following the `corporate-white → "
        "baseball-card` precedent."
    )

    lines_with_mapping = [
        line for line in matching_lines if "executive-architecture" in line
    ]
    assert lines_with_mapping, (
        "Found `exec` token(s) in the command file but none appear on a "
        "line that also mentions `executive-architecture`. The alias "
        "mapping must be explicit — e.g. `If value is `exec`: resolve alias "
        "to `executive-architecture`` — so users and agents can trace the "
        f"dispatch. Lines with standalone `exec`: {matching_lines!r}."
    )
