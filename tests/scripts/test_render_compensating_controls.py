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
   ``message`` is ``{text, markdown}`` (P0-8, extended to this file at W3): the markdown is the reference set's
   mitigation text, ``""`` when the finding has none, and under D8's fallback the source result's ``markdown`` (or ``""``);
   and the zone and DFD kind of a result's logical location come from ``threats.md`` as the scorer renderer takes them.

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
* ``test_r34_*`` (Section 15 at the end, written by T056 before T059): R-34's cell-by-cell goldens for Sections 2 and
  4, the carried rows (AR-T3, AR-T4) and ``CF``. They need the whole renderer, so they wait for T035 and T059; the list
  at the head of Section 15 says which of the two turns each group green.
* Section 16 (T056 too): the gaps that T035's own goldens left (D8's fallback, the baseline, the inputs' forbidden
  characters, the evidence file, the shift table's cap, the failure path) and the SARIF as the 1.1 template shows it
  (``message.markdown``, the rules' ``relationships``, the properties' order). They wait for T035, T053 and T060.
* Section 17 (T056's third instance, from the architect's W3 sweep): a snippet that quotes headings and an inputs table, over two
  runs (ADR-050 D3, "Finding a section"); the architecture source with no flag, where a URI is never the snapshot's (D7); and gap B,
  where every controls result's ``maestro-layer`` is the scorer's, under D8's fallback and with no readable ``threats.md``.
* Section 18 (the same instance, from lane R2's proposals for T053 and T059, and from the architect's quick rulings at W3): the SARIF's
  driver, rules and properties as the template shows them, D8's fallback member by member, the from-disk checks' seeded bugs, the ``ref``
  slot, the evidence file (its URI, a file that the resolver refuses, and one removed between two runs), the logical location's defaults,
  a RESOLVED ID in copied text, and Section 1's line, a row that is overwritten and flagged, and a carried row whose input moved.

The architect's quick rulings at W3 (ADR-050 D2's "Rulings at W3", and the contracts they amend) are pinned where they apply: the overwrite
count is ``counts.cell_overwrites`` (Section 15), the four row checks' strings and Section 2's as-written cell (``test_r34_flag_*``), every
list of finding IDs names at most ten (``test_md_section_5_*``, Section 1's line and the cleared claims' Input Issue), an evidence file that
the resolver refuses is flagged and never exit 2 (Section 18), and a mention of a RESOLVED ID in copied text renders cleanly (Section 18, and
the S-1 variant of Section 17).

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
import shutil
import sys
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script
from .test_render_risk_scores import (
    COMPONENTS, DASH, DATE, DIGEST, KIND_OF, LOCAL_PATH, RESOLVED, RESOLVED_IDS, URI, ZONES, canon, decode, frozen_clock,
    has_section, invoke, make_architecture_md, make_threats_md, mitigation_of, records, s2_key, section, section_text,
    sha256_of, split_headings, subsection_of, table_of, tables, tree_state, working_directory)

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
        saved = self.stage._refuse_forbidden_units
        self.stage._refuse_forbidden_units = lambda *args: None  # the renderer's own refusal is under test, so the planner's earlier one (T146 SA-1) is off
        try:
            with working_directory(self.root), contextlib.redirect_stderr(err):
                result = self.stage.plan_stage(stage=STAGE, out=self.out, date=date, threats=self.threats, risk_scores=self.risk_scores,
                                               architecture=explicit, target=self.target, baseline_dir=baseline_dir, batch_size=batch_size)
        finally:
            self.stage._refuse_forbidden_units = saved
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
        assert label_ids(plain[label][2]) == sorted(canon(i) for i in ids), \
            "%s names the IDs of its shift (at most ten findings are named in full: the cap is ruled at W3, see test_md_section_5_the_examples_cell_names_at_most_ten_ids)" % label
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
        assert result["message"] == {"text": "%s [Control: %s]" % (item["threat"], item["control"]), "markdown": mitigation_of(item)}, \
            "the full threat text of the reference set with a status suffix, and its mitigation as the markdown (P0-8: the key is always written)"
        assert list(result["message"]) == ["text", "markdown"], "the markdown follows the text"
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
    """ADR-050 D2: "read from each §4 body by ``parse_compensating_controls_md``'s rule", so a consumer reads one text in either file.
    The text is what the shipped reader returns from the rendered file, and also the agent's own What and Effort. The from-disk check does not
    take it from the file by the function that built the SARIF: it derives it again from the validated body (T067b H1; see the seeded readers
    in ``test_capture_a_defect_in_the_reader_that_builds_the_sarifs_recommendations_fails_the_from_disk_check``)."""
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
    assert (primary["message"]["markdown"], peer["message"]["markdown"]) == (mitigation_of(by_id("S-2")), mitigation_of(by_id("S-10"))), \
        "ruling C's sentence ends the text, not the markdown"
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
    ("sarif-an-emptied-recommendation", SARIF, json_edit(set_property("T-4", "recommendation", ""))),   # the shape of T067b H1's loss
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


def section_7_shape(md):
    """Section 7 as ``[(subsection heading, the header cells of its first table or None)]``, in file order: what a reader of the file sees of its form."""
    return [(heading, table_of(body)[0] if tables(body) else None) for heading, body in split_headings(section_text(md, "## 7. Analysis Integrity"), "### ")]


def test_template_section_7_has_the_subsections_and_table_headers_that_the_renderer_writes(base):
    """T067b M2. The 1.1 template is the contract for the file (NFR-1's field scope names it, and an adopter or an oracle reads it), so its Section 7 holds the
    subsections that the renderer writes, in the renderer's order, and each table under the header that the renderer gives it: an Integrity Summary
    (``Kind | Cause | Count``), then Finding Flags (``ID | Flag | Field | Cause``), then Input Issues, which has no table, and Assessment Inputs.
    The controls flags compare no two values, so the table has no Stored or Rendered column, and no subsection is called Integrity Flags (the
    template once showed an ``### Integrity Flags`` table of six columns, which the renderer never wrote)."""
    require_the_1_1_template()
    written = section_7_shape(base.md)
    assert written == [("### Integrity Summary", ["Kind", "Cause", "Count"]), ("### Finding Flags", ["ID", "Flag", "Field", "Cause"]),
                       ("### Input Issues", None), ("### Assessment Inputs", ["ID", "Field", "Value"])], "what the renderer writes"
    assert section_7_shape(template_text(MD)) == written, "the template's Section 7 is not the form that the renderer writes"


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


# =============================================================================
# 15. R-34: Sections 2 and 4, cell by cell, and the carried rows (T056; written before T059)
# =============================================================================
#
# ADR-050 D2's table "Controls Sections 2 and 4 in PR 1 (R-34), cell by cell" says what the renderer does with each cell of the
# agent's Section 2 row (``matrix_row``) and with its Section 4 body (``recommendation_body``), and the W3 rulings pin the row's
# form and ``CF`` (``contracts/module-signatures.md``, "The controls ``matrix_row``"). Every line of that table has its goldens
# below, driven as the command drives them: the real planner, a part for each batch, ``reconcile``, the renderer, and then a
# reader of the files. The groups, and what turns each green:
#
# * ``test_r34_fill_*``: the band tables, header and order, and the four computed cells, overwritten by position and counted.
# * ``test_r34_cf_*``: ``CF`` is the renderer's cell, from the accepted ``carried_forward``, and it is never counted.
# * ``test_r34_reject_*``: the Threat ID and the 11-cell count, and Section 4's body, reject the item.
# * ``test_r34_flag_*``: a Control Status, Control Category, Component or MAESTRO Layer cell that disagrees is flagged.
# * ``test_r34_section_4_*``: Section 4's group, order, number, heading and Current Status are written by the renderer.
# * ``test_r34_carry_*``: the carried row (AR-T3), the carried narrative (AR-T4), ``carry_forward_count`` and byte identity.
#
# What turns them green: every case needs T035 (the whole file, Section 7, the records), and most read the SARIF too
# (``assert_same_as_clean``, ``flags_of``), so they need T053. Past those two, T059 turns green the overwrite counts, the four
# flagged checks, the Threat cell, Section 4's body checks and the carried runs' counts. The reject group is turned by D3 step 9's
# structural checks, which run in ``tachi_parts.read_part`` (FX0c): a part that breaks one is ``invalid``, so ``reconcile`` re-dispatches.
#
# The architect ruled T056's open readings 1, 2, 3, 6 and 7 at W3 (the quick rulings, questions 1 to 3, with the part validator that
# FX0c built), and the goldens now pin the rulings:
#
# 1. The overwrite count is the stage record's ``counts.cell_overwrites``, an eighth base count (``part-files.md`` section 5, ADR-050
#    D2). The controls renderer always writes it, ``0`` included, once for each computed cell that held anything but its own slot
#    token, and ``CF`` is never counted. It raises no flag, and it isn't added to ``corrected``, which the controls record never holds.
# 2. The four row checks flag ``input:control_status:sources-disagree``, ``input:control_category:sources-disagree``,
#    ``input:component:sources-disagree`` and ``input:maestro_layer:sources-disagree``, each at most once for a finding and counted
#    under ``counts.input`` (``module-signatures.md``, "The controls renderer's flag vocabulary, closed"). Section 1's ``>`` lines
#    and Section 7 name the finding.
# 3. Section 2 shows a mismatched cell as the agent wrote it, escaped. The SARIF, every total, Sections 3 to 6 and the from-disk
#    checks follow the structured value ("check" is not "fill": FR-K8.1's follow-up makes them fills).
# 6. A cleared ``carried_forward`` claim raises no flag. The stage record's warning ``carried-forward-cleared`` and an Input Issue line
#    record it, and what Section 7 keeps for it is the cleared value (false), so that the next run copies no claim.
# 7. A structural mismatch in the row or the body rejects the item at the part, not at the render: ``tachi_parts.read_part`` finds
#    the part ``invalid``, ``reconcile`` re-dispatches the batch (exit 3, attempt 2), and the second part renders what a clean run
#    renders (``assert_rejected``). The renderer reads every part through ``read_part`` again, and refuses one that was damaged since
#    (Section 18).
#
# Readings that no contract states are marked ``# reading:`` where they are used, and each sits in one helper or one line, so that a
# ruling is a small change:
#
# 4. Section 4's three group headings are the 1.0 template's, and its numbers run unbroken across the groups, as in every shipped example.
# 5. Section 2's Threat ID cell is Section 7's spelling of the ID, whichever allow-listed spelling of it the agent wrote.
# 8. Section 2's Threat cell is the agent's text, escaped and never flagged (D2: "model text (NFR-10 only)"). Lane R2's T035
#    writes the reference set's text there, so ``test_r34_flag_section_2_threat_*`` waits for T059.
# 9. A baseline that resolved and carried nothing has ``carry_forward_count`` 0 and scope ``full`` ("null when no baseline");
#    a directory with no controls file, or an unreadable one, is no baseline (null). Section 16 names the scorer's warning codes
#    for these (``baseline-unresolved``, ``baseline-unreadable``, ``value-not-in-form``, ``duplicate-finding-id``).

COMPUTED_CELLS = ("Inherent Score", "Inherent Severity", "Residual Score", "Residual Severity")
SLOT_OF = dict(zip(COMPUTED_CELLS, ("{{score:inherent}}", "{{band:inherent}}", "{{score:residual}}", "{{band:residual}}")))
BASE_COUNTS = ("units", "open", "resolved", "rendered", "parse_errors", "narrative_fallbacks", "truncations",
               "cell_overwrites")  # part-files.md section 5: the eight base counts, the eighth ruled at W3 (controls only)
FLAG_OF = {  # the closed strings of the four row checks (module-signatures.md, "The controls renderer's flag vocabulary"), by the cell they check
    "Control Status": "input:control_status:sources-disagree", "Control Category": "input:control_category:sources-disagree",
    "Component": "input:component:sources-disagree", "MAESTRO Layer": "input:maestro_layer:sources-disagree"}
UNRESOLVED_FLAG = "input:evidence.file:unresolved"  # an evidence file that the resolver refuses at render time (part-files.md), once per finding
GROUP_OF = {"Critical": "### Critical / High Risk Gaps", "High": "### Critical / High Risk Gaps", "Medium": "### Medium Risk Gaps",
            "Low": "### Low Risk Gaps"}  # reading 4
S2_ID = "S-2"  # the finding that the single-cell cases edit: inherent 9.1 (Critical), residual 4.6 (Medium), found


# --------------------------------------------------------------------------- the agent's row and body, edited

def row_cells(row):
    """A Section 2 row's cells as ``module-signatures.md`` has the renderer read them: edge whitespace dropped, one leading and
    one trailing ``|`` dropped where present, a split on raw ``|``, and each cell stripped."""
    text = row.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") else text
    return [cell.strip() for cell in text.split("|")]


def join_row(cells):
    """The canonical form: ``| `` before the first cell, `` | `` between cells and `` |`` after the last."""
    return "| " + " | ".join(cells) + " |"


def edit_item(finding_id, change):
    """A ``mutate`` for ``Project.write_parts``: ``change(item)`` on the part's item for ``finding_id``, in whichever batch it is."""
    def mutate(part):
        for item in part["items"]:
            if canon(item["finding_id"]) == canon(finding_id):
                change(item)
    return mutate


def with_cells(finding_id, changes):
    """The agent wrote ``changes`` (``{K8 column: text}``) in those cells of its row for ``finding_id``, and its own text in the rest."""
    def change(item):
        cells = row_cells(item["matrix_row"])
        assert len(cells) == len(K8_HEADER), "the harness's own row has 11 cells"
        for name, text in changes.items():
            cells[K8_HEADER.index(name)] = text
        item["matrix_row"] = join_row(cells)
    return edit_item(finding_id, change)


def with_row(finding_id, row):
    return edit_item(finding_id, lambda item: item.__setitem__("matrix_row", row))


def with_body(finding_id, body):
    return edit_item(finding_id, lambda item: item.__setitem__("recommendation_body", body))


def every_item(change):
    def mutate(part):
        for item in part["items"]:
            change(item)
    return mutate


def together(*mutations):
    def mutate(part):
        for each in mutations:
            each(part)
    return mutate


def the_agent_wrote_the_numbers(finding_id):
    """An agent that writes the four computed cells out in full (the right numbers, which are still not the slot tokens)."""
    inherent, inherent_band, _factor, residual, residual_band = golden(finding_id)
    return with_cells(finding_id, dict(zip(COMPUTED_CELLS, (inherent, inherent_band, residual, residual_band))))


# --------------------------------------------------------------------------- reading the records and the files

def gained_counts(record):
    """The stage record's counts beyond the eight base counts: ``part-files.md`` section 5's flag counts by kind (``input``, ``reused-id``)."""
    return {key: value for key, value in record["counts"].items() if key not in BASE_COUNTS and value}


def overwrites(record):
    """``counts.cell_overwrites``: the computed Section 2 cells that held anything but their own slot token (ADR-050 D2, ruled at W3). The
    controls renderer always writes it, ``0`` included, and never adds it to ``corrected``, a flag kind that the controls file doesn't raise."""
    counts = record["counts"]
    assert "cell_overwrites" in counts, "the stage record has no cell_overwrites count, which the controls renderer always writes: %s" % counts
    assert "corrected" not in counts, "an overwrite is no corrected flag, and the controls file raises none: %s" % counts
    return counts["cell_overwrites"]


def assert_nothing_counted(record):
    """No computed cell was overwritten and no flag was raised: ``cell_overwrites`` is 0, and no flag kind has a count. A case that is about
    something else uses this, so it doesn't need the count to be written: ``test_r34_fill_a_clean_run_counts_no_overwrite`` pins that, and the
    carried run of ``test_r34_carry_run_1s_numbers...`` reads it by name."""
    counts = record["counts"]
    assert counts.get("cell_overwrites", 0) == 0 and "corrected" not in counts, counts
    assert gained_counts(record) == {}, counts


def id_pattern(finding_id):
    """A regex for ``finding_id`` in any spelling that canonicalizes to it (``AGP-01`` and ``AGP-1``), as a whole token."""
    prefix, _dash, number = canon(finding_id).partition("-")
    return r"(?<![A-Za-z0-9-])%s-0*%s(?![A-Za-z0-9-])" % (re.escape(prefix), number)


def flags_of(doc):
    """``{finding ID as the SARIF spells it: its integrity-flags}``."""
    return {finding_id: result["properties"]["integrity-flags"] for finding_id, result in results_by_id(doc).items()}


def row_check_flags(flags):
    """The flags in ``flags`` that are one of the four row checks' strings (``FLAG_OF``), in the order they stand."""
    return [flag for flag in flags if flag in FLAG_OF.values()]


def integrity_text(md):
    """Section 7 up to its ``### Assessment Inputs``: where D2 lists input issues, row checks and each finding's flags (FR-K7.4)."""
    return section(md, "## 7. Analysis Integrity").split("### Assessment Inputs")[0]


def warning_lines(md):
    """The ``>`` lines of Section 1, where the template puts the analysis warnings (``> {analysis_warnings}``)."""
    return [line for line in section(md, "## 1. Executive Summary").split("\n") if line.startswith(">")]


def persisted(md):
    """``{canonical ID: item}`` read back from Section 7's Assessment Inputs, as the next run's planner reads them (T143)."""
    return tachi_parsers.parse_controls_assessment_inputs(md)["inputs"]


def inputs_table(md):
    """Section 7's Assessment Inputs table as ``(header, rows)``, decoded."""
    return table_of(subsection_of(md, "## 7. Analysis Integrity", "### Assessment Inputs"), "ID")


def sarif_without_flags(doc):
    """A SARIF document's results and rules with each result's ``integrity-flags`` taken out, the one property that a flagged run adds to."""
    run = copy.deepcopy(doc["runs"][0])
    for result in run["results"]:
        result["properties"].pop("integrity-flags", None)
    return {"results": run["results"], "rules": run["tool"]["driver"]["rules"]}


def the_other_sections(md):
    """Sections 3 to 6, which no cell of Section 2 or 4 reaches."""
    return {title: section(md, title) for title in SECTION_TITLES[2:6]}


def without_warnings(text):
    """``text`` without its ``>`` lines, and with runs of blank lines folded, so that a flagged run's Section 1 reads as the clean run's."""
    kept = "\n".join(line for line in text.split("\n") if not line.startswith(">"))
    return re.sub(r"\n{3,}", "\n\n", kept).strip("\n")


def assert_same_as_clean(project, clean, open_cells=None, carried_differs=False, without_related=False):
    """``project``'s files hold what the clean render's do: the SARIF (bar ``integrity-flags``), Sections 3 to 6, Section 1 (bar its
    warnings); and Section 2, bar the cells that ``open_cells`` (``{canonical ID: (column, ...)}``) leaves open. That is how the goldens
    say "SARIF and totals follow the structured value", and that a cell is "filled", not "checked". With ``carried_differs`` the
    ``CF`` column and the SARIF's ``control-carry-forward`` are left open for every finding, as a follow-up run differs in them. With
    ``without_related`` so is each result's ``relatedLocations``, which an evidence file that the resolver refuses is left out of."""
    def results_of(doc):
        data = sarif_without_flags(doc)
        for result in data["results"]:
            if carried_differs:
                result["properties"]["control-carry-forward"] = None
            if without_related:
                result.pop("relatedLocations", None)
        return data

    assert results_of(project.sarif) == results_of(clean.sarif)
    assert the_other_sections(project.md) == the_other_sections(clean.md)
    one, two = "## 1. Executive Summary", "## 2. Coverage Matrix"
    assert without_warnings(section(project.md, one)) == without_warnings(section(clean.md, one))
    open_cells = dict(open_cells or {})
    if carried_differs:
        open_cells = {finding_id: tuple(open_cells.get(finding_id, ())) + ("CF",) for finding_id in matrix_rows(clean.md)}
    if not open_cells:
        assert section(project.md, two) == section(clean.md, two)
        return
    assert [(band, [row["Threat ID"] for row in rows]) for band, _h, rows in band_tables(project.md)] == [
        (band, [row["Threat ID"] for row in rows]) for band, _h, rows in band_tables(clean.md)], "the same rows under the same bands, in the same order"
    mine, theirs = matrix_rows(project.md), matrix_rows(clean.md)
    assert sorted(mine) == sorted(theirs)
    for finding_id, (band, row) in mine.items():
        left = {name: text for name, text in row.items() if name not in open_cells.get(finding_id, ())}
        right = {name: text for name, text in theirs[finding_id][1].items() if name not in open_cells.get(finding_id, ())}
        assert (band, left) == (theirs[finding_id][0], right), finding_id
    summary = "### Summary Statistics"
    assert subsection_of(project.md, two, summary) == subsection_of(clean.md, two, summary)


# --------------------------------------------------------------------------- running a project, and following it up

def run_ok(stage_module, renderer_module, root, mutate=None, findings=None, **run_options):
    """One render of the eleven findings (or ``findings``), with the agent's part edited by ``mutate``; it finishes (exit 0 or 5)."""
    project = Project(stage_module, renderer_module, root, findings=findings)
    res = project.run(mutate=mutate, **run_options)
    assert res.code in (0, 5), res.describe()
    tp.validate_stage_record(project.record)
    return project


def follow_up(stage_module, renderer_module, root, previous, statuses=None, default="UNCHANGED", with_baseline=True):
    """The next run of the same project: ``threats.md`` names ``baseline/threats.md`` as its baseline, and the baseline is the previous
    run's own files, copied there (``run_carried`` then passes ``baseline_dir=follow.baseline`` to the planner). Each finding has the
    delta status that ``statuses`` (``{canonical ID: status}``) gives it, else ``default``. With ``with_baseline`` false the baseline
    directory holds no controls file."""
    follow = Project(stage_module, renderer_module, root,
                     findings=[dict(item, status=(statuses or {}).get(canon(item["id"]), default)) for item in previous.findings],
                     resolved=previous.resolved, baseline_source="baseline/threats.md")
    follow.baseline = Path(root) / "baseline"
    follow.baseline.mkdir()
    for name in (("threats.md", "risk-scores.md", MD, SARIF) if with_baseline else ("threats.md", "risk-scores.md")):
        if (previous.out / name).is_file():
            shutil.copyfile(str(previous.out / name), str(follow.baseline / name))
    return follow


