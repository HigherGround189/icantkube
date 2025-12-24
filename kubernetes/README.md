# Kubernetes
This directory is the single source of truth for the Kubernetes cluster.
ArgoCD continuously watches this folder and automatically reconciles the cluster state to match what is committed in Git.

> [!IMPORTANT]
> **<u>Any YAML committed to this folder is automatically applied to the cluster.</u>**

# Directory Structure
```yaml
kubernetes/ 
├── apps
├── argocd-boostrap
├── create-apps 
└── data-sources
```

## ```apps/```
Contains application manifests for Kubernetes resources
(e.g. Deployments, Services, Ingresses, ConfigMaps, etc).

## ```argocd-boostrap/```
Contains the ArgoCD App of Apps bootstrap Application, ```argocd-bootstrap```.
This application is responsible for updating the cluster when new YAMLs are committed.

## ```create-apps/```
Contains YAMLs that declare ArgoCD Applications.
Each Application defines what the resources to be deployed and their sources.

## ```data-sources/```
Contains YAMLs that declare ArgoCD repositories (Git, Helm, etc)
Each Repository represents an external source ArgoCD has access to (eg: This Github Repo, Helm Repos, etc).