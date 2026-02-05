kubectl create ns cloudflare-tunnel-ingress-controller
kubeseal --format yaml < cloudflare-credentials-unsealed-secret.yaml > cloudflare-credentials.sealed.yaml 
kubectl -n cloudflare-tunnel-ingress-controller create -f cloudflare-credentials.sealed.yaml

helm repo add strrl.dev https://helm.strrl.dev
helm install cloudflare-tunnel-ingress-controller strrl.dev/cloudflare-tunnel-ingress-controller \
  -f values.yaml -n cloudflare-tunnel-ingress-controller --create-namespace