def carried(previous_md, only=None):
    """What a controls agent hands in for an UNCHANGED finding (its instructions: copy the baseline's values as they stand, and set
    ``carried_forward``): the previous run's persisted inputs, decoded (T143's reader, which the planner reads them through, AR-T3), for
    the findings in ``only`` (canonical IDs), or for all."""
    inputs = persisted(previous_md)

    def mutate(part):
        for index, item in enumerate(part["items"]):
            key = canon(item["finding_id"])
            if only is None or key in only:
                part["items"][index] = dict(copy.deepcopy(inputs[key]), finding_id=item["finding_id"], carried_forward=True)
    return mutate


def run_carried(follow, previous, also=None, only=None):
    """Run ``follow`` with every finding (or the ones in ``only``) copied from ``previous``'s Section 7, and ``also`` on top."""
    mutate = carried(previous.md, only) if also is None else together(carried(previous.md, only), also)
    res = follow.run(mutate=mutate, baseline_dir=follow.baseline)
    assert res.code in (0, 5), res.describe()
    tp.validate_stage_record(follow.record)
    return follow


# --------------------------------------------------------------------------- fill: the band tables, the header, the order, and the four computed cells

def claim_carried(value=True):
    return every_item(lambda item: item.__setitem__("carried_forward", value))


def test_r34_fill_a_clean_run_counts_no_overwrite(base):
    """The agent wrote a slot token in each computed cell, so nothing was overwritten or flagged. The count is still written, as ``0``: the
    controls renderer always writes ``cell_overwrites`` (ADR-050 D2, ruled at W3), where the scorer's record has none."""
    assert base.record["counts"]["cell_overwrites"] == 0 and "corrected" not in base.record["counts"]
    assert_nothing_counted(base.record)


def test_r34_fill_the_band_tables_the_header_and_the_row_order_are_the_renderers_whatever_the_agent_wrote(stage, renderer, base, tmp_path):
    """D2: the band table that each row sits under, the band headers (empty bands left out), the K8 header row and the row order are
    filled. The agent writes only rows, so this agent puts a wrong band in two cells of every row and hands its items in reverse."""
    def wrong_bands(item):
        cells = row_cells(item["matrix_row"])
        cells[K8_HEADER.index("Inherent Severity")], cells[K8_HEADER.index("Residual Severity")] = "Low", "Critical"
        item["matrix_row"] = join_row(cells)

    project = run_ok(stage, renderer, tmp_path, together(every_item(wrong_bands), lambda part: part["items"].reverse()))
    found = band_tables(project.md)
    assert [band for band, _header, _rows in found] == list(BANDS)
    assert [header for _band, header, _rows in found] == [K8_HEADER] * 4
    for band, _header, rows in found:
        assert [canon(row["Threat ID"]) for row in rows] == [canon(i) for i in RESIDUAL_BANDS[band]], "each row is under its COMPUTED band: %s" % band
        assert {row["Residual Severity"] for row in rows} == {band}
    lines = section(project.md, "## 2. Coverage Matrix").split("\n")
    heads = [number for number, line in enumerate(lines) if line.startswith("| Threat ID ")]
    assert len(heads) == 4 and all(re.fullmatch(r"\|(\s*:?-+:?\s*\|){11}", lines[number + 1]) for number in heads), "a separator row under each header"
    assert overwrites(project.record) == 2 * len(FINDINGS), "the two wrong cells of each row are overwritten and counted"
    assert_same_as_clean(project, base)


OVERWRITES = [  # S-2 is 9.1 (Critical) inherent and 4.6 (Medium) residual
    ("a-wrong-score", "Inherent Score", "1.0"),
    ("a-wrong-band", "Inherent Severity", "Low"),
    ("a-wrong-residual", "Residual Score", "9.9"),
    ("a-wrong-residual-band", "Residual Severity", "Critical"),
    ("the-right-number-written-out", "Inherent Score", "9.1"),
    ("prose-where-a-number-belongs", "Residual Score", "about five"),
    ("an-empty-cell", "Residual Severity", ""),
    ("another-cells-slot", "Inherent Score", "{{score:residual}}"),  # reading: only its own slot token is "the slot token"
    ("a-slot-with-text-around-it", "Residual Score", "{{score:residual}} (est.)"),
]


@pytest.mark.parametrize("name,cell,text", OVERWRITES, ids=[case[0] for case in OVERWRITES])
def test_r34_fill_a_computed_cell_that_holds_anything_but_its_slot_is_overwritten_by_position_and_counted(stage, renderer, base, tmp_path, name, cell, text):
    """D2: the four computed cells are "fill, overwritten by column position. The agent writes slot tokens there; other content is
    overwritten and counted in the stage record". One cell is wrong here, so one overwrite is counted, the row shows the computed values,
    and everything else is as in the clean render, Section 7's persisted row included (it is rebuilt with the tokens, ruled at W3)."""
    project = run_ok(stage, renderer, tmp_path, with_cells(S2_ID, {cell: text}))
    inherent, inherent_band, _factor, residual, residual_band = golden(S2_ID)
    band, row = matrix_rows(project.md)[S2_ID]
    assert [row[column] for column in COMPUTED_CELLS] == [inherent, inherent_band, residual, residual_band] and band == residual_band
    assert overwrites(project.record) == 1, gained_counts(project.record)
    assert_same_as_clean(project, base)
    assert inputs_table(project.md) == inputs_table(base.md)
    assert persisted(project.md)[S2_ID]["matrix_row"] == matrix_row_of(by_id(S2_ID)), "the four computed cells hold their slot tokens in Section 7"


def test_r34_fill_every_computed_cell_of_every_row_is_counted_once_each(stage, renderer, base, tmp_path):
    wrong = every_item(lambda item: item.__setitem__("matrix_row", join_row(
        ["0.0" if name in COMPUTED_CELLS else cell for name, cell in zip(K8_HEADER, row_cells(item["matrix_row"]))])))
    project = run_ok(stage, renderer, tmp_path, wrong)
    assert overwrites(project.record) == 4 * len(FINDINGS) == 44, "every computed cell of every row, once each: %s" % project.record["counts"]
    assert gained_counts(project.record) == {}, "an overwrite raises no flag"
    assert_same_as_clean(project, base)


@pytest.mark.parametrize("text", ["CF", "", "yes", DASH])
def test_r34_cf_is_the_renderers_cell_so_the_agents_text_in_it_is_never_counted(stage, renderer, base, tmp_path, text):
    """W3 ruling (``module-signatures.md``): the renderer fills ``CF`` from the accepted ``carried_forward`` by column position, and never
    counts it as an overwrite. This finding is fresh (``carried_forward`` false), so it shows the dash whatever the agent put there."""
    project = run_ok(stage, renderer, tmp_path, with_cells(S2_ID, {"CF": text}))
    assert matrix_rows(project.md)[S2_ID][1]["CF"] == DASH
    assert overwrites(project.record) == 0, gained_counts(project.record)
    assert_same_as_clean(project, base)
    assert persisted(project.md)[S2_ID]["matrix_row"] == matrix_row_of(by_id(S2_ID)), "Section 7 holds the value that Section 2 shows in CF"


LIST_CAP = 10  # ``sarif_common.PEER_CAP``: a list of finding IDs in a rendered markdown file names at most this many (ADR-050 D2, ruled at W3)


def named_list(spelled_ids):
    """What a rendered markdown file writes for a list of findings (ADR-050 D2, ruled at W3, question 4): the first ``LIST_CAP`` IDs in S-2
    order, as Section 7 of ``threats.md`` spells them and joined by ``, ``, then `` and N more`` with N exact. At ``LIST_CAP`` or fewer there is no tail."""
    ordered = sorted(spelled_ids, key=s2_key)
    return ", ".join(ordered[:LIST_CAP]) + (" and %d more" % (len(ordered) - LIST_CAP) if len(ordered) > LIST_CAP else "")


def assert_recorded(project, finding_ids):
    """D2: a cleared ``carried_forward`` is "cleared with the reason recorded", which the architect ruled at W3 (``module-signatures.md``, the
    controls flag vocabulary): the stage record's warning ``carried-forward-cleared`` and an Input Issue line that names the findings (a list of
    IDs, so at most ``LIST_CAP`` of them and a count of the rest) record it, and it raises no flag. Nothing else is counted for it."""
    warnings = [warning for warning in project.record["warnings"] if warning["code"] == "carried-forward-cleared"]
    assert len(warnings) == 1, project.record["warnings"]
    wanted = named_list([by_id(finding_id)["id"] for finding_id in finding_ids])
    assert any(wanted in line for line in integrity_text(project.md).split("\n")), "an Input Issue line names the cleared findings: " + wanted
    assert not any(flags_of(project.sarif).values()) and gained_counts(project.record) == {}, "a cleared claim raises no flag"


def assert_all_fresh(project, counts=("null",)):
    rows = matrix_rows(project.md)
    assert {row["CF"] for _band, row in rows.values()} == {DASH}, "no claim was accepted, so no row shows CF"
    assert frontmatter_value(project.md, "rescan_scope") == "full" and frontmatter_value(project.md, "carry_forward_count") in counts
    assert {result["properties"]["control-carry-forward"] for result in project.sarif["runs"][0]["results"]} == {False}


def test_r34_cf_a_claim_with_no_baseline_is_cleared_and_recorded(stage, renderer, base, tmp_path):
    """D2: ``carried_forward`` is "accepted only for an UNCHANGED finding with a resolved baseline controls file, otherwise cleared with the
    reason recorded". Here every finding is UNCHANGED and every agent claims it, but the run has no baseline."""
    project = Project(stage, renderer, tmp_path, findings=[dict(item, status="UNCHANGED") for item in FINDINGS])
    res = project.run(mutate=claim_carried())
    assert res.code in (0, 5), res.describe()
    assert_all_fresh(project)
    assert_recorded(project, OPEN_IDS)
    assert {item["carried_forward"] for item in persisted(project.md).values()} == {False}, "cleared is what Section 7 keeps, so the next run copies no claim (reading 6, ruled at W3)"
    assert_same_as_clean(project, base)


def test_r34_cf_a_baseline_with_no_controls_file_clears_every_claim(stage, renderer, base, tmp_path):
    first = run_ok(stage, renderer, tmp_path / "first")
    follow = follow_up(stage, renderer, tmp_path / "second", first, with_baseline=False)
    run_carried(follow, first)
    assert_all_fresh(follow)  # no baseline controls file is no baseline: the template says "null when no baseline"
    assert_recorded(follow, OPEN_IDS)
    assert_same_as_clean(follow, base)


def test_r34_cf_a_baseline_accepts_a_claim_only_for_an_unchanged_finding_that_the_agent_carried(stage, renderer, tmp_path):
    """Four claims, one run: S-2 and T-1 are UNCHANGED and carried (accepted); S-10 is UNCHANGED but its agent scanned it afresh (no claim);
    D-2 is UPDATED and AG-1 is NEW, and their agents claim anyway (cleared). ``carry_forward_count`` counts exactly the ``CF`` cells."""
    first = run_ok(stage, renderer, tmp_path / "first")
    statuses = {canon(item["id"]): "NEW" for item in FINDINGS}
    statuses.update({"S-2": "UNCHANGED", "T-1": "UNCHANGED", "S-10": "UNCHANGED", "D-2": "UPDATED"})
    follow = follow_up(stage, renderer, tmp_path / "second", first, statuses=statuses)
    run_carried(follow, first, only={"S-2", "T-1", "D-2", "AG-1"})
    shown = {finding_id: row["CF"] for finding_id, (_band, row) in matrix_rows(follow.md).items()}
    assert {finding_id for finding_id, cell in shown.items() if cell == "CF"} == {"S-2", "T-1"}
    assert {cell for finding_id, cell in shown.items() if finding_id not in ("S-2", "T-1")} == {DASH}
    assert frontmatter_value(follow.md, "rescan_scope") == "incremental" and frontmatter_value(follow.md, "carry_forward_count") == "2"
    flagged = {finding_id for finding_id, result in results_by_id(follow.sarif).items() if result["properties"]["control-carry-forward"] is True}
    assert flagged == {"S-2", "T-1"}
    assert_recorded(follow, ["D-2", "AG-1"])
    kept = persisted(follow.md)
    assert {finding_id: kept[finding_id]["carried_forward"] for finding_id in ("S-2", "T-1", "S-10", "D-2", "AG-1")} == {
        "S-2": True, "T-1": True, "S-10": False, "D-2": False, "AG-1": False}, "Section 7 keeps the accepted value"


# A claim needs a result to carry (ADR-050 D2, ruled at W4): the renderer accepts ``carried_forward`` only for an UNCHANGED finding whose result the
# resolved baseline controls file holds. A 1.1 file holds a result in Section 7's Assessment Inputs, which is what the planner hands the agent to copy
# (AR-T3), and a rendered Section 2 row doesn't count there (RR1). A 1.0 file persists nothing, so it holds a result as a Section 2 row.

def claims(*finding_ids):
    """The agent sets ``carried_forward`` on the items of ``finding_ids`` and changes nothing else in them."""
    return together(*[edit_item(finding_id, lambda item: item.__setitem__("carried_forward", True)) for finding_id in finding_ids])


def without_rows(md, body, finding_id):
    """``md`` with the table rows of ``finding_id`` taken out of ``body``, a section or subsection of it. A seed that finds no row fails the test."""
    kept = "\n".join(line for line in body.split("\n") if not line.startswith("| %s |" % finding_id))
    assert kept != body and md.count(body) == 1, "the seeded edit changed nothing"
    return md.replace(body, kept)


def as_a_1_0_file(md, missing=()):
    """``md`` as a 1.0 controls file holds it: schema 1.0 and no Section 7 table to persist from (so the planner hands over no result), with no
    Section 2 row for each finding of ``missing``."""
    text = drop_table(md.replace('schema_version: "1.1"', 'schema_version: "1.0"', 1), "### Assessment Inputs")
    for finding_id in missing:
        text = without_rows(text, section(text, "## 2. Coverage Matrix"), finding_id)
    assert tachi_parsers.parse_frontmatter(text)["schema_version"] == "1.0" and persisted(text) == {}, "the seeded file reads as a 1.0 file"
    return text


def assert_s2_carried_and_t1_cleared(follow):
    """S-2 and T-1 are UNCHANGED and both claim, and the baseline holds a result for S-2 only. S-2 shows ``CF`` and is counted, and T-1's claim is
    cleared with the reason recorded (the stage record's warning and one Input Issue line, no flag), so T-1 shows the dash and counts as scanned."""
    shown = {finding_id: row["CF"] for finding_id, (_band, row) in matrix_rows(follow.md).items()}
    assert {finding_id for finding_id, cell in shown.items() if cell == "CF"} == {"S-2"} and shown["T-1"] == DASH
    assert frontmatter_value(follow.md, "carry_forward_count") == "1" and frontmatter_value(follow.md, "rescan_scope") == "incremental"
    flagged = {finding_id for finding_id, result in results_by_id(follow.sarif).items() if result["properties"]["control-carry-forward"] is True}
    assert flagged == {"S-2"}
    assert_recorded(follow, ["T-1"])
    assert [warning["detail"] for warning in follow.record["warnings"] if warning["code"] == "carried-forward-cleared"] == [
        "the control analyzer set carried_forward on 1 findings that can't be carried (the baseline %s holds no result for it), such as T-1" % MD]
    assert "- " + tp.escape_prose("1 findings had carried_forward cleared (carried_forward is accepted only for an UNCHANGED finding whose result the "
                                  "resolved baseline %s holds), so they count as scanned: T-1" % MD) in integrity_text(follow.md).split("\n")
    kept = persisted(follow.md)
    assert (kept["S-2"]["carried_forward"], kept["T-1"]["carried_forward"]) == (True, False), "Section 7 keeps the accepted value"


def test_r34_cf_a_1_1_baseline_that_persists_no_result_for_a_finding_clears_its_claim_though_its_section_2_row_is_there(stage, renderer, tmp_path):
    """D2, ruled at W4: in a 1.1 file the result is the one Section 7 persists, and T-1's Section 2 row is no result, because its text is rendered and the
    agent never copies from it. The planner hands S-2's result over and hands T-1 none, so S-2 copies its own and is carried, and T-1's claim, made with
    its own values, is cleared. Before the ruling the renderer accepted it, and showed ``CF`` for a result that came from no baseline."""
    first = run_ok(stage, renderer, tmp_path / "first")
    (first.out / MD).write_text(without_rows(first.md, subsection_of(first.md, "## 7. Analysis Integrity", "### Assessment Inputs"), "T-1"), encoding="utf-8")
    assert "T-1" in matrix_rows(first.md) and "T-1" not in persisted(first.md) and "S-2" in persisted(first.md), "T-1 is in Section 2 and not in Section 7"
    follow = follow_up(stage, renderer, tmp_path / "second", first, statuses={"S-2": "UNCHANGED", "T-1": "UNCHANGED"}, default="NEW")
    run_carried(follow, first, also=claims("T-1"), only={"S-2"})
    assert_s2_carried_and_t1_cleared(follow)


def test_r34_cf_a_1_0_baseline_with_no_section_2_row_for_a_finding_clears_its_claim(stage, renderer, tmp_path):
    """D2, ruled at W4: a 1.0 file has no persisted results, so the agent copies from the file itself, and the file holds a finding as its Section 2 row
    under a band heading. Run 1's file is rewritten as a 1.0 file would be, without T-1's row. S-2 and T-1 are UNCHANGED and both claim: S-2's row is
    there and is carried, T-1's is not and is cleared. Before the ruling the renderer accepted both."""
    first = run_ok(stage, renderer, tmp_path / "first")
    (first.out / MD).write_text(as_a_1_0_file(first.md, missing=("T-1",)), encoding="utf-8")
    assert sorted(matrix_rows(first.md)) == sorted(canon(item["id"]) for item in FINDINGS if canon(item["id"]) != "T-1"), "T-1 has no Section 2 row"
    follow = follow_up(stage, renderer, tmp_path / "second", first, statuses={"S-2": "UNCHANGED", "T-1": "UNCHANGED"}, default="NEW")
    run_carried(follow, first, also=claims("S-2", "T-1"), only=())
    assert_s2_carried_and_t1_cleared(follow)


def test_r34_cf_a_1_0_baseline_with_a_section_2_row_for_every_finding_accepts_every_unchanged_claim(stage, renderer, tmp_path):
    """The upgrade path: every controls file written before schema 1.1 is a 1.0 file, which persists nothing and holds each finding as its Section 2 row.
    Every finding is UNCHANGED and every agent claims it, so every claim is accepted and nothing is cleared, as before the ruling."""
    first = run_ok(stage, renderer, tmp_path / "first")
    (first.out / MD).write_text(as_a_1_0_file(first.md), encoding="utf-8")
    follow = follow_up(stage, renderer, tmp_path / "second", first)
    run_carried(follow, first, also=claim_carried(), only=())
    assert follow.record["warnings"] == []
    assert_carried_from(follow, first)


# --------------------------------------------------------------------------- carry: AR-T3, AR-T4, carry_forward_count and byte identity

def two_runs(stage_module, renderer_module, root, first_mutate=None):
    """A first run (the agent's part edited by ``first_mutate``) and a second in which every finding is UNCHANGED and carried: the agent
    copies the first run's persisted inputs, the way the planner hands them over (AR-T3)."""
    first = run_ok(stage_module, renderer_module, Path(root) / "first", first_mutate)
    follow = run_carried(follow_up(stage_module, renderer_module, Path(root) / "second", first), first)
    return first, follow


def assert_carried_from(follow, first):
    """Every finding of ``follow`` is carried from ``first``: each row shows ``CF``, and ``carry_forward_count`` is the number of ``CF``
    cells and of results that say so (R-20: "the carried-forward marker that ``carry_forward_count`` counts"). A carried row is copied,
    read and checked with no overwrite and no flag, and its narrative takes no fallback. Everything else is what ``first`` wrote."""
    rows = matrix_rows(follow.md)
    shown = [finding_id for finding_id, (_band, row) in rows.items() if row["CF"] == "CF"]
    marked = [finding_id for finding_id, result in results_by_id(follow.sarif).items() if result["properties"]["control-carry-forward"] is True]
    assert sorted(shown) == sorted(rows) and len(rows) == len(FINDINGS)
    assert len(shown) == len(marked) == int(frontmatter_value(follow.md, "carry_forward_count"))
    assert frontmatter_value(follow.md, "rescan_scope") == "incremental"
    assert_nothing_counted(follow.record)  # a carried row is copied, read and checked with no overwrite and no flag (AR-T3): cell_overwrites is 0
    assert (follow.record["counts"].get("narrative_fallbacks", 0), follow.record["counts"].get("truncations", 0)) == (0, 0), "AR-T4"
    assert_same_as_clean(follow, first, carried_differs=True)


def test_r34_carry_run_1s_numbers_are_counted_on_run_1_and_the_carried_run_2_counts_none(stage, renderer, base, tmp_path):
    """The architect's first case (W3): run 1's agent wrote numbers in the computed cells. They are counted on run 1, and Section 7
    persists the row with the slot tokens, so the carried run 2 copies a row that needs no overwrite."""
    first, follow = two_runs(stage, renderer, tmp_path, together(*[the_agent_wrote_the_numbers(item["id"]) for item in FINDINGS]))
    assert overwrites(first.record) == 4 * len(FINDINGS) == 44, first.record["counts"]
    assert overwrites(follow.record) == 0, "the carried run 2 counts none (written, as 0): its rows were persisted with the slot tokens"
    assert_same_as_clean(first, base)
    assert all(persisted(first.md)[canon(item["id"])]["matrix_row"] == matrix_row_of(item) for item in FINDINGS), "Section 7 holds the tokens, not the numbers"
    assert_carried_from(follow, first)


