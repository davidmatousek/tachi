# Archived Docs Workflow-Version Inventory

Status: DOC-001 inventory complete

Scope: `docs/` and `examples/` only. Live workflow files under
`.github/workflows/` are intentionally excluded.

## Scan summary

- `examples/` returned no stale workflow-version matches.
- Maintained docs are already using current guidance or intentional
  validation text.
- Historical docs still carry older workflow-version references as archival
  provenance and are the target for DOC-003 labeling.

## Inventory

### Maintained docs

| File | Hit type | Disposition |
| --- | --- | --- |
| `docs/bill-of-materials.html.md` | workflow-gate regex and checklist text | Keep as current validation language; not stale guidance |
| `docs/publish-readiness-checklist.html.md` | workflow-gate regex and Node 20 check | Keep as current validation language; not stale guidance |

### Historical docs

| File | Hit type | Disposition |
| --- | --- | --- |
| `docs/architecture/02_ADRs/ADR-013-sarif-output-format-adoption.md` | `codeql/upload-sarif@v3` reference | Label as archival provenance in DOC-003 |
| `docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md` | `codeql/upload-sarif@v3` reference | Label as archival provenance in DOC-003 |
| `docs/product/02_PRD/021-platform-adapters-2026-03-23.md` | `codeql/upload-sarif@v3` reference | Label as archival provenance in DOC-003 |
| `docs/guides/CONSUMER_GUIDE_TACHI.md` | `codeql/upload-sarif@v3` reference | Label as archival provenance in DOC-003 |
| `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` | `codeql/upload-sarif@v3` reference | Label as archival provenance in DOC-003 |
| `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md` | `codeql/upload-sarif@v3` reference | Label as archival provenance in DOC-003 |

### Archived roadmap docs

| File | Hit type | Disposition |
| --- | --- | --- |
| `docs/roadmap/2026-06-15-rust-tauri-parity-issue-cards.md` | parity-archive narrative | Keep archived; no active CI guidance |
| `docs/roadmap/2026-06-15-rust-tauri-parity-remediation-roadmap.html.md` | parity-archive narrative | Keep archived; no active CI guidance |
| `docs/roadmap/2026-06-21-rust-tauri-parity-capability-matrix.md` | completed parity artifact | Keep as provenance for RT-024 |
| `docs/roadmap/2026-06-21-rust-tauri-parity-remediation-roadmap.html.md` | completed parity roadmap narrative | Keep as provenance for RT-024 through RT-030 |
| `docs/roadmap/2026-06-21-rust-tauri-parity-issue-cards.md` | completed parity backlog narrative | Keep as provenance for RT-024 through RT-030 |
| `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md` | docs-sweep plan text | Keep as active docs-sweep roadmap |
| `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md` | docs-sweep issue text | Keep as active docs-sweep issue set |

## Disposition

DOC-001 is satisfied by this inventory.

Next ready docs work:

1. DOC-002 refresh maintained docs only if any stale pin remains after the
   gate text is reviewed.
2. DOC-003 label archival docs with explicit historical markers.
3. DOC-004 keep the docs/examples regression scan in place.
