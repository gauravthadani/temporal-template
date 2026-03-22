# Requester Use Case

A Temporal Go sample demonstrating a scheduler workflow pattern for managing concurrent and sequential request processing across modules.

## Overview

This sample implements a pattern where incoming requests are grouped by module (LZ) and processed with the following rules:

- **Intra-module requests** (same `ModuleID`) are processed **sequentially**
- **Inter-module requests** (different `ModuleID`) are processed **concurrently**

### Architecture

```
HTTP POST /signal
        │
        ▼
   Starter (HTTP server)
        │  SignalWithStartWorkflow (per-LZ)
        ▼
RequesterSchedulerWorkflow
        │  routes by ModuleID
        ├──► Module A ──► LZRequestWorkflow ──► Activity
        ├──► Module B ──► LZRequestWorkflow ──► Activity
        └──► Module C ──► LZRequestWorkflow ──► Activity
```

- The **starter** runs an HTTP server on `:8080` that accepts `POST /signal` requests and uses `SignalWithStartWorkflow` to deliver them to a per-LZ scheduler workflow.
- The **`RequesterSchedulerWorkflow`** receives signals, routes each request to the appropriate `Module` by `ModuleID`, and manages completion.
- Each **`Module`** processes its requests sequentially by executing `LZRequestWorkflow` as a child workflow for each request.
- The **`LZRequestWorkflow`** runs an `Activity` that simulates work (30 seconds with heartbeating).
- The scheduler workflow completes when all in-flight requests finish and no new requests arrive within 30 seconds.

## Running the Sample

### Prerequisites

- Go 1.23+
- A running Temporal server

Start the Temporal dev server in a terminal:

```bash
temporal server start-dev
```

You should see output like:

```
CLI 1.5.1 (Server 1.29.1, UI 2.42.1)

Server:  localhost:7233
UI:      http://localhost:8233
Metrics: http://localhost:57058/metrics
```

### 1. Start the Worker

In a second terminal:

```bash
go run helloworld/worker/main.go
```

Expected output:

```
2025/12/22 15:00:15 INFO  No logger configured for temporal client. Created default one.
2025/12/22 15:00:16 INFO  Started Worker Namespace default TaskQueue hello-world WorkerID 82087
```

### 2. Start the HTTP Server (Starter)

In a third terminal:

```bash
go run helloworld/starter/main.go
```

Expected output:

```
2025/12/22 15:07:24 Listening on :8080
```

### 3. Send Requests

Send requests via HTTP POST to `/signal`. Each request must include `LZ`, `ModuleID`, and `RequestID` fields:

```bash
# Two requests for the same LZ but different modules — processed concurrently
curl -X POST http://localhost:8080/signal \
  -H "Content-Type: application/json" \
  -d '{"LZ": "us-east-1", "ModuleID": "module-a", "RequestID": "req-1"}'

curl -X POST http://localhost:8080/signal \
  -H "Content-Type: application/json" \
  -d '{"LZ": "us-east-1", "ModuleID": "module-b", "RequestID": "req-2"}'

# Two requests for the same LZ and same module — processed sequentially
curl -X POST http://localhost:8080/signal \
  -H "Content-Type: application/json" \
  -d '{"LZ": "us-east-1", "ModuleID": "module-a", "RequestID": "req-3"}'
```

A `202 Accepted` response indicates the request was successfully queued.

## Key Concepts

| Concept | Description |
|---|---|
| `SignalWithStartWorkflow` | Starts the scheduler workflow if not running, then signals it — idempotent per LZ |
| Per-LZ scheduler | One `RequesterSchedulerWorkflow` runs per LZ, identified by `requester-scheduler-scheduler-{LZ}` |
| Module isolation | Each unique `ModuleID` gets its own `Module` with a sequential processing queue |
| Child workflows | Each individual request is executed as a `LZRequestWorkflow` child workflow |
| Idle timeout | Scheduler completes after 30 seconds of inactivity (no new requests) |
| Activity heartbeating | The `Activity` heartbeats every second during its 30-second execution |

## Project Structure

```
helloworld/
├── scheduler/
│   ├── module.go        # Module type: per-ModuleID sequential queue
│   ├── registration.go  # Registration: routes requests, tracks completion
│   └── workflows.go     # RequesterSchedulerWorkflow, LZRequestWorkflow, Activity
├── starter/
│   └── main.go          # HTTP server; signals workflows via SignalWithStartWorkflow
└── worker/
    └── main.go          # Temporal worker; registers workflows and activities
```