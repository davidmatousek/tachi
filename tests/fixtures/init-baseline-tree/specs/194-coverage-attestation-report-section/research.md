# Research Summary: Coverage Attestation Report Section (Feature 194)

**Date**: 2026-04-18
**PRD**: [docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md](../../docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md)
**Purpose**: Ground the spec in verified file locations, extract exact code shapes to mirror, and surface architectural precedents.

---

## Knowledge Base Findings

Authoritative KB entries for this feature (from `docs/INSTITUTIONAL_KNOWLEDGE.md`):

- **KB-031 Phase-Insertion Pattern** (lines 643-662) — Direct architectural precedent. Feature 141 added a new Typst page + `has-attack-chains` boolean + conditional section with 5 baselines byte-identical. F-B's `has-source-attribution` mirrors this shape exactly. Recipe: (1) schema/contract, (2) parser/aggregator, (3) conditional gate boolean, (4) downstream conditional sections.
- **KB-034 Byte-Identical Baselines + Deterministic Timestamps** (lines 712-731) — Governs SC-2 regression posture. `SOURCE_DATE_EPOCH=1700000000` (ADR-021). Rule: do NOT change the epoch constant.
- **KB-023 Centralized Parser Module** (lines 459-478) — F-A2 already added `source_attribution` extraction to `parse_threats_findings` at line 796. F-B reads from the parser, aggregates in `extract-report-data.py`.
- **PAT-013 Typst Hub-First Architecture** (lines 264-277) — Theme/shared tokens stabilized (Feature 060). F-B reuses existing theme; no foundation phase needed. `main.typ:88-108` default-guard pattern is the canonical idiom.
- **KB-022 Template Parity** (lines 436-455) — Feature 091 (maestro-findings.typ) and Feature 141 (attack-chain.typ) followed single-export-function Typst pattern; F-B mirrors.
- **KB-029 Silent Dead-Code Fallbacks** (lines 597-616) — CAUTION: do NOT add a "graceful degradation" text-fallback for missing taxonomy data. Per Feature 130 lesson: silent fallbacks mask correctness regressions. `has-source-attribution: false` → omit entirely (already PRD-correct).
- **KB-036 Dual-Commit Proposed → Accepted ADR Governance** (lines 758-777) — ADR-029 follows F-A1 / F-A2 cadence: Proposed at schema-lock, Accepted at pre-merge with `<pending-post-merge-fill>`, post-merge SHA fill commit directly to main.
- **PAT-017 Output Template Parity** (lines 330-347) — Typst data contract ↔ `main.typ` default-guards ↔ aggregator output triple must stay in sync.

**No past incidents** of new Typst pages breaking byte-identity. Features 091, 112, 128, 141, 142 all shipped cleanly with the `has-X` gate pattern.

---

## Codebase Analysis (File:Line Citations — Verified)

### Feature 141 `has-attack-chains` — Direct Architectural Precedent

- **Boolean emission** — `scripts/extract-report-data.py:1426`:
  ```python
  lines.append(f"#let has-attack-chains = {_typst_bool(data.get('has_attack_chains', False))}")
  ```
- **Default-value guard** — `templates/tachi/security-report/main.typ:103`:
  ```typst
  #let has-attack-chains = if has-attack-chains != none { has-attack-chains } else { false }
  #let attack-chains = if attack-chains != none { attack-chains } else { () }
  ```
- **Conditional inclusion block** — `main.typ:246`:
  ```typst
  #if has-attack-chains and attack-chains.len() > 0 {
    section-divider("Cross-Layer Attack Chain Analysis", classification: classification)
    ...
  }
  ```
- **Unconditional import** — `main.typ:47`:
  ```typst
  #import "attack-chain.typ": attack-chain-page
  ```

### Feature 128 MAESTRO Precedent — New-Page + Boolean

- **Boolean emission** — `extract-report-data.py:1362`:
  ```python
  lines.append(f"#let has-maestro-data = {_typst_bool(data.get('has_maestro_data', False))}")
  ```
- **Defaults block** — `main.typ:89` and import at `:43`.

### Placement Target Verified

- `main.typ:348` — End of MAESTRO-findings block (confirmed opening of `#if has-maestro-data`).
- `main.typ:398` — Start of compensating-controls block (confirmed `#if has-compensating-controls`).
- F-B conditional inclusion must land between these two blocks (Q7 resolution).

### F-A2 Upstream Data Contract Verified

- **Field present** — `schemas/finding.yaml:212`: `source_attribution:` field (list[record], schema v1.5).
- **Parser round-trip** — `scripts/tachi_parsers.py:796`: `parse_threats_findings` stores `source_attribution` records on finding dict when present.

### F-A1 Denominator Authority Verified

Direct Python count via `yaml.safe_load` on each framework YAML (matches PRD claims):

