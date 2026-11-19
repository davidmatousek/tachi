#!/usr/bin/env python3
"""stamp-tachi-version.py -- stamp ``tachi_version`` into a threats.md frontmatter (Feature 391, Part B2).

/tachi.threat-model runs this as its Step 2.6, after threats.md is written and
the Step 2.5 populator re-assert is done. It records which tachi release wrote
the file, copied from the one-line marker the installer leaves at
``templates/tachi/VERSION``. The model never writes this field: the script is
its only writer, so the value is deterministic and a second run changes nothing.

Usage::

    python3 scripts/stamp-tachi-version.py --threats PATH
        [--marker templates/tachi/VERSION] [--check] [--json]

What it does to ``--threats``, in place:

* Writes ``tachi_version: "<value>"`` on the line right after ``schema_version:``
  in the YAML frontmatter, or at the end of the frontmatter when there is no
  ``schema_version:``. A ``tachi_version:`` line that is already there is
  updated where it stands, and any duplicate of it is dropped.
* Finds the frontmatter in either shape ``tachi_parsers`` reads: a ``---`` block
  at the top of the file, or a ``---`` block inside a ``yaml`` code fence.
* Leaves every other byte alone: line endings (LF or CRLF), a missing final
  newline and the whole body after the frontmatter. A file that already carries
  the stamp is not rewritten.
* Writes through a temp file and a rename in the same directory, so a failure
  never leaves a partial file. A symbolic link at PATH is replaced by a regular
  file, never written through, and a file that is not writable is refused, not
  replaced.

``<value>`` is the marker's value. When the marker is absent or malformed it is
``unknown`` and the reason goes to stderr. The marker is one line,
``tachi_version: <value>``, where the value is one token (a letter or digit, then
letters, digits and ``. _ + ~ -``, at most 128 characters). The run archiver
applies the same rule, so its manifest and the stamped file always agree.

Scope decision (CF-21): this script writes ``tachi_version`` and no other key.
Writing ``schema_version`` from ``schemas/output.yaml`` was measured in a scratch
clone and is not zero-churn: it turns five infographic goldens red
(``test_existing_templates_unchanged``; each golden embeds a ``schema_version``).
So there is no ``--schema-version-from-template`` flag, and ``schema_version``
stays model-authored and declared-only, as ``schemas/output.yaml`` and
``output-schemas.md`` state. Record:
``specs/391-isolated-auditable-operation/test-results/t038a-measurement.md``.

Constraints: Python >= 3.9, stdlib only.

Exit codes. ``--check`` exits what a stamp run would: 0 when it would change
nothing, 1 when it would write, 2 when it would fail.
    0  stamped; or the file already carries the stamp and nothing is written; or
       ``--check`` and the file carries the stamp.
    1  ``--check`` only: the field is missing, differs from the marker, or is not
       in the form this script writes. Nothing is written.
    2  error, nothing written: the file is unreadable, unwritable or not a
       regular file, it has no frontmatter, or an argument is bad.

Messages go to stderr with a ``[391]`` prefix. They name files and the value read
from the marker, never the content of the file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import traceback

FIELD = "tachi_version"
UNKNOWN = "unknown"
DEFAULT_MARKER = "templates/tachi/VERSION"
MARKER_MAX_BYTES = 4096

# AOD-SIMPLIFICATION: writes tachi_version only, schema_version stays model-authored — upgrade: regenerate the five infographic goldens, then add a flag that reads schemas/output.yaml (CF-21)

# The marker's one line. The value is one token with nothing in it that a
# double-quoted YAML scalar would need escaped. Kept identical to _MARKER_RE in
# scripts/archive-run-transcripts.py, so the manifest's tachi_version and the
# stamped one cannot disagree.
_MARKER_RE = re.compile(r"tachi_version:[ \t]*([A-Za-z0-9][A-Za-z0-9._+~-]{0,127})[ \t]*\r?\Z")

# Frontmatter is found on lines, as bytes: the file is never decoded or newline-
# translated, so every byte outside the inserted line survives.
_LINE_RE = re.compile(rb"[^\n]*\n|[^\n]+")
_DELIM_RE = re.compile(rb"---[ \t]*")
_FENCE_RE = re.compile(rb"```yaml[ \t]*")
_SCHEMA_KEY_RE = re.compile(rb"schema_version[ \t]*:")
_FIELD_KEY_RE = re.compile(rb"tachi_version[ \t]*:")


class StampError(Exception):
    """A failure that exits 2. The message names a file or a rule, never file content."""


# =============================================================================
# The marker
# =============================================================================


def _read_marker(path):
    """``(value, reason)``: the marker's value and None, or ``("unknown", why)``."""
    try:
        st = os.lstat(path)
        if not stat.S_ISREG(st.st_mode):
            return UNKNOWN, "it is not a regular file"
        if st.st_size > MARKER_MAX_BYTES:
            return UNKNOWN, "it is larger than %d bytes" % MARKER_MAX_BYTES
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        return UNKNOWN, "it does not exist"
    except (OSError, UnicodeDecodeError) as exc:
        return UNKNOWN, "it cannot be read (%s)" % (getattr(exc, "strerror", None) or type(exc).__name__)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    match = _MARKER_RE.match(lines[0]) if len(lines) == 1 else None
    if match is None:
        return UNKNOWN, "it is not exactly one line of the form tachi_version: <value>"
    return match.group(1), None


