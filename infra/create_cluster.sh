#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/terraform"
GEN_DIR="${SCRIPT_DIR}/generated"
KUBECONFIG_PATH="${GEN_DIR}/k3s.yaml"
SSH_KEY_PATH="${SSH_KEY_PATH:-}"

for cmd in terraform ssh kubectl helm kubeseal; do
  command -v "${cmd}" >/dev/null || {
    echo "Missing required command: ${cmd}"
    exit 1
  }
done

mkdir -p "${GEN_DIR}"

terraform -chdir="${TF_DIR}" init -input=false
terraform -chdir="${TF_DIR}" apply -auto-approve -input=false

IP="$(terraform -chdir="${TF_DIR}" output -raw elastic_ip)"
SSH_USER="$(terraform -chdir="${TF_DIR}" output -raw ssh_user)"

if [[ -z "${IP}" || -z "${SSH_USER}" ]]; then
  echo "ERROR: missing terraform outputs (elastic_ip / ssh_user)"
  exit 1
fi

SSH_OPTS=(
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o ConnectTimeout=10
)

if [[ -n "${SSH_KEY_PATH}" ]]; then
  SSH_OPTS+=(-i "${SSH_KEY_PATH}")
fi

echo "Waiting for SSH on ${SSH_USER}@${IP}..."
until ssh "${SSH_OPTS[@]}" "${SSH_USER}@${IP}" "echo ssh-ready" >/dev/null 2>&1; do
  sleep 5
done

echo "Installing k3s on server..."
ssh "${SSH_OPTS[@]}" "${SSH_USER}@${IP}" \
  "curl -sfL https://get.k3s.io | sh -s - --disable traefik --disable local-storage --disable servicelb --disable metrics-server --disable-cloud-controller"

echo "Fetching kubeconfig..."
ssh "${SSH_OPTS[@]}" "${SSH_USER}@${IP}" "sudo cat /etc/rancher/k3s/k3s.yaml" > "${KUBECONFIG_PATH}"
sed -i "s/127.0.0.1/${IP}/g" "${KUBECONFIG_PATH}"
sed -i "s/localhost/${IP}/g" "${KUBECONFIG_PATH}"
chmod 600 "${KUBECONFIG_PATH}"

KUBECONFIG="${KUBECONFIG_PATH}" kubectl wait --for=condition=Ready node --all --timeout=5m

"${SCRIPT_DIR}/redeploy.sh" "${KUBECONFIG_PATH}"

cat <<EOF
Cluster is ready.
Kubeconfig: ${KUBECONFIG_PATH}

Use:
  export KUBECONFIG="${KUBECONFIG_PATH}"
EOF