| Framework | Top-level records | PRD claim | Match |
|-----------|-------------------|-----------|-------|
| OWASP | 60 | 60 | ✓ |
| MITRE ATT&CK | 38 | 38 | ✓ |
| MITRE ATLAS | 12 | 12 | ✓ |
| NIST AI RMF | 72 | 72 | ✓ |
| CWE | 53 | 53 | ✓ |
| **Total** | **235** | **235** | ✓ |

PRD's Q2-A trivial resolution is correct. Q-EXPLORE-A1 finding of 887 was a line-count artifact, not YAML record count.

### Backward-Compatibility Harness

`tests/scripts/test_backward_compatibility.py:38-45` — 5 non-agentic baselines:
- `web-app`, `microservices`, `ascii-web-api`, `free-text-microservice`, `maestro-reference`

6th baseline `mermaid-agentic-app` intentionally excluded per line 16. `agentic-app` is the 7th example (the re-baselineable one per Feature 128 convention).

**Discrepancy with PRD**: PRD lists the 5 baselines as (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`). Harness actually has `maestro-reference` instead of `mermaid-agentic-app`. This is a PRD drift to note during planning — spec should reference the harness directly rather than hardcoding the list.

---

## Architecture Constraints

Relevant ADRs (cross-referenced from PRD):

- **ADR-021** — `SOURCE_DATE_EPOCH=1700000000` byte-determinism. SC-2 gate depends on this.
- **ADR-022** — CLI-prerequisite fail-loud pattern. Aggregator malformed-YAML handling follows this (fail loud, not silent).
- **ADR-023** — Skill-references pattern, 22-file zero-edit invariant. Preserved by F-B (no agent / skill edits).
- **ADR-027** (Feature 180, F-A1) — Taxonomy crosswalk schema. Source of denominator YAMLs.
- **ADR-028** (Feature 189, F-A2) — `source_attribution` schema contract + 5-value enum + 3-value `relationship` enum. Upstream dependency.
- **ADR-029** (this feature) — To be authored Day 1, transitioned Accepted Day 4.

Touch points enumerated by precedent audit:

1. New file — `templates/tachi/security-report/coverage-attestation.typ`
2. New function — `scripts/extract-report-data.py` (aggregator + boolean emission)
3. 3 coordinated edits — `templates/tachi/security-report/main.typ` (default guard, import, conditional block)
4. New tests — `tests/scripts/` (fixtures + aggregator unit tests + pagination smoke)
5. New ADR — `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`

No schema changes. No agent edits. No skill edits.

---

## Industry Research

**Frame**: F-B is tachi-internal and follows internal precedent patterns (Feature 141, Feature 128). No external/industry research surfaced novel concerns — this is an additive PDF-section feature using already-stabilized architectural patterns.

**Adjacent references** (for author context, not implementation guidance):
- OWASP Coverage Matrix patterns (compliance-tooling convention): per-framework coverage percentages with Gap classification are standard in tools like Snyk, Veracode, Semgrep Pro. F-B's 3-value (Covered/Partial/Gap) classification follows this convention.
- CSA MAESTRO threat umbrella: F-B is orthogonal to MAESTRO (MAESTRO renders per-layer findings; F-B renders per-framework coverage).

---

## Recommendations for Spec

1. **Use precedent line citations verbatim** — all line numbers in the PRD (main.typ:103, :246, :348, :398, extract-report-data.py:1362, :1426, tachi_parsers.py:796) are verified. Spec can trust them.

2. **Mirror Feature 141 code shape** for the `has-X` pattern — default-guard idiom at `main.typ:103`, conditional block at `:246`, boolean emission at `extract-report-data.py:1426`. The spec should require byte-identical pattern structure (not just semantic equivalence).

3. **SC-2 baseline list reference** — spec should reference `tests/scripts/test_backward_compatibility.py:38-45` as the authoritative baseline list, not hardcode a list (the harness has `maestro-reference` not `mermaid-agentic-app` per PRD v1.1 drift).

4. **Denominator computation point** — spec should specify that `yaml_record_count` is computed ONCE per framework at data-extraction time and pinned in the emitted Typst contract (avoids re-reads during Typst rendering, preserves determinism).

5. **Scope boundaries are P0** — the 22-file zero-edit invariant + zero-crosswalk-JOIN + zero-schema-change constraints are BLOCKER-level per ADR-023 / ADR-028 lineage. Spec should hoist these to explicit "Won't Have" scope lines.

6. **Test structure** — 3 fixtures (empty / one-primary / multi-mixed) per PRD FR-6, with a Day 3 pagination smoke on 100-finding × 5-framework synthetic fixture. Architect's R1/R8 pagination risks mitigate through this smoke.

7. **Absence-means-zero-output** — KB-029 cautionary tale means spec should explicitly forbid any "section unavailable" placeholder text in the absent case. The section is omitted entirely or it renders fully populated; no middle ground.

8. **Q5 deferral is OK for spec** — ux-ui-designer memo Day 2 AM is acceptable spec-time; the visual treatment is an implementation detail the spec can constrain (WCAG AA color-blind accessible, color + icon combo) without specifying the exact palette.
