# ArgoCD Bootstrap
This folder contains the ArgoCD App of Apps Bootstrap Application, ```argocd-bootstrap```.

> [!NOTE]
> This application is responsible for updating the cluster when new YAMLs are committed. If this application goes down, all other applications will go down as well. 

> [!WARNING]
> **Do not modify anything in this folder, as a misconfiguration could cripple our entire cluster.**