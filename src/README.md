# Apps
This folder contains the source code for user-built microservices (AI inference, website, auth, etc..)

> [!TIP]
> Your microservice source code should be in a subfolder here.

## Example
Let's say you want to create a microservice called ```echo```. You should create a folder and place all your application code required for deployment here.

```yaml
src/
└── echo
    ├── .venv
    ├── main.py
    └── Dockerfile # You need to containerize your microservice
```

> [!IMPORTANT]
> After pushing your Docker image to Docker Hub, go to [apps](/kubernetes/apps/) to define how your app will be deployed via Kubernetes
