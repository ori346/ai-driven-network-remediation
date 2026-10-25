# CPU Misconfiguration Demo

This alert demo runs a client, microservice A, and CPU-starved microservice B. B
starts with a 25m CPU limit; the remediation raises that limit. The chart can put
all three components on one cluster or split B onto a second cluster.

## Build and push

Choose a registry you can push to, then use the same registry and version for
deployment. From the repository root, build and push with:

```bash
make cpu-demo-build-images CPU_DEMO_REGISTRY=registry.example/team
make cpu-demo-push-images CPU_DEMO_REGISTRY=registry.example/team
```

`CPU_DEMO_REGISTRY` defaults to `EDGE_REGISTRY`; `CPU_DEMO_VERSION` defaults to
`VERSION`.

## Deploy

The root deployment can install the demo after the normal hub and edge
deployment. It uses the same `CLUSTER_COUNT` mode as the rest of the stack:

```bash
make deploy ENABLE_CPU_DEMO=true CPU_DEMO_REGISTRY=registry.example/team
```

If the stack is already deployed, install or reset only the demo workloads with
the root wrapper, using the same topology mode as the stack:

```bash
make cpu-demo-deploy CLUSTER_COUNT=1 CPU_DEMO_REGISTRY=registry.example/team
```

With `CLUSTER_COUNT=1`, all components use the current kubeconfig and the demo
site defaults to `EDGE_SITE_ID`. With `CLUSTER_COUNT>=2`, the demo uses the first
two spoke names (`SPOKE_NAME_PREFIX-01` and `SPOKE_NAME_PREFIX-02`); run from the
ACM hub context. The client and microservice A run on SITE_A; B and its Route
run on SITE_B. Override either default with `CPU_DEMO_SITE_A` or
`CPU_DEMO_SITE_B`.

```bash
make deploy CLUSTER_COUNT=2 ENABLE_CPU_DEMO=true \
  CPU_DEMO_REGISTRY=registry.example/team
```

To install the demo on an already deployed multi-cluster stack, use
`make cpu-demo-deploy CLUSTER_COUNT=2 CPU_DEMO_REGISTRY=registry.example/team`.

When enabled, root deployment passes the effective demo site IDs to the chatbot
configuration. If overriding `CPU_DEMO_SITE_A` or `CPU_DEMO_SITE_B`, use those
same overrides with `make deploy ENABLE_CPU_DEMO=true` so the chatbot points to
the demo sites.

Click **Trigger CPU Misconfiguration Demo** in the UI to publish the alert. That
button only publishes an alert; it does not deploy or reset the workloads. This
demo does not run the LLM judge. After remediation, reset microservice B's CPU
limit to 25m with `make cpu-demo-deploy`,
passing the same topology and registry settings used for deployment.

## Remove

Root teardown removes the demo before removing hub or cluster resources when
`ENABLE_CPU_DEMO=true`:

```bash
make teardown ENABLE_CPU_DEMO=true CLUSTER_COUNT=1
```

For multi-cluster teardown, pass the same `CLUSTER_COUNT` and site overrides,
and run from the ACM hub context. The standalone sub-Makefile `deploy` and
`undeploy` targets remain available.
