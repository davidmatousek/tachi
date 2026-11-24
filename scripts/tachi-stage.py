#!/usr/bin/env python3
"""Plan, reconcile and fail a batched stage: the one script that owns batching and resume (F-374).

A stage that has more units than one agent can write in one response is split into batches. A fresh
plan holds the batches, each with a batch input an agent reads and a part path it writes. The command
dispatches what the plan lists, and this script works out from the files on disk what is done and what
isn't, never from an agent's reply (ADR-050 D3, D4, D6; ``contracts/cli.md``).

    python3 scripts/tachi-stage.py --version
    python3 scripts/tachi-stage.py plan      --stage risk-score --out DIR --date YYYY-MM-DD --threats FILE [...]
    python3 scripts/tachi-stage.py plan      --stage compensating-controls --out DIR --date YYYY-MM-DD --risk-scores FILE --target DIR [...]
    python3 scripts/tachi-stage.py reconcile --stage S --out DIR --plan ID --plan-digest HEX
    python3 scripts/tachi-stage.py fail      --stage S --out DIR --plan ID --plan-digest HEX --reason R [--detail TEXT]
    python3 scripts/tachi-stage.py architecture-source --threats FILE --architecture PATH

Each command prints one JSON object on stdout and errors on stderr, in D4's four-line form (``TACHI <STAGE>
FAILED``, the batch or agent, ``Remedy:``, ``Kept for diagnosis:``). The exit codes are D4's:

    0 done           1 an input is missing or unreadable      2 a validation, usage or guard failure
    3 batches pending (``reconcile`` only)                    4 a cap or the retry budget is exhausted
    5 done, with a warning (``architecture-source`` only, here)

The scorer's plan sends the agent only the findings that need judgment (ADR-050 D2): the non-peers that are NEW or
UPDATED, or have no usable row in the baseline. The renderer inherits the rest, through the same
``tachi_scoring_rules.route_scorer_units``, so the planner and the renderer always agree. When ``threats.md`` is absent
the member set is read from the ``threats.sarif`` beside it (D8's fallback).

The controls plan sends the agent every scored open finding (ADR-050 D2, D8, D9), because the agent copies an UNCHANGED
result from its batch input. The units are the open rows of ``--risk-scores``, read through the tolerant reader that the
renderer reads that file with (``tachi_scoring_rules.read_baseline_scores``), or, when it is absent, the ``risk-scores.sarif``
beside it. Each row holds the finding's Section 7 values from the ``threats.md`` that the input's validated ``source_file``
names. An UNCHANGED finding's row also holds its baseline's persisted result (``evidence[]``, ``matrix_row``,
``recommendation_body`` and the judgment values, narrative text included), decoded, from the baseline's Section 7
``### Assessment Inputs`` through ``tachi_parsers.parse_controls_assessment_inputs``, never from the rendered file (AR-T3).

The plan holds the stage's pointers as ``refs`` (the authority, so a plan with no units keeps them), and each batch input
copies them for its agent. A ``--architecture`` candidate that the shared resolver refuses, whatever check fails, is left
out of ``refs`` and recorded as the plan's ``architecture_warning``, which the renderer's stage record lists first (D7).

The planner is also a function, :func:`plan_stage`. Batch sizes are constants in ``BATCH_SIZES``, not adopter
settings, so ``plan_stage``'s ``batch_size`` argument is the one way a test sets a smaller one (D6).

Everything the batch commands write sits under ``--out``, and every path under it is recomputed from ``--out``, the
stage and allow-listed IDs by ``tachi_parts``' layout builders, never read from a file, except the plan's
digest-checked ``inputs``. ``architecture-source`` is the one other writer: it edits the one ``--threats`` file in
place. Standard library only, and Python 3.9 syntax.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 9):  # the floor, checked before any other import (ADR-050 D4, S-11)
    sys.stderr.write("tachi-stage.py needs Python 3.9 or later (found %d.%d.%d)\n" % tuple(sys.version_info[:3]))
    sys.exit(2)

import argparse
import datetime
import json
import os
import platform
import re
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional

if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_write_confinement.py)
    sys.dont_write_bytecode = True  # no bytecode cache for the local imports below (ADR-049 D8)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sarif_common as sc  # noqa: E402
import tachi_parts as tp  # noqa: E402
import tachi_scoring_rules as rules  # noqa: E402
from tachi_parsers import (  # noqa: E402
    ReferenceSetError, parse_baseline_frontmatter, parse_controls_assessment_inputs, parse_correlation_groups, parse_reference_set,
    parse_sarif_member_set)

CONTROLS = "compensating-controls"

# ADR-050 D6, "Amended at W1": the output budget per stage in units per batch. A stage at or below its size
# plans one batch, so its agent runs once (NFR-4). `trees` is PR 2's stage, listed so the sizes live in one table.
BATCH_SIZES = {"risk-score": 13, CONTROLS: 11, "trees": 12}

# What an UNCHANGED controls unit's row takes from its baseline's persisted result (ADR-050 D2, AR-T3): the controls payload's
# keys that the agent copies as they stand. `carried_forward` is left out, because the agent sets it true when it copies.
CARRIED_KEYS = ("control_status", "control_category", "confidence", "evidence", "matrix_row", "recommendation_body")

WAVE_SIZE = 16          # S-8: at most 16 in flight per wave, which leaves margin under Claude Code's 20
MAX_ATTEMPT = 3         # P-8: the original and at most two retries per lineage
MAX_BATCHES = 999       # the batch ID is B followed by three digits

# --reason -> (what failed, the remedy). The first is the message's reason, and the second its `Remedy:` line.
REASONS = {
    "agent-not-spawned": (
        "a typed agent could not be spawned",
        "run scripts/install.sh to install the tachi agents and scripts, then re-run the command"),
    "unrecoverable-batch": (
        "a batch could not be completed within the retry caps",
        "re-run the command, and report the kept plan directory if the same batch fails again"),
    "check-failed": (
        "a completeness or parity check failed",
        "re-run the command; the earlier outputs were left or put back as they were"),
    "render-failed": (
        "the renderer failed",
        "re-run the command; the earlier outputs were left or put back as they were"),
}

_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.ASCII)
_HEX64 = re.compile(r"[0-9a-f]{64}", re.ASCII)


class StageError(Exception):
    """A stop with D4's exit code and its four-line message."""

    def __init__(self, code: int, stage: Optional[str], reason: str, remedy: str = "", batch: Optional[tuple] = None,
                 agent: Optional[str] = None, kept: Optional[str] = None) -> None:
        super().__init__(reason)
        self.code, self.stage, self.reason, self.remedy = code, stage, reason, remedy
        self.batch, self.agent, self.kept = batch, agent, kept

    def text(self) -> str:
        lines = ["TACHI %s FAILED: %s" % ((self.stage or "STAGE").upper(), self.reason)]
        if self.batch:
            lines.append("Batch %s: %s" % self.batch)
        if self.agent:
            lines.append("Agent: %s" % self.agent)
        if self.remedy:
            lines.append("Remedy: %s" % self.remedy)
        if self.kept:
            lines.append("Kept for diagnosis: %s" % self.kept)
        return "\n".join(lines)


# =============================================================================
# Small helpers: time, documents, arguments
# =============================================================================

def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(obj: Any) -> str:
    """Stable JSON: sorted keys, two-space indent, ASCII escapes, one trailing newline."""
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def _write_document(stage: str, path: str, obj: Dict[str, Any], schema: str, validator: Any) -> str:
    """Write one planner or record document, only if it passes its own validator and its size cap. Returns its text.

    The validator is the reader's: a writer that produced a document its readers refuse would end the stage later,
    far from the cause. A writer never writes a document over its cap (ruled at W1).
    """
    try:
        validator(obj)
    except tp.PartError as exc:
        raise StageError(2, stage, "a %s this step wrote fails its own contract (%s)" % (schema, exc.detail),
                         "report this as a bug in tachi-stage.py") from None
    text = _dump(obj)
    if len(text) > tp.MAX_DOCUMENT_BYTES[schema]:
        raise StageError(2, stage, "a %s would be %d bytes, over its cap of %d" % (schema, len(text), tp.MAX_DOCUMENT_BYTES[schema]),
                         "reduce the input (fewer or shorter findings) and re-run")
    tp.atomic_write(path, text)
    return text


def _out_dir(stage: str, out: Any, missing_code: int = 1) -> str:
    """``--out`` as an absolute path that every document can carry, and that is a directory (``missing_code`` if not)."""
    text = os.path.abspath(os.fspath(out))
    problem = tp.path_problem(text, allow_absolute=True)
    if problem is not None:
        raise StageError(2, stage, "--out is not an acceptable path (%s)" % problem,
                         "use a directory whose path has no backslash, backtick or control character")
    if not os.path.isdir(text):
        raise StageError(missing_code, stage, "--out %s is not a directory" % text, "create it or correct --out")
    return text


