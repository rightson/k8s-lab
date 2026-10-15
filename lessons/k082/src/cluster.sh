#!/usr/bin/env bash
# Prepared for an explicitly owned, disposable cluster; NOT live-tested in this run.
set -euo pipefail
export KIND_EXPERIMENTAL_PROVIDER=docker
LESSON_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PRIVATE_DIR="$LESSON_DIR/.private"
KUBE_FILE="$PRIVATE_DIR/kubeconfig"
MARKER_FILE="$PRIVATE_DIR/cluster-uid"
CLUSTER_NAME="k082-foundations"
CONTEXT_NAME="kind-k082-foundations"
NAMESPACE_NAME="k082-foundations"
NODE_IMAGE="kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5"
test "$#" -gt 0 || { echo "Action required" >&2; exit 2; }
action="$1"
k() { kubectl --kubeconfig "$KUBE_FILE" --context "$CONTEXT_NAME" -n "$NAMESPACE_NAME" "$@"; }
guard() {
  test -f "$KUBE_FILE" && test -f "$MARKER_FILE" || { echo "No owned cluster marker" >&2; exit 2; }
  actual_uid="$(kubectl --kubeconfig "$KUBE_FILE" --context "$CONTEXT_NAME" get namespace kube-system -o jsonpath='{.metadata.uid}')"
  recorded_uid="$(<"$MARKER_FILE")"
  test -n "$recorded_uid" && test "$actual_uid" = "$recorded_uid" || { echo "Cluster UID mismatch" >&2; exit 2; }
}
validate_pod() {
  test "$#" -eq 2 || { echo "Action and explicit lesson Pod required" >&2; exit 2; }
  [[ "$2" =~ ^api-[a-z0-9]+-[a-z0-9]+$ ]] || { echo "Invalid lesson Pod name" >&2; exit 2; }
  POD_NAME="$2"
  label="$(k get pod "$POD_NAME" -o jsonpath='{.metadata.labels.app}')"
  test "$label" = "k082-api" || { echo "Not a lesson Pod" >&2; exit 2; }
}
request() {
  k exec "$POD_NAME" -c api -- python -c 'import sys,urllib.request; u="http://127.0.0.1:8080"+sys.argv[1]; r=urllib.request.Request(u,method=sys.argv[2]); print(urllib.request.urlopen(r,timeout=3).read().decode())' "$1" "$2"
}
case "$action" in
  create)
    test "$#" -eq 3 && test "$2" = "--confirm-isolated" || { echo "Require --confirm-isolated BASE_IMAGE" >&2; exit 2; }
    BASE_IMAGE="$3"
    [[ "$BASE_IMAGE" =~ ^python:3\.12\.14-slim-bookworm@sha256:[0-9a-f]{64}$ ]] || { echo "Supply a reviewed digest-pinned Python base" >&2; exit 2; }
    for binary in docker kind kubectl python3; do
      command -v "$binary" >/dev/null || { echo "Missing $binary; no installation/escalation attempted" >&2; exit 2; }
    done
    [[ "$(kind version)" == "kind v0.33.0 "* ]] || { echo "Require kind v0.33.0" >&2; exit 2; }
    test ! -e "$KUBE_FILE" && test ! -e "$MARKER_FILE" || { echo "Existing local state; inspect before retry" >&2; exit 2; }
    clusters="$(kind get clusters)"
    if [[ $'\n'"$clusters"$'\n' == *$'\n'"$CLUSTER_NAME"$'\n'* ]]; then
      echo "Cluster exists; refusing adoption" >&2; exit 2
    fi
    mkdir -p "$PRIVATE_DIR"
    chmod 700 "$PRIVATE_DIR"
    kind create cluster --name "$CLUSTER_NAME" --kubeconfig "$KUBE_FILE" --config "$LESSON_DIR/manifests/kind.yaml" --image "$NODE_IMAGE" --wait 120s
    chmod 600 "$KUBE_FILE"
    kubectl --kubeconfig "$KUBE_FILE" --context "$CONTEXT_NAME" get namespace kube-system -o jsonpath='{.metadata.uid}' > "$MARKER_FILE"
    chmod 600 "$MARKER_FILE"
    guard
    IMAGE_SUFFIX="$(python3 -c 'import hashlib,sys,pathlib; p=pathlib.Path(sys.argv[1]); print(hashlib.sha256(sys.argv[2].encode()+(p/"src/api.py").read_bytes()+(p/"src/Dockerfile").read_bytes()).hexdigest()[:20])' "$LESSON_DIR" "$BASE_IMAGE")"
    APP_IMAGE="k082-api:$IMAGE_SUFFIX"
    docker build --build-arg "BASE_IMAGE=$BASE_IMAGE" -t "$APP_IMAGE" "$LESSON_DIR/src"
    docker image inspect "$APP_IMAGE" --format '{{.Id}}' > "$PRIVATE_DIR/app-image-id"
    printf '%s\n' "$APP_IMAGE" > "$PRIVATE_DIR/app-image-tag"
    printf '%s\n' "$BASE_IMAGE" > "$PRIVATE_DIR/base-image"
    kind load docker-image --name "$CLUSTER_NAME" "$APP_IMAGE"
    python3 "$LESSON_DIR/src/render.py" "$APP_IMAGE" > "$PRIVATE_DIR/rendered.yaml"
    k apply -f - <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: k082-foundations
  labels:
    lesson: k082
    pod-security.kubernetes.io/enforce: restricted
