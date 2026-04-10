"""F-128 command dispatch tests (T026) — US-3 file-content assertions.

This module implements task T026 for feature 128-prd-128-executive (Wave 5,
US-3). It verifies that ``.claude/commands/tachi.infographic.md`` registers
the new ``executive-architecture`` template in two places the user can reach:

1. The ``all`` shorthand expansion — running ``/tachi.infographic`` with no
   ``--template`` flag (or ``--template all``) must generate the executive
   architecture infographic alongside the other templates.
2. The ``exec`` alias — a short alias mapping to ``executive-architecture``
   so users can type ``/tachi.infographic --template exec`` instead of the
   full template name. This matches the existing alias convention
   (``corporate-white`` → ``baseball-card``, ``maestro`` → maestro pair).

These are **file-content assertions**, not script invocations. They open the
command markdown file and assert string presence. They will initially FAIL
until T027 lands the corresponding command file edits. T028 is the gate
check that re-runs these tests after T027 has shipped.

Why file-content tests instead of parsing?
------------------------------------------
The command file is hand-authored markdown with prose, YAML-ish fragments,
and bullet lists. A full markdown AST parse would be brittle and misleading
— the user-facing contract is "the template appears in the ``all``
expansion list and the ``exec`` alias is documented". Simple substring
checks verify exactly that contract without coupling to formatting.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMAND_FILE = REPO_ROOT / ".claude" / "commands" / "tachi.infographic.md"


def _read_command_file() -> str:
    """Read the infographic command file. Fails loudly if missing."""
    assert COMMAND_FILE.exists(), (
        f"Command file not found: {COMMAND_FILE}. T026 expects the existing "
        f"tachi.infographic command to be present — this test asserts content, "
        f"not existence."
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

    # Locate the "all expands to" expansion block. The current file uses the
    # phrase: `"all" expands to: baseball-card, system-architecture, risk-funnel.`
    # T027 will add `executive-architecture` to that list. Capture the full
    # sentence (up to the next period or newline-bullet) so we can assert
    # membership against only the expansion text.
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
        "infographic. Fix in .claude/commands/tachi.infographic.md Step 2 "
        "template expansion rules (T027)."
    )


def test_exec_alias_dispatches_to_executive_architecture() -> None:
    """The ``exec`` alias must map to ``executive-architecture``.

    The existing command file documents aliases two ways:

    * In the Step 0 valid-values list (``corporate-white`` appears alongside
      the canonical template names)
    * In the Step 0 resolution rule (``If value is `corporate-white`: resolve
      alias to `baseball-card```)

    T027 should add ``exec`` following the same convention. This test does
    not mandate a specific format — it accepts any of:

    * ``exec`` listed in the valid values enumeration AND a resolution rule
      ``If value is `exec`: resolve alias to `executive-architecture```
    * A one-line alias mapping like ``exec → executive-architecture``
    * An entry in a dedicated Aliases line (``Aliases: corporate-white →
      baseball-card, exec → executive-architecture, ...``)

    The test asserts two things:

    1. The token ``exec`` appears somewhere in the file as a standalone word
       (not as a substring of ``executive-architecture``)
    2. That standalone ``exec`` reference appears on a line that also
       mentions ``executive-architecture`` — this proves the mapping is
       explicit, not accidental
    """
    content = _read_command_file()

    # Find every line in the file that mentions `exec` as a standalone
    # identifier. We strip out occurrences that are just substrings of
    # `executive-architecture` by using a negative lookahead — `exec` must
    # NOT be followed by `utive-architecture`.
    standalone_exec_pattern = re.compile(r"\bexec\b(?!utive-architecture)")

    matching_lines: list[str] = []
    for line in content.splitlines():
        if standalone_exec_pattern.search(line):
            matching_lines.append(line)

    assert matching_lines, (
        "No standalone `exec` token found in "
        f"{COMMAND_FILE}. T027 must document `exec` as an alias for "
        "`executive-architecture` — add it to the Step 0 valid values list "
        "AND the alias resolution rule, following the `corporate-white → "
        "baseball-card` precedent."
    )

    # At least one of those lines must also mention `executive-architecture`
    # — that is the explicit mapping that proves `exec` is an alias.
    lines_with_mapping = [
        line for line in matching_lines if "executive-architecture" in line
    ]
    assert lines_with_mapping, (
        "Found `exec` token(s) in the command file but none appear on a "
        "line that also mentions `executive-architecture`. The alias "
        "mapping must be explicit — e.g. `If value is `exec`: resolve alias "
        "to `executive-architecture`` — so users and agents can trace the "
        f"dispatch. Lines with standalone `exec`: {matching_lines!r}. "
        "Fix in .claude/commands/tachi.infographic.md Step 0 alias "
        "resolution rules (T027)."
    )
