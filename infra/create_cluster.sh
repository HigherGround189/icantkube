#!/usr/bin/env bash
set -euo pipefail

# --- prerequisites ---
command -v terraform >/dev/null
command -v talosctl >/dev/null

# # --- paths ---
TF_DIR="terraform"
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

# --- generate secrets ---
mkdir -p "${GEN_DIR}"
talosctl gen secrets --output-file "${SECRETS_FILE}" --force

# --- generate talos config ---
talosctl gen config \
  --force \
  icantkube-cluster "https://${IP}" \
  --with-secrets "${SECRETS_FILE}" \
  --config-patch @"${PATCH_DIR}/allow-controlplane-workloads.yaml" \
  --config-patch @"${PATCH_DIR}/dhcp.yaml" \
  --config-patch @"${PATCH_DIR}/kubelet-cert-rotation.yaml" \
  --config-patch @"${PATCH_DIR}/predictable-interface-names.yaml" \
  --config-patch @"${PATCH_DIR}/extra-mounts.yaml" \
  --config-patch @"${PATCH_DIR}/add-disk.yaml" \
  --config-patch @"${PATCH_DIR}/bind-addresses.yaml" \
  --output "${GEN_DIR}"

cp "${GEN_DIR}/talosconfig" ~/.talos/config

# --- talos client config ---
talosctl config endpoints "${IP}"
talosctl config node "${IP}"

# --- apply config ---
talosctl apply-config \
  -f "${GEN_DIR}/controlplane.yaml" \
  -n "${IP}" \
  --insecure

until talosctl bootstrap -n "$IP"; do
  echo "Waiting for Talos bootstrap to become available..."
  sleep 15
done
# --- wait for kube-apiserver ---
talosctl health \
  -n "${IP}" \
  --wait-timeout 10m || true

# --- fetch kubeconfig ---
talosctl kubeconfig \
  -n "${IP}" \
  --force

echo "Cluster ready at ${IP}"