def test_r34_carry_a_fresh_row_is_shown_as_carried_on_run_2_with_no_overwrite_and_no_fallback(stage, renderer, base, tmp_path):
    """The architect's second case (W3): fresh on run 1, with ``CF`` shown as the dash, then carried on run 2. The copied row still has the dash,
    ``CF`` is shown, and nothing is overwritten, because ``CF`` is the renderer's cell. Section 7 then holds the value that Section 2 shows."""
    first, follow = two_runs(stage, renderer, tmp_path)
    assert_all_fresh(first)
    assert_same_as_clean(first, base)
    assert_carried_from(follow, first)
    inputs = persisted(follow.md)
    for item in FINDINGS:
        cells = row_cells(matrix_row_of(item))
        cells[K8_HEADER.index("CF")] = "CF"
        assert inputs[canon(item["id"])]["matrix_row"] == join_row(cells), "Section 7 persists CF as Section 2 shows it: %s" % item["id"]
        assert inputs[canon(item["id"])]["carried_forward"] is True
    assert not [sentence for sentence in tp.FALLBACK_SENTENCES.values() if sentence in follow.md], "AR-T4: no fixed fallback sentence anywhere"


def test_r34_carry_the_carried_row_and_narrative_are_filled_again_from_this_runs_values(stage, renderer, tmp_path):
    """AR-T3 and AR-T4: Section 7 persists the row and the narrative with their slots, so a carried finding shows this run's numbers, not the
    baseline's. T-1 (a found finding with an effectiveness assessment) is 7.3 in run 1 and 6.0 in run 2: its residual is 3.0 and Low, and its
    narrative says so, with no fallback."""
    first = run_ok(stage, renderer, Path(tmp_path) / "first")
    follow = follow_up(stage, renderer, Path(tmp_path) / "second", first)
    moved = [dict(item, inherent="6.0") if item["id"] == "T-1" else item for item in follow.findings]
    follow.risk_scores.write_text(make_risk_scores_md(moved, follow.resolved), encoding="utf-8")
    run_carried(follow, first)
    band, row = matrix_rows(follow.md)["T-1"]
    assert (band, row["CF"], [row[column] for column in COMPUTED_CELLS]) == ("Low", "CF", ["6.0", "Medium", "3.0", "Low"])
    assert_nothing_counted(follow.record)
    assert follow.record["counts"].get("narrative_fallbacks", 0) == 0
    values = {("score", "inherent"): "6.0", ("score", "residual"): "3.0", ("band", "inherent"): "Medium", ("band", "residual"): "Low",
              ("count", "evidence"): "1", ("pct", "reduction"): str(ts.reduction_percentage(Decimal("6.0"), Decimal("3.0"))), ("name", "component"): "auth-broker"}
    block = next(body for cat, heading, body in control_blocks(follow.md) if "`src/validate/schema.py:17`" in body and slug(cat) == "input-validation")
    _header, rows = table_of(block, "Dimension")
    shown = {row[0]: row[2] for row in rows}
    for dimension, cell in ASSESSMENT.items():
        assert shown[dimension.capitalize()] == decode(tp.resolve_narrative(cell["rationale"], STAGE, lambda kind, argument: values.get((kind, argument)), sink="cell")), dimension
    assert "{{" not in block and "7.3" not in block and "3.7" not in block, "the baseline's numbers are nowhere in the carried prose"
    assert persisted(follow.md)["T-1"]["evidence"][0]["assessment"]["configuration"]["rationale"] == ASSESSMENT["configuration"]["rationale"], "and Section 7 still holds the slots"


ENTITY_SUMMARY = "Escapes &lt; and splits on | before parsing."
ENTITY_SNIPPET = "fields = line.split('|')  # &lt; stays text"
ENTITY_WHAT = "Split on the pipe | and keep &lt; as text."
ENTITY_RATIONALE = "Rejects &lt; and | in the names of {{name:component}}."
ENTITY_THREAT = "Shared tokens let callers pass &lt;b&gt; as text."


def with_entities(findings):
    """Copies of ``findings`` in which three results hold text that a renderer must escape exactly once, however many runs carry it: a literal
    ``&lt;`` (four characters of text, not a less-than sign) and a ``|``, in an evidence summary and snippet, a narrative rationale and a body."""
    out = copy.deepcopy(findings)
    for item in out:
        if item["id"] in ("T-1", "AGP-01"):
            entry = item["evidence"][0]
            entry["summary"], entry["snippet"] = ENTITY_SUMMARY, ENTITY_SNIPPET
        if item["id"] == "T-1":
            item["evidence"][0]["assessment"]["coverage"]["rationale"] = ENTITY_RATIONALE
        if item["id"] in ("AGP-01", "E-3"):
            item["rec"]["what"] = ENTITY_WHAT
    return out


def without_stamp(text):
    """A markdown file without its last line, the provenance stamp, whose digest names the run's own parts."""
    return text.rstrip("\n").rsplit("\n", 1)[0]


def test_r34_carry_an_unchanged_result_with_entities_and_pipes_is_byte_identical_on_every_carried_run(stage, renderer, tmp_path):
    """An UNCHANGED result whose evidence holds ``&lt;`` and ``|`` is escaped once per render and never compounds (ADR-050 D2, RR1): the
    carried runs 2 and 3 write the same bytes (bar the stamp, which names each run's own parts), and run 1's escape is still one level deep."""
    first = run_ok(stage, renderer, Path(tmp_path) / "r1", with_cells("S-2", {"Threat": ENTITY_THREAT}), findings=with_entities(FINDINGS))
    second = run_carried(follow_up(stage, renderer, Path(tmp_path) / "r2", first), first)
    third = run_carried(follow_up(stage, renderer, Path(tmp_path) / "r3", second), second)
    for run in (first, second, third):
        assert "&amp;lt;" in run.md and "&amp;amp;" not in run.md and "&#124;" in run.md, "escaped once, on every run"
        results = results_by_id(run.sarif)
        assert results["AGP-01"]["properties"]["control-evidence"][0]["snippet"] == ENTITY_SNIPPET, "SARIF strings are json.dumps only: raw text"
        assert results["AGP-01"]["properties"]["recommendation"] == results["E-3"]["properties"]["recommendation"] == ENTITY_WHAT, "the section 4 round trip"
        assert read_findings(run.md)[canon("AGP-01")]["recommendation"] == ENTITY_WHAT
        assert matrix_rows(run.md)["S-2"][1]["Threat"] == ENTITY_THREAT
    assert_carried_from(second, first)
    assert_carried_from(third, second)
    assert without_stamp(second.md) == without_stamp(third.md), "carried twice: byte-identical"

    def sarif_of(run):
        doc = copy.deepcopy(run.sarif)
        doc["runs"][0]["properties"]["tachi_provenance"]["input_digest"] = None
        return doc

    assert sarif_of(second) == sarif_of(third)
    assert persisted(second.md) == persisted(third.md)
    for key, item in persisted(first.md).items():
        cells = row_cells(item["matrix_row"])
        cells[K8_HEADER.index("CF")] = "CF"
        assert persisted(second.md)[key] == dict(item, carried_forward=True, matrix_row=join_row(cells)), "Section 7 differs only in what carrying changes: %s" % key


# --------------------------------------------------------------------------- reject: the Threat ID, the 11 cells and Section 4's body

def assert_rejected(project, mutate):
    """D2: "a mismatch rejects the item (D3), and its batch is re-dispatched". D3 step 9 says that structure rejects the part, and only
    ``reconcile`` re-dispatches a batch, from what ``tachi_parts.read_part`` says: FX0c built the row and body checks there, which closes
    reading 7. So ``reconcile`` finds the part ``invalid`` and the batch is pending again (exit 3, attempt 2). A good second part then
    renders what a clean run renders, nothing of the rejected row survives, and the record shows the one retry. A first, clean render
    gives the bytes that the second attempt is held to. (The renderer reads every part through ``read_part`` again: Section 18.)"""
    assert project.run().code == 0
    clean = project.outputs()
    project.plan()
    project.write_parts(mutate=mutate)
    first = project.reconcile()
    assert first.code == 3, "the part is rejected at ``read_part``, so its batch is pending again: %s" % first.describe()
    pending = [batch["batch_id"] for wave in json.loads(first.out)["waves"] for batch in wave]
    assert pending == ["B001"], first.describe()
    retry = project.batch_input("B001")
    assert retry["attempt"] == 2 and retry["part_path"].endswith("B001.a2.json"), "the same batch, a second attempt"
    project.write_parts(only={"B001"})
    assert project.reconcile().code == 0
    res = project.render()
    assert res.code == 0, res.describe()
    assert project.outputs() == clean, "the second attempt renders what a clean run renders"
    assert project.record["overflow_events"] == [{"batch_id": "B001", "attempt": 1, "kind": "invalid"}]
    assert project.record["batches"] == {"planned": 1, "dispatched": 2, "done": 1, "retried": 1, "split": 0, "exhausted": 0}


def a_row(change):
    """An agent whose row for the finding is ``change(its own cells)``, a list of cells or the row's text."""
    def edit(item):
        made = change(row_cells(item["matrix_row"]))
        item["matrix_row"] = made if isinstance(made, str) else join_row(made)
    return edit


BAD_ROWS = [
    ("the-id-of-another-finding", "S-2", lambda cells: ["T-1"] + cells[1:]),
    ("an-id-outside-the-allow-list", "S-2", lambda cells: ["X-99"] + cells[1:]),
    ("a-lowercase-id", "S-2", lambda cells: ["s-2"] + cells[1:]),
    ("an-empty-id", "S-2", lambda cells: [""] + cells[1:]),
    ("ten-cells", "S-2", lambda cells: cells[:8] + cells[9:]),
    ("twelve-cells-from-a-pipe-in-the-threat", "S-2", lambda cells: cells[:4] + ["Tokens | shared"] + cells[5:]),
    ("one-cell", "S-2", lambda cells: cells[:1]),
    ("an-empty-row", "S-2", lambda cells: ""),
]


@pytest.mark.parametrize("name,finding_id,change", BAD_ROWS, ids=[case[0] for case in BAD_ROWS])
def test_r34_reject_a_wrong_threat_id_or_a_cell_count_other_than_11_rejects_the_item(project, name, finding_id, change):
    assert_rejected(project, edit_item(finding_id, a_row(change)))


@pytest.mark.parametrize("finding_id,spelled", [("AGP-01", "AGP-1"), ("S-2", "S-02")])
def test_r34_reject_an_id_that_canonicalizes_to_the_findings_is_accepted_and_spelled_as_section_7_spells_it(stage, renderer, base, tmp_path, finding_id, spelled):
    """The row's Threat ID "must pass the allow-list and canonicalize to the item's ``finding_id``". These do, so the item stands. Section 2
    and Section 4 are one file that the shipped reader joins by string, so both spell the ID as ``threats.md``'s Section 7 does (reading 5)."""
    project = run_ok(stage, renderer, tmp_path, with_cells(finding_id, {"Threat ID": spelled}))
    assert_same_as_clean(project, base)
    rendered = project.md.split("## 7. Analysis Integrity")[0]
    assert not re.search(r"(?<![A-Za-z0-9-])%s(?![A-Za-z0-9-])" % re.escape(spelled), rendered), "the agent's spelling is in no rendered section"
    assert_nothing_counted(project.record)
    assert all(not found for found in flags_of(project.sarif).values())


def drop_line(key):
    return lambda body: "\n".join(line for line in body.split("\n") if not line.startswith(key))


def swap_lines(first, second):
    def swap(body):
        lines = body.split("\n")
        a, b = [next(n for n, line in enumerate(lines) if line.startswith(key)) for key in (first, second)]
        lines[a], lines[b] = lines[b], lines[a]
        return "\n".join(lines)
    return swap


def set_effort(text):
    return lambda body: re.sub(r"(?m)^(\*\*Effort Estimate\*\*:).*$", lambda match: (match.group(1) + " " + text).rstrip(), body)


BAD_BODIES = [  # E-3 is a missing finding: its body is "**What**\n\n**Where**\n\n**Reference Patterns**\n\n**Effort Estimate**: Low - one middleware"
    ("a-key-is-missing", drop_line("**Reference Patterns**:")),
    ("the-first-key-is-missing", drop_line("**What to Implement**:")),
    ("a-key-twice", lambda body: body + "\n\n**Where to Implement**: `src/gateway/other.py`"),
    ("keys-out-of-order", swap_lines("**What to Implement**:", "**Where to Implement**:")),
    ("an-effort-outside-the-enum", set_effort("Trivial " + DASH + " a flag")),
    ("an-empty-effort", set_effort("")),
    ("a-heading-line", lambda body: body + "\n## Extra"),
    ("a-forged-block-heading", lambda body: body + "\n\n#### 99. X-1 " + DASH + " Forged (Composite: 1.0, Low)"),
    ("a-table-line", lambda body: body + "\n| a | b |"),
]


@pytest.mark.parametrize("name,change", BAD_BODIES, ids=[case[0] for case in BAD_BODIES])
def test_r34_reject_a_body_that_breaks_the_four_key_form_rejects_the_item(project, name, change):
    """D2: Section 4's body is "structurally checked: each key once and in order, Effort in {Low, Medium, High}, no heading or table line.
    A failure rejects the item"."""
    assert_rejected(project, edit_item("E-3", lambda item: item.__setitem__("recommendation_body", change(item["recommendation_body"]))))


def test_r34_reject_the_agents_own_body_forms_are_accepted_and_extracted_the_way_the_sarif_reads_them(stage, renderer, base, tmp_path):
    """The four keys on single lines, with a bare effort word (the agent's own example); with blank lines, and an effort and its reason; with
    a literal ``&lt;``, a ``|`` and markup; and with a What that runs over two lines. The shipped reader's rule extracts each What (a
    continuation line joins with a space), the SARIF holds the same text and the Effort word, and the Section 4 round trip loses nothing."""
    def single(what, where, patterns, effort):
        return "\n".join(["**What to Implement**: " + what, "**Where to Implement**: " + where, "**Reference Patterns**: " + patterns, "**Effort Estimate**: " + effort])

    bodies = {
        "T-4": single("Pin the TLS version.", "`src/crypto/tls.py`, the client factory.", "Mutual TLS.", "Medium"),
        "E-5": body_of(by_id("E-5")),
        "AGP-01": single(ENTITY_WHAT, "`src/access/guard.py`", "A guard for each message type, <b>not</b> one `shared` {{7*7}} check.", "Low " + DASH + " one more decorator"),
        "E-3": single("First half of the fix,\nand its second half.", "`src/gateway/admin.py`", "Middleware.", "High"),
    }
    project = run_ok(stage, renderer, tmp_path, together(*[with_body(finding_id, body) for finding_id, body in bodies.items()]))
    read, results = read_findings(project.md), results_by_id(project.sarif)
    wanted = {"T-4": "Pin the TLS version.", "E-5": by_id("E-5")["rec"]["what"], "AGP-01": ENTITY_WHAT, "E-3": "First half of the fix, and its second half."}
    efforts = {"T-4": "Medium", "E-5": "High", "AGP-01": "Low", "E-3": "High"}
    for finding_id, what in wanted.items():
        assert read[canon(finding_id)]["recommendation"] == what == results[finding_id]["properties"]["recommendation"], finding_id
        assert results[finding_id]["properties"]["effort-estimate"] == efforts[finding_id], finding_id
    block = recommendation_blocks(project.md)[canon("AGP-01")]
    assert "<b>" not in project.md and "{{7*7}}" not in project.md and "&lt;b&gt;not&lt;/b&gt;" in block and "&amp;lt;" in block
    assert_nothing_counted(project.record)


# --------------------------------------------------------------------------- flag: Control Status, Control Category, Component and MAESTRO Layer

MISMATCHES = [  # (name, finding, cell, the agent's text)
    ("a-found-status-for-a-partial-finding", "AGP-01", "Control Status", "Control Found"),
    ("a-missing-status-for-a-found-finding", S2_ID, "Control Status", "No Control Found"),
    ("another-category", "T-1", "Control Category", "Encryption"),
    ("a-word-that-is-no-category", "S-10", "Control Category", "Biometrics"),
    ("another-component", "T-4", "Component", "edge-gateway"),
    ("another-layer-code", "LLM-4", "MAESTRO Layer", "L5 " + DASH + " Evaluation and Observability"),
    ("unclassified-for-a-classified-layer", "AG-1", "MAESTRO Layer", "Unclassified"),
    ("an-empty-component", "T-4", "Component", ""),
    ("a-layer-name-with-no-code", "LLM-4", "MAESTRO Layer", "Agent Framework"),  # no code, so it is compared as written (module-signatures.md)
    ("a-category-with-markup", "S-10", "Control Category", "Biometrics <b>x</b> & `y` {{7*7}}"),  # shown as the agent wrote it, but escaped
]


@pytest.mark.parametrize("name,finding_id,cell,text", MISMATCHES, ids=[case[0] for case in MISMATCHES])
def test_r34_flag_a_cell_that_disagrees_with_the_structured_value_is_flagged_and_every_file_follows_the_structure(stage, renderer, base, tmp_path, name, finding_id, cell, text):
    """D2 and the W3 rulings (``module-signatures.md``): Control Status (through ``classify_control_status``), Control Category, Component and
    MAESTRO Layer are "check against the structured judgment or input". A mismatch is flagged once with the cell's closed string (``FLAG_OF``),
    counted under ``counts.input``, and named in Section 1's warnings and Section 7. It never rejects the item. Section 2 shows the agent's cell
    as written, escaped; the SARIF, every total, Sections 3 to 6 and every other cell are the structured value's, as in the clean run."""
    project = run_ok(stage, renderer, tmp_path, with_cells(finding_id, {cell: text}))
    flags = flags_of(project.sarif)
    assert flags[finding_id] == [FLAG_OF[cell]], "exactly one flag, and it is the cell's own string: %r" % (flags[finding_id],)
    assert [other for other, found in flags.items() if found and other != finding_id] == [], "no other finding is flagged"
    assert project.record["counts"]["input"] == 1 and project.record["counts"].get("cell_overwrites", 0) == 0, "the flag is counted under input, and no cell was overwritten"
    assert any(re.search(id_pattern(finding_id), line) for line in warning_lines(project.md)), "Section 1's warnings name the finding"
    kind, field, cause = FLAG_OF[cell].split(":")
    assert any(re.search(id_pattern(finding_id), line) and kind in line and field in line and cause in line
               for line in integrity_text(project.md).split("\n")), "Section 7 lists the flag with its finding"
    assert matrix_rows(project.md)[canon(finding_id)][1][cell] == text, "Section 2 shows the agent's cell as written"
    assert tp.escape_cell(text) in raw_row(project.md, "## 2. Coverage Matrix", by_id(finding_id)["id"]), "and escaped"
    assert_same_as_clean(project, base, open_cells={canon(finding_id): (cell,)})
    cells = row_cells(matrix_row_of(by_id(finding_id)))
    cells[K8_HEADER.index(cell)] = text
    assert persisted(project.md)[canon(finding_id)]["matrix_row"] == join_row(cells), "Section 7 keeps every cell but the computed ones as the part wrote it"


AGREEMENTS = [  # a spelling that classifies, or names, the same value is not a mismatch
    ("a-short-status", "AGP-01", "Control Status", "Partial"),
    ("the-word-missing", "E-3", "Control Status", "Missing"),
    ("a-lowercase-found", S2_ID, "Control Status", "found"),
    ("the-category-slug", "T-1", "Control Category", "input-validation"),
    ("a-layer-name-with-the-same-code", "LLM-4", "MAESTRO Layer", "L3 " + DASH + " Agent Frameworks"),  # the input says "Agent Framework"
    ("a-layer-code-alone", "LLM-4", "MAESTRO Layer", "L3"),
    ("a-longer-status-that-classifies-the-same", "AGP-01", "Control Status", "Partially covered"),
]


@pytest.mark.parametrize("name,finding_id,cell,text", AGREEMENTS, ids=[case[0] for case in AGREEMENTS])
def test_r34_flag_a_spelling_that_means_the_same_value_is_not_a_mismatch(stage, renderer, base, tmp_path, name, finding_id, cell, text):
    """The status is compared through ``classify_control_status``, the category by its name or its slug, and the layer by its code (``L1`` to
    ``L7``), so the "Agent Framework" and "Agent Frameworks" variants of the shipped files agree (``module-signatures.md``)."""
    if cell == "Control Status":
        assert tachi_parsers.classify_control_status(text)[0] == STATUS_CLASS[by_id(finding_id)["control"]], "the premise: the classifier reads it as the finding's class"
    project = run_ok(stage, renderer, tmp_path, with_cells(finding_id, {cell: text}))
    assert all(not found for found in flags_of(project.sarif).values())
    assert_nothing_counted(project.record)
    assert not [line for line in warning_lines(project.md) if re.search(id_pattern(finding_id), line)]
    assert_same_as_clean(project, base, open_cells={canon(finding_id): (cell,)})


@pytest.mark.parametrize("agent,flagged", [("Unclassified", False), ("L7 " + DASH + " Agent Ecosystem", True)])
def test_r34_flag_unclassified_matches_only_itself(stage, renderer, tmp_path, agent, flagged):
    """``Unclassified`` is the layer of a component that ``threats.md`` leaves without one, and it "matches only itself": the agent's
    ``Unclassified`` agrees with it, and any classified layer is a mismatch."""
    project = Project(stage, renderer, tmp_path)
    project.threats.write_text(project.threats.read_text(encoding="utf-8").replace("L7 " + DASH + " Agent Ecosystem", "Unclassified"), encoding="utf-8")
    res = project.run(mutate=with_cells("E-5", {"MAESTRO Layer": agent}))
    assert res.code in (0, 5), res.describe()
    assert results_by_id(project.sarif)["E-5"]["properties"]["maestro-layer"] == "Unclassified", "the SARIF follows the input"
    assert row_check_flags(flags_of(project.sarif)["E-5"]) == ([FLAG_OF["MAESTRO Layer"]] if flagged else [])


