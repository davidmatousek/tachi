"""Goldens for ``scripts/render-compensating-controls.py``, written before the script (F-374 T034; TDD).

They target ``contracts/cli.md`` (the CLI and the exit table), ``contracts/part-files.md`` (the controls payload, the
stage record), ``contracts/module-signatures.md`` (the persisted-inputs format), ``contracts/sarif-result.md`` and
ADR-050 D2 (field ownership), D3 (escaping, slots), D4 (the write order, failure, the stamp, declared paths), D5
(arithmetic), D7 and D8 (SARIF identity and membership) and D15 (schema 1.1), never an implementation. T035 writes
the renderer to them. Until then they fail: the script does not exist. R-34's cell-by-cell goldens for Sections 2 and
4 (every cell D2 lists is filled, or its mismatch is flagged) are T056's, and go into this file after these. Here a
Section 2 cell is read by its header name and only for a finding whose agent row agrees with the input, and a
Section 4 block is read through the shipped reader, so nothing below restates or contradicts T056's cases.

How they run (ADR-050 D16, H15): the entry is loaded through ``tests/conftest.py``'s ``_load_hyphenated_script`` and
driven in-process through ``main(argv)``, so pytest-cov counts it. Nothing here starts a subprocess: the one thing a
process alone shows, the 3.9 refusal before any import, is ``test_runtime_floor_374.py``'s. The generic readers and the
synthetic reference set come from ``test_render_risk_scores.py`` (T027), which this module is modelled on. The plan is
made by ``tachi-stage.py``'s ``plan_stage`` with every pointer that ``contracts/cli.md`` lists for the stage
(``Project.plan`` is the one place to follow a change to the controls planner, T036).

What these goldens assume of ``render-compensating-controls.py`` (R2 follows them; where a contract left a form open
the test says ``# reading:``, or the docstring says so, and the architect rules it at integration):

1. **The CLI** is ``render-compensating-controls.py --out DIR --plan ID --plan-digest HEX`` with ``--help`` and
   ``--version`` (``contracts/cli.md``). ``main(argv=None) -> int``. The exit codes are the table's: 0 and 5 write both
   files, 1 is a missing input, 2 a validation or guard failure, 4 a failed completeness or parity check. The renderer
   never rewrites ``plan.json``. stdout carries summary lines, and a failure prints D4's
   ``TACHI COMPENSATING-CONTROLS FAILED:`` message.
2. **Where it reads.** The plan's ``params.scoring_date`` is the date, ``inputs.risk_scores`` is this run's
   ``risk-scores.md`` (the member set, and each finding's inherent score, which is its Composite cell and is never
   re-scored), ``refs.target`` is the scanned directory, and ``refs.architecture`` is the URI's candidate. The
   ``threats.md`` is the one that the input's frontmatter ``source_file`` names (relative to the working directory):
   it supplies the component, the threat, the MAESTRO layer, the zone and the DFD kind, and Section 4a's groups.
   The parts are the current plan's ``done`` batches, each re-validated with ``tachi_parts.read_part``.
3. **Where it writes.** Both files go to ``<plan>/staged/`` first (with ``tachi_parts.atomic_write``), are read back
   from disk and checked, and only then move onto the canonical names with ``os.replace``. The stage record is
   ``<plan>/stage-record.json``.
4. **The files.** ``compensating-controls.md`` is schema 1.1 with Sections 1 to 7, ending in the stamp comment, and
   ``compensating-controls.sarif`` is the shared emitter's file. The renderer's name in both stamps is the literal
   ``render-compensating-controls.py``, and the three digests (the two stamps and the stage record) are one value.
5. **The readings these goldens pin where the template is silent:**
   Section 2's header is K8's, ``Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent
   Severity | Control Status | Control Category | Residual Score | Residual Severity`` (``test_tachi_parsers.py``'s "agent
   spec order"); a finding's ID is spelled as Section 7 of ``threats.md`` spells it in Sections 2 and 4, so that the
   shipped reader joins them; a per-item ``{{pct:reduction}}`` is ``reduction_percentage(inherent, residual)``; the
   band-shift table's Examples cell names the finding IDs of its shift, and ``Change`` is the residual count less the
   inherent one; a Section 3 control's heading names its evidence entry's ``summary``; the SARIF result order is
   Section 2's; ``recommendation`` is the "What to Implement" text and
   ``effort-estimate`` the Effort word, both ``""`` for a found finding; ``control-carry-forward`` is a JSON boolean;
   ``message`` is ``{text}`` alone; and the zone and DFD kind of a result's logical location come from ``threats.md``
   as the scorer renderer takes them.

Expected values are literals (``GOLDEN``), and ``test_harness_the_literal_goldens_equal_the_shipped_arithmetic``
re-derives each from the shipped arithmetic (``tachi_scoring``), so a wrong number in a test fails there first.
Fixtures are synthetic (H8).

The groups of tests, by the task that turns them green:

* ``test_harness_*``: no renderer needed; they check the synthetic inputs and the literals.
* ``test_cli_*``: T035 (the entry, the exit table).
* ``test_md_*``: T035 (the file's sections and rows, Section 7), and T059 for Sections 2 and 4.
* ``test_sarif_*``: T035 and T053 (the shared emitter's file); ``test_corr_*``: one correlation group.
* ``test_agree_*`` and ``test_readers_*``: the ``.md``-``.sarif`` agreement and NFR-1's round trip.
* ``test_staged_*`` and ``test_failure_*``: D4's write order and the ``fail`` step (F2).
* ``test_record_*``: the stamp, the stage record and the declared-paths check.
* ``test_batching_*`` and ``test_determinism_*``: NFR-4 and NFR-2.
* ``test_narrative_*``: the slots, the per-field fallback, cuts and hostile text.
* ``test_template_*``: the 1.1 template and the renderer agree (D15). They skip until T060 (lane D) brings the
  template to 1.1, and then they pin it.

Standard library and pytest only, and Python 3.9 syntax.
"""
from __future__ import annotations

import ast
import contextlib
import copy
import datetime
import hashlib
import inspect
import io
import json
import math
import os
import re
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script
from .test_render_risk_scores import (
    COMPONENTS, DASH, DATE, DIGEST, KIND_OF, LOCAL_PATH, RESOLVED, RESOLVED_IDS, URI, ZONES, canon, decode, frozen_clock,
    has_section, invoke, make_architecture_md, make_threats_md, records, s2_key, section, section_text, sha256_of,
    split_headings, subsection_of, table_of, tables, tree_state, working_directory)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import sarif_common as sc  # noqa: E402  -- after the sys.path mutation
import tachi_parsers  # noqa: E402
import tachi_parts as tp  # noqa: E402
import tachi_scoring as ts  # noqa: E402
import tachi_scoring_rules as rules  # noqa: E402

STAGE = "compensating-controls"
MD, SARIF = "compensating-controls.md", "compensating-controls.sarif"
TOOL = "tachi-control-analyzer"
RENDERER = SCRIPTS_DIR / "render-compensating-controls.py"
# The stamp's renderer is the installed file name, with .py, as one literal in the markdown comment and in SARIF's
# tachi_provenance (cli.md "The stamp's renderer"); it matches INSTALL_MANIFEST.md and REQUIRED_SCRIPT_NAMES.
RENDERER_NAME = "render-compensating-controls.py"
FAILED = "TACHI COMPENSATING-CONTROLS FAILED:"
TEMPLATES = REPO_ROOT / "templates" / "tachi" / "output-schemas"
EARLIER_MD = b"# the earlier run's controls markdown\n"
EARLIER_SARIF = b'{"earlier": "controls run"}\n'

# =============================================================================
# 1. The synthetic project: eleven scored findings, their controls and their goldens
# =============================================================================
#
# Eleven open findings on five components, and the three RESOLVED ones of the scorer's project. They were chosen so
# that one render shows: all four inherent and all four residual bands, and every band shift of ADR-050 D2's table
# but Critical to Low; found, partial and missing results (four, four and three); seven residuals that end in a
# half before rounding (4.55, 3.65, 2.75, 4.85, 4.65, 3.45 and 7.05: half-even rounds five of them the other way
# and a float rounds four), a residual tie (S-10 and R-1) that S-2's order breaks, an inherent tie (T-4 and E-5) that does the same for the
# highest-risk unmitigated finding, a found finding with the highest inherent score of all (D-2, which must not be
# that finding), a reduction percentage of exactly 28.25, coverage and residual-band distributions whose last point
# goes to the label that sorts first, a leading-zero ID (AGP-01), one control that two findings share, one file and
# line under two categories, one category with two lines of one file, markup, a backtick and ``{{`` in the text, a
# backtick run inside a snippet, and non-ASCII text. Every threat is at most 60 characters and every component at most
# 30, so risk-scores.md's shortened cells read the same as the reference set's full text, and no source of the
# component or the threat can differ.

K8_HEADER = ["Threat ID", "CF", "Component", "MAESTRO Layer", "Threat", "Inherent Score", "Inherent Severity", "Control Status",
             "Control Category", "Residual Score", "Residual Severity"]
STATUS_CELL = {"found": "Control Found", "partial": "Partial Control", "missing": "No Control Found"}
STATUS_CLASS = {"found": "found", "partial": "partial", "missing": "none"}  # classify_control_status's names
CONTROL_CATEGORY_NAME = {
    "authentication": "Authentication", "access-control": "Access Control", "input-validation": "Input Validation",
    "encryption": "Encryption", "rate-limiting": "Rate Limiting", "logging-audit": "Logging/Audit",
    "csrf-protection": "CSRF Protection", "csp-security-headers": "CSP/Security Headers"}
CATEGORY_ORDER = tuple(CONTROL_CATEGORY_NAME)  # the template's order of Section 3's categories
EFFECTIVENESS = {"found": "strong", "partial": "moderate", "missing": "none"}  # P0, derived from the status
SECTION_TITLES = ["## 1. Executive Summary", "## 2. Coverage Matrix", "## 3. Control Details", "## 4. Recommendations",
                  "## 5. Residual Risk Summary", "## 6. Methodology", "## 7. Analysis Integrity"]
BANDS = ("Critical", "High", "Medium", "Low")

HOSTILE_THREAT = "Untrusted <b>x</b> and `tick` and {{7*7}} reach the model."
HOSTILE_WHAT = "Check the role claim before every admin route <b>and</b> log each denied `attempt` & alert."

ASSESSMENT = {  # narrative, so digits only through slots (ADR-050 D3's table for this stage)
    "coverage": {"rating": "High", "rationale": "Validation covers {{count:evidence}} entry point of {{name:component}}."},
    "configuration": {"rating": "Medium", "rationale": "Strict mode is on, so risk falls from {{score:inherent}} to {{score:residual}}."},
    "currency": {"rating": "Medium", "rationale": "Maintained code: the {{band:inherent}} finding drops to {{band:residual}}."},
    "completeness": {"rating": "Low", "rationale": "A reduction of {{pct:reduction}} percent still leaves the batch endpoints open."},
}


def evidence(file, line, summary, snippet, language="python", assessment=None):
    return {"file": file, "line": line, "language": language, "snippet": snippet, "summary": summary, "assessment": assessment}


TOKENS = evidence("src/auth/tokens.py", 42, "Token verification at the gateway entry point.",
                  "def verify_token(token):\n    return check_signature(token)")
SESSION = evidence("src/auth/session.py", 88, "Session expiry is checked before every request.",
                   "if session.expired():\n    raise SessionExpired()")
SCHEMA_INPUT = evidence("src/validate/schema.py", 17, "Request bodies are validated against a strict schema.",
                        "schema = Schema(strict=True)\nschema.validate(body)", assessment=ASSESSMENT)
SCHEMA_ROLE = evidence("src/validate/schema.py", 17, "The schema module also rejects bodies from the wrong role.",
                       "schema.require_role(body, role)")
GUARD = evidence("src/access/guard.py", 30, "Role guard on the worker message handler.", "@require_role('worker')\ndef handle(message):")
BUCKET_A = evidence("src/limits/bucket.py", 12, "Per-client token bucket on the planner endpoint.", "bucket = TokenBucket(rate=5)")
BUCKET_B = evidence("src/limits/bucket.py", 58, "The bucket refills on a fixed timer.", "timer.every(1, bucket.refill)")
POOL = evidence("src/limits/pool.py", 21, "The connection pool is capped for each caller.", "pool = Pool(max_per_caller=4)")
TLS = evidence("src/crypto/tls.py", 9, "Calls <script>alert(1)</script> before the TLS check.",
               'cfg = "```"  # a run of backticks inside code\nverify(cfg)')


def recommendation(what, where, patterns, effort, why):
    return {"what": what, "where": where, "patterns": patterns, "effort": effort, "why": why}


def finding(finding_id, component, threat, risk, inherent, control, category, confidence, items=(), rec=None):
    """One synthetic scored finding. ``status`` is the reference set's delta status, ``control`` the agent's judgment."""
    return {"id": finding_id, "component": component, "threat": threat, "risk": risk, "status": "NEW", "inherent": inherent,
            "control": control, "category": category, "confidence": confidence, "evidence": list(items), "rec": rec}


FINDINGS = [
    finding("S-2", "edge-gateway", "Shared tokens let callers impersonate each other.", "High", "9.1", "found", "authentication", "High", [TOKENS]),
    finding("T-1", "auth-broker", "Backups of session grants are writable by operators.", "High", "7.3", "found", "input-validation",
            "Medium", [SCHEMA_INPUT]),
    finding("S-10", "auth-broker", "Étienne's token is long-lived and shared across services.", "Medium", "5.5", "found",
            "authentication", "High", [TOKENS, SESSION]),
    finding("D-2", "vector-store", "Bulk reads exhaust the store's connection pool.", "Medium", "9.7", "found", "rate-limiting", "Low", [POOL]),
    finding("AGP-01", "vector-store", "Worker agents accept each other's instructions unchecked.", "High", "8.4", "partial",
            "access-control", "Medium", [GUARD],
            recommendation("Extend the role guard to the retry path of the worker bus.", "src/access/guard.py, the retry handler",
                           "Deny by default, with one guard for each message type.", "Low", "one more decorator")),
    finding("LLM-4", "planner-agent", HOSTILE_THREAT, "Medium", "6.2", "partial", "access-control", "Low", [GUARD, SCHEMA_ROLE],
            recommendation("Reject model output that names a tool outside the allow list.", "src/validate/schema.py, the output check",
                           "An allow list with schema validation.", "Medium", "a new check and its tests")),
    finding("AG-1", "planner-agent", "Memory entries written by the planner are trusted later.", "Medium", "4.6", "partial",
            "rate-limiting", "Medium", [BUCKET_A, BUCKET_B],
            recommendation("Expire planner memory entries and verify their origin before reuse.", "src/limits/bucket.py, the memory reader",
                           "Signed entries with a time to live.", "High", "the memory format changes")),
    finding("T-4", "auth-broker", "Session grants can be altered in transit between hops.", "High", "9.4", "partial", "encryption", "High", [TLS],
            recommendation("Pin the TLS version and verify the peer on every internal hop.", "src/crypto/tls.py, the client factory",
                           "Mutual TLS between the broker and the gateway.", "Medium", "one client factory changes")),
    finding("E-5", "client-portal", "Role claims are trusted without a second check.", "Critical", "9.4", "missing", "access-control", None, [],
            recommendation("Re-check the role claim against the directory before each admin action.", "src/access/directory.py",
                           "A central policy decision point.", "High", "a new service call on every admin path")),
    finding("E-3", "edge-gateway", "Admin routes skip the role check.", "High", "7.6", "missing", "access-control", None, [],
            recommendation(HOSTILE_WHAT, "src/gateway/admin.py", "Middleware for each route group.", "Low", "one middleware")),
    finding("R-1", "planner-agent", "Portal actions are logged without the acting identity.", "Low", "2.8", "missing", "logging-audit", None, [],
            recommendation("Record the acting identity with every action taken through the portal.", "src/audit/log.py",
                           "Structured audit events with a subject field.", "Medium", "the event schema grows")),
]
BY_ID = {canon(item["id"]): item for item in FINDINGS}
OPEN_IDS = [item["id"] for item in FINDINGS]

