# Frontend Developer — SwiftUI + CloudKit Supplement

## Stack Context

SwiftUI declarative UI with Swift 6+ Observation framework (`@Observable`), NavigationStack and NavigationSplitView for navigation, Swift structured concurrency (async/await, actors, TaskGroup), Core Data with CloudKit sync (`NSPersistentCloudKitContainer`), Swift Package Manager for dependencies, Xcode as the build system. Minimum deployment targets: iOS 17.0 / macOS 14.0 (required for Observation framework).

## Conventions

- ALWAYS use SwiftUI for all UI; only use UIViewRepresentable when no SwiftUI equivalent exists
- ALWAYS use `@Observable` (Observation framework) for view models; never ObservableObject or @Published
- ALWAYS annotate view models with `@MainActor` for thread-safe UI updates
- ALWAYS use `@State` to own `@Observable` view models in the view that creates them
- ALWAYS use `@Environment` for dependency injection of shared services and view models
- ALWAYS use `NavigationStack` with `NavigationLink(value:)` and `.navigationDestination` for type-safe stack navigation
- ALWAYS use `NavigationSplitView` for sidebar/detail layouts on iPad and Mac
- ALWAYS use `.task {}` modifier for async data loading on view appear; never `.onAppear` with `Task {}`
- ALWAYS use async/await for all asynchronous operations; never completion handlers in new code
- ALWAYS use Swift structured concurrency (`async let`, `TaskGroup`) for parallel operations
- ALWAYS use `@ViewBuilder` for composable view helper methods; never return `AnyView`
- ALWAYS handle loading, error, and empty states in every view that fetches data
- ALWAYS handle offline gracefully in views backed by CloudKit; show cached Core Data results
- ALWAYS use SF Symbols for icons, consistent with Apple Human Interface Guidelines
- ALWAYS group views by feature: `Views/{FeatureName}/{FeatureName}View.swift`
- ALWAYS extract reusable view components to `Views/Components/`
- ALWAYS define view-specific types and small extensions in the same file as the view
- ALWAYS use Swift Package Manager for all third-party dependencies

## Anti-Patterns

- NEVER use `ObservableObject`, `@Published`, `@StateObject`, or `@ObservedObject`; use `@Observable` and `@State`
- NEVER use `NavigationView`; it is deprecated; use `NavigationStack` or `NavigationSplitView`
- NEVER use `AnyView` for type erasure; use `@ViewBuilder`, `Group`, or conditional views
- NEVER use completion handlers for new async code; use async/await exclusively
- NEVER force unwrap (`!`) data from CloudKit, network responses, or user input
- NEVER mutate `@State` from background threads; ensure mutations are on `@MainActor`
- NEVER use global singletons for state; use `@Environment` and dependency injection
- NEVER nest view bodies more than 3 levels deep; extract sub-views into computed properties or separate types
- NEVER use CocoaPods or Carthage; use Swift Package Manager exclusively
- NEVER use UIKit lifecycle methods; use SwiftUI view modifiers (`.task`, `.onDisappear`, `.onChange`)
- NEVER use string-based navigation; use typed `NavigationPath` and `.navigationDestination(for:)`
- NEVER perform Core Data writes on the main thread for large batch operations; use `newBackgroundContext()`

## Guardrails

- View files: `Views/{Feature}/{FeatureName}View.swift` (PascalCase with `View` suffix)
- ViewModel files: `ViewModels/{Feature}ViewModel.swift` (PascalCase with `ViewModel` suffix)
- Component files: `Views/Components/{ComponentName}.swift` (PascalCase)
- Model files: `Models/{ModelName}.swift` (PascalCase, matching Core Data entity names)
- Maximum view body complexity: extract sub-views when body exceeds ~50 lines
- All view models must conform to `@MainActor` and be marked `@Observable`
- All CloudKit-backed views must display cached data when offline and surface sync errors non-intrusively
- All new Swift files must use strict concurrency checking (`SWIFT_STRICT_CONCURRENCY = complete`)
- No `Any` type; use generics or protocols with associated types when the type varies
- Previews must be provided for every view using `#Preview` macro syntax (not `PreviewProvider`)
