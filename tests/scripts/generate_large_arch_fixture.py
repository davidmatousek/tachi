"""Deterministic generator for F-374's synthetic large-architecture fixture (spec S-4).

Built in two steps. W0 (T003) wrote the CLI, the seeded helpers, the serializer and the part
registry. T019 (W1) fills the base parts: the architecture, the baseline run directory, the stub
codebase and the gated subset. T040, T148 and T103 fill the variant parts that are still stubs.
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
Scale of the base set: 408 open findings over all 12 prefixes (56 Critical), 6 RESOLVED, 21 correlation groups
(13 span three or more categories). Each of its six targeted outputs is over twice the 64k cap by UTF-8 bytes / 4.
Every score is internally consistent (CVSS from its vector, composite from its parts, no rounding tie), so the
base set carries no seeded error; the seeded-error, legacy-format, tagged, ties and regroup parts add those.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
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
    for row in COMPONENT_ROWS:
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
             table(("Zone", "Trust Level", "Components"), [(z["name"], z["level"], ", ".join(z["members"])) for z in world["zones"]]),
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
        'run_id: "%s"' % runs["threats"], "baseline:", '  source: "baseline-runs/%s/threats.md"' % dates["baseline"],
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
           table(("Field", "Value"), (("Source", "baseline-runs/%s/threats.md" % cfg["dates"]["baseline"]), ("Date", cfg["dates"]["baseline"]),
                                      ("Baseline Findings", baseline_count(world)), ("Run ID", cfg["run_ids"]["baseline"]))),
           # The block exactly as scripts/populate-affected-assets.py renders it (no introduction, one row per finding in
           # Section 7's order), so that Step 1.5 of /tachi.risk-score rewrites nothing. No component carries a tag.
           "", "---", "", "## Affected Assets", "",
           table(("Finding ID", "Affected Assets"), [(f["id"], "[]") for f in ranked])]
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
            "properties": {"security-severity": fmt1(s["composite"]), "cvss-base-score": fmt1(s["cvss"]), "cvss-vector": s["vector"],
                           "exploitability": fmt1(s["expl"]), "scalability": fmt1(s["scale"]), "reachability": fmt1(s["reach"]),
                           "composite-weights": "0.35/0.30/0.15/0.20", "score-source": "fresh",
                           "baseline-state": {STATUS_NEW: "new", STATUS_UNCHANGED: "unchanged", STATUS_UPDATED: "updated"}[f["status"]],
                           "severity-band": s["band"], "risk-owner": "Unassigned", "remediation-sla": s["sla"],
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
                lines.append('        %s["%s"]' % (name.replace("-", "_"), name))
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
    lines += ["", "## Notes", "",
              "No component in this description carries an asset-sensitivity tag. The platform and every name in it are invented for testing."]
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
                 [(f["id"], "fresh", f["comp"], clip(f["short"], 64), fmt1(scores[f["id"]]["cvss"]), fmt1(scores[f["id"]]["expl"]),
                   fmt1(scores[f["id"]]["scale"]), fmt1(scores[f["id"]]["reach"]), fmt1(scores[f["id"]]["composite"]),
                   scores[f["id"]]["band"], scores[f["id"]]["sla"], scores[f["id"]]["disposition"]) for f in order]),
           "", "> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored "
           "independently. Correlated peer findings inherit the primary's scores to keep the group consistent.", "", "---", "",
           "## 3. Dimensional Breakdown", "",
           "Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.", ""]
    for f in order:
        s = scores[f["id"]]
        comp = world["by_name"][f["comp"]]
        out += ["### %s %s %s" % (f["id"], EM, f["comp"]), "", "**Threat**: %s" % first_sentence(f["threat"]), "",
                "**Category**: %s | **Original Risk Level**: %s | **Composite**: %s (%s)" % (
                    _category_name(f["prefix"]), f["risk"], fmt1(s["composite"]), s["band"]), ""]
        if f["id"] in peer_of:
            lead, group_id = peer_of[f["id"]]
            out += ["**Correlation Group**: Scores inherited from primary finding %s (%s). Dimensional detail is recorded on the primary." % (lead, group_id),
                    "", "**Score**: %s | **Vector**: `%s`" % (fmt1(s["cvss"]), s["vector"]), "", "---", ""]
            continue
        metrics = dict(part.split(":") for part in s["vector"].split("/")[1:])
        out += ["#### CVSS 3.1 Base", "", "**Score**: %s | **Vector**: `%s`" % (fmt1(s["cvss"]), s["vector"]), "",
                table(("Metric", "Value", "Rationale"),
                      [(label, names[metrics[key]], why[metrics[key]]) for key, label, names, why in CVSS_METRICS]), "",
                "#### Exploitability", "", "**Score**: %s (average of sub-dimensions)" % fmt1(s["expl"]), "",
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
                  [(f["id"], scores[f["id"]]["band"], "Unassigned", scores[f["id"]]["sla"], scores[f["id"]]["disposition"],
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