def _plan_arguments(stage: str, plan_id: str, digest: str) -> None:
    """D3: IDs and digests pass their allow-lists, as ASCII full matches, before they become paths."""
    if not tp.id_matches("plan", plan_id):
        raise StageError(2, stage, "--plan is not a plan ID", "pass the plan ID that plan printed")
    if not isinstance(digest, str) or _HEX64.fullmatch(digest) is None:
        raise StageError(2, stage, "--plan-digest is not a SHA-256 in lowercase hex", "pass the digest that the last plan or reconcile printed")


def _digest_or_none(path: str, out: Optional[str] = None) -> Optional[str]:
    """A file's digest, or None when it is missing, unreadable, or (given ``out``) fails the path guard."""
    if out is not None and tp.path_guard_problem(path, out) is not None:
        return None
    try:
        return tp.file_digest(path)
    except OSError:
        return None


def _waves(out: str, stage: str, plan_id: str, entries: List[Dict[str, Any]]) -> List[List[Dict[str, str]]]:
    flat = [{"batch_id": e["batch_id"], "input_path": tp.input_path(out, stage, plan_id, e["batch_id"])} for e in entries]
    return [flat[start:start + WAVE_SIZE] for start in range(0, len(flat), WAVE_SIZE)]


# =============================================================================
# plan
# =============================================================================

def _read_threats(stage: str, path: str, remedy: str = "regenerate threats.md with /tachi.threat-model") -> tuple:
    """The bytes and text of ``threats.md`` (or of another input, with its own ``remedy``): at most 16 MiB (D3 step 2) and strict UTF-8."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read(tp.MAX_AGENT_INPUT_BYTES + 1)
    except OSError as exc:
        raise StageError(1, stage, "cannot read %s (%s)" % (path, exc.strerror or "error"), "check the path and re-run") from None
    if len(raw) > tp.MAX_AGENT_INPUT_BYTES:
        raise StageError(2, stage, "%s is over %d bytes" % (path, tp.MAX_AGENT_INPUT_BYTES), remedy)
    try:
        return raw, raw.decode("utf-8")
    except UnicodeDecodeError:
        raise StageError(2, stage, "%s is not strict UTF-8" % path, remedy) from None


def _unit_row(finding: Dict[str, Any]) -> Dict[str, Any]:
    """One unit row for a batch input: Section 7's row as verbatim data, with the canonical ID."""
    row = {"finding_id": tp.canonical_finding_id(finding["id"])}
    for key in ("component", "threat", "risk_level", "mitigation", "agentic_pattern", "delta_status"):
        if key in finding:
            row[key] = finding[key]
    return row


def _architecture_ref(stage: str, candidate: Any) -> tuple:
    """The architecture candidate through the shared resolver's first step (ADR-050 D7), as ``(path, warning)``.

    ``sarif_common.resolve_explicit`` is the step ``resolve_architecture`` runs first, so ``plan`` and the renderer
    agree on every check and on the warning's code and text, and ``architecture-source`` makes the same checks under
    the same code. The path is absolute and in its canonical spelling: a regular file below the working directory,
    with no symlink on the way, spelled as the volume spells it. So ``refs.architecture`` and the body line name one
    path. A candidate it refuses, whatever check fails (a control character, backslash or backtick included, which
    used to exit 2), is left out of ``refs``, so the agents never see it, and ``(None, warning)`` comes back for the
    plan to record as its ``architecture_warning`` (ruled at W2). Nothing here stops a run (D7). stderr gets one
    ``WARNING`` line that names the candidate, escaped and untruncated, and the failed check, which is the last part
    of the warning's code. The line is this step's own: the warning's detail shortens the candidate to 80 characters.
    """
    given = os.fspath(candidate) if isinstance(candidate, os.PathLike) else candidate  # as typed, so a `..` or a link is refused as `architecture-source` refuses it
    root = os.getcwd()
    resolved, warning = sc.resolve_explicit(given, root=root)
    if resolved is None:
        check = warning["code"].rpartition(":")[2]  # a refusal always comes with its warning
        sys.stderr.write("WARNING: the architecture path %r is not used (%s), so it is not passed to the agents\n" % (given, check))
        return None, warning
    path = os.path.join(root, resolved.path)
    problem = tp.path_problem(path, allow_absolute=True)  # the working directory itself can hold a character a document can't carry
    if problem is not None:
        raise StageError(2, stage, "--architecture resolves to a path that documents cannot carry (%s)" % problem,
                         "run from a directory whose path has no backslash, backtick or control character")
    return path, None


def _pointer_refs(stage: str, risk_scores: Any, baseline_dir: Any, architecture: Any, target: Any) -> tuple:
    """The optional ``--risk-scores``, ``--baseline-dir``, ``--architecture`` and ``--target`` pointers.

    Each becomes an absolute path under its closed ``refs`` name, and a file that the stage reads also becomes a
    digest-checked input, so a change during the run is caught. The architecture goes through the shared resolver
    (``_architecture_ref``) and needs no syntactic pre-check: a candidate it refuses is dropped with a warning, which
    the plan records, because a stage never stops for it (ADR-050 D7). ``--baseline-dir`` is only checked here: it
    may name a run directory or a file in one (D9), and each stage's routing resolves it. The controls stage passes
    ``risk_scores=None``, because it reads that input itself (``_controls_scored_input``). It returns
    ``(inputs, refs, baseline, architecture_warning)``, where ``baseline`` is that checked path or ``None``.
    """
    inputs: Dict[str, Dict[str, Any]] = {}
    refs: Dict[str, str] = {}
    baseline: Optional[str] = None
    architecture_warning: Optional[Dict[str, str]] = None
    for name, given, kind in (("risk_scores", risk_scores, "file"), ("baseline_dir", baseline_dir, "baseline"),
                              ("architecture", architecture, "candidate"), ("target", target, "dir")):
        if given is None:
            continue
        if kind == "candidate":
            resolved, architecture_warning = _architecture_ref(stage, given)
            if resolved is not None:
                refs[name] = resolved
            continue
        path = os.path.abspath(os.fspath(given))
        problem = tp.path_problem(path, allow_absolute=True)
        if problem is not None:
            raise StageError(2, stage, "--%s is not an acceptable path (%s)" % (name.replace("_", "-"), problem),
                             "use a path with no backslash, backtick or control character")
        if kind == "baseline":
            if not os.path.exists(path):
                raise StageError(1, stage, "--baseline-dir %s names nothing" % path, "check the path and re-run")
            baseline = path
            continue
        if not (os.path.isfile(path) if kind == "file" else os.path.isdir(path)):
            raise StageError(1, stage, "--%s %s is not a %s" % (name.replace("_", "-"), path, "file" if kind == "file" else "directory"),
                             "check the path and re-run")
        refs[name] = path
        if kind == "file":
            inputs[name] = _input_entry(stage, path)
    return inputs, refs, baseline, architecture_warning


def _input_entry(stage: str, path: str, raw: Optional[bytes] = None) -> Dict[str, Any]:
    if raw is None:
        try:
            with open(path, "rb") as handle:
                raw = handle.read()
        except OSError as exc:
            raise StageError(1, stage, "cannot read %s (%s)" % (path, exc.strerror or "error"), "check the path and re-run") from None
    return {"path": os.path.abspath(path), "sha256": tp.sha256_hex(raw), "bytes": len(raw)}


def _walk(out: str):
    """``(relative path, size, mtime_ns)`` for every file under ``out``, in a fixed order. Links to directories aren't followed."""
    for directory, subdirs, files in os.walk(out):
        subdirs.sort()
        for name in sorted(files):
            path = os.path.join(directory, name)
            try:
                status = os.lstat(path)
            except OSError:  # pragma: no cover  (a file removed while the walk runs)
                continue
            yield os.path.relpath(path, out).replace(os.sep, "/"), status.st_size, max(0, status.st_mtime_ns)


def _snapshot(out: str) -> Optional[Dict[str, List[int]]]:
    """D4's ``{out}`` snapshot: each path with its size and ``mtime_ns``. None above 20,000 entries or for a name the
    plan can't record, and the declared-paths check is then skipped with a warning."""
    entries: Dict[str, List[int]] = {}
    for relpath, size, mtime in _walk(out):
        if len(entries) >= tp.MAX_SNAPSHOT_ENTRIES or tp.path_problem(relpath) is not None:
            sys.stderr.write("WARNING: the {out} snapshot is skipped, so the declared-paths check is too "
                             "(more than %d files, or a name that can't be recorded)\n" % tp.MAX_SNAPSHOT_ENTRIES)
            return None
        entries[relpath] = [size, mtime]
    return entries


