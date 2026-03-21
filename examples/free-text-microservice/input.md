# Example Input: E-Commerce Microservice Architecture

This file demonstrates the **free-text** input format for tachi. It describes an e-commerce microservice architecture using prose narrative rather than diagram syntax. The parser detects this format by the absence of diagram keywords and the presence of natural language component descriptions.

---

format: free-text

---

## System Overview

The system is an e-commerce order processing platform built on a microservice architecture. It handles customer-facing order placement, payment processing, and inventory management through a set of loosely coupled services communicating over a combination of synchronous HTTP and asynchronous messaging.

## Components

The **API Gateway** is the single entry point for all external client traffic. It receives HTTPS requests from web browsers and mobile applications on port 443, terminates TLS, performs rate limiting, and routes requests to the appropriate internal service based on URL path prefixes. The gateway authenticates incoming requests by validating JWT tokens issued by an external identity provider. It runs as a containerized process behind a cloud load balancer.

The **Order Service** is responsible for the complete order lifecycle. It exposes an internal REST API on port 8080 that accepts order creation, retrieval, and status update requests from the API Gateway over HTTP. When a new order is placed, the Order Service validates the order payload, reserves inventory by sending a synchronous HTTP request to the Inventory Database, and initiates payment by publishing an `order.payment.requested` event to the Message Queue. It persists order records to its own order table within the Inventory Database. The Order Service consumes `payment.completed` and `payment.failed` events from the Message Queue to update order status accordingly.

The **Payment Service** processes payment transactions. It subscribes to `order.payment.requested` events from the Message Queue and, upon receiving a payment request, calls the External Payment Provider's REST API over HTTPS to authorize and capture the payment. The Payment Service sends the customer's tokenized card information, order amount, and currency to the provider. It receives authorization responses synchronously. After processing, the Payment Service publishes either a `payment.completed` or `payment.failed` event back to the Message Queue. It maintains a local transaction log in the Inventory Database for reconciliation purposes.

The **Inventory Database** is a PostgreSQL 15 relational database running on port 5432. It stores product catalog data (SKUs, descriptions, pricing), real-time stock levels, order records, and payment transaction logs. The Order Service and Payment Service connect to it using connection pooling over TCP with TLS-encrypted connections. The database enforces row-level security policies and uses parameterized queries exclusively. Backups run every 6 hours to encrypted cloud storage.

The **Message Queue** is a RabbitMQ 3.12 cluster running on port 5672 (AMQP) with management interface on port 15672. It provides durable, persistent message delivery between services. Three exchanges are configured: `orders` (topic exchange for order lifecycle events), `payments` (topic exchange for payment result events), and `inventory` (fanout exchange for stock-level change notifications). All connections use AMQP over TLS. Messages are persisted to disk and acknowledged explicitly by consumers.

The **External Payment Provider** is a third-party payment processing service (Stripe). It exposes a REST API at `https://api.stripe.com/v1/` and accepts HTTPS requests authenticated with API secret keys. The Payment Service sends payment authorization and capture requests containing tokenized card data, amounts, and idempotency keys. The provider returns authorization codes, decline reasons, or error responses synchronously. Webhook callbacks are sent to a dedicated endpoint on the Payment Service for asynchronous event notifications (chargebacks, refunds, disputes).

## Data Flows

External clients send HTTPS requests containing order data (product IDs, quantities, shipping address, payment token) to the API Gateway. The API Gateway validates the JWT token, strips sensitive headers, and forwards the request body over HTTP to the Order Service on the internal network.

The Order Service sends an HTTP GET request to the Inventory Database (via its data access layer) to check stock availability for the requested products. If stock is sufficient, it sends an HTTP POST to reserve the inventory, then publishes an `order.payment.requested` message to the RabbitMQ `orders` exchange. This message contains the order ID, total amount, currency, and payment token.

The Payment Service consumes the `order.payment.requested` message from RabbitMQ, extracts the payment details, and sends an HTTPS POST request to the Stripe API at `https://api.stripe.com/v1/charges` with the tokenized card data, amount, and an idempotency key. Stripe responds with an authorization result.

The Payment Service publishes either a `payment.completed` or `payment.failed` event to the RabbitMQ `payments` exchange. The Order Service consumes this event and updates the order status in the Inventory Database accordingly. If payment failed, the Order Service releases the previously reserved inventory.

Stripe sends asynchronous webhook HTTPS POST callbacks to the Payment Service for events such as chargebacks and refund completions. The Payment Service verifies the webhook signature, processes the event, and updates transaction records in the Inventory Database.

## Trust Boundaries

Trust boundary: External Zone. The external zone encompasses all clients (web browsers, mobile applications) and the External Payment Provider (Stripe). Traffic from this zone is untrusted. All communication uses HTTPS with TLS 1.2 or higher. The API Gateway is the only component that accepts connections from the external zone.

Trust boundary: DMZ. The API Gateway sits in the DMZ, acting as the boundary between untrusted external traffic and the internal service network. It performs authentication (JWT validation), authorization (scope checking), input validation, rate limiting, and request sanitization before forwarding traffic inward. No internal service is directly reachable from the external zone.

Trust boundary: Internal Services Zone. The Order Service, Payment Service, Inventory Database, and Message Queue all reside within the internal services zone. Services communicate over the internal network using HTTP (between services) and TCP with TLS (to the database and message queue). Network policies restrict traffic so that only the API Gateway can reach the Order Service, only the Order Service and Payment Service can reach the Inventory Database, and only the Order Service and Payment Service can connect to the Message Queue.

Trust boundary: External Services Zone. The External Payment Provider (Stripe) operates outside the organization's control. Communication between the Payment Service and Stripe crosses from the internal zone to the external services zone over HTTPS. API secret keys authenticate requests. Webhook callbacks from Stripe into the Payment Service cross from the external services zone back into the internal zone and must be validated using signature verification.
