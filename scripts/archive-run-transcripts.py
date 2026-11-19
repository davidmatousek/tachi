#!/usr/bin/env python3
"""archive-run-transcripts.py -- archive a Claude Code session and write its provenance manifest (Feature 391, Part B1).

Run by the operator from a plain shell AFTER a session. It copies the session's
transcripts verbatim to a location that cannot be committed, then writes
``run-manifest.json`` (structured fields only) saying which model served each
agent, which tachi agents were dispatched at any depth, which hosts the tool
calls named, which calls were denied, and the hash of every file in the run's
output directory. The archive is SENSITIVE: it holds your architecture, code and
findings unredacted. The manifest is not: its fields are structural, and a final
scan refuses to write it when a secret-shaped value reached it.

Usage::

    python3 scripts/archive-run-transcripts.py (--session SESSION_ID | --latest)
        [--project-dir PATH] [--dest PATH] [--output-dir PATH]
        [--allow-live] [--live-window-seconds 120] [--json]

Constraints: Python >= 3.9, stdlib only (no PyYAML). Run it under the same
secret-injection wrapper as the session, so the final scan sees the same
secret-named environment values the session did. The manifest fields are
documented in ``schemas/run-manifest.yaml``.

Exit codes:
    0  archived and manifest written, or an identical finished archive already
       exists (no-op).
    1  refused or failed: destination refusals (inside a git work tree and not
       ignored, non-empty, symlink into a work tree, live session), a parse
       failure against the minimal contract, a source tree that holds a symlink,
       or a secret-scan hit. No manifest is written on a parse failure or a scan
       hit; the verbatim copy that preceded it is kept for inspection.
    2  infrastructure: no Claude Code projects directory, no transcript matching
       the project, no installed tachi agents, an unreadable file, ``git``
       absent when a work-tree check is needed, or a bad argument.

Error messages go to stderr with a ``[391]`` prefix. They name files, line
numbers, rule ids and environment variable NAMES, never transcript content or
secret values.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import ipaddress
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
import traceback
from collections import Counter

# =============================================================================
# Constants
# =============================================================================

MANIFEST_VERSION = 1
MANIFEST_NAME = "run-manifest.json"
MANIFEST_TMP_NAME = ".run-manifest.json.tmp"

DEFAULT_LIVE_WINDOW_SECONDS = 120
DIR_MODE = 0o700
FILE_MODE = 0o600
CHUNK_BYTES = 1024 * 1024
GIT_TIMEOUT_SECONDS = 30
SCAN_CWD_LINES = 2000  # discovery reads at most this many lines per transcript

TACHI_PREFIX = "tachi-"
SYNTHETIC_MODEL = "<synthetic>"
UNPARSEABLE = "<unparseable>"
DISPATCH_TOOL_NAMES = ("Agent", "Task")  # "Task" is the legacy name of "Agent"
EGRESS_TOOLS = ("Bash", "WebFetch")
DENIAL_KINDS = ("sandbox", "classifier", "permission-rule")

# Claude Code versions whose denial markers were checked against a RECORDED run
# (feature 391 T035 appends the recorded run's version). Empty until then: the
# synthetic fixtures model the layout but must never populate this set, so every
# manifest reads denial_detection.status "not-validated" and an empty
# egress_denied list never reads as "no denials occurred".
VALIDATED_DENIAL_VERSIONS = frozenset()

# The twelve metadata keys observed at Claude Code 2.1.328 (W0' spike). Only
# agentType and toolUseId are required; anything else is listed, never rejected.
KNOWN_META_KEYS = frozenset({
    "agentType", "description", "finished", "isBuiltIn", "launchedWithDefaults",
    "model", "parentAgentId", "pickedEffortModel", "requestNonInteractive",
    "requestShape", "spawnDepth", "toolUseId",
})

# Entry types and assistant keys seen so far. Anything else is tolerated and
# counted in the run summary (layout drift shows up there, never as a failure).
KNOWN_ENTRY_TYPES = frozenset({
    "user", "assistant", "attachment", "system", "summary", "mode",
    "permission-mode", "session-owner", "atis-latch", "api-request",
    "api-request-blob", "api-request-shape", "queue-operation", "last-prompt",
    "tools-used", "ai-title", "file-history-snapshot", "file-history-delta",
})
KNOWN_ASSISTANT_KEYS = frozenset({
    "type", "uuid", "parentUuid", "timestamp", "sessionId", "cwd", "version",
    "gitBranch", "userType", "entrypoint", "isSidechain", "isMeta", "agentId",
    "message", "requestId", "requestedModel", "attributionAgent",
    "attributionSkill", "serverClassifierRequest", "effort", "perTurnEffort",
    "sandboxed", "isApiErrorMessage", "error", "slug",
})

_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_CLOEXEC = getattr(os, "O_CLOEXEC", 0)

# A value copied out of a transcript into the manifest must be one short token
# (no whitespace or control characters): structure, never free text.
_TOKEN_RE = re.compile(r"[^\s\x00-\x1f\x7f]{1,128}\Z")
_SESSION_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
_MARKER_RE = re.compile(r"tachi_version:[ \t]*([A-Za-z0-9][A-Za-z0-9._+~-]{0,127})[ \t]*\r?\Z")
_TS_RE = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})[Tt ](\d{2}):(\d{2}):(\d{2})(?:[.,](\d{1,9}))?"
    r"[ ]?(Z|z|[+-]\d{2}(?::?\d{2})?)?\Z"
)
_URL_RE = re.compile(r"""\b([A-Za-z][A-Za-z0-9+.\-]{1,15})://([^\s'"<>`\\|^{}]+)""")
_HOST_LABEL_RE = re.compile(r"[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?\Z")

# Environment variables that locate a git repository must not steer the
# destination check (it has to see the real work tree around the destination).
_GIT_LOCATION_VARS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_PREFIX",
    "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE",
)