def _take_preimages(stage: str, out: str, plan_id: str) -> Dict[str, Optional[str]]:
    """Copy each existing canonical output of the stage into ``preimage/`` and record its digest (D4).

    A name that holds no regular file records null: ``fail`` then puts nothing back.
    """
    preimage: Dict[str, Optional[str]] = {}
    for name in tp.CANONICAL_OUTPUTS[stage]:
        path = os.path.join(out, name)
        try:
            is_regular = stat.S_ISREG(os.lstat(path).st_mode)
        except OSError:
            is_regular = False
        if not is_regular:
            preimage[name] = None
            continue
        with open(path, "rb") as handle:
            data = handle.read()
        tp.atomic_write(tp.preimage_path(out, stage, plan_id, name), data)
        preimage[name] = tp.sha256_hex(data)
    return preimage


def _prepare_directories(stage: str, out: str, plan_id: str) -> None:
    """Make ``.tachi-build/<stage>/<plan_id>/`` and its first three subdirectories, through no link (KB 24).

    ``.tachi-build`` and the stage directory are checked one by one, and the plan directory is new, so everything
    this step makes lies under ``--out`` by identity.
    """
    for directory in (os.path.join(out, tp.BUILD_DIR), tp.stage_dir(out, stage)):
        if os.path.islink(directory) or (os.path.lexists(directory) and not os.path.isdir(directory)):
            raise StageError(2, stage, "%s is a symbolic link or not a directory" % directory, "remove it and re-run")
        os.makedirs(directory, exist_ok=True)
    try:
        os.mkdir(tp.plan_dir(out, stage, plan_id))
        for name in ("inputs", "parts", "preimage"):
            os.mkdir(tp.plan_subdir(out, stage, plan_id, name))
    except OSError as exc:
        raise StageError(2, stage, "cannot make the plan directory (%s)" % (exc.strerror or "error"), "re-run the command") from None


def _write_batch_input(stage: str, out: str, plan: Dict[str, Any], entry: Dict[str, Any], units: List[Dict[str, Any]]) -> None:
    """Write a batch's input for its current attempt, and record its digest in the plan's entry.

    The input's ``refs`` and ``params`` are verbatim copies of the plan's: the plan is the authority, and the agent
    reads only its batch input (the dispatch prompt is fixed). A retry's input is written the same way, so it
    copies the plan's ``refs`` and not its parent's (ruled at W2).
    """
    body = {
        "schema": tp.BATCH_INPUT_SCHEMA, "plan_id": plan["plan_id"], "batch_id": entry["batch_id"], "stage": stage,
        "agent_type": plan["agent_type"], "finding_ids": list(entry["finding_ids"]), "attempt": entry["attempt"],
        "part_path": tp.part_path(out, stage, plan["plan_id"], entry["batch_id"], entry["attempt"]),
        "tree_paths": {}, "units": units, "refs": plan["refs"], "params": plan["params"],
    }
    text = _write_document(stage, tp.input_path(out, stage, plan["plan_id"], entry["batch_id"]), body,
                           tp.BATCH_INPUT_SCHEMA, tp.validate_batch_input)
    entry["input_sha256"] = tp.sha256_hex(text.encode("utf-8"))


def _read_member_set(stage: str, threats: Any, threats_path: str) -> tuple:
    """The open findings of the run, as ``(raw bytes, [(finding row, unit row)], threats.md text, path read, SARIF groups, lacking)``.

    They come from the reference set of ``threats.md`` (S-12). The scorer falls back to the ``threats.sarif`` beside it
    when ``threats.md`` is absent, read through ``parse_sarif_member_set`` (ADR-050 D8, AR-T2): its units name the
    finding only, and the agent reads the rest from ``refs.threats``. An empty extraction is an error, never a pass
    (KB 22), and it ends the run here, before anything is written or dispatched.

    ``lacking`` maps each canonical ID to the names of the values its form lacks (S-12(b)): the reference set's own
    map, or, for the SARIF fallback, ``{id: ["delta_status"]}`` for every member, since a SARIF result records no
    status. The routing derives each missing status from the baseline, and the renderer passes the same map (ruled at W2).
    """
    beside = os.path.join(os.path.dirname(threats_path), "threats.sarif")
    if not (stage == "risk-score" and os.path.basename(threats_path) == "threats.md"
            and not os.path.lexists(threats_path) and os.path.lexists(beside)):
        raw, text = _read_threats(stage, threats_path)
        try:
            reference = parse_reference_set(text, source=os.fspath(threats))
        except ReferenceSetError as exc:
            raise StageError(2, stage, "%s. Expected %s" % (exc.reason, exc.expected), exc.remedy) from None
        for canonical in reference["duplicates"]:
            sys.stderr.write("WARNING: %s lists %s more than once; the first row is used\n" % (threats_path, canonical))
        return raw, [(finding, _unit_row(finding)) for finding in reference["open"]], text, threats_path, [], reference["lacking"]
    sys.stderr.write("WARNING: %s is absent, so the findings are read from %s (the SARIF fallback)\n" % (threats_path, beside))
    raw, text = _read_threats(stage, beside)
    try:
        member_set = parse_sarif_member_set(text)
    except ValueError as exc:
        raise StageError(2, stage, "%s: %s" % (beside, str(exc)[:200]), "restore threats.md, or regenerate it with /tachi.threat-model") from None
    members = sorted(member_set["members"], key=tp.finding_sort_key)
    return (raw, [({"id": member}, {"finding_id": member}) for member in members], None, beside, member_set["groups"],
            {member: ["delta_status"] for member in members})


def _scorer_routing(stage: str, members: list, text: Optional[str], sarif_groups: list, lacking: Dict[str, List[str]],
                    baseline_flag: Optional[str], extra_inputs: Dict[str, Dict[str, Any]], refs: Dict[str, str]) -> "rules.ScorerRouting":
    """Who the scorer agent scores (ADR-050 D2, D9): the baseline is resolved, read, and the units are partitioned.

    The baseline is the ``--baseline-dir`` pointer, else ``baseline.source`` of the input ``threats.md`` (R-6). A
    baseline that does not resolve, or whose ``risk-scores.md`` is missing or unreadable, means every finding is
    scored fresh, and a warning says why (S-12(d)): it never stops the run. A baseline in use is recorded as
    ``refs.baseline_dir`` and its files as digest-checked inputs, so the renderer routes against the same files.
    A finding whose form lacks ``delta_status`` takes its status from the baseline in ``route_scorer_units``, the one
    place that derives it: UNCHANGED, and carried, when the baseline has a usable open row for its ID, and NEW otherwise.
    """
    source = parse_baseline_frontmatter(text)["source"] if text is not None else None
    resolution = rules.resolve_baseline(flag=baseline_flag, baseline_source=source, cwd=Path(os.getcwd()))
    scores = None
    if resolution.run_dir is not None:
        refs["baseline_dir"] = os.fspath(resolution.run_dir)
        scored, sarif = resolution.files.get("risk-scores.md"), resolution.files.get("risk-scores.sarif")
        if scored is None:
            sys.stderr.write("WARNING: the baseline run directory has no usable risk-scores.md (%s), so every finding is scored fresh\n"
                             % resolution.file_reasons.get("risk-scores.md", "missing"))
        else:
            scores = rules.read_baseline_scores(scored, sarif_path=sarif)
            if scores.readable:
                extra_inputs["baseline_risk_scores"] = _input_entry(stage, os.fspath(scored))
                if sarif is not None and os.path.getsize(sarif) <= tp.MAX_AGENT_INPUT_BYTES:
                    extra_inputs["baseline_risk_scores_sarif"] = _input_entry(stage, os.fspath(sarif))
            else:
                sys.stderr.write("WARNING: the baseline risk-scores.md can't be read (%s), so it counts as missing: its owners, SLAs and "
                                 "dispositions are not carried, and every finding is scored fresh\n" % scores.reason)
    elif resolution.reason != "not-named":
        sys.stderr.write("WARNING: no baseline is used (%s: %s), so every finding is scored fresh\n" % (resolution.origin, resolution.reason))
    rows = [row for row, _ in members]
    groups = parse_correlation_groups(text, member_ids=[row["id"] for row in rows])["groups"] if text is not None else sarif_groups
    return rules.route_scorer_units(rows, groups=groups, baseline=scores, lacking=lacking)


# =============================================================================
# The controls stage's units (T036; ADR-050 D2, D8, D9)
# =============================================================================

