# Apps
This folder contains application manifests for Kubernetes resources
(e.g. Deployments, Services, Ingresses, ConfigMaps, etc).

> [!TIP]
> You should define your application's YAMLs in a subfolder here.

## Example
Let's say you want to create an application called ```my-webserver```. You should create a folder here, and place all your yamls inside that folder.

```yaml
apps/
└── my-webserver # Create this folder, and place all your yamls inside
    ├── deployment.yaml
    ├── ingress.yaml
    └── service.yaml
```

> [!IMPORTANT]
> Remember to create an ArgoCD Application in [create-apps](/kubernetes/create-apps), or your App will not be deployed.









