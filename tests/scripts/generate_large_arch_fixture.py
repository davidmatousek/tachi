"""Deterministic generator for F-374's synthetic large-architecture fixture (spec S-4).

SKELETON (W0, T003). The CLI, the seeded helpers, the serializer and the part registry are
real. T019, T040, T148 and T103 fill the stubs. Standard library only, Python 3.9 syntax.

    python3 tests/scripts/generate_large_arch_fixture.py --out DIR [--variant NAME|all]

Determinism contract (S-4, S-11; T020 pins it):
  - One fixed seed (SEED), and one stream per part, derived from SEED and the part's name. So
    adding or removing a part never moves another part's bytes.
  - Every decision comes from Rng.unit() (the stdlib random() draw) or from a label hash. No other
    stdlib random method is used, because Python doesn't guarantee their sequences across versions.
  - Nothing reads hash(), set order, the clock, the locale, the environment or directory order.
  - Files are written by this module: UTF-8, LF newlines, exactly one trailing newline. JSON comes
    from dumps() below (sorted keys, ASCII escapes), never from json.dumps.
  - Output is byte-identical on Python 3.9 to 3.13.

Layout convention: a part writes under a directory named for itself, and no two parts may emit
the same path. Tests regenerate into a temporary directory and compare bytes with the committed
copy under tests/scripts/fixtures/large_arch/. They never rewrite tracked files.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import random
import re
import sys
from collections.abc import Sequence
from typing import Optional

SEED = 374  # Fixed. Changing it changes every committed byte.

# S-2's total order of finding prefixes. Every part that numbers findings uses this one copy.
PREFIX_ORDER = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")


# --------------------------------------------------------------------------- seeded helpers
def label_hash(label: str) -> int:
    """A 64-bit hash of SEED and a label: the other source of decisions besides Rng.unit()."""
    digest = hashlib.sha256(("%d:%s" % (SEED, label)).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def label_below(label: str, n: int) -> int:
    """An integer in [0, n) fixed by the label alone, for decisions that must survive edits elsewhere."""
    if n < 1:
        raise ValueError("n must be at least 1")
    return label_hash(label) % n


class Rng:
    """One seeded stream per part. unit() is the only draw; below() and pick() derive from it."""

    def __init__(self, name: str) -> None:
        self._stream = random.Random()
        self._stream.seed(label_hash("stream:" + name))

    def unit(self) -> float:
        """A float in [0.0, 1.0)."""
        return self._stream.random()

    def below(self, n: int) -> int:
        """An integer in [0, n)."""
        if n < 1:
            raise ValueError("n must be at least 1")
        return min(int(self.unit() * n), n - 1)

    def pick(self, items: Sequence):
        """One element of a non-empty sequence."""
        return items[self.below(len(items))]


# --------------------------------------------------------------------------- serializer
_JSON_ESCAPE = re.compile(r'[\x00-\x1f"\\\x7f-\U0010ffff]')
_SHORT_ESCAPES = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t", "\b": "\\b", "\f": "\\f"}


def _escape(match: "re.Match[str]") -> str:
    char = match.group(0)
    if char in _SHORT_ESCAPES:
        return _SHORT_ESCAPES[char]
    code = ord(char)
    if code > 0xFFFF:  # a surrogate pair, so the output stays ASCII
        code -= 0x10000
        return "\\u%04x\\u%04x" % (0xD800 + (code >> 10), 0xDC00 + (code & 0x3FF))
    return "\\u%04x" % code


def _emit(value, indent: int, level: int, sort_keys: bool, out: list) -> None:
    if value is None:
        out.append("null")
    elif value is True or value is False:
        out.append("true" if value else "false")
    elif isinstance(value, int):
        out.append(str(int(value)))
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NaN and Infinity have no JSON form")
        out.append(repr(value))
    elif isinstance(value, str):
        out.append('"' + _JSON_ESCAPE.sub(_escape, value) + '"')
    elif isinstance(value, (list, tuple, dict)):
        is_map = isinstance(value, dict)
        if not value:
            out.append("{}" if is_map else "[]")
            return
        if is_map:
            if not all(isinstance(key, str) for key in value):
                raise TypeError("JSON object keys must be strings")
            members = sorted(value) if sort_keys else list(value)
        else:
            members = list(range(len(value)))
        inner = "\n" + " " * (indent * (level + 1)) if indent else ""
        out.append("{" if is_map else "[")
        for position, key in enumerate(members):
            out.append(("," if position else "") + inner)
            if is_map:
                out.append('"' + _JSON_ESCAPE.sub(_escape, key) + '"' + (": " if indent else ":"))
            _emit(value[key], indent, level + 1, sort_keys, out)
        out.append(("\n" + " " * (indent * level) if indent else "") + ("}" if is_map else "]"))
    else:
        raise TypeError("cannot serialize %s" % type(value).__name__)


def dumps(value, indent: int = 2, sort_keys: bool = True) -> str:
    """Canonical JSON text with no trailing newline. indent=0 gives one compact line.

    Handles None, bool, int, finite float, str, list, tuple and dict with str keys. Keys are
    sorted by code point unless sort_keys is False, which keeps insertion order (guaranteed
    since Python 3.7). Non-ASCII characters are written as \\uXXXX escapes.
    """
    out: list = []
    _emit(value, indent, 0, sort_keys, out)
    return "".join(out)


# --------------------------------------------------------------------------- build and write
_PATH_OK = re.compile(r"[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)*")


def _check_path(path: str) -> None:
    if not _PATH_OK.fullmatch(path) or {".", ".."} & set(path.split("/")):
        raise ValueError("unsafe fixture path: %r" % path)


def _canonical_text(text: str) -> bytes:
    if "\r" in text:
        raise ValueError("generated text holds a carriage return")
    return (text.rstrip("\n") + "\n").encode("utf-8")


def build(variant: str = "all") -> dict:
    """Run the selected parts and return {relative path: bytes}. Pure: it touches no file."""
    if variant != "all" and variant not in PARTS:
        raise ValueError("unknown variant: %r" % variant)
    names = list(PARTS) if variant == "all" else [variant]
    files: dict = {}
    seen: dict = {}
    for name in names:
        for path, text in PARTS[name](Rng(name)).items():
            _check_path(path)
            key = path.lower()  # a case-insensitive checkout must not merge two files
            if key in seen:
                raise ValueError("%s (part %s) collides with %s (part %s)" % ((path, name) + seen[key]))
            seen[key] = (path, name)
            files[path] = _canonical_text(text)
    return files


def write_files(out: str, files: dict) -> None:
    """Write {relative path: bytes} under out, in sorted order, creating directories."""
    for path in sorted(files):
        target = os.path.join(out, *path.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(files[path])


# --------------------------------------------------------------------------- parts
# A part is a pure function of its Rng and SEED: it returns {relative path: text}. It may open more
# streams with Rng("<part>/<aspect>"). Parts that share data (the architecture and the findings)
# rebuild it from the seed through one helper that T019 adds, never from another part's output, so
# each part stays independent and regenerates alone with --variant NAME.
def part_canary(rng: Rng) -> dict:
    """W0 canary: exercises every helper, so a version difference shows up here first (S-4)."""
    probe = {
        "seed": SEED,
        "unit": [rng.unit() for _ in range(3)],
        "below": [rng.below(1000) for _ in range(8)],
        "pick": [rng.pick(("worker-2", "s3-archive", "gateway")) for _ in range(6)],
        "label": {name: label_below(name, 1000) for name in ("S-1", "worker-2", "s3-archive")},
        "serializer": {
            "z": [True, False, None, 0, -7, 1.5, 1e16, 0.1],
            "a": "tab\t quote\" back\\ line\n tilde~ del\x7f "
                 "e-acute\N{LATIN SMALL LETTER E WITH ACUTE} emoji\U0001f600",
            "empty": {"map": {}, "list": []},
        },
    }
    return {"canary/probe.json": dumps(probe), "canary/probe.txt": "LF only\nsecond line\n\n\n"}


def part_architecture(rng: Rng) -> dict:
    """T019: 25 components (some digit-bearing), 4+ trust zones, all 7 MAESTRO layers, 2+ LLM, 2+ agentic."""
    return {}


def part_baseline(rng: Rng) -> dict:
    """T019: baseline run dir (S-4): threats.md, attack-trees/ + manifest, scores and controls .md, 3 SARIF files."""
    return {}


def part_stub_codebase(rng: Rng) -> dict:
    """T019: a small code tree with detectable controls for some findings."""
    return {}


def part_gated_subset(rng: Rng) -> dict:
    """T019: the small Mermaid-free subset for gated CI (tests pass it a smaller batch size)."""
    return {}


def part_seeded_error(rng: Rng) -> dict:
    """T040: per prefix, a wrong composite, band, vector and reachability value, a missing vector, controls."""
    return {}


def part_legacy_format(rng: Rng) -> dict:
    """T040: no sub-score tables, partial vectors in markdown, full vectors in SARIF, one disagreement (R-26)."""
    return {}


def part_tagged(rng: Rng) -> dict:
    """T040: tagged components, findings above 9.2, a carried legacy finding, ruling A's band moves."""
    return {}


