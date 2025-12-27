cd /kubernetes/apps/argocd/helm
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd -f values-override.yaml -n argocd --create-namespace

cd /kubernetes/apps/sealed-secrets/helm
helm install sealed-secrets sealed-secrets/sealed-secrets -f values-override.yaml -n sealed-secrets --create-namespace

cd /kubernetes/data-sources/
kubeseal --format < github-repo-unsealed-secret.yaml > github-repo.sealed.yaml
k apply -f github-repo.sealed.yaml

cd /kubernetes/apps/cloudflare-tunnel-ingress-controller
kubeseal --format yaml < cloudflare-credentials-unsealed-secret.yaml > cloudflare-credentials.sealed.yaml

cd /kubernetes/apps/mlflow
kubeseal --format yaml < mlflow-auth-credential-unsealed-secret.yaml > mlflow-auth-credential.sealed.yaml
kubeseal --format yaml < mlflow-postgresql-credentials-unsealed-secret.yaml > mlflow-postgresql-credentials.sealed.yaml

cd /kubernetes/argocd-boostrap/
k apply -f track-create-apps-and-data-sources.yaml

