# Fuzz And Mutation Baseline

Generated offline as the initial advisory artifact for AQ-054.

## Status

- `cargo fuzz` lane: documented, not executed in this environment
- `cargo-mutants` lane: documented, not executed in this environment
- Baseline survivors: to be filled after a full local run
- Baseline crashes: to be filled after a full local run

## Follow-Up Beads

- Follow-up Beads tasks should be created from actual fuzz or mutation survivors
- Create a parser roundtrip survivor task once the first fuzz pass produces output
- Create a normalization survivor task once mutation output identifies a weak case
- Create a rendering survivor task once the first mutation pass identifies brittle output

## Notes

- Keep this artifact free of secrets, credentials, and customer data
- Update it only with code-path evidence and stable repro steps
