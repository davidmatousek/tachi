# Security Analyst — SwiftUI + CloudKit Supplement

## Stack Context

SwiftUI with Swift 6+ strict concurrency, CloudKit (CKContainer, CKDatabase, CKRecord, CKSubscription), Core Data with NSPersistentCloudKitContainer, Keychain Services (Security framework), App Transport Security (ATS), Data Protection API (NSFileProtection), LocalAuthentication (LAContext for biometrics), App Sandbox and entitlements, App Store distribution with code signing, Xcode build configuration, iOS/macOS/visionOS targets.

## Conventions

OWASP Mobile Top 10 mapped to SwiftUI + CloudKit + Core Data + Apple Platform Security:

- **M1 Improper Credential Usage**: ALWAYS store credentials, tokens, and secrets in Keychain via Security framework or KeychainAccess library — NEVER in UserDefaults, plists, or hardcoded strings. ALWAYS scope Keychain items with `kSecAttrAccessGroup` only when app group sharing is required. ALWAYS set `kSecAttrAccessible` to `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` for sensitive items.
- **M2 Inadequate Supply Chain Security**: ALWAYS audit Swift Package Manager dependencies before adoption. ALWAYS pin exact dependency versions in `Package.resolved`. ALWAYS review package source for obfuscated code or excessive entitlement requests. ALWAYS prefer Apple-provided frameworks over third-party equivalents when functionality matches.
- **M3 Insecure Authentication/Authorization**: ALWAYS use CloudKit user identity (`CKCurrentUserDefaultName`) for ownership checks. ALWAYS gate sensitive operations behind biometric auth via `LAContext.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)`. ALWAYS validate CloudKit record ownership server-side — never trust client-only ownership assertions. ALWAYS handle `CKError.notAuthenticated` with re-authentication prompts.
- **M4 Insufficient Input/Output Validation**: ALWAYS validate and sanitize all user input before `CKRecord.setValue(_:forKey:)` operations. ALWAYS validate CloudKit record field types before casting — NEVER force unwrap `CKRecord` values. ALWAYS use `Codable` with strict type validation for data serialization. ALWAYS sanitize any user-generated strings before display in SwiftUI `Text` views.
- **M5 Insecure Communication**: ALWAYS enforce App Transport Security (ATS) globally — NEVER set `NSAllowsArbitraryLoads` to `true`. ALWAYS use HTTPS for all custom API endpoints. ALWAYS implement certificate pinning via `URLSessionDelegate` for non-Apple endpoints. ALWAYS use CloudKit native APIs for Apple-managed transport (Apple handles TLS for CloudKit).
- **M6 Inadequate Privacy Controls**: ALWAYS declare all data usage in `NSPrivacyTrackedDomains` and `NSPrivacyAccessedAPITypes` in `PrivacyInfo.xcprivacy`. ALWAYS request permissions at point of use with meaningful usage descriptions. ALWAYS use CloudKit private database for user-specific data — public database only for non-sensitive, shared content. NEVER log PII, tokens, or biometric status even in debug builds.
- **M7 Insufficient Binary Protections**: ALWAYS enable Bitcode and code signing for all targets. ALWAYS use `@ObfuscatedString` or build-phase encryption for any embedded configuration values. ALWAYS verify entitlements match minimum required capabilities — remove unused entitlements. ALWAYS enable hardened runtime for macOS targets.
- **M8 Security Misconfiguration**: ALWAYS set `NSFileProtectionComplete` on Core Data persistent store via `NSPersistentStoreDescription.setOption`. ALWAYS configure CloudKit container permissions with minimum required access. ALWAYS use separate CloudKit containers for development and production. ALWAYS disable debug logging and verbose error output in release builds.
- **M9 Insecure Data Storage**: ALWAYS encrypt sensitive local data at rest using Data Protection API (`NSFileProtectionComplete`). ALWAYS use Keychain for tokens and credentials — NEVER `UserDefaults` or `@AppStorage`. ALWAYS enable Core Data encryption when using `NSPersistentCloudKitContainer`. ALWAYS exclude sensitive files from iCloud and iTunes backup via `URLResourceValues.isExcludedFromBackup`.
- **M10 Insufficient Cryptography**: ALWAYS use Apple CryptoKit (`AES.GCM`, `SHA256`, `P256`) for cryptographic operations — NEVER roll custom crypto. ALWAYS store encryption keys in Keychain, NEVER alongside encrypted data. ALWAYS use `SecRandomCopyBytes` for cryptographically secure random generation.

## Anti-Patterns

- NEVER store secrets, API keys, tokens, or passwords in `UserDefaults`, `@AppStorage`, `Info.plist`, or hardcoded source — use Keychain exclusively
- NEVER disable App Transport Security globally with `NSAllowsArbitraryLoads` — request specific domain exceptions only with documented justification
- NEVER force unwrap (`!`) CloudKit record fields or network response data — use optional binding or `guard let`
- NEVER trust client-side ownership checks alone — validate record ownership via CloudKit record metadata
- NEVER share CloudKit private database records without explicit user consent and re-authentication
- NEVER log sensitive information (tokens, passwords, PII, biometric results) in any build configuration
- NEVER store encryption keys alongside encrypted data or in UserDefaults
- NEVER skip error handling on CloudKit operations — network, auth, quota, and zone failures are expected
- NEVER use `String(describing:)` or string interpolation to build `NSPredicate` queries — use `NSPredicate(format:argumentArray:)` with parameterized arguments
- NEVER request entitlements beyond what the app requires — remove unused capabilities from signing

## Guardrails

- PR security review checklist: Keychain usage for secrets, ATS enabled, CloudKit ACLs configured, no force unwraps on remote data, no PII in logs, entitlements minimized
- All CloudKit record types MUST have zone-level access controls reviewed before release
- All sensitive local data MUST use `NSFileProtectionComplete` on the persistent store
- All custom network endpoints MUST use HTTPS with certificate pinning via `URLSessionDelegate`
- All biometric-gated operations MUST include fallback to device passcode via `LAPolicy.deviceOwnerAuthentication`
- `PrivacyInfo.xcprivacy` MUST declare all accessed API types and tracking domains before App Store submission
- All Keychain operations MUST specify `kSecAttrAccessible` with the most restrictive level appropriate
- All `CKRecord` field access MUST use optional binding — zero tolerance for force unwraps on remote data
- All entitlement changes MUST be reviewed for capability creep in every security review
