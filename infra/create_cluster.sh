#!/usr/bin/env bash
set -euo pipefail

# --- prerequisites ---
command -v terraform >/dev/null
command -v talosctl >/dev/null
command -v jq >/dev/null

# --- paths ---
TF_DIR="tf"
PATCH_DIR="patches"
GEN_DIR="generated"
SECRETS_FILE="${GEN_DIR}/secrets.yaml"

# --- terraform ---
cd "${TF_DIR}"
terraform init -input=false
terraform apply -auto-approve -input=false

IP="$(terraform output -raw elastic_ip)"
cd ..

if [[ -z "${IP}" ]]; then
  echo "ERROR: elastic_ip output is empty"
  exit 1
fi

# --- talos client config ---
talosctl config endpoints "${IP}"
talosctl config node "${IP}"

# --- generate secrets if missing ---
mkdir -p "${GEN_DIR}"
if [[ ! -f "${SECRETS_FILE}" ]]; then
  talosctl gen secrets > "${SECRETS_FILE}"
fi

# --- generate talos config ---
talosctl gen config \
  --force \
  icantkube-cluster "${IP}" \
  --with-secrets "${SECRETS_FILE}" \
  --config-patch @"${PATCH_DIR}/allow-controlplane-workloads.yaml" \
  --config-patch @"${PATCH_DIR}/dhcp.yaml" \
  --config-patch @"${PATCH_DIR}/kublet-cert-rotation.yaml" \
  --config-patch @"${PATCH_DIR}/predictable-interface-names.yaml" \
  --config-patch @"${PATCH_DIR}/extra-mounts.yaml" \
  --config-patch @"${PATCH_DIR}/add-disk.yaml" \
  --config-patch @"${PATCH_DIR}/bind-addresses.yaml" \
  --output "${GEN_DIR}"

# --- apply config ---
talosctl apply-config \
  -f "${GEN_DIR}/controlplane.yaml" \
  -n "${IP}" \
  --insecure

# --- bootstrap (idempotent) ---
if ! talosctl health -n "${IP}" >/dev/null 2>&1; then
  talosctl bootstrap -n "${IP}"
fi

# --- wait for kube-apiserver ---
talosctl health \
  -n "${IP}" \
  --wait-timeout 10m

# --- fetch kubeconfig ---
talosctl kubeconfig \
  -n "${IP}" \
  --force

echo "Cluster ready at ${IP}"
