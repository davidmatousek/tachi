#!/usr/bin/env python3
"""Generate ``threats.sarif`` from the compiled ``threats.md`` (F-374, PR 2; ADR-050 D1, D7, D8).

From PR 2 on, shipped code writes ``threats.sarif`` and no agent does. The model compiles ``threats.md``, and this script reads
that file and writes the SARIF through the shared emitter (``scripts/sarif_common.py``), so each result's identity, its
membership and its correlation are functions of the findings alone. It runs once, in the main session, at Step 2.10 of
``/tachi.threat-model``, after the checks of Steps 2.5 to 2.9:

    python3 scripts/generate-threats-sarif.py --threats FILE --out DIR [--architecture PATH]

What it reads, all from ``--threats``:

* the member set is Section 7's open findings (NEW, UPDATED and UNCHANGED), through the reference-set wrapper, so the drift
  forms that tachi's shipped samples show are read too (D8). A finding in Section 4c, RESOLVED, is a result nowhere;
* each finding's component, zone, kind and layer come from Sections 1 and 2 and the per-finding tables, by ADR-050 D2's layer
  chain, and ``affected_assets`` is copied from the populator's block (ADR-046 D2);
* the groups come from Section 4a through ``parse_correlation_groups``, whose claim rule decides them. It reports no repeated
  member: ``check-threat-model.py`` makes that report once, at Step 2.8, so the codes stay 0, 1, 2 and 4 (S1P-A19);
* ``baseline-run-id`` is the run ID that the frontmatter's baseline block names, and is absent in a first run.

``--architecture`` is optional. It is the command's own path to the architecture file, a candidate for D7's resolver, which
checks it in code and then tries the body line and the default (``sarif_common.resolve_architecture``). A candidate that fails
a check warns on stderr, and the run goes on (S1P-A26). No script takes a finished URI.

It writes ``<out>/threats.sarif`` and nothing else, atomically and only after the emitter's self-check, so a run that stops
leaves an earlier file as it was. It reads no earlier ``threats.sarif`` and no baseline SARIF: every key is recomputed.

Exit codes are ``contracts/cli.md``'s: 0 done, 1 an input is missing or unreadable, 2 a validation, usage or guard failure
(Section 7 unreadable, an input that isn't strict UTF-8, a forbidden character in a value that it takes), 4 the emitter's
self-check or a backstop failed or the file could not be written. It never exits 3 or 5. A failure prints D4's message on stderr.
On success stdout is one JSON object (S1P-A27) and each warning is a ``WARNING`` line on stderr.

Nothing here reads the clock or a random source, so the bytes depend on the input alone. Standard library plus the shared
helpers, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("generate-threats-sarif.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import os
import re
from decimal import Decimal
from typing import Any, Dict, List, Mapping, Optional, Tuple

sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import sarif_common as sc  # noqa: E402
import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402
import tachi_scoring as ts  # noqa: E402

STAGE = "threats-sarif"  # the banner of D4's message. The generator takes no plan, so it keeps no plan directory
RENDERER = "generate-threats-sarif.py"  # the stamp's name: the installed file name, as a literal (contracts/cli.md)
SARIF = "threats.sarif"
TOOL = sc.TOOL_NAMES[SARIF]
PLACEHOLDER_COMPONENT, PLACEHOLDER_THREAT = "Unspecified", "No threat description."  # a finding whose form lacks them (the renderers' words)
# The fields of a finding that reach the file. ``id`` passes the allow-list, and the status is read through a closed map.
COPIED_FIELDS = ("component", "threat", "mitigation", "risk_level", "agentic_pattern")

KIND_OF_DFD_TYPE = {"External Entity": "external-entity", "Process": "process", "Data Store": "data"}  # D8's closed map; anything else is ``process``
_LAYER = re.compile(r"L[1-7](?![0-9])", re.ASCII)
BASELINE_STATE = {"NEW": "new", "UNCHANGED": "unchanged", "UPDATED": "updated"}  # ``absent`` never occurs: RESOLVED findings are no result (D8)

# A finding's category tags: ``security``, then ``stride`` or ``ai``, then the category's own (S1P-A28). ``TE`` takes ``AG``'s plus its own.
_STRIDE, _AGENTIC, _LLM = ("security", "stride"), ("security", "ai", "agentic"), ("security", "ai", "llm")
CATEGORY_TAGS = {
    "S": _STRIDE + ("spoofing",), "T": _STRIDE + ("tampering",), "R": _STRIDE + ("repudiation",),
    "I": _STRIDE + ("information-disclosure",), "D": _STRIDE + ("denial-of-service",), "E": _STRIDE + ("elevation-of-privilege",),
    "AG": _AGENTIC, "AGP": _AGENTIC + ("agentic-pattern",), "TE": _AGENTIC + ("human-trust-exploitation",),
    "LLM": _LLM, "OI": _LLM + ("output-integrity",), "MI": _LLM + ("misinformation",),
}

# A rule's ``security-severity`` is the highest value among its results (sarif-specification.md: the severity table), and a risk
# level that is none of the five words counts as a Medium, the ``warning`` that ``sarif_common.level_for_band`` gives it.
SECURITY_SEVERITY = {"Critical": Decimal("9.0"), "High": Decimal("8.0"), "Medium": Decimal("5.0"), "Low": Decimal("2.0"), "Note": Decimal("0.1")}
DEFAULT_SEVERITY = SECURITY_SEVERITY["Medium"]

# The run's taxonomies, as sarif-specification.md declares them for this file ("Declare exactly two entries", whose index order never changes),
# and the driver's ``supportedTaxonomies`` that name them by index. The rules' ``relationships`` link to ``OWASP`` and ``CWE`` by name.
TAXONOMIES = [
    {"name": "OWASP", "version": "2021", "informationUri": "https://owasp.org/Top10/", "organization": "OWASP Foundation",
     "shortDescription": {"text": "OWASP Top 10 Web Application Security Risks"}},
    {"name": "CWE", "version": "4.13", "informationUri": "https://cwe.mitre.org/", "organization": "MITRE",
     "shortDescription": {"text": "Common Weakness Enumeration"}},
]
SUPPORTED_TAXONOMIES = [{"name": "OWASP", "index": 0}, {"name": "CWE", "index": 1}]

# Each rule's ``help`` as ``(text, markdown)``, by category. The shared rule table (``sarif_common.RULES``) carries none, and this file's contract
# names the field (sarif-specification.md, "Rule Definition Templates": every rule MUST include ``help``), so it stays, with the words that this
# generator has always written. Only the rules of categories that have a result are written.
RULE_HELP = {
    "spoofing": (
        "Review authentication mechanisms at all trust boundaries. Verify mTLS, signed tokens, and session binding controls.",
        "Review authentication mechanisms at all trust boundaries.\n\n**References**: OWASP A07 (Identification and Authentication Failures), "
        "CWE-287 (Improper Authentication), OWASP LLM01:2026 (for LLM-specific identity bypass)"),
    "tampering": (
        "Review integrity controls on all data flows, stored data, and inter-process messages. Verify digital signatures, hash verification, "
        "and write-access controls.",
        "Review integrity controls on all data flows.\n\n**References**: OWASP A08 (Software and Data Integrity Failures), "
        "CWE-345 (Insufficient Verification of Data Authenticity)"),
    "repudiation": (
        "Review audit logging completeness and tamper-evidence. Verify that all agent actions are logged with content hashes and service key "
        "signatures before execution.",
        "Review audit logging completeness.\n\n**References**: OWASP A09 (Security Logging and Monitoring Failures), CWE-778 (Insufficient Logging)"),
    "info-disclosure": (
        "Review access controls on all data stores and output paths. Verify output scrubbing, field-level log classification, and query result "
        "authorization.",
        "Review access controls on data stores and outputs.\n\n**References**: OWASP A01 (Broken Access Control), "
        "CWE-200 (Exposure of Sensitive Information)"),
    "denial-of-service": (
        "Review rate limiting, resource quotas, circuit breakers, and backpressure mechanisms on all components.",
        "Review rate limiting and resource controls.\n\n**References**: OWASP A05 (Security Misconfiguration), "
        "CWE-400 (Uncontrolled Resource Consumption)"),
    "privilege-escalation": (
        "Review authorization enforcement at all components. Verify per-session scoped permissions, zero-trust tool authorization, and model "
        "update signing.",
        "Review authorization enforcement.\n\n**References**: OWASP A01 (Broken Access Control), CWE-269 (Improper Privilege Management)"),
    "agentic": (
        "Review agent scope enforcement, tool call validation, inter-agent rate limits, inter-agent channel authentication, and model update "
        "capability auditing.",
        "Review agent scope enforcement and tool validation.\n\n**References**: OWASP Agentic Security Initiative (ASI-01, ASI-07), "
        "MCP Top 10 (MCP-03), MITRE ATLAS (AML.T0060), CWE-693 (Protection Mechanism Failure), CWE-287 (Improper Authentication)"),
    "llm": (
        "Review prompt injection controls, training data provenance, output encoding for execution sinks, model extraction detection, and "
        "factual-output grounding for advisory systems.",
        "Review LLM input/output controls.\n\n**References**: OWASP LLM Top 10 v2026 (LLM01, LLM05, LLM07, LLM10), "
        "CWE-74 (Improper Neutralization of Special Elements)"),
}
CATEGORY_OF_RULE = {rule_id: category for category, rule_id in sc.RULE_ID_BY_CATEGORY.items()}


class Run(tp.RunCore):
    """``tachi_parts.RunCore``'s fields (the warnings, the layers, the components and their zones, the groups and the URI), and what Section 7 is read against."""

    def __init__(self) -> None:
        super().__init__()
        self.aware = False                          # the threat model names a baseline. Without one, every result is new (S1P-A28)
        self.baseline_run_id: Optional[str] = None  # the run that the baseline names, which ``baseline-run-id`` carries
        self.affected: Dict[str, List[str]] = {}    # the Affected Assets block, by canonical finding ID, in the block's own order
        self.folded: Dict[str, Tuple[str, str]] = {}  # Section 1's components by case-folded name, the first listed winning: a finding may spell one in another case


