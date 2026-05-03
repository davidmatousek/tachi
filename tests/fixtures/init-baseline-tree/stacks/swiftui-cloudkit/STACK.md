# SwiftUI + CloudKit Stack

**Target**: Solo developers and small teams building native iOS/macOS applications
**Stack**: SwiftUI · Swift 6+ · CloudKit · SwiftData · Swift Package Manager · Xcode 26+
**Use Case**: Native iOS/macOS applications with cloud sync, offline-first, iCloud integration
**Deployment**: App Store (iOS/macOS), TestFlight (beta)
**Philosophy**: Declarative UI, protocol-oriented design, offline-first with cloud sync, platform-native patterns

---

## Architecture Pattern

### UI Framework

ALWAYS use SwiftUI for all user interface code. ONLY bridge to UIKit (`UIViewRepresentable`) when a SwiftUI equivalent does not exist — document the justification inline.

### Application Architecture

- MVVM (Model-View-ViewModel) with clear layer separation.
- Views declare UI and bind to ViewModels. Views NEVER contain business logic or direct data access.
- ViewModels own state and orchestrate Service calls. ViewModels NEVER import SwiftUI — they depend on Observation framework only.
- Services encapsulate external concerns (CloudKit, Keychain, networking). Services are injected into ViewModels via protocol-based dependency injection.

### Data Flow

- **Persistence**: SwiftData with CloudKit integration (`ModelContainer` configured for iCloud sync). SwiftData handles local SQLite storage and automatic CloudKit synchronization.
- **Queries**: Use `@Query` in Views for reactive data fetching. Use `ModelContext` in ViewModels and Services for programmatic CRUD.
- **Sync**: CloudKit sync is automatic via SwiftData's `ModelConfiguration` with `cloudKitDatabase` parameter. NEVER manage CKRecord operations manually unless SwiftData cannot express the requirement.
- **Offline-first**: All operations write to local SwiftData store first. CloudKit sync occurs when connectivity is available.

### State Management

- **View state**: `@State` for view-local ephemeral state (toggles, form fields, sheet presentation).
- **ViewModel state**: `@Observable` ViewModels injected via `@State` or `@Environment`. NEVER use `ObservableObject` / `@Published` — these are legacy patterns.
- **App-wide state**: Use `@Environment` with custom `EnvironmentKey` for shared services and configuration.
- **Navigation state**: `NavigationStack` with `NavigationPath` for programmatic navigation. Use `NavigationSplitView` for multi-column layouts on iPad/macOS.

### Concurrency

- ALWAYS use `async/await` for all asynchronous operations. NEVER use completion handlers in new code.
- ALWAYS use `@MainActor` for ViewModels and any code that updates UI state.
- Use `actor` types for thread-safe mutable state that must be accessed from multiple isolation domains.
- Use `nonisolated` only for pure functions and stateless computed properties.

---

## File Structure

```
{AppName}/
├── App/
│   ├── {AppName}App.swift          # @main entry point, ModelContainer setup
│   └── AppEnvironment.swift        # Environment keys and shared configuration
├── Views/
│   ├── ContentView.swift           # Root view (NavigationSplitView or TabView)
│   ├── {Feature}/                  # Feature-grouped views
│   │   ├── {Feature}View.swift
│   │   └── {Feature}DetailView.swift
│   └── Components/                 # Reusable view components
│       ├── LoadingView.swift
│       └── ErrorView.swift
├── ViewModels/
│   ├── {Feature}ViewModel.swift    # @Observable, @MainActor
│   └── {Feature}DetailViewModel.swift
├── Models/
│   ├── {Entity}.swift              # SwiftData @Model definitions
│   └── {ValueType}.swift           # Value types, enums, DTOs
├── Services/
│   ├── CloudKitService.swift       # CloudKit operations beyond SwiftData auto-sync
│   ├── KeychainService.swift       # Secure credential storage
│   └── {Feature}Service.swift      # Feature-specific service logic
├── Protocols/
│   ├── {Service}Protocol.swift     # Service abstractions for DI and testing
│   └── Identifiable+Extensions.swift
├── Extensions/
│   ├── View+Extensions.swift       # SwiftUI view modifiers
│   └── Date+Extensions.swift       # Foundation type extensions
├── Resources/
│   ├── Assets.xcassets             # Images, colors, app icon
│   ├── Localizable.xcstrings       # String catalog for localization
│   └── Preview Content/            # Preview assets
├── {AppName}.entitlements          # iCloud, push notifications capabilities
└── Info.plist                      # App configuration (if needed beyond Xcode settings)

{AppName}Tests/
├── ViewModels/
│   └── {Feature}ViewModelTests.swift
├── Services/
│   └── {Service}Tests.swift
├── Models/
│   └── {Entity}Tests.swift
└── Mocks/
    └── Mock{Service}.swift         # Protocol-conforming test doubles

{AppName}UITests/
├── {Feature}UITests.swift
└── TestHelpers/
    └── XCUIApplication+Extensions.swift
```