# The two frontmatter forms the other readers accept (``tachi_parsers.parse_frontmatter``): plain, and inside a ``yaml`` fence.
_FRONTMATTER = (re.compile(r"\A---[ \t\r]*\n(.*?)\n---", re.DOTALL), re.compile(r"```yaml[ \t\r]*\n---[ \t\r]*\n(.*?)\n---[ \t\r]*\n```", re.DOTALL))
_SOURCE_FILE_LINE = re.compile(r"^source_file[ \t]*:[ \t]*(?P<value>.*)$")


def _scored_source_file(text: str) -> Optional[str]:
    """The ``source_file`` of a ``risk-scores.md``'s frontmatter, or ``None``: the threat model that was scored (D7, D8).

    The first top-level ``source_file`` line of the frontmatter counts. A quoted value loses its quotes, and ``null``, ``~``
    and an empty value mean none. What comes back is a candidate only: ``tachi_scoring_rules.check_run_file`` validates it.
    """
    text = text.lstrip("\ufeff")
    for pattern in _FRONTMATTER:
        found = pattern.search(text)
        if found is None:
            continue
        for line in found.group(1).split("\n"):
            match = _SOURCE_FILE_LINE.match(line.rstrip())
            if match is None:
                continue
            value = match.group("value").strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return None if value.strip() in ("", "null", "~") else value
        return None
    return None


def _same_file(first: Any, second: Any) -> bool:
    try:
        return os.path.samefile(os.fspath(first), os.fspath(second))
    except OSError:
        return False


def _id_list(finding_ids: List[str]) -> str:
    """A short list of IDs for a warning: the first five, and a count of the rest."""
    shown = ", ".join(finding_ids[:5])
    return shown + (" and %d more" % (len(finding_ids) - 5) if len(finding_ids) > 5 else "")


def _controls_scored_input(stage: str, given: Any) -> tuple:
    """The controls stage's input, as ``(path read, its bytes, the scored finding IDs in S-2 order, markdown text or None)``.

    The members are the open rows of ``risk-scores.md``, read through ``tachi_scoring_rules.read_baseline_scores``, the tolerant
    reader (R-26) that the renderer reads the file with, so the planner and the renderer see one set. Section 2a's RESOLVED rows
    are not in it (D8). When ``risk-scores.md`` is absent and a ``risk-scores.sarif`` lies beside it, that file is read
    instead, through ``parse_sarif_member_set`` (D8's fallback, AR-T2), and no markdown text comes back. An empty extraction,
    or an input that can't be read, is an error and ends the run here, before anything is written or dispatched (KB 22).
    """
    path = os.path.abspath(os.fspath(given))
    problem = tp.path_problem(path, allow_absolute=True)
    if problem is not None:
        raise StageError(2, stage, "--risk-scores is not an acceptable path (%s)" % problem, "use a path with no backslash, backtick or control character")
    remedy = "regenerate it with /tachi.risk-score"
    beside = os.path.join(os.path.dirname(path), "risk-scores.sarif")
    if os.path.basename(path) == "risk-scores.md" and not os.path.lexists(path) and os.path.lexists(beside):
        sys.stderr.write("WARNING: %s is absent, so the findings are read from %s (the SARIF fallback)\n" % (path, beside))
        raw, text = _read_threats(stage, beside, remedy)
        try:
            members = sorted(parse_sarif_member_set(text)["members"], key=tp.finding_sort_key)
        except ValueError as exc:
            raise StageError(2, stage, "%s: %s" % (beside, str(exc)[:200]), "restore risk-scores.md, or " + remedy) from None
        return beside, raw, members, None
    raw, text = _read_threats(stage, path, remedy)
    scores = rules.read_baseline_scores(Path(path))
    if not scores.rows:  # the reader opens through no link, so `missing` here, after the read above, means a link or a file that isn't regular
        why = {"missing": "it is a symbolic link or not a regular file", "no-rows": "it has no scored row"}.get(scores.reason or "", "it lists no open finding")
        raise StageError(2, stage, "%s can't be the scored input (%s)" % (path, why), remedy)
    if scores.issues:
        sys.stderr.write("WARNING: %s has %d input issue(s), the first being: %s. A row that can't be read is not planned, "
                         "and the renderer lists the issues under Input Issues\n" % (path, len(scores.issues), scores.issues[0].detail[:160]))
    return path, raw, list(scores.rows), text


