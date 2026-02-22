#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
K8S_DIR="${ROOT_DIR}/kubernetes"
SECRETS_DIR="${K8S_DIR}/secrets"
GEN_DIR="${SCRIPT_DIR}/generated"

mkdir -p "${GEN_DIR}"

echo "Starting minikube"
minikube start
kubectl config use-context minikube

helm repo add argo https://argoproj.github.io/argo-helm
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm repo update

helm upgrade --install argocd argo/argo-cd \
  -f "${K8S_DIR}/apps/core/argocd/helm/values-override.yaml" \
  -n argocd \
  --create-namespace

kubectl wait --for=condition=Established crd/applications.argoproj.io --timeout=5m

helm upgrade --install sealed-secrets sealed-secrets/sealed-secrets \
  -f "${K8S_DIR}/apps/core/sealed-secrets/helm/values-override.yaml" \
  -n sealed-secrets \
  --create-namespace

kubectl -n sealed-secrets rollout status deployment/sealed-secrets --timeout=5m

find "${SECRETS_DIR}" -type f -name "*.unsealed.yaml" -print0 | while IFS= read -r -d '' unsealed_file; do
  sealed_file="${unsealed_file%.unsealed.yaml}.sealed.yaml"
  kubeseal \
    --controller-name sealed-secrets \
    --controller-namespace sealed-secrets \
    --format yaml \
    < "${unsealed_file}" \
    > "${sealed_file}"
done

kubeseal \
  --controller-name sealed-secrets \
  --controller-namespace sealed-secrets \
  --format yaml \
  < "${K8S_DIR}/data-sources/github-repo.yaml" \
  > "${GEN_DIR}/github-repo.sealed.yaml"

kubectl apply -f "${GEN_DIR}/github-repo.sealed.yaml"
kubectl apply -f "${K8S_DIR}/argocd-boostrap/track-create-apps-and-data-sources.yaml"

echo "Done. Context=minikube"