def part_id_reuse(rng: Rng) -> dict:
    """T040: PR 1's case (a NEW finding reusing a baseline ID). T148: PR 2's high-water-mark and no-mark baselines."""
    return {}


def part_ties(rng: Rng) -> dict:
    """T040: a band-moving composite tie, a rounding-only tie and a residual tie (R-11)."""
    return {}


def part_regroup_pair(rng: Rng) -> dict:
    """T040: two runs where correlation regroups carried findings and moves a primary, plus a re-run."""
    return {}


def part_chain_cap(rng: Rng) -> dict:
    """T148: chain material that yields more than 105 consolidated chains (S-3(g)'s offline test)."""
    return {}


def part_pr2_runs(rng: Rng) -> dict:
    """T103: threat-model run dirs (records, briefs, ID map, Phase 1 tables), tree batches, report parts."""
    return {}


PARTS = {
    "canary": part_canary,
    "architecture": part_architecture,
    "baseline": part_baseline,
    "stub-codebase": part_stub_codebase,
    "gated-subset": part_gated_subset,
    "seeded-error": part_seeded_error,
    "legacy-format": part_legacy_format,
    "tagged": part_tagged,
    "id-reuse": part_id_reuse,
    "ties": part_ties,
    "regroup-pair": part_regroup_pair,
    "chain-cap": part_chain_cap,
    "pr2-runs": part_pr2_runs,
}


# --------------------------------------------------------------------------- command line
def main(argv: Optional[Sequence[str]] = None) -> int:
    """Exit codes: 0 written; 1 a part broke the contract; 2 usage error."""
    parser = argparse.ArgumentParser(description="Generate F-374's synthetic fixture deterministically.")
    parser.add_argument("--out", required=True, metavar="DIR", help="directory to write into (created if missing)")
    parser.add_argument("--variant", default="all", help="one part (%s), or all (default)" % ", ".join(PARTS))
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_request:  # argparse exits; main() returns instead, so tests can call it
        return exit_request.code if isinstance(exit_request.code, int) else 2
    if os.path.exists(args.out) and not os.path.isdir(args.out):
        print("error: --out is not a directory", file=sys.stderr)
        return 2
    if args.variant != "all" and args.variant not in PARTS:
        print("error: unknown variant %r" % args.variant, file=sys.stderr)
        return 2
    try:
        files = build(args.variant)
    except ValueError as problem:
        print("error: %s" % problem, file=sys.stderr)
        return 1
    write_files(args.out, files)
    print("wrote %d files, %d bytes" % (len(files), sum(len(data) for data in files.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