# =============================================================================
# The frontmatter
# =============================================================================


def _content(line):
    return line.rstrip(b"\r\n")


def _eol(line):
    if line.endswith(b"\r\n"):
        return b"\r\n"
    return b"\n" if line.endswith(b"\n") else b""


def _find_frontmatter(lines):
    """``(first, last)`` with the frontmatter body at ``lines[first:last]``, or None.

    The same two shapes, in the same order, as ``tachi_parsers._extract_frontmatter_text``:
    a ``---`` block that opens the file, else a ``---`` block right after a
    ``yaml`` code fence (its closing ``---`` is followed by the closing fence).
    """
    if lines and _DELIM_RE.fullmatch(_content(lines[0])):
        for j in range(1, len(lines)):
            if _DELIM_RE.fullmatch(_content(lines[j])):
                return 1, j
    for i in range(len(lines) - 2):
        if _FENCE_RE.fullmatch(_content(lines[i])) and _DELIM_RE.fullmatch(_content(lines[i + 1])):
            for j in range(i + 2, len(lines) - 1):
                if _DELIM_RE.fullmatch(_content(lines[j])) and _content(lines[j + 1]).startswith(b"```"):
                    return i + 2, j
    return None


def _stamped_lines(lines, first, last, value):
    """``lines`` with ``tachi_version`` set to ``value`` inside the body ``lines[first:last]``."""
    stamp = ('%s: "%s"' % (FIELD, value)).encode("ascii")
    body = []
    done = False
    for line in lines[first:last]:
        if _FIELD_KEY_RE.match(line):  # an existing field keeps its place; a duplicate is dropped
            if not done:
                body.append(stamp + (_eol(line) or b"\n"))
                done = True
            continue
        body.append(line)
    if not done:
        at = len(body)
        eol = _eol(body[-1]) if body else _eol(lines[first - 1])
        for k, line in enumerate(body):
            if _SCHEMA_KEY_RE.match(line):
                at = k + 1
                while at < len(body) and body[at][:1] in (b" ", b"\t"):  # keep a multi-line value whole
                    at += 1
                eol = _eol(line)
                break
        body.insert(at, stamp + (eol or b"\n"))
    return lines[:first] + body + lines[last:]


# =============================================================================
# File I/O
# =============================================================================


def _read_threats(path):
    """``(data, mode)`` of a regular file, read as bytes."""
    try:
        st = os.stat(path)
        if not stat.S_ISREG(st.st_mode):
            raise StampError("%s is not a regular file" % path)
        with open(path, "rb") as fh:
            return fh.read(), stat.S_IMODE(st.st_mode)
    except OSError as exc:
        raise StampError("cannot read %s (%s)" % (path, exc.strerror or type(exc).__name__))