def test_r34_flag_section_2_threat_is_model_text_shown_escaped_and_never_checked_or_filled(stage, renderer, base, tmp_path):
    """D2: "§2 Threat | model text (NFR-10 only)". It may differ from the reference set's text, it is never flagged, a slot token in it is never
    filled (``part-files.md``), and the SARIF message keeps the reference set's full text."""
    text = "Tokens <i>can</i> be shared & `reused` {{7*7}} and {{count:evidence}} here."
    project = run_ok(stage, renderer, tmp_path, with_cells(S2_ID, {"Threat": text}))
    assert matrix_rows(project.md)[S2_ID][1]["Threat"] == text
    rendered = project.md.split("## 7. Analysis Integrity")[0]
    assert "<i>" not in rendered and "{{7*7}}" not in rendered and "{{count:evidence}}" not in rendered, "escaped, and the slot token is not filled"
    assert text in persisted(project.md)[S2_ID]["matrix_row"], "Section 7 keeps the agent's cell as written"
    assert all(not found for found in flags_of(project.sarif).values())
    assert_nothing_counted(project.record)
    assert_same_as_clean(project, base, open_cells={S2_ID: ("Threat",)})


def test_r34_the_row_is_read_with_or_without_outer_pipes_and_persisted_in_the_canonical_form(stage, renderer, base, tmp_path):
    """``module-signatures.md``: the renderer "reads a row with or without the outer pipes", and Section 7 persists "the row in this form,
    rebuilt from its 11 cells". These rows have no outer pipes, tight pipes, and spaces and a tab around the line. None needs an overwrite."""
    rows = {S2_ID: lambda cells: " | ".join(cells), "T-1": lambda cells: "|" + "|".join(cells) + "|", "S-10": lambda cells: "  \t" + join_row(cells) + " \t "}
    project = run_ok(stage, renderer, tmp_path, together(*[edit_item(finding_id, a_row(change)) for finding_id, change in rows.items()]))
    assert_nothing_counted(project.record)
    assert all(not found for found in flags_of(project.sarif).values())
    assert_same_as_clean(project, base)
    assert all(persisted(project.md)[canon(item["id"])]["matrix_row"] == matrix_row_of(item) for item in FINDINGS)


# --------------------------------------------------------------------------- Section 4: the group, order, number, heading and Current Status

def test_r34_section_4_the_group_order_number_heading_and_status_are_the_renderers(base):
    """D2: "The §4 group each block sits under (band of inherent), block order (inherent descending, then S-2), number, heading
    ``#### n. ID — Component (Composite: x, Band)``, ``**Current Status**:`` line: fill". The numbers run on through the groups (reading 4)."""
    groups = [(heading, body) for heading, body in split_headings(section_text(base.md, "## 4. Recommendations"), "### ") if heading.endswith(" Risk Gaps")]
    assert [heading for heading, _body in groups] == ["### Critical / High Risk Gaps", "### Medium Risk Gaps", "### Low Risk Gaps"]
    number, seen = 0, []
    for heading, body in groups:
        for block_heading, block in split_headings(heading + "\n" + body, "#### "):
            number += 1
            match = re.fullmatch(r"#### (\d+)\. (\S+) %s (.+) \(Composite: (\d+\.\d), (Critical|High|Medium|Low)\)" % DASH, block_heading)
            assert match, block_heading
            finding_id = match.group(2)
            item = by_id(finding_id)
            inherent, inherent_band = golden(finding_id)[:2]
            assert (int(match.group(1)), match.group(3), match.group(4), match.group(5)) == (number, item["component"], inherent, inherent_band), block_heading
            assert finding_id == item["id"], "the ID as Section 7 spells it"
            assert GROUP_OF[inherent_band] == heading, "%s is %s, so it sits under %s" % (finding_id, inherent_band, GROUP_OF[inherent_band])
            lines = [line for line in block.split("\n") if line.strip()]
            assert lines[0] == "**Current Status**: " + STATUS_CELL[item["control"]], "the status that the structured judgment gives"
            seen.append(finding_id)
    assert seen == RECOMMENDED, "inherent descending, then S-2's order"


def test_r34_section_4_each_body_line_is_written_as_the_agent_wrote_it_under_the_renderers_status_line(base):
    blocks = recommendation_blocks(base.md)
    for finding_id in RECOMMENDED:
        for line in (line for line in body_of(by_id(finding_id)).split("\n") if line.strip()):
            assert tp.escape_prose(line) in blocks[canon(finding_id)].split("\n"), "%s: %s" % (finding_id, line)


# =============================================================================
# 16. What T035's goldens left out (the gaps that lane R2's proposed cases found, reviewed and adapted by T056)
# =============================================================================
#
# D8's SARIF fallback, the baseline, forbidden characters in the inputs, the evidence file, a repeated ID, an unreadable threat model,
# the extremes (every finding found, none found), the shift table's cap, the failure path, and the SARIF's ``message`` and rules as the
# 1.1 template shows them. They reach branches of the renderer that the goldens above don't (ADR-050 D16's 80% gate), and each asserts
# what a contract rules. Where one names a form that no contract fixes (a warning code, say), it says ``reading:``.

ODD_LAYER = "L9 odd layer"  # a layer with no code in L1 to L7, so it is compared as written (module-signatures.md)


def layers_unclassified(item):
    cells = row_cells(item["matrix_row"])
    cells[K8_HEADER.index("MAESTRO Layer")] = "Unclassified"
    item["matrix_row"] = join_row(cells)


def assert_done_with_warnings(res, project):
    assert res.code == 5 and project.record["status"] == "success-with-warnings" and project.record["warnings"], res.describe()


def test_harness_the_lists_cap_is_the_shared_peer_cap():
    assert LIST_CAP == sc.PEER_CAP == 10, "ADR-050 D2, ruled at W3: one cap for ruling C's sentence and for every list of IDs in a rendered markdown file"


@pytest.mark.parametrize("size", [10, 11, 14], ids=["ten-are-named-in-full", "eleven-are-ten-and-one-more", "fourteen-are-ten-and-four-more"])
def test_md_section_5_the_examples_cell_names_at_most_ten_ids(stage, renderer, tmp_path, size):
    """ADR-050 D2, ruled at W3 (question 4): the Examples cell names the first ten IDs of its shift in S-2's order, joined by ``, ``, then
    `` and N more`` with N exact, and has no tail at ten or fewer. It is the cap of ruling C's sentence (``sarif_common.PEER_CAP``), and the
    same form as every other list of IDs in a rendered markdown file. These shifts hold ``size`` findings, all with no shift."""
    many = [finding("I-%d" % number, "vector-store", "Synthetic gap number %d." % number, "Low", "2.8", "missing", "logging-audit", None, [],
                    recommendation("Log it.", "src/audit/log.py", "Events.", "Low", "one line")) for number in range(1, size + 1)]
    project = run_ok(stage, renderer, tmp_path, findings=many)
    _header, rows = table_of(subsection_of(project.md, "## 5. Residual Risk Summary", "### Per-Severity-Band Shift"), "Shift")
    shown = {re.sub(r"\*", "", row[0]).strip(): row for row in rows}
    assert int(shown["No Shift"][1]) == size and int(re.sub(r"\*", "", shown["Total"][1])) == size
    assert shown["No Shift"][2] == named_list([item["id"] for item in many]), shown["No Shift"][2]


def test_md_when_every_finding_has_a_control_none_is_unmitigated_and_nothing_is_recommended(stage, renderer, tmp_path):
    project = run_ok(stage, renderer, tmp_path, findings=[by_id(i) for i in ("S-2", "T-1")])  # both found
    summary = section(project.md, "## 1. Executive Summary")
    assert not re.search(r"\*\*Highest-Risk Unmitigated Finding\*\*: (?:S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-\d+", summary), "a found finding is never it"
    assert recommendation_blocks(project.md) == {} and len(matrix_rows(project.md)) == 2


def test_md_when_no_control_was_found_section_3_has_no_control(stage, renderer, tmp_path):
    project = run_ok(stage, renderer, tmp_path, findings=[by_id(i) for i in ("E-5", "E-3", "R-1")])  # all missing
    assert control_blocks(project.md) == []
    assert persisted(project.md) and tachi_parsers.parse_controls_assessment_inputs(project.md)["errors"] == []
    assert len(recommendation_blocks(project.md)) == 3


# --------------------------------------------------------------------------- the baseline

def test_baseline_a_directory_with_no_controls_file_is_no_baseline_and_says_so(stage, renderer, tmp_path):
    """D9: "a missing file means no baseline: the stage scores fresh and records why". reading: the scorer's warning code."""
    project = Project(stage, renderer, tmp_path)
    empty = tmp_path / "empty-baseline"
    empty.mkdir()
    res = project.run(baseline_dir=str(empty))
    assert_done_with_warnings(res, project)
    assert [warning["code"] for warning in project.record["warnings"]] == ["baseline-unresolved"]
    assert_all_fresh(project)


def test_baseline_an_unreadable_controls_file_is_no_baseline_and_says_so(stage, renderer, tmp_path):
    """D9 (S-12(d)): a present file that "isn't UTF-8" counts as missing, and the stage warns. reading: the scorer's warning code."""
    project = Project(stage, renderer, tmp_path)
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    (baseline / MD).write_bytes(b"\xff\xfe not utf-8")
    res = project.run(baseline_dir=str(baseline))
    assert_done_with_warnings(res, project)
    assert [warning["code"] for warning in project.record["warnings"]] == ["baseline-unreadable"]
    assert_all_fresh(project)


def test_baseline_a_resolved_baseline_with_nothing_carried_counts_zero_and_is_a_full_scan(stage, renderer, tmp_path):
    """The template: ``carry_forward_count`` is "null when no baseline", so a baseline that resolved and carried nothing counts 0, and the
    scope is full (every agent scanned afresh)."""
    first = run_ok(stage, renderer, Path(tmp_path) / "first")
    follow = follow_up(stage, renderer, Path(tmp_path) / "second", first)
    res = follow.run(baseline_dir=follow.baseline)
    assert res.code == 0, res.describe()
    assert frontmatter_value(follow.md, "carry_forward_count") == "0" and frontmatter_value(follow.md, "rescan_scope") == "full"
    assert follow.record["warnings"] == []
    assert_nothing_counted(follow.record)


def carry_the_planners_rows(follow):
    """The agent's part for every batch of ``follow``, written as the command has it done (AR-T3): the planner (run with the baseline) puts
    each UNCHANGED finding's persisted results in its unit's row, the agent copies them back with ``carried_forward`` set, and ``reconcile``
    completes. Returns the canonical IDs whose rows were copied, in the order the batches gave them."""
    follow.plan(baseline_dir=str(follow.baseline))
    keys = ("control_status", "control_category", "confidence", "evidence", "matrix_row", "recommendation_body")
    seen = []
    for batch_id in follow.batches():
        units = {canon(unit["finding_id"]): unit for unit in follow.batch_input(batch_id)["units"]}

        def copy_units(part, units=units):
            for item in part["items"]:
                unit = units[canon(item["finding_id"])]
                assert all(key in unit for key in keys), "the planner puts every persisted value in an UNCHANGED unit's row"
                item.update({key: copy.deepcopy(unit[key]) for key in keys})
                item["carried_forward"] = True
                seen.append(canon(item["finding_id"]))

        follow.write_part(batch_id, mutate=copy_units)
    assert follow.reconcile().code == 0
    return seen


def test_carry_the_agent_copies_the_planners_unit_row_and_the_renderer_takes_it_unchanged(stage, renderer, tmp_path):
    """AR-T3 end to end (T036 with T035): the planner puts run 1's persisted results in each UNCHANGED unit's row (``part-files.md``: its
    ``evidence[]``, ``matrix_row`` and ``recommendation_body``, decoded, beside the status, category and confidence), the agent copies them
    back with ``carried_forward`` set, and the renderer shows ``CF`` and keeps the same values, with no overwrite and no fallback."""
    first = run_ok(stage, renderer, Path(tmp_path) / "first")
    follow = follow_up(stage, renderer, Path(tmp_path) / "second", first)
    seen = carry_the_planners_rows(follow)
    assert sorted(seen, key=s2_key) == [canon(i) for i in S2_ORDER]
    res = follow.render()
    assert res.code in (0, 5), res.describe()
    tp.validate_stage_record(follow.record)
    assert_carried_from(follow, first)


# --------------------------------------------------------------------------- D8's fallback: only risk-scores.sarif

def sarif_input(findings, mitigated=True):
    """A ``risk-scores.sarif`` in the fields that T142's reader takes (D8): the member set, each result's composite and band, and its
    component, threat and layer. ``mitigated`` gives each result but E-3's a ``message.markdown``."""
    results = []
    for item in findings:
        inherent = golden(item["id"])[0]
        message = {"text": item["threat"]}
        if mitigated and item["id"] != "E-3":
            message["markdown"] = "Source mitigation for %s." % item["id"]
        results.append({
            "ruleId": "tachi/stride/spoofing", "level": "warning", "message": message,
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": URI}, "region": {"startLine": 1}},
                           "logicalLocations": [{"name": item["component"], "kind": "process"}]}],
            "partialFingerprints": {"primaryLocationLineHash": "0000000000000000:1", "findingId/v1": item["id"]},
            "properties": {"security-severity": inherent, "severity-band": ts.band(Decimal(inherent)),
                           "maestro-layer": ODD_LAYER if item["id"] == S2_ID else COMPONENTS[item["component"]][1]}})
    return json.dumps({"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "tachi-risk-scorer"}}, "results": results}]})


def use_sarif(project, text):
    """T036's fallback: ``--risk-scores`` names a ``risk-scores.md`` that is absent, and ``risk-scores.sarif`` lies beside it."""
    project.risk_scores.unlink()
    (project.out / "risk-scores.sarif").write_text(text, encoding="utf-8")


def test_fallback_a_run_with_only_risk_scores_sarif_renders_the_same_findings(stage, renderer, tmp_path):
    """D8 (AR-T2): when ``risk-scores.md`` is absent the member set and the inherent scores come from ``risk-scores.sarif``, and each member's
    layer from its own result (gap B). That form records no ``delta_status``, so each member is flagged ``input:delta_status:not-in-form`` and the
    stage record warns. The SARIF's ``message.markdown`` is the source result's, or ``""`` where it has none (P0-8)."""
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, sarif_input(FINDINGS))
    res = project.run(mutate=with_cells(S2_ID, {"MAESTRO Layer": ODD_LAYER}))
    assert_done_with_warnings(res, project)
    assert frontmatter_value(project.md, "source_file") == "run/risk-scores.sarif"
    found = matrix_rows(project.md)
    assert sorted(found, key=s2_key) == [canon(i) for i in S2_ORDER]
    for finding_id, (band, row) in found.items():
        inherent, inherent_band, _factor, residual, _residual_band = golden(finding_id)
        assert (row["Inherent Score"], row["Inherent Severity"], row["Residual Score"], band) == (inherent, inherent_band, residual, golden(finding_id)[4])
    assert found[S2_ID][1]["MAESTRO Layer"] == ODD_LAYER
    assert "value-not-in-form" in [warning["code"] for warning in project.record["warnings"]]  # reading: the scorer's code for it
    lines = integrity_text(project.md).split("\n")
    for finding_id in OPEN_IDS:
        assert any(re.search(id_pattern(finding_id), line) and "input" in line and "delta_status" in line and "not-in-form" in line for line in lines), finding_id
    results = results_by_id(project.sarif)
    for item in FINDINGS:
        assert results[item["id"]]["message"]["markdown"] == ("" if item["id"] == "E-3" else "Source mitigation for %s." % item["id"]), item["id"]
        assert results[item["id"]]["properties"]["maestro-layer"] == (ODD_LAYER if item["id"] == S2_ID else COMPONENTS[item["component"]][1])
        assert "input:delta_status:not-in-form" in results[item["id"]]["properties"]["integrity-flags"]


def plan_holding(project, name, text):
    """Make the project's plan hold ``text`` as its input ``name``, as a plan made from ``text`` would: the file is rewritten, the plan records its
    new digest and size, and the project takes the plan's new digest. Every batch input and part stays as it was, so this is a part set that is
    complete and valid for the plan's own units. It is how a test reaches a refusal of the renderer that the planner now makes first (T067b M1)."""
    plan = project.plan_json()
    entry = plan["inputs"][name]
    data = text.encode("utf-8")
    Path(entry["path"]).write_bytes(data)
    entry["sha256"], entry["bytes"] = tp.sha256_hex(data), len(data)
    path = project.plan_dir / "plan.json"
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    project.digest = tp.file_digest(path)


def without_a_score(document):
    """S-2's result (the first) loses its composite: ``properties.security-severity`` is the only place the scorer's SARIF holds one."""
    del document["runs"][0]["results"][0]["properties"]["security-severity"]


def with_a_peer_reference_only(document):
    """R-1 loses its own result and T-4's names it in ``relatedLocations``, the legacy form: the file lists R-1 as a member that it holds no result for."""
    results = document["runs"][0]["results"]
    results[:] = [result for result in results if result["partialFingerprints"]["findingId/v1"] != "R-1"]
    result_of(document, "T-4")["relatedLocations"] = [{"id": 0, "message": {"text": "R-1: " + by_id("R-1")["threat"]}}]


BACKSTOPS = [  # (name, the finding the message names, the edit of a valid risk-scores.sarif, the reason's words)
    ("a-member-with-no-score", "S-2", without_a_score, "holds no score from 0.0 to 10.0"),
    ("a-member-named-only-as-a-peer-reference", "R-1", with_a_peer_reference_only, "only as a peer reference"),
]


@pytest.mark.parametrize("name,finding_id,edit,reason", BACKSTOPS, ids=[case[0] for case in BACKSTOPS])
def test_fallback_backstop_the_renderer_still_refuses_a_member_that_it_cannot_score(stage, renderer, tmp_path, name, finding_id, edit, reason):
    """T067b M1, the renderer's half. Under D8's fallback a member with no composite score, and a member that only a legacy peer reference names
    (it has no result of its own, so no score), can't be rendered. ``plan`` refuses both before it dispatches anything (KB 22; ``test_tachi_stage.py``
    pins that), so a plan made by this planner never holds them. The renderer keeps its own refusal as the backstop: a plan
    from an earlier planner, or one edited by hand, can still reach it, and the render then ends with exit 2 and the finding named, before it
    stages or replaces anything.

    The part set here is complete and valid. The plan is made from the whole file, every part is written and reconciled, and then
    ``plan_holding`` makes the plan hold the edited file, which is the plan that a planner without the refusal would have recorded."""
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, sarif_input(FINDINGS))
    project.earlier()
    project.prepare()
    document = json.loads(sarif_input(FINDINGS))
    edit(document)
    plan_holding(project, "risk_scores", json.dumps(document))
    res = project.render()
    assert res.code == 2, res.describe()
    assert_failure_message(res, project.plan_id)
    assert re.search(id_pattern(finding_id), res.err) and reason in res.err, "the message names the finding and says why: " + res.describe()
    assert "Remedy: regenerate it with /tachi.risk-score" in res.err, res.describe()
    assert not (project.plan_dir / "staged").exists(), "the refusal comes before anything is staged"
    project.assert_earlier_outputs_untouched()


def test_fallback_the_legacy_id_form_names_the_same_members(stage, renderer, tmp_path):
    """reading (T142's reader): an older ``risk-scores.sarif`` names its finding in ``properties.id`` and has no ``findingId/v1``."""
    project = Project(stage, renderer, tmp_path)
    document = json.loads(sarif_input(FINDINGS))
    for result in document["runs"][0]["results"]:
        result["properties"]["id"] = result["partialFingerprints"].pop("findingId/v1")
    use_sarif(project, json.dumps(document))
    res = project.run(mutate=with_cells(S2_ID, {"MAESTRO Layer": ODD_LAYER}))
    assert_done_with_warnings(res, project)
    assert sorted(matrix_rows(project.md), key=s2_key) == [canon(i) for i in S2_ORDER]


# --------------------------------------------------------------------------- the evidence file