YAML
    k apply --dry-run=server -f "$PRIVATE_DIR/rendered.yaml"
    k apply -f "$PRIVATE_DIR/rendered.yaml"
    k rollout status deployment/api --timeout=120s
    ;;
  status)
    guard
    kubectl --kubeconfig "$KUBE_FILE" --context "$CONTEXT_NAME" get nodes -o 'custom-columns=NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status,KUBELET:.status.nodeInfo.kubeletVersion,RUNTIME:.status.nodeInfo.containerRuntimeVersion,KERNEL:.status.nodeInfo.kernelVersion'
    k get deployment,replicaset,pods,service -o wide
    k get pods -l app=k082-api -o jsonpath='{range .items[*]}{.metadata.name}{" uid="}{.metadata.uid}{" node="}{.spec.nodeName}{" restarts="}{.status.containerStatuses[0].restartCount}{" ready="}{.status.containerStatuses[0].ready}{" imageID="}{.status.containerStatuses[0].imageID}{"\n"}{end}'
    k get endpointslices -l kubernetes.io/service-name=api -o jsonpath='{range .items[*].endpoints[*]}{.targetRef.name}{" ready="}{.conditions.ready}{"\n"}{end}'
    ;;
  identity|increment|crash|not-ready|ready|delete-pod)
    guard; validate_pod "$@"
    case "$action" in
      identity) request /id GET ;;
      increment) request /increment POST ;;
      crash) request /admin/crash POST ;;
      not-ready) request /admin/not-ready POST ;;
      ready) request /admin/ready POST ;;
      delete-pod) k delete pod "$POD_NAME" --wait=true --timeout=60s ;;
    esac
    ;;
  service-request)
    guard; validate_pod "$@"
    k exec "$POD_NAME" -c api -- python -c 'import urllib.request; print(urllib.request.urlopen("http://api:8080/id",timeout=3).read().decode())'
    ;;
  bad-rollout)
    guard
    k set env deployment/api VERSION=v2 FAIL_READINESS=1
    k rollout status deployment/api --timeout=15s
    ;;
  undo)
    guard
    k rollout undo deployment/api
    k rollout status deployment/api --timeout=120s
    ;;
  cleanup)
    test "$#" -eq 2 && test "$2" = "--confirm-isolated" || { echo "Require --confirm-isolated" >&2; exit 2; }
    guard
    kind delete cluster --name "$CLUSTER_NAME" --kubeconfig "$KUBE_FILE"
    clusters="$(kind get clusters)"
    if [[ $'\n'"$clusters"$'\n' == *$'\n'"$CLUSTER_NAME"$'\n'* ]]; then
      echo "Cluster still exists; ownership files retained" >&2; exit 2
    fi
    rm -- "$KUBE_FILE" "$MARKER_FILE"
    ;;
  *) echo "Actions: create/status/identity/increment/crash/not-ready/ready/delete-pod/service-request/bad-rollout/undo/cleanup" >&2; exit 2 ;;
esac