# What the renderer computes: (inherent, inherent band, P0 reduction factor, residual, residual band). Derived by hand from
# the contract (``q1(inherent * (1 - factor))``, half up), and re-derived from the shipped arithmetic by the first harness test.
GOLDEN = {
    "S-2": ("9.1", "Critical", "0.50", "4.6", "Medium"),     # 4.55: a float rounds it down to 4.5
    "T-1": ("7.3", "High", "0.50", "3.7", "Low"),            # 3.65: half-even and a float round it down
    "S-10": ("5.5", "Medium", "0.50", "2.8", "Low"),         # 2.75, tied with R-1
    "D-2": ("9.7", "Critical", "0.50", "4.9", "Medium"),     # 4.85: half-even and a float round it down
    "AGP-01": ("8.4", "High", "0.25", "6.3", "Medium"),      # 6.3 exactly
    "LLM-4": ("6.2", "Medium", "0.25", "4.7", "Medium"),     # 4.65: half-even rounds it down
    "AG-1": ("4.6", "Medium", "0.25", "3.5", "Low"),         # 3.45: half-even rounds it down
    "T-4": ("9.4", "Critical", "0.25", "7.1", "High"),       # 7.05: half-even and a float round it down
    "E-5": ("9.4", "Critical", "0.00", "9.4", "Critical"),
    "E-3": ("7.6", "High", "0.00", "7.6", "High"),
    "R-1": ("2.8", "Low", "0.00", "2.8", "Low"),             # tied with S-10
}
HALF_CASES = ("S-2", "T-1", "S-10", "D-2", "LLM-4", "AG-1", "T-4")  # the residuals that end in a half before rounding
RESIDUAL_ORDER = ["E-5", "E-3", "T-4", "AGP-01", "D-2", "LLM-4", "S-2", "T-1", "AG-1", "S-10", "R-1"]  # residual descending, then S-2
S2_ORDER = ["S-2", "S-10", "T-1", "T-4", "R-1", "D-2", "E-3", "E-5", "AG-1", "AGP-01", "LLM-4"]
RECOMMENDED = ["T-4", "E-5", "AGP-01", "E-3", "LLM-4", "AG-1", "R-1"]  # partial and missing: inherent descending, then S-2
RESIDUAL_BANDS = {"Critical": ["E-5"], "High": ["E-3", "T-4"], "Medium": ["AGP-01", "D-2", "LLM-4", "S-2"],
                  "Low": ["T-1", "AG-1", "S-10", "R-1"]}
TOTAL_INHERENT, TOTAL_RESIDUAL, DELTA, REDUCTION = "80.0", "57.4", "22.6", "28.3"  # 22.6 / 80.0 = 28.25 exactly: a tie
COVERAGE = {"found": 4, "partial": 4, "missing": 3}
COVERAGE_PCT = {"found": 37, "partial": 36, "missing": 27}  # 36.36, 36.36 and 27.27: the last point goes to "found", which sorts first
INHERENT_COUNTS = {"Critical": 4, "High": 3, "Medium": 3, "Low": 1}
RESIDUAL_COUNTS = {"Critical": 1, "High": 2, "Medium": 4, "Low": 4}
RESIDUAL_PCT = {"Critical": 9, "High": 18, "Medium": 36, "Low": 37}  # the last point goes to "Low", which sorts before "Medium"
SHIFTS = {  # "inherent band -> residual band": the findings that moved, in S-2 order
    "Critical -> High": ["T-4"], "Critical -> Medium": ["S-2", "D-2"], "Critical -> Low": [], "High -> Medium": ["AGP-01"],
    "High -> Low": ["T-1"], "Medium -> Low": ["S-10", "AG-1"], "No Shift": ["R-1", "E-3", "E-5", "LLM-4"]}
HIGHEST_UNMITIGATED = "T-4"  # T-4 and E-5 tie at 9.4, and S-2's order puts T-4 first; D-2 (9.7) is found
GROUPS = [("CG-1", ["S-2", "S-10"])]  # Section 4a: S-2 is listed first, so it is the primary and S-10 its peer

# Section 3: one control for each distinct (category, file, line), and the findings it mitigates.
CONTROLS = [
    ("authentication", "src/auth/tokens.py", 42, ["S-2", "S-10"]),
    ("authentication", "src/auth/session.py", 88, ["S-10"]),
    ("access-control", "src/access/guard.py", 30, ["AGP-01", "LLM-4"]),
    ("access-control", "src/validate/schema.py", 17, ["LLM-4"]),
    ("input-validation", "src/validate/schema.py", 17, ["T-1"]),
    ("encryption", "src/crypto/tls.py", 9, ["T-4"]),
    ("rate-limiting", "src/limits/pool.py", 21, ["D-2"]),
    ("rate-limiting", "src/limits/bucket.py", 12, ["AG-1"]),
    ("rate-limiting", "src/limits/bucket.py", 58, ["AG-1"]),
]
EVIDENCE_ENTRIES = 11  # before the two shared entries collapse into one control each (tokens.py:42 and guard.py:30)


def golden(finding_id):
    return GOLDEN[next(key for key in GOLDEN if canon(key) == canon(finding_id))]


def by_id(finding_id, findings=None):
    if findings is None:
        return BY_ID[canon(finding_id)]
    return next(item for item in findings if canon(item["id"]) == canon(finding_id))


def residual_of(item):
    return ts.residual_score(Decimal(item["inherent"]), ts.REDUCTION_FACTOR_P0[item["control"]])


# --------------------------------------------------------------------------- the agent's part


def evidence_entry(entry):
    out = {key: entry[key] for key in ("file", "line", "language", "snippet", "summary")}
    if entry["assessment"]:
        out["assessment"] = copy.deepcopy(entry["assessment"])
    return out


def body_of(item):
    rec = item["rec"]
    return "\n\n".join(["**What to Implement**: " + rec["what"], "**Where to Implement**: " + rec["where"],
                        "**Reference Patterns**: " + rec["patterns"], "**Effort Estimate**: %s %s %s" % (rec["effort"], DASH, rec["why"])])


def matrix_cells(item):
    """The agent's own Section 2 row: its judgment in the text cells, and a slot token in each computed cell."""
    return [item["id"], DASH, item["component"], COMPONENTS[item["component"]][1], item["threat"], "{{score:inherent}}", "{{band:inherent}}",
            STATUS_CELL[item["control"]], CONTROL_CATEGORY_NAME[item["category"]], "{{score:residual}}", "{{band:residual}}"]


def matrix_row_of(item):
    return "| " + " | ".join(matrix_cells(item)) + " |"


def controls_item(item):
    """One valid ``compensating-controls`` item (``contracts/part-files.md``) for a synthetic finding."""
    return {
        "finding_id": item["id"], "control_status": item["control"], "control_category": item["category"],
        "confidence": item["confidence"], "carried_forward": False, "evidence": [evidence_entry(entry) for entry in item["evidence"]],
        "matrix_row": matrix_row_of(item), "recommendation_body": None if item["control"] == "found" else body_of(item),
    }


def lookup_for(item):
    """The slot lookup the renderer must give a finding: this item's rendered values (ADR-050 D3's table)."""
    inherent, inherent_band, _factor, residual, residual_band = golden(item["id"])
    values = {("score", "inherent"): inherent, ("score", "residual"): residual, ("band", "inherent"): inherent_band,
              ("band", "residual"): residual_band, ("count", "evidence"): str(len(item["evidence"])),
              ("pct", "reduction"): str(ts.reduction_percentage(Decimal(inherent), Decimal(residual))), ("name", "component"): item["component"]}
    return lambda kind, argument: values.get((kind, argument))


def narrative(item, text, sink="cell"):
    """What the renderer writes for a narrative field of ``item``: the slots filled, then escaped."""
    return tp.resolve_narrative(text, STAGE, lookup_for(item), sink=sink)


def effort_of(body):
    return re.search(r"\*\*Effort Estimate\*\*: (Low|Medium|High)\b", body).group(1)


def what_of(body):
    return re.search(r"\*\*What to Implement\*\*: (.*)", body).group(1)


# --------------------------------------------------------------------------- the inputs: risk-scores.md, the target


def make_risk_scores_md(findings=None, resolved=None, source="run/threats.md", date=DATE, scores=None):
    """A ``risk-scores.md`` the way the scorer renderer writes it: frontmatter, Section 2 (cells shortened and escaped),
    Section 2a, and one Section 3 heading for each finding. ``scores`` replaces a finding's four sub-scores (a default
    of the composite itself, so the row's arithmetic holds); the composite is always the finding's inherent score."""
    findings = FINDINGS if findings is None else findings
    resolved = RESOLVED if resolved is None else resolved
    scores = scores or {}
    lines = ["---", 'schema_version: "1.1"', 'date: "%s"' % date, 'source_file: "%s"' % source, 'classification: "confidential"',
             "scoring_weights:", "  cvss_base: 0.35", "  exploitability: 0.30", "  scalability: 0.15", "  reachability: 0.20", "baseline:",
             "  source: null", "  inherited_count: null", "  fresh_count: null", "---", "", "# Risk Scores Report", "",
             "## 1. Executive Summary", "", "%d open findings were scored on %s." % (len(findings), date), "", "---", "",
             "## 2. Scored Threat Table", "",
             "| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Flags |",
             "|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|-------|"]
    for item in sorted(findings, key=lambda each: (-Decimal(each["inherent"]), s2_key(each["id"]))):
        band = ts.band(Decimal(item["inherent"]))
        cells = scores.get(canon(item["id"]), [item["inherent"]] * 4)
        lines.append("| %s | fresh | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            item["id"], tp.escape_cell(item["component"]), tp.escape_cell(item["threat"]), cells[0], cells[1], cells[2], cells[3],
            item["inherent"], band, ts.SEVERITY_BANDS[band]["sla"], ts.SEVERITY_BANDS[band]["disposition"], DASH))
    lines.append("")
    if resolved:
        lines += ["---", "", "## 2a. Resolved Findings", "",
                  "| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Status | Owner | Review Date | Flags |",
                  "|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|--------|-------|-------------|-------|"]
        lines += ["| %s | inherited | %s | %s | %s | RESOLVED | %s | %s | resolved |" % (
            finding_id, component, threat, " | ".join([DASH] * 8), DASH, DASH) for finding_id, component, threat, _risk, _why in resolved]
        lines.append("")
    lines += ["---", "", "## 3. Dimensional Breakdown", ""]
    for item in sorted(findings, key=lambda each: (-Decimal(each["inherent"]), s2_key(each["id"]))):
        band = ts.band(Decimal(item["inherent"]))
        lines += ["### %s %s %s" % (item["id"], DASH, tp.escape_prose(item["component"])), "", "**Threat**: %s" % tp.escape_prose(item["threat"]), "",
                  "**Category**: %s | **Original Risk Level**: %s | **Composite**: %s (%s)" % (
                      ts.category_for_prefix(item["id"].partition("-")[0]), item["risk"], item["inherent"], band), "", "---", ""]
    return "\n".join(lines) + "\n"


def evidence_files(findings):
    """``{path: line count}`` of the files in the target that the findings' evidence names."""
    found = {}
    for item in findings:
        for entry in item["evidence"]:
            found[entry["file"]] = max(found.get(entry["file"], 0), entry["line"] + 20)
    return found


# =============================================================================
# 2. Reading the output
# =============================================================================


def cell_number(cell):
    """A table cell as a ``Decimal``: bold markers, a percent sign and a Unicode or ASCII sign are read, nothing else."""
    text = re.sub(r"[*%]", "", cell).replace("−", "-").replace("+", "").strip()
    return Decimal(text)


def band_tables(md):
    """``[(band, header, [row dict])]`` for Section 2's residual-band tables, in file order."""
    found = []
    for heading, body in split_headings(section_text(md, "## 2. Coverage Matrix"), "### "):
        match = re.fullmatch(r"### (Critical|High|Medium|Low) Residual Severity", heading)
        if match:
            header, rows = table_of(body, "Threat ID")
            found.append((match.group(1), header, records(header, rows)))
    return found


def matrix_rows(md):
    """``{canonical ID: (band, row dict)}`` for every Section 2 row."""
    out = {}
    for band, _header, rows in band_tables(md):
        for row in rows:
            assert canon(row["Threat ID"]) not in out, "a finding is in Section 2 twice: %s" % row["Threat ID"]
            out[canon(row["Threat ID"])] = (band, row)
    return out


def control_blocks(md):
    """``[(category heading, control heading, body)]`` for every control of Section 3, in file order."""
    found = []
    for category, body in split_headings(section_text(md, "## 3. Control Details"), "### "):
        for heading, block in split_headings(category + "\n" + body, "#### "):
            found.append((category[len("### "):], heading, block))
    return found


def recommendation_blocks(md):
    """``{canonical ID: block text}`` for each ``#### n. ID`` block of Section 4, wherever its group heading is."""
    found = {}
    for heading, body in split_headings(section_text(md, "## 4. Recommendations"), "#### "):
        match = re.match(r"#### \d+\. (\S+) " + DASH + " ", heading)
        assert match, "a Section 4 block heading is not '#### n. ID %s Component (...)': %r" % (DASH, heading)
        assert canon(match.group(1)) not in found, "Section 4 has two blocks for %s" % match.group(1)
        found[canon(match.group(1))] = heading + "\n" + body
    return found


def read_findings(md):
    """``{canonical ID: row}`` from the shipped reader, which keys a row by the spelling of its Section 2 cell."""
    return {canon(row["id"]): row for row in tachi_parsers.parse_compensating_controls_md(md)["findings"]}