def test_evidence_a_file_is_shown_in_its_canonical_spelling_and_persisted_as_written(stage, renderer, tmp_path):
    """``part-files.md``: "A ``file`` is checked, never rewritten. ``./a//b.py`` is kept as written in the validated part. The resolver
    canonicalizes it at render time (ADR-050 D7), and both rendered files use that canonical spelling, so ``.md`` and ``.sarif`` agree"."""
    def untidy(part):
        for item in part["items"]:
            for entry in item["evidence"]:
                if entry["file"] == "src/auth/tokens.py":
                    entry["file"] = "./src//auth/tokens.py"

    project = run_ok(stage, renderer, tmp_path, untidy)
    assert "**Detected in**: `src/auth/tokens.py:42`" in project.md and "./src//auth" not in project.md.split("## 7. Analysis Integrity")[0]
    assert persisted(project.md)[S2_ID]["evidence"][0]["file"] == "./src//auth/tokens.py"
    result = results_by_id(project.sarif)[S2_ID]
    assert result["properties"]["control-evidence"][0]["file"] == "src/auth/tokens.py"
    assert result["relatedLocations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "src/auth/tokens.py"


# A file that the resolver refuses (missing, a link, not a regular file) is flagged and never exit 2: the architect ruled it at W3 (question 5),
# which flips T052's open question 1 and T056's first reading. Its goldens are in Section 18, "the evidence file".


# --------------------------------------------------------------------------- what the inputs hold

def test_input_a_forbidden_character_in_the_threat_model_is_refused_and_not_echoed(stage, renderer, tmp_path):
    """P0-4 (``module-signatures.md``, ``forbidden_character``): "A renderer, at the point it takes a value from an input that isn't a part,
    refusing the value with exit 2"."""
    project = Project(stage, renderer, tmp_path)
    original = by_id("E-3")["threat"]
    text = project.threats.read_text(encoding="utf-8")
    assert original in text
    project.threats.write_text(text.replace(original, original.replace("skip", "skip\x1b[31m")), encoding="utf-8")
    project.earlier()
    res = project.run()
    assert res.code == 2, res.describe()
    assert re.search(id_pattern("E-3"), res.err) and "\x1b" not in res.err, res.describe()
    project.assert_earlier_outputs_untouched()


def test_input_a_forbidden_character_in_a_value_taken_from_the_scored_input_is_refused(stage, renderer, tmp_path):
    """The same rule for ``risk-scores.md``. With no ``source_file`` the finding texts come from it, so a bidi control in one would reach the
    output unless it is refused."""
    original = by_id("E-3")["threat"]
    text = make_risk_scores_md().replace('source_file: "run/threats.md"', "source_file: null").replace(original, original.replace("skip", "skip‮"))
    assert "‮" in text
    project = Project(stage, renderer, tmp_path, risk_scores_text=text)
    project.earlier()
    res = project.run(mutate=every_item(layers_unclassified))
    assert res.code == 2, res.describe()
    assert re.search(id_pattern("E-3"), res.err) and "‮" not in res.err, res.describe()
    project.assert_earlier_outputs_untouched()


def test_input_reused_id_is_carried_over_from_the_scored_input(stage, renderer, tmp_path):
    """Ruling B (D7; ``sarif-result.md``): both files carry ``reused-id:finding_id:baseline`` for the same finding, and the scored input's
    Score Flags table is where the next stage finds it."""
    text = make_risk_scores_md() + ("\n## 6. Score Integrity\n\n### Score Flags\n\n| ID | Flag | Field | Stored | Rendered | Cause |\n"
                                    "|----|------|-------|--------|----------|-------|\n| T-1 | reused-id | finding_id | T-1 | " + DASH + " | baseline |\n\n")
    project = Project(stage, renderer, tmp_path, risk_scores_text=text)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    assert project.record["counts"]["reused-id"] == 1
    assert any(re.search(id_pattern("T-1"), line) and "reused-id" in line and "finding_id" in line and "baseline" in line for line in integrity_text(project.md).split("\n"))
    flags = flags_of(project.sarif)
    assert flags["T-1"] == ["reused-id:finding_id:baseline"] and [i for i, found in flags.items() if found and i != "T-1"] == []


def test_input_a_finding_listed_twice_in_the_threat_model_is_read_once_and_warned(stage, renderer, tmp_path):
    """``part-files.md``: a repeated canonical ID is read, never refused; "each renderer lists the IDs under Input Issues (scorer §6, controls §7)
    and as the stage record's warning ``duplicate-finding-id``, and exits 5"."""
    project = Project(stage, renderer, tmp_path, repeated=[("T-1", "auth-broker")])
    res = project.run()
    assert_done_with_warnings(res, project)
    assert [warning["code"] for warning in project.record["warnings"]] == ["duplicate-finding-id"]
    assert re.search(id_pattern("T-1"), subsection_of(project.md, "## 7. Analysis Integrity", "### Input Issues"))
    assert len(matrix_rows(project.md)) == len(FINDINGS), "one ID is one finding (D-4)"


def test_input_a_scored_input_with_no_source_file_leaves_the_threat_model_unread_and_the_layers_unclassified(stage, renderer, tmp_path):
    """T053 and gap B: with no readable ``threats.md`` there is none, with a reason in the stage record that says the layers fell back
    too, and each layer is ``Unclassified``. The component and threat come from the scored input."""
    text = make_risk_scores_md().replace('source_file: "run/threats.md"', "source_file: null")
    project = Project(stage, renderer, tmp_path, risk_scores_text=text)
    res = project.run(mutate=every_item(layers_unclassified))
    assert_done_with_warnings(res, project)
    assert any("layer" in warning["detail"].lower() for warning in project.record["warnings"]), project.record["warnings"]
    found = matrix_rows(project.md)
    assert len(found) == len(FINDINGS) and {row["MAESTRO Layer"] for _band, row in found.values()} == {"Unclassified"}
    assert {row["Component"] for _band, row in found.values()} == {item["component"] for item in FINDINGS}
    assert {result["properties"]["maestro-layer"] for result in project.sarif["runs"][0]["results"]} == {"Unclassified"}


def test_input_a_source_file_that_does_not_validate_is_explained_in_the_record(stage, renderer, tmp_path):
    text = make_risk_scores_md(source="../elsewhere/threats.md")
    project = Project(stage, renderer, tmp_path, risk_scores_text=text)
    res = project.run(mutate=every_item(layers_unclassified))
    assert_done_with_warnings(res, project)
    reason = rules.check_run_file("../elsewhere/threats.md", cwd=Path(project.root), expected_name="threats.md").reason
    assert reason and any(reason in warning["detail"] for warning in project.record["warnings"]), project.record["warnings"]


# --------------------------------------------------------------------------- the SARIF as the 1.1 template shows it

def test_sarif_a_finding_with_no_mitigation_has_an_empty_markdown_and_the_key_stays(stage, renderer, tmp_path):
    """P0-8: ``message.markdown`` is always written, the empty string included, and the self-check passes."""
    project = Project(stage, renderer, tmp_path)
    cell = mitigation_of(by_id("E-3"))
    text = project.threats.read_text(encoding="utf-8")
    assert text.count(cell) == 1
    project.threats.write_text(text.replace(cell, ""), encoding="utf-8")
    res = project.run()
    assert res.code in (0, 5), res.describe()
    results = results_by_id(project.sarif)
    assert results["E-3"]["message"] == {"text": "%s [Control: missing]" % by_id("E-3")["threat"], "markdown": ""}
    assert results["E-5"]["message"]["markdown"] == mitigation_of(by_id("E-5"))
    sc.self_check(project.sarif["runs"][0]["results"], tool=TOOL, member_ids=OPEN_IDS, assignments={}, resolved_ids=RESOLVED_IDS, uri=URI)


def test_template_the_sarif_rules_are_the_templates_with_a_computed_severity(base):
    """Gap A (``sarif-result.md``): each rule has ``id``, ``shortDescription``, ``fullDescription``, ``properties`` (``tags``, then
    ``security-severity``) and ``relationships``, in that order, as the template shows them. Only the severity is computed."""
    require_the_1_1_template()
    template = {rule["id"]: rule for rule in json.loads(template_text(SARIF))["runs"][0]["tool"]["driver"]["rules"]}
    written = base.sarif["runs"][0]["tool"]["driver"]["rules"]
    assert len(written) == 7, "one rule for each category with a result: the project has no information disclosure finding"
    assert [rule["id"] for rule in written] == [rule_id for rule_id in template if rule_id in {rule["id"] for rule in written}], "in the template's order"
    for rule in written:
        wanted = copy.deepcopy(template[rule["id"]])
        wanted["properties"]["security-severity"] = rule["properties"]["security-severity"]
        assert rule == wanted, rule["id"]
        assert list(rule) == ["id", "shortDescription", "fullDescription", "properties", "relationships"] and list(rule["properties"]) == ["tags", "security-severity"]


def test_template_each_result_carries_the_templates_properties_in_its_order(base):
    """Gap B (``sarif-result.md``): ``maestro-layer`` follows ``residual-risk``; ``integrity-flags`` is last, and a group member's correlation keys
    come after it. The order is the template's."""
    require_the_1_1_template()
    order = list(json.loads(template_text(SARIF))["runs"][0]["results"][0]["properties"])
    assert order.index("maestro-layer") == order.index("residual-risk") + 1 and order[-1] == "integrity-flags"
    for result in base.sarif["runs"][0]["results"]:
        assert list(result["properties"]) == order, result["partialFingerprints"]["findingId/v1"]


# --------------------------------------------------------------------------- the failure path

def test_failure_an_unexpected_error_is_a_failure_message_and_replaces_no_file(stage, renderer, tmp_path, monkeypatch):
    """AR-T5 (D4): a failure prints the stage's FAILED message with a remedy and the plan's place, whatever raised it. An exception that no
    check meant to raise is the renderer's own defect, and it too leaves every canonical file as it was. ``tachi_parts.fence_for`` is the
    shared function that every Section 3 control calls, so an error seeded there is no check's."""
    project = Project(stage, renderer, tmp_path)
    project.earlier()
    project.prepare()

    def boom(snippet):
        raise RuntimeError("seeded defect\x07")

    monkeypatch.setattr(tp, "fence_for", boom)
    res = project.render()
    assert res.code not in (0, 5), res.describe()
    assert_failure_message(res, project.plan_id)
    assert "seeded defect" in res.err and "\x07" not in res.err, "reading: the error is named, with its control characters made plain (the scorer's)"
    project.assert_earlier_outputs_untouched()


# =============================================================================
# 17. The W3 sweep's rulings for this renderer (ADR-050 D3 and D7; sarif-result.md, gap B)
# =============================================================================
#
# The architect's sweep gave this module three things. First, a code snippet that quotes headings and an inputs table, over two runs: a
# snippet's lines stay raw inside their fence (D3), so a reader that finds a section by a heading line wherever it is would take the
# quoted line for the real one, and the run would fail a from-disk check (exit 4) or lose every carried result. Second, the URI with no
# ``--architecture`` flag: the planner holds none, both agents read the run's snapshot, and the renderer resolves D7's chain, so a
# snapshot is never the URI. Third, gap B: every controls result carries the scorer's ``maestro-layer``.
#
# What turns them green: the snippet cases need T059's fence-aware lookups (``_check_staged``), and the one that names S-1 also needs R3a's
# narrower RESOLVED scan (question 9); the URI and layer cases need T053.

# The architect's five lines, with S-7 in the row: a finding of no project here, open or resolved, so that the case holds against any self-check. The
# same lines with S-1, a RESOLVED finding of the project, are the architect's own. The self-check read an ID in a snippet as a reference (P0-10) until
# question 9's narrower scan (ruled at W3), so that case waits for it.
QUOTED = "\n".join(["## 4. Recommendations", "### Assessment Inputs", "| ID | Field | Value |", "|----|-------|-------|", "| S-7 | control_status | found |"])
QUOTED_S1 = QUOTED.replace("S-7", "S-1")
CONTROL_AND_FENCE_MARKS = "x = 1\n**Detected in**: `x.py:1`\n```\n~~~\n## 2. Coverage Matrix"  # a control's own line, shorter and tilde fences, an earlier section's head
SECTION_5_TABLE = "### Aggregate Risk Reduction\n| Metric | Value |\n|---|---|\n| Total Inherent Risk Score | 1.0 |\n| Overall Reduction | 1.0% |"  # Section 5 follows Section 3
# T067b H1: the head of Section 4 and then the head of Section 5, quoted. A reader that finds Section 4 by a raw line, as the shipped
# ``parse_compensating_controls_md`` does, opens it inside Section 3 and closes it on the next line, and every recommendation is lost with no error.
SECTION_4_THEN_5 = "## 4. Recommendations\n## 5. Residual Risk Summary\nx = 1"
PLAIN = "pool = Pool(max_per_caller=4)\npool.open()\npool.limit(4)\npool.warm()\npool.close()"  # five lines that are no heading, no row and no fence
QUOTING = [("the-architects-five-lines", QUOTED), ("the-architects-lines-naming-a-resolved-finding", QUOTED_S1),
           ("a-control-line-and-fence-marks", CONTROL_AND_FENCE_MARKS), ("a-section-5-table", SECTION_5_TABLE),
           ("section-4s-head-then-section-5s-head", SECTION_4_THEN_5)]


def with_snippet(findings, finding_id, snippet, entry=0):
    """Copies of ``findings`` in which evidence entry ``entry`` of ``finding_id`` holds ``snippet`` (a deep copy, so the module's own findings stay as they are)."""
    out = copy.deepcopy(findings)
    by_id(finding_id, out)["evidence"][entry]["snippet"] = snippet
    return out


def block_of(snippet):
    """What Section 3 holds for a snippet of python: its fence (``tachi_parts.fence_for``), the language, the snippet as written, the fence again."""
    fence = tp.fence_for(snippet)
    return "%spython\n%s\n%s\n" % (fence, snippet, fence)


def blank_fences(md):
    """``md`` with every line of every fenced block emptied, the fence lines too: the file as a reader that skips code sees it. The section
    helpers above find a heading by its first characters wherever it sits, so they read a file that quotes a heading in a snippet as having two."""
    out, fence = [], None
    for line in md.split("\n"):
        if fence is None:
            opener = re.match(r"[ \t]*(`{3,}|~{3,})", line)
            if not opener or (opener.group(1)[0] == "`" and "`" in line[opener.end():]):
                out.append(line)
                continue
            fence = opener.group(1)
        else:
            closer = re.fullmatch(r"[ \t]*(`{3,}|~{3,})[ \t\r]*", line)
            if closer and closer.group(1)[0] == fence[0] and len(closer.group(1)) >= len(fence):
                fence = None
        out.append("")
    return "\n".join(out)


class WithoutFences(object):
    """A project whose ``md`` is read through ``blank_fences``, so that the carry helpers can read a file that quotes headings in a snippet."""

    def __init__(self, project):
        self.project = project

    def __getattr__(self, name):
        return getattr(self.project, name)

    @property
    def md(self):
        return blank_fences(self.project.md)


@pytest.mark.parametrize("name,snippet", QUOTING, ids=[case[0] for case in QUOTING])
def test_capture_a_snippet_that_quotes_headings_or_a_table_is_read_as_neither_over_two_runs(stage, renderer, tmp_path, name, snippet):
    """The architect's two-run case (W3 sweep; ADR-050 D3, "Finding a section"). One found control's evidence snippet is five lines that quote
    ``## 4. Recommendations``, ``### Assessment Inputs`` and an inputs table's header, separator and row. D3 writes a snippet raw inside its
    fence, so those lines sit in Section 3 as written, and every reader that a from-disk check or the next run relies on finds a section by
    its exact heading line outside code. Run 1 exits 0 and its Section 7 reads back whole. Run 2 carries every UNCHANGED result: the planner
    reads run 1's file, the agent copies what it was handed, and the render exits 0 with every row carried.

    The snippet is S-2's, which S-10 shares: that control is the first of Section 3's nine, so a lookup that a quoted heading cuts short loses
    the "Detected in" lines of the eight after it, and a quoted ``## 4.`` has a later real one to be mistaken for.

    Mutation check (by hand, in a clone, results file): with the renderer's five ``match_heading`` calls on ``outside_fences=False``, run 1 of
    every case exits 4 ("## 4. Recommendations has 2 headings" and the like). Switched off one at a time, each call is caught by a case.

    The last case is T067b's H1, which is the one that a SARIF ``recommendation`` shows: the snippet ends the shipped reader's Section 4
    inside Section 3, so a SARIF built by that reader holds no recommendation at all, with exit 0 and an intact markdown. The case pins each
    ``recommendation`` to the agent's own What to Implement, and then the whole SARIF to the one of the same project with five plain lines, so
    a reader that takes the quoted lines for the section's own fails it."""
    findings = with_snippet(FINDINGS, "S-2", snippet)
    first = Project(stage, renderer, tmp_path / "first", findings=findings)
    res = first.run()
    assert res.code == 0, res.describe()
    tp.validate_stage_record(first.record)
    assert first.record["warnings"] == []
    assert_nothing_counted(first.record)
    assert block_of(snippet) in first.md, "Section 3 holds the snippet as written, inside its fence"
    read = tachi_parsers.parse_controls_assessment_inputs(first.md)
    assert read["errors"] == [] and sorted(read["inputs"], key=s2_key) == [canon(i) for i in S2_ORDER], "Section 7 reads back whole"
    for item in findings:
        want = controls_item(item)
        want.pop("finding_id")
        assert read["inputs"][canon(item["id"])] == want, item["id"]
    assert read["inputs"]["S-2"]["evidence"][0]["snippet"] == read["inputs"]["S-10"]["evidence"][0]["snippet"] == snippet

    # nothing else moved: the same project with five plain lines for the snippet writes the same files, bar the snippet and the stamp
    twin = run_ok(stage, renderer, tmp_path / "twin", findings=with_snippet(FINDINGS, "S-2", PLAIN))
    swapped = first.md.replace(block_of(snippet), block_of(PLAIN)).replace(tp.escape_cell(snippet, keep_slots=True), tp.escape_cell(PLAIN, keep_slots=True))
    assert without_stamp(swapped) == without_stamp(twin.md), "the quoted lines change nothing but themselves"
    results = results_by_id(first.sarif)
    for item in findings:   # each recommendation is the agent's own text, which a reader that lost Section 4 would leave empty (T067b H1)
        wanted = "" if item["control"] == "found" else item["rec"]["what"]
        assert results[item["id"]]["properties"]["recommendation"] == wanted, "the SARIF's recommendation of %s" % item["id"]

    def normalized(project):
        doc = copy.deepcopy(project.sarif)
        doc["runs"][0]["properties"]["tachi_provenance"]["input_digest"] = None
        for result in doc["runs"][0]["results"]:
            for entry in result["properties"]["control-evidence"]:
                entry["snippet"] = PLAIN if entry["snippet"] == snippet else entry["snippet"]
        return doc

    assert normalized(first) == normalized(twin)

    follow = follow_up(stage, renderer, tmp_path / "second", first)
    seen = carry_the_planners_rows(follow)
    assert sorted(seen, key=s2_key) == [canon(i) for i in S2_ORDER], "the planner read run 1's Section 7 whole, so every finding has its result to carry"
    res = follow.render()
    assert res.code == 0, res.describe()
    tp.validate_stage_record(follow.record)
    assert_carried_from(WithoutFences(follow), WithoutFences(first))
    assert block_of(snippet) in follow.md and persisted(follow.md)["S-2"]["evidence"][0]["snippet"] == snippet, "the snippet came through the carry as written"


def whole_file_recommendations(md_text):
    """The reader that built the SARIF's ``recommendation`` before T146: the shipped ``parse_compensating_controls_md`` over the whole file,
    which finds its Section 4 by a raw line (``^##\\s+4\\.\\s+Recommendations``, with no fence tracking)."""
    return {canon(found["id"]): found["recommendation"] for found in tachi_parsers.parse_compensating_controls_md(md_text)["findings"]}


SEEDED_READERS = [  # (name, the reader that replaces the renderer's, the snippet of S-2's evidence: None keeps the project's own)
    ("the-whole-file-reader-with-a-quoted-heading", whole_file_recommendations, SECTION_4_THEN_5),
    ("a-reader-that-finds-no-block", lambda md_text: {}, None),
]


@pytest.mark.parametrize("name,reader,snippet", SEEDED_READERS, ids=[case[0] for case in SEEDED_READERS])
def test_capture_a_defect_in_the_reader_that_builds_the_sarifs_recommendations_fails_the_from_disk_check(stage, renderer, tmp_path, monkeypatch, name, reader, snippet):
    """T067b H1, the check's half. The SARIF's ``recommendation`` is read from the rendered Section 4, so a from-disk check that read it back with the
    same function could not see a defect in that function: the two sides would agree whatever it did. The check derives the value again from each
    validated part body, so a reader that loses the text ends the render with exit 4, and no canonical file is replaced.

    The first case seeds back the defect that H1 found (the shipped reader over the whole file, with ``SECTION_4_THEN_5`` in Section 3), and the
    second a reader that finds nothing. Neither writes a SARIF the check accepts. (Without the seed, the same project renders with exit 0: that is
    the first case of ``test_capture_a_snippet_that_quotes_headings_or_a_table_is_read_as_neither_over_two_runs``.)"""
    findings = FINDINGS if snippet is None else with_snippet(FINDINGS, "S-2", snippet)
    project = Project(stage, renderer, tmp_path, findings=findings)
    project.earlier()
    project.prepare()
    monkeypatch.setattr(renderer, "_section_4_recommendations", reader)
    res = project.render()
    assert res.code == 4, "a completeness or parity check that fails is exit 4 (cli.md): %s" % res.describe()
    assert_failure_message(res, project.plan_id)
    first = "T-4"  # the first finding in S-2 order that has a Section 4 block, and so a recommendation (the message cuts a long value at 60 characters)
    assert re.search(r"%s: the recommendation is '' in the SARIF and %s" % (id_pattern(first), re.escape("'" + by_id(first)["rec"]["what"][:20])), res.err), res.describe()
    project.assert_earlier_outputs_untouched()


# --------------------------------------------------------------------------- the architecture source, with no flag

SNAPSHOT_PATH = "run/architecture.md"  # the run directory's copy of the architecture file, relative to the working directory
URI_CHAIN = [  # (name, the threat model's body line, whether the run directory holds the snapshot, every result's URI, the warnings' codes)
    ("a-body-line-outside-docs-security", "docs/other/architecture.md", True, "docs/other/architecture.md", []),
    ("an-untidy-body-line-is-spelled-canonically", "./docs//other/architecture.md", True, "docs/other/architecture.md", []),
    ("no-body-line-with-a-snapshot-beside-the-threat-model", None, True, URI, ["architecture-path:body-line:absent"]),
    ("a-body-line-with-no-snapshot-fails-closed-to-the-default", "docs/other/architecture.md", False, URI, ["architecture-path:body-line:no-snapshot"]),
    ("a-body-line-that-names-the-snapshot-itself", SNAPSHOT_PATH, True, URI, ["architecture-path:body-line:is-snapshot"]),
]


@pytest.mark.parametrize("body,snapshot,uri,codes", [case[1:] for case in URI_CHAIN], ids=[case[0] for case in URI_CHAIN])
def test_uri_with_no_flag_every_result_names_the_body_lines_canonical_path_or_the_default_and_never_the_snapshot(stage, renderer, tmp_path, body, snapshot, uri, codes):
    """ADR-050 D7, "With no flag" (ruled at W3, the architect's sweep): the planner holds no ``refs.architecture`` and never fills it from the
    chain or from a snapshot. Both agents read the run's snapshot as data, and the renderer resolves D7's chain: the body line (canonical, and
    only when the snapshot checks it), else the default. So the URI is one of those two, in every result, whatever the run directory holds,
    and the stage record lists each warning of the chain, in order, with the override flag named (T052 pins the resolver itself)."""
    project = Project(stage, renderer, tmp_path, body_line=body)
    elsewhere = project.root / "docs" / "other" / "architecture.md"
    elsewhere.parent.mkdir(parents=True)
    elsewhere.write_text("# an architecture file that is not under docs/security\n", encoding="utf-8")
    if snapshot:
        (project.out / "architecture.md").write_text("# the snapshot that the threat model copied\n", encoding="utf-8")
    res = project.run(architecture=None)
    assert res.code == (5 if codes else 0), res.describe()
    plan = project.plan_json()
    assert "architecture" not in plan["refs"] and not plan.get("architecture_warning"), "no flag, so the plan holds none"
    results = project.sarif["runs"][0]["results"]
    uris = {result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for result in results}
    assert uris == {uri} and SNAPSHOT_PATH not in uris, "the snapshot is read by the agents and is never the URI"
    sc.self_check(results, tool=TOOL, member_ids=OPEN_IDS, assignments={}, resolved_ids=RESOLVED_IDS, uri=uri)
    record = project.record
    assert [warning["code"] for warning in record["warnings"]] == codes, "the stage record lists the resolver's warnings, in order"
    assert record["status"] == ("success-with-warnings" if codes else "success")
    assert all("--architecture-path" in warning["detail"] for warning in record["warnings"]), "each one names the override flag"


# --------------------------------------------------------------------------- gap B: the layer is the scorer's

def blank_section_7_layers(text):
    """``threats.md`` with the MAESTRO Layer cell of every Section 7 row emptied, so the chain's first step finds nothing."""
    out, inside = [], False
    for line in text.split("\n"):
        if line.startswith("## "):
            inside = line.startswith("## 7.")
        elif inside and line.startswith("| ") and not line.startswith("| Finding ID") and "|--" not in line:
            cells = line.split(" | ")
            cells[5] = ""
            line = " | ".join(cells)
        out.append(line)
    return "\n".join(out)


def respell_components(text):
    """``threats.md`` with each Section 1 component name in capitals: a lookup by the exact name finds nothing, and only the case-folded one does."""
    out, inside = [], False
    for line in text.split("\n"):
        if line.startswith("### "):
            inside = line.startswith("### Components")
        elif inside and line.startswith("| ") and not line.startswith("| Component") and "|--" not in line:
            cells = line.split(" | ")
            cells[0] = "| " + cells[0][2:].upper()
            line = " | ".join(cells)
        out.append(line)
    return "\n".join(out)


@pytest.fixture(scope="module")
def identity():
    """T052's module, ``test_sarif_identity.py``, imported when a case first needs it (as it imports ``test_render_risk_scores``), so that the rest of
    this module collects without it. Its ``make_project`` renders the scorer's own files first and then drives this stage, which is what gap B and the
    scorer's-own-SARIF fallback compare against."""
    from . import test_sarif_identity
    return test_sarif_identity


@pytest.fixture(scope="module")
def rrs():
    """The scorer renderer's goldens (T027), whose project T052's ``make_project`` builds on."""
    from . import test_render_risk_scores
    return test_render_risk_scores


@pytest.fixture(scope="module")
def entries(identity, stage, renderer):
    """``(tachi-stage.py, render-risk-scores.py)`` and ``.controls``, as T052's ``make_project`` takes them. The controls entry is this module's."""
    taken = identity.Entries((stage, _load_hyphenated_script("render_risk_scores_for_controls_tests", "render-risk-scores.py")))
    taken._controls = renderer
    return taken


@pytest.mark.parametrize("variant", ["as-written", "section-7-layers-blank", "blank-and-component-names-respelled"])
def test_layer_every_controls_result_has_the_scorers_maestro_layer_for_the_same_finding(identity, rrs, entries, tmp_path, variant):
    """sarif-result.md, gap B: a controls result's ``maestro-layer`` is "the string the scorer file writes for that finding", by the scorer's
    rule. The scorer's own file is rendered first (T052's project), from the same ``threats.md``. In the second variant the reference set holds no
    layer, so the chain reaches the component's Section 1 layer; in the third that lookup is by name only after a case fold. Both files agree."""
    project = identity.make_project(identity.CONTROLS_FILE, rrs, entries, tmp_path, groups=identity.FIRST_RUN_GROUPS)
    if variant != "as-written":
        text = blank_section_7_layers(project.threats.read_text(encoding="utf-8"))
        project.threats.write_text(respell_components(text) if variant.startswith("blank-and") else text, encoding="utf-8")
    res = project.run()
    assert res.code in (0, 5), res.describe()
    controls, scorer = identity.results_by(project.sarif), identity.results_by(project.scorer_sarif)
    assert sorted(controls) == sorted(scorer) and controls
    for finding_id, result in controls.items():
        assert result["properties"]["maestro-layer"] == scorer[finding_id]["properties"]["maestro-layer"], finding_id
    if variant != "as-written":
        assert {result["properties"]["maestro-layer"] for result in controls.values()} <= {layer for _kind, layer in COMPONENTS.values()}, "the component's layer, never Unclassified"


def blank_component_layers(text):
    """``threats.md`` with the MAESTRO Layer cell of every Section 1 component emptied, so the chain's last step finds nothing."""
    out, inside = [], False
    for line in text.split("\n"):
        if line.startswith("### "):
            inside = line.startswith("### Components")
        elif inside and line.startswith("| ") and not line.startswith("| Component") and "|--" not in line:
            cells = line.split(" | ")
            cells[2] = ""
            line = " | ".join(cells)
        out.append(line)
    return "\n".join(out)


def test_v48_a_controls_result_has_the_scorers_layer_when_only_the_findings_own_rows_hold_it(identity, rrs, entries, tmp_path):
    """T066's U-1, gap B end to end. The threat model is in the v4.48.x form: Section 7 and Section 1 hold no layer, and each finding's is in its own row of a
    §3 or §4 table (a row wider than its header, and a bold-labelled sub-table, among them), E-5's excepted, which has no row. Both renderers read those rows through
    ``tachi_parsers.parse_finding_layers``, so every controls result's ``maestro-layer`` is the scorer's, and an agent that copies the layer into its Section 2
    cell is not flagged ``input:maestro_layer:sources-disagree``."""
    project = identity.make_project(identity.CONTROLS_FILE, rrs, entries, tmp_path)
    text = blank_component_layers(blank_section_7_layers(project.threats.read_text(encoding="utf-8")))
    project.threats.write_text(text.replace("## 6. Risk Summary", rrs.v48_tables() + "\n## 6. Risk Summary", 1), encoding="utf-8")
    wanted = {item["id"]: "Unclassified" if item["id"] == rrs.V48_NO_ROW else COMPONENTS[item["component"]][1] for item in rrs.SPECS}
    res = project.run(mutate=together(*[with_cells(finding_id, {"MAESTRO Layer": layer}) for finding_id, layer in wanted.items()]))
    assert res.code in (0, 5), res.describe()
    controls, scorer = identity.results_by(project.sarif), identity.results_by(project.scorer_sarif)
    assert sorted(controls) == sorted(scorer) == sorted(wanted)
    for finding_id, layer in wanted.items():
        assert controls[finding_id]["properties"]["maestro-layer"] == scorer[finding_id]["properties"]["maestro-layer"] == layer, finding_id
        assert FLAG_OF["MAESTRO Layer"] not in controls[finding_id]["properties"]["integrity-flags"], "the agent's cell is the structured layer: %s" % finding_id
    assert {layer for layer in wanted.values()} - {"Unclassified"}, "layers were read, so the check is not vacuous"


def test_v48_an_agent_cell_that_differs_from_the_row_layer_is_flagged_once_and_the_sarif_follows_the_row(identity, rrs, entries, tmp_path):
    """The structured value wins (ADR-050 D2): S-2's row says edge-gateway's layer, and an agent that wrote another is flagged, with the SARIF unchanged."""
    project = identity.make_project(identity.CONTROLS_FILE, rrs, entries, tmp_path)
    text = blank_component_layers(blank_section_7_layers(project.threats.read_text(encoding="utf-8")))
    project.threats.write_text(text.replace("## 6. Risk Summary", rrs.v48_tables() + "\n## 6. Risk Summary", 1), encoding="utf-8")
    wanted = {item["id"]: "Unclassified" if item["id"] == rrs.V48_NO_ROW else COMPONENTS[item["component"]][1] for item in rrs.SPECS}
    agent = {finding_id: layer for finding_id, layer in wanted.items() if finding_id != "S-2"}
    agent["S-2"] = "L1 " + DASH + " Foundation Model"
    res = project.run(mutate=together(*[with_cells(finding_id, {"MAESTRO Layer": layer}) for finding_id, layer in agent.items()]))
    assert res.code in (0, 5), res.describe()
    controls = identity.results_by(project.sarif)
    assert controls["S-2"]["properties"]["maestro-layer"] == wanted["S-2"] != agent["S-2"]
    layer_flag = FLAG_OF["MAESTRO Layer"]
    assert controls["S-2"]["properties"]["integrity-flags"].count(layer_flag) == 1, "flagged once"
    assert [finding_id for finding_id, found in controls.items() if layer_flag in found["properties"]["integrity-flags"]] == ["S-2"]


SHIPPED_CONTROLS_SHAPES = [   # (the example, its open findings that no contract section of its threat model gives a layer: they are Unclassified)
    ("mobile-banking-app/sample-report", []),
    ("agentic-app/sample-report", ["AGP-1"]),   # a row wider than its header and bold-labelled sub-tables in §4.2
]


@pytest.mark.parametrize("example,unlisted", SHIPPED_CONTROLS_SHAPES, ids=[case[0] for case in SHIPPED_CONTROLS_SHAPES])
def test_v48_a_shipped_threat_model_gives_each_finding_the_layer_that_its_own_scorer_wrote(renderer, rrs, tmp_path, example, unlisted):
    """The renderer's own readers (``_read_reference`` and ``_overlay_reference``) over a copy of the example's ``threats.md``, in ``tmp_path`` and read-only:
    nothing under ``examples/`` is touched. The layers are those of the example's own ``risk-scores.sarif``, which v4.48.4's scorer read from the same rows."""
    copy = tmp_path / "threats.md"
    copy.write_bytes((REPO_ROOT / "examples" / example / "threats.md").read_bytes())
    copy.chmod(0o444)
    run = renderer.Run()
    run.threats_text, run.threats_path = copy.read_text(encoding="utf-8"), "threats.md"
    reference = renderer._read_reference(run, "kept")
    assert reference is not None, "premise: the example's Section 7 reads"
    members = [{"id": row["id"], "canon": canon(row["id"]), "component": "Unspecified", "threat": "", "layer": ""} for row in reference["open"]]
    renderer._overlay_reference(run, members, reference)
    shipped = rrs.shipped_layers(example)
    assert members and [member["canon"] for member in members if member["canon"] not in shipped] == []
    for member in members:
        assert member["layer"] == ("Unclassified" if member["canon"] in unlisted else shipped[member["canon"]]), member["id"]
    assert len({member["layer"] for member in members} - {"Unclassified"}) >= 2, "layers were read, so the check is not vacuous"


def test_layer_under_the_fallback_a_member_takes_its_own_layer_and_a_blank_or_missing_one_is_unclassified(stage, renderer, tmp_path):
    """sarif-result.md, gap B: "under D8's fallback, the member's ``details.layer`` (P0-3), else ``Unclassified``". A layer that a result lacks, one that
    is blank and one that is not text hold none (``parse_sarif_member_set``), and Section 2 shows the structured value where the agent agrees."""
    document = json.loads(sarif_input(FINDINGS))
    properties = {result["partialFingerprints"]["findingId/v1"]: result["properties"] for result in document["runs"][0]["results"]}
    del properties["E-5"]["maestro-layer"]
    properties["R-1"]["maestro-layer"] = "   "
    properties["T-4"]["maestro-layer"] = 7
    lost = ("E-5", "R-1", "T-4")
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, json.dumps(document))
    res = project.run(mutate=together(with_cells(S2_ID, {"MAESTRO Layer": ODD_LAYER}), *[with_cells(i, {"MAESTRO Layer": "Unclassified"}) for i in lost]))
    assert_done_with_warnings(res, project)
    results, rows = results_by_id(project.sarif), matrix_rows(project.md)
    for item in FINDINGS:
        wanted = "Unclassified" if item["id"] in lost else ODD_LAYER if item["id"] == S2_ID else COMPONENTS[item["component"]][1]
        assert results[item["id"]]["properties"]["maestro-layer"] == wanted, item["id"]
        assert rows[canon(item["id"])][1]["MAESTRO Layer"] == wanted, item["id"]
        assert not row_check_flags(results[item["id"]]["properties"]["integrity-flags"]), "the agent agrees, so nothing is flagged: %s" % item["id"]