---

## Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Views | PascalCase + `View` suffix | `UserProfileView.swift` |
| ViewModels | PascalCase + `ViewModel` suffix | `UserProfileViewModel.swift` |
| Models (SwiftData) | PascalCase, no suffix | `User.swift`, `Task.swift` |
| Services | PascalCase + `Service` suffix | `CloudKitService.swift` |
| Protocols | PascalCase, descriptive noun or `-able`/`-ing` | `DataStoring`, `Authenticatable` |
| Extensions | `{Type}+{Purpose}.swift` | `View+Extensions.swift` |
| Unit tests | PascalCase + `Tests` suffix | `UserProfileViewModelTests.swift` |
| UI tests | PascalCase + `UITests` suffix | `AuthenticationUITests.swift` |
| Properties | camelCase | `userName`, `isLoading` |
| Type-level constants | camelCase or `static let` | `static let maxRetryCount = 3` |
| Enum cases | camelCase | `.loading`, `.error(String)` |
| SwiftData model properties | camelCase, matches CloudKit record field names | `createdAt`, `ownerID` |
| Packages (SPM) | PascalCase | `KeychainAccess`, `SnapshotTesting` |

---

## Security Patterns

### Credential Storage

- ALWAYS use Keychain (via `Security` framework or `KeychainAccess` package) for storing credentials, tokens, and sensitive user data.
- NEVER store secrets, tokens, or credentials in `UserDefaults` — it is an unencrypted plist.
- NEVER store secrets in `Info.plist`, source code, asset catalogs, or string catalogs.

### Network Security

- ALWAYS use App Transport Security (HTTPS only). NEVER add ATS exception domains unless connecting to a local development server with a documented justification.
- NEVER disable ATS globally via `NSAllowsArbitraryLoads`.
- ALWAYS use `URLSession` with certificate pinning for sensitive API endpoints.

### Data Access Control

- ALWAYS configure CloudKit container permissions with appropriate database scope (private, shared, or public).
- ALWAYS use SwiftData's `ModelConfiguration` to control which models sync to CloudKit and which remain local-only.
- ALWAYS validate and sanitize user input before writing to SwiftData models.
- NEVER expose CloudKit container identifiers or API tokens in client-visible logs.

### Input Validation

- ALWAYS validate user input at the ViewModel layer before passing to Services.
- NEVER trust data from external sources (CloudKit records, deep links, push notification payloads) without validation.
- ALWAYS use Swift's type system (enums, optionals, value types) as the first line of defense.

---

## Coding Standards

### Always Use

