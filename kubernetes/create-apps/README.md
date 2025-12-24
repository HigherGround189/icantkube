# Create Apps
This folder contains YAMLs that declare ArgoCD Applications.
Each Application defines what the resources to be deployed and their sources.

> [!NOTE]
> You must create an ArgoCD Application here to deploy your application on the cluster (and for it to appear on the ArgoCD Dashboard).

## Example

### Git Source
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: <APP-NAME>
  namespace: argocd
spec:
  project: default

  source:
    repoURL: <GIT-REPO-URL>
    targetRevision: <GIT-REPO-BRANCH>
    path: <FOLDER-APP-YAMLS-ARE-IN> 
    # Eg: kubernetes/apps/frontend-test

  destination:
    server: https://kubernetes.default.svc
    namespace: <NAMESPACE-APP-IS-DEPLOYED-TO>

  syncPolicy:
    automated:
      prune: true
      selfHeal: true

```

### Helm Source (with ```values.yaml``` in Git)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: <APP-NAME>
  namespace: argocd
spec:
  project: default

  sources:
    # App Helm chart source
    - repoURL: <APP-HELM-CHART-URL>
      chart: <APP-HELM-CHART-NAME>
      targetRevision: "<APP-HELM-CHART-VERSION>"
      helm:
        valueFiles:
          - $values/<VALUES.YAML-PATH>  
          #Eg: - $values/kubernetes/apps/sealed-secrets/values-override.yaml

    # Git Repo containing values.yaml
    - repoURL: <GIT-REPO-URL>
      targetRevision: <GIT-REPO-BRANCH>
      ref: values

  destination:
    server: https://kubernetes.default.svc
    namespace: <NAMESPACE-APP-IS-DEPLOYED-TO>

  syncPolicy:
    automated:
      prune: true
      selfHeal: true

```