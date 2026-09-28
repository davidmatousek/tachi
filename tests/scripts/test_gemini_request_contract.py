"""K14 static contract test (Feature 373, T014) -- A1-A8.

Pins every Gemini `generateContent` request-configuration surface to the
known-good form and the current GA model chain, per
``specs/373-adopter-install-output-fidelity/contracts/gemini-request-and-scaffold.md``
(the normative contract; assertion IDs A1-A8 below correspond to its
"Static contract test" table). Read that contract before changing this file.

Scope: A1-A8 only. A9 and A10 (K15's allow-list / lock-amendment assertions)
land later, in W2, only if K15 ships (tasks.md T029) -- this module
deliberately does not implement them.

``IMAGE_SIZE_RESTORED`` is pinned here from the W0 live smoke render (T002,
``specs/373-adopter-install-output-fidelity/test-results/w0-smoke.md``): all
four ``imageSize: "2K"`` calls returned an image whose long edge was exactly
2x its default-size sibling, at every shipped model x aspect-ratio
combination, so 2K ships. Per the contract, flipping this constant is a
one-commit operation touching the six configuration blocks (this repo's
five ``templates/tachi/infographics/infographic-*.md`` files plus
``executive-architecture.md``), the reference, the adapter copy and this
constant together -- never this constant alone.

``CHAIN`` is the GA replacement pair named in plan.md PD-14 / spec.md
FR-K14.4: ``gemini-3-pro-image`` (primary), then ``gemini-3.1-flash-image``
(fallback). The three retired preview/GA IDs it replaces
(``RETIRED_MODEL_IDS`` below) must not appear anywhere in the distributed
render surface except the reference's single ``Retired models:``
provenance line (A6).

A8 is written against the *template text* (the scaffold contract), not
against the splitter's internals, so it holds regardless of the splitter
implementation. PD-6 hardens the marker-detection in
``scripts/extract-infographic-data.py`` in a parallel W1 worktree (Lane
B1, tasks.md T007); PD-6 itself records that the hardening is byte-neutral
on today's five templates, so ``extract_prompt_scaffold``'s *output* for
these shipped templates is identical before and after that hardening
lands. ``_raw_prompt_fence`` below is a deliberately independent,
from-scratch extraction (not a reuse of the module under test's internal
marker-finding) so the "postamble starts after the marker line" assertion
is checked against the raw template text itself, never against the
extractor's own bookkeeping.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]

# --- W0 pin (T002) -----------------------------------------------------
# See specs/373-adopter-install-output-fidelity/test-results/w0-smoke.md
# "Decisions" #1: all four 2K calls' long edge was exactly 2x the default
# variant's, at every shipped model x ratio combination.
IMAGE_SIZE_RESTORED = True

# plan.md PD-14 / spec.md FR-K14.4 -- primary first, GA replacements only.
CHAIN = ["gemini-3-pro-image", "gemini-3.1-flash-image"]

RETIRED_MODEL_IDS = (
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
)

# Matches a Gemini image-model ID (e.g. "gemini-3-pro-image",
# "gemini-3.1-flash-image-preview") without false-matching an unrelated
# "gemini-*.md" filename reference (those never contain an "-image" segment).
_MODEL_ID_RE = re.compile(r"gemini-[0-9][0-9a-zA-Z.\-]*?-image(?:-preview)?\b")

# generationConfig.imageConfig.aspectRatio's supported set (contract, A2).
SUPPORTED_ASPECT_RATIOS = {
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
}

_TEMPLATE_KEYS = {"model", "fallback_model", "response_modalities", "aspect_ratio", "image_size"}

REFERENCE_PATH = REPO_ROOT / ".claude" / "skills" / "tachi-infographics" / "references" / "gemini-prompt-construction.md"
EXEC_ARCH_PATH = REPO_ROOT / ".claude" / "skills" / "tachi-infographics" / "references" / "executive-architecture.md"
AGENT_PATH = REPO_ROOT / ".claude" / "agents" / "tachi" / "threat-infographic.md"
ADAPTER_PATH = REPO_ROOT / "adapters" / "claude-code" / "agents" / "references" / "infographic-gemini-api.md"
ADAPTER_DIR = ADAPTER_PATH.parent

TEMPLATE_NAMES = ["baseball-card", "maestro-heatmap", "maestro-stack", "risk-funnel", "system-architecture"]
TEMPLATE_PATHS = {
    name: REPO_ROOT / "templates" / "tachi" / "infographics" / f"infographic-{name}.md"
    for name in TEMPLATE_NAMES
}


# =============================================================================
# Shared helpers (deliberately independent of scripts/extract-infographic-data.py
# except where A8 explicitly exercises that module's own public function)
# =============================================================================


def _extract_yaml_fence_after(text: str, heading: str, start: int = 0) -> tuple[dict, int]:
    """Find literal ``heading`` at/after ``start``, then parse the next fenced ```yaml block.

    Returns ``(parsed, heading_line_index)`` -- a 0-based line index so
    callers can assert ordering relative to another marker in the file.
    """
    idx = text.index(heading, start)
    fence = re.search(r"```yaml\s*\n(.*?)\n```", text[idx:], re.DOTALL)
    assert fence, f"no yaml fence found after heading {heading!r} (offset {idx})"
    data = yaml.safe_load(fence.group(1))
    heading_line_index = text.count("\n", 0, idx)
    return data, heading_line_index


def _extract_json_fence_after(text: str, marker: str) -> dict:
    idx = text.index(marker)
    fence = re.search(r"```json\s*\n(.*?)\n```", text[idx:], re.DOTALL)
    assert fence, f"no json fence found after marker {marker!r}"
    return json.loads(fence.group(1))


def _section(text: str, heading: str) -> str:
    """Return a ``#``-heading section's body text, up to the next same-or-higher heading."""
    pattern = re.compile(rf"^(#{{1,6}})\s+{re.escape(heading)}\s*$", re.MULTILINE)
    m = pattern.search(text)
    assert m, f"heading {heading!r} not found"
    level = len(m.group(1))
    rest = text[m.end():]
    nxt = re.search(rf"^#{{1,{level}}}\s+", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def _markdown_table_rows(text: str) -> list:
    """Parse a GFM table's data rows (drops the header row and the ``---`` separator)."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("|")]
    all_rows = [[cell.strip() for cell in ln.strip("|").split("|")] for ln in lines]
    data_rows = []
    past_separator = False
    for row in all_rows:
        if all(re.fullmatch(r":?-{1,}:?", cell) for cell in row):
            past_separator = True
            continue
        if past_separator:
            data_rows.append(row)
    return data_rows


def _table_after(text: str, marker: str) -> list:
    return _markdown_table_rows(text[text.index(marker):])


def _contains_key(obj: Any, key: str) -> bool:
    """Recursively search a parsed JSON/YAML structure for a dict key."""
    if isinstance(obj, dict):
        if key in obj:
            return True
        return any(_contains_key(v, key) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_key(v, key) for v in obj)
    return False


def _model_ids_in(text: str) -> list:
    return _MODEL_ID_RE.findall(text)


def _raw_prompt_fence(template_name: str) -> str:
    """Independently extract a template's raw Gemini Prompt Template fenced block.

    Deliberately reimplemented rather than calling
    ``extract_prompt_scaffold`` -- A8's "postamble starts after the marker
    line" assertion is checked against the template TEXT itself (the
    scaffold contract), so it holds whether or not PD-6's splitter
    hardening (tasks.md T007, a parallel W1 worktree) has landed yet.
    """
    text = TEMPLATE_PATHS[template_name].read_text(encoding="utf-8")
    heading = re.search(r"^#{1,4}\s+.*[Gg]emini.*[Pp]rompt.*$", text, re.MULTILINE)
    assert heading, f"no Gemini Prompt heading found in {template_name}"
    fence = re.search(r"```\s*\n(.*?)\n```", text[heading.end():], re.DOTALL)
    assert fence, f"no fenced prompt block found after the Gemini Prompt heading in {template_name}"
    return fence.group(1)


def _assert_template_block_shape(data: dict, *, aspect_ratio: str) -> None:
    """Shared A2/A3 shape assertions ("A2's key rules")."""
    assert set(data.keys()) <= _TEMPLATE_KEYS, f"unexpected keys: {set(data.keys()) - _TEMPLATE_KEYS}"
    assert data["model"] == CHAIN[0]
    assert data["fallback_model"] == CHAIN[1]
    assert data["response_modalities"] == ["TEXT", "IMAGE"]
    assert data["aspect_ratio"] == aspect_ratio
    assert data["aspect_ratio"] in SUPPORTED_ASPECT_RATIOS
    if IMAGE_SIZE_RESTORED:
        assert data.get("image_size") == "2K"
    else:
        assert "image_size" not in data


# =============================================================================
# A1 -- the reference request body
# =============================================================================


class TestA1ReferenceRequestBody:
    def test_body_shape_and_forbidden_keys(self):
        text = REFERENCE_PATH.read_text(encoding="utf-8")
        body = _extract_json_fence_after(text, "**Request Body**:")
        gen_config = body["generationConfig"]

        assert gen_config["responseModalities"] == ["TEXT", "IMAGE"]
        assert "aspectRatio" in gen_config["imageConfig"]

        # Forbidden shapes (contract "Forbidden" list).
        assert "aspectRatio" not in gen_config
        assert "imageSize" not in gen_config
        assert not _contains_key(body, "resolution")
        assert not _contains_key(body, "responseFormat")

        if IMAGE_SIZE_RESTORED:
            assert gen_config["imageConfig"].get("imageSize") == "2K"
        else:
            assert "imageSize" not in gen_config["imageConfig"]

    def test_no_resolution_anywhere_in_file(self):
        text = REFERENCE_PATH.read_text(encoding="utf-8")
        assert "resolution" not in text.lower()

    def test_response_parsing_names_camel_case_keys(self):
        text = REFERENCE_PATH.read_text(encoding="utf-8")
        section = _section(text, "Response Parsing")
        assert "inlineData" in section
        assert "mimeType" in section


# =============================================================================
# A2 -- the five template blocks
# =============================================================================


class TestA2TemplateBlocks:
    @pytest.mark.parametrize("name", TEMPLATE_NAMES)
    def test_block_shape(self, name):
        text = TEMPLATE_PATHS[name].read_text(encoding="utf-8")
        data, _ = _extract_yaml_fence_after(text, "## Gemini API Configuration")
        _assert_template_block_shape(data, aspect_ratio="16:9")


# =============================================================================
# A3 -- the executive-architecture block, after the END marker
# =============================================================================


class TestA3ExecutiveArchitectureBlock:
    def test_block_after_end_marker_is_portrait(self):
        text = EXEC_ARCH_PATH.read_text(encoding="utf-8")
        end_marker = "=== END VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ==="
        end_idx = text.index(end_marker)
        end_line = text.count("\n", 0, end_idx)

        data, heading_line = _extract_yaml_fence_after(text, "## Gemini API Configuration", start=end_idx)
        assert heading_line > end_line, "the configuration block must follow the END marker line"

        _assert_template_block_shape(data, aspect_ratio="3:4")

        width, height = (int(part) for part in data["aspect_ratio"].split(":"))
        assert width < height, "3:4 must be portrait (width < height)"


# =============================================================================
# A4 -- the shipped adapter copy
# =============================================================================


class TestA4AdapterCopy:
    def test_body_conforms_to_a1(self):
        text = ADAPTER_PATH.read_text(encoding="utf-8")
        body = _extract_json_fence_after(text, "**Request Body**:")
        gen_config = body["generationConfig"]

        assert gen_config["responseModalities"] == ["TEXT", "IMAGE"]
        assert "aspectRatio" in gen_config["imageConfig"]
        assert "aspectRatio" not in gen_config
        assert "imageSize" not in gen_config
        assert not _contains_key(body, "resolution")
        assert not _contains_key(body, "responseFormat")

        if IMAGE_SIZE_RESTORED:
            assert gen_config["imageConfig"].get("imageSize") == "2K"
        else:
            assert "imageSize" not in gen_config["imageConfig"]

    def test_no_resolution_anywhere_in_file(self):
        text = ADAPTER_PATH.read_text(encoding="utf-8")
        assert "resolution" not in text.lower()

    def test_names_only_chain_models_primary_first(self):
        text = ADAPTER_PATH.read_text(encoding="utf-8")
        found = _model_ids_in(text)
        assert found, "expected at least one model ID in the adapter copy"
        assert set(found) <= set(CHAIN), f"unexpected model IDs: {set(found) - set(CHAIN)}"
        assert set(CHAIN) <= set(found), "adapter copy must name every chain model"
        assert text.index(CHAIN[0]) < text.index(CHAIN[1]), "primary model must appear first"

    def test_response_parsing_names_inline_data(self):
        text = ADAPTER_PATH.read_text(encoding="utf-8")
        section = _section(text, "Response Parsing")
        assert "inlineData" in section


# =============================================================================
# A5 -- the key -> field table and the reference's chain / default model
# =============================================================================


_KEY_FIELD_EXPECTATIONS = {
    "model": "models/{model}:generateContent",
    "fallback_model": "the next model",
    "response_modalities": "generationConfig.responseModalities",
    "aspect_ratio": "generationConfig.imageConfig.aspectRatio",
    "image_size": "generationConfig.imageConfig.imageSize",
}


class TestA5KeyFieldTableAndChain:
    def test_key_field_table_present_with_every_row(self):
        text = REFERENCE_PATH.read_text(encoding="utf-8")
        rows = _table_after(text, "Key → field table")
        mapping = {row[0].strip("`"): row[1] for row in rows if row}
        for key, expected_substring in _KEY_FIELD_EXPECTATIONS.items():
            assert key in mapping, f"missing key->field row for {key!r}"
            assert expected_substring in mapping[key], (
                f"row for {key!r} does not map to {expected_substring!r}: {mapping[key]!r}"
            )

    def test_reference_chain_and_default_model(self):
        text = REFERENCE_PATH.read_text(encoding="utf-8")
        data, _ = _extract_yaml_fence_after(text, "## Gemini API Configuration")
        config = data["gemini_config"]
        assert config["chain"] == CHAIN
        assert config["default_model"] == CHAIN[0]