def frontmatter_value(md, key):
    match = re.search(r"(?m)^%s:[ \t]*(.*?)[ \t]*$" % re.escape(key), md)
    assert match, "no %s in the frontmatter" % key
    return match.group(1).strip('"')


def raw_row(md, title, first_cell):
    """The raw line of the row in ``title`` whose first cell is ``first_cell``."""
    for line in section(md, title).split("\n"):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0] == first_cell:
            return line
    raise AssertionError("no row %r in %s" % (first_cell, title))


def results_by_id(doc):
    return {result["partialFingerprints"]["findingId/v1"]: result for result in doc["runs"][0]["results"]}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def label_ids(cell):
    return sorted(canon(found) for found in re.findall(r"\b[A-Z]{1,3}-\d+\b", cell))


def expected_assessment_inputs(findings):
    """Section 7's ``### Assessment Inputs`` rows (``contracts/module-signatures.md``): one for each value that exists, in S-2
    order of ID and then the payload's key order, escaped on write and shown here decoded."""
    rows = []
    for item in sorted(findings, key=lambda each: s2_key(each["id"])):
        part = controls_item(item)
        finding_id = item["id"]
        for name in ("control_status", "control_category"):
            rows.append((finding_id, name, part[name]))
        if part["confidence"] is not None:
            rows.append((finding_id, "confidence", part["confidence"]))
        rows.append((finding_id, "carried_forward", "true" if part["carried_forward"] else "false"))
        for index, entry in enumerate(part["evidence"]):
            rows += [(finding_id, "evidence.%d.%s" % (index, name), str(entry[name])) for name in ("file", "line", "language", "snippet", "summary")]
            for dimension in tp.ASSESSMENT_DIMENSIONS if "assessment" in entry else ():
                rows += [(finding_id, "evidence.%d.assessment.%s.%s" % (index, dimension, key), entry["assessment"][dimension][key])
                         for key in ("rating", "rationale")]
        rows.append((finding_id, "matrix_row", part["matrix_row"]))
        if part["recommendation_body"] is not None:
            rows.append((finding_id, "recommendation_body", part["recommendation_body"]))
    return rows


# =============================================================================
# 3. The harness
# =============================================================================


def assert_failure_message(res, plan_id=None):
    """D4's failure message: the first line names the stage, then the remedy and where the plan was kept."""
    assert res.err.startswith(FAILED) or "\n" + FAILED in res.err, res.describe()
    assert "Remedy:" in res.err, res.describe()
    if plan_id is not None:
        assert re.search(r"Kept for diagnosis: .*%s" % re.escape(plan_id), res.err), res.describe()


@pytest.fixture(scope="module")
def stage():
    return _load_hyphenated_script("tachi_stage_for_controls_tests", "tachi-stage.py")


@pytest.fixture(scope="module")
def renderer():
    if not RENDERER.is_file():
        pytest.fail("scripts/render-compensating-controls.py does not exist yet: T035 writes it to these goldens (TDD)", pytrace=False)
    return _load_hyphenated_script("render_compensating_controls_under_test", "render-compensating-controls.py")


