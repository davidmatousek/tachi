# Orchestration Safe Operation Guide

## Overview

The AOD orchestrator infrastructure supports specific modes for safe operation during active orchestration runs. This guide covers how to start services, handle restarts, troubleshoot port conflicts, and interpret dashboard connection states.

---

## Starting Services for Orchestration

### `make start-stable` (Recommended for Orchestration)

Use `make start-stable` when running orchestration sessions. This mode starts the backend **without hot-reload**, preventing WebSocket drops caused by automatic restarts.

```bash
make start-stable
```

### `make start` (Development Mode)

Use `make start` during normal development. This mode starts the backend with `--reload`, which automatically restarts the server when backend files change.

```bash
make start
```

**Warning**: Editing backend files during an active orchestration run **will** restart the backend, drop WebSocket connections, and may disrupt active agent sessions. Use `make start-stable` to avoid this.

---

## Restarting Services

### `make restart`

Stops and restarts both the backend and frontend processes.

```bash
make restart
```

**When to use**: After manual code changes that require a full restart, or when recovering from a stuck state.

---

## Port Conflict Troubleshooting

`make start` automatically detects and cleans up orphan processes that may be occupying required ports:

- Only AOD-related processes are auto-killed (uvicorn, Python, node).
- If a port is occupied by an **unrelated** process, a warning is shown with manual resolution steps.

### Manual Fallback

If automatic cleanup does not resolve the conflict, kill processes on the required ports manually:

```bash
lsof -ti:8000 | xargs kill -9   # Backend (uvicorn)
lsof -ti:5173 | xargs kill -9   # Frontend (node/vite)
```

---

## Dashboard Connection States

The dashboard displays a connection indicator reflecting the current WebSocket state:

| State | Indicator | Description |
|-------|-----------|-------------|
| **Live** | Green dot | WebSocket connected. Real-time updates are active. |
| **Reconnecting...** | Amber banner | Backend restarted. Auto-reconnecting with exponential backoff. |
| **Polling** | Orange banner | WebSocket failed to reconnect. Polling fallback is active (5-second interval). |

---

## Best Practices

- Use `make start-stable` during orchestration runs to prevent WebSocket disruptions.
- Use `make start` during development for hot-reload convenience.
- If you must edit backend code during an active orchestration, expect a brief dashboard disconnection while the server restarts.
- Check the dashboard connection banner to confirm reconnection after any backend restart.