# =============================================================================
# A6 -- no retired model ID anywhere in the surface, except one reference line
# =============================================================================


def _surface_files() -> list:
    files = []
    files.extend(sorted((REPO_ROOT / "templates" / "tachi" / "infographics").glob("*.md")))
    files.extend(sorted((REPO_ROOT / ".claude" / "skills" / "tachi-infographics").rglob("*.md")))
    files.append(AGENT_PATH)
    files.extend(sorted(ADAPTER_DIR.glob("*.md")))
    return files


SURFACE_FILES = _surface_files()


class TestA6NoRetiredModelIDs:
    @pytest.mark.parametrize(
        "path", SURFACE_FILES, ids=[str(p.relative_to(REPO_ROOT)) for p in SURFACE_FILES]
    )
    def test_no_retired_ids_outside_the_single_exception(self, path):
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for retired_id in RETIRED_MODEL_IDS:
                if retired_id not in line:
                    continue
                is_exempt = path == REFERENCE_PATH and line.strip().startswith("Retired models:")
                assert is_exempt, (
                    f"{path.relative_to(REPO_ROOT)}:{lineno} names retired model "
                    f"{retired_id!r} outside the single permitted 'Retired models:' line"
                )

    def test_reference_has_exactly_one_retired_models_line(self):
        text = REFERENCE_PATH.read_text(encoding="utf-8")
        matches = [ln for ln in text.splitlines() if ln.strip().startswith("Retired models:")]
        assert len(matches) == 1
        for retired_id in RETIRED_MODEL_IDS:
            assert retired_id in matches[0]


