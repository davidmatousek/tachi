# Threat Model Report

---

```yaml
---
schema_version: "1.0"
date: "2026-03-21"
input_format: "free-text"
classification: "confidential"
---
```

---

## 1. System Overview

An e-commerce order processing platform built on a microservice architecture. The system handles customer-facing order placement, payment processing, and inventory management through loosely coupled services communicating over synchronous HTTP and asynchronous AMQP messaging.

### Components

| Component | Type | Description |
|-----------|------|-------------|
| External Clients | External Entity | Web browsers and mobile applications that submit orders and authenticate via JWT |
| API Gateway | Process | Single HTTPS entry point on port 443; terminates TLS, validates JWT tokens, enforces rate limits, routes to internal services |
| Order Service | Process | Manages order lifecycle via internal REST API on port 8080; publishes and consumes message queue events |
| Payment Service | Process | Processes payment transactions by consuming MQ events and calling the External Payment Provider API |
| Inventory Database | Data Store | PostgreSQL 15 on port 5432; stores product catalog, stock levels, order records, and payment transaction logs |
| Message Queue | Data Store | RabbitMQ 3.12 cluster on port 5672 (AMQP over TLS); provides durable persistent message delivery between services |
| External Payment Provider | External Entity | Stripe REST API at api.stripe.com; processes payment authorizations and sends webhook callbacks |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| External Clients | API Gateway | Order data (product IDs, quantities, shipping address, payment token), JWT auth | HTTPS/TLS 1.2+ |
| API Gateway | Order Service | Validated request body (order payload) | HTTP |
| Order Service | Inventory Database | Stock queries, inventory reservations, order records | TCP/TLS (connection pooled) |
| Order Service | Message Queue | `order.payment.requested` events (order ID, amount, currency, payment token) | AMQP/TLS |
| Message Queue | Payment Service | `order.payment.requested` events | AMQP/TLS |
| Payment Service | External Payment Provider | Tokenized card data, order amount, currency, idempotency key | HTTPS/TLS 1.2+ |
| External Payment Provider | Payment Service | Authorization responses; webhook callbacks (chargebacks, refunds, disputes) | HTTPS/TLS 1.2+ |
| Payment Service | Message Queue | `payment.completed` or `payment.failed` events | AMQP/TLS |
| Message Queue | Order Service | `payment.completed` or `payment.failed` events | AMQP/TLS |
| Payment Service | Inventory Database | Payment transaction logs | TCP/TLS (connection pooled) |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Database | PostgreSQL | 15 |
| Message Broker | RabbitMQ | 3.12 |
| Auth | JWT (external identity provider) | RFC 7519 |
| Payment Gateway | Stripe REST API | v1 |
| Transport | TLS | 1.2+ |
| Protocol | AMQP | 0-9-1 |
| Protocol | HTTP/HTTPS | 1.1 |
| Container Runtime | Docker (containerized services) | unknown |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| External Zone | Untrusted | External Clients, External Payment Provider |
| DMZ | Semi-trusted | API Gateway |
| Internal Services Zone | Trusted | Order Service, Payment Service, Inventory Database, Message Queue |
| External Services Zone | Untrusted | External Payment Provider |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Client-to-DMZ | External Zone | DMZ | External Clients -> API Gateway | TLS termination, JWT validation, rate limiting, input sanitization |
| DMZ-to-Internal | DMZ | Internal Services Zone | API Gateway -> Order Service | URL-based routing, stripped sensitive headers, network policy restrictions |
| Internal-to-ExternalServices | Internal Services Zone | External Services Zone | Payment Service -> External Payment Provider | HTTPS, API secret key auth, idempotency keys |
| ExternalServices-to-Internal | External Services Zone | Internal Services Zone | External Payment Provider -> Payment Service | Webhook signature verification, TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

