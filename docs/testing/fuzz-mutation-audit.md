# Fuzz And Mutation Audit

This lane is advisory and starts observationally.
It is intended to run manually or on a scheduled non-blocking workflow.

## Baseline commands

- `cargo fuzz run parser_roundtrip`
- `cargo fuzz run reporting_roundtrip`
- `cargo-mutants run --workspace --test`

## Baseline artifacts

- `docs/reports/fuzz-mutation-baseline.md`
- Follow-up Beads tasks for any surviving parser, normalization, or rendering cases
- `.github/workflows/fuzz-mutation-audit.yml` for the scheduled/manual advisory lane

## Promotion criteria

- At least one crash or survivor is recorded before fail-closed promotion
- Commands stay documented and manually runnable
- The baseline report is kept offline and reproducible from the repo
- The scheduled workflow remains non-blocking by policy

## Privacy And Security Notes

- Do not store secrets, credentials, or customer data in the baseline report
- Keep survivor notes scoped to code paths, inputs, and public issue references
- Treat this lane as advisory until the team sets a blocking policy