def _write_atomic(path, data, mode):
    """Replace ``path`` with ``data`` through a temp file and a rename beside it."""
    if not os.access(path, os.W_OK):  # a rename would bypass a read-only file's own signal
        raise StampError("%s is not writable" % path)
    temp = os.path.join(os.path.dirname(path) or ".", ".%s.stamp.%d.tmp" % (os.path.basename(path), os.getpid()))
    try:
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # O_EXCL: never through a link or onto a file
    except OSError as exc:
        raise StampError("cannot write %s (%s)" % (path, exc.strerror or type(exc).__name__))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(temp, mode)
        os.replace(temp, path)
    except OSError as exc:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise StampError("cannot write %s (%s)" % (path, exc.strerror or type(exc).__name__))


# =============================================================================
# CLI
# =============================================================================


def _run(args, summary):
    value, reason = _read_marker(args.marker)
    summary["tachi_version"] = value
    if reason:
        summary["warnings"].append('version marker %s: %s; using "%s"' % (args.marker, reason, UNKNOWN))

    data, mode = _read_threats(args.threats)
    lines = _LINE_RE.findall(data)
    found = _find_frontmatter(lines)
    if found is None:
        raise StampError("%s has no YAML frontmatter (expected a leading --- block or one inside a yaml code fence)"
                         % args.threats)
    stamped = b"".join(_stamped_lines(lines, found[0], found[1], value))

    if stamped == data:
        summary["status"] = "unchanged"
        return 0
    if args.check:
        summary["status"] = "stale"
        summary["reason"] = '%s: %s is not stamped as "%s"; run without --check to stamp it' % (args.threats, FIELD, value)
        return 1
    _write_atomic(args.threats, stamped, mode)
    summary["status"] = "stamped"
    return 0


def _build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="stamp-tachi-version.py",
        description=("Stamp the installed tachi version into a threats.md frontmatter as tachi_version, copied "
                     "from the one-line marker templates/tachi/VERSION (feature 391). Deterministic and "
                     "idempotent; the model never writes the field."),
    )
    parser.add_argument("--threats", required=True, metavar="PATH",
                        help="The threats.md to stamp, in place.")
    parser.add_argument("--marker", metavar="PATH", default=DEFAULT_MARKER,
                        help="The version marker (default: %(default)s, relative to the current directory). "
                             "Absent or malformed, the stamped value is 'unknown'.")
    parser.add_argument("--check", action="store_true",
                        help="Write nothing. Exit 0 if the file already carries the stamp, 1 if the field is "
                             "missing or differs from the marker.")
    parser.add_argument("--json", action="store_true", help="Print the run summary as JSON on stdout.")
    return parser


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)
    summary = {"status": "error", "threats": args.threats, "marker": args.marker,
               "tachi_version": None, "check": args.check, "warnings": []}
    try:
        code = _run(args, summary)
    except StampError as exc:
        summary["reason"], code = str(exc), 2
    except Exception as exc:  # last resort: an uncaught error would exit 1, which means "check failed"
        where = traceback.extract_tb(exc.__traceback__)[-1].lineno if exc.__traceback__ else 0
        summary["reason"], code = "internal error (%s at line %d)" % (type(exc).__name__, where), 2
    if code != 0:
        print("[391] %s" % summary["reason"], file=sys.stderr)
    for text in summary["warnings"]:
        print("[391] warning: %s" % text, file=sys.stderr)
    if args.json:
        print(json.dumps(summary, sort_keys=True, indent=2))
    elif summary["status"] == "stamped":
        print('[391] stamped %s "%s" in %s' % (FIELD, summary["tachi_version"], args.threats))
    elif summary["status"] == "unchanged":
        print('[391] %s "%s" is already stamped in %s; nothing to do' % (FIELD, summary["tachi_version"], args.threats))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