# =============================================================================
# Reading threats.md
# =============================================================================

def _refuse(source: str, finding_id: Optional[str], value: Any, place: Optional[Any] = None) -> None:
    """Exit 2 when ``value``, which the generator takes from ``threats.md``, holds a character that D3's step 10 forbids (NFR-10, P0-4).

    ``threats.md`` isn't a part, so nothing has checked its text: a carriage return, an escape or a bidi control would reach a SARIF string
    and a viewer. Each value is checked where it is taken, before any result is built. The message gives the character's code point and never
    its text. ``finding_id`` names the finding, and ``None`` a component, zone or layer name (or, with ``place``, what ``place`` says).
    """
    problem = tp.forbidden_problem(source, finding_id, value, place)
    if problem is not None:
        raise tp.StageFailure(2, STAGE, problem, "regenerate %s with /tachi.threat-model, or edit the value to remove the character, then re-run the command" % source)


def _read_threats(path: str, source: str) -> Tuple[bytes, str]:
    """The bytes and the text of ``--threats``: a regular file of at most 16 MiB (D3 step 2) and strict UTF-8."""
    raw, reason = tp.read_capped(path, tp.MAX_AGENT_INPUT_BYTES, tp.RENDERER_READ_REASONS)
    if raw is None:
        if reason == "too-large":
            raise tp.StageFailure(2, STAGE, "%s is over %d bytes" % (source, tp.MAX_AGENT_INPUT_BYTES), "regenerate threats.md with /tachi.threat-model")
        raise tp.StageFailure(1, STAGE, "%s cannot be read (%s)" % (source, reason), "check the --threats path and re-run")
    try:
        return raw, raw.decode("utf-8")
    except UnicodeDecodeError:
        raise tp.StageFailure(2, STAGE, "the threat model input %s is not strict UTF-8" % source, "regenerate threats.md with /tachi.threat-model") from None