# =============================================================================
# A7 -- the agent's mapping instruction, executive-architecture.md pointer,
# and the error table's 400 / 404-403 / exhausted-chain / catch-all rows
# =============================================================================


class TestA7AgentMappingAndErrorTable:
    def test_mapping_instruction_and_executive_architecture_pointer(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        assert "Request Configuration Mapping" in text
        section = _section(text, "Request Configuration Mapping")
        assert "executive-architecture.md" in section
        assert "never fall back" in section.lower()
        assert "key → field table" in section.lower() or "key-to-field table" in section.lower()

    def test_skill_reference_table_points_to_executive_architecture(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        section = _section(text, "Skill References")
        assert "executive-architecture.md" in section

    def test_error_table_has_400_row(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        section = _section(text, "Error Handling & Graceful Degradation")
        assert "400" in section
        assert "Not walked" in section
        assert "Error" in section

    def test_error_table_has_404_403_walked_row(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        section = _section(text, "Error Handling & Graceful Degradation")
        assert "404" in section
        assert "403" in section
        assert "Walked" in section

    def test_error_table_has_exhausted_chain_row(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        section = _section(text, "Error Handling & Graceful Degradation")
        assert "exhausted" in section.lower()
        assert "each model tried" in section.lower()

    def test_error_table_has_catch_all_row(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        section = _section(text, "Error Handling & Graceful Degradation")
        assert "5xx" in section
        assert "no image part" in section.lower()

    def test_429_hint_to_reorder_models(self):
        text = AGENT_PATH.read_text(encoding="utf-8")
        section = _section(text, "Error Handling & Graceful Degradation")
        assert "429" in section
        assert "fallback_model" in section or "`model`" in section


# =============================================================================
# A8 -- strengthened scaffold boundaries, for the five scaffolded templates
# =============================================================================


class TestA8ScaffoldBoundaries:
    @pytest.mark.parametrize("name", TEMPLATE_NAMES)
    def test_scaffold_found_and_bounded(self, name, extract_infographic_data):
        scaffold = extract_infographic_data.extract_prompt_scaffold(name, repo_root=REPO_ROOT)
        assert scaffold["found"] is True

        preamble = scaffold["preamble"]
        postamble = scaffold["postamble"]

        preamble_last_line = preamble.rstrip("\n").splitlines()[-1]
        assert preamble_last_line.startswith("DATA CONTENT (render this")
        assert "STYLING DIRECTIVES" in preamble

        postamble_first_line = postamble.splitlines()[0]
        assert re.match(r'^FOOTER[^\n]*: "', postamble_first_line), (
            f"postamble's first line does not match ^FOOTER...: \" : {postamble_first_line!r}"
        )
        assert "STYLING DIRECTIVES" not in postamble
        assert "DATA CONTENT (render this" not in postamble

        # The postamble's start must lie after the marker line -- checked
        # against the raw template TEXT (see _raw_prompt_fence's docstring),
        # not against the extractor's own internal bookkeeping.
        raw = _raw_prompt_fence(name)
        marker_idx = raw.index("DATA CONTENT (render this")
        postamble_idx = raw.index(postamble_first_line)
        assert postamble_idx > marker_idx

    @pytest.mark.parametrize("name", TEMPLATE_NAMES)
    def test_exactly_one_line_start_footer_after_marker(self, name):
        """N8 (tasks.md T014): exactly one line-start FOOTER after the marker line."""
        raw = _raw_prompt_fence(name)
        lines = raw.split("\n")
        marker_line_idx = next(i for i, ln in enumerate(lines) if ln.startswith("DATA CONTENT (render this"))
        footer_line_count = sum(1 for ln in lines[marker_line_idx + 1:] if ln.startswith("FOOTER"))
        assert footer_line_count == 1
