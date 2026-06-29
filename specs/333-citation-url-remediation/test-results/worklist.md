# F-333 Citation-URL Remediation — Work-List (T001)

> **Status**: SETUP — mapping doc only. NO catalog edits in this file.
> **Generated**: 2026-06-29 (T001)
> **Scope**: Dead-URL classes surfaced by the #183 link-rot monitor's first live sweep (41 findings, #332).

---

## Per-Class Work-List

| Class | Source File | Distinct URLs / IDs | Total Occurrences | Resolution Strategy |
|-------|------------|---------------------|-------------------|---------------------|
| ATLAS (US-1) | `schemas/taxonomy/mitre-atlas.yaml` | 36 distinct `AML.Txxxx` technique IDs | 36 `url:` refs | Host-scoped re-classify: add `_HOST_STATUS_OVERRIDES = {"atlas.mitre.org": {404: Verdict.NEEDS_REVIEW}}` in `scripts/check-citation-urls.py:_verdict_for_status`. Zero data edits to YAML. |
| ATLAS (US-1) | `schemas/taxonomy/crosswalk.yaml` | 96 distinct `atlas.mitre.org/techniques/` citation refs | 96 `citation:` refs | Covered by the same host-scoped override above — same host key. Zero data edits. |
| NIST DOI (US-2) | `schemas/taxonomy/nist-ai-rmf.yaml` | 1 distinct dead DOI: `https://doi.org/10.6028/NIST.AI.100-1` | 73 `url:` refs (all records share this one URL) | Single URL replacement cascades to all 73 records. Re-point to the live NIST PDF direct URL (to be confirmed during T006 architect fork). |
| OWASP (US-3) | `schemas/taxonomy/owasp.yaml` | 11 distinct `genai.owasp.org` URLs (10 `llm0X2025-*` year-suffixed + 1 Agentic page `owasp-top-10-for-agentic-applications-for-2026`). `llm01-prompt-injection/` is LIVE — regression guard, leave unchanged. | 11 `url:` refs | Re-point confirmed-dead `llm0X2025-*` variants + dead Agentic page; leave `llm01-prompt-injection/` untouched. |
| OWASP (US-3) | `schemas/taxonomy/crosswalk.yaml` | 16 distinct `genai.owasp.org` citation strings (adds 4 non-year twins `llm02/03/04/05-*` and a 2nd Agentic page `agentic-ai-top-10-vulnerabilities/`). `llm01-prompt-injection/` LIVE in 3 crosswalk records — leave unchanged. | ~25 `citation:` refs (includes annotation suffixes) | See disambiguation note below. Re-point dead variants only. |

---

## OWASP Twin-URL Disambiguation (Mandatory Before US-3 Edits)

`crosswalk.yaml` carries BOTH year-suffixed (`llm0X2025-*`) AND non-year (`llm0X-*`) variants for LLM02–LLM05. These are distinct citation strings pointing at different URL paths. The live/dead status of each variant must be adjudicated individually during T005 (architect research fork) before any edit. **No stale variant may survive**: after remediation, every non-live `llm0X` URL form must be corrected or removed.

| Variant form | Example | Status | Action |
|---|---|---|---|
| Non-year twin (`llm0X-*`) | `llm02-sensitive-information-disclosure/` | Unknown — adjudicate in T005 | Fix or confirm live before closing |
| Year-suffixed (`llm0X2025-*`) | `llm022025-sensitive-information-disclosure/` | Dead per #332 sweep | Re-point to confirmed live URL |
| Agentic page (owasp.yaml) | `owasp-top-10-for-agentic-applications-for-2026/` | Dead per #332 sweep | Re-point to confirmed live URL |
| Agentic page (crosswalk.yaml) | `agentic-ai-top-10-vulnerabilities/` | Unknown — adjudicate in T005 | Fix or confirm live before closing |
| LLM01 regression guard | `llm01-prompt-injection/` | **LIVE — do not touch** | Leave unchanged in both files |

---

## Out-of-Scope Classes

| Class | Location | Reason Out-of-Scope |
|-------|----------|---------------------|
| `tachi-control-category → nist-ai-rmf` local-file citations | `schemas/taxonomy/crosswalk.yaml` (31 edges) | Cite `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` — distinct defect class from dead-DOI; tracked as #325; deferred standalone (FR-005). See `deferred-325.md`. |

---

## Notes

- ATLAS 404s are CLIENT-SIDE ANTI-BOT GATING per R7 TRIPWIRE (mitre-atlas.yaml:18–26, resolved T020 2026-04-17). IDs verified stable via authoritative `mitre-atlas/atlas-data` repo. Resolution is a monitor re-classify, not a data edit — zero YAML changes expected for the ATLAS class.
- NIST count: 73 records, all sharing one DOI URL. A single-URL replacement is a cascade to all 73 with zero per-record research needed beyond confirming the replacement URL resolves.
- This document is a mapping artifact only. No edits to any `schemas/taxonomy/*.yaml` file are made here or implied here.
