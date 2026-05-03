# Tester — SwiftUI + CloudKit Supplement

## Stack-Specific E2E Conventions

This pack opts out of the AOD E2E automation contract. Per `stacks/swiftui-cloudkit/STACK.md` (`e2e_opt_out`), `xcodebuild test` requires scheme and destination placeholders that the current `test_command` schema does not express.

XCTest command substitution (scheme/destination) is tracked in the upstream AOD Kit — see `stacks/swiftui-cloudkit/STACK.md` (`e2e_opt_out`) for the tracking issue reference. Until that schema extension lands, UI flows are validated via XCUITest in-repo (`xcodebuild test -scheme <App>`), not the AOD E2E gate.