# Final secret scan: known key formats (matched at any length, case-insensitively
# because hostnames are lower-cased before they reach the manifest) ...
_KEY_PATTERNS = (
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("anthropic-api-key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai-api-key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("github-fine-grained-token", re.compile(r"github_pat_[A-Za-z0-9_]{22,}")),
    ("aws-access-key-id", re.compile(r"(?:AKIA|ASIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA)[0-9A-Z]{16}")),
    ("slack-token", re.compile(r"xox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("stripe-key", re.compile(r"[sr]k_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("json-web-token", re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}")),
    ("service-account-token", re.compile(r"ops_[A-Za-z0-9+/=_\-]{40,}")),
    ("bearer-credential", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/\-]{20,}")),
    ("url-userinfo-password", re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^/\s:@]+:[^/\s@]+@")),
)
_KEY_PATTERNS = tuple((rule, re.compile(rx.pattern, re.IGNORECASE)) for rule, rx in _KEY_PATTERNS)
# ... and the VALUES of environment variables whose NAMES say they are secrets.
_SECRET_NAME_RE = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL", re.IGNORECASE)
_SECRET_VALUE_FLOOR = 8  # shorter values collide with counts, mode names and ids
_NOT_SECRET_LITERALS = frozenset({"true", "false", "yes", "no", "on", "off", "null", "none"})


# =============================================================================
# Errors
# =============================================================================


class ArchiveError(Exception):
    """Base class: ``reason`` is printed to stderr; ``exit_code`` is returned."""

    exit_code = 1
    status = "failed"

    def __init__(self, reason):
        Exception.__init__(self, reason)
        self.reason = reason


class Refusal(ArchiveError):
    """A deny-by-default refusal (destination, live session, source symlink)."""

    status = "refused"


class ParseFailure(ArchiveError):
    """The transcripts do not meet the minimal parse contract (or a scan hit)."""

    status = "failed"


class InfraError(ArchiveError):
    """Infrastructure problem: missing input, unreadable file, git absent."""

    exit_code = 2
    status = "infra"


# =============================================================================
# Small helpers
# =============================================================================


def _token(value, what):
    """Return ``value`` when it is one short token; otherwise fail the run."""
    if isinstance(value, str) and _TOKEN_RE.match(value):
        return value
    raise ParseFailure("unexpected shape for %s (expected one short token)" % what)


def _label(value):
    """A token for display counts (entry types, keys); odd values collapse."""
    if isinstance(value, str) and _TOKEN_RE.match(value):
        return value
    return UNPARSEABLE


def _posix(*parts):
    return "/".join(parts)


def _utc_stamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_timestamp(text):
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None.

    Hand-parsed on purpose: ``datetime.fromisoformat`` rejects a ``Z`` suffix
    before Python 3.11, and ``%f`` cannot take nanosecond fractions.
    """
    m = _TS_RE.match(text)
    if m is None:
        return None
    year, month, day, hour, minute, second = (int(m.group(i)) for i in range(1, 7))
    frac = m.group(7) or ""
    micro = int((frac + "000000")[:6]) if frac else 0
    try:
        dt = datetime.datetime(year, month, day, hour, minute, second, micro,
                               tzinfo=datetime.timezone.utc)
    except ValueError:
        return None
    zone = m.group(8)
    if zone and zone not in ("Z", "z"):
        digits = zone[1:].replace(":", "")
        offset = datetime.timedelta(hours=int(digits[0:2]), minutes=int(digits[2:4] or 0))
        dt = dt - offset if zone[0] == "+" else dt + offset
    return dt


def _version_key(version):
    """Sort Claude Code versions by their numeric components (2.1.9 before 2.1.10)."""
    return (tuple(int(p) if p.isdigit() else -1 for p in re.split(r"[.\-]", version)), version)


def _hash_open_file(fh):
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = fh.read(CHUNK_BYTES)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def _hash_regular_file(path):
    """SHA-256 and size of a regular file, never following a symlink."""
    fd = os.open(path, os.O_RDONLY | _NOFOLLOW | _CLOEXEC)
    with os.fdopen(fd, "rb") as fh:
        if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
            raise OSError("not a regular file")
        return _hash_open_file(fh)


# =============================================================================
# Roster and version marker
# =============================================================================


def _frontmatter_value(text, key):
    """Value of a top-level ``key:`` line in a leading ``---`` block, or None."""
    lines = text.split("\n")
    if not lines or lines[0].lstrip("﻿").strip() != "---":
        return None
    prefix = key + ":"
    for line in lines[1:]:
        line = line.rstrip("\r")
        if line.strip() == "---":
            break
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                return value[1:-1]
            return value.split(" #", 1)[0].strip()
    return None


def _load_roster(project_real):
    """{tachi agent name: pinned model alias or None} from the installed agents.

    The roster is the ``name:`` values of ``.claude/agents/tachi/*.md`` under the
    project (the permissions matrix is not installed, and its absence is never an
    error). ``pinned_model`` is the alias string exactly as the file writes it.
    """
    agents_dir = os.path.join(project_real, ".claude", "agents", "tachi")
    try:
        names = sorted(os.listdir(agents_dir))
    except OSError:
        raise InfraError("no installed tachi agents: .claude/agents/tachi/ is missing under --project-dir")
    roster = {}
    for fname in names:
        path = os.path.join(agents_dir, fname)
        if not fname.endswith(".md") or os.path.islink(path) or not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                head = fh.read(65536)
        except OSError:
            continue
        name = _frontmatter_value(head, "name")
        if not name or not name.startswith(TACHI_PREFIX) or not _TOKEN_RE.match(name):
            continue
        model = _frontmatter_value(head, "model")
        if name not in roster:
            roster[name] = model if model and _TOKEN_RE.match(model) else None
    if not roster:
        raise InfraError("no installed tachi agents: no 'name: tachi-*' agent file under .claude/agents/tachi/")
    return roster


def _read_version_marker(project_real):
    """The install-time ``tachi_version`` value, or ``unknown`` (absent or malformed)."""
    path = os.path.join(project_real, "templates", "tachi", "VERSION")
    try:
        st = os.lstat(path)
        if not stat.S_ISREG(st.st_mode) or st.st_size > 4096:
            return "unknown"
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return "unknown"
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != 1:
        return "unknown"
    m = _MARKER_RE.match(lines[0])
    return m.group(1) if m else "unknown"


# =============================================================================
# Discovery (project found by matching the transcripts' cwd)
# =============================================================================


def _config_dir():
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    if configured:
        return os.path.abspath(os.path.expanduser(configured))
    return os.path.join(os.path.expanduser("~"), ".claude")


def _first_cwd(path):
    """The real path of the first ``cwd`` a transcript records, or None."""
    try:
        with open(path, "rb") as fh:
            for index, raw in enumerate(fh):
                if index >= SCAN_CWD_LINES:
                    break
                if b'"cwd"' not in raw:
                    continue
                try:
                    obj = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(obj, dict) and isinstance(obj.get("cwd"), str) and obj["cwd"]:
                    return os.path.realpath(obj["cwd"])
    except OSError:
        return None
    return None


def _discover(projects_dir, project_real, session_id, latest, warnings):
    """Return the main transcript path whose cwd matches the project."""
    try:
        slugs = sorted(os.listdir(projects_dir))
    except OSError:
        raise InfraError("cannot read the Claude Code projects directory")
    candidates = []
    for slug in slugs:
        slug_dir = os.path.join(projects_dir, slug)
        try:
            if not stat.S_ISDIR(os.lstat(slug_dir).st_mode):
                continue  # also skips a symlinked entry
            names = [session_id + ".jsonl"] if session_id else sorted(os.listdir(slug_dir))
        except OSError:
            continue
        for name in names:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(slug_dir, name)
            try:
                st = os.lstat(path)
            except OSError:
                continue
            if stat.S_ISREG(st.st_mode):
                candidates.append((st.st_mtime_ns, path))
    candidates.sort(reverse=True)  # newest first
    matches = []
    for _mtime, path in candidates:
        if _first_cwd(path) == project_real:
            matches.append(path)
            if latest:
                break
    if not matches:
        if session_id:
            raise InfraError("no transcript for that session id matches --project-dir")
        raise InfraError("no main transcript matches --project-dir (matched by the transcripts' cwd)")
    if len(matches) > 1:
        warnings.append("more than one transcript matched the session id; the newest was used")
    return matches[0]


# =============================================================================
# Source tree
# =============================================================================


def _enumerate_source(main_path, session_id):
    """([(rel, abs)] files, [rel] directories) of the session, refusing symlinks."""
    slug_dir = os.path.dirname(main_path)
    session_dir = os.path.join(slug_dir, session_id)
    files = [(session_id + ".jsonl", main_path)]
    dirs = []
    if not os.path.lexists(session_dir):
        return files, dirs
    if not stat.S_ISDIR(os.lstat(session_dir).st_mode):
        raise Refusal("the session directory is a symbolic link or not a directory; refusing to copy it")
    dirs.append(session_id)
    for root, dnames, fnames in os.walk(session_dir, topdown=True, followlinks=False):
        dnames.sort()
        rel_root = os.path.relpath(root, slug_dir).replace(os.sep, "/")
        for dname in dnames:
            if os.path.islink(os.path.join(root, dname)):
                raise Refusal("the session tree holds a symbolic link (%s/%s); refusing to copy it" % (rel_root, dname))
            dirs.append(_posix(rel_root, dname))
        for fname in sorted(fnames):
            full = os.path.join(root, fname)
            mode = os.lstat(full).st_mode
            rel = _posix(rel_root, fname)
            if stat.S_ISLNK(mode):
                raise Refusal("the session tree holds a symbolic link (%s); refusing to copy it" % rel)
            if not stat.S_ISREG(mode):
                raise Refusal("the session tree holds a file that is not a regular file (%s)" % rel)
            files.append((rel, full))
    return files, dirs


def _first_timestamp(path):
    """The first parseable top-level ``timestamp`` of a transcript, or None."""
    try:
        with open(path, "rb") as fh:
            for raw in fh:
                if b'"timestamp"' not in raw:
                    continue
                try:
                    obj = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(obj, dict) and isinstance(obj.get("timestamp"), str):
                    dt = _parse_timestamp(obj["timestamp"])
                    if dt is not None:
                        return dt
    except OSError:
        return None
    return None


# =============================================================================
# Destination and the refusal matrix
# =============================================================================


def _nearest_existing(path):
    """(deepest existing ancestor, [missing components below it]) of an absolute path."""
    current = path
    missing = []
    while not os.path.lexists(current):
        parent, tail = os.path.split(current)
        if parent == current:
            break
        missing.append(tail)
        current = parent
    missing.reverse()
    return current, missing


def _git_marker_above(real_path):
    """Directory at or above ``real_path`` that holds a ``.git`` entry, or None."""
    current = real_path
    while True:
        if os.path.lexists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def _git_env():
    env = {k: v for k, v in os.environ.items() if k not in _GIT_LOCATION_VARS}
    env["GIT_DISCOVERY_ACROSS_FILESYSTEM"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def _run_git(args, cwd):
    git = shutil.which("git")
    if git is None:
        raise InfraError("git is required for the destination work-tree check but was not found")
    try:
        return subprocess.run([git] + args, cwd=cwd, env=_git_env(), stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=GIT_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InfraError("git could not be run for the destination check (%s)" % type(exc).__name__)


def _check_destination(dest_abs):
    """Deny by default: refuse a destination a later commit could pick up."""
    # 1. A symbolic link in the destination path that resolves into a work tree.
    prefix = os.sep
    for part in dest_abs.split(os.sep):
        if not part:
            continue
        prefix = os.path.join(prefix, part)
        if not os.path.lexists(prefix):
            break
        if os.path.islink(prefix) and _git_marker_above(os.path.realpath(prefix)) is not None:
            raise Refusal("a symbolic link in the destination path resolves into a git work tree; refusing to follow it")
    # 2. The nearest existing ancestor (real path) inside a work tree, unless the
    #    work tree ignores a path inside the destination.
    ancestor, missing = _nearest_existing(dest_abs)
    real_ancestor = os.path.realpath(ancestor)
    if _git_marker_above(real_ancestor) is None:
        return
    cwd = real_ancestor if os.path.isdir(real_ancestor) else os.path.dirname(real_ancestor)
    top = _run_git(["rev-parse", "--show-toplevel"], cwd)
    if top.returncode != 0 or not top.stdout.strip():
        raise Refusal("the destination lies where git cannot name the enclosing work tree; refusing (deny by default)")
    toplevel = os.path.realpath(top.stdout.decode("utf-8", "replace").strip())
    probe = os.path.join(real_ancestor, *(missing + [".probe"]))
    ignored = _run_git(["check-ignore", "-q", "--", probe], toplevel)
    if ignored.returncode == 0:
        return
    if ignored.returncode == 1:
        raise Refusal("the destination is inside a git work tree and is not ignored there (git check-ignore); "
                      "choose a --dest outside any work tree or ignore the runs directory")
    raise Refusal("cannot tell whether git ignores the destination (git check-ignore exit %d); refusing" % ignored.returncode)


def _existing_archive_is_identical(dest_abs, source_files):
    """Refuse unless dest holds an identical, FINISHED archive; True means no-op."""
    for rel, src in source_files:
        archived = os.path.join(dest_abs, *rel.split("/"))
        try:
            same = _hash_regular_file(archived)[0] == _hash_regular_file(src)[0]
        except OSError:
            same = False
        if not same:
            raise Refusal("the destination is not empty and does not hold an identical archive of this session; use a new --dest")
    manifest = os.path.join(dest_abs, MANIFEST_NAME)
    try:
        finished = stat.S_ISREG(os.lstat(manifest).st_mode)
    except OSError:
        finished = False
    if not finished:
        raise Refusal("incomplete archive: run-manifest.json absent; use a new --dest")
    return True


def _check_live(source_files, window, allow_live):
    if allow_live:
        return
    now = time.time()
    live = []
    for rel, src in source_files:
        if rel.endswith(".jsonl") and now - os.lstat(src).st_mtime < window:
            live.append(rel)
    if live:
        raise Refusal("the session looks live: %d transcript(s) changed within the last %d s; "
                      "wait for it to finish or pass --allow-live" % (len(live), window))


def _prepare_destination(dest_abs):
    """Create the destination and any missing parents, directories owner-only."""
    ancestor, missing = _nearest_existing(dest_abs)
    current = ancestor
    try:
        for part in missing:
            current = os.path.join(current, part)
            os.mkdir(current, DIR_MODE)
            os.chmod(current, DIR_MODE)
        st = os.stat(dest_abs)
    except OSError as exc:
        raise InfraError("cannot create the destination directory (%s)" % (exc.strerror or type(exc).__name__))
    if not missing:  # a pre-existing empty destination: it must be ours and owner-only
        if hasattr(os, "geteuid") and st.st_uid != os.geteuid():
            raise Refusal("the destination directory is owned by another user")
        if st.st_mode & 0o077:
            os.chmod(dest_abs, DIR_MODE)


# =============================================================================
# Verbatim copy
# =============================================================================


def _copy_file(src, dst, rel):
    """Copy one regular file: O_EXCL, mode 0600, no symlink followed; hash-checked."""
    try:
        sfd = os.open(src, os.O_RDONLY | _NOFOLLOW | _CLOEXEC)
    except OSError as exc:
        raise InfraError("cannot read %s (%s)" % (rel, exc.strerror or type(exc).__name__))
    with os.fdopen(sfd, "rb") as fin:
        if not stat.S_ISREG(os.fstat(fin.fileno()).st_mode):
            raise Refusal("the session tree holds a file that is not a regular file (%s)" % rel)
        try:
            dfd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW | _CLOEXEC, FILE_MODE)
        except OSError as exc:
            raise InfraError("cannot create %s in the archive (%s)" % (rel, exc.strerror or type(exc).__name__))
        digest = hashlib.sha256()
        size = 0
        with os.fdopen(dfd, "wb") as fout:
            while True:
                chunk = fin.read(CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
                fout.write(chunk)
                size += len(chunk)
            fout.flush()
            os.fchmod(fout.fileno(), FILE_MODE)
    try:
        check, check_size = _hash_regular_file(dst)
    except OSError as exc:
        raise InfraError("cannot read back %s from the archive (%s)" % (rel, exc.strerror or type(exc).__name__))
    if check != digest.hexdigest() or check_size != size:
        raise InfraError("the archived copy of %s differs from what was read from the source" % rel)
    return rel, size, check


def _copy_session(dest_abs, source_files, source_dirs):
    try:
        for rel in source_dirs:
            path = os.path.join(dest_abs, *rel.split("/"))
            os.mkdir(path, DIR_MODE)
            os.chmod(path, DIR_MODE)
    except OSError as exc:
        raise InfraError("cannot create an archive directory (%s)" % (exc.strerror or type(exc).__name__))
    return [_copy_file(src, os.path.join(dest_abs, *rel.split("/")), rel) for rel, src in source_files]


# =============================================================================
# Transcript scan
# =============================================================================


def _host_from_authority(authority):
    """Bare lower-case hostname from a URL authority, or UNPARSEABLE."""
    if "@" in authority:
        authority = authority.rsplit("@", 1)[1]  # userinfo dropped
    if authority.startswith("["):
        end = authority.find("]")
        if end == -1:
            return UNPARSEABLE
        host = authority[1:end]
        rest = authority[end + 1:]
        if rest and not re.match(r":\d{0,5}\Z", rest):
            return UNPARSEABLE
        try:
            ipaddress.IPv6Address(host.split("%", 1)[0])
        except ValueError:
            return UNPARSEABLE
        return host.lower()
    host = authority
    if ":" in authority:
        host, port = authority.rsplit(":", 1)
        if not re.match(r"\d{0,5}\Z", port):
            return UNPARSEABLE
    host = host.rstrip(".").lower()
    if not host or len(host) > 253:
        return UNPARSEABLE
    if all(_HOST_LABEL_RE.match(label) for label in host.split(".")):
        return host
    return UNPARSEABLE


# AOD-SIMPLIFICATION: URL hosts in Bash commands and WebFetch URLs only -- upgrade: add other tools that carry a URL field (for example MCP browser tools) when the spec grows
def _hosts_in_text(text, strict=False):
    """Distinct hosts named by URLs in ``text``; userinfo, port, query and fragment are never kept."""
    if not isinstance(text, str):
        return []
    found = []
    for match in _URL_RE.finditer(text):
        if match.group(1).lower() == "file":
            continue
        host = _host_from_authority(re.split(r"[/?#]", match.group(2), 1)[0])
        if host not in found:
            found.append(host)
    if strict and not found and text.strip():
        found.append(UNPARSEABLE)
    return found


class _Scan(object):
    """Everything one transcript contributes, from a single pass over its lines."""

    def __init__(self, rel, owner, expected_agent_type):
        self.rel = rel
        self.owner = owner  # "main" or a subagent id
        self.expected = expected_agent_type  # meta agentType (subagents only)
        self.blank_lines = 0
        self.type_counts = Counter()
        self.assistant_keys = Counter()
        self.versions = set()
        self.ts_min = None
        self.ts_max = None
        self.ts_unparsed = 0
        self.turn_models = {}  # message.id -> model, one entry per response
        self.idless_turns = Counter()  # model -> responses without a message.id
        self.synthetic_turns = 0
        self.attributed = False
        self.attribution_value = None
        self.tool_calls = Counter()  # tool name -> distinct tool_use ids
        self.seen_tool_ids = set()
        self.calls = []  # (tool_use id or None, record) for every distinct call
        self.results = {}  # tool_use_id -> any error result seen
        self.denials = []  # (recognised kind, tool_use_id or None)
        self.denied_ids = set()  # every call a denial marker names, whatever its kind
        self.unrecognised_kinds = Counter()
        self.modes = []
        self.mode_entries = 0
        self.mode_unparsed = 0

    # -- derived -------------------------------------------------------------
    def histogram(self):
        hist = Counter(self.turn_models.values())
        hist.update(self.idless_turns)
        return hist

    def turns(self):
        return sum(self.histogram().values()) + self.synthetic_turns

    # -- scanning ------------------------------------------------------------
    def _fail(self, lineno, what):
        raise ParseFailure("%s: line %d: %s" % (self.rel, lineno, what))

    def scan(self, path):
        try:
            fh = open(path, "rb")
        except OSError as exc:
            raise InfraError("cannot read %s (%s)" % (self.rel, exc.strerror or type(exc).__name__))
        with fh:
            lineno = 0
            try:
                for raw in fh:
                    lineno += 1
                    if not raw.strip():
                        self.blank_lines += 1
                        continue
                    try:
                        obj = json.loads(raw)
                    except ValueError:
                        self._fail(lineno, "not valid JSON")
                    self._entry(obj, lineno)
            except OSError as exc:
                raise InfraError("cannot read %s (%s)" % (self.rel, exc.strerror or type(exc).__name__))

    def _entry(self, obj, lineno):
        if not isinstance(obj, dict):
            self.type_counts["<non-object>"] += 1
            return
        etype = obj.get("type")
        self.type_counts[_label(etype)] += 1
        version = obj.get("version")
        if isinstance(version, str):
            self.versions.add(_token(version, "version (%s line %d)" % (self.rel, lineno)))
        stamp = obj.get("timestamp")
        if isinstance(stamp, str):
            dt = _parse_timestamp(stamp)
            if dt is None:
                self.ts_unparsed += 1
            else:
                if self.ts_min is None or dt < self.ts_min:
                    self.ts_min = dt
                if self.ts_max is None or dt > self.ts_max:
                    self.ts_max = dt
        if etype == "assistant":
            self._assistant(obj, lineno)
        elif etype == "user":
            self._user(obj, lineno)
        elif etype == "permission-mode":
            self._permission_mode(obj)

    def _permission_mode(self, obj):
        self.mode_entries += 1
        for key in ("permissionMode", "mode", "permission_mode"):
            value = obj.get(key)
            if isinstance(value, str) and _TOKEN_RE.match(value):
                self.modes.append(value)
                return
        self.mode_unparsed += 1

    def _assistant(self, obj, lineno):
        for key in obj:
            self.assistant_keys[_label(key)] += 1
        message = obj.get("message")
        model = message.get("model") if isinstance(message, dict) else None
        if not isinstance(model, str) or not model:
            self._fail(lineno, "assistant line without message.model")
        model = _token(model, "message.model (%s line %d)" % (self.rel, lineno))
        if model == SYNTHETIC_MODEL:
            self.synthetic_turns += 1  # each synthetic line is one synthetic turn, never in the histogram
        else:
            msg_id = message.get("id")
            if isinstance(msg_id, str) and msg_id:
                previous = self.turn_models.setdefault(msg_id, model)
                if previous != model:
                    self._fail(lineno, "lines of one response (same message.id) disagree on message.model")
            else:
                self.idless_turns[model] += 1
            attribution = obj.get("attributionAgent")
            if attribution is not None and self.expected is not None:
                if attribution != self.expected:
                    self._fail(lineno, "attributionAgent disagrees with the metadata agentType")
                self.attributed = True
                self.attribution_value = attribution
        content = message.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    self._tool_use(block, lineno)

    def _tool_use(self, block, lineno):
        name = block.get("name")
        if not isinstance(name, str) or not name:
            self._fail(lineno, "tool_use without a name")
        name = _token(name, "tool name (%s line %d)" % (self.rel, lineno))
        tid = block.get("id")
        tid = _token(tid, "tool_use id (%s line %d)" % (self.rel, lineno)) if isinstance(tid, str) and tid else None
        if tid is not None:
            if tid in self.seen_tool_ids:
                return  # the same call replayed on another line
            self.seen_tool_ids.add(tid)
        self.tool_calls[name] += 1
        inp = block.get("input")
        inp = inp if isinstance(inp, dict) else {}
        record = {"name": name, "subagent_type": None, "hosts": []}
        if name in DISPATCH_TOOL_NAMES:
            if tid is None:
                self._fail(lineno, "%s tool_use without an id" % name)
            subagent_type = inp.get("subagent_type")
            if isinstance(subagent_type, str) and subagent_type:
                record["subagent_type"] = _token(subagent_type, "subagent_type (%s line %d)" % (self.rel, lineno))
        elif name == "Bash":
            record["hosts"] = _hosts_in_text(inp.get("command"))
        elif name == "WebFetch":
            record["hosts"] = _hosts_in_text(inp.get("url"), strict=True)
        self.calls.append((tid, record))

    def _user(self, obj, lineno):
        message = obj.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        blocks = [b for b in content if isinstance(b, dict) and b.get("type") == "tool_result"] \
            if isinstance(content, list) else []
        ids = []
        for block in blocks:
            tid = block.get("tool_use_id")
            if isinstance(tid, str) and tid:
                tid = _token(tid, "tool_result id (%s line %d)" % (self.rel, lineno))
                ids.append(tid)
                self.results[tid] = self.results.get(tid, False) or block.get("is_error") is True
                if "toolDenialKind" in block:
                    self._denial(block.get("toolDenialKind"), tid)
        # A denial marker on the entry itself (or its toolUseResult) belongs to the
        # entry's only tool_result; with several results the call cannot be named.
        entry_marker = "toolDenialKind" in obj
        marker = obj.get("toolDenialKind")
        result = obj.get("toolUseResult")
        if not entry_marker and isinstance(result, dict) and "toolDenialKind" in result:
            entry_marker = True
            marker = result.get("toolDenialKind")
        if entry_marker:
            self._denial(marker, ids[0] if len(ids) == 1 else None)

    def _denial(self, kind, tid):
        if tid is not None:
            self.results[tid] = True  # a denied call never succeeded
            self.denied_ids.add(tid)
        if isinstance(kind, str) and kind in DENIAL_KINDS:
            self.denials.append((kind, tid))
        else:
            self.unrecognised_kinds[_label(kind)] += 1


class _Instance(object):
    """One subagent instance: its metadata and its scanned transcript."""

    def __init__(self, agent_id, meta_rel, transcript_rel):
        self.agent_id = agent_id
        self.meta_rel = meta_rel
        self.transcript_rel = transcript_rel
        self.agent_type = None
        self.tool_use_id = None
        self.unknown_meta_keys = []
        self.scan = None
        self.skipped = False  # zero turns and an errored dispatch: archived, not listed


def _load_meta(dest_abs, instance):
    path = os.path.join(dest_abs, *instance.meta_rel.split("/"))
    try:
        with open(path, "rb") as fh:
            meta = json.loads(fh.read())
    except OSError as exc:
        raise InfraError("cannot read %s (%s)" % (instance.meta_rel, exc.strerror or type(exc).__name__))
    except ValueError:
        raise ParseFailure("%s: not valid JSON" % instance.meta_rel)
    if not isinstance(meta, dict):
        raise ParseFailure("%s: not a JSON object" % instance.meta_rel)
    for key in ("agentType", "toolUseId"):
        value = meta.get(key)
        if not isinstance(value, str) or not value:
            raise ParseFailure("%s: missing required key %s" % (instance.meta_rel, key))
        _token(value, "%s (%s)" % (key, instance.meta_rel))
    instance.agent_type = meta["agentType"]
    instance.tool_use_id = meta["toolUseId"]
    instance.unknown_meta_keys = sorted(_label(k) for k in meta if k not in KNOWN_META_KEYS)


# =============================================================================
# Analysis: attribution, dispatch topology, egress, denials
# =============================================================================


def _analyse(dest_abs, session_id, copied, roster, marker_version, archived_at, output_dir, warnings, summary):
    """Parse the archived copy against the minimal contract and build the manifest."""
    sub_prefix = session_id + "/subagents/"
    metas = {}
    transcripts = {}
    for rel, _size, _digest in copied:
        if not rel.startswith(sub_prefix):
            continue
        base = rel.rsplit("/", 1)[1]
        if base.endswith(".meta.json"):
            table, key = metas, base[:-len(".meta.json")]
        elif base.endswith(".jsonl"):
            table, key = transcripts, base[:-len(".jsonl")]
        else:
            continue
        agent_id = _token(key[len("agent-"):] if key.startswith("agent-") else key, "subagent file name")
        if agent_id in table:
            raise ParseFailure("two subagent files claim the same id (%s)" % rel)
        table[agent_id] = rel

    instances = {}
    for agent_id in sorted(set(metas) | set(transcripts)):
        if agent_id not in metas:
            raise ParseFailure("subagent transcript without a metadata file (%s)" % transcripts[agent_id])
        inst = _Instance(agent_id, metas[agent_id], transcripts.get(agent_id))
        _load_meta(dest_abs, inst)
        instances[agent_id] = inst

    # -- scan every transcript, main first -----------------------------------
    main_rel = session_id + ".jsonl"
    main_scan = _Scan(main_rel, "main", None)
    main_scan.scan(os.path.join(dest_abs, main_rel))
    scans = [main_scan]
    for inst in instances.values():
        inst.scan = _Scan(inst.transcript_rel or inst.meta_rel, inst.agent_id, inst.agent_type)
        if inst.transcript_rel:
            inst.scan.scan(os.path.join(dest_abs, *inst.transcript_rel.split("/")))
        scans.append(inst.scan)

    # -- global indexes --------------------------------------------------------
    tool_index = {}  # tool_use id -> (owner, record)
    results = {}  # tool_use id -> errored
    denials = []  # (recognised kind, tool_use id or None)
    denied_ids = set()  # calls denied under any kind: they are not observed egress
    unrecognised = Counter()
    for scan in scans:
        for tid, record in scan.calls:
            if tid is None:
                continue
            if tid in tool_index:
                raise ParseFailure("tool_use id appears in more than one transcript; the dispatch topology is ambiguous")
            tool_index[tid] = (scan.owner, record)
        for tid, errored in scan.results.items():
            results[tid] = results.get(tid, False) or errored
        denials.extend(scan.denials)
        denied_ids.update(scan.denied_ids)
        unrecognised.update(scan.unrecognised_kinds)

    # -- main must be attributable ------------------------------------------------
    if main_scan.turns() == 0:
        raise ParseFailure("%s: zero assistant turns" % main_rel)
    if not main_scan.histogram():
        raise ParseFailure("%s: the served-model histogram is empty (every turn is synthetic)" % main_rel)

    # -- instances: topology, then the per-instance parse contract -------------------
    by_tool_use = {}
    for inst in instances.values():
        if inst.tool_use_id in by_tool_use:
            raise ParseFailure("two subagent metadata files reference the same tool_use id")
        by_tool_use[inst.tool_use_id] = inst
        found = tool_index.get(inst.tool_use_id)
        if found is None or found[1]["name"] not in DISPATCH_TOOL_NAMES:
            raise ParseFailure("a subagent metadata file references a tool_use id that no archived transcript "
                               "holds as an Agent or Task call; the dispatch topology cannot be established")

    depths = {"main": 0}

    def depth_of(owner, trail=()):
        if owner in depths:
            return depths[owner]
        if owner in trail:
            raise ParseFailure("the dispatch chain loops back on itself")
        parent_owner = tool_index[instances[owner].tool_use_id][0]
        depths[owner] = depth_of(parent_owner, trail + (owner,)) + 1
        return depths[owner]

    for inst in instances.values():
        scan = inst.scan
        errored = results.get(inst.tool_use_id, False)
        if scan.turns() == 0:
            if not errored:
                raise ParseFailure("%s: zero assistant turns" % (inst.transcript_rel or inst.meta_rel))
            inst.skipped = True  # an errored dispatch that never ran: listed as dispatch-failed only
            continue
        if not scan.histogram():
            raise ParseFailure("%s: the served-model histogram is empty (every turn is synthetic)" % inst.transcript_rel)
        if not scan.attributed:
            raise ParseFailure("%s: no non-synthetic line carries attributionAgent" % inst.transcript_rel)
        depth_of(inst.agent_id)

    # -- dispatches of tachi agents, at any depth -------------------------------------
    dispatches = []
    not_recorded = []
    for tid, (owner, record) in tool_index.items():
        agent = record["subagent_type"]
        if record["name"] not in DISPATCH_TOOL_NAMES or not agent or not agent.startswith(TACHI_PREFIX):
            continue
        errored = results.get(tid, False)
        inst = by_tool_use.get(tid)
        reason = None
        if inst is not None:
            if inst.agent_type != agent:
                raise ParseFailure("a subagent's metadata agentType differs from the dispatched subagent_type")
            status = "dispatch-failed" if inst.skipped else "recorded"
            reason = "dispatch-failed" if inst.skipped else None
        elif errored:
            status, reason = "dispatch-failed", "dispatch-failed"
        else:  # a successful (or unanswered) dispatch with no transcript: the one class that trips TW-B1
            status, reason = "not-recorded", "no-transcript"
        entry = {
            "agent": agent,
            "tool_use_id": tid,
            "dispatched_from": owner,
            "spawn_depth": depth_of(owner) + 1,
            "status": status,
        }
        dispatches.append(entry)
        if reason:
            not_recorded.append({"agent": agent, "tool_use_id": tid, "dispatched_from": owner, "reason": reason})
    dispatches.sort(key=lambda d: (d["spawn_depth"], d["dispatched_from"], d["tool_use_id"]))
    not_recorded.sort(key=lambda d: (d["dispatched_from"], d["tool_use_id"]))

    subagents = []
    for inst in sorted(instances.values(), key=lambda i: (depths.get(i.agent_id, 0), i.agent_id)):
        if inst.skipped:
            continue
        scan = inst.scan
        subagents.append({
            "agent_id": inst.agent_id,
            "agent_type": inst.agent_type,
            "attribution_agent": scan.attribution_value,
            "spawn_depth": depths[inst.agent_id],
            "parent_tool_use_id": inst.tool_use_id,
            "pinned_model": roster.get(inst.agent_type) if inst.agent_type.startswith(TACHI_PREFIX) else None,
            # AOD-SIMPLIFICATION: no requestedModel in v1 -- upgrade: manifest v2 adds a
            # requested_model_histogram and a count of turns whose requested and served models differ.
            "served_model_histogram": dict(scan.histogram()),
            "synthetic_turns": scan.synthetic_turns,
            "turns": scan.turns(),
            "tool_calls_by_tool": dict(scan.tool_calls),
            "unknown_meta_keys": inst.unknown_meta_keys,
        })

    recorded_types = set(s["agent_type"] for s in subagents)
    dispatched_names = set(d["agent"] for d in dispatches)
    not_dispatched = sorted(name for name in roster if name not in recorded_types and name not in dispatched_names)

    # -- egress and denials ---------------------------------------------------------------
    observed = Counter()
    for scan in scans:
        for tid, record in scan.calls:
            if record["name"] in EGRESS_TOOLS and not (tid and tid in denied_ids):
                for host in record["hosts"]:
                    observed[(host, record["name"])] += 1
    denied = Counter()
    for kind, tid in denials:
        record = tool_index[tid][1] if tid in tool_index else None
        for host in (record["hosts"] if record and record["hosts"] else [UNPARSEABLE]):
            denied[(host, kind)] += 1
    unparsed = sum(n for (host, _x), n in observed.items() if host == UNPARSEABLE) \
        + sum(n for (host, _x), n in denied.items() if host == UNPARSEABLE)

    versions = sorted(set().union(*[s.versions for s in scans]), key=_version_key)
    validated = [v for v in versions if v in VALIDATED_DENIAL_VERSIONS]
    detection_ok = bool(versions) and len(validated) == len(versions) and not unrecognised
    stamps = [t for s in scans for t in (s.ts_min, s.ts_max) if t is not None]
    if not stamps:
        raise ParseFailure("no parseable timestamp in any transcript")

    modes = sorted(set(mode for scan in scans for mode in scan.modes))
    artifacts, artifacts_reason = (_hash_artifacts(output_dir, warnings), None) if output_dir \
        else (None, "no-output-dir")

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "tachi_version": marker_version,
        "session_id": session_id,
        "claude_code_versions": versions,
        "started_at": _utc_stamp(min(stamps)),
        "ended_at": _utc_stamp(max(stamps)),
        "archived_at": _utc_stamp(archived_at),
        "transcripts": [{"path": rel, "bytes": size, "sha256": digest} for rel, size, digest in sorted(copied)],
        "main": {
            "served_model_histogram": dict(main_scan.histogram()),
            "turns": main_scan.turns(),
            "synthetic_turns": main_scan.synthetic_turns,
            "tool_calls_by_tool": dict(main_scan.tool_calls),
        },
        "dispatches": dispatches,
        "subagents": subagents,
        "tachi_agents_not_recorded": not_recorded,
        "tachi_agents_not_dispatched": not_dispatched,
        "permission_modes_seen": modes,
        "egress_observed": [{"host": h, "tool": t, "count": n} for (h, t), n in sorted(observed.items())],
        "egress_unparsed_count": unparsed,
        "egress_denied": [{"host": h, "kind": k, "count": n} for (h, k), n in sorted(denied.items())],
        "denial_detection": {
            "status": "validated" if detection_ok else "not-validated",
            "validated_claude_code_versions": validated,
        },
        "artifacts": artifacts,
    }
    if artifacts_reason:
        manifest["artifacts_reason"] = artifacts_reason

    # -- run summary (counts only; nothing here goes into the manifest) ----------------------
    entry_types = Counter()
    assistant_keys = Counter()
    for scan in scans:
        entry_types.update(scan.type_counts)
        assistant_keys.update(scan.assistant_keys)
    summary.update({
        "entry_types": dict(entry_types),
        "unknown_entry_types": dict((t, n) for t, n in entry_types.items() if t not in KNOWN_ENTRY_TYPES),
        "assistant_keys": dict(assistant_keys),
        "unknown_assistant_keys": dict((k, n) for k, n in assistant_keys.items() if k not in KNOWN_ASSISTANT_KEYS),
        "blank_lines": sum(s.blank_lines for s in scans),
        "timestamps_unparsed": sum(s.ts_unparsed for s in scans),
        "permission_mode_entries": sum(s.mode_entries for s in scans),
        "permission_mode_entries_without_a_mode": sum(s.mode_unparsed for s in scans),
        "unrecognised_denial_kinds": dict(unrecognised),
        "denials_seen": len(denials) + sum(unrecognised.values()),
        "dispatch_counts": dict(Counter(d["status"] for d in dispatches)),
        "subagent_instances": len(subagents),
        "non_tachi_instances": sum(1 for s in subagents if not s["agent_type"].startswith(TACHI_PREFIX)),
        "instances_with_unknown_meta_keys": sum(1 for s in subagents if s["unknown_meta_keys"]),
    })
    if not_recorded and any(n["reason"] == "no-transcript" for n in not_recorded):
        warnings.append("%d successful tachi dispatch(es) have no subagent transcript (reason no-transcript): "
                        "attribution is incomplete for them (the TW-B1 condition)"
                        % sum(1 for n in not_recorded if n["reason"] == "no-transcript"))
    if unrecognised:
        warnings.append("denial markers of an unrecognised kind were seen; denial detection is not validated for this run")
    return manifest


def _hash_artifacts(output_dir, warnings):
    out = []
    for root, dnames, fnames in os.walk(output_dir, topdown=True, followlinks=False):
        dnames.sort()
        for dname in list(dnames):
            if os.path.islink(os.path.join(root, dname)):
                warnings.append("a symbolic link in --output-dir was not followed")
                dnames.remove(dname)
        for fname in sorted(fnames):
            full = os.path.join(root, fname)
            try:
                if not stat.S_ISREG(os.lstat(full).st_mode):
                    warnings.append("a non-regular file in --output-dir was skipped")
                    continue
                digest, size = _hash_regular_file(full)
            except OSError as exc:
                raise InfraError("cannot read an artifact in --output-dir (%s)" % (exc.strerror or type(exc).__name__))
            out.append({"path": os.path.relpath(full, output_dir).replace(os.sep, "/"), "bytes": size, "sha256": digest})
    out.sort(key=lambda a: a["path"])
    return out


# =============================================================================
# Final secret scan and manifest write
# =============================================================================


def _secret_env_values():
    values = []
    for name, value in os.environ.items():
        if not _SECRET_NAME_RE.search(name) or len(value) < _SECRET_VALUE_FLOOR:
            continue
        if value.lower() in _NOT_SECRET_LITERALS or re.match(r"[0-9.+\-]+\Z", value):
            continue
        values.append((name, value))
    return values


def _iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield key
            if key != "sha256":  # hash fields are excluded from the scan
                for text in _iter_strings(value):
                    yield text
    elif isinstance(node, (list, tuple)):
        for value in node:
            for text in _iter_strings(value):
                yield text


def _scan_manifest(manifest):
    """Hits as (field, rule). Field names are structural positions, never values."""
    secrets = _secret_env_values()
    hits = set()
    for top, value in manifest.items():
        items = list(enumerate(value)) if isinstance(value, list) else [(None, value)]
        for index, item in items:
            where = top if index is None else "%s[%d]" % (top, index)
            for text in _iter_strings(item):
                for rule, pattern in _KEY_PATTERNS:
                    if pattern.search(text):
                        hits.add((where, rule))
                lowered = text.lower()
                for name, secret in secrets:
                    if secret.lower() in lowered:
                        hits.add((where, "environment variable " + name))
    return sorted(hits)


def _write_manifest(dest_abs, manifest):
    text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    final = os.path.join(dest_abs, MANIFEST_NAME)
    temp = os.path.join(dest_abs, MANIFEST_TMP_NAME)
    try:
        if os.path.lexists(final):
            raise InfraError("run-manifest.json already exists in the destination")
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW | _CLOEXEC, FILE_MODE)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fchmod(fh.fileno(), FILE_MODE)
        os.rename(temp, final)  # a finished manifest appears whole or not at all
    except OSError as exc:
        raise InfraError("cannot write run-manifest.json (%s)" % (exc.strerror or type(exc).__name__))
    return final


# =============================================================================
# Orchestration and CLI
# =============================================================================


def _resolve_destination(args, project_real, session_id, main_path):
    if args.dest:
        return os.path.abspath(os.path.expanduser(args.dest))
    home = os.path.expanduser("~")
    if not os.path.isabs(home):
        raise InfraError("cannot determine the home directory; pass --dest")
    first = _first_timestamp(main_path)
    if first is None:
        raise ParseFailure("%s.jsonl: no parseable timestamp; pass --dest" % session_id)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(project_real)) or "project"
    return os.path.join(home, ".tachi", "runs", name, "%s-%s" % (first.strftime("%Y-%m-%d"), session_id))


def _run(args, summary, warnings):
    if args.session is not None and not _SESSION_ID_RE.match(args.session):
        raise InfraError("--session is not a valid session id")
    if args.live_window_seconds < 0:
        raise InfraError("--live-window-seconds must not be negative")
    project_real = os.path.realpath(os.path.expanduser(args.project_dir or os.getcwd()))
    if not os.path.isdir(project_real):
        raise InfraError("--project-dir is not a directory")
    output_dir = None
    if args.output_dir:
        output_dir = os.path.abspath(os.path.expanduser(args.output_dir))
        if not os.path.isdir(output_dir):
            raise InfraError("--output-dir is not a directory")

    roster = _load_roster(project_real)
    marker_version = _read_version_marker(project_real)
    projects_dir = os.path.join(_config_dir(), "projects")
    if not os.path.isdir(projects_dir):
        raise InfraError("Claude Code projects directory not found; set CLAUDE_CONFIG_DIR if it lives elsewhere")

    main_path = _discover(projects_dir, project_real, args.session, args.latest, warnings)
    session_id = os.path.basename(main_path)[:-len(".jsonl")]
    summary["session_id"] = session_id
    source_files, source_dirs = _enumerate_source(main_path, session_id)

    dest_abs = _resolve_destination(args, project_real, session_id, main_path)
    summary["archive_dir"] = dest_abs
    _check_destination(dest_abs)
    if os.path.lexists(dest_abs):
        if not os.path.isdir(dest_abs):
            raise Refusal("the destination exists and is not a directory")
        if os.listdir(dest_abs):
            _existing_archive_is_identical(dest_abs, source_files)
            summary["status"] = "no-op"
            return
    _check_live(source_files, args.live_window_seconds, args.allow_live)

    _prepare_destination(dest_abs)
    copied = _copy_session(dest_abs, source_files, source_dirs)
    summary["files"] = len(copied)
    summary["bytes"] = sum(size for _rel, size, _digest in copied)

    archived_at = datetime.datetime.now(datetime.timezone.utc)
    manifest = _analyse(dest_abs, session_id, copied, roster, marker_version, archived_at, output_dir, warnings, summary)
    hits = _scan_manifest(manifest)
    if hits:
        raise ParseFailure("final secret scan hit in the manifest (%s); no manifest written"
                           % "; ".join("%s: %s" % hit for hit in hits[:10]))
    summary["manifest"] = _write_manifest(dest_abs, manifest)
    summary["status"] = "archived"
    summary["turns"] = {"main": manifest["main"]["turns"],
                        "subagents": sum(s["turns"] for s in manifest["subagents"])}


def _build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="archive-run-transcripts.py",
        description=("Archive a finished Claude Code session's transcripts verbatim to a location that "
                     "cannot be committed, and write run-manifest.json (feature 391). Run it from a "
                     "plain shell after the session, under the same secret-injection wrapper."),
    )
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--session", metavar="SESSION_ID", help="The session to archive (its main transcript's file stem).")
    which.add_argument("--latest", action="store_true", help="Archive the newest main transcript of this project.")
    parser.add_argument("--project-dir", metavar="PATH", default=None,
                        help="The project (default: the current directory). Transcripts are matched to it by their cwd.")
    parser.add_argument("--dest", metavar="PATH", default=None,
                        help="Destination directory (default: ~/.tachi/runs/<project>/<YYYY-MM-DD>-<session>/).")
    parser.add_argument("--output-dir", metavar="PATH", default=None,
                        help="The run's output directory; the manifest then records a hash of every file in it.")
    parser.add_argument("--allow-live", action="store_true",
                        help="Archive even if a transcript changed within the live window.")
    parser.add_argument("--live-window-seconds", type=int, default=DEFAULT_LIVE_WINDOW_SECONDS, metavar="N",
                        help="A transcript modified within N seconds marks the session live (default %(default)s).")
    parser.add_argument("--json", action="store_true", help="Print the run summary as JSON on stdout.")
    return parser


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)
    summary = {"status": "failed", "session_id": None, "warnings": []}
    warnings = summary["warnings"]
    try:
        _run(args, summary, warnings)
        code = 0
    except ArchiveError as exc:
        summary["status"], summary["reason"], code = exc.status, exc.reason, exc.exit_code
        print("[391] %s" % exc.reason, file=sys.stderr)
    except OSError as exc:
        summary["status"], summary["reason"], code = "infra", "unexpected I/O error (%s)" % (exc.strerror or type(exc).__name__), 2
        print("[391] %s" % summary["reason"], file=sys.stderr)
    except Exception as exc:  # last resort: never echo transcript content in a traceback
        where = traceback.extract_tb(exc.__traceback__)[-1].lineno if exc.__traceback__ else 0
        summary["status"], summary["reason"], code = "infra", "internal error (%s at line %d)" % (type(exc).__name__, where), 2
        print("[391] %s" % summary["reason"], file=sys.stderr)
    for text in warnings:
        print("[391] warning: %s" % text, file=sys.stderr)
    if args.json:
        print(json.dumps(summary, sort_keys=True, indent=2))
    elif code == 0 and summary["status"] == "archived":
        print("[391] archived session %s to %s (%d files, %d bytes)"
              % (summary["session_id"], summary["archive_dir"], summary["files"], summary["bytes"]))
    elif code == 0:
        print("[391] session %s is already archived at %s; nothing to do" % (summary["session_id"], summary["archive_dir"]))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