class Project(object):
    """One synthetic project: a working directory, an architecture file, a target codebase, and a run directory that holds
    the reference set (``threats.md``) and this run's ``risk-scores.md``, the controls stage's input."""

    def __init__(self, stage_module, renderer_module, root, findings=None, resolved=None, groups=(), risk_scores_text=None, **threats_options):
        self.stage, self.renderer = stage_module, renderer_module
        self.root = Path(root)
        self.out = self.root / "run"
        self.architecture = self.root / "docs" / "security" / "architecture.md"
        self.threats = self.out / "threats.md"
        self.risk_scores = self.out / "risk-scores.md"
        self.target = self.root / "target"
        self.findings = list(FINDINGS if findings is None else findings)
        self.resolved = list(RESOLVED if resolved is None else resolved)
        self.plan_id = self.digest = None
        self.plan_stderr = ""
        self.last = None
        self.architecture.parent.mkdir(parents=True)
        self.out.mkdir(parents=True)
        self.architecture.write_text(make_architecture_md(), encoding="utf-8")
        self.threats.write_text(make_threats_md(self.findings, self.resolved, groups=groups, **threats_options), encoding="utf-8")
        self.risk_scores.write_text(make_risk_scores_md(self.findings, self.resolved) if risk_scores_text is None else risk_scores_text, encoding="utf-8")
        self.target.mkdir(parents=True, exist_ok=True)
        for path, lines in evidence_files(self.findings).items():
            (self.target / path).parent.mkdir(parents=True, exist_ok=True)
            (self.target / path).write_text("".join("# line %d of %s\n" % (number, path) for number in range(1, lines + 1)), encoding="utf-8")

    # ---- layout
    @property
    def plan_dir(self):
        return Path(tp.plan_dir(self.out, STAGE, self.plan_id))

    def read_json(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def plan_json(self):
        return self.read_json(self.plan_dir / "plan.json")

    def batches(self):
        return {entry["batch_id"]: entry for entry in self.plan_json()["batches"]}

    def batch_input(self, batch_id):
        return self.read_json(tp.input_path(self.out, STAGE, self.plan_id, batch_id))

    # ---- earlier outputs
    def earlier(self):
        (self.out / MD).write_bytes(EARLIER_MD)
        (self.out / SARIF).write_bytes(EARLIER_SARIF)

    def assert_earlier_outputs_untouched(self):
        assert (self.out / MD).read_bytes() == EARLIER_MD
        assert (self.out / SARIF).read_bytes() == EARLIER_SARIF

    # ---- plan, parts, reconcile
    def plan(self, batch_size=None, date=DATE, architecture=True, baseline_dir=None):
        """The planner through its function interface, as ``test_tachi_stage.py`` calls it (ADR-050 D6).

        The call passes every pointer that ``contracts/cli.md`` lists for the stage: ``--threats``, ``--risk-scores``,
        ``--architecture``, ``--target`` and ``--baseline-dir``. (T036 moves the controls planner's units to
        ``risk-scores.md``; the goldens here run against either, because both name the same eleven findings.)
        """
        err = io.StringIO()
        explicit = self.architecture if architecture is True else (architecture or None)
        with working_directory(self.root), contextlib.redirect_stderr(err):
            result = self.stage.plan_stage(stage=STAGE, out=self.out, date=date, threats=self.threats, risk_scores=self.risk_scores,
                                           architecture=explicit, target=self.target, baseline_dir=baseline_dir, batch_size=batch_size)
        self.plan_stderr = err.getvalue()
        self.plan_id, self.digest = result["plan_id"], result["plan_digest"]
        return result

    def part_for(self, batch_id, mutate=None):
        bi = self.batch_input(batch_id)
        part = {"schema": "tachi.part/1", "plan_id": bi["plan_id"], "batch_id": bi["batch_id"], "stage": bi["stage"],
                "agent_type": bi["agent_type"], "finding_ids": list(bi["finding_ids"]),
                "items": [controls_item(by_id(finding_id, self.findings)) for finding_id in bi["finding_ids"]], "fragments": []}
        if mutate is not None:
            mutate(part)
        return part

    def write_part(self, batch_id, mutate=None, raw=None):
        path = Path(self.batch_input(batch_id)["part_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            path.write_bytes(raw)
        else:
            path.write_text(json.dumps(self.part_for(batch_id, mutate)), encoding="utf-8")
        return path

    def write_parts(self, only=None, mutate=None):
        for batch_id, entry in self.batches().items():
            if entry["state"] != "split" and (only is None or batch_id in only):
                self.write_part(batch_id, mutate)

    def reconcile(self):
        res = invoke(self.stage, ["reconcile", "--stage", STAGE, "--out", self.out, "--plan", self.plan_id, "--plan-digest", self.digest], self.root)
        if res.code in (0, 3, 4):
            self.digest = json.loads(res.out)["plan_digest"]
        return res

    def prepare(self, batch_size=None, date=DATE, mutate=None, architecture=True, baseline_dir=None):
        """Plan, write a valid part for every batch and reconcile to complete (the command's Steps 2 to 4)."""
        self.plan(batch_size, date, architecture, baseline_dir)
        self.write_parts(mutate=mutate)
        res = self.reconcile()
        assert res.code == 0, res.describe()

    def render(self, *extra):
        self.last = invoke(self.renderer, ["--out", self.out, "--plan", self.plan_id, "--plan-digest", self.digest, *extra], self.root)
        return self.last

    def run(self, batch_size=None, date=DATE, mutate=None, architecture=True, baseline_dir=None):
        self.prepare(batch_size, date, mutate, architecture, baseline_dir)
        return self.render()

    def fail(self, reason="check-failed", detail=None):
        extra = ["--detail", detail] if detail is not None else []
        return invoke(self.stage, ["fail", "--stage", STAGE, "--out", self.out, "--plan", self.plan_id, "--plan-digest", self.digest,
                                   "--reason", reason, *extra], self.root)

    # ---- what the render wrote
    @property
    def md(self):
        return (self.out / MD).read_text(encoding="utf-8")

    @property
    def sarif_text(self):
        return (self.out / SARIF).read_text(encoding="utf-8")

    @property
    def sarif(self):
        return json.loads(self.sarif_text)

    @property
    def record(self):
        return self.read_json(tp.stage_record_path(self.out, STAGE, self.plan_id))

    def outputs(self):
        return {name: ((self.out / name).read_bytes() if (self.out / name).exists() else None) for name in (MD, SARIF)}


@pytest.fixture(scope="module")
def base(stage, renderer, tmp_path_factory):
    """One clean render of the eleven-finding project, shared by the read-only goldens below."""
    project = Project(stage, renderer, tmp_path_factory.mktemp("base"))
    res = project.run()
    assert res.code in (0, 5), "the base render must finish for the goldens below to read it:\n" + res.describe()
    return project


@pytest.fixture
def project(stage, renderer, tmp_path):
    return Project(stage, renderer, tmp_path)


@contextlib.contextmanager
def watching_replace(log):
    """Record every ``os.replace(src, dst)`` as ``(absolute src, absolute dst, staged names then present, src's sha256)``."""
    real = os.replace

    def replace(src, dst, *args, **kwargs):
        source, destination = os.path.abspath(str(src)), os.path.abspath(str(dst))
        present = [name for name in (MD, SARIF) if os.path.exists(os.path.join(os.path.dirname(source), name))]
        seen = hashlib.sha256(Path(source).read_bytes()).hexdigest() if os.path.isfile(source) else None
        log.append((source, destination, present, seen))
        return real(src, dst, *args, **kwargs)

    os.replace = replace
    try:
        yield
    finally:
        os.replace = real


@contextlib.contextmanager
def tampering_with_staged(name, edit):
    """While active, the staged file ``name`` is edited on disk right after the renderer writes it.

    The renderer then reads it back from disk (ADR-050 D4), so this is a seeded renderer bug that only a from-disk check
    can see. It hooks ``os.replace``, which ``tachi_parts.atomic_write`` ends with (reading: the renderer stages with it).
    A seed that could not be planted (the text has no such row, or the file was never staged) fails the test here, and
    never passes for a check that caught it.
    """
    real = os.replace
    planted, failures = [], []

    def replace(src, dst, *args, **kwargs):
        result = real(src, dst, *args, **kwargs)
        destination = str(dst)
        if os.path.basename(destination) == name and (os.sep + "staged" + os.sep) in destination:
            text = Path(destination).read_text(encoding="utf-8")
            try:
                edited = edit(text)
            except Exception as exc:  # an edit that finds nothing to change must not look like a renderer that failed a check
                failures.append(exc)
                return result
            if edited == text:
                failures.append(AssertionError("the seeded edit changed nothing"))
            Path(destination).write_text(edited, encoding="utf-8")
            planted.append(destination)
        return result

    os.replace = replace
    try:
        yield
    finally:
        os.replace = real
    assert planted and not failures, "the seeded bug was not planted in the staged %s: %r" % (name, failures)


@contextlib.contextmanager
def failing_replace(name):
    """While active, moving a staged file onto the canonical name ``name`` fails with an I/O error."""
    real = os.replace

    def replace(src, dst, *args, **kwargs):
        if os.path.basename(str(dst)) == name and (os.sep + "staged" + os.sep) in str(src) and (os.sep + "staged" + os.sep) not in str(dst):
            raise OSError(5, "Input/output error")
        return real(src, dst, *args, **kwargs)

    os.replace = replace
    try:
        yield
    finally:
        os.replace = real


# =============================================================================
# 4. Harness checks: no renderer needed
# =============================================================================


def test_harness_the_literal_goldens_equal_the_shipped_arithmetic():
    """The expectations below are literals, so this is where a wrong number is caught: each one is re-derived."""
    assert sorted(GOLDEN) == sorted(item["id"] for item in FINDINGS)
    inherent_total = residual_total = Decimal("0.0")
    for item in FINDINGS:
        inherent, inherent_band, factor, residual, residual_band = GOLDEN[item["id"]]
        assert (inherent, ts.band(Decimal(inherent))) == (item["inherent"], inherent_band), item["id"]
        assert Decimal(factor) == ts.REDUCTION_FACTOR_P0[item["control"]], "the P0 factor of %s" % item["control"]
        assert (str(residual_of(item)), ts.band(residual_of(item))) == (residual, residual_band), item["id"]
        inherent_total += Decimal(inherent)
        residual_total += Decimal(residual)
    assert (str(inherent_total), str(residual_total), str(inherent_total - residual_total)) == (TOTAL_INHERENT, TOTAL_RESIDUAL, DELTA)
    assert str(ts.reduction_percentage(inherent_total, residual_total)) == REDUCTION
    coverage = {status: sum(1 for item in FINDINGS if item["control"] == status) for status in COVERAGE}
    assert coverage == COVERAGE and ts.largest_remainder(coverage) == COVERAGE_PCT and sum(COVERAGE_PCT.values()) == 100
    inherent_counts = {band: sum(1 for value in GOLDEN.values() if value[1] == band) for band in BANDS}
    residual_counts = {band: sum(1 for value in GOLDEN.values() if value[4] == band) for band in BANDS}
    assert inherent_counts == INHERENT_COUNTS and residual_counts == RESIDUAL_COUNTS
    assert ts.largest_remainder(residual_counts) == RESIDUAL_PCT and sum(RESIDUAL_PCT.values()) == 100
    assert {band: [i for i in RESIDUAL_ORDER if golden(i)[4] == band] for band in BANDS} == RESIDUAL_BANDS


def test_harness_the_half_cases_tell_half_up_from_half_even_and_a_float():
    """Every case is a tie after the multiplication, so q1's rounding decides it. A golden that two other roundings also
    give would pin nothing, so each case is checked to differ from at least one of them (and the 4.55 case from a float)."""
    different_from_half_even = different_from_float = 0
    for finding_id in HALF_CASES:
        item = by_id(finding_id)
        exact = (Decimal(item["inherent"]) * (1 - ts.REDUCTION_FACTOR_P0[item["control"]])).normalize()
        assert exact.as_tuple().exponent == -2 and str(exact)[-1] == "5", "%s: %s is not a tie at the tenths" % (finding_id, exact)
        half_even = exact.quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)
        by_float = Decimal(str(round(float(exact), 1)))
        different_from_half_even += half_even != Decimal(golden(finding_id)[3])
        different_from_float += by_float != Decimal(golden(finding_id)[3])
    assert different_from_half_even >= 5 and different_from_float >= 3
    assert round(4.55, 1) == 4.5 and str(ts.residual_score(Decimal("9.1"), Decimal("0.50"))) == "4.6", "residual-risk.md:112's example"
    reduction = Decimal(DELTA) * 100 / Decimal(TOTAL_INHERENT)
    assert reduction == Decimal("28.25") and str(reduction.quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)) == "28.2"


def test_harness_the_orders_and_the_groups_follow_the_contract():
    by_score = sorted(GOLDEN, key=lambda i: (-Decimal(GOLDEN[i][3]), s2_key(i)))
    assert by_score == RESIDUAL_ORDER
    assert sorted(OPEN_IDS, key=s2_key) == S2_ORDER
    assert sorted((i for i in GOLDEN if by_id(i)["control"] != "found"), key=lambda i: (-Decimal(GOLDEN[i][0]), s2_key(i))) == RECOMMENDED
    tied = [i for i in RESIDUAL_ORDER if GOLDEN[i][3] == "2.8"]
    assert tied == ["S-10", "R-1"], "S-2's order breaks the residual tie"
    unmitigated = [i for i in GOLDEN if by_id(i)["control"] != "found"]
    assert max(Decimal(GOLDEN[i][0]) for i in GOLDEN) == Decimal("9.7") and by_id("D-2")["control"] == "found"
    assert sorted(unmitigated, key=lambda i: (-Decimal(GOLDEN[i][0]), s2_key(i)))[0] == HIGHEST_UNMITIGATED
    moved = {}
    for finding_id in S2_ORDER:
        inherent_band, residual_band = golden(finding_id)[1], golden(finding_id)[4]
        label = "No Shift" if inherent_band == residual_band else "%s -> %s" % (inherent_band, residual_band)
        moved.setdefault(label, []).append(finding_id)
    assert moved == {label: ids for label, ids in SHIFTS.items() if ids}
    assert sum(len(ids) for ids in SHIFTS.values()) == len(FINDINGS)
    # Section 3: one control for each distinct (category, file, line), and the findings that name it.
    grouped = {}
    for item in FINDINGS:
        for entry in item["evidence"]:
            grouped.setdefault((item["category"], entry["file"], entry["line"]), []).append(item["id"])
    assert sorted(grouped) == sorted((c, f, n) for c, f, n, _ids in CONTROLS) and len(CONTROLS) == 9
    assert {(c, f, n): sorted(ids, key=s2_key) for (c, f, n), ids in grouped.items()} == {(c, f, n): ids for c, f, n, ids in CONTROLS}
    assert sum(len(item["evidence"]) for item in FINDINGS) == EVIDENCE_ENTRIES


def test_harness_the_synthetic_texts_are_short_enough_for_every_source_to_agree():
    """risk-scores.md shortens a component at 30 characters and a threat at 60, so with these every source reads the same."""
    for item in FINDINGS:
        assert len(item["component"]) <= 30 and len(item["threat"]) <= 60, item["id"]
        assert item["component"] in COMPONENTS and len(matrix_row_of(item)) <= 1200


def test_harness_the_synthetic_threats_md_is_a_valid_reference_set():
    text = make_threats_md(FINDINGS, RESOLVED)
    reference = tachi_parsers.parse_reference_set(text)
    assert [canon(row["id"]) for row in reference["open"]] == [canon(i) for i in S2_ORDER]
    assert [row["id"] for row in reference["resolved"]] == RESOLVED_IDS and reference["duplicates"] == []
    assert {row["id"]: row["id"] for row in reference["open"]}["AGP-01"] == "AGP-01", "Section 7's spelling is kept"
    by_row = {canon(row["id"]): row for row in reference["open"]}
    for item in FINDINGS:
        row = by_row[canon(item["id"])]
        assert (row["component"], row["threat"], row["delta_status"]) == (item["component"], item["threat"], "NEW"), item["id"]
    groups = tachi_parsers.parse_correlation_groups(make_threats_md(FINDINGS, RESOLVED, groups=GROUPS))["groups"]
    assert [(group["group_id"], group["members"]) for group in groups] == [("CG-1", ["S-2", "S-10"])]


def test_harness_the_synthetic_risk_scores_md_reads_back_as_the_scorer_writes_it(tmp_path):
    text = make_risk_scores_md()
    rows = tachi_parsers.parse_risk_scores_findings(text)
    assert [row["id"] for row in rows] == [i for i in sorted(OPEN_IDS, key=lambda each: (-Decimal(golden(each)[0]), s2_key(each)))]
    for row in rows:
        inherent, inherent_band = golden(row["id"])[:2]
        assert (row["composite_score"], row["severity"]) == (inherent, inherent_band), row["id"]
    path = tmp_path / "risk-scores.md"
    path.write_text(text, encoding="utf-8")
    scores = rules.read_baseline_scores(path)
    assert scores.readable and sorted(scores.rows, key=s2_key) == [canon(i) for i in S2_ORDER], "the D9 reader reads every open row"
    assert sorted(scores.resolved_rows) == sorted(RESOLVED_IDS)
    for finding_id, row in scores.rows.items():
        item = by_id(finding_id)
        assert (str(row.stored["composite"]), row.band, row.component, row.threat) == (item["inherent"], golden(finding_id)[1], item["component"], item["threat"])
    assert re.search(r'(?m)^source_file: "run/threats.md"$', text)


def test_harness_the_target_holds_every_evidence_file_and_the_resolver_accepts_it(tmp_path):
    project = Project(_load_hyphenated_script("tachi_stage_for_controls_harness", "tachi-stage.py"), None, tmp_path)
    paths = {entry["file"] for item in FINDINGS for entry in item["evidence"]}
    assert paths == set(evidence_files(FINDINGS)) and len(paths) == 7
    for path in sorted(paths):
        resolved = sc.resolve_file(path, root=str(project.target))
        assert (resolved.path, resolved.uri) == (path, path), "relative to the target, in their canonical spelling"


def test_harness_the_agents_rows_have_eleven_cells_and_slots_in_the_computed_ones():
    for item in FINDINGS:
        cells = [cell.strip() for cell in matrix_row_of(item).strip().strip("|").split("|")]
        assert len(cells) == len(K8_HEADER) == 11 and "|" not in " ".join(matrix_cells(item)), item["id"]
        computed = {name: cells[K8_HEADER.index(name)] for name in ("Inherent Score", "Inherent Severity", "Residual Score", "Residual Severity")}
        assert computed == {"Inherent Score": "{{score:inherent}}", "Inherent Severity": "{{band:inherent}}",
                            "Residual Score": "{{score:residual}}", "Residual Severity": "{{band:residual}}"}
        assert cells[K8_HEADER.index("CF")] == DASH and cells[0] == item["id"]


def test_harness_the_part_bodies_hold_the_four_keys_once_in_order():
    for item in FINDINGS:
        if item["control"] == "found":
            assert controls_item(item)["recommendation_body"] is None
            continue
        body = body_of(item)
        keys = [re.match(r"\*\*([A-Za-z ]+)\*\*: ", line).group(1) for line in body.split("\n") if line]
        assert keys == ["What to Implement", "Where to Implement", "Reference Patterns", "Effort Estimate"], item["id"]
        assert effort_of(body) in ("Low", "Medium", "High") and what_of(body) == item["rec"]["what"]
        assert not re.search(r"(?m)^(#|\|)", body) and len(body) <= 2000


def section_2_and_4_of(ids):
    """A Section 2 and a Section 4 in the template's form for ``ids``, for the shipped reader (no renderer is involved)."""
    lines = ["## 2. Coverage Matrix", ""]
    for band in BANDS:
        mine = [i for i in RESIDUAL_ORDER if i in ids and golden(i)[4] == band]
        if mine:
            lines += ["### %s Residual Severity" % band, "", "| " + " | ".join(K8_HEADER) + " |", "|" + "---|" * len(K8_HEADER)]
            for finding_id in mine:
                inherent, inherent_band, _factor, residual, residual_band = golden(finding_id)
                cells = matrix_cells(by_id(finding_id))
                for token, value in (("{{score:inherent}}", inherent), ("{{band:inherent}}", inherent_band),
                                     ("{{score:residual}}", residual), ("{{band:residual}}", residual_band)):
                    cells = [value if cell == token else cell for cell in cells]
                lines.append("| " + " | ".join(tp.escape_cell(cell) for cell in cells) + " |")
            lines.append("")
    lines += ["## 4. Recommendations", ""]
    for number, finding_id in enumerate([i for i in RECOMMENDED if i in ids], 1):
        item = by_id(finding_id)
        lines += ["#### %d. %s %s %s (Composite: %s, %s)" % (number, item["id"], DASH, item["component"], item["inherent"], golden(finding_id)[1]),
                  "", "**Current Status**: %s" % STATUS_CELL[item["control"]], "", tp.escape_prose(body_of(item)), "", "---", ""]
    return "\n".join(lines) + "\n## 5. Residual Risk Summary\n"


def test_harness_sarifs_recommendation_is_what_the_shipped_section_4_reader_returns():
    """ADR-050 D2's rule for SARIF's ``recommendation``: "read from each §4 body by ``parse_compensating_controls_md``'s rule". It is
    the "What to Implement" text, which the shipped reader returns from a block in the template's form, decoded, even when
    the markdown held markup, a backtick and an ampersand (escaped as prose). This needs no renderer."""
    read = tachi_parsers.parse_compensating_controls_md(section_2_and_4_of(set(OPEN_IDS)))
    found = {canon(row["id"]): row["recommendation"] for row in read["findings"]}
    assert found == {canon(item["id"]): ("" if item["control"] == "found" else item["rec"]["what"]) for item in FINDINGS}
    assert found["E-3"] == HOSTILE_WHAT, "backticks, markup and an ampersand come back as the agent wrote them"


def test_harness_the_synthetic_parts_pass_the_shipped_validator(stage, tmp_path):
    root = Project(stage, None, tmp_path)
    root.prepare(batch_size=4)
    assert sorted(root.batches()) == ["B001", "B002", "B003"]
    seen = []
    for batch_id, entry in root.batches().items():
        result = tp.read_part(root.batch_input(batch_id)["part_path"], root.out, root.plan_id, batch_id, STAGE, "tachi-control-analyzer",
                              entry["finding_ids"])
        assert result.state == "done", (batch_id, result.detail)
        assert result.counts == {"narrative_fallbacks": 0, "truncations": 0} and result.flags == {}
        seen += [item["finding_id"] for item in result.part["items"]]
        for item in result.part["items"]:
            assert item == dict(controls_item(by_id(item["finding_id"])), finding_id=canon(item["finding_id"])), "validation changes no value"
    assert sorted(seen, key=s2_key) == [canon(i) for i in S2_ORDER], "a validated part carries canonical IDs"
    plan = root.plan_json()  # what the renderer reads from the plan: the input risk-scores.md, the target, the architecture and the date
    assert "risk_scores" in plan["inputs"] and set(plan["refs"]) >= {"risk_scores", "target", "architecture"}
    assert plan["params"]["scoring_date"] == DATE and plan["unit_count"] == len(FINDINGS)


def test_harness_the_slot_lookup_resolves_every_slot_the_narrative_uses():
    item = by_id("T-1")
    for dimension, cell in ASSESSMENT.items():
        assert narrative(item, cell["rationale"]) is not None, dimension
    assert narrative(item, ASSESSMENT["coverage"]["rationale"]) == "Validation covers 1 entry point of auth-broker."
    assert narrative(item, ASSESSMENT["configuration"]["rationale"]) == "Strict mode is on, so risk falls from 7.3 to 3.7."
    assert narrative(item, ASSESSMENT["currency"]["rationale"]) == "Maintained code: the High finding drops to Low."
    assert narrative(item, ASSESSMENT["completeness"]["rationale"]) == "A reduction of 49.3 percent still leaves the batch endpoints open."


# =============================================================================
# 5. The entry: arguments and the exit table (T035; contracts/cli.md)
# =============================================================================


def test_cli_help_and_version_are_supported(renderer, tmp_path):
    helped = invoke(renderer, ["--help"], tmp_path)
    assert helped.code == 0 and all(flag in helped.out for flag in ("--out", "--plan", "--plan-digest")), helped.describe()
    versioned = invoke(renderer, ["--version"], tmp_path)
    assert versioned.code == 0, versioned.describe()
    assert tp.VERSION in versioned.out + versioned.err  # reading: cli.md says tests may accept either stream
    assert "%d.%d" % sys.version_info[:2] in versioned.out + versioned.err, "the interpreter's version too"


def test_cli_a_missing_plan_digest_is_a_usage_error(renderer, tmp_path):
    res = invoke(renderer, ["--out", tmp_path, "--plan", "20261122T100000Z-0123456789ab"], tmp_path)
    assert res.code == 2, res.describe()


def test_cli_a_run_directory_with_no_plan_is_a_missing_input(renderer, tmp_path):
    (tmp_path / "run").mkdir()
    res = invoke(renderer, ["--out", tmp_path / "run", "--plan", "20261122T100000Z-0123456789ab", "--plan-digest", "0" * 64], tmp_path)
    assert res.code == 1, res.describe()
    assert_failure_message(res)
    assert not (tmp_path / "run" / MD).exists() and not (tmp_path / "run" / SARIF).exists()


def test_cli_a_plan_digest_that_differs_exits_2_and_writes_nothing(project):
    project.earlier()
    project.prepare()
    before = tree_state(project.out)
    res = invoke(project.renderer, ["--out", project.out, "--plan", project.plan_id, "--plan-digest", "0" * 64], project.root)
    assert res.code == 2, res.describe()
    assert_failure_message(res)
    assert tree_state(project.out) == before, "a refused plan leaves every file as it was"
    project.assert_earlier_outputs_untouched()


def test_cli_a_plan_that_current_json_does_not_name_exits_2(project):
    project.prepare()
    older_id, older_digest = project.plan_id, project.digest
    project.plan()  # a newer plan replaces the pointer
    res = invoke(project.renderer, ["--out", project.out, "--plan", older_id, "--plan-digest", older_digest], project.root)
    assert res.code == 2, res.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists()


def test_cli_a_changed_plan_input_exits_2(project):
    project.prepare()
    project.risk_scores.write_text(project.risk_scores.read_text(encoding="utf-8") + "\nAn edit after plan.\n", encoding="utf-8")
    res = project.render()
    assert res.code == 2, res.describe()
    assert_failure_message(res, project.plan_id)
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists()


def test_cli_the_summary_goes_to_stdout_and_the_renderer_leaves_the_plan_alone(base):
    assert base.last.code == 0, base.last.describe()
    assert base.last.out.strip(), "the renderer prints summary lines, so the command restates no number (D4 Step 6)"
    assert not base.last.out.lstrip().startswith("{"), "summary lines, not one JSON object (cli.md)"
    for number in (len(FINDINGS), COVERAGE["found"], COVERAGE["missing"]):
        assert re.search(r"(?<![\w.])%d(?![\w.])" % number, base.last.out), "the summary has the count %d: %s" % (number, base.last.out)
    assert tp.file_digest(base.plan_dir / "plan.json") == base.digest, "only plan and reconcile write the plan (contracts/part-files.md)"
    assert tp.read_document(tp.pointer_path(base.out, STAGE), base.out, tp.POINTER_SCHEMA)["plan_id"] == base.plan_id
    # reading: the summary states the number of scored findings and each status's count, as the scorer's states its bands'


# =============================================================================
# 6. compensating-controls.md: coverage, arithmetic and the sections (T035; ADR-050 D2, D5, D15)
# =============================================================================


def test_md_the_run_is_clean(base):
    assert base.last.code == 0, base.last.describe()
    assert base.record["warnings"] == [] and base.record["status"] == "success"


def test_md_the_frontmatter_is_schema_1_1_for_a_run_with_no_baseline(base):
    assert frontmatter_value(base.md, "schema_version") == "1.1"
    assert frontmatter_value(base.md, "date") == DATE and frontmatter_value(base.md, "classification") == "security"
    assert frontmatter_value(base.md, "rescan_scope") == "full", "no baseline: every finding is scanned"
    assert frontmatter_value(base.md, "carry_forward_count") == "null"
    for key, path in (("source_file", base.risk_scores), ("target_path", base.target)):
        value = frontmatter_value(base.md, key)
        assert not os.path.isabs(value), "%s is relative to the working directory, so no local path reaches the file (NFR-6)" % key
        assert os.path.samefile(str(base.root / value), str(path)), key


def test_md_the_sections_come_in_order(base):
    lines = base.md.split("\n")
    positions = []
    for title in SECTION_TITLES:
        found = [n for n, line in enumerate(lines) if line.startswith(title)]
        assert len(found) == 1, "%s: %d headings" % (title, len(found))
        positions.append(found[0])
    assert positions == sorted(positions), "Sections 1 to 7, with Analysis Integrity last (D15)"


def test_md_every_scored_open_finding_is_in_section_2_exactly_once(base):
    found = matrix_rows(base.md)  # asserts that no finding is listed twice
    assert sorted(found, key=s2_key) == [canon(i) for i in S2_ORDER] and len(found) == len(FINDINGS)
    assert sorted(row["Threat ID"] for _band, row in found.values()) == sorted(OPEN_IDS), \
        "an ID is spelled as the reference set spells it, AGP-01 included, so that Section 4 joins to it (D3)"
    for finding_id in RESOLVED_IDS:
        assert not re.search(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(finding_id), base.md), "%s is RESOLVED: it appears nowhere (D8)" % finding_id


def test_md_section_2_groups_its_rows_by_residual_band_and_orders_them(base):
    found = band_tables(base.md)
    assert [band for band, _h, _r in found] == list(BANDS), "Critical first"
    for band, _header, rows in found:
        assert [canon(row["Threat ID"]) for row in rows] == [canon(i) for i in RESIDUAL_BANDS[band]], "residual descending, then S-2: %s" % band
        assert {row["Residual Severity"] for row in rows} == {band}
    assert [canon(row["Threat ID"]) for _b, _h, rows in found for row in rows] == [canon(i) for i in RESIDUAL_ORDER]


def test_md_section_2_uses_the_k8_header_in_every_band_table(base):
    assert [header for _band, header, _rows in band_tables(base.md)] == [K8_HEADER] * 4, "one schema, MAESTRO Layer and Control Category included (FR-K8.1)"


def test_md_section_2_omits_a_band_with_no_row(stage, renderer, tmp_path):
    subset = [by_id(i) for i in ("S-10", "AG-1", "R-1")]  # residuals 2.8, 3.5 and 2.8: all Low
    project = Project(stage, renderer, tmp_path, findings=subset)
    res = project.run()
    assert res.code == 0, res.describe()
    assert [band for band, _h, _r in band_tables(project.md)] == ["Low"], "a band with no finding has neither a heading nor an empty table"
    assert "### Critical Residual Severity" not in project.md and "### High Residual Severity" not in project.md
    assert sorted(matrix_rows(project.md), key=s2_key) == ["S-10", "R-1", "AG-1"]


def test_md_section_2_rows_carry_each_findings_inputs_and_computed_values(base):
    for finding_id, (band, row) in matrix_rows(base.md).items():
        item = by_id(finding_id)
        inherent, inherent_band, _factor, residual, residual_band = golden(finding_id)
        assert (row["Inherent Score"], row["Inherent Severity"], row["Residual Score"], row["Residual Severity"]) == (
            inherent, inherent_band, residual, residual_band), finding_id
        assert (row["Component"], row["MAESTRO Layer"], row["Threat"], row["CF"]) == (
            item["component"], COMPONENTS[item["component"]][1], item["threat"], DASH), finding_id
        assert tachi_parsers.classify_control_status(row["Control Status"])[0] == STATUS_CLASS[item["control"]], finding_id
        assert slug(row["Control Category"]) == item["category"], finding_id
        assert band == residual_band


def test_md_residuals_round_half_up_by_q1(base):
    rows = matrix_rows(base.md)
    for finding_id in HALF_CASES:
        item = by_id(finding_id)
        exact = Decimal(item["inherent"]) * (1 - ts.REDUCTION_FACTOR_P0[item["control"]])
        assert rows[canon(finding_id)][1]["Residual Score"] == str(ts.q1(exact)) == golden(finding_id)[3], "%s: %s" % (finding_id, exact)
    assert rows["S-2"][1]["Residual Score"] == "4.6", "residual-risk.md:112: 4.55 is 4.6, where Python's round() gives 4.5"
    assert rows["T-4"][1]["Residual Score"] == "7.1" and rows["T-4"][0] == "High", "7.05 is 7.1, and it is High, not the 7.0 of a float"


def test_md_the_inherent_score_is_the_input_composite_and_never_rescored(stage, renderer, tmp_path):
    """The row's sub-scores can't produce its composite, and its Severity cell contradicts it. The inherent score is the
    Composite cell and its severity is band(inherent): ADR-050 D2, "never re-scored"."""
    text = make_risk_scores_md(scores={"S-2": ["1.0"] * 4}).replace("| 9.1 | Critical | 24h |", "| 9.1 | Low | 90d |")
    assert "| 9.1 | Low | 90d |" in text and "| 1.0 | 1.0 | 1.0 | 1.0 | 9.1 |" in text
    project = Project(stage, renderer, tmp_path, risk_scores_text=text)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    band, row = matrix_rows(project.md)["S-2"]
    assert (row["Inherent Score"], row["Inherent Severity"], row["Residual Score"], band) == ("9.1", "Critical", "4.6", "Medium")
    assert results_by_id(project.sarif)["S-2"]["properties"]["inherent-risk"] == "9.1"


def test_md_section_1_states_the_coverage_counts_and_percentages(base):
    body = section(base.md, "## 1. Executive Summary")
    assert "**11** threats analyzed | **4** Control Found | **4** Partial Control | **3** No Control Found" in body
    assert "**Coverage**: 37% Found | 36% Partial | 27% Missing" in body, "largest remainder: 36.36 and 36.36 tie, and the point goes to the label that sorts first"
    header, rows = table_of(body, "Status")
    assert header == ["Status", "Count", "Percentage"]
    plain = [[re.sub(r"\*", "", cell) for cell in row] for row in rows]
    assert plain == [["Control Found", "4", "37%"], ["Partial Control", "4", "36%"], ["No Control Found", "3", "27%"], ["Total", "11", "100%"]]
    kinds = [tachi_parsers.classify_control_status(row["Control Status"])[0] for _b, row in matrix_rows(base.md).values()]
    assert (kinds.count("found"), kinds.count("partial"), kinds.count("none")) == (4, 4, 3), "the counts are the rows' own"


def test_md_section_1_states_the_totals_as_the_sums_of_the_rows(base):
    body = section(base.md, "## 1. Executive Summary")
    assert "**Risk Reduction**: 80.0 inherent -> 57.4 residual (**28.3%** reduction)" in body, "22.6 of 80.0 is 28.25%, which rounds half up"
    rows = [row for _band, row in matrix_rows(base.md).values()]
    assert sum(Decimal(row["Inherent Score"]) for row in rows) == Decimal(TOTAL_INHERENT)
    assert sum(Decimal(row["Residual Score"]) for row in rows) == Decimal(TOTAL_RESIDUAL), "the residual total is the sum of the rounded rows"


def test_md_section_1_names_the_highest_risk_unmitigated_finding(base):
    body = section(base.md, "## 1. Executive Summary")
    line = [line for line in body.split("\n") if line.startswith("**Highest-Risk Unmitigated Finding**:")]
    assert len(line) == 1, body
    assert line[0].startswith("**Highest-Risk Unmitigated Finding**: T-4 %s auth-broker %s Composite 9.4 (Critical)" % (DASH, DASH)), \
        "a partial or missing finding with the highest inherent score, ties in S-2 order: D-2 (9.7) is found and E-5 ties at 9.4 but sorts later"


def test_md_section_1_has_the_metadata_table(base):
    body = section(base.md, "## 1. Executive Summary")
    header, rows = table_of(body, "Metric")
    shown = {row[0]: row[1] for row in rows}
    assert header == ["Metric", "Value"]
    assert shown["Analysis date"] == DATE and shown["Schema version"] == "1.1"
    assert shown["Source file"].strip("`") == frontmatter_value(base.md, "source_file")
    assert shown["Target codebase"].strip("`") == frontmatter_value(base.md, "target_path")


def test_md_section_2_summary_statistics_count_the_rows_by_residual_band(base):
    body = [body for heading, body in split_headings(section_text(base.md, "## 2. Coverage Matrix"), "### ") if heading == "### Summary Statistics"]
    assert len(body) == 1
    header, rows = table_of(body[0], "Residual Severity")
    assert header == ["Residual Severity", "Count", "Percentage"]
    plain = [[re.sub(r"\*", "", cell) for cell in row] for row in rows]
    assert plain == [[band, str(RESIDUAL_COUNTS[band]), "%d%%" % RESIDUAL_PCT[band]] for band in BANDS] + [["Total", "11", "100%"]], \
        "largest remainder: Medium and Low tie, and the point goes to Low, which sorts first"


def test_md_section_3_has_one_control_for_each_category_file_and_line(base):
    blocks = control_blocks(base.md)
    found = []
    for category, heading, body in blocks:
        detected = re.search(r"\*\*Detected in\*\*: `([^`]+)`", body)
        assert detected, "no 'Detected in' line: %s" % heading
        file, _colon, line = decode(detected.group(1)).rpartition(":")
        found.append((slug(category), file, int(line)))
    assert sorted(found) == sorted((c, f, n) for c, f, n, _ids in CONTROLS), "one control for each distinct (category, file, line)"
    assert len(blocks) == len(set(found)) == 9 < EVIDENCE_ENTRIES, "a shared control is listed once, and one file:line under two categories twice"
    ids = [re.match(r"#### (\S+) " + DASH + " ", heading).group(1) for _c, heading, _b in blocks]
    assert len(set(ids)) == len(ids) and all(re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*", each) for each in ids), "control IDs are unique tokens"


def test_md_section_3_groups_the_controls_by_category_in_the_templates_order(base):
    headings = [heading[len("### "):] for heading, _body in split_headings(section_text(base.md, "## 3. Control Details"), "### ")]
    present = [name for name in CATEGORY_ORDER if any(c == name for c, _f, _n, _i in CONTROLS)]
    assert [slug(heading) for heading in headings] == present == ["authentication", "access-control", "input-validation", "encryption", "rate-limiting"]
    assert headings[0] == "Authentication" and headings[-1] == "Rate Limiting"
    assert "### Logging/Audit" not in base.md.split("## 4. Recommendations")[0], "a category with no detected control has no subsection"


def test_md_section_3_each_control_lists_the_threats_it_mitigates(base):
    by_key = {}
    for category, _heading, body in control_blocks(base.md):
        file, _colon, line = decode(re.search(r"\*\*Detected in\*\*: `([^`]+)`", body).group(1)).rpartition(":")
        by_key[(slug(category), file, int(line))] = body
    for category, file, line, ids in CONTROLS:
        body = by_key[(category, file, line)]
        header, rows = table_of(body, "Threat ID")
        assert header == ["Threat ID", "Component", "Threat", "Inherent Score", "Reduction Factor", "Residual Score"]
        found = {canon(row["Threat ID"]): row for row in records(header, rows)}
        assert sorted(found, key=s2_key) == [canon(i) for i in ids], (category, file, line)
        for finding_id in ids:
            item = by_id(finding_id)
            row = found[canon(finding_id)]
            assert (row["Component"], row["Inherent Score"], row["Residual Score"]) == (item["component"], golden(finding_id)[0], golden(finding_id)[3])
            assert Decimal(row["Reduction Factor"]) == ts.REDUCTION_FACTOR_P0[item["control"]], finding_id
        status = re.search(r"\*\*Status\*\*: ([^|\n]+?)\s*(?:\||\n)", body).group(1)
        effectiveness = re.search(r"\*\*Effectiveness\*\*: (\w+)", body).group(1)
        kind = by_id(ids[0])["control"]
        assert tachi_parsers.classify_control_status(status)[0] == STATUS_CLASS[kind] and effectiveness.lower() == EFFECTIVENESS[kind], (category, file, line)


def test_md_section_3_shows_each_controls_summary_and_its_code_in_a_long_enough_fence(base):
    shown = {}
    for category, heading, body in control_blocks(base.md):
        detected = decode(re.search(r"\*\*Detected in\*\*: `([^`]+)`", body).group(1))
        shown[(slug(category), detected)] = (heading, body)
    for category, file, line, ids in CONTROLS:
        entry = next(e for e in by_id(ids[0])["evidence"] if (e["file"], e["line"]) == (file, line))
        heading, block = shown[(category, "%s:%d" % (file, line))]
        assert heading.endswith(" %s %s" % (DASH, tp.escape_cell(entry["summary"]))), "the control's summary is the evidence summary, escaped"
        fence = tp.fence_for(entry["snippet"])
        assert "%s%s\n%s\n%s\n" % (fence, entry["language"], entry["snippet"], fence) in block, "the snippet is written as it is, inside its fence"
    assert len(shown) == 9
    assert tp.fence_for(TLS["snippet"]) == "````", "the TLS snippet holds a run of three backticks, so its fence is four"


def test_md_section_3_fills_the_slots_of_the_effectiveness_narrative(base):
    block = next(body for cat, heading, body in control_blocks(base.md) if "`src/validate/schema.py:17`" in body and slug(cat) == "input-validation")
    header, rows = table_of(block, "Dimension")
    assert header == ["Dimension", "Rating", "Rationale"]
    shown = {row[0]: row for row in rows}
    item = by_id("T-1")
    for dimension, cell in ASSESSMENT.items():
        label, rating, rationale = shown[dimension.capitalize()]
        assert (label, rating) == (dimension.capitalize(), cell["rating"])
        assert rationale == decode(narrative(item, cell["rationale"])), dimension
    assert "{{" not in block, "no slot token survives into Section 3"


def test_md_section_4_has_one_block_for_each_partial_or_missing_finding_and_none_for_a_found_one(base):
    blocks = recommendation_blocks(base.md)
    assert sorted(blocks, key=s2_key) == sorted((canon(i) for i in RECOMMENDED), key=s2_key)
    for finding_id, block in blocks.items():
        item = by_id(finding_id)
        status = re.search(r"\*\*Current Status\*\*: (.*)", block).group(1)
        assert tachi_parsers.classify_control_status(status)[0] == STATUS_CLASS[item["control"]], finding_id
        positions = [block.index(key) for key in ("**What to Implement**:", "**Where to Implement**:", "**Reference Patterns**:", "**Effort Estimate**:")]
        assert positions == sorted(positions), "each key once, in order: %s" % finding_id
        assert not re.search(r"(?m)^(#{1,3} |\|)", block.split("\n", 1)[1]), "no heading or table line inside a block"
    findings = read_findings(base.md)
    assert sorted(findings, key=s2_key) == [canon(i) for i in S2_ORDER]
    for item in FINDINGS:
        wanted = "" if item["control"] == "found" else item["rec"]["what"]
        assert findings[canon(item["id"])]["recommendation"] == wanted, "the shipped reader joins each block to its finding: %s" % item["id"]


def test_md_section_5_has_the_aggregate_reduction_table(base):
    header, rows = table_of(subsection_of(base.md, "## 5. Residual Risk Summary", "### Aggregate Risk Reduction"), "Metric")
    assert header == ["Metric", "Value"]
    shown = {row[0]: row[1] for row in rows}
    assert [row[0] for row in rows] == ["Total Inherent Risk Score", "Total Residual Risk Score", "Delta", "Overall Reduction"]
    assert (shown["Total Inherent Risk Score"], shown["Total Residual Risk Score"], shown["Delta"]) == (TOTAL_INHERENT, TOTAL_RESIDUAL, DELTA)
    assert cell_number(shown["Overall Reduction"]) == Decimal(REDUCTION)
    assert cell_number(shown["Total Inherent Risk Score"]) - cell_number(shown["Total Residual Risk Score"]) == cell_number(shown["Delta"])


def test_md_section_5_has_the_band_shift_table(base):
    body = subsection_of(base.md, "## 5. Residual Risk Summary", "### Per-Severity-Band Shift")
    header, rows = table_of(body, "Shift")
    assert header == ["Shift", "Count", "Examples"]
    plain = {re.sub(r"\*", "", row[0]).replace("\u2192", "->").strip(): row for row in rows}
    assert list(plain) == list(SHIFTS) + ["Total"], "the six shifts, then No Shift, then the total"
    for label, ids in SHIFTS.items():
        assert int(plain[label][1]) == len(ids), label
        assert label_ids(plain[label][2]) == sorted(canon(i) for i in ids), "%s names the IDs of its shift (reading: all of them, as there are at most four)" % label
    assert int(re.sub(r"\*", "", plain["Total"][1])) == len(FINDINGS) == sum(int(row[1]) for label, row in plain.items() if label != "Total")


def test_md_section_5_has_the_severity_distribution_comparison(base):
    header, rows = table_of(subsection_of(base.md, "## 5. Residual Risk Summary", "### Severity Distribution Comparison"), "Severity")
    assert header == ["Severity", "Inherent Count", "Residual Count", "Change"]
    plain = [[re.sub(r"\*", "", cell) for cell in row] for row in rows]
    assert [row[0] for row in plain] == list(BANDS) + ["Total"]
    for row in plain[:4]:
        assert (int(row[1]), int(row[2])) == (INHERENT_COUNTS[row[0]], RESIDUAL_COUNTS[row[0]])
        assert cell_number(row[3]) == RESIDUAL_COUNTS[row[0]] - INHERENT_COUNTS[row[0]], "Change is the residual count less the inherent one (reading)"
    assert (int(plain[4][1]), int(plain[4][2])) == (11, 11)


def test_md_section_5_has_the_reduction_factor_reference(base):
    header, rows = table_of(subsection_of(base.md, "## 5. Residual Risk Summary", "### Reduction Factor Reference"), "Control Status")
    assert header[:2] == ["Control Status", "Reduction Factor"]
    shown = {row[0]: Decimal(row[1]) for row in rows}
    assert shown == {"Control Found": Decimal("0.50"), "Partial Control": Decimal("0.25"), "No Control Found": Decimal("0.00")}
    assert [shown[STATUS_CELL[status]] for status in ts.REDUCTION_FACTOR_P0] == list(ts.REDUCTION_FACTOR_P0.values()), "the table is the P0 factors"


def test_md_section_7_has_its_defined_places_and_a_clean_run_lists_nothing(base):
    body = section(base.md, "## 7. Analysis Integrity")
    parts = [line for line in body.split("\n") if line.startswith("### ")]
    assert "### Input Issues" in parts and "### Assessment Inputs" in parts, "the rows the agent couldn't parse have a place of their own (FR-K7.4)"
    issues = subsection_of(base.md, "## 7. Analysis Integrity", "### Input Issues")
    assert all(not rows for _header, rows in tables(issues)), "Input Issues lists nothing for a clean run"
    assert not re.search(r"input:[a-z_.]+:(truncated|narrative-fallback)|reused-id", body), "and no finding carries a flag"


def test_md_section_7_assessment_inputs_are_the_persisted_format_exactly(base):
    header, rows = table_of(subsection_of(base.md, "## 7. Analysis Integrity", "### Assessment Inputs"), "ID")
    assert header == ["ID", "Field", "Value"]
    got = [(canon(row[0]), row[1], row[2]) for row in rows]
    want = [(canon(finding_id), field, value) for finding_id, field, value in expected_assessment_inputs(FINDINGS)]
    assert got == want  # reading: an ID's spelling is Section 7's or the canonical one; both compare as one


def test_md_section_7_persists_the_slots_and_the_evidence_escaped_on_write(base):
    raw = subsection_of(base.md, "## 7. Analysis Integrity", "### Assessment Inputs")
    assert "{{score:inherent}}" in raw and "{{count:evidence}}" in raw, "slot tokens are kept in the narrative text and in matrix_row (RR1, AR-T3)"
    line = [line for line in raw.split("\n") if line.startswith("| T-1 |") and "evidence.0.assessment.configuration.rationale" in line][0]
    assert tp.escape_cell(ASSESSMENT["configuration"]["rationale"], keep_slots=True) in line
    row_line = [line for line in raw.split("\n") if line.startswith("| E-3 |") and "| matrix_row |" in line][0]
    assert tp.escape_cell(matrix_row_of(by_id("E-3")), keep_slots=True) in row_line and "&#124;" in row_line, "the row's own pipes are escaped, so it stays one cell"
    snippet_line = [line for line in raw.split("\n") if line.startswith("| T-4 |") and "evidence.0.snippet" in line][0]
    assert tp.escape_cell(TLS["snippet"], keep_slots=True) in snippet_line and "&#10;" in snippet_line and "&#96;&#96;&#96;" in snippet_line


def test_md_the_file_ends_with_the_stamp(base):
    md = base.md
    stamp = tp.read_stamp(md)
    assert stamp is not None and md.rstrip("\n").split("\n")[-1] == tp.stamp_comment(stamp["renderer"], stamp["input_digest"])
    assert stamp["renderer"] == RENDERER_NAME and stamp["version"] == tp.VERSION and DIGEST.match(stamp["input_digest"])


def test_md_every_table_row_has_the_columns_of_its_header(base):
    for header, rows in tables(base.md):
        for row in rows:
            assert len(row) == len(header), "a cell broke its row: %s under %s" % (row, header)


def test_md_untrusted_text_is_escaped_in_every_markdown_sink(base):
    md = base.md
    assert "<b>" not in md and "{{7*7}}" not in md and "<script" not in md
    line = raw_row(md, "## 2. Coverage Matrix", "LLM-4")
    assert "&lt;b&gt;" in line and "&#96;" in line and "&#123;&#123;" in line
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in md, "the evidence summary, in its control's heading"
    block = recommendation_blocks(md)["E-3"]
    assert tp.escape_prose(what_of(body_of(by_id("E-3")))) in block and "&lt;b&gt;and&lt;/b&gt;" in block
    assert "\u00c9tienne" in md, "the markdown is UTF-8 and keeps non-ASCII text as it is"
    assert tp.fence_for(TLS["snippet"]) + "python\n" + TLS["snippet"] in md, "a snippet is the one text that stays raw, inside its fence"


# =============================================================================
# 7. compensating-controls.sarif (T035, T053; ADR-050 D7, D8; contracts/sarif-result.md)
# =============================================================================


def test_sarif_the_document_is_the_shared_emitters_two_space_ascii_json(base):
    text, doc = base.sarif_text, base.sarif
    assert text == json.dumps(doc, indent=2, ensure_ascii=True) + "\n", "the bytes are the emitter's: two spaces, ASCII, a final newline"
    assert text.isascii()
    assert doc["version"] == "2.1.0" and doc["$schema"] == sc.SARIF_SCHEMA_URI
    assert len(doc["runs"]) == 1
    run = doc["runs"][0]
    assert "automationDetails" not in run, "the upload step's category governs, and tachi never writes one (D7)"
    driver = run["tool"]["driver"]
    assert driver["name"] == TOOL == sc.TOOL_NAMES[SARIF]
    assert driver["informationUri"] == sc.INFORMATION_URI, "the real URI, never a placeholder (FR-E.9)"
    assert driver["supportedTaxonomies"] == sc.supported_taxonomies()
    assert run["taxonomies"] == sc.TAXONOMIES


def test_sarif_one_result_per_open_finding_and_none_for_a_resolved_one(base):
    doc = base.sarif
    results = doc["runs"][0]["results"]
    assert len(results) == len(FINDINGS), "N is the number of scored open findings (D8's counting rule)"
    assert sorted(results_by_id(doc)) == sorted(OPEN_IDS), "findingId/v1 keeps Section 7's spelling, AGP-01 included"
    for finding_id in RESOLVED_IDS:
        assert not re.search(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(finding_id), base.sarif_text), finding_id


def test_sarif_every_result_passes_the_shared_emitters_self_check(base):
    results = base.sarif["runs"][0]["results"]
    sc.self_check(results, tool=TOOL, member_ids=OPEN_IDS, assignments={}, resolved_ids=RESOLVED_IDS, uri=URI)


def test_sarif_the_results_follow_section_2s_order(base):
    assert [canon(result["partialFingerprints"]["findingId/v1"]) for result in base.sarif["runs"][0]["results"]] == [canon(i) for i in RESIDUAL_ORDER], \
        "control-analyzer.md Phase 6c: residual descending, then S-2's order (reading)"


def test_sarif_each_result_carries_its_goldens(base):
    results = results_by_id(base.sarif)
    for item in FINDINGS:
        finding_id = item["id"]
        result = results[finding_id]
        inherent, _inherent_band, _factor, residual, residual_band = golden(finding_id)
        assert result["ruleId"] == sc.rule_id_for(finding_id)
        assert result["level"] == sc.level_for_band(residual_band), "the level follows the RESIDUAL band (Phase 6c)"
        assert result["message"] == {"text": "%s [Control: %s]" % (item["threat"], item["control"])}, \
            "the full threat text of the reference set, a status suffix, and no markdown (control-analyzer.md Phase 6c)"
        assert result["partialFingerprints"] == sc.partial_fingerprints(TOOL, finding_id)
        zone = next(name for name, _label, _level, members in ZONES if item["component"] in members)
        location = result["locations"][0]
        assert location["physicalLocation"] == {"artifactLocation": {"uri": URI}, "region": {"startLine": 1}}
        assert location["logicalLocations"] == [{"name": item["component"], "fullyQualifiedName": "%s/%s" % (zone, item["component"]),
                                                 "kind": KIND_OF[COMPONENTS[item["component"]][0]]}]
        properties = result["properties"]
        for key, value in {"security-severity": residual, "control-status": item["control"], "control-carry-forward": False,
                           "control-effectiveness": EFFECTIVENESS[item["control"]], "inherent-risk": inherent, "residual-risk": residual,
                           "maestro-layer": COMPONENTS[item["component"]][1]}.items():
            assert properties[key] == value, (finding_id, key)
        assert properties["control-evidence"] == [{"file": e["file"], "line": e["line"], "snippet": e["snippet"]} for e in item["evidence"]], finding_id
        assert properties["integrity-flags"] == [], "always present, and sorted (D7)"
        assert not [key for key in properties if key.startswith("correlation-")]
        related = result.get("relatedLocations", [])
        assert len(related) == len(item["evidence"]), "evidence only, one for each entry, and none for a missing control (D8)"
        for index, (entry, shown) in enumerate(zip(item["evidence"], related)):
            assert shown["id"] == index and shown["physicalLocation"] == {"artifactLocation": {"uri": entry["file"]}, "region": {"startLine": entry["line"]}}
            match = re.fullmatch(r"Control evidence: (.+) detected in (.+)", shown["message"]["text"])
            assert match and match.group(2) == entry["file"] and slug(match.group(1)) == item["category"], shown["message"]


def test_sarifs_recommendation_and_effort_estimate_are_read_from_each_section_4_body(base):
    """ADR-050 D2: "read from each §4 body by ``parse_compensating_controls_md``'s rule", so the two files agree by construction.
    The text is what the shipped reader returns from the rendered file, and also the agent's own What and Effort."""
    read = read_findings(base.md)
    results = results_by_id(base.sarif)
    for item in FINDINGS:
        properties = results[item["id"]]["properties"]
        if item["control"] == "found":
            assert (properties["recommendation"], properties["effort-estimate"]) == ("", ""), "a found finding has no Section 4 block (reading: both are empty)"
            assert read[canon(item["id"])]["recommendation"] == ""
            continue
        assert properties["recommendation"] == read[canon(item["id"])]["recommendation"] == item["rec"]["what"], item["id"]
        assert properties["effort-estimate"] == item["rec"]["effort"] == effort_of(recommendation_blocks(base.md)[canon(item["id"])]), item["id"]
    assert results["E-3"]["properties"]["recommendation"] == HOSTILE_WHAT, "raw in SARIF (json.dumps only), escaped in the markdown"


def test_sarif_each_rule_carries_the_highest_residual_of_its_findings(base):
    run = base.sarif["runs"][0]
    rule_list = {rule["id"]: rule for rule in run["tool"]["driver"]["rules"]}
    highest = {}
    for item in FINDINGS:
        rule_id = sc.rule_id_for(item["id"])
        highest[rule_id] = max(highest.get(rule_id, Decimal("0.0")), Decimal(golden(item["id"])[3]))
    assert sorted(rule_list) == sorted(highest), "a rule with no finding is omitted (Phase 6c): there is none for information disclosure"
    assert len(highest) == 7
    for rule_id, score in highest.items():
        rule = rule_list[rule_id]
        assert rule["properties"]["security-severity"] == str(score), rule_id
        assert rule["shortDescription"]["text"] and rule["fullDescription"]["text"] and rule["properties"]["tags"], rule_id


def test_sarif_carries_the_provenance_stamp(base):
    stamp = base.sarif["runs"][0]["properties"]["tachi_provenance"]
    assert list(stamp) == ["renderer", "version", "input_digest"]
    assert stamp["renderer"] == RENDERER_NAME and stamp["version"] == tp.VERSION and DIGEST.match(stamp["input_digest"])


def test_sarif_hostile_text_is_raw_and_non_ascii_text_is_escaped(base):
    results = results_by_id(base.sarif)
    assert results["LLM-4"]["message"]["text"] == "%s [Control: partial]" % HOSTILE_THREAT, "SARIF strings go through json.dumps only (ADR-050 D3)"
    assert results["T-4"]["properties"]["control-evidence"][0]["snippet"] == TLS["snippet"], "the snippet's backtick run is raw"
    assert "\\u00c9tienne" in base.sarif_text and "\\u2014" in base.sarif_text, "non-ASCII is written as an escape"
    assert results["S-10"]["message"]["text"] == "%s [Control: found]" % by_id("S-10")["threat"]


def test_corr_a_correlated_peer_is_a_result_with_the_correlation_properties_and_ruling_cs_sentence(stage, renderer, tmp_path):
    project = Project(stage, renderer, tmp_path, groups=GROUPS)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    doc = project.sarif
    results = results_by_id(doc)
    assert len(doc["runs"][0]["results"]) == len(FINDINGS), "each peer is counted once, as a result and nowhere else (FR-K7.1)"
    assignments = sc.correlation_assignments([(group, members) for group, members in GROUPS], OPEN_IDS)
    sc.self_check(doc["runs"][0]["results"], tool=TOOL, member_ids=OPEN_IDS, assignments=assignments, resolved_ids=RESOLVED_IDS, uri=URI)
    primary, peer = results["S-2"], results["S-10"]
    assert primary["message"]["text"] == "%s [Control: found] Correlated in CG-1; peers S-10." % by_id("S-2")["threat"]
    assert peer["message"]["text"] == "%s [Control: found] Correlated in CG-1; primary S-2." % by_id("S-10")["threat"]
    assert [primary["properties"][key] for key in sc.CORRELATION_KEYS] == ["CG-1", "primary", "S-2"]
    assert [peer["properties"][key] for key in sc.CORRELATION_KEYS] == ["CG-1", "peer", "S-2"]
    for result in results.values():
        assert all(not entry["message"]["text"].startswith(("S-", "T-", "R-", "I-", "D-", "E-", "AG")) for entry in result.get("relatedLocations", [])), \
            "relatedLocations hold code evidence only: no entry names a finding (D8)"
    assert results["S-2"]["partialFingerprints"] == sc.partial_fingerprints(TOOL, "S-2"), "a regroup is a property, never a key"
    plain = Project(stage, renderer, tmp_path / "plain")
    assert plain.run().code in (0, 5)
    assert {i: r["partialFingerprints"] for i, r in results_by_id(plain.sarif).items()} == {i: r["partialFingerprints"] for i, r in results.items()}


# =============================================================================
# 8. The two files agree, and the existing readers still read them (NFR-1)
# =============================================================================


def test_agree_the_md_and_the_sarif_agree_on_every_open_finding(base):
    results = results_by_id(base.sarif)
    rows = matrix_rows(base.md)
    read = read_findings(base.md)
    assert {canon(i) for i in results} == set(rows) == set(read)
    for finding_id, result in results.items():
        band, row = rows[canon(finding_id)]
        properties = result["properties"]
        assert (row["Inherent Score"], row["Residual Score"]) == (properties["inherent-risk"], properties["residual-risk"])
        assert properties["security-severity"] == properties["residual-risk"], "SARIF's severity is the residual score (Phase 6c)"
        assert tachi_parsers.classify_control_status(row["Control Status"])[0] == STATUS_CLASS[properties["control-status"]]
        assert result["level"] == sc.level_for_band(band) and slug(row["Control Category"]) == by_id(finding_id)["category"]
        assert properties["recommendation"] == read[canon(finding_id)]["recommendation"]
        assert properties["maestro-layer"] == row["MAESTRO Layer"]
        assert result["message"]["text"].startswith(row["Threat"])


def test_readers_the_existing_parsers_read_the_rendered_md_back(base):
    md = base.md
    result = tachi_parsers.parse_compensating_controls_md(md)
    rows = {canon(row["id"]): row for row in result["findings"]}
    assert sorted(rows, key=s2_key) == [canon(i) for i in S2_ORDER] and len(result["findings"]) == len(FINDINGS), "one row for each finding"
    for finding_id, row in rows.items():
        inherent, inherent_band, _factor, residual, residual_band = golden(finding_id)
        item = by_id(finding_id)
        assert (str(row["inherent"]), row["inherent_severity"], row["residual_score"], row["residual_severity"]) == (inherent, inherent_band, residual, residual_band)
        assert (row["status_class"], row["component"], row["carried_forward"]) == (STATUS_CLASS[item["control"]], item["component"], False), finding_id
        assert (row["maestro_layer"], slug(row["control_category"])) == (COMPONENTS[item["component"]][1], item["category"]), finding_id
    assert result["severity"] == {"critical": 1, "high": 2, "medium": 4, "low": 4, "note": 0, "total": 11}
    assert result["coverage_summary"] == {"total-found": 4, "total-partial": 4, "total-missing": 3}
    assert (result["inherent_score"], result["residual_score"], result["risk_reduction"], result["control_coverage_pct"]) == (80.0, 57.4, 28.3, 37.0)
    assert len(result["controls"]) == 9
    assert sorted((slug(c["category"]), c["evidence"]) for c in result["controls"]) == sorted(
        (category, "%s:%d" % (file, line)) for category, file, line, _ids in CONTROLS)
    assert sum(entry["found"] + entry["partial"] + entry["missing"] for entry in result["coverage_matrix"]) == len(FINDINGS)
    persisted = tachi_parsers.parse_controls_assessment_inputs(md)
    assert persisted["errors"] == [] and sorted(persisted["inputs"], key=s2_key) == [canon(i) for i in S2_ORDER]
    for item in FINDINGS:
        want = controls_item(item)
        want.pop("finding_id")
        assert persisted["inputs"][canon(item["id"])] == want, "the persisted inputs read back as the validated part (AR-T3): %s" % item["id"]


# =============================================================================
# 9. The staged write, and what a failure leaves behind (F2; ADR-050 D4; KB 21, 22)
# =============================================================================


def first_line_edit(prefix, change):
    """An edit of a staged markdown file: ``change`` applied to the first line that starts with ``prefix``."""
    def edit(text):
        lines = text.split("\n")
        index = next(n for n, line in enumerate(lines) if line.startswith(prefix))
        replaced = change(lines[index])
        if replaced is None:
            del lines[index]
        else:
            lines[index] = replaced
        return "\n".join(lines)
    return edit


def row_cell_edit(finding_id, column, value):
    """Set one Section 2 cell of one finding, found by the table's own header, so the edit follows the schema."""
    def edit(text):
        lines = text.split("\n")
        header = None
        for number, line in enumerate(lines):
            if not line.startswith("|"):
                header = None
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells[0] == "Threat ID":
                header = cells
            elif header and column in header and tp.id_matches("finding", cells[0]) and canon(cells[0]) == canon(finding_id):
                cells[header.index(column)] = value  # the first such row is Section 2's: Section 3 comes later
                lines[number] = "| " + " | ".join(cells) + " |"
                return "\n".join(lines)
        raise AssertionError("no Section 2 row for %s" % finding_id)
    return edit


def json_edit(change):
    """An edit of a staged SARIF file: parse it, change the document, write it back in the emitter's form."""
    def edit(text):
        document = json.loads(text)
        change(document)
        return json.dumps(document, indent=2, ensure_ascii=True) + "\n"
    return edit


def result_of(document, finding_id):
    return results_by_id(document)[finding_id]


def duplicate_a_result(document):
    document["runs"][0]["results"].append(copy.deepcopy(document["runs"][0]["results"][0]))


def add_a_resolved_result(document):
    extra = copy.deepcopy(document["runs"][0]["results"][0])
    extra["partialFingerprints"] = sc.partial_fingerprints(TOOL, "S-1")
    document["runs"][0]["results"].append(extra)


def set_property(finding_id, key, value):
    return lambda document: result_of(document, finding_id)["properties"].__setitem__(key, value)


# Each case seeds one renderer bug that only a check on the files read back from disk can see, and every one of them must
# stop the run before any canonical file is replaced (ADR-050 D4, steps 5 and 6).
CHECK_FAILURES = [
    ("md-lost-an-open-row", MD, first_line_edit("| E-5 |", lambda line: None)),
    ("md-a-residual-the-sarif-does-not-have", MD, row_cell_edit("S-2", "Residual Score", "4.7")),
    ("md-a-status-the-sarif-does-not-have", MD, row_cell_edit("AGP-01", "Control Status", "Control Found")),
    ("md-a-total-that-is-not-the-sum-of-the-rows", MD, first_line_edit("**Risk Reduction**:", lambda line: line.replace("80.0 inherent", "81.0 inherent", 1))),
    ("sarif-lost-a-result", SARIF, json_edit(lambda document: document["runs"][0]["results"].pop(0))),
    ("sarif-has-a-result-twice", SARIF, json_edit(duplicate_a_result)),
    ("sarif-names-a-resolved-finding", SARIF, json_edit(add_a_resolved_result)),
    ("sarif-a-residual-the-md-does-not-have", SARIF, json_edit(set_property("S-2", "security-severity", "1.0"))),
    ("sarif-a-status-the-md-does-not-have", SARIF, json_edit(set_property("AGP-01", "control-status", "found"))),
    ("sarif-a-recommendation-the-md-does-not-have", SARIF, json_edit(set_property("T-4", "recommendation", "A different recommendation."))),
]


def test_staged_both_files_are_checked_on_disk_before_either_replaces_a_canonical_file(project):
    log = []
    with watching_replace(log):
        res = project.run()
    assert res.code == 0, res.describe()
    out = os.path.abspath(str(project.out))
    moves = [entry for entry in log if os.path.dirname(entry[1]) == out and os.path.basename(entry[1]) in (MD, SARIF)]
    assert sorted(os.path.basename(dst) for _src, dst, _present, _seen in moves) == [MD, SARIF], "each canonical file is replaced once"
    for src, dst, _present, seen in moves:
        assert os.sep + "staged" + os.sep in src and os.path.basename(src) == os.path.basename(dst), "only a staged file replaces a canonical one"
        assert seen == sha256_of(dst), "the bytes that were staged are the bytes now in place"
    assert sorted(moves[0][2]) == [MD, SARIF], "both staged files are on disk before the first move, so the checks ran on them"
    assert max(log.index(entry) for entry in log if os.sep + "staged" + os.sep in entry[1]) < min(log.index(entry) for entry in moves)


@pytest.mark.parametrize("name,target,edit", CHECK_FAILURES, ids=[case[0] for case in CHECK_FAILURES])
def test_staged_a_failing_check_leaves_the_canonical_files_untouched(project, name, target, edit):
    project.earlier()
    project.prepare()
    with tampering_with_staged(target, edit):
        res = project.render()
    assert res.code == 4, "a completeness or parity check that fails is exit 4 (cli.md): %s" % res.describe()
    assert_failure_message(res, project.plan_id)
    project.assert_earlier_outputs_untouched()
    assert (project.plan_dir / "staged" / target).is_file(), "the staged file stays for diagnosis (KB 21)"
    failed = project.fail("check-failed")
    assert failed.code == 0, failed.describe()
    assert json.loads(failed.out)["moved"] == [] and json.loads(failed.out)["restored"] == [], "there was nothing to put back"
    project.assert_earlier_outputs_untouched()
    assert project.record["status"] == "failed" and project.record["error"]["code"] == "check-failed"


def test_staged_a_failing_check_on_a_first_run_leaves_no_canonical_file(project):
    project.prepare()
    with tampering_with_staged(MD, first_line_edit("| E-5 |", lambda line: None)):
        res = project.render()
    assert res.code == 4, res.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists(), "a failed run never leaves a file under a canonical name"


def test_failure_render_failed_a_move_that_fails_half_way_is_undone_by_fail(project):
    project.earlier()
    project.prepare()
    with failing_replace(SARIF):  # the markdown moves, then the SARIF's move fails: a half-applied pair
        res = project.render()
    assert res.code not in (0, 5), res.describe()
    assert_failure_message(res, project.plan_id)
    assert tp.file_digest(project.plan_dir / "plan.json") == project.digest
    failed = project.fail("render-failed", detail="the move failed")
    assert failed.code == 0, failed.describe()
    project.assert_earlier_outputs_untouched()
    assert project.record["status"] == "failed" and project.record["error"]["code"] == "render-failed"


def test_failure_render_failed_on_a_first_run_moves_the_half_written_file_aside(project):
    project.prepare()
    with failing_replace(SARIF):
        res = project.render()
    assert res.code not in (0, 5), res.describe()
    failed = project.fail("render-failed")
    assert failed.code == 0, failed.describe()
    assert not (project.out / MD).exists() and not (project.out / SARIF).exists()
    assert (project.plan_dir / "failed" / MD).is_file(), "kept for diagnosis, and under no name any auto-detect site would take"


@pytest.mark.parametrize("damage", ["missing", "invalid", "stale"])
def test_failure_a_batch_without_a_valid_part_is_never_rendered(project, damage):
    project.earlier()
    project.prepare(batch_size=4)  # three batches, all reconciled as done
    path = Path(project.batch_input("B002")["part_path"])
    if damage == "missing":
        path.unlink()
    elif damage == "invalid":
        path.write_bytes(b'{"schema": "tachi.part/1"}')
    else:  # a part that is valid for this batch but belongs to another plan
        stale = project.part_for("B002")
        stale["plan_id"] = "20250101T000000Z-0123456789ab"
        path.write_text(json.dumps(stale), encoding="utf-8")
    res = project.render()
    assert res.code in (1, 2, 4), "the renderer re-validates every part it reads: %s" % res.describe()
    assert_failure_message(res, project.plan_id)
    assert "B002" in res.err, "the message names the batch"
    project.assert_earlier_outputs_untouched()


# =============================================================================
# 10. Records: the stamp, the stage record, the declared-paths check (FR-E.7; NFR-5)
# =============================================================================


def test_record_the_stamp_and_the_digest_are_one_value_in_three_places(base):
    stamp = tp.read_stamp(base.md)
    sarif_stamp = base.sarif["runs"][0]["properties"]["tachi_provenance"]
    assert (sarif_stamp["renderer"], sarif_stamp["version"], sarif_stamp["input_digest"]) == (stamp["renderer"], stamp["version"], stamp["input_digest"])
    assert base.record["input_digest"] == stamp["input_digest"]


def test_record_the_stamp_reads_the_shipped_version_constant(project, monkeypatch):
    monkeypatch.setattr(tp, "VERSION", "9.8.7")
    res = project.run()
    assert res.code == 0, res.describe()
    assert tp.read_stamp(project.md)["version"] == "9.8.7", "the goldens read tachi_parts.VERSION, never a literal (D4)"
    assert project.sarif["runs"][0]["properties"]["tachi_provenance"]["version"] == "9.8.7"
    assert project.record["tachi_version"] == "9.8.7"


def test_record_the_stage_record_is_valid_and_complete(base):
    record = base.record
    tp.validate_stage_record(record)
    assert (record["schema"], record["stage"], record["plan_id"]) == ("tachi.stage-record/1", STAGE, base.plan_id)
    assert (record["status"], record["error"], record["tachi_version"]) == ("success", None, tp.VERSION)
    assert DIGEST.match(record["input_digest"])
    assert record["started_utc"] <= record["finished_utc"]
    counts = record["counts"]
    assert (counts["units"], counts["open"], counts["rendered"]) == (len(FINDINGS), len(FINDINGS), len(FINDINGS))
    assert [counts.get(key, 0) for key in ("parse_errors", "narrative_fallbacks", "truncations")] == [0, 0, 0]
    assert record["batches"] == {"planned": 1, "dispatched": 1, "done": 1, "retried": 0, "split": 0, "exhausted": 0}
    assert (record["overflow_events"], record["retries"], record["warnings"], record["undeclared_paths"]) == ([], [], [], [])
    assert sorted(record["outputs"], key=lambda entry: entry["path"]) == sorted(
        [{"path": MD, "sha256": sha256_of(base.out / MD)}, {"path": SARIF, "sha256": sha256_of(base.out / SARIF)}],
        key=lambda entry: entry["path"]), "paths are relative to --out, and each digest is the file in place"


def test_record_an_undeclared_path_exits_5_and_still_writes_both_files(project):
    project.prepare()
    (project.out / "gen.py").write_text("print('a helper nobody declared')\n", encoding="utf-8")
    res = project.render()
    assert res.code == 5, res.describe()
    record = project.record
    assert (record["status"], record["undeclared_paths"]) == ("success-with-warnings", ["gen.py"]), "SC-3 is measured, not gated (KB 17)"
    assert len(project.sarif["runs"][0]["results"]) == len(FINDINGS) and has_section(project.md, "## 7. Analysis Integrity")
    tp.validate_stage_record(record)
    assert re.search(r"gen\.py", res.out), "the summary lines carry the warning: " + res.describe()


def test_record_a_path_the_run_changed_but_declared_is_not_reported(project):
    project.earlier()  # the earlier outputs are in the plan's snapshot, so the render changes them: declared
    project.prepare()
    res = project.render()
    assert res.code == 0, res.describe()
    assert project.record["undeclared_paths"] == []


def test_record_every_file_the_run_wrote_is_a_declared_path(base):
    """The renderer's own writes are the stage's canonical files and D3's layout, nothing else (ADR-050 D4)."""
    snapshot = base.plan_json()["out_snapshot"]
    written = []
    for path in sorted(base.out.rglob("*")):
        if path.is_file():
            relpath = path.relative_to(base.out).as_posix()
            status = path.stat()
            if snapshot.get(relpath) != [status.st_size, status.st_mtime_ns]:
                written.append(relpath)
    assert written, "the render wrote files"
    assert [relpath for relpath in written if not tp.is_declared_path(relpath, STAGE, base.plan_id)] == []
    assert {MD, SARIF, ".tachi-build/%s/%s/stage-record.json" % (STAGE, base.plan_id)} <= set(written)


def test_record_a_record_lists_at_most_the_cap_of_undeclared_paths_and_warns_with_the_full_count(project):
    project.prepare()
    extra = 5
    for number in range(tp.MAX_UNDECLARED_PATHS + extra):
        (project.out / ("stray-%04d.txt" % number)).write_text("x\n", encoding="utf-8")
    res = project.render()
    assert res.code == 5, res.describe()
    record = project.record
    assert record["undeclared_paths"] == sorted(record["undeclared_paths"]) and len(record["undeclared_paths"]) == tp.MAX_UNDECLARED_PATHS
    truncated = [warning for warning in record["warnings"] if warning["code"] == "undeclared-paths-truncated"]
    assert len(truncated) == 1 and str(tp.MAX_UNDECLARED_PATHS + extra) in truncated[0]["detail"], "ruled at W1: the full count is in the warning"
    tp.validate_stage_record(record)
    assert len(project.sarif["runs"][0]["results"]) == len(FINDINGS), "a stray file never stops the render (KB 17)"


# =============================================================================
# 11. Batching and determinism (NFR-4, NFR-2; ADR-050 D4, D5, D6)
# =============================================================================


def test_batching_a_run_at_the_batch_size_invokes_the_agent_once(project, stage):
    res = project.run()
    assert res.code == 0, res.describe()
    plan = project.plan_json()
    assert plan["unit_count"] == len(FINDINGS) <= stage.BATCH_SIZES[STAGE] and [b["batch_id"] for b in plan["batches"]] == ["B001"]
    assert project.record["batches"]["planned"] == 1 and project.record["batches"]["dispatched"] == 1


@pytest.mark.parametrize("batch_size", [1, 3, 4])
def test_batching_a_run_in_several_batches_writes_the_same_bytes_as_one_batch(project, batch_size):
    assert project.run().code == 0
    one_batch = project.outputs()
    res = project.run(batch_size=batch_size)  # the planner's function interface: the one way a test sets a smaller size
    assert res.code == 0, res.describe()
    assert project.record["batches"]["planned"] == math.ceil(len(FINDINGS) / batch_size) > 1
    assert project.outputs() == one_batch, "the batch boundaries show nowhere in the output (NFR-2)"


def test_batching_a_halved_batch_writes_the_same_bytes_as_one_batch(project):
    assert project.run().code == 0
    one_batch = project.outputs()
    project.plan(batch_size=4)  # B001, B002, B003
    project.write_parts(only={"B002", "B003"})  # B001's agent ran out of room, so it wrote nothing
    first = project.reconcile()
    assert first.code == 3, first.describe()
    pending = sorted(batch["batch_id"] for wave in json.loads(first.out)["waves"] for batch in wave)
    assert pending == ["B001-1", "B001-2"]
    project.write_parts(only=set(pending))
    assert project.reconcile().code == 0
    res = project.render()
    assert res.code == 0, res.describe()
    assert project.outputs() == one_batch
    record = project.record
    assert record["batches"] == {"planned": 3, "dispatched": 5, "done": 4, "retried": 2, "split": 1, "exhausted": 0}
    events, retries = tp.retry_history(STAGE, project.out, project.plan_json())
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "missing"}]
    assert (record["overflow_events"], record["retries"]) == (events, retries)


