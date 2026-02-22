#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
K8S_DIR="${ROOT_DIR}/kubernetes"
KUBECONFIG_PATH="${1:-${SCRIPT_DIR}/generated/k3s.yaml}"

for cmd in kubectl helm kubeseal; do
  command -v "${cmd}" >/dev/null || {
    echo "Missing required command: ${cmd}"
    exit 1
  }
done

if [[ ! -f "${KUBECONFIG_PATH}" ]]; then
  echo "Kubeconfig not found: ${KUBECONFIG_PATH}"
  exit 1
fi

export KUBECONFIG="${KUBECONFIG_PATH}"

helm repo add argo https://argoproj.github.io/argo-helm
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm repo update

helm upgrade --install argocd argo/argo-cd \
  -f "${K8S_DIR}/apps/core/argocd/helm/values-override.yaml" \
  -n argocd \
  --create-namespace

echo "Waiting for ArgoCD CRDs and server deployment..."
kubectl wait --for=condition=Established crd/applications.argoproj.io --timeout=5m
kubectl -n argocd rollout status deployment/argocd-server --timeout=5m

helm upgrade --install sealed-secrets sealed-secrets/sealed-secrets \
  -f "${K8S_DIR}/apps/core/sealed-secrets/helm/values-override.yaml" \
  -n sealed-secrets \
  --create-namespace

echo "Waiting for sealed-secrets controller..."
SEALED_DEPLOY=""
until [[ -n "${SEALED_DEPLOY}" ]]; do
  SEALED_DEPLOY="$(kubectl -n sealed-secrets get deployment -l app.kubernetes.io/instance=sealed-secrets -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"
  sleep 2
done
kubectl -n sealed-secrets rollout status "deployment/${SEALED_DEPLOY}" --timeout=5m

# Seal and apply the ArgoCD Git repository secret.
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

kubeseal \
  --controller-name sealed-secrets \
  --controller-namespace sealed-secrets \
  --format yaml \
  < "${K8S_DIR}/data-sources/github-repo.yaml" \
  > "${TMP_DIR}/github-repo.sealed.yaml"

kubectl apply -f "${TMP_DIR}/github-repo.sealed.yaml"

# Re-seal any local unsealed files if present, then apply.
while IFS= read -r -d '' unsealed_file; do
  sealed_file="${unsealed_file%.unsealed.yaml}.sealed.yaml"
  kubeseal \
    --controller-name sealed-secrets \
    --controller-namespace sealed-secrets \
    --format yaml \
    < "${unsealed_file}" \
    > "${sealed_file}"
  kubectl apply -f "${sealed_file}"
done < <(find "${K8S_DIR}" -type f -name "*.unsealed.yaml" -print0)

kubectl apply -f "${K8S_DIR}/argocd-boostrap/track-create-apps-and-data-sources.yaml"

echo "ArgoCD bootstrap applied successfully."
