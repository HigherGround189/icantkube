# Data Sources
This folder contains YAMLs that declare ArgoCD repositories (Git, Helm, etc)
Each Repository represents an external source ArgoCD has access to (eg: This Github Repo, Helm Repos, etc).

## Example

### Helm Repo
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <REPO-NAME>
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: helm
  url: <HELM-REPO-URL>
```

### Git Repo (Public)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <REPO-NAME>
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: <GIT-REPO-URL> # Url must end with .git
```

### Git Repo (Private)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <REPO-NAME>
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: <GIT-REPO-URL> # Url must end with .git
  password: <TOKEN-TO-ACCESS-REPO>
  username: <GITHUB-USERNAME>
```

> [!CAUTION]
> **Do not commit a private repo with the access token in plaintext. Use kubeseal instead.**

Use kubeseal to encrypt plaintext secrets (such as the repo access token).
Assuming the kubeseal CLI is installed:

```bash
# Assuming your YAML file is called repo-unsealed-secret.yaml
kubeseal --format yaml < repo-unsealed-secret.yaml > repo.sealed.yaml
```

Make sure to commit ```repo.sealed.yaml``` instead of ```repo-unsealed-secret.yaml```.

> [!TIP]
> Add ```-unsealed-secret``` to the end of your unencrypted file (eg: ```myrepo-unsealed-secret.yaml```). This is because .gitignore is configured to ignore such files, removing the risk of accidentally pushing sensitive information.

> [!NOTE]
> Add ```.sealed``` to the end of your encrypted file (eg: ```myrepo.sealed.yaml```). This is purely for organisational purposes.


