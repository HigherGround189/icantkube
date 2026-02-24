from kr8s.objects import Deployment

def template_deployment(model_name: str, replicas: int, prediction_interval: str):
    """
    Templates a Kubernetes Deployment manifest for a model-inference-server microservice.
    You can see the YAML version of the deployment in the "reference-deployment.yaml" file in the same directory as this one

    Args:
        model_name (str): Name of the mlflow model. 
        replicas (int): Number of pod replicas to deploy.
        prediction_interval (str): Prediction interval for the mlflow model.

    Returns:
        Deployment: A templated Kubernetes Deployment object.
    """
    return Deployment({
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": f"{model_name}-inference-server",
        "namespace": "model-pipeline",
        "annotations": {
            "inference-server": "True",
            "model-name": str(model_name)
        }
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
                "image": "icantkube/model-inference-server:v0.39",
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
                },
                                {
                    "secretRef": {
                    "name": "mariadb-credentials-secret"
                    }
                },
                {
                    "configMapRef": {
                    "name": "mariadb-config"
                    }
                }
                ]
            }
            ]
        }
        }
    }
})
