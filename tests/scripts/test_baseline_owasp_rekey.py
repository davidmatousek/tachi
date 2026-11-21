"""Fix 397 (N5) — carried-forward OWASP LLM 2025 codes are re-keyed to the 2026 edition.

Phase 1a carries baseline findings forward. It used to copy `owasp_ref` verbatim, so a
baseline written before the 2026 cutover (F-362, ADR-048) re-emitted `LLM<NN>:2025` tokens
beside NEW findings' `:2026` tokens. The 2025 -> 2026 change is a permutation, so the same
number then named two different categories in one table.

The orchestrator applies the fix by following prose, so this module pins what a mistake in
that prose would silently break:
  * the re-key table in `baseline-correlation.md` is exactly the 2025 -> 2026 permutation
    published with F-362, and its category names match `schemas/taxonomy/owasp.yaml`;
  * the structural-validation check in `output-schemas.md` uses a pattern that flags every
    2025 code and passes 2026, ASI and MCP tokens;
  * the rule sits next to the `maestro_layer` rule, covers UNCHANGED, UPDATED and RESOLVED
    findings, and keeps the delta status;
  * applying the documented table to a synthetic baseline AI table leaves no 2025 token,
    keeps every other token and the rest of each cell, and is idempotent.

Synthetic rows only. Stdlib + pytest (+ the suite's PyYAML). Gated in
`.github/workflows/tachi-pytest.yml`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / ".claude" / "skills" / "tachi-orchestration" / "references"
CORRELATION = REFERENCES / "baseline-correlation.md"
OUTPUT_SCHEMAS = REFERENCES / "output-schemas.md"
OWASP_CATALOG = ROOT / "schemas" / "taxonomy" / "owasp.yaml"

# The 2025 -> 2026 permutation as published with F-362 (CHANGELOG "Feature 362" migration
# table; ADR-048). Written out here as independent ground truth, not parsed from the file
# under test.
F362_SIGMA = {
    "LLM01": "LLM01", "LLM02": "LLM02", "LLM03": "LLM04", "LLM04": "LLM05", "LLM05": "LLM10",
    "LLM06": "LLM03", "LLM07": "LLM08", "LLM08": "LLM09", "LLM09": "LLM07", "LLM10": "LLM06",
}
VALIDATION_PATTERN = r"LLM\d{2}:2025"  # as written in the output-schemas.md check
TOKEN_2025 = re.compile(r"LLM(\d{2}):2025")
ROW_RE = re.compile(r"^\| `(LLM\d{2}):2025` \| `(LLM\d{2}):2026` \| ([^|]+?) \|$", re.M)

SYNTHETIC_BASELINE_AI_TABLE = """\
| ID | Status | Component | MAESTRO Layer | Agentic Pattern | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|-----------------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | UNCHANGED | Chat Service | L1 — Foundation Model | — | Synthetic: hidden instructions disclosed on request | OWASP LLM07:2025 | MEDIUM | HIGH | High | Synthetic mitigation |
| LLM-2 | UPDATED | Chat Service | L1 — Foundation Model | — | Synthetic: unchecked factual claims reach users | OWASP LLM09:2025 | MEDIUM | MEDIUM | Medium | Synthetic mitigation |
| LLM-3 | NEW | Chat Service | L1 — Foundation Model | — | Synthetic: fabricated citations in answers | OWASP LLM07:2026 | MEDIUM | MEDIUM | Medium | Synthetic mitigation |
| AG-1 | UNCHANGED | Planner Agent | L3 — Agent Framework | — | Synthetic: agent acts beyond its mandate | OWASP LLM06:2025, ASI-01 | HIGH | HIGH | Critical | Synthetic mitigation |
| AG-2 | UNCHANGED | Tool Gateway | L3 — Agent Framework | — | Synthetic: every tool exposed to every client | MCP-03 | MEDIUM | HIGH | High | Synthetic mitigation |
| AG-3 | NEW | Planner Agent | L3 — Agent Framework | — | Synthetic: goal hijack through retrieved content | ASI-01, ASI-10 | MEDIUM | HIGH | High | Synthetic mitigation |
"""


def _rekey_table() -> list[tuple[str, str, str]]:
    return ROW_RE.findall(CORRELATION.read_text(encoding="utf-8"))


def _rekey(cell: str, table: dict[str, str]) -> str:
    """Replace each `LLM<NN>:2025` token with its 2026 token; leave the rest of the cell."""
    return TOKEN_2025.sub(lambda m: f"{table['LLM' + m.group(1)]}:2026", cell)


def _rows(table_md: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.strip().strip("|").split("|") for line in table_md.strip().splitlines()]
    header = [cell.strip() for cell in lines[0]]
    return header, [[cell.strip() for cell in line] for line in lines[2:]]


def _editions_by_code(cells: list[str]) -> dict[str, set[str]]:
    seen: dict[str, set[str]] = {}
    for cell in cells:
        for code, year in re.findall(r"(LLM\d{2}):(\d{4})", cell):
            seen.setdefault(code, set()).add(year)
    return seen


def test_rekey_table_is_the_f362_permutation() -> None:
    assert sorted(F362_SIGMA.values()) == sorted(F362_SIGMA)  # ground truth is a bijection
    rows = _rekey_table()
    assert len(rows) == 10, f"expected 10 re-key rows in {CORRELATION.name}, found {len(rows)}"
    assert {old: new for old, new, _ in rows} == F362_SIGMA


def test_rekey_table_names_match_the_owasp_catalog() -> None:
    records = yaml.safe_load(OWASP_CATALOG.read_text(encoding="utf-8"))
    assert isinstance(records, list)
    names = {r["id"]: r["name"] for r in records if re.fullmatch(r"LLM\d{2}", str(r.get("id")))}
    assert len(names) == 10
    rows = _rekey_table()
    assert len(rows) == 10, f"expected 10 re-key rows in {CORRELATION.name}, found {len(rows)}"
    for old, new, name in rows:
        assert name == names[new], f"{old}:2025 -> {new}:2026 names {name!r}, catalog says {names[new]!r}"


def test_rekey_rule_sits_next_to_the_maestro_layer_rule() -> None:
    text = CORRELATION.read_text(encoding="utf-8")
    delta = text.split("## Delta Classification", 1)[1].split("### Sequential ID Assignment", 1)[0]
    assert "**MAESTRO layer handling**" in delta
    assert "**OWASP edition re-keying**" in delta
    assert "`UNCHANGED`, `UPDATED` and `RESOLVED`" in delta
    assert "never changes a finding's delta status" in delta


def test_validation_check_rejects_2025_tokens_in_the_ai_tables() -> None:
    checks = [line for line in OUTPUT_SCHEMAS.read_text(encoding="utf-8").splitlines()
              if line.startswith("- [ ]") and f"`{VALIDATION_PATTERN}`" in line]
    assert len(checks) == 1, "expected exactly one structural-validation check for 2025 tokens"
    assert "OWASP Reference" in checks[0] and "AI tables" in checks[0]
    assert "baseline-correlation.md" in checks[0]


@pytest.mark.parametrize("cell", [f"OWASP LLM{n:02d}:2025" for n in range(1, 11)]
                         + ["LLM07:2025", "OWASP LLM06:2025, ASI-01", "ASI-02, OWASP LLM10:2025"])
def test_validation_pattern_flags_every_2025_code(cell: str) -> None:
    assert re.search(VALIDATION_PATTERN, cell)


@pytest.mark.parametrize("cell", [f"OWASP LLM{n:02d}:2026" for n in range(1, 11)]
                         + ["ASI-01", "ASI-01, ASI-10", "MCP-03", "OWASP LLM03:2026, ASI-01"])
def test_validation_pattern_passes_2026_asi_and_mcp_tokens(cell: str) -> None:
    assert not re.search(VALIDATION_PATTERN, cell)


def test_rekeying_a_synthetic_baseline_table() -> None:
    table = {old: new for old, new, _ in _rekey_table()}
    assert len(table) == 10, f"expected 10 re-key rows in {CORRELATION.name}, found {len(table)}"
    header, rows = _rows(SYNTHETIC_BASELINE_AI_TABLE)
    ref = header.index("OWASP Reference")
    before = [row[ref] for row in rows]
    # The synthetic table reproduces the defect: LLM07 appears in two editions.
    assert _editions_by_code(before)["LLM07"] == {"2025", "2026"}

    after = [_rekey(cell, table) for cell in before]

    assert not any(re.search(VALIDATION_PATTERN, cell) for cell in after)
    assert after == [
        "OWASP LLM08:2026",           # System Prompt Leakage (2025) -> Hidden Context Exposure
        "OWASP LLM07:2026",           # Misinformation keeps its category, takes its 2026 code
        "OWASP LLM07:2026",           # already 2026: unchanged
        "OWASP LLM03:2026, ASI-01",   # only the LLM token changes; the ASI token and comma stay
        "MCP-03",                     # MCP token: unchanged
        "ASI-01, ASI-10",             # ASI tokens: unchanged
    ]
    assert all(years == {"2026"} for years in _editions_by_code(after).values())
    assert [_rekey(cell, table) for cell in after] == after  # idempotent