def test_determinism_the_output_is_byte_identical_under_a_patched_clock(project):
    moments = [datetime.datetime(2020, 2, 29, 12, 0, 0, tzinfo=datetime.timezone.utc),
               datetime.datetime(2031, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc)]
    runs = []
    for moment in moments:
        with frozen_clock(moment):
            res = project.run()
        assert res.code == 0, res.describe()
        runs.append((project.outputs(), project.plan_id, project.record))
    res = project.run()  # the real clock
    assert res.code == 0, res.describe()
    runs.append((project.outputs(), project.plan_id, project.record))
    assert runs[0][0] == runs[1][0] == runs[2][0], "the clock never enters a rendered file (ADR-050 D5), and the plan ID never does (D4)"
    assert len({plan_id for _outputs, plan_id, _record in runs}) == 3
    for moment, (_outputs, _plan, record) in zip(moments, runs):
        assert record["finished_utc"] == moment.strftime("%Y-%m-%dT%H:%M:%SZ"), "the clock reaches the stage record, and only there"


def test_determinism_rendering_the_same_plan_again_changes_no_byte(project):
    assert project.run().code == 0
    first = project.outputs()
    again = project.render()
    assert again.code == 0, again.describe()
    assert project.outputs() == first


def test_determinism_the_date_is_the_plans_and_moves_the_frontmatter_and_the_digest(project):
    assert project.run().code == 0
    first = tp.read_stamp(project.md)["input_digest"]
    res = project.run(date="2027-03-05")
    assert res.code == 0, res.describe()
    assert frontmatter_value(project.md, "date") == "2027-03-05"
    shown = {row[0]: row[1] for row in table_of(section(project.md, "## 1. Executive Summary"), "Metric")[1]}
    assert shown["Analysis date"] == "2027-03-05"
    assert tp.read_stamp(project.md)["input_digest"] != first, "the date is a parameter of the input digest (ADR-050 D4)"


