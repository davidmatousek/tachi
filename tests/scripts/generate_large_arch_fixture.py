"""Deterministic generator for F-374's synthetic large-architecture fixture (spec S-4).

Built in steps. W0 (T003) wrote the CLI, the seeded helpers, the serializer and the part
registry. T019 (W1) filled the base parts: the architecture, the baseline run directory, the stub
codebase and the gated subset. T040 (W2) fills the PR 1 variants, listed below. T148 and T103 fill
the parts that are still stubs (chain-cap, pr2-runs, and the PR 2 half of id-reuse).
Standard library only, Python 3.9 syntax.

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

The base set (T019), as committed:
  canary/         W0's determinism probe.
  architecture/   architecture.md: 25 invented components in 5 trust zones and all 7 MAESTRO layers, with a Mermaid diagram.
                  The SARIF files name docs/security/architecture.md as their input; copy this file there to use it.
  baseline/       one baseline run directory: threats.md (schema 1.4, baseline-aware: delta statuses, Section 4c and 8),
                  risk-scores.md and compensating-controls.md (schema 1.0, the templates' shape), threats.sarif,
                  risk-scores.sarif, compensating-controls.sarif, and attack-trees/ with its .manifest.json.
                  It is a pre-fix (v4.48.4) output: a correlated peer is a relatedLocations entry of its primary in
                  threats.sarif, and the other two SARIF files hold one result per finding.
  stub-codebase/  one short, never-run module per security control. The controls report quotes its file and line.
  gated-subset/   the same run directory at 42 findings, a text architecture and no trees: no Mermaid anywhere,
                  for jobs that have no mmdc. Tests pass a small batch size so that each batched path runs twice.
The PR 1 variants (T040) sit beside the base set and never move a byte of it. Each is a directory of scenarios, and a scenario is one
scorer run: baseline/ (the baseline run directory the renderer reads), run/threats.md, architecture/ when the case has one, and
expected-outcomes.json (format tachi.fixture-expected/1, described at the variants' code below). The base set's tree digest
(W1's digest_tree.py over the five base directories) is d35f160950e1c8459c3d4bca, and a test pins it.
  seeded-error/main                a pre-fix baseline with, for each of the 12 prefixes, a wrong composite, a wrong band, an out-of-clamp
                                   CVSS score, an out-of-range reachability and a missing vector; clamp, N17, rounding, override,
                                   compound-label and RESOLVED controls (S-4, SC-4, R-9, R-10, R-11, R-30, R-31)
  legacy-format/main               the compact form with no sub-score tables, vectors on only some rows, full vectors in the SARIF, one
                                   disagreement and seeded errors; legacy-format/no-baseline-date holds the review-date fallback rungs (R-26)
  tagged/renderer-form, legacy-form ruling A in both directions, PM-T7's band that holds, and R-25's outcomes, on a baseline that records its
                                   tags and on one that does not
  tagged/s13-*                     S-13's five branches: block equal, stale block, no architecture file, neither source, a drift form
  id-reuse/pr1                     a NEW finding whose ID the baseline risk-scores.md used (ruling B); id-reuse/pr2 is T148's
  ties/scorer, ties/controls       band-moving and rounding-only composite ties, boundary composites, and residual ties (R-11)
  regroup-pair/main                correlation regroups carried findings and changes a primary, with a NEW and an UPDATED peer, and a re-run
Scale of the base set: 408 open findings over all 12 prefixes (56 Critical), 6 RESOLVED, 21 correlation groups
(13 span three or more categories). Each of its six targeted outputs is over twice the 64k cap by UTF-8 bytes / 4.
Every score is internally consistent (CVSS from its vector, composite from its parts, no rounding tie), so the
base set carries no seeded error; the seeded-error, legacy-format, tagged, ties and regroup parts add those.
PR 2's cases (T148) wait on no ruling. They use the PR 1 variants' scenario layout and tachi.fixture-expected/1 envelope, and their code
sits just above PARTS, so that it merges beside T040's code and never inside it:
  chain-cap/main            attack-chains.py's input and S-3(g)'s offline test: run/threats.md (Sections 5 to 8 cut down, Section 7 whole),
                            run/tachi-build/phase1/inventory.json (a working directory renames tachi-build/ to .tachi-build/, a name that
                            .gitignore excludes) and more than 105 consolidated chains, built in islands that no flow joins
  id-reuse/pr2              ruling B's high-water mark: a baseline whose mark sits above its live IDs, and a run with NEW findings under,
                            at and above it
  id-reuse/pr2-no-mark      the same baseline with no mark, as every pre-PR 2 baseline: the first PR 2 run seeds its mark from live IDs
                            and Section 4c (PM-T7)
PR 2's run directories (T103) sit in pr2-runs/, six scenarios in the same layout (run/, baseline/ and expected-outcomes.json), and their code
is the block that starts at "T103: PR 2's run directories", just above PARTS. The first four are for check-threat-model.py: forms (every provenance
form), truncation (a stateless run whose dispatches are cut short and re-dispatched), and reissue-mark and reissue-no-mark (T148's id-reuse runs, with
the records that make their provenance whole). The last two are the trees stage and the report stage of the forms run, before and after
assemble-report.py trees. A record's brief, a brief's inputs, a plan and a batch input hold absolute paths, so the committed copy is built for the
root PR2R_ROOT, a path that exists nowhere, and materialize(scenario, directory) builds the same scenario for a real directory, with every path and
every digest that binds the files rewritten for it.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import itertools
import math
import os
import random
import re
import sys
from collections.abc import Sequence
from fractions import Fraction
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


# --------------------------------------------------------------------------- score arithmetic
# Scores are held as integers in tenths (75 means 7.5), so no float ever reaches a file. Rounding is
# half-up on exact integers, the rule ADR-050 D5 pins for the renderers.
EM = "\u2014"  # the em dash the shipped formats use in layer names and placeholders


def fmt1(tenths: int) -> str:
    """Format a score held in tenths: 75 -> '7.5', 100 -> '10.0'."""
    return "%d.%d" % divmod(tenths, 10)


def half_up(numerator: int, denominator: int) -> int:
    """Round numerator / denominator to the nearest integer, halves up (non-negative inputs)."""
    return (2 * numerator + denominator) // (2 * denominator)


def composite_tenths(c: int, e: int, s: int, r: int) -> int:
    """0.35 x CVSS + 0.30 x exploitability + 0.15 x scalability + 0.20 x reachability, in tenths."""
    return half_up(35 * c + 30 * e + 15 * s + 20 * r, 100)


def composite_is_tie(c: int, e: int, s: int, r: int) -> bool:
    return (35 * c + 30 * e + 15 * s + 20 * r) % 100 == 50


# Section 3's weighted table, as the 1.1 template and the renderer write it: the dimension's label, its key in a score row and its weight in hundredths.
WEIGHT_ROWS = (("CVSS Base", "cvss", 35), ("Exploitability", "expl", 30), ("Scalability", "scale", 15), ("Reachability", "reach", 20))


def weighted_cell(tenths: int, weight: int) -> str:
    """A Weighted cell for a score in tenths and a weight in hundredths: exact in thousandths, then half up to two decimals.

    8.3 x 0.35 is 2.905 and shows 2.91, and 2.5 x 0.20 shows 0.50."""
    return "%d.%02d" % divmod(half_up(tenths * weight, 10), 100)


def composite_on_boundary(t: int) -> bool:
    return t in (40, 70, 90)


def band_of(tenths: int) -> str:
    return "Critical" if tenths >= 90 else "High" if tenths >= 70 else "Medium" if tenths >= 40 else "Low"


BAND_GOVERNANCE = {  # band -> (SLA text, SLA days, disposition)
    "Critical": ("24h", 1, "Mitigate"),
    "High": ("7d", 7, "Mitigate"),
    "Medium": ("30d", 30, "Review"),
    "Low": ("90d", 90, "Review"),
}


def residual_tenths(tenths: int, factor_pct: int) -> int:
    return half_up(tenths * (100 - factor_pct), 100)


def residual_is_tie(tenths: int, factor_pct: int) -> bool:
    return (tenths * (100 - factor_pct)) % 100 == 50


def add_days(iso: str, days: int) -> str:
    year, month, day = (int(part) for part in iso.split("-"))
    return (datetime.date(year, month, day) + datetime.timedelta(days=days)).isoformat()


# CVSS 3.1 base score from the specification's formulas, in exact fractions so that no float or
# Python version can move a rounding boundary.
_W_AV = {"N": Fraction(85, 100), "A": Fraction(62, 100), "L": Fraction(55, 100), "P": Fraction(2, 10)}
_W_AC = {"L": Fraction(77, 100), "H": Fraction(44, 100)}
_W_UI = {"N": Fraction(85, 100), "R": Fraction(62, 100)}
_W_CIA = {"H": Fraction(56, 100), "L": Fraction(22, 100), "N": Fraction(0)}
_W_PR = {
    "U": {"N": Fraction(85, 100), "L": Fraction(62, 100), "H": Fraction(27, 100)},
    "C": {"N": Fraction(85, 100), "L": Fraction(68, 100), "H": Fraction(5, 10)},
}


def cvss_tenths(vector: str) -> int:
    """Base score of a 'CVSS:3.1/AV:../...' vector in tenths (the specification's Roundup included)."""
    metrics = dict(part.split(":") for part in vector.split("/")[1:])
    changed = metrics["S"] == "C"
    iss = 1 - (1 - _W_CIA[metrics["C"]]) * (1 - _W_CIA[metrics["I"]]) * (1 - _W_CIA[metrics["A"]])
    if changed:
        impact = Fraction(752, 100) * (iss - Fraction(29, 1000)) - Fraction(325, 100) * (iss - Fraction(2, 100)) ** 15
    else:
        impact = Fraction(642, 100) * iss
    if impact <= 0:
        return 0
    exploitability = (
        Fraction(822, 100) * _W_AV[metrics["AV"]] * _W_AC[metrics["AC"]]
        * _W_PR["C" if changed else "U"][metrics["PR"]] * _W_UI[metrics["UI"]]
    )
    raw = impact + exploitability
    if changed:
        raw *= Fraction(108, 100)
    scaled = round(min(raw, Fraction(10)) * 100000)  # exact; halves go to even, as in the specification
    return scaled // 10000 if scaled % 10000 == 0 else scaled // 10000 + 1


CATEGORY_VECTOR = {  # schemas/risk-scoring.yaml category_defaults
    "spoofing": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N",
    "tampering": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L",
    "repudiation": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N",
    "info-disclosure": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N",
    "denial-of-service": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
    "privilege-escalation": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H",
    "agentic": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L",
    "llm": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N",
}
_CATEGORY_DEFAULT_TENTHS = {  # cvss-vectors.md's documented table, used as the calculator's own check
    "spoofing": 82, "tampering": 71, "repudiation": 43, "info-disclosure": 65,
    "denial-of-service": 75, "privilege-escalation": 99, "agentic": 99, "llm": 93,
}
PREFIX_CATEGORY = {  # ADR-050 D10: a category for every prefix
    "S": "spoofing", "T": "tampering", "R": "repudiation", "I": "info-disclosure",
    "D": "denial-of-service", "E": "privilege-escalation",
    "AG": "agentic", "AGP": "agentic", "TE": "agentic", "LLM": "llm", "OI": "llm", "MI": "llm",
}


def self_test_cvss() -> None:
    """Fail loudly if the calculator drifts from the documented defaults or two FIRST vectors."""
    for category, vector in CATEGORY_VECTOR.items():
        if cvss_tenths(vector) != _CATEGORY_DEFAULT_TENTHS[category]:
            raise ValueError("CVSS calculator disagrees with the documented default for %s" % category)
    if cvss_tenths("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H") != 98:
        raise ValueError("CVSS calculator: all-high unchanged scope is not 9.8")
    if cvss_tenths("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H") != 100:
        raise ValueError("CVSS calculator: all-high changed scope is not 10.0")


def prefix_rank(finding_id: str) -> tuple:
    """S-2's total order: prefix rank, then the numeric suffix as an integer."""
    prefix, _, number = finding_id.rpartition("-")
    return (PREFIX_ORDER.index(prefix), int(number))


def finding_id_text(prefix: str, number: int) -> str:
    """AGP ids are zero-padded to two digits (AGP-01), every other prefix is plain."""
    return "%s-%02d" % (prefix, number) if prefix == "AGP" else "%s-%d" % (prefix, number)


# --------------------------------------------------------------------------- text helpers
def clip(text: str, limit: int) -> str:
    """Cut at a word boundary and end with '...', as the shipped tables do."""
    if len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0].rstrip(",;:") + "..."


def cell(text: str) -> str:
    """A table cell: never a pipe or a newline, because the pre-fix readers do not decode escapes."""
    if "|" in text or "\n" in text or "\r" in text:
        raise ValueError("table cell holds a pipe or a newline: %r" % text[:60])
    return text


def table(header: Sequence, rows: Sequence) -> str:
    """A GitHub pipe table. Rows are sequences of cell texts."""
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("-" * (len(h) + 2) for h in header) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(cell(str(value)) for value in row) + " |")
    return "\n".join(lines)


def digest16(text: str) -> str:
    """primaryLocationLineHash: the first 16 hex digits of sha256('{ruleId}|{component}')."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

# --------------------------------------------------------------------------- vocabulary
# Everything below is invented. The platform, its components and its findings describe no real system.
PLATFORM = "Brindle Freight Platform"
LAYER_NAME = {
    1: "Foundation Model", 2: "Data Operations", 3: "Agent Framework", 4: "Deployment Infrastructure",
    5: "Evaluation and Observability", 6: "Security and Compliance", 7: "Agent Ecosystem",
}


def layer_label(number: int) -> str:
    return "L%d %s %s" % (number, EM, LAYER_NAME[number])


# zone -> (trust level, baseline reachability in tenths). Reachability stays inside its trust range
# (Untrusted 8.0-10.0, Semi-trusted 4.0-7.0, Trusted 1.0-4.0).
ZONES = (
    ("Public Internet", "Untrusted", 90),
    ("Edge DMZ", "Semi-trusted", 65),
    ("Agent Runtime Zone", "Trusted", 25),
    ("Data Zone", "Trusted", 25),
    ("Operations Zone", "Trusted", 25),
    ("Partner Exchange", "Semi-trusted", 55),  # empty in the base and gated profiles; T040's variant worlds use it
)
ZONE_LEVEL = {name: level for name, level, _ in ZONES}
ZONE_REACH = {name: reach for name, _, reach in ZONES}

# ai: the threat sub-agents that apply (AG:autonomy AG:tool LLM:inject LLM:poison LLM:theft OI MI TE).
# traits: human (emits to people), sink (its output reaches an execution sink), log (keeps a record).
COMPONENT_ROWS = (
    ("client-portal", "External Entity", 7, "Public Internet", (), ("human",),
     "Browser front end where operators submit shipment requests and approve agent proposals",
     "operator requests and approval decisions", "session cookie"),
    ("partner-feed", "External Entity", 7, "Public Internet", (), (),
     "Carrier systems that push manifests and status events through signed webhooks",
     "signed carrier manifests", "webhook signature"),
    ("edge-gateway", "Process", 4, "Edge DMZ", ("LLM:inject",), (),
     "Ingress proxy that terminates TLS, applies request limits and screens prompts before the intake agent",
     "inbound API requests", "bearer token"),
    ("auth-broker", "Process", 6, "Edge DMZ", (), (),
     "Token broker that validates operator and partner credentials and mints short-lived session grants",
     "credential assertions and session grants", "refresh token"),
    ("intake-agent", "Process", 3, "Agent Runtime Zone", ("AG:autonomy", "LLM:inject", "OI", "MI", "TE"), ("human", "sink"),
     "LLM-backed agent that turns free-text requests into structured shipment tasks and answers operators",
     "free-text shipment requests", "service token"),
    ("planner-agent", "Process", 3, "Agent Runtime Zone", ("AG:autonomy", "AG:tool", "LLM:inject", "OI"), ("sink",),
     "Planning agent that decomposes tasks, selects tools and assigns subtasks to the router",
     "task plans and tool selections", "agent session token"),
    ("router-agent", "Process", 3, "Agent Runtime Zone", ("AG:autonomy", "AG:tool", "LLM:inject"), (),
     "Router agent that matches subtasks to worker agents and tracks their progress",
     "subtask assignments", "routing token"),
    ("worker-2", "Process", 3, "Agent Runtime Zone", ("AG:autonomy", "AG:tool", "LLM:inject", "OI"), ("sink",),
     "Worker agent that optimises routes and looks up carrier rates through the tool server",
     "work orders and route candidates", "worker credential"),
    ("worker-3", "Process", 3, "Agent Runtime Zone", ("AG:autonomy", "AG:tool", "LLM:inject", "MI"), (),
     "Worker agent that drafts customs documents and delivery notices from retrieved context",
     "work orders and draft documents", "worker credential"),
    ("reviewer-agent", "Process", 3, "Agent Runtime Zone", ("AG:autonomy", "LLM:inject", "MI", "TE"), ("human",),
     "Reviewer agent that checks worker output and presents proposals to operators for approval",
     "drafted proposals awaiting review", "reviewer session"),
    ("tool-server-1", "Process", 3, "Agent Runtime Zone", ("AG:tool", "AG:autonomy", "LLM:inject"), ("sink",),
     "Tool server that exposes carrier rate, booking, label and customs tools to the agents",
     "tool call arguments and results", "tool API key"),
    ("model-gateway", "Process", 1, "Agent Runtime Zone", ("LLM:inject", "LLM:theft", "OI"), (),
     "Gateway that fronts the hosted foundation models and enforces per-agent quotas",
     "prompts and completions", "model API key"),
    ("embed-service-2", "Process", 1, "Agent Runtime Zone", ("LLM:poison", "LLM:theft"), (),
     "Embedding service that vectorises documents and queries for retrieval",
     "document chunks and query embeddings", "service credential"),
    ("summarizer-llm", "Process", 1, "Agent Runtime Zone", ("LLM:inject", "LLM:poison", "LLM:theft", "OI", "MI", "TE"), ("human", "sink"),
     "Fine-tuned summarisation model that writes customer-facing shipment summaries",
     "shipment records fed into summaries", "inference credential"),
    ("vector-store-a", "Data Store", 2, "Data Zone", ("LLM:poison",), (),
     "Vector database holding embedded carrier documents and ticket history",
     "embedded documents and metadata", "database credential"),
    ("kb-index", "Data Store", 2, "Data Zone", ("LLM:poison",), (),
     "Knowledge base index of carrier tariffs, customs rules and resolved tickets",
     "carrier tariffs and customs rules", "index credential"),
    ("memory-store", "Data Store", 2, "Data Zone", ("LLM:poison",), (),
     "Long-term agent memory that keeps task history and operator preferences",
     "task history and operator preferences", "store credential"),
    ("s3-archive", "Data Store", 2, "Data Zone", ("LLM:poison",), (),
     "Object archive of transcripts, exported manifests and fine-tuning corpora",
     "archived transcripts and training corpora", "access key"),
    ("feature-store-2", "Data Store", 2, "Data Zone", ("LLM:poison",), (),
     "Feature store feeding the ranking and fine-tuning jobs",
     "ranking and fine-tuning features", "pipeline credential"),
    ("queue-a2", "Process", 4, "Agent Runtime Zone", ("AG:tool", "AG:autonomy"), (),
     "Message bus that carries task and result messages between the agents",
     "task and result messages", "broker credential"),
    ("scheduler-1", "Process", 4, "Agent Runtime Zone", ("AG:autonomy",), (),
     "Scheduler agent that starts recurring planning runs and retries failed tasks",
     "recurring planning triggers", "scheduler credential"),
    ("trace-collector", "Process", 5, "Operations Zone", ("LLM:inject", "LLM:poison"), ("log",),
     "Collector that stores prompts, completions and tool traces for debugging and replay",
     "prompts, completions and tool traces", "collector token"),
    ("eval-runner", "Process", 5, "Operations Zone", ("LLM:poison", "LLM:inject", "MI"), (),
     "Evaluation harness that replays traces against candidate models and grades answers with an LLM judge",
     "replayed traces and judge verdicts", "evaluation credential"),
    ("policy-engine", "Process", 6, "Operations Zone", ("AG:autonomy", "LLM:inject"), (),
     "Policy engine that evaluates guardrail rules and approval requirements for agent actions",
     "guardrail rules and approval decisions", "policy token"),
    ("audit-ledger", "Data Store", 6, "Operations Zone", (), ("log",),
     "Append-only ledger of approvals, tool calls and administrative actions",
     "approval and tool call records", "ledger credential"),
)

# Components that only the variant worlds (T040) use. The base profile (components None) never reads them.
VARIANT_COMPONENT_ROWS = (
    ("partner-sandbox", "External Entity", 7, "Partner Exchange", (), (),
     "Carrier test harness that submits trial manifests and replays recorded webhooks against the gateway",
     "trial manifests and recorded webhooks", "sandbox token"),
)

# (source, destination, data, protocol). A directed acyclic graph: request paths only, so that the
# structural-connection test of Phase 3.5 sees a pipeline and not a clique.
FLOW_ROWS = (
    ("client-portal", "edge-gateway", "Operator requests and session cookies", "HTTPS (TLS 1.3)"),
    ("partner-feed", "edge-gateway", "Signed manifest webhooks and booking confirmations", "HTTPS (TLS 1.3)"),
    ("edge-gateway", "auth-broker", "Token introspection requests", "gRPC over mTLS"),
    ("edge-gateway", "intake-agent", "Screened operator requests", "HTTP/2 over mTLS"),
    ("auth-broker", "policy-engine", "Entitlement lookups", "gRPC over mTLS"),
    ("intake-agent", "queue-a2", "Structured task messages", "NATS over TLS"),
    ("intake-agent", "embed-service-2", "Query text for retrieval", "gRPC over mTLS"),
    ("intake-agent", "trace-collector", "Prompt and completion traces", "OTLP over TLS"),
    ("scheduler-1", "queue-a2", "Recurring task triggers", "NATS over TLS"),
    ("queue-a2", "planner-agent", "Task messages", "NATS over TLS"),
    ("planner-agent", "model-gateway", "Prompts and completions", "HTTPS (TLS 1.3)"),
    ("planner-agent", "memory-store", "Task history reads and writes", "PostgreSQL over TLS"),
    ("planner-agent", "policy-engine", "Action approval requests", "gRPC over mTLS"),
    ("planner-agent", "router-agent", "Subtask assignments", "HTTP/2 over mTLS"),
    ("planner-agent", "trace-collector", "Plan and tool selection traces", "OTLP over TLS"),
    ("router-agent", "worker-2", "Route optimisation work orders", "HTTP/2 over mTLS"),
    ("router-agent", "worker-3", "Document drafting work orders", "HTTP/2 over mTLS"),
    ("worker-2", "tool-server-1", "Tool calls (JSON-RPC)", "HTTPS (TLS 1.3)"),
    ("worker-2", "vector-store-a", "Similarity queries", "PostgreSQL over TLS"),
    ("worker-2", "trace-collector", "Worker traces", "OTLP over TLS"),
    ("worker-3", "tool-server-1", "Tool calls (JSON-RPC)", "HTTPS (TLS 1.3)"),
    ("worker-3", "summarizer-llm", "Draft text for summarisation", "gRPC over mTLS"),
    ("worker-3", "trace-collector", "Worker traces", "OTLP over TLS"),
    ("tool-server-1", "audit-ledger", "Tool call records", "gRPC over mTLS"),
    ("summarizer-llm", "reviewer-agent", "Generated summaries", "HTTP/2 over mTLS"),
    ("edge-gateway", "reviewer-agent", "Approval queries and operator decisions", "HTTP/2 over mTLS"),
    ("reviewer-agent", "audit-ledger", "Approval records", "gRPC over mTLS"),
    ("policy-engine", "audit-ledger", "Policy decisions", "gRPC over mTLS"),
    ("embed-service-2", "vector-store-a", "Embedding upserts", "PostgreSQL over TLS"),
    ("kb-index", "embed-service-2", "Document batches for embedding", "gRPC over mTLS"),
    ("s3-archive", "kb-index", "Tariff and rule documents", "HTTPS (TLS 1.3)"),
    ("trace-collector", "s3-archive", "Archived trace batches", "HTTPS (TLS 1.3)"),
    ("trace-collector", "eval-runner", "Replay datasets", "gRPC over mTLS"),
    ("eval-runner", "feature-store-2", "Evaluation features", "PostgreSQL over TLS"),
    ("feature-store-2", "summarizer-llm", "Fine-tuning examples", "gRPC over mTLS"),
    ("audit-ledger", "s3-archive", "Ledger exports", "HTTPS (TLS 1.3)"),
    ("partner-sandbox", "edge-gateway", "Trial manifests and replayed webhooks", "HTTPS (TLS 1.3)"),
)

TECHNOLOGY_ROWS = (
    ("Runtime", "Python", "3.12"),
    ("Agent framework", "Graph-based agent orchestration library", "0.2"),
    ("Gateway", "Envoy proxy", "1.29"),
    ("Identity", "OIDC with ES256 JWTs", "RFC 7519"),
    ("Messaging", "NATS JetStream", "2.10"),
    ("Database", "PostgreSQL with a vector extension", "16"),
    ("Object storage", "S3-compatible archive", "unknown"),
    ("Model hosting", "Hosted foundation model API", "unknown"),
    ("Tool protocol", "MCP over HTTP (JSON-RPC)", "2025-06"),
    ("Observability", "OpenTelemetry collector", "0.98"),
    ("Front end", "React single-page application", "18"),
    ("Policy", "Rule-based policy engine", "unknown"),
)

CROSSING_CONTROLS = {  # (from zone, to zone) -> controls named in Section 2
    ("Public Internet", "Edge DMZ"): "TLS 1.3 termination, request size limits, webhook signature checks",
    ("Edge DMZ", "Agent Runtime Zone"): "Mutual TLS, token validation, prompt screening",
    ("Edge DMZ", "Operations Zone"): "Mutual TLS, scoped entitlement lookups",
    ("Agent Runtime Zone", "Data Zone"): "Per-service database roles, TLS to the database, query allowlists",
    ("Agent Runtime Zone", "Operations Zone"): "Mutual TLS, write-only trace and audit endpoints",
    ("Agent Runtime Zone", "Public Internet"): "TLS 1.3, response filtering, human approval for outbound actions",
    ("Operations Zone", "Data Zone"): "Scoped export credentials, TLS, bucket policies",
    ("Operations Zone", "Agent Runtime Zone"): "Mutual TLS, signed training manifests",
    ("Data Zone", "Agent Runtime Zone"): "Mutual TLS, signed training manifests",
}

# --------------------------------------------------------------------------- text banks
# Each scenario is (threat core, mitigation core). Slots: {c} component, {p} a neighbour in the data
# flow, {a} what the component handles, {t} its credential noun, {z} its zone, {o} the trace collector.
SCENARIOS = {
    "S": (
        ("An attacker replays a captured {t} against {c}, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.",
         "Bind each {t} to the client certificate or device key, shorten its lifetime to minutes and reject any token presented from a different channel than the one it was issued to."),
        ("A compromised peer presents a forged service identity to {c}, and {c} accepts the claim without verifying the signature chain back to the issuing authority.",
         "Require mutual TLS between {p} and {c} and validate the full certificate chain, issuer and audience on every request instead of trusting the caller's own claim."),
        ("A shared or long-lived {t} on {c} lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.",
         "Replace the shared {t} with per-workload identities that rotate automatically, and alert when one identity authenticates from two networks within the rotation window."),
        ("An unauthenticated callback or health route on {c} accepts requests that downstream code treats as if they had come from {p}.",
         "Remove implicit trust in route names: authenticate every route of {c}, including callbacks and health checks, and drop requests that carry no verified caller identity."),
        ("Session fixation against {c} lets an attacker pre-seed an identifier and reuse the session after the victim authenticates.",
         "Issue a fresh session identifier on every authentication and privilege change, set strict cookie attributes and invalidate any identifier supplied before login."),
        ("Certificate or DNS spoofing between {p} and {c} lets an attacker terminate the connection and present a lookalike endpoint when pinning is absent.",
         "Pin the expected certificate authority for the link between {p} and {c}, validate host names strictly and fail closed when validation cannot complete."),
        ("Low-entropy identifiers accepted by {c} double as credentials, so an attacker who enumerates them submits requests under a victim's identity.",
         "Separate identifiers from secrets, generate secrets from a cryptographic random source of at least 128 bits and rate-limit failed lookups against {c}."),
    ),
    "T": (
        ("Unsanitised {a} reach {c} and are processed as trusted structure, so crafted input changes how later steps interpret the record.",
         "Validate {a} against a strict schema at the boundary of {c}, reject unknown fields and normalise encodings before any downstream use."),
        ("An attacker who can write to the channel between {p} and {c} modifies {a} in transit because messages carry no integrity protection of their own.",
         "Sign messages between {p} and {c} with a per-service key and verify the signature and a monotonic counter before accepting any change."),
        ("An update to {c} is pulled without provenance checks, so a poisoned package can alter how {a} are handled at run time.",
         "Pin dependencies by digest, verify signatures and provenance attestations in CI, and block deployment of {c} when a component lacks a valid attestation."),
        ("Configuration of {c} can be rewritten by any service that holds the shared deployment credential, silently changing how {a} are handled.",
         "Keep the configuration of {c} in a versioned, access-controlled repository, require review for changes and alert on drift from the approved revision."),
        ("A race between concurrent writers lets an attacker overwrite {a} on {c} after validation but before use, defeating the earlier check.",
         "Make validation and use atomic: take a version-checked write or compare-and-set on {a}, and reject updates whose version no longer matches."),
        ("Replay of an earlier valid update to {a} reaches {c} because updates carry no nonce or expiry, restoring a state the owner already corrected.",
         "Add a nonce and a short expiry to every update accepted by {c}, store seen nonces for the validity window and reject any repeat."),
        ("Serialised objects arriving from {p} are deserialised by {c} with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.",
         "Replace permissive deserialisation in {c} with a closed schema of allowed types, and reject payloads that name types outside it."),
        ("Backups and exports of {a} on {c} are writable by operators without a second approver, so a malicious change survives restores.",
         "Protect exports and backups of {a} with write-once storage and dual approval for restore, and verify checksums against a separately held manifest."),
    ),
    "R": (
        ("Actions taken through {c} are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to {a}.",
         "Log the verified principal, request identifier, source address and outcome for every state change in {c}, and ship the records to the audit ledger."),
        ("Log entries from {c} can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.",
         "Write the records of {c} to an append-only store that operators cannot modify, and anchor periodic hashes of the log in a separate system."),
        ("Clock drift between {c} and {p} leaves events in inconsistent order, so the sequence of actions on {a} cannot be reconstructed reliably.",
         "Synchronise {c} and {p} to a trusted time source, record monotonic sequence numbers with every event and alert when drift exceeds one second."),
        ("Delegated actions performed by {c} on behalf of a user are recorded under the service identity alone, hiding who authorised them.",
         "Carry the originating user and the approval reference through every delegated call made by {c}, and record both in the audit entry."),
        ("Failed and rejected attempts against {c} are not logged, so probing of {a} leaves no trace that an investigator could use.",
         "Log denied and malformed requests to {c} at a retained severity, aggregate them per source and alert on sustained probing."),
        ("Operators approve changes to {a} through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.",
         "Bind each approval to the exact change hash it covers, record approver and time in the audit ledger and refuse to execute unbound changes."),
    ),
    "I": (
        ("Verbose error responses from {c} reveal internal paths, query text and identifiers of {a} to any caller who can trigger a failure.",
         "Return generic error codes from {c}, log the detail on the server only and strip stack traces and identifiers from every external response."),
        ("{a} held by {c} are readable by any service in the {z} that shares the same network role, because access is granted by network position.",
         "Grant access to {a} per workload identity with least privilege, enforce it at {c} and remove network-position trust within the {z}."),
        ("Logs and traces emitted by {c} include raw {a}, so anyone with access to the logging pipeline can read content meant for one tenant.",
         "Redact or tokenise sensitive fields before {c} emits logs and traces, and restrict the logging pipeline to the roles that need it."),
        ("Data in transit between {p} and {c} is protected only on the outer hop, which leaves {a} readable on the internal segment after termination.",
         "Keep TLS end to end between {p} and {c}, disable plaintext listeners and verify the negotiated protocol version in deployment checks."),
        ("A timing or size difference in the responses of {c} lets an observer infer whether specific records of {a} exist.",
         "Equalise response size and timing for existence checks in {c}, and return the same status for present and absent records."),
        ("Backups of {a} taken from {c} are stored unencrypted in a shared location that wider operations staff can read.",
         "Encrypt backups of {a} with keys held outside the storage account, restrict the location to the recovery role and audit every read."),
        ("Cross-tenant filters on {c} are applied in application code only, so one missing predicate exposes another tenant's {a}.",
         "Enforce tenant isolation in the data layer with row-level policies or separate keys, and add a regression test that queries across tenants."),
        ("Secrets such as the {t} for {c} appear in process arguments and environment dumps that diagnostic tooling captures.",
         "Pass the {t} to {c} through a secret manager mount, exclude it from process listings and diagnostics, and rotate it after any exposure."),
    ),
    "D": (
        ("A burst of requests exhausts the connection pool of {c}, which queues work without a bound and blocks legitimate use of {a}.",
         "Set explicit concurrency and queue limits on {c}, shed load with a clear status when saturated and apply per-caller quotas."),
        ("A single oversized or deeply nested payload makes {c} spend disproportionate memory and CPU parsing {a}.",
         "Cap payload size, nesting depth and parse time in {c}, and reject requests that exceed the limits before allocation."),
        ("Retry storms from {p} multiply the load on {c} when it slows down, turning a brief delay into a sustained outage.",
         "Add jittered exponential backoff and a retry budget to {p}, and enable a circuit breaker so that {c} can recover."),
        ("A slow-read attack holds connections to {c} open and ties up the workers handling {a} until none remain for real requests.",
         "Apply idle and total timeouts on every connection to {c}, bound workers per client and move slow clients to a separate pool."),
        ("Unbounded growth of stored {a} on {c} fills its volume, after which writes fail for every other consumer.",
         "Set quotas and retention for {a} on {c}, alert at eighty percent capacity and reserve space for control-plane writes."),
        ("A dependency of {c} becomes unavailable and the failure cascades because {c} waits on it synchronously for every request.",
         "Isolate calls from {c} to the dependency with timeouts and bulkheads, serve degraded results where possible and alert on dependency health."),
        ("Expensive queries over {a} can be triggered by any authorised caller of {c}, so one user can degrade the service for all.",
         "Enforce cost limits and pagination on queries to {c}, run heavy work on a separate pool and cancel queries that exceed the budget."),
    ),
    "E": (
        ("Object identifiers in requests to {c} are trusted without an ownership check, so a caller can read or change {a} that belong to others.",
         "Check ownership or entitlement for every object reference at {c} on the server, and deny by default when the check cannot be made."),
        ("Role claims carried in the {t} presented to {c} are honoured without confirmation against the authoritative directory.",
         "Resolve roles for {c} from the authoritative directory on each request or from a short cache, and ignore role claims supplied by the caller."),
        ("An administrative interface of {c} is reachable from the same network as ordinary callers and relies on a single shared password.",
         "Move the administrative interface of {c} behind a separate listener with strong authentication, network restriction and per-user accounts."),
        ("{c} runs with broader permissions than its function needs, so a flaw in handling {a} yields access to unrelated resources.",
         "Reduce the permissions of {c} to the minimum for {a}, drop capabilities it does not use and review the grants on a schedule."),
        ("A confused-deputy path lets a low-privilege caller ask {c} to act on {a} using the privileges of {p}.",
         "Pass the caller's authority through to {c} and evaluate the original caller's rights, never those of {p}, for every delegated action."),
        ("Multi-tenant separation in {c} depends on a request header that clients can set, allowing one tenant to act in another's scope.",
         "Derive the tenant for {c} from the verified credential, ignore client-supplied tenant headers and test cross-tenant requests in CI."),
        ("A privileged maintenance task of {c} can be triggered through a queue message that any producer on the bus may publish.",
         "Restrict who can publish maintenance messages that {c} acts on, sign them and require an authorised approver for destructive operations."),
    ),
    "AG:autonomy": (
        ("{c} can act on {a} without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.",
         "Require explicit human approval in {c} for actions above a defined impact threshold, and bind each approval to the exact action it covers."),
        ("The goal or instruction set of {c} can be changed through content it reads, steering it toward actions its operators never intended.",
         "Keep the goals of {c} in signed configuration that content cannot alter, and refuse plan changes that originate from retrieved text."),
        ("{c} runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.",
         "Set hard limits on steps, tool calls, runtime and spend for {c}, stop on breach and report the stop reason to the operator."),
        ("Delegation from {p} to {c} carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.",
         "Issue narrowly scoped, short-lived delegation grants to {c} and verify scope on every action instead of inheriting the parent session."),
        ("Memory written by {c} is trusted on later runs, so one poisoned entry changes the behaviour of every future task.",
         "Tag memory entries with provenance and trust level, sanitise them on read and let operators review and expire entries written by {c}."),
        ("{c} retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.",
         "Make the actions of {c} idempotent with request keys, cap retries and require confirmation before repeating any action with external effects."),
        ("{c} can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.",
         "Remove the ability of {c} to start other agents unless an operator pre-registers them, and enforce a global ceiling on active agents."),
    ),
    "AG:tool": (
        ("{c} invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed.",
         "Validate every argument against the tool schema in {c} before the call, enforce allowlists of values and reject free-form commands."),
        ("A tool description supplied by a connected server is trusted by {c} verbatim, letting a malicious description redirect which tool is called and why.",
         "Pin approved tool definitions by digest in {c}, show changes to operators for review and ignore descriptions that differ from the pinned copy."),
        ("{c} holds one credential that grants every tool, so the compromise of any single tool call exposes all connected systems.",
         "Issue per-tool, short-lived credentials to {c} scoped to one action each, and revoke them automatically after use."),
        ("Tool results returned to {c} are fed back into the next prompt without sanitising, so a result can carry instructions for the agent.",
         "Treat tool results as data in {c}: delimit them, strip instruction-like content and never let results change the tool allowlist."),
        ("An attacker chains two individually safe tools through {c} to reach an outcome neither was approved for, such as an export followed by an upload.",
         "Define forbidden tool sequences for {c}, evaluate each call in the context of the previous ones and require approval for risky combinations."),
        ("{c} does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives.",
         "Apply per-task and per-tool quotas to {c}, alert on unusual call patterns and block calls once a cost ceiling is reached."),
        ("Tool calls made by {c} are not tied to the end user, so the tool server cannot tell whose authority a request carries.",
         "Propagate a signed end-user context with each tool call from {c} and make the tool server authorise against it, not against the agent identity."),
    ),
    "LLM:inject": (
        ("Instructions hidden in {a} reach the prompt of {c} and override its system guidance, because content and instructions share one context.",
         "Separate instructions from content in the prompts of {c}, delimit untrusted text and run an injection classifier before the model sees it."),
        ("A user message crafted to look like a system directive persuades {c} to disclose its configuration or ignore its rules.",
         "Keep the system guidance for {c} out of reach of user text, test against known jailbreak patterns in CI and refuse requests that reference hidden instructions."),
        ("Indirect injection through documents retrieved for {c} lets the author of a retrieved page steer the answer without ever talking to the system.",
         "Score retrieved passages for instruction-like content before {c} uses them, attribute every passage to its source and cap how much any one source contributes."),
        ("Encoded or multilingual payloads bypass the keyword filter in front of {c}, which only checks plain English text.",
         "Normalise and decode inputs before filtering in {c}, apply semantic checks instead of keyword lists and review filter misses weekly."),
        ("{c} passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.",
         "Re-screen conversation history on each turn in {c}, expire old turns and mark which turns came from untrusted sources."),
        ("Prompt content logged by {p} is later replayed to {c} for evaluation, carrying planted instructions into a trusted context.",
         "Mark replayed prompts as untrusted when {c} processes them, and exclude logged content from any privileged instruction slot."),
        ("An attacker splits a payload across several messages so that no single message trips the filter in front of {c}.",
         "Evaluate the accumulated conversation in {c} as a whole, track cumulative risk and reset trust when it crosses a threshold."),
        ("{c} follows links and files named in {a}, which turns a harmless-looking request into a fetch of attacker-controlled content.",
         "Restrict what {c} may fetch to an allowlist of domains and types, fetch through a sandbox and present the results as untrusted data."),
    ),
    "LLM:poison": (
        ("Records written into {c} by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.",
         "Record provenance for every entry in {c}, require review for low-trust sources and exclude unreviewed entries from retrieval and training."),
        ("Fine-tuning data assembled from {c} is not checked for outliers or duplicates, so a small batch of crafted examples changes model behaviour.",
         "Screen training data from {c} for duplicates, outliers and trigger patterns, hold out a clean evaluation set and compare behaviour before every release."),
        ("Embeddings stored by {c} can be crowded with near-duplicate vectors that win similarity searches for chosen queries.",
         "Limit how many near-duplicate vectors one source can add to {c}, monitor retrieval for sudden dominance and re-rank with source reputation."),
        ("Anyone who can write to the ingestion path of {c} can slip in documents that contradict authoritative sources.",
         "Restrict write access to the ingestion path of {c}, sign documents from authoritative sources and prefer them when answers conflict."),
        ("Evaluation labels consumed from {c} are produced by a judge model that can itself be influenced by planted traces.",
         "Calibrate the judge on a human-labelled subset from {c}, rotate judge prompts and flag results that drift from the human baseline."),
        ("A delayed trigger planted in {a} on {c} changes behaviour only after a date or phrase, so pre-release testing never sees it.",
         "Scan {a} on {c} for trigger-like strings, test with date and phrase perturbations and keep immutable snapshots for rollback."),
    ),
    "LLM:theft": (
        ("Systematic queries against {c} let an attacker approximate the behaviour of the model and train a copy.",
         "Rate-limit and profile query patterns against {c}, add output perturbation for anomalous clients and watermark responses."),
        ("Model weights or adapters served by {c} are readable by operators and by any process sharing the host.",
         "Store the weights for {c} encrypted with keys in a hardware-backed service, restrict loading to the serving identity and audit every access."),
        ("Verbose responses from {c} expose token probabilities and intermediate scores that speed up extraction.",
         "Remove probability and score fields from external responses of {c} unless a contract requires them, and round any that remain."),
        ("A shared API key for {c} is distributed to several teams, so a leak lets outsiders run unlimited inference.",
         "Issue per-team keys for {c} with quotas and expiry, and revoke them automatically when usage deviates from the team's profile."),
    ),
    "OI": (
        ("Model output from {c} is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.",
         "Encode model output from {c} for its destination, render it as text by default and apply a content security policy that blocks inline script."),
        ("Text generated by {c} is placed into a database query or shell argument without parameterisation, allowing the model to be steered into injection.",
         "Never build queries or commands from model output of {c}: use parameterised calls and fixed argument vectors with allowlisted values."),
        ("{c} emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.",
         "Validate URLs from {c} against an allowlist, resolve and block private ranges before fetching, and fetch from a restricted network."),
        ("Structured output from {c} is trusted by {p} as already validated, so a malformed field flows straight into business logic.",
         "Validate the output of {c} against a strict schema in {p}, treat it as untrusted input and reject anything that fails."),
        ("Markdown or HTML produced by {c} contains remote images that leak data when a client renders it.",
         "Strip remote resources from the output of {c} before display, proxy images through a controlled service and disable automatic loading."),
        ("File paths or names produced by {c} are used to write files, letting crafted output reach locations outside the intended directory.",
         "Generate file names for {c} on the server, confine writes to a sandbox directory and reject any path component supplied by the model."),
    ),
    "MI": (
        ("{c} states carrier rules and customs requirements as fact without grounding them in a cited source, so an operator may act on an invented rule.",
         "Require {c} to cite a retrievable source for each factual claim, show the citations and decline to answer when none is found."),
        ("Confident wording from {c} hides low retrieval quality, so operators cannot tell a grounded answer from a guess.",
         "Expose retrieval strength alongside the answers of {c} and switch to an explicit uncertainty message below a threshold."),
        ("Outputs from {c} flow into decisions without a review step, so one wrong answer is repeated across many shipments.",
         "Route decisions based on the output of {c} through human review above a risk threshold and audit a subset of the remainder."),
        ("{c} fabricates reference numbers and clause citations that look real, which operators then paste into official documents.",
         "Verify identifiers and citations produced by {c} against authoritative systems before display, and mark unverifiable ones clearly."),
        ("Stale data in the knowledge base lets {c} present superseded tariffs as current, causing wrong quotes.",
         "Stamp every source used by {c} with an effective date, suppress answers built on expired sources and alert owners when content ages out."),
    ),
    "TE": (
        ("{c} speaks with an authoritative tone about customs and legal matters, and operators may defer to it without checking.",
         "Label the output of {c} as machine generated, state its limits plainly and avoid wording that claims professional authority."),
        ("{c} adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.",
         "Disclose that {c} is an automated agent at the start of each session and avoid human-like names or personal claims."),
        ("Persuasive phrasing from {c} pushes operators to approve proposals quickly, which reduces careful review.",
         "Neutralise urgency and pressure wording in {c}, present alternatives with their trade-offs and require a deliberate action to approve."),
        ("{c} builds rapport over long sessions and starts to share unprompted details about earlier operators.",
         "Isolate sessions of {c} per operator, forbid recall of other operators' details and review long sessions for rapport patterns."),
        ("{c} claims certainty it does not have when summarising shipment risk, and customers rely on the stated confidence.",
         "Attach calibrated confidence and the basis for each claim to the output of {c}, and block unqualified guarantees in customer-facing text."),
    ),
}

# OWASP Reference cell per AI scenario (index-aligned with SCENARIOS); LLM references use the 2026 keys.
AI_REFERENCES = {
    "AG:autonomy": ("ASI-01", "ASI-01", "ASI-10", "ASI-03", "ASI-06", "ASI-08", "ASI-10"),
    "AG:tool": ("ASI-02", "MCP-03", "ASI-03", "ASI-02", "ASI-02", "ASI-08", "ASI-03"),
    "LLM:inject": ("OWASP LLM01:2026",) * 8,
    "LLM:poison": ("OWASP LLM05:2026", "OWASP LLM05:2026", "OWASP LLM09:2026", "OWASP LLM05:2026", "OWASP LLM05:2026", "OWASP LLM05:2026"),
    "LLM:theft": ("OWASP LLM06:2026", "OWASP LLM06:2026", "OWASP LLM06:2026", "OWASP LLM06:2026"),
    "OI": ("OWASP LLM10:2026",) * 6,
    "MI": ("OWASP LLM07:2026",) * 5,
    "TE": ("ASI-09",) * 5,
}

# The three net-new pattern findings (Phase 3.6 emits at most one per pattern): prefix AGP, ids 01 to 03.
AGP_ROWS = (
    ("agent_collusion", "worker-2", "ASI-07",
     "Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour.",
     "Monitor combined activity across agents, set aggregate budgets for groups of workers and separate the channels that agents can use to coordinate. Recommended controls: behavioural baselining of the collective agent system and alerts on coordinated bursts."),
    ("temporal_attack", "scheduler-1", "ASI-06",
     "State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run weeks later, after the original entry has left review and the context that explained it is gone.",
     "Expire persisted instructions, re-review any state that scheduled runs read and compare behaviour against pre-run snapshots. Recommended controls: provenance attestation for stored state and audit trails for every memory write."),
    ("emergent_behavior", "planner-agent", "ASI-08",
     "Interacting planning and routing agents amplify each other's outputs through feedback until their combined behaviour diverges from what any single agent was tested for, and per-agent safety checks never see the divergence.",
     "Add fail-safe stop conditions for the planning loop, bound the actions each cycle may take and evaluate collective behaviour in staging. Recommended controls: bounded action scopes and behavioural baselining of the whole system."),
    # Rows 4 to 7 serve only the variant worlds (T040), which need more than three AGP findings; the base profiles never reach them.
    ("trust_exploitation", "worker-2", "ASI-09",
     "Operators and downstream agents start to accept worker output without checking it because earlier results were reliable, so one confidently stated wrong result passes straight into shipments and documents.",
     "Require evidence for each recommendation, sample outputs for independent review and show uncertainty to operators so that reliance stays proportionate. Recommended controls: confidence attestation and periodic human spot checks."),
    ("resource_competition", "tool-server-1", "ASI-04",
     "Several agents compete for the same carrier rate and booking tools, and the heaviest user starves the others, so low priority work stalls or is retried until a limit is hit.",
     "Give each agent a quota on shared tools, queue work fairly and alert when one agent holds a tool for longer than its slot. Recommended controls: per-agent rate limits and fair scheduling."),
    ("communication_vulnerability", "planner-agent", "ASI-07",
     "Messages between the planner and its workers travel over a shared channel with no per-sender signature, so a compromised participant can forge or replay instructions that other agents act on.",
     "Sign each inter-agent message with the sender's key, include a nonce and reject replays. Recommended controls: authenticated channels between agents and message integrity checks."),
    ("emergent_behavior", "intake-agent", "ASI-08",
     "The intake and planning agents adjust to each other's phrasing over many runs until requests are structured in ways no test covered, and the drift is invisible in any single exchange.",
     "Track the distribution of structured requests over time and alert on drift. Recommended controls: behavioural baselining and periodic replay against a fixed test set."),
)

CONTEXT_CLAUSES = (
    "{c} runs in the {z} and exchanges {a} with {p} over {proto}, so anything able to reach {p} can also reach this weakness.",
    "{p} trusts {c} to pass {a} along unchanged, which removes the second chance to catch the problem downstream.",
    "The weakness sits at layer {layer} of the stack, so every workflow that depends on {a} inherits the exposure.",
    "Because {c} serves the {z}, a single failure here reaches each consumer of {a} at once.",
    "The exposure follows from how {c} receives {a} from {p} and hands them to the next stage without an independent check.",
)
IMPACT_CLAUSES = {
    "S": ("Until the credential is revoked the attacker acts with the victim's authority, and the audit trail attributes the actions to the victim.",
          "A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic."),
    "T": ("Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source.",
          "The change can persist across restarts and restores, which makes the original state difficult to prove and to recover."),
    "R": ("Without reliable records an investigation cannot establish who acted, so disputes about responsibility stay unresolved.",
          "Incident responders lose the sequence of events, which delays containment and weakens any later accountability claim."),
    "I": ("The exposed material can be reused for follow-on attacks and may trigger notification duties if it covers customer data.",
          "Disclosure is silent, so the affected parties learn about it only when the information is misused."),
    "D": ("Operators lose the ability to book or amend shipments while the condition lasts, and recovery depends on manual intervention.",
          "The outage propagates to dependent agents, which stall or retry and prolong the disruption."),
    "E": ("The caller gains rights that were never granted, which allows reading and changing data across tenants and approvals.",
          "Once the boundary is crossed the attacker can reach administrative functions and persist there."),
    "AG": ("The agent acts at machine speed on behalf of the operator, so a single manipulated decision can cause many unwanted changes before a person notices.",
           "Actions taken by the agent look legitimate in the logs, which slows detection and complicates rollback."),
    "LLM": ("The answers or side effects of the model then serve the attacker's goal, and the behaviour can be repeated against every user of the component.",
            "The failure is probabilistic, so it may pass pre-release testing and appear only under adversarial input."),
    "OI": ("The unsafe output reaches an interpreter that trusts it, turning a text generation problem into code or request execution.",
           "Downstream components cannot tell the model's output from validated input, so no later layer is likely to catch it."),
    "MI": ("Operators act on the wrong information, and the error is copied into shipments, documents and customer communication.",
           "The mistake looks authoritative, so it is rarely questioned until a downstream party objects."),
    "TE": ("People defer to the agent more than its reliability justifies, which weakens the human oversight the design depends on.",
           "The effect builds over time as users come to rely on the agent's tone instead of its evidence."),
}
LIKELIHOOD_WHY = {
    "HIGH": "the path needs no special position and uses interfaces that are exposed by design",
    "MEDIUM": "the path needs a foothold on a neighbouring service or a prepared request",
    "LOW": "the path needs several preconditions to line up, such as insider access or a rare timing window",
}
IMPACT_WHY = {
    "HIGH": "the affected data or action is central to shipment handling and hard to reverse",
    "MEDIUM": "the effect is bounded to one workflow or one tenant and can be corrected with effort",
    "LOW": "the effect is contained and easy to reverse once it is noticed",
}
MITIGATION_CLAUSES = (
    "Add a regression test for this abuse path to the CI suite and alert through {o} when the control fires.",
    "Verify the control in a pre-production exercise and review it again after any change to {c}.",
    "Name an owner for this control, review it each quarter and route violations to {o} so that responders see them in one place.",
    "Track coverage of this control as a release criterion for {c} and record any exception with an expiry date.",
    "Confirm the fix with a targeted test against {c}, and keep the evidence with the change record for later audits.",
)

# --------------------------------------------------------------------------- the world
# A profile fixes the scale. The base profile is the S-4 base set; the gated profile is the small,
# Mermaid-free subset. Both build through the same code, so they cannot drift apart.
RESOLVED_BASE = (  # (prefix, component, reason, last risk level)
    ("S", "legacy-batch-1", "Component 'legacy-batch-1' removed from architecture", "High"),
    ("T", "legacy-batch-1", "Component 'legacy-batch-1' removed from architecture", "Medium"),
    ("I", "report-export-2", "Component 'report-export-2' removed from architecture", "High"),
    ("D", "report-export-2", "Component 'report-export-2' removed from architecture", "Medium"),
    ("R", "edge-gateway", "Threat category no longer applicable to 'edge-gateway' (request logging moved to trace-collector)", "Low"),
    ("LLM", "summarizer-llm", "Threat category no longer applicable to 'summarizer-llm' (free-text fields removed from prompts)", "Medium"),
)
RESOLVED_GATED = (
    ("S", "legacy-batch-1", "Component 'legacy-batch-1' removed from architecture", "High"),
    ("I", "report-export-2", "Component 'report-export-2' removed from architecture", "Medium"),
    ("R", "edge-gateway", "Threat category no longer applicable to 'edge-gateway' (request logging moved to trace-collector)", "Low"),
)
RETIRED_COMPONENTS = {  # removed since the baseline: only the resolved findings name them
    "legacy-batch-1": ("Process", 4, "Agent Runtime Zone", "nightly manifest exports", "batch credential"),
    "report-export-2": ("Process", 7, "Agent Runtime Zone", "exported shipment reports", "export credential"),
}

PROFILES = {
    "base": {
        "components": None,
        "counts": {"S": 42, "T": 46, "R": 32, "I": 46, "D": 38, "E": 34,
                   "AG": 44, "AGP": 3, "LLM": 58, "OI": 28, "MI": 20, "TE": 17},
        "resolved": RESOLVED_BASE,
        "new_pm": 100, "updated_pm": 60,  # per mille of the carried findings
        "critical_min": 56,
        "dates": {"threats": "2026-10-19", "baseline": "2026-09-21", "scores": "2026-10-20", "controls": "2026-10-21"},
        "run_ids": {"threats": "2026-10-19T09-30-00", "baseline": "2026-09-21T09-12-00"},
        "trees": True,
        "mermaid": True,
        "architecture_file": "docs/security/architecture.md",
    },
    "gated": {
        "components": ("client-portal", "edge-gateway", "auth-broker", "intake-agent", "planner-agent", "worker-2",
                       "tool-server-1", "model-gateway", "vector-store-a", "audit-ledger"),
        "counts": {"S": 4, "T": 4, "R": 3, "I": 4, "D": 3, "E": 3,
                   "AG": 6, "AGP": 1, "LLM": 7, "OI": 3, "MI": 2, "TE": 2},
        "resolved": RESOLVED_GATED,
        "new_pm": 150, "updated_pm": 100,
        "critical_min": 6,
        "dates": {"threats": "2026-10-19", "baseline": "2026-09-21", "scores": "2026-10-20", "controls": "2026-10-21"},
        "run_ids": {"threats": "2026-10-19T09-30-00", "baseline": "2026-09-21T09-12-00"},
        "trees": False,
        "mermaid": False,
        "architecture_file": "docs/security/architecture.md",
    },
}

CORRELATION_RULES = (  # (STRIDE prefix, AI sub-agent, rule name): ADR dispatch-rules CR-1 .. CR-5
    ("T", "LLM:poison", "CR-1"), ("E", "AG:autonomy", "CR-2"), ("I", "LLM:inject", "CR-3"),
    ("R", "AG:autonomy", "CR-4"), ("D", "AG:tool", "CR-5"),
)
GROUP_LABEL = {
    "S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Info-Disclosure", "D": "Denial-of-Service",
    "E": "Privilege-Escalation", "AG:autonomy": "Agent-Autonomy", "AG:tool": "Tool-Abuse",
    "LLM:inject": "Prompt-Injection", "LLM:poison": "Data-Poisoning",
}
CATEGORY_TITLE = {
    "S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information Disclosure",
    "D": "Denial of Service", "E": "Elevation of Privilege",
    "AG": "Agentic", "AGP": "Agentic", "TE": "Agentic", "LLM": "LLM", "OI": "LLM", "MI": "LLM",
}
STRIDE_PREFIXES_ORDER = ("S", "T", "R", "I", "D", "E")
TABLE_ORDER = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "TE", "LLM", "OI", "MI")  # where rows appear in Section 3 and 4
RISK_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Note": 0}
RISK_MATRIX = {  # (likelihood, impact) -> OWASP 3x3 risk level
    ("LOW", "HIGH"): "Medium", ("MEDIUM", "HIGH"): "High", ("HIGH", "HIGH"): "Critical",
    ("LOW", "MEDIUM"): "Low", ("MEDIUM", "MEDIUM"): "Medium", ("HIGH", "MEDIUM"): "High",
    ("LOW", "LOW"): "Note", ("MEDIUM", "LOW"): "Low", ("HIGH", "LOW"): "Medium",
}
LI_WEIGHTS = {  # prefix -> (likelihood LOW/MEDIUM/HIGH, impact LOW/MEDIUM/HIGH), in percent
    "S": ((25, 45, 30), (15, 40, 45)), "T": ((25, 45, 30), (15, 40, 45)), "R": ((30, 50, 20), (35, 45, 20)),
    "I": ((25, 45, 30), (15, 40, 45)), "D": ((20, 45, 35), (20, 50, 30)), "E": ((30, 45, 25), (10, 35, 55)),
    "AG": ((20, 45, 35), (10, 35, 55)), "AGP": ((0, 100, 0), (0, 100, 0)), "TE": ((25, 45, 30), (15, 40, 45)),
    "LLM": ((20, 40, 40), (10, 35, 55)), "OI": ((25, 45, 30), (10, 35, 55)), "MI": ((25, 45, 30), (15, 40, 45)),
}
LEVELS = ("LOW", "MEDIUM", "HIGH")
STATUS_NEW, STATUS_UPDATED, STATUS_UNCHANGED = "NEW", "UPDATED", "UNCHANGED"


def _stride_eligible(prefix: str, comp: dict) -> bool:
    if comp["dfd"] == "External Entity":
        return prefix in ("S", "R")
    if comp["dfd"] == "Data Store":
        return prefix in ("T", "I", "D") or (prefix == "R" and "log" in comp["traits"])
    return True


def _ai_subs(prefix: str, comp: dict) -> tuple:
    if prefix == "AG":
        return tuple(code for code in comp["ai"] if code.startswith("AG:"))
    if prefix == "LLM":
        return tuple(code for code in comp["ai"] if code.startswith("LLM:"))
    return (prefix,) if prefix in comp["ai"] else ()


def _slots(prefix: str, comps: list) -> list:
    """Every (component, sub-agent) pair that may carry findings of a prefix, in inventory order."""
    out = []
    for comp in comps:
        if prefix in STRIDE_PREFIXES_ORDER:
            if _stride_eligible(prefix, comp):
                out.append((comp, None))
        else:
            for sub in _ai_subs(prefix, comp):
                out.append((comp, sub))
    return out


def _risk_of(like: str, imp: str) -> str:
    return RISK_MATRIX[(like, imp)]


def _draw3(rng: "Rng", weights: tuple) -> int:
    roll = rng.below(100)
    return 0 if roll < weights[0] else 1 if roll < weights[0] + weights[1] else 2


def pattern_of(prefix: str, sub, comp: dict) -> str:
    """The agentic pattern Phase 3.6 would classify a finding under; most findings have none."""
    name = comp["name"]
    if prefix == "S" and comp["dfd"] == "Process" and comp["layer"] == 3:
        return "trust_exploitation"
    if prefix == "D" and name in ("queue-a2", "planner-agent", "router-agent", "worker-2", "worker-3", "tool-server-1"):
        return "resource_competition"
    if prefix in ("T", "I") and name == "queue-a2":
        return "communication_vulnerability"
    if prefix == "AG" and sub == "AG:autonomy" and name in ("scheduler-1", "planner-agent", "policy-engine"):
        return "temporal_attack" if name == "scheduler-1" else "emergent_behavior"
    if prefix == "AG" and sub == "AG:tool" and name in ("worker-2", "worker-3"):
        return "agent_collusion"
    if prefix == "TE":
        return "trust_exploitation"
    return "none"


def build_world(profile_name: str) -> dict:
    """The deterministic model every part renders from. Cached per profile, so parts stay independent."""
    cached = _WORLD_CACHE.get(profile_name)
    if cached is not None:
        return cached
    self_test_cvss()
    profile = PROFILES[profile_name]
    wanted = profile["components"]
    comps = []
    for row in COMPONENT_ROWS + (VARIANT_COMPONENT_ROWS if wanted is not None else ()):
        if wanted is not None and row[0] not in wanted:
            continue
        name, dfd, layer, zone, ai, traits, desc, asset, tok = row
        comps.append({"name": name, "dfd": dfd, "layer": layer, "zone": zone, "ai": ai, "traits": traits,
                      "desc": desc, "asset": asset, "tok": tok, "index": len(comps)})
    by_name = {comp["name"]: comp for comp in comps}
    flows = [flow for flow in FLOW_ROWS if flow[0] in by_name and flow[1] in by_name]
    for comp in comps:
        inbound = [flow for flow in flows if flow[1] == comp["name"]]
        outbound = [flow for flow in flows if flow[0] == comp["name"]]
        comp["peers"] = [(flow[0], flow[3]) for flow in inbound] + [(flow[1], flow[3]) for flow in outbound]
    zones = []
    for zone_name, level, reach in ZONES:
        members = [comp["name"] for comp in comps if comp["zone"] == zone_name]
        if members:
            zones.append({"name": zone_name, "level": level, "reach": reach, "members": members})
    observer = "trace-collector" if "trace-collector" in by_name else "audit-ledger" if "audit-ledger" in by_name else "the monitoring pipeline"
    world = {"profile": profile_name, "cfg": profile, "components": comps, "by_name": by_name, "flows": flows,
             "zones": zones, "observer": observer}
    _allocate_findings(world)
    _number_findings(world)
    _assign_levels(world)
    _write_texts(world)
    _build_groups(world)
    _WORLD_CACHE[profile_name] = world
    return world


_WORLD_CACHE: dict = {}


def _allocate_findings(world: dict) -> None:
    """Decide how many findings of each prefix sit on which component and sub-agent."""
    comps, counts = world["components"], world["cfg"]["counts"]
    explicit = world["cfg"].get("explicit")
    if explicit is not None:  # a variant world (T040) names every finding: (prefix, component, sub-agent)
        findings, agp_seen = [], 0
        for prefix, comp_name, sub in explicit:
            entry = {"prefix": prefix, "sub": sub, "comp": comp_name, "cidx": world["by_name"][comp_name]["index"]}
            if prefix == "AGP":
                entry["agp"] = agp_seen
                agp_seen += 1
            findings.append(entry)
        world["findings"] = findings
        return
    rng = Rng("world/%s/allocate" % world["profile"])
    quota = {}  # (prefix, component name, sub) -> findings
    anchors_needed = {}
    # Anchors first: every AI-bearing component gets one correlatable STRIDE + AI pair, so that it can form a group.
    for comp in comps:
        options = [rule for rule in CORRELATION_RULES
                   if rule[1] in comp["ai"] and _stride_eligible(rule[0], comp)]
        if not options:
            continue
        picked = options[comp["index"] % len(options)]  # rotate, so the rules spread across the inventory
        stride_prefix, sub, _ = picked
        ai_prefix = sub.split(":")[0]
        for key in ((stride_prefix, comp["name"], None), (ai_prefix, comp["name"], sub)):
            quota[key] = quota.get(key, 0) + 1
            anchors_needed[key[0]] = anchors_needed.get(key[0], 0) + 1
    # One component also gets both STRIDE sides of the two agent-autonomy rules, so every profile holds a group that
    # spans three categories (CR-2 and CR-4 merge into one group, as the correlation algorithm specifies).
    cross = next((comp for comp in comps if comp["dfd"] == "Process" and "AG:autonomy" in comp["ai"]), None)
    if cross is not None:
        for key in (("E", cross["name"], None), ("R", cross["name"], None), ("AG", cross["name"], "AG:autonomy")):
            if key not in quota:
                quota[key] = 1
    for prefix in PREFIX_ORDER:
        if prefix == "AGP":
            continue
        total = counts[prefix]
        slots = _slots(prefix, comps)
        if not slots:
            raise ValueError("no component can carry %s findings in profile %s" % (prefix, world["profile"]))
        have = sum(count for (p, _, _), count in quota.items() if p == prefix)
        if have > total:
            raise ValueError("anchors for %s exceed its count in profile %s" % (prefix, world["profile"]))
        weights = []
        for comp, sub in slots:
            weight = 3 if comp["name"] in ("edge-gateway", "intake-agent", "planner-agent", "tool-server-1", "summarizer-llm") else 2
            if (prefix, comp["name"], sub) in quota:
                weight += 1
            weights.append(weight)
        # Give every slot one finding when the count allows it, then spread the rest by weight.
        if total - have >= len(slots) - sum(1 for comp, sub in slots if (prefix, comp["name"], sub) in quota):
            for comp, sub in slots:
                key = (prefix, comp["name"], sub)
                if key not in quota:
                    quota[key] = 1
                    have += 1
        wsum = sum(weights)
        while have < total:
            roll = rng.below(wsum)
            for (comp, sub), weight in zip(slots, weights):
                if roll < weight:
                    key = (prefix, comp["name"], sub)
                    quota[key] = quota.get(key, 0) + 1
                    break
                roll -= weight
            have += 1
    findings = []
    for prefix in PREFIX_ORDER:
        if prefix == "AGP":
            continue
        for comp, sub in _slots(prefix, comps):
            for _ in range(quota.get((prefix, comp["name"], sub), 0)):
                findings.append({"prefix": prefix, "sub": sub, "comp": comp["name"], "cidx": comp["index"]})
    # AGP: the (at most three) net-new pattern findings, on the components the pattern rules name.
    for position in range(world["cfg"]["counts"]["AGP"]):
        pattern, comp_name, ref, _, _ = AGP_ROWS[position]
        if comp_name not in world["by_name"]:
            comp_name = "planner-agent" if "planner-agent" in world["by_name"] else comps[0]["name"]
        findings.append({"prefix": "AGP", "sub": None, "comp": comp_name, "cidx": world["by_name"][comp_name]["index"],
                         "agp": position})
    world["findings"] = findings


def _number_findings(world: dict) -> None:
    """IDs, statuses and the gaps that RESOLVED baseline findings leave behind."""
    cfg = world["cfg"]
    resolved_by_prefix = {}
    for prefix, comp_name, reason, risk in cfg["resolved"]:
        resolved_by_prefix.setdefault(prefix, []).append((comp_name, reason, risk))
    for prefix in PREFIX_ORDER:
        group = [f for f in world["findings"] if f["prefix"] == prefix]
        group.sort(key=lambda f: (f["cidx"], f["sub"] or ""))
        if prefix == "AGP":
            for number, finding in enumerate(group, start=1):
                finding.update({"num": number, "status": STATUS_UNCHANGED})
            continue
        gaps_wanted = len(resolved_by_prefix.get(prefix, ()))
        fresh = round_half(len(group) * cfg["new_pm"], 1000)
        ranked = sorted(range(len(group)), key=lambda i: label_hash("new:%s:%d" % (prefix, i)))
        new_positions = set(ranked[:fresh])  # membership tests only; never iterated
        carried = [f for i, f in enumerate(group) if i not in new_positions]
        newcomers = [f for i, f in enumerate(group) if i in new_positions]
        span = len(carried) + gaps_wanted
        gaps = []
        for k in range(gaps_wanted):
            candidate = 1 + label_below("gap:%s:%d" % (prefix, k), max(span - 2, 1))
            while candidate in gaps:
                candidate += 1
            gaps.append(candidate)
        gaps.sort()
        numbers = [n for n in range(1, span + 1) if n not in gaps]
        for finding, number in zip(carried, numbers):
            finding.update({"num": number, "status": STATUS_UNCHANGED})
        updated = round_half(len(carried) * cfg["updated_pm"], 1000)
        order = sorted(range(len(carried)), key=lambda i: label_hash("upd:%s:%d" % (prefix, i)))
        for i in order[:updated]:
            carried[i]["status"] = STATUS_UPDATED
        for offset, finding in enumerate(newcomers, start=1):
            finding.update({"num": span + offset, "status": STATUS_NEW})
        world.setdefault("resolved_numbers", {})[prefix] = gaps
    for finding in world["findings"]:
        finding["id"] = finding_id_text(finding["prefix"], finding["num"])
    world["findings"].sort(key=lambda f: prefix_rank(f["id"]))
    world["resolved"] = []
    for prefix, comp_name, reason, risk in cfg["resolved"]:
        position = [r for r in cfg["resolved"] if r[0] == prefix].index((prefix, comp_name, reason, risk))
        number = world["resolved_numbers"][prefix][position]
        world["resolved"].append({"prefix": prefix, "sub": "LLM:inject" if prefix == "LLM" else None, "comp": comp_name,
                                  "num": number, "id": finding_id_text(prefix, number), "reason": reason, "risk": risk})
    world["resolved"].sort(key=lambda r: prefix_rank(r["id"]))


def round_half(numerator: int, denominator: int) -> int:
    return half_up(numerator, denominator)


def _assign_levels(world: dict) -> None:
    """Likelihood, impact, risk level and the agentic pattern of every finding."""
    rng = Rng("world/%s/levels" % world["profile"])
    for finding in world["findings"]:
        weights = LI_WEIGHTS[finding["prefix"]]
        finding["like"] = LEVELS[_draw3(rng, weights[0])]
        finding["imp"] = LEVELS[_draw3(rng, weights[1])]
    floor = world["cfg"]["critical_min"]
    criticals = [f for f in world["findings"] if (f["like"], f["imp"]) == ("HIGH", "HIGH")]
    if len(criticals) < floor:
        # Promote the highest-ranked High findings, in a label-hash order, until the floor holds.
        pool = [f for f in world["findings"] if _risk_of(f["like"], f["imp"]) == "High" and f["prefix"] != "AGP"]
        pool.sort(key=lambda f: label_hash("promote:" + f["id"]))
        for finding in pool[: floor - len(criticals)]:
            finding["like"], finding["imp"] = "HIGH", "HIGH"
    by_name = world["by_name"]
    for finding in world["findings"]:
        finding["risk"] = _risk_of(finding["like"], finding["imp"])
        comp = by_name[finding["comp"]]
        finding["layer"] = comp["layer"]
        if finding["prefix"] == "AGP":
            finding["pattern"] = AGP_ROWS[finding["agp"]][0]
        else:
            finding["pattern"] = pattern_of(finding["prefix"], finding["sub"], comp)


def _text_slots(world: dict, comp: dict, key: str) -> dict:
    peers = comp["peers"] or [("the neighbouring service", "an internal channel")]
    pick = peers[label_below(key + "/peer", len(peers))]
    return {"c": comp["name"], "p": pick[0], "a": comp["asset"], "t": comp["tok"], "z": comp["zone"],
            "o": world["observer"], "proto": pick[1], "layer": LAYER_NAME[comp["layer"]]}


def _scenario_key(prefix: str, sub) -> str:
    return sub if sub else prefix


def compose_text(world: dict, comp: dict, prefix: str, sub, label: str, used: dict, rating=None) -> tuple:
    """(threat, mitigation, threat summary, mitigation summary, OWASP reference) for one finding."""
    key = _scenario_key(prefix, sub)
    rows = SCENARIOS[key]
    slot_key = (comp["name"], key)
    ordinal = used.get(slot_key, 0)
    used[slot_key] = ordinal + 1
    index = (label_below("scenario:%s:%s" % slot_key, len(rows)) + ordinal) % len(rows)
    slots = _text_slots(world, comp, label)
    core_t, core_m = rows[index]
    family = prefix if prefix in IMPACT_CLAUSES else "AG" if prefix in ("AGP", "TE") else "LLM"
    context = CONTEXT_CLAUSES[label_below(label + "/ctx", len(CONTEXT_CLAUSES))].format(**slots)
    impact = IMPACT_CLAUSES[family][label_below(label + "/imp", 2)]
    verify = MITIGATION_CLAUSES[label_below(label + "/mit", len(MITIGATION_CLAUSES))].format(**slots)
    parts = [core_t.format(**slots), context, impact]
    if rating is not None:
        like, imp = rating
        parts.append("Rated %s likelihood because %s, and %s impact because %s." % (like, LIKELIHOOD_WHY[like], imp, IMPACT_WHY[imp]))
    threat = " ".join(parts)
    mitigation = " ".join((core_m.format(**slots), verify))
    refs = AI_REFERENCES.get(key)
    return threat, mitigation, clip(core_t.format(**slots), 112), clip(core_m.format(**slots), 150), (refs[index] if refs else "")


def _write_texts(world: dict) -> None:
    used: dict = {}
    for finding in world["findings"]:
        comp = world["by_name"][finding["comp"]]
        if finding["prefix"] == "AGP":
            _, _, ref, core_t, core_m = AGP_ROWS[finding["agp"]]
            slots = _text_slots(world, comp, finding["id"])
            threat = " ".join((core_t, CONTEXT_CLAUSES[label_below(finding["id"] + "/ctx", len(CONTEXT_CLAUSES))].format(**slots),
                               "Rated %s likelihood because %s, and %s impact because %s." % (
                                   finding["like"], LIKELIHOOD_WHY[finding["like"]], finding["imp"], IMPACT_WHY[finding["imp"]])))
            mitigation = core_m
            finding.update({"threat": threat, "mit": mitigation, "short": clip(core_t, 112), "mit_short": clip(core_m, 150), "ref": ref})
            continue
        threat, mitigation, short, mit_short, ref = compose_text(world, comp, finding["prefix"], finding["sub"], finding["id"], used,
                                                                    (finding["like"], finding["imp"]))
        finding.update({"threat": threat, "mit": mitigation, "short": short, "mit_short": mit_short, "ref": ref})
    for item in world["resolved"]:
        name = item["comp"]
        if name in world["by_name"]:
            comp = world["by_name"][name]
        else:
            dfd, layer, zone, asset, tok = RETIRED_COMPONENTS[name]
            comp = {"name": name, "dfd": dfd, "layer": layer, "zone": zone, "asset": asset, "tok": tok,
                    "peers": [("edge-gateway", "HTTPS (TLS 1.3)")], "ai": (), "traits": ()}
        threat, mitigation, short, mit_short, _ = compose_text(world, comp, item["prefix"], item["sub"], item["id"], used)
        item.update({"threat": threat, "short": short})


def _build_groups(world: dict) -> None:
    """Section 4a: one correlation group per component, merging every rule that matches there."""
    if world["cfg"].get("no_groups"):  # a variant world (T040) that sets its own groups, or has none
        for finding in world["findings"]:
            finding["group"] = None
            finding["primary"] = False
        world["groups"] = []
        return
    groups = []
    by_comp = {}
    for finding in world["findings"]:
        by_comp.setdefault(finding["comp"], []).append(finding)
    for comp in world["components"]:
        here = by_comp.get(comp["name"], [])
        members, taken, rules_hit = [], [], []
        order = sorted(range(len(CORRELATION_RULES)), key=lambda i: label_hash("rule:%s:%d" % (comp["name"], i)))
        for i in order:
            stride_prefix, sub, rule = CORRELATION_RULES[i]
            # A rule matches on category alone, so a finding that an earlier rule already put in this component's group
            # still satisfies it; the group only grows by the findings that are not in it yet.
            if not any(f["prefix"] == stride_prefix for f in here) or not any(f["sub"] == sub for f in here) or len(members) >= 6:
                continue
            stride = [f for f in here if f["prefix"] == stride_prefix and f["id"] not in taken]
            ai = [f for f in here if f["sub"] == sub and f["id"] not in taken]
            take_s = 2 if len(stride) > 1 and label_below("take-s:%s:%d" % (comp["name"], i), 10) < 3 else 1
            take_a = 2 if len(ai) > 1 and label_below("take-a:%s:%d" % (comp["name"], i), 10) < 3 else 1
            added = False
            for finding in stride[:take_s] + ai[:take_a]:
                taken.append(finding["id"])
                members.append(finding)
                added = True
            if added:
                rules_hit.append(rule)
        if not members:
            continue
        stride_members = sorted([f for f in members if f["prefix"] in STRIDE_PREFIXES_ORDER], key=lambda f: prefix_rank(f["id"]))
        ai_members = sorted([f for f in members if f["prefix"] not in STRIDE_PREFIXES_ORDER], key=lambda f: prefix_rank(f["id"]))
        ordered = stride_members + ai_members
        groups.append({"id": "CG-%d" % (len(groups) + 1), "component": comp["name"], "members": ordered,
                       "rules": rules_hit, "risk": max((f["risk"] for f in ordered), key=lambda r: RISK_RANK[r])})
    for group in groups:
        for position, finding in enumerate(group["members"]):
            finding["group"] = group["id"]
            finding["primary"] = position == 0
    for finding in world["findings"]:
        finding.setdefault("group", None)
        finding.setdefault("primary", False)
    world["groups"] = groups

# --------------------------------------------------------------------------- scores and controls
EXPLOIT_BASE = {  # four sub-scores per category: techniques, complexity, tooling, skill (0-10)
    "spoofing": (7, 7, 7, 6), "tampering": (6, 6, 5, 5), "repudiation": (4, 6, 3, 4), "info-disclosure": (7, 7, 6, 6),
    "denial-of-service": (8, 8, 7, 8), "privilege-escalation": (6, 6, 5, 5), "agentic": (6, 5, 4, 5), "llm": (8, 8, 7, 8),
}
SCALE_BASE = {  # scriptability, target scope, resources, detection difficulty (0-10)
    "spoofing": (8, 6, 8, 5), "tampering": (5, 4, 7, 4), "repudiation": (3, 3, 8, 7), "info-disclosure": (7, 6, 8, 4),
    "denial-of-service": (9, 8, 5, 3), "privilege-escalation": (6, 5, 8, 5), "agentic": (4, 5, 8, 6), "llm": (7, 7, 9, 6),
}
REACH_RANGE = {"Untrusted": (80, 100), "Semi-trusted": (40, 70), "Trusted": (10, 40)}
CVSS_METRICS = (
    ("AV", "Attack Vector (AV)", {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"},
     {"N": "Reachable over the network", "A": "Needs an adjacent network", "L": "Needs local access", "P": "Needs physical access"}),
    ("AC", "Attack Complexity (AC)", {"L": "Low", "H": "High"},
     {"L": "No special conditions", "H": "Needs specific conditions"}),
    ("PR", "Privileges Required (PR)", {"N": "None", "L": "Low", "H": "High"},
     {"N": "No privileges needed", "L": "A basic account is needed", "H": "Administrative rights are needed"}),
    ("UI", "User Interaction (UI)", {"N": "None", "R": "Required"},
     {"N": "No user action needed", "R": "A user must act"}),
    ("S", "Scope (S)", {"U": "Unchanged", "C": "Changed"},
     {"U": "Impact stays in the component", "C": "Impact crosses a boundary"}),
    ("C", "Confidentiality (C)", {"N": "None", "L": "Low", "H": "High"},
     {"N": "No disclosure", "L": "Limited disclosure", "H": "Broad disclosure"}),
    ("I", "Integrity (I)", {"N": "None", "L": "Low", "H": "High"},
     {"N": "No modification", "L": "Limited modification", "H": "Broad modification"}),
    ("A", "Availability (A)", {"N": "None", "L": "Low", "H": "High"},
     {"N": "No loss of service", "L": "Degraded service", "H": "Loss of service"}),
)
EXPLOIT_PARTS = (
    ("Known Techniques", ("Not described outside research", "Described in research", "Documented and widely used")),
    ("Attack Complexity", ("Needs chained steps", "Needs some preparation", "A single step suffices")),
    ("Tooling Availability", ("Needs custom tooling", "Tools need adaptation", "Common tools apply")),
    ("Skill Level", ("Needs deep expertise", "Intermediate skill", "Little skill needed")),
)
SCALE_PARTS = (
    ("Scriptability", ("Manual for each target", "Partly automatable", "Fully automatable")),
    ("Target Scope", ("One specific target", "A class of targets", "Every instance")),
    ("Resource Requirements", ("Needs heavy infrastructure", "Moderate resources", "Minimal resources")),
    ("Detection Difficulty", ("Readily detected", "Detectable with monitoring", "Blends with normal use")),
)


def _tier(value: int) -> int:
    return 0 if value <= 3 else 1 if value <= 6 else 2


def refine_vector(base: str, rng: "Rng") -> str:
    """A per-finding refinement of the category default, as the scorer does in its Section 3."""
    m = dict(part.split(":") for part in base.split("/")[1:])
    if rng.below(100) < 12:
        m["AV"] = "A" if rng.below(2) else "L"
    if rng.below(100) < 22:
        m["AC"] = "H" if m["AC"] == "L" else "L"
    if rng.below(100) < 35:
        m["PR"] = {"N": "L", "L": rng.pick(("N", "H")), "H": "L"}[m["PR"]]
    if rng.below(100) < 20:
        m["UI"] = "R" if m["UI"] == "N" else "N"
    if rng.below(100) < 12:
        m["S"] = "C" if m["S"] == "U" else "U"
    for key in ("C", "I", "A"):
        if rng.below(100) < 30:
            m[key] = {"H": "L", "L": rng.pick(("N", "H")), "N": "L"}[m[key]]
    if m["C"] == m["I"] == m["A"] == "N":
        m["I"] = "L"
    return "CVSS:3.1/" + "/".join("%s:%s" % (key, m[key]) for key in ("AV", "AC", "PR", "UI", "S", "C", "I", "A"))


def _sub_scores(base: tuple, rng: "Rng") -> tuple:
    values = [max(1, min(10, v + rng.below(4) - 2)) for v in base]
    if sum(values) % 2:  # an even sum keeps the average on a half point, so no rounding tie can arise
        values[3] += 1 if values[3] < 10 else -1
    return tuple(values)


def score_one(world: dict, finding: dict, rng: "Rng") -> dict:
    category = PREFIX_CATEGORY[finding["prefix"]]
    comp = world["by_name"][finding["comp"]]
    vector = refine_vector(CATEGORY_VECTOR[category], rng)
    cvss = cvss_tenths(vector)
    exposed = 2 if ZONE_LEVEL[comp["zone"]] in ("Untrusted", "Semi-trusted") else 0  # reachable from outside: easier and wider
    expl_sub0 = _sub_scores(tuple(min(10, v + exposed) for v in EXPLOIT_BASE[category]), rng)
    scale_sub0 = _sub_scores(tuple(min(10, v + exposed) for v in SCALE_BASE[category]), rng)
    lo, hi = REACH_RANGE[ZONE_LEVEL[comp["zone"]]]
    reach0 = max(lo, min(hi, ZONE_REACH[comp["zone"]] + 5 * (rng.below(5) - 2)))
    # A tie (the weighted sum ends in exactly .50 of a tenth) or a band boundary is nudged away. A reachability
    # step moves the sum by a multiple of 100, so it only clears a boundary; a sub-score step of 2 clears a tie.
    nudges = ((None, 0), ("reach", 5), ("reach", -5), ("scale", 2), ("scale", -2), ("expl", 2), ("expl", -2),
              ("reach", 10), ("reach", -10), ("scale", 4), ("expl", 4))
    for kind, delta in nudges:
        reach, expl_sub, scale_sub = reach0, list(expl_sub0), list(scale_sub0)
        if kind == "reach":
            reach = max(lo, min(hi, reach0 + delta))
        elif kind == "scale":
            scale_sub[0] = max(1, min(10, scale_sub[0] + delta))
        elif kind == "expl":
            expl_sub[0] = max(1, min(10, expl_sub[0] + delta))
        if sum(expl_sub) % 2 or sum(scale_sub) % 2:
            continue
        expl, scale = 5 * sum(expl_sub) // 2, 5 * sum(scale_sub) // 2
        total = composite_tenths(cvss, expl, scale, reach)
        if not composite_is_tie(cvss, expl, scale, reach) and not composite_on_boundary(total):
            break
    else:
        raise ValueError("no tie-free composite for %s" % finding["id"])
    band = band_of(total)
    sla, days, disposition = BAND_GOVERNANCE[band]
    return {"vector": vector, "cvss": cvss, "expl_sub": tuple(expl_sub), "expl": expl, "scale_sub": tuple(scale_sub),
            "scale": scale, "reach": reach, "composite": total, "band": band, "sla": sla, "sla_days": days,
            "disposition": disposition, "primary": finding["id"]}


def build_scores(world: dict) -> dict:
    """Scores for every open finding. A correlated peer inherits its primary's scores whole (severity-bands.md)."""
    if "scores" in world:
        return world["scores"]
    rng = Rng("world/%s/scores" % world["profile"])
    scores = {}
    for finding in world["findings"]:
        if finding["group"] is None or finding["primary"]:
            scores[finding["id"]] = score_one(world, finding, rng)
    for group in world["groups"]:
        lead = scores[group["members"][0]["id"]]
        for member in group["members"][1:]:
            scores[member["id"]] = dict(lead)
    for finding in world["findings"]:
        scores[finding["id"]]["review"] = add_days(world["cfg"]["dates"]["scores"], scores[finding["id"]]["sla_days"])
    world["scores"] = scores
    return scores


# Controls the stub codebase implements. Each gives its category, the components it protects, its own rating
# and the five lines of evidence a control report quotes; the stub files are written from these rows.
CONTROL_CATEGORIES = (  # (id, title, STRIDE prefixes mapped to it)
    ("authentication", "Authentication", ("S",)),
    ("access-control", "Access Control", ("S", "E")),
    ("input-validation", "Input Validation", ("T",)),
    ("encryption", "Encryption", ("I",)),
    ("rate-limiting", "Rate Limiting", ("D",)),
    ("logging-audit", "Logging/Audit", ("R",)),
    ("csrf-protection", "CSRF Protection", ()),
    ("csp-security-headers", "CSP/Security Headers", ()),
)
CONTROL_ROWS = (
    ("authentication", "Signed token verification at the gateway", "src/gateway/token_verify.py", "moderate",
     ("edge-gateway", "auth-broker", "intake-agent", "client-portal"),
     ("def verify_token(raw, keys, audience):", "    claims = decode_signed(raw, keys, algorithms=[\"ES256\"])", "    if claims[\"aud\"] != audience or claims[\"exp\"] < now():",
      "        raise Rejected(\"token not valid for this service\")", "    return claims")),
    ("authentication", "Mutual TLS between internal services", "src/gateway/mtls_config.py", "weak",
     ("planner-agent", "router-agent", "worker-2", "worker-3", "tool-server-1", "queue-a2"),
     ("def internal_context(ca_bundle, cert, key):", "    ctx = new_tls_context(purpose=\"server\")", "    ctx.load_chain(cert, key)",
      "    ctx.require_client_certificate(ca_bundle)", "    return ctx")),
    ("access-control", "Role check on every request", "src/policy/rbac.py", "moderate",
     ("auth-broker", "policy-engine", "planner-agent", "reviewer-agent", "audit-ledger"),
     ("def require_role(role):", "    def guard(request):", "        if role not in directory.roles_for(request.principal):",
      "            raise Forbidden(request.principal, role)", "    return guard")),
    ("access-control", "Per-agent tool allowlist", "src/tools/allowlist.py", "weak",
     ("tool-server-1", "worker-2", "worker-3", "router-agent", "planner-agent"),
     ("def allowed(agent_id, tool, arguments):", "    entry = ALLOWLIST.get(agent_id, {}).get(tool)", "    if entry is None:",
      "        return False", "    return entry.accepts(arguments)")),
    ("input-validation", "Schema validation of structured requests", "src/intake/schema.py", "moderate",
     ("intake-agent", "edge-gateway", "tool-server-1", "queue-a2", "planner-agent"),
     ("def parse_request(payload):", "    data = REQUEST_SCHEMA.validate(payload, extra=\"forbid\")", "    if len(data[\"text\"]) > MAX_TEXT:",
      "        raise Rejected(\"request too large\")", "    return data")),
    ("input-validation", "Parameterised database queries", "src/store/queries.py", "moderate",
     ("memory-store", "vector-store-a", "kb-index", "feature-store-2", "audit-ledger"),
     ("def load_task(conn, task_id):", "    cur = conn.cursor()", "    cur.execute(\"select body from tasks where id = %s\", (task_id,))",
      "    row = cur.fetchone()", "    return row[0] if row else None")),
    ("encryption", "TLS 1.3 for outbound and inbound links", "src/common/tls.py", "moderate",
     ("edge-gateway", "model-gateway", "embed-service-2", "summarizer-llm", "trace-collector"),
     ("def client_context():", "    ctx = new_tls_context(purpose=\"client\")", "    ctx.minimum_version = TLS_1_3",
      "    ctx.verify_hostname = True", "    return ctx")),
    ("encryption", "Encryption of archived objects", "src/store/archive_crypto.py", "weak",
     ("s3-archive", "memory-store", "audit-ledger"),
     ("def seal(blob, key_id):", "    key = key_service.data_key(key_id)", "    nonce = random_bytes(12)",
      "    return nonce + aead_encrypt(key, nonce, blob)", "")),
    ("rate-limiting", "Token bucket per caller at the edge", "src/gateway/ratelimit.py", "moderate",
     ("edge-gateway", "auth-broker", "model-gateway"),
     ("def allow(caller, now):", "    bucket = buckets.setdefault(caller, Bucket(rate=RATE, burst=BURST))", "    bucket.refill(now)",
      "    return bucket.take(1)", "")),
    ("rate-limiting", "Step and spend budget per agent task", "src/agents/budget.py", "weak",
     ("planner-agent", "router-agent", "worker-2", "worker-3", "scheduler-1", "queue-a2"),
     ("def charge(task, steps, tokens):", "    task.steps += steps", "    task.tokens += tokens",
      "    if task.steps > MAX_STEPS or task.tokens > MAX_TOKENS:", "        raise BudgetExceeded(task.id)")),
    ("logging-audit", "Append-only audit writer", "src/audit/ledger_writer.py", "moderate",
     ("audit-ledger", "policy-engine", "reviewer-agent", "tool-server-1", "planner-agent"),
     ("def record(event):", "    entry = {\"at\": utc_now(), \"who\": event.principal, \"what\": event.action}", "    entry[\"prev\"] = ledger.tail_hash()",
      "    ledger.append(entry)", "    return entry[\"prev\"]")),
    ("logging-audit", "Trace redaction before storage", "src/obs/trace_redact.py", "weak",
     ("trace-collector", "eval-runner", "intake-agent", "model-gateway"),
     ("def redact(span):", "    for field in SENSITIVE_FIELDS:", "        if field in span.attributes:",
      "            span.attributes[field] = \"[redacted]\"", "    return span")),
    ("csrf-protection", "Anti-forgery token on state changes", "src/portal/csrf.py", "moderate",
     ("client-portal", "reviewer-agent"),
     ("def check_csrf(request):", "    sent = request.headers.get(\"x-csrf-token\", \"\")", "    if not constant_time_equal(sent, request.session.csrf_token):",
      "        raise Forbidden(\"anti-forgery check failed\")", "")),
    ("csp-security-headers", "Content security policy and framing limits", "src/gateway/headers.py", "weak",
     ("edge-gateway", "client-portal"),
     ("def add_security_headers(response):", "    response.headers[\"content-security-policy\"] = \"default-src 'self'\"", "    response.headers[\"x-frame-options\"] = \"DENY\"",
      "    response.headers[\"strict-transport-security\"] = \"max-age=31536000\"", "    return response")),
)
CONTROL_FACTOR = {"found": 50, "partial": 25, "missing": 0}  # P0 reduction factors, in percent
CONTROL_STATUS_TEXT = {"found": "Control Found", "partial": "Partial Control", "missing": "No Control Found"}
EFFECTIVENESS_OF = {"found": "moderate", "partial": "weak", "missing": "none"}
RECOMMENDATION_BANK = {  # control category -> (what to implement, reference patterns, effort when missing, effort when partial)
    "authentication": ("Verify the caller's signed credential on every request to this component and bind it to the channel it arrived on",
                       "Short-lived signed tokens, mutual TLS, workload identity", "Medium", "Low"),
    "access-control": ("Evaluate the original caller's entitlement for each object and action, and deny by default when the check cannot be made",
                       "Role and attribute checks at the service boundary, deny-by-default policy", "High", "Medium"),
    "input-validation": ("Validate each structured input against a closed schema before use, and reject unknown fields and oversized values",
                         "Schema validation, parameterised queries, output encoding", "Medium", "Low"),
    "encryption": ("Protect this data in transit and at rest with current protocols and keys held outside the storage account",
                   "TLS 1.3, envelope encryption, managed key service", "Medium", "Low"),
    "rate-limiting": ("Bound concurrency, request rate and per-task spend for this component and shed load with a clear status",
                      "Token buckets, bulkheads, circuit breakers, task budgets", "Medium", "Low"),
    "logging-audit": ("Record who did what, to which object, with which outcome, in a store that operators cannot alter",
                      "Append-only ledger, hash chaining, structured events", "Medium", "Low"),
    "csrf-protection": ("Require an anti-forgery token on every state-changing request from a browser session",
                        "Synchroniser tokens, same-site cookies, origin checks", "Low", "Low"),
    "csp-security-headers": ("Send a restrictive content security policy and framing limits with every response",
                             "Content security policy, transport security header, framing restrictions", "Low", "Low"),
}


def control_category_ids(prefix: str) -> tuple:
    """The control categories searched for a finding prefix (stride_control_mapping in the schema)."""
    category = PREFIX_CATEGORY[prefix]
    if category == "agentic":
        return tuple(cat[0] for cat in CONTROL_CATEGORIES)
    if category == "llm":
        return ("input-validation", "logging-audit")
    return tuple(cat[0] for cat in CONTROL_CATEGORIES if prefix in cat[2])


def build_controls(world: dict) -> dict:
    """Control status, residual score and recommendation for every open finding."""
    if "controls" in world:
        return world["controls"]
    scores = build_scores(world)
    names = {comp["name"] for comp in world["components"]}  # membership only; never iterated
    defs = []
    for number, row in enumerate(CONTROL_ROWS, start=1):
        category, summary, path, rating, covers, snippet = row
        defs.append({"id": "CTRL-%02d" % number, "category": category, "summary": summary, "path": path, "rating": rating,
                     "covers": tuple(name for name in covers if name in names), "snippet": tuple(line for line in snippet if line),
                     "line": stub_line(number)})
    by_finding = {}
    for finding in world["findings"]:
        score = scores[finding["id"]]
        wanted = control_category_ids(finding["prefix"])
        candidates = [d for d in defs if d["category"] in wanted and finding["comp"] in d["covers"]]
        best = None
        for d in candidates:
            if best is None or (d["rating"] == "moderate" and best["rating"] != "moderate"):
                best = d
        desired = "missing" if best is None else ("found" if best["rating"] == "moderate" else "partial")
        if desired == "found" and label_below("downgrade:" + finding["id"], 100) < 22:
            desired = "partial"
        chain = [desired] + [s for s in ("partial", "found", "missing") if s != desired]
        if best is None:
            chain = ["missing"]
        status = next(s for s in chain if not residual_is_tie(score["composite"], CONTROL_FACTOR[s]))
        residual = residual_tenths(score["composite"], CONTROL_FACTOR[status])
        control = best if status != "missing" else None
        by_finding[finding["id"]] = {"status": status, "control": control, "residual": residual,
                                     "band": band_of(residual), "factor": CONTROL_FACTOR[status]}
    world["controls"] = {"defs": defs, "by_finding": by_finding}
    return world["controls"]

# --------------------------------------------------------------------------- threats.md
GE = "\u2265"  # the greater-or-equal sign the pattern gate text uses


def largest_remainder(counts: Sequence, total_units: int = 1000) -> list:
    """Split total_units across counts in proportion, so the parts sum exactly (ties go to the earlier row)."""
    whole = sum(counts)
    if whole == 0:
        return [0 for _ in counts]
    base = [total_units * c // whole for c in counts]
    order = sorted(range(len(counts)), key=lambda i: (-(total_units * counts[i] % whole), i))
    for i in order[: total_units - sum(base)]:
        base[i] += 1
    return base


def pct(units: int) -> str:
    return fmt1(units) + "%"


def component_type_label(comp: dict) -> str:
    """The coverage-gate type the shipped matrices print for a component."""
    if comp["dfd"] == "External Entity":
        return "external_entity"
    if comp["dfd"] == "Data Store":
        return "data_store"
    if comp["name"].startswith("tool-server"):
        return "mcp_server"
    return "llm_process" if any(code.startswith("LLM:") for code in comp["ai"]) else "process"


def required_categories(comp: dict) -> list:
    required = [p for p in STRIDE_PREFIXES_ORDER if _stride_eligible(p, comp)]
    names = {"S": "spoofing", "T": "tampering", "R": "repudiation", "I": "info-disclosure",
             "D": "denial-of-service", "E": "privilege-escalation"}
    out = [names[p] for p in required]
    if any(code.startswith("AG:") for code in comp["ai"]):
        out.append("agentic")
    if any(code.startswith("LLM:") for code in comp["ai"]):
        out.append("llm")
    return out


def dedup_units(world: dict, findings: Sequence) -> list:
    """Findings as the deduplicated units Sections 5 and 6 count: a correlation group counts once."""
    seen, units = [], []
    for finding in findings:
        if finding["group"] is None:
            units.append((finding["risk"], finding["comp"], finding["prefix"], [finding]))
        elif finding["group"] not in seen:
            seen.append(finding["group"])
            group = next(g for g in world["groups"] if g["id"] == finding["group"])
            units.append((group["risk"], group["component"], finding["prefix"], list(group["members"])))
    return units


def coverage_cell_columns(finding: dict) -> str:
    if finding["prefix"] in STRIDE_PREFIXES_ORDER:
        return finding["prefix"]
    return "AG" if PREFIX_CATEGORY[finding["prefix"]] == "agentic" else "LLM"


def baseline_count(world: dict) -> int:
    return sum(1 for f in world["findings"] if f["status"] != STATUS_NEW) + len(world["resolved"])


def render_architecture_tables(world: dict) -> str:
    comps = world["components"]
    lines = ["## 1. System Overview", "",
             "Parsed summary of the architecture input for the %s: a multi-agent platform that turns operator requests into planned, "
             "reviewed and audited shipment actions. %d components were identified across %d trust zones. The inventory below is the "
             "scope of this threat model." % (PLATFORM, len(comps), len(world["zones"])),
             "", "### Components", "",
             table(("Component", "Type", "MAESTRO Layer", "Description"),
                   [(c["name"], c["dfd"], layer_label(c["layer"]), c["desc"]) for c in comps]),
             "", "### Data Flows", "",
             table(("Source", "Destination", "Data", "Protocol"), [(s, d, data, proto) for s, d, data, proto in world["flows"]]),
             "", "### Technologies", "",
             table(("Category", "Technology", "Version (if known)"), TECHNOLOGY_ROWS),
             "", "---", "", "## 2. Trust Boundaries", "",
             "Trust zones group components that share a security posture. Each crossing between zones is a priority target for analysis.",
             "", "### Trust Zones", "",
             table(("Zone", "Trust Level", "Components"), [(z["name"], z.get("label", z["level"]), ", ".join(z["members"])) for z in world["zones"]]),
             "", "### Boundary Crossings", ""]
    crossings = []  # (from zone, to zone) -> flows, in first-seen order
    for source, dest, _, _ in world["flows"]:
        pair = (world["by_name"][source]["zone"], world["by_name"][dest]["zone"])
        if pair[0] == pair[1]:
            continue
        for entry in crossings:
            if entry[0] == pair:
                entry[1].append("%s -> %s" % (source, dest))
                break
        else:
            crossings.append((pair, ["%s -> %s" % (source, dest)]))
    rows = []
    for (src_zone, dst_zone), members in crossings:
        shown = ", ".join(members[:4]) + (" and %d more" % (len(members) - 4) if len(members) > 4 else "")
        rows.append(("%s to %s" % (src_zone, dst_zone), src_zone, dst_zone, shown,
                     CROSSING_CONTROLS.get((src_zone, dst_zone), "Mutual TLS, authentication")))
    lines.append(table(("Crossing", "From Zone", "To Zone", "Components", "Controls"), rows))
    return "\n".join(lines)


def _finding_row(f: dict, ai: bool) -> list:
    base = [f["id"], f["status"], f["comp"], layer_label(f["layer"]), f["threat"]]
    if ai:
        base.append(f["ref"])
    return base + [f["like"], f["imp"], f["risk"], f["mit"]]


def render_threats_md(world: dict) -> str:
    cfg, findings = world["cfg"], world["findings"]
    dates, runs = cfg["dates"], cfg["run_ids"]
    first = [
        "---", 'schema_version: "1.4"', 'date: "%s"' % dates["threats"],
        'input_format: "%s"' % ("mermaid" if cfg["mermaid"] else "free-text"), 'classification: "confidential"',
        'run_id: "%s"' % runs["threats"], "baseline:",
        '  source: "%s"' % cfg.get("baseline_source", "baseline-runs/%s/threats.md" % dates["baseline"]),
        '  date: "%s"' % dates["baseline"], "  finding_count: %d" % baseline_count(world), '  run_id: "%s"' % runs["baseline"],
        "coverage_gate:", '  status: "pass"', "  gaps: []", "---", "",
        "# Threat Model Report", "", render_architecture_tables(world), "", "---", "",
        "## 3. STRIDE Tables", "",
        "One table per STRIDE category. Every row carries a delta status against the baseline run. RESOLVED findings are listed in Section 4c.",
        "", "**Risk level computation (OWASP 3x3 matrix):**", "",
        "| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |", "|---|---|---|---|",
        "| **HIGH Impact** | Medium | High | Critical |", "| **MEDIUM Impact** | Low | Medium | High |",
        "| **LOW Impact** | Note | Low | Medium |", "",
    ]
    stride_titles = (("S", "3.1 Spoofing (S)", "Threats where an attacker pretends to be something or someone else."),
                     ("T", "3.2 Tampering (T)", "Threats where an attacker modifies data or code without authorization."),
                     ("R", "3.3 Repudiation (R)", "Threats where an actor denies an action without the system being able to prove otherwise."),
                     ("I", "3.4 Information Disclosure (I)", "Threats where sensitive data is exposed to unauthorized parties."),
                     ("D", "3.5 Denial of Service (D)", "Threats where an attacker degrades or prevents legitimate access."),
                     ("E", "3.6 Elevation of Privilege (E)", "Threats where an attacker gains higher access rights than authorized."))
    header = ("ID", "Status", "Component", "MAESTRO Layer", "Threat", "Likelihood", "Impact", "Risk Level", "Mitigation")
    ai_header = ("ID", "Status", "Component", "MAESTRO Layer", "Threat", "OWASP Reference", "Likelihood", "Impact", "Risk Level", "Mitigation")
    for prefix, title, blurb in stride_titles:
        rows = [_finding_row(f, False) for f in findings if f["prefix"] == prefix]
        first += ["### " + title, "", blurb, "", table(header, rows), ""]
    first += ["---", "", "## 4. AI Threat Tables", "",
              "Findings from the AI-specific agents. Each row adds an OWASP reference to the standard fields.", ""]
    for title, blurb, prefixes in (
            ("4.1 Agentic Threats (AG)", "Threats arising from autonomous agent behavior, tool use and the way people rely on agent output.", ("AG", "AGP", "TE")),
            ("4.2 LLM Threats (LLM)", "Threats to and through the language models: injection, poisoning, extraction, unsafe output and misinformation.", ("LLM", "OI", "MI"))):
        rows = [_finding_row(f, True) for f in findings if f["prefix"] in prefixes]
        first += ["### " + title, "", blurb, "", table(ai_header, rows), ""]
    first += ["---", "", "## 4a. Correlated Findings", "",
              "Cross-agent correlation groups link findings from different agent categories that target the same component. "
              "Original findings stay in Sections 3 and 4; groups are additive.", "",
              table(("Group", "Findings", "Component", "Threat Summary", "Risk Level"),
                    [(g["id"], ", ".join(m["id"] for m in g["members"]), g["component"],
                      "; ".join("%s: %s" % (GROUP_LABEL[m["sub"] or m["prefix"]], clip(m["short"], 70)) for m in g["members"]),
                      g["risk"]) for g in world["groups"]]),
              "", "---", ""]
    first += _pattern_section(world) + _resolved_section(world)
    first += _coverage_sections(world) + _risk_summary(world) + _actions_and_delta(world)
    return "\n".join(first)


def _pattern_section(world: dict) -> list:
    comps = world["components"]
    agentic = [c["name"] for c in comps if c["ai"]]
    patterns = ("agent_collusion", "emergent_behavior", "temporal_attack", "trust_exploitation",
                "communication_vulnerability", "resource_competition")
    rows = []
    for index, pattern in enumerate(patterns):
        ids = [f["id"] for f in world["findings"] if f["pattern"] == pattern]
        if ids:
            rows.append((len(ids), index, pattern, ids))
    rows.sort(key=lambda r: (-r[0], r[1]))
    return ["## 4b. Findings by Agentic Pattern", "",
            "**Multi-agent gate predicate evaluation**:",
            "- Condition (a): %s2 agentic or LLM components: TRUE (%d components)" % (GE, len(agentic)),
            "- Condition (b): inter-agent data flow between two agentic components: TRUE",
            "- Condition (c): explicit multi-agent keyword in the architecture: TRUE",
            "- **Predicate result: TRUE**", "",
            table(("Pattern", "Count", "Findings"), [(p, n, ", ".join(ids)) for n, _, p, ids in rows]),
            "", "---", ""]


def _resolved_section(world: dict) -> list:
    rows = [(r["id"], r["comp"], r["short"], r["risk"], r["reason"]) for r in world["resolved"]]
    return ["## 4c. Resolved Findings", "",
            "Findings from the baseline that no longer apply in the current architecture. Each keeps its original ID, description and last-known risk level.",
            "", table(("ID", "Component", "Threat", "Last Risk Level", "Resolution Reason"), rows), "", "---", ""]


def _coverage_sections(world: dict) -> list:
    comps, findings = world["components"], world["findings"]
    columns = ("S", "T", "R", "I", "D", "E", "AG", "LLM")
    rows, col_totals, merged = [], [0] * len(columns), 0
    for comp in comps:
        cells, row_total = [], 0
        here = [f for f in findings if f["comp"] == comp["name"]]
        for ci, col in enumerate(columns):
            if col in STRIDE_PREFIXES_ORDER:
                applicable = _stride_eligible(col, comp)
            elif col == "AG":
                applicable = any(code.startswith("AG:") or code == "TE" for code in comp["ai"])
            else:
                applicable = any(code.startswith("LLM:") or code in ("OI", "MI") for code in comp["ai"])
            if not applicable:
                cells.append("n/a")
                continue
            members = [f for f in here if coverage_cell_columns(f) == col]
            groups = {f["group"] for f in members if f["group"]}  # membership only
            count = sum(1 for f in members if f["group"] is None) + len(groups)
            cells.append(str(count) if count else EM)
            row_total += count
            col_totals[ci] += count
        rows.append([comp["name"]] + cells + [str(row_total)])
    total_row = ["**Total**"] + ["**%d**" % n for n in col_totals] + ["**%d**" % sum(col_totals)]
    merged = sum(len(g["members"]) for g in world["groups"])
    out = ["## 5. Coverage Matrix", "",
           "Each cell is the deduplicated finding count for a component and category (a correlation group counts once). "
           "%s means analyzed with no findings; n/a means the category does not apply." % EM, "",
           "| Component | S | T | R | I | D | E | AG | LLM | Total |", "|-----------|---|---|---|---|---|---|----|-----|-------|"]
    out += ["| " + " | ".join(r) + " |" for r in rows] + ["| " + " | ".join(total_row) + " |", "",
           "Counts reflect deduplicated findings. %d correlation groups merged %d individual findings." % (len(world["groups"]), merged),
           "", "---", "", "## 5a. Coverage Gate Results", "",
           "Coverage gate passed %s all required threat categories evaluated for every component." % EM, "",
           "### Coverage Requirements Matrix", ""]
    gate_rows = []
    for comp in comps:
        required = required_categories(comp)
        gate_rows.append((comp["name"], component_type_label(comp), ", ".join(required),
                          "%d / %d" % (len(required), len(required)), "None"))
    out += [table(("Component", "Determined Type", "Required Categories", "Evaluated", "Gaps"), gate_rows), "", "---", ""]
    return out


def _risk_summary(world: dict) -> list:
    findings = world["findings"]
    units = dedup_units(world, findings)
    levels = ("Critical", "High", "Medium", "Low", "Note")
    dedup = [sum(1 for u in units if u[0] == lvl) for lvl in levels]
    raw = [sum(1 for f in findings if f["risk"] == lvl) for lvl in levels]
    share = largest_remainder(dedup)
    count_text = lambda d, r: str(d) if d == r else "%d (%d raw)" % (d, r)  # noqa: E731
    rows = [(lvl, count_text(d, r), pct(s)) for lvl, d, r, s in zip(levels, dedup, raw, share)]
    rows.append(("**Total**", "**%s**" % count_text(sum(dedup), sum(raw)), "**100%**"))
    layer_rows = []
    for number in range(1, 8):
        in_layer = [u for u in units if world["by_name"][u[1]]["layer"] == number]
        has_comp = any(c["layer"] == number for c in world["components"])
        if in_layer:
            top = max((u[0] for u in in_layer), key=lambda r: RISK_RANK[r])
            layer_rows.append((layer_label(number), len(in_layer), top))
        elif has_comp:
            layer_rows.append((layer_label(number), 0, "Analyzed %s no findings this scan" % EM))
        else:
            layer_rows.append((layer_label(number), 0, "Not applicable %s no components map to this layer" % EM))
    return ["## 6. Risk Summary", "",
            "Aggregate counts of findings by risk level, computed with the OWASP 3x3 matrix (likelihood x impact).", "",
            "### Risk Calibration Matrix", "",
            "| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |", "|---|---|---|---|",
            "| **HIGH Impact** | Medium | High | Critical |", "| **MEDIUM Impact** | Low | Medium | High |",
            "| **LOW Impact** | Note | Low | Medium |", "",
            "#### Risk by MAESTRO Layer", "",
            table(("MAESTRO Layer", "Finding Count", "Highest Severity"), layer_rows), "",
            "Risk summary counts below reflect deduplicated findings. A correlation group counts as one threat at its group risk level.", "",
            table(("Risk Level", "Count", "Percentage"), rows), "", "---", ""]


def _assets_cell(world: dict, finding: dict) -> str:
    """The populator's value for one finding: the sorted tags of its component, as '[a, b]', or '[]'."""
    tags = world.get("block_tags", world.get("asset_tags", {})).get(finding["comp"], ())  # block_tags: a block that differs from the architecture's
    return "[" + ", ".join(sorted(tags)) + "]"


def _actions_and_delta(world: dict) -> list:
    findings = world["findings"]
    ranked = sorted(findings, key=lambda f: (-RISK_RANK[f["risk"]], TABLE_ORDER.index(f["prefix"]), f["num"]))
    rows = [(f["id"], f["status"], CATEGORY_TITLE[f["prefix"]], EM if f["pattern"] == "none" else f["pattern"], f["comp"],
             layer_label(f["layer"]), f["short"], f["risk"], f["mit_short"]) for f in ranked]
    counts = {s: sum(1 for f in findings if f["status"] == s) for s in (STATUS_NEW, STATUS_UNCHANGED, STATUS_UPDATED)}
    resolved = len(world["resolved"])
    cfg = world["cfg"]
    out = ["## 7. Recommended Actions", "",
           "All findings sorted by risk level descending, then by table order. Critical and High findings should be addressed before deployment.",
           "", table(("Finding ID", "Status", "Category", "Pattern", "Component", "MAESTRO Layer", "Threat", "Risk Level", "Mitigation"), rows),
           "", "---", "", "## 8. Delta Summary", "",
           "The lifecycle of every finding relative to the baseline run. Section 4c lists the resolved findings.", "",
           "### Finding Lifecycle", "",
           table(("Status", "Count", "Description"), (
               ("NEW", counts[STATUS_NEW], "Findings discovered in this run with no baseline match"),
               ("UNCHANGED", counts[STATUS_UNCHANGED], "Findings identical to baseline (same component, threat, assessment)"),
               ("UPDATED", counts[STATUS_UPDATED], "Findings with changed context since baseline"),
               ("RESOLVED", resolved, "Baseline findings no longer applicable (see Section 4c for details)"),
               ("**Total**", "**%d**" % (len(findings) + resolved), "Sum of all findings (active + resolved)"))),
           "", "### Baseline Reference", "",
           table(("Field", "Value"), (("Source", cfg.get("baseline_source", "baseline-runs/%s/threats.md" % cfg["dates"]["baseline"])), ("Date", cfg["dates"]["baseline"]),
                                      ("Baseline Findings", baseline_count(world)), ("Run ID", cfg["run_ids"]["baseline"]))),
           # The block exactly as scripts/populate-affected-assets.py renders it (no introduction, one row per finding in
           # Section 7's order), so that Step 1.5 of /tachi.risk-score rewrites nothing. No component carries a tag.
           "", "---", "", "## Affected Assets", "",
           table(("Finding ID", "Affected Assets"), [(f["id"], _assets_cell(world, f)) for f in ranked])]
    return out

# --------------------------------------------------------------------------- SARIF, stub code, trees, architecture
SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json"
INFO_URI = "https://github.com/owner/tachi"
CATEGORY_RULE = {
    "spoofing": "tachi/stride/spoofing", "tampering": "tachi/stride/tampering", "repudiation": "tachi/stride/repudiation",
    "info-disclosure": "tachi/stride/information-disclosure", "denial-of-service": "tachi/stride/denial-of-service",
    "privilege-escalation": "tachi/stride/elevation-of-privilege", "agentic": "tachi/ai/agentic-threats", "llm": "tachi/ai/llm-threats",
}
RULE_TEXT = {  # rule id -> (short, full, help text, help markdown, tags, OWASP id, CWE id)
    "tachi/stride/spoofing": ("Identity spoofing threats",
        "Threats where an attacker pretends to be something or someone else, such as replaying credentials or impersonating a trusted component.",
        "Review authentication mechanisms, token validation, credential storage and session management at every trust boundary.",
        "## Detection Guidance\n\nReview authentication mechanisms for weaknesses:\n- Token signing and binding\n- Credential storage and rotation\n- Session management\n\n## Framework References\n\n- OWASP Top 10: A07 Identification and Authentication Failures\n- CWE-287: Improper Authentication",
        ("security", "stride", "spoofing", "authentication"), "A07", "CWE-287"),
    "tachi/stride/tampering": ("Data tampering threats",
        "Threats where an attacker modifies data or code without authorization, in transit, at rest or in the build and deployment path.",
        "Review input validation, message integrity, configuration control and supply chain provenance.",
        "## Detection Guidance\n\nReview integrity controls:\n- Schema validation at boundaries\n- Message signing\n- Build provenance\n\n## Framework References\n\n- OWASP Top 10: A08 Software and Data Integrity Failures\n- CWE-345: Insufficient Verification of Data Authenticity",
        ("security", "stride", "tampering", "integrity"), "A08", "CWE-345"),
    "tachi/stride/repudiation": ("Repudiation threats",
        "Threats where an actor can deny an action because the system cannot prove who did what and when.",
        "Review audit logging, log protection, time synchronisation and approval binding.",
        "## Detection Guidance\n\nReview accountability controls:\n- Who, what, when and outcome in every record\n- Tamper-evident storage\n- Approval binding\n\n## Framework References\n\n- OWASP Top 10: A09 Security Logging and Monitoring Failures\n- CWE-778: Insufficient Logging",
        ("security", "stride", "repudiation", "logging"), "A09", "CWE-778"),
    "tachi/stride/information-disclosure": ("Information disclosure threats",
        "Threats where sensitive data is exposed to parties that should not see it, through errors, logs, storage or transport.",
        "Review error handling, logging content, encryption in transit and at rest, and tenant isolation.",
        "## Detection Guidance\n\nReview confidentiality controls:\n- Error and log content\n- Encryption in transit and at rest\n- Tenant isolation\n\n## Framework References\n\n- OWASP Top 10: A01 Broken Access Control\n- CWE-200: Exposure of Sensitive Information",
        ("security", "stride", "information-disclosure", "data-exposure"), "A01", "CWE-200"),
    "tachi/stride/denial-of-service": ("Denial of service threats",
        "Threats where an attacker degrades or prevents legitimate use through resource exhaustion or cascading dependency failure.",
        "Review limits on concurrency, payload size, retries and dependency timeouts.",
        "## Detection Guidance\n\nReview availability controls:\n- Rate and concurrency limits\n- Timeouts and bulkheads\n- Capacity alerts\n\n## Framework References\n\n- OWASP Top 10: A05 Security Misconfiguration\n- CWE-400: Uncontrolled Resource Consumption",
        ("security", "stride", "denial-of-service", "availability"), "A05", "CWE-400"),
    "tachi/stride/elevation-of-privilege": ("Elevation of privilege threats",
        "Threats where a caller gains rights that were not granted, through missing ownership checks, role confusion or excess permissions.",
        "Review authorization at every object and action, role resolution and the permissions each service holds.",
        "## Detection Guidance\n\nReview authorization controls:\n- Ownership checks on object references\n- Role resolution\n- Least privilege\n\n## Framework References\n\n- OWASP Top 10: A01 Broken Access Control\n- CWE-269: Improper Privilege Management",
        ("security", "stride", "elevation-of-privilege", "authorization"), "A01", "CWE-269"),
    "tachi/ai/agentic-threats": ("AI agent autonomy and misuse threats",
        "Threats arising from autonomous agent behavior, including uncontrolled tool use, excessive autonomy, agent-to-agent trust and reliance on agent output.",
        "Review agent autonomy boundaries, tool access controls, human approval gates and inter-agent trust assumptions.",
        "## Detection Guidance\n\nReview agent controls:\n- Tool allowlists and scopes\n- Human approval for high-impact actions\n- Delegation limits\n\n## Framework References\n\n- OWASP Agentic Security Initiative\n- CWE-693: Protection Mechanism Failure",
        ("security", "ai", "agentic", "autonomy", "tool-use"), "", "CWE-693"),
    "tachi/ai/llm-threats": ("LLM-specific threats",
        "Threats to and through language models, including prompt injection, data poisoning, extraction, unsafe output handling and misinformation.",
        "Review prompt construction, retrieval sources, training data provenance, output handling and grounding.",
        "## Detection Guidance\n\nReview model controls:\n- Separation of instructions and content\n- Provenance of retrieved and training data\n- Output validation\n\n## Framework References\n\n- OWASP Top 10 for LLM Applications\n- CWE-74: Improper Neutralization of Special Elements in Output",
        ("security", "ai", "llm", "prompt-injection"), "", "CWE-74"),
}
CONTROL_TITLE = {cid: title for cid, title, _ in CONTROL_CATEGORIES}
LEVEL_OF_BAND = {"Critical": "error", "High": "error", "Medium": "warning", "Low": "note", "Note": "note"}
RULE_SEVERITY_OF_RISK = {"Critical": "9.0", "High": "8.0", "Medium": "5.0", "Low": "2.0", "Note": "0.1"}
KIND_OF_DFD = {"Process": "process", "External Entity": "external-entity", "Data Store": "data-store"}
TAXONOMIES = (
    {"name": "OWASP", "version": "2021", "informationUri": "https://owasp.org/Top10/", "organization": "OWASP Foundation",
     "shortDescription": {"text": "OWASP Top 10 Web Application Security Risks"}},
    {"name": "CWE", "version": "4.13", "informationUri": "https://cwe.mitre.org/", "organization": "MITRE",
     "shortDescription": {"text": "Common Weakness Enumeration"}},
)


def first_sentence(text: str) -> str:
    cut = text.find(". ")
    return text if cut < 0 else text[: cut + 1]


def finding_rule(finding: dict) -> str:
    return CATEGORY_RULE[PREFIX_CATEGORY[finding["prefix"]]]


def logical_location(world: dict, comp_name: str) -> dict:
    comp = world["by_name"][comp_name]
    return {"name": comp_name, "fullyQualifiedName": "%s/%s" % (comp["zone"], comp_name), "kind": KIND_OF_DFD[comp["dfd"]]}


def location_block(world: dict, comp_name: str) -> list:
    return [{"physicalLocation": {"artifactLocation": {"uri": world["cfg"]["architecture_file"]}, "region": {"startLine": 1}},
             "logicalLocations": [logical_location(world, comp_name)]}]


def rule_entries(world: dict, severity_of_rule: dict, results_rules: Sequence) -> list:
    """One reportingDescriptor per category that produced findings, in the spec's category order."""
    entries = []
    for rule_id in CATEGORY_RULE.values():
        if rule_id not in results_rules:
            continue
        short, full, help_text, help_md, tags, owasp, cwe = RULE_TEXT[rule_id]
        relationships = []
        for target, name in ((owasp, "OWASP"), (cwe, "CWE")):
            if target:
                relationships.append({"target": {"id": target, "toolComponent": {"name": name}}, "kinds": ["relevant"]})
        entries.append({"id": rule_id, "shortDescription": {"text": short}, "fullDescription": {"text": full},
                        "help": {"text": help_text, "markdown": help_md},
                        "properties": {"tags": list(tags), "security-severity": severity_of_rule[rule_id]},
                        "relationships": relationships})
    return entries


def sarif_document(driver: dict, results: list) -> dict:
    return {"$schema": SARIF_SCHEMA, "version": "2.1.0",
            "runs": [{"tool": {"driver": driver}, "taxonomies": [dict(t) for t in TAXONOMIES], "results": results}]}


def render_threats_sarif(world: dict) -> str:
    """threats.sarif as v4.48.4 writes it: a correlated peer is not a top-level result, it sits in its primary's relatedLocations."""
    run_id = world["cfg"]["run_ids"]["baseline"]
    state = {STATUS_NEW: "new", STATUS_UNCHANGED: "unchanged", STATUS_UPDATED: "updated"}
    results, worst = [], {}
    for f in world["findings"]:
        if f["group"] is not None and not f["primary"]:
            continue
        rule = finding_rule(f)
        worst[rule] = max(worst.get(rule, "Note"), f["risk"], key=lambda r: RISK_RANK[r])
        tags = ["maestro-layer:L%d" % f["layer"]] + (["maestro-pattern:%s" % f["pattern"]] if f["pattern"] != "none" else [])
        result = {"ruleId": rule, "message": {"text": f["threat"], "markdown": f["mit"]}, "level": LEVEL_OF_BAND[f["risk"]],
                  "locations": location_block(world, f["comp"])}
        if f["group"] is not None:
            group = next(g for g in world["groups"] if g["id"] == f["group"])
            result["relatedLocations"] = [
                {"id": index, "message": {"text": "%s: %s" % (peer["id"], peer["short"])},
                 "logicalLocations": [logical_location(world, peer["comp"])]}
                for index, peer in enumerate(group["members"][1:])]
        prints = {"primaryLocationLineHash": digest16("%s|%s" % (rule, f["comp"])), "findingId/v1": f["id"]}
        if f["group"] is not None:
            prints["correlationGroup"] = f["group"]
        prints["baselineRunId"] = "" if f["status"] == STATUS_NEW else run_id
        result["partialFingerprints"] = prints
        result["properties"] = {"baselineState": state[f["status"]], "maestro-layer": layer_label(f["layer"]), "tags": tags,
                                "affected_assets": []}
        results.append(result)
    severity = {rule: RULE_SEVERITY_OF_RISK[risk] for rule, risk in worst.items()}
    driver = {"name": "Tachi", "semanticVersion": "1.1", "informationUri": INFO_URI,
              "supportedTaxonomies": [{"name": "OWASP", "index": 0}, {"name": "CWE", "index": 1}],
              "rules": rule_entries(world, severity, list(worst))}
    return dumps(sarif_document(driver, results), indent=2, sort_keys=False)


def _sarif_vector(score: dict) -> dict:
    """The SARIF result's cvss-vector property: the row's vector, a vector that disagrees with the markdown's, or none."""
    vector = score.get("sarif_vector", score["vector"])
    return {} if vector is None else {"cvss-vector": vector}


def render_risk_scores_sarif(world: dict) -> str:
    scores = build_scores(world)
    results, worst = [], {}
    for f in sorted(world["findings"], key=lambda f: (-scores[f["id"]]["composite"], prefix_rank(f["id"]))):
        s = scores[f["id"]]
        rule = finding_rule(f)
        worst[rule] = max(worst.get(rule, 0), s["composite"])
        results.append({
            "ruleId": rule, "message": {"text": first_sentence(f["threat"]), "markdown": first_sentence(f["mit"])},
            "level": LEVEL_OF_BAND[s["band"]], "locations": location_block(world, f["comp"]),
            "partialFingerprints": {"primaryLocationLineHash": digest16("%s|%s" % (rule, f["comp"])), "findingId/v1": f["id"]},
            "properties": {"security-severity": fmt1(s["composite"]), "cvss-base-score": fmt1(s["cvss"]),
                           **_sarif_vector(s),
                           "exploitability": fmt1(s["expl"]), "scalability": fmt1(s["scale"]), "reachability": fmt1(s["reach"]),
                           "composite-weights": "0.35/0.30/0.15/0.20", "score-source": s.get("source", "fresh"),
                           "baseline-state": {STATUS_NEW: "new", STATUS_UNCHANGED: "unchanged", STATUS_UPDATED: "updated"}[f["status"]],
                           "severity-band": s["band"], "risk-owner": s.get("owner", "Unassigned"), "remediation-sla": s["sla"],
                           "risk-disposition": s["disposition"], "review-date": s["review"],
                           "maestro-layer": layer_label(f["layer"]), "affected_assets": []}})
    driver = {"name": "tachi-risk-scorer", "version": "1.0", "semanticVersion": "1.0", "informationUri": INFO_URI,
              "supportedTaxonomies": [{"name": "OWASP", "index": 0}, {"name": "CWE", "index": 1}],
              "rules": rule_entries(world, {r: fmt1(v) for r, v in worst.items()}, list(worst))}
    return dumps(sarif_document(driver, results), indent=2, sort_keys=False)


def render_controls_sarif(world: dict) -> str:
    scores, controls = build_scores(world), build_controls(world)
    results, worst = [], {}
    order = sorted(world["findings"], key=lambda f: (-controls["by_finding"][f["id"]]["residual"], prefix_rank(f["id"])))
    for f in order:
        s, c = scores[f["id"]], controls["by_finding"][f["id"]]
        rule = finding_rule(f)
        worst[rule] = max(worst.get(rule, 0), c["residual"])
        control = c["control"]
        evidence = [] if control is None else [{"file": control["path"], "line": control["line"], "snippet": "\n".join(control["snippet"])}]
        recommendation, effort = control_recommendation(world, f, c)
        result = {"ruleId": rule,
                  "message": {"text": "%s [Control: %s]" % (first_sentence(f["threat"]), c["status"])},
                  "level": LEVEL_OF_BAND[c["band"]], "locations": location_block(world, f["comp"])}
        if control is not None:
            result["relatedLocations"] = [{"id": 0, "message": {"text": "Control evidence: %s detected in %s" % (
                CONTROL_TITLE[control["category"]], control["path"])},
                "physicalLocation": {"artifactLocation": {"uri": control["path"]}, "region": {"startLine": control["line"]}}}]
        result["partialFingerprints"] = {"primaryLocationLineHash": digest16("%s|%s" % (rule, f["comp"])), "findingId/v1": f["id"]}
        result["properties"] = {"security-severity": fmt1(c["residual"]), "control-status": c["status"], "control-evidence": evidence,
                                "control-carry-forward": False, "control-effectiveness": EFFECTIVENESS_OF[c["status"]],
                                "maestro-layer": layer_label(f["layer"]), "inherent-risk": fmt1(s["composite"]),
                                "residual-risk": fmt1(c["residual"]), "recommendation": recommendation, "effort-estimate": effort}
        results.append(result)
    driver = {"name": "tachi-control-analyzer", "version": "1.0", "semanticVersion": "1.0", "informationUri": INFO_URI,
              "supportedTaxonomies": [{"name": "OWASP", "index": 0}, {"name": "CWE", "index": 1}],
              "rules": rule_entries(world, {r: fmt1(v) for r, v in worst.items()}, list(worst))}
    return dumps(sarif_document(driver, results), indent=2, sort_keys=False)


def recommendation_path(comp_name: str, category: str) -> str:
    return "stub-codebase/src/%s/%s.py" % (comp_name.replace("-", "_"), category.replace("-", "_"))


# --------------------------------------------------------------------------- stub codebase
def stub_line(number: int) -> int:
    """The line a control's evidence starts on: the five-line header, plus a few comment lines that vary per file."""
    return 6 + (number % 4)


def stub_files(world: dict) -> dict:
    controls = build_controls(world)
    files = {"README.md": "# Stub codebase\n\nA small synthetic code tree for the %s fixture. It holds one short, "
                          "never-run module per security control, so that the controls stage has evidence to find. "
                          "Nothing here is real, and nothing here is meant to be executed.\n" % PLATFORM}
    for number, d in enumerate(controls["defs"], start=1):
        header = ['"""%s.' % d["summary"], "", "Synthetic stub for the large-architecture fixture. It is never run.", '"""', ""]
        header += ["# review note %d" % (index + 1) for index in range(stub_line(number) - 6)]
        files[d["path"]] = "\n".join(header + list(d["snippet"])) + "\n"
    return files


# --------------------------------------------------------------------------- attack trees
def tree_text(world: dict, f: dict) -> str:
    comp = world["by_name"][f["comp"]]
    node = f["id"].replace("-", "")
    peer = (comp["peers"] or [("the neighbouring service", "an internal channel")])[0]
    clean = lambda text: text.replace('"', "'")  # noqa: E731  # a double quote would end a Mermaid label
    goal = clean(clip(f["short"], 74))
    lines = [
        "# %s: %s" % (f["id"], clip(f["short"], 70)), "",
        "**Component**: %s | **Risk Level**: %s | **Finding**: %s" % (f["comp"], f["risk"], f["id"]), "",
        first_sentence(f["threat"]), "", "```mermaid", "flowchart TD",
        '    %s_root["%s"]' % (node, goal), '    %s_or1{{"OR"}}' % node,
        '    %s_sub1["Reach %s in the %s"]' % (node, comp["name"], comp["zone"]),
        '    %s_sub2["Rely on the weakness described in %s"]' % (node, f["id"]),
        '    %s_leaf1["A path exists from %s over %s"]' % (node, clean(peer[0]), clean(peer[1])),
        '    %s_leaf2["%s are accepted without an independent check"]' % (node, clean(comp["asset"].capitalize())),
        '    %s_leaf3["The weakness is present: %s"]' % (node, clean(clip(f["short"], 70))),
        '    %s_leaf4["No effective control observed: %s"]' % (node, clean(clip(f["mit_short"], 70))),
        "", "    %s_root --> %s_or1" % (node, node), "    %s_or1 --> %s_sub1" % (node, node), "    %s_or1 --> %s_sub2" % (node, node),
        "    %s_sub1 --> %s_leaf1" % (node, node), "    %s_sub1 --> %s_leaf2" % (node, node),
        "    %s_sub2 --> %s_leaf3" % (node, node), "    %s_sub2 --> %s_leaf4" % (node, node), "",
        "    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff",
        "    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff",
        "    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333",
        "    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333", "",
        "    class %s_root goal" % node, "    class %s_or1 orGate" % node, "    class %s_sub1,%s_sub2 subGoal" % (node, node),
        "    class %s_leaf1,%s_leaf2,%s_leaf3,%s_leaf4 leaf" % (node, node, node, node), "```"]
    return "\n".join(lines)


def tree_files(world: dict) -> dict:
    """attack-trees/: one file per Critical or High finding, plus the manifest the report agent reads (schema 1.0)."""
    files, entries = {}, []
    fresh = carried = regenerated = 0
    for f in world["findings"]:
        if f["risk"] not in ("Critical", "High"):
            continue
        path = "attack-trees/%s-attack-tree.md" % f["id"].lower()
        files[path] = tree_text(world, f)
        if f["status"] == STATUS_UNCHANGED:
            roll = label_below("sim:" + f["id"], 100)
            if roll < 90:
                action, similarity = "carried_forward", 0.80 + label_below("simv:" + f["id"], 19) / 100
                carried += 1
            else:
                action, similarity = "regenerated", 0.40 + label_below("simv:" + f["id"], 30) / 100
                regenerated += 1
        else:
            action, similarity = "generated_fresh", None
            fresh += 1
        entries.append({"finding_id": f["id"], "delta_status": f["status"], "action": action,
                        "similarity_score": similarity, "file_path": path})
    manifest = {"schema_version": "1.0", "rule_applied": "Rule 2", "attack_tree_count": len(entries), "trees": entries,
                "summary": {"fresh": fresh, "carried_forward": carried, "regenerated": regenerated}}
    files["attack-trees/.manifest.json"] = dumps(manifest, indent=2, sort_keys=False)
    return files


# --------------------------------------------------------------------------- the architecture description
def architecture_text(world: dict) -> str:
    comps, zones = world["components"], world["zones"]
    lines = ["# %s: architecture" % PLATFORM, "",
             "The %s is a multi-agent system that turns operator requests into planned, reviewed and audited shipment actions. "
             "Operators submit requests through a web portal. An intake agent structures each request, a planner decomposes it, "
             "a router assigns subtasks to worker agents, and a reviewer presents the result for approval. Agents reach carrier "
             "systems only through one tool server, and every approval and tool call is written to an append-only ledger." % PLATFORM, ""]
    if world["cfg"]["mermaid"]:
        lines += ["## Diagram", "", "```mermaid", "flowchart LR"]
        for zone in zones:
            lines.append('    subgraph %s["%s"]' % (zone["name"].replace(" ", "_"), zone["name"]))
            for name in zone["members"]:
                tags = world.get("asset_tags", {}).get(name, ())
                label = "%s<br/>[asset:%s]" % (name, ",".join(sorted(tags))) if tags else name
                lines.append('        %s["%s"]' % (name.replace("-", "_"), label))
            lines.append("    end")
        for source, dest, data, _ in world["flows"]:
            lines.append('    %s -->|"%s"| %s' % (source.replace("-", "_"), clip(data, 40), dest.replace("-", "_")))
        lines += ["```", ""]
    lines += ["## Components", ""]
    for comp in comps:
        lines.append("- **%s** (%s, %s): %s." % (comp["name"], comp["dfd"].lower(), comp["zone"], comp["desc"]))
    lines += ["", "## Trust zones", ""]
    for zone in zones:
        lines.append("- **%s** (%s): %s." % (zone["name"], zone["level"].lower(), ", ".join(zone["members"])))
    lines += ["", "## Data flows", ""]
    for source, dest, data, proto in world["flows"]:
        lines.append("- %s sends %s to %s over %s." % (source, data.lower(), dest, proto))
    note = ("A component whose diagram label ends in an asset block carries those asset-sensitivity tags."
            if world.get("asset_tags") else "No component in this description carries an asset-sensitivity tag.")
    lines += ["", "## Notes", "", note + " The platform and every name in it are invented for testing."]
    return "\n".join(lines)

# --------------------------------------------------------------------------- risk-scores.md
SCORING_METHOD = """## 5. Scoring Methodology

This section documents the quantitative scoring model behind the scores in this report.

### 5.1 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity from the CVSS 3.1 base metrics, with the full vector shown for each finding. |
| **Exploitability** | 30% | Practical feasibility from known techniques, complexity, tooling and skill. |
| **Scalability** | 15% | Potential for automated, large-scale use from scriptability, scope, resources and detection difficulty. |
| **Reachability** | 20% | Exposure of the component within the trust boundary architecture, derived from its trust zone. |

### 5.2 Composite Score Formula

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The composite is rounded to one decimal place and falls in the range 0.0 to 10.0.

### 5.3 Severity Band Mapping

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band.

### 5.4 Data Sources

- **Threat findings**: parsed from `threats.md`. All original metadata is preserved.
- **Trust zone data**: taken from the trust zone table of `threats.md` for reachability scoring.
- **Category default vectors**: CVSS 3.1 baselines per threat category, refined for each finding.

### 5.5 Reproducibility

The composite formula, weights and band mapping are deterministic. Each dimension score carries a tolerance of +/- 0.5 between runs.
"""


def _category_name(prefix: str) -> str:
    return PREFIX_CATEGORY[prefix]


def render_risk_scores_md(world: dict) -> str:
    scores, cfg = build_scores(world), world["cfg"]
    findings = world["findings"]
    order = sorted(findings, key=lambda f: (-scores[f["id"]]["composite"], prefix_rank(f["id"])))
    bands = ("Critical", "High", "Medium", "Low")
    counts = [sum(1 for f in findings if scores[f["id"]]["band"] == band) for band in bands]
    share = largest_remainder(counts)
    best = {}
    for f in findings:
        entry = best.setdefault(f["comp"], [0, 0])
        entry[0] += 1
        entry[1] = max(entry[1], scores[f["id"]]["composite"])
    top = sorted(best.items(), key=lambda kv: (-kv[1][1], -kv[1][0], kv[0]))[0]
    peer_of = {}
    for group in world["groups"]:
        for member in group["members"][1:]:
            peer_of[member["id"]] = (group["members"][0]["id"], group["id"])
    out = ["---", 'schema_version: "1.0"', 'date: "%s"' % cfg["dates"]["scores"], 'source_file: "baseline/threats.md"',
           'classification: "confidential"', "scoring_weights:", "  cvss_base: 0.35", "  exploitability: 0.30",
           "  scalability: 0.15", "  reachability: 0.20", "baseline:", "  source: null", "  inherited_count: null",
           "  fresh_count: null", "---", "", "# Risk Scores Report", "",
           "## 1. Executive Summary", "",
           "**%d** threats scored | **%d** Critical | **%d** High | **%d** Medium | **%d** Low" % ((len(findings),) + tuple(counts)), "",
           "**Highest-Risk Component**: %s %s %d finding(s), max composite %s" % (top[0], EM, top[1][0], fmt1(top[1][1])), "",
           table(("Metric", "Value"), (("Scoring date", cfg["dates"]["scores"]), ("Source file", "`baseline/threats.md`"), ("Schema version", "1.0"))),
           "", "**Severity Distribution:**", "",
           table(("Severity", "Count", "Percentage"),
                 [(b, c, pct(s)) for b, c, s in zip(bands, counts, share)] + [("**Total**", "**%d**" % len(findings), "**100%**")]),
           "", "> Trust zone data was available for every component, so no reachability value was defaulted.", "", "---", "",
           "## 2. Scored Threat Table", "",
           "Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.", "",
           table(("ID", "Source", "Component", "Threat", "CVSS", "Exploit.", "Scale.", "Reach.", "Composite", "Severity", "SLA", "Disposition"),
                 [(f["id"], scores[f["id"]].get("source", "fresh"), f["comp"], clip(f["short"], 64), fmt1(scores[f["id"]]["cvss"]), fmt1(scores[f["id"]]["expl"]),
                   fmt1(scores[f["id"]]["scale"]), fmt1(scores[f["id"]]["reach"]), fmt1(scores[f["id"]]["composite"]),
                   scores[f["id"]]["band"], scores[f["id"]]["sla"], scores[f["id"]]["disposition"]) for f in order]),
           "", "> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored "
           "independently. Correlated peer findings inherit the primary's scores to keep the group consistent.", "", "---", "",
           "## 3. Dimensional Breakdown", "",
           "Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.", ""]
    for f in order:
        s = scores[f["id"]]
        comp = world["by_name"][f["comp"]]
        vector_text = "`%s`" % s["vector"] if s["vector"] is not None else EM  # a seeded variant row may have no vector
        out += ["### %s %s %s" % (f["id"], EM, f["comp"]), "", "**Threat**: %s" % first_sentence(f["threat"]), "",
                "**Category**: %s | **Original Risk Level**: %s | **Composite**: %s (%s)" % (
                    _category_name(f["prefix"]), f["risk"], fmt1(s["composite"]), s["band"]), ""]
        if f["id"] in peer_of:
            lead, group_id = peer_of[f["id"]]
            out += ["**Correlation Group**: Scores inherited from primary finding %s (%s). Dimensional detail is recorded on the primary." % (lead, group_id),
                    "", "**Score**: %s | **Vector**: %s" % (fmt1(s["cvss"]), vector_text), "", "---", ""]
            continue
        metrics = dict(part.split(":") for part in s["vector"].split("/")[1:]) if s["vector"] is not None else {}
        out += ["#### CVSS 3.1 Base", "", "**Score**: %s | **Vector**: %s" % (fmt1(s["cvss"]), vector_text), ""]
        if metrics:
            out += [table(("Metric", "Value", "Rationale"),
                          [(label, names[metrics[key]], why[metrics[key]]) for key, label, names, why in CVSS_METRICS]), ""]
        out += ["#### Exploitability", "", "**Score**: %s (average of sub-dimensions)" % fmt1(s["expl"]), "",
                table(("Sub-Dimension", "Score", "Rationale"),
                      [(name, v, phrases[_tier(v)]) for (name, phrases), v in zip(EXPLOIT_PARTS, s["expl_sub"])]), "",
                "#### Scalability", "", "**Score**: %s (average of sub-dimensions)" % fmt1(s["scale"]), "",
                table(("Sub-Dimension", "Score", "Rationale"),
                      [(name, v, phrases[_tier(v)]) for (name, phrases), v in zip(SCALE_PARTS, s["scale_sub"])]), "",
                "#### Reachability", "", "**Score**: %s | **Trust Zone**: %s (%s)" % (fmt1(s["reach"]), comp["zone"], ZONE_LEVEL[comp["zone"]]), "",
                "%s sits in the %s. The zone baseline is %s and the refinement for this finding gives %s." % (
                    f["comp"], comp["zone"], fmt1(ZONE_REACH[comp["zone"]]), fmt1(s["reach"])), "", "---", ""]
    out += ["## 4. Governance Fields", "",
            "Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.", "",
            table(("ID", "Severity", "Owner", "SLA", "Disposition", "Review Date"),
                  [(f["id"], scores[f["id"]]["band"], scores[f["id"]].get("owner", "Unassigned"), scores[f["id"]]["sla"], scores[f["id"]]["disposition"],
                    scores[f["id"]]["review"]) for f in order]), "", "---", "", SCORING_METHOD]
    return "\n".join(out)


# --------------------------------------------------------------------------- compensating-controls.md
CONTROLS_METHOD = """## 6. Methodology

This section documents the compensating controls analysis methodology used to produce this report.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

```
Residual Score = Inherent Score * (1 - Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0], rounded half-up to one decimal place and mapped to severity bands with the thresholds used for risk scoring.

### 6.4 Data Sources

- **Scored threats**: parsed from `risk-scores.md` (canonical) or `risk-scores.sarif` (fallback).
- **Target codebase**: scanned through the `--target` path, with heuristic directories prioritized when no architecture mapping exists.
- **STRIDE-to-control mapping**: the canonical mapping from threat categories to control categories drives which controls are searched for.

### 6.5 Limitations

- Static analysis only: runtime control behavior is not evaluated.
- 200-file read budget: large codebases may have directories skipped with warnings.
- Files over 5,000 tokens are truncated to security-relevant sections.
- Binary reduction factors approximate control impact.
"""
EFFECTIVENESS_ROWS = {
    "moderate": (("Coverage", "Moderate", "Applied on the main request path of the protected components"),
                 ("Configuration", "Adequate", "Defaults have been reviewed and tightened"),
                 ("Currency", "Current", "Built on maintained primitives"),
                 ("Completeness", "Partial", "Some secondary paths are not covered")),
    "weak": (("Coverage", "Limited", "Applied on part of the request path only"),
             ("Configuration", "Basic", "Defaults are mostly unchanged"),
             ("Currency", "Current", "Built on maintained primitives"),
             ("Completeness", "Low", "Several paths and components are not covered")),
}
EFFORT_WHY = {"Low": "a configuration change or a small addition", "Medium": "a new module and its tests",
              "High": "a cross-cutting change that touches several components"}


ACCEPTANCE_TEXT = {
    "authentication": "Acceptance check: a request that carries a missing, expired or mismatched credential is rejected with a logged reason, and a valid request still succeeds.",
    "access-control": "Acceptance check: a caller without the entitlement is denied for every object and action, including through indirect paths, and the denial is recorded.",
    "input-validation": "Acceptance check: malformed, oversized and unexpected fields are rejected before any side effect, and a regression test covers each rejected shape.",
    "encryption": "Acceptance check: a scan of the link or store shows only current protocol versions and encrypted content, and keys rotate without downtime.",
    "rate-limiting": "Acceptance check: a load test above the configured limits is shed with a clear status while normal traffic keeps its latency budget.",
    "logging-audit": "Acceptance check: every state change produces one complete record that an operator cannot edit, and a gap in the sequence raises an alert.",
    "csrf-protection": "Acceptance check: a state-changing request without a valid anti-forgery token is refused, and legitimate sessions are unaffected.",
    "csp-security-headers": "Acceptance check: a header scan of every response shows the policy, and any page that needs an exception has a recorded justification.",
}
ROLLOUT_TEXT = (
    "Roll the change out behind a flag, watch error rates for one release and remove the flag once no regression is seen.",
    "Ship to the internal environment first, compare behaviour with the previous release and promote after reviewing the first week of records.",
    "Apply the change to the most exposed instances first, then to the rest, and keep the previous configuration available for a quick rollback.",
    "Coordinate the change with the owners of dependent services so that none of them relies on the behaviour being removed.",
)


def recommendation_parts(world: dict, finding: dict, outcome: dict) -> dict:
    """The four fields a recommendation carries, for a finding whose control is partial or missing."""
    wanted = control_category_ids(finding["prefix"])
    category = wanted[label_below("rec:" + finding["id"], len(wanted))]
    core, patterns, effort_missing, effort_partial = RECOMMENDATION_BANK[category]
    comp = world["by_name"][finding["comp"]]
    title = CONTROL_TITLE[category].lower()
    addressed = first_sentence(finding["threat"])
    tail = " ".join((ACCEPTANCE_TEXT[category], ROLLOUT_TEXT[label_below("rollout:" + finding["id"], len(ROLLOUT_TEXT))]))
    if outcome["status"] == "partial":
        control = outcome["control"]
        return {"what": "Harden the existing %s control: %s on the paths of %s that it does not yet cover. The current implementation is recorded at "
                        "%s:%d and covers the main request path. Extend it to the secondary paths and add a test that exercises each of them. "
                        "This addresses: %s %s" % (title, core[0].lower() + core[1:], comp["name"], control["path"], control["line"], addressed, tail),
                "path": control["path"],
                "why": "the existing control lives here and covers the main request path of %s, and the owners of that module already review changes to it" % comp["name"],
                "patterns": patterns, "effort": effort_partial,
                "effort_why": "the foundation exists, so the work is to extend coverage, add tests and confirm the secondary paths behave the same way"}
    return {"what": "Implement %s for %s. %s. Place the control where %s are first received, so that nothing downstream has to repeat the check. "
                    "This addresses: %s %s" % (title, comp["name"], core, comp["asset"], addressed, tail),
            "path": recommendation_path(comp["name"], category),
            "why": "a new module next to the code that handles %s, so the owners of that code review the control with it" % comp["asset"],
            "patterns": patterns, "effort": effort_missing,
            "effort_why": "%s, including the tests that keep the control in place after later changes" % EFFORT_WHY[effort_missing]}


def control_recommendation(world: dict, finding: dict, outcome: dict) -> tuple:
    """(recommendation text, effort) for SARIF; ('', '') when the control is found."""
    if outcome["status"] == "found":
        return "", ""
    p = recommendation_parts(world, finding, outcome)
    return "%s Suggested location: %s. Reference patterns: %s." % (p["what"], p["path"], p["patterns"]), p["effort"]


def render_controls_md(world: dict) -> str:
    scores, controls = build_scores(world), build_controls(world)
    outcome, findings, cfg = controls["by_finding"], world["findings"], world["cfg"]
    total = len(findings)
    status_counts = {s: sum(1 for f in findings if outcome[f["id"]]["status"] == s) for s in ("found", "partial", "missing")}
    share = largest_remainder([status_counts["found"], status_counts["partial"], status_counts["missing"]])
    inherent = sum(scores[f["id"]]["composite"] for f in findings)
    residual = sum(outcome[f["id"]]["residual"] for f in findings)
    reduction = half_up((inherent - residual) * 1000, inherent)
    gaps = [f for f in findings if outcome[f["id"]]["status"] == "missing"]
    worst = sorted(gaps, key=lambda f: (-scores[f["id"]]["composite"], prefix_rank(f["id"])))[0]
    out = ["---", 'schema_version: "1.0"', 'date: "%s"' % cfg["dates"]["controls"], 'source_file: "baseline/risk-scores.md"',
           'target_path: "stub-codebase"', 'classification: "security"', 'rescan_scope: "full"', "carry_forward_count: null", "---", "",
           "# Compensating Controls Report", "", "## 1. Executive Summary", "",
           "**%d** threats analyzed | **%d** Control Found | **%d** Partial Control | **%d** No Control Found" % (
               total, status_counts["found"], status_counts["partial"], status_counts["missing"]), "",
           "**Coverage**: %s Found | %s Partial | %s Missing" % (pct(share[0]), pct(share[1]), pct(share[2])), "",
           "**Risk Reduction**: %s inherent -> %s residual (**%s** reduction)" % (fmt1(inherent), fmt1(residual), pct(reduction)), "",
           "**Highest-Risk Unmitigated Finding**: %s %s %s %s Composite %s (%s)" % (
               worst["id"], EM, worst["comp"], EM, fmt1(scores[worst["id"]]["composite"]), scores[worst["id"]]["band"]), "",
           table(("Metric", "Value"), (("Analysis date", cfg["dates"]["controls"]), ("Source file", "`baseline/risk-scores.md`"),
                                       ("Target codebase", "`stub-codebase`"), ("Schema version", "1.0"))), "",
           "**Coverage Distribution:**", "",
           table(("Status", "Count", "Percentage"),
                 (("Control Found", status_counts["found"], pct(share[0])), ("Partial Control", status_counts["partial"], pct(share[1])),
                  ("No Control Found", status_counts["missing"], pct(share[2])), ("**Total**", "**%d**" % total, "**100%**"))),
           "", "> Analysis completed within the file-read budget; no directories were skipped.", "", "---", "",
           "## 2. Coverage Matrix", "",
           "Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.", ""]
    matrix_header = ("Threat ID", "CF", "Component", "Threat", "Inherent Score", "Inherent Severity", "Control Status", "Residual Score", "Residual Severity")
    for band in ("Critical", "High", "Medium", "Low"):
        rows = sorted([f for f in findings if outcome[f["id"]]["band"] == band],
                      key=lambda f: (-outcome[f["id"]]["residual"], prefix_rank(f["id"])))
        if not rows:
            continue
        out += ["### %s Residual Severity" % band, "",
                table(matrix_header, [(f["id"], EM, f["comp"], clip(first_sentence(f["threat"]), 190), fmt1(scores[f["id"]]["composite"]), scores[f["id"]]["band"],
                                       CONTROL_STATUS_TEXT[outcome[f["id"]]["status"]], fmt1(outcome[f["id"]]["residual"]), band) for f in rows]), ""]
    resid_counts = [sum(1 for f in findings if outcome[f["id"]]["band"] == b) for b in ("Critical", "High", "Medium", "Low")]
    resid_share = largest_remainder(resid_counts)
    out += ["### Summary Statistics", "",
            table(("Residual Severity", "Count", "Percentage"),
                  [(b, c, pct(s)) for b, c, s in zip(("Critical", "High", "Medium", "Low"), resid_counts, resid_share)] + [("**Total**", "**%d**" % total, "**100%**")]),
            "", "---", "", "## 3. Control Details", "",
            "Per-control evidence showing detected security controls with their location, code evidence and threat coverage, grouped by control category.", ""]
    for cid, title, _ in CONTROL_CATEGORIES:
        for d in controls["defs"]:
            users = [f for f in findings if outcome[f["id"]]["control"] is d]
            if d["category"] != cid or not users:
                continue
            out += ["### %s" % title, "", "#### %s %s %s" % (d["id"], EM, d["summary"]), "",
                    "**Category**: %s | **Status**: %s | **Effectiveness**: %s" % (
                        title, "Control Found" if d["rating"] == "moderate" else "Partial Control", d["rating"].capitalize()), "",
                    "**Detected in**: `%s:%d`" % (d["path"], d["line"]), "", "```python"] + list(d["snippet"]) + [
                    "```", "", "> Code snippet limited to 5 lines centered on the control implementation.", "",
                    "**Effectiveness Assessment**:", "", table(("Dimension", "Rating", "Rationale"), EFFECTIVENESS_ROWS[d["rating"]]), "",
                    "**Threats Mitigated by This Control**:", "",
                    table(("Threat ID", "Component", "Threat", "Inherent Score", "Reduction Factor", "Residual Score"),
                          [(f["id"], f["comp"], clip(f["short"], 60), fmt1(scores[f["id"]]["composite"]),
                            "0.%02d" % outcome[f["id"]]["factor"], fmt1(outcome[f["id"]]["residual"])) for f in users]), "", "---", ""]
    out += ["## 4. Recommendations", "",
            "Actionable recommendations for threats classified as \"No Control Found\" or \"Partial Control\", sorted by composite risk score descending.", ""]
    needing = sorted([f for f in findings if outcome[f["id"]]["status"] != "found"],
                     key=lambda f: (-scores[f["id"]]["composite"], prefix_rank(f["id"])))
    number = 0
    for title, bands in (("Critical / High Risk Gaps", ("Critical", "High")), ("Medium Risk Gaps", ("Medium",)), ("Low Risk Gaps", ("Low",))):
        chosen = [f for f in needing if scores[f["id"]]["band"] in bands]
        if not chosen:
            continue
        out += ["### " + title, ""]
        for f in chosen:
            number += 1
            p = recommendation_parts(world, f, outcome[f["id"]])
            out += ["#### %d. %s %s %s (Composite: %s, %s)" % (number, f["id"], EM, f["comp"], fmt1(scores[f["id"]]["composite"]), scores[f["id"]]["band"]), "",
                    "**Current Status**: %s" % CONTROL_STATUS_TEXT[outcome[f["id"]]["status"]], "", "**What to Implement**: %s" % p["what"], "",
                    "**Where to Implement**: `%s` %s %s" % (p["path"], EM, p["why"]), "", "**Reference Patterns**: %s" % p["patterns"], "",
                    "**Effort Estimate**: %s %s %s" % (p["effort"], EM, p["effort_why"]), "", "---", ""]
    shifts = {}
    for f in findings:
        a, b = scores[f["id"]]["band"], outcome[f["id"]]["band"]
        shifts.setdefault((a, b) if a != b else None, []).append(f["id"])
    shift_rows = []
    for a, b in (("Critical", "High"), ("Critical", "Medium"), ("Critical", "Low"), ("High", "Medium"), ("High", "Low"), ("Medium", "Low")):
        ids = shifts.get((a, b), [])
        shift_rows.append(("%s -> %s" % (a, b), len(ids), ", ".join(ids[:3]) or EM))
    none_ids = shifts.get(None, [])
    shift_rows += [("No Shift", len(none_ids), ", ".join(none_ids[:3]) or EM), ("**Total**", "**%d**" % total, "")]
    inherent_counts = [sum(1 for f in findings if scores[f["id"]]["band"] == b) for b in ("Critical", "High", "Medium", "Low")]
    compare = [(b, i, r, "%+d" % (r - i)) for b, i, r in zip(("Critical", "High", "Medium", "Low"), inherent_counts, resid_counts)]
    out += ["## 5. Residual Risk Summary", "",
            "Comparison of inherent risk (before controls) to residual risk (after controls).", "", "### Aggregate Risk Reduction", "",
            table(("Metric", "Value"), (("Total Inherent Risk Score", fmt1(inherent)), ("Total Residual Risk Score", fmt1(residual)),
                                        ("Delta", fmt1(inherent - residual)), ("Overall Reduction", pct(reduction)))), "",
            "### Per-Severity-Band Shift", "", table(("Shift", "Count", "Examples"), shift_rows), "",
            "### Severity Distribution Comparison", "",
            table(("Severity", "Inherent Count", "Residual Count", "Change"), compare + [("**Total**", "**%d**" % total, "**%d**" % total, "")]), "",
            "### Reduction Factor Reference", "",
            table(("Control Status", "Reduction Factor", "Formula", "Description"), (
                ("Control Found", "0.50", "Inherent * 0.50", "Control detected with evidence. Residual is 50% of inherent."),
                ("Partial Control", "0.25", "Inherent * 0.75", "Control exists but incomplete coverage. Residual is 75% of inherent."),
                ("No Control Found", "0.00", "Inherent * 1.00", "No matching control detected. Residual equals inherent."))),
            "", "---", "", CONTROLS_METHOD]
    return "\n".join(out)

# --------------------------------------------------------------------------- T040: the PR 1 variants
# A variant is a directory of scenarios. A scenario is one scorer run: the baseline directory the renderer reads, the
# run's own threats.md, the architecture file when the case has one, and expected-outcomes.json, which states what the
# renderer must correct, flag or leave alone, field by field. Every expected value is worked out here from first
# principles (the CVSS calculator above, half-up composites, ADR-050 D9 and D10), never read from a renderer.
#
# The file format is tachi.fixture-expected/1:
#   scenario, variant, stage, run{...}, baseline{...}, tag_source{...}, routing{...}, agent_inputs{id: payload},
#   findings{id: {case, treatment, stored{...}, rendered{...}, flags[...], normalized}}, unflagged[ids],
#   counts{...}, notes[...], flag_reading[...]
# A flag object is {flag, kind, field, cause, stored, rendered, basis}. basis is "pinned" (the string is in the scorer's
# closed flag vocabulary, contracts/module-signatures.md, which the architect ruled at W1) or "optional" (the renderer
# may add it or not, and a test accepts both). A finding carries at most one flag per kind and field.
RUN_DATE = "2026-11-23"   # the --date input of every scenario
SCORED_ON = "2026-11-09"  # the day the baselines scored: their own front-matter date

METRIC_ORDER = ("AV", "AC", "PR", "UI", "S", "C", "I", "A")
METRIC_CHOICES = (("AV", "NALP"), ("AC", "LH"), ("PR", "NLH"), ("UI", "NR"), ("S", "UC"), ("C", "HLN"), ("I", "HLN"), ("A", "HLN"))
TAG_FORCES = {  # schemas/risk-scoring.yaml, asset_modifiers.tags
    "pii": (("C", "H"),), "phi": (("C", "H"),), "auth": (("C", "H"), ("I", "H")),
    "secrets": (("C", "H"), ("I", "H")), "financial": (("I", "H"),), "safety": (("A", "H"),),
}
LEVEL_RANK = {"N": 0, "L": 1, "H": 2}
CEILING = 92  # the asset-modifier ceiling, in tenths
BAND_ORDER = ("Low", "Medium", "High", "Critical")  # ascending
REACH_BASELINE = {"Untrusted": 90, "Semi-trusted": 55, "Trusted": 25}  # reachability-analysis.md, in tenths
REACH_KEYWORDS = (  # zone-name substrings and their adjustments, in tenths; every matching keyword counts
    (("internet", "public", "external"), 5), (("user", "client"), 5), (("dmz", "perimeter", "gateway"), 5),
    (("internal", "backend", "core"), -5), (("database", "storage", "data store"), -5),
)
PART_TRUST = {"Untrusted": "Untrusted", "Semi-trusted": "Semi-Trusted", "Trusted": "Trusted"}  # the part contract's spelling

# D9's four causes name the step that produced a field's new value. The architect ruled them at W1 and closed the scorer's flag
# vocabulary in contracts/module-signatures.md. They live here, once: a rename is these four lines and a regeneration.
CAUSE_VECTOR = "vector"              # cvss_base
CAUSE_ARITHMETIC = "arithmetic"      # composite_score
CAUSE_BAND_MAPPING = "band-mapping"  # severity_band
CAUSE_FOLLOWS_BAND = "follows-band"  # remediation_sla, risk_disposition, review_date

FLAG_READING = (
    "A flag is kind:field:cause, and the field is the value whose status the flag describes, by its schemas/risk-scoring.yaml name: "
    "cvss_base, composite_score, severity_band, remediation_sla, risk_disposition, review_date, reachability.",
    "The cause of a 'corrected' flag names the step that produced the field's new value: a changed cvss_base is '%s', a changed "
    "composite_score is '%s', a changed severity_band is '%s' (or 'rounding' when only rounding moved the band), and a changed "
    "remediation_sla, risk_disposition or review_date is '%s'. Where a fallback set the review date, 'baseline-date' or 'clock-restarted' "
    "replaces '%s'. A change that the asset tags alone explain takes 'retagged' and the cause 'asset-tags' on every field it moves "
    "(ruling A). A finding carries at most one flag per kind and field." % (
        CAUSE_VECTOR, CAUSE_ARITHMETIC, CAUSE_BAND_MAPPING, CAUSE_FOLLOWS_BAND, CAUSE_FOLLOWS_BAND),
    "A rounding-only composite difference is normalized and counted and never flagged: only a band that it moves is flagged, "
    "as severity_band:rounding.",
    "basis 'pinned': the string is in the closed vocabulary of contracts/module-signatures.md, and a test requires it. 'optional': the "
    "renderer may add the flag or not, and a test accepts both. Only the flags on a value that the input's form lacks are optional, because "
    "the cause for those is open (S-12(b), named by T032).",
    "A flag that the renderer adds and that is not listed is a defect of one side: the list is complete for the cases here.",
)


def vector_parts(vector: str) -> dict:
    return dict(part.split(":") for part in vector.split("/")[1:])


def vector_text(parts: dict) -> str:
    return "CVSS:3.1/" + "/".join("%s:%s" % (key, parts[key]) for key in METRIC_ORDER)


def elevate_vector(vector: str, tags: Sequence) -> str:
    """The vector with every tag's forced bits raised to H (floor only), as asset-modifiers.md and tachi_scoring.elevate do."""
    parts = vector_parts(vector)
    for tag in tags:
        for key, level in TAG_FORCES[tag]:
            if LEVEL_RANK[level] > LEVEL_RANK[parts[key]]:
                parts[key] = level
    return vector_text(parts)


_CVSS_CACHE: dict = {}


def cvss_of(vector: str) -> int:
    if vector not in _CVSS_CACHE:
        _CVSS_CACHE[vector] = cvss_tenths(vector)
    return _CVSS_CACHE[vector]


_ALL_VECTORS: list = []


def every_vector() -> list:
    """All 2,592 base vectors in one fixed order (the metric choices, left to right)."""
    if not _ALL_VECTORS:
        for choice in itertools.product(*(values for _, values in METRIC_CHOICES)):
            _ALL_VECTORS.append("CVSS:3.1/" + "/".join("%s:%s" % (key, value) for (key, _), value in zip(METRIC_CHOICES, choice)))
    return _ALL_VECTORS


def category_bounds(category: str) -> tuple:
    """The finding's own category bound: its default score minus and plus 1.0, in tenths (max(0, d - 10), min(100, d + 10))."""
    default = _CATEGORY_DEFAULT_TENTHS[category]
    return max(0, default - 10), min(100, default + 10)


def clamp(value: int, bounds: tuple) -> int:
    return max(bounds[0], min(bounds[1], value))


def chain_tenths(vector: str, tags: Sequence, bounds) -> int:
    """D10's chain for a fresh finding or a renderer-form row: base(v), clamped to the stored bounds when there are some,
    then R-25: when a tag forces a bit, the larger of that and the elevated score capped at 9.2."""
    assessed = cvss_of(vector)
    if bounds is not None:
        assessed = clamp(assessed, bounds)
    if tags:
        assessed = max(assessed, min(cvss_of(elevate_vector(vector, tags)), CEILING))
    return assessed


def legacy_check(stored: int, vector, category: str, tags: Sequence) -> tuple:
    """D10's legacy list, in order, the first matching step deciding. Returns (rendered tenths, (kind, field, cause) or None, step)."""
    if vector is None:
        return stored, ("unverifiable", "cvss_base", "no-vector"), 1
    base = cvss_of(vector)
    candidates = (base, clamp(base, category_bounds(category)))
    forcing = bool(tags)
    elevated = elevate_vector(vector, tags) if forcing else vector
    elevated_base = cvss_of(elevated)

    def outcome(assessed: int) -> int:
        return max(assessed, min(elevated_base, CEILING)) if forcing else assessed

    if forcing and elevated == vector and CEILING < stored <= base:
        return stored, ("unchecked", "cvss_base", "assessed-unrecorded"), 2
    if any(stored == outcome(a) for a in candidates) or (forcing and stored == CEILING and elevated_base > CEILING):
        return stored, None, 3
    if forcing:
        for a in candidates:
            if stored == a and a < outcome(a):
                return outcome(a), ("retagged", "cvss_base", "asset-tags"), 4
    others = [clamp(base, category_bounds(other)) for other in sorted(_CATEGORY_DEFAULT_TENTHS) if other != category]
    if stored in others:
        return stored, ("unchecked", "cvss_base", "bound-n17c"), 5
    if forcing and CEILING < stored < elevated_base:
        return stored, ("unchecked", "cvss_base", "assessed-unrecorded"), 5
    return outcome(base), ("corrected", "cvss_base", CAUSE_VECTOR), 6


def reach_value(zone_name: str, level: str, auth: int, net: int) -> int:
    """Reachability in tenths: the trust level's baseline, the zone-name keywords, then the barrier counts, clamped to the level's range."""
    value = REACH_BASELINE[level]
    lowered = zone_name.lower()
    for words, adjustment in REACH_KEYWORDS:
        value += adjustment * sum(1 for word in words if word in lowered)
    rng = REACH_RANGE[level]
    return clamp(clamp(value, rng) - 15 * min(auth, 3) - 10 * min(net, 3), rng)


def sla_day_count(sla: str) -> int:
    number = int(sla[:-1])
    return -(-number // 24) if sla.endswith("h") else number


def mean_tenths(values: Sequence) -> int:
    """The mean of four 0-10 sub-scores in tenths, half-up (the scorer's q1 over an exact quarter)."""
    return half_up(25 * sum(values), 10)


def make_flag(kind: str, field, cause, stored=None, rendered=None, basis="pinned") -> dict:
    """A flag object. basis: pinned (in the closed vocabulary) or optional (see the header)."""
    text = ":".join(part for part in (kind, field, cause) if part is not None)
    return {"flag": text, "kind": kind, "field": field, "cause": cause, "stored": stored, "rendered": rendered, "basis": basis}


def stored_values(row: dict) -> dict:
    """A row's values in the renderer's field names, as text (a missing vector is null)."""
    return {"cvss_vector": row["vector"], "cvss_base": fmt1(row["cvss"]), "exploitability": fmt1(row["expl"]),
            "scalability": fmt1(row["scale"]), "reachability": fmt1(row["reach"]), "composite_score": fmt1(row["composite"]),
            "severity_band": row["band"], "remediation_sla": row["sla"], "risk_disposition": row["disposition"],
            "review_date": row["review"], "risk_owner": row.get("owner", "Unassigned")}


def carried_expectation(row: dict, ctx: dict) -> dict:
    """What the renderer does with one carried finding (ADR-050 D9 steps 1 to 4, D10, ruling A), from its stored row.

    ctx: tags (this run's tags on the finding's component), baseline_date (the baseline file's front-matter date or None),
    compound_zones (zones whose Section 2 label is ambiguous). Returns {rendered, flags, normalized, step, band_change}."""
    tags = tuple(ctx.get("tags", ()))
    category = PREFIX_CATEGORY[row["prefix"]]
    flags = []
    stored = stored_values(row)

    # The CVSS chain. cvss_baseline is the value that the baseline's own tags give, to tell a retag from a correction.
    cvss_retagged = False
    if row["form"] == "renderer":
        cvss = chain_tenths(row["vector"], tags, row.get("bounds"))
        cvss_baseline = chain_tenths(row["vector"], row["tags_used"], row.get("bounds"))
        step = "renderer"
        if cvss != row["cvss"]:
            cvss_retagged = cvss_baseline == row["cvss"]
            flags.append(make_flag("retagged" if cvss_retagged else "corrected", "cvss_base", "asset-tags" if cvss_retagged else CAUSE_VECTOR,
                                   fmt1(row["cvss"]), fmt1(cvss)))
    else:
        cvss, found, step = legacy_check(row["cvss"], row["vector"], category, tags)
        cvss_baseline = row["cvss"]
        if found is not None:
            cvss_retagged = found[0] == "retagged"
            flags.append(make_flag(found[0], found[1], found[2], fmt1(row["cvss"]), fmt1(cvss)))  # an unchecked or unverifiable score is kept
        if row.get("md_vector") is not None and row.get("sarif_vector") not in (None, row.get("md_vector")):
            flags.append(make_flag("input", "cvss_vector", "sources-disagree", row["sarif_vector"], row["md_vector"]))

    # Reachability (a legacy row's only range check, R-10).
    if row["form"] == "legacy":
        level = ZONE_LEVEL[row["zone"]]
        if row["zone"] in ctx.get("compound_zones", ()):
            flags.append(make_flag("unchecked", "reachability", "compound-trust-label", fmt1(row["reach"]), None))
        elif not REACH_RANGE[level][0] <= row["reach"] <= REACH_RANGE[level][1]:
            flags.append(make_flag("input", "reachability", "out-of-range", fmt1(row["reach"]), None))

    # The composite and the band.
    total = 35 * cvss + 30 * row["expl"] + 15 * row["scale"] + 20 * row["reach"]
    composite = half_up(total, 100)
    rounding_only = total % 100 == 50 and row["composite"] == composite - 1
    baseline_composite = composite_tenths(cvss_baseline, row["expl"], row["scale"], row["reach"])
    new_band = band_of(composite)
    normalized = False
    if composite != row["composite"] and not rounding_only:
        tags_explain = cvss_retagged and row["composite"] == baseline_composite
        flags.append(make_flag("retagged" if tags_explain else "corrected", "composite_score", "asset-tags" if tags_explain else CAUSE_ARITHMETIC,
                               fmt1(row["composite"]), fmt1(composite)))
    band_change = "none"
    if new_band != row["band"]:
        if rounding_only:
            band_change = "rounding"
            flags.append(make_flag("corrected", "severity_band", "rounding", row["band"], new_band))  # the composite's own change is normalized
        elif cvss_retagged and band_of(baseline_composite) == row["band"]:
            band_change = "retagged-up" if BAND_ORDER.index(new_band) > BAND_ORDER.index(row["band"]) else "retagged-down"
            flags.append(make_flag("retagged", "severity_band", "asset-tags", row["band"], new_band))
        else:
            band_change = "corrected"
            flags.append(make_flag("corrected", "severity_band", CAUSE_BAND_MAPPING, row["band"], new_band))
    elif rounding_only:
        normalized = True

    # Governance (R-5, R-31, ruling A).
    defaults = BAND_GOVERNANCE[row["band"]]
    # A missing SLA is a gap in the baseline, not a human's choice, so it is no override (R-31).
    sla_override, disposition_override = row["sla"] is not None and row["sla"] != defaults[0], row["disposition"] != defaults[2]
    if sla_override:
        flags.append(make_flag("override", "remediation_sla", "human", row["sla"], row["sla"]))
    if disposition_override:
        flags.append(make_flag("override", "risk_disposition", "human", row["disposition"], row["disposition"]))
    new_defaults = BAND_GOVERNANCE[new_band]
    sla = row["sla"] if sla_override else new_defaults[0]
    disposition = row["disposition"] if disposition_override else new_defaults[2]
    review = row["review"]
    follows = "asset-tags" if band_change.startswith("retagged") else CAUSE_FOLLOWS_BAND
    kind = "retagged" if band_change.startswith("retagged") else "corrected"
    rung = None
    if band_change != "none" and not sla_override:
        days = sla_day_count(sla)
        if band_change == "retagged-up":
            candidate = add_days(ctx["run_date"], days)
            review = row["review"] if row["review"] is not None and row["review"] < candidate else candidate
        else:  # a correction, a rounding move or a lowering: the original scoring date plus the new SLA (R-5)
            if row["form"] == "renderer":
                original = row["scored_on"]
            elif row["review"] is not None and row["sla"] is not None and re.fullmatch(r"[0-9]+[hd]", row["sla"]):
                original = add_days(row["review"], -sla_day_count(row["sla"]))
            else:
                original = None
            if original is not None:
                review = add_days(original, days)
            elif ctx.get("baseline_date"):
                review, rung = add_days(ctx["baseline_date"], days), ("corrected", "review_date", "baseline-date")
            elif row["review"] is not None:
                review, rung = row["review"], ("unchecked", "review_date", "scoring-date-unknown")
            else:
                review, rung = add_days(ctx["run_date"], days), ("corrected", "review_date", "clock-restarted")
    if sla != row["sla"] and not sla_override:
        # a missing SLA is a value that the input's form lacks: the cause for that is open (S-12(b)), so its flag is optional
        flags.append(make_flag(kind, "remediation_sla", follows, row["sla"], sla, basis="optional" if row["sla"] is None else "pinned"))
    if disposition != row["disposition"] and not disposition_override:
        flags.append(make_flag(kind, "risk_disposition", follows, row["disposition"], disposition))
    if rung is not None:  # a fallback's flag replaces follows-band: the review date carries one flag per kind
        flags.append(make_flag(rung[0], rung[1], rung[2], row["review"], review))
    elif review != row["review"]:
        flags.append(make_flag(kind, "review_date", follows, row["review"], review))

    rendered = dict(stored)
    rendered.update({"cvss_base": fmt1(cvss), "composite_score": fmt1(composite), "severity_band": new_band,
                     "remediation_sla": sla, "risk_disposition": disposition, "review_date": review})
    return {"rendered": rendered, "flags": flags, "normalized": normalized, "step": step, "band_change": band_change}


# --- worlds and rows -------------------------------------------------------------------------------------------------
GATED_COMPONENTS = PROFILES["gated"]["components"]
COMPOUND_LABEL = "Semi-trusted / Trusted"  # a Section 2 label that normalizes to two trust levels (N17)


def variant_profile(explicit: list, components: Sequence, resolved: Sequence = (), no_groups: bool = True) -> dict:
    """A profile whose findings are named one by one. Dates: the baselines scored on SCORED_ON, this run is RUN_DATE."""
    return {
        "components": tuple(components), "counts": {}, "resolved": tuple(resolved), "new_pm": 0, "updated_pm": 0, "critical_min": 0,
        "dates": {"threats": RUN_DATE, "baseline": SCORED_ON, "scores": SCORED_ON, "controls": SCORED_ON},
        "run_ids": {"threats": "2026-11-23T10-00-00", "baseline": "2026-11-09T10-00-00"},
        "trees": False, "mermaid": False, "architecture_file": "docs/security/architecture.md",
        "explicit": list(explicit), "no_groups": no_groups, "baseline_source": "baseline/threats.md",
    }


def spread(prefix: str, count: int, component_names: Sequence) -> list:
    """count findings of one prefix, dealt round-robin over the components that can carry it (inventory order)."""
    if prefix == "AGP":
        cycle = [name for name in ("planner-agent", "worker-2", "tool-server-1", "intake-agent") if name in component_names]
        return [("AGP", cycle[i % len(cycle)], None) for i in range(count)]
    comps = [comp for comp in COMPONENT_ROWS if comp[0] in component_names]
    pool = [{"name": row[0], "dfd": row[1], "ai": row[4], "traits": row[5], "index": index} for index, row in enumerate(comps)]
    slots = _slots(prefix, pool)
    return [(prefix, slots[i % len(slots)][0]["name"], slots[i % len(slots)][1]) for i in range(count)]


def settle(row: dict) -> dict:
    """Recompute a row's composite from its own cells, and its band and governance from the composite."""
    row["composite"] = composite_tenths(row["cvss"], row["expl"], row["scale"], row["reach"])
    return set_band(row, band_of(row["composite"]), row.get("scored_on", SCORED_ON))


def set_band(row: dict, band: str, scored_on: str = SCORED_ON) -> dict:
    sla, days, disposition = BAND_GOVERNANCE[band]
    row.update({"band": band, "sla": sla, "sla_days": days, "disposition": disposition, "review": add_days(scored_on, days)})
    return row


def awkward(row: dict) -> bool:
    """True when a row's composite is a rounding tie or sits on a band boundary: a clean role must be neither."""
    return composite_is_tie(row["cvss"], row["expl"], row["scale"], row["reach"]) or composite_on_boundary(row["composite"])


def sub_scores(total: int) -> tuple:
    """Four 1-10 sub-scores that sum to total, as even as they can be."""
    return tuple(total // 4 + (1 if i < total % 4 else 0) for i in range(4))


MEAN_OF = {total: mean_tenths(sub_scores(total)) for total in range(4, 41)}  # a sub-score total's mean, in tenths, worked out once


def make_rows(world: dict) -> dict:
    """The natural, internally consistent legacy row of every open finding: the baseline of a clean run."""
    scores = build_scores(world)
    rows = {}
    for f in world["findings"]:
        row = dict(scores[f["id"]])
        row.update({"id": f["id"], "prefix": f["prefix"], "comp": f["comp"], "zone": world["by_name"][f["comp"]]["zone"], "form": "legacy",
                    "md_vector": row["vector"], "sarif_vector": row["vector"], "owner": "Unassigned", "source": "fresh",
                    "md_form": "AB"[label_below("md-form:" + f["id"], 2)]})
        rows[f["id"]] = row
    return rows


def resolved_as_finding(world: dict, item: dict) -> dict:
    """A RESOLVED item as the baseline knew it: an open finding, so that the baseline's files can hold its row."""
    comp = world["by_name"][item["comp"]]
    return {"id": item["id"], "prefix": item["prefix"], "sub": item["sub"], "comp": item["comp"], "num": item["num"],
            "threat": item["threat"], "short": item["short"], "risk": item["risk"], "status": STATUS_UNCHANGED, "group": None,
            "primary": False, "layer": comp["layer"], "pattern": "none", "mit": "Remediate as described in the baseline report.",
            "mit_short": "Remediate as described in the baseline report.", "like": "MEDIUM", "imp": "MEDIUM", "ref": ""}


def clone_world(master: dict, **replace) -> dict:
    """A shallow copy of a cached world with some keys replaced, so that no scenario touches the cache."""
    world = dict(master)
    world.update(replace)
    return world


def baseline_world(master: dict, rows: dict, extra: Sequence = ()) -> dict:
    """The world as the baseline run saw it: the open findings and the ones that were resolved since, with the stored rows."""
    findings = sorted(list(master["findings"]) + [resolved_as_finding(master, item) for item in extra], key=lambda f: prefix_rank(f["id"]))
    return clone_world(master, findings=findings, resolved=[], groups=[], scores=rows)


def vector_choice(label: str, predicate) -> list:
    """Every vector that passes predicate, rotated to start at the label's hash, so that two labels rarely share a first pick."""
    matches = [v for v in every_vector() if predicate(v)]
    if not matches:
        raise ValueError("no vector passes the predicate for %s" % label)
    start = label_below(label, len(matches))
    return matches[start:] + matches[:start]


# --- roles: each takes a natural row and returns the row as a baseline stored it ---------------------------------------
def role_clean(row: dict, label: str) -> dict:
    return dict(row)


def role_wrong_composite(row: dict, label: str) -> dict:
    """The stored composite is off by 0.2 to 0.5 and stays in the right band, so only the arithmetic is wrong."""
    deltas = (3, -3, 4, -4, 5, -5, 2, -2)
    start = label_below(label, len(deltas))
    for i in range(len(deltas)):
        wrong = row["composite"] + deltas[(start + i) % len(deltas)]
        if 0 <= wrong <= 100 and wrong not in (40, 70, 90) and band_of(wrong) == band_of(row["composite"]):
            return dict(row, composite=wrong)
    raise ValueError("no in-band wrong composite for %s" % row["id"])


def role_wrong_band(row: dict, label: str) -> dict:
    """The composite is right and the band is the neighbour below or above it; the SLA, disposition and review date follow the wrong
    band, so none of them is an override."""
    index = BAND_ORDER.index(row["band"])
    options = [BAND_ORDER[j] for j in (index - 1, index + 1) if 0 <= j < len(BAND_ORDER)]
    return set_band(dict(row), options[label_below(label, len(options))])


def role_bad_vector(row: dict, label: str, cascade: str = "") -> dict:
    """The stored CVSS cell is far from what its vector gives and is no documented clamp: D10's step 6.
    cascade '' keeps the composite as the right score gives it (one flag); 'composite' computes it from the wrong cell with the band held;
    'band' computes it from the wrong cell and moves the band."""
    category = PREFIX_CATEGORY[row["prefix"]]
    deltas = (17, -19, 23, -21, 15, -16, 28, -24, 13, -13, 31, -29)
    start = label_below(label, len(deltas))
    for i in range(len(deltas)):
        wrong = row["cvss"] + deltas[(start + i) % len(deltas)]
        if not 0 <= wrong <= 100:
            continue
        _, _, step = legacy_check(wrong, row["vector"], category, ())
        if step != 6:
            continue
        out = dict(row, cvss=wrong)
        if cascade:
            out["composite"] = composite_tenths(wrong, row["expl"], row["scale"], row["reach"])
            if awkward(out) or out["composite"] == row["composite"]:
                continue
            if (band_of(out["composite"]) == row["band"]) != (cascade == "composite"):
                continue
            set_band(out, band_of(out["composite"]))
        return out
    raise ValueError("no step-6 vector error for %s (%s)" % (row["id"], cascade))


def role_reach_out_of_range(row: dict, label: str) -> dict:
    """The stored reachability is outside its trust level's range; the composite follows it, so only the range is wrong."""
    level = ZONE_LEVEL[row["zone"]]
    options = {"Trusted": (70, 75, 80, 65), "Semi-trusted": (15, 20, 25, 90), "Untrusted": (30, 35, 25, 20)}[level]
    start = label_below(label, len(options))
    for i in range(len(options)):
        out = settle(dict(row, reach=options[(start + i) % len(options)]))
        if not awkward(out):
            return out
    raise ValueError("no out-of-range reachability for %s" % row["id"])


def role_missing_vector(row: dict, label: str) -> dict:
    return dict(row, vector=None, md_vector=None, sarif_vector=None)


def role_clamp_control(row: dict, label: str) -> dict:
    """A vector whose score is outside the finding's own category bound, stored as that bound: a documented clamp, never flagged."""
    category = PREFIX_CATEGORY[row["prefix"]]
    bounds = category_bounds(category)
    for v in vector_choice("%s/vector" % label, lambda vec: cvss_of(vec) != clamp(cvss_of(vec), bounds)):
        out = settle(dict(row, vector=v, md_vector=v, sarif_vector=v, cvss=clamp(cvss_of(v), bounds)))
        if not awkward(out):
            return out
    raise ValueError("no clamp control for %s" % row["id"])


def n17_values(vector: str, category: str) -> list:
    """The scores that another category's bound would clamp this vector to, and that neither the vector nor its own bound gives."""
    base = cvss_of(vector)
    own = clamp(base, category_bounds(category))
    return sorted({clamp(base, category_bounds(other)) for other in sorted(_CATEGORY_DEFAULT_TENTHS) if other != category} - {base, own})


def role_n17_bound(row: dict, label: str) -> dict:
    """The stored score is another category's bound clamp of the vector: a possible cross-category peer, so unchecked (D10 step 5)."""
    category = PREFIX_CATEGORY[row["prefix"]]
    for v in vector_choice("%s/vector" % label, lambda vec: bool(n17_values(vec, category))):
        values = n17_values(v, category)
        out = settle(dict(row, vector=v, md_vector=v, sarif_vector=v, cvss=values[label_below(label + "/value", len(values))]))
        if not awkward(out):
            return out
    raise ValueError("no N17 bound case for %s" % row["id"])


def tie_candidates(row: dict, moves_band: bool, top: int = 36) -> list:
    """Rows whose composite is an exact x.x5 tie, with the stored value the lower neighbour. moves_band picks ties on a band boundary
    (6.95, 8.95 or 3.95 give 7.0, 9.0 or 4.0), otherwise a tie in the middle of a band."""
    level = ZONE_LEVEL[row["zone"]]
    lo, hi = REACH_RANGE[level]
    found = []
    for reach in range(lo, hi + 1, 5):
        for e_total in range(12, top + 1):
            for s_total in range(12, top + 1):
                expl, scale = MEAN_OF[e_total], MEAN_OF[s_total]
                total = 35 * row["cvss"] + 30 * expl + 15 * scale + 20 * reach
                if total % 100 != 50:
                    continue
                exact = half_up(total, 100)
                if (exact in (40, 70, 90)) != moves_band:
                    continue
                if not moves_band and band_of(exact - 1) != band_of(exact):
                    continue
                found.append((reach, e_total, s_total, exact))
    return found


def role_rounding_tie(row: dict, label: str, moves_band: bool) -> dict:
    """The exact composite ends in .x5 and the baseline stored the lower neighbour. In mid-band the band holds and the difference is
    normalized; on a boundary the lower neighbour is in the lower band, and the difference is a band correction by rounding (R-11)."""
    found = tie_candidates(row, moves_band)
    if not found:
        raise ValueError("no tie for %s" % row["id"])
    reach, e_total, s_total, exact = found[label_below(label, len(found))]
    out = dict(row, reach=reach, expl_sub=sub_scores(e_total), expl=mean_tenths(sub_scores(e_total)),
               scale_sub=sub_scores(s_total), scale=mean_tenths(sub_scores(s_total)), composite=exact - 1)
    return set_band(out, band_of(exact - 1))


def role_override_sla(row: dict, label: str) -> dict:
    """A human tightened the SLA: the review date was counted from it, and the renderer must carry both and flag the override."""
    out = dict(row, sla="14d", sla_days=14, review=add_days(SCORED_ON, 14), owner="platform-team")
    return out


def role_override_disposition(row: dict, label: str) -> dict:
    return dict(row, disposition="Accept", owner="risk-office")


# --- the files of a scenario ----------------------------------------------------------------------------------------------
def baseline_threats_stub(world: dict) -> str:
    """The baseline run's threats.md, cut to what the baseline resolver and a reference-set reader use: the trust zones, Section 4c,
    Section 7 and the Affected Assets block. The scorer reads nothing else from it (ADR-050 D9, R-6)."""
    cfg = world["cfg"]
    dates, runs = cfg["dates"], cfg["run_ids"]
    ranked = sorted(world["findings"], key=lambda f: (-RISK_RANK[f["risk"]], TABLE_ORDER.index(f["prefix"]), f["num"]))
    rows = [(f["id"], f["status"], CATEGORY_TITLE[f["prefix"]], EM if f["pattern"] == "none" else f["pattern"], f["comp"],
             layer_label(f["layer"]), f["short"], f["risk"], f["mit_short"]) for f in ranked]
    zones = [(z["name"], z.get("label", z["level"]), ", ".join(z["members"])) for z in world["zones"]]
    out = ["---", 'schema_version: "1.4"', 'date: "%s"' % dates["baseline"], 'input_format: "free-text"', 'classification: "confidential"',
           'run_id: "%s"' % runs["baseline"], "baseline:", "  source: null", "  date: null", "  finding_count: null", "  run_id: null",
           "coverage_gate:", '  status: "pass"', "  gaps: []", "---", "", "# Threat Model Report", "",
           "This file is the baseline run's threats.md, cut down to the sections that a baseline reader uses.", "",
           "## 2. Trust Boundaries", "", "### Trust Zones", "", table(("Zone", "Trust Level", "Components"), zones), "", "---", "",
           "## 4c. Resolved Findings", "", table(("ID", "Component", "Threat", "Last Risk Level", "Resolution Reason"), []), "", "---", "",
           "## 7. Recommended Actions", "",
           table(("Finding ID", "Status", "Category", "Pattern", "Component", "MAESTRO Layer", "Threat", "Risk Level", "Mitigation"), rows),
           "", "---", "", "## Affected Assets", "", table(("Finding ID", "Affected Assets"), [(f["id"], _assets_cell(world, f)) for f in ranked])]
    return "\n".join(out)


def tally(findings: dict) -> dict:
    """The counts a stage record would hold for this scenario, by flag kind. An optional flag never counts."""
    by_kind, flagged = {}, set()
    for fid, record in findings.items():
        for flag in record["flags"]:
            if flag["basis"] == "optional":
                continue
            by_kind[flag["kind"]] = by_kind.get(flag["kind"], 0) + 1
            flagged.add(fid)
    return {"flags_by_kind": by_kind, "findings_with_flags": len(flagged), "findings": len(findings),
            "normalized": sum(1 for record in findings.values() if record["normalized"])}


def finding_record(row: dict, case: str, ctx: dict, treatment: str = "carried") -> dict:
    """One finding's expected outcome: its stored values, what the renderer writes, and every flag, from the carried-row oracle."""
    result = carried_expectation(row, ctx)
    record = {"case": case, "treatment": treatment, "prefix": row["prefix"], "component": row["comp"], "form": row["form"],
              "stored": stored_values(row), "rendered": result["rendered"], "flags": result["flags"], "normalized": result["normalized"],
              "d10_step": result["step"], "vector_sources": {"markdown": row.get("md_vector"), "sarif": row.get("sarif_vector")}}
    if row["form"] == "renderer":
        record["stored_inputs"] = {"tags_used": list(row["tags_used"]), "scored_on": row["scored_on"],
                                   "score_bounds": None if row.get("bounds") is None else [fmt1(row["bounds"][0]), fmt1(row["bounds"][1])]}
    return record


def unflagged_ids(findings: dict) -> list:
    """The findings that the renderer must leave exactly as stored: no flag, nothing normalized, nothing recomputed."""
    return sorted((fid for fid, r in findings.items() if not r["flags"] and not r["normalized"] and r["rendered"] == r["stored"]), key=prefix_rank)


def expected_document(variant: str, scenario: str, summary: str, run: dict, baseline: dict, tag_source: dict, findings: dict,
                      routing: dict = None, extra: dict = None, notes: Sequence = ()) -> str:
    ordered = {fid: findings[fid] for fid in sorted(findings, key=prefix_rank)}
    doc = {"schema": "tachi.fixture-expected/1", "variant": variant, "scenario": scenario, "stage": "risk-score", "summary": summary,
           "run": run, "baseline": baseline, "tag_source": tag_source,
           "routing": routing if routing is not None else {
               "to_agent": [], "carried": [fid for fid in ordered if ordered[fid]["treatment"] == "carried"],
               "copy_primary": {}, "carried_peers": {}},
           "findings": ordered, "unflagged": unflagged_ids(ordered), "counts": tally(ordered), "notes": list(notes),
           "flag_reading": list(FLAG_READING),
           # True for every scenario whose threats.md carries the block that the shipped populator writes for its architecture
           "populator_fixed_point": run["architecture"] is not None}
    if extra:
        doc.update(extra)
    return dumps(doc)


def standard_run(has_architecture: bool = True, threats: str = "run/threats.md") -> dict:
    return {"date": RUN_DATE, "threats": threats, "architecture": "architecture/architecture.md" if has_architecture else None,
            "baseline_dir": "baseline", "baseline_source": "baseline/threats.md",
            "how": "copy the scenario directory to a working directory and run from there: the front matter's baseline.source and "
                   "every path here are relative to it"}


def legacy_baseline(files: Sequence, date=SCORED_ON, form: str = "legacy", note: str = "") -> dict:
    return {"form": form, "files": list(files), "frontmatter_date": date, "note": note}


# --- the seeded-error scenario (S-4, SC-4) ---------------------------------------------------------------------------------
SEEDED_COUNTS = {"S": 9, "T": 9, "R": 9, "I": 9, "D": 9, "E": 9, "AG": 9, "AGP": 7, "LLM": 9, "OI": 9, "MI": 9, "TE": 9}
SEEDED_RESOLVED = (
    ("S", "edge-gateway", "Component 'legacy-batch-1' removed from architecture", "High"),
    ("T", "vector-store-a", "Component 'report-export-2' removed from architecture", "Medium"),
)
# The roles every prefix gets, in this order, dealt to its findings by a label hash. Some prefixes swap a clean slot for a control.
SEEDED_ROLES = ("wrong-composite", "wrong-band", "bad-vector", "reach-out-of-range", "missing-vector", "clamp-control", "n17-bound",
                "clean", "clean")
SEEDED_SWAPS = {"S": "rounding-only", "T": "rounding-only", "I": "rounding-only", "R": "override-sla", "D": "override-disposition",
                "E": "cascade-composite", "AG": "cascade-band"}


def _seeded_explicit() -> list:
    names = tuple(name for name in GATED_COMPONENTS)
    explicit = []
    for prefix in PREFIX_ORDER:
        explicit += spread(prefix, SEEDED_COUNTS[prefix], names)
    explicit += [("S", "partner-sandbox", None), ("R", "partner-sandbox", None)]
    return explicit


PROFILES["seeded"] = variant_profile(_seeded_explicit(), GATED_COMPONENTS + ("partner-sandbox",), SEEDED_RESOLVED)


def apply_role(role: str, row: dict, label: str) -> dict:
    if role in ("clean", "clean-a", "clean-b"):
        return role_clean(row, label)
    if role == "wrong-composite":
        return role_wrong_composite(row, label)
    if role == "wrong-band":
        return role_wrong_band(row, label)
    if role == "bad-vector":
        return role_bad_vector(row, label)
    if role == "cascade-composite":
        return role_bad_vector(row, label, "composite")
    if role == "cascade-band":
        return role_bad_vector(row, label, "band")
    if role == "reach-out-of-range":
        return role_reach_out_of_range(row, label)
    if role == "missing-vector":
        return role_missing_vector(row, label)
    if role == "clamp-control":
        return role_clamp_control(row, label)
    if role == "n17-bound":
        return role_n17_bound(row, label)
    if role == "rounding-only":
        return role_rounding_tie(row, label, False)
    if role == "override-sla":
        return role_override_sla(row, label)
    if role == "override-disposition":
        return role_override_disposition(row, label)
    raise ValueError("unknown role %r" % role)


def seeded_error_files() -> dict:
    master = build_world("seeded")
    natural = make_rows(master)
    stored, roles = {}, {}
    for prefix in PREFIX_ORDER:
        pool = [f["id"] for f in master["findings"] if f["prefix"] == prefix and f["comp"] != "partner-sandbox"]
        pool.sort(key=lambda fid: label_hash("seeded-role:" + fid))
        plan = list(SEEDED_ROLES[:len(pool)])
        if prefix == "AGP":
            plan = list(SEEDED_ROLES[:7])
        if prefix in SEEDED_SWAPS:
            plan[plan.index("clean")] = SEEDED_SWAPS[prefix]
        if len(plan) != len(pool):
            raise ValueError("prefix %s: %d findings for %d roles" % (prefix, len(pool), len(plan)))
        for fid, role in zip(pool, plan):
            roles[fid] = role
            stored[fid] = apply_role(role, natural[fid], "seeded:" + fid)
    for f in master["findings"]:
        if f["comp"] == "partner-sandbox":
            roles[f["id"]] = "compound-label"
            stored[f["id"]] = dict(natural[f["id"]])
    # R-30: two findings the baseline scored and this run no longer has. Their rows carry a wrong composite on purpose.
    resolved_rows = {}
    rng = Rng("seeded/resolved")
    for item in master["resolved"]:
        row = dict(score_one(master, item, rng))
        row.update({"id": item["id"], "prefix": item["prefix"], "comp": item["comp"], "zone": master["by_name"][item["comp"]]["zone"],
                    "form": "legacy", "md_vector": row["vector"], "sarif_vector": row["vector"], "owner": "Unassigned", "source": "fresh"})
        row["review"] = add_days(SCORED_ON, row["sla_days"])
        resolved_rows[item["id"]] = role_wrong_composite(row, "seeded:" + item["id"])
    all_rows = dict(stored)
    all_rows.update(resolved_rows)
    for row in all_rows.values():
        row["sarif_vector"] = None  # this baseline has no SARIF, so a vector has one source only

    ctx = {"tags": (), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ("Partner Exchange",)}
    findings = {}
    for fid, row in stored.items():
        findings[fid] = finding_record(row, roles[fid], ctx)
    for fid, row in resolved_rows.items():
        values = stored_values(row)
        findings[fid] = {"case": "resolved-wrong-composite", "treatment": "resolved", "prefix": row["prefix"], "component": row["comp"],
                         "form": "legacy", "stored": values, "rendered": dict(values), "normalized": False, "d10_step": None,
                         "vector_sources": {"markdown": row["md_vector"], "sarif": None},
                         "flags": [make_flag("resolved", None, None)]}

    run_world = clone_world(master, zones=[dict(z, label=COMPOUND_LABEL) if z["name"] == "Partner Exchange" else z for z in master["zones"]])
    base = baseline_world(master, all_rows, master["resolved"])
    base["zones"] = run_world["zones"]
    root = "seeded-error/main/"
    files = {
        root + "run/threats.md": render_threats_md(run_world),
        root + "architecture/architecture.md": architecture_text(master),
        root + "baseline/risk-scores.md": render_risk_scores_md(base),
        root + "baseline/threats.md": baseline_threats_stub(base),
    }
    summary = ("S-4's seeded-error variant. A baseline written by the pre-fix scorer holds, for each of the 12 prefixes, a wrong composite, a "
               "wrong band, a CVSS score that its vector does not give, an out-of-range reachability under an unambiguous label and a "
               "missing vector, plus the documented exceptions as controls and the N17 cases. Every finding is UNCHANGED, so every one is "
               "carried and recomputed.")
    notes = [
        "Every finding of run/threats.md is UNCHANGED and has a row in the baseline: the renderer carries all of them. Nothing is routed to the agent.",
        "baseline/threats.md is the baseline run's file cut to Sections 2, 4c and 7 and the Affected Assets block. R-6's resolver needs it to exist; "
        "the scorer reads only baseline/risk-scores.md.",
        "The baseline has no risk-scores.sarif, so a missing vector has no second source and stays missing.",
        "Case 'bad-vector' stores a CVSS cell that its vector does not give, with the composite the right cell gives: one flag, no cascade. "
        "Cases 'cascade-composite' and 'cascade-band' store the composite that the wrong cell gives, so the correction moves the composite, "
        "and for 'cascade-band' the band: the composite and band flags are the ones that flag_reading's causes name.",
        "Case 'rounding-only' stores the lower neighbour of an exact x.x5 composite, in the middle of a band: the difference is normalized and "
        "counted, never flagged (R-11).",
        "Case 'resolved-wrong-composite': these two baseline rows belong to findings that Section 4c of the run lists as RESOLVED. R-30 "
        "keeps their last-known values verbatim, so the wrong composite is neither recomputed nor flagged; the row is marked resolved.",
        "Case 'compound-label': Section 2 labels the zone 'Semi-trusted / Trusted', so the reachability range check is N17-dependent and "
        "is reported as unchecked, never as a violation (R-10).",
        "Overrides: 'override-sla' and 'override-disposition' carry a human owner and a value that differs from the stored band's default; they are "
        "carried verbatim and flagged, and the review date is kept.",
    ]
    files[root + "expected-outcomes.json"] = expected_document(
        "seeded-error", "main", summary, standard_run(), legacy_baseline(("threats.md", "risk-scores.md"), note="pre-fix form (v4.48.4), no SARIF"),
        {"source": "block", "block_equals_recomputation": True, "tags": {}, "warning": False}, findings, notes=notes)
    return files



# --- the legacy-format variant (R-26) --------------------------------------------------------------------------------------
def render_compact_scores_md(world: dict, scores: dict, style: dict) -> str:
    """A risk-scores.md in the compact form that older runs wrote (R-26): no sub-score tables, a vector on only some rows, and the
    heading and header spellings that the tolerant reader accepts. style: numbered (## 2. or ## Section 2:), dash (### ID - comp
    or ### ID: comp), long_headers (Exploitability or Exploit), date (a front-matter date or none)."""
    cfg, findings = world["cfg"], world["findings"]
    order = sorted(findings, key=lambda f: (-scores[f["id"]]["composite"], prefix_rank(f["id"])))
    bands = ("Critical", "High", "Medium", "Low")
    counts = [sum(1 for f in findings if scores[f["id"]]["band"] == band) for band in bands]

    def heading(number: int, title: str) -> str:
        return ("## %d. %s" % (number, title)) if style["numbered"] else ("## Section %d: %s" % (number, title))

    def dash(value) -> str:
        return EM if value is None else value

    head = ["Exploitability", "Scalability", "Reachability"] if style["long_headers"] else ["Exploit", "Scale", "Reach"]
    out = ["---", 'schema_version: "1.0"']
    if style["date"]:
        out.append('date: "%s"' % cfg["dates"]["scores"])
    out += ['source_file: "baseline/threats.md"', 'classification: "confidential"', "scoring_weights:", "  cvss_base: 0.35",
            "  exploitability: 0.30", "  scalability: 0.15", "  reachability: 0.20", "---", "", "# Risk Scores Report", "",
            heading(1, "Executive Summary"), "",
            "**%d** threats scored | **%d** Critical | **%d** High | **%d** Medium | **%d** Low" % ((len(findings),) + tuple(counts)), "",
            heading(2, "Scored Threat Table"), "",
            table(("ID", "Component", "Threat", "CVSS", head[0], head[1], head[2], "Composite", "Severity", "SLA", "Disposition"),
                  [(f["id"], f["comp"], clip(f["short"], 64), fmt1(scores[f["id"]]["cvss"]), fmt1(scores[f["id"]]["expl"]),
                    fmt1(scores[f["id"]]["scale"]), fmt1(scores[f["id"]]["reach"]), fmt1(scores[f["id"]]["composite"]),
                    scores[f["id"]]["band"], dash(scores[f["id"]]["sla"]), scores[f["id"]]["disposition"]) for f in order]),
            "", heading(3, "Dimensional Breakdown"), ""]
    for f in order:
        s = scores[f["id"]]
        out += [("### %s %s %s" % (f["id"], EM, f["comp"])) if style["dash"] else ("### %s: %s" % (f["id"], f["comp"])), "",
                "**Threat**: %s" % first_sentence(f["threat"]), ""]
        if s.get("md_vector") is not None:
            if s.get("md_form", "A") == "A":
                out += ["**CVSS Vector**: `%s`" % s["md_vector"], ""]
            else:
                out += ["**Score**: %s | **Vector**: `%s`" % (fmt1(s["cvss"]), s["md_vector"]), ""]
    out += [heading(4, "Governance Fields"), "",
            table(("ID", "Severity", "Owner", "SLA", "Disposition" if style["long_headers"] else "Disp", "Review Date"),
                  [(f["id"], scores[f["id"]]["band"], scores[f["id"]].get("owner", "Unassigned"), dash(scores[f["id"]]["sla"]),
                    scores[f["id"]]["disposition"], dash(scores[f["id"]]["review"])) for f in order])]
    return "\n".join(out)


# One finding per prefix on each side of the table: the first takes a seeded error, the second a format case or a control.
LEGACY_FIRST = {prefix: ("wrong-composite" if index % 2 == 0 else "bad-vector-sarif-only") for index, prefix in enumerate(PREFIX_ORDER)}
LEGACY_SECOND = {"S": "disagree", "T": "disagree-md-wins", "R": "neither", "I": "sarif-only", "D": "rung-review-missing",
                 "E": "rung-sla-missing", "AG": "md-and-sarif", "AGP": "md-only", "LLM": "md-and-sarif", "OI": "md-and-sarif",
                 "MI": "md-and-sarif", "TE": "md-and-sarif"}


def _legacy_explicit() -> list:
    explicit = []
    for prefix in PREFIX_ORDER:
        explicit += spread(prefix, 2, GATED_COMPONENTS)
    return explicit


PROFILES["legacy"] = variant_profile(_legacy_explicit(), GATED_COMPONENTS)


def other_vector(vector: str, label: str, spread_tenths: int = 12) -> str:
    """A vector whose score is at least spread_tenths away from this one's and that a step-6 correction would catch."""
    base = cvss_of(vector)
    for v in vector_choice(label, lambda vec: abs(cvss_of(vec) - base) >= spread_tenths):
        return v
    raise ValueError("no vector for %s" % label)


def apply_legacy_role(role: str, row: dict, label: str) -> dict:
    row = dict(row)
    if role == "wrong-composite":
        return role_wrong_composite(row, label)
    if role == "bad-vector-sarif-only":  # the vector is only in the SARIF, so the correction proves that the SARIF is read
        out = role_bad_vector(row, label)
        out["md_vector"] = None
        return out
    if role == "disagree":  # the markdown's vector is the one the stored score follows; the SARIF's differs
        row["sarif_vector"] = other_vector(row["vector"], label + "/sarif")
        return row
    if role == "disagree-md-wins":  # the stored score follows the SARIF's vector, but the markdown's is the one that counts
        category = PREFIX_CATEGORY[row["prefix"]]
        for v in vector_choice(label + "/sarif", lambda vec: abs(cvss_of(vec) - row["cvss"]) >= 12):
            if legacy_check(cvss_of(v), row["vector"], category, ())[2] == 6:
                return dict(row, sarif_vector=v, cvss=cvss_of(v))
        raise ValueError("no disagreement for %s" % row["id"])
    if role == "neither":
        return role_missing_vector(row, label)
    if role == "sarif-only":
        return dict(row, md_vector=None)
    if role == "md-only":
        return dict(row, sarif_vector=None)
    if role == "md-and-sarif":
        return row
    if role in ("rung-review-missing", "rung-sla-missing", "rung-no-date-sla", "rung-no-date-both"):
        out = role_wrong_band(row, label)
        if role == "rung-review-missing":
            out["review"] = None
        else:
            out["sla"] = None
            if role == "rung-no-date-both":
                out["review"] = None
        return out
    raise ValueError("unknown legacy role %r" % role)


def legacy_worlds(profile: str):
    master = build_world(profile)
    return master, make_rows(master)


def legacy_scenario(variant_dir: str, scenario: str, master: dict, rows: dict, roles: dict, style: dict, ctx_date, summary: str,
                    notes: Sequence) -> dict:
    ctx = {"tags": (), "run_date": RUN_DATE, "baseline_date": ctx_date, "compound_zones": ()}
    findings = {fid: finding_record(rows[fid], roles[fid], ctx) for fid in rows}
    base = baseline_world(master, rows)
    root = "%s/%s/" % (variant_dir, scenario)
    files = {
        root + "run/threats.md": render_threats_md(master),
        root + "architecture/architecture.md": architecture_text(master),
        root + "baseline/risk-scores.md": render_compact_scores_md(base, rows, style),
        root + "baseline/risk-scores.sarif": render_risk_scores_sarif(base),
        root + "baseline/threats.md": baseline_threats_stub(base),
    }
    form = {"date": ctx_date, "style": "%s headings, %s subsections, %s headers" % (
        "numbered" if style["numbered"] else "Section N", "dash" if style["dash"] else "colon", "long" if style["long_headers"] else "short")}
    files[root + "expected-outcomes.json"] = expected_document(
        variant_dir, scenario, summary, standard_run(),
        legacy_baseline(("threats.md", "risk-scores.md", "risk-scores.sarif"), date=ctx_date, form="legacy-compact",
                        note="compact pre-fix form: %s; no sub-score tables; the SARIF holds a vector for the rows that the markdown lacks" % form["style"]),
        {"source": "block", "block_equals_recomputation": True, "tags": {}, "warning": False}, findings, notes=notes)
    return files


def legacy_format_files() -> dict:
    master, natural = legacy_worlds("legacy")
    rows, roles = {}, {}
    for prefix in PREFIX_ORDER:
        pool = sorted((f["id"] for f in master["findings"] if f["prefix"] == prefix), key=prefix_rank)
        if len(pool) != 2:
            raise ValueError("prefix %s should have two findings in the legacy world" % prefix)
        for fid, role in zip(pool, (LEGACY_FIRST[prefix], LEGACY_SECOND[prefix])):
            roles[fid] = role
            rows[fid] = apply_legacy_role(role, natural[fid], "legacy:" + fid)
    notes = [
        "The baseline is in the compact form (R-26): Section N headings, long header spellings, '### ID - component' subsections, no sub-score "
        "tables, and a vector on only some rows. The exploitability, scalability and reachability values are the inputs, kept as stored.",
        "A row's vector comes from the markdown ('**CVSS Vector**:' or after '**Vector**:'), or else from the SARIF's cvss-vector property "
        "keyed by findingId/v1. Case 'bad-vector-sarif-only' has no markdown vector, so its correction shows that the SARIF is read.",
        "Case 'disagree': the markdown and the SARIF name different vectors and the stored score follows the markdown's. The markdown's is "
        "used and the disagreement is flagged, input:cvss_vector:sources-disagree.",
        "Case 'disagree-md-wins': the stored score follows the SARIF's vector, but the markdown's vector is the one that counts, so the score "
        "is corrected to the markdown's vector's score as well as the disagreement being flagged.",
        "Case 'neither': no vector anywhere (the SARIF result has no cvss-vector property): unverifiable, the score is kept (R-7).",
        "Cases 'rung-review-missing' and 'rung-sla-missing' are wrong bands whose original scoring date cannot be derived (the stored review "
        "date, or the stored SLA, is missing). The baseline's front-matter date stands in for it: corrected:review_date:baseline-date.",
        "baseline/threats.md is the baseline run's file cut to Sections 2, 4c and 7 and the Affected Assets block.",
    ]
    return legacy_scenario("legacy-format", "main", master, rows, roles,
                           {"numbered": False, "dash": True, "long_headers": True, "date": True}, SCORED_ON,
                           "S-4's legacy-format variant (R-26): a compact baseline with no sub-score tables, vectors on only some markdown rows, "
                           "full vectors in the SARIF, one markdown-versus-SARIF disagreement and seeded composite and vector errors.", notes)


def _legacy_date_explicit() -> list:
    return [("S", "edge-gateway", None), ("T", "intake-agent", None), ("R", "edge-gateway", None), ("I", "vector-store-a", None)]


PROFILES["legacy-date"] = variant_profile(_legacy_date_explicit(), GATED_COMPONENTS)


def legacy_no_date_files() -> dict:
    master, natural = legacy_worlds("legacy-date")
    plan = {"S-1": "rung-no-date-sla", "T-1": "rung-no-date-both", "R-1": "wrong-composite", "I-1": "md-and-sarif"}
    rows = {fid: apply_legacy_role(role, natural[fid], "legacy-date:" + fid) for fid, role in plan.items()}
    notes = [
        "The baseline's front matter has no date, so D9's first fallback is unavailable. S-1 has its SLA missing and its review date present: "
        "the stored review date is kept, flagged unchecked:review_date:scoring-date-unknown.",
        "T-1 has both missing: the review date is this run's date plus the new SLA, flagged corrected:review_date:clock-restarted. "
        "No step is silent (D9).",
        "A missing SLA is a gap, not an override: the SLA follows the corrected band. The cause for a value that the input's form lacks "
        "is open (S-12(b), named by T032), so the SLA's own flag is optional.",
        "R-1 and I-1 are controls: a wrong composite in the band, and a row with nothing wrong.",
    ]
    return legacy_scenario("legacy-format", "no-baseline-date", master, rows, plan,
                           {"numbered": True, "dash": False, "long_headers": False, "date": False}, None,
                           "The review-date fallback rungs that need a baseline with no front-matter date (ADR-050 D9): the stored review date "
                           "kept, and the clock restarted.", notes)



# --- the tagged variant (R-25, ruling A, S-13) ---------------------------------------------------------------------------
def find_scores(label: str, vector_ok, accept) -> tuple:
    """The first (vector, exploitability total, scalability total) in a label-rotated order for which accept(v, expl, scale) holds."""
    combos = [(e, s) for e in range(12, 37) for s in range(12, 37)]
    for v in vector_choice(label + "/v", vector_ok):
        start = label_below(label + "/" + v, len(combos))
        for k in range(len(combos)):
            e_total, s_total = combos[(start + k) % len(combos)]
            if accept(v, MEAN_OF[e_total], MEAN_OF[s_total]):
                return v, e_total, s_total
    raise ValueError("no scores satisfy %s" % label)


def clean_composite(cvss: int, expl: int, scale: int, reach: int) -> bool:
    return not composite_is_tie(cvss, expl, scale, reach) and not composite_on_boundary(composite_tenths(cvss, expl, scale, reach))


def tag_search(label: str, reach: int, before: Sequence, after: Sequence, band_before=None, band_after=None, same_band: bool = False,
               vector_ok=None, bounds=None, must_change: bool = True) -> tuple:
    """Scores for a row that a change of tags from `before` to `after` moves (or leaves) as asked, with no tie or boundary on either side."""
    def accept(v, expl, scale):
        old, new = chain_tenths(v, before, bounds), chain_tenths(v, after, bounds)
        if must_change and old == new:
            return False
        if not (clean_composite(old, expl, scale, reach) and clean_composite(new, expl, scale, reach)):
            return False
        band_old, band_new = band_of(composite_tenths(old, expl, scale, reach)), band_of(composite_tenths(new, expl, scale, reach))
        if same_band:
            return band_old == band_new
        return band_old == band_before and band_new == band_after
    return find_scores(label, vector_ok or (lambda v: True), accept)


def tagged_row(rid: str, prefix: str, comp: str, zone: str, vector: str, e_total: int, s_total: int, reach: int, form: str,
               cvss: int, scored_on: str = SCORED_ON, **more) -> dict:
    """A baseline row with every field set. cvss is the stored score; the composite, band and governance follow from the cells."""
    row = {"id": rid, "prefix": prefix, "comp": comp, "zone": zone, "form": form, "vector": vector, "md_vector": vector,
           "sarif_vector": None, "cvss": cvss, "expl_sub": sub_scores(e_total), "expl": mean_tenths(sub_scores(e_total)),
           "scale_sub": sub_scores(s_total), "scale": mean_tenths(sub_scores(s_total)), "reach": reach, "owner": "Unassigned",
           "source": "fresh", "md_form": "A", "scored_on": scored_on, "primary": rid}
    row.update(more)
    return settle(row)


def case_ids(world: dict, plan: Sequence) -> dict:
    """Map each plan entry (case, prefix, comp, sub) to the ID the numbering gave it: the nth entry of a (prefix, comp, sub) is its nth finding."""
    seen, out = {}, {}
    for case, prefix, comp, sub in plan:
        key = (prefix, comp, sub)
        n = seen.get(key, 0)
        seen[key] = n + 1
        matches = sorted((f for f in world["findings"] if (f["prefix"], f["comp"], f["sub"]) == key), key=lambda f: f["num"])
        out[case] = matches[n]["id"]
    return out


# T031's template, risk-scores.md schema 1.1, is the authority for the renderer-form file below. Section 5 is static text there, so the
# generator carries it verbatim, and a test compares it with the template.
SCORING_METHOD_11 = """## 5. Scoring Methodology

This section documents the quantitative scoring model used to produce the risk scores in this report. All scores are derived from the threat findings identified during threat modeling and are intended to replace qualitative risk ratings with data-backed, reproducible numeric assessments.

### 5.1 Scoring Dimensions

Each threat finding is assessed across four independent dimensions, each producing a score on a 0.0 to 10.0 scale.

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity of the vulnerability using CVSS 3.1 base metrics: attack vector, attack complexity, privileges required, user interaction, scope, and confidentiality/integrity/availability impact. Each finding includes the full CVSS vector string for auditability. |
| **Exploitability** | 30% | Practical likelihood of exploitation based on known attack techniques, tooling availability, required skill level, and attack complexity. Higher scores indicate threats with well-documented exploit paths and readily available tooling. |
| **Scalability** | 15% | Potential for automated, large-scale exploitation based on scriptability, breadth of target scope, resource requirements for the attacker, and difficulty of detection. Higher scores indicate threats that can be weaponized across many targets with minimal effort. |
| **Reachability** | 20% | Exposure of the targeted component within the system's trust boundary architecture. Derived from trust zone data in the threat model and supplemented by architecture documentation when available. Higher scores indicate components directly exposed to untrusted networks. |

### 5.2 Default Weights and Rationale

The default weight allocation reflects the following priorities:

- **CVSS Base (35%)** receives the highest weight because intrinsic vulnerability severity is the strongest predictor of potential damage. CVSS 3.1 is an industry-standard metric with well-understood interpretation.
- **Exploitability (30%)** is weighted second because a severe vulnerability that is difficult to exploit in practice poses less immediate risk than one with known, tooled attack paths.
- **Reachability (20%)** accounts for architectural context. A critical vulnerability behind multiple trust boundaries and authentication layers presents less operational risk than the same vulnerability on an internet-facing endpoint.
- **Scalability (15%)** receives the lowest weight because while automation potential increases aggregate risk, it is less deterministic than the other dimensions and often correlates with exploitability.

These weights are fixed for this scoring run and are recorded in the report frontmatter for reproducibility.

### 5.3 Composite Score Formula

The composite risk score for each finding is calculated as a weighted sum of the four dimension scores:

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The sum runs over the stored one-decimal values and is rounded half up to one decimal (a composite of 4.55 is 4.6). The composite score is bounded to the 0.0-10.0 range. Because each dimension is independently scored on a 0.0-10.0 scale and the weights sum to 1.0, the composite inherently falls within this range.

### 5.4 Severity Band Mapping

Composite scores are mapped to severity bands that drive default governance actions:

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band (e.g., a composite score of exactly 7.0 maps to High, not Medium). These bands are aligned with the severity classifications defined in `schemas/output.yaml` to maintain backward compatibility with existing tachi threat model output.

### 5.5 Data Sources

Scoring draws on the following inputs:

- **Threat findings**: Parsed from `threats.md` (markdown table format) or `threats.sarif` (SARIF 2.1.0 JSON). All original threat metadata (ID, component, category, description, likelihood, impact) is preserved through the scoring pipeline.
- **Trust zone data**: Extracted from `threats.md` Section 2 (trust zone table) as the primary source for reachability scoring. Components in Untrusted/External zones score 8.0-10.0 reachability; Semi-Trusted/Application zones score 4.0-7.0; Trusted/Internal zones score 1.0-4.0.
- **Architecture documentation**: When `architecture.md` is available, it provides supplementary context such as authentication barriers and network exposure details that refine the baseline reachability score derived from trust zones.
- **Category default vectors**: CVSS 3.1 baseline vectors are defined per STRIDE threat category in `schemas/risk-scoring.yaml`. This includes tachi-specific defaults for AI threat categories (agentic and LLM) that lack standard CVSS mappings. Per-threat analysis may refine these baselines based on the specific threat description.
- **The baseline**: When a baseline `risk-scores.md` is available, a carried finding's inputs (its vector, sub-scores, reachability inputs and human governance fields) come from it, and Section 6 records which baseline was used.

When trust zone data is unavailable (no Section 2 in `threats.md` and no `architecture.md`), a default reachability score of 5.0 is applied with a warning in the output.

### 5.6 Reproducibility

The scorer's assessments (the CVSS vector, the eight sub-scores and the reachability inputs) are produced by an LLM at temperature 0. For the same threat model input, each of them is expected to be reproducible within a **+/- 0.5 tolerance** across runs. This tolerance reflects the inherent variability in LLM-based analysis and is considered acceptable for risk prioritization purposes.

Everything the renderer computes from those assessments is deterministic: the averages, the CVSS base score, the composite, the severity band, the SLA and the review date. The renderer uses exact decimal arithmetic and takes the date as an input, so the same parts and the same date give the same file, byte for byte. The composite formula, weights, and severity band mappings carry no tolerance."""

# The four narrative fields of a scored finding, in the scorer's order. Plain prose with no numeral and no slot, so the text in
# Section 3 and the text in Section 6's Scoring Inputs are the same.
RENDERER_NARRATIVE = (
    ("rationale.cvss", "The vector follows the category default with a network attack path and the stated privileges."),
    ("rationale.exploitability", "The sub-scores reflect documented techniques and common tooling for this kind of weakness."),
    ("rationale.scalability", "The weakness can be scripted and repeated across instances with modest resources."),
    ("rationale.reachability", "The component sits in a trusted zone with no extra barriers recorded."),
)
FLAG_KIND_ORDER = ("corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input")  # Section 2's Flags cell
STAMP_VERSION = "4.48.4"  # a synthetic stamp: the version that wrote the baseline, in the form that tachi_parts reads


def whole_percentages(counts: dict) -> dict:
    """The template's severity percentages: whole numbers that sum to 100 by largest remainder, ties to the band name that sorts first
    (ADR-050 D5), and all zero when there is nothing to count."""
    total = sum(counts.values())
    if total == 0:
        return {band: 0 for band in counts}
    share = {band: 100 * n // total for band, n in counts.items()}
    for band in sorted(counts, key=lambda b: (-(100 * counts[b] % total), b))[:100 - sum(share.values())]:
        share[band] += 1
    return share


def renderer_form_md(world: dict, rows: dict, tag_source: str = "block") -> str:
    """risk-scores.md in schema 1.1 as the renderer writes it, laid out by templates/tachi/output-schemas/risk-scores.md: the templated
    Executive Summary, a Flags column in Section 2, no Section 2a when nothing is resolved, the scorer's rationale prose in Section 3
    beside per-metric cells that read the dash (and each finding's MAESTRO Layer field and weighted table), Section 5 as the template
    has it, and Section 6, Score Integrity, ending in Scoring Inputs, the one table that the next run reads its carried inputs from. The
    template's own explanatory subsections (column and field definitions, override guidance) are documentation, and no shipped output
    carries them."""
    cfg, findings, by_name = world["cfg"], world["findings"], world["by_name"]
    when = cfg["dates"]["scores"]
    order = sorted(findings, key=lambda f: (-rows[f["id"]]["composite"], prefix_rank(f["id"])))
    bands = ("Critical", "High", "Medium", "Low")
    counts = {band: sum(1 for f in findings if rows[f["id"]]["band"] == band) for band in bands}
    share = whole_percentages(counts)
    best = {}
    for f in findings:
        entry = best.setdefault(f["comp"], [0, 0])
        entry[0] += 1
        entry[1] = max(entry[1], rows[f["id"]]["composite"])
    top = sorted(best.items(), key=lambda kv: (-kv[1][1], -kv[1][0], kv[0]))[0]

    def dash(value) -> str:
        return EM if value is None else value

    def flags_cell(row: dict) -> str:
        kinds = [kind for kind in FLAG_KIND_ORDER if kind in row.get("flag_kinds", ())]
        return ", ".join(kinds) if kinds else EM

    out = ["---", 'schema_version: "1.1"', 'date: "%s"' % when, 'source_file: "baseline/threats.md"', 'classification: "confidential"',
           "scoring_weights:", "  cvss_base: 0.35", "  exploitability: 0.30", "  scalability: 0.15", "  reachability: 0.20", "baseline:",
           "  source: null", "  inherited_count: null", "  fresh_count: null", "---", "", "# Risk Scores Report", "",
           "## 1. Executive Summary", "",
           "%d open findings were scored on %s: %d Critical, %d High, %d Medium and %d Low." % ((len(findings), when) + tuple(counts[b] for b in bands)),
           "", "**Highest-Risk Component**: %s %s %d finding(s), max composite %s" % (top[0], EM, top[1][0], fmt1(top[1][1])), "",
           "**Resolved findings** (Section 2a, outside the distribution below): %d" % len(world["resolved"]), "",
           table(("Metric", "Value"), (("Scoring date", when), ("Source file", "`baseline/threats.md`"), ("Schema version", "1.1"))),
           "", "**Severity Distribution:**", "",
           table(("Severity", "Count", "Percentage"),
                 [(b, counts[b], "%d%%" % share[b]) for b in bands] + [("**Total**", "**%d**" % len(findings), "**100%**")]),
           "", "> Trust zone data was available for every component, so no reachability value was defaulted.", "", "---", "",
           "## 2. Scored Threat Table", "",
           "Findings sorted by Composite score descending (highest risk first), and by finding ID within equal scores. Boundary values map to "
           "the higher severity band (e.g., 7.0 = High, 9.0 = Critical).", "",
           table(("ID", "Source", "Component", "Threat", "CVSS", "Exploit.", "Scale.", "Reach.", "Composite", "Severity", "SLA", "Disposition", "Flags"),
                 [(f["id"], rows[f["id"]].get("source", "fresh"), f["comp"], clip(f["short"], 64), fmt1(rows[f["id"]]["cvss"]),
                   fmt1(rows[f["id"]]["expl"]), fmt1(rows[f["id"]]["scale"]), fmt1(rows[f["id"]]["reach"]), fmt1(rows[f["id"]]["composite"]),
                   rows[f["id"]]["band"], dash(rows[f["id"]]["sla"]), rows[f["id"]]["disposition"], flags_cell(rows[f["id"]])) for f in order]),
           "", "> **Correlated findings**: For correlation groups (Section 4a of the source threat model), the primary finding is scored "
           "independently. A NEW or UPDATED peer takes its primary's assessment and is scored with its own asset tags. An UNCHANGED peer keeps "
           "its own score, and is flagged `divergent` when that score differs from its primary's.", "", "---", ""]
    if world["resolved"]:
        raise ValueError("a renderer-form fixture with RESOLVED findings needs Section 2a, which no scenario has yet")
    out += ["## 3. Dimensional Breakdown", "",
            "Per-finding detail showing the full scoring rationale for each dimension. One subsection per open finding, ordered by composite "
            "score descending (matching Section 2 sort order).", ""]
    prose = dict(RENDERER_NARRATIVE)
    for f in order:
        r, comp = rows[f["id"]], by_name[f["comp"]]
        metrics = vector_parts(r["vector"])
        out += ["### %s %s %s" % (f["id"], EM, f["comp"]), "", "**Threat**: %s" % f["threat"], "",
                "**Category**: %s | **MAESTRO Layer**: %s | **Original Risk Level**: %s | **Composite**: %s (%s)" % (
                    PREFIX_CATEGORY[f["prefix"]], layer_label(f["layer"]), f["risk"], fmt1(r["composite"]), r["band"]), ""]
        if r.get("integrity"):
            out += ["**Integrity**: %s" % ", ".join(r["integrity"]), ""]
        out += [table(("Dimension", "Score", "Weight", "Weighted"),
                      [(label, fmt1(r[key]), "0.%02d" % weight, weighted_cell(r[key], weight)) for label, key, weight in WEIGHT_ROWS])
                + "\n| **Composite** | | | **%s** |" % fmt1(r["composite"]), "",
                "#### CVSS 3.1 Base", "", "**Score**: %s | **Vector**: `%s`" % (fmt1(r["cvss"]), r["vector"]), "",
                table(("Metric", "Value", "Rationale"), [(label, names[metrics[key]], EM) for key, label, names, _ in CVSS_METRICS]), "",
                prose["rationale.cvss"], "",
                "#### Exploitability", "", "**Score**: %s (average of sub-dimensions)" % fmt1(r["expl"]), "",
                table(("Sub-Dimension", "Score", "Rationale"), [(name, v, EM) for (name, _), v in zip(EXPLOIT_PARTS, r["expl_sub"])]), "",
                prose["rationale.exploitability"], "",
                "#### Scalability", "", "**Score**: %s (average of sub-dimensions)" % fmt1(r["scale"]), "",
                table(("Sub-Dimension", "Score", "Rationale"), [(name, v, EM) for (name, _), v in zip(SCALE_PARTS, r["scale_sub"])]), "",
                prose["rationale.scalability"], "",
                "#### Reachability", "", "**Score**: %s | **Trust Zone**: %s (%s)" % (fmt1(r["reach"]), comp["zone"], PART_TRUST[ZONE_LEVEL[comp["zone"]]]),
                "", prose["rationale.reachability"], "", "---", ""]
    inputs = []
    for fid in sorted(rows, key=prefix_rank):
        r = rows[fid]
        values = [("cvss_vector", r["vector"])]
        values += list(zip(("exploitability.known_techniques", "exploitability.attack_complexity", "exploitability.tooling_availability",
                            "exploitability.skill_level"), r["expl_sub"]))
        values += list(zip(("scalability.scriptability", "scalability.target_scope", "scalability.resource_requirements",
                            "scalability.detection_difficulty"), r["scale_sub"]))
        values += [("reachability.zone", r["zone"]), ("reachability.trust_level", PART_TRUST[ZONE_LEVEL[r["zone"]]]),
                   ("reachability.auth_barriers", 0), ("reachability.network_boundaries", 0)]
        values += list(RENDERER_NARRATIVE)
        if r.get("bounds") is not None:
            values.append(("score_bounds", "%s,%s" % (fmt1(r["bounds"][0]), fmt1(r["bounds"][1]))))
        values += [("tags", ",".join(sorted(r["tags_used"]))), ("scored_on", r["scored_on"])]
        inputs += [(fid, key, value) for key, value in values]
    digest = hashlib.sha256(b"tachi fixture: tagged/renderer-form baseline, input of the scorer renderer").hexdigest()
    out += ["## 4. Governance Fields", "",
            "Remediation tracking metadata for each scored finding. Default values are severity-driven and intended for manual override by "
            "security managers during risk review.", "",
            table(("ID", "Severity", "Owner", "SLA", "Disposition", "Review Date"),
                  [(f["id"], rows[f["id"]]["band"], rows[f["id"]].get("owner", "Unassigned"), dash(rows[f["id"]]["sla"]),
                    rows[f["id"]]["disposition"], dash(rows[f["id"]]["review"])) for f in order]), "", "---", "",
            SCORING_METHOD_11.rstrip("\n"), "", "---", "", "## 6. Score Integrity", "",
            "What the renderer checked, corrected or could not check, and the inputs it scored from. A first run with no baseline has "
            "nothing to correct, so its Score Flags table is empty.", "",
            "### Integrity Summary", "", table(("Kind", "Cause", "Count"), []), "", "**Normalized (rounding only)**: 0", "",
            "**Baseline source**: none", "", "**Tag source**: %s" % tag_source, "",
            "### Score Flags", "", table(("ID", "Flag", "Field", "Stored", "Rendered", "Cause"), []), "",
            "### Input Issues", "", "None.", "",
            "### Scoring Inputs", "", table(("ID", "Field", "Value"), inputs), "",
            "<!-- tachi-provenance: renderer=render-risk-scores.py; version=%s; input-digest=sha256:%s -->" % (STAMP_VERSION, digest)]
    return "\n".join(out)


def drift_threats_md(world: dict) -> str:
    """threats.md in the drift form that tachi's shipped samples show (S-12(a)): '## Section N: Title' headings, one field table per
    finding, and Section 7 as a numbered list of bolded IDs. It has no Status column and no Section 7 table, so the populator reads no
    finding from it. The Affected Assets block is the empty one that Step 1.5 leaves on such a file."""
    cfg, findings = world["cfg"], world["findings"]
    stride = [("S", "Spoofing (S)"), ("T", "Tampering (T)"), ("R", "Repudiation (R)"), ("I", "Information Disclosure (I)"),
              ("D", "Denial of Service (D)"), ("E", "Elevation of Privilege (E)")]
    out = ["---", 'schema_version: "1.4"', 'date: "%s"' % cfg["dates"]["threats"], 'input_format: "mermaid"', 'classification: "confidential"',
           'run_id: "%s"' % cfg["run_ids"]["threats"], "baseline:", '  source: "%s"' % cfg["baseline_source"],
           '  date: "%s"' % cfg["dates"]["baseline"], "coverage_gate:", '  status: "pass"', "  gaps: []", "---", "",
           "# Threat Model %s %s" % (EM, PLATFORM), "", "## Section 1: Architecture Overview", "",
           "A multi-agent platform that turns operator requests into planned, reviewed and audited shipment actions.", "", "### Components", "",
           table(("Component", "Type", "Description"), [(c["name"], c["dfd"], c["desc"]) for c in world["components"]]), "",
           "### Trust Zones", "",
           table(("Zone", "Trust Level", "Components"), [(z["name"], z.get("label", z["level"]), ", ".join(z["members"])) for z in world["zones"]]),
           "", "---", "", "## Section 2: STRIDE Findings", ""]
    for prefix, title in stride:
        here = [f for f in findings if f["prefix"] == prefix]
        if not here:
            continue
        out += ["### " + title, ""]
        for f in here:
            comp = world["by_name"][f["comp"]]
            out += ["#### %s %s %s" % (f["id"], EM, clip(f["short"], 60)), "", "| Field | Value |", "|---|---|", "| **id** | %s |" % f["id"],
                    "| **category** | stride |", "| **component** | %s |" % f["comp"], "| **dfd_element_type** | %s |" % comp["dfd"],
                    "| **threat** | %s |" % cell(f["threat"]), "| **likelihood** | %s |" % f["like"], "| **impact** | %s |" % f["imp"],
                    "| **risk_level** | %s |" % f["risk"], "| **mitigation** | %s |" % cell(f["mit"]), ""]
    out += ["---", "", "## Section 4a: Correlated Findings", "", "**Cross-agent correlations detected**: NONE in this baseline.", "", "---", "",
            "## Section 6: Carry-Forward / Resolved (Baseline Mode)", "", "**Mode**: BASELINE.", "",
            table(("Lifecycle Status", "Count"), (("`[UNCHANGED]`", len(findings)), ("`[NEW]`", 0), ("`[UPDATED]`", 0), ("`[RESOLVED]`", 0))),
            "", "---", "", "## Section 7: Recommended Actions (Prioritized)", ""]
    number = 1
    for level, heading in (("Critical", "CRITICAL Priority (immediate action)"), ("High", "HIGH Priority (within sprint)"),
                           ("Medium", "MEDIUM Priority (next quarter)"), ("Low", "LOW Priority (backlog)")):
        here = [f for f in findings if f["risk"] == level]
        if not here:
            continue
        out += ["### " + heading, ""]
        for f in here:
            out.append("%d. **%s %s %s**: %s" % (number, f["id"], EM, clip(f["short"], 60), f["mit_short"]))
            number += 1
        out.append("")
    out += ["---", "", "## Affected Assets", "", table(("Finding ID", "Affected Assets"), [])]
    return "\n".join(out)


TAG_COMPONENTS = ("planner-agent", "tool-server-1", "model-gateway", "vector-store-a", "audit-ledger", "edge-gateway")


def tagged_profile(plan: Sequence) -> dict:
    profile = variant_profile([(prefix, comp, sub) for _, prefix, comp, sub in plan], GATED_COMPONENTS)
    profile["mermaid"] = True  # the asset tags live in the Mermaid labels of the architecture description
    return profile


def with_block(text: str, keep: bool = True) -> str:
    """threats.md with its Affected Assets block, or cut off just before it (the run had no block at all)."""
    if keep:
        return text
    cut = text.rfind("\n---\n\n## Affected Assets")
    return text[:cut]


def tag_source_record(source: str, tags: dict, block_present: bool, architecture_present: bool, block_equals, warning: bool,
                      cause: str) -> dict:
    return {"source": source, "tags": {comp: list(values) for comp, values in sorted(tags.items()) if values}, "block_present": block_present,
            "architecture_present": architecture_present, "block_equals_recomputation": block_equals, "warning": warning, "cause": cause}


# --- tagged/renderer-form: ruling A in both directions, and R-25's outcomes, on rows that record their tags ----------------------
TAGW_PLAN = (
    ("up-band-review-later", "T", "vector-store-a", None),
    ("up-band-review-earlier", "T", "vector-store-a", None),
    ("up-band-sla-override", "T", "vector-store-a", None),
    ("band-holds-tag-added", "D", "vector-store-a", None),
    ("down-band", "T", "audit-ledger", None),
    ("band-holds-tag-removed", "D", "audit-ledger", None),
    ("r25-assessed-above-ceiling", "E", "model-gateway", None),
    ("r25-ceiling-binds", "S", "model-gateway", None),
    ("r25-tag-is-no-op", "T", "model-gateway", None),
    ("tag-unchanged-elevated", "D", "tool-server-1", None),
    ("untagged", "T", "planner-agent", None),
    ("clamped-new-finding", "T", "planner-agent", None),
)
TAGW_NOW = {"vector-store-a": ("pii",), "model-gateway": ("secrets",), "tool-server-1": ("safety",)}      # this run's architecture
TAGW_THEN = {"model-gateway": ("secrets",), "audit-ledger": ("financial",), "tool-server-1": ("safety",)}  # what the baseline scored under
PROFILES["tagw"] = tagged_profile(TAGW_PLAN)


def renderer_form_rows(master: dict) -> tuple:
    ids = case_ids(master, TAGW_PLAN)
    rows, cases = {}, {}
    auth = {"S": "spoofing", "T": "tampering", "E": "privilege-escalation", "D": "denial-of-service"}

    def zone_of(comp):
        return master["by_name"][comp]["zone"]

    def build(case, prefix, comp, vector, e_total, s_total, tags_then, scored_on=SCORED_ON, bounds=None, **more):
        zone = zone_of(comp)
        reach = reach_value(zone, ZONE_LEVEL[zone], 0, 0)
        row = tagged_row(ids[case], prefix, comp, zone, vector, e_total, s_total, reach, "renderer", chain_tenths(vector, tags_then, bounds),
                         scored_on, bounds=bounds, tags_used=tuple(sorted(tags_then)), **more)
        rows[row["id"]], cases[row["id"]] = row, case
        return row

    def moving(case, prefix, comp, then, now, band_then, band_now, scored_on=SCORED_ON, **more):
        zone = zone_of(comp)
        reach = reach_value(zone, ZONE_LEVEL[zone], 0, 0)
        v, e, s = tag_search("tagw:" + case, reach, then, now, band_then, band_now)
        return build(case, prefix, comp, v, e, s, then, scored_on, **more)

    moving("up-band-review-later", "T", "vector-store-a", (), TAGW_NOW["vector-store-a"], "Medium", "High")
    moving("up-band-review-earlier", "T", "vector-store-a", (), TAGW_NOW["vector-store-a"], "Medium", "High", scored_on="2026-09-28")
    row = moving("up-band-sla-override", "T", "vector-store-a", (), TAGW_NOW["vector-store-a"], "Medium", "High")
    row.update(sla="14d", sla_days=14, review=add_days(SCORED_ON, 14), owner="platform-team")
    for case, prefix, comp, then, now in (("band-holds-tag-added", "D", "vector-store-a", (), TAGW_NOW["vector-store-a"]),
                                          ("band-holds-tag-removed", "D", "audit-ledger", TAGW_THEN["audit-ledger"], ())):
        zone = zone_of(comp)
        reach = reach_value(zone, ZONE_LEVEL[zone], 0, 0)
        v, e, s = tag_search("tagw:" + case, reach, then, now, same_band=True)
        build(case, prefix, comp, v, e, s, then)
    moving("down-band", "T", "audit-ledger", TAGW_THEN["audit-ledger"], (), "High", "Medium")

    reach_trusted = 25
    secrets = TAGW_NOW["model-gateway"]
    v = CATEGORY_VECTOR["privilege-escalation"]
    e, s = find_scores("tagw:r25-above", lambda vec: vec == v, lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach_trusted))[1:]
    build("r25-assessed-above-ceiling", "E", "model-gateway", v, e, s, secrets)
    v, e, s = find_scores("tagw:r25-binds", lambda vec: cvss_of(vec) < CEILING < cvss_of(elevate_vector(vec, secrets)),
                          lambda vec, ex, sc: clean_composite(CEILING, ex, sc, reach_trusted))
    build("r25-ceiling-binds", "S", "model-gateway", v, e, s, secrets)
    v, e, s = find_scores("tagw:r25-noop", lambda vec: elevate_vector(vec, secrets) == vec and 70 <= cvss_of(vec) < CEILING,
                          lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach_trusted))
    build("r25-tag-is-no-op", "T", "model-gateway", v, e, s, secrets)
    safety = TAGW_NOW["tool-server-1"]
    v, e, s = find_scores("tagw:kept", lambda vec: cvss_of(elevate_vector(vec, safety)) != cvss_of(vec) and cvss_of(elevate_vector(vec, safety)) < CEILING,
                          lambda vec, ex, sc: clean_composite(chain_tenths(vec, safety, None), ex, sc, reach_trusted))
    build("tag-unchanged-elevated", "D", "tool-server-1", v, e, s, safety)
    v, e, s = find_scores("tagw:plain", lambda vec: 50 <= cvss_of(vec) <= 80, lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach_trusted))
    build("untagged", "T", "planner-agent", v, e, s, ())
    bounds = category_bounds("tampering")
    v, e, s = find_scores("tagw:clamp", lambda vec: cvss_of(vec) > bounds[1],
                          lambda vec, ex, sc: clean_composite(bounds[1], ex, sc, reach_trusted))
    build("clamped-new-finding", "T", "planner-agent", v, e, s, (), bounds=bounds)
    return rows, cases


def tagged_renderer_form_files() -> dict:
    master = build_world("tagw")
    rows, cases = renderer_form_rows(master)
    ctx_for = lambda comp: {"tags": TAGW_NOW.get(comp, ()), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ()}  # noqa: E731
    findings = {fid: finding_record(row, cases[fid], ctx_for(row["comp"])) for fid, row in rows.items()}
    run_world = clone_world(master, asset_tags=TAGW_NOW)
    base = clone_world(baseline_world(master, rows), asset_tags=TAGW_THEN)
    root = "tagged/renderer-form/"
    files = {
        root + "run/threats.md": render_threats_md(run_world),
        root + "architecture/architecture.md": architecture_text(run_world),
        root + "baseline/risk-scores.md": renderer_form_md(base, rows),
        root + "baseline/threats.md": baseline_threats_stub(base),
    }
    notes = [
        "The baseline is a renderer-form (schema 1.1) risk-scores.md: it records each row's assessed vector, its score_bounds, the tags it was "
        "scored under and its scored-on date in Section 6's Scoring Inputs (the format frozen in contracts/module-signatures.md). So every "
        "case here is decidable: recomputing with the recorded tags either gives the stored value (a retag) or it does not (a correction).",
        "Ruling A, up: a tag added on vector-store-a (pii) raises the score and the band. The change is retagged, never corrected, for the CVSS "
        "score, the composite, the band and the values that follow the band. The review date becomes this run's date plus the new SLA "
        "unless the stored review date is earlier ('up-band-review-later' and 'up-band-review-earlier'). An SLA override keeps its review "
        "date and its SLA ('up-band-sla-override'); the disposition still follows the band.",
        "Ruling A, down: the financial tag on audit-ledger is gone, so the score and the band fall. The original scoring date is kept, so the "
        "review date is the scored-on date plus the lower band's SLA ('down-band'). A deadline missed under the lower band stays missed.",
        "PM-T7: 'band-holds-tag-added' and 'band-holds-tag-removed' move cvss_base and the composite but not the band: both are flagged "
        "retagged, the band is not flagged, and nothing that follows the band changes.",
        "R-25's documented outcomes are controls, flagged zero times: an assessed score above 9.2 that the tag does not lower, an elevated "
        "score that the 9.2 ceiling holds at 9.2, a tag whose bits the vector already has, a tag that was already in effect when the row was "
        "scored, an untagged finding, and a NEW finding's score held at its category bound (stored as score_bounds).",
        "Reachability is the trusted-zone value (2.5) with no barriers, as the renderer computes it from the recorded zone, trust level and "
        "barrier counts. The Section 6 narrative rows hold plain prose with no numeral and no slot.",
        "The run's threats.md carries the populator's Affected Assets block for this architecture, so it is a fixed point of the populator.",
    ]
    files[root + "expected-outcomes.json"] = expected_document(
        "tagged", "renderer-form", "Ruling A's tag-driven moves in both directions, PM-T7's band-holding move and R-25's documented outcomes, "
        "on a baseline that records its tags.", standard_run(),
        legacy_baseline(("threats.md", "risk-scores.md"), form="renderer", note="schema 1.1, Section 6 Scoring Inputs present"),
        tag_source_record("block", TAGW_NOW, True, True, True, False, "the block equals the recomputation"), findings, notes=notes,
        extra={"tags_this_run": {k: list(v) for k, v in sorted(TAGW_NOW.items())},
               "tags_recorded_by_baseline": {k: list(v) for k, v in sorted(TAGW_THEN.items())}})
    return files


# --- tagged/legacy-form: the first renderer run after an upgrade (ruling A's legacy case) ------------------------------------
TAGL_PLAN = (
    ("up-band-review-later", "T", "vector-store-a", None),
    ("up-band-review-earlier", "T", "vector-store-a", None),
    ("band-holds", "D", "vector-store-a", None),
    ("assessed-unrecorded", "E", "model-gateway", None),
    ("documented-pass", "T", "model-gateway", None),
    ("ceiling-pass", "S", "model-gateway", None),
    ("n17-assessed-unrecorded", "S", "model-gateway", None),
    ("untagged", "T", "planner-agent", None),
)
TAGL_NOW = {"vector-store-a": ("pii",), "model-gateway": ("secrets",)}
PROFILES["tagl"] = tagged_profile(TAGL_PLAN)


def legacy_form_rows(master: dict) -> tuple:
    ids = case_ids(master, TAGL_PLAN)
    rows, cases = {}, {}
    reach = 25

    def build(case, prefix, comp, vector, e_total, s_total, stored_cvss, scored_on=SCORED_ON):
        zone = master["by_name"][comp]["zone"]
        row = tagged_row(ids[case], prefix, comp, zone, vector, e_total, s_total, reach, "legacy", stored_cvss, scored_on)
        rows[row["id"]], cases[row["id"]] = row, case
        return row

    now = TAGL_NOW["vector-store-a"]
    for case, prefix, scored_on in (("up-band-review-later", "T", SCORED_ON), ("up-band-review-earlier", "T", "2026-09-28")):
        v, e, s = tag_search("tagl:" + case, reach, (), now, "Medium", "High")
        build(case, prefix, "vector-store-a", v, e, s, cvss_of(v), scored_on)
    v, e, s = tag_search("tagl:band-holds", reach, (), now, same_band=True)
    build("band-holds", "D", "vector-store-a", v, e, s, cvss_of(v))
    secrets = TAGL_NOW["model-gateway"]
    v = CATEGORY_VECTOR["privilege-escalation"]  # already carries C:H and I:H, so only an elevated score above 9.2 is stored
    e, s = find_scores("tagl:unrecorded", lambda vec: vec == v, lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach))[1:]
    build("assessed-unrecorded", "E", "model-gateway", v, e, s, cvss_of(v))
    v, e, s = find_scores("tagl:pass", lambda vec: elevate_vector(vec, secrets) == vec and 70 <= cvss_of(vec) < CEILING,
                          lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach))
    build("documented-pass", "T", "model-gateway", v, e, s, cvss_of(v))
    v, e, s = find_scores("tagl:ceiling", lambda vec: cvss_of(vec) < CEILING < cvss_of(elevate_vector(vec, secrets)),
                          lambda vec, ex, sc: clean_composite(CEILING, ex, sc, reach))
    build("ceiling-pass", "S", "model-gateway", v, e, s, CEILING)

    def n17_ok(vec):
        base, top = cvss_of(vec), cvss_of(elevate_vector(vec, secrets))
        return base < CEILING < top and top >= 96 and legacy_check(95, vec, "spoofing", secrets)[1] == ("unchecked", "cvss_base", "assessed-unrecorded")
    v, e, s = find_scores("tagl:n17", n17_ok, lambda vec, ex, sc: clean_composite(95, ex, sc, reach))
    build("n17-assessed-unrecorded", "S", "model-gateway", v, e, s, 95)
    v, e, s = find_scores("tagl:plain", lambda vec: 50 <= cvss_of(vec) <= 80, lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach))
    build("untagged", "T", "planner-agent", v, e, s, cvss_of(v))
    return rows, cases


def tagged_legacy_form_files() -> dict:
    master = build_world("tagl")
    rows, cases = legacy_form_rows(master)
    ctx_for = lambda comp: {"tags": TAGL_NOW.get(comp, ()), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ()}  # noqa: E731
    findings = {fid: finding_record(row, cases[fid], ctx_for(row["comp"])) for fid, row in rows.items()}
    run_world = clone_world(master, asset_tags=TAGL_NOW)
    base = clone_world(baseline_world(master, rows), asset_tags={})
    root = "tagged/legacy-form/"
    files = {
        root + "run/threats.md": render_threats_md(run_world),
        root + "architecture/architecture.md": architecture_text(run_world),
        root + "baseline/risk-scores.md": render_risk_scores_md(base),
        root + "baseline/threats.md": baseline_threats_stub(base),
    }
    notes = [
        "The baseline is a pre-fix risk-scores.md: it records no tags, so every tag this run applies is new to it. This is the first renderer "
        "run after an upgrade, and D9 ends the UNCHANGED exemption, so tags apply to carried findings (ruling A's legacy case).",
        "'up-band-review-later' and 'up-band-review-earlier': the stored score lacks the elevation (D10 step 4), so it becomes the elevated "
        "score, retagged. The band rises only because of the tag, so the review date is this run's date plus the new SLA unless the stored "
        "review date is earlier. A legacy row has no recorded tags, and the band the stored values give is the band it holds.",
        "'band-holds': the tag moves the score and the composite but not the band: two retagged flags and nothing else.",
        "'assessed-unrecorded' (D10 step 2): the vector already has the tag's bits and only a score above 9.2 is stored, so the assessed score "
        "is unrecorded. The stored score is kept and reported as unchecked (R-25).",
        "'documented-pass' and 'ceiling-pass': the stored score is the documented outcome (the elevated score, or the 9.2 ceiling when the "
        "elevated score is above it), so nothing is flagged.",
        "'n17-assessed-unrecorded' (D10 step 5): a forcing tag, and a stored score above 9.2 and below the elevated score. Unchecked, kept.",
    ]
    files[root + "expected-outcomes.json"] = expected_document(
        "tagged", "legacy-form", "R-25's legacy outcomes and ruling A's legacy case: a pre-fix baseline that records no tags, scored under "
        "this run's tags.", standard_run(), legacy_baseline(("threats.md", "risk-scores.md"), note="pre-fix form, no tags recorded"),
        tag_source_record("block", TAGL_NOW, True, True, True, False, "the block equals the recomputation"), findings, notes=notes,
        extra={"tags_this_run": {k: list(v) for k, v in sorted(TAGL_NOW.items())}})
    return files


# --- tagged/s13-*: the five branches of one tag source (S-13, PM-T4, AR-T4) ------------------------------------------------
S13_PLAN = (
    ("elevated-by-pii", "T", "vector-store-a", None),
    ("pii-is-no-op", "I", "vector-store-a", None),
    ("elevated-by-secrets", "T", "model-gateway", None),
    ("secrets-is-no-op", "E", "model-gateway", None),
    ("spoofing-on-untagged", "S", "tool-server-1", None),
    ("dos-on-untagged", "D", "tool-server-1", None),
)
S13_ARCH = {"vector-store-a": ("pii",), "model-gateway": ("secrets",)}
S13_STALE_BLOCK = {"model-gateway": ("secrets",), "tool-server-1": ("auth",)}          # vector-store-a's tag is missing, tool-server-1 has a stale one
S13_UNVERIFIED_BLOCK = {"vector-store-a": ("pii",), "model-gateway": ("secrets",), "tool-server-1": ("auth",)}
PROFILES["s13"] = tagged_profile(S13_PLAN)


def s13_rows(master: dict) -> tuple:
    ids = case_ids(master, S13_PLAN)
    rows, cases = {}, {}
    reach = 25

    def build(case, prefix, comp, vector, e_total, s_total):
        zone = master["by_name"][comp]["zone"]
        row = tagged_row(ids[case], prefix, comp, zone, vector, e_total, s_total, reach, "legacy", cvss_of(vector))
        rows[row["id"]], cases[row["id"]] = row, case

    pii, secrets, auth = ("pii",), ("secrets",), ("auth",)
    v, e, s = tag_search("s13:pii", reach, (), pii, "Medium", "High", vector_ok=lambda vec: 60 <= cvss_of(vec) <= 80)
    build("elevated-by-pii", "T", "vector-store-a", v, e, s)
    v, e, s = find_scores("s13:pii-noop", lambda vec: elevate_vector(vec, pii) == vec and 50 <= cvss_of(vec) < CEILING,
                          lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach))
    build("pii-is-no-op", "I", "vector-store-a", v, e, s)
    v, e, s = tag_search("s13:secrets", reach, (), secrets, same_band=True, vector_ok=lambda vec: 50 <= cvss_of(vec) <= 80)
    build("elevated-by-secrets", "T", "model-gateway", v, e, s)
    v, e, s = find_scores("s13:secrets-noop", lambda vec: elevate_vector(vec, secrets) == vec and 70 <= cvss_of(vec) < CEILING,
                          lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach))
    build("secrets-is-no-op", "E", "model-gateway", v, e, s)
    # the two findings on tool-server-1 move under a stale or unverified 'auth' and stay put under the architecture
    for case, prefix, label in (("spoofing-on-untagged", "S", "s13:spoof"), ("dos-on-untagged", "D", "s13:dos")):
        v, e, s = find_scores(
            label, lambda vec: 50 <= cvss_of(vec) <= 85 and cvss_of(elevate_vector(vec, auth)) - cvss_of(vec) >= 10,
            lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach) and clean_composite(cvss_of(elevate_vector(vec, auth)), ex, sc, reach))
        build(case, prefix, "tool-server-1", v, e, s)
    return rows, cases


def s13_scenario(name: str, summary: str, notes: Sequence, arch_tags, block_tags, block_present: bool, architecture_present: bool,
                 used_tags: dict, source: str, warning: bool, cause: str, drift: bool = False, fixed_point=None) -> dict:
    master = build_world("s13")
    rows, cases = s13_rows(master)
    ctx_for = lambda comp: {"tags": used_tags.get(comp, ()), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ()}  # noqa: E731
    findings = {fid: finding_record(row, cases[fid], ctx_for(row["comp"])) for fid, row in rows.items()}
    run_world = clone_world(master, asset_tags=arch_tags or {}, block_tags=block_tags or {})
    base = clone_world(baseline_world(master, rows), asset_tags={}, block_tags={})
    root = "tagged/%s/" % name
    threats = drift_threats_md(run_world) if drift else with_block(render_threats_md(run_world), block_present)
    files = {root + "run/threats.md": threats, root + "baseline/risk-scores.md": render_risk_scores_md(base),
             root + "baseline/threats.md": baseline_threats_stub(base)}
    if architecture_present:
        files[root + "architecture/architecture.md"] = architecture_text(run_world)
    recomputed = {comp: tags for comp, tags in (arch_tags or {}).items() if tags}
    equal = None if not architecture_present else (not drift and block_present and {c: t for c, t in (block_tags or {}).items() if t} == recomputed)
    files[root + "expected-outcomes.json"] = expected_document(
        "tagged", name, summary, standard_run(architecture_present), legacy_baseline(("threats.md", "risk-scores.md"), note="pre-fix form, no tags recorded"),
        tag_source_record(source, used_tags, block_present, architecture_present, equal, warning, cause), findings, notes=notes,
        extra={"architecture_tags": {k: list(v) for k, v in sorted((arch_tags or {}).items())},
               "block_tags": {k: list(v) for k, v in sorted((block_tags or {}).items())} if block_present else None,
               "populator_fixed_point": fixed_point,
               "populator_fixed_point_note": "true: the shipped populator, run on the architecture and this file, leaves it as it is; false: it "
                                              "rewrites the block; null: there is no architecture file to run it with"})
    return files


def tagged_s13_files() -> dict:
    common = [
        "Six carried legacy rows scored before any tags applied, so each tag that the chosen source applies shows as a retag: 'elevated-by-pii' "
        "(the band rises) and 'elevated-by-secrets' (the band holds) move; 'pii-is-no-op' and 'secrets-is-no-op' carry bits their vectors "
        "already have; the two findings on tool-server-1 move only if a source gives that component the auth tag.",
        "The source is chosen once per run and never mixed: a run that scores one component from the block and another from the architecture "
        "has failed this case. The warning is recorded in the stage record, and the run never stops for it (FR-N16.2, S-13).",
    ]
    files = {}
    files.update(s13_scenario(
        "s13-block-equal", "S-13, branch 1: the block equals the recomputation, so the block is the source.", common + [
            "The Affected Assets block lists exactly the tags that the architecture gives, so the populator leaves the file as it is."],
        S13_ARCH, S13_ARCH, True, True, S13_ARCH, "block", False, "the block equals the recomputation", fixed_point=True))
    files.update(s13_scenario(
        "s13-stale-block", "S-13, branch 2: a stale block. The recomputation from the architecture is the source, with a warning.", common + [
            "The block misses vector-store-a's pii tag and gives tool-server-1 an auth tag the architecture does not have. Scoring from the "
            "block would elevate the wrong rows; the expected values follow the architecture's tags alone.",
            "This file is deliberately not a fixed point of the populator: running Step 1.5 would rewrite its block."],
        S13_ARCH, S13_STALE_BLOCK, True, True, S13_ARCH, "recomputed", True, "the block differs from the recomputation", fixed_point=False))
    files.update(s13_scenario(
        "s13-no-architecture", "S-13, branch 3: no architecture file. The block is used as it is and recorded as unverified.", common + [
            "The block's auth tag on tool-server-1 cannot be checked and is applied: that is what 'unverified' means. The command's own "
            "architecture path is absent, so there is nothing to recompute from."],
        None, S13_UNVERIFIED_BLOCK, True, False, S13_UNVERIFIED_BLOCK, "block-unverified", True, "no architecture file to verify the block against"))
    files.update(s13_scenario(
        "s13-neither-source", "S-13, branch 4: neither source. No finding is elevated, and the run warns, records the cause and continues.",
        common + ["There is no Affected Assets block and no architecture file. Every row is carried as stored, with no tag applied."],
        None, None, False, False, {}, "none", True, "no block and no architecture file"))
    files.update(s13_scenario(
        "s13-drift-form", "S-13, branch 5: a drift form. The populator reads no finding from it, so the block is empty and the tags are "
        "recomputed through the reference set.", common + [
            "threats.md is in the drift form of tachi's shipped samples (S-12(a)): Section N headings, one field table per finding, Section 7 as "
            "a numbered list. Its Affected Assets block is the empty one that Step 1.5 leaves on such a file, so it misses every open finding "
            "and is stale. The findings' components come from the field tables; their delta status is derived from the baseline (S-12(b)), "
            "and any flag that derivation adds is outside this case's assertions."],
        S13_ARCH, {}, True, True, S13_ARCH, "recomputed", True, "the block is empty on a drift form", drift=True, fixed_point=True))
    return files



# --- findings that the agent scores (NEW, or whose ID the baseline used) --------------------------------------------------------
RATIONALE = {
    "cvss": "The weakness is reachable over the network with the stated privileges, so the vector follows the category default.",
    "exploitability": "Public techniques and common tools apply, and the sub-scores reflect that.",
    "scalability": "The weakness can be scripted and repeated against each instance with modest resources.",
    "reachability": "The component sits in the zone shown, with no extra barriers recorded.",
}
EXPL_KEYS = ("known_techniques", "attack_complexity", "tooling_availability", "skill_level")
SCALE_KEYS = ("scriptability", "target_scope", "resource_requirements", "detection_difficulty")


def agent_payload(vector: str, e_total: int, s_total: int, zone: str) -> dict:
    """The judgment a scorer agent returns for one finding (contracts/part-files.md): a vector, eight sub-scores and the reachability
    inputs, with prose that holds no digit."""
    return {"cvss_vector": vector, "exploitability": dict(zip(EXPL_KEYS, sub_scores(e_total))),
            "scalability": dict(zip(SCALE_KEYS, sub_scores(s_total))),
            "reachability": {"zone": zone, "trust_level": PART_TRUST[ZONE_LEVEL[zone]], "auth_barriers": 0, "network_boundaries": 0},
            "rationale": dict(RATIONALE)}


def fresh_expectation(payload: dict, prefix: str, tags: Sequence, run_date: str, bounded: bool = True) -> dict:
    """What the renderer writes for a finding that the agent scored this run: a NEW finding in a baseline-aware run is held to its own
    category's bound (stored as score_bounds), the asset tags raise it by R-25, and the governance fields start from this run's date."""
    category = PREFIX_CATEGORY[prefix]
    bounds = category_bounds(category) if bounded else None
    zone = payload["reachability"]["zone"]
    cvss = chain_tenths(payload["cvss_vector"], tags, bounds)
    expl = mean_tenths(tuple(payload["exploitability"][key] for key in EXPL_KEYS))
    scale = mean_tenths(tuple(payload["scalability"][key] for key in SCALE_KEYS))
    reach = reach_value(zone, ZONE_LEVEL[zone], payload["reachability"]["auth_barriers"], payload["reachability"]["network_boundaries"])
    composite = composite_tenths(cvss, expl, scale, reach)
    band = band_of(composite)
    sla, days, disposition = BAND_GOVERNANCE[band]
    return {"cvss_vector": payload["cvss_vector"], "cvss_base": fmt1(cvss), "exploitability": fmt1(expl), "scalability": fmt1(scale),
            "reachability": fmt1(reach), "composite_score": fmt1(composite), "severity_band": band, "remediation_sla": sla,
            "risk_disposition": disposition, "review_date": add_days(run_date, days), "risk_owner": "Unassigned",
            "score_source": "fresh", "scored_on": run_date,
            "score_bounds": None if bounds is None else [fmt1(bounds[0]), fmt1(bounds[1])]}


def replace_world_findings(master: dict, keep: Sequence, status: dict = None, **more) -> dict:
    """A copy of the world with only the named findings, some of them given a different delta status."""
    status = status or {}
    findings = [dict(f, status=status.get(f["id"], f["status"])) for f in master["findings"] if f["id"] in keep]
    return clone_world(master, findings=findings, **more)


def assign_groups(world: dict, member_ids: Sequence) -> dict:
    """The world with its correlation groups set by hand: each group is a list of IDs, its first member the primary (ADR-050 D8)."""
    by_id = {f["id"]: dict(f, group=None, primary=False) for f in world["findings"]}
    groups = []
    for number, ids in enumerate(member_ids, start=1):
        members = [by_id[i] for i in ids]
        groups.append({"id": "CG-%d" % number, "component": members[0]["comp"], "members": members, "rules": [],
                       "risk": max((m["risk"] for m in members), key=RISK_RANK.get)})
        for position, member in enumerate(members):
            member["group"], member["primary"] = groups[-1]["id"], position == 0
    return clone_world(world, findings=[by_id[f["id"]] for f in world["findings"]], groups=groups)


# --- id-reuse, PR 1 (ruling B) ----------------------------------------------------------------------------------------------
REUSE_PLAN = (("S", "edge-gateway", None), ("S", "auth-broker", None), ("T", "edge-gateway", None), ("T", "auth-broker", None),
              ("T", "intake-agent", None), ("T", "planner-agent", None), ("T", "worker-2", None), ("T", "vector-store-a", None))
PROFILES["reuse"] = variant_profile(REUSE_PLAN, GATED_COMPONENTS, (
    ("I", "audit-ledger", "Component 'legacy-batch-1' removed from architecture", "Medium"),))


def id_reuse_pr1_files() -> dict:
    master = build_world("reuse")
    natural = make_rows(master)
    # The baseline's own T-4: another finding (on vector-store-a) that held the number, scored High, with a human owner and an Accept.
    old_source = next(f for f in master["findings"] if f["id"] == "T-6")
    old = dict(old_source, id="T-4", num=4)
    zone = master["by_name"]["vector-store-a"]["zone"]
    old_row = tagged_row("T-4", "T", "vector-store-a", zone, "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H", 32, 32, 25, "legacy",
                         cvss_of("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H"))
    old_row.update(owner="platform-team", disposition="Accept")
    carried = ("S-1", "S-2", "T-1", "T-2", "T-3")
    rows = {fid: natural[fid] for fid in carried}
    rows["T-4"] = old_row
    resolved_item = master["resolved"][0]
    resolved_row = dict(score_one(master, resolved_item, Rng("reuse/resolved")))
    resolved_row.update({"id": "I-1", "prefix": "I", "comp": resolved_item["comp"], "zone": master["by_name"][resolved_item["comp"]]["zone"],
                         "form": "legacy", "md_vector": resolved_row["vector"], "sarif_vector": None, "owner": "Unassigned",
                         "source": "fresh", "review": add_days(SCORED_ON, resolved_row["sla_days"])})
    rows["I-1"] = resolved_row
    for row in rows.values():
        row["sarif_vector"] = None  # this baseline has no SARIF

    reach_trusted = 25
    # T-4: NEW, and its number is the baseline's. Its vector scores above tampering's bound, so the bound holds it at 8.1.
    bounds = category_bounds("tampering")
    v4, e4, s4 = find_scores("reuse:T-4", lambda vec: cvss_of(vec) > bounds[1] and vec != old_row["vector"],
                             lambda vec, ex, sc: clean_composite(bounds[1], ex, sc, reach_trusted))
    v5, e5, s5 = find_scores("reuse:T-5", lambda vec: bounds[0] <= cvss_of(vec) <= bounds[1],
                             lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach_trusted))
    agent_inputs = {"T-4": agent_payload(v4, e4, s4, "Agent Runtime Zone"), "T-5": agent_payload(v5, e5, s5, "Agent Runtime Zone")}

    ctx = {"tags": (), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ()}
    findings = {fid: finding_record(rows[fid], "clean", ctx) for fid in carried}
    for fid, case, flags in (("T-4", "reused-id", [make_flag("reused-id", "finding_id", "baseline", "T-4", None)]),
                             ("T-5", "new-finding", [])):
        rendered = fresh_expectation(agent_inputs[fid], "T", (), RUN_DATE)
        record = {"case": case, "treatment": "agent", "prefix": "T", "component": next(f["comp"] for f in master["findings"] if f["id"] == fid),
                  "form": "fresh", "stored": None, "rendered": rendered, "flags": flags, "normalized": False, "d10_step": None}
        if fid == "T-4":
            record["baseline_row_not_inherited"] = stored_values(old_row)
        findings[fid] = record
    values = stored_values(resolved_row)
    findings["I-1"] = {"case": "resolved", "treatment": "resolved", "prefix": "I", "component": resolved_row["comp"], "form": "legacy",
                       "stored": values, "rendered": dict(values), "normalized": False, "d10_step": None,
                       "vector_sources": {"markdown": resolved_row["md_vector"], "sarif": None},
                       "flags": [make_flag("resolved", None, None)]}

    run_world = replace_world_findings(master, carried + ("T-4", "T-5"), {"T-4": STATUS_NEW, "T-5": STATUS_NEW})
    base_findings = [f for f in master["findings"] if f["id"] in carried] + [old, resolved_as_finding(master, resolved_item)]
    base = clone_world(master, findings=sorted(base_findings, key=lambda f: prefix_rank(f["id"])), resolved=[], groups=[], scores=rows)
    root = "id-reuse/pr1/"
    files = {
        root + "run/threats.md": render_threats_md(run_world),
        root + "architecture/architecture.md": architecture_text(run_world),
        root + "baseline/risk-scores.md": render_risk_scores_md(base),
        root + "baseline/threats.md": baseline_threats_stub(base),
    }
    routing = {"to_agent": ["T-4", "T-5"], "carried": list(carried), "copy_primary": {}, "carried_peers": {}}
    notes = [
        "Ruling B, PR 1: T-4 is a NEW finding whose ID the baseline's risk-scores.md already used for another finding (a tampering finding on "
        "vector-store-a, scored High, with a human owner and an Accept disposition). A NEW finding whose ID is in any baseline row goes to the "
        "agent, never to the carried set, and is flagged reused-id. Nothing of the old row may reach the new finding.",
        "T-5 is a NEW finding with a number the baseline never used: scored fresh, and not flagged. It is the control.",
        "agent_inputs holds the judgment that a scorer agent returns for T-4 and T-5 (the part payload's keys, with prose that has no digit). "
        "A test builds a tachi.part/1 from it for the planned batch. The expected values follow from it: a NEW finding in a baseline-aware run is "
        "held to its own category's bound (score_bounds, 6.1 to 8.1 for tampering), the owner is Unassigned, and the review date is this "
        "run's date plus the new SLA.",
        "I-1 is in Section 4c as RESOLVED and has a baseline row, which R-30 carries verbatim and marks resolved. It is not a reuse: its ID is "
        "not in Section 7.",
        "The PR 2 half of this variant (a baseline whose high-water mark sits above its live IDs) is T148's, in id-reuse/pr2/.",
    ]
    files[root + "expected-outcomes.json"] = expected_document(
        "id-reuse", "pr1", "S-4's id-reuse variant for PR 1: a NEW finding whose ID the baseline risk-scores.md used (ruling B).", standard_run(),
        legacy_baseline(("threats.md", "risk-scores.md"), note="pre-fix form, no SARIF"),
        {"source": "block", "block_equals_recomputation": True, "tags": {}, "warning": False}, findings, routing=routing,
        extra={"agent_inputs": agent_inputs}, notes=notes)
    return files


# --- ties (R-11) -----------------------------------------------------------------------------------------------------------
def role_tie(row: dict, label: str, moves_band: bool, exact=None, stored_is_exact: bool = False, top: int = 36) -> dict:
    """A row whose composite is an exact x.x5 tie (moving to the boundary `exact` when asked). The baseline stored the lower neighbour,
    or, for a control, the half-up value itself."""
    near = (lambda vec: True) if exact is None else (lambda vec: abs(cvss_of(vec) - exact) <= 25)
    for v in [row["vector"]] + vector_choice(label + "/v", near):
        trial = dict(row, vector=v, md_vector=v, sarif_vector=None, cvss=cvss_of(v))
        found = [c for c in tie_candidates(trial, moves_band, top) if exact is None or c[3] == exact]
        if not found:
            continue
        reach, e_total, s_total, value = found[label_below(label, len(found))]
        out = dict(trial, reach=reach, expl_sub=sub_scores(e_total), expl=mean_tenths(sub_scores(e_total)),
                   scale_sub=sub_scores(s_total), scale=mean_tenths(sub_scores(s_total)))
        out["composite"] = value if stored_is_exact else value - 1
        return set_band(out, band_of(out["composite"]))
    raise ValueError("no tie for %s" % label)


def role_boundary(row: dict, label: str, target: int) -> dict:
    """A row whose composite is exactly 4.0, 7.0 or 9.0 with no rounding: the boundary maps to the higher band."""
    level = ZONE_LEVEL[row["zone"]]
    lo, hi = REACH_RANGE[level]
    for v in vector_choice(label + "/v", lambda vec: abs(cvss_of(vec) - target) <= 25):
        found = []
        for reach in range(lo, hi + 1, 5):
            for e_total in range(12, 41):
                for s_total in range(12, 41):
                    if 35 * cvss_of(v) + 30 * MEAN_OF[e_total] + 15 * MEAN_OF[s_total] + 20 * reach == 100 * target:
                        found.append((reach, e_total, s_total))
        if found:
            reach, e_total, s_total = found[label_below(label, len(found))]
            out = dict(row, vector=v, md_vector=v, sarif_vector=None, cvss=cvss_of(v), reach=reach, expl_sub=sub_scores(e_total),
                       expl=mean_tenths(sub_scores(e_total)), scale_sub=sub_scores(s_total), scale=mean_tenths(sub_scores(s_total)),
                       composite=target)
            return set_band(out, band_of(target))
    raise ValueError("no boundary row for %s" % label)


TIES_PLAN = (
    ("tie-band-moves-70", "S", "edge-gateway", None), ("tie-band-moves-90", "T", "edge-gateway", None),
    ("tie-rounding-only", "R", "edge-gateway", None), ("tie-rounding-only", "I", "edge-gateway", None),
    ("boundary-exact-70", "D", "edge-gateway", None), ("boundary-exact-90", "E", "edge-gateway", None),
    ("boundary-exact-40", "AG", "intake-agent", "AG:autonomy"), ("tie-stored-as-half-up", "LLM", "edge-gateway", "LLM:inject"),
    ("tie-band-moves-40", "MI", "intake-agent", "MI"),
)
PROFILES["ties"] = variant_profile([(prefix, comp, sub) for _, prefix, comp, sub in TIES_PLAN], GATED_COMPONENTS)

# R-11's residual tie lives in the controls stage: residual = inherent x (1 - reduction factor), half-up to one decimal.
RESIDUAL_CASES = (  # (finding, composite in tenths, control status)
    ("S-1", 91, "found"), ("T-1", 49, "found"), ("R-1", 46, "partial"), ("I-1", 83, "found"), ("D-1", 60, "partial"), ("E-1", 77, "missing"))
RESIDUAL_FACTOR = {"found": 50, "partial": 25, "missing": 0}
PROFILES["tiesc"] = variant_profile([("S", "client-portal", None), ("T", "edge-gateway", None), ("R", "edge-gateway", None),
                                     ("I", "edge-gateway", None), ("D", "edge-gateway", None), ("E", "edge-gateway", None)], GATED_COMPONENTS)


def ties_scorer_files() -> dict:
    master = build_world("ties")
    natural = make_rows(master)
    plan = {"tie-band-moves-70": ("band", 70), "tie-band-moves-90": ("band", 90), "tie-band-moves-40": ("band", 40),
            "tie-rounding-only": ("mid", None), "tie-stored-as-half-up": ("exact", None), "boundary-exact-70": ("boundary", 70),
            "boundary-exact-90": ("boundary", 90), "boundary-exact-40": ("boundary", 40)}
    rows, cases = {}, {}
    for entry in TIES_PLAN:
        case = entry[0]
        fid = [i for i in master["findings"] if i["prefix"] == entry[1] and i["comp"] == entry[2]][0]["id"]
        kind, value = plan[case]
        label = "ties:" + fid
        base_row = natural[fid]
        if kind == "band":
            row = role_tie(base_row, label, True, exact=value, top=40)
        elif kind == "mid":
            row = role_tie(base_row, label, False)
        elif kind == "exact":
            row = role_tie(base_row, label, False, stored_is_exact=True)
        else:
            row = role_boundary(base_row, label, value)
        rows[fid], cases[fid] = row, case
    ctx = {"tags": (), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ()}
    findings = {fid: finding_record(row, cases[fid], ctx) for fid, row in rows.items()}
    base = baseline_world(master, rows)
    root = "ties/scorer/"
    files = {
        root + "run/threats.md": render_threats_md(master),
        root + "architecture/architecture.md": architecture_text(master),
        root + "baseline/risk-scores.md": render_risk_scores_md(base),
        root + "baseline/threats.md": baseline_threats_stub(base),
    }
    notes = [
        "R-11. The weighted sum of a tie ends in exactly .x5 (6.95, 8.95, 3.95, mid-band values). The renderer rounds half up; this baseline "
        "stored the lower neighbour.",
        "'tie-band-moves-*': the exact composite is 6.95, 8.95 or 3.95, so half-up gives 7.0, 9.0 or 4.0 and the stored 6.9, 8.9 or 3.9 is in "
        "the band below. The difference moves the band, so it is flagged corrected:severity_band:rounding and R-5 applies: the original "
        "scoring date is kept, and the SLA, disposition and review date follow the new band. The composite's own change is normalized, "
        "and only the band is flagged (D9).",
        "'tie-rounding-only': a mid-band tie whose lower neighbour is in the same band. The composite is normalized to the half-up value and "
        "counted in the run summary, never flagged per finding.",
        "'tie-stored-as-half-up' is the control: the baseline already stored the half-up value.",
        "'boundary-exact-*': composites of exactly 7.0, 9.0 and 4.0 with no rounding. A boundary maps to the higher band, and nothing is flagged.",
    ]
    files[root + "expected-outcomes.json"] = expected_document(
        "ties", "scorer", "S-4's ties variant (R-11), the scorer half: band-moving ties, a rounding-only tie that does not move the band, "
        "a tie stored correctly, and composites exactly on a band boundary.", standard_run(),
        legacy_baseline(("threats.md", "risk-scores.md"), note="pre-fix form, no SARIF"),
        {"source": "block", "block_equals_recomputation": True, "tags": {}, "warning": False}, findings, notes=notes)
    return files


def ties_controls_files() -> dict:
    master = build_world("tiesc")
    natural = make_rows(master)
    rows, cases = {}, {}
    ids = sorted((f["id"] for f in master["findings"]), key=prefix_rank)
    wanted = {fid: composite for fid, composite, _ in RESIDUAL_CASES}
    for fid in ids:
        row = dict(natural[fid])
        target = wanted[fid]
        for v in vector_choice("tiesc:" + fid, lambda vec: True):
            lo, hi = REACH_RANGE[ZONE_LEVEL[row["zone"]]]
            found = [(r, e, s) for r in range(lo, hi + 1, 5) for e in range(12, 41) for s in range(12, 41)
                     if composite_tenths(cvss_of(v), MEAN_OF[e], MEAN_OF[s], r) == target
                     and not composite_is_tie(cvss_of(v), MEAN_OF[e], MEAN_OF[s], r)]
            if found:
                r, e, s = found[label_below("tiesc:" + fid, len(found))]
                row.update(vector=v, md_vector=v, sarif_vector=None, cvss=cvss_of(v), reach=r, expl_sub=sub_scores(e),
                           expl=mean_tenths(sub_scores(e)), scale_sub=sub_scores(s), scale=mean_tenths(sub_scores(s)), composite=target)
                set_band(row, band_of(target))
                break
        else:
            raise ValueError("no row with composite %s" % target)
        rows[fid] = row
    cases_out = []
    for fid, composite, status in RESIDUAL_CASES:
        pct = RESIDUAL_FACTOR[status]
        product = composite * (100 - pct)  # the exact residual in thousandths of a point
        residual = half_up(product, 100)
        exact = ("%d.%03d" % divmod(product, 1000)).rstrip("0")
        exact = exact + "0" if exact.endswith(".") else exact
        floor_tenths = product // 100
        half_even = floor_tenths + (floor_tenths % 2 if product % 100 == 50 else (1 if product % 100 > 50 else 0))
        cases_out.append({"finding": fid, "inherent": fmt1(composite), "inherent_band": band_of(composite), "control_status": status,
                          "reduction_factor": "0.%02d" % pct, "residual_exact": exact, "residual": fmt1(residual),
                          "residual_band": band_of(residual), "is_tie": product % 100 == 50,
                          "half_even_would_give": fmt1(half_even),
                          "float_round_would_give": fmt1(int(round(round(composite / 10.0 * (100 - pct) / 100.0, 1) * 10)))})
    base = baseline_world(master, rows)
    root = "ties/controls/"
    files = {
        root + "run/threats.md": render_threats_md(master),
        root + "run/risk-scores.md": render_risk_scores_md(base),
    }
    notes = [
        "The controls stage's input: run/risk-scores.md is the scorer's output for this run, and each finding's inherent score is its composite. "
        "The controls renderer never re-scores it (ADR-050 D2).",
        "residual = q1(inherent x (1 - reduction factor)), half up, with the P0 factors found 0.50, partial 0.25 and missing 0.00. 'residual_exact' is "
        "the product before rounding. S-1 is the documented 4.55, which must give 4.6; T-1 and R-1 are ties whose half-even rounding would give 2.4 and "
        "3.4, and I-1's 4.15 is a float trap (a binary float holds it just below). D-1 is a partial control with an exact result, and E-1 a missing "
        "control that changes nothing.",
        "The test supplies the controls agent's judgment (control_status per finding); this file fixes the arithmetic that follows from it.",
    ]
    doc = {"schema": "tachi.fixture-expected/1", "variant": "ties", "scenario": "controls", "stage": "compensating-controls",
           "summary": "S-4's ties variant (R-11), the controls half: residual ties.",
           "run": {"date": RUN_DATE, "threats": "run/threats.md", "risk_scores": "run/risk-scores.md", "architecture": None,
                   "how": "copy the scenario directory to a working directory; the controls stage reads run/risk-scores.md as its input"},
           "controls_cases": cases_out, "notes": notes, "flag_reading": list(FLAG_READING)}
    files[root + "expected-outcomes.json"] = dumps(doc)
    return files


# --- the regroup pair (US-5 #6, R-4, R-31, S-7) ----------------------------------------------------------------------------
PAIR_PLAN = (("S", "client-portal", None), ("S", "auth-broker", None), ("T", "edge-gateway", None), ("T", "vector-store-a", None),
             ("R", "intake-agent", None), ("I", "edge-gateway", None), ("D", "edge-gateway", None), ("E", "edge-gateway", None),
             ("AG", "intake-agent", "AG:autonomy"), ("LLM", "edge-gateway", "LLM:inject"))
PROFILES["pair"] = variant_profile(list(PAIR_PLAN), GATED_COMPONENTS)
PAIR_GROUPS_BEFORE = (("I-1", "LLM-1"), ("R-1", "AG-1"))
PAIR_GROUPS_AFTER = (("T-1", "I-1", "D-1", "E-1", "LLM-1"), ("R-1", "AG-1"))
INHERITED_KEYS = ("vector", "md_vector", "sarif_vector", "cvss", "expl_sub", "expl", "scale_sub", "scale", "reach", "composite", "band",
                  "sla", "sla_days", "disposition", "review", "owner")


def banded_row(row: dict, label: str, band: str) -> dict:
    """The row with scores that give a clean composite in the asked band."""
    reach = row["reach"]
    v, e, s = find_scores(label, lambda vec: True,
                          lambda vec, ex, sc: clean_composite(cvss_of(vec), ex, sc, reach)
                          and band_of(composite_tenths(cvss_of(vec), ex, sc, reach)) == band)
    return settle(dict(row, vector=v, md_vector=v, sarif_vector=v, cvss=cvss_of(v), expl_sub=sub_scores(e), expl=mean_tenths(sub_scores(e)),
                       scale_sub=sub_scores(s), scale=mean_tenths(sub_scores(s))))


def group_records(groups: Sequence, kept: Sequence) -> list:
    return [{"id": "CG-%d" % number, "primary": ids[0], "members": [i for i in ids if i in kept]} for number, ids in enumerate(groups, start=1)]


def regroup_pair_files() -> dict:
    master = build_world("pair")
    natural = make_rows(master)
    ids = [f["id"] for f in master["findings"]]
    before = [i for i in ids if i != "D-1"]  # D-1 is NEW in the second run
    rows = {fid: dict(natural[fid]) for fid in before}
    rows["T-1"] = banded_row(rows["T-1"], "pair:T-1", "Medium")
    rows["I-1"] = banded_row(rows["I-1"], "pair:I-1", "High")
    rows["E-1"] = banded_row(rows["E-1"], "pair:E-1", "High")
    rows["E-1"]["owner"] = "appsec-team"
    for peer, primary in (("LLM-1", "I-1"), ("AG-1", "R-1")):  # the baseline's peers carry their primary's scores whole
        rows[peer] = dict(rows[peer], **{key: rows[primary][key] for key in INHERITED_KEYS})
    for row in rows.values():
        row["source"] = "fresh"

    def world_for(keep, status, groups, source, baseline_date):
        cfg = dict(master["cfg"], baseline_source=source, dates=dict(master["cfg"]["dates"], baseline=baseline_date))
        return assign_groups(replace_world_findings(master, keep, status, cfg=cfg), groups)

    run1 = world_for(before, {}, PAIR_GROUPS_BEFORE, "baseline/threats.md", SCORED_ON)
    run2 = world_for(ids, {"D-1": STATUS_NEW, "E-1": STATUS_UPDATED}, PAIR_GROUPS_AFTER, "run1/threats.md", RUN_DATE)
    run3 = world_for(ids, {}, PAIR_GROUPS_AFTER, "run2/threats.md", RUN_DATE)
    base = assign_groups(clone_world(master, findings=[f for f in master["findings"] if f["id"] in before], resolved=[], scores=rows),
                         PAIR_GROUPS_BEFORE)

    ctx = {"tags": (), "run_date": RUN_DATE, "baseline_date": SCORED_ON, "compound_zones": ()}
    # run 1: the legacy baseline, scored again with the same groups. Nothing is wrong, so nothing is flagged.
    run1_findings = {fid: finding_record(rows[fid], "unchanged-group" if fid in ("I-1", "LLM-1", "R-1", "AG-1") else "ungrouped", ctx)
                     for fid in before}
    # run 2: the regroup. T-1 is the new primary; I-1 and LLM-1 keep their scores and diverge; D-1 and E-1 copy T-1.
    run2_findings = {fid: finding_record(rows[fid], "ungrouped", ctx) for fid in before}
    primary = run2_findings["T-1"]
    run2_findings["T-1"]["case"] = "new-primary"
    for fid in ("I-1", "LLM-1"):
        record = run2_findings[fid]
        record["case"] = "unchanged-peer-diverges"
        record["flags"].append(make_flag("divergent", "composite_score", "primary=T-1", record["stored"]["composite_score"],
                                         primary["rendered"]["composite_score"]))
    for fid in ("R-1", "AG-1"):
        run2_findings[fid]["case"] = "unchanged-group"
    for fid, case in (("D-1", "new-peer"), ("E-1", "updated-peer")):
        own = rows.get(fid)
        rendered = dict(primary["rendered"])
        rendered["risk_owner"] = own["owner"] if own else "Unassigned"
        rendered["review_date"] = add_days(RUN_DATE, sla_day_count(rendered["remediation_sla"]))
        run2_findings[fid] = {"case": case, "treatment": "copy-primary", "prefix": fid.partition("-")[0],
                              "component": next(f["comp"] for f in master["findings"] if f["id"] == fid), "form": "legacy",
                              "stored": stored_values(own) if own else None, "rendered": rendered, "flags": [], "normalized": False,
                              "d10_step": None, "primary": "T-1"}
    # run 3: an unchanged re-run on run 2's output. Every value is carried as run 2 wrote it.
    run3_findings = {}
    for fid in ids:
        values = dict(run2_findings[fid]["rendered"])
        flags = ([make_flag("divergent", "composite_score", "primary=T-1", values["composite_score"],
                            run2_findings["T-1"]["rendered"]["composite_score"])] if fid in ("I-1", "LLM-1") else [])
        run3_findings[fid] = {"case": "rerun", "treatment": "carried", "prefix": fid.partition("-")[0], "component": run2_findings[fid]["component"],
                              "form": "renderer", "stored": values, "rendered": dict(values), "flags": flags, "normalized": False,
                              "d10_step": "renderer"}

    def section(findings, routing, groups, threats, baseline_dir):
        ordered = {fid: findings[fid] for fid in sorted(findings, key=prefix_rank)}
        return {"threats": threats, "baseline_dir": baseline_dir, "routing": routing, "groups": groups, "findings": ordered,
                "unflagged": unflagged_ids(ordered), "counts": tally(ordered)}

    peers_before = {"LLM-1": "I-1", "AG-1": "R-1"}
    peers_after = {"I-1": "T-1", "LLM-1": "T-1", "AG-1": "R-1"}
    runs = {
        "run1": section(run1_findings, {"to_agent": [], "carried": sorted(before, key=prefix_rank), "copy_primary": {}, "carried_peers": peers_before},
                        group_records(PAIR_GROUPS_BEFORE, before), "run1/threats.md", "baseline"),
        "run2": section(run2_findings, {"to_agent": [], "carried": sorted((fid for fid in before if fid != "E-1"), key=prefix_rank),
                                        "copy_primary": {"D-1": "T-1", "E-1": "T-1"}, "carried_peers": peers_after},
                        group_records(PAIR_GROUPS_AFTER, ids), "run2/threats.md", "run1"),
        "run3": section(run3_findings, {"to_agent": [], "carried": sorted(ids, key=prefix_rank), "copy_primary": {},
                                        "carried_peers": dict(peers_after, **{"D-1": "T-1", "E-1": "T-1"})},
                        group_records(PAIR_GROUPS_AFTER, ids), "run3/threats.md", "run2"),
    }
    notes = [
        "Three runs in sequence, each writing its outputs next to its own threats.md (--out run1, then run2, then run3), so that each run's "
        "baseline.source finds the last run's output: run1 reads baseline/, run2 reads run1/, run3 reads run2/. run1 and run2's baselines "
        "are therefore the renderer's own output, and only the first baseline is a fixture file.",
        "Run 1 scores the legacy baseline again with the baseline's groups, CG-1 = [I-1, LLM-1] and CG-2 = [R-1, AG-1]. Nothing is wrong and "
        "nothing is flagged: it is the first renderer run, and the scores it carries are the ones run 2 must not move.",
        "Run 2 regroups. Correlation now puts T-1, an ungrouped Medium finding, first in CG-1, so the group's primary changes from I-1 (High) to "
        "T-1. No carried finding's score, band or SLA changes because of the regroup alone (US-5 #6). I-1 and LLM-1 are UNCHANGED peers whose "
        "carried score differs from the new primary's: they keep it and are flagged divergent:composite_score:primary=T-1. D-1 (NEW) and E-1 "
        "(UPDATED) are peers that copy T-1's vector and scores; E-1 keeps its owner and, because its band changes, restarts its clock.",
        "Run 3 re-runs run 2's file with every status UNCHANGED, on run 2's output. It keeps every key and value of run 2, and the divergences "
        "stay flagged, since I-1 and LLM-1 still differ from T-1. D-1 and E-1 are now carried peers that equal their primary.",
        "S-7: the correlation outcome of the pair (which findings group, and each group's primary) is the same whatever the SARIF recipe does; "
        "'groups' lists it per run, primary first.",
        "baseline/risk-scores.sarif is a pre-fix file: its hashes are the legacy ones, which a renderer never copies and never matches on.",
    ]
    doc = {"schema": "tachi.fixture-expected/1", "variant": "regroup-pair", "scenario": "main", "stage": "risk-score",
           "summary": "S-4's regroup pair: correlation regroups carried findings and changes a primary, with a NEW peer, an UPDATED peer, an "
                      "UNCHANGED peer whose score differs from its new primary's, and an unchanged re-run.",
           "run": {"date": RUN_DATE, "architecture": "architecture/architecture.md", "sequence": ["run1", "run2", "run3"],
                   "out_dirs": {"run1": "run1", "run2": "run2", "run3": "run3"},
                   "how": "copy the scenario directory to a working directory and run the three in order from there"},
           "baseline": legacy_baseline(("threats.md", "risk-scores.md", "risk-scores.sarif"), note="pre-fix form with its SARIF; only run1 reads it"),
           "tag_source": {"source": "block", "block_equals_recomputation": True, "tags": {}, "warning": False},
           "runs": runs,
           "identity": {"keys_equal": ["run1", "run2", "run3"], "for_findings_present_in_both": True,
                        "rerun_matches": {"run3": "run2"},
                        "note": "every carried finding keeps its SARIF identity fields across the regroup, and the unchanged re-run keeps "
                                "them and its values; the properties that name a baseline state or a score source may differ with the status"},
           "populator_fixed_point": True, "notes": notes, "flag_reading": list(FLAG_READING)}
    root = "regroup-pair/main/"
    return {
        root + "baseline/risk-scores.md": render_risk_scores_md(base),
        root + "baseline/risk-scores.sarif": render_risk_scores_sarif(base),
        root + "baseline/threats.md": baseline_threats_stub(base),
        root + "architecture/architecture.md": architecture_text(master),
        root + "run1/threats.md": render_threats_md(run1),
        root + "run2/threats.md": render_threats_md(run2),
        root + "run3/threats.md": render_threats_md(run3),
        root + "expected-outcomes.json": dumps(doc),
    }

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


def _run_directory(world: dict, root: str) -> dict:
    """The files of one baseline run directory, under root: the three reports, their SARIF files and the trees."""
    files = {
        root + "/threats.md": render_threats_md(world),
        root + "/threats.sarif": render_threats_sarif(world),
        root + "/risk-scores.md": render_risk_scores_md(world),
        root + "/risk-scores.sarif": render_risk_scores_sarif(world),
        root + "/compensating-controls.md": render_controls_md(world),
        root + "/compensating-controls.sarif": render_controls_sarif(world),
    }
    if world["cfg"]["trees"]:
        for path, text in tree_files(world).items():
            files[root + "/" + path] = text
    return files


def part_architecture(rng: Rng) -> dict:
    """T019: the architecture description of the base set: 25 components, 5 zones, all seven MAESTRO layers."""
    return {"architecture/architecture.md": architecture_text(build_world("base"))}


def part_baseline(rng: Rng) -> dict:
    """T019: the baseline run directory: 408 open findings, 6 resolved, 21 groups, trees, scores and controls, three SARIF files."""
    return _run_directory(build_world("base"), "baseline")


def part_stub_codebase(rng: Rng) -> dict:
    """T019: a small code tree with one control per module, so that the controls stage finds evidence for some findings."""
    return {"stub-codebase/" + path: text for path, text in stub_files(build_world("base")).items()}


def part_gated_subset(rng: Rng) -> dict:
    """T019: the small Mermaid-free subset for gated CI: the same run directory at 42 findings, a text architecture, no trees."""
    world = build_world("gated")
    files = _run_directory(world, "gated-subset/baseline")
    files["gated-subset/architecture/architecture.md"] = architecture_text(world)
    return files


def part_seeded_error(rng: Rng) -> dict:
    """T040: per prefix, a wrong composite, band, vector and reachability value, a missing vector, controls."""
    return seeded_error_files()


def part_legacy_format(rng: Rng) -> dict:
    """T040: no sub-score tables, partial vectors in markdown, full vectors in SARIF, one disagreement (R-26)."""
    files = legacy_format_files()
    files.update(legacy_no_date_files())
    return files


def part_tagged(rng: Rng) -> dict:
    """T040: tagged components, findings above 9.2, a carried legacy finding, ruling A's band moves, and S-13's five branches."""
    files = tagged_renderer_form_files()
    files.update(tagged_legacy_form_files())
    files.update(tagged_s13_files())
    return files


def part_id_reuse(rng: Rng) -> dict:
    """T040: PR 1's case (a NEW finding reusing a baseline ID). T148: PR 2's high-water-mark and no-mark baselines."""
    files = id_reuse_pr1_files()  # T148 adds id_reuse_pr2_files() here, under id-reuse/pr2/
    return files


def part_ties(rng: Rng) -> dict:
    """T040: a band-moving composite tie, a rounding-only tie and a residual tie (R-11)."""
    files = ties_scorer_files()
    files.update(ties_controls_files())
    return files


def part_regroup_pair(rng: Rng) -> dict:
    """T040: two runs where correlation regroups carried findings and moves a primary, plus a re-run."""
    return regroup_pair_files()


def part_chain_cap(rng: Rng) -> dict:
    """T148: chain material that yields more than 105 consolidated chains (S-3(g)'s offline test)."""
    return chain_cap_files()


def part_pr2_runs(rng: Rng) -> dict:
    """T103: threat-model run dirs (records, briefs, ID map, Phase 1 tables), tree batches, report parts (code below the id-reuse part)."""
    return pr2r_files(PR2R_ROOT)


# --------------------------------------------------------------------------- T148: PR 2's fixture cases
# Three cases that wait on no ruling, in the scenario layout and envelope of T040's variants (<variant>/<scenario>/, with
# expected-outcomes.json in format tachi.fixture-expected/1): chain-cap/main, id-reuse/pr2 and id-reuse/pr2-no-mark. Every name
# below starts cc_, ir2_ or pr2_ or is a PR2_ / CC_ / IR2_ constant, so that T040's module-level names (merged in at T085) can't meet them.
# Expected values are worked out here from the spec and ADR-050, never read from a script: no chain script or reissue check exists yet.
PR2_RUN_DATE = "2026-11-23"
PR2_BASELINE_DATE = "2026-11-09"
PR2_RUN_ID = "2026-11-23T10-00-00"
PR2_BASELINE_RUN_ID = "2026-11-09T10-00-00"
PR2_DROP_NOTE = "Remediate as described in the baseline report."


def pr2_expected_document(variant: str, scenario: str, stage: str, summary: str, run: dict, extra: dict, notes: Sequence) -> str:
    doc = {"schema": "tachi.fixture-expected/1", "variant": variant, "scenario": scenario, "stage": stage, "summary": summary,
           "run": run, "notes": list(notes)}
    doc.update(extra)
    return dumps(doc)


def pr2_section_row(finding: dict, layer_cell: str) -> tuple:
    """One Section 7 row, in the shipped column order."""
    return (finding["id"], finding["status"], CATEGORY_TITLE[finding["prefix"]], EM if finding["pattern"] == "none" else finding["pattern"],
            finding["comp"], layer_cell, finding["short"], finding["risk"], finding["mit_short"])


PR2_ACTION_COLUMNS = ("Finding ID", "Status", "Category", "Pattern", "Component", "MAESTRO Layer", "Threat", "Risk Level", "Mitigation")


def pr2_frontmatter(date: str, run_id: str) -> list:
    """The front matter of a run that has no baseline of its own (the form the shipped writer leaves for a first run)."""
    return ["---", 'schema_version: "1.4"', 'date: "%s"' % date, 'input_format: "free-text"', 'classification: "confidential"',
            'run_id: "%s"' % run_id, "baseline:", "  source: null", "  date: null", "  finding_count: null", "  run_id: null",
            "coverage_gate:", '  status: "pass"', "  gaps: []", "---", ""]


# --- chain-cap (S-4, S-3, FR-K4.1b) ----------------------------------------------------------------------------------------
# Chain material for attack-chains.py: a threats.md cut down to the sections that the script reads and that its outcome record
# lands between (5, 6, 7, 8 and Affected Assets), and the persisted Phase 1 inventory (contracts/threat-model-records.md). The
# material is a set of islands, and no flow joins two islands, so each island forms its chains alone and the counts add up. Every
# island is declared with the chains it must give. expected-outcomes.json is built from that declaration, and the test re-derives
# the chains from the files with its own coding of S-3 and compares: a mistake in either shows. The links an island needs are rows
# of attack-chain-patterns-shared.md's transition table. The plain pairs use only rows with no reverse row, so a pair has one link.
CC_RISK = {"C": "Critical", "H": "High", "M": "Medium", "L": "Low"}
CC_PLAIN_TYPES = (  # (source prefix, source layer, target prefix, target layer): table rows whose reverse is not a row
    ("T", 1, "S", 3), ("T", 1, "E", 3), ("I", 1, "I", 2), ("I", 1, "I", 7), ("T", 2, "S", 3), ("I", 2, "I", 3),
    ("I", 2, "I", 7), ("E", 3, "E", 7), ("I", 3, "I", 7), ("T", 4, "T", 6), ("I", 4, "I", 3), ("I", 4, "I", 6),
    ("D", 4, "D", 7), ("T", 5, "T", 6), ("R", 5, "R", 6), ("R", 5, "R", 3), ("D", 5, "D", 6), ("T", 6, "E", 3),
    ("S", 6, "S", 3), ("I", 6, "I", 3), ("E", 6, "E", 3), ("E", 6, "E", 7), ("T", 7, "T", 3), ("T", 7, "T", 2),
)
CC_SEVERITY_PAIRS = ("CH", "HC", "HH", "CC", "MC", "CL", "HM", "LH", "CM", "MH", "HL", "LC")  # at least one Critical or High each
CC_PLAIN_ISLANDS = 109  # with the specials below: 120 consolidated chains, 16 more candidates than that
CC_CAP, CC_SURFACED = 100, 5  # S-3(g): at most 100 compact rows. S-3(f): at most five full chains
CC_STEMS = {1: ("model-host", "embed-node"), 2: ("feature-store", "vector-index"), 3: ("task-agent", "tool-router"),
            4: ("runtime-pool", "deploy-hub"), 5: ("trace-sink", "eval-bench"), 6: ("policy-gate", "audit-vault"),
            7: ("partner-api", "user-portal"), None: ("legacy-adapter", "legacy-adapter")}
CC_KIND = {"partner-api": "External Entity", "user-portal": "External Entity", "feature-store": "Data Store",
           "vector-index": "Data Store", "trace-sink": "Data Store"}
CC_ABOUT = {"model-host": "Serves a hosted model endpoint to the agents", "embed-node": "Computes embeddings for retrieval",
            "feature-store": "Keeps engineered features for the agents", "vector-index": "Holds the retrieval index",
            "task-agent": "Plans and runs one class of task", "tool-router": "Routes tool calls from the agents",
            "runtime-pool": "Hosts the agent workers", "deploy-hub": "Rolls out agent releases",
            "trace-sink": "Collects traces from the agents", "eval-bench": "Scores agent runs against fixed cases",
            "policy-gate": "Checks each action against policy", "audit-vault": "Keeps the signed audit records",
            "partner-api": "Exposes the platform to a partner system", "user-portal": "Front end for operators",
            "legacy-adapter": "Adapter whose layer was never classified"}
CC_ZONE = {1: "Agent Runtime Zone", 2: "Data Zone", 3: "Agent Runtime Zone", 4: "Operations Zone", 5: "Operations Zone",
           6: "Operations Zone", 7: "Edge DMZ", None: "Operations Zone"}
CC_ASSETS = ("job queue entries", "model prompts", "feature vectors", "trace spans", "policy decisions", "partner requests", "audit records")
CC_TOKENS = ("service credential", "API token", "signing key", "session token")
CC_FLOW_DATA = (("Task requests", "HTTPS (TLS 1.3)"), ("Run events", "gRPC (mTLS)"), ("Model calls", "HTTPS (TLS 1.3)"),
                ("Policy checks", "gRPC (mTLS)"))
CC_ARROW = "\u2192"


def cc_node(prefix, layer, risk=None, sub=None) -> dict:
    """One component. prefix None: a hop with no finding. layer None: a component whose layer was never classified."""
    return {"prefix": prefix, "layer": layer, "risk": CC_RISK[risk] if risk else None, "sub": sub}


def cc_island(kind: str, nodes: list, flows: Sequence, chains: Sequence, candidates: int, dropped: dict = None, **more) -> dict:
    island = {"kind": kind, "nodes": nodes, "flows": [tuple(flow) for flow in flows], "chains": [list(order) for order in chains],
              "candidates": candidates, "dropped": dropped or {}}
    island.update(more)
    return island


def cc_islands() -> list:
    n = cc_node
    out = [
        # A V: two four-finding arms that end at one sink. Their initial exploits differ and neither chain is a run of the other, so
        # both stay (S-3(d)), and only one surfaces (S-3(f)). The arms' tails fold into them: 2 + 2 chains that are not listed.
        cc_island("v-arms", [n("T", 5, "H"), n("T", 6, "M"), n("E", 3, "H"), n("T", 4, "M"), n("T", 6, "H"), n("E", 3, "H"), n("E", 7, "C")],
                  [(0, 1), (1, 2), (2, 6), (3, 4), (4, 5), (5, 6)], [[0, 1, 2, 6], [3, 4, 5, 6]], 6, {"folded": 4}),
        # A path of four with its own end: its tails [1,2,3] and [2,3] fold into it.
        cc_island("path-4", [n("T", 4, "H"), n("T", 6, "C"), n("E", 3, "H"), n("E", 7, "C")], [(0, 1), (1, 2), (2, 3)], [[0, 1, 2, 3]], 3,
                  {"folded": 2}),
        # Paths of three: the tail [1,2] folds into each.
        cc_island("path-3", [n("I", 1, "H"), n("I", 2, "C"), n("I", 3, "M")], [(0, 1), (1, 2)], [[0, 1, 2]], 2, {"folded": 1}),
        cc_island("path-3", [n("I", 4, "C"), n("I", 3, "H"), n("I", 7, "M")], [(0, 1), (1, 2)], [[0, 1, 2]], 2, {"folded": 1}),
        cc_island("path-3", [n("T", 5, "M"), n("T", 6, "H"), n("E", 3, "C")], [(0, 1), (1, 2)], [[0, 1, 2]], 2, {"folded": 1}),
        # A mutual pair: each finding has a link to the other, so two chains hold the same two findings. The better-ranked one stays.
        cc_island("mutual", [n("T", 1, "H"), n("T", 2, "M")], [(0, 1)], [], 2, {"deduplicated": 1}, mutual=[(0, 1)]),
        cc_island("mutual", [n("E", 3, "C"), n("T", 2, "H")], [(0, 1)], [], 2, {"deduplicated": 1}, mutual=[(0, 1)]),
        cc_island("mutual", [n("D", 3, "H"), n("D", 4, "H")], [(1, 0)], [], 2, {"deduplicated": 1}, mutual=[(0, 1)]),
        # Components that no flow joins directly: the link runs through the transitive closure (two hops, then three hops against
        # the link's direction). Their flows pass through hops that carry no finding.
        cc_island("closure-2", [n("I", 3, "H"), n(None, 4), n("I", 7, "C")], [(0, 1), (1, 2)], [[0, 2]], 1, closure=2),
        cc_island("closure-3", [n("T", 7, "H"), n(None, 3), n(None, 2), n("T", 3, "C")], [(3, 2), (2, 1), (1, 0)], [[0, 3]], 1, closure=3),
        # Pairs that form a chain with no Critical or High finding: candidates only.
        cc_island("filtered", [n("T", 4, "M"), n("T", 6, "L")], [(0, 1)], [], 1, {"filtered": 1}),
        cc_island("filtered", [n("I", 2, "L"), n("I", 3, "M")], [(0, 1)], [], 1, {"filtered": 1}),
        cc_island("filtered", [n("R", 5, "M"), n("R", 3, "M")], [(1, 0)], [], 1, {"filtered": 1}),
        cc_island("filtered", [n("D", 5, "L"), n("D", 6, "L")], [(0, 1)], [], 1, {"filtered": 1}),
    ]
    for index in range(CC_PLAIN_ISLANDS):
        source, from_layer, target, to_layer = CC_PLAIN_TYPES[index % len(CC_PLAIN_TYPES)]
        from_risk, to_risk = CC_SEVERITY_PAIRS[label_below("cc:severity:%d" % index, len(CC_SEVERITY_PAIRS))]
        reverse = label_below("cc:direction:%d" % index, 3) == 0  # one in three: the flow runs against the link
        out.append(cc_island("plain", [n(source, from_layer, from_risk), n(target, to_layer, to_risk)], [(1, 0) if reverse else (0, 1)], [[0, 1]], 1))
    first = len(out) - CC_PLAIN_ISLANDS  # findings that the chain script must leave out, joined to the first plain islands by a flow
    for offset, (prefix, layer, sub, risk) in enumerate((("AG", 3, "AG:autonomy", "C"), ("AG", 4, "AG:tool", "H"), ("LLM", 1, "LLM:inject", "C"),
                                                         ("LLM", 2, "LLM:poison", "H"))):
        island = out[first + offset]
        island["nodes"].append(n(prefix, layer, risk, sub))
        island["flows"].append((len(island["nodes"]) - 1, 0))
    for offset, (prefix, risk, inbound) in enumerate((("S", "H", True), ("T", "C", False))):  # a STRIDE finding on an unclassified layer
        island = out[first + 4 + offset]
        island["nodes"].append(n(prefix, None, risk))
        island["flows"].append((len(island["nodes"]) - 1, 0) if inbound else (0, len(island["nodes"]) - 1))
    return out


def cc_material() -> dict:
    """Everything the chain-cap files and expectations need: names, finding IDs and texts, the inventory, and the declared chains."""
    islands = cc_islands()
    count = 0
    for island in islands:  # component names: a stem for the layer and a running number, unique across the whole set
        for node in island["nodes"]:
            count += 1
            stems = CC_STEMS[node["layer"]]
            node["name"] = "%s-%d" % (stems[label_below("cc:stem:%d" % count, len(stems))], count)
            node["stem"] = node["name"].rpartition("-")[0]
    pool = [(i, j) for i, island in enumerate(islands) for j, node in enumerate(island["nodes"]) if node["prefix"] is not None]
    pool.sort(key=lambda pair: label_hash("cc:id:%d:%d" % pair))  # numbers go out in an order unrelated to the islands'
    numbers: dict = {}
    for i, j in pool:
        node = islands[i]["nodes"][j]
        numbers[node["prefix"]] = numbers.get(node["prefix"], 0) + 1
        node["num"], node["id"] = numbers[node["prefix"]], finding_id_text(node["prefix"], numbers[node["prefix"]])
    used: dict = {}
    for i, island in enumerate(islands):
        for j, node in enumerate(island["nodes"]):
            if node["prefix"] is None:
                continue
            near = [island["nodes"][a if b == j else b]["name"] for a, b in island["flows"] if j in (a, b)]
            comp = {"name": node["name"], "dfd": "Process", "layer": node["layer"] or 3, "zone": CC_ZONE[node["layer"]],
                    "asset": CC_ASSETS[label_below("cc:asset:" + node["name"], len(CC_ASSETS))],
                    "tok": CC_TOKENS[label_below("cc:token:" + node["name"], len(CC_TOKENS))],
                    "peers": [(name, "an internal channel") for name in near[:1]], "ai": (), "traits": ()}
            _, _, short, mit_short, _ = compose_text({"observer": "the trace collector"}, comp, node["prefix"], node["sub"], node["id"], used)
            node.update(short=short, mit_short=mit_short)
    findings = [{"id": node["id"], "prefix": node["prefix"], "num": node["num"], "status": STATUS_NEW, "comp": node["name"],
                 "layer": node["layer"], "risk": node["risk"], "pattern": "none", "short": node["short"], "mit_short": node["mit_short"]}
                for island in islands for node in island["nodes"] if node["prefix"] is not None]
    return {"islands": islands, "findings": findings, "chains": cc_chains(islands)}


def cc_breaking_target(ids: list, risks: list) -> str:
    """The orchestrator's Step 4: the higher-severity finding of a pair (the first on a tie), the middle of three, otherwise the
    intermediate finding with the highest i x (n - 1 - i), the higher severity next and the earlier position last."""
    size = len(ids)
    if size == 2:
        return ids[1] if RISK_RANK[risks[1]] > RISK_RANK[risks[0]] else ids[0]
    if size == 3:
        return ids[1]
    return ids[max(range(1, size - 1), key=lambda i: (i * (size - 1 - i), RISK_RANK[risks[i]], -i))]


def cc_reaches(island: dict, source: int, target: int) -> bool:
    """Whether the island's flows lead from one node to another: a direct flow is one hop, and hops add up (the transitive closure)."""
    ahead: dict = {}
    for first, second in island["flows"]:
        ahead.setdefault(first, []).append(second)
    seen: set = set()
    stack = list(ahead.get(source, ()))
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(ahead.get(node, ()))
    return target in seen


def cc_chains(islands: list) -> list:
    """The consolidated chains the islands declare, ranked as S-3(e) says, each with its layers, surfacing and breaking target."""
    chains = []
    for island in islands:
        orders = list(island["chains"])
        for first, second in island.get("mutual", ()):  # identical finding sets: the chain whose IDs rank first stays
            ranked = sorted(([first, second], [second, first]), key=lambda order: tuple(prefix_rank(island["nodes"][k]["id"]) for k in order))
            orders.append(ranked[0])
        for order in orders:
            nodes = [island["nodes"][k] for k in order]
            ids, risks = [node["id"] for node in nodes], [node["risk"] for node in nodes]
            chains.append({"members": ids, "layers": ["L%d" % node["layer"] for node in nodes], "risks": risks,
                           "max_severity": max(risks, key=RISK_RANK.get), "breaking_target": cc_breaking_target(ids, risks),
                           "kind": island["kind"], "against_flow": any(not cc_reaches(island, a, b) for a, b in zip(order, order[1:]))})
    chains.sort(key=lambda c: (-RISK_RANK[c["max_severity"]], -len(c["members"]), tuple(prefix_rank(i) for i in c["members"])))
    ended: dict = {}
    for rank, chain in enumerate(chains, start=1):
        chain["id"] = "CHAIN-%03d" % rank
        ended.setdefault(chain["members"][-1], []).append(chain["id"])
    for chain in chains:
        chain["surfaced"] = False
    surfaced = 0
    for chain in chains:  # S-3(f): in rank order, unless a surfaced chain already ends at the same finding; stop at five
        terminal = chain["members"][-1]
        if surfaced < CC_SURFACED and not any(other["surfaced"] for other in chains if other["members"][-1] == terminal):
            chain["surfaced"] = True
            chain["converging"] = len(ended[terminal]) - 1  # the other consolidated chains that end at this finding
            surfaced += 1
    return chains


def cc_chain_record(chain: dict) -> dict:
    keys = ("id", "members", "layers", "max_severity", "surfaced", "breaking_target", "kind", "against_flow") + (
        ("converging",) if chain["surfaced"] else ())
    return {key: chain[key] for key in keys}


def cc_rows(chains: list) -> list:
    """The compact rows of attack-chains.md Section 3 (contracts/threat-model-records.md): every chain that is not shown in full."""
    rest = [chain for chain in chains if not chain["surfaced"]]
    return ["| %s | %s | %s | %s | %s |" % (chain["id"], (" %s " % CC_ARROW).join(chain["layers"]), (" %s " % CC_ARROW).join(chain["members"]),
                                         chain["max_severity"], chain["breaking_target"]) for chain in rest[:CC_CAP]]


def cc_threats_md(material: dict) -> str:
    """The chain material's threats.md: front matter, and the sections 5 to 8 and Affected Assets in their shipped order. Sections 5, 6
    and 8 are cut to a sentence, because the script reads none of them. Section 7 is the reference set it reads."""
    ranked = sorted(material["findings"], key=lambda f: (-RISK_RANK[f["risk"]], TABLE_ORDER.index(f["prefix"]), f["num"]))
    rows = [pr2_section_row(f, layer_label(f["layer"]) if f["layer"] else "Unclassified") for f in ranked]
    out = pr2_frontmatter(PR2_RUN_DATE, PR2_RUN_ID) + [
        "# Threat Model Report", "",
        "This file is the chain material of F-374's chain-cap variant: a threats.md cut down to the sections that attack-chains.py reads "
        "and that its outcome record lands between. The inventory it reads is beside it, under tachi-build/phase1/.", "",
        "---", "", "## 5. Coverage Matrix", "", "The coverage tables are left out of this cut.", "", "---", "",
        "## 6. Risk Summary", "", "The risk summary is left out of this cut.", "", "---", "",
        "## 7. Recommended Actions", "",
        "All findings sorted by risk level descending, then by table order. Critical and High findings should be addressed before deployment.", "",
        table(PR2_ACTION_COLUMNS, rows), "", "---", "", "## 8. Delta Summary", "",
        "This run has no baseline, so every finding is NEW.", "", "---", "", "## Affected Assets", "",
        table(("Finding ID", "Affected Assets"), [(f["id"], "[]") for f in ranked])]
    return "\n".join(out)


def cc_inventory(material: dict) -> str:
    """tachi.phase1-inventory/1 (contracts/threat-model-records.md): every component, every flow, and the zones."""
    components, flows, zones = [], [], {}
    for island in material["islands"]:
        for node in island["nodes"]:
            layer = node["layer"]
            components.append({"name": node["name"], "dfd_type": CC_KIND.get(node["stem"], "Process"),
                               "maestro_layer": "L%d" % layer if layer else "Unclassified", "description": CC_ABOUT[node["stem"]]})
            zones.setdefault(CC_ZONE[layer], []).append(node["name"])
        for source, target in island["flows"]:
            data, protocol = CC_FLOW_DATA[label_below("cc:flow:%s" % island["nodes"][source]["name"], len(CC_FLOW_DATA))]
            flows.append({"source": island["nodes"][source]["name"], "destination": island["nodes"][target]["name"], "data": data, "protocol": protocol})
    return dumps({"schema": "tachi.phase1-inventory/1", "components": components, "data_flows": flows,
                  "trust_zones": [{"name": name, "components": zones[name]} for name in sorted(zones)]})


def chain_cap_files() -> dict:
    material = cc_material()
    chains = material["chains"]
    shown = [chain for chain in chains if chain["surfaced"]]
    candidates, consolidated = sum(i["candidates"] for i in material["islands"]), len(chains)
    dropped = {kind: sum(i["dropped"].get(kind, 0) for i in material["islands"]) for kind in ("deduplicated", "filtered", "folded")}
    if candidates != consolidated + sum(dropped.values()) or consolidated <= CC_CAP + CC_SURFACED or len(shown) != CC_SURFACED:
        raise ValueError("chain-cap: the declared islands do not add up (%d candidates, %d consolidated, %s dropped)" % (candidates, consolidated, dropped))
    rows = cc_rows(chains)
    listed = len(rows)
    outcome = "chains written (%d); candidates %d; surfaced %d" % (consolidated, candidates, len(shown))
    root = "chain-cap/main/"
    notes = [
        "The material is %d islands and no flow joins two. Each island is a short list of components with findings, and the chains it gives are "
        "declared with it, so the counts below are by construction. The test re-derives them from the committed files with its own coding of "
        "S-3, which is the check that the declaration and the files agree." % len(material["islands"]),
        "%d consolidated chains: more than the 105 at which S-3(g)'s bound bites. At most five surface, so %d are not shown in full, 100 of them get "
        "a compact row and the last line states how many are not listed (%d)." % (consolidated, consolidated - len(shown), consolidated - len(shown) - listed),
        "Surfacing (S-3(f)): the V island's two chains end at one finding. Whichever ranks first surfaces, and carries converging 1; the other "
        "ranks within the first few places and is passed over. It is not surfaced, so it has a compact row.",
        "candidates minus consolidated is the sum of the three drops: tails that fold into a longer chain, a mutual pair's second chain, "
        "and chains with no Critical or High finding. chains.json does not carry the drops, so only their sum is checkable against a script.",
        "Closure: closure-2 and closure-3 have no flow between the two components that carry findings. The link exists only through the "
        "transitive closure.",
        "Direction: in closure-3, in some other special islands and in one plain island in three, the flow runs against the link, so the link's "
        "source component cannot reach its target and only the other way round holds. Such a chain has against_flow true. It exists only if "
        "reachability counts in either direction (orchestrator.md Phase 3.5 step 2, 'or vice versa'; ADR-050 D13, 'one component is reachable "
        "from the other'), which is how the rule stands (S-3(b), unchanged). Narrowing it to the link's direction is an R-21 change, and the "
        "chains that need it are counts.against_flow of the consolidated ones.",
        "Left out of chain formation: AG and LLM findings, and STRIDE findings on an unclassified layer. Six such findings sit on components "
        "that a flow joins to a chain's components, so a script that forgot the rule would see them.",
        "A chain's breaking target follows the orchestrator's Step 4. The V island's two arms use both tie-breaks of the 4-finding rule: "
        "the higher severity, then the earlier position.",
        "The compact rows are in the shipped format of contracts/threat-model-records.md. A row's layers and findings are in chain order.",
        "Not reached here: a finding with more than one onward link (S-3(c)'s choice among candidates, which no island needs), and a chain that "
        "is a run in the middle of another. The tests of attack-chains.py build those inline.",
        "How to run: copy run/ to a working directory and rename its tachi-build/ to .tachi-build/ (.gitignore excludes that name, so the "
        "committed copy cannot hold it). Then run attack-chains.py with --run-dir on the working directory.",
    ]
    expected = {
        "counts": {"candidates": candidates, "consolidated": consolidated, "surfaced": len(shown), "compact_rows": listed,
                   "not_listed": consolidated - len(shown) - listed, "dropped": dropped, "findings_in_section_7": len(material["findings"]),
                   "findings_in_chains": len({i for chain in chains for i in chain["members"]}),
                   "against_flow": sum(1 for chain in chains if chain["against_flow"]),
                   "components": sum(len(i["nodes"]) for i in material["islands"]), "islands": len(material["islands"])},
        "outcome_record": outcome,
        "frontmatter_counts": {"chain_count": consolidated, "surfaced_count": len(shown), "candidate_count": candidates},
        "remainder_line": "**Consolidated chains not listed**: %d" % (consolidated - len(shown) - listed),
        "chains": [cc_chain_record(chain) for chain in chains],
        "compact_rows": rows,
        "surfaced": [chain["id"] for chain in shown],
        "skipped_for_a_shared_terminal": [chain["id"] for chain in chains if not chain["surfaced"] and any(
            other["surfaced"] and other["members"][-1] == chain["members"][-1] for other in chains)],
    }
    run = {"date": PR2_RUN_DATE, "threats": "run/threats.md", "inventory": "run/tachi-build/phase1/inventory.json",
           "inventory_in_a_run_directory": ".tachi-build/phase1/inventory.json",
           "how": "copy run/ to a working directory and rename tachi-build/ to .tachi-build/; the committed copy cannot hold that name"}
    return {
        root + "run/threats.md": cc_threats_md(material),
        root + "run/tachi-build/phase1/inventory.json": cc_inventory(material),
        root + "expected-outcomes.json": pr2_expected_document(
            "chain-cap", "main", "chains", "S-4's chain-cap variant: chain material with more than 105 consolidated chains, for S-3(g)'s bound, "
            "the remainder line and FR-K4.1b's check.", run, expected, notes),
    }


# --- id-reuse, PR 2 (ruling B, ADR-050 D7, D12) -----------------------------------------------------------------------------
# A baseline and a run, taken from the gated world, for PR 2's two parts of ruling B: `tachi-stage.py id-mark` writes the per-prefix
# high-water mark (the larger of the baseline's mark and the run's highest ID, or, where the baseline has none, the baseline's highest
# live or Section 4c ID), and `check-threat-model.py` reports any NEW finding whose ID the baseline used or that sits at or below the
# baseline's mark. The baseline is a stub (its Section 4c, its Section 7 and the mark line), and the run is the world's complete
# threats.md with a few NEW findings renumbered. Two scenarios share one baseline and differ in whether it holds the mark:
#   id-reuse/pr2          the mark sits above the baseline's live IDs (above its Section 4c IDs too, for some prefixes)
#   id-reuse/pr2-no-mark  no mark at all, as every pre-PR 2 baseline: the mark is seeded from the live IDs and Section 4c
IR2_EARLIER = (  # what the baseline's own run resolved: its Section 4c, which holds IDs above the baseline's live ones
    ("S-6", "label-printer-1", "A shared batch credential for label-printer-1 is accepted from any caller that can reach its callback route, "
     "so one leaked copy authenticates as the batch job.", "Medium", "Component 'label-printer-1' removed from architecture"),
    ("T-4", "label-printer-1", "Label files that label-printer-1 renders can be replaced in storage before they print, so a shipment may "
     "carry the wrong destination.", "Low", "Component 'label-printer-1' removed from architecture"),
)
IR2_MARK = {"S": 8, "T": 6, "R": 6, "I": 5, "D": 9, "E": 3, "AG": 5, "AGP": 2, "LLM": 9, "OI": 3, "MI": 4, "TE": 2}  # the baseline's mark
IR2_MARK_NAME = "**ID high-water mark**: "


def ir2_highest(ids: Sequence) -> dict:
    """The highest number of each prefix among some IDs, in S-2's prefix order. Canonical: AGP-01 counts as AGP-1."""
    top: dict = {}
    for finding_id in ids:
        prefix, _, number = finding_id.rpartition("-")
        top[prefix] = max(top.get(prefix, 0), int(number))
    return {prefix: top[prefix] for prefix in PREFIX_ORDER if prefix in top}


def ir2_line(numbers: dict) -> str:
    return "%s`%s`" % (IR2_MARK_NAME, ", ".join("%s-%d" % (prefix, numbers[prefix]) for prefix in PREFIX_ORDER if prefix in numbers))


def ir2_run_world(remap: dict) -> dict:
    """The run: the gated world dated after its baseline, with the NEW findings in remap renumbered (old ID -> new ID)."""
    master = build_world("gated")
    findings = []
    for source in master["findings"]:
        new_id = remap.get(source["id"], source["id"])
        findings.append(dict(source, id=new_id, num=int(new_id.rpartition("-")[2])))
    findings.sort(key=lambda f: prefix_rank(f["id"]))
    by_id = {f["id"]: f for f in findings}
    groups = []
    for source in master["groups"]:
        members = [by_id[remap.get(m["id"], m["id"])] for m in source["members"]]
        ordered = (sorted((m for m in members if m["prefix"] in STRIDE_PREFIXES_ORDER), key=lambda m: prefix_rank(m["id"])) +
                   sorted((m for m in members if m["prefix"] not in STRIDE_PREFIXES_ORDER), key=lambda m: prefix_rank(m["id"])))
        for position, member in enumerate(ordered):
            member["group"], member["primary"] = source["id"], position == 0
        groups.append(dict(source, members=ordered))
    cfg = dict(master["cfg"], dates=dict(master["cfg"]["dates"], threats=PR2_RUN_DATE, baseline=PR2_BASELINE_DATE),
               run_ids={"threats": PR2_RUN_ID, "baseline": PR2_BASELINE_RUN_ID})
    return dict(master, findings=findings, groups=groups, cfg=cfg)


def ir2_baseline_rows(world: dict) -> list:
    """Section 7 of the baseline: the run's carried findings, and the ones that the run resolved, as they stood then."""
    rows = [(f["risk"], f["prefix"], f["num"], pr2_section_row(dict(f, status=STATUS_UNCHANGED), layer_label(f["layer"])))
            for f in world["findings"] if f["status"] != STATUS_NEW]
    for item in world["resolved"]:
        comp = world["by_name"].get(item["comp"])
        layer = comp["layer"] if comp else RETIRED_COMPONENTS[item["comp"]][1]
        row = {"id": item["id"], "status": STATUS_UNCHANGED, "prefix": item["prefix"], "pattern": "none", "comp": item["comp"],
               "short": item["short"], "risk": item["risk"], "mit_short": PR2_DROP_NOTE}
        rows.append((item["risk"], item["prefix"], item["num"], pr2_section_row(row, layer_label(layer))))
    rows.sort(key=lambda r: (-RISK_RANK[r[0]], TABLE_ORDER.index(r[1]), r[2]))
    return [r[3] for r in rows]


def ir2_baseline_text(world: dict, mark) -> str:
    """The baseline's threats.md, cut down to what the check and the mark's writer read. mark None: a pre-PR 2 baseline, with no mark."""
    cut = ("This file is a baseline run's threats.md, cut down to Section 4c, Section 7 and the ID high-water mark line." if mark is not None else
           "This file is a baseline run's threats.md, cut down to Section 4c and Section 7. It has no ID high-water mark line, as every "
           "baseline that an earlier release wrote.")
    out = pr2_frontmatter(PR2_BASELINE_DATE, PR2_BASELINE_RUN_ID) + ["# Threat Model Report", "", cut, ""]
    if mark is not None:
        out += [ir2_line(mark), ""]  # between the front matter and the first ## heading, outside any fence
    out += ["## 4c. Resolved Findings", "",
            "Findings from the baseline that no longer apply in the current architecture. Each keeps its original ID, description and last-known risk level.",
            "", table(("ID", "Component", "Threat", "Last Risk Level", "Resolution Reason"), IR2_EARLIER), "", "---", "",
            "## 7. Recommended Actions", "", table(PR2_ACTION_COLUMNS, ir2_baseline_rows(world))]
    return "\n".join(out)


def ir2_files(scenario: str, remap: dict, mark, summary: str, notes: Sequence) -> dict:
    world = ir2_run_world(remap)
    live = [row[0] for row in ir2_baseline_rows(world)]
    earlier = [row[0] for row in IR2_EARLIER]
    seed = ir2_highest(live + earlier)
    reference = mark if mark is not None else seed  # what a run's numbering has to clear
    run_open = [f["id"] for f in world["findings"]]
    run_highest = ir2_highest(run_open)
    result = {prefix: max(run_highest.get(prefix, 0), reference.get(prefix, 0)) for prefix in PREFIX_ORDER if prefix in run_highest or prefix in reference}
    if result != {prefix: max(ir2_highest(run_open + [r["id"] for r in world["resolved"]]).get(prefix, 0), reference.get(prefix, 0))
                  for prefix in result}:
        raise ValueError("id-reuse/%s: the run's Section 4c would move the mark, so the case would depend on how 'highest' is read" % scenario)
    judged = {}
    for finding in world["findings"]:
        if finding["status"] != STATUS_NEW:
            continue
        prefix, number = finding["id"].rpartition("-")[0], finding["num"]
        why = (["baseline-open"] if finding["id"] in live else []) + (["baseline-resolved"] if finding["id"] in earlier else [])
        below = number <= seed.get(prefix, 0)
        if mark is not None and number <= mark[prefix]:
            why.append("at-or-below-mark")
        elif mark is None and below and not why:  # an unused number under the seeded mark: whether the check flags it is not ruled
            raise ValueError("id-reuse/%s: %s sits under the seeded mark without being used, which the fixture must not decide" % (scenario, finding["id"]))
        judged[finding["id"]] = {"flagged": bool(why), "reasons": why, "mark": None if mark is None else mark[prefix],
                                 "baseline_highest_open": ir2_highest(live).get(prefix, 0), "boundary": mark is not None and number == mark[prefix]}
    flagged = [fid for fid in judged if judged[fid]["flagged"]]
    root = "id-reuse/%s/" % scenario
    run_text = render_threats_md(world).replace("baseline-runs/%s/threats.md" % PR2_BASELINE_DATE, "baseline/threats.md")
    expected = {
        "baseline": {"threats": "baseline/threats.md", "mark_present": mark is not None, "mark": mark, "mark_line": None if mark is None else ir2_line(mark),
                     "open_highest": ir2_highest(live), "resolved_highest": ir2_highest(earlier), "seed": seed,
                     "mark_above_open": [p for p in PREFIX_ORDER if mark and p in mark and mark[p] > ir2_highest(live).get(p, 0)],
                     "mark_above_seed": [p for p in PREFIX_ORDER if mark and p in mark and mark[p] > seed.get(p, 0)]},
        "reissue": {"reads": "the baseline's mark, or with none the seed from its live IDs and Section 4c", "new_findings": judged,
                    "flagged": flagged, "unflagged_new": [fid for fid in judged if fid not in flagged], "count": len(flagged), "exit_code": 5 if flagged else 0},
        "id_mark": {"reference": reference, "run_highest": run_highest, "result": result, "line": ir2_line(result),
                    "moved": [p for p in result if result[p] > reference.get(p, 0)], "kept": [p for p in result if result[p] == reference.get(p, 0)],
                    "spelling": "canonical, no leading zeros: the run's own AGP row is AGP-01 and its mark entry AGP-%d" % result["AGP"]},
    }
    run = {"date": PR2_RUN_DATE, "threats": "run/threats.md", "baseline_source": "baseline/threats.md",
           "how": "copy the scenario directory to a working directory and run from there: the front matter's baseline.source and every path "
                  "here are relative to it. id-mark takes run/threats.md as --threats and baseline/threats.md as --baseline, and writes the mark "
                  "into a copy"}
    return {root + "baseline/threats.md": ir2_baseline_text(world, mark), root + "run/threats.md": run_text,
            root + "expected-outcomes.json": pr2_expected_document("id-reuse", scenario, "id-mark+reissue-check", summary, run, expected, notes)}


def id_reuse_pr2_files() -> dict:
    common = [
        "The run is the gated world's threats.md, complete, with its NEW findings renumbered where the case needs it. Its baseline is a stub "
        "of Section 4c and Section 7, with the mark line where the baseline has one. Every carried finding in the run is in the baseline's "
        "Section 7, and so are the three findings that the run resolved.",
        "id_mark.result is what `tachi-stage.py id-mark` must write (ruling B, ADR-050 D7): per prefix, the larger of the run's highest ID and "
        "the baseline's mark, or, where the baseline has none, its highest live or Section 4c ID. The run's own Section 4c never decides a "
        "prefix here, so the case does not depend on how 'highest' is read. The line is in canonical spelling and in S-2's prefix order. "
        "(No script exists yet: the values come from the ruling's words, and T092 and T095 are the first to run a script on them.)",
        "reissue.flagged is what `check-threat-model.py` must report with the reused-id code (D12): a NEW finding whose ID the baseline used, "
        "or that sits at or below the baseline's mark. It warns and exits 5. Carried findings (UNCHANGED, UPDATED) are never flagged, whatever "
        "their numbers are.",
    ]
    with_mark = common + [
        "The mark sits above the baseline's live IDs for eight prefixes (S, T, R, I, D, AGP, LLM and MI). The numbers between belong to findings "
        "that earlier runs resolved and that no list holds any more, apart from S-6 and T-4, which Section 4c holds. It equals the highest live "
        "ID for E, AG, OI and TE.",
        "S-5 is the case that only the mark catches: no baseline list holds S-5, and it sits above the baseline's live IDs, but the mark is S-8. "
        "T-4 is a NEW finding with a number that the baseline's Section 4c holds, so it is reused twice over. I-5 equals the mark exactly, and "
        "'at or below' includes it.",
        "AG-6 is the control: it numbers just above a mark that equals the highest live ID. LLM-10 numbers above the mark and skips LLM-7 to "
        "LLM-9, which is what PR 2's item 1 says ('numbering can skip'). Neither is flagged.",
        "The mark does not move down: for eight prefixes the run's highest ID is below the baseline's mark, and the result keeps the mark. It "
        "moves for AG and LLM only.",
    ]
    no_mark = common + [
        "The baseline has no mark line, as every pre-PR 2 baseline. The seed is each prefix's highest live or Section 4c ID: S-6 and T-4 come "
        "from Section 4c, and a seed from the live IDs alone would be S-4 and T-3.",
        "S-6 is a NEW finding whose number only Section 4c holds: flagged as used by the baseline. T-5 numbers just above the seeded T-4, "
        "and I-5, AG-6 and LLM-7 just above their seeds: none is flagged.",
        "The case holds no NEW finding that sits under a seed without being used by the baseline (the generator refuses to build one), "
        "because whether the check reads a seeded mark as a mark is not ruled. ADR-050 D7's limit stays: an ID resolved before the baseline run, "
        "which the baseline no longer lists, can still be reissued once, and nothing here can show it.",
    ]
    files = ir2_files("pr2", {"LLM-7": "LLM-10"}, IR2_MARK,
                      "S-4's id-reuse variant for PR 2: a baseline whose high-water mark sits above its live IDs (ruling B).", with_mark)
    files.update(ir2_files("pr2-no-mark", {"S-5": "S-6", "T-4": "T-5"}, None,
                           "S-4's id-reuse variant for PR 2, first run: a baseline with no mark at all, seeded from its live IDs and Section 4c (PM-T7).",
                           no_mark))
    return files


def part_id_reuse_pr1_pr2(rng: Rng) -> dict:
    """T040's PR 1 case and T148's PR 2 cases, both under id-reuse/ (a part writes only under its own name)."""
    files = part_id_reuse(rng)
    files.update(id_reuse_pr2_files())
    return files


# --------------------------------------------------------------------------- T103: PR 2's run directories (pr2-runs/)
# Six scenarios for the two checks and the two assemblers (spec S-4; ADR-050 D11 to D14). Each is a directory of the committed copy, under
# pr2-runs/, that holds run/ (the {out} directory of a threat-model run), baseline/ where the run has a baseline, and expected-outcomes.json
# (tachi.fixture-expected/1). A run's .tachi-build/ is written as tachi-build/, because .gitignore excludes the dotted name. Every name and
# every finding is invented, and every record, brief, plan, batch input and part follows the contracts' closed key sets: the tests read them
# back through the shipped validators.
#   forms             a baseline run in which the findings take every provenance form (FR-N4.5): a dispatch record that keeps the ID, one that
#                     renumbers it, one whose agent folds into another prefix (OI and MI into LLM, TE into AG: #356's table), a baseline
#                     carry-forward, a Phase 3.6 pattern finding, and the dispositions that match a carried finding or merge into one
#   truncation        a run with no baseline in which two planned dispatches are cut short and re-dispatched: a split into one record for each
#                     component, then a repeat for two of the pieces, with each of the four reasons a record can carry (FR-N4.7, item O-alpha)
#   reissue-mark      T148's id-reuse/pr2 run (its threats.md, byte for byte) with the records that make its provenance whole, so that the
#                     check meets ruling B's reissued IDs alone
#   reissue-no-mark   the same for id-reuse/pr2-no-mark, the first PR 2 run on a baseline with no mark (PM-T7)
#   trees             the forms run's trees stage, as the planner and the agents leave it before assemble-report.py trees runs: the plan, two
#                     batch inputs and parts, every generated tree, and the baseline's trees (Rule 2, with Rule 3's decisions in the parts)
#   report            the same run after that assembly (its attack-trees/ and manifest) and its report stage: the plan, eight batch inputs and
#                     parts, one narrative that breaks the numeral ban and one that is cut at its limit
# Everything with an absolute path in it (a record's brief and prompt, a brief's inputs, a plan, a batch input) is built for a root. The
# committed copy uses PR2R_ROOT, a path that exists nowhere, and materialize() builds a scenario for a real directory, so that the digests
# that bind the plan, its inputs and its parts hold there too. Names here start pr2r_ or PR2R_.
PR2R_ROOT = "/synthetic-case"
PR2R_VERSION = "4.48.5"
PR2R_IDS = {"trees": "20261123T101500Z-7a1c3e5d9b02", "report": "20261123T103000Z-4e8f2a6c1d07"}
PR2R_CREATED = {"trees": "2026-11-23T10:15:00Z", "report": "2026-11-23T10:30:00Z"}
PR2R_STAGE_AGENT = {"trees": "tachi-attack-tree-delta", "report": "tachi-threat-report"}
PR2R_TREES_BATCH = 12  # the trees stage's batch size (S1P-A57)
PR2R_SCENARIOS = ("forms", "truncation", "reissue-mark", "reissue-no-mark", "trees", "report")
PR2R_BASELINE_TREE_NOTE = "Carried from the baseline run."  # the line that tells a baseline's tree from a fresh one

# The Phase 2 roster (.claude/skills/tachi-shared/references/agent-roster-shared.md), in its order: the agent, its dispatch key, the prefix its own
# findings carry and the prefix Phase 3 files them under today. A fold is a row whose last two cells differ.
PR2R_ROSTER = (
    ("tachi-spoofing", "S", "S", "S"), ("tachi-tampering", "T", "T", "T"), ("tachi-repudiation", "R", "R", "R"),
    ("tachi-info-disclosure", "I", "I", "I"), ("tachi-denial-of-service", "D", "D", "D"),
    ("tachi-privilege-escalation", "E", "E", "E"), ("tachi-agent-autonomy", "AG", "AG", "AG"), ("tachi-tool-abuse", "AG", "AG", "AG"),
    ("tachi-human-trust-exploitation", "AG", "TE", "AG"), ("tachi-prompt-injection", "LLM", "LLM", "LLM"),
    ("tachi-data-poisoning", "LLM", "LLM", "LLM"), ("tachi-model-theft", "LLM", "LLM", "LLM"),
    ("tachi-output-integrity", "LLM", "OI", "LLM"), ("tachi-misinformation", "LLM", "MI", "LLM"),
)
PR2R_EMITS = {row[0]: row[2] for row in PR2R_ROSTER}
PR2R_FILES_UNDER = {row[0]: row[3] for row in PR2R_ROSTER}
PR2R_AGENT_OF_STRIDE = {row[1]: row[0] for row in PR2R_ROSTER[:6]}
PR2R_AGENT_OF_SUB = {"AG:autonomy": "tachi-agent-autonomy", "AG:tool": "tachi-tool-abuse", "TE": "tachi-human-trust-exploitation",
                     "LLM:inject": "tachi-prompt-injection", "LLM:poison": "tachi-data-poisoning", "LLM:theft": "tachi-model-theft",
                     "OI": "tachi-output-integrity", "MI": "tachi-misinformation"}
PR2R_CATEGORY_KEY = {"S": "spoofing", "T": "tampering", "R": "repudiation", "I": "information_disclosure", "D": "denial_of_service",
                     "E": "elevation_of_privilege", "AG": "agentic", "AGP": "agentic", "TE": "agentic", "LLM": "llm", "OI": "llm", "MI": "llm"}
PR2R_CATEGORY_KEYS = ("spoofing", "tampering", "repudiation", "information_disclosure", "denial_of_service", "elevation_of_privilege",
                      "agentic", "llm")
PR2R_PATTERNS = ("agent_collusion", "emergent_behavior", "temporal_attack", "trust_exploitation", "communication_vulnerability",
                 "resource_competition")
# What each scenario does to the gated world. forms: three findings of the folding agents become NEW findings that Phase 3 files under another
# prefix, and the pattern finding is NEW (the world has them all carried). Matched and merged dispositions name an ID and the symbol that Phase 3's
# ID map gives it: = matched exactly, ~ matched by similarity, > merged into. The agent that returned the duplicate is the one that owns the target.
PR2R_FORMS_RELABEL = (("OI-3", "LLM"), ("MI-2", "LLM"), ("TE-2", "AG"))
PR2R_FORMS_EXTRAS = (("S-1", "="), ("T-2", "~"), ("AG-3", "~"), ("LLM-6", "="), ("T-4", ">"), ("E-2", ">"),
                     ("I-1", "="), ("I-3", "="), ("I-4", "="), ("I-4", ">"))  # the last four put the one new I finding at its own number: kept as is
PR2R_TRUNCATION_EXTRAS = (("T-3", ">"), ("S-2", ">"))
# A planned dispatch that was cut short: (agent, why, findings it had listed, {component of a replacement: (why, findings listed)} for the
# replacements that were cut short too). The agent's planned dispatch is split into one replacement for each component of its scope, and a
# replacement that is cut short is repeated once (item O-alpha, "Lineage").
PR2R_TRUNCATIONS = (
    ("tachi-agent-autonomy", "no_end_marker", 2, {"planner-agent": ("timed_out", 0)}),
    ("tachi-human-trust-exploitation", "agent_failed", 0, {"worker-2": ("overflow_error", 1)}),
)
# What an earlier run resolved, for the forms baseline's Section 4c: IDs above the baseline's live ones, under prefixes the forms run issues no NEW
# finding for, so that no ID of the run is reissued.
PR2R_EARLIER = (
    ("D-6", "legacy-batch-1", "A nightly export route on legacy-batch-1 accepted requests with no check on the caller.", "Medium",
     "Component 'legacy-batch-1' removed from architecture"),
    ("E-5", "report-export-2", "A shared export account on report-export-2 could approve its own report requests.", "Low",
     "Component 'report-export-2' removed from architecture"),
)
_PR2R_CACHE: dict = {}


def pr2r_sha(text: str) -> str:
    """The SHA-256 of a file as the generator writes it, which is what every digest in a plan binds."""
    return hashlib.sha256(_canonical_text(text)).hexdigest()


def pr2r_agent_of(finding: dict) -> str:
    return PR2R_AGENT_OF_SUB[finding["sub"]] if finding["sub"] else PR2R_AGENT_OF_STRIDE[finding["prefix"]]


def pr2r_origin(finding: dict) -> str:
    """Where FR-N4.5 finds a final finding's provenance: a dispatch record (class 1), a baseline carry-forward (class 2) or a named rule (class 3)."""
    if finding["status"] != STATUS_NEW:
        return "carried"
    return "rule" if finding["prefix"] == "AGP" else "record"


def pr2r_rebuild(world: dict, changes: dict) -> dict:
    """A copy of a world whose findings are re-made: changes maps an old ID to the keys that differ (prefix, num, status). Groups follow, as in D8."""
    mapping, findings = {}, []
    for source in world["findings"]:
        finding = dict(source, **changes.get(source["id"], {}))
        finding["id"] = finding_id_text(finding["prefix"], finding["num"])
        mapping[source["id"]] = finding["id"]
        findings.append(finding)
    findings.sort(key=lambda f: prefix_rank(f["id"]))
    by_id = {f["id"]: f for f in findings}
    groups = []
    for source in world["groups"]:
        members = [by_id[mapping[m["id"]]] for m in source["members"]]
        ordered = (sorted((m for m in members if m["prefix"] in STRIDE_PREFIXES_ORDER), key=lambda m: prefix_rank(m["id"])) +
                   sorted((m for m in members if m["prefix"] not in STRIDE_PREFIXES_ORDER), key=lambda m: prefix_rank(m["id"])))
        for position, member in enumerate(ordered):
            member["group"], member["primary"] = source["id"], position == 0
        groups.append(dict(source, members=ordered))
    return clone_world(world, findings=findings, groups=groups)


def pr2r_dated(world: dict) -> dict:
    """The gated world as a run of 2026-11-23 over a baseline of 2026-11-09, whose threats.md names baseline/threats.md as its source."""
    cfg = dict(world["cfg"], dates=dict(world["cfg"]["dates"], threats=PR2_RUN_DATE, baseline=PR2_BASELINE_DATE),
               run_ids={"threats": PR2_RUN_ID, "baseline": PR2_BASELINE_RUN_ID}, baseline_source="baseline/threats.md")
    return clone_world(world, cfg=cfg)


def pr2r_forms_world() -> dict:
    master = pr2r_dated(build_world("gated"))
    top: dict = {}
    for finding in master["findings"]:
        top[finding["prefix"]] = max(top.get(finding["prefix"], 0), finding["num"])
    changes = {"AGP-01": {"status": STATUS_NEW}}
    for old_id, prefix in PR2R_FORMS_RELABEL:
        top[prefix] += 1
        changes[old_id] = {"prefix": prefix, "num": top[prefix], "status": STATUS_NEW}
    return pr2r_rebuild(master, changes)


def pr2r_stateless_world() -> dict:
    """The same findings in a first run: all NEW, numbered from 1 for each prefix, the folded three last under the prefix Phase 3 files them in."""
    master = pr2r_dated(build_world("gated"))
    moved = dict(PR2R_FORMS_RELABEL)
    order: dict = {}
    for finding in master["findings"]:
        if finding["id"] not in moved:
            order.setdefault(finding["prefix"], []).append(finding["id"])
    for old_id, prefix in PR2R_FORMS_RELABEL:
        order.setdefault(prefix, []).append(old_id)
    changes = {old_id: {"prefix": prefix, "num": number, "status": STATUS_NEW}
               for prefix, ids in order.items() for number, old_id in enumerate(ids, start=1)}
    return clone_world(pr2r_rebuild(master, changes), resolved=[])


def pr2r_stateless_text(world: dict) -> str:
    """threats.md of a run with no baseline, the form a first run leaves: the front matter says so and Sections 4c and 8 are not there. The rest is
    render_threats_md's own text, cut at the headings."""
    text = render_threats_md(world)
    _, marker, rest = text.partition("\n# Threat Model Report")
    start, stop = rest.index("## 4c. Resolved Findings"), rest.index("## 5. Coverage Matrix")
    rest = rest[:start] + rest[stop:]
    start, stop = rest.index("## 8. Delta Summary"), rest.index("## Affected Assets")
    return "\n".join(pr2_frontmatter(PR2_RUN_DATE, PR2_RUN_ID)) + marker + rest[:start] + rest[stop:]


def pr2r_baseline_text(world: dict) -> str:
    """The forms baseline's threats.md, cut down to Section 4c and Section 7: no mark line, as every baseline that an earlier release wrote."""
    out = pr2_frontmatter(PR2_BASELINE_DATE, PR2_BASELINE_RUN_ID) + [
        "# Threat Model Report", "",
        "This file is a baseline run's threats.md, cut down to Section 4c and Section 7. It has no ID high-water mark line, as every baseline "
        "that an earlier release wrote.", "",
        "## 4c. Resolved Findings", "",
        "Findings from the baseline that no longer apply in the current architecture. Each keeps its original ID, description and last-known risk level.",
        "", table(("ID", "Component", "Threat", "Last Risk Level", "Resolution Reason"), PR2R_EARLIER), "", "---", "",
        "## 7. Recommended Actions", "", table(PR2_ACTION_COLUMNS, ir2_baseline_rows(world))]
    return "\n".join(out)


def pr2r_dispatch_row(comp: dict) -> dict:
    """One row of phase1/dispatch.json: the STRIDE letters that apply to the component, and AG and LLM where a sub-agent of theirs does."""
    ai = []
    if any(code.startswith("AG:") or code == "TE" for code in comp["ai"]):
        ai.append("AG")
    if any(code.startswith("LLM:") or code in ("OI", "MI") for code in comp["ai"]):
        ai.append("LLM")
    return {"component": comp["name"], "stride": [p for p in STRIDE_PREFIXES_ORDER if _stride_eligible(p, comp)], "ai": ai}


def pr2r_planned(world: dict) -> list:
    """The planned set (item O-alpha): one dispatch for each roster agent with a component in scope, a pure function of the dispatch table."""
    rows = [pr2r_dispatch_row(comp) for comp in world["components"]]
    planned = []
    for agent, key, _, _ in PR2R_ROSTER:
        scope = [row["component"] for row in rows if key in row["stride"] or key in row["ai"]]
        if scope:
            planned.append({"agent": agent, "scope": scope})
    return planned


def pr2r_inventory_text(world: dict) -> str:
    return dumps({
        "schema": "tachi.phase1-inventory/1",
        "components": [{"name": c["name"], "dfd_type": c["dfd"], "maestro_layer": "L%d" % c["layer"], "description": c["desc"]} for c in world["components"]],
        "data_flows": [{"source": s, "destination": d, "data": data, "protocol": proto} for s, d, data, proto in world["flows"]],
        "trust_zones": [{"name": z["name"], "components": list(z["members"])} for z in world["zones"]]})


def pr2r_dispatches(world: dict, truncations: Sequence = ()) -> list:
    """Every dispatch of the run, in ID order: the planned ones, then each cut-short dispatch's replacements, then the repeats (item O-alpha, "IDs"
    and "Lineage"). Each is {id, agent, origin, scope, status, reason, supersedes, superseded_by, attempt, partial}; partial is how many findings
    a cut-short report listed before it stopped."""
    records = []
    for number, item in enumerate(pr2r_planned(world), start=1):
        records.append({"id": "dsp-%03d" % number, "agent": item["agent"], "origin": "planned", "scope": item["scope"], "status": "complete",
                        "reason": None, "supersedes": None, "superseded_by": [], "attempt": 1, "partial": 0})
    by_agent = {record["agent"]: record for record in records}
    follow, issued = [], len(records)
    for agent, reason, partial, again in truncations:
        parent = by_agent[agent]
        parent.update(status="superseded", reason=reason, partial=partial)
        for component in parent["scope"]:
            issued += 1
            child = {"id": "dsp-%03d" % issued, "agent": agent, "origin": "redispatch", "scope": [component], "status": "complete", "reason": None,
                     "supersedes": parent["id"], "superseded_by": [], "attempt": 2, "partial": 0}
            parent["superseded_by"].append(child["id"])
            records.append(child)
            follow.append((child, again.get(component)))
    for child, ending in follow:
        if ending is None:
            continue
        issued += 1
        repeat = {"id": "dsp-%03d" % issued, "agent": child["agent"], "origin": "redispatch", "scope": list(child["scope"]), "status": "complete",
                  "reason": None, "supersedes": child["id"], "superseded_by": [], "attempt": 3, "partial": 0}
        child.update(status="superseded", reason=ending[0], partial=ending[1], superseded_by=[repeat["id"]])
        records.append(repeat)
    return records


def pr2r_returns(world: dict, dispatches: list, extras: Sequence) -> dict:
    """What each live record's agent listed, as {dispatch ID: [(target ID, kind)]}: kind is kept, =, ~ or >. A finding goes to the one live record of
    its agent whose scope holds its component (the lineage rule makes that one), and a record lists its findings component by component."""
    by_id = {f["id"]: f for f in world["findings"]}
    wanted = [(f["id"], "kept") for f in world["findings"] if pr2r_origin(f) == "record"] + list(extras)
    out = {d["id"]: [] for d in dispatches if d["status"] == "complete"}
    for target, kind in wanted:
        finding = by_id[target]
        homes = [d for d in dispatches if d["status"] == "complete" and d["agent"] == pr2r_agent_of(finding) and finding["comp"] in d["scope"]]
        if len(homes) != 1:
            raise ValueError("%s has %d live records of its agent that cover %s" % (target, len(homes), finding["comp"]))
        out[homes[0]["id"]].append((target, kind))
    listed_first = {"kept": 0, "=": 1, "~": 2, ">": 3}  # on one finding, the surviving one comes before the duplicate that merges into it
    for d in dispatches:
        if d["id"] in out:
            out[d["id"]].sort(key=lambda item: (d["scope"].index(by_id[item[0]]["comp"]), prefix_rank(item[0]), listed_first[item[1]]))
    return out


def pr2r_disposition(item: tuple) -> str:
    target, kind = item
    return target if kind == "kept" else kind + target


def pr2r_local_ids(agent: str, count: int) -> list:
    """An agent's own provisional IDs for one report: its prefix and a running number from 1, whatever the final IDs are."""
    return ["%s-%d" % (PR2R_EMITS[agent], n) for n in range(1, count + 1)]


def pr2r_provenance(world: dict, dispatches: list, returns: dict) -> dict:
    """FR-N4.5's entry for every open finding and FR-N4.6's, worked out from the declaration: the class, and for a dispatch record the record, the local
    ID, the disposition and its form (kept, renumbered or folded). Also the ID map's matched and merged entries, and the check's counts."""
    kept, side = {}, []
    for d in dispatches:
        if d["id"] not in returns:
            continue
        for local, item in zip(pr2r_local_ids(d["agent"], len(returns[d["id"]])), returns[d["id"]]):
            if item[1] == "kept":
                kept[item[0]] = (d["id"], d["agent"], local)
            else:
                side.append({"record": d["id"], "agent": d["agent"], "local_id": local, "disposition": pr2r_disposition(item), "kind": item[1],
                             "target": item[0]})
    findings, counts = {}, {"recorded": 0, "carried": 0, "rule": 0, "renumbered": 0, "folded": 0}
    for f in world["findings"]:
        origin = pr2r_origin(f)
        entry = {"class": {"record": 1, "carried": 2, "rule": 3}[origin], "origin": origin, "status": f["status"], "record": None, "agent": None,
                 "local_id": None, "form": None}
        if origin == "record":
            record, agent, local = kept[f["id"]]
            if local == f["id"]:
                form = "kept"
            elif PR2R_EMITS[agent] != f["prefix"] and PR2R_FILES_UNDER[agent] == f["prefix"]:
                form = "folded"
            elif local.rpartition("-")[0] == f["prefix"]:
                form = "renumbered"
            else:
                raise ValueError("%s is kept by %s, which is not allowed that prefix" % (f["id"], agent))
            entry.update(record=record, agent=agent, local_id=local, form=form)
            counts["recorded"] += 1
            if form != "kept":
                counts[form] += 1
        else:
            counts["carried" if origin == "carried" else "rule"] += 1
        findings[f["id"]] = entry
    return {"findings": findings, "side": side, "counts": counts}


def pr2r_batches_summary(dispatches: list) -> dict:
    """Phase 2's six counts as the check's hand-off carries them (threat-model-records.md, "The stage record"): coverage-gap records are not counted."""
    lineage = [d for d in dispatches if d["origin"] != "coverage-gap"]
    planned = sum(1 for d in lineage if d["origin"] == "planned")
    retried = sum(1 for d in lineage if d["origin"] == "redispatch")
    return {"planned": planned, "dispatched": planned + retried, "done": sum(1 for d in lineage if d["status"] == "complete"), "retried": retried,
            "split": sum(1 for d in lineage if d["status"] == "superseded"), "exhausted": sum(1 for d in lineage if d["status"] == "unrecovered")}


PR2R_REISSUE = {"reissue-mark": ("pr2", {"LLM-7": "LLM-10"}), "reissue-no-mark": ("pr2-no-mark", {"S-5": "S-6", "T-4": "T-5"})}  # T148's scenarios and remaps
PR2R_KEY_ORDER = ("S", "T", "R", "I", "D", "E", "AG", "LLM")  # a dispatch key, in the order the contracts list them


def pr2r_case(name: str) -> dict:
    """The part of a provenance scenario that names no root: its world, its texts and the dispatches with what each returned. Pure, and cached."""
    cached = _PR2R_CACHE.get(name)
    if cached is not None:
        return cached
    if name == "forms":
        world, extras, truncations = pr2r_forms_world(), PR2R_FORMS_EXTRAS, ()
        threats, baseline = render_threats_md(world), pr2r_baseline_text(world)
    elif name == "truncation":
        world, extras, truncations = pr2r_stateless_world(), PR2R_TRUNCATION_EXTRAS, PR2R_TRUNCATIONS
        threats, baseline = pr2r_stateless_text(world), None
    elif name in PR2R_REISSUE:  # T148's runs: the same threats.md and baseline, byte for byte, so that "S-4's PR 2 case" is the case itself
        scenario, remap = PR2R_REISSUE[name]
        files = id_reuse_pr2_files()
        world, extras, truncations = ir2_run_world(remap), (), ()
        threats, baseline = files["id-reuse/%s/run/threats.md" % scenario], files["id-reuse/%s/baseline/threats.md" % scenario]
    else:
        raise ValueError("not a provenance scenario: %r" % name)
    dispatches = pr2r_dispatches(world, truncations)
    returns = pr2r_returns(world, dispatches, extras)
    case = {"name": name, "world": world, "stateless": baseline is None, "threats": threats, "baseline": baseline, "extras": extras,
            "dispatches": dispatches, "returns": returns, "provenance": pr2r_provenance(world, dispatches, returns)}
    _PR2R_CACHE[name] = case
    return case


def pr2r_reissued(case: dict) -> list:
    """The NEW findings that ruling B's check flags in the two reissue scenarios (ADR-050 D7): an ID that the baseline's Section 7 or 4c holds, or
    that sits at or below the baseline's mark. T148's expected-outcomes.json holds the same list, and a test compares the two."""
    if case["name"] not in PR2R_REISSUE:
        return []
    mark = IR2_MARK if case["name"] == "reissue-mark" else None
    used = [row[0] for row in ir2_baseline_rows(case["world"])] + [row[0] for row in IR2_EARLIER]
    return [f["id"] for f in case["world"]["findings"]
            if f["status"] == STATUS_NEW and (f["id"] in used or (mark is not None and f["num"] <= mark[f["prefix"]]))]


def pr2r_provenance_files(name: str, root: str) -> dict:
    """The files of one provenance scenario for a root, relative to its directory: run/ (threats.md, the architecture snapshot, tachi-build/ with the
    Phase 1 tables, one brief and one record for each dispatch, and the ID map) and baseline/, where the run has one."""
    case = pr2r_case(name)
    world, dispatches, returns = case["world"], case["dispatches"], case["returns"]
    out = root + "/run"
    build = out + "/.tachi-build"
    covered: dict = {}
    for f in world["findings"]:
        if f["status"] != STATUS_NEW:  # what the baseline already covers: every open finding that the run carries
            key = f["prefix"] if f["prefix"] in STRIDE_PREFIXES_ORDER else ("AG" if PREFIX_CATEGORY[f["prefix"]] == "agentic" else "LLM")
            covered.setdefault(f["comp"], set()).add(key)
    files = {"run/threats.md": case["threats"], "run/architecture.md": architecture_text(world),
             "run/tachi-build/phase1/inventory.json": pr2r_inventory_text(world),
             "run/tachi-build/phase1/dispatch.json": dumps({"schema": "tachi.phase1-dispatch/1",
                                                            "rows": [pr2r_dispatch_row(c) for c in world["components"]]})}
    if case["baseline"] is not None:
        files["baseline/threats.md"] = case["baseline"]
    if name == "forms":  # the baseline's trees too, the trees scenario's files: a live trees plan on this run then meets Rule 3 units
        by_id = {f["id"]: f for f in world["findings"]}
        for finding_id in pr2r_trees_material(world)["with_tree"]:
            files["baseline/attack-trees/%s-attack-tree.md" % finding_id.lower()] = pr2r_tree_file(world, by_id[finding_id], True)
    idmap = {}
    for d in dispatches:
        brief, live = build + "/briefs/%s.json" % d["id"], d["status"] == "complete"
        items = returns.get(d["id"], [])
        count = len(items) if live else d["partial"]
        files["run/tachi-build/records/%s.json" % d["id"]] = dumps({
            "schema": "tachi.dispatch-record/1", "dispatch_id": d["id"], "agent_type": d["agent"], "origin": d["origin"],
            "scope": {"components": d["scope"]}, "brief": brief, "prompt": "Read and follow the brief at %s." % brief, "end_marker": live,
            "status": d["status"], "supersedes": d["supersedes"], "superseded_by": d["superseded_by"], "reason": d["reason"], "count": count,
            "local_ids": pr2r_local_ids(d["agent"], count)})
        files["run/tachi-build/briefs/%s.json" % d["id"]] = dumps({
            "schema": "tachi.brief/1", "dispatch_id": d["id"], "agent_type": d["agent"], "targets": d["scope"],
            "inputs": {"architecture": out + "/architecture.md", "inventory": build + "/phase1/inventory.json",
                       "dispatch_table": build + "/phase1/dispatch.json"},
            "baseline_focus": None if case["stateless"] else [
                {"component": c, "covered": [k for k in PR2R_KEY_ORDER if k in covered.get(c, ())]} for c in d["scope"]]})
        if live:
            idmap[d["id"]] = [pr2r_disposition(item) for item in items]
    files["run/tachi-build/idmap.json"] = dumps({"schema": "tachi.idmap/1", "records": idmap})
    files["expected-outcomes.json"] = pr2r_provenance_expected(case)
    return files


def pr2r_case_notes(case: dict) -> list:
    """What is particular to one provenance scenario, in words. Worked out from the declaration, so that a note can't name a record or an ID that
    the scenario does not hold."""
    name, dispatches, prov, world = case["name"], case["dispatches"], case["provenance"], case["world"]
    if name == "forms":
        by_form: dict = {}
        for finding_id, entry in prov["findings"].items():
            if entry["form"]:
                by_form.setdefault(entry["form"], []).append(finding_id)
        by_kind: dict = {}
        for item in prov["side"]:
            by_kind.setdefault(item["kind"], []).append(item["target"])
        carried = {f["id"] for f in world["findings"] if f["status"] != STATUS_NEW}
        fold_text = "; ".join("%s, kept by %s as its local %s%s" % (
            f, prov["findings"][f]["agent"], prov["findings"][f]["local_id"],
            " (also a carried finding's final ID)" if prov["findings"][f]["local_id"] in carried else "") for f in by_form["folded"])
        rule = [f for f, entry in prov["findings"].items() if entry["class"] == 3]
        empty = next(d["id"] for d in dispatches if not case["returns"][d["id"]])
        new = next(f for f, entry in prov["findings"].items() if entry["class"] == 1 and entry["form"] == "renumbered")
        home = prov["findings"][new]["record"]
        recipes = (
            "Edits that make the negative cases of D12's list, each one change to a materialized copy of this run. No records at all: remove "
            "tachi-build/records/ and briefs/. A planned agent with no record: remove %s's record and brief (it lists nothing, so the ID map loses "
            "only an empty list). A finding with two entries: add %s to the ID map under %s, and a local ID and count to that record. An orphan "
            "finding: remove %s from the ID map under %s, and its local ID and one from the count. An extra key in a brief, or a prompt that "
            "differs: edit the brief or the record. A Section 6 that disagrees: change one count in threats.md's risk-level table. The truncation "
            "scenario's last repeat, set to unrecovered, ends a lineage." % (empty, new, empty, new, home))
        return [
            "Forms in this run. Kept as its agent numbered it: %s. Renumbered, a local number that differs from the final one: %s. Folded, where Phase "
            "3 files an agent's own prefix under another (#356's table): %s. NEW with no disposition that names it, Phase 3.6's rule: %s. Every other "
            "finding is carried, UNCHANGED or UPDATED and in the baseline." % (
                ", ".join(by_form["kept"]), ", ".join(by_form["renumbered"]), fold_text, ", ".join(rule)),
            "Dispositions that are not kept ones. Matched exactly: %s. Matched by similarity: %s. Merged into: %s. Such a disposition gives no finding "
            "a provenance of its own, and a matched target must be a carried finding." % (
                ", ".join(by_kind["="]), ", ".join(by_kind["~"]), ", ".join(by_kind[">"])),
            "baseline_focus: every brief lists each target component with the categories that the baseline's carried findings cover. No mark line "
            "is in the baseline, and no NEW ID is at or under what a seed from its live IDs and Section 4c would give, so the run has no reissued ID.",
            "baseline/ also holds the baseline's attack-trees/, the same files as the trees scenario's, so that this one run can start a whole offline "
            "pass: the check on these records, then a live trees plan and a report plan (the trees and report scenarios are that pass's later states, "
            "built for a fixed plan ID).",
            recipes,
        ]
    if name == "truncation":
        parts = []
        for d in (d for d in dispatches if d["status"] == "superseded"):
            listed = "after %d finding%s" % (d["partial"], "" if d["partial"] == 1 else "s") if d["partial"] else "with no report"
            kind = "planned dispatch" if d["attempt"] == 1 else "replacement for %s" % d["scope"][0]
            into = ("split into %s to %s" % (d["superseded_by"][0], d["superseded_by"][-1])) if len(d["superseded_by"]) > 1 else (
                "repeated by %s" % d["superseded_by"][0])
            parts.append("%s (%s's %s) ended %s, with reason %s, and is %s" % (d["id"], d["agent"], kind, listed, d["reason"], into))
        counts = pr2r_batches_summary(dispatches)
        return [
            "The run has no baseline, so every finding is NEW and every brief's baseline_focus is null (a stateless run). threats.md has no "
            "Section 4c or 8 and its front matter has no baseline.",
            "Two lineages. A planned dispatch is split into one replacement for each component of its scope, and a replacement that ends early is "
            "repeated once: " + "; ".join(parts) + ". A superseded record's findings are not in the ID map, and no other record names them.",
            "Phase 2's counts: %(planned)d planned, %(retried)d retried (a split of k components counts k, a repeat one), %(dispatched)d dispatched, "
            "%(done)d done, %(split)d split and %(exhausted)d exhausted." % counts,
        ]
    return [
        "The threats.md and the baseline are T148's id-reuse/%s files, byte for byte (a test compares them). The records add what a run needs for the "
        "check to reach ruling B's reissue check: each NEW finding is kept by the one record of its agent, and every carried finding is carried." %
        PR2R_REISSUE[name][0],
        "provenance.check.reissued is T148's reissue.flagged: the NEW findings whose ID the baseline used or that sit at or below its mark. The "
        "check reports them with the code id:reissued and exits 5; nothing else in this run warns or fails.",
    ]


def pr2r_provenance_expected(case: dict) -> str:
    world, dispatches, prov, name = case["world"], case["dispatches"], case["provenance"], case["name"]
    flagged = pr2r_reissued(case)
    counts = dict(prov["counts"], open=len(world["findings"]), resolved=len(world["resolved"]))
    counts["reused-id"] = len(flagged)
    counts = {key: counts[key] for key in ("open", "resolved", "recorded", "carried", "rule", "renumbered", "folded", "reused-id")}
    planned = [d for d in dispatches if d["origin"] == "planned"]
    stateless = case["stateless"]
    summary = {
        "forms": "S-4's PR 2 provenance case on a baseline: every form that FR-N4.5 and FR-N4.6 meet, over 14 planned dispatches that all return.",
        "truncation": "S-4's PR 2 truncation case in a stateless run: two planned dispatches cut short and re-dispatched, with all four reasons.",
        "reissue-mark": "S-4's id-reuse/pr2 run, with the records that make its provenance whole: ruling B's reissued IDs, against a baseline mark.",
        "reissue-no-mark": "S-4's id-reuse/pr2-no-mark run, with its records: the first PR 2 run on a baseline with no mark (PM-T7).",
    }[name]
    notes = [
        "This is a provenance scenario for check-threat-model.py (D12) and the Phase 2 half of the run-level record. run/ is the {out} directory: "
        "threats.md, the architecture snapshot, and tachi-build/ (named .tachi-build/ in a working directory, which .gitignore excludes here). "
        "Every absolute path in a record and a brief names the root %s, which materialize() replaces with a real directory. The files hold exactly "
        "what the contracts' key sets allow, and test_fixture_374.py reads each one back through the shipped validators." % PR2R_ROOT,
        "The planned set follows from phase1/dispatch.json and the roster alone: %d dispatches, one for each agent with a component in scope, in the "
        "roster's order (dsp-001 to dsp-%03d). A planned record's scope is that agent's components, in the inventory's order." % (len(planned), len(planned)),
        "Every finding's provenance is in provenance.findings: class 1 (a dispatch record keeps it), 2 (a baseline carry-forward) or 3 (Phase 3.6's "
        "rule). A record's local IDs are its agent's own: its emitted prefix and a number from 1 in its report's order, so they can equal another "
        "finding's final ID. The ID map holds one disposition for each local ID, in order. These values are worked out here from the contracts and "
        "are not read from any script: no check script exists yet, and T095 and T096 are the first to run one on them.",
        "run/ holds no run-level plan, no hand-off and no sections.json: tachi-stage.py plan --stage threat-model writes the plan, the check writes its "
        "hand-off under that plan's checks/ directory, and a test that needs the manifest or the threats-md parts builds them itself. Section 6 and the "
        "other tables of threats.md are the generator's (render_threats_md), as in every other scenario.",
    ]
    notes += pr2r_case_notes(case)
    doc = {
        "schema": "tachi.fixture-expected/1", "variant": "pr2-runs", "scenario": name, "stage": "provenance-check", "summary": summary,
        "run": {"date": PR2_RUN_DATE, "threats": "run/threats.md", "baseline": None if stateless else "baseline/threats.md",
                "architecture": "run/architecture.md", "tachi_build": "run/tachi-build",
                "how": "gen.materialize(scenario, directory) writes run/ and baseline/ for that directory, with tachi-build/ renamed .tachi-build/ and "
                       "every absolute path rewritten, then check-threat-model.py --run-dir <directory>/run --plan <plan> and --baseline "
                       "<directory>/baseline/threats.md, or --no-baseline for a run with no baseline"},
        "notes": notes,
        "provenance": {
            "stateless": stateless,
            "open_ids": [f["id"] for f in world["findings"]], "resolved_ids": [r["id"] for r in world["resolved"]],
            "planned": [{"dispatch_id": d["id"], "agent_type": d["agent"], "scope": d["scope"]} for d in planned],
            "records": [{"dispatch_id": d["id"], "agent_type": d["agent"], "origin": d["origin"], "status": d["status"], "reason": d["reason"],
                         "supersedes": d["supersedes"], "superseded_by": d["superseded_by"], "attempt": d["attempt"],
                         "count": len(case["returns"][d["id"]]) if d["status"] == "complete" else d["partial"]} for d in dispatches],
            "idmap": {d["id"]: [pr2r_disposition(item) for item in case["returns"][d["id"]]] for d in dispatches if d["status"] == "complete"},
            "findings": prov["findings"], "side_dispositions": prov["side"],
            "counts": counts, "batches": pr2r_batches_summary(dispatches),
            "check": {"exit_code": 5 if flagged else 0, "status": "warn" if flagged else "pass",
                      "warnings": ["id:reissued"] if flagged else [], "error": None, "reissued": flagged},
        },
    }
    return dumps(doc)


# --- the trees and report stages (ADR-050 D14, items O-beta and O-gamma; contracts/part-files.md) --------------------------------------------
# Both stages run on the forms run. A plan, a batch input and a part are written for a root as the planner and the agents would leave them, with
# the digests that bind them: each batch input's SHA-256 is in the plan, and the plan's own SHA-256 is the plan_digest that a caller passes.
def pr2r_reference_rows(world: dict) -> dict:
    """The world's reference set as tachi_parsers.parse_reference_set reads its threats.md: Section 7's short texts, an em dash for the likelihood and
    impact it has no column for, and Section 4c's rows. A test compares this with the shipped reader's output, so a change there shows."""
    return {"open": [{"id": f["id"], "component": f["comp"], "threat": f["short"], "likelihood": EM, "impact": EM, "risk_level": f["risk"],
                      "mitigation": f["mit_short"], "agentic_pattern": f["pattern"], "delta_status": f["status"]} for f in world["findings"]],
            "resolved": [{"id": r["id"], "component": r["comp"], "threat": r["short"], "risk_level": r["risk"], "resolution_reason": r["reason"],
                          "delta_status": "RESOLVED"} for r in world["resolved"]]}


def pr2r_reference_digest(world: dict) -> str:
    """tachi_parts.reference_digest's value: the SHA-256 of the rows' canonical JSON (sorted keys, no spaces, ASCII)."""
    return hashlib.sha256(dumps(pr2r_reference_rows(world), indent=0).encode("utf-8")).hexdigest()


def pr2r_tree_file(world: dict, finding: dict, baseline: bool) -> str:
    """A tree file. The baseline's copy of a finding's tree carries one more line than the fresh one, so a copy of either shows which it came from."""
    text = tree_text(world, finding)
    if not baseline:
        return text
    head, _, rest = text.partition("\n\n")
    return head + "\n\n" + PR2R_BASELINE_TREE_NOTE + "\n\n" + rest


def pr2r_trees_material(world: dict) -> dict:
    """Rule 2's plan for the run (D14; S1P-A43): a tree for every open Critical or High finding, generated fresh, and the part's answer for each
    UNCHANGED finding whose baseline holds a tree, which is Rule 3's decision. One UNCHANGED finding has no baseline tree, the isolated fallback."""
    chosen = [f for f in world["findings"] if f["risk"] in ("Critical", "High")]
    unchanged = [f for f in chosen if f["status"] == STATUS_UNCHANGED]
    lacking = {unchanged[0]["id"]} if unchanged else set()
    with_tree = [f["id"] for f in chosen if f["status"] != STATUS_NEW and f["id"] not in lacking]
    units, items, rule3 = [], {}, 0
    for f in chosen:
        planned = "regenerated" if f["status"] == STATUS_UNCHANGED and f["id"] in with_tree else "generated_fresh"
        units.append({"finding_id": f["id"], "delta_status": f["status"], "action": planned})
        item = {"finding_id": f["id"], "delta_status": f["status"], "action": planned}
        if planned == "regenerated":
            rule3 += 1
            if rule3 % 3 == 0:  # the fresh tree is materially different: it stands
                item.update(similarity_score=(40 + label_below("pr2r:sim:" + f["id"], 25)) / 100)
            else:  # the baseline's tree stands: the part says carried_forward, and the assembler copies the baseline's file
                item.update(action="carried_forward", similarity_score=(80 + label_below("pr2r:sim:" + f["id"], 19)) / 100)
        items[f["id"]] = item
    order = sorted(chosen, key=lambda f: (f["risk"] != "Critical", prefix_rank(f["id"])))  # the merged manifest: Critical first, then High, each in S-2 order
    entries = []
    for f in order:
        entry = {"finding_id": f["id"], "delta_status": f["status"], "action": items[f["id"]]["action"]}
        if "similarity_score" in items[f["id"]]:
            entry["similarity_score"] = items[f["id"]]["similarity_score"]
        entry["file_path"] = "attack-trees/%s-attack-tree.md" % f["id"].lower()
        entries.append(entry)
    actions = [entry["action"] for entry in entries]
    manifest = {"schema_version": "1.0", "rule_applied": "Rule 2", "attack_tree_count": len(entries), "trees": entries,
                "summary": {"fresh": actions.count("generated_fresh"), "carried_forward": actions.count("carried_forward"),
                            "regenerated": actions.count("regenerated")}}
    return {"findings": chosen, "units": units, "items": items, "with_tree": with_tree, "lacking": sorted(lacking), "manifest": manifest}


def pr2r_stage_batches(stage: str, plan_id: str, base: str, specs: Sequence, refs: dict, params: dict) -> tuple:
    """The batch inputs and parts of one stage, as ({path under the plan's directory: text}, the plan's batch entries). base is the plan's directory."""
    files, entries = {}, []
    for spec in specs:
        batch_id = spec["batch_id"]
        input_text = dumps({
            "schema": "tachi.batch-input/1", "plan_id": plan_id, "batch_id": batch_id, "stage": stage, "agent_type": PR2R_STAGE_AGENT[stage],
            "finding_ids": spec["finding_ids"], "attempt": 1, "part_path": "%s/parts/%s.a1.json" % (base, batch_id),
            "tree_paths": spec.get("tree_paths", {}), "units": spec["units"], "refs": refs, "params": params})
        files["inputs/%s.json" % batch_id] = input_text
        files["parts/%s.a1.json" % batch_id] = dumps({
            "schema": "tachi.part/1", "plan_id": plan_id, "batch_id": batch_id, "stage": stage, "agent_type": PR2R_STAGE_AGENT[stage],
            "finding_ids": spec["finding_ids"], "items": spec["items"], "fragments": spec.get("fragments", [])})
        entries.append({"batch_id": batch_id, "parent": None, "attempt": 1, "finding_ids": spec["finding_ids"],
                        "input_sha256": pr2r_sha(input_text), "state": "done"})
    return files, entries


def pr2r_plan_text(stage: str, inputs: dict, refs: dict, params: dict, batch_size, unit_count: int, entries: list) -> str:
    return dumps({
        "schema": "tachi.plan/1", "plan_id": PR2R_IDS[stage], "stage": stage, "agent_type": PR2R_STAGE_AGENT[stage], "created_utc": PR2R_CREATED[stage],
        "tachi_version": PR2R_VERSION, "inputs": inputs, "refs": refs, "architecture_warning": None, "params": params, "batch_size": batch_size,
        "unit_count": unit_count, "preimage": {}, "out_snapshot": None, "retry_budget": {"limit": 2 * len(entries), "used": 0}, "batches": entries})


def pr2r_plan_input(path: str, text: str) -> dict:
    return {"path": path, "sha256": pr2r_sha(text), "bytes": len(_canonical_text(text))}


def pr2r_trees_stage(root: str) -> dict:
    """The trees stage of the forms run, as {path under the scenario's directory: text} and the values that its plan and its manifest fix."""
    case = pr2r_case("forms")
    world, threats = case["world"], case["threats"]
    material = pr2r_trees_material(world)
    out, plan_id = root + "/run", PR2R_IDS["trees"]
    base, rel = "%s/.tachi-build/trees/%s" % (out, plan_id), "run/tachi-build/trees/%s/" % PR2R_IDS["trees"]
    by_id = {f["id"]: f for f in world["findings"]}
    ids = [f["id"] for f in material["findings"]]
    chunks = [ids[i:i + PR2R_TREES_BATCH] for i in range(0, len(ids), PR2R_TREES_BATCH)]
    refs, params = {"baseline_dir": root + "/baseline"}, {"scoring_date": PR2_RUN_DATE, "rule_applied": "Rule 2",
                                                         "reference_digest": pr2r_reference_digest(world)}
    specs, files = [], {}
    for number, chunk in enumerate(chunks, start=1):
        specs.append({"batch_id": "B%03d" % number, "finding_ids": chunk,
                      "tree_paths": {fid: "%s/trees/%s-attack-tree.md" % (base, fid.lower()) for fid in chunk},
                      "units": [unit for unit in material["units"] if unit["finding_id"] in chunk], "items": [material["items"][fid] for fid in chunk]})
        for fid in chunk:
            files[rel + "trees/%s-attack-tree.md" % fid.lower()] = pr2r_tree_file(world, by_id[fid], False)
    stage_files, entries = pr2r_stage_batches("trees", plan_id, base, specs, refs, params)
    files.update({rel + path: text for path, text in stage_files.items()})
    plan = pr2r_plan_text("trees", {"threats": pr2r_plan_input(out + "/threats.md", threats)}, refs, params, PR2R_TREES_BATCH, len(ids), entries)
    files[rel + "plan.json"] = plan
    files["run/tachi-build/trees/current.json"] = dumps({"schema": "tachi.plan-pointer/1", "plan_id": plan_id})
    return {"files": files, "plan": plan, "plan_digest": pr2r_sha(plan), "material": material, "chunks": chunks, "params": params,
            "manifest_text": dumps(material["manifest"], indent=2, sort_keys=False)}


def pr2r_final_tree(world: dict, finding: dict, item: dict) -> str:
    """The bytes that attack-trees/<id>-attack-tree.md holds once the trees stage has run: the baseline's file when the part carried it forward."""
    return pr2r_tree_file(world, finding, item["action"] == "carried_forward")


def pr2r_trees_expected(name: str, root: str) -> str:
    stage = pr2r_trees_stage(root)
    material, manifest = stage["material"], stage["material"]["manifest"]
    units = []
    for unit in material["units"]:
        item = material["items"][unit["finding_id"]]
        entry = {"finding_id": unit["finding_id"], "delta_status": unit["delta_status"], "planned_action": unit["action"], "action": item["action"]}
        if "similarity_score" in item:
            entry["similarity_score"] = item["similarity_score"]
        entry["final_tree_comes_from"] = "baseline" if item["action"] == "carried_forward" else "plan"
        units.append(entry)
    carried = manifest["summary"]["carried_forward"]
    doc = {
        "schema": "tachi.fixture-expected/1", "variant": "pr2-runs", "scenario": name, "stage": "trees-assembly",
        "summary": ("S-4's PR 2 tree batches: the forms run's trees stage under Rule 2, with its manifests and Rule 3's decisions, before assemble-report.py trees runs."
                    if name == "trees" else
                    "S-4's PR 2 report parts: the forms run after assemble-report.py trees (its attack-trees/ and merged manifest), with the report stage's plan, "
                    "batch inputs and parts."),
        "run": {"date": PR2_RUN_DATE, "threats": "run/threats.md", "baseline": "baseline/threats.md", "baseline_trees": "baseline/attack-trees",
                "trees_plan_dir": "run/tachi-build/trees/%s" % PR2R_IDS["trees"],
                "how": "gen.materialize(scenario, directory) writes the scenario for that directory (plans, batch inputs and their digests hold only for the "
                       "root they were built for). Then assemble-report.py <mode> --run-dir <directory>/run --plan <plan_id> --plan-digest <plan_digest>"},
        "notes": [
            "Rule 2 applies: the baseline exists and the run has NEW, UPDATED and RESOLVED findings. Every open Critical or High finding gets a tree, in "
            "batches of %d in S-2 order (S1P-A57). A NEW or UPDATED finding is planned generated_fresh. An UNCHANGED finding whose baseline holds a tree "
            "is a Rule 3 unit, planned regenerated, and its part's item says regenerated (the fresh tree stands) or carried_forward (the baseline's "
            "stands), each with a similarity_score, which is the one value in which a part may differ from its batch input (S1P-A43). One UNCHANGED "
            "finding (%s) has no tree in the baseline, so it is planned generated_fresh: Rule 1's isolated fallback, here under Rule 2." % (
                PR2R_TREES_BATCH, ", ".join(material["lacking"])),
            "A baseline tree differs from the fresh tree of its finding by one line (%r), so a copy shows its source: the merged tree of a "
            "carried_forward item is the baseline's file byte for byte (FR-K5.3), and every other is the plan's tree under trees/." % PR2R_BASELINE_TREE_NOTE,
            "The plan's digests are the contract's: each batch input's SHA-256 is in the plan, the plan's SHA-256 is plan_digest, and params.reference_digest is "
            "tachi_parts.reference_digest of the run's reference set. The plan's inputs names (threats; for the report plan also trees_plan and tree_manifest) "
            "follow lane T's tests (RD-4, RD-10), because no ruling names them yet: T092's planner is the one to confirm them.",
        ],
        "trees": {
            "plan_id": PR2R_IDS["trees"], "plan_digest": stage["plan_digest"], "rule_applied": "Rule 2", "batch_size": PR2R_TREES_BATCH,
            "unit_count": len(material["units"]), "reference_digest": stage["params"]["reference_digest"],
            "batches": [{"batch_id": "B%03d" % n, "finding_ids": chunk} for n, chunk in enumerate(stage["chunks"], start=1)],
            "units": units, "baseline_trees": material["with_tree"], "unchanged_without_baseline_tree": material["lacking"],
            "merged_manifest": manifest,
            "stage_record_counts": {"units": len(material["units"]), "carried": carried, "rendered": manifest["attack_tree_count"]},
        },
    }
    return dumps(doc)


def pr2r_trees_files(root: str) -> dict:
    stage = pr2r_trees_stage(root)
    case = pr2r_case("forms")
    world = case["world"]
    by_id = {f["id"]: f for f in world["findings"]}
    files = dict(stage["files"])
    files["run/threats.md"] = case["threats"]
    files["baseline/threats.md"] = case["baseline"]
    for fid in stage["material"]["with_tree"]:
        files["baseline/attack-trees/%s-attack-tree.md" % fid.lower()] = pr2r_tree_file(world, by_id[fid], True)
    files["expected-outcomes.json"] = pr2r_trees_expected("trees", root)
    return files


# The report's texts. None holds a numeral outside a slot (ADR-050 D3's ban), apart from the one that breaks it on purpose, and the opening of the
# executive summary runs past its limit on purpose: the report stage's record then counts one fallback and one truncation.
PR2R_NARRATIVES = (
    "{{finding:%(id)s}} affects {{name:component:%(id)s}} and is rated {{band:risk:%(id)s}}. The weakness lets an attacker act with more authority than intended.",
    "On {{name:component:%(id)s}}, {{finding:%(id)s}} is rated {{band:risk:%(id)s}}. Fixing it closes a path that the attack tree for this finding follows.",
    "The risk of {{finding:%(id)s}} is {{band:risk:%(id)s}}, and it sits on {{name:component:%(id)s}}. Owners should treat it with the findings around it.",
)
PR2R_PATTERN_TEXT = {
    "agent_collusion": "Agents that coordinate through a shared channel can add up actions that no single limit covers.",
    "emergent_behavior": "Planning agents that feed each other's output can drift into behavior that no one tested for.",
    "temporal_attack": "State kept between runs can carry an instruction that acts long after it was written.",
    "trust_exploitation": "Agents and people that trust a fluent answer pass it on without a check of its source.",
    "communication_vulnerability": "Messages between agents can be read or changed on the channel that joins them.",
    "resource_competition": "Agents that share one pool can starve each other, and the slowest one sets the pace.",
}
PR2R_PADDING = "The posture also reflects how long these weaknesses have stayed open and how many components share each one. "


def pr2r_row(finding: dict) -> dict:
    return {"finding_id": finding["id"], "component": finding["comp"], "threat": finding["short"], "risk_level": finding["risk"],
            "mitigation": finding["mit_short"], "agentic_pattern": finding["pattern"], "delta_status": finding["status"]}


def pr2r_report_specs(world: dict) -> list:
    """The report stage's batches in the template's order, as pr2r_stage_batches takes them (plus each batch's section): a section part holds fragments,
    a findings part one item for each finding. No attack_chains part is planned, because threats.md holds no outcome record (S1P-A58)."""
    findings = world["findings"]
    low = ("Medium", "Low", "Note")
    summarize = len(findings) > 30  # D6: a finding is summarized when the run has more than 30 open findings and its level is Medium or lower
    narrated = [f for f in findings if not (summarize and f["risk"] in low)]
    summarized = [f for f in findings if summarize and f["risk"] in low]
    in_category = {c: [f for f in findings if PR2R_CATEGORY_KEY[f["prefix"]] == c] for c in PR2R_CATEGORY_KEYS}
    categories = [c for c in PR2R_CATEGORY_KEYS if in_category[c]]
    summary_categories = [c for c in categories if any(f in summarized for f in in_category[c])]
    patterns = [p for p in PR2R_PATTERNS if any(f["pattern"] == p for f in findings)]
    peers = {m["id"] for g in world["groups"] for m in g["members"][1:]}  # D8: a group's row stands for its primary
    roadmap = [f for f in findings if f["id"] not in peers]
    group_of = {g["members"][0]["id"]: g for g in world["groups"]}
    critical = [f["id"] for f in findings if f["risk"] == "Critical"]
    spoofing = [f["id"] for f in findings if f["prefix"] == "S"]
    agentic = [f["id"] for f in findings if f["prefix"] == "AG"]

    def section(name: str, pairs: list, extra: dict = None) -> dict:
        units = [dict({"section": name, "key": key}, **(extra or {}).get(key, {})) for key, _ in pairs]
        return {"section": name, "kind": "section", "finding_ids": [], "items": [], "units": units,
                "fragments": [{"slot_key": key, "text": text} for key, text in pairs if text is not None]}

    posture = ("The posture is shaped by {{count:critical}} critical and {{count:high}} high findings among {{count:open}} open findings, and "
               "{{count:new}} of them are new in this run. ") + PR2R_PADDING * 15
    ids_of = lambda c, subset: [f["id"] for f in in_category[c] if f in subset]  # noqa: E731
    category_units = {"category." + c: {"narrated": ids_of(c, narrated), "summarized": ids_of(c, summarized)} for c in categories}
    category_units.update({"summary." + c: {"narrated": ids_of(c, narrated), "summarized": ids_of(c, summarized)} for c in summary_categories})
    specs = [
        section("exec_summary", [
            ("risk_posture", posture),
            ("top_threats", "The most serious threats are {{finding:%s}} on {{name:component:%s}} and {{finding:%s}} on {{name:component:%s}}." % (
                critical[0], critical[0], critical[1], critical[1])),
            ("key_recommendations", "Close the critical findings first, beginning with {{finding:%s}}, then work through the high findings in the order "
                                    "of the roadmap." % critical[0]),
            ("compliance", "Several findings bear on access control, audit and data protection duties, so the owners of those duties should read the roadmap.")]),
        section("architecture_overview", [
            ("system_context", "The platform turns operator requests into planned and audited shipment actions, and every agent reaches carrier systems "
                               "through one tool server."),
            ("trust_boundaries", "The platform spans 5 trust zones, and requests cross from the public internet into the edge zone first.")]),
        section("threat_categories", [("overview", "Findings appear in every category, and the agentic and language model categories carry the most severe ones.")] +
                [("category." + c, "Open findings in this category number {{count:%s}}, and {{count:%s.critical}} of them are critical." % (c, c)) for c in categories] +
                [("summary." + c, "The remaining findings in this category are of medium or lower severity and are summarized here.") for c in summary_categories],
                category_units)]
    rows = [dict(pr2r_row(f), section="threat_analysis", tree=f["risk"] in ("Critical", "High")) for f in narrated]
    items = [{"finding_id": f["id"], "narrative": PR2R_NARRATIVES[label_below("pr2r:narrative:" + f["id"], len(PR2R_NARRATIVES))] % {"id": f["id"]},
              "tree_summary": ("The tree for {{finding:%s}} starts at a connected component and ends at the weakness named above." % f["id"])
              if f["risk"] in ("Critical", "High") else None} for f in narrated]
    specs.append({"section": "threat_analysis", "kind": "findings", "finding_ids": [f["id"] for f in narrated], "items": items, "units": rows, "fragments": []})
    specs.append(section("cross_cutting_themes", [("themes", None)]))
    specs[-1]["fragments"] = [
        {"slot_key": "theme.1.title", "text": "Shared credentials recur"},
        {"slot_key": "theme.1.body", "text": "Long-lived tokens and shared accounts appear on several components, for example {{finding:%s}} and {{finding:%s}}." % (
            spoofing[0], spoofing[1])},
        {"slot_key": "theme.2.title", "text": "Agent authority is wide"},
        {"slot_key": "theme.2.body", "text": "Agents hold broad tool access, so one injected instruction reaches far, as {{finding:%s}} shows." % agentic[0]}]
    specs.append(section("agentic_patterns", [("pattern." + p, PR2R_PATTERN_TEXT[p]) for p in patterns]))
    rows = []
    for f in roadmap:
        row = dict(pr2r_row(f), section="remediation_roadmap")
        if f["id"] in group_of:  # a group's primary stands for the group: its ID and its members' rows
            row.update(group=group_of[f["id"]]["id"], members=[pr2r_row(m) for m in group_of[f["id"]]["members"]])
        rows.append(row)
    efforts = ("Low", "Medium", "High")
    items = [{"finding_id": f["id"], "effort": efforts[label_below("pr2r:effort:" + f["id"], 3)],
              "dependencies": "Depends on the credential rotation work." if label_below("pr2r:deps:" + f["id"], 3) == 0 else None} for f in roadmap]
    specs.append({"section": "remediation_roadmap", "kind": "findings", "finding_ids": [f["id"] for f in roadmap], "items": items, "units": rows, "fragments": []})
    specs.append(section("delta_summary", [("progress", "Since the baseline, {{count:new}} findings are new, {{count:updated}} changed and {{count:unchanged}} "
                                                       "stayed as they were, and {{count:resolved}} were resolved.")]))
    order = ["exec_summary", "architecture_overview", "threat_categories", "threat_analysis", "cross_cutting_themes", "agentic_patterns",
             "remediation_roadmap", "delta_summary"]  # the template's order (tachi_parts.REPORT_PARTS), less attack_chains
    specs.sort(key=lambda spec: order.index(spec["section"]))
    for number, spec in enumerate(specs, start=1):
        spec["batch_id"] = "B%03d" % number
    return specs


def pr2r_report_stage(root: str) -> dict:
    """The report stage of the forms run after assemble-report.py trees: the plan pins the trees plan, the merged manifest and threats.md."""
    case, trees = pr2r_case("forms"), pr2r_trees_stage(root)
    world, out, plan_id = case["world"], root + "/run", PR2R_IDS["report"]
    base, rel = "%s/.tachi-build/report/%s" % (out, plan_id), "run/tachi-build/report/%s/" % plan_id
    specs = pr2r_report_specs(world)
    params = {"scoring_date": PR2_RUN_DATE, "reference_digest": pr2r_reference_digest(world), "trees_plan_id": PR2R_IDS["trees"]}
    stage_files, entries = pr2r_stage_batches("report", plan_id, base, specs, {}, params)
    unit_count = sum(len(spec["units"]) for spec in specs)
    inputs = {"threats": pr2r_plan_input(out + "/threats.md", case["threats"]),
              "trees_plan": pr2r_plan_input("%s/.tachi-build/trees/%s/plan.json" % (out, PR2R_IDS["trees"]), trees["plan"]),
              "tree_manifest": pr2r_plan_input(out + "/attack-trees/.manifest.json", trees["manifest_text"])}
    plan = pr2r_plan_text("report", inputs, {}, params, None, unit_count, entries)
    files = {rel + path: text for path, text in stage_files.items()}
    files[rel + "plan.json"] = plan
    files["run/tachi-build/report/current.json"] = dumps({"schema": "tachi.plan-pointer/1", "plan_id": plan_id})
    return {"files": files, "plan": plan, "plan_digest": pr2r_sha(plan), "specs": specs, "unit_count": unit_count, "params": params, "trees": trees}


def pr2r_report_expected(root: str) -> str:
    stage = pr2r_report_stage(root)
    case = pr2r_case("forms")
    world, specs, trees = case["world"], stage["specs"], stage["trees"]
    findings = world["findings"]
    peers = sorted({m["id"] for g in world["groups"] for m in g["members"][1:]}, key=prefix_rank)
    spec_of = {spec["section"]: spec for spec in specs}
    doc = {
        "schema": "tachi.fixture-expected/1", "variant": "pr2-runs", "scenario": "report", "stage": "report-assembly",
        "summary": "S-4's PR 2 report parts: the forms run after assemble-report.py trees, with the report stage's plan, batch inputs and parts.",
        "run": {"date": PR2_RUN_DATE, "threats": "run/threats.md", "baseline": "baseline/threats.md", "attack_trees": "run/attack-trees",
                "trees_plan_dir": "run/tachi-build/trees/%s" % PR2R_IDS["trees"], "report_plan_dir": "run/tachi-build/report/%s" % PR2R_IDS["report"],
                "how": "gen.materialize(scenario, directory) writes the scenario for that directory (plans, batch inputs and their digests hold only for the "
                       "root they were built for). Then assemble-report.py report --run-dir <directory>/run --plan <plan_id> --plan-digest <plan_digest>. "
                       "Do not run the trees mode first: the report plan pins this run's merged manifest, and the trees mode would write its own bytes"},
        "notes": [
            "This is the forms run after Step 2.9's trees stage: run/attack-trees/ holds each tree as assemble-report.py trees leaves it (a copy of the baseline's "
            "file for a carried_forward item, the plan's tree otherwise) and the merged manifest. The report plan pins threats.md, the trees plan and that "
            "manifest by digest, and params.reference_digest is the run's reference set's. Eight batches, in the template's order: six section parts "
            "(executive summary, architecture overview, threat categories, cross-cutting themes, agentic patterns and the delta summary) and two "
            "findings parts (the threat analysis and the remediation roadmap).",
            "The run has more than 30 open findings, so each Medium, Low and Note finding is summarized by its category and the Critical and High findings are "
            "narrated one by one. No attack_chains part is planned: threats.md holds no outcome record, so the planner plans none and Section 6 would print "
            "the outcome line (S1P-A58). Each findings part fits in one batch (22 narrated findings and 144 roadmap rows are the sizes), so none is split.",
            "Two fragments are wrong on purpose. architecture_overview's trust_boundaries holds a digit outside a slot, so it takes the fixed fallback "
            "sentence (one narrative_fallback). exec_summary's risk_posture is longer than its 1,500 characters, and is cut where plain text stands (one "
            "truncation). Both parts are valid: a narrative that breaks the rules takes its fixed sentence and an over-limit one is cut, so reconcile "
            "accepts them (D3), and the report stage's record counts both.",
            "A section unit holds its section and key, and a category's unit its narrated and summarized IDs; a findings unit holds the finding's Section 7 "
            "row (a roadmap primary also its group and the members' rows). The contract says more rows go in a section unit, and no script reads them yet: "
            "T109's plan is what settles them.",
        ],
        "report": {
            "plan_id": PR2R_IDS["report"], "plan_digest": stage["plan_digest"], "trees_plan_id": PR2R_IDS["trees"], "trees_plan_digest": trees["plan_digest"],
            "reference_digest": stage["params"]["reference_digest"], "unit_count": stage["unit_count"],
            "batches": [{"batch_id": spec["batch_id"], "section": spec["section"], "kind": spec["kind"],
                         "units": [unit.get("key") or unit["finding_id"] for unit in spec["units"]]} for spec in specs],
            "open_ids": [f["id"] for f in findings], "narrated": [item["finding_id"] for item in spec_of["threat_analysis"]["items"]],
            "summarized": [f["id"] for f in findings if f["risk"] in ("Medium", "Low", "Note")],
            "roadmap": [item["finding_id"] for item in spec_of["remediation_roadmap"]["items"]], "roadmap_peers": peers,
            "patterns": [unit["key"].split(".", 1)[1] for unit in spec_of["agentic_patterns"]["units"]],
            "attack_chains_planned": False,
            "deliberate": [{"batch_id": spec_of["architecture_overview"]["batch_id"], "slot_key": "trust_boundaries",
                            "what": "a digit outside a slot: the per-field fallback"},
                           {"batch_id": spec_of["exec_summary"]["batch_id"], "slot_key": "risk_posture", "what": "longer than its limit: cut and flagged"}],
            "stage_record_counts": {"units": stage["unit_count"], "narrative_fallbacks": 1, "truncations": 1},
        },
    }
    return dumps(doc)


def pr2r_report_files(root: str) -> dict:
    case = pr2r_case("forms")
    world = case["world"]
    by_id = {f["id"]: f for f in world["findings"]}
    stage = pr2r_report_stage(root)
    trees = stage["trees"]
    files = dict(trees["files"])
    files.update(stage["files"])
    files["run/threats.md"] = case["threats"]
    files["baseline/threats.md"] = case["baseline"]
    for fid in trees["material"]["with_tree"]:
        files["baseline/attack-trees/%s-attack-tree.md" % fid.lower()] = pr2r_tree_file(world, by_id[fid], True)
    for fid, item in trees["material"]["items"].items():
        files["run/attack-trees/%s-attack-tree.md" % fid.lower()] = pr2r_final_tree(world, by_id[fid], item)
    files["run/attack-trees/.manifest.json"] = trees["manifest_text"]
    files["expected-outcomes.json"] = pr2r_report_expected(root)
    return files


def pr2r_scenario_files(name: str, root: str) -> dict:
    """One scenario's files for a root, relative to the scenario's own directory, in the committed copy's naming (tachi-build/)."""
    if name in ("forms", "truncation", "reissue-mark", "reissue-no-mark"):
        return pr2r_provenance_files(name, root)
    if name == "trees":
        return pr2r_trees_files(root)
    if name == "report":
        return pr2r_report_files(root)
    raise ValueError("unknown scenario: %r" % name)


def pr2r_files(root: str) -> dict:
    """Every scenario for a root, as {path under pr2-runs/: text}."""
    return {"pr2-runs/%s/%s" % (name, path): text for name in PR2R_SCENARIOS for path, text in pr2r_scenario_files(name, root).items()}


_PR2R_ROOT_OK = re.compile(r"/[A-Za-z0-9_.+@=,~-]+(/[A-Za-z0-9_.+@=,~-]+)*")


def materialize(scenario: str, dest: str) -> list:
    """Write one pr2-runs scenario for a real directory, so that a script can run on it: dest/run is the run's {out}, with its tachi-build/ named
    .tachi-build/, dest/baseline is the baseline run directory where the scenario has one, and expected-outcomes.json sits beside them. Every
    absolute path in a record, a brief, a plan and a batch input names dest, and each digest that binds them is computed for it (the committed
    copy holds the same files built for PR2R_ROOT). dest must be an absolute path of plain characters. Returns the files written, relative to dest."""
    if scenario not in PR2R_SCENARIOS:
        raise ValueError("unknown scenario: %r" % (scenario,))
    if not isinstance(dest, str) or not _PR2R_ROOT_OK.fullmatch(dest) or {".", ".."} & set(dest.split("/")):
        raise ValueError("dest must be an absolute path of letters, digits and . _ + @ = , ~ - only: %r" % (dest,))
    files, written = pr2r_scenario_files(scenario, dest), []
    for path in sorted(files):
        target = "run/.tachi-build/" + path[len("run/tachi-build/"):] if path.startswith("run/tachi-build/") else path
        full = os.path.join(dest, *target.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as handle:
            handle.write(_canonical_text(files[path]))
        written.append(target)
    return sorted(written)


PARTS = {
    "canary": part_canary,
    "architecture": part_architecture,
    "baseline": part_baseline,
    "stub-codebase": part_stub_codebase,
    "gated-subset": part_gated_subset,
    "seeded-error": part_seeded_error,
    "legacy-format": part_legacy_format,
    "tagged": part_tagged,
    "id-reuse": part_id_reuse_pr1_pr2,
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
