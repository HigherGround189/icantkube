from kr8s.objects import Deployment, Service

def template_deployment(model_name: str, replicas: int, prediction_interval: str):
    return Deployment({
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": f"{model_name}-inference-server",
        "namespace": "model-pipeline"
    },
    "spec": {
        "replicas": replicas,
        "selector": {
        "matchLabels": {
            "app": f"{model_name}-inference-server"
        }
        },
        "template": {
        "metadata": {
            "labels": {
            "app": f"{model_name}-inference-server"
            }
        },
        "spec": {
            "containers": [
            {
                "name": f"{model_name}-inference-server",
                "image": "icantkube/model-inference-server:v0.26",
                "ports": [
                {
                    "containerPort": 80
                }
                ],
                "env": [
                {
                    "name": "MODEL_NAME",
                    "value": str(model_name.capitalize())
                },
                {
                    "name": "PREDICTION_INTERVAL",
                    "value": str(prediction_interval)
                }
                ],
                "envFrom": [
                {
                    "secretRef": {
                    "name": "mlflow-credentials-secret"
                    }
                },
                {
                    "configMapRef": {
                    "name": "mlflow-server-link-config"
                    }
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