def test_determinism_the_input_digest_follows_the_inputs_and_not_the_plan(project):
    assert project.run().code == 0
    first = tp.read_stamp(project.md)["input_digest"]
    assert project.run().code == 0 and tp.read_stamp(project.md)["input_digest"] == first, "a fresh plan ID, the same digest"

    def reword(part):
        part["items"][0]["evidence"][0]["summary"] = "A different summary of the control."

    assert project.run(mutate=reword).code == 0
    assert tp.read_stamp(project.md)["input_digest"] != first, "an accepted part's items are in the digest"


def test_determinism_no_local_path_reaches_either_file(base):
    for text in (base.md, base.sarif_text):
        assert not LOCAL_PATH.search(text), "a local path in the output leaks the layout and differs between machines (NFR-2, NFR-6)"
        for path in {str(base.root), str(base.out), str(base.target), os.path.realpath(str(base.root))}:
            assert path not in text, "the project's own path is in the output: %s" % path


# =============================================================================
# 12. The agent's narrative: the per-field fallback, cuts and hostile text (ADR-050 D3; PM rulings 1 and 2)
# =============================================================================


def damage_two_fields(part):
    for item in part["items"]:
        if canon(item["finding_id"]) == "T-1":
            item["evidence"][0]["assessment"]["coverage"]["rationale"] = "There are 3 gaps in coverage."  # a digit outside a slot
        if canon(item["finding_id"]) == "AG-1":
            item["evidence"][0]["summary"] = "x" * 161  # one over the limit of 160


