# ICANTKUBE 🥀🥀🥀

# Project overview and objectives

## Problem Statement

Our problem statement for project (machine failure)

## System Architecture

Include System Architecture diagram here. 

### Model Pipeline

Explain what model pipeline does (preferably each part)

# Instructions to build and run system

Not sure if needed, waiting for response by Ms Seah

# Microservices
Create table with description of each microservice and its purpose

# Dataset information and sources
I got no clue for this one 

# Any known issues or limitations
Dependency on cloudflare

# Additional K8s Features
Add table of additional k8s features here.














<br><bn><br><bn><br><bn><br><bn><br><bn><br><bn><br><bn><br><bn><br><bn><br><bn>

# RESTRUCTURING IN PROGRESS (EVERYTHING ABOVE THIS PART IS A SUBMISSION REQUIREMENT)

## TBD

* Add contribution table here.
* Add table of resources used (eg: deployment, statefulset etc)
* Template out all yamls from helm

## Slides Order

* Problem Statement
* Individual Contributions
* System Architecture
  * What Argocd does
  * How Cloudflare Ingress works
  * What Promtheus + Grafana do
  * Model Training as a whole
  * How models are tracked in mlflow

Note: "Describe how your architecture ensures scalability, modularity, and fault tolerance."

## Links

* [Website](https://home.icantkube.help/)
* [ArgoCD](https://argocd.icantkube.help/)
* [Mlflow](https://mlflow.icantkube.help/)
* [Grafana](https://grafana.icantkube.help/)
* [Prometheus](https://prometheus.icantkube.help/)
* [Kubebox](https://kubebox.icantkube.help/)
* [PHPMyAdmin](https://phpmyadmin.icantkube.help/)
* [RustFS](https://rustfs.icantkube.help/)

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


### horizontal_auto_scaler.yaml
The horizontal pod auto scaler scales the number of pods of the designated target in the scaleTargetRef. In this case, we have set it to automatically control scaling of the rollout pods. We can set up the max and min number of pods, time between scaling up and scaling down the number of pods.

apiVersion: autoscaling/v2 - 
kind: HorizontalPodAutoscaler
metadata:
  name: sensor-data-hpa

spec:
  scaleTargetRef:
    apiVersion: argoproj.io/v1alpha1
    kind: Rollout
    name: sensor-data-rollout

  minReplicas: 1
  maxReplicas: 4

  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 99

  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      selectPolicy: Max
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 1
        periodSeconds: 15
      selectPolicy: Max