Threats where an attacker pretends to be something or someone else.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | API Gateway | Attacker forges or steals JWT tokens to impersonate authenticated users, placing fraudulent orders or accessing other customers' order data | HIGH | HIGH | Critical | Enforce short-lived JWT expiration (15 min); implement token revocation list; validate issuer and audience claims on every request; use RS256 asymmetric signing |
| S-2 | Payment Service | Attacker compromises the Stripe API secret key from configuration or environment variable leakage, enabling unauthorized payment operations (refunds, charges) against the merchant account | LOW | HIGH | Medium | Store API keys in a secrets manager (not environment variables or config files); rotate keys quarterly; restrict key permissions to minimum required operations; monitor Stripe dashboard for anomalous API calls |
| S-3 | Order Service | Rogue internal service impersonates the API Gateway to send fabricated requests to the Order Service on port 8080, bypassing authentication and rate limiting | MEDIUM | HIGH | High | Implement mutual TLS or signed request headers between API Gateway and Order Service; enforce network policies restricting port 8080 access to the API Gateway container only |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Message Queue | Attacker with access to the internal network injects or modifies messages on the RabbitMQ `orders` exchange, fabricating `order.payment.requested` events with altered amounts or forged order IDs | MEDIUM | HIGH | High | Enable RabbitMQ message signing or HMAC validation between producers and consumers; enforce AMQP user-level permissions so only the Order Service can publish to the `orders` exchange; restrict network access to port 5672 |
| T-2 | Inventory Database | Attacker manipulates order records or stock levels directly in the database by exploiting a compromised service account with excessive privileges | LOW | HIGH | Medium | Apply principle of least privilege: Order Service account can only write to order tables, Payment Service account can only write to transaction tables; enable PostgreSQL audit logging on all DML operations |
| T-3 | Payment Service | Attacker intercepts or replays webhook callbacks from Stripe with modified payment amounts or forged completion statuses, causing the system to fulfill unpaid orders | MEDIUM | HIGH | High | Verify Stripe webhook signatures using the endpoint signing secret on every callback; enforce HTTPS-only webhook endpoint; implement idempotency checks to prevent replay attacks |

### 3.3 Repudiation (R)

Threats where an attacker denies having performed an action without the system being able to prove otherwise.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | Order Service | Customer disputes a legitimate order placement, and the system cannot prove the order was authorized because no audit trail captures the authenticated user identity, source IP, and timestamp at order creation | MEDIUM | MEDIUM | Medium | Implement an immutable audit log capturing user ID, session ID, source IP, user agent, order payload hash, and timestamp for every order creation and status change; store logs in append-only storage |
| R-2 | Payment Service | Payment transaction outcome is disputed, but the system lacks correlation between the Stripe charge ID, internal order ID, and the message queue event that triggered the payment, preventing forensic reconstruction | MEDIUM | HIGH | High | Log complete payment lifecycle with correlation IDs linking order ID, MQ message ID, Stripe charge ID, and authorization result; retain transaction logs for regulatory compliance period |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | Inventory Database | PostgreSQL connection strings containing credentials are exposed in application error stack traces returned to the API Gateway and forwarded to external clients | MEDIUM | HIGH | High | Implement structured error handling in Order Service and Payment Service that returns generic error codes to upstream callers; log detailed errors (including stack traces) to internal-only centralized logging; never propagate database errors across trust boundaries |
| I-2 | Message Queue | Sensitive payment data (tokenized card info, payment amounts, customer IDs) in transit on RabbitMQ queues is readable by any service with AMQP credentials, violating least-privilege access to payment data | MEDIUM | MEDIUM | Medium | Encrypt sensitive message payloads at the application layer before publishing (envelope encryption); enforce per-queue ACLs so only the Payment Service can consume from the `orders` exchange payment routing key; segregate payment messages into a dedicated vhost |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access to the system.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | API Gateway | Volumetric attack floods the API Gateway with malformed HTTPS requests, exhausting TLS handshake capacity and connection pool, blocking all legitimate client traffic | HIGH | HIGH | Critical | Deploy upstream DDoS protection (cloud provider WAF/shield); enforce per-IP and per-user rate limiting; implement connection timeouts and circuit breaker patterns; auto-scale gateway instances |
| D-2 | Message Queue | Malicious or buggy producer floods the RabbitMQ cluster with messages, consuming disk space and memory, causing the broker to block all publishers and halt order processing | MEDIUM | HIGH | High | Configure RabbitMQ per-queue message limits and per-connection publish rate limits; set memory and disk high watermarks; implement dead-letter exchanges for unprocessable messages; monitor queue depth with alerts |
| D-3 | Inventory Database | Concurrent connection exhaustion against PostgreSQL caused by uncontrolled connection pool growth from the Order Service and Payment Service during traffic spikes, making the database unreachable | MEDIUM | HIGH | High | Enforce connection pool max limits per service (e.g., 20 connections each); configure PostgreSQL max_connections appropriately; implement connection timeout and retry with exponential backoff; use PgBouncer for connection multiplexing |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | Order Service | Attacker manipulates order status transitions (e.g., from "payment_failed" to "fulfilled") by sending crafted HTTP requests to the Order Service, bypassing the intended state machine and fulfilling unpaid orders | MEDIUM | HIGH | High | Implement a strict order state machine that validates all transitions server-side; reject invalid state transitions with explicit errors; log all status change attempts including denied transitions |
| E-2 | API Gateway | Attacker modifies JWT claims (role, scope, or user ID) in a stolen token to escalate from a customer role to an admin role, gaining access to order management and refund endpoints | LOW | HIGH | Medium | Validate JWT signature and all claims (role, scope, issuer, audience, expiration) against the identity provider on every request; never trust client-supplied role values; implement claim-based access control at both gateway and service layers |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

