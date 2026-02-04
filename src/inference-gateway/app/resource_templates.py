from kr8s.objects import Deployment, Service

def template_deployment(name):
    return Deployment({
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name,
            "namespace": "inference"
        },
        "spec": {
            "replicas": 1,
            "selector": {
            "matchLabels": {
                "app": f"{name}-inference-server"
            }
            },
            "template": {
            "metadata": {
                "labels": {
                "app": f"{name}-inference-server"
                }
            },
            "spec": {
                "containers": [
                {
                    "name": f"{name}-inference-server",
                    "image": "icantkube/model-inference-server",
                    "ports": [
                    {
                        "containerPort": 80
                    }
                    ]
                }
                ]
            }
        }
    }
})

def template_service(name):
    return Service()