# ICANTKUBE 🥀 

## Kubernetes 
The [kubernetes/](kubernetes/) folder is the single source of truth for our kubernetes cluster. ArgoCD continuously watches the folder and automatically reconciles cluster resources to match what is committed in Git.

## Application Code
The [src/](src/) folder contains the source code for user-built microservices (AI inference, Website, Model Training, etc..)

## Image Auto-Build & Auto-Update
To improve developer experience, we use github actions to automatically build container images, and to update image tags in Kubernetes deployments. 

Auto update and auto build can be enabled once you have: 
 1. Added your image to [imageConfig.yaml](imageConfig.yaml).
 2. Named your dockerfile appropriately.   
 3. Created ```kustomization.yaml```.

### ImageConfig.yaml
To register your image for Auto-Build & Auto-Update, you must add it to [imageConfig.yaml](imageConfig.yaml) in this format:
```yaml
<imageName>:
  autoUpdate: true
  autoBuild: true
```

> [!IMPORTANT]
> Your image **MUST** be published by the [icantkube/ user](https://hub.docker.com/repositories/icantkube) on Dockerhub.

### Dockerfile Naming
Your Dockerfile must also be called ```image-name.Dockerfile```. For example, if your image name is ```backend```, your Dockerfile should be called ```backend.Dockerfile```. This is for the image builder to determine what to name your image.

### Deployment.yaml
The Auto Updater will not edit your ```deployment.yaml``` directly. Instead, it looks for a ```kustomization.yaml``` in the same directory.

Here is an example:
```bash
.
├── config.yaml
├── deployment.yaml
├── ingress.yaml
├── kustomization.yaml # <---
├── namespace.yaml
└── service.yaml
```

Here is a template for ```kustomization.yaml```:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- config.yaml
- deployment.yaml
- ingress.yaml
- namespace.yaml
- service.yaml
# Make sure to put ALL your resources here

images:
- name: <imageName> #eg: icantkube/api-gateway
  newTag: <imageTag> #eg: v0.3

```
