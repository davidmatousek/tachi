# Brindle Freight Platform: architecture

The Brindle Freight Platform is a multi-agent system that turns operator requests into planned, reviewed and audited shipment actions. Operators submit requests through a web portal. An intake agent structures each request, a planner decomposes it, a router assigns subtasks to worker agents, and a reviewer presents the result for approval. Agents reach carrier systems only through one tool server, and every approval and tool call is written to an append-only ledger.

## Components

- **client-portal** (external entity, Public Internet): Browser front end where operators submit shipment requests and approve agent proposals.
- **edge-gateway** (process, Edge DMZ): Ingress proxy that terminates TLS, applies request limits and screens prompts before the intake agent.
- **auth-broker** (process, Edge DMZ): Token broker that validates operator and partner credentials and mints short-lived session grants.
- **intake-agent** (process, Agent Runtime Zone): LLM-backed agent that turns free-text requests into structured shipment tasks and answers operators.
- **planner-agent** (process, Agent Runtime Zone): Planning agent that decomposes tasks, selects tools and assigns subtasks to the router.
- **worker-2** (process, Agent Runtime Zone): Worker agent that optimises routes and looks up carrier rates through the tool server.
- **tool-server-1** (process, Agent Runtime Zone): Tool server that exposes carrier rate, booking, label and customs tools to the agents.
- **model-gateway** (process, Agent Runtime Zone): Gateway that fronts the hosted foundation models and enforces per-agent quotas.
- **vector-store-a** (data store, Data Zone): Vector database holding embedded carrier documents and ticket history.
- **audit-ledger** (data store, Operations Zone): Append-only ledger of approvals, tool calls and administrative actions.
- **partner-sandbox** (external entity, Partner Exchange): Carrier test harness that submits trial manifests and replays recorded webhooks against the gateway.

## Trust zones

- **Public Internet** (untrusted): client-portal.
- **Edge DMZ** (semi-trusted): edge-gateway, auth-broker.
- **Agent Runtime Zone** (trusted): intake-agent, planner-agent, worker-2, tool-server-1, model-gateway.
- **Data Zone** (trusted): vector-store-a.
- **Operations Zone** (trusted): audit-ledger.
- **Partner Exchange** (semi-trusted): partner-sandbox.

## Data flows

- client-portal sends operator requests and session cookies to edge-gateway over HTTPS (TLS 1.3).
- edge-gateway sends token introspection requests to auth-broker over gRPC over mTLS.
- edge-gateway sends screened operator requests to intake-agent over HTTP/2 over mTLS.
- planner-agent sends prompts and completions to model-gateway over HTTPS (TLS 1.3).
- worker-2 sends tool calls (json-rpc) to tool-server-1 over HTTPS (TLS 1.3).
- worker-2 sends similarity queries to vector-store-a over PostgreSQL over TLS.
- tool-server-1 sends tool call records to audit-ledger over gRPC over mTLS.
- partner-sandbox sends trial manifests and replayed webhooks to edge-gateway over HTTPS (TLS 1.3).

## Notes

No component in this description carries an asset-sensitivity tag. The platform and every name in it are invented for testing.