UNREADABLE = [  # (name, the scored input's source_file, or None for a null one)
    ("source-file-is-null", None),
    ("source-file-is-outside-the-working-directory", "../elsewhere/threats.md"),
    ("source-file-names-a-file-that-is-not-there", "run/gone/threats.md"),
]


@pytest.mark.parametrize("name,source", UNREADABLE, ids=[case[0] for case in UNREADABLE])
def test_layer_with_no_readable_threat_model_every_layer_is_unclassified_nothing_is_correlated_and_the_record_says_why(stage, renderer, tmp_path, name, source):
    """sarif-result.md, gap B: "with no readable ``threats.md``, it is ``Unclassified``, under the stage record's reason for that file". The reason
    names the layers, since that is what the reader loses (and the correlation). No key changes: the hash and ``findingId/v1`` are over the finding's
    ID alone, so they equal the ones of the run that did read the threat model."""
    with_model = Project(stage, renderer, tmp_path / "with", groups=GROUPS)
    assert with_model.run().code in (0, 5)
    kept = {canon(finding_id): result for finding_id, result in results_by_id(with_model.sarif).items()}
    assert kept["S-2"]["properties"]["correlation-group"] == "CG-1", "the control: with the threat model, the group is written"
    scored = make_risk_scores_md().replace('source_file: "run/threats.md"', "source_file: null") if source is None else make_risk_scores_md(source=source)
    without = Project(stage, renderer, tmp_path / "without", groups=GROUPS, risk_scores_text=scored)
    res = without.run(mutate=every_item(layers_unclassified))
    assert_done_with_warnings(res, without)
    results = results_by_id(without.sarif)
    assert sorted(canon(finding_id) for finding_id in results) == sorted(kept)
    for finding_id, result in results.items():
        assert result["properties"]["maestro-layer"] == "Unclassified", finding_id
        assert not [key for key in result["properties"] if key.startswith("correlation-")], finding_id
        assert "Correlated in" not in result["message"]["text"], finding_id
        assert result["partialFingerprints"]["primaryLocationLineHash"] == kept[canon(finding_id)]["partialFingerprints"]["primaryLocationLineHash"], "no key changes"
    unreadable = [warning for warning in without.record["warnings"] if warning["code"] == "threats-unreadable"]  # reading: the code
    assert len(unreadable) == 1, without.record["warnings"]
    assert "layer" in unreadable[0]["detail"].lower(), "the reason names the layers: " + unreadable[0]["detail"]
    if source is not None:
        reason = rules.check_run_file(source, cwd=Path(without.root), expected_name="threats.md").reason
        assert reason and reason in unreadable[0]["detail"], "and the check's own reason for the file: " + unreadable[0]["detail"]


# =============================================================================
# 18. What T053's and T059's goldens left out (lane R2's proposals, reviewed and adapted by T056's third instance)
# =============================================================================
#
# The SARIF as the contract and the 1.1 template show it, D8's fallback member by member, the from-disk checks' seeded bugs, the ``ref``
# slot, an evidence file at its edges (encoded, refused by the resolver, removed between runs), the logical location's defaults, a
# forbidden character in the zone and in a fallback member's mitigation, and a mention of a RESOLVED ID in text that the renderer copies.
# The proposals that are not here, and why, are in the results file: a body's grammar belongs to ``test_tachi_parts.py`` (section 23), the
# rule table and the taxonomy map to ``test_sarif_identity.py`` (section 20), and the 3.9 floor to ``test_runtime_floor_374.py``.


@pytest.fixture(scope="module")
def grouped(stage, renderer, tmp_path_factory):
    """One clean render of the eleven findings with Section 4a's group CG-1 (S-2 its primary, S-10 its peer), shared by the read-only goldens below."""
    project = Project(stage, renderer, tmp_path_factory.mktemp("grouped"), groups=GROUPS)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    return project


# --------------------------------------------------------------------------- the SARIF as the contract and the template show it

def test_sarif_the_driver_carries_the_release_version_in_both_version_fields(base):
    """sarif-result.md (ruled at W3): in the scorer and controls files ``semanticVersion`` and ``version`` both carry tachi's release version, the stamp's."""
    driver = base.sarif["runs"][0]["tool"]["driver"]
    assert driver["version"] == driver["semanticVersion"] == tp.VERSION


def test_sarif_the_carry_flag_is_a_json_boolean_and_the_flags_are_an_array(base):
    """``False == 0`` in Python, so ``test_sarif_each_result_carries_its_goldens`` can't tell a ``0`` from the ``false`` that the template shows."""
    for result in base.sarif["runs"][0]["results"]:
        assert type(result["properties"]["control-carry-forward"]) is bool and isinstance(result["properties"]["integrity-flags"], list)
    assert '"control-carry-forward": false' in base.sarif_text and '"integrity-flags": []' in base.sarif_text


def test_template_the_run_block_and_the_drivers_keys_are_the_templates_in_its_order(base):
    """The run as the 1.1 template shows it: the document's, the run's and the driver's keys in the template's order, the taxa, the stamp's keys,
    the schema and the version."""
    require_the_1_1_template()
    template = json.loads(template_text(SARIF))
    shown, run, wanted_run = base.sarif, base.sarif["runs"][0], template["runs"][0]
    assert shown["$schema"] == template["$schema"] and shown["version"] == template["version"]
    assert list(run) == list(wanted_run), "``properties`` follows ``results``"
    assert list(run["tool"]["driver"]) == list(wanted_run["tool"]["driver"])
    assert run["tool"]["driver"]["supportedTaxonomies"] == wanted_run["tool"]["driver"]["supportedTaxonomies"] and run["taxonomies"] == wanted_run["taxonomies"]
    assert list(run["properties"]["tachi_provenance"]) == list(wanted_run["properties"]["tachi_provenance"])


def test_template_a_group_members_correlation_keys_follow_the_templates_properties(grouped):
    """A group member's three correlation keys come after the template's last property, and a result outside a group has none."""
    require_the_1_1_template()
    order = list(json.loads(template_text(SARIF))["runs"][0]["results"][0]["properties"])
    results = results_by_id(grouped.sarif)
    assert {finding_id for finding_id, result in results.items() if "correlation-group" in result["properties"]} == {"S-2", "S-10"}
    for finding_id, result in results.items():
        assert list(result["properties"]) == order + (list(sc.CORRELATION_KEYS) if finding_id in ("S-2", "S-10") else []), finding_id


# --------------------------------------------------------------------------- a finding with no row in the threat model, and a bad Section 4a row

def test_sarif_a_scored_finding_with_no_open_row_in_the_threat_model_has_an_empty_markdown_and_the_components_layer(stage, renderer, tmp_path):
    """A finding that the scored input lists and the threat model has no open row for keeps its component, threat and layer from the scored input
    and the component's Section 1 layer (gap B: the chain's third step), has an empty ``message.markdown`` (P0-8: the key stays), and is listed
    under Input Issues."""
    project = Project(stage, renderer, tmp_path)
    kept = [line for line in project.threats.read_text(encoding="utf-8").split("\n") if not line.startswith("| T-1 |")]
    project.threats.write_text("\n".join(kept), encoding="utf-8")
    res = project.run()
    assert res.code in (0, 5), res.describe()
    result = results_by_id(project.sarif)["T-1"]
    assert result["message"]["markdown"] == "" and result["properties"]["maestro-layer"] == COMPONENTS["auth-broker"][1]
    assert any(re.search(id_pattern("T-1"), line) for line in integrity_text(project.md).split("\n")), "Input Issues lists the finding"


def test_corr_a_malformed_section_4a_row_is_an_input_issue_and_the_other_groups_stand(stage, renderer, tmp_path):
    """D8: a Section 4a row that can't be read is listed under Input Issues and skipped, and the group of another row stands. Two rows here have
    two cells, and the third is the project's own group."""
    project = Project(stage, renderer, tmp_path, groups=GROUPS)
    text = project.threats.read_text(encoding="utf-8").replace("| CG-1 |", "| CG-1 | S-2, S-10 |\n| not-a-group | S-2, T-1 |\n| CG-1 |", 1)
    assert "not-a-group" in text
    project.threats.write_text(text, encoding="utf-8")
    res = project.run()
    assert res.code in (0, 5), res.describe()
    issues = [line for line in integrity_text(project.md).split("\n") if "4a" in line]
    assert len(issues) == 2, integrity_text(project.md)
    results = results_by_id(project.sarif)
    assert [results[finding_id]["properties"]["correlation-group"] for finding_id in ("S-2", "S-10")] == ["CG-1", "CG-1"]
    assert not [key for key in results["T-1"]["properties"] if key.startswith("correlation-")] and "not-a-group" not in project.sarif_text


REPEATED_GROUPS = GROUPS + [("CG-2", ["S-10", "T-1"])]   # S-10 is in both: CG-1 claims it, and CG-2 is left with T-1 alone and falls away