No agentic or LLM components detected in the architecture. The system uses traditional microservice patterns with no autonomous agents, AI orchestrators, or tool-calling interfaces.

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|

**Findings: 0**

### 4.2 LLM Threats (LLM)

No agentic or LLM components detected in the architecture. The system uses no language models, embedding services, or AI-powered processing pipelines.

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|

**Findings: 0**

---

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| External Clients | - |  | - |  |  |  |  |  | 0 |
| API Gateway | 1 | - | - | - | 1 | 1 |  |  | 3 |
| Order Service | 1 | - | 1 | - | - | 1 |  |  | 3 |
| Payment Service | 1 | 1 | 1 | - | - | - |  |  | 3 |
| Inventory Database |  | 1 |  | 1 | 1 |  |  |  | 3 |
| Message Queue |  | 1 |  | 1 | 1 |  |  |  | 3 |
| External Payment Provider | - |  | - |  |  |  |  |  | 0 |
| **Total** | **3** | **3** | **2** | **2** | **3** | **2** | **0** | **0** | **15** |

---

## 6. Risk Summary

**OWASP 3x3 risk matrix reference:**

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 2 | 13.3% |
| High | 8 | 53.3% |
| Medium | 5 | 33.3% |
| Low | 0 | 0.0% |
| Note | 0 | 0.0% |
| **Total** | **15** | **100%** |

---

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-1 | API Gateway | JWT token forgery or theft enabling user impersonation | Critical | Enforce short-lived JWT expiration (15 min); implement token revocation list; validate issuer and audience claims; use RS256 asymmetric signing |
| D-1 | API Gateway | Volumetric DDoS exhausting TLS capacity and connection pool | Critical | Deploy upstream DDoS protection; enforce per-IP and per-user rate limiting; implement connection timeouts and circuit breaker patterns; auto-scale |
| S-3 | Order Service | Rogue internal service impersonating API Gateway | High | Implement mutual TLS or signed request headers between gateway and services; enforce network policies restricting port 8080 |
| T-1 | Message Queue | Message injection or modification on RabbitMQ orders exchange | High | Enable message signing/HMAC; enforce AMQP user-level publish permissions; restrict network access to port 5672 |
| T-3 | Payment Service | Forged or replayed Stripe webhook callbacks | High | Verify Stripe webhook signatures; enforce HTTPS-only endpoint; implement idempotency checks against replay |
| R-2 | Payment Service | Payment transaction disputes without cross-system correlation | High | Log complete payment lifecycle with correlation IDs linking order, MQ message, and Stripe charge; retain for compliance |
| I-1 | Inventory Database | Database credentials exposed in error stack traces | High | Structured error handling returning generic codes; internal-only centralized logging; never propagate database errors across trust boundaries |
| D-2 | Message Queue | Message flood consuming broker disk and memory | High | Configure per-queue message limits and publish rate limits; set memory/disk watermarks; dead-letter exchanges; queue depth monitoring |
| D-3 | Inventory Database | Connection pool exhaustion during traffic spikes | High | Enforce per-service connection pool limits; configure PostgreSQL max_connections; connection timeout with exponential backoff; PgBouncer |
| E-1 | Order Service | Order status manipulation bypassing state machine | High | Strict server-side state machine validation; reject invalid transitions; log all status change attempts |
| S-2 | Payment Service | Stripe API key compromise enabling unauthorized payment operations | Medium | Secrets manager for API keys; quarterly rotation; minimum-permission key scoping; Stripe dashboard anomaly monitoring |
| T-2 | Inventory Database | Direct database record manipulation via over-privileged service account | Medium | Least-privilege database accounts per service; PostgreSQL audit logging on all DML operations |
| R-1 | Order Service | Missing audit trail for order creation disputes | Medium | Immutable audit log with user ID, session ID, source IP, user agent, payload hash, and timestamp; append-only storage |
| I-2 | Message Queue | Payment data readable by any AMQP-credentialed service | Medium | Application-layer envelope encryption; per-queue ACLs; dedicated payment vhost |
| E-2 | API Gateway | JWT claim manipulation for role escalation | Medium | Validate JWT signature and all claims against identity provider; claim-based access control at gateway and service layers |
