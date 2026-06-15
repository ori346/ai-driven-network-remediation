# CPU Misconfiguration Showcase

A sample edge workload where one service is deliberately deployed with insufficient CPU resources, causing cascading performance degradation across the system.

## Architecture

```
  ┌───────────────────────────────────────────────────────┐
  │  EDGE CLUSTER                                         │
  │                                                       │
  │  ┌────────┐  POST /enqueue  ┌────────────────┐        │
  │  │ Client ├────────────────►│ Microservice A │        │
  │  │  2 r/s │                 │ (Queue Service) │       │
  │  └────────┘                 └───────┬────────┘        │
  │                                     │                 │
  │                            POST /process              │
  │                                     │                 │
  │                             ┌───────▼─────────┐       │
  │                             │ Microservice B  │       │
  │                             │(Compute Service)│       │
  │                             │                 │       │
  │                             │  CPU: 25m limit │       │
  │                             │ (should be 250m)│  BUG  │
  │                             └─────────────────┘       │
  │                                                       │
  └───────────────────────────────────────────────────────┘
```

## How It Breaks

1. **Client** sends 2 requests/second to **Microservice A**, each asking to count primes up to 30,000
2. **Microservice A** queues them and forwards to **Microservice B**
3. **Microservice B** is CPU-starved (25m limit instead of 250m) — prime counting takes far longer than expected
4. The queue in Microservice A builds up faster than it drains
5. Structured JSON logs with `queue_depth` are emitted, signaling the problem

## Components

| Component | Description | Location |
|---|---|---|
| Client | Async load generator (configurable rate and prime target) | `client/` |
| Microservice A | Queue service - buffers and forwards requests | `microservice-a/` |
| Microservice B | CPU-intensive compute service (prime counting) | `microservice-b/` |
| Helm Chart | Kubernetes deployment (includes the CPU bug) | `chart/` |

## Quick Start

```bash
# Build and push container images
make build-images
make push-images

# Deploy microservices to edge namespace
make deploy

# Deploy Grafana alerting rules to hub namespace
make deploy-alerting

# Or do everything at once
make deploy-all
```

## Cleanup

```bash
make undeploy-all
```
