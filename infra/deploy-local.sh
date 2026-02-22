#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
K8S_DIR="${ROOT_DIR}/kubernetes"
SECRETS_DIR="${K8S_DIR}/secrets"
GEN_DIR="${SCRIPT_DIR}/generated"
KUBEBOX_KUBECONFIG_UNSEALED="${SECRETS_DIR}/visibility/kubebox-kubeconfig.unsealed.yaml"
ARGOCD_ADMIN_USERNAME="${ARGOCD_ADMIN_USERNAME:-}"
ARGOCD_ADMIN_PASSWORD="${ARGOCD_ADMIN_PASSWORD:-}"

mkdir -p "${GEN_DIR}"

if [[ -z "${ARGOCD_ADMIN_USERNAME}" || -z "${ARGOCD_ADMIN_PASSWORD}" ]]; then
  echo "Set ARGOCD_ADMIN_USERNAME and ARGOCD_ADMIN_PASSWORD before running."
  exit 1
fi

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
kubectl -n argocd rollout status deployment/argocd-server --timeout=5m

echo "Updating ArgoCD admin credentials"
kubectl -n argocd port-forward svc/argocd-server 8080:80 >/tmp/argocd-port-forward.log 2>&1 &
ARGOCD_PF_PID=$!
sleep 3

ARGOCD_INITIAL_PASSWORD="$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
argocd login localhost:8080 --plaintext --username "${ARGOCD_ADMIN_USERNAME}" --password "${ARGOCD_INITIAL_PASSWORD}" --insecure
argocd account update-password \
  --account "${ARGOCD_ADMIN_USERNAME}" \
  --current-password "${ARGOCD_INITIAL_PASSWORD}" \
  --new-password "${ARGOCD_ADMIN_PASSWORD}"
kill "${ARGOCD_PF_PID}"

helm upgrade --install sealed-secrets sealed-secrets/sealed-secrets \
  -f "${K8S_DIR}/apps/core/sealed-secrets/helm/values-override.yaml" \
  -n sealed-secrets \
  --create-namespace

kubectl -n sealed-secrets rollout status deployment/sealed-secrets --timeout=5m

echo "Generating kubebox kubeconfig unsealed secret"
kubectl config view --raw --minify --flatten > "${GEN_DIR}/kubebox-kubeconfig.yaml"
cat > "${KUBEBOX_KUBECONFIG_UNSEALED}" <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: kubeconfig-external-secret
  namespace: kubebox
type: Opaque
stringData:
  kubeconfig: |
$(sed 's/^/    /' "${GEN_DIR}/kubebox-kubeconfig.yaml")
EOF

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
kubectl apply -f "${K8S_DIR}/argocd-boostrap/track-create-apps-and-data-sources-local.yaml"

kubectl create namespace cloudflare-tunnel-ingress-controller --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace model-pipeline --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace kubebox --dry-run=client -o yaml | kubectl apply -f -

find "${SECRETS_DIR}" -type f -name "*.sealed.yaml" -print0 | while IFS= read -r -d '' sealed_file; do
  kubectl apply -f "${sealed_file}"
done

echo "done"