def _prepare(run: Run, text: str, source: str) -> Dict[str, Any]:
    """Read the reference set and everything around it. Returns the reference set; fills ``run``."""
    try:
        reference = tachi_parsers.parse_reference_set(text, source=source)
    except tachi_parsers.ReferenceSetError as exc:
        raise tp.StageFailure(2, STAGE, "%s. Expected %s" % (exc.reason, exc.expected), exc.remedy) from None
    if reference["duplicates"]:
        run.warn("duplicate-finding-id", "%s lists these findings more than once, and the first row of each is used: %s" % (source, ", ".join(reference["duplicates"])))
    if reference["lacking"]:
        names = sorted({name for found in reference["lacking"].values() for name in found})
        run.warn("value-not-in-form", "Section 7 of %s (the %s form) lacks %s for %d of %d findings: a missing component or threat is written as %s and %s, and a missing "
                 "status counts as new" % (source, reference["form"], ", ".join(names), len(reference["lacking"]), len(reference["open"]),
                                           PLACEHOLDER_COMPONENT, PLACEHOLDER_THREAT))
    open_ids = [tp.canonical_finding_id(row["id"]) for row in reference["open"]]

    for row in tachi_parsers.parse_markdown_table(text, "### Components"):
        name = row.get("Component", "").strip()
        if name and name not in run.component_info:
            run.component_info[name] = (row.get("Type", "").strip(), row.get("MAESTRO Layer", "").strip())
    for name, info in run.component_info.items():
        run.folded.setdefault(name.casefold(), info)
    for canonical, layer in tachi_parsers.parse_finding_layers(text).items():   # D2's chain, steps 1 and 2: Section 7's cell, else the finding's own row in §3 or §4
        run.finding_layer.setdefault(canonical, layer)
    for row in tachi_parsers.parse_markdown_table(text, "### Trust Zones"):   # a zone is as Section 2 writes it, a layer note such as ``(L4)`` included
        zone = row.get("Zone", "").strip()
        if not zone:
            continue
        for member in (part.strip() for part in row.get("Components", "").split(",")):
            if member:
                run.component_zone.setdefault(member.casefold(), zone)

    grouped = tachi_parsers.parse_correlation_groups(text, member_ids=open_ids)   # the claim rule is its own; a repeated member is ``check-threat-model.py``'s report (S1P-A19)
    if grouped["errors"]:
        run.warn("correlation-row-skipped", "Section 4a of %s has %d malformed row(s), which are skipped (line %s)"
                 % (source, len(grouped["errors"]), ", ".join(str(problem["line"]) for problem in grouped["errors"][:5])))
    run.groups = grouped["groups"]
    run.assignments = sc.correlation_assignments([(group["group_id"], group["members"]) for group in run.groups], open_ids)

    for finding_id, tags in sc.parse_affected_assets(text).items():   # copied as the block has them, matched by finding ID (sarif-specification.md)
        if tp.id_matches("finding", finding_id):
            run.affected.setdefault(tp.canonical_finding_id(finding_id), tags)
    baseline = tachi_parsers.parse_baseline_frontmatter(text)
    run.aware, run.baseline_run_id = bool(baseline["has_baseline"]), baseline["run_id"]

    for finding in reference["open"]:   # NFR-10: a value from the input is checked where it is taken, before anything is built from it
        canonical = tp.canonical_finding_id(finding["id"])
        _refuse(source, finding["id"], {name: finding.get(name) for name in COPIED_FIELDS})
        _refuse(source, finding["id"], {"affected_assets": run.affected.get(canonical, [])})
    for canonical, layer in run.finding_layer.items():
        _refuse(source, canonical, {"layer": layer})
    _refuse(source, None, (run.component_info, run.component_zone))
    if run.baseline_run_id is not None:
        _refuse(source, None, run.baseline_run_id, place=lambda char: "the baseline run ID in its frontmatter")
    return reference