- **SwiftUI** for all UI — bridge to UIKit only when no SwiftUI equivalent exists.
- **`@Observable`** (Observation framework) for all ViewModels. Pair with `@State` in Views.
- **`@MainActor`** on all ViewModels and any code that mutates UI-bound state.
- **`NavigationStack`** for navigation — not the deprecated `NavigationView`.
- **`async/await`** for all asynchronous operations. Use structured concurrency (`TaskGroup`, `async let`) for parallel work.
- **Swift Package Manager** for all third-party dependencies.
- **SwiftData** with `@Model` for persistence. Configure `ModelContainer` in the `@main` App struct.
- **`@Query`** for reactive data fetching in Views.
- **Protocol-based dependency injection** for all Services — enables testing with mock implementations.
- **Value types** (`struct`, `enum`) by default. Use `class` only for SwiftData `@Model`, `@Observable` ViewModels, and reference semantics.
- **`Result` type or `throws`** for error handling. Define domain-specific error enums conforming to `LocalizedError`.
- **`guard` statements** for early returns. Prefer `guard let` over `if let` for unwrapping that exits scope.
- **Access control** — mark types and members with the minimum necessary visibility (`private`, `fileprivate`, `internal`, `public`).
- **Swift 6 strict concurrency** — enable strict concurrency checking in build settings. Fix all warnings.

### Never Use

- **`ObservableObject` / `@Published`** — use `@Observable` (Observation framework).
- **`NavigationView`** (deprecated) — use `NavigationStack` or `NavigationSplitView`.
- **Completion handlers** for new async code — use `async/await`.
- **CocoaPods or Carthage** — use Swift Package Manager exclusively.
- **Force unwraps (`!`)** on optional values from external sources (network, CloudKit, user input).
- **Implicitly unwrapped optionals** — except `@IBOutlet` in UIKit bridge code.
- **`AnyView`** type erasure — use `@ViewBuilder`, `some View`, or concrete types.
- **Global mutable state** (`static var`) — use `@Environment`, actors, or dependency injection.
- **UIKit view controllers** when a SwiftUI equivalent exists.
- **`UserDefaults`** for sensitive data — use Keychain.
- **Storyboards or XIBs** — SwiftUI only.
- **`DispatchQueue`** for concurrency — use Swift concurrency (`async/await`, actors, `Task`).
- **Singletons** — use protocol-based DI via `@Environment` or initializer injection.

---

## Testing Conventions

<!-- BEGIN: aod-test-contract -->
```yaml
test_command: "xcodebuild test -scheme <App>"
e2e_opt_out: "XCTest command substitution (scheme/destination placeholders) requires schema extension — tracked in #140"
```
<!-- END: aod-test-contract -->

### Framework Stack

| Level | Framework | Purpose |
|-------|-----------|---------|
| Unit | Swift Testing | ViewModels, Services, Models, business logic |
| Integration | Swift Testing | Service interactions, SwiftData operations |
| UI | XCUITest (XCTest) | User flows, accessibility, screen interactions |
| Snapshot | swift-snapshot-testing | Visual regression for SwiftUI views |

### Test File Conventions

- Place unit and integration tests in `{AppName}Tests/` target, mirroring source directory structure.
- Place UI tests in `{AppName}UITests/` target.
- ALWAYS use the `Tests` suffix for unit/integration test files. ALWAYS use `UITests` suffix for UI test files.
- Place mock implementations in `{AppName}Tests/Mocks/`. Mocks conform to the same protocol as the real Service.

### Unit Tests (Swift Testing)

- Test ViewModels by injecting mock Services and verifying state changes.
- Test Services by mocking external dependencies (CloudKit, network).
- Test model validation logic and computed properties.
- Use `@Test` attribute and `#expect` macro. NEVER use legacy `XCTAssert` in new unit tests.
- Name tests descriptively: `@Test("User creation fails with empty name")`.

### UI Tests (XCUITest)

- Cover critical user journeys: onboarding, CRUD operations, sync feedback.
- ALWAYS use `accessibilityIdentifier` for element identification — NEVER rely on string content that may be localized.
- Use `XCUIApplication` launch arguments to configure test state (e.g., skip onboarding, use mock data).
- Test both online and offline scenarios when CloudKit sync is involved.

### Snapshot Tests

- Use [swift-snapshot-testing](https://github.com/pointfreeco/swift-snapshot-testing) for visual regression of SwiftUI views.
- Snapshot key views in both light and dark mode, and multiple Dynamic Type sizes.
- Store reference images in `{AppName}Tests/__Snapshots__/`.

### Coverage

- Enforce minimum 80% line coverage on ViewModels and Services.
- Do NOT enforce coverage thresholds on Views — test critical interactions via UI tests, not view rendering.
