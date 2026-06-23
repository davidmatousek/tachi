# Fuzz And Mutation Baseline

Generated offline as the initial advisory artifact for AQ-054.
This baseline pairs with the scheduled/manual advisory workflow and the
publish gate docs; it is intentionally non-blocking until survivors justify
promotion.

## Status

- `cargo fuzz` lane: documented, not executed in this environment
- `cargo-mutants` lane: documented, not executed in this environment
- Baseline survivors: to be filled after a full local run
- Baseline crashes: to be filled after a full local run
- Parser roundtrip seed coverage now exists in `crates/tachi-core/tests/parsers.rs`
  via `parse_threats_findings_roundtrips_a_canonical_seed_row_without_loss`
  so a future survivor has a regression landing zone even before the first
  real fuzz output is captured.

## Follow-Up Beads

- Follow-up Beads tasks should be created from actual fuzz or mutation survivors
- Create a parser roundtrip survivor task once the first fuzz pass produces output
- Create a normalization survivor task once mutation output identifies a weak case
- Create a rendering survivor task once the first mutation pass identifies brittle output
- Current follow-up issues are tracked in Beads as `AQ-054.4`, `AQ-054.5`, and
  `AQ-054.6`; revalidate them after the first real fuzz or mutation run.

## Notes

- Keep this artifact free of secrets, credentials, and customer data
- Update it only with code-path evidence and stable repro steps