# =============================================================================
# The results, the rules and the file
# =============================================================================

def _result(run: Run, finding: Mapping[str, Any]) -> Dict[str, Any]:
    """One result for one open finding, through the shared emitter (D7, D8).

    ``properties`` hold exactly the keys that this file's own contract names (S1P-A28): ``tags``, ``maestro-layer``, ``severity``,
    ``baselineState`` and ``affected_assets``, then ``baseline-run-id`` where the threat model names a baseline run. The emitter adds the
    ``correlation-*`` keys and ruling C's sentence.
    """
    canonical = tp.canonical_finding_id(finding["id"])
    component = finding["component"] or PLACEHOLDER_COMPONENT
    info = run.component_info.get(component) or run.folded.get(component.casefold()) or ("", "")   # Section 1 lists a component by name, case-folded
    layer = run.finding_layer.get(canonical) or info[1] or "Unclassified"
    found = _LAYER.match(layer)
    tags = list(CATEGORY_TAGS[canonical.partition("-")[0]]) + ["maestro-layer:" + (found.group(0) if found else "Unclassified")]
    pattern = finding.get("agentic_pattern") or "none"
    if pattern != "none":   # ``multiple`` included
        tags.append("maestro-pattern:" + pattern)
    state = BASELINE_STATE.get(finding.get("delta_status"), "new") if run.aware else "new"
    properties: Dict[str, Any] = {"tags": tags, "maestro-layer": layer, "severity": finding["risk_level"], "baselineState": state,
                                  "affected_assets": list(run.affected.get(canonical, ()))}
    if run.baseline_run_id:
        properties["baseline-run-id"] = "" if state == "new" else run.baseline_run_id
    return sc.build_result(tool=TOOL, finding_id=finding["id"], message=finding["threat"] or PLACEHOLDER_THREAT, markdown=finding["mitigation"] or "",
                           level=sc.level_for_band(finding["risk_level"]), uri=run.uri, component=component,
                           zone=run.component_zone.get(component.casefold()) or "Application Zone", kind=KIND_OF_DFD_TYPE.get(info[0], "process"),
                           properties=properties, correlation=run.assignments.get(canonical))