def test_narrative_a_bad_field_takes_its_fixed_sentence_and_a_long_one_is_cut_and_both_are_flagged(project):
    res = project.run(mutate=damage_two_fields)
    assert res.code in (0, 5), res.describe()  # reading: a fallback is a flag and a count, not a warning
    fallback_flag, cut_flag = "input:evidence.assessment.coverage:narrative-fallback", "input:evidence.summary:truncated"

    sentence = tp.FALLBACK_SENTENCES["evidence.assessment.coverage"]
    block = next(body for cat, heading, body in control_blocks(project.md) if "`src/validate/schema.py:17`" in body and slug(cat) == "input-validation")
    assert sentence in block and "gaps in coverage" not in project.md, "the field's text is gone, and the row is not"
    assert "x" * 160 in project.md and "x" * 161 not in project.md

    results = results_by_id(project.sarif)
    assert results["T-1"]["properties"]["integrity-flags"] == [fallback_flag]
    assert results["AG-1"]["properties"]["integrity-flags"] == [cut_flag]
    assert all(results[i]["properties"]["integrity-flags"] == [] for i in OPEN_IDS if i not in ("T-1", "AG-1"))

    body = section(project.md, "## 7. Analysis Integrity")
    for finding_id, flag in (("T-1", fallback_flag), ("AG-1", cut_flag)):
        kind, field, cause = flag.split(":")
        assert any(finding_id in line and kind in line and field in line and cause in line for line in body.split("\n")), \
            "Section 7 lists each finding's flags (FR-K7.4): %s" % flag

    counts = project.record["counts"]
    assert counts["narrative_fallbacks"] == 1 and counts["truncations"] == 1 and counts["input"] >= 2

    persisted = tachi_parsers.parse_controls_assessment_inputs(project.md)["inputs"]
    assert persisted["T-1"]["evidence"][0]["assessment"]["coverage"]["rationale"] == sentence, "the validated text is what is carried"
    assert persisted["AG-1"]["evidence"][0]["summary"] == "x" * 160


