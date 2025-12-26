# Apps
This folder contains the source code for user-built microservices (AI inference, website, auth, etc..)

> [!TIP]
> Your microservice source code should be a HTTP server listening on port 80 in a subfolder here.

## Example
Let's say you want to create a microservice called ```echo```. You should create a folder and place all your application code required for deployment here.

```yaml
src/
└── echo
    ├── .venv
    ├── main.py
    └── Dockerfile # You need to containerize your microservice
```

You also need to update [config.yml](/kubernetes/apps/api-gateway/config.yaml) using the following format:
```yaml
services:
    <name>:
        http://<name>.<namespace>.svc.cluster.local
```

> [!IMPORTANT]
> After pushing your Docker image to Docker Hub, go to [apps](/kubernetes/apps/) to define how your app will be deployed via Kubernetes. You will need to use the Kubernetes manifest files to specify the name and namespace that you are using to define your microservice in the API config file.