def test_corr_an_id_that_two_groups_list_stays_in_the_first_and_is_listed_warned_and_counted(stage, renderer, tmp_path):
    """PM W4 ruling R-F: D8's claim rule is unchanged (S-10 is CG-1's peer, and T-1 is in no group), and the run says so. Input Issues (Section 7) has one
    line that names the ID and both groups, the stage record's warning ``correlation-member-repeated`` counts it, and the run exits 5. A project whose
    groups don't overlap has neither."""
    project = Project(stage, renderer, tmp_path / "repeated", groups=REPEATED_GROUPS)
    res = project.run()
    assert res.code == 5, res.describe()
    record = project.record
    assert record["status"] == "success-with-warnings"
    warnings = [warning for warning in record["warnings"] if warning["code"] == "correlation-member-repeated"]
    assert [warning["detail"] for warning in warnings] == ["Section 4a of threats.md lists 1 finding in more than one correlation group, and the first group "
                                                           "claims each: S-10"]
    issues = subsection_of(project.md, "## 7. Analysis Integrity", "### Input Issues")
    assert ("- Section 4a of threats.md: S-10 is listed in CG-1 and CG-2. CG-1 claims it, and CG-2 does not. "
            "CG-2 is left with fewer than two findings and emits no correlation.") in issues
    assert record["counts"]["parse_errors"] == 1, "the stage record counts the issue"
    results = results_by_id(project.sarif)
    assert (results["S-10"]["properties"]["correlation-group"], results["S-10"]["properties"]["correlation-role"]) == ("CG-1", "peer")
    assert not [key for key in results["T-1"]["properties"] if key.startswith("correlation-")], "CG-2 fell away, so T-1 is in no group"
    clean = Project(stage, renderer, tmp_path / "clean", groups=GROUPS)
    assert clean.run().code in (0, 5)
    assert not [warning for warning in clean.record["warnings"] if warning["code"] == "correlation-member-repeated"]
    assert subsection_of(clean.md, "## 7. Analysis Integrity", "### Input Issues").strip() == "None." and clean.record["counts"]["parse_errors"] == 0


def test_corr_the_claiming_group_that_emits_nothing_is_named_in_the_issue_and_the_id_stays_uncorrelated(stage, renderer, tmp_path):
    """D8's literal reading: a group that falls away still claims its IDs. CG-1 lists S-2 and a finding that this run doesn't score, so it emits nothing, and
    S-2, which CG-2 lists too, is in no group. The Input Issue says so, which the files alone would not."""
    groups = [("CG-1", ["S-2", "S-99"]), ("CG-2", ["S-2", "S-10", "T-1"])]
    project = Project(stage, renderer, tmp_path, groups=groups)
    res = project.run()
    assert res.code == 5, res.describe()
    issues = subsection_of(project.md, "## 7. Analysis Integrity", "### Input Issues")
    assert ("- Section 4a of threats.md: S-2 is listed in CG-1 and CG-2. CG-1 claims it, and CG-2 does not. "
            "CG-1 emits no correlation either, so S-2 is in no group.") in issues
    results = results_by_id(project.sarif)
    assert not [key for key in results["S-2"]["properties"] if key.startswith("correlation-")], "S-2 is claimed by a group that emits nothing"
    assert [results[finding_id]["properties"]["correlation-group"] for finding_id in ("S-10", "T-1")] == ["CG-2", "CG-2"], "CG-2 keeps two findings"


# --------------------------------------------------------------------------- D8's fallback, member by member

def fallback_document():
    """``sarif_input`` with what a member can carry that the first fallback case leaves out: a named group (S-2 its primary and S-10 its peer, with
    the scorer's own sentence), ``reused-id`` in S-2's own flags, a zone and a DFD kind of their own, kinds that the renderer maps (a ``data-store`` is
    ``data``, any other word is a process), and a legacy group (T-4 names T-1 as its peer, and no group has an ID)."""
    document = json.loads(sarif_input(FINDINGS))
    results = {result["partialFingerprints"]["findingId/v1"]: result for result in document["runs"][0]["results"]}

    def place(finding_id):
        return results[finding_id]["locations"][0]["logicalLocations"][0]

    results["S-2"]["message"]["text"] += " Correlated in CG-1; peers S-10."
    results["S-10"]["message"]["text"] += " Correlated in CG-1; primary S-2."
    results["S-2"]["properties"].update({"correlation-group": "CG-1", "correlation-role": "primary", "correlation-primary": "S-2",
                                         "score-flags": ["reused-id:finding_id:baseline"]})
    results["S-10"]["properties"].update({"correlation-group": "CG-1", "correlation-role": "peer", "correlation-primary": "S-2"})
    place("S-2").update({"fullyQualifiedName": "Fallback Zone/edge-gateway", "kind": "data-store"})
    place("S-10")["kind"] = "external-entity"
    place("D-2")["kind"] = "database"
    del place("E-3")["kind"]
    results["T-4"]["relatedLocations"] = [{"id": 0, "message": {"text": "T-1: " + by_id("T-1")["threat"]}}]
    return document


def test_fallback_each_members_own_group_flag_kind_and_zone_are_kept_and_the_sentence_is_written_once(stage, renderer, tmp_path):
    """D8 and ruling C: under the fallback a group is the member's own (``correlation-*``), and the scorer's sentence that ends its text is replaced by this file's,
    never doubled; ``reused-id`` is carried from its own flags; and its DFD kind goes through the renderer's map (ruled at W3, question 7:
    ``external-entity``, ``process``, ``data`` and the generator's ``data-store``, which is ``data``; any other word or none is ``process``)."""
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, json.dumps(fallback_document()))
    res = project.run(mutate=with_cells(S2_ID, {"MAESTRO Layer": ODD_LAYER}))
    assert_done_with_warnings(res, project)
    results = results_by_id(project.sarif)
    primary, peer = results["S-2"], results["S-10"]
    assert primary["message"]["text"] == "%s [Control: found] Correlated in CG-1; peers S-10." % by_id("S-2")["threat"]
    assert peer["message"]["text"] == "%s [Control: found] Correlated in CG-1; primary S-2." % by_id("S-10")["threat"]
    assert [primary["properties"][key] for key in sc.CORRELATION_KEYS] == ["CG-1", "primary", "S-2"]
    assert [peer["properties"][key] for key in sc.CORRELATION_KEYS] == ["CG-1", "peer", "S-2"]
    assert "reused-id:finding_id:baseline" in primary["properties"]["integrity-flags"] and "reused-id:finding_id:baseline" not in peer["properties"]["integrity-flags"]
    kinds = {finding_id: result["locations"][0]["logicalLocations"][0]["kind"] for finding_id, result in results.items()}
    assert (kinds["S-2"], kinds["S-10"], kinds["D-2"], kinds["E-3"]) == ("data", "external-entity", "process", "process")
    assert primary["locations"][0]["logicalLocations"][0]["fullyQualifiedName"] == "Fallback Zone/edge-gateway"  # reading: the zone is the member's own


def test_fallback_a_group_with_no_id_correlates_nothing_and_is_counted(stage, renderer, tmp_path):
    """D8 (P0-3): an old scorer file's group has no ID, so the renderer has none to write. Its members carry no ``correlation-*`` property and no
    sentence, and the stage record warns ``correlation-group-unnamed`` with the count (ADR-050 D8, ruled at the P0 checkpoint)."""
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, json.dumps(fallback_document()))
    res = project.run(mutate=with_cells(S2_ID, {"MAESTRO Layer": ODD_LAYER}))
    assert_done_with_warnings(res, project)
    results = results_by_id(project.sarif)
    for finding_id in ("T-4", "T-1"):
        assert not [key for key in results[finding_id]["properties"] if key.startswith("correlation-")], finding_id
        assert "Correlated in" not in results[finding_id]["message"]["text"], finding_id
    unnamed = [warning for warning in project.record["warnings"] if warning["code"] == "correlation-group-unnamed"]
    assert len(unnamed) == 1 and re.search(r"\b1\b", unnamed[0]["detail"]) and re.search(r"\b2\b", unnamed[0]["detail"]), \
        "the warning counts the groups that have no ID (one) and the groups of the file (two): %s" % project.record["warnings"]


def test_fallback_a_member_that_names_its_component_in_the_singular_logical_location_has_it(stage, renderer, tmp_path):
    """ADR-050 D8, ruled at W3 (question 7a): an older scorer or controls SARIF puts a result's component in ``locations[0].logicalLocation``, an object, and
    two shipped scorer files do on every result. The fallback reads it as it reads the plural form, so the component is the member's and no row of Section 2
    is flagged for a component that the renderer lost. This guards the switch to the shared reader, which has to keep it."""
    document = json.loads(sarif_input(FINDINGS))
    for result in document["runs"][0]["results"]:
        place = result["locations"][0]
        place["logicalLocation"] = place.pop("logicalLocations")[0]
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, json.dumps(document))
    res = project.run(mutate=with_cells(S2_ID, {"MAESTRO Layer": ODD_LAYER}))  # the member's own layer, as in the other fallback cases
    assert_done_with_warnings(res, project)
    for item in FINDINGS:
        assert matrix_rows(project.md)[canon(item["id"])][1]["Component"] == item["component"], item["id"]
        assert results_by_id(project.sarif)[item["id"]]["locations"][0]["logicalLocations"][0]["name"] == item["component"], item["id"]
    assert not any(row_check_flags(found) for found in flags_of(project.sarif).values())


def test_fallback_a_run_over_the_scorers_own_sarif_gives_the_same_results_as_a_run_over_its_markdown(identity, rrs, entries, tmp_path):
    """D8's fallback end to end (AR-T2): the scorer's own ``risk-scores.sarif`` stands in for its ``risk-scores.md``, and every result says the same
    but its flags, which gain ``input:delta_status:not-in-form`` (that form has no status)."""
    project = identity.make_project(identity.CONTROLS_FILE, rrs, entries, tmp_path, groups=identity.FIRST_RUN_GROUPS)
    assert project.run().code in (0, 5)
    with_markdown = identity.results_by(project.sarif)
    (project.out / "risk-scores.md").unlink()
    project.prepare()
    res = project.render()
    assert res.code == 5, res.describe()
    codes = [warning["code"] for warning in project.record["warnings"]]
    assert "value-not-in-form" in codes and "correlation-group-unnamed" not in codes, codes  # every group of the scorer's own file has an ID; reading: the scorer's code
    from_sarif = identity.results_by(project.sarif)
    assert sorted(from_sarif) == sorted(with_markdown)
    for finding_id, result in from_sarif.items():
        wanted, got = copy.deepcopy(with_markdown[finding_id]), copy.deepcopy(result)
        for each in (wanted, got):
            each["properties"].pop("integrity-flags")
        assert got == wanted, finding_id
        assert "input:delta_status:not-in-form" in result["properties"]["integrity-flags"], finding_id


def test_fallback_the_scorers_sarif_is_refused_for_a_forbidden_character_in_a_members_mitigation(stage, renderer, tmp_path):
    """P0-4: the renderer takes each fallback member's ``message.markdown``, so it refuses a bidi control in one (exit 2), names the finding and
    never echoes the character."""
    document = json.loads(sarif_input(FINDINGS))
    document["runs"][0]["results"][0]["message"]["markdown"] = "a mitigation" + chr(0x202e)  # S-2's: the first result
    project = Project(stage, renderer, tmp_path)
    use_sarif(project, json.dumps(document))
    project.earlier()
    project.prepare()
    res = project.render()
    assert res.code == 2, res.describe()
    assert re.search(id_pattern(S2_ID), res.err) and chr(0x202e) not in res.err, res.describe()
    project.assert_earlier_outputs_untouched()


# --------------------------------------------------------------------------- the from-disk checks, seeded one bug at a time

def edit_rule(change):
    return json_edit(lambda document: change(document["runs"][0]["tool"]["driver"]["rules"]))


def swap_first_two(document):
    results = document["runs"][0]["results"]
    results[0], results[1] = results[1], results[0]


# Each seed is one renderer bug that only a check on the file read back from disk can see (ADR-050 D4, steps 5 and 6). Every staged text that
# differs from the rendered one fails the byte check, so a seed also has to be named by the check of its own: the message holds the word
# that the second column gives, which is the SARIF key or the thing that the check is about, never a sentence.
SARIF_SEEDS = [  # (name, a word that the message names, the seeded edit of the staged SARIF)
    ("a-forbidden-character", "U+202E", json_edit(lambda d: result_of(d, "T-4")["message"].__setitem__("markdown", "Pin TLS" + chr(0x202e) + " now."))),
    ("a-driver-version", "driver", json_edit(lambda d: d["runs"][0]["tool"]["driver"].__setitem__("version", "0.0.0"))),
    ("a-driver-information-uri", "driver", json_edit(lambda d: d["runs"][0]["tool"]["driver"].__setitem__("informationUri", "https://example.invalid/"))),
    ("a-stamp", "stamp", json_edit(lambda d: d["runs"][0]["properties"]["tachi_provenance"].__setitem__("version", "0.0.0"))),
    ("a-rule-severity", "rules", edit_rule(lambda rules: rules[0]["properties"].__setitem__("security-severity", "0.1"))),
    ("a-lost-rule", "rules", edit_rule(lambda rules: rules.pop(0))),
    ("a-rule-description", "rules", edit_rule(lambda rules: rules[0]["shortDescription"].__setitem__("text", "Other."))),
    ("a-level", "level", json_edit(lambda d: result_of(d, "S-2").__setitem__("level", "error"))),
    ("a-layer", "maestro-layer", json_edit(set_property("S-2", "maestro-layer", "L9 other"))),
    ("an-effort", "effort-estimate", json_edit(set_property("T-4", "effort-estimate", "High"))),
    ("a-carry-flag", "control-carry-forward", json_edit(set_property("S-2", "control-carry-forward", True))),
    ("evidence-text", "control-evidence", json_edit(set_property("S-2", "control-evidence", [{"file": "x", "line": 1, "snippet": "y"}]))),
    ("a-flag", "integrity-flags", json_edit(set_property("S-2", "integrity-flags", ["input:x:y"]))),
    ("an-inherent-score", "inherent-risk", json_edit(set_property("S-2", "inherent-risk", "1.0"))),
    ("a-related-location", "relatedLocations", json_edit(
        lambda d: result_of(d, "S-2")["relatedLocations"][0]["physicalLocation"]["artifactLocation"].__setitem__("uri", "elsewhere.py"))),
    ("a-broken-related-location", "relatedLocations", json_edit(lambda d: result_of(d, "S-2").__setitem__("relatedLocations", ["x"]))),
    ("results-out-of-order", "order", json_edit(swap_first_two)),
    ("a-result-that-is-not-an-object", "not an object", json_edit(lambda d: d["runs"][0]["results"].__setitem__(0, "x"))),
    ("a-result-with-no-fingerprint", "partialFingerprints", json_edit(lambda d: d["runs"][0]["results"][0].pop("partialFingerprints"))),
    ("not-a-document", "SARIF document", lambda text: "{}\n"),
    ("a-badly-shaped-run", "SARIF document", json_edit(lambda d: d["runs"][0].__setitem__("results", "none"))),
    ("a-different-text-than-rendered", "rendered", lambda text: text.replace("\n  ", "\n   ", 1)),
    ("a-correlation-primary-naming-a-resolved-finding", "T-3", json_edit(set_property("S-10", "correlation-primary", "T-3"))),
    ("a-finding-id-naming-a-resolved-finding", "T-3", json_edit(lambda d: result_of(d, "S-2")["partialFingerprints"].__setitem__("findingId/v1", "T-3"))),
]


@pytest.mark.parametrize("name,word,edit", SARIF_SEEDS, ids=[case[0] for case in SARIF_SEEDS])
def test_staged_a_seeded_sarif_bug_is_named_and_stops_the_run_before_any_canonical_file_is_replaced(stage, renderer, tmp_path, name, word, edit):
    """A defect in the staged SARIF is exit 4 (a parity check that fails), the message names what is wrong, and no canonical file is replaced
    (ADR-050 D4). The group lets a case seed a ``correlation-primary``; the last two name a RESOLVED finding where one is still refused (question 9)."""
    project = Project(stage, renderer, tmp_path, groups=GROUPS)
    project.earlier()
    project.prepare()
    with tampering_with_staged(SARIF, edit):
        res = project.render()
    assert res.code == 4, res.describe()
    assert_failure_message(res, project.plan_id)
    assert word.lower() in " ".join(res.err.split()).lower(), "the message names %r: %s" % (word, res.err[:500])
    project.assert_earlier_outputs_untouched()


SECTION_4_SEEDS = [  # (name, the seeded edit of the staged markdown): a block that is not the renderer's, in each of the ways that it fills
    ("the-group-of-a-block", first_line_edit("### Medium Risk Gaps", lambda line: "### Low Risk Gaps")),
    ("the-band-in-a-heading", first_line_edit("#### 1. T-4 ", lambda line: line.replace("Critical)", "High)"))),
    ("the-number-of-a-block", first_line_edit("#### 2. E-5 ", lambda line: line.replace("#### 2.", "#### 5."))),
    ("the-status-line", first_line_edit("**Current Status**: Partial Control", lambda line: "**Current Status**: Control Found")),
    ("a-lost-block", first_line_edit("#### 3. AGP-01 ", lambda line: "#### 3. XX-99 " + line.split(" ", 3)[3])),
]


@pytest.mark.parametrize("name,edit", SECTION_4_SEEDS, ids=[case[0] for case in SECTION_4_SEEDS])
def test_staged_a_section_4_that_is_not_the_renderers_stops_the_run_and_the_message_names_it(project, name, edit):
    """D2: Section 4's group, order, number, heading and status line are the renderer's, so the from-disk check finds a block that isn't."""
    project.earlier()
    project.prepare()
    with tampering_with_staged(MD, edit):
        res = project.render()
    assert res.code == 4, res.describe()
    assert_failure_message(res, project.plan_id)
    assert "section 4" in " ".join(res.err.split()).lower(), res.err[:500]
    project.assert_earlier_outputs_untouched()


@pytest.mark.parametrize("name,finding_id,change", [
    ("a-row-of-ten-cells", "S-2", lambda item: item.__setitem__("matrix_row", join_row(row_cells(item["matrix_row"])[:10]))),
    ("another-findings-id", "S-2", lambda item: item.__setitem__("matrix_row", item["matrix_row"].replace("| S-2 |", "| T-1 |", 1))),
    ("a-body-with-a-heading", "E-3", lambda item: item.__setitem__("recommendation_body", item["recommendation_body"] + "\n## Extra")),
])
def test_failure_a_part_that_breaks_the_structure_after_reconcile_is_still_refused_at_render(project, name, finding_id, change):
    """``read_part`` owns the row's and the body's structure (reading 7), and the renderer reads every part through it again. A part that was valid
    when ``reconcile`` read it and was damaged after is refused at render (exit 2), the message names its batch, and no earlier file is replaced."""
    project.earlier()
    project.prepare()
    path = Path(project.batch_input("B001")["part_path"])
    part = json.loads(path.read_text(encoding="utf-8"))
    for item in part["items"]:
        if canon(item["finding_id"]) == canon(finding_id):
            change(item)
    path.write_text(json.dumps(part), encoding="utf-8")
    res = project.render()
    assert res.code == 2, res.describe()
    assert_failure_message(res, project.plan_id)
    assert "B001" in res.err, "the message names the batch"
    project.assert_earlier_outputs_untouched()


# --------------------------------------------------------------------------- the ``ref`` slot

def test_narrative_a_ref_slot_names_only_the_findings_own_taxonomy_ids(stage, renderer, tmp_path):
    """ADR-050 D3's slot table: ``{{ref:ID}}`` must be one of the finding's own taxonomy IDs, "those in its reference cell, its rule's relationships in
    the renderer's rule table, and its MAESTRO layer". T-1 is a tampering finding on a Layer 6 component: A08 and CWE-345 are its rule's and L6 is
    its layer, so the coverage rationale is filled. CWE-287 is the spoofing rule's and L3 is not its layer, so those two fields take their fixed
    sentences and are flagged."""
    def mutate(part):
        for item in part["items"]:
            if canon(item["finding_id"]) == "T-1":
                assessment = item["evidence"][0]["assessment"]
                assessment["coverage"]["rationale"] = "The check covers {{ref:CWE-345}} and {{ref:A08}} of the tampering rule, in layer {{ref:L6}}."
                assessment["currency"]["rationale"] = "It does not touch {{ref:CWE-287}}, which the spoofing rule holds."
                assessment["configuration"]["rationale"] = "It does not reach {{ref:L3}} either."

    project = run_ok(stage, renderer, tmp_path, mutate)
    block = next(body for cat, heading, body in control_blocks(project.md) if "`src/validate/schema.py:17`" in body and slug(cat) == "input-validation")
    _header, rows = table_of(block, "Dimension")
    shown = {row[0]: row[2] for row in rows}
    assert shown["Coverage"] == "The check covers CWE-345 and A08 of the tampering rule, in layer L6."
    for dimension in ("currency", "configuration"):
        assert shown[dimension.capitalize()] == tp.FALLBACK_SENTENCES["evidence.assessment." + dimension], dimension
    assert flags_of(project.sarif)["T-1"] == ["input:evidence.assessment.configuration:narrative-fallback", "input:evidence.assessment.currency:narrative-fallback"]
    assert project.record["counts"]["narrative_fallbacks"] == 2


# --------------------------------------------------------------------------- the evidence file: its URI, and a file that the resolver refuses

def test_evidence_a_name_that_needs_encoding_is_a_uri_in_the_location_and_a_path_in_the_text(stage, renderer, tmp_path):
    """The related location's ``uri`` is percent-encoded (FR-E.2), and the message, ``control-evidence`` and Section 3 name the path as it is."""
    def mutate(part):
        for item in part["items"]:
            if canon(item["finding_id"]) == "S-2":
                item["evidence"][0]["file"] = "src/odd dir/a#b.py"

    project = Project(stage, renderer, tmp_path)
    odd = project.target / "src" / "odd dir" / "a#b.py"
    odd.parent.mkdir(parents=True)
    odd.write_text("# a synthetic module\n" * 60, encoding="utf-8")
    res = project.run(mutate=mutate)
    assert res.code in (0, 5), res.describe()
    result = results_by_id(project.sarif)[S2_ID]
    shown = result["relatedLocations"][0]
    assert shown["physicalLocation"]["artifactLocation"]["uri"] == "src/odd%20dir/a%23b.py"
    assert shown["message"]["text"].endswith("detected in src/odd dir/a#b.py")
    assert result["properties"]["control-evidence"][0]["file"] == "src/odd dir/a#b.py"
    assert "**Detected in**: `src/odd dir/a#b.py:42`" in project.md