# =============================================================================
# 13. The 1.1 template and the renderer agree (D15; they skip until T060 lands, and then pin it)
# =============================================================================


def template_text(name):
    return (TEMPLATES / name).read_text(encoding="utf-8")


def require_the_1_1_template():
    if not re.search(r"Schema version\s*:\s*1\.1\b", template_text(MD)):
        pytest.skip("the controls template is still 1.0: T060 (lane D) brings it to 1.1")


def test_template_the_markdown_template_is_schema_1_1_and_has_the_renderers_sections():
    require_the_1_1_template()
    text = template_text(MD)
    for heading in SECTION_TITLES + ["### Assessment Inputs", "### Input Issues"]:
        assert re.search(r"(?m)^%s\b" % re.escape(heading), text), "the template has no %r, which the renderer writes" % heading
    assert re.search(r'(?m)^schema_version: "1\.1"$', text)


def test_template_section_2_has_the_k8_header_the_renderers_goldens_assume():
    require_the_1_1_template()
    headers = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in template_text(MD).split("\n") if line.startswith("| Threat ID ")]
    bands = [header for header in headers if "Residual Severity" in header]  # Section 3's "Threats Mitigated" table has its own header
    assert len(bands) == 4 and all(header == K8_HEADER for header in bands), "T056's goldens and the part's matrix_row read these cells by position"


def test_template_the_sarif_template_carries_the_real_information_uri():
    require_the_1_1_template()
    document = json.loads(template_text(SARIF))
    assert document["runs"][0]["tool"]["driver"]["informationUri"] == sc.INFORMATION_URI, "FR-E.9 (#412)"


# =============================================================================
# 14. The entry's shape (H15)
# =============================================================================


def test_cli_the_entry_keeps_the_populators_shape(renderer):
    parameters = inspect.signature(renderer.main).parameters
    assert list(parameters) == ["argv"] and parameters["argv"].default is None
    tree = ast.parse(RENDERER.read_text(encoding="utf-8"))
    guards = [node for node in tree.body if isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
              and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"]
    assert guards, "a __main__ guard"
    guard = guards[-1]
    assert len(guard.body) == 1 and "main" in ast.dump(guard.body[0]), "a thin guard: the work is in main(argv)"