def _controls_baseline(stage: str, resolution: "rules.BaselineResolution", inputs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """The baseline's persisted controls results by canonical ID (AR-T3), and its file as a digest-checked input.

    The file is ``compensating-controls.md`` in the baseline run directory. A result is read from its Section 7 ``### Assessment
    Inputs``, decoded, through ``parse_controls_assessment_inputs`` (T143): never from the rendered Sections 2, 3 or 4, whose text
    the renderer escaped. A pre-1.1 file has no Section 7 and gives none, and the agent copies from the file itself then (D2). A row
    the reader refuses leaves that finding without a result, so it is scanned fresh. A file that is missing or unreadable
    counts as missing (S-12(d)): it never stops the run.
    """
    path = resolution.files.get("compensating-controls.md")
    if path is None:
        sys.stderr.write("WARNING: the baseline run directory has no usable compensating-controls.md (%s), so every finding is scanned fresh\n"
                         % resolution.file_reasons.get("compensating-controls.md", "missing"))
        return {}
    try:
        raw, text = _read_threats(stage, os.fspath(path), "regenerate it with /tachi.compensating-controls")
    except StageError as exc:
        sys.stderr.write("WARNING: the baseline compensating-controls.md can't be read (%s), so it counts as missing and every finding "
                         "is scanned fresh\n" % exc.reason)
        return {}
    inputs["baseline_compensating_controls"] = _input_entry(stage, os.fspath(path), raw)
    persisted = parse_controls_assessment_inputs(text)
    if persisted["errors"]:
        sys.stderr.write("WARNING: the baseline compensating-controls.md has %d unreadable persisted row(s), the first being: %s. "
                         "Those findings are scanned fresh\n" % (len(persisted["errors"]), persisted["errors"][0]["reason"][:160]))
    return persisted["inputs"]


def _controls_units(stage: str, risk_scores: Any, threats: Any, baseline_flag: Optional[str], inputs: Dict[str, Dict[str, Any]],
                    refs: Dict[str, str]) -> List[Dict[str, Any]]:
    """The controls plan's units: every scored open finding of ``risk-scores.md``, in S-2 order (ADR-050 D2, D8, D9).

    The agent gets every scored finding, because it copies an UNCHANGED result from its row. A row holds the finding's
    Section 7 values (``_unit_row``) from the ``threats.md`` that the input's validated ``source_file`` names: the path
    must pass ``check_run_file`` (a regular file called ``threats.md``, no symlink on the way, under the working
    directory), the reach that D8 gives the renderer too. A ``--threats`` that is also given must be that file, because one
    stage must read one threat model. When the file can't be reached, or the input is
    ``risk-scores.sarif``, a row holds the finding's ID only, and nothing is carried forward, with a warning: the agent
    reads the rest from ``refs.risk_scores`` (this version's rows hold no more, until D8's per-member details land, P0-3).

    An UNCHANGED finding's row also takes its baseline's persisted result (``CARRIED_KEYS``), decoded, from
    ``_controls_baseline``. A finding whose form has no Status gets no ``delta_status`` and no carried result: the agent
    scans it fresh, whatever the baseline holds. ``--baseline-dir`` comes first, then the ``baseline.source`` of that
    ``threats.md`` (R-6). The input, the threat model and the baseline's controls file become digest-checked ``inputs``, and
    ``refs`` gains ``risk_scores``, ``threats`` and ``baseline_dir`` where they apply, so the renderer reads what the plan
    read. Nothing here stops a run for a baseline or a threat model that can't be used (S-12(d), D7's spirit).
    """
    cwd = os.getcwd()
    scored, scored_raw, members, scored_text = _controls_scored_input(stage, risk_scores)
    refs["risk_scores"] = scored
    inputs["risk_scores"] = _input_entry(stage, scored, scored_raw)

    source = _scored_source_file(scored_text) if scored_text is not None else None
    checked = rules.check_run_file(source, cwd=Path(cwd), expected_name="threats.md")
    reference: Dict[str, tuple] = {}
    threats_text: Optional[str] = None
    lacking: Dict[str, List[str]] = {}
    if checked.path is not None:
        threats_path = os.fspath(checked.path)
        problem = tp.path_problem(threats_path, allow_absolute=True)  # the working directory itself can hold a character a document can't carry
        if problem is not None:
            raise StageError(2, stage, "the threat model that source_file names resolves to a path that documents cannot carry (%s)" % problem,
                             "run from a directory whose path has no backslash, backtick or control character")
        if threats is not None and not _same_file(threats, threats_path):
            raise StageError(2, stage, "--threats %s is not the threat model that risk-scores.md names as its source (%s)" % (os.fspath(threats), source),
                             "drop --threats: this stage reaches threats.md through risk-scores.md's source_file")
        raw, pairs, threats_text, _, _, lacking = _read_member_set(stage, threats_path, threats_path)
        reference = {tp.canonical_finding_id(finding["id"]): (finding, unit) for finding, unit in pairs}
        refs["threats"] = threats_path
        inputs["threats"] = _input_entry(stage, threats_path, raw)
    else:
        why = ("risk-scores.sarif names no source" if scored_text is None else "source_file names no threat model" if source is None
               else "source_file %r can't be used: %s" % (source[:80], checked.reason))
        sys.stderr.write("WARNING: threats.md is not read (%s), so each unit holds the finding ID only and nothing is carried forward%s\n"
                         % (why, "; --threats is not used by this stage" if threats is not None else ""))

    baseline_source = parse_baseline_frontmatter(threats_text)["source"] if threats_text is not None else None
    resolution = rules.resolve_baseline(flag=baseline_flag, baseline_source=baseline_source, cwd=Path(cwd))
    persisted: Dict[str, Dict[str, Any]] = {}
    if resolution.run_dir is not None:
        refs["baseline_dir"] = os.fspath(resolution.run_dir)
        persisted = _controls_baseline(stage, resolution, inputs)
    elif resolution.reason != "not-named":
        sys.stderr.write("WARNING: no baseline is used (%s: %s), so every finding is scanned fresh\n" % (resolution.origin, resolution.reason))

    units: List[Dict[str, Any]] = []
    for finding_id in members:
        found = reference.get(finding_id)
        unit = dict(found[1]) if found is not None else {"finding_id": finding_id}
        if found is not None and found[0].get("delta_status") == "UNCHANGED" and finding_id in persisted:
            unit.update({key: persisted[finding_id][key] for key in CARRIED_KEYS})
        units.append(unit)

    if threats_text is not None:
        scored_ids = set(members)
        strangers = [finding_id for finding_id in members if finding_id not in reference]
        unscored = [finding_id for finding_id in reference if finding_id not in scored_ids]
        no_status = [finding_id for finding_id in members if "delta_status" in lacking.get(finding_id, ())]
        if strangers:
            sys.stderr.write("WARNING: %d scored finding(s) are not open findings of %s (%s), so their rows hold the ID only\n"
                             % (len(strangers), refs["threats"], _id_list(strangers)))
        if unscored:
            sys.stderr.write("WARNING: %d open finding(s) of %s are not in %s and are not planned (%s)\n"
                             % (len(unscored), refs["threats"], refs["risk_scores"], _id_list(unscored)))
        if no_status:
            sys.stderr.write("WARNING: Section 7 of %s has no Status for %d scored finding(s) (%s), so each is scanned fresh and none is "
                             "carried forward\n" % (refs["threats"], len(no_status), _id_list(no_status)))
    return units


def plan_stage(stage: str, out: Any, date: str, threats: Any = None, risk_scores: Any = None, baseline_dir: Any = None,
               architecture: Any = None, target: Any = None, batch_size: Optional[int] = None) -> Dict[str, Any]:
    """Plan one stage and return ``{plan_id, plan_digest, waves}``, the object ``plan`` prints.

    Reads the reference finding set from ``threats`` through the shared wrapper, so an unreadable Section 7 ends the
    run here, before anything is written or dispatched (S-12(c)). For the scorer it keeps only the findings that need
    judgment (D2: ``_scorer_routing``), and reads ``threats.sarif`` instead when ``threats.md`` is absent (D8). The
    controls stage plans from ``risk_scores`` and ``target`` instead (``_controls_units``): every scored open finding,
    each UNCHANGED one with its baseline's persisted result, and ``threats`` is optional there, because the
    ``threats.md`` comes from the input's ``source_file``. Splits those units, in S-2 order, into balanced contiguous
    batches of at most ``batch_size`` (the stage's constant when ``None``), writes the plan, one batch input for each
    batch and the pre-image copies, and only then replaces the current-plan pointer. A plan with no units (every
    finding carried or copied) has no batches and a null ``batch_size``, and reconciles as complete.

    The plan holds the stage's pointers as ``refs``, built once after the routing (which adds ``baseline_dir``), and each
    batch input copies them for its agent, so a plan with no units keeps them for the renderer's URI. It also holds
    ``architecture_warning``: the warning the shared resolver raised when it refused the ``--architecture`` candidate, or
    ``None`` (``_architecture_ref``; ruled at W2).
    """
    if stage not in tp.STAGE_AGENTS:
        raise StageError(2, stage, "%r is not a stage this version plans" % (stage,), "use risk-score or compensating-controls")
    if not isinstance(date, str) or _DATE.fullmatch(date) is None:
        raise StageError(2, stage, "--date is not YYYY-MM-DD", "pass the scoring date as YYYY-MM-DD")
    try:
        datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
    except ValueError:
        raise StageError(2, stage, "--date is not a calendar date", "pass the scoring date as YYYY-MM-DD") from None
    if stage == CONTROLS:  # the agent scans a codebase, and the renderer resolves each evidence file under it (D7)
        if risk_scores is None:
            raise StageError(2, stage, "--risk-scores is required for the %s stage" % stage, "pass the risk-scores.md to plan from")
        if target is None:
            raise StageError(2, stage, "--target is required for the %s stage" % stage, "pass the codebase directory to scan")
    elif threats is None:
        raise StageError(2, stage, "--threats is required for the %s stage" % stage, "pass the threats.md to plan from")
    size = BATCH_SIZES[stage] if batch_size is None else batch_size
    if type(size) is not int or not 1 <= size <= tp.MAX_IDS:
        raise StageError(2, stage, "the batch size must be an integer from 1 to %d" % tp.MAX_IDS)
    out = _out_dir(stage, out)

    if stage == CONTROLS:
        # AOD-SIMPLIFICATION: refs.architecture comes from the --architecture flag alone - upgrade: with no flag, fill it in _controls_units from D7's chain (the body line of the threats.md it reads, then the default)
        plan_inputs, refs, baseline_flag, architecture_warning = _pointer_refs(stage, None, baseline_dir, architecture, target)
        units = _controls_units(stage, risk_scores, threats, baseline_flag, plan_inputs, refs)
    else:
        threats_path = os.path.abspath(os.fspath(threats))
        problem = tp.path_problem(threats_path, allow_absolute=True)
        if problem is not None:
            raise StageError(2, stage, "--threats is not an acceptable path (%s)" % problem, "use a path with no backslash, backtick or control character")
        raw, members, text, threats_path, sarif_groups, lacking = _read_member_set(stage, threats, threats_path)
        extra_inputs, refs, baseline_flag, architecture_warning = _pointer_refs(stage, risk_scores, baseline_dir, architecture, target)
        refs = dict(refs, threats=threats_path)
        if stage == "risk-score":  # D2: only the findings that need judgment go to the agent
            to_agent = set(_scorer_routing(stage, members, text, sarif_groups, lacking, baseline_flag, extra_inputs, refs).to_agent)
            members = [pair for pair in members if tp.canonical_finding_id(pair[0]["id"]) in to_agent]
        units = [unit for _, unit in members]
        plan_inputs = dict(extra_inputs, threats=_input_entry(stage, threats_path, raw))

    count = len(units)
    planned = -(-count // size)
    if planned > MAX_BATCHES:
        raise StageError(2, stage, "%d findings at %d a batch need %d batches, and a batch ID allows %d" % (count, size, planned, MAX_BATCHES),
                         "reduce the findings, or report this as a bug")

    plan_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + os.urandom(6).hex()
    _prepare_directories(stage, out, plan_id)
    snapshot = _snapshot(out)  # before this plan writes a file of its own, so its files are new
    preimage = _take_preimages(stage, out, plan_id)

    plan: Dict[str, Any] = {
        "schema": tp.PLAN_SCHEMA, "plan_id": plan_id, "stage": stage, "agent_type": tp.STAGE_AGENTS[stage],
        "created_utc": _utc_now(), "tachi_version": tp.VERSION,
        "inputs": plan_inputs, "refs": refs, "architecture_warning": architecture_warning,
        "params": {"scoring_date": date}, "batch_size": size if count else None, "unit_count": count, "preimage": preimage,
        "out_snapshot": snapshot, "retry_budget": {"limit": 2 * planned, "used": 0}, "batches": [],
    }
    base, extra = divmod(count, planned) if planned else (0, 0)
    at = 0
    for number in range(planned):
        take = base + (1 if number < extra else 0)
        entry = {"batch_id": "B%03d" % (number + 1), "parent": None, "attempt": 1,
                 "finding_ids": [row["finding_id"] for row in units[at:at + take]], "input_sha256": "0" * 64, "state": "pending"}
        _write_batch_input(stage, out, plan, entry, units[at:at + take])
        plan["batches"].append(entry)
        at += take
    text = _write_document(stage, tp.plan_path(out, stage, plan_id), plan, tp.PLAN_SCHEMA, tp.validate_plan)
    _write_document(stage, tp.pointer_path(out, stage), {"schema": tp.POINTER_SCHEMA, "plan_id": plan_id}, tp.POINTER_SCHEMA, tp.validate_pointer)
    return {"plan_id": plan_id, "plan_digest": tp.sha256_hex(text.encode("utf-8")), "waves": _waves(out, stage, plan_id, plan["batches"])}


# =============================================================================
# reconcile
# =============================================================================

def _read_document(stage: str, path: str, out: str, schema: str, what: str) -> Dict[str, Any]:
    """``tachi_parts.read_document`` with D4's exit codes: 1 for a missing file, 2 for anything the contract refuses."""
    try:
        return tp.read_document(path, out, schema)
    except tp.PartError as exc:
        if exc.kind == "missing":
            raise StageError(1, stage, "%s is missing" % what, "re-run the plan step") from None
        raise StageError(2, stage, "%s is not acceptable (%s)" % (what, exc.detail), "re-run the command") from None


def _trusted_plan(stage: str, out: str, plan_id: str, digest: str) -> Dict[str, Any]:
    """The plan ``--plan`` names, once the pointer, its digest, its inputs and every batch input check out.

    Planner state is checked, not trusted (D3): a plan file or batch input edited after ``plan``, a ``--plan`` that
    disagrees with ``current.json``, an input that changed, or a digest that differs all exit 2.
    """
    pointer = _read_document(stage, tp.pointer_path(out, stage), out, tp.POINTER_SCHEMA, "the plan pointer")
    if pointer["plan_id"] != plan_id:
        raise StageError(2, stage, "--plan %s disagrees with current.json, which names %s" % (plan_id, pointer["plan_id"]),
                         "pass the plan ID that plan printed")
    path = tp.plan_path(out, stage, plan_id)
    problem = tp.path_guard_problem(path, out)
    if problem == "missing":
        raise StageError(1, stage, "plan.json is missing", "re-run the plan step")
    if problem is not None:
        raise StageError(2, stage, "plan.json failed the path guard (%s)" % problem, "re-run the command")
    if tp.file_digest(path) != digest:
        raise StageError(2, stage, "the plan file's digest differs from --plan-digest",
                         "pass the digest that the last plan or reconcile printed; if the plan was edited, re-run the command")
    plan = _read_document(stage, path, out, tp.PLAN_SCHEMA, "plan.json")
    if (plan["plan_id"], plan["stage"]) != (plan_id, stage):
        raise StageError(2, stage, "plan.json is for another plan or stage", "re-run the command")
    for name, entry in plan["inputs"].items():
        if _digest_or_none(entry["path"]) != entry["sha256"]:
            raise StageError(2, stage, "the input %s changed (or vanished) since plan" % name, "re-run the command")
    for entry in plan["batches"]:
        if _digest_or_none(tp.input_path(out, stage, plan_id, entry["batch_id"]), out) != entry["input_sha256"]:
            raise StageError(2, stage, "the batch input %s changed after plan" % entry["batch_id"], "re-run the command")
    return plan


def _read_batch(stage: str, out: str, plan: Dict[str, Any], entry: Dict[str, Any]) -> tp.PartResult:
    return tp.read_part(tp.part_path(out, stage, plan["plan_id"], entry["batch_id"], entry["attempt"]), out,
                        plan["plan_id"], entry["batch_id"], stage, plan["agent_type"], entry["finding_ids"])


def _retry(stage: str, out: str, plan: Dict[str, Any], entry: Dict[str, Any], kind: str) -> bool:
    """Retry the batch ``entry``, whose attempt came back ``kind``. False when the caps leave no retry.

    A missing, overflowed or unparseable batch of two or more units is halved into ``<id>-1`` and ``<id>-2``, each
    with the parent's attempt plus one, at a cost of 2. Any other batch (``invalid``, or one unit) is retried as it
    is, with its attempt raised and its input rewritten, at a cost of 1 (ADR-050 D6; ``contracts/part-files.md``).
    Each input is written from the plan: its ``refs`` are the plan's, never the parent input's (ruled at W2).
    """
    budget = plan["retry_budget"]
    halve = kind in ("missing", "overflow", "unparseable") and len(entry["finding_ids"]) >= 2
    cost = 2 if halve else 1
    if entry["attempt"] >= MAX_ATTEMPT or budget["used"] + cost > budget["limit"]:
        return False
    parent_input = _read_document(stage, tp.input_path(out, stage, plan["plan_id"], entry["batch_id"]), out, tp.BATCH_INPUT_SCHEMA,
                                  "the batch input %s" % entry["batch_id"])
    units = {tp.canonical_finding_id(row["finding_id"]): row for row in parent_input["units"]}
    budget["used"] += cost
    if not halve:
        entry["attempt"] += 1
        entry["state"] = "pending"
        _write_batch_input(stage, out, plan, entry, parent_input["units"])
        return True
    ids = entry["finding_ids"]
    middle = (len(ids) + 1) // 2
    entry["state"] = "split"
    at = plan["batches"].index(entry)
    for offset, (suffix, chunk) in enumerate((("-1", ids[:middle]), ("-2", ids[middle:]))):
        child = {"batch_id": entry["batch_id"] + suffix, "parent": entry["batch_id"], "attempt": entry["attempt"] + 1,
                 "finding_ids": list(chunk), "input_sha256": "0" * 64, "state": "pending"}
        plan["batches"].insert(at + 1 + offset, child)  # next to its parent, so the plan stays in S-2 order
        _write_batch_input(stage, out, plan, child, [units[tp.canonical_finding_id(i)] for i in chunk])
    return True


def reconcile_stage(stage: str, out: Any, plan_id: str, digest: str) -> tuple:
    """Work out from the files on disk what is done, and return ``(exit code, printed object, exhausted entries)``.

    Each batch's part is read for its current attempt only, so a part from an earlier plan or attempt never counts.
    Whatever isn't done is retried within the caps, and the plan file is replaced if anything changed. Exit 0 means
    every batch is done, 3 that batches are pending, and 4 that a cap or the retry budget ran out.
    """
    out = _out_dir(stage, out)
    _plan_arguments(stage, plan_id, digest)
    plan = _trusted_plan(stage, out, plan_id, digest)
    before = _dump(plan)
    exhausted = []
    for entry in list(plan["batches"]):  # a snapshot: children inserted below wait for the next reconcile
        if entry["state"] == "split":
            continue
        if entry["state"] != "failed":
            result = _read_batch(stage, out, plan, entry)
            if result.state == "done":
                entry["state"] = "done"
                continue
            if _retry(stage, out, plan, entry, result.state):
                continue
            entry["state"] = "failed"
        exhausted.append(entry)
    if _dump(plan) != before:
        digest = tp.sha256_hex(_write_document(stage, tp.plan_path(out, stage, plan_id), plan, tp.PLAN_SCHEMA, tp.validate_plan).encode("utf-8"))
    pending = [e for e in plan["batches"] if e["state"] == "pending"]
    printed: Dict[str, Any] = {"status": "complete", "plan_digest": digest,
                               "done": [e["batch_id"] for e in plan["batches"] if e["state"] == "done"], "waves": [], "exhausted": []}
    code = 0
    if exhausted:
        printed.update(status="exhausted", exhausted=[{"batch_id": e["batch_id"], "finding_ids": e["finding_ids"]} for e in exhausted])
        code = 4
    elif pending:
        printed.update(status="pending", waves=_waves(out, stage, plan_id, pending))
        code = 3
    return code, printed, exhausted


# =============================================================================
# fail
# =============================================================================

def _detail_problem(detail: str) -> Optional[str]:
    """``--detail`` is at most 500 characters and a string field: D3's character rules apply (ruled at W1)."""
    try:
        tp.closed_string(detail, "--detail", 0, 500)
    except tp.PartError as exc:
        return exc.detail
    return None


def _current_plan(out: str, stage: str) -> Optional[str]:
    """The plan ID ``current.json`` names, or None if there is no acceptable pointer."""
    try:
        return tp.read_document(tp.pointer_path(out, stage), out, tp.POINTER_SCHEMA)["plan_id"]
    except tp.PartError:
        return None


def _undeclared_paths(out: str, stage: str, plan: Dict[str, Any]) -> tuple:
    """Paths that are new or changed since the plan and that the stage's grammar doesn't declare.

    Returns ``(paths, warnings)``. The paths are sorted and capped at ``MAX_UNDECLARED_PATHS``, and a cut adds the
    warning ``undeclared-paths-truncated`` with the full count (ruled at W1). A plan with no snapshot skips the check.
    """
    snapshot = plan["out_snapshot"]
    if snapshot is None:
        return [], [{"code": "declared-paths-skipped", "detail": "the plan took no snapshot of the output directory"}]
    found = sorted(relpath for relpath, size, mtime in _walk(out)
                   if snapshot.get(relpath) != [size, mtime] and not tp.is_declared_path(relpath, stage, plan["plan_id"]))
    recordable = [relpath for relpath in found if tp.path_problem(relpath) is None]
    warnings = []
    if len(recordable) != len(found):
        warnings.append({"code": "undeclared-paths-unrecordable", "detail": "%d undeclared paths have names a record can't hold" % (len(found) - len(recordable))})
    if len(recordable) > tp.MAX_UNDECLARED_PATHS:
        warnings.append({"code": "undeclared-paths-truncated",
                         "detail": "%d undeclared paths in all; the first %d are listed" % (len(recordable), tp.MAX_UNDECLARED_PATHS)})
    return recordable[:tp.MAX_UNDECLARED_PATHS], warnings


def _move_and_restore(stage: str, out: str, plan: Dict[str, Any]) -> tuple:
    """Move each changed canonical output into ``failed/`` and put its pre-image copy back (D4; KB 21's double gate).

    A file moves only if its name is in the stage's closed set, and it is a regular file directly in ``{out}``.
    Nothing is overwritten, and a pre-image goes back only if its digest matches the one the plan recorded. A
    refused file stays where it is, and the others still go. Returns ``(moved, restored, refusals)``.
    """
    plan_id = plan["plan_id"]
    moved: List[str] = []
    restored: List[str] = []
    refusals: List[str] = []
    for name in tp.CANONICAL_OUTPUTS[stage]:  # the name gate: only the stage's own outputs are ever touched
        path = os.path.join(out, name)
        try:
            mode = os.lstat(path).st_mode
        except OSError:
            continue  # nothing there
        if not stat.S_ISREG(mode):  # the file gate: a link or a directory is never moved
            refusals.append("%s is not a regular file" % name)
            continue
        recorded = plan["preimage"].get(name)
        if tp.file_digest(path) == recorded:
            continue  # unchanged since the plan: an earlier run's output stays where it is
        destination = tp.failed_path(out, stage, plan_id, name)
        failed_directory = os.path.dirname(destination)
        if os.path.islink(failed_directory) or os.path.lexists(destination) or (
                os.path.lexists(failed_directory) and not os.path.isdir(failed_directory)):
            refusals.append("%s would overwrite or pass through something in failed/" % name)
            continue
        try:
            os.makedirs(failed_directory, exist_ok=True)
            os.replace(path, destination)
        except OSError as exc:
            refusals.append("%s could not be moved into failed/ (%s)" % (name, exc.strerror or "error"))
            continue
        moved.append(name)
        if recorded is None:
            continue
        copy = tp.preimage_path(out, stage, plan_id, name)
        if _digest_or_none(copy, out) != recorded:
            refusals.append("the pre-image of %s is missing or no longer matches its recorded digest, so it was not put back" % name)
            continue
        with open(copy, "rb") as handle:
            tp.atomic_write(path, handle.read())
        restored.append(name)
    return moved, restored, refusals


def fail_stage(stage: str, out: Any, plan_id: str, digest: str, reason: str, detail: Optional[str] = None) -> tuple:
    """End a stage that can't finish, and return ``(exit code, printed object, the message to print)``.

    Writes the failed stage record first. If the plan file's digest and the pointer both check out, it then moves
    each changed canonical output into ``failed/`` and restores the earlier run's copy, so an earlier run's outputs
    survive, a check that failed on staged files changed nothing, and a half-applied pair is undone. Exit 2 means a
    guard refused a move or the plan couldn't be trusted, and the record is written either way.
    """
    if reason not in REASONS:
        raise StageError(2, stage, "--reason is not one of %s" % ", ".join(sorted(REASONS)))
    if detail is not None:
        problem = _detail_problem(detail)
        if problem is not None:
            raise StageError(2, stage, "--detail is not acceptable (%s)" % problem, "pass at most 500 characters of plain text")
    out = _out_dir(stage, out, missing_code=2)  # fail has no exit 1 (cli.md)
    _plan_arguments(stage, plan_id, digest)
    path = tp.plan_path(out, stage, plan_id)
    if tp.path_guard_problem(path, out) is not None:
        raise StageError(2, stage, "there is no plan %s to fail" % plan_id, "check --plan and --out")
    trusted, warnings = True, []
    if tp.file_digest(path) != digest:
        trusted = False
        warnings.append({"code": "plan-digest-mismatch", "detail": "the plan file's digest differs from --plan-digest, so nothing was moved"})
    try:
        plan = tp.read_document(path, out, tp.PLAN_SCHEMA)
    except tp.PartError as exc:
        raise StageError(2, stage, "plan.json is not acceptable (%s)" % exc.detail, "re-run the command") from None
    if _current_plan(out, stage) != plan_id:
        trusted = False
        warnings.append({"code": "pointer-mismatch", "detail": "current.json does not name this plan, so nothing was moved"})

    what, remedy = REASONS[reason]
    first = next((e for e in plan["batches"] if e["state"] == "failed"), None) if reason == "unrecoverable-batch" else None
    kept = tp.plan_dir(out, stage, plan_id)
    events, retries = tp.retry_history(stage, out, plan)
    undeclared, undeclared_warnings = _undeclared_paths(out, stage, plan)
    # D7's order puts the explicit candidate's warning first. A plan that fails its trust checks has no say in the record.
    planned_warning = [dict(plan["architecture_warning"])] if trusted and plan["architecture_warning"] is not None else []
    accepted = {}
    for entry in plan["batches"]:
        if entry["state"] == "done":
            result = _read_batch(stage, out, plan, entry)
            if result.state == "done":
                accepted.update({item["finding_id"]: item for item in result.part["items"]})
    record: Dict[str, Any] = {
        "schema": tp.STAGE_RECORD_SCHEMA, "stage": stage, "plan_id": plan_id, "status": "failed", "tachi_version": tp.VERSION,
        "started_utc": plan["created_utc"], "finished_utc": _utc_now(),
        "input_digest": tp.input_digest({
            "sources": {name: entry["sha256"] for name, entry in sorted(plan["inputs"].items())}, "params": plan["params"],
            "items": [accepted[key] for key in sorted(accepted, key=tp.finding_sort_key)], "fragments": []}),
        "counts": {"units": plan["unit_count"], "open": plan["unit_count"]},
        "batches": {"planned": sum(1 for e in plan["batches"] if e["parent"] is None),
                    "dispatched": sum(1 for e in plan["batches"] if e["parent"] is None) + plan["retry_budget"]["used"],
                    "done": sum(1 for e in plan["batches"] if e["state"] == "done"), "retried": plan["retry_budget"]["used"],
                    "split": sum(1 for e in plan["batches"] if e["state"] == "split"),
                    "exhausted": sum(1 for e in plan["batches"] if e["state"] == "failed")},
        "overflow_events": events, "retries": retries, "warnings": planned_warning + warnings + undeclared_warnings,
        "undeclared_paths": undeclared, "outputs": [],
        "error": {"code": reason, "message": what + (": " + detail if detail else ""),
                  "batch_id": first["batch_id"] if first else None, "finding_ids": list(first["finding_ids"]) if first else [],
                  "remedy": remedy},
    }
    record_path = tp.stage_record_path(out, stage, plan_id)
    _write_document(stage, record_path, record, tp.STAGE_RECORD_SCHEMA, tp.validate_stage_record)  # first, before any move

    moved: List[str] = []
    restored: List[str] = []
    refusals: List[str] = []
    if trusted:
        moved, restored, refusals = _move_and_restore(stage, out, plan)
        record["outputs"] = [{"path": "%s/%s/%s/failed/%s" % (tp.BUILD_DIR, stage, plan_id, name),
                              "sha256": tp.file_digest(tp.failed_path(out, stage, plan_id, name))} for name in moved]
        for refusal in refusals:
            record["warnings"].append({"code": "move-refused", "detail": refusal})
        if moved or refusals:
            _write_document(stage, record_path, record, tp.STAGE_RECORD_SCHEMA, tp.validate_stage_record)
    code = 0 if trusted and not refusals else 2
    named_agent = reason == "agent-not-spawned"
    headline = what + (": " + detail if detail and not named_agent else "")
    problems = [w["detail"] for w in warnings] + refusals
    message = StageError(code, stage, headline + ("; " + "; ".join(problems) if problems else ""), remedy,
                         batch=(first["batch_id"], ", ".join(first["finding_ids"])) if first else None,
                         agent=detail if named_agent and detail else None, kept=kept)
    return code, {"moved": moved, "restored": restored, "record": record_path}, message.text()


# =============================================================================
# architecture-source (FR-E.18; ADR-050 D7 item 6)
# =============================================================================

def _edit_architecture_line(text: str, path: Optional[str]) -> tuple:
    """``threats.md``'s text with its architecture-source lines removed and, given a ``path``, one put back.

    Returns ``(new text, what happened)``: ``added``, ``replaced``, ``removed`` or ``unchanged``. Only the lines that
    ``sarif_common``'s reader finds count (after the frontmatter, before the first ``## `` heading, outside code
    fences), so a forged copy inside a fence is neither read nor changed. A removed line takes the one blank line
    after it, so a line that an earlier run added leaves the text as it was, and a second upsert changes no byte.
    The new line goes at the region's end, followed by a blank line when a heading follows.
    """
    found = sc.find_architecture_source_lines(text)
    edited = text
    for start, end, _path in reversed(found):  # from the end, so the earlier offsets stay true
        for blank in ("\n", "\r\n"):
            if edited.startswith(blank, end):
                end += len(blank)
                break
        edited = edited[:start] + edited[end:]
    if path is not None:
        _begin, stop = sc.architecture_source_region(edited)
        joiner = "" if stop == 0 or edited[stop - 1] == "\n" else "\n"
        gap = "\n\n" if stop < len(edited) else "\n"
        edited = edited[:stop] + joiner + sc.format_architecture_source_line(path) + gap + edited[stop:]
    if edited == text:
        return edited, "unchanged"
    if path is None:
        return edited, "removed"
    return edited, "replaced" if found else "added"


def architecture_source(threats: Any, candidate: str) -> tuple:
    """Write, replace or remove the ``**Architecture source**`` line of a ``threats.md``, and return ``(code, printed)``.

    ``candidate`` is the command's own path to the architecture file. The shared resolver checks it (ADR-050 D7) and
    gives its canonical spelling, which the line carries. This never falls back to the body line or the default
    constant (ruled at W1): if the resolver refuses the path, any line already in the file is removed, so a line that
    the orchestrator wrote can't survive, a warning goes to stderr, and the exit code is 5. The run goes on.

    ``threats`` is edited in place, atomically, and only when its text changes. It must be a regular file and not a
    link, so the edit never detaches a link from its target.
    """
    stage = "threat-model"
    path = os.path.abspath(os.fspath(threats))
    try:
        mode = os.lstat(path).st_mode
    except OSError as exc:
        raise StageError(1, stage, "cannot read %s (%s)" % (path, exc.strerror or "error"), "check the path and re-run") from None
    if not stat.S_ISREG(mode):
        raise StageError(2, stage, "%s is a link or not a regular file, so it is not edited in place" % path, "pass the threats.md itself")
    _raw, text = _read_threats(stage, path)

    resolved: Optional[str] = None
    warnings: List[Dict[str, str]] = []
    try:
        resolved = sc.resolve_file(candidate, allow_absolute=True).path
        sc.format_architecture_source_line(resolved)  # a canonical spelling the line can't carry is a failure too
    except (sc.PathCheckError, ValueError) as exc:
        check = exc.check if isinstance(exc, sc.PathCheckError) else "unrepresentable"
        resolved = None
        warnings.append({"code": "architecture-path:explicit:%s" % check,
                         "detail": "the --architecture path %s failed the %s check, so no architecture-source line was written "
                                   "and any existing one was removed. Pass %s with the repo-relative path of the architecture file."
                                   % (repr(candidate)[:80], check, sc.ARCHITECTURE_FLAG)})
    edited, action = _edit_architecture_line(text, resolved)
    if edited != text:
        try:
            tp.atomic_write(path, edited)
        except OSError as exc:
            raise StageError(1, stage, "cannot write %s (%s)" % (path, exc.strerror or "error"), "check the directory's permissions and re-run") from None
    return (5 if warnings else 0), {"architecture_source": resolved, "action": action, "warnings": warnings}


# =============================================================================
# The command line
# =============================================================================

def _emit(obj: Dict[str, Any]) -> None:
    sys.stdout.write(_dump(obj))


def _run_plan(args: argparse.Namespace) -> int:
    _emit(plan_stage(args.stage, args.out, args.date, threats=args.threats, risk_scores=args.risk_scores,
                     baseline_dir=args.baseline_dir, architecture=args.architecture, target=args.target))
    return 0


def _run_reconcile(args: argparse.Namespace) -> int:
    code, printed, exhausted = reconcile_stage(args.stage, args.out, args.plan, args.plan_digest)
    _emit(printed)
    if exhausted:
        first = exhausted[0]
        more = "" if len(exhausted) == 1 else " (%d batches in all ran out of retries)" % len(exhausted)
        sys.stderr.write(StageError(4, args.stage, "batch %s could not be completed within the retry caps%s" % (first["batch_id"], more),
                                    "re-run the command, and report the kept plan directory if the same batch fails again",
                                    batch=(first["batch_id"], ", ".join(first["finding_ids"])),
                                    kept=tp.plan_dir(args.out, args.stage, args.plan)).text() + "\n")
    return code


def _run_fail(args: argparse.Namespace) -> int:
    code, printed, message = fail_stage(args.stage, args.out, args.plan, args.plan_digest, args.reason, args.detail)
    _emit(printed)
    sys.stderr.write(message + "\n")
    return code


def _run_architecture_source(args: argparse.Namespace) -> int:
    code, printed = architecture_source(args.threats, args.architecture)
    _emit(printed)
    for warning in printed["warnings"]:
        sys.stderr.write("WARNING: %s\n" % warning["detail"])
    return code


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tachi-stage.py", description="Plan, reconcile and fail a batched tachi stage (F-374).")
    parser.add_argument("--version", action="version",
                        version="tachi-stage.py %s (python %s)" % (tp.VERSION, platform.python_version()))
    commands = parser.add_subparsers(dest="command", required=True)
    stages = sorted(tp.STAGE_AGENTS)

    plan = commands.add_parser("plan", help="split a stage's units into batches and write the plan")
    plan.add_argument("--stage", required=True, choices=stages)
    plan.add_argument("--out", required=True, help="the run's output directory; everything is written under it")
    plan.add_argument("--date", required=True, help="the scoring date, YYYY-MM-DD")
    plan.add_argument("--threats", help="the threats.md to read the reference finding set from (required for risk-score; compensating-controls "
                                        "reaches it through risk-scores.md's source_file, so there it is optional and must be that file)")
    plan.add_argument("--risk-scores", help="the risk-scores.md that compensating-controls plans from (required there; the risk-scores.sarif "
                                            "beside it is read when it is absent)")
    plan.add_argument("--baseline-dir", help="a baseline run directory")
    plan.add_argument("--architecture", help="a candidate path to the architecture file")
    plan.add_argument("--target", help="the codebase directory a stage reads (required for compensating-controls)")
    plan.set_defaults(run=_run_plan)

    for name, run, text in (("reconcile", _run_reconcile, "work out what is done, and what to dispatch next"),
                            ("fail", _run_fail, "end a stage that can't finish, and put earlier outputs back")):
        command = commands.add_parser(name, help=text)
        command.add_argument("--stage", required=True, choices=stages)
        command.add_argument("--out", required=True)
        command.add_argument("--plan", required=True, help="the plan ID that plan printed")
        command.add_argument("--plan-digest", required=True, help="the plan_digest that the last plan or reconcile printed")
        if name == "fail":
            command.add_argument("--reason", required=True, choices=sorted(REASONS))
            command.add_argument("--detail", help="at most 500 characters of plain text, such as the agent that failed")
        command.set_defaults(run=run)

    source = commands.add_parser("architecture-source", help="write the threats.md line that names the architecture file")
    source.add_argument("--threats", required=True, help="the threats.md to edit in place")
    source.add_argument("--architecture", required=True, help="the command's own path to the architecture file; the shared resolver checks it")
    source.set_defaults(run=_run_architecture_source)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return args.run(args)
    except StageError as exc:
        sys.stderr.write(exc.text() + "\n")
        return exc.code


if __name__ == "__main__":  # pragma: no cover  (a process alone shows it: test_exit_codes_come_from_a_real_interpreter)
    raise SystemExit(main())
