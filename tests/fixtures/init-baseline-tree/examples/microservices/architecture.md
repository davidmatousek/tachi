# Microservices E-Commerce Platform — Architecture

Example architecture input for a microservices-based e-commerce platform. This diagram demonstrates a traditional distributed system with synchronous REST calls between services, asynchronous event-driven communication via a message queue, and clear trust boundary separation across four zones.

format: mermaid

```mermaid
flowchart TD
    Client[Client Application]

    subgraph External Clients
        Client
    end

    subgraph DMZ
        Gateway[API Gateway]
        Registry[Service Registry]
    end

    subgraph Internal Services
        OrderSvc[Order Service]
        PaymentSvc[Payment Service]
        NotifSvc[Notification Service]
        MQ[(Message Queue)]
        OrderDB[(Order Database)]
        InventoryDB[(Inventory Database)]
    end

    subgraph External Services
        PaymentProvider[External Payment Provider]
    end

    Client -->|HTTPS Request| Gateway
    Gateway -->|Service Lookup| Registry
    Registry -->|Endpoint List| Gateway
    Gateway -->|REST / Route Request| OrderSvc
    Gateway -->|REST / Route Request| PaymentSvc

    OrderSvc -->|Read/Write Orders| OrderDB
    OrderSvc -->|Check Stock / Reserve Items| InventoryDB
    OrderSvc -->|Publish OrderCreated Event| MQ
    OrderSvc -->|REST / Payment Request| PaymentSvc

    PaymentSvc -->|HTTPS / Charge Request| PaymentProvider
    PaymentProvider -->|Payment Result| PaymentSvc
    PaymentSvc -->|Publish PaymentCompleted Event| MQ

    MQ -->|OrderCreated Event| NotifSvc
    MQ -->|PaymentCompleted Event| NotifSvc
    NotifSvc -->|Send Email / SMS| Client
```

## Component Summary

| Component | DFD Element Type | Notes |
|-----------|------------------|-------|
| Client Application | External Entity | End-user browser or mobile app; untrusted zone |
| API Gateway | Process | Single entry point; routes requests, enforces auth; DMZ zone |
| Service Registry | Process | Maintains service endpoint catalog for dynamic discovery; DMZ zone |
| Order Service | Process | Handles order creation, validation, and lifecycle; trusted zone |
| Payment Service | Process | Orchestrates payment flow with external provider; trusted zone |
| Notification Service | Process | Consumes async events and delivers user notifications; trusted zone |
| Message Queue | Data Store | Async event bus for decoupled service-to-service communication; trusted zone |
| Order Database | Data Store | Persistent storage for order records and state; trusted zone |
| Inventory Database | Data Store | Persistent storage for product stock levels; trusted zone |
| External Payment Provider | External Entity | Third-party payment processor (e.g., Stripe); untrusted zone |