def _rules(reference: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """The driver's rules: the shared table's rule for each category that has a result, with its ``security-severity`` taken from those results, and its ``help``."""
    highest: Dict[str, Decimal] = {}
    for finding in reference["open"]:
        category = ts.category_for_prefix(tp.canonical_finding_id(finding["id"]).partition("-")[0])
        value = SECURITY_SEVERITY.get(finding["risk_level"], DEFAULT_SEVERITY)
        highest[category] = max(highest.get(category, value), value)
    rules = []
    for rule in sc.build_rules(highest):
        text, markdown = RULE_HELP[CATEGORY_OF_RULE[rule["id"]]]
        # id, shortDescription, fullDescription, help, properties, relationships: the order of every shipped threats.sarif
        rules.append({"id": rule["id"], "shortDescription": rule["shortDescription"], "fullDescription": rule["fullDescription"],
                      "help": {"text": text, "markdown": markdown}, "properties": rule["properties"], "relationships": rule["relationships"]})
    return rules


def _build_parser() -> argparse.ArgumentParser:
    parser = tp.build_parser(RENDERER, "Generate threats.sarif from the compiled threats.md (F-374).", plan=False)
    parser.add_argument("--threats", required=True, help="the compiled threats.md that the file is generated from")
    parser.add_argument("--architecture", default=None,
                        help="the command's own path to the architecture file, a candidate for the URI that every result carries (ADR-050 D7)")
    return parser


def _run(args: argparse.Namespace) -> int:
    out = tp.directory_argument(STAGE, args.out)
    source = os.path.basename(args.threats)
    raw, text = _read_threats(args.threats, source)
    run = Run()
    reference = _prepare(run, text, source)

    # The architecture file: the one path that gives the URI (ADR-050 D7). The resolver takes the flag, then the body line, then the default.
    resolution = sc.resolve_architecture(args.architecture, threats_text=text, run_dir=os.path.dirname(os.path.abspath(args.threats)), root=run.cwd)
    run.uri = resolution.uri
    for found in resolution.warnings:
        run.warn(found["code"], found["detail"])

    results = [_result(run, finding) for finding in reference["open"]]
    digest = tp.input_digest({"sources": {"threats": tp.sha256_hex(raw)}, "params": {"architecture_uri": run.uri}})
    # ``semanticVersion`` is tachi's release version, the value that the provenance stamp carries (PM W3 ruling 2c, as for the other two files)
    driver = sc.build_driver(SARIF, semantic_version=tp.VERSION, rules=_rules(reference), supported=SUPPORTED_TAXONOMIES)
    document = sc.build_document(driver, TAXONOMIES, results, sc.provenance_stamp(RENDERER, tp.VERSION, digest), schema_first=True)

    try:   # D8's self-check, before any write: N results for N open findings, tachi's own hashes, one URI, no RESOLVED reference, ruling C's sentence
        sc.self_check(results, tool=TOOL, member_ids=[tp.canonical_finding_id(row["id"]) for row in reference["open"]], assignments=run.assignments,
                      resolved_ids=[row["id"] for row in reference["resolved"]], uri=run.uri)
    except sc.SelfCheckError as exc:
        raise tp.StageFailure(4, STAGE, "the SARIF fails its own self-check: %s" % "; ".join(exc.problems[:5]),
                              "correct what the check names in %s, or report this as a bug in %s; nothing was written" % (source, RENDERER)) from None
    offender = tp.first_forbidden(document)   # the backstop on every decoded string of the file, whatever path it took to reach it (NFR-10, P0-4)
    if offender is not None:
        raise tp.StageFailure(4, STAGE, "the SARIF holds the character U+%04X, which the part contract forbids, in %s" % (ord(offender[1]), ascii(offender[0])),
                              "report this as a bug in %s; nothing was written" % RENDERER)
    try:
        tp.atomic_write(os.path.join(out, SARIF), sc.to_json(document))
    except OSError as exc:
        raise tp.StageFailure(4, STAGE, "%s could not be written (%s)" % (SARIF, exc.strerror or "error"), tp.RETRY_REMEDY) from None

    for warning in run.warnings:
        sys.stderr.write("WARNING: %s: %s\n" % (warning["code"], warning["detail"]))
    sys.stdout.write(tp.dump_json({"architecture": run.uri, "input_digest": digest, "output": SARIF, "results": len(results),
                                   "warnings": [warning["code"] for warning in run.warnings]}))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    return tp.run_entry(stage=STAGE, renderer=RENDERER, args=_build_parser().parse_args(argv), run=_run)


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_runtime_floor_374.py, test_write_confinement.py)
    raise SystemExit(main())