def make_missing(path):
    path.unlink()


def make_a_link(path):
    path.unlink()
    path.symlink_to("session.py")  # a link to a sibling file: the resolver never follows one


def make_a_directory(path):
    path.unlink()
    path.mkdir()


REFUSED = [("a-missing-file", make_missing, "missing"), ("a-link", make_a_link, "symlink"), ("a-directory", make_a_directory, "not-a-regular-file")]


@pytest.mark.parametrize("name,make,check", REFUSED, ids=[case[0] for case in REFUSED])
def test_evidence_a_file_that_the_resolver_refuses_is_flagged_and_left_out_of_the_related_locations_and_the_run_finishes(stage, renderer, base, tmp_path, name, make, check):
    """ADR-050 D2 and ``part-files.md`` (ruled at W3, question 5): an evidence ``file`` that the resolver refuses at render time, whether it is missing,
    a link or not a regular file, is flagged and never refused, because a carried result's evidence is copied verbatim and a refusal would recur on every
    later run. ``tokens.py`` is the evidence of S-2 (its only entry) and S-10 (one of two). Each of the two findings is flagged ``input:evidence.file:unresolved``
    once, counted under ``counts.input``; the stage record warns ``evidence-file-unresolved`` (so exit 5); §7 names each failed entry and the resolver's check;
    ``relatedLocations`` leaves the entry out (S-2 has none left, so it has no key); and the judgment and every computed value are those of a resolved file."""
    project = Project(stage, renderer, tmp_path)
    make(project.target / "src" / "auth" / "tokens.py")
    with pytest.raises(sc.PathCheckError) as caught:
        sc.resolve_file("src/auth/tokens.py", root=str(project.target))
    assert caught.value.check == check, "the premise: the resolver's own name for it"
    project.earlier()
    res = project.run()
    assert res.code == 5, res.describe()
    assert project.record["status"] == "success-with-warnings"
    assert [warning["code"] for warning in project.record["warnings"]] == ["evidence-file-unresolved"], "the one warning, with the code that the architect ruled"
    assert all(re.search(id_pattern(finding_id), project.record["warnings"][0]["detail"]) for finding_id in ("S-2", "S-10")), project.record["warnings"]
    flags = flags_of(project.sarif)
    assert {finding_id: found for finding_id, found in flags.items() if found} == {"S-2": [UNRESOLVED_FLAG], "S-10": [UNRESOLVED_FLAG]}
    assert project.record["counts"]["input"] == 2 and overwrites(project.record) == 0
    results = results_by_id(project.sarif)
    assert "relatedLocations" not in results["S-2"], "the only entry is left out, so the result has no key"
    assert [shown["physicalLocation"]["artifactLocation"]["uri"] for shown in results["S-10"]["relatedLocations"]] == ["src/auth/session.py"]
    assert [entry["file"] for entry in results["S-10"]["properties"]["control-evidence"]] == ["src/auth/tokens.py", "src/auth/session.py"], "both entries stay in control-evidence"
    for finding_id in ("S-2", "S-10"):
        assert any(re.search(id_pattern(finding_id), line) and "src/auth/tokens.py" in line and check in line for line in integrity_text(project.md).split("\n")), \
            "Section 7 names the finding, the file and the resolver's check: %s" % finding_id
        assert any(re.search(id_pattern(finding_id), line) for line in warning_lines(project.md)), "Section 1's warnings name the finding"
    assert_same_as_clean(project, base, without_related=True)


def test_evidence_a_finding_whose_every_entry_is_refused_is_flagged_once_lists_each_entry_and_has_no_related_locations(stage, renderer, base, tmp_path):
    """Question 5: the flag is once for a finding "however many of its entries fail", and Section 7 names each failed entry. S-10 cites ``tokens.py``
    and ``session.py``, and both are gone: it has two failed entries and one flag, no ``relatedLocations`` key, and both entries still in ``control-evidence``."""
    project = Project(stage, renderer, tmp_path)
    for name in ("tokens.py", "session.py"):
        (project.target / "src" / "auth" / name).unlink()
    res = project.run()
    assert res.code == 5, res.describe()
    flags = flags_of(project.sarif)
    assert flags["S-10"] == [UNRESOLVED_FLAG] and flags["S-2"] == [UNRESOLVED_FLAG]
    assert project.record["counts"]["input"] == 2, "one flag for each of the two findings, not for each of the three entries"
    entries_listed = [line for line in integrity_text(project.md).split("\n") if re.search(id_pattern("S-10"), line)]
    assert [name for name in ("src/auth/tokens.py", "src/auth/session.py") if any(name in line for line in entries_listed)] == ["src/auth/tokens.py", "src/auth/session.py"], \
        "Section 7 names each failed entry of S-10: %s" % entries_listed
    result = results_by_id(project.sarif)["S-10"]
    assert "relatedLocations" not in result and [entry["file"] for entry in result["properties"]["control-evidence"]] == ["src/auth/tokens.py", "src/auth/session.py"]
    assert_same_as_clean(project, base, without_related=True)


def test_evidence_an_unresolved_file_is_shown_as_the_agent_wrote_it_and_a_resolved_one_in_its_canonical_spelling(stage, renderer, tmp_path):
    """``part-files.md`` (ruled at W3): an entry that the resolver refuses has no canonical spelling, so Section 3, ``control-evidence`` and Section 7
    show its ``file`` as written, escaped; a resolved one stays canonical in Section 3 and both SARIF places, and Section 7 keeps what was written."""
    def untidy(part):
        for item in part["items"]:
            if canon(item["finding_id"]) in ("S-2", "S-10"):
                item["evidence"][0]["file"] = "./src//auth/tokens.py"
            if canon(item["finding_id"]) == "S-10":
                item["evidence"][1]["file"] = "./src//auth/session.py"

    project = Project(stage, renderer, tmp_path)
    (project.target / "src" / "auth" / "tokens.py").unlink()
    res = project.run(mutate=untidy)
    assert res.code == 5, res.describe()
    assert "**Detected in**: `./src//auth/tokens.py:42`" in project.md and "**Detected in**: `src/auth/session.py:88`" in project.md
    results = results_by_id(project.sarif)
    assert [entry["file"] for entry in results["S-10"]["properties"]["control-evidence"]] == ["./src//auth/tokens.py", "src/auth/session.py"]
    assert results["S-2"]["properties"]["control-evidence"][0]["file"] == "./src//auth/tokens.py"
    assert [shown["physicalLocation"]["artifactLocation"]["uri"] for shown in results["S-10"]["relatedLocations"]] == ["src/auth/session.py"]
    assert [entry["file"] for entry in persisted(project.md)["S-10"]["evidence"]] == ["./src//auth/tokens.py", "./src//auth/session.py"], "Section 7 keeps what was written"


def test_evidence_a_carried_result_whose_file_was_removed_between_runs_renders_with_the_flag_and_not_an_exit(stage, renderer, tmp_path):
    """The case that decided question 5: run 1 is clean, and ``tokens.py`` is removed before run 2, whose agent copies every UNCHANGED result's evidence
    verbatim and scans nothing. The render finishes with exit 5: S-2 and S-10 are flagged and the stage record warns, every row is still carried, and
    the results are run 1's but for the flag and the entry that has no location."""
    first = run_ok(stage, renderer, tmp_path / "first")
    follow = follow_up(stage, renderer, tmp_path / "second", first)
    (follow.target / "src" / "auth" / "tokens.py").unlink()
    seen = carry_the_planners_rows(follow)
    assert sorted(seen, key=s2_key) == [canon(i) for i in S2_ORDER]
    res = follow.render()
    assert res.code == 5, res.describe()
    tp.validate_stage_record(follow.record)
    assert [warning["code"] for warning in follow.record["warnings"]] == ["evidence-file-unresolved"]
    flags = flags_of(follow.sarif)
    assert {finding_id: found for finding_id, found in flags.items() if found} == {"S-2": [UNRESOLVED_FLAG], "S-10": [UNRESOLVED_FLAG]}
    rows = matrix_rows(follow.md)
    assert {row["CF"] for _band, row in rows.values()} == {"CF"} and frontmatter_value(follow.md, "carry_forward_count") == str(len(FINDINGS))
    assert {result["properties"]["control-carry-forward"] for result in follow.sarif["runs"][0]["results"]} == {True}
    assert "relatedLocations" not in results_by_id(follow.sarif)["S-2"]
    assert_same_as_clean(follow, first, carried_differs=True, without_related=True)
    assert persisted(follow.md) == {key: dict(item, carried_forward=True, matrix_row=join_row([("CF" if name == "CF" else cell) for name, cell in zip(K8_HEADER, row_cells(item["matrix_row"]))]))
                                    for key, item in persisted(first.md).items()}, "Section 7 keeps what run 1 persisted, but for the carry"


# --------------------------------------------------------------------------- the logical location's defaults, and forbidden characters in names

def drop_table(text, heading):
    """``text`` without the ``###`` table that starts with ``heading`` (up to the next heading)."""
    out, skipping = [], False
    for line in text.split("\n"):
        if line.startswith("### "):
            skipping = line.startswith(heading)
            if skipping:
                continue
        elif line.startswith("## "):
            skipping = False
        if not skipping:
            out.append(line)
    return "\n".join(out)


@pytest.mark.parametrize("name", ["no-components-table", "no-trust-zones-table", "a-zone-that-lists-no-member-of-the-component"])
def test_sarif_a_component_that_the_threat_model_places_nowhere_is_a_process_in_the_application_zone(stage, renderer, tmp_path, name):
    """The logical location is read from ``threats.md`` as the scorer reads it: the kind from the component's Section 1 type, the zone from the Section 2 row
    that lists it. A component with no type is a ``process`` (the default of the scorer's map), and one with no zone is in ``Application Zone``."""
    project = Project(stage, renderer, tmp_path, groups=GROUPS)
    text = project.threats.read_text(encoding="utf-8")
    if name == "no-components-table":
        text = drop_table(text, "### Components")
    elif name == "no-trust-zones-table":
        text = drop_table(text, "### Trust Zones")
    else:
        text = text.replace("| Data Zone | Trusted | vector-store |", "| Data Zone | Trusted | |")
    assert text != project.threats.read_text(encoding="utf-8")
    project.threats.write_text(text, encoding="utf-8")
    res = project.run()
    assert res.code in (0, 5), res.describe()
    for finding_id, result in results_by_id(project.sarif).items():
        component = by_id(finding_id)["component"]
        logical = result["locations"][0]["logicalLocations"][0]
        placed = name != "no-trust-zones-table" and not (name.startswith("a-zone") and component == "vector-store")
        zone = next(zone_name for zone_name, _label, _level, members in ZONES if component in members) if placed else "Application Zone"
        kind = "process" if name == "no-components-table" else KIND_OF[COMPONENTS[component][0]]
        assert logical == {"name": component, "fullyQualifiedName": "%s/%s" % (zone, component), "kind": kind}, finding_id


def test_input_a_forbidden_character_in_a_zone_name_is_refused_and_not_echoed(stage, renderer, tmp_path):
    """P0-4: the zone name is taken from ``threats.md`` into every result's logical location, so a bidi control in it is refused at the point it is read
    (exit 2, naming the zone), and the character is never echoed."""
    project = Project(stage, renderer, tmp_path)
    text = project.threats.read_text(encoding="utf-8")
    assert "| Edge DMZ |" in text
    project.threats.write_text(text.replace("| Edge DMZ |", "| Edge" + chr(0x202e) + " DMZ |", 1), encoding="utf-8")
    project.earlier()
    res = project.run()
    assert res.code == 2, res.describe()
    assert "zone" in res.err.lower() and chr(0x202e) not in res.err, res.describe()
    project.assert_earlier_outputs_untouched()


# --------------------------------------------------------------------------- a RESOLVED ID in the text that the renderer copies

MENTIONS = [  # (name, what the part, the threat model or the target holds that names the RESOLVED finding T-3)
    ("a-snippet-comment", "S-2's snippet holds ``# mitigates T-3``"),
    ("an-evidence-path", "AG-1's first entry is the file ``docs/T-3.md``"),
    ("a-recommendation", "E-3's What to Implement names T-3"),
    ("a-threat-text", "R-1's threat text, which the reference set gives message.text, names T-3"),
    ("a-mitigation", "E-5's mitigation in the threat model, which is message.markdown, names T-3"),
]


@pytest.mark.parametrize("name,what", MENTIONS, ids=[case[0] for case in MENTIONS])
def test_resolved_a_mention_of_a_resolved_finding_in_text_the_renderer_copies_renders_cleanly(stage, renderer, tmp_path, name, what):
    """ADR-050 D8 and ``sarif-result.md`` (ruled at W3, question 9): the self-check's scan for a RESOLVED finding reads only the strings that a renderer
    composes or takes as a closed value, so an ID in copied text is a mention and not a reference: a snippet, an evidence path, the recommendation, the
    reference set's threat and mitigation. T-3 is RESOLVED in the project, the control analyzer copies an UNCHANGED finding's evidence verbatim, and an
    exit 4 here would recur on every baseline-aware run. The run is clean, and no result is written for T-3. (The two seeds that still fail with
    exit 4, a ``correlation-primary`` and a ``findingId/v1`` that name it, are among the SARIF seeds above.)"""
    findings = copy.deepcopy(FINDINGS)
    if name == "a-snippet-comment":
        by_id("S-2", findings)["evidence"][0]["snippet"] = "def verify_token(token):\n    # mitigates T-3\n    return check_signature(token)"
    elif name == "an-evidence-path":
        by_id("AG-1", findings)["evidence"][0]["file"] = "docs/T-3.md"
    elif name == "a-recommendation":
        by_id("E-3", findings)["rec"]["what"] = "Mirror the fix that was made for T-3 on the admin routes."
    elif name == "a-threat-text":
        by_id("R-1", findings)["threat"] = "Portal actions repeat the T-3 logging gap."
    project = Project(stage, renderer, tmp_path, findings=findings)
    if name == "a-mitigation":
        text = project.threats.read_text(encoding="utf-8")
        assert "Mitigation text for E-5." in text
        project.threats.write_text(text.replace("Mitigation text for E-5.", "Mitigation text for E-5, as for T-3."), encoding="utf-8")
    res = project.run()
    assert res.code == 0, res.describe()
    assert project.record["warnings"] == []
    results = results_by_id(project.sarif)
    assert sorted(results) == sorted(OPEN_IDS), "no result for T-3"
    assert "T-3" in project.sarif_text, "the mention is in the file: " + what


# --------------------------------------------------------------------------- T059's edges: the warning line, a row that is both, a carried row whose input moved

@pytest.mark.parametrize("count", [7, 11], ids=["seven-are-named-in-full", "eleven-are-ten-and-one-more"])
def test_r34_flag_section_1_names_at_most_ten_flagged_findings_and_counts_the_rest(stage, renderer, tmp_path, count):
    """ADR-050 D2, ruled at W3 (question 4, which answers T056's open question 4): Section 1's warning line for the cells that disagree is a list of finding
    IDs, so it names the first ten in S-2's order and counts the rest, as every list in a rendered markdown file does. Here ``count`` of the project's eleven
    findings have a Control Category cell that names no category, and each is flagged once."""
    ids = [item["id"] for item in sorted(FINDINGS, key=lambda each: s2_key(each["id"]))][:count]
    project = run_ok(stage, renderer, tmp_path, together(*[with_cells(finding_id, {"Control Category": "Biometrics"}) for finding_id in ids]))
    wanted = named_list(ids)
    assert len([line for line in warning_lines(project.md) if wanted in line]) == 1, (wanted, warning_lines(project.md))
    assert project.record["counts"]["input"] == count


def test_r34_flag_a_row_can_be_overwritten_and_flagged_at_once_and_the_two_are_counted_apart(stage, renderer, tmp_path):
    """One row, two computed cells that hold something else (overwritten, ``cell_overwrites``) and two checked cells that disagree (flagged, ``input``): the
    two counts are independent, neither raises the other's flag, and Section 2 shows the computed values in the first two and the agent's text in the others."""
    project = run_ok(stage, renderer, tmp_path, with_cells("T-4", {"Inherent Score": "1.0", "Residual Severity": "Low", "Component": "somewhere-else",
                                                                   "MAESTRO Layer": "L1 " + DASH + " Foundation Model"}))
    assert overwrites(project.record) == 2 and project.record["counts"]["input"] == 2
    flags = flags_of(project.sarif)
    assert flags["T-4"] == [FLAG_OF["Component"], FLAG_OF["MAESTRO Layer"]] and not [i for i, found in flags.items() if found and i != "T-4"]
    band, row = matrix_rows(project.md)["T-4"]
    assert (band, row["Inherent Score"], row["Residual Severity"], row["Component"], row["MAESTRO Layer"]) == (
        "High", "9.4", "High", "somewhere-else", "L1 " + DASH + " Foundation Model")


def test_r34_flag_a_carried_rows_layer_that_moved_in_the_input_is_flagged_and_the_sarif_follows_the_input(stage, renderer, tmp_path):
    """AR-T3: a carried row is "copied, read and checked", so a layer that moved in the threat model since run 1 disagrees with the cell that the agent copied.
    The three findings on ``auth-broker`` are each flagged once, Section 2 keeps the carried cell as written (ruled at W3, question 3), and the SARIF says the
    input's layer."""
    first = run_ok(stage, renderer, tmp_path / "first")
    follow = follow_up(stage, renderer, tmp_path / "second", first)
    old, new = "L6 " + DASH + " Security and Compliance", "L5 " + DASH + " Evaluation and Observability"
    text = follow.threats.read_text(encoding="utf-8")
    assert old in text
    follow.threats.write_text(text.replace(old, new), encoding="utf-8")
    run_carried(follow, first)
    on_broker = sorted((item["id"] for item in FINDINGS if item["component"] == "auth-broker"), key=s2_key)
    flags = flags_of(follow.sarif)
    assert sorted((finding_id for finding_id, found in flags.items() if found), key=s2_key) == on_broker
    results = results_by_id(follow.sarif)
    for finding_id in on_broker:
        assert flags[finding_id] == [FLAG_OF["MAESTRO Layer"]] and results[finding_id]["properties"]["maestro-layer"] == new, finding_id
        assert matrix_rows(follow.md)[canon(finding_id)][1]["MAESTRO Layer"] == old, "Section 2 keeps the carried cell"
    assert follow.record["counts"]["input"] == len(on_broker) and follow.record["counts"].get("cell_overwrites", 0) == 0


def score_flags_table(finding_id):
    return ("### Score Flags\n\n| ID | Flag | Field | Stored | Rendered | Cause |\n|----|------|-------|--------|----------|-------|\n"
            "| %s | reused-id | finding_id | %s | %s | baseline |\n" % (finding_id, finding_id, DASH))


def test_input_a_fenced_score_flags_table_in_the_scored_input_is_not_read(stage, renderer, tmp_path):
    """The read of the scored input's Score Flags finds the heading outside code, as every reader of a section does (ADR-050 D3, "Finding a section"). The
    scorer's file holds no fence, so a fenced table there is a quotation: it names T-1, and the real table after it names S-2."""
    text = make_risk_scores_md()
    marker = "---\n\n## 3. Dimensional Breakdown"
    assert marker in text
    quoted = "\n```\n" + score_flags_table("T-1") + "```\n\n"
    text = text.replace(marker, quoted + marker, 1) + "\n## 6. Score Integrity\n\n" + score_flags_table("S-2") + "\n"
    project = Project(stage, renderer, tmp_path, risk_scores_text=text)
    res = project.run()
    assert res.code in (0, 5), res.describe()
    flags = flags_of(project.sarif)
    assert flags["S-2"] == ["reused-id:finding_id:baseline"] and flags["T-1"] == [], flags


ACCEPTED_FORMS = [  # E-3 is a missing finding whose Effort is "Low": each is a body that the part validator accepts (test_tachi_parts.py, section 23)
    ("indented-key-lines", lambda body: "\n".join("   " + line if line else line for line in body.split("\n"))),
    ("a-hyphenated-effort", lambda body: body.replace("**Effort Estimate**: Low", "**Effort Estimate**: Low-effort")),
    ("no-space-after-the-colon", lambda body: body.replace("**Effort Estimate**: ", "**Effort Estimate**:")),
    ("a-preamble-line", lambda body: "A first line of its own.\n" + body),
    ("a-line-after-the-effort", lambda body: body + "\nand one more line"),
]


@pytest.mark.parametrize("name,change", ACCEPTED_FORMS, ids=[case[0] for case in ACCEPTED_FORMS])
def test_r34_section_4_a_body_form_that_the_validator_accepts_is_rendered_and_read_the_same_by_both_files(stage, renderer, tmp_path, name, change):
    """``test_tachi_parts.py`` owns the body's grammar (its section 23); this case owns what follows an accepted form. Section 4 holds the block, the SARIF's
    ``effort-estimate`` is the Effort word, and its ``recommendation`` is what the shipped reader returns for the rendered block, whatever that is."""
    project = run_ok(stage, renderer, tmp_path, edit_item("E-3", lambda item: item.__setitem__("recommendation_body", change(item["recommendation_body"]))))
    assert canon("E-3") in recommendation_blocks(project.md)
    properties = results_by_id(project.sarif)["E-3"]["properties"]
    assert properties["effort-estimate"] == "Low" and properties["recommendation"] == read_findings(project.md)[canon("E-3")]["recommendation"]
    assert_nothing_counted(project.record)
