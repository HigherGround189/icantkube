helm repo add traefik https://traefik.github.io/charts
kubectl create ns traefik
helm install --namespace=traefik \
    traefik traefik/traefik