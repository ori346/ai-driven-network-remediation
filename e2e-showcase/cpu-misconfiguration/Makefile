CONTAINER_TOOL  ?= podman
REGISTRY        ?= quay.io/rh-ai-quickstart
VERSION         ?= 0.1.0
ARCH            ?= linux/amd64
PUSH_EXTRA_ARGS ?=

NAMESPACE       ?= hub
EDGE_NAMESPACE  ?= edge

SHOWCASE_RELEASE := cpu-misconfiguration
SHOWCASE_CHART   := chart

SHOWCASE_CLIENT_IMG          := $(REGISTRY)/showcase-client:$(VERSION)
SHOWCASE_MICROSERVICE_A_IMG  := $(REGISTRY)/showcase-microservice-a:$(VERSION)
SHOWCASE_MICROSERVICE_B_IMG  := $(REGISTRY)/showcase-microservice-b:$(VERSION)

# ── Images ───────────────────────────────────────────────────────

.PHONY: build-images
build-images:
	$(CONTAINER_TOOL) build -t $(SHOWCASE_CLIENT_IMG) --platform=$(ARCH) -f client/Containerfile client
	$(CONTAINER_TOOL) build -t $(SHOWCASE_MICROSERVICE_A_IMG) --platform=$(ARCH) -f microservice-a/Containerfile microservice-a
	$(CONTAINER_TOOL) build -t $(SHOWCASE_MICROSERVICE_B_IMG) --platform=$(ARCH) -f microservice-b/Containerfile microservice-b

.PHONY: push-images
push-images:
	$(CONTAINER_TOOL) push $(SHOWCASE_CLIENT_IMG) $(PUSH_EXTRA_ARGS)
	$(CONTAINER_TOOL) push $(SHOWCASE_MICROSERVICE_A_IMG) $(PUSH_EXTRA_ARGS)
	$(CONTAINER_TOOL) push $(SHOWCASE_MICROSERVICE_B_IMG) $(PUSH_EXTRA_ARGS)

# ── Edge Deployment ──────────────────────────────────────────────

.PHONY: deploy
deploy: edge-namespace
	helm upgrade --install $(SHOWCASE_RELEASE) $(SHOWCASE_CHART) \
		--namespace $(EDGE_NAMESPACE) \
		--set image.registry=$(REGISTRY) \
		--set image.tag=$(VERSION) \
		--wait --timeout 5m

.PHONY: undeploy
undeploy:
	helm uninstall $(SHOWCASE_RELEASE) --namespace $(EDGE_NAMESPACE) --ignore-not-found

.PHONY: edge-namespace
edge-namespace:
	@oc create namespace $(EDGE_NAMESPACE) 2>/dev/null ||:

# ── Hub Alerting ─────────────────────────────────────────────────

.PHONY: deploy-alerting
deploy-alerting:
	HUB_NAMESPACE=$(NAMESPACE) EDGE_NAMESPACE=$(EDGE_NAMESPACE) envsubst < alerting/grafana-alerting.yaml \
		| oc apply -n $(NAMESPACE) -f -

.PHONY: undeploy-alerting
undeploy-alerting:
	oc delete configmap grafana-alerting -n $(NAMESPACE) --ignore-not-found

# ── Full Showcase ────────────────────────────────────────────────

.PHONY: deploy-all
deploy-all: deploy deploy-alerting

.PHONY: undeploy-all
undeploy-all: undeploy undeploy-alerting
